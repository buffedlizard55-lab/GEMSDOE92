"""Current UI status cannot be overridden by stale historical summaries."""
import json

import pytest

from scripts.render_readiness import (
    ARCHIVE_START, END, ROOT, START, build_status, panel, rejection_proof_errors, render_page, sync,
    validate_current_submission_record,
)
from scripts.preflight_dense_witness import SAMPLE_SHA256


def test_recorded_universal_stop_is_consistent():
    proof = json.loads((ROOT / 'evidence/review_f23_preflight.json').read_text())
    assert not rejection_proof_errors(proof, SAMPLE_SHA256)


@pytest.mark.parametrize('key,value', [
    ('sha256', '0' * 64), ('submission_eligible', True), ('grid_checks_pass', 'true'),
    ('threshold', 0.8), ('positive_in_footprint', 1), ('verdict', 'unique'),
    ('forward_overlap_for_any_nonempty_in_footprint_dot_set', True),
])
def test_malformed_or_reinterpreted_rejection_proof_fails(key, value):
    proof = json.loads((ROOT / 'evidence/review_f23_preflight.json').read_text())
    proof[key] = value
    assert rejection_proof_errors(proof, SAMPLE_SHA256)


def test_changed_sample_invalidates_proof():
    proof = json.loads((ROOT / 'evidence/review_f23_preflight.json').read_text())
    assert rejection_proof_errors(proof, '0' * 64)


def test_generated_status_is_current_and_never_grants_slot():
    assert sync(check=True) == []
    status = build_status()
    assert status['format_pass'] is True
    assert status['submission_eligible'] is False
    assert status['candidate_artifact_exists'] is True
    assert status['candidate_byte_distinct_from_pinned_parent'] is True
    assert status['candidate_registry_unique_under_literal_rule'] is False
    assert 'new_unique_tiff_generated' not in status
    assert status['correlation_overlap_vs_registry']['evidence_class'] == 'REGISTRY-MEASUREMENT'
    assert status['correlation_overlap_vs_registry']['forward_overlap'] == 1.0
    assert status['correlation_overlap_vs_registry']['threshold'] == 0.70
    assert status['holdout_dti']['evidence_class'] == 'HOLDOUT-DTI'
    assert status['holdout_dti']['evaluator_version'] == 'gems57-pooled-hide-v2'
    assert status['holdout_dti']['withheld_positive_pixels'] == 22663
    assert status['organizer_confirmed_score'] is None
    assert len(status['note']) <= 140
    rendered = panel(status)
    assert 'OK TO DOWNLOAD FOR RESEARCH' in rendered
    assert 'DO NOT SUBMIT' in rendered
    assert 'not registry-unique' in rendered
    assert 'Unique research TIFF available' not in rendered
    assert 'Download research-only' in rendered


def test_compact_current_card_must_match_the_byte_bound_readiness_record():
    status = build_status()
    current = json.loads((ROOT / 'docs/downloads/current_submission.json').read_text())
    validate_current_submission_record(
        current,
        file='docs/' + status['file'],
        sha256=status['raster_sha256'],
        lane=status['lane'],
        arm=status['arm'],
        submission_name=status['submission_name'],
        note=status['note'],
    )
    current['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='sha256'):
        validate_current_submission_record(
            current,
            file='docs/' + status['file'],
            sha256=status['raster_sha256'],
            lane=status['lane'],
            arm=status['arm'],
            submission_name=status['submission_name'],
            note=status['note'],
        )


def test_renderer_is_idempotent_and_moves_stale_banner_into_archive():
    block = START + '\n<section>DO NOT SUBMIT</section>\n' + END
    original = '<html><body><main>old</main></body></html>'
    rendered = render_page(original, block)
    assert render_page(rendered, block) == rendered
    polluted = rendered.replace('<body>', '<body><aside>STALE PROMOTION</aside>')
    repaired = render_page(polluted, block)
    assert repaired.index(START) < repaired.index(ARCHIVE_START) < repaired.index('STALE PROMOTION')
    assert render_page(repaired, block) == repaired


@pytest.mark.parametrize('text', ['<html/>', '<body>' + START + '</body>',
                                      '<body>' + START + END + START + END + '</body>'])
def test_malformed_page_is_rejected(text):
    with pytest.raises(ValueError):
        render_page(text, START + END)


def test_panel_escapes_record_only_fields():
    status = json.loads((ROOT / 'docs/downloads/readiness.json').read_text())
    status['note'] = '<script>alert(1)</script>'
    rendered = panel(status)
    assert '<script>' not in rendered
    assert '&lt;script&gt;' in rendered


def test_note_schema_aliases_are_checked_not_guessed():
    from scripts.render_readiness import form_note
    assert form_note({'note': 'research'}) == 'research'
    assert form_note({'submission_note': 'research'}) == 'research'
    assert form_note({'note': 'research', 'submission_note': 'research'}) == 'research'
    for invalid in ({}, {'note': 'x' * 141}, {'note': None},
                    {'note': 'one', 'submission_note': 'two'}):
        with pytest.raises(ValueError):
            form_note(invalid)


def test_withdrawn_clearance_matches_disk_not_placeholder_metadata():
    import rasterio
    from gems.rasters import sha256_file
    receipt = json.loads((ROOT / 'docs/downloads/knickloqo_submission_run_card.json').read_text())
    path = ROOT / 'docs/downloads' / receipt['file']
    assert receipt['raster_sha256'] == sha256_file(path)
    assert receipt['metadata_measured_from_disk']['bytes'] == path.stat().st_size
    with rasterio.open(path) as ds:
        assert receipt['metadata_measured_from_disk']['shape'] == list(ds.shape)
        assert receipt['metadata_measured_from_disk']['transform'] == list(ds.transform)[:6]
        assert receipt['metadata_measured_from_disk']['nodata'] == ds.nodata
    assert receipt['submission_eligible'] is False
    assert receipt['verdict'] == 'negative'
    assert receipt['organizer_confirmed_score'] is None


# Legacy CLI regression coverage lives in test_submission_entrypoint.py.
