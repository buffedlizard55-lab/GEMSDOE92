#!/usr/bin/env python3
"""Repair v2: refill pool excludes the UNION of all current offender halos."""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
from gems import lbm_place as P, uniqueness_v3 as U  # noqa
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
    dots0 = np.load(CACHE/"candidate_dots_e3d.npy"); n_target = dots0.size
    grid = grid_mod.load_grid(ROOT / "data" / "bridge"); foot, cat = grid.footprint, grid.catalogue
    rho = np.load(CACHE/"rho_ens.npy").astype(np.float64); iso = P.isolated_value(rho)
    eligible = (foot & ~cat & (edt(cat) > 2.0)).ravel()
    fp_lin = np.flatnonzero(foot.ravel())
    reg_files = sorted((ROOT/"docs/downloads").glob("*.tif")) + sorted(F9.glob("*.tif")) + sorted((ROOT/"data").rglob("*.tif"))
    reg, seen = {}, set()
    for p in reg_files:
        s = hashlib.sha256(p.read_bytes()).hexdigest()
        if s in seen: continue
        seen.add(s); a = read01(p); pos = a > 0; npos = int(pos.sum())
        if npos == 0: continue
        if npos / float(foot.sum()) <= 0.20:
            their = np.flatnonzero(pos.ravel())
            if float((edt(pos) <= 3.0)[foot].mean()) > 0.70:
                v = a.ravel()[fp_lin]; k = min(n_target, fp_lin.size); their = fp_lin[np.argpartition(-v, k)[:k]]
        else:
            v = a.ravel()[fp_lin]; k = min(n_target, fp_lin.size); their = fp_lin[np.argpartition(-v, k)[:k]]
        reg[str(p.relative_to(ROOT))] = np.sort(their)
    halos = {nm: halo_mask(th) for nm, th in reg.items()}
    log(f"registry={len(reg)} n={n_target}")
    dotset = np.zeros(H * W, bool); dotset[dots0] = True
    def audit(ds):
        cur = np.flatnonzero(ds)
        return sorted(((float(halos[nm][cur].mean()), nm) for nm in reg), reverse=True)
    for rnd in range(6):
        ranked = audit(dotset); worst = ranked[:5]
        log(f"round {rnd} worst:", [(round(w, 4), nm.split('/')[-1][:40]) for w, nm in worst])
        offenders = [nm for w, nm in ranked if w > 0.68]
        if not offenders: break
        union_halo = np.zeros(H * W, bool)
        counts = np.zeros(H * W, np.int16)
        for nm in offenders: union_halo |= halos[nm]; counts += halos[nm]
        cur = np.flatnonzero(dotset)
        # remove: dots inside the worst offender halo first, highest offender-count, lowest iso
        w0, nm0 = ranked[0]
        inside = cur[halos[nm0][cur]]
        n_move = int(np.ceil((w0 - 0.64) * cur.size))
        order = np.lexsort((iso[inside], -counts[inside]))
        inside = inside[order[:n_move]]
        pool = np.flatnonzero(eligible & ~union_halo & ~dotset)
        if pool.size < inside.size:
            log(f"  pool short: {pool.size} < {inside.size}; relaxing to worst-halo-only exclusion")
            pool = np.flatnonzero(eligible & ~halos[nm0] & ~dotset)
        pool = pool[np.argsort(-iso[pool])[:inside.size]]
        dotset[inside] = False; dotset[pool] = True
        log(f"  moved {inside.size} (offenders={len(offenders)}, worst={nm0.split('/')[-1][:40]})")
    out = np.flatnonzero(dotset); np.save(CACHE/"candidate_dots_final.npy", out)
    ranked = audit(dotset)
    log("final worst:", [(round(w, 4), nm.split('/')[-1][:40]) for w, nm in ranked[:6]], "n=", out.size)
    (CACHE/"repair2_summary.json").write_text(json.dumps(dict(final_worst=ranked[:10], n=int(out.size)), indent=2, default=float))

if __name__ == "__main__":
    main()
