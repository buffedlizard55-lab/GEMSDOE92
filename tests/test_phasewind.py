import numpy as np
import pytest

from gems.phasewind import phase_winding_scale, persistent_surface


def test_complex_gradient_winding_detects_an_isolated_extremum():
    y, x = np.mgrid[-48:49, -48:49]
    image = (x * x + y * y).astype(np.float32)
    valid = np.ones(image.shape, bool)
    a = phase_winding_scale(image, valid, sigma_px=2.0)
    center = (48, 48)
    assert a["charge"][center] == pytest.approx(1.0, abs=0.05)
    assert a["charge_confidence"][center] > 0.95
    assert a["feature"].max() > 0.0
    assert np.isfinite(a["feature"]).all()
    assert a["feature"].min() >= 0.0
    assert a["feature"].max() <= 1.0


def test_linear_field_has_no_phase_winding_feature():
    y, x = np.mgrid[:96, :96]
    image = x.astype(np.float32)
    valid = np.ones(image.shape, bool)
    a = phase_winding_scale(image, valid, sigma_px=2.0)
    assert not np.any(a["feature"] > 0.0)


def test_phase_winding_rejects_bad_inputs_and_masks_sentinels():
    image = np.ones((20, 20), np.float32)
    with pytest.raises(ValueError, match="matching 2-D"):
        phase_winding_scale(image, np.ones((20, 19), bool), 2.0)
    with pytest.raises(ValueError, match="positive"):
        phase_winding_scale(image, np.ones_like(image, bool), 0.0)
    image[10, 10] = -3.4e38
    valid = np.ones_like(image, bool)
    a = phase_winding_scale(image, valid, sigma_px=1.0)
    assert not a["valid"][10, 10]
    assert not a["feature"][10, 10]
    assert np.isfinite(a["feature"]).all()


def _response(charge, feature):
    return {"charge": np.asarray(charge, np.float32), "feature": np.asarray(feature, np.float32)}


def test_persistent_surface_requires_same_signed_charge_across_scales():
    shape = (5, 5)
    q2 = np.ones(shape, np.float32)
    q4 = np.ones(shape, np.float32)
    q8 = -np.ones(shape, np.float32)
    f2 = np.full(shape, 0.8, np.float32)
    f4 = np.full(shape, 0.6, np.float32)
    f8 = np.full(shape, 0.9, np.float32)
    scales = {2.0: _response(q2, f2), 4.0: _response(q4, f4), 8.0: _response(q8, f8)}
    two_scale = persistent_surface(scales, ((2.0, 4.0),))
    all_scales = persistent_surface(scales)
    assert np.allclose(two_scale, 0.6)
    assert np.allclose(all_scales, 0.6)


def test_persistent_surface_validates_pairs_and_shapes():
    scales = {
        2.0: _response(np.ones((2, 2)), np.ones((2, 2))),
        4.0: _response(np.ones((3, 2)), np.ones((3, 2))),
    }
    with pytest.raises(ValueError, match="shape mismatch"):
        persistent_surface(scales)
    matching = {2.0: _response(np.ones((2, 2)), np.ones((2, 2))),
                4.0: _response(np.ones((2, 2)), np.ones((2, 2)))}
    with pytest.raises(ValueError, match="duplicate scale pair"):
        persistent_surface(matching, ((2.0, 4.0), (4.0, 2.0)))
