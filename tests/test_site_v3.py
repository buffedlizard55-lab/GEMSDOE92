"""Contract for the evidence-bound v3 site (2026-10-27)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _card():
    import render_site_v3
    return json.loads(render_site_v3.PRIMARY_CARD.read_text(encoding="utf-8"))


def test_pages_are_exactly_the_rendered_evidence():
    import render_site_v3
    for path, text in render_site_v3.render().items():
        assert path.read_text(encoding="utf-8") == text, f"stale: {path}"


def test_single_primary_bound_to_bytes_audit_and_run_card():
    from check_site import primary_download, _audit_path
    from gems.rasters import sha256_file
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    problems: list[str] = []
    rel = primary_download(html, problems)
    assert rel and not problems
    tif = DOCS / rel
    digest = sha256_file(tif)
    audit = json.loads(_audit_path(tif).read_text(encoding="utf-8"))
    card = json.loads((ROOT / audit["run_card"]).read_text(encoding="utf-8"))
    assert audit["sha256_zeros"] == digest == card["raster_sha256"]
    assert audit["verdict"] == card["verdict"] and audit["submission_eligible"] is card["submission_eligible"]
    assert all(r["ok"] is True for r in audit["gates_zeros"])


def test_status_feeds_agree_with_run_card():
    card = _card()
    cur = json.loads((DOCS / "downloads/current_submission.json").read_text(encoding="utf-8"))
    rdy = json.loads((DOCS / "downloads/readiness.json").read_text(encoding="utf-8"))
    assert cur["sha256"] == rdy["raster_sha256"] == card["raster_sha256"]
    assert cur["ok_to_submit"] is rdy["submission_eligible"] is card["submission_eligible"]
    assert cur["submission_name"] == rdy["submission_name"] == card["submission_name"]
    assert cur["note"] == rdy["note"] == card["note"] and 0 < len(card["note"]) <= 140


def test_verdict_wording_is_unambiguous_and_first():
    card = _card()
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    box = html.split('id="submit-now"', 1)[1].split("</section>", 1)[0]
    assert html.index('id="submit-now"') < html.index('id="summary"')
    if card["verdict"] == "promote":
        assert "OK TO SUBMIT" in box and "DO NOT SUBMIT" not in box
    else:
        assert "DO NOT SUBMIT" in box and "OK TO SUBMIT" not in box


def test_promoted_card_satisfies_every_promotion_gate():
    card = _card()
    if card["verdict"] != "promote":
        pytest.skip("current primary is not promoted")
    g = card["gates_passed"]
    assert g["format"] and g["uniqueness_pi1"] and g["model_beats_0_2778_at_q05"]
    assert g["model_robust_all_specs_ge_R0"] and g["no_leakage"]
    u = card["uniqueness"]
    assert u["final_worst_overlap"] <= 0.70 and u["final_worst_abs_rho"] <= 0.90
    assert u["surface_worst_abs_rho"] <= 0.90
    assert card["leakage_canaries"]["max_auc"] <= 0.90
    assert card["model_estimate"]["bootstrap"]["q05"] > 0.2778
    v = card["validator_output"]
    for k in ("no_nan_in_footprint", "values_in_0_1", "crs_match", "shape_match", "transform_match"):
        assert v[k] is True


def test_run_card_has_protocol_fields_and_labels():
    card = _card()
    for k in ("hypothesis", "mechanism", "named_non_fault_mimic", "holdout_dti", "uniqueness",
              "validator_output", "raster_sha256", "submission_name", "note", "verdict"):
        assert k in card
    assert card["holdout_dti"]["evidence_class"] == "HOLDOUT-DTI"
    assert card["model_estimate"]["evidence_class"].startswith("MODEL")
    assert card["holdout_dti"]["withheld_positive_pixels"] > 0


def test_how_to_page_explains_portal_error_and_limits():
    html = (DOCS / "how-to-submit.html").read_text(encoding="utf-8")
    assert "Predicted values must be in range [0, 1]" in html
    assert "3 submissions per week" in html
    assert "drivendata.org/competitions/306/competition-doe-gems/submissions/" in html


def test_renderer_refuses_model_based_override(monkeypatch):
    import render_site_v3
    card, f9, f9u, model, val = render_site_v3.load()
    card['verdict'] = 'promote'
    card['submission_eligible'] = True
    monkeypatch.setattr(render_site_v3, 'load', lambda: (card, f9, f9u, model, val))
    with pytest.raises(ValueError, match='blocked'):
        render_site_v3.render()


def test_current_research_file_failed_mandatory_gates():
    card = _card()
    assert card['verdict'] == 'negative' and card['submission_eligible'] is False
    assert card['gates_passed']['catalogue_holdout_beats_r0_recipe'] is False
    assert card['uniqueness']['literal_reading']['duplicate_under_literal'] is True
