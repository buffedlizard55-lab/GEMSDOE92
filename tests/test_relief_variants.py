"""Unit, metric-oracle, and policy tests for RELIEF variants (runs in CI without competition TIFFs)."""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from exact_dti_refill import (  # noqa: E402
    select_exact_marginal_dti_add_spaced,
    select_exact_marginal_dti_drop,
)
from gems.variants import Dots, compute_relief_terciles, relief  # noqa: E402
from gems57 import metric  # noqa: E402


def _expected_dti_bruteforce(mask: np.ndarray, w: np.ndarray) -> float:
    """Exact expected DTI oracle from scratch over weighted support w."""
    w64 = np.asarray(w, dtype=np.float64)
    H, W = mask.shape
    by, bx = np.nonzero(mask)
    if len(by) == 0:
        return 0.0
    cov = np.zeros((H, W), dtype=np.float64)
    m_dot = np.zeros(len(by), dtype=np.float64)
    for dy, dx, kw in zip(metric.OFF_DY, metric.OFF_DX, metric.OFF_K):
        ny, nx = by + int(dy), bx + int(dx)
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        np.maximum.at(cov, (ny[ok], nx[ok]), kw)
        m_dot[ok] = np.maximum(m_dot[ok], w64[ny[ok], nx[ok]] * float(kw))
    t_val = float((w64 * cov).sum())
    s_val = float(len(by))
    m_val = float(m_dot.sum())
    w_tot = float(w64.sum())
    return t_val / (metric.ALPHA * (t_val + s_val - m_val) + metric.BETA * w_tot + metric.EPS)


def test_exact_marginal_dti_drop_matches_bruteforce_oracle_with_ties() -> None:
    rng = np.random.default_rng(20261024)
    w = rng.random((16, 18))
    base = rng.random((16, 18)) < 0.22
    # Force exact overlapping kernel ties on adjacent dots
    base[7, 7] = True
    base[7, 9] = True
    removable = np.ones_like(base, dtype=bool)
    removable[:3, :] = False

    n_drop = 7
    fast = select_exact_marginal_dti_drop(base, removable, w, n_drop=n_drop)

    oracle = base.copy()
    for _ in range(n_drop):
        ys, xs = np.nonzero(oracle & removable)
        best_dti = -1.0
        best_pt = None
        for y, x in zip(ys.tolist(), xs.tolist()):
            trial = oracle.copy()
            trial[y, x] = False
            sc = _expected_dti_bruteforce(trial, w)
            if sc > best_dti + 1e-15:
                best_dti = sc
                best_pt = (y, x)
        assert best_pt is not None
        oracle[best_pt] = False

    assert np.array_equal(fast, oracle)
    assert int(fast.sum()) == int(base.sum()) - n_drop


def test_exact_marginal_dti_add_spaced_matches_oracle_and_blocks_cardinal_neighbors() -> None:
    rng = np.random.default_rng(1024)
    w = rng.random((16, 18))
    base = np.zeros((16, 18), dtype=bool)
    base[4, 4] = True
    base[10, 12] = True
    cands = rng.random((16, 18)) < 0.35

    n_add = 6
    min_nn = math.sqrt(2.0)
    fast = select_exact_marginal_dti_add_spaced(base, cands, w, n_add=n_add, min_nn=min_nn)

    oracle = base.copy()
    for _ in range(n_add):
        oy, ox = np.nonzero(oracle)
        cy, cx = np.nonzero(cands & ~oracle)
        best_dti = -1.0
        best_pt = None
        for y, x in zip(cy.tolist(), cx.tolist()):
            if np.any(np.hypot(oy - y, ox - x) < min_nn - 1e-9):
                continue
            trial = oracle.copy()
            trial[y, x] = True
            sc = _expected_dti_bruteforce(trial, w)
            if sc > best_dti + 1e-15:
                best_dti = sc
                best_pt = (y, x)
        assert best_pt is not None
        oracle[best_pt] = True

    assert np.array_equal(fast, oracle)
    fy, fx = np.nonzero(fast)
    nn = cKDTree(np.c_[fy, fx]).query(np.c_[fy, fx], k=2)[0][:, 1]
    assert float(nn.min()) >= min_nn - 1e-6


def test_dti_algebra_penalizes_soft_downscaling_justifying_unit_mass_relief() -> None:
    truth = np.zeros((20, 20), dtype=bool)
    truth[10, 3:17] = True
    pred_unit = np.zeros((20, 20), dtype=np.float64)
    pred_unit[10, 4:17:3] = 1.0
    dti_unit = metric.dti_exact(pred_unit, truth)["dti"]
    dti_soft = metric.dti_exact(0.80 * pred_unit, truth)["dti"]
    assert dti_soft < dti_unit - 0.02


def test_compute_relief_terciles_masks_float32_nodata_sentinel() -> None:
    elev = np.linspace(-300.0, 600.0, 900, dtype=np.float32).reshape(30, 30)
    elev[0, :15] = np.float32(-3.4028235e38)
    valid = np.ones((30, 30), dtype=bool)
    valid[-1, :] = False

    terc, (q33, q67) = compute_relief_terciles(elev, valid=valid)
    assert (terc[0, :15] == -1).all()
    assert (terc[-1, :] == -1).all()
    assert -150.0 < q33 < 50.0
    assert 250.0 < q67 < 450.0
    counts = [int((terc == t).sum()) for t in (0, 1, 2)]
    assert max(counts) - min(counts) <= 1


def test_gems_relief_builder_invariants_and_fault_domain_gain() -> None:
    H, W = 36, 60
    elev = np.zeros((H, W), dtype=np.float32)
    elev[:12, :] = -250.0   # Tercile 0: Basin
    elev[12:24, :] = -20.0  # Tercile 1: Piedmont
    elev[24:, :] = 300.0    # Tercile 2: Range-front
    terc, _ = compute_relief_terciles(elev)

    # 30 parent unit-mass dots (10 per tercile, spaced >= 4 px)
    ys, xs = [], []
    for row in (5, 17, 29):
        for col in range(6, 46, 4):
            ys.append(row)
            xs.append(col)
    parent = Dots(np.array(ys), np.array(xs), np.ones(len(ys)))

    # Candidate corridor in each tercile (midpoint infill + extension)
    cands = np.zeros((H, W), dtype=bool)
    for row in (5, 17, 29):
        cands[row, 4:56:2] = True
    score = np.linspace(0.2, 1.0, H * W).reshape(H, W)

    # Concealed truth fault lies strictly in Basin (row 5)
    truth = np.zeros((H, W), dtype=bool)
    truth[5, 4:56] = True

    v_basin = relief(
        parent, elev, terc, frac=0.13, direction="to_basin",
        candidates=cands, relief_score=score, min_nn=math.sqrt(2.0),
    )
    v_rf = relief(
        parent, elev, terc, frac=0.13, direction="to_range_front",
        candidates=cands, relief_score=score, min_nn=math.sqrt(2.0),
    )
    for v in (v_basin, v_rf):
        assert len(v.dots) == len(parent)
        assert np.allclose(v.dots.p, 1.0)
        assert 10.0 <= v.pct_changed <= 15.0
        nn = cKDTree(np.c_[v.dots.ys, v.dots.xs]).query(np.c_[v.dots.ys, v.dots.xs], k=2)[0][:, 1]
        assert float(nn.min()) >= math.sqrt(2.0) - 1e-6

    m0 = np.zeros((H, W), dtype=bool)
    m0[parent.ys, parent.xs] = True
    mb = np.zeros((H, W), dtype=bool)
    mb[v_basin.dots.ys, v_basin.dots.xs] = True
    mr = np.zeros((H, W), dtype=bool)
    mr[v_rf.dots.ys, v_rf.dots.xs] = True

    assert metric.dti_binary(mb, truth)["dti"] > metric.dti_binary(m0, truth)["dti"]
    assert metric.dti_binary(mr, truth)["dti"] < metric.dti_binary(m0, truth)["dti"]

    with pytest.raises(ValueError, match="RELIEF frac"):
        relief(parent, elev, terc, frac=0.05, direction="to_basin", candidates=cands)


def test_relief_receipts_ledger_and_policy_invariants() -> None:
    doc = json.loads((ROOT / "evidence" / "relief_variants.json").read_text(encoding="utf-8"))
    assert doc["axis"] == "RELIEF"
    assert doc["parent"] == "h33-h33-2-b2"
    assert doc["parent_claim"]["evidence_label"] == "CLAIM"
    assert doc["parent_claim"]["receipt"] is False
    assert doc["exact_parent_rebuild"]["matches_recorded_hashes"] is True
    assert doc["exact_parent_rebuild"]["zeros_sha256"] == (
        "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
    )
    assert doc["exact_parent_rebuild"]["nan_sha256"] == (
        "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd"
    )
    assert doc["relief_definition"]["in_footprint_nodata_pixels_masked"] == 3061
    assert "Band 12" in doc["relief_definition"]["det_elev_band"]
    assert "Band 19" in doc["relief_definition"]["det_elev_slope_band"]

    variants = doc["variants"]
    assert [v["value"] for v in variants] == ["basin11pct", "piedmont11pct", "rangefront11pct"]
    for v in variants:
        assert v["n_dots"] == 37654
        assert v["status"] == "BUILT"
        assert 10.0 <= v["pct_changed"] <= 15.0
        assert 1.0 <= v["pct_changed"] <= 50.0
        assert v["predicted_change"].startswith("MODEL:")
        assert len(v["form_note"]) <= 140
        assert v["spacing_and_clearance"]["min_interdot_nn_px"] >= math.sqrt(2.0) - 1e-6
        assert v["spacing_and_clearance"]["added_dots_within_3px"] == 0
        assert v["spacing_and_clearance"]["added_min_catalogue_distance_px"] > 3.0
        assert v["parent_diff"]["min_catalogue_distance_px"] > 2.0
        assert all(v["format_validation"]["nan"].values())
        assert all(v["format_validation"]["zeros"].values())

    with (ROOT / "ledger" / "submissions.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    shas = [r["sha256"] for r in rows]
    pairs = [(r["parent"], r["axis"], r["value"]) for r in rows]
    assert len(shas) == len(set(shas))
    assert len(pairs) == len(set(pairs))
    relief_rows = [r for r in rows if r["axis"] == "RELIEF"]
    assert [r["value"] for r in relief_rows] == ["basin11pct", "piedmont11pct", "rangefront11pct"]
    for r in relief_rows:
        assert r["n_dots"] == "37654"
        assert r["receipt_score"] == ""
        assert r["receipt_date"] == ""

    cards = json.loads((ROOT / "ledger" / "mechanism_cards.json").read_text(encoding="utf-8"))
    for v in variants:
        assert v["id"] in cards
        c = cards[v["id"]]
        for req_key in (
            "hypothesis",
            "mechanism",
            "non_fault_mimic",
            "predicted_sign_and_size",
            "falsifier",
        ):
            assert c.get(req_key)

    proxy_doc = json.loads(
        (ROOT / "evidence" / "relief_proxy_audit.json").read_text(encoding="utf-8")
    )
    assert proxy_doc["evidence_label"] == "PROXY"
    assert proxy_doc["leakage_canaries"]["stop_and_investigate_if_any_gt_0_90"] is False
    assert proxy_doc["leakage_canaries"]["max_symmetric_auc"] < 0.90
