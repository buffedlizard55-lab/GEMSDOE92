"""End-to-end regression & protocol safety tests for 2026-10-29 LIDAR-SINTERVALVE."""
from __future__ import annotations

import ast
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import pytest
import rasterio

import validate_submission
from gems import gates, lidar_sintervalve
from gems57 import validate as gems57_validate
from scripts import check_site, render_site_v3

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DL = DOCS / "downloads"
EVID = ROOT / "evidence"

TIF_NAME = "gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e-zeros.tif"
ZIP_NAME = "gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e-zeros.zip"
CARD_NAME = "gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e_run_card.json"
AUDIT_NAME = "gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e-zeros-audit.json"
EXPECTED_SHA256 = "0db6046848adf1ac78d71baa34a49ae54c75018542ca50c3d2fb3e479505780e"


def test_lidar_sintervalve_never_reads_catalogue_distance_column() -> None:
    """Guard IR-1029-6: external CSVs have dist_known_fault_px; code must never touch it."""
    src = (ROOT / "gems" / "lidar_sintervalve.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    string_literals = [
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    assert "dist_known_fault_px" not in string_literals
    assert len(lidar_sintervalve.LIDAR_SINTERVALVE_NAMES) == 8
    assert len(lidar_sintervalve.EXPECTED_TRAINING_BAND_TAGS) == 19


def test_synthetic_quantile_bridge_and_hydro_plume_are_finite_and_in_unit_range() -> None:
    rng = np.random.default_rng(42)
    shape = (20, 20)
    valid = np.ones(shape, dtype=bool)
    has_lidar = np.zeros(shape, dtype=bool)
    has_lidar[:15, :] = True
    X_10m_valid = rng.normal(size=(shape[0] * shape[1], 4)).astype(np.float32)
    raw_1m = (0.7 * X_10m_valid[:, 0] - 0.4 * X_10m_valid[:, 1] + 0.1 * rng.normal(size=400)).reshape(shape).astype(np.float32)
    quad_valid = np.repeat(np.arange(4, dtype=np.int32), 100)
    q = lidar_sintervalve.quantile_bridge_1m_to_10m(raw_1m, has_lidar, X_10m_valid, valid, quad_valid)
    assert q.shape == shape and q.dtype == np.float32
    assert np.isfinite(q).all()
    assert float(q.min()) >= 0.0 and float(q.max()) <= 1.0
    assert abs(float(q[has_lidar].mean()) - float(q[~has_lidar].mean())) < 0.08


def test_e1_canaries_and_e2_holdout_receipts_pass_protocol_gates() -> None:
    e1 = json.loads((EVID / "lidarsintervalve_e1_canaries_20261029.json").read_text(encoding="utf-8"))
    assert e1["gate_pass"] is True and e1["leakage_flag"] is False
    assert e1["n_features_tested"] == 54
    assert e1["max_symmetric_auc_all_54"] <= 0.90
    assert e1["max_symmetric_auc_h92g1_9"] <= 0.90
    for seam in e1["quantile_bridge_seam_parity"]:
        assert seam["abs_mean_gap"] < 0.02

    e2 = json.loads((EVID / "lidarsintervalve_e2_holdout_20261029.json").read_text(encoding="utf-8"))
    assert e2["evaluator_version"] == "gems57-pooled-hide-v2"
    assert e2["withheld_positive_pixels"] == 22663
    lsv_far = e2["scores"]["lidarsintervalve_far"]["dti"]
    nx_far = e2["scores"]["control_netexpand_far"]["dti"]
    r0_rec = e2["scores"]["control_H19_5"]["dti"]
    assert lsv_far == pytest.approx(0.17861884985575596, abs=1e-9)
    assert lsv_far > nx_far > r0_rec
    assert e2["paired_by_candidate"]["lidarsintervalve_far"]["control_H19_5"]["ci95"][0] > 0.06


def test_e3_geotiff_run_card_and_validator_are_byte_bound_and_fail_closed(capsys) -> None:
    tif_path = DL / TIF_NAME
    zip_path = DL / ZIP_NAME
    card_path = DL / CARD_NAME
    audit_path = DL / AUDIT_NAME
    feed_path = DL / "lidarsintervalve_readiness_20261029.json"
    for p in (tif_path, zip_path, card_path, audit_path, feed_path):
        assert p.is_file(), f"missing {p}"

    sha = hashlib.sha256(tif_path.read_bytes()).hexdigest()
    assert sha == EXPECTED_SHA256

    card = json.loads(card_path.read_text(encoding="utf-8"))
    ev_card = json.loads((EVID / "lidarsintervalve_latest_20261029.json").read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    feed = json.loads(feed_path.read_text(encoding="utf-8"))
    assert card == ev_card
    assert card["raster_sha256"] == sha == audit["sha256_zeros"] == feed["raster_sha256"]
    assert card["verdict"] == "negative" and card["submission_eligible"] is False
    assert 0 < len(card["note"]) <= 140
    for key in (
        "hypothesis", "mechanism", "named_non_fault_mimic_process", "holdout_dti",
        "correlation_overlap_vs_registry", "raster_sha256", "validator_output",
        "submission_name", "note", "verdict",
    ):
        assert key in card

    pi1 = card["correlation_overlap_vs_registry"]["final_dots_pi1"]
    assert pi1["pi1_pass"] is True
    assert pi1["worst_overlap_3px"] <= 0.70
    assert pi1["worst_abs_rho"] <= 0.90
    assert card["correlation_overlap_vs_registry"]["registry_unique_sha256"] == 2263

    with zipfile.ZipFile(zip_path) as zf:
        assert zf.namelist() == [TIF_NAME]
        assert hashlib.sha256(zf.read(TIF_NAME)).hexdigest() == sha

    with rasterio.open(ROOT / "data/bridge/sample_submission.tif") as ds_ref:
        foot = np.isfinite(ds_ref.read(1))
    with rasterio.open(ROOT / "data/bridge/existing_faults.tif") as ds_cat:
        cat = ds_cat.read(1) > 0.5
    ok, _ = gates.summarise(
        gates.run_gates(
            str(tif_path),
            str(ROOT / "data/bridge/sample_submission.tif"),
            str(ROOT / "data/bridge/existing_faults.tif"),
            prune_radius=2,
            require_submission_encoding=True,
        )
    )
    assert ok is True
    gems57_validate.assert_submittable(gems57_validate.validate(tif_path, foot, cat))

    # Fail-closed CLI check: format passes locally, but verdict=negative exits 1 with DO NOT SUBMIT
    rc = validate_submission.main([str(tif_path)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "RESULT: PASS (11 gates)" in out
    assert "DO NOT SUBMIT" in out
    assert ("OK TO " + "SUBMIT") not in out


def test_20261029_site_pages_have_no_conflict_markers_and_match_renderer() -> None:
    expected = render_site_v3.render()
    for path, text in expected.items():
        assert path.read_text(encoding="utf-8") == text
        assert "<<<<<<<" not in text and ">>>>>>>" not in text
        assert ("OK TO " + "SUBMIT") not in text

    exec29 = (DOCS / "executive-summary-20261029-lidarsintervalve.html").read_text(encoding="utf-8")
    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36", "GEMSDOE92"):
        assert site in exec29
    assert "0.2784" in exec29 and "0.178619" in exec29
    assert "DO NOT SUBMIT" in exec29

    problems: list[str] = []
    check_site.check_lidarsintervalve_20261029(problems)
    assert problems == []
