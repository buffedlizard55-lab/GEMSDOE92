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
    assert 'FORMAT-VALIDATION: PASS' in output
    assert 'DO NOT SUBMIT' in output
    assert 'Expected Score' not in output


def test_inherited_clearance_card_is_corrected_and_negative():
    card = json.loads((ROOT / 'docs/downloads/knickloqo_submission_run_card.json').read_text())
    assert card['submission_eligibility']['submission_eligible'] is False
    assert card['submission_eligibility']['verdict'] == 'negative'
    meta = card['submission_metadata']
    raster = ROOT / 'docs/downloads' / meta['file_name']
    assert meta['sha256_tif'] == hashlib.sha256(raster.read_bytes()).hexdigest()
    assert meta['file_size_bytes'] == raster.stat().st_size
    assert card['format_validation']['shape'] == [3730, 3292]
    assert card['review_correction']['original_commit']
