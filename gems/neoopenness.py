"""NEO-OPNS lane surface: TPI + LoG curvature openness (2026-10-25).

Geology
-------
Low-angle Quaternary piedmont scarps (<2° fan gradient, 0.5–2 m high) are
invisible to the H19-5 multi-line worm skeleton (no magnetic/gravity
contrast: same lithology, thin cover) and to BREAKLINE's raw slope-break
magnitude (mountain cliffs at 10–25° dominate).  Topographic Position Index

    TPI_500(x) = det_elev(x) − mean_{11×11}(det_elev)(x)

measures local enclosure at 500 m radius: a 0.8 m scarp on a 1° fan still
produces a ±0.4 m TPI dipole, whereas regional slope is removed.  Profile
curvature κ = ∇²(det_elev) peaks at scarp crest/base.  The product
|TPI|·|κ| isolates narrow linear enclosure anomalies; log-slope
||∇ log(slope+1°)|| compresses the dynamic range so 25° cliffs (log 26 =3.26)
do not drown 1° scarps (log 2 =0.69).  Coherence rejects isotropic wash.
A thin-cover piedmont habitat H = H_z·H_c·H_g favors transitional alluvial
aprons (peaked at 120 m cover, not 180 m) while a weak K/Th radiometric
gradient corroboration supports pedogenic carbonate steps.

Nothing here reads the fault catalogue.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter, laplace, sobel

from .breakline import percentile_rank, structure_tensor_coherence

__all__ = [
    "percentile_rank",
    "structure_tensor_coherence",
    "tpi_500",
    "log_slope_break",
    "profile_curvature",
    "piedmont_habitat",
    "radiometric_contact",
    "lane_surface",
]

COVER_CENTER_M = 120.0
COVER_LOG_SIGMA = 1.0
GEO_BOOST_RADIUS_PX = 20  # 2 km
GEO_BOOST_STRENGTH = 0.3


def _clean(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    fill = float(np.median(a[m])) if m.any() else 0.0
    return np.where(np.isfinite(a), a, np.float32(fill)).astype(np.float32)


def tpi_500(det_elev: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """TPI at ~500 m radius (11×11 window at 100 m pixels)."""
    z = _clean(det_elev, valid)
    # uniform_filter with size 11 approximates 550 m radius; reflective padding
    mean11 = uniform_filter(z, size=11, mode="nearest")
    return (z - mean11).astype(np.float32)


def profile_curvature(det_elev: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Discrete Laplacian |∇²z| as profile curvature proxy."""
    z = _clean(det_elev, valid)
    # gaussian pre-smooth 1 px to suppress 1-pixel noise before Laplacian
    sm = gaussian_filter(z, 1.0)
    lap = laplace(sm, mode="nearest")
    return np.abs(lap).astype(np.float32)


def log_slope_break(det_elev_slope: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """||∇ log(slope+1°)|| — compressed break-in-slope magnitude."""
    s = _clean(det_elev_slope, valid)
    # slope may be negative due to detrending slope definition? Clamp.
    s = np.maximum(s, 0.0)
    log_s = np.log1p(s).astype(np.float32)  # log(1 + slope_deg)
    gy, gx = np.gradient(log_s)
    return np.hypot(gy, gx).astype(np.float32)


def piedmont_habitat(
    det_elev: np.ndarray,
    depth_to_base: np.ndarray,
    grav_slope: np.ndarray,
    valid: np.ndarray,
    *,
    cover_center_m: float = COVER_CENTER_M,
    cover_log_sigma: float = COVER_LOG_SIGMA,
) -> dict[str, np.ndarray]:
    """Thin-cover piedmont habitat H = H_z * H_c * H_g in [0,1]."""
    valid = np.asarray(valid, bool)
    z = _clean(det_elev, valid)
    db = np.maximum(_clean(depth_to_base, valid), 0.0)
    grav = _clean(grav_slope, valid)

    # H_z: det_elev Gaussian around median (avoid high range-core and deep playa)
    if valid.any():
        p50 = float(np.median(z[valid]))
        # IQR robust scale
        p75, p25 = np.percentile(z[valid], [75, 25])
        sz = max(float(p75 - p25) / 1.34898, 1.0)
    else:
        p50, sz = 0.0, 100.0
    hz = np.exp(-0.5 * ((z - p50) / sz) ** 2).astype(np.float32)

    # H_c: log-cover Gaussian peaked at cover_center_m
    log_db = np.log1p(db).astype(np.float32)
    lc = float(np.log1p(cover_center_m))
    hc = np.exp(-0.5 * ((log_db - lc) / float(cover_log_sigma)) ** 2).astype(np.float32)

    # H_g: gravity-slope rank boost (accommodation-zone density transition)
    # Use percentile_rank inline to avoid double-clean
    grav_rank = percentile_rank(grav, valid)
    hg = (0.5 + 0.5 * grav_rank).astype(np.float32)

    h_apron = np.where(valid, hz * hc * hg, 0.0).astype(np.float32)
    return {"H_z": hz.astype(np.float32), "H_c": hc.astype(np.float32), "H_g": hg, "H_apron": h_apron}


def radiometric_contact(
    k_th_ratio: np.ndarray | None,
    u_th_ratio: np.ndarray | None,
    valid: np.ndarray,
) -> np.ndarray:
    """Combined K/Th + U/Th lateral gradient magnitude, pct-normalized."""
    valid = np.asarray(valid, bool)
    if k_th_ratio is None and u_th_ratio is None:
        return np.ones(valid.shape, np.float32) * 0.5  # neutral

    def _grad_mag(field: np.ndarray | None) -> np.ndarray:
        if field is None:
            return np.zeros(valid.shape, np.float32)
        f = _clean(field, valid)
        # Sobel gradients
        gy = sobel(f, axis=0, mode="nearest")
        gx = sobel(f, axis=1, mode="nearest")
        return np.hypot(gy, gx).astype(np.float32)

    gk = _grad_mag(k_th_ratio) if k_th_ratio is not None else 0
    gu = _grad_mag(u_th_ratio) if u_th_ratio is not None else 0
    # Combined: K/Th primary, U/Th half-weight
    combined = (gk + 0.5 * gu).astype(np.float32) if isinstance(gk, np.ndarray) else gk
    if isinstance(combined, np.ndarray):
        # percentile rank to [0,1], then 0.5+0.5*rank so it never zeroes out terrain signal
        pr = percentile_rank(combined, valid)
        return (0.5 + 0.5 * pr).astype(np.float32)
    return np.ones(valid.shape, np.float32) * 0.5


def _geothermal_boost(
    footprint: np.ndarray,
    gdr_points_yx: tuple[np.ndarray, np.ndarray] | None,
    valid: np.ndarray,
) -> np.ndarray:
    """Weak boost (1.0→1.3) within 2 km of blind ≥80°C geothermometer cells."""
    valid = np.asarray(valid, bool)
    if gdr_points_yx is None or len(gdr_points_yx[0]) == 0:
        return np.ones(valid.shape, np.float32)
    ys, xs = gdr_points_yx
    # Rasterize wells to binary, then distance transform
    from scipy.ndimage import distance_transform_edt

    well = np.zeros(valid.shape, bool)
    # Clip to bounds
    ok = (ys >= 0) & (ys < valid.shape[0]) & (xs >= 0) & (xs < valid.shape[1])
    well[ys[ok], xs[ok]] = True
    dist = distance_transform_edt(~well).astype(np.float32)
    # Boost = 1 + 0.3 * max(0, 1 - dist/20) inside footprint
    boost = np.where(valid, 1.0 + GEO_BOOST_STRENGTH * np.maximum(0.0, 1.0 - dist / GEO_BOOST_RADIUS_PX), 1.0).astype(np.float32)
    return boost


def lane_surface(
    det_elev: np.ndarray,
    det_elev_slope: np.ndarray,
    depth_to_base: np.ndarray,
    iso_grav_anom_slope: np.ndarray,
    valid: np.ndarray,
    *,
    k_th_ratio: np.ndarray | None = None,
    u_th_ratio: np.ndarray | None = None,
    gdr_points_yx: tuple[np.ndarray, np.ndarray] | None = None,
) -> dict[str, np.ndarray]:
    """Build NEO-OPNS surface and components."""
    valid = np.asarray(valid, bool)

    tpi = tpi_500(det_elev, valid)
    curv = profile_curvature(det_elev, valid)
    # Enclosure magnitude: |TPI| * |curvature|
    encl = (np.abs(tpi) * curv).astype(np.float32)
    encl_pct = percentile_rank(encl, valid)

    brk = log_slope_break(det_elev_slope, valid)
    brk_pct = percentile_rank(brk, valid)

    coh = structure_tensor_coherence(det_elev, valid)

    hab = piedmont_habitat(det_elev, depth_to_base, iso_grav_anom_slope, valid)
    h_apron = hab["H_apron"]

    rad = radiometric_contact(k_th_ratio, u_th_ratio, valid)
    geo = _geothermal_boost(valid, gdr_points_yx, valid)

    # Fuse: openness core (enclosure) weighted by slope complement and coherence,
    # gated by habitat, corroborated by radiometrics, boosted by wells.
    # Use 0.6*break_pct + 0.4 baseline so pure TPI still emits even where log-slope is low
    s_raw = (encl_pct * coh * (0.6 * brk_pct + 0.4) * h_apron * rad * geo).astype(np.float32)
    s_pct = percentile_rank(s_raw, valid)

    return {
        "TPI": tpi,
        "curvature": curv,
        "encl": encl,
        "encl_pct": encl_pct,
        "break": brk,
        "break_pct": brk_pct,
        "coherence": coh,
        "H_z": hab["H_z"],
        "H_c": hab["H_c"],
        "H_g": hab["H_g"],
        "H_apron": h_apron,
        "radiometric": rad,
        "geothermal_boost": geo,
        "S_raw": s_raw,
        "S_pct": s_pct,
    }
