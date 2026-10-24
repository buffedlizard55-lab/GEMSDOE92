#!/usr/bin/env python3
"""LCS: shared hide-and-recover HOLDOUT-DTI, leakage canary and SGMC control (report only).

Same instrument as scripts/report_proxies.py (``gems57-pooled-hide-v2``, seeds 20 & 30,
paired 20 km spatial-block bootstrap, pooled DTI alpha 0.2 / beta 0.8, 300 m triangular
kernel; visible faults masked pixel-exactly).  Arms: parent R0, the LCS candidate, the
UNCAPPED consensus selection (research arm), and a spaced random control with the same
budget.  NOT fold-pure for the lane voters: those lanes were built with the full
catalogue, so this is a diagnostic and never a promotion proof or a score.

Leakage canary: the lane-vote sum alone (defined everywhere) separating hidden catalogue
segments from same-fold non-catalogue background; symmetric AUC > 0.90 => stop.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]
from gems import lcs  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric  # noqa: E402

CACHE = ROOT / ".cache" / "lcs"


def _lbc():
    spec = importlib.util.spec_from_file_location("lbc", ROOT / "scripts" / "lb_concordance.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def random_spaced_control(grid, n, seed=520810):
    rng = np.random.default_rng(seed)
    d_cat = ndi.distance_transform_edt(~grid.catalogue)
    cand = np.argwhere(grid.footprint & (d_cat > lcs.MIN_CATALOGUE_DISTANCE_PX))
    order = rng.permutation(len(cand))
    sel = lcs.spaced_capped_greedy(order, cand, grid.footprint.shape, n)
    m = np.zeros(grid.footprint.shape, bool)
    m[cand[sel.index, 0], cand[sel.index, 1]] = True
    return m


def main() -> int:
    build = json.loads((ROOT / "evidence" / "lcs_build.json").read_text())
    cand_file = ROOT / "releases" / build["candidate"]["file"]
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    fp = grid.footprint
    arms = {}
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        arms["R0"] = (ds.read(1) > 0) & fp
    with rasterio.open(cand_file) as ds:
        arms["LCS"] = (ds.read(1) > 0) & fp
    # uncapped research arm: rebuild from cache (deterministic)
    P = np.load(CACHE / "pool.npz")
    order = np.argsort(-P["score"].astype(np.float64), kind="stable")
    unc = lcs.spaced_capped_greedy(order, P["yx"], fp.shape, lcs.N_TARGET).index
    m = np.zeros(fp.shape, bool)
    m[P["yx"][unc, 0], P["yx"][unc, 1]] = True
    arms["LCS_uncapped_research"] = m
    arms["RANDOM_spaced"] = random_spaced_control(grid, int(arms["LCS"].sum()))
    # the repository's recorded holdout best (RELIEF p10): the bar the protocol says a slot-worthy idea must beat
    relief = ROOT / "docs" / "downloads" / "h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24-zeros.tif"
    with rasterio.open(relief) as ds:
        arms["RELIEF_p10_holdout_best"] = (ds.read(1) > 0) & fp
    for k, v in arms.items():
        assert not (v & grid.catalogue).any(), k

    folds, split_receipts = [], []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})

    terms_by_arm, per_fold = {}, {}
    for name, mask in arms.items():
        total, per_fold[name] = None, []
        for fold in folds:
            sc, t = evaluate_holdout.evaluate(mask.astype(np.float32), fold, fp)
            per_fold[name].append(float(sc["dti"]))
            total = t if total is None else total + t
        terms_by_arm[name] = total
    pooled = evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate="LCS")

    # ---- leakage canary on the consensus vote sum (defined for every pixel) ----------------
    lbc = _lbc()
    nfp = int(fp.sum())
    c_rand = lcs.random_dot_credit(nfp)
    votes = np.zeros(fp.shape, np.float32)
    for key, sub, repo, score, _ in lbc.LANES:
        if "sgmc" in key:
            continue
        p = lbc.find_file(sub, repo)
        with rasterio.open(p) as ds:
            a = ds.read(1)
        dots = np.isfinite(a) & (a > 0) & fp
        w = np.log(max(lcs.credit_per_dot(score, int(dots.sum())) / c_rand, 1.0001))
        votes += np.float32(w) * ((ndi.distance_transform_edt(~dots) <= lcs.RADIUS_PX) & fp)
    rng = np.random.default_rng(520810)
    y_parts, idx_parts = [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & fp)
        neg = np.flatnonzero(fold["region"] & fp & ~grid.catalogue)
        n = min(len(neg), max(1, 2 * len(pos)))
        neg = rng.choice(neg, size=n, replace=False) if len(neg) > n else neg
        idx_parts.extend((pos, neg))
        y_parts.extend((np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)))
    y = np.concatenate(y_parts)
    flat = np.concatenate(idx_parts)
    auc = float(roc_auc_score(y, votes.ravel()[flat]))
    canary = dict(feature="lane-vote sum (LB-weighted halo votes of the 10 voters)", auc=round(auc, 6),
                  symmetric_auc=round(max(auc, 1 - auc), 6),
                  status="INVESTIGATE" if max(auc, 1 - auc) > 0.90 else "PASS (<=0.90)",
                  caveat="voters were built with the full catalogue; an AUC near 0.5-0.7 is therefore the expected, non-leaking regime")

    # ---- SGMC control -----------------------------------------------------------------------
    from build_prune_rungs import verify_inputs  # pinned-hash resolution shared with the other lanes
    sgmc_path = verify_inputs()["sgmc_faults_control"]
    with rasterio.open(sgmc_path) as ds:
        sgmc = (ds.read(1) > 0) & fp
    sgmc_truth = sgmc & ~grid.catalogue & ~ndi.binary_dilation(grid.catalogue, iterations=3)
    sgmc_scores = {n: round(metric.dti_binary(mk, sgmc_truth, valid=fp, known=grid.catalogue)["dti"], 6) for n, mk in arms.items()}

    report = dict(
        evidence_label="PROXY", created_utc="2026-10-24", candidate=cand_file.name,
        purpose="Report-only hide-and-recover instrument, single-feature leakage canary and SGMC control for the LCS lane.",
        evaluator=evaluate_holdout.VERSION,
        holdout=dict(seeds=[20, 30], withheld_positive_pixels=sum(int(f["truth"].sum()) for f in folds),
                     scores=pooled, per_fold_dti=per_fold, split_receipts=split_receipts,
                     ci_method="paired 20 km spatial-block bootstrap, 1000 draws, seed 520810",
                     not_fold_pure=("voter lanes were built from the full catalogue; arm R0 inherits a d_cat > 2 px and arm LCS a d_cat > 3 px exclusion "
                                    "around ALL mapped faults including withheld ones")),
        leakage_canary=canary,
        sgmc_control=dict(truth_pixels=int(sgmc_truth.sum()), dti_by_arm=sgmc_scores,
                          delta_vs_r0={k: round(v - sgmc_scores["R0"], 6) for k, v in sgmc_scores.items()},
                          note="SGMC bedrock faults are not the leaderboard truth (SGMC-lane rasters score ~0.05 live); control only"),
        warning="PROXY diagnostics: not a leaderboard score, not a promotion proof, not a win probability.",
    )
    out = ROOT / "evidence" / "lcs_proxy_audit.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    s = pooled["scores"]
    print(json.dumps(dict(
        evaluator=evaluate_holdout.VERSION, withheld=report["holdout"]["withheld_positive_pixels"],
        dti={n: round(s[n]["dti"], 6) for n in arms}, ci95={n: [round(x, 6) for x in s[n]["ci95"]] for n in arms},
        paired_vs_LCS={n: {"delta": round(d["delta"], 6), "ci95": [round(x, 6) for x in d["ci95"]]}
                       for n, d in pooled["paired_differences"].items()},
        canary=canary, sgmc=sgmc_scores), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
