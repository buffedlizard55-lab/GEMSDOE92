"""LIDAR-SINTERVALVE lane (H-92G1): 1 m USGS 3DEP LiDAR Wallace Crest-Toe Dipole,
Antislope Graben Scarp & Channel-Bank Veto Coupled to Tufa-Filtered Sinter / 2m-Probe
Hydrothermal Conduits.

Pre-registered in docs/HYPOTHESES_20261029_LIDAR_SINTERVALVE.md (Rank #1).

Strict invariants:
  1. Zero fault-catalogue inputs ever enter compute_lidar_sintervalve_features().
     Columns named ``dist_known_fault_px`` in GDR CSVs are explicitly rejected/ignored.
  2. All 19 GDAL band descriptions of training_features.tif are asserted before reading.
  3. On the 24.66% of footprint pixels where USGS 3DEP 1 m LiDAR tile coverage is absent
     (``valid < 0.5``), every 1 m LiDAR physical index is quantile-mapped inside ``valid >= 0.5``
     to Uniform(0, 1) and seamlessly imputed on ``valid < 0.5`` via a 4-quadrant spatial
     out-of-fold Ridge bridge fitted strictly to the 100%-coverage USGS 3DEP 10 m sub-pixel
     topographic stack (``topo_10m_derived_100m_u8.tif``), eliminating survey-boundary seams.
"""
from __future__ import annotations

import csv
import gc
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter

from .breakline import percentile_rank
from .hydroconduit import _clean_valid
from .knick_loqo import (
    DEBIASED_INDICES,
    SUB_KNICK_INDICES,
    calibrate_quadrant_probabilities,
    fit_single_loqo,
)
from .netexpand import CONTEXT_COLS, LISTRIC_COLS, NEW_COLS as NX_NEW_COLS
from .ventscarp import (
    _decode_u8_band,
    _rasterize_2m_temperature_probes,
    _rasterize_paleo_vents,
    anisotropic_strike_plume,
)

__all__ = [
    "LIDAR_SINTERVALVE_NAMES",
    "EXPECTED_TRAINING_BAND_TAGS",
    "assert_training_band_tags",
    "dequantize_lidar_band",
    "quantile_bridge_1m_to_10m",
    "compute_lidar_sintervalve_features",
    "build_lidar_sintervalve_crest",
    "branch_columns_53",
    "fit_predict_lidar_sintervalve_loqo",
]

LIDAR_SINTERVALVE_NAMES: tuple[str, ...] = (
    "lidar_wallace_dipole",
    "lidar_bank_vetoed_scarp",
    "lidar_antislope_graben",
    "lidar_ex2m_coherence",
    "lidar_subsurf_strike_lock",
    "sinter_probe_volc_valve",
    "fournier_peclet_upflow",
    "lidar_sinter_concordance",
)

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

LIDAR_QUANT_SPEC: dict[str, tuple[float, str]] = {
    "ex_max": (1.5, "sqrt"),
    "ex_mean": (0.3, "sqrt"),
    "step_max": (1.0, "sqrt"),
    "lapneg_max": (0.05, "sqrt"),
    "lappos_max": (0.05, "sqrt"),
    "downface_max": (1.0, "sqrt"),
    "upface_max": (1.0, "sqrt"),
    "cross_max": (1.0, "sqrt"),
    "relief": (300.0, "sqrt"),
    "coh100": (1.0, "linear"),
    "strike": (180.0, "linear"),
    "valid": (1.0, "linear"),
}

# 53-column layout: 45 NETEXPAND columns + 8 H-92G1 LIDAR-SINTERVALVE columns
LSV_COLS: tuple[int, ...] = tuple(range(45, 53))
N_COLS_53: int = 53


def assert_training_band_tags(ds: rasterio.DatasetReader) -> None:
    """Verify GDAL band tags on training_features.tif match canonical physical channels."""
    if ds.count != 19:
        raise ValueError(f"Expected 19 bands in training_features.tif, got {ds.count}")
    for b_idx, exp_name in EXPECTED_TRAINING_BAND_TAGS.items():
        tags = ds.tags(b_idx)
        desc = (tags.get("name") or ds.descriptions[b_idx - 1] or tags.get("DESCRIPTION") or "").strip()
        short_desc = desc.split(" - ", 1)[0].strip()
        if short_desc and short_desc != exp_name:
            raise ValueError(f"Band {b_idx} tag mismatch: got {desc!r}, expected {exp_name!r}")


def dequantize_lidar_band(q: np.ndarray, xmax: float, mode: str) -> np.ndarray:
    """Invert ``q = 1 + round(254 * t(clip(x / xmax, 0, 1)))``; ``q == 0`` -> 0.0."""
    q_arr = np.asarray(q, dtype=np.uint8)
    out = np.zeros(q_arr.shape, dtype=np.float32)
    nz = q_arr > 0
    u = np.clip((q_arr[nz].astype(np.float32) - 1.0) / np.float32(254.0), 0.0, 1.0)
    if mode == "sqrt":
        out[nz] = np.float32(xmax) * (u * u)
    elif mode == "linear":
        out[nz] = np.float32(xmax) * u
    else:
        raise ValueError(f"Unknown lidar quantisation mode {mode!r}")
    return out


def quantile_bridge_1m_to_10m(
    raw_1m: np.ndarray,
    has_lidar: np.ndarray,
    X_10m_valid: np.ndarray,
    valid: np.ndarray,
    quad_valid: np.ndarray,
    *,
    ridge_alpha: float = 250.0,
) -> np.ndarray:
    """Map ``raw_1m`` on ``has_lidar & valid`` to Uniform(0, 1) quantiles and seamlessly
    impute ``~has_lidar & valid`` via spatial 4-quadrant out-of-fold Ridge on 10 m 3DEP,
    rank-matching imputed quantiles to Uniform(0, 1) so no tile-coverage seam exists."""
    val = np.asarray(valid, dtype=bool)
    lid_mask_val = np.asarray(has_lidar, dtype=bool)[val]
    raw_val = np.nan_to_num(raw_1m[val].astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)

    u_val = np.full(raw_val.shape, 0.5, dtype=np.float32)
    if np.any(lid_mask_val):
        lid_vals = raw_val[lid_mask_val]
        order = np.argsort(lid_vals, kind="mergesort")
        ranks = np.empty(lid_vals.size, dtype=np.float32)
        ranks[order] = (np.arange(lid_vals.size, dtype=np.float32) + 0.5) / float(lid_vals.size)
        u_val[lid_mask_val] = ranks

    miss_mask_val = ~lid_mask_val
    if np.any(miss_mask_val) and np.any(lid_mask_val):
        # Spatial out-of-fold linear/quadratic Ridge from standardized 10m 3DEP predictors
        p = X_10m_valid.shape[1]
        X_aug = np.empty((X_10m_valid.shape[0], p + 1), dtype=np.float32)
        X_aug[:, 0] = 1.0
        X_aug[:, 1:] = X_10m_valid

        pred_miss = np.empty(int(miss_mask_val.sum()), dtype=np.float32)
        miss_indices = np.flatnonzero(miss_mask_val)
        q_miss = quad_valid[miss_indices]

        # Fit Ridge per quadrant leaving target quadrant out to prevent spatial overfitting
        eye = np.eye(p + 1, dtype=np.float64)
        eye[0, 0] = 0.0
        for q_id in np.unique(q_miss):
            tr = lid_mask_val & (quad_valid != q_id)
            if int(tr.sum()) < 1000:
                tr = lid_mask_val
            Xt = X_aug[tr]
            yt = u_val[tr].astype(np.float64)
            # Subsample training rows deterministically to <=250k for fast O(N p^2) solve
            if Xt.shape[0] > 250_000:
                step = max(1, Xt.shape[0] // 250_000)
                Xt = Xt[::step]
                yt = yt[::step]
            A = Xt.T.astype(np.float64) @ Xt.astype(np.float64) + float(ridge_alpha) * eye
            b = Xt.T.astype(np.float64) @ yt
            w = np.linalg.solve(A, b).astype(np.float32)
            sel = q_miss == q_id
            pred_miss[sel] = X_aug[miss_indices[sel]] @ w

        # Quantile-match predicted missing cells to Uniform(0, 1) so marginal distribution
        # on non-LiDAR cells equals LiDAR cells identically (zero survey-mask shift!)
        m_order = np.argsort(pred_miss, kind="mergesort")
        m_ranks = np.empty(pred_miss.size, dtype=np.float32)
        m_ranks[m_order] = (np.arange(pred_miss.size, dtype=np.float32) + 0.5) / float(pred_miss.size)
        u_val[miss_mask_val] = m_ranks

    out = np.zeros(val.shape, dtype=np.float32)
    out[val] = u_val
    return out


def _rasterize_volcanic_vents(csv_path: Path, shape: tuple[int, int], valid: np.ndarray) -> np.ndarray:
    """Rasterize Quaternary volcanic vents (DOE GDR #1391) strictly from (row, col, rock_type).
    Explicitly ignores dist_known_fault_px."""
    H, W = shape
    imp = np.zeros(shape, dtype=np.float32)
    with csv_path.open("r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                r = int(float(row["row"]))
                c = int(float(row["col"]))
            except (KeyError, TypeError, ValueError):
                continue
            if 0 <= r < H and 0 <= c < W and valid[r, c]:
                rtype = (row.get("rock_type") or "").lower()
                w = 1.35 if ("rhyol" in rtype or "dacit" in rtype or "silic" in rtype) else 1.00
                imp[r, c] += np.float32(w)
    return imp


def _rasterize_fournier_disequilibrium(csv_path: Path, shape: tuple[int, int], valid: np.ndarray) -> np.ndarray:
    """Rasterize positive Fournier silica geothermometer enthalpy disequilibrium
    ``max(0, max(T_quartz, T_chalcedony) - T_measured)`` from DOE GDR #1391 wells/springs.
    Explicitly ignores dist_known_fault_px."""
    H, W = shape
    imp = np.zeros(shape, dtype=np.float32)
    with csv_path.open("r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                r = int(float(row["row"]))
                c = int(float(row["col"]))
            except (KeyError, TypeError, ValueError):
                continue
            if not (0 <= r < H and 0 <= c < W and valid[r, c]):
                continue
            vals_gt = []
            for k in ("geothermquartz_c", "geothermchalc_c"):
                try:
                    v = float(row.get(k, "nan"))
                    if np.isfinite(v) and 20.0 <= v <= 350.0:
                        vals_gt.append(v)
                except (TypeError, ValueError):
                    pass
            try:
                t_meas = float(row.get("temp_c", "nan"))
            except (TypeError, ValueError):
                t_meas = np.nan
            if vals_gt:
                t_deep = max(vals_gt)
                t_ref = t_meas if (np.isfinite(t_meas) and t_meas > 5.0) else 18.0
                dt = max(0.0, t_deep - t_ref)
                if dt > 15.0:
                    imp[r, c] = max(imp[r, c], np.float32(np.log1p(dt - 15.0)))
    return imp


def compute_lidar_sintervalve_features(
    *,
    lidar_tif: Path,
    topo10m_tif: Path,
    paleo_zip: Path,
    probe2m_zip: Path,
    volc_csv: Path,
    wellspring_csv: Path,
    det_elev: np.ndarray,
    grav_anom: np.ndarray,
    depth_to_base: np.ndarray,
    cond_surf: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Compute the 8 zero-catalogue H-92G1 features and ``lidar_valid_raw`` canary array."""
    foot = np.asarray(footprint, dtype=bool)
    val = np.asarray(valid, dtype=bool) & foot
    quad_val = np.asarray(quad, dtype=np.int32)[val]

    # 1. Load 100%-coverage 10 m 3DEP predictors on valid cells for seamless quantile bridging
    with rasterio.open(topo10m_tif) as ds10:
        transform = ds10.transform
        b10_list = []
        for b_idx in range(1, ds10.count + 1):
            arr10 = _decode_u8_band(ds10, b_idx)[val]
            med = float(np.median(arr10))
            iqr = max(float(np.quantile(arr10, 0.75) - np.quantile(arr10, 0.25)), 1e-5)
            b10_list.append(np.clip((arr10 - med) / iqr, -4.0, 6.0).astype(np.float32))
        dem10_mean = _decode_u8_band(ds10, 9)
        curv10_val = b10_list[5]
        coh10_val = b10_list[6]
    X_10m_valid = np.column_stack(b10_list).astype(np.float32)
    del b10_list
    gc.collect()

    # 2. Load & de-quantize 12-band USGS 3DEP 1 m LiDAR raster
    with rasterio.open(lidar_tif) as dsl:
        if dsl.count != 12:
            raise ValueError(f"Expected 12 bands in {lidar_tif}, got {dsl.count}")
        ex_max = dequantize_lidar_band(dsl.read(1), *LIDAR_QUANT_SPEC["ex_max"])
        step_max = dequantize_lidar_band(dsl.read(3), *LIDAR_QUANT_SPEC["step_max"])
        lapneg = dequantize_lidar_band(dsl.read(4), *LIDAR_QUANT_SPEC["lapneg_max"])
        lappos = dequantize_lidar_band(dsl.read(5), *LIDAR_QUANT_SPEC["lappos_max"])
        downface = dequantize_lidar_band(dsl.read(6), *LIDAR_QUANT_SPEC["downface_max"])
        upface = dequantize_lidar_band(dsl.read(7), *LIDAR_QUANT_SPEC["upface_max"])
        cross = dequantize_lidar_band(dsl.read(8), *LIDAR_QUANT_SPEC["cross_max"])
        relief1m = dequantize_lidar_band(dsl.read(9), *LIDAR_QUANT_SPEC["relief"])
        coh100 = dequantize_lidar_band(dsl.read(10), *LIDAR_QUANT_SPEC["coh100"])
        strike1m = dequantize_lidar_band(dsl.read(11), *LIDAR_QUANT_SPEC["strike"])
        valid1m = dequantize_lidar_band(dsl.read(12), *LIDAR_QUANT_SPEC["valid"])

    has_lidar = (valid1m >= np.float32(0.5)) & val
    lidar_valid_raw = valid1m.copy()
    del valid1m

    # Subsurface gradient strike from scalar B13 gravity + B15 basement depth (self-consistent units)
    g_s = gaussian_filter(_clean_valid(grav_anom, val), 2.0).astype(np.float32)
    gy, gx = np.gradient(g_s.astype(np.float64))
    g_mag = np.hypot(gy, gx).astype(np.float32)
    db_s = gaussian_filter(_clean_valid(depth_to_base, val), 2.0).astype(np.float32)
    by, bx = np.gradient(db_s.astype(np.float64))
    b_mag = np.hypot(by, bx).astype(np.float32)
    del g_s, db_s

    # Strike azimuth (degrees clockwise from North, 0..180): tangent is perpendicular to gradient!
    # Grid: +col = East (+x), +row = South (-y) -> grad = (gx, -gy) in (East, North),
    # so strike tangent in (East, North) is (gy, gx), azimuth clockwise from North = atan2(gy, gx) mod pi.
    theta_sub_rad = np.mod(np.arctan2(gy + 0.5 * by, gx + 0.5 * bx), np.pi).astype(np.float32)
    del gy, gx, by, bx

    # Lahontan ~1,330 m highstand shoreline bench suppressor where subsurface gradient is weak
    g_rank = percentile_rank(g_mag + np.float32(0.5) * b_mag, val)
    elev_use = np.where(dem10_mean > 100.0, dem10_mean, _clean_valid(det_elev, val))
    s_lahontan = (
        np.exp(-0.5 * ((elev_use - np.float32(1330.0)) / np.float32(45.0)) ** 2)
        * np.clip(1.0 - g_rank, 0.0, 1.0)
    ).astype(np.float32)
    del dem10_mean, elev_use, g_mag, b_mag, g_rank

    inv_sqrt_rel = np.float32(1.0) / np.sqrt(relief1m + np.float32(5.0))
    contour_step = np.maximum(downface, upface)
    v_bank = np.maximum(
        0.0,
        (contour_step - cross) / (contour_step + cross + np.float32(1e-4)),
    ).astype(np.float32)

    # Raw 1m physical channels (evaluated on has_lidar, quantile-bridged on ~has_lidar)
    raw_wallace = (np.sqrt(np.maximum(lapneg * lappos, 0.0)) * coh100 * inv_sqrt_rel).astype(np.float32)
    raw_bank_veto = (step_max * v_bank * coh100 * inv_sqrt_rel).astype(np.float32)
    raw_antislope = (upface * coh100 * (np.float32(1.0) - np.float32(0.75) * s_lahontan) * inv_sqrt_rel).astype(np.float32)
    raw_ex2m = (ex_max * coh100).astype(np.float32)
    raw_strikelock = (
        np.abs(np.cos(np.deg2rad(strike1m) - theta_sub_rad)) * coh100
    ).astype(np.float32)

    del ex_max, step_max, lapneg, lappos, downface, upface, cross, relief1m, coh100, strike1m
    del contour_step, v_bank, inv_sqrt_rel, s_lahontan, theta_sub_rad, curv10_val, coh10_val
    gc.collect()

    f_wallace = quantile_bridge_1m_to_10m(raw_wallace, has_lidar, X_10m_valid, val, quad_val)
    f_bank_veto = quantile_bridge_1m_to_10m(raw_bank_veto, has_lidar, X_10m_valid, val, quad_val)
    f_antislope = quantile_bridge_1m_to_10m(raw_antislope, has_lidar, X_10m_valid, val, quad_val)
    f_ex2m = quantile_bridge_1m_to_10m(raw_ex2m, has_lidar, X_10m_valid, val, quad_val)
    f_strikelock = quantile_bridge_1m_to_10m(raw_strikelock, has_lidar, X_10m_valid, val, quad_val)
    del raw_wallace, raw_bank_veto, raw_antislope, raw_ex2m, raw_strikelock, X_10m_valid, has_lidar
    gc.collect()

    # 3. Hydrothermal sinter / 2m-probe / volcanic vent & Fournier enthalpy disequilibrium channels
    paleo_imp, _ = _rasterize_paleo_vents(paleo_zip, transform, foot.shape, val)
    probe_imp, _ = _rasterize_2m_temperature_probes(probe2m_zip, transform, foot.shape, val, dab_threshold_c=1.0)
    volc_imp = _rasterize_volcanic_vents(volc_csv, foot.shape, val)

    combined_vent_imp = (paleo_imp + np.float32(0.85) * probe_imp + np.float32(0.65) * volc_imp).astype(np.float32)
    del paleo_imp, probe_imp, volc_imp
    vent_plume_near = anisotropic_strike_plume(
        combined_vent_imp, val, strike_deg_east_of_north=18.0, sigma_parallel_px=18.0, sigma_perp_px=6.5
    )
    vent_plume_reg = anisotropic_strike_plume(
        combined_vent_imp, val, strike_deg_east_of_north=18.0, sigma_parallel_px=42.0, sigma_perp_px=15.0
    )
    del combined_vent_imp
    f_sinter_valve = percentile_rank(
        (np.float32(0.65) * vent_plume_near + np.float32(0.35) * vent_plume_reg).astype(np.float32), val
    )
    del vent_plume_near, vent_plume_reg

    fournier_imp = _rasterize_fournier_disequilibrium(wellspring_csv, foot.shape, val)
    fournier_plume = anisotropic_strike_plume(
        fournier_imp, val, strike_deg_east_of_north=18.0, sigma_parallel_px=26.0, sigma_perp_px=9.0
    )
    del fournier_imp
    cond_rank = percentile_rank(np.log(np.maximum(_clean_valid(cond_surf, val), np.float32(0.1))), val)
    f_fournier = percentile_rank((fournier_plume * (np.float32(0.40) + np.float32(0.60) * cond_rank)).astype(np.float32), val)
    del fournier_plume, cond_rank

    hydro_max = np.maximum(f_sinter_valve, f_fournier)
    scarp_core = np.float32(0.55) * f_wallace + np.float32(0.45) * f_antislope
    f_concord = percentile_rank(np.sqrt(np.maximum(scarp_core * hydro_max, 0.0)).astype(np.float32), val)
    del hydro_max, scarp_core

    feats = {
        "lidar_wallace_dipole": f_wallace,
        "lidar_bank_vetoed_scarp": f_bank_veto,
        "lidar_antislope_graben": f_antislope,
        "lidar_ex2m_coherence": f_ex2m,
        "lidar_subsurf_strike_lock": f_strikelock,
        "sinter_probe_volc_valve": f_sinter_valve,
        "fournier_peclet_upflow": f_fournier,
        "lidar_sinter_concordance": f_concord,
    }
    for k in feats:
        arr = np.where(val, np.nan_to_num(feats[k], nan=0.0, posinf=0.0, neginf=0.0), 0.0).astype(np.float32)
        arr[:8, :] = 0.0
        arr[-8:, :] = 0.0
        arr[:, :8] = 0.0
        arr[:, -8:] = 0.0
        feats[k] = arr
    return feats, lidar_valid_raw


def build_lidar_sintervalve_crest(
    lsv_feats: dict[str, np.ndarray],
    l_netexpand: np.ndarray,
    valid: np.ndarray,
) -> np.ndarray:
    """Fuse geophysical/listric crest ``l_netexpand`` with channel-vetoed 1 m LiDAR Wallace
    crest-toe dipole & antislope graben scarp crest."""
    val = np.asarray(valid, dtype=bool)
    lidar_scarp = np.sqrt(
        np.maximum(
            lsv_feats["lidar_wallace_dipole"] * lsv_feats["lidar_bank_vetoed_scarp"],
            0.0,
        )
    )
    lidar_anti = np.sqrt(
        np.maximum(
            lsv_feats["lidar_antislope_graben"] * lsv_feats["lidar_subsurf_strike_lock"],
            0.0,
        )
    )
    lidar_loc = (np.maximum(lidar_scarp, lidar_anti) ** np.float32(1.35)).astype(np.float32)
    out = np.maximum(np.asarray(l_netexpand, dtype=np.float32), np.float32(0.92) * lidar_loc)
    return np.where(val, np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0), 0.0).astype(np.float32)


def branch_columns_53(*, with_context: bool) -> dict[str, tuple[int, ...]]:
    extra = set(LISTRIC_COLS) | set(NX_NEW_COLS) | set(LSV_COLS) | (set(CONTEXT_COLS) if with_context else set())
    full = tuple(range(N_COLS_53)) if with_context else tuple(
        c for c in range(N_COLS_53) if c not in CONTEXT_COLS
    )
    # Subsurface + hydrothermal + strike-locked antislope branch (excludes raw slope bias)
    sub_lsv = set(LISTRIC_COLS) | set(NX_NEW_COLS) | {46, 47, 49, 50, 51, 52} | (set(CONTEXT_COLS) if with_context else set())
    return {
        "full": full,
        "debiased": tuple(sorted(set(DEBIASED_INDICES) | extra)),
        "sub": tuple(sorted(set(SUB_KNICK_INDICES) | sub_lsv)),
    }


def fit_predict_lidar_sintervalve_loqo(
    X_foot: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    label_mask: np.ndarray,
    *,
    with_context: bool = True,
    excluded_mask: np.ndarray | None = None,
    guard_px: int = 12,
    neg_buffer_px: float = 5.0,
    neg_pos_ratio: int = 4,
    seed: int = 20261029,
    max_iter: int = 185,
    calibrate_quadrants: bool = True,
    calib_weight: float = 0.80,
    power_gamma: float = 3.3,
) -> dict[str, np.ndarray]:
    """3-branch spatial LOQO (15% full / 40% debiased / 45% sub) on the 53-col H-92G1 stack."""
    valid_b = np.asarray(valid, dtype=bool) & np.asarray(footprint, dtype=bool)
    cols = branch_columns_53(with_context=with_context)
    kw = dict(
        excluded_mask=excluded_mask,
        guard_px=guard_px,
        neg_buffer_px=neg_buffer_px,
        neg_pos_ratio=neg_pos_ratio,
        max_iter=max_iter,
    )
    p_full = fit_single_loqo(
        X_foot, footprint, valid_b, quad, label_mask,
        feature_cols=cols["full"], seed=int(seed), **kw
    )
    p_deb = fit_single_loqo(
        X_foot, footprint, valid_b, quad, label_mask,
        feature_cols=cols["debiased"], seed=int(seed) + 1, **kw
    )
    p_sub = fit_single_loqo(
        X_foot, footprint, valid_b, quad, label_mask,
        feature_cols=cols["sub"], seed=int(seed) + 2, **kw
    )
    raw = (
        np.float32(0.15) * p_full
        + np.float32(0.40) * p_deb
        + np.float32(0.45) * p_sub
    ).astype(np.float32)
    cal = (
        calibrate_quadrant_probabilities(
            raw, valid_b, quad, calib_weight=calib_weight, power_gamma=power_gamma
        )
        if calibrate_quadrants
        else raw.copy()
    )
    return {
        "p_full": p_full,
        "p_debiased": p_deb,
        "p_sub": p_sub,
        "raw_proba": raw,
        "cal_proba": cal,
    }
