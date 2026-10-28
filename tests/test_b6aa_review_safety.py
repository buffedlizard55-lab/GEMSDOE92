"""Release-blocking gates: no projection or self-declared verdict may promote."""
import copy
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]

def test_negative_candidate_and_both_binding_failures():
    c = json.loads((ROOT/'evidence/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json').read_text())
    assert c['verdict'] == 'negative' and c['submission_eligible'] is False
    assert c['gates_passed']['catalogue_holdout_beats_r0_recipe'] is False
    assert c['uniqueness']['literal_reading']['duplicate_under_literal'] is True
    assert c['uniqueness']['surface_worst_overlap'] > .70

def test_renderer_rejects_forged_promotion():
    from scripts.render_safe_review import render
    c = json.loads((ROOT/'evidence/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json').read_text())
    for key, value in [('verdict','promote'),('submission_eligible',True)]:
        forged = copy.deepcopy(c); forged[key] = value
        with pytest.raises(ValueError, match='blocked'):
            render(forged)

def test_live_pages_and_feeds_unambiguously_negative():
    for filename in ['index.html','nine-sites.html','how-to-submit.html','executive-summary.html','SUBMIT.html','submit.html','SUBMIT_NOW.html']:
        text = (ROOT/'docs'/filename).read_text()
        assert 'DO NOT SUBMIT' in text and 'OK TO SUBMIT' not in text
    readiness = json.loads((ROOT/'docs/downloads/readiness.json').read_text())
    assert readiness['submission_eligible'] is False and readiness['verdict'] == 'negative'
    assert len(readiness['blocking_reasons']) >= 3
    assert any('HOLDOUT-DTI' in reason for reason in readiness['blocking_reasons'])
