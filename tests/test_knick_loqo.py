"""Unit and integration tests for the KNICKLOQO lane, Action #1 dual-reading audit,
and #IR-92-NE-QUADRANT-LOQO-COLLAPSE resolution (2026-10-25).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from gems.knick_loqo import (
    DEBIASED_INDICES,
    FEATURE_NAMES,
    SUB_KNICK_INDICES,
    build_knick_crest_surface,
)

ROOT = Path(__file__).resolve().parents[1]


def test_knick_loqo_feature_schema_has_no_catalogue_distance():
    assert len(FEATURE_NAMES) == 30
    assert len(set(FEATURE_NAMES)) == 30
    for name in FEATURE_NAMES:
        assert "dist_known" not in name.lower()
        assert "catalogue" not in name.lower()
    assert len(DEBIASED_INDICES) == 24
    assert len(SUB_KNICK_INDICES) == 27
    debiased_names = {FEATURE_NAMES[i] for i in DEBIASED_INDICES}
    assert "coulomb_mesoscale_z" in debiased_names
    assert "geod_2ndinv_raw" not in debiased_names
    sub_names = {FEATURE_NAMES[i] for i in SUB_KNICK_INDICES}
    assert "thalweg_knickzone_idx" in sub_names
    assert "poisson_mag_grav_collinearity" in sub_names
    assert "cross_contour_transgression" in sub_names
    assert "rel_log_slope_break" not in sub_names


def test_build_knick_crest_surface_finite_and_bounded():
    rng = np.random.default_rng(42)
    h, w = 24, 24
    valid = np.ones((h, w), dtype=bool)
    p = rng.uniform(0.0, 1.0, size=(h, w)).astype(np.float32)
    l_topo = rng.uniform(0.0, 1.0, size=(h, w)).astype(np.float32)
    l_knick = rng.uniform(0.0, 1.0, size=(h, w)).astype(np.float32)
    l_sub = rng.uniform(0.0, 1.0, size=(h, w)).astype(np.float32)
    out = build_knick_crest_surface(p, l_topo, l_sub, valid, l_knick=l_knick)
    assert out["S_crest"].shape == (h, w)
    assert out["ridge_1d"].shape == (h, w)
    assert np.isfinite(out["S_crest"]).all()
    assert float(out["S_crest"].min()) >= 0.0
    assert float(out["S_crest"].max()) <= 3.0
    assert out["ridge_1d"].any()


def test_action1_coulomb_loqo_dual_reading_audit_receipt():
    path = ROOT / "evidence/coulomb_loqo_dual_reading_audit.json"
    assert path.is_file()
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["evidence_class"] == "REGISTRY-MEASUREMENT"
    s = doc["candidates"]["COULOMBLOQO_standalone"]
    d45 = doc["candidates"]["COULOMBLOQO_dual45"]
    assert s["continuous_gt_150k_over_70pct_count"] == 0
    assert d45["continuous_gt_150k_over_70pct_count"] == 0
    assert s["continuous_gt_150k_matched_budget_worst_overlap_3px"] < 0.70
    assert d45["continuous_gt_150k_matched_budget_worst_overlap_3px"] < 0.70
    # Post-merge collision with EULERFUSE_gravity recorded honestly
    assert "eulerfuse-gravity" in s["worst_operative_witness"]
    assert s["worst_operative_overlap_3px"] > 0.70
    assert s["dual_reading_verdict_at_150k_cutoff"] == "negative"
    assert d45["dual_reading_verdict_at_150k_cutoff"] == "negative"


def test_knick_loqo_screen_canaries_and_preplacement_uniqueness():
    doc = json.loads((ROOT / "evidence/knick_loqo_screen.json").read_text(encoding="utf-8"))
    can = doc["leakage_canaries"]
    assert len(can["features"]) == 50
    assert can["all_pass"] is True
    assert can["max_symmetric_auc"] <= 0.90
    u = doc["preplacement_surface_uniqueness"]
    assert u["duplicate"] is False
    assert u["worst_abs_spearman_exact_full_footprint"] <= 0.90
    assert u["worst_top37654_forward_3px_overlap"] <= 0.70


def test_knick_loqo_variants_proxy_audit_and_run_card_consistency():
    vdoc = json.loads((ROOT / "evidence/knick_loqo_variants.json").read_text(encoding="utf-8"))
    pdoc = json.loads((ROOT / "evidence/knick_loqo_proxy_audit.json").read_text(encoding="utf-8"))
    dual = json.loads((ROOT / "evidence/knick_loqo_dual_reading_audit.json").read_text(encoding="utf-8"))
    card = json.loads((ROOT / "evidence/knick_loqo_run_card.json").read_text(encoding="utf-8"))
    canon = json.loads((ROOT / "evidence/run_card.json").read_text(encoding="utf-8"))

    assert card == canon
    assert len(vdoc["variants"]) == 3
    for v in vdoc["variants"]:
        tif = ROOT / v["file_zeros"]
        assert tif.is_file()
        assert hashlib.sha256(tif.read_bytes()).hexdigest() == v["sha256_zeros"]
        assert v["n_dots"] == 37654
        assert all(g["ok"] for g in v["gates_zeros"])
        assert all(g["ok"] for g in v["gates_nan"])
        stem = tif.name[: -len("-zeros.tif")]
        sidecar = tif.parent / f"{stem}-audit.json"
        assert sidecar.is_file()
        sdoc = json.loads(sidecar.read_text(encoding="utf-8"))
        assert sdoc["overall_pass"] is True
        assert sdoc["submission_eligible"] is False
        assert sdoc["sha256_zeros"] == v["sha256_zeros"]

    scores = pdoc["hide_and_recover_pooled_by_candidate"]["standalone"]["scores"]
    assert scores["standalone"]["withheld_positive_pixels"] == 22663
    # All-time #1 static HOLDOUT-DTI
    assert scores["standalone"]["dti"] == pytest.approx(0.010788, abs=1e-6)
    assert scores["standalone"]["dti"] > scores["COULOMBLOQO_standalone"]["dti"]
    assert scores["standalone"]["dti"] > scores["EULERFUSE_gravity"]["dti"]
    assert scores["standalone"]["dti"] > scores["uncal"]["dti"]
    # NE quadrant restoration (#IR-92-NE-QUADRANT-LOQO-COLLAPSE cured)
    q_stand = pdoc["quadrant_dot_allocation"]["standalone"]
    q_coul = pdoc["quadrant_dot_allocation"]["COULOMBLOQO_standalone"]
    assert q_stand["Q1"] == 9286
    assert q_stand["Q1"] > 2 * q_coul["Q1"]
    # Public dual-reading uniqueness passes across all 3 arms
    for arm in ("standalone", "uncal", "dual35"):
        du = dual["candidates"][arm]
        assert du["operative_over_70pct_count"] == 0
        assert du["worst_operative_overlap_3px"] <= 0.70
        assert du["dual_reading_verdict"] == "unique"

    assert len(card["submission_name"]) <= 140
    assert len(card["note"]) <= 140
    assert card["weekly_slots_used"] == 0
    assert card["experiments_used"] == 3
    assert card["verdict"] == "negative"
    assert card["submission_eligible"] is False
