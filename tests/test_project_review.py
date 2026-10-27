"""One-command review is engineering evidence, never a submission selector."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import sys

import pytest

from scripts import review_project as review

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def stop_card():
    return json.loads((ROOT / 'evidence/review_e7bc063a_preflight.json').read_text())


def install_audit(monkeypatch, stop_card):
    monkeypatch.setattr(review, 'audit', lambda *_: copy.deepcopy(stop_card))


def test_check_plan_is_only_engineering_and_shared_validators():
    plan = review.checks(sys.executable)
    assert len({name for name, _ in plan}) == len(plan) == 9
    assert plan[0][1] == [sys.executable, '-m', 'pytest', 'tests', '-q']
    # Include staged changes too; plain `git diff --check` misses them.
    assert plan[-1][1] == ['git', 'diff', '--check', 'HEAD', '--']
    assert all('--check' in argv for name, argv in plan if name.startswith('review_'))
    assert not any('build_' in arg or 'run_salem' in arg for _, argv in plan for arg in argv)
    assert not any('drivendata.org' in arg for _, argv in plan for arg in argv)


@pytest.mark.parametrize('fail_index', [None, 0, 3, 8])
def test_engineering_pass_or_failure_never_grants_clearance(monkeypatch, stop_card, fail_index):
    install_audit(monkeypatch, stop_card)
    calls = []
    def fake(name, argv, root, timeout):
        calls.append(name)
        return {'name': name, 'passed': len(calls) - 1 != fail_index}
    monkeypatch.setattr(review, 'run_check', fake)
    card = review.review(ROOT, Path('witness'), sys.executable)
    assert card['engineering_checks_complete'] is True
    assert card['engineering_checks_passed'] is (fail_index is None)
    assert card['submission_eligible'] is False and card['verdict'] == 'negative'
    assert card['raster_sha256'] is None and card['submission_name'] is None
    assert card['validator_output']['status'] == 'not_run'
    assert card['holdout_dti']['value'] is None
    assert card['weekly_slots_used'] == card['experiments'] == 0
    assert card['score_estimate'] is None
    assert card['official_sources_live_verified'] is False
    old = card['historical_research_reference']
    assert old['raster_sha256'] == stop_card['raster_sha256']
    assert old['format_pass'] is True
    assert old['validator_output'] == stop_card['validator_output']
    assert len(card['note']) <= 140


def test_expired_budget_cannot_be_called_complete(monkeypatch, stop_card):
    install_audit(monkeypatch, stop_card)
    monkeypatch.setattr(review, 'run_check', lambda *_a, **_k: pytest.fail('out of budget'))
    card = review.review(ROOT, Path('witness'), sys.executable, budget_seconds=0)
    assert card['engineering_checks'] == []
    assert not card['engineering_checks_complete']
    assert not card['engineering_checks_passed']
    assert card['submission_eligible'] is False


@pytest.mark.parametrize('field,value', [
    ('submission_eligible', 'false'), ('submission_eligible', True),
    ('experiments', False), ('weekly_slots_used', False),
    ('new_unique_tiff_generated', 0), ('verdict', 'promote'),
])
def test_changed_audit_semantics_rejected(stop_card, field, value):
    stop_card[field] = value
    with pytest.raises(ValueError, match='semantics'):
        review.validate_stop(stop_card)


def test_changed_universal_witness_proof_rejected(stop_card):
    stop_card['correlation_overlap_vs_registry']['preplacement_proof']['positive_in_footprint'] -= 1
    with pytest.raises(ValueError, match='positive_in_footprint'):
        review.validate_stop(stop_card)


def test_run_check_records_real_failure_and_hashes(tmp_path):
    row = review.run_check('fail', [sys.executable, '-c',
                           'import sys; print("diagnostic"); sys.exit(7)'], tmp_path)
    assert row['returncode'] == 7 and row['passed'] is False
    assert row['stdout_tail'] == 'diagnostic\n'
    assert row['stdout_sha256'] == review.sha256(b'diagnostic\n')
    assert not row['timed_out']


def test_run_check_missing_executable_is_failure(tmp_path):
    row = review.run_check('missing', [str(tmp_path / 'missing')], tmp_path)
    assert row['returncode'] is None and row['passed'] is False
    assert row['stderr_tail']


def test_timeout_is_failure_and_kills_process_group(tmp_path):
    row = review.run_check('timeout', [sys.executable, '-c',
                           'import time; time.sleep(10)'], tmp_path, timeout=0.05)
    assert row['timed_out'] and not row['passed']
    assert row['returncode'] != 0


def test_atomic_receipt_never_replaces_existing_or_dangling_link(tmp_path):
    path = tmp_path / 'receipt.json'
    review.write_receipt(path, {'verdict': 'negative'})
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        review.write_receipt(path, {'verdict': 'promote'})
    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]
    path.unlink()
    path.symlink_to(tmp_path / 'missing')
    with pytest.raises(FileExistsError):
        review.write_receipt(path, {'verdict': 'negative'})
    assert path.is_symlink() and not path.exists()
    assert len(list(tmp_path.iterdir())) == 1


def test_receipt_rejects_nonfinite_json_without_leaving_file(tmp_path):
    path = tmp_path / 'receipt.json'
    with pytest.raises(ValueError):
        review.write_receipt(path, {'number': float('nan')})
    assert not os.path.lexists(path)


@pytest.mark.parametrize('passed,expected', [(True, 1), (False, 2)])
def test_cli_only_exits_stop_or_inconclusive(tmp_path, monkeypatch, capsys, passed, expected):
    monkeypatch.setattr(review, 'review', lambda *_: {
        'engineering_checks_passed': passed, 'submission_eligible': False})
    output = tmp_path / 'receipt.json'
    assert review.main(['--output', str(output)]) == expected
    assert 'DO NOT SUBMIT' in capsys.readouterr().out
    assert json.loads(output.read_text())['submission_eligible'] is False


def test_cli_preserves_existing_evidence(tmp_path, monkeypatch):
    output = tmp_path / 'receipt.json'
    output.write_text('historical')
    monkeypatch.setattr(review, 'review', lambda *_: pytest.fail('must not run'))
    assert review.main(['--output', str(output)]) == 2
    assert output.read_text() == 'historical'


def test_cli_refuses_fetch_outside_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(review, 'fetch_witness', lambda *_: pytest.fail('must not fetch'))
    assert review.main(['--output', str(tmp_path / 'receipt.json'), '--fetch-witness',
                        '--witness', str(tmp_path / 'download.tif')]) == 2


def test_cli_proof_failure_never_emits_success_receipt(tmp_path, monkeypatch):
    def fail(*_):
        raise ValueError('proof unavailable')
    monkeypatch.setattr(review, 'review', fail)
    output = tmp_path / 'receipt.json'
    assert review.main(['--output', str(output)]) == 2
    assert not output.exists()
