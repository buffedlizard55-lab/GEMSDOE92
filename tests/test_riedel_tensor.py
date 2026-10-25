from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rasterio

from gems.rasters import sha256_file
from gems.riedel_tensor import FEATURE_NAMES_36

ROOT = Path(__file__).resolve().parents[1]


def test_riedel_tensor_feature_names_contract():
    assert len(FEATURE_NAMES_36) == 36
    assert len(set(FEATURE_NAMES_36)) == 36
    expected_new = {
        "f31_tensor_tilt_gz",
        "f32_tensor_ghz_hess",
        "f33_tensor_dipole_concord",
        "f34_riedel_obliquity_r",
        "f35_rad_pot_concord",
        "f36_wallace_basal_toe",
    }
    assert expected_new.issubset(set(FEATURE_NAMES_36))


def test_riedel_tensor_screen_and_leakage_canaries():
    sdoc = json.loads((ROOT / "evidence/riedel_tensor_screen.json").read_text(encoding="utf-8"))
    lc = sdoc["leakage_canaries"]
    assert lc["all_pass"] is True
    assert len(lc["features"]) >= 50
    assert lc["max_symmetric_auc"] <= 0.90

    pre = sdoc["preplacement_surface_uniqueness"]
    assert pre["duplicate"] is False
    assert pre["worst_abs_spearman_exact_full_footprint"] <= 0.90
    assert pre["worst_top37654_forward_3px_overlap"] <= 0.70


def test_riedel_tensor_variants_and_geotiff_gates():
    vdoc = json.loads((ROOT / "evidence/riedel_tensor_variants.json").read_text(encoding="utf-8"))
    variants = vdoc["variants"]
    assert len(variants) == 3
    arms = [v["value"] for v in variants]
    assert arms == ["standalone", "uncal", "hybrid35"]

    with rasterio.open(ROOT / "data/bridge/sample_submission.tif") as ref_ds:
        ref_shape = ref_ds.shape
        ref_crs = str(ref_ds.crs)
        ref_transform = tuple(ref_ds.transform)
        foot = np.isfinite(ref_ds.read(1))
    with rasterio.open(ROOT / "data/bridge/existing_faults.tif") as cat_ds:
        cat = (cat_ds.read(1) > 0) & foot

    for v in variants:
        zpath = ROOT / v["file_zeros"]
        assert zpath.is_file(), f"Missing {zpath}"
        assert sha256_file(zpath) == v["sha256_zeros"]
        assert all(g["ok"] for g in v["gates_zeros"])
        assert all(g["ok"] for g in v["gates_nan"])
        assert len(v["form_note"]) <= 140

        with rasterio.open(zpath) as ds:
            assert ds.shape == ref_shape == (3730, 3292)
            assert str(ds.crs) == ref_crs == "EPSG:32611"
            assert tuple(ds.transform) == ref_transform
            assert ds.dtypes[0] == "float32"
            arr = ds.read(1)

        assert int(np.isnan(arr).sum()) == 0
        assert float(arr.min()) >= 0.0
        assert float(arr.max()) <= 1.0
        assert float(np.abs(arr[~foot]).max()) == 0.0
        assert float(np.abs(arr[cat]).max()) == 0.0
        assert int((arr > 0).sum()) == 37654


def test_riedel_tensor_run_card_and_proxy_audit():
    pdoc = json.loads((ROOT / "evidence/riedel_tensor_proxy_audit.json").read_text(encoding="utf-8"))
    rc = json.loads((ROOT / "evidence/riedel_tensor_run_card.json").read_text(encoding="utf-8"))
    dl_rc = json.loads((ROOT / "docs/downloads/riedel_tensor_run_card.json").read_text(encoding="utf-8"))
    assert rc == dl_rc

    assert pdoc["winning_arm"] == "standalone"
    assert rc["holdout_dti"]["dti"] > 0.010788  # beats KNICKLOQO standalone
    assert rc["holdout_dti"]["strict_draw_blind_dcat2_dti"] > 0.010958
    assert rc["holdout_dti"]["strict_draw_blind_dvis2_dti"] > 0.109043
    assert rc["sgmc_proxy"]["dti"] > 0.103912
    assert rc["leakage_canary_max_symmetric_auc"] <= 0.90

    for arm in ("standalone", "uncal", "hybrid35"):
        ab = rc["ablation_summary"][arm]
        assert ab["worst_local_forward_overlap_3px"] <= 0.70
        assert ab["worst_local_abs_spearman_phi"] <= 0.90
        assert ab["local_duplicate"] is False
        assert ab["public_dual_reading_worst_overlap_3px"] <= 0.70
        assert ab["public_dual_reading_verdict"] == "unique"

    assert rc["verdict"] == "negative"
    assert rc["submission_eligible"] is False
    assert rc["weekly_slots_used"] == 0
    assert rc["experiments_used"] == 3
    assert len(rc["note"]) <= 140
