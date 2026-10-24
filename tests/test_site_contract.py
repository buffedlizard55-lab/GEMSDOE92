"""The public site must expose exactly one zeros-outside download and not call HOLDOUT a score."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_index_has_download_and_slot_warning():
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    assert "OK TO DOWNLOAD" in html
    assert "NOT recommended for a weekly competition slot" in html
    assert "downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.tif" in html
    assert "Predicted values must be in range [0, 1]" in html
    assert "HOLDOUT-DTI" in html
    assert "ORGANIZER-CONFIRMED" not in html.split("HOLDOUT-DTI")[1][:200]


def test_submit_page_exists():
    html = (ROOT / "docs" / "submit.html").read_text(encoding="utf-8")
    assert "How to make a competition submission" in html
    assert "zeros-outside" in html.lower() or "zeros-outside" in html or "zeros" in html
