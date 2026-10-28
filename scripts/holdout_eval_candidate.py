#!/usr/bin/env python3
"""Streamlined holdout evaluation using the shared gems57 stack.

Builds the catalogue hide-and-recover holdout (whole buffered segments withheld
per spatial quadrant, visible faults masked pixel-exactly), scores a candidate
binary prediction with score_cell (exact DTI, triangular 3 px kernel), pools
tp/fp/fn across all fold cells, and reports pooled DTI. Computes the SAME number
for R0 (GEMSDOE32 winner, reported holdout 0.09775) for apples-to-apples
comparison. Evidence class: HOLDOUT-DTI (evaluator gems57-pooled-hide-v2).

This is a local surrogate instrument; per holdout_validity.py it is only weakly
correlated with leaderboard CLAIMs (Spearman 0.13), so the result is reported,
not treated as an organizer score.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import grid as grid_mod, holdout as hold_mod  # noqa: E402
from gems57.metric import ALPHA, BETA  # noqa: E402


def load_pred(path):
    import rasterio
    with rasterio.open(path) as ds:
        a = ds.read(1).astype(np.float64)
    return a > 0.5


def pooled_dti(context, emitted):
    tp = fp = fn = 0.0
    n_truth = n_emit = 0
    for cell in context.cells:
        r = hold_mod.score_cell(cell, emitted)
        tp += r["tp"]; fp += r["fp"]; fn += r["fn"]
        n_truth += r["n_truth"]; n_emit += r["n_emitted"]
    den = tp + ALPHA * fp + BETA * fn
    dti = tp / den if den > 0 else 0.0
    return dict(dti=dti, tp=tp, fp=fp, fn=fn, n_truth=n_truth, n_emitted=n_emit)


def main() -> int:
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    ctx = hold_mod.build_holdout(grid)
    print(f"holdout cells={len(ctx.cells)} folds=4 seeds=2 modes=all+detached")
    for name, path in (("R0_GEMSDOE32(reported 0.09775)", "data/parent_R0_zeros.tif"),
                       ("candidate_damagezone", "docs/downloads/gemsdoe92-damagezone-dots-20261028-zeros.tif")):
        emitted = load_pred(ROOT / path)
        res = pooled_dti(ctx, emitted)
        print(f"{name}: pooled_DTI={res['dti']:.6f} tp={res['tp']:.2f} fp={res['fp']:.2f} "
              f"fn={res['fn']:.2f} n_truth={res['n_truth']} n_emitted={res['n_emitted']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
