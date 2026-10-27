"""Regression and receipt-integrity tests for 2026-10-27 session d30d387c."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pytest

from scripts import audit_public_registry, build_public_registry_index, render_review_d30d387c

ROOT = Path(__file__).resolve().parents[1]


def test_d30d387c_run_card_is_reproducible_rejection_only_and_dual_witness_bound():
    card = json.loads(render_review_d30d387c.OUTPUT.read_text(encoding="utf-8"))
    assert card == render_review_d30d387c.build()
    assert render_review_d30d387c.PUBLIC_INPUT.read_bytes() == render_review_d30d387c.INPUT.read_bytes()
    assert render_review_d30d387c.PUBLIC_FLEET.read_bytes() == render_review_d30d387c.FLEET.read_bytes()

    assert card["verdict"] == "negative"
    assert card["submission_eligible"] is False
    assert card["new_unique_tiff_generated"] is False
    assert card["raster_sha256"] is None
    assert card["submission_name"] is None and card["submission_note"] is None
    assert card["experiments"] == card["weekly_slots_used"] == 0
    assert card["holdout_dti"]["value"] is None and card["holdout_dti"]["ci95"] is None
    assert card["organizer_confirmed_score"] is None
    assert card["score_estimate"] is None

    ov = card["correlation_overlap_vs_registry"]
    assert ov["forward_overlap_vs_17gemsdoe_continuous_witness"] == 1.0
    assert ov["pigeonhole_min_overlap_at_37654_dots_vs_13gemsdoe_binary_witness"] > 0.82
    low, high = ov["observed_overlap_range_across_11_oct25_27_delta_artifacts_vs_13gemsdoe"]
    assert 0.98 < low <= high == 1.0

    fixes = card["data_integrity_and_code_fixes_d30d387c"]
    assert fixes["verified_core_pins"] == 12
    assert fixes["verified_external_pins"] == 7
    assert fixes["interior_finite_nodata_sentinel_pixels_bands_1_5_7_19"] == 3061
    assert fixes["interior_finite_nodata_sentinel_pixels_band_6_tc"] == 3073
    assert fixes["band6_tc_pearson_r_vs_geodawn_radiometric_total_count"] > 0.99
    assert abs(fixes["band6_tc_pearson_r_vs_true_magnetic_tilt_atan2_b9_b3"]) < 0.05

    fleet = card["fleet_20261027_summary"]
    assert fleet["delta_artifacts_audited"] == 11
    assert fleet["multi_owner_repos_audited"] == 12
    assert fleet["active_multi_owner_repos_with_tiffs"] == 6
    assert len(fleet["stub_readme_only_multi_owner_repos"]) == 6


def test_d30d387c_run_card_rejects_tampered_fleet_or_input_receipt(tmp_path, monkeypatch):
    bad_fleet = json.loads(render_review_d30d387c.FLEET.read_text(encoding="utf-8"))
    bad_fleet["submission_eligible"] = True
    p = tmp_path / "fleet.json"
    p.write_text(json.dumps(bad_fleet), encoding="utf-8")
    monkeypatch.setattr(render_review_d30d387c, "FLEET", p)
    with pytest.raises(ValueError, match="fleet 2026-10-27"):
        render_review_d30d387c.build()


def test_multi_owner_default_owners_and_nonstandard_submission_subpaths():
    assert set(audit_public_registry.DEFAULT_OWNERS) == {
        "buffedlizard55-lab",
        "kanlerxz87-cyber",
        "eugboogieman123-ops",
        "wingbangboozle1-lang",
        "ginnymcfiner23-ux",
    }
    accepted = [
        "docs/downloads/gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite.tif",
        "data/scored/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif",
        "docs/cadg-submod/downloads/kanlergems2-htcads-exp-2-37654dots.tif",
        "docs/candidate_downloads/wbg1-cand.tif",
        "docs/ssp1/downloads/wbg2-cand.tif",
        "downloads/wbg3-cand.tif",
        "docs/hce/downloads/kanler3-cand.tif",
        "submissions/sub1.tif",
    ]
    for path in accepted:
        assert audit_public_registry._is_submission_tif_path(path), path

    rejected = [
        "data/external/geodawn_rad_u8.tif",
        "data/bridge/training_features.tif",
        "data/bridge/existing_faults.tif",
        "data/bridge/labels.tif",
        "README.md",
    ]
    for path in rejected:
        assert not audit_public_registry._is_submission_tif_path(path), path


def test_classify_and_extract_dots_preserves_full_binary_lattice_without_tie_truncation():
    flat = np.zeros(300_000, dtype=np.float32)
    # 206,895 binary 1.0 pixels spanning both northern and southern halves of the array
    pos_idx = np.linspace(0, 299_999, 206_895, dtype=np.int64)
    flat[pos_idx] = 1.0
    pos = np.flatnonzero(flat > 0)

    kind, extracted, tie_truncated, n_distinct = build_public_registry_index.classify_and_extract_dots(
        flat, pos, dot_field_max=150_000, top_k=200_000
    )
    assert kind == "dense_binary_lattice"
    assert tie_truncated is False
    assert n_distinct == 1
    assert np.array_equal(extracted, pos)
    assert extracted[-1] == 299_999  # southern-most row preserved!

    # By contrast, a continuous multi-level surface > top_k is classified as dense_continuous
    rng = np.random.default_rng(42)
    flat_cont = rng.uniform(0.01, 1.0, size=250_000).astype(np.float32)
    pos_cont = np.flatnonzero(flat_cont > 0)
    kind_c, extracted_c, _, n_distinct_c = build_public_registry_index.classify_and_extract_dots(
        flat_cont, pos_cont, dot_field_max=150_000, top_k=200_000
    )
    assert kind_c == "continuous_surface"
    assert len(extracted_c) == 200_000
    assert n_distinct_c > 2


def test_claimed_ledger_20261027_records_new_claims_and_never_fabricates_organizer_receipts():
    ledger = ROOT / "ledger/site_scores_claimed_20261027.csv"
    rows = list(csv.DictReader(ledger.open(encoding="utf-8")))
    assert len(rows) >= 149
    by_sub = {r["submission_name"]: r for r in rows if r["submission_name"]}
    assert by_sub["gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite"]["score"] == "0.2250"
    assert by_sub["gemsdoe36-kpl36-exp3-20261026-fc869911e88c-zeros"]["score"] == "0.1647"
    assert by_sub["gemsdoe33-s33-seisdil-strain-seismicity-37654-20261026-3463540a7e02-zeros"]["score"] == "0.0963"
    assert by_sub["gems28-s21-puhgb-20261026-16bbf281ba9b-allfinite"]["score"] == "0.0206"
    assert by_sub["gems91-s22-omtj-e1-20261026-a99b8923f0-zeros"]["score"] == "0.0298"
    for r in rows:
        assert "ORGANIZER-CONFIRMED" not in r["evidence_label"]
    sites = {r["site"] for r in rows}
    for multi in (
        "KANLERGEMSDOE1", "KANLERGEMSDOE2", "KANLERGEMSDOE3",
        "EUGGEMSDOE1", "EUGGEMSDOE2", "EUGGEMSDOE3",
        "WBGGEMSDOE1", "WBGGEMSDOE2", "WBGGEMSDOE3",
        "GINNYGEMSDOE1", "GINNYGEMSDOE2", "GINNYGEMSDOE3",
    ):
        assert multi in sites
