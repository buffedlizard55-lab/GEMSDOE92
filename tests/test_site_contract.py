"""The public site must show one inspection download without implying clearance."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_index_has_inspection_warning_and_exact_download():
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    assert "INSPECTION ONLY — DO NOT SUBMIT" in html
    assert "Weekly slot: NO." in html
    assert "full-support witness" in html
    assert "downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.tif" in html
    assert "Predicted values must be in range [0, 1]" in html
    assert "HOLDOUT-DTI" in html
    assert "OK TO DOWNLOAD" not in html
    assert "ORGANIZER-CONFIRMED" not in html.split("HOLDOUT-DTI")[1][:200]


def test_submit_page_states_block_and_form_policy():
    html = (ROOT / "docs" / "submit.html").read_text(encoding="utf-8")
    assert "Submission status: blocked" in html
    assert "DO NOT SUBMIT" in html
    assert "When a future candidate is actually cleared" in html
    assert "≤140 characters" in html
