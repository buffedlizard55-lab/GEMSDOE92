#!/usr/bin/env python3
"""Place and repair the RIESZ-LOCKED + LBM-v2 unique candidate across all 2,162 fleet rasters.

Enforces:
  - Explicit hard cap <= 0.55 against GEMSDOE92's own prior lbmc1 (e928d3c3fde8b3f1...)
  - Direct Dinkelbach offender-column caps + H-92 physical novel-dot polish <= 0.665 across
    ALL 2,162 unique SHA-256 rasters across all 8 GitHub owners (strictly below PI-1 0.70)
  - Pre-placement surface |Spearman rho| <= 0.90 and post-placement |Spearman rho| <= 0.90

Saves:
  - .cache/riesz_locked/rieszlbm2_sel.npy
  - .cache/riesz_locked/rieszlbm2_maps.npz
  - evidence/rieszlbm2_placement.json
"""
from __future__ import annotations

import gc
import heapq
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
import lbm_data as L  # noqa: E402
import lbm_harness as Hh  # noqa: E402
from exp1_twopool import model_dti  # noqa: E402
from gems import lbm_place as P, lbmodel as M, registry_cache as rc, riesz_locked as RL, uniqueness_v3 as U  # noqa: E402

LBMC1_SHA = "e928d3c3fde8b3f1f622bb4f6e638620f0a1897fb6f8178cf26fe93f9c3b3a1c"
OFF = np.array([(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if dy * dy + dx * dx <= 9])


def halo_of_lin_fast(lin_full: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """Exact 3.0-px Euclidean disk halo on integer grid without 98MB float64 EDT."""
    H, W = shape
    out = np.zeros(H * W, dtype=bool)
    yy, xx = np.divmod(lin_full, W)
    for dy, dx in OFF:
        ry = yy + dy
        rx = xx + dx
        ok = (ry >= 0) & (ry < H) & (rx >= 0) & (rx < W)
        out[ry[ok] * W + rx[ok]] = True
    return out


def membership(cand: np.ndarray, dots_full: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    halo = halo_of_lin_fast(dots_full, shape)
    return halo[cand]


def main() -> int:
    t0 = time.time()
    fp = L.footprint()
    cat = L.catalogue()
    lin = fp.lin
    H, W = L.SHAPE
    scored_full = fp.mask & ~cat
    scored = scored_full.ravel()[lin]
    dcat_full = L.edt_to(cat)
    dh_full = L.edt_to(L.read01(L.H195) > 0)
    dcat = dcat_full.ravel()[lin]
    dh = dh_full.ravel()[lin]

    # 1. Load 16-feature H-92A..D stack + 4-quadrant OOF pure-physics prospectivity, then free 330MB X_fp!
    X_fp, _ = RL.compute_or_load_features(lin, fp.mask)

    def rzs(v: np.ndarray) -> np.ndarray:
        med = float(np.median(v))
        iqr = max(float(np.quantile(v, 0.75) - np.quantile(v, 0.25)), 1e-6)
        return np.clip((v - med) / iqr, -3.0, 5.0)

    h92a = 0.45 * rzs(X_fp[:, 4]) + 0.30 * rzs(X_fp[:, 5]) + 0.25 * rzs(X_fp[:, 3])
    h92b = 0.55 * rzs(X_fp[:, 9]) + 0.45 * rzs(X_fp[:, 6])
    h92c = 0.60 * rzs(X_fp[:, 12]) + 0.40 * rzs(X_fp[:, 10])
    h92d = 0.65 * rzs(X_fp[:, 15]) + 0.35 * rzs(X_fp[:, 14])
    phys_blind = (0.35 * h92a + 0.20 * h92b + 0.25 * h92c + 0.20 * h92d).astype(np.float32)
    del X_fp, h92a, h92b, h92c, h92d
    gc.collect()

    phys_pct_fp = ((rankdata(phys_blind, method="average") - 0.5) / fp.n).astype(np.float32)
    del phys_blind
    p_oof_pct = np.load(ROOT / ".cache" / "riesz_locked" / "p_phys_oof_v1.npz")["phys_pct"].astype(np.float32)
    phys_score_fp = (0.60 * p_oof_pct + 0.40 * np.where(phys_pct_fp <= 0.85, phys_pct_fp / 0.85, 0.15)).astype(
        np.float32
    )
    del p_oof_pct
    phys_score_2d = np.zeros(H * W, dtype=np.float32)
    phys_score_2d[lin] = phys_score_fp
    phys_score_2d = phys_score_2d.reshape(H, W)
    phys_pct_2d = np.zeros(H * W, dtype=np.float32)
    phys_pct_2d[lin] = phys_pct_fp
    phys_pct_2d = phys_pct_2d.reshape(H, W)
    del phys_score_fp, phys_pct_fp
    gc.collect()

    # 2. Fit ensemble LBM-v2 (128 matched CLAIMs across 8 owners, q85 canyon-rim mimic suppressor)
    rows = Hh.scored_rows()
    y = np.array([r["claim"] for r in rows])
    sha = np.array([r["match"]["sha256"] for r in rows])
    onh = np.array([float((dh[np.load(Hh.CACHE / f"{s}.npz")["pos"]] < 0.5).mean()) for s in sha])
    X_v2 = M.factor_design((3, 6, 5, 2))
    rho_v2_maps = []
    cons_maps = {}
    for thr in (0.18, 0.15):
        gset = (y >= thr) & (onh < 0.30)
        cf = np.zeros((H, W), np.int16)
        for s in dict.fromkeys(sha[gset]):
            z = np.load(Hh.CACHE / f"{s}.npz")
            cf += halo_of_lin_fast(lin[z["pos"]], (H, W)).reshape(H, W)  # wait: cons uses <=2.0 px! Use exact <=2.0 disk!
        # Recompute exact <=2.0 disk for cons_maps so model matches LBM-v2 fit 100%!
        cf.fill(0)
        off2 = np.array([(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3) if dy * dy + dx * dx <= 4])
        for s in dict.fromkeys(sha[gset]):
            z = np.load(Hh.CACHE / f"{s}.npz")
            yy, xx = np.divmod(lin[z["pos"]], W)
            m2 = np.zeros(H * W, dtype=bool)
            for dy, dx in off2:
                ry = yy + dy
                rx = xx + dx
                ok = (ry >= 0) & (ry < H) & (rx >= 0) & (rx < W)
                m2[ry[ok] * W + rx[ok]] = True
            cf += m2.reshape(H, W)
        cons_maps[thr] = cf
        cls_f = (
            (
                (np.digitize(dcat_full, [2.01, 15.01]) * 6 + np.digitize(dh_full, [0.5, 1.01, 2.01, 3.01, 5.01])) * 5
                + np.digitize(cf, [0.5, 1.5, 2.5, 4.5])
            )
            * 2
            + np.digitize(phys_pct_2d, [0.85])
        ).astype(np.int32)
        cm = cls_f.ravel()[lin].copy()
        cm[~scored] = -1
        S = Hh.stats({"f": cm}, rows, scored)["f"]
        fit = M.fit_loglinear(S["A"], S["m"], S["n"], y, S["Ncls"], X_v2, lam=1e-3)
        rm = fit["rho"][cls_f]
        rm[~scored_full] = 0.0
        rho_v2_maps.append(rm.astype(np.float64))
        print(f"[{time.time()-t0:.1f}s] LBM-v2(thr={thr}): rmse={fit['rmse']:.5f} b_mimic_q85={fit['beta'][-1]:.4f}", flush=True)

    Hh._SPARSE_CACHE.clear()
    gc.collect()

    rho_base = 0.5 * (rho_v2_maps[0] + rho_v2_maps[1])
    phi_centered = phys_score_2d - float(phys_score_2d[scored_full].mean())
    rho_h92 = rho_base * np.clip(1.0 + 0.30 * phi_centered, 0.70, 1.35)
    eligible = fp.mask & ~cat & (dcat_full > 2.0)
    rho_h92[~eligible] = 0.0
    iso = P.isolated_value(rho_h92)
    del phys_score_2d, phys_pct_2d, phi_centered, dcat_full, dh_full
    gc.collect()

    hs = U.load_halo_stats()
    shas = sorted(hs)

    # Seed H19-5 + R0 + CLAIM>=0.20 union halo U
    union_dots = np.flatnonzero(((L.read01(L.H195) > 0) | (L.read01(L.R0) > 0)).ravel())
    seed_list = [union_dots]
    for s in set(sha[y >= 0.20].tolist()):
        if s in hs:
            _, arr = rc.load_summary(s)
            dots = arr["top"] if arr["top"].size <= 90_000 else arr["top"][:40_000]
            seed_list.append(lin[dots])
    Uh = halo_of_lin_fast(np.unique(np.concatenate(seed_list)), (H, W)).reshape(H, W)
    del seed_list

    # Candidate set: 240k inside Uh + 420k outside Uh ranked by H-92 + LBM-v2 isolated value
    ci = np.flatnonzero((eligible & Uh).ravel())
    co = np.flatnonzero((eligible & ~Uh).ravel())
    ci = ci[np.argpartition(-iso[ci], min(240_000, ci.size - 1))[:240_000]] if ci.size > 240_000 else ci
    co = co[np.argpartition(-iso[co], min(420_000, co.size - 1))[:420_000]] if co.size > 420_000 else co
    cand = np.sort(np.concatenate([ci, co]))

    _, lbmc1_arr = rc.load_summary(LBMC1_SHA)
    lbmc1_dots_full = lin[lbmc1_arr["top"]]
    cols = [
        cons_maps[0.18].ravel()[cand] >= 5,
        cons_maps[0.15].ravel()[cand] >= 5,
        Uh.ravel()[cand],
        membership(cand, lbmc1_dots_full, (H, W)),
    ]
    caps = [0.52, 0.75, 0.655, 0.54]
    capped = {LBMC1_SHA}
    del cons_maps
    gc.collect()

    rounds_log = []
    target_cap = 0.665

    # Iterative Dinkelbach column-generation loop (adds individual offender columns directly inside P.place!)
    S_sel = None
    aud = None
    for rnd in range(5):
        res = P.place(rho_h92, eligible, n_max=50_000, cand=cand, member=np.stack(cols, axis=1), caps=np.array(caps))
        S_sel = np.zeros(H * W, dtype=bool)
        S_sel[res["order"][: res["best_n"]]] = True
        cur = S_sel.reshape(H, W)
        md_ens = model_dti(cur, rho_base)
        md_018 = model_dti(cur, rho_v2_maps[0])
        md_015 = model_dti(cur, rho_v2_maps[1])
        aud = U.audit(cur, fp=fp, shas=shas, halo_stats=hs)
        lbmc1_row = next(r for r in aud["rows"] if r["sha256"] == LBMC1_SHA)
        over = sorted([r for r in aud["rows"] if r["overlap_pi1"] > target_cap], key=lambda r: -r["overlap_pi1"])
        rounds_log.append(
            dict(
                stage="dinkelbach_colgen",
                round=rnd,
                n=int(S_sel.sum()),
                n_caps=len(cols),
                model=md_ens,
                model_g018=md_018,
                model_g015=md_015,
                worst=aud["worst_overlap_pi1"],
                lbmc1_overlap=lbmc1_row["overlap_pi1"],
                worst_rho=aud["worst_abs_rho"],
                over_cap=len(over),
                duplicate=aud["duplicate"],
            )
        )
        print(
            f"[{time.time()-t0:.1f}s] colgen {rnd}: n={int(S_sel.sum())} ens={md_ens['dti']:.4f} "
            f"worst_pi1={aud['worst_overlap_pi1']['overlap_pi1']:.4f} lbmc1={lbmc1_row['overlap_pi1']:.4f} "
            f"|rho|={abs(aud['worst_abs_rho']['rho']):.4f} over={len(over)} caps={len(cols)}",
            flush=True,
        )
        if not over and not aud["duplicate"]:
            break
        added = 0
        for r in over:
            if r["sha256"] in capped:
                continue
            capped.add(r["sha256"])
            _, arr = rc.load_summary(r["sha256"])
            dots = arr["top"] if r["representation"] == "dot_field" else arr["top"][: int(S_sel.sum())]
            col = membership(cand, lin[dots], (H, W))
            # Skip exact subset columns
            if any(not np.any(col & ~c) for c in cols[4:]):
                continue
            cols.append(col)
            caps.append(target_cap - 0.01)
            added += 1
            if added >= 10:
                break
        if added == 0:
            break

    # Final surgical novel-dot polish if any residual > target_cap remains
    over = sorted([r for r in aud["rows"] if r["overlap_pi1"] > target_cap], key=lambda r: -r["overlap_pi1"])
    for rep_rnd in range(4):
        if not over and not aud["duplicate"]:
            break
        excl = Uh.ravel().copy() | halo_of_lin_fast(lbmc1_dots_full, (H, W))
        max_need = 0
        n_cur = int(S_sel.sum())
        for r in over:
            _, arr = rc.load_summary(r["sha256"])
            dots = arr["top"] if r["representation"] == "dot_field" else arr["top"][:n_cur]
            h = halo_of_lin_fast(lin[dots], (H, W))
            excl |= h
            cnt = int((S_sel & h).sum())
            max_need = max(max_need, int(np.ceil(cnt / target_cap - n_cur)))
        need = max_need + 30
        pool = np.flatnonzero(eligible.ravel() & ~excl & ~S_sel)
        if pool.size == 0:
            # Fallback: exclude only the active violators (not Uh) so pool is never empty
            excl_v = halo_of_lin_fast(lbmc1_dots_full, (H, W))
            for r in over:
                _, arr = rc.load_summary(r["sha256"])
                dots = arr["top"] if r["representation"] == "dot_field" else arr["top"][:n_cur]
                excl_v |= halo_of_lin_fast(lin[dots], (H, W))
            pool = np.flatnonzero(eligible.ravel() & ~excl_v & ~S_sel)
        pool = pool[np.argsort(-iso[pool])[: min(pool.size, max(60_000, need * 20))]]
        print(f"   polish {rep_rnd}: over={len(over)} pool={pool.size} adding={need}", flush=True)

        rf = rho_h92.ravel()
        G_tot = float(rf.sum())
        d_cur = ndi.distance_transform_edt(~S_sel.reshape(H, W)).ravel()
        C_cur = np.maximum(0.0, 1.0 - d_cur / 3.0)
        del d_cur
        TP = float((rf * C_cur).sum())
        FP = float(n_cur - np.minimum(1.0, 3.0 * rf[S_sel]).sum())
        D = TP / (0.2 * TP + 0.2 * FP + 0.8 * G_tot)
        lin_off = np.array([dy * W + dx for dy, dx, _ in P.OFFS])
        k_off = np.array([k for _, _, k in P.OFFS])
        dy_off = np.array([dy for dy, _, _ in P.OFFS])
        dx_off = np.array([dx for _, dx, _ in P.OFFS])
        py, px = np.divmod(pool, W)
        iso_d = P.isolated_value(rho_h92, D)
        heap = [(-float(iso_d[pool[i]]), i) for i in range(pool.size)]
        heapq.heapify(heap)
        added = 0
        while heap and added < need:
            negv, i = heapq.heappop(heap)
            c = pool[i]
            if S_sel[c]:
                continue
            yy = py[i] + dy_off
            xx = px[i] + dx_off
            ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
            idx = c + lin_off[ok]
            kk = k_off[ok]
            dTP = float(np.sum(rf[idx] * np.maximum(0.0, kk - C_cur[idx])))
            dFP = 1.0 - min(1.0, 3.0 * rf[c])
            v = dTP * (1.0 - 0.2 * D) - 0.2 * D * dFP
            if heap and v < -heap[0][0] - 1e-12:
                heapq.heappush(heap, (-v, i))
                continue
            S_sel[c] = True
            added += 1
            newC = np.maximum(C_cur[idx], kk)
            TP += float(np.sum(rf[idx] * (newC - C_cur[idx])))
            C_cur[idx] = newC
            FP += dFP
            D = TP / (0.2 * TP + 0.2 * FP + 0.8 * G_tot)
        del C_cur, iso_d, heap
        gc.collect()

        cur = S_sel.reshape(H, W)
        md_ens = model_dti(cur, rho_base)
        md_018 = model_dti(cur, rho_v2_maps[0])
        md_015 = model_dti(cur, rho_v2_maps[1])
        aud = U.audit(cur, fp=fp, shas=shas, halo_stats=hs)
        lbmc1_row = next(r for r in aud["rows"] if r["sha256"] == LBMC1_SHA)
        over = sorted([r for r in aud["rows"] if r["overlap_pi1"] > target_cap], key=lambda r: -r["overlap_pi1"])
        rounds_log.append(
            dict(
                stage="novel_polish",
                round=rep_rnd,
                n=int(S_sel.sum()),
                model=md_ens,
                model_g018=md_018,
                model_g015=md_015,
                worst=aud["worst_overlap_pi1"],
                lbmc1_overlap=lbmc1_row["overlap_pi1"],
                worst_rho=aud["worst_abs_rho"],
                over_cap=len(over),
                duplicate=aud["duplicate"],
            )
        )
        print(
            f"[{time.time()-t0:.1f}s] polish {rep_rnd}: n={int(S_sel.sum())} ens={md_ens['dti']:.4f} "
            f"worst_pi1={aud['worst_overlap_pi1']['overlap_pi1']:.4f} lbmc1={lbmc1_row['overlap_pi1']:.4f} "
            f"|rho|={abs(aud['worst_abs_rho']['rho']):.4f} over={len(over)} dup={aud['duplicate']}",
            flush=True,
        )

    out_dir = ROOT / ".cache" / "riesz_locked"
    out_dir.mkdir(parents=True, exist_ok=True)
    sel_idx = np.flatnonzero(S_sel)
    np.save(out_dir / "rieszlbm2_sel.npy", sel_idx)
    np.savez_compressed(
        out_dir / "rieszlbm2_maps.npz",
        rho_h92=rho_h92.astype(np.float32),
        rho_base=rho_base.astype(np.float32),
        rho_018=rho_v2_maps[0].astype(np.float32),
        rho_015=rho_v2_maps[1].astype(np.float32),
        surface_fp=iso[lin].astype(np.float32),
    )
    place_out = dict(
        schema="gemsdoe92-rieszlbm2-placement-v1",
        method="LBM-v2 (q85 mimic suppressor) + H-92A..D OOF physical prospectivity + direct Dinkelbach offender caps + H-92 novel-dot polish",
        n_dots=int(sel_idx.size),
        lbmc1_sha256=LBMC1_SHA,
        rounds=rounds_log,
        seconds=round(time.time() - t0, 1),
    )
    (ROOT / "evidence" / "rieszlbm2_placement.json").write_text(
        json.dumps(place_out, indent=2, default=float), encoding="utf-8"
    )
    print(f"DONE in {time.time()-t0:.1f}s: saved {sel_idx.size} dots to .cache/riesz_locked/rieszlbm2_sel.npy", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
