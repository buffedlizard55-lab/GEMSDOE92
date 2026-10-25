import numpy as np
import pytest

from gems.listric import LISTRIC_FEATURE_NAMES, _shift, compute_listric_features


def test_shift_no_wrap():
    a = np.zeros((5, 5), np.float32); a[2, 2] = 1.0
    s = _shift(a, 2, 0)
    assert s[4, 2] == 1.0 and s.sum() == 1.0
    s2 = _shift(a, -3, 0)
    assert s2.sum() == 0.0  # shifted off-grid, no wraparound


def test_listric_features_shapes_and_range():
    rng = np.random.default_rng(7); shape = (48, 40); foot = np.ones(shape, bool)
    f = compute_listric_features(
        det_elev=rng.normal(1500, 40, shape).astype("f4"),
        det_elev_slope=np.abs(rng.normal(4, 1, shape)).astype("f4"),
        grav_hg=rng.normal(0, 1, shape).astype("f4"),
        depth_to_base=np.abs(rng.normal(400, 80, shape)).astype("f4"),
        footprint=foot, valid=foot)
    for name in LISTRIC_FEATURE_NAMES:
        v = f[name]
        assert v.shape == shape and np.isfinite(v).all()
        assert v.min() >= 0.0 and v.max() <= 1.0001
    assert f["L_listric"].shape == shape


def test_listric_offset_excess_nonnegative():
    rng = np.random.default_rng(1); shape = (32, 32); foot = np.ones(shape, bool)
    f = compute_listric_features(
        det_elev=rng.normal(0, 1, shape).astype("f4"),
        det_elev_slope=np.abs(rng.normal(0, 1, shape)).astype("f4"),
        grav_hg=rng.normal(0, 1, shape).astype("f4"),
        depth_to_base=np.abs(rng.normal(0, 1, shape)).astype("f4"),
        footprint=foot, valid=foot)
    assert (f["listric_offset_excess"] >= 0).all()
