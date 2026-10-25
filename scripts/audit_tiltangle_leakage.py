#!/usr/bin/env python3
"""Audit the merged TILTANGLE artifact for Protocol Rule 1, 2, 3, 4 & 5 compliance.

Verifies from disk without modifying the historical TIFF bytes:
1. Protocol Rule 4 (Leakage Canary):
   - Pure gravity surface components (`hgm`, `tilt`, `s_raw`, `S`) are catalogue-free
     and pass (`max symmetric AUC = 0.526594 <= 0.90`).
   - However, `scripts/build_tiltangle_submission.py` multiplied `S` by
     `d_pref = clip(1 - (d_cat - 3)/12, 0, 1)` computed from the FULL
     `existing_faults.tif` catalogue (including the withheld faults) before
     static evaluation. Because `d_cat == 0` on every withheld fault,
     `d_pref == 1.0` on 100% of withheld fault pixels and has symmetric
     `AUC = 0.962399 > 0.90` (FAIL: target leakage).
2. Protocol Rule 2 & 3 (Holdout DTI with 95% CI via `vendor/gems57/evaluate_holdout.py`,
   `gems57-pooled-hide-v2`, 22,663 withheld positives, 1,000-draw paired spatial-block
   bootstrap):
   - Leaked static raster (`gemsdoe92-tiltangle-tiltangle-37654-20261025T182301Z-zeros.tif`):
     `0.031591 [0.028908, 0.034083]` (invalidated by full-catalogue `d_pref` leakage).
   - Leak-free static `d_cat > 2.0` on pure `S` (no `d_pref` halo):
     `0.005272 [0.003786, 0.006778]` (paired delta vs `R0` `0.004006` is
     `+0.001266 [-0.000246, +0.002801]`, 95% CI includes 0; below `COULOMBDM`
     `0.007816`, `KNICKLOQO` `0.010788`, and `LISTRICLOQO` `0.013295`).
   - Leak-free strict fold-visible Rule-2 `d_visible > 2.0` with `d_pref` derived
     strictly from `fold["visible"]`:
     `0.085247 [0.072361, 0.097824]` (below `H19-5` `0.096757`, `COULOMBLOQO`
     `0.113316`, `LISTRICLOQO` `0.114410`, and `FAULTNET` `0.175147`).
   - Leak-free strict fold-visible Rule-2 `d_visible > 2.0` on pure `S`:
     `0.042670 [0.030209, 0.055396]`.
3. Protocol Rule 1 (Registry Uniqueness):
   - Local registry (141 other valid exact-grid rasters): worst 3-px dot-field
     forward overlap is `0.776332 > 0.70` vs
     `docs/downloads/gemsdoe92-netexpand-netexpand-37654-20261025-f705be3a-zeros.tif`
     and `0.761513 > 0.70` vs
     `docs/downloads/gemsdoe92-netexpand-netexpandfar-37654-20261025-47bacc15-zeros.tif`
     (FAIL: local dot-field duplicate); worst surface `|Spearman rho| = 0.073692 <= 0.90`.
   - Pinned public dense witness (`17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif`,
     `5,167,373` positive footprint pixels): literal 3-px forward overlap `1.0000 > 0.70`
     (FAIL: literal duplicate stop).
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems.breakline import spaced_top_mask  # noqa: E402
from gems.tiltangle import lane_surface  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, uniqueness as U  # noqa: E402

TIF_REL = "docs/downloads/gemsdoe92-tiltangle-tiltangle-37654-20261025T182301Z-zeros.tif"
RUN_CARD_REL = "docs/downloads/gemsdoe92-tiltangle-tiltangle-37654-20261025T182301Z-zeros_run_card.json"
AUDIT_OUT = ROOT / "evidence" / "tiltangle_audit_20261025.json"
STACK_PATH = ROOT / ".cache" / "gems_inputs" / "training_features.tif"
N_DOTS = 37_654
MIN_DIST_PX = 2.8


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def symmetric_auc(scores: np.ndarray, labels: np.ndarray) -> tuple[float, float]:
    pos = scores[labels]
    neg = scores[~labels]
    all_s = np.concatenate([pos, neg])
    ranks = rankdata(all_s, method="average").astype(np.float64)
    auc = float((ranks[: pos.size].sum() - pos.size * (pos.size + 1) / 2.0) / (pos.size * neg.size))
    return auc, float(max(auc, 1.0 - auc))


def main() -> int:
    grid = grid_mod.load_grid()
    foot, cat = grid.footprint, grid.catalogue
    tif_path = ROOT / TIF_REL
    tif_sha = sha256_file(tif_path)

    with rasterio.open(tif_path) as ds:
        ta_arr = ds.read(1).astype(np.float32)
        expected_grid = (ds.shape, ds.crs, ds.transform)
    with rasterio.open(ROOT / "data/parent_R0_zeros.tif") as ds:
        r0_arr = ds.read(1).astype(np.float32)

    surf = lane_surface(str(STACK_PATH), foot)
    valid = surf["valid"]
    S = surf["S"].astype(np.float32)

    d_cat_full = ndi.distance_transform_edt(~(cat & foot)).astype(np.float32)
    d_pref_full = np.clip(1.0 - (d_cat_full - 3.0) / 12.0, 0.0, 1.0).astype(np.float32)
    allowed_full = valid & ~cat & (d_cat_full > 2.0)
    pred_pure_static = spaced_top_mask(
        S, allowed_full, N_DOTS, min_dist_px=MIN_DIST_PX, cand_cap=900_000
    ).astype(np.float32)

    folds = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)

    held_union = np.zeros(foot.shape, dtype=bool)
    vis_union = np.zeros(foot.shape, dtype=bool)
    for fold in folds:
        held_union |= np.asarray(fold["truth"], bool)
        vis_union |= np.asarray(fold["visible"], bool)

    eval_mask = valid & ~vis_union
    labels = held_union[eval_mask]

    canary_rows = {}
    for name, arr in (
        ("hgm", surf["hgm"]),
        ("tilt_deg", surf["tilt"]),
        ("s_raw", surf["s_raw"]),
        ("S_percentile_rank", S),
        ("d_pref_full_catalogue_LEAKED", d_pref_full),
    ):
        raw_auc, sym_auc = symmetric_auc(arr[eval_mask], labels)
        canary_rows[name] = {
            "raw_auc": round(raw_auc, 6),
            "symmetric_auc": round(sym_auc, 6),
            "pass_le_0p90": bool(sym_auc <= 0.90),
        }

    surface_max_auc = max(
        canary_rows[k]["symmetric_auc"] for k in ("hgm", "tilt_deg", "s_raw", "S_percentile_rank")
    )
    overall_max_auc = max(r["symmetric_auc"] for r in canary_rows.values())

    terms_by_arm = {
        "TILTANGLE_static_leaked_dpref": None,
        "TILTANGLE_pure_static_dcat2": None,
        "TILTANGLE_vis_dpref_rule2": None,
        "TILTANGLE_pure_rule2": None,
        "R0": None,
    }
    for fold in folds:
        vis = np.asarray(fold["visible"], bool)
        d_vis = ndi.distance_transform_edt(~(vis & foot)).astype(np.float32)
        allowed_vis = valid & ~vis & (d_vis > 2.0)
        d_pref_vis = np.clip(1.0 - (d_vis - 3.0) / 12.0, 0.0, 1.0).astype(np.float32)
        w_vis = (S * d_pref_vis).astype(np.float32)
        w_vis[~allowed_vis] = 0.0
        pred_vis_dpref = spaced_top_mask(
            w_vis, allowed_vis, N_DOTS, min_dist_px=MIN_DIST_PX, cand_cap=900_000
        ).astype(np.float32)
        pred_pure_rule2 = spaced_top_mask(
            S, allowed_vis, N_DOTS, min_dist_px=MIN_DIST_PX, cand_cap=900_000
        ).astype(np.float32)
        for arm_name, arr in (
            ("TILTANGLE_static_leaked_dpref", ta_arr),
            ("TILTANGLE_pure_static_dcat2", pred_pure_static),
            ("TILTANGLE_vis_dpref_rule2", pred_vis_dpref),
            ("TILTANGLE_pure_rule2", pred_pure_rule2),
            ("R0", r0_arr),
        ):
            _, t = evaluate_holdout.evaluate(arr, fold, foot)
            old = terms_by_arm[arm_name]
            terms_by_arm[arm_name] = t if old is None else old + t

    summary_static = evaluate_holdout.pooled_summary(
        {k: terms_by_arm[k] for k in ("TILTANGLE_pure_static_dcat2", "TILTANGLE_static_leaked_dpref", "R0")},
        draws=1000,
        seed=520810,
        candidate="TILTANGLE_pure_static_dcat2",
    )
    summary_rule2 = evaluate_holdout.pooled_summary(
        {k: terms_by_arm[k] for k in ("TILTANGLE_vis_dpref_rule2", "TILTANGLE_pure_rule2", "R0")},
        draws=1000,
        seed=520810,
        candidate="TILTANGLE_vis_dpref_rule2",
    )

    # Local registry uniqueness scan
    dot_mask = ta_arr > 0
    foot_idx = np.flatnonzero(foot)
    sub = np.sort(np.random.default_rng(20261025).choice(foot_idx, size=400_000, replace=False))
    surf_sub = S.ravel()[sub].astype(np.float32)
    ta_sub = ta_arr.ravel()[sub].astype(np.float32)

    local_over_70 = []
    worst_ovl = 0.0
    worst_ovl_file = None
    worst_surf_rho = 0.0
    worst_surf_rho_file = None
    worst_final_rho = 0.0
    worst_final_rho_file = None
    n_local = 0

    for folder in (ROOT / "docs/downloads", ROOT / "releases", ROOT / "data", ROOT / "data/bridge"):
        for p in sorted(folder.glob("*.tif")):
            if "tiltangle" in p.name:
                continue
            if p.name in ("sample_submission.tif", "existing_faults.tif", "labels.tif"):
                continue
            try:
                with rasterio.open(p) as ds:
                    if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected_grid:
                        continue
                    raw = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
            except Exception:
                continue
            sup = (raw > 0) & foot
            if not sup.any():
                continue
            n_local += 1
            rel = str(p.relative_to(ROOT))
            ovl = float(U._near(sup, 3.0)[dot_mask].mean())
            tv = raw.ravel()[sub]
            s_rho = abs(float(spearmanr(surf_sub, tv).statistic)) if np.ptp(tv) else 0.0
            f_rho = abs(float(spearmanr(ta_sub, tv).statistic)) if np.ptp(tv) else 0.0
            if ovl > worst_ovl:
                worst_ovl, worst_ovl_file = ovl, rel
            if s_rho > worst_surf_rho:
                worst_surf_rho, worst_surf_rho_file = s_rho, rel
            if f_rho > worst_final_rho:
                worst_final_rho, worst_final_rho_file = f_rho, rel
            if ovl > 0.70:
                local_over_70.append(
                    {"file": rel, "forward_3px_overlap": round(ovl, 6), "their_positive_pixels": int(sup.sum())}
                )

    local_over_70.sort(key=lambda r: r["forward_3px_overlap"], reverse=True)

    uniqueness_block = {
        "evidence_class": "REGISTRY-MEASUREMENT",
        "unique_under_literal_rule": False,
        "local_dot_field_duplicate": bool(worst_ovl > 0.70),
        "stop_required": True,
        "local_rasters_checked": n_local,
        "local_worst_forward_3px_overlap": round(worst_ovl, 6),
        "local_worst_forward_3px_overlap_raster": worst_ovl_file,
        "local_rasters_over_0p70": local_over_70,
        "local_worst_abs_spearman_surface": round(worst_surf_rho, 6),
        "local_worst_abs_spearman_surface_raster": worst_surf_rho_file,
        "local_worst_abs_spearman_final": round(worst_final_rho, 6),
        "local_worst_abs_spearman_final_raster": worst_final_rho_file,
        "public_dense_witness_forward_overlap": 1.0,
        "public_dense_witness_raster": "buffedlizard55-lab/17GEMSDOE:docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif",
        "public_dense_witness_git_blob_sha": "374c88b1da2b803e2ed160de467fd71ae114010d",
        "public_dense_witness_sha256": "ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be",
        "threshold_overlap": 0.70,
        "threshold_abs_rho": 0.90,
    }

    leakage_block = {
        "threshold_symmetric_auc": 0.90,
        "surface_only_max_symmetric_auc": round(surface_max_auc, 6),
        "surface_only_all_pass": bool(surface_max_auc <= 0.90),
        "overall_max_symmetric_auc": round(overall_max_auc, 6),
        "overall_all_pass": bool(overall_max_auc <= 0.90),
        "withheld_fault_fraction_with_d_pref_eq_1": float((d_pref_full[eval_mask][labels] == 1.0).mean()),
        "finding": (
            "Pure gravity surface features pass (max symmetric AUC 0.526594 <= 0.90), "
            "but scripts/build_tiltangle_submission.py multiplied S by d_pref computed from "
            "the full existing_faults.tif catalogue (including withheld faults) before static "
            "holdout scoring. Full-catalogue d_pref has symmetric AUC 0.962399 > 0.90 (FAIL: "
            "target leakage), inflating the static holdout figure from 0.005272 (pure S) to "
            "0.031591 (buffered) / 0.033466 (unbuffered)."
        ),
        "features": canary_rows,
    }

    audit_doc = {
        "schema": "gemsdoe92-tiltangle-audit-v1",
        "reviewed_utc": datetime.now(timezone.utc).isoformat(),
        "lane": "TILTANGLE",
        "file": TIF_REL,
        "raster_sha256": tif_sha,
        "verdict": "negative",
        "submission_eligible": False,
        "leakage_canaries": leakage_block,
        "correlation_overlap_vs_registry": uniqueness_block,
        "holdout_dti_recomputed": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": evaluate_holdout.VERSION,
            "withheld_positive_pixels": 22663,
            "pure_surface_static_dcat2": summary_static["scores"]["TILTANGLE_pure_static_dcat2"],
            "pure_surface_static_paired_vs_R0": summary_static["paired_differences"]["R0"],
            "visible_only_dpref_rule2_dvis2": summary_rule2["scores"]["TILTANGLE_vis_dpref_rule2"],
            "visible_only_dpref_rule2_paired_vs_R0": summary_rule2["paired_differences"]["R0"],
            "pure_surface_rule2_dvis2": summary_rule2["scores"]["TILTANGLE_pure_rule2"],
            "leaked_full_catalogue_dpref_static_INVALID": summary_static["scores"]["TILTANGLE_static_leaked_dpref"],
            "R0_control": summary_static["scores"]["R0"],
        },
    }
    AUDIT_OUT.write_text(json.dumps(audit_doc, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    # Update the served TILTANGLE run card so it carries all mandatory Protocol Rule 5 fields
    rc_path = ROOT / RUN_CARD_REL
    rc = json.loads(rc_path.read_text(encoding="utf-8"))
    rc["raster_sha256"] = tif_sha
    rc["submission_name"] = rc["submission"]["name"]
    rc["note"] = (
        "h33-h33-2-b2; TILTANGLE research only (DO NOT SUBMIT): gravity edge x collar; "
        "pure static HOLDOUT-DTI 0.005272; duplicate"
    )
    rc["submission"]["note"] = rc["note"]
    rc["submission"]["note_chars"] = len(rc["note"])
    rc["submission_eligible"] = False
    rc["verdict"] = "negative"
    rc["named_non_fault_process_that_could_mimic_it"] = rc["non_fault_mimic"]
    rc["validator_output"] = rc["format_validation"]
    rc["leakage_canaries"] = leakage_block
    rc["correlation_overlap_vs_registry"] = uniqueness_block
    rc["holdout_dti"] = {
        "evidence_class": "HOLDOUT-DTI",
        "evaluator_version": evaluate_holdout.VERSION,
        "alpha": 0.2,
        "beta": 0.8,
        "triangular_radius_m": 300.0,
        "withheld_positive_pixels": 22663,
        "dti": summary_static["scores"]["TILTANGLE_pure_static_dcat2"]["dti"],
        "ci95": summary_static["scores"]["TILTANGLE_pure_static_dcat2"]["ci95"],
        "paired_vs_R0": summary_static["paired_differences"]["R0"],
        "strict_draw_blind_dvis2_with_visible_dpref_dti": summary_rule2["scores"]["TILTANGLE_vis_dpref_rule2"]["dti"],
        "strict_draw_blind_dvis2_with_visible_dpref_ci95": summary_rule2["scores"]["TILTANGLE_vis_dpref_rule2"]["ci95"],
        "strict_draw_blind_dvis2_pure_surface_dti": summary_rule2["scores"]["TILTANGLE_pure_rule2"]["dti"],
        "strict_draw_blind_dvis2_pure_surface_ci95": summary_rule2["scores"]["TILTANGLE_pure_rule2"]["ci95"],
        "invalidated_leaked_full_catalogue_dpref_static": {
            "buffered_22663_dti": summary_static["scores"]["TILTANGLE_static_leaked_dpref"]["dti"],
            "buffered_22663_ci95": summary_static["scores"]["TILTANGLE_static_leaked_dpref"]["ci95"],
            "unbuffered_45253_dti": 0.03346643401066433,
            "invalidated_reason": (
                "Full-catalogue d_pref used existing_faults.tif (including withheld faults) "
                "and failed the Protocol Rule 4 leakage canary with symmetric AUC 0.962399 > 0.90."
            ),
        },
    }
    rc["notes"] = (
        "Format-valid research TIFF; DO NOT SUBMIT. Audited 2026-10-25: (1) the original "
        "0.033466 static figure used d_pref computed from the full catalogue including withheld "
        "faults (canary symmetric AUC 0.962399 > 0.90, target leakage); leak-free pure-surface "
        "static HOLDOUT-DTI is 0.005272 [0.003786, 0.006778] and strict fold-visible Rule-2 "
        "HOLDOUT-DTI is 0.085247 [0.072361, 0.097824] (with visible-only d_pref) / 0.042670 "
        "[0.030209, 0.055396] (pure S), all below repository holdout-best; (2) fails local "
        "3-px dot-field uniqueness (0.776332 > 0.70 vs NETEXPAND netexpand) and literal "
        "dense-witness overlap (1.0000 > 0.70)."
    )
    rc_path.write_text(json.dumps(rc, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"WROTE {AUDIT_OUT} and updated {rc_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
