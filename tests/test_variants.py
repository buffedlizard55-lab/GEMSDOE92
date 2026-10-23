"""Tests for the axis builders: one axis at a time, exact change accounting."""

import numpy as np
import pytest

from gems.variants import Dots, concentration, mass_add, mass_drop, prune, snap


def grid_dots(n_side=6, step=5, p=1.0):
    ys, xs = [], []
    for i in range(n_side):
        for j in range(n_side):
            ys.append(3 + i * step)
            xs.append(3 + j * step)
    return Dots(np.array(ys), np.array(xs), np.full(len(ys), p))


def test_dots_reject_zero_mass():
    with pytest.raises(AssertionError):
        Dots([1], [1], [0.0])


def test_mass_drop_removes_worst_by_ranking():
    d = grid_dots()
    ranking = np.arange(len(d), dtype=float)  # higher index = better
    v = mass_drop(d, ranking, frac=0.10)
    n_drop = int(round(0.10 * len(d)))
    assert len(v.dots) == len(d) - n_drop
    # the dropped dots must be exactly the lowest-ranked n_drop dots
    worst = {k for k, _ in sorted(zip(zip(d.ys.tolist(), d.xs.tolist()), ranking),
                                  key=lambda t: t[1])[:n_drop]}
    assert d.keys - v.dots.keys == worst


def test_mass_drop_preserves_mass_per_dot():
    d = grid_dots()
    v = mass_drop(d, np.arange(len(d), dtype=float), frac=0.2)
    assert np.allclose(np.unique(v.dots.p), 1.0)


def test_mass_add_skips_occupied_and_is_ranked():
    d = grid_dots()
    ranked = ([((0, 0), 1.0), ((3, 3), 0.9)]
              + [((200 + i, 200), 0.5 - i * 0.01) for i in range(10)])
    v = mass_add(d, ranked, frac=0.10)
    assert (0, 0) in v.dots.keys          # empty pixel, taken first
    assert (200, 200) in v.dots.keys
    # (3,3) is a parent dot, so it must not be double-counted as an addition
    assert v.stats["n_added"] == int(round(0.10 * len(d)))
    assert len(v.dots.keys) == len(d) + v.stats["n_added"]
    assert len(v.dots) == len(d) + int(round(0.10 * len(d)))


def test_prune_enforces_radius_and_holds_count():
    d = grid_dots()
    # catalogue pixel right next to a dot
    cat_y, cat_x = 3, 4
    refill = [(90, 90 + i) for i in range(50)]
    v = prune(d, [cat_y], [cat_x], radius_px=1, refill=refill, min_catalogue_px=3)
    assert len(v.dots) == len(d)                    # count held
    from scipy.spatial import cKDTree
    tree = cKDTree([[cat_y, cat_x]])
    dd, _ = tree.query(np.c_[v.dots.ys, v.dots.xs])
    assert (dd > 1).all()                           # nothing within 1 px


def test_prune_refuses_radius_at_or_inside_hard_constraint():
    d = grid_dots()
    with pytest.raises(ValueError, match="hard constraint"):
        prune(d, [3], [3], radius_px=3, refill=[(90, 90)], min_catalogue_px=3)


def test_prune_refuses_empty_catalogue():
    d = grid_dots()
    with pytest.raises(ValueError, match="catalogue mask is empty"):
        prune(d, [], [], radius_px=1, refill=[(90, 90)])


def test_concentration_moves_to_high_prior_blocks():
    d = grid_dots(n_side=8, step=5)
    prior = np.zeros((60, 60))
    prior[:, :30] = 0.1      # low-prior half
    prior[:, 30:] = 0.9      # high-prior half
    fp = np.ones((60, 60), bool)
    v = concentration(d, prior, block_px=10, frac=0.15, footprint=fp)
    assert len(v.dots) == len(d)
    before = v.stats["mean_prior_movers_before"]
    after = v.stats["mean_prior_dest"]
    assert after > before
    assert np.isfinite(v.stats["block_density_cv_before"])
    assert np.isfinite(v.stats["block_density_cv_after"])


def test_concentration_count_and_mass_preserved():
    d = grid_dots(n_side=8, step=5)
    prior = np.random.default_rng(3).random((60, 60))
    v = concentration(d, prior, block_px=10, frac=0.15)
    assert len(v.dots) == len(d)
    assert v.dots.p.sum() == pytest.approx(d.p.sum())


def test_snap_respects_shift_bound_and_count():
    d = grid_dots()
    response = np.zeros((80, 80))
    response[40:60, 40:60] = 5.0
    fp = np.ones((80, 80), bool)
    v = snap(d, response, max_shift=2, footprint=fp)
    assert len(v.dots) == len(d)
    assert np.allclose(v.dots.p, d.p)
    assert v.stats["max_displacement_px"] <= 2.0 + 1e-9


def test_snap_respects_keep_out_mask():
    d = Dots(np.array([10]), np.array([10]), np.array([1.0]))
    response = np.zeros((40, 40))
    response[10, 11] = 9.0          # strongest, but forbidden
    response[10, 9] = 3.0
    keep_out = np.zeros((40, 40), bool)
    keep_out[10, 11] = True
    v = snap(d, response, max_shift=2, keep_out=keep_out)
    assert (v.dots.ys[0], v.dots.xs[0]) == (10, 9)


def test_snap_never_stacks_two_dots_on_one_pixel():
    d = Dots(np.array([10, 10]), np.array([10, 12]), np.array([1.0, 1.0]))
    response = np.zeros((40, 40))
    response[10, 11] = 9.0
    v = snap(d, response, max_shift=2)
    assert len(set(zip(v.dots.ys.tolist(), v.dots.xs.tolist()))) == 2


def test_variant_declares_change_fraction():
    d = grid_dots()
    v = mass_drop(d, np.arange(len(d), dtype=float), frac=0.10)
    assert 1.0 <= v.pct_changed <= 50.0


def test_builder_rejects_out_of_window_change():
    """A 0.5% edit must not masquerade as a variant."""
    d = grid_dots(n_side=20, step=3)     # 400 dots
    ranking = np.arange(len(d), dtype=float)
    from gems.variants import Variant
    v = Variant("MASS", "tiny", d, len(d), 2, {})
    with pytest.raises(ValueError, match="outside the brief"):
        v.check_change()
