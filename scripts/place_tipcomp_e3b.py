#!/usr/bin/env python3
"""E3b (placement revision inside experiment 3): ensemble density
sqrt(rho_published128 x rho_refit26) x tip x complement, with individual
3-px caps vs priors, focus-9 peaks, and every E3a offender >0.60."""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
from gems import lbmodel as M, lbm_place as P, tipcomp as TC, uniqueness_v3 as U  # noqa
from gems57 import grid as grid_mod  # noqa

H, W = 3730, 3292; CACHE = ROOT / ".cache" / "tipcomp"; F9 = ROOT / ".cache" / "focus9_20261028b"
def read01(p):
    with rasterio.open(p) as ds: a = ds.read(1).astype(np.float32)
    return np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
def edt(m): return ndi.distance_transform_edt(~m).astype(np.float32)
def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)
OFF3 = [(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if dy*dy + dx*dx <= 9]
def halo_col(cand, dots):
    halo = np.zeros(H * W, bool); dy_, dx_ = np.divmod(dots, W)
    for ddy, ddx in OFF3:
        ry, rx = dy_ + ddy, dx_ + ddx; ok = (ry >= 0) & (ry < H) & (rx >= 0) & (rx < W)
        halo[ry[ok] * W + rx[ok]] = True
    return halo[cand]

def main():
    grid = grid_mod.load_grid(ROOT / "data" / "bridge"); foot, cat = grid.footprint, grid.catalogue
    h19 = read01(ROOT/"data/bridge/h19_5.tif") > 0; dcat, dh19 = edt(cat), edt(h19)
    GSET = ["GSET_G10_h28_01839.tif","GSET_G27_h29_0219.tif","GEMSDOE27_h31_0225.tif","GSET_G49_gate_02376.tif",
            "GSET_G48_h59_02296.tif","GSET_G70_p5_02478.tif","GSET_G73_h73_01917.tif","GSET_G76_ptcf_02343.tif",
            "GSET_G82_h82_01886.tif","GSET_G91_lftg_01823.tif"]
    cons = np.zeros((H, W), np.int16)
    for fn in GSET: cons += (edt(read01(F9/fn) > 0) <= 2.0)
    cls = ((np.digitize(dcat, [2.01, 15.01]) * 6 + np.digitize(dh19, [0.5, 1.01, 2.01, 3.01, 5.01])) * 5
           + np.digitize(cons, [0.5, 1.5, 2.5, 4.5])).astype(np.int32)
    scored = foot & ~cat; cls_sc = np.where(scored, cls, -1); K = 90
    z = np.load(CACHE/"design.npz"); Ncls = z["Ncls"]
    rho_pub_map = z["rho_pub"][cls].astype(np.float64)
    rho_ref_map = z["rho_refit"][cls].astype(np.float64)
    tip = TC.tip_continuation_field(cat)
    peaks = [F9/"GEMSDOE24_peak_d15.tif", ROOT/"data/bridge/d28.tif", F9/"GEMSDOE27_peak_gap.tif",
             F9/"GEMSDOE28_peak_h36.tif", F9/"GEMSDOE30_peak_d28p.tif", F9/"GEMSDOE31_peak_solo.tif",
             ROOT/"data/parent_R0_zeros.tif", F9/"GEMSDOE33_peak_h33d.tif", F9/"GEMSDOE36_peak_pinn.tif"]
    comp = TC.coverage_complement(dh19, [read01(p) > 0 for p in peaks])
    tip_c = tip - float(tip[scored].mean())
    rho = np.sqrt(np.maximum(rho_pub_map, 1e-12) * np.maximum(rho_ref_map, 1e-12)) \
        * np.clip(1.0 + 0.35 * tip_c, 0.65, 1.40) * (1.0 + 0.25 * comp)
    eligible = foot & ~cat & (dcat > 2.0); rho[~eligible] = 0.0
    np.save(CACHE/"rho_ens.npy", rho.astype(np.float32))
    iso = P.isolated_value(rho); elin = np.flatnonzero(eligible.ravel())
    cand = np.sort(elin[np.argpartition(-iso[elin], 350_000)[:350_000]])  # provisional; expanded below
    # cap sources: priors + peaks + E3a offenders > 0.60
    ev = json.loads((ROOT/"evidence/tipcomp_20261028.json").read_text())
    offenders = [r["file"] for r in ev["uniqueness"]["rows"] if r["overlap_pi1"] > 0.60]
    cap_files = {}
    for p in peaks: cap_files[str(p.relative_to(ROOT)) if str(p).startswith(str(ROOT)) else str(p)] = 0.65
    cap_files["docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif"] = 0.60
    cap_files["docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif"] = 0.60
    for f in offenders: cap_files.setdefault(f, 0.65)
    dot_lists, caps, names = [], [], []
    for rel, cp in cap_files.items():
        p = (ROOT / rel) if not Path(rel).is_absolute() else Path(rel)
        if not p.exists(): log("skip missing", rel); continue
        dot_lists.append(np.flatnonzero((read01(p) > 0).ravel())); caps.append(cp); names.append(rel)
    # expand pool with best candidates OUTSIDE the offender-union halo (anti-deadlock)
    union_dots = np.unique(np.concatenate(dot_lists)) if dot_lists else np.array([], np.int64)
    uhalo = np.zeros(H * W, bool); uy, ux = np.divmod(union_dots, W)
    for ddy, ddx in OFF3:
        ry, rx = uy + ddy, ux + ddx; ok = (ry >= 0) & (ry < H) & (rx >= 0) & (rx < W)
        uhalo[ry[ok] * W + rx[ok]] = True
    out_pool = elin[~uhalo[elin]]
    k_out = min(250_000, max(out_pool.size - 1, 0))
    top_out = out_pool[np.argpartition(-iso[out_pool], k_out)[:250_000]] if out_pool.size > 1 else out_pool
    cand = np.sort(np.unique(np.concatenate([cand, top_out])))
    log(f"pool={cand.size} outside-union in pool={int((~uhalo[cand]).sum())}")
    cols = [halo_col(cand, d) for d in dot_lists]
    # aggregate skeleton-halo column: bounds overlap vs every on-skeleton raster
    cols.append((dh19.ravel()[cand] <= 3.0)); caps.append(0.62); names.append("AGG_dh19_le3")
    log(f"cap columns={len(cols)}")
    res = P.place(rho, eligible, n_max=60_000, cand=cand, member=np.stack(cols, axis=1), caps=np.array(caps))
    order = np.asarray(res["order"]); log("best_n", res["best_n"], "best_D", res.get("best_D"), "D_end", res.get("D"))
    np.save(CACHE/"e3b_order.npy", order)
    # evaluate prefixes under BOTH specs; pick max of min(pub, refit)
    grid_n = sorted(set([int(res["best_n"]), 19071, 25000, 30000, 35000, 37654, 40000, 44090, 50000, int(order.size)]))
    table = {}
    for nn in grid_n:
        if nn <= 0 or nn > order.size: continue
        arr = np.zeros(H * W, np.float32); arr[order[:nn]] = 1.0
        r = M.design_row(arr.reshape(H, W), cls_sc, K)
        pub = float(M.predict(z["rho_pub"], r["A"], r["m"], r["n"], Ncls)[0])
        ref = float(M.predict(z["rho_refit"], r["A"], r["m"], r["n"], Ncls)[0])
        table[str(nn)] = dict(published128=pub, refit26=ref, min_spec=min(pub, ref))
        log(f"n={nn} pub={pub:.4f} refit={ref:.4f}")
    best = max(table.items(), key=lambda kv: kv[1]["min_spec"])
    nn = int(best[0]); dots = np.sort(order[:nn]); np.save(CACHE/"candidate_dots_e3b.npy", dots)
    real = {}
    for rel, cp in cap_files.items():
        p = (ROOT / rel) if not Path(rel).is_absolute() else Path(rel)
        if p.exists(): real[rel] = float(U.near_fraction(dots, np.flatnonzero((read01(p) > 0).ravel()), (H, W)))
    out = dict(best_n_place=int(res["best_n"]), best_D_place=float(res.get("best_D", float("nan"))),
               prefix_table=table, chosen_n=nn, caps=dict(zip(names, caps)), realised=real,
               worst_realised=max(real.values()) if real else None)
    (CACHE/"e3b_summary.json").write_text(json.dumps(out, indent=2, default=float))
    ev["E3b"] = out; (ROOT/"evidence/tipcomp_20261028.json").write_text(json.dumps(ev, indent=2, default=float))
    log("chosen", nn, best[1], "worst realised cap overlap", out["worst_realised"])

if __name__ == "__main__":
    main()
