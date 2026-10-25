"""KNICKLOQO lane: Province-Debiased Quadrant-Calibrated LOQO with Incised
Thalweg Knickzone Convexity, Cross-Contour Pluvial Shoreline Deconfounding,
and Sliding-Window Poisson's-Relation Magneto-Gravity Concordance.

Pre-registered hypothesis & equations: docs/HYPOTHESES_20261025_KNICKLOQO.md.

Resolves two coupled bottlenecks from prior sessions:
1. #IR-92-NE-QUADRANT-LOQO-COLLAPSE: Augments the 24 physical features with
   4.5 km (45 px) mesoscale locally standardized geodetic strain anomalies,
   combines full-feature, province-debiased, and subsurface-knickzone LOQO
   ensembles, and applies label-free within-quadrant quantile calibration so
   the interior Humboldt/Owyhee domain (NE quadrant) is never starved.
2. #IR-92-COULOMBLOQO-EULERFUSE-POSTMERGE-COLLISION: Combines incised drainage
   thalweg knickzone convexity (lambda_1(det_elev) > 0 x ||grad log(slope+1)||),
   cross-contour tectonic transgression vs. Lake Lahontan shoreline null, and
   Poisson's-relation magneto-gravity vector collinearity along a multi-branch
   (thalweg knickzone + subsurface Poisson + scarp) 1D crest architecture.

Strict zero-leakage invariant: no fault catalogue array enters any feature
or surface function in this module.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt, gaussian_filter
from sklearn.ensemble import HistGradientBoostingClassifier

from .breakline import percentile_rank, spaced_top_mask
from .coulomb_loqo import (
    _grad_xy,
    _sat,
    coulomb_tendencies,
    cross_physics_axial_order,
    directional_ridge_1d,
    gdr_blind_thermal_features,
    hessian_ridge_strength,
)
from .hydroconduit import (
    _clean_valid,
    coherence_and_strike_deg,
    cross_strike_monotonicity,
)

__all__ = [
    "FEATURE_NAMES",
    "DEBIASED_INDICES",
    "SUB_KNICK_INDICES",
    "mesoscale_zscore",
    "thalweg_concavity_strength",
    "compute_knick_loqo_stack",
    "calibrate_quadrant_probabilities",
    "fit_single_loqo",
    "fit_predict_knick_loqo",
    "build_knick_crest_surface",
    "gdr_blind_thermal_features",
    "spaced_top_mask",
]

FEATURE_NAMES: tuple[str, ...] = (
    # Group A: Topographic Hessian ridges, scarp step & cover (8)
    "rel_log_slope_break",
    "hess_log_slope_s12",
    "hess_log_slope_s30",
    "cross_strike_monotonicity_600m",
    "topo_tensor_coherence",
    "det_elev_m",
    "log1p_depth_to_base_m",
    "basement_relief_grad",
    # Group B: Polarity-locked footwall concordance & gravity tilt (4)
    "dip_concord_elev_grav",
    "dip_concord_elev_basement",
    "ew_scarp_grav_hg_lock",
    "grav_tilt_miller_singh",
    # Group C: True Band 2 RTP magnetic tilt, demag, Hessian & axial lock (4)
    "rtp_tilt_miller_singh",
    "rtp_demag_trough",
    "rtp_hess_ridge_s20",
    "cross_physics_axial_order_R",
    # Group D: Stress-resolved 2D Coulomb slip & dilation tendency (3)
    "coulomb_dilation_tendency",
    "coulomb_slip_tendency",
    "geod_2ndinv_raw",
    # Group E: MT clay-cap margin, radioelements & blind geothermometry (5)
    "mt_log_cond_grad",
    "mt_cond_surf_raw",
    "rad_k_over_th",
    "rad_u_over_th_grad",
    "gdr_blind_geotherm_plume",
    # Group F: New KNICKLOQO Thalweg Knickzone, Shoreline-Null, Poisson & Debiased Strain (6)
    "thalweg_knickzone_idx",
    "cross_contour_transgression",
    "lahontan_shoreline_null",
    "poisson_mag_grav_collinearity",
    "poisson_tilt_concordance",
    "coulomb_mesoscale_z",
)

# Province-debiased feature subset: excludes raw regional baseline levels (5, 6, 16, 17, 18, 20)
DEBIASED_INDICES: tuple[int, ...] = tuple(
    i for i in range(len(FEATURE_NAMES)) if i not in (5, 6, 16, 17, 18, 20)
)

# Subsurface + Thalweg-Knickzone feature subset: excludes raw surface slope-Hessian ridges (0, 1, 2)
SUB_KNICK_INDICES: tuple[int, ...] = (
    3, 4, 5, 6, 7,
    8, 9, 10, 11,
    12, 13, 14, 15,
    16, 17, 18,
    19, 20, 21, 22, 23,
    24, 25, 26, 27, 28, 29,
)


def thalweg_concavity_strength(
    field: np.ndarray,
    valid: np.ndarray,
    sigma: float = 1.5,
) -> np.ndarray:
    """Scale-normalized principal positive Hessian eigenvalue ``max(0, lambda_max) * sigma^2``.

    Identifies concave-upward incised drainage thalwegs and ephemeral fan washes
    of width ~``2*sigma`` pixels regardless of azimuth.
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
    lam_max = 0.5 * (tr + rad)
    thalweg = (np.maximum(lam_max, 0.0) * np.float32(sigma * sigma)).astype(np.float32)
    thalweg[~np.asarray(valid, bool)] = 0.0
    return thalweg


def mesoscale_zscore(
    arr: np.ndarray,
    valid: np.ndarray,
    sigma_px: float = 45.0,
    eps: float = 1e-4,
    clip_z: float = 5.0,
) -> np.ndarray:
    """Compute a 4.5 km (45 px) mesoscale locally standardized anomaly inside ``valid``."""
    valid_b = np.asarray(valid, dtype=bool)
    clean = _clean_valid(arr, valid_b)
    reg_mean = gaussian_filter(clean, float(sigma_px)).astype(np.float32)
    diff = (clean - reg_mean).astype(np.float32)
    reg_var = np.maximum(gaussian_filter(diff * diff, float(sigma_px)), 0.0).astype(np.float32)
    reg_sd = np.sqrt(reg_var + np.float32(eps * eps)).astype(np.float32)
    z = np.clip(diff / reg_sd, -float(clip_z), float(clip_z)).astype(np.float32)
    return np.where(valid_b, z, 0.0).astype(np.float32)


def compute_knick_loqo_stack(
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
    """Compute the 30 catalogue-free physical features and 1D localization channels."""
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
    log_slope = np.log(np.maximum(_clean_valid(det_elev_slope, valid), 0.0) + np.float32(1.0)).astype(
        np.float32
    )
    lsy, lsx = _grad_xy(log_slope, valid, sigma=1.0)
    rel_break = np.where(valid, np.hypot(lsy, lsx), 0.0).astype(np.float32)
    del lsy, lsx
    hess_s12 = hessian_ridge_strength(log_slope, valid, sigma=1.2)
    hess_s30 = hessian_ridge_strength(log_slope, valid, sigma=3.0)
    del log_slope

    mu_step = cross_strike_monotonicity(
        det_elev, valid, half_span_px=3, normal_sigma=3.0, elev_floor_m=0.5
    )
    coh_topo, az_topo = coherence_and_strike_deg(det_elev, valid)
    z_clean = np.where(valid, _clean_valid(det_elev, valid), 0.0).astype(np.float32)
    db_pos = np.maximum(_clean_valid(depth_to_base, valid), 0.0)
    log_db = np.where(valid, np.log1p(db_pos), 0.0).astype(np.float32)
    log_db10 = np.log(db_pos + np.float32(10.0)).astype(np.float32)
    del db_pos
    dby, dbx = _grad_xy(log_db10, valid, sigma=2.0)
    base_grad = np.where(valid, np.hypot(dby, dbx), 0.0).astype(np.float32)
    del log_db10

    _put(0, rel_break)
    _put(1, hess_s12)
    _put(2, hess_s30)
    _put(3, mu_step)
    _put(4, coh_topo)
    _put(5, z_clean)
    _put(6, log_db)
    _put(7, base_grad)
    del z_clean, log_db

    # --- Thalweg Knickzone & Cross-Contour Shoreline-Null Deconfounding ---
    thal_15 = thalweg_concavity_strength(det_elev, valid, sigma=1.5)
    thal_30 = thalweg_concavity_strength(det_elev, valid, sigma=3.0)
    thalweg_concav = np.maximum(thal_15, np.float32(0.75) * thal_30).astype(np.float32)
    del thal_15, thal_30
    thalweg_knick = np.where(
        valid,
        _sat(thalweg_concav, 1.8) * _sat(rel_break, 0.045),
        0.0,
    ).astype(np.float32)
    del thalweg_concav

    zy, zx = _grad_xy(det_elev, valid, sigma=2.0)
    znorm = np.hypot(zy, zx)
    az_rad = np.radians(az_topo)
    ty_r = (-np.cos(az_rad)).astype(np.float32)
    tx_r = np.sin(az_rad).astype(np.float32)
    cross_contour = np.where(
        valid,
        np.clip(np.abs(ty_r * zy + tx_r * zx) / (znorm + np.float32(0.35)), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del az_rad, ty_r, tx_r

    # Local 1D topographic localization in [0, 1)
    l_topo = np.where(
        valid,
        0.52 * _sat(hess_s12, 0.06)
        + 0.48 * _sat(rel_break * (0.35 + 0.65 * mu_step) * coh_topo, 0.04),
        0.0,
    ).astype(np.float32)

    # Local 1D thalweg knickzone + cross-contour slope-toe break localization in [0, 1)
    l_knick = np.where(
        valid,
        0.55 * _sat(thalweg_knick * (0.50 + 0.50 * cross_contour), 0.10)
        + 0.45 * _sat(rel_break * (0.40 + 0.60 * cross_contour) * (0.35 + 0.65 * mu_step), 0.04),
        0.0,
    ).astype(np.float32)
    del rel_break, hess_s12, hess_s30, mu_step

    # --- Group B: Polarity-locked footwall concordance & gravity tilt ---
    gy, gx = _grad_xy(grav_anom, valid, sigma=2.0)
    gnorm = np.hypot(gy, gx)
    dip_grav = np.where(
        valid,
        np.clip((zy * gy + zx * gx) / (znorm * gnorm + np.float32(1e-4)), -1.0, 1.0),
        0.0,
    ).astype(np.float32)

    bnorm = np.hypot(dby, dbx)
    dip_base = np.where(
        valid,
        np.clip(-(zy * dby + zx * dbx) / (znorm * bnorm + np.float32(1e-4)), -1.0, 1.0),
        0.0,
    ).astype(np.float32)
    del zy, dby, dbx, bnorm, znorm

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

    lahontan_null = np.where(
        valid,
        ((1.0 - cross_contour) ** 2)
        * np.exp(-base_grad / np.float32(0.04))
        * (1.0 - np.float32(0.75) * grav_tilt),
        0.0,
    ).astype(np.float32)

    _put(8, dip_grav)
    _put(9, dip_base)
    _put(10, ew_lock)
    _put(11, grav_tilt)
    del dip_grav, dip_base, ew_lock

    # --- Group C: True Band 2 RTP tilt/demag/Hessian, Poisson & cross-physics axial lock ---
    u_rtp = gaussian_filter(_clean_valid(rtp, valid), 1.0).astype(np.float32)
    ry, rx = np.gradient(u_rtp)
    r_gh = np.hypot(ry, rx).astype(np.float32)
    ryy, _ = np.gradient(ry)
    _, rxx = np.gradient(rx)
    r_lap = (rxx + ryy).astype(np.float32)
    del u_rtp, ryy, rxx

    # Sliding-window Poisson's-relation magneto-gravity vector collinearity (Chandler et al. 1981)
    dot_mg = (ry * gy + rx * gx).astype(np.float32)
    denom_mg = (r_gh * gnorm + np.float32(1e-4)).astype(np.float32)
    poisson_collin = np.where(
        valid,
        np.clip(np.abs(dot_mg) / denom_mg, 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del ry, rx, gy, gx, gnorm, dot_mg, denom_mg

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

    poisson_tilt_concord = np.where(
        valid,
        poisson_collin * np.sqrt(np.maximum(rtp_tilt * grav_tilt, 0.0)),
        0.0,
    ).astype(np.float32)

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
    del rtp_demag

    # --- Group D: Stress-resolved 2D Coulomb slip & dilation tendency + Mesoscale Debiased Strain ---
    t_dil, t_slip = coulomb_tendencies(comp_strike, geod_shearrate, geod_dilaterate, valid)
    s2i = np.where(valid, np.maximum(_clean_valid(geod_2ndinv, valid), 0.0), 0.0).astype(np.float32)

    s2i_z = mesoscale_zscore(geod_2ndinv, valid, sigma_px=45.0, eps=0.25)
    shr_z = mesoscale_zscore(geod_shearrate, valid, sigma_px=45.0, eps=0.25)
    dil_z = mesoscale_zscore(geod_dilaterate, valid, sigma_px=45.0, eps=0.25)
    dth = np.radians(comp_strike - 15.0)
    cos2_n = (np.cos(dth) ** 2).astype(np.float32)
    sin2_2n = (np.sin(2.0 * dth) ** 2).astype(np.float32)
    shr_local = (1.0 / (1.0 + np.exp(-0.85 * (0.60 * shr_z + 0.40 * s2i_z)))).astype(np.float32)
    dil_local = (1.0 / (1.0 + np.exp(-0.85 * dil_z))).astype(np.float32)
    coulomb_meso = np.where(
        valid,
        (0.55 * cos2_n * dil_local + 0.45 * np.maximum(cos2_n, np.float32(0.85) * sin2_2n) * shr_local)
        * (0.60 + 0.40 * r_axial),
        0.0,
    ).astype(np.float32)
    del comp_strike, r_axial, s2i_z, shr_z, dil_z, dth, cos2_n, sin2_2n, shr_local, dil_local

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
    k_th = np.where(valid, gaussian_filter(_clean_valid(k_th_raw, valid_rad), 2.0), 0.0).astype(
        np.float32
    )
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

    # --- Group F: Put 6 new KNICKLOQO features ---
    _put(24, thalweg_knick)
    _put(25, cross_contour)
    _put(26, lahontan_null)
    _put(27, poisson_collin)
    _put(28, poisson_tilt_concord)
    _put(29, coulomb_meso)
    del thalweg_knick, cross_contour, lahontan_null, coulomb_meso

    # Subsurface Poisson + RTP + Basement + MT 1D localization channel
    l_sub = np.where(
        valid,
        0.38 * _sat(rtp_hess, 0.04)
        + 0.22 * rtp_tilt * (0.60 + 0.40 * poisson_collin)
        + 0.16 * poisson_tilt_concord
        + 0.14 * _sat(base_grad, 0.025)
        + 0.10 * _sat(mt_grad, 0.012) * grav_tilt,
        0.0,
    ).astype(np.float32)
    del rtp_hess, rtp_tilt, poisson_collin, poisson_tilt_concord, base_grad, mt_grad, grav_tilt

    return {
        "X_foot": X,
        "valid": valid,
        "L_topo": l_topo,
        "L_knick": l_knick,
        "L_sub": l_sub,
    }


def calibrate_quadrant_probabilities(
    raw_proba: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    *,
    calib_weight: float = 0.80,
    power_gamma: float = 3.3,
) -> np.ndarray:
    """Label-free within-quadrant empirical quantile calibration of LOQO probabilities."""
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(raw_proba, dtype=np.float32), 0.0, 1.0), 0.0)
    lam = float(np.clip(calib_weight, 0.0, 1.0))
    if lam <= 0.0:
        return p
    gam = float(max(power_gamma, 0.5))
    out = np.zeros_like(p, dtype=np.float32)
    for q in (0, 1, 2, 3):
        m_q = valid_b & (quad == q)
        if not np.any(m_q):
            continue
        q_rank = percentile_rank(p, m_q)
        p_q = p[m_q]
        r_q = q_rank[m_q] ** np.float32(gam)
        out[m_q] = ((1.0 - lam) * p_q + lam * r_q).astype(np.float32)
    return out


def fit_single_loqo(
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
    seed: int = 20261025,
    max_iter: int = 185,
) -> np.ndarray:
    """Fit a single 4-quadrant Leave-One-Quadrant-Out model on ``feature_cols``."""
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

    foot_row_map = np.full(foot.shape, -1, dtype=np.int32)
    foot_row_map[foot] = np.arange(int(foot.sum()), dtype=np.int32)

    raw_proba = np.zeros(foot.shape, dtype=np.float32)
    present_quads = [int(q) for q in (0, 1, 2, 3) if np.any((quad == q) & valid_b)]

    for q in present_quads:
        target_q = (quad == q) & valid_b
        guard = binary_dilation(quad == q, iterations=int(guard_px)) if guard_px > 0 else (quad == q)
        train_dom = valid_b & (quad >= 0) & (quad != q) & (~guard) & (~excl)

        pos_mask = train_dom & lbl
        neg_pool = train_dom & (~lbl) & (d_lbl > float(neg_buffer_px))

        pos_idx = foot_row_map[pos_mask]
        neg_idx = foot_row_map[neg_pool]
        if pos_idx.size == 0 or neg_idx.size == 0:
            raise ValueError(
                f"Quadrant {q} KNICKLOQO training split has empty class: pos={pos_idx.size}, neg={neg_idx.size}"
            )

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

        raw_proba[target_q] = preds

    return raw_proba


def fit_predict_knick_loqo(
    X_foot: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    label_mask: np.ndarray,
    *,
    excluded_mask: np.ndarray | None = None,
    guard_px: int = 12,
    neg_buffer_px: float = 5.0,
    neg_pos_ratio: int = 4,
    seed: int = 20261025,
    max_iter: int = 185,
    w_full: float = 0.15,
    w_debiased: float = 0.35,
    w_sub: float = 0.50,
    calibrate_quadrants: bool = True,
    calib_weight: float = 0.80,
    power_gamma: float = 3.3,
) -> dict[str, np.ndarray]:
    """Fit the 3-branch (Full, Province-Debiased, Subsurface-Knickzone) LOQO ensemble."""
    valid_b = np.asarray(valid, dtype=bool) & np.asarray(footprint, dtype=bool)
    p_full = fit_single_loqo(
        X_foot, footprint, valid_b, quad, label_mask,
        feature_cols=None, excluded_mask=excluded_mask,
        guard_px=guard_px, neg_buffer_px=neg_buffer_px,
        neg_pos_ratio=neg_pos_ratio, seed=int(seed), max_iter=max_iter,
    )
    p_deb = fit_single_loqo(
        X_foot, footprint, valid_b, quad, label_mask,
        feature_cols=DEBIASED_INDICES, excluded_mask=excluded_mask,
        guard_px=guard_px, neg_buffer_px=neg_buffer_px,
        neg_pos_ratio=neg_pos_ratio, seed=int(seed) + 1, max_iter=max_iter,
    )
    p_sub = fit_single_loqo(
        X_foot, footprint, valid_b, quad, label_mask,
        feature_cols=SUB_KNICK_INDICES, excluded_mask=excluded_mask,
        guard_px=guard_px, neg_buffer_px=neg_buffer_px,
        neg_pos_ratio=neg_pos_ratio, seed=int(seed) + 2, max_iter=max_iter,
    )
    raw_proba = (
        np.float32(w_full) * p_full
        + np.float32(w_debiased) * p_deb
        + np.float32(w_sub) * p_sub
    ).astype(np.float32)

    cal_proba = (
        calibrate_quadrant_probabilities(
            raw_proba, valid_b, quad, calib_weight=calib_weight, power_gamma=power_gamma
        )
        if calibrate_quadrants
        else raw_proba.copy()
    )
    return {
        "p_full": p_full,
        "p_debiased": p_deb,
        "p_sub": p_sub,
        "raw_proba": raw_proba,
        "cal_proba": cal_proba,
    }


def build_knick_crest_surface(
    proba_2d: np.ndarray,
    l_topo: np.ndarray,
    l_sub: np.ndarray | None,
    valid: np.ndarray,
    *,
    l_knick: np.ndarray | None = None,
    topo_weight: float = 0.15,
    knick_weight: float = 1.00,
    sub_weight: float = 1.45,
) -> dict[str, np.ndarray]:
    """Combine KNICKLOQO fault probability with 1D knickzone + subsurface Poisson + scarp crests."""
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0), 0.0)
    e_line = np.float32(topo_weight) * np.asarray(l_topo, dtype=np.float32)
    if l_knick is not None:
        e_line = np.maximum(e_line, np.float32(knick_weight) * np.asarray(l_knick, dtype=np.float32))
    if l_sub is not None:
        e_line = np.maximum(e_line, np.float32(sub_weight) * np.asarray(l_sub, dtype=np.float32))

    s_crest = np.where(valid_b, p * (np.float32(0.14) + np.float32(0.86) * e_line), 0.0).astype(
        np.float32
    )
    ridge_1d = directional_ridge_1d(s_crest, valid_b)
    return {
        "S_crest": s_crest,
        "E_line": np.where(valid_b, e_line, 0.0).astype(np.float32),
        "ridge_1d": ridge_1d,
    }
