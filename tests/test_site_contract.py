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
    # A negative artifact must never be presented with an action label that
    # sounds like permission to use a competition slot.
    assert "Download the submission" not in html
    assert "DO NOT SUBMIT" in html
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
    m = re.search(r'href="(downloads/[^"]+-zeros\.tif)" data-primary="true"', html) \
        or re.search(r'href="(downloads/[^"]+-zeros\.tif)"', html)
    assert m, "index.html offers no zeros-outside primary"
    primary = DOCS / m.group(1)
    assert primary.is_file()

    variant = primary.stem.removesuffix("-zeros")
    audit_path = primary.with_name(variant + "-audit.json")
    assert audit_path.is_file(), f"no audit receipt beside the primary: {audit_path.name}"

    doc = json.loads(audit_path.read_text())
    assert doc["overall_pass"] is True  # format-valid is distinct from slot eligibility
    assert doc["sha256_zeros"] == hashlib.sha256(primary.read_bytes()).hexdigest()
    assert all(g["ok"] for g in doc["gates_zeros"]), "audit records a failing format gate"
    pub = doc["public_registry_uniqueness"]
    assert pub["candidate_hash_matches_scan"] is True
    # fail-closed consistency: eligibility requires a passing literal gate AND a promote verdict
    if pub["unique_under_literal_rule"] is False:
        assert pub["stop_required"] is True
        assert doc["submission_eligible"] is False
    if doc.get("verdict") != "promote":
        assert doc["submission_eligible"] is False


def test_public_registry_receipt_is_valid_json_and_records_stop():
    """Published machine-readable uniqueness evidence must parse, fail closed, and cite scope."""
    audit = json.loads((DOCS / "downloads" / "public_registry_uniqueness.json").read_text())
    assert audit["evidence_class"] == "REGISTRY-MEASUREMENT"
    assert audit["final_dots"]["stop_required"] is True
    assert audit["inventory"]["one_band_exact_template_grid_rasters_compared"] == 1279


def test_legacy_submission_page_redirect_does_not_claim_breakline_is_primary():
    """Aliases must describe the same current primary and warning as the canonical guide."""
    canonical = (DOCS / "SUBMIT.html").read_text(encoding="utf-8")
    for name in ("executive-summary.html", "submit.html"):
        page = (DOCS / name).read_text(encoding="utf-8")
        assert "SCARPDIPOLE" in page
        assert "NOT CLEARED" in page
        assert "Current primary: BREAKLINE" not in page
        assert "SUBMIT.html" in page and "SCARPDIPOLE" in canonical


def test_submit_page_exists():
    for name in ("SUBMIT.html", "submit.html", "executive-summary.html"):
        p = DOCS / name
        assert p.is_file(), f"missing {p}"
        html = p.read_text(encoding="utf-8")
        assert "SCARPDIPOLE" in html
        assert "Current primary: BREAKLINE" not in html
    submit_html = (DOCS / "SUBMIT.html").read_text(encoding="utf-8")
    assert "zeros" in submit_html.lower()
    assert "DrivenData" in submit_html
    assert "h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-zeros.tif" in submit_html
    assert "current artifact is blocked" in submit_html.lower()
    assert "Do not perform these steps with the current artifact" in submit_html
    assert "submission_eligible: true" in submit_html


def test_primary_audit_agrees_with_run_card():
    audit = json.loads((DOCS / "downloads" / "h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-audit.json").read_text())
    card = json.loads((ROOT / audit["run_card"]).read_text())
    assert audit["sha256_zeros"] == card["sha256"]["zeros"]
    assert audit["submission_eligible"] is False
    assert card["submission_eligible"] is False
    assert card["verdict"].startswith("negative")

