#!/usr/bin/env python3
"""Fail-closed EULERFUSE closeout and final run-card builder.

Run only after screening, holdout evaluation, artifact packaging, and the public
registry audit.  This script consumes no organizer slot.  It verifies that all
source receipts describe the same exact bytes, records the public duplicate
stop in the artifact audit, and writes one canonical negative run card plus
byte-identical served mirrors.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "docs" / "downloads"
STEM = "gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros"
TIF = DOWNLOADS / f"{STEM}.tif"
ZIP = DOWNLOADS / f"{STEM}.zip"
AUDIT = DOWNLOADS / f"{STEM}-audit.json"
METADATA = DOWNLOADS / f"{STEM}.json"
SCREEN = ROOT / "evidence" / "eulerfuse_screen.json"
HOLDOUT = ROOT / "evidence" / "eulerfuse_holdout.json"
PUBLIC = ROOT / "evidence" / "eulerfuse_public_registry.json"
RUN_CARD = ROOT / "evidence" / "eulerfuse_run_card.json"
NAME = "GEMSDOE92-EULERFUSE-gravity-20261024"
NOTE = "EULERFUSE gravity: 37654 LOQO Euler-contact dots; HOLDOUT-DTI 0.110387; negative"


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    screen = read_json(SCREEN)
    holdout = read_json(HOLDOUT)
    public = read_json(PUBLIC)
    audit = read_json(AUDIT)
    metadata = read_json(METADATA)

    tif_sha, zip_sha = sha256(TIF), sha256(ZIP)
    require(len(NOTE) <= 140, "note exceeds 140 characters")
    require(holdout["best_arm"] == "gravity", "best arm changed after frozen evaluation")
    require(holdout["experiments_used"] == holdout["budget_limit"] == 3,
            "three-arm EULERFUSE budget is not closed")
    require(holdout["decision"]["promotion_gate_pass"] is False,
            "promotion state changed; do not use the negative closeout")
    require(holdout["decision"]["weekly_slot_used"] is False,
            "holdout receipt unexpectedly records a weekly slot")
    require(screen["leakage_canaries"]["all_pass"] is True,
            "leakage canary failed")
    require(public["candidate_file_sha256"] == tif_sha == audit["sha256"] == metadata["sha256"],
            "candidate hashes disagree across exact-file receipts")
    require(public["inventory"]["candidate_exact_sha256_matches"] == 0,
            "candidate is byte-identical to a public registry raster")
    require(public["preplacement_surface"]["stop_required"] is True,
            "expected literal pre-placement stop is absent")
    require(public["final_dots"]["stop_required"] is True,
            "expected literal final stop is absent")
    require(public["preplacement_surface"]["worst_forward_overlap"] > 0.70,
            "pre-placement overlap no longer exceeds the frozen threshold")
    require(public["final_dots"]["worst_forward_overlap"] > 0.70,
            "final overlap no longer exceeds the frozen threshold")
    require(audit["zip_sha256"] == zip_sha, "ZIP hash does not match artifact audit")
    require(audit["all_gates_pass"] is True, "local format gates did not all pass")
    require(audit["validator_output"]["all_checks_passed"] is True,
            "exact-file validator did not pass")
    require(audit["validator_output"]["checks"]["range_0_1_guaranteed"] is True,
            "exact-file range gate did not pass")
    require(audit["dot_count"] == public["candidate"]["dots"] == 37_654,
            "candidate dot count changed")

    strict = holdout["primary_drawblind_visible_mask"]["pooled_by_candidate"]["gravity"]
    gravity = strict["scores"]["gravity"]
    base = strict["scores"]["base_control"]
    paired = strict["paired_differences"]["base_control"]
    pre_local = screen["preplacement_local_registry"]["gravity"]
    final_local = holdout["final_local_registry"]["gravity"]
    witness = public["binding_witness"]["full_footprint_surface"]
    inventory = public["inventory"]

    audit.update({
        "status_text": (
            "OK TO DOWNLOAD FOR RESEARCH; DO NOT SUBMIT — HOLDOUT-DTI promotion "
            "gate failed and literal public registry overlap stop triggered."
        ),
        "public_registry_audit": "evidence/eulerfuse_public_registry.json",
        "public_surface_worst_forward_overlap_3px": public["preplacement_surface"]["worst_forward_overlap"],
        "public_final_worst_forward_overlap_3px": public["final_dots"]["worst_forward_overlap"],
        "public_duplicate_under_literal_rule": True,
    })
    AUDIT.write_text(json.dumps(audit, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    metadata.update({
        "approved_for_weekly_slot": False,
        "promoted": False,
        "submission_eligible": False,
        "status": (
            "OK TO DOWNLOAD FOR RESEARCH; DO NOT SUBMIT — HOLDOUT-DTI promotion "
            "gate failed and literal public registry overlap stop triggered."
        ),
        "public_registry_audit": "evidence/eulerfuse_public_registry.json",
    })
    METADATA.write_text(json.dumps(metadata, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    validator = audit["validator_output"]
    validator_summary = {
        "result": "PASS",
        "validation_class": "LOCAL FORMAT/RANGE VALIDATION; NOT ORGANIZER ACCEPTANCE",
        "single_band": validator["meta"]["count"] == 1,
        "dtype": validator["meta"]["dtype"],
        "crs": validator["meta"]["crs"],
        "shape": validator["meta"]["shape"],
        "transform": validator["meta"]["transform"],
        "crs_shape_transform_match": all(g["ok"] for g in audit["gates"][:3]),
        "no_nan_inside_footprint": validator["checks"]["in_footprint_all_finite"],
        "no_nan_anywhere": validator["checks"]["no_nan_anywhere"],
        "no_infinity_anywhere": validator["checks"]["no_inf_anywhere"],
        "values_in_0_1": validator["checks"]["range_0_1_guaranteed"],
        "min": validator["min"],
        "max": validator["max"],
        "zeros_outside_footprint": validator["checks"]["outside_footprint_zero"],
        "catalogue_mass": audit["catalogue_mass"],
        "min_catalogue_distance_px": audit["min_catalogue_distance_px"],
        "dot_count": audit["dot_count"],
        "must_gates_passed": sum(g["ok"] for g in audit["gates"]),
        "must_gates_failed": sum(not g["ok"] for g in audit["gates"]),
    }

    card = {
        "schema": "gemsdoe92.run-card.v1",
        "hypothesis": "Catalogue-missing, basin-covered normal-fault contacts can be recovered by stable structural-index N=0 Euler source locations that independently agree in reduced-to-pole magnetics and isostatic gravity and are consistent with depth to basement.",
        "mechanism": "EULERFUSE solves local moving-window N=0 Euler equations on catalogue-free RTP and gravity fields, rasterizes stable shallow inferred source subcrops, adds the gravity solution and basement-depth consistency to a four-quadrant leave-one-quadrant-out physical classifier, and emits 37,654 spaced 1-D crest dots beyond the 2-pixel mapped-catalogue collar.",
        "named_non_fault_process_that_could_mimic_it": "A volcanic dike, caldera ring fracture, pluton margin, or lithologic contact can produce a stable potential-field contact without young fault displacement.",
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": holdout["evaluator_version"],
            "withheld_positive_pixels": gravity["withheld_positive_pixels"],
            "alpha": strict["alpha"],
            "beta": strict["beta"],
            "triangular_kernel_m": strict["triangular_radius_m"],
            "arm": "gravity",
            "dti": gravity["dti"],
            "ci95": gravity["ci95"],
            "fresh_base_control_dti": base["dti"],
            "fresh_base_control_ci95": base["ci95"],
            "paired_delta_vs_fresh_base_control": paired["delta"],
            "paired_delta_ci95": paired["ci95"],
            "promotion_gate_pass": False,
            "organizer_confirmed": False,
        },
        "leakage_canary": {
            "evidence_class": "HOLDOUT-CANARY",
            "features_tested": len(screen["leakage_canaries"]["features"]),
            "threshold_symmetric_auc": screen["leakage_canaries"]["threshold_symmetric_auc"],
            "max_symmetric_auc": screen["leakage_canaries"]["max_symmetric_auc"],
            "max_feature": screen["leakage_canaries"]["max_symmetric_feature"],
            "all_pass": screen["leakage_canaries"]["all_pass"],
        },
        "correlation_overlap_vs_registry": {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "local_preplacement_rasters": pre_local["registry_rasters_checked"],
            "surface_worst_abs_spearman": pre_local["worst_abs_surface_spearman_250k"],
            "preplacement_preview_worst_forward_overlap_3px": pre_local["worst_preview_forward_overlap_3px"],
            "local_final_worst_abs_spearman": final_local["worst_abs_spearman_phi"],
            "local_final_worst_forward_overlap_3px": final_local["worst_forward_overlap_3px"],
            "public_repositories_scanned": inventory["matching_public_repositories"],
            "public_exact_grid_rasters_compared": inventory["one_band_exact_template_grid_rasters_compared"],
            "public_surface_worst_abs_spearman": public["preplacement_surface"]["worst_abs_spearman"],
            "public_final_worst_abs_spearman": public["final_dots"]["worst_abs_spearman"],
            "public_surface_worst_forward_overlap_3px": public["preplacement_surface"]["worst_forward_overlap"],
            "public_final_worst_forward_overlap_3px": public["final_dots"]["worst_forward_overlap"],
            "exact_sha256_matches": inventory["candidate_exact_sha256_matches"],
            "duplicate_under_literal_rule": True,
            "binding_witness": witness["raster"],
            "binding_witness_positive_footprint_pixels": witness["positive_pixels_in_footprint"],
            "scope_caveat": "Current public default branches and configured TIFF paths only; one invalid public TIFF made the accessible-scan completeness flag false. The dense witness alone is binding under the literal rule.",
        },
        "raster_sha256": tif_sha,
        "zip_sha256": zip_sha,
        "validator_output": validator,
        "validator_gates": audit["gates"],
        "validator_all_gates_pass": audit["all_gates_pass"],
        "validator_summary": validator_summary,
        "submission_name": NAME,
        "submission_note": NOTE,
        "submission_note_characters": len(NOTE),
        "primary_download": str(TIF.relative_to(ROOT)),
        "zip_download": str(ZIP.relative_to(ROOT)),
        "verdict": "negative",
        "submission_eligible": False,
        "weekly_slots_used": 0,
        "experiments_used": holdout["experiments_used"],
        "experiment_budget": holdout["budget_limit"],
        "verdict_detail": "Negative: the gravity arm is byte-unique and format-valid but does not beat the freshly reproduced holdout control, and both preplacement/final public scans exceed the literal 70% overlap stop because a registry probability surface is positive across the entire footprint. OK to download for research; DO NOT SUBMIT.",
    }
    text = json.dumps(card, indent=2, allow_nan=False) + "\n"
    RUN_CARD.write_text(text, encoding="utf-8")
    (DOWNLOADS / RUN_CARD.name).write_text(text, encoding="utf-8")
    (DOWNLOADS / PUBLIC.name).write_bytes(PUBLIC.read_bytes())
    print(json.dumps({
        "run_card": str(RUN_CARD.relative_to(ROOT)),
        "raster_sha256": tif_sha,
        "verdict": card["verdict"],
        "submission_eligible": card["submission_eligible"],
        "format_gates_pass": audit["all_gates_pass"],
        "public_literal_stop": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
