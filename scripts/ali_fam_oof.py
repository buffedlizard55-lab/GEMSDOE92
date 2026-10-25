#!/usr/bin/env python3
"""ALI lane, step A: out-of-fold Fault-Appearance Model (FAM).

Gradient-boosted classifier of *what catalogued faults look like* in the 19-band
competition stack + 10 m DEM derivatives + chi/knickpoint + GeoDAWN radiometrics
+ 11 multi-scale context operators.  Positives = catalogue pixels (or VISIBLE
catalogue pixels for a hide-and-recover draw); negatives = pixels > 5 px from
that same label set.  Predictions are quadrant out-of-fold (LOQO), so no pixel is
scored by a model that saw its own quadrant.  No catalogue distance is a feature.

Outputs (gitignored, .cache/work/fam/): fam_<labelset>.npy (float32 over the
footprint index), plus a JSON receipt with per-fold AUC and leakage canaries.
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np
from scipy import ndimage
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from vendor.gems57.grid import load_grid  # noqa: E402
from vendor.gems57.holdout import quadrant_ids, buffered_component_draw  # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))
from ali_features import foot_index, safe_load, safe_save  # noqa: E402

W = ROOT / ".cache" / "work"
OUT = W / "fam"


def labels_for(labelset: str, grid):
    cat = np.asarray(grid.catalogue, bool)
    if labelset == "full":
        return cat, None
    seed = int(labelset.replace("seed", ""))
    folds, _ = buffered_component_draw(grid, seed=seed)
    return np.asarray(folds[0]["visible"], bool), folds


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labelset", default="full", help="full | seed20 | seed21")
    ap.add_argument("--neg", type=int, default=220_000)
    args = ap.parse_args()
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    grid = load_grid()
    idx = foot_index()
    meta = json.load(open(W / "feat" / "X_all.json"))
    X = safe_load(W / "feat" / "X_all.npy", meta["sha256"], mmap="r")
    names = meta["names"]
    if not np.array_equal(np.flatnonzero(np.asarray(grid.footprint).ravel()), idx):
        raise SystemExit("vendor grid footprint != sample_submission finite cells")
    lab, _ = labels_for(args.labelset, grid)
    d_lab = ndimage.distance_transform_edt(~lab).ravel()[idx]
    y_pos = lab.ravel()[idx]
    quad = quadrant_ids(grid.footprint).ravel()[idx]
    rng = np.random.default_rng(92_0 + len(args.labelset))
    f = np.zeros(idx.size, np.float32)
    receipt = dict(labelset=args.labelset, features=names, n_features=len(names), folds=[])
    for q in range(4):
        tr = quad != q
        pos = np.flatnonzero(tr & y_pos)
        negpool = np.flatnonzero(tr & (d_lab > 5))
        neg = rng.choice(negpool, size=min(args.neg, negpool.size), replace=False)
        ii = np.concatenate([pos, neg]); yy = np.concatenate([np.ones(pos.size), np.zeros(neg.size)])
        w = np.where(yy == 1, neg.size / max(pos.size, 1), 1.0)
        clf = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.08, max_leaf_nodes=31,
                                             min_samples_leaf=80, l2_regularization=1.0, random_state=q)
        clf.fit(np.asarray(X[ii]), yy, sample_weight=w)
        te = np.flatnonzero(quad == q)
        for a in range(0, te.size, 400_000):
            sl = te[a:a + 400_000]
            f[sl] = clf.predict_proba(np.asarray(X[sl]))[:, 1].astype(np.float32)
        # held-out AUC: label pixels vs d>5 pixels inside the held-out quadrant
        tp = np.flatnonzero((quad == q) & y_pos); tn = np.flatnonzero((quad == q) & (d_lab > 5))
        tn = rng.choice(tn, size=min(200_000, tn.size), replace=False)
        auc = float(roc_auc_score(np.r_[np.ones(tp.size), np.zeros(tn.size)], np.r_[f[tp], f[tn]]))
        receipt["folds"].append(dict(quadrant=int(q), n_pos=int(pos.size), n_neg=int(neg.size), heldout_auc=auc))
        print(f"[{args.labelset}] q{q} pos={pos.size} neg={neg.size} heldout AUC={auc:.4f} t={time.time()-t0:.0f}s", flush=True)
    receipt["sha256"] = safe_save(OUT / f"fam_{args.labelset}.npy", f)
    receipt["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(receipt, open(OUT / f"fam_{args.labelset}.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
