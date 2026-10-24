#!/usr/bin/env python3
"""REPORT ONLY instruments for STRAINBREAK variants (mirrors report_breakline_proxies).

1. HOLDOUT-DTI (gems57-pooled-hide-v2, seeds 20+30, pooled, paired bootstrap)
   vs R0, RELIEF p10 (holdout best, duplicate) and BREAKLINE f45Ltop (best
   locally-unique) -- the promotion bars, on identical folds.
2. SGMC off-catalogue control PROXY (62,703 px).
3. Fixed-catalogue diagnostic (explicitly NOT a holdout).
4. Leakage canaries: S and components, symmetric AUC (stop > 0.90).
5. Literal uniqueness: pre-placement surface (sampled Spearman + spaced
   top-37,654 surface-set 3px overlap) AND final dots vs every local
   registry raster (shared uniqueness() from report_breakline_proxies).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import verify_all_manifests
from gems.breakline import spaced_top_mask
from gems.strainbreak import strainbreak_surface
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric
from report_breakline_proxies import load_mask, uniqueness


def main() -> int:
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    foot, cat = grid.footprint, grid.catalogue

    arms: dict[str, np.ndarray] = {}
    with rasterio.open(paths["parent_r0_zeros"]) as ds:
        arms["R0"] = (ds.read(1) > 0) & foot
    arms["RELIEFp10"] = load_mask(ROOT / "docs/downloads/h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24-zeros.tif", foot)
    arms["BREAKLINEf45"] = load_mask(ROOT / "docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif", foot)
    receipt = json.loads((ROOT / "evidence" / "strainbreak_variants.json").read_text(encoding="utf-8"))
    own_files = set()
    cand_names = []
    for item in receipt["variants"]:
        arms[item["value"]] = load_mask(ROOT / "releases" / item["fallback_file"], foot)
        cand_names.append(item["value"])
        own_files.update({item["fallback_file"], item["primary_file"]})
    # sibling doses of THIS lane are not registry witnesses against each other
    # for the headline verdict; their mutual overlap is reported separately below.

    folds, split_receipts = [], []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})
    terms_by_arm, per_arm_fold_scores = {}, {}
    for name, mask in arms.items():
        all_terms = None; per_arm_fold_scores[name] = []
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(mask.astype(np.float32), fold, foot)
            per_arm_fold_scores[name].append(float(score["dti"]))
            all_terms = terms if all_terms is None else all_terms + terms
        terms_by_arm[name] = all_terms
    pooled_by_candidate = {c: evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=c)
                           for c in cand_names}
    pooled = pooled_by_candidate[cand_names[0]]

    with rasterio.open(paths["training_features"]) as ds:
        b4 = ds.read(4, masked=True).filled(np.nan).astype(np.float32)
        b8 = ds.read(8, masked=True).filled(np.nan).astype(np.float32)
        b12 = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    v_topo = foot & np.isfinite(b12) & (b12 > -1e30) & np.isfinite(b19) & (b19 > -1e30)
    v_strain = foot & np.isfinite(b4) & (b4 > -1e30)
    surf = strainbreak_surface(b12, b19, b4, v_topo, v_strain)

    rng = np.random.default_rng(520810); y_parts, idx_parts = [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & foot)
        neg = np.flatnonzero(fold["region"] & foot & ~cat)
        n = min(len(neg), max(1, 2 * len(pos)))
        neg = rng.choice(neg, size=n, replace=False) if len(neg) > n else neg
        idx_parts.extend((pos, neg)); y_parts.extend((np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)))
    y = np.concatenate(y_parts); flat = np.concatenate(idx_parts)
    canaries = {}
    for name, arr in {"strainbreak_S_pct": surf["S_pct"], "breakline_L_pct": surf["L_pct"],
                      "strain_pct_band4": surf["strain_pct"], "band4_geod_2ndinv": b4,
                      "band8_geod_dilaterate": b8}.items():
        vals = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat]
        auc = float(roc_auc_score(y, vals)); sym = max(auc, 1 - auc)
        canaries[name] = {"auc": round(auc, 6), "symmetric_auc": round(sym, 6),
                          "status": "INVESTIGATE" if sym > 0.90 else "REPORT_ONLY_PASS"}
    del b4, b8, b12, b19  # free band arrays before the registry passes (4 GB sandbox)

    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_scores = {k: round(float(metric.dti_binary(m, sgmc_truth, valid=foot, known=cat)["dti"]), 6) for k, m in arms.items()}
    catdiag = {k: round(float(metric.dti_binary(m, cat, valid=foot, known=None)["dti"]), 6) for k, m in arms.items()}

    uniq = uniqueness({k: arms[k] for k in ("R0", "RELIEFp10", *cand_names)}, foot, own_files)

    # ---- pre-placement surface check (protocol: surface AND final dots) ----
    d_cat = distance_transform_edt(~cat)
    h19 = load_mask(ROOT / "data/bridge/h19_5.tif", foot)
    d_h19 = distance_transform_edt(~h19)
    bl45_far = arms["BREAKLINEf45"] & (d_h19 > 3.0)
    d_bl45far = distance_transform_edt(~bl45_far)
    far_pool = foot & surf["valid_both"] & (d_cat > 2.0) & (d_h19 > 3.0) & (~arms["R0"]) & (d_bl45far > 3.0)
    surface_set = spaced_top_mask(surf["S_raw"], far_pool, 37654)
    surf_uniq = uniqueness({"R0": arms["R0"], "RELIEFp10": arms["RELIEFp10"], "SURFACE_TOP37654": surface_set},
                            foot, own_files)["SURFACE_TOP37654"]
    # sampled Spearman of continuous surface vs worst registry binaries
    fp_idx = np.flatnonzero(foot)
    sample = np.random.default_rng(20261024).choice(fp_idx, size=300_000, replace=False)
    s_vals = surf["S_pct"].ravel()[sample]
    spear_rows = []
    by_name = {p.name: p for p in [ROOT/"data/parent_R0_zeros.tif",
                                   *sorted((ROOT/"data/bridge").glob("*.tif")),
                                   *sorted((ROOT/"docs/downloads").glob("*.tif")),
                                   *sorted((ROOT/"releases").glob("*.tif"))]}
    for row in surf_uniq["rows"]:
        p = by_name.get(row["registry_file"])
        if p is None:
            spear_rows.append({"registry_file": row["registry_file"], "sampled_spearman_surface": None,
                               "note": "path not re-located for sampled Spearman; binary phi in rows is binding"})
            continue
        m = load_mask(p, foot)
        rho = float(spearmanr(s_vals, m.ravel()[sample].astype(float)).statistic)
        spear_rows.append({"registry_file": row["registry_file"], "sampled_spearman_surface": round(rho, 6)})
        del m
    worst_spear = max((r for r in spear_rows if r["sampled_spearman_surface"] is not None),
                      key=lambda r: abs(r["sampled_spearman_surface"]))

    report = {
        "evidence_label": "PROXY", "created_utc": "20261024", "axis": "STRAINBREAK",
        "parent": "h33-h33-2-b2",
        "hide_and_recover_pooled_summary": pooled,
        "hide_and_recover_pooled_by_candidate": pooled_by_candidate,
        "holdout_splits": split_receipts, "per_arm_fold_scores": per_arm_fold_scores,
        "leakage_canaries": {"definition": "symmetric AUC on hidden catalogue positives vs non-catalogue negatives in buffered fold regions",
                             "results": canaries, "max_symmetric_auc": max(c["symmetric_auc"] for c in canaries.values()),
                             "stop_and_investigate_if_any_gt_0_90": any(c["status"] == "INVESTIGATE" for c in canaries.values())},
        "sgmc_control_proxy": {"source": "manifest-pinned USGS SGMC derived fault control (https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d)",
                               "truth_pixels_after_catalogue_and_3px_exclusion": int(sgmc_truth.sum()),
                               "variant_dti": sgmc_scores,
                               "variant_deltas_vs_r0": {k: round(v - sgmc_scores["R0"], 6) for k, v in sgmc_scores.items()}},
        "fixed_catalogue_diagnostic": {"evidence_class": "PROXY-DIAGNOSTIC (not a holdout; no withholding)",
                                       "variant_dti": catdiag,
                                       "variant_deltas_vs_r0": {k: round(v - catdiag["R0"], 6) for k, v in catdiag.items()}},
        "uniqueness_final_dots": uniq,
        "uniqueness_preplacement_surface": {
            "spaced_top37654_set": {k: surf_uniq[k] for k in ("registry_rasters_checked", "worst_forward_overlap",
                                    "worst_forward_overlap_file", "worst_abs_spearman", "worst_abs_spearman_file", "duplicate")},
            "sampled_spearman_continuous_surface": {"n_sample": 300000, "worst": worst_spear, "rows": spear_rows},
        },
        "caution": "HOLDOUT-DTI / SGMC / fixed-catalogue numbers are local instruments, never live scores or organizer receipts.",
    }
    out = ROOT / "evidence" / "strainbreak_proxy_audit.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print(json.dumps({
        "holdout_scores": {k: v["dti"] for k, v in pooled["scores"].items()},
        "paired": {c: {k: (v["delta"], v["ci95"]) for k, v in pooled_by_candidate[c]["paired_differences"].items()} for c in cand_names},
        "canary_max": report["leakage_canaries"]["max_symmetric_auc"],
        "sgmc": sgmc_scores, "catdiag": catdiag,
        "uniq_dots": {k: {"worst_fwd": v["worst_forward_overlap"], "file": v["worst_forward_overlap_file"],
                          "worst_rho": v["worst_abs_spearman"], "dup": v["duplicate"], "n": v["registry_rasters_checked"]}
                      for k, v in uniq.items()},
        "uniq_surface": report["uniqueness_preplacement_surface"],
    }, indent=2)[:6000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
