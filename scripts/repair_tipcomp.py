#!/usr/bin/env python3
"""Swap-repair: for each registry offender with PI-1 overlap > 0.68, move the
lowest-value in-halo dots to the highest-value eligible cells outside that
halo (n fixed). Rounds until worst <= 0.68 or 4 rounds."""
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
    dots = np.load(CACHE/"candidate_dots_e3d.npy")
    grid = grid_mod.load_grid(ROOT / "data" / "bridge"); foot, cat = grid.footprint, grid.catalogue
    rho = np.load(CACHE/"rho_ens.npy").astype(np.float64)
    iso = P.isolated_value(rho)
    eligible = foot & ~cat & (edt(cat) > 2.0)
    fp_lin = np.flatnonzero(foot.ravel())
    # build PI-1 registry dot sets once
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
                v = a.ravel()[fp_lin]; k = min(dots.size, fp_lin.size); their = fp_lin[np.argpartition(-v, k)[:k]]
        else:
            v = a.ravel()[fp_lin]; k = min(dots.size, fp_lin.size); their = fp_lin[np.argpartition(-v, k)[:k]]
        reg[str(p.relative_to(ROOT))] = np.sort(their)
    log(f"registry sets={len(reg)} n={dots.size}")
    dotset = np.zeros(H * W, bool); dotset[dots] = True
    history = []
    for rnd in range(4):
        cur = np.flatnonzero(dotset)
        worst = sorted(((float(U.near_fraction(cur, th, (H, W))), nm) for nm, th in reg.items()), reverse=True)[:6]
        history.append(worst)
        log(f"round {rnd} worst:", [(round(w, 4), nm.split('/')[-1][:44]) for w, nm in worst])
        if worst[0][0] <= 0.68: break
        for w, nm in worst:
            if w <= 0.68: continue
            cur = np.flatnonzero(dotset); halo = halo_mask(reg[nm])
            inside = cur[halo[cur]]; n_move = int(np.ceil((w - 0.66) * cur.size))
            inside = inside[np.argsort(iso[inside])[:n_move]]  # lowest value first
            pool = np.flatnonzero((eligible.ravel()) & ~halo & ~dotset)
            pool = pool[np.argsort(-iso[pool])[:n_move]]
            dotset[inside] = False; dotset[pool] = True
            log(f"  moved {inside.size} dots out of {nm.split('/')[-1][:44]}")
    out_dots = np.flatnonzero(dotset); np.save(CACHE/"candidate_dots_final.npy", out_dots)
    final_worst = sorted(((float(U.near_fraction(out_dots, th, (H, W))), nm) for nm, th in reg.items()), reverse=True)[:6]
    log("final worst:", [(round(w, 4), nm.split('/')[-1][:44]) for w, nm in final_worst], "n=", out_dots.size)
    (CACHE/"repair_summary.json").write_text(json.dumps(dict(history=history, final_worst=final_worst, n=int(out_dots.size)), indent=2, default=float))

if __name__ == "__main__":
    main()
