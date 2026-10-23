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
def snap(parent: Dots, response: np.ndarray, max_shift: int = 2,
         footprint: np.ndarray | None = None,
         keep_out: np.ndarray | None = None) -> Variant:
    """Move each dot to the local maximum of `response` within +-max_shift px.

    Same count, same mass. `keep_out` marks pixels a dot may NOT move onto
    (catalogue exclusions). Mean displacement is reported; SNAP is exempt from
    the brief's 1-50% changed window.
    """
    if max_shift < 1:
        raise ValueError("max_shift must be >= 1")
    if response.shape[0] <= parent.ys.max() or response.shape[1] <= parent.xs.max():
        raise ValueError("response grid does not cover the dots")
    H, W = response.shape
    res = np.where(np.isfinite(response), response, -np.inf)

    occupied = parent.keys
    new_ys, new_xs = parent.ys.copy(), parent.xs.copy()
    disp = np.zeros(len(parent))
    for j, (y, x) in enumerate(zip(parent.ys.tolist(), parent.xs.tolist())):
        best_key, best_px = None, (y, x)
        for dy in range(-max_shift, max_shift + 1):
            for dx in range(-max_shift, max_shift + 1):
                yy, xx = y + dy, x + dx
                if not (0 <= yy < H and 0 <= xx < W):
                    continue
                if np.hypot(dy, dx) > max_shift:
                    continue
                if footprint is not None and not footprint[yy, xx]:
                    continue
                if keep_out is not None and keep_out[yy, xx]:
                    continue
                if (yy, xx) != (y, x) and (yy, xx) in occupied:
                    continue
                # strongest response; ties broken by smallest displacement
                key = (res[yy, xx], -np.hypot(dy, dx))
                if best_key is None or key > best_key:
                    best_key, best_px = key, (yy, xx)
        if best_key is None:
            raise ValueError(
                f"no legal SNAP destination within {max_shift}px of {(y, x)}; "
                "refusing to leave a forbidden origin or exceed the shift bound"
            )
        yy, xx = best_px
        if (yy, xx) != (y, x):
            occupied.discard((y, x))
            occupied.add((yy, xx))
        new_ys[j], new_xs[j] = yy, xx
        disp[j] = np.hypot(yy - y, xx - x)

    out = Dots(new_ys, new_xs, parent.p)
    v = Variant("SNAP", f"max{max_shift}px", out, len(parent), _changed(parent, out),
                stats={"mean_displacement_px": float(disp.mean()),
                       "median_displacement_px": float(np.median(disp)),
                       "frac_moved": float((disp > 0).mean()),
                       "max_displacement_px": float(disp.max())})
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
    v.check_change()
    return v
