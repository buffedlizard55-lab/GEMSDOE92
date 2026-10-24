"""Tests for the CONCENTRATION axis builder (prior-driven reallocation).

The builder must: move exactly the requested fraction of dots, take them from the
lowest-prior blocks, deliver them to the highest-prior blocks, keep count and unit
mass, respect the `allowed` mask and the spacing floor, and be bit-reproducible.
"""

import numpy as np
import pytest
from scipy.spatial import cKDTree

from gems.variants import (
    Dots,
    block_density_cv_pair,
    concentration_reallocate,
    spacing_blocked,
)


def line_dots(rows=(10, 20, 30), cols=range(10, 100, 4)):
    ys, xs = [], []
    for r in rows:
        for c in cols:
            ys.append(r)
            xs.append(c)
    return Dots(np.array(ys), np.array(xs), np.ones(len(ys)))


def grid(n=120):
    H = W = n
    foot = np.zeros((H, W), bool)
    foot[5:n - 5, 5:n - 5] = True
    net = np.zeros((H, W), bool)
    for r in (10, 20, 30):
        net[r, 10:100] = True
    return foot, net


def test_moves_exactly_the_requested_fraction_and_holds_count():
    foot, net = grid()
    d = line_dots()
    w = np.ones(foot.shape, np.float32)
    w[:, 60:] = 3.0
    v = concentration_reallocate(d, w, foot, net.copy(), block_px=10, frac=0.10)
    assert len(v.dots) == len(d)
    assert v.stats["n_moved"] == int(round(0.10 * len(d)))
    assert v.pct_changed == pytest.approx(100.0 * v.stats["n_moved"] / len(d))
    assert v.stats["count_preserved"]


def test_sources_are_low_prior_and_arrivals_are_high_prior():
    foot, net = grid()
    d = line_dots()
    w = np.ones(foot.shape, np.float32)
    w[:, 60:] = 3.0            # right half of the grid is favoured
    v = concentration_reallocate(d, w, foot, net.copy(), block_px=10, frac=0.10)
    old = set(zip(d.ys.tolist(), d.xs.tolist()))
    new = set(zip(v.dots.ys.tolist(), v.dots.xs.tolist()))
    added = np.array(sorted(new - old))
    removed = np.array(sorted(old - new))
    assert len(added) == len(removed) == v.stats["n_moved"]
    assert (added[:, 1] >= 50).all(), "arrivals must land in the high-prior blocks"
    assert (removed[:, 1] < 50).all(), "departures must come from the low-prior blocks"


def test_mass_per_dot_is_preserved():
    foot, net = grid()
    d = line_dots()
    w = np.ones(foot.shape, np.float32)
    w[:, 60:] = 2.0
    v = concentration_reallocate(d, w, foot, net.copy(), block_px=10, frac=0.10)
    assert v.dots.p.sum() == pytest.approx(d.p.sum())
    assert np.allclose(np.unique(v.dots.p), 1.0)


def test_arrivals_stay_inside_the_allowed_mask():
    foot, net = grid()
    d = line_dots()
    w = np.ones(foot.shape, np.float32)
    w[:, 60:] = 3.0
    v = concentration_reallocate(d, w, foot, net.copy(), block_px=10, frac=0.10)
    assert net[v.dots.ys, v.dots.xs].all()


def test_no_duplicate_pixels_and_floor_is_respected():
    foot, net = grid()
    d = line_dots()
    w = np.ones(foot.shape, np.float32)
    w[:, 60:] = 3.0
    v = concentration_reallocate(d, w, foot, net.copy(), block_px=10, frac=0.10,
                                 min_nn=1.0)
    keys = list(zip(v.dots.ys.tolist(), v.dots.xs.tolist()))
    assert len(keys) == len(set(keys))
    nn, _ = cKDTree(np.c_[v.dots.ys, v.dots.xs]).query(
        np.c_[v.dots.ys, v.dots.xs], k=2)
    assert nn[:, 1].min() >= 1.0 - 1e-9


def test_builder_is_bit_reproducible():
    foot, net = grid()
    d = line_dots()
    w = np.ones(foot.shape, np.float32)
    w[:, 60:] = 3.0
    a = concentration_reallocate(d, w, foot, net.copy(), block_px=10, frac=0.20)
    b = concentration_reallocate(d, w, foot, net.copy(), block_px=10, frac=0.20)
    assert np.array_equal(a.dots.ys, b.dots.ys)
    assert np.array_equal(a.dots.xs, b.dots.xs)


def test_refuses_empty_prior_blocks_for_every_dot():
    foot, net = grid()
    d = line_dots()
    w = np.zeros(foot.shape, np.float32)   # no prior anywhere
    with pytest.raises(ValueError):
        concentration_reallocate(d, w, foot, net.copy(), block_px=10, frac=0.10)


def test_refuses_when_no_legal_destination_pixel_exists():
    foot, net = grid()
    d = line_dots()
    w = np.ones(foot.shape, np.float32)
    empty = np.zeros(foot.shape, bool)
    with pytest.raises(ValueError):
        concentration_reallocate(d, w, foot, empty, block_px=10, frac=0.10)


def test_spacing_blocked_marks_only_the_open_disc():
    base = np.zeros((40, 40), bool)
    base[20, 20] = True
    blk = spacing_blocked(base, 2.828427)
    assert blk[20, 20] and blk[21, 20] and blk[22, 21]     # inside the open disc
    assert not blk[22, 22]                                 # d = 2.828 = the floor
    assert not blk[24, 20]


def test_block_density_cv_pair_reports_both_definitions():
    foot, net = grid()
    d = line_dots()
    out = block_density_cv_pair(d, net, 10)
    assert out["cv_count"] >= 0
    assert out["cv_density"] >= 0
    assert out["mean_dots_per_network_px"] > 0
