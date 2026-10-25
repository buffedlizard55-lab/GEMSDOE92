"""VARIO feature operators: exact small-grid checks, no catalogue inputs."""
import numpy as np

from gems.vario import (
    NEW_FEATURE_NAMES,
    directional_semivariance,
    mt_changepoint_constcover,
    semivariogram_features,
)


def _valid(shape):
    return np.ones(shape, bool)


def test_semivariance_constant_field_is_zero():
    z = np.full((31, 29), 7.0, np.float32)
    sv = directional_semivariance(z, _valid(z.shape), lag=2)
    assert np.allclose(sv["gmean"], 0.0)
    f = semivariogram_features(z, _valid(z.shape))
    assert set(f) == {"sv_aniso_l2", "sv_aniso_l4", "sv_lagratio"}
    assert np.allclose(f["sv_aniso_l2"], 0.0)
    assert np.isfinite(f["sv_lagratio"]).all()


def test_semivariance_stripes_are_anisotropic():
    # Vertical stripes: E-W lag crosses stripes (high gamma), N-S does not.
    yy, xx = np.mgrid[0:61, 0:61]
    z = (100.0 * np.sin(2 * np.pi * xx / 8.0)).astype(np.float32)
    f = semivariogram_features(z, _valid(z.shape))
    core = f["sv_aniso_l2"][15:-15, 15:-15]
    assert core.mean() > 0.2  # strongly anisotropic fabric
    assert (f["sv_aniso_l2"] >= 0).all() and (f["sv_aniso_l2"] <= 2).all()
    assert (f["sv_lagratio"] >= 0).all() and (f["sv_lagratio"] <= 5).all()


def test_semivariance_isotropic_noise_low_anisotropy():
    rng = np.random.default_rng(3)
    from scipy.ndimage import gaussian_filter
    z = gaussian_filter(rng.standard_normal((61, 61)).astype(np.float32), 2.0)
    f = semivariogram_features(z, _valid(z.shape))
    core = f["sv_aniso_l4"][15:-15, 15:-15]
    yy, xx = np.mgrid[0:61, 0:61]
    stripes = (100.0 * np.sin(2 * np.pi * xx / 8.0)).astype(np.float32)
    fs = semivariogram_features(stripes, _valid(z.shape))
    assert core.mean() < fs["sv_aniso_l4"][15:-15, 15:-15].mean()


def test_mt_changepoint_discounts_cover_gradient():
    # Identical conductivity step in two halves; left half has flat cover,
    # right half has a strong cover-depth step at the same place.  The
    # constant-cover half must score higher.
    h, w = 41, 81
    cond = np.ones((h, w), np.float32)
    cond[:, 20:30] = 2.0
    cond[:, 60:70] = 2.0
    depth = np.full((h, w), 300.0, np.float32)
    depth[:, 60:70] = 3000.0  # cover changes where the right MT step is
    f = mt_changepoint_constcover(cond, depth, _valid((h, w)))
    left = f[10:-10, 18:32].max()
    right = f[10:-10, 58:72].max()
    assert left > right > 0
    assert np.isfinite(f).all() and (f >= 0).all()


def test_new_feature_names_count():
    assert len(NEW_FEATURE_NAMES) == 9
    assert len(set(NEW_FEATURE_NAMES)) == 9
