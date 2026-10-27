#!/usr/bin/env python3
"""Characterize the pinned registry witness; never create a candidate or clearance."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.audit_readiness import DEFAULT_WITNESS  # noqa: E402
from scripts.preflight_dense_witness import preflight  # noqa: E402


def describe_support(footprint: np.ndarray, values: np.ndarray) -> dict:
    if (footprint.shape != values.shape or footprint.dtype != np.bool_
            or not footprint.any() or not np.isfinite(values[footprint]).all()):
        raise ValueError('invalid, empty, or non-finite footprint')
    inside = values[footprint]
    return {
        'finite_footprint_pixels': int(inside.size),
        'positive_footprint_pixels': int((inside > 0).sum()),
        'minimum': float(inside.min()),
        'maximum': float(inside.max()),
        'distinct_values': int(np.unique(inside).size),
        'binary_zero_or_one_pixels': int(((inside == 0) | (inside == 1)).sum()),
    }


def inspect(sample: Path, witness: Path) -> dict:
    proof = preflight(sample, witness)  # verifies both hash pins and alignment
    if proof['universal_nonempty_in_footprint_overlap_stop'] is not True:
        raise ValueError('this rejection-only audit does not establish full positive support')
    with rasterio.open(sample) as ref, rasterio.open(witness) as src:
        footprint = np.isfinite(ref.read(1))
        if not np.array_equal(footprint, ref.read_masks(1) > 0):
            raise ValueError('sample finite footprint and GDAL validity mask disagree')
        if not (src.read_masks(1)[footprint] > 0).all():
            raise ValueError('witness has masked pixels inside sample footprint')
        stats = describe_support(footprint, src.read(1))
    return {
        'schema': 'gemsdoe92-witness-support-v1',
        'evidence_class': 'REGISTRY-MEASUREMENT (one witness, rejection only)',
        'observed_utc': datetime.now(timezone.utc).isoformat(),
        'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'sample_sha256': proof['sample_sha256'],
        'witness_sha256': proof['sha256'],
        'witness_url': proof['witness_url'],
        'statistics': stats,
        'interpretation': ('If each positive continuous-probability pixel is a dot, every nonempty '
                           'in-footprint dot set overlaps the witness at 1.0. The instruction does '
                           'not resolve whether continuous values are intended as dots. This is a '
                           'fail-closed representation stop, not proof of geological identity.'),
        'new_candidate': False, 'experiments': 0, 'submission_eligible': False,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sample', type=Path, default=ROOT / 'data/bridge/sample_submission.tif')
    p.add_argument('--witness', type=Path, default=DEFAULT_WITNESS)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(argv)
    try:
        if args.output.exists():
            raise ValueError('receipt already exists')
        result = inspect(args.sample, args.witness)
        content = json.dumps(result, indent=2, allow_nan=False) + '\n'
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as f:
            f.write(content)
    except (OSError, ValueError, rasterio.errors.RasterioError) as exc:
        print(f'INCONCLUSIVE — DO NOT SUBMIT: {exc}', file=sys.stderr)
        return 2
    print(f"Witness support characterized; no candidate or clearance: {args.output}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
