"""Automated regression and artifact-integrity tests for Lane RIEDELVENT."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio

from gems import ledger as ledger_mod
from gems.riedelvent import (
    ABLATED_NOVENT_INDICES,
    FEATURE_NAMES,
    build_additive_tail_allocation,
    flexural_hinge_field,
    riedel_obliquity_field,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"
SAMPLE_SUB_CANDIDATES = (
    ROOT / ".cache" / "gems_inputs" / "bridge" / "sample_submission.tif",
    ROOT / "data" / "bridge" / "sample_submission.tif",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sample_sub_path() -> Path | None:
    for p in SAMPLE_SUB_CANDIDATES:
        if p.is_file():
            return p
    return None


def test_riedelvent_feature_partition():
    assert len(FEATURE_NAMES) == 30
    assert len(ABLATED_NOVENT_INDICES) == 17
    kept_names = {FEATURE_NAMES[i] for i in ABLATED_NOVENT_INDICES}
    for excluded_feat in (
        "paleo_vent_aniso_plume",
        "probe_2mdab_aniso_plume",
        "active_thermal_spring_aniso",
        "unified_vent_district_halo",
        "rad_k_over_th_z",
        "rad_u_over_th_z",
        "grauch_mag_demag_residual",
        "mt_claycap_perimeter_grad",
        "heatflow_scarp_coupling",
        "riedel_obliquity_index",
        "riedel_strain_coupling",
        "flexure_hinge_curvature",
        "flexure_gravity_concordance",
    ):
        assert excluded_feat not in kept_names


def test_riedel_obliquity_and_flexural_hinge_operators():
    h, w = 96, 96
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    valid = np.ones((h, w), dtype=bool)
    valid[:6, :] = False

    # Master field striking N0E (gradient along x); fine field striking N19E
    theta_master = np.deg2rad(0.0)
    theta_fine = np.deg2rad(19.0)
    master = np.tanh((xx - 48.0) * np.cos(theta_master) / 6.0).astype(np.float32)
    fine_oblique = np.tanh(
        ((xx - 48.0) * np.cos(theta_fine) - (yy - 48.0) * np.sin(theta_fine)) / 2.5
    ).astype(np.float32)
    fine_parallel = np.tanh((xx - 48.0) * np.cos(theta_master) / 2.5).astype(np.float32)

    r_oblique, d_oblique = riedel_obliquity_field(fine_oblique, master, valid)
    r_parallel, _ = riedel_obliquity_field(fine_parallel, master, valid)
    assert r_oblique.dtype == np.float32 and d_oblique.dtype == np.float32
    assert np.isfinite(r_oblique).all() and np.isfinite(d_oblique).all()
    assert float(r_oblique[~valid].max()) == 0.0
    assert float(r_oblique.min()) >= 0.0
    assert float(r_oblique[40:56, 40:56].mean()) > 2.0 * float(r_parallel[40:56, 40:56].mean())

    # Flexural hinge: basement deepens across x=48 while gravity drops across x=48
    depth_m = (50.0 + 900.0 / (1.0 + np.exp(-(xx - 48.0) / 3.0))).astype(np.float32)
    iso_grav = (-10.0 - 12.0 / (1.0 + np.exp(-(xx - 48.0) / 3.0))).astype(np.float32)
    curv, conc = flexural_hinge_field(depth_m, iso_grav, valid)
    assert curv.dtype == np.float32 and conc.dtype == np.float32
    assert np.isfinite(curv).all() and np.isfinite(conc).all()
    assert float(curv[~valid].max()) == 0.0 and float(conc[~valid].max()) == 0.0
    assert float(curv[:, 44:54].max()) > 0.1
    assert float(conc[:, 44:54].max()) > 0.02


def test_additive_tail_allocation_respects_primary_unit_and_tail_weights():
    rng = np.random.default_rng(20261025)
    score = rng.uniform(0.0, 1.0, size=(128, 128)).astype(np.float32)
    pool = np.ones((128, 128), dtype=bool)
    pool[:8, :] = False
    pool[:, :8] = False

    arr = build_additive_tail_allocation(
        score,
        pool,
        n_core=100,
        n_total=160,
        tail_weight=0.30,
        min_dist_px=3.30,
    )
    assert arr.dtype == np.float32
    assert np.isfinite(arr).all()
    assert float(arr.min()) >= 0.0
    assert float(arr.max()) <= 1.0
    assert float(arr[~pool].max()) == 0.0

    ones = int((np.isclose(arr, 1.0)).sum())
    tails = int((np.isclose(arr, 0.30, atol=1e-5)).sum())
    pos = int((arr > 0).sum())
    assert ones == 100
    assert tails == 60
    assert pos == 160
    assert abs(float(arr.sum()) - (100 * 1.0 + 60 * 0.30)) < 1e-3


def test_riedelvent_artifacts_receipts_and_run_card_integrity():
    for name in ("riedelvent_run_card.json", "riedelvent_holdout.json", "riedelvent_uniqueness.json"):
        src = EVIDENCE / name
        dl = DOCS / "downloads" / name
        assert src.is_file() and dl.is_file(), f"missing {name}"
        assert src.read_bytes() == dl.read_bytes(), f"byte mismatch for {name}"

    card = json.loads((EVIDENCE / "riedelvent_run_card.json").read_text(encoding="utf-8"))
    holdout = json.loads((EVIDENCE / "riedelvent_holdout.json").read_text(encoding="utf-8"))
    uniq = json.loads((EVIDENCE / "riedelvent_uniqueness.json").read_text(encoding="utf-8"))

    for req_key in (
        "hypothesis",
        "mechanism",
        "non_fault_mimic",
        "named_non_fault_process_that_could_mimic_it",
        "holdout_dti",
        "correlation_overlap_vs_registry",
        "raster_sha256",
        "validator_output",
        "submission_name",
        "note",
        "verdict",
    ):
        assert req_key in card, f"missing Run Card key: {req_key}"

    assert card["verdict"] == "negative"
    assert card["submission_eligible"] is False
    assert card["weekly_slots_used"] == 0
    assert card["experiments_used"] == 3
    assert len(card["note"]) <= 140
    assert card["leakage_canary"]["all_pass"] is True
    assert card["leakage_canary"]["max_single_feature_symmetric_auc"] <= 0.90
    assert card["leakage_canary"]["draw_blind_surface_symmetric_auc"] <= 0.90

    # Verify all 30 single-feature + 1 LOQO OOF surface canaries individually <= 0.90
    assert holdout["leakage_canaries"]["all_pass"] is True
    assert len(holdout["leakage_canaries"]["features"]) == 31
    for feat, row in holdout["leakage_canaries"]["features"].items():
        assert 0.50 <= row["symmetric_auc"] <= 0.90, f"canary out of range for {feat}"

    # Verify 102-repo dual-reading uniqueness across all 3 arms
    assert uniq["public_inventory"]["repos_scanned"] == 102
    assert uniq["public_inventory"]["external_compatible_rasters"] >= 1350
    for arm in ("riedelvent", "riedel_novent", "riedelvent_tail"):
        assert uniq["local_summary"][arm]["local_unique"] is True
        assert uniq["local_summary"][arm]["worst_forward_overlap_3px"] <= 0.70
        assert uniq["local_summary"][arm]["worst_surface_abs_spearman"] <= 0.90
        pub = uniq["public_102repo_summary"][arm]
        assert pub["dual_reading_unique"] is True
        assert pub["worst_operative_overlap_3px"] <= 0.70
        assert pub["dot_fields_le_50k_worst_overlap_3px"] <= 0.70
        assert pub["worst_surface_abs_spearman"] <= 0.90
        assert pub["literal_worst_overlap_3px"] == 1.0

    # Verify statistical holdout findings
    st = holdout["static_deployment_holdout_dti"]["scores"]
    st_pairs = holdout["static_deployment_holdout_dti"]["paired_differences"]
    st_tail_pairs = holdout["static_deployment_holdout_dti_tail_candidate"]["paired_differences"]
    r2 = holdout["strict_draw_blind_rule2_holdout_dti"]["scores"]
    r2_tail_pairs = holdout["strict_draw_blind_rule2_holdout_dti_tail_candidate"]["paired_differences"]
    sgmc = holdout["usgs_sgmc_off_catalogue_proxy"]

    # riedelvent beats VENTSCARP, LISTRICDIP_updip50, and R0 on static holdout with 95% CI > 0
    assert st["riedelvent"]["dti"] > st["VENTSCARP_ventscarp"]["dti"]
    assert st_pairs["VENTSCARP_ventscarp"]["ci95"][0] > 0.0
    assert st_pairs["LISTRICDIP_updip50"]["ci95"][0] > 0.0
    assert st_pairs["R0"]["ci95"][0] > 0.0

    # riedelvent_tail strictly beats binary riedelvent on static, Rule-2, and SGMC with 95% CI > 0
    assert st["riedelvent_tail"]["dti"] > st["riedelvent"]["dti"]
    assert st_tail_pairs["riedelvent"]["ci95"][0] > 0.0
    assert st_tail_pairs["VENTSCARP_ventscarp"]["ci95"][0] > 0.0
    assert r2["riedelvent_tail"]["dti"] > r2["riedelvent"]["dti"]
    assert r2_tail_pairs["riedelvent"]["ci95"][0] > 0.0
    assert sgmc["riedelvent_tail"]["dti"] > sgmc["riedelvent"]["dti"]
    assert sgmc["riedelvent_tail"]["dti"] > sgmc["KNICKLOQO_standalone"]["dti"]

    sample_sub = _sample_sub_path()
    ref_crs = ref_shape = ref_transform = foot = None
    if sample_sub is not None:
        with rasterio.open(sample_sub) as ref:
            ref_crs = ref.crs
            ref_shape = ref.shape
            ref_transform = ref.transform
            foot = np.isfinite(ref.read(1))

    ledger_by_id = {r["id"]: r for r in ledger_mod.load()}
    index_html = (DOCS / "index.html").read_text(encoding="utf-8")
    exec_html = (DOCS / "executive-summary.html").read_text(encoding="utf-8")
    submit_html = (DOCS / "SUBMIT.html").read_text(encoding="utf-8")
    readme_txt = (ROOT / "README.md").read_text(encoding="utf-8")

    for arm, art in holdout["artifacts"].items():
        tif_path = ROOT / art["file_zeros"]
        zip_path = ROOT / art["file_zip"]
        aud_path = ROOT / art["file_audit"]
        assert tif_path.is_file() and zip_path.is_file() and aud_path.is_file()
        assert _sha256(tif_path) == art["sha256_zeros"]
        assert _sha256(zip_path) == art["sha256_zip"]
        assert len(art["submission_note"]) <= 140

        aud = json.loads(aud_path.read_text(encoding="utf-8"))
        assert aud["overall_pass"] is True
        assert aud["submission_eligible"] is False
        assert aud["verdict"] == "negative"
        assert aud["sha256_zeros"] == art["sha256_zeros"]
        assert all(g["ok"] for g in aud["gates_zeros"])

        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            assert len(names) == 1 and names[0].endswith(".tif")
            assert hashlib.sha256(zf.read(names[0])).hexdigest() == art["sha256_zeros"]

        with rasterio.open(tif_path) as ds:
            assert ds.count == 1
            assert ds.dtypes[0] == "float32"
            assert ds.shape == (3730, 3292)
            assert int(ds.crs.to_epsg()) == 32611
            if ref_crs is not None:
                assert ds.crs == ref_crs
                assert ds.shape == ref_shape
                assert ds.transform == ref_transform
            arr = ds.read(1)
            assert np.isfinite(arr).all()
            assert float(arr.min()) >= 0.0
            assert float(arr.max()) <= 1.0
            if foot is not None:
                assert float(arr[~foot].max()) == 0.0
            assert int((arr > 0).sum()) == art["n_positive_pixels"]

        assert art["stem"] in ledger_by_id
        assert ledger_by_id[art["stem"]]["sha256"] == art["sha256_zeros"]
        assert f"downloads/{tif_path.name}" in index_html
        assert f"downloads/{tif_path.name}" in exec_html
        assert f"downloads/{tif_path.name}" in submit_html
        assert f"docs/downloads/{tif_path.name}" in readme_txt
