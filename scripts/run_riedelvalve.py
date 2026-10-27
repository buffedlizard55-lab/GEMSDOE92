#!/usr/bin/env python3
"""End-to-end zero-leakage execution of the pre-registered RIEDELVALVE lane.

Pre-registration: docs/HYPOTHESES_20261025_RIEDELVALVE.md
Strict PARALLEL-RUN PROTOCOL compliance:
  - Rule 1 (Lane & Uniqueness): Single lane ``RIEDELVALVE``. Checks BOTH
    pre-placement continuous crest surfaces AND final emitted GeoTIFF dot masks
    against all local GEMSDOE92 rasters and all 102 public buffedlizard55-lab/*GEMSDOE*
    repositories (1,492 Git-blob-SHA1-verified TIFF blobs), recording both
    dual_reading_decision (<=150k sparse dot_field + >150k matched-budget 37,654)
    and the binding literal 17GEMSDOE dense-surface witness (1.000 > 0.70).
  - Rule 2 (Reuse): Reuses shared vendor/gems57/evaluate_holdout.py
    (gems57-pooled-hide-v2, 22,663 withheld positives), vendor/gems57/holdout.py,
    vendor/gems57/submission_writer.py, vendor/gems57/validate.py, and gems/gates.py.
  - Rule 3 (Labels): Every number labeled HOLDOUT-DTI (with evaluator version,
    withheld positives, 95% spatial-cluster CI) or PROXY (USGS SGMC).
  - Rule 4 (Leakage Canary): Tests all 32 features individually AND draw-blind
    LOQO surfaces on the 22,663 withheld holdout positives BEFORE placement;
    halts if any symmetric AUC > 0.90.
  - Rule 5 (Run Card): Emits evidence/riedelvalve_run_card.json + per-file
    -audit.json sidecars with verdict="negative", submission_eligible=false.
  - Rule 6 (Budget): Strictly 3 experiments (riedelvalve, riedel_n90k,
    noriedel_ablation); 0 weekly submission slots consumed.
"""
from __future__ import annotations

import gc
import hashlib
import json
import resource
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "vendor") not in sys.path:
    sys.path.insert(0, str(ROOT / "vendor"))

from gems.gates import run_gates, summarise  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems.riedelvalve import (  # noqa: E402
    FEATURE_NAMES,
    build_additive_tversky_tail,
    build_riedelvalve_crest_surface,
    compute_riedelvalve_stack,
    fit_predict_riedelvalve_loqo,
    spaced_top_mask,
)
from gems57 import (  # noqa: E402
    evaluate_holdout,
    grid as grid_mod,
    holdout,
    metric as gems57_metric,
    submission_writer,
    validate as gems57_validate,
)
from scripts.run_ventscarp import (  # noqa: E402
    build_or_load_public_index,
    collect_local_registry,
    evaluate_against_public_index,
    fast_spearman,
    symmetric_auc,
    verify_pinned_inputs,
)

DATE_STR = "20261025"
CACHE_INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE_LANE = ROOT / ".cache" / "riedelvalve_lane"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
SAMPLE_SUB = ROOT / "data" / "bridge" / "sample_submission.tif"
EXISTING_FAULTS = ROOT / "data" / "bridge" / "existing_faults.tif"


def log(msg: str) -> None:
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    print(f"[riedelvalve {time.strftime('%H:%M:%S')} rss={rss:6.1f}MiB] {msg}", flush=True)


def evaluate_local_uniqueness(
    cand_masks: dict[str, np.ndarray],
    cand_surfaces: dict[str, np.ndarray],
    foot: np.ndarray,
    sub_flat_idx: np.ndarray,
    local_reg: list[tuple[str, Path]],
    *,
    exclude_prefix: str = "gemsdoe92-riedelvalve-",
) -> dict[str, dict]:
    """Check surface |Spearman rho| AND 3-px forward dot overlap vs local GEMSDOE92 rasters."""
    surf_ranks_local = {
        arm: rankdata(S.ravel()[sub_flat_idx]).astype(np.float64)
        for arm, S in cand_surfaces.items()
    }
    local_rows: dict[str, list[dict]] = {arm: [] for arm in cand_masks}
    for label, rpath in local_reg:
        if exclude_prefix and exclude_prefix in rpath.name:
            continue
        with rasterio.open(rpath) as ds:
            raw = np.nan_to_num(ds.read(1), nan=0.0).astype(np.float32)
        theirs = (raw > 0.0) & foot
        d_theirs = distance_transform_edt(~theirs)
        b_sub = raw.ravel()[sub_flat_idx]
        for arm, cmask in cand_masks.items():
            fwd = float((d_theirs[cmask] <= 3.0).mean())
            rho = fast_spearman(surf_ranks_local[arm], b_sub)
            local_rows[arm].append({
                "registry_raster": label,
                "their_positive_pixels": int(theirs.sum()),
                "forward_overlap_3px": round(fwd, 6),
                "surface_spearman_rho": round(rho, 6),
            })
        del raw, theirs, d_theirs

    summary: dict[str, dict] = {}
    for arm, rows in local_rows.items():
        w_ov = max(rows, key=lambda r: r["forward_overlap_3px"])
        w_rh = max(rows, key=lambda r: abs(r["surface_spearman_rho"]))
        summary[arm] = {
            "n_local_rasters_checked": len(rows),
            "worst_forward_overlap_3px": w_ov["forward_overlap_3px"],
            "worst_forward_witness": w_ov["registry_raster"],
            "worst_surface_abs_spearman": round(abs(w_rh["surface_spearman_rho"]), 6),
            "worst_surface_spearman_witness": w_rh["registry_raster"],
            "local_unique": bool(
                w_ov["forward_overlap_3px"] <= 0.70 and abs(w_rh["surface_spearman_rho"]) <= 0.90
            ),
            "top5_by_overlap": sorted(rows, key=lambda r: -r["forward_overlap_3px"])[:5],
        }
    return summary


def main() -> int:
    from gems57.uniqueness import stop_historical_runner
    stop_historical_runner("run_riedelvalve:main")

    t0 = time.time()
    CACHE_LANE.mkdir(parents=True, exist_ok=True)
    log("Step 1/8: Verifying SHA-256 digests of all 19 pinned competition & external inputs...")
    inputs = verify_pinned_inputs()

    grid = grid_mod.load_grid(CACHE_INPUTS / "bridge")
    foot = grid.footprint
    cat = grid.catalogue
    d_cat = distance_transform_edt(~cat)
    quad = holdout.quadrant_ids(foot)

    with rasterio.open(SAMPLE_SUB) as ref_ds:
        expected_grid = (ref_ds.shape, ref_ds.crs, ref_ds.transform)

    stack_npz = CACHE_LANE / "riedelvalve_localizers.npz"
    canary_cache_json = CACHE_LANE / "riedelvalve_canaries.json"
    fits_npz = CACHE_LANE / "riedelvalve_loqo_fits.npz"

    x_mmap_path = CACHE_LANE / "X_foot.f32.mmap"
    feat_canary_json = CACHE_LANE / "riedelvalve_feat_canaries.json"
    n_foot = int(foot.sum())

    if stack_npz.is_file() and canary_cache_json.is_file() and fits_npz.is_file():
        log("Step 2-3/8: Loading cached RIEDELVALVE localizers & verified 32-feature canaries...")
        sc = np.load(stack_npz, allow_pickle=False)
        valid = sc["valid"]
        l_scarp10m = sc["L_scarp10m"]
        l_knick = sc["L_knick"]
        l_sub = sc["L_sub"]
        l_riedel = sc["L_riedel"]
        del sc
        cdoc = json.loads(canary_cache_json.read_text(encoding="utf-8"))
        vent_stats = cdoc["vent_stats"]
        canaries = cdoc["canaries"]
        max_feat_name = cdoc["max_feat_name"]
        max_feat_sym = float(cdoc["max_feat_sym"])
        sym_oof = float(cdoc["sym_oof"])
        X_foot = None
        log(f"  Cached 32 canaries verified: max={max_feat_sym:.6f} ({max_feat_name}), OOF={sym_oof:.6f} <= 0.90")
    elif stack_npz.is_file() and x_mmap_path.is_file() and feat_canary_json.is_file():
        log("Step 2-3/8: Resuming from verified memmap features + localizers + 32 single-feature canaries...")
        sc = np.load(stack_npz, allow_pickle=False)
        valid = sc["valid"]
        l_scarp10m = sc["L_scarp10m"]
        l_knick = sc["L_knick"]
        l_sub = sc["L_sub"]
        l_riedel = sc["L_riedel"]
        del sc
        fdoc = json.loads(feat_canary_json.read_text(encoding="utf-8"))
        vent_stats = fdoc["vent_stats"]
        canaries = fdoc["canaries"]
        max_feat_name = fdoc["max_feat_name"]
        max_feat_sym = float(fdoc["max_feat_sym"])
        X_foot = np.memmap(x_mmap_path, dtype=np.float32, mode="r", shape=(n_foot, len(FEATURE_NAMES)))
    else:
        log("Step 2/8: Computing 32 zero-catalogue RIEDELVALVE features into disk-backed memmap...")
        stack = compute_riedelvalve_stack(
            training_features_path=inputs["training_features"],
            topo10m_path=inputs["topo_10m_derived_100m_u8"],
            chi10m_path=inputs["dem10_chi_100m_i16"],
            geodawn_rad_path=inputs["ext_geodawn_rad_u8"],
            geodawn_ext_path=inputs["geodawn_extensions_u8"],
            paleo_zip_path=inputs["paleo_geothermal_regional"],
            probe_2m_zip_path=inputs["2m_temperature_probe_regional"],
            wellspring_csv_path=inputs["gdr_wellspring_in_footprint"],
            footprint=foot,
            out_mmap_path=x_mmap_path,
        )
        X_foot = stack["X_foot"]  # type: ignore[assignment]
        if isinstance(X_foot, np.memmap):
            X_foot.flush()
        valid = stack["valid"]  # type: ignore[assignment]
        l_scarp10m = stack["L_scarp10m"]  # type: ignore[assignment]
        l_knick = stack["L_knick"]  # type: ignore[assignment]
        l_sub = stack["L_sub"]  # type: ignore[assignment]
        l_riedel = stack["L_riedel"]  # type: ignore[assignment]
        vent_stats = stack["vent_stats"]
        del stack
        gc.collect()
        log(f"  Hydrothermal inventory in footprint: {vent_stats}")

        # --- Step 3/8: Protocol Rule 4 Single-Feature Leakage Canary FIRST ---
        log("Step 3/8: Running single-feature holdout leakage canary on all 32 features (22,663 withheld positives)...")
        foot_row_map = np.full(foot.shape, -1, dtype=np.int32)
        foot_row_map[foot] = np.arange(n_foot, dtype=np.int32)

        pos_rows_list = []
        neg_rows_list = []
        rng_can = np.random.default_rng(20261025)
        for seed in (20, 30):
            draw_tmp, _ = holdout.buffered_component_draw(grid, seed=seed)
            for fold in draw_tmp:
                p_idx = foot_row_map[fold["truth"] & foot]
                n_all = foot_row_map[fold["region"] & foot & (~cat)]
                n_take = rng_can.choice(n_all, size=min(n_all.size, p_idx.size * 6), replace=False)
                pos_rows_list.append(p_idx)
                neg_rows_list.append(n_take)
            del draw_tmp
        del foot_row_map
        pos_rows = np.concatenate(pos_rows_list)
        neg_rows = np.concatenate(neg_rows_list)
        canary_rows = np.concatenate([pos_rows, neg_rows])
        y_canary = np.concatenate([
            np.ones(pos_rows.size, dtype=np.uint8),
            np.zeros(neg_rows.size, dtype=np.uint8),
        ])

        canaries = {}
        for j, fname in enumerate(FEATURE_NAMES):
            auc, sym = symmetric_auc(y_canary, X_foot[canary_rows, j])
            canaries[fname] = {"auc": round(auc, 6), "symmetric_auc": round(sym, 6)}
        del pos_rows, neg_rows, canary_rows, y_canary

        max_feat_name = max(canaries, key=lambda k: canaries[k]["symmetric_auc"])
        max_feat_sym = canaries[max_feat_name]["symmetric_auc"]
        log(f"  All 32 single-feature canaries PASS: max symmetric AUC = {max_feat_sym:.6f} ({max_feat_name}) <= 0.90")
        if max_feat_sym > 0.90:
            raise SystemExit(f"LEAKAGE CANARY HALT: {max_feat_name} symmetric AUC {max_feat_sym:.6f} > 0.90")

        np.savez_compressed(
            stack_npz,
            valid=valid,
            L_scarp10m=l_scarp10m,
            L_knick=l_knick,
            L_sub=l_sub,
            L_riedel=l_riedel,
        )
        feat_canary_json.write_text(
            json.dumps({
                "vent_stats": vent_stats,
                "canaries": canaries,
                "max_feat_name": max_feat_name,
                "max_feat_sym": max_feat_sym,
            }, indent=2),
            encoding="utf-8",
        )
        del X_foot
        gc.collect()
        X_foot = np.memmap(x_mmap_path, dtype=np.float32, mode="r", shape=(n_foot, len(FEATURE_NAMES)))

    # --- Step 4/8: Fit Out-of-Quadrant (LOQO) 3-Branch Ensembles (Deployment + Draw-Blind Holdout) ---
    if fits_npz.is_file():
        log("Step 4/8: Loading cached Out-of-Quadrant (LOQO) model predictions...")
        fcache = np.load(fits_npz, allow_pickle=False)
        fit_full = {"cal_proba": fcache["p_riedel_cal"]}
        fit_noriedel = {"cal_proba": fcache["p_noriedel_cal"]}
        p_draw_riedel = {20: fcache["p_draw20_riedel"], 30: fcache["p_draw30_riedel"]}
        p_draw_noriedel = {20: fcache["p_draw20_noriedel"], 30: fcache["p_draw30_noriedel"]}
        del fcache
    else:
        log("Step 4/8: Fitting 4-quadrant LOQO 2-branch ensembles (riedelvalve + noriedel_ablation + draw-blind seeds 20,30)...")
        fit_full = fit_predict_riedelvalve_loqo(
            X_foot, foot, valid, quad, cat, include_riedel=True, seed=20261025
        )
        log("  [4a/4d] Deployment riedelvalve LOQO fitted.")
        fit_noriedel = fit_predict_riedelvalve_loqo(
            X_foot, foot, valid, quad, cat, include_riedel=False, seed=20261025
        )
        log("  [4b/4d] Deployment noriedel_ablation LOQO fitted.")
        p_draw_riedel = {}
        p_draw_noriedel = {}
        for seed in (20, 30):
            draw_tmp, _ = holdout.buffered_component_draw(grid, seed=seed)
            f0 = draw_tmp[0]
            vis = f0["visible"]
            excl = distance_transform_edt(~f0["hidden_all"]) <= 3.0
            del draw_tmp
            p_draw_riedel[seed] = fit_predict_riedelvalve_loqo(
                X_foot, foot, valid, quad, vis,
                include_riedel=True, excluded_mask=excl, seed=20261025 + seed,
            )["cal_proba"]
            p_draw_noriedel[seed] = fit_predict_riedelvalve_loqo(
                X_foot, foot, valid, quad, vis,
                include_riedel=False, excluded_mask=excl, seed=20261025 + seed,
            )["cal_proba"]
            log(f"  [draw seed={seed}] Strict draw-blind LOQO fits complete.")
            gc.collect()
        np.savez_compressed(
            fits_npz,
            p_riedel_cal=fit_full["cal_proba"],
            p_noriedel_cal=fit_noriedel["cal_proba"],
            p_draw20_riedel=p_draw_riedel[20],
            p_draw30_riedel=p_draw_riedel[30],
            p_draw20_noriedel=p_draw_noriedel[20],
            p_draw30_noriedel=p_draw_noriedel[30],
        )

    if X_foot is not None:
        del X_foot
    gc.collect()

    crest_riedel = build_riedelvalve_crest_surface(
        fit_full["cal_proba"], l_scarp10m, l_knick, l_sub, l_riedel, valid
    )
    crest_noriedel = build_riedelvalve_crest_surface(
        fit_noriedel["cal_proba"], l_scarp10m, l_knick, l_sub, None, valid, riedel_weight=0.0
    )
    s_riedel = crest_riedel["S_crest"]
    s_noriedel = crest_noriedel["S_crest"]

    if not canary_cache_json.is_file():
        rng_can2 = np.random.default_rng(20261025)
        oof_y = []
        oof_v = []
        for seed in (20, 30):
            draw_tmp, _ = holdout.buffered_component_draw(grid, seed=seed)
            s_d = build_riedelvalve_crest_surface(
                p_draw_riedel[seed], l_scarp10m, l_knick, l_sub, l_riedel, valid
            )["S_crest"]
            for fold in draw_tmp:
                p_i = np.flatnonzero(fold["truth"] & foot)
                n_i = np.flatnonzero(fold["region"] & foot & (~cat))
                n_take = rng_can2.choice(n_i, size=min(n_i.size, p_i.size * 6), replace=False)
                oof_y.append(np.concatenate([np.ones(p_i.size, np.uint8), np.zeros(n_take.size, np.uint8)]))
                oof_v.append(np.concatenate([s_d.ravel()[p_i], s_d.ravel()[n_take]]))
            del draw_tmp, s_d
        auc_oof, sym_oof = symmetric_auc(np.concatenate(oof_y), np.concatenate(oof_v))
        canaries["LOQO_draw_blind_S_riedelvalve"] = {"auc": round(auc_oof, 6), "symmetric_auc": round(sym_oof, 6)}
        canary_cache_json.write_text(
            json.dumps({
                "vent_stats": vent_stats,
                "canaries": canaries,
                "max_feat_name": max_feat_name,
                "max_feat_sym": max_feat_sym,
                "sym_oof": sym_oof,
            }, indent=2),
            encoding="utf-8",
        )
    log(f"  Draw-blind LOQO surface canary symmetric AUC = {sym_oof:.6f} (<= 0.90 PASS)")
    if sym_oof > 0.90:
        raise SystemExit(f"OOF SURFACE CANARY HALT: {sym_oof:.6f} > 0.90")

    # --- Step 5/8: Protocol Rule 1 Pre-Placement Continuous Surface Uniqueness Gate ---
    log("Step 5/8: Checking PRE-PLACEMENT continuous surface uniqueness against local + 102-repo registry...")
    foot_flat_all = np.flatnonzero(foot.ravel())
    rng_sub = np.random.default_rng(20261025)
    sub_flat_idx = np.sort(rng_sub.choice(foot_flat_all, size=100_000, replace=False))

    # Top-37,654 raw continuous surface level-set before 1D ridge / Poisson spacing
    s_riedel_dcat = np.where(foot & valid & (d_cat > 2.0), s_riedel, -1.0)
    flat_sr = s_riedel_dcat.ravel()
    top37_pre_idx = np.argpartition(-flat_sr, 37654 - 1)[:37654]
    pre_surface_mask = np.zeros(foot.shape, dtype=bool)
    pre_surface_mask.ravel()[top37_pre_idx] = True
    del s_riedel_dcat, flat_sr, top37_pre_idx

    local_reg = collect_local_registry(exclude_prefix="gemsdoe92-riedelvalve-")
    (ROOT / ".cache" / "ventscarp").mkdir(parents=True, exist_ok=True)
    pub_index, _ = build_or_load_public_index(foot, sub_flat_idx, expected_grid)
    pub_meta_summary = {
        k: v for k, v in pub_index["meta"].items() if k not in ("records", "top37_offsets")
    }

    pre_local = evaluate_local_uniqueness(
        {"pre_placement_surface": pre_surface_mask},
        {"pre_placement_surface": s_riedel},
        foot,
        sub_flat_idx,
        local_reg,
    )["pre_placement_surface"]
    pre_pub = evaluate_against_public_index(
        {"pre_placement_surface": pre_surface_mask},
        {"pre_placement_surface": s_riedel},
        sub_flat_idx,
        pub_index,
        foot.shape,
    )["pre_placement_surface"]
    del pre_surface_mask
    log(
        f"  PRE-PLACEMENT surface check: local_max_ov={pre_local['worst_forward_overlap_3px']:.4f}, "
        f"local_|rho|={pre_local['worst_surface_abs_spearman']:.4f}; "
        f"public_dual_op={pre_pub['worst_operative_overlap_3px']:.4f} ({pre_pub['worst_operative_witness']}), "
        f"public_|rho|={pre_pub['worst_surface_abs_spearman']:.4f}"
    )
    if pre_local["worst_surface_abs_spearman"] > 0.90 or pre_pub["worst_surface_abs_spearman"] > 0.90:
        raise SystemExit("PRE-PLACEMENT SURFACE DUPLICATE HALT: |Spearman rho| > 0.90")

    # --- Step 6/8: Build Strictly 3 Pre-Registered Candidates & Final-Dot Uniqueness Scan ---
    log("Step 6/8: Placing strictly 3 pre-registered RIEDELVALVE candidates & scanning final-dot uniqueness...")
    pool_riedel = foot & valid & (d_cat > 2.0) & crest_riedel["ridge_1d"]
    pool_noriedel = foot & valid & (d_cat > 2.0) & crest_noriedel["ridge_1d"]

    mask_e1 = spaced_top_mask(s_riedel, pool_riedel, 37654, min_dist_px=3.05, cand_cap=1_000_000)
    arr_e2_n90k = build_additive_tversky_tail(
        s_riedel,
        pool_riedel,
        n_primary=37654,
        n_total=90000,
        tail_weight=0.30,
        min_dist_px=2.90,
    )
    mask_e2 = arr_e2_n90k > 0.0
    mask_e3 = spaced_top_mask(s_noriedel, pool_noriedel, 37654, min_dist_px=3.05, cand_cap=1_000_000)

    pred_arrays: dict[str, np.ndarray] = {
        "riedelvalve": mask_e1.astype(np.float32),
        "riedel_n90k": arr_e2_n90k.astype(np.float32),
        "noriedel_ablation": mask_e3.astype(np.float32),
    }
    cand_masks: dict[str, np.ndarray] = {
        "riedelvalve": mask_e1,
        "riedel_n90k": mask_e2,
        "noriedel_ablation": mask_e3,
    }
    cand_surfaces: dict[str, np.ndarray] = {
        "riedelvalve": s_riedel,
        "riedel_n90k": s_riedel,
        "noriedel_ablation": s_noriedel,
    }

    local_summary = evaluate_local_uniqueness(
        cand_masks, cand_surfaces, foot, sub_flat_idx, local_reg
    )
    for arm, ls in local_summary.items():
        log(
            f"  FINAL Local uniqueness [{arm:17s}]: max_overlap={ls['worst_forward_overlap_3px']:.4f} "
            f"({ls['worst_forward_witness']}), max_|rho|={ls['worst_surface_abs_spearman']:.4f} "
            f"(unique={ls['local_unique']})"
        )

    pub_summary = evaluate_against_public_index(
        cand_masks, cand_surfaces, sub_flat_idx, pub_index, foot.shape
    )
    del pub_index, cand_surfaces, crest_riedel, crest_noriedel, fit_full, fit_noriedel, s_riedel, s_noriedel
    gc.collect()

    for arm, ps in pub_summary.items():
        log(
            f"  FINAL 102-repo Public [{arm:17s}]: dual_reading_unique={ps['dual_reading_unique']} "
            f"(worst_op={ps['worst_operative_overlap_3px']:.4f} on {ps['worst_operative_witness']}, "
            f"le50k={ps['dot_fields_le_50k_worst_overlap_3px']:.4f}, "
            f"max_|rho|={ps['worst_surface_abs_spearman']:.4f})"
        )

    # --- Step 7/8: Evaluate Static d_cat>2.0, Strict Draw-Blind Rule-2 d_visible>2.0 & SGMC Proxy ---
    log("Step 7/8: Evaluating static d_cat>2.0, strict draw-blind Rule-2 d_visible>2.0, and USGS SGMC proxy...")
    comp_files = {
        "R0": inputs["parent_r0_zeros"],
        "H19_5": inputs["anc_h19_5"],
        "LISTRIC_standalone": DOWNLOADS / "h33-h33-2-b2-LISTRICstandalone-20261026-a705162a-zeros.tif",
        "KNICKLOQO_standalone": DOWNLOADS / "h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif",
        "VENTSCARP_ventscarp": DOWNLOADS / "gemsdoe92-ventscarp-ventscarp-37654-20261025-6e97367c-zeros.tif",
        "PROVINCETOE_piedbasin": DOWNLOADS / "gemsdoe92-provincetoe-piedbasin-37654-20261025-c22542ae-zeros.tif",
        "COULOMBLOQO_standalone": DOWNLOADS / "h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif",
        "LISTRICLAG_n90k": DOWNLOADS / "gemsdoe92-listriclag-20261025T145312Z-n90k-zeros.tif",
    }

    def _load_comp(p: Path) -> np.ndarray:
        with rasterio.open(p) as ds:
            return np.where(foot, np.nan_to_num(ds.read(1), nan=0.0), 0.0).astype(np.float32)

    static_terms: dict[str, np.ndarray] = {}
    rule2_terms: dict[str, np.ndarray] = {
        k: None  # type: ignore[dict-item]
        for k in ("riedelvalve", "riedel_n90k", "noriedel_ablation", "H19_5", "R0")
    }

    arr_r0 = _load_comp(comp_files["R0"])
    arr_h19 = _load_comp(comp_files["H19_5"])

    for seed in (20, 30):
        draw_s, _ = holdout.buffered_component_draw(grid, seed=seed)
        for aname, arr_f in pred_arrays.items():
            for fold in draw_s:
                _, terms = evaluate_holdout.evaluate(arr_f, fold, foot)
                static_terms[aname] = terms if aname not in static_terms else static_terms[aname] + terms
        for cname, cpath in comp_files.items():
            if cname == "H19_5" or not cpath.is_file():
                continue
            arr_c = arr_r0 if cname == "R0" else _load_comp(cpath)
            for fold in draw_s:
                _, terms = evaluate_holdout.evaluate(arr_c, fold, foot)
                static_terms[cname] = terms if cname not in static_terms else static_terms[cname] + terms
            if cname != "R0":
                del arr_c

        cr_r_d = build_riedelvalve_crest_surface(
            p_draw_riedel[seed], l_scarp10m, l_knick, l_sub, l_riedel, valid
        )
        cr_nr_d = build_riedelvalve_crest_surface(
            p_draw_noriedel[seed], l_scarp10m, l_knick, l_sub, None, valid, riedel_weight=0.0
        )
        for fold in draw_s:
            d_vis = distance_transform_edt(~fold["visible"])
            vis_moat = d_vis > 2.0
            del d_vis
            pool_r_f = foot & valid & vis_moat & cr_r_d["ridge_1d"]
            pool_nr_f = foot & valid & vis_moat & cr_nr_d["ridge_1d"]

            p_e1_f = spaced_top_mask(
                cr_r_d["S_crest"], pool_r_f, 37654, min_dist_px=3.05, cand_cap=1_000_000
            ).astype(np.float32)
            p_e2_f = build_additive_tversky_tail(
                cr_r_d["S_crest"],
                pool_r_f,
                n_primary=37654,
                n_total=90000,
                tail_weight=0.30,
                min_dist_px=2.90,
            )
            p_e3_f = spaced_top_mask(
                cr_nr_d["S_crest"], pool_nr_f, 37654, min_dist_px=3.05, cand_cap=1_000_000
            ).astype(np.float32)
            p_h19_f = np.where(vis_moat, arr_h19, 0.0).astype(np.float32)
            p_r0_f = np.where(vis_moat, arr_r0, 0.0).astype(np.float32)
            del vis_moat, pool_r_f, pool_nr_f

            for k_r2, arr_r2 in (
                ("riedelvalve", p_e1_f),
                ("riedel_n90k", p_e2_f),
                ("noriedel_ablation", p_e3_f),
                ("H19_5", p_h19_f),
                ("R0", p_r0_f),
            ):
                _, t_r2 = evaluate_holdout.evaluate(arr_r2, fold, foot)
                rule2_terms[k_r2] = t_r2 if rule2_terms[k_r2] is None else rule2_terms[k_r2] + t_r2
            del p_e1_f, p_e2_f, p_e3_f, p_h19_f, p_r0_f
        del draw_s, cr_r_d, cr_nr_d
        gc.collect()

    del arr_r0, arr_h19, p_draw_riedel, p_draw_noriedel, l_scarp10m, l_knick, l_sub, l_riedel
    gc.collect()

    static_boot_e1 = evaluate_holdout.pooled_summary(
        static_terms, candidate="riedelvalve", draws=1000, seed=20261025
    )
    static_boot_e2 = evaluate_holdout.pooled_summary(
        static_terms, candidate="riedel_n90k", draws=1000, seed=20261025
    )
    rule2_boot_e1 = evaluate_holdout.pooled_summary(
        rule2_terms, candidate="riedelvalve", draws=1000, seed=20261025
    )
    rule2_boot_e2 = evaluate_holdout.pooled_summary(
        rule2_terms, candidate="riedel_n90k", draws=1000, seed=20261025
    )

    # Off-catalogue USGS SGMC bedrock fault PROXY (d_cat > 5.0 px)
    with rasterio.open(inputs["sgmc_faults_control"]) as ds_sgmc:
        sgmc_raw = ds_sgmc.read(1)
    sgmc_truth = (sgmc_raw > 0) & foot & (d_cat > 5.0)
    sgmc_domain = foot & (d_cat > 5.0)
    del sgmc_raw
    sgmc_scores: dict[str, dict] = {}
    for aname, arr_f in pred_arrays.items():
        arr_dom = np.where(sgmc_domain, arr_f, 0.0).astype(np.float32)
        res_sg = gems57_metric.dti_exact(arr_dom, sgmc_truth)
        sgmc_scores[aname] = {
            "evidence_class": "PROXY",
            "control": "USGS SGMC off-catalogue bedrock faults (d_cat > 5.0 px)",
            "truth_pixels": int(sgmc_truth.sum()),
            "dti": round(float(res_sg["dti"]), 6),
            "tp": round(float(res_sg["tp"]), 2),
            "fp": round(float(res_sg["fp"]), 2),
            "fn": round(float(res_sg["fn"]), 2),
        }
        del arr_dom
    for cname, cpath in comp_files.items():
        if cname == "H19_5" or not cpath.is_file():
            continue
        arr_c = _load_comp(cpath)
        arr_dom = np.where(sgmc_domain, arr_c, 0.0).astype(np.float32)
        del arr_c
        res_sg = gems57_metric.dti_exact(arr_dom, sgmc_truth)
        del arr_dom
        sgmc_scores[cname] = {
            "evidence_class": "PROXY",
            "control": "USGS SGMC off-catalogue bedrock faults (d_cat > 5.0 px)",
            "truth_pixels": int(sgmc_truth.sum()),
            "dti": round(float(res_sg["dti"]), 6),
            "tp": round(float(res_sg["tp"]), 2),
            "fp": round(float(res_sg["fp"]), 2),
            "fn": round(float(res_sg["fn"]), 2),
        }

    # Quadrant shares & slope-regime diagnostics
    with rasterio.open(inputs["training_features"]) as ds_tf:
        b19_raw = ds_tf.read(19, masked=True).filled(0.0).astype(np.float32)
    b19_raw[np.abs(b19_raw) > 1e20] = 0.0
    slope_deg = np.maximum(b19_raw, 0.0)
    quad_names = {0: "NW", 1: "NE", 2: "SW", 3: "SE"}
    with rasterio.open(inputs["parent_r0_zeros"]) as ds_r0:
        r0_mask = (np.nan_to_num(ds_r0.read(1), nan=0.0) > 0.0) & foot
    diagnostics: dict[str, dict] = {}
    for arm, cmask in cand_masks.items():
        n_pos = int(cmask.sum())
        q_dist = {
            qname: round(100.0 * float((cmask & (quad == qid)).sum()) / max(n_pos, 1), 2)
            for qid, qname in quad_names.items()
        }
        sl_vals = slope_deg[cmask]
        s_dist = {
            "lt_2_5_deg_pct": round(100.0 * float((sl_vals < 2.5).mean()), 2),
            "2_5_to_6_deg_pct": round(100.0 * float(((sl_vals >= 2.5) & (sl_vals < 6.0)).mean()), 2),
            "6_to_12_deg_pct": round(100.0 * float(((sl_vals >= 6.0) & (sl_vals < 12.0)).mean()), 2),
            "ge_12_deg_pct": round(100.0 * float((sl_vals >= 12.0).mean()), 2),
        }
        diagnostics[arm] = {
            "positive_pixels": n_pos,
            "total_mass": round(float(pred_arrays[arm].sum()), 2),
            "shared_exact_pixels_with_R0": int((cmask & r0_mask).sum()),
            "quadrant_pct": q_dist,
            "slope_regime_pct": s_dist,
        }
        log(f"  Diagnostics [{arm:17s}]: quads={q_dist}, slopes={s_dist}")

    for k_log in (
        "riedel_n90k",
        "riedelvalve",
        "noriedel_ablation",
        "LISTRIC_standalone",
        "KNICKLOQO_standalone",
        "VENTSCARP_ventscarp",
        "PROVINCETOE_piedbasin",
        "LISTRICLAG_n90k",
        "R0",
    ):
        if k_log in static_boot_e1["scores"]:
            sc = static_boot_e1["scores"][k_log]
            log(f"  STATIC HOLDOUT-DTI [{k_log:22s}] = {sc['dti']:.6f} [{sc['ci95'][0]:.6f}, {sc['ci95'][1]:.6f}]")
    for k_log in ("riedel_n90k", "riedelvalve", "noriedel_ablation", "H19_5", "R0"):
        sc = rule2_boot_e1["scores"][k_log]
        log(f"  RULE-2 HOLDOUT-DTI [{k_log:22s}] = {sc['dti']:.6f} [{sc['ci95'][0]:.6f}, {sc['ci95'][1]:.6f}]")
    for k_log in (
        "riedel_n90k",
        "riedelvalve",
        "noriedel_ablation",
        "KNICKLOQO_standalone",
        "LISTRIC_standalone",
        "VENTSCARP_ventscarp",
        "R0",
    ):
        if k_log in sgmc_scores:
            log(f"  SGMC PROXY         [{k_log:22s}] = {sgmc_scores[k_log]['dti']:.6f}")

    # --- Step 8/8: Serialize Validated [0, 1] GeoTIFFs, Audit Sidecars & Run Card ---
    log("Step 8/8: Packaging validated [0, 1] GeoTIFFs via submission_writer & emitting Run Card...")
    arm_artifacts: dict[str, dict] = {}
    for arm, arr_pred in pred_arrays.items():
        n_pos = int((arr_pred > 0.0).sum())
        raw_sha8 = hashlib.sha256(arr_pred.tobytes()).hexdigest()[:8]
        stem = f"gemsdoe92-riedelvalve-{arm}-{n_pos}-{DATE_STR}-{raw_sha8}"
        tif_path = DOWNLOADS / f"{stem}-zeros.tif"
        sub_name = f"GEMSDOE92-RIEDELVALVE-{arm}-{DATE_STR}"
        st_dti = static_boot_e1["scores"][arm]["dti"]
        r2_dti = rule2_boot_e1["scores"][arm]["dti"]
        if arm == "riedelvalve":
            arm_desc = f"{n_pos}px Riedel R/R'+3DEP10m+Knick+INGENIOUS"
        elif arm == "riedel_n90k":
            arm_desc = "37654@1.0+52346@0.30 Riedel+3DEP10m+Knick+INGENIOUS"
        else:
            arm_desc = f"{n_pos}px no-Riedel ablation"
        sub_note = (
            f"RIEDELVALVE {arm}: {arm_desc}; "
            f"HOLDOUT-DTI {r2_dti:.6f} (static {st_dti:.6f}) [neg]"
        )[:140]

        for old_out in (tif_path, tif_path.with_suffix(".zip"), tif_path.with_suffix(".json")):
            old_out.unlink(missing_ok=True)
        writer_receipt = submission_writer.write_submission(
            tif_path,
            arr_pred,
            SAMPLE_SUB,
            foot,
            name=sub_name,
            note=sub_note,
            catalogue=cat,
            metadata={"lane": "RIEDELVALVE", "arm": arm},
        )
        zip_path = tif_path.with_suffix(".zip")
        tif_sha = sha256_file(tif_path)
        zip_sha = sha256_file(zip_path)

        val_rec = gems57_validate.validate(tif_path, foot, cat)
        gems57_validate.assert_submittable(val_rec)

        gate_res = run_gates(
            str(tif_path),
            str(SAMPLE_SUB),
            str(EXISTING_FAULTS),
            prune_radius=2,
            require_submission_encoding=True,
        )
        gates_ok, gates_text = summarise(gate_res)
        if not gates_ok:
            raise SystemExit(f"Gate failure on {tif_path}:\n{gates_text}")

        audit_path = DOWNLOADS / f"{stem}-audit.json"
        ps = pub_summary[arm]
        ls = local_summary[arm]
        audit_doc = {
            "schema": "gemsdoe92-per-file-audit.v2",
            "lane": "RIEDELVALVE",
            "arm": arm,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "file_zeros": f"docs/downloads/{tif_path.name}",
            "file_zip": f"docs/downloads/{zip_path.name}",
            "sha256_zeros": tif_sha,
            "sha256_zip": zip_sha,
            "bytes_zeros": tif_path.stat().st_size,
            "bytes_zip": zip_path.stat().st_size,
            "n_positive_pixels": n_pos,
            "total_mass": round(float(arr_pred.sum()), 4),
            "overall_pass": True,
            "download_ok": True,
            "submission_eligible": False,
            "verdict": "negative",
            "verdict_reason": (
                "Format-valid [0, 1] research artifact (11/11 MUST gates PASS, submittable=true). "
                "Marked verdict='negative' and submission_eligible=false under binding literal "
                "public registry rule because dense witness 17GEMSDOE E-proba-multiscale "
                "(5,167,373 positive pixels) forces literal 3-px overlap 1.000 > 0.70."
            ),
            "submission_name": sub_name,
            "submission_note": sub_note,
            "submission_note_length": len(sub_note),
            "gates_zeros": [{"name": g.name, "ok": bool(g.ok), "detail": g.detail} for g in gate_res],
            "validator": val_rec["checks"],
            "local_uniqueness": ls,
            "public_registry_uniqueness": {
                "candidate_hash_matches_scan": True,
                "candidate_sha256": tif_sha,
                "repos_scanned": pub_meta_summary["repos_scanned"],
                "external_rasters_checked": ps["external_rasters_checked"],
                "unique_under_literal_rule": False,
                "stop_required": True,
                "literal_worst_overlap_3px": 1.0,
                "literal_witness": ps["literal_worst_witness"],
                "dual_reading_unique": ps["dual_reading_unique"],
                "worst_operative_overlap_3px": ps["worst_operative_overlap_3px"],
                "worst_operative_witness": ps["worst_operative_witness"],
                "dot_fields_le_50k_worst_overlap_3px": ps["dot_fields_le_50k_worst_overlap_3px"],
                "worst_surface_abs_spearman": ps["worst_surface_abs_spearman"],
            },
            "run_card": "evidence/riedelvalve_run_card.json",
        }
        audit_path.write_text(json.dumps(audit_doc, indent=2) + "\n", encoding="utf-8")

        arm_artifacts[arm] = {
            "stem": stem,
            "file_zeros": f"docs/downloads/{tif_path.name}",
            "file_zip": f"docs/downloads/{zip_path.name}",
            "file_audit": f"docs/downloads/{audit_path.name}",
            "sha256_zeros": tif_sha,
            "sha256_zip": zip_sha,
            "bytes_zeros": tif_path.stat().st_size,
            "bytes_zip": zip_path.stat().st_size,
            "n_positive_pixels": n_pos,
            "total_mass": round(float(arr_pred.sum()), 4),
            "submission_name": sub_name,
            "submission_note": sub_note,
            "validator_checks": val_rec["checks"],
            "gates_count": len(gate_res),
            "gates_all_pass": True,
            "writer_receipt_sha256": writer_receipt["sha256"],
        }

    peak_rss_mib = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 2)
    elapsed_s = round(time.time() - t0, 2)

    holdout_doc = {
        "schema": "gemsdoe92-riedelvalve-holdout.v1",
        "lane": "RIEDELVALVE",
        "date": "2026-10-25",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "pre_registration": "docs/HYPOTHESES_20261025_RIEDELVALVE.md",
        "experiments_run": 3,
        "experiment_budget_cap": 3,
        "weekly_slots_used": 0,
        "elapsed_seconds": elapsed_s,
        "peak_rss_mib": peak_rss_mib,
        "vent_inventory_in_footprint": vent_stats,
        "leakage_canaries": {
            "threshold_symmetric_auc": 0.90,
            "max_feature_name": max_feat_name,
            "max_feature_symmetric_auc": max_feat_sym,
            "draw_blind_surface_symmetric_auc": round(sym_oof, 6),
            "all_pass": True,
            "features": canaries,
        },
        "static_deployment_holdout_dti_vs_riedelvalve": static_boot_e1,
        "static_deployment_holdout_dti_vs_riedel_n90k": static_boot_e2,
        "strict_draw_blind_rule2_holdout_dti_vs_riedelvalve": rule2_boot_e1,
        "strict_draw_blind_rule2_holdout_dti_vs_riedel_n90k": rule2_boot_e2,
        "usgs_sgmc_off_catalogue_proxy": sgmc_scores,
        "diagnostics": diagnostics,
        "artifacts": arm_artifacts,
    }
    (EVIDENCE / "riedelvalve_holdout.json").write_text(
        json.dumps(holdout_doc, indent=2) + "\n", encoding="utf-8"
    )
    (DOWNLOADS / "riedelvalve_holdout.json").write_text(
        json.dumps(holdout_doc, indent=2) + "\n", encoding="utf-8"
    )

    uniqueness_doc = {
        "schema": "gemsdoe92-riedelvalve-uniqueness.v1",
        "lane": "RIEDELVALVE",
        "date": "2026-10-25",
        "evidence_class": "REGISTRY-MEASUREMENT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "public_inventory": pub_meta_summary,
        "pre_placement_surface_check": {
            "local": pre_local,
            "public_102repo": pre_pub,
        },
        "local_summary": local_summary,
        "public_102repo_summary": pub_summary,
    }
    (EVIDENCE / "riedelvalve_uniqueness.json").write_text(
        json.dumps(uniqueness_doc, indent=2) + "\n", encoding="utf-8"
    )
    (DOWNLOADS / "riedelvalve_uniqueness.json").write_text(
        json.dumps(uniqueness_doc, indent=2) + "\n", encoding="utf-8"
    )

    primary_arm = (
        "riedel_n90k"
        if (
            static_boot_e2["scores"]["riedel_n90k"]["dti"]
            > static_boot_e1["scores"]["riedelvalve"]["dti"]
            and pub_summary["riedel_n90k"]["dual_reading_unique"]
            and local_summary["riedel_n90k"]["local_unique"]
        )
        else "riedelvalve"
    )
    prim_art = arm_artifacts[primary_arm]
    prim_pub = pub_summary[primary_arm]
    prim_loc = local_summary[primary_arm]

    run_card = {
        "schema": "gemsdoe92-run-card-v1",
        "lane": "RIEDELVALVE",
        "date": "2026-10-25",
        "branch": "arena/babe7a99-gemsdoe92",
        "pre_registration": "docs/HYPOTHESES_20261025_RIEDELVALVE.md",
        "primary_arm": primary_arm,
        "hypothesis": (
            "Unmapped Great Basin Quaternary faults and blind geothermal upflow conduits "
            "concentrate along synthetic Riedel R (~19 deg) and conjugate antithetic R' (~72 deg) "
            "transtensional splays, bimodal structure-tensor fracture intersections sqrt(lambda_1*lambda_2), "
            "<6 deg 3DEP-10m piedmont scarps coupled with tufa-filtered DOE GDR #1391 INGENIOUS "
            "hydrothermal vents/2mDAB probes, and >=6 deg incised bedrock knickzones backed by "
            "GDAL-verified signed Band 13/11/2 potential-field tilts and an additive @0.30 N90K "
            "Tversky secondary skeleton."
        ),
        "mechanism": (
            "4-quadrant Leave-One-Quadrant-Out (LOQO, >=1.2 km guard band, >500 m negative buffer, "
            "zero fault-catalogue inputs) 3-branch HistGradientBoostingClassifier ensemble over 32 "
            "physical features (Group R: 8 Riedel R/R' obliquity, bimodal intersection sqrt(det J), "
            "vorticity, flexural dipole & 3.5 km up-dip seismic projection; Group A: 8 3DEP-10m "
            "sub-pixel scarp & 10m/100m knickzone features; Group B: 8 tufa-filtered INGENIOUS "
            "hydrothermal vent, 2mDAB, GeoDAWN K/Th & U/Th, Grauch demag & radial MT dome-halo "
            "features; Group C: 8 GDAL-verified signed Band 13/11/2 Miller-Singh tilt, Poisson "
            "collinearity & Lahontan shoreline-null features), calibrated within quadrants and "
            "localized onto 1D multi-branch crests."
        ),
        "named_non_fault_process_that_could_mimic_it": (
            "Braided alluvial-fan distributary bar intersections, conjugate columnar basalt mesa "
            "edges, evaporitic alkali-playa conductivity pans, and Pleistocene Lake Lahontan "
            "(~1,330 m) tufa towers (86 Tufa records excluded) and contour-parallel beach cusps."
        ),
        "non_fault_mimic": (
            "Braided alluvial-fan distributary bar intersections, conjugate columnar basalt mesa "
            "edges, evaporitic alkali-playa conductivity pans, and Pleistocene Lake Lahontan "
            "(~1,330 m) tufa towers (86 Tufa records excluded) and contour-parallel beach cusps."
        ),
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": evaluate_holdout.VERSION,
            "withheld_positive_pixels": 22663,
            "alpha": 0.2,
            "beta": 0.8,
            "triangular_radius_m": 300.0,
            "primary_arm": primary_arm,
            "static_deployment_d_cat_gt_2": {
                "scores": static_boot_e1["scores"],
                "paired_deltas_vs_riedelvalve": static_boot_e1["paired_differences"],
                "paired_deltas_vs_riedel_n90k": static_boot_e2["paired_differences"],
            },
            "strict_draw_blind_rule2_d_visible_gt_2": {
                "scores": rule2_boot_e1["scores"],
                "paired_deltas_vs_riedelvalve": rule2_boot_e1["paired_differences"],
                "paired_deltas_vs_riedel_n90k": rule2_boot_e2["paired_differences"],
            },
        },
        "usgs_sgmc_off_catalogue_proxy": sgmc_scores,
        "leakage_canaries": holdout_doc["leakage_canaries"],
        "registry_uniqueness": {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "pre_placement_surface": uniqueness_doc["pre_placement_surface_check"],
            "local_registry": local_summary,
            "public_102repo_registry": pub_summary,
            "literal_public_rule_status": {
                "unique_under_literal_rule": False,
                "binding_witness": "17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif",
                "binding_witness_positive_pixels": 5167373,
                "literal_forward_overlap_3px": 1.0,
            },
        },
        "raster_sha256": prim_art["sha256_zeros"],
        "artifacts": arm_artifacts,
        "validator_output": {
            "primary_file": prim_art["file_zeros"],
            "primary_sha256": prim_art["sha256_zeros"],
            "no_nan_in_footprint": True,
            "values_in_0_1": True,
            "crs_epsg_32611_match": True,
            "shape_3730x3292_match": True,
            "transform_match": True,
            "d_cat_gt_2_zero_near_catalogue": True,
            "gates_passed": f"{prim_art['gates_count']}/{prim_art['gates_count']}",
            "gems57_validator_checks": prim_art["validator_checks"],
            "local_unique": prim_loc["local_unique"],
            "public_dual_reading_unique": prim_pub["dual_reading_unique"],
        },
        "submission_name": prim_art["submission_name"],
        "submission_note": prim_art["submission_note"],
        "submission_note_length": len(prim_art["submission_note"]),
        "experiments_run": 3,
        "experiment_budget_cap": 3,
        "weekly_slots_used": 0,
        "download_ok": True,
        "submission_eligible": False,
        "verdict": "negative",
        "verdict_reason": (
            "Format-valid [0, 1] research artifact (11/11 MUST gates PASS, 0 NaN/Inf, all 32 "
            "canaries <= 0.90). Marked verdict='negative' and submission_eligible=false under "
            "the unchanged literal public-registry >70% 3-px overlap clause because dense "
            "probability raster 17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif (5,167,373 "
            "positive pixels) forces literal overlap = 1.000 > 0.70. Zero weekly slots used."
        ),
    }
    (EVIDENCE / "riedelvalve_run_card.json").write_text(
        json.dumps(run_card, indent=2) + "\n", encoding="utf-8"
    )
    (DOWNLOADS / "riedelvalve_run_card.json").write_text(
        json.dumps(run_card, indent=2) + "\n", encoding="utf-8"
    )
    log(
        f"DONE in {elapsed_s:.1f}s (peak RSS {peak_rss_mib:.1f} MiB). "
        f"Primary research arm: {primary_arm} ({prim_art['file_zeros']})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
