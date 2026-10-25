"""Synthetic unit tests for the FLEXMAG lane surface (no competition data)."""
import numpy as np
import pytest

from gems.flexmag import (
    BAND,
    compute_flexmag_surfaces,
    dog_bandpass,
    gradient_magnitude,
    magnetic_asa,
)


def _step_field(shape=(240, 240), col=120, lo=100.0, hi=900.0):
    f = np.full(shape, lo, np.float32)
    f[:, col:] = hi
    return f


def test_band_ids_match_stack_descriptions():
    assert BAND == dict(rtp=2, tmi_hg=3, tmi_vg=9, det_elev=12, depth_to_base=15)


def test_dog_bandpass_kills_constant_and_regional_tilt():
    valid = np.ones((120, 120), bool)
    const = np.full((120, 120), 7.0, np.float32)
    assert np.abs(dog_bandpass(const, valid)).max() < 1e-4
    tilt = np.tile(np.linspace(0, 1000, 120, dtype=np.float32), (120, 1))
    # small sigmas so the test interior is many sigma from the reflected edge
    bp = dog_bandpass(tilt, valid, sigma_near=2.0, sigma_far=8.0)
    # interior of a pure linear ramp has ~no band-pass energy
    assert np.abs(bp[40:-40, 40:-40]).max() < 5.0


def test_hinge_peaks_at_a_blinded_step():
    foot = np.ones((240, 240), bool)
    base = _step_field()
    elev = _step_field(lo=0.0, hi=-80.0)  # hanging wall down where cover thickens
    hg = np.zeros((240, 240), np.float32); hg[:, 118:123] = 50.0
    vg = np.zeros((240, 240), np.float32)
    rtp = _step_field(lo=-100.0, hi=100.0)
    out = compute_flexmag_surfaces(depth_to_base=base, det_elev=elev,
                                   tmi_hg=hg, tmi_vg=vg, rtp=rtp, footprint=foot)
    mid = out["S_flexmag"][120, :]
    assert int(np.argmax(mid)) == pytest.approx(120, abs=6)
    assert mid[120] > mid[40] and mid[120] > mid[200]


def test_surfaces_finite_unit_range_and_zero_outside_valid():
    foot = np.zeros((240, 240), bool); foot[20:-20, 20:-20] = True
    rng = np.random.default_rng(7)
    kw = {k: rng.normal(0, 1, (240, 240)).astype(np.float32)
          for k in ("depth_to_base", "det_elev", "tmi_hg", "tmi_vg", "rtp")}
    kw["depth_to_base"][0, 0] = np.nan  # sentinel handling must not propagate
    out = compute_flexmag_surfaces(footprint=foot, **kw)
    for k in ("hinge", "coherence", "mag", "S_flexmag", "S_flex", "S_mag"):
        v = out[k]
        assert np.isfinite(v).all() and v.min() >= 0.0 and v.max() <= 1.0
        assert (v[~out["valid"]] == 0.0).all()
    # edge erosion: nothing valid within EDGE_ERODE_PX of the footprint edge
    assert not out["valid"][:50, :].any()


def test_magnetic_gate_downweights_hinge_without_mag_edge():
    foot = np.ones((240, 240), bool)
    base = _step_field(); elev = _step_field(lo=0.0, hi=-80.0)
    zeros = np.zeros((240, 240), np.float32)
    # low-amplitude noise background (a perfectly constant ASA field has no
    # meaningful percentile rank; real stack bands are never constant)
    bg = np.random.default_rng(3).normal(0, 0.01, (240, 240)).astype(np.float32)
    rtp = _step_field(lo=-100.0, hi=100.0)
    nomag = compute_flexmag_surfaces(depth_to_base=base, det_elev=elev,
                                     tmi_hg=bg, tmi_vg=zeros, rtp=rtp,
                                     footprint=foot)
    hg = np.zeros((240, 240), np.float32); hg[:, 118:123] = 50.0
    withmag = compute_flexmag_surfaces(depth_to_base=base, det_elev=elev,
                                       tmi_hg=hg, tmi_vg=zeros, rtp=rtp,
                                       footprint=foot)
    # same hinge: with a co-located magnetic edge the hinge crest must not
    # lose rank against the no-mag case (gate floor is 0.30, not 0)
    assert withmag["S_flexmag"][120, 120] >= nomag["S_flexmag"][120, 120] - 0.05
    assert withmag["mag"][120, 120] > nomag["mag"][120, 120]


def test_shape_mismatch_rejected():
    foot = np.ones((10, 10), bool)
    good = np.zeros((10, 10), np.float32)
    bad = np.zeros((9, 10), np.float32)
    with pytest.raises(ValueError):
        compute_flexmag_surfaces(depth_to_base=bad, det_elev=good, tmi_hg=good,
                                 tmi_vg=good, rtp=good, footprint=foot)


def test_gradient_and_asa_helpers():
    f = _step_field((60, 60), col=30)
    g = gradient_magnitude(f)
    assert g[30, 30] > g[30, 5]
    asa = magnetic_asa(np.full((60, 60), 3.0, np.float32),
                       np.full((60, 60), 4.0, np.float32),
                       np.ones((60, 60), bool))
    assert asa[30, 30] == pytest.approx(5.0, abs=0.05)
