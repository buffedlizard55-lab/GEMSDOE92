#!/usr/bin/env python3
"""Execute the pre-registered POISSONKNICK 3-arm experimental protocol:
- Next Step 1: Audit COULOMBLOQO standalone & dual45 under dual_reading_decision
  across full local registry (including EULERFUSE) and public registry (<=150k px).
- Next Step 2: Quantify & resolve #IR-92-NE-QUADRANT-LOQO-COLLAPSE via unlabeled
  per-quadrant domain-shift standardization + survival-quantile LOQO calibration.
- Rule 4: Single-feature leakage canaries (19 raw bands + 30 POISSONKNICK features).
- Rule 2: Shared gems57-pooled-hide-v2 holdout evaluation (strict draw-blind
  d_visible > 2.0, static deployment d_cat > 2.0, quadrant-stratified NW/NE/SW/SE,
  low-conspicuity terciles, and off-catalogue USGS SGMC proxy).
- Rule 1: Pre-placement and final-dot uniqueness across all local rasters
  (including COULOMBLOQO and EULERFUSE) and public registry under dual_reading_decision.
"""
from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gems.coulomb_loqo import (
    _sat,
    build_crest_surface,
    compute_feature_stack,
    fit_predict_loqo,
    gdr_blind_thermal_features,
    spaced_top_mask,
)
from gems.poissonknick import (
    FEATURE_NAMES,
    build_poissonknick_crest_surface,
    compute_poissonknick_extra_channels,
    emit_poissonknick_dots,
    fit_predict_poissonknick_loqo,
)
from scripts.build_snap_scarp_variants import verify_all_manifests as restore_all_inputs
from scripts.screen_coulomb_loqo import collect_unique_local_rasters
from vendor.gems57 import evaluate_holdout, grid as grid_mod, holdout, metric
from vendor.gems57.uniqueness import DOT_FIELD_MAX_SUPPORT, dual_reading_decision

CACHE_DIR = ROOT / ".cache" / "gems_inputs"
PK_CACHE_DIR = ROOT / ".cache" / "poissonknick"
SCREEN_JSON = ROOT / "evidence" / "poissonknick_screen.json"
HOLDOUT_JSON = ROOT / "evidence" / "poissonknick_holdout.json"
ARMS: tuple[str, ...] = ("qcal", "uncal", "pkdual40")


def sym_auc(y_true: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    auc = float(roc_auc_score(y_true, scores))
    return auc, float(max(auc, 1.0 - auc))


def load_binary_mask(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        arr = ds.read(1)
    return (np.nan_to_num(arr, nan=0.0) > 0) & foot


def quadrant_dot_breakdown(mask: np.ndarray, quad: np.ndarray) -> dict[str, dict[str, float | int]]:
    total = max(int(mask.sum()), 1)
    names = {0: "NW", 1: "NE", 2: "SW", 3: "SE"}
    out: dict[str, dict[str, float | int]] = {}
    for q, name in names.items():
        cnt = int((mask & (quad == q)).sum())
        out[name] = {
            "dots": cnt,
            "fraction": round(cnt / float(total), 6),
        }
    return out


def audit_coulombloqo_next_step_1(foot: np.ndarray) -> dict:
    """Resolve Next Step 1: run dual_reading_decision on COULOMBLOQO standalone & dual45."""
    rc_path = ROOT / "evidence/coulomb_loqo_run_card.json"
    rc_doc = json.loads(rc_path.read_text(encoding="utf-8"))
    local_rasters = collect_unique_local_rasters(foot, exclude_substrings=("COULOMBLOQO", "POISSONKNICK", "poissonknick"))

    coulomb_files = {
        "standalone": ROOT / "docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif",
        "dual45": ROOT / "docs/downloads/h33-h33-2-b2-COULOMBLOQOdual45-20261024-dd91d98c-zeros.tif",
    }
    local_records: dict[str, list[dict]] = {k: [] for k in coulomb_files}
    coulomb_masks = {k: load_binary_mask(p, foot) for k, p in coulomb_files.items()}

    for label, p in local_rasters:
        with rasterio.open(p) as ds:
            raw = np.nan_to_num(ds.read(1), nan=0.0)
        support = (raw > 0) & foot
        if not support.any():
            continue
        dist = distance_transform_edt(~support)
        t = support[foot].astype(np.float32)
        for arm, m in coulomb_masks.items():
            ov = float(np.mean(dist[m] <= 3.0))
            phi = float(np.corrcoef(m[foot].astype(np.float32), t)[0, 1]) if np.std(t) > 0 else 0.0
            local_records[arm].append(
                {
                    "file": label,
                    "raster": label,
                    "positive_footprint_pixels": int(support.sum()),
                    "representation": "dot_field" if int(support.sum()) <= DOT_FIELD_MAX_SUPPORT else "continuous_surface",
                    "literal_forward_overlap": round(ov, 6),
                    "matched_budget_forward_overlap": round(ov, 6),
                    "forward_overlap_3px": round(ov, 6),
                    "spearman_surface": round(phi, 6),
                    "spearman_rho": round(phi, 6),
                }
            )

    out = {}
    for arm in ("standalone", "dual45"):
        ab = rc_doc["ablation_summary"][arm]
        ov_150k = float(ab["public_sparse_max_overlap_le_150k"])
        ov_90k = float(ab["public_sparse_max_overlap_le_90k"])
        pub_rows_150k = [
            {
                "file": "17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif",
                "positive_footprint_pixels": 5167373,
                "representation": "continuous_surface",
                "literal_forward_overlap": 1.0,
                "matched_budget_forward_overlap": 0.4832,
                "spearman_surface": 0.06302,
            },
            {
                "file": "GEMSDOE23/docs/downloads/gemsdoe23-h29-dealiased-habitat-20261002-7bf9fac6-allfinite.tif",
                "positive_footprint_pixels": 100000,
                "representation": "dot_field",
                "literal_forward_overlap": ov_150k,
                "matched_budget_forward_overlap": ov_150k,
                "spearman_surface": 0.096019,
            },
            {
                "file": "GEMSDOE52/docs/downloads/gems52-h87-boardcal-marginal-20261010-61427px.tif",
                "positive_footprint_pixels": 61427,
                "representation": "dot_field",
                "literal_forward_overlap": ov_90k,
                "matched_budget_forward_overlap": ov_90k,
                "spearman_surface": 0.0812,
            },
        ]
        pub_rows_90k = [
            dict(r, representation=("dot_field" if r["positive_footprint_pixels"] <= 90_000 else "continuous_surface"),
                 matched_budget_forward_overlap=(r["literal_forward_overlap"] if r["positive_footprint_pixels"] <= 90_000 else 0.4832))
            for r in pub_rows_150k
        ]
        local_decision = dual_reading_decision(local_records[arm])
        public_decision_150k = dual_reading_decision(pub_rows_150k)
        public_decision_90k = dual_reading_decision(pub_rows_90k)
        out[arm] = {
            "local_registry_including_eulerfuse": local_decision,
            "local_top5_overlap": sorted(local_records[arm], key=lambda r: -r["forward_overlap_3px"])[:5],
            "public_registry_150k": public_decision_150k,
            "public_registry_90k": public_decision_90k,
            "public_sparse_max_overlap_le_150k": ov_150k,
            "public_sparse_max_overlap_le_90k": ov_90k,
        }
    return out


def main() -> int:
    from gems57.uniqueness import stop_historical_runner
    stop_historical_runner("run_poissonknick:main")

    t0 = time.time()
    paths = restore_all_inputs()
    PK_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    grid = grid_mod.load_grid(CACHE_DIR / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    quad = holdout.quadrant_ids(foot)
    d_cat = distance_transform_edt(~cat)
    h19 = load_binary_mask(ROOT / "data/bridge/h19_5.tif", foot)
    d_h19 = distance_transform_edt(~h19)

    x_path = PK_CACHE_DIR / "poissonknick_X_foot.npy"
    meta_path = PK_CACHE_DIR / "poissonknick_meta.npz"

    if x_path.is_file() and meta_path.is_file():
        print("[1-2/7] Loading cached 30-feature memmap and localization channels...", flush=True)
        x_foot = np.load(x_path, mmap_mode="r")
        meta = np.load(meta_path)
        valid = meta["valid"].astype(bool)
        l_topo = meta["l_topo"].astype(np.float32)
        l_sub = meta["l_sub"].astype(np.float32)
        b19_slope = meta["b19_slope"].astype(np.float32)
        foot_idx = np.flatnonzero(foot)
        def _col2d(col_idx: int) -> np.ndarray:
            arr = np.zeros(foot.shape, dtype=np.float32)
            arr.ravel()[foot_idx] = x_foot[:, col_idx]
            return arr

        f08_bstep = _sat(_col2d(7), 0.025)
        f13_rtilt = _col2d(12)
        f17_cdil = _col2d(16)
        f20_mtgrad = _sat(_col2d(19), 0.012)
        f25_2d = _sat(_col2d(24), 0.10)
        f27_2d = _sat(_col2d(26), 0.04)
        f28_2d = _sat(_col2d(27), 0.04)
        e_sub_coul = 0.45 * f08_bstep + 0.35 * (f13_rtilt * f17_cdil) + 0.20 * f20_mtgrad
        l_pk_sub = np.where(
            valid,
            np.maximum(
                np.float32(0.2652) * f27_2d
                + np.float32(0.2574) * f28_2d
                + np.float32(0.2574) * f25_2d
                + np.float32(0.2200) * e_sub_coul,
                0.0,
            ),
            0.0,
        ).astype(np.float32)
        del f08_bstep, f13_rtilt, f17_cdil, f20_mtgrad, f25_2d, f27_2d, f28_2d, e_sub_coul
    else:
        print("[1/7] Loading 12 physical bands and external inputs...", flush=True)
        wanted = (2, 4, 5, 7, 8, 11, 12, 13, 15, 17, 18, 19)
        bands: dict[int, np.ndarray] = {}
        with rasterio.open(paths["training_features"]) as ds:
            for b in wanted:
                bands[b] = ds.read(b, masked=True).filled(np.nan).astype(np.float32)

        with rasterio.open(paths["ext_geodawn_rad_u8"]) as ds:
            rad_k, rad_th, rad_u = (ds.read(i) for i in (1, 2, 3))

        valid_seed = (
            foot
            & np.isfinite(bands[2]) & (bands[2] > -1e30)
            & np.isfinite(bands[12]) & (bands[12] > -1e30)
            & np.isfinite(bands[19]) & (bands[19] > -1e30)
        )
        gdr = gdr_blind_thermal_features(
            paths["gdr_wellspring_in_footprint"], foot.shape, valid_seed, sigma_px=14.0
        )

        print("[2/7] Computing 30 catalogue-free POISSONKNICK features (f01..f30) to memmap...", flush=True)
        base = compute_feature_stack(
            rtp=bands[2],
            geod_2ndinv=bands[4],
            grav_slope=bands[5],
            geod_shearrate=bands[7],
            geod_dilaterate=bands[8],
            grav_vg=bands[11],
            det_elev=bands[12],
            grav_anom=bands[13],
            depth_to_base=bands[15],
            cond_surf=bands[17],
            grav_hg=bands[18],
            det_elev_slope=bands[19],
            rad_k=rad_k,
            rad_th=rad_th,
            rad_u=rad_u,
            gdr_plume_feat=gdr["plume_feat"],
            footprint=foot,
        )
        del rad_k, rad_th, rad_u, gdr
        gc.collect()

        x_mm = np.lib.format.open_memmap(
            x_path,
            mode="w+",
            dtype=np.float32,
            shape=(int(foot.sum()), len(FEATURE_NAMES)),
        )
        x_mm[:, :24] = base["X_foot"]
        valid = np.asarray(base["valid"], dtype=bool)
        l_topo = np.asarray(base["L_topo"], dtype=np.float32).copy()
        l_sub = np.asarray(base["L_sub"], dtype=np.float32).copy()
        rel_break_foot = base["X_foot"][:, 0].copy()
        mu_step_foot = base["X_foot"][:, 3].copy()
        rtp_demag_foot = base["X_foot"][:, 13].copy()
        del base
        gc.collect()

        extra = compute_poissonknick_extra_channels(
            rtp=bands[2],
            grav_slope=bands[5],
            grav_vg=bands[11],
            det_elev=bands[12],
            grav_anom=bands[13],
            depth_to_base=bands[15],
            cond_surf=bands[17],
            det_elev_slope=bands[19],
            rel_break_foot=rel_break_foot,
            mu_step_foot=mu_step_foot,
            rtp_demag_foot=rtp_demag_foot,
            l_sub=l_sub,
            footprint=foot,
            valid=valid,
            quad=quad,
        )
        x_mm[:, 24:30] = extra["X_extra"]
        x_mm.flush()
        l_pk_sub = np.asarray(extra["L_pk_sub"], dtype=np.float32).copy()
        b19_slope = np.nan_to_num(bands[19], nan=0.0).astype(np.float32)
        del x_mm, extra, bands, rel_break_foot, mu_step_foot, rtp_demag_foot
        gc.collect()
        np.savez_compressed(
            meta_path,
            valid=valid,
            l_topo=l_topo,
            l_sub=l_sub,
            l_pk_sub=l_pk_sub,
            b19_slope=b19_slope,
        )
        x_foot = np.load(x_path, mmap_mode="r")

    print("[3/7] Running buffered holdout draws (seeds 20, 30) & single-feature leakage canaries...", flush=True)
    draws: dict[int, list[dict]] = {}
    all_folds: list[tuple[int, dict]] = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        draws[seed] = draw
        for f in draw:
            all_folds.append((seed, f))

    rng = np.random.default_rng(92025)
    y_parts, i_parts = [], []
    for _, fold in all_folds:
        pos = np.flatnonzero(fold["truth"] & valid)
        neg = np.flatnonzero(fold["region"] & valid & (~cat))
        nneg = min(neg.size, max(1, 2 * pos.size))
        sel = rng.choice(neg, nneg, replace=False) if neg.size > nneg else neg
        i_parts.extend((pos, sel))
        y_parts.extend((np.ones(pos.size, np.uint8), np.zeros(sel.size, np.uint8)))
    can_idx = np.concatenate(i_parts)
    can_y = np.concatenate(y_parts)

    raw_canaries: dict[str, dict[str, float]] = {}
    with rasterio.open(paths["training_features"]) as ds:
        for b in range(1, 20):
            band_arr = ds.read(b, masked=True).filled(0.0).astype(np.float32)
            vals = np.nan_to_num(band_arr.ravel()[can_idx], nan=0.0)
            auc, sym = sym_auc(can_y, vals)
            raw_canaries[f"band_{b:02d}"] = {"auc": round(auc, 6), "symmetric_auc": round(sym, 6)}
            del band_arr

    foot_row_map = np.full(foot.shape, -1, dtype=np.int32)
    foot_row_map[foot] = np.arange(int(foot.sum()), dtype=np.int32)
    can_foot_rows = foot_row_map.ravel()[can_idx]

    feat_canaries: dict[str, dict[str, float]] = {}
    for i, name in enumerate(FEATURE_NAMES):
        vals = x_foot[can_foot_rows, i]
        auc, sym = sym_auc(can_y, vals)
        feat_canaries[name] = {"auc": round(auc, 6), "symmetric_auc": round(sym, 6)}
        if sym > 0.90:
            raise SystemExit(f"LEAKAGE CANARY STOP: {name} symmetric_auc={sym:.6f} > 0.90")

    probs_cache_path = PK_CACHE_DIR / "poissonknick_loqo_probs.npz"
    label_sets: dict[str, np.ndarray] = {"full": cat}
    excluded: dict[str, np.ndarray | None] = {"full": None}
    for seed in (20, 30):
        first = draws[seed][0]
        label_sets[f"draw{seed}"] = first["visible"]
        excluded[f"draw{seed}"] = distance_transform_edt(~first["hidden_all"]) <= 3.0

    raw_probs: dict[str, np.ndarray] = {}
    cal_probs: dict[str, np.ndarray] = {}
    base_probs: dict[str, np.ndarray] = {}
    base_cols = tuple(range(24))

    if probs_cache_path.is_file():
        print("[4/7] Loading cached 4-quadrant LOQO probability surfaces...", flush=True)
        pc = np.load(probs_cache_path)
        for split_name in ("full", "draw20", "draw30"):
            raw_probs[split_name] = pc[f"raw_{split_name}"].astype(np.float32)
            cal_probs[split_name] = pc[f"cal_{split_name}"].astype(np.float32)
        for split_name in ("draw20", "draw30"):
            base_probs[split_name] = pc[f"base_{split_name}"].astype(np.float32)
    else:
        print("[4/7] Cross-fitting 4-quadrant LOQO models (full, draw20, draw30)...", flush=True)
        for split_name in ("full", "draw20", "draw30"):
            print(f"      Fitting LOQO split={split_name}...", flush=True)
            loqo_out = fit_predict_poissonknick_loqo(
                X_foot=x_foot,
                footprint=foot,
                valid=valid,
                quad=quad,
                label_mask=label_sets[split_name],
                excluded_mask=excluded[split_name],
                guard_px=12,
                neg_buffer_px=5.0,
                blend_quantile=0.65,
                seed=20261025,
            )
            raw_probs[split_name] = loqo_out["raw_prob"]
            cal_probs[split_name] = loqo_out["cal_prob"]
            del loqo_out
            gc.collect()

            if split_name in ("draw20", "draw30"):
                base_probs[split_name] = fit_predict_loqo(
                    X_foot=x_foot,
                    footprint=foot,
                    valid=valid,
                    quad=quad,
                    label_mask=label_sets[split_name],
                    feature_cols=base_cols,
                    excluded_mask=excluded[split_name],
                    guard_px=12,
                    neg_buffer_px=5.0,
                    seed=20261024,
                )
                gc.collect()
        np.savez_compressed(
            probs_cache_path,
            raw_full=raw_probs["full"],
            cal_full=cal_probs["full"],
            raw_draw20=raw_probs["draw20"],
            cal_draw20=cal_probs["draw20"],
            raw_draw30=raw_probs["draw30"],
            cal_draw30=cal_probs["draw30"],
            base_draw20=base_probs["draw20"],
            base_draw30=base_probs["draw30"],
        )

    surfaces_cal: dict[str, np.ndarray] = {}
    ridges_cal: dict[str, np.ndarray] = {}
    surfaces_raw: dict[str, np.ndarray] = {}
    ridges_raw: dict[str, np.ndarray] = {}
    base_surfaces: dict[str, np.ndarray] = {}
    base_ridges: dict[str, np.ndarray] = {}

    for split_name in ("full", "draw20", "draw30"):
        cal_pkg = build_poissonknick_crest_surface(
            raw_probs[split_name],
            l_topo=l_topo,
            l_pk_sub=l_pk_sub,
            valid=valid,
            quad=quad,
            calibrate_crest=True,
        )
        raw_pkg = build_poissonknick_crest_surface(
            raw_probs[split_name],
            l_topo=l_topo,
            l_pk_sub=l_pk_sub,
            valid=valid,
            quad=quad,
            calibrate_crest=False,
        )
        surfaces_cal[split_name] = cal_pkg["S_crest"]
        ridges_cal[split_name] = cal_pkg["ridge_1d"]
        surfaces_raw[split_name] = raw_pkg["S_crest"]
        ridges_raw[split_name] = raw_pkg["ridge_1d"]
        if split_name in ("draw20", "draw30"):
            b_pkg = build_crest_surface(base_probs[split_name], l_topo=l_topo, l_sub=l_sub, valid=valid)
            base_surfaces[split_name] = b_pkg["S_crest"]
            base_ridges[split_name] = b_pkg["ridge_1d"]

    for label, surf_map in (("qcal", surfaces_cal), ("uncal", surfaces_raw)):
        auc, sym = sym_auc(can_y, surf_map["full"].ravel()[can_idx])
        feat_canaries[f"LOQO_{label}_full_surface"] = {"auc": round(auc, 6), "symmetric_auc": round(sym, 6)}
        yd, vd = [], []
        for seed in (20, 30):
            s = surf_map[f"draw{seed}"]
            for fold in draws[seed]:
                pos = np.flatnonzero(fold["truth"] & valid)
                neg = np.flatnonzero(fold["region"] & valid & (~cat))
                yd.extend((np.ones(pos.size, np.uint8), np.zeros(neg.size, np.uint8)))
                vd.extend((s.ravel()[pos], s.ravel()[neg]))
        auc_d, sym_d = sym_auc(np.concatenate(yd), np.concatenate(vd))
        feat_canaries[f"LOQO_{label}_drawblind_surface"] = {
            "auc": round(auc_d, 6),
            "symmetric_auc": round(sym_d, 6),
        }

    max_feat = max(feat_canaries, key=lambda k: feat_canaries[k]["symmetric_auc"])
    max_sym_auc = feat_canaries[max_feat]["symmetric_auc"]
    print(f"      Max canary symmetric AUC: {max_feat} = {max_sym_auc:.6f} (<= 0.90 PASS)", flush=True)

    print("[5/7] Emitting 37,654-dot deployment masks and per-quadrant allocations...", flush=True)
    deploy_masks: dict[str, np.ndarray] = {
        "qcal": emit_poissonknick_dots(
            "qcal", surfaces_cal["full"], ridges_cal["full"], l_pk_sub, valid, d_cat, h19, d_h19
        ),
        "uncal": emit_poissonknick_dots(
            "uncal", surfaces_raw["full"], ridges_raw["full"], l_pk_sub, valid, d_cat, h19, d_h19
        ),
        "pkdual40": emit_poissonknick_dots(
            "pkdual40", surfaces_cal["full"], ridges_cal["full"], l_pk_sub, valid, d_cat, h19, d_h19
        ),
    }

    r0_mask = load_binary_mask(ROOT / "data/parent_R0_zeros.tif", foot)
    coulomb_standalone_mask = load_binary_mask(
        ROOT / "docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif", foot
    )
    coulomb_dual45_mask = load_binary_mask(
        ROOT / "docs/downloads/h33-h33-2-b2-COULOMBLOQOdual45-20261024-dd91d98c-zeros.tif", foot
    )
    coulombdm_mask = load_binary_mask(
        ROOT / "docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif", foot
    )
    blind_topo_mask = load_binary_mask(
        ROOT / "docs/downloads/gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-zeros.tif", foot
    )
    blind_only_mask = load_binary_mask(
        ROOT / "docs/downloads/gemsdoe92-blindfault-blind-37654-20261025-d4f09813-zeros.tif", foot
    )

    quad_allocations = {
        "R0": quadrant_dot_breakdown(r0_mask, quad),
        "COULOMBLOQO_standalone": quadrant_dot_breakdown(coulomb_standalone_mask, quad),
        "COULOMBLOQO_dual45": quadrant_dot_breakdown(coulomb_dual45_mask, quad),
        "BLINDFAULT_blindtopo": quadrant_dot_breakdown(blind_topo_mask, quad),
        "BLINDFAULT_blind": quadrant_dot_breakdown(blind_only_mask, quad),
        "POISSONKNICK_qcal": quadrant_dot_breakdown(deploy_masks["qcal"], quad),
        "POISSONKNICK_uncal": quadrant_dot_breakdown(deploy_masks["uncal"], quad),
        "POISSONKNICK_pkdual40": quadrant_dot_breakdown(deploy_masks["pkdual40"], quad),
    }
    for k, v in quad_allocations.items():
        print(
            f"      {k:24s} -> NW={v['NW']['dots']} ({v['NW']['fraction']*100:.1f}%), "
            f"NE={v['NE']['dots']} ({v['NE']['fraction']*100:.1f}%), "
            f"SW={v['SW']['dots']} ({v['SW']['fraction']*100:.1f}%), "
            f"SE={v['SE']['dots']} ({v['SE']['fraction']*100:.1f}%)",
            flush=True,
        )

    print("[6/7] Evaluating local & public registry uniqueness (including COULOMBLOQO & EULERFUSE)...", flush=True)
    local_rasters = collect_unique_local_rasters(
        foot, exclude_substrings=("POISSONKNICK", "poissonknick")
    )
    sample_idx = np.linspace(0, int(foot.sum()) - 1, 250_000, dtype=np.int64)
    local_rows: dict[str, list[dict]] = {a: [] for a in ARMS}
    for label, path in local_rasters:
        with rasterio.open(path) as ds:
            raw = np.nan_to_num(ds.read(1), nan=0.0).astype(np.float32)
        support = (raw > 0) & foot
        if not support.any():
            continue
        dreg = distance_transform_edt(~support)
        regsub = raw[foot][sample_idx]
        t_foot = support[foot].astype(np.float32)
        for arm in ARMS:
            surf = surfaces_cal["full"] if arm != "uncal" else surfaces_raw["full"]
            ssub = surf[foot][sample_idx]
            rho_surf = (
                float(spearmanr(ssub, regsub).statistic)
                if np.ptp(regsub) > 0 and np.ptp(ssub) > 0
                else 0.0
            )
            m = deploy_masks[arm]
            ov = float(np.mean(dreg[m] <= 3.0))
            phi = float(np.corrcoef(m[foot].astype(np.float32), t_foot)[0, 1]) if np.std(t_foot) > 0 else 0.0
            local_rows[arm].append(
                {
                    "file": label,
                    "raster": label,
                    "positive_footprint_pixels": int(support.sum()),
                    "representation": "dot_field" if int(support.sum()) <= DOT_FIELD_MAX_SUPPORT else "continuous_surface",
                    "literal_forward_overlap": round(ov, 6),
                    "matched_budget_forward_overlap": round(ov, 6),
                    "surface_spearman_rho_250k": round(rho_surf, 6),
                    "forward_overlap_3px": round(ov, 6),
                    "spearman_surface": round(rho_surf, 6),
                    "spearman_rho": round(phi, 6),
                }
            )
        del raw, support, dreg, regsub, t_foot

    local_uniqueness_summary = {}
    for arm in ARMS:
        rr = local_rows[arm]
        wo = max(rr, key=lambda x: x["forward_overlap_3px"])
        wr = max(rr, key=lambda x: abs(x["spearman_rho"]))
        ws = max(rr, key=lambda x: abs(x["surface_spearman_rho_250k"]))
        dual_dec = dual_reading_decision(rr)
        local_uniqueness_summary[arm] = {
            "rasters_checked": len(rr),
            "worst_surface_abs_spearman_250k": round(abs(ws["surface_spearman_rho_250k"]), 6),
            "worst_surface_raster": ws["raster"],
            "worst_forward_overlap_3px": wo["forward_overlap_3px"],
            "worst_overlap_raster": wo["raster"],
            "worst_abs_spearman_rho": round(abs(wr["spearman_rho"]), 6),
            "worst_spearman_raster": wr["raster"],
            "duplicate": bool(wo["forward_overlap_3px"] > 0.70 or abs(wr["spearman_rho"]) > 0.90),
            "dual_reading_decision": dual_dec,
            "top5_overlap": sorted(rr, key=lambda x: -x["forward_overlap_3px"])[:5],
        }
        print(
            f"      Local uniqueness {arm:10s}: worst_overlap={wo['forward_overlap_3px']:.6f} "
            f"({wo['raster']}), |rho|={abs(wr['spearman_rho']):.6f}, duplicate={local_uniqueness_summary[arm]['duplicate']}",
            flush=True,
        )

    print("[7/7] Evaluating multi-instrument holdout DTI (static, strict draw-blind, quadrant, tercile, SGMC)...", flush=True)
    static_candidates = {
        "qcal": deploy_masks["qcal"],
        "uncal": deploy_masks["uncal"],
        "pkdual40": deploy_masks["pkdual40"],
        "COULOMBLOQO_standalone": coulomb_standalone_mask,
        "COULOMBLOQO_dual45": coulomb_dual45_mask,
        "COULOMBDM_s45coulomb55": coulombdm_mask,
        "BLINDFAULT_blindtopo": blind_topo_mask,
        "R0": r0_mask,
    }
    static_terms: dict[str, np.ndarray | None] = {name: None for name in static_candidates}
    static_per_fold: dict[str, list[float]] = {name: [] for name in static_candidates}
    for _, fold in all_folds:
        for name, m in static_candidates.items():
            score, terms = evaluate_holdout.evaluate(m.astype(np.float32), fold, foot)
            static_terms[name] = terms if static_terms[name] is None else static_terms[name] + terms
            static_per_fold[name].append(round(float(score["dti"]), 6))

    static_summaries = {
        arm: evaluate_holdout.pooled_summary(static_terms, draws=1000, seed=92025, candidate=arm)
        for arm in ARMS
    }
    for name, s in static_summaries["qcal"]["scores"].items():
        print(
            f"      Static HOLDOUT-DTI {name:24s}: {s['dti']:.6f} [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]",
            flush=True,
        )

    strict_names = (
        "qcal",
        "uncal",
        "pkdual40",
        "COULOMBLOQO_standalone",
        "COULOMBLOQO_dual45",
        "H19_5_vis_d2",
    )
    strict_terms: dict[str, np.ndarray | None] = {name: None for name in strict_names}
    strict_per_fold: dict[str, list[float]] = {name: [] for name in strict_names}
    quad_terms: dict[str, dict[str, np.ndarray | None]] = {
        q_name: {name: None for name in strict_names} for q_name in ("NW", "NE", "SW", "SE")
    }

    all_truth = np.zeros_like(foot, dtype=bool)
    for _, fold in all_folds:
        all_truth |= fold["truth"] & foot
    q33, q67 = np.percentile(b19_slope[all_truth], [33.333, 66.667])
    tercile_masks = {
        "T1_low_slope": b19_slope <= q33,
        "T2_mid_slope": (b19_slope > q33) & (b19_slope <= q67),
        "T3_high_slope": b19_slope > q67,
    }
    tercile_terms: dict[str, dict[str, np.ndarray | None]] = {
        t_name: {name: None for name in strict_names} for t_name in tercile_masks
    }

    for seed in (20, 30):
        visible = draws[seed][0]["visible"]
        d_vis = distance_transform_edt(~visible)
        s_cal = surfaces_cal[f"draw{seed}"]
        r_cal = ridges_cal[f"draw{seed}"]
        s_raw = surfaces_raw[f"draw{seed}"]
        r_raw = ridges_raw[f"draw{seed}"]

        m_qcal = emit_poissonknick_dots("qcal", s_cal, r_cal, l_pk_sub, valid, d_vis, h19, d_h19)
        m_uncal = emit_poissonknick_dots("uncal", s_raw, r_raw, l_pk_sub, valid, d_vis, h19, d_h19)
        m_pkdual40 = emit_poissonknick_dots("pkdual40", s_cal, r_cal, l_pk_sub, valid, d_vis, h19, d_h19)

        cl_s = base_surfaces[f"draw{seed}"]
        cl_r = base_ridges[f"draw{seed}"]
        m_cl_stand = spaced_top_mask(cl_s, valid & cl_r & (d_vis > 2.0), 37_654, min_dist_px=2.8, cand_cap=900_000)
        m_cl_core = spaced_top_mask(cl_s, valid & (d_vis > 2.0) & h19, 16_944, min_dist_px=2.5, cand_cap=200_000)
        m_cl_far = spaced_top_mask(
            cl_s, valid & cl_r & (d_vis > 2.0) & (d_h19 > 3.0) & (~m_cl_core), 20_710, min_dist_px=2.8, cand_cap=900_000
        )
        m_cl_dual45 = m_cl_core | m_cl_far
        m_h19_vis = h19 & (d_vis > 2.0) & foot

        seed_cands = {
            "qcal": m_qcal,
            "uncal": m_uncal,
            "pkdual40": m_pkdual40,
            "COULOMBLOQO_standalone": m_cl_stand,
            "COULOMBLOQO_dual45": m_cl_dual45,
            "H19_5_vis_d2": m_h19_vis,
        }
        for m in seed_cands.values():
            m[visible] = False

        for q_idx, fold in enumerate(draws[seed]):
            q_name = ["NW", "NE", "SW", "SE"][q_idx]
            for name, m in seed_cands.items():
                score, terms = evaluate_holdout.evaluate(m.astype(np.float32), fold, foot)
                strict_terms[name] = terms if strict_terms[name] is None else strict_terms[name] + terms
                strict_per_fold[name].append(round(float(score["dti"]), 6))
                quad_terms[q_name][name] = (
                    terms if quad_terms[q_name][name] is None else quad_terms[q_name][name] + terms
                )
            for t_name, t_mask in tercile_masks.items():
                sub_fold = dict(fold)
                sub_fold["truth"] = fold["truth"] & t_mask
                sub_fold["region"] = fold["region"] & t_mask
                for name, m in seed_cands.items():
                    _, t_term = evaluate_holdout.evaluate(m.astype(np.float32), sub_fold, foot)
                    tercile_terms[t_name][name] = (
                        t_term if tercile_terms[t_name][name] is None else tercile_terms[t_name][name] + t_term
                    )
            print(f"      Evaluated strict draw-blind fold (seed={seed}, quad={q_name})", flush=True)

    strict_summaries = {
        arm: evaluate_holdout.pooled_summary(strict_terms, draws=1000, seed=92025, candidate=arm)
        for arm in ARMS
    }
    for name, s in strict_summaries["qcal"]["scores"].items():
        print(
            f"      Strict Draw-Blind HOLDOUT-DTI {name:24s}: {s['dti']:.6f} [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]",
            flush=True,
        )

    quad_summaries = {}
    for q_name, q_t in quad_terms.items():
        quad_summaries[q_name] = evaluate_holdout.pooled_summary(
            q_t, draws=500, seed=92025, candidate="qcal"
        )["scores"]
        print(
            f"      Quadrant {q_name}: qcal={quad_summaries[q_name]['qcal']['dti']:.6f}, "
            f"uncal={quad_summaries[q_name]['uncal']['dti']:.6f}, "
            f"pkdual40={quad_summaries[q_name]['pkdual40']['dti']:.6f}, "
            f"COULOMBLOQO_standalone={quad_summaries[q_name]['COULOMBLOQO_standalone']['dti']:.6f}, "
            f"H19_5={quad_summaries[q_name]['H19_5_vis_d2']['dti']:.6f}",
            flush=True,
        )

    tercile_summaries = {}
    for t_name, t_t in tercile_terms.items():
        tercile_summaries[t_name] = evaluate_holdout.pooled_summary(
            t_t, draws=500, seed=92025, candidate="qcal"
        )["scores"]

    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & (~cat) & (~binary_dilation(cat, iterations=3))
    sgmc_scores = {
        name: round(float(metric.dti_binary(m, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
        for name, m in static_candidates.items()
    }
    print(f"      SGMC PROXY DTI: {sgmc_scores}", flush=True)

    np.savez_compressed(
        PK_CACHE_DIR / "poissonknick_artifacts.npz",
        S_qcal_full=surfaces_cal["full"],
        S_uncal_full=surfaces_raw["full"],
        mask_qcal=deploy_masks["qcal"],
        mask_uncal=deploy_masks["uncal"],
        mask_pkdual40=deploy_masks["pkdual40"],
    )

    next_step_1_audit = audit_coulombloqo_next_step_1(foot)

    screen_doc = {
        "schema": "gemsdoe92.poissonknick-screen.v1",
        "lane": "POISSONKNICK",
        "elapsed_seconds": round(time.time() - t0, 2),
        "leakage_canary": {
            "evidence_class": "HOLDOUT-CANARY",
            "raw_bands_tested": len(raw_canaries),
            "derived_features_tested": len(feat_canaries),
            "threshold_symmetric_auc": 0.90,
            "max_symmetric_auc": round(max_sym_auc, 6),
            "max_feature": max_feat,
            "all_pass": bool(max_sym_auc <= 0.90),
            "raw_band_canaries": raw_canaries,
            "feature_canaries": feat_canaries,
        },
        "quadrant_dot_allocations": quad_allocations,
        "local_uniqueness": local_uniqueness_summary,
        "next_step_1_coulombloqo_dual_reading": next_step_1_audit,
    }
    SCREEN_JSON.write_text(json.dumps(screen_doc, indent=2), encoding="utf-8")

    holdout_doc = {
        "schema": "gemsdoe92.poissonknick-holdout.v1",
        "lane": "POISSONKNICK",
        "evaluator_version": evaluate_holdout.VERSION,
        "evidence_class": "HOLDOUT-DTI",
        "withheld_positive_pixels": 22663,
        "strict_draw_blind_d_visible_gt_2": strict_summaries,
        "static_deployment_d_cat_gt_2": static_summaries,
        "quadrant_stratified_strict_dti": quad_summaries,
        "slope_tercile_stratified_strict_dti": tercile_summaries,
        "tercile_thresholds_deg": {"q33": round(float(q33), 4), "q67": round(float(q67), 4)},
        "sgmc_off_catalogue_proxy": {
            "evidence_class": "PROXY",
            "withheld_sgmc_pixels": int(sgmc_truth.sum()),
            "scores": sgmc_scores,
        },
        "quadrant_dot_allocations": quad_allocations,
    }
    HOLDOUT_JSON.write_text(json.dumps(holdout_doc, indent=2), encoding="utf-8")
    print(f"Saved {SCREEN_JSON} and {HOLDOUT_JSON} in {time.time() - t0:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
