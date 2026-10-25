"""LISTRIC lane: listric normal-fault surface/subsurface offset-pair features.

Pre-registered in docs/HYPOTHESES_20261026_LISTRIC.md.  Extends the KNICKLOQO
30-feature catalogue-free stack with four features targeting 45-60 deg listric
normal faults whose surface scarp is laterally offset 200-800 m (2-8 px) from
the subsurface gravity/basement inflection toward the hanging wall.

Strict zero-leakage invariant: no fault catalogue array enters any function.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

from .breakline import percentile_rank
from .hydroconduit import _clean_valid
from .knick_loqo import (
    DEBIASED_INDICES,
    SUB_KNICK_INDICES,
    calibrate_quadrant_probabilities,
    fit_single_loqo,
    thalweg_concavity_strength,
)

__all__ = [
    "LISTRIC_FEATURE_NAMES",
    "LISTRIC_COL0",
    "compute_listric_features",
    "fit_predict_listric_loqo",
]

LISTRIC_FEATURE_NAMES: tuple[str, ...] = (
    "listric_offset_concord",
    "listric_offset_excess",
    "listric_dip_concord",
    "listric_rollover",
)
LISTRIC_COL0 = 30  # appended after KNICKLOQO's 30 features

_DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def _shift(arr: np.ndarray, dy: int, dx: int) -> np.ndarray:
    out = np.zeros_like(arr)
    ys = slice(max(dy, 0), arr.shape[0] + min(dy, 0))
    yt = slice(max(-dy, 0), arr.shape[0] + min(-dy, 0))
    xs = slice(max(dx, 0), arr.shape[1] + min(dx, 0))
    xt = slice(max(-dx, 0), arr.shape[1] + min(-dx, 0))
    out[ys, xs] = arr[yt, xt]
    return out


def _grad_mag(field: np.ndarray, valid: np.ndarray, sigma: float = 1.0):
    u = gaussian_filter(_clean_valid(field, valid), float(sigma)).astype(np.float32)
    gy, gx = np.gradient(u)
    return gx.astype(np.float32), gy.astype(np.float32), np.hypot(gx, gy).astype(np.float32)


def compute_listric_features(
    *,
    det_elev: np.ndarray,
    det_elev_slope: np.ndarray,
    grav_hg: np.ndarray,
    depth_to_base: np.ndarray,
    footprint: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Return 4 full-grid listric features (float32, 0 outside valid) + L_listric."""
    foot = np.asarray(footprint, dtype=bool)
    val = np.asarray(valid, dtype=bool) & foot

    # Surface scarp strength: slope-break magnitude
    log_slope = np.log(np.maximum(_clean_valid(det_elev_slope, val), 0.0) + np.float32(1.0)).astype(np.float32)
    _, _, scarp_mag = _grad_mag(log_slope, val, sigma=1.0)
    r_scarp = percentile_rank(scarp_mag, val)

    # Subsurface edge: gravity horizontal gradient x basement-relief gradient
    _, _, base_grad = _grad_mag(depth_to_base, val, sigma=1.5)
    r_hg = percentile_rank(np.abs(_clean_valid(grav_hg, val)), val)
    r_base = percentile_rank(base_grad, val)
    sub_edge = np.sqrt(np.maximum(r_hg * r_base, 0.0)).astype(np.float32)

    colocated = np.sqrt(np.maximum(r_scarp * sub_edge, 0.0)).astype(np.float32)
    shifted_max = np.zeros_like(sub_edge)
    for dist in (3, 6):
        for dy, dx in _DIRS:
            shifted_max = np.maximum(shifted_max, _shift(sub_edge, dy * dist, dx * dist))
    offset_concord = np.sqrt(np.maximum(r_scarp * shifted_max, 0.0)).astype(np.float32)
    offset_excess = np.clip(offset_concord - colocated, 0.0, None).astype(np.float32)

    # Dip concordance: downhill direction vs basement-deepening direction
    ex, ey, emag = _grad_mag(det_elev, val, sigma=2.0)
    bx, by, bmag = _grad_mag(depth_to_base, val, sigma=2.0)
    cosang = (-ex * bx - ey * by) / (emag * bmag + np.float32(1e-6))
    dip = (np.float32(0.5) * (np.clip(cosang, -1.0, 1.0) + np.float32(1.0))
           * np.sqrt(np.maximum(percentile_rank(emag, val) * percentile_rank(bmag, val), 0.0))).astype(np.float32)

    # Rollover: concave elev curvature in annulus around subsurface edge
    annulus = np.clip(gaussian_filter(sub_edge, 5.0) - gaussian_filter(sub_edge, 1.5), 0.0, None).astype(np.float32)
    conc = thalweg_concavity_strength(det_elev, val, sigma=3.0)
    rollover = np.sqrt(np.maximum(percentile_rank(annulus, val) * percentile_rank(conc, val), 0.0)).astype(np.float32)

    feats = {
        "listric_offset_concord": offset_concord,
        "listric_offset_excess": offset_excess,
        "listric_dip_concord": dip.astype(np.float32),
        "listric_rollover": rollover,
    }
    for k in feats:
        feats[k] = np.where(val, np.nan_to_num(feats[k], nan=0.0, posinf=0.0, neginf=0.0), 0.0).astype(np.float32)
        feats[k][:8, :] = 0.0; feats[k][-8:, :] = 0.0; feats[k][:, :8] = 0.0; feats[k][:, -8:] = 0.0
    feats["L_listric"] = percentile_rank(feats["listric_offset_concord"], val).astype(np.float32)
    return feats


def fit_predict_listric_loqo(X_foot, footprint, valid, quad, label_mask, *, excluded_mask=None,
                             guard_px=12, neg_buffer_px=5.0, neg_pos_ratio=4, seed=20261026,
                             max_iter=185, calibrate_quadrants=True, calib_weight=0.80, power_gamma=3.3):
    """3-branch LOQO (15% full-34 / 35% debiased+listric / 50% sub-knick+listric)."""
    valid_b = np.asarray(valid, dtype=bool) & np.asarray(footprint, dtype=bool)
    listric_cols = tuple(range(LISTRIC_COL0, LISTRIC_COL0 + 4))
    deb_cols = tuple(sorted(set(DEBIASED_INDICES) | set(listric_cols)))
    sub_cols = tuple(sorted(set(SUB_KNICK_INDICES) | set(listric_cols)))
    kw = dict(excluded_mask=excluded_mask, guard_px=guard_px, neg_buffer_px=neg_buffer_px,
              neg_pos_ratio=neg_pos_ratio, max_iter=max_iter)
    p_full = fit_single_loqo(X_foot, footprint, valid_b, quad, label_mask, feature_cols=None, seed=int(seed), **kw)
    p_deb = fit_single_loqo(X_foot, footprint, valid_b, quad, label_mask, feature_cols=deb_cols, seed=int(seed) + 1, **kw)
    p_sub = fit_single_loqo(X_foot, footprint, valid_b, quad, label_mask, feature_cols=sub_cols, seed=int(seed) + 2, **kw)
    raw = (np.float32(0.15) * p_full + np.float32(0.35) * p_deb + np.float32(0.50) * p_sub).astype(np.float32)
    cal = (calibrate_quadrant_probabilities(raw, valid_b, quad, calib_weight=calib_weight, power_gamma=power_gamma)
           if calibrate_quadrants else raw.copy())
    return {"p_full": p_full, "p_debiased": p_deb, "p_sub": p_sub, "raw_proba": raw, "cal_proba": cal}
