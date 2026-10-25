"""POISSONFLEX lane: Province-Calibrated Moving-Window Poisson Gravity-Magnetic
Demagnetization, Buried Basement 2nd-Order Rollover Flexure & Wineglass-Knickpoint
Cross-Fitted LOQO Ridge Model.

Pre-registered BEFORE implementation in ``docs/HYPOTHESES_20261025_POISSONFLEX.md``.

Physical & statistical architecture
-----------------------------------
1. Moving-window Poisson gravity-magnetic relation & hydrothermal magnetite-destruction
   residual (Garland 1951; Cordell & Taylor 1971; Chandler et al. 1981; Blakely 1995):
   couples Band 2 ``rtp`` (M) with Band 11 ``iso_grav_anom_vg`` (dg/dz) and gravity
   horizontal gradient to separate crust-penetrating basement faults and hydrothermally
   demagnetized geothermal conduits from flat-lying remanent volcanic sheets.
2. Buried basement 2nd-order listric rollover flexure & differential-compaction hinge
   (Jachens & Holzer 1982; Gibbs 1984; Jachens & Moring 1990): normal-projected second
   derivative ``n_B^T H(log(B + 20)) n_B`` of Band 15 ``depth_to_base_surf`` localizes
   convex-upward buried footwall shoulders updip of broad 1st-order gravity ramps.
3. Wineglass-canyon saddle knickpoint & strike-steered line integral (Bull 2007;
   Kirby & Whipple 2012): opposite-sign Hessian principal curvatures ``lambda_1 > 0 > lambda_2``
   integrated along regional basement/gravity strike bridge stream-dissected interfluves.
4. Unsupervised within-quadrant covariate rank alignment + Bolstad cross-quadrant
   quantile probability equalization: eliminates ``#IR-92-NE-QUADRANT-LOQO-COLLAPSE``
   using strictly unlabeled covariates and unlabeled out-of-quadrant predictions.

Strict zero-leakage invariant: no fault catalogue array enters feature computation,
and ``dist_known_fault_px`` in GDR #1391 is never read.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import (
    binary_dilation,
    distance_transform_edt,
    gaussian_filter,
)
from scipy.stats import rankdata
from sklearn.ensemble import HistGradientBoostingClassifier

from .breakline import spaced_top_mask
from .coulomb_loqo import (
    _grad_xy,
    _sat,
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

FEATURE_NAMES: tuple[str, ...] = (
    # Group A: Moving-window Poisson gravity-magnetic coupling & demagnetization
    "f01_poisson_r_pg",
    "f02_poisson_alpha_jump",
    "f03_poisson_demag_conduit",
    "f04_poisson_concord_step",
    # Group B: Buried basement 2nd-order listric rollover flexure & compaction hinge
    "f05_base_shoulder_curv",
    "f06_base_hess_ridge",
    "f07_compaction_flex_lock",
    "f08_base_step_grad",
    # Group C: Wineglass-canyon saddle knickpoint & strike-steered line integral
    "f09_knickpoint_saddle",
    "f10_knick_strike_integral",
    "f11_valley_pinch_break",
    # Group D: Multi-scale topographic scarp ridges & footwall polarity concordance
    "f12_rel_log_slope_break",
    "f13_hess_ridge_s12",
    "f14_hess_ridge_s30",
    "f15_step_monotonicity_600m",
    "f16_dip_concord_grav",
    "f17_dip_concord_base",
    "f18_ew_polarity_lock",
    "f19_grav_tilt_edge",
    # Group E: True Band 2 RTP contacts & province-aligned Mohr-Coulomb criticality
    "f20_rtp_tilt_edge",
    "f21_rtp_hess_ridge",
    "f22_cross_physics_axial_lock",
    "f23_coulomb_ext_aligned",
    "f24_coulomb_shear_aligned",
    "f25_strain_2ndinv_qrank",
    # Group F: Province-aligned basin context, MT clay-cap, radioelements & blind GDR
    "f26_det_elev_qrank",
    "f27_depth_base_qrank",
    "f28_mt_claycap_grad",
    "f29_rad_contact_grad",
    "f30_gdr_blind_plume",
)

__all__ = [
    "FEATURE_NAMES",
    "within_quadrant_rank",
    "bolstad_equalize_quadrants",
    "moving_window_poisson",
    "basement_rollover_flexure",
    "knickpoint_saddle_and_integral",
    "compute_poissonflex_stack",
    "compute_poissonflex_from_files",
    "fit_predict_loqo_poissonflex",
    "build_poissonflex_crest_surface",
    "select_nested_oof_budget",
    "spaced_top_mask",
]


def within_quadrant_rank(
    field: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
) -> np.ndarray:
    """Strictly label-free, zero-cross-quadrant empirical quantile in [0, 1].

    Each quadrant ``q in {0, 1, 2, 3}`` is ranked independently using ONLY its own
    unlabeled valid pixels, aligning domain marginals across tectonic provinces.
    """
    arr = np.asarray(field)
    valid_b = np.asarray(valid, dtype=bool) & np.isfinite(arr)
    out = np.zeros(arr.shape, dtype=np.float32)
    present = [int(q) for q in np.unique(quad[valid_b]) if int(q) >= 0]
    for q in present:
        m = valid_b & (quad == q)
        vals = arr[m]
        if vals.size <= 1:
            out[m] = 0.5 if vals.size == 1 else 0.0
            continue
        ranks = rankdata(vals, method="average")
        out[m] = ((ranks - 1.0) / float(vals.size - 1)).astype(np.float32)
    return out


def bolstad_equalize_quadrants(
    proba_2d: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    *,
    n_knots: int = 2049,
) -> np.ndarray:
    """Label-free Bolstad quantile normalization of out-of-quadrant probabilities.

    Maps each quadrant's predicted score vector monotonically onto the mean
    inverse-CDF across quadrants on ``[0, 1]``:
      1. Preserves 100% of within-quadrant classifier ranking (strictly monotone);
      2. Keeps authentic probability tail sharpness (low median, crisp top-0.5% tail);
      3. Allocates high-probability tails across quadrants strictly in proportion to
         valid footprint area, curing ``#IR-92-NE-QUADRANT-LOQO-COLLAPSE``.
    """
    p = np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0)
    valid_b = np.asarray(valid, dtype=bool)
    present = [int(q) for q in (0, 1, 2, 3) if np.any(valid_b & (quad == q))]
    if len(present) <= 1:
        return np.where(valid_b, p, 0.0).astype(np.float32)

    grid_u = np.linspace(0.0, 1.0, int(n_knots), dtype=np.float64)
    q_curves = []
    for q in present:
        vals = p[valid_b & (quad == q)].astype(np.float64)
        q_curves.append(np.quantile(vals, grid_u))
    ref_curve = np.mean(np.vstack(q_curves), axis=0)
    # Enforce tiny strict monotonicity floor so flat plateaus stay tie-safe
    ref_curve = np.maximum.accumulate(ref_curve)

    out = np.zeros(p.shape, dtype=np.float32)
    for q in present:
        m = valid_b & (quad == q)
        vals = p[m]
        if vals.size <= 1:
            out[m] = vals
            continue
        u = (rankdata(vals, method="average") - 1.0) / float(vals.size - 1)
        out[m] = np.interp(u, grid_u, ref_curve).astype(np.float32)
    return np.clip(out, 0.0, 1.0).astype(np.float32)


def moving_window_poisson(
    rtp: np.ndarray,
    grav_vg: np.ndarray,
    grav_slope: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    *,
    window_sigma_px: float = 4.0,
) -> dict[str, np.ndarray]:
    """Moving-window Poisson coupling (Band 2 RTP vs Band 11 vertical gravity gradient).

    Under Poisson's relation, M(x) = A(x) + alpha * dg/dz(x) with alpha ~ dJ / drho.
    Returns:
      - ``r_pg``: local correlation in [-1, 1]
      - ``alpha_jump``: ||grad arsinh(alpha / scale)|| across concealed terrane contacts
      - ``demag_conduit``: high gravity-gradient + decoupled RTP + positive RTP Laplacian
      - ``concord_step``: coupled positive Poisson basement fault contact
      - ``rtp_tilt``: Miller-Singh coherence-weighted RTP contact edge
      - ``rtp_hess``: Hessian ridge of log(1 + ||grad_h RTP||)
    """
    valid_b = np.asarray(valid, dtype=bool)
    m_clean = _clean_valid(rtp, valid_b).astype(np.float32)
    gz_clean = _clean_valid(grav_vg, valid_b).astype(np.float32)
    gs_clean = np.maximum(_clean_valid(grav_slope, valid_b), 0.0).astype(np.float32)

    sig = float(window_sigma_px)
    mu_m = gaussian_filter(m_clean, sig, mode="nearest")
    mu_g = gaussian_filter(gz_clean, sig, mode="nearest")
    cov_mg = gaussian_filter(m_clean * gz_clean, sig, mode="nearest") - mu_m * mu_g
    var_m = np.maximum(gaussian_filter(m_clean * m_clean, sig, mode="nearest") - mu_m * mu_m, 0.0)
    var_g = np.maximum(gaussian_filter(gz_clean * gz_clean, sig, mode="nearest") - mu_g * mu_g, 0.0)
    del mu_m, mu_g, gz_clean

    eps_var = np.float32(1e-3)
    r_pg = (cov_mg / (np.sqrt(var_m * var_g) + np.float32(1e-4))).astype(np.float32)
    r_pg = np.where(valid_b, np.clip(r_pg, -1.0, 1.0), 0.0).astype(np.float32)

    vg_med = float(np.median(var_g[valid_b])) if valid_b.any() else 1.0
    reg_g = np.float32(max(0.05 * vg_med, 1e-3))
    alpha = (cov_mg / (var_g + reg_g)).astype(np.float32)
    del cov_mg, var_m, var_g
    a_scale = float(np.percentile(np.abs(alpha[valid_b]), 75)) if valid_b.any() else 10.0
    a_scale = max(a_scale, 1.0)
    alpha_comp = np.arcsinh(alpha / np.float32(a_scale)).astype(np.float32)
    del alpha
    ay, ax = _grad_xy(alpha_comp, valid_b, sigma=1.5)
    alpha_jump = np.where(valid_b, np.hypot(ay, ax), 0.0).astype(np.float32)
    del alpha_comp, ay, ax

    # RTP derivatives for Laplacian demagnetization trough & Miller-Singh tilt
    u_rtp = gaussian_filter(m_clean, 1.0, mode="nearest").astype(np.float32)
    del m_clean
    ry, rx = np.gradient(u_rtp)
    r_gh = np.hypot(ry, rx).astype(np.float32)
    ryy, _ = np.gradient(ry)
    _, rxx = np.gradient(rx)
    r_lap = (rxx + ryy).astype(np.float32)
    del u_rtp, ry, rx, ryy, rxx

    coh_rtp, az_rtp = coherence_and_strike_deg(rtp, valid_b)
    rtp_tilt = np.where(
        valid_b,
        (r_gh / np.sqrt(r_gh * r_gh + r_lap * r_lap + np.float32(1.5 ** 2))) * coh_rtp,
        0.0,
    ).astype(np.float32)
    rtp_hess = hessian_ridge_strength(np.log1p(r_gh), valid_b, sigma=2.0)
    del r_gh

    gs_q = within_quadrant_rank(gs_clean, valid_b, quad)
    del gs_clean
    lap_pos_sat = _sat(np.maximum(r_lap, 0.0), 1.5)
    del r_lap
    demag_conduit = np.where(
        valid_b,
        gs_q * (np.float32(1.0) - np.abs(r_pg)) * (np.float32(0.25) + np.float32(0.75) * lap_pos_sat),
        0.0,
    ).astype(np.float32)
    concord_step = np.where(
        valid_b,
        gs_q * np.maximum(r_pg, 0.0) * rtp_tilt,
        0.0,
    ).astype(np.float32)
    del gs_q, lap_pos_sat

    return {
        "r_pg": r_pg,
        "alpha_jump": alpha_jump,
        "demag_conduit": demag_conduit,
        "concord_step": concord_step,
        "rtp_tilt": rtp_tilt,
        "rtp_hess": rtp_hess,
        "coh_rtp": coh_rtp,
        "az_rtp": az_rtp,
    }


def basement_rollover_flexure(
    depth_to_base: np.ndarray,
    det_elev: np.ndarray,
    valid: np.ndarray,
    *,
    curv_sigma_px: float = 2.5,
) -> dict[str, np.ndarray]:
    """2nd-order buried basement rollover shoulder & differential-compaction hinge."""
    valid_b = np.asarray(valid, dtype=bool)
    db_pos = np.maximum(_clean_valid(depth_to_base, valid_b), 0.0).astype(np.float32)
    log_b20 = np.log(db_pos + np.float32(20.0)).astype(np.float32)
    log_b10 = np.log(db_pos + np.float32(10.0)).astype(np.float32)
    del db_pos

    # Broad basinward dip normal n_B of buried basement surface
    by_broad, bx_broad = _grad_xy(log_b20, valid_b, sigma=3.5)
    bnorm_broad = np.hypot(by_broad, bx_broad) + np.float32(1e-5)
    ny = (by_broad / bnorm_broad).astype(np.float32)
    nx = (bx_broad / bnorm_broad).astype(np.float32)
    del by_broad, bx_broad, bnorm_broad

    # Hessian of log(B + 20)
    sm_b = gaussian_filter(log_b20, float(curv_sigma_px), mode="nearest").astype(np.float32)
    by, bx = np.gradient(sm_b)
    byy, byx = np.gradient(by)
    bxy, bxx = np.gradient(bx)
    bhxy = (np.float32(0.5) * (byx + bxy)).astype(np.float32)
    s2 = np.float32(curv_sigma_px * curv_sigma_px)
    # Normal-projected 2nd derivative: > 0 on convex-upward buried footwall shoulder!
    kappa_b_perp = ((ny * ny * byy + np.float32(2.0) * ny * nx * bhxy + nx * nx * bxx) * s2).astype(np.float32)
    kappa_b_perp = np.where(valid_b, kappa_b_perp, 0.0).astype(np.float32)
    del sm_b, by, bx, byy, byx, bxy, bxx, bhxy

    # Principal positive ridge of log(B + 20) (convex-upward shoulder = negative Hessian of -log(B+20))
    base_hess_ridge = hessian_ridge_strength(-log_b20, valid_b, sigma=2.0)
    del log_b20

    # Normal-projected surface curvature along same basement dip normal (differential compaction monocline)
    z_clean = _clean_valid(det_elev, valid_b).astype(np.float32)
    sm_z = gaussian_filter(z_clean, float(curv_sigma_px), mode="nearest").astype(np.float32)
    del z_clean
    zy, zx = np.gradient(sm_z)
    zyy, zyx = np.gradient(zy)
    zxy, zxx = np.gradient(zx)
    zhxy = (np.float32(0.5) * (zyx + zxy)).astype(np.float32)
    kappa_z_perp = ((ny * ny * zyy + np.float32(2.0) * ny * nx * zhxy + nx * nx * zxx) * s2).astype(np.float32)
    del sm_z, zy, zx, zyy, zyx, zxy, zxx, zhxy, ny, nx

    cb = float(np.percentile(np.abs(kappa_b_perp[valid_b]), 75)) if valid_b.any() else 0.05
    cz = float(np.percentile(np.abs(kappa_z_perp[valid_b]), 75)) if valid_b.any() else 2.0
    cb = max(cb, 1e-3)
    cz = max(cz, 0.1)
    # Convex-upward surface monocline (-kappa_z_perp > 0) locked to buried footwall shoulder (+kappa_b_perp > 0)
    compaction_lock = np.where(
        valid_b,
        np.tanh(-kappa_z_perp / np.float32(cz)) * np.tanh(kappa_b_perp / np.float32(cb)),
        0.0,
    ).astype(np.float32)
    del kappa_z_perp

    dby, dbx = _grad_xy(log_b10, valid_b, sigma=2.0)
    base_step_grad = np.where(valid_b, np.hypot(dby, dbx), 0.0).astype(np.float32)
    coh_base, az_base = coherence_and_strike_deg(log_b10, valid_b)
    del log_b10

    return {
        "shoulder_curv": kappa_b_perp,
        "base_hess_ridge": base_hess_ridge,
        "compaction_lock": compaction_lock,
        "base_step_grad": base_step_grad,
        "dby": dby,
        "dbx": dbx,
        "coh_base": coh_base,
        "az_base": az_base,
    }


def knickpoint_saddle_and_integral(
    det_elev: np.ndarray,
    strike_deg: np.ndarray,
    valid: np.ndarray,
    *,
    hess_sigma_px: float = 1.5,
    along_sigma_px: float = 6.0,
    cross_sigma_px: float = 1.0,
) -> dict[str, np.ndarray]:
    """Opposite-sign Hessian saddle knickpoint & strike-steered cross-canyon integral.

    At a faulted wineglass canyon mouth, transverse valley curvature is concave
    (``lambda_1 > 0``) while longitudinal thalweg curvature is convex (``lambda_2 < 0``).
    An 8-orientation steerable anisotropic Gaussian filter bank integrates collinear
    knickpoints across adjacent canyons along local basement/gravity strike.
    """
    valid_b = np.asarray(valid, dtype=bool)
    z = gaussian_filter(_clean_valid(det_elev, valid_b), float(hess_sigma_px), mode="nearest").astype(np.float32)
    zy, zx = np.gradient(z)
    zyy, zyx = np.gradient(zy)
    zxy, zxx = np.gradient(zx)
    zhxy = (np.float32(0.5) * (zyx + zxy)).astype(np.float32)
    del z, zy, zx, zyx, zxy

    tr = (zxx + zyy).astype(np.float32)
    disc = np.sqrt((zxx - zyy) ** 2 + np.float32(4.0) * zhxy * zhxy).astype(np.float32)
    del zxx, zyy, zhxy
    s2 = np.float32(hess_sigma_px * hess_sigma_px)
    lam1 = (np.float32(0.5) * (tr + disc) * s2).astype(np.float32)
    lam2 = (np.float32(0.5) * (tr - disc) * s2).astype(np.float32)
    del tr, disc

    saddle = np.sqrt(np.maximum(lam1, 0.0) * np.maximum(-lam2, 0.0)).astype(np.float32)
    del lam1, lam2
    saddle = np.where(valid_b, saddle, 0.0).astype(np.float32)

    # 8-orientation steerable anisotropic Gaussian line-integral bank on [0, 180)
    # Compass strike az: 0 = N-S (along row y), 90 = E-W (along col x)
    n_orient = 8
    step_deg = 180.0 / n_orient  # 22.5 deg
    rad = max(int(np.ceil(2.5 * float(along_sigma_px))), 2)
    yy, xx = np.mgrid[-rad : rad + 1, -rad : rad + 1].astype(np.float32)
    az_mod = (np.asarray(strike_deg, dtype=np.float32) % np.float32(180.0))
    pos = az_mod / np.float32(step_deg)
    k0 = (np.floor(pos).astype(np.int32)) % n_orient
    frac = (pos - np.floor(pos)).astype(np.float32)
    del az_mod, pos

    from scipy.ndimage import convolve

    steered = np.zeros(saddle.shape, dtype=np.float32)
    for k in range(n_orient):
        th = np.deg2rad(k * step_deg)
        # Unit strike vector in (dy, dx): az=0 -> (-1, 0) N-S; az=90 -> (0, 1) E-W
        ty = np.float32(-np.cos(th))
        tx = np.float32(np.sin(th))
        u_along = yy * ty + xx * tx
        u_cross = -yy * tx + xx * ty
        kern = np.exp(
            -0.5 * ((u_along / np.float32(along_sigma_px)) ** 2 + (u_cross / np.float32(cross_sigma_px)) ** 2)
        ).astype(np.float32)
        kern /= np.sum(kern)
        resp_k = convolve(saddle, kern, mode="nearest")
        sel_curr = k0 == k
        if np.any(sel_curr):
            steered[sel_curr] += (np.float32(1.0) - frac[sel_curr]) * resp_k[sel_curr]
        sel_prev = k0 == ((k - 1) % n_orient)
        if np.any(sel_prev):
            steered[sel_prev] += frac[sel_prev] * resp_k[sel_prev]
        del resp_k
    del k0, frac
    steered = np.where(valid_b, steered, 0.0).astype(np.float32)

    return {
        "knickpoint_saddle": saddle,
        "knick_strike_integral": steered,
    }


def compute_poissonflex_stack(
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
    quad: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute ``(N_foot, 30)`` float32 POISSONFLEX matrix + 1D crest channels."""
    foot = np.asarray(footprint, dtype=bool)
    valid = (
        foot
        & np.isfinite(det_elev) & (det_elev > -1e30)
        & np.isfinite(det_elev_slope) & (det_elev_slope > -1e30)
        & np.isfinite(rtp) & (rtp > -1e30)
    )
    foot_idx = np.flatnonzero(foot)
    X = np.zeros((int(foot_idx.size), len(FEATURE_NAMES)), dtype=np.float32)

    def _put(col: int, arr2d: np.ndarray) -> None:
        flat = np.asarray(arr2d, dtype=np.float32).ravel()[foot_idx]
        X[:, col] = np.nan_to_num(flat, nan=0.0, posinf=0.0, neginf=0.0)

    # --- Group A: Moving-window Poisson gravity-magnetic coupling & demagnetization ---
    pois = moving_window_poisson(rtp, grav_vg, grav_slope, valid, quad, window_sigma_px=4.0)
    _put(0, pois["r_pg"])
    _put(1, pois["alpha_jump"])
    _put(2, pois["demag_conduit"])
    _put(3, pois["concord_step"])

    # --- Group B: Buried basement 2nd-order listric rollover flexure & compaction ---
    flex = basement_rollover_flexure(depth_to_base, det_elev, valid, curv_sigma_px=2.5)
    _put(4, flex["shoulder_curv"])
    _put(5, flex["base_hess_ridge"])
    _put(6, flex["compaction_lock"])
    _put(7, flex["base_step_grad"])

    # --- Regional strike across subsurface + topography for knickpoint steering & axial lock ---
    coh_topo, az_topo = coherence_and_strike_deg(det_elev, valid)
    coh_grav, az_grav = coherence_and_strike_deg(grav_anom, valid)
    _, sub_strike = cross_physics_axial_order(
        [pois["az_rtp"], az_grav, flex["az_base"]],
        [pois["coh_rtp"], coh_grav, flex["coh_base"]],
        valid,
    )
    r_axial, comp_strike = cross_physics_axial_order(
        [az_topo, pois["az_rtp"], az_grav, flex["az_base"]],
        [coh_topo, pois["coh_rtp"], np.float32(0.8) * coh_grav, np.float32(0.8) * flex["coh_base"]],
        valid,
    )
    del az_topo, az_grav, coh_grav

    # --- Group C: Wineglass-canyon saddle knickpoint & strike-steered line integral ---
    knick = knickpoint_saddle_and_integral(det_elev, sub_strike, valid, hess_sigma_px=1.5, along_sigma_px=6.0)
    del sub_strike
    log_slope = np.log(np.maximum(_clean_valid(det_elev_slope, valid), 0.0) + np.float32(1.0)).astype(np.float32)
    lsy, lsx = _grad_xy(log_slope, valid, sigma=1.0)
    rel_break = np.where(valid, np.hypot(lsy, lsx), 0.0).astype(np.float32)
    del lsy, lsx

    k_c0 = float(np.percentile(knick["knickpoint_saddle"][valid], 85)) if valid.any() else 1.0
    k_c0 = max(k_c0, 1e-3)
    valley_pinch = np.where(
        valid,
        _sat(knick["knickpoint_saddle"], k_c0) * rel_break,
        0.0,
    ).astype(np.float32)
    _put(8, knick["knickpoint_saddle"])
    _put(9, knick["knick_strike_integral"])
    _put(10, valley_pinch)

    # --- Group D: Multi-scale topographic scarp ridges & footwall polarity concordance ---
    hess_s12 = hessian_ridge_strength(log_slope, valid, sigma=1.2)
    hess_s30 = hessian_ridge_strength(log_slope, valid, sigma=3.0)
    del log_slope
    mu_step = cross_strike_monotonicity(det_elev, valid, half_span_px=3, normal_sigma=3.0, elev_floor_m=0.5)

    zy, zx = _grad_xy(det_elev, valid, sigma=2.0)
    znorm = np.hypot(zy, zx)
    gy, gx = _grad_xy(grav_anom, valid, sigma=2.0)
    gnorm = np.hypot(gy, gx)
    dip_grav = np.where(valid, np.clip((zy * gy + zx * gx) / (znorm * gnorm + np.float32(1e-4)), -1.0, 1.0), 0.0).astype(np.float32)
    bnorm = np.hypot(flex["dby"], flex["dbx"])
    dip_base = np.where(
        valid,
        np.clip(-(zy * flex["dby"] + zx * flex["dbx"]) / (znorm * bnorm + np.float32(1e-4)), -1.0, 1.0),
        0.0,
    ).astype(np.float32)
    del zy, gy, gx, gnorm, bnorm, znorm

    b18_clean = _clean_valid(grav_hg, valid)
    ew_lock = np.where(valid, np.tanh(zx / np.float32(8.0)) * np.tanh(b18_clean / np.float32(1.5)), 0.0).astype(np.float32)
    del zx, b18_clean

    gs_clean = np.maximum(_clean_valid(grav_slope, valid), 0.0)
    gvg_clean = _clean_valid(grav_vg, valid)
    grav_tilt = np.where(
        valid,
        gs_clean / np.sqrt(gs_clean * gs_clean + (np.float32(0.05) * gvg_clean) ** 2 + np.float32(0.02 ** 2)),
        0.0,
    ).astype(np.float32)
    del gs_clean, gvg_clean

    _put(11, rel_break)
    _put(12, hess_s12)
    _put(13, hess_s30)
    _put(14, mu_step)
    _put(15, dip_grav)
    _put(16, dip_base)
    _put(17, ew_lock)
    _put(18, grav_tilt)
    del dip_grav, dip_base, ew_lock, hess_s30

    # --- Group E: True RTP contacts & province-aligned Mohr-Coulomb criticality ---
    _put(19, pois["rtp_tilt"])
    _put(20, pois["rtp_hess"])
    _put(21, r_axial)

    th_diff = np.deg2rad(comp_strike - np.float32(15.0))
    ext_geom = (np.cos(th_diff) ** 2).astype(np.float32)
    shear_geom = (np.sin(np.float32(2.0) * th_diff) ** 2).astype(np.float32)
    del th_diff, comp_strike

    dil_q = within_quadrant_rank(_clean_valid(geod_dilaterate, valid), valid, quad)
    shr_q = within_quadrant_rank(_clean_valid(geod_shearrate, valid), valid, quad)
    s2i_q = within_quadrant_rank(_clean_valid(geod_2ndinv, valid), valid, quad)

    coul_ext = np.where(valid, r_axial * ext_geom * (np.float32(0.35) + np.float32(0.65) * dil_q), 0.0).astype(np.float32)
    coul_shr = np.where(valid, r_axial * shear_geom * (np.float32(0.35) + np.float32(0.65) * shr_q), 0.0).astype(np.float32)
    del ext_geom, shear_geom, dil_q, shr_q, r_axial
    _put(22, coul_ext)
    _put(23, coul_shr)
    _put(24, s2i_q)
    del coul_ext, coul_shr, s2i_q

    # --- Group F: Province-aligned basin context, MT clay-cap, radioelements & GDR ---
    z_q = within_quadrant_rank(_clean_valid(det_elev, valid), valid, quad)
    db_q = within_quadrant_rank(np.maximum(_clean_valid(depth_to_base, valid), 0.0), valid, quad)
    _put(25, z_q)
    _put(26, db_q)
    del z_q, db_q

    cond_clean = np.maximum(_clean_valid(cond_surf, valid), np.float32(0.1))
    cy, cx = _grad_xy(np.log(cond_clean).astype(np.float32), valid, sigma=2.0)
    mt_grad = np.where(valid, np.hypot(cy, cx), 0.0).astype(np.float32)
    del cond_clean, cy, cx

    valid_rad = (
        valid
        & np.isfinite(rad_k)
        & np.isfinite(rad_th)
        & np.isfinite(rad_u)
        & (np.asarray(rad_th) > 0)
    )
    k_th = np.where(valid_rad, np.asarray(rad_k, np.float32) / (np.asarray(rad_th, np.float32) + np.float32(1.0)), 0.0).astype(np.float32)
    u_th = np.where(valid_rad, np.asarray(rad_u, np.float32) / (np.asarray(rad_th, np.float32) + np.float32(1.0)), 0.0).astype(np.float32)
    ky, kx = _grad_xy(k_th, valid_rad, sigma=2.0)
    uy, ux = _grad_xy(u_th, valid_rad, sigma=2.0)
    rad_grad = np.where(valid, np.hypot(ky, kx) + np.hypot(uy, ux), 0.0).astype(np.float32)
    del k_th, u_th, ky, kx, uy, ux, valid_rad

    _put(27, mt_grad)
    _put(28, rad_grad)
    _put(29, np.where(valid, np.asarray(gdr_plume_feat, np.float32), 0.0).astype(np.float32))
    del rad_grad

    # --- 1D Structural Crest Localizers (scarp+knickpoint AND Poisson+flexure+RTP+MT) ---
    ki_c0 = float(np.percentile(knick["knick_strike_integral"][valid], 85)) if valid.any() else 0.5
    ki_c0 = max(ki_c0, 1e-3)
    l_scarp_knick = np.where(
        valid,
        0.45 * _sat(hess_s12, 0.06)
        + 0.30 * _sat(rel_break * (0.35 + 0.65 * mu_step) * coh_topo, 0.04)
        + 0.25 * _sat(knick["knick_strike_integral"], ki_c0),
        0.0,
    ).astype(np.float32)
    del hess_s12, rel_break, mu_step, coh_topo, knick, valley_pinch

    aj_c0 = float(np.percentile(pois["alpha_jump"][valid], 85)) if valid.any() else 0.1
    aj_c0 = max(aj_c0, 1e-3)
    bh_c0 = float(np.percentile(flex["base_hess_ridge"][valid], 85)) if valid.any() else 0.02
    bh_c0 = max(bh_c0, 1e-4)
    l_poisson_flex = np.where(
        valid,
        0.30 * _sat(flex["base_hess_ridge"], bh_c0)
        + 0.25 * _sat(pois["alpha_jump"], aj_c0)
        + 0.20 * pois["demag_conduit"]
        + 0.15 * _sat(pois["rtp_hess"], 0.04)
        + 0.10 * _sat(mt_grad, 0.012) * grav_tilt,
        0.0,
    ).astype(np.float32)

    return {
        "X_foot": X,
        "valid": valid,
        "L_scarp_knick": l_scarp_knick,
        "L_poisson_flex": l_poisson_flex,
    }


def _read_f32_band(stack_path, band: int) -> np.ndarray:
    import rasterio

    with rasterio.open(stack_path) as ds:
        return ds.read(int(band), masked=True).filled(np.nan).astype(np.float32)


def compute_poissonflex_from_files(
    stack_path,
    rad_path,
    gdr_csv_path,
    footprint: np.ndarray,
    quad: np.ndarray,
    *,
    out_x: np.ndarray | None = None,
) -> dict[str, np.ndarray | dict]:
    """Stream bands one group at a time (< 750 MB peak RSS on 3730x3292 grid)."""
    import gc
    import rasterio

    foot = np.asarray(footprint, dtype=bool)
    foot_idx = np.flatnonzero(foot)
    n_foot = int(foot_idx.size)
    X = out_x if out_x is not None else np.zeros((n_foot, len(FEATURE_NAMES)), dtype=np.float32)
    assert X.shape == (n_foot, len(FEATURE_NAMES))

    def _put(col: int, arr2d: np.ndarray) -> None:
        flat = np.asarray(arr2d, dtype=np.float32).ravel()[foot_idx]
        X[:, col] = np.nan_to_num(flat, nan=0.0, posinf=0.0, neginf=0.0)

    # Establish valid mask using Bands 2, 12, 19
    rtp = _read_f32_band(stack_path, 2)
    det_elev = _read_f32_band(stack_path, 12)
    det_elev_slope = _read_f32_band(stack_path, 19)
    valid = (
        foot
        & np.isfinite(det_elev) & (det_elev > -1e30)
        & np.isfinite(det_elev_slope) & (det_elev_slope > -1e30)
        & np.isfinite(rtp) & (rtp > -1e30)
    )
    del det_elev_slope
    gc.collect()

    # --- Group A: Moving-window Poisson gravity-magnetic coupling & demagnetization ---
    grav_vg = _read_f32_band(stack_path, 11)
    grav_slope = _read_f32_band(stack_path, 5)
    pois = moving_window_poisson(rtp, grav_vg, grav_slope, valid, quad, window_sigma_px=4.0)
    del rtp
    _put(0, pois["r_pg"])
    _put(1, pois["alpha_jump"])
    _put(2, pois["demag_conduit"])
    _put(3, pois["concord_step"])
    _put(19, pois["rtp_tilt"])
    _put(20, pois["rtp_hess"])

    gs_clean = np.maximum(_clean_valid(grav_slope, valid), 0.0)
    gvg_clean = _clean_valid(grav_vg, valid)
    del grav_slope, grav_vg
    grav_tilt = np.where(
        valid,
        gs_clean / np.sqrt(gs_clean * gs_clean + (np.float32(0.05) * gvg_clean) ** 2 + np.float32(0.02 ** 2)),
        0.0,
    ).astype(np.float32)
    del gs_clean, gvg_clean
    _put(18, grav_tilt)

    aj_c0 = max(float(np.percentile(pois["alpha_jump"][valid], 85)) if valid.any() else 0.1, 1e-3)
    l_pf_accum = (
        0.25 * _sat(pois["alpha_jump"], aj_c0)
        + 0.20 * pois["demag_conduit"]
        + 0.15 * _sat(pois["rtp_hess"], 0.04)
    ).astype(np.float32)
    az_rtp, coh_rtp = pois["az_rtp"], pois["coh_rtp"]
    del pois
    gc.collect()

    # --- Group B: Buried basement 2nd-order rollover flexure & compaction ---
    depth_to_base = _read_f32_band(stack_path, 15)
    flex = basement_rollover_flexure(depth_to_base, det_elev, valid, curv_sigma_px=2.5)
    _put(4, flex["shoulder_curv"])
    _put(5, flex["base_hess_ridge"])
    _put(6, flex["compaction_lock"])
    _put(7, flex["base_step_grad"])
    _put(25, within_quadrant_rank(_clean_valid(det_elev, valid), valid, quad))
    _put(26, within_quadrant_rank(np.maximum(_clean_valid(depth_to_base, valid), 0.0), valid, quad))
    del depth_to_base

    bh_c0 = max(float(np.percentile(flex["base_hess_ridge"][valid], 85)) if valid.any() else 0.02, 1e-4)
    l_pf_accum = (l_pf_accum + 0.30 * _sat(flex["base_hess_ridge"], bh_c0)).astype(np.float32)
    dby, dbx, az_base, coh_base = flex["dby"], flex["dbx"], flex["az_base"], flex["coh_base"]
    del flex
    gc.collect()

    # --- Regional strikes & Group D polarity ---
    grav_anom = _read_f32_band(stack_path, 13)
    coh_topo, az_topo = coherence_and_strike_deg(det_elev, valid)
    coh_grav, az_grav = coherence_and_strike_deg(grav_anom, valid)
    _, sub_strike = cross_physics_axial_order(
        [az_rtp, az_grav, az_base],
        [coh_rtp, coh_grav, coh_base],
        valid,
    )
    r_axial, comp_strike = cross_physics_axial_order(
        [az_topo, az_rtp, az_grav, az_base],
        [coh_topo, coh_rtp, np.float32(0.8) * coh_grav, np.float32(0.8) * coh_base],
        valid,
    )
    del az_topo, az_rtp, coh_rtp, az_grav, coh_grav, az_base, coh_base
    _put(21, r_axial)

    zy, zx = _grad_xy(det_elev, valid, sigma=2.0)
    znorm = np.hypot(zy, zx)
    gy, gx = _grad_xy(grav_anom, valid, sigma=2.0)
    del grav_anom
    gnorm = np.hypot(gy, gx)
    _put(15, np.where(valid, np.clip((zy * gy + zx * gx) / (znorm * gnorm + np.float32(1e-4)), -1.0, 1.0), 0.0))
    del gy, gx, gnorm
    bnorm = np.hypot(dby, dbx)
    _put(16, np.where(valid, np.clip(-(zy * dby + zx * dbx) / (znorm * bnorm + np.float32(1e-4)), -1.0, 1.0), 0.0))
    del zy, dby, dbx, bnorm, znorm

    grav_hg = _read_f32_band(stack_path, 18)
    b18_clean = _clean_valid(grav_hg, valid)
    del grav_hg
    _put(17, np.where(valid, np.tanh(zx / np.float32(8.0)) * np.tanh(b18_clean / np.float32(1.5)), 0.0))
    del zx, b18_clean
    gc.collect()

    # --- Group C & D: Knickpoints + multi-scale topographic scarp ridges ---
    knick = knickpoint_saddle_and_integral(det_elev, sub_strike, valid, hess_sigma_px=1.5, along_sigma_px=6.0)
    del sub_strike
    mu_step = cross_strike_monotonicity(det_elev, valid, half_span_px=3, normal_sigma=3.0, elev_floor_m=0.5)
    del det_elev

    det_elev_slope = _read_f32_band(stack_path, 19)
    log_slope = np.log(np.maximum(_clean_valid(det_elev_slope, valid), 0.0) + np.float32(1.0)).astype(np.float32)
    del det_elev_slope
    lsy, lsx = _grad_xy(log_slope, valid, sigma=1.0)
    rel_break = np.where(valid, np.hypot(lsy, lsx), 0.0).astype(np.float32)
    del lsy, lsx
    hess_s12 = hessian_ridge_strength(log_slope, valid, sigma=1.2)
    hess_s30 = hessian_ridge_strength(log_slope, valid, sigma=3.0)
    del log_slope

    k_c0 = max(float(np.percentile(knick["knickpoint_saddle"][valid], 85)) if valid.any() else 1.0, 1e-3)
    _put(8, knick["knickpoint_saddle"])
    _put(9, knick["knick_strike_integral"])
    _put(10, np.where(valid, _sat(knick["knickpoint_saddle"], k_c0) * rel_break, 0.0))
    _put(11, rel_break)
    _put(12, hess_s12)
    _put(13, hess_s30)
    _put(14, mu_step)
    del hess_s30

    ki_c0 = max(float(np.percentile(knick["knick_strike_integral"][valid], 85)) if valid.any() else 0.5, 1e-3)
    l_scarp_knick = np.where(
        valid,
        0.45 * _sat(hess_s12, 0.06)
        + 0.30 * _sat(rel_break * (0.35 + 0.65 * mu_step) * coh_topo, 0.04)
        + 0.25 * _sat(knick["knick_strike_integral"], ki_c0),
        0.0,
    ).astype(np.float32)
    del hess_s12, rel_break, mu_step, coh_topo, knick
    gc.collect()

    # --- Group E: Province-aligned Mohr-Coulomb criticality ---
    th_diff = np.deg2rad(comp_strike - np.float32(15.0))
    del comp_strike
    ext_geom = (np.cos(th_diff) ** 2).astype(np.float32)
    shear_geom = (np.sin(np.float32(2.0) * th_diff) ** 2).astype(np.float32)
    del th_diff

    geod_dil = _read_f32_band(stack_path, 8)
    dil_q = within_quadrant_rank(_clean_valid(geod_dil, valid), valid, quad)
    del geod_dil
    _put(22, np.where(valid, r_axial * ext_geom * (np.float32(0.35) + np.float32(0.65) * dil_q), 0.0))
    del ext_geom, dil_q

    geod_shr = _read_f32_band(stack_path, 7)
    shr_q = within_quadrant_rank(_clean_valid(geod_shr, valid), valid, quad)
    del geod_shr
    _put(23, np.where(valid, r_axial * shear_geom * (np.float32(0.35) + np.float32(0.65) * shr_q), 0.0))
    del shear_geom, shr_q, r_axial

    geod_s2i = _read_f32_band(stack_path, 4)
    _put(24, within_quadrant_rank(_clean_valid(geod_s2i, valid), valid, quad))
    del geod_s2i
    gc.collect()

    # --- Group F: MT clay-cap gradient, GeoDAWN lateral gradients & blind GDR ---
    cond_surf = _read_f32_band(stack_path, 17)
    cond_clean = np.maximum(_clean_valid(cond_surf, valid), np.float32(0.1))
    del cond_surf
    cy, cx = _grad_xy(np.log(cond_clean).astype(np.float32), valid, sigma=2.0)
    del cond_clean
    mt_grad = np.where(valid, np.hypot(cy, cx), 0.0).astype(np.float32)
    del cy, cx
    _put(27, mt_grad)
    l_poisson_flex = np.where(valid, l_pf_accum + 0.10 * _sat(mt_grad, 0.012) * grav_tilt, 0.0).astype(np.float32)
    del l_pf_accum, mt_grad, grav_tilt
    gc.collect()

    with rasterio.open(rad_path) as rds:
        rad_k = rds.read(1)
        rad_th = rds.read(2)
        rad_u = rds.read(3)
    valid_rad = valid & np.isfinite(rad_k) & np.isfinite(rad_th) & np.isfinite(rad_u) & (rad_th > 0)
    k_th = np.where(valid_rad, rad_k.astype(np.float32) / (rad_th.astype(np.float32) + np.float32(1.0)), 0.0).astype(np.float32)
    u_th = np.where(valid_rad, rad_u.astype(np.float32) / (rad_th.astype(np.float32) + np.float32(1.0)), 0.0).astype(np.float32)
    del rad_k, rad_th, rad_u
    ky, kx = _grad_xy(k_th, valid_rad, sigma=2.0)
    uy, ux = _grad_xy(u_th, valid_rad, sigma=2.0)
    del k_th, u_th, valid_rad
    _put(28, np.where(valid, np.hypot(ky, kx) + np.hypot(uy, ux), 0.0))
    del ky, kx, uy, ux

    gdr_info = gdr_blind_thermal_features(gdr_csv_path, foot.shape, valid, sigma_px=14.0)
    _put(29, np.where(valid, gdr_info["plume_feat"], 0.0))
    if hasattr(X, "flush"):
        X.flush()

    return {
        "X_foot": X,
        "valid": valid,
        "L_scarp_knick": l_scarp_knick,
        "L_poisson_flex": l_poisson_flex,
        "gdr_meta": {
            "n_thermal_pixels": int(gdr_info["n_thermal_pixels"]),
            "n_blind_geotherm_pixels": int(gdr_info["n_blind_geotherm_pixels"]),
        },
    }


def fit_predict_loqo_poissonflex(
    X_foot: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    label_mask: np.ndarray,
    *,
    feature_cols: tuple[int, ...] | None = None,
    excluded_mask: np.ndarray | None = None,
    equalize_quadrants: bool = True,
    guard_px: int = 12,
    neg_buffer_px: float = 5.0,
    neg_pos_ratio: int = 4,
    seed: int = 20261025,
    max_iter: int = 200,
) -> dict[str, np.ndarray]:
    """Strictly spatially blocked 4-quadrant LOQO classifier with optional Bolstad calibration.

    Returns both ``proba_raw`` and ``proba_eq`` in ``[0, 1]`` from ONE fit pass so the
    ``poissonflex_raw`` ablation costs zero redundant tree fits.
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
    foot_row_map = np.full(foot.shape, -1, dtype=np.int32)
    foot_row_map[foot] = np.arange(int(foot.sum()), dtype=np.int32)

    proba_raw = np.zeros(foot.shape, dtype=np.float32)
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
            raise ValueError(f"Quadrant {q} LOQO training split has empty class: pos={pos_idx.size}, neg={neg_idx.size}")

        rng = np.random.default_rng(int(seed) + 97 * q)
        n_neg = min(int(neg_idx.size), max(int(pos_idx.size) * int(neg_pos_ratio), 1))
        if n_neg < neg_idx.size:
            neg_sel = np.sort(rng.choice(neg_idx, size=n_neg, replace=False))
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
            preds[start:stop] = clf.predict_proba(X_foot[te_idx[start:stop]][:, cols])[:, 1].astype(np.float32)
        proba_raw[target_q] = preds

    proba_eq = bolstad_equalize_quadrants(proba_raw, valid_b, quad) if equalize_quadrants else proba_raw.copy()
    return {"proba_raw": proba_raw, "proba_eq": proba_eq}


def build_poissonflex_crest_surface(
    proba_2d: np.ndarray,
    l_scarp_knick: np.ndarray,
    l_poisson_flex: np.ndarray,
    valid: np.ndarray,
    *,
    sub_weight: float = 0.90,
) -> dict[str, np.ndarray]:
    """Localize LOQO probability onto 1D scarp/knickpoint and Poisson/flexure crests."""
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0), 0.0)
    e_line = np.maximum(
        np.asarray(l_scarp_knick, dtype=np.float32),
        np.float32(sub_weight) * np.asarray(l_poisson_flex, dtype=np.float32),
    )
    s_crest = np.where(valid_b, p * (np.float32(0.15) + np.float32(0.85) * e_line), 0.0).astype(np.float32)
    ridge_1d = directional_ridge_1d(s_crest, valid_b)
    return {
        "S_crest": s_crest,
        "E_line": np.where(valid_b, e_line, 0.0).astype(np.float32),
        "ridge_1d": ridge_1d,
    }


def select_nested_oof_budget(
    s_crest: np.ndarray,
    allowed_pool: np.ndarray,
    inner_folds: list[dict],
    footprint: np.ndarray,
    *,
    budget_grid: tuple[int, ...] = (28_000, 32_000, 35_000, 37_654, 41_000, 45_000),
    min_dist_px: float = 2.8,
) -> dict[str, object]:
    """Select global dot budget ``S`` on strictly visible-only inner holdout folds.

    Ranks candidates ONCE via greedy spacing up to ``max(budget_grid)`` so every
    candidate budget is an exact prefix of the spaced ranking and runs in seconds.
    """
    from gems57 import evaluate_holdout, metric as gems57_metric

    max_b = max(int(b) for b in budget_grid)
    # Extract ordered spaced indices once
    scores = np.where(allowed_pool, np.asarray(s_crest, dtype=np.float32), -np.inf)
    flat_cand = np.flatnonzero(allowed_pool & np.isfinite(scores))
    order = np.argsort(-scores.ravel()[flat_cand], kind="mergesort")[: min(flat_cand.size, 950_000)]
    sorted_idx = flat_cand[order]
    h, w = footprint.shape
    ys, xs = np.unravel_index(sorted_idx, (h, w))

    r_ceil = int(np.ceil(min_dist_px))
    r2 = float(min_dist_px) * float(min_dist_px)
    offsets = [
        (dy, dx)
        for dy in range(-r_ceil, r_ceil + 1)
        for dx in range(-r_ceil, r_ceil + 1)
        if dy * dy + dx * dx < r2
    ]
    blocked = np.zeros((h, w), dtype=bool)
    picked_y, picked_x = [], []
    for y, x in zip(ys.tolist(), xs.tolist()):
        if blocked[y, x]:
            continue
        picked_y.append(y)
        picked_x.append(x)
        if len(picked_y) >= max_b:
            break
        for dy, dx in offsets:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w:
                blocked[ny, nx] = True

    grid_scores: dict[int, float] = {}
    for b in budget_grid:
        b_int = int(b)
        m = np.zeros((h, w), dtype=np.float32)
        k = min(b_int, len(picked_y))
        m[picked_y[:k], picked_x[:k]] = 1.0
        tp_sum = fp_sum = fn_sum = 0.0
        for fold in inner_folds:
            sc, _ = evaluate_holdout.evaluate(m, fold, footprint)
            tp_sum += float(sc["tp"])
            fp_sum += float(sc["fp"])
            fn_sum += float(sc["fn"])
        grid_scores[b_int] = round(gems57_metric.dti_from_components(tp_sum, fp_sum, fn_sum), 6)

    best_b = max(grid_scores, key=lambda b: grid_scores[b])
    return {"best_budget": int(best_b), "grid_dti": grid_scores, "max_available": len(picked_y)}
