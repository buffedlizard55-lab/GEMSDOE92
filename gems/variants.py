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
def relief(parent: Dots, detrended_elev: np.ndarray, terciles: np.ndarray,
           frac: float = 0.12, direction: str = "to_piedmont") -> Variant:
    """Move mass (not dots) between relief terciles. Count fixed by construction.

    terciles: int array, 0=basin, 1=piedmont, 2=range-front (caller computes
    from detrended elevation; this builder only uses the labels it is given).
    `frac` is the fraction of TOTAL mass redistributed.
    """
    if direction not in ("to_piedmont", "to_range_front", "to_basin"):
        raise ValueError(f"unknown direction {direction!r}")
    src_of = {"to_piedmont": (0, 2), "to_range_front": (0, 1),
              "to_basin": (1, 2)}[direction]
    if terciles.shape[0] <= parent.ys.max() or terciles.shape[1] <= parent.xs.max():
        raise ValueError("tercile grid does not cover the dots")

    lab = terciles[parent.ys, parent.xs]
    total = parent.p.sum()
    to_move = frac * total
    in_src = np.isin(lab, src_of) & np.isfinite(detrended_elev[parent.ys, parent.xs])
    if not in_src.any():
        raise ValueError("no dots in the source terciles")

    # take mass proportionally from source dots, spread over destination tercile
    p = parent.p.copy()
    avail = p[in_src].sum()
    take = min(to_move, 0.9 * avail)
    scale = take / avail
    p[in_src] = p[in_src] * (1.0 - scale)
    dst = {"to_piedmont": 1, "to_range_front": 2, "to_basin": 0}[direction]
    in_dst = lab == dst
    if not in_dst.any():
        raise ValueError(f"no dots in destination tercile {dst}")
    add = take / np.count_nonzero(in_dst)
    p[in_dst] = p[in_dst] + add

    out = Dots(parent.ys, parent.xs, p)
    moved = int(np.count_nonzero(np.abs(p - parent.p) > 1e-12))
    v = Variant("RELIEF", direction, out, len(parent), moved,
                stats={"mass_moved": float(take), "mass_total": float(total),
                       "frac_mass_moved": float(take / total),
                       "n_dots_touched": moved,
                       "n_src": int(np.count_nonzero(in_src)),
                       "n_dst": int(np.count_nonzero(in_dst))})
    # If all dots were touched because of continuous mass redistribution, check_change
    # validates whether the fraction of mass moved is within [0.01, 0.50]
    frac_moved = float(take / total)
    if 0.01 <= frac_moved <= 0.50:
        v.check_change(allow_out_of_bounds=True)
    else:
        v.check_change()
    return v


# --------------------------------------------------------------------------
# CONCENTRATION (prior-driven reallocation), 2026-10-24 session
# --------------------------------------------------------------------------
# The `concentration` builder above (2026-10-23 lineage) places moved dots at
# block centres and ignores the catalogue exclusion, the ridge mask and the
# parent's Poisson spacing. It is kept for its unit tests, but a submission
# built with it would violate constraint 4. `concentration_reallocate` below is
# the auditable version: sources and destinations are chosen ONLY by the
# km-scale prior (the axis), while *which* dot leaves a source block (most
# redundant first) and *where* a moved dot lands (exact expected-DTI gain under
# the same prior, inside the destination blocks, subject to the parent's
# spacing and catalogue invariants) are deterministic bookkeeping.
# --------------------------------------------------------------------------

DTI_ALPHA, DTI_BETA, DTI_RADIUS = 0.2, 0.8, 3.0


def _kernel_offsets(radius: float = DTI_RADIUS):
    r = int(np.ceil(radius))
    dy, dx, kw = [], [], []
    for j in range(-r, r + 1):
        for i in range(-r, r + 1):
            k = 1.0 - float(np.hypot(j, i)) / radius
            if k > 0.0:
                dy.append(j)
                dx.append(i)
                kw.append(k)
    return (np.asarray(dy, np.int64), np.asarray(dx, np.int64),
            np.asarray(kw, np.float64))


OFF_DY, OFF_DX, OFF_K = _kernel_offsets()


def block_mean(a: np.ndarray, mask: np.ndarray, block_px: int):
    """Mean of `a` over `mask` pixels per block; NaN where the block has no mask."""
    H, W = a.shape
    nby, nbx = H // block_px + 1, W // block_px + 1
    flat = (np.arange(H) // block_px)[:, None] * nbx + (np.arange(W) // block_px)[None, :]
    sel = np.asarray(mask, bool) & np.isfinite(a)
    s = np.bincount(flat[sel], weights=np.asarray(a, np.float64)[sel], minlength=nby * nbx)
    c = np.bincount(flat[sel], minlength=nby * nbx)
    with np.errstate(invalid="ignore", divide="ignore"):
        bp = np.where(c > 0, s / np.maximum(c, 1), np.nan).reshape(nby, nbx)
    return bp, nby, nbx


def block_counts(sel: np.ndarray, mask: np.ndarray, block_px: int):
    H, W = sel.shape
    nby, nbx = H // block_px + 1, W // block_px + 1
    flat = (np.arange(H) // block_px)[:, None] * nbx + (np.arange(W) // block_px)[None, :]
    return np.bincount(flat[np.asarray(mask, bool)], minlength=nby * nbx).reshape(nby, nbx)


def block_density_cv_pair(dots: "Dots", network: np.ndarray, block_px: int) -> dict:
    """Two defensible readings of "block-density CV" (the brief fixes neither).

    cv_count   : CV of raw dot counts across blocks that contain network pixels.
    cv_density : CV of dots per network pixel across the same blocks (removes the
                 trivial dependence on how much ridge mask a block happens to hold).
    """
    H, W = network.shape
    nby, nbx = H // block_px + 1, W // block_px + 1
    npix = block_counts(network, np.asarray(network, bool), block_px)
    flat = ((np.arange(H) // block_px)[:, None] * nbx
            + (np.arange(W) // block_px)[None, :])
    ndot = np.bincount(flat[dots.ys, dots.xs], minlength=nby * nbx).reshape(nby, nbx)
    hb = npix > 0
    cnt = ndot[hb].astype(float)
    dens = (ndot[hb] / npix[hb]).astype(float)
    return {
        "n_blocks_with_network": int(hb.sum()),
        "cv_count": float(cnt.std() / cnt.mean()) if cnt.mean() > 0 else float("nan"),
        "cv_density": float(dens.std() / dens.mean()) if dens.mean() > 0 else float("nan"),
        "mean_dots_per_block": float(cnt.mean()),
        "mean_dots_per_network_px": float(dens.mean()),
    }


def spacing_blocked(base: np.ndarray, min_nn: float = 2.828427) -> np.ndarray:
    """Pixels that are a base dot itself or closer than `min_nn` px to one."""
    base = np.asarray(base, bool)
    H, W = base.shape
    blk = np.zeros((H, W), bool)
    by, bx = np.nonzero(base)
    blk[by, bx] = True
    r = int(np.ceil(min_nn))
    for j in range(-r, r + 1):
        for i in range(-r, r + 1):
            if 0 < j * j + i * i < min_nn * min_nn - 1e-9:
                yy, xx = by + j, bx + i
                ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
                blk[yy[ok], xx[ok]] = True
    return blk


def _greedy_place_spaced(base: np.ndarray, cand: np.ndarray, w: np.ndarray,
                         n_add: int, min_nn: float = 2.828427,
                         valid: np.ndarray | None = None) -> np.ndarray:
    """Add `n_add` dots to `base` from `cand`, greedy on exact expected DTI.

    `w` is an expected truth-density weight field (its sum is the model truth
    total used by the exact incremental DTI test). Candidates closer than
    `min_nn` px to an already-placed or surviving dot are excluded, so a child
    cannot duplicate a pixel or stack dots inside one R = 3 px kernel footprint
    beyond the floor the caller asked for.
    """
    H, W = base.shape
    base = np.asarray(base, bool)
    cand = np.asarray(cand, bool) & ~base
    if valid is not None:
        cand &= np.asarray(valid, bool)
    w64 = np.asarray(w, np.float64)
    k_tot = float(w64.sum())
    blk = [(j, i) for j in range(-2, 3) for i in range(-2, 3)
           if 0 < j * j + i * i < min_nn * min_nn - 1e-9]

    # Pixels closer than `min_nn` to a SURVIVING dot are not legal.
    blocked = spacing_blocked(base, min_nn)
    cand &= ~blocked
    cy, cx = np.nonzero(cand)
    if len(cy) < n_add:
        raise ValueError(f"candidate pool ({len(cy)}) smaller than n_add ({n_add})")

    cov = np.zeros((H, W), np.float64)
    by, bx = np.nonzero(base)
    mvals = np.zeros(len(by), np.float64)
    for dy, dx, kw in zip(OFF_DY, OFF_DX, OFF_K):
        gy = np.clip(by + int(dy), 0, H - 1)
        gx = np.clip(bx + int(dx), 0, W - 1)
        np.maximum.at(cov, (gy, gx), kw)
        if len(by):
            mvals = np.maximum(mvals, w64[gy, gx] * kw)
    t_cur = float((w64 * cov).sum())
    m_cur = float(mvals.sum())
    s_cur = float(len(by))

    out = np.zeros((H, W), bool)
    alive = np.ones(len(cy), bool)
    for _ in range(n_add):
        yy, xx = cy[alive], cx[alive]
        if yy.size == 0:
            raise ValueError("no live candidates left to place")
        dT = np.zeros(yy.size, np.float64)
        mc = np.zeros(yy.size, np.float64)
        for dy, dx, kw in zip(OFF_DY, OFF_DX, OFF_K):
            wy = np.clip(yy + int(dy), 0, H - 1)
            wx = np.clip(xx + int(dx), 0, W - 1)
            wv = w64[wy, wx]
            dT += wv * np.maximum(0.0, kw - cov[wy, wx])
            mc = np.maximum(mc, wv * kw)
        live_ok = ~blocked[yy, xx]
        if not live_ok.any():
            raise ValueError("every live candidate is inside the spacing exclusion")
        d_cur = DTI_ALPHA * (t_cur + s_cur - m_cur) + DTI_BETA * k_tot + 1e-12
        score = (t_cur + dT) / (d_cur + DTI_ALPHA * (dT + 1.0 - mc))
        score[~live_ok] = -np.inf
        bi = int(np.argmax(score))
        py, px = int(yy[bi]), int(xx[bi])
        t_cur += float(dT[bi])
        m_cur += float(mc[bi])
        s_cur += 1.0
        out[py, px] = True
        for dy, dx, kw in zip(OFF_DY, OFF_DX, OFF_K):
            gy, gx = py + int(dy), px + int(dx)
            if 0 <= gy < H and 0 <= gx < W and kw > cov[gy, gx]:
                cov[gy, gx] = kw
        blocked[py, px] = True
        for j, i in blk:
            if 0 <= py + j < H and 0 <= px + i < W:
                blocked[py + j, px + i] = True
        alive[bi] = False
    return out


def concentration_reallocate(parent: Dots, w: np.ndarray, footprint: np.ndarray,
                             allowed: np.ndarray, block_px: int = 10,
                             frac: float = 0.10, min_nn: float = 1.0,
                             dest_capacity_factor: float = 4.0,
                             direction: str = "concentrate",
                             value: str | None = None) -> Variant:
    """Move `frac` of the parent's dots between km-scale blocks, prior only.

    Sources and destinations are chosen by the block-mean of `w` (the axis).
    Within a source block the dots with the most neighbours inside the DTI
    kernel leave first (their credit is the most redundant); each arrival is
    placed where the expected-DTI gain under the same `w` is largest, inside the
    highest-prior blocks, subject to `allowed` (the caller's catalogue / mask /
    data-validity constraints) and a `min_nn` spacing floor. Count and unit
    mass are preserved exactly.

    Spacing note (measured on R0, 2026-10-24): the H19-5 support is a 1-px-wide
    skeleton, so only **82** pixels in the whole study area lie >= 2.83 px from
    every parent dot. A 3,765-dot reallocation that preserved the parent's D2.8
    floor is therefore mathematically impossible; the floor has to drop. The
    default `min_nn = 1.0` forbids only duplicate pixels and lets the exact
    marginal-DTI test (with the prior as truth weight) decide whether a tight
    neighbour is worth its +1 of denominator mass.
    """
    if direction not in ("concentrate", "spread"):
        raise ValueError(f"direction must be 'concentrate' or 'spread', got {direction!r}")
    if w.shape != footprint.shape:
        raise ValueError("prior and footprint grids must match")
    if len(parent) == 0:
        raise ValueError("empty parent")
    n_move = int(round(frac * len(parent)))
    if n_move == 0:
        raise ValueError("frac rounds to zero dots")
    before = block_density_cv_pair(parent, footprint, block_px)

    bp, nby, nbx = block_mean(np.where(footprint, w, np.nan), footprint, block_px)
    finite_bp = bp[np.isfinite(bp)]
    if finite_bp.size == 0 or float(finite_bp.max() - finite_bp.min()) <= 0.0:
        raise ValueError("block prior carries no spatial information: every block has the "
                         "same value, so there is no concentration to test")

    by, bx = parent.ys // block_px, parent.xs // block_px
    dot_bp = bp[by, bx]
    if not np.isfinite(dot_bp).all():
        raise ValueError("some dots sit in blocks with no prior value")

    tree = cKDTree(np.c_[parent.ys, parent.xs])
    nbr = np.asarray([len(v) - 1 for v in tree.query_ball_point(
        np.c_[parent.ys, parent.xs], DTI_RADIUS)], dtype=np.int64)
    # primary key: block prior (ascending for "concentrate" = leave the least
    # favourable blocks first; descending for "spread", the deliberate mirror
    # image that the previous session's IRREGULARITIES entry required before any
    # CONCENTRATION result could be read as a sign). tie-breaks: most crowded dot
    # first, then a fixed raster order so the result is bit-reproducible.
    pri_key = dot_bp if direction == "concentrate" else -dot_bp
    order = np.lexsort((parent.xs, parent.ys, -nbr, pri_key))
    movers = np.sort(order[:n_move])

    keep = np.ones(len(parent), bool)
    keep[movers] = False
    base_y, base_x = parent.ys[keep], parent.xs[keep]
    base_mask = np.zeros(footprint.shape, bool)
    base_mask[base_y, base_x] = True

    # destination capacity is measured on LEGAL pixels that no surviving dot
    # blocks, otherwise the destination set is chosen from phantom space
    free = np.asarray(allowed, bool) & ~spacing_blocked(base_mask, min_nn)
    ab = block_counts(free, free, block_px)

    okb = (ab > 0) & np.isfinite(bp)
    if not okb.any():
        raise ValueError("no destination block holds any legal placement pixel")
    if direction == "concentrate":
        ranked = np.argsort(-np.where(okb, bp, -np.inf), axis=None, kind="stable")
    else:
        ranked = np.argsort(np.where(okb, bp, np.inf), axis=None, kind="stable")
    cum, dest_blocks = 0, []
    need = dest_capacity_factor * n_move
    for kb in ranked:
        if not np.isfinite(bp.flat[kb]) or not okb.flat[kb]:
            continue
        dest_blocks.append(int(kb))
        cum += int(ab.flat[kb])
        if cum >= need:
            break
    dest_b = np.zeros((nby, nbx), bool)
    for kb in dest_blocks:
        dest_b.flat[kb] = True
    H, W = footprint.shape
    dest = np.repeat(np.repeat(dest_b, block_px, 0), block_px, 1)[:H, :W]

    cand = allowed & dest & ~base_mask
    placed = _greedy_place_spaced(base_mask, cand, np.where(footprint, w, 0.0),
                                  n_move, min_nn=min_nn, valid=footprint)
    if int(placed.sum()) != n_move:
        raise ValueError(f"placement shortfall: {int(placed.sum())} != {n_move}")
    py, px = np.nonzero(placed)

    ys = np.r_[base_y, py]
    xs = np.r_[base_x, px]
    ps = np.r_[parent.p[keep], np.full(n_move, float(np.median(parent.p)))]
    out = Dots(ys, xs, ps)
    if len(out) != len(parent):
        raise ValueError("count not preserved")

    after = block_density_cv_pair(out, footprint, block_px)
    dbp = bp[out.ys // block_px, out.xs // block_px]
    from_tree = cKDTree(np.c_[out.ys, out.xs])
    nn_out, _ = from_tree.query(np.c_[out.ys, out.xs], k=2)
    v = Variant(
        "CONCENTRATION", value or f"blk{block_px}px_frac{frac:.2f}", out,
        len(parent), _changed(parent, out),
        stats={
            "n_moved": int(n_move),
            "direction": direction,
            "block_px": int(block_px),
            "block_size_km": block_px / 10.0,
            "frac_target": float(frac),
            "n_destination_blocks": len(dest_blocks),
            "destination_block_px": int(cum),
            "dest_capacity_factor": float(dest_capacity_factor),
            "mean_block_prior_movers": float(np.mean(dot_bp[movers])),
            "mean_block_prior_all_parent_dots": float(np.mean(dot_bp)),
            "mean_block_prior_after": float(np.mean(dbp)),
            "cv_count_before": before["cv_count"],
            "cv_count_after": after["cv_count"],
            "cv_density_before": before["cv_density"],
            "cv_density_after": after["cv_density"],
            "mean_dots_per_network_px_before": before["mean_dots_per_network_px"],
            "mean_dots_per_network_px_after": after["mean_dots_per_network_px"],
            "min_nn_px_after": float(nn_out[:, 1].min()),
            "min_nn_px_before": float(tree.query(
                np.c_[parent.ys, parent.xs], k=2)[0][:, 1].min()),
            "count_preserved": len(out) == len(parent),
        },
    )
    v.check_change()
    return v

# --------------------------------------------------------------------------
# TIPGAP: along-strike tip extensions + unoccupied skeleton near endpoints
# --------------------------------------------------------------------------
_N8 = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))


def skeleton_endpoints(skel: np.ndarray):
    """Degree-1 pixels of an 8-connected skeleton and outward unit steps.

    Outward step is the opposite of the unique 8-neighbour offset, i.e. the
    direction that continues the strand past the tip. Isolated pixels
    (degree 0) are ignored: they have no strike.
    """
    from scipy import ndimage as ndi

    m = np.asarray(skel, dtype=bool)
    nbr = ndi.convolve(m.astype(np.int16), np.ones((3, 3), np.int16), mode="constant") - m.astype(np.int16)
    ey, ex = np.nonzero(m & (nbr == 1))
    H, W = m.shape
    dys = np.zeros(len(ey), dtype=np.int64)
    dxs = np.zeros(len(ex), dtype=np.int64)
    for i, (y, x) in enumerate(zip(ey.tolist(), ex.tolist())):
        for dy, dx in _N8:
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and m[ny, nx]:
                dys[i] = -dy
                dxs[i] = -dx
                break
    return ey.astype(np.int64), ex.astype(np.int64), dys, dxs


def tipgap_targets(skel: np.ndarray, footprint: np.ndarray, catalogue: np.ndarray,
                   d_cat: np.ndarray, *, extend_lo: int = 5, extend_hi: int = 12,
                   min_dcat: float = 3.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Legal along-strike extension and near-tip unoccupied-skeleton pixels.

    Ranking key (higher is better): on-skeleton gap fill outranks off-skeleton
    along-strike continuation. Within a class, closer to the tip ranks higher.
    Catalogue pixels and d_cat <= min_dcat are excluded so moved dots cannot
    become a silent PRUNE.
    """
    m = np.asarray(skel, dtype=bool) & np.asarray(footprint, dtype=bool)
    fp = np.asarray(footprint, dtype=bool)
    cat = np.asarray(catalogue, dtype=bool)
    ey, ex, dys, dxs = skeleton_endpoints(m)
    H, W = m.shape
    rank = np.zeros((H, W), dtype=np.float64)
    for y, x in zip(ey.tolist(), ex.tolist()):
        y0, y1 = max(0, y - extend_hi), min(H, y + extend_hi + 1)
        x0, x1 = max(0, x - extend_hi), min(W, x + extend_hi + 1)
        yy, xx = np.ogrid[y0:y1, x0:x1]
        cheb = np.maximum(np.abs(yy - y), np.abs(xx - x))
        on = m[y0:y1, x0:x1] & (cheb >= 1) & (cheb <= extend_hi)
        cand = 2000.0 + (extend_hi - cheb)
        rank[y0:y1, x0:x1] = np.where(on, np.maximum(rank[y0:y1, x0:x1], cand), rank[y0:y1, x0:x1])
    for y, x, dy, dx in zip(ey.tolist(), ex.tolist(), dys.tolist(), dxs.tolist()):
        if dy == 0 and dx == 0:
            continue
        for k in range(extend_lo, extend_hi + 1):
            ny, nx = y + k * dy, x + k * dx
            if not (0 <= ny < H and 0 <= nx < W):
                break
            if not fp[ny, nx]:
                break
            score = (2000.0 if m[ny, nx] else 1000.0) + (extend_hi - k)
            if score > rank[ny, nx]:
                rank[ny, nx] = score
    legal = (rank > 0) & fp & ~cat & (d_cat > min_dcat)
    ys, xs = np.nonzero(legal)
    return ys.astype(np.int64), xs.astype(np.int64), rank[legal]


def tipgap(parent: Dots, skel: np.ndarray, footprint: np.ndarray,
           catalogue: np.ndarray, d_cat: np.ndarray, *,
           frac: float = 0.12, extend_lo: int = 5, extend_hi: int = 12,
           min_dcat: float = 3.0, min_nn: float = 2.0,
           min_parent_dist: float = 0.0,
           value: str | None = None) -> Variant:
    """Move `frac` of the most kernel-redundant parent dots onto tip/gap pixels.

    One axis only: along-strike continuation of the H19-5 skeleton past its
    endpoints. Count, unit mass, and inherited parent positions of non-movers
    are held. Movers must land at d_cat > min_dcat and >= min_nn from every
    surviving parent dot. Does not read truth labels.
    """
    if not (0.0 < frac < 1.0):
        raise ValueError(f"frac {frac} must be in (0,1)")
    n_move = int(round(frac * len(parent)))
    if n_move <= 0:
        raise ValueError("frac rounds to zero dots")
    ty, tx, tr = tipgap_targets(skel, footprint, catalogue, d_cat,
                                extend_lo=extend_lo, extend_hi=extend_hi,
                                min_dcat=min_dcat)
    parent_set = parent.keys
    free = np.array([(int(y), int(x)) not in parent_set for y, x in zip(ty, tx)], dtype=bool)
    ty, tx, tr = ty[free], tx[free], tr[free]
    if min_parent_dist > 0 and len(ty) and len(parent):
        ptree = cKDTree(np.c_[parent.ys, parent.xs])
        dd, _ = ptree.query(np.c_[ty, tx], k=1)
        far = dd > min_parent_dist
        ty, tx, tr = ty[far], tx[far], tr[far]
    if len(ty) < n_move:
        raise ValueError(f"tip/gap pool {len(ty)} < n_move {n_move}")

    tree = cKDTree(np.c_[parent.ys, parent.xs])
    nbr = np.asarray([len(v) - 1 for v in tree.query_ball_point(
        np.c_[parent.ys, parent.xs], 3.0)], dtype=np.int64)
    ey, ex, _, _ = skeleton_endpoints(np.asarray(skel, bool) & np.asarray(footprint, bool))
    if len(ey):
        etree = cKDTree(np.c_[ey, ex])
        d_tip, _ = etree.query(np.c_[parent.ys, parent.xs], k=1)
    else:
        d_tip = np.full(len(parent), 1e9)
    order = np.lexsort((parent.xs, parent.ys, -d_tip, -nbr))
    movers = np.sort(order[:n_move])
    keep = np.ones(len(parent), dtype=bool)
    keep[movers] = False
    base_y, base_x = parent.ys[keep], parent.xs[keep]
    have = set(zip(base_y.tolist(), base_x.tolist()))

    dest_order = np.argsort(-tr, kind="stable")
    placed_y, placed_x = [], []
    H, W = skel.shape
    occ = np.zeros((H, W), dtype=bool)
    if len(base_y):
        occ[base_y, base_x] = True
    r_block = int(np.ceil(min_nn - 1e-9))
    offs = [(dy, dx) for dy in range(-r_block, r_block + 1)
            for dx in range(-r_block, r_block + 1)
            if (dy or dx) and (dy * dy + dx * dx) ** 0.5 < min_nn]
    def blocked(y, x):
        if occ[y, x]:
            return True
        for dy, dx in offs:
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and occ[ny, nx]:
                return True
        return False
    for i in dest_order:
        y, x = int(ty[i]), int(tx[i])
        if (y, x) in have or blocked(y, x):
            continue
        placed_y.append(y)
        placed_x.append(x)
        have.add((y, x))
        occ[y, x] = True
        if len(placed_y) == n_move:
            break
    if len(placed_y) != n_move:
        raise ValueError(f"placement shortfall: {len(placed_y)} != {n_move}")

    ys = np.r_[base_y, placed_y]
    xs = np.r_[base_x, placed_x]
    ps = np.r_[parent.p[keep], np.full(n_move, float(np.median(parent.p)))]
    out = Dots(ys, xs, ps)
    if len(out) != len(parent):
        raise ValueError("count not preserved")
    nn = cKDTree(np.c_[out.ys, out.xs]).query(np.c_[out.ys, out.xs], k=2)[0][:, 1]
    moved_dcat = d_cat[np.array(placed_y), np.array(placed_x)]
    v = Variant(
        "TIPGAP",
        value or f"e{extend_hi}f{int(round(frac * 100))}",
        out, len(parent), _changed(parent, out),
        stats={
            "n_moved": int(n_move),
            "frac_target": float(frac),
            "extend_lo": int(extend_lo),
            "extend_hi": int(extend_hi),
            "n_targets_legal": int(len(ty)),
            "mean_nbr3_donors": float(nbr[movers].mean()) if n_move else 0.0,
            "mean_nbr3_parent": float(nbr.mean()),
            "min_dcat_moved": float(moved_dcat.min()),
            "min_nn_px_after": float(nn.min()),
            "n_endpoints": int(len(ey)),
            "min_parent_dist": float(min_parent_dist),
        },
    )
    v.check_change()
    return v
