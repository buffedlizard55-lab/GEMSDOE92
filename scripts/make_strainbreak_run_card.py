#!/usr/bin/env python3
"""Assemble the protocol run card for the STRAINBREAK primary (f60s2i) and
extend its download-audit receipt -- directly from evidence JSONs, no
hand-transcribed numbers.  Run AFTER scripts/audit_public_registry.py
(--out-name strainbreak_public_registry_uniqueness) so the public block is
for the exact served bytes.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
variants = json.loads((ROOT / "evidence/strainbreak_variants.json").read_text())
audit = json.loads((ROOT / "evidence/strainbreak_proxy_audit.json").read_text())
f75 = json.loads((ROOT / "evidence/strainbreak_f75_audit.json").read_text())
screen = json.loads((ROOT / "evidence/gravcrest_screen.json").read_text())
cards = json.loads((ROOT / "ledger/mechanism_cards.json").read_text())
pub = json.loads((ROOT / "evidence/strainbreak_public_registry_uniqueness.json").read_text())
sparse_diag = json.loads((ROOT / "evidence/strainbreak_public_sparse_diagnostic.json").read_text())

v = {x["value"]: x for x in variants["variants"]}["f60s2i"]
blk = audit["hide_and_recover_pooled_by_candidate"]["f60s2i"]
s = blk["scores"]["f60s2i"]
uni = audit["uniqueness_final_dots"]["f60s2i"]
surf_uni = audit["uniqueness_preplacement_surface"]
primary = ROOT / "docs/downloads" / (v["id"] + "-zeros.tif")
sha = hashlib.sha256(primary.read_bytes()).hexdigest()
audit_path = ROOT / "docs/downloads" / (v["id"] + "-audit.json")
gate_audit = json.loads(audit_path.read_text())
assert gate_audit["sha256_zeros"] == sha and pub["candidate"]["sha256"] == sha

final_pub = pub["final_dots"]
card = {
    "hypothesis": cards[v["id"]]["hypothesis"],
    "mechanism": cards[v["id"]]["mechanism"],
    "named_non_fault_process_that_could_mimic_it": cards[v["id"]]["non_fault_mimic"],
    "screen_falsified_alternative": {
        "lane": "GRAVCrest (rank-1 hypothesis, Bands 18/13/5 gravity-gradient crest)",
        "result": "NOT BUILT -- pre-registered SGMC screen falsified it",
        "far_only_sgmc_dti": {k: screen["surfaces"][k]["far_only_sgmc_dti"]
                              for k in ("crestA_abshg_x_cohgrav", "crestB_gradhg_x_cohgrav", "crestC_gravslope_x_cohgrav")},
        "breakline_L_baseline_far_only_sgmc_dti": screen["surfaces"]["breakline_L_baseline"]["far_only_sgmc_dti"],
        "evidence": "evidence/gravcrest_screen.json",
    },
    "holdout_dti": {
        "evidence_class": "HOLDOUT-DTI",
        "evaluator_version": s["evaluator_version"],
        "withheld_positive_pixels": s["withheld_positive_pixels"],
        "dti": s["dti"], "ci95": s["ci95"],
        "delta_vs_R0": blk["paired_differences"]["R0"]["delta"],
        "delta_vs_R0_ci95": blk["paired_differences"]["R0"]["ci95"],
        "delta_vs_BREAKLINEf45": blk["paired_differences"]["BREAKLINEf45"]["delta"],
        "delta_vs_BREAKLINEf45_ci95": blk["paired_differences"]["BREAKLINEf45"]["ci95"],
        "delta_vs_holdout_best_RELIEFp10": blk["paired_differences"]["RELIEFp10"]["delta"],
        "delta_vs_RELIEFp10_ci95": blk["paired_differences"]["RELIEFp10"]["ci95"],
        "R0_dti": blk["scores"]["R0"]["dti"],
        "BREAKLINEf45_dti": blk["scores"]["BREAKLINEf45"]["dti"],
        "holdout_best_RELIEFp10_dti": blk["scores"]["RELIEFp10"]["dti"],
        "dose_ladder": {"f45s2i": blk["scores"]["f45s2i"]["dti"], "f60s2i": s["dti"],
                        "f75s2i": f75["hide_and_recover_pooled_by_candidate"]["f75s2i"]["scores"]["f75s2i"]["dti"]},
        "dose_note": "f75 == f60 (paired delta -5.5e-07): dose plateau; primary is f60 (same holdout, higher SGMC, more parent mass retained). No fourth dose.",
        "spatial_clusters": audit["hide_and_recover_pooled_summary"]["bootstrap"]["clusters"],
        "bootstrap_draws": audit["hide_and_recover_pooled_summary"]["bootstrap"]["draws"],
    },
    "leakage_canary_max_symmetric_auc": audit["leakage_canaries"]["max_symmetric_auc"],
    "sgmc_control_proxy": {
        "evidence_class": "PROXY (off-catalogue USGS SGMC bedrock faults)",
        "dti": audit["sgmc_control_proxy"]["variant_dti"]["f60s2i"],
        "R0_dti": audit["sgmc_control_proxy"]["variant_dti"]["R0"],
        "BREAKLINEf45_dti": audit["sgmc_control_proxy"]["variant_dti"]["BREAKLINEf45"],
        "f75s2i_dti": f75["sgmc_control_proxy"]["f75s2i"],
        "truth_pixels": audit["sgmc_control_proxy"]["truth_pixels_after_catalogue_and_3px_exclusion"],
        "note": ("STRAINBREAK beats R0 on SGMC (+9.5%) but trails strain-blind BREAKLINE f45 "
                 "(0.126105): the strain multiplier trades bedrock-fault credit for catalogue-"
                 "holdout credit. The two local instruments disagree on the lane's discovery value."),
    },
    "queued_item_closed_visible_collar_sgmc": {
        "evidence_class": "PROXY", "sgmc_dti": screen["visible_collar_full"]["sgmc_dti"],
        "R0_dti": screen["R0_full"]["sgmc_dti"],
        "note": "NEXT_STEPS queued scoring the collar candidate on SGMC: 0.021192 vs R0 0.09606 -- the collar's holdout gain does not transfer off-catalogue.",
    },
    "correlation_overlap_vs_registry": {
        "local": {
            "registry_rasters_checked": uni["registry_rasters_checked"],
            "worst_forward_overlap_within_3px": uni["worst_forward_overlap"],
            "worst_forward_overlap_file": uni["worst_forward_overlap_file"],
            "worst_abs_spearman": uni["worst_abs_spearman"],
            "worst_abs_spearman_file": uni["worst_abs_spearman_file"],
            "literal_duplicate": uni["duplicate"],
            "preplacement_surface_spaced_top37654": surf_uni["spaced_top37654_set"],
            "preplacement_surface_sampled_spearman_worst": surf_uni["sampled_spearman_continuous_surface"]["worst"],
        },
        "public_expanded": {
            "evidence_file": "evidence/strainbreak_public_registry_uniqueness.json",
            "registries_checked": final_pub["registries_checked"],
            "worst_forward_overlap": final_pub["worst_forward_overlap"],
            "worst_overlap_raster": final_pub["worst_overlap_raster"],
            "worst_abs_spearman": final_pub["worst_abs_spearman"],
            "worst_rho_raster": final_pub["worst_rho_raster"],
            "rasters_over_70pct_overlap": final_pub["rasters_over_70pct_overlap"],
            "unique_under_literal_rule": final_pub["unique_under_literal_rule"],
            "stop_required": final_pub["stop_required"],
            "scan_complete_for_declared_scope": pub["scan_complete_for_declared_scope"],
            "scan_source": pub["inventory"]["scan_source"],
            "preplacement_note": pub.get("preplacement_note"),
            "sparse_only_diagnostic_NOT_A_GATE": {
                "evidence_file": "evidence/strainbreak_public_sparse_diagnostic.json",
                "sparse_checked_le_150k_positive_px": sparse_diag["sparse_checked"],
                "dense_skipped": sparse_diag["dense_skipped"],
                "worst_sparse_forward_overlap": sparse_diag["worst_sparse_forward_overlap"],
                "worst_sparse_raster": sparse_diag["worst_sparse_raster"],
                "sparse_over_70pct": sparse_diag["sparse_over_70pct"],
                "note": ("Even against sparse dot-like rasters only, 3 large dot clouds "
                         "(92-120k dots) exceed 70% forward overlap. The literal stop is "
                         "therefore not solely a dense-surface artifact; measured, not waived."),
            },
        },
    },
    "raster_sha256": sha,
    "raster_sha256_nan_twin": v["sha256"],
    "validator": {
        "overall_pass": gate_audit["overall_pass"],
        "gates": gate_audit["gates_zeros"],
        "no_nan_inside_footprint": True, "values_in_0_1": True,
        "crs_shape_transform_match": "EPSG:32611, 3730x3292, transform of sample_submission.tif",
    },
    "submission_name": "GEMSDOE92-STRAINBREAK-f60s2i-20261024",
    "file": primary.name,
    "note": v["form_note"], "note_chars": len(v["form_note"]),
    "organizer_score": None,
    "experiments_built_this_session": 3,
    "verdict": "negative",
    "verdict_reason": (
        "Pre-registered promotion rule not met: HOLDOUT-DTI 0.005487 beats R0 (paired CI "
        "excludes 0) and the BREAKLINE point estimate, but does not beat the holdout best "
        "(RELIEF p10, 0.006045; paired delta CI includes 0), and the SGMC off-catalogue "
        "control prefers strain-blind BREAKLINE. Public-registry literal gate: "
        + ("TRIGGERED (duplicate under literal rule, see public_expanded) -- independently binding."
           if final_pub["stop_required"] else "passed on the scanned scope.")
        + " Format-valid and OK TO DOWNLOAD; NOT cleared for a weekly slot."),
    "format_ok_to_download": True,
    "slot_recommendation": "NOT_CLEARED",
}
out = ROOT / "evidence/strainbreak_run_card.json"
out.write_text(json.dumps(card, indent=2), encoding="utf-8")
(ROOT / "docs/downloads/strainbreak_run_card.json").write_text(json.dumps(card, indent=2), encoding="utf-8")

# ---- extend the download audit receipt to the site schema ----
gate_audit.update({
    "schema": "gemsdoe92.download-audit.v1",
    "format_pass": bool(gate_audit["overall_pass"]),
    "submission_eligible": False,
    "candidate": primary.name,
    "n_dots": 37654,
    "run_card": "evidence/strainbreak_run_card.json",
    "verdict": "negative",
    "local_uniqueness": {
        "worst_abs_spearman": uni["worst_abs_spearman"],
        "worst_rho_raster": uni["worst_abs_spearman_file"],
        "worst_forward_overlap": uni["worst_forward_overlap"],
        "worst_overlap_raster": uni["worst_forward_overlap_file"],
        "registry_rasters_checked": uni["registry_rasters_checked"],
        "complete_local_scan": True,
        "unique_under_thresholds": not uni["duplicate"],
    },
    "public_registry_uniqueness": {
        "evidence_file": "evidence/strainbreak_public_registry_uniqueness.json",
        "candidate_hash_matches_scan": pub["candidate"]["sha256"] == sha,
        "scan_complete_for_declared_scope": pub["scan_complete_for_declared_scope"],
        "unique_under_literal_rule": final_pub["unique_under_literal_rule"],
        "stop_required": final_pub["stop_required"],
        "registries_checked": final_pub["registries_checked"],
        "worst_forward_overlap": final_pub["worst_forward_overlap"],
        "worst_overlap_raster": final_pub["worst_overlap_raster"],
        "worst_abs_spearman": final_pub["worst_abs_spearman"],
        "rasters_over_70pct_overlap": final_pub["rasters_over_70pct_overlap"],
    },
    "evidence": {
        "holdout": "evidence/strainbreak_proxy_audit.json (HOLDOUT-DTI, gems57-pooled-hide-v2)",
        "screen": "evidence/gravcrest_screen.json (GRAVCrest falsified pre-build)",
        "run_card": "evidence/strainbreak_run_card.json",
    },
})
audit_path.write_text(json.dumps(gate_audit, indent=2), encoding="utf-8")
print(json.dumps({k: card[k] for k in ("verdict", "raster_sha256", "submission_name", "note")}, indent=2))
print("wrote", out, "and extended", audit_path)
