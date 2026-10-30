from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "executive-summary-nine-sites-20261030.html"


def test_focus_nine_summary_is_fail_closed_and_covers_requested_sites() -> None:
    page = PAGE.read_text(encoding="utf-8")
    sites = [
        "GEMSDOE24",
        "GEMSDOE25",
        "GEMSDOE27",
        "GEMSDOE28",
        "GEMSDOE30",
        "GEMSDOE31",
        "GEMSDOE32",
        "GEMSDOE33",
        "GEMSDOE36",
    ]
    for site in sites:
        assert f"<th scope=\"row\">{site}</th>" in page
    assert "NO FILE IS CLEARED TO SUBMIT" in page
    assert "DO NOT SUBMIT" in page
    assert "Estimated leaderboard score" in page
    assert "No exact-file leaderboard estimator is validated" in page
    assert "ORGANIZER-CONFIRMED" not in page


def test_focus_nine_summary_is_bound_to_archived_evidence_and_downloads_are_research_only() -> None:
    page = PAGE.read_text(encoding="utf-8")
    sources = json.loads((ROOT / "evidence" / "focus9_sources_20261028.json").read_text())
    uniqueness = json.loads(
        (ROOT / "evidence" / "focus9_uniqueness_20261028.json").read_text()
    )
    holdout = json.loads(
        (ROOT / "evidence" / "focus9_executive_audit_20261026.json").read_text()
    )
    assert set(sources) == set(uniqueness)
    for site, record in sources.items():
        assert record["best"] in page
        assert record["sha256"] in page
        assert record["claim"] is not None
        assert uniqueness[site]["unique_pi1"] is False
        assert f"{uniqueness[site]['worst_overlap']:.4f}" in page
    assert holdout["holdout_evaluator"].startswith("gems57-pooled-hide-v2")
    assert "Download historical TIFF (research only)" in page
    assert "DO NOT SUBMIT" in page
    assert "Download historical TIFF" in page and "submit" in page.lower()
    assert "focus9_uniqueness_20261028.json" in page


def test_focus_summary_is_linked_from_pages_home_and_repo_readme() -> None:
    homepage = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "executive-summary-nine-sites-20261030.html" in homepage
    assert "REVIEW_20261030_FOCUS9.md" in homepage
    assert "docs/executive-summary-nine-sites-20261030.html" in readme
    assert "docs/REVIEW_20261030_FOCUS9.md" in readme
