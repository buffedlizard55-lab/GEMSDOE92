"""Public-site contract: downloadable research artifacts are never confused with slot clearance."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"


def _index() -> str:
    return (DOCS / "index.html").read_text(encoding="utf-8")


def test_index_has_research_download_and_literal_slot_warning():
    html = _index()
    assert "OK TO DOWNLOAD" in html
    assert "NOT CLEARED FOR A WEEKLY SLOT" in html
    assert "DUPLICATE UNDER THE LITERAL REGISTRY RULE" in html
    assert re.search(r'href="downloads/[^"]+-zeros\.tif"', html), \
        "no zeros-outside download is offered"
    assert "Predicted values must be in range [0, 1]" in html
    assert "Download the submission" not in html
    assert "DO NOT SUBMIT" in html
    assert re.search(r"(weekly slot|3/week|weekly competition slot|human step)", html, re.I)
    assert "HOLDOUT-DTI" in html
    assert "TIPGAPfar18f33" in html
    assert "negative" in html
    assert "downloads/current_status.json" in html
    first_holdout = html.split("HOLDOUT-DTI", 1)[1][:200]
    assert "ORGANIZER-CONFIRMED" not in first_holdout


def test_index_features_springalign_as_research_only_with_provenance_caveat():
    html = _index()
    assert "Latest prior research artifact — SPRINGALIGN f33Ctop — DO NOT SUBMIT" in html
    first_download = re.search(r'href="(downloads/[^"]+-zeros\.tif)"', html)
    assert first_download and "SPRINGALIGN" in first_download.group(1)
    assert "GEMSDOE92-SPRINGALIGN-f33Ctop-20261025" in html
    assert "the filename date is not independently verified" in html
    assert "below the saved RELIEF p10 holdout best" in html
    status = json.loads((DOWNLOADS / "current_status.json").read_text(encoding="utf-8"))
    candidate = status["latest_historical_candidate"]
    assert candidate["name"] == "GEMSDOE92-SPRINGALIGN-f33Ctop-20261025"
    assert candidate["submission_eligible"] is False
    assert candidate["download_use"] == "research_only_do_not_submit"


def test_index_links_every_served_zeros_file():
    html = _index()
    served = sorted(p.name for p in DOWNLOADS.glob("*-zeros.tif"))
    assert served, "no zeros-outside files in docs/downloads"
    for name in served:
        assert f"downloads/{name}" in html, f"{name} is served but not linked from index.html"


def test_first_research_download_has_byte_matched_format_and_negative_audit():
    """The first downloadable raster must remain auditable, not submission-cleared."""
    html = _index()
    m = re.search(r'href="(downloads/[^"]+-zeros\.tif)"', html)
    assert m, "index.html offers no zeros-outside research download"
    raster = DOCS / m.group(1)
    assert raster.is_file()
    variant = raster.stem.removesuffix("-zeros")
    audit_path = raster.with_name(variant + "-audit.json")
    assert audit_path.is_file(), f"no exact-byte audit beside download: {audit_path.name}"

    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["overall_pass"] is True
    assert audit["sha256_zeros"] == hashlib.sha256(raster.read_bytes()).hexdigest()
    assert all(g["ok"] for g in audit["gates_zeros"])
    assert audit["submission_eligible"] is False
    registry = audit["public_registry_uniqueness"]
    assert registry["candidate_hash_matches_scan"] is True
    assert registry["unique_under_literal_rule"] is False
    assert registry["stop_required"] is True
    card = json.loads((ROOT / audit["run_card"]).read_text(encoding="utf-8"))
    assert card["verdict"] == "negative"
    assert card["raster_sha256"] == audit["sha256_zeros"]
    status = json.loads((DOWNLOADS / "current_status.json").read_text(encoding="utf-8"))
    assert status["latest_historical_candidate"]["file"] == raster.name


def test_current_status_feed_and_review_card_are_consistent():
    status = json.loads((DOWNLOADS / "current_status.json").read_text(encoding="utf-8"))
    card = json.loads((DOWNLOADS / "current_review_run_card.json").read_text(encoding="utf-8"))

    assert status["status"] == "blocked_no_submission_cleared"
    assert status["submission_eligible"] is False
    assert status["new_tif_generated_this_review"] is False
    assert status["weekly_slots_used_this_review"] == 0
    witness = status["registry_blocker"]
    assert witness["evidence_class"] == "REGISTRY-MEASUREMENT"
    assert witness["positive_pixels_in_footprint"] == witness["footprint_pixels"]
    assert witness["positive_fraction_of_footprint"] == 1.0
    assert witness["literal_forward_overlap_stop_threshold"] == 0.7
    assert "not a fresh exhaustive" in witness["scope"].lower()
    assert status["organizer_confirmed_score"] is None

    assert card["decision_status"] == "blocked_before_experiment"
    assert card["holdout_dti"]["status"] == "NOT_RUN"
    assert card["raster_sha256"]["status"] == "NOT_GENERATED"
    assert card["submission_eligible"] is False
    assert card["weekly_slots_used"] == 0
    assert card["verdict"] == "negative"
    assert card["correlation_overlap_vs_registry"]["evidence_class"] == "REGISTRY-MEASUREMENT"


def test_downloadable_public_registry_receipt_is_valid_and_scoped():
    audit = json.loads((DOWNLOADS / "public_registry_uniqueness.json").read_text(encoding="utf-8"))
    assert audit["evidence_class"] == "REGISTRY-MEASUREMENT"
    assert audit["final_dots"]["stop_required"] is True
    assert audit["inventory"]["one_band_exact_template_grid_rasters_compared"] == 1279


def test_aliases_and_executive_summary_match_current_blocked_status():
    canonical = (DOCS / "SUBMIT.html").read_text(encoding="utf-8")
    for name in ("executive-summary.html", "submit.html"):
        page = (DOCS / name).read_text(encoding="utf-8")
        assert "ANASIG" in page
        assert "NOT CLEARED" in page
        assert "DO NOT SUBMIT" in page
        assert "Current primary: BREAKLINE" not in page
        assert "SUBMIT.html" in page and "ANASIG" in canonical


def test_submission_guide_is_future_only_and_explains_form():
    page = (DOCS / "SUBMIT.html").read_text(encoding="utf-8")
    assert "zeros" in page.lower()
    assert "DrivenData" in page
    assert "current artifact is blocked" in page.lower()
    assert "Do not perform these steps with the current artifact" in page
    assert "submission_eligible: true" in page
    assert "140 characters" in page or "140-character" in page
    assert "DO NOT SUBMIT" in page
