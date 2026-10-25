"""A research-only alias must not become a submission CTA after a parallel merge."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil

import pytest

from gems.status_contract import alias_errors, check_publication
from scripts.render_readiness import build_status
from scripts.render_current_submission import HTML_PAGES, MD_PAGES, BEGIN, END, inject

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def cards():
    status = build_status(ROOT)  # Re-read the actual candidate with shared gates.
    current = json.loads((ROOT / 'docs/downloads/current_submission.json').read_text())
    public = json.loads((ROOT / 'docs/downloads/review797e_run_card.json').read_text())
    return status, current, public


def test_current_publication_is_consistent(cards):
    assert alias_errors(*cards) == []
    assert check_publication(ROOT, cards[0]) == []
    assert 'check_publication(ROOT, build_status(ROOT))' in (ROOT / 'scripts/check_site.py').read_text()


@pytest.mark.parametrize('field,value', [
    ('file', 'docs/downloads/not-the-primary-zeros.tif'),
    ('sha256', 'f' * 64), ('note', 'not the audited note'),
    ('submission_name', 'different name'),
    ('ok_to_submit', True), ('ok_to_submit', 'false'),
    ('verdict', 'promote'), ('ok_to_download', False),
])
def test_changed_lane_alias_never_advertises_a_different_decision(cards, field, value):
    status, current, public = copy.deepcopy(cards)
    current[field] = value
    assert alias_errors(status, current, public)


@pytest.mark.parametrize('field,value', [
    ('primary_download', 'docs/downloads/wrong-zeros.tif'),
    ('raster_sha256', '0' * 64), ('note', 'this is not the form note'),
    ('submission_eligible', True), ('verdict', 'promote'),
    ('organizer_confirmed_score', 0.4413),
    ('new_raster_generated', True),
    ('historical_artifact_was_generated', False),
    ('revalidated_by', 'fake review'),
    ('holdout_dti', {'evidence_class': 'HOLDOUT-DTI', 'dti': 0.4413}),
    ('validator_output', []),
    ('experiments_executed', 3), ('weekly_slots_used', 1),
    ('correlation_overlap_vs_registry', {'forward_overlap': 0.0, 'stop_required': False}),
])
def test_changed_public_alias_cannot_bypass_gate(cards, field, value):
    status, current, public = copy.deepcopy(cards)
    public[field] = value
    assert alias_errors(status, current, public)


@pytest.mark.parametrize('key,value', [
    ('dti', 0.4413), ('ci95', [0.0, 1.0]),
    ('evaluator_version', 'unknown'), ('withheld_positives', 1),
    ('evidence_class', 'ORGANIZER-CONFIRMED'),
    ('paired_vs_control', {'delta': 0.4413}),
])
def test_holdout_claim_cannot_drift_from_audited_run_card(cards, key, value):
    status, current, public = copy.deepcopy(cards)
    current['holdout_dti'][key] = value
    assert alias_errors(status, current, public)


@pytest.fixture
def publication(tmp_path, cards):
    for source in (*HTML_PAGES, *MD_PAGES, ROOT / 'docs/downloads/current_submission.json',
                   ROOT / 'docs/downloads/readiness.json',
                   ROOT / 'docs/downloads/review797e_run_card.json',
                   ROOT / 'evidence/review797e_run_card.json',
                   ROOT / 'docs/downloads/review48_run_card.json',
                   ROOT / 'docs/downloads/session_78db3076_run_card.json',
                   ROOT / 'evidence/session_78db3076_final.json'):
        rel = source.relative_to(ROOT)
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    assert check_publication(tmp_path, cards[0]) == []
    return tmp_path


@pytest.mark.parametrize('rel', ['README.md', 'docs/index.html', 'docs/executive-summary.html',
                                 'docs/SUBMIT.html', 'docs/submit.html', 'index.html'])
def test_each_entry_point_is_checked_even_when_json_is_intact(publication, cards, rel):
    page = publication / rel
    page.write_text(page.read_text().replace('Newest lane result', 'SUBMIT NOW — stale parallel lane', 1))
    assert any(rel in p and 'panel' in p for p in check_publication(publication, cards[0]))


def test_missing_markers_and_duplicate_markers_fail_closed(publication, cards):
    page = publication / 'docs/index.html'
    text = page.read_text()
    page.write_text(text.replace(BEGIN, '', 1))
    assert any('docs/index.html' in p for p in check_publication(publication, cards[0]))
    page.write_text(text + BEGIN)
    assert any('docs/index.html' in p for p in check_publication(publication, cards[0]))


def test_lane_renderer_is_idempotent_without_readiness_markers():
    page = '# Guide\n\nHistorical text\n'
    block = BEGIN + '\nDO NOT SUBMIT\n' + END
    once = inject(page, block, False)
    assert inject(once, block, False) == once
    for malformed in (BEGIN, END, END + BEGIN, BEGIN + END + BEGIN + END):
        with pytest.raises(ValueError, match='markers'):
            inject(page + malformed, block, False)


def test_session_card_must_match_evidence_and_independent_audit(publication, cards):
    final = publication / 'docs/downloads/session_78db3076_run_card.json'
    card = json.loads(final.read_text())
    card['note'] = 'changed published note'
    final.write_text(json.dumps(card))
    assert any('final review run card' in p for p in check_publication(publication, cards[0]))

    # Forging both alias and mirror still disagrees with the independently
    # verified rejection audit, whose implementation hash is checked by CI.
    mirror = publication / 'evidence/session_78db3076_final.json'
    mirror.write_text(final.read_text())
    assert any('independently validated audit' in p for p in check_publication(publication, cards[0]))


def test_mirror_or_readiness_manifest_drift_is_rejected(publication, cards):
    mirror = publication / 'evidence/review797e_run_card.json'
    card = json.loads(mirror.read_text())
    card['note'] = 'different form note'
    mirror.write_text(json.dumps(card))
    assert any('mirror' in p for p in check_publication(publication, cards[0]))
    shutil.copyfile(ROOT / 'evidence/review797e_run_card.json', mirror)
    manifest = publication / 'docs/downloads/readiness.json'
    stale = json.loads(manifest.read_text())
    stale['file'] = 'downloads/other-zeros.tif'
    manifest.write_text(json.dumps(stale))
    assert any('readiness.json' in p for p in check_publication(publication, cards[0]))
