"""DRAINAGE-KNICK lane: multi-scale terrain knickzone x buried-basement step.

This label-free surface targets scarpless faults expressed as a narrow, persistent
change in detrended-elevation slope, coincident with a depth-to-basement edge and
geodetic shear. It uses only bands 7, 12, 15 and 19 of the pinned feature stack;
the fault catalogue is deliberately absent from feature construction.

Non-fault mimic: resistant stratigraphic contacts, pluvial shorelines, fan toes,
and DEM seams.
"""
from __future__ import annotations

import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter, gaussian_gradient_magnitude

SENTINEL = -3.4028235e38
BAND = {"shear": 7, "elevation": 12, "basement": 15, "slope": 19}


def read_band(path: str, band: int) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(band).astype(np.float32)


def clean(a: np.ndarray, footprint: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ok = footprint & np.isfinite(a) & (a > SENTINEL + 1e6)
    fill = float(np.median(a[ok])) if ok.any() else 0.0
    return np.where(ok, a, fill).astype(np.float32), ok


def percentile_rank(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    out = np.zeros(a.shape, np.float32)
    vals = np.asarray(a, np.float32)[valid]
    if not vals.size:
        return out
    q = np.quantile(vals, np.linspace(0, 1, 1001))
    out[valid] = np.interp(vals, q, np.linspace(0, 1, 1001)).astype(np.float32)
    return out


def lane_surface(stack_path: str, footprint: np.ndarray) -> dict[str, np.ndarray]:
    """Return three auditable single-feature canaries and their product surface."""
    arrays, masks = {}, []
    for name, band in BAND.items():
        arrays[name], ok = clean(read_band(stack_path, band), footprint)
        masks.append(ok)
    valid = np.logical_and.reduce(masks) & footprint

    # Scale persistence suppresses one-pixel DEM texture and broad regional tilt.
    elev = arrays["elevation"]
    slope = np.log1p(np.maximum(arrays["slope"], 0))
    curv2 = np.abs(gaussian_filter(elev, 2.0, order=(2, 0)) +
                   gaussian_filter(elev, 2.0, order=(0, 2)))
    curv6 = np.abs(gaussian_filter(elev, 6.0, order=(2, 0)) +
                   gaussian_filter(elev, 6.0, order=(0, 2)))
    slope_break = np.abs(slope - gaussian_filter(slope, 5.0))
    terrain = percentile_rank(np.minimum(percentile_rank(curv2, valid),
                                         percentile_rank(curv6, valid)) *
                              percentile_rank(slope_break, valid), valid)

    basement_edge = percentile_rank(
        gaussian_gradient_magnitude(arrays["basement"], sigma=3.0), valid)
    shear = percentile_rank(np.maximum(arrays["shear"], 0), valid)

    # Geometric mean avoids underflow while requiring all three mechanisms.
    surface = np.cbrt(np.maximum(terrain * basement_edge * shear, 0)).astype(np.float32)
    surface[~valid] = 0
    return {"valid": valid, "terrain_persistence": terrain,
            "basement_edge": basement_edge, "shear": shear, "S": surface}
