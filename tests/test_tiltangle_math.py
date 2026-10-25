"""Regression for the archived TILTANGLE operator's actual derivative math.

This is a tiny synthetic unit test, not a geological experiment or holdout.
The derivative angle is not the physical dip of a fault/contact.
"""
from __future__ import annotations

import numpy as np

from gems import tiltangle


def test_vertical_derivative_is_downweighted_not_called_steep_fault(monkeypatch):
    horizontal = np.full((2, 2), 3.0, dtype=np.float32)
    vertical = np.array([[0.0, 4.0], [0.0, 4.0]], dtype=np.float32)
    stack = {11: vertical, 13: np.zeros_like(horizontal), 18: horizontal}
    monkeypatch.setattr(tiltangle, 'read_stack_band', lambda _path, band: stack[band])

    result = tiltangle.lane_surface('synthetic-no-geotiff', np.ones((2, 2), bool))
    assert np.all(result['valid'])
    np.testing.assert_allclose(result['hgm'], horizontal)
    np.testing.assert_allclose(result['tilt'][0], [0, np.degrees(np.arctan2(4, 3))], atol=1e-5)
    np.testing.assert_allclose(result['s_raw'][0], [3.0, 3.0 * (3.0 / 5.0) ** 2], atol=1e-5)
    assert result['s_raw'][0, 1] < result['s_raw'][0, 0]
