#!/usr/bin/env python3
"""Rejection-only entry point using the shared strict validator.

A format pass is not upload clearance. The literal universal registry stop is
binding; exit 1 means DO NOT SUBMIT even when all format checks pass. No exception
is converted into success. No score or organizer-acceptance forecast is made.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

import rasterio
from gems.gates import run_gates, summarise
from scripts.check_site import primary_download

ROOT = Path(__file__).resolve().parent


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', nargs='?', type=Path)
    args = parser.parse_args(argv)
    try:
        candidate = args.candidate
        if candidate is None:
            problems = []
            rel = primary_download((ROOT / 'docs/index.html').read_text(), problems)
            if problems or rel is None:
                raise ValueError('; '.join(problems))
            candidate = ROOT / 'docs' / rel
        results = run_gates(
            str(candidate), str(ROOT / 'data/bridge/sample_submission.tif'),
            str(ROOT / 'data/bridge/labels.tif'), prune_radius=2,
            require_submission_encoding=True,
        )
        ok, report = summarise(results)
        print(report)
        print('FORMAT PASS (local only)' if ok else 'FORMAT FAIL')
        print('DO NOT SUBMIT: literal registry stop; no weekly-slot clearance.')
        return 1
    except (OSError, ValueError, rasterio.errors.RasterioError) as exc:
        print(f'INCONCLUSIVE / DO NOT SUBMIT: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
