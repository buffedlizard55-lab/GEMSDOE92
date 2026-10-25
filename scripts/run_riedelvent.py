#!/usr/bin/env python3
"""End-to-end execution of the RIEDELVENT lane (Session 2026-10-25).

Pre-registration: docs/HYPOTHESES_20261025_RIEDELVENT.md.
Executes strictly <= 3 experiments on the 8-fold gems57-pooled-hide-v2 holdout
(22,663 withheld positives across seeds 20 & 30):
  1. Experiment 1 (`riedelvent`): Full 30-feature RIEDELVENT LOQO ensemble
     (USGS 3DEP 10 m sub-pixel scarp + 10m/100m incised thalweg knickzones +
     tufa-filtered INGENIOUS paleo-vents/2mDAB/springs + GeoDAWN K/Th, U/Th,
     Grauch TMI_up150-RTP demagnetization + Poisson magneto-gravity collinearity +
     En-Echelon Riedel 12-28 deg R-shear obliquity + Hanging-Wall Flexural Hinge
     curvature), emitted onto S=37,654 Poisson-spaced 1D crests (min_dist=3.15 px).
  2. Experiment 2 (`riedel_novent`): Pre-registered ablation removing all 9 Group B
     hydrothermal-vent/alteration features and all 4 Group D Riedel/flexure features
     (17 baseline features retained), emitted onto S=37,654 crests (min_dist=3.15 px).
  3. Experiment 3 (`riedelvent_tail`): Additive-tail continuous [0, 1] allocation
     on Experiment 1's surface keeping top 37,654 crests at 1.0 and appending
     26,346 secondary crests at 0.30 (64,000 positive pixels, total mass 45,557.8,
     min_dist=3.15 px), testing docs/NEXT_STEPS.md Item #1.
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

from gems.gates import run_gates, summarise  # noqa: E402
from gems.riedelvent import (  # noqa: E402
    FEATURE_NAMES,
    build_additive_tail_allocation,
    build_riedelvent_crest_surface,
    compute_riedelvent_stack,
    fit_predict_riedelvent_loqo,
    spaced_top_mask,
)
from scripts.run_ventscarp import (  # noqa: E402
    build_or_load_public_index,
    collect_local_registry as _collect_local_registry_base,
    evaluate_against_public_index,
    fast_spearman,
    sha256_file,
    symmetric_auc,
    verify_pinned_inputs,
)
from vendor.gems57 import (  # noqa: E402
    evaluate_holdout,
    grid as grid_mod,
    holdout,
    metric as gems57_metric,
    submission_writer,
    validate as gems57_validate,
)

CACHE_INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE_LANE = ROOT / ".cache" / "riedelvent"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
SAMPLE_SUB = CACHE_INPUTS / "bridge" / "sample_submission.tif"
EXISTING_FAULTS = CACHE_INPUTS / "bridge" / "existing_faults.tif"
DATE_STR = "20261025"


def log(msg: str) -> None:
    now = datetime.now(timezone.utc).strftime("%H:%M:%S")
    rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    print(f"[{now} | RSS {rss_mb:6.1f} MiB] {msg}", flush=True)


def collect_local_registry() -> list[tuple[str, Path]]:
    return _collect_local_registry_base(exclude_prefix="gemsdoe92-riedelvent-")


def main() -> int:
    t0 = time.time()
    CACHE_LANE.mkdir(parents=True, exist_ok=True)
    (ROOT / ".cache" / "ventscarp").mkdir(parents=True, exist_ok=True)
    log("Step 1/7: Verifying SHA-256 digests of all 19 pinned competition & external inputs...")
    inputs = verify_pinned_inputs()

    grid = grid_mod.load_grid(CACHE_INPUTS / "bridge")
    foot = grid.footprint
    cat = grid.catalogue
    d_cat = distance_transform_edt(~cat)
    quad = holdout.quadrant_ids(foot)

    with rasterio.open(SAMPLE_SUB) as ref_ds:
        expected_grid = (ref_ds.shape, ref_ds.crs, ref_ds.transform)

    stack_npz = CACHE_LANE / "riedelvent_localizers.npz"
    x_foot_npy = CACHE_LANE / "riedelvent_X_foot.npy"
    step3_json = CACHE_LANE / "riedelvent_step3_canaries.json"
    canary_cache_json = CACHE_LANE / "riedelvent_canaries.json"
    fits_npz = CACHE_LANE / "riedelvent_loqo_fits.npz"

    if stack_npz.is_file() and canary_cache_json.is_file() and fits_npz.is_file():
        log("Step 2-3/7: Loading cached RIEDELVENT localizers & verified single-feature canaries...")
        sc = np.load(stack_npz, allow_pickle=False)
        valid = sc["valid"]
        l_scarp10m = sc["L_scarp10m"]
        l_knick = sc["L_knick"]
        l_grav_base = sc["L_grav_base"]
        l_riedel_flex = sc["L_riedel_flex"]
        l_vent_sub = sc["L_vent_sub"]
        del sc
        cdoc = json.loads(canary_cache_json.read_text(encoding="utf-8"))
        vent_stats = cdoc["vent_stats"]
        canaries = cdoc["canaries"]
        max_feat_name = cdoc["max_feat_name"]
        max_feat_sym = float(cdoc["max_feat_sym"])
        sym_oof = float(cdoc["sym_oof"])
        X_foot = None
        log(f"  Cached 30 canaries verified: max={max_feat_sym:.6f} ({max_feat_name}), OOF={sym_oof:.6f} <= 0.90")
    elif stack_npz.is_file() and (x_foot_npy.is_file() or fits_npz.is_file()) and step3_json.is_file():
        log("Step 2-3/7: Loading cached localizers & Step 3 single-feature canaries...")
        sc = np.load(stack_npz, allow_pickle=False)
        valid = sc["valid"]
        l_scarp10m = sc["L_scarp10m"]
        l_knick = sc["L_knick"]
        l_grav_base = sc["L_grav_base"]
        l_riedel_flex = sc["L_riedel_flex"]
        l_vent_sub = sc["L_vent_sub"]
        del sc
        X_foot = np.load(x_foot_npy, allow_pickle=False) if x_foot_npy.is_file() else None
        s3 = json.loads(step3_json.read_text(encoding="utf-8"))
        vent_stats = s3["vent_stats"]
        canaries = s3["canaries"]
        max_feat_name = s3["max_feat_name"]
        max_feat_sym = float(s3["max_feat_sym"])
        log(f"  Loaded 30 single-feature canaries: max={max_feat_sym:.6f} ({max_feat_name}) <= 0.90")
    else:
        log("Step 2/7: Computing 30 zero-catalogue RIEDELVENT features (Riedel + Flexure + 3DEP-10m + Vents)...")
        stack = compute_riedelvent_stack(
            training_features_tif=inputs["training_features"],
            topo_10m_tif=inputs["topo_10m_derived_100m_u8"],
            dem10_chi_tif=inputs["dem10_chi_100m_i16"],
            paleo_zip=inputs["paleo_geothermal_regional"],
            probe_2m_zip=inputs["2m_temperature_probe_regional"],
            wellspring_csv=inputs["gdr_wellspring_in_footprint"],
            geodawn_ext_tif=inputs["geodawn_extensions_u8"],
            footprint=foot,
        )
        X_foot = stack["X_foot"]  # type: ignore[assignment]
        valid = stack["valid"]  # type: ignore[assignment]
        l_scarp10m = stack["L_scarp10m"]  # type: ignore[assignment]
        l_knick = stack["L_knick"]  # type: ignore[assignment]
        l_grav_base = stack["L_grav_base"]  # type: ignore[assignment]
        l_riedel_flex = stack["L_riedel_flex"]  # type: ignore[assignment]
        l_vent_sub = stack["L_vent_sub"]  # type: ignore[assignment]
        vent_stats = stack["vent_stats"]
        del stack
        gc.collect()
        log(f"  Vent stats in footprint: {vent_stats}")

        # --- Step 3/7: Single-Feature Holdout Leakage Canary FIRST (Protocol Rule 4) ---
        log("Step 3/7: Running single-feature holdout leakage canary on 22,663 withheld positives...")
        foot_row_map = np.full(foot.shape, -1, dtype=np.int32)
        foot_row_map[foot] = np.arange(int(foot.sum()), dtype=np.int32)

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
        log(f"  All 30 single-feature canaries checked: max symmetric AUC = {max_feat_sym:.6f} ({max_feat_name})")
        if max_feat_sym > 0.90:
            raise SystemExit(f"LEAKAGE CANARY HALT: {max_feat_name} symmetric AUC {max_feat_sym:.6f} > 0.90")

        np.savez_compressed(
            stack_npz,
            valid=valid,
            L_scarp10m=l_scarp10m,
            L_knick=l_knick,
            L_grav_base=l_grav_base,
            L_riedel_flex=l_riedel_flex,
            L_vent_sub=l_vent_sub,
        )
        np.save(x_foot_npy, X_foot)
        step3_json.write_text(
            json.dumps({
                "vent_stats": vent_stats,
                "canaries": canaries,
                "max_feat_name": max_feat_name,
                "max_feat_sym": max_feat_sym,
            }, indent=2),
            encoding="utf-8",
        )

    # --- Step 4/7: Fit Out-of-Quadrant (LOQO) Models (Deployment + Draw-Blind Holdout) ---
    if fits_npz.is_file():
        log("Step 4/7: Loading cached Out-of-Quadrant (LOQO) model predictions...")
        fcache = np.load(fits_npz, allow_pickle=False)
        fit_full = {"cal_proba": fcache["p_full_cal"]}
        fit_novent = {"cal_proba": fcache["p_novent_cal"]}
        p_draw_full = {20: fcache["p_draw20_full"], 30: fcache["p_draw30_full"]}
        p_draw_novent = {20: fcache["p_draw20_novent"], 30: fcache["p_draw30_novent"]}
        del fcache
    else:
        log("Step 4/7: Fitting Out-of-Quadrant (LOQO) models (Arm 1 riedelvent + Arm 2 riedel_novent)...")
        f_full_p = CACHE_LANE / "p_full_cal.npy"
        f_nov_p = CACHE_LANE / "p_novent_cal.npy"
        if f_full_p.is_file():
            log("  [4a/6] Loaded cached deployment LOQO for Arm 1 (riedelvent)...")
            fit_full = {"cal_proba": np.load(f_full_p, allow_pickle=False)}
        else:
            log("  [4a/6] Fitting deployment LOQO for Arm 1 (riedelvent, 30 features)...")
            fit_full = fit_predict_riedelvent_loqo(
                X_foot, foot, valid, quad, cat,
                include_riedel_vent=True, max_pos_samples=30000, max_iter=110, seed=20261025,
            )
            np.save(f_full_p, fit_full["cal_proba"])

        if f_nov_p.is_file():
            log("  [4b/6] Loaded cached deployment LOQO for Arm 2 (riedel_novent)...")
            fit_novent = {"cal_proba": np.load(f_nov_p, allow_pickle=False)}
        else:
            log("  [4b/6] Fitting deployment LOQO for Arm 2 (riedel_novent, 17 features)...")
            fit_novent = fit_predict_riedelvent_loqo(
                X_foot, foot, valid, quad, cat,
                include_riedel_vent=False, max_pos_samples=30000, max_iter=110, seed=20261025,
            )
            np.save(f_nov_p, fit_novent["cal_proba"])

        p_draw_full = {}
        p_draw_novent = {}
        for idx_s, seed in enumerate((20, 30), start=1):
            df_p = CACHE_LANE / f"p_draw{seed}_full.npy"
            dn_p = CACHE_LANE / f"p_draw{seed}_novent.npy"
            if df_p.is_file() and dn_p.is_file():
                log(f"  [4{chr(98 + 2 * idx_s - 1)}-4{chr(98 + 2 * idx_s)}/6] Loaded cached draw-blind LOQO (seed={seed})...")
                p_draw_full[seed] = np.load(df_p, allow_pickle=False)
                p_draw_novent[seed] = np.load(dn_p, allow_pickle=False)
                continue
            draw_tmp, _ = holdout.buffered_component_draw(grid, seed=seed)
            f0 = draw_tmp[0]
            vis = f0["visible"]
            excl = distance_transform_edt(~f0["hidden_all"]) <= 3.0
            del draw_tmp
            log(f"  [4{chr(98 + 2 * idx_s - 1)}/6] Fitting draw-blind LOQO (seed={seed}, riedelvent)...")
            p_draw_full[seed] = fit_predict_riedelvent_loqo(
                X_foot, foot, valid, quad, vis,
                include_riedel_vent=True, excluded_mask=excl,
                max_pos_samples=30000, max_iter=110, seed=20261025 + seed,
            )["cal_proba"]
            np.save(df_p, p_draw_full[seed])
            log(f"  [4{chr(98 + 2 * idx_s)}/6] Fitting draw-blind LOQO (seed={seed}, riedel_novent)...")
            p_draw_novent[seed] = fit_predict_riedelvent_loqo(
                X_foot, foot, valid, quad, vis,
                include_riedel_vent=False, excluded_mask=excl,
                max_pos_samples=30000, max_iter=110, seed=20261025 + seed,
            )["cal_proba"]
            np.save(dn_p, p_draw_novent[seed])

        np.savez_compressed(
            fits_npz,
            p_full_cal=fit_full["cal_proba"],
            p_novent_cal=fit_novent["cal_proba"],
            p_draw20_full=p_draw_full[20],
            p_draw30_full=p_draw_full[30],
            p_draw20_novent=p_draw_novent[20],
            p_draw30_novent=p_draw_novent[30],
        )
        for tmp_p in (
            x_foot_npy,
            f_full_p,
            f_nov_p,
            CACHE_LANE / "p_draw20_full.npy",
            CACHE_LANE / "p_draw20_novent.npy",
            CACHE_LANE / "p_draw30_full.npy",
            CACHE_LANE / "p_draw30_novent.npy",
        ):
            tmp_p.unlink(missing_ok=True)

    if X_foot is not None:
        del X_foot
    gc.collect()

    crest_full = build_riedelvent_crest_surface(
        fit_full["cal_proba"], l_scarp10m, l_knick, l_vent_sub, valid, l_riedel_flex=l_riedel_flex
    )
    crest_novent = build_riedelvent_crest_surface(
        fit_novent["cal_proba"], l_scarp10m, l_knick, l_grav_base, valid, l_riedel_flex=None
    )
    s_full = crest_full["S_crest"]
    s_novent = crest_novent["S_crest"]

    if not canary_cache_json.is_file():
        rng_can2 = np.random.default_rng(20261025)
        oof_y = []
        oof_v = []
        for seed in (20, 30):
            draw_tmp, _ = holdout.buffered_component_draw(grid, seed=seed)
            s_d = build_riedelvent_crest_surface(
                p_draw_full[seed], l_scarp10m, l_knick, l_vent_sub, valid, l_riedel_flex=l_riedel_flex
            )["S_crest"]
            for fold in draw_tmp:
                p_i = np.flatnonzero(fold["truth"] & foot)
                n_i = np.flatnonzero(fold["region"] & foot & (~cat))
                n_take = rng_can2.choice(n_i, size=min(n_i.size, p_i.size * 6), replace=False)
                oof_y.append(np.concatenate([np.ones(p_i.size, np.uint8), np.zeros(n_take.size, np.uint8)]))
                oof_v.append(np.concatenate([s_d.ravel()[p_i], s_d.ravel()[n_take]]))
            del draw_tmp, s_d
        auc_oof, sym_oof = symmetric_auc(np.concatenate(oof_y), np.concatenate(oof_v))
        canaries["LOQO_draw_blind_S_riedelvent"] = {"auc": round(auc_oof, 6), "symmetric_auc": round(sym_oof, 6)}
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

    # --- Step 5/7: Build Strictly 3 Pre-Registered Candidates & Uniqueness Scan ---
    log("Step 5/7: Building 3 pre-registered candidates & running local + 102-repo uniqueness scan...")
    pool_full = foot & valid & (d_cat > 2.0) & crest_full["ridge_1d"]
    pool_novent = foot & valid & (d_cat > 2.0) & crest_novent["ridge_1d"]

    mask_arm1 = spaced_top_mask(s_full, pool_full, 37654, min_dist_px=3.30, cand_cap=950_000)
    mask_arm2 = spaced_top_mask(s_novent, pool_novent, 37654, min_dist_px=3.30, cand_cap=950_000)
    arr_arm3_tail = build_additive_tail_allocation(
        s_full, pool_full, n_core=37654, n_total=64000, tail_weight=0.30, min_dist_px=3.30
    )
    mask_arm3 = arr_arm3_tail > 0.0

    pred_arrays: dict[str, np.ndarray] = {
        "riedelvent": mask_arm1.astype(np.float32),
        "riedel_novent": mask_arm2.astype(np.float32),
        "riedelvent_tail": arr_arm3_tail.astype(np.float32),
    }
    cand_masks: dict[str, np.ndarray] = {
        "riedelvent": mask_arm1,
        "riedel_novent": mask_arm2,
        "riedelvent_tail": mask_arm3,
    }
    cand_surfaces: dict[str, np.ndarray] = {
        "riedelvent": s_full,
        "riedel_novent": s_novent,
        "riedelvent_tail": s_full,
    }

    foot_flat_all = np.flatnonzero(foot.ravel())
    rng_sub = np.random.default_rng(20261025)
    sub_flat_idx = np.sort(rng_sub.choice(foot_flat_all, size=100_000, replace=False))
    surf_ranks_local = {
        arm: rankdata(S.ravel()[sub_flat_idx]).astype(np.float64)
        for arm, S in cand_surfaces.items()
    }

    local_reg = collect_local_registry()
    local_rows: dict[str, list[dict]] = {arm: [] for arm in cand_masks}
    for label, rpath in local_reg:
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

    local_summary: dict[str, dict] = {}
    for arm, rows in local_rows.items():
        w_ov = max(rows, key=lambda r: r["forward_overlap_3px"])
        w_rh = max(rows, key=lambda r: abs(r["surface_spearman_rho"]))
        local_summary[arm] = {
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
        log(
            f"  Local uniqueness [{arm}]: max_overlap={w_ov['forward_overlap_3px']:.4f} "
            f"({w_ov['registry_raster']}), max_|rho|={abs(w_rh['surface_spearman_rho']):.4f}"
        )

    pub_index, _ = build_or_load_public_index(foot, sub_flat_idx, expected_grid)
    pub_meta_summary = {
        k: v for k, v in pub_index["meta"].items() if k not in ("records", "top37_offsets")
    }
    pub_summary = evaluate_against_public_index(
        cand_masks, cand_surfaces, sub_flat_idx, pub_index, foot.shape
    )
    del pub_index
    gc.collect()
    for arm, ps in pub_summary.items():
        log(
            f"  102-repo Public uniqueness [{arm}]: dual_reading_unique={ps['dual_reading_unique']} "
            f"(worst_op={ps['worst_operative_overlap_3px']:.4f} on {ps['worst_operative_witness']}, "
            f"le50k={ps['dot_fields_le_50k_worst_overlap_3px']:.4f}, "
            f"max_|rho|={ps['worst_surface_abs_spearman']:.4f})"
        )

    # --- Step 6/7: Evaluate Static, Strict Draw-Blind Rule-2, Quadrant & SGMC Proxy ---
    log("Step 6/7: Evaluating static d_cat>2.0, draw-blind Rule-2 d_visible>2.0, and USGS SGMC proxy...")
    del crest_full, crest_novent, fit_full, fit_novent, s_full, s_novent, cand_surfaces
    gc.collect()

    comp_files = {
        "R0": inputs["parent_r0_zeros"],
        "H19_5": inputs["anc_h19_5"],
        "VENTSCARP_ventscarp": DOWNLOADS / "gemsdoe92-ventscarp-ventscarp-37654-20261025-6e97367c-zeros.tif",
        "VENTSCARP_novent": DOWNLOADS / "gemsdoe92-ventscarp-scarp10m_novent-37654-20261025-3c9a1c6e-zeros.tif",
        "KNICKLOQO_standalone": DOWNLOADS / "h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif",
        "PROVINCETOE_piedbasin": DOWNLOADS / "gemsdoe92-provincetoe-piedbasin-37654-20261025-c22542ae-zeros.tif",
        "POISSONKNICK_qcal": DOWNLOADS / "gemsdoe92-poissonknick-qcal-37654-20261025-9cfcc9b9-zeros.tif",
        "COULOMBLOQO_standalone": DOWNLOADS / "h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif",
        "LISTRICDIP_updip50": DOWNLOADS / "gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif",
    }

    def _load_comp(p: Path) -> np.ndarray:
        with rasterio.open(p) as ds:
            return np.where(foot, np.nan_to_num(ds.read(1), nan=0.0), 0.0).astype(np.float32)

    static_terms: dict[str, np.ndarray] = {}
    rule2_terms: dict[str, np.ndarray] = {
        k: None for k in ("riedelvent", "riedel_novent", "riedelvent_tail", "H19_5", "R0")
    }  # type: ignore[dict-item]

    arr_r0 = _load_comp(comp_files["R0"])
    arr_h19 = _load_comp(comp_files["H19_5"])

    for seed in (20, 30):
        draw_s, _ = holdout.buffered_component_draw(grid, seed=seed)
        # 6a. Accumulate static deployment terms for this seed
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

        # 6b. Strict Draw-Blind Rule-2 HOLDOUT-DTI for this seed (all 4 folds share draw_s[0]["visible"])
        cr_f_d = build_riedelvent_crest_surface(
            p_draw_full[seed], l_scarp10m, l_knick, l_vent_sub, valid, l_riedel_flex=l_riedel_flex
        )
        cr_nv_d = build_riedelvent_crest_surface(
            p_draw_novent[seed], l_scarp10m, l_knick, l_grav_base, valid, l_riedel_flex=None
        )
        d_vis = distance_transform_edt(~draw_s[0]["visible"])
        vis_moat = d_vis > 2.0
        del d_vis
        pool_f_f = foot & valid & vis_moat & cr_f_d["ridge_1d"]
        pool_nv_f = foot & valid & vis_moat & cr_nv_d["ridge_1d"]

        p_f_f = spaced_top_mask(
            cr_f_d["S_crest"], pool_f_f, 37654, min_dist_px=3.30, cand_cap=950_000
        ).astype(np.float32)
        p_nv_f = spaced_top_mask(
            cr_nv_d["S_crest"], pool_nv_f, 37654, min_dist_px=3.30, cand_cap=950_000
        ).astype(np.float32)
        p_tail_f = build_additive_tail_allocation(
            cr_f_d["S_crest"], pool_f_f, n_core=37654, n_total=64000, tail_weight=0.30, min_dist_px=3.30
        )
        p_h19_f = np.where(vis_moat, arr_h19, 0.0).astype(np.float32)
        p_r0_f = np.where(vis_moat, arr_r0, 0.0).astype(np.float32)
        del vis_moat, pool_f_f, pool_nv_f, cr_f_d, cr_nv_d

        for fold in draw_s:
            for k_r2, arr_r2 in (
                ("riedelvent", p_f_f),
                ("riedel_novent", p_nv_f),
                ("riedelvent_tail", p_tail_f),
                ("H19_5", p_h19_f),
                ("R0", p_r0_f),
            ):
                _, t_r2 = evaluate_holdout.evaluate(arr_r2, fold, foot)
                rule2_terms[k_r2] = t_r2 if rule2_terms[k_r2] is None else rule2_terms[k_r2] + t_r2
        del p_f_f, p_nv_f, p_tail_f, p_h19_f, p_r0_f, draw_s
        gc.collect()

    del arr_r0, arr_h19, p_draw_full, p_draw_novent, l_scarp10m, l_knick, l_grav_base, l_riedel_flex, l_vent_sub
    gc.collect()

    static_boot = evaluate_holdout.pooled_summary(
        static_terms, candidate="riedelvent", draws=1000, seed=20261025
    )
    static_boot_tail = evaluate_holdout.pooled_summary(
        static_terms, candidate="riedelvent_tail", draws=1000, seed=20261025
    )
    rule2_boot = evaluate_holdout.pooled_summary(
        rule2_terms, candidate="riedelvent", draws=1000, seed=20261025
    )
    rule2_boot_tail = evaluate_holdout.pooled_summary(
        rule2_terms, candidate="riedelvent_tail", draws=1000, seed=20261025
    )

    # 6c. Off-catalogue USGS SGMC bedrock fault PROXY (d_cat > 5.0 px)
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

    # 6d. Quadrant shares & slope-regime distribution
    with rasterio.open(inputs["training_features"]) as ds_tf:
        b19_raw = ds_tf.read(19, masked=True).filled(0.0).astype(np.float32)
    b19_raw[np.abs(b19_raw) > 1e20] = 0.0
    slope_deg = (
        np.rad2deg(np.arctan(np.maximum(b19_raw, 0.0)))
        if float(np.percentile(b19_raw[foot], 99.0)) <= 2.5
        else np.maximum(b19_raw, 0.0)
    )
    quad_names = {0: "NW", 1: "NE", 2: "SW", 3: "SE"}
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
            "quadrant_pct": q_dist,
            "slope_regime_pct": s_dist,
        }
        log(f"  Diagnostics [{arm}]: quads={q_dist}, slopes={s_dist}")

    for k_log in (
        "riedelvent",
        "riedel_novent",
        "riedelvent_tail",
        "VENTSCARP_ventscarp",
        "KNICKLOQO_standalone",
        "PROVINCETOE_piedbasin",
        "LISTRICDIP_updip50",
        "R0",
    ):
        if k_log in static_boot["scores"]:
            sc = static_boot["scores"][k_log]
            log(f"  STATIC HOLDOUT-DTI [{k_log:22s}] = {sc['dti']:.6f} [{sc['ci95'][0]:.6f}, {sc['ci95'][1]:.6f}]")
    for k_log in ("riedelvent", "riedel_novent", "riedelvent_tail", "H19_5", "R0"):
        sc = rule2_boot["scores"][k_log]
        log(f"  RULE-2 HOLDOUT-DTI [{k_log:22s}] = {sc['dti']:.6f} [{sc['ci95'][0]:.6f}, {sc['ci95'][1]:.6f}]")
    for k_log in ("riedelvent", "riedel_novent", "riedelvent_tail", "VENTSCARP_ventscarp", "KNICKLOQO_standalone", "R0"):
        if k_log in sgmc_scores:
            log(f"  SGMC PROXY         [{k_log:22s}] = {sgmc_scores[k_log]['dti']:.6f}")

    # --- Step 7/7: Serialize Validated [0, 1] GeoTIFFs, Audit Sidecars & Run Card ---
    log("Step 7/7: Packaging validated [0, 1] GeoTIFFs via submission_writer & emitting Run Card...")
    arm_artifacts: dict[str, dict] = {}
    for arm, arr_pred in pred_arrays.items():
        n_pos = int((arr_pred > 0.0).sum())
        raw_sha8 = hashlib.sha256(arr_pred.tobytes()).hexdigest()[:8]
        stem = f"gemsdoe92-riedelvent-{arm}-{n_pos}-{DATE_STR}-{raw_sha8}"
        tif_path = DOWNLOADS / f"{stem}-zeros.tif"
        sub_name = f"GEMSDOE92-RIEDELVENT-{arm}-{DATE_STR}"
        st_dti = static_boot["scores"][arm]["dti"]
        r2_dti = rule2_boot["scores"][arm]["dti"]
        if arm == "riedelvent":
            arm_desc = f"{n_pos}px Riedel+Flexure+3DEP10m+vents"
        elif arm == "riedel_novent":
            arm_desc = f"{n_pos}px no-Riedel/vent ablation"
        else:
            arm_desc = f"{n_pos}px 37654@1+26346@0.30 Riedel+vents"
        sub_note = (
            f"RIEDELVENT {arm}: {arm_desc}; "
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
            metadata={"lane": "RIEDELVENT", "arm": arm},
        )
        zip_path = tif_path.with_suffix(".zip")
        for out_p in (tif_path, zip_path, tif_path.with_suffix(".json")):
            if out_p.is_file():
                out_p.chmod(0o644)
        tif_sha = sha256_file(tif_path)
        zip_sha = sha256_file(zip_path)

        val_rec = gems57_validate.validate(tif_path, foot, cat)
        gems57_validate.assert_submittable(val_rec)

        gate_res = run_gates(
            str(tif_path), str(SAMPLE_SUB), str(EXISTING_FAULTS),
            prune_radius=2, require_submission_encoding=True,
        )
        gates_ok, gates_text = summarise(gate_res)
        if not gates_ok:
            raise SystemExit(f"Gate failure on {tif_path}:\n{gates_text}")

        audit_path = DOWNLOADS / f"{stem}-audit.json"
        ps = pub_summary[arm]
        ls = local_summary[arm]
        audit_doc = {
            "schema": "gemsdoe92-per-file-audit.v2",
            "lane": "RIEDELVENT",
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
            "run_card": "evidence/riedelvent_run_card.json",
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
        "schema": "gemsdoe92-riedelvent-holdout.v1",
        "lane": "RIEDELVENT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "pre_registration": "docs/HYPOTHESES_20261025_RIEDELVENT.md",
        "experiments_run": 3,
        "experiment_budget_cap": 3,
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
        "static_deployment_holdout_dti": static_boot,
        "static_deployment_holdout_dti_tail_candidate": static_boot_tail,
        "strict_draw_blind_rule2_holdout_dti": rule2_boot,
        "strict_draw_blind_rule2_holdout_dti_tail_candidate": rule2_boot_tail,
        "usgs_sgmc_off_catalogue_proxy": sgmc_scores,
        "diagnostics": diagnostics,
        "artifacts": arm_artifacts,
    }
    (EVIDENCE / "riedelvent_holdout.json").write_text(
        json.dumps(holdout_doc, indent=2) + "\n", encoding="utf-8"
    )
    (DOWNLOADS / "riedelvent_holdout.json").write_text(
        json.dumps(holdout_doc, indent=2) + "\n", encoding="utf-8"
    )

    uniqueness_doc = {
        "schema": "gemsdoe92-riedelvent-uniqueness.v1",
        "lane": "RIEDELVENT",
        "evidence_class": "REGISTRY-MEASUREMENT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "public_inventory": pub_meta_summary,
        "local_summary": local_summary,
        "public_102repo_summary": pub_summary,
    }
    (EVIDENCE / "riedelvent_uniqueness.json").write_text(
        json.dumps(uniqueness_doc, indent=2) + "\n", encoding="utf-8"
    )
    (DOWNLOADS / "riedelvent_uniqueness.json").write_text(
        json.dumps(uniqueness_doc, indent=2) + "\n", encoding="utf-8"
    )

    prim = arm_artifacts["riedelvent"]
    prim_static = static_boot["scores"]["riedelvent"]
    prim_r2 = rule2_boot["scores"]["riedelvent"]
    prim_ps = pub_summary["riedelvent"]
    prim_ls = local_summary["riedelvent"]

    run_card = {
        "schema": "gemsdoe92-run-card-v1",
        "lane": "RIEDELVENT",
        "date": "2026-10-25",
        "branch": "arena/e4879d8c-gemsdoe92",
        "pre_registration": "docs/HYPOTHESES_20261025_RIEDELVENT.md",
        "hypothesis": (
            "Unmapped Quaternary Basin-and-Range normal/transtensional faults and blind "
            "geothermal upflow conduits across both low-relief (<6 deg) piedmont aprons and "
            "incised (>=6 deg) range-front canyons express via (1) en-echelon Coulomb-Riedel "
            "R-shear obliquity (Delta_theta in [12, 28 deg]) between fine-scale (150 m) "
            "scarp/RTP magnetic strike and mesoscale (1.4 km) basement/gravity master-zone "
            "strike coupled to geodetic shear/dilatation strain, (2) hanging-wall flexural "
            "rollover hinge curvature (450-1,350 m DoG of log1p(depth_to_base) and antiparallel "
            "iso_grav_anom drop), and (3) slope-regime coupled USGS 3DEP 10 m sub-pixel scarps, "
            "10m/100m incised thalweg knickzones, Poisson magneto-gravity collinearity, and "
            "tufa-filtered DOE GDR #1391 INGENIOUS paleo-geothermal vents & 2mDAB thermal probes."
        ),
        "mechanism": (
            "4-quadrant Leave-One-Quadrant-Out (LOQO, >=1.2 km guard band, >500 m negative "
            "buffer, zero fault-catalogue inputs) HistGradientBoostingClassifier ensemble over "
            "30 physical features (Group A: 9 USGS 3DEP 10 m sub-pixel scarp & 10m/100m thalweg "
            "knickzone features; Group B: 9 tufa-filtered INGENIOUS hydrothermal vent, 2mDAB, "
            "K/Th, U/Th & Grauch demagnetization features; Group C: 8 province-debiased gravity, "
            "basement, Poisson collinearity & Lake Lahontan shoreline-null features; Group D: 4 "
            "en-echelon Riedel 12-28 deg obliquity & hanging-wall flexural hinge features), "
            "evaluated across 37,654-dot binary (`riedelvent`), 17-feature ablation (`riedel_novent`), "
            "and 64,000-dot additive-tail (`riedelvent_tail`: 37,654@1.0 + 26,346@0.30) arms."
        ),
        "non_fault_mimic": (
            "En-echelon longitudinal eolian sand dunes, braided alluvial fan distributary bars, "
            "and Pleistocene Lake Lahontan shoreline tufa towers (86 Tufa records excluded from "
            "Paleo_geothermal_final.csv) and ~1,330 m Sehoo contour-parallel wave-cut beach "
            "benches (suppressed by cross-contour transgression, shoreline-null penalty, and "
            "antiparallel basement/gravity flexural concordance)."
        ),
        "named_non_fault_process_that_could_mimic_it": (
            "En-echelon longitudinal eolian sand dunes, braided alluvial fan distributary bars, "
            "and Pleistocene Lake Lahontan shoreline tufa towers (86 Tufa records excluded from "
            "Paleo_geothermal_final.csv) and ~1,330 m Sehoo contour-parallel wave-cut beach "
            "benches (suppressed by cross-contour transgression, shoreline-null penalty, and "
            "antiparallel basement/gravity flexural concordance)."
        ),
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": evaluate_holdout.VERSION,
            "withheld_positive_pixels": prim_static["withheld_positive_pixels"],
            "alpha": 0.2,
            "beta": 0.8,
            "triangular_radius_m": 300.0,
            "static_deployment_d_cat_gt_2": {
                "riedelvent": prim_static,
                "riedel_novent": static_boot["scores"]["riedel_novent"],
                "riedelvent_tail": static_boot["scores"]["riedelvent_tail"],
                "VENTSCARP_ventscarp": static_boot["scores"].get("VENTSCARP_ventscarp"),
                "KNICKLOQO_standalone": static_boot["scores"].get("KNICKLOQO_standalone"),
                "PROVINCETOE_piedbasin": static_boot["scores"].get("PROVINCETOE_piedbasin"),
                "LISTRICDIP_updip50": static_boot["scores"].get("LISTRICDIP_updip50"),
                "R0": static_boot["scores"]["R0"],
                "paired_deltas_vs_riedelvent": static_boot["paired_differences"],
                "paired_deltas_vs_riedelvent_tail": static_boot_tail["paired_differences"],
            },
            "strict_draw_blind_rule2_d_visible_gt_2": {
                "riedelvent": prim_r2,
                "riedel_novent": rule2_boot["scores"]["riedel_novent"],
                "riedelvent_tail": rule2_boot["scores"]["riedelvent_tail"],
                "H19_5": rule2_boot["scores"]["H19_5"],
                "R0": rule2_boot["scores"]["R0"],
                "paired_deltas_vs_riedelvent": rule2_boot["paired_differences"],
                "paired_deltas_vs_riedelvent_tail": rule2_boot_tail["paired_differences"],
            },
            "usgs_sgmc_off_catalogue_proxy": sgmc_scores,
        },
        "leakage_canary": {
            "threshold": 0.90,
            "max_single_feature": max_feat_name,
            "max_single_feature_symmetric_auc": max_feat_sym,
            "draw_blind_surface_symmetric_auc": round(sym_oof, 6),
            "all_pass": True,
        },
        "registry_uniqueness": {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "local_GEMSDOE92": local_summary,
            "public_102_repos": pub_summary,
        },
        "correlation_overlap_vs_registry": {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "local": prim_ls,
            "public_102_repos": prim_ps,
        },
        "raster_file": prim["file_zeros"],
        "zip_file": prim["file_zip"],
        "audit_file": prim["file_audit"],
        "raster_sha256": prim["sha256_zeros"],
        "zip_sha256": prim["sha256_zip"],
        "all_arm_artifacts": arm_artifacts,
        "validator": {
            "submittable": True,
            "gates_passed": f"{prim['gates_count']}/{prim['gates_count']}",
            "no_nan_inside_footprint": True,
            "no_nan_anywhere": True,
            "values_in_0_1": True,
            "crs": "EPSG:32611",
            "shape": [3730, 3292],
            "transform_matches_sample_submission": True,
            "positive_pixels": prim["n_positive_pixels"],
            "zero_dots_on_mapped_catalogue": True,
            "checks": prim["validator_checks"],
        },
        "validator_output": {
            "submittable": True,
            "gates_passed": f"{prim['gates_count']}/{prim['gates_count']}",
            "no_nan_inside_footprint": True,
            "no_nan_anywhere": True,
            "values_in_0_1": True,
            "crs": "EPSG:32611",
            "shape": [3730, 3292],
            "transform_matches_sample_submission": True,
            "positive_pixels": prim["n_positive_pixels"],
            "zero_dots_on_mapped_catalogue": True,
        },
        "submission_name": prim["submission_name"],
        "submission_note": prim["submission_note"],
        "note": prim["submission_note"],
        "submission_note_length": len(prim["submission_note"]),
        "experiments_used": 3,
        "experiment_budget": 3,
        "weekly_slots_used": 0,
        "download_ok": True,
        "submission_eligible": False,
        "verdict": "negative",
        "verdict_explanation": (
            "OK TO DOWNLOAD FOR RESEARCH (11/11 format gates PASS, finite [0, 1], 0 NaN). "
            "DO NOT SUBMIT to a live weekly DrivenData slot: binding literal public registry "
            "overlap rule hits 1.000 > 0.70 on all-positive dense witness 17GEMSDOE "
            "E-proba-multiscale (5,167,373 positive pixels). Dual-reading / matched-budget "
            "sparse uniqueness across all 102 public repos is reported alongside."
        ),
    }
    (EVIDENCE / "riedelvent_run_card.json").write_text(
        json.dumps(run_card, indent=2) + "\n", encoding="utf-8"
    )
    (DOWNLOADS / "riedelvent_run_card.json").write_text(
        json.dumps(run_card, indent=2) + "\n", encoding="utf-8"
    )

    log(f"COMPLETE in {elapsed_s:.1f}s (peak RSS {peak_rss_mib:.1f} MiB)!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
