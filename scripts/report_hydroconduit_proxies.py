#!/usr/bin/env python3
"""Evaluate the 3 pre-registered HYDROCONDUIT experiments across all local instruments.

1. Static-raster pooled HOLDOUT-DTI (gems57-pooled-hide-v2, seeds 20+30, 22,663 withheld
   positives, 157 spatial clusters, 1,000 paired cluster-bootstrap draws) vs R0, RELIEFp10,
   STRAINBREAKf60, ANASIGf45, SPRINGALIGNf33, and BREAKLINEf45.
2. Protocol Rule 2 fold-by-fold d_visible > 2.0 HOLDOUT-DTI (measuring true blind-fault
   recovery when the 2-px exclusion is computed strictly from fold['visible_catalogue'],
   with paired cluster-bootstrap CI via evaluate_holdout.pooled_summary).
3. Off-catalogue USGS SGMC fault proxy DTI (62,703 truth pixels >3 px from catalogue).
4. Final-dot local registry uniqueness (3-px forward overlap and |Spearman rho|).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import verify_all_manifests  # noqa: E402
from gems.hydroconduit import (  # noqa: E402
    gdr_blind_thermal_plume,
    hydroconduit_surface,
    spaced_top_mask,
)
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric as gems57_metric  # noqa: E402
from report_breakline_proxies import load_mask, uniqueness  # noqa: E402

VARIANTS_JSON = ROOT / "evidence" / "hydroconduit_variants.json"
SCREEN_JSON = ROOT / "evidence" / "hydroconduit_preplacement_screen.json"
OUT_JSON = ROOT / "evidence" / "hydroconduit_proxy_audit.json"


def evaluate_fold_visible_holdout(
    foot: np.ndarray,
    folds: list[dict],
    h19: np.ndarray,
    d_h19: np.ndarray,
    surf: dict[str, np.ndarray],
) -> dict:
    """True Protocol Rule 2 fold-by-fold evaluation using strictly fold['visible_catalogue']."""
    n_tot = 37654
    n_far = int(round(0.45 * n_tot))
    n_skel = n_tot - n_far
    scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)

    terms_vis: dict[str, list] = {"H19_skeleton_dvis2": [], "HYDROCONDUIT_f45hydro_dvis2": []}
    built_cache: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for fold in folds:
        vis = fold["visible"]
        vid = id(vis)
        if vid not in built_cache:
            d_vis = distance_transform_edt(~vis)
            pool_h19_vis = foot & surf["valid"] & h19 & (d_vis > 2.0)
            pred_skel = spaced_top_mask(scan_rank, pool_h19_vis, n_tot, min_dist_px=2.4).astype(np.float32)
            pred_skel[vis] = 0.0

            skel_vis = spaced_top_mask(surf["hab_hydro_pct"], pool_h19_vis, n_skel, min_dist_px=2.5)
            pool_far_vis = foot & surf["valid"] & (d_vis > 2.0) & (d_h19 > 3.0) & (~skel_vis)
            far_vis = spaced_top_mask(surf["S_hydro_raw"], pool_far_vis, n_far, min_dist_px=2.8)
            pred_hydro = (skel_vis | far_vis).astype(np.float32)
            pred_hydro[vis] = 0.0
            built_cache[vid] = (pred_skel, pred_hydro)
        else:
            pred_skel, pred_hydro = built_cache[vid]

        _, t_s = evaluate_holdout.evaluate(pred_skel, fold, foot)
        terms_vis["H19_skeleton_dvis2"].extend(t_s)
        _, t_h = evaluate_holdout.evaluate(pred_hydro, fold, foot)
        terms_vis["HYDROCONDUIT_f45hydro_dvis2"].extend(t_h)

    summary = evaluate_holdout.pooled_summary(
        terms_vis, draws=1000, seed=520810, candidate="HYDROCONDUIT_f45hydro_dvis2"
    )
    return {
        "evidence_class": "HOLDOUT-DTI (true fold-by-fold d_visible > 2.0; zero full-catalogue self-masking)",
        "evaluator_version": evaluate_holdout.VERSION,
        "pooled_summary": summary,
        "note": (
            "Demonstrates the structural self-masking discovery: when d > 2.0 px is computed "
            "from visible_catalogue per fold rather than static full existing_faults.tif, "
            "withheld fault segments are not artificially zeroed within 200 m of themselves."
        ),
    }


def main() -> int:
    paths = verify_all_manifests()
    vdoc = json.loads(VARIANTS_JSON.read_text(encoding="utf-8"))
    sdoc = json.loads(SCREEN_JSON.read_text(encoding="utf-8"))
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    foot, cat = grid.footprint, grid.catalogue

    arms: dict[str, np.ndarray] = {
        "R0": load_mask(paths["parent_r0_zeros"], foot),
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
        np_path = ROOT / v["file_nan"]
        arms[val] = load_mask(zp, foot)
        cand_names.append(val)
        own_files.update({zp.name, np_path.name})

    # 1. Static-raster pooled HOLDOUT-DTI via shared vendor/gems57/evaluate_holdout.py
    folds, split_receipts = [], []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})

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

    pooled_by_cand = {
        c: evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=c)
        for c in cand_names
    }

    # 2. True fold-by-fold d_visible > 2.0 HOLDOUT-DTI
    with rasterio.open(paths["training_features"]) as ds:
        b2_rtp = ds.read(2, masked=True).filled(np.nan).astype(np.float32)
        b4_s2i = ds.read(4, masked=True).filled(np.nan).astype(np.float32)
        b8_dil = ds.read(8, masked=True).filled(np.nan).astype(np.float32)
        b12_el = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b15_db = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b17_cd = ds.read(17, masked=True).filled(np.nan).astype(np.float32)
        b19_sl = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    with rasterio.open(paths["ext_geodawn_rad_u8"]) as ds:
        rad_k = ds.read(1)
        rad_th = ds.read(2)
    valid_base = foot & np.isfinite(b12_el) & (b12_el > -1e30)
    gdr_info = gdr_blind_thermal_plume(
        paths["gdr_wellspring_in_footprint"], foot.shape, valid_base, sigma_px=15.0
    )
    surf = hydroconduit_surface(
        det_elev=b12_el, det_elev_slope=b19_sl, depth_to_base=b15_db,
        geod_2ndinv=b4_s2i, geod_dilaterate=b8_dil, rtp=b2_rtp, cond_surf=b17_cd,
        rad_k=rad_k, rad_th=rad_th, gdr_plume_pct=gdr_info["plume_pct"],  # type: ignore[arg-type]
        footprint=foot,
    )
    del b2_rtp, b4_s2i, b8_dil, b12_el, b15_db, b17_cd, b19_sl, rad_k, rad_th

    h19 = load_mask(ROOT / "data/bridge/h19_5.tif", foot)
    d_h19 = distance_transform_edt(~h19)
    fold_vis_eval = evaluate_fold_visible_holdout(foot, folds, h19, d_h19, surf)

    # 3. Off-catalogue USGS SGMC control proxy DTI (62,703 pixels >3 px from catalogue)
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

    # 4. Final-dot local registry uniqueness (excluding own session siblings)
    uniq_final = uniqueness({k: arms[k] for k in cand_names}, foot, own_files)
    # Also compute mutual overlap among the 3 sibling builds for transparency
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

    out_doc = {
        "schema": "gemsdoe92-hydroconduit-proxy-audit.v1",
        "lane": "HYDROCONDUIT",
        "evaluator_version": evaluate_holdout.VERSION,
        "split_receipts": split_receipts,
        "leakage_canaries": sdoc["leakage_canaries"],
        "uniqueness_preplacement_surface": sdoc["preplacement_surface_uniqueness"],
        "hide_and_recover_pooled_by_candidate": pooled_by_cand,
        "hide_and_recover_per_fold_dti": per_arm_fold_scores,
        "hide_and_recover_fold_visible_rule2_diagnostic": fold_vis_eval,
        "sgmc_control_proxy": {
            "evidence_class": "PROXY (off-catalogue USGS SGMC bedrock faults)",
            "truth_pixels_after_catalogue_and_3px_exclusion": int(sgmc_truth.sum()),
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
                "delta_vs_RELIEFp10": pooled_by_cand[k]["paired_differences"]["RELIEFp10"]["delta"],
                "delta_vs_RELIEFp10_ci95": pooled_by_cand[k]["paired_differences"]["RELIEFp10"]["ci95"],
                "delta_vs_STRAINBREAKf60": pooled_by_cand[k]["paired_differences"]["STRAINBREAKf60"]["delta"],
                "delta_vs_STRAINBREAKf60_ci95": pooled_by_cand[k]["paired_differences"]["STRAINBREAKf60"]["ci95"],
            }
            for k in cand_names
        },
        "reference_static_holdout_dti": {
            k: pooled_by_cand["f45hydro"]["scores"][k]["dti"]
            for k in ("R0", "RELIEFp10", "STRAINBREAKf60", "ANASIGf45", "SPRINGALIGNf33", "BREAKLINEf45")
        },
        "fold_visible_rule2_scores": fold_vis_eval["pooled_summary"]["scores"],
        "fold_visible_rule2_delta": fold_vis_eval["pooled_summary"]["paired_differences"],
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
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
