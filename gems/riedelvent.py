"""RIEDELVENT lane: En-Echelon Riedel R-Shear Obliquity (12-28 deg) x Hanging-Wall
Flexural Hinge Curvature x Slope-Regime Coupled 3DEP-10m Sub-Pixel Scarp, Incised
Thalweg Knickzone & Tufa-Filtered INGENIOUS Hydrothermal Vent Out-of-Quadrant
(LOQO) Fault Discovery.

Pre-registered hypothesis & equations: docs/HYPOTHESES_20261025_RIEDELVENT.md.

Key physical innovations:
1. En-echelon Riedel R-shear obliquity (``riedel_obliquity_index``,
   ``riedel_strain_coupling``): measures the acute axial obliquity
   ``Delta_theta in [0, 90 deg]`` between fine-scale (150 m) scarp/RTP magnetic
   strike and mesoscale (1.4 km) gravity/basement master-fault strike, isolating
   synthetic Coulomb-Riedel R-shears and P-shear relays in ``[12, 28 deg]``
   (centered at ``phi/2 ~= 19 deg``) weighted by structure-tensor coherence and
   mesoscale geodetic shear/dilatation strain.
2. Hanging-wall flexural hinge curvature (``flexure_hinge_curvature``,
   ``flexure_gravity_concordance``): extracts the 450-1,350 m difference-of-Gaussians
   flexural rollover inflection of ``log1p(depth_to_base_surf)`` (Band 15) and
   ``iso_grav_anom`` (Band 13) where basement deepening and gravity drop are
   antiparallel across concealed basin-margin master faults.
3. Slope-regime coupled 1D crest localization fusing ``< 8.5 deg`` piedmont
   USGS 3DEP 10 m sub-pixel scarps + tufa-filtered INGENIOUS hydrothermal vent
   plumes (``VENTSCARP``) with ``>= 6 deg`` incised drainage thalweg knickzones
   + sliding-window Poisson magneto-gravity collinearity (``KNICKLOQO``), tested
   under both 37,654-dot binary emission (``riedelvent``) and 64,000-dot additive
   tail emission (``riedelvent_tail``: 37,654 @ 1.0 + 26,346 @ 0.30).

Strict zero-leakage invariant: zero fault-catalogue arrays ever enter any
feature or surface builder in this module.
"""
from __future__ import annotations

import gc
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt, gaussian_filter
from sklearn.ensemble import HistGradientBoostingClassifier

from .breakline import spaced_top_mask
from .coulomb_loqo import _grad_xy, _sat, directional_ridge_1d, hessian_ridge_strength
from .hydroconduit import _clean_valid, coherence_and_strike_deg, cross_strike_monotonicity
from .knick_loqo import (
    calibrate_quadrant_probabilities,
    mesoscale_zscore,
    thalweg_concavity_strength,
)
from .ventscarp import (
    _decode_u8_band,
    _rasterize_2m_temperature_probes,
    _rasterize_active_thermal_springs,
    _rasterize_paleo_vents,
    anisotropic_strike_plume,
    is_hydrothermal_paleo_vent,
    subpixel_scarp_excess,
)

__all__ = [
    "FEATURE_NAMES",
    "GROUP_A_SCARP_KNICK_INDICES",
    "GROUP_B_VENT_INDICES",
    "GROUP_C_SUBSURF_INDICES",
    "GROUP_D_RIEDEL_FLEX_INDICES",
    "ABLATED_NOVENT_INDICES",
    "RIEDEL_SUBSURF_INDICES",
    "riedel_obliquity_field",
    "flexural_hinge_field",
    "build_additive_tail_allocation",
    "compute_riedelvent_stack",
    "fit_predict_riedelvent_loqo",
    "build_riedelvent_crest_surface",
    "is_hydrothermal_paleo_vent",
    "anisotropic_strike_plume",
    "subpixel_scarp_excess",
    "spaced_top_mask",
]

FEATURE_NAMES: tuple[str, ...] = (
    # Group A: Seamless USGS 3DEP 10 m Sub-Pixel Scarp & 10m/100m Thalweg Knickzones (0..8)
    "scarp10m_excess_max",
    "scarp10m_excess_p90",
    "scarp10m_slope_std_norm",
    "scarp10m_curv_prof_piedmont",
    "scarp10m_linear_coherence",
    "scarp10m_steep_step_grad",
    "chi10m_knick_step",
    "chi10m_ksn_drainage",
    "thalweg100m_knickzone_idx",
    # Group B: Tufa-Filtered INGENIOUS Paleo/Blind Hydrothermal Vents, 2mDAB & Alteration (9..17)
    "paleo_vent_aniso_plume",
    "probe_2mdab_aniso_plume",
    "active_thermal_spring_aniso",
    "unified_vent_district_halo",
    "rad_k_over_th_z",
    "rad_u_over_th_z",
    "grauch_mag_demag_residual",
    "mt_claycap_perimeter_grad",
    "heatflow_scarp_coupling",
    # Group C: Province-Debiased Subsurface Potential, Poisson Collinearity & Shoreline Null (18..25)
    "iso_grav_slope_meso_z",
    "grav_tilt_grad",
    "basement_step_grad",
    "poisson_mag_grav_collinearity",
    "dip_concord_scarp_grav",
    "strain_2ndinv_meso_z",
    "cross_contour_scarp_transgression",
    "lahontan_shoreline_mimic_index",
    # Group D: En-Echelon Riedel R-Shear Obliquity & Hanging-Wall Flexural Hinge (26..29)
    "riedel_obliquity_index",
    "riedel_strain_coupling",
    "flexure_hinge_curvature",
    "flexure_gravity_concordance",
)

GROUP_A_SCARP_KNICK_INDICES: tuple[int, ...] = tuple(range(0, 9))
GROUP_B_VENT_INDICES: tuple[int, ...] = tuple(range(9, 18))
GROUP_C_SUBSURF_INDICES: tuple[int, ...] = tuple(range(18, 26))
GROUP_D_RIEDEL_FLEX_INDICES: tuple[int, ...] = tuple(range(26, 30))

# Arm 2 (riedel_novent): ablates all 9 Group B hydrothermal-vent features and all 4 Group D Riedel/flexure features
ABLATED_NOVENT_INDICES: tuple[int, ...] = GROUP_A_SCARP_KNICK_INDICES + GROUP_C_SUBSURF_INDICES

# Subsurface + Riedel + Flexure + Hydrothermal Valve branch (forces model to weight deeper geophysical + Riedel/vent coupling)
RIEDEL_SUBSURF_INDICES: tuple[int, ...] = (
    (0, 3, 4, 6, 7, 8)
    + GROUP_B_VENT_INDICES
    + GROUP_C_SUBSURF_INDICES
    + GROUP_D_RIEDEL_FLEX_INDICES
)

# Province-debiased full feature tuple (all 30 features are already baseline-level free!)
FULL_INDICES: tuple[int, ...] = tuple(range(len(FEATURE_NAMES)))


def riedel_obliquity_field(
    fine_field: np.ndarray,
    master_field: np.ndarray,
    valid: np.ndarray,
    *,
    fine_grad_sigma: float = 1.2,
    fine_tensor_sigma: float = 2.5,
    master_grad_sigma: float = 4.0,
    master_tensor_sigma: float = 14.0,
    target_obliquity_deg: float = 19.0,
    bandwidth_deg: float = 6.5,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute en-echelon Riedel R-shear obliquity index and acute axial angle ``Delta_theta``.

    Measures the acute angle ``Delta_theta in [0, 90 deg]`` between the fine-scale
    (150-250 m) surface/near-surface break strike ``theta_fine`` and the mesoscale
    (1.4 km) basement/gravity master-zone strike ``theta_master``. Under Coulomb-Riedel
    mechanics with friction angle ``phi in [30, 38 deg]``, synthetic R-shears form at
    ``Delta_theta = phi/2 ~= 15-19 deg`` (and P-shear relays in ``12-28 deg``).
    """
    if bandwidth_deg <= 0.0:
        raise ValueError("bandwidth_deg must be positive")
    valid_b = np.asarray(valid, dtype=bool)
    coh_f, az_f = coherence_and_strike_deg(
        fine_field,
        valid_b,
        deriv_sigma=float(fine_grad_sigma),
        tensor_sigma=float(fine_tensor_sigma),
    )
    coh_m, az_m = coherence_and_strike_deg(
        master_field,
        valid_b,
        deriv_sigma=float(master_grad_sigma),
        tensor_sigma=float(master_tensor_sigma),
    )
    # Axial difference in [0, 90 deg]
    diff_rad = np.deg2rad(np.asarray(az_f, dtype=np.float32) - np.asarray(az_m, dtype=np.float32))
    cos_diff = np.clip(np.abs(np.cos(diff_rad)), 0.0, 1.0)
    delta_deg = np.rad2deg(np.arccos(cos_diff)).astype(np.float32)

    gauss_ang = np.exp(
        -0.5 * (((delta_deg - np.float32(target_obliquity_deg)) / np.float32(bandwidth_deg)) ** 2)
    ).astype(np.float32)
    coh_geom = np.sqrt(np.maximum(coh_f * coh_m, 0.0)).astype(np.float32)
    idx = np.where(valid_b, gauss_ang * coh_geom, 0.0).astype(np.float32)
    delta_out = np.where(valid_b, delta_deg, 0.0).astype(np.float32)
    return idx, delta_out


def flexural_hinge_field(
    depth_to_base_m: np.ndarray,
    iso_grav_anom: np.ndarray,
    valid: np.ndarray,
    *,
    sigma_inner_px: float = 4.5,
    sigma_outer_px: float = 13.5,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute hanging-wall flexural rollover hinge curvature and gravity concordance.

    Above a concealed listric or normal master fault, the hanging-wall basin floor
    exhibits a 450-1,350 m flexural rollover inflection where ``log1p(depth_to_base)``
    curves downward while ``iso_grav_anom`` drops antiparallel to basement deepening.
    """
    if sigma_inner_px <= 0.0 or sigma_outer_px <= sigma_inner_px:
        raise ValueError("Require 0 < sigma_inner_px < sigma_outer_px")
    valid_b = np.asarray(valid, dtype=bool)
    base_clean = np.maximum(_clean_valid(depth_to_base_m, valid_b), 0.0).astype(np.float32)
    base_log = np.log1p(base_clean).astype(np.float32)
    del base_clean

    b_in = gaussian_filter(base_log, float(sigma_inner_px)).astype(np.float32)
    b_out = gaussian_filter(base_log, float(sigma_outer_px)).astype(np.float32)
    dog_base = np.maximum(b_in - b_out, 0.0).astype(np.float32)
    del b_in, b_out

    by, bx = _grad_xy(base_log, valid_b, sigma=2.0)
    b_step = np.hypot(bx, by).astype(np.float32)
    del base_log

    hinge_curv = np.where(valid_b, dog_base * b_step * np.float32(10.0), 0.0).astype(np.float32)
    del dog_base

    grav_clean = _clean_valid(iso_grav_anom, valid_b).astype(np.float32)
    g_in = gaussian_filter(grav_clean, float(sigma_inner_px)).astype(np.float32)
    g_out = gaussian_filter(grav_clean, float(sigma_outer_px)).astype(np.float32)
    dog_grav = np.maximum(g_out - g_in, 0.0).astype(np.float32)
    del g_in, g_out

    gy, gx = _grad_xy(grav_clean, valid_b, sigma=2.0)
    g_step = np.hypot(gx, gy).astype(np.float32)
    del grav_clean

    # Antiparallel alignment: basement deepens (+grad B) where gravity drops (-grad G)
    anti_cos = np.clip(-(bx * gx + by * gy) / (b_step * g_step + np.float32(1e-4)), 0.0, 1.0)
    flex_grav = np.where(
        valid_b,
        np.log1p(dog_grav) * anti_cos * _sat(b_step, 0.14),
        0.0,
    ).astype(np.float32)
    return hinge_curv, flex_grav


def build_additive_tail_allocation(
    s_crest: np.ndarray,
    candidate_pool: np.ndarray,
    *,
    n_core: int = 37654,
    n_total: int = 64000,
    tail_weight: float = 0.30,
    min_dist_px: float = 3.30,
) -> np.ndarray:
    """Build an additive-tail continuous [0, 1] allocation keeping top ``n_core`` crests at 1.0.

    Addresses docs/NEXT_STEPS.md Item #1:
      - Ranks 1..n_core receive full unit weight 1.0 (preserving 100% of primary TP_w
        and avoiding VENTSCARP E3's soft-weight dilution of primary crests).
      - Ranks (n_core + 1)..n_total receive continuous weight ``tail_weight`` in (0, 1)
        (capturing secondary en-echelon Riedel & hydrothermal step-over strands with a
        70% reduction in false-positive denominator cost under alpha=0.2, beta=0.8).
    """
    if not (0.0 < tail_weight <= 1.0):
        raise ValueError("tail_weight must lie in (0, 1]")
    if n_total < n_core or n_core < 1:
        raise ValueError("Require 1 <= n_core <= n_total")

    sel_all = spaced_top_mask(
        s_crest,
        candidate_pool,
        int(n_total),
        min_dist_px=float(min_dist_px),
        cand_cap=950_000,
    )
    idx = np.flatnonzero(sel_all)
    out = np.zeros(s_crest.shape, dtype=np.float32)
    if idx.size == 0:
        return out
    vals = s_crest.ravel()[idx]
    order = np.argsort(-vals, kind="mergesort")
    sorted_idx = idx[order]

    core_idx = sorted_idx[: int(n_core)]
    tail_idx = sorted_idx[int(n_core) : int(n_total)]
    out.ravel()[core_idx] = 1.0
    if tail_idx.size > 0:
        out.ravel()[tail_idx] = np.float32(tail_weight)
    return out


def compute_riedelvent_stack(
    training_features_tif: Path,
    topo_10m_tif: Path,
    dem10_chi_tif: Path,
    paleo_zip: Path,
    probe_2m_zip: Path,
    wellspring_csv: Path,
    geodawn_ext_tif: Path,
    footprint: np.ndarray,
) -> dict[str, object]:
    """Stream all 30 zero-catalogue RIEDELVENT features into ``X_foot`` (<1.45 GiB peak RSS)."""
    foot = np.asarray(footprint, dtype=bool)
    shape = foot.shape
    n_foot = int(foot.sum())
    X = np.zeros((n_foot, len(FEATURE_NAMES)), dtype=np.float32)

    def _read_tf(b: int) -> np.ndarray:
        with rasterio.open(training_features_tif) as ds:
            arr = ds.read(b, masked=True).filled(np.nan).astype(np.float32)
        arr[np.abs(arr) > 1e20] = np.nan
        return arr

    # Read 100 m detrended elevation & slope first to establish exact valid mask
    b12_elev = _read_tf(12)
    b19_slope = _read_tf(19)
    valid = foot & np.isfinite(b12_elev) & np.isfinite(b19_slope)
    with rasterio.open(training_features_tif) as ds_ref:
        transform = ds_ref.transform

    b19_clean = _clean_valid(b19_slope, valid)
    p99_b19 = float(np.percentile(b19_clean[valid], 99.0))
    if p99_b19 <= 2.5:
        slope_100m_deg = np.rad2deg(np.arctan(np.maximum(b19_clean, 0.0))).astype(np.float32)
    else:
        slope_100m_deg = np.maximum(b19_clean, 0.0).astype(np.float32)
    del b19_slope

    # --- Group A: USGS 3DEP 10 m Sub-Pixel Scarp + 10m/100m Thalweg Knickzones (0..8) ---
    with rasterio.open(topo_10m_tif) as ds10:
        s10_p90 = _decode_u8_band(ds10, 1)
        s10_max = _decode_u8_band(ds10, 2)
        s10_std = _decode_u8_band(ds10, 4)
        curv10_prof = _decode_u8_band(ds10, 6)
        asp10_coh = _decode_u8_band(ds10, 7)
        hs10_lin = _decode_u8_band(ds10, 8)
        dem10_mean = _decode_u8_band(ds10, 9)

    ex_max = subpixel_scarp_excess(s10_max, slope_100m_deg, valid)
    ex_p90 = subpixel_scarp_excess(s10_p90, slope_100m_deg, valid)
    std_norm = np.where(valid, s10_std / (1.0 + 0.25 * slope_100m_deg), 0.0).astype(np.float32)
    pied_gate = np.exp(-((slope_100m_deg / np.float32(11.5)) ** 2)).astype(np.float32)
    curv_pied = np.where(valid, np.log1p(np.maximum(curv10_prof, 0.0)) * pied_gate, 0.0).astype(
        np.float32
    )
    lin_coh = np.where(valid, asp10_coh * hs10_lin, 0.0).astype(np.float32)
    gy_s10, gx_s10 = _grad_xy(s10_p90, valid, sigma=1.0)
    steep_step_grad = np.hypot(gx_s10, gy_s10).astype(np.float32)

    X[:, 0] = ex_max[foot]
    X[:, 1] = ex_p90[foot]
    X[:, 2] = std_norm[foot]
    X[:, 3] = curv_pied[foot]
    X[:, 4] = lin_coh[foot]
    X[:, 5] = steep_step_grad[foot]
    del s10_max, s10_std, asp10_coh, hs10_lin, gy_s10, gx_s10

    with rasterio.open(dem10_chi_tif) as dschi:
        step_raw = dschi.read(1).astype(np.float32)
        ksn_raw = dschi.read(3).astype(np.float32)
        area_raw = dschi.read(4).astype(np.float32)
    chi_valid = valid & (step_raw > -32000)
    chi_step_pos = np.where(chi_valid, np.log1p(np.maximum(step_raw, 0.0) * 0.001), 0.0).astype(
        np.float32
    )
    chi_step_sm = np.where(valid, gaussian_filter(chi_step_pos, 1.6), 0.0).astype(np.float32)
    ksn_pos = np.where(
        chi_valid & (ksn_raw > -32000) & (area_raw > -32000),
        np.log1p(np.maximum(ksn_raw, 0.0)) * np.maximum(area_raw * 0.001 - 4.0, 0.0),
        0.0,
    ).astype(np.float32)
    ksn_sm = np.where(valid, gaussian_filter(ksn_pos, 1.6), 0.0).astype(np.float32)
    X[:, 6] = chi_step_sm[foot]
    X[:, 7] = ksn_sm[foot]
    del step_raw, ksn_raw, area_raw, chi_valid, chi_step_pos, ksn_pos

    # 100 m incised drainage thalweg knickzone (from KNICKLOQO)
    log_slope100 = np.log(np.maximum(b19_clean, 0.0) + np.float32(1.0)).astype(np.float32)
    del b19_clean
    lsy, lsx = _grad_xy(log_slope100, valid, sigma=1.0)
    rel_break100 = np.where(valid, np.hypot(lsy, lsx), 0.0).astype(np.float32)
    del lsy, lsx, log_slope100
    thal_15 = thalweg_concavity_strength(b12_elev, valid, sigma=1.5)
    thal_30 = thalweg_concavity_strength(b12_elev, valid, sigma=3.0)
    thal_concav = np.maximum(thal_15, np.float32(0.75) * thal_30).astype(np.float32)
    del thal_15, thal_30
    thalweg_knick = np.where(
        valid,
        _sat(thal_concav, 1.8) * _sat(rel_break100, 0.045),
        0.0,
    ).astype(np.float32)
    del thal_concav
    X[:, 8] = thalweg_knick[foot]

    mu_step100 = cross_strike_monotonicity(
        b12_elev, valid, half_span_px=3, normal_sigma=3.0, elev_floor_m=0.5
    )

    # Cross-contour scarp transgression vs 1,330 m Lake Lahontan shoreline bench mimic
    gy_c100, gx_c100 = _grad_xy(b12_elev, valid, sigma=4.5)
    gy_s, gx_s = _grad_xy(s10_p90, valid, sigma=1.2)
    ang_c = np.arctan2(gy_c100, gx_c100)
    ang_s = np.arctan2(gy_s, gx_s)
    transgress = np.where(valid, np.abs(np.sin(ang_s - ang_c)), 0.0).astype(np.float32)
    lahontan_elev = np.exp(-(((dem10_mean - np.float32(1330.0)) / np.float32(45.0)) ** 2)).astype(
        np.float32
    )
    lahontan_null = np.where(valid, lahontan_elev * (1.0 - transgress), 0.0).astype(np.float32)
    del gy_c100, gx_c100, gy_s, gx_s, ang_c, ang_s, lahontan_elev

    # 1D Sub-Pixel Piedmont Scarp & Coupled 10m/100m Knickzone Localizer Branches
    l_scarp10m = np.where(
        valid,
        0.34 * _sat(ex_max, 0.85) * (0.35 + 0.65 * pied_gate)
        + 0.26 * _sat(curv_pied, 1.60)
        + 0.22 * _sat(lin_coh, 0.22) * (0.40 + 0.60 * pied_gate)
        + 0.18 * _sat(steep_step_grad, 3.5) * pied_gate,
        0.0,
    ).astype(np.float32)
    l_knick = np.where(
        valid,
        0.44 * (0.62 * _sat(chi_step_sm, 0.25) + 0.38 * _sat(ksn_sm, 2.2))
        + 0.34 * _sat(thalweg_knick * (0.50 + 0.50 * transgress), 0.10)
        + 0.22 * _sat(rel_break100 * (0.40 + 0.60 * transgress) * (0.35 + 0.65 * mu_step100), 0.045),
        0.0,
    ).astype(np.float32)
    del (
        ex_p90,
        std_norm,
        curv10_prof,
        curv_pied,
        lin_coh,
        steep_step_grad,
        chi_step_sm,
        ksn_sm,
        thalweg_knick,
        rel_break100,
        mu_step100,
    )
    gc.collect()

    # --- Group B: Tufa-Filtered INGENIOUS Hydrothermal Vents, 2mDAB & Alteration (9..17) ---
    paleo_imp, paleo_stats = _rasterize_paleo_vents(paleo_zip, transform, shape, valid)
    probe_imp, probe_stats = _rasterize_2m_temperature_probes(probe_2m_zip, transform, shape, valid)
    spring_imp, spring_stats = _rasterize_active_thermal_springs(wellspring_csv, shape, valid)

    paleo_plume = anisotropic_strike_plume(
        paleo_imp, valid, strike_deg_east_of_north=18.0, sigma_parallel_px=24.0, sigma_perp_px=8.0
    )
    probe_plume = anisotropic_strike_plume(
        probe_imp, valid, strike_deg_east_of_north=18.0, sigma_parallel_px=22.0, sigma_perp_px=7.5
    )
    spring_plume = anisotropic_strike_plume(
        spring_imp, valid, strike_deg_east_of_north=18.0, sigma_parallel_px=24.0, sigma_perp_px=8.0
    )
    vent_comb = (1.20 * paleo_imp + 1.00 * probe_imp + 0.85 * spring_imp).astype(np.float32)
    district_halo = np.where(valid, gaussian_filter(vent_comb, 46.0) * 100.0, 0.0).astype(
        np.float32
    )
    del paleo_imp, probe_imp, spring_imp, vent_comb

    X[:, 9] = np.log1p(paleo_plume * 4.0)[foot]
    X[:, 10] = np.log1p(probe_plume * 3.0)[foot]
    X[:, 11] = np.log1p(spring_plume * 2.5)[foot]
    X[:, 12] = np.log1p(district_halo)[foot]

    with rasterio.open(geodawn_ext_tif) as dsext:
        thk_u8 = dsext.read(1).astype(np.float32)
        uth_u8 = dsext.read(3).astype(np.float32)
        tmi150_u8 = dsext.read(4).astype(np.float32)
    ext_valid = valid & (thk_u8 > 0) & (tmi150_u8 > 0)
    k_over_th_z = -mesoscale_zscore(thk_u8, ext_valid, sigma_px=40.0)
    u_over_th_z = mesoscale_zscore(uth_u8, ext_valid, sigma_px=40.0)

    b2_rtp = _read_tf(2)
    rtp_clean = _clean_valid(b2_rtp, valid)
    rtp_z30 = mesoscale_zscore(b2_rtp, ext_valid & np.isfinite(b2_rtp), sigma_px=30.0)
    tmi150_z30 = mesoscale_zscore(tmi150_u8, ext_valid, sigma_px=30.0)
    grauch_demag = np.where(ext_valid, np.clip(tmi150_z30 - rtp_z30, -4.0, 4.0), 0.0).astype(
        np.float32
    )
    gy_demag, gx_demag = _grad_xy(grauch_demag, valid, sigma=1.5)
    grauch_edge = np.hypot(gx_demag, gy_demag).astype(np.float32)
    del thk_u8, uth_u8, tmi150_u8, ext_valid, b2_rtp, rtp_z30, tmi150_z30, gy_demag, gx_demag

    b17_mt = _read_tf(17)
    mt_log = np.log1p(np.maximum(_clean_valid(b17_mt, valid), 0.0)).astype(np.float32)
    gy_mt, gx_mt = _grad_xy(mt_log, valid, sigma=2.0)
    mt_grad = np.hypot(gx_mt, gy_mt).astype(np.float32)
    del b17_mt, mt_log, gy_mt, gx_mt

    b3_hf = _read_tf(3)
    hf_z = mesoscale_zscore(b3_hf, valid & np.isfinite(b3_hf), sigma_px=55.0)
    hf_scarp = np.where(
        valid,
        np.maximum(hf_z, 0.0) * (0.4 + 0.6 * _sat(ex_max, 0.85))
        + np.log1p(paleo_plume + probe_plume + 0.5 * spring_plume) * _sat(ex_max, 0.85),
        0.0,
    ).astype(np.float32)
    del b3_hf, hf_z

    X[:, 13] = k_over_th_z[foot]
    X[:, 14] = u_over_th_z[foot]
    X[:, 15] = grauch_demag[foot]
    X[:, 16] = mt_grad[foot]
    X[:, 17] = hf_scarp[foot]

    vent_gate = np.clip(
        0.36
        + 0.64
        * _sat(
            paleo_plume * 2.5 + probe_plume * 2.0 + spring_plume * 1.2 + 0.25 * district_halo,
            0.60,
        ),
        0.36,
        1.0,
    ).astype(np.float32)
    del paleo_plume, probe_plume, spring_plume, district_halo, k_over_th_z, u_over_th_z, grauch_demag, hf_scarp
    gc.collect()

    # --- Group C: Province-Debiased Subsurface, Poisson Collinearity & Shoreline Null (18..25) ---
    b5_gslope = _read_tf(5)
    gslope_z = mesoscale_zscore(b5_gslope, valid & np.isfinite(b5_gslope), sigma_px=42.0)
    del b5_gslope

    b18_grav = _read_tf(18)
    gy_g, gx_g = _grad_xy(b18_grav, valid, sigma=2.0)
    gh = np.hypot(gx_g, gy_g).astype(np.float32)
    gz_approx = gaussian_filter(_clean_valid(b18_grav, valid), 2.0) - gaussian_filter(
        _clean_valid(b18_grav, valid), 6.0
    )
    grav_tilt = np.arctan2(gz_approx, gh + np.float32(1e-4)).astype(np.float32)
    gy_gt, gx_gt = _grad_xy(grav_tilt, valid, sigma=1.5)
    grav_tilt_grad = np.hypot(gx_gt, gy_gt).astype(np.float32)
    del gz_approx, grav_tilt, gy_gt, gx_gt

    b15_base = _read_tf(15)
    base_clean = np.maximum(_clean_valid(b15_base, valid), 0.0).astype(np.float32)
    base_log = np.where(valid, np.log1p(base_clean), 0.0).astype(np.float32)
    gy_b, gx_b = _grad_xy(base_log, valid, sigma=1.8)
    base_step = np.hypot(gx_b, gy_b).astype(np.float32)
    del gy_b, gx_b

    # Sliding-window Poisson's-relation magneto-gravity vector collinearity (Band 2 RTP vs Band 13/18 gravity)
    u_rtp = gaussian_filter(rtp_clean, 1.2).astype(np.float32)
    ry, rx = np.gradient(u_rtp)
    r_gh = np.hypot(ry, rx).astype(np.float32)
    del u_rtp
    poisson_collin = np.where(
        valid,
        np.clip(np.abs(ry * gy_g + rx * gx_g) / (r_gh * gh + np.float32(1e-4)), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    rtp_hess = hessian_ridge_strength(np.log1p(r_gh), valid, sigma=2.0)
    r_gh_norm = _sat(r_gh, float(np.percentile(r_gh[valid], 75.0)) + 1e-4)
    del ry, rx, r_gh, rtp_clean

    # Polarity concordance: hanging-wall downslope (-grad dem10_mean) aligned with gravity drop (-grad grav)
    gy_z10, gx_z10 = _grad_xy(dem10_mean, valid, sigma=1.8)
    nz10 = np.hypot(gx_z10, gy_z10) + np.float32(1e-4)
    ng = gh + np.float32(1e-4)
    dip_concord = np.where(
        valid,
        np.clip((gx_z10 * gx_g + gy_z10 * gy_g) / (nz10 * ng), -1.0, 1.0)
        * _sat(gh, float(np.percentile(gh[valid], 75.0)) + 1e-4),
        0.0,
    ).astype(np.float32)
    del dem10_mean, gy_z10, gx_z10, gy_g, gx_g, gh

    b4_s2i = _read_tf(4)
    s2i_z = mesoscale_zscore(b4_s2i, valid & np.isfinite(b4_s2i), sigma_px=45.0)
    del b4_s2i

    X[:, 18] = gslope_z[foot]
    X[:, 19] = grav_tilt_grad[foot]
    X[:, 20] = base_step[foot]
    X[:, 21] = poisson_collin[foot]
    X[:, 22] = dip_concord[foot]
    X[:, 23] = s2i_z[foot]
    X[:, 24] = transgress[foot]
    X[:, 25] = lahontan_null[foot]
    del dip_concord, transgress, lahontan_null

    # --- Group D: En-Echelon Riedel Obliquity & Hanging-Wall Flexural Hinge (26..29) ---
    # Fine-scale surface/shallow scarp field vs mesoscale basement/gravity master field
    fine_struct = np.where(valid, 0.65 * s10_p90 + 0.35 * b12_elev * 0.05, 0.0).astype(np.float32)
    master_struct = np.where(
        valid, 0.55 * _clean_valid(b18_grav, valid) - 0.45 * base_log * 4.0, 0.0
    ).astype(np.float32)
    del s10_p90, b12_elev, b18_grav, base_log

    riedel_idx, _ = riedel_obliquity_field(
        fine_struct,
        master_struct,
        valid,
        fine_grad_sigma=1.2,
        fine_tensor_sigma=2.5,
        master_grad_sigma=4.0,
        master_tensor_sigma=14.0,
        target_obliquity_deg=19.0,
        bandwidth_deg=6.5,
    )
    del fine_struct, master_struct

    b7_shr = _read_tf(7)
    shr_z = mesoscale_zscore(b7_shr, valid & np.isfinite(b7_shr), sigma_px=45.0)
    del b7_shr

    b8_dil = _read_tf(8)
    dil_z = mesoscale_zscore(b8_dil, valid & np.isfinite(b8_dil), sigma_px=45.0)
    del b8_dil

    strain_gate = (
        1.0 / (1.0 + np.exp(-0.85 * (0.50 * shr_z + 0.35 * dil_z + 0.15 * s2i_z)))
    ).astype(np.float32)
    riedel_strain = np.where(valid, riedel_idx * strain_gate, 0.0).astype(np.float32)
    del shr_z, dil_z, s2i_z, strain_gate

    b13_iso = _read_tf(13)
    flex_curv, flex_grav = flexural_hinge_field(
        b15_base, b13_iso, valid, sigma_inner_px=4.5, sigma_outer_px=13.5
    )
    del b15_base, b13_iso, base_clean

    X[:, 26] = riedel_idx[foot]
    X[:, 27] = riedel_strain[foot]
    X[:, 28] = flex_curv[foot]
    X[:, 29] = flex_grav[foot]

    # 1D Subsurface, Riedel-Flexure & Hydrothermal Crest Localizers
    l_grav_base = np.where(
        valid,
        0.34 * _sat(grav_tilt_grad, 0.22)
        + 0.26 * _sat(base_step, 0.16)
        + 0.22 * _sat(rtp_hess, 0.04) * (0.60 + 0.40 * poisson_collin)
        + 0.18 * _sat(np.maximum(gslope_z, 0.0), 1.8),
        0.0,
    ).astype(np.float32)

    l_riedel_flex = np.where(
        valid,
        0.40 * _sat(riedel_strain, 0.16)
        + 0.32 * _sat(flex_curv, 0.04)
        + 0.16 * _sat(flex_grav, 0.22)
        + 0.12 * r_gh_norm,
        0.0,
    ).astype(np.float32)

    l_vent_sub = np.where(
        valid,
        (
            0.46 * l_grav_base
            + 0.24 * l_riedel_flex
            + 0.18 * _sat(grauch_edge, 0.45)
            + 0.12 * _sat(mt_grad, 0.015)
        )
        * vent_gate,
        0.0,
    ).astype(np.float32)

    del (
        ex_max,
        pied_gate,
        grauch_edge,
        mt_grad,
        vent_gate,
        gslope_z,
        grav_tilt_grad,
        base_step,
        poisson_collin,
        rtp_hess,
        r_gh_norm,
        riedel_idx,
        riedel_strain,
        flex_curv,
        flex_grav,
        slope_100m_deg,
    )
    gc.collect()

    return {
        "X_foot": X,
        "valid": valid,
        "L_scarp10m": l_scarp10m,
        "L_knick": l_knick,
        "L_grav_base": l_grav_base,
        "L_riedel_flex": l_riedel_flex,
        "L_vent_sub": l_vent_sub,
        "vent_stats": {
            "paleo_geothermal": paleo_stats,
            "temperature_probe_2m": probe_stats,
            "active_thermal_springs": spring_stats,
        },
    }


def fit_riedelvent_single_loqo(
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
    neg_pos_ratio: int = 3,
    max_pos_samples: int = 40000,
    seed: int = 20261025,
    max_iter: int = 145,
) -> np.ndarray:
    """Fit a 4-quadrant Leave-One-Quadrant-Out model with stratified positive cap."""
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

    raw_proba = np.zeros(foot.shape, dtype=np.float32)
    present_quads = [int(q) for q in (0, 1, 2, 3) if np.any((quad == q) & valid_b)]

    for q in present_quads:
        target_q = (quad == q) & valid_b
        guard = binary_dilation(quad == q, iterations=int(guard_px)) if guard_px > 0 else (quad == q)
        train_dom = valid_b & (quad >= 0) & (quad != q) & (~guard) & (~excl)

        pos_mask = train_dom & lbl
        neg_pool = train_dom & (~lbl) & (d_lbl > float(neg_buffer_px))

        pos_idx_all = foot_row_map[pos_mask]
        neg_idx = foot_row_map[neg_pool]
        if pos_idx_all.size == 0 or neg_idx.size == 0:
            raise ValueError(
                f"Quadrant {q} RIEDELVENT training split has empty class: pos={pos_idx_all.size}, neg={neg_idx.size}"
            )

        rng = np.random.default_rng(int(seed) + 97 * q)
        if int(max_pos_samples) > 0 and pos_idx_all.size > int(max_pos_samples):
            pos_idx = rng.choice(pos_idx_all, size=int(max_pos_samples), replace=False)
            pos_idx.sort()
        else:
            pos_idx = pos_idx_all

        n_neg = min(int(neg_idx.size), max(int(pos_idx.size) * int(neg_pos_ratio), 1))
        if n_neg < neg_idx.size:
            neg_sel = rng.choice(neg_idx, size=n_neg, replace=False)
            neg_sel.sort()
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
            learning_rate=0.065,
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
        batch = 350_000
        for start in range(0, te_idx.size, batch):
            stop = min(start + batch, te_idx.size)
            X_te = X_foot[te_idx[start:stop]][:, cols]
            preds[start:stop] = clf.predict_proba(X_te)[:, 1].astype(np.float32)

        raw_proba[target_q] = preds

    return raw_proba


def fit_predict_riedelvent_loqo(
    X_foot: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    label_mask: np.ndarray,
    *,
    include_riedel_vent: bool = True,
    excluded_mask: np.ndarray | None = None,
    guard_px: int = 12,
    neg_buffer_px: float = 5.0,
    neg_pos_ratio: int = 3,
    max_pos_samples: int = 40000,
    seed: int = 20261025,
    max_iter: int = 145,
    calib_weight: float = 0.80,
    power_gamma: float = 3.15,
) -> dict[str, np.ndarray]:
    """Fit a strictly Out-of-Quadrant (LOQO) ensemble with or without Group B+D Riedel/vent features."""
    valid_b = np.asarray(valid, dtype=bool) & np.asarray(footprint, dtype=bool)
    if include_riedel_vent:
        p_all = fit_riedelvent_single_loqo(
            X_foot,
            footprint,
            valid_b,
            quad,
            label_mask,
            feature_cols=FULL_INDICES,
            excluded_mask=excluded_mask,
            guard_px=guard_px,
            neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio,
            max_pos_samples=max_pos_samples,
            seed=int(seed),
            max_iter=max_iter,
        )
        p_sub = fit_riedelvent_single_loqo(
            X_foot,
            footprint,
            valid_b,
            quad,
            label_mask,
            feature_cols=RIEDEL_SUBSURF_INDICES,
            excluded_mask=excluded_mask,
            guard_px=guard_px,
            neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio,
            max_pos_samples=max_pos_samples,
            seed=int(seed) + 13,
            max_iter=max_iter,
        )
        raw_proba = (np.float32(0.45) * p_all + np.float32(0.55) * p_sub).astype(np.float32)
    else:
        novent_sub = (0, 3, 4, 6, 7, 8) + GROUP_C_SUBSURF_INDICES
        p_all = fit_riedelvent_single_loqo(
            X_foot,
            footprint,
            valid_b,
            quad,
            label_mask,
            feature_cols=ABLATED_NOVENT_INDICES,
            excluded_mask=excluded_mask,
            guard_px=guard_px,
            neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio,
            max_pos_samples=max_pos_samples,
            seed=int(seed),
            max_iter=max_iter,
        )
        p_sub = fit_riedelvent_single_loqo(
            X_foot,
            footprint,
            valid_b,
            quad,
            label_mask,
            feature_cols=novent_sub,
            excluded_mask=excluded_mask,
            guard_px=guard_px,
            neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio,
            max_pos_samples=max_pos_samples,
            seed=int(seed) + 13,
            max_iter=max_iter,
        )
        raw_proba = (np.float32(0.45) * p_all + np.float32(0.55) * p_sub).astype(np.float32)

    cal_proba = calibrate_quadrant_probabilities(
        raw_proba, valid_b, quad, calib_weight=calib_weight, power_gamma=power_gamma
    )
    return {
        "raw_proba": raw_proba,
        "cal_proba": cal_proba,
    }


def build_riedelvent_crest_surface(
    proba_2d: np.ndarray,
    l_scarp10m: np.ndarray,
    l_knick: np.ndarray,
    l_sub: np.ndarray,
    valid: np.ndarray,
    *,
    l_riedel_flex: np.ndarray | None = None,
    scarp_weight: float = 0.72,
    knick_weight: float = 0.70,
    sub_weight: float = 1.05,
    riedel_weight: float = 1.38,
) -> dict[str, np.ndarray]:
    """Fuse LOQO fault posterior with 10 m sub-pixel scarp, 10m/100m knickzone, and Riedel/vent crests."""
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0), 0.0)
    sc = np.asarray(l_scarp10m, dtype=np.float32)
    kn = np.asarray(l_knick, dtype=np.float32)
    sb = np.asarray(l_sub, dtype=np.float32)

    if l_riedel_flex is not None:
        rf = np.asarray(l_riedel_flex, dtype=np.float32)
        e_line = np.maximum(
            np.float32(riedel_weight) * rf,
            np.maximum(
                np.float32(scarp_weight) * sc * (np.float32(0.45) + np.float32(0.55) * rf),
                np.maximum(
                    np.float32(knick_weight) * kn * (np.float32(0.50) + np.float32(0.50) * rf),
                    np.float32(sub_weight) * sb * (np.float32(0.55) + np.float32(0.45) * rf),
                ),
            ),
        )
    else:
        e_line = np.maximum(
            np.float32(0.70) * sc * (np.float32(0.45) + np.float32(0.55) * sb),
            np.maximum(
                np.float32(0.82) * kn * (np.float32(0.45) + np.float32(0.55) * sb),
                np.float32(1.32) * sb,
            ),
        )

    s_crest = np.where(valid_b, p * (np.float32(0.15) + np.float32(0.85) * e_line), 0.0).astype(
        np.float32
    )
    ridge_1d = directional_ridge_1d(s_crest, valid_b)
    return {
        "S_crest": s_crest,
        "E_line": np.where(valid_b, e_line, 0.0).astype(np.float32),
        "ridge_1d": ridge_1d,
    }
