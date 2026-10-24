"""SPRINGALIGN lane surface: geothermal spring-pair strike alignment.

Points (row, col, temp_c) of hot springs/wells from the pinned GDR
INGENIOUS wellspring table.  For every pair 10-60 px apart, the segment
between them (extended 25% of its length at each end, capped 15 px) is a
candidate fault-strike line: geothermal upflow localises on fracture
permeability, so springs fed by one blind fault align along its strike
even with no scarp / magnetic expression.  Votes accumulate
sqrt(Ti*Tj)/100 along each segment; the surface is the percentile rank.

This is alignment geometry, not spring density/proximity (never built
in this repo; named untested in docs/NEXT_STEPS.md item 4).

Mimics: lithologic contacts, paleochannels, aqueducts, playa shorelines.
Nothing here reads the fault catalogue.  Pure array math.
"""
from __future__ import annotations
import numpy as np
from scipy.spatial import cKDTree
from .breakline import percentile_rank, spaced_top_mask  # noqa: F401  (re-export)

MIN_SEP_PX, MAX_SEP_PX, EXT_FRAC, EXT_CAP_PX = 10.0, 60.0, 0.25, 15.0

def hot_points(rows, cols, temps, min_temp_c=40.0):
    """Dedupe by pixel (max temp), keep temp >= min_temp_c. Deterministic."""
    best = {}
    for r, c, t in zip(rows, cols, temps):
        if not np.isfinite(t) or t < min_temp_c:
            continue
        k = (int(r), int(c))
        if k not in best or t > best[k]:
            best[k] = float(t)
    pts = sorted(best.items())  # row-major deterministic
    rc = np.array([k for k, _ in pts], dtype=float) if pts else np.empty((0, 2))
    tt = np.array([v for _, v in pts], dtype=float) if pts else np.empty(0)
    return rc, tt

def alignment_votes(shape, points_rc, temps):
    """Accumulated strike votes (float32). points_rc: (n,2) float (row,col)."""
    votes = np.zeros(shape, np.float64)
    n = len(points_rc)
    if n < 2:
        return votes.astype(np.float32), {"n_points": int(n), "n_pairs": 0}
    tree = cKDTree(points_rc)
    pairs = tree.query_pairs(MAX_SEP_PX)
    used = 0
    H, W = shape
    for i, j in sorted(pairs):
        d = float(np.hypot(*(points_rc[i] - points_rc[j])))
        if d < MIN_SEP_PX:
            continue
        used += 1
        w = float(np.sqrt(temps[i] * temps[j]) / 100.0)
        direction = (points_rc[j] - points_rc[i]) / d
        ext = min(EXT_FRAC * d, EXT_CAP_PX)
        a = points_rc[i] - direction * ext
        b = points_rc[j] + direction * ext
        steps = max(2, int(np.ceil(d + 2 * ext)) + 1)
        line = a[None, :] + (b - a)[None, :] * (np.arange(steps) / (steps - 1))[:, None]
        yy = np.clip(np.rint(line[:, 0]).astype(int), 0, H - 1)
        xx = np.clip(np.rint(line[:, 1]).astype(int), 0, W - 1)
        np.add.at(votes, (yy, xx), w)
    return votes.astype(np.float32), {"n_points": int(n), "n_pairs": int(used)}

def lane_surface(shape, points_rc, temps, valid):
    votes, meta = alignment_votes(shape, points_rc, temps)
    valid = np.asarray(valid, bool)
    s_raw = np.where(valid, votes, 0.0).astype(np.float32)
    return {"S_raw": s_raw, "S_pct": percentile_rank(s_raw, valid), **meta}

def corridor_surface(shape, points_rc, temps, valid, sigma_px=3.0):
    """Gaussian-corridor variant: votes smoothed sigma_px, re-ranked.

    Dots sit within ~2 sigma of an alignment line, not only on its 1-px
    rasterisation -- the fault-zone corridor, and the spaced-emission
    pool a 1-px line cannot supply at f45.
    """
    from scipy.ndimage import gaussian_filter
    base = lane_surface(shape, points_rc, temps, valid)
    sm = gaussian_filter(base["S_raw"], float(sigma_px)).astype(np.float32)
    valid = np.asarray(valid, bool)
    sm = np.where(valid, sm, 0.0).astype(np.float32)
    return {"S_raw": sm, "S_pct": percentile_rank(sm, valid),
            "n_points": base["n_points"], "n_pairs": base["n_pairs"]}
