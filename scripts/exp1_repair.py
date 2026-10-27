#!/usr/bin/env python3
"""EXP1 final step: repair the remaining registry-cap violations by adding novel dots.

Input: the hybrid round-0 selection S (union-capped placement, n=28,731).
For every raster R whose PI-1 dots contain more than ``--cap`` of S, novel dots
are added from cells outside the union halo U and outside every such halo(R),
chosen by exact marginal expected-DTI gain given the coverage of S, until every
overlap is <= ``--cap``.  The full 2,060-raster audit is then re-run; any new
violator is added to the exclusion set and the loop repeats.
"""
from __future__ import annotations

import argparse
import heapq
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

OUT = ROOT / ".cache" / "exp1" / "final"


def halo_of(lin_full, shape):
    H, W = shape
    g = np.zeros(H * W, bool); g[lin_full] = True
    return ndi.distance_transform_edt(~g.reshape(H, W)) <= 3.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default=str(ROOT / ".cache" / "exp1" / "hybrid" / "round0_sel.npy"))
    ap.add_argument("--cap", type=float, default=0.685)
    ap.add_argument("--rounds", type=int, default=6)
    ap.add_argument("--maps", default=str(ROOT / ".cache" / "lbm" / "lbm_ens_maps.npz"))
    ap.add_argument("--out", default="final_ens")
    args = ap.parse_args()
    out_dir = OUT.parent / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    fp = L.footprint(); cat = L.catalogue(); H, W = L.SHAPE
    maps = np.load(args.maps)
    rho = maps["rho_full"].astype(np.float64).ravel()
    eligible = (fp.mask & ~cat & (L.edt_to(cat) > 2.0)).ravel()
    hs = U.load_halo_stats(); shas = sorted(hs)
    S = np.zeros(H * W, bool); S[np.load(args.start)] = True
    rows0 = json.loads((ROOT / ".cache" / "exp1" / "twopool" / "round0_audit_rows.json").read_text())
    top = [r for r in sorted(rows0, key=lambda r: -r["overlap_pi1"]) if r["overlap_pi1"] > 0.70][:30]
    union_dots = np.zeros(H * W, bool)
    for r in top:
        meta, arr = rc.load_summary(r["sha256"])
        dots = arr["top"] if r["representation"] == "dot_field" else arr["top"][:41480]
        union_dots[fp.lin[dots]] = True
    excl = halo_of(np.flatnonzero(union_dots), (H, W)).ravel()
    lin_off = np.array([dy * W + dx for dy, dx, _ in P.OFFS]); k_off = np.array([k for _, _, k in P.OFFS])
    dy_off = np.array([dy for dy, _, _ in P.OFFS]); dx_off = np.array([dx for _, dx, _ in P.OFFS])
    G = float(rho.sum())
    rep = dict(method="repair by novel-dot addition", start=args.start, cap=args.cap, rounds=[])
    violators: dict[str, np.ndarray] = {}
    for rnd in range(args.rounds):
        cur = S.reshape(H, W)
        md = model_dti(cur, rho.reshape(H, W))
        md018 = model_dti(cur, maps["rho_018"].astype(np.float64)) if "rho_018" in maps.files else None
        md015 = model_dti(cur, maps["rho_015"].astype(np.float64)) if "rho_015" in maps.files else None
        aud = U.audit(cur, fp=fp, shas=shas, halo_stats=hs)
        over = [r for r in aud["rows"] if r["overlap_pi1"] > args.cap]
        rep["rounds"].append(dict(round=rnd, n=int(S.sum()), model=md, model_g018=md018, model_g015=md015, worst=aud["worst_overlap_pi1"],
                                  worst_rho=aud["worst_abs_rho"], over_cap=len(over), duplicate=aud["duplicate"]))
        print(f"round {rnd}: n={int(S.sum())} ens={md['dti']:.4f} g018={md018['dti'] if md018 else 0:.4f} g015={md015['dti'] if md015 else 0:.4f} worst {aud['worst_overlap_pi1']['overlap_pi1']:.4f} "
              f"|rho| {abs(aud['worst_abs_rho']['rho']):.3f} over-cap {len(over)} dup={aud['duplicate']} [{time.time()-t0:.0f}s]",
              flush=True)
        np.save(out_dir / f"round{rnd}_sel.npy", np.flatnonzero(S))
        if not over:
            (out_dir / "final_audit.json").write_text(json.dumps(aud, indent=1), encoding="utf-8")
            rep["final_round"] = rnd
            break
        # exclusion set grows with every violator's halo
        for r in over:
            if r["sha256"] in violators:
                continue
            meta, arr = rc.load_summary(r["sha256"])
            dots = arr["top"] if r["representation"] == "dot_field" else arr["top"][: int(S.sum())]
            h = halo_of(fp.lin[dots], (H, W)).ravel()
            violators[r["sha256"]] = h
            excl |= h
        # counts per violator for the current S
        vk = list(violators)
        counts = np.array([int((S & violators[k]).sum()) for k in vk])
        n = int(S.sum())
        need = int(np.ceil(max(0.0, (counts.max() / args.cap) - n))) + 25
        pool = np.flatnonzero(eligible & ~excl & ~S)
        print(f"   violators {len(vk)}; exclusion covers {excl.reshape(H, W)[fp.mask].mean():.3f}; pool {pool.size}; "
              f"adding ~{need} novel dots", flush=True)
        # coverage of S, then lazy greedy additions from the pool
        d = ndi.distance_transform_edt(~S.reshape(H, W)).ravel()
        C = np.maximum(0.0, 1 - d / 3.0)
        TP = float((rho * C).sum()); FP = float(n - np.minimum(1, 3 * rho[S]).sum())
        D = TP / (0.2 * TP + 0.2 * FP + 0.8 * G)
        py, px = np.divmod(pool, W)
        iso = P.isolated_value(rho.reshape(H, W), D)[pool]
        heap = [(-float(iso[i]), i) for i in range(pool.size)]
        heapq.heapify(heap)
        added = 0
        while heap and added < need:
            negv, i = heapq.heappop(heap)
            c = pool[i]
            if S[c]:
                continue
            yy = py[i] + dy_off; xx = px[i] + dx_off
            ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
            idx = c + lin_off[ok]; kk = k_off[ok]
            dTP = float(np.sum(rho[idx] * np.maximum(0.0, kk - C[idx])))
            dFP = 1.0 - min(1.0, 3.0 * rho[c])
            v = dTP * (1 - 0.2 * D) - 0.2 * D * dFP
            if heap and v < -heap[0][0] - 1e-12:
                heapq.heappush(heap, (-v, i)); continue
            S[c] = True; added += 1
            newC = np.maximum(C[idx], kk); TP += float(np.sum(rho[idx] * (newC - C[idx]))); C[idx] = newC
            FP += dFP; D = TP / (0.2 * TP + 0.2 * FP + 0.8 * G)
        print(f"   added {added}; model DTI now {D:.4f}", flush=True)
    np.save(out_dir / "final_sel.npy", np.flatnonzero(S))
    rep["violators"] = list(violators); rep["seconds"] = round(time.time() - t0, 1)
    pj = ROOT / "evidence" / "exp1_placement_hybrid_ens.json"
    place = json.loads(pj.read_text()) if pj.exists() else {}
    place.update(method="two-pool union cap (30 top offenders) + trust cap, then repair by novel-dot addition",
                 repair=rep, rounds=place.get("rounds", []) + rep["rounds"])
    (ROOT / "evidence" / "exp1_placement.json").write_text(json.dumps(place, indent=1, default=float), encoding="utf-8")
    (out_dir / "placement.json").write_text(json.dumps(place, indent=1, default=float), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
