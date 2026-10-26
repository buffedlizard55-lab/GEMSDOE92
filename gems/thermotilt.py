"""THERMOTILT lane: Upgradient Piezometric Thermal-Plume Back-Projection,
Exact 2D-FFT Harmonic 1VD Signed-Tilt Contact Crests (HD_TDR), Antithetic
Accommodation-Zone Dip-Reversal Twist, and Inner-Annulus-Suppressed Distal
En-Echelon Accommodation Bridges.

Pre-registered BEFORE implementation in ``docs/HYPOTHESES_20261026_THERMOTILT.md``.

Physical mechanisms implemented:
1. Exact 2D-FFT Harmonic First Vertical Derivative (1VD) & Verduzco-Salem (2004,
   2007) Amplitude-Invariant Signed Tilt Horizontal Derivative (HD_TDR) on both
   Band 2 Reduced-to-Pole Magnetics and Band 13 Isostatic Gravity:
       F{d_z U}(k) = |k| * exp(-|k| * z0) * F{U}(k)
       theta_U(x)  = arctan2(d_z U, ||grad_h U|| + eps) in (-pi/2, +pi/2)
       HD_TDR_U(x) = ||grad_h theta_U(x)||
   Unlike ``gems/tiltangle.py`` (which took ``abs(Band 11)`` on gravity only and
   destroyed the sign of d_z), ``harmonic_1vd_signed_tilt`` preserves the exact
   Laplace half-space sign across steep fault contacts and extracts amplitude-
   invariant contact crests over deeply buried (Band 15 > 400 m) basin faults.
2. Upgradient Piezometric Thermal-Plume Back-Projection (Coolbaugh et al., 2006;
   Ferguson et al., 2009): buoyant hydrothermal fluids ascend blind piedmont or
   intrabasin faults and migrate laterally downgradient through alluvial-fan
   aquifers before emerging at warm springs or warming shallow 2 m probes. We
   advect tufa-excluded sinter vents, 2 m temperature probes, and >=35 C GDR
   springs UPSLOPE along the regional hydraulic-head unit vector +u_up(x) by
   l in {5, 11, 18} px (0.5, 1.1, 1.8 km) and contrast against downslope outflow.
3. Antithetic Accommodation-Zone Polarity-Reversal Tensor (Faulds & Varga, 1998;
   Faulds & Hinz, 2015): measures cross-strike head-on convergence and horst
   divergence of unit horizontal gravity gradient vectors u_g(x +/- L n_perp)
   across L in {6, 12} px, targeting synthetic-antithetic graben transfer zones
   and buried intrabasin horsts where opposing dips cancel regional relief.
4. Inner-Annulus-Suppressed Distal En-Echelon Accommodation Bridge (Exp 2 & Exp 3
   only; strictly fold-visible ``fold.visible`` and self-component-excluded):
   suppresses the crowded r <= 9.0 px near-tip halo via smooth annular window
   W_ann(r) = clip((r - 9.0) / 6.0, 0, 1) * exp(-(r - 9.0) / 24.0) for
   9 < r <= 46 px along conjugate +/-16 deg en-echelon azimuths and opposing-tip
   bridges, paired with a dual-regime capacity quota (<= 39.8% distal bridge,
   >= 60.2% off-corridor blind THERMOTILT discoveries at strict d > 2.0 px).

Memory budget: streams channels into float32 ``X_foot`` (< 1.3 GiB peak RSS
inside 3.8 GiB / 0-swap workspace).
"""
from __future__ import annotations

import gc
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.fft import irfft2, next_fast_len, rfft2, rfftfreq, fftfreq
from scipy.ndimage import distance_transform_edt, gaussian_filter
from sklearn.linear_model import LogisticRegression

from .breakline import spaced_top_mask
from .chilistric import compute_adaptive_dip_offset_px, compute_second_best_corroboration
from .coulomb_loqo import (
    _grad_xy,
    _sat,
    directional_ridge_1d,
    gdr_blind_thermal_features,
    hessian_ridge_strength,
)
from .faultnet import STRUCT8, endpoints, gaussian_density, own_gaussian_sum
from .hydroconduit import _clean_valid, coherence_and_strike_deg, cross_strike_monotonicity
from .knick_loqo import calibrate_quadrant_probabilities, mesoscale_zscore
from .listric_loqo import bilinear_sample_2d
from .relayconduit import steerable_oof_autocontext
from .ventscarp import (
    _decode_u8_band,
    _rasterize_2m_temperature_probes,
    _rasterize_active_thermal_springs,
    _rasterize_paleo_vents,
    anisotropic_strike_plume,
    subpixel_scarp_excess,
)

FEATURE_NAMES: tuple[str, ...] = (
    # Group H: Harmonic 2D-FFT 1VD Signed-Tilt, AZ-Twist & Upgradient Thermal Physics (0..18; ZERO topo/cat)
    "tt_mag_1vd_zero_contact",      # 0
    "tt_mag_hd_tdr_crest",          # 1
    "tt_grav_1vd_zero_contact",     # 2
    "tt_grav_hd_tdr_crest",         # 3
    "tt_mag_grav_tilt_phaselock",   # 4
    "tt_az_graben_convergence",     # 5
    "tt_az_horst_divergence",       # 6
    "tt_upflow_piezo_backproj",     # 7
    "tt_upflow_conduit_lock",       # 8
    "tt_paleo_sinter_upflow",       # 9
    "tt_grauch_demag_valve",        # 10
    "tt_mt_depth_deconf_edge",      # 11
    "tt_base_step_grad",            # 12
    "tt_base_flex_curv",            # 13
    "tt_adapt_listric_ramp",        # 14
    "tt_strain_transtension",       # 15
    "tt_seismic_criticality",       # 16
    "tt_rad_k_th_alteration",       # 17
    "tt_rad_redox_dipole",          # 18
    # Group G: USGS 3DEP 10 m Sub-Pixel Scarp, Chi-Steps & Lahontan Deconfounder (19..27; ZERO cat)
    "tt_scarp10m_excess_max",       # 19
    "tt_scarp10m_curv_pied",        # 20
    "tt_scarp10m_coherence",        # 21
    "tt_chi10m_knick_step",         # 22
    "tt_chi10m_ksn",                # 23
    "tt_elev_hess_multi",           # 24
    "tt_elev_step_mono",            # 25
    "tt_dip_concord_grav_base",     # 26
    "tt_lahontan_mimic_null",       # 27
    "tt_multiline_corrob_sec",      # 28
    # Group A: Stage-1 OOF Multi-Azimuth Structural Auto-Context (29..32; ZERO cat in surface)
    "tt_oof_blind_line_short",      # 29
    "tt_oof_blind_line_long",       # 30
    "tt_oof_phys_line_short",       # 31
    "tt_oof_phys_bridge_axial",     # 32
    # Group D: Inner-Annulus-Suppressed Distal Accommodation Bridges (33..36; fold.visible ONLY)
    "tt_da_enechelon_annulus",      # 33
    "tt_da_axial_far_annulus",      # 34
    "tt_da_stepover_bridge",        # 35
    "tt_da_strike_concord",         # 36
)

STAGE1_SUB_COLS: tuple[int, ...] = tuple(range(0, 19))
STAGE1_FULL_COLS: tuple[int, ...] = tuple(range(0, 29))
OOF_CTX_COLS: tuple[int, ...] = (29, 30, 31, 32)
DISTAL_COLS: tuple[int, ...] = (33, 34, 35, 36)

BLIND_SUB_STAGE2_COLS: tuple[int, ...] = STAGE1_SUB_COLS + (29, 30)
BLIND_FULL_STAGE2_COLS: tuple[int, ...] = STAGE1_FULL_COLS + OOF_CTX_COLS
DISTAL_SUB_STAGE2_COLS: tuple[int, ...] = STAGE1_SUB_COLS + (29, 30) + DISTAL_COLS
DISTAL_FULL_STAGE2_COLS: tuple[int, ...] = STAGE1_FULL_COLS + OOF_CTX_COLS + DISTAL_COLS

INNER_SUPPRESS_R_PX: float = 9.0
DISTAL_RAMP_PX: float = 6.0
DISTAL_MAX_R_PX: int = 46

__all__ = [
    "FEATURE_NAMES",
    "STAGE1_SUB_COLS",
    "STAGE1_FULL_COLS",
    "OOF_CTX_COLS",
    "DISTAL_COLS",
    "BLIND_SUB_STAGE2_COLS",
    "BLIND_FULL_STAGE2_COLS",
    "DISTAL_SUB_STAGE2_COLS",
    "DISTAL_FULL_STAGE2_COLS",
    "harmonic_1vd_signed_tilt",
    "upgradient_piezometric_backprojection",
    "antithetic_accommodation_twist",
    "distal_annular_accommodation_fields",
    "compute_thermotilt_physics_stack",
    "fit_stage1_oof_loqo",
    "fit_stage2_thermotilt_loqo",
    "allocate_dual_regime_crests",
    "build_graded_tail_allocation",
]


def _read_tf_band(ds: rasterio.DatasetReader, idx: int) -> np.ndarray:
    arr = ds.read(int(idx)).astype(np.float32)
    arr[(~np.isfinite(arr)) | (arr <= -1e20)] = np.nan
    return arr


def _store_col(
    X_foot: np.ndarray,
    col: int,
    arr: np.ndarray,
    foot: np.ndarray,
    valid: np.ndarray,
) -> None:
    clean = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
    clean[~valid] = 0.0
    X_foot[:, col] = clean[foot]


def harmonic_1vd_signed_tilt(
    field: np.ndarray,
    valid: np.ndarray,
    *,
    z0_px: float = 1.5,
    pad_px: int = 32,
) -> dict[str, np.ndarray]:
    """Compute exact 2D-FFT Laplace half-space 1VD, signed Miller-Singh tilt,
    zero-crossing contact score, and Verduzco-Salem amplitude-invariant HD_TDR.

    In wavenumber space k = 2*pi*(fx, fy):
        F{d_z U}(k) = |k| * exp(-|k| * z0_px) * F{U}(k)
    """
    v = np.asarray(valid, dtype=bool)
    h, w = v.shape
    if not v.any():
        z = np.zeros((h, w), dtype=np.float32)
        return {
            "vdr": z,
            "signed_tilt": z.copy(),
            "zero_contact": z.copy(),
            "hd_tdr": z.copy(),
            "strike_deg": z.copy(),
        }

    u_clean = _clean_valid(field, v).astype(np.float32)
    # Remove smooth regional DC/trend before mirror-padded FFT to avoid boundary steps
    u_reg = gaussian_filter(u_clean, sigma=48.0).astype(np.float32)
    u_det = (u_clean - u_reg).astype(np.float32)
    del u_reg

    u_pad = np.pad(u_det, ((pad_px, pad_px), (pad_px, pad_px)), mode="reflect")
    del u_det
    hp, wp = u_pad.shape
    fft_h = next_fast_len(hp)
    fft_w = next_fast_len(wp)
    if fft_h > hp or fft_w > wp:
        u_pad = np.pad(u_pad, ((0, fft_h - hp), (0, fft_w - wp)), mode="reflect")

    spec = rfft2(u_pad, workers=2)
    del u_pad
    ky = (2.0 * np.pi * fftfreq(fft_h, d=1.0)).astype(np.float32)[:, None]
    kx = (2.0 * np.pi * rfftfreq(fft_w, d=1.0)).astype(np.float32)[None, :]
    krad = np.hypot(ky, kx).astype(np.float32)
    del ky, kx
    filt = (krad * np.exp(-krad * np.float32(z0_px))).astype(np.float32)
    del krad
    spec *= filt
    del filt
    vdr_full = irfft2(spec, s=(fft_h, fft_w), workers=2)
    del spec
    vdr = np.asarray(vdr_full[pad_px : pad_px + h, pad_px : pad_px + w], dtype=np.float32)
    del vdr_full

    # Horizontal gradient at matched upward-continuation smoothing scale
    uy, ux = _grad_xy(u_clean, v, sigma=max(0.95 * float(z0_px), 1.0))
    del u_clean
    thdr = np.hypot(uy, ux).astype(np.float32)
    strike_deg = ((np.degrees(np.arctan2(uy, ux)) + 90.0) % 180.0).astype(np.float32)
    del uy, ux

    eps_scale = float(np.percentile(thdr[v], 15.0)) * 0.15 + 1e-5
    signed_tilt = np.arctan2(vdr, thdr + np.float32(eps_scale)).astype(np.float32)

    thdr_med = float(np.median(thdr[v])) + 1e-5
    thdr_sat = _sat(thdr, 1.55 * thdr_med)
    del thdr
    zero_contact = (np.exp(-((signed_tilt / np.float32(0.34)) ** 2)) * thdr_sat).astype(np.float32)
    del thdr_sat

    # Verduzco et al. (2004) / Salem et al. (2007) Total Horizontal Derivative of Signed Tilt
    ty, tx = _grad_xy(signed_tilt, v, sigma=1.25)
    hd_raw = np.hypot(ty, tx).astype(np.float32)
    del ty, tx
    hd_med = float(np.median(hd_raw[v])) + 1e-5
    # Emphasize HD_TDR near signed-tilt zero crossings (steep contact crests)
    hd_tdr = (_sat(hd_raw, 1.65 * hd_med) * (np.float32(0.35) + np.float32(0.65) * np.exp(-((signed_tilt / np.float32(0.55)) ** 2)))).astype(np.float32)
    del hd_raw

    for a in (vdr, signed_tilt, zero_contact, hd_tdr, strike_deg):
        a[~v] = 0.0
    return {
        "vdr": vdr,
        "signed_tilt": signed_tilt,
        "zero_contact": zero_contact,
        "hd_tdr": hd_tdr,
        "strike_deg": strike_deg,
    }


def upgradient_piezometric_backprojection(
    outflow_source: np.ndarray,
    uy_upslope: np.ndarray,
    ux_upslope: np.ndarray,
    valid: np.ndarray,
    *,
    shifts_px: tuple[float, ...] = (5.0, 11.0, 18.0),
    weights: tuple[float, ...] = (0.45, 0.35, 0.20),
    plume_sigma_px: float = 4.5,
) -> np.ndarray:
    """Back-project surface hydrothermal outflow anomalies upslope along +u_upslope.

    If a warm spring / 2m-probe anomaly sits at downgradient toe x_s, and the
    buried source fault sits upslope at x = x_s + ell * u_upslope(x), then
    evaluating ``plume(x - ell * u_upslope(x))`` peaks directly on the upslope
    blind fault at x, while subtracting ``0.45 * plume(x + ell * u_upslope(x))``
    suppresses downgradient playa outflow tails.
    """
    v = np.asarray(valid, dtype=bool)
    h, w = v.shape
    if not v.any():
        return np.zeros((h, w), dtype=np.float32)

    src = np.where(v, np.maximum(np.nan_to_num(outflow_source, nan=0.0), 0.0), 0.0).astype(np.float32)
    if float(src.max()) <= 0.0:
        return np.zeros((h, w), dtype=np.float32)

    plume = gaussian_filter(src, sigma=float(plume_sigma_px)).astype(np.float32)
    del src
    yy, xx = np.meshgrid(np.arange(h, dtype=np.float32), np.arange(w, dtype=np.float32), indexing="ij")
    uy = np.asarray(uy_upslope, dtype=np.float32)
    ux = np.asarray(ux_upslope, dtype=np.float32)

    acc = np.zeros((h, w), dtype=np.float32)
    for ell, wt in zip(shifts_px, weights):
        s_f = np.float32(ell)
        # Candidate x is upslope of spring -> spring is at x - ell * u_upslope
        up_hit = bilinear_sample_2d(plume, yy - s_f * uy, xx - s_f * ux, v)
        dn_null = bilinear_sample_2d(plume, yy + s_f * uy, xx + s_f * ux, v)
        diff = np.maximum(up_hit - np.float32(0.45) * dn_null, 0.0)
        acc += np.float32(wt) * diff
        del up_hit, dn_null, diff
    del plume, yy, xx

    p95 = float(np.percentile(acc[v], 95.0)) if v.any() else 0.0
    scale = max(p95 * 1.35, float(acc.max()) * 0.25, 1e-6)
    out = _sat(acc, scale)
    out[~v] = 0.0
    return out


def antithetic_accommodation_twist(
    grav_anom: np.ndarray,
    ny_perp: np.ndarray,
    nx_perp: np.ndarray,
    valid: np.ndarray,
    *,
    offsets_px: tuple[float, ...] = (6.0, 12.0),
) -> tuple[np.ndarray, np.ndarray]:
    """Detect antithetic graben convergence and intrabasin horst divergence
    via cross-strike polarity reversal of unit horizontal gravity gradients.

    In gravity, grad_h(g_iso) points from hanging-wall graben lows toward
    footwall horst highs.
    - Across a narrow graben / synthetic-antithetic accommodation zone, the
      gradient at x + L*n points toward +n while at x - L*n it points toward -n
      (opposing vectors: u_+ . u_- < 0 and (u_+ - u_-) . n > 0 -> divergence of
      gravity highs away from graben center = opposing fault dips converging!).
    - Across a buried intrabasin horst crest, u_+ . u_- < 0 with (u_+ - u_-) . n < 0
      (gradients point inward from both basins onto the horst block).
    """
    v = np.asarray(valid, dtype=bool)
    h, w = v.shape
    if not v.any():
        z = np.zeros((h, w), dtype=np.float32)
        return z, z.copy()

    gy, gx = _grad_xy(_clean_valid(grav_anom, v), v, sigma=2.0)
    gmag = np.hypot(gy, gx).astype(np.float32)
    gmed = float(np.median(gmag[v])) + 1e-5
    gsat = _sat(gmag, 1.45 * gmed)
    inv_g = 1.0 / np.maximum(gmag, np.float32(gmed * 0.15 + 1e-6))
    ugy = (gy * inv_g).astype(np.float32)
    ugx = (gx * inv_g).astype(np.float32)
    del gy, gx, gmag, inv_g

    yy, xx = np.meshgrid(np.arange(h, dtype=np.float32), np.arange(w, dtype=np.float32), indexing="ij")
    ny = np.asarray(ny_perp, dtype=np.float32)
    nx = np.asarray(nx_perp, dtype=np.float32)

    graben_conv = np.zeros((h, w), dtype=np.float32)
    horst_div = np.zeros((h, w), dtype=np.float32)
    w_norm = 1.0 / float(max(len(offsets_px), 1))

    for L in offsets_px:
        Lf = np.float32(L)
        yp, xp = yy + Lf * ny, xx + Lf * nx
        ym, xm = yy - Lf * ny, xx - Lf * nx

        uy_p = bilinear_sample_2d(ugy, yp, xp, v)
        ux_p = bilinear_sample_2d(ugx, yp, xp, v)
        uy_m = bilinear_sample_2d(ugy, ym, xm, v)
        ux_m = bilinear_sample_2d(ugx, ym, xm, v)
        amp_p = bilinear_sample_2d(gsat, yp, xp, v)
        amp_m = bilinear_sample_2d(gsat, ym, xm, v)
        del yp, xp, ym, xm

        # Opposing polarity strength in [0, 1]
        anti = np.maximum(-(uy_p * uy_m + ux_p * ux_m), 0.0)
        geom_amp = np.sqrt(np.maximum(amp_p * amp_m, 0.0))
        # Signed normal flux: >0 over graben trough (opposing faults dip inward), <0 over horst crest
        n_flux = (uy_p - uy_m) * ny + (ux_p - ux_m) * nx
        del uy_p, ux_p, uy_m, ux_m, amp_p, amp_m

        graben_conv += np.float32(w_norm) * anti * np.clip(0.5 * np.maximum(n_flux, 0.0), 0.0, 1.0) * geom_amp
        horst_div += np.float32(w_norm) * anti * np.clip(0.5 * np.maximum(-n_flux, 0.0), 0.0, 1.0) * geom_amp
        del anti, geom_amp, n_flux

    del ugy, ugx, gsat, yy, xx
    graben_conv = np.where(v, _sat(graben_conv, max(float(np.percentile(graben_conv[v], 96.0)) * 1.25, 0.05)), 0.0).astype(np.float32)
    horst_div = np.where(v, _sat(horst_div, max(float(np.percentile(horst_div[v], 96.0)) * 1.25, 0.05)), 0.0).astype(np.float32)
    return graben_conv, horst_div


def _tip_records(
    mask: np.ndarray,
    labels: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
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


def distal_annular_accommodation_fields(
    catalogue_visible: np.ndarray,
    edge_strike_deg: np.ndarray,
    valid: np.ndarray,
    *,
    inner_r_px: float = INNER_SUPPRESS_R_PX,
    ramp_px: float = DISTAL_RAMP_PX,
    max_r_px: int = DISTAL_MAX_R_PX,
    enechelon_deg: float = 16.0,
) -> dict[str, np.ndarray]:
    """Compute 4 strictly fold-visible, self-component-excluded distal accommodation
    bridge channels with inner near-tip halo suppression (r <= inner_r_px -> 0.0).
    """
    vis = np.asarray(catalogue_visible, dtype=bool)
    v = np.asarray(valid, dtype=bool)
    shape = vis.shape
    h, w = shape
    labels, _ = ndi.label(vis, STRUCT8)

    ty, tx, uy, ux, tw, tcomp = _tip_records(vis, labels)
    en_lobe = np.zeros(shape, dtype=np.float32)
    ax_lobe = np.zeros(shape, dtype=np.float32)
    bw = np.zeros(shape, dtype=np.float32)
    bjy = np.zeros(shape, dtype=np.float32)
    bjx = np.zeros(shape, dtype=np.float32)

    cos_e = np.float32(np.cos(np.radians(enechelon_deg)))
    sin_e = np.float32(np.sin(np.radians(enechelon_deg)))

    if ty.size > 0:
        g_idx = np.arange(-max_r_px, max_r_px + 1, dtype=np.float32)
        gy_full, gx_full = np.meshgrid(g_idx, g_idx, indexing="ij")
        dist_full = np.hypot(gy_full, gx_full).astype(np.float32)
        inv_dist_full = np.where(dist_full > 0.0, 1.0 / np.maximum(dist_full, 1e-6), 0.0).astype(np.float32)

        # Smooth inner annulus suppression: ZERO for dist <= inner_r_px!
        ann_ramp = np.clip((dist_full - np.float32(inner_r_px)) / np.float32(max(ramp_px, 1.0)), 0.0, 1.0)
        in_ann = (dist_full > np.float32(inner_r_px)) & (dist_full <= np.float32(max_r_px))
        w_en_full = np.where(in_ann, ann_ramp * np.exp(-(dist_full - np.float32(inner_r_px)) / 20.0), 0.0).astype(np.float32)
        w_ax_full = np.where(in_ann, ann_ramp * np.exp(-(dist_full - np.float32(inner_r_px)) / 32.0), 0.0).astype(np.float32)

        in_br = (dist_full > np.float32(max(inner_r_px - 2.0, 5.0))) & (dist_full <= np.float32(max_r_px))
        br_ramp = np.clip((dist_full - np.float32(max(inner_r_px - 2.0, 5.0))) / np.float32(max(ramp_px, 1.0)), 0.0, 1.0)
        w_br_full = np.where(in_br, br_ramp * np.exp(-(dist_full - np.float32(inner_r_px)) / 26.0), 0.0).astype(np.float32)

        for i in range(ty.size):
            wt = float(tw[i])
            if wt <= 0.0:
                continue
            cy, cx = int(ty[i]), int(tx[i])
            u_y, u_x = np.float32(uy[i]), np.float32(ux[i])
            # Conjugate +/-16 deg Riedel/en-echelon unit vectors
            u1y, u1x = u_y * cos_e - u_x * sin_e, u_y * sin_e + u_x * cos_e
            u2y, u2x = u_y * cos_e + u_x * sin_e, -u_y * sin_e + u_x * cos_e

            y0, y1 = max(0, cy - max_r_px), min(h, cy + max_r_px + 1)
            x0, x1 = max(0, cx - max_r_px), min(w, cx + max_r_px + 1)
            sy0, sy1 = y0 - (cy - max_r_px), y0 - (cy - max_r_px) + (y1 - y0)
            sx0, sx1 = x0 - (cx - max_r_px), x0 - (cx - max_r_px) + (x1 - x0)

            dy = gy_full[sy0:sy1, sx0:sx1]
            dx = gx_full[sy0:sy1, sx0:sx1]
            inv_d = inv_dist_full[sy0:sy1, sx0:sx1]

            c0 = np.maximum((dy * u_y + dx * u_x) * inv_d, 0.0)
            p0 = np.abs(dy * u_x - dx * u_y)

            c1 = np.maximum((dy * u1y + dx * u1x) * inv_d, 0.0)
            p1 = np.abs(dy * u1x - dx * u1y)
            c2 = np.maximum((dy * u2y + dx * u2x) * inv_d, 0.0)
            p2 = np.abs(dy * u2x - dx * u2y)

            en_ang = np.maximum(
                (c1 * c1) * np.exp(-0.5 * (p1 / 6.5) ** 2),
                (c2 * c2) * np.exp(-0.5 * (p2 / 6.5) ** 2),
            ).astype(np.float32)
            ke = np.float32(wt) * w_en_full[sy0:sy1, sx0:sx1] * en_ang
            ka = np.float32(wt) * w_ax_full[sy0:sy1, sx0:sx1] * (c0 * c0) * np.exp(-0.5 * (p0 / 10.5) ** 2).astype(np.float32)
            fwd_b = np.maximum((dy * u_y + dx * u_x) * inv_d + 0.18, 0.0) / 1.18
            kb = np.float32(wt) * w_br_full[sy0:sy1, sx0:sx1] * (fwd_b * fwd_b) * np.exp(-0.5 * (p0 / 10.0) ** 2).astype(np.float32)

            en_lobe[y0:y1, x0:x1] += ke
            ax_lobe[y0:y1, x0:x1] += ka
            bw[y0:y1, x0:x1] += kb
            bjy[y0:y1, x0:x1] += kb * u_y
            bjx[y0:y1, x0:x1] += kb * u_x

        # Exact self-component subtraction on training positive pixels
        order = np.argsort(tcomp, kind="mergesort")
        ty_s, tx_s, uy_s, ux_s, tw_s, tc_s = ty[order], tx[order], uy[order], ux[order], tw[order], tcomp[order]
        uniq_c, starts, counts = np.unique(tc_s, return_index=True, return_counts=True)
        objs = ndi.find_objects(labels)
        r_br_min = float(max(inner_r_px - 2.0, 5.0))
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
                in_r = (dist > r_br_min) & (dist <= max_r_px)
                if not in_r.any():
                    continue
                oy_k, ox_k = oy[in_r], ox[in_r]
                dy_k, dx_k, d_k = dy[in_r], dx[in_r], dist[in_r]
                inv_d = 1.0 / np.maximum(d_k, 1e-6)
                u_y, u_x = np.float32(uy_s[k]), np.float32(ux_s[k])
                u1y, u1x = u_y * cos_e - u_x * sin_e, u_y * sin_e + u_x * cos_e
                u2y, u2x = u_y * cos_e + u_x * sin_e, -u_y * sin_e + u_x * cos_e

                ann_r = np.clip((d_k - np.float32(inner_r_px)) / np.float32(max(ramp_px, 1.0)), 0.0, 1.0)
                w_en_k = np.where(d_k > inner_r_px, ann_r * np.exp(-(d_k - np.float32(inner_r_px)) / 20.0), 0.0)
                w_ax_k = np.where(d_k > inner_r_px, ann_r * np.exp(-(d_k - np.float32(inner_r_px)) / 32.0), 0.0)
                br_r = np.clip((d_k - np.float32(r_br_min)) / np.float32(max(ramp_px, 1.0)), 0.0, 1.0)
                w_br_k = br_r * np.exp(-(d_k - np.float32(inner_r_px)) / 26.0)

                c0 = np.maximum((dy_k * u_y + dx_k * u_x) * inv_d, 0.0)
                p0 = np.abs(dy_k * u_x - dx_k * u_y)
                c1 = np.maximum((dy_k * u1y + dx_k * u1x) * inv_d, 0.0)
                p1 = np.abs(dy_k * u1x - dx_k * u1y)
                c2 = np.maximum((dy_k * u2y + dx_k * u2x) * inv_d, 0.0)
                p2 = np.abs(dy_k * u2x - dx_k * u2y)

                en_ang = np.maximum(
                    (c1 * c1) * np.exp(-0.5 * (p1 / 6.5) ** 2),
                    (c2 * c2) * np.exp(-0.5 * (p2 / 6.5) ** 2),
                )
                ke = wt * w_en_k * en_ang
                ka = wt * w_ax_k * (c0 * c0) * np.exp(-0.5 * (p0 / 10.5) ** 2)
                fwd_b = np.maximum((dy_k * u_y + dx_k * u_x) * inv_d + 0.18, 0.0) / 1.18
                kb = wt * w_br_k * (fwd_b * fwd_b) * np.exp(-0.5 * (p0 / 10.0) ** 2)

                en_lobe[oy_k, ox_k] -= ke.astype(np.float32)
                ax_lobe[oy_k, ox_k] -= ka.astype(np.float32)
                bw[oy_k, ox_k] -= kb.astype(np.float32)
                bjy[oy_k, ox_k] -= (kb * u_y).astype(np.float32)
                bjx[oy_k, ox_k] -= (kb * u_x).astype(np.float32)

    np.maximum(en_lobe, 0.0, out=en_lobe)
    np.maximum(ax_lobe, 0.0, out=ax_lobe)
    np.maximum(bw, 0.0, out=bw)

    bridge_sq = bw * bw - (bjy * bjy + bjx * bjx)
    np.maximum(bridge_sq, 0.0, out=bridge_sq)
    bridge = np.sqrt(bridge_sq, dtype=np.float32)
    del bw, bjy, bjx, bridge_sq

    da_en = np.log1p(en_lobe * np.float32(4.5)).astype(np.float32)
    da_ax = np.log1p(ax_lobe * np.float32(3.5)).astype(np.float32)
    da_br = np.log1p(bridge * np.float32(6.5)).astype(np.float32)
    del en_lobe, ax_lobe, bridge

    # Self-excluded regional structural fabric concordance (sigma = 38 px)
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
        0.0,
        1.0,
    )
    del a_r, b_r, c_r, norm_rad
    d_rad = np.radians(np.asarray(edge_strike_deg, dtype=np.float32) - reg_strike_deg)
    da_concord = (np.cos(d_rad) ** 2 * coh_reg).astype(np.float32)
    del reg_strike_deg, coh_reg, d_rad

    for arr in (da_en, da_ax, da_br, da_concord):
        arr[~v] = 0.0
    return {
        "tt_da_enechelon_annulus": da_en,
        "tt_da_axial_far_annulus": da_ax,
        "tt_da_stepover_bridge": da_br,
        "tt_da_strike_concord": da_concord,
    }


def compute_thermotilt_physics_stack(
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
    out_npy_path: Path | None = None,
) -> dict[str, object]:
    """Build all 29 zero-catalogue THERMOTILT channels (0..28) + strike/cover priors
    with peak anonymous RSS < 950 MiB (using disk-backed memmap when ``out_npy_path``
    is supplied). Zero fault-catalogue arrays are read here.
    """
    foot = np.asarray(footprint, dtype=bool)
    shape = foot.shape
    n_foot = int(foot.sum())
    if out_npy_path is not None:
        out_npy_path = Path(out_npy_path)
        out_npy_path.parent.mkdir(parents=True, exist_ok=True)
        X_foot = np.lib.format.open_memmap(
            out_npy_path, mode="w+", dtype=np.float32, shape=(n_foot, len(FEATURE_NAMES))
        )
        X_foot[:] = 0.0
    else:
        X_foot = np.zeros((n_foot, len(FEATURE_NAMES)), dtype=np.float32)

    line_hydro_harmonic = np.zeros(shape, dtype=np.float32)

    with rasterio.open(training_features_tif) as ds:
        ref_transform = ds.transform
        b2_raw = _read_tf_band(ds, 2)
        b12_raw = _read_tf_band(ds, 12)
        b13_raw = _read_tf_band(ds, 13)
        b19_raw = _read_tf_band(ds, 19)
        valid = foot & np.isfinite(b2_raw) & np.isfinite(b12_raw) & np.isfinite(b13_raw) & np.isfinite(b19_raw)
        del b12_raw, b19_raw

        # --- 0..4: Exact 2D-FFT Harmonic 1VD & Verduzco-Salem Signed-Tilt Contact Crests ---
        mag_harm = harmonic_1vd_signed_tilt(b2_raw, valid, z0_px=1.45)
        _store_col(X_foot, 0, mag_harm["zero_contact"], foot, valid)
        f01_mag_hd = mag_harm["hd_tdr"]
        mag_tilt = mag_harm["signed_tilt"]
        mag_strike = mag_harm["strike_deg"]
        del mag_harm
        _store_col(X_foot, 1, f01_mag_hd, foot, valid)

        grav_harm = harmonic_1vd_signed_tilt(b13_raw, valid, z0_px=1.80)
        _store_col(X_foot, 2, grav_harm["zero_contact"], foot, valid)
        f03_grav_hd = grav_harm["hd_tdr"]
        grav_tilt = grav_harm["signed_tilt"]
        grav_strike = grav_harm["strike_deg"]
        del grav_harm
        _store_col(X_foot, 3, f03_grav_hd, foot, valid)

        phase_diff = np.minimum(np.abs(grav_tilt - mag_tilt), np.abs(grav_tilt + mag_tilt))
        f04_phaselock = (
            np.sqrt(np.maximum(f01_mag_hd * f03_grav_hd, 0.0))
            * np.exp(-(phase_diff / np.float32(0.55)))
        ).astype(np.float32)
        del mag_tilt, grav_tilt, phase_diff
        _store_col(X_foot, 4, f04_phaselock, foot, valid)
        line_hydro_harmonic += np.float32(0.28) * np.maximum(f01_mag_hd, f03_grav_hd) + np.float32(0.22) * f04_phaselock
        del f04_phaselock
        gc.collect()

        # --- 10: Grauch (2001) Magnetite-Destruction Alteration Valve (uses b2_raw, then frees b2_raw) ---
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
        f10_demag = _sat(np.maximum(0.65 * (z_up - z_rtp) + 0.35 * np.abs(z_tmi - z_up), 0.0), 1.45)
        del z_tmi, z_up, z_rtp
        _store_col(X_foot, 10, f10_demag, foot, valid)
        gc.collect()

        # Regional upslope / updip unit vector +u_upslope and structural normal n_perp
        dbase = np.maximum(_clean_valid(_read_tf_band(ds, 15), valid), 0.0).astype(np.float32)
        log_dbase = np.log1p(dbase).astype(np.float32)
        dby_r, dbx_r = _grad_xy(log_dbase, valid, sigma=6.0)
        db_rmag = np.hypot(dby_r, dbx_r) + np.float32(1e-6)

        gy_r, gx_r = _grad_xy(_clean_valid(b13_raw, valid), valid, sigma=6.0)
        g_rmag = np.hypot(gy_r, gx_r) + np.float32(1e-6)

        with rasterio.open(topo_10m_tif) as ds10_head:
            dem10_m = _clean_valid(_decode_u8_band(ds10_head, 9), valid).astype(np.float32)
        zy_r, zx_r = _grad_xy(dem10_m, valid, sigma=6.5)
        z_rmag = np.hypot(zy_r, zx_r) + np.float32(1e-6)
        del dem10_m

        uy_up_raw = 0.58 * (zy_r / z_rmag) - 0.27 * (dby_r / db_rmag) + 0.15 * (gy_r / g_rmag)
        ux_up_raw = 0.58 * (zx_r / z_rmag) - 0.27 * (dbx_r / db_rmag) + 0.15 * (gx_r / g_rmag)
        u_up_mag = np.hypot(uy_up_raw, ux_up_raw) + np.float32(1e-6)
        uy_upslope = (uy_up_raw / u_up_mag).astype(np.float32)
        ux_upslope = (ux_up_raw / u_up_mag).astype(np.float32)
        del uy_up_raw, ux_up_raw, u_up_mag

        ny_raw = -0.45 * (dby_r / db_rmag) + 0.35 * (gy_r / g_rmag) + 0.20 * (zy_r / z_rmag)
        nx_raw = -0.45 * (dbx_r / db_rmag) + 0.35 * (gx_r / g_rmag) + 0.20 * (zx_r / z_rmag)
        n_mag = np.hypot(ny_raw, nx_raw) + np.float32(1e-6)
        ny_perp = (ny_raw / n_mag).astype(np.float32)
        nx_perp = (nx_raw / n_mag).astype(np.float32)
        del dby_r, dbx_r, db_rmag, gy_r, gx_r, g_rmag, zy_r, zx_r, z_rmag, ny_raw, nx_raw, n_mag

        # --- 5..6: Antithetic Accommodation-Zone Polarity-Reversal Tensor ---
        f05_az_graben, f06_az_horst = antithetic_accommodation_twist(b13_raw, ny_perp, nx_perp, valid)
        _store_col(X_foot, 5, f05_az_graben, foot, valid)
        _store_col(X_foot, 6, f06_az_horst, foot, valid)
        line_hydro_harmonic += np.float32(0.20) * np.maximum(f05_az_graben, f06_az_horst)
        del f06_az_horst
        gc.collect()

        # --- 11: Depth-Deconfounded MT Clay-Cap Lateral Edge (B17 vs B15) ---
        cond_log = np.log1p(np.maximum(_clean_valid(_read_tf_band(ds, 17), valid), 0.0)).astype(np.float32)
        bv = log_dbase[valid]
        cv = cond_log[valid]
        bz = (log_dbase - np.float32(bv.mean())) / np.float32(float(bv.std()) + 1e-5)
        z1 = bz[valid]
        # Subsample 250k points for quadratic OLS so column_stack is < 3 MiB instead of 60 MiB float64
        sub_step = max(z1.size // 250_000, 1)
        zs = z1[::sub_step]
        cs = cv[::sub_step]
        coef, *_ = np.linalg.lstsq(np.column_stack([np.ones_like(zs), zs, zs * zs]), cs, rcond=None)
        del bv, cv, z1, zs, cs
        mt_resid = np.where(valid, cond_log - (coef[0] + coef[1] * bz + coef[2] * bz * bz), 0.0).astype(np.float32)
        del cond_log, bz
        mry, mrx = _grad_xy(mt_resid, valid, sigma=1.8)
        del mt_resid
        mrmag = np.hypot(mry, mrx).astype(np.float32)
        del mry, mrx
        f11_mt_edge = _sat(mrmag, max(float(np.percentile(mrmag[valid], 78.0)) * 1.6, 0.035))
        del mrmag
        _store_col(X_foot, 11, f11_mt_edge, foot, valid)
        line_hydro_harmonic += np.float32(0.12) * np.maximum(f10_demag, f11_mt_edge)
        sub_conduit_gate = np.maximum.reduce([f01_mag_hd, f03_grav_hd, f11_mt_edge, f10_demag, f05_az_graben])
        del f05_az_graben, f10_demag, f11_mt_edge
        gc.collect()

        # --- 12..14: Basement Step, Flexure Curvature & Adaptive Listric Updip Ramp ---
        by, bx = _grad_xy(log_dbase, valid, sigma=1.8)
        base_grad = np.hypot(by, bx).astype(np.float32)
        base_strike = ((np.degrees(np.arctan2(by, bx)) + 90.0) % 180.0).astype(np.float32)
        f12_base_step = _sat(base_grad, 0.07)
        _store_col(X_foot, 12, f12_base_step, foot, valid)
        _store_col(X_foot, 13, _sat(hessian_ridge_strength(log_dbase, valid, sigma=3.0), 0.05), foot, valid)

        w_cover = np.clip(log_dbase / np.float32(np.log1p(500.0)), 0.20, 0.75).astype(np.float32)
        w_cover[~valid] = 0.20
        del log_dbase

        ghg = np.maximum(_clean_valid(_read_tf_band(ds, 18), valid), 0.0)
        gvg = _clean_valid(_read_tf_band(ds, 11), valid)
        gslope = np.maximum(_clean_valid(_read_tf_band(ds, 5), valid), 0.0)
        s_adapt = compute_adaptive_dip_offset_px(dbase, ghg, gvg, valid)
        del dbase, gvg
        gh_med = float(np.median(ghg[valid])) + 1e-5
        gs_med = float(np.median(gslope[valid])) + 1e-5
        sub_ramp_src = np.where(
            valid,
            0.38 * f03_grav_hd
            + 0.24 * _sat(ghg, 1.50 * gh_med)
            + 0.18 * _sat(gslope, 1.50 * gs_med)
            + 0.20 * f12_base_step,
            0.0,
        ).astype(np.float32)
        del ghg, gslope
        yy, xx = np.meshgrid(np.arange(shape[0], dtype=np.float32), np.arange(shape[1], dtype=np.float32), indexing="ij")
        f14_adapt_listric = np.where(
            valid,
            0.55 * bilinear_sample_2d(sub_ramp_src, yy - s_adapt * ny_perp, xx - s_adapt * nx_perp, valid)
            + 0.45 * bilinear_sample_2d(sub_ramp_src, yy - np.maximum(s_adapt - 0.85, 1.4) * ny_perp, xx - np.maximum(s_adapt - 0.85, 1.4) * nx_perp, valid),
            0.0,
        ).astype(np.float32)
        del sub_ramp_src, s_adapt, yy, xx, ny_perp, nx_perp
        _store_col(X_foot, 14, f14_adapt_listric, foot, valid)
        gc.collect()

        # --- 15..16: Geodetic Transtensional Strain & Microseismic Criticality ---
        s_2nd = mesoscale_zscore(_clean_valid(_read_tf_band(ds, 4), valid), valid, sigma_px=32.0)
        s_shr = mesoscale_zscore(_clean_valid(_read_tf_band(ds, 7), valid), valid, sigma_px=32.0)
        s_dil = mesoscale_zscore(_clean_valid(_read_tf_band(ds, 8), valid), valid, sigma_px=32.0)
        _store_col(
            X_foot, 15,
            np.clip(0.50 * s_2nd + 0.30 * s_shr + 0.20 * np.maximum(s_dil, -1.0), -4.0, 5.0),
            foot, valid,
        )
        del s_2nd, s_shr, s_dil

        deq = np.maximum(_clean_valid(_read_tf_band(ds, 10), valid), 0.0)
        ieq = np.maximum(_clean_valid(_read_tf_band(ds, 16), valid), 0.0)
        seis = (np.log1p(ieq) / (1.0 + deq / np.float32(25.0))).astype(np.float32)
        del deq, ieq
        _store_col(X_foot, 16, mesoscale_zscore(seis, valid, sigma_px=36.0), foot, valid)
        del seis

        # Read b12 & b19 just before Step 19..28 after freeing subsurface temporaries
        det_elev = _clean_valid(_read_tf_band(ds, 12), valid)
        slope100 = np.maximum(_clean_valid(_read_tf_band(ds, 19), valid), 0.0)
        gy13, gx13 = _grad_xy(_clean_valid(b13_raw, valid), valid, sigma=2.0)
        del b13_raw
        gc.collect()

    # Compute B12/B13/B15 concordance right away so gy13, gx13, by, bx can be freed!
    ey, ex = _grad_xy(det_elev, valid, sigma=1.6)
    enorm = np.maximum(np.hypot(ey, ex), 1e-5)
    gnorm13 = np.maximum(np.hypot(gy13, gx13), 1e-5)
    bnorm = np.maximum(base_grad, 1e-5)
    concord_eb = ((-ey * by - ex * bx) / (enorm * bnorm)).astype(np.float32)
    concord_eg = ((ey * gy13 + ex * gx13) / (enorm * gnorm13)).astype(np.float32)
    del ey, ex, enorm, by, bx, gy13, gx13, gnorm13, bnorm
    _store_col(X_foot, 26, np.clip(0.55 * concord_eb + 0.45 * concord_eg, -1.0, 1.0), foot, valid)
    del concord_eb, concord_eg
    gc.collect()

    # --- 7..9: Upgradient Piezometric Thermal-Plume Back-Projection & Valve Lock ---
    probe_src, probe_stats = _rasterize_2m_temperature_probes(probe_2m_zip, ref_transform, shape, foot)
    spring_src, spring_stats = _rasterize_active_thermal_springs(wellspring_csv, shape, foot)
    active_outflow = (spring_src + np.float32(0.85) * probe_src).astype(np.float32)
    del probe_src, spring_src
    f07_upflow = upgradient_piezometric_backprojection(
        active_outflow, uy_upslope, ux_upslope, valid,
        shifts_px=(5.0, 11.0, 18.0), weights=(0.45, 0.35, 0.20), plume_sigma_px=4.8,
    )
    del active_outflow
    gdr_sym = gdr_blind_thermal_features(wellspring_csv, shape, valid, sigma_px=13.0)["plume_feat"]
    f07_blend = np.where(valid, np.clip(0.72 * f07_upflow + 0.28 * _sat(gdr_sym, 0.85), 0.0, 1.0), 0.0).astype(np.float32)
    del f07_upflow, gdr_sym
    _store_col(X_foot, 7, f07_blend, foot, valid)

    f08_conduit_lock = np.where(
        valid,
        np.clip(f07_blend * (np.float32(0.28) + np.float32(0.72) * sub_conduit_gate), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del f07_blend, sub_conduit_gate
    _store_col(X_foot, 8, f08_conduit_lock, foot, valid)

    paleo_src, paleo_stats = _rasterize_paleo_vents(paleo_zip, ref_transform, shape, foot)
    paleo_up = upgradient_piezometric_backprojection(
        paleo_src, uy_upslope, ux_upslope, valid,
        shifts_px=(3.5, 8.5, 14.0), weights=(0.50, 0.32, 0.18), plume_sigma_px=4.2,
    )
    paleo_strike = anisotropic_strike_plume(paleo_src, valid, sigma_parallel_px=16.0, sigma_perp_px=5.5, strike_deg_east_of_north=18.0)
    del paleo_src
    f09_sinter_up = np.where(
        valid,
        np.clip(0.60 * paleo_up + 0.40 * _sat(np.log1p(paleo_strike * np.float32(28.0)), 0.45), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del paleo_up, paleo_strike
    _store_col(X_foot, 9, f09_sinter_up, foot, valid)

    line_hydro_harmonic += np.float32(0.18) * np.maximum(f08_conduit_lock, f09_sinter_up)
    np.clip(line_hydro_harmonic, 0.0, 1.0, out=line_hydro_harmonic)
    line_hydro_harmonic[~valid] = 0.0
    del f08_conduit_lock, f09_sinter_up
    gc.collect()

    # --- 17..18: GeoDAWN K/Th Alteration & Signed Upslope Redox Dipole ---
    with rasterio.open(geodawn_rad_tif) as ds_rad:
        rk = ds_rad.read(1).astype(np.float32)
        rth = ds_rad.read(2).astype(np.float32)
        ru = ds_rad.read(3).astype(np.float32)
    rad_ok = valid & (rk > 0) & (rth > 0) & (ru > 0)
    k_th = _clean_valid(np.where(rad_ok, rk / np.maximum(rth, 1.0), np.nan), valid)
    u_th = _clean_valid(np.where(rad_ok, ru / np.maximum(rth, 1.0), np.nan), valid)
    del rk, rth, ru, rad_ok
    _store_col(X_foot, 17, mesoscale_zscore(k_th, valid, sigma_px=26.0), foot, valid)

    ky, kx = _grad_xy(k_th, valid, sigma=2.2)
    uy_r, ux_r = _grad_xy(u_th, valid, sigma=2.2)
    del k_th, u_th
    dk_up = ky * uy_upslope + kx * ux_upslope
    du_dn = -(uy_r * uy_upslope + ux_r * ux_upslope)
    del ky, kx, uy_r, ux_r, uy_upslope, ux_upslope
    dipole_raw = np.sqrt(np.maximum(dk_up, 0.0) * np.maximum(du_dn, 0.0)).astype(np.float32)
    del dk_up, du_dn
    _store_col(X_foot, 18, _sat(dipole_raw, max(float(np.percentile(dipole_raw[valid], 92.0)) * 1.4, 1e-4)), foot, valid)
    del dipole_raw
    gc.collect()

    # --- 19..28: USGS 3DEP 10 m Scarp, 10 m Chi, Lahontan Null & 3-Family Corroboration ---
    with rasterio.open(topo_10m_tif) as ds_t10:
        s_max = _decode_u8_band(ds_t10, 2)
        f19_scarp_ex = subpixel_scarp_excess(s_max, slope100, valid)
        del s_max
        _store_col(X_foot, 19, f19_scarp_ex, foot, valid)

        pied_w = (1.0 / (1.0 + (slope100 / np.float32(9.5)) ** 2)).astype(np.float32)
        f20_curv_pied = _sat(_clean_valid(_decode_u8_band(ds_t10, 6), valid) * pied_w, 6.0)
        del pied_w
        _store_col(X_foot, 20, f20_curv_pied, foot, valid)

        coh10 = (_clean_valid(_decode_u8_band(ds_t10, 7), valid) * _clean_valid(_decode_u8_band(ds_t10, 8), valid)).astype(np.float32)
        f21_coh10 = _sat(coh10, 0.22)
        del coh10
        _store_col(X_foot, 21, f21_coh10, foot, valid)

        dem10_m2 = _clean_valid(_decode_u8_band(ds_t10, 9), valid).astype(np.float32)
    del slope100

    with rasterio.open(dem10_chi_tif) as ds_chi:
        chi_step = np.maximum(ds_chi.read(1).astype(np.float32) / 1000.0, 0.0)
        chi_ksn = np.maximum(ds_chi.read(3).astype(np.float32), 0.0)
    f22_chi_step = _sat(np.log1p(_clean_valid(chi_step, valid) * np.float32(4.0)), 0.85)
    f23_chi_ksn = _sat(np.log1p(_clean_valid(chi_ksn, valid) * np.float32(0.08)), 1.40)
    del chi_step, chi_ksn
    _store_col(X_foot, 22, f22_chi_step, foot, valid)
    _store_col(X_foot, 23, f23_chi_ksn, foot, valid)
    del f23_chi_ksn

    h12 = _sat(hessian_ridge_strength(det_elev, valid, sigma=1.2), 1.4)
    h30 = _sat(hessian_ridge_strength(det_elev, valid, sigma=3.0), 2.2)
    f24_hess = (np.float32(0.55) * h12 + np.float32(0.45) * h30).astype(np.float32)
    del h12, h30
    _store_col(X_foot, 24, f24_hess, foot, valid)

    coh_el, topo_strike = coherence_and_strike_deg(det_elev, valid, deriv_sigma=1.2, tensor_sigma=3.5)
    _store_col(X_foot, 25, cross_strike_monotonicity(det_elev, valid, half_span_px=3), foot, valid)
    del det_elev

    lahontan_band = np.exp(-0.5 * ((dem10_m2 - np.float32(1330.0)) / np.float32(45.0)) ** 2).astype(np.float32)
    f27_lahontan = (lahontan_band * (1.0 - np.minimum(base_grad / np.float32(0.08), 1.0))).astype(np.float32)
    del dem10_m2, lahontan_band
    _store_col(X_foot, 27, f27_lahontan, foot, valid)

    line_scarp_chi = np.where(
        valid,
        np.clip(
            (0.35 * f19_scarp_ex + 0.22 * f20_curv_pied + 0.18 * f21_coh10 + 0.13 * f22_chi_step + 0.12 * f24_hess)
            * np.exp(-1.5 * f27_lahontan),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    del f19_scarp_ex, f20_curv_pied, f21_coh10, f22_chi_step, f24_hess, f27_lahontan

    f28_corrob = compute_second_best_corroboration(line_scarp_chi, f14_adapt_listric, line_hydro_harmonic, valid)
    _store_col(X_foot, 28, f28_corrob, foot, valid)
    del f28_corrob, f14_adapt_listric

    # Cover-adaptive multi-physics strike orientation in [0, 180)
    w_topo = np.where(valid, coh_el * (1.0 - 0.65 * w_cover), 0.0).astype(np.float32)
    w_harm = np.where(valid, 0.55 * f03_grav_hd + 0.45 * f01_mag_hd + 0.40 * f12_base_step, 0.0).astype(np.float32)
    c2 = (
        w_topo * np.cos(np.radians(2.0 * topo_strike))
        + w_harm * (
            0.45 * np.cos(np.radians(2.0 * grav_strike))
            + 0.30 * np.cos(np.radians(2.0 * mag_strike))
            + 0.25 * np.cos(np.radians(2.0 * base_strike))
        )
    )
    s2 = (
        w_topo * np.sin(np.radians(2.0 * topo_strike))
        + w_harm * (
            0.45 * np.sin(np.radians(2.0 * grav_strike))
            + 0.30 * np.sin(np.radians(2.0 * mag_strike))
            + 0.25 * np.sin(np.radians(2.0 * base_strike))
        )
    )
    edge_strike_deg = ((0.5 * np.degrees(np.arctan2(s2, c2))) % 180.0).astype(np.float32)
    edge_strike_deg[~valid] = 0.0
    del coh_el, topo_strike, grav_strike, mag_strike, base_strike, base_grad, w_topo, w_harm, c2, s2
    del f01_mag_hd, f03_grav_hd, f12_base_step
    if isinstance(X_foot, np.memmap):
        X_foot.flush()
    gc.collect()

    return {
        "X_foot": X_foot,
        "valid": valid,
        "w_cover": w_cover,
        "edge_strike_deg": edge_strike_deg,
        "line_hydro_harmonic": line_hydro_harmonic,
        "line_scarp_chi": line_scarp_chi,
        "external_stats": {
            "paleo_vents": paleo_stats,
            "probes_2m": probe_stats,
            "thermal_springs": spring_stats,
        },
    }


def _fit_logistic_subsampled(
    X_foot: np.ndarray,
    cols: tuple[int, ...],
    pos_foot: np.ndarray,
    neg_foot: np.ndarray,
    *,
    max_pos: int = 24000,
    max_neg: int = 96000,
    C: float = 0.35,
    seed: int = 20261026,
) -> tuple[LogisticRegression, np.ndarray, np.ndarray]:
    """Fit standardized L2 logistic regression on balanced subsampled footprint rows."""
    rng = np.random.default_rng(seed)
    pos_idx = np.flatnonzero(pos_foot)
    neg_idx = np.flatnonzero(neg_foot)
    if pos_idx.size > max_pos:
        pos_idx = rng.choice(pos_idx, size=max_pos, replace=False)
    if neg_idx.size > max_neg:
        neg_idx = rng.choice(neg_idx, size=max_neg, replace=False)

    tr_idx = np.concatenate([pos_idx, neg_idx])
    y_tr = np.concatenate([
        np.ones(pos_idx.size, dtype=np.int32),
        np.zeros(neg_idx.size, dtype=np.int32),
    ])
    X_tr = X_foot[tr_idx][:, list(cols)].astype(np.float32)
    mu = X_tr.mean(axis=0).astype(np.float32)
    sd = np.maximum(X_tr.std(axis=0), 1e-5).astype(np.float32)
    X_std = np.clip((X_tr - mu) / sd, -8.0, 8.0)

    clf = LogisticRegression(C=float(C), max_iter=350, class_weight="balanced", solver="lbfgs")
    clf.fit(X_std, y_tr)
    return clf, mu, sd


def _predict_logistic_foot(
    clf: LogisticRegression,
    mu: np.ndarray,
    sd: np.ndarray,
    X_foot: np.ndarray,
    cols: tuple[int, ...],
    chunk: int = 600_000,
) -> np.ndarray:
    n = X_foot.shape[0]
    out = np.empty(n, dtype=np.float32)
    col_list = list(cols)
    for i0 in range(0, n, chunk):
        i1 = min(i0 + chunk, n)
        Xb = np.clip((X_foot[i0:i1, col_list] - mu) / sd, -8.0, 8.0)
        out[i0:i1] = clf.predict_proba(Xb)[:, 1].astype(np.float32)
    return out


def fit_stage1_oof_loqo(
    X_foot: np.ndarray,
    foot: np.ndarray,
    valid: np.ndarray,
    visible_cat: np.ndarray,
    quad: np.ndarray,
    *,
    train_mask_grid: np.ndarray | None = None,
    seed: int = 20261026,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit pairwise out-of-fold Stage-1 blind-subsurface & full-physics models across
    the spatial quadrants ``quad`` (0..3) so every training quadrant receives strictly
    OOF predictions and any held-out quadrant averages all Stage-1 OOF models.
    """
    foot_b = np.asarray(foot, dtype=bool)
    valid_f = np.asarray(valid, dtype=bool)[foot_b]
    vis_b = np.asarray(visible_cat, dtype=bool)
    d_vis = distance_transform_edt(~vis_b).astype(np.float32)

    if train_mask_grid is not None:
        tr_elig = np.asarray(train_mask_grid, dtype=bool)[foot_b] & valid_f
    else:
        tr_elig = valid_f

    pos_all = vis_b[foot_b] & tr_elig
    neg_all = (d_vis[foot_b] > 4.5) & tr_elig
    del d_vis

    quad_f = np.asarray(quad, dtype=np.int32)[foot_b]
    q_masks_f = [quad_f == qi for qi in range(4)]
    n_f = int(foot_b.sum())

    oof_sub_f = np.zeros(n_f, dtype=np.float32)
    oof_full_f = np.zeros(n_f, dtype=np.float32)
    counts_f = np.zeros(n_f, dtype=np.float32)

    active_qs = [qi for qi in range(4) if int((pos_all & q_masks_f[qi]).sum()) >= 50]
    if len(active_qs) >= 2:
        for val_qi in active_qs:
            tr_mask = np.zeros(n_f, dtype=bool)
            for tr_qi in active_qs:
                if tr_qi != val_qi:
                    tr_mask |= q_masks_f[tr_qi]
            clf_s, mu_s, sd_s = _fit_logistic_subsampled(
                X_foot, STAGE1_SUB_COLS, pos_all & tr_mask, neg_all & tr_mask, seed=seed + 11 * val_qi
            )
            clf_p, mu_p, sd_p = _fit_logistic_subsampled(
                X_foot, STAGE1_FULL_COLS, pos_all & tr_mask, neg_all & tr_mask, seed=seed + 29 * val_qi
            )
            eval_mask = ~tr_mask
            idx_ev = np.flatnonzero(eval_mask)
            Xb_s = np.clip((X_foot[idx_ev][:, list(STAGE1_SUB_COLS)] - mu_s) / sd_s, -8.0, 8.0)
            Xb_p = np.clip((X_foot[idx_ev][:, list(STAGE1_FULL_COLS)] - mu_p) / sd_p, -8.0, 8.0)
            oof_sub_f[idx_ev] += clf_s.predict_proba(Xb_s)[:, 1].astype(np.float32)
            oof_full_f[idx_ev] += clf_p.predict_proba(Xb_p)[:, 1].astype(np.float32)
            counts_f[idx_ev] += 1.0
    else:
        clf_s, mu_s, sd_s = _fit_logistic_subsampled(X_foot, STAGE1_SUB_COLS, pos_all, neg_all, seed=seed)
        clf_p, mu_p, sd_p = _fit_logistic_subsampled(X_foot, STAGE1_FULL_COLS, pos_all, neg_all, seed=seed + 1)
        oof_sub_f = _predict_logistic_foot(clf_s, mu_s, sd_s, X_foot, STAGE1_SUB_COLS)
        oof_full_f = _predict_logistic_foot(clf_p, mu_p, sd_p, X_foot, STAGE1_FULL_COLS)
        counts_f[:] = 1.0

    counts_f = np.maximum(counts_f, 1.0)
    p_sub = np.zeros(foot_b.shape, dtype=np.float32)
    p_full = np.zeros(foot_b.shape, dtype=np.float32)
    p_sub[foot_b] = oof_sub_f / counts_f
    p_full[foot_b] = oof_full_f / counts_f
    p_sub[~valid] = 0.0
    p_full[~valid] = 0.0
    return p_sub, p_full


def fit_stage2_thermotilt_loqo(
    X_foot: np.ndarray,
    foot: np.ndarray,
    valid: np.ndarray,
    w_cover: np.ndarray,
    edge_strike_deg: np.ndarray,
    line_hydro_harmonic: np.ndarray,
    visible_cat: np.ndarray,
    quad: np.ndarray,
    *,
    include_distal: bool,
    train_mask_grid: np.ndarray | None = None,
    seed: int = 20261026,
) -> np.ndarray:
    """Fit bimodal (cover-weighted subsurface + full-physics) Stage-2 THERMOTILT surface
    and sharpen along local multi-physics fault strike via 1D directional ridge bonus.
    """
    foot_b = np.asarray(foot, dtype=bool)
    valid_b = np.asarray(valid, dtype=bool)
    valid_f = valid_b[foot_b]
    vis_b = np.asarray(visible_cat, dtype=bool)
    d_vis = distance_transform_edt(~vis_b).astype(np.float32)

    if train_mask_grid is not None:
        tr_elig = np.asarray(train_mask_grid, dtype=bool)[foot_b] & valid_f
    else:
        tr_elig = valid_f

    pos_all = vis_b[foot_b] & tr_elig
    neg_all = (d_vis[foot_b] > 4.5) & tr_elig
    del d_vis

    cols_sub = DISTAL_SUB_STAGE2_COLS if include_distal else BLIND_SUB_STAGE2_COLS
    cols_full = DISTAL_FULL_STAGE2_COLS if include_distal else BLIND_FULL_STAGE2_COLS

    if train_mask_grid is not None:
        clf_s, mu_s, sd_s = _fit_logistic_subsampled(X_foot, cols_sub, pos_all, neg_all, C=0.30, seed=seed + 101)
        clf_p, mu_p, sd_p = _fit_logistic_subsampled(X_foot, cols_full, pos_all, neg_all, C=0.30, seed=seed + 202)
        ps_f = _predict_logistic_foot(clf_s, mu_s, sd_s, X_foot, cols_sub)
        pf_f = _predict_logistic_foot(clf_p, mu_p, sd_p, X_foot, cols_full)
    else:
        quad_f = np.asarray(quad, dtype=np.int32)[foot_b]
        q_masks_f = [quad_f == qi for qi in range(4)]
        ps_f = np.zeros(int(foot_b.sum()), dtype=np.float32)
        pf_f = np.zeros(int(foot_b.sum()), dtype=np.float32)
        covered = np.zeros(int(foot_b.sum()), dtype=bool)
        for qi, qf in enumerate(q_masks_f):
            if not qf.any():
                continue
            tr_m = ~qf
            clf_s, mu_s, sd_s = _fit_logistic_subsampled(
                X_foot, cols_sub, pos_all & tr_m, neg_all & tr_m, C=0.30, seed=seed + 31 * qi
            )
            clf_p, mu_p, sd_p = _fit_logistic_subsampled(
                X_foot, cols_full, pos_all & tr_m, neg_all & tr_m, C=0.30, seed=seed + 47 * qi
            )
            idx_q = np.flatnonzero(qf)
            Xb_s = np.clip((X_foot[idx_q][:, list(cols_sub)] - mu_s) / sd_s, -8.0, 8.0)
            Xb_p = np.clip((X_foot[idx_q][:, list(cols_full)] - mu_p) / sd_p, -8.0, 8.0)
            ps_f[idx_q] = clf_s.predict_proba(Xb_s)[:, 1].astype(np.float32)
            pf_f[idx_q] = clf_p.predict_proba(Xb_p)[:, 1].astype(np.float32)
            covered[idx_q] = True
        if (~covered).any():
            clf_s, mu_s, sd_s = _fit_logistic_subsampled(X_foot, cols_sub, pos_all, neg_all, C=0.30, seed=seed + 99)
            clf_p, mu_p, sd_p = _fit_logistic_subsampled(X_foot, cols_full, pos_all, neg_all, C=0.30, seed=seed + 199)
            idx_u = np.flatnonzero(~covered)
            ps_f[idx_u] = clf_s.predict_proba(np.clip((X_foot[idx_u][:, list(cols_sub)] - mu_s) / sd_s, -8.0, 8.0))[:, 1].astype(np.float32)
            pf_f[idx_u] = clf_p.predict_proba(np.clip((X_foot[idx_u][:, list(cols_full)] - mu_p) / sd_p, -8.0, 8.0))[:, 1].astype(np.float32)

    wc_f = np.asarray(w_cover, dtype=np.float32)[foot_b]
    hh_f = np.asarray(line_hydro_harmonic, dtype=np.float32)[foot_b]
    p_blend_f = ((wc_f * ps_f + (1.0 - wc_f) * pf_f) * (np.float32(0.82) + np.float32(0.36) * hh_f)).astype(np.float32)

    surf = np.zeros(foot_b.shape, dtype=np.float32)
    surf[foot_b] = p_blend_f
    surf = calibrate_quadrant_probabilities(surf, valid_b, quad)

    surf_sm = gaussian_filter(surf, sigma=1.1).astype(np.float32)
    ridge = directional_ridge_1d(surf_sm, valid_b).astype(np.float32)
    crest = np.where(valid_b, np.clip(surf_sm * (np.float32(0.82) + np.float32(0.22) * ridge), 0.0, 1.0), 0.0).astype(np.float32)
    return crest


def allocate_dual_regime_crests(
    blind_surface: np.ndarray,
    distal_surface: np.ndarray | None,
    line_hydro_harmonic: np.ndarray,
    distal_bridge_strength: np.ndarray | None,
    visible_cat: np.ndarray,
    valid: np.ndarray,
    *,
    budget_dots: int = 37654,
    corridor_max_dots: int = 15000,
    min_dcat_px: float = 2.0,
    min_sep_px: float = 2.85,
) -> np.ndarray:
    """Allocate ``budget_dots`` mutually spaced 1.0 impulses strictly at ``d_vis > min_dcat_px``.

    - If ``distal_surface`` is None (Exp 1 ``thermotilt_blind``): selects ``budget_dots``
      spaced crests from the zero-catalogue ``blind_surface`` boosted on novel
      harmonic-tilt / upgradient-thermal / accommodation-twist features.
    - If ``distal_surface`` is provided (Exp 2 ``thermotilt_distal_bridge``):
      enforces an explicit dual-regime capacity split:
        * Regime A (<= ``corridor_max_dots`` = 39.8%): distal annular accommodation
          corridor (``distal_bridge_strength > 0`` at r > 9 px from visible tips,
          gated by physical ``blind_surface`` corroboration).
        * Regime B (>= ``budget_dots - corridor_max_dots`` = 60.2%): off-corridor
          blind THERMOTILT discoveries across the full footprint, maintaining strict
          ``min_sep_px`` mutual exclusion from Regime A dots as well.
    """
    v = np.asarray(valid, dtype=bool)
    vis = np.asarray(visible_cat, dtype=bool)
    d_vis = distance_transform_edt(~vis).astype(np.float32)
    elig = v & (d_vis > float(min_dcat_px))
    del d_vis

    blind_boosted = np.where(
        elig,
        np.asarray(blind_surface, dtype=np.float32) * (np.float32(0.74) + np.float32(0.52) * np.asarray(line_hydro_harmonic, dtype=np.float32)),
        0.0,
    ).astype(np.float32)

    if distal_surface is None or distal_bridge_strength is None or corridor_max_dots <= 0:
        mask = spaced_top_mask(
            blind_boosted,
            elig,
            int(budget_dots),
            min_dist_px=float(min_sep_px),
            cand_cap=950_000,
            require_full=True,
        )
        return mask.astype(np.float32)

    br_str = np.asarray(distal_bridge_strength, dtype=np.float32)
    corridor_elig = elig & (br_str > np.float32(0.06))
    # Require physical corroboration inside distal bridge so empty alluvium is rejected
    corridor_score = np.where(
        corridor_elig,
        np.asarray(distal_surface, dtype=np.float32) * np.sqrt(np.maximum(blind_boosted, np.float32(1e-4))),
        0.0,
    ).astype(np.float32)

    mask_a = spaced_top_mask(
        corridor_score,
        corridor_elig,
        int(corridor_max_dots),
        min_dist_px=float(min_sep_px),
        cand_cap=650_000,
        require_full=False,
    )
    n_a = int(mask_a.sum())
    rem = max(int(budget_dots) - n_a, 0)
    if rem == 0:
        return mask_a.astype(np.float32)

    # Exclude corridor_elig AND min_sep_px halo around Regime A dots so Regime B
    # strictly allocates >= (budget_dots - corridor_max_dots) off-corridor blind crests!
    if n_a > 0:
        d_a = distance_transform_edt(~mask_a).astype(np.float32)
        base_rem = elig & (d_a >= float(min_sep_px))
        del d_a
    else:
        base_rem = elig
    elig_b = base_rem & (~corridor_elig)

    mask_b = spaced_top_mask(
        blind_boosted,
        elig_b,
        rem,
        min_dist_px=float(min_sep_px),
        cand_cap=950_000,
        require_full=False,
    )
    still_rem = rem - int(mask_b.sum())
    if still_rem > 0:
        d_ab = distance_transform_edt(~(mask_a | mask_b)).astype(np.float32)
        mask_spill = spaced_top_mask(
            blind_boosted,
            elig & (d_ab >= float(min_sep_px)),
            still_rem,
            min_dist_px=float(min_sep_px),
            cand_cap=950_000,
            require_full=True,
        )
        del d_ab
        return (mask_a | mask_b | mask_spill).astype(np.float32)
    return (mask_a | mask_b).astype(np.float32)


def build_graded_tail_allocation(
    primary_binary: np.ndarray,
    ranking_surface: np.ndarray,
    visible_cat: np.ndarray,
    valid: np.ndarray,
    *,
    extra_dots: int = 12346,
    tail_weight: float = 0.62,
    min_dcat_px: float = 2.0,
    min_sep_px: float = 3.00,
) -> np.ndarray:
    """Add ``extra_dots`` mutually spaced secondary crests at fractional amplitude
    ``tail_weight`` in (0, 1) without altering the 1.0 primary crests (Exp 3).
    """
    prim = np.asarray(primary_binary, dtype=np.float32) > 0.5
    v = np.asarray(valid, dtype=bool)
    vis = np.asarray(visible_cat, dtype=bool)
    d_vis = distance_transform_edt(~vis).astype(np.float32)
    d_prim = distance_transform_edt(~prim).astype(np.float32)
    elig_tail = v & (d_vis > float(min_dcat_px)) & (d_prim >= float(min_sep_px))
    del d_vis, d_prim

    tail_mask = spaced_top_mask(
        np.asarray(ranking_surface, dtype=np.float32),
        elig_tail,
        int(extra_dots),
        min_dist_px=float(min_sep_px),
        cand_cap=800_000,
        require_full=False,
    )
    out = np.zeros(v.shape, dtype=np.float32)
    out[tail_mask] = np.float32(tail_weight)
    out[prim] = np.float32(1.0)
    out[~v] = 0.0
    return out
