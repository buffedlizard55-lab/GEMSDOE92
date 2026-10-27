"""The latest card and executive table stay evidence-bound and rejection-only."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import render_focus9_page, render_review_b97812a3 as review

ROOT = Path(__file__).resolve().parents[1]


def test_run_card_is_reproducible_and_does_not_promote():
    actual = json.loads(review.OUTPUT.read_text())
    assert review.build() == actual
    assert actual['verdict'] == 'negative' and actual['submission_eligible'] is False
    assert actual['new_unique_tiff_generated'] is False
    assert actual['raster_sha256'] is None and actual['submission_name'] is None
    assert actual['submission_note'] is None and actual['weekly_slots_used'] == 0
    assert actual['holdout_dti']['value'] is None
    assert actual['correlation_overlap_vs_registry']['rank_correlation'] is None
    assert actual['correlation_overlap_vs_registry']['final_dots_overlap'] is None
    old = actual['historical_research_reference']
    assert old['status'] == 'research only; DO NOT SUBMIT'
    assert old['format_pass'] is True and old['prior_holdout_dti']['status'].startswith('historical')


def test_review_rejects_corrupted_support_receipt(tmp_path, monkeypatch):
    altered = json.loads(review.SUPPORT.read_text())
    altered['statistics']['positive_footprint_pixels'] -= 1
    path = tmp_path / 'support.json'
    path.write_text(json.dumps(altered))
    monkeypatch.setattr(review, 'SUPPORT', path)
    with pytest.raises(ValueError, match='witness characterization'):
        review.build()


def test_focus_page_distinguishes_historical_ref_checks_from_scores():
    text = (ROOT / 'docs/focus9.html').read_text()
    assert text == render_focus9_page.render()
    assert 'Not a current or complete inventory' in text
    assert 'pixel-exact, not a surrounding buffer' in text
    assert 'nearby unmasked predictions are evaluated normally' in text
    assert 'continuous-probability' in text and 'not proof of geological identity' in text
    assert 'focus-freshness.js' in text
    assert 'body{background:#f5f7fb;color:#17212b}' in text
    assert 'aria-label="Scrollable historical nine-site table"' in text
    assert text.count('data-focus-repo=') == 9
    assert 'session_b97812a3_run_card.json' in text


def test_focus_page_rejects_snapshot_not_bound_to_inventory(tmp_path, monkeypatch):
    altered = json.loads(render_focus9_page.FRESHNESS.read_text())
    altered['inventory_sha256'] = '0' * 64
    path = tmp_path / 'fresh.json'
    path.write_text(json.dumps(altered))
    monkeypatch.setattr(render_focus9_page, 'FRESHNESS', path)
    with pytest.raises(ValueError, match='inconsistent with the pinned inventory'):
        render_focus9_page.render()
