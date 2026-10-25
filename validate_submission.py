#!/usr/bin/env python3
"""Run format-only checks; this does NOT establish submission eligibility.

The shared validator checks CRS, shape, transform, dtype, range, catalogue mass,
and zeros-outside encoding. It does not run the public registry uniqueness scan or
holdout promotion gate. Under the current literal registry protocol every nonempty
in-footprint raster hits the pinned full-footprint witness; do not submit a file.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
DEFAULT_CANDIDATE = ROOT / "docs/downloads/h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif"
SHARED_VALIDATOR = ROOT / "scripts/validate_submission.py"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="GeoTIFF path(s) to check (format only)")
    parser.add_argument("--candidate", action="append", default=[], help="GeoTIFF path to check (repeatable)")
    args = parser.parse_args(argv)
    paths = [Path(p) for p in (*args.candidate, *args.paths)] or [DEFAULT_CANDIDATE]

    env = os.environ.copy()
    vendor = str(ROOT / "vendor")
    env["PYTHONPATH"] = vendor + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    command = [sys.executable, str(SHARED_VALIDATOR)]
    command.extend(str(p if p.is_absolute() else (Path.cwd() / p).resolve()) for p in paths)
    result = subprocess.run(command, cwd=ROOT, env=env, check=False)
    if result.returncode:
        return result.returncode

    print("\nFORMAT VALIDATION PASSED. This is not a uniqueness or submission-clearance result.")
    print("The binding literal registry witness gives overlap 1.000 > 0.70 for any nonempty in-footprint raster.")
    print("DO NOT SUBMIT or spend a weekly slot under the current protocol.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
