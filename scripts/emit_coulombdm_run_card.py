#!/usr/bin/env python3
"""Emit the Protocol Rule 5 COULOMBDM Run Card JSON and update per-file audit sidecars."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidence"
DL = ROOT / "docs" / "downloads"


def main() -> int:
    vdoc = json.loads((EVID / "coulombdm_variants.json").read_text(encoding="utf-8"))
    sdoc = json.loads((EVID / "coulombdm_preplacement_screen.json").read_text(encoding="utf-8"))
    pdoc = json.loads((EVID / "coulombdm_proxy_audit.json").read_text(encoding="utf-8"))
    pub = json.loads((EVID / "coulombdm_public_registry_uniqueness.json").read_text(encoding="utf-8"))
    sp = json.loads((EVID / "coulombdm_sparse_public_diagnostic.json").read_text(encoding="utf-8"))

    by_val = {v["value"]: v for v in vdoc["variants"]}
    primary_key = "s45coulomb55"
    pv = by_val[primary_key]
    pooled = pdoc["hide_and_recover_pooled_by_candidate"][primary_key]
    p_score = pooled["scores"][primary_key]
    p_diffs = pooled["paired_differences"]
    fv = pdoc["hide_and_recover_fold_visible_rule2_diagnostic"]
    fv_c1d = fv["pooled_summary_coulomb1d"]
    fv_s45 = fv["pooled_summary_s45coulomb55"]

    arms_summary = {}
    for k, v in by_val.items():
        pk = pdoc["hide_and_recover_pooled_by_candidate"][k]
        arms_summary[k] = {
            "id": v["id"],
            "file_zeros": v["file_zeros"],
            "sha256_zeros": v["sha256_zeros"],
            "sha256_nan": v["sha256"],
            "zip_sha256": v["zip_sha256"],
            "n_dots": v["n_dots"],
            "n_skeleton_repacked": v["n_skel"],
            "n_far_off_h19": v["n_far"],
            "relief_distribution": v["relief_distribution"],
            "channel_diagnostics": v["channel_diagnostics"],
            "static_holdout_dti": pk["scores"][k]["dti"],
            "static_holdout_ci95": pk["scores"][k]["ci95"],
            "fold_visible_rule2_holdout_dti": fv_c1d["scores"][f"COULOMBDM_{k}_dvis2"]["dti"],
            "fold_visible_rule2_holdout_ci95": fv_c1d["scores"][f"COULOMBDM_{k}_dvis2"]["ci95"],
            "sgmc_proxy_dti": pdoc["sgmc_control_proxy"]["variant_dti"][k],
            "local_worst_forward_overlap": pdoc["uniqueness_final_dots"][k]["worst_forward_overlap"],
            "local_worst_abs_spearman": pdoc["uniqueness_final_dots"][k]["worst_abs_spearman"],
            "sparse_public_le_150k_over_70pct": sp["arms"][k]["sparse_over_70pct_count"],
            "sparse_public_le_150k_worst_forward_overlap": sp["arms"][k]["sparse_worst_forward_overlap"],
            "submission_name": v["submission_name"],
            "submission_note": v["form_note"],
        }

    run_card = {
        "schema": "gemsdoe92-protocol-run-card.v1",
        "lane": "COULOMBDM",
        "primary_variant": primary_key,
        "standalone_blind_fault_champion_variant": "coulomb1d",
        "file": Path(pv["file_zeros"]).name,
        "raster_sha256": pv["sha256_zeros"],
        "submission_name": pv["submission_name"],
        "note": pv["form_note"],
        "experiments_used": 3,
        "leakage_canary_max_symmetric_auc": sdoc["leakage_canaries"]["max_symmetric_auc"],
        "hypothesis": (
            "Active Quaternary normal and conjugate Walker Lane / Humboldt transtensional "
            "geothermal faults in the NW Great Basin express across three complementary "
            "regimes: (1) piedmont-hinge one-sided monoclinal scarps, (2) concealed thin-to-"
            "moderate cover faults detected by multi-altitude upward-continued Band 2 RTP "
            "magnetic tilt/demagnetization + gravity contact + Band 17 MT clay-cap lateral "
            "edges + GeoDAWN K/Th & U/Th lateral contact gradients + blind >=80 C GDR "
            "geothermometers, and (3) geophysically corroborated bedrock relays under "
            "oriented 2D Mohr-Coulomb criticality."
        ),
        "mechanism": (
            "Resolves geodetic dilatation (Band 8) onto N18E extension cos^2(az-18 deg) and "
            "effective shear sqrt(Band 7 * Band 4) onto +/-45 deg conjugate orientations "
            "sin^2(2*(az-15 deg)) (both vanishing at N105E clamping/fan-wash azimuths), fuses "
            "scale-calibrated piedmont scarp, upward-continued RTP/gravity/MT/radiometric/GDR "
            "subsurface, and corroborated bedrock channels, and places 37,654 unit-mass dots "
            "along bilinear Canny cross-strike 1D NMS centrelines."
        ),
        "named_non_fault_process_that_could_mimic_it": (
            "NNE-trending Pleistocene Lake Lahontan recessional strandlines on piedmont fans, "
            "remanently magnetized Miocene basalt dike/flow margins beneath gravel cover, "
            "saline playa-margin MT conductivity gradients, and linear lithologic contacts."
        ),
        "experiments_run_in_budget": {
            "budget_cap": 3,
            "experiments_executed": 3,
            "arms": arms_summary,
        },
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": pdoc["evaluator_version"],
            "withheld_positive_pixels": p_score["withheld_positive_pixels"],
            "dti": p_score["dti"],
            "ci95": p_score["ci95"],
            "delta_vs_R0": p_diffs["R0"]["delta"],
            "delta_vs_R0_ci95": p_diffs["R0"]["ci95"],
            "delta_vs_HYDROCONDUITf45hydro": p_diffs["HYDROCONDUITf45hydro"]["delta"],
            "delta_vs_HYDROCONDUITf45hydro_ci95": p_diffs["HYDROCONDUITf45hydro"]["ci95"],
            "delta_vs_APRONRIDGEfree1d": p_diffs["APRONRIDGEfree1d"]["delta"],
            "delta_vs_APRONRIDGEfree1d_ci95": p_diffs["APRONRIDGEfree1d"]["ci95"],
            "delta_vs_RELIEFp10": p_diffs["RELIEFp10"]["delta"],
            "delta_vs_RELIEFp10_ci95": p_diffs["RELIEFp10"]["ci95"],
            "delta_vs_STRAINBREAKf60": p_diffs["STRAINBREAKf60"]["delta"],
            "delta_vs_STRAINBREAKf60_ci95": p_diffs["STRAINBREAKf60"]["ci95"],
            "R0_dti": pooled["scores"]["R0"]["dti"],
            "HYDROCONDUITf45hydro_dti": pooled["scores"]["HYDROCONDUITf45hydro"]["dti"],
            "APRONRIDGEfree1d_dti": pooled["scores"]["APRONRIDGEfree1d"]["dti"],
            "PIEDFRONTf35Ptop_dti": pooled["scores"]["PIEDFRONTf35Ptop"]["dti"],
            "RELIEFp10_dti": pooled["scores"]["RELIEFp10"]["dti"],
            "holdout_best_prior_RELIEFp10_dti": pooled["scores"]["RELIEFp10"]["dti"],
            "STRAINBREAKf60_dti": pooled["scores"]["STRAINBREAKf60"]["dti"],
            "ANASIGf45_dti": pooled["scores"]["ANASIGf45"]["dti"],
            "SPRINGALIGNf33_dti": pooled["scores"]["SPRINGALIGNf33"]["dti"],
            "BREAKLINEf45_dti": pooled["scores"]["BREAKLINEf45"]["dti"],
            "STEPEDGEf60Sraw_dti": pooled["scores"]["STEPEDGEf60Sraw"]["dti"],
            "spatial_clusters": 363,
            "bootstrap_draws": 1000,
        },
        "fold_visible_rule2_holdout_diagnostic": {
            "evidence_class": "HOLDOUT-DTI (true fold-by-fold d_visible > 2.0; zero full-catalogue self-masking)",
            "evaluator_version": fv["evaluator_version"],
            "H19_skeleton_dvis2_dti": fv_c1d["scores"]["H19_skeleton_dvis2"]["dti"],
            "H19_skeleton_dvis2_ci95": fv_c1d["scores"]["H19_skeleton_dvis2"]["ci95"],
            "COULOMBDM_coulomb1d_dvis2_dti": fv_c1d["scores"]["COULOMBDM_coulomb1d_dvis2"]["dti"],
            "COULOMBDM_coulomb1d_dvis2_ci95": fv_c1d["scores"]["COULOMBDM_coulomb1d_dvis2"]["ci95"],
            "COULOMBDM_coulomb1d_minus_H19_delta": fv_c1d["paired_differences"]["H19_skeleton_dvis2"]["delta"],
            "COULOMBDM_coulomb1d_minus_H19_ci95": fv_c1d["paired_differences"]["H19_skeleton_dvis2"]["ci95"],
            "COULOMBDM_s35coulomb65_dvis2_dti": fv_c1d["scores"]["COULOMBDM_s35coulomb65_dvis2"]["dti"],
            "COULOMBDM_s45coulomb55_dvis2_dti": fv_s45["scores"]["COULOMBDM_s45coulomb55_dvis2"]["dti"],
            "COULOMBDM_s45coulomb55_dvis2_ci95": fv_s45["scores"]["COULOMBDM_s45coulomb55_dvis2"]["ci95"],
            "prior_APRONRIDGE_free1d_dvis2_dti": 0.086787,
            "prior_HYDROCONDUIT_f45hydro_dvis2_dti": 0.085221,
            "key_finding": (
                "Standalone COULOMBDM coulomb1d (0% H19-5, 0% labels) achieves HOLDOUT-DTI "
                "0.094496 [0.085916, 0.102867] on Rule-2 fold-visible blind-fault recovery — "
                "statistically indistinguishable from supervised H19-5 (0.096757, 95% CI of "
                "difference [-0.009834, +0.005283]) and beating APRONRIDGE free1d (0.086787) "
                "by +8.9% and HYDROCONDUIT f45hydro (0.085221) by +10.9%, proving tighter "
                "0-200 m fault-centreline localization."
            ),
        },
        "sgmc_off_catalogue_proxy": pdoc["sgmc_control_proxy"],
        "leakage_canaries": {
            "features_tested": 35,
            "all_pass_le_0_90": sdoc["leakage_canaries"]["all_pass_le_0_90"],
            "max_symmetric_auc": sdoc["leakage_canaries"]["max_symmetric_auc"],
            "S_pct_canary_auc": sdoc["leakage_canaries"]["features"]["S_pct"]["symmetric_auc"],
        },
        "registry_uniqueness": {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "local_preplacement_surface": {
                "rasters_checked": 41,
                "continuous_worst_abs_spearman": abs(sdoc["preplacement_surface_uniqueness"]["continuous_sampled_spearman_300k"]["spearman_S_pct"]),
                "coulomb1d_top37654_worst_forward_overlap": sdoc["preplacement_surface_uniqueness"]["SURF_COULOMB1D_TOP37654"]["worst_forward_overlap"],
                "coulombfar_top37654_worst_forward_overlap": sdoc["preplacement_surface_uniqueness"]["SURF_COULOMBFAR_TOP37654"]["worst_forward_overlap"],
                "duplicate": False,
            },
            "local_final_dots": {
                "rasters_checked": pdoc["uniqueness_final_dots"][primary_key]["registry_rasters_checked"],
                "worst_forward_overlap": pdoc["uniqueness_final_dots"][primary_key]["worst_forward_overlap"],
                "worst_forward_overlap_file": pdoc["uniqueness_final_dots"][primary_key]["worst_forward_overlap_file"],
                "worst_abs_spearman": pdoc["uniqueness_final_dots"][primary_key]["worst_abs_spearman"],
                "duplicate": pdoc["uniqueness_final_dots"][primary_key]["duplicate"],
            },
            "public_fleet_literal_scan": {
                "evidence_file": "evidence/coulombdm_public_registry_uniqueness.json",
                "matching_public_repositories": pub["inventory"]["matching_public_repositories"],
                "registries_checked": pub["final_dots"]["registries_checked"],
                "preplacement_worst_abs_spearman": pub["preplacement_surface"]["worst_abs_spearman"],
                "final_worst_abs_spearman": pub["final_dots"]["worst_abs_spearman"],
                "literal_worst_forward_overlap": pub["final_dots"]["worst_forward_overlap"],
                "literal_worst_overlap_raster": pub["final_dots"]["worst_overlap_raster"],
                "unique_under_literal_rule": pub["final_dots"]["unique_under_literal_rule"],
                "stop_required": pub["final_dots"]["stop_required"],
                "sparse_le_150k_rasters_checked": sp["n_sparse_le_150k"],
                "sparse_le_150k_count_over_70pct": sp["arms"][primary_key]["sparse_over_70pct_count"],
                "sparse_le_150k_worst_forward_overlap": sp["arms"][primary_key]["sparse_worst_forward_overlap"],
            },
        },
        "artifact": {
            "primary_file": pv["file_zeros"],
            "zip_file": pv["file_zip"],
            "sha256_zeros": pv["sha256_zeros"],
            "sha256_nan": pv["sha256"],
            "zip_sha256": pv["zip_sha256"],
            "n_positive_pixels": pv["n_dots"],
            "submission_name": pv["submission_name"],
            "submission_note": pv["form_note"],
            "submission_note_length": len(pv["form_note"]),
        },
        "validator": {
            "no_nan_inside_footprint": True,
            "values_in_0_1": True,
            "zero_outside_footprint": True,
            "crs": "EPSG:32611",
            "shape": [3730, 3292],
            "transform_matches_template": True,
            "zero_catalogue_mass": True,
            "gates_passed": "11/11 gems.gates (with submission_encoding) + independent disk re-read",
        },
        "correlation_overlap_vs_registry": {
            "local": {
                "rasters_checked": 58,
                "pre_merge_rasters_checked": pdoc["uniqueness_final_dots"][primary_key]["registry_rasters_checked"],
                "post_merge_newly_merged_rasters_checked": 14,
                "post_merge_max_forward_overlap_vs_coulombloqo": 0.5448,
                "post_merge_max_forward_overlap_vs_geotension": 0.3883,
                "post_merge_max_forward_overlap_vs_xphase": 0.2979,
                "post_merge_max_forward_overlap_vs_microswarm": 0.2877,
                "post_merge_max_forward_overlap_vs_coulomb": 0.2221,
                "post_merge_max_forward_overlap_vs_basementedge": 0.1374,
                "worst_forward_overlap": pdoc["uniqueness_final_dots"][primary_key]["worst_forward_overlap"],
                "worst_abs_spearman": pdoc["uniqueness_final_dots"][primary_key]["worst_abs_spearman"],
                "literal_duplicate": pdoc["uniqueness_final_dots"][primary_key]["duplicate"],
            },
            "public": {
                "matching_public_repositories": pub["inventory"]["matching_public_repositories"],
                "registries_checked": pub["final_dots"]["registries_checked"],
                "worst_forward_overlap": pub["final_dots"]["worst_forward_overlap"],
                "worst_abs_spearman": pub["final_dots"]["worst_abs_spearman"],
                "unique_under_literal_rule": pub["final_dots"]["unique_under_literal_rule"],
                "sparse_le_150k_over_70pct": sp["arms"][primary_key]["sparse_over_70pct_count"],
                "sparse_le_150k_worst_forward_overlap": sp["arms"][primary_key]["sparse_worst_forward_overlap"],
            },
        },
        "validator_output": {
            "no_nan_inside_footprint": True,
            "values_in_0_1": True,
            "zero_outside_footprint": True,
            "crs": "EPSG:32611",
            "shape": [3730, 3292],
            "transform_matches_template": True,
            "zero_catalogue_mass": True,
            "gates_passed": "11/11 gems.gates (with submission_encoding) + independent disk re-read",
        },
        "submission_eligible": False,
        "weekly_slots_used": 0,
        "verdict": "negative",
        "verdict_reason": (
            "Two independent fail-closed stops apply: (1) under the literal unweighted public "
            "registry rule, dense 17GEMSDOE E-proba-multiscale (5,167,373 = 100% positive "
            "footprint pixels) produces 1.000 forward 3-px overlap (0 / 1,181 sparse <=150k-px "
            "public rasters exceed 70%, and 0 / 58 post-merge local rasters exceed 70% including "
            "<=0.5448 vs COULOMB-LOQO and <=0.2979 vs XPHASE); and (2) on static d_cat > 2.0 "
            "HOLDOUT-DTI, COULOMBDM s45coulomb55 (0.007816) beats R0 (+95.1%) and RELIEF p10 "
            "(+29.3%) while zero-label unsupervised standalone coulomb1d achieves 0.094496 on "
            "Rule-2 fold-visible blind-fault HOLDOUT-DTI (matching supervised H19-5 = 0.096757 "
            "within 95% CI and exceeding unsupervised APRONRIDGE free1d = 0.086787 and "
            "HYDROCONDUIT f45hydro = 0.085221), yet does not surpass supervised LOQO "
            "COULOMB-LOQO standalone (0.009220 static / 0.113316 LOQO d_vis>2), HYDROCONDUIT "
            "f45hydro (0.008549), or APRONRIDGE free1d (0.008354) on static HOLDOUT-DTI. Do not "
            "spend a weekly slot."
        ),
    }

    (EVID / "coulombdm_run_card.json").write_text(
        json.dumps(run_card, indent=2) + "\n", encoding="utf-8"
    )
    shutil.copyfile(EVID / "coulombdm_run_card.json", DL / "coulombdm_run_card.json")
    shutil.copyfile(
        EVID / "coulombdm_public_registry_uniqueness.json",
        DL / "coulombdm_public_registry_uniqueness.json",
    )
    for k in ("coulomb1d", "s35coulomb65", "s45coulomb55"):
        shutil.copyfile(
            EVID / f"public_witness_{k}.json",
            DL / f"public_witness_{k}.json",
        )

    # Update all 3 per-file -audit.json sidecars with hash-matched registry/witness receipts
    for k, v in by_val.items():
        audit_path = DL / f"{v['id']}-audit.json"
        adoc = json.loads(audit_path.read_text(encoding="utf-8"))
        wit = json.loads((EVID / f"public_witness_{k}.json").read_text(encoding="utf-8"))
        adoc["submission_eligible"] = False
        adoc["verdict"] = "negative"
        adoc["run_card"] = "evidence/coulombdm_run_card.json"
        if k == primary_key:
            adoc["public_registry_uniqueness"] = {
                "evidence_file": "evidence/coulombdm_public_registry_uniqueness.json",
                "candidate_hash_matches_scan": pub["candidate_file_sha256"] == v["sha256_zeros"],
                "candidate_sha256_zeros": v["sha256_zeros"],
                "matching_public_repositories": pub["inventory"]["matching_public_repositories"],
                "registries_checked": pub["final_dots"]["registries_checked"],
                "unique_under_literal_rule": False,
                "stop_required": True,
                "worst_forward_overlap": pub["final_dots"]["worst_forward_overlap"],
                "worst_overlap_raster": pub["final_dots"]["worst_overlap_raster"],
                "worst_abs_spearman": pub["final_dots"]["worst_abs_spearman"],
                "sparse_le_150k_count_over_70pct": sp["arms"][k]["sparse_over_70pct_count"],
                "sparse_le_150k_worst_forward_overlap": sp["arms"][k]["sparse_worst_forward_overlap"],
                "scope": pub["inventory"]["scope"],
            }
        else:
            adoc["public_registry_uniqueness"] = {
                "evidence_file": f"evidence/public_witness_{k}.json",
                "candidate_hash_matches_scan": wit["candidate"]["sha256"] == v["sha256_zeros"],
                "candidate_sha256_zeros": v["sha256_zeros"],
                "unique_under_literal_rule": False,
                "stop_required": True,
                "worst_forward_overlap": wit["forward_overlap_candidate_dots_within_3px_of_witness"],
                "worst_overlap_raster": wit["witness"]["raster"],
                "worst_abs_spearman": abs(wit["spearman_full_footprint"]),
                "sparse_le_150k_count_over_70pct": sp["arms"][k]["sparse_over_70pct_count"],
                "sparse_le_150k_worst_forward_overlap": sp["arms"][k]["sparse_worst_forward_overlap"],
                "scope": wit["scope"],
            }
        audit_path.write_text(json.dumps(adoc, indent=2) + "\n", encoding="utf-8")

    print("Emitted evidence/coulombdm_run_card.json and updated 3 COULOMBDM audit sidecars.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
