"""Unit, artifact, and protocol-policy tests for SCARPDIPOLE (2026-10-24)."""
from __future__ import annotations

import csv
import hashlib
import json
import warnings
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy.special import erf

from gems.scarpdipole import (
    grad32,
    piedmont_range_envelope,
    scarp_profile_dipole,
    scarpdipole_surface,
)

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_grad32_is_float32_and_second_order_exact_on_linear():
    y, x = np.mgrid[0:32, 0:40].astype(np.float32)
    f = 2.5 * y - 1.25 * x + 7.0
    gy, gx = grad32(f)
    assert gy.dtype == np.float32 and gx.dtype == np.float32
    assert np.allclose(gy, 2.5, atol=1e-5)
    assert np.allclose(gx, -1.25, atol=1e-5)


def test_scarp_profile_dipole_peaks_on_erf_fault_trace_midpoint():
    """Hanks-Bucknam-Wallace synthetic check: z(x) = -erf((x - x0)/w) peaks at x = x0."""
    rng = np.random.default_rng(7)
    h, w = 80, 96
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    x0 = 48.0
    # Upslope (west, x < x0) higher; downslope (east, x > x0) lower + gentle background slope & micro-roughness
    z = (-25.0 * erf((x - x0) / 3.0) - 0.15 * x + 0.05 * y + rng.normal(0.0, 0.08, (h, w))).astype(np.float32)
    valid = np.ones((h, w), dtype=bool)
    dip = scarp_profile_dipole(z, valid, sigmas=(1.0, 2.0))
    assert dip.dtype == np.float32
    assert np.isfinite(dip).all()
    assert 0.0 <= float(dip.min()) and float(dip.max()) <= 1.0

    # Row-averaged profile must peak within <= 1 px of the analytical fault trace x0 = 48
    mean_col_profile = dip[20:60, 12:-12].mean(axis=0)
    peak_x = 12 + int(np.argmax(mean_col_profile))
    assert abs(peak_x - int(x0)) <= 1
    assert float(dip[20:60, int(x0)].mean()) > 0.90
    assert float(dip[20:60, 15].mean()) < 0.65


def test_scarpdipole_surface_handles_nan_sentinels_and_piedmont_envelope():
    rng = np.random.default_rng(42)
    y, x = np.mgrid[0:64, 0:64].astype(np.float32)
    det_elev = (-15.0 * erf((x - 32.0) / 2.5) + 0.2 * y + rng.normal(0, 0.05, (64, 64))).astype(np.float32)
    gy, gx = grad32(det_elev)
    det_slope = np.hypot(gy, gx).astype(np.float32)
    valid = np.ones((64, 64), dtype=bool)
    valid[:4, :] = False
    det_elev[:2, :] = np.nan
    det_elev[2:4, :] = -3.4e38

    env, (lo, hi) = piedmont_range_envelope(det_elev, valid)
    assert lo < hi
    assert np.all(env[~valid] == 0.0)
    assert bool(np.all(np.isclose(env[valid], 0.45, atol=1e-6) | np.isclose(env[valid], 1.0, atol=1e-6)))

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        out = scarpdipole_surface(det_elev, det_slope, valid)
    s_pct = out["S_pct"]
    assert isinstance(s_pct, np.ndarray) and s_pct.dtype == np.float32
    assert np.isfinite(s_pct).all()
    assert np.all(s_pct[~valid] == 0.0)
    assert 0.0 <= float(s_pct.min()) and float(s_pct.max()) <= 1.0


def test_scarpdipole_built_variants_and_zip_integrity():
    vdoc = json.loads((ROOT / "evidence" / "scarpdipole_variants.json").read_text(encoding="utf-8"))
    assert vdoc["axis"] == "SCARPDIPOLE"
    assert len(vdoc["variants"]) == 3  # Protocol Rule 6: <= 3 experiments

    expected_doses = [("f42dipole", 15815, 21839), ("f45dipole", 16944, 20710), ("f50dipole", 18827, 18827)]
    for v, (val_name, n_far, n_on) in zip(vdoc["variants"], expected_doses):
        assert v["value"] == val_name
        assert v["n_dots"] == 37654
        assert v["n_far_off_h19"] == n_far
        assert v["n_on_h19"] == n_on
        assert len(v["form_note"]) <= 140
        assert all(g["ok"] for g in v["gates_zeros"])

        tif_path = ROOT / v["file_zeros"]
        assert tif_path.is_file()
        assert _sha256(tif_path) == v["sha256_zeros"]
        with rasterio.open(tif_path) as ds:
            arr = ds.read(1)
            assert ds.count == 1 and ds.dtypes[0] == "float32"
            assert ds.shape == (3730, 3292)
            assert str(ds.crs) == "EPSG:32611"
            assert np.isfinite(arr).all()
            assert float(arr.min()) == 0.0 and float(arr.max()) == 1.0
            assert int((arr > 0).sum()) == 37654

    # Verify primary single-TIFF ZIP archive
    prim_tif = ROOT / vdoc["variants"][0]["file_zeros"]
    prim_zip = prim_tif.with_suffix(".zip")
    assert prim_zip.is_file()
    with zipfile.ZipFile(prim_zip, "r") as zf:
        names = zf.namelist()
        assert names == [prim_tif.name]
        assert hashlib.sha256(zf.read(names[0])).hexdigest() == vdoc["variants"][0]["sha256_zeros"]


def test_scarpdipole_run_card_and_audit_protocol_compliance():
    rc = json.loads((ROOT / "evidence" / "scarpdipole_run_card.json").read_text(encoding="utf-8"))
    rc_canon = json.loads((ROOT / "evidence" / "run_card.json").read_text(encoding="utf-8"))
    assert rc == rc_canon

    # Protocol Rule 5 required Run Card fields
    for key in (
        "hypothesis", "mechanism", "named_non_fault_mimic", "holdout_dti",
        "leakage_canary", "registry_uniqueness", "raster_sha256",
        "validator_output", "submission_name", "submission_note", "verdict",
    ):
        assert key in rc and rc[key] not in (None, "")

    assert len(rc["submission_note"]) <= 140
    assert rc["validator_output"]["passed"] is True
    assert rc["validator_output"]["no_nan_in_footprint"] is True
    assert rc["validator_output"]["values_in_0_1"] is True
    assert rc["validator_output"]["crs_shape_transform_match_template"] is True
    assert rc["leakage_canary"]["passed"] is True
    assert rc["leakage_canary"]["scarpdipole_S_pct_symmetric_auc"] <= 0.90

    # Verify holdout superiority in both regimes + SGMC lift
    ff = rc["holdout_dti"]["fold_fair_d_visible_gt_2px"]
    st = rc["holdout_dti"]["static_final_raster_d_full_cat_gt_2px"]
    assert ff["pooled_dti"] > ff["visible_collar_dti"] > ff["parent_B2_visible_dti"]
    assert ff["paired_delta_vs_parent_B2_visible"]["ci95"][0] > 0.0
    assert ff["paired_delta_vs_visible_collar"]["ci95"][0] > 0.0
    assert st["pooled_dti"] > st["RELIEFp10_dti"] > st["BREAKLINEf45Ltop_dti"] > st["R0_dti"]
    assert st["paired_delta_vs_R0"]["ci95"][0] > 0.0
    assert st["paired_delta_vs_BREAKLINEf45Ltop"]["ci95"][0] > 0.0
    assert rc["off_catalogue_sgmc_proxy"]["dti"] > 0.096060

    # Verify sparse uniqueness + un-waived literal negative verdict
    pub = rc["registry_uniqueness"]["public_registry_1300_rasters"]
    assert pub["compatible_rasters_compared"] >= 1290
    assert pub["final_worst_abs_spearman"] <= 0.90
    assert pub["nonbinding_sparse_dotted_le_60k_submissions"]["count"] >= 1000
    assert pub["nonbinding_sparse_dotted_le_60k_submissions"]["rasters_over_70pct_overlap"] == 0
    assert pub["saturation_certificate"]["universal_overlap_blocker"] is True
    assert rc["submission_eligible"] is False
    assert rc["verdict"] == "negative"


def test_ledger_and_all_json_files_are_valid():
    for folder in ("evidence", "docs/downloads", "registry", "ledger"):
        for jp in sorted((ROOT / folder).rglob("*.json")):
            doc = json.loads(jp.read_text(encoding="utf-8"))
            assert isinstance(doc, (dict, list)), f"Unexpected JSON root in {jp}"

    with (ROOT / "ledger" / "submissions.csv").open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    scarp_rows = [r for r in rows if r["axis"] == "SCARPDIPOLE"]
    assert len(scarp_rows) == 3
    cards = json.loads((ROOT / "ledger" / "mechanism_cards.json").read_text(encoding="utf-8"))
    for r in scarp_rows:
        assert r["id"] in cards
        assert r["receipt_score"] == ""
