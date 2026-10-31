#!/usr/bin/env python3
"""GX lane: hide-and-recover validation of the externally sourced feature model.

Protocol compliance
-------------------
* Rule 2 (reuse, don't rebuild): the folds come from the shared
  ``gems57.holdout.buffered_component_draw`` (whole catalogue components
  withheld inside label-blind eroded quadrants, 3 px feature buffer), and the
  score comes from the shared ``gems57.evaluate_holdout`` (pooled DTI,
  alpha 0.2 / beta 0.8, 300 m triangular kernel, visible faults masked
  pixel-exactly) with ``pooled_summary``'s paired 20 km block bootstrap.
* Rule 3 (label every number): everything written to
  ``evidence/gx_holdout.json`` carries ``evidence_class``.
  HOLDOUT-DTI values are measured by the shared evaluator, not projected.
* Rule 4 (leakage canary): every feature is screened alone on the holdout
  first; any feature with a solo holdout AUC above 0.90 is dropped from the
  model and reported.

Model
-----
Stage 1 is a logistic regression on 47 externally derived layers (lidar scarp
operators, GeoDAWN radiometric / magnetic contacts, orientation coherence,
distance to the SGMC compilation, distance to thermal indicators).  It is
refit for every draw from that draw's **visible** catalogue only.  Dot
emission is ridge thinning: highest-probability pixel first, then a disc of
radius ``spacing`` is blocked out, until the budget is reached, and every dot
must be more than 2 px from the visible catalogue (the R0 rule).

Arms
----
``gx_s{spacing}_n{budget}`` candidate arms, plus two controls:
``r0_recipe``  H19-5 skeleton thinned to 2.8 px with d_visible > 2
               (the recipe that produced the 0.2778 CLAIM lineage);
``random``     same number of dots placed uniformly at random in the same mask.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
import gx_features as F  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa: E402

OUT = ROOT / "evidence" / "gx_holdout.json"
PCACHE = ROOT / ".cache" / "gx"
SEEDS = (20, 30)
SPACINGS = (2.0, 2.5, 3.0)
BUDGETS = (25_000, 37_654, 50_000, 65_000, 80_000)
LEAK_AUC = 0.90
NEG_SAMPLE = 300_000


def nms_dots(order_lin: np.ndarray, shape, min_dist: float, n: int) -> np.ndarray:
    """Take ``order_lin`` in order, blocking a disc of radius ``min_dist``."""
    H, W = shape
    block = np.zeros(H * W, bool)
    taken = np.zeros(H * W, bool)
    r = int(np.ceil(min_dist))
    offs = np.array([dy * W + dx for dy in range(-r, r + 1) for dx in range(-r, r + 1)
                     if dy * dy + dx * dx <= min_dist * min_dist], np.int64)
    cnt = 0
    for c in order_lin:
        if block[c]:
            continue
        taken[c] = True
        cnt += 1
        nb = c + offs
        nb = nb[(nb >= 0) & (nb < H * W)]
        block[nb] = True
        if cnt >= n:
            break
    return taken.reshape(H, W)


def auc(scores: np.ndarray, pos: np.ndarray, neg: np.ndarray) -> float:
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    allv = np.concatenate([scores[pos], scores[neg]])
    order = np.argsort(allv, kind="stable")
    sv = allv[order]
    r = np.empty(sv.size, np.float64)
    r[order] = np.arange(1, sv.size + 1, dtype=np.float64)
    i = 0
    while i < sv.size:                      # average ties
        j = i
        while j + 1 < sv.size and sv[j + 1] == sv[i]:
            j += 1
        if j > i:
            r[order[i:j + 1]] = 0.5 * (i + 1 + j + 1)
        i = j + 1
    rp = r[:pos.size].sum()
    return float((rp - pos.size * (pos.size + 1) / 2) / (pos.size * neg.size))


def main() -> int:
    t0 = time.time()
    F.build()
    meta, mm = F.load()
    names = meta["feature_names"]
    nf = meta["n_features"]
    grid = grid_mod.load_grid()
    foot, cat = grid.footprint, grid.catalogue
    H, W = foot.shape
    NPX = H * W

    # ---- folds -------------------------------------------------------------
    draws = []
    for seed in SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        draws.extend([(seed, f) for f in folds])

    # ---- shared sample rows (catalogue positives + random negatives) --------
    rng = np.random.default_rng(20261031)
    cat_idx = np.flatnonzero((cat & foot).ravel())
    neg_pool = np.flatnonzero((foot & ~cat).ravel())
    neg_idx = rng.choice(neg_pool, NEG_SAMPLE, replace=False)
    sample_rows = np.concatenate([cat_idx, neg_idx])
    n_pos_rows = cat_idx.size

    X = np.empty((nf, sample_rows.size), np.float32)
    for i in range(nf):
        arr = np.asarray(mm[i])
        X[i] = arr[sample_rows]
    del mm
    Xs = X.T.astype(np.float64)
    mu = Xs.mean(axis=0)
    sd = Xs.std(axis=0)
    sd[sd < 1e-9] = 1.0
    Z = (Xs - mu) / sd

    # ---- leakage canaries (solo AUC on pooled holdout) ----------------------
    hpos = np.zeros(NPX, bool)
    for _, f in draws:
        tr = np.asarray(f["truth"], bool)
        hpos |= (tr & foot).ravel()
    hneg = rng.choice(np.flatnonzero((foot & ~cat).ravel()), 200_000, replace=False)
    canaries = []
    mm2 = np.memmap(ROOT / meta["data"], dtype=np.float32, mode="r", shape=(nf, NPX))
    for i in range(nf):
        arr = np.asarray(mm2[i])
        canaries.append(dict(feature=names[i], auc_holdout=round(auc(arr, np.flatnonzero(hpos), hneg), 4)))
    leaked = [c["feature"] for c in canaries if c["auc_holdout"] > LEAK_AUC]
    keep = [i for i in range(nf) if names[i] not in leaked]
    print(f"canaries: {len(leaked)} feature(s) above {LEAK_AUC}: {leaked}", flush=True)

    # ---- fit one model per draw (visible catalogue only) --------------------
    coefs, inters = [], []
    for seed, f in draws:
        vis = np.asarray(f["visible"], bool)
        vis_rows = np.flatnonzero(vis.ravel())
        pos_mask = np.isin(sample_rows, vis_rows)
        y = np.zeros(sample_rows.size, np.int8)
        y[pos_mask] = 1
        lr = LogisticRegression(max_iter=400, C=1.0, n_jobs=1)
        lr.fit(Z, y)
        w = np.zeros(nf)
        w[keep] = lr.coef_[0][keep]
        coefs.append(w / sd)
        inters.append(float(lr.intercept_[0] - float(w @ mu)))
        print(f"  fit seed={seed} fold={f.get('key')} positives={int(y.sum())}", flush=True)

    # ---- one streaming pass produces p for every draw -----------------------
    P = np.zeros((len(draws), NPX), np.float32)
    for i in range(nf):
        arr = np.asarray(mm2[i]).astype(np.float32)
        for j in range(len(draws)):
            P[j] += coefs[j][i] * arr
        del arr
    for j in range(len(draws)):
        P[j] += np.float32(inters[j])
    np.save(PCACHE / "gx_holdout_P.npy", P.astype(np.float16))
    del mm2, X, Xs, Z
    print(f"[{time.time()-t0:6.0f}s] probability surfaces ready", flush=True)

    # ---- arms, per draw ----------------------------------------------------
    h19 = np.zeros((H, W), bool)
    with __import__("rasterio").open(ROOT / "data" / "bridge" / "h19_5.tif") as ds:
        h19 = np.nan_to_num(ds.read(1)) > 0
    d28 = np.zeros((H, W), bool)
    with __import__("rasterio").open(ROOT / "data" / "bridge" / "d28.tif") as ds:
        d28 = np.nan_to_num(ds.read(1)) > 0

    terms: dict[str, np.ndarray] = {}
    per_fold: dict[str, list] = {}
    dot_counts: dict[str, list] = {}

    for j, (seed, f) in enumerate(draws):
        vis = np.asarray(f["visible"], bool)
        dvis = ndi.distance_transform_edt(~vis)
        elig = foot & (dvis > 2.0)
        p = P[j].reshape(H, W)
        pv = np.where(elig, p, np.float32(-1e9))
        idx = np.flatnonzero(elig.ravel())
        order = idx[np.argsort(-pv.ravel()[idx], kind="stable")]
        arms: dict[str, np.ndarray] = {}
        for sp in SPACINGS:
            for bud in BUDGETS:
                arms[f"gx_s{sp}_n{bud}"] = nms_dots(order, (H, W), sp, bud).astype(np.float32)
        elig_r0 = h19 & foot & (dvis > 2.0)
        arms["r0_recipe"] = nms_dots(np.flatnonzero(elig_r0.ravel()), (H, W), 2.8, 10 ** 9).astype(np.float32)
        n_rand = int(arms["r0_recipe"].sum())
        ridx = rng.choice(np.flatnonzero(elig.ravel()), n_rand, replace=False)
        rnd = np.zeros((H, W), np.float32)
        rnd.flat[ridx] = 1.0
        arms["random"] = rnd
        for name, arr in arms.items():
            sc, tm = evaluate_holdout.evaluate(arr, f, foot)
            terms[name] = tm if name not in terms else terms[name] + tm
            per_fold.setdefault(name, []).append(round(float(sc["dti"]), 6))
            dot_counts.setdefault(name, []).append(int((arr > 0).sum()))
        print(f"[{time.time()-t0:6.0f}s] draw {j+1}/{len(draws)} done", flush=True)

    summary = evaluate_holdout.pooled_summary(terms, candidate="gx_s2.5_n50000")
    result = dict(evidence_class="HOLDOUT-DTI",
                  evaluator=summary["evaluator_version"], seeds=list(SEEDS),
                  n_draws=len(draws), alpha=summary["alpha"], beta=summary["beta"],
                  triangular_radius_m=summary["triangular_radius_m"],
                  features_used=[names[i] for i in keep], features_dropped=leaked,
                  model="logistic regression, refit per draw on the visible catalogue",
                  canaries=canaries, pooled=summary, per_fold_dti=per_fold,
                  dot_counts=dot_counts,
                  withheld_positive_pixels=summary["scores"]["gx_s2.5_n50000"]["withheld_positive_pixels"])
    OUT.write_text(json.dumps(result, indent=1))
    print(json.dumps(summary["scores"], indent=1))
    print(f"wrote {OUT} ({time.time()-t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
