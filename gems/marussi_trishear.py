"""MARUSSI-TRISHEAR + WALKER-LANE-VORTICITY lane (2026-10-29, H-92M1 & H-92M2).

Pre-registered in ``docs/HYPOTHESES_20261029_MARUSSI_TRISHEAR.md`` BEFORE implementation:
  H-92M1 (MARUSSI-TRISHEAR):
    - Full 3D Laplace-consistent Marussi potential-field tensor T_ij (Pedersen & Rasmussen
      1990; Bevis & Pedersen 2014) on B13 isostatic gravity (cross-checked against B18)
      and B02 RTP magnetics, isolating elongate 2D fault steps via the scale-free rotational
      invariant dimensionality index D_2D = 1 - |det(T)| / [2*(-I_1/3 + eps)^(3/2)] in [0, 1]
      while rejecting 3D equant plutons/caldera plugs (D_2D -> 0).
    - Allmendinger (1998) trishear blind-fault-propagation monocline operator coupling deep
      2D Marussi basement steps with updip (footwall-shifted 500 m at ~60 deg dip)
      long-wavelength topographic flexure over unconsolidated cover (B15 > 40 m).
    - Cooper & Cowan (2006) potential-field terracing crest sharpener, Gallardo & Meju (2003)
      joint gravity-magnetic cross-gradient & hydrothermally demagnetized conduit detector,
      true Salem et al. (2008) suspended tilt-depth gate from B02 RTP (fixing IR-1028B-3:
      Band 6 `tc` is never treated as magnetic tilt), and Niblett-Bostick electromagnetic
      skin-depth lateral gradient from B17 subsurface conductivity.
  H-92M2 (WALKER-LANE-VORTICITY):
    - Geodetic kinematic vorticity proxy W_k = |gamma_dot| / sqrt(gamma_dot^2 + eps_dot^2)
      (B07, B08, B04) partitioning favored structural strike between NNE Basin-and-Range
      normal extension (low W_k -> N022E) and Walker Lane transtensional step-over /
      pull-apart accommodation zones (high W_k -> N062E sinistral-normal & N318W dextral).

Engineered for < 1.1 GiB peak RSS on 3.8 GiB zero-swap containers via stage-wise band release
and scale-normalized float32 invariant evaluation.
"""
from __future__ import annotations

import gc
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import rankdata

from gems.riesz_locked import _dequant_u8, _load_fournier_diseq_grid

FEATURE_NAMES: tuple[str, ...] = (
    "m01_marussi_grav_d2d_step",
    "m02_marussi_rtp_d2d_step",
    "m03_trishear_blind_monocline",
    "m04_cooper_terracing_crest",
    "m05_gallardo_meju_collinear",
    "m06_gallardo_demag_conduit",
    "m07_salem_true_tilt_depth_gate",
    "m08_niblett_bostick_skindepth_step",
    "m09_radiometric_k_enrichment_step",
    "m10_piedmont_1d_crest_nocanyon",
    "m11_walker_lane_vorticity_wk",
    "m12_vorticity_strike_partition",
    "m13_helmholtz_shear_boundary",
    "m14_fournier_trishear_upflow",
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = ROOT / ".cache" / "marussi_trishear" / "features_fp_v1.npz"


def clean_sentinel_edt(arr: np.ndarray, valid_extra: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Mask non-finite and |x| >= 1e20 float32 sentinels and fill via EDT nearest neighbor."""
    x = np.asarray(arr, dtype=np.float32)
    ok = np.isfinite(x) & (np.abs(x) < 1.0e20)
    if valid_extra is not None:
        ok &= valid_extra
    if not ok.all():
        ind = ndi.distance_transform_edt(~ok, return_distances=False, return_indices=True)
        filled = x[tuple(ind)].astype(np.float32, copy=False)
    else:
        filled = x.copy()
    return filled, ok


def pct_fp(vec_fp: np.ndarray) -> np.ndarray:
    """Empirical [0, 1] percentile transform over the valid footprint."""
    v = np.asarray(vec_fp, dtype=np.float64)
    med = float(np.nanmedian(v)) if np.isfinite(v).any() else 0.0
    v = np.where(np.isfinite(v), v, med)
    r = rankdata(v, method="average")
    return ((r - 0.5) / max(v.size, 1)).astype(np.float32)


def _grad_mag_f32(u: np.ndarray) -> np.ndarray:
    """Memory-lean float32 central-difference gradient magnitude (zero float64 allocations)."""
    gx = np.empty_like(u, dtype=np.float32)
    gy = np.empty_like(u, dtype=np.float32)
    gx[:, 1:-1] = 0.5 * (u[:, 2:] - u[:, :-2])
    gx[:, 0] = u[:, 1] - u[:, 0]
    gx[:, -1] = u[:, -1] - u[:, -2]
    gy[1:-1, :] = 0.5 * (u[2:, :] - u[:-2, :])
    gy[0, :] = u[1, :] - u[0, :]
    gy[-1, :] = u[-1, :] - u[-2, :]
    np.hypot(gx, gy, out=gx)
    return gx


def marussi_tensor_invariants(
    potential_vert_field: np.ndarray,
    lambda_min_px: float = 6.0,
    lambda_max_px: float = 260.0,
    return_strike: bool = True,
) -> dict[str, np.ndarray]:
    """Full 3D Laplace-consistent Marussi tensor invariants in scale-normalized float32."""
    h, w = potential_vert_field.shape
    ky = (2.0 * np.pi * np.fft.fftfreq(h)).astype(np.float32)[:, None]
    kx = (2.0 * np.pi * np.fft.rfftfreq(w)).astype(np.float32)[None, :]
    kr = np.hypot(kx, ky).astype(np.float32)

    k_lo = float(2.0 * np.pi / lambda_max_px)
    k_hi = float(2.0 * np.pi / lambda_min_px)
    bp = ((1.0 - np.exp(-0.5 * (kr / max(k_lo, 1e-6)) ** 2)) * np.exp(-0.5 * (kr / max(k_hi, 1e-6)) ** 2)).astype(np.float32)
    bp[0, 0] = 0.0
    inv_kr = np.where(kr > 1e-7, 1.0 / np.maximum(kr, 1e-7), 0.0).astype(np.float32)

    u0 = potential_vert_field - np.float32(np.mean(potential_vert_field))
    ghat = (np.fft.rfft2(u0) * bp).astype(np.complex64)
    del bp, u0

    txx = np.fft.irfft2((-kx * kx * inv_kr).astype(np.complex64) * ghat, s=(h, w)).astype(np.float32)
    tyy = np.fft.irfft2((-ky * ky * inv_kr).astype(np.complex64) * ghat, s=(h, w)).astype(np.float32)
    txy = np.fft.irfft2((-kx * ky * inv_kr).astype(np.complex64) * ghat, s=(h, w)).astype(np.float32)
    txz = np.fft.irfft2((1j * kx).astype(np.complex64) * ghat, s=(h, w)).astype(np.float32)
    tyz = np.fft.irfft2((1j * ky).astype(np.complex64) * ghat, s=(h, w)).astype(np.float32)
    del ghat, kx, ky, kr, inv_kr

    hg = np.hypot(txz, tyz).astype(np.float32)
    # Normalize T_ij by RMS scale s0 before cubic invariants so float32 never overflows or underflows!
    s0 = np.float32(float(np.std(hg)) + 1e-6)
    txx /= s0
    tyy /= s0
    txy /= s0
    txzn = txz / s0
    tyzn = tyz / s0
    tzz = -(txx + tyy)

    i1 = txx * tyy + tyy * tzz + tzz * txx - txy * txy - txzn * txzn - tyzn * tyzn
    det_t = (
        txx * (tyy * tzz - tyzn * tyzn)
        - txy * (txy * tzz - tyzn * txzn)
        + txzn * (txy * tyzn - tyy * txzn)
    )
    del txx, tyy, tzz, txy, txzn, tyzn
    mag_i1 = np.maximum(-i1 * np.float32(1.0 / 3.0), np.float32(0.0))
    del i1
    eps = np.float32(float(np.quantile(mag_i1[::4, ::4], 0.20)) * 0.05 + 1e-6)
    denom = np.float32(2.0) * ((mag_i1 + eps) * np.sqrt(mag_i1 + eps))
    d2d = np.clip(1.0 - np.abs(det_t) / np.maximum(denom, 1e-12), 0.0, 1.0).astype(np.float32)
    del det_t, mag_i1, denom

    out = dict(d2d=d2d, hg=hg, txz=txz, tyz=tyz)
    if return_strike:
        hg_safe = np.maximum(hg, 1e-9)
        sin_psi = (-tyz / hg_safe).astype(np.float32)
        cos_psi = (-txz / hg_safe).astype(np.float32)
        out["cos_2psi"] = (cos_psi * cos_psi - sin_psi * sin_psi).astype(np.float32)
        out["sin_2psi"] = (2.0 * sin_psi * cos_psi).astype(np.float32)
    return out


def cooper_terracing_gradient(field_filled: np.ndarray, sigma_px: float = 2.8, n_iter: int = 3) -> np.ndarray:
    """Cooper & Cowan (2006) potential-field terracing operator + float32 gradient crest."""
    u = ndi.gaussian_filter(field_filled, sigma=sigma_px).astype(np.float32)
    scale = np.float32(float(np.std(u)) * 0.15 + 1e-6)
    inv_s = np.float32(1.0 / max(float(scale) * 0.05, 1e-6))
    for _ in range(n_iter):
        lap = ndi.laplace(u)
        u = u - np.float32(0.35) * scale * np.tanh(lap * inv_s).astype(np.float32)
        del lap
    return _grad_mag_f32(u)


def salem_true_rtp_tilt_depth_gate(rtp_filled: np.ndarray, smooth_px: float = 2.0) -> np.ndarray:
    """True Salem et al. (2008) suspended magnetic tilt-depth indicator from B02 RTP ONLY."""
    h, w = rtp_filled.shape
    ky = (2.0 * np.pi * np.fft.fftfreq(h)).astype(np.float32)[:, None]
    kx = (2.0 * np.pi * np.fft.rfftfreq(w)).astype(np.float32)[None, :]
    kr = np.hypot(kx, ky).astype(np.float32)
    taper = np.exp(-0.5 * (smooth_px ** 2) * (kr ** 2)).astype(np.float32)
    mhat = (np.fft.rfft2(rtp_filled - np.float32(np.mean(rtp_filled))) * taper).astype(np.complex64)
    del taper
    mx = np.fft.irfft2((1j * kx).astype(np.complex64) * mhat, s=(h, w)).astype(np.float32)
    my = np.fft.irfft2((1j * ky).astype(np.complex64) * mhat, s=(h, w)).astype(np.float32)
    mz = np.fft.irfft2(kr.astype(np.complex64) * mhat, s=(h, w)).astype(np.float32)
    del mhat, kx, ky, kr
    mh = np.hypot(mx, my)
    del mx, my
    eps = np.float32(float(np.quantile(mh[::4, ::4], 0.15)) * 0.1 + 1e-6)
    theta = np.arctan2(mz, mh + eps).astype(np.float32)
    del mz
    grad_theta = _grad_mag_f32(theta)
    z_px = 1.0 / np.maximum(grad_theta, np.float32(0.015))
    del grad_theta
    zero_prox = np.exp(-0.5 * (theta / np.float32(0.42)) ** 2).astype(np.float32)
    del theta
    depth_win = (
        np.clip((z_px - np.float32(1.5)) / np.float32(3.0), 0.0, 1.0)
        * np.exp(-0.5 * (np.maximum(z_px - np.float32(18.0), 0.0) / np.float32(18.0)) ** 2)
    ).astype(np.float32)
    del z_px
    amp_gate = np.tanh(mh / np.float32(float(np.quantile(mh[::4, ::4], 0.50)) + 1e-6)).astype(np.float32)
    del mh
    return (zero_prox * depth_win * amp_gate).astype(np.float32)


def _shift_field_along_vec(field: np.ndarray, ux: np.ndarray, uy: np.ndarray, step_px: float = 5.0) -> np.ndarray:
    """Memory-lean nearest-integer vector lookup field(y + step*uy, x + step*ux) without mgrid."""
    h, w = field.shape
    dy = np.rint(step_px * uy).astype(np.int32)
    dx = np.rint(step_px * ux).astype(np.int32)
    ry = np.clip(np.arange(h, dtype=np.int32)[:, None] + dy, 0, h - 1)
    rx = np.clip(np.arange(w, dtype=np.int32)[None, :] + dx, 0, w - 1)
    return field[ry, rx]


def directional_ridge_response(score_2d: np.ndarray, cos_2psi: np.ndarray, sin_2psi: np.ndarray) -> np.ndarray:
    """Enhance 1D structural fault crests by comparing score_2d to cross-strike neighbors (+-2 px)."""
    psi = np.float32(0.5) * np.arctan2(sin_2psi, cos_2psi)
    nx = np.cos(psi).astype(np.float32)
    ny = np.sin(psi).astype(np.float32)
    del psi
    s_plus = _shift_field_along_vec(score_2d, nx, ny, step_px=2.0)
    s_minus = _shift_field_along_vec(score_2d, nx, ny, step_px=-2.0)
    crest = np.maximum(score_2d - np.float32(0.5) * (s_plus + s_minus), np.float32(0.0))
    return (np.float32(0.55) * score_2d + np.float32(0.90) * crest).astype(np.float32)


def compute_or_load_features(
    fp_lin: np.ndarray,
    fp_mask: np.ndarray,
    *,
    cache_path: Path = DEFAULT_CACHE,
    force: bool = False,
) -> tuple[np.ndarray, dict[str, np.ndarray], dict]:
    """Compute or load the 14-feature H-92M1 + H-92M2 stack on valid footprint pixels."""
    if cache_path.exists() and not force:
        z = np.load(cache_path, allow_pickle=False)
        names = tuple(str(s) for s in z["feature_names"])
        if names == FEATURE_NAMES and z["X_fp"].shape == (fp_lin.size, len(FEATURE_NAMES)):
            aux = {
                "cos_2psi_T": z["cos_2psi_T"].astype(np.float32),
                "sin_2psi_T": z["sin_2psi_T"].astype(np.float32),
                "wk": z["wk"].astype(np.float32),
            }
            return z["X_fp"].astype(np.float32), aux, {"cached": True, "path": str(cache_path)}

    tf_path = ROOT / ".cache" / "gems_inputs" / "training_features.tif"
    topo10_path = ROOT / ".cache" / "gems_inputs" / "external" / "topo_10m_derived_100m_u8.tif"
    ext_path = ROOT / ".cache" / "gems_inputs" / "external" / "geodawn_extensions_u8.tif"
    ws_csv = ROOT / ".cache" / "gems_inputs" / "external" / "gdr_wellspring_in_footprint.csv"
    probe_zip = ROOT / ".cache" / "gems_inputs" / "external" / "2m_temperature_probe_INGENIOUS_regional_data.zip"

    n_fp = fp_lin.size
    X = np.empty((n_fp, len(FEATURE_NAMES)), dtype=np.float32)
    sentinel_counts: dict[str, int] = {}

    with rasterio.open(tf_path) as ds_tf:
        shape = ds_tf.shape
        h, w = shape
        ref_transform = ds_tf.transform

        def _rd(b: int, nm: str) -> np.ndarray:
            raw = ds_tf.read(b)
            sentinel_counts[f"B{b:02d}_{nm}"] = int(((~np.isfinite(raw)) | (np.abs(raw) >= 1.0e20))[fp_mask].sum())
            filled, _ = clean_sentinel_edt(raw, fp_mask)
            return filled

        # --- Stage 1: Gravity Marussi Tensor +RTP Marussi Tensor + Gallardo-Meju + Salem B02 ---
        b13_grav = _rd(13, "iso_grav_anom")
        b18_ghg = _rd(18, "iso_grav_anom_hg")
        mg = marussi_tensor_invariants(b13_grav, lambda_min_px=6.0, lambda_max_px=260.0, return_strike=True)
        grav_step_2d = (mg["d2d"] * np.sqrt(np.maximum(mg["hg"], 0.0) * np.maximum(b18_ghg, 0.0) + 1e-8)).astype(np.float32)
        del b18_ghg
        X[:, 0] = pct_fp(grav_step_2d.ravel()[fp_lin])

        b02_rtp = _rd(2, "rtp")
        mm = marussi_tensor_invariants(b02_rtp, lambda_min_px=5.0, lambda_max_px=180.0, return_strike=False)
        X[:, 1] = pct_fp((mm["d2d"] * mm["hg"]).ravel()[fp_lin])

        dot_gm = np.abs(mg["txz"] * mm["txz"] + mg["tyz"] * mm["tyz"])
        cross_gm = np.abs(mg["txz"] * mm["tyz"] - mg["tyz"] * mm["txz"])
        denom_gm = mg["hg"] * mm["hg"] + np.float32(1e-8)
        X[:, 4] = pct_fp(((dot_gm / denom_gm) * np.sqrt(denom_gm) * np.sqrt(mg["d2d"] * mm["d2d"])).ravel()[fp_lin])
        del dot_gm, mm
        gc.collect()

        rtp_trough = np.maximum(
            ndi.gaussian_filter(b02_rtp, sigma=22.0) - ndi.gaussian_filter(b02_rtp, sigma=2.5),
            np.float32(0.0),
        )
        X[:, 5] = pct_fp((grav_step_2d * rtp_trough * (1.0 - 0.5 * (cross_gm / denom_gm))).ravel()[fp_lin])
        del rtp_trough, cross_gm, denom_gm

        X[:, 6] = pct_fp(salem_true_rtp_tilt_depth_gate(b02_rtp, smooth_px=2.0).ravel()[fp_lin])
        del b02_rtp
        gc.collect()

        # --- Stage 2: Allmendinger Trishear Blind Monocline + Cooper Terracing + 1D Crest ---
        b15_base = _rd(15, "depth_to_base_surf")
        b12_det_elev = _rd(12, "det_elev")
        b19_eslope = _rd(19, "det_elev_slope")

        terr_g = cooper_terracing_gradient(b13_grav, sigma_px=2.8, n_iter=3)
        del b13_grav
        terr_b = cooper_terracing_gradient(np.log1p(np.maximum(b15_base, 0.0)), sigma_px=2.8, n_iter=3)
        terr_joint = mg["d2d"] * (
            0.60 * terr_g / (float(np.std(terr_g)) + 1e-6) + 0.40 * terr_b / (float(np.std(terr_b)) + 1e-6)
        )
        X[:, 3] = pct_fp(terr_joint.ravel()[fp_lin])
        del terr_g, terr_b, terr_joint
        gc.collect()

        with rasterio.open(topo10_path) as ds_t10:
            slp10_max, _ = _dequant_u8(ds_t10, 2)
            asp_coh, _ = _dequant_u8(ds_t10, 7)
            dem10, ok_dem = _dequant_u8(ds_t10, 9)
        dem_clean, _ = clean_sentinel_edt(np.where(ok_dem, dem10, b12_det_elev), fp_mask)
        del dem10, ok_dem, b12_det_elev
        mono_band = (ndi.gaussian_filter(dem_clean, sigma=7.0) - ndi.gaussian_filter(dem_clean, sigma=20.0)).astype(np.float32)
        del dem_clean
        mono_inflect = _grad_mag_f32(mono_band)
        del mono_band

        hg_n = np.maximum(mg["hg"], np.float32(1e-6))
        ux_fw = (mg["txz"] / hg_n).astype(np.float32)
        uy_fw = (mg["tyz"] / hg_n).astype(np.float32)
        del hg_n
        mono_updip = _shift_field_along_vec(mono_inflect, ux_fw, uy_fw, step_px=5.0)
        del ux_fw, uy_fw

        cover_blind_gate = np.clip((b15_base - np.float32(40.0)) / np.float32(180.0), 0.05, 1.0).astype(np.float32)
        canyon_pen = np.exp(
            -0.5 * (np.maximum(slp10_max - np.float32(10.0), 0.0) / np.float32(8.0)) ** 2
            * np.clip(1.0 - b15_base / np.float32(50.0), 0.0, 1.0)
        ).astype(np.float32)
        trishear_blind = grav_step_2d * (0.40 * mono_inflect + 0.60 * mono_updip) * cover_blind_gate * canyon_pen
        X[:, 2] = pct_fp(trishear_blind.ravel()[fp_lin])
        del mono_inflect, mono_updip, cover_blind_gate, trishear_blind

        v_s10 = slp10_max.ravel()[fp_lin]
        v_s100 = b19_eslope.ravel()[fp_lin]
        beta_slp = np.float32(float(np.cov(v_s10, v_s100)[0, 1] / max(np.var(v_s100), 1e-6)))
        scarp_res = (np.maximum(slp10_max - beta_slp * b19_eslope, 0.0) * asp_coh * canyon_pen).astype(np.float32)
        del asp_coh, b19_eslope, b15_base
        base_crest_in = (
            0.55 * (grav_step_2d / np.float32(float(np.std(grav_step_2d)) + 1e-6))
            + 0.45 * (scarp_res / np.float32(float(np.std(scarp_res)) + 1e-6))
        ).astype(np.float32)
        del scarp_res, grav_step_2d
        crest_1d = directional_ridge_response(base_crest_in, mg["cos_2psi"], mg["sin_2psi"])
        X[:, 9] = pct_fp(crest_1d.ravel()[fp_lin])
        del base_crest_in, crest_1d
        gc.collect()

        # --- Stage 3: Niblett-Bostick Skin-Depth & Radiometric K-Alteration ---
        b17_cond = _rd(17, "cond_surf")
        sigma_pos = np.maximum(b17_cond - np.float32(float(np.quantile(b17_cond[fp_mask], 0.01))), 0.0) + np.float32(1e-3)
        del b17_cond
        skin_log = ndi.gaussian_filter((-0.5 * np.log(sigma_pos)).astype(np.float32), sigma=2.5)
        del sigma_pos
        skin_grad = _grad_mag_f32(skin_log)
        del skin_log
        playa_flat_pen = (0.35 + 0.65 * np.clip(slp10_max / np.float32(2.5), 0.0, 1.0)).astype(np.float32)
        del slp10_max
        X[:, 7] = pct_fp((skin_grad * (0.45 + 0.55 * mg["d2d"]) * playa_flat_pen).ravel()[fp_lin])
        del skin_grad, playa_flat_pen

        b06_tc_rad = _rd(6, "tc_radiometric_not_tilt")
        with rasterio.open(ext_path) as ds_ext:
            thk_u8 = ds_ext.read(1).astype(np.float32)
            uk_u8 = ds_ext.read(2).astype(np.float32)
            ok_ext = (thk_u8 > 0) & fp_mask
        k_enrich = np.where(ok_ext, (255.0 - thk_u8) / 255.0 + 0.35 * (uk_u8 / 255.0), 0.0).astype(np.float32)
        del thk_u8, uk_u8, ok_ext
        tc_grad = _grad_mag_f32(ndi.gaussian_filter(b06_tc_rad, sigma=2.5).astype(np.float32))
        rad_step = k_enrich * (0.4 + 0.6 * mg["d2d"]) + 0.25 * tc_grad / np.float32(float(np.std(b06_tc_rad)) + 1e-6)
        X[:, 8] = pct_fp((rad_step * canyon_pen).ravel()[fp_lin])
        del b06_tc_rad, k_enrich, tc_grad, rad_step, canyon_pen
        gc.collect()

        # --- Stage 4: H-92M2 Walker Lane Kinematic Vorticity & Strain Locking ---
        b04_geod2 = _rd(4, "geod_2ndinv")
        b07_shear = _rd(7, "geod_shearrate")
        b08_dilat = _rd(8, "geod_dilaterate")
        b10_deq = _rd(10, "deq_n100a15")
        b16_ieq = _rd(16, "ieq_n100a15")

    shear_pos = np.maximum(b07_shear, np.float32(0.0))
    dilat_abs = np.abs(b08_dilat)
    eps_w = np.float32(float(np.quantile(shear_pos[fp_mask], 0.20)) * 0.25 + 1e-6)
    wk = (shear_pos / np.sqrt(shear_pos * shear_pos + dilat_abs * dilat_abs + eps_w * eps_w)).astype(np.float32)
    strain_mag = pct_fp(b04_geod2.ravel()[fp_lin])
    del b04_geod2, dilat_abs
    X[:, 10] = pct_fp(wk.ravel()[fp_lin] * (0.35 + 0.65 * strain_mag))
    del strain_mag

    def _cos2_align(deg_cw_north: float) -> np.ndarray:
        a2 = np.deg2rad(2.0 * deg_cw_north)
        return np.clip(
            0.5 * (1.0 + mg["cos_2psi"] * np.float32(np.cos(a2)) + mg["sin_2psi"] * np.float32(np.sin(a2))),
            0.0,
            1.0,
        ).astype(np.float32)

    s_vort = ((1.0 - wk) * _cos2_align(22.0) + wk * np.maximum(_cos2_align(62.0), _cos2_align(142.0))) * mg["d2d"]
    X[:, 11] = pct_fp((s_vort * np.sqrt(np.maximum(mg["hg"], 0.0))).ravel()[fp_lin])
    del s_vort

    strain_grad = _grad_mag_f32(ndi.gaussian_filter(shear_pos, sigma=4.0)) + np.float32(0.7) * _grad_mag_f32(
        ndi.gaussian_filter(b08_dilat, sigma=4.0)
    )
    del b07_shear, b08_dilat, shear_pos
    lock_factor = (
        np.clip(1.0 - 0.55 * (b16_ieq / np.float32(float(np.quantile(b16_ieq[fp_mask], 0.95)) + 1e-6)), 0.25, 1.0)
        * np.exp(-0.5 * (np.maximum(b10_deq - np.float32(35.0), 0.0) / np.float32(45.0)) ** 2)
    ).astype(np.float32)
    del b10_deq, b16_ieq
    X[:, 12] = pct_fp((strain_grad * lock_factor * (0.4 + 0.6 * mg["d2d"])).ravel()[fp_lin])
    del strain_grad, lock_factor
    gc.collect()

    # --- Stage 5: Clean Fournier Enthalpy Disequilibrium + 2m Probe Upflow ---
    diseq_halo, gdr_meta = _load_fournier_diseq_grid(ws_csv, probe_zip, ref_transform, shape, fp_mask)
    ts_2d = np.zeros(h * w, dtype=np.float32)
    ts_2d[fp_lin] = 0.55 * X[:, 2] + 0.45 * X[:, 7]
    upflow_conduit = diseq_halo * (0.25 + 0.75 * ts_2d.reshape(h, w))
    X[:, 13] = pct_fp(upflow_conduit.ravel()[fp_lin])
    del diseq_halo, ts_2d, upflow_conduit

    aux = {
        "cos_2psi_T": mg["cos_2psi"].ravel()[fp_lin].astype(np.float32),
        "sin_2psi_T": mg["sin_2psi"].ravel()[fp_lin].astype(np.float32),
        "wk": wk.ravel()[fp_lin].astype(np.float32),
    }
    del mg, wk
    gc.collect()

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        cache_path,
        X_fp=X,
        feature_names=np.array(FEATURE_NAMES),
        cos_2psi_T=aux["cos_2psi_T"],
        sin_2psi_T=aux["sin_2psi_T"],
        wk=aux["wk"],
    )
    meta = {
        "cached": False,
        "path": str(cache_path),
        "shape": list(shape),
        "n_footprint": int(n_fp),
        "n_features": len(FEATURE_NAMES),
        "sentinel_pixels_cleaned_inside_footprint": sentinel_counts,
        "band6_tc_used_as_magnetic_tilt": False,
        "gdr_wellspring_hygiene": gdr_meta,
    }
    return X, aux, meta
