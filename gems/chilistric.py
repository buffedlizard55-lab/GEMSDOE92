"""CHILISTRIC lane: Depth- & Tilt-Adaptive Listric Hanging-Wall Updip Projection
+ Seamless USGS 3DEP 10 m Sub-Pixel Scarp & Fluvial Chi-Step Interfluve Bridge
+ Local-Strike-Advected Hydrothermal Sinter/2m-Probe Valve Corroboration (LOQO).

Pre-registered hypothesis & equations: docs/HYPOTHESES_20261025_CHILISTRIC.md.

Key physical innovations over LISTRICLOQO and VENTSCARP:
1. Spatially depth- & tilt-adaptive updip listric projection s_adapt(x) in [1.80, 6.20] px
   from effective cover thickness h_eff(x) = min(Band 15, 1100 m) and smoothed
   gravity horizontal-to-vertical gradient dip proxy cot(theta_dip)(x) (Band 18 / |Band 11|),
   preventing footwall overshoot on shallow (<200 m) bedrock pediments while capturing
   deep (>650 m) listric graben master faults within the 300 m (3.0 px) DTI kernel.
2. Seamless USGS 3DEP 1/3-arc-second (~10 m) sub-pixel scarp excess, Wallace profile
   curvature, aspect/hillshade coherence, and 10 m tributary fluvial chi/k_sn knickpoint
   steps bridged +/- 3.4 & +/- 4.6 px along local strike across faceted interfluves,
   deconfounded for ~1,330 m Pleistocene Lake Lahontan wave-cut shoreline benches.
3. Local-strike-advected (+/- 3.5, 7.5, 12.5 px along t_strike(x)) tufa-excluded
   DOE GDR #1391 paleo-geothermal vents (siliceous sinter, explosion craters, Qss,
   travertine; pure lacustrine Tufa excluded), shallow 2 m temperature probe conductive
   anomalies (F2mDAB >= 1.2 C), and geothermometer springs locked onto Grauch (2001)
   150 m upward-continued magnetite-destruction residuals (z(TMI_up150) - z(RTP)) and
   cover-deconfounded magnetotelluric lateral conductivity walls.
4. Second-best multi-line physical corroboration gate across the 3 orthogonal physical
   families {10m Scarp/Chi, Adaptive Updip Listric, Hydrothermal/Alteration Valve} plus
   non-diluting additive secondary recall expansion (preserving 1.0 on top 37,654 crests
   while adding mutually spaced secondary corroborated crests at amplitude w_tail in (0, 1]).

Strict zero-leakage invariant: zero fault-catalogue arrays ever enter any feature
or surface builder in this module.
"""
from __future__ import annotations

import gc
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt, gaussian_filter

from .breakline import spaced_top_mask
from .coulomb_loqo import _grad_xy, _sat, directional_ridge_1d
from .hydroconduit import _clean_valid
from .knick_loqo import calibrate_quadrant_probabilities, fit_single_loqo, mesoscale_zscore
from .listric_loqo import (
    DEBIASED_INDICES as BASE_DEBIASED_INDICES,
    FEATURE_NAMES as BASE_LISTRIC_FEATURE_NAMES,
    LISTRIC_EXTRA_NAMES,
    SUB_KNICK_INDICES as BASE_SUB_KNICK_INDICES,
    bilinear_sample_2d,
    compute_listric_extra_channels,
)
from .knick_loqo import compute_knick_loqo_stack
from .ventscarp import (
    _decode_u8_band,
    _rasterize_2m_temperature_probes,
    _rasterize_active_thermal_springs,
    _rasterize_paleo_vents,
    anisotropic_strike_plume,
    subpixel_scarp_excess,
)

__all__ = [
    "CHILISTRIC_EXTRA_NAMES",
    "FEATURE_NAMES",
    "BASE_ONLY_INDICES",
    "DEBIASED_INDICES",
    "ADAPT_SUB_INDICES",
    "SCARP10M_HYDRO_INDICES",
    "compute_adaptive_dip_offset_px",
    "compute_second_best_corroboration",
    "compute_chilistric_extra_channels",
    "compute_chilistric_stack",
    "fit_predict_chilistric_loqo",
    "build_chilistric_crest_surface",
    "build_additive_tail_allocation",
    "spaced_top_mask",
]

CHILISTRIC_EXTRA_NAMES: tuple[str, ...] = (
    "f37_adapt_listric_updip_ramp",
    "f38_scarp10m_lahontan_deconfound",
    "f39_chi10m_interfluve_bridge",
    "f40_scarp10m_adapt_listric_lock",
    "f41_strike_advected_vent_probe_valve",
    "f42_grauch_demag_alteration_valve",
    "f43_mt_depth_residual_edge",
    "f44_multiline_second_best_corrob",
)

FEATURE_NAMES: tuple[str, ...] = BASE_LISTRIC_FEATURE_NAMES + CHILISTRIC_EXTRA_NAMES

# Ablation indices (drops all 8 new CHILISTRIC channels 36..43)
BASE_ONLY_INDICES: tuple[int, ...] = tuple(range(0, 36))

# Province-debiased branch: base debiased + all 8 new scale-free CHILISTRIC channels
DEBIASED_INDICES: tuple[int, ...] = BASE_DEBIASED_INDICES + (36, 37, 38, 39, 40, 41, 42, 43)

# Adaptive subsurface + listric + MT/demag branch
ADAPT_SUB_INDICES: tuple[int, ...] = BASE_SUB_KNICK_INDICES + (36, 38, 39, 41, 42, 43)

# 10 m Sub-Pixel Scarp + Chi + Strike-Advected Hydrothermal Valve branch
SCARP10M_HYDRO_INDICES: tuple[int, ...] = (
    0, 2, 4, 8, 9, 10, 12, 13, 21, 22, 23, 27, 29, 30, 33, 34, 35,
    36, 37, 38, 39, 40, 41, 42, 43,
)


def compute_adaptive_dip_offset_px(
    depth_to_base: np.ndarray,
    grav_hg: np.ndarray,
    grav_vg: np.ndarray,
    valid: np.ndarray,
    *,
    min_shift_px: float = 1.80,
    max_shift_px: float = 6.20,
) -> np.ndarray:
    """Compute spatially adaptive updip listric offset ``s_adapt(x)`` in 100 m pixels.

    Shallow pediment margins (h_base ~ 100-200 m) receive ~1.8-2.3 px updip shift so
    projections do not overshoot onto footwall granite; deep asymmetric grabens
    (h_base >= 700 m) with listric flattening (high |grav_hg| / |grav_vg| ratio)
    receive up to 5.5-6.2 px updip shift onto the surface range-front break.
    """
    valid_b = np.asarray(valid, dtype=bool)
    if not valid_b.any():
        return np.zeros(valid_b.shape, dtype=np.float32)

    b_clean = np.clip(_clean_valid(depth_to_base, valid_b), 0.0, 4000.0).astype(np.float32)
    b_smooth = gaussian_filter(b_clean, sigma=2.2).astype(np.float32)
    h_eff = np.minimum(b_smooth, np.float32(1100.0))

    hg_sm = gaussian_filter(np.maximum(_clean_valid(grav_hg, valid_b), 0.0), sigma=2.5).astype(np.float32)
    vg_sm = gaussian_filter(np.abs(_clean_valid(grav_vg, valid_b)), sigma=2.5).astype(np.float32)
    hg_med = float(np.median(hg_sm[valid_b])) + 1e-5

    cot_dip = np.clip(0.66 + 0.34 * (hg_sm / (vg_sm + np.float32(hg_med))), 0.66, 1.12).astype(np.float32)
    s_adapt = np.clip(1.75 + 0.0040 * h_eff * cot_dip, float(min_shift_px), float(max_shift_px)).astype(
        np.float32
    )
    s_adapt[~valid_b] = 0.0
    return s_adapt


def compute_second_best_corroboration(
    line_a: np.ndarray,
    line_b: np.ndarray,
    line_c: np.ndarray,
    valid: np.ndarray,
) -> np.ndarray:
    """Return pixelwise second-largest amplitude across 3 normalized physical families.

    Suppresses single-modality false positives (where two families are ~0) while
    rewarding faults corroborated by ANY two of {10m Scarp/Chi, Adaptive Updip Listric,
    Hydrothermal/Alteration Valve}.
    """
    valid_b = np.asarray(valid, dtype=bool)
    a = np.where(valid_b, np.clip(np.asarray(line_a, dtype=np.float32), 0.0, 1.0), 0.0)
    b = np.where(valid_b, np.clip(np.asarray(line_b, dtype=np.float32), 0.0, 1.0), 0.0)
    c = np.where(valid_b, np.clip(np.asarray(line_c, dtype=np.float32), 0.0, 1.0), 0.0)
    # Median of 3 values = a + b + c - min(a,b,c) - max(a,b,c)
    mn = np.minimum(np.minimum(a, b), c)
    mx = np.maximum(np.maximum(a, b), c)
    sec = np.clip(a + b + c - mn - mx, 0.0, 1.0).astype(np.float32)
    sec[~valid_b] = 0.0
    return sec


def _mt_depth_deconfounded_edge(
    cond_surf: np.ndarray,
    depth_to_base: np.ndarray,
    grav_vg: np.ndarray,
    valid: np.ndarray,
) -> np.ndarray:
    """Regress out smooth basin-depth conductivity expectation E[log(1+cond) | h_base]
    and extract lateral gradient edges concordant with vertical-gravity zero crossings.
    """
    valid_b = np.asarray(valid, dtype=bool)
    if not valid_b.any():
        return np.zeros(valid_b.shape, dtype=np.float32)

    cond_log = np.log1p(np.maximum(_clean_valid(cond_surf, valid_b), 0.0)).astype(np.float32)
    b_log = np.log1p(np.clip(_clean_valid(depth_to_base, valid_b), 0.0, 5000.0)).astype(np.float32)
    # Fit quadratic conditional expectation E[cond_log | b_log] on valid footprint
    bv = b_log[valid_b]
    cv = cond_log[valid_b]
    b_mean = float(bv.mean())
    b_std = float(bv.std()) + 1e-5
    bz = (b_log - np.float32(b_mean)) / np.float32(b_std)
    z1 = bz[valid_b]
    z2 = z1 * z1
    design = np.column_stack([np.ones_like(z1), z1, z2])
    coef, *_ = np.linalg.lstsq(design, cv, rcond=None)
    expected = (coef[0] + coef[1] * bz + coef[2] * (bz * bz)).astype(np.float32)
    resid = np.where(valid_b, cond_log - expected, 0.0).astype(np.float32)

    ry, rx = _grad_xy(resid, valid_b, sigma=1.8)
    rmag = np.hypot(ry, rx).astype(np.float32)
    rp75 = max(float(np.percentile(rmag[valid_b], 75.0)), 0.035)
    rsat = _sat(rmag, 1.65 * rp75)

    vg_clean = _clean_valid(grav_vg, valid_b).astype(np.float32)
    vg_iqr = float(np.percentile(np.abs(vg_clean[valid_b]), 75.0)) + 1e-5
    vg_zero = np.exp(-0.5 * ((vg_clean / (1.55 * vg_iqr)) ** 2)).astype(np.float32)

    out = np.where(valid_b, np.clip(rsat * (0.42 + 0.58 * vg_zero), 0.0, 1.0), 0.0).astype(np.float32)
    return out


def compute_chilistric_extra_channels(
    *,
    l_sub: np.ndarray,
    l_rad_relay: np.ndarray,
    rtp: np.ndarray,
    grav_slope: np.ndarray,
    grav_vg: np.ndarray,
    det_elev: np.ndarray,
    grav_anom: np.ndarray,
    depth_to_base: np.ndarray,
    cond_surf: np.ndarray,
    grav_hg: np.ndarray,
    det_elev_slope: np.ndarray,
    topo_10m_tif: Path,
    dem10_chi_tif: Path,
    paleo_zip: Path,
    probe_2m_zip: Path,
    wellspring_csv: Path,
    geodawn_ext_tif: Path,
    transform: rasterio.Affine,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute the 8 new zero-catalogue CHILISTRIC channels (f37..f44) and 1D branches."""
    valid_b = np.asarray(valid, dtype=bool)
    shape = valid_b.shape
    h, w = shape

    # 1. Regional Updip Footwall Normal n_updip and Strike Tangent t_strike
    b_clean = np.clip(_clean_valid(depth_to_base, valid_b), 0.0, 5000.0).astype(np.float32)
    log_b = np.log1p(b_clean).astype(np.float32)
    dby_m, dbx_m = _grad_xy(log_b, valid_b, sigma=5.5)
    db_mag = np.hypot(dby_m, dbx_m) + np.float32(1e-6)

    gy_m, gx_m = _grad_xy(grav_anom, valid_b, sigma=5.5)
    g_mag = np.hypot(gy_m, gx_m) + np.float32(1e-6)

    ey_m, ex_m = _grad_xy(det_elev, valid_b, sigma=4.5)
    e_mag = np.hypot(ey_m, ex_m) + np.float32(1e-6)

    uy = -0.46 * (dby_m / db_mag) + 0.34 * (gy_m / g_mag) + 0.20 * (ey_m / e_mag)
    ux = -0.46 * (dbx_m / db_mag) + 0.34 * (gx_m / g_mag) + 0.20 * (ex_m / e_mag)
    umag = np.hypot(uy, ux) + np.float32(1e-6)
    ny_up = (uy / umag).astype(np.float32)
    nx_up = (ux / umag).astype(np.float32)
    ty_st = (-nx_up).astype(np.float32)
    tx_st = ny_up.astype(np.float32)
    del dby_m, dbx_m, db_mag, gy_m, gx_m, g_mag, ey_m, ex_m, e_mag, uy, ux, umag

    # 2. Depth- & Tilt-Adaptive Listric Updip Subsurface Ramp (f37 & L_adapt_listric)
    s_adapt = compute_adaptive_dip_offset_px(depth_to_base, grav_hg, grav_vg, valid_b)

    dby2, dbx2 = _grad_xy(log_b, valid_b, sigma=2.0)
    db_step = np.hypot(dby2, dbx2)
    db_med = float(np.median(db_step[valid_b])) + 1e-5
    db_sat = _sat(db_step, 1.55 * db_med)
    del dby2, dbx2, db_step, log_b

    gs_clean = np.maximum(_clean_valid(grav_slope, valid_b), 0.0).astype(np.float32)
    gh_clean = np.maximum(_clean_valid(grav_hg, valid_b), 0.0).astype(np.float32)
    gs_med = float(np.median(gs_clean[valid_b])) + 1e-5
    gh_med = float(np.median(gh_clean[valid_b])) + 1e-5
    sub_ramp = np.where(
        valid_b,
        0.44 * np.asarray(l_sub, dtype=np.float32)
        + 0.30 * _sat(gh_clean, 1.50 * gh_med)
        + 0.14 * _sat(gs_clean, 1.50 * gs_med)
        + 0.12 * db_sat,
        0.0,
    ).astype(np.float32)
    del gs_clean, gh_clean, db_sat, b_clean

    yy, xx = np.meshgrid(
        np.arange(h, dtype=np.float32),
        np.arange(w, dtype=np.float32),
        indexing="ij",
    )
    s_lo = np.maximum(s_adapt - np.float32(0.75), np.float32(1.40))
    s_hi = np.minimum(s_adapt + np.float32(0.75), np.float32(6.80))

    r_mid = bilinear_sample_2d(sub_ramp, yy - s_adapt * ny_up, xx - s_adapt * nx_up, valid_b)
    r_lo = bilinear_sample_2d(sub_ramp, yy - s_lo * ny_up, xx - s_lo * nx_up, valid_b)
    r_hi = bilinear_sample_2d(sub_ramp, yy - s_hi * ny_up, xx - s_hi * nx_up, valid_b)
    del sub_ramp, s_lo, s_hi, s_adapt

    l_adapt_listric = np.where(
        valid_b,
        np.clip(0.50 * r_mid + 0.25 * r_lo + 0.25 * r_hi, 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    f37_adapt_listric_updip_ramp = np.where(
        valid_b,
        np.clip(0.55 * l_adapt_listric + 0.45 * np.maximum(r_mid, np.maximum(r_lo, r_hi)), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del r_mid, r_lo, r_hi

    # 3. Seamless 3DEP 10 m Sub-Pixel Scarp + Lahontan Shoreline Deconfounder (f38)
    b19_clean = _clean_valid(det_elev_slope, valid_b)
    p99_b19 = float(np.percentile(b19_clean[valid_b], 99.0)) if valid_b.any() else 1.0
    if p99_b19 <= 2.5:
        slope_100m_deg = np.rad2deg(np.arctan(np.maximum(b19_clean, 0.0))).astype(np.float32)
    else:
        slope_100m_deg = np.maximum(b19_clean, 0.0).astype(np.float32)
    del b19_clean

    with rasterio.open(topo_10m_tif) as ds10:
        s10_p90 = _decode_u8_band(ds10, 1)
        s10_max = _decode_u8_band(ds10, 2)
        curv10_prof = _decode_u8_band(ds10, 6)
        asp10_coh = _decode_u8_band(ds10, 7)
        hs10_lin = _decode_u8_band(ds10, 8)
        dem10_mean = _decode_u8_band(ds10, 9)

    ex_max = subpixel_scarp_excess(s10_max, slope_100m_deg, valid_b)
    pied_gate = np.exp(-((slope_100m_deg / np.float32(11.8)) ** 2)).astype(np.float32)
    curv_pied = np.where(valid_b, np.log1p(np.maximum(curv10_prof, 0.0)) * pied_gate, 0.0).astype(np.float32)
    lin_coh = np.where(valid_b, asp10_coh * hs10_lin, 0.0).astype(np.float32)
    gy_s10, gx_s10 = _grad_xy(s10_p90, valid_b, sigma=1.0)
    steep_step = np.hypot(gx_s10, gy_s10).astype(np.float32)

    # Lake Lahontan (~1,330 m) horizontal shoreline bench mimic index:
    # High when elevation sits near 1,330 +/- 55 m AND scarp gradient parallels elevation contour
    # (low cross-contour transgression) AND lacks adaptive updip gravity support.
    zy10, zx10 = _grad_xy(dem10_mean, valid_b, sigma=2.5)
    zmag10 = np.hypot(zy10, zx10) + np.float32(1e-5)
    smag10 = steep_step + np.float32(1e-5)
    # Cross-contour transgression = |grad(slope_10m) x grad(elev_10m)| / (|grad(slope)| |grad(elev)|)
    cross_sin = np.abs((gx_s10 * zy10 - gy_s10 * zx10) / (smag10 * zmag10))
    lahontan_band = np.exp(-0.5 * (((dem10_mean - np.float32(1330.0)) / np.float32(55.0)) ** 2)).astype(np.float32)
    lahontan_mimic = np.where(
        valid_b,
        lahontan_band * (np.float32(1.0) - cross_sin) * np.exp(-3.5 * f37_adapt_listric_updip_ramp),
        0.0,
    ).astype(np.float32)
    del s10_p90, s10_max, curv10_prof, asp10_coh, hs10_lin, dem10_mean, gy_s10, gx_s10, zy10, zx10, zmag10, smag10

    scarp10m_raw = (
        0.36 * _sat(ex_max, 0.82) * (0.35 + 0.65 * pied_gate)
        + 0.26 * _sat(curv_pied, 1.55)
        + 0.22 * _sat(lin_coh, 0.21) * (0.40 + 0.60 * pied_gate)
        + 0.16 * _sat(steep_step, 3.40) * pied_gate
    )
    f38_scarp10m_lahontan_deconfound = np.where(
        valid_b,
        np.clip(scarp10m_raw * (np.float32(1.0) - np.float32(0.55) * lahontan_mimic) * (0.75 + 0.25 * cross_sin), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del ex_max, pied_gate, curv_pied, lin_coh, steep_step, slope_100m_deg, scarp10m_raw, lahontan_band, lahontan_mimic, cross_sin

    # 4. Seamless 3DEP 10 m Fluvial Chi-Step Interfluve Bridge (f39 & L_scarp10m_chi_bridge)
    with rasterio.open(dem10_chi_tif) as dschi:
        step_raw = dschi.read(1).astype(np.float32)
        ksn_raw = dschi.read(3).astype(np.float32)
        area_raw = dschi.read(4).astype(np.float32)
    chi_valid = valid_b & (step_raw > -32000)
    chi_step_pos = np.where(chi_valid, np.log1p(np.maximum(step_raw, 0.0) * 0.001), 0.0).astype(np.float32)
    chi_sm = np.where(valid_b, gaussian_filter(chi_step_pos, 1.4), 0.0).astype(np.float32)
    ksn_pos = np.where(
        chi_valid & (ksn_raw > -32000) & (area_raw > -32000),
        np.log1p(np.maximum(ksn_raw, 0.0)) * np.clip(area_raw * 0.001 - 4.0, 0.0, 3.8),
        0.0,
    ).astype(np.float32)
    ksn_sm = np.where(valid_b, gaussian_filter(ksn_pos, 1.4), 0.0).astype(np.float32)
    l_chi_local = np.where(valid_b, 0.62 * _sat(chi_sm, 0.24) + 0.38 * _sat(ksn_sm, 2.10), 0.0).astype(np.float32)
    del step_raw, ksn_raw, area_raw, chi_valid, chi_step_pos, chi_sm, ksn_pos, ksn_sm

    c_p34 = bilinear_sample_2d(l_chi_local, yy + 3.4 * ty_st, xx + 3.4 * tx_st, valid_b)
    c_m34 = bilinear_sample_2d(l_chi_local, yy - 3.4 * ty_st, xx - 3.4 * tx_st, valid_b)
    c_p46 = bilinear_sample_2d(l_chi_local, yy + 4.6 * ty_st, xx + 4.6 * tx_st, valid_b)
    c_m46 = bilinear_sample_2d(l_chi_local, yy - 4.6 * ty_st, xx - 4.6 * tx_st, valid_b)
    f39_chi10m_interfluve_bridge = np.where(
        valid_b,
        np.clip(
            0.46 * l_chi_local
            + 0.30 * (0.5 * (c_p34 + c_m34))
            + 0.24 * np.sqrt(np.maximum(c_p34, c_p46) * np.maximum(c_m34, c_m46)),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    del l_chi_local, c_p34, c_m34, c_p46, c_m46

    l_scarp10m_chi_bridge = np.where(
        valid_b,
        np.clip(
            0.58 * f38_scarp10m_lahontan_deconfound
            + 0.42 * f39_chi10m_interfluve_bridge,
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)

    f40_scarp10m_adapt_listric_lock = np.where(
        valid_b,
        np.clip(
            np.sqrt(np.maximum(l_scarp10m_chi_bridge, 0.03) * np.maximum(f37_adapt_listric_updip_ramp, 0.0)),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)

    # 5. Local-Strike-Advected Tufa-Filtered Paleo-Vent + 2m Probe + Spring Valve (f41)
    paleo_imp, paleo_stats = _rasterize_paleo_vents(paleo_zip, transform, shape, valid_b)
    probe_imp, probe_stats = _rasterize_2m_temperature_probes(probe_2m_zip, transform, shape, valid_b)
    spring_imp, spring_stats = _rasterize_active_thermal_springs(wellspring_csv, shape, valid_b)

    vent_seed = np.where(
        valid_b,
        gaussian_filter((1.35 * paleo_imp + 1.05 * probe_imp + 0.80 * spring_imp).astype(np.float32), sigma=2.2),
        0.0,
    ).astype(np.float32)
    reg_plume = anisotropic_strike_plume(
        (1.25 * paleo_imp + 1.00 * probe_imp + 0.75 * spring_imp).astype(np.float32),
        valid_b,
        strike_deg_east_of_north=18.0,
        sigma_parallel_px=22.0,
        sigma_perp_px=7.5,
    )
    del paleo_imp, probe_imp, spring_imp

    # Advect local hydrothermal impulse along local strike tangent t_strike (+/- 3.5, 7.5, 12.5 px)
    v_0 = vent_seed
    v_35 = 0.5 * (
        bilinear_sample_2d(vent_seed, yy + 3.5 * ty_st, xx + 3.5 * tx_st, valid_b)
        + bilinear_sample_2d(vent_seed, yy - 3.5 * ty_st, xx - 3.5 * tx_st, valid_b)
    )
    v_75 = 0.5 * (
        bilinear_sample_2d(vent_seed, yy + 7.5 * ty_st, xx + 7.5 * tx_st, valid_b)
        + bilinear_sample_2d(vent_seed, yy - 7.5 * ty_st, xx - 7.5 * tx_st, valid_b)
    )
    v_125 = 0.5 * (
        bilinear_sample_2d(vent_seed, yy + 12.5 * ty_st, xx + 12.5 * tx_st, valid_b)
        + bilinear_sample_2d(vent_seed, yy - 12.5 * ty_st, xx - 12.5 * tx_st, valid_b)
    )
    del vent_seed, yy, xx, ny_up, nx_up, ty_st, tx_st

    strike_vent = (1.00 * v_0 + 0.82 * v_35 + 0.60 * v_75 + 0.40 * v_125) * np.float32(18.0)
    f41_strike_advected_vent_probe_valve = np.where(
        valid_b,
        np.clip(0.62 * _sat(strike_vent, 0.35) + 0.38 * _sat(reg_plume * 3.2, 0.45), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del v_0, v_35, v_75, v_125, strike_vent, reg_plume

    # 6. Grauch (2001) Upward-Continued Magnetite Destruction + GeoDAWN Alteration Valve (f42)
    with rasterio.open(geodawn_ext_tif) as dsext:
        thk_u8 = dsext.read(1).astype(np.float32)
        uth_u8 = dsext.read(3).astype(np.float32)
        tmi150_u8 = dsext.read(4).astype(np.float32)
    ext_valid = valid_b & (thk_u8 > 0) & (tmi150_u8 > 0)
    k_over_th_z = -mesoscale_zscore(thk_u8, ext_valid, sigma_px=40.0)
    u_over_th_z = mesoscale_zscore(uth_u8, ext_valid, sigma_px=40.0)
    rtp_z30 = mesoscale_zscore(rtp, ext_valid & np.isfinite(rtp), sigma_px=30.0)
    tmi150_z30 = mesoscale_zscore(tmi150_u8, ext_valid, sigma_px=30.0)
    grauch_demag = np.where(ext_valid, np.clip(tmi150_z30 - rtp_z30, 0.0, 4.0), 0.0).astype(np.float32)
    dy_dm, dx_dm = _grad_xy(grauch_demag, valid_b, sigma=1.6)
    demag_edge = np.hypot(dy_dm, dx_dm).astype(np.float32)
    dm_med = float(np.median(demag_edge[valid_b])) + 1e-5
    alt_enrich = np.maximum(0.55 * k_over_th_z + 0.45 * u_over_th_z, 0.0).astype(np.float32)

    f42_grauch_demag_alteration_valve = np.where(
        valid_b,
        np.clip(
            (0.45 * _sat(grauch_demag, 1.10) + 0.30 * _sat(demag_edge, 1.6 * dm_med) + 0.25 * _sat(alt_enrich, 1.25))
            * (0.45 + 0.55 * np.maximum(f41_strike_advected_vent_probe_valve, f37_adapt_listric_updip_ramp)),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    del thk_u8, uth_u8, tmi150_u8, ext_valid, k_over_th_z, u_over_th_z, rtp_z30, tmi150_z30, grauch_demag, dy_dm, dx_dm, demag_edge, alt_enrich

    # 7. Cover-Deconfounded Magnetotelluric Lateral Conductivity Wall (f43)
    f43_mt_depth_residual_edge = _mt_depth_deconfounded_edge(
        cond_surf, depth_to_base, grav_vg, valid_b
    )

    l_hydro_valve = np.where(
        valid_b,
        np.clip(
            0.34 * np.asarray(l_rad_relay, dtype=np.float32)
            + 0.28 * f41_strike_advected_vent_probe_valve
            + 0.22 * f42_grauch_demag_alteration_valve
            + 0.16 * f43_mt_depth_residual_edge,
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)

    # 8. Multi-Line Second-Best Physical Corroboration Gate (f44)
    f44_multiline_second_best_corrob = compute_second_best_corroboration(
        l_scarp10m_chi_bridge,
        l_adapt_listric,
        l_hydro_valve,
        valid_b,
    )

    return dict(
        f37_adapt_listric_updip_ramp=f37_adapt_listric_updip_ramp,
        f38_scarp10m_lahontan_deconfound=f38_scarp10m_lahontan_deconfound,
        f39_chi10m_interfluve_bridge=f39_chi10m_interfluve_bridge,
        f40_scarp10m_adapt_listric_lock=f40_scarp10m_adapt_listric_lock,
        f41_strike_advected_vent_probe_valve=f41_strike_advected_vent_probe_valve,
        f42_grauch_demag_alteration_valve=f42_grauch_demag_alteration_valve,
        f43_mt_depth_residual_edge=f43_mt_depth_residual_edge,
        f44_multiline_second_best_corrob=f44_multiline_second_best_corrob,
        L_scarp10m_chi_bridge=l_scarp10m_chi_bridge,
        L_adapt_listric=l_adapt_listric,
        L_hydro_valve=l_hydro_valve,
        vent_audit=dict(
            paleo=paleo_stats,
            probe_2m=probe_stats,
            thermal_springs=spring_stats,
        ),
    )


def compute_chilistric_stack(
    *,
    training_features_tif: Path,
    rad_tif: Path,
    gdr_wellspring_csv: Path,
    topo_10m_tif: Path,
    dem10_chi_tif: Path,
    paleo_zip: Path,
    probe_2m_zip: Path,
    geodawn_ext_tif: Path,
    footprint: np.ndarray,
    out_npy_path: Path | None = None,
) -> dict[str, object]:
    """Compute the full 44-feature zero-catalogue CHILISTRIC stack in 3 memory-bounded phases (<1.5 GiB RSS)."""
    from .coulomb_loqo import gdr_blind_thermal_features

    foot = np.asarray(footprint, dtype=bool)
    n_foot = int(foot.sum())
    if out_npy_path is not None:
        out_npy_path.parent.mkdir(parents=True, exist_ok=True)
        X_out: np.ndarray = np.lib.format.open_memmap(
            out_npy_path, mode="w+", dtype=np.float32, shape=(n_foot, len(FEATURE_NAMES))
        )
    else:
        X_out = np.zeros((n_foot, len(FEATURE_NAMES)), dtype=np.float32)

    def _rd_tf(band_idx: int) -> np.ndarray:
        with rasterio.open(training_features_tif) as src:
            a = src.read(band_idx).astype(np.float32)
        a[~foot] = np.nan
        a[np.abs(a) > 1e20] = np.nan
        return a

    with rasterio.open(training_features_tif) as src_meta:
        transform = src_meta.transform

    # Phase A: cols 0..29 (KNICKLOQO base stack)
    rtp = _rd_tf(2)
    geod_2ndinv = _rd_tf(4)
    grav_slope = _rd_tf(5)
    geod_shearrate = _rd_tf(7)
    geod_dilaterate = _rd_tf(8)
    grav_vg = _rd_tf(11)
    det_elev = _rd_tf(12)
    grav_anom = _rd_tf(13)
    depth_to_base = _rd_tf(15)
    cond_surf = _rd_tf(17)
    grav_hg = _rd_tf(18)
    det_elev_slope = _rd_tf(19)

    with rasterio.open(rad_tif) as rsrc:
        rad_k = rsrc.read(1).astype(np.float32)
        rad_th = rsrc.read(2).astype(np.float32)
        rad_u = rsrc.read(3).astype(np.float32)

    gdr_plume = gdr_blind_thermal_features(gdr_wellspring_csv, foot.shape, foot)

    knick = compute_knick_loqo_stack(
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
        gdr_plume_feat=gdr_plume["plume_feat"],
        footprint=foot,
    )
    X_out[:, :30] = knick["X_foot"]
    valid = knick["valid"]
    l_topo = knick["L_topo"]
    l_knick = knick["L_knick"]
    l_sub = knick["L_sub"]
    del knick, geod_2ndinv, geod_shearrate, geod_dilaterate, gdr_plume
    gc.collect()

    # Phase B: cols 30..35 (LISTRICLOQO channels)
    extra_ll = compute_listric_extra_channels(
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
        X_out[:, 30 + k_i] = extra_ll[k_name][foot]
    l_knick_bridge = extra_ll["L_knick_bridge"]
    l_listric_fixed = extra_ll["L_listric_updip"]
    l_rad_relay_base = extra_ll["L_rad_relay"]
    del l_knick, rad_k, rad_th, rad_u, extra_ll
    gc.collect()

    # Phase C: cols 36..43 (CHILISTRIC 10m scarp/chi + adaptive listric + strike-hydro valve)
    extra_cl = compute_chilistric_extra_channels(
        l_sub=l_sub,
        l_rad_relay=l_rad_relay_base,
        rtp=rtp,
        grav_slope=grav_slope,
        grav_vg=grav_vg,
        det_elev=det_elev,
        grav_anom=grav_anom,
        depth_to_base=depth_to_base,
        cond_surf=cond_surf,
        grav_hg=grav_hg,
        det_elev_slope=det_elev_slope,
        topo_10m_tif=topo_10m_tif,
        dem10_chi_tif=dem10_chi_tif,
        paleo_zip=paleo_zip,
        probe_2m_zip=probe_2m_zip,
        wellspring_csv=gdr_wellspring_csv,
        geodawn_ext_tif=geodawn_ext_tif,
        transform=transform,
        valid=valid,
    )
    for k_i, k_name in enumerate(CHILISTRIC_EXTRA_NAMES):
        X_out[:, 36 + k_i] = extra_cl[k_name][foot]
    if hasattr(X_out, "flush"):
        X_out.flush()

    del l_sub, rtp, grav_slope, grav_vg, det_elev, grav_anom, depth_to_base, cond_surf, grav_hg, det_elev_slope
    gc.collect()

    out = dict(
        X_foot=X_out,
        valid=valid,
        L_topo=l_topo,
        L_knick_bridge=l_knick_bridge,
        L_listric_fixed=l_listric_fixed,
        L_rad_relay_base=l_rad_relay_base,
        L_scarp10m_chi_bridge=extra_cl["L_scarp10m_chi_bridge"],
        L_adapt_listric=extra_cl["L_adapt_listric"],
        L_hydro_valve=extra_cl["L_hydro_valve"],
        f44_corrob=extra_cl["f44_multiline_second_best_corrob"],
        vent_audit=extra_cl["vent_audit"],
    )
    del extra_cl
    gc.collect()
    return out


def fit_predict_chilistric_loqo(
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
    max_iter: int = 195,
    w_full: float = 0.14,
    w_debiased: float = 0.28,
    w_adapt_sub: float = 0.34,
    w_scarp10m_hydro: float = 0.24,
    calib_weight_full: float = 0.38,
    calib_weight_sub: float = 0.86,
    power_gamma: float = 3.35,
) -> dict[str, np.ndarray]:
    """Fit 4-branch selective-quadrant-calibrated CHILISTRIC LOQO ensemble."""
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
    p_adapt = fit_single_loqo(
        X_foot, footprint, valid_b, quad, label_mask,
        feature_cols=ADAPT_SUB_INDICES, excluded_mask=excluded_mask,
        guard_px=guard_px, neg_buffer_px=neg_buffer_px,
        neg_pos_ratio=neg_pos_ratio, seed=int(seed) + 2, max_iter=max_iter,
    )
    p_sh = fit_single_loqo(
        X_foot, footprint, valid_b, quad, label_mask,
        feature_cols=SCARP10M_HYDRO_INDICES, excluded_mask=excluded_mask,
        guard_px=guard_px, neg_buffer_px=neg_buffer_px,
        neg_pos_ratio=neg_pos_ratio, seed=int(seed) + 3, max_iter=max_iter,
    )

    raw_proba = (
        np.float32(w_full) * p_full
        + np.float32(w_debiased) * p_deb
        + np.float32(w_adapt_sub) * p_adapt
        + np.float32(w_scarp10m_hydro) * p_sh
    ).astype(np.float32)

    p_full_cal = calibrate_quadrant_probabilities(
        p_full, valid_b, quad, calib_weight=calib_weight_full, power_gamma=power_gamma
    )
    w_rest = max(float(w_debiased + w_adapt_sub + w_scarp10m_hydro), 1e-6)
    p_rest = (
        (np.float32(w_debiased) * p_deb + np.float32(w_adapt_sub) * p_adapt + np.float32(w_scarp10m_hydro) * p_sh)
        / np.float32(w_rest)
    ).astype(np.float32)
    p_rest_cal = calibrate_quadrant_probabilities(
        p_rest, valid_b, quad, calib_weight=calib_weight_sub, power_gamma=power_gamma
    )
    selectcal_proba = (
        np.float32(w_full) * p_full_cal + np.float32(w_rest) * p_rest_cal
    ).astype(np.float32)

    return dict(
        p_full=p_full,
        p_debiased=p_deb,
        p_adapt_sub=p_adapt,
        p_scarp10m_hydro=p_sh,
        raw_proba=raw_proba,
        selectcal_proba=selectcal_proba,
    )


def build_chilistric_crest_surface(
    proba_2d: np.ndarray,
    l_scarp10m_chi_bridge: np.ndarray,
    l_adapt_listric: np.ndarray,
    l_hydro_valve: np.ndarray,
    f44_corrob: np.ndarray,
    valid: np.ndarray,
    *,
    scarp10m_chi_weight: float = 1.28,
    adapt_listric_weight: float = 1.48,
    hydro_valve_weight: float = 1.18,
    corrob_boost: float = 0.52,
) -> dict[str, np.ndarray]:
    """Build multi-line corroborated 1D crest surface and union directional ridge mask."""
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0), 0.0)

    e_scarp = np.float32(scarp10m_chi_weight) * np.asarray(l_scarp10m_chi_bridge, dtype=np.float32)
    e_listric = np.float32(adapt_listric_weight) * np.asarray(l_adapt_listric, dtype=np.float32)
    e_hydro = np.float32(hydro_valve_weight) * np.asarray(l_hydro_valve, dtype=np.float32)
    e_line = np.maximum(e_scarp, np.maximum(e_listric, e_hydro))

    # Multi-line second-best corroboration factor (19GEMSDOE physical corroboration principle)
    corrob_gate = np.float32(1.0) + np.float32(corrob_boost) * np.clip(
        np.asarray(f44_corrob, dtype=np.float32) / np.float32(0.22), 0.0, 1.25
    )

    s_crest = np.where(
        valid_b,
        p * (np.float32(0.12) + np.float32(0.88) * e_line) * corrob_gate,
        0.0,
    ).astype(np.float32)

    ridge_1d = (
        directional_ridge_1d(s_crest, valid_b)
        | directional_ridge_1d(np.where(valid_b, p * l_scarp10m_chi_bridge, 0.0).astype(np.float32), valid_b)
        | directional_ridge_1d(np.where(valid_b, p * l_adapt_listric, 0.0).astype(np.float32), valid_b)
        | directional_ridge_1d(np.where(valid_b, p * l_hydro_valve, 0.0).astype(np.float32), valid_b)
    )
    return dict(
        S_crest=s_crest,
        E_line=np.where(valid_b, e_line, 0.0).astype(np.float32),
        ridge_1d=ridge_1d,
    )


def build_additive_tail_allocation(
    primary_dots: np.ndarray,
    score_surface: np.ndarray,
    eligible_mask: np.ndarray,
    *,
    n_tail_dots: int = 14346,
    min_dist_from_primary_px: float = 4.20,
    tail_min_dist_px: float = 4.20,
    tail_weight: float = 0.65,
    cand_cap: int = 1_200_000,
) -> np.ndarray:
    """Preserve exact 1.0 peaks on ``primary_dots`` while adding ``n_tail_dots``
    non-overlapping secondary crests at amplitude ``tail_weight`` in (0, 1].
    """
    if not (0.0 < tail_weight <= 1.0):
        raise ValueError("tail_weight must lie in (0, 1]")
    prim = np.asarray(primary_dots, dtype=bool)
    elig = np.asarray(eligible_mask, dtype=bool)
    if prim.shape != elig.shape or prim.shape != score_surface.shape:
        raise ValueError("shape mismatch in build_additive_tail_allocation")

    out = np.where(prim, np.float32(1.0), np.float32(0.0)).astype(np.float32)
    if int(n_tail_dots) <= 0:
        return out

    d_prim = distance_transform_edt(~prim)
    tail_elig = elig & (~prim) & (d_prim >= float(min_dist_from_primary_px))
    tail_dots = spaced_top_mask(
        score_surface,
        tail_elig,
        int(n_tail_dots),
        min_dist_px=float(tail_min_dist_px),
        cand_cap=int(cand_cap),
    )
    out[tail_dots] = np.float32(tail_weight)
    return out
