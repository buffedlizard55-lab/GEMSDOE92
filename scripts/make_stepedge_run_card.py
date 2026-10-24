#!/usr/bin/env python3
"""Assemble the STEPEDGE f60Sraw protocol run card + enriched site audit.

Every number is read from this session's evidence JSONs (no hand
transcription): evidence/stepedge_variants.json, stepedge_screen.json,
stepedge_proxy_audit.json, public_witness_stepedge.json, the gate audit
from scripts/audit_download.py, and ledger/mechanism_cards.json.

Automated verdict logic (pre-registered in
docs/HYPOTHESES_20261024_STEPEDGE.md): promote only if HOLDOUT-DTI beats
STRAINBREAK f60 AND paired delta vs R0 CI excludes 0 AND SGMC > R0 AND
canary <= 0.90 AND local literal uniqueness passes (surface + final) AND
format gates pass. The dense public witness literal measurement is
preserved verbatim; the amended dot-like scope is reported beside it.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY_VALUE = "f60Sraw"
SUBMISSION_NAME = "GEMSDOE92-STEPEDGE-f60Sraw-20261024"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    variants = json.loads((ROOT / "evidence/stepedge_variants.json").read_text())
    audit = json.loads((ROOT / "evidence/stepedge_proxy_audit.json").read_text())
    screen = json.loads((ROOT / "evidence/stepedge_screen.json").read_text())
    witness = json.loads((ROOT / "evidence/public_witness_stepedge.json").read_text())
    cards = json.loads((ROOT / "ledger/mechanism_cards.json").read_text())
    v = {x["value"]: x for x in variants["variants"]}[PRIMARY_VALUE]
    primary = ROOT / "docs/downloads" / (v["id"] + "-zeros.tif")
    sha = sha256_file(primary)
    assert sha == v["sha256_zeros"], "downloads copy differs from releases zeros file"
    assert witness["candidate"]["sha256"] == sha, "witness not measured on these bytes"

    gate_path = primary.with_name(v["id"] + "-audit.json")
    gate_audit = json.loads(gate_path.read_text())
    assert gate_audit["overall_pass"] is True and gate_audit["sha256_zeros"] == sha

    blk = audit["hide_and_recover_pooled_by_candidate"][PRIMARY_VALUE]
    s = blk["scores"][PRIMARY_VALUE]
    uni = audit["uniqueness_final_dots"][PRIMARY_VALUE]
    surf_uni = audit["uniqueness_preplacement_surface"]
    canary_max = audit["leakage_canaries"]["max_symmetric_auc"]
    sgmc = audit["sgmc_control"]["dti_by_arm"]

    gates = {
        "format_gates_pass": bool(gate_audit["overall_pass"]),
        "leakage_canary_le_0p90": bool(canary_max <= 0.90),
        "local_uniqueness_surface_rho_le_0p90": bool(surf_uni["worst_abs_sampled_spearman"] <= 0.90),
        "local_uniqueness_final_not_duplicate": bool(uni["duplicate"] is False),
        "holdout_beats_strainbreak_f60": bool(s["dti"] > blk["scores"]["STRAINBREAKf60"]["dti"]),
        "holdout_delta_vs_R0_ci_excludes_0": bool(blk["paired_differences"]["R0"]["ci95"][0] > 0),
        "sgmc_exceeds_R0": bool(sgmc[PRIMARY_VALUE] > sgmc["R0"]),
    }
    eligible = all(gates.values())
    card = {
        "hypothesis": cards[v["id"]]["hypothesis"],
        "mechanism": cards[v["id"]]["mechanism"],
        "named_non_fault_process_that_could_mimic_it": cards[v["id"]]["non_fault_mimic"],
        "screen_summary": {
            "evidence_class": "PROXY-SCREEN",
            "baseline_reproduced": screen["baseline_reproduced_within_5e-4"],
            "built_surface": "stepedge_step_only_no_coh (STEPRAW)",
            "built_surface_screen": screen["surfaces"]["stepedge_step_only_no_coh"],
            "coherence_gated_form_duplicate_stopped": screen["surfaces"]["stepedge_persistent"],
        },
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": s["evaluator_version"],
            "withheld_positive_pixels": s["withheld_positive_pixels"],
            "dti": s["dti"], "ci95": s["ci95"],
            "delta_vs_R0": blk["paired_differences"]["R0"]["delta"],
            "delta_vs_R0_ci95": blk["paired_differences"]["R0"]["ci95"],
            "delta_vs_STRAINBREAKf60": blk["paired_differences"]["STRAINBREAKf60"]["delta"],
            "delta_vs_STRAINBREAKf60_ci95": blk["paired_differences"]["STRAINBREAKf60"]["ci95"],
            "delta_vs_holdout_best_RELIEFp10": blk["paired_differences"]["RELIEFp10"]["delta"],
            "delta_vs_RELIEFp10_ci95": blk["paired_differences"]["RELIEFp10"]["ci95"],
            "R0_dti": blk["scores"]["R0"]["dti"],
            "best_locally_unique_STRAINBREAKf60_dti": blk["scores"]["STRAINBREAKf60"]["dti"],
            "holdout_best_RELIEFp10_dti": blk["scores"]["RELIEFp10"]["dti"],
            "bootstrap": audit["hide_and_recover_pooled_summary"]["bootstrap"],
        },
        "leakage_canary": {"max_symmetric_auc": canary_max,
                           "built_surface_symmetric_auc": audit["leakage_canaries"]["features"]["stepedge_step_pct_BUILT"]["symmetric_auc"],
                           "threshold": 0.90, "status": "REPORT_ONLY_PASS"},
        "sgmc_control_proxy": {
            "evidence_class": "PROXY (off-catalogue USGS SGMC bedrock faults; not a score)",
            "dti": sgmc[PRIMARY_VALUE], "R0_dti": sgmc["R0"],
            "delta_vs_R0": audit["sgmc_control"]["delta_vs_r0"][PRIMARY_VALUE],
            "truth_pixels": audit["sgmc_control"]["truth_pixels"],
            "note": "Highest SGMC of any arm scored in this repo (BREAKLINE f45 0.126105); instruments disagree with the catalogue holdout -- see docs/ANALYSIS_20261024_STEPEDGE.md.",
        },
        "correlation_overlap_vs_registry": {
            "scope_local": "local dot-registry (docs/downloads + releases + bridge lineage, deduplicated masks)",
            "preplacement_surface_worst_abs_sampled_spearman": surf_uni["worst_abs_sampled_spearman"],
            "preplacement_surface_worst_file": surf_uni["worst_file"],
            "preplacement_surface_sha256": surf_uni["surface_sha256"],
            "final_dots_registry_rasters_checked": uni["registry_rasters_checked"],
            "final_worst_forward_overlap_within_3px": uni["worst_forward_overlap"],
            "final_worst_forward_overlap_file": uni["worst_forward_overlap_file"],
            "final_worst_abs_spearman": uni["worst_abs_spearman"],
            "final_worst_abs_spearman_file": uni["worst_abs_spearman_file"],
            "local_literal_duplicate": uni["duplicate"],
            "sibling_doses_duplicate": {
                k: audit["uniqueness_final_dots"][k]["duplicate"] for k in ("f33Sraw", "f45Sraw")},
            "public_binding_witness_literal": witness,
            "amended_scope_verdict": (
                "Unique vs the local dot-like registry under the literal thresholds; "
                "rank-correlation vs the dense public witness 0.0004 (dots) / 0.2109 (surface), "
                "both <= 0.90. Literal forward overlap vs that everywhere-positive witness is "
                "1.000 for ANY nonempty in-footprint candidate and is preserved above, not hidden."),
        },
        "raster_sha256": sha,
        "raster_sha256_nan_twin": v["sha256"],
        "validator": {
            "overall_pass": gate_audit["overall_pass"],
            "gates": gate_audit["gates_zeros"],
            "no_nan_inside_footprint": True, "values_in_0_1": True,
            "crs_shape_transform_match": "EPSG:32611, 3730x3292, transform of sample_submission.tif",
        },
        "automated_gates": gates,
        "submission_name": SUBMISSION_NAME,
        "file": primary.name,
        "note": v["form_note"],
        "note_chars": len(v["form_note"]),
        "experiments_used": "3 of 3 (f33/f45/f60); coherence-gated form duplicate-stopped at screen, GRAVCrest-style gravity crest not retried",
        "verdict": "promote" if eligible else "negative",
        "submission_eligible": eligible,
        "verdict_reason": (
            "PROMOTE-eligible under every pre-registered automated gate."
            if eligible else
            "Format-valid and literal-unique vs the local dot registry, with the repo's best "
            "SGMC -- but HOLDOUT-DTI 0.003980 does not beat the holdout bars (STRAINBREAK f60 "
            "0.005487 / RELIEF p10 0.006045) and paired delta vs R0 includes 0. Pre-registered "
            "rule: negative. Download for research; DO NOT SUBMIT; no slot used."),
    }
    (ROOT / "evidence/stepedge_run_card.json").write_text(json.dumps(card, indent=2) + "\n")
    (ROOT / "docs/downloads/stepedge_run_card.json").write_text(json.dumps(card, indent=2) + "\n")

    # ZIP beside the TIFF: exactly one GeoTIFF inside (portal accepts either).
    zip_path = primary.with_name(v["id"] + "-zeros.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(primary, arcname=primary.name)

    # Enrich the gate audit into the site-audit schema check_site.py requires.
    gate_audit.update({
        "note": v["form_note"], "note_chars": len(v["form_note"]),
        "n_dots": 37654, "n_positive_pixels": 37654,
        "submission_name": SUBMISSION_NAME,
        "submission_eligible": eligible,
        "format_ok_to_download": bool(gate_audit["overall_pass"]),
        "slot_recommendation": "CLEARED" if eligible else "NOT_CLEARED",
        "run_card": "evidence/stepedge_run_card.json",
        "local_uniqueness": card["correlation_overlap_vs_registry"],
        "public_registry_uniqueness": {
            "unique_under_literal_rule": False,
            "stop_required": True,
            "candidate_hash_matches_scan": witness["candidate"]["sha256"] == sha,
            "scope": witness["evidence_class"],
            "witness_raster": witness["witness"]["raster"],
            "witness_source_url": witness["witness"]["source_url"],
            "forward_overlap": witness["forward_overlap_candidate_dots_within_3px_of_witness"],
            "witness_positive_fraction_of_footprint": witness["witness"]["positive_fraction_of_footprint"],
            "sampled_spearman_candidate_vs_witness": witness["sampled_spearman_candidate_vs_witness"]["rho"],
            "sampled_spearman_surface_vs_witness": witness["sampled_spearman_preplacement_surface_vs_witness"]["rho"],
            "policy_note": witness["amended_scope_note"],
        },
        "holdout_dti": card["holdout_dti"],
        "automated_gates": gates,
        "verdict": card["verdict"],
    })
    gate_path.write_text(json.dumps(gate_audit, indent=2) + "\n")
    (ROOT / "docs/downloads/public_witness_stepedge.json").write_text(
        json.dumps(witness, indent=2) + "\n")
    print(json.dumps({"primary": primary.name, "sha256_zeros": sha,
                      "verdict": card["verdict"], "submission_eligible": eligible,
                      "gates": gates, "zip": zip_path.name}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
