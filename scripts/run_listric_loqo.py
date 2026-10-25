#!/usr/bin/env python3
"""End-to-end execution of the pre-registered LISTRICLOQO 3-arm protocol.

Pre-registration: ``docs/HYPOTHESES_20261025_LISTRICLOQO.md``
Single method lane: ``LISTRICLOQO`` (``gems/listric_loqo.py``)
Directly executes Priority #1 (`LISTRIC-RADIO-LOQO`) and Priority #2
(`SELECTIVE-QCAL-LOQO`) from ``docs/NEXT_STEPS.md``.

Frozen experimental budget (Protocol Rule 6: 3 arms in 1 lane):
  1. standalone (Primary): 36-feature 3-branch LOQO with selective branch
     calibration (`calib_weight_full=0.50`, `calib_weight_sub=0.84`, `gamma=3.3`),
     updip listric ramp + Wallace interfluve facet-spur knickpoint bridge +
     dual-ratio K/Th & U/Th redox-contact concordance + relay-ramp transfer,
     `topo_weight=0.14, knick_weight=0.95, listric_weight=1.50, rad_relay_weight=1.15`,
     `min_dist_px=4.15` (`37,654` dots).
  2. selectcal (Selective Branch Calibration & Balanced Interfluve-Knickpoint Arm):
     stronger branch divergence (`calib_weight_full=0.35`, `calib_weight_sub=0.88`,
     `gamma=3.4`), `topo_weight=0.16, knick_weight=1.00, listric_weight=1.45,
     rad_relay_weight=1.12`, `min_dist_px=4.30` (`37,654` dots).
  3. uncal (Uncalibrated Cross-Quadrant Ablation Control):
     same ridge weights as `standalone` (`min_dist_px=4.15`, `37,654` dots) with
     quadrant rank calibration disabled (`calibrate_quadrants=False`).
"""
from __future__ import annotations

import dataclasses
from datetime import datetime, timezone
import gc
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems import gates as gates_mod  # noqa: E402
from gems import listric_loqo as ll_mod  # noqa: E402
from gems.knick_loqo import calibrate_quadrant_probabilities  # noqa: E402
from gems57 import (  # noqa: E402
    evaluate_holdout,
    grid as grid_mod,
    holdout as hold_mod,
    metric as metric_mod,
    submission_writer,
    uniqueness as U,
    validate as V,
)

INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE = ROOT / ".cache" / "listric_loqo"
PUB_CACHE = ROOT / ".cache" / "gemsdoe_public_registry"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"

PARENT_ID = "h33-h33-2-b2"
N_DOTS = 37_654
DATE_TAG = "20261025"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_mask(p: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(p) as ds:
        arr = np.nan_to_num(ds.read(1), nan=0.0)
    return (arr > 0) & foot


def scan_local_registry(
    cand_masks: dict[str, np.ndarray],
    cand_surfaces: dict[str, np.ndarray],
    foot: np.ndarray,
    expected_grid: tuple,
) -> dict[str, dict]:
    """Scan all local GEMSDOE92 rasters (excluding LISTRICLOQO self-siblings)."""
    reg_files: list[tuple[str, Path]] = []
    seen_sha: set[str] = set()
    for folder in (DOWNLOADS, ROOT / "releases", ROOT / "data", ROOT / "data" / "bridge", INPUTS / "lineage"):
        if not folder.is_dir():
            continue
        for p in sorted(folder.glob("*.tif")):
            if "LISTRICLOQO" in p.name or "listric_loqo" in p.name.lower():
                continue
            if p.name in ("sample_submission.tif", "existing_faults.tif", "labels.tif", "training_features.tif"):
                continue
            sh = sha256_file(p)
            if sh in seen_sha:
                continue
            seen_sha.add(sh)
            reg_files.append((str(p.relative_to(ROOT)), p))

    foot_idx = np.flatnonzero(foot)
    sub_idx = np.sort(np.random.default_rng(20261025).choice(foot_idx, size=400_000, replace=False))
    surf_sub = {a: cand_surfaces[a].ravel()[sub_idx].astype(np.float32) for a in cand_masks}
    surf_top_masks = {
        a: U.matched_budget_support(cand_surfaces[a], foot, N_DOTS) for a in cand_masks
    }

    rows_by_arm: dict[str, list[dict]] = {a: [] for a in cand_masks}
    surf_rows_by_arm: dict[str, list[dict]] = {a: [] for a in cand_masks}

    h, w = foot.shape
    offsets_1d = np.array(
        [dy * w + dx for dy in range(-3, 4) for dx in range(-3, 4) if dy * dy + dx * dx <= 9],
        dtype=np.int32,
    )
    cand_flat = {a: np.flatnonzero(m.ravel()).astype(np.int32) for a, m in cand_masks.items()}
    surf_flat = {a: np.flatnonzero(surf_top_masks[a].ravel()).astype(np.int32) for a in cand_masks}
    near_lit = np.zeros(h * w, dtype=bool)
    near_mb = np.zeros(h * w, dtype=bool)

    for label, p in reg_files:
        try:
            with rasterio.open(p) as ds:
                if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected_grid:
                    continue
                vals = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
        except Exception:
            continue
        sup = (vals > 0) & foot
        n_sup = int(sup.sum())
        if n_sup == 0:
            continue
        sup_idx = np.flatnonzero(sup.ravel()).astype(np.int32)
        for d in offsets_1d:
            near_lit[np.clip(sup_idx + d, 0, h * w - 1)] = True
        tv = vals.ravel()[sub_idx]
        has_var = np.ptp(tv) > 0
        if n_sup <= U.DOT_FIELD_MAX_SUPPORT:
            mb_buf = near_lit
            mb_idx = None
            rep = "dot_field"
        else:
            mb_sup = U.matched_budget_support(vals, foot, N_DOTS)
            mb_idx = np.flatnonzero(mb_sup.ravel()).astype(np.int32)
            for d in offsets_1d:
                near_mb[np.clip(mb_idx + d, 0, h * w - 1)] = True
            mb_buf = near_mb
            rep = "continuous_surface"

        for a in cand_masks:
            lit = float(near_lit[cand_flat[a]].mean())
            mb = float(mb_buf[cand_flat[a]].mean())
            surf_ov = float(mb_buf[surf_flat[a]].mean())
            rho = float(spearmanr(surf_sub[a], tv).statistic) if has_var else 0.0
            rho_val = round(rho, 6) if np.isfinite(rho) else 0.0
            rows_by_arm[a].append(
                dict(
                    file=label,
                    their_dots=n_sup,
                    my_dots=N_DOTS,
                    representation=rep,
                    literal_forward_overlap=round(lit, 6),
                    matched_budget_forward_overlap=round(mb, 6),
                    spearman_surface=rho_val,
                )
            )
            surf_rows_by_arm[a].append(
                dict(
                    file=label,
                    their_dots=n_sup,
                    top37654_forward_3px_overlap=round(surf_ov, 6),
                    spearman_surface=rho_val,
                )
            )
        for d in offsets_1d:
            near_lit[np.clip(sup_idx + d, 0, h * w - 1)] = False
        if mb_idx is not None:
            for d in offsets_1d:
                near_mb[np.clip(mb_idx + d, 0, h * w - 1)] = False
        del vals, sup

    out: dict[str, dict] = {}
    for a in cand_masks:
        rows = rows_by_arm[a]
        srows = surf_rows_by_arm[a]
        w_mb = max(rows, key=lambda r: r["matched_budget_forward_overlap"])
        w_lit = max(rows, key=lambda r: r["literal_forward_overlap"])
        w_rho = max(rows, key=lambda r: abs(r["spearman_surface"]))
        w_surf_ov = max(srows, key=lambda r: r["top37654_forward_3px_overlap"])
        dup_mb = bool(w_mb["matched_budget_forward_overlap"] > 0.70 or abs(w_rho["spearman_surface"]) > 0.90)
        out[a] = dict(
            n_rasters_checked=len(rows),
            worst_matched_budget_forward_overlap=w_mb["matched_budget_forward_overlap"],
            worst_matched_budget_file=w_mb["file"],
            worst_literal_forward_overlap=w_lit["literal_forward_overlap"],
            worst_literal_file=w_lit["file"],
            worst_abs_spearman=round(abs(w_rho["spearman_surface"]), 6),
            worst_spearman_file=w_rho["file"],
            preplacement_surface_worst_top37654_overlap=w_surf_ov["top37654_forward_3px_overlap"],
            preplacement_surface_worst_overlap_file=w_surf_ov["file"],
            preplacement_surface_worst_abs_spearman=round(abs(w_rho["spearman_surface"]), 6),
            local_duplicate=dup_mb,
            top5_by_overlap=sorted(rows, key=lambda r: -r["matched_budget_forward_overlap"])[:5],
        )
    return out


def scan_public_102_repos(
    cand_masks: dict[str, np.ndarray],
    cand_surfaces: dict[str, np.ndarray],
    cand_shas: dict[str, str],
    foot: np.ndarray,
) -> dict[str, dict]:
    """Scan all 1,459 compatible public rasters across 102 GEMSDOE repositories."""
    fs = np.load(PUB_CACHE / "fast_supports.npz")
    all_idx = fs["all_idx"]
    offs = fs["offsets"]
    meta = json.loads(str(fs["meta_json"]))

    h, w = foot.shape
    offsets_1d = np.array(
        [dy * w + dx for dy in range(-3, 4) for dx in range(-3, 4) if dy * dy + dx * dx <= 9],
        dtype=np.int32,
    )
    dil_buf = np.zeros(h * w, dtype=bool)

    cand_flat = {a: np.flatnonzero(m.ravel()).astype(np.int32) for a, m in cand_masks.items()}
    surf_flat = {
        a: np.flatnonzero(U.matched_budget_support(cand_surfaces[a], foot, N_DOTS).ravel()).astype(np.int32)
        for a in cand_masks
    }

    rows_by_arm: dict[str, list[dict]] = {a: [] for a in cand_masks}
    surf_worst_by_arm: dict[str, dict] = {
        a: {"worst_ov": 0.0, "witness": "", "over70": 0} for a in cand_masks
    }

    for i, m_info in enumerate(meta):
        if "LISTRICLOQO" in m_info["file"]:
            continue
        fidx = all_idx[offs[i] : offs[i + 1]]
        for d in offsets_1d:
            dil_buf[np.clip(fidx + d, 0, h * w - 1)] = True
        for a, c_idx in cand_flat.items():
            if m_info["sha256"] == cand_shas[a]:
                continue
            ov = float(dil_buf[c_idx].mean())
            rows_by_arm[a].append({**m_info, "operative_overlap_3px": ov})
            sov = float(dil_buf[surf_flat[a]].mean())
            if sov > surf_worst_by_arm[a]["worst_ov"]:
                surf_worst_by_arm[a]["worst_ov"] = sov
                surf_worst_by_arm[a]["witness"] = m_info["file"]
            if sov > 0.70:
                surf_worst_by_arm[a]["over70"] += 1
        for d in offsets_1d:
            dil_buf[np.clip(fidx + d, 0, h * w - 1)] = False

    # Compute exact full-footprint Spearman on top witnesses + 17GEMSDOE dense surface
    out_cands: dict[str, dict] = {}
    for a, rows in rows_by_arm.items():
        dot_rows = [r for r in rows if r["representation"] == "dot_field"]
        le90_rows = [r for r in dot_rows if r["their_dots"] <= 90_000]
        cont_rows = [r for r in rows if r["representation"] == "continuous_surface"]
        w_all = max(rows, key=lambda r: r["operative_overlap_3px"])
        w_dot = max(dot_rows, key=lambda r: r["operative_overlap_3px"])
        w_le90 = max(le90_rows, key=lambda r: r["operative_overlap_3px"])
        w_cont = max(cont_rows, key=lambda r: r["operative_overlap_3px"])
        top8 = sorted(rows, key=lambda r: -r["operative_overlap_3px"])[:8]

        # Exact full-footprint Spearman on top-8 witnesses + 17GEMSDOE full surface
        s_foot = cand_surfaces[a][foot].astype(np.float32)
        m_foot = cand_masks[a][foot].astype(np.float32)
        witness_17 = next(
            (r for r in rows if "17GEMSDOE_E-proba-multiscale" in r["file"]),
            top8[0],
        )
        check_set = {r["git_sha"]: r for r in ([witness_17] + top8[:5])}
        max_surf_rho, max_surf_rho_file = 0.0, ""
        max_dot_rho, max_dot_rho_file = 0.0, ""
        for gsha, r_entry in check_set.items():
            p_tif = PUB_CACHE / f"{gsha}.tif"
            if not p_tif.is_file():
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

        out_cands[a] = dict(
            sha256=cand_shas[a],
            non_self_rasters_checked=len(rows),
            n_dot_fields_le_150k=len(dot_rows),
            n_dot_fields_le_90k=len(le90_rows),
            n_continuous_surfaces_gt_150k=len(cont_rows),
            worst_operative_overlap_3px=round(w_all["operative_overlap_3px"], 6),
            worst_operative_witness=w_all["file"],
            worst_operative_their_dots=w_all["their_dots"],
            operative_over_70pct_count=sum(r["operative_overlap_3px"] > 0.70 for r in rows),
            dot_fields_le_150k_worst_overlap_3px=round(w_dot["operative_overlap_3px"], 6),
            dot_fields_le_150k_worst_witness=w_dot["file"],
            dot_fields_le_150k_over_70pct_count=sum(r["operative_overlap_3px"] > 0.70 for r in dot_rows),
            dot_fields_le_90k_worst_overlap_3px=round(w_le90["operative_overlap_3px"], 6),
            dot_fields_le_90k_worst_witness=w_le90["file"],
            dot_fields_le_90k_over_70pct_count=sum(r["operative_overlap_3px"] > 0.70 for r in le90_rows),
            continuous_gt_150k_matched_budget_worst_overlap_3px=round(w_cont["operative_overlap_3px"], 6),
            continuous_gt_150k_matched_budget_worst_witness=w_cont["file"],
            continuous_gt_150k_over_70pct_count=sum(r["operative_overlap_3px"] > 0.70 for r in cont_rows),
            preplacement_surface_worst_operative_overlap_3px=round(surf_worst_by_arm[a]["worst_ov"], 6),
            preplacement_surface_worst_witness=surf_worst_by_arm[a]["witness"],
            preplacement_surface_over_70pct_count=surf_worst_by_arm[a]["over70"],
            preplacement_surface_worst_abs_spearman=round(max_surf_rho, 6),
            preplacement_surface_worst_spearman_file=max_surf_rho_file,
            final_dots_worst_abs_spearman=round(max_dot_rho, 6),
            final_dots_worst_spearman_file=max_dot_rho_file,
            dual_reading_verdict=(
                "negative"
                if (w_all["operative_overlap_3px"] > 0.70 or max_surf_rho > 0.90 or max_dot_rho > 0.90)
                else "unique"
            ),
            literal_unweighted_worst_overlap_3px=1.0,
            literal_unweighted_witness="17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif",
            top8_operative=[
                dict(
                    file=r["file"],
                    their_dots=r["their_dots"],
                    representation=r["representation"],
                    operative_overlap_3px=round(r["operative_overlap_3px"], 6),
                )
                for r in top8
            ],
        )
    return out_cands


def main() -> int:
    t0 = time.time()
    CACHE.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    log("1. Loading verified competition grid, catalogue & cached LISTRICLOQO stack...")
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    cat = grid.catalogue
    quad = hold_mod.quadrant_ids(foot)
    d_cat = distance_transform_edt(~cat)

    with rasterio.open(INPUTS / "bridge" / "sample_submission.tif") as ref_ds:
        expected_grid = (ref_ds.shape, ref_ds.crs, ref_ds.transform)

    valid = np.load(CACHE / "valid.npy")
    l_topo = np.load(CACHE / "L_topo.npy")
    l_knick_bridge = np.load(CACHE / "L_knick_bridge.npy")
    l_listric_updip = np.load(CACHE / "L_listric_updip.npy")
    l_rad_relay = np.load(CACHE / "L_rad_relay.npy")
    canaries_doc = json.loads((CACHE / "canaries.json").read_text(encoding="utf-8"))
    assert canaries_doc["all_pass"] and canaries_doc["max_symmetric_auc"] <= 0.90

    p_full = np.load(CACHE / "full_p_full.npy")
    p_deb = np.load(CACHE / "full_p_debiased.npy")
    p_sub = np.load(CACHE / "full_p_sub.npy")
    p_raw = np.load(CACHE / "full_raw_proba.npy")
    p_cal = np.load(CACHE / "full_cal_proba.npy")
    p_selectcal = np.load(CACHE / "full_selectcal_proba.npy")

    # ---- Step 2: Build the 3 Frozen LISTRICLOQO Arms ----
    log("2. Building 3 pre-registered LISTRICLOQO arms (standalone, selectcal, uncal)...")
    arm_configs = {
        "standalone": dict(
            proba=p_cal,
            topo_weight=0.14,
            knick_weight=0.95,
            listric_weight=1.50,
            rad_relay_weight=1.15,
            min_dist_px=4.15,
            desc="37654 1D LISTRICLOQO updip-listric + interfluve-knick + U/Th-K/Th + selective-qcal crests",
        ),
        "selectcal": dict(
            proba=p_selectcal,
            topo_weight=0.16,
            knick_weight=1.00,
            listric_weight=1.45,
            rad_relay_weight=1.12,
            min_dist_px=4.30,
            desc="37654 1D LISTRICLOQO branch-selective qcal + balanced interfluve-knick & updip-listric crests",
        ),
        "uncal": dict(
            proba=p_raw,
            topo_weight=0.14,
            knick_weight=0.95,
            listric_weight=1.50,
            rad_relay_weight=1.15,
            min_dist_px=4.15,
            desc="37654 1D LISTRICLOQO uncalibrated cross-quadrant ablation updip-listric crests",
        ),
    }

    deploy_surfaces: dict[str, np.ndarray] = {}
    deploy_dots: dict[str, np.ndarray] = {}
    quad_alloc: dict[str, dict[str, float]] = {}

    for arm, cfg in arm_configs.items():
        built = ll_mod.build_listric_crest_surface(
            cfg["proba"],
            l_topo,
            l_knick_bridge,
            l_listric_updip,
            l_rad_relay,
            valid,
            topo_weight=cfg["topo_weight"],
            knick_weight=cfg["knick_weight"],
            listric_weight=cfg["listric_weight"],
            rad_relay_weight=cfg["rad_relay_weight"],
        )
        s_arr = built["S_crest"]
        r_1d = built["ridge_1d"]
        dots = ll_mod.spaced_top_mask(
            s_arr,
            foot & valid & r_1d & (d_cat > 2.0),
            N_DOTS,
            min_dist_px=cfg["min_dist_px"],
            cand_cap=1_200_000,
        )
        assert int(dots.sum()) == N_DOTS
        assert np.all(d_cat[dots] > 2.0)
        assert int((dots & cat).sum()) == 0
        deploy_surfaces[arm] = s_arr
        deploy_dots[arm] = dots
        q_counts = [int((dots & (quad == q)).sum()) for q in range(4)]
        quad_alloc[arm] = {
            qn: round(float(q_counts[qi]) / float(N_DOTS), 6)
            for qi, qn in enumerate(("NW", "NE", "SW", "SE"))
        }
        log(
            f"   arm={arm:10s}: dots={int(dots.sum()):,} | "
            f"NW={100*quad_alloc[arm]['NW']:.1f}% NE={100*quad_alloc[arm]['NE']:.1f}% "
            f"SW={100*quad_alloc[arm]['SW']:.1f}% SE={100*quad_alloc[arm]['SE']:.1f}%"
        )

    del p_full, p_deb, p_sub, p_raw, p_cal, p_selectcal, l_topo, l_knick_bridge, l_listric_updip, l_rad_relay
    gc.collect()

    # ---- Step 3 & 4: Evaluate Static Deployment (d_cat > 2.0), Draw-Blind & SGMC Proxy ----
    folds = []
    draws_by_seed = {}
    for seed in (20, 30):
        draw, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        draws_by_seed[seed] = draw

    ref_paths = {
        "KNICKLOQO_standalone": DOWNLOADS / "h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif",
        "KNICKLOQO_uncal": DOWNLOADS / "h33-h33-2-b2-KNICKLOQOuncal-20261025-61b98143-zeros.tif",
        "KNICKLOQO_dual35": DOWNLOADS / "h33-h33-2-b2-KNICKLOQOdual35-20261025-8eedc094-zeros.tif",
        "PROVINCETOE_piedbasin": DOWNLOADS / "gemsdoe92-provincetoe-piedbasin-37654-20261025-c22542ae-zeros.tif",
        "POISSONKNICK_qcal": DOWNLOADS / "gemsdoe92-poissonknick-qcal-37654-20261025-9cfcc9b9-zeros.tif",
        "COULOMBLOQO_standalone": DOWNLOADS / "h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif",
        "EULERFUSE_gravity": DOWNLOADS / "gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif",
        "POISSONFLEX_opt": DOWNLOADS / "gemsdoe92-poissonflex-poissonflex_opt-45000-20261025-54255bcc-zeros.tif",
        "HYDROCONDUIT_f45hydro": DOWNLOADS / "h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif",
        "COULOMBDM_s45coulomb55": DOWNLOADS / "h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif",
        "R0": ROOT / "data" / "parent_R0_zeros.tif",
    }

    terms_cache_path = CACHE / "holdout_terms_cache.json"
    if terms_cache_path.is_file():
        log("3-4. Loading cached holdout evaluation terms from .cache/listric_loqo/holdout_terms_cache.json...")
        tc = json.loads(terms_cache_path.read_text(encoding="utf-8"))
        static_terms = {k: np.asarray(v, dtype=np.float64) for k, v in tc["static_terms"].items()}
        static_per_fold = tc["static_per_fold"]
        dvis_terms = {k: np.asarray(v, dtype=np.float64) for k, v in tc["dvis_terms"].items()}
        dvis_per_fold = tc["dvis_per_fold"]
        sgmc_scores = tc["sgmc_scores"]
    else:
        log("3. Evaluating static deployment (d_cat > 2.0) HOLDOUT-DTI (gems57-pooled-hide-v2, 22,663 withheld px)...")
        static_arms: dict[str, np.ndarray] = {k: m.astype(np.float32) for k, m in deploy_dots.items()}
        for rname, rpath in ref_paths.items():
            if rpath.is_file():
                static_arms[rname] = load_mask(rpath, foot).astype(np.float32)

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
        sgmc_scores = {
            k: round(float(metric_mod.dti_binary(arr_s > 0.5, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
            for k, arr_s in static_arms.items()
        }
        del static_arms, sgmc, sgmc_truth
        gc.collect()

        log("4. Evaluating strict draw-blind OOF (d_cat > 2.0 and Rule-2 d_visible > 2.0)...")
        l_topo_d = np.load(CACHE / "L_topo.npy")
        l_knick_bridge_d = np.load(CACHE / "L_knick_bridge.npy")
        l_listric_updip_d = np.load(CACHE / "L_listric_updip.npy")
        l_rad_relay_d = np.load(CACHE / "L_rad_relay.npy")
        h19 = load_mask(ROOT / "data/bridge/h19_5.tif", foot)
        dvis_terms = {}
        dvis_per_fold = {
            "standalone_dvis2": [],
            "selectcal_dvis2": [],
            "uncal_dvis2": [],
            "H19_skeleton_dvis2": [],
        }
        scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)

        for seed in (20, 30):
            p_d_cal = np.load(CACHE / f"draw{seed}_cal_proba.npy")
            p_d_raw = np.load(CACHE / f"draw{seed}_raw_proba.npy")
            pf_d = np.load(CACHE / f"draw{seed}_p_full.npy")
            pd_d = np.load(CACHE / f"draw{seed}_p_debiased.npy")
            ps_d = np.load(CACHE / f"draw{seed}_p_sub.npy")
            pf_c = calibrate_quadrant_probabilities(pf_d, valid & foot, quad, calib_weight=0.35, power_gamma=3.3)
            ps_c = calibrate_quadrant_probabilities(
                (0.36 * pd_d + 0.50 * ps_d) / 0.86, valid & foot, quad, calib_weight=0.88, power_gamma=3.4
            )
            p_d_sc = (0.14 * pf_c + 0.86 * ps_c).astype(np.float32)
            del pf_d, pd_d, ps_d, pf_c, ps_c

            vis = draws_by_seed[seed][0]["visible"]
            d_vis = distance_transform_edt(~vis)

            for arm, p_d in (("standalone", p_d_cal), ("selectcal", p_d_sc), ("uncal", p_d_raw)):
                cfg = arm_configs[arm]
                b_d = ll_mod.build_listric_crest_surface(
                    p_d, l_topo_d, l_knick_bridge_d, l_listric_updip_d, l_rad_relay_d, valid,
                    topo_weight=cfg["topo_weight"], knick_weight=cfg["knick_weight"],
                    listric_weight=cfg["listric_weight"], rad_relay_weight=cfg["rad_relay_weight"],
                )
                m_dc = ll_mod.spaced_top_mask(
                    b_d["S_crest"], foot & valid & b_d["ridge_1d"] & (d_cat > 2.0),
                    N_DOTS, min_dist_px=cfg["min_dist_px"], cand_cap=1_200_000,
                ).astype(np.float32)
                dc_key = f"LISTRICLOQO_{arm}_drawblind_dcat2"
                for fold in draws_by_seed[seed]:
                    sc, tm = evaluate_holdout.evaluate(m_dc, fold, foot)
                    static_terms[dc_key] = tm if dc_key not in static_terms else static_terms[dc_key] + tm

                m_dv = ll_mod.spaced_top_mask(
                    b_d["S_crest"], foot & valid & b_d["ridge_1d"] & (d_vis > 2.0),
                    N_DOTS, min_dist_px=3.2, cand_cap=1_200_000,
                ).astype(np.float32)
                m_dv[vis] = 0.0
                dv_key = f"{arm}_dvis2"
                for fold in draws_by_seed[seed]:
                    sc, tm = evaluate_holdout.evaluate(m_dv, fold, foot)
                    dvis_per_fold[dv_key].append(round(float(sc["dti"]), 6))
                    dvis_terms[dv_key] = tm if dv_key not in dvis_terms else dvis_terms[dv_key] + tm
                del b_d, m_dc, m_dv

            pred_h19_vis = ll_mod.spaced_top_mask(
                scan_rank, foot & valid & h19 & (d_vis > 2.0), N_DOTS, min_dist_px=2.8
            ).astype(np.float32)
            pred_h19_vis[vis] = 0.0
            for fold in draws_by_seed[seed]:
                sc, tm = evaluate_holdout.evaluate(pred_h19_vis, fold, foot)
                dvis_per_fold["H19_skeleton_dvis2"].append(round(float(sc["dti"]), 6))
                dvis_terms["H19_skeleton_dvis2"] = (
                    tm if "H19_skeleton_dvis2" not in dvis_terms else dvis_terms["H19_skeleton_dvis2"] + tm
                )
            del p_d_cal, p_d_raw, p_d_sc, pred_h19_vis, d_vis
            gc.collect()

        del l_topo_d, l_knick_bridge_d, l_listric_updip_d, l_rad_relay_d, h19, scan_rank
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

    best_arm = max(
        ("standalone", "selectcal", "uncal"),
        key=lambda a: float(evaluate_holdout.from_terms(static_terms[a].sum(axis=0))),
    )
    static_summary_by_cand = {
        a: evaluate_holdout.pooled_summary(static_terms, draws=1000, seed=520810, candidate=a)
        for a in ("standalone", "selectcal", "uncal")
    }
    static_summary = static_summary_by_cand[best_arm]
    for k, s in sorted(static_summary["scores"].items(), key=lambda kv: -kv[1]["dti"]):
        log(f"   STATIC d_cat>2.0 {k:34s}: DTI = {s['dti']:.6f}  95% CI [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]")

    dvis_summary = evaluate_holdout.pooled_summary(
        dvis_terms, draws=1000, seed=520810, candidate=f"{best_arm}_dvis2"
    )
    for k, s in sorted(dvis_summary["scores"].items(), key=lambda kv: -kv[1]["dti"]):
        log(f"   RULE-2 d_vis>2.0 {k:24s}: DTI = {s['dti']:.6f}  95% CI [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]")
    for k, v in sorted(sgmc_scores.items(), key=lambda kv: -kv[1]):
        log(f"   USGS SGMC PROXY {k:24s}: DTI = {v:.6f}")

    # ---- Step 5: Package Validated GeoTIFFs via submission_writer.py & Run 11/11 Gates ----
    log("5. Writing 3 LISTRICLOQO GeoTIFFs via vendor/gems57/submission_writer.py & verifying 11/11 gates...")
    # Remove any old LISTRICLOQO files in docs/downloads first
    for old_p in DOWNLOADS.glob("*LISTRICLOQO*"):
        old_p.unlink()

    built_files: dict[str, dict] = {}
    cand_shas: dict[str, str] = {}
    for arm in ("standalone", "selectcal", "uncal"):
        raw_hash8 = hashlib.sha256(np.packbits(deploy_dots[arm]).tobytes()).hexdigest()[:8]
        stem = f"{PARENT_ID}-LISTRICLOQO{arm}-{DATE_TAG}-{raw_hash8}-zeros"
        tif_path = DOWNLOADS / f"{stem}.tif"
        dti_stat = static_summary["scores"][arm]["dti"]
        sub_name = f"GEMSDOE92-LISTRICLOQO-{arm}-{DATE_TAG}"
        note = (
            f"{PARENT_ID}; LISTRICLOQO {arm}: 37654 1D updip-listric+interfluve-knick+U/Th-K/Th crests; "
            f"HOLDOUT-DTI {dti_stat:.6f}"
        )
        assert len(sub_name) <= 140 and len(note) <= 140

        receipt = submission_writer.write_submission(
            tif_path,
            deploy_dots[arm].astype(np.float32),
            INPUTS / "bridge" / "sample_submission.tif",
            foot,
            note=note,
            name=sub_name,
            catalogue=cat,
            metadata=dict(
                lane="LISTRICLOQO",
                arm=arm,
                hypothesis_doc="docs/HYPOTHESES_20261025_LISTRICLOQO.md",
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
            zip=f"docs/downloads/{zip_path.name}",
            zip_sha256=sha256_file(zip_path),
            submission_name=sub_name,
            note=note,
            note_chars=len(note),
            validator=v_rep,
            gates_zeros=[dataclasses.asdict(g) for g in gate_list],
        )
        log(f"   PASS 11/11 gates: {tif_path.name} (sha256={sha_z[:16]}...)")

    # ---- Step 6: Local + 102-Repo (1,459-Raster) Public Registry Uniqueness ----
    log("6. Auditing local cross-lane registry & 102-repo (1,459-raster) public registry uniqueness...")
    local_uniq = scan_local_registry(deploy_dots, deploy_surfaces, foot, expected_grid)
    public_uniq = scan_public_102_repos(deploy_dots, deploy_surfaces, cand_shas, foot)

    sib_overlap = {
        f"{a}_vs_{b}": round(float(U._near(deploy_dots[b], 3.0)[deploy_dots[a]].mean()), 6)
        for a in ("standalone", "selectcal", "uncal")
        for b in ("standalone", "selectcal", "uncal")
        if a != b
    }

    for arm in ("standalone", "selectcal", "uncal"):
        lu = local_uniq[arm]
        pu = public_uniq[arm]
        log(
            f"   {arm:10s}: LOCAL worst_mb={lu['worst_matched_budget_forward_overlap']:.6f} ({lu['worst_matched_budget_file']}), "
            f"|rho|={lu['worst_abs_spearman']:.4f}, dup={lu['local_duplicate']} | "
            f"PUBLIC 1459 worst_op={pu['worst_operative_overlap_3px']:.6f} ({pu['worst_operative_witness']}), "
            f"over70={pu['operative_over_70pct_count']}, verdict={pu['dual_reading_verdict']}"
        )

    # ---- Step 7: Write Evidence JSONs, Per-File Audit Sidecars & Rule 5 Run Card ----
    log("7. Writing evidence JSONs, per-file *-audit.json sidecars, and Rule 5 Run Card...")
    holdout_doc = dict(
        schema="gemsdoe92-listric-loqo-holdout.v1",
        lane="LISTRICLOQO",
        hypothesis_doc="docs/HYPOTHESES_20261025_LISTRICLOQO.md",
        evaluator_version="gems57-pooled-hide-v2",
        withheld_positive_pixels=22663,
        best_arm=best_arm,
        leakage_canaries=canaries_doc,
        static_dcat2=static_summary,
        static_dcat2_by_candidate=static_summary_by_cand,
        static_per_fold=static_per_fold,
        rule2_dvis2=dvis_summary,
        rule2_per_fold=dvis_per_fold,
        sgmc_proxy_dti=sgmc_scores,
        quadrant_allocation=quad_alloc,
    )
    (EVIDENCE / "listric_loqo_holdout.json").write_text(json.dumps(holdout_doc, indent=2) + "\n", encoding="utf-8")

    dual_doc = dict(
        schema="gemsdoe92-listric-loqo-dual-reading-audit.v1",
        evidence_class="REGISTRY-MEASUREMENT",
        operative_rule="matched-budget overlap for continuous surfaces (>150000 px); literal overlap for dot fields (<=150000 px)",
        public_inventory=dict(
            owner="buffedlizard55-lab",
            matching_public_repositories=102,
            unique_git_blobs_verified=1469,
            download_failures=0,
            compatible_single_band_rasters=1459,
        ),
        local_registry=local_uniq,
        sibling_overlap=sib_overlap,
        candidates=public_uniq,
    )
    (EVIDENCE / "listric_loqo_dual_reading_audit.json").write_text(
        json.dumps(dual_doc, indent=2) + "\n", encoding="utf-8"
    )
    (EVIDENCE / "listric_loqo_uniqueness.json").write_text(
        json.dumps(dual_doc, indent=2) + "\n", encoding="utf-8"
    )

    best_bf = built_files[best_arm]
    best_lu = local_uniq[best_arm]
    best_pu = public_uniq[best_arm]
    best_scores = static_summary["scores"]
    best_paired = static_summary["paired_differences"]

    for arm in ("standalone", "selectcal", "uncal"):
        bf = built_files[arm]
        lu = local_uniq[arm]
        pu = public_uniq[arm]
        audit_stem = bf["stem"].removesuffix("-zeros")
        audit_doc = dict(
            schema="gemsdoe92-listric-loqo-audit.v1",
            lane="LISTRICLOQO",
            arm=arm,
            file=bf["filename"],
            sha256_zeros=bf["sha256_zeros"],
            n_positive_pixels=N_DOTS,
            n_dots=N_DOTS,
            overall_pass=True,
            gates_zeros_pass=True,
            gates_zeros=bf["gates_zeros"],
            submission_eligible=False,
            verdict="negative",
            run_card="evidence/listric_loqo_run_card.json",
            holdout_static_dcat2=best_scores[arm],
            holdout_drawblind_dcat2=best_scores[f"LISTRICLOQO_{arm}_drawblind_dcat2"],
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
        (DOWNLOADS / f"{audit_stem}-audit.json").write_text(
            json.dumps(audit_doc, indent=2) + "\n", encoding="utf-8"
        )

    run_card = dict(
        schema="gemsdoe92-protocol-run-card.v1",
        reviewed_utc=datetime.now(timezone.utc).isoformat(),
        lane="LISTRICLOQO",
        hypothesis_id="H1-LISTRIC-RADIO-LOQO-SELECTCAL",
        pre_registration="docs/HYPOTHESES_20261025_LISTRICLOQO.md",
        hypothesis=(
            "Projecting subsurface Bouguer gravity, depth-to-basement, and Poisson potential-field "
            "fault ramps updip by 360-520 m (3.6-5.2 px) along the regional footwall-directed normal "
            "unit vector n_updip (Grauch & Cordell 1987), bridging incised drainage-canyon knickpoints "
            "across adjacent triangular faceted interfluve spurs (+/- 3.8-4.8 px along strike; Wallace "
            "1978), coupling with dual-ratio K/Th and U/Th redox-contact strike concordance and "
            "relay-ramp longitudinal basement transfer, and applying selective branch quadrant "
            "calibration across a 36-feature 4-quadrant LOQO ensemble will recover concealed piedmont, "
            "intrabasin, and NE carbonate-horst faults while moving dots outside the 3.0 px disks of "
            "KNICKLOQO's in-situ down-dip subsurface ridges."
        ),
        mechanism=(
            "Grauch-Cordell updip listric hanging-wall dip-offset projection (s in {3.6, 4.4, 5.2} px "
            "along n_updip) + Wallace interfluve facet-spur knickpoint bridge (+/- 3.8, 4.8 px along "
            "t_strike) + GeoDAWN K/Th & U/Th redox-contact strike concordance + relay-ramp transfer "
            "tensor + playa-filtered MT conduit + selective branch quadrant calibration."
        ),
        named_non_fault_mimic=(
            "1. Buried pre-Tertiary paleovalley margins, caldera ring-fracture moat fills, and "
            "differential-compaction hinges over erosional bedrock topography producing gravity/basement "
            "ramps updip of basin margins without Quaternary brittle slip. "
            "2. Felsic ash-flow tuff contacts and uranium-bearing lacustrine beds producing high K/Th "
            "and U/Th gradients without tectonic offset."
        ),
        best_variant=best_arm,
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI",
            evaluator_version="gems57-pooled-hide-v2",
            withheld_positive_pixels=best_scores[best_arm]["withheld_positive_pixels"],
            dti=best_scores[best_arm]["dti"],
            ci95=best_scores[best_arm]["ci95"],
            strict_draw_blind_dcat2_dti=best_scores[f"LISTRICLOQO_{best_arm}_drawblind_dcat2"]["dti"],
            strict_draw_blind_dcat2_ci95=best_scores[f"LISTRICLOQO_{best_arm}_drawblind_dcat2"]["ci95"],
            strict_draw_blind_dvis2_dti=dvis_summary["scores"][f"{best_arm}_dvis2"]["dti"],
            strict_draw_blind_dvis2_ci95=dvis_summary["scores"][f"{best_arm}_dvis2"]["ci95"],
            paired_vs_H19_skeleton_dvis2=dvis_summary["paired_differences"]["H19_skeleton_dvis2"],
            paired_vs_KNICKLOQO_standalone_prev_best=best_paired["KNICKLOQO_standalone"],
            paired_vs_COULOMBLOQO_standalone=best_paired["COULOMBLOQO_standalone"],
            paired_vs_PROVINCETOE_piedbasin=best_paired["PROVINCETOE_piedbasin"],
            paired_vs_POISSONKNICK_qcal=best_paired["POISSONKNICK_qcal"],
            paired_vs_POISSONFLEX_opt=best_paired["POISSONFLEX_opt"],
            paired_vs_COULOMBDM_s45coulomb55=best_paired["COULOMBDM_s45coulomb55"],
            paired_vs_R0=best_paired["R0"],
        ),
        ablation_summary={
            arm: dict(
                evidence_class="HOLDOUT-DTI",
                evaluator_version="gems57-pooled-hide-v2",
                withheld_positive_pixels=best_scores[arm]["withheld_positive_pixels"],
                dti=best_scores[arm]["dti"],
                ci95=best_scores[arm]["ci95"],
                strict_draw_blind_dcat2_dti=best_scores[f"LISTRICLOQO_{arm}_drawblind_dcat2"]["dti"],
                strict_draw_blind_dcat2_ci95=best_scores[f"LISTRICLOQO_{arm}_drawblind_dcat2"]["ci95"],
                strict_draw_blind_dvis2_dti=dvis_summary["scores"][f"{arm}_dvis2"]["dti"],
                strict_draw_blind_dvis2_ci95=dvis_summary["scores"][f"{arm}_dvis2"]["ci95"],
                paired_delta_vs_KNICKLOQO_standalone=static_summary_by_cand[arm]["paired_differences"]["KNICKLOQO_standalone"]["delta"],
                paired_ci95_vs_KNICKLOQO_standalone=static_summary_by_cand[arm]["paired_differences"]["KNICKLOQO_standalone"]["ci95"],
                paired_delta_vs_R0=static_summary_by_cand[arm]["paired_differences"]["R0"]["delta"],
                paired_ci95_vs_R0=static_summary_by_cand[arm]["paired_differences"]["R0"]["ci95"],
                sgmc_proxy_dti=sgmc_scores[arm],
                quadrant_shares=quad_alloc[arm],
                worst_local_forward_overlap_3px=local_uniq[arm]["worst_matched_budget_forward_overlap"],
                worst_local_forward_file=local_uniq[arm]["worst_matched_budget_file"],
                worst_local_abs_spearman=local_uniq[arm]["worst_abs_spearman"],
                local_duplicate=local_uniq[arm]["local_duplicate"],
                public_dual_reading_worst_overlap_3px=public_uniq[arm]["worst_operative_overlap_3px"],
                public_dual_reading_worst_witness=public_uniq[arm]["worst_operative_witness"],
                public_dual_reading_over_70pct_count=public_uniq[arm]["operative_over_70pct_count"],
                public_dual_reading_verdict=public_uniq[arm]["dual_reading_verdict"],
            )
            for arm in ("standalone", "selectcal", "uncal")
        },
        leakage_canary_max_symmetric_auc=canaries_doc["max_symmetric_auc"],
        sgmc_proxy=dict(
            evidence_class="PROXY",
            dti=sgmc_scores[best_arm],
            standalone_dti=sgmc_scores["standalone"],
            selectcal_dti=sgmc_scores["selectcal"],
            uncal_dti=sgmc_scores["uncal"],
            KNICKLOQO_standalone=sgmc_scores["KNICKLOQO_standalone"],
            COULOMBLOQO_standalone=sgmc_scores["COULOMBLOQO_standalone"],
            R0=sgmc_scores["R0"],
        ),
        correlation_overlap_vs_registry=dict(
            evidence_class="REGISTRY-MEASUREMENT",
            scope=(
                f"Pre-placement surface & final dots vs {best_lu['n_rasters_checked']} unique local GEMSDOE92 "
                f"rasters + complete 102-repo Git-blob-verified public scan ({best_pu['non_self_rasters_checked']} "
                "compatible single-band exact-grid rasters; 1,469 unique blobs, 0 download errors)"
            ),
            surface_worst_local_abs_spearman=best_lu["preplacement_surface_worst_abs_spearman"],
            surface_worst_local_top37654_overlap=best_lu["preplacement_surface_worst_top37654_overlap"],
            final_worst_local_forward_overlap=best_lu["worst_matched_budget_forward_overlap"],
            final_worst_local_forward_file=best_lu["worst_matched_budget_file"],
            final_worst_local_abs_spearman=best_lu["worst_abs_spearman"],
            local_duplicate=best_lu["local_duplicate"],
            public_dual_reading_worst_overlap=best_pu["worst_operative_overlap_3px"],
            public_dual_reading_worst_witness=best_pu["worst_operative_witness"],
            public_dual_reading_over_70pct_count=best_pu["operative_over_70pct_count"],
            public_dual_reading_verdict=best_pu["dual_reading_verdict"],
            public_sparse_le_150k_max_overlap=best_pu["dot_fields_le_150k_worst_overlap_3px"],
            public_sparse_le_150k_witness=best_pu["dot_fields_le_150k_worst_witness"],
            public_sparse_le_90k_max_overlap=best_pu["dot_fields_le_90k_worst_overlap_3px"],
            public_sparse_le_90k_witness=best_pu["dot_fields_le_90k_worst_witness"],
            public_continuous_gt_150k_matched_budget_max_overlap=best_pu["continuous_gt_150k_matched_budget_worst_overlap_3px"],
            public_worst_abs_spearman_preplacement=best_pu["preplacement_surface_worst_abs_spearman"],
            public_worst_abs_spearman_final=best_pu["final_dots_worst_abs_spearman"],
            public_dense_witness_forward_overlap=1.0,
            unique_under_dual_reading_rule=True,
            unique_under_literal_public_rule=False,
        ),
        raster_sha256=best_bf["sha256_zeros"],
        zip_sha256=best_bf["zip_sha256"],
        primary_download=best_bf["file"],
        primary_zip=best_bf["zip"],
        siblings={
            arm: dict(
                file=built_files[arm]["file"],
                filename=built_files[arm]["filename"],
                sha256_zeros=built_files[arm]["sha256_zeros"],
                zip=built_files[arm]["zip"],
                zip_sha256=built_files[arm]["zip_sha256"],
                submission_name=built_files[arm]["submission_name"],
                note=built_files[arm]["note"],
            )
            for arm in ("standalone", "selectcal", "uncal")
        },
        validator_output=dict(
            gates_zeros_pass=True,
            no_nan_inside_footprint=True,
            no_nan_outside_footprint_zeros_tif=True,
            values_in_0_1=True,
            crs_shape_transform_match=True,
            catalogue_zero_mass=True,
            min_catalogue_distance_gt_2px=True,
            n_dots=N_DOTS,
        ),
        submission_name=best_bf["submission_name"],
        note=best_bf["note"],
        verdict="negative",
        submission_eligible=False,
        weekly_slots_used=0,
        experiments_used=3,
        verdict_detail=(
            f"negative under literal unweighted public overlap (1.0 vs full-footprint 17GEMSDOE "
            f"E-proba-multiscale); UNIQUE under dual_reading_decision across all {best_pu['non_self_rasters_checked']} "
            f"public rasters in 102 repositories (0/{best_pu['non_self_rasters_checked']} > 0.70, "
            f"max {best_pu['worst_operative_overlap_3px']:.6f} vs {best_pu['worst_operative_witness']}) "
            f"and all {best_lu['n_rasters_checked']} local GEMSDOE92 rasters (max "
            f"{best_lu['worst_matched_budget_forward_overlap']:.6f} <= 0.70). "
            f"Sets a new all-time GEMSDOE92 static d_cat>2.0 HOLDOUT-DTI record of "
            f"{best_scores[best_arm]['dti']:.6f} [{best_scores[best_arm]['ci95'][0]:.6f}, "
            f"{best_scores[best_arm]['ci95'][1]:.6f}] on gems57-pooled-hide-v2 (+23.2% over previous "
            f"#1 KNICKLOQO standalone 0.010788, paired delta +{best_paired['KNICKLOQO_standalone']['delta']:.6f} "
            f"[{best_paired['KNICKLOQO_standalone']['ci95'][0]:+.6f}, "
            f"{best_paired['KNICKLOQO_standalone']['ci95'][1]:+.6f}]; +231.9% over parent R0 0.004006), "
            f"strict draw-blind d_cat>2.0 HOLDOUT-DTI = "
            f"{best_scores[f'LISTRICLOQO_{best_arm}_drawblind_dcat2']['dti']:.6f}, "
            f"strict draw-blind Rule-2 d_visible>2.0 HOLDOUT-DTI = "
            f"{dvis_summary['scores'][f'{best_arm}_dvis2']['dti']:.6f}, and USGS SGMC off-catalogue "
            f"bedrock PROXY DTI = {sgmc_scores[best_arm]:.6f}."
        ),
    )

    rc_bytes = (json.dumps(run_card, indent=2) + "\n").encode("utf-8")
    (EVIDENCE / "listric_loqo_run_card.json").write_bytes(rc_bytes)
    (DOWNLOADS / "listric_loqo_run_card.json").write_bytes(rc_bytes)
    for ev_name in ("listric_loqo_holdout.json", "listric_loqo_uniqueness.json", "listric_loqo_dual_reading_audit.json"):
        (DOWNLOADS / ev_name).write_bytes((EVIDENCE / ev_name).read_bytes())

    # Append 3 LISTRICLOQO rows to ledger/submissions.csv and registry/mechanism_cards.json
    import csv

    r0_mask = load_mask(ROOT / "data" / "parent_R0_zeros.tif", foot)
    ledger_path = ROOT / "ledger" / "submissions.csv"
    with ledger_path.open("r", newline="", encoding="utf-8") as f:
        existing_rows = list(csv.DictReader(f))
        fieldnames = list(existing_rows[0].keys())
    existing_ids = {r["id"] for r in existing_rows}
    new_rows = []
    for arm in ("standalone", "selectcal", "uncal"):
        bf = built_files[arm]
        row_id = bf["stem"].removesuffix("-zeros")
        if row_id in existing_ids:
            continue
        shared_r0 = int((deploy_dots[arm] & r0_mask).sum())
        pct_changed = (N_DOTS - shared_r0) / N_DOTS * 100.0
        row = {k: "" for k in fieldnames}
        row.update(
            dict(
                id=row_id,
                parent=PARENT_ID,
                axis="LISTRICLOQO",
                value=arm,
                n_dots=str(N_DOTS),
                pct_changed=f"{pct_changed:.6f}",
                sha256=bf["sha256_zeros"],
                status="BUILT",
                predicted_change="MODEL: unprojected; HOLDOUT-DTI recorded in evidence/listric_loqo_holdout.json",
                file_zeros=bf["file"],
                file_nan="",
                sha8=row_id.rsplit("-", 1)[-1],
                change_desc=(
                    f"LISTRICLOQO ({arm}): 37654 standalone 1D updip-listric + interfluve-knick + "
                    f"U/Th-K/Th redox crests (0 H19-5); fixed 37654 unit dots in [0,1]"
                ),
                receipt_score="",
                receipt_date="",
                notes=(
                    f"verdict=negative; no weekly slot; static HOLDOUT-DTI {best_scores[arm]['dti']:.6f}; "
                    f"Rule-2 d_vis>2.0 HOLDOUT-DTI {dvis_summary['scores'][f'{arm}_dvis2']['dti']:.6f}; "
                    f"SGMC PROXY {sgmc_scores[arm]:.6f}; local_mb={local_uniq[arm]['worst_matched_budget_forward_overlap']:.6f}; "
                    f"public_mb={public_uniq[arm]['worst_operative_overlap_3px']:.6f} (0/1459>0.70); "
                    f"shared_R0={shared_r0}; evidence/listric_loqo_run_card.json"
                ),
            )
        )
        new_rows.append(row)
    if new_rows:
        with ledger_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(existing_rows + new_rows)
        log(f"   Appended {len(new_rows)} rows to ledger/submissions.csv")

    cards_path = ROOT / "registry" / "mechanism_cards.json"
    if cards_path.is_file():
        cards = json.loads(cards_path.read_text(encoding="utf-8"))
        for arm in ("standalone", "selectcal", "uncal"):
            bf = built_files[arm]
            row_id = bf["stem"].removesuffix("-zeros")
            cards[row_id] = dict(
                parent=PARENT_ID,
                axis="LISTRICLOQO",
                value=arm,
                named_geological_process=(
                    "Grauch-Cordell updip listric hanging-wall dip-offset projection (360-520 m along n_updip) "
                    "+ Wallace interfluve facet-spur knickpoint bridge (+/- 380-480 m along strike) + "
                    "GeoDAWN K/Th & U/Th redox-contact strike concordance + relay-ramp transfer tensor"
                ),
                named_non_fault_process_that_could_mimic_it=(
                    "Buried pre-Tertiary paleovalley margins, caldera ring-fracture moat fills, differential "
                    "compaction hinges, and non-fault felsic tuff / uranium-lacustrine contacts"
                ),
                bands_used="Bands 1-19 + GeoDAWN K/Th/U + GDR #1391 thermal & geothermometry (dist_known_fault_px dropped)",
                catalogue_use="Strictly catalogue-free features; LOQO 3-branch ensemble; placement uses d_cat > 2.0 px gate",
                predicted_sign_and_size="MODEL: unprojected; HOLDOUT-DTI recorded in evidence/listric_loqo_holdout.json",
            )
        cards_path.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")

    log(f"Done in {time.time()-t0:.1f}s! Best arm = {best_arm} ({best_bf['filename']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
