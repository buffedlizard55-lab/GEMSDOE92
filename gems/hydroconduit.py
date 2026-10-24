"""HYDROCONDUIT lane surface: Piedmont-Hinge Relative Monoclinal Scarp & Hydrothermal RTP Conduit.

Pre-registered hypothesis & equations: docs/HYPOTHESES_20261024_HYDROCONDUIT.md.

Physical summary
----------------
1. Relative Monoclinal Scarp Detector (``T_scarp``):
   - Background-normalized log-slope break ``||grad log(max(Band19, 0) + 1 deg)||``
     detects subtle 1-5 m Quaternary alluvial-fan scarps on 1-5 deg piedmonts without
     being hijacked by 25-40 deg bare mountain range-core cliffs (which consumed
     74.8% of un-normalized BREAKLINE far dots).
   - 600 m (+/-3 px) cross-strike monotonicity ``mu_step in [0, 1]`` distinguishes
     one-sided tectonic steps/monoclines (mu_step -> 1) from symmetric V-shaped
     erosional canyons and sharp ridge crests (mu_step -> 0).
   - Structure-tensor coherence of detrended elevation (Band 12) enforces linearity.

2. Piedmont-Cover & Andersonian Transtensional Envelope (``A_tect``):
   - Piedmont elevation envelope (Band 12 ``det_elev`` centered at -50 m, sigma 140 m)
     and shallow-to-intermediate basement cover envelope (Band 15 ``depth_to_base_surf``
     log-normal around ~180 m) localize brittle fault projection and range-front
     fluid breach.
   - Andersonian strike compatibility ``0.35 + 0.65 cos^2(az - 15 deg)`` favors
     NNW-NNE-NE Basin-and-Range / Walker Lane strikes while suppressing transverse
     WNW-ESE piedmont fan washes (~105 deg), combined with GPS/InSAR strain
     (Band 4 ``geod_2ndinv`` + Band 8 ``geod_dilaterate``).

3. Hydrothermal Upflow & True Reduced-to-Pole Magnetic Conduit (``G_hydro``):
   - True Band 2 ``rtp`` Miller-Singh / Verduzco phase-normalized tilt-contact edge
     plus positive horizontal-Laplacian magnetite-destruction trough (correcting the
     Band 6 ``tc`` = Radiometric Total Count mislabelling in training_features.tif).
   - USGS GeoDAWN ``K / (Th + 1)`` potassic alteration ratio, Band 17 MT subsurface
     electrical conductivity, and DOE GDR #1391 INGENIOUS thermal + blind chemical
     geothermometer (quartz/chalcedony/Na-K-Ca >= 80 C) plume.

Strict zero-leakage invariant: no fault catalogue array enters any function in this
module. Reuses ``percentile_rank`` and ``spaced_top_mask`` from ``gems.breakline``.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter

from .breakline import (
    DERIV_SIGMA_PX,
    TENSOR_SIGMA_PX,
    percentile_rank,
    spaced_top_mask,
)


def _clean_valid(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Replace non-valid, non-finite, or sentinel (<= -1e30) cells with valid median."""
    arr = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, dtype=bool) & np.isfinite(arr) & (arr > -1e30)
    fill = np.float32(np.median(arr[m])) if m.any() else np.float32(0.0)
    return np.where(m, arr, fill).astype(np.float32)

__all__ = [
    "coherence_and_strike_deg",
    "cross_strike_monotonicity",
    "rtp_tilt_and_demag",
    "gdr_blind_thermal_plume",
    "hydroconduit_surface",
    "percentile_rank",
    "spaced_top_mask",
]


def coherence_and_strike_deg(
    field: np.ndarray,
    valid: np.ndarray,
    deriv_sigma: float = DERIV_SIGMA_PX,
    tensor_sigma: float = TENSOR_SIGMA_PX,
) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(coherence, strike_azimuth_deg)`` in ``[0, 1]`` and ``[0, 180)``.

    Grid convention: row (+y) points South, col (+x) points East.
    Compass strike azimuth is measured clockwise from North:
    ``0`` = N-S strike, ``45`` = NE-SW strike, ``90`` = E-W strike, ``135`` = NW-SE strike.
    """
    a = gaussian_filter(_clean_valid(field, valid), float(deriv_sigma))
    gy, gx = np.gradient(a)
    jxx = gaussian_filter(gx * gx, float(tensor_sigma))
    jyy = gaussian_filter(gy * gy, float(tensor_sigma))
    jxy = gaussian_filter(gx * gy, float(tensor_sigma))
    coh = np.sqrt((jxx - jyy) ** 2 + 4.0 * jxy * jxy) / np.maximum(jxx + jyy, 1e-12)
    coh = np.clip(coh, 0.0, 1.0).astype(np.float32)
    phi = 0.5 * np.arctan2(2.0 * jxy, jxx - jyy)
    az_deg = (np.degrees(np.arctan2(-np.sin(phi), -np.cos(phi))) % 180.0).astype(np.float32)
    return coh, az_deg


def cross_strike_monotonicity(
    det_elev: np.ndarray,
    valid: np.ndarray,
    half_span_px: int = 3,
    normal_sigma: float = 3.0,
    elev_floor_m: float = 0.5,
) -> np.ndarray:
    """One-sided step monotonicity ``|E(+K n) - E(-K n)| / (TV_K(E) + floor)`` in ``[0, 1]``.

    Approaches 1 across monotonic fault scarps/monoclines and 0 across symmetric
    V-shaped erosional gullies or ridge crests.
    """
    if half_span_px < 1:
        raise ValueError("half_span_px must be >= 1")
    e_clean = _clean_valid(det_elev, valid)
    e1 = gaussian_filter(e_clean, 1.0).astype(np.float32)
    e_broad = gaussian_filter(e_clean, float(normal_sigma))
    gy, gx = np.gradient(e_broad)
    gnorm = np.maximum(np.hypot(gy, gx), 1e-6)
    ny = (gy / gnorm).astype(np.float32)
    nx = (gx / gnorm).astype(np.float32)
    del e_clean, e_broad, gy, gx, gnorm

    h, w = e1.shape
    if h < 2 or w < 2:
        return np.zeros((h, w), dtype=np.float32)
    max_y = np.nextafter(np.float32(h - 1), np.float32(0.0))
    max_x = np.nextafter(np.float32(w - 1), np.float32(0.0))
    base_y = np.arange(h, dtype=np.float32)[:, None]
    base_x = np.arange(w, dtype=np.float32)[None, :]

    def _sample(step_k: int) -> np.ndarray:
        yy = np.clip(base_y + np.float32(step_k) * ny, np.float32(0.0), max_y)
        xx = np.clip(base_x + np.float32(step_k) * nx, np.float32(0.0), max_x)
        y0 = np.minimum(yy.astype(np.int32), h - 2)
        x0 = np.minimum(xx.astype(np.int32), w - 2)
        fy = np.clip(yy - y0, 0.0, 1.0)
        fx = np.clip(xx - x0, 0.0, 1.0)
        v00 = e1[y0, x0]
        v01 = e1[y0, x0 + 1]
        v10 = e1[y0 + 1, x0]
        v11 = e1[y0 + 1, x0 + 1]
        return ((1.0 - fy) * ((1.0 - fx) * v00 + fx * v01)
                + fy * ((1.0 - fx) * v10 + fx * v11)).astype(np.float32)

    first_val = _sample(-half_span_px)
    prev_val = first_val
    tv = np.zeros((h, w), dtype=np.float32)
    for k in range(-half_span_px + 1, half_span_px + 1):
        cur_val = _sample(k)
        tv += np.abs(cur_val - prev_val)
        prev_val = cur_val
    net = np.abs(prev_val - first_val)
    mu = net / (tv + np.float32(elev_floor_m))
    mu = np.clip(mu, 0.0, 1.0).astype(np.float32)
    mu[~np.asarray(valid, bool)] = 0.0
    return mu


def rtp_tilt_and_demag(rtp: np.ndarray, valid: np.ndarray) -> dict[str, np.ndarray]:
    """Compute depth-invariant RTP tilt-contact edge and magnetite-destruction trough.

    Uses Laplace's equation above magnetic sources: ``d^2(RTP)/dz^2 = -(d^2/dx^2 + d^2/dy^2) RTP``.
    """
    valid_b = np.asarray(valid, bool) & np.isfinite(rtp) & (rtp > -1e30)
    u = gaussian_filter(_clean_valid(rtp, valid_b), 1.0).astype(np.float32)
    uy, ux = np.gradient(u)
    gh = np.hypot(uy, ux).astype(np.float32)
    uyy, _ = np.gradient(uy)
    _, uxx = np.gradient(ux)
    lap_h = (uxx + uyy).astype(np.float32)
    vzz = -lap_h
    del u, uy, ux, uyy, uxx

    g0 = float(np.median(gh[valid_b]) * 0.10 + 1e-6) if valid_b.any() else 1e-3
    coh_rtp, _ = coherence_and_strike_deg(rtp, valid_b)
    # Cosine of Miller-Singh/Verduzco tilt angle peaks at 1 over vertical contacts at any burial depth
    tilt_edge = (gh / np.sqrt(gh * gh + vzz * vzz + np.float32(g0 * g0)) * coh_rtp).astype(np.float32)
    # Hydrothermal magnetite -> pyrite/clay destruction creates linear RTP lows (lap_h > 0)
    demag_trough = (percentile_rank(np.maximum(lap_h, 0.0), valid_b) * coh_rtp).astype(np.float32)
    m_raw = (0.60 * percentile_rank(tilt_edge, valid_b) + 0.40 * percentile_rank(demag_trough, valid_b)).astype(np.float32)
    m_pct = percentile_rank(m_raw, valid_b)
    return {
        "tilt_edge": tilt_edge,
        "demag_trough": demag_trough,
        "rtp_conduit_pct": m_pct,
    }


def gdr_blind_thermal_plume(
    csv_path: str | Path,
    shape: tuple[int, int],
    valid: np.ndarray,
    sigma_px: float = 15.0,
) -> dict[str, np.ndarray | int]:
    """Build smooth geothermal anomaly plume from GDR #1391 surface + blind chemical geothermometers.

    Explicitly captures blind geothermal wells/springs where surface ``temp_c < 40 C``
    (due to cold shallow aquifer mixing) while quartz, chalcedony, or Na-K-Ca cation
    geothermometers record ``>= 80 C`` reservoir equilibrium temperatures, and strips
    trailing whitespace on ``thermalclass`` (fixing the 121 ``'Hot '`` rows).
    """
    df = pd.read_csv(csv_path)
    h, w = shape
    rows = pd.to_numeric(df["row"], errors="coerce")
    cols = pd.to_numeric(df["col"], errors="coerce")
    in_grid = rows.notna() & cols.notna() & (rows >= 0) & (rows < h) & (cols >= 0) & (cols < w)
    sub = df.loc[in_grid].copy()
    r_idx = sub["row"].astype(int).to_numpy()
    c_idx = sub["col"].astype(int).to_numpy()

    t_surf = pd.to_numeric(sub["temp_c"], errors="coerce").to_numpy(dtype=np.float64)
    chem_cols = [c for c in ("geothermquartz_c", "geothermchalc_c", "geothermcat_c") if c in sub.columns]
    if chem_cols:
        t_chem = np.full(len(sub), -np.inf, dtype=np.float64)
        for c in chem_cols:
            vals = pd.to_numeric(sub[c], errors="coerce").to_numpy(dtype=np.float64)
            fin = np.isfinite(vals)
            t_chem[fin] = np.maximum(t_chem[fin], vals[fin])
        t_chem[~np.isfinite(t_chem)] = np.nan
    else:
        t_chem = np.full(len(sub), np.nan, dtype=np.float64)

    tclass = sub["thermalclass"].fillna("").astype(str).str.strip().to_numpy()
    is_hot_class = np.isin(tclass, ["Hot", "Warm"])
    is_surf_anom = np.isfinite(t_surf) & (t_surf >= 35.0)
    is_chem_anom = np.isfinite(t_chem) & (t_chem >= 80.0)
    is_blind_chem = is_chem_anom & (~np.isfinite(t_surf) | (t_surf < 40.0))
    keep = is_hot_class | is_surf_anom | is_chem_anom

    surf_excess = np.where(np.isfinite(t_surf), np.maximum(t_surf - 20.0, 0.0) / 120.0, 0.0)
    chem_excess = np.where(np.isfinite(t_chem), 0.5 * np.maximum(t_chem - 60.0, 0.0) / 120.0, 0.0)
    class_floor = np.where(tclass == "Hot", 0.50, np.where(tclass == "Warm", 0.25, 0.0))
    weights = np.clip(np.maximum.reduce([surf_excess, chem_excess, class_floor]), 0.0, 1.0)

    impulses = np.zeros((h, w), dtype=np.float32)
    blind_mask = np.zeros((h, w), dtype=bool)
    if np.any(keep):
        np.maximum.at(impulses, (r_idx[keep], c_idx[keep]), weights[keep].astype(np.float32))
    if np.any(is_blind_chem):
        blind_mask[r_idx[is_blind_chem], c_idx[is_blind_chem]] = True

    plume_raw = gaussian_filter(impulses, float(sigma_px)).astype(np.float32)
    valid_b = np.asarray(valid, bool)
    pos_valid = valid_b & (plume_raw > 1e-12)
    plume_pct = np.zeros((h, w), dtype=np.float32)
    if np.any(pos_valid):
        f_zero = float(1.0 - pos_valid.sum() / max(int(valid_b.sum()), 1))
        pos_ranks = percentile_rank(plume_raw, pos_valid)
        plume_pct[pos_valid] = (f_zero + (1.0 - f_zero) * pos_ranks[pos_valid]).astype(np.float32)
    return {
        "plume_raw": plume_raw,
        "plume_pct": plume_pct,
        "n_thermal_pixels": int((impulses > 0).sum()),
        "n_blind_geotherm_pixels": int(blind_mask.sum()),
    }


def hydroconduit_surface(
    *,
    det_elev: np.ndarray,
    det_elev_slope: np.ndarray,
    depth_to_base: np.ndarray,
    geod_2ndinv: np.ndarray,
    geod_dilaterate: np.ndarray,
    rtp: np.ndarray,
    cond_surf: np.ndarray,
    rad_k: np.ndarray,
    rad_th: np.ndarray,
    gdr_plume_pct: np.ndarray,
    footprint: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute pre-registered ``S_pied`` (Exp 1) and ``S_hydro`` (Exp 2 & Exp 3) surfaces."""
    fp = np.asarray(footprint, bool)
    valid = (
        fp
        & np.isfinite(det_elev) & (det_elev > -1e30)
        & np.isfinite(det_elev_slope) & (det_elev_slope > -1e30)
        & np.isfinite(depth_to_base) & (depth_to_base > -1e30)
        & np.isfinite(geod_2ndinv) & (geod_2ndinv > -1e30)
        & np.isfinite(geod_dilaterate) & (geod_dilaterate > -1e30)
        & np.isfinite(rtp) & (rtp > -1e30)
        & np.isfinite(cond_surf) & (cond_surf > -1e30)
    )

    # 1. Relative Monoclinal Scarp Detector T_scarp
    s_clean = np.maximum(_clean_valid(det_elev_slope, valid), 0.0)
    log_slope = np.log(s_clean + np.float32(1.0)).astype(np.float32)
    ls_y, ls_x = np.gradient(log_slope)
    rel_break_pct = percentile_rank(np.hypot(ls_y, ls_x).astype(np.float32), valid)
    del s_clean, log_slope, ls_y, ls_x

    coh_elev, strike_deg = coherence_and_strike_deg(det_elev, valid)
    mu_step = cross_strike_monotonicity(det_elev, valid, half_span_px=3, normal_sigma=3.0, elev_floor_m=0.5)
    t_scarp = (rel_break_pct * coh_elev * mu_step).astype(np.float32)

    # 2. Piedmont-Hinge & Andersonian Transtensional Envelope A_tect
    e_clean = _clean_valid(det_elev, valid)
    z_elev = np.clip((e_clean - np.float32(-50.0)) / np.float32(140.0), -20.0, 20.0)
    p_elev = np.exp(-0.5 * (z_elev ** 2)).astype(np.float32)
    db_clean = np.maximum(_clean_valid(depth_to_base, valid), 0.0)
    log_db = np.log10(db_clean + np.float32(10.0))
    z_db = np.clip((log_db - np.float32(2.28)) / np.float32(0.65), -20.0, 20.0)
    p_cover = (0.25 + 0.75 * np.exp(-0.5 * (z_db ** 2))).astype(np.float32)
    del e_clean, z_elev, db_clean, log_db, z_db

    strike_rad = np.radians(strike_deg - np.float32(15.0))
    kappa_strike = (0.35 + 0.65 * (np.cos(strike_rad) ** 2)).astype(np.float32)
    strain_2nd_pct = percentile_rank(geod_2ndinv, valid)
    strain_dil_pct = percentile_rank(geod_dilaterate, valid)
    kappa_strain = (0.40 + 0.60 * (0.50 * strain_2nd_pct + 0.50 * strain_dil_pct)).astype(np.float32)

    hab_pied = (p_elev * p_cover * kappa_strain).astype(np.float32)
    hab_pied[~valid] = 0.0
    a_tect = (hab_pied * kappa_strike).astype(np.float32)
    a_tect[~valid] = 0.0

    s_pied_raw = (t_scarp * a_tect).astype(np.float32)
    s_pied_raw[~valid] = 0.0
    s_pied_pct = percentile_rank(s_pied_raw, valid)

    # 3. Hydrothermal Upflow & True RTP Conduit G_hydro
    rtp_parts = rtp_tilt_and_demag(rtp, valid)
    m_rtp = rtp_parts["rtp_conduit_pct"]

    rad_valid = valid & np.isfinite(rad_k) & np.isfinite(rad_th) & (rad_k > 0) & (rad_th > 0)
    kth_ratio = np.zeros_like(det_elev, dtype=np.float32)
    kth_ratio[rad_valid] = (rad_k[rad_valid].astype(np.float32) / (rad_th[rad_valid].astype(np.float32) + np.float32(1.0)))
    kth_smooth = gaussian_filter(_clean_valid(kth_ratio, rad_valid), 2.0).astype(np.float32)
    r_kth = percentile_rank(kth_smooth, rad_valid)
    c_mt = percentile_rank(cond_surf, valid)
    q_gdr = np.where(valid, np.asarray(gdr_plume_pct, dtype=np.float32), 0.0).astype(np.float32)

    g_hydro_raw = (0.35 * m_rtp + 0.25 * r_kth + 0.20 * c_mt + 0.20 * q_gdr).astype(np.float32)
    g_hydro = percentile_rank(g_hydro_raw, valid)

    s_hydro_raw = (s_pied_raw * (0.50 + 0.50 * g_hydro)).astype(np.float32)
    s_hydro_raw[~valid] = 0.0
    s_hydro_pct = percentile_rank(s_hydro_raw, valid)

    hab_hydro = (hab_pied * (0.50 + 0.50 * g_hydro)).astype(np.float32)
    hab_hydro[~valid] = 0.0

    return {
        "valid": valid,
        "rel_break_pct": rel_break_pct,
        "coh_elev": coh_elev,
        "mu_step": mu_step,
        "t_scarp": t_scarp,
        "p_elev": p_elev,
        "p_cover": p_cover,
        "kappa_strike": kappa_strike,
        "kappa_strain": kappa_strain,
        "hab_pied_pct": percentile_rank(hab_pied, valid),
        "hab_hydro_pct": percentile_rank(hab_hydro, valid),
        "m_rtp": m_rtp,
        "r_kth": r_kth,
        "c_mt": c_mt,
        "q_gdr": q_gdr,
        "g_hydro": g_hydro,
        "S_pied_raw": s_pied_raw,
        "S_pied_pct": s_pied_pct,
        "S_hydro_raw": s_hydro_raw,
        "S_hydro_pct": s_hydro_pct,
    }
