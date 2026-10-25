import importlib.util
from pathlib import Path

import numpy as np
import pytest

spec = importlib.util.spec_from_file_location(
    'preflight', Path(__file__).resolve().parents[1] / 'scripts/preflight_dense_witness.py')
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


def test_universal_stop_all_footprint():
    footprint = np.array([[False, True, True], [True, False, True]])
    witness = np.array([[0, 0.1, 1], [0.01, 0, 0.7]])
    assert preflight.universal_stop(footprint, witness)
    witness[1, 0] = 0
    assert not preflight.universal_stop(footprint, witness)


def test_reject_invalid_witness():
    footprint = np.ones((2, 2), bool)
    with pytest.raises(ValueError):
        preflight.universal_stop(footprint, np.ones((2, 3)))
    with pytest.raises(ValueError):
        preflight.universal_stop(footprint, np.array([[1., np.nan], [1., 1.]]))
    with pytest.raises(ValueError):
        preflight.universal_stop(np.zeros((2, 2), bool), np.ones((2, 2)))


def write_tif(path, data, *, crs='EPSG:32611', transform=None):
    import rasterio
    from rasterio.transform import from_origin
    with rasterio.open(path, 'w', driver='GTiff', height=data.shape[0],
                       width=data.shape[1], count=1, dtype='float32', crs=crs,
                       transform=transform or from_origin(243350, 4508550, 100, 100)) as ds:
        ds.write(data.astype('float32'), 1)


@pytest.fixture
def pinned_pair(tmp_path, monkeypatch):
    sample, witness = tmp_path / 'sample.tif', tmp_path / 'witness.tif'
    write_tif(sample, np.array([[np.nan, 0.0], [0.0, 0.0]]))
    write_tif(witness, np.ones((2, 2)))
    monkeypatch.setattr(preflight, 'SAMPLE_SHA256', preflight.hashes(sample)[0])
    sha, blob = preflight.hashes(witness)
    monkeypatch.setattr(preflight, 'WITNESS_SHA256', sha)
    monkeypatch.setattr(preflight, 'WITNESS_BLOB', blob)
    return sample, witness


def test_preflight_pins_sample_and_preserves_rejection_scope(pinned_pair):
    result = preflight.preflight(*pinned_pair)
    assert result['schema'].endswith('v2')
    assert result['sample_sha256'] == preflight.hashes(pinned_pair[0])[0]
    assert result['reviewed_utc']
    assert len(result['implementation_sha256']) == 64
    assert result['footprint_pixels'] == 3
    assert result['forward_overlap_for_any_nonempty_in_footprint_dot_set'] == 1
    assert result['submission_eligible'] is False
    assert 'Single pinned witness' in result['scope']


def test_reject_same_grid_but_changed_footprint(pinned_pair):
    sample, witness = pinned_pair
    write_tif(sample, np.zeros((2, 2)))
    with pytest.raises(ValueError, match='sample SHA-256 mismatch'):
        preflight.preflight(sample, witness)


def test_reject_changed_witness(pinned_pair):
    sample, witness = pinned_pair
    write_tif(witness, np.full((2, 2), 0.2))
    with pytest.raises(ValueError, match='witness SHA-256 or Git blob mismatch'):
        preflight.preflight(sample, witness)


@pytest.mark.parametrize('change', ['crs', 'transform', 'shape'])
def test_reject_misaligned_witness_even_when_pinned(pinned_pair, monkeypatch, change):
    from rasterio.transform import from_origin
    sample, witness = pinned_pair
    kw = {}
    data = np.ones((2, 2))
    if change == 'crs':
        kw['crs'] = 'EPSG:4326'
    elif change == 'transform':
        kw['transform'] = from_origin(243450, 4508550, 100, 100)
    else:
        data = np.ones((2, 3))
    write_tif(witness, data, **kw)
    sha, blob = preflight.hashes(witness)
    monkeypatch.setattr(preflight, 'WITNESS_SHA256', sha)
    monkeypatch.setattr(preflight, 'WITNESS_BLOB', blob)
    with pytest.raises(ValueError, match='not aligned'):
        preflight.preflight(sample, witness)


def test_cli_refuses_receipt_overwrite(pinned_pair, tmp_path, monkeypatch):
    import sys
    sample, witness = pinned_pair
    output = tmp_path / 'receipt.json'
    output.write_text('historical receipt')
    monkeypatch.setattr(sys, 'argv', ['preflight', '--sample', str(sample),
                        '--witness', str(witness), '--output', str(output)])
    assert preflight.main() == 2
    assert output.read_text() == 'historical receipt'


def test_cli_duplicate_returns_one_and_writes_receipt(pinned_pair, tmp_path, monkeypatch):
    import json
    import sys
    sample, witness = pinned_pair
    output = tmp_path / 'receipt.json'
    monkeypatch.setattr(sys, 'argv', ['preflight', '--sample', str(sample),
                        '--witness', str(witness), '--output', str(output)])
    assert preflight.main() == 1
    assert json.loads(output.read_text())['verdict'] == 'negative'


def test_sample_pin_matches_manifest():
    import json
    root = Path(__file__).resolve().parents[1]
    entries = json.loads((root / 'registry/session_manifest.json').read_text())['files']
    entry = next(e for e in entries if e['id'] == 'sample_submission')
    assert preflight.SAMPLE_SHA256 == entry['sha256']
