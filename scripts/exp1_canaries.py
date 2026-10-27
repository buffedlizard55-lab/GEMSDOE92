#!/usr/bin/env python3
"""Leakage canaries for EXP1 (protocol rule 4): each feature alone vs withheld truth.

On the shared gems57 draws (seeds 20, 30; whole components withheld), every
EXP1 input is scored *alone* as a ranking of scored cells (fold region minus
visible faults); AUC > 0.90 for any single feature would indicate label leakage.
Catalogue distance uses VISIBLE faults only.  Output: evidence/exp1_canaries.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
import lbm_data as L  # noqa: E402
from gems import lbmodel as M  # noqa: E402
from gems57 import grid as grid_mod, holdout as hold_mod  # noqa: E402


def auc(score_pos: np.ndarray, score_neg: np.ndarray) -> float:
    s = np.concatenate([score_pos, score_neg])
    r = rankdata(s)
    n1, n0 = score_pos.size, score_neg.size
    return float((r[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def main() -> int:
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    foot = grid.footprint
    from exp1_holdout import cons_layers
    conses = cons_layers()
    cons = conses[0.18].astype(np.float64)
    dh = ndi.distance_transform_edt(~(L.read01(L.H195) > 0))
    ens = json.loads((ROOT / "evidence" / "lbm_ensemble_model.json").read_text())
    X = M.factor_design((3, 6, 5))
    rho_cs = {thr: np.minimum(np.exp(X @ np.array(ens["members"][f"gset_{thr}"]["beta"])), 0.5) for thr in (0.18, 0.15)}
    rng = np.random.default_rng(7)
    pooled = {k: ([], []) for k in ("neg_dcat_visible", "neg_dist_h19", "consensus_count", "lbm_rho")}
    per_fold = []
    for seed in (20, 30):
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        vis = folds[0]["visible"]; known = folds[0]["masked_known"]
        dvis = ndi.distance_transform_edt(~vis)
        base = (np.digitize(dvis, [2.01, 15.01]) * 6 + np.digitize(dh, [0.5, 1.01, 2.01, 3.01, 5.01])) * 5
        rho_ens = sum(0.5 * rho_cs[t][base + np.digitize(conses[t], [0.5, 1.5, 2.5, 4.5])] for t in (0.18, 0.15))
        feats = {"neg_dcat_visible": -dvis, "neg_dist_h19": -dh, "consensus_count": cons, "lbm_rho": rho_ens}
        for fold in folds:
            region = fold["region"] & foot & ~known
            truth = fold["truth"] & region
            neg = region & ~truth
            ni = np.flatnonzero(neg.ravel())
            if ni.size > 200000:
                ni = rng.choice(ni, 200000, replace=False)
            pi = np.flatnonzero(truth.ravel())
            row = dict(seed=seed, fold=fold["name"], positives=int(pi.size))
            for k, f in feats.items():
                fv = f.ravel()
                row[k] = auc(fv[pi], fv[ni])
                pooled[k][0].append(fv[pi]); pooled[k][1].append(fv[ni])
            per_fold.append(row)
    out = dict(schema="gemsdoe92-exp1-canaries-v1", threshold=0.90,
               pooled_auc={k: auc(np.concatenate(v[0]), np.concatenate(v[1])) for k, v in pooled.items()},
               per_fold=per_fold)
    out["max_auc"] = max(out["pooled_auc"].values())
    out["leakage_flag"] = bool(out["max_auc"] > 0.90 or any(r[k] > 0.90 for r in per_fold for k in pooled))
    (ROOT / "evidence" / "exp1_canaries.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["pooled_auc"], indent=1), "leakage_flag", out["leakage_flag"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
