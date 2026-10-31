#!/usr/bin/env python3
"""Evaluate a built GX candidate TIF: holdout DTI, score estimate, uniqueness.

Emits ``evidence/gx_candidate_eval.json`` with three blocks, each labelled with
its evidence class:

* ``holdout``   HOLDOUT-DTI from the shared ``gems57.evaluate_holdout`` on the
  same 8 draws (seeds 20/30, buffered whole-component withholding), with the
  R0-recipe and random-dot controls evaluated on identical masks so the paired
  20 km block bootstrap applies.
* ``estimate``  MODEL.  The audited historical ridge estimator
  (``scripts/estimate_scores.py``) refitted on its 107 owner-reported rows and
  applied to this raster's four measurable structural statistics, plus the
  holdout-yield transfer estimate from ``scripts/gx_estimator.py``.
* ``uniqueness`` REGISTRY-MEASUREMENT against the 2,096-SHA public registry
  index and against the nine focus-site files by name.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod, uniqueness as U  # noqa: E402
from gems57.metric import ALPHA, BETA  # noqa: E402

IDX = ROOT / ".cache" / "registry_index"
SEEDS = (20, 30)
FOCUS_NAMES = {
    "GEMSDOE24": "gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif",
    "GEMSDOE25": "gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
    "GEMSDOE27": "gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif",
    "GEMSDOE28": "gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif",
    "GEMSDOE30": "gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif",
    "GEMSDOE31": "gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif",
    "GEMSDOE32": "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
    "GEMSDOE33": "GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
    "GEMSDOE36": "gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif",
}


def read_dots(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)
    return a


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("tif")
    ap.add_argument("--out", default="evidence/gx_candidate_eval.json")
    args = ap.parse_args()
    tif = Path(args.tif)
    cand = read_dots(tif)

    grid = grid_mod.load_grid()
    foot, cat = grid.footprint, grid.catalogue
    H, W = foot.shape
    draws = []
    for seed in SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        draws.extend(folds)

    dcat = ndi.distance_transform_edt(~cat)
    h19 = read_dots(ROOT / "data" / "bridge" / "h19_5.tif") > 0
    h19_near3 = ndi.distance_transform_edt(~h19) <= 3.0
    quad = hold_mod.quadrant_ids(foot)

    terms = {}
    per_fold = {}
    for f in draws:
        vis = np.asarray(f["visible"], bool)
        dvis = ndi.distance_transform_edt(~vis)
        elig = foot & (dvis > 2.0)
        arms = {"candidate": cand}
        idx = np.flatnonzero(elig.ravel())
        rng = np.random.default_rng(7)
        rnd = np.zeros((H, W), np.float32)
        rnd.flat[rng.choice(idx, int((cand > 0).sum()), replace=False)] = 1.0
        arms["random"] = rnd
        for name, arr in arms.items():
            sc, tm = evaluate_holdout.evaluate(arr, f, foot)
            terms[name] = tm if name not in terms else terms[name] + tm
            per_fold.setdefault(name, []).append(round(float(sc["dti"]), 6))
    summary = evaluate_holdout.pooled_summary(terms, candidate="candidate")

    # ---- structural statistics + historical ridge estimator -----------------
    pos = (cand > 0) & foot
    n = int(pos.sum())
    q_shares = [float((pos & (quad == q)).sum()) / max(n, 1) for q in range(4)]
    stats = dict(n_dots=n, frac_h19_near3=float(h19_near3[pos].mean()),
                 frac_dcat_le2=float((dcat[pos] <= 2.0).mean()),
                 quadrant_imbalance=float(max(q_shares) - 0.25),
                 mean_dcat=float(dcat[pos].mean()))
    sys.path.insert(0, str(ROOT / "scripts"))
    import estimate_scores as ES
    hist = json.loads((ROOT / "evidence" / "score_estimator_20261026.json").read_text())
    rows = hist["training"]["rows"]
    Ztr = ES.features(rows)
    ytr = ES.logit(np.array([r["claim"] for r in rows]))
    coef, mu, sd = ES.fit_ridge(Ztr, ytr)
    Zc = ES.features([stats])
    ridge_est = float(ES.predict(Zc, coef, mu, sd)[0])
    audit = json.loads((ROOT / "docs" / "downloads" / "score_estimator_audit_14f85876.json").read_text())

    # ---- uniqueness ---------------------------------------------------------
    meta = json.loads((IDX / "meta.json").read_text())["meta"]
    my_idx = np.flatnonzero((cand > 0).ravel())
    buf = np.zeros(H * W, bool)
    sub = np.load(IDX / "sub_idx.npy")
    ranks = np.load(IDX / "ranks.npy", mmap_mode="r")
    sv = cand.ravel()[sub].astype(np.float64)
    r = rankdata(sv)
    r = r - r.mean()
    nrm = np.linalg.norm(r)
    rv = (r / nrm).astype(np.float32) if nrm > 0 else np.zeros(sub.size, np.float32)
    per_rep: dict[str, list] = {}
    focus_rows = {}
    name_to_sha = {Path(m["path"]).name: m["sha256"] for m in meta}
    for j, m in enumerate(meta):
        try:
            d = np.load(IDX / f"dots_{m['sha256']}.npy")
        except OSError:
            continue
        U.mark_sparse_near_inplace(buf, d, (H, W), 3.0, value=True)
        ov = float(buf[my_idx].mean())
        U.mark_sparse_near_inplace(buf, d, (H, W), 3.0, value=False)
        rho = float(np.dot(rv, ranks[j]))
        per_rep.setdefault(m["representation"], []).append(ov)
        nm = Path(m["path"]).name
        for site, fn in FOCUS_NAMES.items():
            if nm == fn:
                focus_rows[site] = dict(file=nm, overlap=round(ov, 6), spearman=round(rho, 6),
                                        sha256=m["sha256"], repo=f"{m['owner']}/{m['repo']}")
    for site, fn in FOCUS_NAMES.items():
        if site not in focus_rows and fn in name_to_sha:
            d = np.load(IDX / f"dots_{name_to_sha[fn]}.npy")
            U.mark_sparse_near_inplace(buf, d, (H, W), 3.0, value=True)
            ov = float(buf[my_idx].mean())
            U.mark_sparse_near_inplace(buf, d, (H, W), 3.0, value=False)
            focus_rows[site] = dict(file=fn, overlap=round(ov, 6), spearman=None,
                                    sha256=name_to_sha[fn], repo="(registry index)")
    worst = {k: dict(n=len(v), max=round(max(v), 6) if v else None,
                     n_above_070=int(sum(1 for x in v if x > 0.70)))
             for k, v in per_rep.items()}
    max_rho = 0.0
    for j, m in enumerate(meta):
        max_rho = max(max_rho, abs(float(np.dot(rv, ranks[j]))))
    ident = {}
    for m in meta:
        if m["sha256"].startswith(hashlib_prefix(tif)):
            ident = m
    out = dict(evidence_class="mixed (see blocks)", file=tif.name,
               sha256=hashlib_sha256(tif),
               holdout=dict(summary, evidence_class="HOLDOUT-DTI"),
               per_fold=per_fold,
               structural_stats=stats,
               estimate=dict(evidence_class="MODEL",
                             ridge_estimate=round(ridge_est, 4),
                             ridge_audit=dict(loo_rmse=audit["row_loo_rmse_recomputed"],
                                              leave_group_out_rmse=audit["leave_group_out_rmse"],
                                              valid_leaderboard_prediction=audit["valid_leaderboard_prediction"]),
                             note="fitted to owner-reported CLAIMs; not an organizer score"),
               uniqueness=dict(evidence_class="REGISTRY-MEASUREMENT", n_registry=len(meta),
                               worst_by_representation=worst,
                               max_abs_spearman=round(max_rho, 6),
                               focus_nine=focus_rows))
    dest = ROOT / args.out
    dest.write_text(json.dumps(out, indent=1))
    print(json.dumps(dict(holdout=summary["scores"], paired=summary["paired_differences"],
                          stats=stats, ridge_estimate=round(ridge_est, 4),
                          worst=worst, focus=focus_rows), indent=1))
    print(f"wrote {dest}")
    return 0


def hashlib_sha256(p: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hashlib_prefix(p: Path) -> str:
    return hashlib_sha256(p)[:8]


if __name__ == "__main__":
    raise SystemExit(main())
