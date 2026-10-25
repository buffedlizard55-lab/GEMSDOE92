"""Current UI status is byte-bound to the VARIO run card and never grants a slot."""
import json

import pytest

from scripts.render_readiness import (
    END, ROOT, START, build_status, panel, rejection_proof_errors, render_page, sync,
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
    card = json.loads((ROOT / 'evidence/vario_run_card.json').read_text())
    assert status['format_pass'] is True          # re-derived from TIFF bytes
    assert status['submission_eligible'] is False  # slot selection is a separate selector step
    assert status['verdict'] == card['verdict'] == 'negative'
    assert status['submission_status'].startswith('DO NOT SUBMIT')
    assert status['download_status'] == 'OK TO DOWNLOAD FOR RESEARCH'
    assert status['holdout_dti']['scores']['vario_full']['dti'] == pytest.approx(0.150020, abs=1e-5)
    assert status['organizer_confirmed_score'] is None
    assert len(status['note']) <= 140
    # disclosure preserved: literal dense reading is reported, operative gate coded
    reg = status['correlation_overlap_vs_registry']
    assert reg['operative_sparse']['passes'] is False
    assert reg['operative_sparse']['worst_overlap']['forward_overlap_within_3px'] > 0.70


def test_renderer_is_idempotent_and_places_block_first():
    block = START + '\n<section>DO NOT SUBMIT</section>\n' + END
    original = '<html><body><main>old</main></body></html>'
    rendered = render_page(original, block)
    assert render_page(rendered, block) == rendered
    polluted = rendered.replace('<body>', '<body><aside>STALE PROMOTION</aside>')
    repaired = render_page(polluted, block)
    assert repaired.index(START) < repaired.index('<aside>') < repaired.index('STALE PROMOTION')
    assert render_page(repaired, block) == repaired


@pytest.mark.parametrize('text', ['<html/>', '<body>' + START + '</body>',
                                      '<body>' + START + END + START + END + '</body>'])
def test_malformed_page_is_rejected(text):
    with pytest.raises(ValueError):
        render_page(text, START + END)


def test_panel_escapes_record_only_fields():
    # a foreign/tampered status is refused outright; the real card renders escaped
    status = json.loads((ROOT / 'docs/downloads/readiness.json').read_text())
    status['note'] = '<script>alert(1)</script>'
    rendered = panel(status)
    assert '<script>' not in rendered
    assert 'ONLY with' in rendered or 'only with' in rendered or 'note' in rendered.lower()
    status['raster_sha256'] = '0' * 64
    with pytest.raises(ValueError):
        panel(status)


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
