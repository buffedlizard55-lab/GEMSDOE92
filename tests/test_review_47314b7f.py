"""Publication must not turn a rejection witness into upload clearance."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_current_clearance_is_fail_closed():
    ready = json.loads((ROOT / 'docs/downloads/readiness.json').read_text())
    card = json.loads((ROOT / 'docs/downloads/review_47314b7f_run_card.json').read_text())
    raster = ROOT / 'docs' / card['file']
    assert ready['submission_eligible'] is card['submission_eligible'] is False
    assert ready['verdict'] == card['verdict'] == 'negative'
    assert hashlib.sha256(raster.read_bytes()).hexdigest() == card['raster_sha256']
    assert raster.stat().st_size == card['actual_bytes']
    assert card['registry']['forward_overlap'] > 0.70
    assert len(card['note']) <= 140
    assert card['experiments'] == card['weekly_slots_used'] == 0


def test_primary_pages_show_stop_before_archive():
    for rel in ['index.html', 'docs/index.html', 'docs/executive-summary.html',
                'docs/how-to-submit.html', 'docs/nine-sites.html']:
        text = (ROOT / rel).read_text()
        assert text.index('Current review: DO NOT SUBMIT') < text.index('<details data-status-archive="true">')
        assert 'review-47314b7f.html' in text
