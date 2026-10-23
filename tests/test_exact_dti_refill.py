from __future__ import annotations

import numpy as np

from exact_dti_refill import dot_thin, select_exact_marginal_dti_add


def test_dot_thin_is_deterministic_and_respects_open_disk_minimum() -> None:
    source = np.zeros((30, 40), dtype=bool)
    source[5:24, 7:31] = True
    a = dot_thin(source, 2.8)
    b = dot_thin(source, 2.8)
    assert np.array_equal(a, b)
    yy, xx = np.nonzero(a)
    for i in range(len(yy)):
        if i + 1 < len(yy):
            d2 = (yy[i + 1 :] - yy[i]) ** 2 + (xx[i + 1 :] - xx[i]) ** 2
            assert np.all(d2 >= 2.8**2)


def test_exact_refill_preserves_count_and_obeys_candidate_pool() -> None:
    base = np.zeros((20, 20), dtype=bool)
    base[3, 3] = True
    base[12, 12] = True
    candidates = np.zeros_like(base)
    candidates[3, 8] = True
    candidates[8, 8] = True
    candidates[16, 3] = True
    weights = np.ones(base.shape, dtype=np.float32)
    out = select_exact_marginal_dti_add(base, candidates, weights, n_add=2)
    assert int(out.sum()) == 4
    assert np.all(out[~(base | candidates)] == 0)
    assert int((out & candidates).sum()) == 2
