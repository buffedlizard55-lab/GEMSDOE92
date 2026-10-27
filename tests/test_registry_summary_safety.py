"""Shared registry summaries may reject, but must never manufacture clearance."""
from __future__ import annotations

import hashlib

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from gems57 import uniqueness as u


def row(overlap=0.1, rho=0.0, **overrides):
    return {
        'submission': 'fixture',
        'my_dots_within_3px_of_theirs': overlap,
        'spearman_full_footprint': rho,
        'rank_exact': True,
        'jaccard_dot_sets': 0.0,
        'duplicate_by_overlap': False,
        'duplicate_by_rho': False,
        'identical_bytes': False,
        'identical_decoded_predictions': False,
        **overrides,
    }


def summary(rows, *, expected=None, complete=True, errors=None):
    return u.summarize_registry_rows(
        rows, registry_rasters_expected=len(rows) if expected is None else expected,
        complete_accessible_scan=complete, source_errors=errors or [],
        candidate_meta={'my_dots': 1, 'candidate_rank_variation': True}, scope='test only')


def test_empty_inventory_never_promotes():
    result = summary([])
    assert result['unique'] is False
    assert result['stop_required'] is True
    assert result['verdict'] == 'negative'
    assert result['complete_accessible_scan'] is False
    with pytest.raises(ValueError, match='nonempty'):
        u.binding_duplicate_decision([])


@pytest.mark.parametrize('value', [1.0, 0.700001])
def test_measured_overlap_overrides_a_false_caller_flag(value):
    result = summary([row(overlap=value, duplicate_by_overlap=False)])
    assert result['duplicate_count'] == 1
    assert result['stop_required'] and not result['unique']


@pytest.mark.parametrize('rho', [-0.91, 0.91])
def test_measured_rank_overrides_a_false_caller_flag(rho):
    result = summary([row(rho=rho, duplicate_by_rho=False)])
    assert result['duplicate_count'] == 1
    assert result['stop_required'] and not result['unique']


@pytest.mark.parametrize('rank_exact', [False, None, 'true'])
def test_sampled_or_unattested_rank_never_clears(rank_exact):
    if rank_exact == 'true':
        with pytest.raises(ValueError, match='invalid registry boolean'):
            summary([row(rank_exact=rank_exact)])
    elif rank_exact is None:
        incomplete = row()
        incomplete.pop('rank_exact')
        result = summary([incomplete])
        assert result['registry_inventory_complete'] and not result['full_grid_rank_complete']
        assert not result['unique'] and result['stop_required']
    else:
        result = summary([row(rank_exact=rank_exact)])
        assert result['registry_inventory_complete'] and not result['full_grid_rank_complete']
        assert not result['unique'] and result['stop_required']


def test_worst_rank_uses_absolute_value():
    result = summary([row(rho=-0.99, submission='negative'),
                      row(rho=0.70, submission='positive')])
    assert result['worst_rho_submission'] == 'negative'
    assert result['worst_spearman_full_footprint'] == -0.99
    assert result['worst_abs_spearman_full_footprint'] == 0.99


@pytest.mark.parametrize('complete', [False, 'false', 'true', 1, None])
def test_only_literal_true_can_claim_completeness(complete):
    assert not summary([row()], complete=complete)['unique']


def test_error_count_and_missing_sources_stop():
    assert not summary([row(), {'error': 'unreadable'}])['unique']
    assert not summary([row()], errors=['source unavailable'])['unique']
    assert not summary([row()], expected=2)['unique']
    d = u.binding_duplicate_decision([row(), {'error': 'unreadable'}])
    assert d['missing_or_invalid'] == 1 and d['stop_required']
    assert d['verdict'] == 'negative' and not d['submission_eligible']


@pytest.mark.parametrize('key,value', [
    ('my_dots_within_3px_of_theirs', np.nan),
    ('my_dots_within_3px_of_theirs', -0.1),
    ('my_dots_within_3px_of_theirs', True),
    ('spearman_full_footprint', np.inf),
    ('spearman_full_footprint', -1.1),
    ('duplicate_by_overlap', 'false'),
])
def test_malformed_rows_cannot_clear(key, value):
    bad = row(**{key: value})
    with pytest.raises(ValueError):
        summary([bad])
    if key != 'duplicate_by_overlap':
        with pytest.raises(ValueError):
            u.binding_duplicate_decision([bad])


def test_strict_threshold_and_single_row_is_diagnostic_only():
    r = row(overlap=0.70, rho=-0.90)
    assert summary([r])['unique']
    d = u.binding_duplicate_decision([r])
    assert not d['stop_required'] and d['verdict'] == 'diagnostic-clear-only'
    assert not d['submission_eligible']


def test_two_phase_summary_honors_negative_rank_and_errors():
    r = row(rho=-0.95, their_dots=1, their_dots_within_3px_of_mine=0.0)
    out = u.two_phase_summary([r, {'error': 'missing'}], footprint_cells=100)
    assert out['literal_reading']['duplicate']
    assert out['literal_reading']['rho_firings'] == 1
    assert out['stop_required'] and out['missing_or_invalid'] == 1
    assert out['submission_eligible'] is False


def test_incremental_merge_requires_exact_identity_and_literal_completeness():
    def audit(digest):
        return {
            'candidate_file_sha256': 'a' * 64, 'candidate_decoded_sha256': 'b' * 64,
            'my_dots': 1, 'candidate_rank_variation': True,
            'rho_limit': u.RHO_LIMIT, 'overlap_limit': u.OVERLAP_LIMIT,
            'jaccard_limit': u.JACCARD_LIMIT, 'complete_accessible_scan': True,
            'missing_or_invalid': 0, 'source_errors': [],
            'rows': [row(sha256=digest, sources=['fixture'])],
            'registry_rasters_checked': 1,
        }
    base, ext = audit('c' * 64), audit('d' * 64)
    assert u.merge_registry_audits(base, ext, registry_rasters_expected=2)['unique']
    assert not u.merge_registry_audits(base, ext, registry_rasters_expected=2,
                                      complete_accessible_scan='false')['unique']
    base['candidate_file_sha256'] = ext['candidate_file_sha256'] = None
    with pytest.raises(ValueError, match='valid candidate'):
        u.merge_registry_audits(base, ext, registry_rasters_expected=2)
    base['candidate_file_sha256'] = ext['candidate_file_sha256'] = 'a' * 64
    base['complete_accessible_scan'] = 'true'
    with pytest.raises(ValueError, match='base audit'):
        u.merge_registry_audits(base, ext, registry_rasters_expected=2)


def test_inventory_boolean_and_pins_are_binding(tmp_path):
    p = tmp_path / 'prior.tif'
    with rasterio.open(p, 'w', driver='GTiff', height=4, width=4, count=1,
                       dtype='float32', crs='EPSG:32611',
                       transform=from_origin(1, 1, 100, 100)) as dst:
        a = np.zeros((4, 4), dtype=np.float32)
        a[3, 3] = 1
        dst.write(a, 1)
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    rec = {'repo_first': 'owner/repo', 'sources': ['prior'],
           'cache_file': str(p), 'sha256': digest}
    mine = np.zeros((4, 4), dtype=np.float32)
    mine[0, 0] = 1
    index = {'rasters': [rec], 'complete_accessible_scan': 'true', 'errors': []}
    result = u.compare_array_to_registry(mine, index, np.ones((4, 4), bool))
    assert not result['unique'] and not result['complete_accessible_scan']
    index['complete_accessible_scan'] = True
    rec['sha256'] = ''
    result = u.compare_array_to_registry(mine, index, np.ones((4, 4), bool))
    assert not result['unique'] and result['missing_or_invalid'] == 1
    assert 'pin' in result['rows'][0]['error']


def test_float64_out_of_range_cannot_round_into_validity():
    mine = np.zeros((4, 4), dtype=np.float64)
    mine[1, 1] = 1.0 + 1e-10  # rounds to 1.0 as float32
    with pytest.raises(ValueError, match=r'finite in \[0,1\]'):
        u.compare_array_to_registry(mine, [], np.ones((4, 4), bool))


def test_nonfinite_registry_inside_footprint_fails_closed(tmp_path):
    p = tmp_path / 'prior.tif'
    prior = np.zeros((4, 4), dtype=np.float32)
    prior[2, 2] = np.nan
    with rasterio.open(p, 'w', driver='GTiff', height=4, width=4, count=1,
                       dtype='float32', crs='EPSG:32611',
                       transform=from_origin(1, 1, 100, 100)) as dst:
        dst.write(prior, 1)
    record = {'repo_first': 'owner/repo', 'sources': ['prior'],
              'cache_file': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
    index = {'rasters': [record], 'complete_accessible_scan': True, 'errors': []}
    mine = np.zeros((4, 4), dtype=np.float32)
    mine[0, 0] = 1
    result = u.compare_array_to_registry(mine, index, np.ones((4, 4), bool))
    assert not result['unique'] and result['missing_or_invalid'] == 1
    assert 'nonfinite' in result['rows'][0]['error']


def test_disk_candidate_grid_is_checked_before_comparison(tmp_path):
    p = tmp_path / 'candidate.tif'
    with rasterio.open(p, 'w', driver='GTiff', height=4, width=4, count=1,
                       dtype='float32', crs='EPSG:4326',
                       transform=from_origin(1, 1, 100, 100)) as dst:
        dst.write(np.ones((4, 4), dtype=np.float32), 1)
    from rasterio.crs import CRS
    expected = ((4, 4), CRS.from_epsg(32611), from_origin(1, 1, 100, 100))
    with pytest.raises(ValueError, match='candidate CRS/shape/transform'):
        u.compare_to_registry(p, [], np.ones((4, 4), bool), expected_grid=expected)
