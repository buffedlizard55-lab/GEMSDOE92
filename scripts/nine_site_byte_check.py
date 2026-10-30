#!/usr/bin/env python3
"""Byte- and dot-level check of the nine user-listed GEMSDOE best files (2026-10-30).

Reproduce (needs network to github.com; run outside the repo):

    mkdir -p /tmp/nine && cd /tmp/nine
    for s in 24 25 27 28 30 31 32 33 36; do
      git clone -q --filter=blob:none --no-checkout --depth 1 \
        https://github.com/buffedlizard55-lab/GEMSDOE$s G$s
    done
    # then check out the exact files named in NINE_FILES below into /tmp/nine/tifs/G<site>.tif
    python scripts/nine_site_byte_check.py --tif-dir /tmp/nine/tifs \
        --out evidence/nine_site_byte_check_20261030.json

Definitions (stated, not assumed):
* dot      = finite pixel with value > 0 (NaN and 0 are not dots).
* within-3px of B = Euclidean distance (pixels, 100 m grid) from the dot to the
  nearest dot of B is <= 3.0 (the 300 m kernel radius of the competition metric).
* random baseline = uniform random dot fields with the same count inside the
  same 5,167,373-cell finite footprint, measured against GEMSDOE32's dots.

This script measures only the geometry of the submitted rasters. It is not a
leaderboard estimate and it does not clear anything for submission.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

# site -> exact file name in the owner repo at its default-branch HEAD (2026-10-30 clone)
NINE_FILES = {
    "24": "gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif",
    "25": "gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
    "27": "gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif",
    "28": "gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif",
    "30": "gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif",
    "31": "gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif",
    "32": "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
    "33": "GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
    "36": "gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif",
}
R_PX = 3.0
SEED = 20261030


def _load(path: Path):
    raw = path.read_bytes()
    with rasterio.open(path) as ds:
        a = ds.read(1).astype("float64")
        meta = dict(
            sha256=hashlib.sha256(raw).hexdigest(),
            bytes=len(raw),
            crs=str(ds.crs),
            shape=list(a.shape),
            dtype=ds.dtypes[0],
            bands=ds.count,
            transform=[float(v) for v in ds.transform[:6]],
        )
    fin = np.isfinite(a)
    meta.update(
        n_nan=int(np.isnan(a).sum()),
        n_zero=int((a == 0).sum()),
        n_dots=int((fin & (a > 0)).sum()),
        n_out_of_0_1=int((fin & ((a < 0) | (a > 1))).sum()),
        n_finite=int(fin.sum()),
    )
    return meta, fin & (a > 0), fin


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tif-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    sites = list(NINE_FILES)
    meta, dots, fin = {}, {}, {}
    for s in sites:
        m, d, f = _load(args.tif_dir / f"G{s}.tif")
        meta[s] = m
        dots[s], fin[s] = d, f

    edt = {s: distance_transform_edt(~dots[s]) for s in sites}
    pair = {}
    for a_, b_ in itertools.permutations(sites, 2):
        n = int(dots[a_].sum())
        pair[f"{a_}->{b_}"] = round(float((edt[b_][dots[a_]] <= R_PX).sum()) / n, 6)

    exact = [[a_, b_] for a_, b_ in itertools.combinations(sites, 2)
             if np.array_equal(dots[a_], dots[b_])]

    # random baseline vs GEMSDOE32 (same count, same finite footprint)
    rng = np.random.default_rng(SEED)
    ref = "32"
    cells = np.flatnonzero(fin["24"])  # NaN-encoded footprint (5,167,373 cells)
    nb = int(dots[ref].sum())
    base = []
    for _ in range(5):
        idx = rng.choice(cells, size=nb, replace=False)
        r = np.zeros(dots[ref].shape, bool)
        r.flat[idx] = True
        base.append(round(float((edt[ref][r] <= R_PX).mean()), 6))

    out = {
        "schema": "nine_site_byte_check/v1",
        "generated_utc": "2026-10-30",
        "definitions": {
            "dot": "finite and value > 0",
            "within_3px": "Euclidean distance <= 3.0 px to nearest dot of the other file",
            "footprint": "finite cells of the NaN-encoded GEMSDOE24 raster",
        },
        "files": {s: {"owner_repo": f"buffedlizard55-lab/GEMSDOE{s}", "file": NINE_FILES[s], **meta[s]}
                  for s in sites},
        "pairwise_A_fraction_within_3px_of_B": pair,
        "min_over_others_per_site": {s: min(v for k, v in pair.items() if k.startswith(s + "->")) for s in sites},
        "max_over_others_per_site": {s: max(v for k, v in pair.items() if k.startswith(s + "->")) for s in sites},
        "exact_identical_dot_sets": exact,
        "random_baseline_within_3px_of_GEMSDOE32": {"seed": SEED, "trials": base,
                                                    "mean": round(float(np.mean(base)), 6)},
        "verdict_note": "Geometry only. Not a leaderboard estimate; no file is cleared for submission.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
