import numpy as np

from gems.drainage_knick import percentile_rank


def test_percentile_rank_bounds_and_mask():
    a = np.arange(9, dtype=np.float32).reshape(3, 3)
    valid = np.ones_like(a, dtype=bool)
    valid[0, 0] = False
    out = percentile_rank(a, valid)
    assert out.dtype == np.float32
    assert out[0, 0] == 0
    assert np.all((out >= 0) & (out <= 1))
    assert out[2, 2] == 1


def test_percentile_rank_empty_is_zero():
    a = np.ones((2, 2), dtype=np.float32)
    out = percentile_rank(a, np.zeros_like(a, dtype=bool))
    assert np.array_equal(out, np.zeros_like(a))
