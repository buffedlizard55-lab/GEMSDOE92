"""The merged repository review must not impersonate a concurrent experiment.

The review card is a time-stamped negative snapshot; if the public primary
changes later it remains historical rather than silently claiming clearance.
"""
from __future__ import annotations

import json
from pathlib import Path

from gems.rasters import sha256_file
from scripts.render_readiness import build_status

ROOT = Path(__file__).resolve().parents[1]


def test_final_review_card_is_mirrored_and_cannot_claim_a_new_submission():
    source = ROOT / 'evidence/session_78db3076_final.json'
    published = ROOT / 'docs/downloads/session_78db3076_run_card.json'
    assert source.read_bytes() == published.read_bytes()
    card = json.loads(source.read_text())
    assert card['verdict'] == 'negative' and card['submission_eligible'] is False
    assert card['new_unique_tiff_generated'] is False
    assert card['experiments_this_review'] == card['experiments'] == card['weekly_slots_used'] == 0
    assert card['concurrent_lane_new_tiff_generated'] is True
    assert card['concurrent_vario_experiments'] == 3
    assert card['organizer_confirmed_score'] is None
    assert card['holdout_dti']['value'] is None
    assert card['concurrent_lane_holdout_dti']['evidence_class'] == 'HOLDOUT-DTI'
    assert card['correlation_overlap_vs_registry']['forward_overlap_for_any_nonempty_in_footprint_candidate'] == 1.0
    assert card['concurrent_lane_sparse_registry_worst_overlap'] > 0.70
    assert card['format_pass'] is True and 0 < len(card['note']) <= 140
    assert sha256_file(ROOT / card['primary_download']) == card['raster_sha256']
    quarantined = card['quarantined_invalid_download']
    assert quarantined['removed_from_served_files'] is True
    assert not (ROOT / quarantined['previous_path']).exists()
    archive_receipt = json.loads((ROOT / 'evidence/listric_halo_run_card.json').read_text())
    assert archive_receipt['raster_sha256'] == quarantined['sha256']
    assert archive_receipt['serving_quarantine']['removed_from_docs_downloads'] is True
    status_path = ROOT / card['current_publication_status']
    # Code and current-publication hashes only need to remain live while this
    # card still describes the active status. Future changes archive the card.
    if sha256_file(status_path) == card['publication_status_sha256']:
        for rel, digest in card['input_sha256'].items():
            assert sha256_file(ROOT / rel) == digest, rel
        status = build_status(ROOT)
        assert status['raster_sha256'] == card['raster_sha256']
        assert status['submission_eligible'] is False
        assert status['verdict'] == 'negative'
