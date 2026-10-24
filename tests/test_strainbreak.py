"""STRAINBREAK surface invariants (pure array math, synthetic fields)."""
import numpy as np

from gems.strainbreak import strainbreak_surface


def _fields(shape=(60, 70), seed=7):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:shape[0], 0:shape[1]]
    elev = (np.sin(x / 9.0) * 40 + rng.normal(0, 1, shape)).astype(np.float32)
    slope = (np.abs(np.cos(x / 9.0)) * 5 + rng.normal(0, 0.2, shape)).astype(np.float32)
    strain = (x / shape[1] * 80 + rng.normal(0, 2, shape)).astype(np.float32)
    return elev, slope, strain


def test_strainbreak_keys_ranges_and_valid_intersection():
    elev, slope, strain = _fields()
    vt = np.ones(elev.shape, bool); vt[:5, :] = False
    vs = np.ones(elev.shape, bool); vs[:, -5:] = False
    out = strainbreak_surface(elev, slope, strain, vt, vs)
    assert set(out) == {"L_raw", "L_pct", "strain_pct", "S_raw", "S_pct", "valid_both"}
    both = vt & vs
    assert np.array_equal(out["valid_both"], both)
    for k in ("L_raw", "L_pct", "strain_pct", "S_raw", "S_pct"):
        a = out[k]
        assert a.shape == elev.shape and np.isfinite(a).all(), k
        assert a.min() >= 0.0 and a.max() <= 1.0, k
    # S is exactly L_raw * strain rank on the intersection, zero outside it
    expect = (out["L_raw"] * out["strain_pct"]).astype(np.float32)
    assert np.allclose(out["S_raw"][both], expect[both])
    assert (out["S_raw"][~both] == 0).all()


def test_strainbreak_monotone_in_strain_for_fixed_terrain():
    elev, slope, _ = _fields()
    vt = np.ones(elev.shape, bool); vs = np.ones(elev.shape, bool)
    ramp = np.tile(np.linspace(1, 100, elev.shape[1], dtype=np.float32), (elev.shape[0], 1))
    out = strainbreak_surface(elev, slope, ramp, vt, vs)
    # strain percentile must increase across the ramp (column means strictly rising)
    col_means = out["strain_pct"].mean(axis=0)
    assert np.all(np.diff(col_means) > 0)
    # and S is L scaled by that percentile: where L>0, S/L equals the strain rank
    m = out["L_raw"] > 0
    assert np.allclose(out["S_raw"][m] / out["L_raw"][m], out["strain_pct"][m], atol=1e-6)
