"""COULOMBDM lane surface: Two-Regime Oriented 2D Mohr-Coulomb Slip-Dilation &
Multi-Altitude Upward-Continued RTP/Gravity/MT-Clay-Cap 1D Ridge Synthesis.

Pre-registered hypothesis & equations: docs/HYPOTHESES_20261024_COULOMBDM.md.

Physical summary
----------------
1. Oriented 2D Mohr-Coulomb Transtensional Criticality (``coulomb_criticality_2d``):
   - Projects GPS/InSAR volumetric dilatation (Band 8 ``geod_dilaterate``) onto
     N18E normal-opening orientations ``cos^2(theta - 18 deg)`` and shear strain
     rate ``sqrt(Band 7 * Band 4)`` onto conjugate +/-45 deg Walker Lane (N30W) and
     Humboldt (N60E) transtensional shear orientations ``sin^2(2*(theta - 15 deg))``.
   - Both terms vanish simultaneously near ``theta = 105 deg`` (WNW-ESE, parallel to
     sigma_h,min clamping and range-perpendicular erosional canyons/fan washes).

2. Multi-Altitude FFT Upward-Continued RTP Tilt & Demagnetization (``upward_rtp_conduit``):
   - Mirror-padded 2D Fourier upward continuation ``exp(-|k|z)`` of Band 2 ``rtp``
     across ``z in {100, 300, 600 m}`` extracts crust-penetrating Miller-Singh
     vertical-contact crests (rejecting surficial volcanic float and fixing the
     Band 6 ``tc`` = Radiometric Total Count mislabelling) plus positive-Laplacian
     hydrothermal magnetite-destruction troughs.

3. Clay-Cap Lateral Edge, Radiometric Contact Gradient, Gravity Tilt & GDR (``claycap_alteration_conduit``):
   - Lateral gradient ``||grad Band 17||`` of MT electrical conductivity at smectite
     clay-cap / resistive-footwall upflow boundaries (Cumming 2009; Wannamaker et al. 2014),
     Miller-Singh isostatic gravity contact tilt from Bands 5 & 11, GeoDAWN lateral
     radiometric contact gradient ``||grad(K/(Th+1))||`` + ``||grad(U/(Th+1))||``
     (avoiding unfaulted felsic mountain-core K/U bias), and GDR #1391 surface + >=80 C
     blind chemical geothermometer plumes.

4. Rank-Calibrated Multi-Regime Synthesis + Bilinear Cross-Strike 1D NMS (``oriented_nms_1d``):
   - Unifies (i) piedmont-hinge relative monoclinal scarps, (ii) concealed thin-cover
     subsurface RTP/gravity/MT/GDR conduits, and (iii) geophysically corroborated
     range-front/relay bedrock faults along strict 1-px cross-strike Canny crests.

Strict zero-leakage invariant: no fault catalogue array enters any function in this
module. Reuses primitives from ``gems.hydroconduit`` and ``gems.breakline``.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

from .breakline import percentile_rank, spaced_top_mask
from .hydroconduit import (
    _clean_valid,
    coherence_and_strike_deg,
    cross_strike_monotonicity,
    gdr_blind_thermal_plume,
)

__all__ = [
    "coulomb_criticality_2d",
    "fft_upward_continue",
    "upward_rtp_conduit",
    "claycap_alteration_conduit",
    "oriented_nms_1d",
    "coulombdm_surface",
    "gdr_blind_thermal_plume",
    "percentile_rank",
    "spaced_top_mask",
]


def fft_upward_continue(
    field: np.ndarray,
    valid: np.ndarray,
    heights_m: tuple[float, ...] = (100.0, 300.0, 600.0),
    pixel_m: float = 100.0,
    pad_px: int = 64,
) -> dict[float, np.ndarray]:
    """Potential-field 2D Fourier upward continuation ``U(k; z) = U(k; 0) exp(-|k| z)``.

    Uses symmetric mirror padding so grid boundaries introduce zero wrap-around ringing.
    """
    if pixel_m <= 0.0:
        raise ValueError("pixel_m must be positive")
    if pad_px < 0:
        raise ValueError("pad_px must be >= 0")
    clean = _clean_valid(field, valid)
    h, w = clean.shape
    pad_y = min(int(pad_px), max(h - 1, 0))
    pad_x = min(int(pad_px), max(w - 1, 0))
    padded = np.pad(clean, ((pad_y, pad_y), (pad_x, pad_x)), mode="reflect").astype(np.float64)
    hp, wp = padded.shape

    spec = np.fft.rfft2(padded)
    ky = 2.0 * np.pi * np.fft.fftfreq(hp, d=float(pixel_m))
    kx = 2.0 * np.pi * np.fft.rfftfreq(wp, d=float(pixel_m))
    k_rad = np.hypot(ky[:, None], kx[None, :])

    out: dict[float, np.ndarray] = {}
    for z in heights_m:
        zf = float(z)
        if zf < 0.0:
            raise ValueError("upward continuation height z must be >= 0")
        att = np.exp(-zf * k_rad)
        rec = np.fft.irfft2(spec * att, s=(hp, wp))[pad_y : pad_y + h, pad_x : pad_x + w]
        out[zf] = rec.astype(np.float32)
    return out


def upward_rtp_conduit(
    rtp: np.ndarray,
    valid: np.ndarray,
    heights_m: tuple[float, float, float] = (100.0, 300.0, 600.0),
    pixel_m: float = 100.0,
) -> dict[str, np.ndarray]:
    """Multi-altitude upward-continued RTP Miller-Singh contact persistence & demag trough."""
    valid_b = np.asarray(valid, bool) & np.isfinite(rtp) & (rtp > -1e30)
    up = fft_upward_continue(rtp, valid_b, heights_m=heights_m, pixel_m=pixel_m)

    z0, z1, z2 = (float(z) for z in heights_m)
    contacts = []
    lap_z0 = None
    gh_z0 = None
    for idx, zf in enumerate((z0, z1, z2)):
        uz = up[zf]
        uy, ux = np.gradient(uz)
        gh = np.hypot(uy, ux).astype(np.float32)
        uyy, _ = np.gradient(uy)
        _, uxx = np.gradient(ux)
        lap_h = (uxx + uyy).astype(np.float32)
        if idx == 0:
            lap_z0 = lap_h
            gh_z0 = gh
        vzz = -lap_h
        g0 = float(np.median(gh[valid_b]) * 0.12 + 1e-6) if valid_b.any() else 1e-3
        cz = (gh / np.sqrt(gh * gh + vzz * vzz + np.float32(g0 * g0))).astype(np.float32)
        contacts.append(np.clip(cz, 0.0, 1.0))

    coh_rtp, az_rtp = coherence_and_strike_deg(up[z1], valid_b, deriv_sigma=1.0, tensor_sigma=3.0)
    assert lap_z0 is not None and gh_z0 is not None
    grad_pct = percentile_rank(gh_z0, valid_b)
    persist_contact = (
        np.cbrt(contacts[0] * contacts[1] * contacts[2]) * grad_pct * coh_rtp
    ).astype(np.float32)
    persist_pct = percentile_rank(persist_contact, valid_b)

    demag_raw = (percentile_rank(np.maximum(lap_z0, 0.0), valid_b) * coh_rtp).astype(np.float32)
    demag_pct = percentile_rank(demag_raw, valid_b)

    conduit_raw = (0.70 * persist_pct + 0.30 * demag_pct).astype(np.float32)
    conduit_pct = percentile_rank(conduit_raw, valid_b)
    return {
        "rtp_persist_pct": persist_pct,
        "rtp_demag_pct": demag_pct,
        "rtp_conduit_pct": conduit_pct,
        "coh_rtp": coh_rtp,
        "az_rtp": az_rtp,
    }


def coulomb_criticality_2d(
    strike_deg: np.ndarray,
    geod_2ndinv: np.ndarray,
    geod_shearrate: np.ndarray,
    geod_dilaterate: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Oriented 2D Mohr-Coulomb transtensional opening + conjugate shear criticality in [0, 1].

    Under NW Great Basin extension (sigma_H,max ~ N15E, sigma_h,min ~ N105E):
      - Tensile / normal dip-slip opening peaks near N18E: ``cos^2(theta - 18 deg)``
        weighted by positive volumetric dilatation ``max(Band 8, 0)``.
      - Conjugate Walker Lane (N30W = 150 deg) & Humboldt (N60E = 60 deg) shear peaks
        at +/-45 deg to sigma_H,max: ``sin^2(2*(theta - 15 deg))`` weighted by
        ``sqrt(max(Band 7, 0) * max(Band 4, 0))``.
      - Both vanish simultaneously near ``theta = 105 deg`` (WNW-ESE clamping & fan washes).
    """
    valid_b = np.asarray(valid, bool)
    th = np.asarray(strike_deg, dtype=np.float32)
    b4 = np.maximum(_clean_valid(geod_2ndinv, valid_b), 0.0)
    b7 = np.maximum(_clean_valid(geod_shearrate, valid_b), 0.0)
    b8_pos = np.maximum(_clean_valid(geod_dilaterate, valid_b), 0.0)

    dil_pct = percentile_rank(b8_pos, valid_b)
    shr_pct = percentile_rank(np.sqrt(b7 * b4).astype(np.float32), valid_b)

    cos_open = (np.cos(np.radians(th - 18.0)) ** 2).astype(np.float32)
    sin_conj = (np.sin(2.0 * np.radians(th - 15.0)) ** 2).astype(np.float32)
    kappa_mc = np.maximum(cos_open, 0.85 * sin_conj).astype(np.float32)

    strain_drive = percentile_rank(0.55 * (dil_pct * cos_open) + 0.45 * (shr_pct * sin_conj), valid_b)
    c_crit = np.where(
        valid_b,
        0.28 + 0.72 * kappa_mc * (0.45 + 0.55 * strain_drive),
        0.0,
    ).astype(np.float32)
    return {
        "kappa_mc": np.where(valid_b, kappa_mc, 0.0).astype(np.float32),
        "strain_drive": strain_drive,
        "c_coulomb": c_crit,
    }


def claycap_alteration_conduit(
    cond_surf: np.ndarray,
    grav_slope: np.ndarray,
    grav_vg: np.ndarray,
    rad_k: np.ndarray,
    rad_th: np.ndarray,
    rad_u: np.ndarray,
    gdr_plume_pct: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Gravity Miller-Singh contact, MT clay-cap lateral edge, radiometric contact gradient & GDR."""
    valid_b = np.asarray(valid, bool)
    b5 = np.maximum(_clean_valid(grav_slope, valid_b), 0.0)
    b11 = _clean_valid(grav_vg, valid_b)
    grav_contact = (b5 / np.sqrt(b5 * b5 + (np.float32(0.04) * b11) ** 2 + np.float32(1e-4))).astype(np.float32)
    grav_contact_pct = percentile_rank(grav_contact * percentile_rank(b5, valid_b), valid_b)

    c17 = gaussian_filter(_clean_valid(cond_surf, valid_b), 1.5).astype(np.float32)
    cy, cx = np.gradient(c17)
    mt_edge_pct = percentile_rank(np.hypot(cy, cx).astype(np.float32), valid_b)

    rk = np.asarray(rad_k, dtype=np.float32)
    rth = np.asarray(rad_th, dtype=np.float32)
    ru = np.asarray(rad_u, dtype=np.float32)
    rad_valid = valid_b & ((rk > 0.0) | (rth > 0.0) | (ru > 0.0))
    if int(rad_valid.sum()) > 100:
        kth = gaussian_filter(np.where(rad_valid, rk / (rth + 1.0), 0.0).astype(np.float32), 1.5)
        uth = gaussian_filter(np.where(rad_valid, ru / (rth + 1.0), 0.0).astype(np.float32), 1.5)
        ky, kx = np.gradient(kth)
        uy, ux = np.gradient(uth)
        rad_grad = 0.60 * percentile_rank(np.hypot(ky, kx).astype(np.float32), rad_valid) + 0.40 * percentile_rank(
            np.hypot(uy, ux).astype(np.float32), rad_valid
        )
        rad_alt_pct = np.where(rad_valid, percentile_rank(rad_grad, rad_valid), 0.5).astype(np.float32)
        rad_alt_pct[~valid_b] = 0.0
    else:
        rad_alt_pct = np.where(valid_b, 0.5, 0.0).astype(np.float32)

    gdr_p = np.where(valid_b, np.clip(np.asarray(gdr_plume_pct, dtype=np.float32), 0.0, 1.0), 0.0)
    hydro_boost = np.where(
        valid_b,
        percentile_rank(0.40 * mt_edge_pct + 0.25 * rad_alt_pct + 0.35 * gdr_p, valid_b),
        0.0,
    ).astype(np.float32)
    return {
        "grav_contact_pct": grav_contact_pct,
        "mt_edge_pct": mt_edge_pct,
        "rad_alt_pct": rad_alt_pct,
        "hydro_boost_pct": hydro_boost,
    }


def oriented_nms_1d(
    surface: np.ndarray,
    strike_deg: np.ndarray,
    valid: np.ndarray,
    step_px: float = 1.0,
) -> np.ndarray:
    """Bilinear Canny-style cross-strike 1D non-maximum suppression along normal ``(sin az, cos az)``."""
    s = np.asarray(surface, dtype=np.float32)
    valid_b = np.asarray(valid, bool)
    h, w = s.shape
    if h < 3 or w < 3:
        return np.zeros((h, w), dtype=bool)

    rad = np.radians(np.asarray(strike_deg, dtype=np.float32))
    ny = (np.sin(rad) * np.float32(step_px)).astype(np.float32)
    nx = (np.cos(rad) * np.float32(step_px)).astype(np.float32)

    max_y = np.nextafter(np.float32(h - 1), np.float32(0.0))
    max_x = np.nextafter(np.float32(w - 1), np.float32(0.0))
    base_y = np.arange(h, dtype=np.float32)[:, None]
    base_x = np.arange(w, dtype=np.float32)[None, :]

    def _interp(sign: float) -> np.ndarray:
        yy = np.clip(base_y + np.float32(sign) * ny, np.float32(0.0), max_y)
        xx = np.clip(base_x + np.float32(sign) * nx, np.float32(0.0), max_x)
        y0 = np.minimum(yy.astype(np.int32), h - 2)
        x0 = np.minimum(xx.astype(np.int32), w - 2)
        fy = np.clip(yy - y0, 0.0, 1.0)
        fx = np.clip(xx - x0, 0.0, 1.0)
        v00 = s[y0, x0]
        v01 = s[y0, x0 + 1]
        v10 = s[y0 + 1, x0]
        v11 = s[y0 + 1, x0 + 1]
        return (
            (1.0 - fy) * ((1.0 - fx) * v00 + fx * v01)
            + fy * ((1.0 - fx) * v10 + fx * v11)
        ).astype(np.float32)

    sp = _interp(+1.0)
    sm = _interp(-1.0)
    crest = valid_b & (s > 0.0) & (((s >= sp) & (s > sm)) | ((s > sp) & (s >= sm)))
    return crest


def coulombdm_surface(
    *,
    det_elev: np.ndarray,
    det_elev_slope: np.ndarray,
    depth_to_base: np.ndarray,
    grav_slope: np.ndarray,
    grav_vg: np.ndarray,
    geod_2ndinv: np.ndarray,
    geod_shearrate: np.ndarray,
    geod_dilaterate: np.ndarray,
    rtp: np.ndarray,
    cond_surf: np.ndarray,
    rad_k: np.ndarray,
    rad_th: np.ndarray,
    rad_u: np.ndarray,
    gdr_plume_pct: np.ndarray,
    footprint: np.ndarray,
) -> dict[str, np.ndarray | float]:
    """Compute the full catalogue-free COULOMBDM surface, 1D NMS crest mask, and diagnostics."""
    foot = np.asarray(footprint, bool)
    valid = foot.copy()
    for arr in (
        det_elev,
        det_elev_slope,
        depth_to_base,
        grav_slope,
        grav_vg,
        geod_2ndinv,
        geod_shearrate,
        geod_dilaterate,
        rtp,
        cond_surf,
    ):
        a = np.asarray(arr, dtype=np.float32)
        valid &= np.isfinite(a) & (a > -1e30)

    # 1. Surface relative log-slope break + 600 m cross-strike monotonicity + elevation coherence
    sl_pos = np.maximum(_clean_valid(det_elev_slope, valid), 0.0)
    log_sl = gaussian_filter(np.log(sl_pos + np.float32(1.0)).astype(np.float32), 1.0)
    sy, sx = np.gradient(log_sl)
    rel_break_pct = percentile_rank(np.hypot(sy, sx).astype(np.float32), valid)
    del sl_pos, log_sl, sy, sx

    coh_elev, az_elev = coherence_and_strike_deg(det_elev, valid)
    mu_step = cross_strike_monotonicity(det_elev, valid, half_span_px=3, normal_sigma=3.0)
    scarp_raw = (rel_break_pct * (0.30 + 0.70 * mu_step) * coh_elev).astype(np.float32)
    scarp_edge_pct = percentile_rank(scarp_raw, valid)

    # 2. Subsurface upward-continued RTP + gravity contact + MT clay-cap + alteration/GDR
    rtp_bundle = upward_rtp_conduit(rtp, valid)
    clay_bundle = claycap_alteration_conduit(
        cond_surf=cond_surf,
        grav_slope=grav_slope,
        grav_vg=grav_vg,
        rad_k=rad_k,
        rad_th=rad_th,
        rad_u=rad_u,
        gdr_plume_pct=gdr_plume_pct,
        valid=valid,
    )

    # 3. Oriented 2D Mohr-Coulomb criticality on topographic and magnetic strike fields
    coul_elev = coulomb_criticality_2d(az_elev, geod_2ndinv, geod_shearrate, geod_dilaterate, valid)
    coul_rtp = coulomb_criticality_2d(rtp_bundle["az_rtp"], geod_2ndinv, geod_shearrate, geod_dilaterate, valid)

    # 4. Structural habitat envelopes (Piedmont hinge, Concealed cover, Range-front/relay bedrock)
    el_c = _clean_valid(det_elev, valid)
    db_c = np.maximum(_clean_valid(depth_to_base, valid), 0.0)
    if valid.any():
        p33, p67 = [float(x) for x in np.percentile(el_c[valid], [33.333333, 66.666667])]
    else:
        p33, p67 = -100.0, 100.0
    z_mid = float(0.5 * (p33 + p67))
    z_sig = float(max(0.95 * (p67 - p33), 1.0))

    pied_elev_env = np.exp(-0.5 * ((el_c - z_mid) / z_sig) ** 2).astype(np.float32)
    pied_cover_env = np.exp(-0.5 * ((np.log1p(db_c) - float(np.log1p(175.0))) / 1.40) ** 2).astype(np.float32)
    concealed_env = (
        np.exp(-0.5 * ((np.log1p(db_c) - float(np.log1p(240.0))) / 1.45) ** 2)
        * (0.20 + 0.80 * pied_elev_env)
    ).astype(np.float32)
    # Upper-piedmont / range-block tectonic envelope (suppressing deep flat playas el_c < p33)
    range_gate = (1.0 / (1.0 + np.exp(-(el_c - p33) / 45.0))).astype(np.float32)

    hydro_mod = (0.76 + 0.24 * clay_bundle["hydro_boost_pct"]).astype(np.float32)
    grav_mod = (0.62 + 0.38 * clay_bundle["grav_contact_pct"]).astype(np.float32)
    geophys_corrob = (
        0.55 * rtp_bundle["rtp_conduit_pct"] + 0.45 * clay_bundle["grav_contact_pct"]
    ).astype(np.float32)

    # Regime A: Piedmont accommodation monoclinal scarp channel (scale-matched via scarp_raw)
    r_pied = np.where(
        valid,
        scarp_raw
        * pied_elev_env
        * pied_cover_env
        * grav_mod
        * coul_elev["c_coulomb"]
        * hydro_mod
        * (0.78 + 0.22 * rtp_bundle["rtp_persist_pct"]),
        0.0,
    ).astype(np.float32)

    # Regime B: Concealed thin-to-moderate cover RTP + gravity + MT clay-cap conduit
    sub_raw = (
        rtp_bundle["rtp_persist_pct"]
        * rtp_bundle["coh_rtp"]
        * (0.55 + 0.45 * clay_bundle["grav_contact_pct"])
        * (0.65 + 0.35 * clay_bundle["hydro_boost_pct"])
    ).astype(np.float32)
    r_sub = np.where(
        valid,
        0.72 * sub_raw * concealed_env * coul_rtp["c_coulomb"],
        0.0,
    ).astype(np.float32)

    # Regime C: Geophysically & Coulomb-corroborated range-front / relay bedrock faults
    r_bed = np.where(
        valid,
        0.64 * scarp_raw * range_gate * (0.45 + 0.55 * geophys_corrob) * coul_elev["c_coulomb"] * hydro_mod,
        0.0,
    ).astype(np.float32)

    # Fuzzy multi-regime union with per-pixel winning orientation for Canny 1D NMS
    s_raw = np.maximum(np.maximum(r_pied, r_sub), r_bed).astype(np.float32)
    use_rtp_strike = (r_sub > r_pied) & (r_sub >= r_bed)
    az_win = np.where(use_rtp_strike, rtp_bundle["az_rtp"], az_elev).astype(np.float32)
    s_raw_smooth = np.where(valid, gaussian_filter(s_raw, 0.55), 0.0).astype(np.float32)
    crest_1d = oriented_nms_1d(s_raw_smooth, az_win, valid, step_px=1.0)
    s_pct = percentile_rank(s_raw_smooth, valid)

    # Skeleton habitat score for hybrid H19-5 submodular selection
    hab_coulomb = np.where(
        valid,
        percentile_rank(
            (0.62 * pied_elev_env * pied_cover_env + 0.20 * concealed_env + 0.18 * range_gate * geophys_corrob)
            * coul_elev["c_coulomb"]
            * grav_mod
            * hydro_mod,
            valid,
        ),
        0.0,
    ).astype(np.float32)

    return {
        "valid": valid,
        "rel_break_pct": rel_break_pct,
        "mu_step": mu_step,
        "coh_elev": coh_elev,
        "scarp_edge_pct": scarp_edge_pct,
        "rtp_persist_pct": rtp_bundle["rtp_persist_pct"],
        "rtp_demag_pct": rtp_bundle["rtp_demag_pct"],
        "rtp_conduit_pct": rtp_bundle["rtp_conduit_pct"],
        "grav_contact_pct": clay_bundle["grav_contact_pct"],
        "mt_edge_pct": clay_bundle["mt_edge_pct"],
        "rad_alt_pct": clay_bundle["rad_alt_pct"],
        "hydro_boost_pct": clay_bundle["hydro_boost_pct"],
        "kappa_mc": coul_elev["kappa_mc"],
        "c_coulomb_elev": coul_elev["c_coulomb"],
        "c_coulomb_rtp": coul_rtp["c_coulomb"],
        "r_pied": r_pied,
        "r_sub": r_sub,
        "r_bed": r_bed,
        "S_raw": s_raw_smooth,
        "S_pct": s_pct,
        "az_win": az_win,
        "crest_1d": crest_1d,
        "hab_coulomb_pct": hab_coulomb,
        "p33_det_elev_m": p33,
        "p67_det_elev_m": p67,
    }
