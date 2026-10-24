#!/usr/bin/env python3
"""Build and validate a unique, all-finite visible-fault-collar candidate.

The holdout path uses only each draw's ``fold['visible']`` catalogue for
catalogue-derived placement. The full catalogue is used only to enforce the
final competition's known-fault exclusion. No DrivenData credentials/network
access or leaderboard claims are used.
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems.gates import run_gates, summarise  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout  # noqa: E402
from vendor.gems57.uniqueness import _near, compare_array_to_registry  # noqa: E402

NAME = "GEMSDOE92-visible-collar-r0-excluded-20261024"
COUNT = 37_654
LOWER_PX = 2.0
UPPER_PX = 3.0
SEED = 20
DRAWS = 1_000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def choose_collar(footprint: np.ndarray, reference_dots: np.ndarray,
                  visible_catalogue: np.ndarray, *, final_catalogue: np.ndarray | None = None) -> np.ndarray:
    """Select a fixed number in the 2–3 px visible-fault collar, outside R0's 3px halo.

    Stable lexicographic order (distance, row, column) is deterministic. The
    holdout caller deliberately omits ``final_catalogue``: no hidden catalogue
    pixels enter its feature/placement rule. The final writer supplies the full
    known catalogue to enforce the competition's zero-known-fault requirement.
    """
    visible = np.asarray(visible_catalogue, bool)
    distance = distance_transform_edt(~visible)
    allowed = np.asarray(footprint, bool) & (distance > LOWER_PX) & (distance <= UPPER_PX)
    if final_catalogue is not None:
        allowed &= ~np.asarray(final_catalogue, bool)
    allowed &= ~_near(np.asarray(reference_dots, bool), 3.0)
    y, x = np.nonzero(allowed)
    if len(y) < COUNT:
        raise ValueError(f"legal collar has {len(y)} cells; need {COUNT}")
    order = np.lexsort((x, y, distance[y, x]))
    out = np.zeros(footprint.shape, dtype=bool)
    out[y[order[:COUNT]], x[order[:COUNT]]] = True
    return out


def write_all_finite(path: Path, prediction: np.ndarray, template_path: Path) -> None:
    with rasterio.open(template_path) as src:
        profile = src.profile.copy()
        foot = np.isfinite(src.read(1))
    if prediction.shape != foot.shape or int(prediction.sum()) != COUNT:
        raise ValueError("candidate shape or dot-count mismatch")
    values = np.where(foot, prediction.astype(np.float32), 0.0).astype(np.float32)
    profile.update(driver="GTiff", count=1, dtype="float32", nodata=None,
                   compress="deflate", predictor=3, zlevel=9,
                   tiled=True, blockxsize=256, blockysize=256)
    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(values, 1)
        dst.set_band_description(1, "predicted_new_fault_probability")


def main() -> int:
    data_dir = ROOT / "data" / "bridge"
    grid = grid_mod.load_grid(data_dir)
    footprint = grid.footprint
    parent_path = ROOT / "data" / "parent_R0_zeros.tif"
    with rasterio.open(parent_path) as src:
        parent = (src.read(1) > 0) & footprint
    if int(parent.sum()) != COUNT:
        raise ValueError("pinned R0 dot count changed")

    # Surface-level uniqueness check occurs BEFORE placement: the prospectivity
    # surface is rank-normalized inverse distance in a 2–3 px collar, with R0's
    # 3 px halo removed. This is a planning surface, not a prediction/score.
    full_distance = distance_transform_edt(~grid.catalogue)
    surface = np.zeros(footprint.shape, dtype=np.float32)
    surface_mask = footprint & (full_distance > LOWER_PX) & (full_distance <= UPPER_PX)
    surface_mask &= ~_near(parent, 3.0)
    surface[surface_mask] = (1.0 / full_distance[surface_mask]).astype(np.float32)
    registry_index = ROOT / "evidence" / "lane_registry_index.json"
    pre_registry = compare_array_to_registry(surface, registry_index, footprint)
    if pre_registry["stop_required"]:
        raise RuntimeError("pre-placement uniqueness scan incomplete or duplicate")

    # Hide/recover: one buffered whole-component draw, shared four spatial folds;
    # visible catalogue only is used for each held-out prediction's corridor.
    folds = []
    for seed in (SEED, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
    terms_by_arm: dict[str, np.ndarray] = {"candidate": None, "R0": None}  # type: ignore[dict-item]
    canary_y, canary_x = [], []
    rng = np.random.default_rng(520810)
    for fold in folds:
        visible = np.asarray(fold["visible"], bool)
        candidate_fold = choose_collar(footprint, parent, visible)
        score, terms = evaluate_holdout.evaluate(candidate_fold.astype(np.float32), fold, footprint)
        terms_by_arm["candidate"] = terms if terms_by_arm["candidate"] is None else terms_by_arm["candidate"] + terms
        r0_score, r0_terms = evaluate_holdout.evaluate(parent.astype(np.float32), fold, footprint)
        terms_by_arm["R0"] = r0_terms if terms_by_arm["R0"] is None else terms_by_arm["R0"] + r0_terms
        pos = np.flatnonzero(np.asarray(fold["truth"], bool) & footprint)
        # Full catalogue is used here only to define evaluation negatives, never as an input to the placement surface.
        neg = np.flatnonzero(np.asarray(fold["region"], bool) & footprint & ~grid.catalogue)
        n = min(len(neg), max(1, 2 * len(pos)))
        if n:
            neg = rng.choice(neg, size=n, replace=False) if len(neg) > n else neg
            canary_y.extend([1] * len(pos) + [0] * n)
            dist = distance_transform_edt(~visible).ravel()
            canary_x.extend(dist[np.r_[pos, neg]].tolist())

    pooled = evaluate_holdout.pooled_summary(
        terms_by_arm, draws=DRAWS, seed=520810, candidate="candidate")
    auc = float(roc_auc_score(np.asarray(canary_y), np.asarray(canary_x)))
    symmetric_auc = max(auc, 1.0 - auc)
    if symmetric_auc > 0.90:
        raise RuntimeError(f"leakage canary stopped: symmetric AUC {symmetric_auc:.6f} > 0.90")

    # Final deployment uses the complete available catalogue, as required for
    # known-fault exclusion. Apply the same surface, then check placement-level
    # uniqueness against every locally indexed registry raster.
    final = choose_collar(footprint, parent, grid.catalogue, final_catalogue=grid.catalogue)
    downloads = ROOT / "docs" / "downloads"
    tif_path = downloads / f"{NAME}-zeros.tif"
    write_all_finite(tif_path, final, data_dir / "sample_submission.tif")
    with rasterio.open(tif_path) as ds:
        values = ds.read(1)
        profile_ok = (ds.count == 1 and ds.dtypes[0] == "float32" and
                      ds.crs == rasterio.crs.CRS.from_epsg(32611) and
                      ds.shape == (3730, 3292) and np.isfinite(values).all() and
                      float(values.min()) >= 0 and float(values.max()) <= 1 and
                      np.all(values[~footprint] == 0))
    if not profile_ok:
        raise RuntimeError("serialized candidate failed independent all-finite/grid/range check")
    final_registry = compare_array_to_registry(values, registry_index, footprint,
                                                file_sha256=sha256(tif_path))
    if not final_registry["unique"]:
        raise RuntimeError("final placement failed local registry uniqueness gate")

    gates = run_gates(str(tif_path), str(data_dir / "sample_submission.tif"),
                      str(data_dir / "existing_faults.tif"), prune_radius=2)
    gates_ok, gate_report = summarise(gates)
    if not gates_ok:
        raise RuntimeError(gate_report)

    zip_path = downloads / f"{NAME}-zeros.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(tif_path, arcname=tif_path.name)

    candidate_score = pooled["scores"]["candidate"]
    r0_score = pooled["scores"]["R0"]
    delta = pooled["paired_differences"]["R0"]
    note = "Visible-fault collar 2-3 px; R0 3px halo excluded; 37,654 dots"
    public_scan_path = ROOT / "evidence" / "public_registry_uniqueness.json"
    public_scan = json.loads(public_scan_path.read_text(encoding="utf-8")) if public_scan_path.is_file() else None
    this_sha = sha256(tif_path)
    public_scan_matches = bool(public_scan and public_scan.get("candidate", {}).get("sha256") == this_sha)
    public_unique = bool(public_scan_matches and public_scan["final_dots"].get("unique_under_literal_rule"))
    card = {
        "schema": "gemsdoe92.run-card.v1",
        "hypothesis": "Blind or unmapped faults may occur in a narrow 200–300 m collar around visible faults, beyond the 3-px halo of the inherited R0 dots.",
        "mechanism": "Place 37,654 dots at the closest legal cells 2<d_visible<=3 px from visible catalogue geometry, excluding all cells within 3 px of R0. Holdout uses visible catalogue only; final export additionally excludes full known catalogue.",
        "named_non_fault_mimic": "Non-tectonic lineaments in drainage/alluvial-fan margins and lithologic contacts may lie close to mapped faults and mimic a fault-proximity signal.",
        "holdout_dti": {
            "evaluator_version": evaluate_holdout.VERSION,
            "withheld_positive_pixels": candidate_score["withheld_positive_pixels"],
            "candidate": candidate_score,
            "R0": r0_score,
            "paired_delta_vs_R0": delta,
            "holdout_design": "buffered whole-component hide/recover, 4 spatial quadrants at seeds 20 and 30 (8 folds), pooled DTI alpha=.2 beta=.8 triangular radius=300m; 1,000 paired 20km-cluster draws, seed 520810",
        },
        "leakage_canary": {"feature": "distance to visible faults (alone)", "auc": auc,
                           "symmetric_auc": symmetric_auc, "threshold": 0.90,
                           "status": "PASS" if symmetric_auc <= .90 else "STOP"},
        "correlation_overlap_vs_registry": {
            "registry_scope": "Local index: 14 rasters; public scan: current default-branch submission TIFFs across 102 public buffedlizard55-lab GEMSDOE-named repositories (1,279 matching-grid raster blobs). Neither scan includes all historical, private, site-hosted, or other-owner files.",
            "public_registry_scan": {"evidence_file": "evidence/public_registry_uniqueness.json", "candidate_hash_matches_scan": public_scan_matches,
                                     "scan_complete_for_declared_scope": bool(public_scan_matches and public_scan["inventory"]["download_failures"] == 0 and public_scan["inventory"]["tree_errors"] == 0 and public_scan["inventory"]["truncated_trees"] == 0),
                                     "preplacement_surface": public_scan["preplacement_surface"] if public_scan_matches else None,
                                     "final_dots": public_scan["final_dots"] if public_scan_matches else None,
                                     "unique_under_literal_rule": public_unique,
                                     "stop_required": bool(not public_unique)}, 
            "preplacement_surface": {"worst_abs_spearman": max(abs(r["spearman_full_footprint"]) for r in pre_registry["rows"] if r.get("spearman_full_footprint") is not None),
                                     "worst_rho_raster": pre_registry["worst_rho_submission"],
                                     "worst_dot_overlap": pre_registry["worst_dot_overlap"],
                                     "worst_overlap_raster": pre_registry["worst_overlap_submission"]},
            "final_dots": {"worst_abs_spearman": max(abs(r["spearman_full_footprint"]) for r in final_registry["rows"] if r.get("spearman_full_footprint") is not None),
                            "worst_rho_raster": final_registry["worst_rho_submission"],
                            "worst_forward_overlap": final_registry["worst_dot_overlap"],
                            "worst_overlap_raster": final_registry["worst_overlap_submission"],
                            "registry_rasters_checked": final_registry["registry_rasters_checked"],
                            "complete_local_scan": final_registry["complete_accessible_scan"],
                            "unique_under_thresholds": final_registry["unique"]},
        },
        "raster_sha256": sha256(tif_path),
        "validator": {"status": "PASS", "no_nan_inside_footprint": bool(np.isfinite(values[footprint]).all()),
                       "all_values_in_0_1": bool(values.min() >= 0 and values.max() <= 1),
                       "zeros_outside_footprint": bool(np.all(values[~footprint] == 0)),
                       "crs": "EPSG:32611", "shape": list(values.shape),
                       "transform": [float(v) for v in tuple(rasterio.open(data_dir / "sample_submission.tif").transform)[:6]],
                       "single_band_float32": True, "gates": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates]},
        "submission_name": "GEMSDOE92-visible-collar-r0-excluded-20261024",
        "submission_note": note,
        "verdict": "promote" if delta["ci95"][0] > 0 and final_registry["unique"] and public_unique and gates_ok else "negative",
        "negative_reason": ("Literal public-registry overlap stop: candidate is within 3 px of positive support in registry rasters; do not spend a weekly slot." if public_scan_matches and not public_unique else ("No hash-matched public-registry audit; fail closed." if not public_scan_matches else None)),
        "limits": ["HOLDOUT-DTI is not a DrivenData score.", "Registry scan covers current public default-branch submission TIFFs in 102 owner repositories, not every historic, private, site-hosted, or other-owner file.", "Competition label truth is unpublished; holdout rewards recovery of mapped catalogue features, not necessarily novel live faults."], 
    }
    card_path = ROOT / "evidence" / "visible_collar_run_card.json"
    card_json = json.dumps(card, indent=2) + "\n"
    card_path.write_text(card_json, encoding="utf-8")
    (downloads / "visible_collar_run_card.json").write_text(card_json, encoding="utf-8")
    if public_scan_path.is_file():
        (downloads / "public_registry_uniqueness.json").write_text(
            public_scan_path.read_text(encoding="utf-8"), encoding="utf-8")
    audit = {
        "schema": "gemsdoe92.download-audit.v1", "overall_pass": bool(gates_ok),
        "format_pass": bool(gates_ok), "submission_eligible": bool(gates_ok and public_unique),
        "sha256_zeros": sha256(tif_path), "candidate": tif_path.name,
        "gates_zeros": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates],
        "local_uniqueness": card["correlation_overlap_vs_registry"]["final_dots"],
        "public_registry_uniqueness": card["correlation_overlap_vs_registry"]["public_registry_scan"],
        "evidence": "Format gates passing means OK TO DOWNLOAD, not OK TO SUBMIT. Public registry check is binding and fails; see evidence/public_registry_uniqueness.json. HOLDOUT-DTI is not an organizer receipt.",
    }
    (downloads / f"{NAME}-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tif": str(tif_path), "zip": str(zip_path), "run_card": str(card_path),
                      "sha256": card["raster_sha256"], "verdict": card["verdict"],
                      "candidate_holdout": candidate_score, "r0_holdout": r0_score,
                      "delta": delta, "canary_symmetric_auc": symmetric_auc,
                      "final_registry": card["correlation_overlap_vs_registry"]["final_dots"],
                      "gate_report": gate_report}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
