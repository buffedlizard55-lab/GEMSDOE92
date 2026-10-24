"""Unit tests for the CONCENTRATION builder (no competition data required).

These tests pin the invariants the session relies on:
  * the prior is a km-scale field, continuous, zero outside the footprint blocks
  * movers come from the correct end of the prior distribution, deterministically
  * placement never violates the declared spacing floor and never overfills
  * the block-CV statistic reports both definitions
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_concentration_variants import (  # noqa: E402
    block_keys, choose_movers, density_cv, fault_density_prior, place_movers,
)


@pytest.fixture()
def grid():
    H = W = 60
    foot = np.ones((H, W), bool)
    cat = np.zeros((H, W), bool)
    cat[10:14, 10:14] = True          # dense fault patch in block (1, 1)
    cat[45, 45:50] = True             # line in block (4, 4)
    return foot, cat


def test_prior_is_continuous_and_blocked(grid):
    foot, cat = grid
    prior = fault_density_prior(cat, foot, block_px=10, sigma_px=10)
    dens = prior["dens"]
    assert dens.shape == (7, 7)
    assert np.isfinite(dens[prior["in_footprint"]]).all()
    assert dens[1, 1] > dens[0, 0]     # the dense patch block outranks an empty corner
    assert np.nanmax(dens) <= 1.0
    # every in-footprint block carries a finite prior (blocks past the image edge do not)
    assert np.isfinite(dens).sum() == int(prior["in_footprint"].sum())


def test_choose_movers_takes_the_low_prior_end_and_is_deterministic(grid):
    foot, cat = grid
    dens = fault_density_prior(cat, foot, block_px=10, sigma_px=10)["dens"]
    nbx = dens.shape[1]
    ys = np.repeat(np.arange(0, 60, 5), 1)
    xs = np.arange(0, 60, 5)
    ys, xs = np.meshgrid(ys, xs, indexing="ij")
    ys, xs = ys.ravel(), xs.ravel()
    keys = block_keys(ys, xs, 10, nbx)
    dot_prior = dens.ravel()[keys]

    movers, stats = choose_movers(ys, xs, dens, 10, 12, "up")
    assert len(movers) == 12
    assert dot_prior[movers].mean() <= dot_prior.mean()
    assert dot_prior[movers].max() <= np.quantile(dot_prior, 0.25)

    movers_dn, _ = choose_movers(ys, xs, dens, 10, 12, "dn")
    assert dot_prior[movers_dn].mean() >= dot_prior.mean()

    again, _ = choose_movers(ys, xs, dens, 10, 12, "up")
    assert np.array_equal(movers, again)
    assert stats["source_prior_cut"] <= dots_cut(dot_prior, 12)


def dots_cut(dot_prior, n):
    return np.sort(dot_prior)[n - 1]


def test_place_movers_respects_the_spacing_floor_and_count(grid):
    foot, cat = grid
    dens = fault_density_prior(cat, foot, block_px=10, sigma_px=10)["dens"]
    nbx = dens.shape[1]
    # a lattice of candidates inside block (6, 6) on a 2.5 px pitch, so a >= 2.0 px
    # floor admits exactly one dot per lattice cell
    cy, cx = np.meshgrid(np.arange(55, 60, 3), np.arange(55, 60, 3), indexing="ij")
    cy, cx = cy.ravel(), cx.ravel()
    d0 = np.full(len(cy), 9.0)
    dest_order = [int(5 * nbx + 5)]
    py, px, stats = place_movers(dens, 10, dest_order, cy, cx, d0, 4, 2.0)
    assert len(py) == 4
    pts = np.c_[py, px].astype(float)
    d = np.hypot(pts[:, None, 0] - pts[None, :, 0], pts[:, None, 1] - pts[None, :, 1])
    np.fill_diagonal(d, np.inf)
    assert d.min() >= 2.0 - 1e-9
    assert stats["n_destination_blocks"] == 1


def test_place_movers_fails_loudly_when_capacity_is_exhausted(grid):
    foot, cat = grid
    dens = fault_density_prior(cat, foot, block_px=10, sigma_px=10)["dens"]
    nbx = dens.shape[1]
    cy, cx = np.array([55, 56]), np.array([55, 55])   # two candidates, 1 px apart
    d0 = np.full(2, 9.0)
    with pytest.raises(RuntimeError, match="capacity exhausted"):
        place_movers(dens, 10, [int(5 * nbx + 5)], cy, cx, d0, 2, 2.0)


def test_density_cv_reports_both_definitions():
    foot = np.ones((40, 40), bool)
    dots = np.zeros((40, 40), bool)
    dots[[0, 0, 2, 2], [0, 2, 0, 2]] = True   # four dots in block (0, 0)
    cv = density_cv(dots, foot, block_px=10)
    assert cv["n_blocks_occupied"] == 1
    assert cv["cv_occupied"] == pytest.approx(0.0, abs=1e-12)
    assert cv["cv_all_eligible"] > 0.0
    assert cv["max_dots_per_block"] == 4
