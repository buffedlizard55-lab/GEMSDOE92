#!/usr/bin/env python3
"""REPORT ONLY: catalogue hide-and-recover PROXY, leakage canaries, and SGMC control for DILATATION variants."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, rasterio
from scipy.ndimage import binary_dilation
from sklearn.metrics import roc_auc_score
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]
from build_snap_scarp_variants import sha256_file, verify_all_manifests
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric

def main() -> int:
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    arms: dict[str, np.ndarray] = {}
    with rasterio.open(paths["parent_r0_zeros"]) as ds:
        arms["R0"] = (ds.read(1) > 0) & grid.footprint
    receipt = json.loads((ROOT / "evidence" / "dilatation_variants.json").read_text(encoding="utf-8"))
    for item in receipt["variants"]:
        with rasterio.open(ROOT / "releases" / item["primary_file"]) as ds:
            arms[item["value"]] = (ds.read(1) > 0) & grid.footprint
    folds = []
    split_receipts = []
    for seed in (20, 30):
        draw,_ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})
    terms_by_arm: dict[str, np.ndarray] = {}
    per_arm_fold_scores: dict[str, list[float]] = {}
    for arm_name, mask in arms.items():
        all_terms=None
        per_arm_fold_scores[arm_name]=[]
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(mask.astype(np.float32), fold, grid.footprint)
            per_arm_fold_scores[arm_name].append(float(score["dti"]))
            all_terms = terms if all_terms is None else all_terms + terms
        assert all_terms is not None
        terms_by_arm[arm_name]=all_terms
    pooled = evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate="p12dilatation")
    # leakage canaries: Band 8 dilatation + others
    rng=np.random.default_rng(520810)
    y_parts=[]; sample_indices=[]
    for fold in folds:
        pos=np.flatnonzero(fold["truth"] & grid.footprint)
        negmask=fold["region"] & grid.footprint & ~grid.catalogue
        neg=np.flatnonzero(negmask)
        n=min(len(neg), max(1, 2*len(pos)))
        neg=rng.choice(neg, size=n, replace=False) if len(neg)>n else neg
        sample_indices.extend((pos,neg))
        y_parts.extend((np.ones(len(pos),np.uint8), np.zeros(len(neg),np.uint8)))
    y=np.concatenate(y_parts)
    flat_idx=np.concatenate(sample_indices)
    canaries={}
    with rasterio.open(paths["training_features"]) as ds:
        b8=ds.read(8, masked=True).filled(np.nan).astype(np.float32)
        b7=ds.read(7, masked=True).filled(np.nan).astype(np.float32)
        b4=ds.read(4, masked=True).filled(np.nan).astype(np.float32)
        b15=ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b17=ds.read(17, masked=True).filled(np.nan).astype(np.float32)
    feature_arrays={
        "training_band_8_geod_dilaterate": b8,
        "training_band_7_geod_shearrate": b7,
        "training_band_4_geod_2ndinv": b4,
        "training_band_15_depth_to_base_surf": b15,
        "training_band_17_cond_surf": b17,
    }
    for name, arr in feature_arrays.items():
        vals=np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat_idx]
        auc=float(roc_auc_score(y, vals))
        sym=max(auc,1-auc)
        canaries[name]={"auc": round(auc,6), "symmetric_auc": round(sym,6), "status": "INVESTIGATE" if sym>0.90 else "REPORT_ONLY_PASS"}
    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc=(ds.read(1)>0) & grid.footprint
    sgmc_truth=sgmc & ~grid.catalogue & ~binary_dilation(grid.catalogue, iterations=3)
    sgmc_scores={arm_name: round(float(metric.dti_binary(mask, sgmc_truth, valid=grid.footprint, known=grid.catalogue)["dti"]),6) for arm_name,mask in arms.items()}
    r0_sgmc=sgmc_scores["R0"]
    report={
        "evidence_label": "PROXY",
        "created_utc": "20261025",
        "axis": "DILATATION",
        "purpose": "Report-only catalogue hide-and-recover instrument, leakage canaries, and USGS SGMC bedrock fault control proxy for DILATATION variants from parent R0.",
        "parent": "h33-h33-2-b2",
        "hide_and_recover_pooled_summary": pooled,
        "per_arm_fold_scores": per_arm_fold_scores,
        "leakage_canaries": {"definition": "symmetric AUC on hidden catalogue positives vs non-catalogue negatives in buffered fold regions", "results": canaries, "stop_and_investigate_if_any_gt_0_90": any(c["status"]=="INVESTIGATE" for c in canaries.values()), "max_symmetric_auc": max(c["symmetric_auc"] for c in canaries.values())},
        "sgmc_control_proxy": {"source": "manifest-pinned USGS SGMC derived fault control (https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d, US Public Domain)", "truth_pixels_after_catalogue_and_3px_exclusion": int(sgmc_truth.sum()), "r0_dti": r0_sgmc, "variant_dti": sgmc_scores, "variant_deltas_vs_r0": {k: round(v-r0_sgmc,6) for k,v in sgmc_scores.items()}},
        "caution": "These are catalogue/SGMC PROXY diagnostics, never live public scores, private-set scores, or decision gates."
    }
    out=ROOT/"evidence"/"dilatation_proxy_audit.json"
    out.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(f"Wrote {out}")
    print(json.dumps(report,indent=2))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
