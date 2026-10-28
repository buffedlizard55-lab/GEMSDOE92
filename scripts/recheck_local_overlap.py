#!/usr/bin/env python3
"""Recheck one candidate against every local GeoTIFF on the competition grid.

Scope: docs/**/*.tif and releases/*.tif in this checkout only (NOT the 2,162-raster
remote registry, which needs .cache/ and network access). Writes a JSON receipt.

Metrics, per registry raster R, for candidate C with N positive pixels:
  literal_sparse  fraction of C's dots within 3 px of R's positive pixels
                  (only when R is sparse: positive support <= 20% of footprint)
  top_n           fraction of C's dots within 3 px of R's top-N pixels by value
                  (surface reading, PI-1 in gems/uniqueness_v3.py)
  rho             Spearman rank correlation on a fixed seeded footprint sample
A dense raster (support > 20%) has literal_sparse = null; the literal reading of
that case is degenerate and is discussed in IRREGULARITIES.md (IR-1028B-5).

Usage: python scripts/recheck_local_overlap.py CANDIDATE.tif OUT.json
"""
from __future__ import annotations

import glob
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
SHAPE = (3730, 3292)
EPSG = 32611
RADIUS = 3
SAMPLE_N = 200_000
SAMPLE_SEED = 20261028


def _offsets():
    return [(a, b) for a in range(-RADIUS, RADIUS + 1) for b in range(-RADIUS, RADIUS + 1)
            if a * a + b * b <= RADIUS * RADIUS]


OFFS = _offsets()


def load(path: Path):
    with rasterio.open(path) as d:
        if d.shape != SHAPE or d.crs is None or d.crs.to_epsg() != EPSG:
            return None
        return d.read(1).astype(np.float32)


def near_fraction(ours_lin: np.ndarray, theirs_lin: np.ndarray) -> float:
    if ours_lin.size == 0 or theirs_lin.size == 0:
        return 0.0
    H, W = SHAPE
    grid = np.zeros(H * W, bool)
    grid[theirs_lin] = True
    y, x = np.divmod(ours_lin, W)
    hit = np.zeros(ours_lin.size, bool)
    for a, b in OFFS:
        Y, X = y + a, x + b
        ok = (Y >= 0) & (Y < H) & (X >= 0) & (X < W)
        hit |= ok & grid[np.where(ok, Y * W + X, 0)]
    return float(hit.mean())


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    cand_path, out_path = Path(argv[0]).resolve(), Path(argv[1]).resolve()
    cand = load(cand_path)
    if cand is None:
        print("candidate is not on the competition grid")
        return 2
    cand_flat = cand.ravel()
    ours = np.flatnonzero(cand_flat > 0)
    n = ours.size
    total = SHAPE[0] * SHAPE[1]
    sample = np.random.default_rng(SAMPLE_SEED).choice(total, SAMPLE_N, replace=False)
    rows = []
    files = sorted({p for pat in ("docs/**/*.tif", "releases/*.tif")
                    for p in glob.glob(str(ROOT / pat), recursive=True)})
    for p in files:
        p = Path(p)
        if p.resolve() == cand_path.resolve():
            continue
        try:
            a = load(p)
        except Exception as exc:  # unreadable file: record, do not hide
            rows.append({"file": str(p.relative_to(ROOT)), "error": type(exc).__name__})
            continue
        if a is None:
            rows.append({"file": str(p.relative_to(ROOT)), "error": "grid mismatch"})
            continue
        flat = a.ravel()
        npos = int((flat > 0).sum())
        lit = None
        if 0 < npos <= 0.20 * total:
            lit = near_fraction(ours, np.flatnonzero(flat > 0))
        top = near_fraction(ours, np.argpartition(-flat, n - 1)[:n]) if n else 0.0
        rho = float(spearmanr(cand_flat[sample], flat[sample]).correlation)
        rows.append({"file": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                     "positive_pixels": npos, "literal_sparse": None if lit is None else round(lit, 4),
                     "top_n": round(top, 4), "rho": round(rho, 4)})
    ok = [r for r in rows if "error" not in r]
    summary = {
        "candidate": str(cand_path.relative_to(ROOT)),
        "candidate_sha256": hashlib.sha256(cand_path.read_bytes()).hexdigest(),
        "candidate_dots": int(n),
        "rasters_checked": len(ok),
        "rasters_unreadable": len(rows) - len(ok),
        "worst_literal_sparse": max([r["literal_sparse"] for r in ok if r.get("literal_sparse") is not None] or [0]),
        "worst_top_n": max([r["top_n"] for r in ok] or [0]),
        "max_abs_rho": max([abs(r["rho"]) for r in ok] or [0]),
        "limits": {"overlap": 0.70, "rho": 0.90, "radius_px": RADIUS},
        "scope": "local checkout only; not the remote 2,162-raster registry",
        "rows": rows,
    }
    out_path.write_text(json.dumps(summary, indent=2) + "\n")
    print({k: v for k, v in summary.items() if k != "rows"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
