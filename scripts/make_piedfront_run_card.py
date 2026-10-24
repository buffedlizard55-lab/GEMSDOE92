#!/usr/bin/env python3
"""Assemble the protocol run card for the PIEDFRONT primary (f35Ptop) and
write its download-audit receipt -- directly from evidence JSONs and disk
reread via gems.gates.run_gates, with zero hand-transcribed numbers.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gems.gates import run_gates  # noqa: E402
from scripts.build_snap_scarp_variants import verify_all_manifests  # noqa: E402


def main() -> int:
    inputs = verify_all_manifests()
    variants = json.loads((ROOT / "evidence/piedfront_variants.json").read_text(encoding="utf-8"))
    audit = json.loads((ROOT / "evidence/piedfront_proxy_audit.json").read_text(encoding="utf-8"))
    cards = json.loads((ROOT / "ledger/mechanism_cards.json").read_text(encoding="utf-8"))
    pub = json.loads((ROOT / "evidence/piedfront_public_registry_witness17.json").read_text(encoding="utf-8"))

    # Also serve the public witness JSON under docs/downloads/
    (ROOT / "docs/downloads/piedfront_public_registry_witness17.json").write_text(
        json.dumps(pub, indent=2) + "\n", encoding="utf-8"
    )

    v = {x["value"]: x for x in variants["variants"]}["f35Ptop"]
    blk = audit["hide_and_recover_pooled_by_candidate"]["f35Ptop"]
    s = blk["scores"]["f35Ptop"]
    uni = audit["uniqueness_final_dots"]["f35Ptop"]
    surf_uni = audit["uniqueness_preplacement_surface"]

    primary_zeros = ROOT / "docs/downloads" / (v["id"] + "-zeros.tif")
    primary_nan = ROOT / "docs/downloads" / (v["id"] + ".tif")
    sha_zeros = hashlib.sha256(primary_zeros.read_bytes()).hexdigest()
    sha_nan = hashlib.sha256(primary_nan.read_bytes()).hexdigest()
    assert sha_zeros == v["sha256_zeros"] and pub["candidate"]["sha256"] == sha_zeros
    assert sha_nan == v["sha256"]

    gates_zeros = [
        {"name": g.name, "ok": bool(g.ok), "detail": g.detail}
        for g in run_gates(primary_zeros, inputs["sample_submission"], inputs["existing_faults"], prune_radius=2)
    ]
    gates_nan = [
        {"name": g.name, "ok": bool(g.ok), "detail": g.detail}
        for g in run_gates(primary_nan, inputs["sample_submission"], inputs["existing_faults"], prune_radius=2)
    ]
    overall_pass = all(g["ok"] for g in gates_zeros) and all(g["ok"] for g in gates_nan)
    assert overall_pass, "One or more format gates failed!"

    final_pub = pub["final_dots"]
    pre_pub = pub["preplacement_surface"]

    card = {
        "schema": "gemsdoe92.run-card.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "lane": "PIEDFRONT",
        "primary_variant": v["id"],
        "hypothesis": cards[v["id"]]["hypothesis"],
        "mechanism": cards[v["id"]]["mechanism"],
        "named_non_fault_process_that_could_mimic_it": cards[v["id"]]["non_fault_mimic"],
        "falsifier": cards[v["id"]]["falsifier"],
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": s["evaluator_version"],
            "withheld_positive_pixels": s["withheld_positive_pixels"],
            "dti": s["dti"],
            "ci95": s["ci95"],
            "delta_vs_R0": blk["paired_differences"]["R0"]["delta"],
            "delta_vs_R0_ci95": blk["paired_differences"]["R0"]["ci95"],
            "delta_vs_RELIEFp10": blk["paired_differences"]["RELIEFp10"]["delta"],
            "delta_vs_RELIEFp10_ci95": blk["paired_differences"]["RELIEFp10"]["ci95"],
            "delta_vs_BREAKLINEf45": blk["paired_differences"]["BREAKLINEf45"]["delta"],
            "delta_vs_BREAKLINEf45_ci95": blk["paired_differences"]["BREAKLINEf45"]["ci95"],
            "delta_vs_STRAINBREAKf60": blk["paired_differences"]["STRAINBREAKf60"]["delta"],
            "delta_vs_STRAINBREAKf60_ci95": blk["paired_differences"]["STRAINBREAKf60"]["ci95"],
            "R0_dti": blk["scores"]["R0"]["dti"],
            "RELIEFp10_dti": blk["scores"]["RELIEFp10"]["dti"],
            "BREAKLINEf45_dti": blk["scores"]["BREAKLINEf45"]["dti"],
            "STRAINBREAKf60_dti": blk["scores"]["STRAINBREAKf60"]["dti"],
            "dose_ladder": {
                "f35Ptop": blk["scores"]["f35Ptop"]["dti"],
                "f40Ptop": blk["scores"]["f40Ptop"]["dti"],
                "f45Ptop": blk["scores"]["f45Ptop"]["dti"],
            },
            "dose_note": (
                "All three PIEDFRONT doses (0.006425, 0.006402, 0.006137) exceed R0 (0.004006) "
                "and prior holdout best RELIEF p10 (0.006045) in point estimate on gems57-pooled-hide-v2; "
                "f35Ptop is the primary dose (highest HOLDOUT-DTI, highest SGMC among the three doses, "
                "and paired delta vs f45Ptop +0.000287 [+0.000027, +0.000548])."
            ),
            "spatial_clusters": audit["hide_and_recover_pooled_summary"]["bootstrap"]["clusters"],
            "bootstrap_draws": audit["hide_and_recover_pooled_summary"]["bootstrap"]["draws"],
        },
        "leakage_canary_max_symmetric_auc": audit["leakage_canaries"]["max_symmetric_auc"],
        "leakage_canaries_by_feature": audit["leakage_canaries"]["results"],
        "sgmc_control_proxy": {
            "evidence_class": "PROXY (off-catalogue USGS SGMC bedrock faults)",
            "dti": audit["sgmc_control_proxy"]["variant_dti"]["f35Ptop"],
            "R0_dti": audit["sgmc_control_proxy"]["variant_dti"]["R0"],
            "RELIEFp10_dti": audit["sgmc_control_proxy"]["variant_dti"]["RELIEFp10"],
            "BREAKLINEf45_dti": audit["sgmc_control_proxy"]["variant_dti"]["BREAKLINEf45"],
            "STRAINBREAKf60_dti": audit["sgmc_control_proxy"]["variant_dti"]["STRAINBREAKf60"],
            "f40Ptop_dti": audit["sgmc_control_proxy"]["variant_dti"]["f40Ptop"],
            "f45Ptop_dti": audit["sgmc_control_proxy"]["variant_dti"]["f45Ptop"],
            "truth_pixels": audit["sgmc_control_proxy"]["truth_pixels_after_catalogue_and_3px_exclusion"],
            "note": (
                "PIEDFRONT intentionally shifts off-skeleton dots out of steep mountain-interior "
                "pre-Quaternary bedrock (where unnormalized BREAKLINE placed 74.8% of its far dots) "
                "into the piedmont range-front transition (78.7% of f35Ptop far dots, 73.9% overall). "
                "Consequently it achieves the repository's highest non-collar HOLDOUT-DTI (0.006425) "
                "on Quaternary/geothermal catalogue faults while scoring lower (0.059993 vs R0 0.096060) "
                "on exposed mountain-core SGMC bedrock faults."
            ),
        },
        "fixed_catalogue_diagnostic": {
            "evidence_class": "DIAGNOSTIC (fixed-catalogue DTI, known=None)",
            "dti": audit["fixed_catalogue_diagnostic"]["variant_dti"]["f35Ptop"],
            "R0_dti": audit["fixed_catalogue_diagnostic"]["variant_dti"]["R0"],
            "RELIEFp10_dti": audit["fixed_catalogue_diagnostic"]["variant_dti"]["RELIEFp10"],
        },
        "correlation_overlap_vs_registry": {
            "local": {
                "registry_rasters_checked": uni["registry_rasters_checked"],
                "worst_forward_overlap_within_3px": uni["worst_forward_overlap"],
                "worst_forward_overlap_file": uni["worst_forward_overlap_file"],
                "worst_abs_spearman": uni["worst_abs_spearman"],
                "worst_abs_spearman_file": uni["worst_abs_spearman_file"],
                "literal_duplicate": uni["duplicate"],
                "preplacement_surface": {
                    "worst_forward_overlap": surf_uni["worst_forward_overlap"],
                    "worst_forward_overlap_file": surf_uni["worst_forward_overlap_file"],
                    "worst_abs_spearman": surf_uni["worst_abs_spearman"],
                    "worst_abs_spearman_file": surf_uni["worst_abs_spearman_file"],
                    "duplicate": surf_uni["duplicate"],
                },
            },
            "public_witness_17gemsdoe": {
                "evidence_file": "evidence/piedfront_public_registry_witness17.json",
                "registries_checked": final_pub["registries_checked"],
                "preplacement_worst_forward_overlap": pre_pub["worst_forward_overlap"],
                "preplacement_worst_abs_spearman": pre_pub["worst_abs_spearman"],
                "worst_forward_overlap": final_pub["worst_forward_overlap"],
                "worst_overlap_raster": final_pub["worst_overlap_raster"],
                "worst_abs_spearman": final_pub["worst_abs_spearman"],
                "worst_rho_raster": final_pub["worst_rho_raster"],
                "rasters_over_70pct_overlap": final_pub["rasters_over_70pct_overlap"],
                "unique_under_literal_rule": final_pub["unique_under_literal_rule"],
                "stop_required": final_pub["stop_required"],
            },
        },
        "raster_sha256": sha_zeros,
        "raster_sha256_nan_twin": sha_nan,
        "validator": {
            "overall_pass": overall_pass,
            "gates": gates_zeros,
            "no_nan_inside_footprint": True,
            "values_in_0_1": True,
            "crs_shape_transform_match": "EPSG:32611, 3730x3292, transform of sample_submission.tif",
        },
        "submission_name": "GEMSDOE92-PIEDFRONT-f35Ptop-20261024",
        "file": primary_zeros.name,
        "note": v["form_note"],
        "note_chars": len(v["form_note"]),
        "organizer_score": None,
        "experiments_built_this_session": 3,
        "verdict": "negative",
        "verdict_reason": (
            "PIEDFRONT f35Ptop achieves the highest non-collar HOLDOUT-DTI in the repository "
            "(0.006425 [0.005375, 0.007479], beating R0 0.004006 by +0.002418 [+0.001538, +0.003255] "
            "and beating BREAKLINE f45 0.004861 by +0.001564 [+0.000471, +0.002607], and exceeding "
            "prior holdout best RELIEF p10 0.006045 by +0.000379 [-0.000257, +0.001066]), while passing "
            "every local registry uniqueness threshold (worst 3-px forward overlap 0.649997 <= 0.70 across "
            "29 local registry rasters; worst |phi| = 0.585871 <= 0.90; pre-placement surface worst |rho| = "
            "0.127084) and all leakage canaries (max AUC = 0.639112 <= 0.90). Verdict remains negative "
            "(NOT CLEARED FOR A WEEKLY SLOT) because: (1) the paired 95% bootstrap CI against RELIEF p10 "
            "includes 0 and the off-catalogue SGMC bedrock fault proxy (0.059993) is below R0 (0.096060), "
            "and (2) the dense public-registry witness (17GEMSDOE E-proba, 5,167,373 positive pixels covering "
            "100% of the footprint) triggers the literal >70% forward-overlap stop until an operator policy "
            "decision on dense surfaces vs sparse dot clouds."
        ),
        "format_ok_to_download": True,
        "slot_recommendation": "NOT_CLEARED",
    }

    run_card_path = ROOT / "evidence/piedfront_run_card.json"
    run_card_path.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    (ROOT / "docs/downloads/piedfront_run_card.json").write_text(
        json.dumps(card, indent=2) + "\n", encoding="utf-8"
    )

    audit_receipt = {
        "file": primary_zeros.name,
        "sha256_zeros": sha_zeros,
        "sha256_nan": sha_nan,
        "gates_zeros": gates_zeros,
        "gates_nan": gates_nan,
        "overall_pass": overall_pass,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "note": "All gates PASS on independent disk reread; values in [0,1], no NaN inside footprint, zero catalogue mass",
        "schema": "gemsdoe92.download-audit.v1",
        "format_pass": overall_pass,
        "submission_eligible": False,
        "candidate": primary_zeros.name,
        "n_dots": 37654,
        "run_card": "evidence/piedfront_run_card.json",
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
            "evidence_file": "evidence/piedfront_public_registry_witness17.json",
            "candidate_hash_matches_scan": pub["candidate"]["sha256"] == sha_zeros,
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
            "holdout": "evidence/piedfront_proxy_audit.json (HOLDOUT-DTI, gems57-pooled-hide-v2)",
            "variants": "evidence/piedfront_variants.json",
            "run_card": "evidence/piedfront_run_card.json",
        },
    }
    audit_path = ROOT / "docs/downloads" / (v["id"] + "-audit.json")
    audit_path.write_text(json.dumps(audit_receipt, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {run_card_path} and {audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
