"""Synthetic unit tests for the MT-CHANGEPOINT lane surface (no competition data)."""
import numpy as np
import pytest

from gems.mt_changepoint import (
    BAND,
    compute_mt_changepoint_surfaces,
)


def _step_field(shape=(240, 240), col=120, lo=1.0, hi=10.0):
    f = np.full(shape, lo, np.float32)
    f[:, col:] = hi
    return f


def test_band_ids_match_stack_descriptions():
    assert BAND == dict(
        iso_grav_vg=11,
        depth_to_base=15,
        cond_surf=17,
        det_elev_slope=19,
    )


def test_changepoint_peaks_at_conductivity_step():
    foot = np.ones((240, 240), bool)
    cond = _step_field(lo=0.5, hi=25.0)
    base = _step_field(lo=100.0, hi=800.0)
    grav_vg = np.zeros((240, 240), np.float32)
    grav_vg[:, 118:123] = 10.0
    slope = np.full((240, 240), 5.0, np.float32)

    out = compute_mt_changepoint_surfaces(
        cond_surf=cond,
        depth_to_base=base,
        iso_grav_vg=grav_vg,
        det_elev_slope=slope,
        footprint=foot,
    )
    mid = out["S_mtcp"][120, :]
    assert int(np.argmax(mid)) == pytest.approx(120, abs=6)
    assert mid[120] > mid[40] and mid[120] > mid[200]


def test_surfaces_finite_unit_range_and_zero_outside_valid():
    foot = np.zeros((240, 240), bool)
    foot[30:-30, 30:-30] = True
    rng = np.random.default_rng(42)
    kw = {
        "cond_surf": np.maximum(rng.normal(5, 2, (240, 240)).astype(np.float32), 0.1),
        "depth_to_base": rng.normal(300, 100, (240, 240)).astype(np.float32),
        "iso_grav_vg": rng.normal(0, 5, (240, 240)).astype(np.float32),
        "det_elev_slope": np.maximum(rng.normal(4, 1, (240, 240)).astype(np.float32), 0.0),
    }
    kw["depth_to_base"][0, 0] = np.nan
    out = compute_mt_changepoint_surfaces(footprint=foot, **kw)
    for k in ("S_mtcp", "S_mt", "S_base_grav", "cp_mt_pct", "g_base_pct"):
        v = out[k]
        assert np.isfinite(v).all() and v.min() >= 0.0 and v.max() <= 1.0
        assert (v[~out["valid"]] == 0.0).all()
    # Edge erosion test: margins must be invalid
    assert not out["valid"][:20, :].any()
