#!/usr/bin/env python3
"""PROBE ONLY - not a lane candidate, not offered on the site.

R0 minus the dots that sit on isolated skeleton fragments of the H19-5 mask
(8-connected components of size <= --max-size, default 1).  It is an R0 subset, so it is a
lane duplicate by the 70 % rule and can only be a human-selected measurement slot.

Why it exists: 8,719 of R0's 37,654 dots (23.2 %) are isolated one-pixel components and no
scored raster in the registry removes them (MEASURED, docs/WHY_R0_0_2778.md section 6).  With
credit c per removed dot the score change is about
    +/- (n/D) * (0.0556 * (1 - kbar) - 0.944 * c)       (n = removed dots, D ~ 18,200)
i.e. +0.024 if c = 0, 0 at c = 0.056 (break-even), -0.036 at c = 0.134 (R0 average).  The live score
of this one file therefore measures the credit of the fragment population directly.

Writes releases/ only (gitignored).  Uses the shared fail-closed writer.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import grid as grid_mod  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-size", type=int, default=1, help="drop dots on skeleton components of at most this many pixels")
    args = ap.parse_args()
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    fp, cat = grid.footprint, grid.catalogue
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0 = (ds.read(1) > 0) & fp
    with rasterio.open(ROOT / "data" / "bridge" / "h19_5.tif") as ds:
        h = np.nan_to_num(ds.read(1)) > 0
    lab, _ = ndi.label(h, structure=np.ones((3, 3)))
    sizes = np.bincount(lab.ravel())
    sizes[0] = 0
    drop = r0 & (sizes[lab] <= args.max_size)
    keep = r0 & ~drop
    out = np.zeros(fp.shape, np.float32)
    out[keep] = 1.0
    cid = hashlib.sha256(np.ascontiguousarray(out).tobytes()).hexdigest()[:8]
    name = f"GEMSDOE92-PROBE-R0-minus-fragments-le{args.max_size}-{cid}"
    note = f"PROBE: R0 minus {int(drop.sum())} dots on <= {args.max_size}px skeleton fragments; R0 subset (lane duplicate); measurement only"
    assert len(note) <= 140 and len(name) <= 140
    path = ROOT / "releases" / f"{name}-zeros.tif"
    rec = write_submission(path, out, ROOT / "data" / "bridge" / "sample_submission.tif", fp, note=note, name=name,
                           catalogue=cat, metadata=dict(probe=True, parent="h33-h33-2-b2", dropped=int(drop.sum())))
    print(f"wrote {path.name}: kept {int(keep.sum())} of {int(r0.sum())} dots (dropped {int(drop.sum())}); sha256 {rec['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
