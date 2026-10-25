#!/usr/bin/env python3
"""Evaluate the 3 pre-registered RIEDELTENSOR variants across all holdout, proxy,
local uniqueness, and public dual-reading uniqueness instruments.

Outputs:
- ``evidence/riedel_tensor_proxy_audit.json``
- ``evidence/riedel_tensor_dual_reading_audit.json``
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

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import verify_all_manifests  # noqa: E402
from gems.riedel_tensor import build_riedel_tensor_crest_surface, spaced_top_mask  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric as gems57_metric  # noqa: E402
from screen_riedel_tensor import collect_unique_local_rasters  # noqa: E402

CACHE_DIR = ROOT / ".cache" / "gems_inputs"
NPZ_CACHE = CACHE_DIR / "riedel_tensor_cache.npz"
SCREEN_JSON = ROOT / "evidence" / "riedel_tensor_screen.json"
VARIANTS_JSON = ROOT / "evidence" / "riedel_tensor_variants.json"
OUT_JSON = ROOT / "evidence" / "riedel_tensor_proxy_audit.json"
DUAL_OUT_JSON = ROOT / "evidence" / "riedel_tensor_dual_reading_audit.json"


def load_mask(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        arr = ds.read(1)
    return (np.nan_to_num(arr, nan=0.0) > 0) & foot


def evaluate_local_uniqueness(
    cand_masks: dict[str, np.ndarray],
    foot: np.ndarray,
    local_rasters: list[tuple[str, Path]],
) -> dict[str, dict]:
    out: dict[str, dict] = {}
    n_foot = float(foot.sum())
    n_my_map = {k: float((m & foot).sum()) for k, m in cand_masks.items()}
    rows_by_cand: dict[str, list[dict]] = {k: [] for k in cand_masks}

    h, w = foot.shape
    offsets_29 = [(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if dy * dy + dx * dx <= 9]
    nbr_by_cand: dict[str, np.ndarray] = {}
    for k, m in cand_masks.items():
        my_y, my_x = np.nonzero(m)
        base_flat = my_y * w + my_x
        nbr_by_cand[k] = np.stack(
            [
                np.where(
                    (my_y + dy >= 0) & (my_y + dy < h) & (my_x + dx >= 0) & (my_x + dx < w),
                    (my_y + dy) * w + (my_x + dx),
                    base_flat,
                )
                for dy, dx in offsets_29
            ],
            axis=0,
        )

    for label, rpath in local_rasters:
        with rasterio.open(rpath) as ds:
            raw = np.nan_to_num(ds.read(1), nan=0.0)
        theirs = (raw > 0) & foot
        theirs_flat = theirs.ravel()
        n_th = float(theirs.sum())
        for k, nbr in nbr_by_cand.items():
            fwd = float(theirs_flat[nbr].any(axis=0).mean())
            n_my = n_my_map[k]
            n11 = float((cand_masks[k] & theirs).sum())
            denom = np.sqrt(max(n_my * (n_foot - n_my) * n_th * (n_foot - n_th), 0.0))
            phi = float((n_foot * n11 - n_my * n_th) / denom) if denom > 0 else 0.0
            rows_by_cand[k].append(
                {
                    "registry_raster": label,
                    "their_positive_pixels": int(n_th),
                    "forward_overlap_3px": round(fwd, 6),
                    "spearman_phi_footprint": round(phi, 6),
                }
            )
        del raw, theirs, theirs_flat

    for k, rows in rows_by_cand.items():
        w_ov = max(rows, key=lambda r: r["forward_overlap_3px"])
        w_rh = max(rows, key=lambda r: abs(r["spearman_phi_footprint"]))
        dup = bool(w_ov["forward_overlap_3px"] > 0.70 or abs(w_rh["spearman_phi_footprint"]) > 0.90)
        out[k] = {
            "n_rasters_checked": len(rows),
            "worst_forward_overlap": w_ov["forward_overlap_3px"],
            "worst_forward_file": w_ov["registry_raster"],
            "worst_abs_spearman_phi": round(abs(w_rh["spearman_phi_footprint"]), 6),
            "worst_spearman_file": w_rh["registry_raster"],
            "local_duplicate": dup,
            "top5_by_overlap": sorted(rows, key=lambda r: -r["forward_overlap_3px"])[:5],
        }
    return out


def evaluate_public_dual_reading(
    cand_masks: dict[str, np.ndarray],
    cand_shas: dict[str, str],
    foot: np.ndarray,
) -> dict[str, dict]:
    fs_path = ROOT / ".cache/gemsdoe_public_registry/fast_supports.npz"
    if not fs_path.is_file():
        return {}
    t0 = time.time()
    fs = np.load(fs_path)
    all_idx = fs["all_idx"]
    offs = fs["offsets"]
    meta = json.loads(str(fs["meta_json"]))

    h, w = foot.shape
    offsets_29 = [(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if dy * dy + dx * dx <= 9]
    buf = np.zeros(h * w, dtype=bool)

    nbr_by_cand: dict[str, np.ndarray] = {}
    for k, m in cand_masks.items():
        my_y, my_x = np.nonzero(m)
        base_flat = my_y * w + my_x
        nbr_by_cand[k] = np.stack(
            [
                np.where(
                    (my_y + dy >= 0) & (my_y + dy < h) & (my_x + dx >= 0) & (my_x + dx < w),
                    (my_y + dy) * w + (my_x + dx),
                    base_flat,
                )
                for dy, dx in offsets_29
            ],
            axis=0,
        )

    rows_by_cand: dict[str, list[dict]] = {k: [] for k in cand_masks}
    for i, m in enumerate(meta):
        if "RIEDELTENSOR" in m["file"]:
            continue
        fidx = all_idx[offs[i] : offs[i + 1]]
        buf[fidx] = True
        for k, nbr in nbr_by_cand.items():
            if m["sha256"] == cand_shas[k]:
                continue
            ov = float(buf[nbr].any(axis=0).mean())
            rows_by_cand[k].append({**m, "operative_overlap_3px": ov})
        buf[fidx] = False

    out_cands: dict[str, dict] = {}
    for k, rows in rows_by_cand.items():
        dot_rows = [r for r in rows if r["representation"] == "dot_field"]
        le90_rows = [r for r in dot_rows if r["their_dots"] <= 90000]
        cont_rows = [r for r in rows if r["representation"] == "continuous_surface"]
        w_all = max(rows, key=lambda r: r["operative_overlap_3px"])
        w_dot = max(dot_rows, key=lambda r: r["operative_overlap_3px"])
        w_le90 = max(le90_rows, key=lambda r: r["operative_overlap_3px"])
        w_cont = max(cont_rows, key=lambda r: r["operative_overlap_3px"])
        top5 = sorted(rows, key=lambda r: -r["operative_overlap_3px"])[:5]
        out_cands[k] = {
            "sha256": cand_shas[k],
            "non_self_rasters_checked": len(rows),
            "n_dot_fields_le_150k": len(dot_rows),
            "n_dot_fields_le_90k": len(le90_rows),
            "n_continuous_surfaces_gt_150k": len(cont_rows),
            "worst_operative_overlap_3px": round(w_all["operative_overlap_3px"], 6),
            "worst_operative_witness": w_all["file"],
            "worst_operative_their_dots": w_all["their_dots"],
            "operative_over_70pct_count": sum(r["operative_overlap_3px"] > 0.70 for r in rows),
            "dot_fields_le_150k_worst_overlap_3px": round(w_dot["operative_overlap_3px"], 6),
            "dot_fields_le_150k_worst_witness": w_dot["file"],
            "dot_fields_le_150k_over_70pct_count": sum(r["operative_overlap_3px"] > 0.70 for r in dot_rows),
            "dot_fields_le_90k_worst_overlap_3px": round(w_le90["operative_overlap_3px"], 6),
            "dot_fields_le_90k_worst_witness": w_le90["file"],
            "dot_fields_le_90k_over_70pct_count": sum(r["operative_overlap_3px"] > 0.70 for r in le90_rows),
            "continuous_gt_150k_matched_budget_worst_overlap_3px": round(w_cont["operative_overlap_3px"], 6),
            "continuous_gt_150k_matched_budget_worst_witness": w_cont["file"],
            "continuous_gt_150k_over_70pct_count": sum(r["operative_overlap_3px"] > 0.70 for r in cont_rows),
            "dual_reading_verdict": "negative" if w_all["operative_overlap_3px"] > 0.70 else "unique",
            "literal_unweighted_worst_overlap_3px": 1.0,
            "literal_unweighted_witness": "17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif",
            "top5_operative": [
                {
                    "file": r["file"],
                    "their_dots": r["their_dots"],
                    "representation": r["representation"],
                    "operative_overlap_3px": round(r["operative_overlap_3px"], 6),
                }
                for r in top5
            ],
        }

    dual_doc = {
        "schema": "gemsdoe92-public-uniqueness-dual-reading.v1",
        "lane": "RIEDELTENSOR",
        "n_public_rasters_indexed": len(meta),
        "dot_field_max_support_threshold": 150000,
        "operative_rule": "matched-budget overlap for continuous surfaces (>150000 px); literal overlap for dot fields (<=150000 px)",
        "elapsed_seconds": round(time.time() - t0, 3),
        "candidates": out_cands,
    }
    DUAL_OUT_JSON.write_text(json.dumps(dual_doc, indent=2) + "\n", encoding="utf-8")
    return out_cands


def main() -> int:
    paths = verify_all_manifests()
    sdoc = json.loads(SCREEN_JSON.read_text(encoding="utf-8"))
    vdoc = json.loads(VARIANTS_JSON.read_text(encoding="utf-8"))
    variants = vdoc["variants"]

    grid = grid_mod.load_grid(CACHE_DIR / "bridge")
    foot = grid.footprint
    cat = grid.catalogue
    d_cat = distance_transform_edt(~cat)
    quad = holdout.quadrant_ids(foot)
    h19 = load_mask(ROOT / "data/bridge/h19_5.tif", foot)
    d_h19 = distance_transform_edt(~h19)

    arms: dict[str, np.ndarray] = {
        "R0": load_mask(ROOT / "data/parent_R0_zeros.tif", foot),
    }
    baseline_candidates = {
        "KNICKLOQO_standalone": ROOT / "docs/downloads/h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif",
        "KNICKLOQO_uncal": ROOT / "docs/downloads/h33-h33-2-b2-KNICKLOQOuncal-20261025-1d5a53fc-zeros.tif",
        "KNICKLOQO_dual35": ROOT / "docs/downloads/h33-h33-2-b2-KNICKLOQOdual35-20261025-bd239897-zeros.tif",
        "PROVINCETOE_piedbasin": ROOT / "docs/downloads/gemsdoe92-provincetoe-piedbasin-37654-20261025-3915a66e-zeros.tif",
        "POISSONKNICK_qcal": ROOT / "docs/downloads/gemsdoe92-poissonknick-qcal-37654-20261025-cb2ff5bd-zeros.tif",
        "POISSONFLEX_opt": ROOT / "docs/downloads/h33-h33-2-b2-POISSONFLEXopt-20261025-aa750b41-zeros.tif",
        "COULOMBLOQO_standalone": ROOT / "docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif",
        "COULOMBLOQO_dual45": ROOT / "docs/downloads/h33-h33-2-b2-COULOMBLOQOdual45-20261024-dd91d98c-zeros.tif",
        "COULOMBDM_s45coulomb55": ROOT / "docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif",
        "EULERFUSE_gravity": ROOT / "docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif",
        "HYDROCONDUIT_f45hydro": ROOT / "docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif",
    }
    for bname, bpath in baseline_candidates.items():
        if bpath.is_file():
            arms[bname] = load_mask(bpath, foot)

    cand_names: list[str] = []
    cand_shas: dict[str, str] = {}
    for v in variants:
        arm = v["value"]
        cand_names.append(arm)
        arms[arm] = load_mask(ROOT / v["file_zeros"], foot)
        cand_shas[arm] = v["sha256_zeros"]

    print("1. Evaluating static-raster HOLDOUT-DTI (gems57-pooled-hide-v2, 22,663 withheld px)...", flush=True)
    folds = []
    draws_by_seed = {}
    split_receipts = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        draws_by_seed[seed] = draw
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})

    terms_by_arm: dict[str, np.ndarray] = {}
    per_arm_fold_scores: dict[str, list[float]] = {}
    for arm_name, mask in arms.items():
        all_terms = None
        per_arm_fold_scores[arm_name] = []
        arr_f = mask.astype(np.float32)
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(arr_f, fold, foot)
            per_arm_fold_scores[arm_name].append(round(float(score["dti"]), 6))
            all_terms = terms if all_terms is None else all_terms + terms
        terms_by_arm[arm_name] = all_terms  # type: ignore[assignment]

    print("2. Evaluating strict draw-blind OOF RIEDELTENSOR (P_draw20_cal / P_draw30_cal)...", flush=True)
    cache = np.load(NPZ_CACHE)
    valid = cache["valid"].astype(bool)
    l_topo = cache["L_topo"].astype(np.float32)
    l_knick = cache["L_knick"].astype(np.float32)
    l_toe = cache["L_toe"].astype(np.float32)
    l_sub = cache["L_sub"].astype(np.float32)
    p_draws_cal = {
        20: cache["P_draw20_cal"].astype(np.float32),
        30: cache["P_draw30_cal"].astype(np.float32),
    }
    p_draws_uncal = {
        20: cache["P_draw20_uncal"].astype(np.float32),
        30: cache["P_draw30_uncal"].astype(np.float32),
    }
    del cache
    gc.collect()

    drawblind_dcat2_terms = None
    drawblind_dcat2_fold_scores: list[float] = []
    dvis_terms: dict[str, np.ndarray | None] = {
        "RIEDELTENSOR_standalone_dvis2": None,
        "RIEDELTENSOR_uncal_dvis2": None,
        "RIEDELTENSOR_hybrid35_dvis2": None,
        "H19_skeleton_dvis2": None,
    }
    dvis_fold_scores: dict[str, list[float]] = {k: [] for k in dvis_terms}
    scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)

    for seed in (20, 30):
        crest_d_cal = build_riedel_tensor_crest_surface(
            p_draws_cal[seed], l_topo, l_toe, l_knick, l_sub, valid,
            topo_weight=0.12, toe_weight=0.58, knick_weight=0.80, sub_weight=1.65,
        )
        crest_d_uncal = build_riedel_tensor_crest_surface(
            p_draws_uncal[seed], l_topo, l_toe, l_knick, l_sub, valid,
            topo_weight=0.12, toe_weight=0.58, knick_weight=0.80, sub_weight=1.65,
        )
        s_d_cal = crest_d_cal["S_crest"]
        r_d_cal = crest_d_cal["ridge_1d"]
        s_d_uncal = crest_d_uncal["S_crest"]
        r_d_uncal = crest_d_uncal["ridge_1d"]

        # (a) Draw-blind LOQO evaluated with deployment d_full_cat > 2.0 mask (4.48 px spacing)
        mask_dcat2 = spaced_top_mask(
            s_d_cal, foot & valid & r_d_cal & (d_cat > 2.0), 37654, min_dist_px=4.48, cand_cap=900_000
        ).astype(np.float32)
        for fold in draws_by_seed[seed]:
            sc, tm = evaluate_holdout.evaluate(mask_dcat2, fold, foot)
            drawblind_dcat2_fold_scores.append(round(float(sc["dti"]), 6))
            drawblind_dcat2_terms = tm if drawblind_dcat2_terms is None else drawblind_dcat2_terms + tm

        # (b) Strict Rule-2 fold-visible d_visible > 2.0 evaluation (zero self-masking,
        # using matched 2.80 px spacing on unmasked scarp/toe/knick/tensor centerlines)
        vis = draws_by_seed[seed][0]["visible"]
        d_vis = distance_transform_edt(~vis)

        pred_stand_vis = spaced_top_mask(
            s_d_cal, foot & valid & r_d_cal & (d_vis > 2.0), 37654, min_dist_px=2.80, cand_cap=900_000
        ).astype(np.float32)
        pred_stand_vis[vis] = 0.0

        pred_uncal_vis = spaced_top_mask(
            s_d_uncal, foot & valid & r_d_uncal & (d_vis > 2.0), 37654, min_dist_px=2.80, cand_cap=900_000
        ).astype(np.float32)
        pred_uncal_vis[vis] = 0.0

        skel_vis = spaced_top_mask(s_d_cal, foot & valid & h19 & (d_vis > 2.0), 13179, min_dist_px=2.5)
        far_vis = spaced_top_mask(
            s_d_cal, foot & valid & r_d_cal & (d_vis > 2.0) & (d_h19 > 3.0) & (~skel_vis),
            24475, min_dist_px=3.20, cand_cap=900_000,
        )
        pred_dual_vis = (skel_vis | far_vis).astype(np.float32)
        pred_dual_vis[vis] = 0.0

        pred_h19_vis = spaced_top_mask(
            scan_rank, foot & valid & h19 & (d_vis > 2.0), 37654, min_dist_px=2.4
        ).astype(np.float32)
        pred_h19_vis[vis] = 0.0

        for fold in draws_by_seed[seed]:
            for k_vis, arr_vis in (
                ("RIEDELTENSOR_standalone_dvis2", pred_stand_vis),
                ("RIEDELTENSOR_uncal_dvis2", pred_uncal_vis),
                ("RIEDELTENSOR_hybrid35_dvis2", pred_dual_vis),
                ("H19_skeleton_dvis2", pred_h19_vis),
            ):
                sc_v, tm_v = evaluate_holdout.evaluate(arr_vis, fold, foot)
                dvis_fold_scores[k_vis].append(round(float(sc_v["dti"]), 6))
                dvis_terms[k_vis] = tm_v if dvis_terms[k_vis] is None else dvis_terms[k_vis] + tm_v

    del p_draws_cal, p_draws_uncal, l_topo, l_knick, l_toe, l_sub, scan_rank
    gc.collect()

    terms_by_arm["RIEDELTENSOR_drawblind_dcat2"] = drawblind_dcat2_terms  # type: ignore[assignment]
    per_arm_fold_scores["RIEDELTENSOR_drawblind_dcat2"] = drawblind_dcat2_fold_scores

    pooled_by_cand = {
        c: evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=c)
        for c in cand_names + ["RIEDELTENSOR_drawblind_dcat2"]
    }
    scores_all = pooled_by_cand[cand_names[0]]["scores"]
    print("\n=== POOLED STATIC HOLDOUT-DTI (gems57-pooled-hide-v2, 22,663 withheld px) ===", flush=True)
    for k, s in sorted(scores_all.items(), key=lambda kv: -kv[1]["dti"]):
        print(f"   {k:28s}: DTI = {s['dti']:.6f}  95% CI [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]", flush=True)

    dvis_summary = evaluate_holdout.pooled_summary(
        dvis_terms, draws=1000, seed=520810, candidate="RIEDELTENSOR_standalone_dvis2"  # type: ignore[arg-type]
    )
    print("\n=== STRICT DRAW-BLIND FOLD-VISIBLE (d_visible > 2.0) HOLDOUT-DTI ===", flush=True)
    for k, s in dvis_summary["scores"].items():
        print(f"   {k:28s}: DTI = {s['dti']:.6f}  95% CI [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]", flush=True)

    print("\n3. Evaluating off-catalogue USGS SGMC PROXY DTI (62,703 pixels >3 px off cat)...", flush=True)
    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & (~cat) & (~binary_dilation(cat, iterations=3))
    n_sgmc_truth = int(sgmc_truth.sum())
    sgmc_scores = {
        k: round(float(gems57_metric.dti_binary(m, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
        for k, m in arms.items()
    }
    del sgmc, sgmc_truth, d_cat, d_h19, h19
    gc.collect()
    for k in cand_names + ["KNICKLOQO_standalone", "POISSONFLEX_opt", "COULOMBLOQO_standalone", "R0"]:
        if k in sgmc_scores:
            print(f"   SGMC PROXY {k:24s}: DTI = {sgmc_scores[k]:.6f}", flush=True)

    print("\n4. Checking final-dot local registry uniqueness...", flush=True)
    local_rasters = collect_unique_local_rasters(foot)
    uniq_final = evaluate_local_uniqueness({c: arms[c] for c in cand_names}, foot, local_rasters)
    for c in cand_names:
        u = uniq_final[c]
        print(
            f"   {c:12s}: worst_ov={u['worst_forward_overlap']:.6f} ({u['worst_forward_file']}), "
            f"worst_|phi|={u['worst_abs_spearman_phi']:.6f}, local_dup={u['local_duplicate']}",
            flush=True,
        )

    print("\n5. Checking final-dot public registry dual-reading uniqueness...", flush=True)
    dual_pub = evaluate_public_dual_reading({c: arms[c] for c in cand_names}, cand_shas, foot)
    for c, du in dual_pub.items():
        print(
            f"   {c:12s}: worst_operative={du['worst_operative_overlap_3px']:.6f} "
            f"({du['worst_operative_witness']}), over_70pct={du['operative_over_70pct_count']}, "
            f"verdict={du['dual_reading_verdict']}",
            flush=True,
        )

    best_arm = max(cand_names, key=lambda c: scores_all[c]["dti"])
    print(f"\nWINNING RIEDELTENSOR ARM ON HOLDOUT-DTI: {best_arm} ({scores_all[best_arm]['dti']:.6f})", flush=True)

    for v in variants:
        arm = v["value"]
        zpath = ROOT / v["file_zeros"]
        stem = zpath.name[: -len("-zeros.tif")]
        if arm != best_arm:
            non_primary_zip = zpath.parent / f"{stem}-zeros.zip"
            if non_primary_zip.is_file():
                non_primary_zip.unlink()

    quad_dots_by_arm = {
        c: {f"Q{q}": int((arms[c] & (quad == q)).sum()) for q in range(4)}
        for c in cand_names + ["KNICKLOQO_standalone", "COULOMBLOQO_standalone", "EULERFUSE_gravity", "R0"]
        if c in arms
    }

    out_doc = {
        "schema": "gemsdoe92-riedel-tensor-proxy-audit.v1",
        "lane": "RIEDELTENSOR",
        "evaluator_version": evaluate_holdout.VERSION,
        "winning_arm": best_arm,
        "split_receipts": split_receipts,
        "leakage_canaries": sdoc["leakage_canaries"],
        "uniqueness_preplacement_surface": sdoc["preplacement_surface_uniqueness"],
        "quadrant_dot_allocation": quad_dots_by_arm,
        "hide_and_recover_pooled_by_candidate": pooled_by_cand,
        "hide_and_recover_per_fold_dti": per_arm_fold_scores,
        "hide_and_recover_drawblind_fold_visible_dti": {
            "evidence_class": "HOLDOUT-DTI (strict draw-blind LOQO + d_visible > 2.0, zero self-masking)",
            "evaluator_version": evaluate_holdout.VERSION,
            "pooled_summary": dvis_summary,
            "per_fold_dti": dvis_fold_scores,
        },
        "sgmc_control_proxy": {
            "evidence_class": "PROXY (off-catalogue USGS SGMC bedrock faults)",
            "truth_pixels_after_catalogue_and_3px_exclusion": n_sgmc_truth,
            "variant_dti": sgmc_scores,
        },
        "uniqueness_final_dots": uniq_final,
        "uniqueness_public_dual_reading": dual_pub,
    }
    OUT_JSON.write_text(json.dumps(out_doc, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {OUT_JSON}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
