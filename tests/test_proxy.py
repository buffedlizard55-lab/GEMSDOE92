"""Tests for the report-only proxy: it must run, be labelled PROXY, and
never be mistaken for a score."""

import numpy as np
import pytest

from gems.proxy import evaluate, leakage_canary, split_positives


def test_split_positives_is_deterministic_and_disjoint():
    ys = np.arange(100)
    xs = np.arange(100)
    a_keep, a_hold = split_positives(ys, xs, frac=0.25, seed=3)
    b_keep, b_hold = split_positives(ys, xs, frac=0.25, seed=3)
    assert np.array_equal(a_hold[0], b_hold[0])
    assert len(a_hold[0]) == 25
    assert len(a_keep[0]) + len(a_hold[0]) == 100


def test_perfect_recall_when_dots_sit_on_withheld_truth():
    cat_ys = np.arange(0, 100, 5)
    cat_xs = np.arange(0, 100, 5)
    keep, hold = split_positives(cat_ys, cat_xs, frac=0.25, seed=1)
    res = evaluate(hold[0], hold[1], cat_ys, cat_xs, frac=0.25, seed=1,
                   min_dots_from_keep=False, n_boot=200)
    assert res["evidence"] == "PROXY"
    assert res["recall_at_3px"] == pytest.approx(1.0)
    assert res["n_withheld"] == len(hold[0])


def test_zero_recall_when_dots_are_far_away():
    cat_ys = np.arange(0, 100, 5)
    cat_xs = np.arange(0, 100, 5)
    res = evaluate(cat_ys + 500, cat_xs + 500, cat_ys, cat_xs,
                   min_dots_from_keep=False, n_boot=200)
    assert res["recall_at_3px"] == pytest.approx(0.0)
    lo, hi = res["ci95"]
    assert lo == 0.0 and hi == 0.0


def test_result_never_claims_to_be_a_score():
    cat_ys = np.arange(0, 50, 5)
    res = evaluate(cat_ys, cat_ys, cat_ys, cat_ys, min_dots_from_keep=False, n_boot=50)
    assert "score" not in str(res.get("evidence", "")).lower()
    assert res["evidence"] == "PROXY"
    assert "proxy" in res["note"].lower() or "catalogue" in res["note"].lower()


def test_leakage_canary_flags_near_perfect_feature():
    rng = np.random.default_rng(0)
    feat = rng.normal(size=(50, 50))
    truth = np.zeros((50, 50), bool)
    truth[10:20, 10:20] = True
    feat[truth] = 10.0          # blatant leak
    assert leakage_canary(feat, truth)["status"] == "STOP_AND_INVESTIGATE"


def test_leakage_canary_quiet_on_noise():
    rng = np.random.default_rng(1)
    feat = rng.normal(size=(60, 60))
    truth = np.zeros((60, 60), bool)
    truth[rng.random((60, 60)) < 0.1] = True
    assert leakage_canary(feat, truth)["status"] == "ok"
