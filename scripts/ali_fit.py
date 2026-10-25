#!/usr/bin/env python3
"""ALI lane, step C: fit the latent new-fault intensity lam_b to owner-reported scores.

E[DTI_s](lam) = T/(T + 0.2 (S - M) + 0.8 (G - T)),  T = A_s.lam, G = N.lam, M = (B_s.lam)/3.
log lam_b = mu + alpha[D] + beta[F] + gamma[H] (+ optional D x H interaction).
Least squares on the score claims with a small ridge; leave-one-out (raster and
family) cross-validation is the honesty check.  All inputs are CLAIMS
(owner-reported, no organizer receipts in the repo).  Outputs are MODEL quantities.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / ".cache" / "work"


def load():
    d = json.load(open(W / "ali_design.json"))
    rows = d["rows"]
    # collapse rows with identical scored coverage (same A to 1e-6) -> one point, mean claim
    groups = {}
    for r in rows:
        key = (round(r["S"], 3), tuple(np.round(r["A"], 3)))
        groups.setdefault(key, []).append(r)
    pts = []
    for g in groups.values():
        r = g[0]
        pts.append(dict(name=r["name"], names=[x["name"] for x in g], lb=float(np.mean([x["lb_claim"] for x in g])),
                        S=r["S"], A=np.array(r["A"]), B=np.array(r["B"]), n=r["n_dots"]))
    return d, pts


def design_index(meta, nb):
    nD = len(meta["d_edges"]) - 1; nF = len(meta["f_quantiles"]) - 1
    b = np.arange(nb)
    H = b % 2; F = (b // 2) % nF; D = (b // 2) // nF
    return D, F, H, nD, nF


def make_model(meta, nb, spec):
    D, F, H, nD, nF = design_index(meta, nb)
    cols = [np.ones(nb)]
    names = ["mu"]
    if "D" in spec:
        for j in range(1, nD): cols.append((D == j).astype(float)); names.append(f"D{j}")
    if "Dfar" in spec:   # parsimonious catalogue-distance effect: d_cat > 3 px vs <= 3 px
        cols.append((D >= 1).astype(float)); names.append("Dfar")
    if "F" in spec:
        for j in range(1, nF): cols.append((F == j).astype(float)); names.append(f"F{j}")
    if "H" in spec:
        cols.append(H.astype(float)); names.append("H")
    if "DH" in spec:
        for j in range(1, nD): cols.append(((D == j) & (H == 1)).astype(float)); names.append(f"D{j}H")
    if "FH" in spec:
        for j in range(1, nF): cols.append(((F == j) & (H == 1)).astype(float)); names.append(f"F{j}H")
    return np.stack(cols, 1), names


def predict(theta, Z, pts, N):
    lam = np.exp(Z @ theta)
    G = N @ lam
    out = []
    for p in pts:
        T = p["A"] @ lam
        M = min((p["B"] @ lam) / 3.0, p["S"])
        out.append(T / (T + 0.2 * (p["S"] - M) + 0.8 * (G - T) + 1e-12))
    return np.array(out), lam


def fit(Z, pts, N, ridge=0.05, theta0=None):
    y = np.array([p["lb"] for p in pts])
    k = Z.shape[1]
    if theta0 is None:
        theta0 = np.zeros(k); theta0[0] = np.log(0.003)
    def res(th):
        pr, _ = predict(th, Z, pts, N)
        return np.r_[pr - y, np.sqrt(ridge) * 0.01 * th[1:]]
    sol = least_squares(res, theta0, method="trf", max_nfev=4000)
    return sol.x


def main():
    d, pts = load()
    meta, nb, N = d["meta"], d["n_strata"], np.array(d["N"])
    y = np.array([p["lb"] for p in pts])
    print("distinct scored points:", len(pts))
    fam = np.array([1 if any(k in p["name"] for k in ["h19-5", "d2-8", "d28", "h27-4", "h33-", "d1-5", "rung30", "h38-1", "h32-1", "anderson", "wormrank", "topo-gap", "h59-cover", "h33d"]) else 0 for p in pts])
    results = {}
    for spec in (["D"], ["D", "H"], ["D", "F"], ["D", "F", "H"], ["D", "F", "H", "DH"], ["D", "F", "H", "FH"],
                 ["Dfar", "F"], ["Dfar", "H"], ["Dfar", "F", "H"]):
        Z, names = make_model(meta, nb, spec)
        th = fit(Z, pts, N)
        pr, lam = predict(th, Z, pts, N)
        # leave-one-out
        loo = np.zeros(len(pts))
        for i in range(len(pts)):
            sub = [p for j, p in enumerate(pts) if j != i]
            thi = fit(Z, sub, N, theta0=th)
            loo[i] = predict(thi, Z, [pts[i]], N)[0][0]
        # leave-family-out for the H19 lineage
        sub = [p for j, p in enumerate(pts) if fam[j] == 0]
        thf = fit(Z, sub, N, theta0=th)
        prf = predict(thf, Z, pts, N)[0]
        rmse = float(np.sqrt(np.mean((pr - y) ** 2))); loo_rmse = float(np.sqrt(np.mean((loo - y) ** 2)))
        rho = float(spearmanr(loo, y)[0])
        fam_err = float(np.sqrt(np.mean((prf[fam == 1] - y[fam == 1]) ** 2)))
        key = "+".join(spec)
        results[key] = dict(names=names, theta=th.tolist(), fit_rmse=rmse, loo_rmse=loo_rmse, loo_spearman=rho,
                            lineage_out_rmse=fam_err, loo=loo.tolist(), fit=pr.tolist(),
                            lineage_out_pred=prf.tolist())
        print(f"{key:12s} k={len(names):2d} fitRMSE={rmse:.4f} LOO-RMSE={loo_rmse:.4f} LOO-rho={rho:.3f} lineage-out RMSE={fam_err:.4f}")
        print("   theta:", {n: round(v, 2) for n, v in zip(names, th)})
    json.dump(dict(points=[dict(name=p["name"], aliases=p["names"], lb=p["lb"], S=p["S"], n=p["n"]) for p in pts],
                   lineage_flag=fam.tolist(), models=results, meta=meta), open(W / "ali_fit.json", "w"), indent=1)


if __name__ == "__main__":
    main()
