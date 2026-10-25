"""A parallel merge cannot turn format validity into slot authorization."""
import hashlib
import json
from pathlib import Path

from gems.gates import GateResult
import validate_submission

ROOT = Path(__file__).resolve().parents[1]


def test_compatibility_validator_never_grants_slot(monkeypatch, capsys):
    monkeypatch.setattr(validate_submission, 'run_gates', lambda *a, **k: [
        GateResult('format', True, 'synthetic unit check')])
    assert validate_submission.main([]) == 1
    output = capsys.readouterr().out
    assert 'FORMAT PASS (local only)' in output
    assert 'DO NOT SUBMIT' in output
    assert 'Expected Score' not in output


def test_inherited_clearance_card_is_corrected_and_negative():
    card = json.loads((ROOT / 'docs/downloads/knickloqo_submission_run_card.json').read_text())
    assert card['submission_eligible'] is False
    assert card['verdict'] == 'negative'
    raster = ROOT / card['primary_download']
    assert card['raster_sha256'] == hashlib.sha256(raster.read_bytes()).hexdigest()
    assert card['raster_metadata']['shape'] == [3730, 3292]
    assert (ROOT / card['supersedes']['archived_card']).is_file()
