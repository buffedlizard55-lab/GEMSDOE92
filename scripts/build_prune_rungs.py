#!/usr/bin/env python3
"""Reproducibly build three untried, fixed-mass PRUNE collar-rung candidates from R0.

This script reads only SHA-256-pinned inputs in registry/session_manifest.json. It
rebuilds R0 through the complete H19-5 -> D1.5 -> D2.8 -> SOLO -> R0 recipe,
requires both parent raster hashes to match exactly, then makes three constant-N
PRUNE variants (2.5, 3.5, and 4.5 px catalogue-collar radii) using deterministic
exact-marginal DTI-gain refill on the parent's H19-5 ridge support.

No labels, hidden regions, public/private test partitions, leaderboard, or
submission endpoints are accessed. Candidate TIFFs are deliberately kept out of
this public Git repository; run the script locally to regenerate them in
releases/ (which is gitignored). The ledger, receipts, and recipe are committed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))
from exact_dti_refill import dot_thin, select_exact_marginal_dti_add  # noqa: E402
from gems57 import metric  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA_ZEROS = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
PARENT_SHA_NAN = "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd"

MANIFEST = ROOT / "registry" / "session_manifest.json"
OUT_DIR = ROOT / "releases"
LEDGER = ROOT / "ledger" / "submissions.csv"
RECEIPTS = ROOT / "evidence" / "prune_rungs.json"
PARENT_SHA = {
    "zeros": PARENT_SHA_ZEROS,
    "nan": PARENT_SHA_NAN,
}
RUNG_PX = (2.5, 3.5, 4.5)
DATE = "20261023"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_inputs() -> dict[str, Path]:
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    resolved: dict[str, Path] = {}
    for item in doc["files"]:
        path = ROOT / item["local_path"]
        if not path.is_file():
            raise FileNotFoundError(f"Pinned input missing: {item['id']} at {path}; run scripts/restore_inputs.py")
        got_sha = sha256_file(path)
        got_bytes = path.stat().st_size
        if got_sha != item["sha256"] or got_bytes != item["bytes"]:
            raise RuntimeError(
                f"Pinned input mismatch {item['id']}: sha={got_sha}, bytes={got_bytes}; "
                f"expected sha={item['sha256']}, bytes={item['bytes']}"
            )
        resolved[item["id"]] = path
    return resolved


def percentile_rank(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    vals = np.asarray(a[valid], dtype=np.float32)
    vals = np.nan_to_num(vals, nan=0.0, posinf=0.0, neginf=0.0)
    knots = np.quantile(vals, np.linspace(0.0, 1.0, 1001))
    result = np.zeros(a.shape, dtype=np.float32)
    result[valid] = np.interp(vals, knots, np.linspace(0.0, 1.0, 1001)).astype(np.float32)
    return result


def build_parent(inputs: dict[str, Path]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict]:
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
    for name, rebuilt, ref in (("D1.5", d15, d15_ref), ("D2.8", d28, d28_ref),
                               ("SOLO-D2.8", solo, solo_ref), ("R0", r0, r0_ref)):
        if not np.array_equal(rebuilt, ref):
            raise RuntimeError(f"R0 lineage mask mismatch at {name}")

    profile = cat_profile.copy()
    profile.update(driver="GTiff", dtype="float32", count=1, compress="deflate",
                   predictor=3, zlevel=9, tiled=True, blockxsize=256,
                   blockysize=256, nodata=None)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    zeros = OUT_DIR / "_r0-rebuilt-zeros.tif"
    nan = OUT_DIR / "_r0-rebuilt-nan.tif"
    pz = profile.copy()
    with rasterio.open(zeros, "w", **pz) as ds:
        ds.write(np.where(foot, r0.astype(np.float32), 0.0).astype(np.float32), 1)
    pn = profile.copy()
    pn.update(nodata=np.nan)
    with rasterio.open(nan, "w", **pn) as ds:
        ds.write(np.where(foot, r0.astype(np.float32), np.nan).astype(np.float32), 1)
    hashes = {"zeros": sha256_file(zeros), "nan": sha256_file(nan)}
    zeros.unlink()
    nan.unlink()
    if hashes != PARENT_SHA:
        raise RuntimeError(f"Exact R0 output SHA mismatch: {hashes} != {PARENT_SHA}")
    return foot, cat, d_cat, h19, {"r0": r0, "profile": profile,
                                    "template_profile": template_profile,
                                    "parent_hashes": hashes}


def make_prior(inputs: dict[str, Path], foot: np.ndarray, h19: np.ndarray) -> np.ndarray:
    """Label-free ridge-correlated physical prior, built only from pinned bands."""
    with rasterio.open(inputs["training_features"]) as ds:
        tmi_hg = np.nan_to_num(ds.read(3), nan=0.0).astype(np.float32)
        grav_hg = np.nan_to_num(ds.read(18), nan=0.0).astype(np.float32)
        slope = np.nan_to_num(ds.read(19), nan=0.0).astype(np.float32)
    tmi = percentile_rank(tmi_hg, foot)
    grav = percentile_rank(grav_hg, foot)
    scarp = percentile_rank(slope, foot)
    phys = (0.40 * tmi + 0.35 * grav + 0.25 * scarp).astype(np.float32)
    # A conservative ridge-support mixture; the non-ridge background is not zero so
    # exact marginal DTI selection can still trade among all eligible H19 pixels.
    prior = np.where(h19, 0.30 + 0.70 * phys, 0.08 * phys).astype(np.float32)
    prior[~foot] = 0.0
    prior[~np.isfinite(prior)] = 0.0
    return prior


def write_tif(path: Path, profile: dict, foot: np.ndarray, mask: np.ndarray, nan_outside: bool) -> None:
    p = profile.copy()
    p.update(driver="GTiff", dtype="float32", count=1, compress="deflate",
             predictor=3, zlevel=9, tiled=True, blockxsize=256,
             blockysize=256, nodata=np.nan if nan_outside else None)
    outside = np.nan if nan_outside else 0.0
    arr = np.where(foot, mask.astype(np.float32), np.float32(outside)).astype(np.float32)
    with rasterio.open(path, "w", **p) as ds:
        ds.write(arr, 1)


def validate_reopened(path: Path, template_path: Path, mask: np.ndarray,
                      foot: np.ndarray, cat: np.ndarray, d_cat: np.ndarray,
                      expect_nan_outside: bool) -> dict:
    with rasterio.open(template_path) as ref, rasterio.open(path) as ds:
        a = ds.read(1)
        checks = {
            "crs_matches": ds.crs == ref.crs,
            "shape_matches": ds.shape == ref.shape,
            "transform_matches": ds.transform == ref.transform,
            "dtype_float32": ds.dtypes == ("float32",),
            "one_band": ds.count == 1,
            "inside_finite": bool(np.isfinite(a[foot]).all()),
            "outside_encoding": bool(np.isnan(a[~foot]).all()) if expect_nan_outside else bool(np.all(a[~foot] == 0)),
            "range_0_1": bool(np.all((a[foot] >= 0) & (a[foot] <= 1))),
            "binary_unit_mass": bool(np.array_equal(a[foot], mask[foot].astype(np.float32))),
            "zero_catalogue_mass": bool((a[cat] == 0).all()),
            # PRUNE is the sole brief-defined exception to the 3 px exclusion;
            # all rungs nevertheless preserve R0's stricter-than-2 px clearance.
            "catalogue_distance_gt_2px": bool(np.all(d_cat[mask] > 2.0)),
            "count_37654": int(np.count_nonzero(a[foot])) == 37654,
        }
    if not all(v for k, v in checks.items() if isinstance(v, bool)):
        raise RuntimeError(f"Re-read format gate failed for {path.name}: {checks}")
    return checks


def main() -> int:
    inputs = verify_inputs()
    foot, cat, d_cat, h19, parent = build_parent(inputs)
    r0 = parent["r0"]
    n0 = int(r0.sum())
    if n0 != 37654 or np.any(r0 & cat) or np.any(d_cat[r0] <= 2.0):
        raise RuntimeError("R0 parent invariants failed")
    prior = make_prior(inputs, foot, h19)
    with rasterio.open(inputs["sgmc_faults_control"]) as ds:
        sgmc_raw = (ds.read(1) > 0) & foot
    sgmc_off = sgmc_raw & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_reference = metric.dti_binary(r0, sgmc_off, valid=foot, known=cat)

    prediction_by_radius = {
        2.5: ("MODEL:+0.001", "[-0.010,+0.012]"),
        3.5: ("MODEL:+0.003", "[-0.008,+0.015]"),
        4.5: ("MODEL:-0.004", "[-0.018,+0.008]"),
    }
    mechanism_cards: dict[str, dict] = {}

    # The parent ranking recipe did not persist a complete pixel ranking. This axis
    # uses the registered, deterministic exact DTI-marginal mechanism on the same
    # H19-5 support for all refill candidates; candidate ranking is not a score.
    variants: list[dict] = []
    used_hashes = {PARENT_SHA_NAN, PARENT_SHA_ZEROS}
    reserved_values = {f"p{r:g}px-refill" for r in RUNG_PX}
    if LEDGER.is_file():
        with LEDGER.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("parent") == PARENT_ID and row.get("axis") == "PRUNE" and row.get("value") in reserved_values:
                    continue  # idempotent rebuild of the same exact experiment reservation
                for col in ("sha256", "sha256_zeros"):
                    if row.get(col):
                        used_hashes.add(row[col])
                # Earlier ledger schemas stored only one twin hash. Hash both
                # named files locally where available to prevent encoding twins
                # from escaping exact-hash dedupe.
                for col in ("file_nan", "file_zeros"):
                    file_value = row.get(col, "")
                    if file_value:
                        prior_path = ROOT / file_value
                        if prior_path.is_file():
                            used_hashes.add(sha256_file(prior_path))
    for radius in RUNG_PX:
        base = r0 & (d_cat > radius)
        n_remove = int(n0 - base.sum())
        if n_remove <= 0:
            raise RuntimeError(f"No R0 dots removed at {radius}px")
        pct_changed = 100.0 * n_remove / n0
        if not (1.0 <= pct_changed <= 50.0):
            raise RuntimeError(f"Changed fraction {pct_changed:.4f}% outside 1–50% at {radius}px")
        candidates = h19 & ~base & (d_cat > radius)
        if int(candidates.sum()) < n_remove:
            raise RuntimeError(f"Insufficient H19 refill candidates at {radius}px")
        mask = select_exact_marginal_dti_add(
            base_mask=base, cand_mask=candidates, w=prior, n_add=n_remove,
        )
        if int(mask.sum()) != n0 or np.any(mask & cat) or np.any(d_cat[mask] <= 2.0):
            raise RuntimeError(f"PRUNE invariants failed at {radius}px")
        removed = int(np.count_nonzero(r0 & ~mask))
        added = int(np.count_nonzero(mask & ~r0))
        if removed != added or removed != n_remove:
            raise RuntimeError(f"Parent-diff mismatch at {radius}px: removed={removed} added={added} expected={n_remove}")

        value = f"p{radius:g}px-refill"
        stem = f"h33-h33-2-b2-PRUNE{value}-{DATE}"
        tmp_nan = OUT_DIR / f"._building-{value}-nan.tif"
        tmp_zeros = OUT_DIR / f"._building-{value}-zeros.tif"
        write_tif(tmp_nan, parent["profile"], foot, mask, True)
        write_tif(tmp_zeros, parent["profile"], foot, mask, False)
        # Re-read both encodings before recording their checksums.
        checks_nan = validate_reopened(tmp_nan, inputs["sample_submission"], mask, foot, cat, d_cat, True)
        checks_zero = validate_reopened(tmp_zeros, inputs["sample_submission"], mask, foot, cat, d_cat, False)
        sha_nan, sha_zeros = sha256_file(tmp_nan), sha256_file(tmp_zeros)
        if sha_nan == sha_zeros or sha_nan in used_hashes or sha_zeros in used_hashes:
            raise RuntimeError(f"Exact duplicate SHA-256 at {value}")
        used_hashes.update((sha_nan, sha_zeros))
        # Brief naming convention: the NaN-outside primary is releases/<id>.tif;
        # the exactly equivalent fallback is releases/<id>-zeros.tif.
        short_id = f"h33-h33-2-b2-PRUNE{value}-{DATE}-{sha_nan[:8]}"
        nan_path = OUT_DIR / f"{short_id}.tif"
        zeros_path = OUT_DIR / f"{short_id}-zeros.tif"
        tmp_nan.replace(nan_path)
        tmp_zeros.replace(zeros_path)
        # Final named files are independently reopened after publication within the
        # local release folder; confirm byte identity with the pre-rename receipts.
        final_checks_nan = validate_reopened(nan_path, inputs["sample_submission"], mask, foot, cat, d_cat, True)
        final_checks_zero = validate_reopened(zeros_path, inputs["sample_submission"], mask, foot, cat, d_cat, False)
        if sha256_file(nan_path) != sha_nan or sha256_file(zeros_path) != sha_zeros:
            raise RuntimeError(f"Final-path re-read hash changed at {value}")
        checks_nan, checks_zero = final_checks_nan, final_checks_zero
        pred_text, pred_range = prediction_by_radius[radius]
        note = (f"h33-h33-2-b2; PRUNE collar {radius:g}px; fixed 37654; "
                f"remove/refill {n_remove} ({pct_changed:.2f}%); pred {pred_text}")
        if len(note) > 140:
            raise RuntimeError(f"Form note exceeds 140 chars ({len(note)})")
        record = {
            "id": short_id,
            "site": "GEMSDOE92",
            "name": nan_path.name,
            "file_zeros": str(zeros_path.relative_to(ROOT)),
            "file_nan": str(nan_path.relative_to(ROOT)),
            "sha8": sha_nan[:8],
            "change_desc": (f"remove all parent dots within {radius:g}px of catalogue; "
                            f"refill {n_remove} eligible H19-5 pixels by exact expected-DTI marginal gain"),
            "notes": (f"MODEL range {pred_range}; SGMC PROXY delta "
                      f"{metric.dti_binary(mask, sgmc_off, valid=foot, known=cat)['dti'] - sgmc_reference['dti']:+.6f}; "
                      "see evidence/prune_rungs.json for both encoding hashes and gate receipt"),
            "parent": PARENT_ID,
            "axis": "PRUNE",
            "value": value,
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
            "predicted_change": pred_text,
            "predicted_range": pred_range,
            "prediction_scope": "MODEL scenario range only; public-chunk changes under 0.01 are no evidence. PROXY instruments are diagnostics, never gates.",
            "sgmc_control_proxy": {
                "evidence_label": "PROXY",
                "dti": round(metric.dti_binary(mask, sgmc_off, valid=foot, known=cat)["dti"], 6),
                "delta_vs_r0": round(metric.dti_binary(mask, sgmc_off, valid=foot, known=cat)["dti"] - sgmc_reference["dti"], 6),
                "n_withheld_control_pixels": int(sgmc_off.sum()),
            },
            "parent_diff": {
                "removed": removed,
                "added": added,
                "shared": n0 - removed,
                "moved_pct": round(pct_changed, 6),
                "symmetric_diff_px": removed + added,
                "min_catalogue_distance_px": float(d_cat[mask].min()),
            },
            "format_validation": {"nan": checks_nan, "zeros": checks_zero},
            "form_note": note,
            "gate_status": "PASS (local reread; file not tracked in public Git repo)",
            "git_sha_at_build": __import__("subprocess").check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        }
        variants.append(record)
        mechanism_cards[short_id] = {
            "parent": PARENT_ID,
            "axis": "PRUNE",
            "value": value,
            "hypothesis": (
                f"At fixed mass, removing every R0 dot within {radius:g} pixels of the known-fault catalogue "
                "and reallocating that mass to eligible un-emitted H19-5 ridge pixels improves distance-tolerant "
                "fault detection if near-catalogue kernel overlap wastes precision on mapped traces."
            ),
            "mechanism": (
                "A triangular 300 m kernel gives less incremental credit when emitted mass lies close to already-known "
                "faults. Each replacement is selected by greedy exact marginal gain on the declared label-free prior; "
                "R0 count stays at 37,654. This is a controlled collar-radius change, not a mass change."
            ),
            "non_fault_mimic": (
                "Magnetic/gravity edges and H19-5 lineaments can trace lithologic contacts, caldera ring fractures, "
                "or erosional scarps rather than brittle faults."
            ),
            "predicted_sign_and_size": f"{pred_text} vs R0, with wide {pred_range} scenario range; MODEL only, not a score.",
            "falsifier": (
                "A receipt change <= -0.01 for the 2.5/3.5 px rungs, or >= +0.01 gain for the 4.5 px rung, "
                "would respectively reject a beneficial inner collar or reject the predicted outer-collar turnover."
            ),
            "decision_rule": "Treat absolute live change <0.01 as no evidence; compare only human-provided receipt scores.",
        }
        print(f"BUILT {short_id}: dots={n0}, moved={pct_changed:.2f}%, sha256={sha_nan}")

    # Preserve the established main-branch ledger schema and all older rows.
    # Do not manufacture historical receipt rows; the prompt's raw paste remains
    # separately recorded in ledger/raw_paste.txt and historical_climb.csv.
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    default_fields = ["id", "parent", "axis", "value", "n_dots", "pct_changed", "sha256",
                      "status", "predicted_change", "file_zeros", "file_nan", "sha8",
                      "change_desc", "receipt_score", "receipt_date", "notes"]
    existing: list[dict[str, str]] = []
    fields = default_fields
    if LEDGER.exists():
        with LEDGER.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing = list(reader)
            if reader.fieldnames:
                fields = list(reader.fieldnames)
    new_values = {rec["value"]: rec for rec in variants}
    retained: list[dict[str, str]] = []
    for row in existing:
        key = (row.get("parent", ""), row.get("axis", ""), row.get("value", ""))
        if key[0] == PARENT_ID and key[1] == "PRUNE" and key[2] in new_values:
            expected = new_values[key[2]]["sha256"]
            if row.get("sha256") != expected:
                raise RuntimeError(f"Existing (parent, axis, value) ledger pair has conflicting SHA: {key}")
            continue  # replace this exact experiment reservation idempotently
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

    report = {
        "schema": "gemsdoe92.prune-rungs.v1",
        "session_date_utc": DATE,
        "axis": "PRUNE",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "exact_parent_rebuild": {
            "n_dots": n0,
            "zeros_sha256": parent["parent_hashes"]["zeros"],
            "nan_sha256": parent["parent_hashes"]["nan"],
            "matches_recorded_hashes": True,
        },
        "input_manifest_sha256": sha256_file(MANIFEST),
        "input_count": len(inputs),
        "variants": variants,
        "scope_note": "No submission, leaderboard, hidden labels, or off-manifest data accessed. Both public-repository raster releases are generated locally and ignored by Git.",
    }
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    RECEIPTS.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    cards_path = ROOT / "ledger" / "mechanism_cards.json"
    cards_path.write_text(json.dumps(mechanism_cards, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
