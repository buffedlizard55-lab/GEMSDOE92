#!/usr/bin/env python3
"""Build ``.cache/registry_v3/halo_stats.json`` for ``gems.uniqueness_v3`` (shared producer).

``uniqueness_v3.load_halo_stats`` reads this file, but no producer existed in the repo
(found 2026-10-28 while wiring the full-registry audit).  This script supplies it.

For every unique registry raster that is a candidate *dot field* (in-footprint positive
support <= DENSE_SUPPORT_FRACTION and complete positive list), it records

    halo_frac = fraction of footprint cells whose Euclidean distance to the nearest
                positive cell is <= 3 px

which is the quantity ``uniqueness_v3.classify`` compares with HALO_LIMIT (0.70).
Rasters that are not dot fields get no entry; ``classify`` then treats them as surfaces
(``halo is None`` -> "surface"), exactly as before.

Parity check: the same definition is used inline by scripts/evaluate_tipcomp_candidate.py
(``(edt(pos) <= 3.0)[foot].mean()``); this script prints both values for one file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]

import lbm_data as L  # noqa: E402
from gems import registry_cache as rc  # noqa: E402
from gems import uniqueness_v3 as U  # noqa: E402


_DISK = [(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if dy * dy + dx * dx <= 9]


def halo_fraction(fp: rc.Footprint, pos_full_lin: np.ndarray) -> float:
    """Exact sparse equivalent of ``(edt(pos) <= 3)[footprint].mean()``.

    Dilates each positive cell by the Euclidean disk of radius 3 (the same
    neighbourhood as ``gems.uniqueness_v3._OFFS``) instead of running a full-grid
    distance transform.  Parity with the EDT form is asserted in the __main__ check.
    """
    H, W = rc.SHAPE
    covered = np.zeros(H * W, dtype=bool)
    if pos_full_lin.size:
        yy, xx = np.divmod(pos_full_lin.astype(np.int64), W)
        for dy, dx in _DISK:
            y2 = yy + dy
            x2 = xx + dx
            ok = (y2 >= 0) & (y2 < H) & (x2 >= 0) & (x2 < W)
            covered[y2[ok] * W + x2[ok]] = True
    return float(covered[fp.lin].mean())


def main() -> int:
    inv = json.loads((rc.CACHE / "inventory.json").read_text(encoding="utf-8"))
    shas = sorted({f["sha256"] for r in inv["repositories"] for f in r["files"]})
    fp = L.footprint()
    out, skipped = [], 0
    for i, sha in enumerate(shas):
        meta, arr = rc.load_summary(sha)
        m = meta["meta"]
        sup = m["n_fp_pos"] / fp.n
        if not (sup <= U.DENSE_SUPPORT_FRACTION and m.get("top_complete", True)):
            skipped += 1
            continue
        top = np.asarray(arr["top"], dtype=np.int64)
        out.append({"sha": sha, "halo_frac": round(halo_fraction(fp, fp.lin[top]), 9)})
        if i % 250 == 0:
            print(f"  {i}/{len(shas)}", flush=True)
    (rc.CACHE / "halo_stats.json").write_text(json.dumps(out), encoding="utf-8")
    print(f"halo_stats: {len(out)} dot-field rasters, {skipped} surfaces (no entry) -> {rc.CACHE/'halo_stats.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
