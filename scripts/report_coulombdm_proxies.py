#!/usr/bin/env python3
"""Evaluate the 3 pre-registered COULOMBDM experiments across all local instruments.

1. Static-raster pooled HOLDOUT-DTI (gems57-pooled-hide-v2, seeds 20+30, 22,663 withheld
   positives, 363 spatial clusters, 1,000 paired cluster-bootstrap draws) vs R0,
   HYDROCONDUITf45hydro, APRONRIDGEfree1d, APRONRIDGEs60f40, PIEDFRONTf35Ptop,
   STEPEDGEf60Sraw, RELIEFp10, STRAINBREAKf60, ANASIGf45, SPRINGALIGNf33, and BREAKLINEf45.
2. Protocol Rule 2 fold-by-fold d_visible > 2.0 HOLDOUT-DTI (measuring true blind-fault
   recovery when the 2-px exclusion is computed strictly from fold['visible'],
   with paired cluster-bootstrap CI via evaluate_holdout.pooled_summary).
3. Off-catalogue USGS SGMC fault proxy DTI (62,703 truth pixels >3 px from catalogue).
4. Final-dot local registry uniqueness (3-px forward overlap and |Spearman rho|).
"""
from __future__ import annotations

import gc
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import verify_all_manifests  # noqa: E402
from gems.coulombdm import (  # noqa: E402
    coulombdm_surface,
    gdr_blind_thermal_plume,
    spaced_top_mask,
)
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric as gems57_metric  # noqa: E402
from report_breakline_proxies import load_mask, uniqueness  # noqa: E402

VARIANTS_JSON = ROOT / "evidence" / "coulombdm_variants.json"
SCREEN_JSON = ROOT / "evidence" / "coulombdm_preplacement_screen.json"
OUT_JSON = ROOT / "evidence" / "coulombdm_proxy_audit.json"


def evaluate_fold_visible_holdout(
    foot: np.ndarray,
    folds: list[dict],
    h19: np.ndarray,
    d_h19: np.ndarray,
    valid: np.ndarray,
    crest_1d: np.ndarray,
    s_raw: np.ndarray,
    hab_pct: np.ndarray,
) -> dict:
    """True Protocol Rule 2 fold-by-fold evaluation using strictly fold['visible']."""
    n_tot = 37654
    scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)

    yy2, xx2 = np.ogrid[-2:3, -2:3]
    disk_r2 = (yy2 * yy2 + xx2 * xx2) <= 4
    yy3, xx3 = np.ogrid[-3:4, -3:4]
    disk_r3 = (yy3 * yy3 + xx3 * xx3) <= 9
    far_h19_ok = ~binary_dilation(h19, structure=disk_r3)

    terms_vis: dict[str, list] = {
        "H19_skeleton_dvis2": [],
        "COULOMBDM_coulomb1d_dvis2": [],
        "COULOMBDM_s35coulomb65_dvis2": [],
        "COULOMBDM_s45coulomb55_dvis2": [],
    }
    for idx, fold in enumerate(folds, 1):
        vis = fold["visible"]
        vis_ok = foot & valid & (~binary_dilation(vis, structure=disk_r2))

        pool_h19_vis = vis_ok & h19
        pred_skel = spaced_top_mask(scan_rank, pool_h19_vis, n_tot, min_dist_px=2.4, cand_cap=200_000).astype(np.float32)
        pred_skel[vis] = 0.0
        _, t = evaluate_holdout.evaluate(pred_skel, fold, foot)
        terms_vis["H19_skeleton_dvis2"].extend(t)
        del pred_skel

        pool_free_vis = vis_ok & crest_1d
        pred_c1d = spaced_top_mask(s_raw, pool_free_vis, n_tot, min_dist_px=2.8, cand_cap=300_000).astype(np.float32)
        pred_c1d[vis] = 0.0
        _, t = evaluate_holdout.evaluate(pred_c1d, fold, foot)
        terms_vis["COULOMBDM_coulomb1d_dvis2"].extend(t)
        del pred_c1d, pool_free_vis

        skel_35 = spaced_top_mask(hab_pct, pool_h19_vis, 13179, min_dist_px=2.5, cand_cap=200_000)
        pool_far_vis = vis_ok & crest_1d & far_h19_ok & (~skel_35)
        far_65 = spaced_top_mask(s_raw, pool_far_vis, 24475, min_dist_px=2.8, cand_cap=250_000)
        pred_s35 = (skel_35 | far_65).astype(np.float32)
        pred_s35[vis] = 0.0
        _, t = evaluate_holdout.evaluate(pred_s35, fold, foot)
        terms_vis["COULOMBDM_s35coulomb65_dvis2"].extend(t)
        del skel_35, pool_far_vis, far_65, pred_s35

        skel_45 = spaced_top_mask(hab_pct, pool_h19_vis, 16944, min_dist_px=2.5, cand_cap=200_000)
        pool_far45_vis = vis_ok & crest_1d & far_h19_ok & (~skel_45)
        far_55 = spaced_top_mask(s_raw, pool_far45_vis, 20710, min_dist_px=2.8, cand_cap=250_000)
        pred_s45 = (skel_45 | far_55).astype(np.float32)
        pred_s45[vis] = 0.0
        _, t = evaluate_holdout.evaluate(pred_s45, fold, foot)
        terms_vis["COULOMBDM_s45coulomb55_dvis2"].extend(t)
        del skel_45, pool_far45_vis, far_55, pred_s45, pool_h19_vis, vis_ok
        gc.collect()
        print(f"  [fold-visible] completed fold {idx}/{len(folds)}", flush=True)

    summary_c1d = evaluate_holdout.pooled_summary(
        terms_vis, draws=1000, seed=520810, candidate="COULOMBDM_coulomb1d_dvis2"
    )
    summary_s45 = evaluate_holdout.pooled_summary(
        terms_vis, draws=1000, seed=520810, candidate="COULOMBDM_s45coulomb55_dvis2"
    )
    return {
        "evidence_class": "HOLDOUT-DTI (true fold-by-fold d_visible > 2.0; zero full-catalogue self-masking)",
        "evaluator_version": evaluate_holdout.VERSION,
        "pooled_summary_coulomb1d": summary_c1d,
        "pooled_summary_s45coulomb55": summary_s45,
        "note": (
            "Demonstrates blind-fault recovery when d > 2.0 px is computed strictly from "
            "fold['visible'] rather than static full existing_faults.tif, so withheld fault "
            "segments are not artificially zeroed within 200 m of themselves."
        ),
    }


def main() -> int:
    print("[0/4] Loading manifests & computing slim COULOMBDM surface...", flush=True)
    paths = verify_all_manifests()
    vdoc = json.loads(VARIANTS_JSON.read_text(encoding="utf-8"))
    sdoc = json.loads(SCREEN_JSON.read_text(encoding="utf-8"))
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    foot, cat = grid.footprint, grid.catalogue

    with rasterio.open(paths["training_features"]) as ds:
        b2_rtp = ds.read(2, masked=True).filled(np.nan).astype(np.float32)
        b4_s2i = ds.read(4, masked=True).filled(np.nan).astype(np.float32)
        b5_gsl = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b7_shr = ds.read(7, masked=True).filled(np.nan).astype(np.float32)
        b8_dil = ds.read(8, masked=True).filled(np.nan).astype(np.float32)
        b11_gvg = ds.read(11, masked=True).filled(np.nan).astype(np.float32)
        b12_el = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b15_db = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b17_cd = ds.read(17, masked=True).filled(np.nan).astype(np.float32)
        b19_sl = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    with rasterio.open(paths["ext_geodawn_rad_u8"]) as ds:
        rad_k = ds.read(1)
        rad_th = ds.read(2)
        rad_u = ds.read(3)
    valid_base = foot & np.isfinite(b12_el) & (b12_el > -1e30)
    gdr_info = gdr_blind_thermal_plume(
        paths["gdr_wellspring_in_footprint"], foot.shape, valid_base, sigma_px=15.0
    )
    surf = coulombdm_surface(
        det_elev=b12_el,
        det_elev_slope=b19_sl,
        depth_to_base=b15_db,
        grav_slope=b5_gsl,
        grav_vg=b11_gvg,
        geod_2ndinv=b4_s2i,
        geod_shearrate=b7_shr,
        geod_dilaterate=b8_dil,
        rtp=b2_rtp,
        cond_surf=b17_cd,
        rad_k=rad_k,
        rad_th=rad_th,
        rad_u=rad_u,
        gdr_plume_pct=gdr_info["plume_pct"],  # type: ignore[arg-type]
        footprint=foot,
    )
    valid = np.asarray(surf["valid"], bool).copy()
    crest_1d = np.asarray(surf["crest_1d"], bool).copy()
    s_raw = np.asarray(surf["S_raw"], dtype=np.float32).copy()
    hab_pct = np.asarray(surf["hab_coulomb_pct"], dtype=np.float32).copy()
    del surf, gdr_info, valid_base
    del b2_rtp, b4_s2i, b5_gsl, b7_shr, b8_dil, b11_gvg, b12_el, b15_db, b17_cd, b19_sl, rad_k, rad_th, rad_u
    gc.collect()
    print("[1/4] Building holdout folds & scoring static HOLDOUT-DTI...", flush=True)

    folds, split_receipts = [], []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})
    del grid
    gc.collect()

    arms: dict[str, np.ndarray] = {
        "R0": load_mask(paths["parent_r0_zeros"], foot),
        "HYDROCONDUITf45hydro": load_mask(
            ROOT / "docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif", foot
        ),
        "APRONRIDGEfree1d": load_mask(
            ROOT / "docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif", foot
        ),
        "APRONRIDGEs60f40": load_mask(
            ROOT / "docs/downloads/h33-h33-2-b2-APRONRIDGEs60f40-20261024-6e7e0174-zeros.tif", foot
        ),
        "PIEDFRONTf35Ptop": load_mask(
            ROOT / "docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif", foot
        ),
        "STEPEDGEf60Sraw": load_mask(
            ROOT / "docs/downloads/h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif", foot
        ),
        "RELIEFp10": load_mask(
            ROOT / "docs/downloads/h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24-zeros.tif", foot
        ),
        "STRAINBREAKf60": load_mask(
            ROOT / "docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif", foot
        ),
        "ANASIGf45": load_mask(
            ROOT / "docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif", foot
        ),
        "SPRINGALIGNf33": load_mask(
            ROOT / "docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif", foot
        ),
        "BREAKLINEf45": load_mask(
            ROOT / "docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif", foot
        ),
    }
    own_files: set[str] = set()
    cand_names: list[str] = []
    for v in vdoc["variants"]:
        val = v["value"]
        zp = ROOT / v["file_zeros"]
        np_path = ROOT / v["file_nan_cache"]
        arms[val] = load_mask(zp, foot)
        cand_names.append(val)
        own_files.update({zp.name, np_path.name})

    terms_by_arm, per_arm_fold_scores = {}, {}
    for name, mask in arms.items():
        all_terms = []
        per_arm_fold_scores[name] = []
        arr_f = mask.astype(np.float32)
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(arr_f, fold, foot)
            per_arm_fold_scores[name].append(float(score["dti"]))
            all_terms.extend(terms)
        terms_by_arm[name] = all_terms
        del arr_f

    pooled_by_cand = {
        c: evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=c)
        for c in cand_names
    }
    del terms_by_arm
    gc.collect()

    print("[2/4] Scoring Rule-2 fold-visible d_vis > 2.0 HOLDOUT-DTI...", flush=True)
    h19 = load_mask(ROOT / "data/bridge/h19_5.tif", foot)
    fold_vis_eval = evaluate_fold_visible_holdout(
        foot, folds, h19, h19, valid, crest_1d, s_raw, hab_pct
    )
    del folds, h19, valid, crest_1d, s_raw, hab_pct
    gc.collect()

    print("[3/4] Scoring USGS SGMC off-catalogue proxy DTI...", flush=True)
    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & (~cat) & (~binary_dilation(cat, iterations=3))
    sgmc_scores = {
        k: round(float(gems57_metric.dti_binary(m, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
        for k, m in arms.items()
    }
    cat_diag = {
        k: round(float(gems57_metric.dti_binary(m, cat, valid=foot, known=None)["dti"]), 6)
        for k, m in arms.items()
    }
    n_sgmc_truth = int(sgmc_truth.sum())
    del sgmc, sgmc_truth
    gc.collect()

    print("[4/4] Auditing local registry uniqueness...", flush=True)
    uniq_final = uniqueness({k: arms[k] for k in cand_names}, foot, own_files)
    sibling_overlap = {}
    for a in cand_names:
        for b in cand_names:
            if a >= b:
                continue
            da = distance_transform_edt(~arms[b])
            db = distance_transform_edt(~arms[a])
            sibling_overlap[f"{a}_vs_{b}"] = {
                "a_within_3px_of_b": round(float((da[arms[a]] <= 3.0).mean()), 6),
                "b_within_3px_of_a": round(float((db[arms[b]] <= 3.0).mean()), 6),
            }
            del da, db

    out_doc = {
        "schema": "gemsdoe92-coulombdm-proxy-audit.v1",
        "lane": "COULOMBDM",
        "evaluator_version": evaluate_holdout.VERSION,
        "split_receipts": split_receipts,
        "leakage_canaries": sdoc["leakage_canaries"],
        "uniqueness_preplacement_surface": sdoc["preplacement_surface_uniqueness"],
        "hide_and_recover_pooled_by_candidate": pooled_by_cand,
        "hide_and_recover_per_fold_dti": per_arm_fold_scores,
        "hide_and_recover_fold_visible_rule2_diagnostic": fold_vis_eval,
        "sgmc_control_proxy": {
            "evidence_class": "PROXY (off-catalogue USGS SGMC bedrock faults)",
            "truth_pixels_after_catalogue_and_3px_exclusion": n_sgmc_truth,
            "variant_dti": sgmc_scores,
        },
        "catalogue_diagnostic_NOT_A_HOLDOUT": {
            "evidence_class": "DIAGNOSTIC (full catalogue, affected by d_cat>2 exclusion)",
            "variant_dti": cat_diag,
        },
        "uniqueness_final_dots": {
            k: {
                **{
                    fk: uniq_final[k][fk]
                    for fk in (
                        "registry_rasters_checked",
                        "worst_forward_overlap",
                        "worst_forward_overlap_file",
                        "worst_abs_spearman",
                        "worst_abs_spearman_file",
                        "duplicate",
                    )
                },
                "top5_by_overlap": sorted(
                    uniq_final[k]["rows"],
                    key=lambda r: -r["forward_overlap_my_dots_within_3px"],
                )[:5],
            }
            for k in cand_names
        },
        "sibling_mutual_overlap": sibling_overlap,
    }
    OUT_JSON.write_text(json.dumps(out_doc, indent=2) + "\n", encoding="utf-8")

    summary = {
        "static_holdout_dti": {
            k: {
                "dti": pooled_by_cand[k]["scores"][k]["dti"],
                "ci95": pooled_by_cand[k]["scores"][k]["ci95"],
                "delta_vs_R0": pooled_by_cand[k]["paired_differences"]["R0"]["delta"],
                "delta_vs_R0_ci95": pooled_by_cand[k]["paired_differences"]["R0"]["ci95"],
                "delta_vs_HYDROCONDUITf45hydro": pooled_by_cand[k]["paired_differences"]["HYDROCONDUITf45hydro"]["delta"],
                "delta_vs_HYDROCONDUITf45hydro_ci95": pooled_by_cand[k]["paired_differences"]["HYDROCONDUITf45hydro"]["ci95"],
                "delta_vs_APRONRIDGEfree1d": pooled_by_cand[k]["paired_differences"]["APRONRIDGEfree1d"]["delta"],
                "delta_vs_APRONRIDGEfree1d_ci95": pooled_by_cand[k]["paired_differences"]["APRONRIDGEfree1d"]["ci95"],
                "delta_vs_RELIEFp10": pooled_by_cand[k]["paired_differences"]["RELIEFp10"]["delta"],
                "delta_vs_RELIEFp10_ci95": pooled_by_cand[k]["paired_differences"]["RELIEFp10"]["ci95"],
            }
            for k in cand_names
        },
        "reference_static_holdout_dti": {
            k: pooled_by_cand["coulomb1d"]["scores"][k]["dti"]
            for k in (
                "R0",
                "HYDROCONDUITf45hydro",
                "APRONRIDGEfree1d",
                "APRONRIDGEs60f40",
                "PIEDFRONTf35Ptop",
                "STEPEDGEf60Sraw",
                "RELIEFp10",
                "STRAINBREAKf60",
                "ANASIGf45",
                "SPRINGALIGNf33",
                "BREAKLINEf45",
            )
        },
        "fold_visible_rule2_scores": fold_vis_eval["pooled_summary_coulomb1d"]["scores"],
        "fold_visible_rule2_delta_coulomb1d": fold_vis_eval["pooled_summary_coulomb1d"]["paired_differences"],
        "sgmc_proxy": sgmc_scores,
        "local_uniqueness": {
            k: {
                "worst_overlap": uniq_final[k]["worst_forward_overlap"],
                "worst_file": uniq_final[k]["worst_forward_overlap_file"],
                "worst_rho": uniq_final[k]["worst_abs_spearman"],
                "duplicate": uniq_final[k]["duplicate"],
            }
            for k in cand_names
        },
    }
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
