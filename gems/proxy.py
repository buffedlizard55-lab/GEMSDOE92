"""Catalogue hide-and-recover PROXY.

REPORT ONLY. This is never a gate (brief section 6). It is a local comparator
that answers one question cheaply: *does this candidate rank fault-like pixels
differently from that one?* It cannot answer "what will the leaderboard say".

Why it is only a proxy, in the brief's own numbers: the same test correlated
-0.87 to +0.54 with live scores across 12-14 files, and lidar03 passed it and
then scored 0.1152 live. Treat the output as a preference ordering with wide
error bars, nothing more.

It uses the known-fault catalogue as withheld positives. That is legitimate:
the catalogue is training/known data, not the public-test labels. The function
never looks at a leaderboard and never touches test-region labels.
"""

from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree

RADIUS_PX = 3.0


def split_positives(ys, xs, frac=0.25, seed=0):
    """Deterministically withhold a fraction of catalogue positives."""
    ys = np.asarray(ys)
    xs = np.asarray(xs)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(ys))
    n_hold = max(1, int(round(frac * len(ys))))
    hold, keep = perm[:n_hold], perm[n_hold:]
    return (ys[keep], xs[keep]), (ys[hold], xs[hold])


def _recovered(dots_ys, dots_xs, truth_ys, truth_xs, radius=RADIUS_PX):
    """Fraction of truth positives with at least one dot within `radius`."""
    if len(truth_ys) == 0:
        return float("nan")
    if len(dots_ys) == 0:
        return 0.0
    tree = cKDTree(np.c_[dots_ys, dots_xs])
    d, _ = tree.query(np.c_[truth_ys, truth_xs], k=1)
    return float((d <= radius).mean())


def _bootstrap_ci(values, stat=np.mean, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return (float("nan"), float("nan"))
    idx = rng.integers(0, arr.size, size=(n, arr.size))
    stats = stat(arr[idx], axis=1)
    return (float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5)))


def evaluate(dots_ys, dots_xs, cat_ys, cat_xs, frac=0.25, seed=0,
             n_boot=2000, min_dots_from_keep: bool = True) -> dict:
    """Hide a catalogue fraction, then score candidate dots against it.

    Returns recall on withheld positives with a 95% bootstrap CI over withheld
    positives, plus the count. Labelled PROXY everywhere it is reported.
    """
    keep, hold = split_positives(cat_ys, cat_xs, frac=frac, seed=seed)
    dots_ys = np.asarray(dots_ys)
    dots_xs = np.asarray(dots_xs)

    if min_dots_from_keep:
        # do not let a candidate cheat by simply re-emitting the catalogue
        tree = cKDTree(np.c_[keep[0], keep[1]])
        d, _ = tree.query(np.c_[dots_ys, dots_xs], k=1) if len(dots_ys) else (np.empty(0), None)
        free = d > 2.0 if len(d) else np.ones(0, bool)
        dots_ys, dots_xs = dots_ys[free], dots_xs[free]

    hits = _hits(dots_ys, dots_xs, hold[0], hold[1])
    lo, hi = _bootstrap_ci(hits, n=n_boot, seed=seed)
    return {
        "evidence": "PROXY",
        "n_withheld": int(len(hold[0])),
        "recall_at_3px": float(hits.mean()) if hits.size else float("nan"),
        "ci95": (lo, hi),
        "n_dots_scored": int(len(dots_ys)),
        "note": "catalogue holdout only; weakly related to the live metric",
    }


def _hits(dots_ys, dots_xs, truth_ys, truth_xs, radius=RADIUS_PX):
    if len(truth_ys) == 0:
        return np.empty(0, float)
    if len(dots_ys) == 0:
        return np.zeros(len(truth_ys), float)
    tree = cKDTree(np.c_[dots_ys, dots_xs])
    d, _ = tree.query(np.c_[truth_ys, truth_xs], k=1)
    return (d <= radius).astype(float)


def leakage_canary(feature: np.ndarray, truth_mask: np.ndarray,
                   footprint: np.ndarray | None = None) -> dict:
    """Single-feature AUC. AUC > 0.90 means stop and investigate (brief 6).

    A feature that separates truth from background almost perfectly is a
    leak or a bug, not a discovery.
    """
    pos = truth_mask.astype(bool)
    if footprint is not None:
        valid = footprint & np.isfinite(feature)
    else:
        valid = np.isfinite(feature)
    pos = pos & valid
    neg = valid & ~pos
    if pos.sum() == 0 or neg.sum() == 0:
        return {"evidence": "PROXY", "auc": None, "status": "INSUFFICIENT_DATA"}
    # subsample negatives to keep memory sane
    rng = np.random.default_rng(0)
    neg_idx = np.flatnonzero(neg.ravel())
    if neg_idx.size > 200_000:
        neg_idx = rng.choice(neg_idx, 200_000, replace=False)
    p = feature[pos].ravel()
    n = feature.ravel()[neg_idx]
    # rank-based AUC via Mann-Whitney
    allv = np.r_[p, n]
    order = np.argsort(allv, kind="stable")
    ranks = np.empty(len(allv), float)
    ranks[order] = np.arange(1, len(allv) + 1)
    # average ranks for ties
    import numpy as _np
    uniq, inv, counts = _np.unique(allv, return_inverse=True, return_counts=True)
    sums = _np.bincount(inv, weights=ranks)
    ranks = (sums / counts)[inv]
    auc = (ranks[:len(p)].sum() - len(p) * (len(p) + 1) / 2) / (len(p) * len(n))
    return {
        "evidence": "PROXY",
        "auc": float(auc),
        "status": "STOP_AND_INVESTIGATE" if auc > 0.90 else "ok",
    }
