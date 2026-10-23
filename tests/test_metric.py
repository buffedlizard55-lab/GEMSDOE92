"""Tests for the DTI algebra. These pin the brief's own shortcut, so if the
algebra or the |G| reading is wrong, the build fails before any raster exists."""

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
    assert tot.G == pytest.approx(0.0)      # fully covered
    # DTI = 1 / (0.2*1 + 0.2*0 + 0.8*0) = 5.0
    assert tot.dti == pytest.approx(5.0)


def test_gain_add_matches_brief_shortcut():
    """c > 0.2*DTI: the exact marginal gain must equal c - 0.2*DTI when the
    added dot only touches currently uncovered truth (the brief's algebra)."""
    # one dot on one truth pixel -> DTI 5.0, isolated truth pixel 2 px away
    t = make_truth([(10, 10), (10, 12)])
    ds = DotSet([10], [10], [1.0], t)
    dti0 = ds.totals().dti
    # candidate 2 px from the second truth, at distance 2 from nothing else
    y, x = 10, 14  # distance 2 from truth (10,12); 4 from (10,10) -> clips
    c = kernel(2.0)
    got = ds.gain_add(y, x)
    want = c - 0.2 * dti0
    assert got == pytest.approx(want, abs=1e-9), f"got {got}, shortcut says {want}"


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
