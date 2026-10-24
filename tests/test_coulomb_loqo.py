"""Unit tests for the COULOMB-LOQO lane (gems/coulomb_loqo.py)."""
from __future__ import annotations

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems.coulomb_loqo import (  # noqa: E402
    FEATURE_NAMES,
    TOPO_ONLY_INDICES,
    build_crest_surface,
    compute_feature_stack,
    coulomb_tendencies,
    cross_physics_axial_order,
    fit_predict_loqo,
    gdr_blind_thermal_features,
    hessian_ridge_strength,
)
from gems57.holdout import quadrant_ids  # noqa: E402


def test_hessian_ridge_strength_detects_crest_not_trough():
    h, w = 48, 48
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # Positive convex-up ridge at col 16, negative trough at col 34
    field = np.exp(-0.5 * ((xx - 16.0) / 1.5) ** 2) - np.exp(-0.5 * ((xx - 34.0) / 1.5) ** 2)
    valid = np.ones((h, w), dtype=bool)
    r = hessian_ridge_strength(field, valid, sigma=1.2)
    assert r.dtype == np.float32
    assert np.isfinite(r).all()
    assert float(r[24, 16]) > 0.20
    assert float(r[24, 34]) == 0.0


def test_cross_physics_axial_order_is_180deg_periodic_and_drops_on_orthogonal():
    valid = np.ones((16, 16), dtype=bool)
    th1 = np.full((16, 16), 15.0, dtype=np.float32)
    th2_same = np.full((16, 16), 195.0, dtype=np.float32)  # 15 + 180 deg = identical fault strike
    th2_orth = np.full((16, 16), 105.0, dtype=np.float32)  # orthogonal by 90 deg
    w = np.ones((16, 16), dtype=np.float32)

    r_same, comp_same = cross_physics_axial_order([th1, th2_same], [w, w], valid)
    r_orth, _ = cross_physics_axial_order([th1, th2_orth], [w, w], valid)
    assert np.allclose(r_same, 1.0, atol=1e-5)
    assert np.allclose(comp_same, 15.0, atol=1e-4)
    assert np.allclose(r_orth, 0.0, atol=1e-5)


def test_coulomb_tendencies_peak_at_n15e_and_conjugate_shear():
    valid = np.ones((4,), dtype=bool)
    strikes = np.array([15.0, 105.0, 60.0, 150.0], dtype=np.float32)
    shear = np.full((4,), 20.0, dtype=np.float32)
    dil = np.full((4,), 10.0, dtype=np.float32)

    t_dil, t_slip = coulomb_tendencies(strikes, shear, dil, valid)
    # Normal dilation maximizes at N15E (idx 0) and vanishes at N105E (idx 1)
    assert t_dil[0] == pytest.approx(15.0, abs=1e-4)
    assert t_dil[1] == pytest.approx(0.0, abs=1e-5)
    # Conjugate Riedel shear (60 deg and 150 deg = +/-45 deg from N15E) retains strong slip tendency
    assert t_slip[2] == pytest.approx(0.85 * 20.0, abs=1e-4)
    assert t_slip[3] == pytest.approx(0.85 * 20.0, abs=1e-4)


def test_gdr_blind_thermal_ignores_poisoned_dist_known_fault_px_and_strips_hot_space(tmp_path):
    valid = np.ones((32, 32), dtype=bool)
    df1 = pd.DataFrame({
        "row": [10, 20, 25],
        "col": [10, 20, 25],
        "thermalclass": ["Hot ", "Cold", "Cold"],
        "temp_c": [25.0, 18.0, 15.0],
        "geothermquartz_c": [np.nan, 135.0, 30.0],
        "geothermchalc_c": [np.nan, 110.0, 25.0],
        "geothermcat_c": [np.nan, np.nan, np.nan],
        "dist_known_fault_px": [0.0, 0.0, 0.0],
    })
    df2 = df1.copy()
    df2["dist_known_fault_px"] = [99999.0, -500.0, 12345.0]

    p1 = tmp_path / "gdr1.csv"
    p2 = tmp_path / "gdr2.csv"
    df1.to_csv(p1, index=False)
    df2.to_csv(p2, index=False)

    r1 = gdr_blind_thermal_features(p1, (32, 32), valid, sigma_px=3.0)
    r2 = gdr_blind_thermal_features(p2, (32, 32), valid, sigma_px=3.0)
    assert r1["n_thermal_pixels"] == 2  # trailing-space 'Hot ' + blind 135 C quartz point
    assert r1["n_blind_geotherm_pixels"] == 1
    assert np.array_equal(r1["plume_feat"], r2["plume_feat"])


def test_feature_stack_handles_sentinels_and_polarity_concordance():
    h, w = 64, 64
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    foot = np.ones((h, w), dtype=bool)
    foot[:2, :] = False

    # West-dipping normal fault at col 32: East side (xx > 32) is upthrown footwall
    step = np.tanh((xx - 32.0) / 2.0).astype(np.float32)
    det_elev = 100.0 * step
    det_slope = 15.0 * np.exp(-0.5 * ((xx - 32.0) / 2.0) ** 2)
    grav_anom = 10.0 * step  # concordant footwall high gravity
    depth_base = 300.0 * (1.0 - step) + 20.0  # shallow basement on footwall
    grav_hg = np.gradient(grav_anom)[1]
    rtp = 80.0 * step

    # Inject float32 -3.4e38 sentinels inside footprint to verify no overflow
    det_elev[5, 5] = np.float32(-3.4028235e38)
    rtp[6, 6] = np.float32(-3.4028235e38)

    zeros = np.zeros((h, w), dtype=np.float32)
    ones = np.ones((h, w), dtype=np.float32)
    res = compute_feature_stack(
        rtp=rtp,
        geod_2ndinv=ones * 20.0,
        grav_slope=np.abs(grav_hg),
        geod_shearrate=ones * 10.0,
        geod_dilaterate=ones * 6.0,
        grav_vg=zeros,
        det_elev=det_elev,
        grav_anom=grav_anom,
        depth_to_base=depth_base,
        cond_surf=ones * 2.5,
        grav_hg=grav_hg,
        det_elev_slope=det_slope,
        rad_k=np.full((h, w), 20, dtype=np.uint8),
        rad_th=np.full((h, w), 10, dtype=np.uint8),
        rad_u=np.full((h, w), 8, dtype=np.uint8),
        gdr_plume_feat=zeros,
        footprint=foot,
    )
    X = res["X_foot"]
    assert X.shape == (int(foot.sum()), len(FEATURE_NAMES))
    assert np.isfinite(X).all()
    assert np.isfinite(res["L_topo"]).all() and np.isfinite(res["L_sub"]).all()

    # Check positive footwall-gravity & footwall-basement polarity concordance at col 32
    full_dip_grav = np.zeros((h, w), dtype=np.float32)
    full_dip_grav[foot] = X[:, FEATURE_NAMES.index("f09_dip_concord_grav")]
    full_dip_base = np.zeros((h, w), dtype=np.float32)
    full_dip_base[foot] = X[:, FEATURE_NAMES.index("f10_dip_concord_base")]
    assert float(full_dip_grav[32, 32]) > 0.90
    assert float(full_dip_base[32, 32]) > 0.90


def test_loqo_strictly_isolates_target_quadrant_labels():
    h, w = 80, 80
    yy, xx = np.mgrid[0:h, 0:w]
    foot = np.ones((h, w), dtype=bool)
    valid = np.ones((h, w), dtype=bool)
    quad = quadrant_ids(foot)

    rng = np.random.default_rng(7)
    X = rng.normal(size=(int(foot.sum()), len(FEATURE_NAMES))).astype(np.float32)
    # Plant strong signal on feature 0 along cols 15 and 60 across all quadrants
    on_fault = (np.abs(xx - 15) <= 1) | (np.abs(xx - 60) <= 1)
    X[on_fault.ravel(), 0] += 4.0

    labels_a = on_fault.copy()
    # Mutate labels ONLY inside quadrant 0 (NW): LOQO prediction on quadrant 0 MUST be unchanged!
    labels_b = labels_a.copy()
    labels_b[quad == 0] = ~labels_b[quad == 0]

    p_a = fit_predict_loqo(X, foot, valid, quad, labels_a, guard_px=4, neg_buffer_px=2.0, max_iter=40)
    p_b = fit_predict_loqo(X, foot, valid, quad, labels_b, guard_px=4, neg_buffer_px=2.0, max_iter=40)

    assert np.array_equal(p_a[quad == 0], p_b[quad == 0])
    assert float(p_a[(quad == 0) & on_fault].mean()) > float(p_a[(quad == 0) & (~on_fault)].mean())

    crest = build_crest_surface(p_a, np.ones((h, w), np.float32) * 0.5, None, valid)
    assert crest["S_crest"].shape == (h, w)
    assert len(TOPO_ONLY_INDICES) == 8

    with pytest.raises(ValueError, match="guard_px"):
        fit_predict_loqo(X, foot, valid, quad, labels_a, guard_px=-1)
    with pytest.raises(ValueError, match="neg_pos_ratio"):
        fit_predict_loqo(X, foot, valid, quad, labels_a, neg_pos_ratio=0)
    with pytest.raises(ValueError, match="sigma"):
        hessian_ridge_strength(np.ones((8, 8), np.float32), np.ones((8, 8), bool), sigma=0.0)


def test_feature_stack_handles_nan_float_radiometrics():
    h, w = 24, 24
    foot = np.ones((h, w), dtype=bool)
    ones = np.ones((h, w), dtype=np.float32)
    rad_k = np.full((h, w), 10.0, dtype=np.float32)
    rad_th = np.full((h, w), 5.0, dtype=np.float32)
    rad_u = np.full((h, w), 3.0, dtype=np.float32)
    rad_k[2, 2] = np.nan
    rad_th[3, 3] = np.nan
    rad_u[4, 4] = np.nan
    res = compute_feature_stack(
        rtp=ones,
        geod_2ndinv=ones,
        grav_slope=ones,
        geod_shearrate=ones,
        geod_dilaterate=ones,
        grav_vg=ones,
        det_elev=ones,
        grav_anom=ones,
        depth_to_base=ones,
        cond_surf=ones,
        grav_hg=ones,
        det_elev_slope=ones,
        rad_k=rad_k,
        rad_th=rad_th,
        rad_u=rad_u,
        gdr_plume_feat=ones,
        footprint=foot,
    )
    assert np.isfinite(res["X_foot"]).all()
