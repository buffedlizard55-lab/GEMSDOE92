#!/usr/bin/env python3
"""Fail closed if a GitHub Pages download is missing, out of range, or mislabeled.

The primary is read from the landing page, and every served zeros-outside TIFF
is gated. Per-file expected dot counts are taken from adjacent audit receipts
when available; older fixed-budget descendants are still validated for format
and catalogue compliance. The primary audit SHA must match the served bytes.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from scipy.ndimage import distance_transform_edt  # noqa: E402

from gems.gates import run_gates, summarise  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57.validate import assert_submittable, validate  # noqa: E402

DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"
INDEX = DOCS / "index.html"
SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
LABELS = ROOT / "data" / "bridge" / "labels.tif"

def _receipt_dot_count(path: Path) -> int | None:
    """Read a dot-count assertion from the adjacent audit/run receipt if present."""
    stem = path.stem.removesuffix("-zeros")
    candidates = [path.with_name(stem + "-audit.json"), path.with_suffix(".json")]
    for receipt_path in candidates:
        if not receipt_path.is_file():
            continue
        try:
            doc = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(doc.get("n_positive_pixels"), int):
            return doc["n_positive_pixels"]
        nested = doc.get("validator_receipt")
        objects = [doc.get("raster"), doc.get("validator")]
        if isinstance(nested, dict):
            objects.append(nested.get("validator"))
        for obj in objects:
            if isinstance(obj, dict):
                n = obj.get("emitted_positive_pixels", obj.get("positive_pixels"))
                if isinstance(n, int):
                    return n
    return None


def main() -> int:
    problems: list[str] = []

    if not INDEX.is_file():
        print("FAIL: docs/index.html missing")
        return 2
    html = INDEX.read_text(encoding="utf-8")

    # ---- the page contract, written against properties not one lane's wording --
    for needle in ("OK TO DOWNLOAD", "NOT RECOMMENDED", "Predicted values must be in range [0, 1]",
                   "HOLDOUT-DTI", "unique-within-local-registry"):
        if needle not in html:
            problems.append(f"index.html missing {needle!r}")
    if not re.search(r"(weekly slot|3/week|weekly competition slot|human step)", html):
        problems.append("index.html carries no weekly-slot caution")
    if re.search(r'href="downloads/[^"]+-zeros\.tif"', html) is None:
        problems.append("index.html offers no zeros-outside download")
    # a HOLDOUT number must never be dressed as an organizer receipt
    if re.search(r"ORGANIZER-CONFIRMED[^<]{0,40}0\.00\d{4}", html):
        problems.append("holdout number labeled ORGANIZER-CONFIRMED")

    # ---- every served zeros-outside raster must be linked AND pass the gates ---
    served = sorted(DOWNLOADS.glob("*-zeros.tif"))
    if not served:
        problems.append("no zeros-outside rasters in docs/downloads")
    for path in served:
        if f"downloads/{path.name}" not in html:
            problems.append(f"{path.name} is served but not linked from index.html")

    with rasterio.open(SAMPLE) as ds:
        footprint = np.isfinite(ds.read(1))
    with rasterio.open(LABELS) as ds:
        cat = ds.read(1) > 0.5
    # Parent R0 is itself a registry raster and must be included in the literal gate.
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0 = ds.read(1) > 0
    r0_distance = distance_transform_edt(~r0)
    n_footprint = int(footprint.sum())
    r0_count = int((r0 & footprint).sum())

    for path in served:
        tag = path.name
        with rasterio.open(path) as ds:
            a = ds.read(1)
            if ds.dtypes[0] != "float32" or ds.count != 1:
                problems.append(f"{tag}: dtype/band")
            if not np.isfinite(a).all():
                problems.append(f"{tag}: NaN/inf present (portal [0,1] risk)")
            if a.min() < 0 or a.max() > 1:
                problems.append(f"{tag}: values [{a.min()}, {a.max()}]")
            if np.any((a > 0) & ~footprint):
                problems.append(f"{tag}: mass outside footprint")
            if np.any(a[cat] > 0):
                problems.append(f"{tag}: mass on catalogue")
            candidate_mask = (a > 0) & footprint
            actual_dots = int(candidate_mask.sum())
            expected_dots = _receipt_dot_count(path)
            if expected_dots is not None and actual_dots != expected_dots:
                problems.append(f"{tag}: n_dots {actual_dots} != receipt {expected_dots}")
            elif actual_dots == 0:
                problems.append(f"{tag}: raster contains no positive predictions")

            overlap_fraction = float(np.count_nonzero(candidate_mask & (r0_distance <= 3))) / actual_dots
            p = actual_dots / n_footprint
            q = r0_count / n_footprint
            joint = int((candidate_mask & r0).sum()) / n_footprint
            denom = np.sqrt(p * (1.0 - p) * q * (1.0 - q))
            # For binary masks, Spearman with average ranks equals binary Pearson.
            rho = (joint - p * q) / denom if denom > 0 else 0.0
            print(f"  REGISTRY R0 {tag}: rho={rho:.4f}; {overlap_fraction:.2%} within 3 px")
            if (rho > 0.90 or overlap_fraction > 0.70) and "duplicate" not in html.lower():
                problems.append(f"{tag}: registry threshold exceeded; page must disclose duplicate stop")
            if "OK TO DOWNLOAD AND SUBMIT" in html:
                problems.append("index.html conflates format-valid download with submission clearance")

        try:
            assert_submittable(validate(path, footprint, cat))
        except AssertionError as exc:
            problems.append(f"{tag}: {exc}")

        ok, report = summarise(run_gates(str(path), str(SAMPLE), str(LABELS),
                                         prune_radius=2))
        if not ok:
            problems.append(f"{tag}: gates failed\n{report}")
        else:
            print(f"  PASS {tag}  sha256 {sha256_file(path)[:16]}…")

    # ---- the primary named on the page must match its audit receipt ----------
    m = re.search(r'href="(downloads/[^"]+-zeros\.tif)"', html)
    if m:
        primary = DOCS / m.group(1)
        if not primary.is_file():
            problems.append(f"index.html points at {m.group(1)}, which does not exist")
        else:
            variant = primary.stem.removesuffix("-zeros")
            audit_path = primary.with_name(variant + "-audit.json")
            if not audit_path.is_file():
                problems.append(f"no audit receipt beside the primary: {audit_path.name}")
            else:
                doc = json.loads(audit_path.read_text())
                if doc.get("overall_pass") is not True:
                    problems.append("audit receipt does not record overall_pass == true")
                if doc.get("sha256_zeros") != sha256_file(primary):
                    problems.append("audit receipt sha256 != primary bytes on disk")
                uniqueness = doc.get("uniqueness", {})
                if uniqueness and uniqueness.get("unique_within_scope") is not True:
                    problems.append("primary audit does not pass its stated local uniqueness scan")
                if "NOT RECOMMENDED" not in html and "NOT a weekly slot" not in html:
                    problems.append("primary page does not disclose slot recommendation")
                bad = [g["name"] for g in doc.get("gates_zeros", []) if not g["ok"]]
                if bad:
                    problems.append(f"audit receipt records failing gates: {bad}")
            print(f"  PRIMARY {primary.name}")

            # The competition accepts a ZIP only when it contains one GeoTIFF;
            # verify the actual linked archive and its payload bytes.
            for zip_match in re.finditer(r'href="(downloads/[^\"]+\.zip)"', html):
                zip_path = DOCS / zip_match.group(1)
                if not zip_path.is_file():
                    problems.append(f"linked ZIP is missing: {zip_path.name}")
                    continue
                try:
                    with zipfile.ZipFile(zip_path) as archive:
                        tiff_members = [n for n in archive.namelist()
                                        if n.lower().endswith((".tif", ".tiff"))]
                        if len(tiff_members) != 1:
                            problems.append(f"{zip_path.name}: expected one TIFF, found {len(tiff_members)}")
                        elif sha256_file(primary) != hashlib.sha256(archive.read(tiff_members[0])).hexdigest():
                            problems.append(f"{zip_path.name}: TIFF payload differs from primary download")
                except (OSError, zipfile.BadZipFile) as exc:
                    problems.append(f"{zip_path.name}: invalid ZIP ({exc})")

    if problems:
        print("SITE CHECK FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print(f"SITE CHECK PASS ({len(served)} served raster(s) gated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
