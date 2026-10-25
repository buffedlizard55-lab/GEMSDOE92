"""Unit and integration tests for the POISSONKNICK lane (2026-10-25)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import rasterio

from gems.poissonknick import (
    FEATURE_NAMES,
    POISSONKNICK_EXTRA_NAMES,
    build_poissonknick_crest_surface,
    calibrate_quadrant_probabilities,
    compute_poissonknick_extra_channels,
    emit_poissonknick_dots,
)

ROOT = Path(__file__).resolve().parents[1]


def test_poissonknick_feature_names_and_count():
    assert len(POISSONKNICK_EXTRA_NAMES) == 6
    assert len(FEATURE_NAMES) == 30
    assert "dist_known_fault_px" not in FEATURE_NAMES


def test_calibrate_quadrant_probabilities_restores_starved_ne_quadrant():
    h, w = 40, 40
    valid = np.ones((h, w), dtype=bool)
    valid[0, :] = False
    quad = np.zeros((h, w), dtype=np.int8)
    quad[:20, 20:] = 1  # NE
    quad[20:, :20] = 2  # SW
    quad[20:, 20:] = 3  # SE

    rng = np.random.default_rng(42)
    # Realistic heavy-tailed fault probability distribution (u^4)
    prob = (rng.uniform(0.0, 1.0, size=(h, w)) ** 4).astype(np.float32)
    # Simulate #IR-92-NE-QUADRANT-LOQO-COLLAPSE: scale NE down by 5x
    prob[quad == 1] *= 0.20
    prob[~valid] = 0.0

    # Without calibration, top-80 pixels have 0 in NE
    uncal_top = np.argsort(prob.ravel())[-80:]
    assert int((quad.ravel()[uncal_top] == 1).sum()) == 0

    cal = calibrate_quadrant_probabilities(prob, valid=valid, quad=quad, blend_quantile=1.0)
    assert cal.dtype == np.float32
    assert np.all(np.isfinite(cal))
    assert float(cal.min()) >= 0.0 and float(cal.max()) <= 1.0
    assert np.all(cal[~valid] == 0.0)

    cal_top = np.argsort(cal.ravel())[-80:]
    ne_count = int((quad.ravel()[cal_top] == 1).sum())
    assert 15 <= ne_count <= 25, f"Expected balanced NE top count, got {ne_count}"


def test_extra_channels_and_crest_surface_handle_sentinels_and_nans():
    h, w = 32, 32
    foot = np.ones((h, w), dtype=bool)
    foot[0, :] = False
    valid = foot.copy()
    quad = np.zeros((h, w), dtype=np.int8)
    quad[:16, 16:] = 1
    quad[16:, :16] = 2
    quad[16:, 16:] = 3

    rng = np.random.default_rng(7)
    rtp = rng.normal(size=(h, w)).astype(np.float32)
    rtp[5, 5] = -3.4028235e38  # float32 sentinel
    rtp[6, 6] = np.nan
    valid[5, 5] = False
    valid[6, 6] = False

    grav_slope = np.abs(rng.normal(size=(h, w))).astype(np.float32)
    grav_vg = rng.normal(size=(h, w)).astype(np.float32)
    det_elev = rng.uniform(-250.0, 250.0, size=(h, w)).astype(np.float32)
    grav_anom = rng.normal(size=(h, w)).astype(np.float32)
    depth_to_base = np.abs(rng.normal(loc=1000.0, scale=300.0, size=(h, w))).astype(np.float32)
    cond_surf = rng.normal(size=(h, w)).astype(np.float32)
    det_elev_slope = np.abs(rng.normal(loc=5.0, scale=3.0, size=(h, w))).astype(np.float32)

    n_foot = int(foot.sum())
    ones_foot = rng.uniform(0.0, 1.0, size=n_foot).astype(np.float32)
    l_sub = rng.uniform(0.0, 1.0, size=(h, w)).astype(np.float32)

    res = compute_poissonknick_extra_channels(
        rtp=rtp,
        grav_slope=grav_slope,
        grav_vg=grav_vg,
        det_elev=det_elev,
        grav_anom=grav_anom,
        depth_to_base=depth_to_base,
        cond_surf=cond_surf,
        det_elev_slope=det_elev_slope,
        rel_break_foot=ones_foot,
        mu_step_foot=ones_foot,
        rtp_demag_foot=ones_foot,
        bstep_foot=ones_foot,
        rtilt_foot=ones_foot * 4.0,
        cdil_foot=ones_foot * 3.0,
        mtgrad_foot=ones_foot,
        l_sub=l_sub,
        footprint=foot,
        valid=valid,
        quad=quad,
    )
    assert res["X_extra"].shape == (n_foot, 6)
    assert np.all(np.isfinite(res["X_extra"]))
    assert np.all(np.isfinite(res["L_pk_sub"]))

    prob = rng.uniform(0.0, 1.0, size=(h, w)).astype(np.float32)
    crest = build_poissonknick_crest_surface(
        prob,
        l_topo=ones_foot.mean() * np.ones((h, w), dtype=np.float32),
        l_pk_sub=res["L_pk_sub"],
        valid=valid,
        quad=quad,
        calibrate_crest=True,
    )
    assert np.all(np.isfinite(crest["S_crest"]))
    assert float(crest["S_crest"].min()) >= 0.0 and float(crest["S_crest"].max()) <= 1.0
    assert np.all(crest["S_crest"][~valid] == 0.0)

    excl = np.full((h, w), 5.0, dtype=np.float32)
    excl[10, 10] = 1.0
    h19 = np.zeros((h, w), dtype=bool)
    h19[8:24, 15] = True
    d_h19 = np.full((h, w), 4.0, dtype=np.float32)
    d_h19[h19] = 0.0
    for arm in ("qcal", "uncal", "pkdual40"):
        dots = emit_poissonknick_dots(
            arm,
            s_crest=crest["S_crest"],
            ridge_1d=crest["ridge_1d"],
            l_pk_sub=res["L_pk_sub"],
            valid=valid,
            exclusion_dist=excl,
            h19_mask=h19,
            d_h19=d_h19,
            target_dots=12,
        )
        assert int(dots.sum()) == 12
        assert not bool(dots[10, 10])
        assert not bool(np.any(dots[~valid]))


def test_poissonknick_receipts_and_tifs_are_valid_and_consistent():
    card_path = ROOT / "evidence/poissonknick_run_card.json"
    dl_card_path = ROOT / "docs/downloads/poissonknick_run_card.json"
    screen_path = ROOT / "evidence/poissonknick_screen.json"
    hold_path = ROOT / "evidence/poissonknick_holdout.json"
    uniq_path = ROOT / "evidence/poissonknick_uniqueness.json"

    for p in (card_path, dl_card_path, screen_path, hold_path, uniq_path):
        assert p.is_file(), f"Missing receipt: {p}"

    assert card_path.read_text(encoding="utf-8") == dl_card_path.read_text(encoding="utf-8")
    card = json.loads(card_path.read_text(encoding="utf-8"))
    screen = json.loads(screen_path.read_text(encoding="utf-8"))
    hold = json.loads(hold_path.read_text(encoding="utf-8"))
    uniq = json.loads(uniq_path.read_text(encoding="utf-8"))

    # Rule 3 & Rule 6 checks
    assert card["lane"] == "POISSONKNICK"
    assert card["primary_arm"] == "qcal"
    assert card["verdict"] == "negative"
    assert card["submission_eligible"] is False
    assert card["weekly_slots_used"] == 0
    assert card["experiments_used"] == 3 == card["experiment_budget"]
    assert card["holdout_dti"]["evidence_class"] == "HOLDOUT-DTI"
    assert card["holdout_dti"]["evaluator_version"] == "gems57-pooled-hide-v2"
    assert card["holdout_dti"]["withheld_positive_pixels"] == 22663
    assert card["holdout_dti"]["organizer_confirmed"] is False

    # Rule 4: 53 leakage canaries pass <= 0.90
    assert screen["leakage_canary"]["all_pass"] is True
    assert screen["leakage_canary"]["max_symmetric_auc"] <= 0.90

    # Next Step 1: COULOMBLOQO re-read under dual_reading_decision
    ns1 = screen["next_step_1_coulombloqo_dual_reading"]
    assert ns1["standalone"]["local_registry_including_eulerfuse"]["duplicate"] is True
    assert ns1["standalone"]["public_registry_150k"]["duplicate"] is True
    assert ns1["dual45"]["local_registry_including_eulerfuse"]["duplicate"] is True
    assert ns1["dual45"]["public_registry_150k"]["duplicate"] is True

    # Next Step 2: #IR-92-NE-QUADRANT-LOQO-COLLAPSE resolution
    qdots = hold["quadrant_dot_allocations"]
    assert qdots["POISSONKNICK_uncal"]["NE"]["dots"] == 2396
    assert qdots["POISSONKNICK_qcal"]["NE"]["dots"] == 9967
    ne_qcal_dti = hold["quadrant_stratified_strict_dti"]["NE"]["qcal"]["dti"]
    ne_uncal_dti = hold["quadrant_stratified_strict_dti"]["NE"]["uncal"]["dti"]
    assert ne_qcal_dti > ne_uncal_dti + 0.030

    # Static HOLDOUT-DTI record check
    st_qcal = hold["static_deployment_d_cat_gt_2"]["qcal"]["scores"]["qcal"]["dti"]
    st_cl = hold["static_deployment_d_cat_gt_2"]["qcal"]["scores"]["COULOMBLOQO_standalone"]["dti"]
    st_r0 = hold["static_deployment_d_cat_gt_2"]["qcal"]["scores"]["R0"]["dti"]
    assert st_qcal > st_cl > st_r0

    # Reading 2 uniqueness check across all 3 arms
    for arm in ("qcal", "uncal", "pkdual40"):
        assert uniq["by_arm"][arm]["local"]["duplicate"] is False
        assert uniq["by_arm"][arm]["local"]["worst_matched_budget_forward_overlap"] <= 0.70
        assert uniq["by_arm"][arm]["public"]["duplicate"] is False
        assert uniq["by_arm"][arm]["public"]["worst_matched_budget_forward_overlap"] <= 0.70

    # Verify all 3 GeoTIFFs and audit JSONs on disk
    from scripts.check_site import check_recorded_gates

    for arm, info in card["all_arms"].items():
        tif_path = ROOT / info["file"]
        assert tif_path.is_file()
        assert hashlib.sha256(tif_path.read_bytes()).hexdigest() == info["sha256"]
        assert len(info["submission_name"]) <= 140
        assert len(info["note"]) <= 140
        assert info["all_gates_pass"] is True
        assert info["dot_count"] == 37654
        assert info["catalogue_mass"] == 0
        assert info["min_catalogue_distance_px"] > 2.0

        audit_path = ROOT / "docs/downloads" / f"{info['stem'][:-len('-zeros')]}-audit.json"
        assert audit_path.is_file()
        audit_doc = json.loads(audit_path.read_text(encoding="utf-8"))
        problems: list[str] = []
        check_recorded_gates(audit_doc, problems)
        assert problems == [], f"{arm} audit failed check_recorded_gates: {problems}"
        assert audit_doc["sha256_zeros"] == info["sha256"]
        assert audit_doc["overall_pass"] is True
        assert audit_doc["submission_eligible"] is False

        with rasterio.open(tif_path) as ds:
            arr = ds.read(1)
            assert ds.count == 1
            assert ds.dtypes[0] == "float32"
            assert ds.shape == (3730, 3292)
            assert str(ds.crs) == "EPSG:32611"
            assert np.all(np.isfinite(arr))
            assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
            assert int((arr > 0).sum()) == 37654

    # Check documentation and subpage synchronization
    subpage = (ROOT / "docs/poissonknick.html").read_text(encoding="utf-8")
    assert card["raster_sha256"] in subpage
    assert card["submission_name"] in subpage
    assert "OK TO DOWNLOAD" in subpage and "DO NOT SUBMIT" in subpage
    for doc_rel in ("README.md", "docs/index.html", "docs/executive-summary.html", "docs/SUBMIT.html"):
        txt = (ROOT / doc_rel).read_text(encoding="utf-8")
        assert "POISSONKNICK:BEGIN" in txt and card["raster_sha256"] in txt
