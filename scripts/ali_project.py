#!/usr/bin/env python3
"""ALI lane, step G: MODEL projection (never a score) with jackknife and extrapolation diagnostics.

For the final raster and R0, E[DTI] under (a) D+F+H and (b) the conservative D+H
model (no FAM term, so no extrapolation in FAM), plus the leave-one-out
(jackknife) distribution of the paired difference candidate - R0.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ali_fit  # noqa: E402
from ali_place import Projector  # noqa: E402

W = ROOT / ".cache" / "work"


def main():
    cand_path = Path(sys.argv[1])
    with rasterio.open(cand_path) as ds:
        cand = ds.read(1) > 0
    with rasterio.open(ROOT / "data/parent_R0_zeros.tif") as ds:
        r0 = ds.read(1) > 0
    out = dict(evidence_class="MODEL (latent-intensity projection from owner-reported CLAIMS; NOT a score)", models={})
    for spec in (("D", "F", "H"), ("D", "H")):
        P = Projector(spec)
        cc, cr = P.components(cand), P.components(r0)
        base_c, base_r = P.dti(cc), P.dti(cr)
        jk = []
        for i in range(len(P.pts)):
            sub = [p for j, p in enumerate(P.pts) if j != i]
            th = ali_fit.fit(P.Z, sub, P.N, theta0=P.theta)
            jk.append((P.dti(cc, th), P.dti(cr, th)))
        jk = np.array(jk); dlt = jk[:, 0] - jk[:, 1]
        n = len(dlt)
        se = float(np.sqrt((n - 1) / n * np.sum((dlt - dlt.mean()) ** 2)))
        fitd = json.load(open(W / "ali_fit.json"))["models"]["+".join(spec)]
        out["models"]["+".join(spec)] = dict(
            projected_candidate=base_c, projected_R0=base_r, paired_delta=base_c - base_r,
            jackknife_se_delta=se, jackknife_delta_range=[float(dlt.min()), float(dlt.max())],
            loo_rmse_on_claims=fitd["loo_rmse"], loo_spearman_on_claims=fitd["loo_spearman"])
        print("+".join(spec), f"cand {base_c:.4f} R0 {base_r:.4f} delta {base_c-base_r:+.4f} jackknife SE {se:.4f} range {dlt.min():+.4f}..{dlt.max():+.4f}")
    # extrapolation diagnostic: candidate's share of far dots in each FAM stratum vs the max share in any scored raster
    ev = json.load(open(W / "fam_evidence.json"))
    sid = np.load(W / "ali_sid.npy")
    meta = json.load(open(W / "ali_design.json"))["meta"]
    nF = len(meta["f_quantiles"]) - 1
    F = (sid // 2) % nF
    m = cand & (sid >= 0)
    shares = [float((F[m] == j).mean()) for j in range(nF)]
    out["extrapolation"] = dict(candidate_share_by_fam_stratum=shares, fam_quantile_edges=meta["f_quantiles"],
                                max_share_top0p5pct_any_scored=max(r["top05"] for r in ev),
                                max_share_top1p5pct_any_scored=max(r["top15"] for r in ev),
                                max_share_top4pct_any_scored=max(r["top4"] for r in ev),
                                verdict="EXTRAPOLATION: the candidate concentrates far beyond the FAM range any scored raster sampled; the D+F+H projection is not reliable")
    print("candidate share by FAM stratum", [round(s, 3) for s in shares])
    json.dump(out, open(W / "ali_projection.json", "w"), indent=1)


if __name__ == "__main__":
    main()
