"""Exact lazy-greedy dot placement under the LBM density, with registry caps.

Maximises the model DTI (Dinkelbach form) of a binary dot field:

    value(x) = dTP(x) * (1 - 0.2 D) - 0.2 D * dFP(x)
    dTP(x)   = sum_{|o|<=3} rho(x+o) * max(0, k(o) - C(x+o))
    dFP(x)   = 1 - min(1, 3 rho(x))

where ``C`` is the running kernel coverage of the chosen dots and ``D`` the
running model DTI.  Caps: for every capped column ``j`` (e.g. a registry
raster's 3 px halo), the number of chosen dots inside it may never exceed
``caps[j] * n`` once ``n > min_n_for_cap`` -- which is how the 70% overlap rule
is enforced *during* placement rather than after it.  A dot that would breach
a cap is deferred and re-offered (vectorised feasibility re-check) whenever
capacity grows.  Every prefix is recorded; callers keep the best prefix.
"""
from __future__ import annotations

import heapq

import numpy as np

ALPHA, BETA = 0.2, 0.8
OFFS = [(dy, dx, 1.0 - np.hypot(dy, dx) / 3.0) for dy in range(-3, 4) for dx in range(-3, 4)
        if 1.0 - np.hypot(dy, dx) / 3.0 > 0]


def isolated_value(rho_full: np.ndarray, D: float = 0.28) -> np.ndarray:
    H, W = rho_full.shape
    rho = rho_full.astype(np.float64)
    iso = np.zeros((H, W))
    for dy, dx, k in OFFS:
        ys = slice(max(0, dy), H + min(0, dy)); yd = slice(max(0, -dy), H + min(0, -dy))
        xs = slice(max(0, dx), W + min(0, dx)); xd = slice(max(0, -dx), W + min(0, -dx))
        iso[yd, xd] += k * rho[ys, xs]
    return (iso * (1 - ALPHA * D) - ALPHA * D * (1 - np.minimum(1, 3 * rho))).ravel()


def candidates(rho_full: np.ndarray, eligible_full: np.ndarray, *, init_D: float = 0.28,
               prefilter: int = 1_500_000) -> np.ndarray:
    """Prefiltered candidate cells (full-grid linear indices) by isolated value."""
    v = isolated_value(rho_full, init_D)
    cand = np.flatnonzero(eligible_full.ravel())
    if cand.size > prefilter:
        cand = cand[np.argpartition(-v[cand], prefilter)[:prefilter]]
    return np.sort(cand)


def place(rho_full: np.ndarray, eligible_full: np.ndarray, *, n_max: int,
          cand: np.ndarray | None = None, member: np.ndarray | None = None,
          caps: np.ndarray | None = None, init_D: float = 0.28, min_n_for_cap: int = 0, slack: float = 30.0,
          recheck_every: int = 100) -> dict:
    H, W = rho_full.shape
    rho = rho_full.ravel().astype(np.float64)
    G = float(rho.sum())
    if cand is None:
        cand = candidates(rho_full, eligible_full, init_D=init_D)
    iso_v = isolated_value(rho_full, init_D)
    lin_off = np.array([dy * W + dx for dy, dx, _ in OFFS], np.int64)
    k_off = np.array([k for _, _, k in OFFS], np.float64)
    dy_off = np.array([dy for dy, _, _ in OFFS]); dx_off = np.array([dx for _, dx, _ in OFFS])
    cy, cx = np.divmod(cand, W)
    if member is None:
        member = np.zeros((cand.size, 0), bool)
    member = np.ascontiguousarray(member, dtype=bool)
    capv = np.asarray(caps if caps is not None else np.zeros(member.shape[1]), float)
    counts = np.zeros(member.shape[1], np.int64)
    C = np.zeros(H * W)
    TP = 0.0; FP = 0.0; D = init_D

    def nbr(i):
        yy = cy[i] + dy_off; xx = cx[i] + dx_off
        ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
        return cand[i] + lin_off[ok], k_off[ok]

    heap = [(-float(iso_v[cand[i]]), int(i)) for i in range(cand.size)]
    heapq.heapify(heap)
    taken = np.zeros(cand.size, bool)
    K = member.shape[1]
    blocked: list[list] = [[] for _ in range(K)]     # per-column heaps of deferred items
    n_blocked = 0
    chosen: list[int] = []
    hist_D: list[float] = []

    def release(n_next: int) -> int:
        """Re-offer deferred items whose every cap now has room; re-file the rest.

        2026-10-28 fix (TIPCOMP session): the previous version inspected at
        most 4 items per column and *broke* on the first item that also
        violated another column.  With >= ~15 cap columns almost every
        blocked item violates >= 2 columns, so ``release`` returned 0 while
        releasable items sat deeper in the heaps and placement deadlocked
        after O(10^3) dots.  Now each roomy column is scanned (bounded per
        call) and violators are re-filed without abandoning the column.
        """
        nonlocal n_blocked
        if n_blocked == 0:
            return 0
        room = (counts + 1) <= capv * n_next + slack
        moved = 0
        for j in np.flatnonzero(room).tolist():
            h = blocked[j]
            scanned = 0
            while h and scanned < 64:
                v0, ii = heapq.heappop(h)
                scanned += 1
                bad = np.flatnonzero(member[ii] & ~room)
                if bad.size:
                    heapq.heappush(blocked[int(bad[0])], (v0, ii))
                    continue
                heapq.heappush(heap, (v0, ii)); moved += 1; n_blocked -= 1
        return moved

    while len(chosen) < n_max:
        if not heap:
            if release(len(chosen) + 1) == 0:
                break
            continue
        negv, i = heapq.heappop(heap)
        if taken[i]:
            continue
        idx, kk = nbr(i)
        dTP = float(np.sum(rho[idx] * np.maximum(0.0, kk - C[idx])))
        dFP = 1.0 - min(1.0, 3.0 * rho[cand[i]])
        v = dTP * (1 - ALPHA * D) - ALPHA * D * dFP
        if heap and v < -heap[0][0] - 1e-12:
            heapq.heappush(heap, (-v, i))
            continue
        n_next = len(chosen) + 1
        if K and n_next > min_n_for_cap:
            mi = member[i]
            if mi.any():
                viol = np.flatnonzero(mi & ((counts + 1) > capv * n_next + slack))
                if viol.size:
                    heapq.heappush(blocked[int(viol[0])], (-v, i)); n_blocked += 1
                    continue
        taken[i] = True
        chosen.append(int(cand[i]))
        counts += member[i]
        newC = np.maximum(C[idx], kk)
        TP += float(np.sum(rho[idx] * (newC - C[idx])))
        C[idx] = newC
        FP += dFP
        D = TP / (ALPHA * TP + ALPHA * FP + BETA * G)
        hist_D.append(D)
        release(len(chosen) + 1)
    hD = np.array(hist_D)
    best = int(np.argmax(hD)) + 1 if hD.size else 0
    return dict(order=np.array(chosen, np.int64), D=hD, best_n=best,
                best_D=float(hD[best - 1]) if best else 0.0, G=G, counts_at_end=counts.tolist())


def place_lagrangian(rho_full: np.ndarray, *, n_max: int, cand: np.ndarray, member: np.ndarray,
                     caps: np.ndarray, iters: int = 12, eta: float = 2.0, init_D: float = 0.28,
                     lam0: np.ndarray | None = None, log=print) -> dict:
    """Soft caps by Lagrangian relaxation; returns the best *feasible* prefix found.

    Each iteration runs an uncapped exact lazy greedy whose dot value is reduced
    by ``sum_j lam_j (member_j(x) - cap_j)``.  For every prefix the true model
    DTI and the worst cap ratio are recorded; the best prefix with every ratio
    <= cap is kept.  Multipliers follow a projected subgradient step.
    """
    H, W = rho_full.shape
    rho = rho_full.ravel().astype(np.float64)
    G = float(rho.sum())
    iso_v = isolated_value(rho_full, init_D)
    lin_off = np.array([dy * W + dx for dy, dx, _ in OFFS], np.int64)
    k_off = np.array([k for _, _, k in OFFS], np.float64)
    dy_off = np.array([dy for dy, _, _ in OFFS]); dx_off = np.array([dx for _, dx, _ in OFFS])
    cy, cx = np.divmod(cand, W)
    member = np.ascontiguousarray(member, dtype=bool)
    caps = np.asarray(caps, float)
    K = member.shape[1]
    lam = np.zeros(K) if lam0 is None else np.asarray(lam0, float).copy()
    best = dict(D=-1.0)
    history = []
    for it in range(iters):
        pen = (member.astype(np.float64) @ lam) - float(lam @ caps)
        heap = [(-(float(iso_v[cand[i]]) - pen[i]), int(i)) for i in range(cand.size)]
        heapq.heapify(heap)
        C = np.zeros(H * W); TP = 0.0; FP = 0.0; D = init_D
        counts = np.zeros(K, np.int64)
        chosen = []; hist_D = []; hist_ratio = []
        taken = np.zeros(cand.size, bool)
        while heap and len(chosen) < n_max:
            negv, i = heapq.heappop(heap)
            if taken[i]:
                continue
            yy = cy[i] + dy_off; xx = cx[i] + dx_off
            ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
            idx = cand[i] + lin_off[ok]; kk = k_off[ok]
            dTP = float(np.sum(rho[idx] * np.maximum(0.0, kk - C[idx])))
            dFP = 1.0 - min(1.0, 3.0 * rho[cand[i]])
            v = dTP * (1 - ALPHA * D) - ALPHA * D * dFP - pen[i]
            if heap and v < -heap[0][0] - 1e-12:
                heapq.heappush(heap, (-v, i))
                continue
            taken[i] = True
            chosen.append(int(cand[i]))
            counts += member[i]
            newC = np.maximum(C[idx], kk)
            TP += float(np.sum(rho[idx] * (newC - C[idx])))
            C[idx] = newC
            FP += dFP
            D = TP / (ALPHA * TP + ALPHA * FP + BETA * G)
            hist_D.append(D)
            hist_ratio.append(float(np.max(counts / (caps * len(chosen)))) if K else 0.0)
        hD = np.array(hist_D); hr = np.array(hist_ratio)
        feas = hr <= 1.0
        feas[:500] = False
        if feas.any():
            j = int(np.argmax(np.where(feas, hD, -1.0)))
            if hD[j] > best["D"]:
                best = dict(D=float(hD[j]), n=j + 1, order=np.array(chosen[: j + 1], np.int64), iter=it,
                            lam=lam.copy())
        # subgradient at the unconstrained-best prefix
        jb = int(np.argmax(hD))
        sel = np.array(chosen[: jb + 1])
        pos = np.searchsorted(cand, sel)
        ratio = member[pos].mean(axis=0) if K else np.zeros(0)
        viol = ratio - caps
        history.append(dict(iter=it, best_unconstrained_D=float(hD[jb]), n=jb + 1,
                            worst_ratio=float(ratio.max()) if K else 0.0,
                            feasible_best_D=float(np.max(np.where(feas, hD, -1.0))) if feas.any() else None))
        log(f"   lagrange it {it}: D*={hD[jb]:.4f} n={jb+1} worst ratio {ratio.max() if K else 0:.3f} "
            f"best feasible so far {best['D']:.4f}")
        step = eta / max(K, 1) / (1.0 + 0.5 * it)
        lam = np.maximum(0.0, lam + step * viol)
    best["history"] = history
    best["final_lam"] = lam
    return best
