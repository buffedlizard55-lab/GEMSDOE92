"""On-disk template checks and race-safe packaging use the shared writer."""
from __future__ import annotations

import os
import zipfile
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from gems57 import gates, grid, submission_writer, validate


@pytest.fixture
def tiny_grid(tmp_path, monkeypatch):
    shape = (4, 5)
    transform = from_origin(243350, 4508550, 100, 100)
    monkeypatch.setattr(grid, 'SHAPE', shape)
    monkeypatch.setattr(grid, 'TRANSFORM', transform)
    monkeypatch.setattr(gates, 'SHAPE', shape)
    monkeypatch.setattr(gates, 'TRANSFORM', transform)
    monkeypatch.setattr(validate, 'HEIGHT', shape[0])
    monkeypatch.setattr(validate, 'WIDTH', shape[1])
    monkeypatch.setattr(validate, 'TRANSFORM', transform)
    sample = tmp_path / 'sample.tif'
    data = np.zeros(shape, dtype=np.float32)
    data[0, 0] = np.nan
    with rasterio.open(sample, 'w', driver='GTiff', height=shape[0], width=shape[1],
                       count=1, dtype='float32', crs='EPSG:32611',
                       transform=transform, nodata=np.nan) as ds:
        ds.write(data, 1)
    fp = np.isfinite(data)
    p = np.zeros(shape, dtype=np.float32)
    p[2, 2] = 1
    return sample, fp, p


def test_writer_rejects_supplied_mask_that_includes_reference_nodata(tiny_grid, tmp_path):
    sample, fp, pred = tiny_grid
    fp[0, 0] = True
    out = tmp_path / 'new' / 'candidate.tif'
    with pytest.raises(ValueError, match='outside the reference footprint'):
        submission_writer.write_submission(out, pred, sample, fp, name='test', note='test')
    assert not out.parent.exists()


def test_format_report_derives_reference_footprint_even_without_mask(tiny_grid, tmp_path):
    sample, fp, pred = tiny_grid
    pred[0, 0] = 0.5
    out = tmp_path / 'outside.tif'
    grid.write_geotiff(out, pred)
    report = gates.format_report(out, sample)
    assert not report['ok']
    assert report['mass_outside_reference_footprint'] == 1
    assert any('outside the reference footprint' in s for s in report['problems'])
    forged = gates.format_report(out, sample, footprint=np.ones(fp.shape, bool))
    assert not forged['ok']
    assert any('supplied footprint includes' in s for s in forged['problems'])


def test_writer_success_is_disk_validated_and_one_tiff_zip(tiny_grid, tmp_path):
    sample, fp, pred = tiny_grid
    out = tmp_path / 'candidate.tif'
    receipt = submission_writer.write_submission(out, pred, sample, fp, name='test', note='test')
    assert out.is_file() and out.with_suffix('.json').is_file()
    with zipfile.ZipFile(out.with_suffix('.zip')) as z:
        assert z.namelist() == [out.name]
        assert z.read(out.name) == out.read_bytes()
    assert receipt['template_report']['mass_outside_reference_footprint'] == 0
    assert receipt['approved_for_weekly_slot'] is False
    assert receipt['promoted'] is False


def test_commit_never_overwrites_a_concurrent_file(tiny_grid, tmp_path, monkeypatch):
    sample, fp, pred = tiny_grid
    out = tmp_path / 'candidate.tif'
    orig_link = os.link

    def concurrent_link(src, dst):
        if Path(dst).suffix == '.json':
            Path(dst).write_bytes(b'other process receipt')
        return orig_link(src, dst)

    monkeypatch.setattr(submission_writer.os, 'link', concurrent_link)
    with pytest.raises(FileExistsError):
        submission_writer.write_submission(out, pred, sample, fp, name='test', note='test')
    assert out.with_suffix('.json').read_bytes() == b'other process receipt'
    assert not out.exists() and not out.with_suffix('.zip').exists()
    assert not list(tmp_path.glob('.candidate.*'))


def test_rollback_does_not_delete_a_concurrently_replaced_output(tiny_grid, tmp_path, monkeypatch):
    sample, fp, pred = tiny_grid
    out = tmp_path / 'candidate.tif'
    orig_link = os.link

    def concurrent_link(src, dst):
        if Path(dst).suffix == '.json':
            archive = out.with_suffix('.zip')
            archive.unlink()
            archive.write_bytes(b'other process archive')
            Path(dst).write_bytes(b'other process receipt')
        return orig_link(src, dst)

    monkeypatch.setattr(submission_writer.os, 'link', concurrent_link)
    with pytest.raises(FileExistsError):
        submission_writer.write_submission(out, pred, sample, fp, name='test', note='test')
    assert out.with_suffix('.zip').read_bytes() == b'other process archive'
    assert out.with_suffix('.json').read_bytes() == b'other process receipt'
    assert not out.exists() and not list(tmp_path.glob('.candidate.*'))
