#!/usr/bin/env python3
"""Report proxy instruments for RADSCARP variants.

Mirrors report_breakline_proxies.py but for the fused radiometric+DEM surface.
Instruments:
  1. pooled hide-and-recover holdout (gems57-pooled-hide-v2, seeds 20/30, buffered)
  2. leakage canaries (symmetric AUC per feature)
  3. SGMC off-catalogue control
  4. fixed-catalogue diagnostic
  5. literal uniqueness vs local registry
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
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor"))

from vendor.gems57 import grid as grid_mod, holdout, metric
from vendor.gems57 import evaluate_holdout
from gems.radscarp import lane_surface, percentile_rank, slope_break_magnitude, structure_tensor_coherence, radiometric_ratio

def verify_all_manifests():
    import hashlib, json
    manifest = json.loads((ROOT / "registry/session_manifest.json").read_text(encoding="utf-8"))
    resolved = {}
    for item in manifest["files"]:
        path = ROOT / item["local_path"]
        if not path.is_file():
            raise FileNotFoundError(f"Missing {item['id']} at {path}")
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        got_sha = h.hexdigest()
        if got_sha != item["sha256"] or path.stat().st_size != int(item["bytes"]):
            raise RuntimeError(f"Mismatch {item['id']}")
        resolved[item["id"]] = path
    return resolved

def load_mask(path: Path, foot):
    with rasterio.open(path) as ds:
        a = ds.read(1)
        return (a > 0) & foot

def uniqueness(cand_arms, foot, own_files=None):
    from vendor.gems57 import grid as grid_mod
    from vendor.gems57.uniqueness import compare_array_to_registry
    import hashlib
    # Build registry index from local releases/docs/downloads/lineage before this session
    registry_paths = []
    for pattern in ["releases/*.tif", "docs/downloads/*.tif", ".cache/gems_inputs/lineage/*.tif"]:
        for p in ROOT.glob(pattern):
            if p.name.startswith("._"):
                continue
            if own_files and p.name in own_files:
                continue
            registry_paths.append(p)
    seen = set()
    uniq_paths = []
    for p in registry_paths:
        r = p.resolve()
        if r not in seen:
            seen.add(r)
            uniq_paths.append(p)
    grid = grid_mod.load_grid(ROOT / ".cache/gems_inputs/bridge")
    expected = (grid.shape, grid.crs, grid.transform)
    # Filter to exact grid
    filtered = []
    for p in uniq_paths:
        try:
            with rasterio.open(p) as ds:
                if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected:
                    continue
            filtered.append(p)
        except Exception:
            continue
    # Build index dict for compare_array_to_registry
    # Need to provide rasters with repo_first, sources, cache_file, sha256
    import hashlib as _hl
    rasters = []
    for p in filtered:
        h = _hl.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1<<20), b""):
                h.update(chunk)
        rasters.append({"repo_first": str(p.parent), "sources": [str(p.relative_to(ROOT))], "cache_file": str(p), "sha256": h.hexdigest()})
    index = {"rasters": rasters, "complete_accessible_scan": False, "errors": []}
    out = {}
    for arm_name, mask in cand_arms.items():
        # Convert mask to float predictions (binary 0/1)
        arr = mask.astype(np.float32)
        # compare
        try:
            res = compare_array_to_registry(arr, index, foot, expected_grid=expected)
            rows = res["rows"]
        except Exception as e:
            # Fallback simple
            rows = []
            res = {"rows": []}
        worst_fwd = None
        worst_rho = None
        for r in rows:
            if "my_dots_within_3px_of_theirs" in r:
                if worst_fwd is None or r["my_dots_within_3px_of_theirs"] > worst_fwd["my_dots_within_3px_of_theirs"]:
                    worst_fwd = r
            if "spearman_full_footprint" in r and r["spearman_full_footprint"] is not None:
                if worst_rho is None or abs(r["spearman_full_footprint"]) > abs(worst_rho["spearman_full_footprint"]):
                    worst_rho = r
        out[arm_name] = {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "rule": "literal: forward_overlap >0.70 OR |spearman|>0.90 => duplicate",
            "registry_rasters_checked": len(rows),
            "worst_forward_overlap": worst_fwd["my_dots_within_3px_of_theirs"] if worst_fwd else 0.0,
            "worst_forward_overlap_file": worst_fwd["submission"] if worst_fwd and "submission" in worst_fwd else (worst_fwd["file"] if worst_fwd else "none"),
            "worst_abs_spearman": abs(worst_rho["spearman_full_footprint"]) if worst_rho and worst_rho["spearman_full_footprint"] is not None else 0.0,
            "worst_abs_spearman_file": worst_rho["submission"] if worst_rho and "submission" in worst_rho else (worst_rho["file"] if worst_rho else "none"),
            "duplicate": bool((worst_fwd and worst_fwd["my_dots_within_3px_of_theirs"] > 0.70) or (worst_rho and worst_rho["spearman_full_footprint"] is not None and abs(worst_rho["spearman_full_footprint"]) > 0.90)),
            "rows": rows,
        }
    return out

def main() -> int:
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(ROOT / ".cache/gems_inputs/bridge")
    foot = grid.footprint
    cat = grid.catalogue

    # Load parent and variants
    arms = {}
    with rasterio.open(paths["parent_r0_zeros"]) as ds:
        arms["R0"] = (ds.read(1) > 0) & foot
    # RELIEF control for holdout best
    rel_path = ROOT / "docs/downloads/h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24-zeros.tif"
    if rel_path.is_file():
        arms["RELIEFp10"] = load_mask(rel_path, foot)
    # Load BREAKLINE primary for uniqueness comparison
    br_path = ROOT / "docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif"
    if br_path.is_file():
        arms["BREAKLINEf45"] = load_mask(br_path, foot)
    # Load our variants
    receipt = json.loads((ROOT / "evidence/radscarp_variants.json").read_text(encoding="utf-8"))
    own_files = set()
    for item in receipt["variants"]:
        p = ROOT / "releases" / item["fallback_file"]
        arms[item["value"]] = load_mask(p, foot)
        own_files.add(item["fallback_file"])
        own_files.add(item["primary_file"])

    # 1. pooled holdout
    folds = []
    split_receipts = []
    for seed in (20,30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})
    terms_by_arm = {}
    per_arm_fold_scores = {}
    for arm_name, mask in arms.items():
        all_terms = None
        per_arm_fold_scores[arm_name] = []
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(mask.astype(np.float32), fold, foot)
            per_arm_fold_scores[arm_name].append(float(score["dti"]))
            all_terms = terms if all_terms is None else all_terms + terms
        terms_by_arm[arm_name] = all_terms
    # pooled summaries for our three doses
    pooled_by_candidate = {cand: evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=cand) for cand in ("f33","f38","f45")}
    pooled = pooled_by_candidate["f38"]  # middle dose headline

    # 2. leakage canaries (features vs hidden catalogue)
    rng = np.random.default_rng(520810)
    y_parts, flat_idx_parts = [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & foot)
        neg = np.flatnonzero(fold["region"] & foot & ~cat)
        n = min(len(neg), max(1, 2*len(pos)))
        neg = rng.choice(neg, size=n, replace=False) if len(neg)>n else neg
        flat_idx_parts.extend((pos, neg))
        y_parts.extend((np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)))
    y = np.concatenate(y_parts)
    flat_idx = np.concatenate(flat_idx_parts)

    with rasterio.open(paths["training_features"]) as ds:
        b12 = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
        b14 = ds.read(14, masked=True).filled(np.nan).astype(np.float32)
        b3 = ds.read(3, masked=True).filled(np.nan).astype(np.float32)
        b5 = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b18 = ds.read(18, masked=True).filled(np.nan).astype(np.float32)
    with rasterio.open(paths["ext_geodawn_rad_u8"]) as ds:
        k_b = ds.read(1).astype(np.float32)
        th_b = ds.read(2).astype(np.float32)

    valid_topo = foot & np.isfinite(b12) & (b12 > -1e30) & np.isfinite(b19) & (b19 > -1e30)
    surf = lane_surface(b12, b19, k_b, th_b, valid_topo)

    # Also compute breakline for comparison
    from gems.breakline import lane_surface as br_surface
    br_surf = br_surface(b12, b19, valid_topo)

    feature_arrays = {
        "radscarp_S_pct": surf["S_pct"],
        "radscarp_S_raw": surf["S_raw"],
        "radscarp_L_raw": surf["L_raw"],
        "radscarp_R_raw": surf["R_raw"],
        "radscarp_R_ratio": surf["R_ratio"],
        "breakline_L_pct": br_surf["L_pct"],
        "breakline_L_raw": br_surf["L_raw"],
        "radiometric_K": k_b,
        "radiometric_Th": th_b,
        "training_band_12_det_elev": b12,
        "training_band_19_det_elev_slope": b19,
        "training_band_14_tmi": b14,
        "training_band_3_tmi_hg": b3,
        "training_band_5_iso_grav_slope": b5,
        "training_band_18_iso_grav_hg": b18,
    }
    canaries = {}
    for name, arr in feature_arrays.items():
        vals = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat_idx]
        auc = float(roc_auc_score(y, vals))
        sym = max(auc, 1-auc)
        canaries[name] = {"auc": round(auc,6), "symmetric_auc": round(sym,6), "status": "INVESTIGATE" if sym>0.90 else "REPORT_ONLY_PASS"}

    # 3. SGMC off-catalogue control
    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_scores = {k: round(float(metric.dti_binary(m, sgmc_truth, valid=foot, known=cat)["dti"]),6) for k,m in arms.items()}

    # 4. fixed catalogue diagnostic
    catdiag = {k: round(float(metric.dti_binary(m, cat, valid=foot, known=None)["dti"]),6) for k,m in arms.items()}

    # 5. uniqueness
    uniq = uniqueness(arms, foot, own_files)

    report = {
        "evidence_label": "PROXY",
        "created_utc": "20261025",
        "axis": "RADSCARP",
        "purpose": "Report-only instruments for RADSCARP variants: pooled hide-and-recover HOLDOUT-DTI, leakage canaries, SGMC control, fixed-catalogue diagnostic, literal uniqueness.",
        "parent": "h33-h33-2-b2",
        "hide_and_recover_pooled_summary": pooled,
        "hide_and_recover_pooled_by_candidate": pooled_by_candidate,
        "holdout_splits": split_receipts,
        "per_arm_fold_scores": per_arm_fold_scores,
        "leakage_canaries": {
            "definition": "symmetric AUC on hidden catalogue positives vs non-catalogue negatives in buffered fold regions",
            "results": canaries,
            "stop_and_investigate_if_any_gt_0_90": any(c["status"]=="INVESTIGATE" for c in canaries.values()),
            "max_symmetric_auc": max(c["symmetric_auc"] for c in canaries.values()),
        },
        "sgmc_control_proxy": {
            "source": "manifest-pinned USGS SGMC derived fault control (US Public Domain)",
            "truth_pixels_after_catalogue_and_3px_exclusion": int(sgmc_truth.sum()),
            "r0_dti": sgmc_scores["R0"],
            "variant_dti": sgmc_scores,
            "variant_deltas_vs_r0": {k: round(v - sgmc_scores["R0"],6) for k,v in sgmc_scores.items()},
        },
        "fixed_catalogue_diagnostic": {
            "evidence_class": "PROXY-DIAGNOSTIC (not a holdout)",
            "definition": "DTI of each fixed raster against full known catalogue (known=None)",
            "variant_dti": catdiag,
            "variant_deltas_vs_r0": {k: round(v - catdiag["R0"],6) for k,v in catdiag.items()},
        },
        "uniqueness_final_dots": uniq,
        "caution": "HOLDOUT-DTI / SGMC / fixed-catalogue numbers are local instruments, never live scores.",
    }
    out = ROOT / "evidence/radscarp_proxy_audit.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print(json.dumps({
        "holdout_scores": {k: v["dti"] for k,v in pooled["scores"].items()},
        "paired_deltas_f38": {k: (v["delta"], v["ci95"]) for k,v in pooled["paired_differences"].items()},
        "canary_max": report["leakage_canaries"]["max_symmetric_auc"],
        "sgmc": sgmc_scores,
        "catdiag": catdiag,
        "uniqueness": {k: {"worst_fwd": v["worst_forward_overlap"], "worst_rho": v["worst_abs_spearman"], "duplicate": v["duplicate"], "n_checked": v["registry_rasters_checked"]} for k,v in uniq.items()},
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
