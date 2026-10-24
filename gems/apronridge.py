"""APRONRIDGE lane surface: Thin-Cover Piedmont Accommodation Apron & RTP-Curvature 1D Ridges.

Geology & Geophysics
--------------------
In Great Basin Basin-and-Range extension (Faulds & Hinz, 2015; Siler et al.,
2019; USGS GeoDAWN / DOE INGENIOUS), active Quaternary range-front splays and
synthetic piedmont step-faults reach the surface inside the *piedmont
accommodation apron* -- the structural transition zone where:

1. Detrended elevation (Band 12 ``det_elev``) lies between deep central playas
   and high range crests (suppressing pluvial Lake Lahontan deep-playa
   shoreline benches at low ``det_elev`` and exhumed pre-Quaternary bedrock
   cliffs at high ``det_elev``).
2. Cenozoic sedimentary cover thickness (Band 15 ``depth_to_base_surf``) is
   thin to moderate (~20-600 m, peaked near 180 m), thin enough for brittle
   basement slip to propagate upward as discrete scarps or shallow-buried
   fault steps rather than dissipating into diffuse compaction within >1.5 km
   central graben muds.
3. Regional footwall-to-hanging-wall density transition (Band 5
   ``iso_grav_anom_slope``) corroborates structural accommodation.

Within this accommodation-apron habitat ``H_apron(x)``, unmapped faults
express along 100 m crisp 1D linear edges in at least one of two complementary
physical channels:

* **Surface Alluvial Scarp Channel** ``R_scarp(x)``: coherent break-in-slope
  ``pct_rank(||grad Band19||) * coherence(Band12)`` (catching same-lithology
  Quaternary alluvial scarps invisible to potential-field worms).
* **Subsurface Inclination-Corrected Magnetic Channel** ``R_rtp(x)``:
  ``pct_rank(||grad Band2_rtp||) * pct_rank(-Band6_tc) * coherence(Band2_rtp)``
  (catching fan-washed shallow basement/volcanic offsets directly vertically
  above the contact via Reduced-to-Pole Band 2 + Band 6 curvature, avoiding
  the ~400 m southward dipolar phase shift of raw TMI at ~40 deg N latitude).

Taking the fuzzy union ``max(R_scarp, 0.85 * R_rtp)`` inside ``H_apron`` and
extracting 1D directional non-maximum-suppressed ridge crests prevents 2D blob
clustering under spaced placement.

Zero catalogue information enters any function in this module.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

from .breakline import (
    lane_surface as breakline_lane_surface,
    percentile_rank,
    spaced_top_mask,
    structure_tensor_coherence,
)

__all__ = [
    "COVER_CENTER_M",
    "COVER_LOG_SIGMA",
    "RTP_CHANNEL_WEIGHT",
    "apron_habitat",
    "directional_ridge_1d",
    "lane_surface",
    "percentile_rank",
    "rtp_curvature_ridge",
    "spaced_top_mask",
    "structure_tensor_coherence",
]

COVER_CENTER_M = 180.0
COVER_LOG_SIGMA = 1.35
RTP_CHANNEL_WEIGHT = 0.85
DERIV_SIGMA_PX = 1.0


def _clean(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Replace non-finite or outside-valid cells with the valid median (float32)."""
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    fill = float(np.median(a[m])) if m.any() else 0.0
    return np.where(m, a, np.float32(fill)).astype(np.float32)


def _grad_mag(a: np.ndarray, valid: np.ndarray, sigma: float = DERIV_SIGMA_PX) -> np.ndarray:
    sm = _clean(a, valid)
    if sigma > 0.0:
        sm = gaussian_filter(sm, float(sigma))
    gy, gx = np.gradient(sm)
    return np.hypot(gy, gx).astype(np.float32)


def apron_habitat(
    det_elev: np.ndarray,
    depth_to_base: np.ndarray,
    grav_slope: np.ndarray,
    valid: np.ndarray,
    *,
    cover_center_m: float = COVER_CENTER_M,
    cover_log_sigma: float = COVER_LOG_SIGMA,
) -> dict[str, np.ndarray]:
    """Compute the Thin-Cover Piedmont Accommodation Apron envelope ``H_apron`` in [0, 1]."""
    valid = np.asarray(valid, bool)
    z = _clean(det_elev, valid)
    db = np.maximum(_clean(depth_to_base, valid), 0.0)

    if valid.any():
        p33, p67 = np.percentile(z[valid], [33.333333, 66.666667])
    else:
        p33, p67 = -100.0, 100.0
    z0 = float(0.5 * (p33 + p67))
    sz = float(max(p67 - p33, 1.0))

    pied_env = np.exp(-0.5 * ((z - z0) / sz) ** 2).astype(np.float32)
    log_db = np.log1p(db).astype(np.float32)
    cover_env = np.exp(
        -0.5 * ((log_db - float(np.log1p(cover_center_m))) / float(cover_log_sigma)) ** 2
    ).astype(np.float32)
    grav_env = (0.50 + 0.50 * percentile_rank(grav_slope, valid)).astype(np.float32)

    h_apron = np.where(valid, pied_env * cover_env * grav_env, 0.0).astype(np.float32)
    return {
        "pied_env": np.where(valid, pied_env, 0.0).astype(np.float32),
        "cover_env": np.where(valid, cover_env, 0.0).astype(np.float32),
        "grav_env": np.where(valid, grav_env, 0.0).astype(np.float32),
        "H_apron": h_apron,
        "p33_det_elev_m": float(p33),
        "p67_det_elev_m": float(p67),
    }


def rtp_curvature_ridge(
    rtp: np.ndarray,
    tc: np.ndarray,
    valid: np.ndarray,
    *,
    deriv_sigma: float = DERIV_SIGMA_PX,
) -> dict[str, np.ndarray]:
    """Inclination-corrected RTP horizontal-gradient x inverted ``tc`` x RTP coherence."""
    valid = np.asarray(valid, bool)
    rtp_grad_pct = percentile_rank(_grad_mag(rtp, valid, sigma=deriv_sigma), valid)
    inv_tc_pct = percentile_rank(-_clean(tc, valid), valid)
    coh_rtp = structure_tensor_coherence(rtp, valid)
    r_rtp = np.where(valid, rtp_grad_pct * inv_tc_pct * coh_rtp, 0.0).astype(np.float32)
    return {
        "rtp_grad_pct": rtp_grad_pct,
        "inv_tc_pct": inv_tc_pct,
        "coh_rtp": coh_rtp,
        "R_rtp": r_rtp,
    }


def directional_ridge_1d(surface: np.ndarray, valid: np.ndarray | None = None) -> np.ndarray:
    """Boolean 1D crest mask: strict/weak local maximum across >=1 of 4 principal cross-axes."""
    s = np.asarray(surface, dtype=np.float32)
    p = np.pad(s, 1, mode="edge")
    c = p[1:-1, 1:-1]
    crest = (
        ((c >= p[:-2, 1:-1]) & (c > p[2:, 1:-1]))
        | ((c > p[:-2, 1:-1]) & (c >= p[2:, 1:-1]))
        | ((c >= p[1:-1, :-2]) & (c > p[1:-1, 2:]))
        | ((c > p[1:-1, :-2]) & (c >= p[1:-1, 2:]))
        | ((c >= p[:-2, :-2]) & (c > p[2:, 2:]))
        | ((c > p[:-2, :-2]) & (c >= p[2:, 2:]))
        | ((c >= p[:-2, 2:]) & (c > p[2:, :-2]))
        | ((c > p[:-2, 2:]) & (c >= p[2:, :-2]))
    )
    if valid is not None:
        crest &= np.asarray(valid, bool)
    return crest & (s > 0.0)


def lane_surface(
    det_elev: np.ndarray,
    det_elev_slope: np.ndarray,
    depth_to_base: np.ndarray,
    grav_slope: np.ndarray,
    rtp: np.ndarray,
    tc: np.ndarray,
    valid: np.ndarray,
    *,
    rtp_weight: float = RTP_CHANNEL_WEIGHT,
) -> dict[str, np.ndarray]:
    """Build the full catalogue-free APRONRIDGE surface, ridge mask, and diagnostics."""
    valid = np.asarray(valid, bool)
    hab = apron_habitat(det_elev, depth_to_base, grav_slope, valid)
    bl = breakline_lane_surface(det_elev, det_elev_slope, valid)
    rtp_ch = rtp_curvature_ridge(rtp, tc, valid)

    r_scarp = bl["L_raw"]
    r_rtp = rtp_ch["R_rtp"]
    edge_union = np.maximum(r_scarp, np.float32(rtp_weight) * r_rtp).astype(np.float32)
    s_raw = np.where(valid, hab["H_apron"] * edge_union, 0.0).astype(np.float32)
    s_pct = percentile_rank(s_raw, valid)
    ridge = directional_ridge_1d(s_raw, valid)

    return {
        "H_apron": hab["H_apron"],
        "R_scarp": r_scarp,
        "R_rtp": r_rtp,
        "S_raw": s_raw,
        "S_pct": s_pct,
        "ridge_1d": ridge,
        "valid_all": valid,
        "p33_det_elev_m": hab["p33_det_elev_m"],
        "p67_det_elev_m": hab["p67_det_elev_m"],
    }
