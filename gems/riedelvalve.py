"""RIEDELVALVE lane: Transtensional Riedel (R / R') Shear Obliquity, Bimodal
Structure-Tensor Fracture-Intersection Energy, and Slope-Regime-Partitioned
USGS 3DEP 10 m Scarp + Bedrock Thalweg-Knickzone + DOE GDR #1391 INGENIOUS
Hydrothermal Fault-Valve Coupling.

Pre-registered hypothesis & equations: docs/HYPOTHESES_20261025_RIEDELVALVE.md.

Key physical and engineering advances:
1. Executes docs/NEXT_STEPS.md ``TENSOR-RIEDEL``: cross-scale axial strike
   divergence ``delta_theta in [0, 90 deg]`` between local 300 m-scale 10 m 3DEP
   scarp+chi structure tensors and 4.0 km mesoscale basement+gravity master-fault
   corridors, evaluating synthetic Riedel R (~19 deg) and conjugate antithetic R'
   (~72 deg) angular resonances gated by geodetic rotational vorticity
   ``shearrate / (shearrate + |dilaterate| + eps)``.
2. Bimodal fracture-intersection minor-eigenvalue energy ``sqrt(lambda_1 * lambda_2)``
   (square root of the Harris-Forstner structure-tensor determinant) on both
   10 m sub-pixel scarp+chi fields and signed subsurface gravity/RTP tilts,
   explicitly rewarding Y-splays, fault intersections, and conjugate step-overs
   that prior uniaxial coherence ``(lambda_1 - lambda_2)/(lambda_1 + lambda_2)``
   lanes suppressed.
3. Fixes ``#IR-92-VENTSCARP-BAND18-UNSIGNED-GRAVITY-AND-BAND4-BAND8-SWAP`` by
   computing Miller & Singh (1994) signed gravity tilt from GDAL-verified
   Band 11 (``iso_grav_anom_vg``) / Band 18 (``iso_grav_anom_hg``), signed
   elevation-gravity polarity concordance from Band 13 (``iso_grav_anom``),
   and true geodetic invariants from Band 4 (``geod_2ndinv``), Band 7
   (``geod_shearrate``), and Band 8 (``geod_dilaterate``).
4. Unifies <6 deg piedmont 10 m 3DEP scarp excess + tufa-filtered GDR #1391
   INGENIOUS hydrothermal vents/2mDAB probes with >=6 deg incised 10 m/100 m
   fluvial knickzones, radial MT clay-cap dome-halo gradients, and 3.5 km up-dip
   microseismic cloud back-projection, plus tests the additive ``@ 0.30`` N90K
   secondary Tversky skeleton (``docs/NEXT_STEPS.md`` Priority #1).

Strict zero-leakage invariant: zero fault-catalogue arrays ever enter any
feature or surface function in this module.
"""
from __future__ import annotations

import gc
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import transform as rio_transform
from scipy.ndimage import gaussian_filter, map_coordinates

from .breakline import spaced_top_mask
from .coulomb_loqo import _grad_xy, _sat, directional_ridge_1d, hessian_ridge_strength
from .hydroconduit import _clean_valid, cross_strike_monotonicity
from .knick_loqo import (
    calibrate_quadrant_probabilities,
    fit_single_loqo,
    mesoscale_zscore,
    thalweg_concavity_strength,
)
from .ventscarp import (
    _decode_u8_band,
    _rasterize_2m_temperature_probes,
    _rasterize_paleo_vents,
    anisotropic_strike_plume,
    subpixel_scarp_excess,
)

__all__ = [
    "FEATURE_NAMES",
    "GROUP_R_RIEDEL_INDICES",
    "GROUP_A_TOPO_INDICES",
    "GROUP_B_VALVE_INDICES",
    "GROUP_C_SUBSURF_INDICES",
    "NORIEDEL_INDICES",
    "BRANCH_DEBIASED_RIEDEL_INDICES",
    "BRANCH_PIEDMONT_VALVE_INDICES",
    "structure_tensor_strike_and_bimodal",
    "axial_angle_diff_deg",
    "riedel_obliquity_kernels",
    "updip_field_shift",
    "compute_riedelvalve_stack",
    "fit_predict_riedelvalve_loqo",
    "build_riedelvalve_crest_surface",
    "build_additive_tversky_tail",
    "spaced_top_mask",
]

FEATURE_NAMES: tuple[str, ...] = (
    # Group R: Untried Transtensional Riedel, Bimodal Intersection, Flexural & Up-Dip Seismic (0..7)
    "riedel_synthetic_obliquity_R",
    "riedel_conjugate_obliquity_Rprime",
    "bimodal_intersection_scarp10m",
    "bimodal_intersection_subsurface",
    "transtensional_vorticity_ratio",
    "riedel_vorticity_coupling",
    "flexural_halfgraben_dipole",
    "seismic_updip_trace_proj",
    # Group A: Slope-Partitioned USGS 3DEP 10 m Scarp + Incised 10 m/100 m Knickzones (8..15)
    "scarp10m_excess_max",
    "scarp10m_curv_prof_piedmont",
    "scarp10m_steep_step_grad",
    "scarp10m_linear_coherence",
    "chi10m_knick_step",
    "chi10m_ksn_drainage",
    "thalweg_knickzone_100m",
    "cross_strike_monotonicity_600m",
    # Group B: Tufa-Deconfounded GDR #1391 INGENIOUS Fault-Valve + GeoDAWN + MT Dome Halo (16..23)
    "paleo_vent_aniso_plume",
    "probe_2mdab_aniso_plume",
    "active_geotherm_spring_plume",
    "rad_k_over_th_z",
    "rad_u_over_th_grad",
    "grauch_mag_demag_edge",
    "mt_claycap_dome_halo",
    "valve_riedel_synergy",
    # Group C: Corrected GDAL-Verified Signed Gravity/RTP Tilt, Poisson & Shoreline Null (24..31)
    "true_grav_miller_singh_tilt",
    "true_dip_concord_elev_grav",
    "true_dip_concord_elev_base",
    "poisson_mag_grav_collinearity",
    "rtp_miller_singh_tilt_ridge",
    "basement_step_meso_z",
    "cross_contour_transgression",
    "lahontan_shoreline_null",
)

GROUP_R_RIEDEL_INDICES: tuple[int, ...] = tuple(range(0, 8))
GROUP_A_TOPO_INDICES: tuple[int, ...] = tuple(range(8, 16))
GROUP_B_VALVE_INDICES: tuple[int, ...] = tuple(range(16, 24))
GROUP_C_SUBSURF_INDICES: tuple[int, ...] = tuple(range(24, 32))

# Experiment 3 (noriedel_ablation): drops all 8 Group R features + col 23 (valve_riedel_synergy)
NORIEDEL_INDICES: tuple[int, ...] = GROUP_A_TOPO_INDICES + tuple(range(16, 23)) + GROUP_C_SUBSURF_INDICES

# Branch 2 (Province-debiased Riedel + Subsurface + Knickzone; drops district vent halos 16,17,18)
BRANCH_DEBIASED_RIEDEL_INDICES: tuple[int, ...] = (
    GROUP_R_RIEDEL_INDICES
    + (8, 11, 12, 13, 14, 15)
    + (19, 20, 21, 22, 23)
    + GROUP_C_SUBSURF_INDICES
)

# Branch 3 (Piedmont 10 m Scarp + Riedel Intersection + Hydrothermal Fault-Valve + Signed Tilt)
BRANCH_PIEDMONT_VALVE_INDICES: tuple[int, ...] = (
    (0, 1, 2, 3, 4, 5, 6)
    + (8, 9, 10, 11, 12, 15)
    + GROUP_B_VALVE_INDICES
    + (24, 25, 26, 27, 29, 30, 31)
)


def structure_tensor_strike_and_bimodal(
    field: np.ndarray,
    valid: np.ndarray,
    *,
    grad_sigma: float = 1.0,
    tensor_sigma: float = 2.8,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute axial strike (radians in [0, pi)), major sqrt(lambda_1), bimodal
    intersection energy ``sqrt(lambda_1 * lambda_2)``, and uniaxial coherence.

    On a purely planar 1D ridge ``lambda_2 == 0`` so ``bimodal == 0``; at a
    two-strike fault intersection, Y-splay, or Riedel step-over node both
    ``lambda_1 > 0`` and ``lambda_2 > 0`` so ``bimodal = sqrt(det(J))`` peaks.
    """
    if grad_sigma <= 0.0 or tensor_sigma <= 0.0:
        raise ValueError("grad_sigma and tensor_sigma must be positive")
    valid_b = np.asarray(valid, dtype=bool)
    gy, gx = _grad_xy(field, valid_b, sigma=float(grad_sigma))
    jxx = gaussian_filter((gx * gx).astype(np.float32), float(tensor_sigma))
    jyy = gaussian_filter((gy * gy).astype(np.float32), float(tensor_sigma))
    jxy = gaussian_filter((gx * gy).astype(np.float32), float(tensor_sigma))
    del gx, gy

    tr = (jxx + jyy).astype(np.float32)
    diff = (jxx - jyy).astype(np.float32)
    rad = np.sqrt(np.maximum(diff * diff + np.float32(4.0) * jxy * jxy, 0.0)).astype(np.float32)
    lam1 = np.maximum(np.float32(0.5) * (tr + rad), 0.0).astype(np.float32)
    lam2 = np.maximum(np.float32(0.5) * (tr - rad), 0.0).astype(np.float32)

    # Normal azimuth in (x=East, y=South) is 0.5*atan2(2*jxy, jxx - jyy);
    # tangent strike is normal + pi/2 modulo pi.
    phi_norm = np.float32(0.5) * np.arctan2(np.float32(2.0) * jxy, diff)
    strike_rad = np.mod(phi_norm + np.float32(0.5 * np.pi), np.float32(np.pi)).astype(np.float32)

    det_pos = np.maximum(jxx * jyy - jxy * jxy, 0.0).astype(np.float32)
    bimodal = np.sqrt(det_pos).astype(np.float32)
    major_amp = np.sqrt(lam1).astype(np.float32)
    coherence = (rad / (tr + np.float32(1e-6))).astype(np.float32)

    strike_rad[~valid_b] = 0.0
    major_amp[~valid_b] = 0.0
    bimodal[~valid_b] = 0.0
    coherence[~valid_b] = 0.0
    return strike_rad, major_amp, bimodal, coherence


def axial_angle_diff_deg(strike_a_rad: np.ndarray, strike_b_rad: np.ndarray) -> np.ndarray:
    """Acute axial angle in ``[0, 90]`` degrees between two modulo-pi strike fields."""
    c = np.clip(np.abs(np.cos(strike_a_rad - strike_b_rad)), 0.0, 1.0)
    return np.degrees(np.arccos(c)).astype(np.float32)


def riedel_obliquity_kernels(
    local_strike_rad: np.ndarray,
    master_strike_rad: np.ndarray,
    local_strength: np.ndarray,
    master_strength: np.ndarray,
    valid: np.ndarray,
    *,
    r_angle_deg: float = 19.0,
    r_sigma_deg: float = 8.5,
    rprime_angle_deg: float = 72.0,
    rprime_sigma_deg: float = 9.5,
) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate synthetic Riedel R (~19 deg) and conjugate antithetic R' (~72 deg)
    angular resonance weighted by normalized local and master-corridor strengths.
    """
    if r_sigma_deg <= 0.0 or rprime_sigma_deg <= 0.0:
        raise ValueError("r_sigma_deg and rprime_sigma_deg must be positive")
    valid_b = np.asarray(valid, dtype=bool)
    s_loc = np.nan_to_num(local_strike_rad, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
    s_mas = np.nan_to_num(master_strike_rad, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
    w_loc = np.clip(np.nan_to_num(local_strength, nan=0.0, posinf=0.0, neginf=0.0), 0.0, 1.0)
    w_mas = np.clip(np.nan_to_num(master_strength, nan=0.0, posinf=0.0, neginf=0.0), 0.0, 1.0)
    delta_deg = axial_angle_diff_deg(s_loc, s_mas)
    gate = (w_loc * w_mas).astype(np.float32)
    k_r = np.exp(-0.5 * (((delta_deg - np.float32(r_angle_deg)) / np.float32(r_sigma_deg)) ** 2))
    k_rp = np.exp(
        -0.5 * (((delta_deg - np.float32(rprime_angle_deg)) / np.float32(rprime_sigma_deg)) ** 2)
    )
    out_r = np.where(valid_b, gate * k_r, 0.0).astype(np.float32)
    out_rp = np.where(valid_b, gate * k_rp, 0.0).astype(np.float32)
    return out_r, out_rp


def updip_field_shift(
    field: np.ndarray,
    dip_dir_y: np.ndarray,
    dip_dir_x: np.ndarray,
    valid: np.ndarray,
    *,
    shift_px: float = 35.0,
) -> np.ndarray:
    """Sample ``field`` down-dip at ``(r + shift_px*dip_y, c + shift_px*dip_x)``
    to project a deep hanging-wall geophysical/seismic anomaly up-dip onto its
    candidate surface fault trace ``(r, c)``.
    """
    valid_b = np.asarray(valid, dtype=bool)
    clean = _clean_valid(field, valid_b)
    H, W = clean.shape
    dy = np.nan_to_num(dip_dir_y, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
    dx = np.nan_to_num(dip_dir_x, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
    norm = np.hypot(dy, dx) + np.float32(1e-5)
    uy = (dy / norm).astype(np.float32)
    ux = (dx / norm).astype(np.float32)
    del dy, dx
    rr, cc = np.meshgrid(
        np.arange(H, dtype=np.float32),
        np.arange(W, dtype=np.float32),
        indexing="ij",
    )
    sample_r = np.clip(rr + np.float32(shift_px) * uy, 0.0, float(H - 1))
    sample_c = np.clip(cc + np.float32(shift_px) * ux, 0.0, float(W - 1))
    shifted = map_coordinates(clean, [sample_r, sample_c], order=1, mode="nearest").astype(
        np.float32
    )
    del rr, cc, sample_r, sample_c, uy, ux, norm, clean
    shifted[~valid_b] = 0.0
    return shifted


def _rasterize_geotherm_wells_springs(
    csv_path: Path,
    shape: tuple[int, int],
    valid: np.ndarray,
) -> tuple[np.ndarray, dict[str, int]]:
    """Project DOE GDR #1391 thermal wells/springs + Na-K-Ca/chalcedony geothermometers.

    Strict zero-leakage: reads ONLY ``row``, ``col``, ``temp_c``,
    ``geothermchalc_c``, and ``geothermcat_c`` (never ``dist_known_fault_px``).
    """
    H, W = shape
    grid = np.zeros(shape, dtype=np.float32)
    df = pd.read_csv(csv_path)
    rows = pd.to_numeric(df["row"], errors="coerce").values
    cols = pd.to_numeric(df["col"], errors="coerce").values
    t_meas = pd.to_numeric(df["temp_c"], errors="coerce").fillna(0.0).values
    t_cat = pd.to_numeric(df["geothermcat_c"], errors="coerce").fillna(0.0).values
    t_cha = pd.to_numeric(df["geothermchalc_c"], errors="coerce").fillna(0.0).values
    in_foot = 0
    thermal = 0
    for r_f, c_f, tm, tn, tc in zip(rows, cols, t_meas, t_cat, t_cha):
        if not (np.isfinite(r_f) and np.isfinite(c_f)):
            continue
        r, c = int(round(r_f)), int(round(c_f))
        if 0 <= r < H and 0 <= c < W and valid[r, c]:
            in_foot += 1
            t_eff = max(float(tm), 0.72 * float(min(tn, 300.0)), 0.78 * float(min(tc, 260.0)))
            if t_eff >= 28.0:
                thermal += 1
                w = np.log1p((t_eff - 25.0) / 18.0)
                if w > grid[r, c]:
                    grid[r, c] = np.float32(w)
    return grid, {"total_rows": int(len(df)), "in_footprint": in_foot, "thermal_sites": thermal}


def compute_riedelvalve_stack(
    *,
    training_features_path: Path,
    topo10m_path: Path,
    chi10m_path: Path,
    geodawn_rad_path: Path,
    geodawn_ext_path: Path,
    paleo_zip_path: Path,
    probe_2m_zip_path: Path,
    wellspring_csv_path: Path,
    footprint: np.ndarray,
    out_mmap_path: Path | None = None,
) -> dict[str, object]:
    """Build the 32-feature zero-catalogue RIEDELVALVE stack + 1D crest channels."""
    foot = np.asarray(footprint, dtype=bool)
    H, W = foot.shape
    n_foot = int(foot.sum())
    if out_mmap_path is not None:
        X: np.ndarray = np.memmap(
            out_mmap_path, dtype=np.float32, mode="w+", shape=(n_foot, len(FEATURE_NAMES))
        )
    else:
        X = np.zeros((n_foot, len(FEATURE_NAMES)), dtype=np.float32)

    with rasterio.open(training_features_path) as tf_ds:
        transform = tf_ds.transform

        def _read_tf(band_idx: int) -> np.ndarray:
            arr = tf_ds.read(band_idx).astype(np.float32)
            bad = ~np.isfinite(arr) | (arr <= -1e30)
            arr[bad] = np.nan
            return arr

        b12_elev = _read_tf(12)  # det_elev
        b19_slope = _read_tf(19)  # det_elev_slope
        b2_rtp = _read_tf(2)  # rtp (signed)

        valid = foot & np.isfinite(b12_elev) & np.isfinite(b19_slope) & np.isfinite(b2_rtp)
        slope_100m_deg = np.where(valid, np.maximum(b19_slope, 0.0), 0.0).astype(np.float32)
        del b19_slope

        # --- Group A: Seamless 3DEP 10 m Scarp + 10 m Chi + 100 m Thalweg Knickzones ---
        with rasterio.open(topo10m_path) as t10:
            s10_p90 = _decode_u8_band(t10, 1)
            s10_max = _decode_u8_band(t10, 2)
            s10_steep = _decode_u8_band(t10, 3)
            s10_std = _decode_u8_band(t10, 4)
            curv10 = _decode_u8_band(t10, 6)
            asp_coh10 = _decode_u8_band(t10, 7)
            hs_lin10 = _decode_u8_band(t10, 8)
            dem10_mean = _decode_u8_band(t10, 9)

        ex_max = subpixel_scarp_excess(s10_max, slope_100m_deg, valid)
        ex_p90 = subpixel_scarp_excess(s10_p90, slope_100m_deg, valid)
        s10_std_norm = np.where(
            valid,
            s10_std / (np.float32(1.5) + np.float32(0.35) * slope_100m_deg),
            0.0,
        ).astype(np.float32)

        # Piedmont weight (<9 deg favored; steep >=12 deg unfaulted alpine cliffs suppressed)
        pied_gate = np.exp(-((slope_100m_deg / np.float32(8.5)) ** 2)).astype(np.float32)
        curv10_pied = np.where(valid, np.log1p(curv10 * 100.0) * (0.22 + 0.78 * pied_gate), 0.0).astype(
            np.float32
        )
        lin_coh10 = np.where(
            valid,
            asp_coh10 * (0.35 + 0.65 * hs_lin10) * _sat(s10_std_norm, 1.15),
            0.0,
        ).astype(np.float32)
        gy_st, gx_st = _grad_xy(s10_steep + np.float32(0.02) * s10_p90, valid, sigma=1.1)
        steep_step = np.where(valid, np.hypot(gx_st, gy_st), 0.0).astype(np.float32)
        del s10_max, s10_steep, s10_std, curv10, asp_coh10, hs_lin10, gy_st, gx_st

        with rasterio.open(chi10m_path) as c10:
            step_max = np.maximum(c10.read(1).astype(np.float32), 0.0) / np.float32(1000.0)
            step_min = np.maximum(c10.read(2).astype(np.float32), 0.0) / np.float32(1000.0)
            ksn_max = np.maximum(c10.read(3).astype(np.float32), 0.0)
            log_area = np.maximum(c10.read(4).astype(np.float32), 0.0) / np.float32(1000.0)

        drain_w = np.clip((log_area - np.float32(3.4)) / np.float32(2.6), 0.15, 1.0).astype(
            np.float32
        )
        chi_knick = np.where(valid, np.log1p(np.maximum(step_max - step_min, 0.0) * 8.0) * drain_w, 0.0).astype(
            np.float32
        )
        chi_ksn = np.where(valid, np.log1p(ksn_max * 0.06) * drain_w, 0.0).astype(np.float32)
        del step_max, step_min, ksn_max, log_area, drain_w

        # 100 m incised bedrock thalweg knickzones + 600 m cross-strike step monotonicity
        log_s100 = np.log1p(slope_100m_deg).astype(np.float32)
        lsy, lsx = _grad_xy(log_s100, valid, sigma=1.0)
        rel_break100 = np.where(valid, np.hypot(lsy, lsx), 0.0).astype(np.float32)
        del log_s100, lsy, lsx
        thal_15 = thalweg_concavity_strength(b12_elev, valid, sigma=1.5)
        thal_30 = thalweg_concavity_strength(b12_elev, valid, sigma=3.0)
        thal_knick100 = np.where(
            valid,
            _sat(np.maximum(thal_15, np.float32(0.75) * thal_30), 1.8) * _sat(rel_break100, 0.045),
            0.0,
        ).astype(np.float32)
        del thal_15, thal_30
        mu_step600 = cross_strike_monotonicity(
            b12_elev, valid, half_span_px=3, normal_sigma=3.0, elev_floor_m=0.5
        )

        X[:, 8] = ex_max[foot]
        X[:, 9] = curv10_pied[foot]
        X[:, 10] = steep_step[foot]
        X[:, 11] = lin_coh10[foot]
        X[:, 12] = chi_knick[foot]
        X[:, 13] = chi_ksn[foot]
        X[:, 14] = thal_knick100[foot]
        X[:, 15] = mu_step600[foot]

        # Combined local 10 m scarp + knickzone field for local structure-tensor analysis
        scarp_knick_field = np.where(
            valid,
            0.48 * _sat(ex_max, 0.55)
            + 0.24 * _sat(ex_p90, 0.35)
            + 0.28 * _sat(chi_knick, 0.45),
            0.0,
        ).astype(np.float32)
        strike_loc10, amp_loc10, bimod_scarp10, _ = structure_tensor_strike_and_bimodal(
            scarp_knick_field, valid, grad_sigma=1.0, tensor_sigma=2.6
        )

        # Slope-regime-aware 1D surface crests:
        # L_scarp10m favors piedmont/apron (<9 deg) sub-pixel scarps; L_knick favors incised channels
        l_scarp10m = np.where(
            valid,
            (
                0.40 * _sat(ex_max, 0.62)
                + 0.26 * _sat(curv10_pied, 1.05)
                + 0.20 * _sat(lin_coh10, 0.35)
                + 0.14 * _sat(steep_step, 0.055)
            )
            * (0.28 + 0.72 * pied_gate),
            0.0,
        ).astype(np.float32)
        l_knick = np.where(
            valid,
            0.44 * _sat(chi_knick, 0.52)
            + 0.24 * _sat(chi_ksn, 0.85)
            + 0.32 * _sat(thal_knick100 * (0.40 + 0.60 * mu_step600), 0.12),
            0.0,
        ).astype(np.float32)
        del (
            ex_p90,
            s10_std_norm,
            curv10_pied,
            steep_step,
            lin_coh10,
            chi_knick,
            chi_ksn,
            thal_knick100,
            rel_break100,
            scarp_knick_field,
        )

        # --- Group C: Corrected GDAL-Verified Signed Gravity/RTP Tilt, Basement & Shoreline Null ---
        b11_gvg = _read_tf(11)  # iso_grav_anom_vg (SIGNED vertical gradient!)
        b13_grav = _read_tf(13)  # iso_grav_anom (SIGNED gravity anomaly!)
        b18_ghg = _read_tf(18)  # iso_grav_anom_hg (horizontal gradient magnitude)
        b5_gslope = _read_tf(5)  # iso_grav_anom_slope
        b15_base = _read_tf(15)  # depth_to_base_surf

        # True Miller & Singh (1994) signed gravity tilt angle + spatial gradient ridge
        gvg_c = _clean_valid(b11_gvg, valid)
        ghg_c = np.maximum(_clean_valid(b18_ghg, valid), 0.0)
        grav_ms_tilt = np.where(valid, np.arctan2(gvg_c, ghg_c + np.float32(1e-3)), 0.0).astype(
            np.float32
        )
        gty, gtx = _grad_xy(grav_ms_tilt, valid, sigma=1.5)
        grav_tilt_grad = np.where(valid, np.hypot(gty, gtx), 0.0).astype(np.float32)
        del b11_gvg, gvg_c, gty, gtx

        # True signed gravity gradient (Band 13) & basement deepening gradient (Band 15)
        gy_g13, gx_g13 = _grad_xy(b13_grav, valid, sigma=2.0)
        gnorm13 = np.hypot(gy_g13, gx_g13)

        db_pos = np.maximum(_clean_valid(b15_base, valid), 0.0)
        log_db10 = np.log(db_pos + np.float32(10.0)).astype(np.float32)
        dby, dbx = _grad_xy(log_db10, valid, sigma=2.0)
        bnorm = np.hypot(dby, dbx)

        zy, zx = _grad_xy(b12_elev, valid, sigma=2.0)
        znorm = np.hypot(zy, zx)

        # Polarity concordance: footwall high (+grad elev) aligned with footwall gravity high (+grad Band 13)
        # and opposite hanging-wall basement deepening (-grad Band 15)
        g_scale = float(np.percentile(gnorm13[valid], 72.0)) + 1e-4
        b_scale = float(np.percentile(bnorm[valid], 72.0)) + 1e-4
        dip_grav_true = np.where(
            valid,
            np.clip((zy * gy_g13 + zx * gx_g13) / (znorm * gnorm13 + np.float32(1e-4)), -1.0, 1.0)
            * _sat(gnorm13, g_scale),
            0.0,
        ).astype(np.float32)
        dip_base_true = np.where(
            valid,
            np.clip(-(zy * dby + zx * dbx) / (znorm * bnorm + np.float32(1e-4)), -1.0, 1.0)
            * _sat(bnorm, b_scale),
            0.0,
        ).astype(np.float32)

        # True Band 2 RTP + Band 9 tmi_vg / Band 3 tmi_hg Miller-Singh tilt & Poisson collinearity
        b3_mhg = _read_tf(3)
        b9_mvg = _read_tf(9)
        mvg_c = _clean_valid(b9_mvg, valid)
        mhg_c = np.maximum(_clean_valid(b3_mhg, valid), 0.0)
        rtp_ms_tilt = np.where(valid, np.arctan2(mvg_c, mhg_c + np.float32(1e-2)), 0.0).astype(
            np.float32
        )
        mty, mtx = _grad_xy(rtp_ms_tilt, valid, sigma=1.5)
        rtp_tilt_grad = np.where(valid, np.hypot(mty, mtx), 0.0).astype(np.float32)
        rtp_hess = hessian_ridge_strength(b2_rtp, valid, sigma=2.0)
        rtp_ridge = np.where(
            valid,
            0.60 * _sat(rtp_tilt_grad, 0.25) + 0.40 * _sat(rtp_hess, 6.0),
            0.0,
        ).astype(np.float32)
        del b3_mhg, b9_mvg, mvg_c, mhg_c, mty, mtx, rtp_hess

        ry, rx = _grad_xy(b2_rtp, valid, sigma=2.2)
        rnorm = np.hypot(ry, rx)
        r_scale = float(np.percentile(rnorm[valid], 72.0)) + 1e-4
        poisson_col = np.where(
            valid,
            np.clip(np.abs(ry * gy_g13 + rx * gx_g13) / (rnorm * gnorm13 + np.float32(1e-4)), 0.0, 1.0)
            * np.sqrt(_sat(rnorm, r_scale) * _sat(gnorm13, g_scale)),
            0.0,
        ).astype(np.float32)
        del ry, rx, rnorm

        gslope_z = mesoscale_zscore(b5_gslope, valid & np.isfinite(b5_gslope), sigma_px=45.0)
        base_step_z = np.where(
            valid,
            0.55 * mesoscale_zscore(bnorm, valid, sigma_px=45.0) + 0.45 * gslope_z,
            0.0,
        ).astype(np.float32)
        del b5_gslope, gslope_z

        # Cross-contour transgression vs 1,330 m Pleistocene Lake Lahontan shoreline mimic
        gy_c100, gx_c100 = _grad_xy(b12_elev, valid, sigma=4.5)
        gy_s10, gx_s10 = _grad_xy(s10_p90, valid, sigma=1.2)
        ang_c = np.arctan2(gy_c100, gx_c100)
        ang_s = np.arctan2(gy_s10, gx_s10)
        transgress = np.where(valid, np.abs(np.sin(ang_s - ang_c)), 0.0).astype(np.float32)
        lahontan_elev = np.exp(-(((dem10_mean - np.float32(1330.0)) / np.float32(45.0)) ** 2)).astype(
            np.float32
        )
        lahontan_null = np.where(valid, lahontan_elev * (1.0 - transgress), 0.0).astype(np.float32)
        del s10_p90, dem10_mean, gy_c100, gx_c100, gy_s10, gx_s10, ang_c, ang_s, lahontan_elev

        X[:, 24] = grav_tilt_grad[foot]
        X[:, 25] = dip_grav_true[foot]
        X[:, 26] = dip_base_true[foot]
        X[:, 27] = poisson_col[foot]
        X[:, 28] = rtp_ridge[foot]
        X[:, 29] = base_step_z[foot]
        X[:, 30] = transgress[foot]
        X[:, 31] = lahontan_null[foot]

        # --- Group R: Untried Riedel R/R' Obliquity, Bimodal Intersection, Flexural & Up-Dip Seismic ---
        # Mesoscale (4.0 km) master basement + gravity corridor structure tensor
        master_potential = np.where(
            valid,
            0.55 * mesoscale_zscore(b13_grav, valid, sigma_px=55.0)
            - 0.45 * mesoscale_zscore(log_db10, valid, sigma_px=55.0),
            0.0,
        ).astype(np.float32)
        strike_master, amp_master, _, _ = structure_tensor_strike_and_bimodal(
            master_potential, valid, grad_sigma=4.0, tensor_sigma=14.0
        )
        del master_potential

        loc_w = _sat(amp_loc10, float(np.percentile(amp_loc10[valid], 70.0)) + 1e-5)
        mas_w = _sat(amp_master, float(np.percentile(amp_master[valid], 65.0)) + 1e-5)
        riedel_r, riedel_rp = riedel_obliquity_kernels(
            strike_loc10,
            strike_master,
            loc_w,
            mas_w,
            valid,
            r_angle_deg=19.0,
            r_sigma_deg=8.5,
            rprime_angle_deg=72.0,
            rprime_sigma_deg=9.5,
        )
        del strike_loc10, strike_master, amp_loc10, amp_master, loc_w, mas_w

        # Subsurface bimodal intersection determinant on combined signed gravity + RTP tilts
        sub_tilt_combo = np.where(
            valid,
            0.58 * grav_ms_tilt + 0.42 * rtp_ms_tilt,
            0.0,
        ).astype(np.float32)
        _, _, bimod_sub, _ = structure_tensor_strike_and_bimodal(
            sub_tilt_combo, valid, grad_sigma=1.6, tensor_sigma=3.8
        )
        del grav_ms_tilt, rtp_ms_tilt, sub_tilt_combo

        # GDAL-verified Geodetic Rotational Vorticity: Band 4 (2ndinv), Band 7 (shearrate), Band 8 (dilaterate)
        b4_2nd = _read_tf(4)
        b7_shr = _read_tf(7)
        b8_dil = _read_tf(8)
        shr_pos = np.maximum(_clean_valid(b7_shr, valid), 0.0)
        dil_abs = np.abs(_clean_valid(b8_dil, valid))
        shr_eps = float(np.percentile(shr_pos[valid], 25.0)) + 1e-6
        s2_z = mesoscale_zscore(b4_2nd, valid & np.isfinite(b4_2nd), sigma_px=45.0)
        vort_ratio = np.where(
            valid,
            (shr_pos / (shr_pos + dil_abs + np.float32(shr_eps)))
            * (np.float32(0.45) + np.float32(0.55) * _sat(np.maximum(s2_z + 0.5, 0.0), 1.6)),
            0.0,
        ).astype(np.float32)
        riedel_vort = np.where(
            valid,
            vort_ratio * np.maximum(riedel_r, np.float32(0.85) * riedel_rp),
            0.0,
        ).astype(np.float32)
        del b4_2nd, b7_shr, b8_dil, shr_pos, dil_abs, s2_z

        # Elastic-plate 1.2 km vs 5.0 km flexural half-graben dipole (Band 13 gravity + Band 12 elev + Band 15 wedge)
        g_clean = _clean_valid(b13_grav, valid)
        z_clean = _clean_valid(b12_elev, valid)
        g_bp = (gaussian_filter(g_clean, 10.0) - gaussian_filter(g_clean, 52.0)).astype(np.float32)
        z_bp = (gaussian_filter(z_clean, 10.0) - gaussian_filter(z_clean, 52.0)).astype(np.float32)
        gby, gbx = _grad_xy(g_bp, valid, sigma=2.5)
        zby, zbx = _grad_xy(z_bp, valid, sigma=2.5)
        gb_n = np.hypot(gby, gbx)
        zb_n = np.hypot(zby, zbx)
        flex_dipole = np.where(
            valid,
            np.clip((gby * zby + gbx * zbx) / (gb_n * zb_n + np.float32(1e-4)), -1.0, 1.0)
            * np.sqrt(
                _sat(gb_n, float(np.percentile(gb_n[valid], 70.0)) + 1e-4)
                * _sat(bnorm, b_scale)
            ),
            0.0,
        ).astype(np.float32)
        del b13_grav, b12_elev, g_clean, z_clean, g_bp, z_bp, gby, gbx, zby, zbx, gb_n, zb_n
        del gy_g13, gx_g13, gnorm13, zy, zx, znorm

        # Up-dip 3.5 km microseismic cloud trace projection (Band 10 deq_n100a15, Band 16 ieq_n100a15)
        b10_deq = _read_tf(10)
        b16_ieq = _read_tf(16)
        ieq_z = np.maximum(mesoscale_zscore(b16_ieq, valid & np.isfinite(b16_ieq), sigma_px=50.0), 0.0)
        deq_prox = np.maximum(
            -mesoscale_zscore(
                np.log1p(np.maximum(_clean_valid(b10_deq, valid), 0.0)), valid, sigma_px=50.0
            ),
            0.0,
        )
        seis_cloud = (0.58 * ieq_z + 0.42 * deq_prox).astype(np.float32)
        # Hanging-wall deepening direction is +grad(log_db10) = (dby, dbx); sample down-dip at +35 px
        seis_updip = updip_field_shift(seis_cloud, dby, dbx, valid, shift_px=35.0)
        seis_updip = np.where(valid, seis_updip * (0.30 + 0.70 * _sat(bnorm, b_scale)), 0.0).astype(
            np.float32
        )
        del b10_deq, b16_ieq, ieq_z, deq_prox, seis_cloud, dby, dbx

        bimod_s10_norm = _sat(
            bimod_scarp10, float(np.percentile(bimod_scarp10[valid], 85.0)) + 1e-5
        )
        bimod_sub_norm = _sat(bimod_sub, float(np.percentile(bimod_sub[valid], 85.0)) + 1e-5)

        X[:, 0] = riedel_r[foot]
        X[:, 1] = riedel_rp[foot]
        X[:, 2] = bimod_s10_norm[foot]
        X[:, 3] = bimod_sub_norm[foot]
        X[:, 4] = vort_ratio[foot]
        X[:, 5] = riedel_vort[foot]
        X[:, 6] = flex_dipole[foot]
        X[:, 7] = seis_updip[foot]

        # --- Group B: Tufa-Deconfounded INGENIOUS Fault-Valve + GeoDAWN + MT Clay-Cap Halo ---
        paleo_imp, paleo_stats = _rasterize_paleo_vents(paleo_zip_path, transform, (H, W), valid)
        paleo_plume = anisotropic_strike_plume(
            paleo_imp, valid, strike_deg_east_of_north=18.0, sigma_parallel_px=24.0, sigma_perp_px=8.0
        )
        del paleo_imp

        probe_imp, probe_stats = _rasterize_2m_temperature_probes(
            probe_2m_zip_path, transform, (H, W), valid, dab_threshold_c=1.2
        )
        probe_plume = anisotropic_strike_plume(
            probe_imp, valid, strike_deg_east_of_north=18.0, sigma_parallel_px=20.0, sigma_perp_px=7.0
        )
        del probe_imp

        spring_imp, spring_stats = _rasterize_geotherm_wells_springs(
            wellspring_csv_path, (H, W), valid
        )
        spring_plume = anisotropic_strike_plume(
            spring_imp, valid, strike_deg_east_of_north=18.0, sigma_parallel_px=22.0, sigma_perp_px=8.0
        )
        del spring_imp

        with rasterio.open(geodawn_rad_path) as gr:
            rad_k = _decode_u8_band(gr, 1)
            rad_th = _decode_u8_band(gr, 2)
            rad_u = _decode_u8_band(gr, 3)

        k_over_th = np.where(valid, rad_k / (np.maximum(rad_th, 0.25) + np.float32(0.35)), 0.0).astype(
            np.float32
        )
        u_over_th = np.where(valid, rad_u / (np.maximum(rad_th, 0.25) + np.float32(0.35)), 0.0).astype(
            np.float32
        )
        del rad_k, rad_th, rad_u
        k_th_z = mesoscale_zscore(k_over_th, valid, sigma_px=38.0)
        uty, utx = _grad_xy(u_over_th, valid, sigma=1.6)
        u_th_grad = np.where(valid, np.hypot(uty, utx), 0.0).astype(np.float32)
        del k_over_th, u_over_th, uty, utx

        with rasterio.open(geodawn_ext_path) as ge:
            tmi_up150 = _decode_u8_band(ge, 4)

        grauch_res = (
            mesoscale_zscore(tmi_up150, valid, sigma_px=36.0)
            - mesoscale_zscore(b2_rtp, valid, sigma_px=36.0)
        ).astype(np.float32)
        gry, grx = _grad_xy(grauch_res, valid, sigma=1.6)
        grauch_edge = np.where(valid, np.hypot(gry, grx), 0.0).astype(np.float32)
        del tmi_up150, b2_rtp, grauch_res, gry, grx

        # Radial Smectite Clay-Cap Outer Annulus vs Core + Cover-Normalized Perimeter Gradient
        b17_cond = _read_tf(17)
        cond_log = np.where(valid, np.log1p(np.maximum(_clean_valid(b17_cond, valid), 0.0)), 0.0).astype(
            np.float32
        )
        del b17_cond
        # Cover-normalized conductivity residual (suppresses uniform alkali playa salt pans)
        cond_cover_norm = (cond_log / (np.float32(1.0) + np.float32(0.18) * log_db10)).astype(
            np.float32
        )
        cond_core = gaussian_filter(cond_cover_norm, 4.0).astype(np.float32)
        cond_annulus = gaussian_filter(cond_cover_norm, 18.0).astype(np.float32)
        cy, cx = _grad_xy(cond_cover_norm, valid, sigma=2.2)
        mt_dome_halo = np.where(
            valid,
            0.55 * _sat(np.hypot(cy, cx), 0.020)
            + 0.45 * _sat(np.abs(cond_core - cond_annulus), 0.045),
            0.0,
        ).astype(np.float32)
        del b15_base, db_pos, log_db10, cond_log, cond_cover_norm, cond_core, cond_annulus, cy, cx

        vent_halo = np.maximum(
            _sat(paleo_plume, 0.32),
            np.maximum(_sat(probe_plume, 0.38), _sat(spring_plume, 0.35)),
        ).astype(np.float32)
        alt_halo = (
            np.float32(0.42) * _sat(np.maximum(k_th_z, 0.0), 1.4)
            + np.float32(0.32) * _sat(grauch_edge, 0.42)
            + np.float32(0.26) * mt_dome_halo
        ).astype(np.float32)
        riedel_struct = np.maximum(
            np.maximum(riedel_r, np.float32(0.85) * riedel_rp),
            np.float32(0.80) * np.maximum(bimod_s10_norm, bimod_sub_norm),
        ).astype(np.float32)
        valve_synergy = np.where(
            valid,
            riedel_struct * (np.float32(0.55) * vent_halo + np.float32(0.45) * alt_halo),
            0.0,
        ).astype(np.float32)

        X[:, 16] = paleo_plume[foot]
        X[:, 17] = probe_plume[foot]
        X[:, 18] = spring_plume[foot]
        X[:, 19] = k_th_z[foot]
        X[:, 20] = u_th_grad[foot]
        X[:, 21] = grauch_edge[foot]
        X[:, 22] = mt_dome_halo[foot]
        X[:, 23] = valve_synergy[foot]

    # 1D Subsurface Potential + Riedel/Intersection Crest Localizers
    l_sub = np.where(
        valid,
        0.34 * _sat(grav_tilt_grad, 0.16)
        + 0.24 * _sat(rtp_ridge, 0.48)
        + 0.22 * _sat(poisson_col, 0.35)
        + 0.20 * _sat(bnorm, b_scale) * (0.45 + 0.55 * _sat(np.maximum(dip_grav_true, 0.0), 0.45)),
        0.0,
    ).astype(np.float32)

    l_riedel = np.where(
        valid,
        (
            0.36 * np.maximum(riedel_r, np.float32(0.88) * riedel_rp)
            + 0.34 * bimod_s10_norm
            + 0.30 * bimod_sub_norm
        )
        * (0.62 + 0.38 * np.maximum(vent_halo, alt_halo)),
        0.0,
    ).astype(np.float32)

    del (
        ex_max,
        pied_gate,
        mu_step600,
        ghg_c,
        grav_tilt_grad,
        bnorm,
        dip_grav_true,
        dip_base_true,
        rtp_tilt_grad,
        rtp_ridge,
        poisson_col,
        base_step_z,
        transgress,
        lahontan_null,
        riedel_r,
        riedel_rp,
        bimod_scarp10,
        bimod_sub,
        bimod_s10_norm,
        bimod_sub_norm,
        vort_ratio,
        riedel_vort,
        flex_dipole,
        seis_updip,
        paleo_plume,
        probe_plume,
        spring_plume,
        k_th_z,
        u_th_grad,
        grauch_edge,
        mt_dome_halo,
        vent_halo,
        alt_halo,
        riedel_struct,
        valve_synergy,
    )
    gc.collect()

    np.nan_to_num(X, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    return {
        "X_foot": X,
        "valid": valid,
        "slope_100m_deg": slope_100m_deg,
        "L_scarp10m": l_scarp10m,
        "L_knick": l_knick,
        "L_sub": l_sub,
        "L_riedel": l_riedel,
        "vent_stats": {
            "paleo_geothermal": paleo_stats,
            "temperature_probe_2m": probe_stats,
            "geotherm_wells_springs": spring_stats,
        },
    }


def fit_predict_riedelvalve_loqo(
    X_foot: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    label_mask: np.ndarray,
    *,
    include_riedel: bool = True,
    excluded_mask: np.ndarray | None = None,
    guard_px: int = 12,
    neg_buffer_px: float = 5.0,
    neg_pos_ratio: int = 4,
    seed: int = 20261025,
    max_iter: int = 165,
    calib_weight: float = 0.80,
    power_gamma: float = 3.2,
) -> dict[str, np.ndarray]:
    """Fit the 4-quadrant Leave-One-Quadrant-Out (LOQO) RIEDELVALVE ensemble."""
    valid_b = np.asarray(valid, dtype=bool) & np.asarray(footprint, dtype=bool)
    if include_riedel:
        p_deb = fit_single_loqo(
            X_foot,
            footprint,
            valid_b,
            quad,
            label_mask,
            feature_cols=BRANCH_DEBIASED_RIEDEL_INDICES,
            excluded_mask=excluded_mask,
            guard_px=guard_px,
            neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio,
            seed=int(seed),
            max_iter=max_iter,
        )
        gc.collect()
        p_pied = fit_single_loqo(
            X_foot,
            footprint,
            valid_b,
            quad,
            label_mask,
            feature_cols=BRANCH_PIEDMONT_VALVE_INDICES,
            excluded_mask=excluded_mask,
            guard_px=guard_px,
            neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio,
            seed=int(seed) + 17,
            max_iter=max_iter,
        )
        raw_proba = (np.float32(0.45) * p_deb + np.float32(0.55) * p_pied).astype(np.float32)
        del p_deb, p_pied
    else:
        noriedel_deb = tuple(i for i in BRANCH_DEBIASED_RIEDEL_INDICES if i in NORIEDEL_INDICES)
        noriedel_pied = tuple(i for i in BRANCH_PIEDMONT_VALVE_INDICES if i in NORIEDEL_INDICES)
        p_deb = fit_single_loqo(
            X_foot,
            footprint,
            valid_b,
            quad,
            label_mask,
            feature_cols=noriedel_deb,
            excluded_mask=excluded_mask,
            guard_px=guard_px,
            neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio,
            seed=int(seed),
            max_iter=max_iter,
        )
        gc.collect()
        p_pied = fit_single_loqo(
            X_foot,
            footprint,
            valid_b,
            quad,
            label_mask,
            feature_cols=noriedel_pied,
            excluded_mask=excluded_mask,
            guard_px=guard_px,
            neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio,
            seed=int(seed) + 17,
            max_iter=max_iter,
        )
        raw_proba = (np.float32(0.45) * p_deb + np.float32(0.55) * p_pied).astype(np.float32)
        del p_deb, p_pied

    gc.collect()
    cal_proba = calibrate_quadrant_probabilities(
        raw_proba, valid_b, quad, calib_weight=calib_weight, power_gamma=power_gamma
    )
    return {
        "raw_proba": raw_proba,
        "cal_proba": cal_proba,
    }


def build_riedelvalve_crest_surface(
    proba_2d: np.ndarray,
    l_scarp10m: np.ndarray,
    l_knick: np.ndarray,
    l_sub: np.ndarray,
    l_riedel: np.ndarray | None,
    valid: np.ndarray,
    *,
    scarp_weight: float = 0.96,
    knick_weight: float = 1.02,
    sub_weight: float = 1.18,
    riedel_weight: float = 1.06,
) -> dict[str, np.ndarray]:
    """Sharpen calibrated LOQO fault probability onto 1D multi-branch physical crests."""
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(
        valid_b,
        np.clip(
            np.nan_to_num(np.asarray(proba_2d, dtype=np.float32), nan=0.0, posinf=1.0, neginf=0.0),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    ls = np.clip(
        np.nan_to_num(np.asarray(l_scarp10m, dtype=np.float32), nan=0.0, posinf=1.0, neginf=0.0),
        0.0,
        1.0,
    )
    lk = np.clip(
        np.nan_to_num(np.asarray(l_knick, dtype=np.float32), nan=0.0, posinf=1.0, neginf=0.0),
        0.0,
        1.0,
    )
    lsub = np.clip(
        np.nan_to_num(np.asarray(l_sub, dtype=np.float32), nan=0.0, posinf=1.0, neginf=0.0),
        0.0,
        1.0,
    )
    e_line = np.maximum(
        np.float32(scarp_weight) * ls,
        np.maximum(
            np.float32(knick_weight) * lk,
            np.float32(sub_weight) * lsub,
        ),
    )
    if l_riedel is not None and riedel_weight > 0.0:
        lr = np.clip(
            np.nan_to_num(np.asarray(l_riedel, dtype=np.float32), nan=0.0, posinf=1.0, neginf=0.0),
            0.0,
            1.0,
        )
        e_line = np.maximum(e_line, np.float32(riedel_weight) * lr)
    s_crest = np.where(
        valid_b,
        p * (np.float32(0.14) + np.float32(0.86) * e_line),
        0.0,
    ).astype(np.float32)
    ridge_1d = directional_ridge_1d(s_crest, valid_b)
    return {
        "S_crest": s_crest,
        "E_line": np.where(valid_b, e_line, 0.0).astype(np.float32),
        "ridge_1d": ridge_1d,
    }


def build_additive_tversky_tail(
    s_crest: np.ndarray,
    candidate_pool: np.ndarray,
    *,
    n_primary: int = 37654,
    n_total: int = 90000,
    tail_weight: float = 0.30,
    min_dist_px: float = 2.90,
    require_full: bool = True,
) -> np.ndarray:
    """Emit ``n_primary`` unit crests (``1.0``) plus ``n_total - n_primary`` non-overlapping
    secondary crests at ``tail_weight`` (satisfying the exact Tversky ``alpha=0.2``
    marginal expected-DTI condition ``c_i > alpha * DTI`` without diluting top peaks).
    """
    if n_primary <= 0 or n_total < n_primary:
        raise ValueError("Require 0 < n_primary <= n_total")
    if not (0.0 < tail_weight <= 1.0):
        raise ValueError("tail_weight must lie in (0, 1]")
    clean_crest = np.nan_to_num(
        np.asarray(s_crest, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0
    ).astype(np.float32)
    sel = spaced_top_mask(
        clean_crest,
        candidate_pool,
        int(n_total),
        min_dist_px=float(min_dist_px),
        cand_cap=1_200_000,
        require_full=bool(require_full),
    )
    idx = np.flatnonzero(sel)
    out = np.zeros(clean_crest.shape, dtype=np.float32)
    if idx.size == 0:
        return out
    vals = clean_crest.ravel()[idx]
    order = np.argsort(-vals, kind="mergesort")
    sorted_idx = idx[order]
    k_prim = min(int(n_primary), int(sorted_idx.size))
    out.ravel()[sorted_idx[:k_prim]] = np.float32(1.0)
    if sorted_idx.size > k_prim:
        w = np.clip(np.float32(tail_weight), np.float32(0.0), np.float32(1.0))
        out.ravel()[sorted_idx[k_prim:]] = w
    return out
