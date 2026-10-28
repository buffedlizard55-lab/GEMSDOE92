"""Unit tests for scripts/measure_registry_overlap.py (REGISTRY-MEASUREMENT tool)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import measure_registry_overlap as m  # noqa: E402


def _write(path: Path, arr: np.ndarray, transform=None, crs="EPSG:32611") -> Path:
    t = transform or from_origin(0, 0, 100, 100)
    with rasterio.open(
        path, "w", driver="GTiff", height=arr.shape[0], width=arr.shape[1],
        count=1, dtype="float32", crs=crs, transform=t,
    ) as dst:
        dst.write(arr.astype("float32"), 1)
    return path


def test_disk_is_euclidean_radius_3():
    d = m.disk(3)
    c = 3  # centre index
    assert d[c, c + 3] and d[c + 3, c]          # distance 3 included
    assert d[c + 2, c + 2]                       # distance 2.83 included
    assert not d[c + 3, c + 3]                   # distance 4.24 excluded
    assert d[0, c] and not d[0, 0]               # axis distance 3 in, corner (4.24) out


def test_overlap_boundary_at_3px():
    cand = np.zeros((20, 20), bool)
    cand[10, 10] = True
    wit = np.zeros((20, 20), bool)
    wit[10, 13] = True                           # exactly 3 px away
    assert m.overlap_fraction(cand, wit) == 1.0
    wit2 = np.zeros((20, 20), bool)
    wit2[10, 14] = True                          # 4 px away
    assert m.overlap_fraction(cand, wit2) == 0.0


def test_overlap_empty_candidate_is_zero():
    assert m.overlap_fraction(np.zeros((5, 5), bool), np.ones((5, 5), bool)) == 0.0


def test_topk_selects_largest_finite_cells_only():
    vals = np.array([[0.9, np.nan], [0.5, 0.7]])
    fin = np.isfinite(vals)
    mask = m.topk_mask(vals, fin, 2)
    assert mask.tolist() == [[True, False], [False, True]]
    assert m.topk_mask(vals, fin, 0).sum() == 0


def test_topk_never_pads_with_zero_background():
    vals = np.array([[1.0, 0.0], [0.0, 0.0]])
    fin = np.isfinite(vals)
    mask = m.topk_mask(vals, fin, 50)           # K larger than positive support
    assert mask.sum() == 1 and mask[0, 0]


def test_measure_literal_and_topk_readings(tmp_path):
    w = np.full((30, 30), 0.1, np.float32)
    w[5, 5] = 0.99                               # witness top cell
    w[20, 20] = 0.95                             # second
    wp = _write(tmp_path / "w.tif", w)
    c = np.zeros((30, 30), np.float32)
    c[5, 7] = 1.0                                # 2 px from witness top cell -> overlaps
    c[25, 25] = 1.0                              # far from both top cells
    cp = _write(tmp_path / "c.tif", c)
    out = m.measure(wp, cp)
    assert out["candidate_positive_cells"] == 2
    assert out["overlap_topk_witness_cells"] == pytest.approx(0.5)
    # literal reading: every witness cell is positive, so every candidate dot overlaps
    assert out["overlap_literal_every_positive_witness_cell"] == 1.0
    assert out["clearance"].startswith("none")


def test_measure_rejects_mismatched_grid(tmp_path):
    wp = _write(tmp_path / "w.tif", np.ones((10, 10)))
    cp = _write(tmp_path / "c.tif", np.ones((10, 10)), transform=from_origin(1, 0, 100, 100))
    with pytest.raises(ValueError):
        m.measure(wp, cp)
