"""COULOMB-LOQO lane: Spatially Cross-Fitted (LOQO) Polarity-Locked Multi-Scale
Hessian & 2D Coulomb Transtensional Ridge Model.

Pre-registered hypothesis & equations: ``docs/HYPOTHESES_20261024_COULOMBLOQO.md``.

Key physical & statistical invariants
-------------------------------------
1. **Strict Catalogue Independence of Features**:
   ``compute_feature_stack`` computes 24 physical channels (Groups A-E) solely from
   the 19-band geophysical/topographic stack, USGS GeoDAWN gamma-ray spectrometry
   (``K, Th, U``), and DOE GDR #1391 INGENIOUS thermal & blind chemical geothermometry.
   It explicitly drops ``dist_known_fault_px`` before inspecting any GDR columns and
   never touches ``existing_faults.tif`` or ``labels.tif``.
2. **Zero Transductive Quadrant Coupling**:
   Every feature uses strictly local spatial operators (<= 14 px) and fixed physical
   saturating scales ``x / (x + c0)`` -- never global full-map quantile ranks -- so
   held-out quadrants cannot influence feature scaling in training quadrants.
3. **Strict Leave-One-Quadrant-Out (LOQO) Spatial Cross-Fitting**:
   Using ``gems57.holdout.quadrant_ids(footprint)``, each target quadrant ``q in {0..3}``
   is predicted exclusively by a regularized ``HistGradientBoostingClassifier`` fit on
   ``(quad != q)`` eroded by ``guard_px >= 12`` (1.2 km guard band), with negative
   training samples drawn strictly outside ``d_label > neg_buffer_px`` (500 m).
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.ndimage import binary_dilation, distance_transform_edt, gaussian_filter
from sklearn.ensemble import HistGradientBoostingClassifier

from .apronridge import directional_ridge_1d
from .breakline import spaced_top_mask
from .hydroconduit import (
    _clean_valid,
    coherence_and_strike_deg,
    cross_strike_monotonicity,
)

FEATURE_NAMES: tuple[str, ...] = (
    # Group A: Multi-scale topographic Hessian ridges, scarp step & cover (0..7)
    "f01_rel_log_slope_break",
    "f02_hess_ridge_s12",
    "f03_hess_ridge_s30",
    "f04_step_monotonicity_600m",
    "f05_elev_coherence",
    "f06_det_elev_m",
    "f07_log_depth_base",
    "f08_basement_step_grad",
    # Group B: Polarity-locked footwall-hangingwall concordance & gravity tilt (8..11)
    "f09_dip_concord_grav",
    "f10_dip_concord_base",
    "f11_ew_polarity_lock",
    "f12_grav_tilt_edge",
    # Group C: True Band 2 RTP tilt/demag/Hessian & cross-physics axial lock (12..15)
    "f13_rtp_tilt_edge",
    "f14_rtp_demag_trough",
    "f15_rtp_hess_ridge",
    "f16_cross_physics_axial_lock",
    # Group D: Stress-resolved 2D Coulomb slip & dilation tendency (16..18)
    "f17_coulomb_dilation_tendency",
    "f18_coulomb_slip_tendency",
    "f19_strain_2ndinv",
    # Group E: MT clay-cap margin, radioelement alteration & blind geothermometry (19..23)
    "f20_mt_claycap_grad",
    "f21_mt_cond_level",
    "f22_rad_k_th_ratio",
    "f23_rad_u_th_grad",
    "f24_gdr_blind_plume",
)

TOPO_ONLY_INDICES: tuple[int, ...] = (0, 1, 2, 3, 4, 5, 6, 7)
OPTIMAL_NORMAL_STRIKE_DEG: float = 15.0

__all__ = [
    "FEATURE_NAMES",
    "TOPO_ONLY_INDICES",
    "OPTIMAL_NORMAL_STRIKE_DEG",
    "hessian_ridge_strength",
    "cross_physics_axial_order",
    "coulomb_tendencies",
    "gdr_blind_thermal_features",
    "compute_feature_stack",
    "fit_predict_loqo",
    "build_crest_surface",
    "directional_ridge_1d",
    "spaced_top_mask",
]


def _grad_xy(field: np.ndarray, valid: np.ndarray, sigma: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    u = _clean_valid(field, valid)
    if sigma > 0.0:
        u = gaussian_filter(u, float(sigma)).astype(np.float32)
    gy, gx = np.gradient(u)
    return gy.astype(np.float32), gx.astype(np.float32)


def hessian_ridge_strength(
    field: np.ndarray,
    valid: np.ndarray,
    sigma: float = 1.5,
) -> np.ndarray:
    """Scale-normalized principal negative Hessian eigenvalue ``max(0, -lambda_1) * sigma^2``.

    Detects curvilinear ridge crests of width ~``2*sigma`` pixels regardless of azimuth.
    """
    if sigma <= 0.0:
        raise ValueError("sigma must be positive")
    u = gaussian_filter(_clean_valid(field, valid), float(sigma)).astype(np.float32)
    uy, ux = np.gradient(u)
    uyy, uxy = np.gradient(uy)
    uxy2, uxx = np.gradient(ux)
    hxy = (0.5 * (uxy + uxy2)).astype(np.float32)
    del u, uy, ux, uxy, uxy2

    tr = (uxx + uyy).astype(np.float32)
    rad = np.sqrt((uxx - uyy) ** 2 + 4.0 * hxy * hxy).astype(np.float32)
    # Most negative eigenvalue captures convex-upward 1D ridge crests
    lam_min = 0.5 * (tr - rad)
    ridge = (np.maximum(-lam_min, 0.0) * np.float32(sigma * sigma)).astype(np.float32)
    ridge[~np.asarray(valid, bool)] = 0.0
    return ridge


def cross_physics_axial_order(
    strikes_deg: list[np.ndarray],
    weights: list[np.ndarray],
    valid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(R_axial, composite_strike_deg)`` in ``[0, 1]`` and ``[0, 180)``.

    Uses double-angle axial phasors ``exp(i * 2 * theta)`` so strikes ``theta`` and
    ``theta + 180 deg`` are identical. ``R_axial -> 1`` when independent physical
    fields agree on local fault strike and ``-> 0`` when orthogonal.
    """
    if not strikes_deg or len(strikes_deg) != len(weights):
        raise ValueError("strikes_deg and weights must be non-empty lists of equal length")
    shape = strikes_deg[0].shape
    cos2 = np.zeros(shape, dtype=np.float32)
    sin2 = np.zeros(shape, dtype=np.float32)
    wsum = np.zeros(shape, dtype=np.float32)
    for th, w in zip(strikes_deg, weights):
        rad2 = np.radians(2.0 * np.asarray(th, dtype=np.float32))
        ww = np.maximum(np.asarray(w, dtype=np.float32), 0.0)
        cos2 += ww * np.cos(rad2).astype(np.float32)
        sin2 += ww * np.sin(rad2).astype(np.float32)
        wsum += ww
    denom = np.maximum(wsum, 1e-6)
    r_ax = (np.hypot(cos2, sin2) / denom).astype(np.float32)
    r_ax = np.clip(r_ax, 0.0, 1.0)
    comp_deg = ((0.5 * np.degrees(np.arctan2(sin2, cos2))) % 180.0).astype(np.float32)
    valid_b = np.asarray(valid, bool)
    r_ax[~valid_b] = 0.0
    comp_deg[~valid_b] = 0.0
    return r_ax, comp_deg


def coulomb_tendencies(
    strike_deg: np.ndarray,
    geod_shearrate: np.ndarray,
    geod_dilaterate: np.ndarray,
    valid: np.ndarray,
    optimal_normal_strike_deg: float = OPTIMAL_NORMAL_STRIKE_DEG,
) -> tuple[np.ndarray, np.ndarray]:
    """Project geodetic dilatation & shear rates onto local fault strike (Morris et al., 1996).

    * Normal dilation tendency ``T_d`` peaks along N15E strikes orthogonal to NW Great
      Basin WNW-ESE extension (``sigma_h,min ~ N105E``) and vanishes on N105E segments.
    * Transtensional slip tendency ``T_s`` captures both N15E dip-slip normal faults and
      conjugate NW Walker Lane dextral / ENE Humboldt sinistral shear orientations
      (``sin^2(2 * dtheta)`` peaks at +/-45 deg from N15E, i.e., N30W and N60E).
    """
    valid_b = np.asarray(valid, bool)
    dth = np.radians(np.asarray(strike_deg, dtype=np.float32) - float(optimal_normal_strike_deg))
    cos2_n = (np.cos(dth) ** 2).astype(np.float32)
    sin2_2n = (np.sin(2.0 * dth) ** 2).astype(np.float32)

    dil_pos = np.maximum(_clean_valid(geod_dilaterate, valid_b) + np.float32(5.0), 0.0)
    shr_pos = np.maximum(_clean_valid(geod_shearrate, valid_b), 0.0)

    t_dil = (cos2_n * dil_pos).astype(np.float32)
    t_slip = (np.maximum(cos2_n, np.float32(0.85) * sin2_2n) * shr_pos).astype(np.float32)
    t_dil[~valid_b] = 0.0
    t_slip[~valid_b] = 0.0
    return t_dil, t_slip


def gdr_blind_thermal_features(
    csv_path: str | Path,
    shape: tuple[int, int],
    valid: np.ndarray,
    sigma_px: float = 14.0,
) -> dict[str, np.ndarray | int]:
    """Catalogue-blind hydrothermal upflow plume from GDR #1391 wells and springs.

    Explicitly drops ``dist_known_fault_px`` before touching any data so catalogue
    proximity can never enter the feature stack.
    """
    df = pd.read_csv(csv_path)
    df = df.drop(columns=["dist_known_fault_px"], errors="ignore")
    assert "dist_known_fault_px" not in df.columns

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
    chem_excess = np.where(np.isfinite(t_chem), 0.55 * np.maximum(t_chem - 60.0, 0.0) / 120.0, 0.0)
    class_floor = np.where(tclass == "Hot", 0.50, np.where(tclass == "Warm", 0.25, 0.0))
    weights = np.clip(np.maximum.reduce([surf_excess, chem_excess, class_floor]), 0.0, 1.0)

    impulses = np.zeros((h, w), dtype=np.float32)
    blind_mask = np.zeros((h, w), dtype=bool)
    if np.any(keep):
        np.maximum.at(impulses, (r_idx[keep], c_idx[keep]), weights[keep].astype(np.float32))
    if np.any(is_blind_chem):
        blind_mask[r_idx[is_blind_chem], c_idx[is_blind_chem]] = True

    plume_raw = gaussian_filter(impulses, float(sigma_px)).astype(np.float32)
    feat = np.log1p(np.float32(100.0) * np.maximum(plume_raw, 0.0)).astype(np.float32)
    feat[~np.asarray(valid, bool)] = 0.0
    return {
        "plume_feat": feat,
        "n_thermal_pixels": int((impulses > 0).sum()),
        "n_blind_geotherm_pixels": int(blind_mask.sum()),
    }


def _sat(x: np.ndarray, c0: float) -> np.ndarray:
    xp = np.maximum(np.asarray(x, dtype=np.float32), 0.0)
    return (xp / (xp + np.float32(c0))).astype(np.float32)


def compute_feature_stack(
    *,
    rtp: np.ndarray,
    geod_2ndinv: np.ndarray,
    grav_slope: np.ndarray,
    geod_shearrate: np.ndarray,
    geod_dilaterate: np.ndarray,
    grav_vg: np.ndarray,
    det_elev: np.ndarray,
    grav_anom: np.ndarray,
    depth_to_base: np.ndarray,
    cond_surf: np.ndarray,
    grav_hg: np.ndarray,
    det_elev_slope: np.ndarray,
    rad_k: np.ndarray,
    rad_th: np.ndarray,
    rad_u: np.ndarray,
    gdr_plume_feat: np.ndarray,
    footprint: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute compact ``(N_foot, 24)`` float32 feature matrix + 1D localization fields."""
    foot = np.asarray(footprint, dtype=bool)
    valid = (
        foot
        & np.isfinite(det_elev) & (det_elev > -1e30)
        & np.isfinite(det_elev_slope) & (det_elev_slope > -1e30)
        & np.isfinite(rtp) & (rtp > -1e30)
    )
    foot_idx = np.flatnonzero(foot)
    n_foot = int(foot_idx.size)
    X = np.zeros((n_foot, len(FEATURE_NAMES)), dtype=np.float32)

    def _put(col: int, arr2d: np.ndarray) -> None:
        flat = np.asarray(arr2d, dtype=np.float32).ravel()[foot_idx]
        flat = np.nan_to_num(flat, nan=0.0, posinf=0.0, neginf=0.0)
        X[:, col] = flat

    # --- Group A: Topographic Hessian ridges, scarp step & cover ---
    log_slope = np.log(np.maximum(_clean_valid(det_elev_slope, valid), 0.0) + np.float32(1.0)).astype(np.float32)
    lsy, lsx = _grad_xy(log_slope, valid, sigma=1.0)
    rel_break = np.where(valid, np.hypot(lsy, lsx), 0.0).astype(np.float32)
    del lsy, lsx
    hess_s12 = hessian_ridge_strength(log_slope, valid, sigma=1.2)
    hess_s30 = hessian_ridge_strength(log_slope, valid, sigma=3.0)
    del log_slope

    mu_step = cross_strike_monotonicity(det_elev, valid, half_span_px=3, normal_sigma=3.0, elev_floor_m=0.5)
    coh_topo, az_topo = coherence_and_strike_deg(det_elev, valid)
    z_clean = np.where(valid, _clean_valid(det_elev, valid), 0.0).astype(np.float32)
    db_pos = np.maximum(_clean_valid(depth_to_base, valid), 0.0)
    log_db = np.where(valid, np.log1p(db_pos), 0.0).astype(np.float32)
    log_db10 = np.log(db_pos + np.float32(10.0)).astype(np.float32)
    del db_pos
    dby, dbx = _grad_xy(log_db10, valid, sigma=2.0)
    base_grad = np.where(valid, np.hypot(dby, dbx), 0.0).astype(np.float32)

    _put(0, rel_break)
    _put(1, hess_s12)
    _put(2, hess_s30)
    _put(3, mu_step)
    _put(4, coh_topo)
    _put(5, z_clean)
    _put(6, log_db)
    _put(7, base_grad)
    del z_clean, log_db, log_db10

    # Local 1D topographic localization in [0, 1) (strictly pixel/stencil-local)
    l_topo = np.where(
        valid,
        0.55 * _sat(hess_s12, 0.06) + 0.45 * _sat(rel_break * (0.35 + 0.65 * mu_step) * coh_topo, 0.04),
        0.0,
    ).astype(np.float32)
    del rel_break, hess_s12, hess_s30, mu_step

    # --- Group B: Polarity-locked footwall concordance & gravity tilt ---
    zy, zx = _grad_xy(det_elev, valid, sigma=2.0)
    znorm = np.hypot(zy, zx)
    gy, gx = _grad_xy(grav_anom, valid, sigma=2.0)
    gnorm = np.hypot(gy, gx)
    dip_grav = np.where(
        valid,
        (zy * gy + zx * gx) / (znorm * gnorm + np.float32(1e-4)),
        0.0,
    ).astype(np.float32)
    dip_grav = np.clip(dip_grav, -1.0, 1.0)

    bnorm = np.hypot(dby, dbx)
    # Shallowing basement (-grad D_base) aligned with rising topography (+grad det_elev)
    dip_base = np.where(
        valid,
        -(zy * dby + zx * dbx) / (znorm * bnorm + np.float32(1e-4)),
        0.0,
    ).astype(np.float32)
    dip_base = np.clip(dip_base, -1.0, 1.0)
    del zy, gy, gx, gnorm, dby, dbx, bnorm, znorm

    b18_clean = _clean_valid(grav_hg, valid)
    ew_lock = np.where(
        valid,
        np.tanh(zx / np.float32(8.0)) * np.tanh(b18_clean / np.float32(1.5)),
        0.0,
    ).astype(np.float32)
    del zx, b18_clean

    gs_clean = np.maximum(_clean_valid(grav_slope, valid), 0.0)
    gvg_clean = _clean_valid(grav_vg, valid)
    grav_tilt = np.where(
        valid,
        gs_clean / np.sqrt(gs_clean * gs_clean + (np.float32(0.05) * gvg_clean) ** 2 + np.float32(0.02 ** 2)),
        0.0,
    ).astype(np.float32)
    del gs_clean, gvg_clean

    _put(8, dip_grav)
    _put(9, dip_base)
    _put(10, ew_lock)
    _put(11, grav_tilt)
    del dip_grav, dip_base, ew_lock

    # --- Group C: True Band 2 RTP tilt/demag/Hessian & cross-physics axial lock ---
    u_rtp = gaussian_filter(_clean_valid(rtp, valid), 1.0).astype(np.float32)
    ry, rx = np.gradient(u_rtp)
    r_gh = np.hypot(ry, rx).astype(np.float32)
    ryy, _ = np.gradient(ry)
    _, rxx = np.gradient(rx)
    r_lap = (rxx + ryy).astype(np.float32)
    del u_rtp, ry, rx, ryy, rxx

    coh_rtp, az_rtp = coherence_and_strike_deg(rtp, valid)
    coh_grav, az_grav = coherence_and_strike_deg(grav_anom, valid)

    rtp_tilt = np.where(
        valid,
        (r_gh / np.sqrt(r_gh * r_gh + r_lap * r_lap + np.float32(1.5 ** 2))) * coh_rtp,
        0.0,
    ).astype(np.float32)
    rtp_demag = np.where(
        valid,
        np.log1p(np.maximum(r_lap, 0.0)) * coh_rtp,
        0.0,
    ).astype(np.float32)
    rtp_hess = hessian_ridge_strength(np.log1p(r_gh), valid, sigma=2.0)
    del r_gh, r_lap

    r_axial, comp_strike = cross_physics_axial_order(
        [az_topo, az_rtp, az_grav],
        [coh_topo, coh_rtp, np.float32(0.7) * coh_grav],
        valid,
    )
    del coh_topo, az_topo, coh_rtp, az_rtp, coh_grav, az_grav

    _put(12, rtp_tilt)
    _put(13, rtp_demag)
    _put(14, rtp_hess)
    _put(15, r_axial)
    del rtp_demag, r_axial

    # --- Group D: Stress-resolved 2D Coulomb slip & dilation tendency ---
    t_dil, t_slip = coulomb_tendencies(comp_strike, geod_shearrate, geod_dilaterate, valid)
    del comp_strike
    s2i = np.where(valid, np.maximum(_clean_valid(geod_2ndinv, valid), 0.0), 0.0).astype(np.float32)
    _put(16, t_dil)
    _put(17, t_slip)
    _put(18, s2i)
    del t_dil, t_slip, s2i

    # --- Group E: MT clay-cap margin, radioelements & blind geothermometry ---
    cond_clean = np.maximum(_clean_valid(cond_surf, valid), np.float32(0.1))
    log_cond = np.log(cond_clean).astype(np.float32)
    cy, cx = _grad_xy(log_cond, valid, sigma=2.0)
    mt_grad = np.where(valid, np.hypot(cy, cx), 0.0).astype(np.float32)
    del log_cond, cy, cx

    valid_rad = (
        valid
        & np.isfinite(rad_k)
        & np.isfinite(rad_th)
        & np.isfinite(rad_u)
        & (np.asarray(rad_th) > 0)
    )
    k_th_raw = np.where(
        valid_rad,
        np.asarray(rad_k, dtype=np.float32) / (np.asarray(rad_th, dtype=np.float32) + np.float32(1.0)),
        0.0,
    ).astype(np.float32)
    k_th = np.where(valid, gaussian_filter(_clean_valid(k_th_raw, valid_rad), 2.0), 0.0).astype(np.float32)
    del k_th_raw

    u_th_raw = np.where(
        valid_rad,
        np.asarray(rad_u, dtype=np.float32) / (np.asarray(rad_th, dtype=np.float32) + np.float32(1.0)),
        0.0,
    ).astype(np.float32)
    uy, ux = _grad_xy(u_th_raw, valid_rad, sigma=2.0)
    u_th_grad = np.where(valid, np.hypot(uy, ux), 0.0).astype(np.float32)
    del u_th_raw, uy, ux, valid_rad

    _put(19, mt_grad)
    _put(20, np.where(valid, cond_clean, 0.0).astype(np.float32))
    _put(21, k_th)
    _put(22, u_th_grad)
    _put(23, np.where(valid, gdr_plume_feat, 0.0).astype(np.float32))
    del cond_clean, k_th, u_th_grad

    # Subsurface 1D localization channel (RTP Hessian/tilt + basement step + MT clay-cap edge + gravity tilt)
    l_sub = np.where(
        valid,
        0.45 * _sat(rtp_hess, 0.04)
        + 0.25 * rtp_tilt
        + 0.15 * _sat(base_grad, 0.025)
        + 0.15 * _sat(mt_grad, 0.012) * grav_tilt,
        0.0,
    ).astype(np.float32)
    del rtp_hess, rtp_tilt, base_grad, mt_grad, grav_tilt

    return {
        "X_foot": X,
        "valid": valid,
        "L_topo": l_topo,
        "L_sub": l_sub,
    }


def fit_predict_loqo(
    X_foot: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    label_mask: np.ndarray,
    *,
    feature_cols: tuple[int, ...] | None = None,
    excluded_mask: np.ndarray | None = None,
    guard_px: int = 12,
    neg_buffer_px: float = 5.0,
    neg_pos_ratio: int = 4,
    seed: int = 20261024,
    max_iter: int = 180,
) -> np.ndarray:
    """Strictly spatially blocked 4-quadrant Leave-One-Quadrant-Out fault probability.

    For each target quadrant ``q in {0, 1, 2, 3}``:
    - Training pixels are restricted strictly to ``(quad >= 0) & (quad != q)``
      eroded away from ``(quad == q)`` by ``guard_px`` (>= 1.2 km spatial guard).
    - If ``excluded_mask`` is supplied (e.g. ``hidden_all`` + context buffer in strict
      draw-blind Rule-2 holdout), those pixels are excluded from BOTH positives and
      negatives everywhere.
    - Negative training pixels satisfy ``EDT(~label_mask) > neg_buffer_px`` so unmapped
      near-fault splays are not mislabeled as background.
    """
    if guard_px < 0:
        raise ValueError("guard_px must be >= 0")
    if neg_pos_ratio < 1:
        raise ValueError("neg_pos_ratio must be >= 1")
    foot = np.asarray(footprint, dtype=bool)
    valid_b = np.asarray(valid, dtype=bool) & foot
    lbl = np.asarray(label_mask, dtype=bool) & valid_b
    excl = np.asarray(excluded_mask, dtype=bool) if excluded_mask is not None else np.zeros_like(foot)

    cols = list(feature_cols) if feature_cols is not None else list(range(X_foot.shape[1]))
    d_lbl = distance_transform_edt(~lbl)

    # Map 2D footprint coordinates to compact 0..N_foot-1 row indices
    foot_row_map = np.full(foot.shape, -1, dtype=np.int32)
    foot_row_map[foot] = np.arange(int(foot.sum()), dtype=np.int32)

    proba_2d = np.zeros(foot.shape, dtype=np.float32)
    present_quads = [int(q) for q in (0, 1, 2, 3) if np.any((quad == q) & valid_b)]

    for q in present_quads:
        target_q = (quad == q) & valid_b
        if guard_px > 0:
            guard = binary_dilation(quad == q, iterations=int(guard_px))
        else:
            guard = quad == q
        train_dom = valid_b & (quad >= 0) & (quad != q) & (~guard) & (~excl)

        pos_mask = train_dom & lbl
        neg_pool = train_dom & (~lbl) & (d_lbl > float(neg_buffer_px))

        pos_idx = foot_row_map[pos_mask]
        neg_idx = foot_row_map[neg_pool]
        if pos_idx.size == 0 or neg_idx.size == 0:
            raise ValueError(f"Quadrant {q} LOQO training split has empty class: pos={pos_idx.size}, neg={neg_idx.size}")

        rng = np.random.default_rng(int(seed) + 97 * q)
        n_neg = min(int(neg_idx.size), max(int(pos_idx.size) * int(neg_pos_ratio), 1))
        if n_neg < neg_idx.size:
            neg_sel = rng.choice(neg_idx, size=n_neg, replace=False)
            neg_sel.sort()
        else:
            neg_sel = neg_idx

        tr_idx = np.concatenate([pos_idx, neg_sel])
        X_tr = X_foot[tr_idx][:, cols]
        y_tr = np.concatenate([
            np.ones(pos_idx.size, dtype=np.int8),
            np.zeros(neg_sel.size, dtype=np.int8),
        ])
        # Balance effective class prior toward Tversky beta=0.8 / alpha=0.2 discovery sensitivity
        pos_weight = float(neg_sel.size) / float(max(pos_idx.size, 1))
        sample_w = np.where(y_tr == 1, pos_weight, 1.0).astype(np.float32)

        clf = HistGradientBoostingClassifier(
            loss="log_loss",
            learning_rate=0.06,
            max_iter=int(max_iter),
            max_leaf_nodes=31,
            max_depth=5,
            min_samples_leaf=min(200, max(10, int(tr_idx.size // 40))),
            l2_regularization=10.0,
            early_stopping=False,
            random_state=int(seed) + q,
        )
        clf.fit(X_tr, y_tr, sample_weight=sample_w)

        te_idx = foot_row_map[target_q]
        preds = np.empty(te_idx.size, dtype=np.float32)
        batch = 250_000
        for start in range(0, te_idx.size, batch):
            stop = min(start + batch, te_idx.size)
            X_te = X_foot[te_idx[start:stop]][:, cols]
            preds[start:stop] = clf.predict_proba(X_te)[:, 1].astype(np.float32)

        proba_2d[target_q] = preds

    return proba_2d


def build_crest_surface(
    proba_2d: np.ndarray,
    l_topo: np.ndarray,
    l_sub: np.ndarray | None,
    valid: np.ndarray,
    *,
    sub_weight: float = 0.80,
) -> dict[str, np.ndarray]:
    """Combine out-of-quadrant LOQO fault probability with 1D structural crest localization."""
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0), 0.0)
    if l_sub is not None:
        e_line = np.maximum(
            np.asarray(l_topo, dtype=np.float32),
            np.float32(sub_weight) * np.asarray(l_sub, dtype=np.float32),
        )
    else:
        e_line = np.asarray(l_topo, dtype=np.float32)
    s_crest = np.where(valid_b, p * (np.float32(0.15) + np.float32(0.85) * e_line), 0.0).astype(np.float32)
    ridge_1d = directional_ridge_1d(s_crest, valid_b)
    return {
        "S_crest": s_crest,
        "E_line": np.where(valid_b, e_line, 0.0).astype(np.float32),
        "ridge_1d": ridge_1d,
    }
