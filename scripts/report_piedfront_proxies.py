#!/usr/bin/env python3
"""REPORT ONLY instruments for PIEDFRONT variants.

Computes and records:
1. HOLDOUT-DTI (`gems57-pooled-hide-v2`): buffered whole-component hide-and-recover
   (seeds 20 + 30, 8 folds, 22,663 withheld positives, alpha=0.2, beta=0.8, 300 m
   triangular kernel, 1,000 paired 20 km spatial-cluster bootstrap draws) against
   controls R0 and RELIEFp10 (previous holdout best, 0.006045).
2. Single-feature leakage canaries (Bands 5, 12, 15, 19 and derived surfaces).
3. Off-catalogue USGS SGMC bedrock-fault control PROXY (62,703 truth pixels >3 px
   outside the catalogue).
4. Fixed-catalogue diagnostic (not a holdout; ordering sanity check).
5. Pre-placement surface AND final-dot uniqueness (`REGISTRY-MEASUREMENT`) against
   all locally accessible registry rasters (excluding same-lane siblings).
"""
from __future__ import annotations

import gc
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.spatial import cKDTree
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import verify_all_manifests  # noqa: E402
from gems.piedfront import piedfront_surface, spaced_top_mask  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric  # noqa: E402


def load_mask(path: Path, footprint: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        return (np.nan_to_num(ds.read(1), nan=0.0) > 0) & footprint


def phi_and_jaccard(a: np.ndarray, b: np.ndarray, footprint: np.ndarray) -> tuple[float, float]:
    af = a & footprint
    bf = b & footprint
    n11 = int(np.sum(af & bf))
    n10 = int(np.sum(af & ~bf))
    n01 = int(np.sum(~af & bf))
    n00 = int(np.sum(footprint) - n11 - n10 - n01)
    den = float(np.sqrt(float(max((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00), 1))))
    phi = float((float(n11 * n00 - n10 * n01)) / den) if den > 0 else 0.0
    jac = float(n11 / max(n11 + n10 + n01, 1))
    return phi, jac


def collect_local_registry_paths(own_ids: set[str]) -> list[Path]:
    registry_paths: list[Path] = [
        ROOT / "data/parent_R0_zeros.tif",
        ROOT / "data/bridge/h19_5.tif",
        ROOT / "data/bridge/d28.tif",
        ROOT / "data/bridge/h27_4_solo.tif",
        ROOT / "data/bridge/sample_submission.tif",
        ROOT / "data/bridge/labels.tif",
    ]
    registry_paths += sorted((ROOT / "docs/downloads").glob("*-zeros.tif"))
    registry_paths += sorted((ROOT / "releases").glob("*-zeros.tif"))
    registry_paths += sorted((ROOT / "releases").glob("*STEPOVER*.tif"))
    return [p for p in registry_paths if p.is_file() and p.name not in own_ids]


def run_uniqueness_scans(
    s_pct: np.ndarray,
    s_raw: np.ndarray,
    valid: np.ndarray,
    d_cat: np.ndarray,
    candidate_arms: dict[str, np.ndarray],
    footprint: np.ndarray,
    own_ids: set[str],
) -> tuple[dict, dict]:
    surf_dots = spaced_top_mask(s_raw, valid & (d_cat > 2.0), 37654, min_dist_px=2.8, cand_cap=500_000)
    surf_pts = np.column_stack(np.nonzero(surf_dots))

    rng = np.random.default_rng(520810)
    fp_idx = np.flatnonzero(footprint)
    samp = rng.choice(fp_idx, size=100_000, replace=False)
    s_samp = s_pct.ravel()[samp]

    cand_pts = {k: np.column_stack(np.nonzero(m)) for k, m in candidate_arms.items()}
    cand_trees = {k: cKDTree(pts) for k, pts in cand_pts.items()}

    surf_rows = []
    final_rows: dict[str, list[dict]] = {k: [] for k in candidate_arms}
    seen_masks: set[bytes] = set()

    for p in collect_local_registry_paths(own_ids):
        theirs = load_mask(p, footprint)
        key = np.packbits(theirs).tobytes()
        if key in seen_masks or not theirs.any():
            continue
        seen_masks.add(key)

        their_pts = np.column_stack(np.nonzero(theirs))
        their_tree = cKDTree(their_pts)

        # Surface comparison
        rho = float(spearmanr(s_samp, theirs.astype(np.float32).ravel()[samp]).statistic)
        d_surf, _ = their_tree.query(surf_pts, k=1)
        fwd_surf = float(np.mean(d_surf <= 3.0))
        surf_rows.append({
            "registry_file": p.name,
            "their_dots": int(len(their_pts)),
            "spearman_sample100k": round(rho, 6),
            "abs_spearman_sample100k": round(abs(rho), 6),
            "surface_top37654_forward_overlap_3px": round(fwd_surf, 6),
        })

        # Final-dot comparison for each candidate arm
        for arm_name, mask in candidate_arms.items():
            d_fwd, _ = their_tree.query(cand_pts[arm_name], k=1)
            d_rev, _ = cand_trees[arm_name].query(their_pts, k=1)
            fwd = float(np.mean(d_fwd <= 3.0))
            rev = float(np.mean(d_rev <= 3.0))
            phi, jac = phi_and_jaccard(mask, theirs, footprint)
            final_rows[arm_name].append({
                "registry_file": p.name,
                "their_dots": int(len(their_pts)),
                "forward_overlap_my_dots_within_3px": round(fwd, 6),
                "reverse_overlap_their_dots_within_3px": round(rev, 6),
                "binary_spearman_phi": round(phi, 6),
                "jaccard_exact_pixels": round(jac, 6),
            })

    worst_surf_fwd = max(surf_rows, key=lambda r: r["surface_top37654_forward_overlap_3px"])
    worst_surf_rho = max(surf_rows, key=lambda r: r["abs_spearman_sample100k"])
    surf_uniq = {
        "evidence_class": "REGISTRY-MEASUREMENT",
        "phase": "preplacement_surface",
        "rule": "literal: forward_overlap > 0.70 OR |spearman| > 0.90 => duplicate, log and stop",
        "registry_rasters_checked": len(surf_rows),
        "worst_forward_overlap": worst_surf_fwd["surface_top37654_forward_overlap_3px"],
        "worst_forward_overlap_file": worst_surf_fwd["registry_file"],
        "worst_abs_spearman": worst_surf_rho["abs_spearman_sample100k"],
        "worst_abs_spearman_file": worst_surf_rho["registry_file"],
        "duplicate": bool(
            worst_surf_fwd["surface_top37654_forward_overlap_3px"] > 0.70
            or worst_surf_rho["abs_spearman_sample100k"] > 0.90
        ),
        "rows": surf_rows,
    }

    final_uniq: dict[str, dict] = {}
    for arm_name, rows in final_rows.items():
        worst_fwd = max(rows, key=lambda r: r["forward_overlap_my_dots_within_3px"])
        worst_rho = max(rows, key=lambda r: abs(r["binary_spearman_phi"]))
        final_uniq[arm_name] = {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "phase": "final_dots",
            "rule": "literal: forward_overlap > 0.70 OR |spearman| > 0.90 => duplicate, log and stop",
            "registry_rasters_checked": len(rows),
            "worst_forward_overlap": worst_fwd["forward_overlap_my_dots_within_3px"],
            "worst_forward_overlap_file": worst_fwd["registry_file"],
            "worst_abs_spearman": abs(worst_rho["binary_spearman_phi"]),
            "worst_abs_spearman_file": worst_rho["registry_file"],
            "duplicate": bool(
                worst_fwd["forward_overlap_my_dots_within_3px"] > 0.70
                or abs(worst_rho["binary_spearman_phi"]) > 0.90
            ),
            "rows": rows,
        }
    return surf_uniq, final_uniq


def main() -> int:
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    foot = grid.footprint
    cat = grid.catalogue
    d_cat = distance_transform_edt(~cat)

    arms: dict[str, np.ndarray] = {}
    with rasterio.open(paths["parent_r0_zeros"]) as ds:
        arms["R0"] = (ds.read(1) > 0) & foot
    arms["RELIEFp10"] = load_mask(
        ROOT / "docs/downloads/h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24-zeros.tif", foot
    )
    arms["BREAKLINEf45"] = load_mask(
        ROOT / "docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif", foot
    )
    arms["STRAINBREAKf60"] = load_mask(
        ROOT / "docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif", foot
    )

    receipt = json.loads((ROOT / "evidence" / "piedfront_variants.json").read_text(encoding="utf-8"))
    own_files: set[str] = set()
    cand_arms: dict[str, np.ndarray] = {}
    for item in receipt["variants"]:
        p = ROOT / "releases" / item["fallback_file"]
        m = load_mask(p, foot)
        arms[item["value"]] = m
        cand_arms[item["value"]] = m
        own_files.add(item["fallback_file"])
        own_files.add(item["primary_file"])

    # ---- 1. Pooled hide-and-recover HOLDOUT-DTI ---------------------------
    print("Evaluating HOLDOUT-DTI across 8 folds...")
    folds = []
    split_receipts = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})

    terms_by_arm: dict[str, np.ndarray] = {}
    per_arm_fold_scores: dict[str, list[float]] = {}
    for arm_name, mask in arms.items():
        all_terms = None
        per_arm_fold_scores[arm_name] = []
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(mask.astype(np.float32), fold, foot)
            per_arm_fold_scores[arm_name].append(float(score["dti"]))
            all_terms = terms if all_terms is None else all_terms + terms
        terms_by_arm[arm_name] = all_terms
        print(f"  Arm {arm_name}: mean fold DTI = {np.mean(per_arm_fold_scores[arm_name]):.6f}")

    pooled_by_candidate = {
        cand: evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=cand)
        for cand in cand_arms
    }
    best_cand = max(cand_arms, key=lambda c: pooled_by_candidate[c]["scores"][c]["dti"])
    pooled = pooled_by_candidate[best_cand]

    # ---- 2. Single-feature leakage canaries -------------------------------
    print("Running leakage canaries and surface uniqueness...")
    rng = np.random.default_rng(520810)
    y_parts, sample_indices = [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & foot)
        neg = np.flatnonzero(fold["region"] & foot & ~cat)
        n = min(len(neg), max(1, 2 * len(pos)))
        neg = rng.choice(neg, size=n, replace=False) if len(neg) > n else neg
        sample_indices.extend((pos, neg))
        y_parts.extend((np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)))
    y = np.concatenate(y_parts)
    flat_idx = np.concatenate(sample_indices)
    del folds
    gc.collect()

    with rasterio.open(paths["training_features"]) as ds:
        b5 = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b12 = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b15 = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    valid = (
        foot
        & np.isfinite(b5) & (b5 > -1e30)
        & np.isfinite(b12) & (b12 > -1e30)
        & np.isfinite(b15) & (b15 > -1e30)
        & np.isfinite(b19) & (b19 > -1e30)
    )
    surf = piedfront_surface(b12, b19, b5, b15, valid)
    feature_arrays = {
        "training_band_5_iso_grav_anom_slope": b5,
        "training_band_12_det_elev": b12,
        "training_band_15_depth_to_base_surf": b15,
        "training_band_19_det_elev_slope": b19,
        "piedfront_rel_break_pct": surf["rel_break_pct"],
        "piedfront_R_scarp": surf["R_scarp"],
        "piedfront_W_pied": surf["W_pied"],
        "piedfront_S_pct_main": surf["S_pct"],
    }
    canaries = {}
    for name, arr in feature_arrays.items():
        vals = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat_idx]
        auc = float(roc_auc_score(y, vals))
        sym = max(auc, 1.0 - auc)
        canaries[name] = {
            "auc": round(auc, 6),
            "symmetric_auc": round(sym, 6),
            "status": "INVESTIGATE" if sym > 0.90 else "REPORT_ONLY_PASS",
        }
    s_pct, s_raw = surf["S_pct"], surf["S_raw"]
    del b5, b12, b15, b19, surf, feature_arrays
    gc.collect()

    # ---- 3. Off-catalogue USGS SGMC control PROXY -------------------------
    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_scores = {
        k: round(float(metric.dti_binary(m, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
        for k, m in arms.items()
    }

    # ---- 4. Fixed-catalogue diagnostic ------------------------------------
    catdiag = {
        k: round(float(metric.dti_binary(m, cat, valid=foot, known=None)["dti"]), 6)
        for k, m in arms.items()
    }

    # ---- 5. Pre-placement surface AND final-dot uniqueness ----------------
    surf_uniq, final_uniq = run_uniqueness_scans(
        s_pct, s_raw, valid, d_cat, cand_arms, foot, own_files
    )

    report = {
        "evidence_label": "PROXY",
        "created_utc": "2026-10-24",
        "axis": "PIEDFRONT",
        "best_candidate": best_cand,
        "purpose": (
            "Report-only instruments for PIEDFRONT variants: pooled catalogue hide-and-recover "
            "HOLDOUT-DTI, single-feature leakage canaries, USGS SGMC off-catalogue control, "
            "fixed-catalogue diagnostic, and literal-rule uniqueness on pre-placement surface "
            "and final dots."
        ),
        "parent": "h33-h33-2-b2",
        "hide_and_recover_pooled_summary": pooled,
        "hide_and_recover_pooled_by_candidate": pooled_by_candidate,
        "holdout_splits": split_receipts,
        "per_arm_fold_scores": per_arm_fold_scores,
        "leakage_canaries": {
            "definition": "symmetric AUC on hidden catalogue positives vs non-catalogue negatives in buffered fold regions",
            "results": canaries,
            "stop_and_investigate_if_any_gt_0_90": any(c["status"] == "INVESTIGATE" for c in canaries.values()),
            "max_symmetric_auc": max(c["symmetric_auc"] for c in canaries.values()),
        },
        "sgmc_control_proxy": {
            "source": "manifest-pinned USGS SGMC derived fault control (https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d, US Public Domain)",
            "truth_pixels_after_catalogue_and_3px_exclusion": int(sgmc_truth.sum()),
            "r0_dti": sgmc_scores["R0"],
            "variant_dti": sgmc_scores,
            "variant_deltas_vs_r0": {k: round(v - sgmc_scores["R0"], 6) for k, v in sgmc_scores.items()},
        },
        "fixed_catalogue_diagnostic": {
            "evidence_class": "PROXY-DIAGNOSTIC (not a holdout; no withholding)",
            "definition": "DTI of each fixed raster against the full known catalogue (known=None)",
            "variant_dti": catdiag,
            "variant_deltas_vs_r0": {k: round(v - catdiag["R0"], 6) for k, v in catdiag.items()},
        },
        "uniqueness_preplacement_surface": surf_uniq,
        "uniqueness_final_dots": final_uniq,
        "caution": (
            "HOLDOUT-DTI / SGMC / fixed-catalogue numbers are local instruments, never live "
            "public scores, private-set scores, or organizer receipts."
        ),
    }

    out = ROOT / "evidence" / "piedfront_proxy_audit.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    print(
        json.dumps(
            {
                "best_candidate": best_cand,
                "holdout_scores": {k: v["dti"] for k, v in pooled["scores"].items()},
                "paired_deltas_for_best": {
                    k: {"delta": v["delta"], "ci95": v["ci95"]}
                    for k, v in pooled["paired_differences"].items()
                },
                "canary_max": report["leakage_canaries"]["max_symmetric_auc"],
                "sgmc": sgmc_scores,
                "catdiag": catdiag,
                "surface_uniqueness": {
                    "worst_fwd": surf_uniq["worst_forward_overlap"],
                    "worst_fwd_file": surf_uniq["worst_forward_overlap_file"],
                    "worst_rho": surf_uniq["worst_abs_spearman"],
                    "worst_rho_file": surf_uniq["worst_abs_spearman_file"],
                    "duplicate": surf_uniq["duplicate"],
                    "n_checked": surf_uniq["registry_rasters_checked"],
                },
                "final_uniqueness": {
                    k: {
                        "worst_fwd": v["worst_forward_overlap"],
                        "worst_fwd_file": v["worst_forward_overlap_file"],
                        "worst_rho": v["worst_abs_spearman"],
                        "worst_rho_file": v["worst_abs_spearman_file"],
                        "duplicate": v["duplicate"],
                        "n_checked": v["registry_rasters_checked"],
                    }
                    for k, v in final_uniq.items()
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
