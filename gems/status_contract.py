"""Fail-closed cross-check for the *one* current decision on every entry path.

The freshly rebuilt ``scripts.render_readiness.build_status`` result is the
publication authority. Other JSON cards are archived lane records / aliases,
not independent promotion decisions. A changed alias or generated banner must
fail CI/Pages instead of advertising a different TIFF or score.
"""
from __future__ import annotations

import json
from pathlib import Path


def alias_errors(status: dict, current: dict, public: dict) -> list[str]:
    """Validate duplicate fields against the byte-validated readiness status."""
    errors: list[str] = []
    try:
        file = 'docs/' + status['file']
        digest = status['raster_sha256']
        name, note = status['submission_name'], status['note']
        hold = status['holdout_dti']
        if status['format_pass'] is not True or status['submission_eligible'] is not False or status['verdict'] != 'negative':
            errors.append('readiness cannot authorize a candidate through this rejection-only gate')
        if not isinstance(note, str) or not 0 < len(note) <= 140:
            errors.append('current form note must contain 1..140 characters')
        expected_current = {
            'file': file, 'sha256': digest, 'submission_name': name,
            'note': note, 'ok_to_download': True, 'ok_to_submit': False,
            'verdict': 'negative',
        }
        expected_public = {
            'primary_download': file, 'raster_sha256': digest,
            'submission_name': name, 'note': note,
            'submission_eligible': False, 'verdict': 'negative',
            'new_raster_generated': status['new_unique_tiff_generated'],
            'historical_artifact_was_generated': True,
            'revalidated_by': '2026-10-25 repository audit 78db3076; no new scientific evaluation',
            'experiments_executed': status['experiments_this_review'],
            'weekly_slots_used': status['weekly_slots_used_this_review'],
            'validator_output': status['validator_output'],
            'holdout_dti': hold,
            'organizer_confirmed_score': None,
        }
        for label, card, expected in (('current_submission', current, expected_current),
                                      ('public status', public, expected_public)):
            if not isinstance(card, dict):
                errors.append(f'{label}: must be a JSON object')
                continue
            for key, value in expected.items():
                if type(card.get(key)) is not type(value) or card.get(key) != value:
                    errors.append(f'{label}: {key} differs from readiness')
        if not isinstance(hold, dict) or hold.get('evidence_class') != 'HOLDOUT-DTI':
            errors.append('readiness has no labelled HOLDOUT-DTI')
        elif isinstance(current, dict):
            current_hold = current.get('holdout_dti', {})
            if not isinstance(current_hold, dict):
                errors.append('current_submission: holdout_dti is not an object')
            else:
                for old, new in (('dti', 'dti'), ('ci95', 'ci95'),
                                 ('withheld_positives', 'withheld_positive_pixels'),
                                 ('evaluator_version', 'evaluator_version')):
                    if current_hold.get(old) != hold.get(new):
                        errors.append(f'current_submission: holdout_dti.{old} differs from readiness')
                if current_hold.get('evidence_class') != 'HOLDOUT-DTI':
                    errors.append('current_submission: unlabelled holdout')
                if current_hold.get('paired_vs_control') != hold.get('paired_vs_KNICKLOQO_standalone_prev_best'):
                    errors.append('current_submission: paired control differs from readiness')
        if isinstance(public, dict):
            registry = public.get('correlation_overlap_vs_registry')
            if (not isinstance(registry, dict) or registry.get('forward_overlap') != 1.0
                    or registry.get('stop_required') is not True):
                errors.append('public status: literal registry STOP differs from readiness')
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f'broken readiness schema: {exc}')
    return errors


def check_publication(root: Path, status: dict) -> list[str]:
    """Check JSON aliases and exact current panels on every public entry page.

    Caller must rebuild ``status`` from *on-disk* TIFF/gates first; this check
    does not trust claims of ``format_pass`` in the published JSON. Historical
    banners may remain below these panels but can never be the current decision.
    """
    problems: list[str] = []

    def card(rel: str) -> dict:
        try:
            value = json.loads((root / rel).read_text(encoding='utf-8'))
            if not isinstance(value, dict):
                raise ValueError('not a JSON object')
            return value
        except (OSError, ValueError) as exc:
            problems.append(f'{rel}: missing or invalid status card: {exc}')
            return {}

    current = card('docs/downloads/current_submission.json')
    published = card('docs/downloads/readiness.json')
    public = card('docs/downloads/review797e_run_card.json')
    mirror = card('evidence/review797e_run_card.json')
    audit = card('docs/downloads/review48_run_card.json')
    final = card('docs/downloads/session_78db3076_run_card.json')
    final_evidence = card('evidence/session_78db3076_final.json')
    if published != status:
        problems.append('readiness.json differs from the on-disk validated candidate')
    if mirror != public:
        problems.append('public status and evidence mirror differ')
    if final != final_evidence:
        problems.append('final review run card and evidence mirror differ')

    def without_audit_times(document: dict) -> dict:
        # Separate fresh runs differ only in their acquisition timestamps.
        clean = dict(document)
        clean.pop('reviewed_utc', None)
        registry = clean.get('correlation_overlap_vs_registry')
        if isinstance(registry, dict):
            clean['correlation_overlap_vs_registry'] = dict(registry)
            proof = registry.get('preplacement_proof')
            if isinstance(proof, dict):
                clean['correlation_overlap_vs_registry']['preplacement_proof'] = dict(proof)
                clean['correlation_overlap_vs_registry']['preplacement_proof'].pop('reviewed_utc', None)
        return clean

    # The independently checked, published rejection audit (check_published_audit)
    # is the reference. Neither a changed source hash nor a changed score can be
    # hidden in the new named JSON alias while keeping its evidence mirror intact.
    if without_audit_times(final) != without_audit_times(audit):
        problems.append('final review run card differs from the independently validated audit')
    problems.extend(alias_errors(status, current, public))
    if problems:
        return problems  # Never render a disputed card to compare page content.

    from scripts.render_current_submission import (BEGIN, END, HTML_PAGES, MD_PAGES,
                                                    html_block, md_block)
    for path, prefix in {**HTML_PAGES, **MD_PAGES}.items():
        # These dictionaries point at the live checkout by default. Resolve the
        # same relative page names in root for an isolated fixture or CI clone.
        rel = path.relative_to(path.parents[1] if path.parent.name == 'docs' else path.parent)
        page = root / rel
        if not page.is_file():
            problems.append(f'{rel}: current panel page is missing')
            continue
        expected = html_block(current, prefix) if path in HTML_PAGES else md_block(current, prefix)
        if rel == Path('docs/SUBMIT.md'):
            expected = expected.replace('](SESSION_PROMPT.md)', '](../SESSION_PROMPT.md)')
        text = page.read_text(encoding='utf-8')
        if text.count(BEGIN) != 1 or text.count(END) != 1:
            problems.append(f'{rel}: missing or ambiguous current-panel markers')
            continue
        actual = BEGIN + text.split(BEGIN, 1)[1].split(END, 1)[0] + END
        if actual != expected:
            problems.append(f'{rel}: current panel differs from the validated candidate')
    return problems
