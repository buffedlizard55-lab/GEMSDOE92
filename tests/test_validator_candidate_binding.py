"""IR-1028B-1 regression: the validator must bind run cards to the candidate.

A file is described only by a run card whose SHA-256 AND path name that exact file.
No card, a card for another file, or a 'promote' card must all stay DO NOT SUBMIT.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

import validate_submission as entry

ROOT = Path(__file__).resolve().parents[1]


def _write_card(root: Path, rel_dir: str, name: str, card: dict) -> None:
    d = root / rel_dir
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(json.dumps(card))


@pytest.fixture()
def candidate(tmp_path):
    f = tmp_path / "docs" / "downloads" / "cand-zeros.tif"
    f.parent.mkdir(parents=True)
    f.write_bytes(b"synthetic bytes for binding tests")
    return f


def test_unbound_file_is_do_not_submit(tmp_path, candidate):
    msg = entry.clearance_message(candidate, tmp_path)
    assert msg.startswith("DO NOT SUBMIT")
    assert "no run card is byte-bound" in msg


def test_card_for_other_path_does_not_bind(tmp_path, candidate):
    other = tmp_path / "docs" / "downloads" / "other.tif"
    other.write_bytes(candidate.read_bytes())
    card = {"raster": {"file": "docs/downloads/other.tif",
                       "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest()},
            "verdict": "negative", "submission_eligible": False}
    _write_card(tmp_path, "docs/downloads", "x_run_card.json", card)
    assert "no run card is byte-bound" in entry.clearance_message(candidate, tmp_path)


def test_bound_negative_card_reports_its_verdict(tmp_path, candidate):
    card = {"raster": {"file": "docs/downloads/cand-zeros.tif",
                       "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest()},
            "verdict": "negative", "submission_eligible": False,
            "blocking_reasons": ["holdout tie with R0"]}
    _write_card(tmp_path, "docs/downloads", "c_run_card.json", card)
    msg = entry.clearance_message(candidate, tmp_path)
    assert "verdict=negative in every bound run card" in msg
    assert "holdout tie with R0" in msg
    assert "OK TO SUBMIT" not in msg


def test_promote_card_still_cannot_grant_clearance(tmp_path, candidate):
    card = {"submission_file": "docs/downloads/cand-zeros.tif",
            "raster_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
            "verdict": "promote", "submission_eligible": True}
    _write_card(tmp_path, "evidence", "p_run_card.json", card)
    msg = entry.clearance_message(candidate, tmp_path)
    assert msg.startswith("DO NOT SUBMIT")
    assert "cannot override" in msg
    assert "OK TO SUBMIT" not in msg


def test_cli_exit_code_is_always_rejection_for_current_candidate():
    tip = ROOT / "docs/downloads/gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6-zeros.tif"
    if not tip.exists():
        pytest.skip("candidate file not present")
    proc = subprocess.run([sys.executable, str(ROOT / "validate_submission.py"), str(tip)],
                          capture_output=True, text=True)
    assert proc.returncode == 1
    assert "FORMAT PASS (local only)" in proc.stdout
    assert "DO NOT SUBMIT: verdict=negative" in proc.stdout
    assert "OK TO SUBMIT" not in proc.stdout
