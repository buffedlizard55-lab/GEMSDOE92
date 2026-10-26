"""Evidence, stop ordering, and public wording for the rejection-only review."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts import audit_score_estimator, render_focus9_page, render_review_14f85876, render_review_banner

ROOT = Path(__file__).resolve().parents[1]


def test_public_run_card_is_reproducible_rejection_only_and_byte_bound():
    actual = json.loads(render_review_14f85876.OUTPUT.read_text())
    assert actual == render_review_14f85876.build()
    assert actual["verdict"] == "negative"
    assert actual["submission_eligible"] is False
    assert actual["new_unique_tiff_generated"] is False
    assert actual["experiments"] == actual["weekly_slots_used"] == 0
    assert actual["holdout_dti"]["value"] is None
    assert actual["organizer_confirmed_score"] is None
    assert actual["estimated_leaderboard_score"] is None
    proof = actual["correlation_overlap_vs_registry"]["preplacement_proof"]
    assert proof["universal_nonempty_in_footprint_overlap_stop"] is True
    assert proof["positive_in_footprint"] == proof["footprint_pixels"] == 5_167_373
    assert proof["forward_overlap_for_any_nonempty_in_footprint_dot_set"] == 1.0
    assert proof["threshold"] == 0.70
    data = (ROOT / actual["primary_download"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == actual["raster_sha256"]
    assert all(r["ok"] is True for r in actual["validator_output"])
    assert 0 < len(actual["note"]) <= 140
    assert 0 < len(actual["submission_name"]) <= 140
    pair_file = ROOT / actual["focus_pairwise_correction"]["path"]
    assert hashlib.sha256(pair_file.read_bytes()).hexdigest() == actual["focus_pairwise_correction"]["sha256"]
    pair = json.loads(pair_file.read_text())
    assert pair["pairs"] == 36 and pair["pairs_with_changed_metrics"] == 35
    assert pair["all_match_prior"] is False
    assert pair["all_pairs_duplicate_in_at_least_one_direction_or_rho"] is True
    assert all("duplicate_by_configured_threshold" not in p["fields"] for p in pair["differences_from_prior"])
    p24_25 = next(p for p in pair["comparisons"] if p["site_a"] == "GEMSDOE24" and p["site_b"] == "GEMSDOE25")
    assert p24_25["forward_3px_overlap_a_to_b"] == 1.0
    assert p24_25["forward_3px_overlap_b_to_a"] == 1.0
    identical = [p for p in pair["comparisons"] if p["exact_prediction_match"]]
    assert [(p["site_a"], p["site_b"]) for p in identical] == [("GEMSDOE25", "GEMSDOE30")]


@pytest.mark.parametrize("module_name", ["run_salem_seismo", "run_thermotilt", "run_chilistric", "run_listric_loqo"])
def test_historical_runners_stop_before_mutating_prior_outputs(tmp_path, monkeypatch, module_name):
    import importlib
    runner = importlib.import_module(f"scripts.{module_name}")

    downloads = tmp_path / "downloads"
    downloads.mkdir()
    prior = downloads / "prior-SALEMSEISMO-zeros.tif"
    prior.write_bytes(b"prior immutable research artifact")
    monkeypatch.setattr(runner, "DOWNLOADS", downloads)
    monkeypatch.setattr(runner, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(runner, "EVIDENCE", tmp_path / "evidence")
    with pytest.raises(SystemExit, match="literal pre-placement registry duplicate"):
        runner.main()
    assert prior.read_bytes() == b"prior immutable research artifact"
    assert not (tmp_path / "cache").exists()
    assert not (tmp_path / "evidence").exists()
    assert list(downloads.iterdir()) == [prior]


def test_static_forensic_audit_cannot_overwrite_its_historical_receipt(tmp_path):
    from scripts import audit_focus9_sites
    prior = tmp_path / "prior.json"
    prior.write_text("historical evidence")
    with pytest.raises(SystemExit, match="do not overwrite prior evidence"):
        audit_focus9_sites.main(["--output", str(prior)])
    assert prior.read_text() == "historical evidence"


def test_claim_estimator_cli_cannot_publish_predictions(tmp_path, monkeypatch):
    from scripts import estimate_scores

    target = tmp_path / "historical.json"
    target.write_text("unchanged")
    monkeypatch.setattr(estimate_scores, "OUT", target)
    with pytest.raises(SystemExit, match="unverified CLAIM labels"):
        estimate_scores.main()
    assert target.read_text() == "unchanged"


def test_current_renderer_cannot_promote_via_sparse_only_flags(tmp_path):
    from scripts.render_vario_status import load_card

    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "vario_run_card.json").write_text(json.dumps({
        "lane": "VARIO", "verdict": "promote",
        "gates": {"format": True, "canary": True,
                  "holdout_beats_best_control": True, "operative_uniqueness": True},
    }))
    with pytest.raises(ValueError, match="literal registry pre-placement STOP"):
        load_card(tmp_path)
    from scripts.render_vario_status import readiness, current_submission, panel_html, panel_md, vario_page
    card = {"verdict": "promote"}
    for function, args in ((readiness, (card,)), (current_submission, (card,)),
                           (panel_html, (card, {})), (panel_md, (card, {})),
                           (vario_page, (card, {}))):
        with pytest.raises(ValueError, match="literal registry pre-placement STOP"):
            function(*args)


def test_older_current_submission_renderers_cannot_assert_clearance():
    from scripts.render_current_submission import html_block, md_block
    for renderer in (html_block, md_block):
        with pytest.raises(ValueError, match="literal registry pre-placement STOP"):
            renderer({"ok_to_submit": True}, "")
        with pytest.raises(ValueError, match="literal registry pre-placement STOP"):
            renderer({}, "")


@pytest.mark.parametrize("lane", ["provincetoe", "poissonflex"])
def test_historical_site_renderers_reject_eligible_cards_before_writing(lane, monkeypatch):
    import runpy
    from pathlib import Path
    original = Path.read_text
    card_name = f"{lane}_run_card.json"

    def read_text(path, *args, **kwargs):
        text = original(path, *args, **kwargs)
        if path.name == card_name:
            card = json.loads(text)
            card["submission_eligible"] = True
            return json.dumps(card)
        return text

    monkeypatch.setattr(Path, "read_text", read_text)
    with pytest.raises(ValueError, match="literal registry pre-placement STOP"):
        runpy.run_path(str(ROOT / f"scripts/render_{lane}_site.py"))


def test_grouping_merges_same_site_and_exact_recorded_vectors_transitively():
    rows = [
        {"site": "a", "frac_h19_near3": 0.1, "frac_dcat_le2": 0.2, "n_dots": 10, "quadrant_imbalance": 0.3},
        {"site": "a", "frac_h19_near3": 0.4, "frac_dcat_le2": 0.2, "n_dots": 10, "quadrant_imbalance": 0.3},
        {"site": "b", "frac_h19_near3": 0.4, "frac_dcat_le2": 0.2, "n_dots": 10, "quadrant_imbalance": 0.3},
        {"site": "c", "frac_h19_near3": 0.9, "frac_dcat_le2": 0.2, "n_dots": 10, "quadrant_imbalance": 0.3},
    ]
    g = audit_score_estimator.groups_for(rows)
    assert g[0] == g[1] == g[2] != g[3]


def test_grouped_diagnostic_is_reproducible_but_never_a_prediction_interval():
    data = json.loads(audit_score_estimator.OUTPUT.read_text())
    assert data == audit_score_estimator.audit()
    assert data["training_rows"] == 107
    assert data["groups"] < data["training_rows"]
    assert data["rows_in_multimember_groups"] > 0
    assert data["row_loo_rmse_recomputed"] > 0
    assert data["leave_group_out_rmse"] > 0
    assert data["valid_leaderboard_prediction"] is False
    assert data["individual_prediction_interval_available"] is False
    assert any("not nested" in x for x in data["limitations"])


def test_focus_review_and_latest_visible_panels_do_not_claim_clearance_or_pm():
    assert render_focus9_page.OUTPUT.read_text() == render_focus9_page.render()
    page = render_focus9_page.OUTPUT.read_text()
    assert "DO NOT SUBMIT" in page and "Not supportable" in page
    assert "0.2778 CLAIM" in page and "not an organizer-confirmed" in page
    assert "0.0832 ± 0.0722" not in page
    assert "<strong>not</strong> a per-file ± prediction interval" in page
    assert "not a guarantee" not in page or "not a guarantee of portal acceptance" in page
    for rel in render_review_banner.PAGES:
        text = (ROOT / rel).read_text()
        assert text == render_review_banner.render_page(text, root_page=rel == "index.html")
        visible = text.split(render_review_banner.BEGIN, 1)[1].split(render_review_banner.END, 1)[0]
        assert "DO NOT SUBMIT" in visible and "No new TIFF" in visible
        assert "focus9.html" in visible
        assert "data-official-leaderboard" in visible
        assert text.index(render_review_banner.END) < text.index('id="historical-research-archive"')
