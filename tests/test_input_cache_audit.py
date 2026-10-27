"""Hash/grid input auditing is local and cannot grant submission permission."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from scripts import audit_input_cache as audit


def entry(data=b'known bytes'):
    return {'id': 'feature', 'local_path': '.cache/gems_inputs/feature.tif',
            'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
            'source_url': 'https://github.com/owner/repo'}


def test_input_missing_then_pinned_and_corrupted(tmp_path):
    e = entry()
    assert not audit.inspect_entry(tmp_path, e)['verified']
    p = tmp_path / e['local_path']
    p.parent.mkdir(parents=True)
    p.write_bytes(b'known bytes')
    ok = audit.inspect_entry(tmp_path, e)
    assert ok['verified'] and ok['size_match'] and ok['sha256_match']
    p.write_bytes(b'other bytes')  # same length, different content
    bad = audit.inspect_entry(tmp_path, e)
    assert bad['size_match'] and not bad['sha256_match'] and not bad['verified']


@pytest.mark.parametrize('path', ['../../outside.tif', '.cache/gems_inputs/../../outside.tif', '/tmp/outside.tif'])
def test_manifest_path_must_not_escape_cache(tmp_path, path):
    with pytest.raises(ValueError, match='escapes'):
        audit.inspect_entry(tmp_path, {**entry(), 'local_path': path})


def test_symlink_cannot_escape_cache(tmp_path):
    outside = tmp_path / 'outside.tif'
    outside.write_bytes(b'known bytes')
    link = tmp_path / '.cache/gems_inputs/feature.tif'
    link.parent.mkdir(parents=True)
    link.symlink_to(outside)
    with pytest.raises(ValueError, match='escapes'):
        audit.inspect_entry(tmp_path, entry())


@pytest.mark.parametrize('field,value', [('sha256', ''), ('sha256', 'A' * 64),
                                         ('bytes', 0), ('bytes', True), ('id', '')])
def test_malformed_pins_fail_closed(tmp_path, field, value):
    with pytest.raises(ValueError):
        audit.inspect_entry(tmp_path, {**entry(), field: value})


def test_missing_required_files_never_pass_audit(tmp_path):
    entries = [{**entry(), 'id': name, 'local_path': f'.cache/gems_inputs/{name}.tif'}
               for name in ('sample_submission', 'existing_faults', 'training_features')]
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({'files': entries}))
    result = audit.audit(tmp_path, manifest)
    assert result['files_verified'] == 0
    assert not result['all_local_checks_passed'] and not result['raster_metadata']['checked']
    assert not result['official_origin_authenticated']
    assert not result['redistribution_rights_verified']
    assert not result['submission_eligible']


def test_cli_cannot_overwrite_historical_receipt(tmp_path, monkeypatch, capsys):
    output = tmp_path / 'old.json'
    output.write_text('prior evidence')
    monkeypatch.setattr(audit, 'audit', lambda: pytest.fail('audit should not run'))
    assert audit.main(['--output', str(output)]) == 2
    assert output.read_text() == 'prior evidence'
    assert 'DO NOT SUBMIT' in capsys.readouterr().err


def make_raster(path: Path, count=1, names=None, transform=None):
    with rasterio.open(path, 'w', driver='GTiff', height=3, width=4,
                       count=count, dtype='float32', crs='EPSG:32611',
                       transform=transform or from_origin(1000, 2000, 100, 100)) as dst:
        dst.write(np.ones((count, 3, 4), dtype='float32'))
        for band, name in enumerate(names or [], 1):
            dst.update_tags(band, band_name=name)


def test_metadata_checks_grid_and_each_feature_tag(tmp_path, monkeypatch):
    cache = tmp_path / '.cache/gems_inputs'
    cache.mkdir(parents=True)
    files = {'sample_submission': cache / 'sample.tif',
             'existing_faults': cache / 'faults.tif',
             'training_features': cache / 'features.tif'}
    make_raster(files['sample_submission'])
    make_raster(files['existing_faults'])
    make_raster(files['training_features'], count=2, names=['mag', 'gravity'])
    monkeypatch.setattr(audit, 'EXPECTED_TRAINING_BAND_TAGS', {1: 'mag', 2: 'gravity'})
    manifest = tmp_path / 'manifest.json'

    def pin_files():
        rows = [{'id': name, 'local_path': str(path.relative_to(tmp_path)),
                 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                 'bytes': path.stat().st_size} for name, path in files.items()]
        manifest.write_text(json.dumps({'files': rows}))

    pin_files()
    result = audit.audit(tmp_path, manifest)
    meta = result['raster_metadata']
    assert result['all_local_checks_passed'] and meta['grid_matches_sample']
    assert meta['expected_band_tags_match'] and meta['sample_footprint_nonempty']

    # Even a pinned-but-bad file must fail independent metadata checks.
    make_raster(files['training_features'], count=2, names=['mag', 'WRONG'],
                transform=from_origin(1100, 2000, 100, 100))
    pin_files()
    result = audit.audit(tmp_path, manifest)
    meta = result['raster_metadata']
    assert result['all_pins_verified'] and not result['all_local_checks_passed']
    assert not meta['grid_matches_sample'] and not meta['expected_band_tags_match']
    assert meta['problems']
