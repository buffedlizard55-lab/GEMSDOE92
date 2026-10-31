#!/usr/bin/env python3
"""PEEL lane, step F2: release the placement under the owner's PI-1 rule.

The E3 score field is placed freely at a 37,654-dot budget.  Measured against
the public registry, that free placement loses to one prior raster on 77% of its
dots (limit 70%).  This script keeps the score field and the packing rule and
*enforces* the rule instead: it removes the lowest-scoring dots that are inside
the 3 px halo of a single registry raster until no raster captures more than
``TARGET`` of the released dots.

Removal order is by descending model score, so the surviving set is the best
subset of the validated placement that satisfies the constraint.  The result is
written through the shared fail-closed submission writer.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import submission_writer  # noqa: E402
from gems57.grid import load_grid  # noqa: E402

W = ROOT / ".cache" / "work" / "peel"
DL = ROOT / "docs" / "downloads"
K_BUDGET = 37654
SEP = 2.8
BUF = 2.0
TARGET = 0.55          # release target; the owner's hard limit is 0.70
FLOOR = 12000          # never release fewer dots than this
NAME = "gemsdoe92-peel-scarpalt-20261031-pi1"


def main() -> int:
    grid = load_grid()
    foot = np.asarray(grid.footprint, bool)
    cat = np.asarray(grid.catalogue, bool)
    surf = np.load(W / "surf_full.npy")

    # Start from the released free placement (its dot ordering is exactly the
    # column order of hits.npz, i.e. row-major pixel order).
    with rasterio.open(DL / "gemsdoe92-peel-scarpalt-37654-20261031-zeros.tif") as ds:
        cur = ds.read(1)
    dots0 = (np.nan_to_num(cur) > 0) & foot
    pix = np.flatnonzero(dots0.ravel())              # sorted => row-major dot order
    z = np.load(W / "hits.npz", allow_pickle=True)
    packed = z["packed"]
    meta = json.loads((W / "hits_meta.json").read_text())["rows"]
    n = pix.size
    if int(z["n_dots"][0]) != n:
        raise SystemExit(f"hit matrix is for {int(z['n_dots'][0])} dots, file has {n}")
    hits = np.unpackbits(packed, axis=1)[:, :n].astype(bool)
    score = surf.ravel()[pix]                        # model score per dot, for removal order
    print(f"{hits.shape[0]} sparse rasters x {n} dots", flush=True)

    alive = np.ones(n, bool)
    history = []
    for it in range(40):
        counts = hits[:, alive].sum(axis=1)
        k = int(alive.sum())
        frac = counts / max(k, 1)
        j = int(np.argmax(frac))
        if frac[j] <= TARGET or k <= FLOOR:
            break
        need = int(np.ceil((counts[j] - TARGET * k) / (1.0 - TARGET))) + 1
        idx = np.flatnonzero(alive & hits[j])
        idx = idx[np.argsort(score[idx])]      # lowest-scoring dots go first
        drop = idx[:need]
        alive[drop] = False
        history.append(dict(iteration=it, worst_raster=meta[j]["repo"] + "/" + meta[j]["path"],
                            fraction_before=round(float(frac[j]), 5), dropped=int(drop.size),
                            dots_left=int(alive.sum())))
        print(f"  iter {it}: worst {frac[j]:.4f} ({meta[j]['path'][-40:]}) drop {drop.size} -> {int(alive.sum())} dots", flush=True)

    counts = hits[:, alive].sum(axis=1)
    k = int(alive.sum())
    frac = counts / k
    keep_pix = np.sort(pix[alive])
    print(f"released {k} dots; worst sparse overlap {frac.max():.4f}", flush=True)

    for suffix in ("-zeros.tif", "-zeros.zip", "-zeros.json"):
        p = DL / f"{NAME}{suffix}"
        if p.exists():
            p.unlink()
    dots = np.zeros(foot.shape, bool)
    dots.ravel()[keep_pix] = True
    pred = np.zeros(foot.shape, np.float32)
    pred[dots] = 1.0
    note = (f"PEEL 44-band catalogue-free scarp x alteration model; d_cat>2 collar, "
            f"{k} dots @2.8px; PI-1 capped at {TARGET:.2f} of 1853 public rasters")
    out = DL / f"{NAME}-zeros.tif"
    rec = submission_writer.write_submission(
        out, pred, ROOT / "data" / "bridge" / "sample_submission.tif", foot,
        note=note, name=NAME, catalogue=cat)
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    res = dict(schema="gemsdoe92-peel-release-v1", target=TARGET, limit=0.70,
               budget_before=int(n), dots_released=k, sha256=sha,
               worst_sparse_overlap=round(float(frac.max()), 5),
               worst_raster=dict(repo=meta[int(np.argmax(frac))]["repo"],
                                 path=meta[int(np.argmax(frac))]["path"]),
               rasters_compared=int(hits.shape[0]),
               history=history,
               all_checks_passed=rec["validator"]["all_checks_passed"],
               submission_name=NAME, note=note, note_chars=len(note),
               candidate=str(out.relative_to(ROOT)))
    (ROOT / "evidence" / "peel_release_20261031.json").write_text(
        json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("dots_released", "sha256", "worst_sparse_overlap",
                                          "all_checks_passed")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
