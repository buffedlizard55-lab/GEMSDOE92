"""The current review is a rejection, not another renamed submission."""
import hashlib
import json
from pathlib import Path

import numpy as np

from gems57.metric import dti_exact

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / 'evidence' / name).read_text())


def test_current_review_receipts_are_mirrored_and_consistent():
    for src in (ROOT / 'evidence').glob('review_918b947a_*.json'):
        assert src.read_bytes() == (ROOT / 'docs/downloads' / src.name).read_bytes()
    card = load('review_918b947a_run_card.json')
    witness = load('review_918b947a_primary_witness.json')
    proof = load('review_918b947a_preplacement.json')
    assert card['new_unique_tiff_generated'] is False
    assert card['experiments_executed'] == card['weekly_slots_used'] == 0
    assert card['verdict'] == 'negative'
    assert card['submission_eligible'] is False
    assert card['organizer_confirmed_score'] is None
    assert card['holdout_dti']['new_candidate_dti'] is None
    assert 'not rerun' in card['holdout_dti']['status']
    assert len(card['note']) <= 140
    assert card['raster_sha256'] == witness['candidate']['sha256']
    assert hashlib.sha256((ROOT / card['primary_download']).read_bytes()).hexdigest() == card['raster_sha256']
    assert proof['universal_nonempty_in_footprint_overlap_stop'] is True
    assert proof['positive_in_footprint'] == proof['footprint_pixels']
    assert card['correlation_overlap_vs_registry']['forward_overlap_within_3px'] == 1
    assert all(g['ok'] is True for g in card['validator_output']['gates'])


def test_latest_notice_is_first_and_historical_claims_are_scoped():
    for name in ('index.html', 'executive-summary.html'):
        text = (ROOT / 'docs' / name).read_text()
        notice = text.split('aria-label="Latest verified review">', 1)[1].split('</aside>', 1)[0]
        assert notice.index('session 918b947a') < notice.index('Historical artifact')
        assert 'No new unique TIFF was generated' in notice
        assert 'not rerun' in notice
        assert 'review_918b947a_run_card.json' in notice
        assert 'Newly built this session' not in text
        assert '#1 All-Time Repo High' not in text
        assert "repository's highest" not in text


def test_nearby_dots_can_increase_dti_counterexample():
    """Sub-2.8px separation does not imply zero marginal truth credit."""
    truth = np.zeros((9, 9), bool)
    truth[4, 2] = truth[4, 4] = True
    prediction = np.zeros((9, 9), float)
    prediction[4, 2] = 1
    before = dti_exact(prediction, truth)
    prediction[4, 4] = 1  # 2px from first dot, but adds actual truth credit
    after = dti_exact(prediction, truth)
    assert after['tp'] > before['tp']
    assert after['dti'] > before['dti']
    assert after['fp'] == 0  # not a full per-dot false-positive penalty
