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
    assert "HYDROCONDUIT" in canonical
    for name in ("executive-summary.html", "submit.html"):
        page = (DOCS / name).read_text(encoding="utf-8")
        assert "HYDROCONDUIT" in page
        assert "NOT CLEARED" in page
        assert "Current primary: BREAKLINE" not in page
        assert "SUBMIT.html" in page


def test_hydroconduit_run_card_and_public_scan_integrity():
    """Protocol Rule 5 run card and live public scan must match served primary bytes."""
    import hashlib

    card = json.loads((ROOT / "evidence" / "hydroconduit_run_card.json").read_text(encoding="utf-8"))
    for key in (
        "hypothesis",
        "mechanism",
        "named_non_fault_process_that_could_mimic_it",
        "holdout_dti",
        "correlation_overlap_vs_registry",
        "raster_sha256",
        "validator",
        "submission_name",
        "note",
        "verdict",
    ):
        assert key in card, f"missing run-card key: {key}"

    primary = DOCS / "downloads" / card["file"]
    assert primary.is_file()
    assert hashlib.sha256(primary.read_bytes()).hexdigest() == card["raster_sha256"]
    assert len(card["note"]) <= 140
    assert card["leakage_canary_max_symmetric_auc"] <= 0.90
    assert card["correlation_overlap_vs_registry"]["local"]["literal_duplicate"] is False
    assert card["holdout_dti"]["dti"] > card["holdout_dti"]["holdout_best_prior_RELIEFp10_dti"]
    assert card["verdict"] == "negative"
    assert card["submission_eligible"] is False


def test_submit_page_exists():
    for name in ("SUBMIT.html", "submit.html"):
        p = DOCS / name
        if p.is_file():
            html = p.read_text(encoding="utf-8")
            assert "zeros" in html.lower()
            assert "DrivenData" in html
            assert "current artifact is blocked" in html.lower()
            assert "Do not perform these steps with the current artifact" in html
            assert "submission_eligible: true" in html
            return
    pytest.fail("no submission guide page in docs/")


def test_site_missing_primary_receipt_fails_without_traceback(tmp_path, monkeypatch, capsys):
    import scripts.check_site as site
    primary_name = "example-zeros.tif"
    (tmp_path / primary_name).write_bytes(b"existing candidate")
    index = tmp_path / "index.html"
    index.write_text(f'<a href="downloads/{primary_name}">research</a>')
    # No need to re-gate real 12M-pixel rasters to exercise missing evidence.
    monkeypatch.setattr(site, "INDEX", index)
    monkeypatch.setattr(site, "DOCS", tmp_path)
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    (download_dir / primary_name).write_bytes(b"candidate")
    monkeypatch.setattr(site, "DOWNLOADS", tmp_path / "empty-downloads")
    assert site.main() == 1
    assert "unreadable JSON receipt" in capsys.readouterr().out


@pytest.mark.parametrize("text", ["{broken", "[]", "null"])
def test_site_invalid_json_evidence_fails_closed(tmp_path, text):
    from scripts.check_site import read_json_object
    path = tmp_path / "audit.json"
    path.write_text(text)
    problems = []
    assert read_json_object(path, problems) == {}
    assert problems


def test_pages_validates_before_uploading_artifact():
    workflow = (ROOT / ".github/workflows/pages.yml").read_text()
    assert workflow.index("python scripts/check_site.py") < workflow.index("actions/upload-pages-artifact")
    assert "continue-on-error" not in workflow
    assert "python scripts/check_site.py" in (ROOT / ".github/workflows/ci.yml").read_text()


def test_guides_agree_with_current_primary_and_stop():
    for name in ("SUBMIT.html", "submit.html", "executive-summary.html"):
        html = (DOCS / name).read_text()
        assert 'SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif' in html
        assert 'review_20261024_springalign_witness_v2.json' in html
        assert 'Do not perform these steps with the current artifact' in html
        assert 'separate name field' in html
        assert 'No new unique TIFF was generated' in html
    html = _index()
    assert 'unique GeoTIFF generated this session' not in html
    assert 'format-valid, unique download' not in html


def test_piedfront_primary_contract_across_site_and_readme():
    idx = (DOCS / "index.html").read_text(encoding="utf-8")
    exec_sum = (DOCS / "executive-summary.html").read_text(encoding="utf-8")
    sub = (DOCS / "SUBMIT.html").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for tok in (
        "GEMSDOE92-PIEDFRONT-f35Ptop-20261024",
        "h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif",
        "e314f4c004927ff56334827b4d45c57fc62da3da3010c12682d7cce6d0f185a8",
        "0.006425",
    ):
        assert tok in idx, f"missing {tok} in docs/index.html"
        assert tok in exec_sum, f"missing {tok} in docs/executive-summary.html"
        assert tok in sub, f"missing {tok} in docs/SUBMIT.html"
        assert tok in readme, f"missing {tok} in README.md"
