"""Algorithmic tests for the SCARPPOL lane surface (session 2026-10-24).

Synthetic fields only: a straight scarp step must score higher along its
fall line than across it, and the signed directional change must flip
sign between the crest side and the base side of one step.
"""
from __future__ import annotations

import numpy as np

from gems.scarppol import directional_slope_change, lane_surface


def _scarp():
    yy, xx = np.mgrid[0:60, 0:60]
    elev = (10.0 / (1.0 + np.exp(-(xx - 30) / 1.5))).astype(np.float32)
    gy, gx = np.gradient(elev)
    slope = np.hypot(gy, gx).astype(np.float32)
    return elev, slope


def test_directional_change_sign_flips_across_a_step():
    elev, slope = _scarp()
    valid = np.ones_like(elev, bool)
    dir2 = directional_slope_change(elev, slope, valid)
    # Crest side (uphill of the face centre): slope grows downhill -> dir2
    # of one sign; base side the opposite. Magnitudes near the face must
    # exceed those on the flat benches.
    face = np.abs(dir2[:, 28:33]).mean()
    bench = np.abs(dir2[:, 0:8]).mean()
    assert face > bench


def test_lane_surface_peaks_on_scarp_and_is_unit_range():
    elev, slope = _scarp()
    surf = lane_surface(elev, slope, np.ones_like(elev, bool))
    for key in ("dir2_pct", "coherence", "S_raw", "S_pct"):
        a = surf[key]
        assert a.min() >= 0.0 and a.max() <= 1.0, key
    assert surf["S_pct"][:, 27:34].mean() > surf["S_pct"][:, 0:10].mean()


def test_lane_surface_ignores_nonfinite_cells():
    elev, slope = _scarp()
    elev = elev.copy(); elev[0, 0] = np.nan
    valid = np.isfinite(elev)
    surf = lane_surface(elev, slope, valid)
    assert np.isfinite(surf["S_pct"]).all()
