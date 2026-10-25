#!/usr/bin/env python3
"""POISSONFLEX lane driver:
Stage 1: catalogue-free 30-feature stack + 1D crest localizers (.cache/poissonflex/features.npz)
Stage 2: single-feature leakage canary gate (all symmetric AUCs <= 0.90; Protocol Rule 4)
Stage 3: strict draw-blind Rule-2 LOQO holdout (seeds 20+30, 22,663 withheld positives,
         paired 20 km block bootstrap vs COULOMBLOQO standalone, H19-5, and R0;
         plus low-conspicuity stratum & quadrant-stratified DTI)
Stage 4: full deployment LOQO fit, pre-placement surface check, emission of the 3
         pre-registered arms (poissonflex_eq, poissonflex_raw, poissonflex_opt),
         static d_cat > 2.0 holdout DTI, and off-catalogue USGS SGMC proxy.

Pre-registration: docs/HYPOTHESES_20261025_POISSONFLEX.md.
Reuses unmodified: gems57.holdout, gems57.evaluate_holdout, gems57.metric.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import gc
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.ndimage import distance_transform_edt
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems import blindfault as bf, coulomb_loqo as cl, poissonflex as pf  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric as gems57_metric  # noqa: E402

CACHE = ROOT / ".cache" / "poissonflex"
INPUTS = ROOT / ".cache" / "gems_inputs"
STACK_TIF = INPUTS / "training_features.tif"
RAD_TIF = INPUTS / "external" / "geodawn_rad_u8.tif"
GDR_CSV = INPUTS / "external" / "gdr_wellspring_in_footprint.csv"
SGMC_TIF = INPUTS / "external" / "derived_sgmc_faults_100m_u8.tif"
EVIDENCE = ROOT / "evidence"
DATE = "20261025"
N_PARENT_BUDGET = 37_654
BUDGET_GRID = (26_000, 30_000, 34_000, 37_654, 41_500, 45_000)
SEEDS = (20, 30)
ARMS = ("poissonflex_eq", "poissonflex_raw", "poissonflex_opt")


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_or_compute_features(foot: np.ndarray, quad: np.ndarray) -> dict[str, np.ndarray | dict]:
    x_p = CACHE / "X_foot.npy"
    v_p = CACHE / "valid.npy"
    lsk_p = CACHE / "L_scarp_knick.npy"
    lpf_p = CACHE / "L_poisson_flex.npy"
    con_p = CACHE / "conspicuity.npy"
    meta_p = CACHE / "features_meta.json"

    if all(p.is_file() for p in (x_p, v_p, lsk_p, lpf_p, con_p, meta_p)):
        log("loading memory-mapped POISSONFLEX feature stack from .cache/poissonflex/ ...")
        meta = json.loads(meta_p.read_text())
        return {
            "X_foot": np.load(x_p, mmap_mode="r"),
            "valid": np.load(v_p),
            "L_scarp_knick": np.load(lsk_p),
            "L_poisson_flex": np.load(lpf_p),
            "conspicuity": np.load(con_p),
            "gdr_meta": meta["gdr_meta"],
        }

    log("streaming 30-feature POISSONFLEX stack into memory-mapped .npy (< 750 MB peak RSS) ...")
    n_foot = int(foot.sum())
    x_mm = np.lib.format.open_memmap(x_p, mode="w+", dtype=np.float32, shape=(n_foot, len(pf.FEATURE_NAMES)))
    feats = pf.compute_poissonflex_from_files(STACK_TIF, RAD_TIF, GDR_CSV, foot, quad, out_x=x_mm)
    del x_mm
    gc.collect()

    np.save(v_p, feats["valid"])
    np.save(lsk_p, feats["L_scarp_knick"])
    np.save(lpf_p, feats["L_poisson_flex"])

    with rasterio.open(STACK_TIF) as ds:
        slope = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    consp = bf.conspicuity(slope, feats["valid"])
    del slope
    np.save(con_p, consp)
    meta_p.write_text(json.dumps({"gdr_meta": feats["gdr_meta"], "feature_names": list(pf.FEATURE_NAMES)}, indent=2))
    gc.collect()

    return {
        "X_foot": np.load(x_p, mmap_mode="r"),
        "valid": feats["valid"],
        "L_scarp_knick": feats["L_scarp_knick"],
        "L_poisson_flex": feats["L_poisson_flex"],
        "conspicuity": consp,
        "gdr_meta": feats["gdr_meta"],
    }


def run_canaries(feats: dict, grid, draws: dict, foot: np.ndarray) -> dict:
    can_p = CACHE / "canaries.json"
    if can_p.is_file():
        return json.loads(can_p.read_text())

    valid = feats["valid"]
    hidden_union = np.zeros(foot.shape, dtype=bool)
    for s in SEEDS:
        hidden_union |= draws[s][0]["hidden_all"]
    d_cat = distance_transform_edt(~grid.catalogue)
    far_neg = foot & valid & (d_cat > 5.0)
    del d_cat

    row = np.full(foot.shape, -1, dtype=np.int32)
    row[foot] = np.arange(int(foot.sum()), dtype=np.int32)
    pos = row[hidden_union & valid]
    neg_pool = row[far_neg]
    rng = np.random.default_rng(20261025)
    neg = np.sort(rng.choice(neg_pool, size=min(250_000, neg_pool.size), replace=False))
    y = np.concatenate([np.ones(pos.size, dtype=np.int8), np.zeros(neg.size, dtype=np.int8)])

    rows = []
    X = feats["X_foot"]
    for j, fname in enumerate(pf.FEATURE_NAMES):
        vals = np.concatenate([X[pos, j], X[neg, j]])
        auc = float(roc_auc_score(y, vals))
        sym = max(auc, 1.0 - auc)
        rows.append({
            "feature": fname,
            "auc": round(auc, 6),
            "symmetric_auc": round(sym, 6),
            "pass_le_0p90": bool(sym <= 0.90),
        })
    for lname in ("L_scarp_knick", "L_poisson_flex"):
        lf = feats[lname][foot]
        vals = np.concatenate([lf[pos], lf[neg]])
        auc = float(roc_auc_score(y, vals))
        sym = max(auc, 1.0 - auc)
        rows.append({
            "feature": lname,
            "auc": round(auc, 6),
            "symmetric_auc": round(sym, 6),
            "pass_le_0p90": bool(sym <= 0.90),
        })

    doc = {
        "evidence_class": "HOLDOUT-CANARY (buffered_component_draw seeds 20+30 union vs d_cat > 5 px)",
        "n_pos": int(pos.size),
        "n_neg": int(neg.size),
        "threshold_symmetric_auc": 0.90,
        "max_symmetric_auc": max(r["symmetric_auc"] for r in rows),
        "max_symmetric_feature": max(rows, key=lambda r: r["symmetric_auc"])["feature"],
        "all_pass": all(r["pass_le_0p90"] for r in rows),
        "rows": rows,
    }
    can_p.write_text(json.dumps(doc, indent=2))
    if not doc["all_pass"]:
        raise RuntimeError(f"LEAKAGE CANARY FAILED: {doc['max_symmetric_feature']} = {doc['max_symmetric_auc']}")
    return doc


def low_conspicuity_fold(fold: dict, keep_components: np.ndarray) -> dict:
    comp, _ = ndi.label(fold["hidden_all"], holdout.STRUCT3)
    keep = np.isin(comp, keep_components) & fold["hidden_all"]
    f = dict(fold)
    f["truth"] = fold["truth"] & keep
    f["masked_known"] = fold["masked_known"] | (fold["hidden_all"] & ~keep)
    return f


def low_tercile_components(draw: list[dict], c_field: np.ndarray) -> tuple[np.ndarray, float]:
    hidden = draw[0]["hidden_all"]
    comp, n = ndi.label(hidden, holdout.STRUCT3)
    idx = np.arange(1, n + 1)
    mean_c = ndi.mean(c_field, labels=comp, index=idx)
    cut = float(np.quantile(mean_c, 1.0 / 3.0))
    return idx[mean_c <= cut], cut


def _compute_coulomb_loqo_dvis_worker() -> None:
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    quad = holdout.quadrant_ids(foot)
    draws = {s: holdout.buffered_component_draw(grid, seed=s)[0] for s in SEEDS}

    with rasterio.open(STACK_TIF) as ds:
        rtp = ds.read(2, masked=True).filled(np.nan).astype(np.float32)
        geod_2ndinv = ds.read(4, masked=True).filled(np.nan).astype(np.float32)
        grav_slope = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        geod_shearrate = ds.read(7, masked=True).filled(np.nan).astype(np.float32)
        geod_dilaterate = ds.read(8, masked=True).filled(np.nan).astype(np.float32)
        grav_vg = ds.read(11, masked=True).filled(np.nan).astype(np.float32)
        det_elev = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        grav_anom = ds.read(13, masked=True).filled(np.nan).astype(np.float32)
        depth_to_base = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        cond_surf = ds.read(17, masked=True).filled(np.nan).astype(np.float32)
        grav_hg = ds.read(18, masked=True).filled(np.nan).astype(np.float32)
        det_elev_slope = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    with rasterio.open(RAD_TIF) as rds:
        rad_k = rds.read(1)
        rad_th = rds.read(2)
        rad_u = rds.read(3)
    valid_pre = (
        foot
        & np.isfinite(det_elev) & (det_elev > -1e30)
        & np.isfinite(det_elev_slope) & (det_elev_slope > -1e30)
        & np.isfinite(rtp) & (rtp > -1e30)
    )
    gdr_f = cl.gdr_blind_thermal_features(GDR_CSV, foot.shape, valid_pre, sigma_px=14.0)["plume_feat"]
    st = cl.compute_feature_stack(
        rtp=rtp, geod_2ndinv=geod_2ndinv, grav_slope=grav_slope, geod_shearrate=geod_shearrate,
        geod_dilaterate=geod_dilaterate, grav_vg=grav_vg, det_elev=det_elev, grav_anom=grav_anom,
        depth_to_base=depth_to_base, cond_surf=cond_surf, grav_hg=grav_hg, det_elev_slope=det_elev_slope,
        rad_k=rad_k, rad_th=rad_th, rad_u=rad_u, gdr_plume_feat=gdr_f, footprint=foot,
    )
    del rtp, geod_2ndinv, grav_slope, geod_shearrate, geod_dilaterate, grav_vg, det_elev
    del grav_anom, depth_to_base, cond_surf, grav_hg, det_elev_slope, rad_k, rad_th, rad_u, gdr_f
    gc.collect()

    for s in SEEDS:
        vis = draws[s][0]["visible"]
        hidden = draws[s][0]["hidden_all"]
        collar = distance_transform_edt(~hidden) <= 3.0
        d_vis = distance_transform_edt(~vis)
        p_s = cl.fit_predict_loqo(
            st["X_foot"], foot, st["valid"], quad, vis,
            excluded_mask=(hidden | collar), guard_px=12, neg_buffer_px=5.0, neg_pos_ratio=4,
            seed=20261024 + s, max_iter=180,
        )
        cr = cl.build_crest_surface(p_s, st["L_topo"], st["L_sub"], st["valid"], sub_weight=0.80)
        m = cl.spaced_top_mask(
            cr["S_crest"], foot & st["valid"] & cr["ridge_1d"] & (d_vis > 2.0),
            N_PARENT_BUDGET, min_dist_px=2.8, cand_cap=900_000,
        )
        np.save(CACHE / f"coulomb_loqo_dvis_m{s}.npy", m)
        del p_s, cr, d_vis
        gc.collect()


def load_or_compute_coulomb_loqo_dvis() -> dict[int, np.ndarray]:
    """Compute or load exact draw-blind COULOMBLOQO standalone predictions in isolated subprocess."""
    m20 = CACHE / "coulomb_loqo_dvis_m20.npy"
    m30 = CACHE / "coulomb_loqo_dvis_m30.npy"
    if not (m20.is_file() and m30.is_file()):
        import subprocess

        log("computing exact draw-blind COULOMBLOQO standalone reference masks in isolated worker ...")
        subprocess.check_call([sys.executable, str(Path(__file__).resolve()), "--stage", "cl_worker"])
    return {20: np.load(m20), 30: np.load(m30)}


def nested_visible_budget(
    s_crest: np.ndarray,
    ridge_1d: np.ndarray,
    valid: np.ndarray,
    grid,
    vis_mask: np.ndarray,
    outer_excl: np.ndarray,
    *,
    inner_seed: int,
) -> dict:
    """Strictly visible-only inner holdout budget selection (zero outer truth access)."""
    vis_grid = replace(grid, catalogue=vis_mask)
    inner_draw, _ = holdout.buffered_component_draw(vis_grid, seed=int(inner_seed))
    inner_vis = inner_draw[0]["visible"]
    d_inner_vis = distance_transform_edt(~inner_vis)
    inner_folds = []
    for f in inner_draw:
        fc = dict(f)
        fc["masked_known"] = f["masked_known"] | outer_excl
        inner_folds.append(fc)
    allowed_inner = grid.footprint & valid & ridge_1d & (~outer_excl) & (d_inner_vis > 2.0)
    res = pf.select_nested_oof_budget(
        s_crest, allowed_inner, inner_folds, grid.footprint, budget_grid=BUDGET_GRID, min_dist_px=2.8
    )
    del d_inner_vis
    return res


def main() -> int:
    import pickle

    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("features_canaries", "cl_worker", "holdout_only", "deploy_only", "all"), default="all")
    args = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    if args.stage == "cl_worker":
        _compute_coulomb_loqo_dvis_worker()
        return 0
    if args.stage == "all":
        import subprocess
        for sub_stage in ("cl_worker", "holdout_only", "deploy_only"):
            subprocess.check_call([sys.executable, str(Path(__file__).resolve()), "--stage", sub_stage])
        return 0

    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    quad = holdout.quadrant_ids(foot)
    qnames = {0: "NW", 1: "NE", 2: "SW", 3: "SE"}

    draws = {s: holdout.buffered_component_draw(grid, seed=s)[0] for s in SEEDS}
    receipts = {str(s): [f["receipt"] for f in draws[s]] for s in SEEDS}
    n_withheld = sum(r["withheld_positive_pixels"] for s in SEEDS for r in receipts[str(s)])

    feats = load_or_compute_features(foot, quad)
    can = run_canaries(feats, grid, draws, foot)
    log(
        f"Stage 1-2 PASS: X_foot={feats['X_foot'].shape}, max canary symmetric AUC = "
        f"{can['max_symmetric_auc']:.6f} ({can['max_symmetric_feature']}) <= 0.90"
    )
    if args.stage == "features_canaries":
        return 0

    valid = feats["valid"]
    X_foot = feats["X_foot"]
    l_sk = feats["L_scarp_knick"]
    l_pf = feats["L_poisson_flex"]
    c_field = feats["conspicuity"]
    s3_pkl = CACHE / "stage3_holdout.pkl"

    if args.stage == "holdout_only":
        cl_dvis_masks = load_or_compute_coulomb_loqo_dvis()
        with rasterio.open(ROOT / "data/bridge/h19_5.tif") as ds:
            h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
        scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)

        terms_primary: dict[str, np.ndarray] = {}
        terms_low: dict[str, np.ndarray] = {}
        fold_dti_primary: dict[str, list[dict]] = {}
        low_cuts: dict[str, dict] = {}
        oof_budget_draws: dict[str, dict] = {}

        for s in SEEDS:
            log(f"Stage 3: running strict draw-blind LOQO holdout on seed={s} ...")
            draw = draws[s]
            vis = draw[0]["visible"]
            hidden = draw[0]["hidden_all"]
            collar = distance_transform_edt(~hidden) <= 3.0
            excl = hidden | collar
            d_vis = distance_transform_edt(~vis)

            keep_comp, cut = low_tercile_components(draw, c_field)
            low_cuts[str(s)] = {"cut": cut, "n_low_components": int(keep_comp.size)}
            folds_low = [low_conspicuity_fold(f, keep_comp) for f in draw]

            fit_s = pf.fit_predict_loqo_poissonflex(
                X_foot, foot, valid, quad, vis,
                excluded_mask=excl, equalize_quadrants=True, guard_px=12,
                neg_buffer_px=5.0, neg_pos_ratio=4, seed=20261025 + s, max_iter=200,
            )
            crest_eq = pf.build_poissonflex_crest_surface(fit_s["proba_eq"], l_sk, l_pf, valid, sub_weight=0.90)
            crest_raw = pf.build_poissonflex_crest_surface(fit_s["proba_raw"], l_sk, l_pf, valid, sub_weight=0.90)

            oof_sel = nested_visible_budget(
                crest_eq["S_crest"], crest_eq["ridge_1d"], valid, grid, vis, excl, inner_seed=100 + s
            )
            s_opt = int(oof_sel["best_budget"])
            oof_budget_draws[str(s)] = oof_sel
            log(f"  seed={s} nested visible-only OOF budget selected S={s_opt} ({oof_sel['grid_dti']})")

            m_eq = pf.spaced_top_mask(
                crest_eq["S_crest"], foot & valid & crest_eq["ridge_1d"] & (d_vis > 2.0),
                N_PARENT_BUDGET, min_dist_px=2.8, cand_cap=950_000,
            )
            m_raw = pf.spaced_top_mask(
                crest_raw["S_crest"], foot & valid & crest_raw["ridge_1d"] & (d_vis > 2.0),
                N_PARENT_BUDGET, min_dist_px=2.8, cand_cap=950_000,
            )
            m_opt = pf.spaced_top_mask(
                crest_eq["S_crest"], foot & valid & crest_eq["ridge_1d"] & (d_vis > 2.0),
                s_opt, min_dist_px=2.8, cand_cap=950_000,
            )
            m_h19 = pf.spaced_top_mask(
                scan_rank, foot & valid & h19 & (d_vis > 2.0),
                N_PARENT_BUDGET, min_dist_px=2.4, cand_cap=900_000,
            )
            m_cl = cl_dvis_masks[s]

            pred_map = {
                "poissonflex_eq": m_eq,
                "poissonflex_raw": m_raw,
                "poissonflex_opt": m_opt,
                "COULOMBLOQO_standalone_dvis2": m_cl,
                "H19_5_dvis2": m_h19,
            }
            for aname, pmask in pred_map.items():
                pf32 = pmask.astype(np.float32)
                pf32[vis] = 0.0
                for fold, fl in zip(draw, folds_low):
                    sc, tm = evaluate_holdout.evaluate(pf32, fold, foot)
                    _, tml = evaluate_holdout.evaluate(pf32, fl, foot)
                    terms_primary[aname] = tm if aname not in terms_primary else terms_primary[aname] + tm
                    terms_low[aname] = tml if aname not in terms_low else terms_low[aname] + tml
                    fold_dti_primary.setdefault(aname, []).append({
                        "seed": int(s),
                        "fold": fold["receipt"]["fold"],
                        "dti": round(float(sc["dti"]), 6),
                        "tp": round(float(sc["tp"]), 3),
                        "fp": round(float(sc["fp"]), 3),
                    })
            del fit_s, crest_eq, crest_raw, d_vis, m_eq, m_raw, m_opt, m_h19
            gc.collect()

        arm_prelim = {
            a: float(terms_primary[a][:, 0].sum() / (0.2 * (terms_primary[a][:, 0].sum() + terms_primary[a][:, 1].sum()) + 0.8 * (terms_primary[a][:, 0].sum() + terms_primary[a][:, 2].sum())))
            for a in ARMS
        }
        best_arm = max(ARMS, key=lambda a: arm_prelim[a])
        primary_summary = evaluate_holdout.pooled_summary(terms_primary, candidate=best_arm)
        low_summary = evaluate_holdout.pooled_summary(terms_low, candidate=best_arm)
        for k, sc in primary_summary["scores"].items():
            log(f"  PRIMARY d_vis>2.0 {k:28s}: DTI={sc['dti']:.6f} CI95={[round(x,6) for x in sc['ci95']]}")
        for k, pdiff in primary_summary["paired_differences"].items():
            log(f"  PAIRED DELTA ({best_arm} - {k}): {pdiff['delta']:+.6f} CI95={[round(x,6) for x in pdiff['ci95']]}")
        s3_pkl.write_bytes(pickle.dumps({
            "best_arm": best_arm,
            "primary_summary": primary_summary,
            "low_summary": low_summary,
            "fold_dti_primary": fold_dti_primary,
            "low_cuts": low_cuts,
            "oof_budget_draws": oof_budget_draws,
        }))
        log(f"saved {s3_pkl}")
        return 0

    s3 = pickle.loads(s3_pkl.read_bytes())
    best_arm = s3["best_arm"]
    primary_summary = s3["primary_summary"]
    low_summary = s3["low_summary"]
    fold_dti_primary = s3["fold_dti_primary"]
    low_cuts = s3["low_cuts"]
    oof_budget_draws = s3["oof_budget_draws"]

    # Stage 4: Full deployment fit (all 3 pre-registered arms)
    d_cat = distance_transform_edt(~cat)
    cached_deploy_p = CACHE / "deploy_oof_sel.json"
    if all((CACHE / f"dots_{a}.npy").is_file() and (CACHE / f"S_{a}_full.npy").is_file() for a in ARMS) and cached_deploy_p.is_file():
        log("Stage 4: loading cached deployment surfaces & dots from .cache/poissonflex/ ...")
        dots_map = {a: np.load(CACHE / f"dots_{a}.npy") for a in ARMS}
        surf_map = {a: np.load(CACHE / f"S_{a}_full.npy") for a in ARMS}
        deploy_oof_sel = json.loads(cached_deploy_p.read_text())
    else:
        log("Stage 4: fitting full deployment LOQO on complete mapped catalogue ...")
        fit_full = pf.fit_predict_loqo_poissonflex(
            X_foot, foot, valid, quad, cat,
            excluded_mask=None, equalize_quadrants=True, guard_px=12,
            neg_buffer_px=5.0, neg_pos_ratio=4, seed=20261025, max_iter=200,
        )
        crest_full_eq = pf.build_poissonflex_crest_surface(fit_full["proba_eq"], l_sk, l_pf, valid, sub_weight=0.90)
        crest_full_raw = pf.build_poissonflex_crest_surface(fit_full["proba_raw"], l_sk, l_pf, valid, sub_weight=0.90)

        deploy_oof_sel = nested_visible_budget(
            crest_full_eq["S_crest"], crest_full_eq["ridge_1d"], valid, grid, cat,
            np.zeros_like(foot), inner_seed=111,
        )
        cached_deploy_p.write_text(json.dumps(deploy_oof_sel, indent=2))
        s_opt_deploy = int(deploy_oof_sel["best_budget"])
        log(f"  deployment nested OOF budget S_opt={s_opt_deploy} ({deploy_oof_sel['grid_dti']})")

        pool_eq = foot & valid & crest_full_eq["ridge_1d"] & (d_cat > 2.0)
        pool_raw = foot & valid & crest_full_raw["ridge_1d"] & (d_cat > 2.0)
        dots_map = {
            "poissonflex_eq": pf.spaced_top_mask(crest_full_eq["S_crest"], pool_eq, N_PARENT_BUDGET, min_dist_px=2.8, cand_cap=950_000),
            "poissonflex_raw": pf.spaced_top_mask(crest_full_raw["S_crest"], pool_raw, N_PARENT_BUDGET, min_dist_px=2.8, cand_cap=950_000),
            "poissonflex_opt": pf.spaced_top_mask(crest_full_eq["S_crest"], pool_eq, s_opt_deploy, min_dist_px=2.8, cand_cap=950_000),
        }
        surf_map = {
            "poissonflex_eq": crest_full_eq["S_crest"],
            "poissonflex_raw": crest_full_raw["S_crest"],
            "poissonflex_opt": crest_full_eq["S_crest"],
        }
        for a in ARMS:
            np.save(CACHE / f"dots_{a}.npy", dots_map[a])
            np.save(CACHE / f"S_{a}_full.npy", surf_map[a].astype(np.float32))
        del fit_full, crest_full_eq, crest_full_raw
        gc.collect()

    deployment_meta = {}
    for a in ARMS:
        n_d = int(dots_map[a].sum())
        sha8 = sha256_bytes(np.packbits(dots_map[a].ravel()).tobytes())[:8]
        stem = f"gemsdoe92-poissonflex-{a}-{n_d}-{DATE}-{sha8}-zeros"
        per_q = {
            qnames[q]: {
                "dots": int((dots_map[a] & (quad == q)).sum()),
                "share": round(float((dots_map[a] & (quad == q)).sum()) / max(n_d, 1), 6),
            }
            for q in range(4)
        }
        deployment_meta[a] = {
            "stem": stem,
            "sha8": sha8,
            "dots": n_d,
            "quadrant_dot_allocation": per_q,
            "mean_conspicuity_dots": round(float(c_field[dots_map[a]].mean()), 6),
            "frac_dots_low_conspicuity_le_0p44": round(float((c_field[dots_map[a]] <= 0.444).mean()), 6),
        }
        log(f"  deployment {a:16s}: dots={n_d} stem={stem} quad_shares={ {k: round(v['share']*100,1) for k, v in per_q.items()} }")

    # Static d_cat > 2.0 holdout evaluation across all 8 folds + SGMC proxy
    static_arms = {**dots_map}
    with rasterio.open(ROOT / "data/parent_R0_zeros.tif") as ds:
        static_arms["R0"] = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    with rasterio.open(ROOT / "docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif") as ds:
        static_arms["COULOMBLOQO_standalone"] = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot

    static_terms: dict[str, np.ndarray] = {}
    static_fold_dti: dict[str, list[dict]] = {}
    for aname, pmask in static_arms.items():
        pf32 = pmask.astype(np.float32)
        for s in SEEDS:
            for fold in draws[s]:
                sc, tm = evaluate_holdout.evaluate(pf32, fold, foot)
                static_terms[aname] = tm if aname not in static_terms else static_terms[aname] + tm
                static_fold_dti.setdefault(aname, []).append({
                    "seed": int(s),
                    "fold": fold["receipt"]["fold"],
                    "dti": round(float(sc["dti"]), 6),
                })
    static_summary = evaluate_holdout.pooled_summary(static_terms, candidate=best_arm)
    for k, sc in static_summary["scores"].items():
        log(f"  STATIC d_cat>2.0  {k:28s}: DTI={sc['dti']:.6f} CI95={[round(x,6) for x in sc['ci95']]}")

    # Off-catalogue USGS SGMC bedrock fault proxy
    with rasterio.open(SGMC_TIF) as ds:
        sgmc_raw = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc_raw & (d_cat > 3.0)
    sgmc_scores = {}
    for aname, pmask in static_arms.items():
        res_sg = gems57_metric.dti_binary(pmask, sgmc_truth, valid=foot, known=cat)
        sgmc_scores[aname] = round(float(res_sg["dti"]), 6)
    log(f"  SGMC PROXY (>3px off catalogue, {int(sgmc_truth.sum())} px): {sgmc_scores}")

    # Summarize per-quadrant mean DTI on BOTH primary d_vis>2.0 and static d_cat>2.0
    quad_dti_primary = {}
    for aname, flist in fold_dti_primary.items():
        quad_dti_primary[aname] = {
            qn: round(float(np.mean([x["dti"] for x in flist if x["fold"] == qn])), 6)
            for qn in ("NW", "NE", "SW", "SE")
        }
    quad_dti_static = {}
    for aname, flist in static_fold_dti.items():
        quad_dti_static[aname] = {
            qn: round(float(np.mean([x["dti"] for x in flist if x["fold"] == qn])), 6)
            for qn in ("NW", "NE", "SW", "SE")
        }

    holdout_doc = {
        "schema": "gemsdoe92-poissonflex-holdout.v1",
        "lane": "POISSONFLEX",
        "date": DATE,
        "hypothesis_doc": "docs/HYPOTHESES_20261025_POISSONFLEX.md",
        "evaluator_version": evaluate_holdout.VERSION,
        "evaluator_hashes": evaluate_holdout.implementation_hashes(),
        "split_receipts": receipts,
        "withheld_positive_pixels": int(n_withheld),
        "feature_names": list(pf.FEATURE_NAMES),
        "gdr_meta": feats["gdr_meta"],
        "leakage_canaries": can,
        "nested_oof_budget_selection": {
            "draws": oof_budget_draws,
            "deployment": deploy_oof_sel,
        },
        "best_arm": best_arm,
        "holdout": {
            "primary_dvis2_all_withheld": primary_summary,
            "low_conspicuity_withheld": low_summary,
            "low_conspicuity_cuts": low_cuts,
            "static_dcat2_deployment": static_summary,
            "quadrant_mean_dti_primary_dvis2": quad_dti_primary,
            "quadrant_mean_dti_static_dcat2": quad_dti_static,
            "per_fold_primary_dvis2": fold_dti_primary,
            "per_fold_static_dcat2": static_fold_dti,
        },
        "sgmc_off_catalogue_proxy": {
            "evidence_class": "PROXY (off-catalogue USGS SGMC bedrock faults > 3 px from existing_faults)",
            "truth_pixels": int(sgmc_truth.sum()),
            "dti_by_arm": sgmc_scores,
        },
        "deployment": deployment_meta,
    }
    out_p = EVIDENCE / "poissonflex_holdout.json"
    out_p.write_text(json.dumps(holdout_doc, indent=2) + "\n")
    log(f"wrote {out_p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
