"""Variant builders: one AXIS at a time, from a named parent (brief section 5).

Contract for every builder
--------------------------
    f(parent, **params) -> Variant

* Only the named axis changes. A builder that silently also re-ranks, re-mass-es
  or re-snaps is a bug and tests/test_variants.py asserts it cannot happen.
* Counts, exclusions and mass are preserved unless the axis is MASS.
* The exact fraction of parent dots changed is recorded; for non-SNAP axes the
  brief requires 1% <= changed <= 50%.
* No builder reads the truth set. Truth/holdout is only used downstream for
  PROXY reporting, never to steer a build (no label probing, constraint 5).

Everything is deterministic: no unseeded randomness.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.spatial import cKDTree

MIN_CHANGED, MAX_CHANGED = 0.01, 0.50


@dataclass
class Dots:
    ys: np.ndarray
    xs: np.ndarray
    p: np.ndarray

    def __post_init__(self):
        self.ys = np.asarray(self.ys, dtype=np.int64)
        self.xs = np.asarray(self.xs, dtype=np.int64)
        self.p = np.asarray(self.p, dtype=float)
        assert self.ys.shape == self.xs.shape == self.p.shape, "shape mismatch"
        if len(self.ys):
            assert (self.p > 0).all(), "dots must carry positive mass"

    def __len__(self) -> int:
        return len(self.ys)

    @property
    def keys(self) -> set[tuple[int, int]]:
        return set(zip(self.ys.tolist(), self.xs.tolist()))

    def with_mass(self, p) -> "Dots":
        return Dots(self.ys, self.xs, p)


@dataclass
class Variant:
    axis: str
    value: str
    dots: Dots
    n_parent: int
    n_changed: int
    stats: dict = field(default_factory=dict)

    @property
    def pct_changed(self) -> float:
        return 100.0 * self.n_changed / self.n_parent if self.n_parent else 0.0

    def check_change(self, allow_out_of_bounds: bool = False) -> None:
        if allow_out_of_bounds:
            return
        if not (MIN_CHANGED * 100 <= self.pct_changed <= MAX_CHANGED * 100):
            raise ValueError(
                f"{self.axis}={self.value}: changed {self.pct_changed:.2f}% is outside "
                f"the brief's {MIN_CHANGED*100:.0f}-{MAX_CHANGED*100:.0f}% window")


def _as_coords(seq) -> list[tuple[int, int]]:
    """Accept bare (y, x) pairs or (coord, score) pairs from a ranker."""
    out = []
    for item in seq:
        if (isinstance(item, (tuple, list)) and len(item) == 2
                and isinstance(item[0], (tuple, list, np.ndarray))):
            y, x = item[0]
        else:
            y, x = item
        out.append((int(y), int(x)))
    return out


def _changed(a: Dots, b: Dots) -> int:
    """Dots present in the parent but absent (position) in the variant."""
    ka, kb = a.keys, b.keys
    return len(ka - kb)


# --------------------------------------------------------------------------
# PRUNE: remove dots close to the catalogue, refill to hold the count
# --------------------------------------------------------------------------
def prune(parent: Dots, catalogue_ys, catalogue_xs, radius_px: int,
          refill: list[tuple[int, int]], min_catalogue_px: int = 3) -> Variant:
    """Remove parent dots within `radius_px` of a catalogue pixel; refill.

    Refill candidates must be empty, inside the footprint and >= the hard
    constraint distance from the catalogue -- the caller supplies them already
    ranked (by exact marginal gain), so no ranking happens here. `refill`
    accepts bare (y, x) pairs or (coord, gain) pairs, in rank order.
    """
    if radius_px >= min_catalogue_px:
        raise ValueError(
            f"prune radius {radius_px} px sits at/inside the {min_catalogue_px} px "
            "hard constraint; declare it to the human and pass an explicit override")
    if len(catalogue_ys) == 0:
        raise ValueError("catalogue mask is empty: nothing to prune, this is not an experiment")
    tree = cKDTree(np.c_[catalogue_ys, catalogue_xs])
    d, _ = tree.query(np.c_[parent.ys, parent.xs], k=1)
    drop = d <= radius_px
    keep = ~drop
    n_drop = int(drop.sum())
    if n_drop == 0:
        raise ValueError(f"no parent dots within {radius_px} px of catalogue")

    cat_tree_px = min_catalogue_px
    added = []
    have = parent.keys
    for y, x in _as_coords(refill):
        if (y, x) in have:
            continue
        dd, _ = tree.query([y, x], k=1)
        if dd <= cat_tree_px:
            continue
        added.append((y, x))
        have.add((y, x))
        if len(added) == n_drop:
            break
    if len(added) != n_drop:
        raise ValueError(f"refill short: needed {n_drop}, got {len(added)} candidates")

    ys = np.r_[parent.ys[keep], [a[0] for a in added]]
    xs = np.r_[parent.xs[keep], [a[1] for a in added]]
    ps = np.r_[parent.p[keep], np.full(len(added), parent.p[keep].mean() if keep.any() else 1.0)]
    out = Dots(ys, xs, ps)
    v = Variant(f"PRUNE", f"le{radius_px}px", out, len(parent), _changed(parent, out),
                stats={"n_dropped": n_drop, "n_refilled": len(added),
                       "n_parent": len(parent),
                       "removed_dist_px_median": float(np.median(d[drop]))})
    v.check_change()
    return v


# --------------------------------------------------------------------------
# MASS: drop the lowest-ranked 10% / add the next-ranked 10%
# --------------------------------------------------------------------------
def mass_drop(parent: Dots, ranking: np.ndarray, frac: float = 0.10) -> Variant:
    """Drop the worst `frac` of dots by the parent's OWN ranking (descending)."""
    if len(ranking) != len(parent):
        raise ValueError(f"ranking length {len(ranking)} != n dots {len(parent)}")
    order = np.argsort(-ranking, kind="stable")   # best dot first
    n_drop = int(round(frac * len(parent)))
    if n_drop == 0:
        raise ValueError("frac rounds to zero dots")
    keep = np.zeros(len(parent), bool)
    keep[order[:len(parent) - n_drop]] = True     # keep the best, drop the worst
    out = Dots(parent.ys[keep], parent.xs[keep], parent.p[keep])
    v = Variant("MASS", f"drop{int(frac*100)}", out, len(parent), _changed(parent, out),
                stats={"n_dropped": n_drop,
                       "cut_rank_value": float(ranking[order[len(parent) - n_drop - 1]])})
    v.check_change()
    return v


def mass_add(parent: Dots, ranked_candidates: list[tuple[tuple[int, int], float]],
             frac: float = 0.10) -> Variant:
    """Add the next `frac` best dots from the parent's own ranking."""
    n_add = int(round(frac * len(parent)))
    if n_add == 0:
        raise ValueError("frac rounds to zero dots")
    if len(ranked_candidates) < n_add:
        raise ValueError(f"need {n_add} candidates, got {len(ranked_candidates)}")
    have = parent.keys
    picks = [(y, x) for (y, x), _ in ranked_candidates if (y, x) not in have][:n_add]
    if len(picks) != n_add:
        raise ValueError(f"after dedupe only {len(picks)} candidates remain")
    ys = np.r_[parent.ys, [p[0] for p in picks]]
    xs = np.r_[parent.xs, [p[1] for p in picks]]
    ps = np.r_[parent.p, np.full(n_add, 1.0)]
    out = Dots(ys, xs, ps)
    v = Variant("MASS", f"add{int(frac*100)}", out, len(parent), n_add,
                stats={"n_added": n_add,
                       "min_candidate_gain": float(ranked_candidates[len(picks)-1][1])})
    v.check_change()
    return v


# --------------------------------------------------------------------------
# CONCENTRATION: move dots from low-prior km-scale blocks to high-prior ones
# --------------------------------------------------------------------------
def block_prior(prior: np.ndarray, block_px: int) -> tuple[np.ndarray, int, int]:
    """Mean prior per block, NaN where the block has no finite prior."""
    H, W = prior.shape
    nby, nbx = H // block_px + 1, W // block_px + 1
    bi = np.arange(H) // block_px
    bj = np.arange(W) // block_px
    flat = bi[:, None] * nbx + bj[None, :]
    fp = np.isfinite(prior)
    sums = np.bincount(flat[fp], weights=prior[fp], minlength=nby * nbx)
    cnts = np.bincount(flat[fp], minlength=nby * nbx)
    with np.errstate(invalid="ignore", divide="ignore"):
        bp = np.where(cnts > 0, sums / cnts, np.nan).reshape(nby, nbx)
    return bp, nby, nbx


def block_density_cv(dots: Dots, prior: np.ndarray, footprint: np.ndarray | None,
                     block_px: int) -> float:
    """CV of dot counts across in-footprint blocks (brief's 0.51-0.59 reference)."""
    bp, nby, nbx = block_prior(prior, block_px)
    fb = footprint_blocks(prior, footprint, block_px)
    flat = (dots.ys // block_px) * nbx + (dots.xs // block_px)
    cnt = np.bincount(flat, minlength=nby * nbx).reshape(nby, nbx)
    vals = cnt[fb].astype(float)
    if vals.size == 0 or vals.mean() == 0:
        return float("nan")
    return float(vals.std() / vals.mean())


def footprint_blocks(prior: np.ndarray, footprint: np.ndarray | None,
                     block_px: int) -> np.ndarray:
    """Boolean (nby, nbx) of blocks containing any in-footprint pixel."""
    H, W = prior.shape
    nby, nbx = H // block_px + 1, W // block_px + 1
    src = np.isfinite(prior) if footprint is None else footprint
    flat = (np.arange(H) // block_px)[:, None] * nbx + (np.arange(W) // block_px)[None, :]
    hit = np.bincount(flat[src], minlength=nby * nbx).reshape(nby, nbx)
    return hit > 0


def concentration(parent: Dots, prior: np.ndarray, block_px: int = 10,
                  frac: float = 0.15, footprint: np.ndarray | None = None) -> Variant:
    """Move `frac` of dots from the least-prior blocks to the most-prior blocks.

    block_px = 10 -> 1 km blocks at 100 m pixels. `prior` is a km-scale
    favourability surface (e.g. a fault-interaction-zone prior), NOT truth.
    """
    if prior.shape[0] <= parent.ys.max() or prior.shape[1] <= parent.xs.max():
        raise ValueError("prior grid does not cover the dots")
    bp, nby, nbx = block_prior(prior, block_px)
    fb = footprint_blocks(prior, footprint, block_px)

    by, bx = parent.ys // block_px, parent.xs // block_px
    dot_bp = bp[by, bx]
    n_move = int(round(frac * len(parent)))
    if n_move == 0:
        raise ValueError("frac rounds to zero dots")
    finite = np.isfinite(dot_bp)
    if finite.sum() < n_move:
        raise ValueError(f"only {int(finite.sum())} dots sit in prior-bearing blocks, "
                         f"cannot move {n_move}")

    movers = np.argsort(np.where(finite, dot_bp, np.inf), kind="stable")[:n_move]

    # destination blocks: highest block prior first, footprint only
    score = np.where(fb & np.isfinite(bp), -bp, np.inf)
    block_order = np.argsort(score, axis=None, kind="stable")
    dest = [(int(k) // nbx, int(k) % nbx) for k in block_order
            if np.isfinite(score.flat[int(k)])]

    keep = np.ones(len(parent), bool)
    keep[movers] = False
    ys = [parent.ys[keep]]
    xs = [parent.xs[keep]]
    ps = [parent.p[keep]]
    have = set(zip(parent.ys[keep].tolist(), parent.xs[keep].tolist()))
    H, W = prior.shape
    dest_prior = []
    for t, m in enumerate(movers):
        i, j = dest[t % len(dest)]
        placed = False
        for rad in range(0, block_px + 1):
            for dy in range(-rad, rad + 1):
                for dx in range(-rad, rad + 1):
                    y = i * block_px + block_px // 2 + dy
                    x = j * block_px + block_px // 2 + dx
                    if not (0 <= y < H and 0 <= x < W):
                        continue
                    if footprint is not None and not footprint[y, x]:
                        continue
                    if (y, x) in have:
                        continue
                    have.add((y, x))
                    ys.append(np.array([y])); xs.append(np.array([x]))
                    ps.append(np.array([parent.p[m]]))
                    dest_prior.append(bp[i, j])
                    placed = True
                    break
                if placed: break
            if placed: break
        if not placed:
            raise ValueError("could not place a moved dot: destination blocks full")

    out = Dots(np.concatenate(ys), np.concatenate(xs), np.concatenate(ps))
    v = Variant("CONCENTRATION", f"blk{block_px}px_frac{frac:.2f}", out,
                len(parent), _changed(parent, out),
                stats={"n_moved": n_move, "block_px": block_px,
                       "block_px_km": block_px / 10.0,
                       "mean_prior_movers_before": float(np.nanmean(dot_bp[movers])),
                       "mean_prior_dest": float(np.nanmean(dest_prior)),
                       "block_density_cv_before": block_density_cv(parent, prior, footprint, block_px),
                       "block_density_cv_after": block_density_cv(out, prior, footprint, block_px)})
    v.check_change()
    return v


# --------------------------------------------------------------------------
# SNAP: move each dot <= 2 px onto the strongest edge response in its window
# --------------------------------------------------------------------------
def _snap_offsets(max_shift: float) -> list[tuple[int, int]]:
    """Integer offsets within Euclidean distance `max_shift` (excluding 0,0)."""
    r = int(np.ceil(max_shift))
    out = []
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = float(np.hypot(dy, dx))
            if 0.0 < d <= max_shift + 1e-9:
                out.append((dy, dx))
    if not out:
        raise ValueError("max_shift admits no integer offset but zero")
    return out


def snap(parent: Dots, response: np.ndarray, max_shift: float = 2,
         footprint: np.ndarray | None = None,
         keep_out: np.ndarray | None = None,
         min_gain: float = 0.0,
         min_spacing_px: float = 0.0) -> Variant:
    """Move a dot onto the strongest `response` in its window, when that says
    the dot is mispositioned.

    Rule, per dot: take the strongest legal pixel within `max_shift` px; move
    there only if it beats the dot's own pixel by more than `min_gain` (in
    response units) and the target is at least `min_spacing_px` from every
    other dot. Otherwise the dot stays. Count and mass are conserved exactly
    and no exclusion is lifted: a dot may only land on a pixel inside the
    footprint that is outside `keep_out` (catalogue + declared collar) and not
    already occupied, so two dots can never share a pixel (a shared pixel would
    need a value of 2.0 and break the [0,1] range).

    Why `min_gain` and `min_spacing_px` exist
    -----------------------------------------
    The literal rule (move every dot to the local argmax, gain > 0) moves 99%
    of R0's dots by ~1 px: the response is continuous, so almost every dot has
    a slightly stronger neighbour. That shuffles the whole file for
    sub-threshold evidence and packs dots into 1 px pairs, destroying the
    parent's 2.83 px minimum-spacing invariant (D2.8) and double-crediting the
    same truth pixels -- a change the DTI algebra punishes for reasons that have
    nothing to do with the SNAP hypothesis. `min_gain` makes SNAP an
    evidence-thresholded position correction (the dose knob) and
    `min_spacing_px` keeps the parent's spacing invariant.

    Contention is resolved in a deterministic order: biggest response
    improvement first, then (y, x). SNAP is exempt from the brief's 1-50%
    changed window (count is preserved by construction); its statistic is mean
    displacement.

    Stats also report the two side effects the DTI algebra cares about: the
    response change, and how many dots end up closer than 2.83 px.
    """
    if max_shift < 1:
        raise ValueError("max_shift must be >= 1")
    if response.shape[0] <= parent.ys.max() or response.shape[1] <= parent.xs.max():
        raise ValueError("response grid does not cover the dots")
    H, W = response.shape
    res = np.where(np.isfinite(response), response, -np.inf)
    offsets = _snap_offsets(max_shift)

    # response at every candidate pixel for every dot, shape (n, len(offsets))
    Y = parent.ys[:, None] + np.array([o[0] for o in offsets])[None, :]
    X = parent.xs[:, None] + np.array([o[1] for o in offsets])[None, :]
    inb = (Y >= 0) & (Y < H) & (X >= 0) & (X < W)
    Yc, Xc = np.clip(Y, 0, H - 1), np.clip(X, 0, W - 1)
    VAL = np.full(Y.shape, -np.inf, dtype=np.float64)
    VAL[inb] = res[Yc[inb], Xc[inb]]
    if footprint is not None:
        VAL[inb & ~footprint[Yc, Xc]] = -np.inf
    if keep_out is not None:
        VAL[inb & keep_out[Yc, Xc]] = -np.inf

    home_res = res[parent.ys, parent.xs]
    best_res = np.maximum(VAL.max(axis=1), home_res)
    with np.errstate(invalid="ignore"):
        improvement = best_res - home_res
    # A dot whose own pixel carries no response value (16 of R0's dots sit on
    # sentinel pixels of the 19-band stack) cannot be shown to be mispositioned,
    # so it never moves: it is kept exactly where the parent put it.
    improvement = np.where(np.isfinite(improvement), improvement, -np.inf)
    wants_move = improvement > min_gain
    improvement = np.where(wants_move, improvement, -np.inf)

    # deterministic processing order: biggest improver first
    order = np.lexsort((parent.xs, parent.ys, -np.round(np.where(np.isfinite(improvement), improvement, 0.0), 12)))
    order = order[np.isfinite(improvement[order])]
    # each dot's candidate order: strongest response, then shortest hop, then (dy, dx)
    cand_order = np.lexsort((
        np.array([o[1] for o in offsets])[None, :] * np.ones((len(parent), 1)),
        np.array([o[0] for o in offsets])[None, :] * np.ones((len(parent), 1)),
        np.array([np.hypot(*o) for o in offsets])[None, :] * np.ones((len(parent), 1)),
        -VAL,
    ), axis=1)

    occ = np.zeros((H, W), dtype=np.int32)
    occ[parent.ys, parent.xs] = np.arange(1, len(parent) + 1, dtype=np.int32)
    new_y = parent.ys.copy()
    new_x = parent.xs.copy()

    # forbidden neighbour offsets for a 2.83 px minimum spacing: every offset
    # with |dy|,|dx| <= 2 except the four (2,2) corners, whose distance is 2.828.
    spacing_offsets = [(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3)
                       if (dy, dx) != (0, 0)
                       and np.hypot(dy, dx) < min_spacing_px - 1e-9]

    def clear(yy: int, xx: int, j: int) -> bool:
        for dy, dx in spacing_offsets:
            y2, x2 = yy + dy, xx + dx
            if 0 <= y2 < H and 0 <= x2 < W:
                o = int(occ[y2, x2])
                if o != 0 and o != j + 1:
                    return False
        return True

    n_contested = 0
    n_blocked_by_spacing = 0
    for j in order:
        home = (int(parent.ys[j]), int(parent.xs[j]))
        target = None
        for k in cand_order[j]:
            val = VAL[j, k]
            if not np.isfinite(val):
                continue
            yy, xx = int(Y[j, k]), int(X[j, k])
            occupant = occ[yy, xx]
            if occupant != 0 and occupant != j + 1:
                n_contested += 1
                continue
            if min_spacing_px > 0 and not clear(yy, xx, j):
                n_blocked_by_spacing += 1
                continue
            target = (yy, xx)
            break
        if target is None:
            # Keep the parent pixel. It is legal by inheritance (footprint,
            # off-catalogue) and spacing-safe by the parent's own invariant.
            occupant = occ[home]
            if occupant in (0, j + 1):
                target = home
            else:
                raise ValueError(f"dot {j} at {home} has no legal pixel, not even its own")
        if target != home:
            occ[home] = 0
            occ[target] = j + 1
        new_y[j], new_x[j] = target

    out = Dots(new_y, new_x, parent.p)
    dy = (out.ys - parent.ys).astype(float)
    dx = (out.xs - parent.xs).astype(float)
    disp = np.hypot(dy, dx)
    moved = disp > 0

    from scipy.spatial import cKDTree
    tree = cKDTree(np.c_[out.ys, out.xs])
    d_nn, _ = tree.query(np.c_[out.ys, out.xs], k=2)
    parent_tree = cKDTree(np.c_[parent.ys, parent.xs])
    d_nn_parent, _ = parent_tree.query(np.c_[parent.ys, parent.xs], k=2)

    new_res = res[out.ys, out.xs]
    fin_before = np.isfinite(home_res)
    fin_after = np.isfinite(new_res)
    v = Variant("SNAP", f"max{max_shift:g}px_g{min_gain:.2f}", out, len(parent),
                _changed(parent, out),
                stats={
                    "max_shift_px": float(max_shift),
                    "min_gain": float(min_gain),
                    "min_spacing_px": float(min_spacing_px),
                    "mean_displacement_px": float(disp.mean()),
                    "median_displacement_px": float(np.median(disp)),
                    "p90_displacement_px": float(np.percentile(disp, 90)),
                    "max_displacement_px": float(disp.max()),
                    "frac_moved": float(moved.mean()),
                    "n_moved": int(moved.sum()),
                    "n_contested_pixels": int(n_contested),
                    "n_blocked_by_spacing": int(n_blocked_by_spacing),
                    "mean_response_before": float(np.mean(home_res[fin_before]))
                    if fin_before.any() else float("nan"),
                    "mean_response_after": float(np.mean(new_res[fin_after]))
                    if fin_after.any() else float("nan"),
                    "n_dots_without_home_response": int((~fin_before).sum()),
                    "median_response_gain_moved": float(np.nanmedian(
                        np.where(np.isfinite(new_res) & np.isfinite(home_res),
                                 new_res - home_res, np.nan)[moved]))
                    if moved.any() else 0.0,
                    "n_stayed": int((~moved).sum()),
                    "mean_dx": float(dx.mean()),
                    "mean_dy": float(dy.mean()),
                    "parent_min_nn_px": float(d_nn_parent[:, 1].min()),
                    "snapped_min_nn_px": float(d_nn[:, 1].min()),
                    "snapped_dots_under_2p83px": int((d_nn[:, 1] < 2.828 - 1e-6).sum()),
                    "count_preserved": len(out) == len(parent),
                })
    v.check_change(allow_out_of_bounds=True)
    return v


def snap_spaced(
    parent: Dots,
    response: np.ndarray,
    value: str,
    max_shift: float = 2.0,
    min_nn: float = 2.8,
    min_gain: float = 0.01,
    footprint: np.ndarray | None = None,
    keep_out: np.ndarray | None = None,
) -> Variant:
    """Move each dot <= max_shift px to strongest local response while preserving Poisson spacing.

    Why `min_nn` matters for DTI:
    Parent R0 stems from D2.8 Poisson-disk thinning (`d^2 >= 2.8^2`, min Euclidean
    inter-dot distance sqrt(8) = 2.828 px) matched to the R = 3 px triangular DTI
    kernel `T = sum_g max_x k(||g - x||)`. Snapping dots without an inter-dot spacing
    floor collapses ~23% of dots onto adjacent along-strike pixels (`d = 1.0–1.4 px`),
    duplicating kernel coverage while paying full denominator mass `S`. Enforcing
    the open-disc exclusion `dy^2 + dx^2 < min_nn^2` prevents along-strike bunching
    and isolates cross-strike centering onto the scarp/gradient crest.
    """
    if max_shift <= 0 or max_shift > 2.0 + 1e-9:
        raise ValueError(f"max_shift={max_shift} must be in (0, 2.0] px per SNAP spec")
    if len(parent) == 0:
        return Variant("SNAP", value, parent, 0, 0,
                       stats={"mean_displacement_px": 0.0, "median_displacement_px": 0.0,
                              "frac_moved": 0.0, "max_displacement_px": 0.0, "min_nn_px": float("nan")})
    if response.shape[0] <= parent.ys.max() or response.shape[1] <= parent.xs.max():
        raise ValueError("response grid does not cover the dots")

    H, W = response.shape
    res = np.where(np.isfinite(response), response, -np.inf)

    ir = int(np.floor(max_shift + 1e-9))
    offs = [
        (dy, dx, float(np.hypot(dy, dx)))
        for dy in range(-ir, ir + 1)
        for dx in range(-ir, ir + 1)
        if np.hypot(dy, dx) <= max_shift + 1e-9
    ]
    br = int(np.ceil(min_nn)) if min_nn > 0 else 0
    lim2 = float(min_nn) * float(min_nn)
    b_offs = [
        (dy, dx)
        for dy in range(-br, br + 1)
        for dx in range(-br, br + 1)
        if (dy != 0 or dx != 0) and (dy * dy + dx * dx < lim2)
    ]

    ys0 = parent.ys.astype(np.int64, copy=True)
    xs0 = parent.xs.astype(np.int64, copy=True)
    win_max = res[ys0, xs0].copy()
    for dy, dx, _ in offs:
        yy = np.clip(ys0 + dy, 0, H - 1)
        xx = np.clip(xs0 + dx, 0, W - 1)
        win_max = np.maximum(win_max, res[yy, xx])
    order = np.lexsort((xs0, ys0, -np.where(np.isfinite(win_max), win_max, -1e9)))

    owner = np.full((H, W), -1, dtype=np.int32)
    owner[ys0, xs0] = np.arange(len(parent), dtype=np.int32)
    cur_y = ys0.copy()
    cur_x = xs0.copy()

    for idx in order:
        y0, x0 = int(cur_y[idx]), int(cur_x[idx])
        r_orig = float(res[y0, x0])
        owner[y0, x0] = -1
        best_key = (r_orig if np.isfinite(r_orig) else -1e9, 0.0, -y0, -x0)
        best_pos = (y0, x0)
        for dy, dx, dist in offs:
            if dy == 0 and dx == 0:
                continue
            yy, xx = y0 + dy, x0 + dx
            if not (0 <= yy < H and 0 <= xx < W):
                continue
            if footprint is not None and not footprint[yy, xx]:
                continue
            if keep_out is not None and keep_out[yy, xx]:
                continue
            if owner[yy, xx] != -1:
                continue
            rv = float(res[yy, xx])
            if not np.isfinite(rv) or (rv - r_orig) <= min_gain:
                continue
            conflict = False
            for bdy, bdx in b_offs:
                ny, nx = yy + bdy, xx + bdx
                if 0 <= ny < H and 0 <= nx < W and owner[ny, nx] != -1:
                    conflict = True
                    break
            if conflict:
                continue
            key = (rv, -dist, -yy, -xx)
            if key > best_key:
                best_key = key
                best_pos = (yy, xx)
        cur_y[idx], cur_x[idx] = best_pos
        owner[best_pos[0], best_pos[1]] = int(idx)

    disp = np.hypot(cur_y - ys0, cur_x - xs0)
    out = Dots(cur_y, cur_x, parent.p.copy())
    min_nn_obs = float("nan")
    if len(out) >= 2:
        nn_d, _ = cKDTree(np.c_[out.ys, out.xs]).query(np.c_[out.ys, out.xs], k=2)
        min_nn_obs = float(nn_d[:, 1].min())
    v = Variant(
        "SNAP",
        value,
        out,
        len(parent),
        _changed(parent, out),
        stats={
            "mean_displacement_px": float(disp.mean()),
            "median_displacement_px": float(np.median(disp)),
            "frac_moved": float((disp > 0).mean()),
            "max_displacement_px": float(disp.max()),
            "min_nn_px": min_nn_obs,
        },
    )
    v.check_change(allow_out_of_bounds=True)
    return v


# --------------------------------------------------------------------------
# RELIEF: shift 10-15% of mass between basin / piedmont / range-front terciles
# --------------------------------------------------------------------------
def compute_relief_terciles(
    detrended_elev: np.ndarray,
    valid: np.ndarray | None = None,
    sentinel_floor: float = -1e30,
) -> tuple[np.ndarray, tuple[float, float]]:
    """Classify valid pixels into equal-area detrended-elevation terciles.

    Returns (terciles, (q33, q67)) where:
        0 = basin       (det_elev <= q33)
        1 = piedmont    (q33 < det_elev <= q67)
        2 = range_front (det_elev > q67)
       -1 = invalid / outside footprint / float32 nodata sentinel
    """
    arr = np.asarray(detrended_elev, dtype=np.float64)
    mask = np.isfinite(arr) & (arr > sentinel_floor)
    if valid is not None:
        mask &= np.asarray(valid, dtype=bool)
    if int(mask.sum()) < 3:
        raise ValueError("need at least 3 valid pixels to define relief terciles")
    q33, q67 = (float(x) for x in np.quantile(arr[mask], [1.0 / 3.0, 2.0 / 3.0]))
    terc = np.full(arr.shape, -1, dtype=np.int8)
    terc[mask & (arr <= q33)] = 0
    terc[mask & (arr > q33) & (arr <= q67)] = 1
    terc[mask & (arr > q67)] = 2
    return terc, (q33, q67)


def relief(
    parent: Dots,
    detrended_elev: np.ndarray,
    terciles: np.ndarray,
    frac: float = 0.11,
    direction: str = "to_piedmont",
    candidates: np.ndarray | None = None,
    relief_score: np.ndarray | None = None,
    min_nn: float = 1.41421356,
    value: str | None = None,
) -> Variant:
    """Shift `frac` (10-15%) of unit-mass dots between relief terciles, count fixed.

    Why unit-mass dot reallocation rather than soft weight addition `p + add`:
    Parent R0 carries unit mass `p = 1.0` on all 37,654 dots. Adding `add > 0` to
    destination dots produces `p > 1.0` (failing the `[0, 1]` format gate) and
    modifies 100% of dots (failing the 1-50% change bound), whereas down-scaling
    `p < 1.0` shrinks total mass `S` and incurs a severe DTI denominator penalty
    because `0.8 * |G|` does not scale with `p`. Moving `round(frac * N)` unit-mass
    dots proportionally out of the two source terciles onto eligible `candidates`
    in the destination tercile preserves exact dot count `N`, total mass `S`,
    `[0, 1]` bounds, and `min_nn` inter-dot spacing.
    """
    if direction not in ("to_piedmont", "to_range_front", "to_basin"):
        raise ValueError(f"unknown direction {direction!r}")
    if not (0.10 - 1e-6 <= frac <= 0.15 + 1e-6):
        raise ValueError(f"RELIEF frac={frac} must lie in [0.10, 0.15] per Brief v2 §5")
    src_of = {
        "to_piedmont": (0, 2),
        "to_range_front": (0, 1),
        "to_basin": (1, 2),
    }[direction]
    dst = {"to_piedmont": 1, "to_range_front": 2, "to_basin": 0}[direction]
    if terciles.shape[0] <= parent.ys.max() or terciles.shape[1] <= parent.xs.max():
        raise ValueError("tercile grid does not cover the dots")

    H, W = terciles.shape
    score_grid = (
        np.asarray(relief_score, dtype=np.float64)
        if relief_score is not None
        else np.where(
            np.isfinite(detrended_elev) & (detrended_elev > -1e30),
            np.asarray(detrended_elev, dtype=np.float64),
            0.0,
        )
    )
    lab = terciles[parent.ys, parent.xs]
    valid_dot = np.isfinite(detrended_elev[parent.ys, parent.xs]) & (
        detrended_elev[parent.ys, parent.xs] > -1e30
    )
    in_src = np.isin(lab, src_of) & valid_dot
    n_move = int(round(frac * len(parent)))
    if n_move <= 0:
        raise ValueError("frac rounds to zero dots")
    if int(in_src.sum()) < n_move:
        raise ValueError(
            f"source terciles hold {int(in_src.sum())} dots, fewer than n_move={n_move}"
        )

    # Proportional quota across the two source terciles
    s0, s1 = src_of
    m0 = (lab == s0) & valid_dot
    m1 = (lab == s1) & valid_dot
    n0_src, n1_src = int(m0.sum()), int(m1.sum())
    k0 = min(n0_src, int(round(n_move * n0_src / (n0_src + n1_src))))
    k1 = n_move - k0
    if k1 > n1_src:
        k1 = n1_src
        k0 = n_move - k1

    keep = np.ones(len(parent), dtype=bool)
    for mask_s, k_s in ((m0, k0), (m1, k1)):
        if k_s <= 0:
            continue
        idxs = np.flatnonzero(mask_s)
        ord_s = np.lexsort(
            (parent.xs[idxs], parent.ys[idxs], score_grid[parent.ys[idxs], parent.xs[idxs]])
        )
        keep[idxs[ord_s[:k_s]]] = False

    occ = np.zeros((H, W), dtype=bool)
    occ[parent.ys[keep], parent.xs[keep]] = True

    cand_grid = (
        np.asarray(candidates, dtype=bool)
        if candidates is not None
        else (terciles == dst) & np.isfinite(detrended_elev) & (detrended_elev > -1e30)
    )
    elig = cand_grid & (terciles == dst) & ~occ
    cy, cx = np.nonzero(elig)
    if len(cy) < n_move:
        raise ValueError(
            f"destination tercile {dst} has {len(cy)} candidates, need {n_move}"
        )
    cand_ord = np.lexsort((cx, cy, -score_grid[cy, cx]))

    br = int(np.ceil(min_nn)) if min_nn > 0 else 0
    lim2 = float(min_nn - 1e-9) ** 2 if min_nn > 0 else 0.0
    b_offs = [
        (dy, dx)
        for dy in range(-br, br + 1)
        for dx in range(-br, br + 1)
        if (dy != 0 or dx != 0) and (dy * dy + dx * dx < lim2)
    ]

    add_y: list[int] = []
    add_x: list[int] = []
    for c_idx in cand_ord:
        yy, xx = int(cy[c_idx]), int(cx[c_idx])
        if occ[yy, xx]:
            continue
        if b_offs:
            conflict = False
            for dy, dx in b_offs:
                ny, nx = yy + dy, xx + dx
                if 0 <= ny < H and 0 <= nx < W and occ[ny, nx]:
                    conflict = True
                    break
            if conflict:
                continue
        occ[yy, xx] = True
        add_y.append(yy)
        add_x.append(xx)
        if len(add_y) == n_move:
            break

    if len(add_y) != n_move:
        raise ValueError(
            f"spaced destination placement placed {len(add_y)}/{n_move} dots (min_nn={min_nn:.3f})"
        )

    mean_p = float(parent.p[keep].mean()) if keep.any() else 1.0
    ys = np.r_[parent.ys[keep], np.asarray(add_y, dtype=np.int64)]
    xs = np.r_[parent.xs[keep], np.asarray(add_x, dtype=np.int64)]
    ps = np.r_[parent.p[keep], np.full(n_move, mean_p, dtype=float)]
    out = Dots(ys, xs, ps)

    out_lab = terciles[out.ys, out.xs]
    v = Variant(
        "RELIEF",
        value if value is not None else direction,
        out,
        len(parent),
        _changed(parent, out),
        stats={
            "direction": direction,
            "dst_tercile": dst,
            "src_terciles": list(src_of),
            "n_moved": n_move,
            "frac_mass_moved": float(n_move / len(parent)),
            "mass_total_before": float(parent.p.sum()),
            "mass_total_after": float(out.p.sum()),
            "tercile_counts_before": {int(t): int((lab == t).sum()) for t in (0, 1, 2)},
            "tercile_counts_after": {int(t): int((out_lab == t).sum()) for t in (0, 1, 2)},
        },
    )
    v.check_change()
    return v
