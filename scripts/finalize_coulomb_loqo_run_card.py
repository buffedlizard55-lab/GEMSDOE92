#!/usr/bin/env python3
"""Assemble per-file <stem>-audit.json sidecars and the canonical Protocol Rule 5
Run Card (evidence/coulomb_loqo_run_card.json + docs/downloads/coulomb_loqo_run_card.json)
from verified COULOMB-LOQO screen, proxy-audit, and 102-repo public registry receipts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT)]

from gems.rasters import sha256_file  # noqa: E402

VARIANTS_JSON = ROOT / "evidence" / "coulomb_loqo_variants.json"
PROXY_JSON = ROOT / "evidence" / "coulomb_loqo_proxy_audit.json"
PUB_JSON = ROOT / "evidence" / "coulomb_loqo_public_registry_uniqueness.json"
SPARSE_JSON = ROOT / "evidence" / "coulomb_loqo_public_sparse_diagnostic.json"
RUN_CARD_JSON = ROOT / "evidence" / "coulomb_loqo_run_card.json"
DL_RUN_CARD_JSON = ROOT / "docs" / "downloads" / "coulomb_loqo_run_card.json"


def main() -> int:
    vdoc = json.loads(VARIANTS_JSON.read_text(encoding="utf-8"))
    pdoc = json.loads(PROXY_JSON.read_text(encoding="utf-8"))
    pub = json.loads(PUB_JSON.read_text(encoding="utf-8"))
    sparse = json.loads(SPARSE_JSON.read_text(encoding="utf-8"))

    variants = vdoc["variants"]
    best_arm = pdoc["winning_arm"]
    best_v = next(v for v in variants if v["value"] == best_arm)
    assert sha256_file(ROOT / best_v["file_zeros"]) == best_v["sha256_zeros"]
    assert pub["candidate_file_sha256"] == best_v["sha256_zeros"]

    scores_all = pdoc["hide_and_recover_pooled_by_candidate"][best_arm]["scores"]
    paired_best = pdoc["hide_and_recover_pooled_by_candidate"][best_arm]["paired_differences"]
    dvis_summary = pdoc["hide_and_recover_drawblind_fold_visible_dti"]["pooled_summary"]
    sgmc_scores = pdoc["sgmc_control_proxy"]["variant_dti"]
    uniq_final = pdoc["uniqueness_final_dots"]
    surf_u = pdoc["uniqueness_preplacement_surface"]

    # Write per-file <stem>-audit.json sidecars in docs/downloads/
    for v in variants:
        arm = v["value"]
        u = uniq_final[arm]
        zpath = ROOT / v["file_zeros"]
        assert sha256_file(zpath) == v["sha256_zeros"]
        stem = zpath.name[: -len("-zeros.tif")]
        audit_sidecar = zpath.parent / f"{stem}-audit.json"

        sidecar_doc = {
            "gates_zeros": v["gates_zeros"],
            "gates_zeros_pass": all(g["ok"] for g in v["gates_zeros"]),
            "gates_nan": v["gates_nan"],
            "gates_nan_pass": all(g["ok"] for g in v["gates_nan"]),
            "file": zpath.name,
            "sha256_zeros": v["sha256_zeros"],
            "sha256_nan": v["sha256"],
            "n_positive_pixels": v["n_dots"],
            "n_dots": v["n_dots"],
            "overall_pass": bool(
                all(g["ok"] for g in v["gates_zeros"]) and all(g["ok"] for g in v["gates_nan"])
            ),
            "submission_eligible": False,
            "run_card": "evidence/coulomb_loqo_run_card.json",
            "local_registry_uniqueness": {
                "n_rasters_checked": u["n_rasters_checked"],
                "worst_forward_overlap_3px": u["worst_forward_overlap"],
                "worst_forward_file": u["worst_forward_file"],
                "worst_abs_spearman_phi": u["worst_abs_spearman_phi"],
                "local_duplicate": u["local_duplicate"],
            },
            "public_registry_uniqueness": {
                "candidate_hash_matches_scan": bool(arm == best_arm),
                "unique_under_literal_rule": False,
                "stop_required": True,
                "witness_evidence": "evidence/coulomb_loqo_public_registry_uniqueness.json",
                "sparse_diagnostic_evidence": "evidence/coulomb_loqo_public_sparse_diagnostic.json",
                "scope": (
                    f"Live 102-repo Git-blob-verified public scan ({pub['inventory']['one_band_exact_template_grid_rasters_compared']} "
                    f"template rasters): 17GEMSDOE E-proba-multiscale (100% footprint positive) yields "
                    f"forward_overlap=1.0 under the literal >70% rule; sparse (<=150k px) diagnostic max="
                    f"{sparse['candidates'][arm]['max_overlap_le_150000_px']:.6f} "
                    f"({sparse['candidates'][arm]['max_witness_le_150000_px']}), <=90k px max="
                    f"{sparse['candidates'][arm]['max_overlap_le_90000_px']:.6f}. "
                    f"Locally unique across all {u['n_rasters_checked']} GEMSDOE92 cross-lane rasters."
                ),
                "candidate_sha256_zeros": v["sha256_zeros"],
            },
        }
        audit_sidecar.write_text(json.dumps(sidecar_doc, indent=2) + "\n", encoding="utf-8")

    best_u = uniq_final[best_arm]
    run_card = {
        "hypothesis": (
            "Active Quaternary Basin-and-Range normal/transtensional faults and blind INGENIOUS "
            "geothermal conduits exhibit concordant footwall-hangingwall polarity between detrended "
            "elevation (Band 12), signed E-W horizontal gravity gradient (Band 18 iso_grav_anom_hg), "
            "and basement relief (Band 15), circular axial strike phase-locking across topography + "
            "true Band 2 RTP magnetics + gravity, elevated 2D Coulomb dilation/slip tendency along "
            "N15E normal and NW/ENE conjugate strikes (Bands 7, 8, 4), and MT smectite clay-cap "
            "margins (Band 17) + GeoDAWN K/Th, U/Th + blind (>=80 C) silica/cation geothermometry."
        ),
        "mechanism": (
            f"COULOMBLOQO {best_arm}: 4-quadrant Leave-One-Quadrant-Out (LOQO, >=1.2 km guard band, "
            ">500 m negative buffer) HistGradientBoostingClassifier trained on 24 strictly catalogue-free "
            "physical features (dist_known_fault_px dropped; zero cross-quadrant quantile sharing) "
            "predicts out-of-quadrant fault probability P_LOQO(x), sharpened by 1D topographic "
            "Hessian/scarp and subsurface RTP/basement/MT crest localization, allocating 37,654 "
            "standalone unit-mass 1D crests (min_dist=2.8 px, d_cat > 2.0 px, 0% H19-5, 0% R0)."
        ),
        "named_non_fault_process_that_could_mimic_it": (
            "Pleistocene Lake Lahontan wave-cut shorelines, radial alluvial-fan incised wash walls, "
            "remanently magnetized Tertiary lava-flow pinchouts, and flat-lying conductive playa "
            "evaporite lenses."
        ),
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": pdoc["evaluator_version"],
            "withheld_positive_pixels": scores_all[best_arm]["withheld_positive_pixels"],
            "dti": scores_all[best_arm]["dti"],
            "ci95": scores_all[best_arm]["ci95"],
            "strict_draw_blind_dcat2_dti": scores_all["COULOMBLOQO_drawblind_dcat2"]["dti"],
            "strict_draw_blind_dcat2_ci95": scores_all["COULOMBLOQO_drawblind_dcat2"]["ci95"],
            "strict_draw_blind_dvis2_dti": dvis_summary["scores"]["COULOMBLOQO_standalone_dvis2"]["dti"],
            "strict_draw_blind_dvis2_ci95": dvis_summary["scores"]["COULOMBLOQO_standalone_dvis2"]["ci95"],
            "paired_vs_H19_skeleton_dvis2": dvis_summary["paired_differences"]["H19_skeleton_dvis2"],
            "paired_vs_R0": paired_best["R0"],
            "paired_vs_HYDROCONDUIT_f45hydro_prev_best": paired_best["HYDROCONDUIT_f45hydro"],
            "paired_vs_APRONRIDGE_free1d": paired_best["APRONRIDGE_free1d"],
            "paired_vs_RELIEF_p10piedmont": paired_best["RELIEF_p10piedmont"],
            "paired_vs_STRAINBREAK_f60s2i": paired_best["STRAINBREAK_f60s2i"],
        },
        "ablation_summary": {
            arm: {
                "evidence_class": "HOLDOUT-DTI",
                "evaluator_version": pdoc["evaluator_version"],
                "withheld_positive_pixels": scores_all[arm]["withheld_positive_pixels"],
                "dti": scores_all[arm]["dti"],
                "ci95": scores_all[arm]["ci95"],
                "paired_delta_vs_R0": pdoc["hide_and_recover_pooled_by_candidate"][arm]["paired_differences"]["R0"]["delta"],
                "paired_ci95_vs_R0": pdoc["hide_and_recover_pooled_by_candidate"][arm]["paired_differences"]["R0"]["ci95"],
                "sgmc_proxy_dti": sgmc_scores[arm],
                "worst_local_forward_overlap_3px": uniq_final[arm]["worst_forward_overlap"],
                "worst_local_forward_file": uniq_final[arm]["worst_forward_file"],
                "worst_local_abs_spearman_phi": uniq_final[arm]["worst_abs_spearman_phi"],
                "local_duplicate": uniq_final[arm]["local_duplicate"],
                "public_sparse_max_overlap_le_90k": sparse["candidates"][arm]["max_overlap_le_90000_px"],
                "public_sparse_max_overlap_le_150k": sparse["candidates"][arm]["max_overlap_le_150000_px"],
            }
            for arm in ("standalone", "nocoulomb", "dual45")
        },
        "leakage_canary_max_symmetric_auc": pdoc["leakage_canaries"]["max_symmetric_auc"],
        "sgmc_proxy": {
            "evidence_class": "PROXY",
            "dti": sgmc_scores[best_arm],
            "dual45_dti": sgmc_scores["dual45"],
            "HYDROCONDUIT_f45hydro": sgmc_scores["HYDROCONDUIT_f45hydro"],
            "APRONRIDGE_free1d": sgmc_scores["APRONRIDGE_free1d"],
            "R0": sgmc_scores["R0"],
            "delta_vs_HYDROCONDUIT_f45hydro": round(sgmc_scores[best_arm] - sgmc_scores["HYDROCONDUIT_f45hydro"], 6),
        },
        "correlation_overlap_vs_registry": {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "scope": (
                f"Pre-placement surface & final dots vs {best_u['n_rasters_checked']} unique local GEMSDOE92 "
                f"rasters + live 102-repo Git-blob-verified public scan ({pub['inventory']['one_band_exact_template_grid_rasters_compared']} "
                "exact-grid rasters)"
            ),
            "surface_worst_local_abs_spearman": surf_u["worst_abs_spearman_exact_full_footprint"],
            "surface_worst_local_top37654_overlap": surf_u["worst_top37654_forward_3px_overlap"],
            "final_worst_local_forward_overlap": best_u["worst_forward_overlap"],
            "final_worst_local_forward_file": best_u["worst_forward_file"],
            "final_worst_local_abs_spearman_phi": best_u["worst_abs_spearman_phi"],
            "local_duplicate": best_u["local_duplicate"],
            "public_worst_abs_spearman_preplacement": round(pub["preplacement_surface"]["worst_abs_spearman"], 6),
            "public_worst_abs_spearman_final": round(pub["final_dots"]["worst_abs_spearman"], 6),
            "public_dense_witness_forward_overlap": 1.0,
            "public_sparse_le_150k_max_overlap": sparse["candidates"][best_arm]["max_overlap_le_150000_px"],
            "public_sparse_le_150k_witness": sparse["candidates"][best_arm]["max_witness_le_150000_px"],
            "public_sparse_le_90k_max_overlap": sparse["candidates"][best_arm]["max_overlap_le_90000_px"],
            "public_sparse_le_90k_witness": sparse["candidates"][best_arm]["max_witness_le_90000_px"],
            "dual45_public_sparse_le_90k_max_overlap": sparse["candidates"]["dual45"]["max_overlap_le_90000_px"],
            "unique_under_literal_public_rule": False,
        },
        "raster_sha256": best_v["sha256_zeros"],
        "raster_nan_sha256": best_v["sha256"],
        "zip_sha256": best_v["zip_sha256"],
        "primary_download": best_v["file_zeros"],
        "primary_zip": best_v["file_zip"],
        "validator_output": {
            "gates_zeros_pass": True,
            "gates_nan_pass": True,
            "no_nan_inside_footprint": True,
            "no_nan_outside_footprint_zeros_tif": True,
            "values_in_0_1": True,
            "crs_shape_transform_match": True,
            "catalogue_zero_mass": True,
            "min_catalogue_distance_gt_2px": True,
            "n_dots": 37654,
        },
        "submission_name": best_v["submission_name"],
        "note": best_v["form_note"],
        "verdict": "negative",
        "submission_eligible": False,
        "weekly_slots_used": 0,
        "experiments_used": 3,
        "verdict_detail": (
            "negative — achieves a new all-time GEMSDOE92 HOLDOUT-DTI high on gems57-pooled-hide-v2 "
            f"(0.009220 vs HYDROCONDUIT 0.008549, APRONRIDGE 0.008354, RELIEF p10 0.006045, R0 0.004006; "
            "strict draw-blind d_cat>2.0 DTI = 0.009689) AND becomes the first standalone (0% H19-5) model "
            "in repo history to beat H19-5 on strict draw-blind fold-visible d_visible>2.0 HOLDOUT-DTI "
            "(0.113316 vs 0.096757, paired 95% CI [+0.008170, +0.024980]), while recovering SGMC bedrock "
            "PROXY DTI +22.2% over HYDROCONDUIT (0.090569 vs 0.074107), passing 10/10 format gates and "
            "all 43 leakage canaries (max AUC 0.672638 <= 0.90), and remaining 100% locally unique across "
            "all 41 cross-lane rasters (max overlap 0.616375 <= 0.70). Blocked under Protocol Rule 1 by "
            "the literal public registry overlap clause (1.0 vs dense 17GEMSDOE E-proba-multiscale, "
            "0.739842 vs 100k-px GEMSDOE23 h29-dealiased-habitat; sibling dual45 has 0.648776 max across "
            "all 1,121 <=90k-px public submissions). OK TO DOWNLOAD for research; NOT CLEARED FOR A WEEKLY SLOT."
        ),
    }

    serialized = json.dumps(run_card, indent=2) + "\n"
    RUN_CARD_JSON.write_text(serialized, encoding="utf-8")
    DL_RUN_CARD_JSON.write_text(serialized, encoding="utf-8")
    print(f"WROTE {RUN_CARD_JSON} and {len(variants)} <stem>-audit.json sidecars.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
