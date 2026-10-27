#!/usr/bin/env python3
"""Verify cached owner-mirrored inputs without training or generating a raster.

A successful local pin/grid audit is NOT proof of official origin, redistribution
rights, holdout validity, or permission to submit. The ignored cache is ephemeral.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gems.riedelvent import EXPECTED_TRAINING_BAND_TAGS  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_entry(root: Path, entry: dict) -> dict:
    """Check a manifest row without trusting its path, size or digest fields."""
    if not isinstance(entry, dict):
        raise ValueError('manifest file entry must be an object')
    name, relative, expected, size = (entry.get(k) for k in ('id', 'local_path', 'sha256', 'bytes'))
    if not isinstance(name, str) or not name or not isinstance(relative, str) or not relative:
        raise ValueError('entry needs a nonempty id and local_path')
    if (not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected)
            or type(size) is not int or size <= 0):
        raise ValueError(f'{name}: invalid SHA-256 or size pin')
    cache = (root / '.cache/gems_inputs').resolve()
    target = (root / relative).resolve()
    if not target.is_relative_to(cache) or target == cache:
        raise ValueError(f'{name}: input path escapes ignored cache')
    result = {'id': name, 'path': relative, 'expected_sha256': expected,
              'expected_bytes': size, 'source_url': entry.get('source_url'),
              'present': target.is_file(), 'size_match': False,
              'sha256_match': False, 'observed_sha256': None, 'verified': False}
    if result['present']:
        result['size_match'] = target.stat().st_size == size
        # Hash even on size mismatch so a corrupt file is distinguishable.
        result['observed_sha256'] = sha256_file(target)
        result['sha256_match'] = result['observed_sha256'] == expected
        result['verified'] = bool(result['size_match'] and result['sha256_match'])
    return result


def audit(root: Path = ROOT, manifest_path: Path | None = None) -> dict:
    root = Path(root).resolve()
    manifest_path = Path(manifest_path or root / 'registry/session_manifest.json')
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    entries = manifest.get('files')
    if not isinstance(entries, list) or not entries:
        raise ValueError('manifest must contain a nonempty file list')
    rows = [inspect_entry(root, item) for item in entries]
    by_id = {r['id']: r for r in rows}
    if len(by_id) != len(rows):
        raise ValueError('manifest contains duplicate input ids')
    required = ('sample_submission', 'existing_faults', 'training_features')
    if any(name not in by_id for name in required):
        raise ValueError('manifest is missing a required grid or feature input')
    metadata = {'checked': False, 'grid_matches_sample': None,
                'expected_band_tags_match': None, 'problems': []}
    if all(by_id[name]['verified'] for name in required):
        sample = root / by_id['sample_submission']['path']
        faults = root / by_id['existing_faults']['path']
        features = root / by_id['training_features']['path']
        with rasterio.open(sample) as ref, rasterio.open(faults) as cat, rasterio.open(features) as src:
            expected_grid = (ref.shape, ref.crs, ref.transform)
            grids_match = (ref.count == 1 and ref.crs is not None and cat.count == 1
                           and (cat.shape, cat.crs, cat.transform) == expected_grid
                           and (src.shape, src.crs, src.transform) == expected_grid)
            tags = {i: src.tags(i).get('band_name') for i in src.indexes}
            tags_match = src.count == len(EXPECTED_TRAINING_BAND_TAGS) and tags == EXPECTED_TRAINING_BAND_TAGS
            nonempty_footprint = bool(np.isfinite(ref.read(1)).any())
            if not grids_match:
                metadata['problems'].append('sample, catalogue and feature grid/bands do not align')
            if not tags_match:
                metadata['problems'].append('feature band-name tags do not match the checked-in tag map')
            if not nonempty_footprint:
                metadata['problems'].append('sample footprint is empty')
            if any(dtype != 'float32' for dtype in src.dtypes):
                metadata['problems'].append('feature stack contains a non-float32 band')
            metadata.update(checked=True, grid_matches_sample=bool(grids_match),
                            expected_band_tags_match=bool(tags_match),
                            sample_footprint_nonempty=nonempty_footprint,
                            feature_band_count=src.count, feature_dtypes=list(src.dtypes),
                            feature_band_names={str(k): v for k, v in tags.items()},
                            crs=str(ref.crs), shape=list(ref.shape),
                            transform=list(ref.transform)[:6])
    else:
        metadata['problems'].append('one or more required inputs are missing or failed pins')
    all_pins = all(r['verified'] for r in rows)
    return {
        'schema': 'gemsdoe92-owner-mirror-input-audit-v1',
        'reviewed_utc': datetime.now(timezone.utc).isoformat(),
        'manifest_sha256': hashlib.sha256(raw).hexdigest(),
        'source_class': 'owner-maintained GitHub mirrors; organizer provenance unverified',
        'cache_policy': 'ignored and snapshot-excluded; restore again in a new workspace',
        'files_expected': len(rows), 'files_verified': sum(r['verified'] for r in rows),
        'all_pins_verified': all_pins, 'files': rows, 'raster_metadata': metadata,
        'all_local_checks_passed': bool(all_pins and metadata['checked'] and not metadata['problems']),
        'official_origin_authenticated': False,
        'redistribution_rights_verified': False,
        'training_run': False, 'holdout_run': False, 'submission_eligible': False,
        'limitations': ['Pins establish identity with the owner mirror, not official origin or permission.',
                        'Band names are owner-mirror metadata checked against the repository tag map.',
                        'The experimental lane is blocked by the literal registry witness.'],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New receipt path; existing evidence is never overwritten')
    args = parser.parse_args(argv)
    try:
        if args.output is not None and args.output.exists():
            raise ValueError('output already exists; choose a new receipt path')
        result = audit()
        text = json.dumps(result, indent=2, allow_nan=False) + '\n'
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('x', encoding='utf-8') as output:
                output.write(text)
        print(text, end='')
        return 0 if result['all_local_checks_passed'] else 1
    except (OSError, ValueError, KeyError, TypeError, rasterio.errors.RasterioError) as exc:
        print(f'INPUT AUDIT INCONCLUSIVE — DO NOT SUBMIT: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
