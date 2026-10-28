#!/usr/bin/env python3
"""Check a rejection-only publication; never infer clearance from a static card."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.render_safe_site import render
from gems.gates import run_gates
from gems.rasters import sha256_file

def check():
    errors = []
    for path, expected in render().items():
        if not path.is_file() or path.read_text(encoding='utf-8') != expected:
            errors.append(f'stale or unsafe page: {path.relative_to(ROOT)}')
    card = json.loads((ROOT/'docs/downloads/review_8857_run_card.json').read_text())
    tif = ROOT/'docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif'
    if card['historical_raster_sha256'] != sha256_file(tif):
        errors.append('historical raster hash mismatch')
    if not all(g.ok for g in run_gates(str(tif), str(ROOT/'data/bridge/sample_submission.tif'), str(ROOT/'data/bridge/labels.tif'), prune_radius=2, require_submission_encoding=True)):
        errors.append('historical TIFF format validation failed')
    if card.get('verdict') != 'negative' or card.get('submission_eligible') is not False or card.get('new_raster_sha256') is not None:
        errors.append('rejection semantics invalid')
    return errors

def main():
    try:
        errors = check()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors = [str(exc)]
    if errors:
        print('SITE CHECK FAIL\n'+'\n'.join(errors)); return 1
    print('SITE CHECK PASS: rejection-only site; historical TIFF format checked; no submission clearance')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
