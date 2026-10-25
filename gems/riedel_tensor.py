"""RIEDELTENSOR — 3D Laplace-Consistent Gravity-Gradient Tensor Invariants,
En-Echelon Riedel (R/R') Transtensional Relay Obliquity, Radiometric-Potential
Alteration Contact Coupling & Selective Province-Debiased LOQO.

Pre-registered in ``docs/HYPOTHESES_20261025_RIEDEL_TENSOR.md`` (Rank 1 candidate).

Physical Mechanisms & Mathematical Formulation
----------------------------------------------
1. **Laplace-Consistent 3D Gravity-Gradient Tensor Tilt & Step-Dipole Concordance**
   (Pedersen & Rasmussen 1990, *Geophysics* 55(12); Blakely 1995; Beiki 2010,
   *Geophysics* 75(6)):
   From isostatic gravity anomaly ``g`` (``Band 13``) and vertical gravity
   gradient ``g_z = dg/dz`` (``Band 11``), horizontal differentiation of ``g_z``
   yields the horizontal-vertical tensor components ``G_xz = d(g_z)/dx`` and
   ``G_yz = d(g_z)/dy``, with horizontal magnitude ``||g_hz||_2 = sqrt(G_xz^2 + G_yz^2)``.
   By Laplace's equation in source-free space (``d_xx g + d_yy g + d_zz g = 0``),
   the vertical-vertical tensor component is ``G_zz = -(d_xx g + d_yy g)``.
   Whereas ``g_z`` crosses zero over a steep fault contact, ``||g_hz||_2`` and the
   dimensionless **3D Gravity-Tensor Vertical-Gradient Tilt**:
     ``Theta_gz(x) = ||g_hz(x)||_2 / sqrt(||g_hz(x)||_2^2 + G_zz(x)^2 + eps^2)``
   form a sharp positive crest directly over the fault contact with ``1/z^3``
   depth localization, while the **Signed Step-Dipole Concordance**:
     ``D_gz(x) = max(0, -(grad_h g . g_hz) / (||grad_h g||_2 ||g_hz||_2 + eps)) * Theta_gz(x)``
   verifies a one-sided normal-fault footwall-to-hanging-wall density step.

2. **En-Echelon Synthetic Riedel (R / R') Transtensional Relay Obliquity**
   (Faulds & Hinz 2015, *World Geothermal Congress / NBMG*):
   Computes the acute axial angle ``Delta_theta(x) in [0, 90] deg`` between the
   shallow topographic structure-tensor strike ``theta_topo(x)`` and the composite
   deep potential-field (gravity + RTP magnetic) strike ``theta_deep(x)``.
   Unmapped Quaternary fault splays and blind geothermal upflow zones concentrate
   in synthetic Riedel (``R``, ``theta_R ~ 19 deg``) step-overs and conjugate
   (``R'``, ``theta_R' ~ 68 deg``) transfer relays gated by mesoscale dilatant shear:
     ``R_riedel(x) = exp(-(Delta_theta - 19 deg)^2 / (2 * 11^2)) * sqrt(C_topo * C_deep)``.

3. **3D Radiometric-Potential Alteration Contact Coupling**:
   Couples airborne gamma-ray potassium-metasomatism ``||grad_h(K/Th)||_2`` and
   uranium-redox ``||grad_h(U/Th)||_2`` contact gradients (``ext_geodawn_rad_u8.tif``)
   with ``max(Theta_gz, Tilt_RTP)`` and ``Band 17`` MT smectite clay-cap margins,
   separating fault-hosted hydrothermal alteration zones from rootless surficial
   ash-flow tuff contacts.

4. **Wallace Basal Piedmont Toe Concavity & Selective Branch Calibration**:
   Combines upward-concave basal slope-toe curvature ``lambda_+(nabla^2 z_det)``
   (Wallace 1977) with incised thalweg knickzones, 3D gravity-tensor ridges, and
   selective branch-specific LOQO province calibration (resolving
   ``#IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION``).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import rasterio

from gems57 import holdout as holdout_mod

from .breakline import spaced_top_mask
from .coulomb_loqo import (
    _grad_xy,
    _sat,
    directional_ridge_1d,
    gdr_blind_thermal_features,
    hessian_ridge_strength,
)
from .hydroconduit import (
    _clean_valid,
    coherence_and_strike_deg,
)
from .knick_loqo import (
    FEATURE_NAMES as KNICK_FEATURE_NAMES,
    calibrate_quadrant_probabilities,
    compute_knick_loqo_stack,
    fit_single_loqo,
)

__all__ = [
    "FEATURE_NAMES_36",
    "BRANCH_FULL_COLS",
    "BRANCH_DEBIASED_COLS",
    "BRANCH_TENSOR_SUB_COLS",
    "BRANCH_TOE_RIEDEL_COLS",
    "gravity_tensor_invariants",
    "riedel_relay_obliquity",
    "radiometric_potential_coupling",
    "wallace_basal_toe_concavity",
    "compute_riedel_tensor_stack",
    "build_riedel_tensor_feature_stack",
    "fit_predict_riedel_tensor_loqo",
    "build_riedel_tensor_crest_surface",
    "spaced_top_mask",
]

FEATURE_NAMES_36: tuple[str, ...] = tuple(KNICK_FEATURE_NAMES) + (
    "f31_tensor_tilt_gz",
    "f32_tensor_ghz_hess",
    "f33_tensor_dipole_concord",
    "f34_riedel_obliquity_r",
    "f35_rad_pot_concord",
    "f36_wallace_basal_toe",
)

# Branch 1: Full 36-feature model
BRANCH_FULL_COLS: tuple[int, ...] = tuple(range(36))

# Branch 2: Province-debiased 30-feature model (excludes raw elevation/cover [5, 6],
# raw regional gravity/basement [8, 11], and raw regional strain rates [17, 18])
BRANCH_DEBIASED_COLS: tuple[int, ...] = (
    0, 1, 2, 3, 4, 7, 9, 10, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23,
    24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
)

# Branch 3: Subsurface + Tensor + Riedel + Knickzone 31-feature model (excludes raw
# surface slope/Hessian [0, 1, 2, 5] and raw strain [18] so buried/subtle faults
# are scored purely on tensor, Riedel, knickzone, and basal-toe physics)
BRANCH_TENSOR_SUB_COLS: tuple[int, ...] = (
    3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23,
    24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
)

# Branch 4: Basal-Toe + Riedel + Tensor + Knickzone structural model (28 features)
BRANCH_TOE_RIEDEL_COLS: tuple[int, ...] = (
    3, 4, 7, 9, 10, 12, 13, 14, 15, 16, 19, 21, 22, 23,
    24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
)


def gravity_tensor_invariants(
    grav_iso: np.ndarray,
    grav_vg: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute Laplace-consistent 3D gravity-gradient tensor invariants.

    Parameters
    ----------
    grav_iso : 2D array
        Band 13 isostatic gravity anomaly ``g``.
    grav_vg : 2D array
        Band 11 vertical gravity gradient ``g_z = dg/dz``.
    valid : 2D bool array
        Valid footprint mask.

    Returns
    -------
    dict with keys:
      - ``tensor_tilt_gz`` : ``||g_hz||_2 / sqrt(||g_hz||_2^2 + G_zz^2 + eps^2)`` in ``[0, 1]``
      - ``tensor_ghz_hess`` : 1D Hessian ridge crest of ``||g_hz||_2``
      - ``tensor_dipole_concord`` : Signed normal-fault step-dipole concordance in ``[0, 1]``
    """
    valid_b = np.asarray(valid, dtype=bool)
    g_clean = _clean_valid(grav_iso, valid_b)
    gz_clean = _clean_valid(grav_vg, valid_b)

    # First horizontal derivatives of vertical gravity gradient: (G_yz, G_xz) = grad_h(g_z)
    gyz, gxz = _grad_xy(gz_clean, valid_b, sigma=1.6)
    ghz_mag = np.where(valid_b, np.hypot(gyz, gxz), 0.0).astype(np.float32)

    # Laplace's equation in source-free space: G_zz = -(G_xx + G_yy) = -nabla_h^2(g)
    gy, gx = _grad_xy(g_clean, valid_b, sigma=2.0)
    gyy, _ = np.gradient(gy.astype(np.float32))
    _, gxx = np.gradient(gx.astype(np.float32))
    gzz = np.where(valid_b, -(gxx + gyy), 0.0).astype(np.float32)
    del gxx, gyy

    ghz_rms = float(np.sqrt(np.mean(np.square(ghz_mag[valid_b])))) if np.any(valid_b) else 1.0
    gzz_rms = float(np.sqrt(np.mean(np.square(gzz[valid_b])))) if np.any(valid_b) else 1.0
    ghz_norm = ghz_mag / np.float32(max(ghz_rms, 1e-6))
    gzz_norm = np.abs(gzz) / np.float32(max(gzz_rms, 1e-6))

    eps = np.float32(0.25)
    tensor_tilt_gz = np.where(
        valid_b,
        ghz_norm / np.sqrt(ghz_norm * ghz_norm + gzz_norm * gzz_norm + eps * eps),
        0.0,
    ).astype(np.float32)

    ghz_hess_raw = hessian_ridge_strength(ghz_norm, valid_b, sigma=1.5)
    tensor_ghz_hess = _sat(ghz_hess_raw, 0.35)
    del ghz_hess_raw, ghz_norm, gzz_norm, gzz, ghz_mag

    g_mag = np.hypot(gy, gx)
    gz_mag = np.hypot(gyz, gxz)
    cos_anti = np.where(
        valid_b,
        -(gy * gyz + gx * gxz) / (g_mag * gz_mag + np.float32(1e-6)),
        0.0,
    ).astype(np.float32)
    del gy, gx, gyz, gxz, g_mag, gz_mag
    dipole_pos = np.clip(cos_anti, 0.0, 1.0)
    tensor_dipole_concord = np.where(
        valid_b,
        dipole_pos * tensor_tilt_gz,
        0.0,
    ).astype(np.float32)

    return {
        "tensor_tilt_gz": tensor_tilt_gz,
        "tensor_ghz_hess": tensor_ghz_hess,
        "tensor_dipole_concord": tensor_dipole_concord,
    }


def riedel_relay_obliquity(
    det_elev: np.ndarray,
    rtp: np.ndarray,
    grav_iso: np.ndarray,
    coulomb_meso: np.ndarray,
    valid: np.ndarray,
) -> np.ndarray:
    """Compute en-echelon synthetic Riedel (R/R') transtensional relay obliquity."""
    valid_b = np.asarray(valid, dtype=bool)
    coh_topo, az_topo_deg = coherence_and_strike_deg(det_elev, valid_b)
    coh_rtp, az_rtp_deg = coherence_and_strike_deg(rtp, valid_b)
    coh_grav, az_grav_deg = coherence_and_strike_deg(grav_iso, valid_b)

    az_topo = np.radians(az_topo_deg).astype(np.float32)
    az_rtp = np.radians(az_rtp_deg).astype(np.float32)
    az_grav = np.radians(az_grav_deg).astype(np.float32)
    del az_topo_deg, az_rtp_deg, az_grav_deg

    w_rtp = coh_rtp + np.float32(1e-5)
    w_grav = np.float32(0.85) * coh_grav + np.float32(1e-5)
    c2_deep = w_rtp * np.cos(2.0 * az_rtp) + w_grav * np.cos(2.0 * az_grav)
    s2_deep = w_rtp * np.sin(2.0 * az_rtp) + w_grav * np.sin(2.0 * az_grav)
    az_deep = (0.5 * np.arctan2(s2_deep, c2_deep)).astype(np.float32)
    coh_deep = np.maximum(coh_rtp, np.float32(0.85) * coh_grav).astype(np.float32)
    del coh_rtp, az_rtp, coh_grav, az_grav, c2_deep, s2_deep

    sin_dtheta = np.clip(np.abs(np.sin(az_topo - az_deep)), 0.0, 1.0)
    dtheta_deg = np.degrees(np.arcsin(sin_dtheta)).astype(np.float32)
    joint_coh = np.sqrt(np.maximum(coh_topo * coh_deep, 0.0)).astype(np.float32)
    del coh_topo, az_topo, az_deep, coh_deep, sin_dtheta

    r_synth = np.exp(-0.5 * np.square((dtheta_deg - np.float32(19.0)) / np.float32(11.0))).astype(np.float32)
    r_conj = np.exp(-0.5 * np.square((dtheta_deg - np.float32(68.0)) / np.float32(14.0))).astype(np.float32)
    del dtheta_deg

    strain_gate = np.float32(0.45) + np.float32(0.55) * np.clip(np.asarray(coulomb_meso, dtype=np.float32), 0.0, 1.0)
    riedel_r = np.where(
        valid_b,
        joint_coh * (np.float32(0.76) * r_synth + np.float32(0.24) * r_conj) * strain_gate,
        0.0,
    ).astype(np.float32)
    return riedel_r


def radiometric_potential_coupling(
    rad_k: np.ndarray,
    rad_th: np.ndarray,
    rad_u: np.ndarray,
    rtp_tilt: np.ndarray,
    tensor_tilt_gz: np.ndarray,
    mt_grad: np.ndarray,
    valid: np.ndarray,
) -> np.ndarray:
    """Compute 3D radiometric-potential alteration contact coupling."""
    valid_b = np.asarray(valid, dtype=bool)
    valid_rad = (
        valid_b
        & np.isfinite(rad_k)
        & np.isfinite(rad_th)
        & np.isfinite(rad_u)
        & (np.asarray(rad_th) > 0)
    )
    k_th_raw = np.where(
        valid_rad,
        np.asarray(rad_k, dtype=np.float32) / (np.asarray(rad_th, dtype=np.float32) + np.float32(1.0)),
        0.0,
    ).astype(np.float32)
    u_th_raw = np.where(
        valid_rad,
        np.asarray(rad_u, dtype=np.float32) / (np.asarray(rad_th, dtype=np.float32) + np.float32(1.0)),
        0.0,
    ).astype(np.float32)

    ky, kx = _grad_xy(k_th_raw, valid_rad, sigma=2.0)
    uy, ux = _grad_xy(u_th_raw, valid_rad, sigma=2.0)
    k_th_grad = np.where(valid_b, np.hypot(ky, kx), 0.0).astype(np.float32)
    u_th_grad = np.where(valid_b, np.hypot(uy, ux), 0.0).astype(np.float32)
    del k_th_raw, u_th_raw, ky, kx, uy, ux, valid_rad

    rad_edge = np.float32(0.55) * _sat(k_th_grad, 0.08) + np.float32(0.45) * _sat(u_th_grad, 0.05)
    pot_gate = np.maximum(np.asarray(tensor_tilt_gz, dtype=np.float32), np.asarray(rtp_tilt, dtype=np.float32))
    mt_gate = np.float32(0.60) + np.float32(0.40) * _sat(np.asarray(mt_grad, dtype=np.float32), 0.012)
    return np.where(valid_b, rad_edge * pot_gate * mt_gate, 0.0).astype(np.float32)


def wallace_basal_toe_concavity(
    det_elev: np.ndarray,
    elev_slope: np.ndarray,
    step_pol: np.ndarray,
    valid: np.ndarray,
) -> np.ndarray:
    """Compute Wallace (1977) upward-concave basal piedmont fault-toe curvature."""
    valid_b = np.asarray(valid, dtype=bool)
    z_clean = _clean_valid(det_elev, valid_b)
    concave_raw = hessian_ridge_strength(-z_clean, valid_b, sigma=1.6)
    concave_sat = _sat(concave_raw, 0.14)
    del concave_raw

    slope_deg = np.clip(_clean_valid(elev_slope, valid_b), 0.0, 60.0)
    apron_win = np.exp(-0.5 * np.square((slope_deg - np.float32(5.5)) / np.float32(5.0))).astype(np.float32)
    step_gate = np.float32(0.35) + np.float32(0.65) * np.clip(np.asarray(step_pol, dtype=np.float32), 0.0, 1.0)
    return np.where(valid_b, concave_sat * apron_win * step_gate, 0.0).astype(np.float32)


def compute_riedel_tensor_stack(
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
) -> dict[str, Any]:
    """Compute the 36 catalogue-free ``RIEDELTENSOR`` features and 1D localization channels."""
    foot = np.asarray(footprint, dtype=bool)
    base_res = compute_knick_loqo_stack(
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
    valid = base_res["valid"]
    X30 = base_res["X_foot"]
    n_foot = int(foot.sum())

    X = np.empty((n_foot, len(FEATURE_NAMES_36)), dtype=np.float32)
    X[:, :30] = X30
    del X30

    def _put(col: int, arr2d: np.ndarray) -> None:
        X[:, col] = np.nan_to_num(arr2d[foot], nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)

    def _get2d(col: int) -> np.ndarray:
        out = np.zeros(foot.shape, dtype=np.float32)
        out[foot] = X[:, col]
        return out

    # 1. Laplace-consistent 3D gravity-gradient tensor invariants (Cols 30, 31, 32)
    gtens = gravity_tensor_invariants(grav_anom, grav_vg, valid)
    tensor_tilt_gz = gtens["tensor_tilt_gz"]
    tensor_ghz_hess = gtens["tensor_ghz_hess"]
    tensor_dipole_concord = gtens["tensor_dipole_concord"]
    _put(30, tensor_tilt_gz)
    _put(31, tensor_ghz_hess)
    _put(32, tensor_dipole_concord)

    # 2. En-echelon synthetic Riedel (R / R') transtensional relay obliquity (Col 33)
    coulomb_meso_2d = _get2d(29)
    riedel_r = riedel_relay_obliquity(det_elev, rtp, grav_anom, coulomb_meso_2d, valid)
    _put(33, riedel_r)
    del coulomb_meso_2d

    # 3. 3D Radiometric-potential alteration contact coupling (Col 34)
    rtp_tilt_2d = _get2d(12)
    mt_grad_2d = _get2d(19)
    rad_pot = radiometric_potential_coupling(
        rad_k, rad_th, rad_u, rtp_tilt_2d, tensor_tilt_gz, mt_grad_2d, valid
    )
    _put(34, rad_pot)
    del rtp_tilt_2d, mt_grad_2d

    # 4. Wallace upward-concave basal piedmont fault-toe curvature (Col 35)
    mu_step_2d = _get2d(3)
    basal_toe = wallace_basal_toe_concavity(det_elev, det_elev_slope, mu_step_2d, valid)
    _put(35, basal_toe)
    del mu_step_2d

    # Enhanced subsurface + tensor + Riedel + basement + MT 1D localization channel
    base_grad_2d = _get2d(7)
    rtp_hess_2d = _get2d(14)
    poisson_conc_2d = _get2d(28)
    base_hess = _sat(hessian_ridge_strength(base_grad_2d, valid, sigma=1.8), 0.008)
    mt_hess = _sat(hessian_ridge_strength(mt_grad_2d, valid, sigma=1.8), 0.004)
    riedel_hess = _sat(hessian_ridge_strength(riedel_r, valid, sigma=1.6), 0.025)
    rtp_h_sat = _sat(rtp_hess_2d, 0.04)
    del base_grad_2d, rtp_hess_2d, mt_grad_2d

    l_tensor_sub = np.where(
        valid,
        np.float32(0.19) * tensor_ghz_hess
        + np.float32(0.12) * base_hess
        + np.float32(0.12) * mt_hess
        + np.float32(0.12) * riedel_hess
        + np.float32(0.20) * rtp_h_sat
        + np.float32(0.12) * poisson_conc_2d
        + np.float32(0.10) * tensor_dipole_concord
        + np.float32(0.10) * _sat(rad_pot, 0.18),
        0.0,
    ).astype(np.float32)
    del base_hess, mt_hess, riedel_hess, rtp_h_sat, poisson_conc_2d

    return {
        "X_foot": X,
        "valid": valid,
        "L_topo": base_res["L_topo"],
        "L_knick": base_res["L_knick"],
        "L_toe": basal_toe,
        "L_sub": l_tensor_sub,
    }


def build_riedel_tensor_feature_stack(
    data_dir: Path,
    stack_path: Path,
    rad_path: Path,
    gdr_csv_path: Path,
) -> dict[str, Any]:
    """Stream required bands from disk and construct the 36-feature ``RIEDELTENSOR`` stack."""
    with rasterio.open(data_dir / "sample_submission.tif") as ds_sub:
        sub_arr = ds_sub.read(1)
        footprint = np.isfinite(sub_arr)
        transform = ds_sub.transform
    del sub_arr

    with rasterio.open(data_dir / "existing_faults.tif") as ds_flt:
        cat_faults = (ds_flt.read(1) > 0) & footprint

    def _read_band(p: Path, idx: int) -> np.ndarray:
        with rasterio.open(p) as ds:
            return ds.read(idx, masked=True).filled(np.nan).astype(np.float32)

    rtp = _read_band(stack_path, 2)
    geod_2ndinv = _read_band(stack_path, 4)
    grav_slope = _read_band(stack_path, 5)
    geod_shearrate = _read_band(stack_path, 7)
    geod_dilaterate = _read_band(stack_path, 8)
    grav_vg = _read_band(stack_path, 11)
    det_elev = _read_band(stack_path, 12)
    grav_anom = _read_band(stack_path, 13)
    depth_to_base = _read_band(stack_path, 15)
    cond_surf = _read_band(stack_path, 17)
    grav_hg = _read_band(stack_path, 18)
    det_elev_slope = _read_band(stack_path, 19)

    with rasterio.open(rad_path) as ds_rad:
        rad_k = ds_rad.read(1)
        rad_th = ds_rad.read(2)
        rad_u = ds_rad.read(3)

    valid_base = (
        footprint
        & np.isfinite(det_elev) & (det_elev > -1e30)
        & np.isfinite(det_elev_slope) & (det_elev_slope > -1e30)
        & np.isfinite(rtp) & (rtp > -1e30)
    )
    gdr_res = gdr_blind_thermal_features(gdr_csv_path, footprint.shape, valid_base, sigma_px=14.0)
    gdr_plume = gdr_res["plume_feat"]

    res = compute_riedel_tensor_stack(
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
        gdr_plume_feat=gdr_plume,
        footprint=footprint,
    )
    res["footprint"] = footprint
    res["cat_faults"] = cat_faults
    res["quad"] = holdout_mod.quadrant_ids(footprint)
    res["transform"] = transform
    return res


def fit_predict_riedel_tensor_loqo(
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
    max_iter: int = 185,
    w_full: float = 0.22,
    w_debiased: float = 0.28,
    w_tensor_sub: float = 0.28,
    w_toe_riedel: float = 0.22,
    calib_weight_sub: float = 0.80,
    calib_weight_full: float = 0.45,
    power_gamma: float = 3.2,
) -> dict[str, np.ndarray]:
    """Fit 4-branch ``RIEDELTENSOR`` LOQO ensemble with selective province calibration."""
    valid_b = np.asarray(valid, dtype=bool) & np.asarray(footprint, dtype=bool)
    p_full = fit_single_loqo(
        X_foot,
        footprint,
        valid_b,
        quad,
        label_mask,
        feature_cols=BRANCH_FULL_COLS,
        excluded_mask=excluded_mask,
        guard_px=guard_px,
        neg_buffer_px=neg_buffer_px,
        neg_pos_ratio=neg_pos_ratio,
        seed=seed,
        max_iter=max_iter,
    )
    p_debiased = fit_single_loqo(
        X_foot,
        footprint,
        valid_b,
        quad,
        label_mask,
        feature_cols=BRANCH_DEBIASED_COLS,
        excluded_mask=excluded_mask,
        guard_px=guard_px,
        neg_buffer_px=neg_buffer_px,
        neg_pos_ratio=neg_pos_ratio,
        seed=seed + 31,
        max_iter=max_iter,
    )
    p_tensor_sub = fit_single_loqo(
        X_foot,
        footprint,
        valid_b,
        quad,
        label_mask,
        feature_cols=BRANCH_TENSOR_SUB_COLS,
        excluded_mask=excluded_mask,
        guard_px=guard_px,
        neg_buffer_px=neg_buffer_px,
        neg_pos_ratio=neg_pos_ratio,
        seed=seed + 67,
        max_iter=max_iter,
    )
    p_toe_riedel = fit_single_loqo(
        X_foot,
        footprint,
        valid_b,
        quad,
        label_mask,
        feature_cols=BRANCH_TOE_RIEDEL_COLS,
        excluded_mask=excluded_mask,
        guard_px=guard_px,
        neg_buffer_px=neg_buffer_px,
        neg_pos_ratio=neg_pos_ratio,
        seed=seed + 103,
        max_iter=max_iter,
    )

    w_sum = float(w_full + w_debiased + w_tensor_sub + w_toe_riedel)
    if w_sum <= 0.0:
        raise ValueError("Sum of branch weights must be positive")

    raw_proba = np.where(
        valid_b,
        (
            np.float32(w_full) * p_full
            + np.float32(w_debiased) * p_debiased
            + np.float32(w_tensor_sub) * p_tensor_sub
            + np.float32(w_toe_riedel) * p_toe_riedel
        )
        / np.float32(w_sum),
        0.0,
    ).astype(np.float32)

    w_sub_only = float(w_debiased + w_tensor_sub + w_toe_riedel)
    raw_sub_only = np.where(
        valid_b,
        (
            np.float32(w_debiased) * p_debiased
            + np.float32(w_tensor_sub) * p_tensor_sub
            + np.float32(w_toe_riedel) * p_toe_riedel
        )
        / np.float32(max(w_sub_only, 1e-6)),
        0.0,
    ).astype(np.float32)

    cal_sub = calibrate_quadrant_probabilities(
        raw_sub_only,
        valid_b,
        quad,
        calib_weight=calib_weight_sub,
        power_gamma=power_gamma,
    )
    cal_full = calibrate_quadrant_probabilities(
        p_full,
        valid_b,
        quad,
        calib_weight=calib_weight_full,
        power_gamma=max(2.2, float(power_gamma) - 0.4),
    )

    cal_proba = np.where(
        valid_b,
        (np.float32(w_full) * cal_full + np.float32(w_sub_only) * cal_sub) / np.float32(w_sum),
        0.0,
    ).astype(np.float32)

    return {
        "proba_full": p_full,
        "proba_debiased": p_debiased,
        "proba_tensor_sub": p_tensor_sub,
        "proba_toe_riedel": p_toe_riedel,
        "proba_raw": raw_proba,
        "proba_calibrated": cal_proba,
    }


def build_riedel_tensor_crest_surface(
    proba_2d: np.ndarray,
    l_topo: np.ndarray,
    l_toe: np.ndarray,
    l_knick: np.ndarray,
    l_sub: np.ndarray,
    valid: np.ndarray,
    *,
    topo_weight: float = 0.12,
    toe_weight: float = 0.58,
    knick_weight: float = 0.80,
    sub_weight: float = 1.65,
) -> dict[str, np.ndarray]:
    """Combine LOQO fault probability with 1D multi-physics (scarp + basal-toe + knick + tensor) crests."""
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0), 0.0)

    c_topo = np.float32(topo_weight) * np.asarray(l_topo, dtype=np.float32)
    c_toe = np.float32(toe_weight) * np.asarray(l_toe, dtype=np.float32)
    c_knick = np.float32(knick_weight) * np.asarray(l_knick, dtype=np.float32)
    c_sub = np.float32(sub_weight) * np.asarray(l_sub, dtype=np.float32)

    e_line = np.maximum(np.maximum(c_topo, c_toe), np.maximum(c_knick, c_sub)).astype(np.float32)
    s_crest = np.where(valid_b, p * (np.float32(0.14) + np.float32(0.86) * e_line), 0.0).astype(np.float32)
    ridge_1d = directional_ridge_1d(s_crest, valid_b)
    return {
        "S_crest": s_crest,
        "E_line": np.where(valid_b, e_line, 0.0).astype(np.float32),
        "ridge_1d": ridge_1d,
    }
