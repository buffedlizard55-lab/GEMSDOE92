#!/usr/bin/env python3
"""GX score estimator -- holdout-yield transfer onto the official metric algebra.

Why a new estimator
-------------------
``evidence/score_estimator_20261026.json`` regresses owner-reported CLAIMs on
four structural statistics; its own audit records
``valid_leaderboard_prediction: false`` and leave-group-out RMSE 0.078.  This
module instead uses the *metric algebra*, which is exact given three numbers
that the shared holdout instrument can measure:

    DTI = T / (alpha*(T + n - M) + beta*K)      alpha = 0.2, beta = 0.8

* ``T`` covered truth credit, ``M`` dot self-credit, ``n`` dot count,
  ``K`` truth mass.  (See ``vendor/gems57/metric.py``: the denominator does NOT
  collapse to ``alpha*n + beta*K`` unless ``T == M``.)
* ``K`` for the scored (public) split is *derived*, not fitted: the five
  H19-5-lineage claims form a subset chain (d2.8 -> h27-4 -> h33), and
  requiring the pruned dots to have non-negative yield bounds
  ``K`` to 12.8k-14.1k.  We take ``K = 13219`` (see docs/gx-executive-summary).
* Per-dot truth yield ``t = T/n`` and self-credit ``m = M/n`` are measured for
  any raster on the shared hide-and-recover holdout.  A single scalar
  ``s`` transfers holdout yield to the real (unmapped-fault) task:

      DTI_hat(raster) = (s*t*n) / (0.2*(s*t*n + n - m*n) + 0.8*K)

  ``s`` is fitted by least squares to owner-reported CLAIMs of the nine
  focus-site files, and validated leave-one-out over those nine files.

Evidence classes
----------------
CLAIM   owner-reported score, no organiser receipt (the fit target).
MODEL   every number this script emits (calibrated projection, not a score).
HOLDOUT-DTI  the measured per-dot yields that feed the projection.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa: E402

IDX = ROOT / ".cache" / "registry_index"
K_PUBLIC = 13219.0
ALPHA, BETA = 0.2, 0.8
SEEDS = (20, 30)

FOCUS: dict[str, tuple[str, float]] = {
    # site -> (exact published file name, owner-reported CLAIM)
    "GEMSDOE24": ("gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif", 0.2477),
    "GEMSDOE25": ("gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif", 0.2600),
    "GEMSDOE27": ("gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif", 0.2449),
    "GEMSDOE28": ("gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif", 0.2710),
    "GEMSDOE30": ("gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif", 0.2600),
    "GEMSDOE31": ("gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif", 0.2708),
    "GEMSDOE32": ("gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif", 0.2778),
    "GEMSDOE33": ("GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif", 0.2632),
    "GEMSDOE36": ("gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif", 0.2750),
}


def load_registry_index() -> list[dict]:
    meta = json.loads((IDX / "meta.json").read_text())
    return meta["meta"]


def find_raster(name: str) -> tuple[np.ndarray, dict] | tuple[None, None]:
    for row in load_registry_index():
        if Path(row["path"]).name == name:
            dots = np.load(IDX / f"dots_{row['sha256']}.npy")
            return dots, row
    return None, None


def draws_for(grid):
    out = []
    for seed in SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        out.extend(folds)
    return out


def measure(dots_flat: np.ndarray, shape, folds, foot) -> dict:
    """Pooled holdout terms for one dot set."""
    arr = np.zeros(shape, np.float32)
    arr.flat[dots_flat] = 1.0
    tp = fp = ne = 0.0
    nt = 0
    for f in folds:
        sc, _ = evaluate_holdout.evaluate(arr, f, foot)
        tp += sc["tp"]
        fp += sc["fp"]
        ne += sc["n_emitted"]
        nt = max(nt, int(sc["n_truth"]))
    n_tot = int(dots_flat.size)
    return dict(n_dots=n_tot, tp=float(tp), fp=float(fp), n_emitted=float(ne),
                n_truth_fold=nt, t_per_dot=float(tp / max(ne, 1)),
                m_per_dot=float((ne - fp) / max(ne, 1)))


def dti_hat(t: float, m: float, n: float, s: float, K: float = K_PUBLIC) -> float:
    T = s * t * n
    M = m * n
    return float(T / (ALPHA * (T + n - M) + BETA * K))


def fit_s(rows: list[dict], claims: np.ndarray) -> float:
    """Least-squares scalar yield-transfer on the given rows."""
    best, bs = 1e18, 1.0
    for s in np.linspace(0.05, 6.0, 1200):
        pred = np.array([dti_hat(r["t_per_dot"], r["m_per_dot"], r["n_dots"], s) for r in rows])
        err = float(np.mean((pred - claims) ** 2))
        if err < best:
            best, bs = err, float(s)
    return bs


def main() -> int:
    grid = grid_mod.load_grid()
    foot = grid.footprint
    shape = foot.shape
    folds = draws_for(grid)

    rows: dict[str, dict] = {}
    for site, (name, claim) in FOCUS.items():
        dots, meta = find_raster(name)
        if dots is None:
            print(f"  MISSING in registry index: {site} {name}", file=sys.stderr)
            continue
        m = measure(dots, shape, folds, foot)
        m["site"] = site
        m["file"] = name
        m["sha256"] = meta["sha256"]
        m["claim"] = claim
        m["repo"] = f'{meta["owner"]}/{meta["repo"]}'
        rows[site] = m
        print(f"{site:11s} n={m['n_dots']:6d} t/dot={m['t_per_dot']:.5f} "
              f"m/dot={m['m_per_dot']:.5f} claim={claim}")

    sites = sorted(rows)
    claims = np.array([rows[s]["claim"] for s in sites])
    s_full = fit_s([rows[x] for x in sites], claims)
    loo: dict[str, float] = {}
    for s_name in sites:
        train = [x for x in sites if x != s_name]
        s_i = fit_s([rows[x] for x in train], np.array([rows[x]["claim"] for x in train]))
        r = rows[s_name]
        loo[s_name] = dti_hat(r["t_per_dot"], r["m_per_dot"], r["n_dots"], s_i)
    pred_full = {s: dti_hat(rows[s]["t_per_dot"], rows[s]["m_per_dot"], rows[s]["n_dots"], s_full)
                 for s in sites}
    loo_pred = np.array([loo[s] for s in sites])
    rmse = float(np.sqrt(np.mean((loo_pred - claims) ** 2)))
    mae = float(np.mean(np.abs(loo_pred - claims)))
    from scipy.stats import spearmanr
    rho = float(spearmanr(loo_pred, claims).statistic) if len(sites) > 2 else float("nan")

    out = dict(evidence_class="MODEL", schema="gx-score-estimator.v2",
               estimator="holdout-yield transfer onto DTI = T/(a(T+n-M)+b*K)",
               K_public_split=K_PUBLIC, alpha=ALPHA, beta=BETA,
               evaluator=evaluate_holdout.VERSION, seeds=list(SEEDS),
               yield_transfer_s=round(s_full, 4),
               loo_rmse=round(rmse, 5), loo_mae=round(mae, 5), loo_spearman=round(rho, 4),
               caveats=[
                   "Targets are owner-reported CLAIMs, not organiser receipts.",
                   "All nine anchors are members of one lineage (H19-5 skeleton dotted and "
                   "pruned), so the LOO error measures interpolation inside that lineage, "
                   "NOT accuracy for a differently constructed raster.",
                   "K = 13219 is derived from the subset algebra of the lineage claims, not "
                   "measured; it is the public-split truth mass implied by those claims.",
                   "A MODEL number is never an organiser score.",
               ],
               files={s: {**rows[s], "dti_model_loo": round(loo[s], 4),
                          "dti_model_insample": round(pred_full[s], 4)} for s in sites})
    dest = ROOT / "evidence" / "gx_score_estimator.json"
    dest.write_text(json.dumps(out, indent=1))
    print(f"\ns_transfer={s_full:.4f}  LOO RMSE={rmse:.4f}  MAE={mae:.4f}  rho={rho:.3f}")
    for s in sites:
        print(f"  {s:11s} claim={rows[s]['claim']:.4f} loo={loo[s]:.4f} resid={loo[s]-rows[s]['claim']:+.4f}")
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
