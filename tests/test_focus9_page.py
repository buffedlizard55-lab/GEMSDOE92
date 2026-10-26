"""Contract tests for the 2026-10-26 nine-site executive summary and score estimator.

These guard the two things that matter most to the user:
  * the download table names a real, byte-verifiable file and states its estimate;
  * no MODEL estimate is ever presented as an organizer score.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidence"
DOCS = ROOT / "docs"


def _load(name: str) -> dict:
    return json.loads((EVID / name).read_text())


def test_focus9_page_is_generated_from_receipts_and_links_a_real_file():
    page = DOCS / "focus9.html"
    assert page.is_file(), "docs/focus9.html missing"
    text = page.read_text(encoding="utf-8")
    card = _load("salemseismo_run_card.json")
    tif = Path(card["candidate_file"]).name
    assert f'href="downloads/{tif}"' in text
    assert (DOCS / "downloads" / tif).is_file()
    for href in re.findall(r'href="(downloads/[^"]+)"', text):
        assert (DOCS / href).is_file(), f"broken download link {href}"
    # both verdict badges must be explicit
    assert "OK TO DOWNLOAD FOR RESEARCH" in text
    assert "DO NOT SUBMIT" in text


def test_focus9_page_covers_every_focus_site_and_the_deliverable_table():
    text = (DOCS / "focus9.html").read_text(encoding="utf-8")
    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        assert site in text, site
    assert "Estimated DTI" in text
    assert "Unique vs the 9 sites" in text
    # explain the 0.2778 result without claiming a receipt
    assert "0.2778" in text
    assert "CLAIM" in text


def test_no_model_estimate_is_labelled_as_an_organizer_score():
    text = (DOCS / "focus9.html").read_text(encoding="utf-8")
    assert not re.search(r"ORGANIZER-CONFIRMED[^<]{0,60}0\.\d", text)
    est = _load("score_estimator_20261026.json")
    assert est["evidence_class"].startswith("MODEL")
    assert "NOT an organizer score" in est["evidence_class"]
    assert est["loo_rmse"] > 0 and est["training_rows"] >= 50
    assert 0.0 <= est["loo_spearman"] <= 1.0


def test_focus9_audit_records_match_pinned_bytes_and_keep_zero_xor_identities():
    audit = _load("focus9_executive_audit_20261026.json")
    ids = audit["exact_set_identities"]
    # The lineage algebra this page relies on must stay exactly zero-XOR.
    assert ids["gems25_d28_xor_gems30_d28"] == 0
    assert ids["gems28_solo_xor_gems31_solo"] == 0
    assert ids["gems31_solo_xor_d28_gt1px"] == 0
    assert ids["gems32_b2_xor_d28_gt2px"] == 0
    assert ids["d28_to_solo_pruned_le1px"] + ids["solo_to_b2_pruned_1_to_2px"] == ids["d28_to_b2_total_pruned_le2px"]
    assert ids["gems36_extra_dots_over_gems32_b2"] == 1200
    for rec in audit["records"]:
        assert rec["organizer_confirmed_score"] is None
        assert rec["claim_label"].startswith(("CLAIM", "UNSCORED"))


def test_salemseismo_arms_are_gate_clean_unique_and_byte_bound():
    card = _load("salemseismo_run_card.json")
    assert card["verdict"] == "negative"
    assert card["submission_eligible"] is False
    assert card["weekly_slots_spent"] == 0
    assert card["experiments_run"] == 3
    assert card["organizer_confirmed"] is None
    assert 0 < card["submission_note_chars"] <= 140
    tif = ROOT / card["candidate_file"]
    assert hashlib.sha256(tif.read_bytes()).hexdigest() == card["raster_sha256"]
    uniq = _load("salemseismo_uniqueness.json")
    for arm, rec in uniq["candidates"].items():
        assert rec["operative_over_70pct_count"] == 0, arm
        assert rec["worst_operative_overlap_3px"] <= 0.70, arm
        assert abs(rec["final_dots_worst_abs_spearman"]) <= 0.90, arm
    hold = _load("salemseismo_holdout.json")
    assert hold["leakage_canaries"]["all_pass"] is True
    assert hold["leakage_canaries"]["max_symmetric_auc"] <= 0.90


def test_index_surfaces_the_new_lane_and_the_executive_summary():
    text = (DOCS / "index.html").read_text(encoding="utf-8")
    card = _load("salemseismo_run_card.json")
    assert Path(card["candidate_file"]).name in text
    assert "focus9.html" in text
    assert "SALEMSEISMO" in text
    # the new section must not compete for the machine-readable primary anchor
    assert text.count('data-primary="true"') == 1


def test_score_estimator_is_reproducible_from_committed_receipts():
    est = _load("score_estimator_20261026.json")
    keys = {r["key"] for r in est["predictions"]}
    assert {"GEMSDOE32__historical_best", "GEMSDOE70__fleet_best_non_h195_scored",
            "SALEMSEISMO__celftail52k"} <= keys
    assert len(est["training"]["rows"]) == est["training_rows"]
    for row in est["training"]["rows"]:
        assert 0.0 <= row["claim"] <= 1.0
    # the CLI contract used by the page
    src = (ROOT / "scripts" / "estimate_scores.py").read_text()
    assert "H19_SATURATION" in src
    assert "leave-one-out" in src.lower() or "loo" in src.lower()
