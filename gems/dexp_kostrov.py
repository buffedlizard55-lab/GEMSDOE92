"""DEXP-KOSTROV-KOENDERINK geological & geophysical fault-discovery lane (2026-10-29).

Pre-registered BEFORE implementation in ``docs/HYPOTHESES_20261029_DEXP_KOSTROV.md``.

Physical & differential-geometry architecture
---------------------------------------------
1. Fedi (2007) Multiscale Harmonic Upward-Continuation ``DEXP`` Structural-Index
   (N ~ 0) Fault-Step Selector (Geophysics 72(1): I1-I11):
   Upward-continues scalar Reduced-to-Pole magnetics (B02 ``rtp``) and isostatic
   gravity (B13 ``iso_grav_anom``) across five altitudes z in {100, 200, 400, 800,
   1600} m via exact 2D-FFT spectral continuation exp(-|k|*z) and measures the
   local log-altitude attenuation exponent tau(x,y) = -d ln ||grad_H U(z)|| / d ln z.
   Deeply rooted semi-infinite crustal fault steps satisfy homogeneity N = tau - 1 ~ 0
   (tau ~ 1), whereas shallow Tertiary basaltic lava-flow rims, sills, and plugs
   decay rapidly (N >= 1, tau >= 2).  This physically suppresses the >q85 shallow
   volcanic/canyon edge mimics shown by LBM-v2 to carry negative leaderboard weight.

2. Kostrov (1974) / Simpson (1997) Geodetic Eigen-Strain Regime Kinematics
   (JGR 102:17909-17919):
   Inverts GPS/InSAR areal dilatation rate Delta (B08 ``geod_dilaterate``), maximum
   engineering shear rate gamma_max (B07 ``geod_shearrate``), and second invariant I2
   (B04 ``geod_2ndinv``) into the continuous strain-style index
       S_style = Delta / sqrt(Delta^2 + gamma_max^2 + eps^2) in [-1, +1],
   kinematically gating two unmapped Great Basin geothermal structural styles:
   - Extensional dip-slip normal regime (S_style > 0): updip-projected (420 m into
     footwall along -grad depth_to_basement; Grauch & Cordell 1987) DEXP gravity/
     basement steps + basal piedmont toe inflections;
   - Walker Lane / Humboldt wrench-transtensional shear regime (S_style ~ 0,
     gamma_max >> |Delta|): DEXP magnetic RTP + shallow-filtered MT conductivity
     shear corridors where vertical throw and topographic scarps vanish.

3. Koenderink & van Doorn (1992) Amplitude-Invariant Differential-Geometry Shape
   Index kappa_SI & Curvedness C (Image and Vision Computing 10(8):557-564):
   Isolates cylindrical concave basal-piedmont fault-toe inflections (kappa_SI ~ -0.5)
   independently of scarp height so subtle 1-3 m Quaternary alluvial-fan scarps are
   weighted on par with 300 m bedrock cliffs, with ~1,330 m Lake Lahontan wave-cut
   shoreline notch deconfounding.

Strict zero-leakage invariant
-----------------------------
* All 12 new ``dk01..dk12`` channels (and 16 cached Riesz-Locked channels) use ZERO
  fault-catalogue arrays.
* Fold-visible network continuation channels ``cx01..cx08`` inside holdout folds are
  derived strictly from ``fold['visible']`` with exact own-component self-exclusion
  via :func:`gems.faultnet.context_fields`.
"""
from __future__ import annotations

import gc
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

from . import faultnet as fn, riesz_locked as RL

ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = ROOT / ".cache" / "dexp_kostrov_features_v1.npz"

DK_FEATURE_NAMES: tuple[str, ...] = (
    "dk01_dexp_grav_step_lock",
    "dk02_dexp_rtp_step_lock",
    "dk03_dexp_shallow_volc_reject",
    "dk04_dexp_grav_mag_vector_lock",
    "dk05_kostrov_simpson_style",
    "dk06_extensional_updip_listric",
    "dk07_walker_lane_wrench_conduit",
    "dk08_seismo_strain_slip_rate",
    "dk09_koenderink_piedmont_toe",
    "dk10_koenderink_10m_scarp_coh",
    "dk11_chi_knick_dexp_concord",
    "dk12_rad_uth_kth_mt_valve",
)

CX_FEATURE_NAMES: tuple[str, ...] = (
    "cx01_logdist_other",
    "cx02_dens10_other",
    "cx03_dens40_other",
    "cx04_strike_align_other",
    "cx05_logtip_other",
    "cx06_tip_propagation_halo",
    "cx07_relay_stepover_collar",
    "cx08_wrench_tip_interaction",
)


def clean_band_2d(arr: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Clean NaNs, Infs, and interior -3.4028e38 sentinels (IR-92-FINITE-NODATA-SENTINEL)."""
    a = np.asarray(arr, dtype=np.float32)
    v = np.asarray(valid, dtype=bool)
    good = v & np.isfinite(a) & (np.abs(a) < 1e20)
    med = float(np.median(a[good])) if np.any(good) else 0.0
    out = np.where(good, a, med).astype(np.float32)
    # Smooth exterior gently from boundary median to avoid artificial step at footprint edge
    out[~v] = med
    return out


def _robust_z_pos(field_2d: np.ndarray, valid: np.ndarray, clip_hi: float = 6.0) -> np.ndarray:
    vals = field_2d[valid]
    med = float(np.median(vals))
    iqr = max(float(np.quantile(vals, 0.75) - np.quantile(vals, 0.25)), 1e-6)
    z = np.clip((field_2d - med) / iqr, -3.0, clip_hi).astype(np.float32)
    z[~valid] = 0.0
    return z


def fedi_dexp_step_features(
    field_2d: np.ndarray,
    valid: np.ndarray,
    altitudes_px: tuple[float, ...] = (1.0, 2.0, 4.0, 8.0, 16.0),
    target_n: float = 0.15,
    sigma_n: float = 0.70,
    pad: int = 64,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute Fedi (2007) multiscale upward-continued DEXP structural-index features.

    Returns (step_lock, shallow_decay, gx_z3, gy_z3, gmod_z3) as float32 2-D arrays.
    """
    h, w = field_2d.shape
    f_clean = clean_band_2d(field_2d, valid)
    # Remove regional bilinear trend before reflection-padded harmonic continuation
    reg = ndi.gaussian_filter(f_clean, sigma=48.0, mode="reflect")
    f_hp = (f_clean - reg).astype(np.float32)
    del reg

    fp_pad = np.pad(f_hp, ((pad, pad), (pad, pad)), mode="reflect")
    hp, wp = fp_pad.shape
    ky = (2.0 * np.pi * np.fft.fftfreq(hp)).astype(np.float32)[:, None]
    kx = (2.0 * np.pi * np.fft.rfftfreq(wp)).astype(np.float32)[None, :]
    kk = np.hypot(ky, kx).astype(np.float32)
    F0 = np.fft.rfft2(fp_pad).astype(np.complex64)
    del fp_pad, f_hp

    ln_z = np.log(np.asarray(altitudes_px, dtype=np.float32))
    ln_z_c = ln_z - float(ln_z.mean())
    denom = float(np.sum(ln_z_c**2))

    sum_w_ln_g = np.zeros((h, w), dtype=np.float32)
    g_z1 = None
    g_z2 = None
    g_z8 = None

    for idx, z_px in enumerate(altitudes_px):
        att = np.exp(-kk * float(z_px)).astype(np.float32)
        gx = np.fft.irfft2(F0 * (1j * kx * att), s=(hp, wp))[pad : pad + h, pad : pad + w].astype(np.float32)
        gy = np.fft.irfft2(F0 * (1j * ky * att), s=(hp, wp))[pad : pad + h, pad : pad + w].astype(np.float32)
        gm = np.hypot(gx, gy)
        eps = max(float(np.quantile(gm[valid], 0.15)) * 0.25, 1e-6)
        ln_g = np.log(gm + eps).astype(np.float32)
        sum_w_ln_g += float(ln_z_c[idx]) * ln_g
        if idx == 0:
            g_z1 = ln_g
        elif idx == 1:
            g_z2 = gm
        elif idx == 3:
            g_z8 = ln_g
        del gx, gy, gm, ln_g

    # Also compute z = 3.0 px (300 m) vector gradient for cross-field Poisson lock
    att3 = np.exp(-kk * 3.0).astype(np.float32)
    gx_3 = np.fft.irfft2(F0 * (1j * kx * att3), s=(hp, wp))[pad : pad + h, pad : pad + w].astype(np.float32)
    gy_3 = np.fft.irfft2(F0 * (1j * ky * att3), s=(hp, wp))[pad : pad + h, pad : pad + w].astype(np.float32)
    gm_3 = np.hypot(gx_3, gy_3).astype(np.float32)
    del F0, ky, kx, kk, att3

    tau = (-sum_w_ln_g / denom).astype(np.float32)
    struct_n = np.clip(tau - 1.0, -1.0, 4.0)
    n_weight = np.exp(-0.5 * ((struct_n - float(target_n)) / float(sigma_n)) ** 2).astype(np.float32)

    q90 = max(float(np.quantile(g_z2[valid], 0.90)), 1e-6)
    amp_norm = np.tanh(g_z2 / q90).astype(np.float32)
    step_lock = (amp_norm * n_weight).astype(np.float32)
    step_lock[~valid] = 0.0

    shallow_decay = np.clip(g_z1 - g_z8, 0.0, 6.0).astype(np.float32)
    shallow_decay[~valid] = 0.0
    gx_3[~valid] = 0.0
    gy_3[~valid] = 0.0
    gm_3[~valid] = 0.0
    return step_lock, shallow_decay, gx_3, gy_3, gm_3


def kostrov_simpson_strain_regime(
    dilate_2d: np.ndarray,
    shear_2d: np.ndarray,
    inv2_2d: np.ndarray,
    valid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Invert GPS/InSAR strain invariants into Simpson (1997) strain-style parameter."""
    dil = clean_band_2d(dilate_2d, valid)
    shr = np.maximum(clean_band_2d(shear_2d, valid), 0.0)
    inv2 = np.maximum(clean_band_2d(inv2_2d, valid), 0.0)

    eps0 = max(float(np.quantile(np.hypot(dil[valid], shr[valid]), 0.15)), 1e-6)
    s_style = (dil / np.sqrt(dil * dil + shr * shr + eps0 * eps0)).astype(np.float32)
    s_style[~valid] = 0.0

    med_i2 = max(float(np.median(inv2[valid])), 1e-6)
    med_sh = max(float(np.median(shr[valid])), 1e-6)
    strain_mag = np.log1p(inv2 / med_i2).astype(np.float32)

    w_ext = (np.clip(0.5 + 0.5 * s_style, 0.0, 1.0) * np.where(dil > -0.25 * eps0, 1.0, 0.25) * strain_mag).astype(
        np.float32
    )
    w_wrench = ((1.0 - np.abs(s_style)) * np.log1p(shr / med_sh)).astype(np.float32)
    w_ext[~valid] = 0.0
    w_wrench[~valid] = 0.0
    return s_style, w_ext, w_wrench


def koenderink_shape_and_curvedness(
    elev_2d: np.ndarray,
    valid: np.ndarray,
    sigma: float = 2.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Koenderink & van Doorn (1992) amplitude-invariant Shape Index & Curvedness."""
    z = clean_band_2d(elev_2d, valid)
    hxx = ndi.gaussian_filter(z, sigma=sigma, order=(0, 2), mode="reflect")
    hyy = ndi.gaussian_filter(z, sigma=sigma, order=(2, 0), mode="reflect")
    hxy = ndi.gaussian_filter(z, sigma=sigma, order=(1, 1), mode="reflect")
    tr = hxx + hyy
    disc = np.sqrt(np.maximum((hxx - hyy) ** 2 + 4.0 * hxy * hxy, 0.0))
    k1 = 0.5 * (tr + disc)
    k2 = 0.5 * (tr - disc)
    curv = np.sqrt(0.5 * (k1 * k1 + k2 * k2)).astype(np.float32)
    eps = max(float(np.quantile(disc[valid], 0.10)) * 0.2, 1e-7)
    # Note: for elevation z(x,y), concave upward basal piedmont toe has tr > 0, k1 > 0 -> SI > 0;
    # convex scarp shoulder has tr < 0 -> SI < 0.
    si = ((2.0 / np.pi) * np.arctan2(k1 + k2, k1 - k2 + eps)).astype(np.float32)
    si[~valid] = 0.0
    curv[~valid] = 0.0
    return si, curv


def directional_crest_1d(field_2d: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Soft 1-D directional ridge prominence across 4 orientations at +/-2 px."""
    f = np.where(valid, np.maximum(field_2d, 0.0), 0.0).astype(np.float32)
    s = ndi.gaussian_filter(f, sigma=0.8, mode="constant")
    prom = np.zeros_like(s)
    # 4 axes: E-W (dx=2), N-S (dy=2), NE-SW (2,-2), NW-SE (2,2)
    for dy, dx in ((0, 2), (2, 0), (2, 2), (2, -2)):
        p1 = np.roll(s, shift=(dy, dx), axis=(0, 1))
        p2 = np.roll(s, shift=(-dy, -dx), axis=(0, 1))
        diff = s - 0.5 * (p1 + p2)
        np.maximum(prom, diff, out=prom)
    # Clear 2-px boundary wrap artifact
    prom[:2, :] = 0.0
    prom[-2:, :] = 0.0
    prom[:, :2] = 0.0
    prom[:, -2:] = 0.0
    prom[~valid] = 0.0
    q95 = max(float(np.quantile(prom[valid], 0.95)), 1e-6)
    return np.clip(prom / q95, 0.0, 1.5).astype(np.float32)


def _bilinear_updip_shift(
    field_2d: np.ndarray, ny_up: np.ndarray, nx_up: np.ndarray, shift_px: float, valid: np.ndarray
) -> np.ndarray:
    """Sample ``field_2d`` at (y - shift*ny_up, x - shift*nx_up) so hanging-wall ramps project updip."""
    h, w = field_2d.shape
    yy, xx = np.indices((h, w), dtype=np.float32)
    # Subsurface ramp sits in the hanging wall (-n_updip direction from the surface trace):
    # therefore at a candidate footwall/trace pixel (y, x), we sample down-dip at (y - s*ny_up, x - s*nx_up).
    sy = np.clip(yy - float(shift_px) * ny_up, 0.0, float(h - 1.001))
    sx = np.clip(xx - float(shift_px) * nx_up, 0.0, float(w - 1.001))
    y0 = sy.astype(np.int32)
    x0 = sx.astype(np.int32)
    wy = sy - y0
    wx = sx - x0
    f = np.where(valid, field_2d, 0.0).astype(np.float32)
    out = (1.0 - wy) * ((1.0 - wx) * f[y0, x0] + wx * f[y0, x0 + 1]) + wy * (
        (1.0 - wx) * f[y0 + 1, x0] + wx * f[y0 + 1, x0 + 1]
    )
    out[~valid] = 0.0
    return out.astype(np.float32)


def _decode_u8_band(ds: rasterio.DatasetReader, band: int, valid: np.ndarray) -> np.ndarray:
    raw = ds.read(band)
    tags = ds.tags(band)
    if "q_lo" in tags and "q_hi" in tags:
        lo = float(tags["q_lo"])
        hi = float(tags["q_hi"])
        val = lo + (raw.astype(np.float32) - 1.0) / 254.0 * (hi - lo)
        good = valid & (raw > 0)
    else:
        val = raw.astype(np.float32) / 255.0
        good = valid & (raw > 0)
    med = float(np.median(val[good])) if np.any(good) else 0.0
    out = np.where(good, val, med).astype(np.float32)
    out[~valid] = med
    return out


def compute_or_load_dexp_kostrov_stack(
    fp_lin: np.ndarray, fp_mask: np.ndarray, *, force: bool = False
) -> tuple[np.ndarray, np.ndarray, list[str], dict]:
    """Compute or load the 28-feature zero-catalogue DEXP-Kostrov + Riesz stack on ``fp_lin``.

    Returns ``(X_blind_28, crest_fp, feature_names, meta)`` where ``X_blind_28`` has shape
    ``(5_167_373, 28)`` in ``float32`` and ``crest_fp`` is the composite multi-physics 1-D
    fault-trace crest weight on ``fp_lin``.
    """
    X_riesz, riesz_meta = RL.compute_or_load_features(fp_lin, fp_mask)
    riesz_names = list(RL.FEATURE_NAMES)

    if CACHE_PATH.is_file() and not force:
        with np.load(CACHE_PATH) as z:
            X_dk = z["X_dk"].astype(np.float32)
            crest_fp = z["crest_fp"].astype(np.float32)
        all_names = list(DK_FEATURE_NAMES) + riesz_names
        return np.hstack([X_dk, X_riesz]), crest_fp, all_names, {"cached": True, "riesz": riesz_meta}

    valid = np.asarray(fp_mask, dtype=bool)
    n_fp = fp_lin.size
    X_dk = np.empty((n_fp, len(DK_FEATURE_NAMES)), dtype=np.float32)

    tf_path = ROOT / ".cache" / "gems_inputs" / "training_features.tif"
    ext_path = ROOT / ".cache" / "gems_inputs" / "external" / "geodawn_extensions_u8.tif"
    topo_path = ROOT / ".cache" / "gems_inputs" / "external" / "topo_10m_derived_100m_u8.tif"
    chi_path = ROOT / ".cache" / "gems_inputs" / "external" / "dem10_chi_100m_i16.tif"

    with rasterio.open(tf_path) as tf:
        # 1. Fedi DEXP on B13 isostatic gravity & B02 RTP magnetics
        b13_grav = tf.read(13)
        dk01_grav, _, gx_g3, gy_g3, gm_g3 = fedi_dexp_step_features(b13_grav, valid, target_n=0.15, sigma_n=0.65)
        del b13_grav

        b02_rtp = tf.read(2)
        dk02_rtp, dk03_volc, gx_m3, gy_m3, gm_m3 = fedi_dexp_step_features(
            b02_rtp, valid, target_n=0.15, sigma_n=0.75
        )
        b02_clean = clean_band_2d(b02_rtp, valid)
        del b02_rtp

        # Vector Poisson gradient alignment + magnetite-destruction conduit at z=300 m
        with rasterio.open(ext_path) as eds:
            tmi_up150 = _decode_u8_band(eds, 4, valid)
            thk_u8 = _decode_u8_band(eds, 1, valid)
            uth_u8 = _decode_u8_band(eds, 3, valid)

        dot_gm = gx_g3 * gx_m3 + gy_g3 * gy_m3
        cos2_gm = (dot_gm * dot_gm) / np.maximum((gm_g3 * gm_m3) ** 2, 1e-12)
        qg = max(float(np.quantile(gm_g3[valid], 0.90)), 1e-6)
        qm = max(float(np.quantile(gm_m3[valid], 0.90)), 1e-6)
        mag_destr = np.clip(_robust_z_pos(tmi_up150, valid) - _robust_z_pos(b02_clean, valid), 0.0, 4.0)
        dk04_vec = (
            np.sqrt(np.tanh(gm_g3 / qg) * np.tanh(gm_m3 / qm)) * cos2_gm
            + 0.35 * np.tanh(gm_g3 / qg) * np.tanh(mag_destr / 2.0)
        ).astype(np.float32)
        dk04_vec[~valid] = 0.0
        del b02_clean, tmi_up150, gx_m3, gy_m3, gm_m3, dot_gm, cos2_gm, mag_destr
        gc.collect()

        X_dk[:, 0] = dk01_grav.ravel()[fp_lin]
        X_dk[:, 1] = dk02_rtp.ravel()[fp_lin]
        X_dk[:, 2] = dk03_volc.ravel()[fp_lin]
        X_dk[:, 3] = dk04_vec.ravel()[fp_lin]
        del dk03_volc, dk04_vec

        # 2. Kostrov-Simpson Strain Regime + Updip Listric vs Walker Lane Wrench Gates
        b08_dil = tf.read(8)
        b07_shr = tf.read(7)
        b04_i2 = tf.read(4)
        s_style, w_ext, w_wrench = kostrov_simpson_strain_regime(b08_dil, b07_shr, b04_i2, valid)
        del b08_dil, b07_shr

        b15_base = np.maximum(clean_band_2d(tf.read(15), valid), 0.0)
        log_b15 = np.log1p(b15_base / 25.0).astype(np.float32)
        by = ndi.gaussian_filter(log_b15, sigma=3.0, order=(1, 0), mode="reflect")
        bx = ndi.gaussian_filter(log_b15, sigma=3.0, order=(0, 1), mode="reflect")
        bn = np.hypot(by, bx) + 1e-6
        gn = gm_g3 + 1e-6
        # Footwall-directed unit normal n_updip: -grad(depth_to_base) + grad(iso_grav)
        vy = -0.55 * (by / bn) + 0.45 * (gy_g3 / gn)
        vx = -0.55 * (bx / bn) + 0.45 * (gx_g3 / gn)
        vn = np.hypot(vy, vx) + 1e-6
        ny_up = (vy / vn).astype(np.float32)
        nx_up = (vx / vn).astype(np.float32)
        del by, bx, gy_g3, gx_g3, gm_g3, vy, vx, vn

        base_step = np.tanh(bn / max(float(np.quantile(bn[valid], 0.90)), 1e-6)).astype(np.float32)
        sub_ramp = (0.60 * dk01_grav + 0.40 * base_step).astype(np.float32)
        updip_42 = _bilinear_updip_shift(sub_ramp, ny_up, nx_up, shift_px=4.2, valid=valid)
        dk06_ext_listric = (w_ext * updip_42).astype(np.float32)
        del bn, base_step, sub_ramp, ny_up, nx_up

        b17_cond = np.maximum(clean_band_2d(tf.read(17), valid), 0.0)
        log_cond = np.log1p(b17_cond * 100.0).astype(np.float32)
        cy = ndi.gaussian_filter(log_cond, sigma=2.0, order=(1, 0), mode="reflect")
        cx = ndi.gaussian_filter(log_cond, sigma=2.0, order=(0, 1), mode="reflect")
        cgrad = np.hypot(cy, cx)
        # Filter out deep flat playa smectite clays (b15 > 850 m)
        playa_filter = (1.0 / (1.0 + (b15_base / 850.0) ** 3)).astype(np.float32)
        mt_conduit = (np.tanh(cgrad / max(float(np.quantile(cgrad[valid], 0.90)), 1e-6)) * playa_filter).astype(
            np.float32
        )
        dk07_wrench = (w_wrench * (0.55 * dk02_rtp + 0.45 * mt_conduit)).astype(np.float32)
        del b17_cond, log_cond, cy, cx, cgrad, playa_filter

        b10_deq = np.maximum(clean_band_2d(tf.read(10), valid), 0.0)
        b16_ieq = np.maximum(clean_band_2d(tf.read(16), valid), 0.0)
        inv2_clean = np.maximum(clean_band_2d(b04_i2, valid), 0.0)
        med_i2 = max(float(np.median(inv2_clean[valid])), 1e-6)
        dk08_seismo = (
            np.log1p(b16_ieq / max(float(np.median(b16_ieq[valid])), 1e-6))
            / (1.0 + b10_deq / 15.0)
            * np.log1p(inv2_clean / med_i2)
        ).astype(np.float32)
        dk08_seismo[~valid] = 0.0
        del b04_i2, b10_deq, b16_ieq, inv2_clean, b15_base, log_b15, w_ext, w_wrench
        gc.collect()

        X_dk[:, 4] = s_style.ravel()[fp_lin]
        X_dk[:, 5] = dk06_ext_listric.ravel()[fp_lin]
        X_dk[:, 6] = dk07_wrench.ravel()[fp_lin]
        X_dk[:, 7] = dk08_seismo.ravel()[fp_lin]
        del s_style, dk06_ext_listric, dk08_seismo

        # 3. Koenderink Shape Index, 10m Piedmont Inflection, Chi-Knick & Radioelement Valve
        b12_det = tf.read(12)

    with rasterio.open(topo_path) as tds:
        slope_p90 = _decode_u8_band(tds, 1, valid)
        relief_loc = _decode_u8_band(tds, 5, valid)
        asp_coh = _decode_u8_band(tds, 7, valid)
        dem_mean = _decode_u8_band(tds, 9, valid)

    si_det, curv_det = koenderink_shape_and_curvedness(b12_det, valid, sigma=2.0)
    del b12_det
    qc = max(float(np.quantile(curv_det[valid], 0.75)), 1e-6)
    # Basal piedmont concave trough/inflection (si_det in [+0.20, +0.80]), deconfounded for ~1330m Lahontan shoreline
    lahontan_notch = np.exp(-0.5 * ((dem_mean - 1330.0) / 22.0) ** 2).astype(np.float32)
    dk09_pied_toe = (
        np.exp(-0.5 * ((si_det - 0.48) / 0.28) ** 2) * np.tanh(curv_det / qc) * (1.0 - 0.50 * lahontan_notch)
    ).astype(np.float32)
    dk09_pied_toe[~valid] = 0.0
    del si_det, curv_det, lahontan_notch, dem_mean

    # 10m scarp coherence deconfounded against >q90 extreme canyon-wall relief_local
    q90_rel = max(float(np.quantile(relief_loc[valid], 0.90)), 1e-6)
    canyon_pen = (1.0 / (1.0 + np.maximum(relief_loc / q90_rel - 1.0, 0.0) ** 2)).astype(np.float32)
    q90_slp = max(float(np.quantile(slope_p90[valid], 0.90)), 1e-6)
    dk10_scarp10 = (np.tanh(slope_p90 / q90_slp) * asp_coh * canyon_pen).astype(np.float32)
    dk10_scarp10[~valid] = 0.0
    del slope_p90, relief_loc, asp_coh, canyon_pen

    with rasterio.open(chi_path) as cds:
        step_max = np.maximum(cds.read(1).astype(np.float32) / 1000.0, 0.0)
        ksn_max = np.maximum(cds.read(3).astype(np.float32), 0.0)
    chi_knick = np.tanh(step_max / max(float(np.quantile(step_max[valid], 0.92)), 1e-6)) * np.tanh(
        ksn_max / max(float(np.quantile(ksn_max[valid], 0.90)), 1e-6)
    )
    dk11_chi_dexp = (chi_knick * (0.35 + 0.65 * dk01_grav)).astype(np.float32)
    dk11_chi_dexp[~valid] = 0.0
    del step_max, ksn_max, chi_knick

    # GeoDAWN K/Th (inverse of ThK) + U/Th redox-potassic alteration locked to MT conduit
    kth_alter = 1.0 - np.clip(thk_u8, 0.0, 1.0)
    dk12_rad_mt = ((0.55 * _robust_z_pos(uth_u8, valid) + 0.45 * _robust_z_pos(kth_alter, valid)) * (0.4 + 0.6 * mt_conduit)).astype(
        np.float32
    )
    dk12_rad_mt[~valid] = 0.0
    del thk_u8, uth_u8, kth_alter

    X_dk[:, 8] = dk09_pied_toe.ravel()[fp_lin]
    X_dk[:, 9] = dk10_scarp10.ravel()[fp_lin]
    X_dk[:, 10] = dk11_chi_dexp.ravel()[fp_lin]
    X_dk[:, 11] = dk12_rad_mt.ravel()[fp_lin]

    # Composite multi-physics 1-D fault-trace crest (updip DEXP grav + DEXP RTP/MT wrench + Koenderink piedmont toe + 10m scarp)
    # Deliberately balances subsurface DEXP & basal-toe crests rather than monopolizing mid-slope det_elev!
    c_updip = directional_crest_1d(updip_42, valid)
    c_wrench = directional_crest_1d(0.55 * dk02_rtp + 0.45 * mt_conduit + 0.30 * dk07_wrench, valid)
    c_pied = directional_crest_1d(0.60 * dk09_pied_toe + 0.40 * dk10_scarp10, valid)
    crest_2d = np.maximum.reduce([0.85 * c_updip, 0.85 * c_wrench, 0.80 * c_pied]).astype(np.float32)
    crest_fp = crest_2d.ravel()[fp_lin].astype(np.float32)
    del updip_42, dk01_grav, dk02_rtp, mt_conduit, dk07_wrench, dk09_pied_toe, dk10_scarp10, dk11_chi_dexp, dk12_rad_mt
    del c_updip, c_wrench, c_pied, crest_2d
    gc.collect()

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(CACHE_PATH, X_dk=X_dk, crest_fp=crest_fp)
    all_names = list(DK_FEATURE_NAMES) + riesz_names
    return np.hstack([X_dk, X_riesz]), crest_fp, all_names, {"cached": False, "riesz": riesz_meta}


def visible_network_features(
    vis_2d: np.ndarray,
    det_elev_2d: np.ndarray,
    fp_lin: np.ndarray,
    fp_mask: np.ndarray,
    s_style_fp: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute strictly fold-visible (Rule-2) own-component self-excluded context features.

    Every channel is derived solely from ``vis_2d`` (with each positive pixel's own
    8-connected component deleted via :func:`gems.faultnet.context_fields`) plus
    zero-catalogue ``det_elev_2d`` and ``s_style_fp``.
    """
    ctx_5 = fn.context_fields(vis_2d, det_elev_2d, fp_mask)  # dict or (5, H, W) — check exact return!
    d_vis = ndi.distance_transform_edt(~vis_2d).astype(np.float32)
    if isinstance(ctx_5, dict):
        c1 = ctx_5["cx_logdist"].ravel()[fp_lin]
        c2 = ctx_5["cx_dens10"].ravel()[fp_lin]
        c3 = ctx_5["cx_dens40"].ravel()[fp_lin]
        c4 = ctx_5["cx_strike"].ravel()[fp_lin]
        c5 = ctx_5["cx_logtip"].ravel()[fp_lin]
    else:
        c1 = ctx_5[0].ravel()[fp_lin]
        c2 = ctx_5[1].ravel()[fp_lin]
        c3 = ctx_5[2].ravel()[fp_lin]
        c4 = ctx_5[3].ravel()[fp_lin]
        c5 = ctx_5[4].ravel()[fp_lin]
    del ctx_5

    dist_other = np.expm1(np.maximum(c1, 0.0))
    dist_tip = np.expm1(np.maximum(c5, 0.0))
    c6_tip_halo = np.exp(-0.5 * (dist_tip / 8.0) ** 2).astype(np.float32)
    c7_relay_collar = np.exp(-0.5 * ((dist_other - 6.0) / 4.5) ** 2).astype(np.float32)
    c8_wrench_tip = (c6_tip_halo * (1.0 - np.abs(s_style_fp))).astype(np.float32)

    X_cx = np.column_stack([c1, c2, c3, c4, c5, c6_tip_halo, c7_relay_collar, c8_wrench_tip]).astype(np.float32)
    return X_cx, d_vis
