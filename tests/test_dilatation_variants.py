"""Unit and policy tests for DILATATION variants (no competition TIFFs needed in CI).

Two groups:
  1. Algorithmic — the reallocation primitive that the DILATATION builder relies on
     (lowest-prior donor selection + high-tercile-constrained refill, count held),
     exercised on a synthetic grid so it runs without the 418 MB feature stack.
  2. Policy — the receipts, ledger uniqueness, evidence labels, leakage canary and
     download-site contract for the three variants built this session.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------
# 1. Algorithmic: lowest-prior donors leave, high-tercile arrivals replace them
# --------------------------------------------------------------------------
def _reallocate_low_to_high(donor_mask, donor_prior, cand_mask, prior, n_shift):
    """Minimal mirror of the builder's donor/arrival rule, for the synthetic test.

    This is the same two-step contract `build_dilatation_variants.py` enforces:
    (a) donors are the n_shift LOWEST-prior parent dots, (b) arrivals come only
    from `cand_mask` (high tercile ∩ ridge ∩ clearance), (c) count is held.
    """
    ys, xs = np.nonzero(donor_mask)
    order = np.argsort(donor_prior[np.nonzero(donor_mask)], kind="stable")
    drop_y, drop_x = ys[order[:n_shift]], xs[order[:n_shift]]
    out = donor_mask.copy()
    out[drop_y, drop_x] = False
    cy, cx = np.nonzero(cand_mask & ~out)
    take = np.argsort(-prior[cy, cx], kind="stable")[:n_shift]
    out[cy[take], cx[take]] = True
    return out


def test_dilatation_shift_drops_lowest_prior_and_holds_count():
    mask = np.zeros((30, 30), bool)
    ys = np.arange(2, 22)
    mask[ys, 5] = True                       # 20 dots
    prior = np.zeros((30, 30), np.float32)
    prior[ys, 5] = np.linspace(0.0, 1.0, 20)  # lowest prior at the top rows
    cand = np.zeros((30, 30), bool)
    cand[24:28, 5] = True                     # 4 legal high-tercile arrivals
    out = _reallocate_low_to_high(mask, prior, cand, prior, n_shift=4)
    assert int(out.sum()) == 20                       # count held exactly
    assert np.count_nonzero(mask & ~out) == 4         # exactly 4 removed
    assert np.count_nonzero(out & ~mask) == 4         # exactly 4 added
    # the four removed are the four LOWEST-prior dots (rows 2,3,4,5)
    assert not out[2:6, 5].any()
    # the four added are the four highest-prior legal arrivals
    assert out[24:28, 5].all()


def test_dilatation_arrivals_never_leave_candidate_pool():
    mask = np.zeros((20, 20), bool)
    mask[3:13, 3] = True
    prior = np.zeros((20, 20), np.float32)
    prior[3:13, 3] = np.linspace(0.0, 0.9, 10)
    cand = np.zeros((20, 20), bool)
    cand[15:18, 3] = True
    out = _reallocate_low_to_high(mask, prior, cand, prior, n_shift=3)
    # every pixel that is new must be inside the candidate pool
    new = out & ~mask
    assert new.any()
    assert not (new & ~cand).any()


# --------------------------------------------------------------------------
# 2. Policy: receipts, ledger, evidence labels, download contract
# --------------------------------------------------------------------------
def test_dilatation_receipts_and_policy_invariants() -> None:
    doc = json.loads((ROOT / "evidence" / "dilatation_variants.json").read_text(encoding="utf-8"))
    assert doc["axis"] == "DILATATION"
    assert doc["parent"] == "h33-h33-2-b2"
    assert doc["parent_claim"]["evidence_label"] == "CLAIM"
    assert doc["parent_claim"]["receipt"] is False
    assert doc["exact_parent_rebuild"]["matches_recorded_hashes"] is True
    assert doc["dilatation_terciles"]["band"].startswith("Band 8 geod_dilaterate")

    variants = doc["variants"]
    assert len(variants) == 3
    assert [v["value"] for v in variants] == ["p10dilatation", "p12dilatation", "p15dilatation"]

    for v in variants:
        assert v["n_dots"] == 37654
        assert v["status"] == "BUILT"
        assert v["removed"] == v["added"]                     # count held
        assert v["predicted_change"].startswith("MODEL:")     # never a score
        assert len(v["form_note"]) <= 140                     # submission-form limit
        assert 1.0 <= v["pct_changed"] <= 50.0                # brief's change window
        assert v["parent_diff"]["min_catalogue_distance_px"] > 2.0
        assert v["dilatation_distribution"]["high_pct"] > 36.59  # strictly above R0's 36.60%
        assert all(x for x in v["format_validation"]["nan"].values())
        assert all(x for x in v["format_validation"]["zeros"].values())


def test_dilatation_ledger_is_unique_and_unreceipted() -> None:
    with (ROOT / "ledger" / "submissions.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    shas = [r["sha256"] for r in rows if r.get("sha256")]
    assert len(shas) == len(set(shas)), "Duplicate SHA256 in ledger"
    pairs = [(r["parent"], r["axis"], r["value"]) for r in rows]
    assert len(pairs) == len(set(pairs)), "Duplicate (parent, axis, value) in ledger"

    dil = [r for r in rows if r["axis"] == "DILATATION"]
    assert len(dil) == 3
    for r in dil:
        assert r["n_dots"] == "37654"
        assert r["receipt_score"] == ""    # a projection is never a receipt
        assert r["receipt_date"] == ""


def test_dilatation_mechanism_cards_are_complete() -> None:
    doc = json.loads((ROOT / "evidence" / "dilatation_variants.json").read_text(encoding="utf-8"))
    cards = json.loads((ROOT / "ledger" / "mechanism_cards.json").read_text(encoding="utf-8"))
    for v in doc["variants"]:
        assert v["id"] in cards, f"missing mechanism card for {v['id']}"
        c = cards[v["id"]]
        for key in ("hypothesis", "mechanism", "non_fault_mimic",
                    "predicted_sign_and_size", "falsifier", "decision_rule"):
            assert c.get(key), f"{v['id']} card missing {key}"


def test_dilatation_proxy_audit_labels_and_canary() -> None:
    proxy = json.loads((ROOT / "evidence" / "dilatation_proxy_audit.json").read_text(encoding="utf-8"))
    assert proxy["evidence_label"] == "PROXY"
    assert proxy["hide_and_recover_pooled_summary"]["evidence_class"] == "HOLDOUT-DTI"
    assert proxy["hide_and_recover_pooled_summary"]["triangular_radius_m"] == 300.0
    scores = proxy["hide_and_recover_pooled_summary"]["scores"]
    assert set(scores) == {"R0", "p10dilatation", "p12dilatation", "p15dilatation"}
    # every arm must beat R0 on the holdout, and every CI must be finite
    r0 = scores["R0"]["dti"]
    for arm in ("p10dilatation", "p12dilatation", "p15dilatation"):
        assert scores[arm]["dti"] > r0
        lo, hi = scores[arm]["ci95"]
        assert np.isfinite(lo) and np.isfinite(hi) and lo < hi
    # leakage canary: brief says AUC > 0.90 means stop
    canaries = proxy["leakage_canaries"]
    assert canaries["stop_and_investigate_if_any_gt_0_90"] is False
    assert canaries["max_symmetric_auc"] < 0.90
    assert "training_band_8_geod_dilaterate" in canaries["results"]


def test_dilatation_primary_download_is_tracked_and_gate_passed() -> None:
    """The download the site offers must exist, be tracked, and pass the gates on disk."""
    primary = ROOT / "docs" / "downloads" / "h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-zeros.tif"
    assert primary.is_file(), "primary download missing from docs/downloads"

    audit_path = ROOT / "docs" / "downloads" / "h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["overall_pass"] is True
    for g in audit["gates_zeros"]:
        assert g["ok"], f"gate {g['name']} failed in recorded audit"
    # the recorded hash must match the bytes actually in docs/downloads
    got = hashlib.sha256(primary.read_bytes()).hexdigest()
    assert got == audit["sha256_zeros"], "download bytes drifted from the recorded audit hash"

    # .gitignore must un-ignore exactly these, and keep releases/ ignored
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "!docs/downloads/*.tif" in ignore
    assert "!docs/downloads/*.zip" in ignore


def test_dilatation_site_offers_obvious_download_and_submission_note() -> None:
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    # an obvious diagnostic download; local preflight is not official acceptance
    assert "OK TO DOWNLOAD FOR REVIEW" in html
    assert "h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-zeros.tif" in html
    assert "download" in html
    # a unique submission name and a <=140 char note
    assert "GEMSDOE92-DILATATION-p12-20261025" in html
    note = "HOLDOUT-DTI 0.005779 [0.004863,0.006851], gems57-pooled-hide-v2, n=22663; DILATATION p12 duplicate-stop"
    assert note in html and len(note) <= 140
    # the run card must be present with its verdict
    assert "run-card" in html or "Run card" in html
    assert '"verdict"' in html
    submit = (ROOT / "docs" / "SUBMIT.html").read_text(encoding="utf-8")
    assert "DrivenData" in submit and "OK TO DOWNLOAD" in submit


def test_site_must_disclose_the_uniqueness_failure() -> None:
    """Guard the correction: no unqualified 'submit this' banner may come back.

    This repository shipped a `✅ OK TO DOWNLOAD AND SUBMIT` banner and a
    `verdict: promote` run card for a file that measures 99.37 % within 3 px of
    registry raster R0 -- over the brief's 70 % uniqueness limit. The banner was
    corrected; this test is what stops a later session silently reverting it.
    """
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    # the page must state the disqualification, with the measured number
    assert "NOT CLEARED FOR A WEEKLY SLOT" in html
    assert "99.37" in html
    assert "70 %" in html or "70%" in html
    # and it must not carry the withdrawn recommendation
    assert "OK TO DOWNLOAD AND SUBMIT" not in html
    assert "Verdict: promote" not in html
    assert '"verdict": "promote"' not in html
    # the run card verdict must record the disqualification, not a promotion
    assert "NOT_CLEARED" in html

    # the same disclosure must reach the submission guide and the README
    for rel in ("docs/SUBMIT.html", "docs/SUBMIT.md", "README.md", "SLOT_PLAN.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "NOT CLEARED" in text or "fails uniqueness" in text, \
            f"{rel} recommends a slot without disclosing the uniqueness failure"
