#!/usr/bin/env python3
"""Validate candidate GeoTIFF submission file(s) against the bridged grid & catalogue.

Shared tool fix (2026-10-24 APRONRIDGE session, Protocol Rule 2):
Previously ignored ``sys.argv`` / ``--candidate`` and checked ``releases/*.tif`` only,
allowing ``--candidate /nonexistent.tif`` to exit 0 silently. Now parses ``--candidate``
(repeatable) and positional paths, fails closed if any requested file is missing or
invalid, enforces all-finite ``[0, 1]`` outside the footprint on ``*-zeros.tif`` files,
and defaults (when called with no arguments) to checking both ``releases/*.tif`` and
``docs/downloads/*.tif``.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np
import rasterio

ROOT = pathlib.Path(__file__).resolve().parents[1]
SAMPLE_PATH = ROOT / "data/bridge/sample_submission.tif"
LABELS_PATH = ROOT / "data/bridge/labels.tif"


def load_reference():
    with rasterio.open(SAMPLE_PATH) as ds:
        sample_data = ds.read(1)
        footprint = np.isfinite(sample_data)
        transform = ds.transform
        crs = ds.crs
        shape = (ds.height, ds.width)
    with rasterio.open(LABELS_PATH) as ds:
        labels = ds.read(1) > 0.5
    return footprint, labels, crs, shape, transform


def check_file(path: pathlib.Path, footprint, labels, crs, shape, transform) -> bool:
    path = pathlib.Path(path)
    print(f"\nChecking {path}")
    if not path.is_file():
        print(f"  FAIL: candidate file does not exist: {path}")
        return False
    with rasterio.open(path) as ds:
        data = ds.read(1)
        if ds.crs != crs:
            print(f"  FAIL: CRS mismatch {ds.crs} vs {crs}")
            return False
        if (ds.height, ds.width) != shape:
            print(f"  FAIL: shape mismatch {(ds.height, ds.width)} vs {shape}")
            return False
        if ds.transform != transform:
            print(f"  FAIL: transform mismatch {ds.transform} vs {transform}")
            return False
        if ds.dtypes[0] != "float32":
            print(f"  FAIL: dtype {ds.dtypes[0]} != float32")
            return False
        if ds.count != 1:
            print(f"  FAIL: band count {ds.count} != 1")
            return False

        finite = np.isfinite(data)
        inside = footprint
        outside = ~footprint
        if not np.all(finite[inside]):
            print("  FAIL: NaN/Inf inside footprint")
            return False
        if not np.all((data[inside] >= 0.0) & (data[inside] <= 1.0)):
            print("  FAIL: values outside [0,1] inside footprint")
            return False
        if np.any(data[labels] > 0.0):
            print(f"  FAIL: non-zero mass on catalogue: {float(data[labels].sum())} pixels")
            return False

        n_outside_finite = int(finite[outside].sum())
        n_outside_nan = int(np.isnan(data[outside]).sum())
        if path.name.endswith("-zeros.tif"):
            if ds.nodata is not None:
                print(f"  FAIL: zeros-outside submission has nodata={ds.nodata!r} (must be None)")
                return False
            if n_outside_nan != 0 or not np.all(data[outside] == 0.0):
                print("  FAIL: zeros-outside submission has non-zero or NaN cells outside footprint")
                return False

        print(
            f"  OK: shape {data.shape}, finite inside {int(finite[inside].sum())}/{int(inside.sum())}, "
            f"outside finite {n_outside_finite}, outside NaN {n_outside_nan}, "
            f"n_dots {int((np.nan_to_num(data, nan=0.0) > 0.5).sum())}"
        )
        return True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate", action="append", default=[], help="Candidate GeoTIFF path to validate")
    ap.add_argument("paths", nargs="*", help="Optional positional GeoTIFF path(s)")
    args = ap.parse_args(argv)

    explicit = [pathlib.Path(p) for p in (args.candidate + args.paths)]
    if explicit:
        targets = explicit
    else:
        targets = sorted((ROOT / "releases").glob("*.tif")) + sorted(
            (ROOT / "docs/downloads").glob("*.tif")
        )
        if not targets:
            print("FAIL: no GeoTIFFs found to validate")
            return 1

    footprint, labels, crs, shape, transform = load_reference()
    ok = True
    for p in targets:
        if not check_file(p, footprint, labels, crs, shape, transform):
            ok = False

    if ok:
        print(f"\nAll format checks PASS ({len(targets)} file(s))")
        return 0
    print("\nSome checks FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
