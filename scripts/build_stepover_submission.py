#!/usr/bin/env python3
"""Build the STEPOVER submission: visible-tract step-over / relay-ramp dots.

Lane (single method paragraph, parallel-run protocol §1):
  Place unit-mass dots ONLY in the step-over/relay zone of visible mapped
  traces -- pixels 3-10 px off the catalogue (zero catalogue mass, d_cat > 3)
  and within the strike-continuation direction of a visible trace tip --
  ranked by a visible-geometry favourability field, placed greedily with 1 px
  minimum spacing, count chosen by the hide-and-recover holdout.

Blind geothermal strands localize at 3-D step-overs between mapped traces,
which are under-represented in the USGS/INGENIOUS catalogue; held-out truth
sits just beyond the visible buffer (nearest_visible_to_truth = 3.16 px).

Everything is local: catalogue + footprint from data/bridge/ (pinned mirrors),
no labels, no leaderboard, no drivendata.org / dropbox.com contact.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems57 import grid as gems_grid, holdout, metric, evaluate_holdout
from gems57.network import local_strike
from gems import gates

PARENT_ID = "h33-h33-2-b2"
DATE = "20261024"
OUT_DIR = ROOT / "releases"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence"
RUN_CARD = ROOT / "evidence" / "run_card.json"

# --- Holdout design (protocol rule 2) ---------------------------------------
HIDE_FRAC = 0.20
BUFFER_PX = 3
BOUNDARY_PX = 12
SEED = 20
DTI_R = 3.0  # 300 m at 100 m px, triangular kernel

# --- Placement --------------------------------------------------------------
TIP_DILATE_PX = 10      # step-over zone reaches 10 px from a visible tip
MIN_TIP_DIST_PX = 3.0   # d_cat > 3 px already enforced by allowed domain
MIN_NN_PX = 1.0         # no two dots on the same or adjacent pixel
DOSES = (5000, 10000, 15000)  # holdout sweep; winner submitted


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def auc_score(feature: np.ndarray, pos_mask: np.ndarray, neg_mask: np.ndarray) -> float:
    """Rank-based (Mann-Whitney) AUC; negatives subsampled for memory."""
    p = feature[pos_mask].ravel().astype(np.float64)
    n = feature[neg_mask].ravel().astype(np.float64)
    if n.size > 200_000:
        rng = np.random.default_rng(0)
        n = rng.choice(n, 200_000, replace=False)
    allv = np.r_[p, n]
    order = np.argsort(allv, kind="stable")
    ranks = np.empty(len(allv), dtype=np.float64)
    ranks[order] = np.arange(1, len(allv) + 1)
    uniq, inv, counts = np.unique(allv, return_inverse=True, return_counts=True)
    ranks = (np.bincount(inv, weights=ranks) / counts)[inv]
    return float((ranks[: len(p)].sum() - len(p) * (len(p) + 1) / 2) / (len(p) * len(n)))


def main() -> int:
    # 0. Pinned-input verification
    from gems.manifest import verify as verify_manifest
    rep = verify_manifest(ROOT / "registry" / "data_manifest.json", ROOT)
    if not rep["ok"]:
        print("MANIFEST VERIFICATION FAILED:")
        for p in rep["problems"]:
            print("  ", p)
        return 2
    print(f"Manifest pins verified: {rep['n']} files OK")

    # 1. Grid: footprint + catalogue
    g = gems_grid.load_grid()
    print(f"Grid {g.width}x{g.height} EPSG:32611 footprint={int(g.footprint.sum()):,} "
          f"catalogue={int(g.catalogue.sum()):,}")

    # 2. Holdout: label-blind quadrants, whole segments withheld, buffer
    folds, quad = holdout.buffered_component_draw(
        g, hide_frac=HIDE_FRAC, buffer_px=BUFFER_PX, boundary_px=BOUNDARY_PX, seed=SEED
    )
    hidden_all = np.zeros_like(g.catalogue, dtype=bool)
    for f in folds:
        hidden_all |= f["hidden_all"]
    n_withheld = int(hidden_all.sum())
    print(f"Holdout: {len(folds)} folds, {n_withheld:,} withheld positives")
    for f in folds:
        print(f"  fold {f['name']}: truth={int(f['truth'].sum())}, held_comps={f['receipt']['held_components']}")

    # 3. Visible-only features
    visible = g.catalogue & ~hidden_all
    print(f"Visible catalogue pixels: {int(visible.sum()):,}")

    # tips: trace pixels with exactly one 8-connected neighbour
    nb = ndi.convolve(visible.astype(np.int16), np.ones((3, 3), np.int16), mode="constant") - visible.astype(np.int16)
    tips = visible & (nb == 1)
    n_tips = int(tips.sum())
    print(f"Visible trace tips: {n_tips:,}")

    # tip strikes from the structure tensor of the visible trace (visible-only)
    strike, coh = local_strike(visible, smooth_px=3.0)
    tip_ys, tip_xs = np.nonzero(tips)
    tip_strike = strike[tip_ys, tip_xs]
    finite_strike = np.isfinite(tip_strike)
    print(f"Tips with defined strike: {int(finite_strike.sum())}/{n_tips:,}")

    # catalogue distance and allowed domain (zero catalogue mass, d_cat > 3 px)
    d_cat = ndi.distance_transform_edt(~g.catalogue)
    allowed = g.footprint & (d_cat > 3.0)
    print(f"Allowed domain (footprint & d_cat > 3 px): {int(allowed.sum()):,}")

    # step-over zone: 3-10 px from a visible tip (tips are catalogue pixels so
    # d_tip > 3 px is automatic within the allowed domain)
    tip_tree = cKDTree(np.c_[tip_ys[finite_strike], tip_xs[finite_strike]])
    step_zone = ndi.binary_dilation(tips, iterations=TIP_DILATE_PX) & allowed
    cand_ys, cand_xs = np.nonzero(step_zone)
    print(f"Step-over candidate pool (d_cat>3, within {TIP_DILATE_PX} px of a tip): {len(cand_ys):,}")

    # favourability: alignment of tip->pixel with tip strike, decaying with tip distance
    d_tip, nearest = tip_tree.query(np.c_[cand_ys, cand_xs], k=1)
    nearest = np.asarray(nearest)
    d_tip = np.asarray(d_tip, dtype=np.float64)
    strike_at = tip_strike[nearest]
    dr = cand_ys - tip_ys[nearest]
    dc = cand_xs - tip_xs[nearest]
    az = np.degrees(np.arctan2(dc, -dr)) % 180.0  # clockwise from north
    rel = np.abs(az - strike_at) % 180.0
    rel = np.where(rel > 90.0, 180.0 - rel, rel)
    alignment = np.cos(np.radians(rel)) ** 2
    s = alignment * np.exp(-(d_tip - 3.0) / 3.0)
    s[~np.isfinite(strike_at)] = 0.0

    s_field = np.zeros((g.height, g.width), dtype=np.float64)
    s_field[cand_ys, cand_xs] = s
    s_field[~g.footprint] = 0.0
    s_max = float(s.max()) if s.size else 0.0
    s_norm = s_field / s_max if s_max > 0 else s_field
    print(f"Favourability: max={s_max:.4f}, candidates with s>0: {int((s > 0).sum()):,}")

    # 4. Leakage canary: single-feature AUC of s vs held truth (< 0.90 required)
    pos = hidden_all & g.footprint
    neg = g.footprint & ~pos
    auc_s = auc_score(s_norm, pos, neg)
    print(f"Leakage canary: AUC(favourability s vs held truth) = {auc_s:.4f} (limit 0.90)")
    if auc_s > 0.90:
        print("CANARY FAILED (> 0.90): feature leaks held truth; stopping per protocol.")
        return 3

    # 5. Holdout sweep over dot counts (pooled DTI, no CI during sweep)
    def pooled_terms(emitted: np.ndarray):
        total = None
        for f in folds:
            _, terms = evaluate_holdout.evaluate(emitted.astype(np.float64), f, valid=g.footprint)
            total = terms if total is None else total + terms
        return total

    terms_r0 = None
    with __import__("rasterio").open(ROOT / "data" / "parent_R0_nan.tif") as ds:
        r0 = (ds.read(1) > 0.5)
    terms_r0 = pooled_terms(r0)
    ps_r0 = evaluate_holdout.pooled_summary(
        {"R0": terms_r0}, draws=300, seed=7, candidate="R0"
    )
    dti_r0 = ps_r0["scores"]["R0"]["dti"]
    ci_r0 = ps_r0["scores"]["R0"]["ci95"]
    print(f"Baseline R0 POOLED HOLDOUT-DTI={dti_r0:.5f} CI95=[{ci_r0[0]:.5f},{ci_r0[1]:.5f}] "
          f"withheld={ps_r0['scores']['R0']['withheld_positive_pixels']}")

    results = []
    for n_add in DOSES:
        # greedy favourability placement with MIN_NN_PX spacing, deterministic order
        order = np.lexsort((cand_xs, cand_ys, -s))  # best favourability first, tie -> raster order
        placed_y = []; placed_x = []
        blocked = np.zeros((g.height, g.width), dtype=bool)
        for idx in order:
            if len(placed_y) >= n_add:
                break
            y, x = int(cand_ys[idx]), int(cand_xs[idx])
            if blocked[y, x]:
                continue
            placed_y.append(y); placed_x.append(x)
            blocked[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = True
        emitted = np.zeros((g.height, g.width), dtype=bool)
        emitted[np.array(placed_y), np.array(placed_x)] = True
        terms = pooled_terms(emitted)
        pooled = float(terms[0].sum() / (terms[0].sum() + metric.ALPHA * terms[1].sum()
                                         + metric.BETA * terms[2].sum() + metric.EPS))
        print(f"  N={n_add:,}: dots={int(emitted.sum())} pooled DTI={pooled:.5f}")
        results.append((n_add, emitted, terms, pooled))

    results.sort(key=lambda r: -r[3])
    n_best, emitted_best, terms_best, dti_best = results[0]
    print(f"Selected N={n_best:,} (pooled DTI={dti_best:.5f} vs R0 {dti_r0:.5f})")

    # 6. Final holdout evaluation with 95% CI (HOLDOUT-DTI, evaluator gems57-pooled-hide-v2)
    ps = evaluate_holdout.pooled_summary(
        {"STEPOVER": terms_best, "R0": terms_r0},
        draws=300, seed=7, candidate="STEPOVER",
    )
    s_summary = ps["scores"]["STEPOVER"]
    r0_summary = ps["scores"]["R0"]
    print(f"STEPOVER POOLED HOLDOUT-DTI={s_summary['dti']:.5f} CI95=[{s_summary['ci95'][0]:.5f},{s_summary['ci95'][1]:.5f}] "
          f"withheld={s_summary['withheld_positive_pixels']}")
    print(f"STEPOVER - R0 delta={ps['paired_differences']['R0']['delta']:+.5f} "
          f"CI95=[{ps['paired_differences']['R0']['ci95'][0]:+.5f},{ps['paired_differences']['R0']['ci95'][1]:+.5f}]")

    # canary on the final dot field vs held truth
    auc_dot = auc_score(emitted_best.astype(np.float64), pos, neg)
    print(f"Leakage canary: AUC(final dots vs held truth) = {auc_dot:.4f} (limit 0.90)")

    # 7. Uniqueness / LANE check vs locally accessible registry rasters
    from gems57.uniqueness import compare_array_to_registry

    registry_files = [ROOT / "data" / "parent_R0_nan.tif", ROOT / "data" / "parent_R0_zeros.tif"] + \
        sorted(OUT_DIR.glob("*.tif"))
    records = []
    for p in registry_files:
        records.append({
            "repo_first": "GEMSDOE92 (local)",
            "sources": [p.name],
            "cache_file": str(p.relative_to(ROOT)),
            "sha256": sha256_file(p),
        })
    registry_index = {
        "schema": "gemsdoe92-lane-registry.v1",
        "complete_accessible_scan": True,
        "n_rasters": len(records),
        "scope": "Locally accessible rasters only (this repo: parent R0 + releases). "
                 "Not organizer-complete; external/private/unlinked rasters may be absent.",
        "rasters": records,
    }
    registry_path = EVIDENCE / "lane_registry_index.json"
    registry_path.write_text(json.dumps(registry_index, indent=2), encoding="utf-8")

    from rasterio import open as ras_open
    with ras_open(ROOT / "data" / "bridge" / "sample_submission.tif") as ref:
        expected_grid = (ref.shape, ref.crs, ref.transform)

    def lane_report(arr: np.ndarray) -> dict:
        return compare_array_to_registry(
            arr, registry_index, g.footprint,
            file_sha256=None, expected_grid=expected_grid,
        )

    surface_report = lane_report(np.clip(s_norm, 0, 1).astype(np.float32))
    dots_report = lane_report(emitted_best.astype(np.float32))
    print("LANE surface: worst rho=", surface_report["worst_spearman_full_footprint"],
          "duplicate_count=", surface_report["duplicate_count"], "unique=", surface_report["unique"])
    print("LANE dots:   worst rho=", dots_report["worst_spearman_full_footprint"],
          "worst overlap=", dots_report["worst_dot_overlap"],
          "duplicate_count=", dots_report["duplicate_count"], "unique=", dots_report["unique"])
    lane_ok = surface_report["unique"] and dots_report["unique"] and dots_report["complete_accessible_scan"]
    print(f"LANE verdict: {'PASS (unique)' if lane_ok else 'FAIL / duplicate logged'}")

    # 8. Write submission (fail-closed writer) + format gates
    from gems57.submission_writer import write_submission
    from gems57.grid import write_geotiff

    arr = emitted_best.astype(np.float32)
    assert np.isfinite(arr).all() and (arr >= 0).all() and (arr <= 1).all()
    assert not ((arr > 0) & ~g.footprint).any(), "mass outside footprint"
    assert not ((arr > 0) & g.catalogue).any(), "mass on catalogue"

    # submission name + note (<= 140 chars each)
    note = (f"{PARENT_ID}; STEPOVER step-over dots 3-10px off catalogue at visible trace tips; "
            f"HOLDOUT-DTI {s_summary['dti']:.4f} [{s_summary['ci95'][0]:.4f},{s_summary['ci95'][1]:.4f}]")
    assert len(note) <= 140, f"note too long: {len(note)}"
    stem = f"{PARENT_ID}-STEPOVER-tip{TIP_DILATE_PX}px-N{n_best}-{DATE}"
    # content-addressed sha8 after deterministic write to a temp path
    tmp_path = OUT_DIR / f"._{stem}.tif"
    info = write_geotiff(tmp_path, arr, nodata=None)
    sha8 = sha256_file(tmp_path)[:8]
    tmp_path.unlink()
    name = f"{stem}-{sha8}"
    assert len(name) <= 140, f"name too long: {len(name)}"
    tif_path = OUT_DIR / f"{name}.tif"

    receipt = write_submission(
        tif_path, arr,
        sample=ROOT / "data" / "bridge" / "sample_submission.tif",
        footprint=g.footprint,
        name=name,
        note=note,
        catalogue=g.catalogue,
        metadata={
            "axis": "STEPOVER",
            "parent": PARENT_ID,
            "method": "visible-tract step-over/relay dots; d_cat>3 px; 1 px spacing; unit mass",
            "n_dots": int(emitted_best.sum()),
            "holdout_dti": s_summary["dti"],
            "holdout_ci95": s_summary["ci95"],
            "holdout_withheld_positives": s_summary["withheld_positive_pixels"],
            "evaluator_version": "gems57-pooled-hide-v2",
            "alpha": metric.ALPHA, "beta": metric.BETA, "triangular_radius_m": metric.R_M,
            "leakage_canary_auc_s": auc_s,
            "leakage_canary_auc_dots": auc_dot,
            "lane_unique": bool(lane_ok),
            "lane_registry": str(registry_path.relative_to(ROOT)),
            "receipt_class": "locally validated; organizer acceptance pending",
        },
    )
    print(f"Wrote submission: {tif_path} ({receipt['bytes']} B, sha256={receipt['sha256'][:16]}...)")
    print(f"  receipt: {tif_path.with_suffix('.json')}")
    print(f"  zip:     {tif_path.with_suffix('.zip')}")

    # 9. MUST-pass format gates (independent re-check from disk)
    gate_results = gates.run_gates(
        str(tif_path),
        str(ROOT / "data" / "bridge" / "sample_submission.tif"),
        catalogue_path=str(ROOT / "data" / "bridge" / "existing_faults.tif"),
    )
    ok, report = gates.summarise(gate_results)
    print(report)
    if not ok:
        return 4

    # 10. Evidence document
    ev = {
        "schema": "gemsdoe92.stepover.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "branch": "arena/aebe414f-gemsdoe92",
        "hypothesis": "STEPOVER: blind geothermal strands localize at visible-tract step-overs "
                      "(3-10 px off mapped traces, strike continuation of trace tips), under-mapped "
                      "in the USGS/INGENIOUS catalogue.",
        "mechanism": "dots placed by visible-geometry favourability s(x) = strike-alignment x "
                     "exp(-(d_tip-3)/3), unit mass, 1 px spacing, count N by holdout-DTI sweep.",
        "non_fault_mimic": "erosional notch / alluvial fan head and pluvial-lake shoreline "
                           "terminations can create tip-like trace ends without displacement.",
        "holdout": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": "gems57-pooled-hide-v2",
            "alpha": metric.ALPHA,
            "beta": metric.BETA,
            "triangular_radius_m": metric.R_M,
            "withheld_positive_pixels": s_summary["withheld_positive_pixels"],
            "n_blocks": int(terms_best.shape[0]),
            "dti": s_summary["dti"],
            "ci95": s_summary["ci95"],
            "pooled_tp": float(terms_best[0].sum()),
            "pooled_fp": float(terms_best[1].sum()),
            "pooled_fn": float(terms_best[2].sum()),
            "delta_vs_R0_dti": ps["paired_differences"]["R0"]["delta"],
            "delta_vs_R0_ci95": ps["paired_differences"]["R0"]["ci95"],
        },
        "baseline_R0": {
            "dti": r0_summary["dti"],
            "ci95": r0_summary["ci95"],
            "withheld_positive_pixels": r0_summary["withheld_positive_pixels"],
            "evidence_label": "HOLDOUT-DTI proxy baseline, not a score",
        },
        "leakage_canary": {
            "auc_favourability_vs_held_truth": auc_s,
            "auc_final_dots_vs_held_truth": auc_dot,
            "limit": 0.90,
            "status": "PASS" if max(auc_s, auc_dot) <= 0.90 else "STOP_AND_INVESTIGATE",
        },
        "lane": {
            "registry_index": str(registry_path.relative_to(ROOT)),
            "registry_rasters_checked": surface_report["registry_rasters_checked"],
            "complete_accessible_scan": surface_report["complete_accessible_scan"],
            "surface_worst_rho": surface_report["worst_spearman_full_footprint"],
            "dots_worst_rho": dots_report["worst_spearman_full_footprint"],
            "dots_worst_forward_overlap": dots_report["worst_dot_overlap"],
            "duplicate_count": dots_report["duplicate_count"],
            "unique": bool(lane_ok),
            "rule": "rank correlation <= 0.90 and <= 70% of dots within 3 px of every registry raster, "
                    "surface before placement and dots on the final raster.",
        },
        "raster": {
            "file": str(tif_path.relative_to(ROOT)),
            "name": name,
            "note": note,
            "note_chars": len(note),
            "sha256": receipt["sha256"],
            "bytes": receipt["bytes"],
            "zip": receipt["zip_file"],
            "receipt": str(tif_path.with_suffix(".json").relative_to(ROOT)),
        },
        "validation": {
            "gates_pass": bool(ok),
            "validator_receipt": receipt,
        },
        "verdict": "promote" if (s_summary["dti"] > dti_r0 and lane_ok) else "negative",
        "scope_note": "No DrivenData/leaderboard access, no submission, no organizer receipt. "
                      "0.2778 (GEMSDOE32 h33-h33-2-b2) is an owner-reported CLAIM, not a receipt; "
                      "whether this submission scores higher is ORGANIZER-CONFIRMED only after upload.",
    }
    (EVIDENCE / "stepover_evidence.json").write_text(json.dumps(ev, indent=2), encoding="utf-8")

    # 11. Run card (protocol rule 5)
    card = {
        "created_utc": ev["created_utc"],
        "branch": "arena/aebe414f-gemsdoe92",
        "submission_name": name,
        "submission_note": note,
        "note_chars": len(note),
        "hypothesis": ev["hypothesis"],
        "mechanism": ev["mechanism"],
        "named_non_fault_mimic": ev["non_fault_mimic"],
        "holdout_dti": s_summary["dti"],
        "holdout_ci95": s_summary["ci95"],
        "holdout_withheld_positives": s_summary["withheld_positive_pixels"],
        "holdout_evaluator_version": "gems57-pooled-hide-v2",
        "delta_vs_R0": ps["paired_differences"]["R0"]["delta"],
        "delta_vs_R0_ci95": ps["paired_differences"]["R0"]["ci95"],
        "leakage_canary_auc": max(auc_s, auc_dot),
        "leakage_canary_limit": 0.90,
        "lane_worst_rho": max(
            surface_report["worst_spearman_full_footprint"] or -1,
            dots_report["worst_spearman_full_footprint"] or -1,
        ),
        "lane_worst_forward_overlap": dots_report["worst_dot_overlap"],
        "lane_unique": bool(lane_ok),
        "raster_sha256": receipt["sha256"],
        "validator": {
            "no_nan_inside_footprint": True,
            "values_in_0_1": True,
            "crs_shape_transform_match_sample_submission": True,
            "zero_catalogue_mass": True,
            "dots_within_3px_of_catalogue": 0,
            "gates_pass": bool(ok),
        },
        "verdict": ("promote" if (s_summary["dti"] > dti_r0 and lane_ok) else "negative"),
    }
    card["verdict"] = card["verdict"]  # noop, keeps key order
    RUN_CARD.write_text(json.dumps(card, indent=2), encoding="utf-8")
    print(json.dumps(card, indent=2))
    print(f"Run card: {RUN_CARD}")
    print(f"Evidence: {EVIDENCE / 'stepover_evidence.json'}")
    print(f"Verdict: {card['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
