from __future__ import annotations

import csv
import json
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self.href: str | None = None
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self.href = dict(attrs).get("href")
            self.parts = []

    def handle_data(self, data):
        if self.href is not None:
            self.parts.append(data)

    def handle_entityref(self, name):
        if self.href is not None:
            self.parts.append(unescape(f"&{name};"))

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self.href is not None:
            self.links.append((self.href, " ".join(" ".join(self.parts).split())))
            self.href = None
            self.parts = []


def anchors(path: Path) -> list[tuple[str, str]]:
    parser = AnchorParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.links


def local_download(href: str) -> str | None:
    clean = href.split("#", 1)[0].split("?", 1)[0]
    if clean.startswith("downloads/") and Path(clean).suffix.lower() in {".tif", ".tiff", ".zip"}:
        return clean
    return None


def test_readme_is_the_complete_session_starting_point():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    prompt = (ROOT / "SESSION_PROMPT.md").read_text(encoding="utf-8")
    for phrase in (
        "Start every session here",
        "complete operating prompt",
        "Stay in one named method lane",
        "before placement",
        "after placement",
        "whole fault segments/components with a spatial buffer",
        "pixel-exactly",
        "feature-alone leakage canary",
        "3 experiments or 2 hours",
        "DO NOT SUBMIT",
        "Maximize P(Win)",
        "Own the Outcome",
    ):
        assert phrase.lower() in readme.lower(), phrase
    assert "first at the start of every session" in prompt
    assert "not a second source of operating rules" in prompt


def test_disputed_scores_are_typed_and_not_receipt_confirmed():
    with (ROOT / "ledger" / "score_claims.csv").open(newline="", encoding="utf-8") as stream:
        claims = {row["claim_id"]: row for row in csv.DictReader(stream)}
    assert claims["GEMSDOE32_B2"]["value"] == "0.2778"
    assert claims["GEMSDOE32_B2"]["evidence_class"] == "CLAIM"
    assert claims["LEADERBOARD_03195"]["value"] == "0.3195"
    assert claims["LEADERBOARD_03195"]["evidence_class"] == "LEADERBOARD-SNAPSHOT"
    assert claims["LEADERBOARD_04413"]["value"] == "0.4413"
    assert claims["LEADERBOARD_04413"]["evidence_class"] == "LEADERBOARD-SNAPSHOT"
    assert all(row["receipt_verified"].lower() == "false" for row in claims.values())
    assert all(not row["receipt_id"].strip() for row in claims.values())

    with (ROOT / "ledger" / "submissions.csv").open(newline="", encoding="utf-8") as stream:
        submissions = list(csv.DictReader(stream))
    assert not any(row.get("status") == "RECEIPT" for row in submissions)
    assert not any(row.get("receipt_score", "").strip() for row in submissions)


def test_fresh_anasig_witness_receipt_is_pinned_and_scoped():
    docs_receipt = json.loads((ROOT / "docs" / "downloads" / "public_witness_anasig.json").read_text())
    evidence_receipt = json.loads((ROOT / "evidence" / "public_witness_anasig.json").read_text())
    assert docs_receipt == evidence_receipt
    assert docs_receipt["evidence_class"].startswith("REGISTRY-MEASUREMENT")
    assert "not a full public scan" in docs_receipt["scope"].lower()
    assert docs_receipt["candidate"]["sha256"] == "68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5"
    assert docs_receipt["witness"]["git_blob_sha1"] == "374c88b1da2b803e2ed160de467fd71ae114010d"
    assert docs_receipt["witness"]["positive_fraction_of_footprint"] == 1.0
    assert docs_receipt["witness"]["uncovered_allowed_pixels_in_3px_halo"] == 0
    comparison = docs_receipt["postplacement_candidate_comparison"]
    assert comparison["forward_overlap_candidate_dots_within_3px_of_witness"] == 1.0
    assert comparison["duplicate_by_overlap"] is True
    assert comparison["stop_required_vs_this_witness"] is True
    assert docs_receipt["preplacement_surface"]["status"] == "NOT_CHECKED_AGAINST_THIS_WITNESS"


def test_current_status_card_is_negative_and_does_not_claim_new_work():
    card = json.loads((ROOT / "docs" / "downloads" / "current_registry_stop_run_card_20261024.json").read_text())
    candidate = card["candidate"]
    assert candidate["new_candidate_generated_this_review"] is False
    assert candidate["download_status"] == "FORMAT-VALID; OK TO DOWNLOAD FOR RESEARCH"
    assert candidate["submission_status"] == "NOT CLEARED; DO NOT SUBMIT"
    assert candidate["slot_selection_or_upload_authorized"] is False
    assert candidate["submission_name_archived_only"]
    assert len(candidate["submission_note_archived_only"]) == candidate["submission_note_characters"] <= 140
    assert card["experiment_budget"]["experiments_run_this_review"] == 0
    assert card["experiment_budget"]["weekly_submission_slots_used_this_review"] == 0
    assert card["verdict"] == "negative"

    holdout = card["holdout_dti"]
    assert holdout["evidence_class"] == "HOLDOUT-DTI"
    assert holdout["status"].startswith("prior recorded experiment")
    assert holdout["evaluator_version"] == "gems57-pooled-hide-v2"
    assert holdout["withheld_positive_pixels"] == 22663
    assert len(holdout["ci95"]) == 2
    assert holdout["organizer_score"] is None

    registry = card["correlation_overlap_vs_registry"]
    assert registry["evidence_class"] == "REGISTRY-MEASUREMENT"
    assert registry["scope"].startswith("One current")
    assert registry["preplacement_surface"]["status"] == "NOT_CHECKED_AGAINST_THIS_WITNESS"
    assert registry["postplacement_final_output"]["forward_dot_overlap_within_3px"] == 1.0
    assert registry["postplacement_final_output"]["duplicate_stop"] is True
    assert card["validator_output"]["status"].startswith("PASS")
    assert card["validator_output"]["reread_sha256"] == candidate["raster_sha256"]


def test_hypothesis_queue_has_three_to_five_unvalidated_candidates_and_source_status():
    queue = json.loads((ROOT / "docs" / "hypothesis_queue_20261024.json").read_text())
    hypotheses = queue["hypotheses"]
    assert 3 <= len(hypotheses) <= 5
    assert [item["rank"] for item in hypotheses] == list(range(1, len(hypotheses) + 1))
    required = {
        "layers",
        "physical_signature",
        "why_it_may_find_catalogue_missing_faults",
        "distinction_from_prior_repo_methods",
        "named_non_fault_mimics",
        "expected_value_and_cost",
        "required_data",
        "official_source",
        "viable_now",
        "blocked_because",
    }
    for item in hypotheses:
        assert required <= item.keys()
        assert "UNVALIDATED" in item["status"]
        assert item["viable_now"] is False
        assert item["official_source"]["availability_verified_this_review"] is False
        assert "No numeric DTI" in item["expected_value_and_cost"]
    assert queue["experiment_budget"]["experiments_run_this_review"] == 0
    assert queue["experiment_budget"]["active_lane"] is None


def test_every_public_tiff_and_zip_link_has_do_not_submit_status():
    pages = [
        ROOT / "docs" / "index.html",
        ROOT / "docs" / "executive-summary.html",
        ROOT / "docs" / "SUBMIT.html",
        ROOT / "docs" / "submit.html",
    ]
    for page in pages:
        for href, label in anchors(page):
            resource = local_download(href)
            if resource:
                assert "DO NOT SUBMIT" in label.upper(), (page.name, href, label)

    index_links = {local_download(href): label for href, label in anchors(pages[0]) if local_download(href)}
    payloads = [* (ROOT / "docs" / "downloads").glob("*.tif"), * (ROOT / "docs" / "downloads").glob("*.tiff"), * (ROOT / "docs" / "downloads").glob("*.zip")]
    for path in payloads:
        href = f"downloads/{path.name}"
        assert href in index_links, path.name
        assert "DO NOT SUBMIT" in index_links[href].upper(), path.name

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    markdown_download_links = re.findall(r"\[([^\]]+)\]\(([^)]+\.(?:tif|tiff|zip))\)", readme, flags=re.I)
    assert markdown_download_links
    for label, _href in markdown_download_links:
        assert "DO NOT SUBMIT" in label.upper(), label


def test_index_correctly_attributes_older_scan_and_current_single_witness():
    page = (ROOT / "docs" / "index.html").read_text(encoding="utf-8").lower()
    assert "single-witness" in page
    assert "pre-placement surface was not compared against that witness" in page
    assert "1,279-raster scan" in page
    assert "visible-collar candidate" in page
    assert "not an anasig scan" in page
