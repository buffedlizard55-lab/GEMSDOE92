"""BLINDFAULT lane: conspicuity-reweighted (covariate-shift-corrected), subsurface-only
Leave-One-Quadrant-Out fault model.

Pre-registration: ``docs/HYPOTHESES_20261025_BLINDFAULT.md`` (written before this file).

Mechanism
---------
The USGS/INGENIOUS *catalogue* is a scarp catalogue: faults with a preserved
topographic scarp were mapped, faults without one were not. The competition's
hidden truth (new faults absent from the catalogue) is therefore biased toward
topographically subtle structures. A classifier trained on all catalogue pixels
with equal weight learns conspicuity. BLINDFAULT corrects the covariate shift by

* using ONLY subsurface / potential-field / geodetic features (never slope), and
* weighting each positive training pixel by ``w = 1 / (eps + c)`` where ``c`` in
  ``[0, 1]`` is the rank-normalised local maximum of log-slope -- the
  importance weight of a target domain concentrated on low-conspicuity faults
  (Shimodaira 2000; Sugiyama et al. 2007).

Everything catalogue-derived (the label mask and the negative buffer) is built
from the mask handed in by the caller, so strict draw-blind holdout training is
a matter of passing ``visible`` and the hidden collar as ``excluded_mask``.

Memory discipline: the sandbox has 3 GB.  Bands are read one at a time; the
footprint feature matrix is ``(N_foot, n_features) float32``.
"""
from __future__ import annotations

import numpy as np
import rasterio
from scipy.ndimage import (
    binary_dilation,
    distance_transform_edt,
    gaussian_filter,
    gaussian_gradient_magnitude,
    maximum_filter,
)
from scipy.stats import rankdata
from sklearn.ensemble import HistGradientBoostingClassifier

from .breakline import spaced_top_mask

# 1-based band numbers in training_features.tif (verified against the README band audit)
BAND = dict(rtp=2, tmi_hg=3, geod_shear=7, geod_dilat=8, tmi_vg=9, grav_vg=11, det_elev=12,
            grav_anom=13, depth_base=15, cond_surf=17, grav_hg_ew=18, slope=19)

SUBSURFACE_FEATURES: tuple[str, ...] = (
    "f01_rtp_hgm_s15",          # |grad| of RTP magnetic anomaly, sigma 1.5 px
    "f02_tmi_tilt_angle",       # atan2(TMI vertical gradient, TMI horizontal gradient)
    "f03_grav_hgm_s15",         # |grad| isostatic gravity anomaly
    "f04_grav_vg",              # isostatic gravity vertical gradient (signed)
    "f05_grav_hg_ew",           # signed E-W gravity horizontal derivative (footwall polarity)
    "f06_base_hgm_s15",         # |grad| depth-to-basement (concealed basement step)
    "f07_log_depth_base",       # cover thickness (log)
    "f08_mt_hgm_s15",           # |grad| MT conductivity (clay-cap margin)
    "f09_mt_cond",              # MT conductivity level
    "f10_geod_dilat",           # geodetic dilatation rate (signed)
    "f11_geod_shear",           # geodetic shear strain rate
    "f12_det_elev_lp_s10",      # low-pass detrended elevation (basin/range context only)
)
TOPO_FEATURE = "f13_log_slope"   # used ONLY by the `blindtopo` ablation arm

__all__ = ["BAND", "SUBSURFACE_FEATURES", "TOPO_FEATURE", "read_band", "conspicuity",
           "compute_features", "positive_weights", "fit_predict_loqo_weighted",
           "emit_dots", "spaced_top_mask"]


def read_band(path, band: int) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(int(band)).astype(np.float32)


def _clean(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    a = np.asarray(a, np.float32)
    ok = valid & np.isfinite(a) & (a > -1e30)
    fill = np.float32(np.median(a[ok])) if ok.any() else np.float32(0.0)
    return np.where(ok, a, fill).astype(np.float32)


def _hgm(a: np.ndarray, valid: np.ndarray, sigma: float) -> np.ndarray:
    g = gaussian_gradient_magnitude(_clean(a, valid).astype(np.float64), sigma=sigma, mode="nearest")
    return np.where(valid, g, 0.0).astype(np.float32)


def conspicuity(slope: np.ndarray, valid: np.ndarray, size: int = 5) -> np.ndarray:
    """Rank-normalised 5x5 local maximum of log(1+slope) on valid cells, in [0,1]."""
    ls = np.log1p(np.maximum(_clean(slope, valid), 0.0))
    lm = maximum_filter(ls, size=size, mode="nearest")
    c = np.zeros(slope.shape, np.float32)
    v = lm[valid]
    c[valid] = (rankdata(v, method="average") - 1.0) / max(v.size - 1, 1)
    return c


def compute_features(stack_path, footprint: np.ndarray) -> dict:
    """Return dict(valid, X_foot[(N_foot, 13)], names, conspicuity)."""
    foot = np.asarray(footprint, bool)
    rtp = read_band(stack_path, BAND["rtp"])
    slope = read_band(stack_path, BAND["slope"])
    valid = foot & np.isfinite(rtp) & (rtp > -1e30) & np.isfinite(slope) & (slope > -1e30)
    foot_idx = np.flatnonzero(foot)
    names = list(SUBSURFACE_FEATURES) + [TOPO_FEATURE]
    X = np.zeros((foot_idx.size, len(names)), np.float32)

    def put(col, arr2d):
        flat = np.asarray(arr2d, np.float32).ravel()[foot_idx]
        X[:, col] = np.nan_to_num(flat, nan=0.0, posinf=0.0, neginf=0.0)

    put(0, _hgm(rtp, valid, 1.5)); del rtp
    hg = _clean(read_band(stack_path, BAND["tmi_hg"]), valid)
    vg = _clean(read_band(stack_path, BAND["tmi_vg"]), valid)
    put(1, np.where(valid, np.arctan2(vg, np.maximum(hg, 1e-6)), 0.0)); del hg, vg
    ga = read_band(stack_path, BAND["grav_anom"]); put(2, _hgm(ga, valid, 1.5)); del ga
    put(3, _clean(read_band(stack_path, BAND["grav_vg"]), valid))
    put(4, _clean(read_band(stack_path, BAND["grav_hg_ew"]), valid))
    db = _clean(read_band(stack_path, BAND["depth_base"]), valid)
    put(5, _hgm(db, valid, 1.5)); put(6, np.log1p(np.maximum(db, 0.0))); del db
    mt = _clean(read_band(stack_path, BAND["cond_surf"]), valid)
    put(7, _hgm(mt, valid, 1.5)); put(8, mt); del mt
    put(9, _clean(read_band(stack_path, BAND["geod_dilat"]), valid))
    put(10, _clean(read_band(stack_path, BAND["geod_shear"]), valid))
    de = _clean(read_band(stack_path, BAND["det_elev"]), valid)
    put(11, gaussian_filter(de, sigma=10.0, mode="nearest")); del de
    put(12, np.log1p(np.maximum(_clean(slope, valid), 0.0)))
    c = conspicuity(slope, valid)
    del slope
    return dict(valid=valid, X_foot=X, names=names, conspicuity=c)


def positive_weights(c_pos: np.ndarray, eps: float = 0.1) -> np.ndarray:
    """Importance weights for a target domain concentrated on low conspicuity."""
    return (1.0 / (float(eps) + np.asarray(c_pos, np.float64))).astype(np.float32)


def fit_predict_loqo_weighted(X_foot, footprint, valid, quad, label_mask, *, feature_cols,
                              pos_weight_field=None, excluded_mask=None, guard_px=12,
                              neg_buffer_px=5.0, neg_pos_ratio=3, seed=20261025,
                              max_iter=120) -> np.ndarray:
    """4-quadrant LOQO HGB probability; positives optionally importance-weighted.

    ``pos_weight_field`` is a 2-D field of per-pixel positive weights (None => uniform).
    Weighted positives are rescaled so their total equals the number of negatives
    (balanced prior), exactly as the unweighted ablation does.
    """
    foot = np.asarray(footprint, bool)
    valid_b = np.asarray(valid, bool) & foot
    lbl = np.asarray(label_mask, bool) & valid_b
    excl = np.asarray(excluded_mask, bool) if excluded_mask is not None else np.zeros_like(foot)
    cols = list(feature_cols)
    d_lbl = distance_transform_edt(~lbl)
    row = np.full(foot.shape, -1, np.int32)
    row[foot] = np.arange(int(foot.sum()), dtype=np.int32)
    proba = np.zeros(foot.shape, np.float32)
    for q in (0, 1, 2, 3):
        target = (quad == q) & valid_b
        if not target.any():
            continue
        guard = binary_dilation(quad == q, iterations=int(guard_px)) if guard_px > 0 else (quad == q)
        train_dom = valid_b & (quad >= 0) & (quad != q) & ~guard & ~excl
        pos = train_dom & lbl
        neg_pool = train_dom & ~lbl & (d_lbl > float(neg_buffer_px))
        pos_idx, neg_idx = row[pos], row[neg_pool]
        if pos_idx.size == 0 or neg_idx.size == 0:
            raise ValueError(f"quadrant {q}: empty class pos={pos_idx.size} neg={neg_idx.size}")
        rng = np.random.default_rng(int(seed) + 97 * q)
        n_neg = min(int(neg_idx.size), int(pos_idx.size) * int(neg_pos_ratio))
        neg_sel = np.sort(rng.choice(neg_idx, size=n_neg, replace=False)) if n_neg < neg_idx.size else neg_idx
        tr = np.concatenate([pos_idx, neg_sel])
        y = np.concatenate([np.ones(pos_idx.size, np.int8), np.zeros(neg_sel.size, np.int8)])
        if pos_weight_field is not None:
            wp = np.asarray(pos_weight_field, np.float32)[pos].astype(np.float64)
        else:
            wp = np.ones(pos_idx.size, np.float64)
        wp = wp * (float(neg_sel.size) / float(wp.sum()))
        sw = np.concatenate([wp, np.ones(neg_sel.size)]).astype(np.float32)
        clf = HistGradientBoostingClassifier(
            loss="log_loss", learning_rate=0.08, max_iter=int(max_iter), max_leaf_nodes=31,
            max_depth=5, min_samples_leaf=min(200, max(10, int(tr.size // 40))),
            l2_regularization=10.0, early_stopping=False, random_state=int(seed) + q)
        clf.fit(X_foot[tr][:, cols], y, sample_weight=sw)
        te = row[target]
        out = np.empty(te.size, np.float32)
        for s in range(0, te.size, 250_000):
            e = min(s + 250_000, te.size)
            out[s:e] = clf.predict_proba(X_foot[te[s:e]][:, cols])[:, 1]
        proba[target] = out
    return proba


def emit_dots(surface: np.ndarray, allowed: np.ndarray, n: int = 37_654,
              min_dist_px: float = 2.8) -> np.ndarray:
    m = spaced_top_mask(surface, allowed, int(n), min_dist_px=min_dist_px, cand_cap=900_000)
    if int(m.sum()) != int(n):
        raise RuntimeError(f"spacing floor exhausted the pool: {int(m.sum())} != {n}")
    return m
