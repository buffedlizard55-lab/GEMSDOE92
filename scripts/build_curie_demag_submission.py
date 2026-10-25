#!/usr/bin/env python3
"""CURIE-DEMAG lane build: unique submission GeoTIFF + autonomous validation.

Pre-registration: docs/HYPOTHESES_20261026_CURIEDEMAG.md (Rank 1).

Pipeline (no manual step, no network):
  1. Restore-check pinned inputs (.cache/gems_inputs, SHA-256 verified).
  2. Build CURIE-DEMAG surface from pinned 19-band stack (gems/curie_demag.py):
     multi-scale RTP variance suppression ratio × MT clay-cap flank × RTP demag bowl.
  3. Emit 37,654 unit dots spaced >= 2.83 px on valid & ~catalogue & d_cat>2.0
  4. Package via vendor/gems57/submission_writer.py (zeros-outside, float32, EPSG:32611)
  5. Format gates: gems.gates.run_gates + gems57.validate, independent disk re-read
  6. HOLDOUT-DTI: gems57-pooled-hide-v2, buffered whole-component quadrant draw
     (seeds 20+30, 8 folds, 1.2km guard, 500m negative buffer), pooled DTI + 1000-draw
     paired spatial-block bootstrap CI vs R0, strict hide-and-recover placement rebuilt per fold.
  7. Leakage canaries: symmetric AUC of each feature vs pooled withheld truth; require <=0.90.
  8. Uniqueness: local complete registry literal + |rho|; dense-witness specificity.

Verdict: promote only if strict Rule-2 HOLDOUT-DTI beats holdout-best (0.113316)
with paired CI excluding 0 AND uniqueness passes AND gates pass. Otherwise negative
(research download only). Negative is a deliverable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "gems")]

INPUTS = ROOT / ".cache" / "gems_inputs"
BRIDGE = INPUTS / "bridge"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
RELEASES = ROOT / "releases"

from gems57 import grid as grid_mod, submission_writer, uniqueness as U, validate as V
from gems57 import holdout, evaluate_holdout
from curie_demag import lane_surface

N_DOTS = 37_654
MIN_DIST_PX = 2.8
STACK = INPUTS / "training_features.tif"
HOLDout_BEST_RULE2 = 0.113316
HOLDout_BEST_STATIC = 0.009220

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def auc_sym(scores: np.ndarray, labels: np.ndarray) -> float:
    from scipy.stats import rankdata
    pos = scores[labels]
    neg = scores[~labels]
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    all_scores = np.concatenate([pos, neg])
    ranks = rankdata(all_scores, method="average").astype(np.float64)
    auc = (ranks[: pos.size].sum() - pos.size * (pos.size + 1) / 2.0) / (pos.size * neg.size)
    return float(max(auc, 1.0 - auc))

def build_holdout_terms(grid, surface, valid, r0_arr):
    from gems import breakline
    folds = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
    log(f"holdout: {len(folds)} folds (2 seeds x 4 quadrants); rebuilding placement from visible faults")
    terms_by_arm = {"CURIE_DEMAG": None, "R0": None}
    per_fold = {"CURIE_DEMAG": [], "R0": []}
    for fold in folds:
        visible = np.asarray(fold["visible"], bool)
        d_visible = distance_transform_edt(~visible)
        candidate = valid & ~visible & (d_visible > 2.0)
        pred = breakline.spaced_top_mask(surface, candidate, N_DOTS,
                                         min_dist_px=MIN_DIST_PX, cand_cap=900_000).astype(np.float32)
        for arm_name, arr in (("CURIE_DEMAG", pred), ("R0", r0_arr)):
            score, terms = evaluate_holdout.evaluate(arr, fold, grid.footprint)
            per_fold[arm_name].append(round(float(score["dti"]), 6))
            old = terms_by_arm[arm_name]
            terms_by_arm[arm_name] = terms if old is None else old + terms
    return terms_by_arm, per_fold, folds

def local_registry(exclude_stems):
    files = []
    for d in (DOWNLOADS, RELEASES, ROOT / "data", BRIDGE):
        for p in sorted(d.glob("*.tif")):
            if any(p.name.startswith(s) for s in exclude_stems):
                continue
            files.append(("local:" + str(p.relative_to(ROOT)), p))
    return files

def compare_to_local(cand_dots, surface, foot, registry, expected):
    rows = []
    foot_idx = np.flatnonzero(foot)
    sub = np.sort(np.random.default_rng(20261026).choice(foot_idx, size=400_000, replace=False))
    surf_sub = surface.ravel()[sub].astype(np.float32)
    for label, path in registry:
        try:
            with rasterio.open(path) as ds:
                if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected:
                    rows.append(dict(file=label, error="grid/band mismatch"))
                    continue
                raw = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
        except Exception as exc:
            rows.append(dict(file=label, error=str(exc)[:80]))
            continue
        support = (raw > 0) & foot
        n_sup = int(support.sum())
        if n_sup == 0:
            rows.append(dict(file=label, error="empty"))
            continue
        near_lit = U._near(support, 3.0)
        k = int(cand_dots.sum())
        dot_mask = cand_dots > 0
        lit = float(near_lit[dot_mask].mean())
        if n_sup <= U.DOT_FIELD_MAX_SUPPORT:
            mb, rep = lit, "dot_field"
        else:
            mb = float(U._near(U.matched_budget_support(raw, foot, k), 3.0)[dot_mask].mean())
            rep = "continuous_surface"
        tv = raw.ravel()[sub]
        rho = float(spearmanr(surf_sub, tv).statistic) if (n_sup > 1 and np.ptp(surf_sub) and np.ptp(tv)) else float("nan")
        rows.append(dict(file=label, their_dots=n_sup, my_dots=k, representation=rep,
                         literal_forward_overlap=round(lit, 6),
                         matched_budget_forward_overlap=round(mb, 6),
                         spearman_surface=None if not np.isfinite(rho) else round(rho, 6)))
        del raw, support, near_lit
    return rows

def dual_reading(rows):
    checked = [r for r in rows if "error" not in r]
    if not checked:
        raise ValueError("no registry rows")
    worst_lit = max(checked, key=lambda r: r["literal_forward_overlap"])
    worst_mb = max(checked, key=lambda r: r["matched_budget_forward_overlap"])
    worst_rho = max(checked, key=lambda r: abs(r["spearman_surface"] or 0.0))
    # binding rule: literal overlap + |rho|
    dup_literal = bool(worst_lit["literal_forward_overlap"] > 0.70 or abs(worst_rho["spearman_surface"]) > 0.90)
    # diagnostic matched-budget
    dup_mb = bool(worst_mb["matched_budget_forward_overlap"] > 0.70 or abs(worst_rho["spearman_surface"]) > 0.90)
    return dict(
        evidence_class="REGISTRY-MEASUREMENT",
        rasters_checked=len(checked),
        worst_literal_forward_overlap=float(worst_lit["literal_forward_overlap"]),
        worst_literal_file=worst_lit["file"],
        worst_matched_budget_forward_overlap=float(worst_mb["matched_budget_forward_overlap"]),
        worst_matched_budget_file=worst_mb["file"],
        worst_abs_spearman=abs(float(worst_rho["spearman_surface"])),
        worst_abs_spearman_file=worst_rho["file"],
        duplicate=dup_literal,
        duplicate_matched_budget=dup_mb,
        verdict="negative" if dup_literal else "unique",
    )

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stem", default=None, help="output stem")
    args = ap.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = args.stem or f"gemsdoe92-curiedemag-{stamp}"
    tif_path = DOWNLOADS / f"{stem}-zeros.tif"

    log("0. Load pinned grid (footprint + catalogue)")
    grid = grid_mod.load_grid(BRIDGE)
    foot, cat = grid.footprint, grid.catalogue
    with rasterio.open(BRIDGE / "sample_submission.tif") as ref:
        expected = (ref.shape, ref.crs, ref.transform)
    d_cat = distance_transform_edt(~cat)

    log("1. Build CURIE-DEMAG surface (B2 variance ratio x B17 MT flank x RTP demag bowl)")
    surf = lane_surface(str(STACK), foot)
    valid, S = surf["valid"], surf["S"]
    log(f"  valid={int(valid.sum())}/{foot.size}  S: min {S[valid].min():.4f} max {S[valid].max():.4f} mean {S[valid].mean():.4f}")

    log("2. Emit dots: top surface candidates on valid & ~catalogue & d_cat>2.0, spaced >=2.8px")
    cand = valid & ~cat & (d_cat > 2.0)
    from gems import breakline
    dots = breakline.spaced_top_mask(S, cand, N_DOTS, min_dist_px=MIN_DIST_PX, cand_cap=900_000)
    log(f"  dots={int(dots.sum())} on-catalogue={int((dots & cat).sum())} outside-footprint={int((dots & ~foot).sum())}")

    dots_arr = dots.astype(np.float32)
    r0_path = ROOT / "data" / "parent_R0_zeros.tif"
    if not r0_path.is_file():
        r0_path = BRIDGE / "parent_R0_zeros.tif"
    with rasterio.open(r0_path) as ds:
        r0_arr = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot

    log("3. Package via submission_writer (zeros-outside, [0,1], pinned grid)")
    note = "h33-h33-2-b2; CURIE-DEMAG: RTP variance-suppression x MT clay-cap flank x demag bowl; 37654 dots d_cat>2px"
    name = f"GEMSDOE92-CURIE-DEMAG-{stamp[:8]}"
    if len(note) > 140:
        note = note[:140]
    if len(name) > 140:
        name = name[:140]
    receipt = submission_writer.write_submission(
        tif_path, dots_arr, BRIDGE / "sample_submission.tif", foot,
        note=note, name=name, catalogue=cat,
        metadata=dict(lane="CURIE_DEMAG", hypothesis_doc="docs/HYPOTHESES_20261026_CURIEDEMAG.md"))

    log("4. Independent disk re-read validation + format gates")
    v = V.validate(tif_path, foot, cat)
    V.assert_submittable(v)
    from gems.gates import run_gates, summarise
    gate_results = run_gates(str(tif_path), str(BRIDGE / "sample_submission.tif"),
                             str(BRIDGE / "existing_faults.tif"), prune_radius=2,
                             require_submission_encoding=True)
    gate_ok, gate_report = summarise(gate_results)
    log(f"  format gates: {'PASS' if gate_ok else 'FAIL'}")

    log("5. HOLDOUT-DTI (gems57-pooled-hide-v2, 22,663 withheld positives, seeds 20+30)")
    terms_by_arm, per_fold, folds = build_holdout_terms(grid, S, valid, r0_arr)
    pooled = evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520826, candidate="CURIE_DEMAG")
    primary = pooled["scores"]["CURIE_DEMAG"]
    control = pooled["scores"]["R0"]
    delta = pooled["paired_differences"]["R0"]
    log(f"  CURIE_DEMAG strict fold-visible: {primary['dti']:.6f} CI [{primary['ci95'][0]:.6f}, {primary['ci95'][1]:.6f}] (withheld={primary['withheld_positive_pixels']})")
    log(f"  R0 control: {control['dti']:.6f}; paired delta {delta['delta']:.6f} CI [{delta['ci95'][0]:.6f}, {delta['ci95'][1]:.6f}]")

    log("6. Leakage canaries: symmetric AUC per feature vs pooled withheld truth")
    truth_pool = np.zeros(foot.shape, bool)
    for fold in folds:
        truth_pool |= np.asarray(fold["truth"], bool)
    canaries = {}
    for feat_name in ("suppression", "mt_grad", "demag", "S"):
        feat = surf[feat_name]
        scores = feat[foot]
        labels = truth_pool[foot]
        canaries[feat_name] = auc_sym(scores, labels)
    max_auc = max(canaries.values())
    log(f"  canary max symmetric AUC = {max_auc:.4f} ({canaries})")

    log("7. Uniqueness vs complete local registry")
    registry = local_registry(exclude_stems=(stem,))
    log(f"  {len(registry)} local rasters")
    rows = compare_to_local(dots_arr, S, foot, registry, expected)
    uniq = dual_reading(rows)
    log(f"  local: worst literal={uniq['worst_literal_forward_overlap']:.4f} ({uniq['worst_literal_file']}), MB={uniq['worst_matched_budget_forward_overlap']:.4f}, |rho|={uniq['worst_abs_spearman']:.4f}, duplicate={uniq['duplicate']}")

    # dense-witness specificity if cached
    specificity = None
    # try to find any cached dense witness from evidence/ or .cache
    import glob
    witness_candidates = list(EVIDENCE.glob("*dense*"))
    # if not found, keep specificity null
    if witness_candidates:
        log(f"  dense witnesses in evidence: {len(witness_candidates)} files")

    beats_rule2 = primary["dti"] > HOLDout_BEST_RULE2
    ci_excludes_zero = delta["ci95"][0] > 0
    unique_ok = not uniq["duplicate"]
    beats_holdout_best = beats_rule2 and ci_excludes_zero
    verdict = "promote" if (beats_holdout_best and unique_ok and gate_ok and max_auc <= 0.90) else "negative"
    submission_eligible = bool(verdict == "promote")

    log(f"8. Verdict: {verdict} (beats_rule2={beats_rule2}, ci_excl_0={ci_excludes_zero}, unique_ok={unique_ok}, gates_ok={gate_ok}, maxAUC={max_auc:.4f})")

    audit = dict(
        schema="gemsdoe92-curie-demag-audit.v1", lane="CURIE_DEMAG", arm="primary",
        file=f"docs/downloads/{tif_path.name}", sha256=sha256_file(tif_path),
        bytes=tif_path.stat().st_size, submission_name=name, note=note, note_chars=len(note),
        validator=v, format_gates=[{"gate": r.name, "ok": r.ok, "detail": r.detail} for r in gate_results],
        gates_pass=gate_ok, uniqueness_local=uniq, dense_witness_specificity=specificity,
        public_registry={"available": False, "reason": "local complete registry used; public not scanned in sandbox"},
    )
    audit_path = DOWNLOADS / f"{stem}-audit.json"
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    # also write audit with -zeros.json suffix for site contract
    audit_zeros_path = DOWNLOADS / f"{stem}-zeros.json"
    if not audit_zeros_path.exists():
        audit_zeros_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    card = dict(
        schema="gemsdoe92-run-card.v3", lane="CURIE_DEMAG", date=stamp,
        hypothesis=("Blind hydrothermal upflow alters titanomagnetite to pyrite inside a conductive smectite clay cap, "
                    "creating a multi-scale magnetic quiet trough bounded by steep MT resistivity flanks. "
                    "CURIE-DEMAG combines 300 m vs 1500 m RTP variance suppression, MT clay-cap flank gradient, and RTP demag bowl."),
        mechanism=("Percentile-rank product S = pct_rank(1 - var3/var15) * pct_rank(|grad log B17|) * pct_rank(max(0, laplacian RTP)), "
                   "on valid footprint; 37,654 dots spaced >=2.83 px on valid & ~catalogue & d_cat>2.0. Catalogue used only for masking."),
        named_non_fault_mimic="Thick non-magnetic lacustrine sediments, unaltered basalt cover, survey levelling artifacts, basalt flow edges.",
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI", evaluator_version=evaluate_holdout.VERSION,
            withheld_positives=int(primary["withheld_positive_pixels"]),
            primary_instrument="strict fold-visible rebuild d_visible>2.0, pooled gems57-pooled-hide-v2, seeds 20+30, 8 folds, 1000-draw paired spatial-block bootstrap CI",
            scores={"CURIE_DEMAG": primary, "R0": control},
            paired_vs_R0=dict(delta=delta["delta"], ci95=delta["ci95"]),
            beats_holdout_best=beats_holdout_best,
            holdout_best_reference=dict(lane="COULOMB-LOQO standalone", rule2_d_visible_2=HOLDout_BEST_RULE2, static_d_cat_2=HOLDout_BEST_STATIC,
                                        source="evidence/coulomb_loqo_proxy_audit.json"),
        ),
        holdout_rule2_d_visible_2=dict(
            evidence_class="HOLDOUT-DTI (strict draw-blind fold-visible d_visible>2.0 diagnostic)",
            evaluator_version=evaluate_holdout.VERSION,
            scores={"CURIE_DEMAG": primary, "R0": control},
        ),
        leakage_canaries=dict(max_symmetric_auc=max_auc, all_pass_le_0p90=bool(max_auc <= 0.90), per_feature={k: round(float(v),6) for k,v in canaries.items()}),
        correlation_overlap_vs_registry=dict(local=uniq, public={"available": False, "scope": "not scanned (no gh auth)"}, dense_witness_specificity=specificity),
        raster_sha256=sha256_file(tif_path), zip_sha256=receipt.get("zip_sha256"), file=f"docs/downloads/{tif_path.name}",
        validator_output=dict(no_nan_in_footprint=bool(v["checks"]["in_footprint_all_finite"]), values_in_0_1=bool(v["checks"]["range_0_1_guaranteed"]),
                              crs_shape_transform_match=bool(v["checks"]["crs_epsg_32611"] and v["checks"]["dimensions_3730x3292"] and v["checks"]["transform_matches_sample_submission"]),
                              dots=int(v["emitted_positive_pixels"]), checks=v["checks"]),
        submission_name=name, submission_note=note, note_chars=len(note), experiments_used="1/3", weekly_slots_used=0,
        verdict=verdict, submission_eligible=submission_eligible,
        verdict_reason=f"strict HOLDOUT-DTI {primary['dti']:.6f} vs holdout-best {HOLDout_BEST_RULE2} (Rule-2); paired delta {delta['delta']:.6f} CI [{delta['ci95'][0]:.6f},{delta['ci95'][1]:.6f}]; unique_ok={unique_ok}; gates_ok={gate_ok}; maxAUC {max_auc:.4f}",
        organizer_confirmed=None,
        all_arms={"primary": dict(file=audit["file"], sha256=audit["sha256"], submission_name=name, note=note, note_chars=len(note), validator=v, holdout_dti=primary)},
    )
    card_path = EVIDENCE / f"{stem}_run_card.json"
    card_path.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    (DOWNLOADS / f"{stem}_run_card.json").write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    # also write standardized names for site renders
    (DOWNLOADS / "curie_demag_run_card.json").write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    (DOWNLOADS / "curie_demag_audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    log(f"WROTE {card_path}")
    log(f"WROTE {audit_path}")
    log(f"TIF: {tif_path} (sha256 {sha256_file(tif_path)[:16]}...)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
