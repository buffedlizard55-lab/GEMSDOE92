"""VARIO lane — three catalogue-free feature families not used by any prior lane.

Pre-registration: docs/HYPOTHESES_20261025_VARIO.md (Rank 1).

Families
--------
1. ``sv_*`` — directional semivariogram of Band-2 RTP magnetics.
   For lag ``h`` and azimuth ``theta``, the local semivariance is
   ``gamma(h, theta) = 0.5 * G_sigma[(z(x) - z(x + h*theta))^2]`` where
   ``G_sigma`` is a Gaussian localiser (sigma = 3 px).  A fault that offsets
   or rotates shallow magnetic fabric, or whose damage zone destroys fabric
   continuity across strike, gives high across-strike gamma with low
   along-strike gamma even where the RTP amplitude step itself is weak.
   Features: anisotropy ``(gmax - gmin) / (gmean + eps)`` at lags 2 and 4 px,
   each multiplied by a fabric-energy gate ``gmean / (gmean + median_gmean)``
   so flat, fabric-free areas cannot manufacture anisotropy from noise, plus
   the clipped lag ratio ``gmean(4) / gmean(2)`` (fabric roughness break).
   This is a covariance-domain operator: no existing module in this repo
   computes a multi-lag directional semivariogram (``anasig``/``eulerfuse``/
   ``poissonflex`` are pointwise derivative/tilt/source operators;
   ``xphase`` compares phases of two different fields).

2. ``mt_cp_constcover`` — MT change-point at constant cover.
   ``|grad log cond_surf|`` (Band 17, sigma = 2 px) discounted by the local
   basement-depth gradient: ``gC / (1 + gD / p90(gD))`` with
   ``gD = |grad log(depth_to_base + 10)|`` (Band 15).  A conductivity break
   inside a block of near-constant cover thickness cannot be explained by
   cover thickness alone and is the signature of a discrete fluid conduit.
   Existing MT use (``hydroconduit``, ``coulombdm``, ``coulomb_loqo`` col
   ``mt_log_cond_grad``) is the unconditional gradient or the level.

3. ``t10_*`` / ``chi_step`` — USGS 3DEP ~10 m sub-pixel scarp statistics
   already aggregated onto the 100 m competition grid in the pinned
   ``topo_10m_derived_100m_u8.tif`` / ``dem10_chi_100m_i16.tif`` mirrors
   (decoded with :func:`gems.ventscarp._decode_u8_band` and
   :func:`gems.ventscarp.subpixel_scarp_excess`, reused not forked).
   ``ventscarp`` used these inside its own ensemble; they have never been
   columns of the COULOMBLOQO + FAULTNET stack.

Strict zero-leakage invariant: no fault-catalogue array enters any function
in this module.  All normalisation constants are label-free percentiles /
medians over the valid mask.  Named non-fault mimics: lava-flow/intrusive
contacts and flight-line seams (semivariogram anisotropy), playa/aquifer
salinity fronts (MT break), Lake Lahontan shoreline berms (10 m scarp
statistics).  Separation is delegated to the quadrant-blocked LOQO ensemble
and is falsified or supported only by the paired holdout.
"""
from __future__ import annotations

import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter

from .coulomb_loqo import _grad_xy
from .hydroconduit import _clean_valid
from .ventscarp import _decode_u8_band, subpixel_scarp_excess

NEW_FEATURE_NAMES: tuple[str, ...] = (
    "sv_aniso_l2",
    "sv_aniso_l4",
    "sv_lagratio",
    "mt_cp_constcover",
    "t10_excess_max",
    "t10_curv_log",
    "t10_lincoh",
    "t10_slope_std_norm",
    "chi_step_sm",
)

__all__ = [
    "NEW_FEATURE_NAMES",
    "directional_semivariance",
    "semivariogram_features",
    "mt_changepoint_constcover",
    "topo10_features",
]

_DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))  # E, S, SE, SW unit steps


def _sqdiff_shift(z: np.ndarray, dy: int, dx: int) -> np.ndarray:
    """(z(x) - z(x + (dy,dx)))^2 placed at x; 0 where the shifted pixel is off-grid."""
    h, w = z.shape
    out = np.zeros(z.shape, np.float32)
    y0, y1 = max(0, -dy), min(h, h - dy)
    x0, x1 = max(0, -dx), min(w, w - dx)
    diff = z[y0:y1, x0:x1] - z[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    out[y0:y1, x0:x1] = diff * diff
    return out


def directional_semivariance(
    field: np.ndarray,
    valid: np.ndarray,
    lag: int,
    sigma: float = 3.0,
) -> dict[str, np.ndarray]:
    """Local directional semivariances at one lag (4 azimuths) + summaries.

    Returns float32 full-grid arrays: per-direction ``gamma`` stacked in
    ``gammas`` (shape (4,H,W) is *not* retained; see keys), ``gmean``,
    ``gmax``, ``gmin``.  Memory-lean: directions are accumulated, not stacked.
    """
    if lag <= 0:
        raise ValueError("lag must be positive")
    valid_b = np.asarray(valid, bool)
    z = _clean_valid(field, valid_b)
    gsum = np.zeros(z.shape, np.float32)
    gmax = np.full(z.shape, -np.inf, np.float32)
    gmin = np.full(z.shape, np.inf, np.float32)
    for uy, ux in _DIRECTIONS:
        g = (0.5 * gaussian_filter(_sqdiff_shift(z, lag * uy, lag * ux), float(sigma))).astype(np.float32)
        gsum += g
        np.maximum(gmax, g, out=gmax)
        np.minimum(gmin, g, out=gmin)
        del g
    gmean = (gsum / np.float32(len(_DIRECTIONS))).astype(np.float32)
    for a in (gmean, gmax, gmin):
        a[~valid_b] = 0.0
    return dict(gmean=gmean, gmax=gmax, gmin=gmin)


def _gated_anisotropy(sv: dict[str, np.ndarray], valid_b: np.ndarray) -> np.ndarray:
    gmean = sv["gmean"]
    med = float(np.median(gmean[valid_b])) if valid_b.any() else 0.0
    eps = np.float32(0.05 * med + 1e-12)
    aniso = np.clip((sv["gmax"] - sv["gmin"]) / (gmean + eps), 0.0, 2.0)
    gate = gmean / (gmean + np.float32(med + 1e-12))
    out = (aniso * gate).astype(np.float32)
    out[~valid_b] = 0.0
    return out


def semivariogram_features(rtp: np.ndarray, valid: np.ndarray) -> dict[str, np.ndarray]:
    """Three RTP semivariogram features (lags 2 and 4 px). Catalogue-free."""
    valid_b = np.asarray(valid, bool)
    sv2 = directional_semivariance(rtp, valid_b, lag=2)
    sv4 = directional_semivariance(rtp, valid_b, lag=4)
    med2 = float(np.median(sv2["gmean"][valid_b])) if valid_b.any() else 0.0
    ratio = np.clip(sv4["gmean"] / (sv2["gmean"] + np.float32(0.05 * med2 + 1e-12)), 0.0, 5.0).astype(np.float32)
    ratio[~valid_b] = 0.0
    return dict(
        sv_aniso_l2=_gated_anisotropy(sv2, valid_b),
        sv_aniso_l4=_gated_anisotropy(sv4, valid_b),
        sv_lagratio=ratio,
    )


def mt_changepoint_constcover(cond_surf: np.ndarray, depth_to_base: np.ndarray,
                              valid: np.ndarray) -> np.ndarray:
    """|grad log cond| discounted where basement-depth gradient is large.

    Label-free scale: depth-gradient magnitudes are divided by their 90th
    percentile over ``valid`` before discounting, so the feature is
    dimensionless apart from the conductivity-gradient factor itself.
    """
    valid_b = np.asarray(valid, bool)
    cond = np.maximum(_clean_valid(cond_surf, valid_b), np.float32(1e-6))
    logc = np.log(cond).astype(np.float32)
    del cond
    cy, cx = _grad_xy(logc, valid_b, sigma=2.0)
    del logc
    g_cond = np.hypot(cy, cx).astype(np.float32)
    del cy, cx
    depth = np.maximum(_clean_valid(depth_to_base, valid_b), np.float32(0.0))
    logd = np.log(depth + np.float32(10.0)).astype(np.float32)
    del depth
    dy, dx = _grad_xy(logd, valid_b, sigma=2.0)
    del logd
    g_depth = np.hypot(dy, dx).astype(np.float32)
    del dy, dx
    scale = float(np.percentile(g_depth[valid_b], 90.0)) if valid_b.any() else 0.0
    scale = max(scale, 1e-12)
    out = (g_cond / (1.0 + g_depth / np.float32(scale))).astype(np.float32)
    out[~valid_b] = 0.0
    return out


def _slope100_deg(det_elev_slope: np.ndarray, valid_b: np.ndarray) -> np.ndarray:
    """100 m slope in degrees, using the same scale check as gems.ventscarp."""
    s = _clean_valid(det_elev_slope, valid_b)
    p99 = float(np.percentile(s[valid_b], 99.0)) if valid_b.any() else 0.0
    if p99 <= 2.5:  # rise/run
        return np.rad2deg(np.arctan(np.maximum(s, 0.0))).astype(np.float32)
    return np.maximum(s, 0.0).astype(np.float32)


def topo10_features(topo10_path, dem10_chi_path, det_elev_slope: np.ndarray,
                    valid: np.ndarray) -> dict[str, np.ndarray]:
    """Five 10 m-derived features decoded from the pinned uint8/int16 mirrors.

    Band identities are read from the TIFF tags (``q_lo``/``q_hi``) via the
    shared ``gems.ventscarp._decode_u8_band``; band order is the pinned
    manifest order: 1 slope_p90, 2 slope_max, 4 slope_std, 6 curv_prof_absmax,
    7 aspect_coherence, 8 hs_lineament.
    """
    valid_b = np.asarray(valid, bool)
    slope100 = _slope100_deg(det_elev_slope, valid_b)
    with rasterio.open(topo10_path) as ds:
        if ds.count < 8:
            raise ValueError(f"topo10 mirror has {ds.count} bands, expected >= 8")
        s_max = _decode_u8_band(ds, 2)
        s_std = _decode_u8_band(ds, 4)
        curv = _decode_u8_band(ds, 6)
        asp_coh = _decode_u8_band(ds, 7)
        hs_lin = _decode_u8_band(ds, 8)
    excess = subpixel_scarp_excess(s_max, slope100, valid_b)
    del s_max
    curv_log = np.where(valid_b, np.log1p(np.maximum(curv, 0.0)), 0.0).astype(np.float32)
    del curv
    lincoh = np.where(valid_b, asp_coh * hs_lin, 0.0).astype(np.float32)
    del asp_coh, hs_lin
    std_norm = np.where(valid_b, s_std / (1.0 + np.float32(0.25) * slope100), 0.0).astype(np.float32)
    del s_std, slope100
    with rasterio.open(dem10_chi_path) as ds:
        step_raw = ds.read(1).astype(np.float32)
    chi_ok = valid_b & (step_raw > -32000)
    chi = np.where(chi_ok, np.log1p(np.maximum(step_raw, 0.0) * np.float32(0.001)), 0.0).astype(np.float32)
    del step_raw, chi_ok
    chi_sm = np.where(valid_b, gaussian_filter(chi, 1.6), 0.0).astype(np.float32)
    del chi
    return dict(
        t10_excess_max=excess,
        t10_curv_log=curv_log,
        t10_lincoh=lincoh,
        t10_slope_std_norm=std_norm,
        chi_step_sm=chi_sm,
    )
