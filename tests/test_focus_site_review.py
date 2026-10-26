"""The dated focus-site publication is byte-bound to its durable evidence."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.render_focus_site_review import EVIDENCE, HTML, MARKDOWN, PUBLIC_JSON, generate

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
           "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]


def _data():
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_review_is_rejection_only_and_preserves_all_pairwise_results():
    data = _data()
    assert data["decision"]["new_unique_tiff_generated"] is False
    assert data["decision"]["new_submission_file_downloadable"] is False
    assert data["decision"]["cleared_to_submit"] is False
    assert data["decision"]["experiments"] == 0
    assert data["decision"]["holdout_dti_run"] is False
    assert data["decision"]["weekly_slots_used"] == 0
    concurrent = data["current_upstream_main_context"]
    assert concurrent["lane"].startswith("BLINDEXT")
    assert concurrent["downloadable_for_research"] is True
    assert concurrent["submission_eligible"] is False
    assert concurrent["experiment_count"] == 1
    assert concurrent["weekly_slots_used"] == 0
    assert concurrent["holdout_dti"]["available"] is False
    assert concurrent["registry_measurement_from_lane_run_card"]["duplicate"] is True
    assert concurrent["artifact_git_blob_sha256_verified"] is True
    assert data["protocol"]["witness"]["positive_in_footprint"] == 5_167_373
    assert data["protocol"]["universal_stop_verified"] is True
    assert data["protocol"]["witness"]["universal_stop_verified"] is True
    assert data["protocol"]["literal_full_footprint_overlap"] == 1.0
    assert data["protocol"]["overlap_3px_threshold"] == 0.70
    assert data["protocol"]["absolute_binary_support_rank_correlation_threshold"] == 0.90
    assert len(data["all_pairwise_comparisons"]) == 36
    assert all(p["duplicate_by_configured_threshold"] for p in data["all_pairwise_comparisons"])


def test_each_site_claim_is_unconfirmed_and_has_a_directional_duplicate_witness():
    data = _data()
    sites = data["selected_site_artifacts"]
    assert [r["site"] for r in sites] == TARGETS
    for row in sites:
        assert row["score_provenance"].startswith("CLAIM")
        assert row["organizer_receipt_verified"] is False
        assert row["score_to_raster_receipt_verified"] is False
        assert row["estimated_score"] is None
        assert row["downloadable_for_research"] is True
        assert row["cleared_to_submit"] is False
        witness = row["uniqueness_vs_other_eight"]
        assert witness["passes_requested_thresholds"] is False
        assert witness["candidate_to_witness_overlap_3px"] > 0.70 or \
            witness["abs_binary_support_rank_correlation"] > 0.90
        fmt = row["format_only_validation"]
        assert fmt["passed"] is True
        assert fmt["gates_passed"] == fmt["gates_total"] == 9
        assert all(g["ok"] for g in fmt["gate_results"])
        assert row["comparison_reference"]["same_in_footprint_prediction_as_reported_artifact"] is True
        assert row["comparison_reference"]["exact_array_match_rechecked"] is True


def test_exact_duplicate_and_lineage_irregularities_are_explicit():
    data = _data()
    exact = [(p["site_a"], p["site_b"]) for p in data["all_pairwise_comparisons"]
             if p["exact_prediction_match"]]
    assert exact == [("GEMSDOE25", "GEMSDOE30")]
    r0 = data["strongest_reference"]
    assert r0["site"] == "GEMSDOE32"
    assert r0["score_claim"] == 0.2778
    assert "R0 is exactly D2.8" in r0["local_lineage"]
    assert len(data["all_17_source_variants"]) == 17
    assert all(f["tree_blob_match_verified"] for f in data["all_17_source_variants"])


def test_rendered_public_outputs_match_durable_evidence_and_warn_clearly():
    data = _data()
    outputs = generate(data)
    assert outputs[PUBLIC_JSON] == PUBLIC_JSON.read_text(encoding="utf-8")
    assert outputs[MARKDOWN] == MARKDOWN.read_text(encoding="utf-8")
    assert outputs[HTML] == HTML.read_text(encoding="utf-8")
    html = outputs[HTML]
    assert "NO NEW TIFF" in html and "DO NOT SUBMIT" in html
    assert "Research TIFF" in html and "Not supportable" in html
    assert "no live organizer page" in html.lower()
    assert "all 36 pairs breach" in html
    assert "Separate current-main artifact" in html
    assert "BLINDEXT" in html and "no HOLDOUT-DTI result" in html
    assert 'href="downloads/gemsdoe92-blindext-20261026T162451Z-zeros.tif"' in html
    assert 'href="downloads/gemsdoe92-blindext-20261026T162451Z_run_card.json"' in html
    assert 'href="downloads/focus_sites_release_review_20261026.json"' in html
    assert "✅ OK TO SUBMIT" not in html
    assert Path(ROOT / "docs/downloads/focus_sites_release_review_20261026.json").is_file()
    assert json.loads(PUBLIC_JSON.read_text(encoding="utf-8")) == data


def test_hypothesis_screen_ranks_five_untried_candidates_and_marks_top_holdout_blocked():
    path = ROOT / "docs/HYPOTHESES_20261026_SITE_REVIEW.md"
    text = path.read_text(encoding="utf-8")
    assert text.count("| **") >= 1
    assert "LOCAL-WAVENUMBER-CONSENSUS" in text
    assert "STREAM-PLANFORM-OFFSET GRAPH" in text
    assert "FOCAL-MECHANISM / GEODETIC SLIP-PLANE CONSENSUS" in text
    assert "SEIS-GRAV-SIGNED-LAG" in text
    assert "SEASONAL LANDSAT THERMAL-PERSISTENCE" in text
    assert "Holdout result: NOT RUN" in text
    assert "Not viable in this run" in text
    assert "method paragraph is present" in text
    assert "AUC above `0.90`" in text
    assert "Separate current-repository context" in text and "Do not submit it." in text
