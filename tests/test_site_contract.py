"""The public site must distinguish research downloads from submission eligibility.

The contract checks the current primary's exact bytes, its format receipt,
its negative registry verdict, and consistent download/DO-NOT-SUBMIT wording.
"""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _index() -> str:
    return (DOCS / "index.html").read_text(encoding="utf-8")


def test_index_has_obvious_download_and_no_submit_status():
    html = _index()
    assert "DOWNLOAD STATUS: YES, FOR RESEARCH ONLY. SUBMISSION STATUS: NO" in html
    assert "NOT CLEARED FOR A WEEKLY SLOT" in html
    assert "DUPLICATE UNDER THE LITERAL REGISTRY RULE" in html
    assert "DO NOT SUBMIT" in html
    assert "Predicted values must be in range [0, 1]" in html
    assert "HOLDOUT-DTI" in html
    assert re.search(r'href="downloads/[^"]+-zeros\.tif"', html)
    assert "no new submission artifact generated" in html.lower()
    assert "Download the submission" not in html


def test_index_links_every_served_zeros_file():
    """Anything offered for download must be reachable from the page."""
    html = _index()
    served = sorted(p.name for p in (DOCS / "downloads").glob("*-zeros.tif"))
    linked = set(re.findall(r'href="downloads/([^"]+-zeros\.tif)"', html))
    assert served, "no zeros-outside files in docs/downloads"
    assert set(served) <= linked, f"served raster(s) not linked from index.html: {sorted(set(served) - linked)}"
    assert linked <= set(served), f"homepage link(s) target missing raster(s): {sorted(linked - set(served))}"


def test_primary_download_has_matching_format_and_negative_registry_receipts():
    """The data-primary card must point to the exact bytes covered by its audit/run card."""
    html = _index()
    sections = re.findall(
        r'<section\b(?=[^>]*\bdata-primary="true")[^>]*>(.*?)</section>',
        html,
        flags=re.S,
    )
    assert len(sections) == 1, "homepage must declare exactly one primary research download"
    section = sections[0]
    m = re.search(r'href="(downloads/[^"]+-zeros\.tif)"', section)
    assert m, "primary section offers no zeros-outside GeoTIFF"
    primary = DOCS / m.group(1)
    assert primary.is_file()

    variant = primary.stem.removesuffix("-zeros")
    audit_path = primary.with_name(variant + "-audit.json")
    assert audit_path.is_file(), f"missing primary audit: {audit_path.name}"
    audit = json.loads(audit_path.read_text())
    assert audit["overall_pass"] is True
    assert audit["sha256_zeros"] == hashlib.sha256(primary.read_bytes()).hexdigest()
    assert all(g["ok"] for g in audit["gates_zeros"])
    assert audit["submission_eligible"] is False
    public = audit["public_registry_uniqueness"]
    assert public["candidate_hash_matches_scan"] is True
    assert public["unique_under_literal_rule"] is False
    assert public["stop_required"] is True

    card_path = ROOT / audit["run_card"]
    assert card_path.is_file()
    card = json.loads(card_path.read_text())
    assert card["raster_sha256"] == hashlib.sha256(primary.read_bytes()).hexdigest()
    assert card["verdict"] == "negative"


def test_public_registry_receipt_is_valid_json_and_records_stop():
    """Published machine-readable uniqueness evidence must parse, fail closed, and cite scope."""
    audit = json.loads((DOCS / "downloads" / "public_registry_uniqueness.json").read_text())
    assert audit["evidence_class"] == "REGISTRY-MEASUREMENT"
    assert audit["final_dots"]["stop_required"] is True
    assert audit["inventory"]["one_band_exact_template_grid_rasters_compared"] == 1279


def test_executive_summary_and_submission_aliases_agree_on_current_status():
    executive = (DOCS / "executive-summary.html").read_text(encoding="utf-8")
    canonical = (DOCS / "SUBMIT.html").read_text(encoding="utf-8")
    alias = (DOCS / "submit.html").read_text(encoding="utf-8")
    for page in (executive, canonical, alias):
        assert "DO NOT SUBMIT" in page
    assert "SPRINGALIGN" in executive + canonical
    assert "SUBMIT.html" in executive
    assert "SUBMIT.html" in alias
    assert "No current file is cleared" in canonical
    assert "Do not perform these steps with any current download" in canonical
    assert "submission_eligible: true" in canonical
    assert "Current primary: ANASIG" not in executive + canonical + alias
    assert "Current primary: BREAKLINE" not in executive + canonical + alias


def test_hypothesis_queue_is_explicitly_untested_and_non_predictive():
    text = (DOCS / "HYPOTHESES.md").read_text(encoding="utf-8")
    assert "proposals only" in text.lower()
    assert "not an expected numeric score" in text.lower()
    assert "not viable" in text.lower()
    assert "Paired-profile throw persistence" in text
    assert "Cross-field gravity" in text
    assert "Signed dilatation" in text
    assert "Drainage-crossing persistence" in text
    assert "Expected HOLDOUT-DTI +" not in text


def test_review_card_records_no_build_and_no_invented_holdout():
    card = json.loads((ROOT / "evidence" / "repo_review_run_card_20261024.json").read_text())
    assert card["status"] == "aborted-before-placement"
    assert card["verdict"] == "negative"
    assert card["experiments_used"] == 0
    assert card["submission_slots_used"] == 0
    assert card["holdout_dti"]["evidence_class"] == "NOT_RUN"
    assert card["holdout_dti"]["dti"] is None
    assert card["raster_sha256"] is None
    assert card["submission_name"] is None
    assert card["correlation_overlap_vs_registry"]["witness"]["positive_fraction_of_footprint"] == 1.0
