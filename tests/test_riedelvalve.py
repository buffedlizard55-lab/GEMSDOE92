"""Unit and artifact-contract tests for the RIEDELVALVE lane (2026-10-25)."""
from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path

import numpy as np
import pytest
import rasterio

from gems.gates import run_gates, summarise
from gems.rasters import sha256_file
from gems.riedelvalve import (
    FEATURE_NAMES,
    GROUP_R_RIEDEL_INDICES,
    NORIEDEL_INDICES,
    axial_angle_diff_deg,
    build_additive_tversky_tail,
    build_riedelvalve_crest_surface,
    riedel_obliquity_kernels,
    structure_tensor_strike_and_bimodal,
    updip_field_shift,
)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_SUB = ROOT / "data" / "bridge" / "sample_submission.tif"
EXISTING_FAULTS = ROOT / "data" / "bridge" / "existing_faults.tif"


def test_feature_partition_and_zero_catalogue_source():
    assert len(FEATURE_NAMES) == 32
    assert len(set(FEATURE_NAMES)) == 32
    assert len(GROUP_R_RIEDEL_INDICES) == 8
    assert len(NORIEDEL_INDICES) == 23
    assert set(GROUP_R_RIEDEL_INDICES).isdisjoint(NORIEDEL_INDICES)
    assert 23 not in NORIEDEL_INDICES  # valve_riedel_synergy also dropped in ablation
    src_text = (ROOT / "gems" / "riedelvalve.py").read_text(encoding="utf-8")
    assert "existing_faults" not in src_text
    assert "labels.tif" not in src_text
    assert 'df["dist_known_fault_px"]' not in src_text


def test_structure_tensor_bimodal_isolates_fault_intersections():
    H, W = 56, 64
    valid = np.ones((H, W), dtype=bool)
    valid[:3, :] = False
    y, x = np.meshgrid(np.arange(H, dtype=np.float32), np.arange(W, dtype=np.float32), indexing="ij")
    crossed = np.exp(-(((x - 32.0) / 1.4) ** 2)) + np.exp(-(((y - 28.0) / 1.4) ** 2))
    strike, amp, bimod, coh = structure_tensor_strike_and_bimodal(
        crossed, valid, grad_sigma=1.0, tensor_sigma=2.6
    )
    assert strike.shape == (H, W)
    assert np.all(bimod[~valid] == 0.0)
    # Center of X-intersection must strongly exceed planar limb away from crossing/mask edge
    assert float(bimod[28, 32]) > 25.0 * float(bimod[16, 32])
    assert float(coh[16, 32]) > 0.90
    assert float(coh[28, 32]) < 0.25
    assert float(amp[28, 32]) > 0.0
    with pytest.raises(ValueError):
        structure_tensor_strike_and_bimodal(crossed, valid, grad_sigma=0.0)


def test_axial_angle_and_riedel_obliquity_kernels():
    a = np.deg2rad(np.array([[10.0, 10.0, 10.0, 10.0]], dtype=np.float32))
    b = np.deg2rad(np.array([[10.0, 29.0, 82.0, 171.0]], dtype=np.float32))
    diff = axial_angle_diff_deg(a, b)
    # 10 vs 171 modulo 180 deg is 19 deg!
    np.testing.assert_allclose(diff, [[0.0, 19.0, 72.0, 19.0]], atol=1e-3)

    valid = np.ones_like(a, dtype=bool)
    ones = np.ones_like(a, dtype=np.float32)
    kr, krp = riedel_obliquity_kernels(a, b, ones, ones, valid)
    assert float(kr[0, 1]) > 0.99 and float(kr[0, 3]) > 0.99
    assert float(kr[0, 0]) < 0.15
    assert float(krp[0, 2]) > 0.99 and float(krp[0, 1]) < 0.01


def test_updip_field_shift_projects_hanging_wall_anomaly_to_trace():
    H, W = 40, 60
    valid = np.ones((H, W), dtype=bool)
    _, x = np.meshgrid(np.arange(H, dtype=np.float32), np.arange(W, dtype=np.float32), indexing="ij")
    # Hanging-wall deepens East (+x); deep seismic cloud at col 44 projects updip (-12 px) to col 32
    seis = np.exp(-(((x - 44.0) / 2.0) ** 2)).astype(np.float32)
    shifted = updip_field_shift(seis, np.zeros_like(x), np.ones_like(x), valid, shift_px=12.0)
    assert int(np.argmax(shifted[20])) == 32


def test_crest_and_additive_tversky_tail_invariants():
    rng = np.random.default_rng(42)
    H, W = 64, 64
    valid = np.ones((H, W), dtype=bool)
    p = rng.uniform(0.1, 0.9, size=(H, W)).astype(np.float32)
    ls = rng.uniform(0.0, 1.0, size=(H, W)).astype(np.float32)
    lk = rng.uniform(0.0, 1.0, size=(H, W)).astype(np.float32)
    lsub = rng.uniform(0.0, 1.0, size=(H, W)).astype(np.float32)
    lr = rng.uniform(0.0, 1.0, size=(H, W)).astype(np.float32)
    cr = build_riedelvalve_crest_surface(p, ls, lk, lsub, lr, valid)
    assert cr["S_crest"].dtype == np.float32
    assert np.all((cr["S_crest"] >= 0.0) & (cr["S_crest"] <= 2.0))
    assert np.any(cr["ridge_1d"])

    tail = build_additive_tversky_tail(
        cr["S_crest"], valid, n_primary=20, n_total=55, tail_weight=0.30, min_dist_px=2.5
    )
    assert int((tail == 1.0).sum()) == 20
    assert int(np.isclose(tail, 0.30).sum()) == 35
    assert np.all((tail >= 0.0) & (tail <= 1.0))
    with pytest.raises(ValueError):
        build_additive_tversky_tail(cr["S_crest"], valid, n_primary=30, n_total=20)
    with pytest.raises(ValueError):
        build_additive_tversky_tail(cr["S_crest"], valid, n_primary=10, n_total=20, tail_weight=0.0)


def test_nan_inf_and_empty_mask_edge_cases():
    all_valid = np.ones((24, 24), dtype=bool)
    empty_valid = np.zeros((24, 24), dtype=bool)
    corrupted = np.full((24, 24), np.nan, dtype=np.float32)
    corrupted[4, 4] = np.inf
    corrupted[5, 5] = -np.inf
    corrupted[10:15, 10:15] = 0.7

    for mask in (all_valid, empty_valid):
        st, amp, bim, coh = structure_tensor_strike_and_bimodal(corrupted, mask)
        assert np.isfinite(st).all() and np.isfinite(amp).all()
        assert np.isfinite(bim).all() and np.isfinite(coh).all()
        kr, krp = riedel_obliquity_kernels(corrupted, corrupted, corrupted, corrupted, mask)
        assert np.isfinite(kr).all() and np.isfinite(krp).all()
        up = updip_field_shift(corrupted, corrupted, corrupted, mask)
        assert np.isfinite(up).all()
        cr = build_riedelvalve_crest_surface(
            corrupted, corrupted, corrupted, corrupted, corrupted, mask
        )
        assert np.isfinite(cr["S_crest"]).all() and np.isfinite(cr["E_line"]).all()
        tail = build_additive_tversky_tail(
            corrupted,
            mask,
            n_primary=5,
            n_total=12,
            tail_weight=0.30,
            min_dist_px=1.5,
            require_full=(mask is all_valid),
        )
        assert np.isfinite(tail).all() and np.all((tail >= 0.0) & (tail <= 1.0))
    with pytest.raises(ValueError):
        build_additive_tversky_tail(
            corrupted, empty_valid, n_primary=5, n_total=12, tail_weight=0.30, require_full=True
        )
    with pytest.raises(ValueError):
        riedel_obliquity_kernels(corrupted, corrupted, corrupted, corrupted, all_valid, r_sigma_deg=0.0)


def test_riedelvalve_run_card_and_three_geotiff_artifacts():
    rc_path = ROOT / "evidence" / "riedelvalve_run_card.json"
    dl_rc_path = ROOT / "docs" / "downloads" / "riedelvalve_run_card.json"
    assert rc_path.is_file() and dl_rc_path.is_file()
    assert rc_path.read_bytes() == dl_rc_path.read_bytes()

    rc = json.loads(rc_path.read_text(encoding="utf-8"))
    assert rc["lane"] == "RIEDELVALVE"
    assert rc["date"] == "2026-10-25"
    assert rc["verdict"] == "negative"
    assert rc["submission_eligible"] is False
    assert rc["download_ok"] is True
    assert rc["experiments_run"] == 3
    assert rc["experiment_budget_cap"] == 3
    assert rc["weekly_slots_used"] == 0
    assert len(rc["submission_note"]) <= 140

    # Leakage canaries all <= 0.90
    can = rc["leakage_canaries"]
    assert can["all_pass"] is True
    assert float(can["max_feature_symmetric_auc"]) <= 0.90
    assert float(can["draw_blind_surface_symmetric_auc"]) <= 0.90
    assert len(can["features"]) == 33  # 32 single features + 1 draw-blind OOF surface

    # Holdout evidence classes and paired N90K lift CI > 0
    st = rc["holdout_dti"]["static_deployment_d_cat_gt_2"]
    r2 = rc["holdout_dti"]["strict_draw_blind_rule2_d_visible_gt_2"]
    assert rc["holdout_dti"]["evidence_class"] == "HOLDOUT-DTI"
    assert rc["holdout_dti"]["evaluator_version"] == "gems57-pooled-hide-v2"
    assert rc["holdout_dti"]["withheld_positive_pixels"] == 22663
    delta_n90k = st["paired_deltas_vs_riedel_n90k"]["riedelvalve"]
    assert delta_n90k["delta"] > 0.0 and delta_n90k["ci95"][0] > 0.0
    assert r2["scores"]["riedel_n90k"]["dti"] > r2["scores"]["riedelvalve"]["dti"]
    assert rc["usgs_sgmc_off_catalogue_proxy"]["riedel_n90k"]["dti"] > 0.11

    # Literal witness and dual-reading uniqueness recorded honestly
    lit = rc["registry_uniqueness"]["literal_public_rule_status"]
    assert lit["unique_under_literal_rule"] is False
    assert lit["literal_forward_overlap_3px"] == 1.0
    pub_n90k = rc["registry_uniqueness"]["public_102repo_registry"]["riedel_n90k"]
    assert pub_n90k["dual_reading_unique"] is True
    assert pub_n90k["worst_operative_overlap_3px"] <= 0.70

    # Verify all 3 GeoTIFFs, ZIPs, and -audit.json sidecars on disk
    assert set(rc["artifacts"].keys()) == {"riedelvalve", "riedel_n90k", "noriedel_ablation"}
    for arm, art in rc["artifacts"].items():
        tif = ROOT / art["file_zeros"]
        zpath = ROOT / art["file_zip"]
        apath = ROOT / art["file_audit"]
        assert tif.is_file() and zpath.is_file() and apath.is_file()
        assert sha256_file(tif) == art["sha256_zeros"]
        assert sha256_file(zpath) == art["sha256_zip"]
        with zipfile.ZipFile(zpath) as zf:
            names = zf.namelist()
            assert len(names) == 1 and names[0].endswith("-zeros.tif")
        ok, detail = summarise(
            run_gates(
                str(tif),
                str(SAMPLE_SUB),
                str(EXISTING_FAULTS),
                prune_radius=2,
                require_submission_encoding=True,
            )
        )
        assert ok, f"{arm} failed gates:\n{detail}"
        with rasterio.open(tif) as ds:
            arr = ds.read(1)
            assert int((arr > 0).sum()) == art["n_positive_pixels"]
        adoc = json.loads(apath.read_text(encoding="utf-8"))
        assert adoc["verdict"] == "negative"
        assert adoc["submission_eligible"] is False
        assert adoc["download_ok"] is True
        assert len(adoc["submission_note"]) <= 140

    # Verify ledger, mechanism cards, docs & HTML links
    with (ROOT / "ledger" / "submissions.csv").open(encoding="utf-8") as f:
        ledger_ids = {r["id"] for r in csv.DictReader(f)}
    mc = json.loads((ROOT / "ledger" / "mechanism_cards.json").read_text(encoding="utf-8"))
    index_html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    exec_html = (ROOT / "docs" / "executive-summary.html").read_text(encoding="utf-8")
    readme_md = (ROOT / "README.md").read_text(encoding="utf-8")
    for arm, art in rc["artifacts"].items():
        assert art["stem"] in ledger_ids
        assert art["stem"] in mc
        fname = Path(art["file_zeros"]).name
        assert fname in index_html
        assert fname in exec_html
        assert fname in readme_md
    assert (ROOT / "docs" / "HYPOTHESES_20261025_RIEDELVALVE.md").is_file()
    assert (ROOT / "docs" / "ANALYSIS_20261025_RIEDELVALVE.md").is_file()
    primary_fname = Path(rc["artifacts"][rc["primary_arm"]]["file_zeros"]).name
    primary_sha = rc["raster_sha256"]
    for cross_doc in (
        "SESSION_PROMPT.md",
        "SLOT_PLAN.md",
        "docs/NEXT_STEPS.md",
        "docs/SUBMIT.html",
        "docs/HYPOTHESES.html",
    ):
        txt = (ROOT / cross_doc).read_text(encoding="utf-8")
        assert primary_fname in txt or "riedel_n90k" in txt, f"missing RIEDELVALVE in {cross_doc}"
        if cross_doc in ("SESSION_PROMPT.md", "SLOT_PLAN.md"):
            assert primary_sha in txt, f"missing SHA in {cross_doc}"
