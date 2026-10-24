"""The public site must expose an obvious zeros-outside download and must never
present a local HOLDOUT number as an organizer score.

Updated 2026-10-24 after the expanded public registry scan found a literal duplicate stop.
The contract asserts explicit format-valid vs slot-ineligible status, evidence
labels, a byte-matched audit, and links to every served raster rather than one
stale method name.
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
    assert "NOT CLEARED FOR A WEEKLY SLOT" in html
    assert "DUPLICATE UNDER THE LITERAL REGISTRY RULE" in html
    assert re.search(r'href="downloads/[^"]+-zeros\.tif"', html), \
        "no zeros-outside download is offered"
    # the portal failure the site exists to prevent must be named
    assert "Predicted values must be in range [0, 1]" in html
    # a slot warning must survive whatever the primary is
    assert re.search(r"(weekly slot|3/week|weekly competition slot|human step)", html, re.I), \
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
    """The primary's audit receipt must describe the bytes actually on disk."""
    import hashlib

    html = _index()
    m = re.search(r'href="(downloads/[^"]+-zeros\.tif)"', html)
    assert m, "index.html offers no zeros-outside primary"
    primary = DOCS / m.group(1)
    assert primary.is_file()

    variant = primary.stem.removesuffix("-zeros")
    audit_path = primary.with_name(variant + "-audit.json")
    assert audit_path.is_file(), f"no audit receipt beside the primary: {audit_path.name}"

    doc = json.loads(audit_path.read_text())
    assert doc["overall_pass"] is True  # format-valid is distinct from slot eligibility
    assert doc["submission_eligible"] is False
    assert doc["sha256_zeros"] == hashlib.sha256(primary.read_bytes()).hexdigest()
    assert all(g["ok"] for g in doc["gates_zeros"]), "audit records a failing format gate"
    assert doc["public_registry_uniqueness"]["unique_under_literal_rule"] is False


def test_submit_page_exists():
    for name in ("SUBMIT.html", "submit.html"):
        p = DOCS / name
        if p.is_file():
            html = p.read_text(encoding="utf-8")
            assert "zeros" in html.lower()
            assert "DrivenData" in html
            return
    pytest.fail("no submission guide page in docs/")
