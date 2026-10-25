"""PROVINCETOE lane: Tectonic-Province Strain-Invariant Wallace Basal Toe-Concavity
& Carbonate-Horst Isostatic Flexure LOQO.

Pre-registered hypothesis, equations, and frozen 3-arm protocol:
``docs/HYPOTHESES_20261025_PROVINCETOE.md``.

Physical & statistical invariants
---------------------------------
1. **Catalogue-Blind Feature Stack**:
   All 24 primary features (+ 2 raw-strain ablation columns for Arm 2 ``globalraw``)
   are derived strictly from the 19-band geophysical/topographic stack, USGS GeoDAWN
   gamma-ray spectrometry (``K, Th, U``), and DOE GDR #1391 thermal/chemical
   geothermometry (with ``dist_known_fault_px`` dropped immediately on load).
2. **Strict Zero Cross-Quadrant Coupling**:
   Within-province background normalizations (``within_quadrant_relative_contrast``)
   execute strictly inside ``valid & (quad == q)`` with zero-padded domain masks so
   no pixel from ``quad != q`` can ever influence feature values in quadrant ``q``.
   Cross-strike stencil shifts are bounded to ``<= 4 px`` (``400 m << 1.2 km`` guard).
3. **Wallace Scarp-Diffusion Basal Toe-Concavity & V-Canyon Suppression**:
   Replaces ``COULOMBLOQO``'s convex ``log_slope`` Hessian ridge (which placed
   ``45.2%`` of dots on ``>= 12 deg`` alpine cliffs) with principal positive elevation
   Hessian concavity ``+lambda_max(nabla^2 z)`` gated by cross-eigenvector elevation
   step monotonicity ``M_step`` and one-sided upslope-vs-downslope apron asymmetry
   ``A_toe``, plus the Wallace scarp-diffusion crest-toe dipole ``D_wallace``.
4. **Label-Blind Per-Quadrant Empirical Quantile Calibration**:
   Maps each out-of-quadrant LOQO classifier's predictions onto empirical ranks over
   the *unlabeled* footprint of ``quad == q`` (touching zero test labels), preventing
   Walker Lane GPS strain amplitude from starving the low-strain Northeastern Great
   Basin Carbonate Province (``#IR-92-NE-QUADRANT-LOQO-COLLAPSE``).
"""
from __future__ import annotations

import gc
from pathlib import Path
import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt, gaussian_filter, map_coordinates
from scipy.stats import rankdata
from sklearn.ensemble import HistGradientBoostingClassifier

from .apronridge import directional_ridge_1d
from .breakline import spaced_top_mask
from .coulomb_loqo import (
    OPTIMAL_NORMAL_STRIKE_DEG,
    cross_physics_axial_order,
    gdr_blind_thermal_features,
    hessian_ridge_strength,
)
from .hydroconduit import _clean_valid, coherence_and_strike_deg

PRIMARY_FEATURE_NAMES: tuple[str, ...] = (
    # Group A: Wallace basal toe-concavity, step monotonicity & scarp-diffusion dipole (0..7)
    "f00_toe_concav_s15",
    "f01_toe_concav_s35",
    "f02_apron_asymmetry",
    "f03_wallace_dipole",
    "f04_step_monotonicity",
    "f05_rel_log_slope_step",
    "f06_along_strike_prog",
    "f07_log_slope_mod",
    # Group B: Carbonate-horst isostatic gravity & basement flexure (8..13)
    "f08_rel_grav_slope",
    "f09_grav_hess_ridge",
    "f10_rel_base_grad",
    "f11_dip_concord_grav",
    "f12_dip_concord_base",
    "f13_ew_horst_lock",
    # Group C: Within-province RTP contact & 4-field axial lock (14..17)
    "f14_rel_rtp_grad",
    "f15_rtp_tilt_coh",
    "f16_rtp_hess_ridge",
    "f17_cross_physics_axial4",
    # Group D: Dimensionless tectonic strain-style partitioning (18..20)
    "f18_kinematic_dil_ratio",
    "f19_strike_normal_opt",
    "f20_strike_transtens_opt",
    # Group E: Within-province MT clay-cap edge, GeoDAWN K/Th & blind GDR plume (21..23)
    "f21_rel_mt_grad",
    "f22_rad_k_th_anom",
    "f23_rel_gdr_plume",
)

ABLATION_RAW_NAMES: tuple[str, ...] = (
    "f24_raw_geod_shearrate",
    "f25_raw_geod_2ndinv",
)

ALL_FEATURE_NAMES: tuple[str, ...] = PRIMARY_FEATURE_NAMES + ABLATION_RAW_NAMES

PRIMARY_COLS: tuple[int, ...] = tuple(range(24))
# Arm 2 (globalraw): replaces dimensionless kinematic dil ratio (18) with raw shear/2ndinv (24, 25)
GLOBALRAW_COLS: tuple[int, ...] = tuple(i for i in range(24) if i != 18) + (24, 25)

__all__ = [
    "PRIMARY_FEATURE_NAMES",
    "ABLATION_RAW_NAMES",
    "ALL_FEATURE_NAMES",
    "PRIMARY_COLS",
    "GLOBALRAW_COLS",
    "hessian_concavity_and_axis",
    "wallace_toe_operators",
    "within_quadrant_relative_contrast",
    "within_quadrant_demean",
    "calibrate_quadrant_ranks",
    "compute_provincetoe_stack",
    "fit_predict_provincetoe_loqo",
    "build_provincetoe_surface",
    "directional_ridge_1d",
    "spaced_top_mask",
]


def _sat(x: np.ndarray, c0: float) -> np.ndarray:
    xp = np.maximum(np.asarray(x, dtype=np.float32), 0.0)
    return (xp / (xp + np.float32(c0))).astype(np.float32)


def _grad_xy(field: np.ndarray, valid: np.ndarray, sigma: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    u = _clean_valid(field, valid)
    if sigma > 0.0:
        u = gaussian_filter(u, float(sigma)).astype(np.float32)
    gy, gx = np.gradient(u)
    return gy.astype(np.float32), gx.astype(np.float32)


def hessian_concavity_and_axis(
    field: np.ndarray,
    valid: np.ndarray,
    sigma: float = 1.5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return ``(concavity, crest_convexity, ey_max, ex_max)`` at scale ``sigma``.

    * ``concavity = max(0, +lambda_max) * sigma^2`` peaks along upward-concave basal
      piedmont fault toes where steep footwall slopes meet gentle hangingwall aprons.
    * ``crest_convexity = max(0, -lambda_min) * sigma^2`` peaks along convex-upward
      scarp crests upslope of the fault inflection line.
    * ``(ey_max, ex_max)`` is the unit eigenvector corresponding to ``lambda_max``
      (oriented perpendicular to the basal breakline).
    """
    if sigma <= 0.0:
        raise ValueError("sigma must be positive")
    valid_b = np.asarray(valid, dtype=bool)
    u = gaussian_filter(_clean_valid(field, valid_b), float(sigma)).astype(np.float32)
    uy, ux = np.gradient(u)
    uyy, uxy = np.gradient(uy)
    uxy2, uxx = np.gradient(ux)
    hxy = (0.5 * (uxy + uxy2)).astype(np.float32)
    del u, uy, ux, uxy, uxy2

    tr = (uxx + uyy).astype(np.float32)
    diff = (uyy - uxx).astype(np.float32)
    rad = np.sqrt(diff * diff + 4.0 * hxy * hxy).astype(np.float32)
    lam_max = (0.5 * (tr + rad)).astype(np.float32)
    lam_min = (0.5 * (tr - rad)).astype(np.float32)

    # Principal eigenvector of [uyy, hxy; hxy, uxx] for lambda_max:
    # angle phi in y-x plane satisfies tan(2*phi) = 2*hxy / (uyy - uxx)
    phi = 0.5 * np.arctan2(2.0 * hxy, diff)
    ey = np.cos(phi).astype(np.float32)
    ex = np.sin(phi).astype(np.float32)
    del uxx, uyy, hxy, tr, diff, rad, phi

    s2 = np.float32(sigma * sigma)
    concav = np.where(valid_b, np.maximum(lam_max, 0.0) * s2, 0.0).astype(np.float32)
    convex = np.where(valid_b, np.maximum(-lam_min, 0.0) * s2, 0.0).astype(np.float32)
    ey = np.where(valid_b, ey, 0.0).astype(np.float32)
    ex = np.where(valid_b, ex, 0.0).astype(np.float32)
    return concav, convex, ey, ex


def _sample_offset(arr: np.ndarray, dy: np.ndarray, dx: np.ndarray) -> np.ndarray:
    """Bilinear sample ``arr[r + dy, c + dx]`` clamped at image borders."""
    h, w = arr.shape
    rr = np.clip(np.arange(h, dtype=np.float32)[:, None] + dy, 0.0, float(h - 1))
    cc = np.clip(np.arange(w, dtype=np.float32)[None, :] + dx, 0.0, float(w - 1))
    return map_coordinates(arr, [rr, cc], order=1, mode="nearest").astype(np.float32)


def wallace_toe_operators(
    det_elev: np.ndarray,
    det_elev_slope: np.ndarray,
    valid: np.ndarray,
    span_px: float = 4.0,
    dipole_px: float = 3.0,
) -> dict[str, np.ndarray]:
    """Compute Wallace scarp-diffusion basal toe-concavity, step monotonicity,
    one-sided apron asymmetry, and crest-to-toe diffusion dipole.

    Mathematically suppresses both symmetric V-shaped erosional canyons
    (``z_+ approx z_-`` -> ``M_step -> 0`` and ``s_+ approx s_-`` -> ``A_toe -> 0``)
    and symmetric alpine summit divides while peaking along normal-fault basal
    piedmont toes and degraded intrabasin fault scarps.
    """
    valid_b = np.asarray(valid, dtype=bool)
    z0 = gaussian_filter(_clean_valid(det_elev, valid_b), 1.2).astype(np.float32)
    s0 = gaussian_filter(np.maximum(_clean_valid(det_elev_slope, valid_b), 0.0), 1.2).astype(np.float32)

    concav_15, _, _, _ = hessian_concavity_and_axis(det_elev, valid_b, sigma=1.5)
    concav_20, convex_20, ey, ex = hessian_concavity_and_axis(det_elev, valid_b, sigma=2.0)
    concav_35, _, _, _ = hessian_concavity_and_axis(det_elev, valid_b, sigma=3.5)
    del concav_20

    dy_s = (np.float32(span_px) * ey).astype(np.float32)
    dx_s = (np.float32(span_px) * ex).astype(np.float32)
    z_pos = _sample_offset(z0, dy_s, dx_s)
    z_neg = _sample_offset(z0, -dy_s, -dx_s)
    s_pos = np.maximum(_sample_offset(s0, dy_s, dx_s), 0.0)
    s_neg = np.maximum(_sample_offset(s0, -dy_s, -dx_s), 0.0)
    del dy_s, dx_s, s0

    # Cross-breakline elevation step monotonicity: ~1 on monotonic fault steps/scarps,
    # ~0 in V-shaped stream thalwegs and on symmetric mountain ridge crests.
    dz_net = np.abs(z_pos - z_neg)
    dz_tot = np.abs(z_pos - z0) + np.abs(z_neg - z0) + np.float32(1.5)
    m_step = np.where(valid_b, np.clip(dz_net / dz_tot, 0.0, 1.0), 0.0).astype(np.float32)

    # Orient unit normal (+ny_up, +nx_up) strictly toward the uplifted footwall side
    flip = np.where(z_pos >= z_neg, np.float32(1.0), np.float32(-1.0))
    ny_up = (ey * flip).astype(np.float32)
    nx_up = (ex * flip).astype(np.float32)
    s_up = np.where(z_pos >= z_neg, s_pos, s_neg)
    s_dn = np.where(z_pos >= z_neg, s_neg, s_pos)
    del z0, z_pos, z_neg, s_pos, s_neg, dz_net, dz_tot, flip, ey, ex

    # Signed footwall-steep vs hangingwall-gentle basal apron asymmetry in [0, 1)
    apron_asym = np.where(
        valid_b,
        (np.maximum(s_up - s_dn, 0.0) / (s_up + s_dn + np.float32(1.0))) * m_step,
        0.0,
    ).astype(np.float32)
    del s_up, s_dn

    # Wallace scarp-diffusion dipole: upslope footwall convexity (+d*n_up) paired with
    # downslope hangingwall toe concavity (-d*n_up) across +-dipole_px
    dy_d = (np.float32(dipole_px) * ny_up).astype(np.float32)
    dx_d = (np.float32(dipole_px) * nx_up).astype(np.float32)
    up_convex = np.maximum(_sample_offset(convex_20, dy_d, dx_d), 0.0)
    dn_concav = np.maximum(_sample_offset(concav_15 + convex_20 * np.float32(0.0), -dy_d, -dx_d), 0.0)
    del convex_20, dy_d, dx_d
    wallace_dip = np.where(
        valid_b,
        np.sqrt(up_convex * dn_concav) * m_step,
        0.0,
    ).astype(np.float32)
    del up_convex, dn_concav

    # Along-strike elevation progression (tangent t = (-nx_up, ny_up)):
    # suppresses horizontal pluvial Lake Lahontan/Bonneville shorelines & passive bajada contours
    zy3, zx3 = _grad_xy(det_elev, valid_b, sigma=3.0)
    gnorm3 = np.hypot(zy3, zx3)
    along_prog = np.where(
        valid_b,
        np.abs(-nx_up * zy3 + ny_up * zx3) / (gnorm3 + np.float32(2.0)),
        0.0,
    ).astype(np.float32)
    del zy3, zx3, gnorm3

    return {
        "toe_concav_s15": concav_15,
        "toe_concav_s35": concav_35,
        "apron_asymmetry": apron_asym,
        "wallace_dipole": wallace_dip,
        "step_monotonicity": m_step,
        "along_strike_prog": along_prog,
        "ny_up": ny_up,
        "nx_up": nx_up,
    }


def within_quadrant_relative_contrast(
    pos_field: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    *,
    sigma_bg: float = 6.0,
    c0: float = 1e-3,
) -> np.ndarray:
    """Normalize a non-negative physical gradient strictly within each ``quad == q``.

    Zero-pads outside ``valid & (quad == q)`` and divides by the smoothed mask
    weight inside ``quad == q``, guaranteeing **exact zero cross-quadrant coupling**
    while equalizing low-amplitude carbonate/basin provinces (``NE``) with volcanic
    Walker Lane provinces (``SW``).
    """
    valid_b = np.asarray(valid, dtype=bool)
    f = np.where(valid_b, np.maximum(_clean_valid(pos_field, valid_b), 0.0), 0.0).astype(np.float32)
    out = np.zeros_like(f, dtype=np.float32)
    c0_f = np.float32(c0)
    for q in (0, 1, 2, 3):
        dom = valid_b & (quad == q)
        if not np.any(dom):
            continue
        w = gaussian_filter(dom.astype(np.float32), float(sigma_bg)).astype(np.float32)
        num = gaussian_filter(np.where(dom, f, 0.0).astype(np.float32), float(sigma_bg)).astype(np.float32)
        bg = num / np.maximum(w, np.float32(1e-4))
        out[dom] = f[dom] / (bg[dom] + c0_f)
    return out


def within_quadrant_demean(
    field: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    *,
    sigma_bg: float = 8.0,
) -> np.ndarray:
    """High-pass residual strictly inside each ``valid & (quad == q)`` domain."""
    valid_b = np.asarray(valid, dtype=bool)
    f = np.where(valid_b, _clean_valid(field, valid_b), 0.0).astype(np.float32)
    out = np.zeros_like(f, dtype=np.float32)
    for q in (0, 1, 2, 3):
        dom = valid_b & (quad == q)
        if not np.any(dom):
            continue
        w = gaussian_filter(dom.astype(np.float32), float(sigma_bg)).astype(np.float32)
        num = gaussian_filter(np.where(dom, f, 0.0).astype(np.float32), float(sigma_bg)).astype(np.float32)
        bg = num / np.maximum(w, np.float32(1e-4))
        out[dom] = f[dom] - bg[dom]
    return out


def calibrate_quadrant_ranks(
    proba_2d: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    *,
    gamma: float = 2.0,
) -> np.ndarray:
    """Strictly label-blind per-quadrant empirical quantile calibration.

    Maps each quadrant's out-of-fold probability distribution ``proba_2d[dom_q]``
    to ``(rank / N_q) ** gamma`` using ONLY the unlabeled footprint pixels of
    quadrant ``q``. Preserves exact within-quadrant monotonicity while preventing
    uncalibrated regional logit shifts from starving low-strain quadrants (``NE``).
    """
    if gamma <= 0.0:
        raise ValueError("gamma must be positive")
    valid_b = np.asarray(valid, dtype=bool)
    p = np.nan_to_num(np.asarray(proba_2d, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0)
    out = np.zeros_like(p, dtype=np.float32)
    for q in (0, 1, 2, 3):
        dom = valid_b & (quad == q)
        n_q = int(dom.sum())
        if n_q == 0:
            continue
        ranks = rankdata(p[dom], method="average").astype(np.float64) / float(n_q)
        out[dom] = (ranks ** float(gamma)).astype(np.float32)
    return out


def compute_provincetoe_stack(
    *,
    rtp: np.ndarray,
    geod_2ndinv: np.ndarray,
    grav_slope: np.ndarray,
    geod_shearrate: np.ndarray,
    geod_dilaterate: np.ndarray,
    det_elev: np.ndarray,
    grav_anom: np.ndarray,
    depth_to_base: np.ndarray,
    cond_surf: np.ndarray,
    grav_hg: np.ndarray,
    det_elev_slope: np.ndarray,
    rad_k: np.ndarray,
    rad_th: np.ndarray,
    gdr_plume_feat: np.ndarray,
    footprint: np.ndarray,
    quad: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute ``(N_foot, 26)`` float32 feature stack + 1D basal-toe & subsurface channels."""
    foot = np.asarray(footprint, dtype=bool)
    valid = (
        foot
        & np.isfinite(det_elev) & (det_elev > -1e30)
        & np.isfinite(det_elev_slope) & (det_elev_slope > -1e30)
        & np.isfinite(rtp) & (rtp > -1e30)
    )
    foot_idx = np.flatnonzero(foot)
    n_foot = int(foot_idx.size)
    X = np.zeros((n_foot, len(ALL_FEATURE_NAMES)), dtype=np.float32)

    def _put(col: int, arr2d: np.ndarray) -> None:
        flat = np.asarray(arr2d, dtype=np.float32).ravel()[foot_idx]
        X[:, col] = np.nan_to_num(flat, nan=0.0, posinf=0.0, neginf=0.0)

    # --- Group A: Wallace scarp-diffusion basal toe-concavity & step monotonicity ---
    w_ops = wallace_toe_operators(det_elev, det_elev_slope, valid, span_px=4.0, dipole_px=3.0)
    ny_up = w_ops.pop("ny_up")
    nx_up = w_ops.pop("nx_up")
    m_step = w_ops["step_monotonicity"]
    concav_15 = w_ops["toe_concav_s15"]
    apron_asym = w_ops["apron_asymmetry"]
    wallace_dip = w_ops["wallace_dipole"]

    slp_clean = np.maximum(_clean_valid(det_elev_slope, valid), 0.0).astype(np.float32)
    log_slope = np.log1p(slp_clean).astype(np.float32)
    lsy, lsx = _grad_xy(log_slope, valid, sigma=1.0)
    rel_break_step = np.where(valid, np.hypot(lsy, lsx) * (np.float32(0.25) + np.float32(0.75) * m_step), 0.0).astype(np.float32)
    del lsy, lsx

    _put(0, concav_15)
    _put(1, w_ops["toe_concav_s35"])
    _put(2, apron_asym)
    _put(3, wallace_dip)
    _put(4, m_step)
    _put(5, rel_break_step)
    _put(6, w_ops["along_strike_prog"])
    _put(7, np.where(valid, log_slope, 0.0).astype(np.float32))
    del w_ops, log_slope

    # Raw 1D basal-toe localization (before slope cliff taper, so Arms 1/3 can vary s0 cleanly)
    b_wallace = (concav_15 * (np.float32(0.25) + np.float32(0.75) * apron_asym)).astype(np.float32)
    l_toe_raw = np.where(
        valid,
        0.45 * _sat(b_wallace, 0.90)
        + 0.30 * _sat(wallace_dip, 0.65)
        + 0.25 * _sat(rel_break_step, 0.045),
        0.0,
    ).astype(np.float32)
    del concav_15, apron_asym, wallace_dip, rel_break_step, b_wallace, m_step
    gc.collect()

    # --- Group B: Carbonate-horst isostatic gravity & basement flexure ---
    gs_pos = np.maximum(_clean_valid(grav_slope, valid), 0.0).astype(np.float32)
    rel_grav = within_quadrant_relative_contrast(gs_pos, valid, quad, sigma_bg=6.0, c0=0.025)
    grav_hess = hessian_ridge_strength(np.log1p(np.float32(10.0) * gs_pos), valid, sigma=2.0)
    del gs_pos

    db_pos = np.maximum(_clean_valid(depth_to_base, valid), 0.0).astype(np.float32)
    log_db10 = np.log(db_pos + np.float32(10.0)).astype(np.float32)
    del db_pos
    dby, dbx = _grad_xy(log_db10, valid, sigma=2.0)
    base_grad = np.where(valid, np.hypot(dby, dbx), 0.0).astype(np.float32)
    rel_base = within_quadrant_relative_contrast(base_grad, valid, quad, sigma_bg=6.0, c0=0.012)
    coh_base, az_base = coherence_and_strike_deg(log_db10, valid)
    del log_db10, base_grad

    gy, gx = _grad_xy(grav_anom, valid, sigma=2.0)
    gnorm = np.hypot(gy, gx)
    dip_grav = np.where(
        valid,
        np.clip((ny_up * gy + nx_up * gx) / (gnorm + np.float32(1e-4)), -1.0, 1.0),
        0.0,
    ).astype(np.float32)
    del gy, gx, gnorm

    bnorm = np.hypot(dby, dbx)
    dip_base = np.where(
        valid,
        np.clip(-(ny_up * dby + nx_up * dbx) / (bnorm + np.float32(1e-4)), -1.0, 1.0),
        0.0,
    ).astype(np.float32)
    del dby, dbx, bnorm, ny_up

    b18_clean = _clean_valid(grav_hg, valid)
    ew_lock = np.where(
        valid,
        nx_up * np.tanh(b18_clean / np.float32(1.5)),
        0.0,
    ).astype(np.float32)
    del nx_up, b18_clean

    _put(8, rel_grav)
    _put(9, grav_hess)
    _put(10, rel_base)
    _put(11, dip_grav)
    _put(12, dip_base)
    _put(13, ew_lock)
    del rel_grav, dip_grav, dip_base, ew_lock
    gc.collect()

    # --- Group C: Within-province RTP contact & 4-field cross-physics axial lock ---
    u_rtp = gaussian_filter(_clean_valid(rtp, valid), 1.0).astype(np.float32)
    ry, rx = np.gradient(u_rtp)
    r_gh = np.hypot(ry, rx).astype(np.float32)
    ryy, _ = np.gradient(ry)
    _, rxx = np.gradient(rx)
    r_lap = (rxx + ryy).astype(np.float32)
    del u_rtp, ry, rx, ryy, rxx

    rel_rtp = within_quadrant_relative_contrast(r_gh, valid, quad, sigma_bg=6.0, c0=3.0)
    coh_rtp, az_rtp = coherence_and_strike_deg(rtp, valid)
    coh_topo, az_topo = coherence_and_strike_deg(det_elev, valid)
    coh_grav, az_grav = coherence_and_strike_deg(grav_anom, valid)

    rtp_tilt = np.where(
        valid,
        (r_gh / np.sqrt(r_gh * r_gh + r_lap * r_lap + np.float32(1.5 ** 2))) * coh_rtp,
        0.0,
    ).astype(np.float32)
    rtp_hess = hessian_ridge_strength(np.log1p(r_gh), valid, sigma=2.0)
    del r_gh, r_lap

    r_axial4, comp_strike = cross_physics_axial_order(
        [az_topo, az_grav, az_base, az_rtp],
        [coh_topo, np.float32(0.85) * coh_grav, np.float32(0.75) * coh_base, np.float32(0.80) * coh_rtp],
        valid,
    )
    del coh_topo, az_topo, coh_grav, az_grav, coh_base, az_base, coh_rtp, az_rtp

    _put(14, rel_rtp)
    _put(15, rtp_tilt)
    _put(16, rtp_hess)
    _put(17, r_axial4)
    del rel_rtp, rtp_tilt, r_axial4
    gc.collect()

    # --- Group D: Dimensionless tectonic strain-style partitioning (+ raw ablation cols) ---
    dil_shift = np.maximum(_clean_valid(geod_dilaterate, valid) + np.float32(5.0), 0.0).astype(np.float32)
    shr_pos = np.maximum(_clean_valid(geod_shearrate, valid), 0.0).astype(np.float32)
    s2i_pos = np.maximum(_clean_valid(geod_2ndinv, valid), 0.0).astype(np.float32)

    kin_dil_ratio = np.where(
        valid,
        dil_shift / (dil_shift + shr_pos + np.float32(2.0)),
        0.0,
    ).astype(np.float32)
    dth = np.radians(comp_strike - np.float32(OPTIMAL_NORMAL_STRIKE_DEG))
    strike_norm = np.where(valid, np.cos(dth) ** 2, 0.0).astype(np.float32)
    strike_tran = np.where(valid, np.sin(2.0 * dth) ** 2, 0.0).astype(np.float32)
    del comp_strike, dth, dil_shift

    _put(18, kin_dil_ratio)
    _put(19, strike_norm)
    _put(20, strike_tran)
    _put(24, np.where(valid, shr_pos, 0.0).astype(np.float32))
    _put(25, np.where(valid, s2i_pos, 0.0).astype(np.float32))
    del kin_dil_ratio, strike_norm, strike_tran, shr_pos, s2i_pos

    # --- Group E: Within-province MT clay-cap edge, GeoDAWN K/Th & blind GDR plume ---
    cond_clean = np.maximum(_clean_valid(cond_surf, valid), np.float32(0.1)).astype(np.float32)
    cy, cx = _grad_xy(np.log(cond_clean), valid, sigma=2.0)
    mt_grad = np.where(valid, np.hypot(cy, cx), 0.0).astype(np.float32)
    rel_mt = within_quadrant_relative_contrast(mt_grad, valid, quad, sigma_bg=6.0, c0=0.008)
    del cond_clean, cy, cx, mt_grad

    valid_rad = valid & np.isfinite(rad_k) & np.isfinite(rad_th) & (np.asarray(rad_th) > 0)
    k_th_raw = np.where(
        valid_rad,
        np.asarray(rad_k, dtype=np.float32) / (np.asarray(rad_th, dtype=np.float32) + np.float32(1.0)),
        0.0,
    ).astype(np.float32)
    k_th_smooth = gaussian_filter(_clean_valid(k_th_raw, valid_rad), 2.0).astype(np.float32)
    k_th_anom = within_quadrant_demean(k_th_smooth, valid, quad, sigma_bg=8.0)
    del valid_rad, k_th_raw, k_th_smooth

    rel_gdr = within_quadrant_relative_contrast(gdr_plume_feat, valid, quad, sigma_bg=8.0, c0=0.15)

    _put(21, rel_mt)
    _put(22, k_th_anom)
    _put(23, rel_gdr)
    del k_th_anom, rel_gdr

    # Subsurface 1D localization channel: balanced across carbonate/basin gravity-basement
    # flexure (60%) and magnetic RTP / MT clay-cap edges (40%)
    l_sub = np.where(
        valid,
        0.35 * _sat(grav_hess, 0.018)
        + 0.25 * _sat(rel_base, 1.35)
        + 0.25 * _sat(rtp_hess, 0.045)
        + 0.15 * _sat(rel_mt, 1.35),
        0.0,
    ).astype(np.float32)
    del grav_hess, rel_base, rtp_hess, rel_mt
    gc.collect()

    return {
        "X_foot": X,
        "valid": valid,
        "L_toe_raw": l_toe_raw,
        "L_sub": l_sub,
        "slope_deg": np.where(valid, slp_clean, 0.0).astype(np.float32),
        "gdr_blind": gdr_blind_thermal_features,  # reference for callers
    }


def fit_predict_provincetoe_loqo(
    X_foot: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    label_mask: np.ndarray,
    *,
    feature_cols: tuple[int, ...] = PRIMARY_COLS,
    excluded_mask: np.ndarray | None = None,
    calibrate_quadrants: bool = True,
    rank_gamma: float = 2.0,
    guard_px: int = 12,
    neg_buffer_px: float = 5.0,
    neg_pos_ratio: int = 4,
    seed: int = 20261025,
    max_iter: int = 180,
) -> dict[str, np.ndarray]:
    """Strictly spatially blocked 4-quadrant LOQO fault probability + optional
    label-blind per-quadrant empirical quantile calibration.

    Within each training split ``(quad != q) & ~guard_12px``, positive training
    samples in each of the 3 training quadrants are inverse-prevalence balanced
    so high-density Walker Lane quadrants (``SW``/``SE``) cannot dominate tree
    splits over low-strain quadrants (``NW``/``NE``).
    """
    if guard_px < 0:
        raise ValueError("guard_px must be >= 0")
    if neg_pos_ratio < 1:
        raise ValueError("neg_pos_ratio must be >= 1")
    foot = np.asarray(footprint, dtype=bool)
    valid_b = np.asarray(valid, dtype=bool) & foot
    lbl = np.asarray(label_mask, dtype=bool) & valid_b
    excl = np.asarray(excluded_mask, dtype=bool) if excluded_mask is not None else np.zeros_like(foot)

    cols = list(feature_cols)
    d_lbl = distance_transform_edt(~lbl)

    foot_row_map = np.full(foot.shape, -1, dtype=np.int32)
    foot_row_map[foot] = np.arange(int(foot.sum()), dtype=np.int32)
    quad_foot = quad[foot]

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
            raise ValueError(f"Quadrant {q} LOQO training split has empty class: pos={pos_idx.size}, neg={neg_idx.size}")

        rng = np.random.default_rng(int(seed) + 131 * q)
        # Stratified negative sampling across the 3 training quadrants proportional to footprint
        neg_sel_parts = []
        n_neg_target = min(int(neg_idx.size), max(int(pos_idx.size) * int(neg_pos_ratio), 1))
        other_qs = [oq for oq in present_quads if oq != q]
        neg_q_pools = [foot_row_map[neg_pool & (quad == oq)] for oq in other_qs]
        tot_neg_pool = sum(arr.size for arr in neg_q_pools)
        for k_oq, pool_oq in enumerate(neg_q_pools):
            if pool_oq.size == 0 or tot_neg_pool == 0:
                continue
            take = int(round(n_neg_target * (pool_oq.size / float(tot_neg_pool))))
            take = min(pool_oq.size, max(take, 1))
            if take < pool_oq.size:
                chosen = rng.choice(pool_oq, size=take, replace=False)
                chosen.sort()
                neg_sel_parts.append(chosen)
            else:
                neg_sel_parts.append(pool_oq)
        neg_sel = np.concatenate(neg_sel_parts)

        tr_idx = np.concatenate([pos_idx, neg_sel])
        X_tr = X_foot[tr_idx][:, cols]
        y_tr = np.concatenate([
            np.ones(pos_idx.size, dtype=np.int8),
            np.zeros(neg_sel.size, dtype=np.int8),
        ])

        # Equalize positive class contribution across each training quadrant (only for province-balanced mode)
        sample_w = np.ones(tr_idx.size, dtype=np.float32)
        if calibrate_quadrants:
            pos_q = quad_foot[pos_idx]
            active_oqs = [oq for oq in other_qs if np.any(pos_q == oq)]
            per_q_target_mass = float(neg_sel.size) / float(max(len(active_oqs), 1))
            pos_w = np.ones(pos_idx.size, dtype=np.float32)
            for oq in active_oqs:
                m_oq = pos_q == oq
                pos_w[m_oq] = np.float32(per_q_target_mass / float(m_oq.sum()))
            sample_w[: pos_idx.size] = pos_w
        else:
            sample_w[: pos_idx.size] = np.float32(float(neg_sel.size) / float(max(pos_idx.size, 1)))

        clf = HistGradientBoostingClassifier(
            loss="log_loss",
            learning_rate=0.055,
            max_iter=int(max_iter),
            max_leaf_nodes=31,
            max_depth=5,
            min_samples_leaf=min(200, max(10, int(tr_idx.size // 40))),
            l2_regularization=12.0,
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
        raw_proba[target_q] = preds

    if calibrate_quadrants:
        cal_proba = calibrate_quadrant_ranks(raw_proba, valid_b, quad, gamma=rank_gamma)
    else:
        cal_proba = raw_proba.copy()

    return {
        "raw_proba": raw_proba,
        "cal_proba": cal_proba,
    }


def build_provincetoe_surface(
    proba_2d: np.ndarray,
    l_toe_raw: np.ndarray,
    l_sub: np.ndarray,
    slope_deg: np.ndarray,
    valid: np.ndarray,
    *,
    cliff_slope_deg: float = 15.0,
    sub_weight: float = 0.85,
) -> dict[str, np.ndarray]:
    """Fuse LOQO fault probability with cliff-moderated Wallace basal-toe & subsurface 1D NMS."""
    if cliff_slope_deg <= 0.0:
        raise ValueError("cliff_slope_deg must be positive")
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0), 0.0)
    slp = np.maximum(np.asarray(slope_deg, dtype=np.float32), 0.0)
    w_cliff = (np.float32(1.0) / (np.float32(1.0) + (slp / np.float32(cliff_slope_deg)) ** 2)).astype(np.float32)

    l_toe = (np.asarray(l_toe_raw, dtype=np.float32) * w_cliff).astype(np.float32)
    e_line = np.maximum(l_toe, np.float32(sub_weight) * np.asarray(l_sub, dtype=np.float32))
    s_surface = np.where(valid_b, p * (np.float32(0.15) + np.float32(0.85) * e_line), 0.0).astype(np.float32)
    ridge_1d = directional_ridge_1d(s_surface, valid_b)
    return {
        "S_surface": s_surface,
        "E_line": np.where(valid_b, e_line, 0.0).astype(np.float32),
        "ridge_1d": ridge_1d,
    }
