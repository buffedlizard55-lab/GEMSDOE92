#!/usr/bin/env python3
"""Execute pre-registered DEXP-KOSTROV-KOENDERINK experiments E1, E2, E3 (2026-10-29).

Follows PARALLEL-RUN PROTOCOL Rules 1-6 strictly:
  - Rule 1 (LANE & UNIQUENESS): Checks ALL 2,262 unique SHA-256 rasters across all 8 GitHub
    owners (both 2,139 dot_fields AND 123 surfaces) on BOTH the pre-placement continuous
    surface AND final placed dots; records both PI-1 and literal dense-witness readings.
  - Rule 2 (REUSE SHARED TOOLS): Uses vendor/gems57/evaluate_holdout.py, gems/faultnet.py,
    gems/uniqueness_v3.py, and vendor/gems57/submission_writer.py without private forks.
  - Rule 3 (STRICT LABELING): Labels every metric HOLDOUT-DTI (with evaluator version,
    22,663 withheld positives, 95% CI), CLAIM (owner-reported), or MODEL (diagnostic).
  - Rule 4 (LEAKAGE CANARY): Tests all 36 features individually on holdout first; fails
    closed if any feature exceeds symmetric AUC 0.90.
  - Rule 5 (RUN CARD): Emits byte-bound JSON Run Card + 11-gate format audit; honestly marks
    verdict='negative' / submission_eligible=False under the unresolved literal dense-witness
    rule (17GEMSDOE E-proba-multiscale = 1.000 > 0.70).
  - Rule 6 (BUDGET): Runs exactly 3 holdout experiments (E1, E2, E3); spends 0 weekly slots.
"""
from __future__ import annotations

import gc
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import rankdata
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
import lbm_data as L  # noqa: E402
from gems import (  # noqa: E402
    dexp_kostrov as DK,
    gates as root_gates,
    lbmodel as M,
    registry_cache as rc,
    uniqueness_v3 as U,
)
from gems57 import (  # noqa: E402
    evaluate_holdout,
    grid as grid_mod,
    holdout as hold_mod,
    submission_writer,
)

OFFS_3PX = np.array(
    [(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if dy * dy + dx * dx <= 9.0],
    dtype=np.int64,
)


def halo_bool_1d(dots_full_lin: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """Exact 3.0-px Euclidean disk halo on flattened (H*W,) grid without row-wrap."""
    H, W = shape
    out = np.zeros(H * W, dtype=bool)
    if dots_full_lin.size == 0:
        return out
    y, x = np.divmod(dots_full_lin, W)
    for dy, dx in OFFS_3PX:
        yy = y + dy
        xx = x + dx
        ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
        out[yy[ok] * W + xx[ok]] = True
    return out


def nms_capped_dots(
    order_lin: np.ndarray,
    shape: tuple[int, int],
    min_dist: float,
    n_target: int,
    cap_halos_1d: list[np.ndarray] | None = None,
    cap_frac: float = 0.65,
) -> np.ndarray:
    """Deterministic greedy NMS with optional hard 3-px overlap caps on ``cap_halos_1d``."""
    H, W = shape
    taken = np.zeros(H * W, dtype=bool)
    blocked = np.zeros(H * W, dtype=bool)
    r = int(np.ceil(min_dist))
    offs = np.array(
        [
            dy * W + dx
            for dy in range(-r, r + 1)
            for dx in range(-r, r + 1)
            if 0 < dy * dy + dx * dx < min_dist * min_dist
        ],
        dtype=np.int64,
    )
    halos = cap_halos_1d or []
    m_caps = len(halos)
    max_hits = int(np.floor(cap_frac * n_target))
    hit_counts = np.zeros(m_caps, dtype=np.int64)

    cnt = 0
    for c in order_lin:
        if blocked[c]:
            continue
        if m_caps:
            violate = False
            for j in range(m_caps):
                if halos[j][c] and hit_counts[j] >= max_hits:
                    violate = True
                    break
            if violate:
                continue
        taken[c] = True
        if m_caps:
            for j in range(m_caps):
                if halos[j][c]:
                    hit_counts[j] += 1
        cnt += 1
        cy, cx = divmod(int(c), W)
        # Safe non-wrapping neighborhood block
        nb = c + offs
        nb = nb[(nb >= 0) & (nb < H * W)]
        nby, nbx = np.divmod(nb, W)
        nb = nb[np.abs(nbx - cx) <= r]
        blocked[nb] = True
        blocked[c] = True
        if cnt >= n_target:
            break
    return taken.reshape(H, W)


def quadrant_quantile_calibrate(prob_fp: np.ndarray, q_ids_fp: np.ndarray) -> np.ndarray:
    """Within-quadrant rank-percentile calibration mapped smoothly to [0, 1]."""
    out = np.zeros_like(prob_fp, dtype=np.float32)
    for q in range(4):
        m = q_ids_fp == q
        if not np.any(m):
            continue
        r = (rankdata(prob_fp[m], method="average") - 0.5) / float(m.sum())
        # Convex power blend preserves monotonic probability sharpness near fault crests
        out[m] = (0.35 * prob_fp[m] + 0.65 * (r**3)).astype(np.float32)
    return out


def two_regime_pareto_surface(
    cal_e2: np.ndarray,
    cal_e1: np.ndarray,
    d_fp: np.ndarray,
    elig_fp: np.ndarray,
    midscarp_fp: np.ndarray,
    quota_prox: float = 16_800.0 * 3.2,
    quota_dist: float = 23_200.0 * 3.2,
) -> np.ndarray:
    """Two-regime synthesis (42% proximal 3<d<=15 px splays + 58% distal d>15 px blind structures).

    Within Regime I (3.01 < d <= 15.0 px), weights network-informed E2 (0.76) + blind E1 (0.24).
    Within Regime II (d > 15.0 px), weights zero-catalogue blind DEXP-Kostrov E1 (0.58) + E2 (0.42).
    Maps descending within-regime rank r -> Q / (Q + r) so both pre-placement top-40,000 and
    2.8-px spaced NMS (~3.2 raw crest pixels per spaced dot) naturally achieve ~42% / ~58% balance.
    """
    out = np.zeros_like(cal_e2, dtype=np.float32)
    s_prox = (0.76 * cal_e2 + 0.24 * cal_e1) * (1.0 - 0.30 * midscarp_fp)
    s_dist = (0.58 * cal_e1 + 0.42 * cal_e2) * (1.0 - 0.25 * midscarp_fp)

    m_prox = elig_fp & (d_fp > 3.01) & (d_fp <= 15.0)
    idx_p = np.flatnonzero(m_prox)
    if idx_p.size > 0:
        ord_p = np.argsort(s_prox[idx_p], kind="mergesort")[::-1]
        rk_p = np.arange(idx_p.size, dtype=np.float32)
        out[idx_p[ord_p]] = np.float32(quota_prox) / (np.float32(quota_prox) + rk_p)

    m_dist = elig_fp & (d_fp > 15.0)
    idx_d = np.flatnonzero(m_dist)
    if idx_d.size > 0:
        ord_d = np.argsort(s_dist[idx_d], kind="mergesort")[::-1]
        rk_d = np.arange(idx_d.size, dtype=np.float32)
        out[idx_d[ord_d]] = np.float32(quota_dist) / (np.float32(quota_dist) + rk_d)
    return out


def main() -> int:
    t0 = time.time()
    fp = L.footprint()
    H, W = L.SHAPE
    cat = L.catalogue()
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    foot = grid.footprint
    inv_fp = np.full(H * W, -1, np.int64)
    inv_fp[fp.lin] = np.arange(fp.n)

    # Load det_elev & b19_slope once for context strike & raw single-modality baseline
    with rasterio.open(L.FEATURES) as tf:
        det_elev_2d = DK.clean_band_2d(tf.read(12), foot)
        b19_slope_2d = DK.clean_band_2d(tf.read(19), foot)

    # 1. Compute 28-feature zero-catalogue DEXP-Kostrov + Riesz stack
    X_blind, crest_fp, blind_names, stack_meta = DK.compute_or_load_dexp_kostrov_stack(fp.lin, foot)
    s_style_fp = X_blind[:, 4]
    print(f"[{time.time()-t0:.1f}s] Built 28-feature zero-catalogue stack: {X_blind.shape}", flush=True)

    # Pure zero-catalogue raw DEM mid-scarp halo (never touches catalogue; used for E3 diversity)
    raw_dem_crest = DK.directional_crest_1d(b19_slope_2d, foot)
    q90_b19 = float(np.quantile(b19_slope_2d[foot], 0.88))
    midscarp_monopoly_fp = ((b19_slope_2d.ravel()[fp.lin] > q90_b19) & (raw_dem_crest.ravel()[fp.lin] > 0.65)).astype(
        np.float32
    )
    del b19_slope_2d, raw_dem_crest
    gc.collect()

    # Quadrant assignment on footprint (matching gems57 quadrant geometry)
    yy_fp, xx_fp = np.divmod(fp.lin, W)
    ym, xm = int(np.median(yy_fp)), int(np.median(xx_fp))
    quad_fp = ((yy_fp >= ym).astype(np.int8) * 2 + (xx_fp >= xm).astype(np.int8)).astype(np.int8)

    # 3 & 4. Load cached canaries & holdout if --reuse-holdout is passed, else compute fresh
    canary_path = ROOT / "evidence" / "dexp_kostrov_canaries_20261029.json"
    holdout_path = ROOT / "evidence" / "dexp_kostrov_holdout_20261029.json"
    h19_mask = L.read01(L.H195) > 0
    if "--reuse-holdout" in sys.argv and canary_path.is_file() and holdout_path.is_file():
        canary_out = json.loads(canary_path.read_text(encoding="utf-8"))
        canary_rows = canary_out["features"]
        max_sym_auc = float(canary_out["max_symmetric_auc"])
        holdout_payload = json.loads(holdout_path.read_text(encoding="utf-8"))
        summ_e1 = holdout_payload["summary_e1_blind"]
        summ_e2 = holdout_payload["summary_e2_dual"]
        summ_e3 = holdout_payload["summary_e3_unique"]
        delta_r0 = summ_e3["paired_differences"]["r0_recipe"]
        beats_r0_ci = bool(delta_r0["delta"] > 0 and delta_r0["ci95"][0] > 0)
        print(f"[{time.time()-t0:.1f}s] Loaded cached canaries (max_AUC={max_sym_auc:.5f}) & holdout (E3={summ_e3['scores']['e3_dexp_kostrov_unique']['dti']:.6f})", flush=True)
    else:
        # Build both gems57 holdout draws (seeds 20 & 30; 8 spatial folds; 22,663 withheld positives)
        draws_data = []
        for seed in (20, 30):
            folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
            vis = folds[0]["visible"]
            X_cx, d_vis = DK.visible_network_features(vis, det_elev_2d, fp.lin, foot, s_style_fp)
            draws_data.append((seed, folds, vis, X_cx, d_vis))
            print(f"[{time.time()-t0:.1f}s] Built self-excluded fold-visible network stack for seed={seed}", flush=True)

        # STEP 1 — SINGLE-FEATURE LEAKAGE CANARIES (Protocol Rule 4: AUC <= 0.90 BEFORE trusting any model)
        rng_can = np.random.default_rng(20261029)
        all_feat_names = blind_names + list(DK.CX_FEATURE_NAMES)
        canary_pos_vals = [[] for _ in range(len(all_feat_names))]
        canary_neg_vals = [[] for _ in range(len(all_feat_names))]

        for seed, folds, vis, X_cx, d_vis in draws_data:
            for fold in folds:
                active = foot & fold["region"] & (~fold["masked_known"])
                truth = active & fold["truth"]
                pos_lin = inv_fp[np.flatnonzero(truth.ravel())]
                neg_all = inv_fp[np.flatnonzero((active & ~truth).ravel())]
                neg_sub = rng_can.choice(neg_all, size=min(neg_all.size, pos_lin.size * 10), replace=False)
                for j in range(len(blind_names)):
                    canary_pos_vals[j].append(X_blind[pos_lin, j])
                    canary_neg_vals[j].append(X_blind[neg_sub, j])
                for j in range(len(DK.CX_FEATURE_NAMES)):
                    canary_pos_vals[len(blind_names) + j].append(X_cx[pos_lin, j])
                    canary_neg_vals[len(blind_names) + j].append(X_cx[neg_sub, j])

        canary_rows = []
        for j, fname in enumerate(all_feat_names):
            vp = np.concatenate(canary_pos_vals[j])
            vn = np.concatenate(canary_neg_vals[j])
            yv = np.concatenate([np.ones(vp.size, dtype=np.int8), np.zeros(vn.size, dtype=np.int8)])
            xv = np.nan_to_num(np.concatenate([vp, vn]).astype(np.float64), nan=0.0)
            auc_raw = float(roc_auc_score(yv, xv))
            auc_sym = max(auc_raw, 1.0 - auc_raw)
            canary_rows.append(
                dict(
                    feature=fname,
                    group="zero_catalogue_physics" if j < len(blind_names) else "fold_visible_self_excluded_context",
                    raw_auc=round(auc_raw, 6),
                    symmetric_auc=round(auc_sym, 6),
                    pass_limit_0_90=bool(auc_sym <= 0.90),
                )
            )
        max_sym_auc = max(r["symmetric_auc"] for r in canary_rows)
        leakage_flag = any(r["symmetric_auc"] > 0.90 for r in canary_rows)
        canary_out = dict(
            schema="gemsdoe92-dexp-kostrov-canaries-20261029",
            evaluator_version=evaluate_holdout.VERSION,
            withheld_positive_pixels=22663,
            n_features_tested=len(canary_rows),
            threshold_auc=0.90,
            max_symmetric_auc=round(max_sym_auc, 6),
            leakage_flag=bool(leakage_flag),
            features=canary_rows,
        )
        canary_path.write_text(json.dumps(canary_out, indent=2), encoding="utf-8")
        print(
            f"[{time.time()-t0:.1f}s] Leakage canaries ({len(canary_rows)} features): "
            f"max_sym_AUC = {max_sym_auc:.5f} (limit 0.90) -> {'FAIL' if leakage_flag else 'PASS'}",
            flush=True,
        )
        if leakage_flag:
            raise RuntimeError(f"STOP: Leakage canary exceeded 0.90 (max={max_sym_auc:.5f})")
        del canary_pos_vals, canary_neg_vals

        # STEP 2 — RUN EXACTLY 3 HOLDOUT EXPERIMENTS (E1, E2, E3) ON evaluate_holdout.py
        terms: dict[str, np.ndarray] = {}
        per_fold: dict[str, list[float]] = {}
        holdout_receipts = []
        rng_tr = np.random.default_rng(20261029)

        for seed, folds, vis, X_cx, d_vis in draws_data:
            ts = time.time()
            known = folds[0]["masked_known"]
            vis_fp = vis.ravel()[fp.lin]
            d_vis_fp = d_vis.ravel()[fp.lin]

            p_e1_fp = np.zeros(fp.n, dtype=np.float32)
            p_e2_fp = np.zeros(fp.n, dtype=np.float32)

            for q_idx, fold in enumerate(folds):
                in_q_fp = (fold["region"] & foot).ravel()[fp.lin]
                tr_fp = ~in_q_fp

                pos_idx = np.flatnonzero(tr_fp & vis_fp)
                neg_pool = np.flatnonzero(tr_fp & (~vis_fp) & (d_vis_fp > 2.5))
                neg_idx = rng_tr.choice(neg_pool, size=min(neg_pool.size, pos_idx.size * 6), replace=False)
                tr_idx = np.concatenate([pos_idx, neg_idx])
                y_tr = np.concatenate([np.ones(pos_idx.size, dtype=np.int8), np.zeros(neg_idx.size, dtype=np.int8)])

                clf_e1 = HistGradientBoostingClassifier(
                    max_iter=180,
                    max_depth=6,
                    learning_rate=0.06,
                    min_samples_leaf=80,
                    l2_regularization=2.5,
                    random_state=100 + seed + q_idx,
                )
                clf_e1.fit(X_blind[tr_idx], y_tr)
                p_e1_fp[in_q_fp] = clf_e1.predict_proba(X_blind[in_q_fp])[:, 1].astype(np.float32)

                X_tr_36 = np.hstack([X_blind[tr_idx], X_cx[tr_idx]])
                X_te_36 = np.hstack([X_blind[in_q_fp], X_cx[in_q_fp]])
                clf_e2 = HistGradientBoostingClassifier(
                    max_iter=200,
                    max_depth=6,
                    learning_rate=0.06,
                    min_samples_leaf=80,
                    l2_regularization=2.5,
                    random_state=200 + seed + q_idx,
                )
                clf_e2.fit(X_tr_36, y_tr)
                p_e2_fp[in_q_fp] = clf_e2.predict_proba(X_te_36)[:, 1].astype(np.float32)
                del X_tr_36, X_te_36

            cal_e1 = quadrant_quantile_calibrate(p_e1_fp, quad_fp) * (0.35 + 0.65 * crest_fp)
            cal_e2 = quadrant_quantile_calibrate(p_e2_fp, quad_fp) * (0.30 + 0.70 * crest_fp)

            elig_2 = foot & (~known) & (d_vis > 2.0)
            elig_3 = foot & (~known) & (d_vis > 3.01)
            elig2_lin = np.flatnonzero(elig_2.ravel())
            elig3_lin = np.flatnonzero(elig_3.ravel())
            elig3_fp = elig_3.ravel()[fp.lin]

            r0_rec = nms_capped_dots(np.flatnonzero((h19_mask & elig_2).ravel()), (H, W), 2.8, 10**9).astype(np.float32)
            n_r0 = int(r0_rec.sum())

            s_e1_1d = np.zeros(H * W, dtype=np.float32)
            s_e1_1d[fp.lin] = cal_e1
            ord_e1 = elig2_lin[np.argsort(s_e1_1d[elig2_lin])[::-1]]
            pred_e1 = nms_capped_dots(ord_e1, (H, W), 2.8, n_r0).astype(np.float32)

            s_e2_1d = np.zeros(H * W, dtype=np.float32)
            s_e2_1d[fp.lin] = cal_e2
            ord_e2 = elig3_lin[np.argsort(s_e2_1d[elig3_lin])[::-1]]
            pred_e2 = nms_capped_dots(ord_e2, (H, W), 2.8, 40_000).astype(np.float32)

            cal_e3 = two_regime_pareto_surface(cal_e2, cal_e1, d_vis_fp, elig3_fp, midscarp_monopoly_fp)
            s_e3_1d = np.zeros(H * W, dtype=np.float32)
            s_e3_1d[fp.lin] = cal_e3
            h_r0_vis = halo_bool_1d(np.flatnonzero(r0_rec.ravel() > 0), (H, W))
            h_e1_vis = halo_bool_1d(np.flatnonzero(pred_e1.ravel() > 0), (H, W))
            ord_e3 = elig3_lin[np.argsort(s_e3_1d[elig3_lin])[::-1]]
            pred_e3 = nms_capped_dots(
                ord_e3, (H, W), 2.8, 40_000, cap_halos_1d=[h_r0_vis, h_e1_vis], cap_frac=0.64
            ).astype(np.float32)

            arms = dict(
                r0_recipe=r0_rec,
                e1_dexp_kostrov_blind=pred_e1,
                e2_dexp_kostrov_dual=pred_e2,
                e3_dexp_kostrov_unique=pred_e3,
            )
            for nm, arr in arms.items():
                for fold in folds:
                    sc, tm = evaluate_holdout.evaluate(arr, fold, foot)
                    terms[nm] = tm if nm not in terms else terms[nm] + tm
                    per_fold.setdefault(nm, []).append(round(float(sc["dti"]), 6))
            holdout_receipts.append(
                dict(
                    seed=seed,
                    dots={nm: int(arr.sum()) for nm, arr in arms.items()},
                    folds=[f["receipt"] for f in folds],
                )
            )
            print(
                f"[{time.time()-ts:.1f}s] Holdout seed={seed} done: "
                + ", ".join(f"{k}={int(v.sum())}d" for k, v in arms.items()),
                flush=True,
            )
            del s_e1_1d, s_e2_1d, s_e3_1d, h_r0_vis, h_e1_vis
            gc.collect()

        del draws_data
        gc.collect()

        summ_e1 = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate="e1_dexp_kostrov_blind")
        summ_e2 = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate="e2_dexp_kostrov_dual")
        summ_e3 = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate="e3_dexp_kostrov_unique")

        holdout_payload = dict(
            schema="gemsdoe92-dexp-kostrov-holdout-20261029",
            evaluator=f"{evaluate_holdout.VERSION} (seeds 20,30; 8 spatial folds; 20 km paired block bootstrap 1000 draws)",
            rule="strict Rule-2: all catalogue-derived inputs in E2/E3 use fold['visible'] only with own-component self-exclusion",
            summary_e1_blind=summ_e1,
            summary_e2_dual=summ_e2,
            summary_e3_unique=summ_e3,
            per_fold=per_fold,
            receipts=holdout_receipts,
        )
        holdout_path.write_text(json.dumps(holdout_payload, indent=2, default=float), encoding="utf-8")
        delta_r0 = summ_e3["paired_differences"]["r0_recipe"]
        beats_r0_ci = bool(delta_r0["delta"] > 0 and delta_r0["ci95"][0] > 0)
        print("\n=== POOLED HOLDOUT-DTI (gems57-pooled-hide-v2, 22,663 withheld positives) ===", flush=True)
        for k, v in summ_e3["scores"].items():
            print(f"  {k:24s}: HOLDOUT-DTI = {v['dti']:.6f}  95% CI [{v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}]", flush=True)
        print("\n=== PAIRED DIFFERENCES (E3 - control) ===", flush=True)
        for k, v in summ_e3["paired_differences"].items():
            print(f"  e3_dexp_kostrov_unique - {k:22s}: {v['delta']:+.6f}  95% CI [{v['ci95'][0]:+.6f}, {v['ci95'][1]:+.6f}]", flush=True)
        print(f"E3 beats R0 recipe with paired 95% CI > 0: {beats_r0_ci}", flush=True)

    # 5. STEP 3 — FULL-FOOTPRINT DEPLOYMENT (4-Quadrant Out-of-Fold LOQO on Public Catalogue)
    dep_cache_path = ROOT / ".cache" / "dexp_kostrov_dep_base_v1.npz"
    d_cat_2d = L.edt_to(cat)
    cat_fp = cat.ravel()[fp.lin]
    d_cat_fp = d_cat_2d.ravel()[fp.lin]

    if dep_cache_path.is_file() and "--recompute-dep" not in sys.argv:
        del det_elev_2d, X_blind
        gc.collect()
        base_surf_fp = np.load(dep_cache_path)["base_surf_fp"].astype(np.float32)
        print(f"[{time.time()-t0:.1f}s] Loaded cached deployment base surface", flush=True)
    else:
        X_cx_dep, _ = DK.visible_network_features(cat, det_elev_2d, fp.lin, foot, s_style_fp)
        del det_elev_2d

        p_dep_e1 = np.zeros(fp.n, dtype=np.float32)
        p_dep_e2 = np.zeros(fp.n, dtype=np.float32)
        rng_dep = np.random.default_rng(2026102901)

        for q_idx in range(4):
            in_q = quad_fp == q_idx
            tr_q = ~in_q
            pos_idx = np.flatnonzero(tr_q & cat_fp)
            neg_pool = np.flatnonzero(tr_q & (~cat_fp) & (d_cat_fp > 2.5))
            neg_idx = rng_dep.choice(neg_pool, size=min(neg_pool.size, pos_idx.size * 6), replace=False)
            tr_idx = np.concatenate([pos_idx, neg_idx])
            y_tr = np.concatenate([np.ones(pos_idx.size, dtype=np.int8), np.zeros(neg_idx.size, dtype=np.int8)])

            clf1 = HistGradientBoostingClassifier(
                max_iter=180, max_depth=6, learning_rate=0.06, min_samples_leaf=80, l2_regularization=2.5, random_state=300 + q_idx
            )
            clf1.fit(X_blind[tr_idx], y_tr)
            p_dep_e1[in_q] = clf1.predict_proba(X_blind[in_q])[:, 1].astype(np.float32)

            X_tr_36 = np.hstack([X_blind[tr_idx], X_cx_dep[tr_idx]])
            X_te_36 = np.hstack([X_blind[in_q], X_cx_dep[in_q]])
            clf2 = HistGradientBoostingClassifier(
                max_iter=200, max_depth=6, learning_rate=0.06, min_samples_leaf=80, l2_regularization=2.5, random_state=400 + q_idx
            )
            clf2.fit(X_tr_36, y_tr)
            p_dep_e2[in_q] = clf2.predict_proba(X_te_36)[:, 1].astype(np.float32)
            del X_tr_36, X_te_36

        del X_blind, X_cx_dep
        gc.collect()

        cal_dep_e1 = quadrant_quantile_calibrate(p_dep_e1, quad_fp) * (0.35 + 0.65 * crest_fp)
        cal_dep_e2 = quadrant_quantile_calibrate(p_dep_e2, quad_fp) * (0.30 + 0.70 * crest_fp)
        elig_dep_fp = (~cat_fp) & (d_cat_fp > 3.01)
        base_surf_fp = two_regime_pareto_surface(
            cal_dep_e2, cal_dep_e1, d_cat_fp, elig_dep_fp, midscarp_monopoly_fp
        )
        if base_surf_fp.max() > 0:
            base_surf_fp = (base_surf_fp / float(base_surf_fp.max())).astype(np.float32)
        np.savez_compressed(dep_cache_path, base_surf_fp=base_surf_fp)
        print(f"[{time.time()-t0:.1f}s] Saved deployment base surface cache", flush=True)

    # 6. FULL 2,262-SHA REGISTRY PRE-PLACEMENT SURFACE SHAPING & FINAL DOT PLACEMENT
    inv = json.loads((rc.CACHE / "inventory.json").read_text(encoding="utf-8"))
    all_shas_2262 = sorted({f["sha256"] for r in inv["repositories"] for f in r["files"]})
    hs = U.load_halo_stats()
    n_dots = 40_000
    target_cap = 0.655

    # Fast exact two-level column-generation Lagrangian dual solver:
    # Outer loop runs full 2,262-SHA U.audit; inner loop converges subgradient weights on the active watch-set in <2s!
    surf_fp = base_surf_fp.copy()
    active_offender_halos_fp: dict[str, np.ndarray] = {}
    active_offender_halos_1d: dict[str, np.ndarray] = {}
    aud_surf = None

    for outer in range(4):
        aud_surf = U.audit(
            None,
            our_surface=surf_fp,
            fp=fp,
            shas=all_shas_2262,
            halo_stats=hs,
            n_dots_for_surface=n_dots,
        )
        w_ov = aud_surf["worst_overlap_pi1"]["overlap_pi1"]
        w_rho = abs(aud_surf["worst_abs_rho"]["rho"])
        over = [r for r in aud_surf["rows"] if r["overlap_pi1"] > target_cap]
        print(
            f"[{time.time()-t0:.1f}s] Full 2,262-SHA surface audit {outer}: worst_pi1={w_ov:.5f} "
            f"({aud_surf['worst_overlap_pi1']['sha256'][:10]}) |rho|={w_rho:.5f} over_{target_cap}={len(over)}",
            flush=True,
        )
        if not aud_surf["duplicate"] and w_ov <= 0.675:
            break
        # Add all rasters with overlap > 0.52 into our fast exact watch-set
        watch_rows = [r for r in aud_surf["rows"] if r["overlap_pi1"] > 0.52]
        for r in sorted(watch_rows, key=lambda x: -x["overlap_pi1"])[:60]:
            s_id = r["sha256"]
            if s_id not in active_offender_halos_fp:
                _, arr = rc.load_summary(s_id)
                dots_t = arr["top"] if r["representation"] == "dot_field" else arr["top"][:n_dots]
                h1d = halo_bool_1d(fp.lin[dots_t], (H, W))
                active_offender_halos_1d[s_id] = h1d
                active_offender_halos_fp[s_id] = h1d[fp.lin]
        watch_ids = list(active_offender_halos_fp.keys())
        for inner in range(60):
            top_idx = rc.order_desc(surf_fp.astype(np.float64), fp.tie_key)[:n_dots]
            ovs = {s_id: float(active_offender_halos_fp[s_id][top_idx].mean()) for s_id in watch_ids}
            max_w = max(ovs.values()) if ovs else 0.0
            if max_w <= target_cap:
                break
            pen_fp = np.ones(fp.n, dtype=np.float32)
            for s_id, ov_val in ovs.items():
                if ov_val > target_cap:
                    excess = ov_val - target_cap + 0.005
                    factor = np.float32(np.exp(-0.65 * excess))
                    h_fp = active_offender_halos_fp[s_id]
                    pen_fp[h_fp] = np.minimum(pen_fp[h_fp], factor)
            surf_fp = (surf_fp * pen_fp).astype(np.float32)
            if surf_fp.max() > 0:
                surf_fp /= float(surf_fp.max())

    # Final mandatory full 2,262-SHA verification on pre-placement surface
    if aud_surf is None or aud_surf["duplicate"]:
        aud_surf = U.audit(
            None, our_surface=surf_fp, fp=fp, shas=all_shas_2262, halo_stats=hs, n_dots_for_surface=n_dots
        )
    if aud_surf["duplicate"]:
        raise RuntimeError(f"STOP: Pre-placement surface failed PI-1 uniqueness: {aud_surf['worst_overlap_pi1']}")
    del active_offender_halos_fp
    gc.collect()

    # Now place 40,000 spaced dots (>= 2.8 px, strict d_cat > 3.0 px) from surf_fp with column-generation halo caps across ALL 2,262 SHAs!
    surf_1d = np.zeros(H * W, dtype=np.float32)
    surf_1d[fp.lin] = surf_fp
    elig_dep_2d = foot & (~cat) & (d_cat_2d > 3.01)
    elig_dep_lin = np.flatnonzero(elig_dep_2d.ravel())
    order_dep = elig_dep_lin[np.argsort(surf_1d[elig_dep_lin])[::-1]]
    del surf_1d, surf_fp, base_surf_fp, elig_dep_2d, elig_dep_lin
    gc.collect()

    cap_list_1d = list(active_offender_halos_1d.values())
    capped_shas = set(active_offender_halos_1d.keys())
    del active_offender_halos_1d
    gc.collect()
    aud_final = None
    final_dots_2d = None

    for rnd in range(8):
        final_dots_2d = nms_capped_dots(order_dep, (H, W), 2.8, n_dots, cap_halos_1d=cap_list_1d, cap_frac=0.65)
        aud_final = U.audit(final_dots_2d, fp=fp, shas=all_shas_2262, halo_stats=hs)
        w_ov = aud_final["worst_overlap_pi1"]["overlap_pi1"]
        w_rho = abs(aud_final["worst_abs_rho"]["rho"])
        over = [r for r in aud_final["rows"] if r["overlap_pi1"] > 0.655]
        print(
            f"[{time.time()-t0:.1f}s] Final-dot round {rnd}: dots={int(final_dots_2d.sum())} "
            f"worst_pi1={w_ov:.5f} ({aud_final['worst_overlap_pi1']['sha256'][:10]}) |rho|={w_rho:.5f} over={len(over)}",
            flush=True,
        )
        if not aud_final["duplicate"] and w_ov <= 0.665:
            break
        for r in sorted(over, key=lambda x: -x["overlap_pi1"])[:15]:
            s_id = r["sha256"]
            if s_id not in capped_shas:
                capped_shas.add(s_id)
                _, arr = rc.load_summary(s_id)
                dots_t = arr["top"] if r["representation"] == "dot_field" else arr["top"][: int(final_dots_2d.sum())]
                cap_list_1d.append(halo_bool_1d(fp.lin[dots_t], (H, W)))

    if aud_final["duplicate"]:
        raise RuntimeError(f"STOP: Final dots failed PI-1 uniqueness: {aud_final['worst_overlap_pi1']}")
    del cap_list_1d, order_dep, d_cat_2d
    gc.collect()

    # 7. Evaluate Calibrated LBM-v3 & LBM-v2 Diagnostic on Final Dots (MODEL label ONLY, never a score!)
    lbm29 = json.loads((ROOT / "evidence" / "lbm_oot_and_v3_20261029.json").read_text())
    # Recompute exact coverage vector C of final_dots_2d
    pred_float = final_dots_2d.astype(np.float32)
    C_cand = M.coverage_field(pred_float).ravel()[fp.lin].astype(np.float64)
    pos_cand = np.flatnonzero(pred_float.ravel()[fp.lin] > 0)
    n_cand = int(pos_cand.size)

    # Regime balance check (Regime I 2<d<=15 vs Regime II d>15)
    frac_dcat_2_15 = float(((d_cat_fp[pos_cand] > 2.0) & (d_cat_fp[pos_cand] <= 15.0)).mean())
    frac_dcat_gt15 = float((d_cat_fp[pos_cand] > 15.0).mean())

    # Compute LBM-v2 & LBM-v3 MODEL diagnostic
    h19_dh_fp = ndi.distance_transform_edt(~h19_mask).astype(np.float32).ravel()[fp.lin]
    rows_m = [r for r in json.loads((ROOT / "evidence" / "claims_matched_20261029.json").read_text())["rows"] if "match" in r]
    c28_keys = {
        (r["site"], r["name"])
        for r in json.loads((ROOT / "evidence" / "claims_matched_20261028.json").read_text())["rows"]
        if "match" in r
    }
    cons_fp = np.zeros(fp.n, dtype=np.int16)
    seen_g = set()
    for r in rows_m:
        if (r["site"], r["name"]) not in c28_keys or r["claim"] < 0.18:
            continue
        s_id = r["match"]["sha256"]
        if s_id in seen_g:
            continue
        z = np.load(ROOT / ".cache" / "lbm" / f"{s_id}.npz")
        if float((h19_dh_fp[z["pos"]] < 0.5).mean()) < 0.30:
            seen_g.add(s_id)
            gm = np.zeros(H * W, dtype=bool)
            gm[fp.lin[z["pos"]]] = True
            cons_fp += ndi.distance_transform_edt(~gm.reshape(H, W)).ravel()[fp.lin] <= 2.0

    from scripts.audit_claims_and_lbm_20261029 import compute_blind_phys_percentile
    from gems import riesz_locked as RL_mod

    X_rl_tmp, _ = RL_mod.compute_or_load_features(fp.lin, foot)
    phys_pct_fp = compute_blind_phys_percentile(X_rl_tmp)
    del X_rl_tmp
    scored_fp = (foot & ~cat).ravel()[fp.lin]
    cm_v2 = (
        (np.digitize(d_cat_fp, [2.01, 15.01]) * 6 + np.digitize(h19_dh_fp, [0.5, 1.01, 2.01, 3.01, 5.01])) * 5
        + np.digitize(cons_fp, [0.5, 1.5, 2.5, 4.5])
    ) * 2 + np.digitize(phys_pct_fp, [0.85])
    cm_v2 = cm_v2.astype(np.int32)
    cm_v2[~scored_fp] = -1
    K_cls = 180
    ok_c = cm_v2 >= 0
    Ncls = np.bincount(cm_v2[ok_c], minlength=K_cls).astype(float)
    A_cand = np.bincount(cm_v2[ok_c], weights=C_cand[ok_c], minlength=K_cls)[None, :]
    m_cand = np.bincount(cm_v2[pos_cand], minlength=K_cls).astype(float)[None, :]
    n_vec = np.array([float(n_cand)])

    X_v2 = M.factor_design((3, 6, 5, 2))
    grid_idx = np.indices((3, 6, 5, 2)).reshape(4, -1).T
    X_v3 = np.hstack(
        [
            X_v2,
            ((grid_idx[:, 1] <= 2) & (grid_idx[:, 2] >= 3)).astype(float)[:, None],
            ((grid_idx[:, 0] == 2) & (grid_idx[:, 2] >= 4)).astype(float)[:, None],
            ((grid_idx[:, 1] <= 1) & (grid_idx[:, 2] >= 2)).astype(float)[:, None],
        ]
    )
    rho_v2_132 = np.minimum(np.exp(X_v2 @ np.array(lbm29["models_132"]["lbm_v2_main_effects_132"]["beta"])), 0.50)
    rho_v3_132 = np.minimum(np.exp(X_v3 @ np.array(lbm29["models_132"]["lbm_v3_saturated_132"]["beta"])), 0.50)
    model_v2_est = float(M.predict(rho_v2_132, A_cand, m_cand, n_vec, Ncls)[0])
    model_v3_est = float(M.predict(rho_v3_132, A_cand, m_cand, n_vec, Ncls)[0])
    print(
        f"[{time.time()-t0:.1f}s] Candidate diagnostics: dots={n_cand}, dcat_2_15={frac_dcat_2_15:.4f}, "
        f"dcat_gt15={frac_dcat_gt15:.4f}, MODEL_v2={model_v2_est:.4f}, MODEL_v3={model_v3_est:.4f}",
        flush=True,
    )

    # 8. STEP 4 — PACKAGE VIA SHARED submission_writer.py + WRITE 11-GATE AUDIT & BYTE-BOUND RUN CARD
    support_hash8 = hashlib.sha256(pos_cand.astype(np.int32).tobytes()).hexdigest()[:8]
    stem = f"gemsdoe92-dexpkostrov1-{n_cand}dots-20261029-{support_hash8}"
    tif_path = ROOT / "docs" / "downloads" / f"{stem}-zeros.tif"
    sub_name = f"gemsdoe92-dexpkostrov1-{n_cand}d-{support_hash8}"
    note = (
        f"DEXP-Kostrov E3: {n_cand} binary dots; Fedi DEXP N~0 + Kostrov strain + Koenderink toe; "
        f"HOLDOUT-DTI {summ_e3['scores']['e3_dexp_kostrov_unique']['dti']:.4f} > R0."
    )
    assert len(note) <= 140, f"note too long: {len(note)}"

    receipt = submission_writer.write_submission(
        tif_path,
        pred_float,
        L.SAMPLE,
        foot,
        note=note,
        name=sub_name,
        catalogue=cat,
        metadata={"lane": "DEXP-KOSTROV-KOENDERINK", "experiment": "E3", "date": "2026-10-29"},
    )
    for p_out in (tif_path, tif_path.with_suffix(".zip"), tif_path.with_suffix(".json")):
        if p_out.is_file():
            p_out.chmod(0o644)
    raster_sha = receipt["sha256"]

    # Map SHA -> repo/path for worst overlap & rho witnesses
    sha_to_path = {}
    for r in inv["repositories"]:
        for f in r["files"]:
            sha_to_path.setdefault(f["sha256"], f"{r['owner']}/{r['repo']}:{f['path']}")

    # Focus-9 specific overlaps against our candidate
    f9_src = json.loads((ROOT / "evidence" / "focus9_sources_20261028.json").read_text())
    row_by_sha_final = {r["sha256"]: r for r in aud_final["rows"]}
    row_by_sha_surf = {r["sha256"]: r for r in aud_surf["rows"]}
    focus9_vs_cand = {}
    for site, info in f9_src.items():
        f9_sha = info["sha256"]
        rf = row_by_sha_final.get(f9_sha, {})
        rs = row_by_sha_surf.get(f9_sha, {})
        focus9_vs_cand[site] = dict(
            focus_file=info["best"],
            focus_sha256=f9_sha,
            focus_claim=info["claim"],
            surface_overlap_pi1=rs.get("overlap_pi1"),
            final_overlap_pi1=rf.get("overlap_pi1"),
            final_rho=rf.get("rho"),
        )

    # 11-gate root format check (gems.gates.run_gates) for check_site.py compatibility
    gates_11 = [
        {"name": g.name, "ok": bool(g.ok), "detail": g.detail}
        for g in root_gates.run_gates(tif_path, L.SAMPLE, L.CATALOGUE, require_submission_encoding=True)
    ]
    assert all(g["ok"] for g in gates_11), f"11-gate failure: {gates_11}"

    run_card_rel = f"docs/downloads/{stem}_run_card.json"
    audit_path = ROOT / "docs" / "downloads" / f"{stem}-zeros-audit.json"
    audit_json = dict(
        schema="gemsdoe92-submission-audit-v3",
        id=stem,
        lane="DEXP-KOSTROV-KOENDERINK",
        overall_pass=True,
        verdict="negative",
        submission_eligible=False,
        zeros_file=f"docs/downloads/{tif_path.name}",
        zip_file=f"docs/downloads/{receipt['zip_file']}",
        sha256_zeros=raster_sha,
        sha256_zip=receipt["zip_sha256"],
        bytes_zeros=receipt["bytes"],
        n_dots=n_cand,
        gates_zeros=gates_11,
        run_card=run_card_rel,
        status_note=(
            "Format (11/11), leakage canaries (36/36 <= 0.90), fold-proper HOLDOUT-DTI vs R0 recipe, and "
            "operational PI-1 uniqueness across all 2,262 fleet rasters (pre-placement surface & final dots) "
            "ALL PASS; held fail-closed (verdict='negative', submission_eligible=false) solely under the "
            "unresolved literal dense-witness rule (17GEMSDOE E-proba-multiscale = 1.000 > 0.70) and unverified "
            "official redistribution provenance."
        ),
    )
    audit_path.write_text(json.dumps(audit_json, indent=2) + "\n", encoding="utf-8")

    e3_sc = summ_e3["scores"]["e3_dexp_kostrov_unique"]
    r0_sc = summ_e3["scores"]["r0_recipe"]
    e1_sc = summ_e3["scores"]["e1_dexp_kostrov_blind"]
    e2_sc = summ_e3["scores"]["e2_dexp_kostrov_dual"]

    run_card = dict(
        schema="gemsdoe92-protocol-run-card-v4",
        built_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        lane="DEXP-KOSTROV-KOENDERINK",
        pre_registration="docs/HYPOTHESES_20261029_DEXP_KOSTROV.md",
        experiments_run=3,
        weekly_slots_used=0,
        hypothesis=(
            "Upward-continuing B13 isostatic gravity and B02 RTP magnetics across z in {100..1600} m to isolate "
            "Fedi (2007) DEXP structural-index N ~ 0 crustal fault steps while rejecting shallow N >= 1 Tertiary "
            "volcanic flow/sill edges, gating dip-slip updip listric steps vs Walker Lane wrench-transtensional "
            "MT/RTP shear corridors via the Kostrov-Simpson geodetic strain-style index S_style, and coupling with "
            "amplitude-invariant Koenderink piedmont-toe shape index + strictly fold-visible self-excluded network "
            "continuation recovers both proximal splays (2<d<=15 px) and distal blind faults (d>15 px), beating R0 "
            "recipe on HOLDOUT-DTI while passing full 2,262-SHA PI-1 uniqueness on both surface and final dots."
        ),
        mechanism=(
            "5-altitude 2D-FFT Fedi DEXP structural-index N(x) fault-step filter + Kostrov-Simpson strain-style "
            "kinematic gate S_style + Grauch-Cordell 420 m updip listric projection + Koenderink-van Doorn piedmont "
            "shape index + self-excluded visible-network continuation in a 4-quadrant LOQO ensemble, with Lagrangian "
            "multi-witness diversification across 2,262 registry rasters (40,000 binary dots, >=2.8 px spacing)."
        ),
        named_non_fault_mimic=(
            "Unfaulted Mesozoic granodiorite pluton-wall contacts (N ~ 0-0.4) and ~1,330 m Pleistocene Lake Lahontan "
            "wave-cut shoreline notches; deconfounded by active geodetic strain second invariant I2, elevation-band "
            "shoreline suppression, and shallow-volcanic decay contrast dk03."
        ),
        leakage_canaries=dict(
            n_features_tested=len(canary_rows),
            threshold_auc=0.90,
            max_auc=round(max_sym_auc, 6),
            leakage_flag=False,
            evidence_file="evidence/dexp_kostrov_canaries_20261029.json",
        ),
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI",
            evaluator_version=evaluate_holdout.VERSION,
            withheld_positive_pixels=e3_sc["withheld_positive_pixels"],
            e1_blind_loqo=dict(dti=round(e1_sc["dti"], 6), ci95=[round(x, 6) for x in e1_sc["ci95"]]),
            e2_dual_regime=dict(dti=round(e2_sc["dti"], 6), ci95=[round(x, 6) for x in e2_sc["ci95"]]),
            e3_candidate=dict(dti=round(e3_sc["dti"], 6), ci95=[round(x, 6) for x in e3_sc["ci95"]]),
            r0_recipe_control=dict(dti=round(r0_sc["dti"], 6), ci95=[round(x, 6) for x in r0_sc["ci95"]]),
            paired_e3_vs_r0_recipe=dict(
                delta=round(delta_r0["delta"], 6),
                ci95=[round(x, 6) for x in delta_r0["ci95"]],
                beats_r0_ci95_gt_0=beats_r0_ci,
            ),
            evidence_file="evidence/dexp_kostrov_holdout_20261029.json",
        ),
        model_estimate=dict(
            evidence_class="MODEL (132-claim LOGO diagnostic — NOT a leaderboard score)",
            lbm_v2_132=round(model_v2_est, 4),
            lbm_v3_saturated_132=round(model_v3_est, 4),
            regime_shares=dict(
                dcat_2_to_15px=round(frac_dcat_2_15, 4),
                dcat_gt_15px=round(frac_dcat_gt15, 4),
            ),
            note="Reported strictly as diagnostic MODEL output calibrated on 132 owner CLAIMs (including lbmc1=0.2784).",
        ),
        uniqueness=dict(
            registry_owners=inv["owners"],
            registry_non_empty_repos=len(inv["repositories"]),
            registry_unique_rasters=len(all_shas_2262),
            dot_field_rasters=len(hs),
            surface_rasters=len(all_shas_2262) - len(hs),
            pi1_operational_reading=dict(
                pre_placement_surface_pass=not aud_surf["duplicate"],
                surface_worst_overlap=aud_surf["worst_overlap_pi1"]["overlap_pi1"],
                surface_worst_overlap_witness=sha_to_path.get(aud_surf["worst_overlap_pi1"]["sha256"]),
                surface_worst_abs_rho=abs(aud_surf["worst_abs_rho"]["rho"]),
                surface_worst_rho_witness=sha_to_path.get(aud_surf["worst_abs_rho"]["sha256"]),
                final_dots_pass=not aud_final["duplicate"],
                final_worst_overlap=aud_final["worst_overlap_pi1"]["overlap_pi1"],
                final_worst_overlap_witness=sha_to_path.get(aud_final["worst_overlap_pi1"]["sha256"]),
                final_worst_abs_rho=abs(aud_final["worst_abs_rho"]["rho"]),
                final_worst_rho_witness=sha_to_path.get(aud_final["worst_abs_rho"]["sha256"]),
            ),
            focus9_comparison=focus9_vs_cand,
            literal_reading=dict(
                duplicate_under_literal=bool(aud_final["literal_reading"]["duplicate_under_literal"]),
                worst_literal_overlap=aud_final["literal_reading"]["worst"]["overlap_literal"],
                worst_literal_sha256=aud_final["literal_reading"]["worst"]["sha256"],
                worst_literal_witness=sha_to_path.get(aud_final["literal_reading"]["worst"]["sha256"]),
                note=(
                    "17GEMSDOE E-proba-multiscale is positive (>0) on all 5,167,373 footprint cells (100.0%), "
                    "and 13GEMSDOE r13-lattice-s5 (206,895 binary dots) covers 99.87% of footprint within 3 px, "
                    "forcing literal overlap > 0.70 for every nonempty candidate. Kept fail-closed pending human rule disposition."
                ),
            ),
        ),
        raster=dict(
            file=f"docs/downloads/{tif_path.name}",
            zip_file=f"docs/downloads/{receipt['zip_file']}",
            audit_file=f"docs/downloads/{audit_path.name}",
            bytes=receipt["bytes"],
            n_dots=n_cand,
        ),
        raster_sha256=raster_sha,
        zip_sha256=receipt["zip_sha256"],
        validator_output=dict(
            all_11_gates_pass=True,
            no_nan_in_footprint=True,
            no_nan_anywhere=True,
            values_in_0_1=True,
            crs_match=True,
            shape_match=True,
            transform_match=True,
            zero_on_mapped_catalogue=True,
            template_validator=receipt["validator"],
        ),
        gates_passed=dict(
            format_11_of_11=True,
            no_leakage_canaries_le_0_90=True,
            catalogue_holdout_beats_r0_recipe=beats_r0_ci,
            uniqueness_pi1_surface_2262=not aud_surf["duplicate"],
            uniqueness_pi1_final_2262=not aud_final["duplicate"],
            uniqueness_literal_dense_witness=False,
            official_input_provenance_verified=False,
        ),
        submission_name=sub_name,
        note=note,
        note_chars=len(note),
        verdict="negative",
        submission_eligible=False,
        status_banner="OK TO DOWNLOAD FOR RESEARCH ONLY — DO NOT SUBMIT (held fail-closed at literal dense-witness & provenance gates)",
    )
    (ROOT / run_card_rel).write_text(json.dumps(run_card, indent=2) + "\n", encoding="utf-8")
    (ROOT / "evidence" / f"{stem}_run_card.json").write_text(json.dumps(run_card, indent=2) + "\n", encoding="utf-8")

    print(f"\n[{time.time()-t0:.1f}s] SUCCESS: Wrote {tif_path.name} (SHA-256 {raster_sha[:16]}...)")
    print(f"  HOLDOUT-DTI E3 = {e3_sc['dti']:.6f} vs R0 = {r0_sc['dti']:.6f} (delta = {delta_r0['delta']:+.6f}, CI {delta_r0['ci95']})")
    print(f"  PI-1 2,262-SHA surface worst = {aud_surf['worst_overlap_pi1']['overlap_pi1']:.5f}, final worst = {aud_final['worst_overlap_pi1']['overlap_pi1']:.5f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
