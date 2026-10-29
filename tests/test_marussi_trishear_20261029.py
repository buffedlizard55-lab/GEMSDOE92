"""End-to-end tests for the 2026-10-29 MARUSSI-TRISHEAR lane and lbmc1 0.2784 fleet audit."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np
import rasterio

from gems import marussi_trishear as mt

ROOT = Path(__file__).resolve().parents[1]
STEM = "gemsdoe92-marussitrishear-34000dots-20261029-236171af"
EXPECTED_SHA256 = "f8f8703e4f8efb8f3397ecc5dc8c0fd68b06c64a089a89b02ee7a91395b3a59b"


def test_clean_sentinel_edt_removes_flt_min_without_overflow():
    y, x = np.mgrid[0:64, 0:64].astype(np.float32)
    arr = np.sin(0.1 * x) + 0.5 * np.cos(0.1 * y)
    arr[20:24, 30:33] = -3.4028235e38
    arr[5, 5] = np.nan
    filled, ok = mt.clean_sentinel_edt(arr)
    assert not ok[21, 31] and not ok[5, 5]
    assert np.isfinite(filled).all()
    assert float(np.max(np.abs(filled))) < 5.0


def test_marussi_d2d_separates_elongate_fault_step_from_3d_plug():
    """Pedersen & Rasmussen (1990): a 2D fault step has det(T) -> 0 and D_2D -> 1 vs a 3D plug."""
    yy, xx = np.mgrid[-64:64, -64:64].astype(np.float32)
    # 1D/2D elongate N-S basement fault step: depends only on xx
    step_2d = np.tanh(xx / 6.0).astype(np.float32)
    inv_2d = mt.marussi_tensor_invariants(step_2d, lambda_min_px=4.0, lambda_max_px=96.0)
    assert inv_2d["d2d"].shape == (128, 128)
    assert np.isfinite(inv_2d["d2d"]).all()
    assert float(inv_2d["d2d"].min()) >= 0.0 and float(inv_2d["d2d"].max()) <= 1.0
    # Along the central fault trace (xx ~ 0, away from boundary), D_2D must be near 1.0
    d2d_fault = float(np.median(inv_2d["d2d"][32:96, 62:66]))
    assert d2d_fault > 0.92

    # 3D radially symmetric volcanic plug / pluton: det(T) != 0 so D_2D drops substantially
    r2 = xx * xx + yy * yy
    plug_3d = (1.0 / np.sqrt(r2 + 12.0 ** 2)).astype(np.float32)
    inv_3d = mt.marussi_tensor_invariants(plug_3d, lambda_min_px=4.0, lambda_max_px=96.0)
    d2d_plug_summit = float(np.median(inv_3d["d2d"][60:68, 60:68]))
    assert d2d_plug_summit < 0.45
    assert d2d_fault - d2d_plug_summit > 0.50


def test_cooper_terracing_and_salem_true_tilt_finite():
    yy, xx = np.mgrid[-48:48, -48:48].astype(np.float32)
    f = (np.tanh((xx * 0.8 + yy * 0.6) / 5.0) * 50.0).astype(np.float32)
    ter = mt.cooper_terracing_gradient(f)
    tilt_gate = mt.salem_true_rtp_tilt_depth_gate(f)
    assert ter.shape == f.shape and np.isfinite(ter).all() and float(ter.min()) >= 0.0
    assert tilt_gate.shape == f.shape and np.isfinite(tilt_gate).all()
    assert float(tilt_gate.min()) >= 0.0 and float(tilt_gate.max()) <= 1.0001


def test_marussi_candidate_bytes_gates_and_run_card_consistency():
    tif = ROOT / "docs" / "downloads" / f"{STEM}-zeros.tif"
    zpath = ROOT / "docs" / "downloads" / f"{STEM}-zeros.zip"
    rc_ev = ROOT / "evidence" / f"{STEM}_run_card.json"
    rc_dl = ROOT / "docs" / "downloads" / f"{STEM}_run_card.json"
    audit_p = ROOT / "docs" / "downloads" / f"{STEM}-zeros-audit.json"
    ready_p = ROOT / "docs" / "downloads" / "marussi_trishear_readiness_20261029.json"

    for p in (tif, zpath, rc_ev, rc_dl, audit_p, ready_p):
        assert p.is_file(), f"missing {p}"

    sha = hashlib.sha256(tif.read_bytes()).hexdigest()
    assert sha == EXPECTED_SHA256
    assert rc_ev.read_bytes() == rc_dl.read_bytes()

    with zipfile.ZipFile(zpath) as zf:
        assert zf.namelist() == [tif.name]
        assert hashlib.sha256(zf.read(tif.name)).hexdigest() == EXPECTED_SHA256

    card = json.loads(rc_ev.read_text(encoding="utf-8"))
    audit = json.loads(audit_p.read_text(encoding="utf-8"))
    ready = json.loads(ready_p.read_text(encoding="utf-8"))

    assert card["raster_sha256"] == EXPECTED_SHA256
    assert audit["sha256_zeros"] == EXPECTED_SHA256
    assert ready["raster_sha256"] == EXPECTED_SHA256
    assert card["verdict"] == "negative" and card["submission_eligible"] is False
    assert ready["verdict"] == "negative" and ready["submission_eligible"] is False
    assert audit["overall_pass"] is True and len(audit["gates_zeros"]) == 11
    assert all(g["ok"] for g in audit["gates_zeros"])
    assert 0 < len(card["note"]) <= 140

    # Canaries + Uniqueness + Holdout gates
    assert card["leakage_canaries"]["all_pass"] is True
    assert card["leakage_canaries"]["max_symmetric_auc_all_24_channels"] <= 0.90
    u = card["uniqueness"]
    assert u["registry_rasters"] == 2262
    assert u["pi1_surface_duplicate"] is False and u["surface_worst_overlap"] <= 0.70
    assert u["surface_worst_abs_rho"] <= 0.90
    assert u["pi1_final_dots_duplicate"] is False and u["final_worst_overlap"] <= 0.70
    assert u["final_worst_abs_rho"] <= 0.90
    assert u["literal_reading"]["duplicate_under_literal"] is True

    h = card["holdout_dti"]
    assert h["evaluator_version"] == "gems57-pooled-hide-v2"
    assert h["withheld_positive_pixels"] == 22663
    assert h["e3_deployed_recipe"]["dti"] > h["r0_recipe_control"]["dti"]
    assert h["paired_e3_vs_r0_recipe"]["ci95"][0] > 0.0

    # Direct pixel check on GeoTIFF
    with rasterio.open(tif) as ds, rasterio.open(ROOT / "data" / "bridge" / "sample_submission.tif") as ref:
        assert ds.crs == ref.crs and ds.shape == ref.shape and ds.transform == ref.transform
        assert ds.nodata is None
        arr = ds.read(1)
        ref_arr = ref.read(1)
    assert arr.dtype == np.float32
    assert np.isfinite(arr).all()
    assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
    assert int(np.sum(arr > 0.5)) == 34000
    assert np.all(arr[~np.isfinite(ref_arr)] == 0.0)


def test_20261029_fleet_and_lbm_v3_evidence():
    oot = json.loads((ROOT / "evidence" / "lbm_oot_20261029.json").read_text(encoding="utf-8"))
    lbm3 = json.loads((ROOT / "evidence" / "lbm_v3_20261029.json").read_text(encoding="utf-8"))
    fleet = json.loads((ROOT / "evidence" / "fleet_audit_20261029.json").read_text(encoding="utf-8"))

    assert oot["rows"][0]["claim_20261029"] == 0.2784
    assert oot["passive_3_oot_rmse"] < 0.025
    assert lbm3["n_matched_claims"] == 131 and lbm3["logo_spearman"] > 0.95
    assert abs(lbm3["lbmc1_logo"] - 0.2784) < 0.01
    assert fleet["registry_scope"]["unique_sha256"] == 2262


def test_ledger_pure_lf_and_no_conflict_markers():
    raw_csv = (ROOT / "ledger" / "submissions.csv").read_bytes()
    assert b"\r" not in raw_csv
    with (ROOT / "ledger" / "submissions.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    by_id = {r["id"]: r for r in rows}
    assert STEM in by_id and by_id[STEM]["sha256"] == EXPECTED_SHA256
    assert by_id[STEM]["receipt_score"] == ""
    assert by_id["gemsdoe92-lbmc1-35801dots-20261027-89a660f6"]["receipt_score"] == ""
    assert "0.2784" in by_id["gemsdoe92-lbmc1-35801dots-20261027-89a660f6"]["notes"]

    # Check key HTML/MD docs have zero conflict markers and link the 2026-10-29 summary
    for rel in (
        "docs/index.html",
        "docs/nine-sites.html",
        "docs/how-to-submit.html",
        "docs/executive-summary.html",
        "docs/executive-summary-20261029-marussi-trishear.html",
        "index.html",
        "README.md",
        "SUBMISSION_READY.md",
        "SLOT_PLAN.md",
        "IRREGULARITIES.md",
        "docs/STANDING_PROMPT.md",
        "docs/HYPOTHESES_20261029_MARUSSI_TRISHEAR.md",
        "docs/WHY_0_2778.md",
    ):
        txt = (ROOT / rel).read_text(encoding="utf-8")
        assert "<<<<<<<" not in txt and ">>>>>>>" not in txt, f"conflict marker in {rel}"
