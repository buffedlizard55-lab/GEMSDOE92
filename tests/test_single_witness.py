"""Fail-closed, disk-based tests for the rejection-only witness instrument."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from scripts.check_public_witness import git_blob_sha, measure_witness


@pytest.fixture
def files(tmp_path):
    def write(name, data, **overrides):
        options = dict(driver="GTiff", height=12, width=12, count=1,
                       dtype="float32", crs="EPSG:32611",
                       transform=from_origin(500000, 4200000, 100, 100))
        options.update(overrides)
        p = tmp_path / name
        with rasterio.open(p, "w", **options) as ds:
            ds.write(np.asarray(data, dtype="float32"), 1)
        return p
    ref = np.full((12, 12), np.nan, dtype="float32")
    ref[2:10, 2:10] = 0
    cand = np.zeros_like(ref)
    cand[5, 5] = 1
    return write, write("ref.tif", ref), write("cand.tif", cand), write("wit.tif", np.ones_like(ref))


def measure(files):
    _, ref, cand, wit = files
    return measure_witness(cand, wit, ref, repo="test/registry", path="witness.tif",
                           expected_git_sha=git_blob_sha(wit))


def test_dense_witness_is_universal_stop(files):
    doc = measure(files)
    assert doc["forward_overlap_candidate_dots_within_3px_of_witness"] == 1
    assert doc["universal_nonempty_in_footprint_overlap_stop"] is True
    assert doc["spearman_full_footprint"] is None  # constant witness: undefined
    assert doc["stop_required_vs_this_witness"] is True
    assert doc["submission_eligible"] is False
    json.dumps(doc, allow_nan=False)


@pytest.mark.parametrize("target", ["cand.tif", "wit.tif"])
@pytest.mark.parametrize("override", [dict(crs="EPSG:4326"),
    dict(transform=from_origin(500100, 4200000, 100, 100)), dict(count=2), dict(height=13), dict(width=13)])
def test_mismatched_grids_never_compare(files, target, override):
    write, _, cand, wit = files
    p = cand if target == "cand.tif" else wit
    with rasterio.open(p) as ds:
        data = ds.read(1)
    write(target, data, **override)
    with pytest.raises(ValueError, match="grid/band mismatch"):
        measure(files)


@pytest.mark.parametrize("bad", [np.nan, np.inf, -0.01, 1.01])
def test_invalid_prediction_fails(files, bad):
    _, _, cand, _ = files
    with rasterio.open(cand, "r+") as ds:
        data = ds.read(1)
        data[4, 4] = bad
        ds.write(data, 1)
    with pytest.raises(ValueError, match="all-finite"):
        measure(files)


def test_outside_predictions_not_silently_hidden(files):
    _, _, cand, _ = files
    with rasterio.open(cand, "r+") as ds:
        data = ds.read(1)
        data[0, 0] = 1
        ds.write(data, 1)
    with pytest.raises(ValueError, match="outside footprint"):
        measure(files)


def test_empty_candidate_not_a_uniqueness_escape(files):
    write, _, _, _ = files
    write("cand.tif", np.zeros((12, 12)))
    with pytest.raises(ValueError, match="empty candidate"):
        measure(files)


def test_empty_witness_does_not_fabricate_boundary_distances(files):
    write, _, _, _ = files
    write("wit.tif", np.zeros((12, 12)))
    doc = measure(files)
    assert doc["forward_overlap_candidate_dots_within_3px_of_witness"] == 0
    assert doc["stop_required_vs_this_witness"] is False
    assert doc["unique_under_literal_rule_vs_this_witness"] is None
    assert doc["submission_eligible"] is False


def test_hash_mismatch_fails(files):
    _, ref, cand, wit = files
    with pytest.raises(ValueError, match="SHA mismatch"):
        measure_witness(cand, wit, ref, repo="test/registry", path="wit.tif",
                        expected_git_sha="0" * 40)


def test_rank_alone_can_reject_when_dot_overlap_is_low(files):
    write, _, _, _ = files
    # Opposite signed witness: no shared positive support but |rho| = 1.
    cand = np.zeros((12, 12), dtype="float32")
    cand[2:10, 2:10] = np.linspace(0.01, 1, 64).reshape(8, 8)
    write("cand.tif", cand)
    write("wit.tif", -cand)
    doc = measure(files)
    assert doc["spearman_full_footprint"] == pytest.approx(-1)
    assert doc["forward_overlap_candidate_dots_within_3px_of_witness"] == 0
    assert doc["stop_required_vs_this_witness"] is True


def test_cli_records_stop_and_preserves_old_receipt(files, tmp_path):
    _, ref, cand, wit = files
    output = tmp_path / "receipt.json"
    script = Path(__file__).resolve().parents[1] / "scripts/check_public_witness.py"
    cmd = [sys.executable, str(script), str(cand), str(wit), "--reference", str(ref),
           "--repo", "test/registry", "--path", "wit.tif", "--git-sha", git_blob_sha(wit),
           "--output", str(output)]
    first = subprocess.run(cmd, capture_output=True, text=True)
    assert first.returncode == 1, first.stderr
    old = output.read_bytes()
    second = subprocess.run(cmd, capture_output=True, text=True)
    assert second.returncode == 2
    assert output.read_bytes() == old
