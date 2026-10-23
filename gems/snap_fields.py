"""Label-free SNAP response fields from pinned training_features bands.

Band identities are taken from the GeoTIFF's own tags (not from memory) and
are re-checked empirically in the session builder:

* Band 05 ``iso_grav_anom_slope`` is isotropic |∇_H g| (non-negative).
* Band 02 ``rtp`` is the signed reduced-to-pole anomaly, *not* a gradient.
  Its isotropic horizontal gradient is derived here by central differences.
* Band 18 ``iso_grav_anom_hg`` is signed ∂g/∂x and is **not** used.

No truth / catalogue labels enter these fields.
"""
from __future__ import annotations

import numpy as np

BAND_RTP = 2
BAND_ISO_GRAV_SLOPE = 5
BAND_ISO_GRAV_ANOM = 13
BAND_ISO_GRAV_HG_SIGNED = 18


def percentile_rank(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Footprint percentile rank in [0, 1]; invalid pixels stay 0."""
    out = np.zeros(a.shape, dtype=np.float32)
    vals = np.asarray(a[valid], dtype=np.float64)
    vals = np.nan_to_num(vals, nan=0.0, posinf=0.0, neginf=0.0)
    if vals.size == 0:
        return out
    knots = np.quantile(vals, np.linspace(0.0, 1.0, 1001))
    out[valid] = np.interp(vals, knots, np.linspace(0.0, 1.0, 1001)).astype(np.float32)
    return out


def isotropic_hg(arr: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Isotropic horizontal gradient magnitude via central differences.

    Pixels whose 4-neighbours are not all valid are left as NaN so a SNAP
    window will not treat a nodata hole as an edge.
    """
    a = np.asarray(arr, dtype=np.float64)
    good = np.asarray(valid, dtype=bool) & np.isfinite(a) & (np.abs(a) < 1e20)
    gy = np.full(a.shape, np.nan, dtype=np.float64)
    gx = np.full(a.shape, np.nan, dtype=np.float64)
    both_y = good[2:, :] & good[:-2, :]
    both_x = good[:, 2:] & good[:, :-2]
    gy[1:-1, :][both_y] = (a[2:, :][both_y] - a[:-2, :][both_y]) * 0.5
    gx[:, 1:-1][both_x] = (a[:, 2:][both_x] - a[:, :-2][both_x]) * 0.5
    mag = np.hypot(gy, gx)
    return mag


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.size < 3:
        return float("nan")
    x0, y0 = x - x.mean(), y - y.mean()
    den = float(x0.std() * y0.std())
    if den == 0.0:
        return float("nan")
    return float((x0 * y0).mean() / den)
