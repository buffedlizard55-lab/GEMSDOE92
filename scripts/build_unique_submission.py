#!/usr/bin/env python3
"""
Build a GEMSDOE competition submission GeoTIFF that is:

1. UNIQUE -- not a byte-for-byte or nearest-neighbor copy of any GEMSDOE site
   submission.  Dots are placed from a *different* generative mechanism than
   GEMSDOE32's R0 (H19-5 skeleton thinning + 200 m catalogue collar):
   a two-band catalogue-distance + geophysical-gradient placement that targets
   both fault damage zones (2-8 px from mapped traces) and the blind-fault
   corridor (>1.5 km from mapped traces), where the holdout analysis shows
   5.65x higher hidden-fault density.

2. FORMAT-SAFE -- single-band float32 GeoTIFF, EPSG:32611, 3730x3292,
   sample-submission transform, ALL finite values in [0,1], zeros outside the
   footprint, zero mass on mapped catalogue faults.  This fixes the
   "Predicted values must be in range [0, 1]" portal error caused by NaN
   / out-of-range exterior pixels.

Outputs:
  docs/downloads/<stem>-zeros.tif      (upload-safe, zeros outside footprint)
  docs/downloads/<stem>-zeros.zip      (one-TIFF ZIP)
  docs/downloads/<stem>-zeros-audit.json (format + uniqueness audit)
  docs/downloads/<stem>_run_card.json  (protocol run card)

Usage: python scripts/build_unique_submission.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
from gems.gates import run_gates, summarise  # noqa: E402
from gems57.validate import assert_submittable, validate  # noqa: E402

SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
CATALOGUE = ROOT / "data" / "bridge" / "existing_faults.tif"
DOWNLOADS = ROOT / "docs" / "downloads"
DOWNLOADS.mkdir(parents=True, exist_ok=True)

# --- competition grid -------------------------------------------------------
ALPHA, BETA, R_PX = 0.2, 0.8, 3.0
N_DOTS = 37_654  # same budget as GEMSDOE32's R0 for a like-for-like comparison
OFFS = [(dy, dx, 1.0 - np.hypot(dy, dx) / R_PX)
        for dy in range(-3, 4) for dx in range(-3, 4)
        if 1.0 - np.hypot(dy, dx) / R_PX > 0]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_grid(path):
    with rasterio.open(path) as ds:
        arr = ds.read(1).astype(np.float64)
        meta = dict(
            crs=ds.crs, transform=ds.transform,
            shape=(ds.height, ds.width), dtype=ds.dtypes[0], count=ds.count,
        )
    return arr, meta


def write_geotiff(path, arr_float32, ref_meta):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        path, "w", driver="GTiff",
        height=ref_meta["shape"][0], width=ref_meta["shape"][1],
        count=1, dtype="float32",
        crs=ref_meta["crs"], transform=ref_meta["transform"],
        nodata=None, compress="deflate",
    ) as ds:
        ds.write(arr_float32.astype(np.float32), 1)
    return sha256_file(path)


def main() -> int:
    # 1. Read reference grid + catalogue
    sample_arr, ref_meta = read_grid(SAMPLE)
    footprint = np.isfinite(sample_arr)
    H, W = ref_meta["shape"]

    with rasterio.open(CATALOGUE) as ds:
        cat = ds.read(1).astype(np.float64)
    cat_mask = (cat > 0) & footprint  # mapped faults pixel-exactly

    # 2. Distance transform from catalogue (px)
    dist_cat = ndi.distance_transform_edt(~cat_mask).astype(np.float32)

    # 3. Geophysical gradient alignment: distance from H19-5 ridge skeleton.
    #    h19_5.tif is the GEMSDOE19/GEMSDOE32 lineage skeleton.  We use it ONLY
    #    as a directional prior (ridge normal), not as a dot source: dots are
    #    snapped to the corridor 1 px off the ridge (the observed sub-pixel
    #    dip offset between surface traces and geothermal gradients).
    h195_path = ROOT / "data" / "bridge" / "h19_5.tif"
    h195_arr, _ = read_grid(h195_path)
    h195_mask = (h195_arr > 0) & footprint
    d_to_h195 = ndi.distance_transform_edt(~h195_mask).astype(np.float32)

    # 4. Two-band eligibility:
    #    Band A (damage zone): 2 <= d_cat < 8 px   -- near mapped faults,
    #                        within kernel reach of withheld truth continuations.
    #    Band B (blind corridor): d_cat >= 15 px   -- >1.5 km from mapped faults
    #                        where hidden-fault density is 5.65x higher.
    band_a = (dist_cat > 2.0) & (dist_cat < 8.0) & footprint & ~cat_mask
    band_b = (dist_cat >= 15.0) & footprint & ~cat_mask

    #    Combine with gradient-alignment weighting: prefer pixels 1-2 px off
    #    the H19-5 ridge (dip-offset corridor) inside each band.
    align = np.where((d_to_h195 >= 1.0) & (d_to_h195 <= 2.0), 1.5, 1.0)
    weight_a = np.zeros((H, W), np.float64)
    if band_a.any():
        weight_a[band_a] = align[band_a] * (1.0 / (1.0 + dist_cat[band_a] / 4.0))
    weight_b = np.zeros((H, W), np.float64)
    if band_b.any():
        weight_b[band_b] = align[band_b] * np.minimum(1.0, dist_cat[band_b] / 3000.0)

    # 5. Allocate dots: 40% damage zone (high recall), 60% blind corridor
    #    (higher hidden-fault density per holdout analysis).
    n_a = int(N_DOTS * 0.40)
    n_b = N_DOTS - n_a

    def select_dots(weight_mask, n_target):
        """Greedy distance-thinned selection: pick highest-weight pixel,
        suppress all pixels within 3 px (kernel support) to avoid redundant
        false-positive mass under the triangular kernel."""
        ys, xs = np.nonzero(weight_mask)
        if len(ys) == 0:
            return np.empty(0, np.int64), np.empty(0, np.int64)
        w = weight_mask[ys, xs]
        order = np.argsort(-w, kind="stable")
        ys, xs, w = ys[order], xs[order], w[order]
        taken = np.zeros(len(ys), bool)
        chosen_y, chosen_x = [], []
        grid_taken = np.zeros((H, W), bool)
        for i in range(len(ys)):
            if len(chosen_y) >= n_target:
                break
            if taken[i]:
                continue
            y, x = int(ys[i]), int(xs[i])
            if grid_taken[y, x]:
                continue
            chosen_y.append(y)
            chosen_x.append(x)
            # suppress 3-px halo (exactly the kernel support) to avoid overlap
            y0, y1 = max(0, y - 3), min(H, y + 4)
            x0, x1 = max(0, x - 3), min(W, x + 4)
            grid_taken[y0:y1, x0:x1] = True
        return np.array(chosen_y, np.int64), np.array(chosen_x, np.int64)

    ay, ax = select_dots(weight_a, n_a)
    by, bx = select_dots(weight_b, n_b)
    all_y = np.concatenate([ay, by])
    all_x = np.concatenate([ax, bx])

    # If we couldn't fill the quota from band A, top up from remaining band B
    # pixels not already chosen.
    if len(all_y) < N_DOTS:
        need = N_DOTS - len(all_y)
        chosen = set(zip(all_y.tolist(), all_x.tolist()))
        by2, bx2 = np.nonzero(band_b)
        add = [(int(y), int(x)) for y, x in zip(by2, bx2) if (int(y), int(x)) not in chosen]
        add = add[:need]
        if add:
            all_y = np.concatenate([all_y, np.array([a[0] for a in add], np.int64)])
            all_x = np.concatenate([all_x, np.array([a[1] for a in add], np.int64)])

    n_final = min(len(all_y), N_DOTS)
    all_y, all_x = all_y[:n_final], all_x[:n_final]

    print(f"Band A (damage zone 2-8px): {len(ay)} dots")
    print(f"Band B (blind corridor >15px): {len(by)} dots")
    print(f"Final dots: {n_final}")

    # 6. Build prediction raster: binary dots, zeros outside footprint, zero on
    #    catalogue, all finite, values in {0,1} subset of [0,1].
    pred = np.zeros((H, W), dtype=np.float32)
    pred[all_y, all_x] = 1.0
    pred[~footprint] = 0.0
    pred[cat_mask] = 0.0

    # Safety: enforce [0,1] and finiteness explicitly
    assert np.isfinite(pred).all(), "non-finite values present"
    assert pred.min() >= 0.0 and pred.max() <= 1.0, "values outside [0,1]"
    assert (pred[~footprint] == 0).all(), "mass outside footprint"
    assert (pred[cat_mask] == 0).all(), "mass on catalogue"

    # 7. Tag + write TIFF + ZIP
    tag = hashlib.sha1(np.sort(np.ravel_multi_index((all_y, all_x), (H, W))).astype(np.int64).tobytes()).hexdigest()[:8]
    stem = f"gemsdoe92-blindcorridor-{n_final}dots-20261028-{tag}"
    tif = DOWNLOADS / f"{stem}-zeros.tif"
    name = f"gemsdoe92-blindcorridor-{n_final}d-{tag}"
    note = (f"Blind corridor + damage-zone dots: {n_final} binary dots at 2-8px and >1.5km from "
            f"mapped faults, 1px off H19-5 ridge; 70%/3px caps. MODEL only.")
    assert len(note) <= 140, f"note too long: {len(note)}"

    file_sha = write_geotiff(tif, pred, ref_meta)
    zip_path = DOWNLOADS / f"{stem}-zeros.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(tif, arcname=tif.name)

    # 8. Format gates (submission encoding)
    gates = run_gates(str(tif), str(SAMPLE), str(CATALOGUE), prune_radius=2,
                      require_submission_encoding=True)
    ok, report = summarise(gates)
    print("\n--- FORMAT GATES ---")
    print(report)

    v = validate(tif, footprint, cat_mask)
    assert_submittable(v)

    with rasterio.open(tif) as ds:
        a = ds.read(1)
        grid_ok = dict(
            crs=str(ds.crs), shape=list(ds.shape),
            transform=list(tuple(ds.transform)[:6]), dtype=ds.dtypes[0], count=ds.count,
        )
    with rasterio.open(SAMPLE) as ds:
        ref = dict(crs=str(ds.crs), shape=list(ds.shape),
                   transform=list(tuple(ds.transform)[:6]))

    validator_output = dict(
        no_nan_in_footprint=bool(np.isfinite(a[footprint]).all()),
        no_nan_anywhere=bool(np.isfinite(a).all()),
        values_in_0_1=bool(a.min() >= 0 and a.max() <= 1),
        crs_match=grid_ok["crs"] == ref["crs"],
        shape_match=grid_ok["shape"] == ref["shape"],
        transform_match=grid_ok["transform"] == ref["transform"],
        dtype_float32=grid_ok["dtype"] == "float32",
        single_band=grid_ok["count"] == 1,
        zeros_outside_footprint=bool((a[~footprint] == 0).all()),
        zero_mass_on_mapped_catalogue=bool((a[cat_mask] == 0).all()),
        n_positive=int((a > 0).sum()),
        gates_pass=bool(ok),
        gems57_validate_pass=True,
        gates=[dict(name=g.name, ok=bool(g.ok), detail=g.detail) for g in gates],
    )

    # 9. Uniqueness vs available reference rasters (d28, h19_5, h27_4_solo)
    #    plus the GEMSDOE32 R0 lineage if present.
    refs = {}
    for f in ["d28.tif", "h19_5.tif", "h27_4_solo.tif"]:
        p = ROOT / "data" / "bridge" / f
        if p.is_file():
            arr, _ = read_grid(p)
            refs[f] = arr

    uniqueness_rows = []
    our_dots_lin = np.ravel_multi_index((all_y, all_x), (H, W))
    our_bool = np.zeros(H * W, bool)
    our_bool[our_dots_lin] = True
    from scipy.spatial import cKDTree as _Tree
    for fname, arr in refs.items():
        their = np.nonzero((arr > 0) & footprint)
        if len(their[0]) == 0:
            continue
        tree = _Tree(np.c_[their[0], their[1]])
        d, _ = tree.query(np.c_[all_y, all_x], k=1)
        overlap = float((d <= 3.0).mean())
        uniqueness_rows.append(dict(
            reference=fname, n_their=int(len(their[0])),
            overlap_3px=round(overlap, 6),
            within_limit=overlap <= 0.70,
        ))

    worst_overlap = max((r["overlap_3px"] for r in uniqueness_rows), default=0.0)
    unique_vs_available = worst_overlap <= 0.70

    # 10. Run card
    card = dict(
        schema="gemsdoe92-run-card-v3",
        created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        lane="UNIQUE — blind-fault corridor + damage-zone (catalogue-distance bands)",
        experiment="1 of 3 (budget)",
        hypothesis=(
            "Hidden geothermal faults cluster in two distinct settings: (a) damage zones "
            "2-8 px (200-800 m) from mapped catalogue traces where withheld truth continues "
            "mapped strands, and (b) the blind-fault corridor >1.5 km from mapped faults where "
            "holdout analysis shows 5.65x higher hidden-fault density.  Dots are placed 1 px "
            "off the H19-5 geophysical ridge (dip-offset corridor), NOT by thinning the H19-5 "
            "skeleton itself -- a different generative mechanism from GEMSDOE32's R0."
        ),
        mechanism=(
            "Two-band catalogue-distance eligibility (damage zone 2-8 px; blind corridor >15 px) "
            "weighted by H19-5 ridge-alignment (1-2 px off centerline), greedy 3-px halo "
            "suppression to suppress redundant FP mass, exact {0,1} binary dots, zero mass on "
            "catalogue, zeros outside footprint."
        ),
        named_non_fault_mimic="Lake Lahontan paleoshorelines and incised volcanic canyon rims (high raw curvature, non-tectonic)",
        raster=dict(file=f"docs/downloads/{tif.name}", zip=f"docs/downloads/{zip_path.name}",
                    sha256=file_sha, bytes=tif.stat().st_size, n_dots=n_final),
        raster_sha256=file_sha,
        submission_name=name, note=note, note_chars=len(note),
        holdout_dti=dict(
            evidence_class="MODEL-ONLY (no organizer receipt; holdout not rerun this session)",
            note="Catalogue hide-and-recover HOLDOUT-DTI not independently computed; reported only as MODEL projection.",
        ),
        model_estimate=dict(
            evidence_class="MODEL (not an organizer score)",
            projection="0.30-0.34 range expected (per holdout-density analysis in docs/WHY_0_2778.md)",
            basis="Reallocates R0's wasted near-catalogue dots to blind corridor (>1.5 km, 5.65x density) + damage zone (2-8 px).",
        ),
        leakage_canaries=dict(
            threshold=0.90,
            note="Single-feature canary not run on full 19-band stack (stack absent); band-6 radiometric TC verified as tc (r=0.997140), not magnetic tilt.",
            canaries_run=False,
        ),
        uniqueness=dict(
            interpretation="PI-1 (gems/uniqueness_v3.py); registry cache (.cache/registry_v3) absent in this checkout -- checked vs available bridge rasters only",
            references=uniqueness_rows,
            worst_overlap_3px=round(worst_overlap, 6),
            unique_vs_available=unique_vs_available,
            note="Full 2,060-raster registry audit requires .cache/registry_v3 (network staging pending). Literal reading vs the pinned 17GEMSDOE dense witness is unresolved.",
        ),
        validator_output=validator_output,
        gates_passed=dict(
            format=bool(ok),
            values_in_0_1=validator_output["values_in_0_1"],
            no_nan_anywhere=validator_output["no_nan_anywhere"],
            zeros_outside_footprint=validator_output["zeros_outside_footprint"],
            zero_mass_on_mapped_catalogue=validator_output["zero_mass_on_mapped_catalogue"],
            uniqueness_vs_available=unique_vs_available,
        ),
        verdict="format_pass" if ok and unique_vs_available else "format_pass_uniqueness_pending",
        submission_eligible=False,
        slot_note=("Weekly cap is 3 submissions/week (competition website prevails). "
                   "Full registry uniqueness (PI-1 vs all public GEMSDOE rasters) and the "
                   "literal-dense-witness question are unresolved; a weekly-slot selector "
                   "must clear this separately.  NOT cleared for upload by this script."),
    )

    card_path = DOWNLOADS / f"{stem}_run_card.json"
    card_path.write_text(json.dumps(card, indent=1, default=float), encoding="utf-8")

    audit = dict(
        file=f"docs/downloads/{tif.name}",
        sha256_zeros=file_sha,
        overall_pass=bool(ok),
        n_positive_pixels=int(n_final),
        gates_zeros=[dict(name=g.name, ok=bool(g.ok)) for g in gates],
        validator_output={k: v for k, v in validator_output.items() if isinstance(v, bool)},
        verdict=card["verdict"],
        submission_eligible=False,
        run_card=f"downloads/{card_path.name}",
        uniqueness=card["uniqueness"],
    )
    (DOWNLOADS / f"{stem}-zeros-audit.json").write_text(json.dumps(audit, indent=1), encoding="utf-8")

    print(f"\n--- RESULT ---")
    print(f"File: {tif}")
    print(f"SHA-256: {file_sha}")
    print(f"Dots: {n_final}")
    print(f"Name: {name}")
    print(f"Note: {note}")
    print(f"Verdict: {card['verdict']}")
    print(f"Gates pass: {ok}")
    print(f"Unique vs available refs: {unique_vs_available} (worst overlap {worst_overlap:.4f})")
    print(f"Submission eligible: {card['submission_eligible']} (full registry audit pending)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
