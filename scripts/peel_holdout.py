#!/usr/bin/env python3
"""PEEL lane, step B: spatially blocked hide-and-recover holdout (shared instrument).

Instrument: ``vendor/gems57`` -> ``gems57-pooled-hide-v2``.
``holdout.buffered_component_draw`` withholds whole 8-connected catalogue
components inside a label-blind eroded quadrant, removes a 3-px feature collar
from the *visible* label set, and masks every visible catalogue pixel
pixel-exactly during scoring.  Pooled DTI (alpha 0.2, beta 0.8, 300 m
triangular kernel) with paired physical-block bootstrap CIs.

Arms (one thing at a time)
--------------------------
E1 PEEL-scarp      : structural columns only (LiDAR scarp + 3DEP topo derivatives)
E2 PEEL-scarp+alt  : E1 + GeoDAWN radiometrics and radiometric ratios
E3 PEEL-full       : all 44 columns (E2 + magnetic upward-continuation + chi + SGMC + roads)
CTRL_R0_recipe     : d28 minus 2 px of visible catalogue (the pinned 0.2778 recipe)
CTRL_random        : uniform random dots at matched budget and exclusion collar

Everything is placed with the same NMS/2.8 px rule and the same 37,654-dot budget
so arms differ only in the score field.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import evaluate_holdout, holdout  # noqa: E402
from gems57.grid import load_grid  # noqa: E402

W = ROOT / ".cache" / "work" / "peel"
SEEDS = (20, 30)
K_BUDGET = 37654
SEP = 2.8
BUF = 2.0

SCARP = [n for n in range(8, 29)]          # sc_* + tp_*  (structurally decisive relief)
ALTER = [0, 1, 2, 3, 4, 5, 6]              # rad_*, enh_*


def nms_dots(score: np.ndarray, cand: np.ndarray, sep: float, k_max: int) -> np.ndarray:
    """Greedy non-maximum suppression placement (highest score first, min sep)."""
    H, Wd = score.shape
    flat = np.flatnonzero(cand.ravel())
    order = flat[np.argsort(-score.ravel()[flat], kind="stable")]
    r = int(np.ceil(sep))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (yy * yy + xx * xx) < sep * sep
    occ = np.zeros((H + 2 * r, Wd + 2 * r), bool)
    out = np.zeros((H, Wd), bool)
    n = 0
    for f in order:
        y, x = divmod(int(f), Wd)
        if occ[y + r, x + r]:
            continue
        out[y, x] = True
        occ[y:y + 2 * r + 1, x:x + 2 * r + 1] |= disk
        n += 1
        if n >= k_max:
            break
    return out


def symmetric_auc(score: np.ndarray, y: np.ndarray) -> float:
    s = np.nan_to_num(score.astype(np.float64), nan=0.0)
    a = float(roc_auc_score(y, s))
    return max(a, 1.0 - a)


def fit_surface(X, pos_idx, neg_idx, cols, seed):
    clf = HistGradientBoostingClassifier(
        max_iter=150, learning_rate=0.08, max_leaf_nodes=31,
        min_samples_leaf=40, l2_regularization=1.0, random_state=seed,
        early_stopping=False)
    tr = np.concatenate([pos_idx, neg_idx])
    yy = np.concatenate([np.ones(pos_idx.size, np.int8), np.zeros(neg_idx.size, np.int8)])
    clf.fit(X[tr][:, cols], yy)
    return clf


def predict_full(clf, X, cols, n, batch=600_000):
    out = np.empty(n, np.float32)
    for i in range(0, n, batch):
        out[i:i + batch] = clf.predict_proba(X[i:i + batch][:, cols])[:, 1].astype(np.float32)
    return out


def main() -> int:
    t0 = time.time()
    meta = json.loads((W / "features.json").read_text())
    names = meta["names"]
    X = np.load(W / "X.npy", mmap_mode="r")
    grid = load_grid()
    foot = np.asarray(grid.footprint, bool)
    cat = np.asarray(grid.catalogue, bool)
    idx = np.flatnonzero(foot.ravel())
    n_cells = idx.size
    if X.shape != (n_cells, len(names)):
        raise SystemExit(f"feature matrix {X.shape} does not match footprint {n_cells}")

    with rasterio.open(ROOT / "data/bridge/d28.tif") as ds:
        d28 = (np.nan_to_num(ds.read(1)) > 0) & foot

    arms = {
        "E1_PEEL_scarp": SCARP,
        "E2_PEEL_scarp_alt": sorted(set(SCARP) | set(ALTER)),
        "E3_PEEL_full": list(range(len(names))),
    }
    terms: dict[str, np.ndarray] = {}
    canaries: dict[str, float] = {}
    folds_all = []
    rng = np.random.default_rng(520810)
    negpool_all = np.flatnonzero((foot & ~cat).ravel())
    canary_done = False

    for seed in SEEDS:
        folds, _q = holdout.buffered_component_draw(grid, seed=seed)
        folds_all.extend(folds)
        vis = np.asarray(folds[0]["visible"], bool)
        d_vis = ndi.distance_transform_edt(~vis).astype(np.float32)
        pos = np.flatnonzero((vis.ravel()[idx]))
        neg_local = rng.choice(negpool_all.size, size=min(260_000, negpool_all.size), replace=False)
        neg = np.flatnonzero(np.isin(idx, negpool_all[neg_local])) if False else None
        # map global linear -> footprint row
        neg = np.searchsorted(idx, negpool_all[rng.choice(negpool_all.size, size=240_000, replace=False)])

        # leakage canaries (first seed only): every column alone, fold truth vs region
        if not canary_done:
            ys, ii = [], []
            for f in folds:
                p = np.flatnonzero(f["truth"].ravel() & foot.ravel())
                npool = np.flatnonzero((f["region"] & foot & ~cat).ravel())
                nn = rng.choice(npool, size=min(npool.size, 2 * p.size), replace=False)
                ii.extend((np.searchsorted(idx, p), np.searchsorted(idx, nn)))
                ys.extend((np.ones(p.size), np.zeros(nn.size)))
            flat = np.concatenate(ii)
            y = np.concatenate(ys)
            for j, nm in enumerate(names):
                canaries[nm] = symmetric_auc(np.asarray(X[flat, j], np.float64), y)
            canary_done = True
            worst = max(canaries.items(), key=lambda kv: kv[1])
            print(f"canary worst {worst[0]}={worst[1]:.4f} ({'PASS' if worst[1] <= 0.90 else 'FAIL'})", flush=True)
            if worst[1] > 0.90:
                raise SystemExit("LEAKAGE CANARY FAIL")

        preds: dict[str, np.ndarray] = {}
        for name, cols in arms.items():
            clf = fit_surface(X, pos, neg, cols, seed=seed)
            p = predict_full(clf, X, cols, n_cells)
            surf = np.zeros(foot.shape, np.float32)
            surf.ravel()[idx] = p
            preds[name] = surf
            print(f"  seed {seed} {name} fit+predict {time.time()-t0:.0f}s  mean p={p.mean():.5f}", flush=True)

        eligible = foot & ~cat & (d_vis > BUF)
        for name, surf in preds.items():
            preds[name] = nms_dots(surf, eligible, SEP, K_BUDGET)
        preds["CTRL_R0_recipe"] = d28 & (d_vis > BUF)
        pool = np.flatnonzero(eligible.ravel())
        rnd = np.zeros(foot.shape, bool)
        rnd.ravel()[rng.choice(pool, K_BUDGET, replace=False)] = True
        preds["CTRL_random"] = rnd

        for f in folds:
            for nm, p in preds.items():
                _s, t = evaluate_holdout.evaluate(p.astype(np.float32), f, foot)
                terms[nm] = t if nm not in terms else terms[nm] + t
        print(f"seed {seed} scored t={time.time()-t0:.0f}s", flush=True)

    cand = "E3_PEEL_full"
    s = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate=cand)
    out = dict(schema="gemsdoe92-peel-holdout-v1",
               evaluator_version=evaluate_holdout.VERSION,
               instrument_hashes=evaluate_holdout.implementation_hashes(),
               seeds=list(SEEDS), n_folds=len(folds_all),
               withheld_positive_pixels=int(sum(int(f["truth"].sum()) for f in folds_all)),
               budget_dots=K_BUDGET, nms_sep_px=SEP, exclusion_px=BUF,
               feature_sha256=meta["X_sha256"], canaries=canaries,
               canary_max=max(canaries.values()),
               summaries=s["scores"], paired=s["paired_differences"],
               best_control=s["best_comparable_control"])
    (ROOT / "evidence" / "peel_holdout_20261031.json").write_text(
        json.dumps(out, indent=1, default=float) + "\n", encoding="utf-8")
    print(f"\n{cand}: HOLDOUT-DTI {s['scores'][cand]['dti']:.6f} "
          f"CI {np.round(s['scores'][cand]['ci95'], 6).tolist()}  "
          f"withheld={out['withheld_positive_pixels']}")
    for nm, d in s["scores"].items():
        print(f"   {nm:22s} DTI {d['dti']:.6f} CI {np.round(d['ci95'], 6).tolist()}  "
              f"n={d['withheld_positive_pixels']}")
    for nm, d in s["paired_differences"].items():
        print(f"   paired vs {nm:22s} {d['delta']:+.6f} CI {np.round(d['ci95'], 6).tolist()}")
    print(f"done {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
