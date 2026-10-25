"""Guard the current homepage primary against stale identity and false clearance."""
from __future__ import annotations

import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = "downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif"
SHA = "91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e"
KNICK_SHA = "8ad4a8c2cd8e1fd989b63c752d5e9efc4ba87a2f608ccd551e8787648920d347"


class PrimaryLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "a" and attributes.get("data-primary") == "true":
            self.hrefs.append(attributes.get("href") or "")


def test_homepage_primary_is_the_audited_listricdip_tiff() -> None:
    html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    parser = PrimaryLinks()
    parser.feed(html)
    assert parser.hrefs == [PRIMARY]

    tif = ROOT / "docs" / PRIMARY
    actual_sha = hashlib.sha256(tif.read_bytes()).hexdigest()
    assert actual_sha == SHA

    audit_path = ROOT / "docs/downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["sha256_zeros"] == actual_sha
    assert audit["overall_pass"] is True
    assert audit["submission_eligible"] is False
    assert audit["public_registry_uniqueness"]["unique_under_literal_rule"] is False
    assert audit["public_registry_uniqueness"]["stop_required"] is True

    run_card = json.loads((ROOT / audit["run_card"]).read_text(encoding="utf-8"))
    assert run_card["raster_sha256"] == actual_sha
    assert run_card["verdict"] == "negative"
    assert run_card["submission_eligible"] is False


def test_current_surface_pages_show_verified_primary_hash_and_do_not_submit() -> None:
    for rel in ("README.md", "docs/index.html", "docs/executive-summary.html", "docs/SUBMIT.html"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert SHA in text, f"{rel} does not show the current primary digest"
        assert "DO NOT SUBMIT" in text, f"{rel} must state the file is not submit-cleared"

    # KNICKLOQO remains the best documented local HOLDOUT-DTI, not the current homepage primary.
    for rel in ("README.md", "docs/index.html", "docs/executive-summary.html", "docs/SUBMIT.html"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert KNICK_SHA in text, f"{rel} must preserve the verified KNICKLOQO comparison hash"


def test_repository_review_does_not_claim_a_new_or_promoted_candidate() -> None:
    review = json.loads((ROOT / "evidence/repository_review_20261025_run_card.json").read_text())
    assert review["candidate_experiment"]["status"] == "NOT_RUN"
    assert review["candidate_experiment"]["experiments_used"] == 0
    assert review["candidate_experiment"]["weekly_slots_used"] == 0
    assert review["verdict"] == "negative"
    assert review["submission_eligible"] is False
    assert review["organizer_confirmed"] is None
    assert review["raster_sha256"] == SHA
    assert review["holdout_best_reference"]["raster_sha256"] == KNICK_SHA


def test_pr89_submission_clearance_is_rejected_by_binding_literal_rule() -> None:
    run_card = json.loads((ROOT / "docs/downloads/knickloqo_submission_run_card.json").read_text())
    assert run_card["uniqueness"]["literal_witness"]["worst_overlap"] == 1.0
    assert run_card["uniqueness"]["literal_witness"]["threshold"] == 0.70
    assert run_card["uniqueness"]["literal_witness"]["duplicate"] is True
    assert run_card["uniqueness"]["overall_verdict"] == "DUPLICATE_STOP"
    assert run_card["submission_eligibility"]["uniqueness_pass"] is False
    assert run_card["submission_eligibility"]["submission_eligible"] is False
    assert run_card["submission_eligibility"]["verdict"] == "negative"
    assert run_card["submission_eligibility"]["policy"] == "binding_literal_rule"


def test_download_and_format_pages_do_not_claim_slot_clearance_or_score_projection() -> None:
    ready = (ROOT / "SUBMISSION_READY.md").read_text(encoding="utf-8")
    assert "NOT CLEARED FOR SUBMISSION" in ready
    assert "unsupported projections and are withdrawn" in ready
    assert "Conservative estimate" not in ready and "Optimistic" not in ready

    submit_now = (ROOT / "docs/SUBMIT_NOW.html").read_text(encoding="utf-8")
    assert "DO NOT SUBMIT" in submit_now
    assert "OK TO DOWNLOAD AND SUBMIT" not in submit_now
    assert "literal" in submit_now and "1.000" in submit_now

    validator = (ROOT / "validate_submission.py").read_text(encoding="utf-8")
    assert "NOT SUBMISSION CLEARANCE" in validator
    assert "Expected Score" not in validator
    assert "FILE IS READY FOR SUBMISSION" not in validator

    strategy = (ROOT / "docs/BEAT_0_2778.md").read_text(encoding="utf-8")
    assert "unverified **CLAIM**" in strategy
    assert "do not predict the competition score" in strategy

    fkp = (ROOT / "gems/flexure_knick_province.py").read_text(encoding="utf-8")
    assert "Expected improvement is unknown" in fkp
    assert "raise NotImplementedError" in fkp
