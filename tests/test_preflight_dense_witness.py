import importlib.util
from pathlib import Path

import numpy as np
import pytest

spec = importlib.util.spec_from_file_location(
    'preflight', Path(__file__).resolve().parents[1] / 'scripts/preflight_dense_witness.py')
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


def test_universal_stop_all_footprint():
    footprint = np.array([[False, True, True], [True, False, True]])
    witness = np.array([[0, 0.1, 1], [0.01, 0, 0.7]])
    assert preflight.universal_stop(footprint, witness)
    witness[1, 0] = 0
    assert not preflight.universal_stop(footprint, witness)


def test_reject_invalid_witness():
    footprint = np.ones((2, 2), bool)
    with pytest.raises(ValueError):
        preflight.universal_stop(footprint, np.ones((2, 3)))
    with pytest.raises(ValueError):
        preflight.universal_stop(footprint, np.array([[1., np.nan], [1., 1.]]))
    with pytest.raises(ValueError):
        preflight.universal_stop(np.zeros((2, 2), bool), np.ones((2, 2)))
