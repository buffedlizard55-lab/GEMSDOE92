"""Tests for the MUST-pass format gates, using a synthetic reference grid.

These build real GeoTIFFs on disk (that is the whole point: the gates must see
what the uploader sees, not an in-memory array).
"""

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from gems.cli import main as cli_main
from gems.gates import run_gates, summarise
from gems.rasters import read_reference, sha256_file, write_candidate

SHAPE = (40, 50)


def make_reference(tmp_path, footprint_slice=(slice(5, 35), slice(5, 45))):
    ref = np.full(SHAPE, np.nan, dtype=np.float32)
    ref[footprint_slice] = 0.0
    path = tmp_path / "sample_submission.tif"
    with rasterio.open(path, "w", driver="GTiff", height=SHAPE[0], width=SHAPE[1],
                       count=1, dtype="float32", crs="EPSG:32611",
                       transform=from_origin(500000, 4200000, 100, 100),
                       nodata=np.float32(np.nan)) as ds:
        ds.write(ref, 1)
    return path


def make_catalogue(tmp_path, pixels):
    arr = np.zeros(SHAPE, dtype=np.uint8)
    for y, x in pixels:
        arr[y, x] = 1
    path = tmp_path / "catalogue.tif"
    with rasterio.open(path, "w", driver="GTiff", height=SHAPE[0], width=SHAPE[1],
                       count=1, dtype="uint8", crs="EPSG:32611",
                       transform=from_origin(500000, 4200000, 100, 100)) as ds:
        ds.write(arr, 1)
    return path


def build_dots(pixels):
    arr = np.zeros(SHAPE, dtype=np.float32)
    for y, x in pixels:
        arr[y, x] = 1.0
    return arr


def test_clean_candidate_passes_all_gates(tmp_path):
    refp = make_reference(tmp_path)
    reference = read_reference(refp)
    dots = build_dots([(10, 10), (11, 11), (12, 12)])
    out = tmp_path / "cand.tif"
    write_candidate(out, dots, reference, outside="nan")
    results = run_gates(out, refp)
    ok, report = summarise(results)
    assert ok, report


def test_zeros_outside_is_also_accepted(tmp_path):
    refp = make_reference(tmp_path)
    reference = read_reference(refp)
    dots = build_dots([(10, 10)])
    out = tmp_path / "cand_zeros.tif"
    write_candidate(out, dots, reference, outside="zero")
    ok, report = summarise(run_gates(out, refp))
    assert ok, report


def test_strict_submission_encoding_accepts_only_finite_zeros_outside(tmp_path):
    refp = make_reference(tmp_path)
    reference = read_reference(refp)
    dots = build_dots([(10, 10)])
    out = tmp_path / "cand_zeros.tif"
    write_candidate(out, dots, reference, outside="zero")
    ok, report = summarise(run_gates(out, refp, require_submission_encoding=True))
    assert ok, report
    assert "submission_encoding" in report
    assert "all_finite=True" in report
    assert "zero_outside=True" in report


def test_strict_submission_encoding_rejects_nan_outside(tmp_path):
    refp = make_reference(tmp_path)
    reference = read_reference(refp)
    out = tmp_path / "cand_nan.tif"
    write_candidate(out, build_dots([(10, 10)]), reference, outside="nan")
    ok, report = summarise(run_gates(out, refp, require_submission_encoding=True))
    assert not ok
    assert "submission_encoding" in report
    assert "all_finite=False" in report


def test_cli_submission_preflight_rejects_nan_outside(tmp_path, capsys):
    refp = make_reference(tmp_path)
    reference = read_reference(refp)
    out = tmp_path / "cand_nan.tif"
    write_candidate(out, build_dots([(10, 10)]), reference, outside="nan")

    assert cli_main(["validate", str(out), "--reference", str(refp)]) == 1
    report = capsys.readouterr().out
    assert "submission_encoding" in report
    assert "all_finite=False" in report
    assert "RESULT: FAIL" in report


def test_cli_submission_preflight_accepts_zeros_outside(tmp_path, capsys):
    refp = make_reference(tmp_path)
    reference = read_reference(refp)
    out = tmp_path / "cand_zeros.tif"
    write_candidate(out, build_dots([(10, 10)]), reference, outside="zero")

    assert cli_main(["validate", str(out), "--reference", str(refp)]) == 0
    report = capsys.readouterr().out
    assert "submission_encoding" in report
    assert "all_finite=True" in report
    assert "zero_outside=True" in report
    assert "RESULT: PASS" in report


def test_nan_inside_footprint_fails(tmp_path):
    refp = make_reference(tmp_path)
    reference = read_reference(refp)
    dots = build_dots([(10, 10)])
    out = tmp_path / "cand.tif"
    write_candidate(out, dots, reference)
    # punch a NaN inside the footprint with rasterio directly
    with rasterio.open(out, "r+") as ds:
        arr = ds.read(1)
        arr[20, 20] = np.nan
        ds.write(arr, 1)
    ok, report = summarise(run_gates(out, refp))
    assert not ok
    assert "no_nan_inside_footprint" in report


def test_dot_on_catalogue_fails_zero_mass(tmp_path):
    refp = make_reference(tmp_path)
    catp = make_catalogue(tmp_path, [(10, 10)])
    reference = read_reference(refp)
    dots = build_dots([(10, 10)])          # ON the catalogue
    out = tmp_path / "cand.tif"
    write_candidate(out, dots, reference)
    ok, report = summarise(run_gates(out, refp, catalogue_path=catp))
    assert not ok
    assert "catalogue_zero_mass" in report


def test_dot_within_3px_of_catalogue_fails_distance_gate(tmp_path):
    refp = make_reference(tmp_path)
    catp = make_catalogue(tmp_path, [(10, 10)])
    reference = read_reference(refp)
    dots = build_dots([(10, 12)])          # 2 px away
    out = tmp_path / "cand.tif"
    write_candidate(out, dots, reference)
    ok, report = summarise(run_gates(out, refp, catalogue_path=catp))
    assert not ok
    assert "distance_from_catalogue" in report


def test_prune_axis_deviation_is_declared_not_silent(tmp_path):
    refp = make_reference(tmp_path)
    catp = make_catalogue(tmp_path, [(10, 10)])
    reference = read_reference(refp)
    dots = build_dots([(10, 12)])
    out = tmp_path / "cand.tif"
    write_candidate(out, dots, reference)
    ok, report = summarise(run_gates(out, refp, catalogue_path=catp, prune_radius=2))
    assert ok, report
    assert "declared clearance override" in report


def test_value_out_of_range_fails(tmp_path):
    refp = make_reference(tmp_path)
    reference = read_reference(refp)
    dots = np.zeros(SHAPE, dtype=np.float32)
    dots[10, 10] = 1.5
    out = tmp_path / "cand.tif"
    write_candidate(out, dots, reference)
    ok, report = summarise(run_gates(out, refp))
    assert not ok
    assert "values_in_0_1" in report


@pytest.mark.parametrize("bad", [np.inf, -np.inf, -0.01, 1.01])
def test_invalid_finite_or_infinite_values_outside_footprint_fail(tmp_path, bad):
    refp = make_reference(tmp_path)
    reference = read_reference(refp)
    out = tmp_path / "cand.tif"
    write_candidate(out, build_dots([(10, 10)]), reference, outside="zero")
    with rasterio.open(out, "r+") as ds:
        arr = ds.read(1)
        arr[0, 0] = bad
        ds.write(arr, 1)

    ok, report = summarise(run_gates(out, refp))
    assert not ok
    assert "nan_outside_footprint" in report
    assert "inf=1" in report if np.isinf(bad) else "other=1" in report

    strict_ok, strict_report = summarise(
        run_gates(out, refp, require_submission_encoding=True)
    )
    assert not strict_ok
    assert "submission_encoding" in strict_report


def test_sha256_is_of_the_file_on_disk(tmp_path):
    refp = make_reference(tmp_path)
    reference = read_reference(refp)
    out = tmp_path / "cand.tif"
    sha = write_candidate(out, build_dots([(10, 10)]), reference)
    assert sha == sha256_file(out)
    assert len(sha) == 64
