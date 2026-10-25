#!/usr/bin/env python3
"""REPORT ONLY instruments for COULOMB variants (mirrors report_hydroconduit_proxies).

1. HOLDOUT-DTI (gems57-pooled-hide-v2, seeds 20+30, pooled, paired bootstrap)
   vs R0, RELIEF p10, BREAKLINE f45, APRONRIDGE free1d and HYDROCONDUIT f45hydro
   (the 0.008549 promotion bar) -- all scored on identical folds.
2. SGMC off-catalogue control PROXY (62,703 px).
3. Fixed-catalogue diagnostic (explicitly NOT a holdout).
4. Leakage canaries: S and components + raw bands, symmetric AUC (stop > 0.90).
5. Literal uniqueness: final dots vs every local registry raster (shared
   uniqueness() from report_breakline_proxies); pre-placement surface
   uniqueness lives in evidence/coulomb_preplacement_screen.json.
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

from build_snap_scarp_variants import verify_all_manifests
from gems.coulomb import coulomb_surface
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric
from report_breakline_proxies import load_mask, uniqueness

OUT_JSON = ROOT / "evidence/coulomb_proxy_audit.json"


def main() -> int:
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    foot, cat = grid.footprint, grid.catalogue

    arms: dict[str, np.ndarray] = {}
    with rasterio.open(paths["parent_r0_zeros"]) as ds:
        arms["R0"] = (ds.read(1) > 0) & foot
    arms["RELIEFp10"] = load_mask(
        ROOT / "docs/downloads/h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24-zeros.tif", foot)
    arms["BREAKLINEf45"] = load_mask(
        ROOT / "docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif", foot)
    arms["APRONRIDGEfree1d"] = load_mask(
        ROOT / "docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif", foot)
    arms["HYDROCONDUITf45hydro"] = load_mask(
        ROOT / "docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif", foot)
    receipt = json.loads((ROOT / "evidence/coulomb_variants.json").read_text(encoding="utf-8"))
    own_files = set()
    cand_names = []
    for item in receipt["variants"]:
        arms[item["value"]] = load_mask(ROOT / item["file_zeros"], foot)
        cand_names.append(item["value"])
        own_files.add(Path(item["file_zeros"]).name)

    print("Holdout folds ...", flush=True)
    folds = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
    n_withheld = int(sum(f["truth"].sum() for f in folds))
    terms_by_arm = {}
    per_arm_fold_scores = {}
    for name, mask in arms.items():
        all_terms = None
        per_arm_fold_scores[name] = []
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(mask.astype(np.float32), fold, foot)
            per_arm_fold_scores[name].append(float(score["dti"]))
            all_terms = terms if all_terms is None else all_terms + terms
        terms_by_arm[name] = all_terms
        print(f"  {name}: pooled terms done", flush=True)
    pooled_by_candidate = {c: evaluate_holdout.pooled_summary(
        terms_by_arm, draws=1000, seed=520810, candidate=c) for c in cand_names}

    print("Canary surfaces ...", flush=True)
    with rasterio.open(paths["training_features"]) as ds:
        b2 = ds.read(2, masked=True).filled(np.nan).astype(np.float32)
        b3 = ds.read(3, masked=True).filled(np.nan).astype(np.float32)
        b4 = ds.read(4, masked=True).filled(np.nan).astype(np.float32)
        b5 = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b7 = ds.read(7, masked=True).filled(np.nan).astype(np.float32)
        b8 = ds.read(8, masked=True).filled(np.nan).astype(np.float32)
        b9 = ds.read(9, masked=True).filled(np.nan).astype(np.float32)
        b10 = ds.read(10, masked=True).filled(np.nan).astype(np.float32)
        b12 = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b15 = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b16 = ds.read(16, masked=True).filled(np.nan).astype(np.float32)
        b17 = ds.read(17, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    surf = coulomb_surface(
        det_elev=b12, det_elev_slope=b19, depth_to_base=b15, grav_slope=b5,
        rtp=b2, dilaterate=b8, shearrate=b7, second_inv=b4,
        deq=b10, ieq=b16, footprint=foot)

    rng = np.random.default_rng(520810)
    y_parts, idx_parts = [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & foot)
        neg = np.flatnonzero(fold["region"] & foot & ~cat)
        n = min(len(neg), max(1, 2 * len(pos)))
        neg = rng.choice(neg, size=n, replace=False) if len(neg) > n else neg
        idx_parts.extend((pos, neg))
        y_parts.extend((np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)))
    y = np.concatenate(y_parts)
    flat = np.concatenate(idx_parts)
    canaries = {}
    fields = {"coulomb_S_free_pct": surf["S_free_pct"],
              "coulomb_S_open_pct": surf["S_open_pct"],
              "coulomb_S_seismo_pct": surf["S_seismo_pct"],
              "coulomb_O_pct": surf["O_pct"],
              "coulomb_H_apron": surf["H_apron"],
              "coulomb_R_rtp_tilt": surf["R_rtp_tilt"],
              "coulomb_R_scarp_rel": surf["R_scarp_rel"],
              "coulomb_seismo_pct": surf["seismo_pct"],
              "band2_rtp": b2, "band4_2ndinv": b4, "band5_grav_slope": b5,
              "band7_shearrate": b7, "band8_dilaterate": b8,
              "band10_deq": b10, "band12_det_elev": b12,
              "band15_depth_base": b15, "band16_ieq": b16,
              "band19_slope": b19, "band3_tmi_hg": b3,
              "band9_tmi_vg": b9, "band17_cond": b17}
    for name, arr in fields.items():
        vals = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat]
        auc = float(roc_auc_score(y, vals))
        sym = max(auc, 1 - auc)
        canaries[name] = {"auc": round(auc, 6), "symmetric_auc": round(sym, 6),
                          "status": "INVESTIGATE" if sym > 0.90 else "REPORT_ONLY_PASS"}
    max_sym = max(v["symmetric_auc"] for v in canaries.values())
    print(f"canaries: max symmetric AUC = {max_sym}", flush=True)
    del b2, b3, b4, b5, b7, b8, b9, b10, b12, b15, b16, b17, b19, surf

    print("SGMC + fixed-catalogue diagnostics ...", flush=True)
    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_out, fixed_out = {}, {}
    for name, mask in arms.items():
        sgmc_out[name] = round(float(metric.dti_binary(
            mask, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
        fixed_out[name] = round(float(metric.dti_binary(
            mask, cat, valid=foot, known=None)["dti"]), 6)

    print("Local uniqueness (final dots) ...", flush=True)
    uni = uniqueness(arms, foot, own_files)

    doc = {
        "schema": "gemsdoe92.coulomb-proxy-audit.v1",
        "evaluator": "gems57-pooled-hide-v2",
        "withheld_positives": n_withheld,
        "folds": len(folds),
        "arms": sorted(arms),
        "candidates": cand_names,
        "hide_and_recover_pooled_by_candidate": pooled_by_candidate,
        "per_arm_fold_scores": {k: [round(x, 6) for x in v]
                                for k, v in per_arm_fold_scores.items()},
        "sgmc_proxy_dti": sgmc_out,
        "sgmc_truth_px": int(sgmc_truth.sum()),
        "fixed_catalogue_diagnostic_NOT_A_HOLDOUT": fixed_out,
        "leakage_canaries": canaries,
        "leakage_canary_max_symmetric_auc": max_sym,
        "uniqueness_final_dots": uni,
        "preplacement_surface_uniqueness": "evidence/coulomb_preplacement_screen.json",
    }
    OUT_JSON.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON}", flush=True)
    for c in cand_names:
        s = pooled_by_candidate[c]["scores"][c]
        print(f"{c}: HOLDOUT-DTI {s['dti']} CI95 {s['ci95']} | "
              f"SGMC {sgmc_out[c]} | worst_fwd "
              f"{uni[c]['worst_forward_overlap']} ({uni[c]['worst_forward_overlap_file']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
