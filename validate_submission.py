#!/usr/bin/env python3
"""Run local GeoTIFF format/range preflight; never grant upload eligibility.

A successful local preflight means only that the supplied file matches the
known template grid and local [0, 1]/footprint conventions. It does not test
registry uniqueness, holdout promotion, organizer acceptance, or a weekly-slot
selector. Under the repository's current binding literal-registry rule, files
are research-only and MUST NOT be submitted.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "vendor"), str(ROOT)]

from gems57.validate import validate  # noqa: E402

DEFAULT_FILE = Path(
    "docs/downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif"
)
SAMPLE = ROOT / "data/bridge/sample_submission.tif"
CATALOGUE = ROOT / "data/bridge/existing_faults.tif"


def run_preflight(candidate: Path) -> tuple[bool, dict]:
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    if not SAMPLE.is_file() or not CATALOGUE.is_file():
        raise FileNotFoundError("local sample_submission/existing_faults bridge rasters are missing")

    with rasterio.open(SAMPLE) as ds:
        reference = ds.read(1)
        footprint = np.isfinite(reference)
    with rasterio.open(CATALOGUE) as ds:
        catalogue = ds.read(1) > 0.5
    return True, validate(candidate, footprint=footprint, catalogue=catalogue)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", default=str(DEFAULT_FILE), help="GeoTIFF to format-check")
    args = parser.parse_args(argv)
    candidate = Path(args.file)
    try:
        _, receipt = run_preflight(candidate)
    except (OSError, ValueError) as exc:
        print(f"FORMAT PREFLIGHT FAIL: {exc}")
        return 2

    print(f"File: {candidate}")
    print(f"SHA-256: {receipt['sha256']}")
    for name, ok in receipt["checks"].items():
        print(f"{'PASS' if ok else 'FAIL'} {name}")
    print(f"Overall local format/range preflight: {'PASS' if receipt['all_checks_passed'] else 'FAIL'}")
    print("Submission eligibility: NOT CLEARED by this validator")
    print("Current project decision: DO NOT SUBMIT; research download only")
    print("This tool does not evaluate registry uniqueness, holdout promotion, organizer acceptance, or slot selection.")
    return 0 if receipt["all_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
