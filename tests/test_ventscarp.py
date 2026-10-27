"""Automated regression and artifact-integrity tests for Lane VENTSCARP."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio

from gems import ledger as ledger_mod
from gems.ventscarp import (
    FEATURE_NAMES,
    NOVENT_INDICES,
    anisotropic_strike_plume,
    build_soft_tversky_allocation,
    is_hydrothermal_paleo_vent,
    subpixel_scarp_excess,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_tufa_mimic_filter_and_feature_stack_partition():
    assert is_hydrothermal_paleo_vent("Sinter")[0] is True
    assert is_hydrothermal_paleo_vent("Sinter")[1] > 1.0
    assert is_hydrothermal_paleo_vent("Explosion craters")[0] is True
    assert is_hydrothermal_paleo_vent("Silica-cemented sand")[0] is True
    assert is_hydrothermal_paleo_vent("Travertine")[0] is True
    assert is_hydrothermal_paleo_vent("Carbonate (travertine) cemented fan gravel")[0] is True
    assert is_hydrothermal_paleo_vent("Tufa") == (False, 0.0)
    assert is_hydrothermal_paleo_vent("Shoreline tufa mound") == (False, 0.0)
    assert is_hydrothermal_paleo_vent("") == (False, 0.0)
    assert is_hydrothermal_paleo_vent(None) == (False, 0.0)

    assert len(FEATURE_NAMES) == 26
    assert len(NOVENT_INDICES) == 17
    kept_names = {FEATURE_NAMES[i] for i in NOVENT_INDICES}
    for vent_feat in (
        "paleo_vent_aniso_plume",
        "probe_2mdab_aniso_plume",
        "active_thermal_spring_aniso",
        "unified_vent_district_halo",
        "rad_k_over_th_z",
        "rad_u_over_th_z",
        "grauch_mag_demag_residual",
        "mt_claycap_perimeter_grad",
        "heatflow_scarp_coupling",
    ):
        assert vent_feat not in kept_names


def test_subpixel_scarp_excess_and_anisotropic_strike_plume():
    valid = np.ones((64, 64), dtype=bool)
    valid[:4, :] = False
    s100 = np.full((64, 64), 4.0, dtype=np.float32)
    s10_flat = np.full((64, 64), 3.8, dtype=np.float32)
    assert float(subpixel_scarp_excess(s10_flat, s100, valid).max()) == 0.0

    s10_scarp = s10_flat.copy()
    s10_scarp[32, :] = 14.0
    exc = subpixel_scarp_excess(s10_scarp, s100, valid)
    assert float(exc[32, 32]) > 0.5
    assert float(exc[10, 10]) == 0.0
    assert float(exc[~valid].max()) == 0.0

    src = np.zeros((128, 128), dtype=np.float32)
    src[64, 64] = 10.0
    foot = np.ones((128, 128), dtype=bool)
    foot[:5, :] = False
    plume = anisotropic_strike_plume(
        src, foot, sigma_parallel_px=12.0, sigma_perp_px=2.5, strike_deg_east_of_north=18.0
    )
    assert plume.dtype == np.float32
    assert float(plume[~foot].max()) == 0.0
    assert float(plume.min()) >= 0.0
    along_val = float(plume[64 - 10, 64 + 3])
    across_val = float(plume[64 - 3, 64 - 10])
    assert along_val > 2.5 * across_val


def test_soft_tversky_allocation_respects_range_mask_and_mass_budget():
    rng = np.random.default_rng(92)
    score = rng.uniform(0.0, 1.0, size=(120, 120)).astype(np.float32)
    pool = np.ones((120, 120), dtype=bool)
    pool[:8, :] = False
    pool[:, :10] = False

    arr = build_soft_tversky_allocation(
        score,
        pool,
        n_peaks=180,
        target_mass=120.0,
        min_dist_px=2.9,
        p_min=0.35,
    )
    assert arr.dtype == np.float32
    assert np.isfinite(arr).all()
    assert float(arr.min()) >= 0.0
    assert float(arr.max()) <= 1.0
    assert float(arr[~pool].max()) == 0.0
    pos = arr[arr > 0]
    assert 50 <= pos.size <= 180
    assert float(pos.min()) >= 0.3499
    assert abs(float(arr.sum()) - 120.0) < 0.5


def test_ventscarp_external_manifest_excludes_contaminated_and_biased_files():
    doc = json.loads((ROOT / "registry" / "ventscarp_external_manifest.json").read_text(encoding="utf-8"))
    assert len(doc["files"]) == 7
    paths = {entry["path"] for entry in doc["files"]}
    assert "data/external/gdr_volcanic_vents_in_footprint.csv" not in paths
    assert "data/external/lidar_scarp_features_u8.tif" not in paths
    for entry in doc["files"]:
        assert len(entry["sha256"]) == 64
        assert entry["bytes"] > 0


def test_ventscarp_artifacts_receipts_and_run_card_integrity():
    for name in ("ventscarp_run_card.json", "ventscarp_holdout.json", "ventscarp_uniqueness.json"):
        src = EVIDENCE / name
        dl = DOCS / "downloads" / name
        assert src.is_file() and dl.is_file(), f"missing {name}"
        assert src.read_bytes() == dl.read_bytes(), f"byte mismatch for {name}"

    card = json.loads((EVIDENCE / "ventscarp_run_card.json").read_text(encoding="utf-8"))
    holdout = json.loads((EVIDENCE / "ventscarp_holdout.json").read_text(encoding="utf-8"))
    uniq = json.loads((EVIDENCE / "ventscarp_uniqueness.json").read_text(encoding="utf-8"))

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

    # Verify all 26 single-feature + 1 LOQO OOF surface canaries individually <= 0.90
    assert holdout["leakage_canaries"]["all_pass"] is True
    assert len(holdout["leakage_canaries"]["features"]) == 27
    for feat, row in holdout["leakage_canaries"]["features"].items():
        assert 0.50 <= row["symmetric_auc"] <= 0.90, f"canary out of range for {feat}"

    # Verify 102-repo dual-reading uniqueness across all 3 arms
    assert uniq["public_inventory"]["repos_scanned"] == 102
    assert uniq["public_inventory"]["external_compatible_rasters"] >= 1350
    for arm in ("ventscarp", "scarp10m_novent", "ventscarp_soft"):
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
    r2 = holdout["strict_draw_blind_rule2_holdout_dti"]["scores"]
    assert r2["ventscarp"]["dti"] > r2["scarp10m_novent"]["dti"]
    assert r2["ventscarp"]["dti"] > r2["ventscarp_soft"]["dti"]
    assert r2["ventscarp"]["dti"] > r2["H19_5"]["dti"]
    assert r2["ventscarp"]["dti"] > r2["R0"]["dti"]
    soft_pair = holdout["strict_draw_blind_rule2_holdout_dti"]["paired_differences"]["ventscarp_soft"]
    assert soft_pair["ci95"][0] > 0.0  # binary strictly beats soft [0.35, 1.00] dilution

    # Independently reopen all 3 GeoTIFFs, ZIPs, audits, and ledger rows
    with rasterio.open(ROOT / "data" / "bridge" / "sample_submission.tif") as ref:
        ref_crs = ref.crs
        ref_shape = ref.shape
        ref_transform = ref.transform
        foot = np.isfinite(ref.read(1))

    ledger_by_id = {r["id"]: r for r in ledger_mod.load()}
    index_html = (DOCS / "archive.html").read_text(encoding="utf-8")
    exec_html = (DOCS / "executive-summary.html").read_text(encoding="utf-8")
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
            assert ds.crs == ref_crs
            assert ds.shape == ref_shape
            assert ds.transform == ref_transform
            assert ds.dtypes[0] == "float32"
            arr = ds.read(1)
            assert np.isfinite(arr).all()
            assert float(arr.min()) >= 0.0
            assert float(arr.max()) <= 1.0
            assert float(arr[~foot].max()) == 0.0
            assert int((arr > 0).sum()) == art["n_positive_pixels"]

        assert art["stem"] in ledger_by_id
        assert ledger_by_id[art["stem"]]["sha256"] == art["sha256_zeros"]
        assert f"downloads/{tif_path.name}" in index_html
        assert f"downloads/{tif_path.name}" in exec_html
        assert f"docs/downloads/{tif_path.name}" in readme_txt
