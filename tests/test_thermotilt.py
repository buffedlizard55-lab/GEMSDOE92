"""Unit tests for the THERMOTILT geological lane (gems/thermotilt.py)."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt

from gems.thermotilt import (
    FEATURE_NAMES,
    INNER_SUPPRESS_R_PX,
    allocate_dual_regime_crests,
    antithetic_accommodation_twist,
    build_graded_tail_allocation,
    distal_annular_accommodation_fields,
    fit_stage1_oof_loqo,
    fit_stage2_thermotilt_loqo,
    harmonic_1vd_signed_tilt,
    upgradient_piezometric_backprojection,
)


def test_harmonic_1vd_signed_tilt_localizes_contact_and_preserves_sign():
    h, w = 96, 96
    yy, xx = np.meshgrid(np.arange(h, dtype=np.float32), np.arange(w, dtype=np.float32), indexing="ij")
    valid = np.ones((h, w), dtype=bool)
    # Vertical contact at x = 48: negative for x < 48, positive for x > 48
    step_strong = 50.0 * np.tanh((xx - 48.0) / 3.0)
    step_weak = 2.0 * np.tanh((xx - 48.0) / 3.0)

    res_strong = harmonic_1vd_signed_tilt(step_strong, valid, z0_px=1.4, pad_px=16)
    res_weak = harmonic_1vd_signed_tilt(step_weak, valid, z0_px=1.4, pad_px=16)

    # Sign preservation: 1VD and signed tilt are positive on high block (x=54) and negative on low block (x=42)
    assert float(res_strong["vdr"][48, 54]) > 0.0
    assert float(res_strong["vdr"][48, 42]) < 0.0
    assert float(res_strong["signed_tilt"][48, 54]) > 0.0
    assert float(res_strong["signed_tilt"][48, 42]) < 0.0

    # Contact localization: zero_contact and hd_tdr peak within 1 px of x = 48
    peak_zc = int(np.argmax(res_strong["zero_contact"][48, 20:76]) + 20)
    peak_hd = int(np.argmax(res_strong["hd_tdr"][48, 20:76]) + 20)
    assert abs(peak_zc - 48) <= 1
    assert abs(peak_hd - 48) <= 1

    # Amplitude invariance of Verduzco-Salem HD_TDR across 25x amplitude ratio
    ratio = float(res_weak["hd_tdr"][48, 48]) / max(float(res_strong["hd_tdr"][48, 48]), 1e-6)
    assert 0.80 <= ratio <= 1.25


def test_upgradient_piezometric_backprojection_peaks_upslope_not_downslope():
    h, w = 80, 96
    valid = np.ones((h, w), dtype=bool)
    # Range block is to the WEST (smaller x -> higher elevation -> ux_upslope = -1.0)
    uy_up = np.zeros((h, w), dtype=np.float32)
    ux_up = -np.ones((h, w), dtype=np.float32)

    outflow = np.zeros((h, w), dtype=np.float32)
    outflow[40, 52] = 10.0  # Warm spring at x = 52

    up = upgradient_piezometric_backprojection(
        outflow,
        uy_up,
        ux_up,
        valid,
        shifts_px=(5.0, 11.0, 18.0),
        weights=(0.45, 0.35, 0.20),
        plume_sigma_px=3.0,
    )
    # Upslope (west: x ~ 41..47) must strongly exceed downslope (east: x ~ 57..63)
    upslope_val = float(up[40, 41:48].mean())
    downslope_val = float(up[40, 57:64].mean())
    assert upslope_val > 0.35
    assert upslope_val > 4.0 * downslope_val


def test_antithetic_accommodation_twist_separates_graben_horst_and_ramp():
    h, w = 80, 96
    yy, xx = np.meshgrid(np.arange(h, dtype=np.float32), np.arange(w, dtype=np.float32), indexing="ij")
    valid = np.ones((h, w), dtype=bool)
    ny = np.zeros((h, w), dtype=np.float32)
    nx = np.ones((h, w), dtype=np.float32)

    # 1. Symmetric graben gravity low centered at x = 48
    g_graben = -15.0 * np.exp(-0.5 * ((xx - 48.0) / 6.5) ** 2)
    conv_g, div_g = antithetic_accommodation_twist(g_graben, ny, nx, valid, offsets_px=(6.0, 10.0))
    assert float(conv_g[40, 48]) > 0.42
    assert float(div_g[40, 48]) < 0.05

    # 2. Symmetric intrabasin horst gravity high centered at x = 48
    g_horst = +15.0 * np.exp(-0.5 * ((xx - 48.0) / 6.5) ** 2)
    conv_h, div_h = antithetic_accommodation_twist(g_horst, ny, nx, valid, offsets_px=(6.0, 10.0))
    assert float(div_h[40, 48]) > 0.42
    assert float(conv_h[40, 48]) < 0.05

    # 3. Monotonic planar gravity ramp -> zero polarity reversal in interior
    g_ramp = 0.8 * xx
    conv_r, div_r = antithetic_accommodation_twist(g_ramp, ny, nx, valid, offsets_px=(6.0, 10.0))
    assert float(conv_r[20:60, 25:70].max()) == 0.0
    assert float(div_r[20:60, 25:70].max()) == 0.0


def test_distal_annular_bridge_suppresses_near_tip_and_excludes_self():
    h, w = 110, 110
    valid = np.ones((h, w), dtype=bool)
    vis = np.zeros((h, w), dtype=bool)
    # Single horizontal fault segment from x=20..40 at y=55 (tip at y=55, x=40 pointing +x)
    vis[55, 20:41] = True
    strike = np.full((h, w), 90.0, dtype=np.float32)

    fields = distal_annular_accommodation_fields(vis, strike, valid, inner_r_px=INNER_SUPPRESS_R_PX, max_r_px=42)
    en = fields["tt_da_enechelon_annulus"]
    ax = fields["tt_da_axial_far_annulus"]

    # Self-component exclusion: zero on the segment itself
    assert float(en[vis].max()) == 0.0
    assert float(ax[vis].max()) == 0.0

    # Inner tip-halo suppression: zero within r <= 9 px ahead of the tip (x = 41..49 at y = 55)
    assert float(ax[55, 41:50].max()) == 0.0
    assert float(en[53:58, 41:49].max()) == 0.0

    # Distal annular activation: positive at r ~ 16..28 px ahead of the tip
    assert float(ax[55, 58:68].max()) > 0.05
    assert float(en[50:61, 58:68].max()) > 0.05


def test_dual_regime_and_graded_tail_enforce_collar_range_and_quota():
    h, w = 90, 90
    valid = np.ones((h, w), dtype=bool)
    vis = np.zeros((h, w), dtype=bool)
    vis[45, 20:70] = True
    d_vis = distance_transform_edt(~vis)

    rng = np.random.default_rng(42)
    blind_surf = rng.uniform(0.1, 0.9, size=(h, w)).astype(np.float32)
    distal_surf = rng.uniform(0.2, 1.0, size=(h, w)).astype(np.float32)
    hh = rng.uniform(0.0, 1.0, size=(h, w)).astype(np.float32)
    br = np.zeros((h, w), dtype=np.float32)
    br[10:35, 10:80] = 0.5  # Corridor region

    prim = allocate_dual_regime_crests(
        blind_surf,
        distal_surf,
        hh,
        br,
        vis,
        valid,
        budget_dots=120,
        corridor_max_dots=45,
        min_dcat_px=2.0,
        min_sep_px=2.85,
    )
    assert prim.dtype == np.float32
    assert not np.isnan(prim).any()
    assert float(prim.min()) >= 0.0 and float(prim.max()) <= 1.0
    assert int((prim > 0).sum()) == 120
    assert float(d_vis[prim > 0].min()) > 2.0
    # Quota respected: at most ~45 corridor dots (plus only any spillover if needed, here plenty of non-corridor space)
    assert int(((prim > 0) & (br > 0.06)).sum()) <= 45

    graded = build_graded_tail_allocation(
        prim,
        blind_surf,
        vis,
        valid,
        extra_dots=40,
        tail_weight=0.62,
        min_dcat_px=2.0,
        min_sep_px=3.0,
    )
    assert not np.isnan(graded).any()
    assert float(graded.min()) >= 0.0 and float(graded.max()) <= 1.0
    assert int((graded == 1.0).sum()) == 120
    assert int((graded > 0).sum()) == 160
    assert float(d_vis[graded > 0].min()) > 2.0
    assert len(FEATURE_NAMES) == 37


def test_stage1_and_stage2_loqo_end_to_end_synthetic():
    h, w = 80, 80
    foot = np.ones((h, w), dtype=bool)
    valid = np.ones((h, w), dtype=bool)
    quad = np.zeros((h, w), dtype=np.int32)
    quad[:40, 40:] = 1
    quad[40:, :40] = 2
    quad[40:, 40:] = 3

    vis = np.zeros((h, w), dtype=bool)
    for y in (15, 25, 55, 65):
        vis[y, 8:32] = True
        vis[y, 48:72] = True

    rng = np.random.default_rng(7)
    X_foot = rng.normal(0.0, 1.0, size=(h * w, len(FEATURE_NAMES))).astype(np.float32)
    # Give positive signal on channels 1, 7, 19, 33 along visible faults
    pos_flat = vis.ravel()
    X_foot[pos_flat, 1] += 2.2
    X_foot[pos_flat, 7] += 1.8
    X_foot[pos_flat, 19] += 2.0
    X_foot[pos_flat, 33] += 1.5

    p_sub, p_full = fit_stage1_oof_loqo(X_foot, foot, valid, vis, quad, seed=101)
    assert p_sub.shape == (h, w) and p_full.shape == (h, w)
    assert float(p_full[vis].mean()) > float(p_full[~vis].mean())

    w_cov = np.full((h, w), 0.45, dtype=np.float32)
    strike = np.full((h, w), 90.0, dtype=np.float32)
    hh = np.clip(X_foot[:, 1].reshape(h, w) * 0.25 + 0.5, 0.0, 1.0).astype(np.float32)
    crest = fit_stage2_thermotilt_loqo(
        X_foot,
        foot,
        valid,
        w_cov,
        strike,
        hh,
        vis,
        quad,
        include_distal=True,
        train_mask_grid=(quad != 3),
        seed=202,
    )
    assert crest.shape == (h, w)
    assert not np.isnan(crest).any()
    assert float(crest.min()) >= 0.0 and float(crest.max()) <= 1.0
    # Held-out quadrant 3 should still separate faults from background
    q3_pos = vis & (quad == 3)
    q3_neg = (~vis) & (quad == 3)
    assert float(crest[q3_pos].mean()) > float(crest[q3_neg].mean())


def test_thermotilt_artifacts_run_card_and_focus9_contract():
    import hashlib
    import json
    from pathlib import Path
    import rasterio

    root = Path(__file__).resolve().parents[1]
    ev_rc = root / "evidence" / "thermotilt_run_card.json"
    dl_rc = root / "docs" / "downloads" / "thermotilt_run_card.json"
    assert ev_rc.is_file() and dl_rc.is_file()
    assert ev_rc.read_text(encoding="utf-8") == dl_rc.read_text(encoding="utf-8")

    rc = json.loads(ev_rc.read_text(encoding="utf-8"))
    assert rc["lane"] == "THERMOTILT"
    assert rc["experiments_run"] == 3
    assert rc["weekly_slots_used"] == 0
    assert rc["organizer_confirmed_score"] is None
    assert rc["verdict"] == "negative"
    assert rc["submission_eligible"] is False
    assert rc["leakage_canaries"]["all_pass"] is True
    assert rc["leakage_canaries"]["n_features_tested"] == 37
    assert rc["leakage_canaries"]["max_symmetric_auc"] <= 0.90
    assert len(rc["note"]) <= 140
    assert rc["holdout_dti"]["label"] == "HOLDOUT-DTI"
    assert rc["holdout_dti"]["evaluator_version"] == "gems57-pooled-hide-v2"
    assert rc["holdout_dti"]["withheld_positive_pixels"] == 22663
    assert rc["correlation_overlap_vs_registry"]["operative_sparse_pass"] is True  # historical diagnostic only
    assert rc["protocol_limitations"]
    assert rc["new_unique_tiff_generated"] is False
    assert rc["correlation_overlap_vs_registry"]["focus_9_sites"]["worst_operative_3px_overlap"] <= 0.70
    assert rc["correlation_overlap_vs_registry"]["local_registry"]["worst_operative_3px_overlap"] <= 0.70

    # Verify primary + both sibling GeoTIFFs & ZIPs exist, match exact SHA-256, and satisfy [0, 1] / 0-NaN
    tifs_to_check = [
        (root / rc["primary_download"], rc["raster_sha256"], 37654),
        (
            root / rc["sibling_arms"]["thermotilt_distal"]["file"],
            rc["sibling_arms"]["thermotilt_distal"]["sha256_zeros"],
            37654,
        ),
        (
            root / rc["sibling_arms"]["thermotilt_graded50k"]["file"],
            rc["sibling_arms"]["thermotilt_graded50k"]["sha256_zeros"],
            50000,
        ),
    ]
    for tif_p, exp_sha, exp_pos in tifs_to_check:
        assert tif_p.is_file(), f"Missing {tif_p}"
        got_sha = hashlib.sha256(tif_p.read_bytes()).hexdigest()
        assert got_sha == exp_sha
        with rasterio.open(tif_p) as ds:
            assert ds.count == 1
            assert ds.dtypes == ("float32",)
            assert (ds.height, ds.width) == (3730, 3292)
            assert str(ds.crs) == "EPSG:32611"
            arr = ds.read(1)
            assert int(np.isnan(arr).sum()) == 0
            assert int(np.isinf(arr).sum()) == 0
            assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
            assert int((arr > 0).sum()) == exp_pos

    # Verify all 9 focus sites are byte-audited and documented
    f9_path = root / "evidence" / "focus_9sites_audit_20261026.json"
    assert f9_path.is_file()
    f9 = json.loads(f9_path.read_text(encoding="utf-8"))
    expected_sites = {
        "GEMSDOE24",
        "GEMSDOE25",
        "GEMSDOE27",
        "GEMSDOE28",
        "GEMSDOE30",
        "GEMSDOE31",
        "GEMSDOE32",
        "GEMSDOE33",
        "GEMSDOE36",
    }
    site_prefixes = {k.split("_")[0] for k in f9["sites"].keys()}
    assert expected_sites.issubset(site_prefixes)

    for doc_rel in (
        "docs/HYPOTHESES_20261026_THERMOTILT.md",
        "docs/ANALYSIS_20261026_THERMOTILT.md",
        "docs/REVIEW_20261026_THERMOTILT.md",
        "docs/thermotilt.html",
        "docs/index.html",
        "docs/executive-summary.html",
        "README.md",
    ):
        txt = (root / doc_rel).read_text(encoding="utf-8")
        assert "gemsdoe92-thermotilt-blind-37654-20261026-8c11022a-zeros.tif" in txt or "THERMOTILT" in txt


