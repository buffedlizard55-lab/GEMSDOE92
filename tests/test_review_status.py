"""The review must not turn format validity into competition clearance."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_review_card_preserves_rejection_and_historical_scope():
    card = json.loads((ROOT / 'evidence/review_d97f969e_run_card.json').read_text())
    witness = json.loads((ROOT / 'evidence/review_d97f969e_witness.json').read_text())
    assert card['verdict'] == 'negative'
    assert card['submission_eligible'] is False
    assert card['new_raster_generated'] is False
    assert card['experiments_executed'] == 0
    assert card['raster_sha256'] == witness['candidate']['sha256']
    assert card['registry']['forward_overlap'] > 0.70
    assert card['registry']['stop_required'] is True
    assert 'not rerun' in card['holdout_dti']['status']
    assert card['organizer_confirmed_score'] is None
    assert len(card['submission_note']) <= 140
    for name in ('review_d97f969e_run_card.json', 'review_d97f969e_witness.json'):
        assert (ROOT / 'evidence' / name).read_bytes() == (ROOT / 'docs/downloads' / name).read_bytes()


def test_public_pages_expose_latest_review_before_historical_claims():
    for name in ('index.html', 'executive-summary.html'):
        html = (ROOT / 'docs' / name).read_text()
        notice = html.split('aria-label="Latest verified review">', 1)[1].split('</aside>', 1)[0]
        assert 'DO NOT SUBMIT' in notice
        assert 'not the overall holdout best' in notice
        assert 'not a newly generated submission' in notice
        assert 'REVIEW_D97F969E.md' in notice
        assert 'review_d97f969e_witness.json' in notice
