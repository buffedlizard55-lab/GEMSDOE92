#!/usr/bin/env python3
"""Fit the session's leaderboard model (LBM-v1) and save it with its validation.

Model: rho = exp(b0 + b_dcat[3] + b_dh19[6] + b_cons[5])  (12 parameters)
  dcat  = distance to the mapped catalogue: <=2 | (2,15] | >15 px
  dh19  = distance to the H19-5 multiline skeleton: 0 | 1 | (1,2] | (2,3] | (3,5] | >5 px
  cons  = number of the 10 "G-set" rasters with a dot within 2 px: 0 | 1 | 2 | 3-4 | >=5
G-set (fixed rule): CLAIM >= 0.18 and < 30% of dots on the H19-5 skeleton.

Validation: leave-one-group-out (groups: the whole H19-5 dotting family as one
group, every other site its own group; the consensus layer is rebuilt without
held-out G-set members).  Writes evidence/lbm_v1_model.json and
.cache/lbm/lbm_v1_maps.npz (class maps + rho for placement).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import lbm_data as L  # noqa: E402
import lbm_harness as Hh  # noqa: E402
from gems import lbmodel as M  # noqa: E402

LEVELS = (3, 6, 5)
LAM = 1e-3
OUT_JSON = ROOT / "evidence" / "lbm_v1_model.json"
OUT_MAPS = ROOT / ".cache" / "lbm" / "lbm_v1_maps.npz"


def layers():
    fp = L.footprint(); cat = L.catalogue(); lin = fp.lin
    scored_full = fp.mask & ~cat
    dcat_full = L.edt_to(cat)
    h19 = L.read01(L.H195) > 0
    dh_full = L.edt_to(h19)
    return fp, cat, lin, scored_full, dcat_full, dh_full


def factor_ids(dcat, dh, cons):
    f1 = np.digitize(dcat, [2.01, 15.01])
    f2 = np.digitize(dh, [0.5, 1.01, 2.01, 3.01, 5.01])
    f3 = np.digitize(cons, [0.5, 1.5, 2.5, 4.5])
    return ((f1 * LEVELS[1] + f2) * LEVELS[2] + f3).astype(np.int32)


def main() -> int:
    fp, cat, lin, scored_full, dcat_full, dh_full = layers()
    H, W = L.SHAPE
    scored = scored_full.ravel()[lin]
    dcat = dcat_full.ravel()[lin]; dh = dh_full.ravel()[lin]
    rows = Hh.scored_rows()
    y = np.array([r["claim"] for r in rows])
    sha = np.array([r["match"]["sha256"] for r in rows])
    onh = np.array([float((dh[np.load(Hh.CACHE / f"{s}.npz")["pos"]] < 0.5).mean()) for s in sha])
    gset = (y >= 0.18) & (onh < 0.30)
    groups = np.array(["H19FAM" if o >= 0.7 else r["site"] for o, r in zip(onh, rows)])
    near2 = {}
    near2_full = {}
    for s in dict.fromkeys(sha[gset]):
        z = np.load(Hh.CACHE / f"{s}.npz")
        m = np.zeros(H * W, bool); m[lin[z["pos"]]] = True
        d = ndi.distance_transform_edt(~m.reshape(H, W))
        near2_full[s] = d <= 2.0
        near2[s] = near2_full[s].ravel()[lin]

    def cons_vec(excl=()):
        c = np.zeros(lin.size, np.int16)
        for s, v in near2.items():
            if s not in excl:
                c += v
        return c

    def cmap(cons):
        c = factor_ids(dcat, dh, cons); c[~scored] = -1
        return c

    X = M.factor_design(LEVELS)
    S = Hh.stats({"f": cmap(cons_vec())}, rows, scored)["f"]
    fit = M.fit_loglinear(S["A"], S["m"], S["n"], y, S["Ncls"], X, lam=LAM)
    # grouped CV
    cv = np.zeros(len(y))
    for g in np.unique(groups):
        te = groups == g; tr = ~te
        excl = set(sha[te & gset])
        Sg = Hh.stats({"f": cmap(cons_vec(excl))}, rows, scored)["f"] if excl else S
        f = M.fit_loglinear(Sg["A"][tr], Sg["m"][tr], Sg["n"][tr], y[tr], Sg["Ncls"], X, lam=LAM,
                            beta0=fit["beta"])
        cv[te] = M.predict(f["rho"], Sg["A"][te], Sg["m"][te], Sg["n"][te], Sg["Ncls"])
    h = groups == "H19FAM"
    resid = cv - y
    val = dict(
        logo_rmse_all=float(np.sqrt(np.mean(resid ** 2))),
        logo_spearman_all=float(spearmanr(cv, y)[0]),
        logo_rmse_h19_family=float(np.sqrt(np.mean(resid[h] ** 2))),
        logo_bias_h19_family=float(np.mean(resid[h])),
        logo_rmse_non_gset=float(np.sqrt(np.mean(resid[~gset] ** 2))),
        logo_rmse_gset=float(np.sqrt(np.mean(resid[gset] ** 2))),
        logo_q95_abs_error=float(np.quantile(np.abs(resid), 0.95)),
        n_rows=int(len(y)), n_groups=int(len(np.unique(groups))),
    )
    # full-grid maps for placement
    cons_full = np.zeros((H, W), np.int16)
    for s, v in near2_full.items():
        cons_full += v
    cls_full = factor_ids(dcat_full, dh_full, cons_full)
    rho_full = fit["rho"][cls_full]
    rho_full[~scored_full] = 0.0
    OUT_MAPS.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT_MAPS, rho_full=rho_full.astype(np.float32), cls_full=cls_full,
                        cons_full=cons_full, gset_shas=np.array(sorted(near2_full)))
    names = (["intercept"] + [f"dcat:{l}" for l in ("(2,15]", ">15")] +
             [f"dh19:{l}" for l in ("1", "(1,2]", "(2,3]", "(3,5]", ">5")] +
             [f"cons:{l}" for l in ("1", "2", "3-4", ">=5")])
    out = dict(
        schema="gemsdoe92-lbm-v1", created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        evidence_class="MODEL (fitted to owner-reported CLAIM scores; never an organizer score)",
        model="rho = exp(X beta); E[TP]=sum rho*C; E[M]=sum p*min(1,3rho); DTI=TP/(TP+0.2FP+0.8(G-TP))",
        levels=dict(dcat=["<=2", "(2,15]", ">15"], dh19=["0", "1", "(1,2]", "(2,3]", "(3,5]", ">5"],
                    cons=["0", "1", "2", "3-4", ">=5"]),
        lam=LAM, beta=dict(zip(names, [round(float(b), 6) for b in fit["beta"]])),
        multipliers=dict(zip(names[1:], [round(float(np.exp(b)), 4) for b in fit["beta"][1:]])),
        G_footprint_units=fit["G"], in_sample_rmse=fit["rmse"], validation=val,
        gset=[dict(site=rows[i]["site"], name=rows[i]["name"], claim=float(y[i]), sha256=sha[i],
                   on_h19_fraction=round(float(onh[i]), 4)) for i in np.flatnonzero(gset)],
        rows=[dict(site=r["site"], name=r["name"], claim=float(y[i]), fitted=round(float(fit["pred"][i]), 5),
                   logo=round(float(cv[i]), 5), group=str(groups[i]), sha256=sha[i])
              for i, r in enumerate(rows)],
    )
    OUT_JSON.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(dict(beta=out["multipliers"], G=out["G_footprint_units"], val=val), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
