#!/usr/bin/env python3
"""REPORT ONLY: catalogue hide-and-recover PROXY, leakage canaries, and SGMC control.

No held-out public/private competition labels are used. The only positives in
this file are components from the pinned *known-fault catalogue*, which are
hidden according to the versioned local protocol for a diagnostic only. Results
are not a gate and are never written as a competition score.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "vendor"), str(ROOT / "scripts")]
from build_prune_rungs import sha256_file, verify_inputs  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric  # noqa: E402


def main() -> int:
    paths = verify_inputs()
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    arms: dict[str, np.ndarray] = {"R0": np.zeros(grid.shape, dtype=bool)}
    with rasterio.open(paths["parent_r0_zeros"]) as ds:
        arms["R0"] = (ds.read(1) > 0) & grid.footprint
    receipt = json.loads((ROOT / "evidence" / "prune_rungs.json").read_text())
    for item in receipt["variants"]:
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
        terms_by_arm, draws=1000, seed=520810, candidate="p3.5px-refill"
    )

    # Report-only single-feature leakage canary on withheld known-catalogue
    # components vs non-catalogue background sampled within the same fold region.
    feature_names = {"training_band_3_tmi_hg": 3, "training_band_18_gravity_hg": 18,
                     "training_band_19_detrended_elevation_slope": 19}
    y_parts: list[np.ndarray] = []
    sample_indices: list[np.ndarray] = []
    rng = np.random.default_rng(520810)
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
        for name, band in feature_names.items():
            vals = np.nan_to_num(ds.read(band), nan=0.0).ravel()[flat_idx]
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
        arm_name: round(metric.dti_binary(mask, sgmc_truth, valid=grid.footprint,
                                          known=grid.catalogue)["dti"], 6)
        for arm_name, mask in arms.items()
    }
    r0_score = sgmc_scores["R0"]

    report = {
        "evidence_label": "PROXY",
        "created_utc": "2026-10-23",
        "purpose": "Report-only catalogue hide-and-recover instrument, single-feature leakage canaries, and public-domain SGMC control; none gates the variants.",
        "inputs_verified": {k: {"sha256": sha256_file(v), "bytes": v.stat().st_size}
                            for k, v in paths.items()},
        "holdout_protocol": {
            "implementation": "vendor/gems57/holdout.py buffered_component_draw",
            "evaluator": evaluate_holdout.VERSION,
            "seeds": [20, 30],
            "whole_component_count": sum(len(f["receipt"].get("held_components", []))
                                           if isinstance(f["receipt"].get("held_components"), list) else int(f["receipt"].get("held_components", 0))
                                           for f in folds),
            "withheld_positive_pixels": sum(int(f["truth"].sum()) for f in folds),
            "ci_method": "paired 20 km spatial-block bootstrap, 1,000 draws",
            "scores": pooled,
            "per_fold_dti": per_arm_fold_scores,
            "split_receipts": split_receipts,
        },
        "leakage_canaries": {
            "definition": "symmetric AUC=max(AUC,1-AUC) on hidden known-catalogue positives vs non-catalogue negatives in the same buffered fold regions",
            "features": canaries,
            "max_symmetric_auc": max(x["symmetric_auc"] for x in canaries.values()),
            "stop_and_investigate_if_any_gt_0_90": any(x["symmetric_auc"] > 0.90 for x in canaries.values()),
        },
        "sgmc_control": {
            "evidence_label": "PROXY",
            "source": "manifest-pinned USGS SGMC derived fault control; source URL and license in registry/session_manifest.json",
            "truth_pixels_after_catalogue_and_3px_exclusion": int(sgmc_truth.sum()),
            "dti_by_arm": sgmc_scores,
            "delta_vs_r0": {name: round(score - r0_score, 6) for name, score in sgmc_scores.items()},
        },
        "warning": "These are catalogue/SGMC PROXY diagnostics, not live public scores, not private-set scores, not evidence of win probability, and never pass/fail gates.",
    }
    out = ROOT / "evidence" / "proxy_audit.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "holdout_version": evaluate_holdout.VERSION,
        "withheld_positive_pixels": report["holdout_protocol"]["withheld_positive_pixels"],
        "dti": {n: round(report["holdout_protocol"]["scores"]["scores"][n]["dti"], 6)
                for n in arms},
        "ci95": {n: report["holdout_protocol"]["scores"]["scores"][n]["ci95"]
                 for n in arms},
        "canaries": canaries,
        "sgmc_delta": report["sgmc_control"]["delta_vs_r0"],
        "report": str(out.relative_to(ROOT)),
    }, indent=2))
    return 0 if not report["leakage_canaries"]["stop_and_investigate_if_any_gt_0_90"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
