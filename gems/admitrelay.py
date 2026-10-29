"""ADMITRELAY lane (2026-10-29): Multi-Scale Elastic Admittance Breakdown,
Saunders-Dickson Thorium-Regressed K/U Metasomatism Redox Dipole, Giggenbach
Kinetic Geothermometer Mixing, and Pollard-Segall Crack-Tip Relay / Broadside
Stress-Shadow Mechanics.

Pre-registered in ``docs/HYPOTHESES_20261029_ADMITRELAY.md`` prior to implementation.

Strict zero-leakage contract (Protocol Rules 2 & 4):
- ``compute_or_load_zero_catalogue_features`` reads ONLY geophysical, topographic,
  radiometric, and chemical columns (explicitly refusing ``dist_known_fault_px``,
  ``existing_faults.tif``, or any QFaults/SGMC catalogue layer).
- ``pollard_segall_visible_features`` accepts ONLY the caller's ``vis`` boolean
  array (``fold["visible"]`` during ``gems57-pooled-hide-v2`` spatial holdout;
  ``existing_faults.tif`` ONLY at final deployment).
- Block-streamed in float32 (< 500 MB peak RSS inside 3.8 GiB 0-swap workspace).
"""
from __future__ import annotations

import csv
import gc
import io
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.signal import fftconvolve

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / ".cache" / "gems_inputs"
EXT = INPUTS / "external"
CACHE_DIR = ROOT / ".cache" / "admitrelay"

SENTINEL_CUTOFF = -1e30

ZERO_CAT_FEATURE_NAMES: tuple[str, ...] = (
    "admit_coherence_drop",        # 0: H-1029A Forsyth coherence drop (2.4 km -> 0.4 km)
    "admit_jump_crest",            # 1: H-1029A |grad Z_gh(0.4 km)| mechanical boundary
    "admit_basement_decouple",     # 2: H-1029A gravity vs cover gradient decoupling
    "fault_wedge_breccia_deficit", # 3: H-1029A hanging-wall porous-breccia deficit x MT
    "rad_kd_adularia_excess",      # 4: H-1029B Saunders-Dickson Th-regressed K excess
    "rad_kd_ud_redox_dipole",      # 5: H-1029B antiparallel -grad(K_d).grad(U_d) redox front
    "mag_up150_demag_persistence", # 6: H-1029B GeoDAWN TMI_up150 vs TMI magnetite destruction
    "scarp10m_lahontan_deconf",    # 7: H-1029B 10m subpixel scarp x gravity corroboration
    "kinetic_cat_chalc_gap",       # 8: H-1029D Giggenbach (T_NaKCa - T_chalc) mixing clock
    "quartz_probe_sinter_upflow",  # 9: H-1029D quartz disequilibrium + 2m probes + sinter
    "mt_claycap_seal_margin",      # 10: H-1029D MT clay-cap lateral edge x thermal upflow
    "transtension_strain_gap",     # 11: H-1029D GPS shear*dilatation x seismic gap
)

VISIBLE_FEATURE_NAMES: tuple[str, ...] = (
    "vis_log_dist",
    "vis_tip_lobe_ps",
    "vis_broadside_shadow_ps",
    "vis_net_pollard_segall",
    "vis_gauss_8px",
    "vis_gauss_24px",
    "h19_centerline_exact",
    "h19_decay_2px",
)


def _masked_smooth(arr: np.ndarray, valid: np.ndarray, den_cache: dict[float, np.ndarray], sigma: float) -> np.ndarray:
    if sigma not in den_cache:
        den_cache[sigma] = np.maximum(ndi.gaussian_filter(valid.astype(np.float32), sigma=sigma), 1e-6)
    tmp = np.where(valid, arr, np.float32(0.0)).astype(np.float32)
    ndi.gaussian_filter(tmp, sigma=sigma, output=tmp)
    tmp /= den_cache[sigma]
    tmp[~valid] = 0.0
    return tmp


def _clean_band(ds: rasterio.DatasetReader, band: int, valid: np.ndarray) -> np.ndarray:
    a = ds.read(band).astype(np.float32)
    ok = valid & np.isfinite(a) & (a > SENTINEL_CUTOFF)
    med = np.float32(np.median(a[ok])) if ok.any() else np.float32(0.0)
    a[~ok] = med
    return a


def _grad2d_f32(arr: np.ndarray, eroded: np.ndarray, valid: np.ndarray, den_cache: dict[float, np.ndarray], sigma: float = 1.2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    s = _masked_smooth(arr, valid, den_cache, sigma)
    gy = np.zeros_like(s)
    gx = np.zeros_like(s)
    gy[1:-1, :] = np.float32(0.5) * (s[2:, :] - s[:-2, :])
    gx[:, 1:-1] = np.float32(0.5) * (s[:, 2:] - s[:, :-2])
    gy[~eroded] = 0.0
    gx[~eroded] = 0.0
    gn = np.hypot(gy, gx).astype(np.float32)
    return gy, gx, gn


def _rzs_fp(arr_2d: np.ndarray, fp_lin: np.ndarray) -> np.ndarray:
    v = arr_2d.ravel()[fp_lin].astype(np.float32)
    med = np.float32(np.median(v))
    iqr = np.float32(max(float(np.quantile(v, 0.75) - np.quantile(v, 0.25)), 1e-6))
    return np.clip((v - med) / iqr, -3.0, 6.0).astype(np.float32)


def _rzs_2d(arr: np.ndarray, valid: np.ndarray) -> np.ndarray:
    v = arr[valid]
    med = np.float32(np.median(v))
    iqr = np.float32(max(float(np.quantile(v, 0.75) - np.quantile(v, 0.25)), 1e-6))
    out = np.clip((arr - med) / iqr, -3.0, 6.0).astype(np.float32)
    out[~valid] = 0.0
    return out


def _pct_rank(arr: np.ndarray, valid: np.ndarray) -> np.ndarray:
    v = arr[valid]
    qgrid = np.linspace(0.0, 1.0, 401)
    knots = np.maximum.accumulate(np.quantile(v, qgrid))
    out = np.zeros(arr.shape, dtype=np.float32)
    out[valid] = np.interp(v, knots, qgrid).astype(np.float32)
    return out


def _conditional_residual_on_th(target: np.ndarray, th: np.ndarray, valid: np.ndarray, n_bins: int = 48) -> np.ndarray:
    tv = th[valid]
    yv = target[valid]
    edges = np.unique(np.quantile(tv, np.linspace(0.0, 1.0, n_bins + 1)))
    if edges.size < 3:
        out = (target - np.float32(np.median(yv))).astype(np.float32)
        out[~valid] = 0.0
        return out
    bins = np.clip(np.digitize(tv, edges[1:-1]), 0, edges.size - 2)
    cnt = np.maximum(np.bincount(bins, minlength=edges.size - 1), 1)
    sums = np.bincount(bins, weights=yv.astype(np.float64), minlength=edges.size - 1)
    means = ndi.gaussian_filter1d(sums / cnt, sigma=1.2)
    centers = 0.5 * (edges[:-1] + edges[1:])
    out = np.zeros(target.shape, dtype=np.float32)
    out[valid] = (yv - np.interp(tv, centers, means)).astype(np.float32)
    return out


def _load_kinetic_and_thermal_grids(shape: tuple[int, int], valid: np.ndarray, det_elev: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    H, W = shape
    kin_grid = np.zeros((H, W), dtype=np.float32)
    qtz_grid = np.zeros((H, W), dtype=np.float32)

    ws_path = INPUTS / "gdr_wellspring_in_footprint.csv"
    if not ws_path.is_file():
        ws_path = EXT / "gdr_wellspring_in_footprint.csv"
    with ws_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                r = int(float(row["row"]))
                c = int(float(row["col"]))
            except (KeyError, ValueError):
                continue
            if not (0 <= r < H and 0 <= c < W and valid[r, c]):
                continue
            def _f(k: str) -> float:
                try:
                    x = float(row.get(k, ""))
                    return x if np.isfinite(x) else 0.0
                except ValueError:
                    return 0.0
            t_m = _f("temp_c")
            t_q = _f("geothermquartz_c")
            t_ch = _f("geothermchalc_c")
            t_ca = _f("geothermcat_c")
            if t_m >= 18.0 and 25.0 < t_ch < 260.0 and 25.0 < t_ca < 320.0:
                gap = max(0.0, min(t_ca - t_ch, 140.0))
                if gap > kin_grid[r, c]:
                    kin_grid[r, c] = gap
            if t_m >= 18.0 and 30.0 < t_q < 280.0:
                qd = max(0.0, min(t_q - t_m, 160.0))
                if qd > qtz_grid[r, c]:
                    qtz_grid[r, c] = qd

    paleo_zip = EXT / "paleo_geothermal_regional.zip"
    if paleo_zip.is_file():
        with zipfile.ZipFile(paleo_zip) as zf:
            csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if csv_names:
                txt = io.TextIOWrapper(zf.open(csv_names[0]), encoding="utf-8", errors="replace")
                for row in csv.DictReader(txt):
                    blob = " ".join(str(v).lower() for v in row.values())
                    if "tufa" in blob and "sinter" not in blob:
                        continue
                    x_val = y_val = None
                    for k, v in row.items():
                        kl = k.lower()
                        try:
                            fv = float(v)
                        except (TypeError, ValueError):
                            continue
                        if kl in ("utm_e", "utm_x", "x", "easting") and 200_000 < fv < 700_000:
                            x_val = fv
                        elif kl in ("utm_n", "utm_y", "y", "northing") and 4_000_000 < fv < 4_600_000:
                            y_val = fv
                    if x_val is not None and y_val is not None:
                        cc = int((x_val - 243350.0) / 100.0)
                        rr = int((4508550.0 - y_val) / 100.0)
                        if 0 <= rr < H and 0 <= cc < W and valid[rr, cc]:
                            qtz_grid[rr, cc] = max(qtz_grid[rr, cc], 95.0)

    low_sink = _pct_rank(-det_elev, valid)
    playa_veto = np.clip(1.25 - 0.85 * (low_sink ** 2), 0.25, 1.0).astype(np.float32)
    kin_f = (0.65 * ndi.gaussian_filter(kin_grid, sigma=6.0) + 0.35 * ndi.gaussian_filter(kin_grid, sigma=16.0)) * playa_veto
    qtz_f = (0.65 * ndi.gaussian_filter(qtz_grid, sigma=6.0) + 0.35 * ndi.gaussian_filter(qtz_grid, sigma=16.0))
    kin_f[~valid] = 0.0
    qtz_f[~valid] = 0.0
    return kin_f.astype(np.float32), qtz_f.astype(np.float32)


def compute_or_load_zero_catalogue_features(fp_lin: np.ndarray, valid_2d: np.ndarray, force: bool = False) -> tuple[np.ndarray, dict]:
    """Stream-compute or load the 12 zero-catalogue ADMITRELAY footprint features (< 500 MB RSS)."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / "admitrelay_zero_cat_v1.npz"
    if cache_file.is_file() and not force:
        z = np.load(cache_file)
        if z["X_fp"].shape == (fp_lin.size, len(ZERO_CAT_FEATURE_NAMES)):
            return z["X_fp"].astype(np.float32), {"cached": True, "path": str(cache_file)}

    H, W = valid_2d.shape
    eroded = ndi.binary_erosion(valid_2d, iterations=2)
    den_cache: dict[float, np.ndarray] = {}
    X_fp = np.zeros((fp_lin.size, len(ZERO_CAT_FEATURE_NAMES)), dtype=np.float32)

    tf_path = INPUTS / "training_features.tif"

    # --- BLOCK 1: H-1029A Elastic Admittance Breakdown & Porous Fault-Wedge Deficit (cols 0..3) ---
    with rasterio.open(tf_path) as ds:
        det_elev = _clean_band(ds, 12, valid_2d)
        grav = _clean_band(ds, 13, valid_2d)
        base_d = _clean_band(ds, 15, valid_2d)
        cond = _clean_band(ds, 17, valid_2d)

    gy_g, gx_g, gn_g = _grad2d_f32(grav, eroded, valid_2d, den_cache, sigma=1.2)
    gy_h, gx_h, _ = _grad2d_f32(det_elev, eroded, valid_2d, den_cache, sigma=1.2)
    dot_gh = (gy_g * gy_h + gx_g * gx_h).astype(np.float32)
    gg = (gy_g * gy_g + gx_g * gx_g).astype(np.float32)
    hh = (gy_h * gy_h + gx_h * gx_h).astype(np.float32)
    del gy_h, gx_h

    eps_g = np.float32(np.quantile(gg[valid_2d], 0.35) + 1e-8)
    eps_h = np.float32(np.quantile(hh[valid_2d], 0.35) + 1e-8)

    c_gh_4 = _masked_smooth(dot_gh, valid_2d, den_cache, 4.0)
    gg_4 = _masked_smooth(gg, valid_2d, den_cache, 4.0) + eps_g
    hh_4 = _masked_smooth(hh, valid_2d, den_cache, 4.0) + eps_h
    z_gh_4 = np.clip(c_gh_4 / hh_4, -5.0, 5.0).astype(np.float32)
    coh_4 = (c_gh_4 * c_gh_4) / (gg_4 * hh_4)
    del c_gh_4, gg_4, hh_4

    c_gh_24 = _masked_smooth(dot_gh, valid_2d, den_cache, 24.0)
    coh_24 = (c_gh_24 * c_gh_24) / ((_masked_smooth(gg, valid_2d, den_cache, 24.0) + eps_g) * (_masked_smooth(hh, valid_2d, den_cache, 24.0) + eps_h))
    del dot_gh, hh, c_gh_24

    gn_g_p75 = np.float32(max(float(np.quantile(gn_g[valid_2d], 0.75)), 1e-6))
    grav_gate = np.tanh(gn_g / gn_g_p75).astype(np.float32)
    del gn_g

    X_fp[:, 0] = _rzs_fp(np.maximum(0.0, coh_24 - coh_4) * grav_gate, fp_lin)
    del coh_4, coh_24
    _, _, gn_z = _grad2d_f32(z_gh_4, eroded, valid_2d, den_cache, sigma=1.5)
    X_fp[:, 1] = _rzs_fp(gn_z * grav_gate, fp_lin)
    del z_gh_4, gn_z

    gy_d, gx_d, gn_d = _grad2d_f32(-base_d, eroded, valid_2d, den_cache, sigma=1.5)
    dot_gd = (gy_g * gy_d + gx_g * gx_d).astype(np.float32)
    dd = (gy_d * gy_d + gx_d * gx_d).astype(np.float32)
    del gy_g, gx_g, gy_d, gx_d
    eps_d = np.float32(np.quantile(dd[valid_2d], 0.35) + 1e-8)
    c_gd_5 = _masked_smooth(dot_gd, valid_2d, den_cache, 5.0)
    coh_gd_5 = (c_gd_5 * c_gd_5) / ((_masked_smooth(gg, valid_2d, den_cache, 5.0) + eps_g) * (_masked_smooth(dd, valid_2d, den_cache, 5.0) + eps_d))
    del dot_gd, gg, dd, c_gd_5
    gn_d_p75 = np.float32(max(float(np.quantile(gn_d[valid_2d], 0.75)), 1e-6))
    base_gate = np.tanh(gn_d / gn_d_p75).astype(np.float32)
    del gn_d
    X_fp[:, 2] = _rzs_fp(np.clip(1.0 - coh_gd_5, 0.0, 1.0) * base_gate, fp_lin)
    del coh_gd_5

    grav_res = _conditional_residual_on_th(grav, base_d, valid_2d, n_bins=40)
    del grav, base_d
    log_cond = np.log10(np.maximum(cond - np.float32(np.min(cond[valid_2d])) + 1e-3, 1e-3)).astype(np.float32)
    del cond
    mt_pct = _pct_rank(log_cond, valid_2d)
    X_fp[:, 3] = _rzs_fp(np.maximum(0.0, -grav_res) * mt_pct * grav_gate, fp_lin)
    del grav_res
    gc.collect()

    # --- BLOCK 2: H-1029B Saunders-Dickson Th-Regressed K/U Metasomatism & Demag (cols 4..7) ---
    rad_path = INPUTS / "geodawn_rad_u8.tif"
    if not rad_path.is_file():
        rad_path = EXT / "geodawn_rad_u8.tif"
    with rasterio.open(rad_path) as rds:
        K_ch = _clean_band(rds, 1, valid_2d)
        Th_ch = _clean_band(rds, 2, valid_2d)
        U_ch = _clean_band(rds, 3, valid_2d)
    with rasterio.open(tf_path) as ds:
        elev_slope = _clean_band(ds, 19, valid_2d)
        rtp = _clean_band(ds, 2, valid_2d)
        tmi = _clean_band(ds, 14, valid_2d)

    kd = _conditional_residual_on_th(K_ch, Th_ch, valid_2d, n_bins=48)
    ud = _conditional_residual_on_th(U_ch, Th_ch, valid_2d, n_bins=48)
    del K_ch, Th_ch, U_ch
    slope_gate = np.tanh(np.maximum(elev_slope, 0.0) / max(float(np.quantile(elev_slope[valid_2d], 0.35)), 1e-4)).astype(np.float32)
    del elev_slope
    kd_pos = np.maximum(0.0, _rzs_2d(kd, valid_2d))
    X_fp[:, 4] = _rzs_fp(kd_pos * (0.35 + 0.65 * slope_gate), fp_lin)
    del slope_gate

    gy_k, gx_k, gn_k = _grad2d_f32(kd, eroded, valid_2d, den_cache, sigma=2.0)
    gy_u, gx_u, gn_u = _grad2d_f32(ud, eroded, valid_2d, den_cache, sigma=2.0)
    del kd, ud
    anti_ku = np.maximum(0.0, -(gy_k * gy_u + gx_k * gx_u)).astype(np.float32)
    ku_scale = np.float32(max(float(np.quantile(gn_k[valid_2d], 0.85) * np.quantile(gn_u[valid_2d], 0.85)), 1e-6))
    del gy_k, gx_k, gn_k, gy_u, gx_u, gn_u
    X_fp[:, 5] = _rzs_fp(np.tanh(anti_ku / ku_scale) * (0.40 + 0.60 * grav_gate), fp_lin)
    del anti_ku

    with rasterio.open(EXT / "geodawn_extensions_u8.tif") as eds:
        tmi_up150 = _clean_band(eds, 4, valid_2d)
    demag = np.maximum(0.0, _rzs_2d(tmi_up150, valid_2d) - 0.5 * (_rzs_2d(tmi, valid_2d) + _rzs_2d(rtp, valid_2d)))
    del tmi_up150, tmi, rtp
    X_fp[:, 6] = _rzs_fp(demag * (0.35 + 0.65 * kd_pos), fp_lin)
    del demag, kd_pos

    with rasterio.open(EXT / "topo_10m_derived_100m_u8.tif") as tds:
        s_p90 = _clean_band(tds, 1, valid_2d)
        s_max = _clean_band(tds, 2, valid_2d)
    sub_scarp = _rzs_2d(np.maximum(0.0, s_max - 0.85 * s_p90), valid_2d)
    del s_p90, s_max
    X_fp[:, 7] = _rzs_fp(sub_scarp * (0.25 + 0.75 * np.maximum(grav_gate, base_gate)), fp_lin)
    del sub_scarp, base_gate
    gc.collect()

    # --- BLOCK 3: H-1029D Giggenbach Kinetic Mixing, MT Seal Margin & Strain Gap (cols 8..11) ---
    kin_f, qtz_f = _load_kinetic_and_thermal_grids((H, W), valid_2d, det_elev)
    del det_elev
    X_fp[:, 8] = _rzs_fp(kin_f, fp_lin)
    X_fp[:, 9] = _rzs_fp(qtz_f, fp_lin)

    _, _, gn_mt = _grad2d_f32(log_cond, eroded, valid_2d, den_cache, sigma=2.0)
    del log_cond
    gn_mt_p80 = np.float32(max(float(np.quantile(gn_mt[valid_2d], 0.80)), 1e-6))
    therm_comb = _pct_rank(kin_f + 0.6 * qtz_f, valid_2d)
    del kin_f, qtz_f
    X_fp[:, 10] = _rzs_fp(np.tanh(gn_mt / gn_mt_p80) * mt_pct * (0.35 + 0.65 * therm_comb), fp_lin)
    del gn_mt, mt_pct, therm_comb

    with rasterio.open(tf_path) as ds:
        shear = _clean_band(ds, 7, valid_2d)
        dilat = _clean_band(ds, 8, valid_2d)
        deq = _clean_band(ds, 10, valid_2d)
        ieq = _clean_band(ds, 16, valid_2d)
    z_sh = np.maximum(0.0, _rzs_2d(shear, valid_2d))
    z_di = np.maximum(0.0, _rzs_2d(dilat, valid_2d))
    seis_quiet = 1.0 - 0.5 * _pct_rank(ieq, valid_2d) * (1.0 - _pct_rank(deq, valid_2d))
    del shear, dilat, deq, ieq
    X_fp[:, 11] = _rzs_fp(np.sqrt(z_sh * (0.25 + z_di)) * seis_quiet * (0.40 + 0.60 * grav_gate), fp_lin)
    del z_sh, z_di, seis_quiet, grav_gate, den_cache
    gc.collect()

    np.savez_compressed(cache_file, X_fp=X_fp, feature_names=np.array(ZERO_CAT_FEATURE_NAMES))
    return X_fp, {"cached": False, "path": str(cache_file)}


def _build_pollard_segall_kernels() -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    out = []
    for az_deg in (-25.0, -8.0, 8.0, 22.0, 38.0, 56.0):
        az = np.deg2rad(az_deg)
        uy, ux = -np.cos(az), np.sin(az)
        ny, nx = ux, -uy

        r0 = 4
        y0, x0 = np.mgrid[-r0 : r0 + 1, -r0 : r0 + 1].astype(np.float32)
        s0 = y0 * uy + x0 * ux
        p0 = y0 * ny + x0 * nx
        k_det = np.exp(-0.5 * (s0 / 2.6) ** 2 - 0.5 * (p0 / 0.85) ** 2).astype(np.float32)
        k_det /= max(float(k_det.sum()), 1e-6)

        rt = 28
        yt, xt = np.mgrid[-rt : rt + 1, -rt : rt + 1].astype(np.float32)
        rr_t = np.hypot(yt, xt)
        st = yt * uy + xt * ux
        pt = yt * ny + xt * nx
        cos_a = np.abs(st) / np.maximum(rr_t, 1e-4)
        k_tip = (cos_a ** 4) * np.exp(-0.5 * (pt / 3.2) ** 2) * np.exp(-rr_t / 14.0)
        k_tip[rr_t <= 2.2] = 0.0
        k_tip /= max(float(k_tip.sum()), 1e-6)

        rb = 18
        yb, xb = np.mgrid[-rb : rb + 1, -rb : rb + 1].astype(np.float32)
        rr_b = np.hypot(yb, xb)
        sb = yb * uy + xb * ux
        pb = yb * ny + xb * nx
        sin_a = np.abs(pb) / np.maximum(rr_b, 1e-4)
        k_broad = (sin_a ** 4) * np.exp(-0.5 * (sb / 3.5) ** 2) * np.exp(-rr_b / 9.0)
        k_broad[rr_b <= 2.5] = 0.0
        k_broad /= max(float(k_broad.sum()), 1e-6)

        out.append((k_det.astype(np.float32), k_tip.astype(np.float32), k_broad.astype(np.float32)))
    return out


_PS_KERNELS = _build_pollard_segall_kernels()


def pollard_segall_visible_features(
    vis: np.ndarray,
    dh19_2d: np.ndarray,
    fp_lin: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute strictly fold-visible Pollard-Segall crack-tip / broadside-shadow features + zero-cat H19-5."""
    vf = vis.astype(np.float32)
    d_vis = ndi.distance_transform_edt(~vis).astype(np.float32)

    nbr_k = np.ones((3, 3), dtype=np.int16)
    nbr_k[1, 1] = 0
    nbr_cnt = ndi.convolve(vis.astype(np.int16), nbr_k, mode="constant", cval=0)
    tips = (vis & (nbr_cnt <= 2)).astype(np.float32)
    interior = (vis & (nbr_cnt >= 2)).astype(np.float32)
    del nbr_cnt

    tip_lobe = np.zeros_like(vf)
    broad_shadow = np.zeros_like(vf)

    for k_det, k_tip, k_broad in _PS_KERNELS:
        orient_w = fftconvolve(vf, k_det, mode="same").astype(np.float32)
        src_tip = tips * (0.25 + orient_w) + 0.35 * vf * orient_w
        tl = np.maximum(0.0, fftconvolve(src_tip, k_tip, mode="same").astype(np.float32))
        np.maximum(tip_lobe, tl, out=tip_lobe)
        del src_tip, tl
        src_int = interior * orient_w
        bs = np.maximum(0.0, fftconvolve(src_int, k_broad, mode="same").astype(np.float32))
        broad_shadow += bs
        del orient_w, src_int, bs
    del tips, interior

    broad_shadow /= np.float32(len(_PS_KERNELS))
    tl_fp = tip_lobe.ravel()[fp_lin]
    bs_fp = broad_shadow.ravel()[fp_lin]
    del tip_lobe, broad_shadow

    t_scale = np.float32(max(float(np.quantile(tl_fp, 0.95)), 1e-6))
    b_scale = np.float32(max(float(np.quantile(bs_fp, 0.95)), 1e-6))
    tip_norm = np.tanh(tl_fp / t_scale).astype(np.float32)
    broad_norm = np.tanh(bs_fp / b_scale).astype(np.float32)
    del tl_fp, bs_fp
    net_ps = (tip_norm - np.float32(0.65) * broad_norm).astype(np.float32)

    g8 = ndi.gaussian_filter(vf, sigma=8.0).ravel()[fp_lin].astype(np.float32)
    g24 = ndi.gaussian_filter(vf, sigma=24.0).ravel()[fp_lin].astype(np.float32)
    del vf

    dh_fp = dh19_2d.ravel()[fp_lin]
    X_vis = np.column_stack(
        [
            np.log1p(d_vis.ravel()[fp_lin]),
            tip_norm,
            broad_norm,
            net_ps,
            g8,
            g24,
            (dh_fp < 0.5).astype(np.float32),
            np.exp(-dh_fp / 2.0).astype(np.float32),
        ]
    ).astype(np.float32)
    gc.collect()
    return X_vis, d_vis
