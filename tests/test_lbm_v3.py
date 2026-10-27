"""Tests for the 2026-10-27 leaderboard model, placement and PI-1 uniqueness gate."""
from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import spearmanr

from gems import lbmodel as M
from gems import lbm_place as P
from gems import uniqueness_v3 as U
from vendor.gems57 import metric


def test_coverage_field_matches_official_tp_for_binary_truth():
    rng = np.random.default_rng(0)
    pred = np.zeros((40, 50), np.float32)
    pred[rng.integers(0, 40, 30), rng.integers(0, 50, 30)] = 1.0
    truth = np.zeros((40, 50), bool)
    truth[20, 5:45] = True
    C = M.coverage_field(pred)
    # E[TP] = sum rho*C is exact when rho is the truth indicator
    tp_model = float(C[truth].sum())
    tp_exact = metric.dti_exact(pred, truth)["tp"]
    assert tp_model == pytest.approx(tp_exact, rel=1e-6)  # float32 coverage field


def test_coverage_field_soft_equals_binary_path():
    pred = np.zeros((20, 20), np.float32)
    pred[5, 5] = 1.0; pred[12, 14] = 1.0
    a = M.coverage_field(pred, binary=True)
    b = M.coverage_field(pred, binary=False)
    assert np.allclose(a, b, atol=1e-6)


def test_predict_is_official_dti_algebra():
    A = np.array([[10.0, 0.0]]); m = np.array([[5.0, 0.0]]); n = np.array([100.0])
    rho = np.array([0.1, 0.0]); Ncls = np.array([200.0, 1000.0])
    tp = 1.0; M_ = 5.0 * 0.3; fp = 100 - M_; G = 20.0
    expect = tp / (tp + 0.2 * fp + 0.8 * (G - tp))
    assert M.predict(rho, A, m, n, Ncls)[0] == pytest.approx(expect)


def test_factor_design_shapes():
    X = M.factor_design((3, 6, 5))
    assert X.shape == (90, 1 + 2 + 5 + 4)
    assert np.all(X[:, 0] == 1)


def test_near_fraction_matches_brute_force():
    rng = np.random.default_rng(1)
    H, W = 60, 70
    ours = rng.choice(H * W, 50, replace=False)
    theirs = rng.choice(H * W, 80, replace=False)
    got = U.near_fraction(ours, theirs, (H, W))
    oy, ox = np.divmod(ours, W); ty, tx = np.divmod(theirs, W)
    d = np.hypot(oy[:, None] - ty[None], ox[:, None] - tx[None]).min(axis=1)
    assert got == pytest.approx(float((d <= 3.0).mean()))


def test_exact_spearman_helpers_match_scipy():
    rng = np.random.default_rng(2)
    n = 5000
    top = rng.choice(n, 300, replace=False); vals = rng.random(300); vals[:50] = 1.0
    theirs = np.zeros(n); theirs[top] = vals
    ours_idx = np.sort(rng.choice(n, 120, replace=False)); ours = np.zeros(n); ours[ours_idx] = 1
    assert U.spearman_binary_vs_sparse(ours_idx, n, top, vals) == pytest.approx(spearmanr(ours, theirs)[0], abs=1e-12)
    surf = rng.random(n)
    assert U.spearman_surface_vs_sparse(surf, top, vals) == pytest.approx(spearmanr(surf, theirs)[0], abs=1e-12)


def test_classify_dense_and_space_filling_as_surface():
    n = 1000
    assert U.classify(dict(n_fp_pos=10, top_complete=True), 0.1, n) == "dot_field"
    assert U.classify(dict(n_fp_pos=300, top_complete=True), 0.5, n) == "surface"     # > 20% support
    assert U.classify(dict(n_fp_pos=100, top_complete=True), 0.75, n) == "surface"    # halo > 70%
    assert U.classify(dict(n_fp_pos=100, top_complete=False), 0.1, n) == "surface"


def test_place_respects_caps_at_best_prefix():
    H, W = 80, 80
    rho = np.zeros((H, W)); rho[10:20, 10:70] = 0.2; rho[50:60, 10:70] = 0.02
    elig = np.ones((H, W), bool)
    cand = np.arange(H * W)
    member = (rho.ravel() > 0.1)[:, None]
    res = P.place(rho, elig, n_max=600, cand=cand, member=member, caps=np.array([0.6]), slack=5)
    sel = res["order"][: res["best_n"]]
    share = member[sel, 0].mean()
    assert share <= 0.6 + 5 / max(len(sel), 1) + 1e-9
    assert res["best_D"] > 0
