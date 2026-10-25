"""RELAYCONDUIT lane: Self-Excluded Oriented Fault-Tip Coulomb Relay Lobes,
Opposing-Tip Step-Over Bridges, Out-of-Fold Multi-Azimuth Structural Auto-Context,
and Sedimentary-Cover-Adaptive Blind Subsurface Hydrothermal Conduit Fusion.

Pre-registered BEFORE implementation in ``docs/HYPOTHESES_20261025_RELAYCONDUIT.md``.

Memory-disciplined implementation (< 1.3 GiB peak RSS inside 3.8 GiB / 0-swap sandbox):
reads raster bands on demand, writes each finished channel directly into ``X_foot[:, j]``
(float32), and frees full-grid temporaries immediately.
"""
from __future__ import annotations

import gc
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.ndimage import binary_dilation, distance_transform_edt, gaussian_filter, zoom
from scipy.signal import fftconvolve
from sklearn.ensemble import HistGradientBoostingClassifier

from .breakline import spaced_top_mask
from .coulomb_loqo import _grad_xy, _sat, directional_ridge_1d, gdr_blind_thermal_features, hessian_ridge_strength
from .faultnet import STRUCT8, endpoints, gaussian_density, own_gaussian_sum
from .hydroconduit import _clean_valid, coherence_and_strike_deg, cross_strike_monotonicity
from .knick_loqo import calibrate_quadrant_probabilities, mesoscale_zscore
from .ventscarp import (
    _decode_u8_band,
    _rasterize_2m_temperature_probes,
    _rasterize_active_thermal_springs,
    _rasterize_paleo_vents,
    anisotropic_strike_plume,
    subpixel_scarp_excess,
)

FEATURE_NAMES: tuple[str, ...] = (
    # Group S: Pure-Subsurface & Hydrothermal Conduit Channels (0..14; ZERO B12/B19/3DEP)
    "sub_grav_slope_meso",
    "sub_grav_tilt_ridge",
    "sub_grav_hess_s25",
    "sub_base_step_grad",
    "sub_base_flex_curv",
    "sub_mag_rtp_tilt_edge",
    "sub_mag_up150_demag",
    "sub_mag_vg_ridge",
    "sub_mt_claycap_grad",
    "sub_strain_transtension",
    "sub_seismic_coulomb",
    "sub_rad_k_th_z",
    "sub_rad_u_th_z",
    "sub_paleo_sinter_plume",
    "sub_probe2m_spring_plume",
    # Group G: USGS 3DEP 10 m Sub-Pixel Scarp, Chi-Knickpoints & Concordance (15..25)
    "geo_scarp10m_excess_max",
    "geo_scarp10m_excess_p90",
    "geo_scarp10m_curv_pied",
    "geo_scarp10m_coherence",
    "geo_chi10m_knick_step",
    "geo_chi10m_ksn",
    "geo_hess_s12",
    "geo_hess_s30",
    "geo_step_mono_600m",
    "geo_dip_concord_grav_base",
    "geo_lahontan_mimic_null",
    # Group A: Stage-1 Out-of-Fold Multi-Azimuth Structural Auto-Context (26..29)
    "oof_blind_line_short",
    "oof_blind_line_long",
    "oof_phys_line_short",
    "oof_phys_bridge_axial",
    # Group R: Self-Excluded Oriented Fault-Tip Coulomb Relay Lobes (30..34)
    "rc_tip_cone_short",
    "rc_tip_cone_long",
    "rc_stepover_bridge",
    "rc_tip_vs_shadow",
    "rc_reg_strike_align",
)

STAGE1_BLIND_COLS: tuple[int, ...] = tuple(range(0, 15))
STAGE1_PHYS_COLS: tuple[int, ...] = tuple(range(0, 26))
OOF_COLS: tuple[int, ...] = (26, 27, 28, 29)
RELAY_COLS: tuple[int, ...] = (30, 31, 32, 33, 34)

STAGE2_BLIND_RELAY_COLS: tuple[int, ...] = STAGE1_BLIND_COLS + (26, 27) + RELAY_COLS
STAGE2_FULL_RELAY_COLS: tuple[int, ...] = STAGE1_PHYS_COLS + OOF_COLS + RELAY_COLS
STAGE2_BLIND_NOTIP_COLS: tuple[int, ...] = STAGE1_BLIND_COLS + (26, 27)
STAGE2_FULL_NOTIP_COLS: tuple[int, ...] = STAGE1_PHYS_COLS + OOF_COLS

TIP_MAX_RADIUS_PX: int = 48

__all__ = [
    "FEATURE_NAMES",
    "STAGE1_BLIND_COLS",
    "STAGE1_PHYS_COLS",
    "OOF_COLS",
    "RELAY_COLS",
    "STAGE2_BLIND_RELAY_COLS",
    "STAGE2_FULL_RELAY_COLS",
    "STAGE2_BLIND_NOTIP_COLS",
    "STAGE2_FULL_NOTIP_COLS",
    "oriented_tip_relay_fields",
    "steerable_oof_autocontext",
    "compute_base_physics_stack",
    "fit_pairwise_stage1_oof",
    "fit_stage2_bimodal_loqo",
    "build_dual_conduit_surface",
    "spaced_top_mask",
]


def _tip_records(mask: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Extract skeleton endpoints with outward unit propagation vectors and length weights."""
    ep = endpoints(mask)
    objs = ndi.find_objects(labels)
    ys_out, xs_out, uys_out, uxs_out, w_out, comp_out = [], [], [], [], [], []
    for comp_id, sl in enumerate(objs, start=1):
        if sl is None:
            continue
        sub_c = labels[sl] == comp_id
        comp_size = int(sub_c.sum())
        sub_ep = ep[sl] & sub_c
        if not sub_ep.any():
            continue
        cy, cx = np.nonzero(sub_c)
        ey, ex = np.nonzero(sub_ep)
        len_w = float(min(max(comp_size - 1, 0) / 5.0, 1.0))
        y0, x0 = sl[0].start, sl[1].start
        for ry, rx in zip(ey, ex):
            dy = cy - ry
            dx = cx - rx
            d2 = dy * dy + dx * dx
            ring = (d2 >= 1) & (d2 <= 81)
            if ring.any() and len_w > 0.0:
                vy = float(ry) - float(dy[ring].mean() + ry)
                vx = float(rx) - float(dx[ring].mean() + rx)
                norm = float(np.hypot(vy, vx))
                uy, ux = (vy / norm, vx / norm) if norm > 1e-5 else (0.0, 0.0)
            else:
                uy, ux = 0.0, 0.0
            ys_out.append(y0 + int(ry))
            xs_out.append(x0 + int(rx))
            uys_out.append(uy)
            uxs_out.append(ux)
            w_out.append(len_w if (uy != 0.0 or ux != 0.0) else 0.0)
            comp_out.append(comp_id)
    return (
        np.asarray(ys_out, dtype=np.int32),
        np.asarray(xs_out, dtype=np.int32),
        np.asarray(uys_out, dtype=np.float32),
        np.asarray(uxs_out, dtype=np.float32),
        np.asarray(w_out, dtype=np.float32),
        np.asarray(comp_out, dtype=np.int32),
    )


def _stamp_tip_subset(
    ty: np.ndarray,
    tx: np.ndarray,
    uy: np.ndarray,
    ux: np.ndarray,
    tw: np.ndarray,
    shape: tuple[int, int],
    max_r: int = TIP_MAX_RADIUS_PX,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Accumulate short/long forward tip cones and step-over bridge scalar/vector fluxes."""
    h, w = shape
    cone_s = np.zeros(shape, dtype=np.float32)
    cone_l = np.zeros(shape, dtype=np.float32)
    bw = np.zeros(shape, dtype=np.float32)
    bjy = np.zeros(shape, dtype=np.float32)
    bjx = np.zeros(shape, dtype=np.float32)

    if ty.size == 0:
        return cone_s, cone_l, bw, bjy, bjx

    g_idx = np.arange(-max_r, max_r + 1, dtype=np.float32)
    gy_full, gx_full = np.meshgrid(g_idx, g_idx, indexing="ij")
    dist_full = np.hypot(gy_full, gx_full).astype(np.float32)
    inv_dist_full = np.where(dist_full > 0.0, 1.0 / np.maximum(dist_full, 1e-6), 0.0).astype(np.float32)
    decay_s_full = np.where((dist_full > 0.0) & (dist_full <= max_r), np.exp(-dist_full / 16.0), 0.0).astype(np.float32)
    decay_l_full = np.where((dist_full > 0.0) & (dist_full <= max_r), np.exp(-dist_full / 36.0), 0.0).astype(np.float32)
    decay_b_full = np.where((dist_full > 0.0) & (dist_full <= max_r), np.exp(-dist_full / 24.0), 0.0).astype(np.float32)

    for i in range(ty.size):
        wt = float(tw[i])
        if wt <= 0.0:
            continue
        cy, cx = int(ty[i]), int(tx[i])
        u_y, u_x = float(uy[i]), float(ux[i])

        y0, y1 = max(0, cy - max_r), min(h, cy + max_r + 1)
        x0, x1 = max(0, cx - max_r), min(w, cx + max_r + 1)
        sy0 = y0 - (cy - max_r)
        sy1 = sy0 + (y1 - y0)
        sx0 = x0 - (cx - max_r)
        sx1 = sx0 + (x1 - x0)

        dy = gy_full[sy0:sy1, sx0:sx1]
        dx = gx_full[sy0:sy1, sx0:sx1]
        inv_d = inv_dist_full[sy0:sy1, sx0:sx1]

        proj_cos = (dy * u_y + dx * u_x) * inv_d
        fwd = np.maximum(proj_cos, 0.0)
        fwd2 = fwd * fwd
        perp = np.abs(dy * u_x - dx * u_y)

        ks = wt * decay_s_full[sy0:sy1, sx0:sx1] * fwd2 * np.exp(-0.5 * (perp / 5.5) ** 2).astype(np.float32)
        kl = wt * decay_l_full[sy0:sy1, sx0:sx1] * fwd2 * np.exp(-0.5 * (perp / 11.5) ** 2).astype(np.float32)
        fwd_b = np.maximum(proj_cos + 0.15, 0.0) / 1.15
        kb = wt * decay_b_full[sy0:sy1, sx0:sx1] * (fwd_b * fwd_b) * np.exp(-0.5 * (perp / 9.5) ** 2).astype(np.float32)

        cone_s[y0:y1, x0:x1] += ks
        cone_l[y0:y1, x0:x1] += kl
        bw[y0:y1, x0:x1] += kb
        bjy[y0:y1, x0:x1] += kb * np.float32(u_y)
        bjx[y0:y1, x0:x1] += kb * np.float32(u_x)

    return cone_s, cone_l, bw, bjy, bjx


def oriented_tip_relay_fields(
    catalogue_visible: np.ndarray,
    edge_strike_deg: np.ndarray,
    valid: np.ndarray,
    max_r: int = TIP_MAX_RADIUS_PX,
) -> dict[str, np.ndarray]:
    """Compute 5 exact self-component-excluded fault-tip relay & stress-shadow channels."""
    vis = np.asarray(catalogue_visible, dtype=bool)
    v = np.asarray(valid, dtype=bool)
    shape = vis.shape
    labels, _ = ndi.label(vis, STRUCT8)

    ty, tx, uy, ux, tw, tcomp = _tip_records(vis, labels)
    cone_s, cone_l, bw, bjy, bjx = _stamp_tip_subset(ty, tx, uy, ux, tw, shape, max_r=max_r)

    if ty.size > 0:
        order = np.argsort(tcomp, kind="mergesort")
        ty_s, tx_s, uy_s, ux_s, tw_s, tc_s = ty[order], tx[order], uy[order], ux[order], tw[order], tcomp[order]
        uniq_c, starts, counts = np.unique(tc_s, return_index=True, return_counts=True)
        objs = ndi.find_objects(labels)
        for comp_id, st, cnt in zip(uniq_c, starts, counts):
            sl = objs[int(comp_id) - 1]
            if sl is None:
                continue
            own_mask = labels[sl] == comp_id
            oy, ox = np.nonzero(own_mask)
            oy = oy + sl[0].start
            ox = ox + sl[1].start
            for k in range(int(st), int(st + cnt)):
                wt = float(tw_s[k])
                if wt <= 0.0:
                    continue
                dy = (oy - int(ty_s[k])).astype(np.float32)
                dx = (ox - int(tx_s[k])).astype(np.float32)
                dist = np.hypot(dy, dx)
                in_r = (dist > 0.0) & (dist <= max_r)
                if not in_r.any():
                    continue
                oy_k, ox_k = oy[in_r], ox[in_r]
                dy_k, dx_k, d_k = dy[in_r], dx[in_r], dist[in_r]
                u_y, u_x = float(uy_s[k]), float(ux_s[k])
                proj_cos = (dy_k * u_y + dx_k * u_x) / np.maximum(d_k, 1e-6)
                fwd = np.maximum(proj_cos, 0.0)
                fwd2 = fwd * fwd
                perp = np.abs(dy_k * u_x - dx_k * u_y)

                ks = wt * np.exp(-d_k / 16.0) * fwd2 * np.exp(-0.5 * (perp / 5.5) ** 2)
                kl = wt * np.exp(-d_k / 36.0) * fwd2 * np.exp(-0.5 * (perp / 11.5) ** 2)
                fwd_b = np.maximum(proj_cos + 0.15, 0.0) / 1.15
                kb = wt * np.exp(-d_k / 24.0) * (fwd_b * fwd_b) * np.exp(-0.5 * (perp / 9.5) ** 2)

                cone_s[oy_k, ox_k] -= ks.astype(np.float32)
                cone_l[oy_k, ox_k] -= kl.astype(np.float32)
                bw[oy_k, ox_k] -= kb.astype(np.float32)
                bjy[oy_k, ox_k] -= (kb * u_y).astype(np.float32)
                bjx[oy_k, ox_k] -= (kb * u_x).astype(np.float32)

    np.maximum(cone_s, 0.0, out=cone_s)
    np.maximum(cone_l, 0.0, out=cone_l)
    np.maximum(bw, 0.0, out=bw)

    bridge_sq = bw * bw - (bjy * bjy + bjx * bjx)
    np.maximum(bridge_sq, 0.0, out=bridge_sq)
    bridge = np.sqrt(bridge_sq, dtype=np.float32)
    del bw, bjy, bjx, bridge_sq

    dens8 = gaussian_density(vis, 8.0) - own_gaussian_sum(labels, 8.0)
    np.maximum(dens8, 0.0, out=dens8)
    dens8 *= np.float32(500.0)

    rc_short = np.log1p(cone_s * np.float32(4.0)).astype(np.float32)
    rc_long = np.log1p(cone_l * np.float32(2.5)).astype(np.float32)
    rc_bridge = np.log1p(bridge * np.float32(6.0)).astype(np.float32)
    rc_shadow_diff = (rc_short + np.float32(0.5) * rc_bridge - np.float32(0.55) * np.log1p(dens8)).astype(np.float32)
    del cone_s, cone_l, bridge, dens8

    vs = gaussian_filter(vis.astype(np.float32), 1.5).astype(np.float32)
    gy, gx = np.gradient(vs)
    del vs
    gy[~vis] = 0.0
    gx[~vis] = 0.0
    t_comps = []
    for wgt in (gx * gx, gx * gy, gy * gy):
        full = gaussian_density(wgt, 38.0) - own_gaussian_sum(labels, 38.0, weights=wgt)
        t_comps.append(full)
        del wgt
    del gx, gy
    a_r, b_r, c_r = t_comps
    del t_comps
    norm_rad = 0.5 * np.arctan2(2.0 * b_r, a_r - c_r)
    reg_strike_deg = ((np.degrees(norm_rad) + 90.0) % 180.0).astype(np.float32)
    coh_reg = np.clip(
        (np.sqrt((a_r - c_r) ** 2 + 4.0 * b_r * b_r) / np.maximum(a_r + c_r, 1e-12)).astype(np.float32),
        0.0, 1.0,
    )
    del a_r, b_r, c_r, norm_rad

    d_rad = np.radians(np.asarray(edge_strike_deg, dtype=np.float32) - reg_strike_deg)
    rc_align = (np.cos(d_rad) ** 2 * coh_reg).astype(np.float32)
    del reg_strike_deg, coh_reg, d_rad

    for arr in (rc_short, rc_long, rc_bridge, rc_shadow_diff, rc_align):
        arr[~v] = 0.0
    return {
        "rc_tip_cone_short": rc_short,
        "rc_tip_cone_long": rc_long,
        "rc_stepover_bridge": rc_bridge,
        "rc_tip_vs_shadow": rc_shadow_diff,
        "rc_reg_strike_align": rc_align,
    }


def _oriented_aniso_max(
    log_odds_grid: np.ndarray,
    sigma_along: float,
    sigma_perp: float = 1.5,
    angles_deg: tuple[float, ...] = (0.0, 30.0, 60.0, 90.0, 120.0, 150.0),
) -> np.ndarray:
    """Low-memory 2x-decimated steerable line response (< 40 MiB temporary RAM)."""
    H, W = log_odds_grid.shape
    if H >= 256 and W >= 256:
        small = log_odds_grid[::2, ::2].astype(np.float32)
        sa = max(sigma_along * 0.5, 1.0)
        sp = max(sigma_perp * 0.5, 0.75)
        decimated = True
    else:
        small = log_odds_grid.astype(np.float32)
        sa, sp = float(sigma_along), float(sigma_perp)
        decimated = False

    rad = int(min(max(np.ceil(2.5 * sa), 3), 20))
    ax = np.arange(-rad, rad + 1, dtype=np.float32)
    yy, xx = np.meshgrid(ax, ax, indexing="ij")
    best_sm = np.full(small.shape, -1e9, dtype=np.float32)
    for ang in angles_deg:
        th = np.radians(float(ang))
        u_along = -yy * np.float32(np.cos(th)) + xx * np.float32(np.sin(th))
        u_perp = yy * np.float32(np.sin(th)) + xx * np.float32(np.cos(th))
        kern = np.exp(-0.5 * ((u_along / sa) ** 2 + (u_perp / sp) ** 2)).astype(np.float32)
        kern /= float(max(kern.sum(), 1e-8))
        resp = fftconvolve(small, kern, mode="same").astype(np.float32)
        np.maximum(best_sm, resp, out=best_sm)
    del small
    if not decimated:
        return best_sm
    zy = H / float(best_sm.shape[0])
    zx = W / float(best_sm.shape[1])
    out = zoom(best_sm, (zy, zx), order=1).astype(np.float32)
    return out[:H, :W]


def steerable_oof_autocontext(
    p_blind: np.ndarray,
    p_phys: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Build 4 multi-azimuth structural auto-context channels from Stage-1 OOF probabilities."""
    v = np.asarray(valid, dtype=bool)
    eps = np.float32(1e-4)
    pb = np.clip(np.where(v, p_blind, 0.05).astype(np.float32), eps, 1.0 - eps)
    pp = np.clip(np.where(v, p_phys, 0.05).astype(np.float32), eps, 1.0 - eps)

    lb = np.log(pb / (1.0 - pb)).astype(np.float32)
    lp = np.log(pp / (1.0 - pp)).astype(np.float32)
    del pb, pp
    lb_med = float(np.median(lb[v])) if v.any() else 0.0
    lp_med = float(np.median(lp[v])) if v.any() else 0.0
    lb = np.where(v, lb - np.float32(lb_med), 0.0).astype(np.float32)
    lp = np.where(v, lp - np.float32(lp_med), 0.0).astype(np.float32)

    blind_s = _oriented_aniso_max(lb, sigma_along=6.0, sigma_perp=1.5)
    blind_l = _oriented_aniso_max(lb, sigma_along=16.0, sigma_perp=2.0)
    del lb
    phys_s = _oriented_aniso_max(lp, sigma_along=6.0, sigma_perp=1.5)
    phys_l = _oriented_aniso_max(lp, sigma_along=16.0, sigma_perp=2.0)
    phys_iso = gaussian_filter(lp, sigma=10.0).astype(np.float32)
    phys_bridge_ax = (phys_l - np.float32(0.75) * phys_iso).astype(np.float32)
    del lp, phys_l, phys_iso

    for a in (blind_s, blind_l, phys_s, phys_bridge_ax):
        a[~v] = 0.0
    return {
        "oof_blind_line_short": blind_s,
        "oof_blind_line_long": blind_l,
        "oof_phys_line_short": phys_s,
        "oof_phys_bridge_axial": phys_bridge_ax,
    }


def _read_tf_band(ds: rasterio.DatasetReader, idx: int) -> np.ndarray:
    arr = ds.read(idx).astype(np.float32)
    arr[(~np.isfinite(arr)) | (arr <= -1e20)] = np.nan
    return arr


def _store_col(X_foot: np.ndarray, col: int, arr: np.ndarray, foot: np.ndarray, valid: np.ndarray) -> None:
    clean = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
    clean[~valid] = 0.0
    X_foot[:, col] = clean[foot]


def compute_base_physics_stack(
    *,
    training_features_tif: Path,
    geodawn_rad_tif: Path,
    geodawn_ext_tif: Path,
    topo_10m_tif: Path,
    dem10_chi_tif: Path,
    paleo_zip: Path,
    probe_2m_zip: Path,
    wellspring_csv: Path,
    footprint: np.ndarray,
) -> dict[str, object]:
    """Streaming low-memory (< 1.15 GiB RSS) computation of the 26 zero-catalogue channels."""
    foot = np.asarray(footprint, dtype=bool)
    shape = foot.shape
    n_foot = int(foot.sum())
    X_foot = np.zeros((n_foot, len(FEATURE_NAMES)), dtype=np.float32)
    L_sub = np.zeros(shape, dtype=np.float32)
    L_geo = np.zeros(shape, dtype=np.float32)

    with rasterio.open(training_features_tif) as ds:
        ref_transform = ds.transform
        b12_raw = _read_tf_band(ds, 12)
        b19_raw = _read_tf_band(ds, 19)
        b2_raw = _read_tf_band(ds, 2)
        b13_raw = _read_tf_band(ds, 13)
        valid = foot & np.isfinite(b12_raw) & np.isfinite(b19_raw) & np.isfinite(b2_raw) & np.isfinite(b13_raw)

        # 0..2: Gravity tensor (B05, B11, B18)
        b5 = _clean_valid(_read_tf_band(ds, 5), valid)
        _store_col(X_foot, 0, mesoscale_zscore(b5, valid, sigma_px=28.0), foot, valid)
        del b5

        ghg = np.maximum(_clean_valid(_read_tf_band(ds, 18), valid), 0.0)
        gvg = _clean_valid(_read_tf_band(ds, 11), valid)
        grav_tilt = np.arctan2(gvg, np.sqrt(ghg * ghg + np.float32(1e-6))).astype(np.float32)
        del gvg
        gty, gtx = _grad_xy(grav_tilt, valid, sigma=1.6)
        del grav_tilt
        grav_edge_mag = np.hypot(gty, gtx).astype(np.float32)
        grav_strike = ((np.degrees(np.arctan2(gty, gtx)) + 90.0) % 180.0).astype(np.float32)
        del gty, gtx
        f01 = _sat(grav_edge_mag, 0.14)
        _store_col(X_foot, 1, f01, foot, valid)
        L_sub += np.float32(0.30) * f01
        del f01

        f02 = _sat(hessian_ridge_strength(ghg, valid, sigma=2.5), 0.08)
        _store_col(X_foot, 2, f02, foot, valid)
        L_sub += np.float32(0.18) * f02
        del ghg, f02

        # 3..4: Depth to basement (B15) + cover weight
        dbase = np.maximum(_clean_valid(_read_tf_band(ds, 15), valid), 0.0)
        log_dbase = np.log1p(dbase).astype(np.float32)
        del dbase
        by, bx = _grad_xy(log_dbase, valid, sigma=1.8)
        base_grad = np.hypot(by, bx).astype(np.float32)
        base_strike = ((np.degrees(np.arctan2(by, bx)) + 90.0) % 180.0).astype(np.float32)
        f03 = _sat(base_grad, 0.07)
        _store_col(X_foot, 3, f03, foot, valid)
        L_sub += np.float32(0.24) * f03
        del f03

        f04 = _sat(hessian_ridge_strength(log_dbase, valid, sigma=3.0), 0.05)
        _store_col(X_foot, 4, f04, foot, valid)
        del f04
        w_cover = np.clip(log_dbase / np.float32(np.log1p(500.0)), 0.22, 0.72).astype(np.float32)
        w_cover[~valid] = 0.22
        del log_dbase
        gc.collect()

        # 5..7: Magnetic RTP/TC/TMI/TMI_up150/TMI_VG
        tc_mag = _clean_valid(_read_tf_band(ds, 6), valid)
        mty, mtx = _grad_xy(tc_mag, valid, sigma=1.4)
        del tc_mag
        mag_edge_mag = np.hypot(mty, mtx).astype(np.float32)
        del mty, mtx
        _store_col(X_foot, 5, _sat(mag_edge_mag, 0.18), foot, valid)

        with rasterio.open(geodawn_ext_tif) as ds_ext:
            tmi_up_u8 = ds_ext.read(4)
        tmi_up = np.where(tmi_up_u8 > 0, (tmi_up_u8.astype(np.float32) - 1.0) / 254.0, np.nan)
        tmi_up_clean = _clean_valid(tmi_up, valid & (tmi_up_u8 > 0))
        del tmi_up_u8, tmi_up
        z_tmi = mesoscale_zscore(_clean_valid(_read_tf_band(ds, 14), valid), valid, sigma_px=24.0)
        z_up = mesoscale_zscore(tmi_up_clean, valid, sigma_px=24.0)
        del tmi_up_clean
        z_rtp = mesoscale_zscore(_clean_valid(b2_raw, valid), valid, sigma_px=24.0)
        del b2_raw
        f06 = np.clip(0.6 * (z_up - z_rtp) + 0.4 * np.abs(z_tmi - z_up), -4.0, 5.0).astype(np.float32)
        _store_col(X_foot, 6, f06, foot, valid)
        del z_tmi, z_up, z_rtp, f06

        tmi_vg_abs = np.abs(_clean_valid(_read_tf_band(ds, 9), valid)).astype(np.float32)
        f07 = _sat(hessian_ridge_strength(np.log1p(tmi_vg_abs), valid, sigma=2.0), 0.12)
        del tmi_vg_abs
        _store_col(X_foot, 7, f07, foot, valid)
        L_sub += np.float32(0.16) * f07
        del f07

        # 8: MT smectite clay-cap lateral margin (B17)
        log_mt = np.log(np.maximum(_clean_valid(_read_tf_band(ds, 17), valid), 1e-4)).astype(np.float32)
        cy_mt, cx_mt = _grad_xy(log_mt, valid, sigma=2.0)
        del log_mt
        f08 = _sat(np.hypot(cy_mt, cx_mt), 0.12)
        del cy_mt, cx_mt
        _store_col(X_foot, 8, f08, foot, valid)
        L_sub += np.float32(0.12) * f08
        del f08

        # 9..10: Geodetic strain (B04, B07, B08) + Sibson microseismic criticality (B10, B16)
        s_2nd = mesoscale_zscore(_clean_valid(_read_tf_band(ds, 4), valid), valid, sigma_px=32.0)
        s_shr = mesoscale_zscore(_clean_valid(_read_tf_band(ds, 7), valid), valid, sigma_px=32.0)
        s_dil = mesoscale_zscore(_clean_valid(_read_tf_band(ds, 8), valid), valid, sigma_px=32.0)
        _store_col(
            X_foot, 9,
            np.clip(0.5 * s_2nd + 0.3 * s_shr + 0.2 * np.maximum(s_dil, -1.0), -4.0, 5.0),
            foot, valid,
        )
        del s_2nd, s_shr, s_dil

        deq = np.maximum(_clean_valid(_read_tf_band(ds, 10), valid), 0.0)
        ieq = np.maximum(_clean_valid(_read_tf_band(ds, 16), valid), 0.0)
        seis = (np.log1p(ieq) / (1.0 + deq / np.float32(25.0))).astype(np.float32)
        del deq, ieq
        _store_col(X_foot, 10, mesoscale_zscore(seis, valid, sigma_px=36.0), foot, valid)
        del seis
        gc.collect()

    # 11..12: GeoDAWN K/Th and U/Th alteration enrichment
    with rasterio.open(geodawn_rad_tif) as ds_rad:
        rk = ds_rad.read(1).astype(np.float32)
        rth = ds_rad.read(2).astype(np.float32)
        ru = ds_rad.read(3).astype(np.float32)
    rad_ok = valid & (rk > 0) & (rth > 0) & (ru > 0)
    k_th = np.where(rad_ok, rk / np.maximum(rth, 1.0), 1.0).astype(np.float32)
    u_th = np.where(rad_ok, ru / np.maximum(rth, 1.0), 1.0).astype(np.float32)
    del rk, rth, ru, rad_ok
    _store_col(X_foot, 11, mesoscale_zscore(_clean_valid(k_th, valid), valid, sigma_px=26.0), foot, valid)
    del k_th
    _store_col(X_foot, 12, mesoscale_zscore(_clean_valid(u_th, valid), valid, sigma_px=26.0), foot, valid)
    del u_th
    gc.collect()

    # 13..14: Tufa-filtered INGENIOUS paleo-vents + 2m thermal probes + springs (decimated FFT, <150 MiB)
    paleo_src, vent_paleo_stats = _rasterize_paleo_vents(paleo_zip, ref_transform, shape, foot)
    p_plume = anisotropic_strike_plume(paleo_src, valid, sigma_parallel_px=18.0, sigma_perp_px=6.0, strike_deg_east_of_north=18.0)
    del paleo_src
    _store_col(X_foot, 13, _sat(np.log1p(p_plume * np.float32(30.0)), 0.45), foot, valid)
    del p_plume
    gc.collect()

    probe_src, vent_probe_stats = _rasterize_2m_temperature_probes(probe_2m_zip, ref_transform, shape, foot)
    pr_plume = anisotropic_strike_plume(probe_src, valid, sigma_parallel_px=16.0, sigma_perp_px=6.0, strike_deg_east_of_north=18.0)
    del probe_src
    spring_src, vent_spring_stats = _rasterize_active_thermal_springs(wellspring_csv, shape, foot)
    sp_plume = anisotropic_strike_plume(spring_src, valid, sigma_parallel_px=18.0, sigma_perp_px=6.0, strike_deg_east_of_north=18.0)
    del spring_src
    gdr_blind = gdr_blind_thermal_features(wellspring_csv, shape, valid, sigma_px=14.0)["plume_feat"]
    _store_col(X_foot, 14, _sat(np.log1p((pr_plume + sp_plume) * np.float32(25.0)) + np.float32(0.5) * gdr_blind, 0.55), foot, valid)
    del pr_plume, sp_plume, gdr_blind
    gc.collect()

    # 15..25: USGS 3DEP 10 m scarp excess, 10 m Chi knickpoints, multi-scale Hessian, concordance & Lahontan null
    det_elev = _clean_valid(b12_raw, valid)
    slope100 = np.maximum(_clean_valid(b19_raw, valid), 0.0)
    del b12_raw, b19_raw

    with rasterio.open(topo_10m_tif) as ds_t10:
        s_p90 = _decode_u8_band(ds_t10, 1)
        s_max = _decode_u8_band(ds_t10, 2)
        f15 = subpixel_scarp_excess(s_max, slope100, valid)
        f16 = subpixel_scarp_excess(s_p90, slope100, valid)
        del s_p90, s_max
        _store_col(X_foot, 15, f15, foot, valid)
        _store_col(X_foot, 16, f16, foot, valid)
        L_geo += np.float32(0.34) * f15
        del f15, f16

        pied_w = (1.0 / (1.0 + (slope100 / np.float32(9.0)) ** 2)).astype(np.float32)
        f17 = _sat(_clean_valid(_decode_u8_band(ds_t10, 6), valid) * pied_w, 6.0)
        del pied_w
        _store_col(X_foot, 17, f17, foot, valid)
        L_geo += np.float32(0.20) * f17
        del f17

        coh10 = (_clean_valid(_decode_u8_band(ds_t10, 7), valid) * _clean_valid(_decode_u8_band(ds_t10, 8), valid)).astype(np.float32)
        f18 = _sat(coh10, 0.22)
        del coh10
        _store_col(X_foot, 18, f18, foot, valid)
        L_geo += np.float32(0.16) * f18
        del f18

        dem_m = _clean_valid(_decode_u8_band(ds_t10, 9), valid)
    del slope100

    with rasterio.open(dem10_chi_tif) as ds_chi:
        chi_step = np.maximum(ds_chi.read(1).astype(np.float32) / 1000.0, 0.0)
        chi_ksn = np.maximum(ds_chi.read(3).astype(np.float32), 0.0)
    f19 = _sat(np.log1p(_clean_valid(chi_step, valid) * np.float32(4.0)), 0.85)
    f20 = _sat(np.log1p(_clean_valid(chi_ksn, valid) * np.float32(0.08)), 1.40)
    del chi_step, chi_ksn
    _store_col(X_foot, 19, f19, foot, valid)
    _store_col(X_foot, 20, f20, foot, valid)
    L_geo += np.float32(0.12) * f19
    del f19, f20

    f21 = _sat(hessian_ridge_strength(det_elev, valid, sigma=1.2), 1.4)
    f22 = _sat(hessian_ridge_strength(det_elev, valid, sigma=3.0), 2.2)
    _store_col(X_foot, 21, f21, foot, valid)
    _store_col(X_foot, 22, f22, foot, valid)
    L_geo += np.float32(0.18) * (np.float32(0.55) * f21 + np.float32(0.45) * f22)
    del f21, f22

    coh_el, topo_strike = coherence_and_strike_deg(det_elev, valid, deriv_sigma=1.2, tensor_sigma=3.5)
    _store_col(X_foot, 23, cross_strike_monotonicity(det_elev, valid, half_span_px=3), foot, valid)

    ey, ex = _grad_xy(det_elev, valid, sigma=1.6)
    del det_elev
    enorm = np.maximum(np.hypot(ey, ex), 1e-5)
    gy13, gx13 = _grad_xy(_clean_valid(b13_raw, valid), valid, sigma=2.0)
    del b13_raw
    gnorm13 = np.maximum(np.hypot(gy13, gx13), 1e-5)
    bnorm = np.maximum(base_grad, 1e-5)
    concord_eb = ((-ey * by - ex * bx) / (enorm * bnorm)).astype(np.float32)
    concord_eg = ((ey * gy13 + ex * gx13) / (enorm * gnorm13)).astype(np.float32)
    del ey, ex, enorm, by, bx, gy13, gx13, gnorm13, bnorm
    _store_col(X_foot, 24, np.clip(0.55 * concord_eb + 0.45 * concord_eg, -1.0, 1.0), foot, valid)
    del concord_eb, concord_eg

    lahontan_band = np.exp(-0.5 * ((dem_m - np.float32(1330.0)) / np.float32(45.0)) ** 2).astype(np.float32)
    _store_col(X_foot, 25, lahontan_band * (1.0 - np.minimum(base_grad / np.float32(0.08), 1.0)), foot, valid)
    del dem_m, lahontan_band

    w_topo_st = np.where(valid, coh_el * (1.0 - 0.65 * w_cover), 0.0).astype(np.float32)
    w_sub_st = np.where(valid, _sat(grav_edge_mag, 0.12) + _sat(base_grad, 0.06) + 0.5 * _sat(mag_edge_mag, 0.18), 0.0).astype(np.float32)
    c2 = w_topo_st * np.cos(np.radians(2.0 * topo_strike)) + w_sub_st * np.cos(np.radians(2.0 * 0.5 * (grav_strike + base_strike)))
    s2 = w_topo_st * np.sin(np.radians(2.0 * topo_strike)) + w_sub_st * np.sin(np.radians(2.0 * 0.5 * (grav_strike + base_strike)))
    edge_strike_deg = ((0.5 * np.degrees(np.arctan2(s2, c2))) % 180.0).astype(np.float32)
    del w_topo_st, w_sub_st, c2, s2, coh_el, topo_strike, grav_strike, base_strike, grav_edge_mag, base_grad, mag_edge_mag

    L_geo[~valid] = 0.0
    L_sub[~valid] = 0.0
    gc.collect()

    return {
        "X_foot": X_foot,
        "valid": valid,
        "w_cover": w_cover,
        "edge_strike_deg": edge_strike_deg,
        "L_geo": L_geo,
        "L_sub": L_sub,
        "vent_stats": {
            "paleo_vents": vent_paleo_stats,
            "probes_2m": vent_probe_stats,
            "thermal_springs": vent_spring_stats,
        },
    }


def _fit_hgb_subset(
    X_foot: np.ndarray,
    col_idx: tuple[int, ...],
    pos_foot: np.ndarray,
    neg_pool_foot: np.ndarray,
    seed: int,
    max_iter: int = 150,
    neg_ratio: int = 4,
) -> HistGradientBoostingClassifier:
    pos_idx = np.flatnonzero(pos_foot)
    neg_pool_idx = np.flatnonzero(neg_pool_foot)
    rng = np.random.default_rng(seed)
    n_neg = min(int(neg_pool_idx.size), max(int(pos_idx.size) * neg_ratio, 20_000))
    neg_idx = rng.choice(neg_pool_idx, size=n_neg, replace=False)

    tr_idx = np.concatenate([pos_idx, neg_idx])
    y_tr = np.concatenate([
        np.ones(pos_idx.size, dtype=np.int8),
        np.zeros(neg_idx.size, dtype=np.int8),
    ])
    X_tr = X_foot[tr_idx][:, list(col_idx)]
    pos_weight = float(neg_idx.size) / float(max(pos_idx.size, 1))
    sample_w = np.where(y_tr == 1, pos_weight, 1.0).astype(np.float32)

    clf = HistGradientBoostingClassifier(
        loss="log_loss",
        max_iter=max_iter,
        learning_rate=0.055,
        max_leaf_nodes=31,
        max_depth=6,
        min_samples_leaf=80,
        l2_regularization=5.0,
        early_stopping=False,
        random_state=seed,
    )
    clf.fit(X_tr, y_tr, sample_weight=sample_w)
    return clf


def _predict_chunked(clf: HistGradientBoostingClassifier, X_foot: np.ndarray, col_idx: tuple[int, ...], mask_foot: np.ndarray) -> np.ndarray:
    idx = np.flatnonzero(mask_foot)
    out = np.zeros(idx.size, dtype=np.float32)
    cols = list(col_idx)
    step = 350_000
    for i0 in range(0, idx.size, step):
        sub = idx[i0:i0 + step]
        out[i0:i0 + step] = clf.predict_proba(X_foot[sub][:, cols])[:, 1].astype(np.float32)
    return out


def fit_pairwise_stage1_oof(
    X_foot: np.ndarray,
    labels_positive: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    *,
    exclude_mask: np.ndarray | None = None,
    guard_px: int = 12,
    neg_buffer_px: float = 5.0,
    seed: int = 20261025,
) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    """Fit 6 pairwise 2-quadrant Stage-1 models for M1_blind and M1_phys (strict isolation)."""
    foot = np.asarray(footprint, dtype=bool)
    val = np.asarray(valid, dtype=bool) & foot
    pos = np.asarray(labels_positive, dtype=bool) & val
    excl = np.zeros_like(foot) if exclude_mask is None else np.asarray(exclude_mask, dtype=bool)

    d_pos = distance_transform_edt(~pos)
    neg_ok_grid = val & (~pos) & (d_pos > float(neg_buffer_px)) & (~excl)
    del d_pos
    pos_ok_grid = pos & (~excl)

    q_interior_foot: dict[int, np.ndarray] = {}
    q_exact_foot: dict[int, np.ndarray] = {}
    for q in range(4):
        outside_q = foot & (quad != q)
        eroded_q = (quad == q) & (~binary_dilation(outside_q, iterations=int(guard_px)))
        q_interior_foot[q] = eroded_q[foot]
        q_exact_foot[q] = (val & (quad == q))[foot]

    pos_foot = pos_ok_grid[foot]
    neg_foot = neg_ok_grid[foot]
    val_foot = val[foot]
    del pos_ok_grid, neg_ok_grid

    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    pred_blind_pair: dict[tuple[int, int], dict[int, np.ndarray]] = {}
    pred_phys_pair: dict[tuple[int, int], dict[int, np.ndarray]] = {}

    for p_idx, (qa, qb) in enumerate(pairs):
        tr_region = q_interior_foot[qa] | q_interior_foot[qb]
        clf_b = _fit_hgb_subset(
            X_foot, STAGE1_BLIND_COLS,
            pos_foot & tr_region, neg_foot & tr_region,
            seed=seed + 101 * p_idx, max_iter=120,
        )
        clf_p = _fit_hgb_subset(
            X_foot, STAGE1_PHYS_COLS,
            pos_foot & tr_region, neg_foot & tr_region,
            seed=seed + 211 * p_idx + 7, max_iter=120,
        )
        pb_q: dict[int, np.ndarray] = {}
        pp_q: dict[int, np.ndarray] = {}
        for qt in range(4):
            if qt in (qa, qb):
                continue
            pb_q[qt] = _predict_chunked(clf_b, X_foot, STAGE1_BLIND_COLS, q_exact_foot[qt])
            pp_q[qt] = _predict_chunked(clf_p, X_foot, STAGE1_PHYS_COLS, q_exact_foot[qt])
        pred_blind_pair[(qa, qb)] = pb_q
        pred_phys_pair[(qa, qb)] = pp_q
        del clf_b, clf_p

    out: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for q_star in range(4):
        pb_foot = np.zeros(X_foot.shape[0], dtype=np.float32)
        pp_foot = np.zeros(X_foot.shape[0], dtype=np.float32)
        train_qs = [q for q in range(4) if q != q_star]
        for q_tr in train_qs:
            pair = tuple(sorted(q for q in train_qs if q != q_tr))
            idx_q = np.flatnonzero(q_exact_foot[q_tr])
            pb_foot[idx_q] = pred_blind_pair[pair][q_tr]  # type: ignore[index]
            pp_foot[idx_q] = pred_phys_pair[pair][q_tr]  # type: ignore[index]
        sub_pairs = [
            tuple(sorted((train_qs[0], train_qs[1]))),
            tuple(sorted((train_qs[0], train_qs[2]))),
            tuple(sorted((train_qs[1], train_qs[2]))),
        ]
        idx_star = np.flatnonzero(q_exact_foot[q_star])
        pb_foot[idx_star] = np.mean([pred_blind_pair[sp][q_star] for sp in sub_pairs], axis=0).astype(np.float32)  # type: ignore[index]
        pp_foot[idx_star] = np.mean([pred_phys_pair[sp][q_star] for sp in sub_pairs], axis=0).astype(np.float32)  # type: ignore[index]

        pb_grid = np.zeros(foot.shape, dtype=np.float32)
        pp_grid = np.zeros(foot.shape, dtype=np.float32)
        pb_grid[foot] = np.where(val_foot, pb_foot, 0.0)
        pp_grid[foot] = np.where(val_foot, pp_foot, 0.0)
        out[q_star] = (pb_grid, pp_grid)
    return out


def fit_stage2_bimodal_loqo(
    X_foot: np.ndarray,
    stage1_by_qstar: dict[int, tuple[np.ndarray, np.ndarray]],
    labels_positive: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    w_cover: np.ndarray,
    *,
    use_relay_cols: bool = True,
    target_quadrants: tuple[int, ...] = (0, 1, 2, 3),
    exclude_mask: np.ndarray | None = None,
    guard_px: int = 12,
    neg_buffer_px: float = 5.0,
    seed: int = 20261025,
) -> dict[str, np.ndarray]:
    """Cross-fit Stage-2 Topography-Blind and Full models with strictly isolated OOF auto-context."""
    foot = np.asarray(footprint, dtype=bool)
    val = np.asarray(valid, dtype=bool) & foot
    pos = np.asarray(labels_positive, dtype=bool) & val
    excl = np.zeros_like(foot) if exclude_mask is None else np.asarray(exclude_mask, dtype=bool)

    d_pos = distance_transform_edt(~pos)
    neg_ok_grid = val & (~pos) & (d_pos > float(neg_buffer_px)) & (~excl)
    del d_pos
    pos_ok_grid = pos & (~excl)
    pos_foot = pos_ok_grid[foot]
    neg_foot = neg_ok_grid[foot]
    del pos_ok_grid, neg_ok_grid

    cols_blind = STAGE2_BLIND_RELAY_COLS if use_relay_cols else STAGE2_BLIND_NOTIP_COLS
    cols_full = STAGE2_FULL_RELAY_COLS if use_relay_cols else STAGE2_FULL_NOTIP_COLS

    p_blind_out = np.zeros(foot.shape, dtype=np.float32)
    p_full_out = np.zeros(foot.shape, dtype=np.float32)

    for q_star in target_quadrants:
        pb1, pp1 = stage1_by_qstar[q_star]
        ac = steerable_oof_autocontext(pb1, pp1, val)
        X_foot[:, 26] = ac["oof_blind_line_short"][foot]
        X_foot[:, 27] = ac["oof_blind_line_long"][foot]
        X_foot[:, 28] = ac["oof_phys_line_short"][foot]
        X_foot[:, 29] = ac["oof_phys_bridge_axial"][foot]
        del ac

        test_q = foot & (quad == q_star)
        train_reg = foot & (quad != q_star) & (~binary_dilation(test_q, iterations=int(guard_px)))
        tr_foot = train_reg[foot]
        te_grid = val & (quad == q_star)
        te_foot = te_grid[foot]

        clf_b2 = _fit_hgb_subset(
            X_foot, cols_blind, pos_foot & tr_foot, neg_foot & tr_foot,
            seed=seed + 307 * q_star + 13, max_iter=165,
        )
        clf_f2 = _fit_hgb_subset(
            X_foot, cols_full, pos_foot & tr_foot, neg_foot & tr_foot,
            seed=seed + 409 * q_star + 29, max_iter=165,
        )
        p_blind_out[te_grid] = _predict_chunked(clf_b2, X_foot, cols_blind, te_foot)
        p_full_out[te_grid] = _predict_chunked(clf_f2, X_foot, cols_full, te_foot)
        del clf_b2, clf_f2

    if len(target_quadrants) == 4:
        p_blind_cal = calibrate_quadrant_probabilities(p_blind_out, val, quad, calib_weight=0.25, power_gamma=1.8)
        p_full_cal = calibrate_quadrant_probabilities(p_full_out, val, quad, calib_weight=0.25, power_gamma=1.8)
    else:
        p_blind_cal = p_blind_out
        p_full_cal = p_full_out

    wc = np.asarray(w_cover, dtype=np.float32)
    p_bimodal = ((1.0 - wc) * p_full_cal + wc * p_blind_cal).astype(np.float32)
    p_bimodal[~val] = 0.0
    return {
        "p_blind": p_blind_cal,
        "p_full": p_full_cal,
        "p_bimodal": p_bimodal,
    }


def build_dual_conduit_surface(
    proba: np.ndarray,
    L_geo: np.ndarray,
    L_sub: np.ndarray,
    w_cover: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Build cover-adaptive Dual Geomorphic U Subsurface Geophysical crest surface & 1D gate."""
    v = np.asarray(valid, dtype=bool)
    p = np.where(v, np.asarray(proba, dtype=np.float32), 0.0)
    lg = np.where(v, np.asarray(L_geo, dtype=np.float32), 0.0)
    ls = np.where(v, np.asarray(L_sub, dtype=np.float32), 0.0)
    wc = np.where(v, np.asarray(w_cover, dtype=np.float32), 0.22)

    L_dual = ((1.0 - 0.65 * wc) * lg + (0.45 + 0.65 * wc) * ls).astype(np.float32)
    S_dual = (p * (0.30 + 0.70 * L_dual)).astype(np.float32)
    S_dual[~v] = 0.0

    ridge_dual = directional_ridge_1d(S_dual, v)
    ridge_sub = directional_ridge_1d(p * (0.25 + 0.75 * ls), v) & (wc >= 0.40)
    ridge_union = (ridge_dual | ridge_sub) & v
    return {
        "S_crest": S_dual,
        "ridge_1d": ridge_union,
        "L_dual": L_dual,
    }
