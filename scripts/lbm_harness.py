#!/usr/bin/env python3
"""LBM experiment harness: class maps -> sufficient statistics -> fit -> grouped CV."""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import lbm_data as L  # noqa: E402
from gems import lbmodel as M  # noqa: E402
CACHE = ROOT / ".cache" / "lbm"


def scored_rows():
    rows = [r for r in L.load_claims_matched() if "match" in r]
    return rows


_SPARSE_CACHE: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}


def _load_sparse_npz(sha: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    got = _SPARSE_CACHE.get(sha)
    if got is None:
        z = np.load(CACHE / f"{sha}.npz")
        C = z["C"]
        nz = np.flatnonzero(C > 0).astype(np.int32)
        cw = C[nz].astype(np.float32)
        pos = z["pos"].astype(np.int32)
        val = z["val"].astype(np.float64)
        got = (nz, cw, pos, val)
        _SPARSE_CACHE[sha] = got
    return got


def stats(class_maps: dict[str, np.ndarray], rows, scored_fp: np.ndarray):
    """For each class map (footprint vector int32, -1 = unscored) compute A, m, n."""
    out = {k: dict(A=[], m=[], n=[], K=int(v.max()) + 1) for k, v in class_maps.items()}
    cache = {}
    for r in rows:
        sha = r["match"]["sha256"]
        if sha not in cache:
            nz, cw, pos, val = _load_sparse_npz(sha)
            n = float(val[scored_fp[pos]].sum())
            res = {}
            for k, cm in class_maps.items():
                K = out[k]["K"]
                cnz = cm[nz]
                ok = cnz >= 0
                A = np.bincount(cnz[ok], weights=cw[ok], minlength=K)
                cp = cm[pos]; okp = cp >= 0
                m = np.bincount(cp[okp], weights=val[okp], minlength=K)
                res[k] = (A, m, n)
            cache[sha] = res
        for k in class_maps:
            A, m, n = cache[sha][k]
            out[k]["A"].append(A); out[k]["m"].append(m); out[k]["n"].append(n)
    for k, cm in class_maps.items():
        o = out[k]
        o["A"] = np.array(o["A"]); o["m"] = np.array(o["m"]); o["n"] = np.array(o["n"])
        o["Ncls"] = np.bincount(cm[cm >= 0], minlength=o["K"]).astype(float)
    return out


def grid_pairs(shape):
    """Smoothing pairs for a dense multi-axis class grid (C-order)."""
    idx = np.arange(int(np.prod(shape))).reshape(shape)
    pairs = []
    for ax in range(len(shape)):
        a = np.moveaxis(idx, ax, 0)
        pairs += list(zip(a[:-1].ravel(), a[1:].ravel()))
    return pairs


def logo_cv(S, y, groups, pairs, lam_smooth=1e-4, lam_ridge=1e-6):
    y = np.asarray(y); groups = np.asarray(groups)
    pred = np.zeros(len(y))
    for g in np.unique(groups):
        te = groups == g; tr = ~te
        f = M.fit(S["A"][tr], S["m"][tr], S["n"][tr], y[tr], S["Ncls"], smooth_pairs=pairs,
                  lam_smooth=lam_smooth, lam_ridge=lam_ridge)
        pred[te] = M.predict(f["rho"], S["A"][te], S["m"][te], S["n"][te], S["Ncls"])
    return pred
