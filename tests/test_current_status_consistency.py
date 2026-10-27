"""The page anchor and both current-status feeds must identify one artifact."""
import hashlib
import json
from pathlib import Path

from scripts.check_site_legacy_20261026 import check_current_status_sources


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def make_site(root: Path) -> str:
    primary_rel = "downloads/candidate-zeros.tif"
    primary = root / "docs" / primary_rel
    primary.parent.mkdir(parents=True)
    payload = b"test candidate bytes"
    primary.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    current = {
        "file": f"docs/{primary_rel}",
        "sha256": digest,
        "submission_name": "GEMSDOE92-test",
        "note": "test note",
        "ok_to_download": True,
        "ok_to_submit": False,
        "verdict": "negative",
    }
    readiness = {
        "file": primary_rel,
        "raster_sha256": digest,
        "submission_name": "GEMSDOE92-test",
        "note": "test note",
        "download_status": "OK TO DOWNLOAD FOR RESEARCH",
        "submission_status": "DO NOT SUBMIT — NOT CLEARED",
        "submission_eligible": False,
        "verdict": "negative",
    }
    write_json(root / "docs/downloads/current_submission.json", current)
    write_json(root / "docs/downloads/readiness.json", readiness)
    return primary_rel


def test_working_tree_current_status_sources_share_primary_bytes():
    root = Path(__file__).resolve().parents[1]
    from scripts.check_site_legacy_20261026 import primary_download

    problems = []
    index = (root / "docs/index.html").read_text(encoding="utf-8")
    primary_rel = primary_download(index, problems)
    assert problems == []
    assert primary_rel is not None
    assert check_current_status_sources(primary_rel, root) == []


def test_matching_cards_pass_on_a_minimal_fixture(tmp_path):
    primary_rel = make_site(tmp_path)
    assert check_current_status_sources(primary_rel, tmp_path) == []


def test_stale_path_hash_form_fields_and_eligibility_fail_closed(tmp_path):
    primary_rel = make_site(tmp_path)
    current_path = tmp_path / "docs/downloads/current_submission.json"
    readiness_path = tmp_path / "docs/downloads/readiness.json"
    current = json.loads(current_path.read_text())
    readiness = json.loads(readiness_path.read_text())

    readiness["file"] = "downloads/another-zeros.tif"
    readiness["raster_sha256"] = "0" * 64
    readiness["submission_name"] = "different-name"
    readiness["note"] = "different note"
    readiness["submission_eligible"] = True
    readiness["submission_status"] = "OK TO SUBMIT"
    write_json(readiness_path, readiness)

    errors = check_current_status_sources(primary_rel, tmp_path)
    assert any("readiness.json file" in error for error in errors)
    assert any("readiness.json SHA-256" in error for error in errors)
    assert any("submission_name" in error for error in errors)
    assert any("note" in error for error in errors)
    assert any("submission eligibility" in error for error in errors)


def test_overlong_note_is_rejected_in_either_status_feed(tmp_path):
    primary_rel = make_site(tmp_path)
    current_path = tmp_path / "docs/downloads/current_submission.json"
    current = json.loads(current_path.read_text())
    current["note"] = "x" * 141
    write_json(current_path, current)
    errors = check_current_status_sources(primary_rel, tmp_path)
    assert any("current_submission.json note" in error for error in errors)
    assert any("note" in error and "disagree" in error for error in errors)


def test_future_eligible_status_pair_is_supported(tmp_path):
    primary_rel = make_site(tmp_path)
    current_path = tmp_path / "docs/downloads/current_submission.json"
    readiness_path = tmp_path / "docs/downloads/readiness.json"
    current = json.loads(current_path.read_text())
    readiness = json.loads(readiness_path.read_text())
    current["ok_to_submit"] = True
    readiness["submission_eligible"] = True
    readiness["submission_status"] = "OK TO SUBMIT"
    write_json(current_path, current)
    write_json(readiness_path, readiness)
    assert check_current_status_sources(primary_rel, tmp_path) == []


def test_contradictory_submission_status_wording_is_rejected(tmp_path):
    primary_rel = make_site(tmp_path)
    readiness_path = tmp_path / "docs/downloads/readiness.json"
    readiness = json.loads(readiness_path.read_text())
    readiness["submission_status"] = "DO NOT SUBMIT — OK TO SUBMIT"
    write_json(readiness_path, readiness)
    errors = check_current_status_sources(primary_rel, tmp_path)
    assert any("does not clearly block" in error for error in errors)


def test_unsafe_primary_path_is_rejected(tmp_path):
    assert check_current_status_sources("../outside-zeros.tif", tmp_path) == [
        "primary path is unsafe for current-status comparison"
    ]
