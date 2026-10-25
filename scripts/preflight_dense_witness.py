#!/usr/bin/env python3
"""Rejection-only, pre-placement universal-overlap gate for a pinned dense witness.

Exit 1 = literal registry duplicate/stop; 2 = invalid/inconclusive; never grants
eligibility. No predictions or dots are generated. Pin bytes AND match sample grid.
"""
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
# Same byte pin as registry/session_manifest.json, not merely a grid lookalike.
SAMPLE_SHA256 = '2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc'
WITNESS_SHA256 = 'ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be'
WITNESS_BLOB = '374c88b1da2b803e2ed160de467fd71ae114010d'
WITNESS_REL = 'docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif'


def universal_stop(footprint: np.ndarray, witness: np.ndarray) -> bool:
    """A witness positive everywhere within the footprint covers every valid dot."""
    if footprint.shape != witness.shape or not footprint.any():
        raise ValueError('shape mismatch or empty footprint')
    if not np.isfinite(witness[footprint]).all():
        raise ValueError('nonfinite witness inside footprint')
    return bool((witness[footprint] > 0).all())


def hashes(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    return (hashlib.sha256(data).hexdigest(),
            hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest())


def preflight(sample: Path, witness: Path) -> dict:
    sample_sha, _ = hashes(sample)
    if sample_sha != SAMPLE_SHA256:
        raise ValueError('sample SHA-256 mismatch; refusing an unpinned footprint')
    sha, blob = hashes(witness)
    if (sha, blob) != (WITNESS_SHA256, WITNESS_BLOB):
        raise ValueError('witness SHA-256 or Git blob mismatch')
    with rasterio.open(sample) as ref, rasterio.open(witness) as src:
        grid_ok = (src.count == ref.count == 1 and src.shape == ref.shape
                   and ref.crs is not None
                   and src.crs == ref.crs and src.transform == ref.transform)
        if not grid_ok:
            raise ValueError('witness is not aligned with sample template')
        footprint = np.isfinite(ref.read(1))
        a = src.read(1)
    covers = universal_stop(footprint, a)
    return {
        'schema': 'gemsdoe92-preplacement-stop-v2',
        'evidence_class': 'REGISTRY-MEASUREMENT',
        'reviewed_utc': datetime.now(timezone.utc).isoformat(),
        'sample_sha256': sample_sha,
        'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'Single pinned witness; rejection only. No candidate surface was generated or scored.',
        'witness_url': 'https://github.com/buffedlizard55-lab/17GEMSDOE/blob/6fc71d19d49dca4960d5434bd81b6dd06fcc030a/' + WITNESS_REL,
        'sha256': sha, 'git_blob_sha': blob,
        'grid_checks_pass': grid_ok, 'footprint_pixels': int(footprint.sum()),
        'positive_in_footprint': int(((a > 0) & footprint).sum()),
        'universal_nonempty_in_footprint_overlap_stop': covers,
        'forward_overlap_for_any_nonempty_in_footprint_dot_set': 1.0 if covers else None,
        'threshold': 0.70, 'verdict': 'negative', 'submission_eligible': False,
        'reason': ('Every nonempty candidate is a literal registry duplicate; stop before placement.'
                   if covers else 'No universal stop established; this check is not a clearance.'),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sample', type=Path, default=ROOT / 'data/bridge/sample_submission.tif')
    ap.add_argument('--witness', type=Path, required=True)
    ap.add_argument('--output', type=Path, default=ROOT / 'evidence/preplacement_dense_witness.json')
    args = ap.parse_args()
    try:
        # Preserve prior evidence; a failed run must not leave a stale PASS or
        # silently replace an older receipt under the same filename.
        if args.output.exists():
            raise ValueError('output already exists; choose a new receipt path')
        result = preflight(args.sample, args.witness)
        text = json.dumps(result, indent=2, allow_nan=False) + '\n'
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as out:
            out.write(text)
    except (OSError, ValueError, rasterio.errors.RasterioError) as exc:
        print(f'INCONCLUSIVE: {exc}', file=sys.stderr)
        return 2
    print(text, end='')
    return 1 if result['universal_nonempty_in_footprint_overlap_stop'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
