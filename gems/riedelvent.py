"""RIEDELVENT lane: Transtensional Riedel R/R' Obliquity & 3D Gravity-Tensor
Step-Over Valve + USGS 3DEP 10 m Sub-Pixel Scarps + Tufa-Deconfounded INGENIOUS
Hydrothermal Vents + Möbius-DTI Additive Tail.

Pre-registered specification: ``docs/HYPOTHESES_20261025_RIEDELVENT.md``.

Key physical & engineering guarantees
-------------------------------------
1. **Verified GDAL Band-Tag Assertions (Fixes #IR-92-VENTSCARP-BAND-INDEX-MISATTRIBUTION)**:
   On opening ``training_features.tif``, ``assert_training_band_tags`` verifies exact
   GDAL ``band_name`` metadata for every consumed band (including ``Band 2 = rtp``,
   ``Band 3 = tmi_hg``, ``Band 4 = geod_2ndinv``, ``Band 5 = iso_grav_anom_slope``,
   ``Band 7 = geod_shearrate``, ``Band 8 = geod_dilaterate``, ``Band 11 = iso_grav_anom_vg``,
   ``Band 12 = det_elev``, ``Band 13 = iso_grav_anom``, ``Band 15 = depth_to_base_surf``,
   ``Band 17 = cond_surf``, ``Band 18 = iso_grav_anom_hg``, ``Band 19 = det_elev_slope``).
2. **Zero Fault-Catalogue Dependence**:
   ``build_riedelvent_stack`` never opens or receives ``existing_faults.tif`` or
   ``labels.tif``, and ``_rasterize_active_thermal_springs`` reads only ``(row, col, temp_c)``
   from ``gdr_wellspring_in_footprint.csv``. All 32 features are 100% invariant between
   static deployment and draw-blind ``HOLDOUT-DTI`` folds.
3. **Strict Leave-One-Quadrant-Out (LOQO) Cross-Fitting**:
   Each quadrant ``q in {0, 1, 2, 3}`` is scored exclusively by regularized
   ``HistGradientBoostingClassifier`` ensembles trained on ``quad != q`` eroded by
   a ``>= 1.2 km`` (``12 px``) spatial guard band and ``> 500 m`` (``5 px``) negative
   label buffer, followed by label-free within-quadrant quantile calibration.
4. **Low-RSS Streaming (< 1.4 GiB Peak)**:
   Streams individual ``float32`` bands and packs only footprint pixels
   (``5,167,373 x 32``, ~661 MB ``float32``) so execution stays comfortably inside
   a 3.8 GiB zero-swap container.
"""
from __future__ import annotations

from dataclasses import dataclass
import gc
from pathlib import Path
import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter

from .apronridge import directional_ridge_1d
from .breakline import percentile_rank, spaced_top_mask
from .coulomb_loqo import _grad_xy, coulomb_tendencies, hessian_ridge_strength
from .hydroconduit import _clean_valid, coherence_and_strike_deg, cross_strike_monotonicity
from .knick_loqo import (
    calibrate_quadrant_probabilities,
    fit_single_loqo,
    mesoscale_zscore,
    thalweg_concavity_strength,
)
from .ventscarp import (
    _decode_u8_band,
    _rasterize_2m_temperature_probes,
    _rasterize_active_thermal_springs,
    _rasterize_paleo_vents,
    anisotropic_strike_plume,
    subpixel_scarp_excess,
)

EXPECTED_GRID_H: int = 3730
EXPECTED_GRID_W: int = 3292

EXPECTED_TRAINING_BAND_TAGS: dict[int, str] = {
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

RIEDELVENT_FEATURE_NAMES: tuple[str, ...] = (
    # Group A (0..8): 3DEP 10 m sub-pixel scarp + 10 m chi/ksn + 100 m thalweg knickzones
    "dem10_scarp_excess_max",
    "dem10_scarp_excess_p90",
    "dem10_subpixel_dispersion",
    "dem10_wallace_curv",
    "dem10_linear_coherence",
    "dem10_steep_step_grad",
    "fluvial_chi_step_10m",
    "fluvial_ksn_10m",
    "thalweg_knickzone_100m",
    # Group B (9..14): TENSOR-RIEDEL 3D gravity-tensor step-over & R/R' strike obliquity
    "grav_tensor_3d_stepover",
    "grav_tensor_as_amp",
    "riedel_synthetic_R_20deg",
    "riedel_conjugate_Rprime_72deg",
    "riedel_oblique_excess",
    "transtensional_riedel_pump",
    # Group C (15..22): Tufa-deconfounded INGENIOUS hydrothermal vents, 2m probes & alteration
    "paleo_vent_aniso_plume",
    "probe_2mdab_aniso_plume",
    "active_thermal_spring_aniso",
    "unified_vent_district_halo",
    "rad_k_th_adularia_z",
    "rad_u_th_redox_z",
    "mag_shallow_demag_anom",
    "mt_claycap_tmi_hg_valve",
    # Group D (23..31): Tag-verified subsurface potential fields, Coulomb strain & Lahontan null
    "grav_tilt_edge_b13_b11",
    "dip_concord_z10_grav13",
    "ew_scarp_b18_polarity",
    "poisson_mag_grav_concord",
    "basement_depth_step_grad",
    "coulomb_dilation_slip",
    "geod_shear_mesoscale_z",
    "geod_dilat_mesoscale_z",
    "lahontan_shoreline_null",
)

GROUP_A_INDICES: tuple[int, ...] = tuple(range(0, 9))
GROUP_B_RIEDEL_INDICES: tuple[int, ...] = tuple(range(9, 15))
GROUP_C_VENT_INDICES: tuple[int, ...] = tuple(range(15, 23))
GROUP_D_SUBSURF_INDICES: tuple[int, ...] = tuple(range(23, 32))

# Pre-registered Arm 2 ablation subset: drops Group B (TENSOR-RIEDEL) and Group C (Vents/Alteration)
COLLINEAR_NOVENT_INDICES: tuple[int, ...] = GROUP_A_INDICES + GROUP_D_SUBSURF_INDICES

# Four physically orthogonalized LOQO sub-ensembles for Arm 1 & Arm 3:
PROVINCE_DEBIASED_INDICES: tuple[int, ...] = tuple(
    i for i in range(len(RIEDELVENT_FEATURE_NAMES)) if i not in (18, 29, 30)
)
RIEDEL_SUBSURF_KNICK_INDICES: tuple[int, ...] = (0, 1, 4, 6, 7, 8) + GROUP_B_RIEDEL_INDICES + GROUP_D_SUBSURF_INDICES
HYDROTHERMAL_RIEDEL_SCARP_INDICES: tuple[int, ...] = GROUP_A_INDICES + GROUP_B_RIEDEL_INDICES + GROUP_C_VENT_INDICES + (31,)

RIEDELVENT_BRANCH_SPECS: tuple[tuple[str, tuple[int, ...], float], ...] = (
    ("full_riedelvent", tuple(range(len(RIEDELVENT_FEATURE_NAMES))), 0.22),
    ("province_debiased", PROVINCE_DEBIASED_INDICES, 0.28),
    ("riedel_subsurf_knick", RIEDEL_SUBSURF_KNICK_INDICES, 0.28),
    ("hydrothermal_riedel_scarp", HYDROTHERMAL_RIEDEL_SCARP_INDICES, 0.22),
)

COLLINEAR_NOVENT_BRANCH_SPECS: tuple[tuple[str, tuple[int, ...], float], ...] = (
    ("collinear_all", COLLINEAR_NOVENT_INDICES, 0.50),
    (
        "collinear_debiased",
        tuple(i for i in COLLINEAR_NOVENT_INDICES if i not in (29, 30)),
        0.50,
    ),
)


@dataclass
class RiedelVentStack:
    """Memory-packed zero-catalogue feature matrix + continuous localization channels."""

    X_foot: np.ndarray  # (n_foot, 32) float32
    footprint: np.ndarray  # (H, W) bool
    valid: np.ndarray  # (H, W) bool
    L_scarp10m: np.ndarray  # (H, W) float32 in [0, 1]
    L_riedel: np.ndarray  # (H, W) float32 in [0, 1]
    L_knick: np.ndarray  # (H, W) float32 in [0, 1]
    L_subsurf: np.ndarray  # (H, W) float32 in [0, 1]
    L_topo100: np.ndarray  # (H, W) float32 in [0, 1]
    L_vent_amp: np.ndarray  # (H, W) float32 >= 1.0
    feature_names: tuple[str, ...]
    meta: dict[str, object]


def assert_training_band_tags(
    src: rasterio.DatasetReader,
    band_indices: list[int] | tuple[int, ...] | None = None,
) -> None:
    """Verify exact GDAL ``band_name`` tags on ``training_features.tif``."""
    check_ids = tuple(EXPECTED_TRAINING_BAND_TAGS.keys()) if band_indices is None else tuple(band_indices)
    for b in check_ids:
        expected = EXPECTED_TRAINING_BAND_TAGS[b]
        tags = src.tags(b)
        actual = tags.get("band_name")
        if actual != expected:
            raise ValueError(
                f"training_features.tif Band {b} expected band_name={expected!r}, got {actual!r}"
            )


def _sat_pos(arr: np.ndarray, c0: float) -> np.ndarray:
    """Monotone local saturating transform ``max(x, 0) / (max(x, 0) + c0)`` in ``[0, 1)``."""
    pos = np.maximum(np.asarray(arr, dtype=np.float32), 0.0)
    return (pos / (pos + np.float32(c0))).astype(np.float32)


def _smooth_valid(arr: np.ndarray, valid: np.ndarray, sigma_px: float) -> np.ndarray:
    u = _clean_valid(arr, valid)
    if sigma_px > 0.0:
        u = gaussian_filter(u, float(sigma_px)).astype(np.float32)
    return u


def _decode_i16_band(ds: rasterio.DatasetReader, band_idx: int, scale: float = 1.0) -> np.ndarray:
    raw = ds.read(band_idx)
    nodata = ds.nodatavals[band_idx - 1]
    out = np.zeros(raw.shape, dtype=np.float32)
    ok = raw != nodata if nodata is not None else np.ones(raw.shape, dtype=bool)
    out[ok] = raw[ok].astype(np.float32) * np.float32(scale)
    return out


def gravity_gradient_tensor_invariants(
    grav_anom: np.ndarray,
    grav_vg: np.ndarray,
    valid: np.ndarray,
    sigma_px: float = 2.2,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute Pedersen & Rasmussen (1990) 2D horizontal gravity gradient tensor invariants.

    Returns
    -------
    stepover_3d : float32 (H, W) in [0, 1]
        ``(4 |lambda_1 lambda_2| / (lambda_1^2 + lambda_2^2 + eps)) * pct_rank(||G_AS||)``.
        Vanishes (``-> 0``) on infinite 2D planar steps and peaks (``-> 1``) at 3D
        relay-ramp breaches, fault terminations, and structural intersections.
    log_as_amp : float32 (H, W) >= 0
        ``log(1 + ||G_AS||)`` tensor analytic-signal amplitude.
    gy, gx : float32 (H, W)
        First horizontal derivatives of smoothed ``grav_anom``.
    """
    valid_b = np.asarray(valid, dtype=bool)
    g_sm = _smooth_valid(grav_anom, valid_b, sigma_px=float(sigma_px))
    gy, gx = np.gradient(g_sm)
    gy = gy.astype(np.float32)
    gx = gx.astype(np.float32)
    gyy, gxy1 = np.gradient(gy)
    gxy2, gxx = np.gradient(gx)
    gxy = (0.5 * (gxy1 + gxy2)).astype(np.float32)
    gxx = gxx.astype(np.float32)
    gyy = gyy.astype(np.float32)
    del g_sm, gxy1, gxy2

    tr = (gxx + gyy).astype(np.float32)
    rad = np.sqrt((gxx - gyy) ** 2 + np.float32(4.0) * gxy * gxy).astype(np.float32)
    lam1 = (0.5 * (tr + rad)).astype(np.float32)
    lam2 = (0.5 * (tr - rad)).astype(np.float32)
    del tr, rad

    gz = (np.float32(0.10) * _smooth_valid(grav_vg, valid_b, sigma_px=1.2)).astype(np.float32)
    as_amp = np.sqrt(gxx * gxx + np.float32(2.0) * gxy * gxy + gyy * gyy + gz * gz).astype(np.float32)
    del gxx, gxy, gyy, gz

    dim_ratio = (
        np.float32(4.0)
        * np.abs(lam1 * lam2)
        / (lam1 * lam1 + lam2 * lam2 + np.float32(1e-5))
    ).astype(np.float32)
    del lam1, lam2

    dim_ratio = np.clip(dim_ratio, 0.0, 1.0)
    as_rank = percentile_rank(as_amp, valid_b)
    stepover_3d = np.where(valid_b, dim_ratio * as_rank, 0.0).astype(np.float32)
    log_as_amp = np.where(valid_b, np.log1p(as_amp), 0.0).astype(np.float32)
    gy[~valid_b] = 0.0
    gx[~valid_b] = 0.0
    return stepover_3d, log_as_amp, gy, gx


def riedel_obliquity_couplings(
    surf_gy: np.ndarray,
    surf_gx: np.ndarray,
    base_gy: np.ndarray,
    base_gx: np.ndarray,
    stepover_3d: np.ndarray,
    shear_z: np.ndarray,
    dilat_z: np.ndarray,
    valid: np.ndarray,
    mu_r_deg: float = 20.0,
    sigma_r_deg: float = 8.5,
    mu_rprime_deg: float = 72.0,
    sigma_rprime_deg: float = 9.5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute Tchalenko (1970) synthetic R (20 deg) & antithetic R' (72 deg) strike obliquity."""
    valid_b = np.asarray(valid, dtype=bool)
    s_mag = np.hypot(surf_gy, surf_gx).astype(np.float32)
    b_mag = np.hypot(base_gy, base_gx).astype(np.float32)

    cos_dtheta = np.clip(
        np.abs(surf_gy * base_gy + surf_gx * base_gx) / (s_mag * b_mag + np.float32(1e-6)),
        0.0,
        1.0,
    ).astype(np.float32)
    dtheta_deg = np.degrees(np.arccos(cos_dtheta)).astype(np.float32)
    del cos_dtheta

    edge_prod = np.sqrt(
        percentile_rank(s_mag, valid_b) * percentile_rank(b_mag, valid_b)
    ).astype(np.float32)
    del s_mag, b_mag

    r_syn = (
        np.exp(-0.5 * ((dtheta_deg - np.float32(mu_r_deg)) / np.float32(sigma_r_deg)) ** 2)
        * edge_prod
    ).astype(np.float32)
    r_conj = (
        np.exp(-0.5 * ((dtheta_deg - np.float32(mu_rprime_deg)) / np.float32(sigma_rprime_deg)) ** 2)
        * edge_prod
    ).astype(np.float32)
    r_collin = (
        np.exp(-0.5 * (dtheta_deg / np.float32(sigma_r_deg)) ** 2) * edge_prod
    ).astype(np.float32)
    del dtheta_deg, edge_prod

    r_excess = np.maximum(np.maximum(r_syn, r_conj) - r_collin, 0.0).astype(np.float32)
    del r_collin

    shear_gate = (np.float32(1.0) / (np.float32(1.0) + np.exp(-np.clip(shear_z, -6.0, 6.0)))).astype(
        np.float32
    )
    dilat_gate = (
        np.float32(0.5)
        + np.float32(0.5) / (np.float32(1.0) + np.exp(-np.clip(dilat_z, -6.0, 6.0)))
    ).astype(np.float32)
    trans_pump = (
        (np.float32(0.55) * r_syn + np.float32(0.25) * r_conj + np.float32(0.20) * stepover_3d)
        * shear_gate
        * dilat_gate
    ).astype(np.float32)

    for arr in (r_syn, r_conj, r_excess, trans_pump):
        arr[~valid_b] = 0.0
    return r_syn, r_conj, r_excess, trans_pump


def build_riedelvent_crest_surface(
    proba_2d: np.ndarray,
    stack: RiedelVentStack,
    *,
    ablation_collinear_novent: bool = False,
) -> dict[str, np.ndarray]:
    """Fuse LOQO fault posterior with 1D Riedel/10m-scarp/knick/subsurface localization."""
    valid_b = np.asarray(stack.valid, dtype=bool) & np.asarray(stack.footprint, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0), 0.0)

    if ablation_collinear_novent:
        e_line = np.maximum(
            np.float32(0.95) * stack.L_topo100,
            np.maximum(
                np.float32(0.88) * stack.L_scarp10m,
                np.maximum(
                    np.float32(0.86) * stack.L_knick,
                    np.float32(1.12) * stack.L_subsurf,
                ),
            ),
        ).astype(np.float32)
    else:
        e_base = np.maximum(
            np.float32(0.96) * stack.L_scarp10m,
            np.maximum(
                np.float32(1.06) * stack.L_riedel,
                np.maximum(
                    np.float32(0.92) * stack.L_knick,
                    np.float32(1.18) * stack.L_subsurf,
                ),
            ),
        )
        e_line = (e_base * stack.L_vent_amp).astype(np.float32)

    s_crest = np.where(valid_b, p * (np.float32(0.14) + np.float32(0.86) * e_line), 0.0).astype(
        np.float32
    )
    ridge_1d = directional_ridge_1d(s_crest, valid_b)
    s_max = float(s_crest.max())
    s_unit = (s_crest / np.float32(s_max)).astype(np.float32) if s_max > 0.0 else s_crest.copy()
    return {
        "S_crest": s_crest,
        "S_crest_unit": np.clip(s_unit, 0.0, 1.0).astype(np.float32),
        "E_line": np.where(valid_b, e_line, 0.0).astype(np.float32),
        "ridge_1d": ridge_1d,
    }


def emit_binary_crest_dots(
    s_crest: np.ndarray,
    cand_pool: np.ndarray,
    *,
    n_dots: int = 37_654,
    min_dist_px: float = 3.2,
    cand_cap: int = 500_000,
) -> np.ndarray:
    """Emit deterministic binary ``{0.0, 1.0}`` spaced 1D crest dots."""
    chosen = spaced_top_mask(
        s_crest,
        cand_pool,
        int(n_dots),
        min_dist_px=float(min_dist_px),
        cand_cap=int(cand_cap),
        require_full=False,
    )
    return chosen.astype(np.float32)


def build_additive_mobius_tail_allocation(
    s_crest: np.ndarray,
    cand_pool: np.ndarray,
    *,
    n_primary: int = 37_654,
    n_total: int = 85_000,
    min_dist_px: float = 3.0,
    tail_hi: float = 0.60,
    tail_lo: float = 0.30,
    cand_cap: int = 650_000,
) -> np.ndarray:
    """Möbius-DTI additive recall tail with ZERO dilution of primary crests.

    Ranks ``1..n_primary`` receive exact weight ``1.0``; secondary spaced crests
    ``n_primary+1..n_total`` receive monotone weights linearly ramped from
    ``tail_hi`` to ``tail_lo``.
    """
    if n_total < n_primary or n_primary <= 0:
        raise ValueError(f"Require 0 < n_primary <= n_total, got {n_primary}, {n_total}")
    if not (0.0 < tail_lo <= tail_hi <= 1.0):
        raise ValueError(f"Require 0 < tail_lo <= tail_hi <= 1, got {tail_lo}, {tail_hi}")

    cand_b = np.asarray(cand_pool, dtype=bool)
    chosen = spaced_top_mask(
        s_crest,
        cand_b,
        int(n_total),
        min_dist_px=float(min_dist_px),
        cand_cap=int(cand_cap),
        require_full=False,
    )
    ys, xs = np.nonzero(chosen)
    out = np.zeros(s_crest.shape, dtype=np.float32)
    if ys.size == 0:
        return out

    scores = s_crest[ys, xs].astype(np.float64)
    order = np.lexsort((xs, ys, -scores))
    ys = ys[order]
    xs = xs[order]
    k = ys.size

    k_prim = min(int(n_primary), k)
    out[ys[:k_prim], xs[:k_prim]] = np.float32(1.0)
    if k > k_prim:
        n_tail = k - k_prim
        if n_tail == 1:
            tail_w = np.array([tail_hi], dtype=np.float32)
        else:
            tail_w = np.linspace(float(tail_hi), float(tail_lo), n_tail, dtype=np.float32)
        out[ys[k_prim:], xs[k_prim:]] = np.clip(tail_w, np.float32(1e-4), np.float32(1.0))

    out[~cand_b] = 0.0
    return np.clip(out, 0.0, 1.0).astype(np.float32)


def build_riedelvent_stack(
    training_tif: Path,
    topo10m_tif: Path,
    chi10m_tif: Path,
    geodawn_rad_tif: Path,
    geodawn_ext_tif: Path,
    paleo_zip: Path,
    probe_2m_zip: Path,
    wellspring_csv: Path,
    footprint: np.ndarray,
) -> RiedelVentStack:
    """Build the 32-feature zero-catalogue ``RIEDELVENT`` matrix and 1D localizers."""
    foot = np.asarray(footprint, dtype=bool)
    if foot.shape != (EXPECTED_GRID_H, EXPECTED_GRID_W):
        raise ValueError(f"Unexpected footprint shape: {foot.shape}")

    n_foot = int(foot.sum())
    n_feat = len(RIEDELVENT_FEATURE_NAMES)
    X = np.zeros((n_foot, n_feat), dtype=np.float32)

    def _read_tf(ds: rasterio.DatasetReader, b: int) -> np.ndarray:
        arr = ds.read(b, masked=True).filled(np.nan).astype(np.float32)
        arr[np.abs(arr) > 1e20] = np.nan
        return arr

    def _put(col: int, arr2d: np.ndarray) -> None:
        vals = np.asarray(arr2d, dtype=np.float32)[foot]
        vals = np.nan_to_num(vals, nan=0.0, posinf=0.0, neginf=0.0)
        X[:, col] = vals

    # ------------------------------------------------------------------
    # 1. Verify exact GDAL band tags on training_features.tif & load 100 m topo
    # ------------------------------------------------------------------
    with rasterio.open(training_tif) as ds_tf:
        assert_training_band_tags(ds_tf)
        tf_transform = ds_tf.transform
        b12_det_elev = _read_tf(ds_tf, 12)
        b19_slope100 = _read_tf(ds_tf, 19)

    valid = foot & np.isfinite(b12_det_elev) & np.isfinite(b19_slope100)
    b19_clean = np.where(valid, np.maximum(_clean_valid(b19_slope100, valid), 0.0), 0.0).astype(
        np.float32
    )
    del b19_slope100

    # ------------------------------------------------------------------
    # 2. Group A (0..8): USGS 3DEP 10 m Sub-Pixel Scarp + Chi/ksn + 100 m Thalweg Knickzones
    # ------------------------------------------------------------------
    with rasterio.open(topo10m_tif) as ds_t10:
        s10_p90 = _decode_u8_band(ds_t10, 1)
        s10_max = _decode_u8_band(ds_t10, 2)
        steep_f = _decode_u8_band(ds_t10, 3)
        s10_std = _decode_u8_band(ds_t10, 4)
        curv10 = _decode_u8_band(ds_t10, 6)
        asp_coh = _decode_u8_band(ds_t10, 7)
        hs_lin = _decode_u8_band(ds_t10, 8)
        dem10_z = _decode_u8_band(ds_t10, 9)

    scarp_excess_max = subpixel_scarp_excess(s10_max, b19_clean, valid)
    scarp_excess_p90 = subpixel_scarp_excess(s10_p90, np.float32(0.80) * b19_clean, valid)
    subpix_disp = np.where(valid, s10_std / (s10_p90 + np.float32(0.5)), 0.0).astype(np.float32)
    pied_gate = np.exp(-0.5 * (b19_clean / np.float32(14.0)) ** 2).astype(np.float32)
    wallace_curv = np.where(
        valid,
        np.log1p(np.maximum(curv10, 0.0)) * pied_gate * np.log1p(np.maximum(s10_max, 0.0)),
        0.0,
    ).astype(np.float32)
    lin_coh = np.where(valid, asp_coh * hs_lin, 0.0).astype(np.float32)
    sy_sf, sx_sf = _grad_xy(steep_f, valid, sigma=1.0)
    steep_step = np.where(valid, np.hypot(sy_sf, sx_sf), 0.0).astype(np.float32)
    del s10_max, steep_f, s10_std, curv10, asp_coh, hs_lin, pied_gate, sy_sf, sx_sf

    _put(0, scarp_excess_max)
    _put(1, scarp_excess_p90)
    _put(2, subpix_disp)
    _put(3, wallace_curv)
    _put(4, lin_coh)
    _put(5, steep_step)
    del subpix_disp

    with rasterio.open(chi10m_tif) as ds_chi:
        chi_step_max = _decode_i16_band(ds_chi, 1, scale=0.001)
        ksn10 = _decode_i16_band(ds_chi, 3, scale=1.0)
        log10_area = _decode_i16_band(ds_chi, 4, scale=0.001)

    area_gate = np.clip((log10_area - np.float32(3.5)) / np.float32(2.5), 0.0, 1.0).astype(np.float32)
    fluvial_chi_step = np.where(
        valid, np.log1p(np.maximum(chi_step_max, 0.0)) * area_gate, 0.0
    ).astype(np.float32)
    fluvial_ksn = np.where(
        valid, np.log1p(np.maximum(ksn10, 0.0)) * area_gate, 0.0
    ).astype(np.float32)
    del chi_step_max, ksn10, log10_area, area_gate

    _put(6, fluvial_chi_step)
    _put(7, fluvial_ksn)
    del fluvial_ksn

    # 100 m Incised Thalweg Concavity Knickzone
    log_s100 = np.log(b19_clean + np.float32(0.25)).astype(np.float32)
    lsy, lsx = _grad_xy(log_s100, valid, sigma=1.0)
    rel_break100 = np.where(valid, np.hypot(lsy, lsx), 0.0).astype(np.float32)
    del lsy, lsx
    hess_s12 = hessian_ridge_strength(log_s100, valid, sigma=1.2)
    del log_s100
    mu_step100 = cross_strike_monotonicity(
        b12_det_elev, valid, half_span_px=3, normal_sigma=3.0, elev_floor_m=0.5
    )
    thal_15 = thalweg_concavity_strength(b12_det_elev, valid, sigma=1.5)
    thal_30 = thalweg_concavity_strength(b12_det_elev, valid, sigma=3.0)
    thal_concav = np.maximum(thal_15, np.float32(0.75) * thal_30).astype(np.float32)
    del thal_15, thal_30
    thalweg_knick = np.where(
        valid,
        _sat_pos(thal_concav, 1.8) * _sat_pos(rel_break100, 0.045),
        0.0,
    ).astype(np.float32)
    del thal_concav
    _put(8, thalweg_knick)

    # Surface scarp gradient vector (blending 10 m sub-pixel p90 scarp + 100 m detrended elevation)
    surf_pot = (
        np.float32(0.65) * percentile_rank(s10_p90, valid)
        + np.float32(0.35) * percentile_rank(b12_det_elev, valid)
    ).astype(np.float32)
    surf_gy, surf_gx = _grad_xy(surf_pot, valid, sigma=1.3)
    del surf_pot, s10_p90

    # 10 m DEM horizontal gradient + Lake Lahontan 1330 m contour-parallel null prep
    z10_gy, z10_gx = _grad_xy(dem10_z, valid, sigma=1.5)
    z10_gnorm = np.hypot(z10_gy, z10_gx).astype(np.float32)
    lahontan_elev_band = np.exp(-0.5 * ((dem10_z - np.float32(1330.0)) / np.float32(55.0)) ** 2).astype(
        np.float32
    )
    del dem10_z

    coh_topo, az_topo = coherence_and_strike_deg(b12_det_elev, valid)
    zy100, zx100 = _grad_xy(b12_det_elev, valid, sigma=2.0)
    znorm100 = np.hypot(zy100, zx100).astype(np.float32)
    az_rad = np.radians(az_topo)
    cross_contour = np.where(
        valid,
        np.clip(
            np.abs((-np.cos(az_rad)) * zy100 + np.sin(az_rad) * zx100)
            / (znorm100 + np.float32(0.35)),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    del az_rad, zy100, zx100, znorm100, b12_det_elev, b19_clean
    gc.collect()

    # ------------------------------------------------------------------
    # 3. Group B (9..14) & Group D (23..31): Tag-Verified Gravity Tensor, Riedel & Subsurface
    # ------------------------------------------------------------------
    with rasterio.open(training_tif) as ds_tf:
        b2_rtp = _read_tf(ds_tf, 2)
        b3_tmi_hg = _read_tf(ds_tf, 3)
        b4_2ndinv = _read_tf(ds_tf, 4)
        b5_grav_slope = _read_tf(ds_tf, 5)
        b7_shear = _read_tf(ds_tf, 7)
        b8_dilat = _read_tf(ds_tf, 8)
        b11_grav_vg = _read_tf(ds_tf, 11)
        b13_grav = _read_tf(ds_tf, 13)
        b15_dbase = _read_tf(ds_tf, 15)
        b17_cond = _read_tf(ds_tf, 17)
        b18_grav_hg = _read_tf(ds_tf, 18)

    shear_z = mesoscale_zscore(b7_shear, valid, sigma_px=45.0, eps=0.25)
    dilat_z = mesoscale_zscore(b8_dilat, valid, sigma_px=45.0, eps=0.25)

    stepover_3d, log_as_amp, grav_gy, grav_gx = gravity_gradient_tensor_invariants(
        b13_grav, b11_grav_vg, valid, sigma_px=2.2
    )
    grav_gnorm = np.hypot(grav_gy, grav_gx).astype(np.float32)

    rtp_sm = _smooth_valid(b2_rtp, valid, sigma_px=1.2)
    rtp_gy, rtp_gx = np.gradient(rtp_sm)
    rtp_gy = rtp_gy.astype(np.float32)
    rtp_gx = rtp_gx.astype(np.float32)
    rtp_gnorm = np.hypot(rtp_gy, rtp_gx).astype(np.float32)
    ryy, _ = np.gradient(rtp_gy)
    _, rxx = np.gradient(rtp_gx)
    rtp_lap = (rxx + ryy).astype(np.float32)
    del rtp_sm, rxx, ryy
    coh_rtp, _ = coherence_and_strike_deg(b2_rtp, valid)
    rtp_tilt = np.where(
        valid,
        (rtp_gnorm / np.sqrt(rtp_gnorm * rtp_gnorm + rtp_lap * rtp_lap + np.float32(1.5 ** 2)))
        * coh_rtp,
        0.0,
    ).astype(np.float32)
    del rtp_lap, coh_rtp, b2_rtp

    base_pot = (
        np.float32(0.70) * percentile_rank(b13_grav, valid)
        + np.float32(0.30) * percentile_rank(rtp_gnorm, valid)
    ).astype(np.float32)
    base_gy, base_gx = _grad_xy(base_pot, valid, sigma=2.0)
    del base_pot, b13_grav

    r_syn, r_conj, r_excess, trans_pump = riedel_obliquity_couplings(
        surf_gy,
        surf_gx,
        base_gy,
        base_gx,
        stepover_3d,
        shear_z,
        dilat_z,
        valid,
    )
    del surf_gy, surf_gx, base_gy, base_gx

    _put(9, stepover_3d)
    _put(10, log_as_amp)
    _put(11, r_syn)
    _put(12, r_conj)
    _put(13, r_excess)
    _put(14, trans_pump)
    del log_as_amp

    # Group D (23..31)
    gs_pos = np.where(valid, np.maximum(_clean_valid(b5_grav_slope, valid), 0.0), 0.0).astype(
        np.float32
    )
    gvg_clean = _smooth_valid(b11_grav_vg, valid, sigma_px=1.0)
    grav_tilt = np.where(
        valid,
        gs_pos / np.sqrt(gs_pos * gs_pos + (np.float32(0.05) * gvg_clean) ** 2 + np.float32(0.02 ** 2)),
        0.0,
    ).astype(np.float32)
    del b5_grav_slope, b11_grav_vg, gs_pos, gvg_clean

    dip_concord_grav13 = np.where(
        valid,
        np.clip(
            (z10_gy * grav_gy + z10_gx * grav_gx) / (z10_gnorm * grav_gnorm + np.float32(1e-5)),
            -1.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    del z10_gy, z10_gnorm

    b18_clean = _smooth_valid(b18_grav_hg, valid, sigma_px=1.0)
    ew_polarity = np.where(
        valid,
        np.tanh(z10_gx / np.float32(6.0)) * np.tanh(b18_clean / np.float32(1.5)),
        0.0,
    ).astype(np.float32)
    del z10_gx, b18_grav_hg, b18_clean

    poisson_collin = np.where(
        valid,
        np.clip(
            np.abs(rtp_gy * grav_gy + rtp_gx * grav_gx) / (rtp_gnorm * grav_gnorm + np.float32(1e-4)),
            0.0,
            1.0,
        ),
        0.0,
    ).astype(np.float32)
    poisson_concord = np.where(
        valid,
        poisson_collin * np.sqrt(np.maximum(rtp_tilt * grav_tilt, 0.0)),
        0.0,
    ).astype(np.float32)
    del rtp_gy, rtp_gx, rtp_gnorm, grav_gy, grav_gx, grav_gnorm, poisson_collin

    db_pos = np.where(valid, np.maximum(_clean_valid(b15_dbase, valid), 0.0), 0.0).astype(np.float32)
    del b15_dbase
    dby, dbx = _grad_xy(np.log(db_pos + np.float32(10.0)).astype(np.float32), valid, sigma=2.0)
    db_step = np.where(valid, np.hypot(dby, dbx), 0.0).astype(np.float32)
    del dby, dbx
    base_depth_step = (
        np.float32(0.65) * percentile_rank(db_step, valid)
        + np.float32(0.35) * percentile_rank(np.log1p(db_pos), valid)
    ).astype(np.float32)
    del db_pos

    t_dil, t_slip = coulomb_tendencies(az_topo, b7_shear, b8_dilat, valid)
    s2i_rank = percentile_rank(np.maximum(_smooth_valid(b4_2ndinv, valid, sigma_px=2.0), 0.0), valid)
    coulomb_comb = np.where(
        valid,
        (np.float32(0.55) * t_dil + np.float32(0.45) * t_slip)
        * (np.float32(0.40) + np.float32(0.60) * s2i_rank),
        0.0,
    ).astype(np.float32)
    del az_topo, b7_shear, b8_dilat, b4_2ndinv, t_dil, t_slip, s2i_rank

    lahontan_null = np.where(
        valid,
        lahontan_elev_band
        * ((np.float32(1.0) - cross_contour) ** 2)
        * np.exp(-db_step / np.float32(0.04))
        * (np.float32(1.0) - np.float32(0.75) * grav_tilt),
        0.0,
    ).astype(np.float32)
    del lahontan_elev_band

    _put(23, grav_tilt)
    _put(24, dip_concord_grav13)
    _put(25, ew_polarity)
    _put(26, poisson_concord)
    _put(27, base_depth_step)
    _put(28, coulomb_comb)
    _put(29, shear_z)
    _put(30, dilat_z)
    _put(31, lahontan_null)
    del dip_concord_grav13, ew_polarity, poisson_concord, base_depth_step, coulomb_comb, shear_z, dilat_z, lahontan_null
    gc.collect()

    # ------------------------------------------------------------------
    # 4. Group C (15..22): Tufa-Deconfounded INGENIOUS Vents, 2m Probes & Alteration
    # ------------------------------------------------------------------
    paleo_imp, paleo_stats = _rasterize_paleo_vents(paleo_zip, tf_transform, foot.shape, valid)
    paleo_short = anisotropic_strike_plume(
        paleo_imp, valid, strike_deg_east_of_north=18.0, sigma_parallel_px=16.0, sigma_perp_px=6.5
    )
    paleo_meso = anisotropic_strike_plume(
        paleo_imp, valid, strike_deg_east_of_north=18.0, sigma_parallel_px=38.0, sigma_perp_px=15.0
    )
    paleo_plume = np.where(valid, np.log1p(12.0 * paleo_short + 4.0 * paleo_meso), 0.0).astype(np.float32)
    del paleo_imp, paleo_short

    probe_imp, probe_stats = _rasterize_2m_temperature_probes(
        probe_2m_zip, tf_transform, foot.shape, valid, dab_threshold_c=1.2
    )
    probe_short = anisotropic_strike_plume(
        probe_imp, valid, strike_deg_east_of_north=18.0, sigma_parallel_px=14.0, sigma_perp_px=6.0
    )
    probe_meso = anisotropic_strike_plume(
        probe_imp, valid, strike_deg_east_of_north=18.0, sigma_parallel_px=34.0, sigma_perp_px=14.0
    )
    probe_plume = np.where(valid, np.log1p(10.0 * probe_short + 3.5 * probe_meso), 0.0).astype(np.float32)
    del probe_imp, probe_short

    spring_imp, spring_stats = _rasterize_active_thermal_springs(
        wellspring_csv, foot.shape, valid, min_temp_c=30.0
    )
    spring_plume_raw = anisotropic_strike_plume(
        spring_imp, valid, strike_deg_east_of_north=18.0, sigma_parallel_px=18.0, sigma_perp_px=7.5
    )
    active_spring = np.where(valid, np.log1p(8.0 * spring_plume_raw), 0.0).astype(np.float32)
    del spring_imp, spring_plume_raw

    district_raw = (
        np.float32(0.45) * percentile_rank(paleo_meso, valid)
        + np.float32(0.30) * percentile_rank(probe_meso, valid)
        + np.float32(0.25) * percentile_rank(active_spring, valid)
    ).astype(np.float32)
    vent_district = _smooth_valid(district_raw, valid, sigma_px=55.0)
    del paleo_meso, probe_meso, district_raw

    with rasterio.open(geodawn_rad_tif) as ds_rad:
        rad_k = _decode_u8_band(ds_rad, 1)
        rad_th = _decode_u8_band(ds_rad, 2)
        rad_u = _decode_u8_band(ds_rad, 3)

    with rasterio.open(geodawn_ext_tif) as ds_ext:
        ext_uth = _decode_u8_band(ds_ext, 3)
        ext_tmi_up150 = _decode_u8_band(ds_ext, 4)

    k_th_raw = (np.maximum(rad_k, 0.0) / (np.maximum(rad_th, 0.0) + np.float32(0.35))).astype(np.float32)
    k_th_bg = _smooth_valid(k_th_raw, valid, 24.0)
    k_th_z = np.where(
        valid,
        (_smooth_valid(k_th_raw, valid, 1.5) - k_th_bg) / (np.float32(0.08) + np.abs(k_th_bg)),
        0.0,
    ).astype(np.float32)
    u_th_raw = (
        np.float32(0.5) * ext_uth
        + np.float32(0.5) * (np.maximum(rad_u, 0.0) / (np.maximum(rad_th, 0.0) + np.float32(0.35)))
    ).astype(np.float32)
    u_th_bg = _smooth_valid(u_th_raw, valid, 24.0)
    u_th_z = np.where(
        valid,
        (_smooth_valid(u_th_raw, valid, 1.5) - u_th_bg) / (np.float32(0.08) + np.abs(u_th_bg)),
        0.0,
    ).astype(np.float32)
    del rad_k, rad_th, rad_u, ext_uth, k_th_raw, k_th_bg, u_th_raw, u_th_bg

    demag_shallow = np.where(
        valid,
        _smooth_valid(ext_tmi_up150, valid, 18.0) - _smooth_valid(ext_tmi_up150, valid, 1.5),
        0.0,
    ).astype(np.float32)
    del ext_tmi_up150

    cy, cx = _grad_xy(
        np.log1p(np.maximum(_smooth_valid(b17_cond, valid, 1.2), 0.0)).astype(np.float32),
        valid,
        sigma=2.0,
    )
    cond_grad = np.where(valid, np.hypot(cy, cx), 0.0).astype(np.float32)
    del cy, cx
    tmi_hg_clean = np.maximum(_smooth_valid(b3_tmi_hg, valid, 1.0), 0.0)
    mt_claycap_valve = (
        np.float32(0.55) * percentile_rank(cond_grad, valid)
        + np.float32(0.45) * percentile_rank(np.log1p(tmi_hg_clean) * scarp_excess_p90, valid)
    ).astype(np.float32)
    del b17_cond, b3_tmi_hg, cond_grad, tmi_hg_clean

    _put(15, paleo_plume)
    _put(16, probe_plume)
    _put(17, active_spring)
    _put(18, vent_district)
    _put(19, k_th_z)
    _put(20, u_th_z)
    _put(21, demag_shallow)
    _put(22, mt_claycap_valve)
    del k_th_z, u_th_z, demag_shallow, mt_claycap_valve

    # ------------------------------------------------------------------
    # 5. Construct Continuous Localization Channels in [0, 1]
    # ------------------------------------------------------------------
    l_scarp10m = np.where(
        valid,
        np.float32(0.44) * _sat_pos(scarp_excess_max, 0.35)
        + np.float32(0.24) * _sat_pos(wallace_curv, 0.25)
        + np.float32(0.18) * _sat_pos(steep_step, 0.05)
        + np.float32(0.14) * np.clip(lin_coh, 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    del scarp_excess_max, scarp_excess_p90, wallace_curv, steep_step, lin_coh

    l_knick = np.where(
        valid,
        np.float32(0.54) * _sat_pos(fluvial_chi_step, 0.45)
        + np.float32(0.46) * _sat_pos(thalweg_knick * (np.float32(0.50) + np.float32(0.50) * cross_contour), 0.09),
        0.0,
    ).astype(np.float32)
    del fluvial_chi_step, thalweg_knick

    l_riedel = np.where(
        valid,
        np.float32(0.36) * percentile_rank(r_excess, valid)
        + np.float32(0.28) * percentile_rank(trans_pump, valid)
        + np.float32(0.20) * stepover_3d
        + np.float32(0.16) * np.maximum(r_syn, r_conj),
        0.0,
    ).astype(np.float32)
    del r_syn, r_conj, r_excess, trans_pump, stepover_3d

    l_subsurf = np.where(
        valid,
        np.float32(0.45) * grav_tilt
        + np.float32(0.35) * rtp_tilt
        + np.float32(0.20) * _sat_pos(db_step, 0.035),
        0.0,
    ).astype(np.float32)
    del grav_tilt, rtp_tilt, db_step

    l_topo100 = np.where(
        valid,
        np.float32(0.52) * _sat_pos(hess_s12, 0.06)
        + np.float32(0.48)
        * _sat_pos(rel_break100 * (np.float32(0.35) + np.float32(0.65) * mu_step100) * coh_topo, 0.04),
        0.0,
    ).astype(np.float32)
    del hess_s12, rel_break100, mu_step100, coh_topo, cross_contour

    l_vent_amp = np.where(
        valid,
        np.float32(1.0)
        + np.float32(0.22)
        * percentile_rank(paleo_plume + np.float32(0.8) * probe_plume + np.float32(0.6) * active_spring, valid)
        + np.float32(0.10) * percentile_rank(vent_district, valid),
        1.0,
    ).astype(np.float32)
    del paleo_plume, probe_plume, active_spring, vent_district
    gc.collect()

    meta: dict[str, object] = {
        "n_footprint_pixels": n_foot,
        "n_valid_pixels": int(valid.sum()),
        "n_features": n_feat,
        "verified_training_band_tags": EXPECTED_TRAINING_BAND_TAGS,
        "vent_stats": {
            "paleo_geothermal": paleo_stats,
            "temperature_probe_2m": probe_stats,
            "active_thermal_springs": spring_stats,
        },
    }
    return RiedelVentStack(
        X_foot=X,
        footprint=foot,
        valid=valid,
        L_scarp10m=l_scarp10m,
        L_riedel=l_riedel,
        L_knick=l_knick,
        L_subsurf=l_subsurf,
        L_topo100=l_topo100,
        L_vent_amp=l_vent_amp,
        feature_names=RIEDELVENT_FEATURE_NAMES,
        meta=meta,
    )


def fit_predict_riedelvent_loqo(
    stack: RiedelVentStack,
    quad: np.ndarray,
    label_mask: np.ndarray,
    *,
    ablation_collinear_novent: bool = False,
    excluded_mask: np.ndarray | None = None,
    guard_px: int = 12,
    neg_buffer_px: float = 5.0,
    neg_pos_ratio: int = 4,
    seed: int = 20261025,
    max_iter: int = 185,
    calib_weight: float = 0.80,
    power_gamma: float = 3.2,
) -> dict[str, np.ndarray]:
    """Fit multi-branch LOQO HistGBDT ensemble strictly out-of-quadrant."""
    valid_b = np.asarray(stack.valid, dtype=bool) & np.asarray(stack.footprint, dtype=bool)
    specs = COLLINEAR_NOVENT_BRANCH_SPECS if ablation_collinear_novent else RIEDELVENT_BRANCH_SPECS
    w_total = sum(w for _, _, w in specs)
    raw_proba = np.zeros(stack.footprint.shape, dtype=np.float32)
    branch_maps: dict[str, np.ndarray] = {}

    for idx, (b_name, cols, w) in enumerate(specs):
        p_b = fit_single_loqo(
            stack.X_foot,
            stack.footprint,
            valid_b,
            quad,
            label_mask,
            feature_cols=cols,
            excluded_mask=excluded_mask,
            guard_px=guard_px,
            neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio,
            seed=int(seed) + 19 * idx,
            max_iter=max_iter,
        )
        branch_maps[b_name] = p_b
        raw_proba += np.float32(w / w_total) * p_b

    cal_proba = calibrate_quadrant_probabilities(
        raw_proba, valid_b, quad, calib_weight=calib_weight, power_gamma=power_gamma
    )
    return {
        "raw_proba": raw_proba,
        "cal_proba": cal_proba,
        "branches": branch_maps,
    }


__all__ = [
    "EXPECTED_GRID_H",
    "EXPECTED_GRID_W",
    "EXPECTED_TRAINING_BAND_TAGS",
    "RIEDELVENT_FEATURE_NAMES",
    "GROUP_A_INDICES",
    "GROUP_B_RIEDEL_INDICES",
    "GROUP_C_VENT_INDICES",
    "GROUP_D_SUBSURF_INDICES",
    "COLLINEAR_NOVENT_INDICES",
    "RIEDELVENT_BRANCH_SPECS",
    "COLLINEAR_NOVENT_BRANCH_SPECS",
    "RiedelVentStack",
    "assert_training_band_tags",
    "gravity_gradient_tensor_invariants",
    "riedel_obliquity_couplings",
    "build_riedelvent_crest_surface",
    "emit_binary_crest_dots",
    "build_additive_mobius_tail_allocation",
    "build_riedelvent_stack",
    "fit_predict_riedelvent_loqo",
]
