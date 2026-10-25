#!/usr/bin/env python3
"""Run the pre-registered PHASEWIND holdout experiment; no weekly slot is used.

Reuses the pinned cached feature stack, shared buffered hide-and-recover draw,
pooled DTI evaluator, and the common spaced-emission primitive. It tests each
scale feature and each frozen arm independently for leakage before scoring.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import verify_all_manifests  # noqa: E402
from gems.breakline import spaced_top_mask  # noqa: E402
from gems.phasewind import build_arms  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout  # noqa: E402

INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE = ROOT / ".cache" / "phasewind"
OUT = ROOT / "evidence" / "phasewind_holdout.json"
SEEDS = (20, 30)
# Pre-DTI capacity amendment: shared spacing yields at most 21,291 primary-arm
# candidates in the strict draw-visible domain; 20,000 avoids zero-score fill.
N_DOTS = 20_000
MIN_SPACING_PX = 2.83
PRIMARY_ARM = "phasewind_200_400_800"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def emit(surface: np.ndarray, allowed: np.ndarray, arm: str) -> np.ndarray:
    pool = np.asarray(allowed, bool) & (np.asarray(surface, np.float32) > 0.0)
    available = int(pool.sum())
    if available < N_DOTS:
        raise RuntimeError(
            f"{arm}: only {available} positive phase-winding candidates for "
            f"the pre-registered {N_DOTS}-dot budget; no zero-score fallback permitted"
        )
    dots = spaced_top_mask(
        surface, pool, N_DOTS, min_dist_px=MIN_SPACING_PX, cand_cap=900_000
    )
    if int(dots.sum()) != N_DOTS:
        raise RuntimeError(f"{arm}: spaced emitter returned {int(dots.sum())} dots, expected {N_DOTS}")
    return dots


def symmetric_auc(values: np.ndarray, positive: np.ndarray, negative: np.ndarray) -> dict:
    x_pos = np.asarray(values, np.float32)[positive]
    x_neg = np.asarray(values, np.float32)[negative]
    if not x_pos.size or not x_neg.size:
        raise RuntimeError("leakage canary requires both withheld positives and far negatives")
    labels = np.concatenate([np.ones(x_pos.size, np.uint8), np.zeros(x_neg.size, np.uint8)])
    x = np.concatenate([x_pos, x_neg])
    auc = float(roc_auc_score(labels, x))
    sym = max(auc, 1.0 - auc)
    return dict(auc=auc, symmetric_auc=sym, positive_samples=int(x_pos.size), negative_samples=int(x_neg.size),
                pass_le_0p90=bool(sym <= 0.90))


def main() -> int:
    started = time.time()
    CACHE.mkdir(parents=True, exist_ok=True)
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, catalogue = grid.footprint, grid.catalogue

    draws = {seed: holdout.buffered_component_draw(grid, seed=seed)[0] for seed in SEEDS}
    split_receipts = {str(seed): [fold["receipt"] for fold in draws[seed]] for seed in SEEDS}
    withheld_positive_pixels = sum(
        fold["receipt"]["withheld_positive_pixels"]
        for seed in SEEDS for fold in draws[seed]
    )

    log("loading Band 2 RTP from the verified cached training feature stack")
    with rasterio.open(paths["training_features"]) as ds:
        if ds.count != 19 or ds.shape != foot.shape or ds.crs.to_epsg() != 32611:
            raise RuntimeError("training feature stack count/grid/CRS mismatch")
        rtp = ds.read(2, masked=True).filled(np.nan).astype(np.float32)
    valid = foot & np.isfinite(rtp) & (rtp > -1.0e30)

    cache_path = CACHE / "phasewind_features.npz"
    if cache_path.is_file():
        z = np.load(cache_path)
        scales = {}
        for sigma in (2.0, 4.0, 8.0):
            key = f"s{int(sigma)}"
            scales[sigma] = dict(
                charge=z[f"{key}_charge"],
                charge_confidence=z[f"{key}_charge_confidence"],
                amplitude_rank=z[f"{key}_amplitude_rank"],
                feature=z[f"{key}_feature"],
                valid=z[f"{key}_valid"].astype(bool),
                sigma_px=sigma,
            )
        arms = {name: z[name] for name in (
            "phasewind_200_400", "phasewind_400_800", "phasewind_200_400_800"
        )}
    else:
        log("computing three scale-space phase-winding features (2/4/8 px)")
        result = build_arms(rtp, valid)
        scales, arms = result["scales"], result["arms"]
        payload = {}
        for sigma, data in scales.items():
            key = f"s{int(sigma)}"
            for name in ("charge", "charge_confidence", "amplitude_rank", "feature", "valid"):
                payload[f"{key}_{name}"] = data[name]
        payload.update(arms)
        np.savez_compressed(cache_path, **payload)
        del result, payload
    del rtp

    common_valid = valid.copy()
    for data in scales.values():
        common_valid &= np.asarray(data["valid"], bool)
    if not common_valid.any():
        raise RuntimeError("PHASEWIND has no common valid support")

    # Canary labels use only the shared held-out draws; negatives are far from
    # the faults visible to both seed-20 and seed-30 models. No catalogue value
    # enters the PHASEWIND features themselves.
    hidden_union = np.zeros(foot.shape, bool)
    visible_distance = []
    for seed in SEEDS:
        hidden_union |= np.asarray(draws[seed][0]["hidden_all"], bool)
        visible = np.asarray(draws[seed][0]["visible"], bool)
        visible_distance.append(distance_transform_edt(~visible))
    far_negative = (
        foot & common_valid & ~hidden_union
        & (visible_distance[0] > 5.0) & (visible_distance[1] > 5.0)
    )
    positive = hidden_union & common_valid
    neg_indices = np.flatnonzero(far_negative)
    rng = np.random.default_rng(20261025)
    if neg_indices.size > 200_000:
        neg_indices = rng.choice(neg_indices, size=200_000, replace=False)
    negative_sample = np.zeros(foot.shape, bool)
    negative_sample.ravel()[neg_indices] = True

    canary_rows = {}
    for sigma, data in scales.items():
        canary_rows[f"scale_{int(sigma)}px"] = symmetric_auc(
            np.asarray(data["feature"], np.float32), positive, negative_sample
        )
    for name, surface in arms.items():
        canary_rows[name] = symmetric_auc(surface, positive, negative_sample)
    max_canary = max(row["symmetric_auc"] for row in canary_rows.values())
    all_canaries_pass = all(row["pass_le_0p90"] for row in canary_rows.values())
    canary_receipt = dict(
        evidence_class="HOLDOUT-CANARY",
        evaluator_version=evaluate_holdout.VERSION,
        seed_union=list(SEEDS),
        positive_pixels=int(positive.sum()),
        sampled_far_negatives=int(negative_sample.sum()),
        threshold_symmetric_auc=0.90,
        features=canary_rows,
        max_symmetric_auc=max_canary,
        all_pass=all_canaries_pass,
    )
    (CACHE / "phasewind_canaries.json").write_text(json.dumps(canary_receipt, indent=2) + "\n")
    log(f"single-feature canaries: max symmetric AUC={max_canary:.4f}; pass={all_canaries_pass}")
    if not all_canaries_pass:
        OUT.write_text(json.dumps({
            "schema": "gemsdoe92-phasewind-holdout.v1",
            "lane": "PHASEWIND",
            "status": "stopped_before_DTI: feature canary > 0.90",
            "leakage_canaries": canary_receipt,
            "split_receipts": split_receipts,
            "withheld_positive_pixels": withheld_positive_pixels,
            "experiments_used": 0,
            "weekly_slots_used": 0,
            "verdict": "negative",
        }, indent=2) + "\n")
        return 0

    # Use exactly the current repository best's strict fold-visible clearance.
    # Only the pre-registered primary receives a DTI evaluation. The two
    # ablations were not feasible at the original fixed 37,654-dot budget and
    # are not re-tuned after the canary.
    surfaces = {PRIMARY_ARM: np.asarray(arms[PRIMARY_ARM], np.float32)}
    terms_by_arm = {name: None for name in surfaces}
    fold_scores = {name: [] for name in surfaces}
    candidate_dots = {}
    for seed in SEEDS:
        visible = np.asarray(draws[seed][0]["visible"], bool)
        d_visible = distance_transform_edt(~visible)
        allowed = foot & common_valid & (d_visible > 2.0) & ~visible
        seed_masks = {}
        for name, surface in surfaces.items():
            dots = emit(surface, allowed, name)
            dots[visible] = False
            seed_masks[name] = dots
            if seed == SEEDS[-1]:
                candidate_dots[name] = dots.copy()
            for fold in draws[seed]:
                prediction = dots.astype(np.float32)
                score, terms = evaluate_holdout.evaluate(prediction, fold, foot)
                terms_by_arm[name] = terms if terms_by_arm[name] is None else terms_by_arm[name] + terms
                fold_scores[name].append(float(score["dti"]))
        del seed_masks

    summary = evaluate_holdout.pooled_summary(
        terms_by_arm, draws=1000, seed=820251, candidate=PRIMARY_ARM
    )
    best_arm = max(summary["scores"], key=lambda name: summary["scores"][name]["dti"])
    # Retain seed 30's fold-visible emission only as a reproducibility
    # diagnostic. It is not a deployment preview and is never packaged.
    ref = json.loads((ROOT / "evidence" / "coulomb_loqo_run_card.json").read_text())
    best_ref = dict(
        lane="COULOMBLOQO standalone",
        evidence_class="HOLDOUT-DTI",
        evaluator_version=ref["holdout_dti"]["evaluator_version"],
        withheld_positive_pixels=ref["holdout_dti"]["withheld_positive_pixels"],
        dti=ref["holdout_dti"]["strict_draw_blind_dvis2_dti"],
        ci95=ref["holdout_dti"]["strict_draw_blind_dvis2_ci95"],
        source="evidence/coulomb_loqo_run_card.json; same evaluator and strict d_visible > 2 px instrument",
    )
    beats_holdout_best = bool(summary["scores"][best_arm]["dti"] > best_ref["dti"])

    # Store only re-creatable holdout diagnostics in ignored .cache. This
    # experiment script never writes or publishes a submission GeoTIFF.
    for name, surface in surfaces.items():
        np.save(CACHE / f"{name}_surface.npy", surface)
        np.save(CACHE / f"{name}_seed30_holdout_emission.npy", candidate_dots[name].astype(np.uint8))
    result = {
        "schema": "gemsdoe92-phasewind-holdout.v1",
        "lane": "PHASEWIND",
        "status": "holdout_complete",
        "date_utc": time.strftime("%Y-%m-%d", time.gmtime()),
        "hypothesis_file": "docs/HYPOTHESES_20261025_PHASEWIND.md",
        "implementation_sha256": sha256_file(ROOT / "gems" / "phasewind.py"),
        "input_manifest": "registry/session_manifest.json (all 12 staged pins SHA-256/byte-verified)",
        "feature_stack": {
            "path": str(paths["training_features"].relative_to(ROOT)),
            "sha256": sha256_file(paths["training_features"]),
            "band": 2,
            "band_name": "rtp",
            "shape": list(foot.shape),
            "crs": str(grid.crs),
            "valid_pixels": int(common_valid.sum()),
        },
        "split": {
            "method": "gems57.holdout.buffered_component_draw; buffered whole 8-connected fault components, 4 spatial quadrants per seed",
            "seeds": list(SEEDS),
            "folds": 8,
            "withheld_positive_pixels": withheld_positive_pixels,
            "receipts": split_receipts,
        },
        "leakage_canaries": canary_receipt,
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": evaluate_holdout.VERSION,
            "withheld_positive_pixels": int(summary["scores"][best_arm]["withheld_positive_pixels"]),
            "metric": {"alpha": 0.2, "beta": 0.8, "triangular_kernel_radius_m": 300},
            "strict_instrument": "seed 20+30 buffered whole-component folds; fold-visible d_visible > 2 px; visible fault pixels masked pixel-exactly",
            "scores": summary["scores"],
            "paired_differences_between_arms": summary["paired_differences"],
            "spatial_bootstrap": summary["bootstrap"],
            "per_fold_dti": fold_scores,
            "current_repository_best": best_ref,
            "best_arm": best_arm,
            "beats_repository_best_point": beats_holdout_best,
        },
        "holdout_evaluation_emissions": {
            "description": "seed-specific masks were used only to evaluate HOLDOUT-DTI; no full-domain deployment dots or submission TIFF were produced",
            "production_dot_placement": "suppressed after literal full-footprint registry witness; do not infer final-dot uniqueness",
            "arms": {name: {
                "dots_per_seed": N_DOTS,
                "positive_pool_seed30": int(((surface > 0) & common_valid).sum()),
                "seed30_holdout_emission_sha256_array": hashlib.sha256(np.ascontiguousarray(candidate_dots[name]).tobytes()).hexdigest(),
            } for name, surface in surfaces.items()},
        },
        "experiments_used": 1,
        "experiment_budget_note": "one primary arm scored; two pre-registered ablations not scored because the shared spacing floor could not realize their original 37,654-dot budget",
        "weekly_slots_used": 0,
        "verdict_before_registry": "negative" if not beats_holdout_best else "selector_review_only",
        "holdout_best_reference_is_not_organizer_score": True,
        "elapsed_seconds": round(time.time() - started, 2),
    }
    OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    log(f"HOLDOUT-DTI primary {best_arm}: {summary['scores'][best_arm]['dti']:.6f} "
        f"{summary['scores'][best_arm]['ci95']} vs best {best_ref['dti']:.6f}; beats={beats_holdout_best}")
    log(f"saved {OUT.relative_to(ROOT)}; experiments={result['experiments_used']}/3; slots=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
