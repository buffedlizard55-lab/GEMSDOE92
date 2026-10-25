import numpy as np
import pytest

from gems.eulerfuse import (
    euler_contact_sources,
    joint_euler_features,
    potential_derivatives,
)


def synthetic_fields(n=81):
    y, x = np.mgrid[:n, :n]
    rtp = (
        np.arctan2(x - 39.0, 4.0)
        + 0.7 * np.arctan2((x + y) - 82.0, 6.0)
        + 0.2 * np.exp(-((x - 20.0) ** 2 + (y - 55.0) ** 2) / 200.0)
    ).astype(np.float32)
    grav = (
        0.8 * np.arctan2(x - 41.0, 5.0)
        + 0.6 * np.arctan2((x + y) - 85.0, 8.0)
    ).astype(np.float32)
    valid = np.ones((n, n), dtype=bool)
    valid[:4] = valid[-4:] = False
    valid[:, :4] = valid[:, -4:] = False
    return rtp, grav, valid


def test_potential_derivatives_are_finite_and_masked():
    rtp, _, valid = synthetic_fields()
    fx, fy, fz, strength = potential_derivatives(rtp, valid, sigma_px=1.2)
    for arr in (fx, fy, fz, strength):
        assert arr.shape == valid.shape
        assert arr.dtype == np.float32
        assert np.isfinite(arr).all()
        assert np.all(arr[~valid] == 0)
    assert np.all(strength >= 0)
    assert float(strength[valid].max()) > 0


def test_euler_contact_sources_are_deterministic_and_bounded():
    rtp, _, valid = synthetic_fields()
    kwargs = dict(
        sigma_px=1.2,
        window_radius_px=4,
        strength_quantile=0.50,
        max_centres=1_000,
        batch_size=200,
    )
    one = euler_contact_sources(rtp, valid, **kwargs)
    two = euler_contact_sources(rtp, valid, **kwargs)
    assert one.n_centres_tested > 0
    assert one.n_solutions > 0
    np.testing.assert_array_equal(one.surface, two.surface)
    np.testing.assert_array_equal(one.depth_px, two.depth_px)
    assert np.isfinite(one.surface).all()
    assert float(one.surface.min()) >= 0.0
    assert float(one.surface.max()) <= 1.0
    assert np.all(one.surface[~valid] == 0)
    assert np.all(one.depth_px[one.solution_mask] >= 0.5)
    assert np.all(one.depth_px[one.solution_mask] <= 12.0)


def test_joint_features_have_expected_contract_without_catalogue_input():
    rtp, grav, valid = synthetic_fields()
    depth_m = np.full(valid.shape, 400.0, dtype=np.float32)
    result = joint_euler_features(
        rtp,
        grav,
        depth_m,
        valid,
        sigma_px=1.2,
        window_radius_px=4,
        strength_quantile=0.50,
        max_centres=1_000,
    )
    assert result["diagnostics"]["mag_solutions"] > 0
    assert result["diagnostics"]["grav_solutions"] > 0
    for name in (
        "mag_euler",
        "grav_euler",
        "joint_colocation",
        "depth_agreement",
        "base_consistency",
        "joint_euler",
    ):
        arr = result[name]
        assert arr.shape == valid.shape
        assert arr.dtype == np.float32
        assert np.isfinite(arr).all()
        assert float(arr.min()) >= 0.0
        assert float(arr.max()) <= 1.0
        assert np.all(arr[~valid] == 0)
    assert np.any(result["joint_euler"] > 0)


def test_invalid_parameters_fail_closed():
    rtp, _, valid = synthetic_fields(31)
    with pytest.raises(ValueError):
        potential_derivatives(rtp, valid, sigma_px=0)
    with pytest.raises(ValueError):
        euler_contact_sources(rtp, valid, window_radius_px=1)
    with pytest.raises(ValueError):
        euler_contact_sources(rtp, valid, min_depth_px=2, max_depth_px=1)
    with pytest.raises(ValueError):
        euler_contact_sources(rtp, valid, residual_scale=0)
    with pytest.raises(ValueError):
        potential_derivatives(rtp, valid[:-1], sigma_px=1)
    with pytest.raises(ValueError):
        joint_euler_features(rtp, rtp[:-1], rtp, valid)
