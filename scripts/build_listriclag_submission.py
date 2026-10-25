#!/usr/bin/env python3
"""LISTRICLAG lane build: unique submission GeoTIFF + autonomous validation.

Pre-registration: docs/HYPOTHESES_20261025_LISTRICLAG.md (Rank 1; 3 arms).

Pipeline (no manual step; network only via the separately staged registry cache):
  1. Restore-check pinned inputs (.cache/gems_inputs, SHA-256 verified by
     scripts/restore_inputs.py).
  2. Build the LISTRICLAG surfaces from the pinned 19-band stack, bands
     11/12/15/18/19 (gems/listriclag.py): ring-coupled S and co-located
     ablation S_local.
  3. Arms (pre-registered):
       E1 LISTRICLAG       binary 37,654 unit dots on S
       E2 LISTRICLAG_LOCAL binary 37,654 unit dots on S_local (ablation)
       E3 LISTRICLAG_N90K  90,000 spaced dots on S; prefix 37,654 at 1.0,
                           remainder at 0.30 (emission-policy probe)
     All spacing >= 2.8 px; deployment placement on valid & ~catalogue &
     d_cat > 2.0 px; holdout placement rebuilt per fold from visible faults.
  4. Package primary via vendor/gems57/submission_writer.py (zeros-outside,
     float32, EPSG:32611, 3730x3292, pinned transform, [0,1], zero catalogue
     mass). N90K packaged as a secondary artifact for the record.
  5. Format gates: gems.gates.run_gates (require_submission_encoding) +
     gems57.validate, independent disk re-read.
  6. HOLDOUT-DTI: gems57-pooled-hide-v2, buffered whole-component quadrant
     draw (seeds 20+30, 8 folds, 1.2 km guard, 500 m feature buffer), pooled
     DTI + 1000-draw paired spatial-block bootstrap CI vs R0 control, strict
     Rule-2 hide-and-recover placement rebuilt from visible faults per fold.
  7. Leakage canaries: symmetric AUC of each feature vs pooled withheld
     truth; require <= 0.90 (Protocol Rule 4).
  8. Uniqueness (REGISTRY-MEASUREMENT): complete local registry (served +
     release + bridge rasters), literal + matched-budget 3 px overlap and
     |Spearman rho| on the pre-placement surface; dense-witness specificity
     if the public cache holds the 17GEMSDOE witness. The binding public
     scan runs separately (scripts/audit_public_registry.py --cache-only)
     and is merged by scripts/finalize_listriclag.py.
  9. Write Protocol Rule 5 run card + per-file audit JSON.

Verdict logic: promote only if primary strict fold-visible HOLDOUT-DTI beats
holdout-best (COULOMB-LOQO standalone 0.113316 Rule-2) with paired-vs-R0 CI
excluding 0 AND uniqueness passes (local here; public merged by the finalize
step, which can only downgrade). Otherwise verdict = negative — still a
deliverable: a format-valid unique research TIF, 0 weekly slots.
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
from listriclag import lane_surface  # noqa: E402

N_DOTS = 37_654
N_EXT = 90_000
P_TAIL = 0.30
MIN_DIST_PX = 2.8
STACK = INPUTS / "training_features.tif"
HOLDOUT_BEST_RULE2 = 0.113316   # COULOMB-LOQO standalone, strict draw-blind d_visible > 2.0
HOLDOUT_BEST_STATIC = 0.010788  # KNICKLOQO standalone, static d_cat > 2.0


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
    ranks = rankdata(np.concatenate([pos, neg]), method="average").astype(np.float64)
    auc = (ranks[: pos.size].sum() - pos.size * (pos.size + 1) / 2.0) / (pos.size * neg.size)
    return float(max(auc, 1.0 - auc))


def place_arms(surfaces, candidate):
    """Per-mask placement for all three pre-registered arms."""
    from gems import breakline
    dots_ring = breakline.spaced_top_mask(surfaces["S"], candidate, N_DOTS,
                                          min_dist_px=MIN_DIST_PX, cand_cap=900_000)
    dots_local = breakline.spaced_top_mask(surfaces["S_local"], candidate, N_DOTS,
                                           min_dist_px=MIN_DIST_PX, cand_cap=900_000)
    dots_ext = breakline.spaced_top_mask(surfaces["S"], candidate, N_EXT,
                                         min_dist_px=MIN_DIST_PX, cand_cap=900_000)
    # Deterministic greedy => the 37,654-dot selection is a prefix of the 90,000-dot one.
    if not (dots_ring & dots_ext).sum() == dots_ring.sum():
        raise AssertionError("greedy prefix property violated; N90K arm must contain the primary dots")
    pred_ext = np.where(dots_ext, np.float32(P_TAIL), np.float32(0.0))
    pred_ext[dots_ring] = 1.0
    return {
        "LISTRICLAG": dots_ring.astype(np.float32),
        "LISTRICLAG_LOCAL": dots_local.astype(np.float32),
        "LISTRICLAG_N90K": pred_ext,
    }


def build_holdout_terms(grid, surfaces, valid, r0_arr):
    """Strict hide-and-recover: rebuild every arm's placement per fold from visible faults only."""
    folds = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
    log(f"holdout: {len(folds)} folds (2 seeds x 4 quadrants); rebuilding placement from visible faults")

    arm_names = ["LISTRICLAG", "LISTRICLAG_LOCAL", "LISTRICLAG_N90K", "R0"]
    terms_by_arm = {n: None for n in arm_names}
    per_fold = {n: [] for n in arm_names}
    for i, fold in enumerate(folds):
        visible = np.asarray(fold["visible"], bool)
        d_visible = distance_transform_edt(~visible)
        candidate = valid & ~visible & (d_visible > 2.0)
        preds = place_arms(surfaces, candidate)
        preds["R0"] = r0_arr.astype(np.float32)
        for arm in arm_names:
            score, terms = evaluate_holdout.evaluate(preds[arm], fold, grid.footprint)
            per_fold[arm].append(round(float(score["dti"]), 6))
            old = terms_by_arm[arm]
            terms_by_arm[arm] = terms if old is None else old + terms
        log(f"  fold {i+1}/8 done: " + " ".join(f"{a}={per_fold[a][-1]:.4f}" for a in arm_names))
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
    sub = np.sort(np.random.default_rng(20261025).choice(foot_idx, size=400_000, replace=False))
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
        k = int((cand_dots > 0).sum())
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
    dup = bool(worst_mb["matched_budget_forward_overlap"] > 0.70 or abs(worst_rho["spearman_surface"] or 0.0) > 0.90)
    return dict(
        evidence_class="REGISTRY-MEASUREMENT",
        rasters_checked=len(checked),
        worst_literal_forward_overlap=float(worst_lit["literal_forward_overlap"]),
        worst_literal_file=worst_lit["file"],
        worst_matched_budget_forward_overlap=float(worst_mb["matched_budget_forward_overlap"]),
        worst_matched_budget_file=worst_mb["file"],
        worst_abs_spearman=abs(float(worst_rho["spearman_surface"] or 0.0)),
        worst_abs_spearman_file=worst_rho["file"],
        duplicate=dup,
        verdict="negative" if dup else "unique",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stem", default=None, help="output stem (default timestamped)")
    args = ap.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = args.stem or f"gemsdoe92-listriclag-{stamp}"
    tif_path = DOWNLOADS / f"{stem}-zeros.tif"
    tif_ext_path = DOWNLOADS / f"{stem}-n90k-zeros.tif"

    log("0. Load pinned grid (footprint + catalogue)")
    grid = grid_mod.load_grid(BRIDGE)
    foot, cat = grid.footprint, grid.catalogue
    with rasterio.open(BRIDGE / "sample_submission.tif") as ref:
        expected = (ref.shape, ref.crs, ref.transform)
    d_cat = distance_transform_edt(~cat)

    log("1. Build LISTRICLAG surfaces (bands 11/12/15/18/19: annulus scarp evidence x basement edge x gravity edge)")
    surf = lane_surface(str(STACK), foot)
    valid, S = surf["valid"], surf["S"]

    # Persist the pre-placement surface for the public registry audit (--surface).
    surface_tif = INPUTS / "listriclag_surface.tif"
    grid_mod.write_geotiff(surface_tif, np.where(foot, S, 0).astype(np.float32), nodata=None)
    log(f"  pre-placement surface written: {surface_tif}")

    log("2. Deployment placement: valid & ~catalogue & d_cat > 2.0, spaced >= 2.8 px (3 arms)")
    cand = valid & ~cat & (d_cat > 2.0)
    preds = place_arms(surf, cand)
    dots_arr = preds["LISTRICLAG"]
    log(f"  primary dots={int((dots_arr > 0).sum())} on-catalogue={int(((dots_arr > 0) & cat).sum())} "
        f"outside-footprint={int(((dots_arr > 0) & ~foot).sum())}; "
        f"N90K positives={int((preds['LISTRICLAG_N90K'] > 0).sum())}")

    r0_path = ROOT / "data" / "parent_R0_zeros.tif"
    with rasterio.open(r0_path) as ds:
        r0_arr = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot

    log("3. Package primary + N90K via submission_writer (zeros-outside, [0,1], pinned grid)")
    name = f"GEMSDOE92-LISTRICLAG-{stamp[:8]}"
    note = ("h33-h33-2-b2; LISTRICLAG: 37654 dots, annulus(2.8-8px) scarp evidence x basement-step "
            "x gravity edge; listric updip-lag lane")
    name_ext = f"GEMSDOE92-LISTRICLAG-N90K-{stamp[:8]}"
    note_ext = ("h33-h33-2-b2; LISTRICLAG N90K: 90000 dots (top 37654 @1.0, tail @0.30); "
                "extended-budget emission probe")
    for s in (note, note_ext, name, name_ext):
        assert len(s) <= 140, s
    receipt = submission_writer.write_submission(
        tif_path, dots_arr, BRIDGE / "sample_submission.tif", foot,
        note=note, name=name, catalogue=cat,
        metadata=dict(lane="LISTRICLAG", arm="primary",
                      hypothesis_doc="docs/HYPOTHESES_20261025_LISTRICLAG.md"))
    receipt_ext = submission_writer.write_submission(
        tif_ext_path, preds["LISTRICLAG_N90K"], BRIDGE / "sample_submission.tif", foot,
        note=note_ext, name=name_ext, catalogue=cat,
        metadata=dict(lane="LISTRICLAG", arm="N90K",
                      hypothesis_doc="docs/HYPOTHESES_20261025_LISTRICLAG.md"))

    log("4. Independent disk re-read validation + format gates (both artifacts)")
    v = V.validate(tif_path, foot, cat)
    V.assert_submittable(v)
    v_ext = V.validate(tif_ext_path, foot, cat)
    V.assert_submittable(v_ext)
    from gems.gates import run_gates, summarise  # noqa: E402
    gate_results = run_gates(str(tif_path), str(BRIDGE / "sample_submission.tif"),
                             str(BRIDGE / "existing_faults.tif"), prune_radius=2,
                             require_submission_encoding=True)
    gate_ok, gate_report = summarise(gate_results)
    log(f"  primary format gates: {'PASS' if gate_ok else 'FAIL'}")

    log("5. HOLDOUT-DTI (gems57-pooled-hide-v2, seeds 20+30, strict fold-visible rebuild, 4 arms)")
    terms_by_arm, per_fold, folds = build_holdout_terms(grid, surf, valid, r0_arr)
    pooled = evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810,
                                             candidate="LISTRICLAG")
    primary = pooled["scores"]["LISTRICLAG"]
    ablation = pooled["scores"]["LISTRICLAG_LOCAL"]
    extended = pooled["scores"]["LISTRICLAG_N90K"]
    control = pooled["scores"]["R0"]
    delta_r0 = pooled["paired_differences"]["R0"]
    delta_local = pooled["paired_differences"]["LISTRICLAG_LOCAL"]
    for lab, sc in (("LISTRICLAG", primary), ("LOCAL ablation", ablation),
                    ("N90K", extended), ("R0 control", control)):
        log(f"  {lab}: {sc['dti']:.6f} CI [{sc['ci95'][0]:.6f}, {sc['ci95'][1]:.6f}]")
    log(f"  paired vs R0: {delta_r0['delta']:.6f} CI [{delta_r0['ci95'][0]:.6f}, {delta_r0['ci95'][1]:.6f}]")
    log(f"  paired ring-vs-local: {delta_local['delta']:.6f} CI [{delta_local['ci95'][0]:.6f}, {delta_local['ci95'][1]:.6f}]")

    log("6. Leakage canaries: symmetric AUC per feature vs pooled withheld truth")
    truth_pool = np.zeros(foot.shape, bool)
    for fold in folds:
        truth_pool |= np.asarray(fold["truth"], bool)
    canaries = {}
    for feat_name in ("terrain_ring", "terrain_local", "basement_edge", "grav_edge", "S", "S_local"):
        canaries[feat_name] = auc_sym(surf[feat_name][foot], truth_pool[foot])
    max_auc = max(canaries.values())
    log(f"  canary max symmetric AUC = {max_auc:.4f}")

    log("7. Uniqueness vs complete local registry (literal + matched-budget + |rho|)")
    registry = local_registry(exclude_stems=(stem,))
    log(f"  {len(registry)} local rasters")
    rows = compare_to_local(dots_arr, S, foot, registry, expected)
    uniq = dual_reading(rows)
    log(f"  primary: worst MB={uniq['worst_matched_budget_forward_overlap']:.4f} "
        f"({uniq['worst_matched_budget_file']}), lit={uniq['worst_literal_forward_overlap']:.4f} "
        f"({uniq['worst_literal_file']}), |rho|={uniq['worst_abs_spearman']:.4f} "
        f"({uniq['worst_abs_spearman_file']}), duplicate={uniq['duplicate']}")
    rows_ext = compare_to_local(preds["LISTRICLAG_N90K"], S, foot, registry, expected)
    uniq_ext = dual_reading(rows_ext)
    log(f"  N90K: worst MB={uniq_ext['worst_matched_budget_forward_overlap']:.4f}, "
        f"duplicate={uniq_ext['duplicate']}")

    # Dense-witness specificity (17GEMSDOE E-proba-multiscale) if cached.
    specificity = None
    witness_path = ROOT / ".cache" / "gemsdoe_public_registry" / "374c88b1da2b803e2ed160de467fd71ae114010d.tif"
    if witness_path.is_file():
        with rasterio.open(witness_path) as ds:
            wv = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)
        spec_dots = U.dual_overlap(dots_arr, wv, foot)
        spec_r0 = U.dual_overlap(r0_arr, wv, foot)
        specificity = dict(
            witness="17GEMSDOE E-proba-multiscale (git blob 374c88b1...)",
            witness_positive_footprint_cells=int(((wv > 0) & foot).sum()),
            LISTRICLAG_literal_overlap=spec_dots["literal_forward_overlap"],
            LISTRICLAG_matched_budget_overlap=spec_dots["matched_budget_forward_overlap"],
            R0_parent_literal_overlap=spec_r0["literal_forward_overlap"],
            R0_parent_matched_budget_overlap=spec_r0["matched_budget_forward_overlap"],
        )
        log(f"  dense-witness: lit={spec_dots['literal_forward_overlap']:.3f} "
            f"mb={spec_dots['matched_budget_forward_overlap']:.3f}; "
            f"R0 lit={spec_r0['literal_forward_overlap']:.3f}")

    beats_rule2 = primary["dti"] > HOLDOUT_BEST_RULE2
    ci_excludes_zero = delta_r0["ci95"][0] > 0
    canaries_ok = max_auc <= 0.90
    unique_ok = (not uniq["duplicate"])
    verdict = "promote" if (beats_rule2 and ci_excludes_zero and canaries_ok and unique_ok and gate_ok) else "negative"
    log(f"8. Verdict (local phase): {verdict} (beats_rule2={beats_rule2}, ci_excl_0={ci_excludes_zero}, "
        f"canaries_ok={canaries_ok}, unique_ok={unique_ok}, gates_ok={gate_ok}); "
        f"public scan merged by finalize_listriclag.py (can only downgrade)")

    audit = dict(
        schema="gemsdoe92-listriclag-audit.v1", lane="LISTRICLAG", arm="primary",
        file=f"docs/downloads/{tif_path.name}", sha256=sha256_file(tif_path),
        bytes=tif_path.stat().st_size, submission_name=name, note=note, note_chars=len(note),
        validator=v, format_gates=[{"gate": r.name, "ok": r.ok, "detail": r.detail} for r in gate_results],
        gates_pass=gate_ok, uniqueness_local=uniq, uniqueness_local_rows=rows,
        n90k=dict(file=f"docs/downloads/{tif_ext_path.name}", sha256=sha256_file(tif_ext_path),
                  validator=v_ext, uniqueness_local=uniq_ext),
        dense_witness_specificity=specificity,
        public_registry={"status": "pending", "merged_by": "scripts/finalize_listriclag.py"},
    )
    (DOWNLOADS / f"{stem}-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    card = dict(
        schema="gemsdoe92-run-card.v3", lane="LISTRICLAG", date=stamp,
        session_budget=dict(experiments_used="3/3 (primary + LOCAL ablation + N90K probe)",
                            weekly_slots_used=0),
        hypothesis=("Listric/planar Basin-and-Range normal faults dip 45-60 deg, so the buried basement "
                    "density step images 200-800 m basinward of the surface scarp. Scarp-degraded or "
                    "buried faults keep the offset basement step while the scarp-mapped USGS/INGENIOUS "
                    "catalogue misses them; coupling basement-edge evidence with the strongest scarp "
                    "evidence in a 2.8-8 px annulus (instead of the same pixel) targets exactly that blind spot."),
        mechanism=("Label-free cube-root product of (1) annulus-maximum (2.8-8 px) multi-scale detrended-"
                   "elevation scarp evidence (Bands 12/19), (2) depth-to-basement gradient (Band 15, sigma 3), "
                   "(3) gravity-gradient edge confirmation (|B18 HG| x |B11 VG| rank product). Placement per "
                   "holdout fold rebuilt from fold-visible faults only; deployment dots at d_cat > 2.0 px."),
        named_non_fault_mimic=("Fan-toe/piedmont junctions beside basin-margin onlap density contacts; "
                               "pluvial Lake Lahontan shoreline risers near lithologic density steps; "
                               "DEM seams near gravity survey edges."),
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI", evaluator_version=evaluate_holdout.VERSION,
            withheld_positives=int(primary["withheld_positive_pixels"]),
            primary_instrument=("strict fold-visible rebuild d_visible > 2.0, pooled gems57-pooled-hide-v2, "
                                "seeds 20+30, 8 folds, 1000-draw paired spatial-block bootstrap CI"),
            scores={"LISTRICLAG": primary, "LISTRICLAG_LOCAL": ablation,
                    "LISTRICLAG_N90K": extended, "R0": control},
            per_fold=per_fold,
            paired_vs_R0=dict(delta=delta_r0["delta"], ci95=delta_r0["ci95"]),
            paired_ring_vs_local=dict(delta=delta_local["delta"], ci95=delta_local["ci95"]),
            beats_holdout_best=bool(beats_rule2 and ci_excludes_zero),
            holdout_best_reference=dict(
                rule2_d_visible_2=dict(lane="COULOMB-LOQO standalone", dti=HOLDOUT_BEST_RULE2),
                static_d_cat_2=dict(lane="KNICKLOQO standalone", dti=HOLDOUT_BEST_STATIC)),
        ),
        leakage_canaries=dict(
            max_symmetric_auc=float(max_auc), all_pass_le_0p90=bool(canaries_ok),
            per_feature={k: round(float(x), 6) for k, x in canaries.items()},
        ),
        correlation_overlap_vs_registry=dict(
            local=uniq, local_n90k=uniq_ext,
            public={"status": "pending", "merged_by": "scripts/finalize_listriclag.py"},
            dense_witness_specificity=specificity,
        ),
        raster_sha256=sha256_file(tif_path),
        zip_sha256=receipt.get("zip_sha256"),
        file=f"docs/downloads/{tif_path.name}",
        n90k_file=f"docs/downloads/{tif_ext_path.name}",
        n90k_raster_sha256=sha256_file(tif_ext_path),
        n90k_zip_sha256=receipt_ext.get("zip_sha256"),
        validator_output=dict(
            no_nan_in_footprint=bool(v["checks"]["in_footprint_all_finite"]),
            values_in_0_1=bool(v["checks"]["range_0_1_guaranteed"]),
            crs_shape_transform_match=bool(v["checks"]["crs_epsg_32611"] and v["checks"]["dimensions_3730x3292"]
                                           and v["checks"]["transform_matches_sample_submission"]),
            dots=int(v["emitted_positive_pixels"]),
            checks=v["checks"],
        ),
        submission_name=name, submission_note=note, note_chars=len(note),
        experiments_used="3/3", weekly_slots_used=0,
        verdict=verdict, submission_eligible=bool(verdict == "promote"),
        verdict_reason=(f"strict fold-visible HOLDOUT-DTI {primary['dti']:.6f} vs holdout-best "
                        f"{HOLDOUT_BEST_RULE2} (Rule-2); paired-vs-R0 delta {delta_r0['delta']:.6f} "
                        f"CI [{delta_r0['ci95'][0]:.6f}, {delta_r0['ci95'][1]:.6f}]; ring-vs-local delta "
                        f"{delta_local['delta']:.6f}; unique_ok={unique_ok}; gates_ok={gate_ok}; "
                        f"max canary AUC {max_auc:.4f}; public scan pending"),
        organizer_confirmed=None,
    )
    card_path = EVIDENCE / f"{stem}_run_card.json"
    card_path.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    (DOWNLOADS / f"{stem}_run_card.json").write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    log(f"WROTE {card_path}")
    log(f"TIF: {tif_path} (sha256 {sha256_file(tif_path)[:16]}...)")
    log(f"TIF: {tif_ext_path} (sha256 {sha256_file(tif_ext_path)[:16]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
