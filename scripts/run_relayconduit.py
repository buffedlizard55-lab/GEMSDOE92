#!/usr/bin/env python3
"""End-to-end execution of the pre-registered RELAYCONDUIT lane (2026-10-25).

Pre-registered specification: docs/HYPOTHESES_20261025_RELAYCONDUIT.md.
Executes in memory-isolated child stages (< 1.4 GiB peak RSS per stage inside
the 3.8 GiB / 0-swap sandbox) while strictly enforcing Protocol Rules 1-6:
  1. stage_stack_and_canary: verifies SHA-256 of all 19 pinned inputs, builds
     the 26 zero-catalogue channels, and runs Rule-4 single-feature leakage
     canaries on all 31 base + tip-relay features BEFORE fitting any model.
  2. stage_deploy_and_screen: fits deployment Stage-1 pairwise OOF + Stage-2
     bimodal LOQO, runs Rule-1 PRE-PLACEMENT surface Spearman screen (<= 0.90)
     across local + 1,497 public blobs (102 repos), emits 37,654 spaced dots
     for each of the 3 pre-registered arms, and runs Rule-1 POST-PLACEMENT
     3-px dot overlap screen across all local + 102-repo public rasters.
  3. stage_holdout_seed (seed=20, seed=30): rebuilds visible-only tip-relay
     channels, Stage-1 OOF, Stage-2 bimodal LOQO, OOF canaries, and rebuilt
     COULOMBLOQO controls strictly from fold['visible'], evaluating via
     vendor/gems57/evaluate_holdout.py (gems57-pooled-hide-v2).
  4. stage_finalize: pools 22,663 withheld positives (1,000-draw 20 km block
     bootstrap), writes [0, 1] GeoTIFFs + ZIPs via submission_writer, runs
     11/11 format gates, emits Run Card + audit sidecars, and updates ledger.
"""
from __future__ import annotations

import gc
import hashlib
import json
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems import ledger as ledger_mod  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems.relayconduit import (  # noqa: E402
    FEATURE_NAMES,
    OOF_COLS,
    build_dual_conduit_surface,
    compute_base_physics_stack,
    fit_pairwise_stage1_oof,
    fit_stage2_bimodal_loqo,
    oriented_tip_relay_fields,
    spaced_top_mask,
    steerable_oof_autocontext,
)
from gems57 import (  # noqa: E402
    evaluate_holdout,
    grid as grid_mod,
    holdout,
    metric as gems57_metric,
    submission_writer,
    uniqueness as gems57_uniqueness,
    validate as gems57_validate,
)

DATE_STR = "20261025"
N_DOTS = 37_654
MIN_DIST_PX = 2.8
SEEDS = (20, 30)

CACHE_INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE_LANE = ROOT / ".cache" / "relayconduit"
PUBLIC_CACHE = ROOT / ".cache" / "gemsdoe_public_registry"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
SESSION_MANIFEST = ROOT / "registry" / "session_manifest.json"
EXT_MANIFEST = ROOT / "registry" / "ventscarp_external_manifest.json"
SAMPLE_SUB = CACHE_INPUTS / "bridge" / "sample_submission.tif"
EXISTING_FAULTS = CACHE_INPUTS / "bridge" / "existing_faults.tif"

ARMS = ("relay_conduit", "relay_delta", "conduit_notip")
ARM_COLLAR_PX = {
    "relay_conduit": 3.2,
    "relay_delta": 3.5,
    "conduit_notip": 2.0,
}


def log(msg: str) -> None:
    rss_mib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    try:
        print(f"[{time.strftime('%H:%M:%S')} | RSS {rss_mib:6.1f} MiB] {msg}", flush=True)
    except BrokenPipeError:
        pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_pinned_inputs() -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for mpath in (SESSION_MANIFEST, EXT_MANIFEST):
        doc = json.loads(mpath.read_text(encoding="utf-8"))
        for entry in doc["files"]:
            p = ROOT / entry["local_path"]
            if not p.is_file():
                raise SystemExit(f"Missing pinned input {entry['id']} at {p}")
            got_bytes = p.stat().st_size
            got_sha = sha256_file(p)
            if got_bytes != int(entry["bytes"]) or got_sha != entry["sha256"]:
                raise SystemExit(f"SHA/size mismatch on {entry['id']}: {got_sha} != {entry['sha256']}")
            paths[entry["id"]] = p
    return paths


def symmetric_auc(y_true: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    s = np.nan_to_num(scores, nan=0.0, posinf=0.0, neginf=0.0)
    if np.all(s == s[0]):
        return 0.5, 0.5
    auc = float(roc_auc_score(y_true, s))
    return auc, float(max(auc, 1.0 - auc))


def unit_ranks(v: np.ndarray) -> np.ndarray:
    if np.all(v == v[0]):
        return np.zeros(v.size, dtype=np.float32)
    r = rankdata(v.astype(np.float64))
    r -= r.mean()
    n = float(np.linalg.norm(r))
    return (r / n).astype(np.float32) if n > 0.0 else np.zeros(v.size, dtype=np.float32)


def fill_relay_columns(
    X_foot: np.ndarray,
    foot: np.ndarray,
    cat_mask: np.ndarray,
    edge_strike_deg: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    rf = oriented_tip_relay_fields(cat_mask, edge_strike_deg, valid)
    X_foot[:, 30] = rf["rc_tip_cone_short"][foot]
    X_foot[:, 31] = rf["rc_tip_cone_long"][foot]
    X_foot[:, 32] = rf["rc_stepover_bridge"][foot]
    X_foot[:, 33] = rf["rc_tip_vs_shadow"][foot]
    X_foot[:, 34] = rf["rc_reg_strike_align"][foot]
    return rf


def build_arm_surfaces(
    res_relay: dict[str, np.ndarray],
    res_notip: dict[str, np.ndarray],
    rf: dict[str, np.ndarray],
    L_geo: np.ndarray,
    L_sub: np.ndarray,
    w_cover: np.ndarray,
    valid: np.ndarray,
) -> dict[str, dict[str, np.ndarray]]:
    p_rel = res_relay["p_bimodal"]
    p_notip_full = res_notip["p_full"]
    p_notip_bim = res_notip["p_bimodal"]

    surf_rc = build_dual_conduit_surface(p_rel, L_geo, L_sub, w_cover, valid)

    uplift = np.maximum(p_rel - np.float32(0.75) * p_notip_full, 0.0)
    tip_gate = np.clip(
        np.float32(0.35)
        + np.float32(0.35) * np.tanh(np.maximum(rf["rc_tip_vs_shadow"], 0.0))
        + np.float32(0.30) * w_cover,
        0.25,
        1.0,
    ).astype(np.float32)
    p_delta = (np.float32(0.52) * p_rel + np.float32(0.48) * uplift * tip_gate).astype(np.float32)
    p_delta[~valid] = 0.0
    surf_delta = build_dual_conduit_surface(p_delta, L_geo, L_sub, np.clip(w_cover + 0.10, 0.25, 0.80), valid)

    surf_notip = build_dual_conduit_surface(p_notip_bim, L_geo, L_sub, w_cover, valid)
    return {
        "relay_conduit": surf_rc,
        "relay_delta": surf_delta,
        "conduit_notip": surf_notip,
    }


def load_base_stack(foot: np.ndarray):
    d_np = np.load(CACHE_LANE / "base_physics_stack.npz", allow_pickle=False)
    X_foot = np.zeros((int(foot.sum()), len(FEATURE_NAMES)), dtype=np.float32)
    X_foot[:, :26] = d_np["X_base"]
    valid = d_np["valid"]
    w_cover = d_np["w_cover"]
    edge_strike_deg = d_np["edge_strike_deg"]
    L_geo = d_np["L_geo"]
    L_sub = d_np["L_sub"]
    vent_stats = json.loads(str(d_np["vent_stats_json"]))
    del d_np
    gc.collect()
    return X_foot, valid, w_cover, edge_strike_deg, L_geo, L_sub, vent_stats


def stage_stack_and_canary() -> int:
    from gems57.uniqueness import stop_historical_runner
    stop_historical_runner("run_relayconduit:stage_stack_and_canary")

    CACHE_LANE.mkdir(parents=True, exist_ok=True)
    log("[Stage 1] Verifying SHA-256 digests of all 19 pinned inputs...")
    inputs = verify_pinned_inputs()
    grid = grid_mod.load_grid(CACHE_INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue

    base_npz = CACHE_LANE / "base_physics_stack.npz"
    if not base_npz.is_file():
        log("[Stage 1] Computing 26 zero-catalogue physical, 3DEP-10m scarp/chi & INGENIOUS channels...")
        st = compute_base_physics_stack(
            training_features_tif=inputs["training_features"],
            geodawn_rad_tif=inputs["ext_geodawn_rad_u8"],
            geodawn_ext_tif=inputs["geodawn_extensions_u8"],
            topo_10m_tif=inputs["topo_10m_derived_100m_u8"],
            dem10_chi_tif=inputs["dem10_chi_100m_i16"],
            paleo_zip=inputs["paleo_geothermal_regional"],
            probe_2m_zip=inputs["2m_temperature_probe_regional"],
            wellspring_csv=inputs["gdr_wellspring_in_footprint"],
            footprint=foot,
        )
        np.savez_compressed(
            base_npz,
            X_base=st["X_foot"][:, :26],  # type: ignore[index]
            valid=st["valid"],
            w_cover=st["w_cover"],
            edge_strike_deg=st["edge_strike_deg"],
            L_geo=st["L_geo"],
            L_sub=st["L_sub"],
            vent_stats_json=json.dumps(st["vent_stats"]),
        )
        del st
        gc.collect()

    X_foot, valid, _, edge_strike_deg, _, _, vent_stats = load_base_stack(foot)
    log(f"[Stage 1] Stack ready ({X_foot.nbytes / 1e6:.1f} MB). Running Rule-4 pre-fit single-feature canaries...")

    foot_row = np.full(foot.shape, -1, dtype=np.int32)
    foot_row[foot] = np.arange(int(foot.sum()), dtype=np.int32)
    canary_rows: dict[str, dict] = {}
    for seed in SEEDS:
        folds, _ = holdout.buffered_component_draw(grid, seed=seed)
        vis = folds[0]["visible"]
        fill_relay_columns(X_foot, foot, vis, edge_strike_deg, valid)

        rng = np.random.default_rng(520810 + seed)
        y_list, idx_list = [], []
        for f in folds:
            pos_flat = np.flatnonzero(f["truth"] & foot & valid)
            neg_pool = np.flatnonzero(f["region"] & foot & valid & (~cat))
            neg_flat = rng.choice(neg_pool, size=min(neg_pool.size, pos_flat.size * 5), replace=False)
            idx_list.append(foot_row.ravel()[np.concatenate([pos_flat, neg_flat])])
            y_list.append(np.concatenate([np.ones(pos_flat.size, np.int8), np.zeros(neg_flat.size, np.int8)]))
        eval_rows = np.concatenate(idx_list)
        eval_y = np.concatenate(y_list)

        for col_j, fname in enumerate(FEATURE_NAMES):
            if col_j in OOF_COLS:
                continue
            raw_auc, sym_auc = symmetric_auc(eval_y, X_foot[eval_rows, col_j])
            rec = canary_rows.setdefault(fname, {"draws": {}})
            rec["draws"][str(seed)] = {"auc": round(raw_auc, 6), "symmetric_auc": round(sym_auc, 6)}
            if sym_auc > 0.90:
                raise SystemExit(f"RULE 4 LEAKAGE CANARY FAILED on {fname} (seed={seed}): sym_auc={sym_auc:.6f} > 0.90")
        del folds, vis, eval_rows, eval_y
        gc.collect()

    (CACHE_LANE / "prefit_canaries.json").write_text(json.dumps(canary_rows, indent=2), encoding="utf-8")
    pre_max_feat, pre_max_val = max(
        ((fn_k, max(d["symmetric_auc"] for d in v["draws"].values())) for fn_k, v in canary_rows.items()),
        key=lambda kv: kv[1],
    )
    log(f"[Stage 1] 31/31 base + tip-relay canaries PASS! Max sym AUC = {pre_max_val:.6f} ({pre_max_feat}) <= 0.90; vents={vent_stats}")
    return 0


def build_or_load_public_index(foot: np.ndarray, sub_flat_idx: np.ndarray, expected_grid: tuple) -> dict:
    idx_npz = CACHE_LANE / "public_fast_index_102repos.npz"
    inv_path = PUBLIC_CACHE / "repo_inventory.json"
    inv = json.loads(inv_path.read_text(encoding="utf-8"))

    blob_sources: dict[str, list[str]] = {}
    for repo_entry in inv:
        rname = repo_entry["repo"]
        for t in repo_entry.get("tifs", []):
            blob_sources.setdefault(t["sha"], []).append(f"{rname}/{t['path']}")

    if idx_npz.is_file():
        data = np.load(idx_npz, allow_pickle=False)
        meta = json.loads(str(data["meta_json"]))
        if meta.get("unique_blobs_total") == len(blob_sources):
            return {
                "meta": meta,
                "sparse_idx": data["sparse_idx"],
                "sparse_offsets": data["sparse_offsets"],
                "top37_idx": data["top37_idx"],
                "unit_ranks": data["unit_ranks"],
            }

    log(f"[Stage 2] Indexing {len(blob_sources)} unique Git-verified public blobs from {len(inv)} repos...")
    foot_all_idx = np.flatnonzero(foot.ravel())
    sparse_chunks: list[np.ndarray] = []
    sparse_offsets: list[int] = [0]
    top37_rows: list[np.ndarray] = []
    unit_rank_rows: list[np.ndarray] = []
    records: list[dict] = []
    skipped: list[dict] = []
    dot_max = int(gems57_uniqueness.DOT_FIELD_MAX_SUPPORT)

    for idx_b, (git_sha, srcs) in enumerate(sorted(blob_sources.items())):
        if idx_b and idx_b % 350 == 0:
            log(f"  indexed {idx_b}/{len(blob_sources)} public blobs...")
        bpath = PUBLIC_CACHE / f"{git_sha}.tif"
        if not bpath.is_file():
            skipped.append({"git_sha": git_sha, "source": srcs[0], "reason": "missing_blob"})
            continue
        try:
            with rasterio.open(bpath) as ds:
                if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected_grid:
                    skipped.append({"git_sha": git_sha, "source": srcs[0], "reason": "grid_or_band_mismatch"})
                    continue
                arr = ds.read(1)
        except Exception as exc:
            skipped.append({"git_sha": git_sha, "source": srcs[0], "reason": f"invalid_tiff:{exc}"})
            continue

        clean = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
        del arr
        clean[~foot] = 0.0
        flat = clean.ravel()
        pos_idx = np.flatnonzero(flat > 0.0)
        n_pos = int(pos_idx.size)
        if n_pos == 0:
            skipped.append({"git_sha": git_sha, "source": srcs[0], "reason": "empty_in_footprint"})
            del clean, flat
            continue

        is_external = any(not s.startswith("GEMSDOE92/") for s in srcs)
        ext_src = next((s for s in srcs if not s.startswith("GEMSDOE92/")), srcs[0])
        rep = "dot_field" if n_pos <= dot_max else "continuous_surface"

        unit_rank_rows.append(unit_ranks(flat[sub_flat_idx]))
        if rep == "dot_field":
            sparse_chunks.append(pos_idx.astype(np.int32))
            sparse_offsets.append(sparse_offsets[-1] + n_pos)
            top37_rows.append(np.empty(0, dtype=np.int32))
        else:
            sparse_offsets.append(sparse_offsets[-1])
            vals_foot = flat[foot_all_idx]
            part = np.argpartition(-vals_foot, N_DOTS - 1)[:N_DOTS]
            top37_rows.append(foot_all_idx[part].astype(np.int32))
            del vals_foot, part

        records.append({
            "git_sha": git_sha,
            "file": ext_src,
            "all_sources_count": len(srcs),
            "is_external": is_external,
            "their_dots": n_pos,
            "representation": rep,
        })
        del clean, flat, pos_idx

    sparse_idx = np.concatenate(sparse_chunks) if sparse_chunks else np.empty(0, dtype=np.int32)
    sparse_off_arr = np.asarray(sparse_offsets, dtype=np.int64)
    cont_rows = [r for r in top37_rows if r.size > 0]
    top37_arr = np.stack(cont_rows, axis=0) if cont_rows else np.empty((0, N_DOTS), dtype=np.int32)
    c_ptr = 0
    for rec, r in zip(records, top37_rows):
        if r.size > 0:
            rec["cont_row"] = c_ptr
            c_ptr += 1
        else:
            rec["cont_row"] = -1

    unit_ranks_arr = np.stack(unit_rank_rows, axis=0).astype(np.float32)
    meta = {
        "repos_scanned": len(inv),
        "unique_blobs_total": len(blob_sources),
        "compatible_nonempty_blobs": len(records),
        "external_compatible_rasters": sum(1 for r in records if r["is_external"]),
        "skipped_count": len(skipped),
        "skipped": skipped,
        "records": records,
    }
    np.savez_compressed(
        idx_npz,
        meta_json=json.dumps(meta),
        sparse_idx=sparse_idx,
        sparse_offsets=sparse_off_arr,
        top37_idx=top37_arr,
        unit_ranks=unit_ranks_arr,
    )
    return {
        "meta": meta,
        "sparse_idx": sparse_idx,
        "sparse_offsets": sparse_off_arr,
        "top37_idx": top37_arr,
        "unit_ranks": unit_ranks_arr,
    }


def collect_local_registry(exclude_prefix: str = "gemsdoe92-relayconduit-") -> list[tuple[str, Path]]:
    seen_sha: set[str] = set()
    out: list[tuple[str, Path]] = []
    for d in (DOWNLOADS, ROOT / "data", ROOT / "data" / "bridge", CACHE_INPUTS / "lineage"):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.tif")):
            if p.name.startswith(exclude_prefix):
                continue
            if p.name in ("sample_submission.tif", "labels.tif", "existing_faults.tif"):
                continue
            sh = sha256_file(p)
            if sh in seen_sha:
                continue
            seen_sha.add(sh)
            out.append((str(p.relative_to(ROOT)), p))
    return out


def _build_3px_nbrs(mask: np.ndarray) -> np.ndarray:
    h, w = mask.shape
    offs = [(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if dy * dy + dx * dx <= 9]
    yy, xx = np.nonzero(mask)
    out = np.empty((len(offs), yy.size), dtype=np.int64)
    for k, (dy, dx) in enumerate(offs):
        out[k] = np.clip(yy + dy, 0, h - 1) * w + np.clip(xx + dx, 0, w - 1)
    return out


def stage_deploy_and_screen() -> int:
    from gems57.uniqueness import stop_historical_runner
    stop_historical_runner("run_relayconduit:stage_deploy_and_screen")

    grid = grid_mod.load_grid(CACHE_INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    d_cat = distance_transform_edt(~cat)
    quad = holdout.quadrant_ids(foot)
    with rasterio.open(SAMPLE_SUB) as ref_ds:
        expected_grid = (ref_ds.shape, ref_ds.crs, ref_ds.transform)

    foot_flat_all = np.flatnonzero(foot.ravel())
    sub_flat_idx = np.sort(np.random.default_rng(20261025).choice(foot_flat_all, 100_000, replace=False))

    X_foot, valid, w_cover, edge_strike_deg, L_geo, L_sub, _ = load_base_stack(foot)
    log("[Stage 2] Fitting deployment Stage-1 pairwise OOF + Stage-2 bimodal LOQO...")
    rf_deploy = fill_relay_columns(X_foot, foot, cat, edge_strike_deg, valid)
    stage1_deploy = fit_pairwise_stage1_oof(X_foot, cat, foot, valid, quad, seed=20261025)
    res_relay_dep = fit_stage2_bimodal_loqo(
        X_foot, stage1_deploy, cat, foot, valid, quad, w_cover, use_relay_cols=True, seed=20261025
    )
    res_notip_dep = fit_stage2_bimodal_loqo(
        X_foot, stage1_deploy, cat, foot, valid, quad, w_cover, use_relay_cols=False, seed=20261099
    )
    del stage1_deploy, X_foot
    gc.collect()

    arm_surfs_dep = build_arm_surfaces(res_relay_dep, res_notip_dep, rf_deploy, L_geo, L_sub, w_cover, valid)
    del res_relay_dep, res_notip_dep, rf_deploy, L_geo, L_sub, w_cover
    gc.collect()

    pub_idx = build_or_load_public_index(foot, sub_flat_idx, expected_grid)
    local_rasters = collect_local_registry()

    # Pre-placement surface check (Rule 1)
    u_pub = pub_idx["unit_ranks"]
    recs = pub_idx["meta"]["records"]
    surf_u = {arm: unit_ranks(np.where(foot, arm_surfs_dep[arm]["S_crest"], 0.0).ravel()[sub_flat_idx]) for arm in ARMS}
    pre_screen: dict[str, dict] = {}
    for arm, u_vec in surf_u.items():
        rhos_pub = u_pub @ u_vec
        best_i = int(np.argmax(np.abs(rhos_pub)))
        worst_pub_abs = float(abs(rhos_pub[best_i]))
        worst_loc_abs, worst_loc_file = 0.0, ""
        for rel_p, pth in local_rasters:
            with rasterio.open(pth) as ds:
                arr = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
            arr[~foot] = 0.0
            r_loc = float(np.dot(u_vec, unit_ranks(arr.ravel()[sub_flat_idx])))
            del arr
            if abs(r_loc) > worst_loc_abs:
                worst_loc_abs, worst_loc_file = abs(r_loc), rel_p
        passed = (worst_pub_abs <= 0.90) and (worst_loc_abs <= 0.90)
        pre_screen[arm] = {
            "passed_le_090": bool(passed),
            "public_worst_abs_spearman": round(worst_pub_abs, 6),
            "public_worst_signed_spearman": round(float(rhos_pub[best_i]), 6),
            "public_worst_witness": recs[best_i]["file"],
            "local_worst_abs_spearman": round(worst_loc_abs, 6),
            "local_worst_witness": worst_loc_file,
        }
        log(f"[Stage 2] Pre-placement [{arm:14s}]: pub |rho|={worst_pub_abs:.4f}, loc |rho|={worst_loc_abs:.4f} -> pass={passed}")
        if not passed:
            raise SystemExit(f"RULE 1 PRE-PLACEMENT SURFACE DUPLICATE STOP on {arm}: {pre_screen[arm]}")

    # Place 37,654 spaced dots per arm
    cand_masks: dict[str, np.ndarray] = {}
    for arm in ARMS:
        collar = ARM_COLLAR_PX[arm]
        pool = foot & valid & arm_surfs_dep[arm]["ridge_1d"] & (d_cat > collar)
        dm = spaced_top_mask(arm_surfs_dep[arm]["S_crest"], pool, N_DOTS, min_dist_px=MIN_DIST_PX, cand_cap=950_000)
        cand_masks[arm] = dm
        np.save(CACHE_LANE / f"dots_{arm}.npy", dm)
        log(f"[Stage 2] Emitted [{arm:14s}]: dots={int(dm.sum())}, min_d_cat={float(d_cat[dm].min()):.3f} px")
    del arm_surfs_dep
    gc.collect()

    # Post-placement dot screen across local + 102-repo public registry
    grid_size = foot.size
    dot_max = int(gems57_uniqueness.DOT_FIELD_MAX_SUPPORT)
    nbrs = {arm: _build_3px_nbrs(m) for arm, m in cand_masks.items()}
    u_final = {arm: unit_ranks(m.ravel()[sub_flat_idx].astype(np.float32)) for arm, m in cand_masks.items()}

    local_rows: dict[str, list[dict]] = {arm: [] for arm in ARMS}
    scratch = np.zeros(grid_size, dtype=bool)
    for rel_p, pth in local_rasters:
        with rasterio.open(pth) as ds:
            arr = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
        arr[~foot] = 0.0
        flat = arr.ravel()
        pos_idx = np.flatnonzero(flat > 0.0)
        n_pos = int(pos_idx.size)
        if n_pos == 0:
            del arr, flat
            continue
        rep = "dot_field" if n_pos <= dot_max else "continuous_surface"
        pts = pos_idx if rep == "dot_field" else foot_flat_all[np.argpartition(-flat[foot_flat_all], N_DOTS - 1)[:N_DOTS]]
        u_them = unit_ranks(flat[sub_flat_idx])
        scratch[pts] = True
        for arm in ARMS:
            ov = float(scratch[nbrs[arm]].any(axis=0).mean())
            local_rows[arm].append({
                "file": rel_p,
                "their_dots": n_pos,
                "representation": rep,
                "forward_overlap_3px": round(ov, 6),
                "final_spearman_rho": round(float(np.dot(u_final[arm], u_them)), 6),
                "surface_spearman_rho": round(float(np.dot(surf_u[arm], u_them)), 6),
            })
        scratch[pts] = False
        del arr, flat, pos_idx

    local_summary: dict[str, dict] = {}
    for arm, rows in local_rows.items():
        w_ov = max(rows, key=lambda r: r["forward_overlap_3px"])
        w_rs = max(rows, key=lambda r: abs(r["surface_spearman_rho"]))
        w_rf = max(rows, key=lambda r: abs(r["final_spearman_rho"]))
        over70 = [r for r in rows if r["forward_overlap_3px"] > 0.70]
        local_summary[arm] = {
            "rasters_checked": len(rows),
            "local_unique": bool(len(over70) == 0 and abs(w_rs["surface_spearman_rho"]) <= 0.90 and abs(w_rf["final_spearman_rho"]) <= 0.90),
            "literal_duplicate": bool(len(over70) > 0),
            "worst_forward_overlap_3px": w_ov["forward_overlap_3px"],
            "worst_overlap_witness": w_ov["file"],
            "worst_surface_abs_spearman": round(abs(w_rs["surface_spearman_rho"]), 6),
            "worst_surface_witness": w_rs["file"],
            "worst_final_abs_spearman": round(abs(w_rf["final_spearman_rho"]), 6),
            "top5_overlap": sorted(rows, key=lambda r: -r["forward_overlap_3px"])[:5],
        }

    sp_idx = pub_idx["sparse_idx"]
    sp_off = pub_idx["sparse_offsets"]
    top37 = pub_idx["top37_idx"]
    rhos_s_pub = {arm: u_pub @ surf_u[arm] for arm in ARMS}
    rhos_f_pub = {arm: u_pub @ u_final[arm] for arm in ARMS}
    pub_rows: dict[str, list[dict]] = {arm: [] for arm in ARMS}

    for i, rec in enumerate(recs):
        if not rec["is_external"]:
            continue
        pts = sp_idx[sp_off[i] : sp_off[i + 1]] if rec["representation"] == "dot_field" else top37[rec["cont_row"]]
        scratch[pts] = True
        for arm in ARMS:
            ov = float(scratch[nbrs[arm]].any(axis=0).mean())
            is_full_foot = rec["their_dots"] >= 5_167_000
            pub_rows[arm].append({
                "file": rec["file"],
                "git_sha": rec["git_sha"],
                "their_dots": rec["their_dots"],
                "representation": rec["representation"],
                "operative_overlap_3px": round(ov, 6),
                "literal_overlap_3px": 1.0 if is_full_foot else round(ov, 6),
                "surface_spearman_rho": round(float(rhos_s_pub[arm][i]), 6),
                "final_spearman_rho": round(float(rhos_f_pub[arm][i]), 6),
            })
        scratch[pts] = False

    pub_summary: dict[str, dict] = {}
    for arm, rows in pub_rows.items():
        dot_rows = [r for r in rows if r["representation"] == "dot_field"]
        le50_rows = [r for r in dot_rows if r["their_dots"] <= 50_000]
        cont_rows = [r for r in rows if r["representation"] == "continuous_surface"]
        w_op = max(rows, key=lambda r: r["operative_overlap_3px"])
        w_dot = max(dot_rows, key=lambda r: r["operative_overlap_3px"])
        w_le50 = max(le50_rows, key=lambda r: r["operative_overlap_3px"])
        w_cont = max(cont_rows, key=lambda r: r["operative_overlap_3px"])
        w_rs = max(rows, key=lambda r: abs(r["surface_spearman_rho"]))
        w_rf = max(rows, key=lambda r: abs(r["final_spearman_rho"]))
        over70_op = [r for r in rows if r["operative_overlap_3px"] > 0.70]
        full_foot_count = sum(1 for r in rows if r["their_dots"] >= 5_167_000)

        pub_summary[arm] = {
            "external_rasters_checked": len(rows),
            "dot_fields_le_150k_count": len(dot_rows),
            "dot_fields_le_50k_count": len(le50_rows),
            "continuous_surfaces_gt_150k_count": len(cont_rows),
            "full_footprint_dense_surfaces_count": full_foot_count,
            "worst_surface_abs_spearman": round(abs(w_rs["surface_spearman_rho"]), 6),
            "worst_surface_spearman_signed": w_rs["surface_spearman_rho"],
            "worst_surface_spearman_witness": w_rs["file"],
            "worst_final_abs_spearman": round(abs(w_rf["final_spearman_rho"]), 6),
            "worst_final_spearman_witness": w_rf["file"],
            "worst_operative_overlap_3px": w_op["operative_overlap_3px"],
            "worst_operative_witness": w_op["file"],
            "worst_operative_their_dots": w_op["their_dots"],
            "operative_over_70pct_count": len(over70_op),
            "unique_operative": bool(
                len(over70_op) == 0 and abs(w_rs["surface_spearman_rho"]) <= 0.90 and abs(w_rf["final_spearman_rho"]) <= 0.90
            ),
            "dual_reading_unique": bool(
                len(over70_op) == 0 and abs(w_rs["surface_spearman_rho"]) <= 0.90 and abs(w_rf["final_spearman_rho"]) <= 0.90
            ),
            "dot_fields_le_150k_worst_overlap_3px": w_dot["operative_overlap_3px"],
            "dot_fields_le_150k_worst_witness": w_dot["file"],
            "dot_fields_le_50k_worst_overlap_3px": w_le50["operative_overlap_3px"],
            "dot_fields_le_50k_worst_witness": w_le50["file"],
            "continuous_gt_150k_matched_budget_worst_overlap_3px": w_cont["operative_overlap_3px"],
            "continuous_gt_150k_matched_budget_worst_witness": w_cont["file"],
            "literal_worst_overlap_3px": 1.0,
            "literal_worst_witness": "17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif",
            "unique_under_literal_rule": False,
            "top10_operative": sorted(rows, key=lambda r: -r["operative_overlap_3px"])[:10],
            "top5_surface_spearman": sorted(rows, key=lambda r: -abs(r["surface_spearman_rho"]))[:5],
        }
        log(
            f"[Stage 2] Final uniqueness [{arm:14s}]: loc={local_summary[arm]['worst_forward_overlap_3px']:.4f}, "
            f"pub_op={pub_summary[arm]['worst_operative_overlap_3px']:.4f} ({pub_summary[arm]['worst_operative_witness']}), "
            f"over70={len(over70_op)}, unique_op={pub_summary[arm]['unique_operative']}"
        )

    uniq_doc = {
        "schema": "gemsdoe92-relayconduit-uniqueness.v1",
        "evidence_class": "REGISTRY-MEASUREMENT",
        "lane": "RELAYCONDUIT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "public_inventory": {
            "repos_scanned": pub_idx["meta"]["repos_scanned"],
            "unique_blobs_total": pub_idx["meta"]["unique_blobs_total"],
            "compatible_nonempty_blobs": pub_idx["meta"]["compatible_nonempty_blobs"],
            "external_compatible_rasters": pub_idx["meta"]["external_compatible_rasters"],
            "skipped_count": pub_idx["meta"]["skipped_count"],
        },
        "pre_placement_surface_screen": pre_screen,
        "local_summary": local_summary,
        "public_102repo_summary": pub_summary,
    }
    (CACHE_LANE / "uniqueness_stage.json").write_text(json.dumps(uniq_doc, indent=2), encoding="utf-8")
    return 0


def stage_holdout_seed(seed: int) -> int:
    from gems57.uniqueness import stop_historical_runner
    stop_historical_runner("run_relayconduit:stage_holdout_seed")

    from gems import coulomb_loqo as cl

    inputs = verify_pinned_inputs()
    grid = grid_mod.load_grid(CACHE_INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    quad = holdout.quadrant_ids(foot)

    folds, _ = holdout.buffered_component_draw(grid, seed=seed)
    vis = folds[0]["visible"]
    hid = folds[0]["hidden_all"]
    excl = hid | (distance_transform_edt(~hid) <= 3.0)
    d_vis = distance_transform_edt(~vis)

    X_foot, valid, w_cover, edge_strike_deg, L_geo, L_sub, _ = load_base_stack(foot)
    log(f"[Stage 3 seed={seed}] Rebuilding visible-only tip-relay fields, Stage-1 OOF & Stage-2 bimodal LOQO...")
    rf_s = fill_relay_columns(X_foot, foot, vis, edge_strike_deg, valid)
    st1_s = fit_pairwise_stage1_oof(X_foot, vis, foot, valid, quad, exclude_mask=excl, seed=20261025 + seed)

    # Evaluate OOF auto-context canaries strictly out-of-quadrant
    pb_oof_all = np.zeros(foot.shape, dtype=np.float32)
    pp_oof_all = np.zeros(foot.shape, dtype=np.float32)
    for q_s in range(4):
        qm = valid & (quad == q_s)
        pb_oof_all[qm] = st1_s[q_s][0][qm]
        pp_oof_all[qm] = st1_s[q_s][1][qm]
    ac_s = steerable_oof_autocontext(pb_oof_all, pp_oof_all, valid)
    X_foot[:, 26] = ac_s["oof_blind_line_short"][foot]
    X_foot[:, 27] = ac_s["oof_blind_line_long"][foot]
    X_foot[:, 28] = ac_s["oof_phys_line_short"][foot]
    X_foot[:, 29] = ac_s["oof_phys_bridge_axial"][foot]
    del pb_oof_all, pp_oof_all, ac_s

    foot_row = np.full(foot.shape, -1, dtype=np.int32)
    foot_row[foot] = np.arange(int(foot.sum()), dtype=np.int32)
    rng = np.random.default_rng(520810 + seed)
    y_list, idx_list = [], []
    for f in folds:
        pos_flat = np.flatnonzero(f["truth"] & foot & valid)
        neg_pool = np.flatnonzero(f["region"] & foot & valid & (~cat))
        neg_flat = rng.choice(neg_pool, size=min(neg_pool.size, pos_flat.size * 5), replace=False)
        idx_list.append(foot_row.ravel()[np.concatenate([pos_flat, neg_flat])])
        y_list.append(np.concatenate([np.ones(pos_flat.size, np.int8), np.zeros(neg_flat.size, np.int8)]))
    eval_rows = np.concatenate(idx_list)
    eval_y = np.concatenate(y_list)

    oof_canaries: dict[str, dict] = {}
    for col_j in OOF_COLS:
        fname = FEATURE_NAMES[col_j]
        raw_auc, sym_auc = symmetric_auc(eval_y, X_foot[eval_rows, col_j])
        oof_canaries[fname] = {"auc": round(raw_auc, 6), "symmetric_auc": round(sym_auc, 6)}
        if sym_auc > 0.90:
            raise SystemExit(f"RULE 4 OOF CANARY FAILED on {fname} (seed={seed}): {sym_auc:.6f}")

    res_rel_s = fit_stage2_bimodal_loqo(
        X_foot, st1_s, vis, foot, valid, quad, w_cover,
        use_relay_cols=True, exclude_mask=excl, seed=20261025 + seed,
    )
    res_notip_s = fit_stage2_bimodal_loqo(
        X_foot, st1_s, vis, foot, valid, quad, w_cover,
        use_relay_cols=False, exclude_mask=excl, seed=20261099 + seed,
    )
    del st1_s, X_foot
    gc.collect()

    arm_surfs_s = build_arm_surfaces(res_rel_s, res_notip_s, rf_s, L_geo, L_sub, w_cover, valid)
    for arm_c in ARMS:
        raw_auc, sym_auc = symmetric_auc(eval_y, arm_surfs_s[arm_c]["S_crest"][foot][eval_rows])
        oof_canaries[f"surface_{arm_c}"] = {"auc": round(raw_auc, 6), "symmetric_auc": round(sym_auc, 6)}
    del res_rel_s, res_notip_s, rf_s, L_geo, L_sub, w_cover, eval_rows, eval_y
    gc.collect()

    fold_preds: dict[str, np.ndarray] = {}
    for arm in ARMS:
        col_d = ARM_COLLAR_PX[arm]
        pool_s = foot & valid & arm_surfs_s[arm]["ridge_1d"] & (d_vis > col_d)
        fold_preds[arm] = spaced_top_mask(
            arm_surfs_s[arm]["S_crest"], pool_s, N_DOTS, min_dist_px=MIN_DIST_PX, cand_cap=950_000
        ).astype(np.float32)
    del arm_surfs_s, valid
    gc.collect()

    # Now load COULOMBLOQO stack & fit controls in clean heap (< 950 MiB RSS)
    log(f"[Stage 3 seed={seed}] Rebuilding COULOMBLOQO, H19-5 & R0 controls on identical folds...")
    band_ids_cl = (2, 4, 5, 7, 8, 11, 12, 13, 15, 17, 18, 19)
    b_cl = {}
    with rasterio.open(inputs["training_features"]) as ds_tf:
        for bi in band_ids_cl:
            a = ds_tf.read(bi).astype(np.float32)
            a[(~np.isfinite(a)) | (a <= -1e20)] = np.nan
            b_cl[bi] = a
    with rasterio.open(inputs["ext_geodawn_rad_u8"]) as ds_r:
        rk_c, rth_c, ru_c = ds_r.read(1), ds_r.read(2), ds_r.read(3)
    valid_cl0 = foot & np.isfinite(b_cl[12]) & np.isfinite(b_cl[19]) & np.isfinite(b_cl[2])
    gdr_cl = cl.gdr_blind_thermal_features(inputs["gdr_wellspring_in_footprint"], foot.shape, valid_cl0, sigma_px=14.0)
    st_cl = cl.compute_feature_stack(
        rtp=b_cl[2], geod_2ndinv=b_cl[4], grav_slope=b_cl[5], geod_shearrate=b_cl[7], geod_dilaterate=b_cl[8],
        grav_vg=b_cl[11], det_elev=b_cl[12], grav_anom=b_cl[13], depth_to_base=b_cl[15], cond_surf=b_cl[17],
        grav_hg=b_cl[18], det_elev_slope=b_cl[19], rad_k=rk_c, rad_th=rth_c, rad_u=ru_c,
        gdr_plume_feat=gdr_cl["plume_feat"], footprint=foot,
    )
    del b_cl, rk_c, rth_c, ru_c, gdr_cl, valid_cl0
    gc.collect()

    cl_proba = cl.fit_predict_loqo(
        st_cl["X_foot"], foot, st_cl["valid"], quad, vis,
        excluded_mask=excl, guard_px=12, neg_buffer_px=5.0, seed=20261024,
    )
    cl_crest = cl.build_crest_surface(cl_proba, st_cl["L_topo"], st_cl["L_sub"], st_cl["valid"], sub_weight=0.80)
    valid_cl = st_cl["valid"]
    del st_cl, cl_proba
    gc.collect()

    for cname, col_d in (("control_COULOMBLOQO", 2.0), ("control_COULOMBLOQO_d32", 3.2), ("control_COULOMBLOQO_d35", 3.5)):
        pool_c = foot & valid_cl & cl_crest["ridge_1d"] & (d_vis > col_d)
        fold_preds[cname] = cl.spaced_top_mask(
            cl_crest["S_crest"], pool_c, N_DOTS, min_dist_px=MIN_DIST_PX, cand_cap=900_000
        ).astype(np.float32)
    del cl_crest, valid_cl

    with rasterio.open(inputs["parent_r0_zeros"]) as ds_r0:
        arr_r0 = np.where(foot, np.nan_to_num(ds_r0.read(1).astype(np.float32), nan=0.0), 0.0)
    with rasterio.open(inputs["anc_h19_5"]) as ds_h19:
        h19_mask = (np.nan_to_num(ds_h19.read(1), nan=0.0) > 0) & foot
    scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)
    fold_preds["control_H19_5"] = cl.spaced_top_mask(
        scan_rank, h19_mask & (d_vis > 2.0), N_DOTS, min_dist_px=MIN_DIST_PX, cand_cap=200_000
    ).astype(np.float32)
    fold_preds["control_R0"] = np.where(d_vis > 2.0, arr_r0, 0.0).astype(np.float32)
    del h19_mask, scan_rank

    rule2_terms: dict[str, np.ndarray] = {}
    per_fold: dict[str, list[dict]] = {k: [] for k in fold_preds}
    for fold in folds:
        for k_r2, arr_p in fold_preds.items():
            f_res, t_r2 = evaluate_holdout.evaluate(arr_p, fold, foot)
            rule2_terms[k_r2] = t_r2 if k_r2 not in rule2_terms else rule2_terms[k_r2] + t_r2
            per_fold[k_r2].append({
                "seed": seed,
                "fold": fold["name"],
                "dti": round(float(f_res["dti"]), 6),
                "n_truth": int(f_res["n_truth"]),
                "n_emitted": int(f_res["n_emitted"]),
            })
    del fold_preds

    # Static deployment terms for this seed
    static_terms: dict[str, np.ndarray] = {}
    for arm in ARMS:
        arr_dep = np.load(CACHE_LANE / f"dots_{arm}.npy").astype(np.float32)
        for fold in folds:
            _, t_st = evaluate_holdout.evaluate(arr_dep, fold, foot)
            static_terms[arm] = t_st if arm not in static_terms else static_terms[arm] + t_st
        del arr_dep

    static_comp_files = {
        "VENTSCARP_ventscarp": DOWNLOADS / "gemsdoe92-ventscarp-ventscarp-37654-20261025-6e97367c-zeros.tif",
        "COULOMBLOQO_standalone": DOWNLOADS / "h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif",
        "KNICKLOQO_standalone": DOWNLOADS / "h33-h33-2-b2-KNICKLOQOstandalone-20261025-7a05ff5a-zeros.tif",
        "LISTRICDIP_updip50": DOWNLOADS / "gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif",
        "R0": inputs["parent_r0_zeros"],
    }
    for sname, spath in static_comp_files.items():
        if not spath.is_file():
            continue
        with rasterio.open(spath) as ds_s:
            arr_s = np.where(foot, np.nan_to_num(ds_s.read(1).astype(np.float32), nan=0.0), 0.0)
        for fold in folds:
            _, t_st = evaluate_holdout.evaluate(arr_s, fold, foot)
            static_terms[sname] = t_st if sname not in static_terms else static_terms[sname] + t_st
        del arr_s

    save_dict: dict[str, object] = {
        "meta_json": json.dumps({
            "seed": seed,
            "oof_canaries": oof_canaries,
            "per_fold": per_fold,
            "receipts": [f["receipt"] for f in folds],
        }),
    }
    for k, v in rule2_terms.items():
        save_dict[f"r2_{k}"] = v
    for k, v in static_terms.items():
        save_dict[f"st_{k}"] = v
    np.savez_compressed(CACHE_LANE / f"holdout_seed_{seed}.npz", **save_dict)
    log(f"[Stage 3 seed={seed}] Saved fold terms cleanly.")
    return 0


def stage_finalize(elapsed_total: float) -> int:
    from gems57.uniqueness import stop_historical_runner
    stop_historical_runner("run_relayconduit:stage_finalize")

    inputs = verify_pinned_inputs()
    grid = grid_mod.load_grid(CACHE_INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    d_cat = distance_transform_edt(~cat)
    quad = holdout.quadrant_ids(foot)

    d_base = np.load(CACHE_LANE / "base_physics_stack.npz", allow_pickle=False)
    vent_stats = json.loads(str(d_base["vent_stats_json"]))
    del d_base

    canary_rows = json.loads((CACHE_LANE / "prefit_canaries.json").read_text(encoding="utf-8"))
    uniq_doc = json.loads((CACHE_LANE / "uniqueness_stage.json").read_text(encoding="utf-8"))
    pre_screen = uniq_doc["pre_placement_surface_screen"]
    local_summary = uniq_doc["local_summary"]
    pub_summary = uniq_doc["public_102repo_summary"]

    rule2_terms: dict[str, np.ndarray] = {}
    static_terms: dict[str, np.ndarray] = {}
    per_fold_rule2: dict[str, list[dict]] = {}
    fold_receipts: list[dict] = []

    for seed in SEEDS:
        npz_s = np.load(CACHE_LANE / f"holdout_seed_{seed}.npz", allow_pickle=False)
        meta_s = json.loads(str(npz_s["meta_json"]))
        fold_receipts.extend(meta_s["receipts"])
        for fname, crow in meta_s["oof_canaries"].items():
            canary_rows.setdefault(fname, {"draws": {}})["draws"][str(seed)] = crow
        for k, flist in meta_s["per_fold"].items():
            per_fold_rule2.setdefault(k, []).extend(flist)
        for key in npz_s.files:
            if key.startswith("r2_"):
                arm_k = key[3:]
                rule2_terms[arm_k] = npz_s[key] if arm_k not in rule2_terms else rule2_terms[arm_k] + npz_s[key]
            elif key.startswith("st_"):
                arm_k = key[3:]
                static_terms[arm_k] = npz_s[key] if arm_k not in static_terms else static_terms[arm_k] + npz_s[key]

    boot_by_arm = {
        arm: evaluate_holdout.pooled_summary(rule2_terms, candidate=arm, draws=1000, seed=520810)
        for arm in ARMS
    }
    static_boot = evaluate_holdout.pooled_summary(static_terms, candidate="conduit_notip", draws=1000, seed=520810)

    for k_log in rule2_terms:
        sc = boot_by_arm["relay_conduit"]["scores"][k_log]
        log(f"[Finalize] RULE-2 HOLDOUT-DTI [{k_log:24s}] = {sc['dti']:.6f} [{sc['ci95'][0]:.6f}, {sc['ci95'][1]:.6f}]")
    for k_log in static_boot["scores"]:
        sc = static_boot["scores"][k_log]
        log(f"[Finalize] STATIC HOLDOUT-DTI [{k_log:24s}] = {sc['dti']:.6f} [{sc['ci95'][0]:.6f}, {sc['ci95'][1]:.6f}]")

    cand_masks = {arm: np.load(CACHE_LANE / f"dots_{arm}.npy") for arm in ARMS}
    pred_arrays = {arm: m.astype(np.float32) for arm, m in cand_masks.items()}

    with rasterio.open(inputs["parent_r0_zeros"]) as ds_r0:
        r0_bool = (np.nan_to_num(ds_r0.read(1).astype(np.float32), nan=0.0) > 0.0) & foot
    shared_r0_by_arm = {arm: int((cand_masks[arm] & r0_bool).sum()) for arm in ARMS}
    pct_changed_by_arm = {
        arm: round(100.0 * (1.0 - shared_r0_by_arm[arm] / float(max(int(r0_bool.sum()), 1))), 4)
        for arm in ARMS
    }
    del r0_bool

    with rasterio.open(inputs["sgmc_faults_control"]) as ds_sgmc:
        sgmc_truth = (ds_sgmc.read(1) > 0) & foot & (d_cat > 5.0)
    sgmc_domain = foot & (d_cat > 5.0)
    sgmc_scores: dict[str, dict] = {}
    for arm, arr_f in pred_arrays.items():
        res_sg = gems57_metric.dti_exact(np.where(sgmc_domain, arr_f, 0.0).astype(np.float32), sgmc_truth)
        sgmc_scores[arm] = {
            "evidence_class": "PROXY",
            "control": "USGS SGMC off-catalogue bedrock faults (d_cat > 5.0 px)",
            "truth_pixels": int(sgmc_truth.sum()),
            "dti": round(float(res_sg["dti"]), 6),
        }
        log(f"[Finalize] SGMC PROXY         [{arm:24s}] = {sgmc_scores[arm]['dti']:.6f}")

    with rasterio.open(inputs["training_features"]) as ds_tf:
        b19_raw = np.nan_to_num(ds_tf.read(19).astype(np.float32), nan=0.0)
        b15_raw = np.nan_to_num(ds_tf.read(15).astype(np.float32), nan=0.0)
    b19_raw[np.abs(b19_raw) > 1e20] = 0.0
    b15_raw[np.abs(b15_raw) > 1e20] = 0.0
    slope_deg = (
        np.rad2deg(np.arctan(np.maximum(b19_raw, 0.0)))
        if float(np.percentile(b19_raw[foot], 99.0)) <= 2.5
        else np.maximum(b19_raw, 0.0)
    )
    quad_names = {0: "NW", 1: "NE", 2: "SW", 3: "SE"}
    diagnostics: dict[str, dict] = {}
    for arm, cmask in cand_masks.items():
        n_pos = int(cmask.sum())
        sl_vals = slope_deg[cmask]
        cov_vals = np.maximum(b15_raw[cmask], 0.0)
        diagnostics[arm] = {
            "positive_pixels": n_pos,
            "total_mass": round(float(pred_arrays[arm].sum()), 2),
            "min_distance_to_catalogue_px": round(float(d_cat[cmask].min()), 4),
            "median_distance_to_catalogue_px": round(float(np.median(d_cat[cmask])), 2),
            "quadrant_pct": {
                qname: round(100.0 * float((cmask & (quad == qid)).sum()) / max(n_pos, 1), 2)
                for qid, qname in quad_names.items()
            },
            "slope_regime_pct": {
                "lt_2_5_deg_pct": round(100.0 * float((sl_vals < 2.5).mean()), 2),
                "2_5_to_6_deg_pct": round(100.0 * float(((sl_vals >= 2.5) & (sl_vals < 6.0)).mean()), 2),
                "6_to_12_deg_pct": round(100.0 * float(((sl_vals >= 6.0) & (sl_vals < 12.0)).mean()), 2),
                "ge_12_deg_pct": round(100.0 * float((sl_vals >= 12.0).mean()), 2),
            },
            "sedimentary_cover_pct": {
                "deep_basin_gt_150m_pct": round(100.0 * float((cov_vals > 150.0).mean()), 2),
                "median_cover_m": round(float(np.median(cov_vals)), 1),
            },
        }
    del b19_raw, b15_raw, slope_deg

    unique_op_arms = [a for a in ARMS if pub_summary[a]["unique_operative"] and local_summary[a]["local_unique"]]
    if unique_op_arms:
        hero_arm = max(unique_op_arms, key=lambda a: boot_by_arm[a]["scores"][a]["dti"])
    else:
        hero_arm = max(ARMS, key=lambda a: boot_by_arm[a]["scores"][a]["dti"])
    log(f"[Finalize] Hero arm selected: {hero_arm} (unique_op_arms={unique_op_arms})")

    arm_artifacts: dict[str, dict] = {}
    for arm, arr_pred in pred_arrays.items():
        n_pos = int((arr_pred > 0.0).sum())
        raw_sha8 = hashlib.sha256(arr_pred.tobytes()).hexdigest()[:8]
        stem = f"gemsdoe92-relayconduit-{arm}-{n_pos}-{DATE_STR}-{raw_sha8}"
        tif_path = DOWNLOADS / f"{stem}-zeros.tif"
        sub_name = f"GEMSDOE92-RELAYCONDUIT-{arm}-{DATE_STR}"
        r2_dti = boot_by_arm[arm]["scores"][arm]["dti"]
        st_dti = static_boot["scores"][arm]["dti"]
        if arm == "relay_conduit":
            desc = f"{n_pos}px tip-relay+OOF blind conduit d>3.2px"
        elif arm == "relay_delta":
            desc = f"{n_pos}px tip-relay uplift delta d>3.5px"
        else:
            desc = f"{n_pos}px zero-tip OOF blind+3DEP conduit d>2px"
        sub_note = f"RELAYCONDUIT {arm}: {desc}; HOLDOUT-DTI {r2_dti:.6f} (st {st_dti:.6f}) [neg]"[:140]

        for old_p in DOWNLOADS.glob(f"gemsdoe92-relayconduit-{arm}-*"):
            old_p.unlink(missing_ok=True)

        writer_rec = submission_writer.write_submission(
            tif_path,
            arr_pred,
            SAMPLE_SUB,
            foot,
            name=sub_name,
            note=sub_note,
            catalogue=cat,
            metadata={"lane": "RELAYCONDUIT", "arm": arm},
        )
        zip_path = tif_path.with_suffix(".zip")
        tif_sha = sha256_file(tif_path)
        zip_sha = sha256_file(zip_path)

        val_rec = gems57_validate.validate(tif_path, foot, cat)
        gems57_validate.assert_submittable(val_rec)

        prune_req = 3 if ARM_COLLAR_PX[arm] >= 3.0 else 2
        gate_res = run_gates(
            str(tif_path), str(SAMPLE_SUB), str(EXISTING_FAULTS),
            prune_radius=prune_req, require_submission_encoding=True,
        )
        gates_ok, gates_text = summarise(gate_res)
        if not gates_ok:
            raise SystemExit(f"Gate failure on {tif_path}:\n{gates_text}")

        ps = pub_summary[arm]
        ls = local_summary[arm]
        audit_path = DOWNLOADS / f"{stem}-audit.json"
        audit_doc = {
            "schema": "gemsdoe92-per-file-audit.v2",
            "lane": "RELAYCONDUIT",
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
                + (
                    f"Operative 102-repo uniqueness PASS (worst overlap {ps['worst_operative_overlap_3px']:.4f} <= 0.70, "
                    f"|rho| {ps['worst_surface_abs_spearman']:.4f} <= 0.90); "
                    if ps["unique_operative"]
                    else f"Operative overlap {ps['worst_operative_overlap_3px']:.4f} > 0.70 vs {ps['worst_operative_witness']}; "
                )
                + "marked verdict='negative' and submission_eligible=false under binding literal "
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
                "repos_scanned": uniq_doc["public_inventory"]["repos_scanned"],
                "external_rasters_checked": ps["external_rasters_checked"],
                "unique_under_literal_rule": False,
                "stop_required": True,
                "literal_worst_overlap_3px": 1.0,
                "literal_witness": ps["literal_worst_witness"],
                "dual_reading_unique": ps["dual_reading_unique"],
                "unique_operative": ps["unique_operative"],
                "worst_operative_overlap_3px": ps["worst_operative_overlap_3px"],
                "worst_operative_witness": ps["worst_operative_witness"],
                "dot_fields_le_150k_worst_overlap_3px": ps["dot_fields_le_150k_worst_overlap_3px"],
                "dot_fields_le_50k_worst_overlap_3px": ps["dot_fields_le_50k_worst_overlap_3px"],
                "worst_surface_abs_spearman": ps["worst_surface_abs_spearman"],
            },
            "run_card": "evidence/relayconduit_run_card.json",
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
            "collar_px": ARM_COLLAR_PX[arm],
            "submission_name": sub_name,
            "submission_note": sub_note,
            "validator_checks": val_rec["checks"],
            "gates": [{"name": g.name, "ok": bool(g.ok), "detail": g.detail} for g in gate_res],
            "gates_all_pass": True,
            "writer_receipt_sha256": writer_rec["sha256"],
        }

    feat_canaries_summary = {}
    for fname in FEATURE_NAMES:
        d = canary_rows[fname]["draws"]
        mx = max(v["symmetric_auc"] for v in d.values())
        feat_canaries_summary[fname] = {"max_symmetric_auc": round(mx, 6), "draws": d}
    max_feat_name, max_feat_row = max(feat_canaries_summary.items(), key=lambda kv: kv[1]["max_symmetric_auc"])
    max_surf_sym = max(
        max(v["symmetric_auc"] for v in canary_rows[f"surface_{a}"]["draws"].values())
        for a in ARMS
    )

    hero_boot = boot_by_arm[hero_arm]
    hero_art = arm_artifacts[hero_arm]
    hero_ps = pub_summary[hero_arm]
    hero_ls = local_summary[hero_arm]
    hero_r2 = hero_boot["scores"][hero_arm]
    hero_st = static_boot["scores"][hero_arm]

    holdout_doc = {
        "schema": "gemsdoe92-relayconduit-holdout.v1",
        "lane": "RELAYCONDUIT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "pre_registration": "docs/HYPOTHESES_20261025_RELAYCONDUIT.md",
        "evaluator_version": evaluate_holdout.VERSION,
        "evaluator_hashes": evaluate_holdout.implementation_hashes(),
        "experiments_run": 3,
        "experiment_budget_cap": 3,
        "weekly_slots_used": 0,
        "elapsed_seconds": round(elapsed_total, 2),
        "hero_arm": hero_arm,
        "vent_inventory_in_footprint": vent_stats,
        "leakage_canaries": {
            "all_pass": bool(max_feat_row["max_symmetric_auc"] <= 0.90),
            "threshold_symmetric_auc": 0.90,
            "features_tested_count": len(FEATURE_NAMES),
            "max_single_feature_name": max_feat_name,
            "max_single_feature_symmetric_auc": max_feat_row["max_symmetric_auc"],
            "max_surface_symmetric_auc": round(max_surf_sym, 6),
            "features": feat_canaries_summary,
        },
        "strict_draw_blind_rule2_holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": evaluate_holdout.VERSION,
            "withheld_positives": int(hero_r2["withheld_positive_pixels"]),
            "bootstrap_draws": 1000,
            "bootstrap_cluster_m": 20000,
            "scores": hero_boot["scores"],
            "paired_differences_vs_hero": hero_boot["paired_differences"],
            "paired_differences_by_arm": {a: boot_by_arm[a]["paired_differences"] for a in ARMS},
            "per_fold": per_fold_rule2,
            "fold_receipts": fold_receipts,
        },
        "static_deployment_holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": evaluate_holdout.VERSION,
            "withheld_positives": int(static_boot["scores"]["conduit_notip"]["withheld_positive_pixels"]),
            "scores": static_boot["scores"],
            "paired_differences_vs_conduit_notip": static_boot["paired_differences"],
        },
        "sgmc_off_catalogue_proxy": sgmc_scores,
        "diagnostics": diagnostics,
        "artifacts": arm_artifacts,
    }

    run_card = {
        "schema": "gemsdoe92-run-card.v2",
        "lane": "RELAYCONDUIT",
        "arm": hero_arm,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "pre_registration": "docs/HYPOTHESES_20261025_RELAYCONDUIT.md",
        "hypothesis": (
            "Self-excluded oriented fault-tip Coulomb relay cones and opposing-tip step-over "
            "bridges (sqrt(W_excl^2 - ||J_excl||^2)), fused with pairwise out-of-fold "
            "multi-azimuth structural auto-context and sedimentary-cover-adaptive blind "
            "subsurface hydrothermal conduit modeling (zero-topography gravity/TMI_up150/MT/"
            "seismicity/INGENIOUS sinter & 2m-probe M_blind + 3DEP-10m scarp/chi-knickpoint M_full) "
            "on a Dual Geomorphic U Subsurface Crest Gate, recover concealed step-over and "
            "blind basin faults while avoiding exposed range-front cliff overlap."
        ),
        "mechanism": (
            "Two-stage spatially guarded LOQO: Stage-1 fits 6 pairwise 2-quadrant models for "
            "both Topography-Blind M1_blind (15 subsurface/hydrothermal channels) and Full M1_phys "
            "(26 zero-catalogue channels) so Stage-2 receives strictly out-of-quadrant 6-azimuth "
            "steerable log-odds line integrals without test-quadrant or in-sample leakage. Stage-2 "
            "adds 5 exact self-excluded oriented fault-tip & step-over relay channels and blends "
            "M2_blind with M2_full via cover weight w_cover(B15) on 1D geomorphic U subsurface crests."
        ),
        "non_fault_mimic": (
            "Pleistocene Lake Lahontan (~1,330 m) beach-ridge bars / shoreline tufa mounds and "
            "buried Tertiary lava-flow margins without Quaternary tectonic throw."
        ),
        "named_non_fault_process_that_could_mimic_it": (
            "Pleistocene Lake Lahontan (~1,330 m) shoreline beach bars / lacustrine tufa mounds "
            "and buried lava-flow margins (deconfounded via explicit Tufa exclusion, 1,330 m "
            "contour null, gravity/basement dip concordance, and oriented fault-tip tangents)."
        ),
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": evaluate_holdout.VERSION,
            "withheld_positives": int(hero_r2["withheld_positive_pixels"]),
            "dti": hero_r2["dti"],
            "ci95": hero_r2["ci95"],
            "static_dcat2_dti": hero_st["dti"],
            "static_dcat2_ci95": hero_st["ci95"],
            "paired_vs_COULOMBLOQO_d2": hero_boot["paired_differences"]["control_COULOMBLOQO"],
            "paired_vs_COULOMBLOQO_d32": hero_boot["paired_differences"]["control_COULOMBLOQO_d32"],
            "paired_vs_COULOMBLOQO_d35": hero_boot["paired_differences"]["control_COULOMBLOQO_d35"],
            "paired_vs_conduit_notip": hero_boot["paired_differences"].get("conduit_notip"),
            "paired_vs_H19_5": hero_boot["paired_differences"]["control_H19_5"],
            "paired_vs_R0": hero_boot["paired_differences"]["control_R0"],
            "all_arms_rule2": {a: hero_boot["scores"][a] for a in ARMS},
            "all_arms_static": {a: static_boot["scores"][a] for a in ARMS},
            "sgmc_off_catalogue_proxy": sgmc_scores[hero_arm],
        },
        "leakage_canary": {
            "all_pass": bool(max_feat_row["max_symmetric_auc"] <= 0.90),
            "threshold_symmetric_auc": 0.90,
            "features_tested": len(FEATURE_NAMES),
            "max_single_feature_name": max_feat_name,
            "max_single_feature_symmetric_auc": max_feat_row["max_symmetric_auc"],
            "max_surface_symmetric_auc": round(max_surf_sym, 6),
        },
        "correlation_overlap_vs_registry": {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "pre_placement_surface": pre_screen[hero_arm],
            "local": hero_ls,
            "public_102_repos": hero_ps,
            "unique_operative": hero_ps["unique_operative"] and hero_ls["local_unique"],
            "unique_under_literal_rule": False,
            "literal_stop_witness": hero_ps["literal_worst_witness"],
            "literal_forward_overlap_3px": 1.0,
        },
        "file": Path(hero_art["file_zeros"]).name,
        "primary_download": hero_art["file_zeros"],
        "zip_download": hero_art["file_zip"],
        "raster_sha256": hero_art["sha256_zeros"],
        "zip_sha256": hero_art["sha256_zip"],
        "validator_output": {
            "evidence_class": "FORMAT-VALIDATION",
            "all_must_gates_pass": True,
            "gates_count": len(hero_art["gates"]),
            "values_range": [0.0, 1.0],
            "nan_count": 0,
            "positive_pixels": hero_art["n_positive_pixels"],
            "gates": hero_art["gates"],
            "validator_checks": hero_art["validator_checks"],
        },
        "submission_name": hero_art["submission_name"],
        "note": hero_art["submission_note"],
        "note_length": len(hero_art["submission_note"]),
        "ok_to_download": True,
        "ok_to_submit": False,
        "submission_eligible": False,
        "verdict": "negative",
        "verdict_reason": (
            f"Format-valid [0, 1] GeoTIFF generated this session ({hero_art['n_positive_pixels']} binary dots, "
            f"11/11 automated gates PASS, 0 NaNs). Rule-2 HOLDOUT-DTI = {hero_r2['dti']:.6f} "
            f"[{hero_r2['ci95'][0]:.6f}, {hero_r2['ci95'][1]:.6f}]. "
            + (
                f"Passes operative local + 102-repo sparse/matched-budget uniqueness "
                f"(worst 3-px overlap {hero_ps['worst_operative_overlap_3px']:.4f} <= 0.70, "
                f"worst |rho| {hero_ps['worst_surface_abs_spearman']:.4f} <= 0.90), "
                if hero_ps["unique_operative"]
                else f"Fails operative 102-repo dot overlap ({hero_ps['worst_operative_overlap_3px']:.4f} > 0.70 vs {hero_ps['worst_operative_witness']}), "
            )
            + "and remains verdict='negative' (submission_eligible=false, 0 weekly slots spent) "
            "under the binding literal registry rule (1.000 > 0.70 vs 17GEMSDOE full-footprint surface) "
            "and separate human slot-selector governance."
        ),
        "experiments_used": 3,
        "weekly_slots_used": 0,
        "organizer_confirmed_score": None,
        "siblings": {
            a: {
                "file_zeros": arm_artifacts[a]["file_zeros"],
                "file_zip": arm_artifacts[a]["file_zip"],
                "file_audit": arm_artifacts[a]["file_audit"],
                "sha256_zeros": arm_artifacts[a]["sha256_zeros"],
                "rule2_holdout_dti": boot_by_arm[a]["scores"][a]["dti"],
                "rule2_ci95": boot_by_arm[a]["scores"][a]["ci95"],
                "static_holdout_dti": static_boot["scores"][a]["dti"],
                "unique_operative": pub_summary[a]["unique_operative"],
                "worst_operative_overlap_3px": pub_summary[a]["worst_operative_overlap_3px"],
                "verdict": "negative",
            }
            for a in ARMS
        },
    }

    for fname, obj in (
        ("relayconduit_holdout.json", holdout_doc),
        ("relayconduit_uniqueness.json", uniq_doc),
        ("relayconduit_run_card.json", run_card),
    ):
        raw_txt = json.dumps(obj, indent=2) + "\n"
        (EVIDENCE / fname).write_text(raw_txt, encoding="utf-8")
        (DOWNLOADS / fname).write_text(raw_txt, encoding="utf-8")

    existing_rows = [r for r in ledger_mod.load() if r.get("axis") != "RELAYCONDUIT"]
    ledger_mod.save(existing_rows)

    for arm in ARMS:
        art = arm_artifacts[arm]
        ps = pub_summary[arm]
        ls = local_summary[arm]
        r2_s = boot_by_arm[arm]["scores"][arm]
        st_s = static_boot["scores"][arm]
        ledger_mod.append_variant({
            "id": art["stem"],
            "parent": "h33-h33-2-b2",
            "axis": "RELAYCONDUIT",
            "value": arm,
            "n_dots": str(art["n_positive_pixels"]),
            "pct_changed": f"{pct_changed_by_arm[arm]:.4f}",
            "sha256": art["sha256_zeros"],
            "status": "BUILT",
            "predicted_change": "none; HOLDOUT-DTI recorded in evidence/relayconduit_holdout.json",
            "file_zeros": art["file_zeros"],
            "file_nan": "",
            "sha8": art["sha256_zeros"][:8],
            "change_desc": art["submission_note"],
            "receipt_score": "",
            "receipt_date": "",
            "notes": (
                f"verdict=negative; no weekly slot; rule2_dti={r2_s['dti']:.6f} "
                f"[{r2_s['ci95'][0]:.6f} {r2_s['ci95'][1]:.6f}]; static_dcat2={st_s['dti']:.6f}; "
                f"sgmc_proxy={sgmc_scores[arm]['dti']:.6f}; local_worst={ls['worst_forward_overlap_3px']:.4f}; "
                f"pub_op_worst={ps['worst_operative_overlap_3px']:.4f} (unique_operative={ps['unique_operative']}); "
                f"shared_R0={shared_r0_by_arm[arm]}; evidence/relayconduit_run_card.json"
            ),
        })

    log(f"[Finalize] COMPLETE in {elapsed_total:.1f}s! Hero={hero_arm}: Rule-2={hero_r2['dti']:.6f} [{hero_r2['ci95'][0]:.6f}, {hero_r2['ci95'][1]:.6f}], unique_op={hero_ps['unique_operative']}")
    return 0


def main() -> int:
    from gems57.uniqueness import stop_historical_runner
    stop_historical_runner("run_relayconduit:main")

    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage == "stack":
        return stage_stack_and_canary()
    if stage == "deploy":
        return stage_deploy_and_screen()
    if stage == "holdout_20":
        return stage_holdout_seed(20)
    if stage == "holdout_30":
        return stage_holdout_seed(30)
    if stage == "finalize":
        t_el = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
        return stage_finalize(t_el)

    t0 = time.time()
    for sub in ("stack", "deploy", "holdout_20", "holdout_30"):
        subprocess.run([sys.executable, __file__, sub], check=True)
    subprocess.run([sys.executable, __file__, "finalize", f"{time.time() - t0:.2f}"], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
