"""CLI-level regression tests for run-card binding in validate_submission.py.

Written against the validator on main (PR #168, adjacent-card binding). A file is described
only by a card whose SHA-256 AND path name that exact file; nothing here can grant a slot.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TIPCOMP = ROOT / "docs/downloads/gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6-zeros.tif"
TIPCOMP_CARD = "gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6_run_card.json"


def _run(path: Path):
    return subprocess.run([sys.executable, str(ROOT / "validate_submission.py"), str(path)],
                          capture_output=True, text=True, cwd=ROOT)


@pytest.mark.skipif(not TIPCOMP.exists(), reason="candidate file not present")
def test_bound_negative_card_is_reported_and_exit_is_rejection():
    proc = _run(TIPCOMP)
    assert proc.returncode == 1
    assert "FORMAT PASS (local only)" in proc.stdout
    assert TIPCOMP_CARD in proc.stdout
    assert "verdict=negative" in proc.stdout
    assert "OK TO SUBMIT" not in proc.stdout


@pytest.mark.skipif(not TIPCOMP.exists(), reason="candidate file not present")
def test_same_bytes_under_another_name_is_not_bound(tmp_path):
    # Byte-identical copy: the SHA-256 matches the card but the path does not, and no adjacent card exists.
    copy = tmp_path / "renamed-copy-zeros.tif"
    shutil.copyfile(TIPCOMP, copy)
    proc = _run(copy)
    assert proc.returncode == 1
    assert "no run card byte-bound" in proc.stdout
    assert "OK TO SUBMIT" not in proc.stdout


def test_missing_file_fails_closed():
    proc = _run(ROOT / "docs/downloads/does_not_exist.tif")
    assert proc.returncode != 0
    assert "DO NOT SUBMIT" in proc.stdout + proc.stderr
