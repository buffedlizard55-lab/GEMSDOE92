"""CONCENTRATION axis: move a fraction of the parent's dots between km-scale blocks.

Parent: R0 ``h33-h33-2-b2`` (37,654 unit-mass dots), rebuilt bit-exactly from the
pinned H19-5 -> D1.5 -> D2.8 -> SOLO -> R0 lineage before anything is moved.

What the axis changes
---------------------
Only the *block allocation* of the fixed 37,654-dot budget:

    source blocks      lowest-prior blocks, expanded upward until they can
                       supply 2x the requested number of dots
    destination blocks top quintile of blocks by prior, quota proportional
                       to the block prior

Within those two constraints the machinery is the parent's own:

* removal order = exact marginal DTI loss of deleting that dot, recomputed in
  small batches against the declared evidence weight ``w``;
* placement    = exact marginal DTI gain, step-by-step, restricted to legal
  pixels (in footprint, on H19-5 support, > 2 px from the catalogue).

So the only thing a variant changes, relative to a plain "re-refill" of the
same budget, is *which blocks* the mass is taken from and given to.

Everything is deterministic; no randomness anywhere.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt as edt

from gems57 import metric

OFF_DY = metric.OFF_DY.astype(np.int64)
OFF_DX = metric.OFF_DX.astype(np.int64)
OFF_K = metric.OFF_K.astype(np.float64)


# --------------------------------------------------------------------------
# exact state: T, M, S and the per-pixel top-2 kernel cover
# --------------------------------------------------------------------------
class DotState:
    """Exact DTI totals for a binary dot mask under a weighted evidence field."""

    def __init__(self, mask: np.ndarray, w: np.ndarray):
        self.H, self.W = mask.shape
        self.w = np.asarray(w, dtype=np.float64)
        self.mask = np.asarray(mask, dtype=bool).copy()
        self.w_tot = float(self.w.sum())
        self._rebuild()

    def _rebuild(self) -> None:
        ys, xs = np.nonzero(self.mask)
        self.ys, self.xs = ys, xs
        n = len(ys)
        self.cov1 = np.zeros((self.H, self.W))
        self.own1 = np.full((self.H, self.W), -1, dtype=np.int64)
        self.cov2 = np.zeros((self.H, self.W))
        ids = np.arange(n, dtype=np.int64)
        for dy, dx, kw in zip(OFF_DY, OFF_DX, OFF_K):
            gy, gx = ys + dy, xs + dx
            ok = (gy >= 0) & (gy < self.H) & (gx >= 0) & (gx < self.W)
            np.maximum.at(self.cov1, (gy[ok], gx[ok]), kw)
        for dy, dx, kw in zip(OFF_DY, OFF_DX, OFF_K):
            gy, gx = ys + dy, xs + dx
            ok = (gy >= 0) & (gy < self.H) & (gx >= 0) & (gx < self.W)
            gy, gx, j = gy[ok], gx[ok], ids[ok]
            sel = (kw == self.cov1[gy, gx]) & ((self.own1[gy, gx] < 0) | (j < self.own1[gy, gx]))
            self.own1[gy[sel], gx[sel]] = j[sel]
        for dy, dx, kw in zip(OFF_DY, OFF_DX, OFF_K):
            gy, gx = ys + dy, xs + dx
            ok = (gy >= 0) & (gy < self.H) & (gx >= 0) & (gx < self.W)
            gy, gx, j = gy[ok], gx[ok], ids[ok]
            sel = j != self.own1[gy, gx]
            np.maximum.at(self.cov2, (gy[sel], gx[sel]), kw)
        # per-dot M contribution  m_j = max_g w_g * k(g, j)
        self.m_dot = np.zeros(n)
        for dy, dx, kw in zip(OFF_DY, OFF_DX, OFF_K):
            gy, gx = ys + dy, xs + dx
            ok = (gy >= 0) & (gy < self.H) & (gx >= 0) & (gx < self.W)
            np.maximum.at(self.m_dot, ids[ok], self.w[gy[ok], gx[ok]] * kw)
        self.T = float((self.w * self.cov1).sum())
        self.M = float(self.m_dot.sum())
        self.S = float(n)

    # -- derived ----------------------------------------------------------
    def dti(self) -> float:
        den = metric.ALPHA * (self.T + self.S - self.M) + metric.BETA * self.w_tot
        return float(self.T / den) if den > 0 else 0.0

    def removal_loss(self) -> np.ndarray:
        """dT_rm per dot: credit that would be lost if that dot were deleted.

        A pixel's coverage only falls when the deleted dot is its unique
        arg-max, and then it falls to the second-best kernel value.
        """
        owned = self.own1 >= 0
        if not owned.any():
            return np.zeros(len(self.ys))
        oy, ox = np.nonzero(owned)
        e = self.w[oy, ox] * (self.cov1[oy, ox] - self.cov2[oy, ox])
        return np.bincount(self.own1[oy, ox], weights=e, minlength=len(self.ys))

    def delta_remove(self, j: np.ndarray, dT_rm: np.ndarray) -> np.ndarray:
        """Exact signed dDTI of deleting dots ``j`` (one at a time, from here)."""
        T, S, M, d0 = self.T, self.S, self.M, self.dti()
        den0 = metric.ALPHA * (T + S - M) + metric.BETA * self.w_tot
        T1 = T - dT_rm
        S1 = S - 1.0
        M1 = M - self.m_dot[j]
        den1 = metric.ALPHA * (T1 + S1 - M1) + metric.BETA * self.w_tot
        d1 = np.where(den1 > 0, T1 / np.maximum(den1, 1e-300), 0.0)
        return d1 - d0


def greedy_remove(state: DotState, n_remove: int, allowed: np.ndarray | None = None,
                  batch: int = 100) -> np.ndarray:
    """Remove ``n_remove`` dots with the smallest exact DTI loss, in batches.

    ``allowed`` is a per-dot boolean over the ORIGINAL dot list (the parent's
    dots, in row-major order). The ranking is refreshed every ``batch``
    removals so that the cost of deleting a cluster is not badly understated.
    Deterministic: ties break to the lower dot index. Returns the indices into
    the ORIGINAL dot list that were removed.
    """
    n0 = len(state.ys)
    alive = np.ones(n0, dtype=bool)
    orig_ids = np.arange(n0, dtype=np.int64)
    removed: list[int] = []
    remaining = n_remove
    while remaining > 0:
        sub = np.arange(len(state.ys), dtype=np.int64)
        loss = state.delta_remove(sub, state.removal_loss())
        order = sub[np.argsort(-loss, kind="stable")]
        if allowed is not None:
            ok_now = allowed[orig_ids]
            order = order[ok_now[order]]
        take = min(batch, remaining)
        if len(order) < take:
            raise ValueError("not enough allowed dots to remove")
        picked = order[:take]
        removed.extend(int(orig_ids[i]) for i in picked)
        alive[orig_ids[picked]] = False
        state.mask[state.ys[picked], state.xs[picked]] = False
        state._rebuild()
        # np.nonzero(state.mask) is row-major sorted, and orig_ids was sorted,
        # so the surviving original indices stay aligned with the rebuilt state.
        orig_ids = np.nonzero(alive)[0]
        remaining -= take
    return np.array(removed, dtype=np.int64)


# --------------------------------------------------------------------------
# blocked exact-greedy addition
# --------------------------------------------------------------------------
def allocate_quotas(weights: np.ndarray, avail: np.ndarray, total: int) -> np.ndarray:
    """Split ``total`` dots over blocks, proportional to ``weights``, capped by
    each block's available candidate pixels. Deterministic water-filling."""
    weights = np.asarray(weights, dtype=np.float64).copy()
    avail = np.asarray(avail, dtype=np.int64)
    q = np.zeros(len(weights), dtype=np.int64)
    rem = int(total)
    while rem > 0:
        room = avail - q
        if room.sum() <= 0:
            raise ValueError("destination blocks cannot absorb the requested dots")
        w = np.where(room > 0, weights, 0.0)
        if w.sum() <= 0:
            w = np.where(room > 0, 1.0, 0.0)
        share = rem * w / w.sum()
        add = np.minimum(np.floor(share).astype(np.int64), room)
        if add.sum() < rem:
            resid = share - np.floor(share)
            resid[add >= room] = -np.inf
            for i in np.argsort(-resid, kind="stable"):
                if add.sum() >= rem:
                    break
                if q[i] + add[i] < avail[i]:
                    add[i] += 1
        q += add
        new_rem = rem - int(add.sum())
        if new_rem == rem:
            for i in np.argsort(-w, kind="stable"):
                if rem <= 0:
                    break
                spare = int(avail[i] - q[i])
                if spare > 0:
                    t = min(spare, rem)
                    q[i] += t
                    rem -= t
            break
        rem = new_rem
    return q


def greedy_add_blocked(state: DotState, cand_mask: np.ndarray, n_add: int,
                       block_id: np.ndarray, capacity: np.ndarray) -> int:
    """Add ``n_add`` dots by exact marginal DTI gain, honouring per-block caps.

    ``block_id`` is an int grid giving each pixel's destination block index
    (0..n_dest-1; -1 = not a destination). ``capacity[b]`` is the maximum number
    of dots block ``b`` may receive. At every step the global arg-max over the
    *unfilled* candidates is taken, so the choice within the quota is exact.
    """
    H, W = state.H, state.W
    w64 = state.w
    cov = state.cov1
    T = state.T
    S = state.S
    M = state.M
    capacity = np.asarray(capacity, dtype=np.int64)
    n_dest = len(capacity)

    cy, cx = np.nonzero(cand_mask & ~state.mask)
    if len(cy) < n_add:
        raise ValueError(f"candidate pool ({len(cy)}) smaller than requested ({n_add})")
    cand_block = block_id[cy, cx]
    cand_id_grid = np.full((H, W), -1, dtype=np.int32)
    cand_id_grid[cy, cx] = np.arange(len(cy), dtype=np.int32)

    m_cand = np.zeros(len(cy))
    dT = np.zeros(len(cy))
    for dy, dx, kw in zip(OFF_DY, OFF_DX, OFF_K):
        ny, nx = cy + int(dy), cx + int(dx)
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        wv = w64[ny[ok], nx[ok]]
        m_cand[ok] = np.maximum(m_cand[ok], wv * kw)
        dT[ok] += wv * np.maximum(0.0, kw - cov[ny[ok], nx[ok]])

    # candidates grouped by block, so a filled block can be masked out in O(size)
    order = np.argsort(cand_block, kind="stable")
    cb_sorted = cand_block[order]
    bounds = np.searchsorted(cb_sorted, np.arange(n_dest + 1))
    filled = np.zeros(n_dest, dtype=np.int64)
    usable = np.zeros(len(cy), dtype=bool)
    for b in range(n_dest):
        s, e = bounds[b], bounds[b + 1]
        if capacity[b] > 0 and e > s:
            usable[order[s:e]] = True
    if int(usable.sum()) < n_add:
        raise ValueError("destination blocks cannot absorb the requested dots")

    chosen = np.zeros(len(cy), dtype=bool)
    placed = 0
    while placed < n_add:
        d_cur = metric.ALPHA * (T + S - M) + metric.BETA * state.w_tot + metric.EPS
        nxt = (T + dT) / (d_cur + metric.ALPHA * (dT + 1.0 - m_cand))
        nxt = np.where(usable & ~chosen, nxt, -np.inf)
        best = int(np.argmax(nxt))
        if not np.isfinite(nxt[best]):
            raise ValueError("destination capacity exhausted before quota was met")
        chosen[best] = True
        ry, rx = int(cy[best]), int(cx[best])
        state.mask[ry, rx] = True
        S += 1.0
        M += float(m_cand[best])
        T += 0.0  # T is recomputed from cov below only for coverage bookkeeping
        # update coverage
        ny = ry + OFF_DY
        nx = rx + OFF_DX
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        ny, nx, kw = ny[ok], nx[ok], OFF_K[ok]
        old = cov[ny, nx]
        upd = kw > old
        if np.any(upd):
            uy, ux, uk = ny[upd], nx[upd], kw[upd]
            uold = old[upd]
            cov[uy, ux] = uk
            T += float((w64[uy, ux] * (uk - uold)).sum())
        y0, y1 = max(0, ry - 6), min(H, ry + 7)
        x0, x1 = max(0, rx - 6), min(W, rx + 7)
        sub = cand_id_grid[y0:y1, x0:x1].ravel()
        sub = sub[sub >= 0]
        sub = sub[~chosen[sub]]
        if sub.size:
            sy, sx = cy[sub], cx[sub]
            nd = np.zeros(len(sub))
            for dy_i, dx_i, kw_i in zip(OFF_DY, OFF_DX, OFF_K):
                nny, nnx = sy + int(dy_i), sx + int(dx_i)
                ook = (nny >= 0) & (nny < H) & (nnx >= 0) & (nnx < W)
                nd[ook] += w64[nny[ook], nnx[ook]] * np.maximum(
                    0.0, kw_i - cov[nny[ook], nnx[ook]])
            dT[sub] = nd
        b = int(cand_block[best])
        filled[b] += 1
        if filled[b] >= capacity[b]:
            s, e = bounds[b], bounds[b + 1]
            usable[order[s:e]] = False
        placed += 1
    state.T, state.S, state.M = T, S, M
    return n_add


# --------------------------------------------------------------------------
# block geometry
# --------------------------------------------------------------------------
def block_index(shape, block_px: int):
    H, W = shape
    nby, nbx = H // block_px + 1, W // block_px + 1
    bi = (np.arange(H) // block_px)[:, None] * nbx + (np.arange(W) // block_px)[None, :]
    return bi, nby, nbx


def block_mean(field: np.ndarray, bi, nblk: int, weight: np.ndarray | None = None):
    if weight is None:
        cnt = np.bincount(bi.ravel(), minlength=nblk)
        s = np.bincount(bi.ravel(), weights=np.asarray(field, dtype=np.float64).ravel(),
                        minlength=nblk)
    else:
        m = weight.ravel()
        flat = bi.ravel()
        cnt = np.bincount(flat, weights=m.astype(np.float64), minlength=nblk)
        s = np.bincount(flat, weights=(np.asarray(field, dtype=np.float64).ravel() * m),
                        minlength=nblk)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(cnt > 0, s / np.maximum(cnt, 1e-12), np.nan), cnt


def full_blocks(bi, footprint: np.ndarray, nblk: int, block_px: int, frac: float = 0.9):
    cnt = np.bincount(bi[footprint], minlength=nblk)
    return cnt > frac * block_px * block_px
