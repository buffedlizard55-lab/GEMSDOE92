"""Tests for BREAKLINE variants (session 2026-10-24).

1. Algorithmic: the lane surface separations and the spaced top-L emitter,
   on synthetic fields (no competition TIFFs needed).
2. Policy: builder receipts, ledger, evidence labels, leakage canary,
   literal-uniqueness measurements and the primary download's hash.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from gems.breakline import lane_surface, percentile_rank, spaced_top_mask

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "docs/downloads" / "h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif"
AUDIT = ROOT / "docs/downloads" / "h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-audit.json"


# --------------------------------------------------------------------------
# 1. Algorithmic
# --------------------------------------------------------------------------
def test_percentile_rank_is_monotone_and_in_unit_range():
    a = np.arange(100, dtype=np.float32).reshape(10, 10)
    r = percentile_rank(a, np.ones_like(a, bool))
    assert r.min() >= 0.0 and r.max() <= 1.0
    assert np.all(np.diff(r.ravel()) >= 0)


def test_lane_surface_peaks_on_a_straight_scarp_edge():
    # A smooth step (fault-like scarp) across the middle columns.
    yy, xx = np.mgrid[0:60, 0:60]
    elev = (10.0 / (1.0 + np.exp(-(xx - 30) / 1.5))).astype(np.float32)
    gy, gx = np.gradient(elev)
    slope = np.hypot(gy, gx).astype(np.float32)
    surf = lane_surface(elev, slope, np.ones_like(elev, bool))
    edge_band = surf["L_pct"][:, 27:34]
    far_band = surf["L_pct"][:, 0:10]
    assert edge_band.mean() > far_band.mean()
    # coherence along the straight edge exceeds coherence of white noise
    rng = np.random.default_rng(0)
    noise = rng.normal(0, 1, elev.shape).astype(np.float32)
    nsurf = lane_surface(noise, slope, np.ones_like(elev, bool))
    assert surf["coherence"][:, 28:33].mean() > nsurf["coherence"].mean()


def test_spaced_top_mask_respects_count_floor_and_order():
    surface = np.zeros((40, 40), np.float32)
    surface[10, 10] = 5.0   # global max, must be taken first
    surface[11, 11] = 4.0   # 1.41 px away -> blocked by the floor
    surface[10, 13] = 3.0   # 3 px away -> allowed
    surface[25, 25] = 2.5
    surface[30, 5] = 2.0
    cand = np.ones((40, 40), bool)
    out = spaced_top_mask(surface, cand, 4)
    assert int(out.sum()) == 4
    assert out[10, 10] and not out[11, 11] and out[10, 13] and out[25, 25] and out[30, 5]
    ys, xs = np.nonzero(out)
    for i in range(len(ys)):
        for j in range(i + 1, len(ys)):
            assert np.hypot(ys[i] - ys[j], xs[i] - xs[j]) >= 2.8 - 1e-9


def test_spaced_top_mask_raises_when_pool_cannot_reach_n():
    with pytest.raises(ValueError):
        spaced_top_mask(np.ones((5, 5), np.float32), np.ones((5, 5), bool), 25)


# --------------------------------------------------------------------------
# 2. Policy: receipts, ledger, instruments, download
# --------------------------------------------------------------------------
def test_breakline_receipts_and_policy_invariants():
    doc = json.loads((ROOT / "evidence/breakline_variants.json").read_text(encoding="utf-8"))
    assert doc["axis"] == "BREAKLINE"
    assert doc["parent"] == "h33-h33-2-b2"
    assert doc["parent_claim"]["evidence_label"] == "CLAIM"
    assert doc["parent_claim"]["receipt"] is False
    assert doc["exact_parent_rebuild"]["matches_recorded_hashes"] is True
    assert "spaced_top_mask" in doc["lane_surface"]["refill_rule"] or \
        "spaced top-L" in doc["lane_surface"]["refill_rule"]
    assert doc["lane_surface"]["far_candidate_pool"]["n_candidates"] > 400000

    variants = doc["variants"]
    assert [v["value"] for v in variants] == ["f33Ltop", "f38Ltop", "f45Ltop"]
    for v, frac in zip(variants, (33.0, 38.0, 45.0)):
        assert v["n_dots"] == 37654
        assert v["status"] == "BUILT"
        assert v["removed"] == v["added"]
        assert v["predicted_change"].startswith("MODEL:")     # never a score
        assert len(v["form_note"]) <= 140
        assert abs(v["pct_changed"] - frac) < 0.01            # applied far dose
        assert 1.0 <= v["pct_changed"] <= 50.0                # brief's change window
        assert v["parent_diff"]["min_catalogue_distance_px"] > 2.0
        assert v["parent_diff"]["far_min_distance_to_h19_px"] > 3.0
        assert v["parent_diff"]["shared"] + v["parent_diff"]["added"] == 37654
        assert all(x for x in v["format_validation"]["nan"].values())
        assert all(x for x in v["format_validation"]["zeros"].values())


def test_breakline_ledger_unique_unreceipted_and_superseded_rows():
    with (ROOT / "ledger/submissions.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    shas = [r["sha256"] for r in rows if r.get("sha256")]
    assert len(shas) == len(set(shas))
    pairs = [(r["parent"], r["axis"], r["value"]) for r in rows]
    assert len(pairs) == len(set(pairs))

    ltop = [r for r in rows if r["axis"] == "BREAKLINE" and r["value"].endswith("Ltop")]
    assert len(ltop) == 3
    for r in ltop:
        assert r["n_dots"] == "37654"
        assert r["receipt_score"] == "" and r["receipt_date"] == ""
    # the superseded exact-greedy doses stay on the record, marked as such
    old = [r for r in rows if r["axis"] == "BREAKLINE" and r["value"].endswith("breakline")]
    assert len(old) == 3
    for r in old:
        assert "SUPERSEDED" in r["notes"]


def test_breakline_mechanism_cards_complete():
    doc = json.loads((ROOT / "evidence/breakline_variants.json").read_text(encoding="utf-8"))
    cards = json.loads((ROOT / "ledger/mechanism_cards.json").read_text(encoding="utf-8"))
    for v in doc["variants"]:
        c = cards[v["id"]]
        for key in ("hypothesis", "mechanism", "non_fault_mimic",
                    "predicted_sign_and_size", "falsifier", "decision_rule"):
            assert c.get(key), f"{v['id']} card missing {key}"
        assert "Lahontan" in c["non_fault_mimic"]


def test_breakline_proxy_audit_labels_instruments_and_uniqueness():
    audit = json.loads((ROOT / "evidence/breakline_proxy_audit.json").read_text(encoding="utf-8"))
    assert audit["evidence_label"] == "PROXY"
    pooled = audit["hide_and_recover_pooled_summary"]
    assert pooled["evidence_class"] == "HOLDOUT-DTI"
    assert pooled["evaluator_version"] == "gems57-pooled-hide-v2"
    assert pooled["triangular_radius_m"] == 300.0
    scores = pooled["scores"]
    assert set(scores) == {"R0", "RELIEFp10", "f33Ltop", "f38Ltop", "f45Ltop"}
    assert scores["R0"]["withheld_positive_pixels"] == 22663
    r0 = scores["R0"]["dti"]
    ltops = [scores[k]["dti"] for k in ("f33Ltop", "f38Ltop", "f45Ltop")]
    assert all(v > r0 for v in ltops)                 # every dose beats parent
    assert ltops == sorted(ltops)                     # monotone dose response
    assert ltops[-1] < scores["RELIEFp10"]["dti"]     # but not the holdout best
    # primary (f45) paired delta vs R0 excludes zero
    d45 = audit["hide_and_recover_pooled_by_candidate"]["f45Ltop"]["paired_differences"]["R0"]
    assert d45["ci95"][0] > 0
    # leakage canary
    can = audit["leakage_canaries"]
    assert can["stop_and_investigate_if_any_gt_0_90"] is False
    assert can["max_symmetric_auc"] < 0.90
    assert "breakline_L_pct" in can["results"]
    # SGMC off-catalogue control: every dose above R0
    sg = audit["sgmc_control_proxy"]["variant_dti"]
    assert all(sg[k] > sg["R0"] for k in ("f33Ltop", "f38Ltop", "f45Ltop"))
    # literal uniqueness on final dots vs pre-session registry rasters
    for arm, u in audit["uniqueness_final_dots"].items():
        assert u["duplicate"] is False, arm
        assert u["worst_forward_overlap"] <= 0.70, arm
        assert u["worst_abs_spearman"] <= 0.90, arm
        assert u["registry_rasters_checked"] >= 15, arm


def test_breakline_primary_download_matches_audit_hash():
    assert PRIMARY.is_file()
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert audit["overall_pass"] is True
    assert hashlib.sha256(PRIMARY.read_bytes()).hexdigest() == audit["sha256_zeros"]
    assert all(g["ok"] for g in audit["gates_zeros"])
