#!/usr/bin/env python3
"""EXP1 placement, final form: two-pool capped greedy (provably satisfies every offender cap).

Round 0  -- trust-capped greedy (consensus>=5 share <= ``--trust``), full registry audit.
Round k  -- U = 3 px halo of the UNION of all offender dot sets (halo of a union =
            union of halos), so for every offender R: dots_in(R) <= dots_in(U).
            Greedy with one hard cap ``dots_in(U) <= --cap * n`` (+ the trust cap);
            candidates = best cells inside U plus best cells outside U.  Audit the
            full registry again; any new offender is merged into U.  Stop when the
            PI-1 audit passes.
Outputs .cache/exp1/twopool/ and evidence/exp1_placement.json (MODEL numbers only).
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

OUT = ROOT / ".cache" / "exp1" / "twopool"
EVID = ROOT / "evidence" / "exp1_placement.json"


def model_dti(sel_full, rho_full):
    d = ndi.distance_transform_edt(~sel_full)
    C = np.maximum(0, 1 - d / 3.0)
    tp = float((rho_full * C).sum()); M = float(np.minimum(1, 3 * rho_full[sel_full]).sum())
    n = float(sel_full.sum()); G = float(rho_full.sum()); fp = n - M
    return dict(tp=round(tp, 2), fp=round(fp, 2), G=round(G, 2), n=int(n), dti=tp / (0.2 * tp + 0.2 * fp + 0.8 * G))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-max", type=int, default=60000)
    ap.add_argument("--cap", type=float, default=0.68)
    ap.add_argument("--trust", type=float, default=0.55)
    ap.add_argument("--rounds", type=int, default=10)
    ap.add_argument("--k-in", type=int, default=600000)
    ap.add_argument("--k-out", type=int, default=900000)
    ap.add_argument("--per-round", type=int, default=30)
    ap.add_argument("--round0-only", action="store_true",
                    help="stop after the round-0 placement and save its full registry audit rows")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    fp = L.footprint(); cat = L.catalogue(); H, W = L.SHAPE
    maps = np.load(ROOT / ".cache" / "lbm" / "lbm_v1_maps.npz")
    rho = maps["rho_full"].astype(np.float64)
    cons5 = (maps["cons_full"] >= 5)
    eligible = fp.mask & ~cat
    iso = P.isolated_value(rho)
    halo_stats = U.load_halo_stats(); shas = sorted(halo_stats)
    rep = dict(model="lbm-v1", method="two-pool capped exact greedy", cap=args.cap, trust_cons5_cap=args.trust,
               R0_model=model_dti(L.read01(L.R0) > 0, rho), rounds=[])
    print("R0 under model:", rep["R0_model"], flush=True)
    # round 0
    cand = P.candidates(rho, eligible, prefilter=800000)
    res = P.place(rho, eligible, n_max=args.n_max, cand=cand, member=cons5.ravel()[cand][:, None],
                  caps=np.array([args.trust]))
    cur = np.zeros(H * W, bool); cur[res["order"][:res["best_n"]]] = True; cur = cur.reshape(H, W)
    union_dots = np.zeros(H * W, bool)
    offender_shas: list[str] = []
    for rnd in range(args.rounds + 1):
        md = model_dti(cur, rho)
        aud = U.audit(cur, fp=fp, shas=shas, halo_stats=halo_stats)
        offenders = [r for r in aud["rows"] if r["overlap_pi1"] > 0.70 - 1e-9]
        near = [r for r in aud["rows"] if r["overlap_pi1"] > args.cap]
        rec = dict(round=rnd, n=int(cur.sum()), model=md, worst_overlap=aud["worst_overlap_pi1"],
                   worst_rho=aud["worst_abs_rho"], offenders=len(offenders), near_cap=len(near),
                   duplicate=aud["duplicate"], cons5_share=float(cons5[cur].mean()),
                   in_union_share=float(np.isin(np.flatnonzero(cur.ravel()), np.flatnonzero(union_dots)).mean())
                   if union_dots.any() else None)
        rep["rounds"].append(rec)
        print(f"round {rnd}: n={rec['n']} model DTI={md['dti']:.4f} worst overlap "
              f"{aud['worst_overlap_pi1']['overlap_pi1']:.4f} |rho| {abs(aud['worst_abs_rho']['rho']):.3f} "
              f"offenders {len(offenders)} (> cap {len(near)}) dup={aud['duplicate']} [{time.time()-t_start:.0f}s]",
              flush=True)
        np.save(OUT / f"round{rnd}_sel.npy", np.flatnonzero(cur.ravel()))
        if rnd == 0:
            (OUT / "round0_audit_rows.json").write_text(json.dumps(aud["rows"]), encoding="utf-8")
            if args.round0_only:
                break
        if not aud["duplicate"]:
            rep["final_round"] = rnd
            (OUT / "final_audit.json").write_text(json.dumps(aud, indent=1), encoding="utf-8")
            break
        if rnd == args.rounds:
            break
        # merge every raster above the cap into the union of offender dots
        added = 0
        for r in sorted(offenders, key=lambda r: -r["overlap_pi1"]):
            if added >= args.per_round:
                break
            if r["sha256"] in offender_shas:
                continue
            added += 1
            offender_shas.append(r["sha256"])
            meta, arr = rc.load_summary(r["sha256"])
            dots = arr["top"] if r["representation"] == "dot_field" else arr["top"][: int(cur.sum())]
            union_dots[fp.lin[dots]] = True
        Uhalo = ndi.distance_transform_edt(~union_dots.reshape(H, W)) <= 3.0
        inside = eligible & Uhalo
        outside = eligible & ~Uhalo
        ci = np.flatnonzero(inside.ravel()); co = np.flatnonzero(outside.ravel())
        if ci.size > args.k_in:
            ci = ci[np.argpartition(-iso[ci], args.k_in)[:args.k_in]]
        if co.size > args.k_out:
            co = co[np.argpartition(-iso[co], args.k_out)[:args.k_out]]
        cand = np.sort(np.concatenate([ci, co]))
        member = np.stack([cons5.ravel()[cand], Uhalo.ravel()[cand]], axis=1)
        print(f"   union of {len(offender_shas)} offender dot sets -> halo covers "
              f"{Uhalo[fp.mask].mean():.3f} of footprint; candidates in/out {ci.size}/{co.size}", flush=True)
        res = P.place(rho, eligible, n_max=args.n_max, cand=cand, member=member,
                      caps=np.array([args.trust, args.cap]))
        cur = np.zeros(H * W, bool); cur[res["order"][:res["best_n"]]] = True; cur = cur.reshape(H, W)
    np.save(OUT / "final_sel.npy", np.flatnonzero(cur.ravel()))
    rep["offender_shas"] = offender_shas
    rep["seconds"] = round(time.time() - t_start, 1)
    EVID.write_text(json.dumps(rep, indent=1, default=float), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
