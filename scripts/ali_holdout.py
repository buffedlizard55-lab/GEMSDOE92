#!/usr/bin/env python3
"""ALI lane, step E: shared hide-and-recover holdout (vendor gems57-pooled-hide-v2).

Seeds (20, 30) -> 8 LOQO folds, 22,663 withheld positives (same instrument as the
KNICKLOQO / COULOMBLOQO / LISTRIC run cards).  For each seed the FAM is the one
trained on that draw's VISIBLE catalogue only (scripts/ali_fam_oof.py --labelset
seedNN), quadrant out-of-fold, so a withheld component never reaches a label,
a feature or the exclusion buffer.  Arms are re-placed per seed against the
visible catalogue ("rule-2"); visible faults are masked pixel-exactly by the
shared evaluator.  Controls: H19-5 skeleton, R0 recipe (d28 minus d_visible<=2),
single-layer det_elev_slope NMS at matched geometry, matched random dots.
Leakage canaries: every FAM column alone, symmetric AUC on fold truth vs region.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "vendor")); sys.path.insert(0, str(ROOT / "scripts"))
from gems57 import evaluate_holdout, holdout  # noqa: E402
from gems57.grid import load_grid  # noqa: E402
from ali_features import safe_load  # noqa: E402
from ali_place import nms_dots  # noqa: E402

W = ROOT / ".cache" / "work"
SEEDS = (20, 30)


def fam_map(labelset, foot):
    meta = json.load(open(W / "fam" / f"fam_{labelset}.json"))
    v = safe_load(W / "fam" / f"fam_{labelset}.npy", meta["sha256"])
    out = np.zeros(foot.shape, np.float32); out.ravel()[np.flatnonzero(foot.ravel())] = v
    return out, meta


def symmetric_auc(score, y):
    from sklearn.metrics import roc_auc_score
    s = np.nan_to_num(score.astype(np.float64), nan=np.nanmedian(score))
    a = roc_auc_score(y, s)
    return float(max(a, 1 - a))


def main():
    t0 = time.time()
    arms_cfg = json.loads(sys.argv[1]) if len(sys.argv) > 1 else [
        dict(name="ALI_sep2.5_K37654", sep=2.5, k=37654, buf=3.0),
        dict(name="ALI_sep2.5_K26000", sep=2.5, k=26000, buf=3.0)]
    grid = load_grid()
    foot = np.asarray(grid.footprint, bool); cat = np.asarray(grid.catalogue, bool)
    with rasterio.open(ROOT / "data/bridge/d28.tif") as ds:
        d28 = (np.nan_to_num(ds.read(1)) > 0) & foot
    with rasterio.open(ROOT / "data/bridge/h19_5.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1)) > 0) & foot
    with rasterio.open(ROOT / ".cache/gems_inputs/training_features.tif") as ds:
        slope = ds.read(19).astype(np.float32)
    slope[~np.isfinite(slope) | (slope < -1e30)] = 0
    folds_all, terms = [], {}
    feat = json.load(open(W / "feat" / "X_all.json"))
    X = safe_load(W / "feat" / "X_all.npy", feat["sha256"], mmap="r")
    idx = np.flatnonzero(foot.ravel())
    canaries = {}
    rng = np.random.default_rng(520810)
    for seed in SEEDS:
        folds, _q = holdout.buffered_component_draw(grid, seed=seed)
        folds_all.extend(folds)
        fam, fmeta = fam_map(f"seed{seed}", foot)
        vis = np.asarray(folds[0]["visible"], bool)
        d_vis = distance_transform_edt(~vis)
        preds = {}
        for a in arms_cfg:
            cand = foot & ~cat & (d_vis > a["buf"])  # pixel-exact catalogue pixels are masked anyway
            preds[a["name"]] = nms_dots(fam, foot & (d_vis > a["buf"]), a["sep"], a["k"])
        preds["CTRL_R0recipe_d28_minus_dvis2"] = d28 & (d_vis > 2.0)
        preds["CTRL_H19-5_skeleton"] = h19
        preds["CTRL_slope_NMS_sep2.5_K37654"] = nms_dots(slope, foot & (d_vis > 3.0), 2.5, 37654)
        pool = np.flatnonzero((foot & (d_vis > 3.0)).ravel())
        rnd = np.zeros(foot.shape, bool); rnd.ravel()[rng.choice(pool, 37654, replace=False)] = True
        preds["CTRL_random_K37654"] = rnd
        # leakage canaries: each FAM input column alone + the FAM itself, fold truth vs region pixels
        if seed == SEEDS[0]:
            ys, ii = [], []
            for f in folds:
                pos = np.flatnonzero(f["truth"].ravel() & foot.ravel())
                negpool = np.flatnonzero((f["region"] & foot & ~cat).ravel())
                neg = rng.choice(negpool, size=min(negpool.size, 2 * pos.size), replace=False)
                ii.extend((pos, neg)); ys.extend((np.ones(pos.size), np.zeros(neg.size)))
            flat = np.concatenate(ii); y = np.concatenate(ys)
            pos_in_fp = np.searchsorted(idx, flat)
            for j, nm in enumerate(feat["names"]):
                canaries[nm] = symmetric_auc(np.asarray(X[pos_in_fp, j]), y)
            canaries["FAM_seed_model"] = symmetric_auc(fam.ravel()[flat], y)
            worst = max(canaries.items(), key=lambda kv: kv[1])
            print("canary worst", worst, flush=True)
            if worst[1] > 0.90:
                raise SystemExit(f"LEAKAGE CANARY FAIL {worst}")
        for f in folds:
            for nm, p in preds.items():
                _s, t = evaluate_holdout.evaluate(p.astype(np.float32), f, foot)
                terms[nm] = t if nm not in terms else terms[nm] + t
        print(f"seed {seed} done t={time.time()-t0:.0f}s", flush=True)
    out = dict(evaluator_version=evaluate_holdout.VERSION, seeds=list(SEEDS),
               withheld_positive_pixels=int(sum(int(f["truth"].sum()) for f in folds_all)),
               n_folds=len(folds_all), canaries=canaries, arms=[a["name"] for a in arms_cfg], summaries={})
    for a in arms_cfg:
        s = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate=a["name"])
        out["summaries"][a["name"]] = s
        sc = s["scores"]
        print(f"== candidate {a['name']}")
        for nm in terms:
            print(f"   {nm:36s} HOLDOUT-DTI {sc[nm]['dti']:.6f} CI {np.round(sc[nm]['ci95'], 6).tolist()}"
                  + (f"  paired d vs cand {s['paired'][nm]['delta']:+.6f} CI {np.round(s['paired'][nm]['ci95'],6).tolist()}" if 'paired' in s and nm in s['paired'] else ""))
    json.dump(out, open(W / "ali_holdout.json", "w"), indent=1, default=float)
    print(f"done {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
