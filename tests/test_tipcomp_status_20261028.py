"""Pins the 2026-10-28 TIPCOMP status: downloadable research file, NOT cleared.

Guards against a silent re-render that drops the 'not cleared' label, and checks
that the independent re-check receipt still describes the bytes on disk.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIF = ROOT / "docs/downloads/gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6-zeros.tif"
CARD = ROOT / "docs/downloads/gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6_run_card.json"
RECEIPT = ROOT / "evidence/tipcomp_independent_check_20261028.json"
SHA = "8f27b9d6478526d72a055f0a56c7c8f6db1d63f2f5c66233b7eedbf9937579cf"


def test_tipcomp_bytes_match_run_card_and_receipt():
    digest = hashlib.sha256(TIF.read_bytes()).hexdigest()
    assert digest == SHA
    assert json.loads(CARD.read_text())["raster_sha256"] == SHA
    receipt = json.loads(RECEIPT.read_text())
    assert receipt["checks"]["candidate_sha256"] == SHA
    assert receipt["checks"]["run_card_sha256_matches"] is True
    assert receipt["checks"]["format_gates_pass"] is True
    assert receipt["checks"]["focus9_GEMSDOE24_peak_match"] is True
    assert receipt["submission_eligible"] is False


def test_front_pages_say_download_is_research_and_submit_not_cleared():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    front = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    root = (ROOT / "index.html").read_text(encoding="utf-8")
    for text in (readme, front, root):
        assert "DO NOT SUBMIT" in text
    assert "NOT CLEARED" in front or "NO TIFF IS CLEARED" in readme
    assert "0.09617" in front and "0.09775" in front
    assert SHA in readme and SHA in front
    assert "evidence/tipcomp_independent_check_20261028.json" in readme
    assert "IR-1028C" in readme
