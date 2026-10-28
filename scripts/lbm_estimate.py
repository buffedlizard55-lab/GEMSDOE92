#!/usr/bin/env python3
"""Estimate (MODEL) the public-leaderboard DTI of candidate rasters with the LBM.

For each candidate (a .npy of full-grid linear dot indices, or a GeoTIFF):
* point estimate under LBM-v1 (dcat3 x dh19 x cons, main effects),
* group bootstrap (resampling the 81 CV groups, refitting beta) -> 90%/95%
  intervals for the candidate, for R0 and for the paired difference,
* robustness under alternative specifications (dcat6; dh19 x cons interaction;
  G-set threshold 0.15).
Every number is labelled MODEL; none is an organizer score.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import lbm_data as L  # noqa: E402
import lbm_harness as Hh  # noqa: E402
from gems import lbmodel as M  # noqa: E402


def cand_stats(sel_full: np.ndarray, cls_fp: np.ndarray, K: int, scored_fp: np.ndarray, lin) -> tuple:
    C = M.coverage_field(sel_full.astype(np.float32)).ravel()[lin]
    ok = cls_fp >= 0
    A = np.bincount(cls_fp[ok], weights=C[ok].astype(np.float64), minlength=K)
    pv = sel_full.ravel()[lin].astype(np.float64)
    nz = (pv > 0) & ok
    m = np.bincount(cls_fp[nz], weights=pv[nz], minlength=K)
    n = float(pv[scored_fp].sum())
    return A, m, n


def load_sel(path: Path, shape) -> np.ndarray:
    if path.suffix == ".npy":
        sel = np.zeros(shape[0] * shape[1], bool); sel[np.load(path)] = True
        return sel.reshape(shape)
    return L.read01(path) > 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("candidates", nargs="+")
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--out", default=str(ROOT / "evidence" / "lbm_estimates.json"))
    args = ap.parse_args()
    fp = L.footprint(); cat = L.catalogue(); lin = fp.lin; H, W = L.SHAPE
    scored_full = fp.mask & ~cat
    scored = scored_full.ravel()[lin]
    dcat = L.edt_to(cat).ravel()[lin]
    dh = L.edt_to(L.read01(L.H195) > 0).ravel()[lin]
    rows = Hh.scored_rows()
    y = np.array([r["claim"] for r in rows])
    sha = np.array([r["match"]["sha256"] for r in rows])
    model = json.loads((ROOT / "evidence" / "lbm_v1_model.json").read_text())
    groups = np.array([r["group"] for r in model["rows"]])
    onh = np.array([float((dh[np.load(Hh.CACHE / f"{s}.npz")["pos"]] < 0.5).mean()) for s in sha])

    def cons_layer(thr):
        gset = (y >= thr) & (onh < 0.30)
        c = np.zeros(lin.size, np.int16)
        for s in dict.fromkeys(sha[gset]):
            z = np.load(Hh.CACHE / f"{s}.npz")
            g = np.zeros(H * W, bool); g[lin[z["pos"]]] = True
            c += (ndi.distance_transform_edt(~g.reshape(H, W)).ravel()[lin] <= 2.0)
        return c

    cons18 = cons_layer(0.18)
    cons15 = cons_layer(0.15)
    from gems import riesz_locked as RL
    from scipy.stats import rankdata
    X_fp, _ = RL.compute_or_load_features(lin, fp.mask)
    def _rzs(v):
        med = float(np.median(v))
        iqr = max(float(np.quantile(v, 0.75) - np.quantile(v, 0.25)), 1e-6)
        return np.clip((v - med) / iqr, -3.0, 5.0)
    h92_blind = (
        0.35 * (0.45 * _rzs(X_fp[:, 4]) + 0.30 * _rzs(X_fp[:, 5]) + 0.25 * _rzs(X_fp[:, 3]))
        + 0.20 * (0.55 * _rzs(X_fp[:, 9]) + 0.45 * _rzs(X_fp[:, 6]))
        + 0.25 * (0.60 * _rzs(X_fp[:, 12]) + 0.40 * _rzs(X_fp[:, 10]))
        + 0.20 * (0.65 * _rzs(X_fp[:, 15]) + 0.35 * _rzs(X_fp[:, 14]))
    ).astype(np.float32)
    del X_fp
    phys_q85 = np.digitize((rankdata(h92_blind, method="average") - 0.5) / lin.size, [0.85])
    f2 = np.digitize(dh, [0.5, 1.01, 2.01, 3.01, 5.01])
    f3a = np.digitize(cons18, [0.5, 1.5, 2.5, 4.5]); f3b = np.digitize(cons15, [0.5, 1.5, 2.5, 4.5])
    d3 = np.digitize(dcat, [2.01, 15.01]); d6 = np.digitize(dcat, [2.01, 3.01, 5.01, 8.01, 15.01])
    specs = {
        "lbm_v1": (((d3 * 6 + f2) * 5 + f3a), (3, 6, 5), ()),
        "lbm_v2_riesz": ((((d3 * 6 + f2) * 5 + f3a) * 2 + phys_q85), (3, 6, 5, 2), ()),
        "dcat6": (((d6 * 6 + f2) * 5 + f3a), (6, 6, 5), ()),
        "dh19xcons": (((d3 * 6 + f2) * 5 + f3a), (3, 6, 5), ((1, 2),)),
        "gset015": (((d3 * 6 + f2) * 5 + f3b), (3, 6, 5), ()),
    }
    maps = {}
    for k, (c, lev, _) in specs.items():
        c = c.astype(np.int32); c[~scored] = -1; maps[k] = c
    S = Hh.stats(maps, rows, scored)
    sels = {Path(c).stem: load_sel(Path(c), (H, W)) for c in args.candidates}
    sels["R0_reference"] = L.read01(L.R0) > 0
    out = dict(schema="gemsdoe92-lbm-estimates-v1", evidence_class="MODEL (not an organizer score)",
               candidates={})
    stats_c = {k: {nm: cand_stats(sel, maps[k], S[k]["K"], scored, lin) for nm, sel in sels.items()} for k in specs}
    fits = {}
    for k, (_, lev, inter) in specs.items():
        X = M.factor_design(lev, interactions=inter)
        fits[k] = (X, M.fit_loglinear(S[k]["A"], S[k]["m"], S[k]["n"], y, S[k]["Ncls"], X, lam=1e-3))
    for nm in sels:
        est = {}
        for k in specs:
            X, f = fits[k]
            A, m, n = stats_c[k][nm]
            est[k] = float(M.predict(f["rho"], A[None], m[None], np.array([n]), S[k]["Ncls"])[0])
        out["candidates"][nm] = dict(n_dots=int(sels[nm].sum()), estimates=est)
    # group bootstrap under lbm_v1
    rng = np.random.default_rng(20261027)
    ug = np.unique(groups)
    X, f0 = fits["lbm_v1"]
    boots = {nm: [] for nm in sels}
    for b in range(args.boot):
        pick = rng.choice(ug, size=ug.size, replace=True)
        idx = np.concatenate([np.flatnonzero(groups == g) for g in pick])
        fb = M.fit_loglinear(S["lbm_v1"]["A"][idx], S["lbm_v1"]["m"][idx], S["lbm_v1"]["n"][idx], y[idx],
                             S["lbm_v1"]["Ncls"], X, lam=1e-3, beta0=f0["beta"])
        for nm in sels:
            A, m, n = stats_c["lbm_v1"][nm]
            boots[nm].append(float(M.predict(fb["rho"], A[None], m[None], np.array([n]), S["lbm_v1"]["Ncls"])[0]))
    r0b = np.array(boots["R0_reference"])
    for nm in sels:
        bb = np.array(boots[nm])
        d = bb - r0b
        out["candidates"][nm]["bootstrap"] = dict(
            draws=int(bb.size), q025=float(np.quantile(bb, 0.025)), q05=float(np.quantile(bb, 0.05)),
            median=float(np.median(bb)), q95=float(np.quantile(bb, 0.95)), q975=float(np.quantile(bb, 0.975)),
            delta_vs_R0=dict(median=float(np.median(d)), q025=float(np.quantile(d, 0.025)),
                             q05=float(np.quantile(d, 0.05)), q975=float(np.quantile(d, 0.975)),
                             p_gt0=float(np.mean(d > 0))))
    out["validation"] = model["validation"]
    out["notes"] = ("Point estimates and bootstrap quantiles are MODEL outputs fitted to owner-reported CLAIMs. "
                    "Grouped LOGO RMSE (validation) is the honest per-raster error scale; extrapolation beyond the "
                    "class composition of scored rasters adds unquantified error.")
    Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    for nm, d in out["candidates"].items():
        print(nm, d["n_dots"], {k: round(v, 4) for k, v in d["estimates"].items()},
              {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d["bootstrap"].items() if k != "delta_vs_R0"},
              {k: round(v, 4) for k, v in d["bootstrap"]["delta_vs_R0"].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
