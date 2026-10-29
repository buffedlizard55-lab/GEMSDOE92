"""Regression & physics tests for the 2026-10-29 DEXP-KOSTROV-KOENDERINK lane & 2,262-SHA audit."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine

from gems.dexp_kostrov import (
    CX_FEATURE_NAMES,
    DK_FEATURE_NAMES,
    clean_band_2d,
    directional_crest_1d,
    fedi_dexp_step_features,
    koenderink_shape_and_curvedness,
    kostrov_simpson_strain_regime,
)

ROOT = Path(__file__).resolve().parents[1]
CAND_STEM = "gemsdoe92-dexpkostrov1-40000dots-20261029-ffa21c17"
CAND_SHA256 = "80d66b0590b26ddc9ac56af3964289f63f9c07c80931e3e69a7089dbabbc6faf"


def test_fedi_dexp_step_features_prefers_crustal_step_over_shallow_dipole():
    """Fedi (2007): deep fault step (N~0) decays slower with altitude than shallow dipole."""
    h, w = 128, 128
    valid = np.ones((h, w), dtype=bool)
    x = (np.arange(w, dtype=np.float32) - 64.0) * 100.0  # meters
    step = np.broadcast_to(np.arctan2(x, 300.0), (h, w)).copy().astype(np.float32)
    shallow = np.broadcast_to(x / ((x * x + 50.0 * 50.0) ** 1.5), (h, w)).copy().astype(np.float32)
    # Inject a finite -3.4028235e38 sentinel to prove clean_band_2d strips IR-92-FINITE-NODATA-SENTINEL
    step[10, 10] = np.float32(-3.4028235e38)
    cleaned = clean_band_2d(step, valid)
    assert np.isfinite(cleaned).all() and float(np.abs(cleaned).max()) < 10.0

    s_step, d_step, gx_s, gy_s, gm_s = fedi_dexp_step_features(step, valid)
    s_shal, d_shal, _, _, _ = fedi_dexp_step_features(shallow, valid)

    for arr in (s_step, d_step, gx_s, gy_s, gm_s, s_shal, d_shal):
        assert arr.shape == (h, w) and arr.dtype == np.float32 and np.isfinite(arr).all()
    assert float(s_step.min()) >= 0.0 and float(s_step.max()) <= 1.0
    assert float(d_step[64, 64]) < float(d_shal[64, 64])
    assert float(s_step[64, 64]) > float(s_step[64, 8])
    crest = directional_crest_1d(s_step, valid)
    assert crest.shape == (h, w) and float(crest[64, 64]) > float(crest[64, 20])


def test_kostrov_simpson_strain_regime_and_koenderink_shape_invariance():
    """Kostrov-Simpson S_style separates normal, strike-slip, reverse; Koenderink is scale-invariant."""
    h, w = 96, 96
    valid = np.ones((h, w), dtype=bool)
    shear = np.full((h, w), 10.0, dtype=np.float32)
    dil_ext = np.full((h, w), 15.0, dtype=np.float32)
    dil_ss = np.zeros((h, w), dtype=np.float32)
    dil_rev = np.full((h, w), -15.0, dtype=np.float32)
    inv2 = np.full((h, w), 20.0, dtype=np.float32)

    s_ext, w_ext, _ = kostrov_simpson_strain_regime(dil_ext, shear, inv2, valid)
    s_ss, _, w_wr = kostrov_simpson_strain_regime(dil_ss, shear, inv2, valid)
    s_rev, _, _ = kostrov_simpson_strain_regime(dil_rev, shear, inv2, valid)

    assert np.isfinite(s_ext).all() and np.isfinite(w_ext).all() and np.isfinite(w_wr).all()
    assert float(s_ext[48, 48]) > 0.40
    assert abs(float(s_ss[48, 48])) < 1e-5
    assert float(s_rev[48, 48]) < -0.40

    # Parabolic valley/piedmont toe z = (x - 48)^2: concave-upward => SI > 0, invariant to 100x scaling
    x = np.arange(w, dtype=np.float32)[None, :] - 48.0
    valley = np.broadcast_to(x * x, (h, w)).copy().astype(np.float32)
    ridge = -valley
    si1, c1 = koenderink_shape_and_curvedness(valley, valid, sigma=3.0)
    si100, c100 = koenderink_shape_and_curvedness(valley * np.float32(100.0), valid, sigma=3.0)
    sir, _ = koenderink_shape_and_curvedness(ridge, valid, sigma=3.0)

    assert np.allclose(si1, si100, atol=1e-4)
    assert np.allclose(c1 * 100.0, c100, rtol=1e-3, atol=1e-4)
    assert float(si1[48, 48]) > 0.30
    assert float(sir[48, 48]) < -0.30
    assert len(DK_FEATURE_NAMES) == 12 and len(CX_FEATURE_NAMES) == 8


def test_20261029_candidate_geotiff_zip_gates_and_validator_cli():
    """Verify binary [0,1] encoding, 0 NaN, exact EPSG:32611 grid, ZIP, and fail-closed validator CLI."""
    tif = ROOT / "docs" / "downloads" / f"{CAND_STEM}-zeros.tif"
    zpath = ROOT / "docs" / "downloads" / f"{CAND_STEM}-zeros.zip"
    audit_p = ROOT / "docs" / "downloads" / f"{CAND_STEM}-zeros-audit.json"
    card_p = ROOT / "docs" / "downloads" / f"{CAND_STEM}_run_card.json"
    ready_p = ROOT / "docs" / "downloads" / "dexpkostrov_readiness_20261029.json"

    for p in (tif, zpath, audit_p, card_p, ready_p):
        assert p.is_file(), f"missing {p}"

    tif_bytes = tif.read_bytes()
    assert hashlib.sha256(tif_bytes).hexdigest() == CAND_SHA256

    with rasterio.open(tif) as ds:
        assert ds.count == 1
        assert ds.dtypes == ("float32",)
        assert str(ds.crs) == "EPSG:32611"
        assert (ds.height, ds.width) == (3730, 3292)
        assert ds.transform == Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
        assert ds.nodata is None
        arr = ds.read(1, masked=False)
        assert int((ds.dataset_mask() == 255).sum()) == 3730 * 3292

    assert np.isfinite(arr).all()
    assert np.array_equal(np.unique(arr), np.array([0.0, 1.0], dtype=np.float32))
    assert int((arr == 1.0).sum()) == 40_000

    with zipfile.ZipFile(zpath, "r") as zf:
        assert zf.namelist() == [f"{CAND_STEM}-zeros.tif"]
        assert hashlib.sha256(zf.read(f"{CAND_STEM}-zeros.tif")).hexdigest() == CAND_SHA256

    proc = subprocess.run(
        [sys.executable, str(ROOT / "validate_submission.py"), str(tif)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert proc.returncode == 1
    assert "RESULT: PASS (11 gates)" in proc.stdout
    assert "FORMAT PASS (local only)" in proc.stdout
    assert "DO NOT SUBMIT" in proc.stdout
    assert "OK TO SUBMIT" not in proc.stdout


def test_20261029_evidence_holdout_uniqueness_oot_and_conflict_free_site():
    """Verify canaries, holdout win over R0, 2,262-SHA PI-1 uniqueness, OOT Spearman=1.0, and conflict-free HTML."""
    card = json.loads((ROOT / "evidence" / f"{CAND_STEM}_run_card.json").read_text(encoding="utf-8"))
    assert card["raster_sha256"] == CAND_SHA256
    assert card["verdict"] == "negative" and card["submission_eligible"] is False
    assert card["weekly_slots_used"] == 0 and card["experiments_run"] == 3
    assert 0 < len(card["note"]) <= 140

    # Leakage canaries
    can = json.loads((ROOT / "evidence" / "dexp_kostrov_canaries_20261029.json").read_text(encoding="utf-8"))
    assert can["n_features_tested"] == 36
    assert can["leakage_flag"] is False and can["max_symmetric_auc"] <= 0.90

    # Fold-proper HOLDOUT-DTI strictly beats R0 recipe with paired 95% CI > 0
    h = card["holdout_dti"]
    assert h["evaluator_version"] == "gems57-pooled-hide-v2"
    assert h["withheld_positive_pixels"] == 22663
    assert h["e3_candidate"]["dti"] > h["r0_recipe_control"]["dti"]
    assert h["e2_dual_regime"]["dti"] > h["r0_recipe_control"]["dti"]
    assert h["paired_e3_vs_r0_recipe"]["delta"] > 0.015
    assert h["paired_e3_vs_r0_recipe"]["ci95"][0] > 0.0

    # Full 2,262-SHA PI-1 uniqueness (2,139 dot fields + 123 surfaces)
    u = card["uniqueness"]
    assert u["registry_unique_rasters"] == 2262
    assert u["dot_field_rasters"] + u["surface_rasters"] == 2262
    pi1 = u["pi1_operational_reading"]
    assert pi1["pre_placement_surface_pass"] is True and pi1["surface_worst_overlap"] <= 0.70
    assert pi1["surface_worst_abs_rho"] <= 0.90
    assert pi1["final_dots_pass"] is True and pi1["final_worst_overlap"] <= 0.70
    assert pi1["final_worst_abs_rho"] <= 0.90
    assert u["literal_reading"]["duplicate_under_literal"] is True

    u_ev = json.loads((ROOT / "evidence" / "dexp_kostrov_uniqueness_20261029.json").read_text(encoding="utf-8"))
    assert u_ev["sibling_comparisons"]["GEMSDOE92_lbmc1_0.2784"]["overlap_pi1"] <= 0.25

    # Prospective OOT on newly scored 2026-10-29 claims
    oot = json.loads((ROOT / "evidence" / "lbm_oot_and_v3_20261029.json").read_text(encoding="utf-8"))
    p_oot = oot["prospective_oot_20261029"]
    assert p_oot["n_new_unambiguous_claims"] == 4
    assert p_oot["non_lbmc1_3claims_v2_rmse"] < 0.025
    by_claim = [r["site"] for r in sorted(p_oot["rows"], key=lambda r: r["claim"], reverse=True)]
    by_pred = [r["site"] for r in sorted(p_oot["rows"], key=lambda r: r["lbm_v2_oot"], reverse=True)]
    assert by_claim == by_pred == ["GEMSDOE92", "GEMSDOEkarage1", "ApartGEMSDOE3", "KANLERGEMSDOE3"]

    # Ledger entry
    with (ROOT / "ledger" / "submissions.csv").open(encoding="utf-8", newline="") as f:
        by_id = {r["id"]: r for r in csv.DictReader(f)}
    assert CAND_STEM in by_id and by_id[CAND_STEM]["sha256"] == CAND_SHA256

    # Zero conflict markers & fail-closed wording across all key HTML pages
    for rel in (
        "index.html",
        "docs/index.html",
        "docs/how-to-submit.html",
        "docs/nine-sites.html",
        "docs/executive-summary.html",
        "docs/executive-summary-20261029-dexp-kostrov.html",
    ):
        txt = (ROOT / rel).read_text(encoding="utf-8")
        assert "<<<<<<< " not in txt and ">>>>>>> " not in txt
        assert "DO NOT SUBMIT" in txt and "OK TO SUBMIT" not in txt
        assert CAND_STEM in txt
