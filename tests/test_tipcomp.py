"""TIPCOMP (H-92F1) unit tests: endpoint geometry must be catalogue-only."""
import numpy as np

from gems.tipcomp import coverage_complement, endpoints, tip_continuation_field


def test_endpoints_of_open_polyline():
    m = np.zeros((21, 21), bool)
    m[10, 3:15] = True
    ep = endpoints(m)
    assert ep.sum() == 2 and ep[10, 3] and ep[10, 14]


def test_tip_field_extends_along_strike_not_across():
    m = np.zeros((61, 61), bool)
    m[30, 10:31] = True  # horizontal trace ending at x=30
    f = tip_continuation_field(m)
    assert f[30, 38] > 0.1          # along-strike continuation
    assert f[38, 30] < f[30, 38]     # across-strike is weaker
    assert f[30, 20] == 0.0          # suppressed on/near the catalogue
    assert np.isfinite(f).all() and f.min() >= 0.0


def test_tip_field_empty_catalogue_is_zero():
    f = tip_continuation_field(np.zeros((9, 9), bool))
    assert f.shape == (9, 9) and float(f.max()) == 0.0


def test_coverage_complement_flags_uncovered_ridge():
    ridge = np.full((21, 21), 9.0, dtype=np.float32)
    ridge[10, :] = 0.0
    peak = np.zeros((21, 21), bool); peak[10, 2] = True
    c = coverage_complement(ridge, [peak])
    assert c[10, 15] == 1.0 and c[10, 3] == 0.0 and c[0, 15] == 0.0
