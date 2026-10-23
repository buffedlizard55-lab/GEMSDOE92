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


# ---------------------------------------------------------------------------
# SNAP: evidence threshold, spacing invariant, count conservation
# ---------------------------------------------------------------------------
def _ridge_grid(n=8, step=4):
    """Dots on a regular lattice, with a response ridge offset by +1 px."""
    d = grid_dots(n_side=n, step=step)
    response = np.zeros((80, 80))
    response[:, d.xs + 1] = 1.0          # a strong column ridge, 1 px east
    return d, response


def test_snap_min_gain_keeps_dots_when_gain_is_small():
    d = Dots(np.array([20, 30]), np.array([20, 30]), np.array([1.0, 1.0]))
    response = np.zeros((60, 60))
    response[:, 21] = 0.10               # tiny gain, west column is 0.0
    v0 = snap(d, response, max_shift=2, min_gain=0.0)
    v1 = snap(d, response, max_shift=2, min_gain=0.50)
    # only the dot within 2 px of the ridge can reach it; a 0.10 gain is enough
    # at min_gain=0 and not enough at min_gain=0.50
    assert v0.stats["n_moved"] == 1
    assert v1.stats["n_moved"] == 0
    assert len(v1.dots) == 2


def test_snap_min_gain_is_the_dose_knob():
    d, response = _ridge_grid()
    coarse = snap(d, response, max_shift=2, min_gain=0.9)
    fine = snap(d, response, max_shift=2, min_gain=0.0)
    assert fine.stats["n_moved"] >= coarse.stats["n_moved"]
    assert len(fine.dots) == len(coarse.dots) == len(d)


def test_snap_preserves_min_spacing_invariant():
    # a dense lattice at 2 px spacing is UNSAFE; asking for 2.828 px must not
    # create any pair closer than that after snapping
    ys, xs = [], []
    for i in range(6):
        for j in range(6):
            ys.append(10 + 4 * i)
            xs.append(10 + 4 * j)
    d = Dots(np.array(ys), np.array(xs), np.ones(len(ys)))
    response = np.zeros((60, 60))
    response[10:31, 10:31] = 0.5          # flat plateau, so ties dominate
    response[12:32, 12:32] += 0.6         # diagonal ramp
    v = snap(d, response, max_shift=2, min_gain=0.0, min_spacing_px=2.828)
    from scipy.spatial import cKDTree
    tree = cKDTree(np.c_[v.dots.ys, v.dots.xs])
    nn = tree.query(np.c_[v.dots.ys, v.dots.xs], k=2)[0][:, 1]
    assert nn.min() >= 2.828 - 1e-9
    assert len(v.dots) == len(d)


def test_snap_reports_displacement_and_never_duplicates():
    d, response = _ridge_grid()
    v = snap(d, response, max_shift=2, min_gain=0.0, min_spacing_px=2.828)
    assert len(set(zip(v.dots.ys.tolist(), v.dots.xs.tolist()))) == len(d)
    assert v.stats["max_displacement_px"] <= 2.0 + 1e-9
    assert 0.0 <= v.stats["frac_moved"] <= 1.0
    assert v.stats["mean_displacement_px"] == pytest.approx(
        v.stats["mean_displacement_px"])
    assert v.stats["count_preserved"] is True


def test_snap_never_lands_on_keep_out():
    d = Dots(np.array([20]), np.array([20]), np.array([1.0]))
    response = np.zeros((60, 60))
    response[:, 21] = 9.0                  # strongest, but excluded
    keep_out = np.zeros((60, 60), bool)
    keep_out[:, 21] = True
    v = snap(d, response, max_shift=2, min_gain=0.0, keep_out=keep_out)
    assert (v.dots.ys[0], v.dots.xs[0]) == (20, 20)   # stays home


def test_snap_handles_missing_response_at_home():
    """R0 has 16 dots on sentinel pixels of the feature stack.

    A missing home value cannot show that the dot is mispositioned, so such a
    dot never moves: the count and the position are both conserved (this is the
    documented behaviour for R0's 16 sentinel-pixel dots).
    """
    d = Dots(np.array([20]), np.array([20]), np.array([1.0]))
    response = np.full((60, 60), np.nan)
    response[20, 21] = 0.5
    v = snap(d, response, max_shift=2, min_gain=0.0)
    assert len(v.dots) == 1
    assert (v.dots.ys[0], v.dots.xs[0]) == (20, 20)
    assert v.stats["n_dots_without_home_response"] == 1

    all_nan = np.full((60, 60), np.nan)
    v_stay = snap(d, all_nan, max_shift=2, min_gain=0.0)
    assert len(v_stay.dots) == 1
    assert (v_stay.dots.ys[0], v_stay.dots.xs[0]) == (20, 20)
