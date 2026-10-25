"""VENTSCARP lane: Seamless USGS 3DEP 10 m Sub-Pixel Piedmont Scarp Localization
x Tufa-Filtered INGENIOUS Paleo/Blind Hydrothermal Vent Valve Out-of-Quadrant
(LOQO) Fault Discovery.

Pre-registered hypothesis & equations: docs/HYPOTHESES_20261025_VENTSCARP.md.

Key physical innovations:
1. Seamless USGS 3DEP 1/3-arc-second (~10 m) sub-pixel scarp excess
   ``log(1 + slope_max_10m) - log(1 + slope_100m)``, within-cell slope dispersion,
   piedmont-weighted 10 m Wallace profile curvature, aspect/hillshade strike
   coherence, and 10 m stream-profile chi/k_sn knickpoint steps across 100.00%
   of the 5,167,373-pixel competition footprint.
2. Tufa-filtered DOE GDR #1391 INGENIOUS paleo-geothermal hydrothermal vents
   (siliceous sinter, silica-cemented sand Qss, hydrothermal explosion craters,
   silicified fault breccia, travertine, sulfur/alteration — explicitly excluding
   Pleistocene Lake Lahontan lacustrine tufa mimics), shallow 2-meter temperature
   probe conductive anomalies (2mDAB), and active thermal wells/springs projected
   along anisotropic Great Basin N18E normal-fault strike kernels.
3. Airborne GeoDAWN hydrothermal K/Th & U/Th alteration enrichment, Grauch (2001)
   150 m upward-continuation shallow magnetite-destruction residual
   ``z(TMI_up150) - z(RTP)``, province-debiased mesoscale gravity/basement/strain,
   and explicit 1,330 m Lake Lahontan shoreline bench deconfounding.

Strict zero-leakage invariant: zero fault-catalogue arrays ever enter any
feature or surface builder in this module.
"""
from __future__ import annotations

import gc
import struct
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import transform as rio_transform
from scipy.ndimage import binary_dilation, distance_transform_edt, gaussian_filter, zoom
from scipy.signal import fftconvolve
from sklearn.ensemble import HistGradientBoostingClassifier

from .breakline import percentile_rank, spaced_top_mask
from .coulomb_loqo import _grad_xy, _sat, directional_ridge_1d
from .hydroconduit import _clean_valid
from .knick_loqo import calibrate_quadrant_probabilities, fit_single_loqo, mesoscale_zscore

__all__ = [
    "FEATURE_NAMES",
    "GROUP_A_INDICES",
    "GROUP_B_VENT_INDICES",
    "GROUP_C_SUBSURF_INDICES",
    "NOVENT_INDICES",
    "DEBIASED_VENT_INDICES",
    "is_hydrothermal_paleo_vent",
    "anisotropic_strike_plume",
    "subpixel_scarp_excess",
    "compute_ventscarp_stack",
    "fit_predict_ventscarp_loqo",
    "build_ventscarp_crest_surface",
    "build_soft_tversky_allocation",
    "spaced_top_mask",
]

FEATURE_NAMES: tuple[str, ...] = (
    # Group A: Seamless USGS 3DEP 10 m Sub-Pixel Scarp & Chi Knickpoints (0..7)
    "scarp10m_excess_max",
    "scarp10m_excess_p90",
    "scarp10m_slope_std_norm",
    "scarp10m_curv_prof_piedmont",
    "scarp10m_linear_coherence",
    "scarp10m_steep_step_grad",
    "chi10m_knick_step",
    "chi10m_ksn_drainage",
    # Group B: Tufa-Filtered Paleo/Blind Hydrothermal Vent & Alteration Valve (8..16)
    "paleo_vent_aniso_plume",
    "probe_2mdab_aniso_plume",
    "active_thermal_spring_aniso",
    "unified_vent_district_halo",
    "rad_k_over_th_z",
    "rad_u_over_th_z",
    "grauch_mag_demag_residual",
    "mt_claycap_perimeter_grad",
    "heatflow_scarp_coupling",
    # Group C: Province-Debiased Subsurface Potential, Cover & Shoreline Null (17..25)
    "iso_grav_slope_meso_z",
    "grav_tilt_grad",
    "basement_depth_log",
    "basement_step_grad",
    "dip_concord_scarp_grav",
    "strain_2ndinv_meso_z",
    "strain_dilatation_meso_z",
    "cross_contour_scarp_transgression",
    "lahontan_shoreline_mimic_index",
)

GROUP_A_INDICES: tuple[int, ...] = tuple(range(0, 8))
GROUP_B_VENT_INDICES: tuple[int, ...] = tuple(range(8, 17))
GROUP_C_SUBSURF_INDICES: tuple[int, ...] = tuple(range(17, 26))

# Arm 2 (scarp10m_novent): ablates all 9 Group B geothermal-vent / hydrothermal features
NOVENT_INDICES: tuple[int, ...] = GROUP_A_INDICES + GROUP_C_SUBSURF_INDICES

# Subsurface + Vent + Sub-pixel Excess branch (drops raw basement depth level col 19)
DEBIASED_VENT_INDICES: tuple[int, ...] = tuple(i for i in range(len(FEATURE_NAMES)) if i != 19)

# Subsurface + Hydrothermal Valve branch (forces model to learn deeper geophysical + vent coupling)
VENT_SUBSURF_INDICES: tuple[int, ...] = (0, 3, 4, 6, 7) + GROUP_B_VENT_INDICES + GROUP_C_SUBSURF_INDICES


def is_hydrothermal_paleo_vent(deposit_type: str | float | None) -> tuple[bool, float]:
    """Classify DOE GDR #1391 Paleo_geothermal_final Deposit_type and return (keep, weight).

    Explicitly excludes Pleistocene pluvial Lake Lahontan shoreline calcium-carbonate
    ``Tufa`` deposits (86 in-footprint shoreline mimics) while retaining true
    hydrothermal fault-valve precipitates weighted by reservoir temperature proxy:
      - Sinter (amorphous silica, T_res >= 175 C), Explosion craters, Silicified fault breccia: 1.5
      - Silica-cemented sand/mud/ash (Qss), Silica/Calcite-qtz veins, Alteration/Sulfur: 1.25
      - Non-tufa Travertine / carbonate-cemented fan gravel: 1.0
    """
    if deposit_type is None or (isinstance(deposit_type, float) and np.isnan(deposit_type)):
        return False, 0.0
    s = str(deposit_type).strip().lower()
    if not s:
        return False, 0.0
    # Exclude pure pluvial shoreline tufa mimics ("tufa", but allow "tufa and travertine" at lower weight)
    if "tufa" in s and "travertine" not in s:
        return False, 0.0
    if any(k in s for k in ("sinter", "explosion", "fault breccia")):
        return True, 1.50
    if any(k in s for k in ("silica", "alteration", "argillic", "sulfur", "sulfate", "vein")):
        return True, 1.25
    if "travertine" in s:
        return True, 0.85 if "tufa" in s else 1.00
    return False, 0.0


def anisotropic_strike_plume(
    impulse_grid: np.ndarray,
    valid: np.ndarray,
    *,
    strike_deg_east_of_north: float = 18.0,
    sigma_parallel_px: float = 24.0,
    sigma_perp_px: float = 8.0,
) -> np.ndarray:
    """Convolve point/grid hydrothermal sources with a N18E strike-aligned Gaussian kernel.

    Grid convention: col increases East (+x), row increases South (-y).
    Along-strike unit vector for azimuth ``alpha`` (degrees clockwise from North):
      d_parallel = dx * sin(alpha) + dy * cos(alpha)
      d_perp     = dx * cos(alpha) - dy * sin(alpha)
    where dx = dc and dy = -dr.
    """
    if sigma_parallel_px <= 0.0 or sigma_perp_px <= 0.0:
        raise ValueError("sigmas must be positive")
    imp = np.where(np.isfinite(impulse_grid), np.maximum(impulse_grid, 0.0), 0.0).astype(np.float32)
    if not np.any(imp > 0.0):
        return np.zeros_like(imp, dtype=np.float32)

    H, W = imp.shape
    use_decim = H >= 1000 and W >= 1000 and min(sigma_parallel_px, sigma_perp_px) >= 6.0
    if use_decim:
        h2 = (H + 1) // 2
        w2 = (W + 1) // 2
        pad_h = h2 * 2 - H
        pad_w = w2 * 2 - W
        imp_pad = np.pad(imp, ((0, pad_h), (0, pad_w)), mode="constant") if (pad_h or pad_w) else imp
        imp_work = imp_pad.reshape(h2, 2, w2, 2).sum(axis=(1, 3)).astype(np.float32)
        sp = float(sigma_parallel_px) * 0.5
        sq = float(sigma_perp_px) * 0.5
    else:
        imp_work = imp
        sp = float(sigma_parallel_px)
        sq = float(sigma_perp_px)

    half = int(np.ceil(3.2 * max(sp, sq)))
    coords = np.arange(-half, half + 1, dtype=np.float32)
    dr, dc = np.meshgrid(coords, coords, indexing="ij")
    dx = dc
    dy = -dr
    alpha = np.deg2rad(float(strike_deg_east_of_north))
    sin_a = np.float32(np.sin(alpha))
    cos_a = np.float32(np.cos(alpha))
    d_par = dx * sin_a + dy * cos_a
    d_perp = dx * cos_a - dy * sin_a
    kern = np.exp(-0.5 * ((d_par / np.float32(sp)) ** 2 + (d_perp / np.float32(sq)) ** 2)).astype(
        np.float32
    )
    kern /= np.float32(max(float(kern.max()), 1e-8))

    plume_work = fftconvolve(imp_work, kern, mode="same").astype(np.float32)
    if use_decim:
        plume_up = zoom(plume_work, 2.0, order=1, prefilter=False).astype(np.float32)
        plume = plume_up[:H, :W]
    else:
        plume = plume_work
    plume = np.maximum(plume, 0.0)
    plume[~np.asarray(valid, dtype=bool)] = 0.0
    return plume


def subpixel_scarp_excess(
    slope_10m_deg: np.ndarray,
    slope_100m_deg: np.ndarray,
    valid: np.ndarray,
) -> np.ndarray:
    """Compute positive sub-pixel scarp localization ``max(0, log1p(S_10m) - log1p(S_100m))``.

    Cancels broad uniform mountain cliffs (where S_10m ~= S_100m) while isolating
    discrete 10-30 m fault scarps embedded inside low-slope (<6 deg) 100 m piedmont cells.
    """
    s10 = np.maximum(np.nan_to_num(slope_10m_deg, nan=0.0), 0.0).astype(np.float32)
    s100 = np.maximum(np.nan_to_num(slope_100m_deg, nan=0.0), 0.0).astype(np.float32)
    ex = np.maximum(np.log1p(s10) - np.log1p(s100), 0.0).astype(np.float32)
    ex[~np.asarray(valid, dtype=bool)] = 0.0
    return ex


def _decode_u8_band(ds: rasterio.DatasetReader, band_idx: int) -> np.ndarray:
    raw = ds.read(band_idx)
    tags = ds.tags(band_idx)
    q_lo = float(tags.get("q_lo", 0.0))
    q_hi = float(tags.get("q_hi", 1.0))
    out = np.zeros(raw.shape, dtype=np.float32)
    nz = raw > 0
    out[nz] = np.float32(q_lo) + (raw[nz].astype(np.float32) - 1.0) * np.float32((q_hi - q_lo) / 254.0)
    return out


def _rasterize_paleo_vents(
    zip_path: Path,
    transform: rasterio.Affine,
    shape: tuple[int, int],
    valid: np.ndarray,
) -> tuple[np.ndarray, dict[str, int]]:
    H, W = shape
    grid = np.zeros(shape, dtype=np.float32)
    stats = {"total_rows": 0, "in_footprint": 0, "hydrothermal_kept": 0, "tufa_excluded": 0}
    with zipfile.ZipFile(zip_path) as zf:
        df = pd.read_csv(zf.open("Paleo_geothermal_final.csv"), encoding="cp1252")
    stats["total_rows"] = int(len(df))
    xs, ys = rio_transform(
        "EPSG:4269",
        "EPSG:32611",
        df["Long_deg_NAD83"].values,
        df["Lat_deg_NAD83"].values,
    )
    cols = np.floor((np.asarray(xs) - transform.c) / transform.a).astype(np.int32)
    rows = np.floor((np.asarray(ys) - transform.f) / transform.e).astype(np.int32)
    for r, c, dep in zip(rows, cols, df["Deposit_type"].values):
        if 0 <= r < H and 0 <= c < W and valid[r, c]:
            stats["in_footprint"] += 1
            keep, w = is_hydrothermal_paleo_vent(dep)
            if keep:
                stats["hydrothermal_kept"] += 1
                grid[r, c] += np.float32(w)
            elif dep is not None and "tufa" in str(dep).lower():
                stats["tufa_excluded"] += 1
    return grid, stats


def _rasterize_2m_temperature_probes(
    zip_path: Path,
    transform: rasterio.Affine,
    shape: tuple[int, int],
    valid: np.ndarray,
    *,
    dab_threshold_c: float = 1.2,
) -> tuple[np.ndarray, dict[str, int]]:
    H, W = shape
    grid = np.zeros(shape, dtype=np.float32)
    with zipfile.ZipFile(zip_path) as zf:
        dbf = zf.read(
            "2m_temperature_probe_INGENIOUS_regional_data/"
            "2m_temperature_probe_n83geo/2m_temperature_probe_n83geo.dbf"
        )
    num_rec = struct.unpack("<I", dbf[4:8])[0]
    hdr_len, rec_len = struct.unpack("<HH", dbf[8:12])
    fields: list[tuple[str, int]] = []
    pos = 32
    while pos < hdr_len - 1 and dbf[pos] != 0x0D:
        fname = dbf[pos : pos + 11].split(b"\x00", 1)[0].decode("ascii", errors="replace")
        flen = dbf[pos + 16]
        fields.append((fname, flen))
        pos += 32

    lons: list[float] = []
    lats: list[float] = []
    dabs: list[float] = []
    offset = hdr_len
    for _ in range(num_rec):
        rec = dbf[offset : offset + rec_len]
        offset += rec_len
        if rec[0] == 0x2A:
            continue
        p = 1
        lon_v = lat_v = dab_v = np.nan
        for fname, flen in fields:
            if fname in ("F2mDAB", "LatDegreeN", "LongDegree"):
                txt = rec[p : p + flen].decode("cp1252", errors="replace").strip()
                try:
                    val = float(txt)
                except ValueError:
                    val = np.nan
                if fname == "F2mDAB":
                    dab_v = val
                elif fname == "LatDegreeN":
                    lat_v = val
                elif fname == "LongDegree":
                    lon_v = val
            p += flen
        if np.isfinite(lon_v) and np.isfinite(lat_v) and np.isfinite(dab_v):
            lons.append(lon_v)
            lats.append(lat_v)
            dabs.append(dab_v)

    xs, ys = rio_transform("EPSG:4269", "EPSG:32611", lons, lats)
    cols = np.floor((np.asarray(xs) - transform.c) / transform.a).astype(np.int32)
    rows = np.floor((np.asarray(ys) - transform.f) / transform.e).astype(np.int32)
    in_foot = 0
    pos_anom = 0
    for r, c, dab in zip(rows, cols, dabs):
        if 0 <= r < H and 0 <= c < W and valid[r, c]:
            in_foot += 1
            if dab >= dab_threshold_c:
                pos_anom += 1
                w = np.log1p(float(dab) - dab_threshold_c + 0.5)
                if w > grid[r, c]:
                    grid[r, c] = np.float32(w)
    return grid, {
        "total_valid_records": len(dabs),
        "in_footprint": in_foot,
        "anomalous_ge_threshold": pos_anom,
    }


def _rasterize_active_thermal_springs(
    csv_path: Path,
    shape: tuple[int, int],
    valid: np.ndarray,
    *,
    min_temp_c: float = 30.0,
) -> tuple[np.ndarray, dict[str, int]]:
    H, W = shape
    grid = np.zeros(shape, dtype=np.float32)
    df = pd.read_csv(csv_path)
    # Use ONLY row, col, temp_c (never touch any fault distance if ever present)
    rows = pd.to_numeric(df["row"], errors="coerce").values
    cols = pd.to_numeric(df["col"], errors="coerce").values
    temps = pd.to_numeric(df["temp_c"], errors="coerce").values
    kept = 0
    for r_f, c_f, t_c in zip(rows, cols, temps):
        if not (np.isfinite(r_f) and np.isfinite(c_f) and np.isfinite(t_c)):
            continue
        r, c = int(round(r_f)), int(round(c_f))
        if 0 <= r < H and 0 <= c < W and valid[r, c] and t_c >= min_temp_c:
            kept += 1
            w = np.log1p(min(float(t_c), 160.0) - 25.0)
            if w > grid[r, c]:
                grid[r, c] = np.float32(w)
    return grid, {"total_rows": int(len(df)), "thermal_ge_30c_in_footprint": kept}


def compute_ventscarp_stack(
    training_features_tif: Path,
    topo_10m_tif: Path,
    dem10_chi_tif: Path,
    paleo_zip: Path,
    probe_2m_zip: Path,
    wellspring_csv: Path,
    geodawn_ext_tif: Path,
    footprint: np.ndarray,
) -> dict[str, object]:
    """Stream all 26 zero-catalogue features into ``X_foot`` (<1.4 GiB peak RSS)."""
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
    # 100 m slope in degrees (Band 19 is rise/run gradient; clip >=0)
    with rasterio.open(training_features_tif) as ds_ref:
        transform = ds_ref.transform
    # Check Band 19 scale: in GeoDAWN stack Band 19 is slope in degrees or rise/run
    b19_clean = _clean_valid(b19_slope, valid)
    p99_b19 = float(np.percentile(b19_clean[valid], 99.0))
    if p99_b19 <= 2.5:
        slope_100m_deg = np.rad2deg(np.arctan(np.maximum(b19_clean, 0.0))).astype(np.float32)
    else:
        slope_100m_deg = np.maximum(b19_clean, 0.0).astype(np.float32)
    del b19_slope, b19_clean

    # --- Group A: USGS 3DEP 10 m Sub-Pixel Scarp & Chi Knickpoints ---
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
    # Piedmont weight peaks on [0, 11 deg] where 77% of Basin-and-Range faults sit, damps >=14 deg cliffs
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
    # Spread 10 m channel knickpoints 1.6 px laterally onto adjacent scarp banks
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

    # 1D Sub-Pixel Scarp & Channel Knickpoint Localizer Branches
    l_scarp10m = np.where(
        valid,
        0.34 * _sat(ex_max, 0.85) * (0.35 + 0.65 * pied_gate)
        + 0.26 * _sat(curv_pied, 1.60)
        + 0.22 * _sat(lin_coh, 0.22) * (0.40 + 0.60 * pied_gate)
        + 0.18 * _sat(steep_step_grad, 3.5) * pied_gate,
        0.0,
    ).astype(np.float32)
    l_chi10m = np.where(
        valid,
        0.62 * _sat(chi_step_sm, 0.25) + 0.38 * _sat(ksn_sm, 2.2),
        0.0,
    ).astype(np.float32)
    del ex_p90, std_norm, curv10_prof, curv_pied, lin_coh, steep_step_grad, chi_step_sm, ksn_sm
    gc.collect()

    # --- Group B: Tufa-Filtered Paleo/Blind Hydrothermal Vents & Alteration ---
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

    X[:, 8] = np.log1p(paleo_plume * 4.0)[foot]
    X[:, 9] = np.log1p(probe_plume * 3.0)[foot]
    X[:, 10] = np.log1p(spring_plume * 2.5)[foot]
    X[:, 11] = np.log1p(district_halo)[foot]

    with rasterio.open(geodawn_ext_tif) as dsext:
        thk_u8 = dsext.read(1).astype(np.float32)
        uth_u8 = dsext.read(3).astype(np.float32)
        tmi150_u8 = dsext.read(4).astype(np.float32)
    ext_valid = valid & (thk_u8 > 0) & (tmi150_u8 > 0)
    # Low Th/K == high hydrothermal K/Th enrichment
    k_over_th_z = -mesoscale_zscore(thk_u8, ext_valid, sigma_px=40.0)
    u_over_th_z = mesoscale_zscore(uth_u8, ext_valid, sigma_px=40.0)
    b2_rtp = _read_tf(2)
    rtp_z30 = mesoscale_zscore(b2_rtp, ext_valid & np.isfinite(b2_rtp), sigma_px=30.0)
    tmi150_z30 = mesoscale_zscore(tmi150_u8, ext_valid, sigma_px=30.0)
    # Grauch (2001): positive when shallow RTP is demagnetized relative to 150 m upward-continued TMI
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

    X[:, 12] = k_over_th_z[foot]
    X[:, 13] = u_over_th_z[foot]
    X[:, 14] = grauch_demag[foot]
    X[:, 15] = mt_grad[foot]
    X[:, 16] = hf_scarp[foot]

    vent_gate = np.clip(
        0.35
        + 0.65
        * _sat(
            paleo_plume * 2.5 + probe_plume * 2.0 + spring_plume * 1.2 + 0.25 * district_halo,
            0.60,
        ),
        0.35,
        1.0,
    ).astype(np.float32)
    del paleo_plume, probe_plume, spring_plume, district_halo, k_over_th_z, u_over_th_z, grauch_demag, hf_scarp
    gc.collect()

    # --- Group C: Province-Debiased Subsurface Potential, Cover & Shoreline Null ---
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
    del b18_grav, gz_approx, grav_tilt, gy_gt, gx_gt

    b15_base = _read_tf(15)
    base_log = np.where(valid, np.log1p(np.maximum(_clean_valid(b15_base, valid), 0.0)), 0.0).astype(
        np.float32
    )
    gy_b, gx_b = _grad_xy(base_log, valid, sigma=1.8)
    base_step = np.hypot(gx_b, gy_b).astype(np.float32)
    del b15_base, gy_b, gx_b

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
    del gy_g, gx_g, gh

    b8_s2i = _read_tf(8)
    s2i_z = mesoscale_zscore(b8_s2i, valid & np.isfinite(b8_s2i), sigma_px=45.0)
    del b8_s2i

    b4_dil = _read_tf(4)
    dil_z = mesoscale_zscore(b4_dil, valid & np.isfinite(b4_dil), sigma_px=45.0)
    del b4_dil

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
    del b12_elev, s10_p90, dem10_mean, gy_z10, gx_z10, gy_c100, gx_c100, gy_s, gx_s

    X[:, 17] = gslope_z[foot]
    X[:, 18] = grav_tilt_grad[foot]
    X[:, 19] = base_log[foot]
    X[:, 20] = base_step[foot]
    X[:, 21] = dip_concord[foot]
    X[:, 22] = s2i_z[foot]
    X[:, 23] = dil_z[foot]
    X[:, 24] = transgress[foot]
    X[:, 25] = lahontan_null[foot]

    # Subsurface + Hydrothermal 1D Crest Localizer (with & without hydrothermal channels)
    l_grav_base = np.where(
        valid,
        0.42 * _sat(grav_tilt_grad, 0.22)
        + 0.34 * _sat(base_step, 0.16)
        + 0.24 * _sat( np.maximum(gslope_z, 0.0), 1.8),
        0.0,
    ).astype(np.float32)
    l_vent_sub = np.where(
        valid,
        (0.54 * l_grav_base + 0.28 * _sat(grauch_edge, 0.45) + 0.18 * _sat(mt_grad, 0.015))
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
        base_log,
        base_step,
        dip_concord,
        s2i_z,
        dil_z,
        transgress,
        lahontan_null,
        slope_100m_deg,
    )
    gc.collect()

    return {
        "X_foot": X,
        "valid": valid,
        "L_scarp10m": l_scarp10m,
        "L_chi10m": l_chi10m,
        "L_grav_base": l_grav_base,
        "L_vent_sub": l_vent_sub,
        "vent_stats": {
            "paleo_geothermal": paleo_stats,
            "temperature_probe_2m": probe_stats,
            "active_thermal_springs": spring_stats,
        },
    }


def fit_predict_ventscarp_loqo(
    X_foot: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
    quad: np.ndarray,
    label_mask: np.ndarray,
    *,
    include_vent_features: bool = True,
    excluded_mask: np.ndarray | None = None,
    guard_px: int = 12,
    neg_buffer_px: float = 5.0,
    neg_pos_ratio: int = 4,
    seed: int = 20261025,
    max_iter: int = 185,
    calib_weight: float = 0.80,
    power_gamma: float = 3.1,
) -> dict[str, np.ndarray]:
    """Fit a strictly Out-of-Quadrant (LOQO) ensemble with or without Group B vent features."""
    valid_b = np.asarray(valid, dtype=bool) & np.asarray(footprint, dtype=bool)
    if include_vent_features:
        p_all = fit_single_loqo(
            X_foot,
            footprint,
            valid_b,
            quad,
            label_mask,
            feature_cols=DEBIASED_VENT_INDICES,
            excluded_mask=excluded_mask,
            guard_px=guard_px,
            neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio,
            seed=int(seed),
            max_iter=max_iter,
        )
        p_sub = fit_single_loqo(
            X_foot,
            footprint,
            valid_b,
            quad,
            label_mask,
            feature_cols=VENT_SUBSURF_INDICES,
            excluded_mask=excluded_mask,
            guard_px=guard_px,
            neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio,
            seed=int(seed) + 11,
            max_iter=max_iter,
        )
        raw_proba = (np.float32(0.45) * p_all + np.float32(0.55) * p_sub).astype(np.float32)
    else:
        novent_deb = tuple(i for i in NOVENT_INDICES if i != 19)
        novent_sub = (0, 3, 4, 6, 7) + tuple(i for i in GROUP_C_SUBSURF_INDICES if i != 19)
        p_all = fit_single_loqo(
            X_foot,
            footprint,
            valid_b,
            quad,
            label_mask,
            feature_cols=novent_deb,
            excluded_mask=excluded_mask,
            guard_px=guard_px,
            neg_buffer_px=neg_buffer_px,
            neg_pos_ratio=neg_pos_ratio,
            seed=int(seed),
            max_iter=max_iter,
        )
        p_sub = fit_single_loqo(
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
            seed=int(seed) + 11,
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


def build_ventscarp_crest_surface(
    proba_2d: np.ndarray,
    l_scarp10m: np.ndarray,
    l_chi10m: np.ndarray,
    l_sub: np.ndarray,
    valid: np.ndarray,
    *,
    scarp_weight: float = 0.92,
    chi_weight: float = 0.88,
    sub_weight: float = 1.25,
) -> dict[str, np.ndarray]:
    """Fuse LOQO fault posterior with 10 m sub-pixel scarp, 10 m chi-step, and subsurface crests."""
    valid_b = np.asarray(valid, dtype=bool)
    p = np.where(valid_b, np.clip(np.asarray(proba_2d, dtype=np.float32), 0.0, 1.0), 0.0)
    e_line = np.maximum(
        np.float32(scarp_weight) * np.asarray(l_scarp10m, dtype=np.float32),
        np.maximum(
            np.float32(chi_weight) * np.asarray(l_chi10m, dtype=np.float32),
            np.float32(sub_weight) * np.asarray(l_sub, dtype=np.float32),
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


def build_soft_tversky_allocation(
    s_crest: np.ndarray,
    candidate_pool: np.ndarray,
    *,
    n_peaks: int = 47000,
    target_mass: float = 37654.0,
    p_min: float = 0.35,
    min_dist_px: float = 2.9,
) -> np.ndarray:
    """Assign monotone continuous Tversky weights ``p_i in [p_min, 1.0]`` summing to ``target_mass``.

    Addresses docs/NEXT_STEPS.md Item #4 using ``vendor/gems57/metric.py::dti_exact``:
    selects ``n_peaks`` Poisson-spaced 1D crest maxima and maps descending crest rank
    ``u_k in [0, 1]`` via ``p(u) = p_min + (1 - p_min) * (1 - u)^q`` with exponent ``q > 0``
    solved analytically so ``E[p] * n_actual == target_mass``.
    """
    if not (0.0 < p_min < 1.0):
        raise ValueError("p_min must lie in (0, 1)")
    sel = spaced_top_mask(
        s_crest,
        candidate_pool,
        int(n_peaks),
        min_dist_px=float(min_dist_px),
        cand_cap=900_000,
    )
    idx = np.flatnonzero(sel)
    n_act = int(idx.size)
    out = np.zeros(s_crest.shape, dtype=np.float32)
    if n_act == 0:
        return out
    vals = s_crest.ravel()[idx]
    order = np.argsort(-vals, kind="mergesort")
    sorted_idx = idx[order]
    if n_act <= int(round(target_mass)):
        out.ravel()[sorted_idx] = 1.0
        return out

    mean_target = float(target_mass) / float(n_act)
    frac = np.clip((mean_target - p_min) / (1.0 - p_min), 0.05, 0.98)
    # Integral_0^1 (1 - u)^q du = 1 / (q + 1) == frac  =>  q = (1 / frac) - 1
    q_exp = max(0.05, (1.0 / frac) - 1.0)
    u = np.linspace(0.0, 1.0, n_act, dtype=np.float64)
    w = p_min + (1.0 - p_min) * np.power(1.0 - u, q_exp)
    # Exact mass normalization inside [p_min, 1.0]
    w = np.clip(w * (target_mass / max(float(w.sum()), 1e-8)), p_min, 1.0)
    out.ravel()[sorted_idx] = w.astype(np.float32)
    return out
