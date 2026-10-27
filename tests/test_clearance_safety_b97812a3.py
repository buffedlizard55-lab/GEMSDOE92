"""Regression tests: format checks and historical cards cannot grant a slot."""
from __future__ import annotations

import hashlib
import json

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

import validate_submission as entry
from gems.gates import GateResult, run_gates, summarise
from gems57 import gates as shared_gates
from gems57 import grid, submission_writer, validate as shared_validate
from scripts import validate_submission as format_cli


@pytest.mark.parametrize('gates', [{}, {'format': 'false'},
    {'format': True, 'canary': True, 'holdout_beats_best_control': True,
     'operative_uniqueness': True}])
def test_forged_or_incomplete_promotion_never_grants_a_slot(tmp_path, monkeypatch, capsys, gates):
    (tmp_path / 'evidence').mkdir()
    candidate = tmp_path / 'candidate.tif'
    candidate.write_bytes(b'synthetic only; format gates are deliberately mocked')
    card = {'submission_file': 'candidate.tif',
            'raster_sha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
            'verdict': 'promote', 'submission_eligible': True, 'gates': gates,
            'submission_name': 'not_authorized'}
    (tmp_path / 'evidence/vario_run_card.json').write_text(json.dumps(card))
    monkeypatch.setattr(entry, 'ROOT', tmp_path)
    core = ('crs', 'shape', 'transform', 'dtype_and_band', 'values_in_0_1',
            'no_nan_inside_footprint', 'nan_outside_footprint', 'reread_sha256')
    monkeypatch.setattr(entry, 'run_gates', lambda *a, **kw: [GateResult(n, True, 'mock') for n in core])
    assert entry.main([str(candidate)]) == 1
    text = capsys.readouterr().out
    assert 'FORMAT PASS (local only)' in text
    assert 'DO NOT SUBMIT' in text
    assert 'OK TO SUBMIT' not in text


@pytest.mark.parametrize('results', [[], [GateResult('proxy_not_a_gate', True, '')],
    [GateResult('format', True, '')],  # positive but incomplete evidence is not a format pass
    [GateResult('format', 'false', '')], [GateResult('format', 1, '')],
    [GateResult('format', True, ''), GateResult('format', True, '')]])
def test_missing_truthy_or_duplicate_gates_do_not_pass(results):
    ok, report = summarise(results)
    assert ok is False
    assert 'RESULT: FAIL' in report


@pytest.fixture
def small_grid(tmp_path, monkeypatch):
    shape = (4, 5)
    tr = from_origin(243350, 4508550, 100, 100)
    monkeypatch.setattr(grid, 'SHAPE', shape)
    monkeypatch.setattr(grid, 'TRANSFORM', tr)
    monkeypatch.setattr(shared_gates, 'SHAPE', shape)
    monkeypatch.setattr(shared_gates, 'TRANSFORM', tr)
    monkeypatch.setattr(shared_validate, 'HEIGHT', shape[0])
    monkeypatch.setattr(shared_validate, 'WIDTH', shape[1])
    monkeypatch.setattr(shared_validate, 'TRANSFORM', tr)
    sample = tmp_path / 'sample.tif'
    arr = np.zeros(shape, np.float32)
    arr[0, 0] = np.nan
    with rasterio.open(sample, 'w', driver='GTiff', height=shape[0], width=shape[1],
                       count=1, dtype='float32', crs='EPSG:32611',
                       transform=tr, nodata=np.nan) as dst:
        dst.write(arr, 1)
    fp = np.isfinite(arr)
    return sample, fp, tr


def _candidate(path, tr, *, nodata=None, masked_inside=False):
    arr = np.zeros((4, 5), np.float32)
    arr[2, 2] = 1.0
    with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
        with rasterio.open(path, 'w', driver='GTiff', height=4, width=5, count=1,
                           dtype='float32', crs='EPSG:32611', transform=tr,
                           nodata=nodata) as dst:
            dst.write(arr, 1)
            if masked_inside:
                mask = np.full((4, 5), 255, np.uint8)
                mask[1, 1] = 0
                dst.write_mask(mask)
    return arr


@pytest.mark.parametrize('nodata,masked_inside', [(0, False), (None, True)])
def test_raw_finite_values_with_masked_footprint_are_rejected(
        tmp_path, small_grid, nodata, masked_inside):
    sample, fp, tr = small_grid
    candidate = tmp_path / 'masked.tif'
    arr = _candidate(candidate, tr, nodata=nodata, masked_inside=masked_inside)
    assert np.isfinite(arr).all() and arr.min() >= 0 and arr.max() <= 1
    ok, report = summarise(run_gates(candidate, sample, require_submission_encoding=True))
    assert not ok and 'masked_pixels=' in report and '[FAIL] no_nan_inside_footprint' in report
    shared = shared_gates.format_report(candidate, sample, footprint=fp)
    assert not shared['ok'] and shared['masked_inside_reference_footprint'] > 0
    independent = shared_validate.validate(candidate, fp)
    assert not independent['all_checks_passed']
    assert independent['checks']['in_footprint_unmasked'] is False
    assert not format_cli.check_file(candidate, fp, np.zeros_like(fp),
                                     rasterio.crs.CRS.from_epsg(32611), fp.shape, tr)
    # Without a footprint the independent validator cannot locate a mask;
    # it must also refuse to declare the file clean.
    assert not shared_validate.validate(candidate)['all_checks_passed']


def test_format_cli_validates_reference_mask_and_grid(tmp_path, small_grid, monkeypatch):
    sample, fp, tr = small_grid
    monkeypatch.setattr(format_cli, 'SAMPLE_PATH', sample)
    labels = tmp_path / 'labels.tif'
    monkeypatch.setattr(format_cli, 'LABELS_PATH', labels)
    with rasterio.open(labels, 'w', driver='GTiff', height=4, width=5, count=1,
                       dtype='float32', crs='EPSG:32611', transform=tr) as dst:
        dst.write(np.zeros((4, 5), np.float32), 1)
    checked_fp, cat, crs, shape, transform = format_cli.load_reference()
    assert np.array_equal(checked_fp, fp)
    candidate = tmp_path / 'clean-zeros.tif'
    _candidate(candidate, tr)
    assert format_cli.check_file(candidate, checked_fp, cat, crs, shape, transform)
    with rasterio.open(labels, 'w', driver='GTiff', height=4, width=5, count=1,
                       dtype='float32', crs='EPSG:32611',
                       transform=from_origin(0, 0, 1, 1)) as dst:
        dst.write(np.zeros((4, 5), np.float32), 1)
    with pytest.raises(ValueError, match='catalogue grid'):
        format_cli.load_reference()


def test_masked_catalogue_inside_footprint_is_not_trusted(tmp_path, small_grid, monkeypatch):
    sample, fp, tr = small_grid
    candidate = tmp_path / 'candidate.tif'
    _candidate(candidate, tr)
    labels = tmp_path / 'masked-catalogue.tif'
    with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
        with rasterio.open(labels, 'w', driver='GTiff', height=4, width=5, count=1,
                           dtype='float32', crs='EPSG:32611', transform=tr) as dst:
            dst.write(np.zeros((4, 5), np.float32), 1)
            mask = np.full((4, 5), 255, np.uint8)
            mask[1, 1] = 0
            dst.write_mask(mask)
    ok, report = summarise(run_gates(candidate, sample, labels, require_submission_encoding=True))
    assert not ok and '[FAIL] catalogue_validity' in report
    monkeypatch.setattr(format_cli, 'SAMPLE_PATH', sample)
    monkeypatch.setattr(format_cli, 'LABELS_PATH', labels)
    with pytest.raises(ValueError, match='catalogue contains invalid cells'):
        format_cli.load_reference()


def test_template_rejects_finite_nodata_reference_ambiguity(tmp_path, small_grid, monkeypatch):
    _, _, tr = small_grid
    ref = tmp_path / 'finite-nodata-reference.tif'
    arr = np.zeros((4, 5), np.float32)
    arr[0, 0] = -9999
    with rasterio.open(ref, 'w', driver='GTiff', height=4, width=5, count=1,
                       dtype='float32', crs='EPSG:32611', transform=tr, nodata=-9999) as dst:
        dst.write(arr, 1)
    cand = tmp_path / 'clean.tif'
    pred = _candidate(cand, tr)
    ok, report = summarise(run_gates(cand, ref, require_submission_encoding=True))
    assert not ok and 'reference_footprint' in report
    assert not shared_gates.format_report(cand, ref)['ok']
    monkeypatch.setattr(format_cli, 'SAMPLE_PATH', ref)
    with pytest.raises(ValueError, match='footprint is empty or disagrees'):
        format_cli.load_reference()
    with pytest.raises(ValueError, match='reference finite footprint disagrees'):
        submission_writer.write_submission(tmp_path / 'out.tif', pred, ref,
                                           np.isfinite(arr), name='test', note='test')


def test_writer_does_not_accept_a_smaller_supplied_footprint(tmp_path, small_grid):
    sample, fp, tr = small_grid
    smaller = fp.copy()
    smaller[1, 1] = False
    pred = _candidate(tmp_path / 'clean.tif', tr)
    with pytest.raises(ValueError, match='omits valid reference cells'):
        submission_writer.write_submission(tmp_path / 'new/out.tif', pred, sample, smaller,
                                           name='test', note='test')
    assert not (tmp_path / 'new').exists()
