"""Unit tests for the PROVINCETOE lane (gems/provincetoe.py)."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import pytest
import rasterio

from gems import ledger, provincetoe as pt

ROOT = Path(__file__).resolve().parents[1]


def _make_quad(h: int, w: int) -> np.ndarray:
    quad = np.zeros((h, w), dtype=np.int8)
    quad[: h // 2, w // 2 :] = 1
    quad[h // 2 :, : w // 2] = 2
    quad[h // 2 :, w // 2 :] = 3
    return quad


def test_wallace_basal_toe_suppresses_symmetric_v_canyon_and_ridge():
    """Basal piedmont fault toe must dominate over symmetric V-canyons and ridge divides."""
    h, w = 80, 120
    valid = np.ones((h, w), dtype=bool)
    x = np.arange(w, dtype=np.float32)[None, :]

    # 1. Piedmont normal-fault basal toe at x = 60: steep footwall (x < 60) -> gentle apron (x >= 60)
    z_fault = np.where(x < 60.0, (60.0 - x) * 28.0, (60.0 - x) * 2.0) + np.zeros((h, 1), dtype=np.float32)
    s_fault = np.degrees(np.arctan(np.abs(np.gradient(z_fault, axis=1)) / 100.0)).astype(np.float32)
    ops_fault = pt.wallace_toe_operators(z_fault, s_fault, valid)
    b_fault = float((ops_fault["toe_concav_s15"] * ops_fault["apron_asymmetry"])[40, 60])
    m_fault = float(ops_fault["step_monotonicity"][40, 60])

    # 2. Symmetric V-shaped erosional canyon at x = 60: both walls steep (28 m/px)
    z_canyon = np.abs(x - 60.0) * 28.0 + np.zeros((h, 1), dtype=np.float32)
    s_canyon = np.degrees(np.arctan(np.abs(np.gradient(z_canyon, axis=1)) / 100.0)).astype(np.float32)
    ops_canyon = pt.wallace_toe_operators(z_canyon, s_canyon, valid)
    b_canyon = float((ops_canyon["toe_concav_s15"] * ops_canyon["apron_asymmetry"])[40, 60])
    m_canyon = float(ops_canyon["step_monotonicity"][40, 60])

    # 3. Symmetric alpine summit ridge at x = 60
    z_ridge = -np.abs(x - 60.0) * 28.0 + np.zeros((h, 1), dtype=np.float32)
    s_ridge = np.degrees(np.arctan(np.abs(np.gradient(z_ridge, axis=1)) / 100.0)).astype(np.float32)
    ops_ridge = pt.wallace_toe_operators(z_ridge, s_ridge, valid)
    b_ridge = float((ops_ridge["toe_concav_s15"] * ops_ridge["apron_asymmetry"])[40, 60])

    assert m_fault > 0.85
    assert m_canyon < 0.05
    assert b_fault > 20.0 * max(b_canyon, 1e-6)
    assert b_ridge == pytest.approx(0.0, abs=1e-5)


def test_within_quadrant_operators_have_exact_zero_cross_quadrant_bleed():
    """Perturbing quadrant 1 arbitrarily must change 0.0 bytes in quadrants 0, 2, 3."""
    rng = np.random.default_rng(42)
    h, w = 64, 64
    valid = np.ones((h, w), dtype=bool)
    quad = _make_quad(h, w)
    base = rng.uniform(0.5, 5.0, size=(h, w)).astype(np.float32)
    pert = base.copy()
    pert[quad == 1] = pert[quad == 1] * 1000.0 + 500.0

    r_base = pt.within_quadrant_relative_contrast(base, valid, quad, sigma_bg=5.0, c0=0.1)
    r_pert = pt.within_quadrant_relative_contrast(pert, valid, quad, sigma_bg=5.0, c0=0.1)
    d_base = pt.within_quadrant_demean(base, valid, quad, sigma_bg=5.0)
    d_pert = pt.within_quadrant_demean(pert, valid, quad, sigma_bg=5.0)

    other = quad != 1
    assert np.array_equal(r_base[other], r_pert[other])
    assert np.array_equal(d_base[other], d_pert[other])


def test_calibrate_quadrant_ranks_is_label_blind_and_equalizes_province_budgets():
    """A depressed-logit province (NE) receives equal tail representation after rank calibration."""
    rng = np.random.default_rng(7)
    h, w = 60, 60
    valid = np.ones((h, w), dtype=bool)
    quad = _make_quad(h, w)
    proba = rng.uniform(0.2, 0.9, size=(h, w)).astype(np.float32)
    # Simulate Walker Lane bias depressing NE (quad == 1) logits by 10x
    proba[quad == 1] *= 0.10

    cal = pt.calibrate_quadrant_ranks(proba, valid, quad, gamma=2.0)
    assert cal.min() >= 0.0 and cal.max() <= 1.0
    # Top 10% global threshold on cal should select ~25% from each equal-area quadrant
    top_mask = cal >= np.quantile(cal[valid], 0.90)
    shares = [float((top_mask & (quad == q)).sum()) / float(top_mask.sum()) for q in range(4)]
    for s in shares:
        assert 0.22 <= s <= 0.28


def test_compute_stack_and_loqo_end_to_end_finite_and_guard_blocked():
    """Full 26-column stack + LOQO cross-fit produces finite [0, 1] surfaces."""
    rng = np.random.default_rng(20261025)
    h, w = 72, 72
    foot = np.ones((h, w), dtype=bool)
    foot[0, :] = False
    quad = _make_quad(h, w)

    def _f(lo: float = -1.0, hi: float = 1.0) -> np.ndarray:
        a = rng.uniform(lo, hi, size=(h, w)).astype(np.float32)
        a[0, :] = -3.4e38
        return a

    stack = pt.compute_provincetoe_stack(
        rtp=_f(-100, 100),
        geod_2ndinv=_f(0, 40),
        grav_slope=_f(0, 0.4),
        geod_shearrate=_f(0, 25),
        geod_dilaterate=_f(-5, 20),
        det_elev=_f(-200, 500),
        grav_anom=_f(-15, 15),
        depth_to_base=_f(0, 1500),
        cond_surf=_f(1, 5),
        grav_hg=_f(-3, 3),
        det_elev_slope=_f(0, 30),
        rad_k=_f(1, 50),
        rad_th=_f(1, 50),
        gdr_plume_feat=_f(0, 2),
        footprint=foot,
        quad=quad,
    )
    X = stack["X_foot"]
    assert X.shape == (int(foot.sum()), len(pt.ALL_FEATURE_NAMES))
    assert np.isfinite(X).all()

    labels = np.zeros((h, w), dtype=bool)
    labels[10:25, 15] = True
    labels[12:28, 52] = True
    labels[48:64, 18] = True
    labels[50:66, 54] = True

    res = pt.fit_predict_provincetoe_loqo(
        X, foot, stack["valid"], quad, labels,
        feature_cols=pt.PRIMARY_COLS,
        calibrate_quadrants=True,
        guard_px=4,
        max_iter=25,
    )
    surf = pt.build_provincetoe_surface(
        res["cal_proba"],
        stack["L_toe_raw"],
        stack["L_sub"],
        stack["slope_deg"],
        stack["valid"],
    )
    assert np.isfinite(surf["S_surface"]).all()
    assert float(surf["S_surface"][~foot].max()) == 0.0
    assert 0.0 <= float(surf["S_surface"].min()) <= float(surf["S_surface"].max()) <= 1.0


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_provincetoe_served_geotiffs_zips_and_audits():
    """Verify all 3 served PROVINCETOE GeoTIFFs, one-TIFF ZIPs, and per-file audit receipts."""
    card = json.loads((ROOT / "evidence/provincetoe_run_card.json").read_text())
    with rasterio.open(ROOT / "data/bridge/sample_submission.tif") as ref_ds:
        ref_crs = ref_ds.crs
        ref_shape = ref_ds.shape
        ref_transform = ref_ds.transform
        foot = np.isfinite(ref_ds.read(1))
    with rasterio.open(ROOT / "data/bridge/existing_faults.tif") as cat_ds:
        cat = (np.nan_to_num(cat_ds.read(1), nan=0.0) > 0.5) & foot

    assert set(card["sibling_arms"].keys()) == {"provincetoe", "globalraw", "piedbasin"}
    for arm, info in card["sibling_arms"].items():
        tif_path = ROOT / info["file"]
        zip_path = ROOT / info["zip_file"]
        stem = tif_path.name[: -len("-zeros.tif")]
        aud_path = ROOT / "docs/downloads" / f"{stem}-audit.json"
        assert tif_path.is_file(), f"missing {tif_path}"
        assert zip_path.is_file(), f"missing {zip_path}"
        assert aud_path.is_file(), f"missing {aud_path}"

        actual_sha = _sha256(tif_path)
        actual_zip_sha = _sha256(zip_path)
        aud = json.loads(aud_path.read_text())
        assert actual_sha == info["sha256"] == aud["sha256_zeros"]
        assert actual_zip_sha == info["zip_sha256"] == aud["zip_sha256"]
        assert aud["submission_eligible"] is False
        assert all(g["ok"] is True for g in aud["gates_zeros"]) and len(aud["gates_zeros"]) == 11

        with zipfile.ZipFile(zip_path, "r") as zf:
            assert zf.namelist() == [tif_path.name]
            assert zf.read(tif_path.name) == tif_path.read_bytes()

        with rasterio.open(tif_path) as ds:
            assert ds.count == 1
            assert ds.dtypes[0] == "float32"
            assert ds.crs == ref_crs
            assert ds.shape == ref_shape == (3730, 3292)
            assert ds.transform == ref_transform
            arr = ds.read(1)
        assert np.isfinite(arr).all()
        assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
        assert float(arr[~foot].max()) == 0.0
        assert int((arr > 0).sum()) == 37654
        assert int(((arr > 0) & cat).sum()) == 0


def test_provincetoe_run_card_holdout_and_uniqueness_contracts():
    """Verify Protocol Rules 1, 3, 4, 5, 6 and zero leaked sandbox paths."""
    card_path = ROOT / "evidence/provincetoe_run_card.json"
    hold_path = ROOT / "evidence/provincetoe_holdout.json"
    uniq_path = ROOT / "evidence/provincetoe_uniqueness.json"
    for p in (card_path, hold_path, uniq_path, ROOT / "docs/downloads/provincetoe_run_card.json"):
        raw = p.read_text()
        assert "/home/user" not in raw, f"sandbox path leaked in {p}"

    card = json.loads(card_path.read_text())
    hold = json.loads(hold_path.read_text())
    uniq = json.loads(uniq_path.read_text())

    assert card["lane"] == "PROVINCETOE"
    assert card["experiments_executed"] == 3 and card["budget_cap_experiments"] == 3
    assert card["weekly_slots_used"] == 0
    assert 1 <= len(card["submission_name"]) <= 140
    assert 1 <= len(card["note"]) == card["note_chars"] <= 140
    assert card["validator_output"]["shape"] == [3730, 3292]
    assert card["validator_output"]["values_range"] == [0.0, 1.0]
    assert card["validator_output"]["no_nan_in_footprint"] is True

    # Rule 4: all 28 leakage canaries <= 0.90
    assert hold["leakage_canaries"]["all_pass"] is True
    assert hold["leakage_canaries"]["n_features_tested"] == len(hold["leakage_canaries"]["rows"]) == 28
    assert hold["leakage_canaries"]["max_symmetric_auc"] <= 0.90

    # Rule 3 & Holdout records: static d_cat > 2.0 #1 & #2 repository records + NE collapse cure
    stat = hold["static_dcat2"]["scores"]
    assert stat["piedbasin"]["dti"] > stat["COULOMBLOQO_standalone"]["dti"] > stat["R0"]["dti"]
    assert stat["provincetoe"]["dti"] > stat["COULOMBLOQO_standalone"]["dti"]
    dvis = hold["rule2_dvis2"]["scores"]
    assert dvis["provincetoe"]["dti"] > dvis["H19_5_dvis2"]["dti"]
    assert hold["rule2_dvis2"]["paired_differences"]["H19_5_dvis2"]["ci95"][0] > 0.0
    assert hold["allocation_diagnostics"]["provincetoe"]["quadrant_shares"]["NE"] > 0.24
    assert hold["allocation_diagnostics"]["globalraw"]["quadrant_shares"]["NE"] < 0.08

    # Rule 1 & Fail-Closed Verdict: locally unique + comparable-budget peer unique, fail-closed negative
    loc = card["correlation_overlap_vs_registry"]["local"]
    pub = card["correlation_overlap_vs_registry"]["public"]
    assert loc["duplicate"] is False and loc["worst_matched_budget_forward_overlap"] <= 0.70
    assert uniq["comparable_budget_peer_diagnostic"]["provincetoe"]["max_overlap_le_50k_dots"] <= 0.70
    assert uniq["comparable_budget_peer_diagnostic"]["piedbasin"]["max_overlap_le_50k_dots"] <= 0.70
    assert pub["duplicate"] is True and card["verdict"] == "negative" and card["submission_eligible"] is False


def test_provincetoe_readme_site_and_ledger_sync():
    """Verify top banners in README & GitHub Pages HTML, analysis docs, and ledger rows."""
    for rel in (
        "README.md",
        "docs/index.html",
        "docs/executive-summary.html",
        "docs/SUBMIT.html",
        "docs/submit.html",
        "docs/HYPOTHESES.html",
    ):
        txt = (ROOT / rel).read_text(encoding="utf-8")
        assert "<!-- PROVINCETOE:BEGIN" in txt and "<!-- PROVINCETOE:END -->" in txt, f"missing banner in {rel}"
        assert "OK TO DOWNLOAD FOR RESEARCH" in txt
        assert "DO NOT SUBMIT" in txt
        assert "gemsdoe92-provincetoe-provincetoe-37654-20261025-8b69d44e-zeros.tif" in txt

    hyp = (ROOT / "docs/HYPOTHESES_20261025_PROVINCETOE.md").read_text(encoding="utf-8")
    ana = (ROOT / "docs/ANALYSIS_20261025_PROVINCETOE.md").read_text(encoding="utf-8")
    assert "PROVINCETOE" in hyp and "FLEXISOSTASY" in hyp
    assert "GEMSDOE32" in ana and "0.2778" in ana and "0.4413" in ana

    rows = [r for r in ledger.load() if r["axis"] == "PROVINCETOE"]
    assert len(rows) == 3
    for r in rows:
        assert r["status"] == "BUILT" and r["receipt_score"] == "" and r["n_dots"] == "37654"

