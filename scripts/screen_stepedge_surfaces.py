#!/usr/bin/env python3
"""Pre-registered screen for the STEPEDGE-session surfaces (2026-10-24).

Identical instruments to the preserved GRAVCrest screen design
(evidence/gravcrest_screen.json) and to scripts/report_breakline_proxies.py:
(a) single-feature symmetric-AUC leakage canary vs withheld catalogue
positives (buffered-component folds, seeds 20/30, rng 520810);
(b) a 16,944-dot spaced top-set (2.8 px floor, >3 px off H19-5, d_cat>2 px)
scored alone as PROXY on off-catalogue USGS SGMC bedrock faults and on the
fixed-catalogue diagnostic; (c) far-set forward overlap vs the far dots of
BREAKLINE f45 / ANASIG f45 / STRAINBREAK f60 (lane-disjointness).

Gate zero: the BREAKLINE-L control must reproduce sym AUC 0.621604 and
far-only SGMC 0.072325 before any new number is trusted. Prior sessions ran
their screens from .cache and lost the code; this screen is preserved here.

Every number written is PROXY-SCREEN. Nothing here is a competition score.
Pre-registration: docs/HYPOTHESES_20261024_STEPEDGE.md.
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

from build_snap_scarp_variants import build_and_verify_parent, verify_all_manifests
from gems.breakline import lane_surface as breakline_surface, percentile_rank
from gems.stepedge import lane_surface as stepedge_surface, spaced_top_mask, transversality
from gems57 import grid as grid_mod, holdout, metric

N_FAR = 16944
BASELINE_EXPECTED = {"sym_auc": 0.621604, "far_only_sgmc_dti": 0.072325}


def load_mask(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        return (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot


def main() -> int:
    inputs = verify_all_manifests()
    foot, cat, d_cat, h19, bundle = build_and_verify_parent(inputs)
    r0 = bundle["r0"]
    grid = grid_mod.load_grid(ROOT / ".cache/gems_inputs/bridge")
    assert np.array_equal(grid.footprint, foot) and np.array_equal(grid.catalogue, cat)

    with rasterio.open(inputs["training_features"]) as ds:
        b12 = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    valid_topo = foot & np.isfinite(b12) & (b12 > -1e30) & np.isfinite(b19) & (b19 > -1e30)

    print("Building surfaces ...")
    bl = breakline_surface(b12, b19, valid_topo)
    se = stepedge_surface(b12, valid_topo)                      # persistent (near+far)
    se_near = stepedge_surface(b12, valid_topo, groups=((2.0, 3.0),))
    transv = transversality(b12, valid_topo, se["u_row"], se["u_col"])

    # RADSTEP: max over K/Th/U/TC of percentile-ranked gradient magnitude.
    with rasterio.open(inputs["ext_geodawn_rad_u8"]) as ds:
        rad_valid = foot.copy()
        rad_edge_pct = np.zeros(b12.shape, np.float32)
        for band in (1, 2, 3, 4):
            rb = ds.read(band).astype(np.float32)
            rad_valid &= rb > 0
            gy, gx = np.gradient(rb)
            rad_edge_pct = np.maximum(rad_edge_pct,
                                      percentile_rank(np.hypot(gy, gx), foot & (rb > 0)))
            del rb, gy, gx
    radstep_raw = np.sqrt(np.maximum(se["step_pct"], 0) * rad_edge_pct) * se["coherence"]
    radstep_valid = valid_topo & rad_valid

    transv_raw = bl["L_raw"] * (0.2 + 0.8 * transv)
    surfaces: dict[str, tuple[np.ndarray, np.ndarray]] = {
        # name -> (surface for canary/ranking, valid mask)
        "breakline_L_baseline": (bl["L_pct"], valid_topo),
        "stepedge_persistent": (se["S_pct"], valid_topo),
        "stepedge_near_only": (se_near["S_pct"], valid_topo),
        "transv_L_x_transv": (percentile_rank(transv_raw, valid_topo), valid_topo),
        "radstep_concordance": (percentile_rank(radstep_raw, radstep_valid), radstep_valid),
        "stepedge_step_only_no_coh": (se["step_pct"], valid_topo),
    }
    del bl, se_near, transv, transv_raw, radstep_raw

    # ---- canary sampling (identical construction to report_breakline_proxies)
    folds = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
    rng = np.random.default_rng(520810)
    y_parts, sample_idx = [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & foot)
        neg = np.flatnonzero(fold["region"] & foot & ~cat)
        n = min(len(neg), max(1, 2 * len(pos)))
        neg = rng.choice(neg, size=n, replace=False) if len(neg) > n else neg
        sample_idx.extend((pos, neg))
        y_parts.extend((np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)))
    y = np.concatenate(y_parts)
    flat_idx = np.concatenate(sample_idx)

    # ---- truths and far pool
    with rasterio.open(inputs["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & ~cat & ~binary_dilation(cat, iterations=3)
    d_h19 = distance_transform_edt(~h19)

    prior_fars: dict[str, np.ndarray] = {}
    for name, rel in {
        "breakline_f45": "docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif",
        "anasig_f45": "docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif",
        "strainbreak_f60": "docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif",
    }.items():
        prior_fars[name] = load_mask(ROOT / rel, foot) & (d_h19 > 3.0)
    prior_far_edt = {k: distance_transform_edt(~v) for k, v in prior_fars.items()}

    results: dict[str, dict] = {}
    for name, (surf, valid) in surfaces.items():
        vals = np.nan_to_num(surf, nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat_idx]
        auc = float(roc_auc_score(y, vals))
        far_cand = foot & valid & (d_cat > 2.0) & (d_h19 > 3.0) & (~r0)
        far = spaced_top_mask(surf, far_cand, N_FAR)
        row = {
            "sym_auc": round(max(auc, 1 - auc), 6),
            "auc": round(auc, 6),
            "far_only_sgmc_dti": round(float(metric.dti_binary(
                far, sgmc_truth, valid=foot, known=cat)["dti"]), 6),
            "far_only_fixedcat_dti": round(float(metric.dti_binary(
                far, cat, valid=foot, known=None)["dti"]), 6),
            "far_pool": int(far_cand.sum()),
            "far_overlap_vs_prior_lanes": {
                k: round(float(np.mean(edt[far] <= 3.0)), 6)
                for k, edt in prior_far_edt.items()},
        }
        results[name] = row
        print(name, row)

    base = results["breakline_L_baseline"]
    reproduced = (abs(base["sym_auc"] - BASELINE_EXPECTED["sym_auc"]) < 5e-4
                  and abs(base["far_only_sgmc_dti"] - BASELINE_EXPECTED["far_only_sgmc_dti"]) < 5e-4)
    report = {
        "evidence_class": "PROXY-SCREEN",
        "n_far": N_FAR,
        "sgmc_truth_px": int(sgmc_truth.sum()),
        "baseline_expected": BASELINE_EXPECTED,
        "baseline_reproduced_within_5e-4": bool(reproduced),
        "surfaces": results,
        "preregistered_rule": (
            "Build best non-baseline by far_only_sgmc_dti if sym_auc<=0.90, "
            "far SGMC >= 0.5*baseline, and far overlap vs every prior lane <=0.70."),
    }
    out = ROOT / "evidence/stepedge_screen.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"baseline_reproduced": reproduced, "written": str(out)}, indent=2))
    return 0 if reproduced else 2


if __name__ == "__main__":
    raise SystemExit(main())
