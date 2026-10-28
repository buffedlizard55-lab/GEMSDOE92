"""Tests for the 2026-10-28 RIESZ-LOCKED + LBM-v2 lane, 8-owner fleet & primary GeoTIFF."""
from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine

from gems.riesz_locked import (
    FEATURE_NAMES,
    _clean_edt_fill,
    biharmonic_flexural_dipole,
    riesz_step_congruency,
    wijns_cos_theta_harmonic,
)

ROOT = Path(__file__).resolve().parents[1]
PRIMARY_STEM = "gemsdoe92-rieszlbm2-50000dots-20261028-79041788"
PRIMARY_SHA256 = "d168c7d2a0ea89f9609426fe5f9d5aa0791223131c98a90d55b1f6aa1cbe5d7a"


def test_riesz_step_congruency_separates_odd_fault_step_from_even_ridge():
    """Felsberg & Sommer (2001): odd step peaks at contact; symmetric ridge crest -> 0."""
    h, w = 128, 128
    x = np.arange(w, dtype=np.float32)[None, :]
    step = np.broadcast_to(np.tanh((x - 64.0) / 2.0), (h, w)).astype(np.float32)
    pc_step, c2, s2 = riesz_step_congruency(step, noise_q=0.30)
    assert pc_step.shape == (h, w) and pc_step.dtype == np.float32
    assert np.isfinite(pc_step).all() and pc_step.min() >= 0.0 and pc_step.max() <= 1.0
    # Contact at x=64 has strong odd-step congruency; far background is 0
    assert float(pc_step[64, 64]) > 0.65
    assert float(pc_step[64, 10]) < 0.05
    # Step normal is purely along +x => cos(2*psi) ~ +1
    assert float(c2[64, 64]) > 0.90 and abs(float(s2[64, 64])) < 0.15

    # Symmetric Gaussian dyke/ridge crest has even phase (|even| >> |odd|) => pc == 0 at crest
    ridge = np.broadcast_to(np.exp(-((x - 64.0) ** 2) / (2.0 * 4.0 ** 2)), (h, w)).astype(np.float32)
    pc_ridge, _, _ = riesz_step_congruency(ridge, noise_q=0.30)
    assert float(pc_ridge[64, 64]) == 0.0


def test_wijns_cos_theta_harmonic_is_scale_invariant_and_bounded():
    """Wijns 2D-FFT harmonic 1VD is invariant to 1000x unit rescaling (fixes IR-1028-2)."""
    h, w = 96, 96
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    u = np.tanh((x - 48.0 + 0.2 * (y - 48.0)) / 3.0).astype(np.float32)
    w1 = wijns_cos_theta_harmonic(u)
    w1000 = wijns_cos_theta_harmonic(u * np.float32(1000.0))
    assert w1.dtype == np.float32 and np.isfinite(w1).all()
    assert float(w1.min()) >= 0.0 and float(w1.max()) <= 1.0
    assert np.allclose(w1, w1000, atol=1e-4)
    assert float(w1[48, 48]) > float(w1[48, 8])

    bf = biharmonic_flexural_dipole(u)
    assert bf.shape == (h, w) and bf.dtype == np.float32 and np.isfinite(bf).all()


def test_clean_edt_fill_strips_float32_nodata_sentinels_and_nans():
    arr = np.ones((16, 16), dtype=np.float32) * 42.0
    arr[0, 0] = np.nan
    arr[5, 7] = np.float32(-3.4028235e38)
    filled, ok = _clean_edt_fill(arr)
    assert not ok[0, 0] and not ok[5, 7] and int(ok.sum()) == 254
    assert np.allclose(filled, 42.0)
    assert len(FEATURE_NAMES) == 16


def test_primary_20261028_geotiff_and_zip_portal_compliance():
    """Verify binary [0,1] values, 0 NaN, exact EPSG:32611 grid, and single-TIFF ZIP."""
    tif = ROOT / "docs" / "downloads" / f"{PRIMARY_STEM}-zeros.tif"
    zpath = ROOT / "docs" / "downloads" / f"{PRIMARY_STEM}-zeros.zip"
    assert tif.is_file() and zpath.is_file()

    tif_bytes = tif.read_bytes()
    assert hashlib.sha256(tif_bytes).hexdigest() == PRIMARY_SHA256

    with rasterio.open(tif) as ds:
        assert ds.count == 1
        assert ds.dtypes == ("float32",)
        assert str(ds.crs) == "EPSG:32611"
        assert (ds.height, ds.width) == (3730, 3292)
        assert ds.transform == Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
        assert ds.nodata is None
        arr = ds.read(1, masked=False)
        msk = ds.dataset_mask()
        assert int((msk == 255).sum()) == 3730 * 3292

    assert np.isfinite(arr).all()
    assert float(arr.min()) == 0.0 and float(arr.max()) == 1.0
    uniq = np.unique(arr)
    assert np.array_equal(uniq, np.array([0.0, 1.0], dtype=np.float32))
    assert int((arr == 1.0).sum()) == 50000

    sample_tif = ROOT / ".cache" / "gems_inputs" / "bridge" / "sample_submission.tif"
    faults_tif = ROOT / ".cache" / "gems_inputs" / "bridge" / "existing_faults.tif"
    if sample_tif.is_file() and faults_tif.is_file():
        from scipy import ndimage as ndi
        with rasterio.open(sample_tif) as sds:
            assert (sds.height, sds.width) == (3730, 3292)
            assert sds.crs == ds.crs and sds.transform == ds.transform
            fp = np.isfinite(sds.read(1, masked=False))
        with rasterio.open(faults_tif) as fds:
            cat = fds.read(1, masked=False) > 0
        pos = arr > 0.5
        assert int((pos & ~fp).sum()) == 0
        assert int((pos & cat).sum()) == 0
        d_cat = ndi.distance_transform_edt(~cat)
        assert float(d_cat[pos].min()) > 2.0

    with zipfile.ZipFile(zpath, "r") as zf:
        names = zf.namelist()
        assert names == [f"{PRIMARY_STEM}-zeros.tif"]
        zbytes = zf.read(names[0])
        assert hashlib.sha256(zbytes).hexdigest() == PRIMARY_SHA256


def test_20261028_evidence_fleet_oot_canaries_and_docs_synchronized():
    card = json.loads((ROOT / "evidence" / f"{PRIMARY_STEM}_run_card.json").read_text(encoding="utf-8"))
    assert card["raster_sha256"] == PRIMARY_SHA256
    # Corrected after the source run card's mandatory Rule-1/Rule-2 failures were audited.
    assert card["verdict"] == "negative" and card["submission_eligible"] is False
    assert card["gates_passed"]["catalogue_holdout_beats_r0_recipe"] is False
    assert card["gates_passed"]["uniqueness_pi1"] is False
    assert card["uniqueness"]["literal_reading"]["duplicate_under_literal"] is True
    assert card["promotion_review"]["decision"] == "negative"
    assert 0 < len(card["note"]) <= 140
    assert card["uniqueness"]["registry_owners"] == 8
    assert card["uniqueness"]["registry_rasters"] == 2162
    assert card["uniqueness"]["final_worst_overlap"] <= 0.70
    assert card["uniqueness"]["vs_prior_gemsdoe92_lbmc1_overlap"] <= 0.70
    assert card["uniqueness"]["surface_worst_abs_rho"] <= 0.90
    assert card["uniqueness"]["final_worst_abs_rho"] <= 0.90
    assert card["uniqueness"]["literal_reading"]["worst"] == 1.0
    assert card["uniqueness"]["literal_reading"]["duplicate_under_literal"] is True

    can = json.loads((ROOT / "evidence" / "riesz_locked_canaries.json").read_text(encoding="utf-8"))
    assert can["leakage_flag"] is False and can["max_sym_auc"] <= 0.90

    oot = json.loads((ROOT / "evidence" / "lbm_v1_prospective_oot_20261028.json").read_text(encoding="utf-8"))
    assert oot["n_new_claims"] == 5 and oot["prospective_rmse"] < 0.015

    fleet = json.loads((ROOT / "evidence" / "fleet_8owners_20261028.json").read_text(encoding="utf-8"))
    assert len(fleet["owners"]) == 8 and fleet["unique_sha256"] == 2162
    assert len(fleet["unscored_prompt_entries"]) == 7

    with (ROOT / "ledger" / "submissions.csv").open(encoding="utf-8", newline="") as f:
        by_id = {r["id"]: r for r in csv.DictReader(f)}
    assert PRIMARY_STEM in by_id and by_id[PRIMARY_STEM]["sha256"] == PRIMARY_SHA256
    assert "gemsdoe92-lbmc1-35801dots-20261027-89a660f6" in by_id

    for doc_rel in ("README.md", "SESSION_PROMPT.md", "SLOT_PLAN.md", "IRREGULARITIES.md",
                    "docs/index.html", "docs/how-to-submit.html", "docs/nine-sites.html", "index.html"):
        txt = (ROOT / doc_rel).read_text(encoding="utf-8")
        assert PRIMARY_STEM in txt or PRIMARY_SHA256[:16] in txt, f"missing primary in {doc_rel}"
