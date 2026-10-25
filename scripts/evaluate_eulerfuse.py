#!/usr/bin/env python3
"""Evaluate the three pre-registered EULERFUSE arms without using a live slot."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import verify_all_manifests  # noqa: E402
from gems.breakline import spaced_top_mask  # noqa: E402
from gems.coulomb_loqo import directional_ridge_1d  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric  # noqa: E402
from screen_coulomb_loqo import collect_unique_local_rasters  # noqa: E402

CACHE = ROOT / ".cache" / "gems_inputs" / "eulerfuse_cache.npz"
SCREEN = ROOT / "evidence" / "eulerfuse_screen.json"
OUT = ROOT / "evidence" / "eulerfuse_holdout.json"
CURRENT_BEST = 0.11331615405665604


def load_mask(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return (np.nan_to_num(a, nan=0.0) > 0) & foot


def base_control_surface(raw: np.ndarray, base_line: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Convert EULERFUSE's cached 0.12/0.88 control to original 0.15/0.85 crest."""
    den = np.float32(0.12) + np.float32(0.88) * base_line
    p = np.divide(raw, den, out=np.zeros_like(raw), where=den > 0)
    return np.where(valid, p * (np.float32(0.15) + np.float32(0.85) * base_line), 0).astype(np.float32)


def emit(
    arm: str,
    surface: np.ndarray,
    valid: np.ndarray,
    exclusion_distance: np.ndarray,
    h19: np.ndarray,
    d_h19: np.ndarray,
) -> np.ndarray:
    ridge = directional_ridge_1d(surface, valid)
    pool = valid & ridge & (exclusion_distance > 2.0)
    if arm == "joint45":
        skel = spaced_top_mask(surface, pool & h19, 16_944, min_dist_px=2.5)
        far = spaced_top_mask(
            surface, pool & (d_h19 > 3.0) & (~skel), 20_710,
            min_dist_px=2.8, cand_cap=900_000,
        )
        out = skel | far
    else:
        out = spaced_top_mask(surface, pool, 37_654, min_dist_px=2.8, cand_cap=900_000)
    if int(out.sum()) != 37_654:
        raise RuntimeError(f"{arm}: emitted {int(out.sum())} dots")
    return out


def local_uniqueness(masks: dict[str, np.ndarray], foot: np.ndarray) -> dict[str, dict]:
    rows = {k: [] for k in masks}
    for label, path in collect_unique_local_rasters(foot, exclude_substrings=("eulerfuse", "EULERFUSE")):
        with rasterio.open(path) as ds:
            raw = np.nan_to_num(ds.read(1), nan=0.0)
        support = (raw > 0) & foot
        dist = distance_transform_edt(~support)
        t = support[foot].astype(np.float32)
        for arm, m in masks.items():
            overlap = float(np.mean(dist[m] <= 3.0))
            phi = float(np.corrcoef(m[foot].astype(np.float32), t)[0, 1]) if np.std(t) else 0.0
            rows[arm].append({
                "registry_raster": label,
                "positive_pixels": int(support.sum()),
                "forward_overlap_3px": round(overlap, 6),
                "spearman_phi": round(phi, 6),
            })
    result = {}
    for arm, rr in rows.items():
        wo = max(rr, key=lambda x: x["forward_overlap_3px"])
        wr = max(rr, key=lambda x: abs(x["spearman_phi"]))
        result[arm] = {
            "rasters_checked": len(rr),
            "worst_forward_overlap_3px": wo["forward_overlap_3px"],
            "worst_overlap_raster": wo["registry_raster"],
            "worst_abs_spearman_phi": round(abs(wr["spearman_phi"]), 6),
            "worst_spearman_raster": wr["registry_raster"],
            "duplicate": bool(wo["forward_overlap_3px"] > 0.70 or abs(wr["spearman_phi"]) > 0.90),
            "top5_overlap": sorted(rr, key=lambda x: -x["forward_overlap_3px"])[:5],
        }
    return result


def main() -> int:
    paths = verify_all_manifests()
    if not CACHE.is_file() or not SCREEN.is_file():
        raise SystemExit("Run scripts/screen_eulerfuse.py first")
    screen = json.loads(SCREEN.read_text())
    cache = np.load(CACHE)
    grid = grid_mod.load_grid(ROOT / ".cache/gems_inputs/bridge")
    foot, cat = grid.footprint, grid.catalogue
    valid = cache["valid"].astype(bool)
    base_line = cache["base_line"].astype(np.float32)
    d_cat = distance_transform_edt(~cat)
    h19 = load_mask(ROOT / "data/bridge/h19_5.tif", foot)
    d_h19 = distance_transform_edt(~h19)

    folds_by_seed: dict[int, list[dict]] = {}
    folds = []
    split_receipts = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds_by_seed[seed] = draw
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [f["receipt"] for f in draw]})

    print("[1/4] Emitting deployment previews and static HOLDOUT-DTI...", flush=True)
    full_surfaces = {
        "base_control": base_control_surface(cache["S_base_full"].astype(np.float32), base_line, valid),
        "joint": cache["S_joint_full"].astype(np.float32),
        "gravity": cache["S_gravity_full"].astype(np.float32),
    }
    deployment = {
        "base_control": emit("base_control", full_surfaces["base_control"], valid, d_cat, h19, d_h19),
        "joint": emit("joint", full_surfaces["joint"], valid, d_cat, h19, d_h19),
        "gravity": emit("gravity", full_surfaces["gravity"], valid, d_cat, h19, d_h19),
        "joint45": emit("joint45", full_surfaces["joint"], valid, d_cat, h19, d_h19),
    }
    static_terms = {}
    static_per_fold = {}
    for arm, mask in deployment.items():
        total = None
        vals = []
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(mask.astype(np.float32), fold, foot)
            total = terms if total is None else total + terms
            vals.append(float(score["dti"]))
        static_terms[arm] = total
        static_per_fold[arm] = vals
    static_summary = {
        arm: evaluate_holdout.pooled_summary(static_terms, draws=1000, seed=92024, candidate=arm)
        for arm in ("joint", "gravity", "joint45")
    }

    print("[2/4] Fold-specific draw-blind placement and primary HOLDOUT-DTI...", flush=True)
    strict_terms = {k: None for k in deployment}
    strict_per_fold = {k: [] for k in deployment}
    for seed in (20, 30):
        visible = folds_by_seed[seed][0]["visible"]
        d_vis = distance_transform_edt(~visible)
        surfaces = {
            "base_control": base_control_surface(cache[f"S_base_draw{seed}"].astype(np.float32), base_line, valid),
            "joint": cache[f"S_joint_draw{seed}"].astype(np.float32),
            "gravity": cache[f"S_gravity_draw{seed}"].astype(np.float32),
        }
        masks = {
            "base_control": emit("base_control", surfaces["base_control"], valid, d_vis, h19, d_h19),
            "joint": emit("joint", surfaces["joint"], valid, d_vis, h19, d_h19),
            "gravity": emit("gravity", surfaces["gravity"], valid, d_vis, h19, d_h19),
            "joint45": emit("joint45", surfaces["joint"], valid, d_vis, h19, d_h19),
        }
        for mask in masks.values():
            mask[visible] = False
        for fold in folds_by_seed[seed]:
            for arm, mask in masks.items():
                score, terms = evaluate_holdout.evaluate(mask.astype(np.float32), fold, foot)
                strict_terms[arm] = terms if strict_terms[arm] is None else strict_terms[arm] + terms
                strict_per_fold[arm].append(float(score["dti"]))

    strict_summary = {
        arm: evaluate_holdout.pooled_summary(strict_terms, draws=1000, seed=92024, candidate=arm)
        for arm in ("joint", "gravity", "joint45")
    }
    scores = strict_summary["joint"]["scores"]
    for arm in scores:
        print(f"      {arm:12s} {scores[arm]['dti']:.6f} [{scores[arm]['ci95'][0]:.6f}, {scores[arm]['ci95'][1]:.6f}]", flush=True)
    best = max(("joint", "gravity", "joint45"), key=lambda a: scores[a]["dti"])
    paired = strict_summary[best]["paired_differences"]["base_control"]
    beats_current_point = scores[best]["dti"] > CURRENT_BEST
    beats_fresh_control = paired["delta"] > 0 and paired["ci95"][0] > 0

    print("[3/4] SGMC proxy and final local uniqueness...", flush=True)
    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & (~cat) & (~binary_dilation(cat, iterations=3))
    sgmc_scores = {
        arm: float(metric.dti_binary(mask, sgmc_truth, valid=foot, known=cat)["dti"])
        for arm, mask in deployment.items()
    }
    unique = local_uniqueness({a: deployment[a] for a in ("joint", "gravity", "joint45")}, foot)
    best_local_unique = not unique[best]["duplicate"]
    promote_gate = bool(beats_current_point and beats_fresh_control and best_local_unique)

    print("[4/4] Writing holdout decision...", flush=True)
    out = {
        "schema": "gemsdoe92.eulerfuse-holdout.v1",
        "lane": "EULERFUSE",
        "evaluator_version": evaluate_holdout.VERSION,
        "evidence_label": "HOLDOUT-DTI",
        "split_receipts": split_receipts,
        "withheld_positive_pixels": int(scores[best]["withheld_positive_pixels"]),
        "static_deployment_mask": {
            "pooled_by_candidate": static_summary,
            "per_fold_dti": static_per_fold,
        },
        "primary_drawblind_visible_mask": {
            "pooled_by_candidate": strict_summary,
            "per_fold_dti": strict_per_fold,
        },
        "current_documented_holdout_best": {
            "evidence_class": "HOLDOUT-DTI",
            "value": CURRENT_BEST,
            "source": "evidence/coulomb_loqo_run_card.json",
        },
        "best_arm": best,
        "decision": {
            "beats_current_best_point": beats_current_point,
            "paired_delta_vs_fresh_base_control": paired,
            "paired_ci_excludes_zero_positive": beats_fresh_control,
            "local_unique": best_local_unique,
            "promotion_gate_pass": promote_gate,
            "weekly_slot_used": False,
        },
        "sgmc_proxy": {
            "evidence_class": "PROXY",
            "truth_pixels": int(sgmc_truth.sum()),
            "dti": sgmc_scores,
        },
        "final_local_registry": unique,
        "leakage_canaries": screen["leakage_canaries"],
        "experiments_used": 3,
        "budget_limit": 3,
    }
    OUT.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(f"BEST {best}; promotion_gate={promote_gate}; wrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
