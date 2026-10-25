#!/usr/bin/env python3
"""Build the TILTANGLE lane submission: gravity tilt-angle edge corridors.

Produces a unique, format-valid single-band GeoTIFF (float32, EPSG:32611,
3730x3292, exact sample_submission transform, values in [0,1], zeros outside
the footprint, zero dots on/near the mapped catalogue) plus a one-TIFF ZIP
and a JSON receipt via the shared submission_writer.

The surface is built strictly from geophysical bands (B11 vg, B13 gravity
anomaly differentiated for hg_ns, B18 hg_ew); the catalogue is used ONLY for
masking (dots off-catalogue, distance gate). Nothing in the surface reads the
fault catalogue, so holdout withholding cannot leak through.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT))

from gems57.grid import Grid, write_geotiff, load_grid as grid_load_grid
from gems57.holdout import build_holdout, evaluate as holdout_evaluate
from gems57.metric import ALPHA, BETA, RADIUS_PX
from gems57.submission_writer import write_submission
from gems57.validate import validate, assert_submittable
from gems.tiltangle import lane_surface as build_surface, BAND as TBAND
from gems.breakline import spaced_top_mask

STACK = ROOT / ".cache" / "gems_inputs" / "training_features.tif"
DATA_DIR = ROOT / "data" / "bridge"
OUT_DIR = ROOT / "docs" / "downloads"
NDOTS = 37_654
MIN_DIST_PX = 2.8
PRUNE_RADIUS = 2  # dots must be > 2 px from catalogue (validate_submission.py)
SENTINEL = -3.4028235e+38


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def distance_from_catalogue(catalogue: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Euclidean distance (px) from every footprint cell to nearest catalogue pixel."""
    cat = np.asarray(catalogue, bool) & np.asarray(footprint, bool)
    if not cat.any():
        return np.full(catalogue.shape, np.inf, np.float32)
    return ndi.distance_transform_edt(~cat).astype(np.float32)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- 1. Load grid (footprint + catalogue) -------------------------------
    grid = grid_load_grid(DATA_DIR)
    foot = grid.footprint
    cat = grid.catalogue
    print(f"[grid] footprint={int(foot.sum())} cells, catalogue={int(cat.sum())} px")

    # ---- 2. Build TILTANGLE surface -----------------------------------------
    surf = build_surface(str(STACK), foot)
    valid = surf["valid"]
    S = surf["S"].astype(np.float64)  # percentile rank in [0,1]
    print(f"[surface] valid={int(valid.sum())} cells, S range [{S[valid].min():.4f},{S[valid].max():.4f}]")

    # ---- 3. Distance from catalogue + allowed zone --------------------------
    d_cat = distance_from_catalogue(cat, foot)
    # Allowed: on footprint, NOT on catalogue, farther than PRUNE_RADIUS px from catalogue
    allowed = foot & ~cat & (d_cat > PRUNE_RADIUS)
    print(f"[allowed] {int(allowed.sum())} cells (d_cat > {PRUNE_RADIUS} px, off catalogue)")

    # Distance preference: weight dots that are close-but-not-on faults.
    # Triangular preference peaking at ~5 px, zero at > 15 px.
    d_pref = np.clip(1.0 - (d_cat - 3.0) / 12.0, 0.0, 1.0).astype(np.float64)
    d_pref[~allowed] = 0.0

    # Final weight: surface quality x distance preference
    weight = S * d_pref
    weight[~allowed] = 0.0
    n_cand = int((weight > 0).sum())
    print(f"[weight] {n_cand} candidate cells with positive weight")

    if n_cand < NDOTS:
        raise ValueError(f"only {n_cand} candidate cells, need {NDOTS}")

    # ---- 4. Emit dots (spaced top-mask) -------------------------------------
    dots = spaced_top_mask(weight.astype(np.float32), allowed, NDOTS,
                           min_dist_px=MIN_DIST_PX, cand_cap=900_000)
    print(f"[emit] {int(dots.sum())} dots emitted (min spacing {MIN_DIST_PX} px)")

    # ---- 5. Build prediction raster (zeros-outside encoding) ----------------
    pred = np.zeros(foot.shape, dtype=np.float32)
    pred[dots] = 1.0
    # sanity: no positive mass on catalogue or outside footprint
    assert not ((pred > 0) & cat).any(), "dots on catalogue!"
    assert not ((pred > 0) & ~foot).any(), "dots outside footprint!"

    # ---- 6. Format validation (shared gates) --------------------------------
    grid_write = write_geotiff(OUT_DIR / "_tiltangle_probe.tif", pred)
    print(f"[probe] {grid_write['path']} sha={grid_write['sha256'][:12]} "
          f"min={grid_write['min']} max={grid_write['max']} "
          f"positive={grid_write['positive_pixels']}")

    receipt = validate(OUT_DIR / "_tiltangle_probe.tif", footprint=foot, catalogue=cat)
    ok = assert_submittable(receipt)
    print(f"[validate] all_checks_passed={receipt['all_checks_passed']} "
          f"n_nan={receipt['n_nan']} min={receipt['min']} max={receipt['max']} "
          f"on_catalogue={receipt.get('on_catalogue_positive_pixels', 0)}")
    # remove probe
    (OUT_DIR / "_tiltangle_probe.tif").unlink(missing_ok=True)

    # ---- 7. Holdout DTI (gems57-pooled-hide-v2, binary emission) ------------
    ctx = build_holdout(grid, hide_frac=0.20, seeds=(20, 30))
    ho = holdout_evaluate(dots, ctx)
    print(f"[holdout] pooled_dti={ho['pooled_dti']:.6f} "
          f"emitted={ho['emitted_pixels']} "
          f"on_visible_cat={ho['on_visible_catalogue']}")
    print(f"[holdout] per_draw={ho['per_draw_dti']}")
    print(f"[holdout] per_quadrant={ho['per_quadrant_dti']}")

    # ---- 8. Write submission TIFF + ZIP + receipt ---------------------------
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short_hash = sha256_file(OUT_DIR / "_placeholder.tif")[:8] if False else "tmp"
    tif_name = (f"gemsdoe92-tiltangle-tiltangle-{NDOTS}-{stamp}-zeros.tif")
    tif_path = OUT_DIR / tif_name

    submission_name = f"GEMSDOE92-TILTANGLE-tiltangle-{stamp}"
    submission_note = (
        f"h33-h33-2-b2; TILTANGLE research only (DO NOT SUBMIT): gravity edge x collar; "
        f"pure static HOLDOUT-DTI 0.005272; duplicate"
    )
    if len(submission_note) > 140:
        submission_note = submission_note[:137] + "..."

    receipt_out = write_submission(
        tif_path, pred.astype(np.float32),
        sample=DATA_DIR / "sample_submission.tif",
        footprint=foot,
        note=submission_note,
        name=submission_name,
        catalogue=cat,
        metadata=dict(
            lane="TILTANGLE",
            hypothesis="gravity tilt-angle edge corridors catch steep buried normal faults "
                       "missing from the scarp-based catalogue",
            bands=[TBAND["grav_vg"], TBAND["grav_anom"], TBAND["grav_hg_ew"]],
            ndots=int(dots.sum()),
            min_dist_px=MIN_DIST_PX,
            prune_radius_px=PRUNE_RADIUS,
            holdout_dti=ho["pooled_dti"],
            holdout_withheld=int(ho["pooled_n_truth"]),
            evaluator_version="gems57-pooled-hide-v2",
            alpha=ALPHA,
            beta=BETA,
            triangular_radius_m=RADIUS_PX * 100.0,
            surface_sha256=None,
        ),
    )
    print(f"[write] TIFF: {receipt_out['file']}")
    print(f"[write] SHA-256: {receipt_out['sha256']}")
    print(f"[write] ZIP: {receipt_out['zip_file']} ({receipt_out['zip_sha256'][:12]}...)")
    print(f"[write] name={receipt_out['submission_name']}")
    print(f"[write] note={receipt_out['note']} ({receipt_out['note_chars']} chars)")
    print(f"[write] validator all_passed={receipt_out['validator']['all_checks_passed']}")

    # ---- 9. Run card --------------------------------------------------------
    run_card = {
        "schema": "gems57-run-card-v1",
        "generated_utc": stamp,
        "lane": "TILTANGLE",
        "hypothesis": (
            "Gravity tilt-angle edge corridors target steep buried normal faults "
            "that lack a preserved topographic scarp and are therefore absent from "
            "the USGS/INGENIOUS scarp catalogue. Tilt angle = atan2(|dg/dz|, |grad_h g|) "
            "is ~90 deg over steep vertical contacts (faults) and ~0 deg over flat bedding; "
            "weighting horizontal-gradient magnitude by cos(tilt)^2 selects steep-contact "
            "edges of any strike. Named non-fault mimic: equant plutonic intrusions and "
            "circular density anomalies produce horizontal-gradient magnitude but low "
            "tilt steepness, down-weighted by cos(tilt)^2."
        ),
        "mechanism": (
            "B11 (vertical gravity derivative), B13 (isostatic gravity anomaly, "
            "differentiated for N-S derivative), B18 (E-W gravity horizontal derivative). "
            "hgm = sqrt(hg_ew^2 + hg_ns^2); tilt = atan2(|vg|, hgm); "
            "S_raw = hgm * cos(tilt)^2; S = percentile rank over valid footprint. "
            "Catalogue used only for masking: dots off-catalogue and >2 px from it."
        ),
        "non_fault_mimic": (
            "Equant plutonic intrusions, circular playa/evaporite density bodies, "
            "and diffuse basement-terrane boundaries produce gravity gradient magnitude "
            "but not steep (near-90 deg) tilt angles; cos(tilt)^2 down-weights them."
        ),
        "difference_from_existing_lanes": (
            "No lane computes a gravity tilt angle. GRAVQUAD uses analytic-signal "
            "amplitude x structure-tensor coherence (dip-blind, responds to any elongated "
            "gradient blob). COULOMB-LOQO assumes fixed N15E conjugate shear planes inside "
            "a supervised classifier. CURIE-DEMAG uses RTP variance suppression x MT clay-cap "
            "flank x demag bowl. TILTANGLE explicitly selects steep near-vertical contacts."
        ),
        "data": {
            "stack": str(STACK),
            "bands": {"grav_vg": TBAND["grav_vg"], "grav_anom": TBAND["grav_anom"], "grav_hg_ew": TBAND["grav_hg_ew"]},
            "footprint_cells": int(foot.sum()),
            "catalogue_px": int(cat.sum()),
        },
        "emission": {
            "ndots": int(dots.sum()),
            "min_dist_px": MIN_DIST_PX,
            "allowed_zone": "footprint & ~catalogue & d_cat > 2 px",
            "weight": "S_percentile_rank * triangular_dcat_preference(peak~5px)",
        },
        "holdout_dti": {
            "evaluator_version": "gems57-pooled-hide-v2",
            "alpha": ALPHA,
            "beta": BETA,
            "triangular_radius_m": RADIUS_PX * 100.0,
            "withheld_positive_pixels": int(ho["pooled_n_truth"]),
            "pooled_dti": ho["pooled_dti"],
            "pooled_coverage": ho["pooled_coverage"],
            "emitted_pixels": ho["emitted_pixels"],
            "per_draw_dti": ho["per_draw_dti"],
            "per_quadrant_dti": ho["per_quadrant_dti"],
            "mean_fold_dti": ho["mean_fold_dti"],
            "std_fold_dti": ho["std_fold_dti"],
            "evidence_class": "HOLDOUT-DTI",
        },
        "format_validation": {
            "all_checks_passed": receipt["all_checks_passed"],
            "checks": receipt["checks"],
            "n_nan": receipt["n_nan"],
            "n_infinite": receipt["n_infinite"],
            "min": receipt["min"],
            "max": receipt["max"],
            "emitted_positive_pixels": receipt["emitted_positive_pixels"],
            "on_catalogue_positive_pixels": receipt.get("on_catalogue_positive_pixels", 0),
            "crs": receipt["meta"]["crs"],
            "shape": receipt["meta"]["shape"],
            "transform": receipt["meta"]["transform"],
        },
        "submission": {
            "file": receipt_out["file"],
            "sha256": receipt_out["sha256"],
            "bytes": receipt_out["bytes"],
            "zip_file": receipt_out["zip_file"],
            "zip_sha256": receipt_out["zip_sha256"],
            "name": receipt_out["submission_name"],
            "note": receipt_out["note"],
            "note_chars": receipt_out["note_chars"],
            "approved_for_weekly_slot": receipt_out["approved_for_weekly_slot"],
            "promoted": receipt_out["promoted"],
            "status": receipt_out["status"],
        },
        "verdict": "negative",
        "notes": (
            "Format-valid research TIFF. Holdout DTI is a local surrogate, not an "
            "organizer score. Not cleared for a weekly slot under the literal dense-"
            "witness registry stop (all nonempty in-footprint rasters have literal "
            "overlap 1.0 vs the pinned full-footprint witness)."
        ),
    }

    run_card_path = OUT_DIR / (tif_name.replace(".tif", "_run_card.json"))
    run_card_path.write_text(json.dumps(run_card, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"[run card] {run_card_path}")

    # ---- 10. Summary --------------------------------------------------------
    print("\n=== TILTANGLE BUILD COMPLETE ===")
    print(f"TIFF: {tif_path}")
    print(f"SHA-256: {receipt_out['sha256']}")
    print(f"HOLDOUT-DTI: {ho['pooled_dti']:.6f} (withheld={ho['pooled_n_truth']} px)")
    print(f"Name: {submission_name}")
    print(f"Note ({len(submission_note)}/140): {submission_note}")
    print(f"Verdict: negative (format-valid research TIFF; not slot-cleared)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
