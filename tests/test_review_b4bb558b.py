"""Fresh audit, input evidence, and public negative card remain bound together."""
from __future__ import annotations

import json

import pytest

from scripts import render_review_b4bb558b as review


def test_new_public_card_is_reproducible_and_does_not_relabel_old_raster():
    card = json.loads(review.OUTPUT.read_text())
    assert card == review.build()
    assert review.PUBLIC_INPUT.read_bytes() == review.INPUT.read_bytes()
    assert card['verdict'] == 'negative' and not card['submission_eligible']
    assert not card['new_unique_tiff_generated'] and card['raster_sha256'] is None
    assert card['submission_name'] is None and card['submission_note'] is None
    assert card['experiments'] == card['weekly_slots_used'] == 0
    assert card['holdout_dti']['value'] is None and card['holdout_dti']['ci95'] is None
    overlap = card['correlation_overlap_vs_registry']
    assert overlap['forward_overlap_for_any_nonempty_in_footprint_candidate'] == 1.0
    assert overlap['overlap_threshold'] == 0.70 and overlap['rank_correlation'] is None
    assert card['historical_research_reference']['status'] == 'research only; DO NOT SUBMIT'
    cache = card['input_cache_audit']
    assert cache['verified_pins'] == cache['expected_pins'] == 12
    assert cache['feature_band_count'] == 19 and cache['grid_and_band_tags_match']
    assert not cache['official_origin_authenticated'] and not cache['redistribution_rights_verified']
    assert card['nine_site_rerun']['pairs_checked'] == 36


def test_card_rejects_fabricated_pin_or_origin_claim(tmp_path, monkeypatch):
    data = json.loads(review.INPUT.read_text())
    data['files'][0]['expected_sha256'] = 'a' * 64
    data['files'][0]['observed_sha256'] = 'a' * 64
    bad = tmp_path / 'input.json'
    bad.write_text(json.dumps(data))
    monkeypatch.setattr(review, 'INPUT', bad)
    with pytest.raises(ValueError, match='pinned manifest'):
        review.build()
    data = json.loads(review.PUBLIC_INPUT.read_text())
    data['official_origin_authenticated'] = True
    bad.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='overclaims provenance'):
        review.build()
