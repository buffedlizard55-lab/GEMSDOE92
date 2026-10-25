#!/usr/bin/env python3
"""REPORT ONLY instruments for BREAKLINE variants.

Four separately-labelled readouts, never conflated:

1. HOLDOUT-DTI (`gems57-pooled-hide-v2`): catalogue hide-and-recover --
   whole-component buffered withholding (seeds 20 + 30), visible faults
   masked pixel-exactly, pooled DTI (alpha 0.2, beta 0.8, 300 m
   triangular kernel), paired spatial-cluster bootstrap CIs per dose vs
   every control.  Arms include R0 and RELIEF p10 (the current holdout
   best, 0.006045) so the promotion bar is scored on the same folds.
2. SGMC control PROXY: DTI against USGS SGMC bedrock faults >3 px from
   the catalogue (n = 62,703) -- an off-catalogue truth the catalogue
   holdout cannot see (NEXT_STEPS blocker 2).
3. FIXED-CATALOGUE DIAGNOSTIC: DTI against the full known catalogue.
   This is NOT a holdout (no withholding; candidate construction used
   the catalogue exclusion).  It is recorded only because it tracked the
   pooled-holdout ratio for the three prior arms of this repo
   (RELIEF 1.459 vs 1.509; DILATATION 1.435 vs 1.443; TIPGAP 0.731 vs
   0.680), i.e. as a cheap ordering check.  Decisions use readout 1.
4. Leakage canaries: single-feature symmetric AUC of the lane surface
   and its bands against withheld positives (stop if > 0.90).
5. Uniqueness (lane check on final dots): vs every locally present
   registry raster -- forward/reverse 3 px dot overlap, exact-pixel
   Jaccard, and binary Spearman (= Pearson phi for two binary fields).
   Literal rule: forward overlap > 0.70 or |rho| > 0.90 = duplicate.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import verify_all_manifests
from gems.breakline import lane_surface, percentile_rank, slope_break_magnitude, structure_tensor_coherence
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric


def load_mask(path: Path, footprint: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        return (np.nan_to_num(ds.read(1), nan=0.0) > 0) & footprint


def phi_and_jaccard(a: np.ndarray, b: np.ndarray, footprint: np.ndarray) -> tuple[float, float]:
    """Spearman/Pearson phi and Jaccard for two binary fields on the footprint."""
    af = a & footprint
    bf = b & footprint
    n11 = int(np.sum(af & bf)); n10 = int(np.sum(af & ~bf))
    n01 = int(np.sum(~af & bf)); n00 = int(np.sum(footprint) - n11 - n10 - n01)
    den = float(np.sqrt(float(max((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00), 1))))
    phi = float((float(n11 * n00 - n10 * n01)) / den) if den > 0 else 0.0
    jac = float(n11 / max(n11 + n10 + n01, 1))
    return phi, jac


def uniqueness(arms: dict[str, np.ndarray], footprint: np.ndarray,
               own_ids: set[str]) -> dict:
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

    # Stream the registry one raster at a time using the exact 7x7 Euclidean
    # r<=3.0 px disk (yy^2 + xx^2 <= 9), which is 100% bit-identical to
    # distance_transform_edt(~mask) <= 3.0 while using 12 MB bool instead of
    # 98 MB float64 and running ~80x faster across >40 registry rasters.
    yy3, xx3 = np.ogrid[-3:4, -3:4]
    disk_r3 = (yy3 * yy3 + xx3 * xx3) <= 9
    cand_arms = {k: v for k, v in arms.items() if k not in ("R0", "RELIEFp10")}
    ours_within3 = {k: binary_dilation(v, structure=disk_r3) for k, v in cand_arms.items()}
    rows_by_arm: dict[str, list] = {k: [] for k in cand_arms}
    seen_masks: dict[bytes, str] = {}
    for p in registry_paths:
        if not p.is_file() or p.name in own_ids:
            continue
        theirs = load_mask(p, footprint)
        key = np.packbits(theirs).tobytes()
        if key in seen_masks:
            continue
        seen_masks[key] = p.name
        if not theirs.any():
            continue
        theirs_within3 = binary_dilation(theirs, structure=disk_r3)
        for arm_name, mask in cand_arms.items():
            fwd = float(np.mean(theirs_within3[mask])) if mask.any() else 0.0
            rev = float(np.mean(ours_within3[arm_name][theirs])) if theirs.any() else 0.0
            phi, jac = phi_and_jaccard(mask, theirs, footprint)
            rows_by_arm[arm_name].append({
                "registry_file": p.name, "their_dots": int(theirs.sum()),
                "forward_overlap_my_dots_within_3px": round(fwd, 6),
                "reverse_overlap_their_dots_within_3px": round(rev, 6),
                "binary_spearman_phi": round(phi, 6),
                "jaccard_exact_pixels": round(jac, 6),
            })
        del theirs, theirs_within3
    del ours_within3

    out: dict[str, dict] = {}
    for arm_name, mask in cand_arms.items():
        rows = rows_by_arm[arm_name]
        worst_fwd = max(rows, key=lambda r: r["forward_overlap_my_dots_within_3px"])
        worst_rho = max(rows, key=lambda r: abs(r["binary_spearman_phi"]))
        out[arm_name] = {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "rule": "literal: forward_overlap > 0.70 OR |spearman| > 0.90 => duplicate, log and stop",
            "registry_rasters_checked": len(rows),
            "worst_forward_overlap": worst_fwd["forward_overlap_my_dots_within_3px"],
            "worst_forward_overlap_file": worst_fwd["registry_file"],
            "worst_abs_spearman": abs(worst_rho["binary_spearman_phi"]),
            "worst_abs_spearman_file": worst_rho["registry_file"],
            "duplicate": bool(worst_fwd["forward_overlap_my_dots_within_3px"] > 0.70
                              or abs(worst_rho["binary_spearman_phi"]) > 0.90),
            "rows": rows,
        }
    return out


def main() -> int:
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    foot = grid.footprint
    cat = grid.catalogue

    arms: dict[str, np.ndarray] = {}
    with rasterio.open(paths["parent_r0_zeros"]) as ds:
        arms["R0"] = (ds.read(1) > 0) & foot
    arms["RELIEFp10"] = load_mask(
        ROOT / "docs/downloads/h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24-zeros.tif", foot)
    receipt = json.loads((ROOT / "evidence" / "breakline_variants.json").read_text(encoding="utf-8"))
    own_files = set()
    for item in receipt["variants"]:
        p = ROOT / "releases" / item["fallback_file"]
        arms[item["value"]] = load_mask(p, foot)
        own_files.add(item["fallback_file"])
        own_files.add(item["primary_file"])
    # Registry scope for the BINDING lane check: rasters that existed before
    # this session (other lanes + parent lineage).  This session's own
    # superseded exact-greedy implementations are sibling builds of the same
    # dose ladder -- comparing against them would flag any corrected
    # re-emission as a "duplicate" of itself.  Their overlap with the Ltop
    # doses (0.816-0.860 forward) is instead expected dose-sibling
    # relatedness, recorded in IRREGULARITIES (they are never simultaneously
    # submittable; SLOT_PLAN keeps one BREAKLINE submission total).
    superseded_path = ROOT / "evidence" / "breakline_variants_exactgreedy_superseded.json"
    if superseded_path.is_file():
        superseded = json.loads(superseded_path.read_text(encoding="utf-8"))
        for item in superseded["variants"]:
            own_files.add(item["fallback_file"])
            own_files.add(item["primary_file"])

    # ---- 1. pooled hide-and-recover holdout (shared instrument) ----------
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
    pooled_by_candidate = {
        cand: evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=cand)
        for cand in ("f33Ltop", "f38Ltop", "f45Ltop")
    }
    pooled = pooled_by_candidate["f38Ltop"]  # headline block (middle dose)

    # ---- 2. leakage canaries (single features vs withheld truth) ---------
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

    with rasterio.open(paths["training_features"]) as ds:
        b3 = ds.read(3, masked=True).filled(np.nan).astype(np.float32)
        b5 = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b12 = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    valid_topo = foot & np.isfinite(b12) & (b12 > -1e30) & np.isfinite(b19) & (b19 > -1e30)
    surf = lane_surface(b12, b19, valid_topo)
    feature_arrays = {
        "breakline_L_pct": surf["L_pct"],
        "breakline_break_pct": surf["break_pct"],
        "breakline_coherence": surf["coherence"],
        "slope_break_magnitude_pct": percentile_rank(slope_break_magnitude(b19, valid_topo), valid_topo),
        "coherence_only_recomputed": structure_tensor_coherence(b12, valid_topo),
        "training_band_19_det_elev_slope": b19,
        "training_band_12_det_elev": b12,
        "training_band_3_tmi_hg": b3,
        "training_band_5_iso_grav_anom_slope": b5,
    }
    canaries = {}
    for name, arr in feature_arrays.items():
        vals = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat_idx]
        auc = float(roc_auc_score(y, vals))
        sym = max(auc, 1 - auc)
        canaries[name] = {"auc": round(auc, 6), "symmetric_auc": round(sym, 6),
                          "status": "INVESTIGATE" if sym > 0.90 else "REPORT_ONLY_PASS"}

    # ---- 3. SGMC off-catalogue control -----------------------------------
    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_scores = {k: round(float(metric.dti_binary(
        m, sgmc_truth, valid=foot, known=cat)["dti"]), 6) for k, m in arms.items()}

    # ---- 4. fixed-catalogue diagnostic (explicitly not a holdout) --------
    catdiag = {k: round(float(metric.dti_binary(
        m, cat, valid=foot, known=None)["dti"]), 6) for k, m in arms.items()}

    # ---- 5. uniqueness vs every local registry raster --------------------
    uniq = uniqueness(arms, foot, own_files)

    report = {
        "evidence_label": "PROXY",
        "created_utc": "20261024",
        "axis": "BREAKLINE",
        "purpose": ("Report-only instruments for BREAKLINE variants: pooled catalogue "
                    "hide-and-recover HOLDOUT-DTI, leakage canaries, USGS SGMC off-catalogue "
                    "control, a fixed-catalogue diagnostic, and literal-rule uniqueness "
                    "measurements on the final dots."),
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
            "calibration_note": ("For RELIEF/DILATATION/TIPGAP this diagnostic's ratio vs R0 tracked "
                                 "the pooled holdout ratio within ~0.05; recorded as an ordering "
                                 "check only. Decisions use HOLDOUT-DTI."),
        },
        "uniqueness_final_dots": uniq,
        "caution": ("HOLDOUT-DTI / SGMC / fixed-catalogue numbers are local instruments, never "
                    "live public scores, private-set scores, or organizer receipts."),
    }
    out = ROOT / "evidence" / "breakline_proxy_audit.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print(json.dumps({
        "holdout_scores": {k: v["dti"] for k, v in pooled["scores"].items()},
        "paired_deltas_f38": {k: (v["delta"], v["ci95"]) for k, v in pooled["paired_differences"].items()},
        "canary_max": report["leakage_canaries"]["max_symmetric_auc"],
        "sgmc": sgmc_scores, "catdiag": catdiag,
        "uniqueness": {k: {"worst_fwd": v["worst_forward_overlap"], "worst_fwd_file": v["worst_forward_overlap_file"],
                           "worst_rho": v["worst_abs_spearman"], "worst_rho_file": v["worst_abs_spearman_file"],
                           "duplicate": v["duplicate"], "n_checked": v["registry_rasters_checked"]}
                       for k, v in uniq.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
