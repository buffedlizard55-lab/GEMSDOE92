#!/usr/bin/env python3
"""FAULTNET lane: holdout evaluation (stage ``holdout``) and deployment (stage ``deploy``).

Pre-registration: docs/HYPOTHESES_20261025_FAULTNET.md (frozen arms netctx/netdens/netfar).
Shared tools only: gems57.holdout.buffered_component_draw, gems57.evaluate_holdout,
gems.coulomb_loqo (stack/LOQO/crest/spaced dots), gems57.submission_writer.

Stages are separate processes to stay inside the 3 GB sandbox:
  python scripts/run_faultnet.py holdout   -> .cache/faultnet/holdout_terms.npz + evidence/faultnet_holdout.json
  python scripts/run_faultnet.py deploy    -> .cache/faultnet/dots_<arm>.npy
"""
from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems import coulomb_loqo as cl  # noqa: E402
from gems import faultnet as fn  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa: E402

INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE = ROOT / ".cache" / "faultnet"
EVIDENCE = ROOT / "evidence"
N_DOTS = 37_654
SPACING = 2.8
SEEDS = (20, 30)
N_PHYS = len(cl.FEATURE_NAMES)                       # 24
CTX_COLS = tuple(range(N_PHYS, N_PHYS + len(fn.CONTEXT_NAMES)))
ARM_COLS = {
    "netctx": tuple(range(N_PHYS)) + CTX_COLS,
    "netdens": tuple(range(N_PHYS)) + (N_PHYS + 1, N_PHYS + 2, N_PHYS + 3),
    "control_COULOMBLOQO": tuple(range(N_PHYS)),
}
EMIT_MIN_D = {"netctx": 2.0, "netdens": 2.0, "netfar": 4.0, "control_COULOMBLOQO": 2.0}


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_stack(grid):
    band_ids = (2, 4, 5, 7, 8, 11, 12, 13, 15, 17, 18, 19)
    b = {}
    with rasterio.open(INPUTS / "training_features.tif") as ds:
        for i in band_ids:
            a = ds.read(i).astype(np.float32)
            a[(~np.isfinite(a)) | (a <= -1e20)] = np.nan
            b[i] = a
    with rasterio.open(INPUTS / "external" / "geodawn_rad_u8.tif") as ds:
        rk, rth, ru = ds.read(1), ds.read(2), ds.read(3)
    foot = grid.footprint
    valid_base = foot & np.isfinite(b[12]) & np.isfinite(b[19]) & np.isfinite(b[2])
    gdr = cl.gdr_blind_thermal_features(INPUTS / "external" / "gdr_wellspring_in_footprint.csv",
                                        foot.shape, valid_base, sigma_px=14.0)
    st = cl.compute_feature_stack(
        rtp=b[2], geod_2ndinv=b[4], grav_slope=b[5], geod_shearrate=b[7], geod_dilaterate=b[8],
        grav_vg=b[11], det_elev=b[12], grav_anom=b[13], depth_to_base=b[15], cond_surf=b[17],
        grav_hg=b[18], det_elev_slope=b[19], rad_k=rk, rad_th=rth, rad_u=ru,
        gdr_plume_feat=gdr["plume_feat"], footprint=foot)
    det_elev = b[12]
    del b, rk, rth, ru, gdr, valid_base
    gc.collect()
    n = st["X_foot"].shape[0]
    X = np.zeros((n, N_PHYS + len(fn.CONTEXT_NAMES)), np.float32)
    X[:, :N_PHYS] = st["X_foot"]
    del st["X_foot"]
    gc.collect()
    return X, st["valid"], st["L_topo"], st["L_sub"], det_elev


def fill_context(X, foot, visible, det_elev, valid):
    F = fn.context_fields(visible, det_elev, valid)
    for j, name in enumerate(fn.CONTEXT_NAMES):
        X[:, N_PHYS + j] = F[name][foot]
    return F


def surface_and_dots(proba, L_topo, L_sub, valid, foot, d_ref, arms_min_d):
    c = cl.build_crest_surface(proba, L_topo, L_sub, valid, sub_weight=0.80)
    out = {}
    for name, mind in arms_min_d.items():
        out[name] = cl.spaced_top_mask(c["S_crest"], foot & valid & c["ridge_1d"] & (d_ref > mind),
                                       N_DOTS, min_dist_px=SPACING, cand_cap=900_000)
    return c["S_crest"], out


def stage_holdout() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    quad = hold_mod.quadrant_ids(foot)
    log("loading COULOMBLOQO 24-feature stack + context slots")
    X, valid, L_topo, L_sub, det_elev = load_stack(grid)
    with rasterio.open(INPUTS / "lineage" / "calib_h195_01922.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)
    foot_row = np.full(foot.shape, -1, np.int32)
    foot_row[foot] = np.arange(int(foot.sum()), dtype=np.int32)

    arms = ["netctx", "netdens", "netfar", "control_COULOMBLOQO", "control_H19_5"]
    terms = {a: None for a in arms}
    per_fold = {a: [] for a in arms}
    canaries = []
    receipts = []
    for seed in SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        receipts += [f["receipt"] for f in folds]
        vis, hid = folds[0]["visible"], folds[0]["hidden_all"]
        excl = hid | (distance_transform_edt(~hid) <= 3.0)
        d_vis = distance_transform_edt(~vis)
        log(f"seed {seed}: context fields from VISIBLE catalogue only")
        fill_context(X, foot, vis, det_elev, valid)
        # protocol rule 4: single-feature canaries on this draw (all 29 columns)
        rng = np.random.default_rng(520810 + seed)
        ys, ix = [], []
        for f in folds:
            pos = np.flatnonzero(f["truth"] & foot)
            neg = np.flatnonzero(f["region"] & foot & ~cat)
            neg = rng.choice(neg, min(len(neg), 2 * len(pos)), replace=False)
            ix += [pos, neg]
            ys += [np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)]
        y = np.concatenate(ys)
        rows = foot_row.ravel()[np.concatenate(ix)]
        names = list(cl.FEATURE_NAMES) + list(fn.CONTEXT_NAMES)
        for j, nm in enumerate(names):
            v = X[rows, j]
            a = 0.5 if np.ptp(v) == 0 else float(roc_auc_score(y, v))
            canaries.append(dict(seed=seed, feature=nm, auc=round(a, 6), symmetric_auc=round(max(a, 1 - a), 6)))
        worst = max(c["symmetric_auc"] for c in canaries if c["seed"] == seed)
        log(f"seed {seed}: canary max symmetric AUC = {worst:.4f}")
        if worst > 0.90:
            raise SystemExit(f"LEAKAGE CANARY TRIPPED ({worst:.4f} > 0.90): stop")

        preds = {}
        for model in ("netctx", "netdens", "control_COULOMBLOQO"):
            log(f"seed {seed}: LOQO fit {model} ({len(ARM_COLS[model])} cols)")
            p = cl.fit_predict_loqo(X, foot, valid, quad, vis, feature_cols=ARM_COLS[model],
                                    excluded_mask=excl, guard_px=12, neg_buffer_px=5.0,
                                    seed=20261024 + seed)
            emit = {"netctx": {"netctx": 2.0, "netfar": 4.0}}.get(model, {model: 2.0})
            _, dots = surface_and_dots(p, L_topo, L_sub, valid, foot, d_vis, emit)
            preds.update(dots)
            del p
            gc.collect()
        preds["control_H19_5"] = cl.spaced_top_mask(scan_rank, foot & valid & h19 & (d_vis > 2.0),
                                                   N_DOTS, min_dist_px=2.4)
        for a in arms:
            pr = preds[a].astype(np.float32)
            pr[vis] = 0.0
            for f in folds:
                sc, tm = evaluate_holdout.evaluate(pr, f, foot)
                terms[a] = tm if terms[a] is None else terms[a] + tm
                per_fold[a].append(dict(seed=seed, fold=f["name"], dti=round(float(sc["dti"]), 6),
                                        tpw=round(float(sc["tpw"]), 3), fpw=round(float(sc["fpw"]), 3),
                                        n_truth=int(sc["n_truth"])))
        del preds
        gc.collect()
        log(f"seed {seed} done ({time.time()-t0:.0f}s)")

    np.savez(CACHE / "holdout_terms.npz", **terms)
    summaries = {}
    for cand in ("netctx", "netdens", "netfar"):
        summaries[cand] = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate=cand)
    s0 = summaries["netctx"]["scores"]
    for k, v in sorted(s0.items(), key=lambda kv: -kv[1]["dti"]):
        log(f"  {k:22s} HOLDOUT-DTI {v['dti']:.6f} CI {v['ci95'][0]:.6f}-{v['ci95'][1]:.6f} (withheld {v['withheld_positive_pixels']})")
    doc = dict(schema="gemsdoe92-faultnet-holdout-v1", evidence_class="HOLDOUT-DTI",
               evaluator_version=evaluate_holdout.VERSION,
               instrument="strict draw-blind fold-visible (d_visible > 2.0 emission; netfar d_visible > 4.0)",
               seeds=list(SEEDS), n_dots=N_DOTS, spacing_px=SPACING, arm_columns={k: list(v) for k, v in ARM_COLS.items()},
               feature_names=list(cl.FEATURE_NAMES) + list(fn.CONTEXT_NAMES),
               scores=s0, paired_by_candidate={c: summaries[c]["paired_differences"] for c in summaries},
               bootstrap=summaries["netctx"]["bootstrap"], implementation_sha256=summaries["netctx"]["implementation_sha256"],
               per_fold=per_fold, canaries=canaries, fold_receipts=receipts, runtime_s=round(time.time() - t0, 1))
    (EVIDENCE / "faultnet_holdout.json").write_text(json.dumps(doc, indent=1))
    log(f"wrote evidence/faultnet_holdout.json ({time.time()-t0:.0f}s)")
    return 0


def stage_deploy() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    quad = hold_mod.quadrant_ids(foot)
    X, valid, L_topo, L_sub, det_elev = load_stack(grid)
    d_cat = distance_transform_edt(~cat)
    log("deploy: context fields from FULL catalogue")
    fill_context(X, foot, cat, det_elev, valid)
    for model, emit in (("netctx", {"netctx": 2.0, "netfar": 4.0}), ("netdens", {"netdens": 2.0})):
        log(f"deploy: LOQO fit {model}")
        p = cl.fit_predict_loqo(X, foot, valid, quad, cat, feature_cols=ARM_COLS[model],
                                guard_px=12, neg_buffer_px=5.0, seed=20261025)
        S, dots = surface_and_dots(p, L_topo, L_sub, valid, foot, d_cat, emit)
        np.save(CACHE / f"S_{model}.npy", S)
        for a, m in dots.items():
            np.save(CACHE / f"dots_{a}.npy", m)
            log(f"  {a}: dots={int(m.sum())} on_cat={int((m & cat).sum())} min_dcat={float(d_cat[m].min()):.2f}")
        del p, S
        gc.collect()
    log(f"deploy done ({time.time()-t0:.0f}s)")
    return 0


def stage_farcontrol() -> int:
    """Emission-matched control for netfar: COULOMBLOQO with the same d_visible > 4 emission.

    Not an experiment arm (no new hypothesis): it separates the context-feature effect from the
    emission-halo effect, because the instrument's 3 px context collar puts every withheld truth
    pixel > 3 px from the visible catalogue by construction.
    """
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    quad = hold_mod.quadrant_ids(foot)
    X, valid, L_topo, L_sub, det_elev = load_stack(grid)
    z = dict(np.load(CACHE / "holdout_terms.npz"))
    tm_far = None
    per_fold = []
    for seed in SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        vis, hid = folds[0]["visible"], folds[0]["hidden_all"]
        excl = hid | (distance_transform_edt(~hid) <= 3.0)
        d_vis = distance_transform_edt(~vis)
        log(f"seed {seed}: LOQO fit control_COULOMBLOQO (far emission)")
        p = cl.fit_predict_loqo(X, foot, valid, quad, vis, feature_cols=ARM_COLS["control_COULOMBLOQO"],
                                excluded_mask=excl, guard_px=12, neg_buffer_px=5.0, seed=20261024 + seed)
        _, dots = surface_and_dots(p, L_topo, L_sub, valid, foot, d_vis, {"control_COULOMBLOQO_far": 4.0})
        pr = dots["control_COULOMBLOQO_far"].astype(np.float32)
        pr[vis] = 0.0
        for f in folds:
            sc, tm = evaluate_holdout.evaluate(pr, f, foot)
            tm_far = tm if tm_far is None else tm_far + tm
            per_fold.append(dict(seed=seed, fold=f["name"], dti=round(float(sc["dti"]), 6)))
        del p, dots, pr
        gc.collect()
    z["control_COULOMBLOQO_far"] = tm_far
    np.savez(CACHE / "holdout_terms.npz", **z)
    summ = evaluate_holdout.pooled_summary(z, draws=1000, seed=520810, candidate="netfar")
    doc = json.loads((EVIDENCE / "faultnet_holdout.json").read_text())
    doc["scores"] = summ["scores"]
    doc["paired_by_candidate"]["netfar"] = summ["paired_differences"]
    for cand in ("netctx", "netdens"):
        doc["paired_by_candidate"][cand] = evaluate_holdout.pooled_summary(
            z, draws=1000, seed=520810, candidate=cand)["paired_differences"]
    doc["per_fold"]["control_COULOMBLOQO_far"] = per_fold
    doc["emission_matched_control"] = dict(
        name="control_COULOMBLOQO_far", emission="d_visible > 4.0 (same as netfar)",
        reason="separates context-feature gain from emission-halo gain (3 px context collar => truth > 3 px from visible faults)",
        score=summ["scores"]["control_COULOMBLOQO_far"], netfar_minus_control_far=summ["paired_differences"]["control_COULOMBLOQO_far"])
    (EVIDENCE / "faultnet_holdout.json").write_text(json.dumps(doc, indent=1))
    s = summ["scores"]["control_COULOMBLOQO_far"]
    dd = summ["paired_differences"]["control_COULOMBLOQO_far"]
    log(f"control_COULOMBLOQO_far HOLDOUT-DTI {s['dti']:.6f} CI {s['ci95']}; netfar - control_far = {dd['delta']:+.6f} CI {dd['ci95']} ({time.time()-t0:.0f}s)")
    return 0


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "holdout"
    raise SystemExit({"holdout": stage_holdout, "deploy": stage_deploy, "farcontrol": stage_farcontrol}[stage]())
