#!/usr/bin/env python3
"""Build this session's negative run card from independent, pinned receipts.

Rejection-only: this renderer cannot authorize a slot or produce a candidate.
The GitHub freshness snapshot compares refs, not scores or new TIFFs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gems.gates import run_gates, summarise  # noqa: E402
from scripts.render_readiness import rejection_proof_errors  # noqa: E402

PREFLIGHT = ROOT / 'docs/downloads/session_b97812a3_preflight_final.json'
INPUTS = ROOT / 'docs/downloads/session_b97812a3_input_audit.json'
SUPPORT = ROOT / 'docs/downloads/session_b97812a3_witness_support.json'
FRESHNESS = ROOT / 'docs/downloads/session_b97812a3_focus_freshness.json'
OUTPUT = ROOT / 'docs/downloads/session_b97812a3_run_card.json'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    result = json.loads(path.read_bytes())
    if not isinstance(result, dict):
        raise ValueError(f'expected object: {path}')
    return result


def build() -> dict:
    preflight, inputs, support, fresh = map(load, (PREFLIGHT, INPUTS, SUPPORT, FRESHNESS))
    overlap = preflight['correlation_overlap_vs_registry']
    proof = overlap['preplacement_proof']
    if (preflight['verdict'] != 'negative' or preflight['submission_eligible'] is not False
            or preflight['new_unique_tiff_generated'] is not False
            or preflight['experiments'] != 0 or preflight['weekly_slots_used'] != 0
            or preflight['holdout_dti']['value'] is not None
            or preflight['organizer_confirmed_score'] is not None):
        raise ValueError('preflight must be rejection only')
    if rejection_proof_errors(proof, digest(ROOT / 'data/bridge/sample_submission.tif')):
        raise ValueError('pinned duplicate proof is incomplete')
    if (proof['implementation_sha256'] != digest(ROOT / 'scripts/preflight_dense_witness.py')
            or preflight['audit_implementation_sha256'] != digest(ROOT / 'evidence/archive/audit_readiness_20261030_before_site_primary_binding.py')):
        raise ValueError('preflight implementation differs from receipt')
    stats = support['statistics']
    if (support['schema'] != 'gemsdoe92-witness-support-v1'
            or support['implementation_sha256'] != digest(ROOT / 'scripts/inspect_witness_support.py')
            or support['sample_sha256'] != proof['sample_sha256']
            or support['witness_sha256'] != proof['sha256']
            or stats['finite_footprint_pixels'] != proof['footprint_pixels']
            or stats['positive_footprint_pixels'] != proof['positive_in_footprint']
            or stats['distinct_values'] <= 2 or stats['binary_zero_or_one_pixels'] != 0
            or support['submission_eligible'] is not False or support['new_candidate'] is not False):
        raise ValueError('witness characterization differs from the pinned proof')
    manifest_path = ROOT / 'registry/session_manifest.json'
    manifest = load(manifest_path)
    pinned = {r['id']: r for r in manifest['files']}
    rows = inputs['files']
    by_id = {r['id']: r for r in rows}
    meta = inputs['raster_metadata']
    if (inputs['manifest_sha256'] != digest(manifest_path)
            or inputs['files_expected'] != 12 or inputs['files_verified'] != 12
            or len(rows) != 12 or len(by_id) != 12 or set(by_id) != set(pinned)
            or inputs['all_pins_verified'] is not True or inputs['all_local_checks_passed'] is not True
            or inputs['official_origin_authenticated'] is not False
            or inputs['redistribution_rights_verified'] is not False
            or inputs['submission_eligible'] is not False or inputs['holdout_run'] is not False
            or meta['checked'] is not True or meta['grid_matches_sample'] is not True
            or meta['expected_band_tags_match'] is not True or meta['feature_band_count'] != 19
            or meta['problems']):
        raise ValueError('input audit is incomplete or overclaims provenance')
    if any(r['verified'] is not True or r['observed_sha256'] != pinned[name]['sha256']
           or r['expected_sha256'] != pinned[name]['sha256']
           or r['expected_bytes'] != pinned[name]['bytes']
           or r['path'] != pinned[name]['local_path'] for name, r in by_id.items()):
        raise ValueError('input audit rows differ from manifest')
    if by_id['sample_submission']['expected_sha256'] != proof['sample_sha256']:
        raise ValueError('input footprint does not match rejection proof')
    inventory = ROOT / 'docs/downloads/focus_sites_release_review_20261026.json'
    if (fresh['inventory_sha256'] != digest(inventory) or len(fresh['sites']) != 9
            or fresh['submission_eligible'] is not False or fresh['organizer_confirmed_score'] is not None):
        raise ValueError('GitHub ref snapshot is inconsistent or overclaims')
    primary = (ROOT / preflight['primary_download']).resolve()
    if not primary.is_relative_to((ROOT / 'docs/downloads').resolve()) or digest(primary) != preflight['raster_sha256']:
        raise ValueError('historical reference TIFF does not match its recorded bytes')
    results = run_gates(str(primary), str(ROOT / 'data/bridge/sample_submission.tif'),
                        str(ROOT / 'data/bridge/labels.tif'), prune_radius=2,
                        require_submission_encoding=True)
    ok, _ = summarise(results)
    fresh_gates = [dict(name=r.name, ok=r.ok, detail=r.detail) for r in results]
    if not ok or preflight['format_pass'] is not True or fresh_gates != preflight['validator_output']:
        raise ValueError('historical reference format evidence is stale or failed')
    old_holdout_path = ROOT / 'evidence/vario_holdout.json'
    old = load(old_holdout_path)
    h = old['scores']['vario_full']
    delta = old['paired_by_candidate']['vario_full']['control_FAULTNET_far']
    if (h['evidence_class'] != 'HOLDOUT-DTI' or delta['evidence_class'] != 'HOLDOUT-DTI'
            or h['evaluator_version'] != delta['evaluator_version']
            or h['withheld_positive_pixels'] != delta['withheld_positive_pixels']
            or len(h['ci95']) != 2 or len(delta['ci95']) != 2 or delta['ci95'][1] >= 0):
        raise ValueError('historical comparable holdout is incomplete')
    return {
        'schema': 'gemsdoe92-review-b97812a3-v1',
        'reviewed_utc': preflight['reviewed_utc'],
        'hypothesis': 'LOCAL-WAVENUMBER-CONSENSUS (ranked, untried; no method lane assigned)',
        'mechanism': 'Multi-scale magnetic phase and wavelength boundaries may align buried fault structure; independent geology is needed.',
        'named_non_fault_mimic': 'Lithologic contacts, remanent volcanic bodies, or flight-line and processing artifacts.',
        'holdout_dti': {'evidence_class': 'HOLDOUT-DTI', 'value': None, 'evaluator_version': None,
                        'withheld_positives': None, 'ci95': None,
                        'reason': 'Not run after the conservative pre-placement duplicate STOP.'},
        'leakage_canaries': {'status': 'not_run', 'reason': 'No candidate features were generated.'},
        'correlation_overlap_vs_registry': {
            'evidence_class': 'REGISTRY-MEASUREMENT',
            'rank_correlation': None, 'surface_overlap': None, 'final_dots_overlap': None,
            'conditional_universal_forward_overlap': 1.0, 'threshold': 0.70,
            'condition': 'Every positive continuous-probability witness pixel is treated as a dot.',
            'interpretation': 'Continuous-probability to dot representation is unresolved; not proof of geological identity.',
            'scope': 'One pinned full-support witness; rejection only, not registry clearance.',
            'witness_sha256': proof['sha256'], 'footprint_pixels': stats['finite_footprint_pixels'],
            'positive_pixels': stats['positive_footprint_pixels'],
            'final_dots_status': 'not_run_no_new_raster',
        },
        'new_unique_tiff_generated': False, 'raster_sha256': None,
        'validator_output': {'new_candidate': None, 'status': 'not_run_no_new_raster',
                             'portal_acceptance': 'not tested; local format is not a portal receipt'},
        'submission_name': None, 'submission_note': None,
        'verdict': 'negative', 'submission_eligible': False,
        'experiments': 0, 'weekly_slots_used': 0,
        'organizer_confirmed_score': None, 'leaderboard_estimate': None,
        'historical_research_reference': {
            'file': preflight['primary_download'], 'sha256': preflight['raster_sha256'],
            'status': 'research only; DO NOT SUBMIT', 'format_pass': True, 'format_gates': fresh_gates,
            'prior_holdout_dti': {'evidence_class': 'HOLDOUT-DTI', 'evaluator_version': h['evaluator_version'],
                                  'withheld_positives': h['withheld_positive_pixels'],
                                  'value': h['dti'], 'ci95': h['ci95'],
                                  'paired_difference_vs_FAULTNET_far': delta['delta'],
                                  'paired_difference_ci95': delta['ci95'],
                                  'source': 'evidence/vario_holdout.json', 'source_sha256': digest(old_holdout_path),
                                  'status': 'historical, not rerun here; not an organizer score'},
        },
        'input_cache': {'verified_pins': 12, 'expected_pins': 12, 'feature_band_count': 19,
                        'official_origin_authenticated': False, 'redistribution_rights_verified': False,
                        'cache_persistent': False},
        'nine_site_freshness_snapshot': {'observed_utc': fresh['observed_utc'],
                                          'changed_count': fresh['changed_count'],
                                          'unknown_count': fresh['unknown_count'],
                                          'scope': 'GitHub refs only, not new artifact or score audits'},
        'sources': {str(p.relative_to(ROOT)): digest(p) for p in (PREFLIGHT, INPUTS, SUPPORT, FRESHNESS)},
        'limitations': [
            'No explicitly assigned method lane, fresh candidate, holdout, organizer receipt or competition slot.',
            'No authorized interpretation resolves continuous probability pixels versus registry dots.',
            'Pinned inputs are owner mirrors: official provenance and redistribution rights are unverified.',
            'Local zeros outside the sample footprint are not proven equivalent to official outside-bounds null/NaN.',
            'GitHub refs are time-specific; historical selected-site comparison is not a current complete inventory.',
            'Other historical builders remain unaudited; a format pass never proves uniqueness or portal acceptance.',
        ],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    args = p.parse_args(argv)
    try:
        card = json.dumps(build(), indent=2, allow_nan=False) + '\n'
        if args.check:
            if not OUTPUT.is_file() or OUTPUT.read_text() != card:
                raise ValueError('run card is stale')
            print('session negative run card: OK')
        else:
            OUTPUT.write_text(card, encoding='utf-8')
            print(f'wrote {OUTPUT}')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'session review failed closed: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
