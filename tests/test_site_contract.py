"""Public download pages and their machine receipts must fail closed."""

import hashlib
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PRIMARY_NAME = "h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif"
WITNESS_RECEIPT = "review_20261024_springalign_witness_v2.json"


def _index() -> str:
    return (DOCS / "index.html").read_text(encoding="utf-8")


def test_index_has_obvious_download_and_no_submit_status():
    html = _index()
    assert "DOWNLOAD STATUS: YES, FOR RESEARCH ONLY. SUBMISSION STATUS: NO" in html
    assert "No GeoTIFF is cleared for competition submission" in html
    assert "NOT CLEARED FOR A WEEKLY SLOT" in html
    assert "DUPLICATE UNDER THE LITERAL REGISTRY RULE" in html
    assert "DO NOT SUBMIT" in html
    assert "Predicted values must be in range [0, 1]" in html
    assert "HOLDOUT-DTI" in html
    assert "No new unique TIFF or experiment was produced" in html
    assert "No weekly slot was used" in html
    assert "Download the submission" not in html


def test_index_links_every_served_zeros_file():
    """Every served zeros-outside TIFF is linked, and no stale TIFF link remains."""
    html = _index()
    served = {p.name for p in (DOCS / "downloads").glob("*-zeros.tif")}
    linked = set(re.findall(r'href="downloads/([^"]+-zeros\.tif)"', html))
    assert served
    assert served == linked


def test_primary_download_has_matching_format_and_negative_registry_receipts():
    """The explicit primary must match its audit, exact-file witness and run card."""
    html = _index()
    sections = re.findall(
        r'<section\b(?=[^>]*\bdata-primary="true")[^>]*>(.*?)</section>',
        html,
        flags=re.S,
    )
    assert len(sections) == 1, "homepage must declare exactly one primary research download"
    links = re.findall(r'href="(downloads/[^"]+-zeros\.tif)"', sections[0])
    assert len(links) == 1
    primary = DOCS / links[0]
    assert primary.name == PRIMARY_NAME
    assert primary.is_file()

    expected_hash = hashlib.sha256(primary.read_bytes()).hexdigest()
    variant = primary.stem.removesuffix("-zeros")
    audit_path = primary.with_name(variant + "-audit.json")
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["overall_pass"] is True
    assert audit["sha256_zeros"] == expected_hash
    assert all(g["ok"] for g in audit["gates_zeros"])
    assert audit["submission_eligible"] is False
    public = audit["public_registry_uniqueness"]
    assert public["candidate_hash_matches_scan"] is True
    assert public["unique_under_literal_rule"] is False
    assert public["stop_required"] is True

    receipt_path = ROOT / "evidence" / WITNESS_RECEIPT
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["candidate"]["sha256"] == expected_hash
    assert receipt["forward_overlap_candidate_dots_within_3px_of_witness"] == 1.0
    assert receipt["spearman_full_footprint"] == pytest.approx(0.04372948694731268)
    assert receipt["submission_eligible"] is False
    assert receipt["scope"].startswith("Single witness")

    card_path = ROOT / audit["run_card"]
    card = json.loads(card_path.read_text(encoding="utf-8"))
    assert card["raster_sha256"] == expected_hash
    assert card["verdict"] == "negative"


def test_public_registry_receipt_is_valid_json_and_records_stop():
    """Published machine-readable uniqueness evidence must parse, fail closed, and cite scope."""
    audit = json.loads((DOCS / "downloads" / "public_registry_uniqueness.json").read_text())
    assert audit["evidence_class"] == "REGISTRY-MEASUREMENT"
    assert audit["final_dots"]["stop_required"] is True
    assert audit["inventory"]["one_band_exact_template_grid_rasters_compared"] == 1279


def test_guides_agree_on_current_research_only_status_and_exact_receipt():
    executive = (DOCS / "executive-summary.html").read_text(encoding="utf-8")
    canonical = (DOCS / "SUBMIT.html").read_text(encoding="utf-8")
    alias = (DOCS / "submit.html").read_text(encoding="utf-8")
    for page in (executive, canonical, alias):
        assert "DO NOT SUBMIT" in page
        assert PRIMARY_NAME in page
        assert WITNESS_RECEIPT in page
        assert "No new unique TIFF was generated" in page
    assert "Do not perform these steps with the current artifact" in canonical
    assert "Do not take any current download through submission steps" in alias
    assert "separate name field" in canonical
    assert "separate name field" in executive
    assert "No current file is cleared" in canonical
    assert "Current primary: ANASIG" not in executive + canonical + alias
    assert "Current primary: BREAKLINE" not in executive + canonical + alias


def test_archived_breakline_and_visible_collar_are_not_presented_as_current_primary():
    html = _index()
    guide = (DOCS / "SUBMIT.html").read_text(encoding="utf-8")
    assert "Archived visible-collar" in html
    assert "GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif" in html
    assert "Visible-fault collar 2-3 px; R0 3px halo excluded; 37,654 dots" in html
    assert "visible_collar_run_card.json" in html
    assert "BREAKLINE: DUPLICATE — DO NOT SUBMIT" in html
    assert "BREAKLINE: DUPLICATE — DO NOT SUBMIT" in guide


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
    measured = card["correlation_overlap_vs_registry"]["existing_primary_measurement"]
    assert measured["forward_overlap_within_3px"] == 1.0
    assert measured["candidate_sha256"] == "1772ad5c62506b6b380e221d2202b583edf0a5be4f96916af655e0478eba11b1"


def test_site_missing_primary_receipt_fails_without_traceback(tmp_path, monkeypatch, capsys):
    import scripts.check_site as site

    primary_name = "example-zeros.tif"
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    (download_dir / primary_name).write_bytes(b"not a TIFF; only used to name the missing receipt")
    index = tmp_path / "index.html"
    index.write_text(
        '<section data-primary="true"><a href="downloads/example-zeros.tif">research</a></section>',
        encoding="utf-8",
    )
    monkeypatch.setattr(site, "INDEX", index)
    monkeypatch.setattr(site, "DOCS", tmp_path)
    empty_downloads = tmp_path / "empty-downloads"
    empty_downloads.mkdir()
    monkeypatch.setattr(site, "DOWNLOADS", empty_downloads)
    assert site.main() == 1
    output = capsys.readouterr().out
    assert "unreadable JSON receipt" in output
    assert "Traceback" not in output


@pytest.mark.parametrize("text", ["{broken", "[]", "null"])
def test_site_invalid_json_evidence_fails_closed(tmp_path, text):
    from scripts.check_site import read_json_object

    path = tmp_path / "audit.json"
    path.write_text(text, encoding="utf-8")
    problems = []
    assert read_json_object(path, problems) == {}
    assert problems


def test_pages_validates_before_uploading_artifact():
    workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    assert workflow.index("python scripts/check_site.py") < workflow.index("actions/upload-pages-artifact")
    assert "continue-on-error" not in workflow
    assert "python scripts/check_site.py" in (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
