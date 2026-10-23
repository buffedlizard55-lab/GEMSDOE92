"""Deterministic parent Poisson thinning and exact expected-DTI refill primitives.

Adapted byte-for-byte from the earlier GEMSDOE88 PRUNE builder; this module
contains only local array algorithms and never contacts external services.
"""
from __future__ import annotations
from collections import deque
import numpy as np
from scipy.ndimage import label as ndi_label
from gems57 import metric

def select_exact_marginal_dti_add(
    base_mask: np.ndarray,
    cand_mask: np.ndarray,
    w: np.ndarray,
    n_add: int,
    alpha: float = metric.ALPHA,
    beta: float = metric.BETA,
) -> np.ndarray:
    """Greedily add n_add dots from cand_mask maximizing exact expected DTI at every step.

    Maintains exact per-cell coverage C_A(g) = max_{x in A} k(||g - x||) and updates
    the exact candidate dT array locally inside the 6-px interaction neighborhood on
    every step, taking the exact global argmax across all remaining candidates.
    """
    state = np.asarray(base_mask, dtype=bool).copy()
    if n_add <= 0:
        return state
    H, W = state.shape
    w64 = np.asarray(w, dtype=np.float64)
    w_tot = float(w64.sum())

    # Initial coverage C_A and scalars T, S, M
    cov = np.zeros((H, W), dtype=np.float64)
    by, bx = np.nonzero(state)
    for dy, dx, kw in zip(metric.OFF_DY, metric.OFF_DX, metric.OFF_K):
        ny, nx = by + int(dy), bx + int(dx)
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        np.maximum.at(cov, (ny[ok], nx[ok]), kw)
    t_cur = float((w64 * cov).sum())
    m_base = np.zeros(len(by), dtype=np.float64)
    for dy, dx, kw in zip(metric.OFF_DY, metric.OFF_DX, metric.OFF_K):
        ny, nx = by + int(dy), bx + int(dx)
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        m_base[ok] = np.maximum(m_base[ok], w64[ny[ok], nx[ok]] * kw)
    m_cur = float(m_base.sum())
    s_cur = float(len(by))

    cy, cx = np.nonzero(cand_mask & ~state)
    if len(cy) < n_add:
        raise ValueError(f"Candidate pool ({len(cy)}) smaller than requested refill ({n_add})")

    # Map grid position -> candidate index for instant local invalidation within 6 px
    cand_id_grid = np.full((H, W), -1, dtype=np.int32)
    cand_id_grid[cy, cx] = np.arange(len(cy), dtype=np.int32)

    m_cand = np.zeros(len(cy), dtype=np.float64)
    dT = np.zeros(len(cy), dtype=np.float64)
    for dy, dx, kw in zip(metric.OFF_DY, metric.OFF_DX, metric.OFF_K):
        ny, nx = cy + int(dy), cx + int(dx)
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        wv = w64[ny[ok], nx[ok]]
        m_cand[ok] = np.maximum(m_cand[ok], wv * kw)
        dT[ok] += wv * np.maximum(0.0, kw - cov[ny[ok], nx[ok]])

    chosen = np.zeros(len(cy), dtype=bool)
    off_dy = metric.OFF_DY.astype(np.int64)
    off_dx = metric.OFF_DX.astype(np.int64)
    off_k = metric.OFF_K.astype(np.float64)

    for _ in range(n_add):
        d_cur = alpha * (t_cur + s_cur - m_cur) + beta * w_tot + metric.EPS
        next_dti = (t_cur + dT) / (d_cur + alpha * (dT + 1.0 - m_cand))
        next_dti[chosen] = -1.0
        best = int(np.argmax(next_dti))
        chosen[best] = True
        ry, rx = int(cy[best]), int(cx[best])
        state[ry, rx] = True

        # Update cov around (ry, rx) and recompute exact dT for nearby candidates (|dr|,|dc|<=6)
        ny = ry + off_dy
        nx = rx + off_dx
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        ny, nx, kw = ny[ok], nx[ok], off_k[ok]
        old_c = cov[ny, nx]
        upd = kw > old_c
        if np.any(upd):
            uy, ux, uk, uold = ny[upd], nx[upd], kw[upd], old_c[upd]
            cov[uy, ux] = uk
            t_cur += float((w64[uy, ux] * (uk - uold)).sum())

        s_cur += 1.0
        m_cur += float(m_cand[best])

        y0, y1 = max(0, ry - 6), min(H, ry + 7)
        x0, x1 = max(0, rx - 6), min(W, rx + 7)
        sub_ids = cand_id_grid[y0:y1, x0:x1].ravel()
        sub_ids = sub_ids[sub_ids >= 0]
        if sub_ids.size:
            sub_ids = sub_ids[~chosen[sub_ids]]
        if sub_ids.size:
            sy, sx = cy[sub_ids], cx[sub_ids]
            new_dt = np.zeros(len(sub_ids), dtype=np.float64)
            for dy_i, dx_i, kw_i in zip(off_dy, off_dx, off_k):
                nny, nnx = sy + int(dy_i), sx + int(dx_i)
                ook = (nny >= 0) & (nny < H) & (nnx >= 0) & (nnx < W)
                new_dt[ook] += w64[nny[ook], nnx[ook]] * np.maximum(
                    0.0, kw_i - cov[nny[ook], nnx[ook]]
                )
            dT[sub_ids] = new_dt

    return state

def dot_thin(mask: np.ndarray, min_dist: float) -> np.ndarray:
    """Deterministic geodesic Poisson-disk thinning of binary ridge mask (GEMSDOE25 exact algorithm)."""
    mask = np.asarray(mask, dtype=bool)
    if min_dist <= 1.0 or not mask.any():
        return mask.copy()
    H, W = mask.shape
    pad = int(np.ceil(min_dist)) + 1
    Wp, Hp = W + 2 * pad, H + 2 * pad
    padded = np.zeros((Hp, Wp), dtype=bool)
    padded[pad : pad + H, pad : pad + W] = mask
    flat = bytearray(padded.tobytes())
    visited, blocked, kept = bytearray(Hp * Wp), bytearray(Hp * Wp), bytearray(Hp * Wp)
    r = int(np.ceil(min_dist))
    lim = min_dist * min_dist
    disc = [
        dy * Wp + dx
        for dy in range(-r, r + 1)
        for dx in range(-r, r + 1)
        if dy * dy + dx * dx < lim
    ]
    nbr = (-Wp - 1, -Wp, -Wp + 1, -1, 1, Wp - 1, Wp, Wp + 1)
    comp, _ = ndi_label(padded, structure=np.ones((3, 3), dtype=int))
    fc = comp.ravel()
    order = np.flatnonzero(fc)
    _, first = np.unique(fc[order], return_index=True)
    for seed in order[np.sort(first)].tolist():
        if visited[seed]:
            continue
        visited[seed] = 1
        queue = deque((seed,))
        while queue:
            q = queue.popleft()
            if not blocked[q]:
                kept[q] = 1
                for o in disc:
                    blocked[q + o] = 1
            for o in nbr:
                nb = q + o
                if flat[nb] and not visited[nb]:
                    visited[nb] = 1
                    queue.append(nb)
    out = np.frombuffer(bytes(kept), dtype=np.uint8).reshape(Hp, Wp).astype(bool)
    return out[pad : pad + H, pad : pad + W]
