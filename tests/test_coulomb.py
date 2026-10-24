"""Unit tests for gems/coulomb.py (COULOMB session 2026-10-24).

Locks the pre-registered design constants, the orientation-projection math on
synthetics with known answers, sentinel/NaN safety, and determinism. No
competition data required; all inputs are synthetic.
"""
import numpy as np

from gems.coulomb import (
    ALPHA_EXT_DEG,
    EXT_MIX,
    NW_CENTER_DEG,
    NW_SIGMA_DEG,
    coulomb_opening,
    coulomb_surface,
    magtilt_contact,
    mtedge_dilat,
    seismo_prior,
)


def _field(value, shape=(16, 16)):
    return np.full(shape, float(value), dtype=np.float32)


def test_design_constants_match_preregistration():
    assert ALPHA_EXT_DEG == 100.0
    assert NW_CENTER_DEG == 140.0
    assert NW_SIGMA_DEG == 25.0
    assert EXT_MIX == 0.65


def test_opening_optimal_strike_beats_transverse_strike():
    # Optimal normal-fault strike: normal (strike+90) == alpha_ext == 100 -> strike 10.
    # Transverse E-W strike 100 -> normal 10/190 -> delta 90 deg -> ori 0.
    strike = np.array([[10.0, 10.0, 100.0, 100.0]], dtype=np.float32)
    dil = np.array([[1.0, 8.0, 1.0, 8.0]], dtype=np.float32)
    shr = _field(0.0, (1, 4))
    out = coulomb_opening(strike, dil, shr, np.ones((1, 4), bool), ext_mix=1.0)
    assert (out["O_ext"][0, :2] > 0.0).all()
    assert (out["O_ext"][0, 2:] < 1e-6).all()
    assert (out["opening_ori"][0, :2] == 1.0).all()
    assert (np.abs(out["opening_ori"][0, 2:]) < 1e-6).all()


def test_opening_contracting_crust_scores_zero():
    strike = _field(10.0)
    dil = _field(-3.0)  # contraction: no opening
    shr = _field(0.0)
    out = coulomb_opening(strike, dil, shr, np.ones((16, 16), bool), ext_mix=1.0)
    assert (out["O_ext"] == 0.0).all()
    assert (out["O_raw"] == 0.0).all()


def test_shear_term_prefers_nw_set():
    strike = np.array([[140.0, 0.0]], dtype=np.float32)
    dil = _field(0.0, (1, 2))
    shr = _field(7.0, (1, 2))
    out = coulomb_opening(strike, dil, shr, np.ones((1, 2), bool), ext_mix=0.0)
    assert out["nw_weight"][0, 0] == 1.0
    assert out["O_shear"][0, 0] > out["O_shear"][0, 1] > 0.0
    # N-S strike is 40 deg (mod 180) from the 140-deg center.
    assert abs(out["nw_weight"][0, 1] - np.exp(-0.5 * (40.0 / 25.0) ** 2)) < 1e-6


def test_opening_deterministic_and_bounded():
    rng = np.random.default_rng(7)
    strike = (rng.random((24, 24)) * 180).astype(np.float32)
    dil = (rng.random((24, 24)) * 10 - 2).astype(np.float32)
    shr = (rng.random((24, 24)) * 20).astype(np.float32)
    vb = np.ones((24, 24), bool)
    a = coulomb_opening(strike, dil, shr, vb)
    b = coulomb_opening(strike, dil, shr, vb)
    assert np.array_equal(a["O_raw"], b["O_raw"])
    assert np.isfinite(a["O_raw"]).all()
    assert a["O_raw"].min() >= 0.0 and a["O_raw"].max() <= 1.0
    assert a["O_pct"].min() >= 0.0 and a["O_pct"].max() <= 1.0


def test_opening_sentinel_and_nan_safe():
    strike = _field(10.0)
    dil = _field(5.0)
    shr = _field(7.0)
    dil[0, 0] = np.float32(-3.4028235e38)
    shr[1, 1] = np.nan
    vb = np.ones((16, 16), bool)
    vb[2, 2] = False
    out = coulomb_opening(strike, dil, shr, vb)
    assert np.isfinite(out["O_raw"]).all()
    assert out["O_raw"][2, 2] == 0.0


def test_seismo_prior_shape_and_range():
    rng = np.random.default_rng(3)
    shape = (20, 20)
    deq = (rng.random(shape) * 8000).astype(np.float32)
    ieq = (rng.random(shape) * 3000).astype(np.float32)
    s2i = (rng.random(shape) * 50).astype(np.float32)
    out = seismo_prior(deq, ieq, s2i, np.ones(shape, bool))
    assert out["seismo_raw"].shape == shape
    assert np.isfinite(out["seismo_pct"]).all()
    assert out["seismo_pct"].min() >= 0.0 and out["seismo_pct"].max() <= 1.0
    # Closer to quakes (smaller deq) must rank higher, all else equal.
    d2 = deq.copy()
    d2[0, 0] = 0.0
    out2 = seismo_prior(d2, ieq, s2i, np.ones(shape, bool))
    assert out2["prox"][0, 0] == out2["prox"].max()


def test_magtilt_contact_finite_and_gated():
    rng = np.random.default_rng(5)
    shape = (24, 24)
    hg = (rng.random(shape) * 100).astype(np.float32)
    vg = (rng.random(shape) * 2 - 1).astype(np.float32)
    rtp = (rng.random(shape) * 200 - 100).astype(np.float32)
    out = magtilt_contact(hg, vg, rtp, np.ones(shape, bool))
    assert np.isfinite(out["magtilt_raw"]).all()
    assert out["magtilt_raw"].min() >= 0.0
    assert out["magtilt_pct"].max() <= 1.0


def test_mtedge_dilat_contraction_suppresses():
    rng = np.random.default_rng(9)
    shape = (20, 20)
    cs = (rng.random(shape) * 4).astype(np.float32)
    dil_pos = (rng.random(shape) * 10).astype(np.float32)
    vb = np.ones(shape, bool)
    assert mtedge_dilat(cs, dil_pos, vb)["mtedge_raw"].max() > 0.0
    # Mixed-sign dilatation: every positive cell must outrank every negative cell,
    # because negatives are clipped to a common 0 before ranking.
    dil_mixed = (np.linspace(-5.0, 5.0, 400).reshape(shape)).astype(np.float32)
    pct = mtedge_dilat(cs, dil_mixed, vb)["dil_pos_pct"]
    assert pct[dil_mixed > 0].min() >= pct[dil_mixed < 0].max()
    assert (pct[dil_mixed < 0] == pct[dil_mixed < 0].max()).all()


def test_coulomb_surface_end_to_end_synthetic():
    rng = np.random.default_rng(11)
    shape = (48, 48)
    det_elev = (rng.random(shape) * 400 - 100).astype(np.float32)
    det_elev[24:, :] += 6.0  # a sustained E-W step: strike 90
    args = dict(
        det_elev=det_elev,
        det_elev_slope=(rng.random(shape) * 10).astype(np.float32),
        depth_to_base=(rng.random(shape) * 800 + 20).astype(np.float32),
        grav_slope=(rng.random(shape) * 0.3).astype(np.float32),
        rtp=(rng.random(shape) * 300 - 150).astype(np.float32),
        dilaterate=(rng.random(shape) * 20 - 5).astype(np.float32),
        shearrate=(rng.random(shape) * 30).astype(np.float32),
        second_inv=(rng.random(shape) * 50).astype(np.float32),
        deq=(rng.random(shape) * 8000).astype(np.float32),
        ieq=(rng.random(shape) * 3000).astype(np.float32),
        footprint=np.ones(shape, bool),
    )
    out = coulomb_surface(**args)
    for key in ("S_free_raw", "S_open_raw", "S_seismo_raw", "O_coulomb", "H_apron",
                "R_rtp_tilt", "R_scarp_rel", "strike_joint", "seismo_pct"):
        assert key in out
        assert np.isfinite(out[key]).all(), key
    for key in ("S_free_pct", "S_open_pct", "S_seismo_pct", "O_pct"):
        assert out[key].min() >= 0.0 and out[key].max() <= 1.0, key
    for key in ("ridge_free", "ridge_open", "ridge_seismo"):
        assert out[key].dtype == bool
        assert out[key].any(), key
    # Fusion must differ from the base surface (seismo prior is non-uniform).
    assert not np.array_equal(out["S_seismo_raw"], out["S_free_raw"])
    # Apron gate must differ from the ungated surface.
    assert not np.array_equal(out["S_open_raw"], out["S_free_raw"])
