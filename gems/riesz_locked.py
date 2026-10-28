"""RIESZ-LOCKED-PHYSLBM lane: 4 untried Basin-and-Range geological feature families.

Pre-registered in ``docs/HYPOTHESES_20261028_RIESZ_LOCKED.md`` (2026-10-28):
  H-92A (RIESZ-PIEDMONT): Multi-octave 2D Riesz monogenic odd-step phase congruency
         (Felsberg & Sommer 2001; Kovesi 1999) on B13 gravity, B2 RTP, and B15
         depth-to-basement + range-relief-deconfounded USGS 3DEP 10 m piedmont scarp.
  H-92B (WIJNS-BIHARMONIC): Dimensionally exact 2D-FFT Wijns et al. (2005) 3D
         analytic-signal cos(theta) = |grad_H u| / sqrt(|grad_H u|^2 + (d_z u)^2 + eps^2)
         on B13 gravity and B2 RTP + broken-elastic-plate flexural biharmonic couple
         |grad(laplacian(z_base) - l_f^2 biharmonic(z_base))|.
  H-92C (LOCKED-DEFICIT): Interseismic GPS shear/dilational strain accumulation
         with low contemporary microseismicity release (locked moment-deficit index)
         coupled to USGS 3DEP 10 m fluvial chi-step / k_sn knickzones.
  H-92D (PECLETVENT): Fournier (1977) chemical-minus-measured enthalpy disequilibrium
         dT_diseq = max(0, max(T_quartz, T_chalc, T_cat) - T_meas) from GDR #1391
         (strictly stripping thermalclass and dist_known_fault_px) + 2 m temperature
         probe anomaly (F2mDAB) inside smectite clay-cap & Grauch magnetite-destruction
         seals projected onto Riesz/Wijns structural step conduits.

Zero catalogue labels, zero H19-5, and zero SGMC inputs enter any of the 16 features.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from scipy import ndimage as ndi
from scipy.stats import rankdata

from gems.ventscarp import _rasterize_2m_temperature_probes

FEATURE_NAMES: tuple[str, ...] = (
    # H-92A: Riesz monogenic step-phase congruency & deconfounded 10m piedmont scarp
    "f01_riesz_grav_step",
    "f02_riesz_rtp_step",
    "f03_riesz_base_step",
    "f04_riesz_joint_strike_coh",
    "f05_scarp10m_deconf",
    "f06_curv10m_lineament_pied",
    # H-92B: Wijns 3D analytic-signal cos(theta) & broken-plate biharmonic flexure
    "f07_wijns_cos_theta_grav",
    "f08_wijns_cos_theta_mag",
    "f09_biharmonic_base_dipole",
    "f10_wijns_flex_couple",
    # H-92C: Interseismic locked strain-deficit & 10m fluvial chi/ksn knickzones
    "f11_locked_strain_deficit",
    "f12_chi10m_knick_steep",
    "f13_locked_knick_riesz",
    # H-92D: Fournier enthalpy-disequilibrium blind geothermal Peclet conduit
    "f14_fournier_diseq_halo",
    "f15_claycap_grauch_seal",
    "f16_peclet_blind_conduit",
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = ROOT / ".cache" / "riesz_locked" / "features_fp_v1.npz"


def _clean_edt_fill(arr: np.ndarray, valid_extra: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Mask non-finite and <= -1e30 sentinels and fill invalid cells by nearest neighbor.

    Nearest-neighbor EDT continuation eliminates artificial step jumps at the irregular
    competition footprint boundary and interior sentinel pixels before 2D FFT operators.
    """
    x = np.asarray(arr, dtype=np.float32)
    ok = np.isfinite(x) & (x > -1.0e30)
    if valid_extra is not None:
        ok &= valid_extra
    if not ok.all():
        ind = ndi.distance_transform_edt(~ok, return_distances=False, return_indices=True)
        filled = x[tuple(ind)].astype(np.float32, copy=False)
    else:
        filled = x.copy()
    return filled, ok


def _pct_fp(vec_fp: np.ndarray) -> np.ndarray:
    """Map a 1D footprint vector to uniform [0, 1] empirical percentiles."""
    v = np.asarray(vec_fp, dtype=np.float64)
    v = np.where(np.isfinite(v), v, np.nanmedian(v))
    r = rankdata(v, method="average")
    return ((r - 0.5) / max(v.size, 1)).astype(np.float32)


def _wavenumber_grid(shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """2D rfft2 angular wavenumber grids (kx, ky, k_rad) in radians / pixel (1 px = 100 m)."""
    h, w = shape
    ky = (2.0 * np.pi * np.fft.fftfreq(h)).astype(np.float32)[:, None]
    kx = (2.0 * np.pi * np.fft.rfftfreq(w)).astype(np.float32)[None, :]
    kr = np.hypot(kx, ky).astype(np.float32)
    return kx, ky, kr


def riesz_step_congruency(
    field_filled: np.ndarray,
    wavelengths_px: tuple[float, ...] = (4.0, 8.0, 16.0, 32.0),
    sigma_on_f: float = 0.55,
    noise_q: float = 0.55,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Multi-octave 2D Riesz monogenic odd-step phase congruency (Felsberg & Sommer 2001).

    Across log-Gabor octaves, odd antisymmetric step offsets have local phase
    phi = +-pi/2 (||R u_s|| >> |u_s|), whereas symmetric dykes/plutons/ridges have
    phi in {0, pi} (|u_s| >> ||R u_s||). Returns (pc_step in [0, 1], cos_2psi, sin_2psi)
    where 2*psi encodes axial strike orientation without pi-wrap discontinuity.
    """
    h, w = field_filled.shape
    kx, ky, kr = _wavenumber_grid((h, w))
    inv_kr = np.where(kr > 0.0, 1.0 / np.maximum(kr, 1e-12), 0.0).astype(np.float32)
    rx_mul = (-1j * kx * inv_kr).astype(np.complex64)
    ry_mul = (-1j * ky * inv_kr).astype(np.complex64)

    u0 = field_filled - np.float32(np.mean(field_filled))
    fhat = np.fft.rfft2(u0).astype(np.complex64)

    sum_amp = np.zeros((h, w), dtype=np.float32)
    sum_odd_minus_even = np.zeros((h, w), dtype=np.float32)
    sum_c2 = np.zeros((h, w), dtype=np.float32)
    sum_s2 = np.zeros((h, w), dtype=np.float32)
    log_sig2 = 2.0 * (np.log(sigma_on_f) ** 2)
    noise_thresh = 0.0

    for idx, lam in enumerate(wavelengths_px):
        k0 = float(2.0 * np.pi / lam)
        lg = np.zeros_like(kr, dtype=np.float32)
        pos = kr > 0.0
        lg[pos] = np.exp(-((np.log(kr[pos] / k0)) ** 2) / log_sig2).astype(np.float32)
        bhat = fhat * lg
        even = np.fft.irfft2(bhat, s=(h, w)).astype(np.float32)
        odd_x = np.fft.irfft2(bhat * rx_mul, s=(h, w)).astype(np.float32)
        odd_y = np.fft.irfft2(bhat * ry_mul, s=(h, w)).astype(np.float32)
        odd_mag = np.hypot(odd_x, odd_y)
        amp = np.hypot(even, odd_mag)
        if idx == 0:
            noise_thresh = float(np.quantile(amp, noise_q)) * 1.35
        sum_amp += amp
        sum_odd_minus_even += odd_mag - np.abs(even)
        # Double-angle step-normal vector weighted by odd step energy
        denom = np.maximum(odd_mag * odd_mag, 1e-12)
        sum_c2 += odd_mag * (odd_x * odd_x - odd_y * odd_y) / denom
        sum_s2 += odd_mag * (2.0 * odd_x * odd_y) / denom

    eps0 = float(np.quantile(sum_amp, 0.25)) * 0.25 + 1e-6
    pc = np.clip((sum_odd_minus_even - noise_thresh) / (sum_amp + eps0), 0.0, 1.0).astype(np.float32)
    norm2 = np.maximum(np.hypot(sum_c2, sum_s2), 1e-6)
    return pc, (sum_c2 / norm2).astype(np.float32), (sum_s2 / norm2).astype(np.float32)


def wijns_cos_theta_harmonic(
    field_filled: np.ndarray,
    smooth_px: float = 1.5,
    eps_quantile: float = 0.15,
) -> np.ndarray:
    """Dimensionally exact Wijns et al. (2005) cos(theta) via 2D-FFT harmonic 1VD.

    Computes horizontal gradient (df/dx, df/dy) and upward-harmonic vertical derivative
    df/dz = F^-1(|k| F(f)) in identical physical units per pixel, avoiding cross-band
    unit mismatches (e.g. B03 in nT/km vs B09 in nT/m).
    """
    h, w = field_filled.shape
    kx, ky, kr = _wavenumber_grid((h, w))
    taper = np.exp(-0.5 * (smooth_px ** 2) * (kr ** 2)).astype(np.float32)
    fhat = np.fft.rfft2(field_filled - np.float32(np.mean(field_filled))).astype(np.complex64) * taper
    gx = np.fft.irfft2((1j * kx).astype(np.complex64) * fhat, s=(h, w)).astype(np.float32)
    gy = np.fft.irfft2((1j * ky).astype(np.complex64) * fhat, s=(h, w)).astype(np.float32)
    gz = np.fft.irfft2(kr.astype(np.complex64) * fhat, s=(h, w)).astype(np.float32)
    gh = np.hypot(gx, gy)
    as3 = np.sqrt(gh * gh + gz * gz)
    eps = float(np.quantile(as3, eps_quantile)) * 0.35 + 1e-6
    return np.clip(gh / np.sqrt(gh * gh + gz * gz + eps * eps), 0.0, 1.0).astype(np.float32)


def biharmonic_flexural_dipole(
    z_base_filled: np.ndarray,
    flex_scale_px: float = 20.0,
    smooth_px: float = 3.0,
) -> np.ndarray:
    """Thin-plate elastic flexural load couple |grad(lap(z) - l_f^2 biharmonic(z))|."""
    h, w = z_base_filled.shape
    kx, ky, kr = _wavenumber_grid((h, w))
    taper = np.exp(-0.5 * (smooth_px ** 2) * (kr ** 2)).astype(np.float32)
    k2 = kr * kr
    # Spectral operator for -(laplacian - l_f^2 biharmonic) = k^2 + (l_f_norm * k)^4
    lf_eff = float(1.0 / max(flex_scale_px, 1.0))
    op = (k2 + ( k2 * k2 ) / max(lf_eff * lf_eff, 1e-6)) * taper
    fhat = np.fft.rfft2(z_base_filled - np.float32(np.mean(z_base_filled))).astype(np.complex64) * op
    bx = np.fft.irfft2((1j * kx).astype(np.complex64) * fhat, s=(h, w)).astype(np.float32)
    by = np.fft.irfft2((1j * ky).astype(np.complex64) * fhat, s=(h, w)).astype(np.float32)
    return np.hypot(bx, by).astype(np.float32)


def _dequant_u8(ds: rasterio.DatasetReader, band: int) -> tuple[np.ndarray, np.ndarray]:
    q = ds.read(band)
    tags = ds.tags(band)
    lo = float(tags.get("q_lo", 0.0))
    hi = float(tags.get("q_hi", 1.0))
    ok = q > 0
    val = np.where(ok, lo + (q.astype(np.float32) - 1.0) / 254.0 * (hi - lo), 0.0).astype(np.float32)
    return val, ok


def _load_fournier_diseq_grid(
    wellspring_csv: Path,
    probe_2m_zip: Path,
    ref_transform: rasterio.Affine,
    shape: tuple[int, int],
    foot_mask: np.ndarray,
) -> tuple[np.ndarray, dict]:
    """Rasterize Fournier enthalpy disequilibrium dT = max(T_chem) - T_meas + 2m probe DAB.

    Strictly drops ``thermalclass`` and ``dist_known_fault_px`` before reading values.
    """
    raw = pd.read_csv(
        wellspring_csv,
        usecols=["row", "col", "temp_c", "geothermquartz_c", "geothermchalc_c", "geothermcat_c"],
    )
    assert "thermalclass" not in raw.columns and "dist_known_fault_px" not in raw.columns
    rows = pd.to_numeric(raw["row"], errors="coerce").fillna(-1).astype(int).to_numpy()
    cols = pd.to_numeric(raw["col"], errors="coerce").fillna(-1).astype(int).to_numpy()
    t_meas = pd.to_numeric(raw["temp_c"], errors="coerce").fillna(15.0).to_numpy(dtype=np.float32)
    t_qtz = pd.to_numeric(raw["geothermquartz_c"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)
    t_chl = pd.to_numeric(raw["geothermchalc_c"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)
    t_cat = pd.to_numeric(raw["geothermcat_c"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)
    t_chem = np.maximum.reduce([t_qtz, t_chl, t_cat])
    # Enthalpy disequilibrium specifically highlights cooled blind outflows (high T_chem, modest T_meas)
    diseq = np.clip(t_chem - np.clip(t_meas, 5.0, 120.0), 0.0, 180.0)

    h, w = shape
    imp = np.zeros((h, w), dtype=np.float32)
    in_b = (rows >= 0) & (rows < h) & (cols >= 0) & (cols < w) & (diseq > 15.0)
    for r, c, dv in zip(rows[in_b], cols[in_b], diseq[in_b]):
        if foot_mask[r, c] and dv > imp[r, c]:
            imp[r, c] = float(dv / 120.0)

    probe_imp, probe_stats = _rasterize_2m_temperature_probes(probe_2m_zip, ref_transform, shape, foot_mask)
    combined_src = imp + 0.85 * np.clip(probe_imp, 0.0, 2.5)
    # 2.5 km Darcy lateral outflow kernel + 0.8 km near-vent kernel
    halo = 0.65 * ndi.gaussian_filter(combined_src, sigma=25.0) + 0.35 * ndi.gaussian_filter(combined_src, sigma=8.0)
    meta = {
        "n_diseq_wells_gt15c": int(in_b.sum()),
        "n_2m_probes_in_footprint": int(probe_stats.get("in_footprint", 0)),
        "n_2m_probes_anomalous_ge_1_2c": int(probe_stats.get("anomalous_ge_threshold", 0)),
        "stripped_columns": ["thermalclass", "dist_known_fault_px"],
    }
    return halo.astype(np.float32), meta


def compute_or_load_features(
    fp_lin: np.ndarray,
    fp_mask: np.ndarray,
    *,
    cache_path: Path = DEFAULT_CACHE,
    force: bool = False,
) -> tuple[np.ndarray, dict]:
    """Return ``(X_fp, meta)`` where ``X_fp`` has shape ``(fp.n, 16)`` in ``[0, 1]`` float32."""
    if cache_path.exists() and not force:
        z = np.load(cache_path, allow_pickle=False)
        names = tuple(str(s) for s in z["feature_names"])
        if names == FEATURE_NAMES and z["X_fp"].shape == (fp_lin.size, len(FEATURE_NAMES)):
            return z["X_fp"].astype(np.float32), {"cached": True, "path": str(cache_path)}

    tf_path = ROOT / ".cache" / "gems_inputs" / "training_features.tif"
    topo10_path = ROOT / ".cache" / "gems_inputs" / "external" / "topo_10m_derived_100m_u8.tif"
    chi10_path = ROOT / ".cache" / "gems_inputs" / "external" / "dem10_chi_100m_i16.tif"
    ext_path = ROOT / ".cache" / "gems_inputs" / "external" / "geodawn_extensions_u8.tif"
    ws_csv = ROOT / ".cache" / "gems_inputs" / "external" / "gdr_wellspring_in_footprint.csv"
    probe_zip = ROOT / ".cache" / "gems_inputs" / "external" / "2m_temperature_probe_INGENIOUS_regional_data.zip"

    n_fp = fp_lin.size
    X = np.empty((n_fp, len(FEATURE_NAMES)), dtype=np.float32)

    with rasterio.open(tf_path) as ds_tf:
        shape = ds_tf.shape
        ref_transform = ds_tf.transform

        # --- H-92A & H-92B potential & basement fields ---
        b13_grav, ok13 = _clean_edt_fill(ds_tf.read(13), fp_mask)
        b02_rtp, ok02 = _clean_edt_fill(ds_tf.read(2), fp_mask)
        b15_base, _ = _clean_edt_fill(ds_tf.read(15), fp_mask)
        b12_elev, _ = _clean_edt_fill(ds_tf.read(12), fp_mask)
        b19_slope, _ = _clean_edt_fill(ds_tf.read(19), fp_mask)

        pc_grav, c2g, s2g = riesz_step_congruency(b13_grav)
        pc_rtp, c2m, s2m = riesz_step_congruency(b02_rtp)
        pc_base, _, _ = riesz_step_congruency(np.log1p(np.maximum(b15_base, 0.0)))

        # Axial strike coherence: cos^2(psi_g - psi_m) = 0.5*(1 + cos(2psi_g)*cos(2psi_m) + sin(2psi_g)*sin(2psi_m))
        strike_align = np.clip(0.5 * (1.0 + c2g * c2m + s2g * s2m), 0.0, 1.0)
        joint_strike = strike_align * np.sqrt(pc_grav * pc_rtp)
        del c2g, s2g, c2m, s2m, strike_align

        X[:, 0] = _pct_fp(pc_grav.ravel()[fp_lin])
        X[:, 1] = _pct_fp(pc_rtp.ravel()[fp_lin])
        X[:, 2] = _pct_fp(pc_base.ravel()[fp_lin])
        X[:, 3] = _pct_fp(joint_strike.ravel()[fp_lin])
        del joint_strike

        # Wijns cos(theta) & broken-plate biharmonic flexure
        ct_grav = wijns_cos_theta_harmonic(b13_grav, smooth_px=1.6)
        ct_mag = wijns_cos_theta_harmonic(b02_rtp, smooth_px=1.6)
        bih_base = biharmonic_flexural_dipole(b15_base, flex_scale_px=20.0, smooth_px=3.0)
        cover_gate = np.clip(b15_base / 180.0, 0.05, 1.0)
        bih_gated = bih_base * cover_gate
        del b13_grav, ok13, ok02, bih_base

        X[:, 6] = _pct_fp(ct_grav.ravel()[fp_lin])
        X[:, 7] = _pct_fp(ct_mag.ravel()[fp_lin])
        X[:, 8] = _pct_fp(bih_gated.ravel()[fp_lin])
        X[:, 9] = _pct_fp(ct_grav.ravel()[fp_lin] * X[:, 8])
        del ct_mag, bih_gated

        # --- H-92A 10m Piedmont Scarp Deconfounded from Range-Core Relief ---
        with rasterio.open(topo10_path) as ds_t10:
            slp10_max, ok_t1 = _dequant_u8(ds_t10, 2)
            curv10, _ = _dequant_u8(ds_t10, 6)
            asp_coh, _ = _dequant_u8(ds_t10, 7)
            hs_lin, _ = _dequant_u8(ds_t10, 8)
        # Regress slp10_max on 100m det_elev_slope across valid footprint to isolate sub-pixel scarps
        v_s10 = slp10_max.ravel()[fp_lin]
        v_s100 = b19_slope.ravel()[fp_lin]
        beta_slp = float(np.cov(v_s10, v_s100)[0, 1] / max(np.var(v_s100), 1e-6))
        scarp_excess = np.maximum(slp10_max - beta_slp * b19_slope, 0.0)
        # Suppress high range cores (high positive det_elev with zero sedimentary cover)
        pied_hab = np.clip(1.15 - np.clip((b12_elev - 120.0) / 420.0, 0.0, 0.90), 0.25, 1.15) * (
            0.35 + 0.65 * np.clip(b15_base / 150.0, 0.0, 1.0)
        )
        scarp_deconf = np.where(ok_t1, scarp_excess * asp_coh * pied_hab, 0.0)
        curv_pied = np.where(ok_t1, curv10 * hs_lin * pied_hab, 0.0)
        X[:, 4] = _pct_fp(scarp_deconf.ravel()[fp_lin])
        X[:, 5] = _pct_fp(curv_pied.ravel()[fp_lin])
        del slp10_max, curv10, asp_coh, hs_lin, scarp_excess, pied_hab, scarp_deconf, curv_pied, b12_elev, b19_slope, b15_base

        # --- H-92C Interseismic Locked Strain-Deficit & 10m Chi Knickzones ---
        b07_shear, _ = _clean_edt_fill(ds_tf.read(7), fp_mask)
        b08_dilat, _ = _clean_edt_fill(ds_tf.read(8), fp_mask)
        b16_ieq, _ = _clean_edt_fill(ds_tf.read(16), fp_mask)
        strain_rate = _pct_fp((b07_shear + 0.70 * np.maximum(b08_dilat, 0.0)).ravel()[fp_lin])
        ieq_pct = _pct_fp(b16_ieq.ravel()[fp_lin])
        locked_def = strain_rate * (1.0 - 0.65 * ieq_pct)
        X[:, 10] = _pct_fp(locked_def)
        del b07_shear, b08_dilat, b16_ieq, strain_rate, ieq_pct

        with rasterio.open(chi10_path) as ds_chi:
            chi_step = ds_chi.read(1).astype(np.float32)
            ksn = ds_chi.read(3).astype(np.float32)
            ok_chi = (chi_step > -30000.0) & (ksn > -30000.0)
        knick_chan = np.where(
            ok_chi,
            np.clip(chi_step / 1200.0, 0.0, 2.5) + np.clip(ksn / 85.0, 0.0, 2.5),
            0.0,
        ).astype(np.float32)
        # Propagate channel knickzones 300 m laterally onto adjacent fault-crossing interfluves
        knick_halo = ndi.gaussian_filter(knick_chan, sigma=3.0)
        X[:, 11] = _pct_fp(knick_halo.ravel()[fp_lin])
        step_struct = np.maximum(X[:, 0], X[:, 2])
        X[:, 12] = _pct_fp(X[:, 10] * X[:, 11] * (0.30 + 0.70 * step_struct))
        del chi_step, ksn, ok_chi, knick_chan, knick_halo

        # --- H-92D Fournier Enthalpy-Disequilibrium Blind Geothermal Peclet Conduit ---
        b17_cond, _ = _clean_edt_fill(ds_tf.read(17), fp_mask)

    diseq_halo, gdr_meta = _load_fournier_diseq_grid(ws_csv, probe_zip, ref_transform, shape, fp_mask)
    X[:, 13] = _pct_fp(diseq_halo.ravel()[fp_lin])

    # Local clay-cap high-pass anomaly (suppresses broad flat evaporative playa bowls)
    cond_local = np.maximum(b17_cond - ndi.gaussian_filter(b17_cond, sigma=35.0), 0.0)
    with rasterio.open(ext_path) as ds_ext:
        thk_u8 = ds_ext.read(1).astype(np.float32)
        uth_u8 = ds_ext.read(3).astype(np.float32)
        tmi150_u8 = ds_ext.read(4).astype(np.float32)
        ok_ext = (tmi150_u8 > 0) & fp_mask
    # Local z-residual between 150m upward-continued TMI and shallow RTP (Grauch 2001 magnetite destruction)
    rtp_loc = (b02_rtp - ndi.gaussian_filter(b02_rtp, sigma=25.0)) / (
        np.sqrt(np.maximum(ndi.gaussian_filter(b02_rtp * b02_rtp, sigma=25.0) - ndi.gaussian_filter(b02_rtp, sigma=25.0) ** 2, 1.0))
    )
    t150_loc = (tmi150_u8 - ndi.gaussian_filter(tmi150_u8, sigma=25.0)) / (
        np.sqrt(np.maximum(ndi.gaussian_filter(tmi150_u8 * tmi150_u8, sigma=25.0) - ndi.gaussian_filter(tmi150_u8, sigma=25.0) ** 2, 1.0))
    )
    grauch_demag = np.where(ok_ext, np.clip(t150_loc - rtp_loc, 0.0, 4.0), 0.0)
    rad_alt = np.where(ok_ext, np.clip(uth_u8 / 255.0 - 0.35, 0.0, 1.0) + 0.5 * np.clip(0.55 - thk_u8 / 255.0, 0.0, 1.0), 0.0)
    seal_vec = (
        0.45 * _pct_fp(cond_local.ravel()[fp_lin])
        + 0.35 * _pct_fp(grauch_demag.ravel()[fp_lin])
        + 0.20 * _pct_fp(rad_alt.ravel()[fp_lin])
    )
    X[:, 14] = _pct_fp(seal_vec)
    struct_gate = np.maximum.reduce([X[:, 0], X[:, 1], X[:, 6]])
    X[:, 15] = _pct_fp(X[:, 13] * X[:, 14] * (0.25 + 0.75 * struct_gate))

    del b02_rtp, b17_cond, cond_local, thk_u8, uth_u8, tmi150_u8, rtp_loc, t150_loc, grauch_demag, rad_alt, pc_grav, pc_rtp, pc_base, ct_grav, diseq_halo

    assert np.isfinite(X).all(), "Non-finite entries in RIESZ-LOCKED feature stack"
    assert float(X.min()) >= 0.0 and float(X.max()) <= 1.0, "Feature stack outside [0, 1]"

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        cache_path,
        X_fp=X,
        feature_names=np.array(FEATURE_NAMES),
    )
    meta = {
        "cached": False,
        "path": str(cache_path),
        "n_footprint": int(n_fp),
        "n_features": len(FEATURE_NAMES),
        "feature_names": list(FEATURE_NAMES),
        "gdr_audit": gdr_meta,
    }
    return X, meta
