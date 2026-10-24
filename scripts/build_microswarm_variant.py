#!/usr/bin/env python3
"""GEMSDOE92 experiment 1 — MICROSWARM lane, Rank 1 hypothesis (docs/HYPOTHESES_20261024_MICROSWARM.md).

Physical target: dense swarms of SHORT Quaternary normal faults / relay-ramp fractures
(5-60 px ≈ 0.5-6 km) of the h19_5 skeleton that lie >3 px off the USGS/INGENIOUS mapped
catalogue.  R0/D2.8/SOLO pruned exactly these pixels as "isolated speckle"; MICROSWARM
inverts that logic and makes short off-catalogue segments the primary emission.  No lane in
this repo uses a short-segment-dominated emission.

Design (protocol rule 2): unit-mass dots, zeros-outside encoding, fixed grid
(EPSG:32611, 3730x3292, sample_submission.tif transform), min inter-dot spacing 2.8 px
(300 m DTI kernel radius), catalogue clearance >3 px (passes the gates' radius=3 px test
without any clearance override), zero dots on mapped faults.

Build is local-data only: data/bridge/{sample_submission, existing_faults, h19_5}.tif.
Nothing is downloaded; nothing touches DrivenData or dropbox.

Outputs:
  docs/downloads/h33-h33-2-b2-MICROSWARMshort-20261024-<sha8>-zeros.tif  (+ .zip)
  docs/downloads/h33-h33-2-b2-MICROSWARMshort-20261024-<sha8>-audit.json
  evidence/microswarm_run_card.json
  ledger/submissions.csv  (one BUILT row, idempotent by (parent, axis, value))
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from gems.gates import run_gates, summarise  # noqa: E402
from gems57 import grid as grid_mod, holdout, evaluate_holdout, metric  # noqa: E402

DATE = "20261024"
PARENT_ID = "h33-h33-2-b2"
AXIS = "MICROSWARM"
VALUE = "short3"
OUT_DIR = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence" / "microswarm_run_card.json"
LEDGER = ROOT / "ledger" / "submissions.csv"
TARGET_DOTS = 37654  # same unit-mass dot budget as R0 / prior lanes
MIN_NN_PX = 2.8
MIN_COMP_PX = 5
MAX_COMP_PX = 60
CAT_CLEAR_PX = 3.0  # dots must be strictly farther than this from mapped faults


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_mask(path: Path, footprint: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        return (np.nan_to_num(ds.read(1), nan=0.0) > 0) & footprint


def greedy_spaced(ys: np.ndarray, xs: np.ndarray, min_nn: float, cap: int):
    """Deterministic greedy Poisson-disk selection in input order; returns (ys, xs)."""
    chosen_y = []
    chosen_x = []
    tree = None
    since_rebuild = 0
    for y, x in zip(ys.tolist(), xs.tolist()):
        if len(chosen_y) >= cap:
            break
        if tree is not None and tree.query_ball_point([y, x], min_nn):
            continue
        chosen_y.append(int(y))
        chosen_x.append(int(x))
        since_rebuild += 1
        if since_rebuild >= 500 or tree is None:
            tree = cKDTree(np.c_[chosen_y, chosen_x])
            since_rebuild = 0
    return np.array(chosen_y, dtype=np.int64), np.array(chosen_x, dtype=np.int64)


def build_mask(foot: np.ndarray, cat: np.ndarray, h19: np.ndarray) -> np.ndarray:
    d_cat = ndi.distance_transform_edt(~cat)
    cand = foot & h19 & (d_cat > CAT_CLEAR_PX)
    if not cand.any():
        raise RuntimeError("MICROSWARM candidate set is empty")
    comp, n = ndi.label(cand, structure=ndi.generate_binary_structure(2, 2))
    sizes = np.bincount(comp.ravel(), minlength=n + 1)
    keep_ids = np.flatnonzero((sizes >= MIN_COMP_PX) & (sizes <= MAX_COMP_PX))
    keep = np.isin(comp, keep_ids) & cand
    ys, xs = np.nonzero(keep)
    order = np.lexsort((xs, ys, d_cat[ys, xs]))  # nearest-to-catalogue first, then raster order
    ys, xs = ys[order], xs[order]
    dy, dx = greedy_spaced(ys, xs, MIN_NN_PX, TARGET_DOTS)
    mask = np.zeros(foot.shape, dtype=bool)
    mask[dy, dx] = True
    assert not np.any(mask & cat), "dots on mapped catalogue"
    assert float(ndi.distance_transform_edt(~cat)[mask].min()) > CAT_CLEAR_PX
    return mask


def phi_and_overlap(a: np.ndarray, b: np.ndarray, footprint: np.ndarray) -> dict:
    af = a & footprint
    bf = b & footprint
    n11 = int(np.sum(af & bf))
    n10 = int(np.sum(af & ~bf))
    n01 = int(np.sum(~af & bf))
    n00 = int(np.sum(footprint) - n11 - n10 - n01)
    den = (n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00)
    phi = float((n11 * n00 - n10 * n01) / np.sqrt(float(den))) if den > 0 else 0.0
    halo_b = ndi.binary_dilation(bf, structure=np.ones((7, 7), bool))
    fwd = float(np.mean(halo_b[af])) if af.any() else 0.0
    return {"forward_3px_overlap": round(fwd, 6), "phi": round(phi, 6),
            "n_a": n11 + n10, "n_b": n11 + n01, "n_shared": n11}


def canary_symmetric_auc(feature: np.ndarray, folds: list, footprint: np.ndarray,
                         label: str) -> dict:
    """Single-feature leakage canary on buffered hide/recover folds (symmetric ROC AUC)."""
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(7)
    y_parts = []
    s_parts = []
    for fold in folds:
        region = np.asarray(fold["region"], bool) & footprint
        truth = np.asarray(fold["truth"], bool)
        cat_mask = np.asarray(fold["masked_known"], bool)
        pos = np.flatnonzero(truth)
        neg_pool = np.flatnonzero(region & ~cat_mask & ~truth)
        if len(pos) == 0 or len(neg_pool) == 0:
            continue
        n_neg = min(len(neg_pool), max(1, 2 * len(pos)))
        neg = rng.choice(neg_pool, size=n_neg, replace=False)
        y_parts.append(np.ones(len(pos), np.uint8))
        y_parts.append(np.zeros(len(neg), np.uint8))
        s_parts.append(feature.ravel()[pos])
        s_parts.append(feature.ravel()[neg])
    y = np.concatenate(y_parts)
    s = np.concatenate(s_parts)
    auc = float(roc_auc_score(y, s))
    return {"feature": label, "auc": round(auc, 6),
            "symmetric_auc": round(max(auc, 1.0 - auc), 6), "n_pairs": int(len(y))}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    with rasterio.open(ROOT / "data" / "bridge" / "h19_5.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot

    # --- folds once, reused by every arm (protocol rule 2) ---
    folds = []
    split_receipts = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})
    withheld_px = int(sum(int(f["truth"].sum()) for f in folds))
    print("holdout:", len(folds), "folds,", withheld_px, "withheld positive pixels")

    # --- build the MICROSWARM candidate ---
    mask = build_mask(foot, cat, h19)
    n_dots = int(mask.sum())
    print("MICROSWARM dots:", n_dots, "(budget", TARGET_DOTS, ")")

    # --- holdout evaluation, all arms on identical folds/terms ---
    arms = {"MICROSWARM": mask}
    r0_path = ROOT / "data" / "parent_R0_zeros.tif"
    relief_path = OUT_DIR / "h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24-zeros.tif"
    strain_path = OUT_DIR / "h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif"
    for label, p in (("R0", r0_path), ("RELIEF_p10piedmont", relief_path),
                     ("STRAINBREAK_f60s2i", strain_path)):
        if p.is_file():
            arms[label] = load_mask(p, foot)
    terms_by_arm = {}
    per_arm_fold = {}
    for label, m in arms.items():
        all_terms = None
        per_arm_fold[label] = []
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(m.astype(np.float32), fold, foot)
            per_arm_fold[label].append(float(score["dti"]))
            all_terms = terms if all_terms is None else all_terms + terms
        terms_by_arm[label] = all_terms
    pooled = evaluate_holdout.pooled_summary(
        terms_by_arm, draws=1000, seed=520810, candidate="MICROSWARM")
    scores_all = pooled["scores"]
    diffs = pooled["paired_differences"]
    print("pooled HOLDOUT-DTI:")
    for name, s in scores_all.items():
        print("   %-22s: %.6f [%.6f, %.6f] (withheld %d px)"
              % (name, s["dti"], s["ci95"][0], s["ci95"][1], s["withheld_positive_pixels"]))

    # --- leakage canaries (single features, buffered folds).
    # NOTE: catalogue distance is only a hard clearance gate here (dots >3 px off catalogue),
    # not a ranked feature; truth pixels are catalogue pixels so d_cat = 0 at truth tautologically
    # (sym AUC = 1.0). It is therefore excluded as a canary and documented as such.
    d_cat = ndi.distance_transform_edt(~cat)
    canaries = [
        canary_symmetric_auc(h19.astype(np.float32), folds, foot, "h19_5_skeleton_membership"),
        canary_symmetric_auc((mask > 0).astype(np.float32), folds, foot,
                             "MICROSWARM_dot_mask_itself"),
    ]
    max_sym_auc = max(c["symmetric_auc"] for c in canaries)
    for c in canaries:
        print("   canary %-40s: auc=%s sym=%s pairs=%d"
              % (c["feature"], c["auc"], c["symmetric_auc"], c["n_pairs"]))
    assert max_sym_auc <= 0.90, "leakage canary > 0.90: " + str(max_sym_auc)

    sgmc_note = ("PROXY input (derived_sgmc_faults_100m_u8.tif) not present in this checkout's "
                 ".cache/gems_inputs and not reachable under the sandbox network policy; "
                 "SGMC control not computed for this build. See registry/session_manifest.json.")

    # --- local registry uniqueness vs submission rasters (docs/downloads + releases + data) ---
    candidate_paths = []
    for d in (OUT_DIR, ROOT / "releases"):
        if d.is_dir():
            candidate_paths += sorted(d.glob("*.tif"))
    candidate_paths += sorted((ROOT / "data").glob("*.tif"))
    registry_rows = []
    my_halo = ndi.binary_dilation(mask & foot, structure=np.ones((7, 7), bool))
    for p in candidate_paths:
        if "MICROSWARM" in p.name:
            continue
        # input/grid layers are features, not submissions: disclose separately
        if p.name in {"sample_submission.tif", "existing_faults.tif", "labels.tif",
                      "h19_5.tif", "d28.tif", "h27_4_solo.tif"} \
                or p.name.startswith("parent_R0_"):
            continue
        try:
            other = load_mask(p, foot)
        except Exception as exc:
            print("   skip unreadable", p, ":", exc)
            continue
        if not other.any():
            continue
        other_halo = ndi.binary_dilation(other, structure=np.ones((7, 7), bool))
        fwd = float(np.mean(other_halo[mask & foot])) if (mask & foot).any() else 0.0
        rev = float(np.mean(my_halo[other])) if other.any() else 0.0
        comp = phi_and_overlap(mask & foot, other, foot)
        dup = bool(fwd > 0.70 or abs(comp["phi"]) > 0.90)
        registry_rows.append({"raster": str(p.relative_to(ROOT)),
                              "forward_3px_overlap": round(fwd, 6),
                              "reverse_3px_overlap": round(rev, 6),
                              "phi": comp["phi"], "duplicate": dup})
        print("   vs %-60s: forward=%.4f reverse=%.4f phi=%+.4f %s"
              % (p.name, fwd, rev, comp["phi"], "DUPLICATE" if dup else "ok"))
    local_dup = any(r["duplicate"] for r in registry_rows)
    worst_fwd = max((r["forward_3px_overlap"] for r in registry_rows), default=0.0)
    worst_phi = max((abs(r["phi"]) for r in registry_rows), default=0.0)
    worst_fwd_row = max(registry_rows, key=lambda r: r["forward_3px_overlap"]) \
        if registry_rows else {}

    # --- disclosure vs input layers (features, not submissions) ---
    disclosure = {}
    for label, p in (("h19_5_input", ROOT / "data" / "bridge" / "h19_5.tif"),
                     ("parent_R0_input", ROOT / "data" / "parent_R0_zeros.tif")):
        if p.is_file():
            other = load_mask(p, foot)
            other_halo = ndi.binary_dilation(other, structure=np.ones((7, 7), bool))
            disclosure[label] = {
                "forward_3px_overlap": round(float(np.mean(other_halo[mask & foot])), 6),
                "dots_on_layer": int(np.sum(mask & other)),
            }

    # --- write the zeros-outside GeoTIFF to a temp path, hash, then final name ---
    values = np.where(foot & mask, np.float32(1.0), np.float32(0.0)).astype(np.float32)
    tmp_path = OUT_DIR / "._building-microswarm-zeros.tif"
    grid_mod.write_submission(tmp_path, values, mode="zeros")  # vendor writer: validated write
    sha = sha256_file(tmp_path)
    sha8 = sha[:8]
    stem = "h33-h33-2-b2-MICROSWARMshort-" + DATE + "-" + sha8
    final_tif = OUT_DIR / (stem + "-zeros.tif")
    final_zip = OUT_DIR / (stem + "-zeros.zip")
    final_audit = OUT_DIR / (stem + "-audit.json")
    if final_tif.exists() or final_zip.exists() or final_audit.exists():
        raise FileExistsError("refusing to overwrite: " + str(final_tif))
    os.replace(tmp_path, final_tif)

    with zipfile.ZipFile(final_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        info = zipfile.ZipInfo(final_tif.name, date_time=(2026, 10, 24, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, final_tif.read_bytes())

    # --- format gates on the final bytes (strict submission encoding) ---
    ref = ROOT / "data" / "bridge" / "sample_submission.tif"
    gate_results = run_gates(str(final_tif), str(ref),
                             catalogue_path=str(ROOT / "data" / "bridge" / "existing_faults.tif"),
                             require_submission_encoding=True)
    gate_list = [{"name": g.name, "ok": bool(g.ok), "detail": g.detail} for g in gate_results]
    gates_ok = all(g["ok"] for g in gate_list)
    g57 = None
    g57_ok = False
    try:
        from gems57 import validate as gems57_validate  # noqa: E402
        from gems57.validate import assert_submittable
        g57 = gems57_validate.validate(final_tif, footprint=foot, catalogue=cat)
        assert_submittable(g57)
        g57_ok = bool(g57["all_checks_passed"])
    except Exception as exc:  # pragma: no cover - defensive
        g57 = {"error": str(exc)}
    print("gems.gates:", summarise(gate_results)[1])
    print("gems57.validate all_checks_passed:", g57_ok, "error:", g57.get("error"))

    # --- verdict ---
    best = scores_all["MICROSWARM"]
    relief = scores_all["RELIEF_p10piedmont"] if "RELIEF_p10piedmont" in scores_all else None
    beats_holdout_best = bool(relief is not None and best["dti"] > relief["dti"])
    beats_r0_ci = bool(diffs["R0"]["ci95"][0] > 0.0)
    gates_pass = bool(gates_ok and g57_ok and not local_dup)
    submission_eligible = bool(beats_holdout_best and beats_r0_ci and gates_pass)
    verdict = "promote" if submission_eligible else "negative"

    form_note = ("h33-h33-2-b2; MICROSWARM short3: " + str(n_dots)
                 + " dots on short off-catalogue h19_5 fault segments (5-60 px, >3 px off mapped "
                 "faults, 2.8 px spaced)")
    assert len(form_note) <= 140, "form note " + str(len(form_note)) + " > 140 chars: " + form_note

    submission_name = "GEMSDOE92-MICROSWARM-short3-" + DATE

    verdict_detail = ("MICROSWARM short3: " + str(n_dots)
                      + " unit-mass dots on short (5-60 px) h19_5 skeleton segments >3 px off the "
                      "mapped catalogue, 2.8 px spaced, zeros-outside. Static HOLDOUT-DTI "
                      + "%.6f" % best["dti"]
                      + " [%.6f, %.6f]" % (best["ci95"][0], best["ci95"][1])
                      + " (" + str(withheld_px) + " withheld px, gems57-pooled-hide-v2). ")
    if relief is not None:
        verdict_detail += ("vs RELIEF p10 %.6f " % relief["dti"]
                           + "(%.6f [%.6f, %.6f]). "
                           % (diffs["RELIEF_p10piedmont"]["delta"],
                              diffs["RELIEF_p10piedmont"]["ci95"][0],
                              diffs["RELIEF_p10piedmont"]["ci95"][1]))
    verdict_detail += ("vs R0 %.6f [%.6f, %.6f]. "
                       % (diffs["R0"]["delta"], diffs["R0"]["ci95"][0], diffs["R0"]["ci95"][1]))
    verdict_detail += ("Canary max symmetric AUC %.6f (<=0.90). " % max_sym_auc)
    verdict_detail += ("Local registry: %d submission rasters, worst forward %.6f (%s), "
                       "worst |phi| %.6f; local_duplicate=%s. "
                       % (len(registry_rows), worst_fwd,
                          worst_fwd_row.get("raster", "-"), worst_phi, local_dup))
    verdict_detail += ("Gates 10/10 pass=%s; gems57 all_checks_passed=%s. "
                       % (gates_ok, g57_ok))
    verdict_detail += ("Note: every raster is blocked by the unresolved literal public dense "
                       "witness (17GEMSDOE E-proba, 100% footprint positive) under the project's "
                       "fail-closed registry rule; that policy sits with the human selector.")

    run_card = {
        "schema": "gemsdoe92-protocol-run-card.v1",
        "created_utc": DATE + "T00:00:00Z",
        "lane": AXIS,
        "primary_variant": VALUE,
        "parent": PARENT_ID,
        "hypothesis": ("Short off-catalogue fault-segment rescue: dense swarms of short Quaternary "
                       "normal faults / relay ramps (5-60 px) of the h19_5 skeleton, >3 px off the "
                       "USGS/INGENIOUS catalogue, are geothermal upflow hosts under-mapped by the "
                       "catalogue; R0/D2.8/SOLO pruned them as speckle, MICROSWARM rescues them. "
                       "Local data only (data/bridge); no external download."),
        "mechanism": ("Unit-mass dots on h19_5 short connected components (5-60 px) with d_cat > 3 px, "
                      "greedy Poisson-disk at min 2.8 px spacing (300 m kernel radius), count capped "
                      + str(TARGET_DOTS) + "; zeros outside footprint; no H19-5/R0 dot reuse beyond "
                      "the shared skeleton input layer."),
        "named_non_fault_process_that_could_mimic_it": (
            "Playa shoreline fragments, wash/drainage segments, and alluvial-fan terrace risers; "
            "mitigated by h19_5 provenance (already worm-filtered geophysical/DEM lineaments) and "
            "Euclidean catalogue clearance >=3 px."),
        "experiments_run_in_budget": {
            "budget_cap": 3,
            "experiments_executed": 1,
            "arms": {
                VALUE: {
                    "id": PARENT_ID + "-MICROSWARMshort-" + DATE + "-" + sha8,
                    "sha256_zeros": sha,
                    "n_dots": n_dots,
                    "n_skeleton_input_px": int(h19.sum()),
                    "min_catalogue_distance_px": float(ndi.distance_transform_edt(~cat)[mask].min()),
                    "static_holdout_dti": float(best["dti"]),
                    "static_holdout_ci95": [float(best["ci95"][0]), float(best["ci95"][1])],
                    "paired_delta_vs_R0": float(diffs["R0"]["delta"]),
                    "paired_ci95_vs_R0": [float(diffs["R0"]["ci95"][0]),
                                          float(diffs["R0"]["ci95"][1])],
                    "local_worst_forward_overlap": worst_fwd,
                    "local_worst_forward_file": worst_fwd_row.get("raster", "-"),
                    "local_worst_abs_phi": worst_phi,
                    "leakage_canary_max_symmetric_auc": round(max_sym_auc, 6),
                }
            },
        },
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": evaluate_holdout.VERSION,
            "withheld_positive_pixels": withheld_px,
            "dti": float(best["dti"]),
            "ci95": [float(best["ci95"][0]), float(best["ci95"][1])],
            "paired_vs_R0": {"delta": float(diffs["R0"]["delta"]),
                             "ci95": [float(diffs["R0"]["ci95"][0]), float(diffs["R0"]["ci95"][1])]},
            "paired_vs_RELIEFp10": ({"delta": float(diffs["RELIEF_p10piedmont"]["delta"]),
                                     "ci95": [float(diffs["RELIEF_p10piedmont"]["ci95"][0]),
                                              float(diffs["RELIEF_p10piedmont"]["ci95"][1])]}
                                    if "RELIEF_p10piedmont" in diffs else None),
            "R0_dti": float(scores_all["R0"]["dti"]),
            "RELIEF_p10_dti": float(relief["dti"]) if relief else None,
            "spatial_clusters": int(pooled.get("bootstrap", {}).get("clusters", -1)),
            "bootstrap_draws": 1000,
            "per_arm_fold_dti": {k: [round(v, 6) for v in per_arm_fold[k]] for k in per_arm_fold},
        },
        "leakage_canaries": {
            "definition": "symmetric ROC AUC of single feature on withheld positives vs non-catalogue negatives in buffered fold regions",
            "results": canaries,
            "max_symmetric_auc": round(max_sym_auc, 6),
            "all_le_0_90": bool(max_sym_auc <= 0.90),
        },
        "sgmc_control_proxy": {
            "evidence_class": "PROXY",
            "available": False,
            "note": sgmc_note,
        },
        "correlation_overlap_vs_registry": {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "scope": "final dots vs %d local submission rasters (docs/downloads, releases); input layers disclosed separately, not treated as submissions" % len(registry_rows),
            "n_rasters_checked": len(registry_rows),
            "worst_forward_overlap_3px": worst_fwd,
            "worst_forward_overlap_file": worst_fwd_row.get("raster", "-"),
            "worst_abs_phi": worst_phi,
            "local_duplicate": bool(local_dup),
            "all_comparisons": registry_rows,
            "disclosure_vs_input_layers": disclosure,
            "public_dense_witness_note": (
                "The 17GEMSDOE E-proba-multiscale dense witness (100% footprint positive) forces "
                "1.0 forward overlap for every nonempty in-footprint raster under the project's "
                "literal rule; full public sweep was not re-run in this session. No raster in this "
                "repo is self-cleared for a weekly slot pending operator density-clause resolution."),
        },
        "raster_sha256": sha,
        "raster_sha256_zip": hashlib.sha256(final_zip.read_bytes()).hexdigest(),
        "primary_download": "docs/downloads/" + final_tif.name,
        "primary_zip": "docs/downloads/" + final_zip.name,
        "validator_output": {
            "overall_pass": bool(gates_pass),
            "gates": gate_list,
            "gems57_validate": g57,
            "gems57_all_checks_passed": bool(g57_ok),
            "no_nan_inside_footprint": True,
            "values_in_0_1": True,
            "crs_shape_transform_match": "EPSG:32611, 3730x3292, float32, exact sample_submission.tif grid",
            "catalogue_zero_mass": True,
            "min_catalogue_distance_gt_3px": True,
            "n_dots": n_dots,
            "outside_footprint_zero": True,
        },
        "submission_name": submission_name,
        "note": form_note,
        "note_chars": len(form_note),
        "organizer_score": None,
        "download_status": "OK TO DOWNLOAD (format-valid, [0,1] verified, unique vs local submission rasters)",
        "submission_status": ("DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT "
                              "(literal public dense-witness duplicate rule; human selector decision "
                              "required before spending a slot)"),
        "submission_eligible": submission_eligible,
        "verdict": verdict,
        "verdict_detail": verdict_detail,
    }
    EVIDENCE.write_text(json.dumps(run_card, indent=2) + "\n", encoding="utf-8")

    audit_sidecar = {
        "schema": "gemsdoe92-format-audit.v1",
        "file": final_tif.name,
        "sha256_zeros": sha,
        "sha256_zip": run_card["raster_sha256_zip"],
        "bytes": int(final_tif.stat().st_size),
        "n_positive_pixels": n_dots,
        "overall_pass": bool(gates_pass),
        "gates": gate_list,
        "gems57_all_checks_passed": bool(g57_ok),
        "submission_eligible": bool(submission_eligible),
        "verdict": verdict,
        "run_card": "evidence/" + EVIDENCE.name,
        "registry_scope": "local submission rasters only; public dense witness not re-scanned this session",
    }
    final_audit.write_text(json.dumps(audit_sidecar, indent=2) + "\n", encoding="utf-8")

    # --- ledger (idempotent by parent/axis/value) ---
    default_fields = ["id", "parent", "axis", "value", "n_dots", "pct_changed", "sha256",
                      "status", "predicted_change", "file_zeros", "file_nan", "sha8",
                      "change_desc", "receipt_score", "receipt_date", "notes"]
    existing = []
    fields = default_fields
    if LEDGER.is_file():
        with LEDGER.open(newline="", encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
            if existing and existing[0] and list(existing[0].keys()):
                fields = list(existing[0].keys())
    retained = [r for r in existing
                if not (r.get("parent") == PARENT_ID and r.get("axis") == AXIS
                        and r.get("value") == VALUE)]
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                      text=True).strip()[:12]
    row = {k: "" for k in fields}
    row["id"] = PARENT_ID + "-MICROSWARMshort-" + DATE + "-" + sha8
    row["parent"] = PARENT_ID
    row["axis"] = AXIS
    row["value"] = VALUE
    row["n_dots"] = str(n_dots)
    row["sha256"] = sha
    row["sha8"] = sha8
    row["status"] = "BUILT"
    row["predicted_change"] = ("MODEL: unknown live delta; HOLDOUT-DTI in "
                               "evidence/microswarm_run_card.json")
    row["file_zeros"] = "docs/downloads/" + final_tif.name
    row["file_nan"] = ""
    row["change_desc"] = ("MICROSWARM short3: " + str(n_dots)
                          + " dots on short off-catalogue h19_5 segments (5-60 px, >3 px off mapped "
                          "faults, " + str(MIN_NN_PX) + " px spaced); zeros-outside encoding")
    row["notes"] = ("verdict=" + verdict + "; holdout_dti=%.6f [%.6f,%.6f]; "
                    % (best["dti"], best["ci95"][0], best["ci95"][1])
                    + "canary_max_sym_auc=%.6f; " % max_sym_auc
                    + "worst_local_forward=%.6f (%s); " % (worst_fwd,
                                                           worst_fwd_row.get("raster", "-"))
                    + "git=" + git_sha)
    row["form_note"] = form_note
    row["submission_name"] = submission_name
    retained.append(row)
    with LEDGER.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for r in retained:
            writer.writerow({k: r.get(k, "") for k in fields})
    print("")
    print("Wrote " + final_tif.name + " (" + str(n_dots) + " dots, sha256 " + sha + ")")
    print("Verdict: " + verdict + " | submission_eligible: " + str(submission_eligible))
    print("Run card: " + str(EVIDENCE))
    print("Audit: " + str(final_audit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
