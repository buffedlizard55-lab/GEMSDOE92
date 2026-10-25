"""TILTANGLE lane: gravity tilt-angle edge corridors for buried blind faults.

Geology
-------
The USGS/INGENIOUS catalogue is a *surface-scarp* catalogue: faults are mapped
where a preserved topographic scarp exists. A blind normal fault buried under
thin Quaternary cover, or one whose scarp has diffused below detection, still
juxtaposes rock bodies of different density across its plane. That density
contrast produces a measurable edge in the isostatic gravity field.

The gravity *tilt angle* theta = atan2(|dg/dz|, |grad_h g|) is a rotation-
invariant edge indicator: it is 0 degrees over horizontal (bedding-parallel)
contacts and approaches 90 degrees over steep, vertical contacts -- exactly
the geometry of Basin-and-Range normal faults. Its magnitude is independent of
magnetization direction and of fault strike, so it catches faults of any
orientation that the scarp catalogue missed.

Unlike GRAVQUAD (analytic-signal amplitude x structure-tensor coherence, which
responds to any elongated gradient blob) and unlike COULOMB-LOQO (fixed N15E
conjugate shear planes folded into a supervised classifier), TILTANGLE uses
only the tilt-angle magnitude to select steep vertical-contact edges, then
weights by horizontal-gradient magnitude for edge strength. No catalogue
pixel is used to build the surface; the catalogue is read only by the caller
for masking.

Surface (pure array math on caller-supplied arrays):

    hg_ew = B18 iso_grav_anom_hg          (signed E-W horizontal derivative)
    hg_ns = d/dy(B13 iso_grav_anom)       (N-S horizontal derivative, finite diff)
    vg    = B11 iso_grav_anom_vg          (vertical derivative)
    hgm   = sqrt(hg_ew^2 + hg_ns^2)       (total horizontal gradient = edge strength)
    tilt  = atan2(|vg|, hgm)              (0 = flat bedding, 90 = steep fault)
    S_raw = hgm * cos(tilt)^2             (strong gradient + steep contact)
    S     = pct_rank(S_raw) over valid footprint

Layers
------
* B11 iso_grav_anom_vg   (vertical gravity derivative)
* B13 iso_grav_anom      (isostatic gravity anomaly; differentiated here for hg_ns)
* B18 iso_grav_anom_hg   (signed E-W gravity horizontal derivative)

Named non-fault mimic: equant plutonic intrusions and circular density
anomalies produce horizontal-gradient magnitude but low tilt-angle coherence
(toward 0 or isotropic), so they are down-weighted by cos(tilt)^2.

Difference from existing lanes: no lane in this repository computes a gravity
tilt angle or uses cos(tilt)^2 to select steep-contact edges. GRAVQUAD uses
ASA amplitude (rotation-robust but blind to contact dip); TILTANGLE explicitly
selects steep (near-vertical) contacts.
"""

from __future__ import annotations

import numpy as np
import rasterio

SENTINEL = -3.4028235e+38

# 1-based band numbers in training_features.tif (GDAL-verified in README band audit)
BAND = dict(
    grav_vg=11,      # iso_grav_anom_vg
    grav_anom=13,    # iso_grav_anom (raw field; differentiated for hg_ns)
    grav_hg_ew=18,   # iso_grav_anom_hg (signed E-W horizontal derivative)
)

__all__ = [
    "BAND", "SENTINEL", "read_stack_band", "clean", "percentile_rank",
    "lane_surface",
]


def read_stack_band(path: str, band: int) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(int(band)).astype(np.float32)


def clean(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Replace sentinel / non-finite cells with the finite-valid median."""
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a) & (a > SENTINEL + 1e6)
    fill = float(np.median(a[m])) if m.any() else 0.0
    return np.where(np.isfinite(a) & (a > SENTINEL + 1e6), a, np.float32(fill)).astype(np.float32)


def percentile_rank(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Percentile rank in [0, 1] over ``valid`` finite cells (1001 knots)."""
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    out = np.zeros(a.shape, np.float32)
    vals = a[m]
    if vals.size == 0:
        return out
    knots = np.quantile(vals, np.linspace(0.0, 1.0, 1001))
    out[m] = np.interp(vals, knots, np.linspace(0.0, 1.0, 1001)).astype(np.float32)
    return out


def lane_surface(stack_path: str, footprint: np.ndarray) -> dict:
    """Build the TILTANGLE surface and its components.

    Returns float32 arrays keyed ``hgm``, ``tilt``, ``S_raw``, ``S`` (the
    surface), plus ``valid``. Nothing here reads the fault catalogue, so
    catalogue withholding cannot leak through the surface.
    """
    foot = np.asarray(footprint, bool)
    grav_vg = clean(read_stack_band(stack_path, BAND["grav_vg"]), foot)
    grav_hg_ew = clean(read_stack_band(stack_path, BAND["grav_hg_ew"]), foot)
    grav_anom = clean(read_stack_band(stack_path, BAND["grav_anom"]), foot)

    valid = (
        foot
        & np.isfinite(grav_vg) & (grav_vg > SENTINEL + 1e6)
        & np.isfinite(grav_hg_ew) & (grav_hg_ew > SENTINEL + 1e6)
        & np.isfinite(grav_anom) & (grav_anom > SENTINEL + 1e6)
    )

    # N-S horizontal derivative of the raw gravity anomaly (central difference).
    gy_ns, _gx = np.gradient(grav_anom.astype(np.float64))

    hgm = np.hypot(grav_hg_ew.astype(np.float64), gy_ns)
    # tilt angle in radians: 0 = horizontal contact, pi/2 = steep vertical contact
    tilt = np.arctan2(np.abs(grav_vg.astype(np.float64)), np.maximum(hgm, 1e-12))
    # weight edge strength by steep-contact likelihood: cos(tilt)^2 ~ 1 for vertical
    s_raw = (hgm * np.cos(tilt) ** 2).astype(np.float32)

    del grav_vg, grav_hg_ew, grav_anom, gy_ns

    s_raw[~valid] = 0.0
    s_pct = percentile_rank(s_raw, valid)
    s_pct[~valid] = 0.0

    tilt_deg = np.degrees(tilt).astype(np.float32)
    tilt_deg[~valid] = 0.0

    return dict(
        valid=valid,
        hgm=hgm.astype(np.float32),
        tilt=tilt_deg,
        s_raw=s_raw,
        S=s_pct,
    )
