"""Closeout contracts for the negative, research-only EULERFUSE artifact."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "docs" / "downloads"
STEM = "gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros"
TIF_SHA256 = "5820e882512843a334f4497ed7f294af937339f729e4eeeecdc33d9cdafeeab9"
ZIP_SHA256 = "784ac86499852b6068259715c4e78cb72e791c49899884c9681c168fda8d3f45"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_run_card_is_mirrored_and_fails_closed():
    evidence = ROOT / "evidence" / "eulerfuse_run_card.json"
    mirror = DOWNLOADS / "eulerfuse_run_card.json"
    assert evidence.read_bytes() == mirror.read_bytes()

    card = _json(evidence)
    assert card["verdict"] == "negative"
    assert card["submission_eligible"] is False
    assert card["weekly_slots_used"] == 0
    assert card["experiments_used"] == card["experiment_budget"] == 3
    assert len(card["submission_note"]) <= 140
    assert card["holdout_dti"]["evidence_class"] == "HOLDOUT-DTI"
    assert card["holdout_dti"]["evaluator_version"] == "gems57-pooled-hide-v2"
    assert card["holdout_dti"]["withheld_positive_pixels"] == 22_663
    assert card["holdout_dti"]["promotion_gate_pass"] is False
    assert card["correlation_overlap_vs_registry"]["duplicate_under_literal_rule"] is True
    assert card["correlation_overlap_vs_registry"]["public_final_worst_forward_overlap_3px"] > 0.70


def test_exact_artifact_hash_and_one_file_zip_are_pinned():
    tif = DOWNLOADS / f"{STEM}.tif"
    archive = DOWNLOADS / f"{STEM}.zip"
    assert _sha256(tif) == TIF_SHA256
    assert _sha256(archive) == ZIP_SHA256

    with zipfile.ZipFile(archive) as zf:
        assert zf.namelist() == [tif.name]
        assert zf.read(tif.name) == tif.read_bytes()


def test_run_card_contains_the_exact_validator_receipt():
    card = _json(ROOT / "evidence" / "eulerfuse_run_card.json")
    audit = _json(DOWNLOADS / f"{STEM}-audit.json")
    assert card["raster_sha256"] == audit["sha256"] == TIF_SHA256
    assert card["zip_sha256"] == audit["zip_sha256"] == ZIP_SHA256
    assert card["validator_output"] == audit["validator_output"]
    assert card["validator_gates"] == audit["gates"]
    assert card["validator_all_gates_pass"] is audit["all_gates_pass"] is True
    assert card["validator_output"]["checks"]["range_0_1_guaranteed"] is True
    assert card["validator_output"]["checks"]["outside_footprint_zero"] is True
    assert card["validator_output"]["checks"]["zero_dots_on_mapped_catalogue"] is True
    metadata = _json(DOWNLOADS / f"{STEM}.json")
    assert metadata["submission_eligible"] is False
    assert metadata["approved_for_weekly_slot"] is False
    assert "DO NOT SUBMIT" in metadata["status"]


def test_public_pages_make_the_latest_download_decision_unmistakable():
    for relative in ("README.md", "docs/archive.html", "docs/executive-summary.html", "docs/SUBMIT.html"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert f"{STEM}.tif" in text, relative
        assert TIF_SHA256 in text, relative
        assert "DO NOT SUBMIT" in text, relative
        assert "0.110387" in text, relative
    assert "OK TO DOWNLOAD FOR RESEARCH" in (ROOT / "docs/archive.html").read_text(encoding="utf-8")


def test_run_card_metrics_match_source_evidence():
    card = _json(ROOT / "evidence" / "eulerfuse_run_card.json")
    holdout = _json(ROOT / "evidence" / "eulerfuse_holdout.json")
    public = _json(ROOT / "evidence" / "eulerfuse_public_registry.json")

    score = holdout["primary_drawblind_visible_mask"]["pooled_by_candidate"]["gravity"]["scores"]["gravity"]
    paired = holdout["primary_drawblind_visible_mask"]["pooled_by_candidate"]["gravity"]["paired_differences"]["base_control"]
    assert card["holdout_dti"]["dti"] == score["dti"]
    assert card["holdout_dti"]["ci95"] == score["ci95"]
    assert card["holdout_dti"]["paired_delta_vs_fresh_base_control"] == paired["delta"]
    assert card["holdout_dti"]["paired_delta_ci95"] == paired["ci95"]
    assert public["candidate_file_sha256"] == card["raster_sha256"]
    assert public["inventory"]["candidate_exact_sha256_matches"] == 0
    assert public["preplacement_surface"]["stop_required"] is True
    assert public["final_dots"]["stop_required"] is True
    assert public["binding_witness"]["full_footprint_surface"]["positive_pixels_in_footprint"] == 5_167_373
