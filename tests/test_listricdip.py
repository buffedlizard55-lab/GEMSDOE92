"""Synthetic geometry checks for the listric offset. No catalogue, no rasters."""
import numpy as np

from gems.listricdip import antithetic_surface, sample_shift, updip_shift_px, updip_surface


def test_sample_shift_paints_crest_on_the_updip_landing():
    field = np.zeros((5, 12), np.float32)
    field[2, 8] = 1.0
    ny = np.zeros_like(field)
    nx = np.ones_like(field)
    landed = sample_shift(field, ny, nx, np.float32(3.0))
    assert landed[2, 5] == np.float32(1.0)
    assert landed[2, 8] == np.float32(0.0)


def test_updip_shift_matches_cover_times_cot():
    cover = np.array([400.0, 500.0, 1100.0], np.float32)
    shift = updip_shift_px(cover, 45.0)
    np.testing.assert_allclose(shift, [4.0, 5.0, 11.0], rtol=1e-5)


def test_updip_surface_peaks_updip_of_a_basement_step():
    h, w = 32, 80
    depth = np.full((h, w), 80.0, np.float32)
    depth[:, 50:] = 500.0
    elev = np.tile(np.linspace(0, 30, w, dtype=np.float32), (h, 1))
    slope = np.full((h, w), 2.0, np.float32)
    slope[:, 44:48] = 6.0
    grav = -depth / 50.0
    grav_hg = np.gradient(grav)[1].astype(np.float32)
    valid = np.ones((h, w), bool)
    out = updip_surface(depth, elev, slope, grav, grav_hg, valid, dip_deg=45.0,
                        cover_min_m=200.0, cover_max_m=800.0)
    # 45° and ~500 m cover => about 5 px up-dip (west) of the step at column 50.
    col = int(np.argmax(out["S_raw"][h // 2]))
    assert 40 <= col <= 48, col
    assert out["S_raw"].shape == depth.shape
    assert np.isfinite(out["S_raw"]).all()


def test_antithetic_requires_reversed_polarity_and_ignores_catalogue():
    h, w = 40, 160
    depth = np.full((h, w), 100.0, np.float32)
    depth[:, 40:48] = np.linspace(100, 800, 8, dtype=np.float32)
    depth[:, 48:62] = 800.0
    depth[:, 62:74] = np.linspace(800, 350, 12, dtype=np.float32)
    depth[:, 74:] = 350.0
    elev = np.tile(np.linspace(20, 0, w, dtype=np.float32), (h, 1))
    grav_hg = np.gradient(depth)[1].astype(np.float32)
    valid = np.ones_like(depth, bool)
    out = antithetic_surface(depth, elev, grav_hg, valid, anti_px=22.0, regional_sigma=12.0)
    assert out["S_raw"].shape == depth.shape
    assert np.isfinite(out["S_pct"]).all()
    assert float(out["oppose"].max()) > 0.5
    # Peak must sit on the reversed flank, not on the master step near column 44.
    peak = int(np.argmax(out["S_raw"][h // 2]))
    assert peak >= 54, peak
