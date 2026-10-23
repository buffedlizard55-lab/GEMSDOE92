#!/usr/bin/env python3
"""Screening harness (not a release builder).

Rebuilds R0 exactly, then measures the local PROXY consequence of moving a
fixed fraction of the parent's dot budget between km-scale blocks under several
candidate block priors, in both directions. Output is diagnostic only: it
orders the dose-response and the prior choice. Nothing here is a score, a gate
or a submission.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import uniform_filter, binary_dilation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from exact_dti_refill import dot_thin                       # noqa: E402
from concentration_axis import (DotState, greedy_remove, greedy_add_blocked,  # noqa: E402
                                block_index, block_mean, allocate_quotas)
from gems57 import metric                                   # noqa: E402

C = ROOT / ".cache" / "gems_inputs"
NODATA = -3.4028234663852886e+38


def rd(p):
    with rasterio.open(p) as ds:
        return ds.read(1)


def percentile_rank(a, valid):
    vals = np.asarray(a[valid], dtype=np.float32)
    vals = np.nan_to_num(vals, nan=0.0, posinf=0.0, neginf=0.0)
    knots = np.quantile(vals, np.linspace(0, 1, 1001))
    out = np.zeros(a.shape, dtype=np.float32)
    out[valid] = np.interp(vals, knots, np.linspace(0, 1, 1001)).astype(np.float32)
    return out


def build_inputs():
    tmpl = rd(C / "bridge" / "sample_submission.tif")
    foot = np.isfinite(tmpl)
    cat = (rd(C / "bridge" / "existing_faults.tif") > 0) & foot
    d_cat = np.where(cat, 0.0, 1.0)
    from scipy.ndimage import distance_transform_edt
    d_cat = distance_transform_edt(~cat)
    h19 = (np.nan_to_num(rd(C / "lineage" / "calib_h195_01922.tif"), nan=0.0) > 0) & foot
    d28 = dot_thin(h19, 2.8)
    r0 = d28 & (d_cat > 2.0)
    assert int(r0.sum()) == 37654, r0.sum()
    with rasterio.open(C / "training_features.tif") as ds:
        B = ds.read().astype(np.float32)
    B[B <= NODATA / 2.0] = np.nan
    tmi = percentile_rank(np.nan_to_num(B[2], nan=0.0), foot)
    grav = percentile_rank(np.nan_to_num(B[17], nan=0.0), foot)
    scarp = percentile_rank(np.nan_to_num(B[18], nan=0.0), foot)
    phys = (0.40 * tmi + 0.35 * grav + 0.25 * scarp).astype(np.float32)
    w = np.where(h19, 0.30 + 0.70 * phys, 0.08 * phys).astype(np.float32)
    w[~foot] = 0.0
    w[~np.isfinite(w)] = 0.0
    sgmc = (rd(C / "external" / "derived_sgmc_faults_100m_u8.tif") > 0) & foot
    sgmc_off = sgmc & ~cat & ~binary_dilation(cat, iterations=3)
    return foot, cat, d_cat, h19, r0, w, phys, sgmc_off


def make_priors(foot, cat, w, phys):
    nbr = np.zeros(cat.shape, dtype=np.int16)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            nbr += np.roll(np.roll(cat, dy, 0), dx, 1).astype(np.int16)
    nodes = cat & ((nbr == 1) | (nbr >= 3))
    # deterministic random-block null: same block geometry, shuffled ordering
    rng = np.random.default_rng(20261023)
    H, W = foot.shape
    bi, nby, nbx = block_index((H, W), 50)
    nblk = nby * nbx
    rnd = np.zeros(nblk, dtype=np.float64)
    rnd[:] = rng.permutation(np.arange(nblk)).astype(np.float64)
    rnd_field = rnd[bi]
    return {
        "w_evidence": w.astype(np.float64),
        "phys_only": phys.astype(np.float64),
        "cat_network": uniform_filter(cat.astype(np.float32), size=21, mode="constant").astype(np.float64),
        "cat_nodes": uniform_filter(nodes.astype(np.float32), size=21, mode="constant").astype(np.float64),
        "random_null": rnd_field,
    }


def concentrate(foot, d_cat, h19, r0, w, prior_field, block_px, frac,
                invert=False, seed=0, verbose=True):
    """Move ``frac`` of R0's dots from low-prior to high-prior blocks."""
    H, W = foot.shape
    bi, nby, nbx = block_index((H, W), block_px)
    nblk = nby * nbx
    cnt = np.bincount(bi[foot], minlength=nblk)
    fb = cnt > 0.5 * block_px * block_px
    bp, _ = block_mean(prior_field, bi, nblk, weight=foot)
    bp = np.where(fb, bp, np.nan)

    n_move = int(round(frac * int(r0.sum())))
    legal = h19 & (d_cat > 2.0) & foot
    elig = legal & ~r0
    fin = np.isfinite(bp)

    # ---- destination: top quintile of blocks (bottom quintile when inverted)
    if invert:
        dest_ids = np.nonzero(fin & (bp <= np.nanpercentile(bp[fin], 20)))[0]
        wts = -bp[dest_ids]
    else:
        dest_ids = np.nonzero(fin & (bp >= np.nanpercentile(bp[fin], 80)))[0]
        wts = bp[dest_ids]
    wts = wts - np.nanmin(wts)
    if not np.isfinite(wts).all() or wts.max() <= 0:
        wts = np.ones(len(dest_ids))

    # ---- source: lowest-prior blocks holding >= 2x the demand (mirrored)
    dot_b = bi[r0]
    dot_cnt = np.bincount(dot_b, minlength=nblk)
    key = np.where(fin, bp if not invert else -bp, np.inf)
    order_asc = np.argsort(key, kind="stable")
    cum = np.cumsum(dot_cnt[order_asc])
    k = int(np.searchsorted(cum, 2 * n_move)) + 1
    src_ids = order_asc[:k]
    allowed = np.isin(dot_b, src_ids)

    state = DotState(r0, w)
    t0 = time.time()
    removed = greedy_remove(state, n_move, allowed=allowed, batch=100)
    base = state.mask
    if verbose:
        print(f"    removed {len(removed)} in {time.time()-t0:.1f}s; dti(w) {state.dti():.6f}")

    avail = np.bincount(bi[elig & ~base], minlength=nblk)[dest_ids]
    quota = allocate_quotas(wts, avail, n_move)
    dest_index = np.full(nblk, -1, dtype=np.int32)
    dest_index[dest_ids] = np.arange(len(dest_ids), dtype=np.int32)
    cand_block = dest_index[bi].astype(np.int32)

    t0 = time.time()
    greedy_add_blocked(state, elig & ~base, n_move, cand_block, quota)
    if verbose:
        print(f"    added   {n_move} in {time.time()-t0:.1f}s; dti(w) {state.dti():.6f}")
    return state.mask, dict(n_move=n_move, block_px=block_px,
                            n_src_blocks=int(len(src_ids)), n_dest_blocks=int((quota > 0).sum()),
                            dot_cnt=dot_cnt, bp=bp, fb=fb, bi=bi, nblk=nblk, quota=quota)


def main():
    foot, cat, d_cat, h19, r0, w, phys, sgmc_off = build_inputs()
    priors = make_priors(foot, cat, w, phys)
    base_sgmc = metric.dti_binary(r0, sgmc_off, valid=foot, known=cat)["dti"]
    print(f"R0 vs SGMC-off-catalogue PROXY DTI = {base_sgmc:.6f}  ({int(sgmc_off.sum())} px)")
    print(f"R0 vs evidence weight w  (MODEL)   = {DotState(r0, w).dti():.6f}")

    fracs = [float(a) for a in sys.argv[1:]] or [0.10]
    block_px = 50
    for frac in fracs:
        for name, field in priors.items():
            for invert in (False, True):
                tag = "INVERTED" if invert else "concentrate"
                try:
                    mask, info = concentrate(foot, d_cat, h19, r0, w, field, block_px,
                                             frac, invert=invert, verbose=False)
                except Exception as exc:  # noqa: BLE001
                    print(f"  {name:12s} {tag:11s} f={frac:.2f}  FAILED: {exc}")
                    continue
                d = metric.dti_binary(mask, sgmc_off, valid=foot, known=cat)["dti"]
                dm = DotState(mask, w).dti()
                assert int(mask.sum()) == 37654
                assert not np.any(mask & cat)
                assert np.all(d_cat[mask] > 2.0)
                print(f"  {name:12s} {tag:11s} f={frac:.2f} blk={block_px}px  "
                      f"SGMC PROXY {d:.6f} ({d-base_sgmc:+.6f})   "
                      f"w-MODEL {dm:.6f} ({dm-DotState(r0,w).dti():+.6f})")


if __name__ == "__main__":
    main()
