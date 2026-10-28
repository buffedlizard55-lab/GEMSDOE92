#!/usr/bin/env python3
"""E3c: union-halo cap placement (one column bounds every registry raster by
monotonicity: offender halo subset of union halo) on the ensemble surface."""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
from gems import lbmodel as M, lbm_place as P, uniqueness_v3 as U  # noqa
from gems57 import grid as grid_mod  # noqa

H, W = 3730, 3292; CACHE = ROOT / ".cache" / "tipcomp"; F9 = ROOT / ".cache" / "focus9_20261028b"
def read01(p):
    with rasterio.open(p) as ds: a = ds.read(1).astype(np.float32)
    return np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
def edt(m): return ndi.distance_transform_edt(~m).astype(np.float32)
def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)
OFF3 = [(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if dy*dy + dx*dx <= 9]
def halo_mask(dots):
    halo = np.zeros(H * W, bool); dy_, dx_ = np.divmod(dots, W)
    for ddy, ddx in OFF3:
        ry, rx = dy_ + ddy, dx_ + ddx; ok = (ry >= 0) & (ry < H) & (rx >= 0) & (rx < W)
        halo[ry[ok] * W + rx[ok]] = True
    return halo

def main():
    grid = grid_mod.load_grid(ROOT / "data" / "bridge"); foot, cat = grid.footprint, grid.catalogue
    rho = np.load(CACHE/"rho_ens.npy").astype(np.float64)
    dcat = edt(cat); eligible = foot & ~cat & (dcat > 2.0); rho[~eligible] = 0.0
    # rebuild cls for prefix scoring
    h19 = read01(ROOT/"data/bridge/h19_5.tif") > 0; dh19 = edt(h19)
    GSET = ["GSET_G10_h28_01839.tif","GSET_G27_h29_0219.tif","GEMSDOE27_h31_0225.tif","GSET_G49_gate_02376.tif",
            "GSET_G48_h59_02296.tif","GSET_G70_p5_02478.tif","GSET_G73_h73_01917.tif","GSET_G76_ptcf_02343.tif",
            "GSET_G82_h82_01886.tif","GSET_G91_lftg_01823.tif"]
    cons = np.zeros((H, W), np.int16)
    for fn in GSET: cons += (edt(read01(F9/fn) > 0) <= 2.0)
    cls = ((np.digitize(dcat, [2.01, 15.01]) * 6 + np.digitize(dh19, [0.5, 1.01, 2.01, 3.01, 5.01])) * 5
           + np.digitize(cons, [0.5, 1.5, 2.5, 4.5])).astype(np.int32)
    cls_sc = np.where(foot & ~cat, cls, -1); K = 90
    z = np.load(CACHE/"design.npz"); Ncls = z["Ncls"]
    # union of literal positives over the local registry (dedup by sha), excluding grid files
    reg = sorted((ROOT/"docs/downloads").glob("*.tif")) + sorted(F9.glob("*.tif")) + sorted((ROOT/"data").rglob("*.tif"))
    skip = {"existing_faults.tif", "labels.tif", "sample_submission.tif"}
    union = np.zeros(H * W, bool); seen = set(); nreg = 0
    fp_lin = np.flatnonzero(foot.ravel())
    for p in reg:
        if p.name in skip: continue
        s = hashlib.sha256(p.read_bytes()).hexdigest()
        if s in seen: continue
        seen.add(s); nreg += 1
        a = read01(p); pos = a > 0; npos = int(pos.sum())
        if npos == 0: continue
        if npos / float(foot.sum()) <= 0.20 and float((edt(pos) <= 3.0)[foot].mean()) <= 0.70:
            union |= pos.ravel()  # PI-1 dot field: literal dots
        else:  # PI-1 surface: top-44090 by value inside footprint
            v = a.ravel()[fp_lin]; k = min(44090, fp_lin.size)
            union[fp_lin[np.argpartition(-v, k)[:k]]] = True
    union_halo = halo_mask(np.flatnonzero(union))
    log(f"registry rasters={nreg} union positives={int(union.sum())} union halo frac(foot)={float(union_halo.reshape(H,W)[foot].mean()):.3f}")
    iso = P.isolated_value(rho); elin = np.flatnonzero(eligible.ravel())
    top_all = elin[np.argpartition(-iso[elin], 400_000)[:400_000]]
    out_pool = elin[~union_halo[elin]]
    top_out = out_pool[np.argpartition(-iso[out_pool], min(250_000, out_pool.size))[:250_000]] if out_pool.size else out_pool
    cand = np.sort(np.unique(np.concatenate([top_all, top_out])))
    log("cand outside union halo:", int((~union_halo[cand]).sum()), "/", cand.size)
    srcs = [("union_registry", union_halo, 0.68),
            ("lbmc1", halo_mask(np.flatnonzero((read01(ROOT/"docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif") > 0).ravel())), 0.58),
            ("rieszlbm2", halo_mask(np.flatnonzero((read01(ROOT/"docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif") > 0).ravel())), 0.58),
            ("R0_G32", halo_mask(np.flatnonzero((read01(ROOT/"data/parent_R0_zeros.tif") > 0).ravel())), 0.60)]
    member = np.stack([h_[cand] for _, h_, _ in srcs], axis=1)
    res = P.place(rho, eligible, n_max=60_000, cand=cand, member=member, caps=np.array([c for _, _, c in srcs]))
    order = np.asarray(res["order"]); np.save(CACHE/"e3c_order.npy", order)
    log("order", order.size, "best_n", res["best_n"], "best_D", res.get("best_D"))
    table = {}
    for nn in sorted(set([int(res["best_n"]), 25000, 30000, 35000, 37654, 40000, 44090, 50000, int(order.size)])):
        if nn <= 0 or nn > order.size: continue
        arr = np.zeros(H * W, np.float32); arr[order[:nn]] = 1.0
        r = M.design_row(arr.reshape(H, W), cls_sc, K)
        pub = float(M.predict(z["rho_pub"], r["A"], r["m"], r["n"], Ncls)[0])
        ref = float(M.predict(z["rho_refit"], r["A"], r["m"], r["n"], Ncls)[0])
        table[str(nn)] = dict(published128=pub, refit26=ref, min_spec=min(pub, ref))
        log(f"n={nn} pub={pub:.4f} refit={ref:.4f}")
    best = max(table.items(), key=lambda kv: kv[1]["min_spec"]); nn = int(best[0])
    dots = np.sort(order[:nn]); np.save(CACHE/"candidate_dots_e3c.npy", dots)
    real = {nm: float(union_halo[dots].mean()) if nm == "union_registry" else
            float(U.near_fraction(dots, np.flatnonzero(h_.reshape(H, W).ravel() & False), (H, W))) for nm, h_, _ in srcs[:1]}
    for nm, pth in [("lbmc1", ROOT/"docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif"),
                    ("rieszlbm2", ROOT/"docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif"),
                    ("R0_G32", ROOT/"data/parent_R0_zeros.tif")]:
        real[nm] = float(U.near_fraction(dots, np.flatnonzero((read01(pth) > 0).ravel()), (H, W)))
    out = dict(n_registry=nreg, prefix_table=table, chosen_n=nn, realised=real,
               best_n_place=int(res["best_n"]), best_D_place=float(res.get("best_D", float("nan"))))
    (CACHE/"e3c_summary.json").write_text(json.dumps(out, indent=2, default=float))
    ev = json.loads((ROOT/"evidence/tipcomp_20261028.json").read_text()); ev["E3c"] = out
    (ROOT/"evidence/tipcomp_20261028.json").write_text(json.dumps(ev, indent=2, default=float))
    log("chosen", nn, best[1], real)

if __name__ == "__main__":
    main()
