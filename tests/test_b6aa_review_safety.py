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

def test_tipcomp_is_visible_but_not_promoted_on_landing_page():
    import hashlib
    card_path = ROOT/'docs/downloads/gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6_run_card.json'
    card = json.loads(card_path.read_text())
    raster = ROOT/card['raster']['file']
    assert hashlib.sha256(raster.read_bytes()).hexdigest() == card['raster_sha256']
    assert card['verdict'] == 'negative' and card['submission_eligible'] is False
    assert card['model_estimate']['candidate']['bootstrap_refit26']['q05'] < 0.2778
    assert card['holdout_dti']['paired_e2_vs_r0_recipe']['ci95'][0] < 0
    assert card['holdout_dti']['paired_e2_vs_r0_recipe']['ci95'][1] > 0
    for filename in ['index.html', 'nine-sites.html']:
        page = (ROOT/'docs'/filename).read_text()
        assert 'Latest additional candidate: TIPCOMP — DO NOT SUBMIT' in page
        assert 'Download TIPCOMP GeoTIFF for research only — DO NOT SUBMIT' in page
        assert 'not a complete registry scan and does not resolve the dense-witness interpretation' in page
    summary = (ROOT/'docs/executive-summary-20261028-tipcomp.html').read_text()
    assert 'DO NOT SUBMIT — this candidate is not eligible' in summary
    assert 'No separate selector or weekly slot authorizes bypassing a failed mandatory gate' in summary


def test_live_pages_and_feeds_unambiguously_negative():
    for filename in ['index.html','nine-sites.html','how-to-submit.html','executive-summary.html','SUBMIT.html','submit.html','SUBMIT_NOW.html']:
        text = (ROOT/'docs'/filename).read_text()
        assert 'DO NOT SUBMIT' in text and 'OK TO SUBMIT' not in text
    index = (ROOT/'docs/index.html').read_text()
    assert 'top-K reading' in index and 'not clearance' in index
    assert 'Separate candidate in repository — not cleared' in index
    assert 'gemsdoe92-damagezone-close-dots-20261028-zeros.tif' in index
    readiness = json.loads((ROOT/'docs/downloads/readiness.json').read_text())
    assert readiness['submission_eligible'] is False and readiness['verdict'] == 'negative'
    assert len(readiness['blocking_reasons']) >= 3
    assert any('HOLDOUT-DTI' in reason for reason in readiness['blocking_reasons'])
