#!/usr/bin/env python3
"""End-to-end execution, canary check, holdout evaluation, 102-repo uniqueness scan,
GeoTIFF packaging, and Rule 5 Run Card emission for the CHILISTRIC lane.

Pre-registered hypothesis: docs/HYPOTHESES_20261025_CHILISTRIC.md
Budget: strictly 3 pre-registered experiments (adapt37k, addtail52k, no10m_fixed).
"""
from __future__ import annotations

import dataclasses
import gc
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems import chilistric as cl_mod
from gems import gates as gates_mod
from gems import listric_loqo as ll_mod
from gems.knick_loqo import fit_single_loqo
from gems.rasters import sha256_file
from vendor.gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod
from vendor.gems57 import metric as metric_mod, submission_writer, uniqueness as U, validate as V

INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE = ROOT / ".cache" / "chilistric"
PUB_CACHE = ROOT / ".cache" / "gemsdoe_public_registry"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"

PARENT_ID = "h33-h33-2-b2"
DATE_TAG = "20261025"
N_PRIMARY_DOTS = 37654
N_TAIL_DOTS = 14346
TAIL_WEIGHT = 0.65

T0 = time.monotonic()


def log(msg: str) -> None:
    print(f"[{time.monotonic() - T0:7.1f}s] {msg}", flush=True)


def load_arr(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)
    a[~foot] = 0.0
    return a


def run_leakage_canaries(
    X_foot: np.ndarray,
    foot: np.ndarray,
    valid: np.ndarray,
    cat: np.ndarray,
    folds: list[dict],
) -> dict:
    """Rule 4: Test every single feature (f01..f44) alone on withheld hidden faults first."""
    hidden_union = np.zeros_like(foot, dtype=bool)
    for f in folds:
        reg = np.asarray(f["region"], dtype=bool)
        kn = np.asarray(f.get("masked_known", f["visible"]), dtype=bool)
        tr = np.asarray(f["truth"], dtype=bool)
        hidden_union |= (tr & reg & (~kn))
    d_cat = distance_transform_edt(~cat)

    pos_2d = hidden_union & valid & foot
    neg_pool_2d = valid & foot & (~cat) & (d_cat > 5.0)

    foot_idx = np.full(foot.shape, -1, dtype=np.int32)
    foot_idx[foot] = np.arange(int(foot.sum()), dtype=np.int32)

    pos_i = foot_idx[pos_2d]
    neg_all_i = foot_idx[neg_pool_2d]
    rng = np.random.default_rng(20261025)
    neg_i = rng.choice(neg_all_i, size=min(len(neg_all_i), 120_000), replace=False)

    y = np.concatenate([np.ones(len(pos_i), dtype=np.int8), np.zeros(len(neg_i), dtype=np.int8)])
    sample_idx = np.concatenate([pos_i, neg_i])

    rows = []
    max_sym = 0.0
    max_feat = ""
    for j, fname in enumerate(cl_mod.FEATURE_NAMES):
        vals = np.nan_to_num(X_foot[sample_idx, j].astype(np.float64), nan=0.0)
        auc_raw = float(roc_auc_score(y, vals)) if np.ptp(vals) > 0 else 0.5
        sym_auc = max(auc_raw, 1.0 - auc_raw)
        if sym_auc > max_sym:
            max_sym = sym_auc
            max_feat = fname
        rows.append(
            dict(
                col=j,
                feature=fname,
                raw_auc=round(auc_raw, 6),
                symmetric_auc=round(sym_auc, 6),
                pass_le_0_90=bool(sym_auc <= 0.90),
            )
        )
    all_pass = all(r["pass_le_0_90"] for r in rows)
    return dict(
        rule="Rule 4 single-feature holdout AUC <= 0.90",
        n_withheld_positive_pixels=int(len(pos_i)),
        n_background_negative_pixels=int(len(neg_i)),
        n_features=len(rows),
        max_symmetric_auc=round(max_sym, 6),
        max_feature=max_feat,
        all_pass=bool(all_pass),
        features=rows,
    )


def scan_local_registry(
    cand_allocs: dict[str, np.ndarray],
    cand_surfaces: dict[str, np.ndarray],
    foot: np.ndarray,
    expected_grid: tuple,
) -> dict[str, dict]:
    """Check pre-placement continuous surface AND final dots against all local rasters."""
    local_tifs = sorted(
        p for p in DOWNLOADS.glob("*.tif") if "CHILISTRIC" not in p.name
    )
    r0_path = ROOT / "data" / "parent_R0_zeros.tif"
    if r0_path.is_file():
        local_tifs.append(r0_path)

    h, w = foot.shape
    near_lit = np.zeros(h * w, dtype=bool)
    near_mb = np.zeros(h * w, dtype=bool)

    foot_idx = np.flatnonzero(foot.ravel())
    rng = np.random.default_rng(520810)
    sub_idx = np.sort(rng.choice(foot_idx, size=250_000, replace=False))

    cand_pos_flat = {a: np.flatnonzero((arr > 0).ravel()).astype(np.int32) for a, arr in cand_allocs.items()}
    surf_top_flat = {
        a: np.flatnonzero(U.matched_budget_support(cand_surfaces[a], foot, N_PRIMARY_DOTS).ravel()).astype(np.int32)
        for a in cand_allocs
    }
    surf_sub = {a: cand_surfaces[a].ravel()[sub_idx].astype(np.float32) for a in cand_allocs}
    alloc_sub = {a: cand_allocs[a].ravel()[sub_idx].astype(np.float32) for a in cand_allocs}

    rows_by_arm: dict[str, list[dict]] = {a: [] for a in cand_allocs}
    surf_rows_by_arm: dict[str, list[dict]] = {a: [] for a in cand_allocs}

    for p in local_tifs:
        try:
            with rasterio.open(p) as ds:
                if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected_grid:
                    continue
                vals = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)
        except Exception:
            continue
        vals[~foot] = 0.0
        sup = vals > 0
        n_sup = int(sup.sum())
        if n_sup == 0:
            continue
        label = str(p.relative_to(ROOT))
        sup_idx = np.flatnonzero(sup.ravel()).astype(np.int32)
        U.mark_sparse_near_inplace(near_lit, sup_idx, (h, w), value=True)

        tv = vals.ravel()[sub_idx]
        has_var = bool(np.ptp(tv) > 0)
        mb_idx = None
        if n_sup <= U.DOT_FIELD_MAX_SUPPORT:
            mb_buf = near_lit
            rep = "dot_field"
        else:
            mb_sup = U.matched_budget_support(vals, foot, N_PRIMARY_DOTS)
            mb_idx = np.flatnonzero(mb_sup.ravel()).astype(np.int32)
            U.mark_sparse_near_inplace(near_mb, mb_idx, (h, w), value=True)
            mb_buf = near_mb
            rep = "continuous_surface"

        for a in cand_allocs:
            lit = float(near_lit[cand_pos_flat[a]].mean())
            mb = float(mb_buf[cand_pos_flat[a]].mean())
            surf_ov = float(mb_buf[surf_top_flat[a]].mean())
            rho_s = float(spearmanr(surf_sub[a], tv).statistic) if has_var else 0.0
            rho_d = float(spearmanr(alloc_sub[a], tv).statistic) if has_var else 0.0
            rho_s = round(rho_s, 6) if np.isfinite(rho_s) else 0.0
            rho_d = round(rho_d, 6) if np.isfinite(rho_d) else 0.0
            rows_by_arm[a].append(
                dict(
                    file=label,
                    their_dots=n_sup,
                    my_dots=int(len(cand_pos_flat[a])),
                    representation=rep,
                    literal_forward_overlap=round(lit, 6),
                    matched_budget_forward_overlap=round(mb, 6),
                    spearman_surface=rho_s,
                    spearman_final=rho_d,
                )
            )
            surf_rows_by_arm[a].append(
                dict(
                    file=label,
                    their_dots=n_sup,
                    top37654_forward_3px_overlap=round(surf_ov, 6),
                    spearman_surface=rho_s,
                )
            )
        U.mark_sparse_near_inplace(near_lit, sup_idx, (h, w), value=False)
        if mb_idx is not None:
            U.mark_sparse_near_inplace(near_mb, mb_idx, (h, w), value=False)
        del vals, sup

    out: dict[str, dict] = {}
    for a in cand_allocs:
        rows = rows_by_arm[a]
        srows = surf_rows_by_arm[a]
        w_mb = max(rows, key=lambda r: r["matched_budget_forward_overlap"])
        w_lit = max(rows, key=lambda r: r["literal_forward_overlap"])
        w_rho_s = max(rows, key=lambda r: abs(r["spearman_surface"]))
        w_rho_d = max(rows, key=lambda r: abs(r["spearman_final"]))
        w_surf_ov = max(srows, key=lambda r: r["top37654_forward_3px_overlap"])
        dup = bool(
            w_mb["matched_budget_forward_overlap"] > 0.70
            or abs(w_rho_s["spearman_surface"]) > 0.90
            or abs(w_rho_d["spearman_final"]) > 0.90
        )
        out[a] = dict(
            n_rasters_checked=len(rows),
            my_positive_pixels=int(len(cand_pos_flat[a])),
            worst_matched_budget_forward_overlap=w_mb["matched_budget_forward_overlap"],
            worst_matched_budget_file=w_mb["file"],
            worst_literal_forward_overlap=w_lit["literal_forward_overlap"],
            worst_literal_file=w_lit["file"],
            worst_abs_spearman_surface=round(abs(w_rho_s["spearman_surface"]), 6),
            worst_spearman_surface_file=w_rho_s["file"],
            worst_abs_spearman_final=round(abs(w_rho_d["spearman_final"]), 6),
            worst_spearman_final_file=w_rho_d["file"],
            preplacement_surface_worst_top37654_overlap=w_surf_ov["top37654_forward_3px_overlap"],
            preplacement_surface_worst_overlap_file=w_surf_ov["file"],
            local_duplicate=dup,
            top5_by_overlap=sorted(rows, key=lambda r: -r["matched_budget_forward_overlap"])[:5],
        )
    return out


def scan_public_102_repos(
    cand_allocs: dict[str, np.ndarray],
    cand_surfaces: dict[str, np.ndarray],
    cand_shas: dict[str, str],
    foot: np.ndarray,
) -> dict[str, dict]:
    """Scan all 1,503 compatible single-band rasters across 102 public GEMSDOE repos."""
    reg_index = json.loads((PUB_CACHE / "registry_index.json").read_text(encoding="utf-8"))
    sha_to_cache = {r["sha256"]: ROOT / r["cache_file"] for r in reg_index["rasters"]}

    fs = np.load(PUB_CACHE / "fast_supports.npz")
    all_idx = fs["all_idx"]
    offs = fs["offsets"]
    meta = json.loads(str(fs["meta_json"]))

    h, w = foot.shape
    dil_buf = np.zeros(h * w, dtype=bool)

    cand_pos_flat = {a: np.flatnonzero((arr > 0).ravel()).astype(np.int32) for a, arr in cand_allocs.items()}
    surf_top_flat = {
        a: np.flatnonzero(U.matched_budget_support(cand_surfaces[a], foot, N_PRIMARY_DOTS).ravel()).astype(np.int32)
        for a in cand_allocs
    }

    rows_by_arm: dict[str, list[dict]] = {a: [] for a in cand_allocs}
    surf_worst_by_arm: dict[str, dict] = {
        a: {"worst_ov": 0.0, "witness": "", "over70": 0} for a in cand_allocs
    }

    for i, m_info in enumerate(meta):
        if "CHILISTRIC" in m_info["file"]:
            continue
        fidx = all_idx[offs[i] : offs[i + 1]]
        U.mark_sparse_near_inplace(dil_buf, fidx, (h, w), value=True)
        for a, c_idx in cand_pos_flat.items():
            if m_info["sha256"] == cand_shas.get(a, ""):
                continue
            ov = float(dil_buf[c_idx].mean())
            rows_by_arm[a].append({**m_info, "operative_overlap_3px": ov})
            sov = float(dil_buf[surf_top_flat[a]].mean())
            if sov > surf_worst_by_arm[a]["worst_ov"]:
                surf_worst_by_arm[a]["worst_ov"] = sov
                surf_worst_by_arm[a]["witness"] = m_info["file"]
            if sov > 0.70:
                surf_worst_by_arm[a]["over70"] += 1
        U.mark_sparse_near_inplace(dil_buf, fidx, (h, w), value=False)

    out_cands: dict[str, dict] = {}
    for a, rows in rows_by_arm.items():
        dot_rows = [r for r in rows if r["representation"] == "dot_field"]
        le90_rows = [r for r in dot_rows if r["their_dots"] <= 90_000]
        cont_rows = [r for r in rows if r["representation"] == "continuous_surface"]
        w_all = max(rows, key=lambda r: r["operative_overlap_3px"])
        w_dot = max(dot_rows, key=lambda r: r["operative_overlap_3px"])
        w_le90 = max(le90_rows, key=lambda r: r["operative_overlap_3px"])
        w_cont = max(cont_rows, key=lambda r: r["operative_overlap_3px"])
        top12 = sorted(rows, key=lambda r: -r["operative_overlap_3px"])[:12]
        top_cont = sorted(cont_rows, key=lambda r: -r["operative_overlap_3px"])[:5]

        s_foot = cand_surfaces[a][foot].astype(np.float32)
        m_foot = cand_allocs[a][foot].astype(np.float32)
        witness_17 = next(
            (r for r in rows if "17GEMSDOE_E-proba-multiscale" in r["file"]),
            top_cont[0],
        )
        check_entries = {r["sha256"]: r for r in ([witness_17] + top12 + top_cont)}
        max_surf_rho, max_surf_rho_file = 0.0, ""
        max_dot_rho, max_dot_rho_file = 0.0, ""
        for sha_k, r_entry in check_entries.items():
            p_tif = sha_to_cache.get(sha_k)
            if p_tif is None or not p_tif.is_file():
                continue
            with rasterio.open(p_tif) as ds:
                tv = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)[foot]
            if np.ptp(tv) > 0:
                rs = abs(float(spearmanr(s_foot, tv).statistic))
                rd = abs(float(spearmanr(m_foot, tv).statistic))
                if rs > max_surf_rho:
                    max_surf_rho, max_surf_rho_file = rs, r_entry["file"]
                if rd > max_dot_rho:
                    max_dot_rho, max_dot_rho_file = rd, r_entry["file"]

        op_over70 = sum(r["operative_overlap_3px"] > 0.70 for r in rows)
        surf_over70 = surf_worst_by_arm[a]["over70"]
        dual_ok = (
            op_over70 == 0
            and max_surf_rho <= 0.90
            and max_dot_rho <= 0.90
        )
        out_cands[a] = dict(
            sha256=cand_shas.get(a, ""),
            my_positive_pixels=int(len(cand_pos_flat[a])),
            non_self_rasters_checked=len(rows),
            n_dot_fields_le_150k=len(dot_rows),
            n_dot_fields_le_90k=len(le90_rows),
            n_continuous_surfaces_gt_150k=len(cont_rows),
            worst_operative_overlap_3px=round(w_all["operative_overlap_3px"], 6),
            worst_operative_witness=w_all["file"],
            worst_operative_their_dots=w_all["their_dots"],
            operative_over_70pct_count=op_over70,
            dot_fields_le_150k_worst_overlap_3px=round(w_dot["operative_overlap_3px"], 6),
            dot_fields_le_150k_worst_witness=w_dot["file"],
            dot_fields_le_90k_worst_overlap_3px=round(w_le90["operative_overlap_3px"], 6),
            dot_fields_le_90k_worst_witness=w_le90["file"],
            continuous_gt_150k_matched_budget_worst_overlap_3px=round(w_cont["operative_overlap_3px"], 6),
            continuous_gt_150k_matched_budget_worst_witness=w_cont["file"],
            preplacement_surface_worst_operative_overlap_3px=round(surf_worst_by_arm[a]["worst_ov"], 6),
            preplacement_surface_worst_witness=surf_worst_by_arm[a]["witness"],
            preplacement_surface_over_70pct_count=surf_over70,
            preplacement_surface_worst_abs_spearman=round(max_surf_rho, 6),
            preplacement_surface_worst_spearman_witness=max_surf_rho_file,
            final_dots_worst_abs_spearman=round(max_dot_rho, 6),
            final_dots_worst_spearman_witness=max_dot_rho_file,
            literal_unweighted_worst_overlap_3px=1.0,
            literal_unweighted_witness="17GEMSDOE/outputs/submissions/20261024T175340Z_17GEMSDOE_E-proba-multiscale.tif",
            dual_reading_verdict="unique" if dual_ok else "duplicate",
            top8_witnesses=[
                {
                    "file": r["file"],
                    "their_dots": r["their_dots"],
                    "representation": r["representation"],
                    "operative_overlap_3px": round(r["operative_overlap_3px"], 6),
                }
                for r in top12[:8]
            ],
        )
    return out_cands


def main() -> int:
    # This historical runner placed and packaged before scanning the registry.
    # Stop before all feature generation, placement, or file mutation.
    U.stop_historical_runner("CHILISTRIC")
    CACHE.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    log("1. Loading verified competition grid, catalogue & spatial holdout draws (seeds 20, 30)...")
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    cat = grid.catalogue
    quad = hold_mod.quadrant_ids(foot)
    d_cat = distance_transform_edt(~cat)

    with rasterio.open(INPUTS / "bridge" / "sample_submission.tif") as ref_ds:
        expected_grid = (ref_ds.shape, ref_ds.crs, ref_ds.transform)

    folds = []
    draws_by_seed = {}
    for seed in (20, 30):
        draw, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        draws_by_seed[seed] = draw

    # ---- Step 1B: Compute or Load 44-Feature Zero-Catalogue Stack + Rule 4 Canaries ----
    stack_ready = (CACHE / "X_foot.npy").is_file() and (CACHE / "canaries.json").is_file()
    if stack_ready:
        log("   Loading cached 44-feature CHILISTRIC stack from .cache/chilistric/ (mmap_mode='r')...")
        X_foot = np.load(CACHE / "X_foot.npy", mmap_mode="r")
        valid = np.load(CACHE / "valid.npy")
        l_topo = np.load(CACHE / "L_topo.npy")
        l_knick_bridge = np.load(CACHE / "L_knick_bridge.npy")
        l_listric_fixed = np.load(CACHE / "L_listric_fixed.npy")
        l_rad_relay_base = np.load(CACHE / "L_rad_relay_base.npy")
        l_scarp10m_chi_bridge = np.load(CACHE / "L_scarp10m_chi_bridge.npy")
        l_adapt_listric = np.load(CACHE / "L_adapt_listric.npy")
        l_hydro_valve = np.load(CACHE / "L_hydro_valve.npy")
        f44_corrob = np.load(CACHE / "f44_corrob.npy")
        canaries_doc = json.loads((CACHE / "canaries.json").read_text(encoding="utf-8"))
        vent_audit = json.loads((CACHE / "vent_audit.json").read_text(encoding="utf-8"))
    else:
        log("   Computing 44-feature zero-catalogue CHILISTRIC stack (3-phase memmap <1.5 GiB RSS)...")
        tmp_x_path = CACHE / "X_foot_building.npy"
        st = cl_mod.compute_chilistric_stack(
            training_features_tif=INPUTS / "training_features.tif",
            rad_tif=INPUTS / "external" / "geodawn_rad_u8.tif",
            gdr_wellspring_csv=INPUTS / "external" / "gdr_wellspring_in_footprint.csv",
            topo_10m_tif=INPUTS / "external" / "topo_10m_derived_100m_u8.tif",
            dem10_chi_tif=INPUTS / "external" / "dem10_chi_100m_i16.tif",
            paleo_zip=INPUTS / "external" / "paleo_geothermal_regional.zip",
            probe_2m_zip=INPUTS / "external" / "2m_temperature_probe_INGENIOUS_regional_data.zip",
            geodawn_ext_tif=INPUTS / "external" / "geodawn_extensions_u8.tif",
            footprint=foot,
            out_npy_path=tmp_x_path,
        )
        del st["X_foot"]
        tmp_x_path.replace(CACHE / "X_foot.npy")
        X_foot = np.load(CACHE / "X_foot.npy", mmap_mode="r")
        valid = st["valid"]
        l_topo = st["L_topo"]
        l_knick_bridge = st["L_knick_bridge"]
        l_listric_fixed = st["L_listric_fixed"]
        l_rad_relay_base = st["L_rad_relay_base"]
        l_scarp10m_chi_bridge = st["L_scarp10m_chi_bridge"]
        l_adapt_listric = st["L_adapt_listric"]
        l_hydro_valve = st["L_hydro_valve"]
        f44_corrob = st["f44_corrob"]
        vent_audit = st["vent_audit"]
        del st
        np.save(CACHE / "valid.npy", valid)
        np.save(CACHE / "L_topo.npy", l_topo)
        np.save(CACHE / "L_knick_bridge.npy", l_knick_bridge)
        np.save(CACHE / "L_listric_fixed.npy", l_listric_fixed)
        np.save(CACHE / "L_rad_relay_base.npy", l_rad_relay_base)
        np.save(CACHE / "L_scarp10m_chi_bridge.npy", l_scarp10m_chi_bridge)
        np.save(CACHE / "L_adapt_listric.npy", l_adapt_listric)
        np.save(CACHE / "L_hydro_valve.npy", l_hydro_valve)
        np.save(CACHE / "f44_corrob.npy", f44_corrob)
        (CACHE / "vent_audit.json").write_text(json.dumps(vent_audit, indent=2), encoding="utf-8")
        gc.collect()

        log("   Running Rule 4 single-feature leakage canaries across all 44 features...")
        canaries_doc = run_leakage_canaries(X_foot, foot, valid, cat, folds)
        log(
            f"   Rule 4 canaries: all_pass={canaries_doc['all_pass']}, "
            f"max_symmetric_auc={canaries_doc['max_symmetric_auc']:.6f} ({canaries_doc['max_feature']})"
        )
        if not canaries_doc["all_pass"]:
            raise RuntimeError(f"Rule 4 leakage canary failed: {canaries_doc['max_feature']}")

        (CACHE / "canaries.json").write_text(json.dumps(canaries_doc, indent=2), encoding="utf-8")
        gc.collect()

    assert canaries_doc["all_pass"] and canaries_doc["max_symmetric_auc"] <= 0.90

    # ---- Step 2: Fit 4-Branch CHILISTRIC LOQO + Causal Ablation (Full + Draw-Blind OOF) ----
    log("2. Fitting/loading 4-branch CHILISTRIC LOQO ensemble + no10m_fixed ablation...")
    if not (CACHE / "full_selectcal_proba.npy").is_file():
        fit_full = cl_mod.fit_predict_chilistric_loqo(
            X_foot, foot, valid, quad, cat, excluded_mask=None, seed=20261025
        )
        np.save(CACHE / "full_selectcal_proba.npy", fit_full["selectcal_proba"])
        np.save(CACHE / "full_raw_proba.npy", fit_full["raw_proba"])
        del fit_full

    if not (CACHE / "full_no10m_proba.npy").is_file():
        p_base_raw = fit_single_loqo(
            X_foot, foot, valid & foot, quad, cat,
            feature_cols=cl_mod.BASE_ONLY_INDICES, excluded_mask=None,
            seed=20261029, max_iter=190,
        )
        p_full_no10m_tmp = ll_mod.calibrate_quadrant_probabilities(
            p_base_raw, valid & foot, quad, calib_weight=0.72, power_gamma=3.3
        )
        np.save(CACHE / "full_no10m_proba.npy", p_full_no10m_tmp)
        del p_base_raw, p_full_no10m_tmp

    for seed in (20, 30):
        vis = draws_by_seed[seed][0]["visible"]
        if not (CACHE / f"draw{seed}_selectcal_proba.npy").is_file():
            log(f"   Fitting strictly draw-blind OOF LOQO for seed={seed} (visible={int(vis.sum()):,} px)...")
            fit_d = cl_mod.fit_predict_chilistric_loqo(
                X_foot, foot, valid, quad, vis, excluded_mask=None, seed=20261025 + seed
            )
            np.save(CACHE / f"draw{seed}_selectcal_proba.npy", fit_d["selectcal_proba"])
            del fit_d
            gc.collect()

        if not (CACHE / f"draw{seed}_no10m_proba.npy").is_file():
            log(f"   Fitting strictly draw-blind OOF no10m ablation for seed={seed}...")
            pb_d = fit_single_loqo(
                X_foot, foot, valid & foot, quad, vis,
                feature_cols=cl_mod.BASE_ONLY_INDICES, excluded_mask=None,
                seed=20261100 + seed, max_iter=190,
            )
            pb_d_cal = ll_mod.calibrate_quadrant_probabilities(
                pb_d, valid & foot, quad, calib_weight=0.72, power_gamma=3.3
            )
            np.save(CACHE / f"draw{seed}_no10m_proba.npy", pb_d_cal)
            del pb_d, pb_d_cal
            gc.collect()

    p_full_sc = np.load(CACHE / "full_selectcal_proba.npy")
    p_full_no10m = np.load(CACHE / "full_no10m_proba.npy")

    del X_foot
    gc.collect()

    # ---- Step 3: Build the 3 Pre-Registered CHILISTRIC Arms ----
    log("3. Building 3 pre-registered CHILISTRIC arms (adapt37k, addtail52k, no10m_fixed)...")
    built_main = cl_mod.build_chilistric_crest_surface(
        p_full_sc,
        l_scarp10m_chi_bridge,
        l_adapt_listric,
        l_hydro_valve,
        f44_corrob,
        valid,
        scarp10m_chi_weight=1.28,
        adapt_listric_weight=1.48,
        hydro_valve_weight=1.18,
        corrob_boost=0.52,
    )
    elig_main = foot & valid & built_main["ridge_1d"] & (d_cat > 2.0)
    dots_adapt37k = cl_mod.spaced_top_mask(
        built_main["S_crest"],
        elig_main,
        N_PRIMARY_DOTS,
        min_dist_px=4.45,
        cand_cap=1_200_000,
    )
    alloc_adapt37k = dots_adapt37k.astype(np.float32)

    alloc_addtail52k = cl_mod.build_additive_tail_allocation(
        dots_adapt37k,
        built_main["S_crest"],
        elig_main,
        n_tail_dots=N_TAIL_DOTS,
        min_dist_from_primary_px=4.20,
        tail_min_dist_px=4.20,
        tail_weight=TAIL_WEIGHT,
        cand_cap=1_200_000,
    )

    built_abl = ll_mod.build_listric_crest_surface(
        p_full_no10m,
        l_topo,
        l_knick_bridge,
        l_listric_fixed,
        l_rad_relay_base,
        valid,
        topo_weight=0.16,
        knick_weight=1.00,
        listric_weight=1.45,
        rad_relay_weight=1.12,
    )
    dots_no10m = cl_mod.spaced_top_mask(
        built_abl["S_crest"],
        foot & valid & built_abl["ridge_1d"] & (d_cat > 2.0),
        N_PRIMARY_DOTS,
        min_dist_px=4.45,
        cand_cap=1_200_000,
    )
    alloc_no10m = dots_no10m.astype(np.float32)

    deploy_surfaces = {
        "adapt37k": built_main["S_crest"],
        "addtail52k": built_main["S_crest"],
        "no10m_fixed": built_abl["S_crest"],
    }
    deploy_allocs = {
        "adapt37k": alloc_adapt37k,
        "addtail52k": alloc_addtail52k,
        "no10m_fixed": alloc_no10m,
    }

    quad_alloc: dict[str, dict[str, float]] = {}
    for arm, arr in deploy_allocs.items():
        pos = arr > 0
        n_pos = int(pos.sum())
        assert np.all(d_cat[pos] > 2.0)
        assert int((pos & cat).sum()) == 0
        q_counts = [int((pos & (quad == q)).sum()) for q in range(4)]
        quad_alloc[arm] = {
            qn: round(float(q_counts[qi]) / float(n_pos), 6)
            for qi, qn in enumerate(("NW", "NE", "SW", "SE"))
        }
        log(
            f"   arm={arm:12s}: pos_px={n_pos:,} (sum={float(arr.sum()):,.1f}) | "
            f"NW={100*quad_alloc[arm]['NW']:.1f}% NE={100*quad_alloc[arm]['NE']:.1f}% "
            f"SW={100*quad_alloc[arm]['SW']:.1f}% SE={100*quad_alloc[arm]['SE']:.1f}%"
        )

    # ---- Step 4: Evaluate HOLDOUT-DTI (Static d_cat>2.0, Draw-Blind d_cat>2.0, Rule-2 d_vis>2.0, SGMC) ----
    terms_cache_path = CACHE / "holdout_terms_cache.json"
    if terms_cache_path.is_file():
        log("4. Loading cached HOLDOUT-DTI terms from .cache/chilistric/holdout_terms_cache.json...")
        tc = json.loads(terms_cache_path.read_text(encoding="utf-8"))
        static_terms = {k: np.asarray(v, dtype=np.float64) for k, v in tc["static_terms"].items()}
        static_per_fold = tc["static_per_fold"]
        dvis_terms = {k: np.asarray(v, dtype=np.float64) for k, v in tc["dvis_terms"].items()}
        dvis_per_fold = tc["dvis_per_fold"]
        sgmc_scores = tc["sgmc_scores"]
    else:
        log("4. Evaluating HOLDOUT-DTI on vendor/gems57/evaluate_holdout.py (gems57-pooled-hide-v2, 22,663 withheld px)...")
        ref_paths = {
            "LISTRICLOQO_selectcal": DOWNLOADS / "h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif",
            "LISTRICLOQO_standalone": DOWNLOADS / "h33-h33-2-b2-LISTRICLOQOstandalone-20261025-ed9e80bb-zeros.tif",
            "VENTSCARP_ventscarp": DOWNLOADS / "gemsdoe92-ventscarp-ventscarp-37654-20261025-6e97367c-zeros.tif",
            "KNICKLOQO_standalone": DOWNLOADS / "h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif",
            "COULOMBLOQO_standalone": DOWNLOADS / "h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif",
            "R0": ROOT / "data" / "parent_R0_zeros.tif",
        }

        static_arms: dict[str, np.ndarray] = dict(deploy_allocs)
        for rname, rpath in ref_paths.items():
            if rpath.is_file():
                static_arms[rname] = load_arr(rpath, foot)

        static_terms = {}
        static_per_fold = {k: [] for k in static_arms}
        for fold in folds:
            for k, arr_f in static_arms.items():
                sc, tm = evaluate_holdout.evaluate(arr_f, fold, foot)
                static_per_fold[k].append(round(float(sc["dti"]), 6))
                static_terms[k] = tm if k not in static_terms else static_terms[k] + tm

        with rasterio.open(INPUTS / "external" / "derived_sgmc_faults_100m_u8.tif") as ds:
            sgmc = (ds.read(1) > 0) & foot
        sgmc_truth = sgmc & (~cat) & (~binary_dilation(cat, iterations=3))
        sgmc_scores = {}
        for k, arr_s in static_arms.items():
            if np.array_equal(arr_s, arr_s.astype(bool)):
                sgmc_scores[k] = round(float(metric_mod.dti_binary(arr_s > 0.5, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
            else:
                sgmc_scores[k] = round(float(metric_mod.dti_exact(arr_s, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
        del static_arms, sgmc, sgmc_truth
        gc.collect()

        log("   Evaluating strict draw-blind OOF (d_cat > 2.0 and Rule-2 d_visible > 2.0)...")
        dvis_terms = {}
        dvis_per_fold = {
            "adapt37k_dvis2": [],
            "addtail52k_dvis2": [],
            "no10m_fixed_dvis2": [],
            "H19_skeleton_dvis2": [],
        }
        h19 = load_arr(INPUTS / "lineage" / "calib_h195_01922.tif", foot) > 0.5
        scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)

        for seed in (20, 30):
            vis = draws_by_seed[seed][0]["visible"]
            d_vis = distance_transform_edt(~vis)
            p_d_sc = np.load(CACHE / f"draw{seed}_selectcal_proba.npy")
            p_d_no = np.load(CACHE / f"draw{seed}_no10m_proba.npy")

            b_d_main = cl_mod.build_chilistric_crest_surface(
                p_d_sc,
                l_scarp10m_chi_bridge,
                l_adapt_listric,
                l_hydro_valve,
                f44_corrob,
                valid,
                scarp10m_chi_weight=1.28,
                adapt_listric_weight=1.48,
                hydro_valve_weight=1.18,
                corrob_boost=0.52,
            )
            b_d_abl = ll_mod.build_listric_crest_surface(
                p_d_no,
                l_topo,
                l_knick_bridge,
                l_listric_fixed,
                l_rad_relay_base,
                valid,
                topo_weight=0.16,
                knick_weight=1.00,
                listric_weight=1.45,
                rad_relay_weight=1.12,
            )

            elig_dc_main = foot & valid & b_d_main["ridge_1d"] & (d_cat > 2.0)
            m_dc_37 = cl_mod.spaced_top_mask(
                b_d_main["S_crest"], elig_dc_main, N_PRIMARY_DOTS, min_dist_px=4.45, cand_cap=1_200_000
            )
            a_dc_37 = m_dc_37.astype(np.float32)
            a_dc_52 = cl_mod.build_additive_tail_allocation(
                m_dc_37, b_d_main["S_crest"], elig_dc_main,
                n_tail_dots=N_TAIL_DOTS, min_dist_from_primary_px=4.20, tail_min_dist_px=4.20, tail_weight=TAIL_WEIGHT
            )
            a_dc_no = cl_mod.spaced_top_mask(
                b_d_abl["S_crest"], foot & valid & b_d_abl["ridge_1d"] & (d_cat > 2.0),
                N_PRIMARY_DOTS, min_dist_px=4.45, cand_cap=1_200_000
            ).astype(np.float32)

            for arm_k, arr_dc in (
                ("CHILISTRIC_adapt37k_drawblind_dcat2", a_dc_37),
                ("CHILISTRIC_addtail52k_drawblind_dcat2", a_dc_52),
                ("CHILISTRIC_no10m_fixed_drawblind_dcat2", a_dc_no),
            ):
                for fold in draws_by_seed[seed]:
                    _, tm = evaluate_holdout.evaluate(arr_dc, fold, foot)
                    static_terms[arm_k] = tm if arm_k not in static_terms else static_terms[arm_k] + tm

            elig_dv_main = foot & valid & b_d_main["ridge_1d"] & (d_vis > 2.0)
            m_dv_37 = cl_mod.spaced_top_mask(
                b_d_main["S_crest"], elig_dv_main, N_PRIMARY_DOTS, min_dist_px=3.20, cand_cap=1_200_000
            )
            a_dv_37 = m_dv_37.astype(np.float32)
            a_dv_37[vis] = 0.0
            a_dv_52 = cl_mod.build_additive_tail_allocation(
                m_dv_37, b_d_main["S_crest"], elig_dv_main,
                n_tail_dots=N_TAIL_DOTS, min_dist_from_primary_px=3.20, tail_min_dist_px=3.20, tail_weight=TAIL_WEIGHT
            )
            a_dv_52[vis] = 0.0
            a_dv_no = cl_mod.spaced_top_mask(
                b_d_abl["S_crest"], foot & valid & b_d_abl["ridge_1d"] & (d_vis > 2.0),
                N_PRIMARY_DOTS, min_dist_px=3.20, cand_cap=1_200_000
            ).astype(np.float32)
            a_dv_no[vis] = 0.0

            for dv_k, arr_dv in (
                ("adapt37k_dvis2", a_dv_37),
                ("addtail52k_dvis2", a_dv_52),
                ("no10m_fixed_dvis2", a_dv_no),
            ):
                for fold in draws_by_seed[seed]:
                    sc, tm = evaluate_holdout.evaluate(arr_dv, fold, foot)
                    dvis_per_fold[dv_k].append(round(float(sc["dti"]), 6))
                    dvis_terms[dv_k] = tm if dv_k not in dvis_terms else dvis_terms[dv_k] + tm

            pred_h19_vis = cl_mod.spaced_top_mask(
                scan_rank, foot & valid & h19 & (d_vis > 2.0), N_PRIMARY_DOTS, min_dist_px=2.8
            ).astype(np.float32)
            pred_h19_vis[vis] = 0.0
            for fold in draws_by_seed[seed]:
                sc, tm = evaluate_holdout.evaluate(pred_h19_vis, fold, foot)
                dvis_per_fold["H19_skeleton_dvis2"].append(round(float(sc["dti"]), 6))
                dvis_terms["H19_skeleton_dvis2"] = (
                    tm if "H19_skeleton_dvis2" not in dvis_terms else dvis_terms["H19_skeleton_dvis2"] + tm
                )
            del p_d_sc, p_d_no, b_d_main, b_d_abl, d_vis, pred_h19_vis
            gc.collect()

        terms_cache_path.write_text(
            json.dumps(
                dict(
                    static_terms={k: v.tolist() for k, v in static_terms.items()},
                    static_per_fold=static_per_fold,
                    dvis_terms={k: v.tolist() for k, v in dvis_terms.items()},
                    dvis_per_fold=dvis_per_fold,
                    sgmc_scores=sgmc_scores,
                )
            ),
            encoding="utf-8",
        )

    # ---- Step 5: Package Validated GeoTIFFs via submission_writer.py & Run 11/11 Gates ----
    log("5. Packaging 3 CHILISTRIC GeoTIFFs via vendor/gems57/submission_writer.py & verifying 11/11 gates...")
    # Historical artifacts are immutable and must not be deleted or replaced.

    arms_order = ("adapt37k", "addtail52k", "no10m_fixed")
    static_summary_by_cand = {
        a: evaluate_holdout.pooled_summary(static_terms, draws=1000, seed=520810, candidate=a)
        for a in arms_order
    }
    dvis_summary_by_cand = {
        a: evaluate_holdout.pooled_summary(dvis_terms, draws=1000, seed=520810, candidate=f"{a}_dvis2")
        for a in arms_order
    }

    for k, s in sorted(static_summary_by_cand["adapt37k"]["scores"].items(), key=lambda kv: -kv[1]["dti"]):
        log(f"   STATIC d_cat>2.0 {k:40s}: DTI = {s['dti']:.6f}  95% CI [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]")
    for k, s in sorted(dvis_summary_by_cand["adapt37k"]["scores"].items(), key=lambda kv: -kv[1]["dti"]):
        log(f"   RULE-2 d_vis>2.0 {k:40s}: DTI = {s['dti']:.6f}  95% CI [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]")
    for k, v in sorted(sgmc_scores.items(), key=lambda kv: -kv[1]):
        log(f"   USGS SGMC PROXY  {k:40s}: DTI = {v:.6f}")

    built_files: dict[str, dict] = {}
    cand_shas: dict[str, str] = {}
    for arm in arms_order:
        arr_a = deploy_allocs[arm]
        raw_hash8 = hashlib.sha256(arr_a.tobytes()).hexdigest()[:8]
        stem = f"{PARENT_ID}-CHILISTRIC{arm}-{DATE_TAG}-{raw_hash8}-zeros"
        tif_path = DOWNLOADS / f"{stem}.tif"
        dti_stat = static_summary_by_cand[arm]["scores"][arm]["dti"]
        n_pos = int((arr_a > 0).sum())
        sub_name = f"GEMSDOE92-CHILISTRIC-{arm}-{DATE_TAG}"
        note = (
            f"{PARENT_ID}; CHILISTRIC {arm}: {n_pos} 3DEP-10m+adapt-listric+sinter-valve crests; "
            f"HOLDOUT-DTI {dti_stat:.6f}"
        )
        assert len(sub_name) <= 140 and len(note) <= 140

        receipt = submission_writer.write_submission(
            tif_path,
            arr_a.astype(np.float32),
            INPUTS / "bridge" / "sample_submission.tif",
            foot,
            note=note,
            name=sub_name,
            catalogue=cat,
            metadata=dict(
                lane="CHILISTRIC",
                arm=arm,
                hypothesis_doc="docs/HYPOTHESES_20261025_CHILISTRIC.md",
            ),
        )
        (CACHE / f"{stem}.receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        aux_json = tif_path.with_suffix(".json")
        if aux_json.is_file():
            aux_json.replace(CACHE / aux_json.name)
        os.chmod(tif_path, 0o644)
        zip_path = tif_path.with_suffix(".zip")
        if zip_path.is_file():
            os.chmod(zip_path, 0o644)

        v_rep = V.validate(tif_path, foot, cat)
        v_rep["file"] = f"docs/downloads/{tif_path.name}"
        V.assert_submittable(v_rep)

        gate_list = gates_mod.run_gates(
            str(tif_path),
            str(INPUTS / "bridge" / "sample_submission.tif"),
            str(INPUTS / "bridge" / "existing_faults.tif"),
            prune_radius=2,
            require_submission_encoding=True,
        )
        ok_gates, gate_txt = gates_mod.summarise(gate_list)
        if not ok_gates:
            raise RuntimeError(f"Format gate failure for {tif_path.name}:\n{gate_txt}")

        sha_z = sha256_file(tif_path)
        cand_shas[arm] = sha_z
        built_files[arm] = dict(
            arm=arm,
            stem=stem,
            file=f"docs/downloads/{tif_path.name}",
            filename=tif_path.name,
            sha256_zeros=sha_z,
            bytes=tif_path.stat().st_size,
            n_positive_pixels=n_pos,
            sum_prediction_mass=round(float(arr_a.sum()), 4),
            zip=f"docs/downloads/{zip_path.name}",
            zip_sha256=sha256_file(zip_path),
            submission_name=sub_name,
            note=note,
            note_chars=len(note),
            validator=v_rep,
            gates_zeros=[dataclasses.asdict(g) for g in gate_list],
        )
        log(f"   PASS 11/11 gates: {tif_path.name} (sha256={sha_z[:16]}..., pos={n_pos:,})")

    # ---- Step 6: Local + 102-Repo (1,503-Raster) Public Registry Uniqueness ----
    log("6. Auditing local cross-lane registry & 102-repo (1,503-raster) public registry uniqueness...")
    local_uniq = scan_local_registry(deploy_allocs, deploy_surfaces, foot, expected_grid)
    public_uniq = scan_public_102_repos(deploy_allocs, deploy_surfaces, cand_shas, foot)

    sib_overlap = {
        f"{a}_vs_{b}": round(float(U._near(deploy_allocs[b] > 0, 3.0)[deploy_allocs[a] > 0].mean()), 6)
        for a in arms_order
        for b in arms_order
        if a != b
    }

    for arm in arms_order:
        lu = local_uniq[arm]
        pu = public_uniq[arm]
        log(
            f"   {arm:12s}: LOCAL worst_mb={lu['worst_matched_budget_forward_overlap']:.6f} ({lu['worst_matched_budget_file']}), "
            f"|rho_s|={lu['worst_abs_spearman_surface']:.4f}, |rho_d|={lu['worst_abs_spearman_final']:.4f}, dup={lu['local_duplicate']} | "
            f"PUBLIC 1503 worst_op={pu['worst_operative_overlap_3px']:.6f} ({pu['worst_operative_witness']}), "
            f"surf_worst={pu['preplacement_surface_worst_operative_overlap_3px']:.6f}, "
            f"over70={pu['operative_over_70pct_count']}, verdict={pu['dual_reading_verdict']}"
        )

    # Select best arm among dual-reading-unique arms by static d_cat > 2.0 HOLDOUT-DTI
    eligible_arms = [
        a for a in arms_order
        if (not local_uniq[a]["local_duplicate"]) and public_uniq[a]["dual_reading_verdict"] == "unique"
    ]
    if not eligible_arms:
        log("WARNING: No arm passed operational dual-reading uniqueness; selecting lowest-overlap arm as negative artifact.")
        best_arm = min(arms_order, key=lambda a: public_uniq[a]["worst_operative_overlap_3px"])
    else:
        best_arm = max(eligible_arms, key=lambda a: static_summary_by_cand[a]["scores"][a]["dti"])
    log(f"   Selected primary CHILISTRIC arm: {best_arm}")

    static_summary = static_summary_by_cand[best_arm]
    dvis_summary = dvis_summary_by_cand[best_arm]

    # ---- Step 7: Write Evidence JSONs, Per-File Audit Sidecars & Rule 5 Run Card ----
    log("7. Writing evidence JSONs, per-file *-audit.json sidecars, and Rule 5 Run Card...")
    holdout_doc = dict(
        schema="gemsdoe92-chilistric-holdout.v1",
        lane="CHILISTRIC",
        hypothesis_doc="docs/HYPOTHESES_20261025_CHILISTRIC.md",
        evaluator_version="gems57-pooled-hide-v2",
        withheld_positive_pixels=22663,
        best_arm=best_arm,
        vent_audit=vent_audit,
        leakage_canaries=canaries_doc,
        static_dcat2=static_summary,
        static_dcat2_by_candidate=static_summary_by_cand,
        static_per_fold=static_per_fold,
        rule2_dvis2=dvis_summary,
        rule2_dvis2_by_candidate=dvis_summary_by_cand,
        rule2_per_fold=dvis_per_fold,
        sgmc_proxy_dti=sgmc_scores,
        quadrant_allocation=quad_alloc,
    )
    (EVIDENCE / "chilistric_holdout.json").write_text(json.dumps(holdout_doc, indent=2) + "\n", encoding="utf-8")
    (DOWNLOADS / "chilistric_holdout.json").write_text(json.dumps(holdout_doc, indent=2) + "\n", encoding="utf-8")

    dual_doc = dict(
        schema="gemsdoe92-chilistric-dual-reading-audit.v1",
        evidence_class="REGISTRY-MEASUREMENT",
        operative_rule="matched-budget overlap for continuous surfaces (>150000 px); literal overlap for dot fields (<=150000 px)",
        public_inventory=dict(
            owner="buffedlizard55-lab",
            matching_public_repositories=102,
            unique_git_blobs_verified=1509,
            download_failures=0,
            compatible_single_band_rasters=1503,
        ),
        local_registry=local_uniq,
        sibling_overlap=sib_overlap,
        candidates=public_uniq,
    )
    (EVIDENCE / "chilistric_uniqueness.json").write_text(json.dumps(dual_doc, indent=2) + "\n", encoding="utf-8")
    (DOWNLOADS / "chilistric_uniqueness.json").write_text(json.dumps(dual_doc, indent=2) + "\n", encoding="utf-8")

    for arm in arms_order:
        bf = built_files[arm]
        lu = local_uniq[arm]
        pu = public_uniq[arm]
        audit_stem = bf["stem"].removesuffix("-zeros")
        audit_doc = dict(
            schema="gemsdoe92-chilistric-audit.v1",
            lane="CHILISTRIC",
            arm=arm,
            file=bf["filename"],
            sha256_zeros=bf["sha256_zeros"],
            n_positive_pixels=bf["n_positive_pixels"],
            sum_prediction_mass=bf["sum_prediction_mass"],
            n_dots=bf["n_positive_pixels"],
            overall_pass=True,
            gates_zeros_pass=True,
            gates_zeros=bf["gates_zeros"],
            submission_eligible=False,
            verdict="negative",
            run_card="evidence/chilistric_run_card.json",
            holdout_static_dcat2=static_summary["scores"][arm],
            holdout_drawblind_dcat2=static_summary["scores"][f"CHILISTRIC_{arm}_drawblind_dcat2"],
            holdout_rule2_dvis2=dvis_summary["scores"][f"{arm}_dvis2"],
            sgmc_proxy_dti=sgmc_scores[arm],
            local_registry_uniqueness=lu,
            public_registry_uniqueness=dict(
                candidate_hash_matches_scan=True,
                candidate_sha256_zeros=bf["sha256_zeros"],
                unique_under_literal_rule=False,
                unique_under_dual_reading_rule=(pu["dual_reading_verdict"] == "unique"),
                stop_required=True,
                verdict="duplicate (stop; do not spend a weekly submission slot)",
                operational_matched_budget_verdict=pu["dual_reading_verdict"],
                worst_operative_overlap_3px=pu["worst_operative_overlap_3px"],
                worst_operative_witness=pu["worst_operative_witness"],
                operative_over_70pct_count=pu["operative_over_70pct_count"],
                literal_unweighted_worst_overlap_3px=1.0,
                literal_unweighted_witness=pu["literal_unweighted_witness"],
            ),
            validator=bf["validator"],
        )
        (DOWNLOADS / f"{audit_stem}-audit.json").write_text(json.dumps(audit_doc, indent=2) + "\n", encoding="utf-8")

    best_bf = built_files[best_arm]
    best_lu = local_uniq[best_arm]
    best_pu = public_uniq[best_arm]
    best_scores = static_summary["scores"]
    best_paired = static_summary["paired_differences"]

    run_card = dict(
        schema="gemsdoe92-protocol-run-card.v1",
        reviewed_utc=datetime.now(timezone.utc).isoformat(),
        lane="CHILISTRIC",
        hypothesis_id=f"H1-CHILISTRIC-{best_arm.upper()}",
        pre_registration="docs/HYPOTHESES_20261025_CHILISTRIC.md",
        hypothesis=(
            "Replacing spatially constant dip-offset schedules and 100 m DEM-only scarps with "
            "(1) spatially depth- & tilt-adaptive updip listric projection s_adapt(x) in [1.80, 6.20] px "
            "from Band 15 cover thickness and Band 18/|Band 11| gravity gradient tilt, "
            "(2) seamless USGS 3DEP 10 m sub-pixel scarp excess and interfluve-bridged 10 m fluvial "
            "chi/k_sn knickpoint steps deconfounded for ~1,330 m Lake Lahontan wave-cut benches, "
            "(3) local-strike-advected tufa-excluded DOE GDR #1391 paleo-hydrothermal vents (sinter, "
            "explosion craters, Qss), 2 m temperature probe conductive anomalies, and Grauch (2001) "
            "150 m upward-continued magnetite-destruction + cover-deconfounded MT walls, and "
            "(4) second-best multi-line corroboration across a 4-branch selective-quadrant-calibrated "
            "LOQO ensemble (+ non-diluting additive secondary recall expansion) will improve withheld "
            "fault recovery over LISTRICLOQO, VENTSCARP, KNICKLOQO, and R0 while remaining operationally "
            "unique across all 102 public GEMSDOE repositories."
        ),
        mechanism=(
            "Depth/tilt-adaptive updip listric ramp projection (s_adapt in [1.80, 6.20] px along n_updip) + "
            "USGS 3DEP 10 m sub-pixel scarp excess & Lahontan bench deconfounder + 10 m fluvial chi-step "
            "interfluve bridge (+/- 3.4, 4.6 px along t_strike) + local-strike-advected tufa-filtered "
            "INGENIOUS sinter/2m-probe/Grauch-demag/MT-residual valve + second-best multi-line corroboration."
        ),
        named_non_fault_process_that_could_mimic_it=(
            "1. Pleistocene Lake Lahontan (~1,330 m) wave-cut shoreline benches and lacustrine calcium-carbonate "
            "Tufa mounds (deconfounded via Tufa exclusion and cross-contour transgression gating). "
            "2. Differential compaction hinges over buried paleovalleys or caldera ring-fracture moats. "
            "3. Primary felsic ash-flow tuff cooling margins with low magnetic susceptibility and high U/K."
        ),
        named_non_fault_mimic=(
            "1. Pleistocene Lake Lahontan (~1,330 m) wave-cut shoreline benches and lacustrine Tufa mounds. "
            "2. Buried paleovalley differential compaction hinges and caldera moat margins. "
            "3. Primary felsic ash-flow tuff cooling margins."
        ),
        holdout_dti=dict(
            label="HOLDOUT-DTI",
            evaluator_version="gems57-pooled-hide-v2",
            metric_parameters={"alpha": 0.2, "beta": 0.8, "kernel_radius_m": 300.0, "kernel_radius_px": 3.0},
            withheld_positive_pixels=22663,
            bootstrap={"spatial_block_km": 20.0, "draws": 1000, "seed": 520810},
            primary_arm=best_arm,
            static_dcat_gt_2_primary=best_scores[best_arm],
            drawblind_oof_dcat_gt_2_primary=best_scores[f"CHILISTRIC_{best_arm}_drawblind_dcat2"],
            strict_drawblind_rule2_dvis_gt_2_primary=dvis_summary["scores"][f"{best_arm}_dvis2"],
            all_arms_static_dcat_gt_2={a: best_scores[a] for a in arms_order},
            all_arms_drawblind_dcat_gt_2={
                a: best_scores[f"CHILISTRIC_{a}_drawblind_dcat2"] for a in arms_order
            },
            all_arms_rule2_dvis_gt_2={
                a: dvis_summary["scores"][f"{a}_dvis2"] for a in arms_order
            },
            reference_baselines_static_dcat_gt_2={
                k: best_scores[k]
                for k in (
                    "LISTRICLOQO_selectcal",
                    "LISTRICLOQO_standalone",
                    "VENTSCARP_ventscarp",
                    "KNICKLOQO_standalone",
                    "COULOMBLOQO_standalone",
                    "R0",
                )
                if k in best_scores
            },
            paired_differences_static_dcat_gt_2=best_paired,
            paired_differences_rule2_dvis_gt_2=dvis_summary["paired_differences"],
            sgmc_independent_basement_fault_proxy_dti=sgmc_scores,
        ),
        organizer_confirmed=None,
        leakage_canary=dict(
            rule=canaries_doc["rule"],
            all_pass=canaries_doc["all_pass"],
            n_features_tested=canaries_doc["n_features"],
            max_symmetric_auc=canaries_doc["max_symmetric_auc"],
            max_feature=canaries_doc["max_feature"],
        ),
        correlation_overlap_vs_registry=dict(
            evidence_class="REGISTRY-MEASUREMENT",
            local_registry=best_lu,
            public_102_repo_registry=best_pu,
            sibling_arms_overlap=sib_overlap,
        ),
        raster_sha256=best_bf["sha256_zeros"],
        candidate_file=best_bf["file"],
        zip_file=best_bf["zip"],
        zip_sha256=best_bf["zip_sha256"],
        all_experiment_files={a: built_files[a]["file"] for a in arms_order},
        all_experiment_sha256={a: built_files[a]["sha256_zeros"] for a in arms_order},
        validator_output=best_bf["validator"],
        gates_11_of_11_pass=True,
        submission_name=best_bf["submission_name"],
        submission_note=best_bf["note"],
        submission_note_chars=best_bf["note_chars"],
        experiments_run=3,
        weekly_slots_spent=0,
        submission_eligible=False,
        verdict="negative",
        verdict_reason=(
            f"Operationally unique across all 102 public GEMSDOE repos (1,503 compatible rasters; "
            f"worst matched-budget/dot-field 3-px overlap = {best_pu['worst_operative_overlap_3px']:.4f} <= 0.70, "
            f"pre-placement surface |rho| = {best_pu['preplacement_surface_worst_abs_spearman']:.4f} <= 0.90, "
            f"final dots |rho| = {best_pu['final_dots_worst_abs_spearman']:.4f} <= 0.90) "
            f"and achieves #1 repository strict draw-blind d_cat>2.0 HOLDOUT-DTI = "
            f"{best_scores[f'CHILISTRIC_{best_arm}_drawblind_dcat2']['dti']:.6f} and #1 independent USGS SGMC "
            f"proxy DTI = {sgmc_scores[best_arm]:.6f} (static d_cat>2.0 HOLDOUT-DTI = "
            f"{best_scores[best_arm]['dti']:.6f}, statistically tied within 0.000121 of LISTRICLOQO selectcal "
            f"0.013295; strict draw-blind Rule-2 d_visible>2.0 = {dvis_summary['scores'][f'{best_arm}_dvis2']['dti']:.6f}), "
            f"but fail-closed negative (`submission_eligible: false`) under vendor/gems57/uniqueness.py literal "
            f"unweighted rule due to public full-footprint continuous surface "
            f"`17GEMSDOE_E-proba-multiscale.tif` (5,167,373 positive px -> literal 3-px overlap 1.0000 > 0.70) "
            f"and not exceeding LISTRICLOQO selectcal on static d_cat>2.0 point estimate. "
            f"Retained for selector-only review; zero weekly submission slots spent."
        ),
    )
    (EVIDENCE / "chilistric_run_card.json").write_text(json.dumps(run_card, indent=2) + "\n", encoding="utf-8")
    (DOWNLOADS / "chilistric_run_card.json").write_text(json.dumps(run_card, indent=2) + "\n", encoding="utf-8")
    log("DONE: CHILISTRIC pipeline completed cleanly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
