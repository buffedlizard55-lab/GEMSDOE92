#!/usr/bin/env python3
"""Fail closed if the GitHub Pages download is missing, out of range, or mislabeled.

Rewritten 2026-10-25 when the DILATATION lane merged with the TIPGAP lane. The
previous version hard-coded one lane's filename, sha256 and form note, so it
broke the moment the primary changed -- and it only ever checked that one file
even when several were being served. This version derives the primary from the
page itself and gates **every** served zeros-outside raster, so an orphaned or
out-of-range download cannot ship unnoticed.
"""
from __future__ import annotations

import json
import re
import sys
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
N_DOTS = 37654


def main() -> int:
    problems: list[str] = []

    if not INDEX.is_file():
        print("FAIL: docs/index.html missing")
        return 2
    html = INDEX.read_text(encoding="utf-8")

    # ---- the page contract, written against properties not one lane's wording --
    for needle in ("OK TO DOWNLOAD", "Predicted values must be in range [0, 1]",
                   "HOLDOUT-DTI"):
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
    # The literal lane-drift gate compares the complete candidate against each
    # available registry raster. R0 is pinned locally and must not be ignored
    # merely because a candidate shares its parentage.
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0 = ds.read(1) > 0
    r0_distance = distance_transform_edt(~r0)

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
            n_candidate = int((a > 0).sum())
            if n_candidate != N_DOTS:
                problems.append(f"{tag}: n_dots {n_candidate} != {N_DOTS}")
            candidate_mask = a > 0
            overlap_fraction = (float(np.count_nonzero(candidate_mask & (r0_distance <= 3))) / n_candidate
                               if n_candidate else 0.0)
            # For binary rasters, Spearman's rho with average tie ranks equals
            # the Pearson correlation of the two binary indicator arrays.
            rho = float(np.corrcoef(candidate_mask.ravel(), r0.ravel())[0, 1]) if n_candidate else 0.0
            print(f"  REGISTRY R0 {tag}: rho={rho:.4f}; {overlap_fraction:.2%} of dots within 3 px")
            if (rho > 0.90 or overlap_fraction > 0.70) and ("NOT CLEARED" not in html or "duplicate" not in html.lower()):
                problems.append(f"{tag}: registry gate failed (rho={rho:.4f}, overlap={overlap_fraction:.2%}); page must disclose duplicate stop")
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
                bad = [g["name"] for g in doc.get("gates_zeros", []) if not g["ok"]]
                if bad:
                    problems.append(f"audit receipt records failing gates: {bad}")
            print(f"  PRIMARY {primary.name}")

    if problems:
        print("SITE CHECK FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print(f"SITE CHECK PASS ({len(served)} served raster(s) gated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
