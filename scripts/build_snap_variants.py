#!/usr/bin/env python3
"""Reproducibly build three controlled, spacing-preserving SNAP variants of R0.

Strict compliance with Agent Brief v2:
- Verifies SHA-256 and byte length of all pinned inputs in registry/session_manifest.json
  (and registry/data_manifest.json when data/ is present) before reading any file.
- Rebuilds parent R0 (h33-h33-2-b2) through its exact H19-5 -> D1.5 -> D2.8 -> SOLO -> R0
  lineage and requires BOTH zeros and NaN SHA-256 digests to match byte-for-byte.
- Builds 3 variants on AXIS=SNAP that differ ONLY in the SNAP specification:
    1. scarp2p0px : <=2.0 px (200 m, half GeoDAWN 400 m line spacing) snap to joint
                    scarp slope + piedmont break-in-slope + TMI/gravity horizontal gradient.
    2. scarp1p4px : <=sqrt(2) px (141 m, 8-neighbor) snap to the identical joint surface.
    3. pot2p0px   : <=2.0 px (200 m) snap to provided TMI + unsigned gravity horizontal
                    gradient bands only (Band 3 tmi_hg + Band 5 iso_grav_anom_slope).
- Preserves exact count (37,654 unit-mass dots), parent catalogue exclusions (zero mass on
  catalogue, d_cat > 2.0 px), and parent D2.8 Poisson-disk spacing (min_nn >= 2.8284 px)
  so neighboring dots cannot clump inside the R=3 px DTI kernel.
- Properly masks float32 nodata sentinels (-3.4028235e+38 on 3,061 in-footprint pixels)
  and uses unsigned Band 5 (iso_grav_anom_slope) rather than signed E-W Band 18 (dg/dx).
- Writes releases/<id>.tif (NaN outside) and releases/<id>-zeros.tif (zeros outside),
  re-reads both from disk, runs all MUST-pass format gates, and records parent-diff
  and displacement statistics in ledger/submissions.csv and evidence/snap_variants.json.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from exact_dti_refill import dot_thin  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems.variants import Dots, snap_spaced  # noqa: E402
from gems57 import metric  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA_ZEROS = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
PARENT_SHA_NAN = "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd"
PARENT_SHA = {"zeros": PARENT_SHA_ZEROS, "nan": PARENT_SHA_NAN}

SESSION_MANIFEST = ROOT / "registry" / "session_manifest.json"
DATA_MANIFEST = ROOT / "registry" / "data_manifest.json"
OUT_DIR = ROOT / "releases"
LEDGER = ROOT / "ledger" / "submissions.csv"
RECEIPTS = ROOT / "evidence" / "snap_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"

DATE = "20261023"
SEED = 0  # Deterministic tie-breaking; zero stochastic draws.
MIN_NN_PX = 2.8
MIN_GAIN = 0.01


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_all_manifests() -> dict[str, Path]:
    """Verify SHA-256 and byte length of all pinned inputs before reading any raster."""
    doc = json.loads(SESSION_MANIFEST.read_text(encoding="utf-8"))
    resolved: dict[str, Path] = {}
    for item in doc["files"]:
        path = ROOT / item["local_path"]
        if not path.is_file():
            raise FileNotFoundError(
                f"Pinned input missing: {item['id']} at {path}; run scripts/restore_inputs.py"
            )
        got_sha = sha256_file(path)
        got_bytes = path.stat().st_size
        if got_sha != item["sha256"] or got_bytes != int(item["bytes"]):
            raise RuntimeError(
                f"Pinned input mismatch {item['id']}: sha={got_sha}, bytes={got_bytes}; "
                f"expected sha={item['sha256']}, bytes={item['bytes']}"
            )
        resolved[item["id"]] = path

    if DATA_MANIFEST.is_file():
        d_doc = json.loads(DATA_MANIFEST.read_text(encoding="utf-8"))
        for entry in d_doc.get("files", []):
            dest = ROOT / entry["dest"]
            if dest.is_file():
                got_sha = sha256_file(dest)
                if got_sha != entry["sha256"]:
                    raise RuntimeError(
                        f"data_manifest mismatch {entry['dest']}: got {got_sha} != {entry['sha256']}"
                    )
    return resolved


def percentile_rank(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    vals = np.asarray(a[valid], dtype=np.float32)
    knots = np.quantile(vals, np.linspace(0.0, 1.0, 1001))
    result = np.zeros(a.shape, dtype=np.float32)
    result[valid] = np.interp(vals, knots, np.linspace(0.0, 1.0, 1001)).astype(np.float32)
    return result


def build_and_verify_parent(inputs: dict[str, Path]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict]:
    """Rebuild R0 through exact lineage and require byte-identical zeros + NaN SHA-256."""
    with rasterio.open(inputs["sample_submission"]) as ds:
        template = ds.read(1)
        foot = np.isfinite(template)
        template_profile = ds.profile.copy()
    with rasterio.open(inputs["existing_faults"]) as ds:
        cat = (ds.read(1) > 0) & foot
        cat_profile = ds.profile.copy()
    d_cat = distance_transform_edt(~cat)

    with rasterio.open(inputs["anc_h19_5"]) as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    with rasterio.open(inputs["anc_d1_5"]) as ds:
        d15_ref = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    with rasterio.open(inputs["anc_d2_8"]) as ds:
        d28_ref = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    with rasterio.open(inputs["anc_solo_d2_8"]) as ds:
        solo_ref = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    with rasterio.open(inputs["parent_r0_zeros"]) as ds:
        r0_ref = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot

    d15 = dot_thin(h19, 1.5)
    d28 = dot_thin(h19, 2.8)
    solo = d28 & (d_cat > 1.0)
    r0 = d28 & (d_cat > 2.0)
    for stage_name, rebuilt, ref in (
        ("D1.5", d15, d15_ref),
        ("D2.8", d28, d28_ref),
        ("SOLO-D2.8", solo, solo_ref),
        ("R0", r0, r0_ref),
    ):
        if not np.array_equal(rebuilt, ref):
            raise RuntimeError(f"R0 lineage mask mismatch at stage {stage_name}")

    profile = cat_profile.copy()
    profile.update(
        driver="GTiff",
        dtype="float32",
        count=1,
        compress="deflate",
        predictor=3,
        zlevel=9,
        tiled=True,
        blockxsize=256,
        blockysize=256,
        nodata=None,
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp_zeros = OUT_DIR / "._r0-snap-check-zeros.tif"
    tmp_nan = OUT_DIR / "._r0-snap-check-nan.tif"
    with rasterio.open(tmp_zeros, "w", **profile) as ds:
        ds.write(np.where(foot, r0.astype(np.float32), 0.0).astype(np.float32), 1)
    p_nan = profile.copy()
    p_nan.update(nodata=np.nan)
    with rasterio.open(tmp_nan, "w", **p_nan) as ds:
        ds.write(np.where(foot, r0.astype(np.float32), np.nan).astype(np.float32), 1)

    hashes = {"zeros": sha256_file(tmp_zeros), "nan": sha256_file(tmp_nan)}
    tmp_zeros.unlink()
    tmp_nan.unlink()
    if hashes != PARENT_SHA:
        raise RuntimeError(f"Exact R0 SHA-256 rebuild mismatch: {hashes} != {PARENT_SHA}")

    return foot, cat, d_cat, h19, {
        "r0": r0,
        "profile": profile,
        "template_profile": template_profile,
        "parent_hashes": hashes,
    }


def build_edge_scarp_surfaces(
    inputs: dict[str, Path], foot: np.ndarray
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Build label-free potential-field edge and geomorphic scarp+break surfaces.

    Masks float32 nodata sentinel (-3.4028235e+38 on 3,061 in-footprint pixels)
    and uses unsigned Band 5 (iso_grav_anom_slope = ||grad g||) instead of
    signed E-W directional derivative Band 18 (dg/dx).
    """
    with rasterio.open(inputs["training_features"]) as ds:
        tmi_hg = ds.read(3, masked=True).filled(np.nan).astype(np.float32)
        grav_slope = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        det_slope = ds.read(19, masked=True).filled(np.nan).astype(np.float32)

    valid = (
        foot
        & np.isfinite(tmi_hg)
        & np.isfinite(grav_slope)
        & np.isfinite(det_slope)
        & (tmi_hg > -1e30)
        & (grav_slope > -1e30)
        & (det_slope > -1e30)
    )
    sy, sx = np.gradient(np.where(valid, det_slope, np.nan), 100.0)
    slope_break = np.hypot(sx, sy).astype(np.float32)
    valid_brk = valid & np.isfinite(slope_break)

    p_tmi = percentile_rank(np.where(valid, tmi_hg, 0.0), valid)
    p_grav = percentile_rank(np.where(valid, grav_slope, 0.0), valid)
    p_scarp = percentile_rank(np.where(valid, det_slope, 0.0), valid)
    p_brk = np.where(
        valid_brk,
        percentile_rank(np.where(valid_brk, slope_break, 0.0), valid_brk),
        p_scarp,
    )

    r_pot = np.where(valid, 0.65 * p_tmi + 0.35 * p_grav, -np.inf).astype(np.float32)
    r_es = np.where(
        valid,
        0.35 * p_scarp + 0.35 * p_brk + 0.20 * p_tmi + 0.10 * p_grav,
        -np.inf,
    ).astype(np.float32)
    return valid, {"pot": r_pot, "edge_scarp": r_es}


def write_tif(path: Path, profile: dict, foot: np.ndarray, mask: np.ndarray, nan_outside: bool) -> None:
    p = profile.copy()
    p.update(
        driver="GTiff",
        dtype="float32",
        count=1,
        compress="deflate",
        predictor=3,
        zlevel=9,
        tiled=True,
        blockxsize=256,
        blockysize=256,
        nodata=np.nan if nan_outside else None,
    )
    outside = np.nan if nan_outside else 0.0
    arr = np.where(foot, mask.astype(np.float32), np.float32(outside)).astype(np.float32)
    with rasterio.open(path, "w", **p) as ds:
        ds.write(arr, 1)


def validate_reopened(
    path: Path,
    template_path: Path,
    catalogue_path: Path,
    mask: np.ndarray,
    foot: np.ndarray,
    cat: np.ndarray,
    d_cat: np.ndarray,
    expect_nan_outside: bool,
) -> dict:
    with rasterio.open(template_path) as ref, rasterio.open(path) as ds:
        a = ds.read(1)
        checks = {
            "crs_matches": ds.crs == ref.crs,
            "shape_matches": ds.shape == ref.shape,
            "transform_matches": ds.transform == ref.transform,
            "dtype_float32": ds.dtypes == ("float32",),
            "one_band": ds.count == 1,
            "inside_finite": bool(np.isfinite(a[foot]).all()),
            "outside_encoding": (
                bool(np.isnan(a[~foot]).all())
                if expect_nan_outside
                else bool(np.all(a[~foot] == 0.0))
            ),
            "range_0_1": bool(np.all((a[foot] >= 0.0) & (a[foot] <= 1.0))),
            "binary_unit_mass": bool(np.array_equal(a[foot], mask[foot].astype(np.float32))),
            "zero_catalogue_mass": bool((a[cat] == 0.0).all()),
            "catalogue_distance_gt_2px": bool(np.all(d_cat[mask] > 2.0)),
            "count_37654": int(np.count_nonzero(a[foot])) == 37654,
        }
    # Cross-check with gems/gates.py (with R0's >2px clearance declared)
    gate_results = run_gates(path, template_path, catalogue_path=catalogue_path, prune_radius=2)
    gems_ok, gems_report = summarise(gate_results)
    checks["gems_gates_pass"] = bool(gems_ok)
    if not all(v for v in checks.values() if isinstance(v, bool)):
        raise RuntimeError(f"Re-read format gate failed for {path.name}: {checks}\n{gems_report}")
    return checks


def main() -> int:
    inputs = verify_all_manifests()
    foot, cat, d_cat, h19, parent = build_and_verify_parent(inputs)
    r0 = parent["r0"]
    n0 = int(r0.sum())
    if n0 != 37654 or np.any(r0 & cat) or np.any(d_cat[r0] <= 2.0):
        raise RuntimeError("R0 parent invariants failed")

    valid, surfaces = build_edge_scarp_surfaces(inputs, foot)
    keep_out = (~valid) | cat | (d_cat <= 2.0)

    ys0, xs0 = np.nonzero(r0)
    parent_dots = Dots(ys0, xs0, np.ones(len(ys0), dtype=np.float64))

    with rasterio.open(inputs["sgmc_faults_control"]) as ds:
        sgmc_raw = (ds.read(1) > 0) & foot
    sgmc_off = sgmc_raw & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_reference = metric.dti_binary(r0, sgmc_off, valid=foot, known=cat)

    specs = [
        {
            "value": "scarp2p0px",
            "surface_key": "edge_scarp",
            "max_shift": 2.0,
            "pred": "MODEL:+0.012",
            "pred_range": "[-0.006,+0.025]",
            "short_change": "SNAP <=2.0px edge+scarp+break (nn>=2.8)",
            "hypothesis": (
                "GeoDAWN's 400 m line spacing, 50-60 deg normal-fault hanging-wall dip projection, "
                "and D2.8's unweighted NW-seeded BFS thinning displace R0 dots by 100-200 m cross-strike "
                "from surface fault traces. Snapping <=2.0 px (200 m) onto the joint scarp slope + "
                "piedmont break-in-slope + TMI/gravity horizontal gradient crest while preserving "
                "D2.8's >=2.8 px Poisson spacing raises triangular-kernel credit k(d)=1-d/3 without "
                "along-strike dot clumping."
            ),
            "mechanism": (
                "At fixed S=37,654, DTI = T / (0.2T + 0.2(S-M) + 0.8|G|) rises ~0.26*DTI per unit "
                "fractional gain in T. Shifting dots <=200 m cross-strike onto the piedmont-to-facet "
                "slope inflection (0.35*pct(det_elev_slope) + 0.35*pct(||grad det_elev_slope||) + "
                "0.20*pct(tmi_hg) + 0.10*pct(iso_grav_anom_slope)) increases k(d) by +0.33 per 100 m "
                "of cross-strike error removed, while open-disc spacing d^2 >= 2.8^2 prevents "
                "adjacent dots from collapsing onto redundant kernel footprints."
            ),
            "non_fault_mimic": (
                "Erosional range-front facets, incised alluvial-fan terrace risers, Plio-Pleistocene "
                "pluvial lake shorelines (Lahontan/Bonneville), and resistant volcanic cliff ledges "
                "produce steep slope breaks within 200 m of concealed fault traces without hosting "
                "brittle surface rupture."
            ),
            "falsifier": (
                "A live receipt delta <= -0.01 vs R0 falsifies <=200 m surface-scarp localization and "
                "indicates new-fault truth is dominated by concealed intrabasinal traces or eroded "
                "facets offset from the topographic inflection; |delta| < 0.01 is no evidence."
            ),
        },
        {
            "value": "scarp1p4px",
            "surface_key": "edge_scarp",
            "max_shift": math.sqrt(2.0),
            "pred": "MODEL:+0.008",
            "pred_range": "[-0.004,+0.018]",
            "short_change": "SNAP <=1.41px 8-nbr edge+scarp+break (nn>=2.8)",
            "hypothesis": (
                "Restricting the identical joint scarp + break-in-slope + TMI/gravity edge snap to "
                "an 8-connected Moore window (<=sqrt(2) px = 141 m) corrects D2.8's 1-px NW ribbon-edge "
                "bias and sub-grid alignment error while preventing 2-px (200 m) upslope overshoot onto "
                "eroded footwall facets."
            ),
            "mechanism": (
                "Uses the exact same response surface, exclusions (d_cat > 2.0), count (37,654), and "
                "Poisson spacing (min_nn >= 2.828 px) as scarp2p0px, changing ONLY max_shift from "
                "2.0 px to sqrt(2) px. Comparing scarp1p4px vs scarp2p0px isolates capture radius "
                "(141 m vs 200 m) on identical physics."
            ),
            "non_fault_mimic": (
                "Local 100-141 m topographic terrace edges, talus aprons, and shallow volcanic dike "
                "margins adjacent to mapped H19-5 geophysical corridors."
            ),
            "falsifier": (
                "If scarp1p4px beats scarp2p0px by >= +0.01 on live receipts, the 200 m window "
                "overshoots onto footwall facets; if both trail R0 by >= 0.01, geomorphic scarp "
                "snapping degrades fault localization."
            ),
        },
        {
            "value": "pot2p0px",
            "surface_key": "pot",
            "max_shift": 2.0,
            "pred": "MODEL:-0.002",
            "pred_range": "[-0.014,+0.010]",
            "short_change": "SNAP <=2.0px TMI+grav horiz grad only (nn>=2.8)",
            "hypothesis": (
                "Pure potential-field horizontal-gradient control: if unmapped test faults are "
                "predominantly concealed intrabasinal structures beneath Quaternary playa/alluvial "
                "fill with no surface scarp, snapping <=2.0 px to 0.65*pct(tmi_hg) + "
                "0.35*pct(iso_grav_anom_slope) centers dots over subsurface susceptibility/density "
                "contacts without alluvial-channel or shoreline erosion mimics. Conversely, on dipping "
                "range-front normal faults, 63 deg magnetic inclination and hanging-wall dip projection "
                "shift potential-field gradients 150-300 m off the surface trace."
            ),
            "mechanism": (
                "Identical <=2.0 px window, count (37,654), exclusions (d_cat > 2.0), and spacing "
                "(min_nn >= 2.828 px) as scarp2p0px, removing only the topographic scarp/break terms. "
                "Uses unsigned Band 5 (iso_grav_anom_slope) rather than signed E-W Band 18 (dg/dx) so "
                "east-dipping and west-dipping normal faults are weighted symmetrically."
            ),
            "non_fault_mimic": (
                "Unfaulted plutonic intrusive margins, caldera ring dikes, tilted ash-flow tuff pinchouts, "
                "and hanging-wall down-dip projection offsets of moderately dipping normal faults."
            ),
            "falsifier": (
                "A live receipt gain >= +0.01 over both R0 and scarp2p0px falsifies our surface-scarp "
                "dominance model and proves hidden test faults are predominantly blind/concealed "
                "basement contacts best localized by potential fields alone."
            ),
        },
    ]

    used_hashes = {PARENT_SHA_NAN, PARENT_SHA_ZEROS}
    reserved_values = {s["value"] for s in specs}
    if LEDGER.is_file():
        with LEDGER.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if (
                    row.get("parent") == PARENT_ID
                    and row.get("axis") == "SNAP"
                    and row.get("value") in reserved_values
                ):
                    continue
                if row.get("sha256"):
                    used_hashes.add(row["sha256"].strip())
                for col in ("file_nan", "file_zeros"):
                    rel = (row.get(col) or "").strip()
                    if rel and (ROOT / rel).is_file():
                        used_hashes.add(sha256_file(ROOT / rel))

    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    variants: list[dict] = []
    new_cards: dict[str, dict] = {}

    for spec in specs:
        val = spec["value"]
        resp = surfaces[spec["surface_key"]]
        v = snap_spaced(
            parent=parent_dots,
            response=resp,
            value=val,
            max_shift=float(spec["max_shift"]),
            min_nn=MIN_NN_PX,
            min_gain=MIN_GAIN,
            footprint=foot,
            keep_out=keep_out,
        )
        mask = np.zeros(r0.shape, dtype=bool)
        mask[v.dots.ys, v.dots.xs] = True

        if int(mask.sum()) != n0 or np.any(mask & cat) or np.any(d_cat[mask] <= 2.0):
            raise RuntimeError(f"SNAP invariants failed at {val}")
        if v.stats["max_displacement_px"] > float(spec["max_shift"]) + 1e-6:
            raise RuntimeError(f"Displacement exceeded max_shift at {val}: {v.stats}")
        if v.stats["min_nn_px"] < MIN_NN_PX - 1e-6:
            raise RuntimeError(f"Poisson spacing violated at {val}: {v.stats}")

        removed = int(np.count_nonzero(r0 & ~mask))
        added = int(np.count_nonzero(mask & ~r0))
        if removed != added:
            raise RuntimeError(f"Count mismatch at {val}: removed={removed}, added={added}")
        pct_changed = 100.0 * removed / n0
        mean_disp = v.stats["mean_displacement_px"]
        med_disp = v.stats["median_displacement_px"]
        max_disp = v.stats["max_displacement_px"]
        frac_moved_pct = 100.0 * v.stats["frac_moved"]

        tmp_nan = OUT_DIR / f"._building-SNAP-{val}-nan.tif"
        tmp_zeros = OUT_DIR / f"._building-SNAP-{val}-zeros.tif"
        write_tif(tmp_nan, parent["profile"], foot, mask, True)
        write_tif(tmp_zeros, parent["profile"], foot, mask, False)

        validate_reopened(
            tmp_nan, inputs["sample_submission"], inputs["existing_faults"],
            mask, foot, cat, d_cat, True
        )
        validate_reopened(
            tmp_zeros, inputs["sample_submission"], inputs["existing_faults"],
            mask, foot, cat, d_cat, False
        )
        sha_nan = sha256_file(tmp_nan)
        sha_zeros = sha256_file(tmp_zeros)
        if sha_nan == sha_zeros or sha_nan in used_hashes or sha_zeros in used_hashes:
            tmp_nan.unlink(missing_ok=True)
            tmp_zeros.unlink(missing_ok=True)
            raise RuntimeError(f"Duplicate SHA-256 detected for SNAP {val}")
        used_hashes.update((sha_nan, sha_zeros))

        short_id = f"{PARENT_ID}-SNAP{val}-{DATE}-{sha_nan[:8]}"
        nan_path = OUT_DIR / f"{short_id}.tif"
        zeros_path = OUT_DIR / f"{short_id}-zeros.tif"
        tmp_nan.replace(nan_path)
        tmp_zeros.replace(zeros_path)

        checks_nan = validate_reopened(
            nan_path, inputs["sample_submission"], inputs["existing_faults"],
            mask, foot, cat, d_cat, True
        )
        checks_zero = validate_reopened(
            zeros_path, inputs["sample_submission"], inputs["existing_faults"],
            mask, foot, cat, d_cat, False
        )
        if sha256_file(nan_path) != sha_nan or sha256_file(zeros_path) != sha_zeros:
            raise RuntimeError(f"Post-rename disk reread SHA-256 mismatch at {val}")

        form_note = (
            f"{PARENT_ID}; {spec['short_change']}; mean disp {mean_disp:.2f}px; "
            f"pred {spec['pred']}"
        )
        if len(form_note) > 140:
            raise RuntimeError(f"Form note exceeds 140 chars ({len(form_note)}): {form_note}")

        sgmc_res = metric.dti_binary(mask, sgmc_off, valid=foot, known=cat)
        sgmc_delta = float(sgmc_res["dti"] - sgmc_reference["dti"])

        record = {
            "id": short_id,
            "site": "GEMSDOE92",
            "name": nan_path.name,
            "file_zeros": str(zeros_path.relative_to(ROOT)),
            "file_nan": str(nan_path.relative_to(ROOT)),
            "sha8": sha_nan[:8],
            "change_desc": (
                f"{spec['short_change']}; fixed 37654 dots; mean_disp={mean_disp:.4f}px "
                f"(moved {frac_moved_pct:.2f}%, {removed} px changed)"
            ),
            "notes": (
                f"seed={SEED}; mean_disp={mean_disp:.4f}px; max_disp={max_disp:.4f}px; "
                f"min_nn={v.stats['min_nn_px']:.4f}px; MODEL range {spec['pred_range']}; "
                f"SGMC PROXY delta {sgmc_delta:+.6f}; git={git_sha[:12]}; "
                f"see evidence/snap_variants.json"
            ),
            "parent": PARENT_ID,
            "axis": "SNAP",
            "value": val,
            "n_dots": n0,
            "pct_changed": round(pct_changed, 6),
            "removed": removed,
            "added": added,
            "sha256": sha_nan,
            "sha256_zeros": sha_zeros,
            "primary_file": nan_path.name,
            "fallback_file": zeros_path.name,
            "primary_encoding": "NaN outside footprint",
            "fallback_encoding": "zero outside footprint",
            "status": "BUILT",
            "predicted_change": spec["pred"],
            "predicted_range": spec["pred_range"],
            "prediction_scope": (
                "MODEL scenario range only; public-chunk changes under 0.01 are no evidence. "
                "PROXY instruments are diagnostics, never gates or scores."
            ),
            "displacement_stats": {
                "mean_displacement_px": round(mean_disp, 6),
                "mean_displacement_m": round(100.0 * mean_disp, 4),
                "median_displacement_px": round(med_disp, 6),
                "max_displacement_px": round(max_disp, 6),
                "dots_moved_count": int(round(v.stats["frac_moved"] * n0)),
                "dots_moved_pct": round(frac_moved_pct, 6),
                "min_interdot_nn_px": round(v.stats["min_nn_px"], 6),
            },
            "sgmc_control_proxy": {
                "evidence_label": "PROXY",
                "dti": round(float(sgmc_res["dti"]), 6),
                "delta_vs_r0": round(sgmc_delta, 6),
                "n_withheld_control_pixels": int(sgmc_off.sum()),
            },
            "parent_diff": {
                "removed": removed,
                "added": added,
                "shared": n0 - removed,
                "moved_pct": round(pct_changed, 6),
                "symmetric_diff_px": removed + added,
                "min_catalogue_distance_px": round(float(d_cat[mask].min()), 6),
                "dots_within_3px": int((d_cat[mask] <= 3.0).sum()),
            },
            "format_validation": {"nan": checks_nan, "zeros": checks_zero},
            "form_note": form_note,
            "gate_status": "PASS (local reread + gems.gates; candidate TIFF gitignored for public repo safety)",
            "seed": SEED,
            "git_sha_at_build": git_sha,
        }
        variants.append(record)
        new_cards[short_id] = {
            "parent": PARENT_ID,
            "axis": "SNAP",
            "value": val,
            "hypothesis": spec["hypothesis"],
            "mechanism": spec["mechanism"],
            "non_fault_mimic": spec["non_fault_mimic"],
            "predicted_sign_and_size": (
                f"{spec['pred']} vs R0, with scenario range {spec['pred_range']}; "
                "MODEL only, never a score."
            ),
            "falsifier": spec["falsifier"],
            "decision_rule": "Treat absolute live change <0.01 as no evidence; compare only human-provided receipt scores.",
        }
        print(
            f"BUILT {short_id}: dots={n0}, pct_changed={pct_changed:.2f}%, "
            f"mean_disp={mean_disp:.4f}px, min_nn={v.stats['min_nn_px']:.4f}px, "
            f"SGMC_PROXY_delta={sgmc_delta:+.6f}, sha256={sha_nan}"
        )

    # Update ledger/submissions.csv idempotently while preserving all prior session rows & columns
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    default_fields = [
        "id", "parent", "axis", "value", "n_dots", "pct_changed", "sha256",
        "status", "predicted_change", "file_zeros", "file_nan", "sha8",
        "change_desc", "receipt_score", "receipt_date", "notes",
    ]
    existing: list[dict[str, str]] = []
    fields = default_fields
    if LEDGER.is_file():
        with LEDGER.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing = list(reader)
            if reader.fieldnames:
                fields = list(reader.fieldnames)

    new_by_val = {rec["value"]: rec for rec in variants}
    retained: list[dict[str, str]] = []
    for row in existing:
        key = (row.get("parent", ""), row.get("axis", ""), row.get("value", ""))
        if key[0] == PARENT_ID and key[1] == "SNAP" and key[2] in new_by_val:
            expected_sha = new_by_val[key[2]]["sha256"]
            if row.get("sha256") != expected_sha:
                raise RuntimeError(f"Conflicting SHA for existing ledger cell {key}")
            continue
        retained.append(row)

    seen_pairs = {(r.get("parent", ""), r.get("axis", ""), r.get("value", "")) for r in retained}
    for rec in variants:
        triple = (rec["parent"], rec["axis"], rec["value"])
        if triple in seen_pairs:
            raise RuntimeError(f"Repeated (parent, axis, value) ledger pair: {triple}")

    with LEDGER.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in retained:
            writer.writerow({k: row.get(k, "") for k in fields})
        for rec in variants:
            writer.writerow({k: rec.get(k, "") for k in fields})

    # Merge mechanism cards JSON preserving earlier session cards
    merged_cards: dict[str, dict] = {}
    if CARDS_JSON.is_file():
        merged_cards = json.loads(CARDS_JSON.read_text(encoding="utf-8"))
        # Remove stale SNAP entries if rebuilding idempotently
        merged_cards = {
            k: v for k, v in merged_cards.items()
            if not (v.get("parent") == PARENT_ID and v.get("axis") == "SNAP" and v.get("value") in new_by_val)
        }
    merged_cards.update(new_cards)
    CARDS_JSON.write_text(json.dumps(merged_cards, indent=2) + "\n", encoding="utf-8")

    report = {
        "schema": "gemsdoe92.snap-variants.v1",
        "session_date_utc": DATE,
        "axis": "SNAP",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "exact_parent_rebuild": {
            "n_dots": n0,
            "zeros_sha256": parent["parent_hashes"]["zeros"],
            "nan_sha256": parent["parent_hashes"]["nan"],
            "matches_recorded_hashes": True,
        },
        "input_manifest_sha256": sha256_file(SESSION_MANIFEST),
        "input_count": len(inputs),
        "nodata_and_sign_handling": {
            "in_footprint_nodata_pixels_masked": int((foot & ~valid).sum()),
            "gravity_gradient_band": "Band 5 (iso_grav_anom_slope, unsigned ||grad g||)",
            "signed_band_18_excluded_reason": "Band 18 (iso_grav_anom_hg) is signed E-W derivative dg/dx (corr=0.9482 with gx), which asymmetrically penalizes east-dipping normal faults.",
        },
        "variants": variants,
        "scope_note": (
            "No submission, leaderboard, hidden labels, drivendata.org, or dropbox.com accessed. "
            "Candidate TIFFs are written locally to releases/ and gitignored per public-repo safeguard."
        ),
    }
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    RECEIPTS.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
