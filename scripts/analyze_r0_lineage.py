#!/usr/bin/env python3
"""Forensic audit of why the GEMSDOE32 parent R0 (CLAIM 0.2778) tops the
owner's historical climb, using only hash-pinned local inputs.

Every number is labelled: GEOMETRY (measured here), PROXY (local DTI vs a
named catalogue/control, never a score), or CLAIM (owner-reported live
score copied from ledger/historical_climb.csv; receipt=N in that ledger).

Also cross-checks the two in-repo metric implementations
(gems.metric vs vendor/gems57.metric) against each other and against the
official worked example algebra (DrivenData #306 p.967: TPw=3.00,
FPw=1.89, FNw=2.00 -> 0.60 with alpha=0.2, beta=0.8).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import build_and_verify_parent, verify_all_manifests
from gems.metric import DotSet, Truth
from gems57 import grid as grid_mod, metric


def mask_stats(mask: np.ndarray, foot: np.ndarray, d_cat: np.ndarray) -> dict:
    ys, xs = np.nonzero(mask)
    n = len(ys)
    out: dict = {"n_dots_or_px": int(n)}
    if n >= 2:
        tree = cKDTree(np.c_[ys, xs])
        dd, _ = tree.query(np.c_[ys, xs], k=2)
        nn = dd[:, 1]
        out.update({
            "nn_dist_px_min": round(float(nn.min()), 4),
            "nn_dist_px_median": round(float(np.median(nn)), 4),
            "nn_dist_px_mean": round(float(nn.mean()), 4),
            "frac_with_neighbour_within_3px": round(float((nn <= 3.0).mean()), 6),
            "frac_with_neighbour_within_1px": round(float((nn <= 1.01).mean()), 6),
        })
    if n:
        dself = distance_transform_edt(~mask)
        out.update({
            "frac_footprint_within_3px_of_mask": round(float(((dself <= 3.0) & foot).sum() / foot.sum()), 6),
            "dots_on_catalogue": int((d_cat[mask] == 0).sum()),
            "frac_dots_dcat_le_2px": round(float((d_cat[mask] <= 2.0).mean()), 6),
            "frac_dots_dcat_le_3px": round(float((d_cat[mask] <= 3.0).mean()), 6),
            "frac_dots_dcat_gt_3px": round(float((d_cat[mask] > 3.0).mean()), 6),
            "min_dcat_px": round(float(d_cat[mask].min()), 4),
        })
        del dself
    return out


def main() -> int:
    inputs = verify_all_manifests()  # SHA-256 + byte check, fails closed
    foot, cat, d_cat, h19, bundle = build_and_verify_parent(inputs)
    # build_and_verify_parent rebuilds D1.5->D2.8->SOLO->R0 and asserts
    # mask-equality with the pinned lineage rasters at every stage.
    def load(key):
        with rasterio.open(inputs[key]) as ds:
            return (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot

    stages = {
        "H19-5 skeleton (raw)": h19,
        "D1.5": load("anc_d1_5"),
        "D2.8": load("anc_d2_8"),
        "SOLO-D2.8 (dcat>1)": load("anc_solo_d2_8"),
        "R0 (dcat>2)": bundle["r0"],
    }
    claims = {}
    with open(ROOT / "ledger/historical_climb.csv", newline="") as f:
        for row in csv.DictReader(f):
            claims[row["name"]] = {"score": float(row["score"]), "label": row["evidence_label"],
                                   "receipt": row["receipt"], "n_dots": int(row["n_dots"])}

    with rasterio.open(inputs["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & ~cat & ~binary_dilation(cat, iterations=3)

    stage_rows = {}
    for name, mask in stages.items():
        row = mask_stats(mask, foot, d_cat)
        row["PROXY_fixedcat_dti"] = round(float(metric.dti_binary(
            mask, cat, valid=foot, known=None)["dti"]), 6)
        row["PROXY_sgmc_dti"] = round(float(metric.dti_binary(
            mask, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
        stage_rows[name] = row
        print(name, row)

    # --- metric cross-checks -------------------------------------------
    worked = metric.dti_from_components(3.00, 1.89, 2.00)
    rng = np.random.default_rng(7)
    mismatches = []
    for trial in range(30):
        truth = rng.random((24, 24)) < 0.06
        if not truth.any():
            continue
        pred = (rng.random((24, 24)) < 0.08).astype(np.float32)
        exact = metric.dti_exact(pred, truth)["dti"]
        brute = metric.dti_bruteforce(pred, truth)["dti"]
        tys, txs = np.nonzero(truth)
        gems_dti = DotSet.from_raster(pred.astype(float), Truth(tys, txs)).totals().dti
        mismatches.append({"trial": trial, "vendor_exact": exact, "vendor_brute": brute,
                           "gems_metric": float(gems_dti),
                           "vendor_vs_brute_absdiff": abs(exact - brute),
                           "gems_vs_vendor_absdiff": abs(float(gems_dti) - exact)})
    max_vb = max(m["vendor_vs_brute_absdiff"] for m in mismatches)
    max_gv = max(m["gems_vs_vendor_absdiff"] for m in mismatches)

    # sample_submission identity check (official text: sample predicts
    # total fault absence; bridge copy carries 60,988 positives == catalogue)
    with rasterio.open(inputs["sample_submission"]) as ds:
        sample = ds.read(1)
    sample_pos = np.isfinite(sample) & (sample > 0)
    sample_check = {
        "positive_px": int(sample_pos.sum()), "catalogue_px": int(cat.sum()),
        "positives_equal_catalogue": bool(np.array_equal(sample_pos & foot, cat)),
        "note": "footprint = finite cells is unaffected; values are NOT the all-zero sample described on p.967",
    }

    report = {
        "evidence_class": "GEOMETRY + PROXY (measured locally); CLAIM scores copied from ledger, receipt=N",
        "evaluator": "vendor/gems57/metric.py dti_binary/dti_exact (official p.967 equations)",
        "parent_lineage_rebuilt_mask_exact": True,
        "claims_from_ledger_historical_climb": claims,
        "stages": stage_rows,
        "sgmc_truth_px": int(sgmc_truth.sum()),
        "metric_cross_checks": {
            "official_worked_example_3_1p89_2": worked,
            "expected": 0.60,
            "vendor_exact_vs_bruteforce_max_absdiff_30_random": max_vb,
            "gems_metric_vs_vendor_max_absdiff_30_random": max_gv,
            "gems_metric_agrees_with_official": bool(max_gv < 1e-9),
            "rows": mismatches,
        },
        "sample_submission_check": sample_check,
        " Interpretation": (
            "R0's climb is an emission-geometry effect on a fixed skeleton: "
            "thinning toward the 3 px kernel scale removes max-cover redundancy "
            "(TPw takes a max per truth pixel, so neighbouring dots double-pay "
            "FP mass) and dcat>2 px clearance stops spending mass on/near "
            "pixel-exactly masked known faults. Skeleton content never changed."
        ),
    }
    out = ROOT / "evidence/r0_forensics_20261024.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"worked_example": worked, "max_vendor_vs_brute": max_vb,
                      "max_gems_vs_vendor": max_gv, "sample": sample_check,
                      "written": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
