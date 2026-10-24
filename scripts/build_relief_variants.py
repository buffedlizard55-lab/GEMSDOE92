#!/usr/bin/env python3
"""Reproducibly build three controlled, constant-mass RELIEF variants of R0.

Strict compliance with Agent Brief v2:
- Verifies SHA-256 and byte length of all pinned inputs in registry/session_manifest.json
  (and registry/data_manifest.json when data/ is present) before reading any raster.
- Rebuilds parent R0 (h33-h33-2-b2) through its exact H19-5 -> D1.5 -> D2.8 -> SOLO -> R0
  lineage and requires BOTH zeros and NaN SHA-256 digests to match byte-for-byte.
- Builds 3 variants on AXIS=RELIEF that differ ONLY in the destination structural-relief
  tercile (computed strictly from the detrended-elevation bands Band 12 det_elev and
  Band 19 det_elev_slope, with zero non-relief geophysics bands):
    1. basin11pct      : shift 11.00% (4,142 dots) from Piedmont + Range-front -> Basin
    2. piedmont11pct   : shift 11.00% (4,142 dots) from Basin + Range-front -> Piedmont
    3. rangefront11pct : shift 11.00% (4,142 dots) from Basin + Piedmont -> Range-front
- Uses exact marginal expected-DTI removal (select_exact_marginal_dti_drop) in the two
  source terciles and spaced exact marginal expected-DTI addition
  (select_exact_marginal_dti_add_spaced, min_nn >= sqrt(2) px = D1.5 spacing) on H19-5
  corridors in the destination tercile.
- Holds dot count (37,654) and total mass (37,654.0) fixed; emits zero mass on catalogue
  pixels; keeps 100% of newly added dots > 3.0 px from the catalogue (preserving R0's
  > 2.0 px clearance on surviving inherited dots without PRUNE confounding).
- Writes releases/<id>.tif (NaN outside) and releases/<id>-zeros.tif (zeros outside),
  re-reads both from disk, runs all MUST-pass format gates, and records parent-diff
  and tercile statistics in ledger/submissions.csv and evidence/relief_variants.json.
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
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from exact_dti_refill import (  # noqa: E402
    dot_thin,
    select_exact_marginal_dti_add_spaced,
    select_exact_marginal_dti_drop,
)
from gems.gates import run_gates, summarise  # noqa: E402
from gems.variants import compute_relief_terciles  # noqa: E402
from gems57 import metric  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA_ZEROS = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
PARENT_SHA_NAN = "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd"
PARENT_SHA = {"zeros": PARENT_SHA_ZEROS, "nan": PARENT_SHA_NAN}

SESSION_MANIFEST = ROOT / "registry" / "session_manifest.json"
DATA_MANIFEST = ROOT / "registry" / "data_manifest.json"
OUT_DIR = ROOT / "releases"
LEDGER = ROOT / "ledger" / "submissions.csv"
RECEIPTS = ROOT / "evidence" / "relief_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"

DATE = "20261024"
SEED = 0  # Deterministic row-major tie-breaking; zero stochastic draws.
SHIFT_FRAC = 0.11  # 11.000159% (4,142 / 37,654 dots), strictly inside Brief §5's 10-15%.
MIN_ADD_NN_PX = math.sqrt(2.0)  # D1.5 non-cardinal spacing floor (1.4142 px).
ADDED_MIN_CAT_PX = 3.0  # Brief §4.4: all newly placed dots clear catalogue by > 3.0 px.


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


def build_and_verify_parent(
    inputs: dict[str, Path],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict]:
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
    tmp_zeros = OUT_DIR / "._r0-relief-check-zeros.tif"
    tmp_nan = OUT_DIR / "._r0-relief-check-nan.tif"
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


def _pct_rank_within(a: np.ndarray, mask: np.ndarray) -> np.ndarray:
    vals = np.asarray(a[mask], dtype=np.float32)
    knots = np.quantile(vals, np.linspace(0.0, 1.0, 1001))
    return np.interp(vals, knots, np.linspace(0.0, 1.0, 1001)).astype(np.float32)


def build_relief_surfaces(
    inputs: dict[str, Path], foot: np.ndarray, h19: np.ndarray, d_cat: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Construct equal-area relief terciles and within-tercile H19-5 relief corridor weight.

    Uses ONLY the two topographic detrended-elevation bands in training_features.tif:
    - Band 12 (det_elev): regional structural-relief terciles (0=Basin, 1=Piedmont, 2=Range-front)
    - Band 19 (det_elev_slope) + ||grad(Band 19)||: within-tercile scarp prominence & slope break
    Masks float32 sentinel -3.4028235e+38 (3,061 in-footprint pixels).
    """
    with rasterio.open(inputs["training_features"]) as ds:
        names = {i + 1: (ds.tags(i + 1).get("band_name") or "") for i in range(ds.count)}
        if names.get(12) != "det_elev" or names.get(19) != "det_elev_slope":
            raise RuntimeError(f"Unexpected topographic band tags: {names}")
        det_elev = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        det_slope = ds.read(19, masked=True).filled(np.nan).astype(np.float32)

    valid = (
        foot
        & np.isfinite(det_elev)
        & np.isfinite(det_slope)
        & (det_elev > -1e30)
        & (det_slope > -1e30)
    )
    terciles, (q33, q67) = compute_relief_terciles(det_elev, valid=valid)

    sy, sx = np.gradient(np.where(valid, det_slope, np.nan), 100.0)
    slope_break = np.hypot(sx, sy).astype(np.float32)
    valid_brk = valid & np.isfinite(slope_break)

    p_slp = np.zeros(foot.shape, dtype=np.float32)
    p_brk = np.zeros(foot.shape, dtype=np.float32)
    for t in (0, 1, 2):
        mt = valid & (terciles == t)
        p_slp[mt] = _pct_rank_within(det_slope, mt)
        p_brk[mt] = p_slp[mt]
        mtb = valid_brk & (terciles == t)
        if np.any(mtb):
            p_brk[mtb] = _pct_rank_within(slope_break, mtb)

    w_relief = np.where(
        h19 & valid & (d_cat > 2.0),
        0.50 + 0.25 * p_slp + 0.25 * p_brk,
        0.0,
    ).astype(np.float32)

    meta = {
        "det_elev_band": "Band 12 (det_elev)",
        "det_elev_slope_band": "Band 19 (det_elev_slope) + ||grad(Band 19)||",
        "tercile_cutpoints_m": {"q33_basin_piedmont": round(q33, 4), "q67_piedmont_rangefront": round(q67, 4)},
        "in_footprint_nodata_pixels_masked": int((foot & ~valid).sum()),
        "valid_footprint_pixels": int(valid.sum()),
        "footprint_tercile_pixels": {
            "0_basin": int((terciles == 0).sum()),
            "1_piedmont": int((terciles == 1).sum()),
            "2_range_front": int((terciles == 2).sum()),
        },
    }
    return valid, terciles, w_relief, meta


def write_tif(
    path: Path, profile: dict, foot: np.ndarray, mask: np.ndarray, nan_outside: bool
) -> None:
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
    added_mask: np.ndarray,
    foot: np.ndarray,
    cat: np.ndarray,
    d_cat: np.ndarray,
    expect_nan_outside: bool,
    r0_within_3px: int,
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
            "added_dots_catalogue_distance_gt_3px": bool(
                np.all(d_cat[added_mask] > ADDED_MIN_CAT_PX)
            ),
            "in_collar_3px_le_parent": int((d_cat[mask] <= 3.0).sum()) <= r0_within_3px,
            "count_37654": int(np.count_nonzero(a[foot])) == 37654,
        }
    # Run gems/gates.py both with strict default (verifying only inherited <=3px collar remains)
    # and with R0's >2px clearance declared.
    strict_res = run_gates(path, template_path, catalogue_path=catalogue_path)
    strict_failed = [r.name for r in strict_res if not r.ok]
    checks["gems_strict_non_collar_gates_pass"] = set(strict_failed) <= {"distance_from_catalogue"}
    r0_res = run_gates(path, template_path, catalogue_path=catalogue_path, prune_radius=2)
    gems_ok, gems_report = summarise(r0_res)
    checks["gems_gates_pass"] = bool(gems_ok)
    if not all(v for v in checks.values() if isinstance(v, bool)):
        raise RuntimeError(f"Re-read format gate failed for {path.name}: {checks}\n{gems_report}")
    return checks


def tercile_summary(mask: np.ndarray, terciles: np.ndarray) -> dict[str, dict[str, float | int]]:
    total = int(mask.sum())
    labels = {0: "basin", 1: "piedmont", 2: "range_front", -1: "sentinel_nodata"}
    out: dict[str, dict[str, float | int]] = {}
    for code, name in labels.items():
        cnt = int((mask & (terciles == code)).sum())
        out[name] = {
            "n_dots": cnt,
            "pct_of_total": round(100.0 * cnt / total, 4) if total else 0.0,
        }
    return out


def main() -> int:
    inputs = verify_all_manifests()
    foot, cat, d_cat, h19, parent = build_and_verify_parent(inputs)
    r0 = parent["r0"]
    n0 = int(r0.sum())
    r0_within_3px = int((d_cat[r0] <= 3.0).sum())
    if n0 != 37654 or np.any(r0 & cat) or np.any(d_cat[r0] <= 2.0):
        raise RuntimeError("R0 parent invariants failed")

    valid, terciles, w_relief, relief_meta = build_relief_surfaces(inputs, foot, h19, d_cat)
    n_shift = int(round(SHIFT_FRAC * n0))
    pct_shift_exact = 100.0 * n_shift / n0
    if not (10.0 <= pct_shift_exact <= 15.0):
        raise RuntimeError(f"n_shift={n_shift} ({pct_shift_exact:.4f}%) outside 10-15%")

    with rasterio.open(inputs["sgmc_faults_control"]) as ds:
        sgmc_raw = (ds.read(1) > 0) & foot
    sgmc_off = sgmc_raw & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_reference = metric.dti_binary(r0, sgmc_off, valid=foot, known=cat)

    specs = [
        {
            "value": "basin11pct",
            "dst": 0,
            "srcs": (1, 2),
            "pred": "MODEL:+0.008",
            "pred_range": "[-0.008,+0.022]",
            "short_change": "RELIEF +11% mass to Basin (4142 dots, fixed 37654)",
            "hypothesis": (
                "R0 allocates only 20.43% (7,692) of its dots to the Basin tercile (det_elev <= "
                "-142.91 m) despite Basins occupying 33.33% of the footprint and hosting 30.28% "
                "of known USGS/INGENIOUS faults, because H19-5's topographic-slope weighting "
                "over-allocated dots to steep range-front cliffs (37.72%). Shifting 11.00% of "
                "mass (4,142 unit-mass dots) out of Piedmont + Range-front onto Basin H19-5 "
                "corridors raises Basin share to 31.43% and densifies coverage over concealed "
                "intrabasinal horst-graben and accommodation faults beneath Quaternary valley fill."
            ),
            "mechanism": (
                "At fixed S=37,654, removing 4,142 lowest-marginal-DTI dots proportionally from "
                "Piedmont and Range-front cuts false-positive mass on unfaulted upland cliffs "
                "while coarsening redundant interior chain dots, and adding 4,142 spaced "
                "(min_nn >= 1.414 px, d_cat > 3.0 px) H19-5 dots in Basin raises triangular-kernel "
                "TP_w from ~0.65 toward ~0.90 along concealed intrabasinal corridors."
            ),
            "non_fault_mimic": (
                "Pluvial Pleistocene lake shorelines (Lahontan/Bonneville), axial fluvial terrace "
                "edges, buried paleochannels, and flat-lying intrabasinal basalt flows/sills beneath "
                "playa fill that generate H19-5 lineaments and subtle basin slope breaks without "
                "brittle faulting."
            ),
            "falsifier": (
                "A live receipt delta <= -0.01 vs R0 falsifies concealed-basin fault enrichment "
                "and demonstrates that unmapped test faults are concentrated on piedmont aprons or "
                "exposed range blocks rather than beneath Quaternary valley fill; |delta| < 0.01 "
                "is no evidence."
            ),
        },
        {
            "value": "piedmont11pct",
            "dst": 1,
            "srcs": (0, 2),
            "pred": "MODEL:+0.005",
            "pred_range": "[-0.009,+0.018]",
            "short_change": "RELIEF +11% mass to Piedmont (4142 dots, fixed 37654)",
            "hypothesis": (
                "Active Quaternary Basin-and-Range master normal faults, synthetic bajada "
                "step-faults, and Faulds-type relay ramps peak in the Piedmont tercile "
                "(-142.91 m < det_elev <= +38.75 m, hosting 40.45% of known catalogue faults). "
                "Shifting 11.00% of mass (4,142 unit-mass dots) out of Basin + Range-front into "
                "Piedmont (raising Piedmont share from 41.81% to 52.81%) concentrates kernel "
                "coverage on piedmont fault aprons while shedding both upland volcanic-cliff "
                "false positives and deep-basin potential-field ambiguity."
            ),
            "mechanism": (
                "Holds dot count (37,654), total mass (37,654.0), H19-5 support, and d_cat > 3.0 px "
                "addition clearance identical to basin11pct, changing ONLY the target detrended-"
                "elevation tercile to Piedmont (Tercile 1). Exact marginal-DTI infill (D2.8 -> D1.5 "
                "on strongest piedmont scarp/break H19-5 corridors) increases TP_w along semi-"
                "concealed fan-head and bajada fault traces."
            ),
            "non_fault_mimic": (
                "Incised alluvial-fan channel margins, non-tectonic bajada coalescent toes, "
                "pediment-alluvium erosional contacts, and highstand pluvial beach ridges along "
                "intermediate valley margins."
            ),
            "falsifier": (
                "A live receipt delta <= -0.01 vs R0 falsifies piedmont fault enrichment over R0's "
                "existing 41.81% allocation and indicates expert-mapped new faults lie either "
                "deeper in concealed playas (tested by basin11pct) or higher in bedrock ranges "
                "(tested by rangefront11pct)."
            ),
        },
        {
            "value": "rangefront11pct",
            "dst": 2,
            "srcs": (0, 1),
            "pred": "MODEL:-0.005",
            "pred_range": "[-0.018,+0.010]",
            "short_change": "RELIEF +11% mass to Range-front (4142 dots, fixed 37654)",
            "hypothesis": (
                "Mechanistic bedrock-exposure control. If expert-identified new faults derive "
                "predominantly from lidar, aerial-photo, and 1:24k bedrock compilation in uplifted "
                "ranges where Holocene sediment does not conceal traces (analogous to USGS SGMC, "
                "where 63.61% of off-catalogue bedrock faults sit in Tercile 2), shifting 11.00% "
                "of mass into Range-front (det_elev > +38.75 m, 37.72% -> 48.72%) will raise live "
                "DTI. Under our primary concealed/piedmont fault hypothesis, adding upland mass "
                "instead amplifies false positives on unfaulted volcanic cliff ledges."
            ),
            "mechanism": (
                "Holds dot count (37,654), total mass (37,654.0), H19-5 support, and d_cat > 3.0 px "
                "addition clearance identical to basin11pct and piedmont11pct, changing ONLY the "
                "target detrended-elevation tercile to Range-front (Tercile 2). Completes the "
                "symmetric 3-domain relief simplex so two live receipts uniquely resolve the "
                "geomorphic distribution of unmapped faults."
            ),
            "non_fault_mimic": (
                "Resistant Cenozoic ash-flow tuff cooling-unit cliffs, caldera ring-fracture walls, "
                "glacially/fluvially steepened ridge crests, and unfaulted Mesozoic plutonic "
                "contacts at shallow aeromagnetic terrain clearance."
            ),
            "falsifier": (
                "A live receipt gain >= +0.01 over both R0 and basin11pct falsifies our upland "
                "volcanic-cliff false-positive model and proves unmapped test faults are "
                "dominated by exposed bedrock range-block splays."
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
                    and row.get("axis") == "RELIEF"
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
    r0_terc_summary = tercile_summary(r0, terciles)
    variants: list[dict] = []
    new_cards: dict[str, dict] = {}

    for spec in specs:
        val = spec["value"]
        dst = int(spec["dst"])
        s0, s1 = spec["srcs"]

        m_s0 = r0 & valid & (terciles == s0)
        m_s1 = r0 & valid & (terciles == s1)
        n_s0, n_s1 = int(m_s0.sum()), int(m_s1.sum())
        k0 = int(round(n_shift * n_s0 / (n_s0 + n_s1)))
        k1 = n_shift - k0

        after_drop0 = select_exact_marginal_dti_drop(
            base_mask=r0, removable_mask=m_s0, w=w_relief, n_drop=k0
        )
        base_kept = select_exact_marginal_dti_drop(
            base_mask=after_drop0, removable_mask=m_s1, w=w_relief, n_drop=k1
        )
        if int(base_kept.sum()) != n0 - n_shift:
            raise RuntimeError(f"Unexpected post-drop dot count at {val}: {int(base_kept.sum())}")

        cand_dst = (
            h19
            & ~base_kept
            & valid
            & (terciles == dst)
            & (d_cat > ADDED_MIN_CAT_PX)
        )
        mask = select_exact_marginal_dti_add_spaced(
            base_mask=base_kept,
            cand_mask=cand_dst,
            w=w_relief,
            n_add=n_shift,
            min_nn=MIN_ADD_NN_PX,
        )

        removed_mask = r0 & ~mask
        added_mask = mask & ~r0
        removed = int(removed_mask.sum())
        added = int(added_mask.sum())
        if int(mask.sum()) != n0 or removed != n_shift or added != n_shift:
            raise RuntimeError(
                f"RELIEF count/diff invariant failed at {val}: total={int(mask.sum())}, "
                f"removed={removed}, added={added}, expected_shift={n_shift}"
            )
        if np.any(mask & cat) or np.any(d_cat[mask] <= 2.0):
            raise RuntimeError(f"Catalogue exclusion failed at {val}")
        if np.any(d_cat[added_mask] <= ADDED_MIN_CAT_PX):
            raise RuntimeError(f"Added dot breached 3.0 px catalogue clearance at {val}")

        oy, ox = np.nonzero(mask)
        nn_all = cKDTree(np.c_[oy, ox]).query(np.c_[oy, ox], k=2)[0][:, 1]
        min_nn_obs = float(nn_all.min())
        if min_nn_obs < MIN_ADD_NN_PX - 1e-6:
            raise RuntimeError(f"Minimum inter-dot spacing violated at {val}: {min_nn_obs:.4f}")

        pct_changed = 100.0 * removed / n0
        if not (1.0 <= pct_changed <= 50.0):
            raise RuntimeError(f"pct_changed={pct_changed:.4f}% outside 1-50% at {val}")

        tmp_nan = OUT_DIR / f"._building-RELIEF-{val}-nan.tif"
        tmp_zeros = OUT_DIR / f"._building-RELIEF-{val}-zeros.tif"
        write_tif(tmp_nan, parent["profile"], foot, mask, True)
        write_tif(tmp_zeros, parent["profile"], foot, mask, False)

        validate_reopened(
            tmp_nan, inputs["sample_submission"], inputs["existing_faults"],
            mask, added_mask, foot, cat, d_cat, True, r0_within_3px,
        )
        validate_reopened(
            tmp_zeros, inputs["sample_submission"], inputs["existing_faults"],
            mask, added_mask, foot, cat, d_cat, False, r0_within_3px,
        )
        sha_nan = sha256_file(tmp_nan)
        sha_zeros = sha256_file(tmp_zeros)
        if sha_nan == sha_zeros or sha_nan in used_hashes or sha_zeros in used_hashes:
            tmp_nan.unlink(missing_ok=True)
            tmp_zeros.unlink(missing_ok=True)
            raise RuntimeError(f"Duplicate SHA-256 detected for RELIEF {val}")
        used_hashes.update((sha_nan, sha_zeros))

        short_id = f"{PARENT_ID}-RELIEF{val}-{DATE}-{sha_nan[:8]}"
        nan_path = OUT_DIR / f"{short_id}.tif"
        zeros_path = OUT_DIR / f"{short_id}-zeros.tif"
        tmp_nan.replace(nan_path)
        tmp_zeros.replace(zeros_path)

        checks_nan = validate_reopened(
            nan_path, inputs["sample_submission"], inputs["existing_faults"],
            mask, added_mask, foot, cat, d_cat, True, r0_within_3px,
        )
        checks_zero = validate_reopened(
            zeros_path, inputs["sample_submission"], inputs["existing_faults"],
            mask, added_mask, foot, cat, d_cat, False, r0_within_3px,
        )
        if sha256_file(nan_path) != sha_nan or sha256_file(zeros_path) != sha_zeros:
            raise RuntimeError(f"Post-rename disk reread SHA-256 mismatch at {val}")

        form_note = f"{PARENT_ID}; {spec['short_change']}; pred {spec['pred']}"
        if len(form_note) > 140:
            raise RuntimeError(f"Form note exceeds 140 chars ({len(form_note)}): {form_note}")

        sgmc_res = metric.dti_binary(mask, sgmc_off, valid=foot, known=cat)
        sgmc_delta = float(sgmc_res["dti"] - sgmc_reference["dti"])
        terc_after = tercile_summary(mask, terciles)

        record = {
            "id": short_id,
            "site": "GEMSDOE92",
            "name": nan_path.name,
            "file_zeros": str(zeros_path.relative_to(ROOT)),
            "file_nan": str(nan_path.relative_to(ROOT)),
            "sha8": sha_nan[:8],
            "change_desc": (
                f"{spec['short_change']}; drop {k0}+{k1} from terciles {s0},{s1} and add "
                f"{added} H19-5 (d_cat>3, nn>=1.41) in tercile {dst}"
            ),
            "notes": (
                f"seed={SEED}; moved={removed} ({pct_changed:.4f}%); min_nn={min_nn_obs:.4f}px; "
                f"added_min_dcat={float(d_cat[added_mask].min()):.4f}px; "
                f"MODEL range {spec['pred_range']}; SGMC PROXY delta {sgmc_delta:+.6f}; "
                f"git={git_sha[:12]}; see evidence/relief_variants.json"
            ),
            "parent": PARENT_ID,
            "axis": "RELIEF",
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
            "tercile_allocation": {
                "destination_tercile": dst,
                "source_terciles": [s0, s1],
                "dropped_by_source_tercile": {str(s0): k0, str(s1): k1},
                "before": r0_terc_summary,
                "after": terc_after,
            },
            "spacing_and_clearance": {
                "min_interdot_nn_px": round(min_nn_obs, 6),
                "median_interdot_nn_px": round(float(np.median(nn_all)), 6),
                "added_min_catalogue_distance_px": round(float(d_cat[added_mask].min()), 6),
                "all_min_catalogue_distance_px": round(float(d_cat[mask].min()), 6),
                "inherited_dots_within_3px": int((d_cat[mask] <= 3.0).sum()),
                "added_dots_within_3px": int((d_cat[added_mask] <= 3.0).sum()),
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
            "gate_status": (
                "PASS (local reread + gems.gates; 0 added dots <=3px of catalogue; "
                "candidate TIFF gitignored for public repo safety)"
            ),
            "seed": SEED,
            "git_sha_at_build": git_sha,
        }
        variants.append(record)
        new_cards[short_id] = {
            "parent": PARENT_ID,
            "axis": "RELIEF",
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
            f"BUILT {short_id}: dots={n0}, pct_changed={pct_changed:.4f}%, "
            f"min_nn={min_nn_obs:.4f}px, added_min_dcat={float(d_cat[added_mask].min()):.3f}px, "
            f"SGMC_PROXY_delta={sgmc_delta:+.6f}, sha256={sha_nan}"
        )

    # Idempotently update ledger/submissions.csv while preserving all prior rows & columns
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
        if key[0] == PARENT_ID and key[1] == "RELIEF" and key[2] in new_by_val:
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

    # Merge mechanism cards JSON preserving all earlier session cards
    merged_cards: dict[str, dict] = {}
    if CARDS_JSON.is_file():
        merged_cards = json.loads(CARDS_JSON.read_text(encoding="utf-8"))
        merged_cards = {
            k: v
            for k, v in merged_cards.items()
            if not (
                v.get("parent") == PARENT_ID
                and v.get("axis") == "RELIEF"
                and v.get("value") in new_by_val
            )
        }
    merged_cards.update(new_cards)
    CARDS_JSON.write_text(json.dumps(merged_cards, indent=2) + "\n", encoding="utf-8")

    report = {
        "schema": "gemsdoe92.relief-variants.v1",
        "session_date_utc": DATE,
        "axis": "RELIEF",
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
        "relief_definition": relief_meta,
        "parent_tercile_allocation": r0_terc_summary,
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
