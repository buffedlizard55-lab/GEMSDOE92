#!/usr/bin/env python3
"""Recheck an existing BREAKLINE artifact against one public stop witness.

No new model, dots, surface, or holdout experiment. A single duplicate suffices
for rejection, but a passing witness never certifies uniqueness.
"""
import hashlib
import json
from pathlib import Path
import sys

import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'vendor')]
from gems57.grid import load_grid
from gems57.uniqueness import compare_array_to_registry
from scripts.audit_public_registry import gh_bytes, git_blob_sha


def main():
    cache = ROOT / '.cache/witness'
    cache.mkdir(parents=True, exist_ok=True)
    endpoint = 'repos/buffedlizard55-lab/17GEMSDOE/contents/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif'
    meta = json.loads(gh_bytes(endpoint))
    if meta['sha'] != '374c88b1da2b803e2ed160de467fd71ae114010d':
        raise ValueError('public witness changed; preserve old receipt and review new bytes')
    data = gh_bytes('-H', 'Accept: application/vnd.github.raw', meta['git_url'])
    if git_blob_sha(data) != meta['sha'] or len(data) != meta['size']:
        raise ValueError('public witness Git blob hash/size mismatch')
    witness = cache / 'full_surface.tif'
    witness.write_bytes(data)
    candidate = ROOT / 'docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif'
    with rasterio.open(candidate) as ds:
        a = ds.read(1)
    index = {'complete_accessible_scan': False, 'rasters': [
        {'repo_first': '17GEMSDOE', 'sources': ['17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif'],
         'cache_file': str(witness), 'sha256': hashlib.sha256(data).hexdigest()}]}
    grid = load_grid(ROOT / 'data/bridge')
    result = compare_array_to_registry(a, index, grid.footprint,
                                      file_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest())
    result.update(scope='Single public duplicate witness only; not full-registry clearance',
                  source_url=meta['html_url'], git_blob_sha=meta['sha'], bytes=meta['size'],
                  preplacement_surface='Not rerun; this is retrospective rejection of existing final dots',
                  new_experiments=0, weekly_slots_used=0)
    out = ROOT / 'evidence/breakline_public_witness.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    (ROOT / 'docs/downloads/breakline_public_witness.json').write_text(out.read_text())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
