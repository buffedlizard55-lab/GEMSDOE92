"""Regression tests for fail-closed public registry audit orchestration."""
from scripts.audit_public_registry import fetch_blob, summarize


def test_empty_and_failed_comparisons_are_not_clearance():
    assert not summarize([])['unique_under_literal_rule']
    assert not summarize([{'error': 'bad grid'}])['unique_under_literal_rule']
    assert not summarize([{'my_dots_within_3px_of_theirs': 0.1},
                          {'error': 'unreadable'}])['unique_under_literal_rule']


def test_literal_duplicate_thresholds():
    assert not summarize([{'submission': 'dense', 'my_dots_within_3px_of_theirs': 1.0}])['unique_under_literal_rule']
    assert summarize([{'submission': 'edge', 'my_dots_within_3px_of_theirs': .70}])['unique_under_literal_rule']
    assert summarize([{'submission': 'negative rho', 'spearman_full_footprint': -.95,
                       'duplicate_by_rho': True}])['stop_required']


def test_cache_only_never_downloads_missing_blob(tmp_path, monkeypatch):
    import scripts.audit_public_registry as audit
    monkeypatch.setattr(audit, 'CACHE', tmp_path)
    def no_network(*args, **kwargs):
        raise AssertionError('network called in cache-only mode')
    monkeypatch.setattr(audit, 'gh_bytes', no_network)
    result = fetch_blob({'git_sha': 'absent', 'bytes': 5}, cache_only=True)
    assert 'blob absent in cache-only mode' in result['error']


def test_both_phases_and_scan_completeness_are_binding():
    from scripts.audit_public_registry import audit_verdict
    clear = {'rows': [{'submission': 'r', 'my_dots_within_3px_of_theirs': .2}],
             'complete_accessible_scan': True, 'unique': True}
    duplicate = {**clear, 'rows': [{'submission': 'r', 'my_dots_within_3px_of_theirs': 1.0}], 'unique': False}
    assert 'duplicate' in audit_verdict(duplicate, clear, True)
    assert 'duplicate' in audit_verdict(clear, duplicate, False)
    assert 'incomplete' in audit_verdict(clear, clear, False)
    assert 'incomplete' in audit_verdict(clear, {**clear, 'unique': False}, True)
    assert audit_verdict(clear, clear, True).startswith('selector-review-only')
