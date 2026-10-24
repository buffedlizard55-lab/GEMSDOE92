"""Policy tests for STEPEDGE variants (session 2026-10-24).

Algorithmic surface behaviour is in tests/test_stepedge.py. These pin the
builder receipts, the pre-registered gate outcomes (including the negative
ones -- a test that only passes on success would silently bless a verdict
change), and the primary download's bytes.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "docs/downloads/h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif"
AUDIT = ROOT / "docs/downloads/h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-audit.json"


def test_stepedge_receipts_and_variants():
    doc = json.loads((ROOT / "evidence/stepedge_variants.json").read_text())
    assert doc["axis"] == "STEPEDGE" and doc["parent"] == "h33-h33-2-b2"
    assert doc["parent_claim"] == {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False}
    assert doc["lane_surface"]["far_candidate_pool"]["n_candidates"] > 400000
    assert "preplacement_surface_sha256" in doc["lane_surface"]
    variants = doc["variants"]
    assert [v["value"] for v in variants] == ["f33Sraw", "f45Sraw", "f60Sraw"]
    for v, frac in zip(variants, (33.0, 45.0, 60.0)):
        assert v["n_dots"] == 37654 and v["status"] == "BUILT"
        assert v["removed"] == v["added"]
        assert v["predicted_change"].startswith("MODEL:")   # never a score
        assert len(v["form_note"]) <= 140
        assert abs(v["pct_changed"] - frac) < 0.01
        assert v["parent_diff"]["min_catalogue_distance_px"] > 2.0
        assert v["parent_diff"]["far_min_distance_to_h19_px"] > 3.0
        assert v["parent_diff"]["shared"] + v["parent_diff"]["added"] == 37654
        assert all(x for x in v["format_validation"]["nan"].values())
        assert all(x for x in v["format_validation"]["zeros"].values())


def test_stepedge_ledger_rows_unreceipted():
    with (ROOT / "ledger/submissions.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    mine = [r for r in rows if r["axis"] == "STEPEDGE"]
    assert len(mine) == 3
    for r in mine:
        assert r["n_dots"] == "37654" and r["receipt_score"] == "" and r["receipt_date"] == ""
    cards = json.loads((ROOT / "ledger/mechanism_cards.json").read_text())
    doc = json.loads((ROOT / "evidence/stepedge_variants.json").read_text())
    for v in doc["variants"]:
        c = cards[v["id"]]
        for key in ("hypothesis", "mechanism", "non_fault_mimic",
                    "predicted_sign_and_size", "falsifier", "decision_rule"):
            assert c.get(key), f"{v['id']} card missing {key}"
        assert "Lahontan" in c["non_fault_mimic"]


def test_stepedge_proxy_audit_gate_outcomes():
    audit = json.loads((ROOT / "evidence/stepedge_proxy_audit.json").read_text())
    assert audit["evidence_label"] == "PROXY"
    pooled = audit["hide_and_recover_pooled_summary"]
    assert pooled["evidence_class"] == "HOLDOUT-DTI"
    assert pooled["evaluator_version"] == "gems57-pooled-hide-v2"
    scores = pooled["scores"]
    assert scores["R0"]["withheld_positive_pixels"] == 22663
    # Pre-registered bar FAILS and must stay failed unless evidence changes:
    assert scores["f60Sraw"]["dti"] < scores["STRAINBREAKf60"]["dti"]
    assert scores["f60Sraw"]["dti"] < scores["RELIEFp10"]["dti"]
    d = audit["hide_and_recover_pooled_by_candidate"]["f60Sraw"]["paired_differences"]["R0"]
    assert d["ci95"][0] < 0 < d["ci95"][1]                  # includes zero
    # SGMC: primary is the strongest arm (instruments disagree, recorded)
    sg = audit["sgmc_control"]["dti_by_arm"]
    assert sg["f60Sraw"] == max(sg.values()) and sg["f60Sraw"] > sg["R0"]
    # Leakage canary
    assert audit["leakage_canaries"]["max_symmetric_auc"] < 0.90
    assert audit["leakage_canaries"]["features"]["stepedge_step_pct_BUILT"]["symmetric_auc"] < 0.90
    # Uniqueness: primary unique, siblings duplicate (both facts pinned)
    uni = audit["uniqueness_final_dots"]
    assert uni["f60Sraw"]["duplicate"] is False
    assert uni["f60Sraw"]["worst_forward_overlap"] <= 0.70
    assert uni["f60Sraw"]["registry_rasters_checked"] >= 25
    assert uni["f33Sraw"]["duplicate"] is True and uni["f45Sraw"]["duplicate"] is True
    surf = audit["uniqueness_preplacement_surface"]
    assert surf["worst_abs_sampled_spearman"] <= 0.90
    assert surf["duplicate_by_rho_gt_0p90"] is False


def test_stepedge_run_card_verdict_negative_and_primary_bytes():
    card = json.loads((ROOT / "evidence/stepedge_run_card.json").read_text())
    assert card["verdict"] == "negative" and card["submission_eligible"] is False
    assert card["automated_gates"]["holdout_beats_strainbreak_f60"] is False
    assert card["automated_gates"]["format_gates_pass"] is True
    assert card["note_chars"] <= 140
    assert PRIMARY.is_file()
    assert hashlib.sha256(PRIMARY.read_bytes()).hexdigest() == card["raster_sha256"]
    site_audit = json.loads(AUDIT.read_text())
    assert site_audit["overall_pass"] is True
    assert site_audit["sha256_zeros"] == card["raster_sha256"]
    assert site_audit["submission_eligible"] is False
    assert all(g["ok"] for g in site_audit["gates_zeros"])
    # Dense public witness: literal verdict preserved, rho gates measured.
    pub = site_audit["public_registry_uniqueness"]
    assert pub["unique_under_literal_rule"] is False and pub["stop_required"] is True
    assert pub["candidate_hash_matches_scan"] is True
    assert pub["forward_overlap"] == 1.0
    assert abs(pub["sampled_spearman_candidate_vs_witness"]) <= 0.90
