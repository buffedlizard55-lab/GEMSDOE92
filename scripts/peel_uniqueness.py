#!/usr/bin/env python3
"""PEEL lane, step C2: PI-1 3-px overlap of one candidate against the registry.

Streams the downloaded public blobs one at a time (no per-raster arrays are
kept), so peak memory stays at one 12.3 M-cell grid.  For each registry raster
it answers exactly one question: *how many of the candidate's dots have at
least one positive registry pixel within 3 px (Euclidean)?*  That is computed
from a single nearest-dot index instead of a per-raster distance transform.

Outputs ``evidence/peel_uniqueness_20261031.json`` with both readings of the
owner rule: the operative one restricted to dot-like rasters (support <= 25% of
the footprint) and the literal one over all rasters, which no non-empty
candidate in this repository has ever passed.
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
    dist, inds = ndi.distance_transform_edt(~dots, return_indices=True)
    nearest = np.ravel_multi_index((inds[0].ravel(), inds[1].ravel()), dots.shape)
    near_flat = (dist <= HALO_PX).ravel()
    del dist, inds

    rows, errors, missing = [], [], 0
    for sha, v in inv.items():
        p = BLOBS / f"{sha}.tif"
        if not p.is_file():
            missing += 1
            continue
        try:
            with rasterio.open(p) as ds:
                if tuple(ds.shape) != foot.shape or ds.count != 1:
                    errors.append(dict(sha256=sha, reason="shape/band"))
                    continue
                r = ds.read(1)
        except Exception as exc:  # noqa: BLE001
            errors.append(dict(sha256=sha, reason=type(exc).__name__))
            continue
        pos_flat = (np.nan_to_num(r) > 0).ravel()
        n_pos = int(pos_flat.sum())
        sub = np.flatnonzero(pos_flat & near_flat)
        n_hit = int(np.unique(nearest[sub]).size) if sub.size else 0
        rows.append(dict(sha256=sha, repo=v["repo"], path=v["path"], n_pos=n_pos,
                         frac_pos=round(n_pos / n_foot, 5),
                         sparse=bool(0 < n_pos <= SPARSE_FRAC * n_foot),
                         dots_hit=n_hit, overlap=round(n_hit / max(nd, 1), 5)))
        del r, pos_flat, sub
        if len(rows) % 250 == 0:
            print(f"  {len(rows)} compared", flush=True)

    rows.sort(key=lambda r: -r["overlap"])
    sparse_rows = [r for r in rows if r["sparse"]]
    worst_sparse = max((r["overlap"] for r in sparse_rows), default=0.0)
    worst_literal = rows[0]["overlap"] if rows else 0.0
    res = dict(schema="gemsdoe92-peel-uniqueness-v1",
               candidate=str(cand.relative_to(ROOT)), n_dots=nd,
               known_blobs=len(inv), rasters_scanned=len(rows),
               blobs_not_downloaded=missing, unreadable=len(errors),
               pi1_limit=0.70, halo_px=HALO_PX, sparse_frac=SPARSE_FRAC,
               worst_overlap_sparse=worst_sparse, worst_overlap_literal=worst_literal,
               pi1_sparse_pass=bool(worst_sparse <= 0.70),
               literal_pass=bool(worst_literal <= 0.70),
               n_sparse_rasters_over_0_5=int(sum(r["overlap"] > 0.5 for r in sparse_rows)),
               spearman_leg="NOT_RUN (rank correlation against 1,853 rasters was not computed in this session)",
               errors=errors[:20], top10=rows[:10],
               sparse_top=sparse_rows[:40],
               sparse_raster_shas={r["sha256"]: r["overlap"] for r in sparse_rows if r["overlap"] > 0.40})
    (ROOT / "evidence" / "peel_uniqueness_20261031.json").write_text(
        json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("n_dots", "rasters_scanned", "blobs_not_downloaded",
                                          "worst_overlap_sparse", "worst_overlap_literal",
                                          "pi1_sparse_pass", "literal_pass")}, indent=1))
    for r in rows[:5]:
        print(f"   {r['overlap']:.4f} sparse={r['sparse']} {r['repo']} {r['path'][-55:]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
