#!/usr/bin/env python3
"""ALI lane, step B: aggregate-label design matrix from owner-reported organizer scores.

For every distinct scored registry raster s (exact registry match of the
owner-reported submission name, see .cache/work/scored_table.json) compute, for
each pixel stratum b of the scored domain (footprint minus the pixel-exact
catalogue mask, organizer forum 11516/2):
  A[s,b] = sum_{g in b} C_s(g),  C_s(g) = max_x p_s(x) k(d(x,g))   (official kernel, R = 3 px)
  B[s,b] = sum_{g in b} (p_s * k)(g)                               (dot kernel mass, for E[max k])
  S[s]   = sum p_s over the scored domain
Strata: d_cat bin x FAM-quantile bin x H19-5-skeleton proximity (<=1.5 px or not).
Then E[TP_s] = sum_b lam_b A[s,b] is EXACT in expectation for any truth process
with pixel inclusion probability lam (linearity), whatever its spatial correlation.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / ".cache" / "work"
REG = ROOT / ".cache" / "gemsdoe_public_registry"
D_EDGES = [0, 3, 8, 20, 1e9]
F_QUANT = [0.0, 0.70, 0.90, 0.96, 0.985, 0.995, 1.0]   # FAM quantiles over the scored domain
H_RAD = 1.5


def kernel_offsets(R=3.0):
    out = []
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            d = (dy * dy + dx * dx) ** 0.5
            if d < R:
                out.append((dy, dx, 1.0 - d / R))
    return out


OFFS = kernel_offsets()
K7 = np.zeros((7, 7), np.float32)
for dy, dx, k in OFFS:
    K7[dy + 3, dx + 3] = k


def coverage(p):
    """C(g) = max_x p(x) k(|x-g|) (exact, shift-max over the 29 in-kernel offsets)."""
    c = np.zeros_like(p)
    H, Wd = p.shape
    for dy, dx, k in OFFS:
        ys = slice(max(dy, 0), H + min(dy, 0)); yd = slice(max(-dy, 0), H + min(-dy, 0))
        xs = slice(max(dx, 0), Wd + min(dx, 0)); xd = slice(max(-dx, 0), Wd + min(-dx, 0))
        np.maximum(c[yd, xd], k * p[ys, xs], out=c[yd, xd])
    return c


def strata(foot, cat, fam_full_fp, idx, h19):
    scored = foot & ~cat
    dcat = ndimage.distance_transform_edt(~cat)
    dh = ndimage.distance_transform_edt(~h19)
    fam = np.full(foot.shape, np.nan, np.float32); fam.ravel()[idx] = fam_full_fp
    qs = np.quantile(fam[scored], F_QUANT)
    qs[0] = -np.inf; qs[-1] = np.inf
    db = np.digitize(dcat, D_EDGES[1:-1], right=True)          # 0..5  ((0,2],(2,3],...)
    fb = np.digitize(np.nan_to_num(fam, nan=-1), qs[1:-1], right=False)   # 0..4
    hb = (dh <= H_RAD).astype(np.int16)
    sid = (db * len(qs[:-1]) + fb) * 2 + hb
    sid = np.where(scored, sid, -1).astype(np.int16)
    nb = (len(D_EDGES) - 1) * (len(F_QUANT) - 1) * 2
    return sid, nb, dict(d_edges=D_EDGES, f_quantiles=F_QUANT, fam_thresholds=[float(x) for x in qs[1:-1]], h_radius_px=H_RAD)


def main():
    t0 = time.time()
    with rasterio.open(ROOT / "data/bridge/sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(ROOT / "data/bridge/existing_faults.tif") as ds:
        cat = ds.read(1) == 1
    with rasterio.open(ROOT / "data/bridge/h19_5.tif") as ds:
        h19 = np.nan_to_num(ds.read(1)) > 0
    sys.path.insert(0, str(ROOT / "scripts"))
    from ali_features import safe_load, safe_save
    idx = np.flatnonzero(foot.ravel())
    fam = safe_load(W / "fam" / "fam_full.npy", json.load(open(W / "fam" / "fam_full.json"))["sha256"])
    if not np.isfinite(fam).all():
        raise SystemExit("FAM has non-finite values")
    sid, nb, meta = strata(foot, cat, fam, idx, h19)
    safe_save(W / "ali_sid.npy", sid)
    if any(not np.isfinite(t) for t in meta["fam_thresholds"]):
        raise SystemExit("non-finite FAM thresholds")
    N = np.bincount(sid[sid >= 0].ravel(), minlength=nb).astype(np.float64)
    tab = [r for r in json.load(open(W / "scored_table.json")) if r.get("status") == "ok"]
    seen, rows = {}, []
    for r in tab:
        key = r["sha1"]
        if key in seen:
            seen[key]["aliases"].append(r["name"]); continue
        with rasterio.open(REG / f"{key}.tif") as ds:
            a = ds.read(1).astype(np.float32)
        p = np.where(np.isfinite(a) & foot & ~cat, np.clip(a, 0, 1), 0).astype(np.float32)
        c = coverage(p)
        kd = ndimage.convolve(p, K7, mode="constant")
        m = sid >= 0
        A = np.bincount(sid[m], weights=c[m], minlength=nb)
        B = np.bincount(sid[m], weights=kd[m], minlength=nb)
        rec = dict(sha1=key, name=r["name"], site=r["site"], lb_claim=r["score_claim"], S=float(p.sum()),
                   n_dots=int((p > 0).sum()), A=A.tolist(), B=B.tolist(), aliases=[])
        seen[key] = rec; rows.append(rec)
        print(f"{len(rows):3d} {r['score_claim']:.4f} {r['name'][:60]} t={time.time()-t0:.0f}s", flush=True)
    json.dump(dict(meta=meta, n_strata=nb, N=N.tolist(), rows=rows), open(W / "ali_design.json", "w"))
    print("rows", len(rows), "strata", nb)


if __name__ == "__main__":
    main()
