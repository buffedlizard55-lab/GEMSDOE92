#!/usr/bin/env python3
"""PEEL lane, step F1: dot-level hit matrix against every public sparse raster.

For each registry raster that is dot-like (positive support <= 25% of the
footprint) this records, per candidate dot, whether some raster pixel lies
within 3 px of it.  The matrix is stored packed (1 bit per dot), so the whole
1,800-raster comparison is a few megabytes and can be re-used to *enforce* the
owner's overlap rule during placement rather than measuring it afterwards.

Output: ``.cache/work/peel/hits.npz`` -> ``packed`` (R x ceil(N/8)) uint8,
``shas`` (R,) object, ``meta`` rows as JSON.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57.grid import load_grid  # noqa: E402

BLOBS = ROOT / ".cache" / "registry_blobs"
INDEX = ROOT / ".cache" / "trees" / "submission_blobs.json"
OUT = ROOT / ".cache" / "work" / "peel"
HALO_PX = 3
SPARSE_FRAC = 0.25


def main() -> int:
    cand = ROOT / sys.argv[1]
    inv = json.loads(INDEX.read_text())["blobs"]
    grid = load_grid()
    foot = np.asarray(grid.footprint, bool)
    n_foot = int(foot.sum())
    with rasterio.open(cand) as ds:
        a = ds.read(1)
    dots = (np.isfinite(a) & (np.nan_to_num(a) > 0)) & foot
    nd = int(dots.sum())
    # position of every dot in sorted dot-index space, via a lookup grid
    dot_id = np.full(dots.size, -1, np.int32)
    dot_id.ravel()[np.flatnonzero(dots.ravel())] = np.arange(nd, dtype=np.int32)
    dist, inds = ndi.distance_transform_edt(~dots, return_indices=True)
    nearest = dot_id.reshape(dots.shape)[inds[0], inds[1]].ravel()
    near_flat = (dist <= HALO_PX).ravel()
    del dist, inds, dot_id

    packed, shas, meta = [], [], []
    for sha, v in inv.items():
        p = BLOBS / f"{sha}.tif"
        if not p.is_file():
            continue
        try:
            with rasterio.open(p) as ds:
                if tuple(ds.shape) != foot.shape or ds.count != 1:
                    continue
                r = ds.read(1)
        except Exception:  # noqa: BLE001
            continue
        pos_flat = (np.nan_to_num(r) > 0).ravel()
        n_pos = int(pos_flat.sum())
        if not (0 < n_pos <= SPARSE_FRAC * n_foot):
            del r, pos_flat
            continue
        sub = np.flatnonzero(pos_flat & near_flat)
        ids = np.unique(nearest[sub]) if sub.size else np.empty(0, np.int64)
        bit = np.zeros(nd, bool)
        bit[ids] = True
        packed.append(np.packbits(bit))
        shas.append(sha)
        meta.append(dict(sha256=sha, repo=v["repo"], path=v["path"], n_pos=n_pos,
                         frac_pos=round(n_pos / n_foot, 5),
                         overlap=round(len(ids) / max(nd, 1), 5)))
        del r, pos_flat, sub, bit
        if len(packed) % 250 == 0:
            print(f"  {len(packed)} sparse rasters", flush=True)

    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / "hits.npz", packed=np.stack(packed),
                        shas=np.array(shas, dtype=object), n_dots=np.array([nd]))
    (OUT / "hits_meta.json").write_text(json.dumps(dict(n_dots=nd, rows=meta, halo_px=HALO_PX),
                                                   indent=1) + "\n", encoding="utf-8")
    worst = max(meta, key=lambda m: m["overlap"])
    print(f"{len(meta)} sparse rasters x {nd} dots packed; worst {worst['overlap']} "
          f"{worst['repo']} {worst['path'][-50:]}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
