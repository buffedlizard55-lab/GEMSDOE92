"""No representation diagnostic may authorize bypassing the user's literal gate."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from gems57.uniqueness import dual_reading_decision

ROOT = Path(__file__).resolve().parents[1]


def row(**overrides):
    return {"file": "witness", "representation": "continuous_surface",
            "literal_forward_overlap": 1.0, "matched_budget_forward_overlap": 0.1,
            "spearman_surface": 0.2, **overrides}


def test_dense_witness_is_binding_even_when_matched_budget_is_low():
    d = dual_reading_decision([row()])
    assert d['duplicate'] is True and d['stop_required'] is True
    assert d['verdict'] == 'negative' and d['submission_eligible'] is False
    assert d['worst_matched_budget_forward_overlap'] == 0.1
    assert 'diagnostic only' in d['operative_rule']


def test_errors_cannot_disappear_into_a_unique_verdict():
    d = dual_reading_decision([row(literal_forward_overlap=0.1), {'error': 'unreadable'}])
    assert not d['duplicate']  # incompleteness is not a measured duplicate
    assert d['missing_or_invalid'] == 1
    assert d['stop_required'] and d['verdict'] == 'negative'


@pytest.mark.parametrize('rows', [[], [{'error': 'missing'}], [None], ['PASS']])
def test_no_valid_rows_cannot_pass(rows):
    with pytest.raises(ValueError):
        dual_reading_decision(rows)


@pytest.mark.parametrize('field', ['literal_forward_overlap', 'matched_budget_forward_overlap',
                                    'spearman_surface'])
@pytest.mark.parametrize('value', [float('nan'), float('inf'), '0.1', True, [], {}])
def test_malformed_numbers_fail_closed(field, value):
    with pytest.raises(ValueError):
        dual_reading_decision([row(**{field: value})])


@pytest.mark.parametrize('field', ['literal_forward_overlap', 'matched_budget_forward_overlap',
                                    'spearman_surface'])
def test_missing_measurements_fail_closed(field):
    r = row()
    r.pop(field)
    with pytest.raises(ValueError):
        dual_reading_decision([r])


@pytest.mark.parametrize('rho', [-0.91, 0.91])
def test_rank_gate_is_binding_in_both_directions(rho):
    assert dual_reading_decision([row(literal_forward_overlap=0.1,
                                    spearman_surface=rho)])['duplicate']


def test_threshold_is_strict_and_unique_is_not_submission_permission():
    d = dual_reading_decision([row(literal_forward_overlap=0.7,
                                  matched_budget_forward_overlap=0.7, spearman_surface=-0.9)])
    assert d['duplicate'] is False and d['verdict'] == 'unique'
    assert d['submission_eligible'] is False


@pytest.mark.parametrize('limit', [float('nan'), float('inf'), -0.1, 1.1, True, '0.7'])
def test_invalid_threshold_cannot_disable_gate(limit):
    with pytest.raises(ValueError):
        dual_reading_decision([row()], overlap_limit=limit)


def test_renderer_cannot_reinstate_old_matched_budget_clearance(tmp_path):
    (tmp_path / 'scripts').mkdir()
    (tmp_path / 'evidence').mkdir()
    (tmp_path / 'docs').mkdir()
    script = tmp_path / 'scripts/render_blindfault_site.py'
    shutil.copy(ROOT / 'scripts/render_blindfault_site.py', script)
    card = json.loads((ROOT / 'evidence/blindfault_run_card.json').read_text())
    # Simulate a stale matched-budget promotion. The literal witness must win.
    card['submission_eligible'] = True
    card['verdict'] = 'promote'
    card['correlation_overlap_vs_registry']['public']['worst_literal_forward_overlap'] = 1.0
    (tmp_path / 'evidence/blindfault_run_card.json').write_text(json.dumps(card))
    shutil.copy(ROOT / 'evidence/blindfault_holdout.json', tmp_path / 'evidence')
    (tmp_path / 'README.md').write_text('# Fixture\n')
    pages = [tmp_path / 'docs' / name for name in ('index.html', 'executive-summary.html', 'SUBMIT.html')]
    for page in pages:
        page.write_text('<html><body></body></html>')
    subprocess.run([sys.executable, str(script)], check=True, capture_output=True)
    first = [(p.read_bytes()) for p in pages]
    subprocess.run([sys.executable, str(script)], check=True, capture_output=True)
    for page, original in zip(pages, first):
        assert page.read_bytes() == original
        text = page.read_text()
        assert 'DO NOT SUBMIT — literal registry duplicate stop' in text
        assert 'OK TO SUBMIT' not in text
        assert 'new unique TIFF generated' not in text


@pytest.mark.parametrize('field,value', [
    ('literal_forward_overlap', -0.1), ('literal_forward_overlap', 1.1),
    ('matched_budget_forward_overlap', -0.1), ('matched_budget_forward_overlap', 1.1),
    ('spearman_surface', -1.1), ('spearman_surface', 1.1),
])
def test_out_of_range_measurements_fail_closed(field, value):
    with pytest.raises(ValueError):
        dual_reading_decision([row(**{field: value})])


def test_review_receipts_are_exact_file_rejection_not_new_submission():
    import hashlib
    card = json.loads((ROOT / 'evidence/review376a_run_card.json').read_text())
    witness = json.loads((ROOT / 'evidence/review376a_primary_witness.json').read_text())
    assert card['raster_sha256'] == witness['candidate']['sha256']
    assert hashlib.sha256((ROOT / card['primary_download']).read_bytes()).hexdigest() == card['raster_sha256']
    assert card['verdict'] == 'negative' and card['submission_eligible'] is False
    assert card['new_unique_tiff_generated'] is False
    assert card['experiments_executed'] == card['weekly_slots_used'] == 0
    assert card['holdout_dti']['dti'] is None and card['organizer_confirmed_score'] is None
    assert card['validator_output']['crs_shape_transform_match'] is True
    assert card['validator_output']['all_must_gates_pass'] is True
    assert all(g['ok'] is True for g in card['validator_output']['gates'])
    assert len(card['note']) <= 140
    for src in (ROOT / 'evidence').glob('review376a_*.json'):
        assert src.read_bytes() == (ROOT / 'docs/downloads' / src.name).read_bytes()
