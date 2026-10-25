#!/usr/bin/env python3
"""NETEXPAND lane runner (pre-registration: docs/HYPOTHESES_20261025_NETEXPAND.md).

Stages (separate processes for the 3 GB sandbox, pattern of run_faultnet.py):
  stack    -> .cache/netexpand/X45.npy (context cols zero) + arrays.npz
  holdout  -> strict draw-blind fold-visible pooled HOLDOUT-DTI
              (evidence/netexpand_holdout.json + .cache/netexpand/holdout_terms.npz)
  deploy   -> full-catalogue LOQO probabilities, pure-crest surfaces, dot masks
              (.cache/netexpand/S_*.npy, dots_*.npy)

Shared tools only (Protocol Rule 2): gems57.holdout.buffered_component_draw,
gems57.evaluate_holdout, gems.knick_loqo / gems.listric / gems.faultnet /
gems.netexpand feature builders, gems.breakline.spaced_top_mask.
No TIF is written here; packaging happens in finalize_netexpand.py after the
Rule-1 surface uniqueness check.
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

from gems import faultnet as fn  # noqa: E402
from gems import knick_loqo as kl  # noqa: E402
from gems import listric as ls  # noqa: E402
from gems import netexpand as nx  # noqa: E402
from gems.breakline import spaced_top_mask  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa: E402

INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE = ROOT / ".cache" / "netexpand"
EVIDENCE = ROOT / "evidence"
N_DOTS = 37_654
SPACING = 2.8
SEEDS = (20, 30)
CTX0 = 34  # first context column in the 45-col stack

ALL_NAMES = list(kl.FEATURE_NAMES) + list(ls.LISTRIC_FEATURE_NAMES) + list(fn.CONTEXT_NAMES) + list(nx.NEW_FEATURE_NAMES)


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def read_bands(ids):
    out = {}
    with rasterio.open(INPUTS / "training_features.tif") as ds:
        for b in ids:
            out[b] = ds.read(b, masked=True).filled(np.nan).astype(np.float32)
    return out


def stage_stack() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    log("stack: reading bands")
    b = read_bands((2, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 17, 18, 19))
    with rasterio.open(INPUTS / "external" / "geodawn_rad_u8.tif") as ds:
        rk, rth, ru = ds.read(1), ds.read(2), ds.read(3)
    valid_base = (foot & np.isfinite(b[12]) & (b[12] > -1e30)
                  & np.isfinite(b[19]) & (b[19] > -1e30)
                  & np.isfinite(b[2]) & (b[2] > -1e30))
    from gems.coulomb_loqo import gdr_blind_thermal_features
    gdr = gdr_blind_thermal_features(INPUTS / "external" / "gdr_wellspring_in_footprint.csv",
                                     foot.shape, valid_base, sigma_px=14.0)
    log(f"stack: GDR plume done ({time.time()-t0:.0f}s); knick 30 features...")
    st = kl.compute_knick_loqo_stack(
        rtp=b[2], geod_2ndinv=b[4], grav_slope=b[5], geod_shearrate=b[7],
        geod_dilaterate=b[8], grav_vg=b[11], det_elev=b[12], grav_anom=b[13],
        depth_to_base=b[15], cond_surf=b[17], grav_hg=b[18], det_elev_slope=b[19],
        rad_k=rk, rad_th=rth, rad_u=ru, gdr_plume_feat=gdr["plume_feat"], footprint=foot)
    del rk, rth, ru, gdr, valid_base
    valid = st["valid"]
    log(f"stack: knick done ({time.time()-t0:.0f}s); listric 4...")
    lf = ls.compute_listric_features(det_elev=b[12], det_elev_slope=b[19], grav_hg=b[18],
                                     depth_to_base=b[15], footprint=foot, valid=valid)
    log(f"stack: listric done ({time.time()-t0:.0f}s); netexpand 6...")
    nf = nx.compute_netexpand_features(
        rtp=b[2], tmi=b[14], tmi_vg=b[9], grav_vg=b[11], grav_anom=b[13], grav_hg=b[18],
        depth_to_base=b[15], cond_surf=b[17], footprint=foot, valid=valid)
    det_elev = b[12]
    del b
    gc.collect()
    l_new = nx.build_pure_crest_channel(nf, lf["L_listric"], valid)
    n = st["X_foot"].shape[0]
    X = np.zeros((n, 45), np.float32)
    X[:, :30] = st["X_foot"]
    foot_idx = np.flatnonzero(foot.ravel())
    for j, name in enumerate(ls.LISTRIC_FEATURE_NAMES):
        X[:, 30 + j] = lf[name].ravel()[foot_idx]
    for j, name in enumerate(nx.NEW_FEATURE_NAMES):
        X[:, 39 + j] = nf[name].ravel()[foot_idx]
    np.save(CACHE / "X45.npy", X)
    np.savez(CACHE / "arrays.npz", valid=valid, L_topo=st["L_topo"], L_knick=st["L_knick"],
             L_sub_orig=st["L_sub"], L_new=l_new, L_listric=lf["L_listric"], det_elev=det_elev)
    log(f"stack: wrote X45 {X.shape} + arrays.npz ({time.time()-t0:.0f}s)")
    del X, st, lf, nf
    gc.collect()
    return 0


def load_arrays():
    z = np.load(CACHE / "arrays.npz")
    X = np.load(CACHE / "X45.npy", mmap_mode="r+")
    return X, {k: z[k] for k in z.files}


def fill_context(X, foot, visible, det_elev, valid):
    F = fn.context_fields(visible, det_elev, valid)
    for j, name in enumerate(fn.CONTEXT_NAMES):
        X[:, CTX0 + j] = F[name][foot]
    if hasattr(X, "flush"):
        X.flush()
    return F


def fit_knick_control(X, foot, valid, quad, labels, excluded_mask, seed):
    kw = dict(excluded_mask=excluded_mask, guard_px=12, neg_buffer_px=5.0,
              neg_pos_ratio=4, max_iter=185)
    p_full = kl.fit_single_loqo(X, foot, valid, quad, labels,
                                feature_cols=tuple(range(30)), seed=seed, **kw)
    p_deb = kl.fit_single_loqo(X, foot, valid, quad, labels,
                               feature_cols=kl.DEBIASED_INDICES, seed=seed + 1, **kw)
    p_sub = kl.fit_single_loqo(X, foot, valid, quad, labels,
                               feature_cols=kl.SUB_KNICK_INDICES, seed=seed + 2, **kw)
    raw = (np.float32(0.15) * p_full + np.float32(0.35) * p_deb
           + np.float32(0.50) * p_sub).astype(np.float32)
    return kl.calibrate_quadrant_probabilities(raw, valid, quad,
                                               calib_weight=0.80, power_gamma=3.3)


def pure_dots(proba, arr, valid, foot, d_ref, mind):
    z = np.zeros_like(arr["L_new"])
    c = kl.build_knick_crest_surface(proba, z, arr["L_new"], valid, l_knick=z,
                                     topo_weight=0.0, knick_weight=0.0, sub_weight=1.45)
    dots = spaced_top_mask(c["S_crest"], foot & valid & c["ridge_1d"] & (d_ref > mind),
                           N_DOTS, min_dist_px=SPACING, cand_cap=900_000)
    return c["S_crest"], dots


def orig_dots(proba, arr, valid, foot, d_ref, mind=2.0):
    c = kl.build_knick_crest_surface(proba, arr["L_topo"], arr["L_sub_orig"], valid,
                                     l_knick=arr["L_knick"], topo_weight=0.15,
                                     knick_weight=1.00, sub_weight=1.45)
    dots = spaced_top_mask(c["S_crest"], foot & valid & c["ridge_1d"] & (d_ref > mind),
                           N_DOTS, min_dist_px=SPACING, cand_cap=900_000)
    return c["S_crest"], dots


def stage_holdout() -> int:
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    quad = hold_mod.quadrant_ids(foot)
    X, arr = load_arrays()
    valid, det_elev = arr["valid"], arr["det_elev"]
    with rasterio.open(INPUTS / "lineage" / "calib_h195_01922.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    with rasterio.open(ROOT / "data/parent_R0_zeros.tif") as ds:
        r0 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)
    foot_row = np.full(foot.shape, -1, np.int32)
    foot_row[foot] = np.arange(int(foot.sum()), dtype=np.int32)

    arms = ["netexpand", "netexpand_far", "nocontext", "control_knick", "control_H19_5", "control_R0"]
    terms = {a: None for a in arms}
    per_fold = {a: [] for a in arms}
    canaries, receipts = [], []
    for seed in SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        receipts += [f["receipt"] for f in folds]
        vis, hid = folds[0]["visible"], folds[0]["hidden_all"]
        excl = hid | (distance_transform_edt(~hid) <= 3.0)
        d_vis = distance_transform_edt(~vis)
        log(f"seed {seed}: context from VISIBLE catalogue ({time.time()-t0:.0f}s)")
        fill_context(X, foot, vis, det_elev, valid)
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
        Xm = np.asarray(X)
        for j, nm in enumerate(ALL_NAMES):
            v = Xm[rows, j]
            a = 0.5 if np.ptp(v) == 0 else float(roc_auc_score(y, v))
            canaries.append(dict(seed=seed, feature=nm, auc=round(a, 6),
                                 symmetric_auc=round(max(a, 1 - a), 6)))
        worst = max(c["symmetric_auc"] for c in canaries if c["seed"] == seed)
        wname = max((c for c in canaries if c["seed"] == seed), key=lambda c: c["symmetric_auc"])["feature"]
        log(f"seed {seed}: canary max symmetric AUC = {worst:.4f} ({wname})")
        if worst > 0.90:
            (EVIDENCE / "netexpand_canary_stop.json").write_text(json.dumps(canaries, indent=1))
            raise SystemExit(f"LEAKAGE CANARY TRIPPED ({worst:.4f} > 0.90): stop")

        preds = {}
        log(f"seed {seed}: fit netexpand (with context)")
        res = nx.fit_predict_netexpand_loqo(Xm, foot, valid, quad, vis, with_context=True,
                                            excluded_mask=excl, seed=20261025 + seed)
        S, preds["netexpand"] = pure_dots(res["cal_proba"], arr, valid, foot, d_vis, 2.0)
        _, preds["netexpand_far"] = pure_dots(res["cal_proba"], arr, valid, foot, d_vis, 4.0)
        del res, S
        gc.collect()
        log(f"seed {seed}: fit nocontext ablation ({time.time()-t0:.0f}s)")
        res = nx.fit_predict_netexpand_loqo(Xm, foot, valid, quad, vis, with_context=False,
                                            excluded_mask=excl, seed=20261125 + seed)
        _, preds["nocontext"] = pure_dots(res["cal_proba"], arr, valid, foot, d_vis, 2.0)
        del res
        gc.collect()
        log(f"seed {seed}: fit knick30 control ({time.time()-t0:.0f}s)")
        p = fit_knick_control(Xm, foot, valid, quad, vis, excl, seed=20261225 + seed)
        _, preds["control_knick"] = orig_dots(p, arr, valid, foot, d_vis, 2.0)
        del p
        gc.collect()
        preds["control_H19_5"] = spaced_top_mask(scan_rank, foot & valid & h19 & (d_vis > 2.0),
                                                 N_DOTS, min_dist_px=2.4)
        preds["control_R0"] = r0.copy()
        for a in arms:
            pr = preds[a].astype(np.float32)
            pr[vis] = 0.0
            for f in folds:
                sc, tm = evaluate_holdout.evaluate(pr, f, foot)
                terms[a] = tm if terms[a] is None else terms[a] + tm
                per_fold[a].append(dict(seed=seed, fold=f["name"], dti=round(float(sc["dti"]), 6),
                                        n_truth=int(sc["n_truth"])))
        del preds
        gc.collect()
        log(f"seed {seed} done ({time.time()-t0:.0f}s)")

    np.savez(CACHE / "holdout_terms.npz", **terms)
    summaries = {c: evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate=c)
                 for c in ("netexpand", "netexpand_far", "nocontext")}
    s0 = summaries["netexpand"]["scores"]
    for k, v in sorted(s0.items(), key=lambda kv: -kv[1]["dti"]):
        log(f"  {k:16s} HOLDOUT-DTI {v['dti']:.6f} CI {v['ci95'][0]:.6f}-{v['ci95'][1]:.6f}")
    doc = dict(schema="gemsdoe92-netexpand-holdout-v1", evidence_class="HOLDOUT-DTI",
               evaluator_version=evaluate_holdout.VERSION,
               instrument="strict draw-blind fold-visible (d_visible>2.0; netexpand_far d_visible>4.0)",
               seeds=list(SEEDS), n_dots=N_DOTS, spacing_px=SPACING,
               feature_names=ALL_NAMES, scores=s0,
               paired_by_candidate={c: summaries[c]["paired_differences"] for c in summaries},
               bootstrap=summaries["netexpand"]["bootstrap"],
               implementation_sha256=summaries["netexpand"]["implementation_sha256"],
               per_fold=per_fold, canaries=canaries, fold_receipts=receipts,
               runtime_s=round(time.time() - t0, 1))
    (EVIDENCE / "netexpand_holdout.json").write_text(json.dumps(doc, indent=1))
    log(f"wrote evidence/netexpand_holdout.json ({time.time()-t0:.0f}s)")
    return 0


def stage_deploy() -> int:
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    quad = hold_mod.quadrant_ids(foot)
    X, arr = load_arrays()
    valid, det_elev = arr["valid"], arr["det_elev"]
    d_cat = distance_transform_edt(~cat)
    log("deploy: context from FULL catalogue")
    fill_context(X, foot, cat, det_elev, valid)
    Xm = np.asarray(X)
    log("deploy: fit netexpand")
    res = nx.fit_predict_netexpand_loqo(Xm, foot, valid, quad, cat, with_context=True, seed=20261025)
    S, d2 = pure_dots(res["cal_proba"], arr, valid, foot, d_cat, 2.0)
    _, d4 = pure_dots(res["cal_proba"], arr, valid, foot, d_cat, 4.0)
    np.save(CACHE / "S_netexpand.npy", S)
    np.save(CACHE / "P_netexpand.npy", res["cal_proba"])
    np.save(CACHE / "dots_netexpand.npy", d2)
    np.save(CACHE / "dots_netexpand_far.npy", d4)
    log(f"  netexpand dots={int(d2.sum())} far dots={int(d4.sum())} ({time.time()-t0:.0f}s)")
    del res, S
    gc.collect()
    log("deploy: fit nocontext ablation")
    res = nx.fit_predict_netexpand_loqo(Xm, foot, valid, quad, cat, with_context=False, seed=20261125)
    S, dn = pure_dots(res["cal_proba"], arr, valid, foot, d_cat, 2.0)
    np.save(CACHE / "S_nocontext.npy", S)
    np.save(CACHE / "P_nocontext.npy", res["cal_proba"])
    np.save(CACHE / "dots_nocontext.npy", dn)
    log(f"  nocontext dots={int(dn.sum())} ({time.time()-t0:.0f}s)")
    log(f"deploy done ({time.time()-t0:.0f}s)")
    return 0


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    fn_map = {"stack": stage_stack, "holdout": stage_holdout, "deploy": stage_deploy}
    if stage not in fn_map:
        raise SystemExit(f"usage: run_netexpand.py {'|'.join(fn_map)}")
    raise SystemExit(fn_map[stage]())
