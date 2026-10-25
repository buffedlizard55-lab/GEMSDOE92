"""LISTRICLAG lane: dip-displacement-tolerant surface/subsurface edge coupling.

Basin-and-Range normal faults dip 45-60 degrees, so the buried basement
density step (depth-to-basement gradient, confirmed by isostatic gravity
gradients) images 200-800 m basinward of the surface scarp trace.  Strictly
co-located lanes multiply terrain and basement evidence at the same pixel and
therefore vanish exactly where this lag is largest -- which is also where the
scarp-mapped USGS/INGENIOUS catalogue is blind.  LISTRICLAG couples the
basement-edge evidence at a pixel with the *maximum* terrain scarp evidence
inside a 2.8-8 px (280-800 m) annulus around it.

Bands (1-based in the pinned 19-band stack; descriptions read from the file):
  11 iso_grav_anom_vg, 12 det_elev, 15 depth_to_base_surf,
  18 iso_grav_anom_hg, 19 det_elev_slope.

Label-free: the fault catalogue never enters feature construction.

Named non-fault mimics: fan-toe/piedmont junctions beside basin-margin onlap
density contacts, pluvial Lake Lahontan shoreline risers near lithologic
density steps, DEM seams near gravity survey edges.
"""
from __future__ import annotations

import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter, gaussian_gradient_magnitude, maximum_filter

SENTINEL = -3.4028235e38
BAND = {"grav_vg": 11, "elevation": 12, "basement": 15, "grav_hg": 18, "slope": 19}
RING_OUTER_PX = 8.0   # 800 m: max updip offset for a 45 deg listric fault rooted ~1 km
RING_INNER_PX = 2.8   # same floor as the dot-spacing rule; "near but not here"


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


def annulus_footprint(inner: float = RING_INNER_PX, outer: float = RING_OUTER_PX) -> np.ndarray:
    r = int(np.ceil(outer))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    d = np.hypot(yy, xx)
    return (d >= inner) & (d <= outer)


def terrain_evidence(elev: np.ndarray, slope: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Multi-scale scarp evidence: persistent curvature x local slope break."""
    s = np.log1p(np.maximum(slope, 0))
    curv2 = np.abs(gaussian_filter(elev, 2.0, order=(2, 0)) +
                   gaussian_filter(elev, 2.0, order=(0, 2)))
    curv6 = np.abs(gaussian_filter(elev, 6.0, order=(2, 0)) +
                   gaussian_filter(elev, 6.0, order=(0, 2)))
    slope_break = np.abs(s - gaussian_filter(s, 5.0))
    return percentile_rank(np.minimum(percentile_rank(curv2, valid),
                                      percentile_rank(curv6, valid)) *
                           percentile_rank(slope_break, valid), valid)


def lane_surface(stack_path: str, footprint: np.ndarray) -> dict[str, np.ndarray]:
    """Return auditable single-feature canaries plus the coupled surfaces.

    Keys: ``valid``, ``terrain_local``, ``terrain_ring``, ``basement_edge``,
    ``grav_edge``, ``S`` (LISTRICLAG, ring-coupled) and ``S_local``
    (co-located ablation; identical recipe with the annulus removed).
    """
    arrays, masks = {}, []
    for name, band in BAND.items():
        arrays[name], ok = clean(read_band(stack_path, band), footprint)
        masks.append(ok)
    valid = np.logical_and.reduce(masks) & footprint

    terrain_local = terrain_evidence(arrays["elevation"], arrays["slope"], valid)

    # Dip-displacement tolerance: strongest scarp evidence 2.8-8 px away.
    ring = maximum_filter(terrain_local, footprint=annulus_footprint())
    terrain_ring = percentile_rank(np.where(valid, ring, 0.0), valid)

    # Buried basement step, confirmed by gravity gradients (edge-of-density).
    basement_edge = percentile_rank(
        gaussian_gradient_magnitude(arrays["basement"], sigma=3.0), valid)
    grav_edge = percentile_rank(
        percentile_rank(np.abs(gaussian_filter(arrays["grav_hg"], 1.5)), valid) *
        percentile_rank(np.abs(gaussian_filter(arrays["grav_vg"], 1.5)), valid), valid)

    def couple(terrain_term: np.ndarray) -> np.ndarray:
        s = np.cbrt(np.maximum(terrain_term * basement_edge * grav_edge, 0)).astype(np.float32)
        s[~valid] = 0
        return s

    return {
        "valid": valid,
        "terrain_local": terrain_local,
        "terrain_ring": terrain_ring,
        "basement_edge": basement_edge,
        "grav_edge": grav_edge,
        "S": couple(terrain_ring),
        "S_local": couple(terrain_local),
    }
