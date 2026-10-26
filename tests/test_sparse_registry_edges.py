"""Shared sparse overlap dilation must respect both axes at grid boundaries."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from vendor.gems57 import uniqueness as U

ROOT = Path(__file__).resolve().parents[1]


def test_row_edge_never_wraps_into_previous_or_next_row():
    shape = (6, 10)
    seed = np.array([2 * shape[1]], dtype=np.int64)  # row 2, column 0
    out = np.zeros(shape[0] * shape[1], dtype=bool)
    U.mark_sparse_near_inplace(out, seed, shape)
    halo = out.reshape(shape)
    assert halo[2, 3]
    assert not halo[1, 9]  # a flattened -1 would incorrectly mark this cell
    expected = np.zeros(shape, dtype=bool)
    expected[2, 0] = True
    assert np.array_equal(halo, U._near(expected, 3))
    U.mark_sparse_near_inplace(out, seed, shape, value=False)
    assert not out.any()


@pytest.mark.parametrize("shape", [(1, 1), (2, 5), (6, 10), (31, 27)])
@pytest.mark.parametrize("radius", [0, 1, 2.5, 3])
def test_sparse_halo_matches_shared_dense_reference_and_clears(shape, radius):
    rng = np.random.default_rng(20261026)
    support = rng.random(shape) < 0.15
    support[0, 0] = support[-1, -1] = True
    indices = np.flatnonzero(support)
    out = np.zeros(support.size, dtype=bool)
    U.mark_sparse_near_inplace(out, indices, shape, radius)
    assert np.array_equal(out.reshape(shape), U._near(support, radius))
    U.mark_sparse_near_inplace(out, indices, shape, radius, value=False)
    assert not out.any()


def test_rejects_malformed_buffers_indices_and_radius():
    out = np.zeros(12, dtype=bool)
    with pytest.raises(ValueError):
        U.mark_sparse_near_inplace(out, np.array([-1]), (3, 4))
    with pytest.raises(ValueError):
        U.mark_sparse_near_inplace(out, np.array([12]), (3, 4))
    with pytest.raises(ValueError):
        U.mark_sparse_near_inplace(out, np.array([1.0]), (3, 4))
    with pytest.raises(ValueError):
        U.mark_sparse_near_inplace(np.zeros(12, dtype=np.uint8), np.array([1]), (3, 4))
    with pytest.raises(ValueError):
        U.mark_sparse_near_inplace(out, np.array([1]), (3, 4), float("nan"))
    with pytest.raises(ValueError):
        U.mark_sparse_near_inplace(out, np.array([1]), (3, 4), value=1)
    U.mark_sparse_near_inplace(out, np.array([0]), (3, 4), 1e100)
    assert out.all()


def test_pairwise_recheck_uses_true_2d_distance_at_row_edges():
    from scripts.recheck_focus9_pairwise import pair_statistics
    footprint = np.ones((6, 10), dtype=bool)
    a = np.zeros_like(footprint)
    b = np.zeros_like(footprint)
    a[2, 0] = True
    b[1, 9] = True
    result = pair_statistics(a, b, footprint)
    assert result["forward_3px_overlap_a_to_b"] == 0.0
    assert result["forward_3px_overlap_b_to_a"] == 0.0
    assert result["duplicate_by_configured_threshold"] is False


def test_prior_fast_scanners_share_the_row_safe_implementation():
    for name in ("run_salem_seismo.py", "run_thermotilt.py", "run_chilistric.py",
                 "run_listric_loqo.py", "audit_focus9_sites.py"):
        source = (ROOT / "scripts" / name).read_text()
        assert "U.mark_sparse_near_inplace" in source
        assert "offsets_1d" not in source
        assert "np.clip(fidx + d" not in source
