"""TIPGAP axis: along-strike tip/gap reallocation, one axis only."""

import numpy as np
import pytest
from scipy.ndimage import distance_transform_edt

from gems.variants import Dots, skeleton_endpoints, tipgap, tipgap_targets


def _line_scene():
    """A 40x40 footprint with a 1-px E-W skeleton, catalogue far south."""
    H = W = 40
    fp = np.ones((H, W), dtype=bool)
    skel = np.zeros((H, W), dtype=bool)
    skel[20, 5:25] = True  # endpoints (20,5) west and (20,24) east
    cat = np.zeros((H, W), dtype=bool)
    cat[35, 10:20] = True
    d_cat = distance_transform_edt(~cat)
    # Parent dots every 3 px along the interior of the line, plus a cluster
    ys = np.array([20, 20, 20, 20, 20, 20, 18, 18, 19], dtype=np.int64)
    xs = np.array([8, 11, 14, 17, 20, 23, 14, 15, 14], dtype=np.int64)
    parent = Dots(ys, xs, np.ones(len(ys)))
    return parent, skel, fp, cat, d_cat


def test_skeleton_endpoints_degree_one_and_outward():
    skel = np.zeros((12, 12), dtype=bool)
    skel[6, 2:8] = True  # endpoints (6,2) and (6,7)
    ey, ex, dy, dx = skeleton_endpoints(skel)
    pts = set(zip(ey.tolist(), ex.tolist()))
    assert pts == {(6, 2), (6, 7)}
    for y, x, dyy, dxx in zip(ey, ex, dy, dx):
        if (y, x) == (6, 2):
            assert (int(dyy), int(dxx)) == (0, -1)
        else:
            assert (int(dyy), int(dxx)) == (0, 1)


def test_tipgap_holds_count_and_moves_off_parent():
    parent, skel, fp, cat, d_cat = _line_scene()
    v = tipgap(parent, skel, fp, cat, d_cat, frac=0.22, extend_lo=2, extend_hi=8,
               min_dcat=3.0, min_nn=2.0, value="e8f22")
    assert v.axis == "TIPGAP"
    assert len(v.dots) == len(parent)
    assert v.n_changed >= 1
    # Inherited non-movers stay put.
    assert len(parent.keys & v.dots.keys) == len(parent) - v.n_changed
    # Moved dots are not on the catalogue and sit farther than 3 px.
    moved = v.dots.keys - parent.keys
    for y, x in moved:
        assert not cat[y, x]
        assert d_cat[y, x] > 3.0


def test_tipgap_refuses_empty_frac():
    parent, skel, fp, cat, d_cat = _line_scene()
    with pytest.raises(ValueError, match="zero"):
        tipgap(parent, skel, fp, cat, d_cat, frac=0.001)


def test_tipgap_excludes_catalogue_collar():
    parent, skel, fp, cat, d_cat = _line_scene()
    ys, xs, rank = tipgap_targets(skel, fp, cat, d_cat, extend_lo=2, extend_hi=8, min_dcat=3.0)
    assert len(ys)
    assert not np.any(cat[ys, xs])
    assert np.all(d_cat[ys, xs] > 3.0)
    assert np.all(rank > 0)


def test_tipgap_does_not_change_kept_mass():
    parent, skel, fp, cat, d_cat = _line_scene()
    v = tipgap(parent, skel, fp, cat, d_cat, frac=0.22, extend_lo=2, extend_hi=8)
    assert np.allclose(v.dots.p, 1.0)
    assert abs(float(v.dots.p.sum()) - float(parent.p.sum())) < 1e-9


def test_tipgap_min_parent_dist_rejects_near_parent():
    parent, skel, fp, cat, d_cat = _line_scene()
    v = tipgap(parent, skel, fp, cat, d_cat, frac=0.22, extend_lo=2, extend_hi=8,
               min_parent_dist=3.0, min_nn=2.0)
    moved = v.dots.keys - parent.keys
    from scipy.spatial import cKDTree
    tree = cKDTree(np.c_[parent.ys, parent.xs])
    for y, x in moved:
        d, _ = tree.query([y, x], k=1)
        assert float(d) > 3.0
