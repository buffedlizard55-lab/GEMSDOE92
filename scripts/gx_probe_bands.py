#!/usr/bin/env python3
"""Cheap univariate screen: does each externally sourced band carry fault signal?

Purpose (protocol rule 4, leakage canary).  Before any model is fitted, every
candidate layer is screened alone against the mapped catalogue on the
spatially-blocked hide-and-recover holdout and against the full catalogue.
A single-feature holdout AUC above 0.90 is treated as leakage until proven
otherwise; a single-feature AUC near 0.50 means the layer carries no usable
fault-appearance signal for this task.

Bands are the externally sourced GeoDAWN / lidar stacks pinned in
``registry/lidar1m_external_manifest.json``-style provenance (see
``docs/gx-external-sources.md``) and staged in ``.cache/ext``.

Evidence class of every number printed here: HOLDOUT-DTI-adjacent diagnostic
(AUC on withheld catalogue segments) or REGISTRY-MEASUREMENT.
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
from gems57 import metric  # noqa: E402

EXT = ROOT / ".cache" / "ext"

BANDS: list[tuple[str, str, int, bool]] = [
    # (file, band description, 1-based band index, has_missing_zero)
    ("geodawn_rad_u8.tif", "K", 1, False),
    ("geodawn_rad_u8.tif", "Th", 2, False),
    ("geodawn_rad_u8.tif", "U", 3, False),
    ("geodawn_rad_u8.tif", "TC", 4, False),
    ("geodawn_extensions_u8.tif", "ThK", 1, False),
    ("geodawn_extensions_u8.tif", "UK", 2, False),
    ("geodawn_extensions_u8.tif", "UTh", 3, False),
    ("geodawn_extensions_u8.tif", "TMI_up150", 4, False),
    ("lidar_scarp_features_u8.tif", "ex_max", 1, True),
    ("lidar_scarp_features_u8.tif", "ex_mean", 2, True),
    ("lidar_scarp_features_u8.tif", "step_max", 3, True),
    ("lidar_scarp_features_u8.tif", "lapneg_max", 4, True),
    ("lidar_scarp_features_u8.tif", "lappos_max", 5, True),
    ("lidar_scarp_features_u8.tif", "downface_max", 6, True),
    ("lidar_scarp_features_u8.tif", "upface_max", 7, True),
    ("lidar_scarp_features_u8.tif", "cross_max", 8, True),
    ("lidar_scarp_features_u8.tif", "relief", 9, True),
    ("lidar_scarp_features_u8.tif", "coh100", 10, True),
]

SIGMAS = (1.5, 3.5)


def rank_transform(v: np.ndarray, foot: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Percentile-rank the band inside the footprint; missing -> 0.5."""
    out = np.full(v.shape, 0.5, np.float32)
    idx = np.flatnonzero((foot & valid).ravel())
    vals = v.ravel()[idx]
    order = np.argsort(vals, kind="stable")
    ranks = np.empty(vals.size, np.float32)
    ranks[order] = np.arange(vals.size, dtype=np.float32)
    # average ties
    sv = vals[order]
    i = 0
    while i < sv.size:
        j = i
        while j + 1 < sv.size and sv[j + 1] == sv[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = 0.5 * (i + j)
        i = j + 1
    out.ravel()[idx] = ranks / max(vals.size - 1, 1)
    return out


def auc(scores: np.ndarray, pos: np.ndarray, neg: np.ndarray, cap: int = 400_000) -> float:
    rng = np.random.default_rng(0)
    p = scores[pos]
    n = scores[neg]
    if n.size > cap:
        n = n[rng.choice(n.size, cap, replace=False)]
    if p.size == 0 or n.size == 0:
        return float("nan")
    allv = np.concatenate([p, n])
    r = np.argsort(np.argsort(allv)) + 1.0
    # average ranks for ties
    order = np.argsort(allv, kind="stable")
    sv = allv[order]
    rr = np.empty(sv.size, np.float64)
    rr[order] = np.arange(1, sv.size + 1, dtype=np.float64)
    i = 0
    while i < sv.size:
        j = i
        while j + 1 < sv.size and sv[j + 1] == sv[i]:
            j += 1
        if j > i:
            rr[order[i:j + 1]] = 0.5 * (i + 1 + j + 1)
        i = j + 1
    r = rr
    rp = r[:p.size].sum()
    return float((rp - p.size * (p.size + 1) / 2) / (p.size * n.size))


def main() -> int:
    grid = load_grid()
    foot, cat = grid.footprint, grid.catalogue
    # holdout truth: NW quadrant segments (single cheap fold, screened only)
    from gems57.holdout import build_holdout
    ctx = build_holdout(grid, hide_frac=0.20, seeds=(20,), modes=("all",))
    cell = ctx.cells[0]
    sl = cell.bbox
    cat_vis = ctx.visible(cell.key)
    hold_truth = np.zeros(cat.shape, bool)
    yy, xx = cell.truth_yx
    hold_truth[sl][yy, xx] = True

    foot_idx = np.flatnonzero(foot.ravel())
    pos_all = np.flatnonzero((cat & foot).ravel())
    neg_pool = np.setdiff1d(foot_idx, pos_all, assume_unique=False)
    rng = np.random.default_rng(1)
    neg_all = neg_pool[rng.choice(neg_pool.size, 400_000, replace=False)]

    # holdout positives/negatives inside the fold domain
    region = np.zeros(foot.shape, bool)
    region[sl] = np.asarray(cell.active, bool) | hold_truth[sl]
    hpos = np.flatnonzero(hold_truth.ravel())
    hneg_pool = np.flatnonzero((region & ~cat & foot).ravel())
    hneg = hneg_pool[rng.choice(hneg_pool.size, min(200_000, hneg_pool.size), replace=False)]

    rows = []
    for fname, desc, bidx, has_missing in BANDS:
        path = EXT / fname
        if not path.is_file():
            print(f"MISSING {path}", file=sys.stderr)
            continue
        with rasterio.open(path) as ds:
            v = ds.read(bidx).astype(np.float32)
        valid = (v > 0) if has_missing else np.ones(v.shape, bool)
        b = rank_transform(v, foot, valid)
        for sig in SIGMAS:
            sm = ndi.gaussian_filter(b, sig, mode="nearest")
            gy, gx = np.gradient(sm)
            hg = np.hypot(gy, gx)
            hyy, hyx = np.gradient(gy)
            hxy, hxx = np.gradient(gx)
            hess_min = 0.5 * (hxx + hyy - np.sqrt(np.maximum((hxx - hyy) ** 2 + 4 * hyx * hxy, 0)))
            ridge = np.maximum(-hess_min, 0.0)
            for mname, m in (("smooth", sm), ("hg", hg), ("ridge", ridge)):
                f = m.ravel()
                row = dict(band=desc, file=fname, sigma=sig, measure=mname,
                           auc_catalogue=round(auc(f, pos_all, neg_all), 4),
                           auc_holdout=round(auc(f, hpos, hneg), 4))
                rows.append(row)
                print(f"{desc:14s} s={sig} {mname:7s} AUC_cat={row['auc_catalogue']:.4f} "
                      f"AUC_hold={row['auc_holdout']:.4f}", flush=True)

    out = dict(evidence_class="HOLDOUT-SCREEN", evaluator="gems57-pooled-hide-v2 (single fold, seed 20, mode=all)",
               n_holdout_positives=int(hpos.size), n_catalogue_positives=int(pos_all.size),
               leakage_flag_threshold=0.90, rows=rows)
    dest = ROOT / "evidence" / "gx_band_screen.json"
    dest.write_text(json.dumps(out, indent=1))
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
