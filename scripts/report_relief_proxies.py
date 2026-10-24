#!/usr/bin/env python3
"""REPORT ONLY: catalogue hide-and-recover PROXY, leakage canaries, and SGMC control for RELIEF variants.

No held-out public/private competition labels are used. Positives in hide-and-recover
come solely from buffered whole components of the pinned known-fault catalogue;
SGMC uses the pinned public-domain USGS State Geologic Map Compilation bedrock faults
outside the 3-px catalogue collar. Results are diagnostics ONLY, never gates or scores.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import sha256_file, verify_all_manifests  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric  # noqa: E402


def main() -> int:
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")

    arms: dict[str, np.ndarray] = {}
    with rasterio.open(paths["parent_r0_zeros"]) as ds:
        arms["R0"] = (ds.read(1) > 0) & grid.footprint

    relief_receipt = json.loads((ROOT / "evidence" / "relief_variants.json").read_text(encoding="utf-8"))
    for item in relief_receipt["variants"]:
        with rasterio.open(ROOT / "releases" / item["primary_file"]) as ds:
            arms[item["value"]] = (ds.read(1) > 0) & grid.footprint

    folds = []
    split_receipts = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})

    terms_by_arm: dict[str, np.ndarray] = {}
    per_arm_fold_scores: dict[str, list[float]] = {}
    for arm_name, mask in arms.items():
        all_terms = None
        per_arm_fold_scores[arm_name] = []
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(mask.astype(np.float32), fold, grid.footprint)
            per_arm_fold_scores[arm_name].append(float(score["dti"]))
            all_terms = terms if all_terms is None else all_terms + terms
        assert all_terms is not None
        terms_by_arm[arm_name] = all_terms

    pooled = evaluate_holdout.pooled_summary(
        terms_by_arm, draws=1000, seed=520810, candidate="p12piedmont"
    )

    # Single-feature leakage canaries on known catalogue fold positives
    rng = np.random.default_rng(520810)
    y_parts: list[np.ndarray] = []
    sample_indices: list[np.ndarray] = []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & grid.footprint)
        negmask = fold["region"] & grid.footprint & ~grid.catalogue
        neg = np.flatnonzero(negmask)
        n = min(len(neg), max(1, 2 * len(pos)))
        neg = rng.choice(neg, size=n, replace=False) if len(neg) > n else neg
        sample_indices.extend((pos, neg))
        y_parts.extend((np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)))
    y = np.concatenate(y_parts)
    flat_idx = np.concatenate(sample_indices)

    canaries = {}
    with rasterio.open(paths["training_features"]) as ds:
        b3 = ds.read(3, masked=True).filled(np.nan).astype(np.float32)
        b5 = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b12 = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)

    feature_arrays = {
        "training_band_3_tmi_hg": b3,
        "training_band_5_iso_grav_anom_slope": b5,
        "training_band_12_detrended_elevation": b12,
        "training_band_19_detrended_elevation_slope": b19,
    }
    for name, arr in feature_arrays.items():
        vals = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat_idx]
        auc = float(roc_auc_score(y, vals))
        sym_auc = max(auc, 1.0 - auc)
        canaries[name] = {
            "auc": round(auc, 6),
            "symmetric_auc": round(sym_auc, 6),
            "status": "INVESTIGATE" if sym_auc > 0.90 else "REPORT_ONLY_PASS",
        }

    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & grid.footprint
    sgmc_truth = sgmc & ~grid.catalogue & ~binary_dilation(grid.catalogue, iterations=3)
    sgmc_scores = {
        arm_name: round(
            float(metric.dti_binary(mask, sgmc_truth, valid=grid.footprint, known=grid.catalogue)["dti"]),
            6,
        )
        for arm_name, mask in arms.items()
    }
    r0_sgmc = sgmc_scores["R0"]

    report = {
        "evidence_label": "PROXY",
        "created_utc": "2026-10-24",
        "axis": "RELIEF",
        "purpose": (
            "Report-only catalogue hide-and-recover instrument, single-feature leakage canaries, "
            "and USGS SGMC bedrock fault control proxy for RELIEF variants from parent R0."
        ),
        "parent": "h33-h33-2-b2",
        "hide_and_recover_pooled_summary": pooled,
        "per_arm_fold_scores": per_arm_fold_scores,
        "leakage_canaries": {
            "definition": "symmetric AUC=max(AUC,1-AUC) on hidden known-catalogue positives vs non-catalogue negatives in buffered fold regions",
            "results": canaries,
            "stop_and_investigate_if_any_gt_0_90": any(c["status"] == "INVESTIGATE" for c in canaries.values()),
            "max_symmetric_auc": max(c["symmetric_auc"] for c in canaries.values()),
        },
        "sgmc_control_proxy": {
            "source": "manifest-pinned USGS SGMC derived fault control (https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d, US Public Domain)",
            "truth_pixels_after_catalogue_and_3px_exclusion": int(sgmc_truth.sum()),
            "r0_dti": r0_sgmc,
            "variant_dti": sgmc_scores,
            "variant_deltas_vs_r0": {k: round(v - r0_sgmc, 6) for k, v in sgmc_scores.items()},
        },
        "caution": (
            "These are catalogue/SGMC PROXY diagnostics, never live public scores, private-set scores, "
            "or decision gates. As documented in IRREGULARITIES.md, local catalogue proxies correlate "
            "poorly with live ground-truth changes and serve solely for leakage sanity-checks."
        ),
    }

    out_file = ROOT / "evidence" / "relief_proxy_audit.json"
    out_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote report-only proxy audit to {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
