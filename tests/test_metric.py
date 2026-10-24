"""Tests for the DTI algebra.

Corrected 2026-10-24: the previous tests pinned a session-brief algebra that
could produce DTI = 5.0 (impossible under the official metric, which lies in
[0, 1]). These tests now pin the official p.967 equations and cross-check
gems.metric against vendor/gems57/metric.dti_exact (itself verified against a
literal brute-force transcription in tests/test_metric_and_policy.py)."""

import numpy as np
import pytest

from gems.metric import (ALPHA, BETA, R_PX, DotSet, Truth, kernel)


def make_truth(points):
    ys = np.array([p[0] for p in points])
    xs = np.array([p[1] for p in points])
    return Truth(ys, xs)


def test_kernel_endpoints():
    assert kernel(0.0) == 1.0
    assert kernel(R_PX) == 0.0
    assert kernel(R_PX + 0.5) == 0.0
    assert kernel(1.5) == pytest.approx(0.5)


def test_totals_on_single_dot_single_truth():
    t = make_truth([(10, 10)])
    ds = DotSet([10], [10], [1.0], t)
    tot = ds.totals()
    assert tot.T == pytest.approx(1.0)      # dot sits on truth
    assert tot.S == pytest.approx(1.0)
    assert tot.M == pytest.approx(1.0)
    assert tot.G == pytest.approx(1.0)      # |G| = total truth pixels
    # Official: DTI = 1 / (1 + 0.2*0 + 0.8*0) = 1.0 (perfect, in [0,1])
    assert tot.dti == pytest.approx(1.0)


def test_gain_add_marginal_bar_and_redundancy():
    """Official marginal rule: a non-redundant dot with self-credit k raises
    DTI iff k > ALPHA*DTI; a redundant dot (truth already covered at the same
    kernel weight) has dT = 0 and must not gain."""
    # Isolated second truth 20 px away: no interaction with the first dot.
    t = make_truth([(10, 10), (10, 30)])
    ds = DotSet([10], [10], [1.0], t)
    dti0 = ds.totals().dti
    c = kernel(2.0)  # candidate (10,28) is 2 px from truth (10,30)
    got = ds.gain_add(10, 28)
    assert (got > 0) == (c > ALPHA * dti0)
    # Redundant: truth (10,30) already covered at k=1/3 by a dot at (10,28);
    # an equal-weight dot on the other side adds no TPw.
    ds2 = DotSet([10, 10], [10, 28], [1.0, 1.0], t)
    assert ds2.gain_add(10, 32) < 0


def test_totals_match_vendor_official_metric():
    """gems.metric must agree with vendor/gems57 dti_exact on random cases."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "vendor"))
    from gems57 import metric as vendor_metric

    rng = np.random.default_rng(3)
    for _ in range(25):
        truth = rng.random((20, 20)) < 0.07
        if not truth.any():
            continue
        pred = (rng.random((20, 20)) < 0.09).astype(float)
        tys, txs = np.nonzero(truth)
        ours = DotSet.from_raster(pred, Truth(tys, txs)).totals().dti
        theirs = vendor_metric.dti_exact(pred, truth)["dti"]
        assert ours == pytest.approx(theirs, abs=1e-9)
        assert 0.0 <= ours <= 1.0


def test_gain_add_equals_finite_difference():
    """Brute force: recompute totals with the dot inserted."""
    rng = np.random.default_rng(7)
    truth = make_truth([(rng.integers(0, 40), rng.integers(0, 40)) for _ in range(25)])
    ds = DotSet(rng.integers(0, 40, 20), rng.integers(0, 40, 20),
                np.ones(20), truth)
    base = ds.totals().dti
    for (y, x) in [(0, 0), (20, 20), (5, 35), (39, 39)]:
        if (y, x) in ds.keys:
            continue
        brute = DotSet(np.r_[ds.ys, y], np.r_[ds.xs, x], np.r_[ds.p, 1.0], truth)
        assert ds.gain_add(y, x) == pytest.approx(brute.totals().dti - base, abs=1e-9)


def test_gain_move_equals_finite_difference():
    """Moving a dot must be an exact delta under the same algebra."""
    rng = np.random.default_rng(11)
    truth = make_truth([(rng.integers(0, 30), rng.integers(0, 30)) for _ in range(15)])
    ds = DotSet(rng.integers(0, 30, 12), rng.integers(0, 30, 12), np.ones(12), truth)
    base = ds.totals().dti
    for j, (y, x) in [(0, (3, 3)), (4, (25, 4)), (7, (15, 15))]:
        if (y, x) in ds.keys:
            continue
        ys, xs = ds.ys.copy(), ds.xs.copy()
        ys[j], xs[j] = y, x
        brute = DotSet(ys, xs, ds.p, truth)
        assert ds.gain_move(j, y, x) == pytest.approx(brute.totals().dti - base, abs=1e-9)


def test_dot_carrying_no_truth_is_negative_gain():
    """A dot far from all truth adds mass to the denominator: gain < 0."""
    t = make_truth([(0, 0)])
    ds = DotSet([0], [0], [1.0], t)
    assert ds.gain_add(100, 100) < 0


def test_rank_candidates_sorted_and_deduped():
    t = make_truth([(10, 10)])
    ds = DotSet([10], [10], [1.0], t)
    ranked = ds.rank_candidates([(10, 10), (10, 11), (10, 13), (50, 50)])
    coords = [c for c, _ in ranked]
    assert (10, 10) not in coords          # occupied pixel skipped
    gains = [g for _, g in ranked]
    assert gains == sorted(gains, reverse=True)
    assert coords[0] == (10, 11)           # nearest uncovered-ish truth wins


def test_template_recipe_is_refused():
    """A recipe full of REPLACE_ME must never be accepted as a parent."""
    import json, tempfile, os
    from gems.parent import ParentUnavailable, Recipe
    raw = {"parent_id": "R0", "builder": "gems.builders.x",
           "inputs": {"a.tif": "REPLACE_ME"}, "expected_sha256": "REPLACE_ME",
           "git_sha": "REPLACE_ME", "seed": 0}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(raw, fh)
        name = fh.name
    try:
        with pytest.raises(ParentUnavailable, match="template or incomplete"):
            Recipe.load(name)
    finally:
        os.unlink(name)
