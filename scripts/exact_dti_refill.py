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


def select_exact_marginal_dti_drop(
    base_mask: np.ndarray,
    removable_mask: np.ndarray,
    w: np.ndarray,
    n_drop: int,
    alpha: float = metric.ALPHA,
    beta: float = metric.BETA,
) -> np.ndarray:
    """Greedily drop n_drop dots from (base_mask & removable_mask) maximizing exact expected DTI.

    Maintains per-pixel best coverage c1(g), unique-owner index u1(g), and second-best
    coverage c2(g) across the R=3 px triangular kernel. Whenever two or more active dots
    achieve the same maximum kernel weight at g, c2(g) == c1(g), so removing either dot
    leaves coverage unchanged (c1 - c2 == 0). After each removal at (ry, rx), (c1, u1, c2)
    is recomputed on the 7x7 patch [ry-3:ry+4, rx-3:rx+4] and dT_loss is recomputed from
    scratch for active dots inside [ry-6:ry+7, rx-6:rx+7], eliminating float drift.
    """
    state = np.asarray(base_mask, dtype=bool).copy()
    if n_drop <= 0:
        return state
    rem_mask = np.asarray(removable_mask, dtype=bool)
    if int((state & rem_mask).sum()) < n_drop:
        raise ValueError(
            f"Removable pool ({int((state & rem_mask).sum())}) smaller than requested drop ({n_drop})"
        )

    H, W = state.shape
    w64 = np.asarray(w, dtype=np.float64)
    w_tot = float(w64.sum())
    off_dy = metric.OFF_DY.astype(np.int64)
    off_dx = metric.OFF_DX.astype(np.int64)
    off_k = metric.OFF_K.astype(np.float64)

    ay, ax = np.nonzero(state)
    n_act = len(ay)
    dot_id_grid = np.full((H, W), -1, dtype=np.int32)
    dot_id_grid[ay, ax] = np.arange(n_act, dtype=np.int32)
    active = np.ones(n_act, dtype=bool)
    can_drop = rem_mask[ay, ax].copy()

    c1 = np.zeros((H, W), dtype=np.float64)
    u1 = np.full((H, W), -1, dtype=np.int32)
    c2 = np.zeros((H, W), dtype=np.float64)
    m_dot = np.zeros(n_act, dtype=np.float64)

    for dy, dx, kw in zip(off_dy, off_dx, off_k):
        dy_i, dx_i, kw_f = int(dy), int(dx), float(kw)
        ys0, ys1 = max(0, -dy_i), min(H, H - dy_i)
        xs0, xs1 = max(0, -dx_i), min(W, W - dx_i)
        yd0, yd1 = ys0 + dy_i, ys1 + dy_i
        xd0, xd1 = xs0 + dx_i, xs1 + dx_i

        src_ids = dot_id_grid[ys0:ys1, xs0:xs1]
        has_dot = src_ids >= 0
        if not np.any(has_dot):
            continue
        c1_sub = c1[yd0:yd1, xd0:xd1]
        u1_sub = u1[yd0:yd1, xd0:xd1]
        c2_sub = c2[yd0:yd1, xd0:xd1]

        better1 = has_dot & (kw_f > c1_sub)
        c2_new = np.where(better1, c1_sub, np.where(has_dot & (kw_f > c2_sub), kw_f, c2_sub))
        u1_new = np.where(better1, src_ids, u1_sub)
        c1_new = np.where(better1, kw_f, c1_sub)
        c1[yd0:yd1, xd0:xd1] = c1_new
        u1[yd0:yd1, xd0:xd1] = u1_new
        c2[yd0:yd1, xd0:xd1] = c2_new

    for dy, dx, kw in zip(off_dy, off_dx, off_k):
        ny, nx = ay + int(dy), ax + int(dx)
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        m_dot[ok] = np.maximum(m_dot[ok], w64[ny[ok], nx[ok]] * float(kw))

    t_cur = float((w64 * c1).sum())
    s_cur = float(n_act)
    m_cur = float(m_dot.sum())

    dT_loss = np.zeros(n_act, dtype=np.float64)
    valid_u1 = u1 >= 0
    np.add.at(dT_loss, u1[valid_u1], (w64 * (c1 - c2))[valid_u1])

    for _ in range(n_drop):
        elig = active & can_drop
        t_next = t_cur - dT_loss
        d_next = alpha * (t_next + (s_cur - 1.0) - (m_cur - m_dot)) + beta * w_tot + metric.EPS
        next_dti = np.where(elig, t_next / d_next, -1.0)
        best = int(np.argmax(next_dti))
        if not elig[best]:
            raise RuntimeError("No eligible dot available during exact marginal DTI drop")

        active[best] = False
        ry, rx = int(ay[best]), int(ax[best])
        state[ry, rx] = False
        dot_id_grid[ry, rx] = -1

        py0, py1 = max(0, ry - 3), min(H, ry + 4)
        px0, px1 = max(0, rx - 3), min(W, rx + 4)
        old_patch_t = float((w64[py0:py1, px0:px1] * c1[py0:py1, px0:px1]).sum())

        ph, pw = py1 - py0, px1 - px0
        nc1 = np.zeros((ph, pw), dtype=np.float64)
        nu1 = np.full((ph, pw), -1, dtype=np.int32)
        nc2 = np.zeros((ph, pw), dtype=np.float64)

        sy0, sy1 = max(0, py0 - 3), min(H, py1 + 3)
        sx0, sx1 = max(0, px0 - 3), min(W, px1 + 3)
        local_ids = dot_id_grid[sy0:sy1, sx0:sx1].ravel()
        local_ids = local_ids[local_ids >= 0]
        for lid in local_ids:
            ly, lx = int(ay[lid]) - py0, int(ax[lid]) - px0
            for dy_i, dx_i, kw_i in zip(off_dy, off_dx, off_k):
                gy, gx = ly + int(dy_i), lx + int(dx_i)
                if 0 <= gy < ph and 0 <= gx < pw:
                    if kw_i > nc1[gy, gx]:
                        nc2[gy, gx] = nc1[gy, gx]
                        nc1[gy, gx] = kw_i
                        nu1[gy, gx] = int(lid)
                    elif kw_i > nc2[gy, gx]:
                        nc2[gy, gx] = kw_i

        c1[py0:py1, px0:px1] = nc1
        u1[py0:py1, px0:px1] = nu1
        c2[py0:py1, px0:px1] = nc2
        new_patch_t = float((w64[py0:py1, px0:px1] * nc1).sum())

        t_cur += new_patch_t - old_patch_t
        s_cur -= 1.0
        m_cur -= float(m_dot[best])

        # Recompute dT_loss from scratch for active dots within 6 px of (ry, rx)
        uy0, uy1 = max(0, ry - 6), min(H, ry + 7)
        ux0, ux1 = max(0, rx - 6), min(W, rx + 7)
        upd_ids = dot_id_grid[uy0:uy1, ux0:ux1].ravel()
        upd_ids = upd_ids[upd_ids >= 0]
        if upd_ids.size:
            upd_ids = upd_ids[can_drop[upd_ids]]
        if upd_ids.size:
            ly_arr = ay[upd_ids]
            lx_arr = ax[upd_ids]
            recomp = np.zeros(len(upd_ids), dtype=np.float64)
            for dy_i, dx_i, _ in zip(off_dy, off_dx, off_k):
                nny = ly_arr + int(dy_i)
                nnx = lx_arr + int(dx_i)
                ook = (nny >= 0) & (nny < H) & (nnx >= 0) & (nnx < W)
                if np.any(ook):
                    owners = u1[nny[ook], nnx[ook]]
                    match = owners == upd_ids[ook]
                    if np.any(match):
                        idx_sub = np.flatnonzero(ook)[match]
                        gy_m, gx_m = nny[idx_sub], nnx[idx_sub]
                        recomp[idx_sub] += w64[gy_m, gx_m] * (c1[gy_m, gx_m] - c2[gy_m, gx_m])
            dT_loss[upd_ids] = recomp

    return state


def select_exact_marginal_dti_add_spaced(
    base_mask: np.ndarray,
    cand_mask: np.ndarray,
    w: np.ndarray,
    n_add: int,
    min_nn: float = 1.41421356,
    alpha: float = metric.ALPHA,
    beta: float = metric.BETA,
) -> np.ndarray:
    """Greedily add n_add dots maximizing exact expected DTI while enforcing min_nn spacing.

    Prevents degenerate 1-px cardinal stacking inside the R=3 px DTI kernel while
    evaluating the exact global argmax of expected DTI at every step.
    """
    state = np.asarray(base_mask, dtype=bool).copy()
    if n_add <= 0:
        return state
    H, W = state.shape
    w64 = np.asarray(w, dtype=np.float64)
    w_tot = float(w64.sum())

    br = int(np.ceil(min_nn)) if min_nn > 0 else 0
    lim2 = float(min_nn - 1e-9) ** 2 if min_nn > 0 else 0.0
    block_offs = [
        (dy, dx)
        for dy in range(-br, br + 1)
        for dx in range(-br, br + 1)
        if (dy != 0 or dx != 0) and (dy * dy + dx * dx < lim2)
    ]

    elig_cand = np.asarray(cand_mask, dtype=bool) & ~state
    if block_offs:
        for bdy, bdx in block_offs:
            ys0, ys1 = max(0, -bdy), min(H, H - bdy)
            xs0, xs1 = max(0, -bdx), min(W, W - bdx)
            elig_cand[ys0 + bdy : ys1 + bdy, xs0 + bdx : xs1 + bdx] &= ~state[ys0:ys1, xs0:xs1]

    cy, cx = np.nonzero(elig_cand)
    if len(cy) < n_add:
        raise ValueError(
            f"Spaced candidate pool ({len(cy)}) smaller than requested additions ({n_add})"
        )

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

    blocked = np.zeros(len(cy), dtype=bool)
    off_dy = metric.OFF_DY.astype(np.int64)
    off_dx = metric.OFF_DX.astype(np.int64)
    off_k = metric.OFF_K.astype(np.float64)

    for step in range(n_add):
        d_cur = alpha * (t_cur + s_cur - m_cur) + beta * w_tot + metric.EPS
        next_dti = (t_cur + dT) / (d_cur + alpha * (dT + 1.0 - m_cand))
        next_dti[blocked] = -1.0
        best = int(np.argmax(next_dti))
        if blocked[best] or next_dti[best] < 0.0:
            raise ValueError(
                f"Spaced refill exhausted after {step}/{n_add} additions (min_nn={min_nn:.4f})"
            )
        blocked[best] = True
        ry, rx = int(cy[best]), int(cx[best])
        state[ry, rx] = True

        for bdy, bdx in block_offs:
            ny2, nx2 = ry + bdy, rx + bdx
            if 0 <= ny2 < H and 0 <= nx2 < W:
                cid = int(cand_id_grid[ny2, nx2])
                if cid >= 0:
                    blocked[cid] = True

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
            sub_ids = sub_ids[~blocked[sub_ids]]
        if sub_ids.size:
            sy2, sx2 = cy[sub_ids], cx[sub_ids]
            new_dt = np.zeros(len(sub_ids), dtype=np.float64)
            for dy_i, dx_i, kw_i in zip(off_dy, off_dx, off_k):
                nny, nnx = sy2 + int(dy_i), sx2 + int(dx_i)
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
