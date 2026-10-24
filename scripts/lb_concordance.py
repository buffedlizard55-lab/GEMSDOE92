#!/usr/bin/env python3
"""Leaderboard-concordance test of the lane-consensus premise (MODEL + CLAIM inputs).

Question: does agreement with *other* independent lanes predict a lane's own
organizer-claimed leaderboard credit per dot?  If not, a consensus supplement has
no empirical footing and must not be built.

Inputs (all labelled):
  * registry rasters  - REGISTRY-MEASUREMENT (cached public GEMSDOE blobs)
  * LB scores         - CLAIM (operator-reported, no organizer receipt in this repo)
  * credit-per-dot    - MODEL: inverted from the official DTI algebra
        DTI = T / (0.2 T + 0.2 FP + 0.8 |G|),  FP = N - M,  M ~ T/3,
        |G| = G_EST (inferred from the R0 / SOLO / D2.8 removal ladder; sensitivity reported)
Nothing here is a score and nothing is written as one.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import spearmanr, kendalltau

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import grid as grid_mod  # noqa: E402

CACHE = ROOT / ".cache" / "gemsdoe_public_registry"
G_EST = 12500.0
C_RANDOM_FACTOR = np.pi * 9.0 / 3.0   # integral of the 3 px triangular kernel over the plane (px^2)

# (key, registry path substring, repo, claimed LB score, independent_of_R0_lineage)
LANES = [
    ("R0",        "h33-2-b2-20261004T220000Z-e5eb6e7e", None,       0.2778, False),
    ("gems70_dual", "gems70-p5-dual-submod300-oof38k", "GEMSDOE70", 0.2478, True),
    ("gems49_gate", "gems49-gate_ortho_w0.25-40k-20261006T213721Z-zeros", "GEMSDOE49", 0.2376, True),
    ("gems76_tiltworm", "gems76-ptcf-tiltworm-submod39k", "GEMSDOE76", 0.2343, True),
    ("gems63_cvarlw", "gemsdoe63-cvarlw-thin-s3p17-54864-20261011T220606Z-c58f60c4-zeros", "GEMSDOE63", 0.2303, True),
    ("gems73_mcsc", "gems73-h73-mcsc-seamfree-blakely-37654dots-20261021T073716Z-b27ac445-zeros", "GEMSDOE73", 0.1917, True),
    ("gems82_punoisyor", "gemsdoe82-h82-submodular-punoisyor", "GEMSDOE82", 0.1886, True),
    ("gems10_h28", "gems10-h28-dotted-ridge", "GEMSDOE10", 0.1839, True),
    ("gems75_radon", "gems75-trlt-radon-loco-ridge-20261021-zeros", "GEMSDOE75", 0.1627, True),
    ("gems78_sigx", "gems78-h78sigx-fuse-b5-44090dots-20261022T021932Z-zeros", "GEMSDOE78", 0.1564, True),
    ("gems29_sgmc", "gemsdoe29-sgmc-off-catalogue-44k-20261003-c8dcd780e3fd-nan", "GEMSDOE29", 0.0500, True),
    ("gems72_sgmc", "gemsdoe72-h72-1-sgmc-offcatalogue-20261020T195456Z-6e6525e5-zeros", "GEMSDOE72", 0.0500, True),
]


def credit_per_dot(score: float, n: int, g: float = G_EST) -> float:
    t = (0.2 * n + 0.8 * g) / (1.0 / score - 0.2 + 0.2 / 3.0)
    return t / n


def find_file(sub: str, repo: str | None):
    inv = json.loads((CACHE / "registry_index.json").read_text())
    hits = [r for r in inv["rasters"] if sub in r["sources"][0] and (repo is None or r["repo_first"] == repo)]
    if sub.startswith("h33-2-b2"):
        return ROOT / "data" / "parent_R0_zeros.tif"
    if not hits:
        # tolerant fallback: match on the repo + leading token
        hits = [r for r in inv["rasters"] if (repo is None or r["repo_first"] == repo) and sub.split("-20")[0] in r["sources"][0]]
    return Path(hits[0]["cache_file"]) if hits else None


def main() -> int:
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    fp = grid.footprint
    nfp = int(fp.sum())
    rows, halos = [], {}
    for key, sub, repo, score, indep in LANES:
        p = find_file(sub, repo)
        if p is None:
            rows.append(dict(key=key, error="raster not found in cache", substring=sub))
            continue
        with rasterio.open(p) as ds:
            a = ds.read(1)
        dots = np.isfinite(a) & (a > 0) & fp
        n = int(dots.sum())
        d = ndi.distance_transform_edt(~dots)
        halo = (d <= 3.0) & fp
        halos[key] = (dots, halo)
        rows.append(dict(key=key, file=str(p.relative_to(ROOT)) if str(p).startswith(str(ROOT)) else str(p),
                         n=n, score_claim=score, independent=indep,
                         credit_per_dot=credit_per_dot(score, n),
                         coverage_frac=float(halo.sum() / nfp)))
    ok = [r for r in rows if "error" not in r]
    c_rand = (G_EST / nfp) * C_RANDOM_FACTOR
    for r in ok:
        r["enrichment_vs_random"] = r["credit_per_dot"] / c_rand
    # --- concordance: lane i's agreement with the other independent lanes (and R0 as one lane)
    voters = [r["key"] for r in ok]
    for r in ok:
        i = r["key"]
        dots_i = halos[i][0]
        lifts, votes = [], []
        for j in voters:
            if j == i:
                continue
            hj = halos[j][1]
            overlap = float(hj[dots_i].mean())
            lift = overlap / max(float(hj.sum() / nfp), 1e-9)
            lifts.append(lift)
            ej = next(x for x in ok if x["key"] == j)["enrichment_vs_random"]
            votes.append(overlap * np.log(max(ej, 1e-3)))
        r["mean_lift_vs_others"] = float(np.mean(lifts))
        r["lb_weighted_vote"] = float(np.sum(votes))
    ind = [r for r in ok if r["independent"]]
    out = dict(
        evidence_classes=dict(lanes="REGISTRY-MEASUREMENT", scores="CLAIM (operator-reported)", credit="MODEL"),
        g_est=G_EST, c_random=c_rand, n_lanes=len(ok), lanes=ok, errors=[r for r in rows if "error" in r],
        concordance={},
    )
    for metric in ("mean_lift_vs_others", "lb_weighted_vote"):
        x = [r[metric] for r in ind]
        y = [r["credit_per_dot"] for r in ind]
        rho, p = spearmanr(x, y)
        tau, pt = kendalltau(x, y)
        out["concordance"][metric] = dict(n=len(ind), spearman=float(rho), spearman_p=float(p),
                                          kendall=float(tau), kendall_p=float(pt))
    # sensitivity to the inferred |G|
    sens = {}
    for g in (11000.0, 12500.0, 14000.0):
        y = [credit_per_dot(r["score_claim"], r["n"], g) for r in ind]
        x = [r["mean_lift_vs_others"] for r in ind]
        sens[str(int(g))] = float(spearmanr(x, y)[0])
    out["concordance"]["sensitivity_to_G_spearman_mean_lift"] = sens
    outp = ROOT / "evidence" / "lb_concordance_20261024.json"
    outp.write_text(json.dumps(out, indent=2) + "\n")
    for r in ok:
        print(f"{r['key']:18s} n={r['n']:7d} claim={r['score_claim']:.4f} credit/dot={r['credit_per_dot']:.4f} "
              f"enr={r['enrichment_vs_random']:.2f} lift_others={r['mean_lift_vs_others']:.2f} vote={r['lb_weighted_vote']:.2f}")
    print(json.dumps(out["concordance"], indent=1))
    print("errors:", out["errors"])
    return 0


if __name__ == "__main__" and "--robust" not in sys.argv:
    raise SystemExit(main())


def robustness() -> dict:
    """Stress tests on the concordance premise (called with ``--robust``)."""
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    fp = grid.footprint
    nfp = int(fp.sum())
    lanes = {}
    for key, sub, repo, score, indep in LANES:
        p = find_file(sub, repo)
        with rasterio.open(p) as ds:
            a = ds.read(1)
        dots = np.isfinite(a) & (a > 0) & fp
        halo = (ndi.distance_transform_edt(~dots) <= 3.0) & fp
        lanes[key] = dict(dots=dots, halo=halo, n=int(dots.sum()), score=score, indep=indep)
    for k, v in lanes.items():
        v["credit"] = credit_per_dot(v["score"], v["n"])

    def conc(target_keys, voter_keys):
        x, y = [], []
        for i in target_keys:
            lifts = []
            for j in voter_keys:
                if j == i:
                    continue
                hj = lanes[j]["halo"]
                lifts.append(float(hj[lanes[i]["dots"]].mean()) / max(float(hj.sum() / nfp), 1e-9))
            x.append(np.mean(lifts))
            y.append(lanes[i]["credit"])
        rho, p = spearmanr(x, y)
        return dict(n=len(x), spearman=float(rho), p=float(p))

    ind = [k for k, v in lanes.items() if v["indep"]]
    no_sgmc = [k for k in ind if "sgmc" not in k]
    all_keys = list(lanes)
    non_r0 = [k for k in all_keys if k != "R0"]
    res = dict(
        baseline_all_voters=conc(ind, all_keys),
        voters_exclude_R0=conc(ind, non_r0),
        targets_exclude_sgmc=conc(no_sgmc, all_keys),
        targets_exclude_sgmc_voters_exclude_R0_and_sgmc=conc(no_sgmc, [k for k in non_r0 if "sgmc" not in k]),
    )
    # permutation null on the baseline statistic
    rng = np.random.default_rng(520810)
    x = [np.mean([float(lanes[j]["halo"][lanes[i]["dots"]].mean()) / max(float(lanes[j]["halo"].sum() / nfp), 1e-9)
                  for j in all_keys if j != i]) for i in ind]
    y = np.array([lanes[i]["credit"] for i in ind])
    obs = spearmanr(x, y)[0]
    null = [spearmanr(x, rng.permutation(y))[0] for _ in range(5000)]
    res["permutation_p_one_sided"] = float((np.sum(np.array(null) >= obs) + 1) / (len(null) + 1))
    return res


if __name__ == "__main__" and "--robust" in sys.argv:
    out = robustness()
    p = ROOT / "evidence" / "lb_concordance_robustness_20261024.json"
    p.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))
