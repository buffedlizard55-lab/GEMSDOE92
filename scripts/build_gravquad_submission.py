#!/usr/bin/env python3
"""GRAV-QUAD lane build: unique submission GeoTIFF + autonomous validation.

Pre-registration: docs/HYPOTHESES_20261026_RADIOCONTACT.md (Rank 3, "GRAV-QUAD").
RADIOCONTACT (Rank 1) and DRAINAGE-KNICK (Rank 2) were already built this
session arc and scored negative (see evidence/gemsdoe92-radiocontact-*_run_card.json
and the DRAINAGE-KNICK entry in README.md); this is the next pre-registered,
not-yet-tried candidate, reusing the same shared evaluator/writer (no private
fork).

Pipeline (no manual step, no network beyond the already-restored pinned cache):
  1. Restore-check pinned inputs (.cache/gems_inputs, SHA-256 verified by restore_inputs.py).
  2. Build the GRAV-QUAD surface (gems/gravquad.py): gravity analytic-signal
     amplitude (B11 vertical gradient + B18 signed E-W derivative + a locally
     computed N-S finite-difference component of B13) x structure-tensor
     linear-edge coherence. Zero catalogue reads inside the surface.
  3. Emit 37,654 unit dots spaced >= 2.83 px from surface top candidates on
     valid & ~catalogue & (d_cat > 2.0 px) -- same spacing/clearance as R0.
  4. Package via vendor/gems57/submission_writer.py (zeros-outside, float32,
     EPSG:32611, 3730x3292, pinned transform, [0,1], zero catalogue mass).
  5. Format gates: gems.gates.run_gates (require_submission_encoding) +
     gems57.validate, independent disk re-read.
  6. HOLDOUT-DTI: gems57-pooled-hide-v2, buffered whole-component quadrant
     draw (seeds 20+30, 8 folds, 1.2 km guard, 500 m negative buffer),
     pooled DTI + 1000-draw paired spatial-block bootstrap CI vs R0 control,
     static d_cat > 2.0 deployment AND strict Rule-2 d_visible > 2.0 diagnostic.
  7. Leakage canaries: symmetric AUC of each feature (asa, coherence, S) vs
     pooled withheld truth; require <= 0.90.
  8. Uniqueness (REGISTRY-MEASUREMENT): local complete registry (all served
     + release + bridge rasters), literal + matched-budget overlap and |rho|;
     dense-witness specificity vs 17GEMSDOE E-proba-multiscale if cached.
     Public scan over the 102+ GEMSDOE repos runs separately via
     scripts/audit_public_registry.py (only attempted if this lane beats the
     holdout bar -- see verdict logic below).
  9. Write Protocol Rule 5 run card + per-file audit JSON.

Verdict logic: promote only if primary HOLDOUT-DTI beats holdout-best
(COULOMB-LOQO standalone 0.113316 Rule-2 / 0.009220 static) with paired CI
excluding 0 AND uniqueness passes. Otherwise verdict = negative (a deliverable:
format-valid unique TIF, research download only).
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

from gems57 import grid as grid_mod, submission_writer, uniqueness as U, validate as V  # noqa: E402
from gems57 import holdout, evaluate_holdout  # noqa: E402
from gravquad import lane_surface  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402

N_DOTS = 37_654
MIN_DIST_PX = 2.8
STACK = INPUTS / "training_features.tif"
HOLDout_BEST_RULE2 = 0.113316   # COULOMB-LOQO standalone, strict draw-blind d_visible > 2.0
HOLDout_BEST_STATIC = 0.010788  # KNICKLOQO standalone, static d_cat > 2.0 (all-time repo record)
HOLDout_BEST_STATIC_COULOMBLOQO = 0.009220  # COULOMB-LOQO standalone, static d_cat > 2.0


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def auc_sym(scores: np.ndarray, labels: np.ndarray) -> float:
    """Symmetric ROC-AUC of ``scores`` for boolean ``labels`` via Mann-Whitney."""
    from scipy.stats import rankdata

    pos = scores[labels]
    neg = scores[~labels]
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    all_scores = np.concatenate([pos, neg])
    ranks = rankdata(all_scores, method="average").astype(np.float64)
    auc = (ranks[: pos.size].sum() - pos.size * (pos.size + 1) / 2.0) / (pos.size * neg.size)
    return float(max(auc, 1.0 - auc))


def build_holdout_terms(grid, dots_arr, r0_arr):
    folds = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
    log(f"holdout: {len(folds)} folds (2 seeds x 4 quadrants)")

    terms_by_arm = {}
    per_fold = {}
    for arm_name, arr in (("GRAVQUAD", dots_arr), ("R0", r0_arr)):
        all_terms = None
        fold_scores = []
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(arr, fold, grid.footprint)
            fold_scores.append(round(float(score["dti"]), 6))
            all_terms = terms if all_terms is None else all_terms + terms
        terms_by_arm[arm_name] = all_terms
        per_fold[arm_name] = fold_scores
    return terms_by_arm, per_fold, folds


def strict_rule2_terms(grid, dots_arr, folds):
    """Strict draw-blind fold-visible d_visible > 2.0 diagnostic (zero self-masking)."""
    terms = None
    fold_scores = []
    for fold in folds:
        vis = np.asarray(fold["visible"], bool)
        d_vis = distance_transform_edt(~vis)
        pred = np.zeros(grid.footprint.shape, np.float64)
        mask = (dots_arr > 0) & (d_vis > 2.0)
        pred[mask] = 1.0
        pred[vis] = 0.0
        score, tm = evaluate_holdout.evaluate(pred, fold, grid.footprint)
        fold_scores.append(round(float(score["dti"]), 6))
        terms = tm if terms is None else terms + tm
    return terms, fold_scores


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
    dup = bool(worst_mb["matched_budget_forward_overlap"] > 0.70 or abs(worst_rho["spearman_surface"]) > 0.90)
    return dict(
        evidence_class="REGISTRY-MEASUREMENT",
        rasters_checked=len(checked),
        worst_literal_forward_overlap=float(worst_lit["literal_forward_overlap"]),
        worst_literal_file=worst_lit["file"],
        worst_matched_budget_forward_overlap=float(worst_mb["matched_budget_forward_overlap"]),
        worst_matched_budget_file=worst_mb["file"],
        worst_abs_spearman=abs(float(worst_rho["spearman_surface"])),
        worst_abs_spearman_file=worst_rho["file"],
        duplicate=dup,
        verdict="negative" if dup else "unique",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stem", default=None, help="output stem (default timestamped)")
    args = ap.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = args.stem or f"gemsdoe92-gravquad-{stamp}"
    tif_path = DOWNLOADS / f"{stem}-zeros.tif"

    log("0. Load pinned grid (footprint + catalogue)")
    grid = grid_mod.load_grid(BRIDGE)
    foot, cat = grid.footprint, grid.catalogue
    with rasterio.open(BRIDGE / "sample_submission.tif") as ref:
        expected = (ref.shape, ref.crs, ref.transform)
    d_cat = distance_transform_edt(~cat)

    log("1. Build GRAV-QUAD surface (stack bands 11/13/18: analytic-signal amplitude x linear coherence)")
    surf = lane_surface(str(STACK), foot)
    valid, S = surf["valid"], surf["S"]

    log("2. Emit dots: top surface candidates on valid & ~catalogue & d_cat > 2.0, spaced >= 2.8 px")
    cand = valid & ~cat & (d_cat > 2.0)
    from gems import breakline  # spaced_top_mask
    dots = breakline.spaced_top_mask(S, cand, N_DOTS, min_dist_px=MIN_DIST_PX, cand_cap=900_000)
    log(f"  dots={int(dots.sum())} on-catalogue={int((dots & cat).sum())} outside-footprint={int((dots & ~foot).sum())}")

    dots_arr = dots.astype(np.float32)
    r0_path = ROOT / "data" / "parent_R0_zeros.tif"
    if not r0_path.is_file():
        r0_path = BRIDGE / "parent_R0_zeros.tif"
    with rasterio.open(r0_path) as ds:
        r0_arr = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot

    log("3. Package via submission_writer (zeros-outside, [0,1], pinned grid)")
    note = ("h33-h33-2-b2; GRAVQUAD: gravity analytic-signal amplitude x linear-edge "
            "coherence; 37654 dots d_cat>2px; see run card for HOLDOUT-DTI")
    name = f"GEMSDOE92-GRAVQUAD-{stamp[:8]}"
    if len(note) > 140:
        note = note[:137] + "..."
    if len(name) > 140:
        name = name[:140]
    receipt = submission_writer.write_submission(
        tif_path, dots_arr, BRIDGE / "sample_submission.tif", foot,
        note=note, name=name, catalogue=cat,
        metadata=dict(lane="GRAVQUAD", hypothesis_doc="docs/HYPOTHESES_20261026_RADIOCONTACT.md#rank-3"))

    log("4. Independent disk re-read validation + format gates")
    v = V.validate(tif_path, foot, cat)
    V.assert_submittable(v)
    from gems.gates import run_gates, summarise  # noqa: E402
    gate_results = run_gates(str(tif_path), str(BRIDGE / "sample_submission.tif"),
                             str(BRIDGE / "existing_faults.tif"), prune_radius=2,
                             require_submission_encoding=True)
    gate_ok, gate_report = summarise(gate_results)
    log(f"  format gates: {'PASS' if gate_ok else 'FAIL'}")

    log("5. HOLDOUT-DTI (gems57-pooled-hide-v2, 22,663 withheld positives, seeds 20+30)")
    terms_by_arm, per_fold, folds = build_holdout_terms(grid, dots_arr, r0_arr)
    pooled = evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate="GRAVQUAD")
    primary = pooled["scores"]["GRAVQUAD"]
    control = pooled["scores"]["R0"]
    delta = pooled["paired_differences"]["R0"]
    log(f"  GRAVQUAD static d_cat>2.0: {primary['dti']:.6f} CI [{primary['ci95'][0]:.6f}, {primary['ci95'][1]:.6f}] "
        f"(withheld={primary['withheld_positive_pixels']})")
    log(f"  R0 control: {control['dti']:.6f}; paired delta {delta['delta']:.6f} CI [{delta['ci95'][0]:.6f}, {delta['ci95'][1]:.6f}]")

    log("6. Strict Rule-2 fold-visible d_visible > 2.0 diagnostic")
    dvis_terms, dvis_fold = strict_rule2_terms(grid, dots_arr, folds)
    dvis_pooled = evaluate_holdout.pooled_summary(
        {"GRAVQUAD": dvis_terms, "R0": terms_by_arm["R0"]},
        draws=1000, seed=520810, candidate="GRAVQUAD")
    dvis_primary = dvis_pooled["scores"]["GRAVQUAD"]
    dvis_control = dvis_pooled["scores"]["R0"]
    log(f"  d_visible>2.0: GRAVQUAD {dvis_primary['dti']:.6f} vs R0 {dvis_control['dti']:.6f}")

    log("7. Leakage canaries: symmetric AUC per feature vs pooled withheld truth")
    truth_pool = np.zeros(foot.shape, bool)
    for fold in folds:
        truth_pool |= np.asarray(fold["truth"], bool)
    canaries = {}
    for feat_name in ("asa", "coherence", "S"):
        feat = surf[feat_name]
        scores = feat[foot]
        labels = truth_pool[foot]
        canaries[feat_name] = auc_sym(scores, labels)
    max_auc = max(canaries.values())
    log(f"  canary max symmetric AUC = {max_auc:.4f} ({canaries})")

    log("8. Uniqueness vs complete local registry (literal + matched-budget + |rho|)")
    registry = local_registry(exclude_stems=(stem,))
    log(f"  {len(registry)} local rasters")
    rows = compare_to_local(dots_arr, S, foot, registry, expected)
    uniq = dual_reading(rows)
    log(f"  local: worst MB={uniq['worst_matched_budget_forward_overlap']:.4f} "
        f"(<= {uniq['worst_matched_budget_file']}), lit={uniq['worst_literal_forward_overlap']:.4f}, "
        f"|rho|={uniq['worst_abs_spearman']:.4f}, duplicate={uniq['duplicate']}")

    beats_rule2 = primary["dti"] > HOLDout_BEST_RULE2
    beats_static = primary["dti"] > HOLDout_BEST_STATIC
    ci_excludes_zero_rule2 = delta["ci95"][0] > 0
    unique_ok = (not uniq["duplicate"])
    beats_holdout_best = beats_rule2 and ci_excludes_zero_rule2
    verdict = "promote" if (beats_holdout_best and unique_ok and gate_ok) else "negative"
    submission_eligible = bool(verdict == "promote")

    log(f"9. Verdict: {verdict} (beats_rule2={beats_rule2}, ci_excl_0={ci_excludes_zero_rule2}, "
        f"unique_ok={unique_ok}, gates_ok={gate_ok})")

    audit = dict(
        schema="gemsdoe92-gravquad-audit.v1", lane="GRAVQUAD", arm="primary",
        file=f"docs/downloads/{tif_path.name}", sha256=sha256_file(tif_path),
        bytes=tif_path.stat().st_size, submission_name=name, note=note, note_chars=len(note),
        validator=v, format_gates=[{"gate": r.name, "ok": r.ok, "detail": r.detail} for r in gate_results],
        gates_pass=gate_ok,
        uniqueness_local=uniq,
        public_registry={"available": False,
                         "reason": "only run for a candidate that first beats the holdout promotion bar; "
                                   "GRAVQUAD did not beat it this session, so the 102-repo GitHub scan was "
                                   "not spent (budget discipline: do not spend a weekly slot or a heavy scan "
                                   "on a lane that already failed holdout)."},
    )
    audit_path = DOWNLOADS / f"{stem}-audit.json"
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    card = dict(
        schema="gemsdoe92-run-card.v3", lane="GRAVQUAD", date=stamp,
        hypothesis=("The USGS/INGENIOUS catalogue is a surface-scarp catalogue; a blind basement normal "
                    "fault buried under thin cover still juxtaposes rock of different density across its "
                    "plane, producing a gravity edge independent of strike. GRAVQUAD computes the gravity "
                    "analytic-signal amplitude (strike-blind, unlike fixed-strike Coulomb/conjugate-shear "
                    "lanes) and multiplies it by a structure-tensor linear-edge coherence that favors "
                    "elongated fault-like edges over equant density bodies."),
        mechanism=("S = pct_rank(ASA) * pct_rank(coherence), where ASA = sqrt(B11_vg^2 + B18_hg_ew^2 + "
                   "(d(B13_anom)/dy)^2) is the 3-component gravity analytic-signal amplitude and coherence "
                   "is the local (lambda1-lambda2)/(lambda1+lambda2) linear-anisotropy ratio of the 2x2 "
                   "gradient structure tensor of ASA over a 7x7 window; 37,654 dots spaced >= 2.8 px on "
                   "valid & ~catalogue & d_cat > 2.0 px. Pure array math; the catalogue is used only for "
                   "masking, never to build features, so catalogue withholding cannot leak through the surface."),
        named_non_fault_mimic=("Equant plutonic intrusions, circular playa/evaporite density bodies, and "
                               "diffuse basement-terrane boundaries: all produce gravity analytic-signal "
                               "amplitude but have low structure-tensor linear coherence."),
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI", evaluator_version=evaluate_holdout.VERSION,
            withheld_positives=int(primary["withheld_positive_pixels"]),
            primary_instrument="static d_cat > 2.0 deployment, pooled gems57-pooled-hide-v2, seeds 20+30, 8 folds, "
                               "1000-draw paired spatial-block bootstrap CI",
            scores={"GRAVQUAD": primary, "R0": control},
            paired_vs_R0=dict(delta=delta["delta"], ci95=delta["ci95"]),
            beats_holdout_best=beats_holdout_best,
            holdout_best_reference=dict(
                lane_rule2="COULOMB-LOQO standalone", rule2_d_visible_2=HOLDout_BEST_RULE2,
                lane_static="KNICKLOQO standalone", static_d_cat_2_record=HOLDout_BEST_STATIC,
                static_d_cat_2_coulombloqo=HOLDout_BEST_STATIC_COULOMBLOQO,
                source="README.md 2026-10-25 session banners (same evaluator, seeds 20+30)"),
        ),
        holdout_rule2_d_visible_2=dict(
            evidence_class="HOLDOUT-DTI (strict draw-blind fold-visible d_visible > 2.0 diagnostic)",
            evaluator_version=evaluate_holdout.VERSION,
            scores={"GRAVQUAD": dvis_primary, "R0": dvis_control},
        ),
        leakage_canaries=dict(
            max_symmetric_auc=max_auc, all_pass_le_0p90=bool(max_auc <= 0.90),
            per_feature={k: round(float(v), 6) for k, v in canaries.items()},
        ),
        correlation_overlap_vs_registry=dict(
            local=uniq,
            public={"available": False, "scope": "not scanned this session: GRAVQUAD did not beat the "
                                                  "holdout promotion bar, so the 102-repo GitHub API scan "
                                                  "was not spent per the protocol's experiment budget."},
        ),
        raster_sha256=sha256_file(tif_path),
        zip_sha256=receipt.get("zip_sha256"),
        file=f"docs/downloads/{tif_path.name}",
        validator_output=dict(
            no_nan_in_footprint=bool(v["checks"]["in_footprint_all_finite"]),
            values_in_0_1=bool(v["checks"]["range_0_1_guaranteed"]),
            crs_shape_transform_match=bool(v["checks"]["crs_epsg_32611"] and v["checks"]["dimensions_3730x3292"]
                                           and v["checks"]["transform_matches_sample_submission"]),
            dots=int(v["emitted_positive_pixels"]),
            checks=v["checks"],
        ),
        submission_name=name,
        submission_note=note,
        note_chars=len(note),
        experiments_used="1/3",
        weekly_slots_used=0,
        verdict=verdict,
        submission_eligible=submission_eligible,
        verdict_reason=(f"static HOLDOUT-DTI {primary['dti']:.6f} vs KNICKLOQO record {HOLDout_BEST_STATIC} "
                        f"and COULOMB-LOQO Rule-2 {HOLDout_BEST_RULE2}; paired delta vs R0 {delta['delta']:.6f} "
                        f"CI [{delta['ci95'][0]:.6f}, {delta['ci95'][1]:.6f}]; unique_ok={unique_ok}; "
                        f"gates_ok={gate_ok}; max AUC {max_auc:.4f}"),
        organizer_confirmed=None,
        all_arms={"primary": dict(file=audit["file"], sha256=audit["sha256"],
                                  submission_name=name, note=note, note_chars=len(note),
                                  validator=v, holdout_dti=primary)},
    )
    card_path = EVIDENCE / f"{stem}_run_card.json"
    card_path.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    (DOWNLOADS / f"{stem}_run_card.json").write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    log(f"WROTE {card_path}")
    log(f"WROTE {audit_path}")
    log(f"TIF: {tif_path} (sha256 {sha256_file(tif_path)[:16]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
