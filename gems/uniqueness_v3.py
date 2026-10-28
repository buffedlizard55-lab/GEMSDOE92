"""Registry uniqueness gate, protocol interpretation PI-1 (2026-10-27).

The owner's rule: *a raster is a duplicate if its rank correlation with any
registry raster exceeds 0.90, or more than 70% of its dots fall within 3 px of
one registry raster's dots; check on the surface before placement and on the
final dots.*

What "a registry raster's dots" means (PI-1)
-------------------------------------------
* **Dot field** -- positive support <= 20% of the footprint (pre-existing
  template constant ``DENSE_SUPPORT_FRACTION``) **and** a 3 px halo covering
  <= 70% of the footprint: its dots are its literal positive pixels.
* **Surface** -- anything else (continuous probability maps, and space-filling
  dot lattices whose halo already covers more than the 70% threshold, so the
  test could not tell any candidate from chance): its dots are the top-N
  pixels by value at the candidate's budget N (deterministic seeded tie-break),
  i.e. the dots that raster would have emitted at the same density.
* Rank correlation |rho| > 0.90 is checked against **every** registry raster.
* The literal reading (every positive pixel is a dot) is also measured and
  reported; it is degenerate (a raster positive on all 5,167,373 footprint
  cells gives overlap 1.0 for any candidate) and is not used for the verdict.

All overlaps use Euclidean distance <= 3 px (the official kernel support).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr

from . import registry_cache as rc

RHO_LIMIT = 0.90
OVERLAP_LIMIT = 0.70
RADIUS_PX = 3.0
DENSE_SUPPORT_FRACTION = 0.20
HALO_LIMIT = 0.70

_OFFS = np.array([(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4)
                  if dy * dy + dx * dx <= RADIUS_PX ** 2], np.int64)


def near_fraction(our_lin_full: np.ndarray, their_lin_full: np.ndarray, shape) -> float:
    """Fraction of our dots (full-grid linear idx) within 3 px of any of theirs."""
    if our_lin_full.size == 0:
        return 0.0
    if their_lin_full.size == 0:
        return 0.0
    H, W = shape
    grid = np.zeros(H * W, np.bool_)
    grid[their_lin_full] = True
    y, x = np.divmod(our_lin_full, W)
    hit = np.zeros(our_lin_full.size, bool)
    for dy, dx in _OFFS:
        yy = y + dy; xx = x + dx
        ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
        idx = np.where(ok, yy * W + xx, 0)
        hit |= ok & grid[idx]
    return float(hit.mean())


def _rank_moments(n_total: int, values_pos: np.ndarray):
    """Average ranks of a footprint vector that is 0 except ``values_pos`` (>0).

    Returns (rank_zero, ranks_of_positive_entries, mean_rank, sd_rank)."""
    m = values_pos.size
    n0 = n_total - m
    rank_zero = (n0 + 1) / 2.0
    rp = rankdata(values_pos, method="average") + n0 if m else np.empty(0)
    mean = (n_total + 1) / 2.0
    # variance of average ranks with ties
    _, counts = np.unique(values_pos, return_counts=True) if m else (None, np.empty(0))
    ties = float(((counts.astype(float) ** 3) - counts).sum()) + (float(n0) ** 3 - n0)
    var = (n_total ** 2 - 1) / 12.0 - ties / (12.0 * n_total)
    return rank_zero, rp, mean, float(np.sqrt(max(var, 1e-12)))


def spearman_binary_vs_sparse(our_fp_idx: np.ndarray, n_fp: int, their_top: np.ndarray,
                              their_vals: np.ndarray,
                              in_our: np.ndarray | None = None) -> float:
    """Exact Spearman between our binary footprint vector and a sparse raster."""
    N = our_fp_idx.size
    p = N / n_fp
    if p <= 0 or p >= 1 or their_top.size == 0:
        return 0.0
    rz, rp, mean, sd = _rank_moments(n_fp, their_vals.astype(np.float64))
    if in_our is not None:
        hit = in_our[their_top]
        n_hit = int(hit.sum())
        e1 = (float(rp[hit].sum()) + rz * (N - n_hit)) / N
    else:
        pos_rank = np.full(n_fp, rz)
        pos_rank[their_top] = rp
        e1 = float(pos_rank[our_fp_idx].mean())
    return float(np.sqrt(p / (1 - p)) * (e1 - mean) / sd)


def surface_ranks(our_vec: np.ndarray) -> tuple[np.ndarray, float, float, float]:
    """Average ranks of a footprint vector plus (sum, mean, sd) for fast Spearman."""
    r = rankdata(np.asarray(our_vec, np.float64), method="average")
    return r, float(r.sum()), float(r.mean()), float(r.std())


def spearman_surface_vs_sparse(our_vec: np.ndarray, their_top: np.ndarray, their_vals: np.ndarray,
                               ranks: tuple | None = None) -> float:
    """Exact Spearman of a continuous footprint vector vs a sparse raster in O(support).

    rank_theirs is constant (average zero rank) off the support, so
    cov = (rz*(S_all - S_sup) + sum_sup r_o*r_t)/N - mean_o*mean_t.
    """
    n = our_vec.size
    if their_top.size == 0:
        return 0.0
    r_o, s_all, mean_o, sd_o = ranks if ranks is not None else surface_ranks(our_vec)
    rz, rp, mean_t, sd_t = _rank_moments(n, their_vals.astype(np.float64))
    ro_sup = r_o[their_top]
    e_prod = (rz * (s_all - ro_sup.sum()) + float(np.dot(ro_sup, rp))) / n
    cov = e_prod - mean_o * mean_t
    if sd_o <= 0 or sd_t <= 0:
        return 0.0
    return float(cov / (sd_o * sd_t))


def load_halo_stats(cache: Path = rc.CACHE) -> dict:
    p = cache / "halo_stats.json"
    return {d["sha"]: d for d in json.loads(p.read_text(encoding="utf-8"))}


def classify(meta: dict, halo: float | None, n_fp: int) -> str:
    sup = meta["n_fp_pos"] / n_fp
    if sup <= DENSE_SUPPORT_FRACTION and meta.get("top_complete", True) and halo is not None and halo <= HALO_LIMIT:
        return "dot_field"
    return "surface"


def audit(our_full_bool: np.ndarray | None = None, *, our_surface: np.ndarray | None = None,
          fp: rc.Footprint, shas: list[str], halo_stats: dict, n_dots_for_surface: int | None = None,
          progress: bool = False) -> dict:
    """Audit final dots (``our_full_bool``) or a pre-placement surface.

    For a surface, "our dots" are its top-N footprint cells (N =
    ``n_dots_for_surface``) and rank correlation uses the full surface.
    """
    H, W = rc.SHAPE
    if our_full_bool is not None:
        our_full_lin = np.flatnonzero(np.asarray(our_full_bool, bool).ravel())
        inv = np.full(H * W, -1, np.int64); inv[fp.lin] = np.arange(fp.n)
        our_fp = inv[our_full_lin]
        if (our_fp < 0).any():
            raise ValueError("candidate has dots outside the footprint")
        N = our_fp.size
        mode = "final_dots"
    else:
        s = np.asarray(our_surface, np.float64)
        if s.shape != (fp.n,):
            raise ValueError("surface must be a footprint vector")
        N = int(n_dots_for_surface)
        order = rc.order_desc(s, fp.tie_key)
        our_fp = np.sort(order[:N])
        our_full_lin = fp.lin[our_fp]
        mode = "surface_top_n"
    ranks = surface_ranks(np.asarray(our_surface, np.float64)) if our_surface is not None and our_full_bool is None else None
    in_our = None
    ours_samp_cached = None
    if mode == "final_dots":
        in_our = np.zeros(fp.n, np.bool_)
        in_our[our_fp] = True
        ours_full_fp = np.zeros(fp.n, np.float32); ours_full_fp[our_fp] = 1.0
        ours_samp_cached = ours_full_fp[fp.sample]
    else:
        ours_samp_cached = np.asarray(our_surface)[fp.sample]
    oy, ox = np.divmod(our_full_lin, W)
    nbr_ok = np.empty((len(_OFFS), N), np.bool_)
    nbr_idx = np.zeros((len(_OFFS), N), np.int64)
    for j, (dy, dx) in enumerate(_OFFS):
        yy = oy + dy; xx = ox + dx
        ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
        nbr_ok[j] = ok
        nbr_idx[j] = np.where(ok, yy * W + xx, 0)
    grid_buf = np.zeros(H * W, np.bool_)

    def _fast_near(their_lin: np.ndarray) -> float:
        if N == 0 or their_lin.size == 0:
            return 0.0
        grid_buf[their_lin] = True
        res = float((nbr_ok & grid_buf[nbr_idx]).any(axis=0).mean())
        grid_buf[their_lin] = False
        return res

    rows = []
    for k, sha in enumerate(shas):
        meta, arr = rc.load_summary(sha)
        m = meta["meta"]
        hs = halo_stats.get(sha, {})
        cls = classify(m, hs.get("halo_frac"), fp.n)
        top, vals = arr["top"], arr["topv"]
        if cls == "dot_field":
            dots = top
        else:
            dots = top[:N]
        ov = _fast_near(fp.lin[dots])
        # literal reading: every positive pixel is a dot
        if m.get("top_complete", True):
            lit = ov if cls == "dot_field" else _fast_near(fp.lin[top])
            lit_exact = True
        else:
            lit = 1.0 if m["n_fp_pos"] >= fp.n else max(_fast_near(fp.lin[top]), ov)
            lit_exact = m["n_fp_pos"] >= fp.n
        # rank correlation
        if m.get("top_complete", True):
            if mode == "final_dots":
                rho = spearman_binary_vs_sparse(our_fp, fp.n, top, vals, in_our=in_our)
            else:
                rho = spearman_surface_vs_sparse(np.asarray(our_surface, np.float64), top, vals, ranks=ranks)
            rho_method = "exact"
        else:
            ours_s = ours_samp_cached
            rho = float(spearmanr(ours_s, arr["samp"])[0])
            if not np.isfinite(rho):
                rho = 0.0
            rho_method = f"sampled_{fp.sample.size}"
        rows.append(dict(sha256=sha, representation=cls, n_registry_pos=int(m["n_fp_pos"]),
                         halo_frac=hs.get("halo_frac"), overlap_pi1=round(ov, 6),
                         overlap_literal=round(float(lit), 6), literal_exact=bool(lit_exact),
                         rho=round(float(rho), 6), rho_method=rho_method))
        if progress and k % 250 == 0:
            print(f"  audited {k}/{len(shas)}", flush=True)
    worst_ov = max(rows, key=lambda r: r["overlap_pi1"])
    worst_rho = max(rows, key=lambda r: abs(r["rho"]))
    worst_lit = max(rows, key=lambda r: r["overlap_literal"])
    dup = worst_ov["overlap_pi1"] > OVERLAP_LIMIT or abs(worst_rho["rho"]) > RHO_LIMIT
    return dict(mode=mode, n_dots=int(N), registry_rasters=len(rows),
                rule=dict(overlap_limit=OVERLAP_LIMIT, rho_limit=RHO_LIMIT, radius_px=RADIUS_PX,
                          interpretation="PI-1", dense_support_fraction=DENSE_SUPPORT_FRACTION,
                          halo_limit=HALO_LIMIT),
                duplicate=bool(dup),
                worst_overlap_pi1=worst_ov, worst_abs_rho=worst_rho,
                literal_reading=dict(worst=worst_lit, duplicate_under_literal=bool(
                    worst_lit["overlap_literal"] > OVERLAP_LIMIT or abs(worst_rho["rho"]) > RHO_LIMIT),
                    note="Literal reading is degenerate: any raster positive on every footprint cell gives 1.0."),
                n_overlap_over_0_5=int(sum(r["overlap_pi1"] > 0.5 for r in rows)),
                rows=rows)
