"""POISSONKNICK: Quadrant-calibrated Leave-One-Quadrant-Out (LOQO) fault detector
with Poisson's-relation gravity-magnetic structural decoupling, cross-canyon
thalweg knickpoint convexity, and Lake Lahontan strandline null deconfounding.

Pre-registered hypothesis & equations: ``docs/HYPOTHESES_20261025_POISSONKNICK.md``.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter

from .coulomb_loqo import (
    FEATURE_NAMES as BASE_FEATURE_NAMES,
    _clean_valid,
    _grad_xy,
    _sat,
    build_crest_surface,
    compute_feature_stack as compute_base_feature_stack,
    directional_ridge_1d,
    fit_predict_loqo,
    gdr_blind_thermal_features,
    spaced_top_mask,
)

POISSONKNICK_EXTRA_NAMES: tuple[str, ...] = (
    "f25_poisson_rtp_vg_decouple",
    "f26_poisson_window_cov",
    "f27_thalweg_knick_convexity",
    "f28_lahontan_obliquity_deconfound",
    "f29_quad_norm_depth_base",
    "f30_quad_norm_cond_grav",
)

FEATURE_NAMES: tuple[str, ...] = BASE_FEATURE_NAMES + POISSONKNICK_EXTRA_NAMES

__all__ = [
    "POISSONKNICK_EXTRA_NAMES",
    "FEATURE_NAMES",
    "compute_poissonknick_extra_channels",
    "compute_poissonknick_features",
    "calibrate_quadrant_probabilities",
    "fit_predict_poissonknick_loqo",
    "build_poissonknick_crest_surface",
    "emit_poissonknick_dots",
]


def _quadrant_robust_zscore(
    arr: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
) -> np.ndarray:
    """Standardize `arr` strictly within each quadrant's unlabeled valid footprint."""
    out = np.zeros_like(arr, dtype=np.float32)
    for q in range(4):
        m = valid & (quad == q) & np.isfinite(arr)
        if not np.any(m):
            continue
        vals = arr[m]
        med = float(np.median(vals))
        q25, q75 = np.percentile(vals, [25.0, 75.0])
        iqr = float(max(q75 - q25, 1e-5))
        out[m] = np.clip((arr[m] - med) / iqr, -6.0, 6.0).astype(np.float32)
    return out


def compute_poissonknick_extra_channels(
    *,
    rtp: np.ndarray,
    grav_slope: np.ndarray,
    grav_vg: np.ndarray,
    det_elev: np.ndarray,
    grav_anom: np.ndarray,
    depth_to_base: np.ndarray,
    cond_surf: np.ndarray,
    det_elev_slope: np.ndarray,
    rel_break_foot: np.ndarray,
    mu_step_foot: np.ndarray,
    rtp_demag_foot: np.ndarray,
    bstep_foot: np.ndarray | None = None,
    rtilt_foot: np.ndarray | None = None,
    cdil_foot: np.ndarray | None = None,
    mtgrad_foot: np.ndarray | None = None,
    l_sub: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute the 6 extra POISSONKNICK features `(N_foot, 6)` + `L_pk_sub`."""
    foot = np.asarray(footprint, dtype=bool)
    foot_idx = np.flatnonzero(foot)
    n_foot = int(foot_idx.size)
    x_extra = np.zeros((n_foot, len(POISSONKNICK_EXTRA_NAMES)), dtype=np.float32)

    def _put_extra(col: int, arr2d: np.ndarray) -> None:
        flat = np.asarray(arr2d, dtype=np.float32).ravel()[foot_idx]
        flat = np.nan_to_num(flat, nan=0.0, posinf=0.0, neginf=0.0)
        x_extra[:, col] = flat

    # --- 1. Poisson's-relation gravity-magnetic decoupling (f25) & window covariance (f26) ---
    rtp_gy, rtp_gx = _grad_xy(rtp, valid, sigma=2.0)
    vg_gy, vg_gx = _grad_xy(grav_vg, valid, sigma=2.0)
    rtp_gmag = np.hypot(rtp_gx, rtp_gy).astype(np.float32)
    vg_gmag = np.hypot(vg_gx, vg_gy).astype(np.float32)

    dot_rtp_vg = rtp_gx * vg_gx + rtp_gy * vg_gy
    cos2_rtp_vg = (dot_rtp_vg * dot_rtp_vg) / (
        (rtp_gmag * rtp_gmag + np.float32(1e-6)) * (vg_gmag * vg_gmag + np.float32(1e-6))
    )
    cos2_rtp_vg = np.clip(cos2_rtp_vg, 0.0, 1.0).astype(np.float32)
    del rtp_gy, rtp_gx, vg_gy, vg_gx, dot_rtp_vg

    gs_clean = np.maximum(_clean_valid(grav_slope, valid), 0.0)
    gs_sat = _sat(gs_clean, float(np.median(gs_clean[valid]) + 1e-4))
    vg_sat = _sat(vg_gmag, float(np.median(vg_gmag[valid]) + 1e-4))
    del gs_clean, vg_gmag

    rtp_demag_2d = np.zeros(foot.shape, dtype=np.float32)
    rtp_demag_2d.ravel()[foot_idx] = rtp_demag_foot
    demag_sat = _sat(rtp_demag_2d, 0.05)
    del rtp_demag_2d

    f25_poisson_decouple = np.where(
        valid,
        gs_sat * vg_sat * (np.float32(1.0) - cos2_rtp_vg) + np.float32(0.50) * gs_sat * demag_sat,
        0.0,
    ).astype(np.float32)
    _put_extra(0, f25_poisson_decouple)
    del vg_sat, cos2_rtp_vg, demag_sat

    vg_s = gaussian_filter(_clean_valid(grav_vg, valid), 2.0).astype(np.float32)
    mean_r = gaussian_filter(rtp_gmag, 9.0).astype(np.float32)
    mean_v = gaussian_filter(vg_s, 9.0).astype(np.float32)
    cov_rv = gaussian_filter(rtp_gmag * vg_s, 9.0) - mean_r * mean_v
    var_r = np.maximum(gaussian_filter(rtp_gmag * rtp_gmag, 9.0) - mean_r * mean_r, 0.0)
    var_v = np.maximum(gaussian_filter(vg_s * vg_s, 9.0) - mean_v * mean_v, 0.0)
    f26_poisson_cov = np.where(
        valid,
        np.clip(cov_rv / (np.sqrt(var_r * var_v) + np.float32(1e-5)), -1.0, 1.0),
        0.0,
    ).astype(np.float32)
    _put_extra(1, f26_poisson_cov)
    del rtp_gmag, vg_s, mean_r, mean_v, cov_rv, var_r, var_v, f26_poisson_cov

    # --- 2. Cross-canyon thalweg longitudinal knickpoint convexity (f27) ---
    ez_y, ez_x = _grad_xy(det_elev, valid, sigma=2.0)
    ez_mag = np.hypot(ez_x, ez_y) + np.float32(1e-5)
    nx = (ez_x / ez_mag).astype(np.float32)
    ny = (ez_y / ez_mag).astype(np.float32)
    sx = -ny
    sy = nx

    e_yy, e_yx = np.gradient(ez_y)
    e_xy, e_xx = np.gradient(ez_x)
    e_xy = np.float32(0.5) * (e_xy + e_yx)
    d2z_ds2 = sx * sx * e_xx + np.float32(2.0) * sx * sy * e_xy + sy * sy * e_yy
    thalweg_conv = _sat(np.maximum(d2z_ds2, 0.0), 0.15)
    del ez_y, ez_x, ez_mag, sx, sy, e_yy, e_yx, e_xy, e_xx, d2z_ds2

    sl_y, sl_x = _grad_xy(det_elev_slope, valid, sigma=1.2)
    sl_yy, sl_yx = np.gradient(sl_y)
    sl_xy, sl_xx = np.gradient(sl_x)
    sl_xy = np.float32(0.5) * (sl_xy + sl_yx)
    d2slope_dn2 = nx * nx * sl_xx + np.float32(2.0) * nx * ny * sl_xy + ny * ny * sl_yy
    knick_crest = _sat(np.maximum(-d2slope_dn2, 0.0), 0.08)
    del nx, ny, sl_yy, sl_yx, sl_xy, sl_xx, d2slope_dn2

    rel_break_2d = np.zeros(foot.shape, dtype=np.float32)
    rel_break_2d.ravel()[foot_idx] = rel_break_foot
    mu_step_2d = np.zeros(foot.shape, dtype=np.float32)
    mu_step_2d.ravel()[foot_idx] = np.maximum(mu_step_foot, 0.0)
    rb_sat = _sat(rel_break_2d, 0.05)

    f27_thalweg_knick = np.where(
        valid,
        thalweg_conv
        * (np.float32(0.60) * knick_crest + np.float32(0.40) * rb_sat)
        * (np.float32(0.45) + np.float32(0.55) * mu_step_2d),
        0.0,
    ).astype(np.float32)
    _put_extra(2, f27_thalweg_knick)
    del thalweg_conv, knick_crest, rel_break_2d, mu_step_2d

    # --- 3. Lake Lahontan strandline null deconfounder (f28) ---
    reg_y, reg_x = _grad_xy(det_elev, valid, sigma=10.0)
    reg_mag = np.hypot(reg_x, reg_y) + np.float32(1e-5)
    sl_mag = np.hypot(sl_x, sl_y) + np.float32(1e-5)
    sin_oblique = np.clip(np.abs(sl_x * reg_y - sl_y * reg_x) / (sl_mag * reg_mag), 0.0, 1.0).astype(np.float32)
    del reg_y, reg_x, reg_mag

    ggy, ggx = _grad_xy(grav_anom, valid, sigma=3.0)
    gg_mag = np.hypot(ggx, ggy) + np.float32(1e-5)
    cos2_scarp_grav = np.clip(((sl_x * ggx + sl_y * ggy) / (sl_mag * gg_mag)) ** 2, 0.0, 1.0).astype(np.float32)
    del ggy, ggx, gg_mag, sl_y, sl_x, sl_mag

    f28_lahontan_deconfound = np.where(
        valid,
        rb_sat * (np.float32(0.55) * sin_oblique + np.float32(0.45) * gs_sat * cos2_scarp_grav),
        0.0,
    ).astype(np.float32)
    _put_extra(3, f28_lahontan_deconfound)
    del rb_sat, sin_oblique, gs_sat, cos2_scarp_grav

    # --- 4. Unlabeled per-quadrant domain-shift standardization (f29, f30) ---
    db_pos = np.maximum(_clean_valid(depth_to_base, valid), 0.0)
    log_db = np.log1p(db_pos).astype(np.float32)
    f29_quad_dbase = _quadrant_robust_zscore(log_db, valid, quad)
    _put_extra(4, f29_quad_dbase)
    del db_pos, log_db, f29_quad_dbase

    z_cond = _quadrant_robust_zscore(_clean_valid(cond_surf, valid), valid, quad)
    z_grav = _quadrant_robust_zscore(_clean_valid(grav_anom, valid), valid, quad)
    f30_quad_cond_grav = np.where(valid, np.clip(z_cond - np.float32(0.50) * z_grav, -6.0, 6.0), 0.0).astype(np.float32)
    _put_extra(5, f30_quad_cond_grav)
    del z_cond, z_grav, f30_quad_cond_grav

    if bstep_foot is not None and rtilt_foot is not None and cdil_foot is not None and mtgrad_foot is not None:
        bstep_2d = np.zeros(foot.shape, dtype=np.float32)
        bstep_2d.ravel()[foot_idx] = bstep_foot
        rtilt_2d = np.zeros(foot.shape, dtype=np.float32)
        rtilt_2d.ravel()[foot_idx] = rtilt_foot
        cdil_2d = np.zeros(foot.shape, dtype=np.float32)
        cdil_2d.ravel()[foot_idx] = cdil_foot
        mtgrad_2d = np.zeros(foot.shape, dtype=np.float32)
        mtgrad_2d.ravel()[foot_idx] = mtgrad_foot
        e_sub_coul = (
            np.float32(0.45) * _sat(bstep_2d, 0.025)
            + np.float32(0.35) * (rtilt_2d * cdil_2d)
            + np.float32(0.20) * _sat(mtgrad_2d, 0.012)
        )
    else:
        e_sub_coul = l_sub

    l_pk_sub = np.where(
        valid,
        np.maximum(
            np.float32(0.2652) * _sat(f27_thalweg_knick, 0.04)
            + np.float32(0.2574) * _sat(f28_lahontan_deconfound, 0.04)
            + np.float32(0.2574) * _sat(f25_poisson_decouple, 0.10)
            + np.float32(0.2200) * e_sub_coul,
            0.0,
        ),
        0.0,
    ).astype(np.float32)

    return {
        "X_extra": x_extra,
        "L_pk_sub": l_pk_sub,
    }


def compute_poissonknick_features(
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
    gdr_csv_path: Path | str,
    footprint: np.ndarray,
    quad: np.ndarray,
) -> dict[str, np.ndarray]:
    """Convenience wrapper returning full `(N_foot, 30)` matrix for unit tests."""
    foot = np.asarray(footprint, dtype=bool)
    valid_init = (
        foot
        & np.isfinite(det_elev) & (det_elev > -1e30)
        & np.isfinite(det_elev_slope) & (det_elev_slope > -1e30)
        & np.isfinite(rtp) & (rtp > -1e30)
    )
    gdr_pkg = gdr_blind_thermal_features(gdr_csv_path, foot.shape, valid_init, sigma_px=14.0)
    base = compute_base_feature_stack(
        rtp=rtp,
        geod_2ndinv=geod_2ndinv,
        grav_slope=grav_slope,
        geod_shearrate=geod_shearrate,
        geod_dilaterate=geod_dilaterate,
        grav_vg=grav_vg,
        det_elev=det_elev,
        grav_anom=grav_anom,
        depth_to_base=depth_to_base,
        cond_surf=cond_surf,
        grav_hg=grav_hg,
        det_elev_slope=det_elev_slope,
        rad_k=rad_k,
        rad_th=rad_th,
        rad_u=rad_u,
        gdr_plume_feat=gdr_pkg["plume_feat"],
        footprint=foot,
    )
    extra = compute_poissonknick_extra_channels(
        rtp=rtp,
        grav_slope=grav_slope,
        grav_vg=grav_vg,
        det_elev=det_elev,
        grav_anom=grav_anom,
        depth_to_base=depth_to_base,
        cond_surf=cond_surf,
        det_elev_slope=det_elev_slope,
        rel_break_foot=base["X_foot"][:, 0],
        mu_step_foot=base["X_foot"][:, 3],
        rtp_demag_foot=base["X_foot"][:, 13],
        bstep_foot=base["X_foot"][:, 7],
        rtilt_foot=base["X_foot"][:, 12],
        cdil_foot=base["X_foot"][:, 16],
        mtgrad_foot=base["X_foot"][:, 19],
        l_sub=base["L_sub"],
        footprint=foot,
        valid=base["valid"],
        quad=quad,
    )
    return {
        "X_foot": np.concatenate([base["X_foot"], extra["X_extra"]], axis=1),
        "valid": base["valid"],
        "L_topo": base["L_topo"],
        "L_sub": base["L_sub"],
        "L_pk_sub": extra["L_pk_sub"],
    }


def calibrate_quadrant_probabilities(
    prob: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    blend_quantile: float = 0.65,
) -> np.ndarray:
    """Align per-quadrant LOQO probability tails using unlabeled footprint quantiles."""
    valid_b = np.asarray(valid, dtype=bool)
    if blend_quantile <= 0.0:
        return np.where(valid_b, np.clip(prob, 0.0, 1.0), 0.0).astype(np.float32)

    pooled_vals = np.sort(prob[valid_b].astype(np.float32))
    n_pooled = pooled_vals.size
    if n_pooled == 0:
        return np.zeros_like(prob, dtype=np.float32)

    out = np.zeros_like(prob, dtype=np.float32)
    for q in range(4):
        mask_q = valid_b & (quad == q)
        n_q = int(mask_q.sum())
        if n_q == 0:
            continue
        p_q = prob[mask_q].astype(np.float32)
        order = np.argsort(p_q, kind="mergesort")
        ranks = np.empty(n_q, dtype=np.float64)
        ranks[order] = (np.arange(n_q, dtype=np.float64) + 0.5) / float(n_q)
        pooled_idx = np.clip((ranks * n_pooled).astype(np.int64), 0, n_pooled - 1)
        p_mapped = pooled_vals[pooled_idx]
        out[mask_q] = ((1.0 - blend_quantile) * p_q + blend_quantile * p_mapped).astype(np.float32)

    out[~valid_b] = 0.0
    return np.clip(out, 0.0, 1.0)


def fit_predict_poissonknick_loqo(
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
    blend_quantile: float = 0.65,
    seed: int = 20261025,
) -> dict[str, np.ndarray]:
    """Train 4-quadrant LOQO model and return both raw and quadrant-calibrated surfaces."""
    raw_prob = fit_predict_loqo(
        X_foot=X_foot,
        footprint=footprint,
        valid=valid,
        quad=quad,
        label_mask=label_mask,
        feature_cols=feature_cols,
        excluded_mask=excluded_mask,
        guard_px=guard_px,
        neg_buffer_px=neg_buffer_px,
        seed=seed,
    )
    cal_prob = calibrate_quadrant_probabilities(
        raw_prob,
        valid=valid,
        quad=quad,
        blend_quantile=blend_quantile,
    )
    return {
        "raw_prob": raw_prob,
        "cal_prob": cal_prob,
    }


def build_poissonknick_crest_surface(
    proba_2d: np.ndarray,
    l_topo: np.ndarray,
    l_pk_sub: np.ndarray,
    valid: np.ndarray,
    *,
    quad: np.ndarray | None = None,
    calibrate_crest: bool = True,
) -> dict[str, np.ndarray]:
    """Combine LOQO fault probability with 1D Poisson/knickpoint/Lahontan-deconfounded crest localization."""
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0), 0.0)
    if calibrate_crest and quad is not None:
        p = calibrate_quadrant_probabilities(p, valid=valid_b, quad=quad, blend_quantile=0.85)
    e_line = np.where(valid_b, np.maximum(np.asarray(l_pk_sub, dtype=np.float32), 0.0), 0.0).astype(np.float32)
    s_crest = np.where(valid_b, p * (np.float32(0.20) + np.float32(0.80) * e_line), 0.0).astype(np.float32)
    if calibrate_crest and quad is not None:
        s_crest = calibrate_quadrant_probabilities(
            s_crest,
            valid=valid_b,
            quad=quad,
            blend_quantile=0.85,
        )
    elif np.any(valid_b):
        smax = float(np.max(s_crest[valid_b]))
        if smax > 0:
            s_crest = np.clip(s_crest / smax, 0.0, 1.0).astype(np.float32)
    ridge_1d = directional_ridge_1d(s_crest, valid_b)
    return {
        "S_crest": np.clip(s_crest, 0.0, 1.0).astype(np.float32),
        "E_line": np.clip(e_line, 0.0, 1.0).astype(np.float32),
        "ridge_1d": ridge_1d,
    }


def emit_poissonknick_dots(
    arm: str,
    s_crest: np.ndarray,
    ridge_1d: np.ndarray,
    l_pk_sub: np.ndarray,
    valid: np.ndarray,
    exclusion_dist: np.ndarray,
    h19_mask: np.ndarray,
    d_h19: np.ndarray,
    target_dots: int = 37_654,
) -> np.ndarray:
    """Emit deterministic 37,654-dot binary mask for one of the 3 pre-registered arms."""
    allowed = valid & (exclusion_dist > 2.0)
    ridge_pool = allowed & ridge_1d

    if arm in ("qcal", "uncal"):
        mask = spaced_top_mask(
            s_crest,
            ridge_pool,
            target_dots,
            min_dist_px=2.8,
            cand_cap=900_000,
        )
    elif arm == "pkdual40":
        n_core = int(round(0.40 * target_dots))  # 15,062
        n_off = target_dots - n_core             # 22,592
        core_mask = spaced_top_mask(
            s_crest,
            allowed & h19_mask,
            n_core,
            min_dist_px=2.8,
            cand_cap=200_000,
        )
        n_rem = target_dots - int(core_mask.sum())
        off_pool = ridge_pool & (d_h19 > 3.0) & (~core_mask)
        off_mask = spaced_top_mask(
            s_crest,
            off_pool,
            n_rem,
            min_dist_px=2.8,
            cand_cap=900_000,
        )
        mask = core_mask | off_mask
    else:
        raise ValueError(f"Unknown POISSONKNICK arm: {arm}")

    if int(mask.sum()) < target_dots:
        shortfall = target_dots - int(mask.sum())
        fill = spaced_top_mask(
            s_crest,
            allowed & (~mask),
            shortfall,
            min_dist_px=2.4,
            cand_cap=900_000,
        )
        mask = mask | fill

    return mask
