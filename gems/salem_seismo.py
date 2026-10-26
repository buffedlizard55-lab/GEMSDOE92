"""SALEMSEISMO lane: Shallow Salem Magnetic Tilt-Depth & Remanent-Demagnetization Contacts
+ Walker Lane Azimuthal Seismo-Geodetic Shear Corridors
+ Signed 10 m Piedmont Toe-Concavity & Bipolar Chi-Drainage
+ GeoDAWN Th/K-U/Th Illite-Alteration Curtains
with Seam-Free Dual-Partition (LOQO + Rotated-45-deg LODO) OOF & Exact 25-Offset
300 m Triangular-Kernel Submodular (CELF) Crest Placement.

Pre-registered specification: docs/HYPOTHESES_20261026_SALEMSEISMO.md

Strict zero-leakage invariant: zero fault-catalogue pixels ever enter any feature
or continuous score surface in this module.
"""
from __future__ import annotations

import gc
import heapq
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import convolve, distance_transform_edt, gaussian_filter

from .breakline import spaced_top_mask, structure_tensor_coherence
from .chilistric import compute_adaptive_dip_offset_px, compute_second_best_corroboration
from .coulomb_loqo import _grad_xy, _sat, directional_ridge_1d
from .hydroconduit import _clean_valid
from .knick_loqo import calibrate_quadrant_probabilities, fit_single_loqo, mesoscale_zscore
from .listric_loqo import bilinear_sample_2d
from .ventscarp import (
    _decode_u8_band,
    _rasterize_2m_temperature_probes,
    _rasterize_active_thermal_springs,
    _rasterize_paleo_vents,
    subpixel_scarp_excess,
)

__all__ = [
    "EXPECTED_TRAINING_BANDS",
    "FEATURE_NAMES",
    "CONCEALED_BRANCH_INDICES",
    "DEBIASED_PIEDMONT_INDICES",
    "KERNEL_300M_OFFSETS",
    "KERNEL_300M_7X7",
    "assert_training_band_tags",
    "diamond_wedge_ids",
    "compute_salem_seismo_stack",
    "fit_predict_salem_seismo_dual_oof",
    "build_salem_seismo_crest_surface",
    "celf_submodular_place",
    "celf_additive_tail_allocation",
    "spaced_top_mask",
]

EXPECTED_TRAINING_BANDS: dict[int, str] = {
    1: "mag_anom",
    2: "rtp",
    3: "tmi_hg",
    4: "geod_2ndinv",
    5: "iso_grav_anom_slope",
    6: "tc",
    7: "geod_shearrate",
    8: "geod_dilaterate",
    9: "tmi_vg",
    10: "deq_n100a15",
    11: "iso_grav_anom_vg",
    12: "det_elev",
    13: "iso_grav_anom",
    14: "tmi",
    15: "depth_to_base_surf",
    16: "ieq_n100a15",
    17: "cond_surf",
    18: "iso_grav_anom_hg",
    19: "det_elev_slope",
}

FEATURE_NAMES: tuple[str, ...] = (
    # Family 1: Shallow Concealed Magnetic Contact & Hydrothermal Demagnetization (0..6)
    "s01_salem_tilt_zero_contact",
    "s02_mag_analytic_crest",
    "s03_hydro_mag_trough_wall",
    "s04_remanent_koenigsberger_phase",
    "s05_tmi_rtp_dipole_asymmetry",
    "s06_mt_depth_deconfounded_wall",
    "s07_salem_mt_demag_lock",
    # Family 2: Walker Lane & CNSB Seismo-Geodetic Transtensional Corridor (7..11)
    "s08_seismic_corridor_anisotropy",
    "s09_walker_shear_strain_ridge",
    "s10_transtensional_coulomb_dilation",
    "s11_seismo_geodetic_coupled_zone",
    "s12_seismic_distance_gradient_edge",
    # Family 3: Signed 10 m Piedmont Toe-Concavity, Bipolar Chi & Flexural Toe (12..18)
    "s13_piedmont_signed_toe_concavity",
    "s14_subpixel_relief_scarp_excess",
    "s15_chi10m_synthetic_knick",
    "s16_chi10m_antithetic_graben_pond",
    "s17_bipolar_chi_scarp_lock",
    "s18_flexural_basement_toe_inflection",
    "s19_basin_thickness_regime_context",
    # Family 4: GeoDAWN Th/K-U/Th Alteration Curtain, Sinter Valve & Nematic Bridge (19..25)
    "s20_potassic_illite_thk_trough",
    "s21_redox_uth_uk_fault_front",
    "s22_radiometric_total_count_step",
    "s23_strike_advected_sinter_probe_valve",
    "s24_hydrothermal_alteration_curtain",
    "s25_nematic_tensor_geodesic_bridge",
    "s26_quad_regime_second_best_corrob",
)

# Concealed Basin + Seismo-Geodetic + Alteration branch (drops direct 10m slope/relief & raw basin context)
CONCEALED_BRANCH_INDICES: tuple[int, ...] = (
    0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 10, 11,
    14, 15, 17,
    19, 20, 21, 22, 23, 24, 25,
)

# Scale-free Piedmont + Bipolar Chi + Seismo + Alteration Debiased branch (drops mesoscale depth context s19)
DEBIASED_PIEDMONT_INDICES: tuple[int, ...] = (
    0, 2, 3, 5, 6,
    7, 8, 9, 10, 11,
    12, 13, 14, 15, 16, 17,
    19, 20, 22, 23, 24, 25,
)


def _build_kernel_300m() -> tuple[tuple[tuple[int, int, float], ...], np.ndarray]:
    offs: list[tuple[int, int, float]] = []
    k7 = np.zeros((7, 7), dtype=np.float32)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            d = float(np.hypot(dy, dx))
            if d < 3.0:
                w = float(1.0 - d / 3.0)
                offs.append((dy, dx, w))
                k7[dy + 3, dx + 3] = np.float32(w)
    return tuple(offs), k7


KERNEL_300M_OFFSETS, KERNEL_300M_7X7 = _build_kernel_300m()


def assert_training_band_tags(ds: rasterio.DatasetReader) -> None:
    """Verify all 19 GDAL band_name tags match official GEMS metadata."""
    if ds.count != 19:
        raise ValueError(f"Expected 19 bands in training_features.tif, got {ds.count}")
    for b_idx, expected_name in EXPECTED_TRAINING_BANDS.items():
        actual = ds.tags(b_idx).get("band_name")
        if actual != expected_name:
            raise ValueError(
                f"Band {b_idx} tag mismatch: expected {expected_name!r}, got {actual!r}"
            )


def diamond_wedge_ids(footprint: np.ndarray) -> np.ndarray:
    """Partition active footprint into 4 rotated-45-degree azimuthal wedges (0..3)
    around the footprint centroid so LOQO+LODO averaging eliminates rectangular
    N-S / E-W quadrant boundary seams.
    """
    foot = np.asarray(footprint, dtype=bool)
    ys, xs = np.nonzero(foot)
    if ys.size == 0:
        return np.zeros(foot.shape, dtype=np.int8)
    y_mid = float(np.median(ys))
    x_mid = float(np.median(xs))
    sy = max(float(np.std(ys)), 1.0)
    sx = max(float(np.std(xs)), 1.0)

    yy, xx = np.meshgrid(
        np.arange(foot.shape[0], dtype=np.float32),
        np.arange(foot.shape[1], dtype=np.float32),
        indexing="ij",
    )
    u = (yy - np.float32(y_mid)) / np.float32(sy) + (xx - np.float32(x_mid)) / np.float32(sx)
    v = (yy - np.float32(y_mid)) / np.float32(sy) - (xx - np.float32(x_mid)) / np.float32(sx)
    wedges = ((u >= 0.0).astype(np.int8) * 2 + (v >= 0.0).astype(np.int8)).astype(np.int8)
    return wedges


def _zscore_valid(arr: np.ndarray, valid: np.ndarray) -> np.ndarray:
    c = _clean_valid(arr, valid).astype(np.float32)
    v = c[valid]
    if v.size == 0:
        return np.zeros_like(c, dtype=np.float32)
    med = float(np.median(v))
    iqr = float(np.percentile(v, 75.0) - np.percentile(v, 25.0))
    scale = max(iqr / 1.349, float(np.std(v)), 1e-5)
    out = np.where(valid, np.clip((c - np.float32(med)) / np.float32(scale), -6.0, 6.0), 0.0)
    return out.astype(np.float32)


def _nematic_strike_vectors(field: np.ndarray, valid: np.ndarray, sigma_grad: float = 1.2, sigma_ten: float = 3.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute spin-2 nematic structure-tensor coherence and headless strike tangent (ty, tx)."""
    u = gaussian_filter(_clean_valid(field, valid).astype(np.float32), sigma=float(sigma_grad))
    gy, gx = np.gradient(u)
    jxx = gaussian_filter((gx * gx).astype(np.float32), sigma=float(sigma_ten))
    jyy = gaussian_filter((gy * gy).astype(np.float32), sigma=float(sigma_ten))
    jxy = gaussian_filter((gx * gy).astype(np.float32), sigma=float(sigma_ten))
    tr = jxx + jyy + np.float32(1e-10)
    disc = np.sqrt(np.maximum((jxx - jyy) ** 2 + 4.0 * jxy * jxy, 0.0)).astype(np.float32)
    coh = np.where(valid, np.clip(disc / tr, 0.0, 1.0), 0.0).astype(np.float32)
    # Principal gradient normal angle phi = 0.5 * atan2(2*Jxy, Jxx - Jyy);
    # Strike tangent is perpendicular to principal gradient normal: (-sin(phi), cos(phi))
    two_phi = np.arctan2(2.0 * jxy, jxx - jyy)
    phi = np.float32(0.5) * two_phi
    nx = np.cos(phi).astype(np.float32)
    ny = np.sin(phi).astype(np.float32)
    ty = (-nx).astype(np.float32)
    tx = ny.astype(np.float32)
    return coh, ty, tx


def compute_salem_seismo_stack(
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
) -> dict[str, np.ndarray | dict]:
    """Compute the 26-channel zero-catalogue SALEMSEISMO stack with <1.5 GiB RSS."""
    foot = np.asarray(footprint, dtype=bool)
    h, w = foot.shape
    n_foot = int(foot.sum())

    if out_npy_path is not None:
        X_out: np.ndarray = np.lib.format.open_memmap(
            out_npy_path, mode="w+", dtype=np.float32, shape=(n_foot, len(FEATURE_NAMES))
        )
    else:
        X_out = np.empty((n_foot, len(FEATURE_NAMES)), dtype=np.float32)

    with rasterio.open(training_features_tif) as src:
        assert_training_band_tags(src)
        transform = src.transform
        b01_mag_anom = src.read(1).astype(np.float32)
        b02_rtp = src.read(2).astype(np.float32)
        b03_tmi_hg = src.read(3).astype(np.float32)
        b04_geod_2nd = src.read(4).astype(np.float32)
        b06_tc = src.read(6).astype(np.float32)
        b07_shear = src.read(7).astype(np.float32)
        b08_dilate = src.read(8).astype(np.float32)
        b09_tmi_vg = src.read(9).astype(np.float32)
        b10_deq = src.read(10).astype(np.float32)
        b11_grav_vg = src.read(11).astype(np.float32)
        b12_det_elev = src.read(12).astype(np.float32)
        b13_grav_anom = src.read(13).astype(np.float32)
        b14_tmi = src.read(14).astype(np.float32)
        b15_depth_base = src.read(15).astype(np.float32)
        b16_ieq = src.read(16).astype(np.float32)
        b17_cond = src.read(17).astype(np.float32)
        b18_grav_hg = src.read(18).astype(np.float32)
        b19_elev_slope = src.read(19).astype(np.float32)

    valid = (
        foot
        & np.isfinite(b02_rtp)
        & np.isfinite(b12_det_elev)
        & np.isfinite(b13_grav_anom)
        & np.isfinite(b15_depth_base)
    )

    # Regional updip footwall normal n_updip and strike tangent
    b_clean = np.clip(_clean_valid(b15_depth_base, valid), 0.0, 5000.0).astype(np.float32)
    log_b = np.log1p(b_clean).astype(np.float32)
    dby_m, dbx_m = _grad_xy(log_b, valid, sigma=5.0)
    gy_m, gx_m = _grad_xy(b13_grav_anom, valid, sigma=5.0)
    ey_m, ex_m = _grad_xy(b12_det_elev, valid, sigma=4.5)
    uy = (
        -0.45 * (dby_m / (np.hypot(dby_m, dbx_m) + np.float32(1e-6)))
        + 0.35 * (gy_m / (np.hypot(gy_m, gx_m) + np.float32(1e-6)))
        + 0.20 * (ey_m / (np.hypot(ey_m, ex_m) + np.float32(1e-6)))
    )
    ux = (
        -0.45 * (dbx_m / (np.hypot(dby_m, dbx_m) + np.float32(1e-6)))
        + 0.35 * (gx_m / (np.hypot(gy_m, gx_m) + np.float32(1e-6)))
        + 0.20 * (ex_m / (np.hypot(ey_m, ex_m) + np.float32(1e-6)))
    )
    umag = np.hypot(uy, ux) + np.float32(1e-6)
    ny_up = (uy / umag).astype(np.float32)
    nx_up = (ux / umag).astype(np.float32)
    ty_reg = (-nx_up).astype(np.float32)
    tx_reg = ny_up.astype(np.float32)
    del dby_m, dbx_m, gy_m, gx_m, ey_m, ex_m, uy, ux, umag

    # ---- Family 1: Shallow Concealed Salem Magnetic Contact & Remanent Demag (s01..s07) ----
    with rasterio.open(geodawn_ext_tif) as gext:
        ext_thk = _decode_u8_band(gext, 1) if "q_hi" in gext.tags(1) else gext.read(1).astype(np.float32)
        ext_uk = _decode_u8_band(gext, 2) if "q_hi" in gext.tags(2) else gext.read(2).astype(np.float32)
        ext_uth = _decode_u8_band(gext, 3) if "q_hi" in gext.tags(3) else gext.read(3).astype(np.float32)
        ext_tmi150 = _decode_u8_band(gext, 4) if "q_hi" in gext.tags(4) else gext.read(4).astype(np.float32)

    tc_clean = _clean_valid(b06_tc, valid).astype(np.float32)
    tc_med = float(np.median(tc_clean[valid]))
    tc_centered = tc_clean - np.float32(tc_med)
    tc_iqr = max(float(np.percentile(np.abs(tc_centered[valid]), 70.0)), 1e-4)
    tcy, tcx = _grad_xy(tc_centered, valid, sigma=1.4)
    tc_grad = np.hypot(tcy, tcx).astype(np.float32)
    tc_grad_med = max(float(np.median(tc_grad[valid])), 1e-5)

    hg_m = np.maximum(_clean_valid(b03_tmi_hg, valid), 0.0).astype(np.float32)
    vg_m = _clean_valid(b09_tmi_vg, valid).astype(np.float32)
    analytic_mag = np.hypot(hg_m, vg_m).astype(np.float32)
    am_p70 = max(float(np.percentile(analytic_mag[valid], 70.0)), 1e-4)

    # Upward-continued survival gate (rejects surficial boulder clutter)
    z_tmi150 = _zscore_valid(ext_tmi150, valid)
    z_rtp = _zscore_valid(b02_rtp, valid)
    t150_y, t150_x = _grad_xy(z_tmi150, valid, sigma=1.8)
    t150_grad = _sat(np.hypot(t150_y, t150_x), 0.45)
    del t150_y, t150_x, ext_tmi150

    salem_zero = np.exp(-0.5 * ((tc_centered / np.float32(0.85 * tc_iqr)) ** 2)).astype(np.float32)
    s01_salem = np.where(
        valid,
        np.clip(
            salem_zero
            * _sat(tc_grad, 1.55 * tc_grad_med)
            * (0.35 + 0.65 * _sat(analytic_mag, 1.25 * am_p70))
            * (0.45 + 0.55 * t150_grad),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    del tc_clean, tc_centered, tcy, tcx, tc_grad, salem_zero, t150_grad

    am_meso = mesoscale_zscore( np.log1p(analytic_mag), valid, sigma_px=28.0, eps=0.10 )
    coh_am = structure_tensor_coherence(np.log1p(analytic_mag), valid, deriv_sigma=1.2, tensor_sigma=2.5)
    s02_analytic_crest = np.where(
        valid,
        np.clip((1.0 / (1.0 + np.exp(-1.15 * am_meso))) * coh_am, 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del analytic_mag, am_meso, coh_am

    # Hydrothermal magnetite-destruction trough (-tmi_vg > 0 inside tmi_hg shoulders + Grauch residual)
    vg_neg = np.maximum(-vg_m, 0.0).astype(np.float32)
    vg_p75 = max(float(np.percentile(vg_neg[valid], 75.0)), 1e-4)
    hg_sh = gaussian_filter(hg_m, sigma=2.4).astype(np.float32)
    hg_p70 = max(float(np.percentile(hg_sh[valid], 70.0)), 1e-4)
    grauch_demag = np.maximum(z_tmi150 - z_rtp, 0.0).astype(np.float32)
    s03_hydro_trough = np.where(
        valid,
        np.clip(
            _sat(vg_neg, 1.40 * vg_p75)
            * (0.35 + 0.65 * _sat(hg_sh, 1.20 * hg_p70))
            * (0.40 + 0.60 * _sat(grauch_demag, 0.95)),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    del hg_m, vg_m, vg_neg, hg_sh, grauch_demag, z_tmi150

    # Koenigsberger remanent magnetization phase discordance (Band 1 mag_anom vs Band 2 rtp)
    z_mag = _zscore_valid(b01_mag_anom, valid)
    my1, mx1 = _grad_xy(z_mag, valid, sigma=1.6)
    ry1, rx1 = _grad_xy(z_rtp, valid, sigma=1.6)
    rem_diff = np.hypot(my1 - ry1, mx1 - rx1).astype(np.float32)
    coh_mag = structure_tensor_coherence(z_mag - z_rtp, valid, deriv_sigma=1.2, tensor_sigma=2.6)
    rd_p75 = max(float(np.percentile(rem_diff[valid], 75.0)), 1e-4)
    s04_remanent = np.where(
        valid,
        np.clip(_sat(rem_diff, 1.45 * rd_p75) * (0.35 + 0.65 * coh_mag), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del b01_mag_anom, z_mag, my1, mx1, rem_diff, coh_mag

    # TMI (Band 14) vs RTP (Band 2) cross-strike dipole asymmetry
    z_tmi = _zscore_valid(b14_tmi, valid)
    ty14, tx14 = _grad_xy(z_tmi, valid, sigma=1.8)
    dipole_asym = np.abs((tx14 - rx1) * nx_up + (ty14 - ry1) * ny_up).astype(np.float32)
    da_p75 = max(float(np.percentile(dipole_asym[valid], 75.0)), 1e-4)
    s05_dipole = np.where(valid, _sat(dipole_asym, 1.50 * da_p75), 0.0).astype(np.float32)
    del b14_tmi, b02_rtp, z_tmi, z_rtp, ty14, tx14, ry1, rx1, dipole_asym

    # Depth-deconfounded MT lateral conductivity wall (Band 17 residualized on log depth Band 15)
    cond_log = np.log1p(np.maximum(_clean_valid(b17_cond, valid), 0.0)).astype(np.float32)
    bv = log_b[valid]
    cv = cond_log[valid]
    bz = (log_b - np.float32(bv.mean())) / np.float32(bv.std() + 1e-5)
    design = np.column_stack([np.ones_like(bv), bz[valid], (bz[valid] ** 2)])
    coef, *_ = np.linalg.lstsq(design, cv, rcond=None)
    mt_resid = np.where(valid, cond_log - (coef[0] + coef[1] * bz + coef[2] * (bz * bz)), 0.0).astype(np.float32)
    mty, mtx = _grad_xy(mt_resid, valid, sigma=1.8)
    mt_step = np.hypot(mty, mtx).astype(np.float32)
    mt_p75 = max(float(np.percentile(mt_step[valid], 75.0)), 0.03)
    vg_g = _clean_valid(b11_grav_vg, valid).astype(np.float32)
    vg_iqr = max(float(np.percentile(np.abs(vg_g[valid]), 75.0)), 1e-5)
    vg_zero = np.exp(-0.5 * ((vg_g / np.float32(1.55 * vg_iqr)) ** 2)).astype(np.float32)
    s06_mt_wall = np.where(
        valid,
        np.clip(_sat(mt_step, 1.60 * mt_p75) * (0.45 + 0.55 * vg_zero), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del b17_cond, cond_log, bv, cv, bz, design, mt_resid, mty, mtx, mt_step

    s07_salem_mt_lock = np.where(
        valid,
        np.clip(np.sqrt(np.maximum(s01_salem, s04_remanent) * np.maximum(s03_hydro_trough, s06_mt_wall)), 0.0, 1.0),
        0.0,
    ).astype(np.float32)

    X_out[:, 0] = s01_salem[foot]
    X_out[:, 1] = s02_analytic_crest[foot]
    X_out[:, 2] = s03_hydro_trough[foot]
    X_out[:, 3] = s04_remanent[foot]
    X_out[:, 4] = s05_dipole[foot]
    X_out[:, 5] = s06_mt_wall[foot]
    X_out[:, 6] = s07_salem_mt_lock[foot]

    l_mag_salem = np.where(
        valid,
        np.clip(0.42 * s01_salem + 0.22 * s03_hydro_trough + 0.18 * s06_mt_wall + 0.18 * s07_salem_mt_lock, 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del s02_analytic_crest, s04_remanent, s05_dipole

    # ---- Family 2: Walker Lane & CNSB Seismo-Geodetic Transtensional Corridor (s08..s12) ----
    deq_clean = np.maximum(_clean_valid(b10_deq, valid), 0.0).astype(np.float32)
    ieq_clean = np.maximum(_clean_valid(b16_ieq, valid), 0.0).astype(np.float32)
    deq_scale = max(float(np.percentile(deq_clean[valid], 35.0)), 1e-3)
    eq_prox = np.exp(-deq_clean / np.float32(deq_scale)).astype(np.float32)
    ieq_log = np.log1p(ieq_clean / max(float(np.median(ieq_clean[valid])) + 1e-5, 1e-5)).astype(np.float32)
    eq_raw = (eq_prox * _sat(ieq_log, float(np.percentile(ieq_log[valid], 75.0)) + 1e-4)).astype(np.float32)
    eq_meso = mesoscale_zscore(eq_raw, valid, sigma_px=38.0, eps=0.05)
    s08_seismic_corridor = np.where(
        valid,
        np.clip(0.55 * eq_raw + 0.45 / (1.0 + np.exp(-1.10 * eq_meso)), 0.0, 1.0),
        0.0,
    ).astype(np.float32)

    eqy, eqx = _grad_xy(eq_prox, valid, sigma=1.8)
    eq_edge = np.hypot(eqy, eqx).astype(np.float32)
    eqe_p75 = max(float(np.percentile(eq_edge[valid], 75.0)), 1e-5)
    s12_seismic_edge = np.where(valid, _sat(eq_edge, 1.55 * eqe_p75), 0.0).astype(np.float32)
    del b10_deq, b16_ieq, deq_clean, ieq_clean, eq_prox, ieq_log, eq_raw, eq_meso, eqy, eqx, eq_edge

    shr_z = mesoscale_zscore(b07_shear, valid, sigma_px=42.0, eps=0.15)
    inv_z = mesoscale_zscore(b04_geod_2nd, valid, sigma_px=42.0, eps=0.15)
    dil_z = mesoscale_zscore(b08_dilate, valid, sigma_px=42.0, eps=0.15)
    sy_g, sx_g = _grad_xy(_clean_valid(b07_shear, valid), valid, sigma=2.5)
    sgrad = np.hypot(sy_g, sx_g).astype(np.float32)
    sg_p75 = max(float(np.percentile(sgrad[valid], 75.0)), 1e-6)

    s09_walker_shear = np.where(
        valid,
        np.clip(
            (1.0 / (1.0 + np.exp(-0.95 * (0.62 * shr_z + 0.38 * inv_z))))
            * (0.55 + 0.45 * _sat(sgrad, 1.40 * sg_p75)),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    s10_transtension = np.where(
        valid,
        np.clip(
            (1.0 / (1.0 + np.exp(-1.05 * dil_z))) * (0.45 + 0.55 * s09_walker_shear),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    s11_seismo_geod = np.where(
        valid,
        np.clip(np.sqrt(s08_seismic_corridor * (0.65 * s09_walker_shear + 0.35 * s10_transtension)), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del b04_geod_2nd, b07_shear, b08_dilate, shr_z, inv_z, dil_z, sy_g, sx_g, sgrad

    X_out[:, 7] = s08_seismic_corridor[foot]
    X_out[:, 8] = s09_walker_shear[foot]
    X_out[:, 9] = s10_transtension[foot]
    X_out[:, 10] = s11_seismo_geod[foot]
    X_out[:, 11] = s12_seismic_edge[foot]

    l_seismo_walker = np.where(
        valid,
        np.clip(0.45 * s11_seismo_geod + 0.30 * s12_seismic_edge + 0.25 * s09_walker_shear, 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del s08_seismic_corridor, s09_walker_shear, s10_transtension, s11_seismo_geod, s12_seismic_edge
    gc.collect()

    # ---- Family 3: Signed 10 m Piedmont Toe-Concavity, Bipolar Chi & Flexural Toe (s13..s19) ----
    b19_c = _clean_valid(b19_elev_slope, valid)
    p99_b19 = float(np.percentile(b19_c[valid], 99.0)) if valid.any() else 1.0
    slope_100m_deg = (
        np.rad2deg(np.arctan(np.maximum(b19_c, 0.0))).astype(np.float32)
        if p99_b19 <= 2.5
        else np.maximum(b19_c, 0.0).astype(np.float32)
    )
    del b19_elev_slope, b19_c

    with rasterio.open(topo_10m_tif) as ds10:
        s10_p90 = _decode_u8_band(ds10, 1)
        s10_max = _decode_u8_band(ds10, 2)
        steep10 = _decode_u8_band(ds10, 3)
        s10_std = _decode_u8_band(ds10, 4)
        rel10 = _decode_u8_band(ds10, 5)
        asp10_coh = _decode_u8_band(ds10, 7)
        hs10_lin = _decode_u8_band(ds10, 8)
        dem10_mean = _decode_u8_band(ds10, 9)

    with rasterio.open(dem10_chi_tif) as dschi:
        chi_step_max = dschi.read(1).astype(np.float32)
        chi_step_min = dschi.read(2).astype(np.float32)
        ksn_raw = dschi.read(3).astype(np.float32)
        area_raw = dschi.read(4).astype(np.float32)

    chi_ok = valid & (chi_step_max > -32000) & (area_raw > -32000)
    log10_area = np.where(chi_ok, area_raw * np.float32(0.001), 4.0).astype(np.float32)
    non_river_gate = np.clip((np.float32(6.5) - log10_area) / np.float32(1.2), 0.15, 1.0).astype(np.float32)

    # Signed updip break-in-slope concavity: n_updip . grad(s10_p90) > 0 at piedmont scarp toe
    gs10_y, gs10_x = _grad_xy(s10_p90, valid, sigma=1.1)
    updip_concav = np.maximum(gs10_y * ny_up + gs10_x * nx_up, 0.0).astype(np.float32)
    pied_band = (
        np.exp(-0.5 * (((slope_100m_deg - np.float32(5.5)) / np.float32(6.5)) ** 2))
        * np.clip(slope_100m_deg / np.float32(1.2), 0.20, 1.0)
    ).astype(np.float32)

    # Lake Lahontan (~1,330 m) horizontal shoreline bench deconfounder
    zy10, zx10 = _grad_xy(dem10_mean, valid, sigma=2.4)
    cross_sin = np.abs(
        (gs10_x * zy10 - gs10_y * zx10)
        / ((np.hypot(gs10_y, gs10_x) + np.float32(1e-5)) * (np.hypot(zy10, zx10) + np.float32(1e-5)))
    )
    lahontan_pen = (
        np.float32(1.0)
        - np.float32(0.55)
        * np.exp(-0.5 * (((dem10_mean - np.float32(1330.0)) / np.float32(55.0)) ** 2))
        * (np.float32(1.0) - cross_sin)
    ).astype(np.float32)
    del gs10_y, gs10_x, zy10, zx10, dem10_mean, cross_sin

    uc_p75 = max(float(np.percentile(updip_concav[valid], 75.0)), 0.15)
    std_p75 = max(float(np.percentile(s10_std[valid], 75.0)), 0.50)
    s13_signed_toe = np.where(
        valid,
        np.clip(
            _sat(updip_concav, 1.50 * uc_p75)
            * (0.35 + 0.65 * _sat(s10_std, 1.35 * std_p75))
            * (0.45 + 0.55 * np.clip(steep10 * 2.5, 0.0, 1.0))
            * pied_band
            * non_river_gate
            * lahontan_pen,
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)

    ex_max = subpixel_scarp_excess(s10_max, slope_100m_deg, valid)
    rel_p75 = max(float(np.percentile(rel10[valid], 75.0)), 1.0)
    lin10 = np.clip(asp10_coh * hs10_lin / 0.22, 0.0, 1.0).astype(np.float32)
    s14_relief_excess = np.where(
        valid,
        np.clip(
            (0.52 * _sat(ex_max, 0.85) + 0.48 * _sat(rel10, 1.45 * rel_p75))
            * (0.35 + 0.65 * lin10)
            * (0.35 + 0.65 * pied_band)
            * lahontan_pen,
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    del s10_p90, s10_max, steep10, s10_std, rel10, asp10_coh, hs10_lin, updip_concav, ex_max, lin10, lahontan_pen

    yy, xx = np.meshgrid(
        np.arange(h, dtype=np.float32),
        np.arange(w, dtype=np.float32),
        indexing="ij",
    )

    chi_pos = np.where(chi_ok, np.log1p(np.maximum(chi_step_max, 0.0) * 0.001), 0.0).astype(np.float32)
    ksn_pos = np.where(
        chi_ok & (ksn_raw > -32000),
        np.log1p(np.maximum(ksn_raw, 0.0)) * np.clip(log10_area - 4.0, 0.0, 3.5),
        0.0,
    ).astype(np.float32)
    syn_local = np.where(
        valid,
        0.62 * _sat(gaussian_filter(chi_pos, 1.4), 0.24) + 0.38 * _sat(gaussian_filter(ksn_pos, 1.4), 2.10),
        0.0,
    ).astype(np.float32)
    sp = bilinear_sample_2d(syn_local, yy + 3.5 * ty_reg, xx + 3.5 * tx_reg, valid)
    sm = bilinear_sample_2d(syn_local, yy - 3.5 * ty_reg, xx - 3.5 * tx_reg, valid)
    s15_chi_syn = np.where(valid, np.clip(0.50 * syn_local + 0.30 * 0.5 * (sp + sm) + 0.20 * np.sqrt(sp * sm), 0.0, 1.0), 0.0).astype(np.float32)
    del chi_step_max, ksn_raw, chi_pos, ksn_pos, syn_local, sp, sm

    # Untried negative chi-step (antithetic graben ponding / subsiding relay step_min_x1000 < 0)
    anti_ok = chi_ok & (chi_step_min > -32000)
    chi_neg = np.where(anti_ok, np.log1p(np.maximum(-chi_step_min, 0.0) * 0.001), 0.0).astype(np.float32)
    anti_local = np.where(valid, _sat(gaussian_filter(chi_neg, 1.5), 0.20) * non_river_gate, 0.0).astype(np.float32)
    ap = bilinear_sample_2d(anti_local, yy + 3.5 * ty_reg, xx + 3.5 * tx_reg, valid)
    am = bilinear_sample_2d(anti_local, yy - 3.5 * ty_reg, xx - 3.5 * tx_reg, valid)
    s16_chi_anti = np.where(valid, np.clip(0.52 * anti_local + 0.48 * 0.5 * (ap + am), 0.0, 1.0), 0.0).astype(np.float32)
    del chi_step_min, area_raw, chi_ok, anti_ok, chi_neg, anti_local, ap, am, log10_area, non_river_gate

    s17_bipolar_lock = np.where(
        valid,
        np.clip(np.sqrt(np.maximum(s13_signed_toe, s14_relief_excess) * np.maximum(s15_chi_syn, s16_chi_anti)), 0.0, 1.0),
        0.0,
    ).astype(np.float32)

    # Updip flexural basement toe inflection (damped on steep exposed granite so it stays orthogonal to gravity worms)
    s_adapt = compute_adaptive_dip_offset_px(b15_depth_base, b18_grav_hg, b11_grav_vg, valid, min_shift_px=2.0, max_shift_px=5.8)
    dby2, dbx2 = _grad_xy(log_b, valid, sigma=2.0)
    db_step = np.hypot(dby2, dbx2).astype(np.float32)
    db_p75 = max(float(np.percentile(db_step[valid], 75.0)), 1e-5)
    gh_c = np.maximum(_clean_valid(b18_grav_hg, valid), 0.0).astype(np.float32)
    gh_p75 = max(float(np.percentile(gh_c[valid], 75.0)), 1e-5)
    toe_seed = np.where(
        valid,
        (0.52 * _sat(db_step, 1.40 * db_p75) + 0.48 * _sat(gh_c, 1.45 * gh_p75) * (0.45 + 0.55 * vg_zero)),
        0.0,
    ).astype(np.float32)
    toe_proj = bilinear_sample_2d(toe_seed, yy - s_adapt * ny_up, xx - s_adapt * nx_up, valid)
    non_granite_gate = np.clip((np.float32(22.0) - slope_100m_deg) / np.float32(14.0), 0.25, 1.0).astype(np.float32)
    s18_flex_toe = np.where(valid, np.clip(toe_proj * non_granite_gate, 0.0, 1.0), 0.0).astype(np.float32)
    s19_basin_ctx = np.where(valid, np.clip(log_b / np.float32(8.0), 0.0, 1.0), 0.0).astype(np.float32)
    del s_adapt, dby2, dbx2, db_step, gh_c, toe_seed, toe_proj, non_granite_gate, pied_band, slope_100m_deg, vg_g, vg_zero
    del b11_grav_vg, b12_det_elev, b13_grav_anom, b15_depth_base, b18_grav_hg, b_clean

    X_out[:, 12] = s13_signed_toe[foot]
    X_out[:, 13] = s14_relief_excess[foot]
    X_out[:, 14] = s15_chi_syn[foot]
    X_out[:, 15] = s16_chi_anti[foot]
    X_out[:, 16] = s17_bipolar_lock[foot]
    X_out[:, 17] = s18_flex_toe[foot]
    X_out[:, 18] = s19_basin_ctx[foot]

    l_piedmont_chi = np.where(
        valid,
        np.clip(0.36 * s13_signed_toe + 0.24 * s14_relief_excess + 0.22 * np.maximum(s15_chi_syn, s16_chi_anti) + 0.18 * s18_flex_toe, 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del s14_relief_excess, s15_chi_syn, s16_chi_anti, s17_bipolar_lock, s19_basin_ctx
    gc.collect()

    # ---- Family 4: GeoDAWN Th/K-U/Th Alteration Curtain, Sinter Valve & Nematic Bridge (s20..s26) ----
    # Low Th/K (= potassic/illite alteration) residualized on log_b
    thk_z = _zscore_valid(ext_thk, valid)
    potassic_low = np.maximum(-thk_z, 0.0).astype(np.float32)
    tky, tkx = _grad_xy(thk_z, valid, sigma=1.6)
    tk_step = np.hypot(tky, tkx).astype(np.float32)
    tk_p75 = max(float(np.percentile(tk_step[valid], 75.0)), 1e-4)
    s20_potassic_thk = np.where(
        valid,
        np.clip(0.55 * _sat(potassic_low, 1.15) + 0.45 * _sat(tk_step, 1.45 * tk_p75), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del ext_thk, thk_z, potassic_low, tky, tkx, tk_step

    uth_z = _zscore_valid(ext_uth, valid)
    uk_z = _zscore_valid(ext_uk, valid)
    redox_pos = np.maximum(0.60 * uth_z + 0.40 * uk_z, 0.0).astype(np.float32)
    ruy, rux = _grad_xy(uth_z, valid, sigma=1.8)
    ru_step = np.hypot(ruy, rux).astype(np.float32)
    ru_p75 = max(float(np.percentile(ru_step[valid], 75.0)), 1e-4)
    s21_redox_uth = np.where(
        valid,
        np.clip(0.50 * _sat(redox_pos, 1.15) + 0.50 * _sat(ru_step, 1.45 * ru_p75), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del ext_uth, ext_uk, uth_z, uk_z, redox_pos, ruy, rux, ru_step, log_b

    with rasterio.open(rad_tif) as rds:
        rad_k = rds.read(1).astype(np.float32)
        rad_th = rds.read(2).astype(np.float32)
        rad_tc = rds.read(4).astype(np.float32)
    ky, kx = _grad_xy(_zscore_valid(rad_k, valid), valid, sigma=1.7)
    thy, thx = _grad_xy(_zscore_valid(rad_th, valid), valid, sigma=1.7)
    tcy2, tcx2 = _grad_xy(_zscore_valid(rad_tc, valid), valid, sigma=1.7)
    rad_step = (0.38 * np.hypot(ky, kx) + 0.32 * np.hypot(thy, thx) + 0.30 * np.hypot(tcy2, tcx2)).astype(np.float32)
    rs_p75 = max(float(np.percentile(rad_step[valid], 75.0)), 1e-4)
    s22_rad_contact = np.where(valid, _sat(rad_step, 1.50 * rs_p75), 0.0).astype(np.float32)
    del rad_k, rad_th, rad_tc, ky, kx, thy, thx, tcy2, tcx2, rad_step

    # Spin-2 nematic structure-tensor strike vector from combined geophysical/geomorphic lineaments
    base_uni = (0.34 * l_mag_salem + 0.22 * l_seismo_walker + 0.44 * l_piedmont_chi).astype(np.float32)
    coh_nem, ty_nem, tx_nem = _nematic_strike_vectors(base_uni, valid, sigma_grad=1.2, sigma_ten=3.2)

    paleo_imp, paleo_stats = _rasterize_paleo_vents(paleo_zip, transform, (h, w), valid)
    probe_imp, probe_stats = _rasterize_2m_temperature_probes(probe_2m_zip, transform, (h, w), valid)
    spring_imp, spring_stats = _rasterize_active_thermal_springs(gdr_wellspring_csv, (h, w), valid)
    vent_seed = np.where(
        valid,
        gaussian_filter((1.35 * paleo_imp + 1.05 * probe_imp + 0.80 * spring_imp).astype(np.float32), sigma=2.2),
        0.0,
    ).astype(np.float32)
    del paleo_imp, probe_imp, spring_imp

    vp4 = bilinear_sample_2d(vent_seed, yy + 4.0 * ty_nem, xx + 4.0 * tx_nem, valid)
    vm4 = bilinear_sample_2d(vent_seed, yy - 4.0 * ty_nem, xx - 4.0 * tx_nem, valid)
    vp9 = bilinear_sample_2d(vent_seed, yy + 9.0 * ty_nem, xx + 9.0 * tx_nem, valid)
    vm9 = bilinear_sample_2d(vent_seed, yy - 9.0 * ty_nem, xx - 9.0 * tx_nem, valid)
    v_adv = (0.44 * vent_seed + 0.34 * 0.5 * (vp4 + vm4) + 0.22 * 0.5 * (vp9 + vm9)).astype(np.float32)
    vp95 = max(float(np.percentile(v_adv[valid], 98.5)), 0.015)
    s23_sinter_probe = np.where(valid, _sat(v_adv, 0.90 * vp95), 0.0).astype(np.float32)
    del vent_seed, vp4, vm4, vp9, vm9, v_adv

    s24_hydro_curtain = np.where(
        valid,
        np.clip(
            0.40 * np.sqrt(np.maximum(s20_potassic_thk, s21_redox_uth) * np.maximum(s06_mt_wall, s03_hydro_trough))
            + 0.36 * s23_sinter_probe * (0.40 + 0.60 * np.maximum(s20_potassic_thk, s06_mt_wall))
            + 0.24 * s22_rad_contact,
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)

    # Nematic tensor geodesic bridge (+/- 3 px and +/- 6 px along headless nematic strike)
    np3 = bilinear_sample_2d(base_uni, yy + 3.0 * ty_nem, xx + 3.0 * tx_nem, valid)
    nm3 = bilinear_sample_2d(base_uni, yy - 3.0 * ty_nem, xx - 3.0 * tx_nem, valid)
    np6 = bilinear_sample_2d(base_uni, yy + 6.0 * ty_nem, xx + 6.0 * tx_nem, valid)
    nm6 = bilinear_sample_2d(base_uni, yy - 6.0 * ty_nem, xx - 6.0 * tx_nem, valid)
    s25_nematic_bridge = np.where(
        valid,
        np.clip(
            (0.45 * base_uni + 0.30 * 0.5 * (np3 + nm3) + 0.25 * np.sqrt(np.maximum(np3, np6) * np.maximum(nm3, nm6)))
            * (0.45 + 0.55 * coh_nem),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    del yy, xx, ty_reg, tx_reg, ny_up, nx_up, ty_nem, tx_nem, coh_nem, base_uni, np3, nm3, np6, nm6

    # Quad-regime second-best corroboration across the 4 orthogonal physical families
    # Compute 2nd-largest of 4 values (l_mag_salem, l_seismo_walker, l_piedmont_chi, s24_hydro_curtain)
    stack4 = np.stack([l_mag_salem[foot], l_seismo_walker[foot], l_piedmont_chi[foot], s24_hydro_curtain[foot]], axis=1)
    part4 = np.partition(stack4, 2, axis=1)
    s26_second_best_foot = np.clip(part4[:, 2], 0.0, 1.0).astype(np.float32)
    s26_second_best = np.zeros((h, w), dtype=np.float32)
    s26_second_best[foot] = s26_second_best_foot
    del stack4, part4

    X_out[:, 19] = s20_potassic_thk[foot]
    X_out[:, 20] = s21_redox_uth[foot]
    X_out[:, 21] = s22_rad_contact[foot]
    X_out[:, 22] = s23_sinter_probe[foot]
    X_out[:, 23] = s24_hydro_curtain[foot]
    X_out[:, 24] = s25_nematic_bridge[foot]
    X_out[:, 25] = s26_second_best_foot
    if hasattr(X_out, "flush"):
        X_out.flush()

    del s01_salem, s03_hydro_trough, s06_mt_wall, s07_salem_mt_lock
    del s13_signed_toe, s18_flex_toe
    del s20_potassic_thk, s21_redox_uth, s22_rad_contact, s23_sinter_probe
    gc.collect()

    return dict(
        X_foot=X_out,
        valid=valid,
        L_mag_salem=l_mag_salem,
        L_seismo_walker=l_seismo_walker,
        L_piedmont_chi=l_piedmont_chi,
        L_hydro_curtain=s24_hydro_curtain,
        L_nematic_bridge=s25_nematic_bridge,
        s26_corrob=s26_second_best,
        vent_audit=dict(paleo_vents=paleo_stats, probe_2m=probe_stats, wellspring=spring_stats),
    )


def fit_predict_salem_seismo_dual_oof(
    X_foot: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    diamond_wedge: np.ndarray,
    label_mask: np.ndarray,
    *,
    excluded_mask: np.ndarray | None = None,
    guard_px: int = 12,
    neg_buffer_px: float = 5.0,
    neg_pos_ratio: int = 4,
    seed: int = 20261026,
    max_iter: int = 190,
    w_full: float = 0.24,
    w_concealed: float = 0.42,
    w_debiased: float = 0.34,
    calib_weight_full: float = 0.40,
    calib_weight_branch: float = 0.82,
    power_gamma: float = 3.25,
) -> dict[str, np.ndarray]:
    """Fit Seam-Free Dual-Partition (0.5 * 4-Quadrant LOQO + 0.5 * 4-Wedge Diamond LODO)
    3-branch ensemble with 12 px (1.2 km) spatial guard buffer on every split.
    """
    valid_b = np.asarray(valid, dtype=bool) & np.asarray(footprint, dtype=bool)

    def _fit_partition(part_ids: np.ndarray, seed_off: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        pf = fit_single_loqo(
            X_foot, footprint, valid_b, part_ids, label_mask,
            feature_cols=None, excluded_mask=excluded_mask,
            guard_px=guard_px, neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio, seed=int(seed) + seed_off, max_iter=max_iter,
        )
        pc = fit_single_loqo(
            X_foot, footprint, valid_b, part_ids, label_mask,
            feature_cols=CONCEALED_BRANCH_INDICES, excluded_mask=excluded_mask,
            guard_px=guard_px, neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio, seed=int(seed) + seed_off + 1, max_iter=max_iter,
        )
        pd = fit_single_loqo(
            X_foot, footprint, valid_b, part_ids, label_mask,
            feature_cols=DEBIASED_PIEDMONT_INDICES, excluded_mask=excluded_mask,
            guard_px=guard_px, neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio, seed=int(seed) + seed_off + 2, max_iter=max_iter,
        )
        return pf, pc, pd

    pf_q, pc_q, pd_q = _fit_partition(quad, 0)
    pf_w, pc_w, pd_w = _fit_partition(diamond_wedge, 10)

    p_full = (np.float32(0.5) * (pf_q + pf_w)).astype(np.float32)
    p_conc = (np.float32(0.5) * (pc_q + pc_w)).astype(np.float32)
    p_deb = (np.float32(0.5) * (pd_q + pd_w)).astype(np.float32)

    raw_proba = (
        np.float32(w_full) * p_full
        + np.float32(w_concealed) * p_conc
        + np.float32(w_debiased) * p_deb
    ).astype(np.float32)

    p_full_cal = np.float32(0.5) * (
        calibrate_quadrant_probabilities(p_full, valid_b, quad, calib_weight=calib_weight_full, power_gamma=power_gamma)
        + calibrate_quadrant_probabilities(p_full, valid_b, diamond_wedge, calib_weight=calib_weight_full, power_gamma=power_gamma)
    )
    w_rest = max(float(w_concealed + w_debiased), 1e-6)
    p_rest = ((np.float32(w_concealed) * p_conc + np.float32(w_debiased) * p_deb) / np.float32(w_rest)).astype(np.float32)
    p_rest_cal = np.float32(0.5) * (
        calibrate_quadrant_probabilities(p_rest, valid_b, quad, calib_weight=calib_weight_branch, power_gamma=power_gamma)
        + calibrate_quadrant_probabilities(p_rest, valid_b, diamond_wedge, calib_weight=calib_weight_branch, power_gamma=power_gamma)
    )
    dualcal_proba = (np.float32(w_full) * p_full_cal + np.float32(w_rest) * p_rest_cal).astype(np.float32)

    return dict(
        p_full=p_full,
        p_concealed=p_conc,
        p_debiased=p_deb,
        raw_proba=raw_proba,
        dualcal_proba=dualcal_proba,
    )


def build_salem_seismo_crest_surface(
    proba_2d: np.ndarray,
    l_mag_salem: np.ndarray,
    l_seismo_walker: np.ndarray,
    l_piedmont_chi: np.ndarray,
    l_hydro_curtain: np.ndarray,
    l_nematic_bridge: np.ndarray,
    s26_corrob: np.ndarray,
    valid: np.ndarray,
    *,
    mag_salem_weight: float = 1.42,
    seismo_walker_weight: float = 1.24,
    piedmont_chi_weight: float = 1.30,
    hydro_curtain_weight: float = 1.28,
    nematic_weight: float = 1.16,
    corrob_boost: float = 0.55,
) -> dict[str, np.ndarray]:
    """Build quad-regime corroborated 1D crest surface and union directional ridge mask."""
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0), 0.0)

    e_mag = np.float32(mag_salem_weight) * np.asarray(l_mag_salem, dtype=np.float32)
    e_seis = np.float32(seismo_walker_weight) * np.asarray(l_seismo_walker, dtype=np.float32)
    e_pied = np.float32(piedmont_chi_weight) * np.asarray(l_piedmont_chi, dtype=np.float32)
    e_hyd = np.float32(hydro_curtain_weight) * np.asarray(l_hydro_curtain, dtype=np.float32)
    e_nem = np.float32(nematic_weight) * np.asarray(l_nematic_bridge, dtype=np.float32)
    e_line = np.maximum(e_mag, np.maximum(e_seis, np.maximum(e_pied, np.maximum(e_hyd, e_nem))))

    corrob_gate = np.float32(1.0) + np.float32(corrob_boost) * np.clip(
        np.asarray(s26_corrob, dtype=np.float32) / np.float32(0.20), 0.0, 1.30
    )
    s_crest = np.where(
        valid_b,
        p * (np.float32(0.12) + np.float32(0.88) * e_line) * corrob_gate,
        0.0,
    ).astype(np.float32)

    ridge_1d = (
        directional_ridge_1d(s_crest, valid_b)
        | directional_ridge_1d(np.where(valid_b, p * l_mag_salem, 0.0).astype(np.float32), valid_b)
        | directional_ridge_1d(np.where(valid_b, p * l_seismo_walker, 0.0).astype(np.float32), valid_b)
        | directional_ridge_1d(np.where(valid_b, p * l_piedmont_chi, 0.0).astype(np.float32), valid_b)
        | directional_ridge_1d(np.where(valid_b, p * l_hydro_curtain, 0.0).astype(np.float32), valid_b)
    )
    return dict(
        S_crest=s_crest,
        E_line=np.where(valid_b, e_line, 0.0).astype(np.float32),
        ridge_1d=ridge_1d,
    )


def celf_submodular_place(
    surface: np.ndarray,
    cand_mask: np.ndarray,
    n: int,
    *,
    min_dist_px: float = 2.8,
    power_eta: float = 1.35,
    cand_cap: int = 400_000,
    initial_coverage: np.ndarray | None = None,
    dot_amplitude: float = 1.0,
    require_full: bool = True,
) -> np.ndarray:
    """Exact Minoux (1978) Lazy-Greedy (CELF) Submodular 300 m Triangular-Kernel Placement.

    Maximizes monotone submodular expected weighted recall:
        F(P) = sum_g W(g) * max(C_0(g), max_{p in P} a * k(||g - p||))
    where W(g) = max(surface(g), 0) ** power_eta on valid crest domain,
    k(u) = max(0, 1 - u / 3.0) over the exact 25 nonzero integer offsets (|dy|,|dx| <= 2),
    and accepted dots obey strict pairwise Euclidean separation >= min_dist_px.

    Uses an exact 9x9 support-intersection dirty flag (`touched`): whenever no prior
    accepted dot lies within |dy|<=4, |dx|<=4 of a candidate (so their 5x5 kernels are
    disjoint), its initial convolved gain is bit-exact and accepted in O(1) without
    recomputing the 25-offset sum.
    """
    if not (0.0 < dot_amplitude <= 1.0):
        raise ValueError("dot_amplitude must lie in (0, 1]")
    surf = np.maximum(np.nan_to_num(np.asarray(surface, dtype=np.float32), nan=0.0), 0.0)
    cand = np.asarray(cand_mask, dtype=bool)
    if surf.shape != cand.shape:
        raise ValueError("surface and cand_mask shape mismatch")
    if n <= 0:
        return np.zeros(surf.shape, dtype=bool)

    s_max = float(surf[cand].max()) if cand.any() else 0.0
    if s_max > 0.0:
        w_grid = np.where(surf > 0.0, (surf / np.float32(s_max)) ** np.float32(power_eta), 0.0).astype(np.float32)
    else:
        w_grid = np.zeros_like(surf, dtype=np.float32)

    h, w = surf.shape
    pad = max(5, int(np.ceil(min_dist_px)) + 1)
    w_pad = np.zeros((h + 2 * pad, w + 2 * pad), dtype=np.float32)
    w_pad[pad : pad + h, pad : pad + w] = w_grid

    cov_pad = np.zeros((h + 2 * pad, w + 2 * pad), dtype=np.float32)
    touched = np.zeros((h + 2 * pad, w + 2 * pad), dtype=bool)
    if initial_coverage is not None:
        ic = np.clip(np.asarray(initial_coverage, dtype=np.float32), 0.0, 1.0)
        cov_pad[pad : pad + h, pad : pad + w] = ic
        # Mark 5x5 neighborhood around any nonzero initial coverage as touched
        iy, ix = np.nonzero(ic > 0.0)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                touched[iy + pad + dy, ix + pad + dx] = True

    # Initial marginal gain upper bound when cov == 0: dot_amplitude * (K_7 * W)
    init_gain_2d = (np.float32(dot_amplitude) * convolve(w_grid, KERNEL_300M_7X7, mode="constant")).astype(np.float32)

    ys, xs = np.nonzero(cand)
    gains0 = init_gain_2d[ys, xs]
    if ys.size > cand_cap:
        # Stable top-cand_cap selection
        part_idx = np.argpartition(-gains0, cand_cap)[:cand_cap]
        ys, xs, gains0 = ys[part_idx], xs[part_idx], gains0[part_idx]
    order = np.argsort(-gains0, kind="stable")
    ys = ys[order]
    xs = xs[order]
    gains0 = gains0[order]

    # Build min-heap of (-gain, tie_rank, step_evaluated, y, x)
    # Note: tie_rank = 0..M-1 preserves deterministic row-major tie breaking
    init_step = -1 if initial_coverage is not None else 0
    heap: list[tuple[float, int, int, int, int]] = [
        (-float(gains0[i]), int(i), init_step, int(ys[i]), int(xs[i]))
        for i in range(ys.size)
    ]
    heapq.heapify(heap)

    r_sep = int(np.floor(min_dist_px))
    sep_offs = [
        (dy, dx)
        for dy in range(-r_sep, r_sep + 1)
        for dx in range(-r_sep, r_sep + 1)
        if (dy * dy + dx * dx) < (min_dist_px * min_dist_px)
    ]

    occ_pad = np.zeros((h + 2 * pad, w + 2 * pad), dtype=bool)
    chosen = np.zeros((h, w), dtype=bool)
    amp = float(dot_amplitude)
    k_offs = KERNEL_300M_OFFSETS
    accepted = 0

    while heap and accepted < n:
        neg_g, tie_i, eval_step, y, x = heapq.heappop(heap)
        yp = y + pad
        xp = x + pad
        if occ_pad[yp, xp]:
            continue
        if eval_step < accepted and touched[yp, xp]:
            # Exact 25-offset marginal gain recomputation under current coverage
            g_cur = 0.0
            for dy, dx, kw in k_offs:
                new_c = amp * kw
                old_c = float(cov_pad[yp + dy, xp + dx])
                if new_c > old_c:
                    g_cur += float(w_pad[yp + dy, xp + dx]) * (new_c - old_c)
            # Peek next item in heap: if g_cur is still >= best upper bound, accept immediately!
            if heap and (-g_cur > heap[0][0]):
                heapq.heappush(heap, (-g_cur, tie_i, accepted, y, x))
                continue

        # Accept (y, x)!
        chosen[y, x] = True
        accepted += 1
        if accepted == n:
            break

        for dy, dx in sep_offs:
            occ_pad[yp + dy, xp + dx] = True
        for dy, dx, kw in k_offs:
            new_c = np.float32(amp * kw)
            if new_c > cov_pad[yp + dy, xp + dx]:
                cov_pad[yp + dy, xp + dx] = new_c
        touched[yp - 4 : yp + 5, xp - 4 : xp + 5] = True

    if accepted != n and require_full:
        raise ValueError(
            f"celf_submodular_place: placed {accepted} of {n} requested dots "
            f"(cand_cap={cand_cap}, min_dist_px={min_dist_px})"
        )
    return chosen


def celf_additive_tail_allocation(
    primary_dots: np.ndarray,
    surface: np.ndarray,
    eligible_mask: np.ndarray,
    *,
    n_tail_dots: int = 14346,
    min_dist_from_primary_px: float = 4.0,
    tail_min_dist_px: float = 3.8,
    tail_weight: float = 0.65,
    power_eta: float = 1.35,
    cand_cap: int = 500_000,
) -> np.ndarray:
    """Preserve exact 1.0 amplitude on `primary_dots` and place `n_tail_dots`
    secondary crests at `tail_weight` via exact 300 m CELF marginal gain conditioned
    on the existing coverage of `primary_dots`.
    """
    if not (0.0 < tail_weight <= 1.0):
        raise ValueError("tail_weight must lie in (0, 1]")
    prim = np.asarray(primary_dots, dtype=bool)
    elig = np.asarray(eligible_mask, dtype=bool)
    out = np.where(prim, np.float32(1.0), np.float32(0.0)).astype(np.float32)
    if n_tail_dots <= 0:
        return out

    # Compute exact initial coverage map of primary unit dots
    h, w = prim.shape
    init_cov = np.zeros((h, w), dtype=np.float32)
    p_float = prim.astype(np.float32)
    for dy, dx, kw in KERNEL_300M_OFFSETS:
        ys = slice(max(dy, 0), h + min(dy, 0))
        yd = slice(max(-dy, 0), h + min(-dy, 0))
        xs = slice(max(dx, 0), w + min(dx, 0))
        xd = slice(max(-dx, 0), w + min(-dx, 0))
        np.maximum(init_cov[yd, xd], np.float32(kw) * p_float[ys, xs], out=init_cov[yd, xd])

    d_prim = distance_transform_edt(~prim)
    tail_cand = elig & (~prim) & (d_prim >= float(min_dist_from_primary_px))
    tail_dots = celf_submodular_place(
        surface,
        tail_cand,
        int(n_tail_dots),
        min_dist_px=float(tail_min_dist_px),
        power_eta=float(power_eta),
        cand_cap=int(cand_cap),
        initial_coverage=init_cov,
        dot_amplitude=float(tail_weight),
        require_full=True,
    )
    out[tail_dots] = np.float32(tail_weight)
    return out
