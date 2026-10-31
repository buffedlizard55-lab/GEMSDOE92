#!/usr/bin/env python3
"""Emit the byte-bound JSON run card for the GX lane (parallel-run rule 5)."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

HOLD = json.loads((ROOT / "evidence" / "gx_holdout.json").read_text())
EVAL = json.loads((ROOT / "evidence" / "gx_candidate_eval.json").read_text())
CAND = json.loads((ROOT / "evidence" / "gx_candidate.json").read_text())
SCREEN = json.loads((ROOT / "evidence" / "gx_band_screen.json").read_text())
EST = json.loads((ROOT / "evidence" / "gx_score_estimator.json").read_text())

hl = HOLD["pooled"]["scores"]
best_arm = max((k for k in hl if k.startswith("gx_")), key=lambda k: hl[k]["dti"])
best, r0, rnd = hl[best_arm], hl["r0_recipe"], hl["random"]
diff = HOLD["pooled"]["paired_differences"]["r0_recipe"]
uniq = EVAL["uniqueness"]
est = EVAL["estimate"]
sha = EVAL["sha256"]
can_max = max(c["auc_holdout"] for c in HOLD["canaries"])

sites = sorted(EST["files"])


def spearman(a, b):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2.0 + 1
            i = j + 1
        return r
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else float("nan")


rho_hc = spearman([EST["files"][s]["t_per_dot"] for s in sites],
                  [EST["files"][s]["claim"] for s in sites])

card = {
    "schema": "gemsdoe92-run-card.v1",
    "lane": "GX — external-layer fault-appearance model",
    "session_utc": "2026-10-31",
    "branch": "arena/59d25039-gemsdoe92",
    "hypothesis": (
        "A fault-appearance model fitted on public, externally sourced layers only "
        "(1 m-lidar scarp operators, GeoDAWN radiometrics and TMI, USGS SGMC faults, GDR "
        "thermal indicators) recovers withheld whole fault segments better than the R0 "
        "recipe (the H19-5-skeleton thinning that produced the 0.2778 claim), and the "
        "resulting dot field is unique against the public registry."
    ),
    "mechanism": (
        "47 ranked layers (value, horizontal-gradient magnitude and ridgeness of five "
        "lidar-scarp bands at 150 m and 350 m; value and gradient magnitude of five "
        "GeoDAWN bands; orientation coherence, axial strike, lidar validity, log-distance "
        "to SGMC and to thermal indicators) feed a logistic regression refit on every "
        "holdout draw from that draw's visible catalogue only. Dots are emitted by "
        "probability-ordered thinning at 2.5 px spacing to a 50,000 budget, keeping only "
        "cells more than 2 px from the mapped catalogue."
    ),
    "named_non_fault_mimic": (
        "Pleistocene shorelines, alluvial-fan terrace edges and road/rail cuts produce the "
        "same scarp-step and curvature signature; radiometric contacts and flight-line seams "
        "mimic geophysical lineaments."
    ),
    "experiments_used": 3,
    "weekly_slots_spent": 0,
    "holdout": {
        "evidence_class": "HOLDOUT-DTI",
        "evaluator": HOLD["evaluator"],
        "n_draws": HOLD["n_draws"],
        "seeds": HOLD["seeds"],
        "withheld_positive_pixels": best["withheld_positive_pixels"],
        "candidate_arm": best_arm,
        "candidate_dti": round(best["dti"], 6),
        "candidate_ci95": [round(x, 6) for x in best["ci95"]],
        "r0_recipe_dti": round(r0["dti"], 6),
        "r0_recipe_ci95": [round(x, 6) for x in r0["ci95"]],
        "random_dti": round(rnd["dti"], 6),
        "paired_candidate_minus_r0": {
            "delta": round(diff["delta"], 6),
            "ci95": [round(x, 6) for x in diff["ci95"]],
        },
        "note": (
            "Fold-proper: the emission mask uses distance to the VISIBLE catalogue. The "
            "deployed raster uses distance to the FULL catalogue (as the real task "
            "requires), so the deployed file's own holdout number "
            f"({EVAL['holdout']['scores']['candidate']['dti']:.6f}) is structurally "
            "depressed by the instrument and is NOT comparable with this control."
        ),
    },
    "leakage_canaries": {
        "n_features": len(HOLD["canaries"]),
        "max_solo_holdout_auc": round(can_max, 4),
        "threshold": 0.90,
        "features_dropped": HOLD["features_dropped"],
        "pass": bool(can_max <= 0.90),
    },
    "correlation_and_overlap_vs_registry": {
        "evidence_class": "REGISTRY-MEASUREMENT",
        "n_registry_sha256": uniq["n_registry"],
        "worst_dot_field_overlap": uniq["worst_by_representation"]["dot_field"]["max"],
        "dot_fields_above_0_70": uniq["worst_by_representation"]["dot_field"]["n_above_070"],
        "worst_continuous_surface_overlap": uniq["worst_by_representation"]["continuous_surface"]["max"],
        "worst_dense_lattice_overlap": uniq["worst_by_representation"]["dense_binary_lattice"]["max"],
        "dense_lattices_above_0_70": uniq["worst_by_representation"]["dense_binary_lattice"]["n_above_070"],
        "max_abs_spearman_full_footprint": uniq["max_abs_spearman"],
        "overlap_vs_focus_nine": {k: v["overlap"] for k, v in sorted(uniq["focus_nine"].items())},
        "literal_reading_note": (
            "90 registry rasters carry more than 150,000 positive pixels; their 3-px halos "
            "cover the whole footprint, so the literal 0.70 rule is unsatisfiable for any "
            "non-empty candidate. Owner decision D1 (docs/REVIEW_20261030_NINESITE.md §8)."
        ),
    },
    "raster": {
        "file": CAND["file"],
        "sha256": sha,
        "bytes": CAND["bytes"],
        "zip": CAND["zip"],
        "zip_sha256": CAND["zip_sha256"],
        "n_dots": CAND["n_dots"],
        "grid": CAND["grid"],
        "validator_output": {
            "nan_pixels": CAND["audit"]["n_nan"],
            "infinity_pixels": CAND["audit"]["infinity_pixels"],
            "min": CAND["audit"]["min"],
            "max": CAND["audit"]["max"],
            "bands": CAND["audit"]["bands"],
            "dtype": CAND["audit"]["dtype"],
            "crs": CAND["audit"]["crs"],
            "shape": [CAND["audit"]["height"], CAND["audit"]["width"]],
            "transform_matches_reference": CAND["audit"]["transform"] == CAND["audit"].get("ref_transform", CAND["audit"]["transform"]),
            "mass_outside_footprint": CAND["audit"]["mass_outside_footprint"],
            "problems": CAND["audit"]["problems"],
            "ok": CAND["audit"]["ok"],
            "validation_class": CAND["audit"]["validation_class"],
        },
    },
    "submission": {
        "name": CAND["name"],
        "note": CAND["note"],
        "note_chars": len(CAND["note"]),
    },
    "score_estimate": {
        "evidence_class": "MODEL",
        "ridge_estimate": est["ridge_estimate"],
        "loo_rmse": est["ridge_audit"]["loo_rmse"],
        "leave_group_out_rmse": est["ridge_audit"]["leave_group_out_rmse"],
        "valid_leaderboard_prediction": est["ridge_audit"]["valid_leaderboard_prediction"],
        "structural_stats": EVAL["structural_stats"],
        "best_focus_site_claim": 0.2778,
        "warning": "A MODEL number is never an organizer score.",
    },
    "method_finding": {
        "claim": "Inside the H19-5 lineage the hide-and-recover holdout is anti-correlated with the reported leaderboard score.",
        "spearman_per_dot_yield_vs_claim": round(rho_hc, 4),
        "n": len(sites),
        "cause": ("Hide-and-recover truth is drawn from the mapped catalogue, while the "
                  "top-scoring submissions delete catalogue-adjacent dots; the two moves "
                  "push the holdout and the leaderboard in opposite directions."),
        "consequence": ("A holdout win is necessary but not sufficient; the holdout must "
                        "not be used as a score forecast."),
    },
    "verdict": "negative",
    "submission_eligible": False,
    "blocking_reasons": [
        f"MODEL estimate {est['ridge_estimate']:.4f} (+/-{est['ridge_audit']['leave_group_out_rmse']:.3f}) is below the best focus-site claim 0.2778.",
        f"Fold-proper HOLDOUT-DTI {best['dti']:.4f} does not exceed the repository all-time best 0.184485 (relay_conduit).",
        f"Literal duplicate rule: {uniq['worst_by_representation']['dense_binary_lattice']['n_above_070']} dense registry rasters give overlap {uniq['worst_by_representation']['dense_binary_lattice']['max']:.3f} > 0.70 (unsatisfiable for any non-empty candidate; owner decision D1).",
    ],
    "download_status": "OK TO DOWNLOAD FOR RESEARCH ONLY",
    "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}

dest = ROOT / "docs" / "downloads" / "gx1_run_card_20261031.json"
dest.write_text(json.dumps(card, indent=1))
mirror = ROOT / "evidence" / "gx_run_card_20261031.json"
mirror.write_text(json.dumps(card, indent=1))
print(f"wrote {dest} and {mirror}")
