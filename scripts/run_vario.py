#!/usr/bin/env python3
"""VARIO lane: stack / holdout / deploy stages (separate processes, 3 GB RAM).

Pre-registration: docs/HYPOTHESES_20261025_VARIO.md.
Shared tools only: gems.coulomb_loqo (24-feature stack, LOQO, crest, spaced
dots), gems.faultnet context fields, gems.vario new features,
gems57.holdout.buffered_component_draw, gems57.evaluate_holdout.

  .venv/bin/python scripts/run_vario.py stack    -> .cache/vario/X.npy (memmap-able) + fields
  .venv/bin/python scripts/run_vario.py holdout  -> evidence/vario_holdout.json + terms npz
  .venv/bin/python scripts/run_vario.py deploy   -> .cache/vario/dots_<arm>.npy, S_<arm>.npy
"""
from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt, gaussian_filter
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems import coulomb_loqo as cl  # noqa: E402
from gems import faultnet as fn  # noqa: E402
from gems import vario as vr  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa: E402

INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE = ROOT / ".cache" / "vario"
EVIDENCE = ROOT / "evidence"
N_DOTS = 37_654
SPACING = 2.8
SEEDS = (20, 30)
N_PHYS = len(cl.FEATURE_NAMES)                    # 24
CTX_COLS = tuple(range(N_PHYS, N_PHYS + len(fn.CONTEXT_NAMES)))        # 24..28
NEW_COLS = tuple(range(N_PHYS + len(fn.CONTEXT_NAMES),
                       N_PHYS + len(fn.CONTEXT_NAMES) + len(vr.NEW_FEATURE_NAMES)))  # 29..37
N_COLS = N_PHYS + len(fn.CONTEXT_NAMES) + len(vr.NEW_FEATURE_NAMES)    # 38
ARM_COLS = {
    "vario_full": tuple(range(N_PHYS)) + CTX_COLS + NEW_COLS,
    "vario_nctx": tuple(range(N_PHYS)) + NEW_COLS,
    "control_FAULTNET": tuple(range(N_PHYS)) + CTX_COLS,
    "control_COULOMBLOQO": tuple(range(N_PHYS)),
}
FEATURE_NAMES = list(cl.FEATURE_NAMES) + list(fn.CONTEXT_NAMES) + list(vr.NEW_FEATURE_NAMES)
SMOOTH_SIGMA = 1.85  # GEMSDOE32 live-scatter sigma (owner-model parameter, docs)


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _read_band(path: Path, band: int) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(band).astype(np.float32)
    a[(~np.isfinite(a)) | (a <= -1e20)] = np.nan
    return a


def stage_stack() -> int:
    from gems57.uniqueness import stop_historical_runner
    stop_historical_runner("run_vario:stage_stack")

    CACHE.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    tf = INPUTS / "training_features.tif"
    band_ids = (2, 4, 5, 7, 8, 11, 12, 13, 15, 17, 18, 19)
    b = {i: _read_band(tf, i) for i in band_ids}
    with rasterio.open(INPUTS / "external" / "geodawn_rad_u8.tif") as ds:
        rk, rth, ru = ds.read(1), ds.read(2), ds.read(3)
    valid_base = foot & np.isfinite(b[12]) & np.isfinite(b[19]) & np.isfinite(b[2])
    gdr = cl.gdr_blind_thermal_features(INPUTS / "external" / "gdr_wellspring_in_footprint.csv",
                                        foot.shape, valid_base, sigma_px=14.0)
    log("computing COULOMBLOQO 24-feature stack (shared gems.coulomb_loqo)")
    st = cl.compute_feature_stack(
        rtp=b[2], geod_2ndinv=b[4], grav_slope=b[5], geod_shearrate=b[7], geod_dilaterate=b[8],
        grav_vg=b[11], det_elev=b[12], grav_anom=b[13], depth_to_base=b[15], cond_surf=b[17],
        grav_hg=b[18], det_elev_slope=b[19], rad_k=rk, rad_th=rth, rad_u=ru,
        gdr_plume_feat=gdr["plume_feat"], footprint=foot)
    det_elev = b[12]
    del b, rk, rth, ru, gdr, valid_base
    gc.collect()
    valid = st["valid"]
    n = st["X_foot"].shape[0]
    Xpath = CACHE / "X.npy"
    X = np.lib.format.open_memmap(Xpath, mode="w+", dtype=np.float32, shape=(n, N_COLS))
    X[:, :N_PHYS] = st["X_foot"]
    X[:, N_PHYS:] = 0.0
    X.flush()
    np.save(CACHE / "valid.npy", valid)
    np.save(CACHE / "L_topo.npy", st["L_topo"])
    np.save(CACHE / "L_sub.npy", st["L_sub"])
    np.save(CACHE / "det_elev.npy", det_elev)
    del st, det_elev
    gc.collect()
    log("computing VARIO new features (semivariogram, MT change-point, topo10)")
    rtp = _read_band(tf, 2)
    sv = vr.semivariogram_features(rtp, valid)
    del rtp
    cond = _read_band(tf, 17)
    depth = _read_band(tf, 15)
    sv["mt_cp_constcover"] = vr.mt_changepoint_constcover(cond, depth, valid)
    del cond, depth
    slope19 = _read_band(tf, 19)
    t10 = vr.topo10_features(INPUTS / "external" / "topo_10m_derived_100m_u8.tif",
                             INPUTS / "external" / "dem10_chi_100m_i16.tif",
                             slope19, valid)
    del slope19
    fields = {**sv, **t10}
    del sv, t10
    for j, name in enumerate(vr.NEW_FEATURE_NAMES):
        arr = fields.pop(name)
        col = arr[foot].astype(np.float32)
        col = np.nan_to_num(col, nan=0.0, posinf=0.0, neginf=0.0)
        X[:, NEW_COLS[j]] = col
        stats = dict(min=float(col.min()), max=float(col.max()),
                     mean=float(col.mean()), p99=float(np.percentile(col, 99.0)))
        log(f"  new[{j}] {name}: {stats}")
        del arr, col
    X.flush()
    del X
    gc.collect()
    log(f"stack done: X {n}x{N_COLS} -> {Xpath} ({time.time()-t0:.0f}s)")
    return 0


def _load_X():
    return np.lib.format.open_memmap(CACHE / "X.npy", mode="r+")


def _fill_context(X, foot, visible, det_elev, valid):
    F = fn.context_fields(visible, det_elev, valid)
    for j, name in enumerate(fn.CONTEXT_NAMES):
        X[:, N_PHYS + j] = F[name][foot]
    if hasattr(X, "flush"):
        X.flush()
    return F


def _dots_from_proba(proba, L_topo, L_sub, valid, foot, d_ref, *, smooth=False, min_d=2.0):
    c = cl.build_crest_surface(proba, L_topo, L_sub, valid, sub_weight=0.80)
    surf = c["S_crest"]
    if smooth:
        surf = gaussian_filter(surf, SMOOTH_SIGMA).astype(np.float32)
        surf[~valid] = 0.0
    dots = cl.spaced_top_mask(surf, foot & valid & c["ridge_1d"] & (d_ref > min_d),
                              N_DOTS, min_dist_px=SPACING, cand_cap=900_000)
    return c["S_crest"], dots


# arm -> (model name for the LOQO fit, emission kwargs)
ARMS = {
    "vario_full": ("vario_full", dict()),
    "vario_smooth": ("vario_full", dict(smooth=True)),
    "vario_nctx": ("vario_nctx", dict()),
    "control_FAULTNET": ("control_FAULTNET", dict()),
    "control_FAULTNET_far": ("control_FAULTNET", dict(min_d=4.0)),
    "control_COULOMBLOQO": ("control_COULOMBLOQO", dict()),
}
MODELS = ("vario_full", "vario_nctx", "control_FAULTNET", "control_COULOMBLOQO")
CANDIDATES = ("vario_full", "vario_smooth", "vario_nctx")


def stage_holdout() -> int:
    from gems57.uniqueness import stop_historical_runner
    stop_historical_runner("run_vario:stage_holdout")

    CACHE.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    quad = hold_mod.quadrant_ids(foot)
    X = _load_X()
    valid = np.load(CACHE / "valid.npy")
    L_topo = np.load(CACHE / "L_topo.npy")
    L_sub = np.load(CACHE / "L_sub.npy")
    det_elev = np.load(CACHE / "det_elev.npy")
    with rasterio.open(INPUTS / "lineage" / "calib_h195_01922.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)
    foot_row = np.full(foot.shape, -1, np.int32)
    foot_row[foot] = np.arange(int(foot.sum()), dtype=np.int32)

    arm_names = list(ARMS) + ["control_H19_5"]
    terms = {a: None for a in arm_names}
    per_fold = {a: [] for a in arm_names}
    canaries, receipts = [], []
    for seed in SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        receipts += [f["receipt"] for f in folds]
        vis, hid = folds[0]["visible"], folds[0]["hidden_all"]
        excl = hid | (distance_transform_edt(~hid) <= 3.0)
        d_vis = distance_transform_edt(~vis)
        log(f"seed {seed}: context fields from VISIBLE catalogue only")
        _fill_context(X, foot, vis, det_elev, valid)
        # Rule 4 leakage canaries: every column alone on this draw.
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
        Xc = np.asarray(X[rows])  # materialise canary sample once
        for j, nm in enumerate(FEATURE_NAMES):
            v = Xc[:, j]
            a = 0.5 if np.ptp(v) == 0 else float(roc_auc_score(y, v))
            canaries.append(dict(seed=seed, feature=nm, auc=round(a, 6),
                                 symmetric_auc=round(max(a, 1 - a), 6)))
        del Xc
        worst = max(c["symmetric_auc"] for c in canaries if c["seed"] == seed)
        wname = max((c for c in canaries if c["seed"] == seed), key=lambda c: c["symmetric_auc"])["feature"]
        log(f"seed {seed}: canary max symmetric AUC = {worst:.4f} ({wname})")
        if worst > 0.90:
            raise SystemExit(f"LEAKAGE CANARY TRIPPED ({wname} {worst:.4f} > 0.90): stop")

        preds = {}
        for model in MODELS:
            log(f"seed {seed}: LOQO fit {model} ({len(ARM_COLS[model])} cols)")
            p = cl.fit_predict_loqo(X, foot, valid, quad, vis, feature_cols=ARM_COLS[model],
                                    excluded_mask=excl, guard_px=12, neg_buffer_px=5.0,
                                    seed=20261024 + seed)
            for arm, (mdl, kw) in ARMS.items():
                if mdl == model:
                    _, dots = _dots_from_proba(p, L_topo, L_sub, valid, foot, d_vis, **kw)
                    preds[arm] = dots
            del p
            gc.collect()
        preds["control_H19_5"] = cl.spaced_top_mask(
            scan_rank, foot & valid & h19 & (d_vis > 2.0), N_DOTS, min_dist_px=2.4)
        for a in arm_names:
            pr = preds[a].astype(np.float32)
            pr[vis] = 0.0
            for f in folds:
                sc, tm = evaluate_holdout.evaluate(pr, f, foot)
                terms[a] = tm if terms[a] is None else terms[a] + tm
                per_fold[a].append(dict(seed=seed, fold=f["name"], dti=round(float(sc["dti"]), 6),
                                        tpw=round(float(sc["tpw"]), 3), fpw=round(float(sc["fpw"]), 3),
                                        n_truth=int(sc["n_truth"])))
            del pr
        del preds
        gc.collect()
        log(f"seed {seed} done ({time.time()-t0:.0f}s)")

    np.savez(CACHE / "holdout_terms.npz", **terms)
    summaries = {c: evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate=c)
                 for c in CANDIDATES}
    s0 = summaries["vario_full"]["scores"]
    for k, v in sorted(s0.items(), key=lambda kv: -kv[1]["dti"]):
        log(f"  {k:22s} HOLDOUT-DTI {v['dti']:.6f} CI [{v['ci95'][0]:.6f},{v['ci95'][1]:.6f}] withheld={v['withheld_positive_pixels']}")
    doc = dict(
        schema="gemsdoe92-vario-holdout-v1", evidence_class="HOLDOUT-DTI",
        evaluator_version=evaluate_holdout.VERSION,
        instrument="strict draw-blind fold-visible buffered whole-component holdout (d_visible > 2.0 emission; control_FAULTNET_far d_visible > 4.0)",
        seeds=list(SEEDS), n_dots=N_DOTS, spacing_px=SPACING, smooth_sigma_px=SMOOTH_SIGMA,
        arm_columns={k: list(v) for k, v in ARM_COLS.items()},
        feature_names=FEATURE_NAMES,
        scores=s0,
        paired_by_candidate={c: summaries[c]["paired_differences"] for c in summaries},
        best_comparable_control=summaries["vario_full"]["best_comparable_control"],
        bootstrap=summaries["vario_full"]["bootstrap"],
        implementation_sha256=summaries["vario_full"]["implementation_sha256"],
        historical_reference=dict(
            faultnet_netfar=dict(dti=0.175147, ci95=[0.159756, 0.189860],
                                 withheld_positive_pixels=22663,
                                 source="evidence/faultnet_holdout.json (same instrument/seeds; non-paired)")),
        per_fold=per_fold, canaries=canaries, fold_receipts=receipts,
        runtime_s=round(time.time() - t0, 1))
    (EVIDENCE / "vario_holdout.json").write_text(json.dumps(doc, indent=1))
    log(f"wrote evidence/vario_holdout.json ({time.time()-t0:.0f}s)")
    return 0


def stage_deploy() -> int:
    from gems57.uniqueness import stop_historical_runner
    stop_historical_runner("run_vario:stage_deploy")

    CACHE.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    quad = hold_mod.quadrant_ids(foot)
    X = _load_X()
    valid = np.load(CACHE / "valid.npy")
    L_topo = np.load(CACHE / "L_topo.npy")
    L_sub = np.load(CACHE / "L_sub.npy")
    det_elev = np.load(CACHE / "det_elev.npy")
    d_cat = distance_transform_edt(~cat)
    log("deploy: context fields from FULL catalogue")
    _fill_context(X, foot, cat, det_elev, valid)
    for model in ("vario_full", "vario_nctx"):
        log(f"deploy: LOQO fit {model}")
        p = cl.fit_predict_loqo(X, foot, valid, quad, cat, feature_cols=ARM_COLS[model],
                                guard_px=12, neg_buffer_px=5.0, seed=20261025)
        np.save(CACHE / f"proba_{model}.npy", p)
        for arm, (mdl, kw) in ARMS.items():
            if mdl == model and arm.startswith("vario"):
                S, dots = _dots_from_proba(p, L_topo, L_sub, valid, foot, d_cat, **kw)
                np.save(CACHE / f"S_{arm}.npy", S)
                np.save(CACHE / f"dots_{arm}.npy", dots)
                log(f"  {arm}: dots={int(dots.sum())} on_cat={int((dots & cat).sum())} "
                    f"min_dcat={float(d_cat[dots].min()):.3f}")
                del S, dots
        del p
        gc.collect()
    log(f"deploy done ({time.time()-t0:.0f}s)")
    return 0


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "stack"
    raise SystemExit({"stack": stage_stack, "holdout": stage_holdout, "deploy": stage_deploy}[stage]())
