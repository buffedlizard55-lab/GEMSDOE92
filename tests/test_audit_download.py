"""Audit prose must agree with measured gate failures."""
import json
import sys

import pytest
from scripts import audit_download


@pytest.mark.parametrize('passed', [True, False])
def test_audit_note_tracks_result(tmp_path, monkeypatch, passed):
    zeros = tmp_path / 'test-zeros.tif'
    legacy = tmp_path / 'test.tif'
    monkeypatch.setattr(sys, 'argv', ['audit_download', str(zeros), str(legacy)])
    monkeypatch.setattr(audit_download, 'gates', lambda *a, **k: [
        {'name': 'values_in_0_1', 'ok': passed, 'detail': 'synthetic test'}])
    monkeypatch.setattr(audit_download, 'sha256_file', lambda _: '0' * 64)
    assert audit_download.main() == (0 if passed else 1)
    receipt = json.loads((tmp_path / 'test-audit.json').read_text())
    assert receipt['overall_pass'] is passed
    assert ('All gates PASS' in receipt['note']) is passed
    if not passed:
        assert 'do not submit' in receipt['note']
