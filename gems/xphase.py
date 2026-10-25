"""XPHASE lane: MT–gravity transverse-phase concordance.

Geology
-------
Blind Great Basin geothermal feeders (Faulds & Hinz 2015; Wannamaker et al.)
typically have *no* Quaternary scarp.  They still produce two independent
potential-field signatures that share strike but are offset across-strike by
the finite width of a damage zone / clay-cap margin:

* Band 13 ``iso_grav_anom`` — density contact (basement vs basin fill).
* Band 17 ``cond_surf`` — magnetotelluric conductivity; hydrothermal smectite
  clay caps and upflow conduits create a *lateral* resistivity boundary, not
  a playa-interior conductance maximum.

A lithologic contact that is *not* a permeable fault tends to make the two
gradient peaks *coincident*.  A finite-width feeder tends to make them
parallel in strike (2θ orientation agreement) with a 100–300 m transverse
lag.  Intermediate Band 15 cover (roughly 50–1,200 m) selects concealed
strands; high Band 19 slope is suppressed so mapped range-front cliffs do
not dominate emission.

Zero catalogue information enters any function in this module.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates

from .breakline import percentile_rank, structure_tensor_coherence
from .geotension import directional_ridge_1d

__all__ = [
    "COVER_CENTER_M",
    "COVER_LOG_SIGMA",
    "LAG_PX",
    "directional_ridge_1d",
    "lane_surface",
    "percentile_rank",
    "transverse_phase",
    "xphase_components",
]

COVER_CENTER_M = 250.0
COVER_LOG_SIGMA = 1.40
DERIV_SIGMA_PX = 1.5
LAG_PX = 2.0
EPS = 1.0e-6


def _clean(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    fill = float(np.median(a[m])) if m.any() else 0.0
    return np.where(m, a, np.float32(fill)).astype(np.float32)


def _grad(field: np.ndarray, valid: np.ndarray, sigma: float = DERIV_SIGMA_PX):
    sm = gaussian_filter(_clean(field, valid), float(sigma))
    gy, gx = np.gradient(sm)
    return gy.astype(np.float32), gx.astype(np.float32)


def transverse_phase(
    mag_mt: np.ndarray,
    mag_gr: np.ndarray,
    ny: np.ndarray,
    nx: np.ndarray,
    *,
    lag_px: float = LAG_PX,
) -> np.ndarray:
    """Prefer gravity-gradient peaks offset along the MT normal vs coincident.

    Samples ``mag_gr`` at ±``lag_px`` along the unit MT gradient ``(ny, nx)``.
    ``lag = max(plus, minus) / (mag_gr + max(plus, minus) + eps)`` is near 1
    when the gravity peak is shifted across-strike and near 0.5 when the two
    peaks coincide.
    """
    mag_mt = np.asarray(mag_mt, dtype=np.float32)
    mag_gr = np.asarray(mag_gr, dtype=np.float32)
    ny = np.asarray(ny, dtype=np.float32)
    nx = np.asarray(nx, dtype=np.float32)
    h, w = mag_gr.shape
    yy, xx = np.indices((h, w), dtype=np.float32)
    plus = map_coordinates(
        mag_gr, [yy + float(lag_px) * ny, xx + float(lag_px) * nx],
        order=1, mode="nearest",
    ).astype(np.float32)
    minus = map_coordinates(
        mag_gr, [yy - float(lag_px) * ny, xx - float(lag_px) * nx],
        order=1, mode="nearest",
    ).astype(np.float32)
    off = np.maximum(plus, minus)
    lag = off / (mag_gr + off + np.float32(EPS))
    return np.clip(lag, 0.0, 1.0).astype(np.float32)


def xphase_components(
    cond_surf: np.ndarray,
    iso_grav: np.ndarray,
    depth_to_base: np.ndarray,
    det_elev_slope: np.ndarray,
    valid: np.ndarray,
    *,
    cover_center_m: float = COVER_CENTER_M,
    cover_log_sigma: float = COVER_LOG_SIGMA,
    lag_px: float = LAG_PX,
    apply_lag: bool = True,
) -> dict[str, np.ndarray]:
    """Catalogue-free MT–gravity phase components (all in [0, 1] where ranked)."""
    valid = np.asarray(valid, bool)
    log_cond = np.log1p(np.maximum(_clean(cond_surf, valid), 0.0)).astype(np.float32)
    grav = _clean(iso_grav, valid)
    gy_mt, gx_mt = _grad(log_cond, valid)
    gy_gr, gx_gr = _grad(grav, valid)
    mag_mt = np.hypot(gy_mt, gx_mt).astype(np.float32)
    mag_gr = np.hypot(gy_gr, gx_gr).astype(np.float32)
    nrm = mag_mt + np.float32(EPS)
    ny = (gy_mt / nrm).astype(np.float32)
    nx = (gx_mt / nrm).astype(np.float32)

    # 2θ orientation agreement: 1 if gradients are parallel or anti-parallel
    # (same strike), 0 if perpendicular.
    dot = (gx_mt * gx_gr + gy_mt * gy_gr).astype(np.float32)
    den = mag_mt * mag_gr + np.float32(EPS)
    cos_d = np.clip(dot / den, -1.0, 1.0)
    orient = ((1.0 + (2.0 * cos_d * cos_d - 1.0)) * 0.5).astype(np.float32)

    if apply_lag:
        lag = transverse_phase(mag_mt, mag_gr, ny, nx, lag_px=lag_px)
    else:
        lag = np.ones(mag_mt.shape, dtype=np.float32)

    db = np.maximum(_clean(depth_to_base, valid), 0.0)
    log_db = np.log1p(db).astype(np.float32)
    cover = np.exp(
        -0.5 * ((log_db - float(np.log1p(cover_center_m))) / float(cover_log_sigma)) ** 2
    ).astype(np.float32)

    slope_pct = percentile_rank(_clean(det_elev_slope, valid), valid)
    slope_suppress = (1.0 - 0.85 * slope_pct).astype(np.float32)

    coh = structure_tensor_coherence(log_cond, valid)
    mt_pct = percentile_rank(mag_mt, valid)
    gr_pct = percentile_rank(mag_gr, valid)
    return {
        "mag_mt": mag_mt,
        "mag_gr": mag_gr,
        "mt_pct": mt_pct,
        "gr_pct": gr_pct,
        "orient": np.where(valid, orient, 0.0).astype(np.float32),
        "lag": np.where(valid, lag, 0.0).astype(np.float32),
        "cover": np.where(valid, cover, 0.0).astype(np.float32),
        "slope_suppress": np.where(valid, slope_suppress, 0.0).astype(np.float32),
        "coherence": coh,
        "log_cond": log_cond,
    }


def lane_surface(
    cond_surf: np.ndarray,
    iso_grav: np.ndarray,
    depth_to_base: np.ndarray,
    det_elev_slope: np.ndarray,
    valid: np.ndarray,
    *,
    apply_lag: bool = True,
    lag_px: float = LAG_PX,
) -> dict[str, np.ndarray]:
    """Build S_xphase, 1-D ridge mask, and diagnostics. Catalogue-free."""
    valid = np.asarray(valid, bool)
    c = xphase_components(
        cond_surf, iso_grav, depth_to_base, det_elev_slope, valid,
        apply_lag=apply_lag, lag_px=lag_px,
    )
    s_raw = np.where(
        valid,
        c["mt_pct"] * c["gr_pct"] * c["orient"] * c["cover"]
        * c["lag"] * c["slope_suppress"] * (0.35 + 0.65 * c["coherence"]),
        0.0,
    ).astype(np.float32)
    s_pct = percentile_rank(s_raw, valid)
    ridge = directional_ridge_1d(s_raw, valid)
    out = dict(c)
    out.update({
        "S_raw": s_raw,
        "S_pct": s_pct,
        "ridge_1d": ridge,
        "valid_all": valid,
        "apply_lag": np.array([1.0 if apply_lag else 0.0], dtype=np.float32),
    })
    return out
