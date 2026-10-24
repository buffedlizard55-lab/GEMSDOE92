#!/usr/bin/env python3
"""REPORT ONLY instruments for STEPEDGE variants (2026-10-24).

Same five labelled readouts as scripts/report_breakline_proxies.py:
1. HOLDOUT-DTI (gems57-pooled-hide-v2; seeds 20+30; 22,663 withheld px)
   vs R0, RELIEF p10 (holdout best, duplicate), BREAKLINE f45, ANASIG f45,
   STRAINBREAK f60 (best locally unique) -- identical folds for every arm.
2. SGMC off-catalogue control PROXY (62,703 px).
3. Fixed-catalogue diagnostic (explicitly not a holdout).
4. Single-feature leakage canaries (stop if symmetric AUC > 0.90).
5. Uniqueness: final dots vs every local registry raster (shared
   uniqueness() from report_breakline_proxies), PLUS pre-placement surface
   sampled Spearman vs the same registry (actual persisted surface,
   .cache/stepedge_surface_pct.tif, hash-checked against the build receipt).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import verify_all_manifests
from gems.breakline import lane_surface as breakline_surface, percentile_rank
from gems.stepedge import lane_surface as stepedge_surface
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric
from report_breakline_proxies import load_mask, uniqueness


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def surface_uniqueness(surface: np.ndarray, foot: np.ndarray,
                       own_ids: set[str], n_sample: int = 300_000) -> dict:
    """Sampled Spearman of the CONTINUOUS pre-placement surface vs registry."""
    registry_paths: list[Path] = [
        ROOT / "data/parent_R0_zeros.tif", ROOT / "data/bridge/h19_5.tif",
        ROOT / "data/bridge/d28.tif", ROOT / "data/bridge/h27_4_solo.tif",
        ROOT / "data/bridge/sample_submission.tif", ROOT / "data/bridge/labels.tif",
    ]
    registry_paths += sorted((ROOT / "docs/downloads").glob("*-zeros.tif"))
    registry_paths += sorted((ROOT / "releases").glob("*-zeros.tif"))
    registry_paths += sorted((ROOT / "releases").glob("*STEPOVER*.tif"))
    rng = np.random.default_rng(12345)
    foot_idx = np.flatnonzero(foot)
    sample = rng.choice(foot_idx, size=min(n_sample, len(foot_idx)), replace=False)
    surf_vals = np.nan_to_num(surface.ravel()[sample], nan=0.0)
    rows, seen = [], set()
    for p in registry_paths:
        if not p.is_file() or p.name in own_ids:
            continue
        theirs = load_mask(p, foot)
        key = np.packbits(theirs).tobytes()
        if key in seen or not theirs.any():
            continue
        seen.add(key)
        rho = float(spearmanr(surf_vals, theirs.ravel()[sample].astype(float)).statistic)
        rows.append({"registry_file": p.name, "their_dots": int(theirs.sum()),
                     "sampled_spearman": round(rho, 6)})
        del theirs
    worst = max(rows, key=lambda r: abs(r["sampled_spearman"]))
    return {"evidence_class": "REGISTRY-MEASUREMENT",
            "n_sampled_footprint_px": int(len(sample)), "seed": 12345,
            "registry_rasters_checked": len(rows),
            "worst_abs_sampled_spearman": abs(worst["sampled_spearman"]),
            "worst_file": worst["registry_file"],
            "duplicate_by_rho_gt_0p90": bool(abs(worst["sampled_spearman"]) > 0.90),
            "rows": rows}


def main() -> int:
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(ROOT / ".cache/gems_inputs/bridge")
    foot, cat = grid.footprint, grid.catalogue

    receipt = json.loads((ROOT / "evidence/stepedge_variants.json").read_text())
    arms: dict[str, np.ndarray] = {}
    with rasterio.open(paths["parent_r0_zeros"]) as ds:
        arms["R0"] = (ds.read(1) > 0) & foot
    arms["RELIEFp10"] = load_mask(ROOT / "docs/downloads/h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24-zeros.tif", foot)
    arms["BREAKLINEf45"] = load_mask(ROOT / "docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif", foot)
    arms["ANASIGf45"] = load_mask(ROOT / "docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif", foot)
    arms["STRAINBREAKf60"] = load_mask(ROOT / "docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif", foot)
    own_files = set()
    cand_names = []
    for item in receipt["variants"]:
        arms[item["value"]] = load_mask(ROOT / "releases" / item["fallback_file"], foot)
        own_files.update((item["fallback_file"], item["primary_file"]))
        cand_names.append(item["value"])

    # ---- 1. pooled holdout
    folds, split_receipts = [], []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})
    terms_by_arm, per_arm = {}, {}
    for name, mask in arms.items():
        all_terms, per_arm[name] = None, []
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(mask.astype(np.float32), fold, foot)
            per_arm[name].append(float(score["dti"]))
            all_terms = terms if all_terms is None else all_terms + terms
        terms_by_arm[name] = all_terms
    pooled_by_candidate = {c: evaluate_holdout.pooled_summary(
        terms_by_arm, draws=1000, seed=520810, candidate=c) for c in cand_names}
    pooled = pooled_by_candidate[cand_names[-1]]

    # ---- 2. canaries
    rng = np.random.default_rng(520810)
    y_parts, sample_idx = [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & foot)
        neg = np.flatnonzero(fold["region"] & foot & ~cat)
        n = min(len(neg), max(1, 2 * len(pos)))
        neg = rng.choice(neg, size=n, replace=False) if len(neg) > n else neg
        sample_idx.extend((pos, neg))
        y_parts.extend((np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)))
    y, flat_idx = np.concatenate(y_parts), np.concatenate(sample_idx)

    with rasterio.open(paths["training_features"]) as ds:
        b12 = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    valid_topo = foot & np.isfinite(b12) & (b12 > -1e30) & np.isfinite(b19) & (b19 > -1e30)
    se = stepedge_surface(b12, valid_topo)
    bl = breakline_surface(b12, b19, valid_topo)
    feature_arrays = {
        "stepedge_step_pct_BUILT": se["step_pct"],
        "stepedge_S_pct_coherence_gated_NOT_BUILT": se["S_pct"],
        "stepedge_step_near_pct": percentile_rank(se["step_by_group"][0], valid_topo),
        "stepedge_step_far_pct": percentile_rank(se["step_by_group"][1], valid_topo),
        "stepedge_coherence": se["coherence"],
        "breakline_L_pct_CONTROL": bl["L_pct"],
        "training_band_12_det_elev": b12,
        "training_band_19_det_elev_slope": b19,
    }
    canaries = {}
    for name, arr in feature_arrays.items():
        vals = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat_idx]
        auc = float(roc_auc_score(y, vals))
        canaries[name] = {"auc": round(auc, 6), "symmetric_auc": round(max(auc, 1 - auc), 6),
                          "status": "INVESTIGATE" if max(auc, 1 - auc) > 0.90 else "REPORT_ONLY_PASS"}
    del se, bl, b12, b19

    # ---- 3/4. SGMC + fixed-catalogue
    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_scores = {k: round(float(metric.dti_binary(m, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
                   for k, m in arms.items()}
    catdiag = {k: round(float(metric.dti_binary(m, cat, valid=foot, known=None)["dti"]), 6)
               for k, m in arms.items()}

    # ---- 5. uniqueness: final dots + pre-placement surface
    uniq_arms = {k: arms[k] for k in ["R0", "RELIEFp10", *cand_names]}
    uniq = uniqueness(uniq_arms, foot, own_files)
    surface_path = ROOT / ".cache/stepedge_surface_pct.tif"
    surf_sha = sha256_file(surface_path)
    assert surf_sha == receipt["lane_surface"]["preplacement_surface_sha256"], "surface drift"
    with rasterio.open(surface_path) as ds:
        surface = ds.read(1)
    surf_uniq = surface_uniqueness(surface, foot, own_files)

    report = {
        "evidence_label": "PROXY", "created_utc": "20261024", "axis": "STEPEDGE",
        "purpose": ("Pooled HOLDOUT-DTI, leakage canaries, SGMC off-catalogue control, "
                    "fixed-catalogue diagnostic, and literal-rule uniqueness on the "
                    "pre-placement surface and final dots for STEPEDGE variants."),
        "parent": "h33-h33-2-b2",
        "hide_and_recover_pooled_summary": pooled,
        "hide_and_recover_pooled_by_candidate": pooled_by_candidate,
        "holdout_splits": split_receipts,
        "per_arm_fold_scores": per_arm,
        "leakage_canaries": {
            "definition": "symmetric AUC on withheld positives vs in-region non-catalogue negatives (seeds 20/30 folds, rng 520810)",
            "features": canaries,
            "max_symmetric_auc": max(c["symmetric_auc"] for c in canaries.values()),
        },
        "sgmc_control": {"truth_pixels": int(sgmc_truth.sum()), "dti_by_arm": sgmc_scores,
                         "delta_vs_r0": {k: round(v - sgmc_scores["R0"], 6) for k, v in sgmc_scores.items()}},
        "fixed_catalogue_diagnostic_NOT_A_HOLDOUT": catdiag,
        "uniqueness_final_dots": uniq,
        "uniqueness_preplacement_surface": {
            "surface_file": ".cache/stepedge_surface_pct.tif (gitignored cache)",
            "surface_sha256": surf_sha, **surf_uniq},
        "warning": "HOLDOUT-DTI/PROXY diagnostics only; never a leaderboard score or projection.",
    }
    out = ROOT / "evidence/stepedge_proxy_audit.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    scores = pooled["scores"]
    print(json.dumps({
        "holdout_dti": {k: round(v["dti"], 6) for k, v in scores.items()},
        "ci95": {k: [round(x, 6) for x in v["ci95"]] for k, v in scores.items()},
        "paired_vs_R0": {c: pooled_by_candidate[c]["paired_differences"].get("R0") for c in cand_names},
        "sgmc": sgmc_scores, "fixedcat": catdiag,
        "canary_max": report["leakage_canaries"]["max_symmetric_auc"],
        "uniq_final": {k: {"worst_fwd": v["worst_forward_overlap"], "worst_rho": v["worst_abs_spearman"],
                           "duplicate": v["duplicate"], "n": v["registry_rasters_checked"]}
                       for k, v in uniq.items()},
        "uniq_surface_worst_rho": surf_uniq["worst_abs_sampled_spearman"],
        "written": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
