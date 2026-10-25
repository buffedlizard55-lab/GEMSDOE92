"""LISTRICLOQO lane: Listric Normal-Fault Dip-Offset Hanging-Wall Pullback,
Full 2D Gravity-Gradient Tensor & Riedel (18 deg) En-Echelon Coupling, and
Selective Subsurface-Branch Quadrant-Calibrated LOQO.

Pre-registered hypothesis & equations: docs/HYPOTHESES_20261025_LISTRICLOQO.md.

Resolves three coupled physical and statistical bottlenecks from prior sessions:
1. Dip-Offset Geometry of Basin-and-Range Normal Faults (LISTRIC-ASYMMETRY-DIP):
   Normal faults dip 45-60 deg into the hanging wall, displacing the subsurface
   gravity/basement/RTP/MT gradient maximum 300-500 m (3-5 px) downslope into the
   hanging wall relative to the surface fault scarp / Wallace basal toe. Up-dip
   hanging-wall pullback projects subsurface corroboration back onto the surface
   fault trace while down-dip footwall projection captures synthetic piedmont
   accommodation splays.
2. Full 2D Horizontal-Vertical Gravity-Gradient Tensor & Synthetic Riedel (18 deg)
   Coupling (TENSOR-RIEDEL, Pedersen & Rasmussen 1990; Faulds & Hinz 2015):
   Extracts 2D horizontal gravity gradient tensor eigenvalues (Lambda_1, Lambda_2),
   3D analytic signal tilt from Bands 5, 11, 13, 18, and 18-deg synthetic Riedel
   en-echelon obliquity between surface scarp strike and basement gravity strike.
3. Selective Subsurface-Branch Quadrant Calibration (#IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION):
   Calibrates the subsurface/debiased LOQO branches across quadrants while blending
   with prior-preserving full-stack probabilities, restoring NE (Q1) fault recall
   without starving SW Walker Lane fault density or colliding with local/public
   registry rasters.

Strict zero-leakage invariant: no fault catalogue array enters any feature
or surface function in this module.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt, gaussian_filter

from .breakline import percentile_rank, spaced_top_mask
from .coulomb_loqo import (
    _grad_xy,
    _sat,
    directional_ridge_1d,
    gdr_blind_thermal_features,
)
from .hydroconduit import (
    _clean_valid,
    coherence_and_strike_deg,
    cross_strike_monotonicity,
)
from .knick_loqo import (
    FEATURE_NAMES as KNICK_FEATURE_NAMES,
    calibrate_quadrant_probabilities,
    compute_knick_loqo_stack,
    fit_single_loqo,
    thalweg_concavity_strength,
)

__all__ = [
    "EXTRA_FEATURE_NAMES",
    "FEATURE_NAMES",
    "DEBIASED_INDICES",
    "SUB_LISTRIC_INDICES",
    "sample_bilinear_offset",
    "compute_gravity_tensor_and_riedel",
    "compute_listric_dip_operators",
    "compute_listric_loqo_stack",
    "fit_predict_listric_loqo",
    "build_listric_crest_surface",
    "gdr_blind_thermal_features",
    "spaced_top_mask",
]

EXTRA_FEATURE_NAMES: tuple[str, ...] = (
    "listric_hw_updip_pullback",
    "listric_fw_downdip_splay",
    "wallace_basal_toe_asym",
    "grav_tensor_3d_tilt",
    "grav_tensor_contact_ecc",
    "riedel_en_echelon_coupling",
)

FEATURE_NAMES: tuple[str, ...] = KNICK_FEATURE_NAMES + EXTRA_FEATURE_NAMES

# Province-debiased feature subset (30 features): excludes raw regional baseline levels (5, 6, 16, 17, 18, 20)
DEBIASED_INDICES: tuple[int, ...] = tuple(
    i for i in range(len(FEATURE_NAMES)) if i not in (5, 6, 16, 17, 18, 20)
)

# Subsurface + Listric + Knickzone + Gravity-Tensor subset (31 features):
# excludes raw surface slope-Hessian ridges (0, 1, 2) and raw regional strain (17, 18)
SUB_LISTRIC_INDICES: tuple[int, ...] = tuple(
    i for i in range(len(FEATURE_NAMES)) if i not in (0, 1, 2, 17, 18)
)


def sample_bilinear_offset(
    arr: np.ndarray,
    dy: np.ndarray,
    dx: np.ndarray,
) -> np.ndarray:
    """Vectorized bilinear interpolation of ``arr`` at per-pixel offsets ``(y + dy, x + dx)``."""
    h, w = arr.shape
    yy = np.clip(np.arange(h, dtype=np.float32)[:, None] + dy, 0.0, float(h - 1))
    xx = np.clip(np.arange(w, dtype=np.float32)[None, :] + dx, 0.0, float(w - 1))
    y0 = np.floor(yy).astype(np.int32)
    x0 = np.floor(xx).astype(np.int32)
    y1 = np.minimum(y0 + 1, h - 1)
    x1 = np.minimum(x0 + 1, w - 1)
    wy = (yy - y0).astype(np.float32)
    wx = (xx - x0).astype(np.float32)
    del yy, xx
    return (
        (1.0 - wy) * ((1.0 - wx) * arr[y0, x0] + wx * arr[y0, x1])
        + wy * ((1.0 - wx) * arr[y1, x0] + wx * arr[y1, x1])
    ).astype(np.float32)


def compute_gravity_tensor_and_riedel(
    *,
    det_elev: np.ndarray,
    grav_anom: np.ndarray,
    grav_slope: np.ndarray,
    grav_vg: np.ndarray,
    valid: np.ndarray,
    riedel_deg: float = 18.0,
    riedel_sigma_deg: float = 11.0,
) -> dict[str, np.ndarray]:
    """Compute 2D horizontal-vertical gravity gradient tensor invariants and 18-deg Riedel coupling."""
    valid_b = np.asarray(valid, dtype=bool)
    g_clean = gaussian_filter(_clean_valid(grav_anom, valid_b), 2.0).astype(np.float32)
    gy, gx = np.gradient(g_clean)
    gyy, gxy = np.gradient(gy)
    gxy2, gxx = np.gradient(gx)
    gxy_sym = (0.5 * (gxy + gxy2)).astype(np.float32)
    del g_clean, gy, gx, gxy, gxy2

    # Eigenvalues Lambda_1 >= Lambda_2 of the 2x2 horizontal gravity gradient tensor G_h
    tr = (gxx + gyy).astype(np.float32)
    rad = np.sqrt((gxx - gyy) ** 2 + 4.0 * gxy_sym * gxy_sym).astype(np.float32)
    lam1 = 0.5 * (tr + rad)
    lam2 = 0.5 * (tr - rad)
    frob_sq = (gxx * gxx + 2.0 * gxy_sym * gxy_sym + gyy * gyy).astype(np.float32)
    del gxx, gyy, gxy_sym, tr

    # Horizontal gradient of vertical gravity derivative (G_xz, G_yz) from Band 11
    vg_clean = gaussian_filter(_clean_valid(grav_vg, valid_b), 1.5).astype(np.float32)
    vgy, vgx = np.gradient(vg_clean)
    gvz_norm = (np.hypot(vgy, vgx) * np.float32(0.05)).astype(np.float32)
    del vg_clean, vgy, vgx

    # 3D Gravity-Tensor Analytic Signal Tilt (Pedersen & Rasmussen 1990; Beiki 2010)
    grav_3d_tilt = np.where(
        valid_b,
        gvz_norm / np.sqrt(gvz_norm * gvz_norm + frob_sq + np.float32(1e-4)),
        0.0,
    ).astype(np.float32)
    del gvz_norm, frob_sq

    # Gravity-Tensor Fault-Contact Eccentricity
    gs_clean = np.maximum(_clean_valid(grav_slope, valid_b), 0.0)
    ecc_raw = rad / (np.abs(lam1) + np.abs(lam2) + np.float32(1e-4))
    grav_ecc = np.where(
        valid_b,
        np.clip(ecc_raw, 0.0, 1.0) * _sat(gs_clean, 0.08),
        0.0,
    ).astype(np.float32)
    del rad, lam1, lam2, gs_clean, ecc_raw

    # Synthetic Riedel (R-shear, ~18 deg) En-Echelon Obliquity Coupling
    coh_topo, az_topo = coherence_and_strike_deg(det_elev, valid_b)
    coh_grav, az_grav = coherence_and_strike_deg(grav_anom, valid_b)
    diff_deg = np.abs(az_topo - az_grav) % np.float32(180.0)
    acute_deg = np.minimum(diff_deg, np.float32(180.0) - diff_deg)
    riedel_kernel = np.exp(
        -0.5 * ((acute_deg - np.float32(riedel_deg)) / np.float32(riedel_sigma_deg)) ** 2
    ).astype(np.float32)
    riedel_coup = np.where(
        valid_b,
        riedel_kernel * np.sqrt(np.maximum(coh_topo * coh_grav, 0.0)),
        0.0,
    ).astype(np.float32)
    del coh_topo, az_topo, coh_grav, az_grav, diff_deg, acute_deg, riedel_kernel

    return {
        "grav_tensor_3d_tilt": grav_3d_tilt,
        "grav_tensor_contact_ecc": grav_ecc,
        "riedel_en_echelon_coupling": riedel_coup,
    }


def compute_listric_dip_operators(
    *,
    det_elev: np.ndarray,
    det_elev_slope: np.ndarray,
    depth_to_base: np.ndarray,
    l_topo: np.ndarray,
    l_sub: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute Up-Dip Listric Pullback, Down-Dip Splay Projection, and Wallace Basal Toe."""
    valid_b = np.asarray(valid, dtype=bool)
    z0 = _clean_valid(det_elev, valid_b)
    s0 = np.maximum(_clean_valid(det_elev_slope, valid_b), 0.0)
    db0 = np.maximum(_clean_valid(depth_to_base, valid_b), 0.0)

    # Range-to-basin hanging-wall unit normal n_hw = -grad(G_3(z)) / ||grad(G_3(z))||
    zy3, zx3 = _grad_xy(z0, valid_b, sigma=3.0)
    gnorm = np.hypot(zy3, zx3) + np.float32(0.5)
    nhw_y = (-zy3 / gnorm).astype(np.float32)
    nhw_x = (-zx3 / gnorm).astype(np.float32)
    del zy3, zx3, gnorm

    # Hanging-wall basin deepening gate across +-4 px (400 m)
    db_hw = sample_bilinear_offset(db0, np.float32(4.0) * nhw_y, np.float32(4.0) * nhw_x)
    db_fw = sample_bilinear_offset(db0, np.float32(-4.0) * nhw_y, np.float32(-4.0) * nhw_x)
    basin_deepening = np.tanh(np.maximum(db_hw - db_fw, 0.0) / np.float32(150.0)).astype(np.float32)
    del db0, db_hw, db_fw

    # 1. Up-Dip Listric Hanging-Wall Subsurface Pullback (offsets +3.0 px and +5.0 px down-dip)
    sub_hw3 = sample_bilinear_offset(l_sub, np.float32(3.0) * nhw_y, np.float32(3.0) * nhw_x)
    sub_hw5 = sample_bilinear_offset(l_sub, np.float32(5.0) * nhw_y, np.float32(5.0) * nhw_x)
    sub_updip = np.maximum(sub_hw3, np.float32(0.85) * sub_hw5)
    del sub_hw3, sub_hw5
    listric_updip = np.where(
        valid_b,
        sub_updip * (np.float32(0.35) + np.float32(0.65) * basin_deepening),
        0.0,
    ).astype(np.float32)
    del sub_updip, basin_deepening

    # 2. Down-Dip Listric Range-Front-to-Basin Splay Projection (offsets -2.5 px and -4.0 px upslope)
    topo_fw25 = sample_bilinear_offset(l_topo, np.float32(-2.5) * nhw_y, np.float32(-2.5) * nhw_x)
    topo_fw40 = sample_bilinear_offset(l_topo, np.float32(-4.0) * nhw_y, np.float32(-4.0) * nhw_x)
    topo_downdip = np.maximum(topo_fw25, np.float32(0.80) * topo_fw40)
    del topo_fw25, topo_fw40
    listric_downdip = np.where(
        valid_b,
        np.sqrt(np.maximum(topo_downdip * l_sub, 0.0)),
        0.0,
    ).astype(np.float32)
    del topo_downdip

    # 3. Wallace Basal Piedmont Toe Asymmetry
    s_fw = sample_bilinear_offset(s0, np.float32(-3.0) * nhw_y, np.float32(-3.0) * nhw_x)
    s_hw = sample_bilinear_offset(s0, np.float32(3.0) * nhw_y, np.float32(3.0) * nhw_x)
    del nhw_y, nhw_x
    mu_step = cross_strike_monotonicity(z0, valid_b, half_span_px=3, normal_sigma=3.0, elev_floor_m=0.5)
    apron_asym = (np.maximum(s_fw - s_hw, 0.0) / (s_fw + s_hw + np.float32(1.0))) * mu_step
    del z0, s_fw, s_hw, mu_step
    toe_concav = thalweg_concavity_strength(det_elev, valid_b, sigma=2.0)
    wallace_toe = np.where(
        valid_b,
        _sat(toe_concav, 1.5) * (np.float32(0.30) + np.float32(0.70) * apron_asym),
        0.0,
    ).astype(np.float32)
    del toe_concav, apron_asym

    # Soft alpine cliff taper for bare >16 deg slopes lacking listric/subsurface support
    sub_support = np.maximum(l_sub, listric_updip)
    cliff_excess = np.maximum(s0 - np.float32(16.0), 0.0) / np.float32(14.0)
    cliff_taper = np.exp(-cliff_excess * np.maximum(1.0 - np.float32(2.2) * sub_support, 0.0)).astype(
        np.float32
    )
    del s0, sub_support, cliff_excess

    l_topo_listric = np.where(
        valid_b,
        (
            np.float32(0.55) * l_topo * (np.float32(0.65) + np.float32(0.70) * listric_updip)
            + np.float32(0.45) * wallace_toe
        )
        * cliff_taper,
        0.0,
    ).astype(np.float32)
    del cliff_taper

    return {
        "listric_hw_updip_pullback": listric_updip,
        "listric_fw_downdip_splay": listric_downdip,
        "wallace_basal_toe_asym": wallace_toe,
        "L_topo_listric": l_topo_listric,
    }


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
    """Compute the 36 catalogue-free LISTRICLOQO features and 1D localization channels."""
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
    l_knick_base = base_stack["L_knick"]
    l_sub_base = base_stack["L_sub"]

    dip_ops = compute_listric_dip_operators(
        det_elev=det_elev,
        det_elev_slope=det_elev_slope,
        depth_to_base=depth_to_base,
        l_topo=l_topo,
        l_sub=l_sub_base,
        valid=valid,
    )
    gt_ops = compute_gravity_tensor_and_riedel(
        det_elev=det_elev,
        grav_anom=grav_anom,
        grav_slope=grav_slope,
        grav_vg=grav_vg,
        valid=valid,
    )

    foot_idx = np.flatnonzero(foot)
    n_foot = int(foot_idx.size)
    X_36 = np.zeros((n_foot, len(FEATURE_NAMES)), dtype=np.float32)
    X_36[:, :30] = base_stack["X_foot"]
    del base_stack

    extra_arrays = (
        dip_ops["listric_hw_updip_pullback"],
        dip_ops["listric_fw_downdip_splay"],
        dip_ops["wallace_basal_toe_asym"],
        gt_ops["grav_tensor_3d_tilt"],
        gt_ops["grav_tensor_contact_ecc"],
        gt_ops["riedel_en_echelon_coupling"],
    )
    for k, arr2d in enumerate(extra_arrays):
        flat = np.asarray(arr2d, dtype=np.float32).ravel()[foot_idx]
        X_36[:, 30 + k] = np.nan_to_num(flat, nan=0.0, posinf=0.0, neginf=0.0)

    updip = dip_ops["listric_hw_updip_pullback"]
    downdip = dip_ops["listric_fw_downdip_splay"]
    w_toe = dip_ops["wallace_basal_toe_asym"]
    gt_tilt = gt_ops["grav_tensor_3d_tilt"]
    gt_ecc = gt_ops["grav_tensor_contact_ecc"]
    riedel = gt_ops["riedel_en_echelon_coupling"]

    # Reconstruct 2D footprint maps of basement, MT, U/Th, and GDR blind plume from X_36
    def _col2d(col_idx: int) -> np.ndarray:
        out = np.zeros(foot.shape, dtype=np.float32)
        out.ravel()[foot_idx] = X_36[:, col_idx]
        return out

    base_grad = _sat(_col2d(5), 0.025)
    mt_grad = _sat(_col2d(19), 0.012)
    u_th = _sat(_col2d(22), 0.05)
    gdr_p = _col2d(23)

    # 1. Listric-corroborated Wallace basal toe & up-dip pullback channel
    l_topo_listric = np.where(
        valid,
        np.maximum(
            1.05 * w_toe * (0.35 + 0.65 * updip),
            0.90 * updip * (0.40 + 0.60 * (gt_ecc + gdr_p)),
        ),
        0.0,
    ).astype(np.float32)

    # 2. Down-dip piedmont accommodation splay channel
    l_knick = np.where(
        valid,
        1.15 * downdip * (0.40 + 0.60 * updip),
        0.0,
    ).astype(np.float32)

    # 3. 2D Gravity-Tensor eccentricity, 18-deg Riedel coupling & deep basin/MT/radiometric step
    l_sub = np.where(
        valid,
        1.25 * (
            0.38 * gt_ecc
            + 0.34 * riedel * gt_tilt
            + 0.28 * (0.50 * base_grad + 0.30 * mt_grad + 0.20 * u_th)
        ),
        0.0,
    ).astype(np.float32)

    return {
        "X_foot": X_36,
        "valid": valid,
        "L_topo": l_topo,
        "L_topo_listric": l_topo_listric,
        "L_knick": l_knick,
        "L_sub": l_sub,
    }


def _fit_loqo_branches(
    X_foot: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    label_mask: np.ndarray,
    branch_cols: list[tuple[int, ...] | None],
    *,
    excluded_mask: np.ndarray | None = None,
    guard_px: int = 12,
    neg_buffer_px: float = 5.0,
    neg_pos_ratio: int = 3,
    pos_cap: int = 22_000,
    seed: int = 20261025,
    max_iter: int = 75,
) -> list[np.ndarray]:
    """Fit multiple 4-quadrant LOQO feature-subset branches sharing EDT and index splits."""
    from sklearn.ensemble import HistGradientBoostingClassifier

    foot = np.asarray(footprint, dtype=bool)
    valid_b = np.asarray(valid, dtype=bool) & foot
    lbl = np.asarray(label_mask, dtype=bool) & valid_b
    excl = np.asarray(excluded_mask, dtype=bool) if excluded_mask is not None else np.zeros_like(foot)

    d_lbl = distance_transform_edt(~lbl)
    foot_row_map = np.full(foot.shape, -1, dtype=np.int32)
    foot_row_map[foot] = np.arange(int(foot.sum()), dtype=np.int32)

    outputs = [np.zeros(foot.shape, dtype=np.float32) for _ in branch_cols]
    present_quads = [int(q) for q in (0, 1, 2, 3) if np.any((quad == q) & valid_b)]

    for q in present_quads:
        target_q = (quad == q) & valid_b
        guard = binary_dilation(quad == q, iterations=int(guard_px)) if guard_px > 0 else (quad == q)
        train_dom = valid_b & (quad >= 0) & (quad != q) & (~guard) & (~excl)

        pos_idx = foot_row_map[train_dom & lbl]
        neg_idx = foot_row_map[train_dom & (~lbl) & (d_lbl > float(neg_buffer_px))]
        if pos_idx.size == 0 or neg_idx.size == 0:
            raise ValueError(
                f"Quadrant {q} LISTRICLOQO training split has empty class: pos={pos_idx.size}, neg={neg_idx.size}"
            )

        rng = np.random.default_rng(int(seed) + 97 * q)
        if pos_cap > 0 and pos_idx.size > pos_cap:
            pos_sel = rng.choice(pos_idx, size=int(pos_cap), replace=False)
            pos_sel.sort()
        else:
            pos_sel = pos_idx

        n_neg = min(int(neg_idx.size), max(int(pos_sel.size) * int(neg_pos_ratio), 1))
        if n_neg < neg_idx.size:
            neg_sel = rng.choice(neg_idx, size=n_neg, replace=False)
            neg_sel.sort()
        else:
            neg_sel = neg_idx

        tr_idx = np.concatenate([pos_sel, neg_sel])
        X_tr_all = X_foot[tr_idx]
        y_tr = np.concatenate([
            np.ones(pos_sel.size, dtype=np.int8),
            np.zeros(neg_sel.size, dtype=np.int8),
        ])
        pos_weight = float(neg_sel.size) / float(max(pos_sel.size, 1))
        sample_w = np.where(y_tr == 1, pos_weight, 1.0).astype(np.float32)
        te_idx = foot_row_map[target_q]
        X_te_all = X_foot[te_idx]

        for b_idx, cols in enumerate(branch_cols):
            X_tr = X_tr_all if cols is None else X_tr_all[:, list(cols)]
            clf = HistGradientBoostingClassifier(
                loss="log_loss",
                learning_rate=0.11,
                max_iter=int(max_iter),
                max_leaf_nodes=25,
                max_depth=5,
                min_samples_leaf=min(200, max(10, int(tr_idx.size // 40))),
                l2_regularization=10.0,
                early_stopping=False,
                random_state=int(seed) + 11 * b_idx + q,
            )
            clf.fit(X_tr, y_tr, sample_weight=sample_w)
            X_te = X_te_all if cols is None else X_te_all[:, list(cols)]
            Xb = clf._bin_mapper.transform(X_te)
            raw = np.full(X_te.shape[0], float(clf._baseline_prediction[0, 0]), dtype=np.float64)
            miss_idx = clf._bin_mapper.missing_values_bin_idx_
            for p_tree in clf._predictors:
                raw += p_tree[0].predict_binned(Xb, miss_idx, 4)
            outputs[b_idx][target_q] = (1.0 / (1.0 + np.exp(-raw))).astype(np.float32)
            del Xb, raw
        del X_te_all

    return outputs


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
    neg_pos_ratio: int = 3,
    seed: int = 20261025,
    max_iter: int = 95,
    w_full: float = 0.20,
    w_debiased: float = 0.35,
    w_sub: float = 0.45,
    calibrate_quadrants: bool = True,
    calib_weight: float = 0.72,
    power_gamma: float = 3.25,
) -> dict[str, np.ndarray]:
    """Fit the 3-branch (Full-36, Province-Debiased-30, Subsurface-Listric-31) LOQO ensemble."""
    valid_b = np.asarray(valid, dtype=bool) & np.asarray(footprint, dtype=bool)
    p_full, p_deb, p_sub = _fit_loqo_branches(
        X_foot,
        footprint,
        valid_b,
        quad,
        label_mask,
        [None, DEBIASED_INDICES, SUB_LISTRIC_INDICES],
        excluded_mask=excluded_mask,
        guard_px=guard_px,
        neg_buffer_px=neg_buffer_px,
        neg_pos_ratio=neg_pos_ratio,
        seed=int(seed),
        max_iter=max_iter,
    )
    raw_proba = (
        np.float32(w_full) * p_full
        + np.float32(w_debiased) * p_deb
        + np.float32(w_sub) * p_sub
    ).astype(np.float32)

    # Selective subsurface-branch calibration: calibrate subsurface/debiased branches strongly
    # to eliminate #IR-92-NE-QUADRANT-LOQO-COLLAPSE while blending with prior-preserving raw_proba
    if calibrate_quadrants:
        p_sub_ens = (np.float32(0.45) * p_deb + np.float32(0.55) * p_sub).astype(np.float32)
        p_sub_cal = calibrate_quadrant_probabilities(
            p_sub_ens, valid_b, quad, calib_weight=0.88, power_gamma=power_gamma
        )
        p_raw_cal = calibrate_quadrant_probabilities(
            raw_proba, valid_b, quad, calib_weight=calib_weight, power_gamma=power_gamma
        )
        cal_proba = (np.float32(0.65) * p_raw_cal + np.float32(0.35) * p_sub_cal).astype(np.float32)
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
    l_topo_listric: np.ndarray,
    l_sub: np.ndarray | None,
    valid: np.ndarray,
    *,
    l_knick: np.ndarray | None = None,
    topo_weight: float = 1.00,
    knick_weight: float = 1.00,
    sub_weight: float = 1.00,
) -> dict[str, np.ndarray]:
    """Combine LISTRICLOQO fault probability with 1D listric-scarp, splay & tensor crests."""
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0), 0.0)
    e_line = np.float32(topo_weight) * np.asarray(l_topo_listric, dtype=np.float32)
    if l_knick is not None:
        e_line = np.maximum(e_line, np.float32(knick_weight) * np.asarray(l_knick, dtype=np.float32))
    if l_sub is not None:
        e_line = np.maximum(e_line, np.float32(sub_weight) * np.asarray(l_sub, dtype=np.float32))

    s_crest = np.where(
        valid_b,
        (p ** np.float32(0.75)) * (np.float32(0.01) + np.float32(0.99) * e_line),
        0.0,
    ).astype(np.float32)
    ridge_1d = directional_ridge_1d(s_crest, valid_b)
    return {
        "S_crest": s_crest,
        "E_line": np.where(valid_b, e_line, 0.0).astype(np.float32),
        "ridge_1d": ridge_1d,
    }
