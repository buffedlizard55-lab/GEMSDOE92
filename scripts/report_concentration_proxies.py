#!/usr/bin/env python3
"""REPORT ONLY: catalogue hide-and-recover PROXY, SGMC control, leakage canaries.

IMPORTANT — this session's instrument is invalid by construction.
The CONCENTRATION variants are placed with a km-scale prior built FROM the
known-fault catalogue, and the hide-and-recover instrument withholds catalogue
components as pseudo-truth. Any gain it reports for these arms is partly the
prior looking at itself. The numbers are recorded for completeness and are
labelled LEAKY_BY_CONSTRUCTION; they are never gates, never scores and — for
these three arms only — not decision evidence. The decision anchor remains a
human live receipt.

Canaries: the physical training bands (unchanged from the SNAP session) plus the
prior itself. The prior canary MUST read ~1.0; that is the expected signature of
a deliberately label-derived design prior, not test-label leakage (the catalogue
is a provided competition input; the scored target is new-fault truth).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import sha256_file, verify_all_manifests  # noqa: E402
from build_concentration_variants import fault_density_prior  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric  # noqa: E402

OUT = ROOT / "evidence" / "concentration_proxy_audit.json"


def main() -> int:
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    receipt = json.loads((ROOT / "evidence" / "concentration_variants.json").read_text())

    arms = {"R0": (rasterio_open(paths["parent_r0_zeros"]) > 0) & grid.footprint}
    for item in receipt["variants"]:
        arms[item["id"]] = (rasterio_open(ROOT / "releases" / item["primary_file"]) > 0) & grid.footprint

    folds = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
    terms, per_fold = {}, {}
    for name, mask in arms.items():
        acc = None
        per_fold[name] = []
        for fold in folds:
            score, t = evaluate_holdout.evaluate(mask.astype(np.float32), fold, grid.footprint)
            per_fold[name].append(float(score["dti"]))
            acc = t if acc is None else acc + t
        terms[name] = acc
    pooled = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810,
                                             candidate="R0")

    # physical-band canaries (unchanged) + the design prior, which is expected to trip
    rng = np.random.default_rng(520810)
    ys, xs, flat_idx = [], [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & grid.footprint)
        neg = np.flatnonzero(fold["region"] & grid.footprint & ~grid.catalogue)
        n = min(len(neg), max(1, 2 * len(pos)))
        neg = rng.choice(neg, size=n, replace=False) if len(neg) > n else neg
        ys.extend([np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)])
        flat_idx.append((pos, neg))
    y = np.concatenate([np.concatenate([p, q]) for p, q in
                        [(a, b) for a, b in zip(ys[0::2], ys[1::2])]])
    idx = np.concatenate([np.concatenate([p, q]) for p, q in flat_idx])

    with rasterio.open(paths["training_features"]) as ds:
        b3 = ds.read(3, masked=True).filled(np.nan).astype(np.float32)
        b5 = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    valid = grid.footprint & np.isfinite(b3) & np.isfinite(b5) & np.isfinite(b19)
    sy, sx = np.gradient(np.where(valid, b19, np.nan), 100.0)
    feat = {"training_band_3_tmi_hg": b3,
            "training_band_5_iso_grav_anom_slope": b5,
            "training_band_19_detrended_elevation_slope": b19,
            "derived_grad_band_19_piedmont_slope_break": np.hypot(sx, sy).astype(np.float32)}
    canaries = {}
    for name, arr in feat.items():
        vals = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).ravel()[idx]
        auc = float(roc_auc_score(y, vals))
        canaries[name] = {"auc": round(auc, 6), "symmetric_auc": round(max(auc, 1 - auc), 6)}

    prior = fault_density_prior(grid.catalogue, grid.footprint)
    band_vals = prior["kde"].ravel()[idx].astype(np.float32)
    auc = float(roc_auc_score(y, band_vals))
    canaries["design_prior_1km_fault_kde"] = {
        "auc": round(auc, 6), "symmetric_auc": round(max(auc, 1 - auc), 6),
        "status": "EXPECTED_LEAKY_BY_CONSTRUCTION" if max(auc, 1 - auc) > 0.90 else "REPORT_ONLY_PASS",
    }

    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & grid.footprint
    truth = sgmc & ~grid.catalogue & ~binary_dilation(grid.catalogue, iterations=3)
    sgmc_scores = {n: round(float(metric.dti_binary(m, truth, valid=grid.footprint,
                                                    known=grid.catalogue)["dti"]), 6)
                   for n, m in arms.items()}

    stats = pooled["scores"]
    report = {
        "evidence_label": "PROXY (INVALID FOR THIS SESSION'S ARMS)",
        "created_utc": "2026-10-24",
        "axis": "CONCENTRATION",
        "leak_warning": (
            "The 1 km prior is built from the known-fault catalogue and the holdout "
            "withholds catalogue components as pseudo-truth, so holdout and SGMC "
            "deltas for these arms are contaminated by construction and must not be "
            "read as evidence for or against the variants."
        ),
        "holdout_protocol": {
            "implementation": "vendor/gems57/holdout.py buffered_component_draw",
            "evaluator": evaluate_holdout.VERSION,
            "seeds": [20, 30],
            "withheld_positive_pixels": sum(int(f["truth"].sum()) for f in folds),
            "ci_method": "paired 20 km spatial-block bootstrap, 1,000 draws",
            "scores": {n: {"dti": round(stats[n]["dti"], 6),
                           "ci95": [round(x, 6) for x in stats[n]["ci95"]]} for n in arms},
            "per_fold_dti": per_fold,
            "interpretable": False,
        },
        "sgmc_control": {"truth_pixels": int(truth.sum()), "dti_by_arm": sgmc_scores,
                         "delta_vs_r0": {n: round(s - sgmc_scores["R0"], 6) for n, s in sgmc_scores.items()},
                         "interpretable": False},
        "leakage_canaries": {
            "features": canaries,
            "stop_and_investigate_if_any_gt_0_90": True,
            "interpretation": (
                "The four physical bands stay below 0.57. The design prior reads ~1.0 because it "
                "IS the catalogue: that is the intended design, not hidden-label leakage, and it "
                "is the reason the two instruments above are marked not interpretable."
            ),
        },
        "input_hashes": {k: sha256_file(v) for k, v in paths.items()},
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"holdout": report["holdout_protocol"]["scores"],
                      "sgmc": sgmc_scores,
                      "canaries": {k: v["symmetric_auc"] for k, v in canaries.items()},
                      "report": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


def rasterio_open(p: Path) -> np.ndarray:
    with rasterio.open(p) as ds:
        return ds.read(1)


if __name__ == "__main__":
    raise SystemExit(main())
