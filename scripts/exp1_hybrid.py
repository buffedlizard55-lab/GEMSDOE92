#!/usr/bin/env python3
"""EXP1 final placement: union cap for the main offender family + individual caps for stragglers.

Starts from the two-pool round-1 union (the 30 rasters whose PI-1 dots contained
the most stage-A dots; their halo union is ``U``).  Constraint set:
  * consensus>=5 share <= --trust                 (model trust region)
  * dots inside U <= --cap * n                     (implies every one of the 30)
  * for every later offender R: dots inside halo(R) <= --cap * n   (individual)
Exact lazy greedy with hard caps (slack 30 dots) and per-cap deferral queues.
Each round audits the full 2,060-raster registry; new offenders become new
individual caps.  Stops when the PI-1 audit passes.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import lbm_data as L  # noqa: E402
from gems import lbm_place as P  # noqa: E402
from gems import registry_cache as rc  # noqa: E402
from gems import uniqueness_v3 as U  # noqa: E402
from exp1_twopool import model_dti  # noqa: E402

OUT = ROOT / ".cache" / "exp1" / "hybrid"
OFF = np.array([(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if dy * dy + dx * dx <= 9])


def membership(cand, dots_full, shape):
    H, W = shape
    g = np.zeros(H * W, bool); g[dots_full] = True
    y, x = np.divmod(cand, W)
    hit = np.zeros(cand.size, bool)
    for dy, dx in OFF:
        yy = y + dy; xx = x + dx
        ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
        hit |= ok & g[np.where(ok, yy * W + xx, 0)]
    return hit


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-max", type=int, default=60000)
    ap.add_argument("--cap", type=float, default=0.68)
    ap.add_argument("--trust", type=float, default=0.55)
    ap.add_argument("--trust2", type=float, default=0.78,
                    help="cap on the G015 consensus>=5 share (max observed in scored rasters 0.733 + 0.05)")
    ap.add_argument("--rounds", type=int, default=8)
    ap.add_argument("--union-k", type=int, default=30)
    ap.add_argument("--maps", default=str(ROOT / ".cache" / "lbm" / "lbm_ens_maps.npz"))
    ap.add_argument("--out", default="hybrid_ens")
    args = ap.parse_args()
    out_dir = OUT.parent / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    fp = L.footprint(); cat = L.catalogue(); H, W = L.SHAPE
    maps = np.load(args.maps)
    rho = maps["rho_full"].astype(np.float64)
    cons5 = maps["cons5_018"] if "cons5_018" in maps.files else (maps["cons_full"] >= 5)
    cons5b = maps["cons5_015"] if "cons5_015" in maps.files else cons5
    eligible = fp.mask & ~cat & (L.edt_to(cat) > 2.0)
    iso = P.isolated_value(rho)
    hs = U.load_halo_stats(); shas = sorted(hs)
    rows0 = json.loads((ROOT / ".cache" / "exp1" / "twopool" / "round0_audit_rows.json").read_text())
    top = [r for r in sorted(rows0, key=lambda r: -r["overlap_pi1"]) if r["overlap_pi1"] > 0.70][: args.union_k]
    n0 = 41480
    union_dots = np.zeros(H * W, bool)
    for r in top:
        meta, arr = rc.load_summary(r["sha256"])
        dots = arr["top"] if r["representation"] == "dot_field" else arr["top"][:n0]
        union_dots[fp.lin[dots]] = True
    Uh = ndi.distance_transform_edt(~union_dots.reshape(H, W)) <= 3.0
    ci = np.flatnonzero((eligible & Uh).ravel()); co = np.flatnonzero((eligible & ~Uh).ravel())
    ci = ci[np.argpartition(-iso[ci], min(600000, ci.size - 1))[:600000]] if ci.size > 600000 else ci
    co = co[np.argpartition(-iso[co], min(900000, co.size - 1))[:900000]] if co.size > 900000 else co
    cand = np.sort(np.concatenate([ci, co]))
    cols = [cons5.ravel()[cand], Uh.ravel()[cand], cons5b.ravel()[cand]]
    caps = [args.trust, args.cap, args.trust2]
    names = ["trust:cons>=5 (G018)", f"union:top{len(top)}", "trust:cons>=5 (G015)"]
    capped = {r["sha256"] for r in top}
    rep = dict(method="hybrid: union cap + individual caps", union_members=[r["sha256"] for r in top],
               union_halo_footprint_share=float(Uh[fp.mask].mean()), R0_model=model_dti(L.read01(L.R0) > 0, rho),
               rounds=[])
    print(f"union of {len(top)} -> halo covers {Uh[fp.mask].mean():.3f}; candidates {cand.size}", flush=True)
    cur = None
    for rnd in range(args.rounds):
        res = P.place(rho, eligible, n_max=args.n_max, cand=cand, member=np.stack(cols, axis=1),
                      caps=np.array(caps))
        cur = np.zeros(H * W, bool); cur[res["order"][:res["best_n"]]] = True; cur = cur.reshape(H, W)
        md = model_dti(cur, rho)
        md018 = model_dti(cur, maps["rho_018"].astype(np.float64)) if "rho_018" in maps.files else None
        md015 = model_dti(cur, maps["rho_015"].astype(np.float64)) if "rho_015" in maps.files else None
        aud = U.audit(cur, fp=fp, shas=shas, halo_stats=hs)
        offenders = sorted([r for r in aud["rows"] if r["overlap_pi1"] > args.cap], key=lambda r: -r["overlap_pi1"])
        rec = dict(round=rnd, n=int(cur.sum()), model=md, model_g018=md018, model_g015=md015, n_caps=len(cols), worst_overlap=aud["worst_overlap_pi1"],
                   worst_rho=aud["worst_abs_rho"], offenders_over_cap=len(offenders), duplicate=aud["duplicate"],
                   cons5_share=float(cons5[cur].mean()), union_share=float(Uh[cur].mean()))
        rep["rounds"].append(rec)
        print(f"round {rnd}: n={rec['n']} ens={md['dti']:.4f} g018={md018['dti'] if md018 else 0:.4f} g015={md015['dti'] if md015 else 0:.4f} worst {aud['worst_overlap_pi1']['overlap_pi1']:.4f} "
              f"|rho| {abs(aud['worst_abs_rho']['rho']):.3f} over-cap {len(offenders)} dup={aud['duplicate']} "
              f"caps={len(cols)} [{time.time()-t0:.0f}s]", flush=True)
        np.save(out_dir / f"round{rnd}_sel.npy", np.flatnonzero(cur.ravel()))
        if not aud["duplicate"]:
            rep["final_round"] = rnd
            (out_dir / "final_audit.json").write_text(json.dumps(aud, indent=1), encoding="utf-8")
            break
        added = 0
        for r in offenders:
            if r["sha256"] in capped:
                continue
            capped.add(r["sha256"])
            meta, arr = rc.load_summary(r["sha256"])
            dots = arr["top"] if r["representation"] == "dot_field" else arr["top"][: int(cur.sum())]
            col = membership(cand, fp.lin[dots], (H, W))
            if any(not np.any(col & ~c) for c in cols[3:]):
                continue
            cols.append(col); caps.append(args.cap); names.append(r["sha256"]); added += 1
        if added == 0:
            caps = caps[:3] + [c - 0.01 for c in caps[3:]]
            caps[1] -= 0.01
            print("   no new distinct offenders; tightening caps by 0.01", flush=True)
    np.save(out_dir / "final_sel.npy", np.flatnonzero(cur.ravel()))
    rep["cap_columns"] = names; rep["caps"] = caps; rep["seconds"] = round(time.time() - t0, 1)
    (ROOT / "evidence" / f"exp1_placement_{args.out}.json").write_text(json.dumps(rep, indent=1, default=float), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
