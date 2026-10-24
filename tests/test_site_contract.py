"""The public site must expose an obvious zeros-outside download and must never
present a local HOLDOUT number as an organizer score.

Updated 2026-10-25 when the DILATATION lane merged with the TIPGAP lane on main.
The earlier version asserted one hard-coded TIPGAP sentence; the primary is now
chosen by HOLDOUT-DTI, so the contract is written against *properties* of the
page (one obvious primary, a slot warning, the portal error explained, evidence
labels intact, every served file linked) rather than one lane's wording.
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _index() -> str:
    return (DOCS / "index.html").read_text(encoding="utf-8")


def test_index_has_download_and_slot_warning():
    html = _index()
    # an obvious download, and the encoding that survives the portal validator
    assert "OK TO DOWNLOAD" in html
    assert re.search(r'href="downloads/[^"]+-zeros\.tif"', html), \
        "no zeros-outside download is offered"
    # the portal failure the site exists to prevent must be named
    assert "Predicted values must be in range [0, 1]" in html
    # a slot warning must survive whatever the primary is
    assert re.search(r"(weekly slot|3/week|weekly competition slot|human step)", html), \
        "no weekly-slot caution on the page"
    # evidence discipline: holdout numbers must be labelled, and not dressed as scores
    assert "HOLDOUT-DTI" in html
    first_holdout = html.split("HOLDOUT-DTI")[1][:200]
    assert "ORGANIZER-CONFIRMED" not in first_holdout
    # the negative lane must stay visible as a deliverable, with its verdict
    assert "TIPGAPfar18f33" in html
    assert "negative" in html


def test_index_links_every_served_zeros_file():
    """Anything offered for download must be reachable from the page."""
    html = _index()
    served = sorted(p.name for p in (DOCS / "downloads").glob("*-zeros.tif"))
    assert served, "no zeros-outside files in docs/downloads"
    for name in served:
        assert f"downloads/{name}" in html, f"{name} is served but not linked from index.html"


def test_index_primary_has_an_audit_receipt_that_matches():
    """The primary's local format audit must describe the bytes actually on disk."""
    import hashlib

    html = _index()
    m = re.search(r'href="(downloads/[^"]+-zeros\.tif)"', html)
    assert m, "index.html offers no zeros-outside primary"
    primary = DOCS / m.group(1)
    assert primary.is_file()

    variant = primary.stem.removesuffix("-zeros")
    audit_path = primary.with_name(variant + "-audit.json")
    assert audit_path.is_file(), f"no local format-audit JSON beside the primary: {audit_path.name}"

    doc = json.loads(audit_path.read_text())
    assert doc["overall_pass"] is True
    assert doc["sha256_zeros"] == hashlib.sha256(primary.read_bytes()).hexdigest()
    assert all(g["ok"] for g in doc["gates_zeros"]), "audit records a failing gate"


def test_submit_page_exists_and_distinguishes_download_from_slot_clearance():
    canonical = DOCS / "SUBMIT.html"
    assert canonical.is_file(), "canonical executive summary is missing"
    html = canonical.read_text(encoding="utf-8")
    assert "zeros" in html.lower()
    assert "DrivenData" in html
    assert "OK TO DOWNLOAD" in html
    assert "NOT CLEARED" in html
    assert "recommended to submit?</strong> No" in html
    assert "HOLDOUT-DTI" in html
    assert "null/NaN" in html
    assert "Current decision: do not upload this file" in html


def test_lowercase_submission_guide_redirects_to_canonical():
    lower = DOCS / "submit.html"
    assert lower.is_file()
    html = lower.read_text(encoding="utf-8")
    assert 'url=SUBMIT.html' in html
    assert '<a href="SUBMIT.html">' in html


def test_primary_uniqueness_screen_automatically_blocks_r0_duplicate():
    import numpy as np
    import rasterio
    from scripts.check_site import measure_primary_uniqueness

    html = _index()
    match = re.search(r'href="(downloads/[^"]+-zeros\.tif)"', html)
    assert match, "no primary zeros-outside raster"
    primary = DOCS / match.group(1)
    with rasterio.open(ROOT / "data" / "bridge" / "sample_submission.tif") as ds:
        footprint = np.isfinite(ds.read(1))
    result = measure_primary_uniqueness(primary, footprint)
    assert result["status"] == "DUPLICATE_STOP"
    assert result["candidate_dots_within_3px_of_R0"] > 0.70
    assert "parent R0 only" in result["scope"]


def test_research_review_reports_candidate_blocker_without_claiming_score():
    report = ROOT / "docs" / "RESEARCH_AND_CANDIDATE_REVIEW_20261024.md"
    text = report.read_text(encoding="utf-8")
    assert "five testable hypotheses" in text.lower()
    assert "not viable" in text.lower()
    assert "validation is **blocked**" in text.lower()
    assert "ORGANIZER-CONFIRMED" in text
    card = json.loads((ROOT / "evidence" / "review_run_card_20261024.json").read_text())
    assert card["verdict"] == "negative"
    assert len(card["note"]) <= 140
    assert card["note_characters"] == len(card["note"])
    assert card["validator_output"]["official_submission_format_status"] == "UNRESOLVED_OUTSIDE_ENCODING"
    assert card["new_candidate_validation"]["status"] == "BLOCKED_NOT_RUN"
