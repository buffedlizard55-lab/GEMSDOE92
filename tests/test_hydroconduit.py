"""Unit tests for the label-free HYDROCONDUIT surface module."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

from gems.hydroconduit import (
    coherence_and_strike_deg,
    cross_strike_monotonicity,
    gdr_blind_thermal_plume,
    hydroconduit_surface,
    rtp_tilt_and_demag,
)


def test_coherence_and_strike_azimuth_quadrants():
    h, w = 64, 64
    valid = np.ones((h, w), dtype=bool)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)

    # Pure East-West gradient -> North-South strike (0 deg)
    coh_ns, az_ns = coherence_and_strike_deg(xx * 5.0, valid)
    assert float(coh_ns[32, 32]) > 0.99
    assert min(abs(float(az_ns[32, 32]) - 0.0), abs(float(az_ns[32, 32]) - 180.0)) < 1e-2

    # Pure North-South gradient -> East-West strike (90 deg)
    coh_ew, az_ew = coherence_and_strike_deg(yy * 5.0, valid)
    assert float(coh_ew[32, 32]) > 0.99
    assert abs(float(az_ew[32, 32]) - 90.0) < 1e-2

    # SE gradient (gx=+1, gy=+1) -> NE-SW strike (45 deg)
    coh_ne, az_ne = coherence_and_strike_deg((xx + yy) * 5.0, valid)
    assert float(coh_ne[32, 32]) > 0.99
    assert abs(float(az_ne[32, 32]) - 45.0) < 1e-2


def test_cross_strike_monotonicity_separates_step_from_v_gully():
    h, w = 80, 80
    valid = np.ones((h, w), dtype=bool)
    _, xx = np.mgrid[0:h, 0:w].astype(np.float32)

    # Monotonic normal-fault scarp step centered at x=40
    scarp = 40.0 * np.tanh((xx - 40.0) / 2.5)
    mu_scarp = cross_strike_monotonicity(scarp, valid)

    # Symmetric V-shaped incised stream canyon centered at x=40
    gully = 10.0 * np.abs(xx - 40.0)
    mu_gully = cross_strike_monotonicity(gully, valid)

    assert float(mu_scarp[40, 40]) > 0.90
    assert float(mu_gully[40, 40]) < 0.15
    assert np.all((mu_scarp >= 0.0) & (mu_scarp <= 1.0))


def test_rtp_tilt_and_demag_finite_in_unit_interval():
    rng = np.random.default_rng(42)
    h, w = 64, 64
    valid = np.ones((h, w), dtype=bool)
    valid[:4, :] = False
    _, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # Linear magnetic trough along x=32 plus step along x=16
    rtp = 100.0 * np.tanh((xx - 16.0) / 2.0) - 80.0 * np.exp(-0.5 * ((xx - 32.0) / 1.5) ** 2)
    rtp += rng.normal(0.0, 0.5, size=(h, w)).astype(np.float32)
    rtp[0, 0] = np.nan

    res = rtp_tilt_and_demag(rtp, valid)
    assert np.isfinite(res["rtp_conduit_pct"]).all()
    assert float(res["rtp_conduit_pct"].min()) >= 0.0
    assert float(res["rtp_conduit_pct"].max()) <= 1.0
    # Trough axis at x=32 should exceed background x=52
    assert float(res["demag_trough"][32, 32]) > float(res["demag_trough"][32, 52])


def test_gdr_blind_thermal_plume_handles_blind_chem_and_hot_whitespace(tmp_path: Path):
    csv_file = tmp_path / "gdr.csv"
    pd.DataFrame([
        # Blind chemical geothermometer well: cold surface temp (22 C), high quartz (145 C)
        {"row": 20, "col": 25, "temp_c": 22.0, "thermalclass": "Cold",
         "geothermquartz_c": 145.0, "geothermchalc_c": np.nan, "geothermcat_c": np.nan},
        # Trailing-space 'Hot ' class anomaly
        {"row": 45, "col": 45, "temp_c": np.nan, "thermalclass": "Hot ",
         "geothermquartz_c": np.nan, "geothermchalc_c": np.nan, "geothermcat_c": np.nan},
        # Non-thermal background well
        {"row": 10, "col": 10, "temp_c": 14.0, "thermalclass": "Cold",
         "geothermquartz_c": 40.0, "geothermchalc_c": 35.0, "geothermcat_c": 30.0},
    ]).to_csv(csv_file, index=False)

    valid = np.ones((60, 60), dtype=bool)
    out = gdr_blind_thermal_plume(csv_file, (60, 60), valid, sigma_px=4.0)
    assert out["n_thermal_pixels"] == 2
    assert out["n_blind_geotherm_pixels"] == 1
    plume = out["plume_pct"]
    assert isinstance(plume, np.ndarray)
    assert float(plume[20, 25]) > 0.95
    assert float(plume[45, 45]) > 0.90
    assert float(plume[0, 59]) < 0.20


def test_hydroconduit_surface_deterministic_and_bounded():
    h, w = 72, 72
    fp = np.ones((h, w), dtype=bool)
    fp[:3, :] = False
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)

    det_elev = -50.0 + 30.0 * np.tanh((xx - 36.0) / 2.5)
    det_elev[0, 0] = -1e38
    det_slope = 2.0 + 4.0 * np.exp(-0.5 * ((xx - 36.0) / 2.0) ** 2)
    depth_base = np.full((h, w), 180.0, dtype=np.float32)
    s2i = 20.0 + 5.0 * (yy / h)
    dil = 6.0 + 3.0 * (xx / w)
    rtp = -80.0 * np.exp(-0.5 * ((xx - 36.0) / 2.0) ** 2)
    cond = np.full((h, w), 3.1, dtype=np.float32)
    rad_k = np.full((h, w), 160, dtype=np.uint8)
    rad_th = np.full((h, w), 110, dtype=np.uint8)
    gdr_pct = np.exp(-0.5 * ((xx - 36.0) / 8.0) ** 2).astype(np.float32)

    res1 = hydroconduit_surface(
        det_elev=det_elev, det_elev_slope=det_slope, depth_to_base=depth_base,
        geod_2ndinv=s2i, geod_dilaterate=dil, rtp=rtp, cond_surf=cond,
        rad_k=rad_k, rad_th=rad_th, gdr_plume_pct=gdr_pct, footprint=fp,
    )
    res2 = hydroconduit_surface(
        det_elev=det_elev, det_elev_slope=det_slope, depth_to_base=depth_base,
        geod_2ndinv=s2i, geod_dilaterate=dil, rtp=rtp, cond_surf=cond,
        rad_k=rad_k, rad_th=rad_th, gdr_plume_pct=gdr_pct, footprint=fp,
    )
    for key in ("S_pied_pct", "S_hydro_pct", "hab_pied_pct", "hab_hydro_pct"):
        arr = res1[key]
        assert np.array_equal(arr, res2[key])
        assert np.isfinite(arr).all()
        assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
        assert np.all(arr[~fp] == 0.0)


def test_cross_strike_monotonicity_float32_ulp_at_width_3292():
    # Regression test: at width >= 2048, float32 ulp is 0.000244 > 0.0001
    h, w = 8, 3292
    valid = np.ones((h, w), dtype=bool)
    _, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    mu = cross_strike_monotonicity(xx * 2.0, valid)
    assert mu.shape == (h, w)
    assert np.isfinite(mu).all()
    assert float(mu.min()) >= 0.0 and float(mu.max()) <= 1.0

