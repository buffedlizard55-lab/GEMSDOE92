"""The public site must lead with the download, derive every status from evidence, and never dress a HOLDOUT-DTI
or MODEL number as an organizer score.

Rewritten 2026-10-24.  The earlier contract asserted a fixed "NOT CLEARED / duplicate under the literal registry rule"
banner for every primary, which made OK TO SUBMIT unreachable by construction.  The contract is now derived: the page,
the audit receipt and the run card must equal what gems.uniqueness_policy.decide + gems.verdict.derive compute from the
evidence JSON, and the status cannot be forged by editing HTML (scripts/check_site.py recomputes it).
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]

import check_site  # noqa: E402


def _index() -> str:
    return (DOCS / "index.html").read_text(encoding="utf-8")


def _primary_name() -> str:
    m = re.search(r'href="downloads/([^"]+-zeros\.tif)"', _index())
    assert m, "index.html offers no zeros-outside download"
    return m.group(1)


def _docs():
    name = _primary_name()
    variant = name.removesuffix("-zeros.tif")
    audit = json.loads((DOCS / "downloads" / f"{variant}-audit.json").read_text())
    card = json.loads((ROOT / "evidence" / "lcs_run_card.json").read_text())
    final = json.loads((ROOT / "evidence" / "lcs_registry_final.json").read_text())
    surface = json.loads((ROOT / "evidence" / "lcs_registry_surface.json").read_text())
    return audit, card, final, surface


def test_download_is_the_first_link_and_inside_the_primary_card():
    html = _index()
    first = re.search(r'href="downloads/[^"]+-zeros\.tif"', html)
    card = re.search(r'id="the-file".*?</section>', html, re.S)
    assert first and card
    assert first.start() > card.start() and first.end() < card.end(), "first download link must be inside the primary card"
    assert html.index('id="the-file"') < html.index("<main>"), "the download card must sit above the fold, before <main>"


def test_page_names_the_portal_error_the_evidence_labels_and_the_slot_caution():
    html = _index()
    assert "Predicted values must be in range [0, 1]" in html
    assert "OK TO DOWNLOAD" in html and "OK TO SUBMIT" in html
    assert "HOLDOUT-DTI" in html and "Tier T" in html
    assert re.search(r"(weekly slot|3/week|3 submissions per week|human step)", html, re.I)
    assert not re.search(r"ORGANIZER-CONFIRMED[^<]{0,40}0\.\d{4}", html)
    assert "executive-summary.html" in html


def test_primary_card_shows_exact_name_and_note_within_140_chars():
    audit, card, _, _ = _docs()
    html = _index()
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    assert esc(card["name"]) in html and esc(card["note"]) in html
    assert len(card["name"]) <= 140 and len(card["note"]) <= 140 and card["note_chars"] == len(card["note"])


def test_every_served_zeros_file_is_linked():
    html = _index()
    served = sorted(p.name for p in (DOCS / "downloads").glob("*-zeros.tif"))
    assert served
    for name in served:
        assert f"downloads/{name}" in html, f"{name} is served but not linked from index.html"


def test_primary_audit_and_run_card_match_the_bytes_on_disk():
    audit, card, final, surface = _docs()
    primary = DOCS / "downloads" / _primary_name()
    sha = hashlib.sha256(primary.read_bytes()).hexdigest()
    assert audit["sha256_zeros"] == sha == card["raster_sha256"] == final["candidate_sha256"]
    assert audit["overall_pass"] is True and all(g["ok"] for g in audit["gates_zeros"])
    assert audit["public_registry_uniqueness"]["candidate_hash_matches_scan"] is True
    assert audit["distance_gate_radius_px"] == 3, "the strict 3 px catalogue-distance gate must be the one recorded"


def test_status_on_page_audit_and_card_equals_the_recomputation():
    audit, card, final, surface = _docs()
    derived = check_site.derive_status(card, audit, final, surface)
    assert audit["submission_eligible"] == derived["ok_to_submit"] == card["status"]["ok_to_submit"]
    assert audit["verdict"] == derived["verdict"] == card["verdict"]
    block = re.search(r'id="the-file".*?</section>', _index(), re.S).group(0)
    assert ("✅ OK TO SUBMIT" in block) == derived["ok_to_submit"]
    assert ("⛔ NOT OK TO SUBMIT" in block) == (not derived["ok_to_submit"])
    assert ("SLOT VERDICT: promote" in block) == (derived["verdict"] == "promote")


def test_forged_inputs_flip_the_derived_status():
    audit, card, final, surface = _docs()
    base = check_site.derive_status(card, audit, final, surface)
    f2 = copy.deepcopy(final)
    f2["tier_S"]["max_forward_overlap"] = 0.80
    f2["tier_S"]["n_distinct_over_0_70"] = 1
    assert check_site.derive_status(card, audit, f2, surface)["ok_to_submit"] is False
    c2 = copy.deepcopy(card)
    c2["holdout"]["canary"]["symmetric_auc"] = 0.95
    assert check_site.derive_status(c2, audit, final, surface)["ok_to_submit"] is False
    a2 = copy.deepcopy(audit)
    a2["gates_zeros"][0]["ok"] = False
    d = check_site.derive_status(card, a2, final, surface)
    assert d["ok_to_download"] is False and d["ok_to_submit"] is False
    # a promotion can never rescue an ineligible file
    c3 = copy.deepcopy(card)
    c3["holdout"]["lcs_minus_best"] = dict(delta=0.01, ci95=[0.005, 0.02])
    assert check_site.derive_status(c3, a2, final, surface)["verdict"] == "negative"
    assert base["policy_decision"]["literal_passed"] is False or base["policy_decision"]["tiers"]["T"]["passed"]


def test_literal_rule_is_always_reported_even_when_unpassable():
    audit, card, final, surface = _docs()
    assert "T" in card["registry"]["tiers"]
    assert card["registry"]["blanket_rasters"]["n_distinct"] >= 1
    assert card["status"]["literal_registry_rule_passed"] in (True, False)


def test_public_registry_receipt_from_earlier_sessions_is_still_valid_json_and_cites_scope():
    audit = json.loads((DOCS / "downloads" / "public_registry_uniqueness.json").read_text())
    assert audit["evidence_class"] == "REGISTRY-MEASUREMENT"
    assert audit["final_dots"]["stop_required"] is True
    assert audit["inventory"]["one_band_exact_template_grid_rasters_compared"] == 1279


def test_executive_summary_carries_file_name_note_steps_and_official_links():
    audit, card, _, _ = _docs()
    page = (DOCS / "executive-summary.html").read_text(encoding="utf-8")
    assert audit["file"] in page and "Submit in five steps" in page
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    assert esc(card["name"]) in page and esc(card["note"]) in page
    for url in ("https://www.drivendata.org/competitions/306/competition-doe-gems/",
                "https://docs.nlr.gov/docs/fy26osti/96647.pdf"):
        assert url in page
    assert "Predicted values must be in range [0, 1]" in page and "OK TO DOWNLOAD" in page
    assert "3 submissions per week" in page or "Three submissions per week" in page


def test_legacy_submit_pages_exist_and_point_at_the_current_guide():
    redirect = (DOCS / "submit.html").read_text(encoding="utf-8")
    assert "executive-summary.html" in redirect
    guide = (DOCS / "SUBMIT.html").read_text(encoding="utf-8")
    audit, card, _, _ = _docs()
    assert audit["file"] in guide and "DrivenData" in guide and "OK TO DOWNLOAD" in guide


def test_policy_file_is_valid_and_does_not_change_thresholds():
    from gems import uniqueness_policy as up
    pol = up.load_policy()
    assert pol["thresholds_unchanged"] is True
    assert pol["thresholds"] == {"forward_overlap": 0.70, "abs_spearman": 0.90, "radius_px": 3.0}
    assert "silently drop a raster from the comparison" in pol["never"]


def test_root_page_offers_the_same_download_and_derived_status():
    root_html = (ROOT / "index.html").read_text(encoding="utf-8")
    audit, card, final, surface = _docs()
    assert f"docs/downloads/{audit['file']}" in root_html
    derived = check_site.derive_status(card, audit, final, surface)
    assert ("✅ OK TO SUBMIT" in root_html) == derived["ok_to_submit"]
    assert ("⛔ NOT OK TO SUBMIT" in root_html) == (not derived["ok_to_submit"])
    assert "✅ OK TO DOWNLOAD" in root_html and "docs/index.html" in root_html
    assert "not cleared for submission" not in root_html.lower()
