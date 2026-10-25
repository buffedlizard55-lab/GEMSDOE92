"""COULOMB lane surface: orientation-resolved transtensional opening tendency.

Geology & Geophysics
--------------------
Slip/dilation-tendency theory (Morris, Ferrill & Henderson 1996) predicts that
fractures which are simultaneously well oriented for shear slip and normal
opening under the present-day stress field maintain breccia permeability and
rupture first, whereas misoriented pre-Quaternary contacts stay locked.  The
``existing_faults.tif`` catalogue maps scarps regardless of present-day
activity; a young, still-propagating blind strand in an opening relay can be
geomorphically subtle -- missed by photo-era mapping and by multi-line
potential-field worms -- while sitting in crust that is measurably extending
across its strike today (cf. the 2020 M6.5 Monte Cristo Range rupture of
largely unmapped strands).

Every prior GEMSDOE92 lane weights lineaments by *scalar* strain magnitude
(STRAINBREAK: ``L x pct(Band 4)``; HYDROCONDUIT: ``0.5*pct(Band 4) +
0.5*pct(Band 8)`` times a *static* strike prior that scores a strike
identically in extending and locked crust).  This lane instead *resolves* the
local strain state onto the per-pixel lineament orientation:

* ``O_ext = pct(Band 8 clamped >= 0) x cos^2(normal_az - alpha_ext)`` -- signed
  volumetric dilatation (Band 8 ``geod_dilaterate``) projected across the
  structure-tensor lineament normal, with the regional max-extension azimuth
  pre-registered as the design constant ``ALPHA_EXT_DEG = 100`` (WNW-ESE
  Basin-and-Range GPS extension; Hammond & Thatcher 2004; Kreemer et al.
  2012 -- assumed, never fitted on the holdout);
* ``O_shear = pct(Band 7) x gaussian(strike; 140 deg, 25 deg)`` -- GPS/InSAR
  shear rate (Band 7 ``geod_shearrate``, never used in any built lane) given
  full weight on the NW-striking set that accommodates Walker Lane dextral
  transtension (Faulds, Henry & Hinz);
* ``O_coulomb = 0.65 * O_ext + 0.35 * O_shear`` (pre-registered mix).

The sharp-lineament base reuses (imports, never forks) the two proven
HYDROCONDUIT channels -- the true Band-2 RTP tilt-contact edge /
magnetite-destruction trough and the relative log-slope-break x coherence x
600 m monotonicity scarp detector -- inside the APRONRIDGE thin-cover
piedmont apron habitat.  The lane's novelty is the Coulomb reweighting, the
first use of Band 7, and standalone (zero ``H19-5``/``R0``) 1D-crest emission
with prior-far repulsion.

Zero catalogue information enters any function in this module.

Pre-registration: docs/HYPOTHESES_20261024_COULOMB.md (Rank 1 + screen rule).
"""

from __future__ import annotations

import numpy as np

from .apronridge import apron_habitat, directional_ridge_1d
from .breakline import percentile_rank, spaced_top_mask
from .hydroconduit import (
    coherence_and_strike_deg,
    cross_strike_monotonicity,
    rtp_tilt_and_demag,
)

__all__ = [
    "ALPHA_EXT_DEG",
    "NW_CENTER_DEG",
    "NW_SIGMA_DEG",
    "EXT_MIX",
    "coulomb_opening",
    "coulomb_surface",
    "magtilt_contact",
    "mtedge_dilat",
    "seismo_prior",
    "directional_ridge_1d",
    "percentile_rank",
    "spaced_top_mask",
]

# Pre-registered design constants (HYPOTHESES_20261024_COULOMB.md).  Assumed
# from published regional GPS, never fitted on the holdout.
ALPHA_EXT_DEG = 100.0  # regional max horizontal extension azimuth (WNW-ESE)
NW_CENTER_DEG = 140.0  # Walker Lane dextral NW set center strike
NW_SIGMA_DEG = 25.0  # Walker Lane dextral set angular width
EXT_MIX = 0.65  # O_coulomb = EXT_MIX * O_ext + (1 - EXT_MIX) * O_shear


def _clean_valid(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Replace non-valid, non-finite, or sentinel (<= -1e30) cells with valid median."""
    arr = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, dtype=bool) & np.isfinite(arr) & (arr > -1e30)
    fill = np.float32(np.median(arr[m])) if m.any() else np.float32(0.0)
    return np.where(m, arr, fill).astype(np.float32)


def _angdist_mod180(a_deg: np.ndarray, b_deg: float) -> np.ndarray:
    """Absolute angular distance in [0, 90] under 180-degree (axial) symmetry."""
    d = np.abs(np.asarray(a_deg, dtype=np.float32) - np.float32(b_deg)) % 180.0
    return np.minimum(d, 180.0 - d).astype(np.float32)


def coulomb_opening(
    strike_deg: np.ndarray,
    dilaterate: np.ndarray,
    shearrate: np.ndarray,
    valid: np.ndarray,
    *,
    alpha_ext_deg: float = ALPHA_EXT_DEG,
    nw_center_deg: float = NW_CENTER_DEG,
    nw_sigma_deg: float = NW_SIGMA_DEG,
    ext_mix: float = EXT_MIX,
) -> dict[str, np.ndarray]:
    """Orientation-resolved opening tendency ``O_coulomb`` in [0, 1].

    ``strike_deg`` is compass strike azimuth in [0, 180) (0 = N-S, 90 = E-W).
    ``dilaterate``/``shearrate`` are raw Bands 8/7 (signed/smooth-safe).
    """
    vb = np.asarray(valid, bool)
    dil = np.asarray(dilaterate, dtype=np.float32)
    shr = np.asarray(shearrate, dtype=np.float32)
    strike = np.asarray(strike_deg, dtype=np.float32)

    dil_pct = percentile_rank(dil, vb)
    dil_pos = np.where(vb & np.isfinite(dil) & (dil > -1e30) & (dil > 0), 1.0, 0.0)
    opening_mag = (dil_pct * dil_pos).astype(np.float32)

    normal_az = (strike + 90.0) % 180.0
    delta = _angdist_mod180(normal_az, float(alpha_ext_deg) % 180.0)
    ori = np.cos(np.radians(delta)) ** 2
    o_ext = (opening_mag * ori).astype(np.float32)

    shear_mag = percentile_rank(shr, vb)
    d_nw = _angdist_mod180(strike, float(nw_center_deg))
    w_nw = np.exp(-0.5 * (d_nw / float(nw_sigma_deg)) ** 2).astype(np.float32)
    o_shear = (shear_mag * w_nw).astype(np.float32)

    o_raw = (float(ext_mix) * o_ext + (1.0 - float(ext_mix)) * o_shear).astype(np.float32)
    o_raw[~vb] = 0.0
    o_pct = percentile_rank(o_raw, vb)
    return {
        "opening_mag": opening_mag,
        "opening_ori": ori.astype(np.float32),
        "O_ext": o_ext,
        "shear_mag": shear_mag,
        "nw_weight": w_nw,
        "O_shear": o_shear,
        "O_raw": o_raw,
        "O_pct": o_pct,
    }


def seismo_prior(
    deq: np.ndarray,
    ieq: np.ndarray,
    second_inv: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Instrumental-swarm prior ``pct(-deq) x pct(ieq) x pct(2ndinv)`` (Rank 2)."""
    vb = np.asarray(valid, bool)
    prox = percentile_rank(-_clean_valid(deq, vb), vb)
    inten = percentile_rank(_clean_valid(ieq, vb), vb)
    strain = percentile_rank(_clean_valid(second_inv, vb), vb)
    raw = (prox * inten * strain).astype(np.float32)
    raw[~vb] = 0.0
    return {"prox": prox, "intensity": inten, "strain": strain,
            "seismo_raw": raw, "seismo_pct": percentile_rank(raw, vb)}


def magtilt_contact(
    tmi_hg: np.ndarray,
    tmi_vg: np.ndarray,
    rtp: np.ndarray,
    valid: np.ndarray,
    *,
    tau: float = 0.25,
) -> dict[str, np.ndarray]:
    """Amplitude-normalized TMI tilt-derivative zero-crossing ridge (Rank 3).

    ``theta_m = atan2(Band 9, Band 3 + eps)`` (Salem et al. 2007);
    ridge = ``exp(-|theta_m| / tau) x pct(||grad theta_m||) x coh(Band 2)``.
    """
    vb = np.asarray(valid, bool)
    hg = _clean_valid(tmi_hg, vb)
    vg = _clean_valid(tmi_vg, vb)
    theta = np.arctan2(vg, hg + np.float32(1e-6)).astype(np.float32)
    gy, gx = np.gradient(theta)
    grad_pct = percentile_rank(np.hypot(gy, gx).astype(np.float32), vb)
    del gy, gx
    coh_rtp, _ = coherence_and_strike_deg(rtp, vb)
    zc = np.exp(-np.abs(theta) / float(tau)).astype(np.float32)
    raw = (zc * grad_pct * coh_rtp).astype(np.float32)
    raw[~vb] = 0.0
    return {"theta_m": theta, "tilt_grad_pct": grad_pct, "coh_rtp": coh_rtp,
            "magtilt_raw": raw, "magtilt_pct": percentile_rank(raw, vb)}


def mtedge_dilat(
    cond_surf: np.ndarray,
    dilaterate: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Standalone MT lateral-edge x dilatation lane (Rank 4).

    ``pct(||grad Band 17||) x pct(max(Band 8, 0)) x coh(Band 17)``.
    """
    vb = np.asarray(valid, bool)
    cs = _clean_valid(cond_surf, vb)
    gy, gx = np.gradient(cs)
    edge_pct = percentile_rank(np.hypot(gy, gx).astype(np.float32), vb)
    del cs, gy, gx
    dil = np.asarray(dilaterate, dtype=np.float32)
    dil_pos = np.where(vb & np.isfinite(dil) & (dil > -1e30),
                       np.maximum(dil, 0.0), 0.0).astype(np.float32)
    dil_pct = percentile_rank(dil_pos, vb)
    coh_mt, _ = coherence_and_strike_deg(cond_surf, vb)
    raw = (edge_pct * dil_pct * coh_mt).astype(np.float32)
    raw[~vb] = 0.0
    return {"mt_edge_pct": edge_pct, "dil_pos_pct": dil_pct, "coh_mt": coh_mt,
            "mtedge_raw": raw, "mtedge_pct": percentile_rank(raw, vb)}


def coulomb_surface(
    *,
    det_elev: np.ndarray,
    det_elev_slope: np.ndarray,
    depth_to_base: np.ndarray,
    grav_slope: np.ndarray,
    rtp: np.ndarray,
    dilaterate: np.ndarray,
    shearrate: np.ndarray,
    second_inv: np.ndarray,
    deq: np.ndarray,
    ieq: np.ndarray,
    footprint: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute the pre-registered Rank-1 surfaces ``S_free`` / ``S_open`` / ``S_seismo``.

    * Exp 1 ``S_free   = max(R_rtp_tilt, R_scarp_rel) x O_coulomb x H_apron``
    * Exp 2 ``S_open   = max(R_rtp_tilt, R_scarp_rel) x O_coulomb`` (no apron gate)
    * Exp 3 ``S_seismo = S_free x (0.50 + 0.50 x seismo_prior)`` (Rank-1 x Rank-2 fusion)
    """
    fp = np.asarray(footprint, bool)
    bands = [det_elev, det_elev_slope, depth_to_base, grav_slope, rtp,
             dilaterate, shearrate, second_inv, deq, ieq]
    valid = fp.copy()
    for b in bands:
        bb = np.asarray(b)
        valid &= np.isfinite(bb) & (bb > -1e30)

    # Sharp channel 1: true RTP tilt-contact edge + demagnetization trough.
    rtp_parts = rtp_tilt_and_demag(rtp, valid)
    r_rtp = rtp_parts["rtp_conduit_pct"]
    del rtp_parts

    # Sharp channel 2: relative log-slope break x coherence x monotonicity.
    s_clean = np.maximum(_clean_valid(det_elev_slope, valid), 0.0)
    log_slope = np.log(s_clean + np.float32(1.0)).astype(np.float32)
    del s_clean
    ls_y, ls_x = np.gradient(log_slope)
    rel_break_pct = percentile_rank(np.hypot(ls_y, ls_x).astype(np.float32), valid)
    del log_slope, ls_y, ls_x
    coh_elev, strike_elev = coherence_and_strike_deg(det_elev, valid)
    mu_step = cross_strike_monotonicity(det_elev, valid, half_span_px=3,
                                        normal_sigma=3.0, elev_floor_m=0.5)
    r_scarp = (rel_break_pct * coh_elev * mu_step).astype(np.float32)

    # Joint Band-12 + Band-2 fault normals: strike of the more coherent field.
    coh_rtp, strike_rtp = coherence_and_strike_deg(rtp, valid)
    use_rtp = coh_rtp > coh_elev
    strike_joint = np.where(use_rtp, strike_rtp, strike_elev).astype(np.float32)
    coh_joint = np.maximum(coh_rtp, coh_elev).astype(np.float32)
    del coh_rtp, strike_rtp, strike_elev

    oc = coulomb_opening(strike_joint, dilaterate, shearrate, valid)
    o_raw = oc["O_raw"]
    del oc

    hab = apron_habitat(det_elev, depth_to_base, grav_slope, valid)
    h_apron = hab["H_apron"]
    del hab

    edge_union = np.maximum(r_rtp, r_scarp).astype(np.float32)
    s_open_raw = np.where(valid, edge_union * o_raw, 0.0).astype(np.float32)
    s_free_raw = np.where(valid, s_open_raw * h_apron, 0.0).astype(np.float32)
    del edge_union

    sp = seismo_prior(deq, ieq, second_inv, valid)
    seismo_pct = sp["seismo_pct"]
    del sp
    s_seismo_raw = (s_free_raw * (0.50 + 0.50 * seismo_pct)).astype(np.float32)
    s_seismo_raw[~valid] = 0.0

    s_free_pct = percentile_rank(s_free_raw, valid)
    s_open_pct = percentile_rank(s_open_raw, valid)
    s_seismo_pct = percentile_rank(s_seismo_raw, valid)

    return {
        "valid": valid,
        "R_rtp_tilt": r_rtp,
        "R_scarp_rel": r_scarp,
        "rel_break_pct": rel_break_pct,
        "coh_elev": coh_elev,
        "coh_joint": coh_joint,
        "strike_joint": strike_joint,
        "mu_step": mu_step,
        "O_coulomb": o_raw,
        "O_pct": percentile_rank(o_raw, valid),
        "H_apron": h_apron,
        "seismo_pct": seismo_pct,
        "S_free_raw": s_free_raw,
        "S_free_pct": s_free_pct,
        "S_open_raw": s_open_raw,
        "S_open_pct": s_open_pct,
        "S_seismo_raw": s_seismo_raw,
        "S_seismo_pct": s_seismo_pct,
        "ridge_free": directional_ridge_1d(s_free_raw, valid),
        "ridge_open": directional_ridge_1d(s_open_raw, valid),
        "ridge_seismo": directional_ridge_1d(s_seismo_raw, valid),
    }
