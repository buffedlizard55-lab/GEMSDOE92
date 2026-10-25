"""NETEXPAND lane: network-context + analytic-signal/texture-expanded LOQO.

Pre-registered in docs/HYPOTHESES_20261025_NETEXPAND.md (Rank 1).

Adds six catalogue-free features and a pure new-channel crest on top of the
shared KNICKLOQO (30) + LISTRIC (4) + FAULTNET context (5) stack:

  grav_asa          gravity 3-component analytic-signal amplitude percentile
                    rank (reuses gems.gravquad.analytic_signal_amplitude)
  grav_coh          structure-tensor linear coherence of grav ASA
                    (reuses gems.gravquad.structure_tensor_coherence)
  mag_asa           IQR-standardized magnetic analytic-signal proxy from
                    horizontal gradients of B14 TMI and B9 TMI vertical
                    gradient (band units differ, hence standardization;
                    documented proxy, not a true Nabighian ASA)
  mag_coh           structure-tensor coherence of mag ASA
  curie_suppression multi-scale RTP variance suppression 1 - var3/var15
                    percentile rank (reuses gems.curie_demag.local_variance)
  mt_changepoint    conductivity discontinuity at locally constant cover:
                    rank(|grad log B17|) * (1 - rank(|grad B15|))

Strict invariant: no fault catalogue array enters any function in this
module. Catalogue-network context is computed by gems.faultnet from the
*visible* catalogue supplied by the caller (holdout-safe).
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

from .breakline import percentile_rank
from .curie_demag import local_variance
from .gravquad import analytic_signal_amplitude, structure_tensor_coherence
from .hydroconduit import _clean_valid
from .knick_loqo import (
    DEBIASED_INDICES,
    SUB_KNICK_INDICES,
    calibrate_quadrant_probabilities,
    fit_single_loqo,
)

__all__ = [
    "NEW_FEATURE_NAMES",
    "compute_netexpand_features",
    "build_pure_crest_channel",
    "branch_columns",
    "fit_predict_netexpand_loqo",
]

NEW_FEATURE_NAMES: tuple[str, ...] = (
    "grav_asa",
    "grav_coh",
    "mag_asa",
    "mag_coh",
    "curie_suppression",
    "mt_changepoint",
)

# Column layout of the 45-column NETEXPAND stack.
N_KNICK = 30
LISTRIC_COLS = tuple(range(30, 34))
CONTEXT_COLS = tuple(range(34, 39))
NEW_COLS = tuple(range(39, 45))
N_COLS = 45


def _robust_z(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    v = a[np.asarray(valid, bool) & np.isfinite(a)]
    if v.size == 0:
        return np.zeros_like(a, dtype=np.float32)
    med = float(np.median(v))
    q25, q75 = (float(x) for x in np.quantile(v.astype(np.float64), [0.25, 0.75]))
    iqr = max(q75 - q25, 1e-6)
    return ((a.astype(np.float64) - med) / iqr).astype(np.float32)


def compute_netexpand_features(
    *,
    rtp: np.ndarray,
    tmi: np.ndarray,
    tmi_vg: np.ndarray,
    grav_vg: np.ndarray,
    grav_anom: np.ndarray,
    grav_hg: np.ndarray,
    depth_to_base: np.ndarray,
    cond_surf: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Six new catalogue-free features (percentile-ranked, 0 outside valid)."""
    foot = np.asarray(footprint, dtype=bool)
    val = np.asarray(valid, dtype=bool) & foot

    # --- gravity analytic signal + coherence (gravquad math, array inputs) ---
    g_vg = _clean_valid(grav_vg, val)
    g_hg = _clean_valid(grav_hg, val)
    g_an = _clean_valid(grav_anom, val)
    grav_asa_raw = analytic_signal_amplitude(g_vg, g_hg, g_an)
    del g_vg, g_hg, g_an
    grav_coh_raw = structure_tensor_coherence(grav_asa_raw, val, window=7)
    grav_asa = percentile_rank(grav_asa_raw, val)
    del grav_asa_raw
    grav_coh = percentile_rank(grav_coh_raw, val)
    del grav_coh_raw

    # --- magnetic ASA proxy: standardized components (units differ) ---
    tmi_s = gaussian_filter(_clean_valid(tmi, val), 1.0).astype(np.float32)
    gy, gx = np.gradient(tmi_s.astype(np.float64))
    del tmi_s
    zx = _robust_z(gx.astype(np.float32), val)
    zy = _robust_z(gy.astype(np.float32), val)
    del gx, gy
    zv = _robust_z(_clean_valid(tmi_vg, val), val)
    mag_asa_raw = np.sqrt(
        zx.astype(np.float64) ** 2 + zy.astype(np.float64) ** 2 + zv.astype(np.float64) ** 2
    ).astype(np.float32)
    del zx, zy, zv
    mag_coh_raw = structure_tensor_coherence(mag_asa_raw, val, window=7)
    mag_asa = percentile_rank(mag_asa_raw, val)
    del mag_asa_raw
    mag_coh = percentile_rank(mag_coh_raw, val)
    del mag_coh_raw

    # --- RTP multi-scale variance suppression (curie_demag math) ---
    rtp_c = np.where(val, _clean_valid(rtp, val), 0.0).astype(np.float32)
    var3 = local_variance(rtp_c, size=3)
    var15 = local_variance(rtp_c, size=15)
    del rtp_c
    ratio = var3 / (var15 + np.float32(1e-6))
    del var3, var15
    supp_raw = (1.0 - np.clip(ratio, 0.0, 1.0)).astype(np.float32)
    del ratio
    supp_raw[~val] = 0.0
    curie_suppression = percentile_rank(supp_raw, val)
    del supp_raw

    # --- MT change-point at locally constant cover ---
    cond_c = np.log(np.maximum(_clean_valid(cond_surf, val), np.float32(0.1))).astype(np.float32)
    cy, cx = np.gradient(gaussian_filter(cond_c, 2.0).astype(np.float64))
    del cond_c
    mt_grad = np.hypot(cy, cx).astype(np.float32)
    del cy, cx
    db_c = gaussian_filter(_clean_valid(depth_to_base, val), 2.0).astype(np.float32)
    dy, dx = np.gradient(db_c.astype(np.float64))
    del db_c
    db_grad = np.hypot(dy, dx).astype(np.float32)
    del dy, dx
    mt_changepoint = (
        percentile_rank(mt_grad, val) * (1.0 - percentile_rank(db_grad, val))
    ).astype(np.float32)
    del mt_grad, db_grad

    feats = {
        "grav_asa": grav_asa,
        "grav_coh": grav_coh,
        "mag_asa": mag_asa,
        "mag_coh": mag_coh,
        "curie_suppression": curie_suppression,
        "mt_changepoint": mt_changepoint,
    }
    for k in feats:
        feats[k] = np.where(
            val, np.nan_to_num(feats[k], nan=0.0, posinf=0.0, neginf=0.0), 0.0
        ).astype(np.float32)
        feats[k][:8, :] = 0.0
        feats[k][-8:, :] = 0.0
        feats[k][:, :8] = 0.0
        feats[k][:, -8:] = 0.0
    return feats


def build_pure_crest_channel(
    feats: dict[str, np.ndarray],
    l_listric: np.ndarray,
    valid: np.ndarray,
) -> np.ndarray:
    """L_new in [0,1]: max of ASA-coherence geometric means, alteration
    product rank, and cubed listric crest. Topo/knick channels excluded."""
    val = np.asarray(valid, dtype=bool)
    grav = np.sqrt(np.maximum(feats["grav_asa"] * feats["grav_coh"], 0.0))
    mag = np.sqrt(np.maximum(feats["mag_asa"] * feats["mag_coh"], 0.0))
    alter = percentile_rank(
        (feats["curie_suppression"] * feats["mt_changepoint"]).astype(np.float32), val
    )
    lst = (np.clip(np.asarray(l_listric, dtype=np.float32), 0.0, 1.0) ** np.float32(3.0)).astype(np.float32)
    out = np.maximum(np.maximum(grav, mag), np.maximum(alter, lst)).astype(np.float32)
    return np.where(val, np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0), 0.0).astype(np.float32)


def branch_columns(*, with_context: bool) -> dict[str, tuple[int, ...] | None]:
    extra = set(LISTRIC_COLS) | set(NEW_COLS) | (set(CONTEXT_COLS) if with_context else set())
    full = tuple(range(N_COLS)) if with_context else tuple(
        c for c in range(N_COLS) if c not in CONTEXT_COLS
    )
    return {
        "full": full,
        "debiased": tuple(sorted(set(DEBIASED_INDICES) | extra)),
        "sub": tuple(sorted(set(SUB_KNICK_INDICES) | extra)),
    }


def fit_predict_netexpand_loqo(
    X_foot, footprint, valid, quad, label_mask, *,
    with_context: bool = True,
    excluded_mask=None, guard_px=12, neg_buffer_px=5.0, neg_pos_ratio=4,
    seed=20261025, max_iter=185, calibrate_quadrants=True,
    calib_weight=0.80, power_gamma=3.3,
):
    """3-branch LOQO (15% full / 35% debiased / 50% sub) on the 45-col stack."""
    valid_b = np.asarray(valid, dtype=bool) & np.asarray(footprint, dtype=bool)
    cols = branch_columns(with_context=with_context)
    kw = dict(excluded_mask=excluded_mask, guard_px=guard_px,
              neg_buffer_px=neg_buffer_px, neg_pos_ratio=neg_pos_ratio, max_iter=max_iter)
    p_full = fit_single_loqo(X_foot, footprint, valid_b, quad, label_mask,
                             feature_cols=cols["full"], seed=int(seed), **kw)
    p_deb = fit_single_loqo(X_foot, footprint, valid_b, quad, label_mask,
                            feature_cols=cols["debiased"], seed=int(seed) + 1, **kw)
    p_sub = fit_single_loqo(X_foot, footprint, valid_b, quad, label_mask,
                            feature_cols=cols["sub"], seed=int(seed) + 2, **kw)
    raw = (np.float32(0.15) * p_full + np.float32(0.35) * p_deb
           + np.float32(0.50) * p_sub).astype(np.float32)
    cal = (calibrate_quadrant_probabilities(
        raw, valid_b, quad, calib_weight=calib_weight, power_gamma=power_gamma)
        if calibrate_quadrants else raw.copy())
    return {"p_full": p_full, "p_debiased": p_deb, "p_sub": p_sub,
            "raw_proba": raw, "cal_proba": cal}
