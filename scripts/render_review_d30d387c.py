#!/usr/bin/env python3
"""Publish the 2026-10-27 d30d387c negative review run card, bound fail-closed to receipts.

Binds:
  1. evidence/review_d30d387c_preflight.json (pinned 17GEMSDOE continuous witness + VARIO format recheck)
  2. evidence/input_cache_d30d387c.json + docs/downloads/input_cache_d30d387c.json (12/12 SHA-256 pins + finite -3.4028235e+38 sentinel & Band 6 tc diagnostics)
  3. evidence/fleet_20261027_audit_d30d387c.json + docs/downloads/fleet_20261027_audit_d30d387c.json (dual continuous + 13GEMSDOE binary-lattice pre-placement witnesses, 11 Oct 25-27 prompt delta artifacts, 12 multi-owner repos)
  4. docs/downloads/focus9_pairwise_recheck_14f85876.json (36 row-safe Focus-9 pairwise checks)
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "evidence/review_d30d387c_preflight.json"
INPUT = ROOT / "evidence/input_cache_d30d387c.json"
PUBLIC_INPUT = ROOT / "docs/downloads/input_cache_d30d387c.json"
FLEET = ROOT / "evidence/fleet_20261027_audit_d30d387c.json"
PUBLIC_FLEET = ROOT / "docs/downloads/fleet_20261027_audit_d30d387c.json"
PAIRWISE = ROOT / "docs/downloads/focus9_pairwise_recheck_14f85876.json"
HYPOTHESES = ROOT / "docs/HYPOTHESES_20261027_D30D387C.md"
REVIEW_MD = ROOT / "docs/REVIEW_20261027_D30D387C.md"
OUTPUT = ROOT / "docs/downloads/review_d30d387c_run_card.json"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def build() -> dict:
    proof_raw = PREFLIGHT.read_bytes()
    inputs_raw = INPUT.read_bytes()
    fleet_raw = FLEET.read_bytes()
    pair_raw = PAIRWISE.read_bytes()

    preflight = json.loads(proof_raw)
    inputs = json.loads(inputs_raw)
    fleet = json.loads(fleet_raw)
    pairs = json.loads(pair_raw)

    overlap = preflight["correlation_overlap_vs_registry"]
    proof = overlap["preplacement_proof"]
    if (
        preflight["verdict"] != "negative"
        or preflight["submission_eligible"] is not False
        or preflight["holdout_dti"]["value"] is not None
        or proof["verdict"] != "negative"
        or proof["submission_eligible"] is not False
        or proof["grid_checks_pass"] is not True
        or proof["universal_nonempty_in_footprint_overlap_stop"] is not True
        or proof["positive_in_footprint"] != proof["footprint_pixels"]
        or proof["forward_overlap_for_any_nonempty_in_footprint_dot_set"] != 1.0
        or proof["threshold"] != 0.70
    ):
        raise ValueError("preflight receipt is not a valid rejection-only proof")
    if proof["implementation_sha256"] != digest((ROOT / "scripts/preflight_dense_witness.py").read_bytes()):
        raise ValueError("preflight implementation differs from receipt")
    if preflight["audit_implementation_sha256"] != digest((ROOT / "scripts/audit_readiness.py").read_bytes()):
        raise ValueError("readiness implementation differs from receipt")

    files = inputs["files"]
    meta = inputs["raster_metadata"]
    if (
        inputs["manifest_sha256"] != digest((ROOT / "registry/session_manifest.json").read_bytes())
        or inputs["files_expected"] != 12
        or inputs["files_verified"] != 12
        or len(files) != 12
        or any(r["verified"] is not True or r["observed_sha256"] != r["expected_sha256"] for r in files)
        or inputs["all_pins_verified"] is not True
        or inputs["all_local_checks_passed"] is not True
        or inputs["official_origin_authenticated"] is not False
        or inputs["redistribution_rights_verified"] is not False
        or inputs["submission_eligible"] is not False
        or inputs["holdout_run"] is not False
        or meta["checked"] is not True
        or meta["grid_matches_sample"] is not True
        or meta["expected_band_tags_match"] is not True
        or meta["feature_band_count"] != 19
        or meta["problems"]
        or len(meta.get("feature_band_nodata_audit", [])) != 19
        or meta.get("any_finite_sentinel_in_footprint") is not True
    ):
        raise ValueError("input-cache receipt is incomplete or overclaims provenance")

    dual = fleet["dual_witness_preplacement_certificate"]
    witnesses = {w["id"]: w for w in dual["witnesses"]}
    w_cont = witnesses["dense_continuous_17gemsdoe"]
    w_bin = witnesses["binary_lattice_13gemsdoe"]
    if (
        w_cont["positive_in_footprint"] != 5_167_373
        or w_cont["pigeonhole_min_overlap_at_37654_dots"] != 1.0
        or w_bin["positive_in_footprint"] != 206_895
        or w_bin["halo_3px_in_footprint"] != 5_160_724
        or w_bin["pigeonhole_min_overlap_at_37654_dots"] <= 0.70
        or len(fleet["prompt_20261027_delta_artifacts"]) != 11
        or len(fleet["multi_owner_repositories_20261027"]) != 12
        or fleet["submission_eligible"] is not False
        or fleet["new_unique_tiff_generated"] is not False
        or fleet["weekly_slots_used"] != 0
    ):
        raise ValueError("fleet 2026-10-27 audit receipt failed invariants")

    if (
        pairs["pairs"] != 36
        or pairs["source_blob_and_sha256_verified"] is not True
        or pairs["all_pairs_duplicate_in_at_least_one_direction_or_rho"] is not True
    ):
        raise ValueError("nine-site pairwise receipt failed invariants")

    primary = ROOT / preflight["primary_download"]
    if digest(primary.read_bytes()) != preflight["raster_sha256"]:
        raise ValueError("historical primary research raster SHA-256 mismatch")
    if preflight["format_pass"] is not True or any(x["ok"] is not True for x in preflight["validator_output"]):
        raise ValueError("historical primary research format checks failed")

    holdout_raw = (ROOT / "evidence/vario_holdout.json").read_bytes()
    holdout = json.loads(holdout_raw)
    historical = holdout["scores"]["vario_full"]
    delta = holdout["paired_by_candidate"]["vario_full"]["control_FAULTNET_far"]

    if not HYPOTHESES.is_file():
        raise ValueError("pre-registered hypotheses document missing")

    return {
        "schema": "gemsdoe92-review-d30d387c-v1",
        "branch": "arena/d30d387c-gemsdoe92",
        "reviewed_utc": fleet["reviewed_utc"],
        "hypothesis": "GALLARDO-MEJU-CROSSGRAD-DECOUPLING (Rank 1 of 5 pre-registered untried hypotheses; no lane assigned in [PASTE ONE PARAGRAPH] and halted prior to surface generation/placement under Protocol Rule 1)",
        "mechanism": "Hydrothermal magnetite destruction along oblique dilatant geothermal fault step-overs rotates the reduced-to-pole magnetic gradient away from the footwall isostatic-gravity density gradient (|grad(g_iso) x grad(m_RTP)| > 0 at joint gradient crests), unlike intact lithologic contacts where grad(g_iso) || +-grad(m_RTP).",
        "named_non_fault_mimic": "Reversely magnetized Cenozoic basalt sheets or oblique mafic dikes crossing alluvial basin margins (falsified by Konigsberger TMI/RTP sheet remanence ratio and 1-D ridge continuity).",
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "value": None,
            "ci95": None,
            "evaluator_version": None,
            "withheld_positives": None,
            "reason": "Not run on a new candidate: dual hash-verified public registry witnesses (17GEMSDOE continuous surface AND 13GEMSDOE pure {0,1} binary dot submission) force literal 3-px overlap > 0.70 before surface creation or placement.",
        },
        "leakage_canaries": {
            "status": "not_run",
            "reason": "No new experimental features were constructed after pre-placement STOP.",
        },
        "correlation_overlap_vs_registry": {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "scope": "Dual freshly fetched and Git-blob/SHA-256-verified public witnesses (both continuous float surface and pure {0,1} binary-dot submission) plus 11 Oct 25-27 prompt delta artifacts and 12 multi-owner repositories.",
            "overlap_threshold": 0.70,
            "rank_correlation_threshold": 0.90,
            "forward_overlap_vs_17gemsdoe_continuous_witness": 1.0,
            "pigeonhole_min_overlap_at_37654_dots_vs_13gemsdoe_binary_witness": w_bin["pigeonhole_min_overlap_at_37654_dots"],
            "observed_overlap_range_across_11_oct25_27_delta_artifacts_vs_13gemsdoe": [
                min(r["ov3_vs_13gemsdoe_r13_lattice"] for r in fleet["prompt_20261027_delta_artifacts"]),
                max(r["ov3_vs_13gemsdoe_r13_lattice"] for r in fleet["prompt_20261027_delta_artifacts"]),
            ],
            "rank_correlation": None,
            "rank_correlation_reason": "No new candidate surface or final dots were generated; dual overlap proofs reject prior to placement.",
            "preplacement_proof": proof,
            "dual_witness_certificate_sha256": digest(fleet_raw),
            "surface_check": "rejected_by_dual_witnesses_before_surface_creation",
            "final_dots_check": "not_run_no_new_raster",
        },
        "new_unique_tiff_generated": False,
        "raster_sha256": None,
        "validator_output": {
            "new_candidate": {
                "status": "not_run_no_new_raster",
                "checks": None,
            },
            "all_11_oct25_27_prompt_delta_rasters_strict_format_gates_pass": all(
                r["strict_submission_encoding_gates_pass"] for r in fleet["prompt_20261027_delta_artifacts"]
            ),
            "portal_acceptance": "not tested; local zero-outside-footprint [0, 1] check is not proof of DrivenData portal acceptance",
        },
        "submission_name": None,
        "submission_note": None,
        "verdict": "negative",
        "submission_eligible": False,
        "experiments": 0,
        "weekly_slots_used": 0,
        "organizer_confirmed_score": None,
        "score_estimate": None,
        "score_estimate_reason": "No organizer score-to-file receipts exist, and owner-CLAIM regressions do not yield calibrated per-file prediction intervals (notably GEMSDOE28 s21-puhgb has static HOLDOUT-DTI 0.034629 yet owner CLAIM 0.0206, vs GEMSDOE27 h31-drcg static HOLDOUT-DTI 0.014529 and owner CLAIM 0.2250).",
        "historical_research_reference": {
            "file": preflight["primary_download"],
            "sha256": preflight["raster_sha256"],
            "status": "research only; DO NOT SUBMIT",
            "format_pass": True,
            "format_gates": preflight["validator_output"],
            "name_for_this_old_file_only": preflight["submission_name"],
            "note_for_this_old_file_only": preflight["note"],
            "prior_holdout_dti": {
                "evidence_class": historical["evidence_class"],
                "evaluator_version": historical["evaluator_version"],
                "withheld_positives": historical["withheld_positive_pixels"],
                "value": historical["dti"],
                "ci95": historical["ci95"],
                "paired_difference_vs_control_FAULTNET_far": delta["delta"],
                "paired_difference_ci95": delta["ci95"],
                "source": "evidence/vario_holdout.json",
                "source_sha256": digest(holdout_raw),
                "status": "historical, not rerun here; not an organizer score",
            },
        },
        "data_integrity_and_code_fixes_d30d387c": {
            "input_cache_public_receipt": "docs/downloads/input_cache_d30d387c.json",
            "input_cache_receipt_sha256": digest(inputs_raw),
            "verified_core_pins": 12,
            "verified_external_pins": 7,
            "interior_finite_nodata_sentinel_pixels_bands_1_5_7_19": 3061,
            "interior_finite_nodata_sentinel_pixels_band_6_tc": 3073,
            "band6_tc_pearson_r_vs_geodawn_radiometric_total_count": 0.99714,
            "band6_tc_pearson_r_vs_true_magnetic_tilt_atan2_b9_b3": 0.012796,
            "irregularities_logged": [
                "IR-92-SALEMSEISMO-BAND6-RADIOMETRIC-TC-MISIDENTIFICATION",
                "IR-92-FINITE-NODATA-SENTINEL-IN-FOOTPRINT",
                "IR-92-BINARY-LATTICE-WITNESS-AND-TIE-TRUNCATION",
                "IR-92-MULTI-OWNER-NONSTANDARD-SUBPATHS-AND-STUBS",
            ],
        },
        "fleet_20261027_summary": {
            "public_receipt": "docs/downloads/fleet_20261027_audit_d30d387c.json",
            "receipt_sha256": digest(fleet_raw),
            "focus9_pairwise_receipt_sha256": digest(pair_raw),
            "delta_artifacts_audited": 11,
            "multi_owner_repos_audited": 12,
            "active_multi_owner_repos_with_tiffs": 6,
            "stub_readme_only_multi_owner_repos": [
                m["owner"] + "/" + m["repo"]
                for m in fleet["multi_owner_repositories_20261027"]
                if m["stub_readme_only"]
            ],
        },
        "evidence_sources": {
            "preflight_receipt": "evidence/review_d30d387c_preflight.json",
            "preflight_receipt_sha256": digest(proof_raw),
            "hypotheses": "docs/HYPOTHESES_20261027_D30D387C.md",
            "hypotheses_sha256": digest(HYPOTHESES.read_bytes()),
            "review": "docs/REVIEW_20261027_D30D387C.md",
        },
        "limitations": [
            "Zero organizer-confirmed score receipts exist in ledger/submissions.csv; all fleet leaderboard figures remain owner-reported CLAIMs.",
            "Both 17GEMSDOE (continuous probability surface) and 13GEMSDOE r13-lattice-s5 (pure {0,1} binary 206,895-dot calibration lattice) block nonempty 37,654-dot candidates under literal 3-px >0.70 overlap until a policy owner defines an explicit representation filter.",
            "EUGGEMSDOE1..3 and GINNYGEMSDOE1..3 currently contain only README.md on GitHub and zero GeoTIFFs.",
            "Staged owner-mirror inputs verify SHA-256 pin identity and grid alignment only, not authenticated DrivenData origin or redistribution rights.",
            "No new GeoTIFF, model fit, holdout promotion, or weekly submission slot was created or spent in this session.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        card = json.dumps(build(), indent=2, allow_nan=False) + "\n"
        if args.check:
            if (
                not OUTPUT.is_file()
                or OUTPUT.read_text(encoding="utf-8") != card
                or not PUBLIC_INPUT.is_file()
                or PUBLIC_INPUT.read_bytes() != INPUT.read_bytes()
                or not PUBLIC_FLEET.is_file()
                or PUBLIC_FLEET.read_bytes() != FLEET.read_bytes()
            ):
                raise ValueError("d30d387c public review card, input receipt, or fleet receipt is stale")
            print("2026-10-27 d30d387c review card and receipts: OK")
        else:
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            PUBLIC_INPUT.write_bytes(INPUT.read_bytes())
            PUBLIC_FLEET.write_bytes(FLEET.read_bytes())
            OUTPUT.write_text(card, encoding="utf-8")
            print(f"wrote {OUTPUT}, {PUBLIC_INPUT}, and {PUBLIC_FLEET}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"d30d387c review card failed closed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
