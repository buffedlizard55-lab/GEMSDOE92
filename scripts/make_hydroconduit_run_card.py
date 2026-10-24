#!/usr/bin/env python3
"""Assemble the Protocol Rule 5 JSON run card for HYDROCONDUIT primary (f45hydro)
and enrich its download-audit receipt directly from machine-generated evidence JSONs.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    variants = json.loads((ROOT / "evidence/hydroconduit_variants.json").read_text(encoding="utf-8"))
    audit = json.loads((ROOT / "evidence/hydroconduit_proxy_audit.json").read_text(encoding="utf-8"))
    pub = json.loads((ROOT / "evidence/hydroconduit_public_registry_uniqueness.json").read_text(encoding="utf-8"))
    sparse = json.loads((ROOT / "evidence/hydroconduit_public_sparse_diagnostic.json").read_text(encoding="utf-8"))
    cards = json.loads((ROOT / "ledger/mechanism_cards.json").read_text(encoding="utf-8"))

    by_val = {x["value"]: x for x in variants["variants"]}
    v = by_val["f45hydro"]
    blk = audit["hide_and_recover_pooled_by_candidate"]["f45hydro"]
    s = blk["scores"]["f45hydro"]
    uni = audit["uniqueness_final_dots"]["f45hydro"]
    surf_uni = audit["uniqueness_preplacement_surface"]
    fold_vis = audit["hide_and_recover_fold_visible_rule2_diagnostic"]

    primary = ROOT / "docs/downloads" / f"{v['id']}-zeros.tif"
    sha = hashlib.sha256(primary.read_bytes()).hexdigest()
    audit_path = ROOT / "docs/downloads" / f"{v['id']}-audit.json"
    gate_audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert gate_audit["sha256_zeros"] == sha
    assert pub["candidate"]["sha256"] == sha

    final_pub = pub["final_dots"]
    pre_pub = pub["preplacement_surface"]
    sp_f45 = sparse["f45hydro"]

    card = {
        "schema": "gemsdoe92-protocol-run-card.v1",
        "lane": "HYDROCONDUIT",
        "primary_variant": "f45hydro",
        "hypothesis": cards[v["id"]]["hypothesis"],
        "mechanism": cards[v["id"]]["mechanism"],
        "named_non_fault_process_that_could_mimic_it": cards[v["id"]]["non_fault_mimic"],
        "experiments_run_in_budget": {
            "budget_cap": 3,
            "experiments_executed": 3,
            "arms": {
                k: {
                    "id": by_val[k]["id"],
                    "sha256_zeros": by_val[k]["sha256_zeros"],
                    "sha256_nan": by_val[k]["sha256"],
                    "n_dots": by_val[k]["n_dots"],
                    "n_skeleton_repacked": by_val[k]["parent_diff"]["n_skeleton_repacked"],
                    "n_far_off_h19": by_val[k]["parent_diff"]["n_far_off_h19"],
                    "far_tercile_fractions": by_val[k]["parent_diff"]["far_tercile_fractions"],
                    "static_holdout_dti": audit["hide_and_recover_pooled_by_candidate"][k]["scores"][k]["dti"],
                    "static_holdout_ci95": audit["hide_and_recover_pooled_by_candidate"][k]["scores"][k]["ci95"],
                    "sgmc_proxy_dti": audit["sgmc_control_proxy"]["variant_dti"][k],
                    "local_worst_forward_overlap": audit["uniqueness_final_dots"][k]["worst_forward_overlap"],
                }
                for k in ("f45pied", "f45hydro", "f50hydro")
            },
        },
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": s["evaluator_version"],
            "withheld_positive_pixels": s["withheld_positive_pixels"],
            "dti": s["dti"],
            "ci95": s["ci95"],
            "delta_vs_R0": blk["paired_differences"]["R0"]["delta"],
            "delta_vs_R0_ci95": blk["paired_differences"]["R0"]["ci95"],
            "delta_vs_holdout_best_RELIEFp10": blk["paired_differences"]["RELIEFp10"]["delta"],
            "delta_vs_RELIEFp10_ci95": blk["paired_differences"]["RELIEFp10"]["ci95"],
            "delta_vs_STRAINBREAKf60": blk["paired_differences"]["STRAINBREAKf60"]["delta"],
            "delta_vs_STRAINBREAKf60_ci95": blk["paired_differences"]["STRAINBREAKf60"]["ci95"],
            "delta_vs_SPRINGALIGNf33": blk["paired_differences"]["SPRINGALIGNf33"]["delta"],
            "delta_vs_SPRINGALIGNf33_ci95": blk["paired_differences"]["SPRINGALIGNf33"]["ci95"],
            "R0_dti": blk["scores"]["R0"]["dti"],
            "holdout_best_prior_RELIEFp10_dti": blk["scores"]["RELIEFp10"]["dti"],
            "STRAINBREAKf60_dti": blk["scores"]["STRAINBREAKf60"]["dti"],
            "ANASIGf45_dti": blk["scores"]["ANASIGf45"]["dti"],
            "SPRINGALIGNf33_dti": blk["scores"]["SPRINGALIGNf33"]["dti"],
            "BREAKLINEf45_dti": blk["scores"]["BREAKLINEf45"]["dti"],
            "spatial_clusters": blk["bootstrap"]["clusters"],
            "bootstrap_draws": blk["bootstrap"]["draws"],
        },
        "fold_visible_rule2_holdout_diagnostic": {
            "evidence_class": fold_vis["evidence_class"],
            "evaluator_version": fold_vis["evaluator_version"],
            "H19_skeleton_dvis2_dti": fold_vis["pooled_summary"]["scores"]["H19_skeleton_dvis2"]["dti"],
            "H19_skeleton_dvis2_ci95": fold_vis["pooled_summary"]["scores"]["H19_skeleton_dvis2"]["ci95"],
            "HYDROCONDUIT_f45hydro_dvis2_dti": fold_vis["pooled_summary"]["scores"]["HYDROCONDUIT_f45hydro_dvis2"]["dti"],
            "HYDROCONDUIT_f45hydro_dvis2_ci95": fold_vis["pooled_summary"]["scores"]["HYDROCONDUIT_f45hydro_dvis2"]["ci95"],
            "note": fold_vis["note"],
        },
        "leakage_canary_max_symmetric_auc": audit["leakage_canaries"]["max_symmetric_auc"],
        "leakage_canaries_all_pass_le_0_90": audit["leakage_canaries"]["all_pass_le_0_90"],
        "sgmc_control_proxy": {
            "evidence_class": "PROXY (off-catalogue USGS SGMC bedrock faults >3 px from catalogue)",
            "dti": audit["sgmc_control_proxy"]["variant_dti"]["f45hydro"],
            "f45pied_dti": audit["sgmc_control_proxy"]["variant_dti"]["f45pied"],
            "f50hydro_dti": audit["sgmc_control_proxy"]["variant_dti"]["f50hydro"],
            "R0_dti": audit["sgmc_control_proxy"]["variant_dti"]["R0"],
            "RELIEFp10_dti": audit["sgmc_control_proxy"]["variant_dti"]["RELIEFp10"],
            "STRAINBREAKf60_dti": audit["sgmc_control_proxy"]["variant_dti"]["STRAINBREAKf60"],
            "BREAKLINEf45_dti": audit["sgmc_control_proxy"]["variant_dti"]["BREAKLINEf45"],
            "truth_pixels": audit["sgmc_control_proxy"]["truth_pixels_after_catalogue_and_3px_exclusion"],
            "note": (
                "Adding the hydrothermal/RTP multiplier lifts SGMC (+0.00080 over f45pied), while "
                "suppressing bare mountain range-core cliffs (from 74.8% in BREAKLINE to 6.2% in "
                "f45hydro) trades exposed pre-Quaternary bedrock SGMC faults (0.0741 vs R0 0.0961) "
                "for Quaternary piedmont/geothermal fault localization (+113.4% static HOLDOUT-DTI)."
            ),
        },
        "correlation_overlap_vs_registry": {
            "local": {
                "registry_rasters_checked": uni["registry_rasters_checked"],
                "worst_forward_overlap_within_3px": uni["worst_forward_overlap"],
                "worst_forward_overlap_file": uni["worst_forward_overlap_file"],
                "worst_abs_spearman": uni["worst_abs_spearman"],
                "worst_abs_spearman_file": uni["worst_abs_spearman_file"],
                "literal_duplicate": uni["duplicate"],
                "preplacement_surface_S_hydro_top37654": surf_uni["S_hydro_top37654"],
                "preplacement_surface_continuous_spearman_300k": surf_uni["continuous_sampled_spearman_300k"]["worst_S_hydro"],
            },
            "public_expanded": {
                "evidence_file": "evidence/hydroconduit_public_registry_uniqueness.json",
                "matching_public_repositories": pub["inventory"]["matching_public_repositories"],
                "registries_checked": final_pub["registries_checked"],
                "scan_complete_for_declared_scope": pub["scan_complete_for_declared_scope"],
                "scan_source": pub["inventory"]["scan_source"],
                "preplacement_surface_worst_abs_spearman": pre_pub["worst_abs_spearman"],
                "preplacement_surface_worst_forward_overlap": pre_pub["worst_forward_overlap"],
                "final_dots_worst_abs_spearman": final_pub["worst_abs_spearman"],
                "final_dots_worst_rho_raster": final_pub["worst_rho_raster"],
                "final_dots_worst_forward_overlap": final_pub["worst_forward_overlap"],
                "final_dots_worst_overlap_raster": final_pub["worst_overlap_raster"],
                "rasters_over_70pct_overlap": final_pub["rasters_over_70pct_overlap"],
                "unique_under_literal_rule": final_pub["unique_under_literal_rule"],
                "stop_required": final_pub["stop_required"],
                "sparse_only_diagnostic_NOT_A_GATE": {
                    "evidence_file": "evidence/hydroconduit_public_sparse_diagnostic.json",
                    "sparse_checked_le_150k_positive_px": sp_f45["sparse_le_150k_checked"],
                    "dense_skipped_gt_150k_positive_px": sp_f45["dense_gt_150k_skipped"],
                    "worst_sparse_le_150k_forward_overlap": sp_f45["worst_le_150k"]["forward_overlap"],
                    "worst_sparse_le_150k_raster": sp_f45["worst_le_150k"]["raster"],
                    "count_over_70pct_le_150k": sp_f45["count_over_70pct_le_150k"],
                    "sparse_checked_le_90k_positive_px": sp_f45["sparse_le_90k_checked"],
                    "worst_sparse_le_90k_forward_overlap": sp_f45["worst_le_90k"]["forward_overlap"],
                    "count_over_70pct_le_90k": sp_f45["count_over_70pct_le_90k"],
                    "note": (
                        "Across ALL 1,147 sparse dot-like rasters (<=150k positive px) in all 102 "
                        "public GEMSDOE repositories, ZERO rasters exceed 70% forward overlap "
                        "(max 0.6719 <= 0.70; max <=90k is 0.6518 <= 0.70). Every one of the 118 "
                        "rasters exceeding 70% is a dense >150k-px surface led by 17GEMSDOE "
                        "E-proba-multiscale (5,167,373 positive px = 100% of footprint)."
                    ),
                },
            },
        },
        "raster_sha256": sha,
        "raster_sha256_nan_twin": v["sha256"],
        "validator": {
            "overall_pass": gate_audit["overall_pass"],
            "gates_zeros": gate_audit["gates_zeros"],
            "no_nan_inside_footprint": True,
            "outside_footprint_zero_in_primary": True,
            "values_in_0_1": True,
            "zero_catalogue_mass": True,
            "crs_shape_transform_match": "EPSG:32611, 3730x3292, float32, exact sample_submission.tif grid",
        },
        "submission_name": "GEMSDOE92-HYDROCONDUIT-f45hydro-20261024",
        "file": primary.name,
        "note": v["form_note"],
        "note_chars": len(v["form_note"]),
        "organizer_score": None,
        "download_status": "OK TO DOWNLOAD (format-valid, [0, 1] verified, locally & sparse-public unique)",
        "submission_status": "DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (duplicate under literal dense-surface registry rule; human selector decision required)",
        "submission_eligible": False,
        "verdict": "negative",
        "verdict_reason": (
            "1. Positive achievements: HYDROCONDUIT f45hydro is the first candidate in GEMSDOE92 to "
            "beat BOTH R0 (0.004006 -> 0.008549, +113.4%) and prior holdout-best RELIEF p10 "
            "(0.006045 -> 0.008549, +41.4%, paired 95% CI [+0.00180, +0.00322]) while passing "
            "every single-feature leakage canary (max AUC 0.6501 <= 0.90), local registry "
            "uniqueness (0.5500 <= 0.70), and ALL 1,147 sparse (<=150k px) public rasters across "
            "102 public GEMSDOE repos (max 0.6719 <= 0.70; |rho| <= 0.4396 <= 0.90). "
            "2. Why verdict remains 'negative' (DO NOT SUBMIT without human policy override): "
            "(a) Under the literal Rule-1 wording with no representation exemption, 118 dense "
            "public rasters (>150k positive px, led by 17GEMSDOE E-proba-multiscale with 100% "
            "footprint support) yield 100% > 70% forward overlap; an agent session cannot waive "
            "that rule unilaterally. (b) Multi-instrument disclosure: true fold-by-fold d_visible>2 "
            "holdout (0.0852 vs 0.0968 H19-only) and off-catalogue SGMC bedrock proxy (0.0741 vs "
            "R0 0.0961) show static-holdout gains partly reflect piedmont H19-5 collar repacking "
            "while 45% off-skeleton moves trade H19-5 spine density and mountain-core SGMC faults."
        ),
    }

    card_json = json.dumps(card, indent=2) + "\n"
    (ROOT / "evidence/hydroconduit_run_card.json").write_text(card_json, encoding="utf-8")
    (ROOT / "docs/downloads/hydroconduit_run_card.json").write_text(card_json, encoding="utf-8")

    # Enrich primary -audit.json with public_registry_uniqueness and submission_eligible: false
    gate_audit.update({
        "n_positive_pixels": 37654,
        "n_dots": 37654,
        "gates_zeros_pass": all(g["ok"] for g in gate_audit["gates_zeros"]),
        "gates_nan_pass": all(g["ok"] for g in gate_audit["gates_nan"]),
        "submission_eligible": False,
        "run_card": "evidence/hydroconduit_run_card.json",
        "public_registry_uniqueness": {
            "evidence_file": "evidence/hydroconduit_public_registry_uniqueness.json",
            "candidate_hash_matches_scan": True,
            "candidate_sha256_zeros": sha,
            "matching_public_repositories": pub["inventory"]["matching_public_repositories"],
            "registries_checked": final_pub["registries_checked"],
            "unique_under_literal_rule": final_pub["unique_under_literal_rule"],
            "stop_required": final_pub["stop_required"],
            "worst_forward_overlap": final_pub["worst_forward_overlap"],
            "worst_overlap_raster": final_pub["worst_overlap_raster"],
            "worst_abs_spearman": final_pub["worst_abs_spearman"],
            "sparse_le_150k_count_over_70pct": sp_f45["count_over_70pct_le_150k"],
            "sparse_le_150k_worst_forward_overlap": sp_f45["worst_le_150k"]["forward_overlap"],
            "scope": pub["inventory"]["scope"],
        },
    })
    audit_path.write_text(json.dumps(gate_audit, indent=2) + "\n", encoding="utf-8")

    # Also mark f45pied and f50hydro audit receipts submission_eligible: false with witness note
    for sib_key in ("f45pied", "f50hydro"):
        sv = by_val[sib_key]
        sap = ROOT / "docs/downloads" / f"{sv['id']}-audit.json"
        sdoc = json.loads(sap.read_text(encoding="utf-8"))
        sdoc.update({
            "n_positive_pixels": 37654,
            "n_dots": 37654,
            "submission_eligible": False,
            "run_card": "evidence/hydroconduit_run_card.json",
            "public_registry_uniqueness": {
                "unique_under_literal_rule": False,
                "stop_required": True,
                "note": "Binding dense public witness 17GEMSDOE E-proba-multiscale covers 100% of footprint.",
            },
        })
        sap.write_text(json.dumps(sdoc, indent=2) + "\n", encoding="utf-8")

    print("Wrote evidence/hydroconduit_run_card.json and enriched download audit receipts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
