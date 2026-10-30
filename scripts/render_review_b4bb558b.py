#!/usr/bin/env python3
"""Publish the 2026-10-27 rejection-only review, bound to its source receipts.

No feature generation, holdout or submission is implied. The cache audit proves
owner-mirror identity and basic metadata, not competition provenance or rights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / 'evidence/review_b4bb558b_preflight.json'
INPUT = ROOT / 'evidence/input_cache_b4bb558b.json'
PAIR = ROOT / 'evidence/focus9_recheck_b4bb558b.json'
PREVIOUS_PAIR = ROOT / 'docs/downloads/focus9_pairwise_recheck_14f85876.json'
PUBLIC_INPUT = ROOT / 'docs/downloads/input_cache_b4bb558b.json'
OUTPUT = ROOT / 'docs/downloads/review_b4bb558b_run_card.json'


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def build() -> dict:
    proof_raw, inputs_raw, pairs_raw = PREFLIGHT.read_bytes(), INPUT.read_bytes(), PAIR.read_bytes()
    preflight, inputs, pairs = map(json.loads, (proof_raw, inputs_raw, pairs_raw))
    overlap = preflight['correlation_overlap_vs_registry']
    proof = overlap['preplacement_proof']
    if (preflight['verdict'] != 'negative' or preflight['submission_eligible'] is not False
            or preflight['new_unique_tiff_generated'] is not False or preflight['experiments'] != 0
            or preflight['weekly_slots_used'] != 0 or preflight['holdout_dti']['value'] is not None
            or proof['verdict'] != 'negative' or proof['submission_eligible'] is not False
            or proof['grid_checks_pass'] is not True
            or proof['universal_nonempty_in_footprint_overlap_stop'] is not True
            or proof['positive_in_footprint'] != proof['footprint_pixels']
            or proof['forward_overlap_for_any_nonempty_in_footprint_dot_set'] != 1.0
            or proof['threshold'] != 0.70):
        raise ValueError('preflight is not the complete rejection-only proof')
    if proof['implementation_sha256'] != digest((ROOT / 'scripts/preflight_dense_witness.py').read_bytes()):
        raise ValueError('preflight implementation differs from receipt')
    if preflight['audit_implementation_sha256'] != digest((ROOT / 'evidence/archive/audit_readiness_20261030_before_site_primary_binding.py').read_bytes()):
        raise ValueError('readiness implementation differs from receipt')
    files = inputs['files']
    meta = inputs['raster_metadata']
    if (inputs['manifest_sha256'] != digest((ROOT / 'registry/session_manifest.json').read_bytes())
            or inputs['files_expected'] != 12 or inputs['files_verified'] != 12
            or len(files) != 12 or len({r['id'] for r in files}) != 12
            or any(r['verified'] is not True or r['observed_sha256'] != r['expected_sha256'] for r in files)
            or inputs['all_pins_verified'] is not True or inputs['all_local_checks_passed'] is not True
            or inputs['official_origin_authenticated'] is not False or inputs['redistribution_rights_verified'] is not False
            or inputs['submission_eligible'] is not False or inputs['holdout_run'] is not False
            or meta['checked'] is not True or meta['grid_matches_sample'] is not True
            or meta['expected_band_tags_match'] is not True or meta['feature_band_count'] != 19
            or meta['problems']):
        raise ValueError('input audit is incomplete or overclaims provenance')
    by_id = {r['id']: r for r in files}
    manifest = json.loads((ROOT / 'registry/session_manifest.json').read_bytes())
    pinned = {r['id']: r for r in manifest['files']}
    if set(by_id) != set(pinned) or any(
            row['expected_sha256'] != pinned[name]['sha256']
            or row['expected_bytes'] != pinned[name]['bytes']
            or row['path'] != pinned[name]['local_path']
            for name, row in by_id.items()):
        raise ValueError('input receipt rows do not match the pinned manifest')
    if (by_id['sample_submission']['expected_sha256'] != proof['sample_sha256']
            or digest((ROOT / 'data/bridge/sample_submission.tif').read_bytes()) != proof['sample_sha256']):
        raise ValueError('preflight and input audit use different footprints')
    if (pairs_raw != PREVIOUS_PAIR.read_bytes() or pairs['pairs'] != 36
            or pairs['source_blob_and_sha256_verified'] is not True
            or pairs['all_pairs_duplicate_in_at_least_one_direction_or_rho'] is not True
            or pairs['submission_eligible'] is not False):
        raise ValueError('nine-site rerun differs from corrected rejection evidence')
    primary = ROOT / preflight['primary_download']
    if digest(primary.read_bytes()) != preflight['raster_sha256']:
        raise ValueError('historical research raster does not match its measured hash')
    if preflight['format_pass'] is not True or any(x['ok'] is not True for x in preflight['validator_output']):
        raise ValueError('historical research format evidence is incomplete')
    holdout_raw = (ROOT / 'evidence/vario_holdout.json').read_bytes()
    holdout = json.loads(holdout_raw)
    historical = holdout['scores']['vario_full']
    delta = holdout['paired_by_candidate']['vario_full']['control_FAULTNET_far']
    if (historical['evidence_class'] != 'HOLDOUT-DTI' or delta['evidence_class'] != 'HOLDOUT-DTI'
            or historical['evaluator_version'] != delta['evaluator_version']
            or historical['withheld_positive_pixels'] != delta['withheld_positive_pixels']
            or len(historical['ci95']) != 2 or len(delta['ci95']) != 2 or delta['ci95'][1] >= 0):
        raise ValueError('historical comparable-control evidence is incomplete')
    return {
        'schema': 'gemsdoe92-review-b4bb558b-v1',
        'reviewed_utc': preflight['reviewed_utc'],
        'hypothesis': 'LOCAL-WAVENUMBER-CONSENSUS (conditional research idea; no lane assigned and not tested)',
        'mechanism': 'Possible faults may align multi-scale magnetic phase and wavelength boundaries; complementary geological evidence would be needed.',
        'named_non_fault_mimic': 'Lithologic contacts or flight-line and processing artifacts can create similar magnetic boundaries.',
        'holdout_dti': {
            'evidence_class': 'HOLDOUT-DTI', 'value': None, 'ci95': None,
            'evaluator_version': None, 'withheld_positives': None,
            'reason': 'Not run: a pinned registry witness triggers the literal pre-placement stop.',
        },
        'leakage_canaries': {'status': 'not_run', 'reason': 'No experimental features were generated.'},
        'correlation_overlap_vs_registry': {
            'evidence_class': 'REGISTRY-MEASUREMENT',
            'scope': 'One freshly fetched and hash-verified witness; sufficient for rejection, not global uniqueness clearance.',
            'preplacement_proof': proof,
            'forward_overlap_for_any_nonempty_in_footprint_candidate': 1.0,
            'overlap_threshold': 0.70,
            'rank_correlation': None,
            'rank_correlation_reason': 'No candidate surface or final dots exist; overlap alone rejects.',
            'surface_check': 'rejected_by_universal_witness_before_surface_creation',
            'final_dots_check': 'not_run_no_new_raster',
        },
        'new_unique_tiff_generated': False,
        'raster_sha256': None,
        'validator_output': {
            'new_candidate': {'status': 'not_run_no_new_raster', 'checks': None},
            'portal_acceptance': 'not tested; local zero-outside-footprint encoding is not proof of portal acceptance',
        },
        'submission_name': None,
        'submission_note': None,
        'verdict': 'negative',
        'submission_eligible': False,
        'experiments': 0,
        'weekly_slots_used': 0,
        'organizer_confirmed_score': None,
        'score_estimate': None,
        'score_estimate_reason': 'No organizer score-to-file receipts or valid independent calibration for prospective per-file estimates.',
        'historical_research_reference': {
            'file': preflight['primary_download'], 'sha256': preflight['raster_sha256'],
            'status': 'research only; DO NOT SUBMIT', 'format_pass': True,
            'format_gates': preflight['validator_output'],
            'name_for_this_old_file_only': preflight['submission_name'],
            'note_for_this_old_file_only': preflight['note'],
            'prior_holdout_dti': {
                'evidence_class': historical['evidence_class'],
                'evaluator_version': historical['evaluator_version'],
                'withheld_positives': historical['withheld_positive_pixels'],
                'value': historical['dti'], 'ci95': historical['ci95'],
                'paired_difference_vs_control_FAULTNET_far': delta['delta'],
                'paired_difference_ci95': delta['ci95'],
                'source': 'evidence/vario_holdout.json', 'source_sha256': digest(holdout_raw),
                'status': 'historical, not rerun here; not an organizer score',
            },
        },
        'input_cache_audit': {
            'public_receipt': 'docs/downloads/input_cache_b4bb558b.json',
            'receipt_sha256': digest(inputs_raw), 'reviewed_utc': inputs['reviewed_utc'],
            'verified_pins': 12, 'expected_pins': 12,
            'feature_stack_sha256': by_id['training_features']['expected_sha256'],
            'feature_band_count': 19, 'grid_and_band_tags_match': True,
            'official_origin_authenticated': False, 'redistribution_rights_verified': False,
            'cache_persistent': False,
        },
        'nine_site_rerun': {
            'receipt': 'evidence/focus9_recheck_b4bb558b.json',
            'receipt_sha256': digest(pairs_raw), 'pairs_checked': 36,
            'result': 'Matches prior corrected row-safe receipt byte for byte; all 36 pairs reject in at least one direction or by absolute rho.',
            'same_binary_support': ['GEMSDOE25', 'GEMSDOE30'],
            'scope': 'Nine selected historical artifacts only, not a global uniqueness clearance.',
        },
        'evidence_sources': {
            'preflight_receipt': 'evidence/review_b4bb558b_preflight.json',
            'preflight_receipt_sha256': digest(proof_raw),
            'hypotheses': 'docs/HYPOTHESES_20261026_SITE_REVIEW.md',
            'review': 'docs/REVIEW_B4BB558B.md',
        },
        'limitations': [
            'No official score receipt or current leaderboard position is verified.',
            'A fully dense witness creates a rule/representation degeneracy, not proof of scientific sameness.',
            'Other historical builders remain unaudited; the format writer alone does not establish uniqueness.',
            'Hardlink publication prevents ordinary overwrite; rollback is not atomic against noncooperating concurrent writers.',
            'No policy change, lane selection, model fit, submission or weekly slot selection occurred.',
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    try:
        card = json.dumps(build(), indent=2, allow_nan=False) + '\n'
        if args.check:
            if (not OUTPUT.is_file() or OUTPUT.read_text(encoding='utf-8') != card
                    or not PUBLIC_INPUT.is_file() or PUBLIC_INPUT.read_bytes() != INPUT.read_bytes()):
                raise ValueError('public review card or input receipt is stale')
            print('2026-10-27 review card and input receipt: OK')
        else:
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            PUBLIC_INPUT.write_bytes(INPUT.read_bytes())
            OUTPUT.write_text(card, encoding='utf-8')
            print(f'wrote {OUTPUT} and {PUBLIC_INPUT}')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'review card failed closed: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
