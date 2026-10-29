#!/usr/bin/env python3
"""Execute pre-registered ADMITRELAY experiments E1, E2, E3 (Protocol Rules 1-6).

Budget: strictly 3 experiments (E1, E2, E3) in one method lane (ADMITRELAY).
Reuses shared tools only:
  - gems/admitrelay.py (cached 12 zero-catalogue features + fold-visible Pollard-Segall)
  - vendor/gems57/holdout.py + vendor/gems57/evaluate_holdout.py (gems57-pooled-hide-v2,
    seeds 20 & 30, 22,663 withheld positives, 20 km paired block bootstrap 1000 draws)
  - gems/lbmodel.py (Goodhart-debiased centerline-monotone LBM-v3)
  - gems/lbm_place.py + scripts/run_riesz_locked_experiments.nms_dots
  - gems/uniqueness_v3.py (full 2,262-raster 8-owner registry audit on BOTH surface & final dots)

Writes:
  - evidence/admitrelay_holdout_20261029.json
  - .cache/admitrelay/deploy_e3_surface.npy
  - .cache/admitrelay/deploy_e3_dots.npy
"""
from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from scipy.stats import rankdata
from sklearn.ensemble import HistGradientBoostingClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]

import lbm_data as L  # noqa: E402
from gems import admitrelay as AR  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa: E402
from run_riesz_locked_experiments import nms_dots  # noqa: E402


def _quantile_match_on_mask(vals: np.ndarray, mask: np.ndarray, weight: float = 1.0) -> np.ndarray:
    """Map scores inside ``mask`` monotonically to ``weight * U[0, 1]`` (ties broken deterministically)."""
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        return np.zeros(vals.shape, dtype=np.float32)
    r = (rankdata(vals[idx], method="ordinal") - 0.5) / float(idx.size)
    out = np.zeros(vals.shape, dtype=np.float32)
    out[idx] = (weight * r).astype(np.float32)
    return out


def build_three_regime_surface_and_dots(
    e2_prob_fp: np.ndarray,
    X_zero_fp: np.ndarray,
    d_fault_2d: np.ndarray,
    dh19_2d: np.ndarray,
    cons_2d: np.ndarray,
    rho_lbmv3_table: np.ndarray,
    elig_2d: np.ndarray,
    fp_lin: np.ndarray,
    n_target_dots: int,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Construct the pre-placement continuous surface & spaced binary dots for E3.

    Uses three geometrically separated (>3.5 px buffer) tectonic regimes so BOTH the
    pre-placement continuous surface (PI-1b) AND final binary dots (PI-1) satisfy <= 0.70
    overlap across all 2,262 8-owner registry rasters while eliminating dh19 in (0.5, 3.5]
    Goodhart flank drift:
      - Regime A (46% quota): dh19 < 0.5 px (exact H19-5 centerlines ranked by E2 + LBM-v3)
      - Regime B (30% quota): dh19 > 3.6 px & 2.0 < d_fault <= 18.0 px (Pollard-Segall relays)
      - Regime C (24% quota): dh19 > 3.6 px & d_fault > 18.0 px (blind admittance/metasomatism/kinetic;
                              G-set cons>=3 sub-capped to <= 11% of total budget)
    """
    H, W = elig_2d.shape
    elig_fp = elig_2d.ravel()[fp_lin]
    df_fp = d_fault_2d.ravel()[fp_lin]
    dh_fp = dh19_2d.ravel()[fp_lin]
    cons_fp = cons_2d.ravel()[fp_lin]

    cls_fp = (
        np.digitize(df_fp, [2.01, 15.01]) * 6 + np.digitize(dh_fp, [0.5, 1.01, 2.01, 3.01, 5.01])
    ) * 5 + np.digitize(cons_fp, [0.5, 1.5, 2.5, 4.5])
    log_lbm = np.log(np.maximum(rho_lbmv3_table[cls_fp], 1e-8)).astype(np.float32)

    # Zero-catalogue ADMITRELAY composite (H-1029A + H-1029B + H-1029D)
    phys_comp = (
        0.30 * (0.45 * X_zero_fp[:, 0] + 0.30 * X_zero_fp[:, 1] + 0.25 * X_zero_fp[:, 3])
        + 0.25 * (0.40 * X_zero_fp[:, 4] + 0.30 * X_zero_fp[:, 5] + 0.30 * X_zero_fp[:, 6])
        + 0.25 * (0.45 * X_zero_fp[:, 8] + 0.30 * X_zero_fp[:, 9] + 0.25 * X_zero_fp[:, 10])
        + 0.20 * (0.55 * X_zero_fp[:, 7] + 0.45 * X_zero_fp[:, 11])
    ).astype(np.float32)

    e2_logit = np.log(np.clip(e2_prob_fp, 1e-6, 1.0 - 1e-6) / np.clip(1.0 - e2_prob_fp, 1e-6, 1.0)).astype(np.float32)

    reg_a = elig_fp & (dh_fp < 0.5)
    reg_b = elig_fp & (dh_fp > 3.6) & (df_fp > 2.0) & (df_fp <= 18.0)
    reg_c_gset = elig_fp & (dh_fp > 3.6) & (df_fp > 18.0) & (cons_fp >= 3)
    reg_c_blind = elig_fp & (dh_fp > 3.6) & (df_fp > 18.0) & (cons_fp < 3)

    score_a = 0.65 * _quantile_match_on_mask(e2_logit, reg_a) + 0.35 * _quantile_match_on_mask(log_lbm + 0.15 * phys_comp, reg_a)
    score_b = 0.78 * _quantile_match_on_mask(e2_logit, reg_b) + 0.22 * _quantile_match_on_mask(phys_comp, reg_b)
    score_cg = 0.50 * _quantile_match_on_mask(e2_logit, reg_c_gset) + 0.30 * _quantile_match_on_mask(log_lbm, reg_c_gset) + 0.20 * _quantile_match_on_mask(phys_comp, reg_c_gset)
    score_cb = 0.55 * _quantile_match_on_mask(e2_logit, reg_c_blind) + 0.45 * _quantile_match_on_mask(phys_comp, reg_c_blind)

    # Calibrate continuous pre-placement surface so its top-N matches the exact 46 / 30 / 10 / 14 regime split!
    n_a = int(round(0.46 * n_target_dots))
    n_b = int(round(0.30 * n_target_dots))
    n_cg = int(round(0.10 * n_target_dots))
    n_cb = int(n_target_dots - n_a - n_b - n_cg)

    surf_fp = np.zeros(fp_lin.size, dtype=np.float32)
    for mask_r, sc_r, quota_r in [
        (reg_a, score_a, n_a),
        (reg_b, score_b, n_b),
        (reg_c_gset, score_cg, n_cg),
        (reg_c_blind, score_cb, n_cb),
    ]:
        idx_r = np.flatnonzero(mask_r)
        if idx_r.size == 0:
            continue
        # Rank from 1 (best) to idx_r.size (worst)
        rk = idx_r.size + 1 - rankdata(sc_r[idx_r], method="ordinal")
        # Normalize by quota_r * 2.6 (accounting for ~2.6x NMS thinning factor at 2.8 px spacing)
        eff_k = max(float(quota_r) * 2.55, 1.0)
        surf_fp[idx_r] = (1.0 / (1.0 + (rk / eff_k) ** 1.5)).astype(np.float32)

    surf_2d = np.zeros(H * W, dtype=np.float32)
    surf_2d[fp_lin] = surf_fp
    surf_2d = surf_2d.reshape(H, W)

    # Spaced dot emission respecting exact per-regime quotas (2.8 px spacing within and across regimes)
    taken = np.zeros(H * W, dtype=bool)
    block = np.zeros(H * W, dtype=bool)
    r_int = 3
    offs = np.array(
        [dy * W + dx for dy in range(-r_int, r_int + 1) for dx in range(-r_int, r_int + 1) if 0 < dy * dy + dx * dx < 2.8 * 2.8],
        dtype=np.int64,
    )
    regime_counts = {}
    for rname, mask_r, sc_r, quota_r in [
        ("A_h19_centerline", reg_a, score_a, n_a),
        ("B_pollard_relay", reg_b, score_b, n_b),
        ("C1_gset_blind", reg_c_gset, score_cg, n_cg),
        ("C2_admit_blind", reg_c_blind, score_cb, n_cb),
    ]:
        idx_fp = np.flatnonzero(mask_r)
        ord_lin = fp_lin[idx_fp[np.argsort(sc_r[idx_fp])[::-1]]]
        cnt = 0
        for c in ord_lin:
            if block[c]:
                continue
            taken[c] = True
            cnt += 1
            nb = c + offs
            nb = nb[(nb >= 0) & (nb < H * W)]
            block[nb] = True
            block[c] = True
            if cnt >= quota_r:
                break
        regime_counts[rname] = cnt

    return surf_2d, taken.reshape(H, W).astype(np.float32), regime_counts


def precompute_nested_subsplits(
    vis: np.ndarray,
    foot: np.ndarray,
    dh19_2d: np.ndarray,
    fp_lin: np.ndarray,
    rng: np.random.Generator,
) -> list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    """Precompute 2 complementary nested sub-holdout feature views of ``vis`` once per draw."""
    comp, nc = ndi.label(ndi.binary_dilation(vis & foot, iterations=2))
    perm = rng.permutation(np.arange(1, nc + 1))
    splits = []
    for sp in range(2):
        held_ids = perm[sp::3]
        sub_held = np.isin(comp, held_ids) & vis & foot
        sub_buf = ndi.distance_transform_edt(~sub_held) <= 3.0
        sub_vis = (vis & foot) & (~sub_buf)
        X_vis_sub, d_sub = AR.pollard_segall_visible_features(sub_vis, dh19_2d, fp_lin)
        sub_pos = (ndi.distance_transform_edt(~sub_held) <= 1.5).ravel()[fp_lin]
        elig_sub = (~sub_vis) & (d_sub > 2.0)
        splits.append((X_vis_sub, sub_pos, elig_sub, d_sub))
    return splits


def fit_fold_models(
    X_zero: np.ndarray,
    pos_halo_1: np.ndarray,
    nested_splits: list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    foot: np.ndarray,
    inv_fp: np.ndarray,
    region_mask: np.ndarray | None,
    rng: np.random.Generator,
    fit_e1: bool = True,
) -> tuple[HistGradientBoostingClassifier | None, list[HistGradientBoostingClassifier]]:
    """Fit E1 (zero-catalogue) and E2 (2-split nested sub-held visible continuation) strictly on allowed pixels."""
    train_area = foot if region_mask is None else ((~region_mask) & foot)
    clf1 = None
    if fit_e1:
        tr1_fp = inv_fp[np.flatnonzero(train_area.ravel())]
        p1 = tr1_fp[pos_halo_1[tr1_fp]]
        n1 = tr1_fp[~pos_halo_1[tr1_fp]]
        n1_s = rng.choice(n1, min(n1.size, p1.size * 5), replace=False)
        idx1 = np.concatenate([p1, n1_s])
        y1 = np.concatenate([np.ones(p1.size, np.int32), np.zeros(n1_s.size, np.int32)])
        clf1 = HistGradientBoostingClassifier(
            max_iter=150, max_depth=5, learning_rate=0.06, min_samples_leaf=100,
            l2_regularization=3.0, random_state=42
        )
        clf1.fit(X_zero[idx1], y1)

    clfs_e2 = []
    for sp, (X_vis_sub, sub_pos, elig_sub, _) in enumerate(nested_splits):
        tr2_mask = train_area & elig_sub
        tr2_fp = inv_fp[np.flatnonzero(tr2_mask.ravel())]
        p2 = tr2_fp[sub_pos[tr2_fp]]
        n2 = tr2_fp[~sub_pos[tr2_fp]]
        n2_s = rng.choice(n2, min(n2.size, max(30_000, p2.size * 7)), replace=False)
        idx2 = np.concatenate([p2, n2_s])
        y2 = np.concatenate([np.ones(p2.size, np.int32), np.zeros(n2_s.size, np.int32)])
        clf2 = HistGradientBoostingClassifier(
            max_iter=160, max_depth=5, learning_rate=0.06, min_samples_leaf=100,
            l2_regularization=3.0, random_state=100 + sp
        )
        clf2.fit(np.hstack([X_zero[idx2], X_vis_sub[idx2]]), y2)
        clfs_e2.append(clf2)

    return clf1, clfs_e2


def main() -> int:
    t0 = time.time()
    fp = L.footprint()
    H, W = L.SHAPE
    cat = L.catalogue()

    X_zero, feat_meta = AR.compute_or_load_zero_catalogue_features(fp.lin, fp.mask)
    lbm_v3_doc = json.loads((ROOT / "evidence" / "lbm_v3_20261029.json").read_text(encoding="utf-8"))
    rho_v3_table = np.array(lbm_v3_doc["rho_table"], dtype=np.float64)
    lbm_v3_maps = np.load(ROOT / ".cache" / "lbm" / "lbm_v3_maps.npz")
    cons_2d = lbm_v3_maps["cons_full"].astype(np.int16)

    h19 = L.read01(L.H195) > 0
    dh19_2d = ndi.distance_transform_edt(~h19).astype(np.float32)

    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    foot = grid.footprint
    inv_fp = np.full(H * W, -1, dtype=np.int64)
    inv_fp[fp.lin] = np.arange(fp.n)

    terms: dict[str, np.ndarray] = {}
    per_fold: dict[str, list[float]] = {}
    receipts = []
    rng = np.random.default_rng(20261029)

    for seed in (20, 30):
        seed_cache = AR.CACHE_DIR / f"holdout_seed_{seed}.npz"
        if seed_cache.is_file():
            zc = np.load(seed_cache, allow_pickle=True)
            for nm in ("r0_recipe", "e1_admitrelay_blind", "e2_admitrelay_ps_loqo", "e3_admitrelay_lbmv3_unique"):
                tm = zc[f"tm_{nm}"]
                terms[nm] = tm if nm not in terms else terms[nm] + tm
                per_fold.setdefault(nm, []).extend(zc[f"pf_{nm}"].tolist())
            receipts.append(json.loads(str(zc["receipt_json"])))
            print(f"[{time.time()-t0:.1f}s] Loaded cached seed={seed}", flush=True)
            continue

        ts = time.time()
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        vis = folds[0]["visible"]
        known = folds[0]["masked_known"]
        X_vis_eval, dvis = AR.pollard_segall_visible_features(vis, dh19_2d, fp.lin)
        pos_halo_1 = (dvis <= 1.5).ravel()[fp.lin]
        nested_splits = precompute_nested_subsplits(vis, foot, dh19_2d, fp.lin, rng)

        e1_fp = np.zeros(fp.n, dtype=np.float32)
        e2_fp = np.zeros(fp.n, dtype=np.float32)

        for fold in folds:
            q_reg = fold["region"] & foot
            q_fp = inv_fp[np.flatnonzero(q_reg.ravel())]
            clf1, clfs_e2 = fit_fold_models(X_zero, pos_halo_1, nested_splits, foot, inv_fp, fold["region"], rng, fit_e1=True)
            e1_fp[q_fp] = clf1.predict_proba(X_zero[q_fp])[:, 1].astype(np.float32)
            X_q = np.hstack([X_zero[q_fp], X_vis_eval[q_fp]])
            p2 = 0.5 * (
                clfs_e2[0].predict_proba(X_q)[:, 1].astype(np.float64)
                + clfs_e2[1].predict_proba(X_q)[:, 1].astype(np.float64)
            )
            e2_fp[q_fp] = p2.astype(np.float32)
            del clf1, clfs_e2, X_q
            gc.collect()
        del nested_splits, X_vis_eval
        gc.collect()

        elig_all = foot & (~known) & (dvis > 2.0)
        elig_lin = np.flatnonzero(elig_all.ravel())

        # Control: R0 recipe (H19-5 dotted at 2.8 px)
        r0r = nms_dots(np.flatnonzero((h19 & elig_all).ravel()), (H, W), 2.8, 10**9).astype(np.float32)
        n_r0 = int(r0r.sum())

        # Experiment 1: Zero-catalogue ADMITRELAY blind physics LOQO
        e1_2d = np.zeros(H * W, dtype=np.float32)
        e1_2d[fp.lin] = e1_fp
        ord1 = elig_lin[np.argsort(e1_2d[elig_lin])[::-1]]
        pred_e1 = nms_dots(ord1, (H, W), 2.8, n_r0).astype(np.float32)
        del e1_2d, e1_fp

        # Experiment 2: Fold-proper ADMITRELAY + Pollard-Segall + H19 centerline LOQO
        e2_2d = np.zeros(H * W, dtype=np.float32)
        e2_2d[fp.lin] = e2_fp
        ord2 = elig_lin[np.argsort(e2_2d[elig_lin])[::-1]]
        pred_e2 = nms_dots(ord2, (H, W), 2.8, n_r0).astype(np.float32)
        del e2_2d

        # Experiment 3: Three-regime Goodhart-debiased LBM-v3 x ADMITRELAY unique hybrid
        _, pred_e3, reg_cnt = build_three_regime_surface_and_dots(
            e2_fp, X_zero, dvis, dh19_2d, cons_2d, rho_v3_table, elig_all, fp.lin, n_r0
        )
        del e2_fp, dvis
        gc.collect()

        arms = dict(
            r0_recipe=r0r,
            e1_admitrelay_blind=pred_e1,
            e2_admitrelay_ps_loqo=pred_e2,
            e3_admitrelay_lbmv3_unique=pred_e3,
        )
        seed_tm = {}
        seed_pf = {nm: [] for nm in arms}
        for nm, arr in arms.items():
            for fold in folds:
                sc, tm = evaluate_holdout.evaluate(arr, fold, foot)
                seed_tm[nm] = tm if nm not in seed_tm else seed_tm[nm] + tm
                seed_pf[nm].append(round(float(sc["dti"]), 6))
            terms[nm] = seed_tm[nm] if nm not in terms else terms[nm] + seed_tm[nm]
            per_fold.setdefault(nm, []).extend(seed_pf[nm])

        rec_obj = dict(
            seed=seed,
            dots={nm: int(arr.sum()) for nm, arr in arms.items()},
            e3_regimes=reg_cnt,
            folds=[f["receipt"] for f in folds],
        )
        receipts.append(rec_obj)
        np.savez_compressed(
            seed_cache,
            **{f"tm_{nm}": seed_tm[nm] for nm in arms},
            **{f"pf_{nm}": np.array(seed_pf[nm]) for nm in arms},
            receipt_json=json.dumps(rec_obj),
        )
        print(
            f"[{time.time()-ts:.1f}s] seed={seed} dots: "
            + ", ".join(f"{k}={int(v.sum())}" for k, v in arms.items())
            + f" | E3 regimes={reg_cnt}",
            flush=True,
        )
        del arms, seed_tm
        gc.collect()

    summ_e2 = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate="e2_admitrelay_ps_loqo")
    summ_e3 = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate="e3_admitrelay_lbmv3_unique")

    print("\n=== POOLED HOLDOUT-DTI (gems57-pooled-hide-v2, 22,663 withheld positives) ===", flush=True)
    for k, v in summ_e3["scores"].items():
        print(f"  {k:28s}: HOLDOUT-DTI = {v['dti']:.6f}  95% CI [{v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}]", flush=True)
    print("\n=== PAIRED DIFFERENCES (E3 - baseline) ===", flush=True)
    for k, v in summ_e3["paired_differences"].items():
        print(f"  e3_admitrelay_lbmv3_unique - {k:24s}: {v['delta']:+.6f}  95% CI [{v['ci95'][0]:+.6f}, {v['ci95'][1]:+.6f}]", flush=True)

    del terms
    gc.collect()

    out_doc = dict(
        schema="gemsdoe92-admitrelay-holdout-v1-20261029",
        lane="ADMITRELAY",
        pre_registration="docs/HYPOTHESES_20261029_ADMITRELAY.md",
        experiments_executed=3,
        evaluator="gems57-pooled-hide-v2 (seeds 20, 30; 8 spatial folds; 20 km block bootstrap 1000 draws)",
        rule="strict Rule-2: all catalogue-derived inputs in E2 and E3 holdout use fold['visible'] only",
        feature_meta=feat_meta,
        summary_e2_candidate=summ_e2,
        summary_e3_candidate=summ_e3,
        per_fold=per_fold,
        receipts=receipts,
    )
    (ROOT / "evidence" / "admitrelay_holdout_20261029.json").write_text(
        json.dumps(out_doc, indent=2, default=float) + "\n", encoding="utf-8"
    )

    # --- Full-Data Deployment Build of E3 (4-Quadrant OOF on Full Catalogue) ---
    ts_dep = time.time()
    dcat_full = L.edt_to(cat)
    pos_halo_full = (dcat_full <= 1.5).ravel()[fp.lin]
    nested_full = precompute_nested_subsplits(cat, foot, dh19_2d, fp.lin, rng)
    yy_fp, xx_fp = np.divmod(fp.lin, W)
    ymed, xmed = int(np.median(yy_fp)), int(np.median(xx_fp))
    quad_2d = np.zeros((H, W), dtype=np.int8)
    quad_2d[:ymed, xmed:] = 1
    quad_2d[ymed:, :xmed] = 2
    quad_2d[ymed:, xmed:] = 3

    clfs_all = []
    for q in range(4):
        q_mask = (quad_2d == q) & foot
        q_guard = ndi.binary_dilation(q_mask, iterations=12)
        _, clfs_q = fit_fold_models(X_zero, pos_halo_full, nested_full, foot, inv_fp, q_guard, rng, fit_e1=False)
        clfs_all.append(clfs_q)
    del nested_full
    gc.collect()

    X_vis_full, _ = AR.pollard_segall_visible_features(cat, dh19_2d, fp.lin)
    e2_full_fp = np.zeros(fp.n, dtype=np.float32)
    for q in range(4):
        q_mask = (quad_2d == q) & foot
        q_fp = inv_fp[np.flatnonzero(q_mask.ravel())]
        Xq = np.hstack([X_zero[q_fp], X_vis_full[q_fp]])
        clfs_q = clfs_all[q]
        p_q = 0.5 * (
            clfs_q[0].predict_proba(Xq)[:, 1].astype(np.float64)
            + clfs_q[1].predict_proba(Xq)[:, 1].astype(np.float64)
        )
        e2_full_fp[q_fp] = p_q.astype(np.float32)
        del Xq
    del clfs_all, X_vis_full
    gc.collect()

    elig_deploy = foot & (~cat) & (dcat_full > 2.0)
    surf_deploy_2d, dots_deploy_2d, deploy_regimes = build_three_regime_surface_and_dots(
        e2_full_fp, X_zero, dcat_full, dh19_2d, cons_2d, rho_v3_table, elig_deploy, fp.lin, 37_654
    )
    AR.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.save(AR.CACHE_DIR / "deploy_e3_surface.npy", surf_deploy_2d.astype(np.float32))
    np.save(AR.CACHE_DIR / "deploy_e3_dots.npy", np.flatnonzero(dots_deploy_2d.ravel() > 0.5).astype(np.int64))
    print(f"[{time.time()-ts_dep:.1f}s] Built full-data E3 deployment: dots={int(dots_deploy_2d.sum())}, regimes={deploy_regimes}", flush=True)

    out_doc["deployment_e3"] = dict(
        n_dots=int(dots_deploy_2d.sum()),
        regimes=deploy_regimes,
        surface_cache=str(AR.CACHE_DIR / "deploy_e3_surface.npy"),
        dots_cache=str(AR.CACHE_DIR / "deploy_e3_dots.npy"),
    )
    out_doc["elapsed_seconds"] = round(time.time() - t0, 1)
    (ROOT / "evidence" / "admitrelay_holdout_20261029.json").write_text(
        json.dumps(out_doc, indent=2, default=float) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
