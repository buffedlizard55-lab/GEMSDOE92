#!/usr/bin/env python3
"""Build the ensemble density map rho_ens = mean(rho_G018, rho_G015) for robust placement.

Two consensus definitions fit the CLAIM scores almost equally well (G-set CLAIM >= 0.18:
grouped RMSE 0.0206; >= 0.15: 0.0236).  A candidate optimised for one can look like a tie
with R0 under the other, so placement uses their mean (expected TP is linear in rho).
Writes .cache/lbm/lbm_ens_maps.npz and evidence/lbm_ensemble_model.json.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import lbm_data as L  # noqa: E402
import lbm_harness as Hh  # noqa: E402
from gems import lbmodel as M  # noqa: E402


def main() -> int:
    fp = L.footprint(); cat = L.catalogue(); lin = fp.lin; H, W = L.SHAPE
    scored_full = fp.mask & ~cat; scored = scored_full.ravel()[lin]
    dcat_full = L.edt_to(cat); dh_full = L.edt_to(L.read01(L.H195) > 0)
    dcat = dcat_full.ravel()[lin]; dh = dh_full.ravel()[lin]
    rows = Hh.scored_rows(); y = np.array([r["claim"] for r in rows]); sha = np.array([r["match"]["sha256"] for r in rows])
    onh = np.array([float((dh[np.load(Hh.CACHE / f"{s}.npz")["pos"]] < 0.5).mean()) for s in sha])
    X = M.factor_design((3, 6, 5))
    out = {}; rho_maps = []
    for thr in (0.18, 0.15):
        gset = (y >= thr) & (onh < 0.30)
        cons_full = np.zeros((H, W), np.int16)
        for s in dict.fromkeys(sha[gset]):
            z = np.load(Hh.CACHE / f"{s}.npz"); g = np.zeros(H * W, bool); g[lin[z["pos"]]] = True
            cons_full += (ndi.distance_transform_edt(~g.reshape(H, W)) <= 2.0)
        cls_full = ((np.digitize(dcat_full, [2.01, 15.01]) * 6 + np.digitize(dh_full, [0.5, 1.01, 2.01, 3.01, 5.01])) * 5
                    + np.digitize(cons_full, [0.5, 1.5, 2.5, 4.5])).astype(np.int32)
        cm = cls_full.ravel()[lin].copy(); cm[~scored] = -1
        S = Hh.stats({"f": cm}, rows, scored)["f"]
        f = M.fit_loglinear(S["A"], S["m"], S["n"], y, S["Ncls"], X, lam=1e-3)
        rho = f["rho"][cls_full]; rho[~scored_full] = 0.0
        rho_maps.append(rho.astype(np.float32))
        out[f"gset_{thr}"] = dict(n_gset=int(gset.sum()), in_sample_rmse=f["rmse"], G=f["G"],
                                  beta=[float(b) for b in f["beta"]])
        if thr == 0.18:
            cons5_018 = cons_full >= 5
        else:
            cons5_015 = cons_full >= 5
    rho_ens = 0.5 * (rho_maps[0] + rho_maps[1])
    np.savez_compressed(ROOT / ".cache" / "lbm" / "lbm_ens_maps.npz", rho_full=rho_ens, rho_018=rho_maps[0], rho_015=rho_maps[1],
                        cons5_018=cons5_018, cons5_015=cons5_015)
    (ROOT / "evidence" / "lbm_ensemble_model.json").write_text(json.dumps(dict(
        schema="gemsdoe92-lbm-ensemble-v1", evidence_class="MODEL", combination="arithmetic mean of rho maps",
        grouped_cv_rmse={"gset_0.18": 0.0206, "gset_0.15": 0.0236}, members=out), indent=1), encoding="utf-8")
    print(json.dumps({k: dict(n=v["n_gset"], rmse=round(v["in_sample_rmse"], 4)) for k, v in out.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
