"""Automated unit, mathematical-leakage, forensic, and artifact-contract tests for Lane RELAYCONDUIT."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems import ledger as ledger_mod  # noqa: E402
from gems import relayconduit as rc  # noqa: E402


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_relay_fields_exact_self_exclusion_and_stepover_geometry():
    """Every RELAY_COL at component pixels must match brute-force deletion of that component."""
    h, w = 130, 140
    cat = np.zeros((h, w), dtype=bool)
    # Two opposing N-S en-echelon segments separated by an 8-px step-over gap + 1 E-W segment
    cat[22:56, 56] = True
    cat[64:98, 63] = True
    cat[108, 20:52] = True
    valid = np.ones((h, w), dtype=bool)
    strike = np.full((h, w), 18.0, dtype=np.float32)

    full = rc.oriented_tip_relay_fields(cat, strike, valid)
    assert set(full) == {
        "rc_tip_cone_short",
        "rc_tip_cone_long",
        "rc_stepover_bridge",
        "rc_tip_vs_shadow",
        "rc_reg_strike_align",
    }
    for arr in full.values():
        assert arr.dtype == np.float32
        assert np.isfinite(arr).all()

    # Step-over gap between opposing tips must activate strongly; far corner stays near zero
    assert float(full["rc_stepover_bridge"][60, 59]) > 1.5
    assert float(full["rc_stepover_bridge"][5, 5]) < 1e-2

    # Ahead of lower tip (row 98, col 63 -> row 102, col 63) must have positive tip-vs-shadow,
    # whereas broadside stress shadow (row 40, col 62) must be negative.
    assert float(full["rc_tip_vs_shadow"][101, 63]) > 0.4
    assert float(full["rc_tip_vs_shadow"][40, 62]) < -0.5

    # Exact self-exclusion check against brute-force component deletion
    comp_id, n_comp = ndi.label(cat, structure=np.ones((3, 3), dtype=np.int8))
    assert n_comp == 3
    for cid in range(1, n_comp + 1):
        on = comp_id == cid
        ref = rc.oriented_tip_relay_fields(cat & (~on), strike, valid)
        for key in full:
            np.testing.assert_allclose(full[key][on], ref[key][on], atol=1e-4, rtol=1e-4)


def test_stage1_blind_cols_exclude_topography_and_pairwise_oof_is_quadrant_isolated():
    """Perturbing labels in test quadrant q* must have ZERO effect on Stage-1 OOF predictions in q*."""
    topography_tokens = ("geo_", "scarp", "chi", "elev", "relief", "aspect", "hs_lin")
    for idx in rc.STAGE1_BLIND_COLS:
        fname = rc.FEATURE_NAMES[idx]
        assert fname.startswith("sub_"), f"Non-subsurface col in STAGE1_BLIND_COLS: {fname}"
        assert not any(tok in fname for tok in topography_tokens), f"Topographic leak in blind col: {fname}"

    rng = np.random.default_rng(42)
    h, w = 80, 80
    foot = np.ones((h, w), dtype=bool)
    valid = np.ones((h, w), dtype=bool)
    quad = np.zeros((h, w), dtype=np.int32)
    quad[:40, 40:] = 1
    quad[40:, :40] = 2
    quad[40:, 40:] = 3

    X_foot = rng.normal(size=(h * w, len(rc.FEATURE_NAMES))).astype(np.float32)
    label_a = np.zeros((h, w), dtype=bool)
    for q in range(4):
        qy, qx = np.nonzero(quad == q)
        pick = rng.choice(qy.size, size=45, replace=False)
        label_a[qy[pick], qx[pick]] = True

    oof_a = rc.fit_pairwise_stage1_oof(X_foot, label_a, foot, valid, quad, guard_px=2, neg_buffer_px=2.0, seed=7)

    # Completely replace labels in quadrant 3 and verify quadrant 3 OOF predictions are bit-identical
    label_b = label_a.copy()
    label_b[quad == 3] = ~label_b[quad == 3]
    oof_b = rc.fit_pairwise_stage1_oof(X_foot, label_b, foot, valid, quad, guard_px=2, neg_buffer_px=2.0, seed=7)

    q3 = quad == 3
    np.testing.assert_array_equal(oof_a[3][0][q3], oof_b[3][0][q3])
    np.testing.assert_array_equal(oof_a[3][1][q3], oof_b[3][1][q3])


def test_dual_conduit_surface_and_spaced_top_mask_invariants():
    rng = np.random.default_rng(9)
    h, w = 64, 64
    valid = np.ones((h, w), dtype=bool)
    valid[:4, :] = False
    proba = rng.uniform(0.05, 0.95, size=(h, w)).astype(np.float32)
    L_geo = np.zeros((h, w), dtype=np.float32)
    L_sub = np.zeros((h, w), dtype=np.float32)
    L_geo[:, 20] = 0.8
    L_sub[35, :] = 0.9
    w_cover = np.full((h, w), 0.5, dtype=np.float32)

    surf = rc.build_dual_conduit_surface(proba, L_geo, L_sub, w_cover, valid)
    s = surf["S_crest"]
    assert s.dtype == np.float32
    assert np.isfinite(s).all()
    assert float(s.min()) >= 0.0 and float(s.max()) <= 1.0
    assert float(s[~valid].max()) == 0.0

    dots = rc.spaced_top_mask(s, valid & surf["ridge_1d"], 18, min_dist_px=2.8)
    assert int(dots.sum()) == 18
    assert not np.any(dots & (~valid))
    yy, xx = np.nonzero(dots)
    d2 = (yy[:, None] - yy[None, :]) ** 2 + (xx[:, None] - xx[None, :]) ** 2
    np.fill_diagonal(d2, 9999)
    assert int(d2.min()) >= int(np.ceil(2.8 * 2.8 - 1e-9))


def test_empty_catalogue_and_underfill_fail_closed_edge_cases():
    """Empty catalogue returns zero relay fields; underfilled dot budget raises ValueError."""
    cat0 = np.zeros((32, 32), dtype=bool)
    val = np.ones((32, 32), dtype=bool)
    st = np.zeros((32, 32), dtype=np.float32)
    out = rc.oriented_tip_relay_fields(cat0, st, val)
    assert all(v.shape == (32, 32) and v.dtype == np.float32 and np.all(v == 0.0) for v in out.values())

    with pytest.raises(ValueError, match="selected 0 of 10"):
        rc.spaced_top_mask(np.ones((16, 16), dtype=np.float32), np.zeros((16, 16), dtype=bool), 10)


def test_forensic_r0_pixel_identity_and_labels_count():
    """Reproducibly verify the GEMSDOE32 R0 == D2.8 & (EDT > 2.0) proof and labels.tif == 60,988."""
    with rasterio.open(ROOT / "data" / "bridge" / "labels.tif") as ds_lab:
        lab = ds_lab.read(1)
    with rasterio.open(ROOT / "data" / "bridge" / "existing_faults.tif") as ds_ef:
        ef = np.nan_to_num(ds_ef.read(1), nan=0.0) > 0.0
    with rasterio.open(ROOT / "data" / "bridge" / "d28.tif") as ds_d28:
        d28 = np.nan_to_num(ds_d28.read(1), nan=0.0) > 0.0
    with rasterio.open(ROOT / "data" / "bridge" / "h27_4_solo.tif") as ds_solo:
        solo = np.nan_to_num(ds_solo.read(1), nan=0.0) > 0.0
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds_r0:
        r0 = np.nan_to_num(ds_r0.read(1), nan=0.0) > 0.0

    assert int((np.nan_to_num(lab, nan=0.0) > 0.0).sum()) == 60_988
    assert int(ef.sum()) == 60_988
    edt = ndi.distance_transform_edt(~ef)
    assert int(np.logical_xor(solo, d28 & (edt > 1.0)).sum()) == 0
    assert int(np.logical_xor(r0, d28 & (edt > 2.0)).sum()) == 0
    assert int(r0.sum()) == 37_654


def test_relayconduit_run_card_artifacts_ledger_and_site_contracts():
    """Verify Run Card, Holdout, Uniqueness, 3 GeoTIFFs/ZIPs/Audits, Ledger, and Site links."""
    rc_path = ROOT / "evidence" / "relayconduit_run_card.json"
    ho_path = ROOT / "evidence" / "relayconduit_holdout.json"
    uq_path = ROOT / "evidence" / "relayconduit_uniqueness.json"
    for p in (rc_path, ho_path, uq_path):
        assert p.is_file(), f"Missing {p}"
        dl_mirror = DOCS / "downloads" / p.name
        assert dl_mirror.is_file() and dl_mirror.read_bytes() == p.read_bytes()

    card = json.loads(rc_path.read_text(encoding="utf-8"))
    holdout = json.loads(ho_path.read_text(encoding="utf-8"))
    uniq = json.loads(uq_path.read_text(encoding="utf-8"))

    for req_key in (
        "hypothesis",
        "mechanism",
        "named_non_fault_process_that_could_mimic_it",
        "holdout_dti",
        "correlation_overlap_vs_registry",
        "raster_sha256",
        "validator_output",
        "submission_name",
        "note",
        "verdict",
    ):
        assert req_key in card

    assert card["arm"] == "relay_conduit"
    assert card["verdict"] == "negative"
    assert card["submission_eligible"] is False
    assert card["ok_to_download"] is True
    assert card["ok_to_submit"] is False
    assert card["experiments_used"] == 3
    assert card["weekly_slots_used"] == 0
    assert len(card["note"]) <= 140
    assert card["leakage_canary"]["all_pass"] is True
    assert card["leakage_canary"]["max_single_feature_symmetric_auc"] <= 0.90

    # Local uniqueness on hero relay_conduit (across all 128+ post-merge local rasters) and
    # external 102-repo operative uniqueness on zero-catalogue conduit_notip
    loc_rc = uniq["local_summary"]["relay_conduit"]
    pub_cn = uniq["public_102repo_summary"]["conduit_notip"]
    assert loc_rc["local_unique"] is True and loc_rc["worst_forward_overlap_3px"] <= 0.70
    assert pub_cn["unique_operative"] is True and pub_cn["worst_operative_overlap_3px"] <= 0.70
    assert pub_cn["operative_over_70pct_count"] == 0
    assert pub_cn["worst_surface_abs_spearman"] <= 0.90
    assert pub_cn["literal_worst_overlap_3px"] == 1.0 and pub_cn["unique_under_literal_rule"] is False

    # Statistical holdout findings
    r2_scores = holdout["strict_draw_blind_rule2_holdout_dti"]["scores"]
    assert r2_scores["relay_conduit"]["dti"] > r2_scores["control_COULOMBLOQO_d32"]["dti"]
    pair_rc = holdout["strict_draw_blind_rule2_holdout_dti"]["paired_differences_by_arm"]["relay_conduit"]["control_COULOMBLOQO_d32"]
    assert pair_rc["ci95"][0] > 0.0
    assert holdout["sgmc_off_catalogue_proxy"]["conduit_notip"]["dti"] > 0.10

    # Verify all 3 GeoTIFFs, ZIPs, audits, ledger entries, and site links
    with rasterio.open(ROOT / "data" / "bridge" / "sample_submission.tif") as ref:
        ref_crs, ref_shape, ref_transform = ref.crs, ref.shape, ref.transform
        foot = np.isfinite(ref.read(1))

    ledger_by_id = {r["id"]: r for r in ledger_mod.load()}
    index_html = (DOCS / "index.html").read_text(encoding="utf-8")
    exec_html = (DOCS / "executive-summary.html").read_text(encoding="utf-8")
    submit_html = (DOCS / "SUBMIT.html").read_text(encoding="utf-8")
    subpage_html = (DOCS / "relayconduit.html").read_text(encoding="utf-8")
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
            assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
            assert float(arr[~foot].max()) == 0.0
            assert int((arr > 0).sum()) == 37_654

        assert art["stem"] in ledger_by_id
        assert ledger_by_id[art["stem"]]["sha256"] == art["sha256_zeros"]
        for page_txt in (index_html, exec_html, submit_html, subpage_html):
            assert f"downloads/{tif_path.name}" in page_txt
        assert f"docs/downloads/{tif_path.name}" in readme_txt

    # Verify newly supplied GEMSDOE91 & GEMSDOE92 claims in site_scores_claimed_20261025.csv
    with (ROOT / "ledger" / "site_scores_claimed_20261025.csv").open("r", encoding="utf-8") as f:
        claimed_rows = list(csv.DictReader(f))
    scores_by_site = {}
    for r in claimed_rows:
        if r.get("score"):
            scores_by_site.setdefault(r["site"], set()).add(r["score"])
    assert {"0.1367", "0.1823"}.issubset(scores_by_site["GEMSDOE91"])
    assert "0.0255" in scores_by_site["GEMSDOE92"]

    assert (DOCS / "HYPOTHESES_20261025_RELAYCONDUIT.md").is_file()
    assert (DOCS / "ANALYSIS_20261025_RELAYCONDUIT.md").is_file()

    # Pass-2 link-integrity regression check across entry & RELAYCONDUIT pages
    import re
    for page in (
        ROOT / "README.md",
        DOCS / "index.html",
        DOCS / "executive-summary.html",
        DOCS / "SUBMIT.html",
        DOCS / "relayconduit.html",
        DOCS / "HYPOTHESES_20261025_RELAYCONDUIT.md",
        DOCS / "ANALYSIS_20261025_RELAYCONDUIT.md",
    ):
        txt = page.read_text(encoding="utf-8")
        for m in re.finditer(r'href="([^"]+)"', txt):
            u = m.group(1).split("#")[0]
            if u and not u.startswith(("http://", "https://", "mailto:")):
                assert (page.parent / u).resolve().exists(), f"Broken href {u} in {page.name}"

