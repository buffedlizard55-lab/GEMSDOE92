"""TILTANGLE lane: gravity tilt-angle edge corridors for buried blind faults.

Geological interpretation (corrected 2026-10-25; no raster values changed)
--------------------------------------------------------------------------
The organizer's existing fault catalogue is incomplete and can include faults
without surface scarps. A buried fault could create a gravity contrast, but
an intact lithologic contact or pluton can create the same potential-field
edge. Neither this raster nor a gravity derivative establishes fault dip,
a new fault, or a geothermal resource.

The implemented angle theta = atan2(|dg/dz|, |grad_h g|) is an angle between
*field-derivative magnitudes*, not the dip of a contact or a fault. Theta
approaches 0 when the horizontal gradient dominates and 90 degrees when the
vertical derivative dominates. For hgm > 0, the actual score is
S_raw = hgm * cos(theta)^2 = hgm^3 / (hgm^2 + vg^2). Thus it favors a large
horizontal gradient relative to the vertical derivative; it does not by
itself select steep faults or exclude circular/equant bodies. Earlier comments
and the historical experiment description incorrectly identified theta=90 as
a steep fault while also weighting it toward zero. Those interpretations are
withdrawn without changing the historical code or TIFF.

Unlike GRAVQUAD (analytic-signal amplitude x structure-tensor coherence) and
COULOMB-LOQO (a supervised classifier), this historical lane scores a field
edge by the relative derivative magnitudes. No catalogue pixel is used to
build the surface; the catalogue is read only by the caller for masking.

Surface (pure array math on caller-supplied arrays):

    hg_ew = B18 iso_grav_anom_hg          (signed E-W horizontal derivative)
    hg_ns = d/dy(B13 iso_grav_anom)       (N-S horizontal derivative, finite diff)
    vg    = B11 iso_grav_anom_vg          (vertical derivative)
    hgm   = sqrt(hg_ew^2 + hg_ns^2)       (total horizontal gradient)
    tilt  = atan2(|vg|, hgm)              (0 = horizontal dominates)
    S_raw = hgm * cos(tilt)^2             (horizontal-dominant edge score)
    S     = pct_rank(S_raw) over the implementation's validity mask

Layers
------
* B11 iso_grav_anom_vg   (vertical gravity derivative)
* B13 iso_grav_anom      (isostatic gravity anomaly; differentiated here for hg_ns)
* B18 iso_grav_anom_hg   (signed E-W gravity horizontal derivative)

Named non-fault mimics: plutonic margins and intact lithologic/evaporite
contacts. They can also have large horizontal gradients and are not reliably
rejected by cos(tilt)^2; require independent geological controls. This is a
historical research lane, not a validated, newly promoted fault model.
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
    # Angle of derivative magnitudes, NOT a contact/fault dip estimate:
    # 0 = horizontal gradient dominates; pi/2 = vertical derivative dominates.
    tilt = np.arctan2(np.abs(grav_vg.astype(np.float64)), np.maximum(hgm, 1e-12))
    # S_raw = hgm^3 / (hgm^2 + vg^2) for hgm > 0; this does not select fault dip.
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
