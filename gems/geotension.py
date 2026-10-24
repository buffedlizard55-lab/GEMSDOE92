"""GEOTENSION lane surface: Geodetic Dilatation x Second-Invariant x Shear gating piedmont scarp ridges.

Geology & Geophysics
--------------------
In Basin-and-Range extension (Faulds & Hinz 2015; Faulds et al. 2021;
Kreemer et al. 2014; USGS GeoDAWN / DOE INGENIOUS), geothermal
permeability concentrates where the crust is actively opening, not
merely where a topographic step exists. Dilatational step-overs,
relay ramps and fault terminations host ~32% + 25% of Great Basin
geothermal systems (Giddens & Faulds 2025 review).

The 19-band competition stack provides three independent geodetic
strain invariants from GPS/InSAR (Bands 4,7,8):

* Band 8 ``geod_dilaterate`` – dilatation rate (volumetric strain,
  positive = expansion, nstrain/yr)
* Band 4 ``geod_2ndinv`` – second invariant (strain-rate magnitude)
* Band 7 ``geod_shearrate`` – shear rate (angular deformation)

A blind fault beneath 20–600 m of alluvial apron has no scarp to map
and no lithologic contrast for a potential-field worm, yet still
produces a coherent linear strain discontinuity (high B4 + positive B8)
that can be detected at 100 m posting even when the absolute GPS
posting is ~10 km-smoothed, because the second-invariant gradient
localizes along the fault trace. Gating coherent DEM slope-breaks
(``R_scarp`` from Bands 19/12) inside this tension habitat isolates
the subset of topographic lineaments that are currently opening.

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
    "apron_habitat",
    "directional_ridge_1d",
    "geotension_habitat",
    "lane_surface",
    "percentile_rank",
    "spaced_top_mask",
    "structure_tensor_coherence",
]

COVER_CENTER_M = 180.0
COVER_LOG_SIGMA = 1.35
DERIV_SIGMA_PX = 1.0


def _clean(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
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
    valid: np.ndarray,
    *,
    cover_center_m: float = COVER_CENTER_M,
    cover_log_sigma: float = COVER_LOG_SIGMA,
) -> dict[str, np.ndarray]:
    """Piedmont accommodation apron envelope H_apron in [0,1] (det_elev + cover)."""
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
    h_apron = np.where(valid, pied_env * cover_env, 0.0).astype(np.float32)
    return {
        "pied_env": np.where(valid, pied_env, 0.0).astype(np.float32),
        "cover_env": np.where(valid, cover_env, 0.0).astype(np.float32),
        "H_apron": h_apron,
        "p33_det_elev_m": float(p33),
        "p67_det_elev_m": float(p67),
    }


def geotension_habitat(
    dilaterate: np.ndarray,
    second_inv: np.ndarray,
    shearrate: np.ndarray,
    depth_to_base: np.ndarray,
    det_elev: np.ndarray,
    valid: np.ndarray,
    *,
    cover_center_m: float = COVER_CENTER_M,
    cover_log_sigma: float = COVER_LOG_SIGMA,
) -> dict[str, np.ndarray]:
    """Tension habitat H_ten = pct(dilat+) * pct(2ndInv) * (0.5+0.5*pct(shear)) * H_apron."""
    valid = np.asarray(valid, bool)
    # Positive dilatation only: contraction (<0) suppresses open-fracture permeability
    dil_pos = np.maximum(_clean(dilaterate, valid), 0.0)
    dil_pct = percentile_rank(dil_pos, valid)
    inv_pct = percentile_rank(_clean(second_inv, valid), valid)
    shear_pct = percentile_rank(_clean(shearrate, valid), valid)
    # Shear modulates but does not gate: 0.5 floor preserves dilatational openings in low-shear pure extension
    shear_mod = (0.5 + 0.5 * shear_pct).astype(np.float32)
    ten_raw = (dil_pct * inv_pct * shear_mod).astype(np.float32)
    # Gate by piedmont apron (suppress deep playa and high-range clutter)
    hab = apron_habitat(det_elev, depth_to_base, valid,
                        cover_center_m=cover_center_m, cover_log_sigma=cover_log_sigma)
    h_ten = np.where(valid, ten_raw * hab["H_apron"], 0.0).astype(np.float32)
    return {
        "dil_pct": dil_pct,
        "inv_pct": inv_pct,
        "shear_pct": shear_pct,
        "shear_mod": shear_mod,
        "ten_raw": ten_raw,
        "H_ten": h_ten,
        "H_apron": hab["H_apron"],
        "pied_env": hab["pied_env"],
        "cover_env": hab["cover_env"],
        "p33_det_elev_m": hab["p33_det_elev_m"],
        "p67_det_elev_m": hab["p67_det_elev_m"],
    }


def directional_ridge_1d(surface: np.ndarray, valid: np.ndarray | None = None) -> np.ndarray:
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
    dilaterate: np.ndarray,
    second_inv: np.ndarray,
    shearrate: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Build catalogue-free GEOTENSION surface, ridge mask, and diagnostics."""
    valid = np.asarray(valid, bool)
    hab = geotension_habitat(dilaterate, second_inv, shearrate, depth_to_base, det_elev, valid)
    bl = breakline_lane_surface(det_elev, det_elev_slope, valid)
    r_scarp = bl["L_raw"]
    # Strain habitat gates scarp ridges; coherence of dilatation field emphasizes linear strain discontinuities
    coh_dil = structure_tensor_coherence(dilaterate, valid)
    strain_coh = coh_dil.astype(np.float32)
    # Final surface: tension habitat * scarp * strain coherence (keeps only opening, magnitude, linear fabric, and scarp)
    s_raw = np.where(valid, hab["H_ten"] * r_scarp * (0.50 + 0.50 * strain_coh), 0.0).astype(np.float32)
    s_pct = percentile_rank(s_raw, valid)
    ridge = directional_ridge_1d(s_raw, valid)
    return {
        "H_ten": hab["H_ten"],
        "H_apron": hab["H_apron"],
        "ten_raw": hab["ten_raw"],
        "dil_pct": hab["dil_pct"],
        "inv_pct": hab["inv_pct"],
        "shear_pct": hab["shear_pct"],
        "coh_dil": strain_coh,
        "R_scarp": r_scarp,
        "S_raw": s_raw,
        "S_pct": s_pct,
        "ridge_1d": ridge,
        "valid_all": valid,
        "p33_det_elev_m": hab["p33_det_elev_m"],
        "p67_det_elev_m": hab["p67_det_elev_m"],
    }
