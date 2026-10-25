"""Unit and regression tests for the LISTRICLOQO lane, updip listric projection,
interfluve knickpoint bridging, selective branch quadrant calibration, and complete
102-repo (1,459-raster) uniqueness audit (2026-10-25).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import rasterio

from gems.listric_loqo import (
    DEBIASED_INDICES,
    FEATURE_NAMES,
    LISTRIC_EXTRA_NAMES,
    SUB_KNICK_INDICES,
    bilinear_sample_2d,
    build_listric_crest_surface,
)

ROOT = Path(__file__).resolve().parents[1]


def test_listric_loqo_feature_schema_has_no_catalogue_distance():
    assert len(LISTRIC_EXTRA_NAMES) == 6
    assert len(FEATURE_NAMES) == 36
    assert len(set(FEATURE_NAMES)) == 36
    for name in FEATURE_NAMES:
        assert "dist_known" not in name.lower()
        assert "catalogue" not in name.lower()
    assert len(DEBIASED_INDICES) == 30
    assert len(SUB_KNICK_INDICES) == 33
    deb_names = {FEATURE_NAMES[i] for i in DEBIASED_INDICES}
    assert "f31_listric_updip_sub_ramp" in deb_names
    assert "f34_rad_uth_kth_strike_concord" in deb_names
    assert "geod_2ndinv_raw" not in deb_names
    sub_names = {FEATURE_NAMES[i] for i in SUB_KNICK_INDICES}
    assert "f31_listric_updip_sub_ramp" in sub_names
    assert "f33_carb_bouguer_base_updip" in sub_names
    assert "f35_relay_ramp_strike_transfer" in sub_names
    assert "rel_log_slope_break" not in sub_names


def test_bilinear_sample_2d_exact_shift_and_bounds():
    h, w = 20, 24
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    field = (2.0 * xx + 0.5 * yy).astype(np.float32)
    sample_y = (yy + 1.5).astype(np.float32)
    sample_x = (xx - 2.25).astype(np.float32)
    valid = np.ones((h, w), dtype=bool)
    sampled = bilinear_sample_2d(field, sample_y, sample_x, valid)
    assert sampled.shape == (h, w)
    assert sampled.dtype == np.float32
    assert np.isfinite(sampled).all()
    # Inside interior away from boundary clamping, linear function shifts exact:
    expected = 2.0 * (xx[4:-4, 4:-4] - 2.25) + 0.5 * (yy[4:-4, 4:-4] + 1.5)
    np.testing.assert_allclose(sampled[4:-4, 4:-4], expected, atol=1e-5)


def test_build_listric_crest_surface_finite_and_bounded():
    rng = np.random.default_rng(20261025)
    h, w = 28, 28
    valid = np.ones((h, w), dtype=bool)
    p = rng.uniform(0.0, 1.0, size=(h, w)).astype(np.float32)
    l_topo = rng.uniform(0.0, 1.0, size=(h, w)).astype(np.float32)
    l_knick_bridge = rng.uniform(0.0, 1.0, size=(h, w)).astype(np.float32)
    l_listric = rng.uniform(0.0, 1.0, size=(h, w)).astype(np.float32)
    l_rad = rng.uniform(0.0, 1.0, size=(h, w)).astype(np.float32)
    out = build_listric_crest_surface(
        p, l_topo, l_knick_bridge, l_listric, l_rad, valid
    )
    assert out["S_crest"].shape == (h, w)
    assert out["ridge_1d"].shape == (h, w)
    assert np.isfinite(out["S_crest"]).all()
    assert float(out["S_crest"].min()) >= 0.0
    assert float(out["S_crest"].max()) <= 3.0
    assert out["ridge_1d"].any()


def test_listric_loqo_leakage_canaries_and_holdout_records():
    hdoc = json.loads((ROOT / "evidence/listric_loqo_holdout.json").read_text(encoding="utf-8"))
    can = hdoc["leakage_canaries"]
    assert can["n_tested"] == 42
    assert len(can["rows"]) == 42
    assert can["all_pass"] is True
    assert can["max_symmetric_auc"] <= 0.90

    scores = hdoc["static_dcat2"]["scores"]
    assert scores["selectcal"]["withheld_positive_pixels"] == 22663
    # New all-time #1, #2, #3 static d_cat > 2.0 HOLDOUT-DTI records
    assert scores["selectcal"]["dti"] == pytest.approx(0.013295, abs=2e-6)
    assert scores["standalone"]["dti"] == pytest.approx(0.013250, abs=2e-6)
    assert scores["uncal"]["dti"] == pytest.approx(0.013105, abs=2e-6)
    assert scores["selectcal"]["dti"] > scores["KNICKLOQO_standalone"]["dti"]
    assert scores["standalone"]["dti"] > scores["KNICKLOQO_standalone"]["dti"]
    assert scores["uncal"]["dti"] > scores["KNICKLOQO_standalone"]["dti"]
    assert scores["selectcal"]["dti"] > scores["PROVINCETOE_piedbasin"]["dti"]
    assert scores["selectcal"]["dti"] > scores["COULOMBLOQO_standalone"]["dti"]
    assert scores["selectcal"]["dti"] > 3.0 * scores["R0"]["dti"]

    # Strict draw-blind Rule-2 d_visible > 2.0 record
    dvis_scores = hdoc["rule2_dvis2"]["scores"]
    assert dvis_scores["standalone_dvis2"]["dti"] == pytest.approx(0.114410, abs=2e-6)
    assert dvis_scores["selectcal_dvis2"]["dti"] == pytest.approx(0.113938, abs=2e-6)
    assert dvis_scores["standalone_dvis2"]["dti"] > 0.113316  # beats COULOMBLOQO_standalone
    assert dvis_scores["selectcal_dvis2"]["dti"] > 0.113316  # beats COULOMBLOQO_standalone
    assert dvis_scores["standalone_dvis2"]["dti"] > dvis_scores["H19_skeleton_dvis2"]["dti"]


def test_listric_loqo_tifs_uniqueness_and_run_card_contract():
    rc = json.loads((ROOT / "evidence/listric_loqo_run_card.json").read_text(encoding="utf-8"))
    rc_dl = json.loads((ROOT / "docs/downloads/listric_loqo_run_card.json").read_text(encoding="utf-8"))
    udoc = json.loads((ROOT / "evidence/listric_loqo_uniqueness.json").read_text(encoding="utf-8"))
    ddoc = json.loads((ROOT / "evidence/listric_loqo_dual_reading_audit.json").read_text(encoding="utf-8"))

    assert rc == rc_dl
    assert udoc == ddoc
    assert rc["lane"] == "LISTRICLOQO"
    assert rc["best_variant"] == "selectcal"
    assert rc["weekly_slots_used"] == 0
    assert rc["experiments_used"] == 3
    assert rc["verdict"] == "negative"
    assert rc["submission_eligible"] is False
    assert len(rc["submission_name"]) <= 140
    assert len(rc["note"]) <= 140

    # Verify all 3 emitted GeoTIFFs and their sidecar audit receipts
    for arm in ("standalone", "selectcal", "uncal"):
        sib = rc["siblings"][arm]
        tif_path = ROOT / sib["file"]
        zip_path = ROOT / sib["zip"]
        assert tif_path.is_file()
        assert zip_path.is_file()
        assert hashlib.sha256(tif_path.read_bytes()).hexdigest() == sib["sha256_zeros"]
        assert hashlib.sha256(zip_path.read_bytes()).hexdigest() == sib["zip_sha256"]
        assert len(sib["submission_name"]) <= 140
        assert len(sib["note"]) <= 140

        with rasterio.open(tif_path) as ds:
            assert ds.count == 1
            assert ds.shape == (3730, 3292)
            assert str(ds.crs) == "EPSG:32611"
            arr = ds.read(1)
            assert arr.dtype == np.float32
            assert np.isfinite(arr).all()
            assert float(arr.min()) == 0.0
            assert float(arr.max()) == 1.0
            assert int((arr > 0.5).sum()) == 37654

        stem = tif_path.name[: -len("-zeros.tif")]
        sidecar = tif_path.parent / f"{stem}-audit.json"
        assert sidecar.is_file()
        sdoc = json.loads(sidecar.read_text(encoding="utf-8"))
        assert sdoc["overall_pass"] is True
        assert sdoc["gates_zeros_pass"] is True
        assert sdoc["submission_eligible"] is False
        assert sdoc["sha256_zeros"] == sib["sha256_zeros"]

        # Local + 102-repo (1,459-raster) uniqueness gates
        lu = udoc["local_registry"][arm]
        pu = udoc["candidates"][arm]
        assert lu["local_duplicate"] is False
        assert lu["worst_matched_budget_forward_overlap"] <= 0.70
        assert lu["worst_abs_spearman"] <= 0.90
        assert pu["operative_over_70pct_count"] == 0
        assert pu["worst_operative_overlap_3px"] <= 0.70
        assert pu["preplacement_surface_worst_abs_spearman"] <= 0.90
        assert pu["final_dots_worst_abs_spearman"] <= 0.90
        assert pu["dual_reading_verdict"] == "unique"
