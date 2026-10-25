"""Unit and contract tests for the LISTRICLOQO lane (`gems.listric_loqo`)."""
from __future__ import annotations

import numpy as np

from gems.listric_loqo import (
    DEBIASED_INDICES,
    EXTRA_FEATURE_NAMES,
    FEATURE_NAMES,
    SUB_LISTRIC_INDICES,
    build_listric_crest_surface,
    compute_gravity_tensor_and_riedel,
    compute_listric_dip_operators,
    compute_listric_loqo_stack,
    fit_predict_listric_loqo,
    sample_bilinear_offset,
)


def test_listric_feature_names_and_subsets() -> None:
    assert len(EXTRA_FEATURE_NAMES) == 6
    assert len(FEATURE_NAMES) == 36
    assert len(DEBIASED_INDICES) == 30
    assert len(SUB_LISTRIC_INDICES) == 31
    assert 30 in DEBIASED_INDICES
    assert 35 in SUB_LISTRIC_INDICES


def test_sample_bilinear_offset_recovers_shifted_ridge() -> None:
    h, w = 48, 48
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # Ridge at x = 24, shifted into hanging wall at x = 28 (dx = +4 px)
    sub_ridge = np.exp(-0.5 * ((xx - 28.0) / 1.5) ** 2).astype(np.float32)
    dy = np.zeros_like(sub_ridge)
    dx = np.full_like(sub_ridge, 4.0)
    pulled = sample_bilinear_offset(sub_ridge, dy, dx)
    # After +4 px pullback, the peak should sit at x = 24
    assert float(pulled[24, 24]) > 0.95
    assert float(pulled[24, 24]) > float(sub_ridge[24, 24]) * 5.0


def test_listric_dip_operators_and_gravity_tensor_on_synthetic_fault() -> None:
    h, w = 64, 64
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    valid = np.ones((h, w), dtype=bool)
    # Range on left (x < 30, high elevation), hanging-wall basin on right (x > 30, low elevation)
    det_elev = (150.0 * np.tanh((30.0 - xx) / 3.0)).astype(np.float32)
    det_elev_slope = (14.0 * np.exp(-0.5 * ((xx - 30.0) / 2.5) ** 2)).astype(np.float32)
    depth_to_base = (400.0 / (1.0 + np.exp(-(xx - 31.0) / 2.0))).astype(np.float32)
    l_topo = np.exp(-0.5 * ((xx - 30.0) / 1.5) ** 2).astype(np.float32)
    # Subsurface contact displaced +4 px into the hanging wall (x = 34)
    l_sub = np.exp(-0.5 * ((xx - 34.0) / 1.8) ** 2).astype(np.float32)

    dip_ops = compute_listric_dip_operators(
        det_elev=det_elev,
        det_elev_slope=det_elev_slope,
        depth_to_base=depth_to_base,
        l_topo=l_topo,
        l_sub=l_sub,
        valid=valid,
    )
    updip = dip_ops["listric_hw_updip_pullback"]
    downdip = dip_ops["listric_fw_downdip_splay"]
    w_toe = dip_ops["wallace_basal_toe_asym"]
    assert updip.shape == (h, w)
    assert np.all(np.isfinite(updip))
    # Up-dip pullback at surface scarp x=30 exceeds raw l_sub at x=30
    assert float(updip[32, 30]) > float(l_sub[32, 30]) * 1.5
    # Down-dip splay at hanging-wall x=33 is positive
    assert float(downdip[32, 33]) > 0.20
    assert float(w_toe[:, 29:33].max()) > 0.05

    grav_anom = (-15.0 * np.tanh((xx - 34.0 + 0.32 * (yy - 32.0)) / 3.0)).astype(np.float32)
    grav_slope = np.hypot(*np.gradient(grav_anom)).astype(np.float32)
    grav_vg = np.gradient(grav_slope)[1].astype(np.float32)
    gt_ops = compute_gravity_tensor_and_riedel(
        det_elev=det_elev,
        grav_anom=grav_anom,
        grav_slope=grav_slope,
        grav_vg=grav_vg,
        valid=valid,
    )
    for k in ("grav_tensor_3d_tilt", "grav_tensor_contact_ecc", "riedel_en_echelon_coupling"):
        arr = gt_ops[k]
        assert arr.shape == (h, w)
        assert np.all(np.isfinite(arr))
        assert float(arr.min()) >= 0.0
        assert float(arr.max()) <= 1.0 + 1e-5
    # 18-deg synthetic strike obliquity between x=30 scarp and ~18-deg oblique gravity step
    assert float(gt_ops["riedel_en_echelon_coupling"][32, 31]) > 0.30


def test_compute_listric_loqo_stack_and_fit_predict_are_catalogue_free() -> None:
    rng = np.random.default_rng(92)
    h, w = 48, 48
    foot = np.ones((h, w), dtype=bool)
    foot[0, :] = False
    quad = np.zeros((h, w), dtype=np.int8)
    quad[:24, 24:] = 1
    quad[24:, :24] = 2
    quad[24:, 24:] = 3

    stack = compute_listric_loqo_stack(
        rtp=rng.normal(size=(h, w)).astype(np.float32),
        geod_2ndinv=np.abs(rng.normal(size=(h, w))).astype(np.float32),
        grav_slope=np.abs(rng.normal(size=(h, w))).astype(np.float32),
        geod_shearrate=np.abs(rng.normal(size=(h, w))).astype(np.float32),
        geod_dilaterate=rng.normal(size=(h, w)).astype(np.float32),
        grav_vg=rng.normal(size=(h, w)).astype(np.float32),
        det_elev=(rng.normal(size=(h, w)) * 50.0).astype(np.float32),
        grav_anom=rng.normal(size=(h, w)).astype(np.float32),
        depth_to_base=np.abs(rng.normal(size=(h, w)) * 200.0).astype(np.float32),
        cond_surf=np.abs(rng.normal(size=(h, w)) * 10.0 + 1.0).astype(np.float32),
        grav_hg=np.abs(rng.normal(size=(h, w))).astype(np.float32),
        det_elev_slope=np.abs(rng.normal(size=(h, w)) * 8.0).astype(np.float32),
        rad_k=np.abs(rng.normal(size=(h, w)) * 20.0).astype(np.float32),
        rad_th=np.abs(rng.normal(size=(h, w)) * 20.0).astype(np.float32),
        rad_u=np.abs(rng.normal(size=(h, w)) * 20.0).astype(np.float32),
        gdr_plume_feat=np.clip(rng.uniform(size=(h, w)), 0.0, 1.0).astype(np.float32),
        footprint=foot,
    )
    assert stack["X_foot"].shape == (int(foot.sum()), 36)
    assert np.all(np.isfinite(stack["X_foot"]))

    labels = np.zeros((h, w), dtype=bool)
    labels[6:42, 12] = True
    labels[6:42, 36] = True
    fit = fit_predict_listric_loqo(
        stack["X_foot"],
        foot,
        stack["valid"],
        quad,
        labels,
        guard_px=2,
        neg_buffer_px=2.0,
        max_iter=35,
    )
    for k in ("p_full", "p_debiased", "p_sub", "raw_proba", "cal_proba"):
        arr = fit[k]
        assert arr.shape == (h, w)
        assert np.all(np.isfinite(arr))
        assert float(arr[~foot].max()) == 0.0
        assert 0.0 <= float(arr[foot].min()) <= float(arr[foot].max()) <= 1.0

    crest = build_listric_crest_surface(
        fit["cal_proba"],
        stack["L_topo_listric"],
        stack["L_sub"],
        stack["valid"],
        l_knick=stack["L_knick"],
    )
    assert crest["S_crest"].shape == (h, w)
    assert float(crest["S_crest"][~foot].max()) == 0.0


def test_listric_loqo_evidence_and_run_card_contract() -> None:
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    rc_path = root / "evidence" / "listric_loqo_run_card.json"
    dl_rc_path = root / "docs" / "downloads" / "listric_loqo_run_card.json"
    screen_path = root / "evidence" / "listric_loqo_screen.json"
    variants_path = root / "evidence" / "listric_loqo_variants.json"
    audit_path = root / "evidence" / "listric_loqo_proxy_audit.json"
    dual_path = root / "evidence" / "listric_loqo_dual_reading_audit.json"

    for p in (rc_path, dl_rc_path, screen_path, variants_path, audit_path, dual_path):
        assert p.is_file(), f"Missing LISTRICLOQO evidence file: {p}"

    rc = json.loads(rc_path.read_text(encoding="utf-8"))
    assert rc == json.loads(dl_rc_path.read_text(encoding="utf-8"))
    assert rc["verdict"] == "negative"
    assert rc["submission_eligible"] is False
    assert rc["weekly_slots_used"] == 0
    assert rc["experiments_used"] == 3
    assert len(rc["note"]) <= 140
    assert rc["leakage_canary_max_symmetric_auc"] <= 0.90

    # Verify holdout DTI beats previous #1 KNICKLOQO standalone (0.010788) with 95% CI > 0
    hd = rc["holdout_dti"]
    assert hd["evidence_class"] == "HOLDOUT-DTI"
    assert hd["withheld_positive_pixels"] == 22663
    assert hd["dti"] > 0.0120
    assert hd["paired_vs_KNICKLOQO_standalone_prev_best"]["delta"] > 0.0010
    assert hd["paired_vs_KNICKLOQO_standalone_prev_best"]["ci95"][0] > 0.0
    assert hd["paired_vs_COULOMBLOQO_standalone"]["ci95"][0] > 0.0
    assert hd["paired_vs_R0"]["ci95"][0] > 0.0
    assert hd["strict_draw_blind_dcat2_dti"] > 0.0114
    assert hd["strict_draw_blind_dvis2_dti"] > 0.1110

    # Verify local and public dual-reading uniqueness <= 0.70
    uniq = rc["correlation_overlap_vs_registry"]
    assert uniq["local_duplicate"] is False
    assert uniq["final_worst_local_forward_overlap"] <= 0.70
    assert uniq["public_dual_reading_worst_overlap"] <= 0.70
    assert uniq["public_dual_reading_over_70pct_count"] == 0
    assert uniq["unique_under_dual_reading_rule"] is True
    assert uniq["unique_under_literal_public_rule"] is False

    # Verify exact SHA-256 of served TIF & ZIP matches Run Card and all documentation pages
    import hashlib

    tif_path = root / rc["primary_download"]
    zip_path = root / rc["primary_zip"]
    assert tif_path.is_file() and zip_path.is_file()
    tif_sha = hashlib.sha256(tif_path.read_bytes()).hexdigest()
    zip_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    assert tif_sha == rc["raster_sha256"]
    assert zip_sha == rc["zip_sha256"]
    for doc_rel in (
        "README.md",
        "SESSION_PROMPT.md",
        "docs/REVIEW_CURRENT.md",
        "docs/NEXT_STEPS.md",
        "docs/ANALYSIS_20261025_LISTRICLOQO.md",
        "docs/index.html",
        "docs/executive-summary.html",
        "docs/SUBMIT.html",
    ):
        text = (root / doc_rel).read_text(encoding="utf-8")
        assert tif_sha in text, f"Exact LISTRICLOQO standalone SHA-256 missing in {doc_rel}"

