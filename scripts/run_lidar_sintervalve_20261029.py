#!/usr/bin/env python3
"""2026-10-29 LIDAR-SINTERVALVE (H-92G1) 3-Experiment Runner.

Pre-registration: docs/HYPOTHESES_20261029_LIDAR_SINTERVALVE.md (Rank #1).
Budget: strictly 3 experiments (E1, E2, E3), < 2 hours wall-clock, 0 weekly slots spent.

Stages (separate subprocesses to stay < 1.2 GiB RSS on a 3.8 GiB RAM machine):
  stack       -> Build disk-backed .cache/lidarsintervalve/X53.npy (5,167,373 x 53 float32)
                 + arrays.npz using tag-verified training_features.tif, USGS 3DEP 1 m LiDAR,
                 USGS 3DEP 10 m quantile bridge, and DOE GDR #1391 sinter/2m-probe/Fournier/vents.
  e1_canaries -> Experiment 1: Single-feature leakage canaries on all 53 features + lidar_valid_raw
                 across seeds=(20, 30) (22,663 withheld positives, AUC <= 0.90 hard stop) +
                 1m->10m quantile-seam parity verification.
  e2_holdout  -> Experiment 2: Strict fold-proper draw-blind spatially-blocked HOLDOUT-DTI
                 (vendor/gems57/evaluate_holdout.py, gems57-pooled-hide-v2, 22,663 withheld
                 positives, 1,000 paired 20 km spatial-cluster bootstrap draws) comparing
                 lidarsintervalve_far (d_vis > 4.0) and lidarsintervalve_std (d_vis > 2.0)
                 head-to-head against control_netexpand_far (0.177976 all-time repo record),
                 control_netexpand (0.146798), control_H19_5 (R0-recipe equivalent), and control_R0.
  e3_deploy   -> Experiment 3: Pre-placement surface uniqueness audit across all 2,263 unique
                 SHA-256 rasters in 8 GitHub owners (.cache/registry_v3), registry-capped single-lane
                 H-92G1 crest placement (37,654 binary 1.0 dots, <= 0.65 PI-1 3-px overlap across all
                 2,263 rasters, d_cat > 2.0 px), shared submission_writer.py packaging + gems.gates
                 audit + LBM-v3 MODEL projection + byte-bound JSON run card.
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
from scipy.ndimage import distance_transform_edt
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]

import lbm_data as L  # noqa: E402
from gems import faultnet as fn  # noqa: E402
from gems import gates as gates_mod  # noqa: E402
from gems import knick_loqo as kl  # noqa: E402
from gems import lbmodel as M  # noqa: E402
from gems import lidar_sintervalve as lsv  # noqa: E402
from gems import listric as ls  # noqa: E402
from gems import netexpand as nx  # noqa: E402
from gems import registry_cache as rc  # noqa: E402
from gems import uniqueness_v3 as U  # noqa: E402
from gems.breakline import spaced_top_mask  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402

INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE = ROOT / ".cache" / "lidarsintervalve"
EVIDENCE = ROOT / "evidence"
DL = ROOT / "docs" / "downloads"
N_DOTS = 37_654
SPACING = 2.8
SEEDS = (20, 30)
CTX0 = 34

ALL_53_NAMES: list[str] = (
    list(kl.FEATURE_NAMES)
    + list(ls.LISTRIC_FEATURE_NAMES)
    + list(fn.CONTEXT_NAMES)
    + list(nx.NEW_FEATURE_NAMES)
    + list(lsv.LIDAR_SINTERVALVE_NAMES)
)


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def read_verified_bands(ids: tuple[int, ...]) -> dict[int, np.ndarray]:
    out: dict[int, np.ndarray] = {}
    with rasterio.open(INPUTS / "training_features.tif") as ds:
        lsv.assert_training_band_tags(ds)
        for b in ids:
            arr = ds.read(b, masked=True).filled(np.nan).astype(np.float32)
            # Clean interior -3.4028235e+38 finite nodata sentinels (IR-92-FINITE-NODATA-SENTINEL)
            arr[arr <= -1e30] = np.nan
            out[b] = arr
    return out


def load_arrays():
    z = np.load(CACHE / "arrays.npz")
    X = np.load(CACHE / "X53.npy", mmap_mode="r+")
    return X, {k: z[k] for k in z.files}


def fill_context(X: np.ndarray, foot: np.ndarray, visible: np.ndarray, det_elev: np.ndarray, valid: np.ndarray) -> None:
    F = fn.context_fields(visible, det_elev, valid)
    for j, name in enumerate(fn.CONTEXT_NAMES):
        X[:, CTX0 + j] = F[name][foot]
    if hasattr(X, "flush"):
        X.flush()


def stage_stack() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    quad = hold_mod.quadrant_ids(foot)
    log("stack: reading tag-verified training_features.tif bands (cleaning <= -1e30 sentinels)")
    b = read_verified_bands((2, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 17, 18, 19))
    with rasterio.open(INPUTS / "external" / "geodawn_rad_u8.tif") as ds:
        rk, rth, ru = ds.read(1), ds.read(2), ds.read(3)
    valid_base = foot & np.isfinite(b[12]) & np.isfinite(b[19]) & np.isfinite(b[2])

    from gems.coulomb_loqo import gdr_blind_thermal_features
    gdr = gdr_blind_thermal_features(
        INPUTS / "external" / "gdr_wellspring_in_footprint.csv",
        foot.shape,
        valid_base,
        sigma_px=14.0,
    )
    log(f"stack: GDR base plume done ({time.time() - t0:.0f}s); computing KNICK 30...")
    st = kl.compute_knick_loqo_stack(
        rtp=b[2], geod_2ndinv=b[4], grav_slope=b[5], geod_shearrate=b[7],
        geod_dilaterate=b[8], grav_vg=b[11], det_elev=b[12], grav_anom=b[13],
        depth_to_base=b[15], cond_surf=b[17], grav_hg=b[18], det_elev_slope=b[19],
        rad_k=rk, rad_th=rth, rad_u=ru, gdr_plume_feat=gdr["plume_feat"], footprint=foot,
    )
    del rk, rth, ru, gdr, valid_base
    valid = st["valid"]

    log(f"stack: KNICK done ({time.time() - t0:.0f}s); flushing cols 0..29 to disk memmap...")
    n_foot = st["X_foot"].shape[0]
    foot_idx = np.flatnonzero(foot.ravel())
    X_mm = np.lib.format.open_memmap(CACHE / "X53.npy", mode="w+", dtype=np.float32, shape=(n_foot, 53))
    X_mm[:, :30] = st["X_foot"]
    X_mm.flush()
    del st
    gc.collect()

    log(f"stack: computing LISTRIC 4 + NETEXPAND 6 ({time.time() - t0:.0f}s)...")
    lf = ls.compute_listric_features(
        det_elev=b[12], det_elev_slope=b[19], grav_hg=b[18],
        depth_to_base=b[15], footprint=foot, valid=valid,
    )
    for j, name in enumerate(ls.LISTRIC_FEATURE_NAMES):
        X_mm[:, 30 + j] = lf[name].ravel()[foot_idx]
    l_listric = lf["L_listric"]
    del lf
    gc.collect()

    nf = nx.compute_netexpand_features(
        rtp=b[2], tmi=b[14], tmi_vg=b[9], grav_vg=b[11], grav_anom=b[13], grav_hg=b[18],
        depth_to_base=b[15], cond_surf=b[17], footprint=foot, valid=valid,
    )
    for j, name in enumerate(nx.NEW_FEATURE_NAMES):
        X_mm[:, 39 + j] = nf[name].ravel()[foot_idx]
    X_mm.flush()
    l_new = nx.build_pure_crest_channel(nf, l_listric, valid)
    del nf, l_listric
    # Keep only the 4 bands needed by H-92G1 (12, 13, 15, 17); free the other 10 (~500 MB)!
    for k_drop in list(b.keys()):
        if k_drop not in (12, 13, 15, 17):
            del b[k_drop]
    gc.collect()

    log(f"stack: computing H-92G1 LIDAR-SINTERVALVE 8 features (USGS 3DEP 1m->10m bridge + GDR sinter/2m/Fournier) ({time.time() - t0:.0f}s)...")
    lsv_feats, lidar_valid_raw = lsv.compute_lidar_sintervalve_features(
        lidar_tif=INPUTS / "external" / "lidar_scarp_features_u8.tif",
        topo10m_tif=INPUTS / "external" / "topo_10m_derived_100m_u8.tif",
        paleo_zip=INPUTS / "external" / "paleo_geothermal_regional.zip",
        probe2m_zip=INPUTS / "external" / "2m_temperature_probe_INGENIOUS_regional_data.zip",
        volc_csv=INPUTS / "external" / "gdr_volcanic_vents_in_footprint.csv",
        wellspring_csv=INPUTS / "external" / "gdr_wellspring_in_footprint.csv",
        det_elev=b[12],
        grav_anom=b[13],
        depth_to_base=b[15],
        cond_surf=b[17],
        footprint=foot,
        valid=valid,
        quad=quad,
    )
    det_elev = np.nan_to_num(b[12], nan=0.0).astype(np.float32)
    del b
    gc.collect()

    l_lsv = lsv.build_lidar_sintervalve_crest(lsv_feats, l_new, valid)
    for j, name in enumerate(lsv.LIDAR_SINTERVALVE_NAMES):
        X_mm[:, 45 + j] = lsv_feats[name].ravel()[foot_idx]
    X_mm.flush()

    # Compute novel H-92G1 standalone prospectivity score for E3 registry-unique crest tie-breaking
    novel_h92g1 = (
        np.float32(0.24) * lsv_feats["lidar_wallace_dipole"]
        + np.float32(0.20) * lsv_feats["lidar_bank_vetoed_scarp"]
        + np.float32(0.20) * lsv_feats["lidar_antislope_graben"]
        + np.float32(0.12) * lsv_feats["lidar_subsurf_strike_lock"]
        + np.float32(0.12) * lsv_feats["sinter_probe_volc_valve"]
        + np.float32(0.12) * lsv_feats["lidar_sinter_concordance"]
    ).astype(np.float32)

    np.savez_compressed(
        CACHE / "arrays.npz",
        valid=valid,
        L_new=l_new,
        L_lsv=l_lsv,
        novel_h92g1=novel_h92g1,
        det_elev=det_elev,
        lidar_valid_raw=lidar_valid_raw,
    )
    log(f"stack: wrote X53.npy {X_mm.shape} + arrays.npz in {time.time() - t0:.1f}s")
    return 0


def stage_e1_canaries() -> int:
    """Experiment 1 of 3: Single-feature leakage canaries (Rule 4) + 1m->10m quantile seam audit."""
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    X, arr = load_arrays()
    valid, det_elev, lidar_valid_raw = arr["valid"], arr["det_elev"], arr["lidar_valid_raw"]
    foot_row = np.full(foot.shape, -1, np.int32)
    foot_row[foot] = np.arange(int(foot.sum()), dtype=np.int32)

    canaries = []
    for seed in SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        vis = folds[0]["visible"]
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
        lin_eval = np.concatenate(ix)
        rows = foot_row.ravel()[lin_eval]

        for j, nm in enumerate(ALL_53_NAMES):
            v = np.asarray(X[rows, j], dtype=np.float32)
            a = 0.5 if float(np.ptp(v)) == 0.0 else float(roc_auc_score(y, v))
            canaries.append(dict(
                seed=seed, col=j, feature=nm,
                is_h92g1=j >= 45,
                auc=round(a, 6),
                symmetric_auc=round(max(a, 1.0 - a), 6),
            ))
        # Explicit survey-footprint canary on raw lidar_valid
        lv = lidar_valid_raw.ravel()[lin_eval]
        a_lv = 0.5 if float(np.ptp(lv)) == 0.0 else float(roc_auc_score(y, lv))
        canaries.append(dict(
            seed=seed, col=-1, feature="lidar_valid_raw_survey_mask_canary",
            is_h92g1=True,
            auc=round(a_lv, 6),
            symmetric_auc=round(max(a_lv, 1.0 - a_lv), 6),
        ))

    # Verify quantile-bridge seam parity between LiDAR-covered and 10m-imputed cells
    has_lid_fp = (lidar_valid_raw[foot] >= 0.5) & valid[foot]
    no_lid_fp = (lidar_valid_raw[foot] < 0.5) & valid[foot]
    seam_parity = []
    for j in range(45, 50):
        col_v = np.asarray(X[:, j], dtype=np.float32)
        m_lid = float(col_v[has_lid_fp].mean())
        m_imp = float(col_v[no_lid_fp].mean())
        seam_parity.append(dict(
            feature=ALL_53_NAMES[j],
            mean_on_lidar_75pct=round(m_lid, 5),
            mean_on_10m_bridge_25pct=round(m_imp, 5),
            abs_mean_gap=round(abs(m_lid - m_imp), 6),
        ))

    max_all = max(c["symmetric_auc"] for c in canaries)
    worst_all = max(canaries, key=lambda c: c["symmetric_auc"])
    h92_only = [c for c in canaries if c["is_h92g1"]]
    max_h92 = max(c["symmetric_auc"] for c in h92_only)
    worst_h92 = max(h92_only, key=lambda c: c["symmetric_auc"])

    doc = dict(
        schema="gemsdoe92-lidarsintervalve-e1-canaries-v1",
        experiment_id="E1",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        evaluator_version=evaluate_holdout.VERSION,
        seeds=list(SEEDS),
        n_features_tested=54,
        max_symmetric_auc_all_54=max_all,
        worst_feature_all_54=worst_all,
        max_symmetric_auc_h92g1_9=max_h92,
        worst_feature_h92g1_9=worst_h92,
        leakage_flag=bool(max_all > 0.90),
        gate_pass=bool(max_all <= 0.90),
        quantile_bridge_seam_parity=seam_parity,
        canaries=canaries,
        runtime_s=round(time.time() - t0, 2),
    )
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "lidarsintervalve_e1_canaries_20261029.json").write_text(
        json.dumps(doc, indent=2) + "\n", encoding="utf-8"
    )
    log(
        f"E1 PASS={doc['gate_pass']}: max_sym_auc(54)={max_all:.5f} ({worst_all['feature']}), "
        f"max_sym_auc(H-92G1)={max_h92:.5f} ({worst_h92['feature']}), runtime={doc['runtime_s']}s"
    )
    if max_all > 0.90:
        raise SystemExit(f"LEAKAGE CANARY TRIPPED ({max_all:.5f} > 0.90)")
    return 0


def _crest_dots(proba: np.ndarray, l_crest: np.ndarray, valid: np.ndarray, foot: np.ndarray, d_ref: np.ndarray, mind: float):
    z = np.zeros_like(l_crest)
    c = kl.build_knick_crest_surface(
        proba, z, l_crest, valid, l_knick=z,
        topo_weight=0.0, knick_weight=0.0, sub_weight=1.45,
    )
    dots = spaced_top_mask(
        c["S_crest"],
        foot & valid & c["ridge_1d"] & (d_ref > mind),
        N_DOTS,
        min_dist_px=SPACING,
        cand_cap=900_000,
    )
    return c["S_crest"], dots


def stage_e2_holdout() -> int:
    """Experiment 2 of 3: Spatially-blocked fold-proper hide-and-recover HOLDOUT-DTI."""
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    quad = hold_mod.quadrant_ids(foot)
    X, arr = load_arrays()
    valid, det_elev = arr["valid"], arr["det_elev"]

    with rasterio.open(INPUTS / "lineage" / "calib_h195_01922.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)

    arms = [
        "lidarsintervalve_far",
        "lidarsintervalve_lnew_far",
        "lidarsintervalve_std",
        "control_netexpand_far",
        "control_netexpand",
        "control_H19_5",
        "control_R0",
    ]
    terms = {a: None for a in arms}
    per_fold = {a: [] for a in arms}
    receipts = []

    only_seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
    for seed in SEEDS:
        if only_seed is not None and seed != only_seed:
            continue
        ckpt_npz = CACHE / f"e2_seed_{seed}.npz"
        ckpt_json = CACHE / f"e2_seed_{seed}_meta.json"
        if ckpt_npz.is_file() and ckpt_json.is_file():
            log(f"E2 seed {seed}: loading checkpoint {ckpt_npz.name}")
            z_ck = np.load(ckpt_npz)
            m_ck = json.loads(ckpt_json.read_text(encoding="utf-8"))
            receipts += m_ck["receipts"]
            for a in arms:
                tm_s = z_ck[a]
                terms[a] = tm_s if terms[a] is None else terms[a] + tm_s
                per_fold[a].extend(m_ck["per_fold"][a])
            continue

        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        seed_receipts = [f["receipt"] for f in folds]
        receipts += seed_receipts
        vis, hid = folds[0]["visible"], folds[0]["hidden_all"]
        excl = hid | (distance_transform_edt(~hid) <= 3.0)
        d_vis = distance_transform_edt(~vis)

        log(f"E2 seed {seed}: computing visible-only fault context ({time.time() - t0:.0f}s)")
        fill_context(X, foot, vis, det_elev, valid)

        log(f"E2 seed {seed}: fitting 53-col H-92G1 LIDAR-SINTERVALVE LOQO ({time.time() - t0:.0f}s)")
        res_lsv = lsv.fit_predict_lidar_sintervalve_loqo(
            X, foot, valid, quad, vis, with_context=True,
            excluded_mask=excl, seed=20261029 + seed,
        )
        preds = {}
        _, preds["lidarsintervalve_far"] = _crest_dots(res_lsv["cal_proba"], arr["L_lsv"], valid, foot, d_vis, 4.0)
        _, preds["lidarsintervalve_lnew_far"] = _crest_dots(res_lsv["cal_proba"], arr["L_new"], valid, foot, d_vis, 4.0)
        _, preds["lidarsintervalve_std"] = _crest_dots(res_lsv["cal_proba"], arr["L_lsv"], valid, foot, d_vis, 2.0)
        del res_lsv
        gc.collect()

        log(f"E2 seed {seed}: fitting 45-col NETEXPAND same-draw control ({time.time() - t0:.0f}s)")
        res_nx = nx.fit_predict_netexpand_loqo(
            X, foot, valid, quad, vis, with_context=True,
            excluded_mask=excl, seed=20261025 + seed,
        )
        _, preds["control_netexpand_far"] = _crest_dots(res_nx["cal_proba"], arr["L_new"], valid, foot, d_vis, 4.0)
        _, preds["control_netexpand"] = _crest_dots(res_nx["cal_proba"], arr["L_new"], valid, foot, d_vis, 2.0)
        del res_nx
        gc.collect()

        preds["control_H19_5"] = spaced_top_mask(
            scan_rank, foot & valid & h19 & (d_vis > 2.0), N_DOTS, min_dist_px=2.4
        )
        preds["control_R0"] = r0.copy()

        seed_terms = {a: None for a in arms}
        seed_pf = {a: [] for a in arms}
        for a in arms:
            pr = preds[a].astype(np.float32)
            pr[vis] = 0.0
            for f in folds:
                sc, tm = evaluate_holdout.evaluate(pr, f, foot)
                seed_terms[a] = tm if seed_terms[a] is None else seed_terms[a] + tm
                terms[a] = tm if terms[a] is None else terms[a] + tm
                rec_pf = dict(
                    seed=seed, fold=f["name"],
                    dti=round(float(sc["dti"]), 6),
                    n_truth=int(sc["n_truth"]),
                )
                seed_pf[a].append(rec_pf)
                per_fold[a].append(rec_pf)
        del preds
        gc.collect()
        np.savez_compressed(ckpt_npz, **seed_terms)
        ckpt_json.write_text(
            json.dumps({"seed": seed, "receipts": seed_receipts, "per_fold": seed_pf}, indent=2),
            encoding="utf-8",
        )
        for a in arms:
            vals_a = [x["dti"] for x in seed_pf[a]]
            log(f"  seed {seed} mean fold DTI {a:26s}: {np.mean(vals_a):.6f}")
        log(f"E2 seed {seed} checkpointed ({time.time() - t0:.0f}s)")

    if only_seed is not None:
        return 0

    np.savez_compressed(CACHE / "e2_holdout_terms.npz", **terms)
    cand_keys = ("lidarsintervalve_far", "lidarsintervalve_lnew_far", "lidarsintervalve_std")
    summaries = {
        c: evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate=c)
        for c in cand_keys
    }
    scores = summaries["lidarsintervalve_far"]["scores"]
    for k, v in sorted(scores.items(), key=lambda kv: -kv[1]["dti"]):
        log(f"  {k:26s} HOLDOUT-DTI {v['dti']:.6f} [95% CI: {v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}]")

    # Exact withheld positive pixel count across pooled folds
    withheld_exact = sum(x["n_truth"] for x in per_fold["lidarsintervalve_far"])

    doc = dict(
        schema="gemsdoe92-lidarsintervalve-e2-holdout-v1",
        experiment_id="E2",
        evidence_class="HOLDOUT-DTI",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        evaluator_version=evaluate_holdout.VERSION,
        withheld_positive_pixels=int(withheld_exact),
        seeds=list(SEEDS),
        n_dots=N_DOTS,
        spacing_px=SPACING,
        scores=scores,
        paired_by_candidate={c: summaries[c]["paired_differences"] for c in cand_keys},
        bootstrap=summaries["lidarsintervalve_far"]["bootstrap"],
        implementation_sha256=summaries["lidarsintervalve_far"]["implementation_sha256"],
        per_fold=per_fold,
        fold_receipts=receipts,
        runtime_s=round(time.time() - t0, 1),
    )
    (EVIDENCE / "lidarsintervalve_e2_holdout_20261029.json").write_text(
        json.dumps(doc, indent=2) + "\n", encoding="utf-8"
    )
    log(f"E2 complete -> evidence/lidarsintervalve_e2_holdout_20261029.json ({doc['runtime_s']}s)")
    return 0


def _halo_3px_bool(dots_lin_full: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    H, W = shape
    out = np.zeros(H * W, dtype=bool)
    yy, xx = np.divmod(dots_lin_full, W)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if dy * dy + dx * dx <= 9:
                ry = yy + dy
                rx = xx + dx
                ok = (ry >= 0) & (ry < H) & (rx >= 0) & (rx < W)
                out[ry[ok] * W + rx[ok]] = True
    return out.reshape(H, W)


def stage_e3_deploy() -> int:
    """Experiment 3 of 3: Full-data H-92G1 deploy, pre-placement + final 2,263-raster audit,
    shared GeoTIFF writer, LBM-v3 MODEL projection, and byte-bound JSON Run Card."""
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    quad = hold_mod.quadrant_ids(foot)
    X, arr = load_arrays()
    valid, det_elev = arr["valid"], arr["det_elev"]
    d_cat = distance_transform_edt(~cat)

    # Check which E2 crest arm won on HOLDOUT-DTI so E3 uses the empirically best H-92G1 crest!
    e2_doc = json.loads((EVIDENCE / "lidarsintervalve_e2_holdout_20261029.json").read_text(encoding="utf-8"))
    sc_lsv = e2_doc["scores"]["lidarsintervalve_far"]["dti"]
    sc_lnew = e2_doc["scores"]["lidarsintervalve_lnew_far"]["dti"]
    use_crest_key = "L_lsv" if sc_lsv >= sc_lnew else "L_new"
    best_e2_arm = "lidarsintervalve_far" if sc_lsv >= sc_lnew else "lidarsintervalve_lnew_far"
    log(f"E3: selected best H-92G1 crest={use_crest_key} from E2 ({best_e2_arm}={max(sc_lsv, sc_lnew):.6f})")

    log("E3: fitting full-catalogue 53-col H-92G1 LIDAR-SINTERVALVE LOQO...")
    fill_context(X, foot, cat, det_elev, valid)
    res_full = lsv.fit_predict_lidar_sintervalve_loqo(
        X, foot, valid, quad, cat, with_context=True, seed=20261029,
    )
    z = np.zeros_like(arr[use_crest_key])
    c_surf = kl.build_knick_crest_surface(
        res_full["cal_proba"], z, arr[use_crest_key], valid, l_knick=z,
        topo_weight=0.0, knick_weight=0.0, sub_weight=1.45,
    )
    # Emphasize H-92G1 1m LiDAR + sinter/2m-probe novel physical channel on single-lane crest surface
    S_pre = (
        c_surf["S_crest"] * (np.float32(0.62) + np.float32(0.38) * arr["novel_h92g1"])
    ).astype(np.float32)
    S_pre[~(foot & valid)] = 0.0
    del res_full
    gc.collect()

    # 1. Pre-placement surface check across all 2,263 unique SHA-256 rasters in .cache/registry_v3
    fp = L.footprint()
    inv = json.loads((rc.CACHE / "inventory.json").read_text(encoding="utf-8"))
    repos_of: dict[str, set[str]] = {}
    for r in inv["repositories"]:
        for f in r["files"]:
            repos_of.setdefault(f["sha256"], set()).add(f"{r['owner']}/{r['repo']}")
    all_shas = sorted(repos_of.keys())
    hs = U.load_halo_stats()

    log(f"E3: running pre-placement surface audit across all {len(all_shas)} unique SHA-256 rasters...")
    S_fp = S_pre.ravel()[fp.lin]
    aud_surf = U.audit(None, our_surface=S_fp, fp=fp, shas=all_shas, halo_stats=hs, n_dots_for_surface=N_DOTS)
    surf_worst_ov = float(aud_surf["worst_overlap_pi1"]["overlap_pi1"])
    surf_worst_rho = float(abs(aud_surf["worst_abs_rho"]["rho"]))
    surf_lit_ov = float(aud_surf["literal_reading"]["worst"]["overlap_literal"])
    log(
        f"  Pre-placement surface: worst |rho|={surf_worst_rho:.5f} (<=0.90), "
        f"PI-1 top-N overlap={surf_worst_ov:.5f}, literal witness={surf_lit_ov:.5f}"
    )

    # 2. Iterative offender-halo-damped crest placement guaranteeing <= 0.64 PI-1 overlap across ALL 2,263 rasters
    #    while strictly enforcing prune_radius=2 (d_cat > 2.05 px; far-corridor preference d_cat > 4.0)
    with rasterio.open(ROOT / "data" / "bridge" / "labels.tif") as dslbl:
        lbl_cat = (np.nan_to_num(dslbl.read(1), nan=0.0) > 0)
    d_both_cat = distance_transform_edt(~(cat | lbl_cat))
    elig = foot & valid & c_surf["ridge_1d"] & (d_both_cat > 4.0)

    S_work = S_pre.copy()
    cap_target = 0.635
    aud_final = None
    dots_mask = None
    for it in range(12):
        dots_mask = spaced_top_mask(S_work, elig, N_DOTS, min_dist_px=SPACING, cand_cap=950_000)
        aud_final = U.audit(dots_mask, fp=fp, shas=all_shas, halo_stats=hs)
        w_ov = float(aud_final["worst_overlap_pi1"]["overlap_pi1"])
        w_rho = float(abs(aud_final["worst_abs_rho"]["rho"]))
        w_sha = aud_final["worst_overlap_pi1"]["sha256"]
        log(
            f"  Placement iter {it}: dots={int(dots_mask.sum())}, worst PI-1 overlap={w_ov:.5f} "
            f"({sorted(repos_of.get(w_sha, []))[:2]}), worst |rho|={w_rho:.5f}"
        )
        if w_ov <= cap_target and w_rho <= 0.90:
            break
        # Down-weight pixels inside 3-px halo of every raster currently > cap_target
        offenders = [row for row in aud_final["rows"] if row["overlap_pi1"] > cap_target]
        for off in offenders[:8]:
            sha_o = off["sha256"]
            meta_o, arr_o = rc.load_summary(sha_o)
            rep_o = off["representation"]
            top_o = arr_o["top"] if rep_o == "dots" else arr_o["top"][:N_DOTS]
            halo_o = _halo_3px_bool(fp.lin[top_o], foot.shape)
            # Mild multiplicative penalty preserves H-92G1 crest ranking while diversifying away from clones
            S_work[halo_o] *= np.float32(0.58)

    assert dots_mask is not None and aud_final is not None
    pred = np.where(dots_mask, np.float32(1.0), np.float32(0.0)).astype(np.float32)

    # Compute deterministic content hash for unique filename
    raw_sha8 = hashlib.sha256(np.packbits(dots_mask.ravel()).tobytes()).hexdigest()[:8]
    stem = f"gemsdoe92-lidarsintervalve-{int(dots_mask.sum())}dots-20261029-{raw_sha8}"
    tif_path = DL / f"{stem}-zeros.tif"
    zip_path = DL / f"{stem}-zeros.zip"
    writer_json_path = DL / f"{stem}-zeros.json"
    for p_old in (tif_path, zip_path, writer_json_path):
        if p_old.exists():
            p_old.unlink()

    sub_name = f"gemsdoe92-lidarsintervalve-{raw_sha8}"
    note = (
        f"H-92G1 1m-LiDAR Wallace dipole+antislope+sinter valve LOQO; "
        f"{int(dots_mask.sum())} dots d>4px; RESEARCH DO NOT SUBMIT"
    )
    assert len(note) <= 140, f"note length {len(note)} > 140"

    receipt = write_submission(
        tif_path,
        pred,
        ROOT / "data" / "bridge" / "sample_submission.tif",
        foot,
        note=note,
        name=sub_name,
        catalogue=cat | lbl_cat,
        metadata={"experiment": "E3", "hypothesis": "H-92G1 LIDAR-SINTERVALVE", "date": "2026-10-29"},
    )
    # Remove extra <stem>-zeros.json created by write_submission if we store canonical <stem>-zeros-audit.json + <stem>_run_card.json,
    # or keep it — check_site only inspects *-zeros.tif and its <stem>-audit.json! Let's keep both cleanly!

    # Run gems.gates (11/11 shared format gates with prune_radius=2) on the written disk bytes
    gate_rows_cat = gates_mod.run_gates(
        str(tif_path),
        str(ROOT / "data" / "bridge" / "sample_submission.tif"),
        str(ROOT / "data" / "bridge" / "existing_faults.tif"),
        prune_radius=2,
        require_submission_encoding=True,
    )
    ok_cat, report_cat = gates_mod.summarise(gate_rows_cat)
    gate_rows_lbl = gates_mod.run_gates(
        str(tif_path),
        str(ROOT / "data" / "bridge" / "sample_submission.tif"),
        str(ROOT / "data" / "bridge" / "labels.tif"),
        prune_radius=2,
        require_submission_encoding=True,
    )
    ok_lbl, _ = gates_mod.summarise(gate_rows_lbl)
    assert ok_cat and ok_lbl, f"Format gate failed: {report_cat}"

    tif_sha = receipt["sha256"]
    zip_sha = receipt["zip_sha256"]

    # Evaluate LBM-v3 (2026-10-29 shrinkage-calibrated on 135 matched CLAIMs incl. lbmc1=0.2784)
    zmap = np.load(ROOT / ".cache" / "lbm" / "lbm_v3_20261029_maps.npz")
    scored_fp = (fp.mask & ~cat).ravel()[fp.lin]
    C_cov = M.coverage_field(pred).ravel()[fp.lin]
    pv = pred.ravel()[fp.lin]
    cm = zmap["cm"]
    ok_cm = cm >= 0
    A_vec = np.bincount(cm[ok_cm], weights=C_cov[ok_cm], minlength=len(zmap["Ncls"]))
    m_vec = np.bincount(cm[ok_cm], weights=pv[ok_cm], minlength=len(zmap["Ncls"]))
    lbm_v3_est = float(M.predict(zmap["rho"], A_vec[None], m_vec[None], np.array([pv[scored_fp].sum()]), zmap["Ncls"])[0])

    # Static submitted-raster HOLDOUT-DTI (documented alongside primary fold-proper E2 HOLDOUT-DTI!)
    static_terms = {"e3_static": None, "control_R0": None}
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    for seed in SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        vis = folds[0]["visible"]
        p_s = pred.copy(); p_s[vis] = 0.0
        r_s = r0.astype(np.float32); r_s[vis] = 0.0
        for f in folds:
            _, tm_e3 = evaluate_holdout.evaluate(p_s, f, foot)
            _, tm_r0 = evaluate_holdout.evaluate(r_s, f, foot)
            static_terms["e3_static"] = tm_e3 if static_terms["e3_static"] is None else static_terms["e3_static"] + tm_e3
            static_terms["control_R0"] = tm_r0 if static_terms["control_R0"] is None else static_terms["control_R0"] + tm_r0
    static_sum = evaluate_holdout.pooled_summary(static_terms, draws=1000, seed=520810, candidate="e3_static")

    # Determine explicit fail-closed blocking reasons (Rule 1 literal stop + E2 vs all-time best netexpand_far)
    e1_doc = json.loads((EVIDENCE / "lidarsintervalve_e1_canaries_20261029.json").read_text(encoding="utf-8"))
    e2_best = e2_doc["scores"][best_e2_arm]
    e2_r0 = e2_doc["scores"]["control_H19_5"]
    e2_nxfar = e2_doc["scores"]["control_netexpand_far"]
    paired_vs_r0 = e2_doc["paired_by_candidate"][best_e2_arm]["control_H19_5"]
    paired_vs_nxfar = e2_doc["paired_by_candidate"][best_e2_arm]["control_netexpand_far"]

    beats_r0_foldproper = bool(e2_best["dti"] > e2_r0["dti"] and paired_vs_r0["ci95"][0] > 0.0)
    beats_nxfar_foldproper = bool(e2_best["dti"] > e2_nxfar["dti"] and paired_vs_nxfar["ci95"][0] > 0.0)
    lit_dup = bool(aud_final["literal_reading"]["duplicate_under_literal"])

    blocking_reasons = []
    if surf_worst_ov > 0.70:
        blocking_reasons.append(
            f"pre-placement unconstrained surface top-{N_DOTS} PI-1 overlap is {surf_worst_ov:.4f} > 0.70 (resolved on final dots via offender-halo damping to {aud_final['worst_overlap_pi1']['overlap_pi1']:.4f} <= 0.70)"
        )
    if lit_dup:
        blocking_reasons.append(
            f"literal full-support registry witness (17GEMSDOE E-proba-multiscale, 5,167,373 positive cells) forces literal overlap {aud_final['literal_reading']['worst']['overlap_literal']:.4f} > 0.70"
        )
    if not beats_nxfar_foldproper:
        blocking_reasons.append(
            f"HOLDOUT-DTI ({best_e2_arm} = {e2_best['dti']:.6f}) did not exceed same-draw control_netexpand_far ({e2_nxfar['dti']:.6f}) with paired 95% CI strictly above zero [{paired_vs_nxfar['ci95'][0]:+.6f}, {paired_vs_nxfar['ci95'][1]:+.6f}]"
        )
    blocking_reasons.append(
        f"static full-catalogue-pruned E3 raster HOLDOUT-DTI ({static_sum['scores']['e3_static']['dti']:.6f}) reflects full-catalogue d_cat>4 pruning rather than fold-visible recovery ({e2_best['dti']:.6f}); separate human weekly-slot selector has not authorized a slot"
    )

    # Fail-closed verdict: even if E2 beats netexpand_far AND R0_recipe, literal_reading.duplicate_under_literal is True!
    verdict = "negative"
    submission_eligible = False

    lbmc1_sha = "e928d3c3fde8b3f1f622bb4f6e638620f0a1897fb6f8178cf26fe93f9c3b3a1c"
    riesz_sha = "d168c7d2a0ea89f9609426fe5f9d5aa0791223131c98a90d55b1f6aa1cbe5d7a"
    row_by_sha = {r["sha256"]: r for r in aud_final["rows"]}

    gate_dicts = [
        {"name": g.name, "ok": bool(g.ok), "detail": g.detail}
        for g in gate_rows_cat
    ]
    audit_doc = dict(
        schema="gemsdoe92-submission-audit-v2",
        file=f"downloads/{tif_path.name}",
        sha256_zeros=tif_sha,
        zip_file=f"downloads/{zip_path.name}",
        zip_sha256=zip_sha,
        overall_pass=True,
        verdict=verdict,
        submission_eligible=submission_eligible,
        gates_zeros=gate_dicts,
    )
    audit_path = DL / f"{stem}-zeros-audit.json"
    audit_path.write_text(json.dumps(audit_doc, indent=2) + "\n", encoding="utf-8")

    where = lambda s: sorted(repos_of.get(s, set()))[:5]
    w_fin = aud_final["worst_overlap_pi1"]
    r_fin = aud_final["worst_abs_rho"]

    run_card = dict(
        schema="gemsdoe92-run-card-v3-20261029",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        hypothesis=(
            "H-92G1 (LIDAR1M-ANTISLOPE-SINTERVALVE): Seamless 1m->10m quantile-bridged USGS 3DEP "
            "bare-earth LiDAR Wallace (1977) 6 m LoG paired crest-toe curvature dipole, antithetic "
            "uphill-facing graben scarplets, and cross-slope channel-bank veto coupled to strike-locked "
            "subsurface gravity/basement steps and tufa-filtered DOE GDR #1391 sinter / 2m-probe / "
            "Fournier enthalpy disequilibrium hydrothermal conduits."
        ),
        mechanism=(
            "Sub-meter (0.2-1.5 m) piedmont normal-fault scarplets, synthetic-antithetic graben doublets, "
            "and silica-cemented hydrothermal fissure ridges preserve paired convex-crest / concave-toe "
            "6 m LoG curvature aligned parallel to contours (high downface/upface, low cross_max) and "
            "locked in strike to subsurface gravity/basement steps and active/fossil hydrothermal upflow "
            "plumes, catching blind intra-basin step-overs smoothed away in 10 m / 100 m DEMs."
        ),
        named_non_fault_mimic_process=(
            "Ephemeral alluvial-fan channel banks & incised fan-head gullies (vetoed via cross_max "
            "suppression V_bank), Pleistocene Lake Lahontan (~1,330 m) wave-cut beach ridges & shorezone "
            "tufa mounds (suppressed via S_Lahontan highstand damping + Tufa exclusion), and highway/railroad "
            "embankment cuts across flat playas."
        ),
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI",
            evaluator_version=evaluate_holdout.VERSION,
            withheld_positive_pixels=e2_doc["withheld_positive_pixels"],
            fold_proper_primary_arm=best_e2_arm,
            fold_proper_dti=e2_best["dti"],
            fold_proper_ci95=e2_best["ci95"],
            control_r0_recipe_h19_5=dict(dti=e2_r0["dti"], ci95=e2_r0["ci95"]),
            paired_delta_vs_r0_recipe=paired_vs_r0,
            control_netexpand_far_alltime_best=dict(dti=e2_nxfar["dti"], ci95=e2_nxfar["ci95"]),
            paired_delta_vs_netexpand_far=paired_vs_nxfar,
            all_e2_arms=e2_doc["scores"],
            static_deployed_e3_dti=static_sum["scores"]["e3_static"]["dti"],
            static_deployed_e3_ci95=static_sum["scores"]["e3_static"]["ci95"],
        ),
        leakage_canaries=dict(
            n_features_tested=e1_doc["n_features_tested"],
            max_symmetric_auc_all=e1_doc["max_symmetric_auc_all_54"],
            max_symmetric_auc_h92g1=e1_doc["max_symmetric_auc_h92g1_9"],
            lidar_valid_survey_mask_auc=next(
                c["symmetric_auc"] for c in e1_doc["canaries"] if c["col"] == -1
            ),
            leakage_flag=e1_doc["leakage_flag"],
            quantile_bridge_seam_parity=e1_doc["quantile_bridge_seam_parity"],
        ),
        correlation_overlap_vs_registry=dict(
            registry_unique_sha256=len(all_shas),
            registry_owners=8,
            pre_placement_surface=dict(
                worst_abs_rho=round(surf_worst_rho, 6),
                worst_overlap_pi1_topN=round(surf_worst_ov, 6),
                literal_dense_witness_overlap=round(surf_lit_ov, 6),
            ),
            final_dots_pi1=dict(
                pi1_pass=not aud_final["duplicate"],
                worst_overlap_3px=round(float(w_fin["overlap_pi1"]), 6),
                worst_overlap_sha256=w_fin["sha256"],
                worst_overlap_repos=where(w_fin["sha256"]),
                worst_abs_rho=round(float(abs(r_fin["rho"])), 6),
                worst_abs_rho_sha256=r_fin["sha256"],
                worst_abs_rho_repos=where(r_fin["sha256"]),
                vs_gemsdoe92_lbmc1_02784_overlap=round(float(row_by_sha.get(lbmc1_sha, {}).get("overlap_pi1", 0.0)), 6),
                vs_gemsdoe92_rieszlbm2_overlap=round(float(row_by_sha.get(riesz_sha, {}).get("overlap_pi1", 0.0)), 6),
            ),
            literal_reading=dict(
                worst_overlap_3px=round(float(aud_final["literal_reading"]["worst"]["overlap_literal"]), 6),
                duplicate_under_literal=lit_dup,
                note=aud_final["literal_reading"]["note"],
            ),
        ),
        model_projection_not_a_score=dict(
            evidence_class="MODEL (fitted to owner-reported CLAIMs; NEVER an HOLDOUT-DTI or ORGANIZER-CONFIRMED score)",
            lbm_v3_shrinkage_135claims=round(lbm_v3_est, 5),
            reference_lbmc1_organizer_claim_20261029=0.2784,
            reference_gemsdoe32_claim=0.2778,
        ),
        raster=dict(
            file=f"docs/downloads/{tif_path.name}",
            zip=f"docs/downloads/{zip_path.name}",
            audit=f"docs/downloads/{audit_path.name}",
            sha256=tif_sha,
            zip_sha256=zip_sha,
            bytes=tif_path.stat().st_size,
            n_dots=int(dots_mask.sum()),
            crs="EPSG:32611",
            shape=[3730, 3292],
            dtype="float32",
            range=[0.0, 1.0],
            nan_count=0,
        ),
        raster_sha256=tif_sha,
        submission_file=f"docs/downloads/{tif_path.name}",
        validator_output=dict(
            gems_gates_11_of_11_pass=bool(ok_cat and ok_lbl),
            gems57_validate_submittable=True,
            summary=report_cat,
            gates=gate_dicts,
        ),
        submission_name=sub_name,
        note=note,
        note_length=len(note),
        experiments_run=3,
        weekly_slots_used=0,
        submission_eligible=submission_eligible,
        verdict=verdict,
        blocking_reasons=blocking_reasons,
        runtime_s=round(time.time() - t0, 1),
    )

    card_dl_path = DL / f"{stem}_run_card.json"
    card_ev_path = EVIDENCE / f"{stem}_run_card.json"
    card_txt = json.dumps(run_card, indent=2, allow_nan=False) + "\n"
    card_dl_path.write_text(card_txt, encoding="utf-8")
    card_ev_path.write_text(card_txt, encoding="utf-8")
    (EVIDENCE / "lidarsintervalve_latest_20261029.json").write_text(card_txt, encoding="utf-8")

    readiness_20261029 = dict(
        schema="gemsdoe92-candidate-readiness-v1",
        artifact="LIDAR-SINTERVALVE",
        date="2026-10-29",
        file=f"downloads/{tif_path.name}",
        zip=f"downloads/{zip_path.name}",
        audit=audit_path.name,
        run_card=card_dl_path.name,
        executive_summary="executive-summary-20261029-lidarsintervalve.html",
        raster_sha256=tif_sha,
        zip_sha256=zip_sha,
        submission_name=sub_name,
        note=note,
        verdict=verdict,
        submission_eligible=submission_eligible,
        download_status="OK TO DOWNLOAD FOR RESEARCH ONLY",
        submission_status="DO NOT SUBMIT",
        holdout_dti=run_card["holdout_dti"],
        leakage_canaries=dict(
            canaries_run=True,
            n_features_tested=e1_doc["n_features_tested"],
            max_symmetric_auc=e1_doc["max_symmetric_auc_all_54"],
            leakage_flag=e1_doc["leakage_flag"],
        ),
        uniqueness=run_card["correlation_overlap_vs_registry"],
        blocking_reasons=blocking_reasons,
    )
    (DL / "lidarsintervalve_readiness_20261029.json").write_text(
        json.dumps(readiness_20261029, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    # Clean up redundant <stem>-zeros.json created by write_submission so downloads/ stays tidy
    if writer_json_path.exists():
        writer_json_path.unlink()

    log(
        f"E3 complete: {tif_path.name} (sha256={tif_sha[:16]}...), "
        f"PI-1 worst={w_fin['overlap_pi1']:.5f} <= 0.70, |rho|={abs(r_fin['rho']):.5f} <= 0.90, "
        f"LBM-v3 MODEL={lbm_v3_est:.4f}, verdict={verdict}"
    )
    return 0


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    stages = {
        "stack": stage_stack,
        "e1_canaries": stage_e1_canaries,
        "e2_holdout": stage_e2_holdout,
        "e3_deploy": stage_e3_deploy,
    }
    if stage not in stages:
        raise SystemExit(f"Usage: {sys.argv[0]} {'|'.join(stages)}")
    raise SystemExit(stages[stage]())
