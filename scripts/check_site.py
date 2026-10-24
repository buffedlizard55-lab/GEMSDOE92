#!/usr/bin/env python3
"""Fail closed if the GitHub Pages download is missing, out of range, or mislabeled."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402

from gems.gates import run_gates, summarise  # noqa: E402
from gems57.validate import assert_submittable, validate  # noqa: E402

DOCS = ROOT / "docs"
DOWNLOAD = DOCS / "downloads" / "h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.tif"
INDEX = DOCS / "index.html"
SUBMIT = DOCS / "submit.html"
SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
LABELS = ROOT / "data" / "bridge" / "labels.tif"
EXPECTED_SHA = "0ca8248acace558f5cf86b153134b8fd5cc2b7d5b343d0a36f000f9fbfe4758f"


def main() -> int:
    problems = []
    if not DOWNLOAD.is_file():
        print("FAIL: download GeoTIFF missing:", DOWNLOAD)
        return 2
    html = INDEX.read_text(encoding="utf-8")
    sub = SUBMIT.read_text(encoding="utf-8")
    for needle in (
        "downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.tif",
        "OK TO DOWNLOAD",
        "NOT recommended for a weekly competition slot",
        "Predicted values must be in range [0, 1]",
        EXPECTED_SHA,
        "h33-h33-2-b2; TIPGAP FAR 33% along-strike",
    ):
        if needle not in html:
            problems.append(f"index.html missing {needle!r}")
    if "How to make a competition submission" not in sub:
        problems.append("submit.html missing executive heading")
    # Must not present HOLDOUT as an organizer score.
    if re.search(r"ORGANIZER-CONFIRMED[^<]{0,40}0\\.002723", html):
        problems.append("holdout number labeled ORGANIZER-CONFIRMED")

    from gems.rasters import sha256_file
    sha = sha256_file(DOWNLOAD)
    if sha != EXPECTED_SHA:
        problems.append(f"download sha256 {sha} != {EXPECTED_SHA}")

    with rasterio.open(SAMPLE) as ds:
        footprint = np.isfinite(ds.read(1))
    with rasterio.open(LABELS) as ds:
        cat = ds.read(1) > 0.5
    with rasterio.open(DOWNLOAD) as ds:
        a = ds.read(1)
        if ds.dtypes[0] != "float32" or ds.count != 1:
            problems.append("dtype/band")
        if not np.isfinite(a).all():
            problems.append("NaN/inf in download (portal [0,1] risk)")
        if a.min() < 0 or a.max() > 1:
            problems.append(f"values [{a.min()}, {a.max()}]")
        if np.any((a > 0) & ~footprint):
            problems.append("mass outside footprint")
        if np.any(a[cat] > 0):
            problems.append("mass on catalogue")
        if int((a > 0).sum()) != 37654:
            problems.append(f"n_dots {(a>0).sum()}")

    receipt = validate(DOWNLOAD, footprint, cat)
    try:
        assert_submittable(receipt)
    except AssertionError as exc:
        problems.append(str(exc))
    ok, report = summarise(run_gates(str(DOWNLOAD), str(SAMPLE), str(LABELS), prune_radius=2))
    if not ok:
        problems.append(report)

    if problems:
        print("SITE CHECK FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print("SITE CHECK PASS")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
