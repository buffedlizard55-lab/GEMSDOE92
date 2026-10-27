#!/usr/bin/env python3
"""Spatial hide-and-recover holdout for EXP1 (shared gems57 instrument).

Instrument: vendor/gems57 ``buffered_component_draw`` (whole catalogue
components withheld inside label-blind eroded quadrants, 3 px feature buffer,
seeds 20 and 30) scored with ``evaluate_holdout.evaluate`` (pooled DTI,
alpha 0.2 / beta 0.8, 300 m triangular kernel; visible faults masked
pixel-exactly) and ``pooled_summary`` (paired 20 km block bootstrap).

Arms (strict Rule-2: every catalogue-derived input uses VISIBLE faults only):
* ``exp1_lbm``     -- ensemble LBM density (mean of the G>=0.18 and G>=0.15 fits)
                      with d_cat replaced by d_visible, same trust caps, d_visible > 2,
                      exact lazy-greedy placement.
* ``r0_recipe``    -- H19-5 skeleton dotted at 2.8 px with d_visible > 2 (the
                      R0 recipe re-derived per draw; comparable control).
* ``h19_dense_vis``-- the H19-5 skeleton itself with d_visible > 2.
Limitations: the H19-5 skeleton and the consensus layer were built by earlier
sessions from the full catalogue; that cannot be undone and affects all arms.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
import lbm_data as L  # noqa: E402
from gems import lbm_place as P  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa: E402

OUT = ROOT / "evidence" / "exp1_holdout.json"


def nms_dots(order_lin: np.ndarray, shape, min_dist: float, n: int) -> np.ndarray:
    H, W = shape
    taken = np.zeros(H * W, bool)
    block = np.zeros(H * W, bool)
    r = int(np.ceil(min_dist))
    offs = [dy * W + dx for dy in range(-r, r + 1) for dx in range(-r, r + 1)
            if 0 < dy * dy + dx * dx < min_dist * min_dist]
    offs = np.array(offs, np.int64)
    cnt = 0
    for c in order_lin:
        if block[c]:
            continue
        taken[c] = True; cnt += 1
        nb = c + offs
        nb = nb[(nb >= 0) & (nb < H * W)]
        block[nb] = True
        block[c] = True
        if cnt >= n:
            break
    return taken.reshape(H, W)


def cons_layers(thresholds=(0.18, 0.15)):
    """Consensus counts for each G-set threshold (same rule as lbm_fit_final / lbm_ensemble_map)."""
    import lbm_harness as Hh
    fp = L.footprint(); lin = fp.lin; H, W = L.SHAPE
    dh = L.edt_to(L.read01(L.H195) > 0).ravel()[lin]
    rows = Hh.scored_rows(); y = np.array([r["claim"] for r in rows]); sha = np.array([r["match"]["sha256"] for r in rows])
    onh = np.array([float((dh[np.load(Hh.CACHE / f"{s}.npz")["pos"]] < 0.5).mean()) for s in sha])
    out = {}
    for thr in thresholds:
        c = np.zeros((H, W), np.int16)
        for s in dict.fromkeys(sha[(y >= thr) & (onh < 0.30)]):
            z = np.load(Hh.CACHE / f"{s}.npz"); g = np.zeros(H * W, bool); g[lin[z["pos"]]] = True
            c += (ndi.distance_transform_edt(~g.reshape(H, W)) <= 2.0)
        out[thr] = c
    return out


def main() -> int:
    ens = json.loads((ROOT / "evidence" / "lbm_ensemble_model.json").read_text())
    betas = {0.18: np.array(ens["members"]["gset_0.18"]["beta"]), 0.15: np.array(ens["members"]["gset_0.15"]["beta"])}
    conses = cons_layers()
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    H, W = foot.shape
    h19 = L.read01(L.H195) > 0
    dh = ndi.distance_transform_edt(~h19)
    from gems import lbmodel as M
    X = M.factor_design((3, 6, 5))
    terms: dict[str, np.ndarray] = {}
    per_fold: dict[str, list] = {}
    receipts = []
    for seed in (20, 30):
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        vis = folds[0]["visible"]
        known = folds[0]["masked_known"]
        dvis = ndi.distance_transform_edt(~vis)
        f1 = np.digitize(dvis, [2.01, 15.01]); f2 = np.digitize(dh, [0.5, 1.01, 2.01, 3.01, 5.01])
        rho = np.zeros((H, W))
        for thr, b in betas.items():
            cls = ((f1 * 6 + f2) * 5 + np.digitize(conses[thr], [0.5, 1.5, 2.5, 4.5]))
            rho += 0.5 * np.minimum(np.exp(X @ b), 0.5)[cls]
        rho[~foot | known] = 0.0
        elig = foot & ~known & (dvis > 2.0)
        cand = P.candidates(rho, elig)
        member = np.stack([(conses[0.18].ravel()[cand] >= 5), (conses[0.15].ravel()[cand] >= 5)], axis=1)
        res = P.place(rho, elig, n_max=60000, cand=cand, member=member, caps=np.array([0.55, 0.78]))
        exp1 = np.zeros(H * W, np.float32); exp1[res["order"][:res["best_n"]]] = 1.0
        exp1 = exp1.reshape(H, W)
        # R0 recipe per draw: H19 skeleton (d_visible>2) dotted at 2.8 px in a fixed scan order
        elig_r0 = h19 & foot & (dvis > 2.0) & ~known
        scan = np.flatnonzero(elig_r0.ravel())
        r0r = nms_dots(scan, (H, W), 2.8, 10 ** 9).astype(np.float32)
        h19v = (elig_r0).astype(np.float32)
        arms = dict(exp1_lbm=exp1, r0_recipe=r0r, h19_dense_vis=h19v)
        for name, arr in arms.items():
            for fold in folds:
                sc, tm = evaluate_holdout.evaluate(arr, fold, foot)
                terms[name] = tm if name not in terms else terms[name] + tm
                per_fold.setdefault(name, []).append(round(float(sc["dti"]), 6))
        receipts.append(dict(seed=seed, exp1_dots=int(exp1.sum()), r0_recipe_dots=int(r0r.sum()),
                             h19_dense_px=int(h19v.sum()), folds=[f["receipt"] for f in folds]))
        print(f"seed {seed}: exp1 {int(exp1.sum())} dots, r0_recipe {int(r0r.sum())}", flush=True)
    summ = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate="exp1_lbm")
    out = dict(schema="gemsdoe92-exp1-holdout-v1", instrument="gems57 buffered_component_draw seeds 20,30; "
               "evaluate_holdout.evaluate; pooled_summary (paired 20 km block bootstrap)",
               rule="strict Rule-2: catalogue-derived inputs from visible faults only",
               summary=summ, per_fold=per_fold, receipts=receipts,
               limitations=["H19-5 skeleton and consensus layer were built from the full catalogue by earlier sessions",
                            "this instrument withholds catalogue faults, which differ from the organizer's new-fault labels"])
    OUT.write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    for k, v in summ["scores"].items():
        print(f"{k:>14}: HOLDOUT-DTI {v['dti']:.6f} CI95 [{v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}] withheld {v['withheld_positive_pixels']}")
    for k, v in summ["paired_differences"].items():
        print(f"exp1 - {k}: {v['delta']:+.6f} CI95 [{v['ci95'][0]:+.6f}, {v['ci95'][1]:+.6f}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
