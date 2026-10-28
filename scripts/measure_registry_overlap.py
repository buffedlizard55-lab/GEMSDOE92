#!/usr/bin/env python3
"""Measure registry-overlap under two explicit readings of "dots".

REGISTRY-MEASUREMENT only. This script never grants clearance: the protocol's
duplicate rule (>70% of dots within 3 px of one registry raster's dots) has an
unresolved representation question, because the pinned 17GEMSDOE witness is a
continuous probability surface that is positive on every footprint cell.

Readings reported side by side:

* ``literal``  - every positive witness cell is a dot (the reading that makes
  any nonempty candidate a duplicate).
* ``topk``     - the witness's dots are its top-K cells, K = the candidate's
  positive-cell count (the reading consistent with a fixed dot budget).

"Within 3 px" is a Euclidean disk of radius 3 cells (not a square or diamond).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import rasterio
from scipy import ndimage

RADIUS_PX = 3


def disk(radius: int) -> np.ndarray:
    """Boolean Euclidean disk structuring element of the given radius."""
    r = int(radius)
    yy, xx = np.mgrid[-r : r + 1, -r : r + 1]
    return (xx * xx + yy * yy) <= r * r


def within_radius(mask: np.ndarray, radius: int = RADIUS_PX) -> np.ndarray:
    """Cells lying within ``radius`` (Euclidean) of any True cell in ``mask``."""
    return ndimage.binary_dilation(mask, structure=disk(radius))


def overlap_fraction(candidate_dots: np.ndarray, witness_dots: np.ndarray) -> float:
    """Fraction of candidate dots lying within RADIUS_PX of a witness dot."""
    n = int(candidate_dots.sum())
    if n == 0:
        return 0.0
    near = within_radius(witness_dots)
    return float((candidate_dots & near).sum()) / n


def topk_mask(values: np.ndarray, finite: np.ndarray, k: int) -> np.ndarray:
    """Boolean mask of the k largest POSITIVE finite values.

    Only positive cells can be dots: a binary witness with fewer than k
    positives must not be padded with zero-valued background (ties at zero).
    """
    out = np.zeros(values.shape, dtype=bool)
    pos = finite & (values > 0)
    vals = values[pos]
    if k <= 0 or vals.size == 0:
        return out
    k = min(k, vals.size)
    thr = np.partition(vals, vals.size - k)[vals.size - k]
    out[pos] = vals >= thr
    return out


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def measure(witness: Path, candidate: Path) -> dict:
    with rasterio.open(witness) as ws, rasterio.open(candidate) as cs:
        if ws.crs != cs.crs or ws.shape != cs.shape or ws.transform != cs.transform:
            raise ValueError("witness and candidate grids differ (CRS/shape/transform)")
        w = ws.read(1).astype(np.float64)
        c = cs.read(1).astype(np.float64)
    w_fin = np.isfinite(w)
    c_dots = np.isfinite(c) & (c > 0)
    k = int(c_dots.sum())
    w_topk = topk_mask(w, w_fin, k)
    return {
        "witness": str(witness.name),
        "witness_sha256": sha256(witness),
        "candidate": str(candidate.name),
        "candidate_sha256": sha256(candidate),
        "radius_px": RADIUS_PX,
        "radius_definition": "Euclidean disk, cells",
        "candidate_positive_cells": k,
        "witness_finite_cells": int(w_fin.sum()),
        "witness_positive_finite_cells": int((w_fin & (w > 0)).sum()),
        "overlap_literal_every_positive_witness_cell": overlap_fraction(c_dots, w_fin & (w > 0)),
        "overlap_topk_witness_cells": overlap_fraction(c_dots, w_topk),
        "limit": 0.70,
        "evidence_class": "REGISTRY-MEASUREMENT",
        "clearance": "none - measurement only; the representation rule is unresolved",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("witness", type=Path)
    p.add_argument("candidate", type=Path)
    p.add_argument("--output", type=Path, help="write JSON here (default: stdout)")
    args = p.parse_args(argv)
    try:
        result = measure(args.witness, args.candidate)
    except (OSError, ValueError, rasterio.errors.RasterioError) as exc:
        print(f"INCONCLUSIVE: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
