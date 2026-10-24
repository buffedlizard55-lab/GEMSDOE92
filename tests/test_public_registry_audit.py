"""Regression checks for the public-registry summary; no network required."""
from scripts.audit_public_registry import summarize


def row(overlap=0.0, rho=0.0):
    return dict(submission='witness', my_dots_within_3px_of_theirs=overlap,
                spearman_full_footprint=rho, duplicate_by_rho=abs(rho) > .90)


def test_empty_registry_cannot_clear_uniqueness():
    assert not summarize([])['unique_under_literal_rule']


def test_invalid_registry_cannot_clear_uniqueness():
    assert not summarize([row(), {'error': 'unavailable'}])['unique_under_literal_rule']


def test_overlap_stop_is_strictly_above_threshold():
    assert not summarize([row(.70)])['stop_required']
    assert summarize([row(.700001)])['stop_required']


def test_negative_rank_correlation_also_stops():
    assert summarize([row(rho=-.91)])['stop_required']


def test_dense_witness_is_not_exempt():
    result = summarize([row(1.0, .03)])
    assert result['stop_required']
    assert not result['unique_under_literal_rule']


def test_breakline_stop_receipt_matches_served_bytes_and_current_status():
    import hashlib
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    receipt = json.loads((root / 'evidence/breakline_public_registry_witness17.json').read_text())
    tif = root / 'docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif'
    assert receipt['candidate_file_sha256'] == hashlib.sha256(tif.read_bytes()).hexdigest()
    assert receipt['final_dots']['stop_required']
    assert receipt['witness_only']
    assert not receipt['scan_complete_for_declared_scope']
    assert receipt['preplacement_surface']['status'].startswith('NOT_CHECKED')
    for page in ['index.html', 'SUBMIT.html']:
        html = (root / 'docs' / page).read_text()
        assert 'DO NOT SUBMIT' in html
        assert 'current_status.json' in html
    assert 'BREAKLINE f45Ltop' in (root / 'docs' / 'index.html').read_text()
