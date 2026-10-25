"""LISTRICLOQO lane: Updip Listric Hanging-Wall Dip-Offset Projection, Interfluve
Facet-Spur Knickpoint Bridge, Dual-Ratio Radioelement (K/Th + U/Th) Redox-Contact
Concordance, Relay-Ramp Transfer Tensor & Selective Branch Quadrant-Calibrated
4-Quadrant LOQO Model.

Pre-registered BEFORE evaluation in ``docs/HYPOTHESES_20261025_LISTRICLOQO.md``.
Directly executes Priority #1 (`LISTRIC-RADIO-LOQO`) and Priority #2
(`SELECTIVE-QCAL-LOQO`) from ``docs/NEXT_STEPS.md``.

Physical & statistical architecture
-----------------------------------
1. Grauch-Cordell Updip Listric Hanging-Wall Dip-Offset Projection
   (Grauch & Cordell 1987, Geophysics 52(1):118-131; Jachens & Moring 1990):
   For 45-60 deg dipping Basin-and-Range normal faults, the maximum horizontal
   gradient of isostatic gravity (Bands 5, 18), depth-to-basement (Band 15), and
   subsurface potential-field fault ramps lies 300-520 m (3.0-5.2 px) down-dip in
   the hanging wall relative to the surface fault trace or basal piedmont toe.
   We construct the regional updip footwall-directed unit normal vector ``n_updip``
   from ``-grad log(B + 20)``, ``+grad g_iso``, and ``+grad z_det``, and project
   the subsurface carbonate-gravity/basement/Poisson ramp updip across listric
   offsets ``s in {3.6, 4.4, 5.2} px``.
2. Wallace Interfluve Facet-Spur Knickpoint Bridge
   (Wallace 1978, GSA Bull. 89:1261-1278; Bull 2007):
   Bridges incised drainage-canyon knickpoints across adjacent triangular faceted
   interfluve spurs at ``+/- 3.8 px`` and ``+/- 4.8 px`` along fault strike
   ``t_strike = (-nx_updip, ny_updip)``.
3. Dual-Ratio Radioelement (K/Th + U/Th) Redox-Contact & Strike Concordance
   (Dickson & Scott 1977; Nash 2010):
   Combines potassic adularia-sericite alteration (``K/(Th+10)``) with redox-front
   uranium mobilization (``U/(Th+10)`` ridge & gradient from GeoDAWN Band 3 ``U``)
   and directional strike concordance ``cos^2(theta_rad - theta_sub)`` with the
   updip subsurface fault ramp.
4. En-Echelon Relay-Ramp Transfer Tensor & Playa-Filtered MT Conduit
   (Faulds et al. 2006, 2011):
   Captures longitudinal basement/gravity transfer gradients ``|t_sub . grad B|``
   in step-over relay ramps and filters out flat-lying deep basin-floor playa
   smectite clays (``B > 900 m``) from Band 17 ``cond_surf`` horizontal gradients.
5. Selective Branch Quadrant Calibration
   (resolving ``#IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION``):
   Applies branch-selective within-quadrant quantile calibration across the 3-branch
   (Full, Province-Debiased, Subsurface-Listric-Knickzone) LOQO ensemble so low-strain
   NE Paleozoic carbonate horsts are captured without over-suppressing SW/SE scarps.

Strict zero-leakage invariant: no fault catalogue array enters feature computation,
and ``dist_known_fault_px`` in GDR #1391 is never read.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

from .breakline import spaced_top_mask
from .coulomb_loqo import (
    _grad_xy,
    _sat,
    directional_ridge_1d,
    gdr_blind_thermal_features,
    hessian_ridge_strength,
)
from .hydroconduit import _clean_valid
from .knick_loqo import (
    DEBIASED_INDICES as BASE_DEBIASED_INDICES,
    FEATURE_NAMES as BASE_FEATURE_NAMES,
    SUB_KNICK_INDICES as BASE_SUB_KNICK_INDICES,
    calibrate_quadrant_probabilities,
    compute_knick_loqo_stack,
    fit_single_loqo,
)

LISTRIC_EXTRA_NAMES: tuple[str, ...] = (
    "f31_listric_updip_sub_ramp",
    "f32_listric_scarp_knick_lock",
    "f33_carb_bouguer_base_updip",
    "f34_rad_uth_kth_strike_concord",
    "f35_relay_ramp_strike_transfer",
    "f36_mt_playa_deconfound_conduit",
)

FEATURE_NAMES: tuple[str, ...] = BASE_FEATURE_NAMES + LISTRIC_EXTRA_NAMES

DEBIASED_INDICES: tuple[int, ...] = BASE_DEBIASED_INDICES + (30, 31, 32, 33, 34, 35)
SUB_KNICK_INDICES: tuple[int, ...] = BASE_SUB_KNICK_INDICES + (30, 31, 32, 33, 34, 35)

__all__ = [
    "LISTRIC_EXTRA_NAMES",
    "FEATURE_NAMES",
    "DEBIASED_INDICES",
    "SUB_KNICK_INDICES",
    "bilinear_sample_2d",
    "compute_listric_extra_channels",
    "compute_listric_loqo_stack",
    "fit_predict_listric_loqo",
    "build_listric_crest_surface",
    "spaced_top_mask",
]


def bilinear_sample_2d(
    field: np.ndarray,
    sample_y: np.ndarray,
    sample_x: np.ndarray,
    valid: np.ndarray,
) -> np.ndarray:
    """Vectorized bilinear interpolation of ``field`` at ``(sample_y, sample_x)``."""
    h, w = field.shape
    valid_b = np.asarray(valid, dtype=bool)
    f = np.where(valid_b & np.isfinite(field), field, 0.0).astype(np.float32)
    yc = np.clip(sample_y, 0.0, float(h - 1.001)).astype(np.float32)
    xc = np.clip(sample_x, 0.0, float(w - 1.001)).astype(np.float32)
    y0 = np.floor(yc).astype(np.int32)
    x0 = np.floor(xc).astype(np.int32)
    y1 = np.minimum(y0 + 1, h - 1)
    x1 = np.minimum(x0 + 1, w - 1)
    wy = yc - y0
    wx = xc - x0
    out = (
        (1.0 - wy) * ((1.0 - wx) * f[y0, x0] + wx * f[y0, x1])
        + wy * ((1.0 - wx) * f[y1, x0] + wx * f[y1, x1])
    )
    out[~valid_b] = 0.0
    return out.astype(np.float32)


def compute_listric_extra_channels(
    *,
    l_topo: np.ndarray,
    l_knick: np.ndarray,
    l_sub: np.ndarray,
    grav_slope: np.ndarray,
    grav_vg: np.ndarray,
    det_elev: np.ndarray,
    grav_anom: np.ndarray,
    depth_to_base: np.ndarray,
    cond_surf: np.ndarray,
    grav_hg: np.ndarray,
    rad_k: np.ndarray,
    rad_th: np.ndarray,
    rad_u: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute the 6 new LISTRICLOQO channels (f31-f36) + updip listric, interfluve
    knickpoint bridge, and radioelement-relay 1D localization channels.
    """
    valid_b = np.asarray(valid, dtype=bool)

    # 1. Regional updip footwall-directed unit normal vector n_updip = (ny_up, nx_up)
    b_clean = np.maximum(_clean_valid(depth_to_base, valid_b), 0.0).astype(np.float32)
    log_b = np.log1p(b_clean / 20.0).astype(np.float32)
    by, bx = _grad_xy(log_b, valid_b, sigma=3.0)
    gy, gx = _grad_xy(grav_anom, valid_b, sigma=3.0)
    zy, zx = _grad_xy(det_elev, valid_b, sigma=3.0)

    nb = np.hypot(by, bx) + np.float32(1e-6)
    ng = np.hypot(gy, gx) + np.float32(1e-6)
    nz = np.hypot(zy, zx) + np.float32(1e-6)

    vy = -0.45 * (by / nb) + 0.35 * (gy / ng) + 0.20 * (zy / nz)
    vx = -0.45 * (bx / nb) + 0.35 * (gx / ng) + 0.20 * (zx / nz)
    del by, bx, gy, gx, zy, zx, nb, ng, nz
    vn = np.hypot(vy, vx) + np.float32(1e-6)
    ny_up = (vy / vn).astype(np.float32)
    nx_up = (vx / vn).astype(np.float32)
    ty_st = (-nx_up).astype(np.float32)
    tx_st = ny_up.astype(np.float32)
    del vy, vx, vn

    # 2. Carbonate-horst Bouguer gravity & basement rollover step field
    gs_clean = np.maximum(_clean_valid(grav_slope, valid_b), 0.0).astype(np.float32)
    gh_clean = np.maximum(_clean_valid(grav_hg, valid_b), 0.0).astype(np.float32)
    gs_med = float(np.median(gs_clean[valid_b])) + 1e-5
    gh_med = float(np.median(gh_clean[valid_b])) + 1e-5
    grav_step = (0.55 * _sat(gs_clean, 1.4 * gs_med) + 0.45 * _sat(gh_clean, 1.4 * gh_med)).astype(
        np.float32
    )
    del gs_clean, gh_clean

    dby2, dbx2 = _grad_xy(log_b, valid_b, sigma=1.8)
    b_grad_mag = np.hypot(dby2, dbx2)
    b_grad_med = float(np.median(b_grad_mag[valid_b])) + 1e-5
    base_step = _sat(b_grad_mag, 1.4 * b_grad_med)
    b_hess = hessian_ridge_strength(log_b, valid_b, sigma=2.2)
    b_hess_med = float(np.median(b_hess[valid_b])) + 1e-5
    base_shoulder = _sat(b_hess, 1.5 * b_hess_med)
    del b_hess

    carb_bouguer_in_situ = np.where(
        valid_b,
        0.44 * grav_step + 0.34 * base_step + 0.22 * base_shoulder,
        0.0,
    ).astype(np.float32)
    del base_step, base_shoulder

    sub_total_pure = (0.55 * np.asarray(l_sub, dtype=np.float32) + 0.45 * grav_step).astype(np.float32)
    sub_ramp = np.where(
        valid_b,
        0.56 * np.asarray(l_sub, dtype=np.float32) + 0.44 * carb_bouguer_in_situ,
        0.0,
    ).astype(np.float32)
    del grav_step

    # 3. Updip Listric Dip-Offset Projection (Grauch & Cordell 1987) + Interfluve Facet Bridge
    h, w = l_sub.shape
    yy, xx = np.meshgrid(
        np.arange(h, dtype=np.float32),
        np.arange(w, dtype=np.float32),
        indexing="ij",
    )
    b_smooth = gaussian_filter(b_clean, sigma=2.5).astype(np.float32)
    delta_px = np.clip(2.4 + 0.0048 * b_smooth, 2.4, 4.8).astype(np.float32)
    del b_smooth

    ramp_sched = bilinear_sample_2d(sub_ramp, yy - delta_px * ny_up, xx - delta_px * nx_up, valid_b)
    ramp_s26 = bilinear_sample_2d(sub_ramp, yy - 2.6 * ny_up, xx - 2.6 * nx_up, valid_b)
    ramp_s36 = bilinear_sample_2d(sub_ramp, yy - 3.6 * ny_up, xx - 3.6 * nx_up, valid_b)
    ramp_s46 = bilinear_sample_2d(sub_ramp, yy - 4.6 * ny_up, xx - 4.6 * nx_up, valid_b)

    carb_s34 = bilinear_sample_2d(carb_bouguer_in_situ, yy - 3.4 * ny_up, xx - 3.4 * nx_up, valid_b)
    carb_s46 = bilinear_sample_2d(carb_bouguer_in_situ, yy - 4.6 * ny_up, xx - 4.6 * nx_up, valid_b)

    # Pure updip-projected subsurface ramp (s in {3.6, 4.4, 5.2} px updip of hanging-wall ramp):
    sub_u36 = bilinear_sample_2d(sub_total_pure, yy - 3.6 * ny_up, xx - 3.6 * nx_up, valid_b)
    sub_u44 = bilinear_sample_2d(sub_total_pure, yy - 4.4 * ny_up, xx - 4.4 * nx_up, valid_b)
    sub_u52 = bilinear_sample_2d(sub_total_pure, yy - 5.2 * ny_up, xx - 5.2 * nx_up, valid_b)
    l_listric_updip = np.where(
        valid_b,
        0.45 * sub_u36 + 0.35 * sub_u44 + 0.20 * sub_u52,
        0.0,
    ).astype(np.float32)
    del sub_total_pure, sub_u36, sub_u44, sub_u52

    # Along-strike interfluve facet-spur bridge of incised canyon knickpoints (+/- 3.8 & +/- 4.8 px):
    kn_p38 = bilinear_sample_2d(l_knick, yy + 3.8 * ty_st, xx + 3.8 * tx_st, valid_b)
    kn_m38 = bilinear_sample_2d(l_knick, yy - 3.8 * ty_st, xx - 3.8 * tx_st, valid_b)
    kn_p48 = bilinear_sample_2d(l_knick, yy + 4.8 * ty_st, xx + 4.8 * tx_st, valid_b)
    kn_m48 = bilinear_sample_2d(l_knick, yy - 4.8 * ty_st, xx - 4.8 * tx_st, valid_b)
    l_knick_bridge = np.where(
        valid_b,
        0.55 * (0.5 * (kn_p38 + kn_m38))
        + 0.45 * np.sqrt(np.maximum(kn_p38, kn_p48) * np.maximum(kn_m38, kn_m48)),
        0.0,
    ).astype(np.float32)
    del yy, xx, delta_px, sub_ramp, kn_p38, kn_m38, kn_p48, kn_m48, ty_st, tx_st

    f31_listric_updip_sub_ramp = np.where(
        valid_b,
        np.clip(
            0.40 * ramp_sched
            + 0.32 * np.maximum(ramp_s26, ramp_s36)
            + 0.28 * np.maximum(ramp_s36, ramp_s46),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)

    f33_carb_bouguer_base_updip = np.where(
        valid_b,
        np.clip(0.35 * carb_bouguer_in_situ + 0.40 * carb_s34 + 0.25 * carb_s46, 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del carb_bouguer_in_situ, ramp_sched, ramp_s26, ramp_s36, ramp_s46, carb_s34, carb_s46

    surf_break = np.maximum(np.asarray(l_topo, dtype=np.float32), np.asarray(l_knick, dtype=np.float32))
    f32_listric_scarp_knick_lock = np.where(
        valid_b,
        np.clip(np.sqrt(np.maximum(surf_break, 0.04) * np.maximum(f31_listric_updip_sub_ramp, 0.0)), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del surf_break

    # 4. Dual-Ratio Radioelement (K/Th + U/Th) Redox-Contact & Strike Concordance (f34)
    valid_rad = (
        valid_b
        & np.isfinite(rad_k)
        & np.isfinite(rad_th)
        & np.isfinite(rad_u)
        & (np.asarray(rad_th) > 0)
    )
    k_th = np.where(
        valid_rad,
        np.asarray(rad_k, dtype=np.float32) / (np.asarray(rad_th, dtype=np.float32) + np.float32(10.0)),
        0.0,
    ).astype(np.float32)
    u_th = np.where(
        valid_rad,
        np.asarray(rad_u, dtype=np.float32) / (np.asarray(rad_th, dtype=np.float32) + np.float32(10.0)),
        0.0,
    ).astype(np.float32)
    ky, kx = _grad_xy(k_th, valid_rad, sigma=1.8)
    uy, ux = _grad_xy(u_th, valid_rad, sigma=1.8)
    u_hess = hessian_ridge_strength(u_th, valid_rad, sigma=2.0)
    del k_th, u_th, valid_rad

    ry = 0.52 * ky + 0.48 * uy
    rx = 0.52 * kx + 0.48 * ux
    del ky, kx, uy, ux
    rmag = np.hypot(ry, rx) + np.float32(1e-6)
    rmag_med = float(np.median(rmag[valid_b])) + 1e-5
    u_hess_med = float(np.median(u_hess[valid_b])) + 1e-5
    rad_edge = 0.65 * _sat(rmag, 1.5 * rmag_med) + 0.35 * _sat(u_hess, 1.5 * u_hess_med)
    cos_align = np.abs((ry / rmag) * ny_up + (rx / rmag) * nx_up)
    del ry, rx, rmag, u_hess

    f34_rad_uth_kth_strike_concord = np.where(
        valid_b,
        np.clip(
            rad_edge * (0.35 + 0.65 * (cos_align ** 2)) * np.sqrt(np.maximum(f31_listric_updip_sub_ramp, 0.12)),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    del rad_edge, cos_align

    # 5. Relay-Ramp & Accommodation-Zone Longitudinal Basement Transfer Tensor (f35)
    gy2, gx2 = _grad_xy(grav_anom, valid_b, sigma=2.0)
    t_b = np.abs(-nx_up * dby2 + ny_up * dbx2)
    t_g = np.abs(-nx_up * gy2 + ny_up * gx2)
    del dby2, dbx2, gy2, gx2, ny_up, nx_up, log_b
    tb_med = float(np.median(t_b[valid_b])) + 1e-5
    tg_med = float(np.median(t_g[valid_b])) + 1e-5
    relay_raw = 0.55 * _sat(t_b, 1.5 * tb_med) + 0.45 * _sat(t_g, 1.5 * tg_med)
    del t_b, t_g
    f35_relay_ramp_strike_transfer = np.where(
        valid_b,
        np.clip(relay_raw * np.sqrt(np.maximum(f31_listric_updip_sub_ramp, 0.10)), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del relay_raw

    # 6. Playa-Deconfounded MT Fault Conduit (f36)
    cond_clean = np.maximum(_clean_valid(cond_surf, valid_b), np.float32(0.1))
    log_cond = np.log(cond_clean).astype(np.float32)
    cy, cx = _grad_xy(log_cond, valid_b, sigma=2.0)
    mt_grad = np.hypot(cy, cx)
    mt_med = float(np.median(mt_grad[valid_b])) + 1e-5
    mt_sat = _sat(mt_grad, 1.4 * mt_med)
    del cond_clean, log_cond, cy, cx, mt_grad

    vg_clean = _clean_valid(grav_vg, valid_b).astype(np.float32)
    vg_iqr = float(np.percentile(np.abs(vg_clean[valid_b]), 75.0)) + 1e-5
    vg_zero_lock = np.exp(-0.5 * ((vg_clean / (1.5 * vg_iqr)) ** 2)).astype(np.float32)
    playa_suppress = np.exp(-((b_clean / 900.0) ** 2)).astype(np.float32)
    del vg_clean, b_clean

    f36_mt_playa_deconfound_conduit = np.where(
        valid_b,
        np.clip(mt_sat * (0.30 + 0.70 * playa_suppress) * (0.40 + 0.60 * vg_zero_lock), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del mt_sat, playa_suppress, vg_zero_lock

    l_rad_relay = np.where(
        valid_b,
        np.clip(
            0.38 * f34_rad_uth_kth_strike_concord
            + 0.36 * f35_relay_ramp_strike_transfer
            + 0.26 * f36_mt_playa_deconfound_conduit,
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)

    return dict(
        f31_listric_updip_sub_ramp=f31_listric_updip_sub_ramp,
        f32_listric_scarp_knick_lock=f32_listric_scarp_knick_lock,
        f33_carb_bouguer_base_updip=f33_carb_bouguer_base_updip,
        f34_rad_uth_kth_strike_concord=f34_rad_uth_kth_strike_concord,
        f35_relay_ramp_strike_transfer=f35_relay_ramp_strike_transfer,
        f36_mt_playa_deconfound_conduit=f36_mt_playa_deconfound_conduit,
        L_listric_updip=l_listric_updip,
        L_knick_bridge=l_knick_bridge,
        L_rad_relay=l_rad_relay,
    )


def compute_listric_loqo_stack(
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
    """Compute the 36-feature LISTRICLOQO stack on ``footprint`` + 1D ridge branches."""
    foot = np.asarray(footprint, dtype=bool)
    base_stack = compute_knick_loqo_stack(
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
        gdr_plume_feat=gdr_plume_feat,
        footprint=foot,
    )
    valid = base_stack["valid"]
    l_topo = base_stack["L_topo"]
    l_knick = base_stack["L_knick"]
    l_sub = base_stack["L_sub"]

    n_foot = int(foot.sum())
    X_foot = np.zeros((n_foot, len(FEATURE_NAMES)), dtype=np.float32)
    X_foot[:, :30] = base_stack["X_foot"]
    del base_stack

    extra = compute_listric_extra_channels(
        l_topo=l_topo,
        l_knick=l_knick,
        l_sub=l_sub,
        grav_slope=grav_slope,
        grav_vg=grav_vg,
        det_elev=det_elev,
        grav_anom=grav_anom,
        depth_to_base=depth_to_base,
        cond_surf=cond_surf,
        grav_hg=grav_hg,
        rad_k=rad_k,
        rad_th=rad_th,
        rad_u=rad_u,
        valid=valid,
    )
    for k_i, k_name in enumerate(LISTRIC_EXTRA_NAMES):
        X_foot[:, 30 + k_i] = extra[k_name][foot]

    return {
        "X_foot": X_foot,
        "valid": valid,
        "L_topo": l_topo,
        "L_knick": l_knick,
        "L_knick_bridge": extra["L_knick_bridge"],
        "L_sub": l_sub,
        "L_listric_updip": extra["L_listric_updip"],
        "L_rad_relay": extra["L_rad_relay"],
    }


def fit_predict_listric_loqo(
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
    max_iter: int = 190,
    w_full: float = 0.14,
    w_debiased: float = 0.36,
    w_sub: float = 0.50,
    calibrate_quadrants: bool = True,
    calib_weight_full: float = 0.50,
    calib_weight_sub: float = 0.84,
    power_gamma: float = 3.3,
) -> dict[str, np.ndarray]:
    """Fit the 3-branch (Full, Province-Debiased, Subsurface-Listric-Knickzone) LOQO ensemble
    with selective branch quadrant calibration (`#IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION`).
    """
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

    if calibrate_quadrants:
        p_full_cal = calibrate_quadrant_probabilities(
            p_full, valid_b, quad, calib_weight=calib_weight_full, power_gamma=power_gamma
        )
        p_sub_deb = (
            (np.float32(w_debiased) * p_deb + np.float32(w_sub) * p_sub)
            / np.float32(max(w_debiased + w_sub, 1e-6))
        ).astype(np.float32)
        p_sub_deb_cal = calibrate_quadrant_probabilities(
            p_sub_deb, valid_b, quad, calib_weight=calib_weight_sub, power_gamma=power_gamma
        )
        cal_proba = (
            np.float32(w_full) * p_full_cal
            + np.float32(w_debiased + w_sub) * p_sub_deb_cal
        ).astype(np.float32)
    else:
        cal_proba = raw_proba.copy()

    return {
        "p_full": p_full,
        "p_debiased": p_deb,
        "p_sub": p_sub,
        "raw_proba": raw_proba,
        "cal_proba": cal_proba,
    }


def build_listric_crest_surface(
    proba_2d: np.ndarray,
    l_topo: np.ndarray,
    l_knick_bridge: np.ndarray,
    l_listric_updip: np.ndarray,
    l_rad_relay: np.ndarray,
    valid: np.ndarray,
    *,
    topo_weight: float = 0.14,
    knick_weight: float = 0.95,
    listric_weight: float = 1.50,
    rad_relay_weight: float = 1.15,
) -> dict[str, np.ndarray]:
    """Combine LISTRICLOQO fault probability with updip-projected listric ramp,
    interfluve-bridged canyon knickzone, radioelement/relay-transfer, and topographic 1D crests.
    """
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0), 0.0)

    e_line = np.maximum(
        np.float32(topo_weight) * np.asarray(l_topo, dtype=np.float32),
        np.float32(knick_weight) * np.asarray(l_knick_bridge, dtype=np.float32),
    )
    e_line = np.maximum(
        e_line,
        np.float32(listric_weight) * np.asarray(l_listric_updip, dtype=np.float32),
    )
    e_line = np.maximum(
        e_line,
        np.float32(rad_relay_weight) * np.asarray(l_rad_relay, dtype=np.float32),
    )

    s_crest = np.where(
        valid_b,
        p * (np.float32(0.14) + np.float32(0.86) * e_line),
        0.0,
    ).astype(np.float32)

    ridge_1d = (
        directional_ridge_1d(s_crest, valid_b)
        | directional_ridge_1d(np.where(valid_b, p * l_listric_updip, 0.0).astype(np.float32), valid_b)
        | directional_ridge_1d(np.where(valid_b, p * l_knick_bridge, 0.0).astype(np.float32), valid_b)
        | directional_ridge_1d(np.where(valid_b, p * l_rad_relay, 0.0).astype(np.float32), valid_b)
    )
    return {
        "S_crest": s_crest,
        "E_line": np.where(valid_b, e_line, 0.0).astype(np.float32),
        "ridge_1d": ridge_1d,
    }
