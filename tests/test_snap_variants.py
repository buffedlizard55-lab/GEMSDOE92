"""Unit and policy tests for spacing-preserving SNAP variants (no competition TIFFs needed in CI)."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
import pytest

from gems.variants import Dots, snap, snap_spaced
from gems57 import metric

ROOT = Path(__file__).resolve().parents[1]


def test_snap_spaced_rejects_invalid_max_shift() -> None:
    d = Dots(np.array([10]), np.array([10]), np.array([1.0]))
    resp = np.ones((25, 25), dtype=np.float32)
    with pytest.raises(ValueError, match="max_shift"):
        snap_spaced(d, resp, value="bad", max_shift=2.5)
    with pytest.raises(ValueError, match="max_shift"):
        snap_spaced(d, resp, value="bad0", max_shift=0.0)


def test_snap_spaced_prevents_along_strike_clumping_unlike_naive_snap() -> None:
    """Two dots 3 px apart near a shared isolated peak must NOT collapse to 1 px apart."""
    parent = Dots(np.array([10, 10]), np.array([10, 13]), np.array([1.0, 1.0]))
    resp = np.zeros((25, 25), dtype=np.float32)
    resp[10, 11] = 1.0
    resp[10, 12] = 0.95

    naive = snap(parent, resp, max_shift=2)
    naive_dist = float(np.hypot(naive.dots.ys[0] - naive.dots.ys[1], naive.dots.xs[0] - naive.dots.xs[1]))
    assert naive_dist < 2.0  # naive snap bunches them onto adjacent pixels (10,11) & (10,12)

    spaced = snap_spaced(parent, resp, value="s2", max_shift=2.0, min_nn=2.8, min_gain=0.01)
    assert len(spaced.dots) == 2
    assert np.allclose(spaced.dots.p, 1.0)
    assert spaced.stats["min_nn_px"] >= 2.8
    assert spaced.stats["max_displacement_px"] <= 2.0 + 1e-9


def test_snap_spaced_respects_keep_out_footprint_and_min_gain() -> None:
    parent = Dots(np.array([10, 20]), np.array([10, 20]), np.array([1.0, 1.0]))
    resp = np.full((30, 30), 0.50, dtype=np.float32)
    resp[10, 11] = 0.99  # forbidden by keep_out
    resp[10, 9] = 0.80   # legal improvement (+0.30 > min_gain)
    resp[20, 21] = 0.505  # tiny noise (+0.005 < min_gain=0.01) -> should NOT move

    keep_out = np.zeros((30, 30), dtype=bool)
    keep_out[10, 11] = True
    fp = np.ones((30, 30), dtype=bool)

    v = snap_spaced(
        parent, resp, value="test", max_shift=2.0, min_nn=2.8,
        min_gain=0.01, footprint=fp, keep_out=keep_out,
    )
    coords = set(zip(v.dots.ys.tolist(), v.dots.xs.tolist()))
    assert (10, 9) in coords
    assert (20, 20) in coords
    assert (10, 11) not in coords


def test_snap_spaced_raises_exact_dti_on_offset_fault_trace() -> None:
    """When parent dots sit 2 px off a linear fault scarp at 3 px spacing, SNAP raises DTI."""
    H, W = 30, 60
    truth = np.zeros((H, W), dtype=bool)
    truth[15, 6:54] = True  # E-W fault scarp at row 15

    # Parent dots offset 2 px north (row 13) every 3 px along strike
    xs = np.arange(6, 54, 3)
    ys = np.full_like(xs, 13)
    parent = Dots(ys, xs, np.ones(len(xs)))

    # Response peaks along the fault scarp at row 15
    resp = np.zeros((H, W), dtype=np.float32)
    for r in range(H):
        resp[r, :] = max(0.0, 1.0 - abs(r - 15) * 0.25)

    v = snap_spaced(parent, resp, value="scarp2p0px", max_shift=2.0, min_nn=2.8, min_gain=0.01)
    m_before = np.zeros((H, W), dtype=bool)
    m_before[parent.ys, parent.xs] = True
    m_after = np.zeros((H, W), dtype=bool)
    m_after[v.dots.ys, v.dots.xs] = True

    dti_before = metric.dti_binary(m_before, truth)["dti"]
    dti_after = metric.dti_binary(m_after, truth)["dti"]
    assert dti_after > dti_before + 0.20
    assert v.stats["min_nn_px"] >= 2.8


def test_snap_receipts_ledger_and_policy_invariants() -> None:
    snap_doc = json.loads((ROOT / "evidence" / "snap_variants.json").read_text(encoding="utf-8"))
    assert snap_doc["axis"] == "SNAP"
    assert snap_doc["parent"] == "h33-h33-2-b2"
    assert snap_doc["parent_claim"]["evidence_label"] == "CLAIM"
    assert snap_doc["parent_claim"]["receipt"] is False
    assert snap_doc["exact_parent_rebuild"]["matches_recorded_hashes"] is True
    assert snap_doc["exact_parent_rebuild"]["zeros_sha256"] == (
        "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
    )
    assert snap_doc["exact_parent_rebuild"]["nan_sha256"] == (
        "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd"
    )
    assert snap_doc["nodata_and_sign_handling"]["in_footprint_nodata_pixels_masked"] == 3061
    assert "Band 5" in snap_doc["nodata_and_sign_handling"]["gravity_gradient_band"]

    variants = snap_doc["variants"]
    assert [v["value"] for v in variants] == ["scarp2p0px", "scarp1p4px", "pot2p0px"]
    for v in variants:
        assert v["n_dots"] == 37654
        assert v["status"] == "BUILT"
        assert v["predicted_change"].startswith("MODEL:")
        assert len(v["form_note"]) <= 140
        assert v["displacement_stats"]["max_displacement_px"] <= 2.0 + 1e-6
        if v["value"] == "scarp1p4px":
            assert v["displacement_stats"]["max_displacement_px"] <= math.sqrt(2.0) + 1e-5
        assert v["displacement_stats"]["min_interdot_nn_px"] >= 2.8
        assert v["parent_diff"]["min_catalogue_distance_px"] > 2.0
        assert all(v["format_validation"]["nan"].values())
        assert all(v["format_validation"]["zeros"].values())

    # Check ledger uniqueness on sha256 and (parent, axis, value)
    with (ROOT / "ledger" / "submissions.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    shas = [r["sha256"] for r in rows]
    pairs = [(r["parent"], r["axis"], r["value"]) for r in rows]
    assert len(shas) == len(set(shas))
    assert len(pairs) == len(set(pairs))
    snap_rows = [r for r in rows if r["axis"] == "SNAP"]
    assert len(snap_rows) == 3
    for r in snap_rows:
        assert r["n_dots"] == "37654"
        assert r["receipt_score"] == ""
        assert r["receipt_date"] == ""

    # Check mechanism cards & report-only proxy audit
    cards = json.loads((ROOT / "ledger" / "mechanism_cards.json").read_text(encoding="utf-8"))
    for v in variants:
        assert v["id"] in cards
        c = cards[v["id"]]
        for req_key in ("hypothesis", "mechanism", "non_fault_mimic", "predicted_sign_and_size", "falsifier"):
            assert c.get(req_key)

    proxy_doc = json.loads((ROOT / "evidence" / "snap_proxy_audit.json").read_text(encoding="utf-8"))
    assert proxy_doc["evidence_label"] == "PROXY"
    assert proxy_doc["leakage_canaries"]["stop_and_investigate_if_any_gt_0_90"] is False
    assert proxy_doc["leakage_canaries"]["max_symmetric_auc"] < 0.90
