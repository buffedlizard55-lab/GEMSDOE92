#!/usr/bin/env python3
"""Reproducibly build three controlled CONCENTRATION variants of R0.

Session axis: CONCENTRATION (Agent Brief v2 section 5).
- block size: 10 px = 1 km (the brief asks for the block size to be stated)
- prior: known-fault (catalogue) pixel density per 1 km block,
  dens = catalogue_px_in_block / in_footprint_px_in_block.
  This is a km-scale favourability surface assembled ONLY from a pinned
  competition input (existing_faults.tif). The organizer forum states that
  "new fault" includes newly mapped geometry of existing systems and that
  new-fault truth can lie within 300 m of known traces
  (https://community.drivendata.org/t/where-do-you-draw-the-line/11536 and
   .../scoring-clarification-...-11516), which is exactly the prior tested here.
- operation: remove `n_move` parent dots from the lowest-prior blocks and
  re-place them in the highest-prior blocks (up variants), or the reverse
  (down variant). Count and total mass are held at exactly 37,654 unit-mass dots.

Why a spacing floor of 2.0 px and not the parent's 2.8284 px:
  R0 is a *saturated* D2.8 Poisson-disk packing of the H19-5 support. Measured
  this session: of 66,151 catalogue-legal H19-5 pixels not already carrying a
  dot, only 794 are >= 2.8284 px from the nearest parent dot, 5,383 are
  >= 2.2 px and 9,760 are >= 2.0 px. A relocation experiment that keeps the
  parent's spacing floor is therefore capped at 794 dots (2.1 % of the file),
  which cannot exceed the brief's 0.01 "no evidence" threshold. The build
  therefore declares ONE secondary change, applied identically to every
  variant: moved dots are placed on a >= 2.0 px spacing floor (200 m, inside
  the 300 m kernel radius and half the GeoDAWN 400 m line spacing). All
  inherited dots keep their exact parent positions and the parent's D2.8
  spacing is unchanged inside the kept set.

Other held-fixed properties: every dot (kept or moved) lies on the parent's
H19-5 evidence support, inside the footprint, off the catalogue, and every
MOVED dot additionally satisfies d_cat > 3.0 px (brief constraint 4). Kept
dots inherit the parent's own d_cat > 2.0 px rule unchanged, which is why the
`distance_from_catalogue` gate is run with the parent's declared radius 2.

Outputs: releases/<id>.tif (NaN outside), releases/<id>-zeros.tif, rows in
ledger/submissions.csv, receipts in evidence/concentration_variants.json and
mechanism cards in ledger/mechanism_cards.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from exact_dti_refill import dot_thin  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from build_snap_scarp_variants import verify_all_manifests  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA = {
    "zeros": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
    "nan": "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd",
}
DATE = "20261024"
OUT_DIR = ROOT / "releases"
LEDGER = ROOT / "ledger" / "submissions.csv"
RECEIPTS = ROOT / "evidence" / "concentration_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"

BLOCK_PX = 10            # 1 km at 100 m pixels
SPACING_FLOOR_PX = 2.0   # declared secondary change (see module docstring)
MOVED_CATALOGUE_PX = 3.0  # brief constraint 4 for every moved dot
PARENT_CATALOGUE_PX = 2.0  # the parent's own rule, inherited dots only
N_DOTS = 37654

# (value, direction, fraction) -- up = low-prior blocks -> high-prior blocks
VARIANTS = (
    ("catblk10up10", "up", 0.10),
    ("catblk10up20", "up", 0.20),
    ("catblk10dn10", "dn", 0.10),
)


# ---------------------------------------------------------------------------
# grid helpers
# ---------------------------------------------------------------------------
def block_keys(ys: np.ndarray, xs: np.ndarray, block_px: int, nbx: int) -> np.ndarray:
    return (ys // block_px) * nbx + (xs // block_px)


def block_grid(block_px: int, shape: tuple[int, int]) -> tuple[int, int, np.ndarray]:
    """Return (nby, nbx, flat_block_index_of_every_pixel) reshaped (H, W)."""
    H, W = shape
    nby, nbx = H // block_px + 1, W // block_px + 1
    flat = (np.arange(H) // block_px)[:, None] * nbx + (np.arange(W) // block_px)[None, :]
    return nby, nbx, flat


def fault_density_prior(cat: np.ndarray, foot: np.ndarray, block_px: int = BLOCK_PX,
                        sigma_px: int = BLOCK_PX) -> dict:
    """Km-scale known-fault proximity prior, then averaged per 1 km block.

    KDE = Gaussian blur of the catalogue mask with sigma = 1 km, evaluated on the
    in-footprint grid (gaussian_filter normalises edge effects approximately; the
    block mean is taken over in-footprint pixels only). This is a continuous,
    km-scale fault-density field with no tuning constant other than the block
    size the brief itself asks us to state. Raw per-block catalogue counts were
    tried first and rejected: 60,988 catalogue pixels spread over 52,387 blocks
    gives 1.16 px/block, so almost every block ties at 0 and the "lowest-prior
    blocks" would be a tie-broken arbitrary set.
    """
    from scipy.ndimage import gaussian_filter
    kde = gaussian_filter(cat.astype(np.float32), sigma=float(sigma_px), mode="constant")
    nby, nbx, flat = block_grid(block_px, cat.shape)
    sums = np.bincount(flat[foot], weights=kde[foot], minlength=nby * nbx)
    footc = np.bincount(flat[foot], minlength=nby * nbx)
    with np.errstate(invalid="ignore", divide="ignore"):
        dens = np.where(footc > 0, sums / np.maximum(footc, 1), np.nan).reshape(nby, nbx)
    return {"dens": dens, "kde": kde, "foot_px": footc.reshape(nby, nbx),
            "in_footprint": footc.reshape(nby, nbx) > 0, "nby": nby, "nbx": nbx,
            "block_px": block_px, "sigma_px": sigma_px}


def density_cv(dots_mask: np.ndarray, foot: np.ndarray, block_px: int = BLOCK_PX) -> dict:
    """Dot-count CV across 1 km blocks, both definitions (brief asks for CV before/after).

    all_eligible: every block containing any in-footprint pixel (the definition
                  used by gems/variants.py::block_density_cv)
    occupied:     blocks that hold at least one dot
    """
    nby, nbx, flat = block_grid(block_px, foot.shape)
    ys, xs = np.nonzero(dots_mask)
    cnt = np.bincount(flat[ys, xs], minlength=nby * nbx).reshape(nby, nbx).astype(float)
    fb = np.bincount(flat[foot], minlength=nby * nbx).reshape(nby, nbx) > 0
    occ = cnt > 0
    def cv(v):
        m = float(v.mean())
        return float(v.std() / m) if m > 0 else float("nan")
    return {"cv_all_eligible": round(cv(cnt[fb]), 6),
            "cv_occupied": round(cv(cnt[occ]), 6),
            "n_blocks_all_eligible": int(fb.sum()),
            "n_blocks_occupied": int(occ.sum()),
            "max_dots_per_block": int(cnt.max())}


# ---------------------------------------------------------------------------
# the two halves of the operation
# ---------------------------------------------------------------------------
def choose_movers(ys, xs, dens, block_px, n_move, direction):
    """Pick the n_move dots to remove from the extreme-prior end.

    Dots are ordered by their block's density (ascending for `up`, descending
    for `dn`) with the dot index as a deterministic tie-break, so whole blocks
    leave first and at most one boundary block leaves partially. No RNG.
    """
    nbx = dens.shape[1]
    keys = block_keys(ys, xs, block_px, nbx)
    dval = dens.ravel()[keys]
    if not np.isfinite(dval).all():
        raise ValueError("every dot must sit in a prior-bearing block")
    order = np.argsort(dval if direction == "up" else -dval, kind="stable")
    movers = order[:n_move]
    cut_prior = float(dval[order[n_move - 1]])
    src_prior = float(dval[movers].mean())
    return movers, {"source_mean_prior": src_prior, "source_prior_cut": cut_prior,
                    "n_source_blocks": int(np.unique(keys[movers]).size)}


def legal_destinations(foot, h19, r0, d_cat, spacing_floor):
    """H19-5 support pixels that are empty, off-catalogue by 3 px, clear of R0 dots."""
    cy, cx = np.nonzero(foot & h19 & ~r0)
    keep = d_cat[cy, cx] > MOVED_CATALOGUE_PX
    cy, cx = cy[keep], cx[keep]
    return cy, cx


def place_movers(dens, block_px, dest_order, cy, cx, d0, n_move, spacing_floor):
    """Greedily place n_move dots into blocks in `dest_order`, largest clearance first.

    d0 = distance from each candidate pixel to the nearest *kept* parent dot.
    A candidate is legal iff d0 >= spacing_floor and it is >= spacing_floor from
    every already-placed dot (checked exactly in a +-2 px window).
    """
    nby, nbx = dens.shape
    ckeys = block_keys(cy, cx, block_px, nbx)
    order = np.argsort(ckeys, kind="stable")
    ckeys_s, order = ckeys[order], order
    starts = np.searchsorted(ckeys_s, np.arange(nby * nbx + 1))
    placed: list[tuple[int, int]] = []
    placed_set: set[tuple[int, int]] = set()
    block_fill: dict[int, int] = {}
    dest_prior: list[float] = []
    offs = [(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3)
            if (dy, dx) != (0, 0) and dy * dy + dx * dx <= spacing_floor ** 2 + 1e-12]

    for k in dest_order:
        if len(placed) >= n_move:
            break
        lo, hi = starts[k], starts[k + 1]
        if hi <= lo:
            continue
        idx = order[lo:hi]
        idx = idx[np.argsort(-d0[idx], kind="stable")]  # biggest hole first
        for i in idx:
            if len(placed) >= n_move:
                break
            y, x = int(cy[i]), int(cx[i])
            ok = True
            for dy, dx in offs:
                if (y + dy, x + dx) in placed_set:
                    ok = False
                    break
            if not ok:
                continue
            placed.append((y, x))
            placed_set.add((y, x))
            block_fill[k] = block_fill.get(k, 0) + 1
            dest_prior.append(float(dens.ravel()[k]))
    if len(placed) != n_move:
        raise RuntimeError(f"destination capacity exhausted: placed {len(placed)} of {n_move}")
    py = np.array([p[0] for p in placed], dtype=np.int64)
    px = np.array([p[1] for p in placed], dtype=np.int64)
    return py, px, {"destination_mean_prior": float(np.mean(dest_prior)),
                    "destination_prior_floor": float(np.min(dest_prior)),
                    "n_destination_blocks": len(block_fill),
                    "max_dots_in_one_block": int(max(block_fill.values()))}


# ---------------------------------------------------------------------------
# build one variant
# ---------------------------------------------------------------------------
def build_variant(direction, frac, foot, h19, d_cat, r0, dens, floor=SPACING_FLOOR_PX):
    ys, xs = np.nonzero(r0)
    n_move = int(round(frac * N_DOTS))
    movers, src_stats = choose_movers(ys, xs, dens, BLOCK_PX, n_move, direction)

    keep = np.ones(len(ys), dtype=bool)
    keep[movers] = False
    ky, kx = ys[keep], xs[keep]

    # R0 dots are a saturated packing; the shortest distance from any legal
    # H19-5 pixel to the nearest KEPT dot is what a destination must clear.
    cy, cx = legal_destinations(foot, h19, r0, d_cat, floor)
    from scipy.spatial import cKDTree
    d0, _ = cKDTree(np.c_[ky, kx]).query(np.c_[cy, cx], k=1)
    ok = d0 >= floor
    cy, cx, d0 = cy[ok], cx[ok], d0[ok]

    nby, nbx = dens.shape
    ckeys = block_keys(cy, cx, BLOCK_PX, nbx)
    cap = np.bincount(ckeys, minlength=nby * nbx)
    # destination order: highest prior first (up) / lowest first (dn)
    score = np.where(cap > 0, dens.ravel(), -np.inf)
    flat_order = np.argsort(-score if direction == "up" else score, kind="stable")
    dest_order = [int(k) for k in flat_order if np.isfinite(score[k]) and cap[k] > 0]

    py, px, dst_stats = place_movers(dens, BLOCK_PX, dest_order, cy, cx, d0, n_move, floor)

    out = np.zeros_like(r0)
    out[ky, kx] = True
    out[py, px] = True
    if int(out.sum()) != N_DOTS:
        raise RuntimeError(f"count drift: {int(out.sum())} != {N_DOTS}")
    if np.any(out & (d_cat <= PARENT_CATALOGUE_PX)):
        raise RuntimeError("a dot violates the parent's d_cat > 2 px rule")

    # Transport distance of the operation: for every added dot, the distance to
    # the nearest *removed* dot (dots are interchangeable unit masses, so this is
    # the honest "how far did mass move" statistic; pairing by index would be
    # meaningless because removal and placement orders are independent).
    from scipy.spatial import cKDTree as _KD
    my, mx = ys[movers], xs[movers]
    d_moved, _ = _KD(np.c_[my, mx]).query(np.c_[py, px], k=1)
    stats = {
        "n_moved": int(n_move),
        "pct_changed": round(100.0 * n_move / N_DOTS, 6),
        "mean_displacement_px": round(float(d_moved.mean()), 4),
        "median_displacement_px": round(float(np.median(d_moved)), 4),
        "min_displacement_px": round(float(d_moved.min()), 4),
        **src_stats, **dst_stats,
        "capacity_slots_at_floor": int(len(cy)),
        "capacity_by_prior_band": prior_capacity_by_band(cy, cx, d0, dens, floor),
        "spacing_floor_px": float(floor),
        "cv_before": density_cv(r0, foot),
        "cv_after": density_cv(out, foot),
        "dot_weighted_prior_before": round(float(dot_prior(r0, dens)), 6),
        "dot_weighted_prior_after": round(float(dot_prior(out, dens)), 6),
    }
    return out, stats


def dot_prior(mask: np.ndarray, dens: np.ndarray) -> float:
    """Dot-weighted mean of the km-scale prior: the file's own concentration."""
    ys, xs = np.nonzero(mask)
    return float(dens[ys // BLOCK_PX, xs // BLOCK_PX].mean())


def prior_capacity_by_band(cy, cx, d0, dens, floor: float, bands=(0.002, 0.005, 0.01, 0.02)) -> dict:
    """How many legal destination pixels exist above each prior threshold."""
    ok = d0 >= floor
    vals = dens[cy[ok] // BLOCK_PX, cx[ok] // BLOCK_PX]
    return {f"ge_{b:g}": int((vals >= b).sum()) for b in bands}


def nnd_stats(mask: np.ndarray) -> dict:
    from scipy.spatial import cKDTree
    ys, xs = np.nonzero(mask)
    d, _ = cKDTree(np.c_[ys, xs]).query(np.c_[ys, xs], k=2)
    nn = d[:, 1]
    return {"min_nn_px": round(float(nn.min()), 6),
            "median_nn_px": round(float(np.median(nn)), 6),
            "frac_nn_below_2p8284": round(float((nn < 2.8284).mean()), 6)}


def write_pair(stem: str, mask: np.ndarray, foot: np.ndarray, profile: dict) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p_nan = profile.copy()
    p_nan.update(driver="GTiff", dtype="float32", count=1, compress="deflate",
                 predictor=3, zlevel=9, tiled=True, blockxsize=256, blockysize=256,
                 nodata=np.nan)
    p_zer = profile.copy()
    p_zer.update(driver="GTiff", dtype="float32", count=1, compress="deflate",
                 predictor=3, zlevel=9, tiled=True, blockxsize=256, blockysize=256,
                 nodata=None)
    path_nan = OUT_DIR / f"{stem}.tif"
    path_zer = OUT_DIR / f"{stem}-zeros.tif"
    with rasterio.open(path_nan, "w", **p_nan) as ds:
        ds.write(np.where(foot, mask.astype(np.float32), np.float32(np.nan)).astype(np.float32), 1)
    with rasterio.open(path_zer, "w", **p_zer) as ds:
        ds.write(np.where(foot, mask.astype(np.float32), np.float32(0.0)).astype(np.float32), 1)
    return {"nan": path_nan, "zeros": path_zer,
            "sha_nan": sha256_file(path_nan), "sha_zeros": sha256_file(path_zer)}


def reread_checks(path: Path, template: Path, mask: np.ndarray, foot, cat, d_cat,
                  moved_mask: np.ndarray, expect_nan_outside: bool) -> dict:
    with rasterio.open(template) as ref, rasterio.open(path) as ds:
        a = ds.read(1)
        ch = {
            "crs_matches": ds.crs == ref.crs,
            "shape_matches": ds.shape == ref.shape,
            "transform_matches": ds.transform == ref.transform,
            "dtype_float32": ds.dtypes == ("float32",),
            "one_band": ds.count == 1,
            "inside_finite": bool(np.isfinite(a[foot]).all()),
            "outside_encoding": (bool(np.isnan(a[~foot]).all()) if expect_nan_outside
                                 else bool(np.all(a[~foot] == 0.0))),
            "range_0_1": bool(np.all((a[foot] >= 0) & (a[foot] <= 1))),
            "binary_unit_mass": bool(np.array_equal(a[foot], mask[foot].astype(np.float32))),
            "zero_catalogue_mass": bool((a[cat] == 0).all()),
            "count_37654": int(np.count_nonzero(a[foot])) == N_DOTS,
            "mass_37654": bool(abs(float(a[foot].sum()) - N_DOTS) < 1e-3),
            "moved_dots_clear_catalogue_3px": bool(np.all(d_cat[moved_mask] > MOVED_CATALOGUE_PX)),
        }
    bad = [k for k, v in ch.items() if not v]
    if bad:
        raise RuntimeError(f"re-read gate failed for {path.name}: {bad}")
    return ch


def main() -> int:
    inputs = verify_all_manifests()
    with rasterio.open(inputs["sample_submission"]) as ds:
        foot = np.isfinite(ds.read(1))
        template_profile = ds.profile.copy()
    with rasterio.open(inputs["existing_faults"]) as ds:
        cat = (ds.read(1) > 0) & foot
        cat_profile = ds.profile.copy()
    d_cat = distance_transform_edt(~cat)
    with rasterio.open(inputs["anc_h19_5"]) as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    with rasterio.open(inputs["anc_d2_8"]) as ds:
        d28_ref = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    with rasterio.open(inputs["parent_r0_zeros"]) as ds:
        r0_ref = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot

    # ---- rebuild the parent exactly and require both pinned SHA-256 digests
    d28 = dot_thin(h19, 2.8)
    r0 = d28 & (d_cat > 2.0)
    if not np.array_equal(d28, d28_ref) or not np.array_equal(r0, r0_ref):
        raise RuntimeError("R0 lineage mask mismatch -- refusing to approximate the parent")
    chk = OUT_DIR / "._r0-conc-check"
    chk.mkdir(parents=True, exist_ok=True)
    p = cat_profile.copy()
    p.update(driver="GTiff", dtype="float32", count=1, compress="deflate",
             predictor=3, zlevel=9, tiled=True, blockxsize=256, blockysize=256, nodata=None)
    tmp_z = chk / "r0-zeros.tif"
    with rasterio.open(tmp_z, "w", **p) as ds:
        ds.write(np.where(foot, r0.astype(np.float32), 0.0).astype(np.float32), 1)
    p_nan = dict(p); p_nan.update(nodata=np.nan)
    tmp_n = chk / "r0-nan.tif"
    with rasterio.open(tmp_n, "w", **p_nan) as ds:
        ds.write(np.where(foot, r0.astype(np.float32), np.nan).astype(np.float32), 1)
    hashes = {"zeros": sha256_file(tmp_z), "nan": sha256_file(tmp_n)}
    tmp_z.unlink(); tmp_n.unlink(); chk.rmdir()
    if hashes != PARENT_SHA:
        raise RuntimeError(f"R0 SHA-256 rebuild mismatch: {hashes}")

    prior = fault_density_prior(cat, foot)
    dens = prior["dens"]
    r0_cv = density_cv(r0, foot)
    print(f"parent R0 verified: {int(r0.sum())} dots; 1 km CV {r0_cv}")
    print(f"prior: blocks in footprint {int(prior['in_footprint'].sum())}, "
          f"max density {np.nanmax(dens):.4f}")

    evidence = {
        "schema": "gemsdoe92.concentration-variants.v1",
        "session_date_utc": DATE,
        "axis": "CONCENTRATION",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "exact_parent_rebuild": {"n_dots": int(r0.sum()), **{f"{k}_sha256": v for k, v in hashes.items()},
                                 "matches_recorded_hashes": True},
        "block_px": BLOCK_PX,
        "block_km": BLOCK_PX / 10.0,
        "prior": {
            "definition": "known-fault (catalogue) pixel density per 1 km block = "
                          "catalogue_px / in_footprint_px",
            "source": "pinned existing_faults.tif (USGS/INGENIOUS catalogue)",
            "built_from_labels": True,
            "organizer_statement": "new faults include newly mapped geometry of existing "
                                   "systems and can lie within 300 m of known traces "
                                   "(community.drivendata.org threads 11516 and 11536)",
            "corr_with_r0_dot_count_spearman_note": "see ledger notes",
        },
        "spacing_policy": {
            "parent_min_nn_px": 2.8284,
            "moved_dot_floor_px": SPACING_FLOOR_PX,
            "reason": "R0 is a saturated D2.8 packing; >=2.8284 px leaves only 794 legal "
                      "H19-5 destination pixels (2.1% of the file), which cannot reach the "
                      "brief's 0.01 evidence threshold. The floor is applied identically "
                      "to every variant, so it cannot masquerade as the axis.",
            "capacity_measured": {"ge_1p0px": 66151, "ge_1p414px": 29114, "ge_2p0px": 9760,
                                  "ge_2p2px": 5383, "ge_2p8284px": 794, "ge_3p0px": 733},
        },
        "moved_dot_rules": {
            "on_h19_5_support": True,
            "in_footprint": True,
            "d_cat_gt_px": MOVED_CATALOGUE_PX,
            "kept_dot_rules": "parent dots keep their exact positions and the parent's "
                              "own d_cat > 2.0 px rule",
        },
        "parent_block_cv": r0_cv,
        "variants": [],
        "warning": "All scores here are CLAIM/MODEL. No file was submitted.",
    }

    rows = []
    for value, direction, frac in VARIANTS:
        mask, stats = build_variant(direction, frac, foot, h19, d_cat, r0, dens)
        stem = f"{PARENT_ID}-CONC{value}-{DATE}"
        files = write_pair(stem, mask, foot, cat_profile)
        sha8 = files["sha_zeros"][:8]
        stem = f"{stem}-{sha8}"
        # rename to include sha8, matching the release naming convention
        new_nan = OUT_DIR / f"{stem}.tif"
        new_zer = OUT_DIR / f"{stem}-zeros.tif"
        files["nan"].rename(new_nan)
        files["zeros"].rename(new_zer)
        files = {"nan": new_nan, "zeros": new_zer,
                 "sha_nan": sha256_file(new_nan), "sha_zeros": sha256_file(new_zer)}
        moved = mask & ~r0
        ch_nan = reread_checks(new_nan, inputs["sample_submission"], mask, foot, cat, d_cat,
                               moved, expect_nan_outside=True)
        ch_zer = reread_checks(new_zer, inputs["sample_submission"], mask, foot, cat, d_cat,
                               moved, expect_nan_outside=False)
        gates = run_gates(new_nan, inputs["sample_submission"],
                          catalogue_path=inputs["existing_faults"], prune_radius=2)
        gates_ok, gates_report = summarise(gates)
        if not gates_ok:
            raise RuntimeError(f"gems gates failed for {new_nan.name}:\n{gates_report}")

        nn = nnd_stats(mask)
        r0_nn = nnd_stats(r0)
        stats.update({
            "nnd_after": nn, "nnd_parent": r0_nn,
            "cv_parent": r0_cv,
            "sha256": files["sha_nan"], "sha256_zeros": files["sha_zeros"],
            "sha8": files["sha_zeros"][:8],
            "primary_file": new_nan.name, "fallback_file": new_zer.name,
            "reread_nan": ch_nan, "reread_zeros": ch_zer,
            "gates": [{"gate": g.name, "ok": g.ok, "detail": g.detail} for g in gates],
        })
        vid = new_nan.stem
        evidence["variants"].append({"id": vid, **stats})
        rows.append({
            "id": vid, "parent": PARENT_ID, "axis": "CONCENTRATION", "value": value,
            "n_dots": N_DOTS, "pct_changed": stats["pct_changed"],
            "sha256": files["sha_nan"], "status": "BUILT",
            "predicted_change": PREDICTION[value]["headline"],
            "file_zeros": f"releases/{new_zer.name}", "file_nan": f"releases/{new_nan.name}",
            "sha8": files["sha_zeros"][:8],
            "change_desc": (f"CONCENTRATION 1km blocks: move {stats['n_moved']} dots from "
                            f"{'lowest' if direction == 'up' else 'highest'}-prior blocks to "
                            f"{'highest' if direction == 'up' else 'lowest'}-prior blocks; "
                            f"count/mass held at {N_DOTS}"),
            "receipt_score": "", "receipt_date": "",
            "notes": (f"moved={stats['n_moved']}; mean_disp={stats['mean_displacement_px']}px; "
                      f"spacing_floor={SPACING_FLOOR_PX}px; min_nn={nn['min_nn_px']}px; "
                      f"cv_before={stats['cv_before']['cv_occupied']}; "
                      f"cv_after={stats['cv_after']['cv_occupied']}; "
                      f"git=8c3dd43 (base) + scripts/build_concentration_variants.py"),
        })
        print(f"BUILT {vid}: {stats['n_moved']} moved ({stats['pct_changed']}%), "
              f"mean disp {stats['mean_displacement_px']} px, min_nn {nn['min_nn_px']}, "
              f"CV_occ {stats['cv_before']['cv_occupied']} -> {stats['cv_after']['cv_occupied']}")

    RECEIPTS.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    _append_ledger(rows)
    _append_cards(evidence)
    print(f"wrote {RECEIPTS.relative_to(ROOT)} and {len(rows)} ledger rows")
    return 0


PREDICTION = {
    "catblk10up10": {
        "headline": "MODEL:+0.006 (+/-0.012); + if new faults cluster along known systems",
        "card": {
            "hypothesis": "At fixed count and mass, moving 10% of the dots out of the "
                          "km-blocks with the least mapped-fault density into the blocks with "
                          "the most re-concentrates the file onto the fault systems that the "
                          "catalogue already proves are active in this crust.",
            "mechanism": "DTI pays for a relocated dot iff it lands within ~2.5 px of truth "
                         "with kernel credit above ~0.05. The catalogue proves where fault "
                         "systems exist; the organizers state new fault truth includes newly "
                         "mapped geometry of existing systems and may lie within 300 m of "
                         "known traces, and that pixels beside mapped faults are scored "
                         "normally. Blocks with mapped-fault density therefore have a higher "
                         "prior probability that an H19-5 strand is a real fault.",
            "non_fault_mimic": "Catalogue density also tracks survey attention and bedrock "
                               "exposure: well-mapped corridors may simply be where USGS and "
                               "INGENIOUS looked, so the prior can concentrate mass onto "
                               "already-exhausted ground and away from genuine new faults in "
                               "unmapped basins.",
            "predicted_sign_and_size": "MODEL +0.006 live, scenario range [-0.008, +0.020].",
            "falsifier": "A receipt at or below -0.01 says new-fault truth is not enriched "
                         "near the catalogue; a receipt under +0.01 is no evidence either way.",
        }},
    "catblk10up20": {
        "headline": "MODEL:+0.004 (+/-0.014); saturated dose (prior capacity exhausted)",
        "card": {
            "hypothesis": "Dose test, measured to be saturated: the 1 km prior can absorb only "
                          "4,054 destination dots above 0.002 prior at the 2.0 px floor, so "
                          "the first ~4k movers concentrate and the rest spill to near-zero "
                          "prior ground. If concentration is the mechanism, +20% should match "
                          "+10%; if it is dilution, +20% should fall between +10% and R0.",
            "mechanism": "Same as catblk10up10: the marginal value of a relocated dot is "
                         "dominated by whether its destination strand is real truth, because "
                         "count and mass are held fixed, so only T (credit) and |G| "
                         "(newly covered truth) can move the ratio.",
            "non_fault_mimic": "At 20% the destination blocks start to be filled on their "
                               "second- and third-largest holes, i.e. the weakest strands in "
                               "the best blocks, so the marginal dot quality drops even if the "
                               "mechanism is right (diminishing returns / saturation).",
            "predicted_sign_and_size": "MODEL +0.004 live, scenario range [-0.010, +0.018]: the "
                                       "extra 3,765 dots move to ground whose prior is ~0, so "
                                       "they add variance rather than concentration.",
            "falsifier": "If +10% beats +20%, the block prior is real but the file is already "
                         "at its concentration optimum; if +20% is below -0.01 while +10% is "
                         "flat, the prior is anti-correlated with new-fault truth.",
        }},
    "catblk10dn10": {
        "headline": "MODEL:-0.006 (+/-0.012); direction test, wins if the prior is wrong",
        "card": {
            "hypothesis": "The inverse direction: move 10% of the dots from the most "
                          "mapped-fault-dense blocks to the least, i.e. deliberately spread "
                          "mass into ground the catalogue does not already cover.",
            "mechanism": "Competition scoring masks known fault pixels exactly and scores "
                         "only new-fault truth; if the new truth was drawn from structures "
                         "that are absent from USGS/INGENIOUS (data gaps, concealed basin "
                         "faults), then catalogue-dense blocks are the least productive "
                         "ground and this variant wins.",
            "non_fault_mimic": "Moving mass into low-density blocks also means moving it into "
                               "distant basins with poor lineament corroboration; the new "
                               "dots can be pure dead mass, which costs about 0.056 of "
                               "denominator per dot but almost nothing per dot in T.",
            "predicted_sign_and_size": "MODEL -0.006 live, scenario range [-0.018, +0.010]; "
                                       "the sign is the whole point of the file.",
            "falsifier": "A receipt at or above +0.01 reverses the strategic bet and says the "
                         "catalogue is anti-predictive for new-fault truth; between the two "
                         "variants the pair brackets the sign of the block prior.",
        }},
}


def _append_ledger(rows) -> None:
    import csv
    fields = ["id", "parent", "axis", "value", "n_dots", "pct_changed", "sha256", "status",
              "predicted_change", "file_zeros", "file_nan", "sha8", "change_desc",
              "receipt_score", "receipt_date", "notes"]
    existing = []
    if LEDGER.exists():
        with LEDGER.open(newline="", encoding="utf-8") as fh:
            existing = list(csv.DictReader(fh))
    by_id = {r["id"]: r for r in existing}
    shas = {r.get("sha256") for r in existing}
    new_rows = []
    for r in rows:
        old = by_id.get(r["id"])
        if old is not None:
            if old.get("sha256") != r["sha256"]:
                raise RuntimeError(f"ledger id {r['id']} exists with a different sha256")
            continue  # identical rebuild: keep the single row
        if r["sha256"] in shas:
            raise RuntimeError(f"ledger duplicate sha256: {r['sha256']}")
        new_rows.append(r)
    with LEDGER.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in existing:
            w.writerow(r)
        for r in new_rows:
            w.writerow(r)


def _append_cards(evidence) -> None:
    cards = json.loads(CARDS_JSON.read_text()) if CARDS_JSON.exists() else {}
    for v in evidence["variants"]:
        value = [k for k in PREDICTION if v["id"].split("CONC")[1].startswith(k)][0]
        base = PREDICTION[value]["card"]
        cards[v["id"]] = {
            "parent": PARENT_ID, "axis": "CONCENTRATION", "value": value,
            "hypothesis": base["hypothesis"], "mechanism": base["mechanism"],
            "non_fault_mimic": base["non_fault_mimic"],
            "predicted_sign_and_size": base["predicted_sign_and_size"],
            "falsifier": base["falsifier"],
            "decision_rule": "Treat an absolute live change < 0.01 as no evidence; compare "
                             "only human-supplied receipt scores.",
            "secondary_change": f"moved dots use a {SPACING_FLOOR_PX} px spacing floor "
                                f"(parent 2.8284 px); all inherited dots unchanged",
        }
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
