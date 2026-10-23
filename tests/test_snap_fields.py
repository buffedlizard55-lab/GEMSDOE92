"""Unit tests for SNAP response helpers and ledger reservations. No competition rasters."""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from gems.snap_fields import isotropic_hg, pearson, percentile_rank
from gems.variants import Dots, snap

ROOT = Path(__file__).resolve().parents[1]


def test_percentile_rank_is_monotone_on_valid_pixels() -> None:
    a = np.arange(20, dtype=float).reshape(4, 5)
    valid = np.ones_like(a, dtype=bool)
    valid[0, 0] = False
    r = percentile_rank(a, valid)
    assert r[0, 0] == 0.0
    assert r[0, 1] < r[-1, -1]
    assert r[valid].min() >= 0.0
    assert r[valid].max() <= 1.0 + 1e-6


def test_isotropic_hg_of_a_ramp_is_constant() -> None:
    a = np.tile(np.arange(7, dtype=float), (7, 1))
    valid = np.ones_like(a, dtype=bool)
    mag = isotropic_hg(a, valid)
    interior = mag[2:-2, 2:-2]
    # unit ramp in x: central difference is 1, gy=0, mag=1
    assert np.allclose(interior, 1.0, atol=1e-9)


def test_pearson_of_identical_series_is_one() -> None:
    x = np.linspace(0.0, 1.0, 50)
    assert pearson(x, x) == pytest.approx(1.0)
    assert pearson(x, -x) == pytest.approx(-1.0)


def test_snap_min_gain_refuses_a_tiny_improvement() -> None:
    d = Dots(np.array([10]), np.array([10]), np.array([1.0]))
    response = np.zeros((30, 30))
    response[10, 10] = 0.50
    response[10, 11] = 0.55
    stay = snap(d, response, max_shift=2, min_gain=0.10)
    assert (int(stay.dots.ys[0]), int(stay.dots.xs[0])) == (10, 10)
    move = snap(d, response, max_shift=2, min_gain=0.04)
    assert (int(move.dots.ys[0]), int(move.dots.xs[0])) == (10, 11)


def test_snap_window_is_the_2px_disk_not_the_5x5_square() -> None:
    d = Dots(np.array([10]), np.array([10]), np.array([1.0]))
    response = np.zeros((30, 30))
    response[10, 12] = 5.0   # hypot=2, allowed
    response[12, 12] = 9.0   # hypot=2.828, outside the disk
    v = snap(d, response, max_shift=2)
    assert (int(v.dots.ys[0]), int(v.dots.xs[0])) == (10, 12)
    assert v.stats["max_displacement_px"] <= 2.0 + 1e-9


def test_snap_iso_values_are_unique_in_the_local_ledger() -> None:
    path = ROOT / "ledger" / "submissions.csv"
    if not path.is_file():
        pytest.skip("no ledger")
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    snap_rows = [r for r in rows if r.get("axis") == "SNAP"]
    values = [r.get("value") for r in snap_rows]
    assert len(values) == len(set(values))
    # The three reserved values of this session, once the builder has run.
    reserved = {"iso_g2g10", "rtp_hg2g10", "iso_combo2g10"}
    present = reserved.intersection(values)
    if present:
        assert present == reserved
        for r in snap_rows:
            if r.get("value") in reserved:
                assert r.get("parent") == "h33-h33-2-b2"
                assert r.get("status") == "BUILT"
                assert len(r.get("sha256") or "") == 64
                assert r.get("sha256") != r.get("id")
