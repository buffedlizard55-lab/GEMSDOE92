#!/usr/bin/env python3
"""Catalogue the cached public registry (REGISTRY-MEASUREMENT, not a score).

For every cached single-band template-grid raster this records support size,
whether it is a dense surface or a dot field, the on-catalogue / near-catalogue
counts, and its overlap with the parent R0 in both directions.  The table is the
input to the leaderboard-concordance analysis and to the uniqueness gates.

Support definition = inherited literal rule: finite and > 0, inside the footprint.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import grid as grid_mod  # noqa: E402

INDEX = ROOT / ".cache" / "gemsdoe_public_registry" / "registry_index.json"
OUT = ROOT / "evidence" / "registry_catalog_20261024.csv"
DENSE = 0.20  # support fraction above which a raster is a dense surface (vendor DENSE_SUPPORT_FRACTION)


def main() -> int:
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    fp, cat = grid.footprint, grid.catalogue
    d_cat = ndi.distance_transform_edt(~cat).astype(np.float32)
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0 = (ds.read(1) > 0) & fp
    d_r0 = ndi.distance_transform_edt(~r0).astype(np.float32)
    r0_yx = np.argwhere(r0)
    r0_tree = cKDTree(r0_yx)
    index = json.loads(INDEX.read_text())
    rows = []
    for k, item in enumerate(index["rasters"]):
        with rasterio.open(item["cache_file"]) as ds:
            a = ds.read(1)
            nodata = ds.nodata
        fin = np.isfinite(a)
        sup = fin & (a > 0) & fp
        n = int(sup.sum())
        vals = a[sup]
        row = dict(
            repo=item["repo_first"], path=item["sources"][0].split("/", 1)[1], sha256=item["sha256"],
            bytes=item["bytes"], n_pos=n, support_frac=n / max(int(fp.sum()), 1),
            n_nan=int((~fin).sum()), nodata=("" if nodata is None else float(nodata)),
            pos_outside_fp=int(((a > 0) & fin & ~fp).sum()),
            binary=bool(n > 0 and np.all(vals == 1.0)),
            vmax=float(vals.max()) if n else 0.0, vmin_pos=float(vals.min()) if n else 0.0,
            vmax_all=float(np.nanmax(a)) if fin.any() else float("nan"),
            on_catalogue=int((sup & cat).sum()),
            within2=int((sup & (d_cat <= 2.0)).sum()),
            rev_overlap_r0=float((d_r0[sup] <= 3.0).mean()) if n else 0.0,  # their dots within 3 px of R0 dots
            identical_to_r0=bool(n == int(r0.sum()) and np.array_equal(sup, r0)),
        )
        row["dense"] = bool(row["support_frac"] > DENSE)
        if n and not row["dense"]:
            yx = np.argwhere(sup)
            d, _ = cKDTree(yx).query(r0_yx, k=1)
            row["fwd_overlap_r0"] = float((d <= 3.0).mean())  # R0 dots within 3 px of theirs
        else:
            row["fwd_overlap_r0"] = ""
        rows.append(row)
        if (k + 1) % 200 == 0:
            print(f"  catalogued {k + 1}/{len(index['rasters'])}", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(dict(rows=len(rows), out=str(OUT.relative_to(ROOT)),
                          dense=sum(r["dense"] for r in rows),
                          identical_to_r0=sum(r["identical_to_r0"] for r in rows),
                          empty=sum(r["n_pos"] == 0 for r in rows)), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
