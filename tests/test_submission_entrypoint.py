"""A validator exception or local format pass must never imply slot clearance."""
import json
from pathlib import Path

import pytest

import validate_submission as entry
from gems.gates import GateResult
from gems.rasters import sha256_file

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('passing', [True, False])
def test_format_result_never_authorizes_submission(monkeypatch, capsys, passing):
    calls = []
    def gates(*args, **kwargs):
        calls.append((args, kwargs))
        return [GateResult('submission_encoding', passing, 'test')]
    monkeypatch.setattr(entry, 'run_gates', gates)
    assert entry.main(['test.tif']) == 1
    assert calls[0][1]['require_submission_encoding'] is True
    assert len(calls[0][0]) == 3  # candidate, reference, catalogue
    output = capsys.readouterr().out
    assert 'DO NOT SUBMIT' in output
    assert 'READY FOR SUBMISSION' not in output
    assert 'Expected Score' not in output


@pytest.mark.parametrize('error', [OSError('missing'), ValueError('bad raster')])
def test_validation_errors_never_become_success(monkeypatch, capsys, error):
    def fail(*args, **kwargs):
        raise error
    monkeypatch.setattr(entry, 'run_gates', fail)
    assert entry.main(['bad.tif']) == 2
    assert 'DO NOT SUBMIT' in capsys.readouterr().err


def test_superseding_knick_card_has_real_hash_and_no_clearance():
    card = json.loads((ROOT / 'docs/downloads/knickloqo_submission_run_card.json').read_text())
    assert card['submission_eligible'] is False
    assert card['verdict'] == 'negative'
    assert card['raster_sha256'] == sha256_file(ROOT / card['primary_download'])
    assert card['raster_metadata']['shape'] == [3730, 3292]
    assert card['correlation_overlap_vs_registry']['forward_overlap'] == 1.0
    assert card['holdout_dti']['dti'] is None
    assert (ROOT / card['supersedes']['archived_card']).is_file()
