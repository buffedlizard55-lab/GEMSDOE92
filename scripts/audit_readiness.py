#!/usr/bin/env python3
"""Reproduce the literal pre-placement STOP and revalidate the current download.

No model, raster or submission is created. Exit 1 = confirmed protocol STOP;
exit 2 = inconclusive/invalid evidence. This rejection-only command never grants
clearance. Use --fetch-witness to retrieve the pinned public GitHub blob via gh;
otherwise the witness must already exist locally. All downloads stay ignored.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.preflight_dense_witness import (  # noqa: E402
    WITNESS_BLOB, WITNESS_SHA256, hashes, preflight,
)
from scripts.render_readiness import build_status  # noqa: E402

BLOB_API = f'repos/buffedlizard55-lab/17GEMSDOE/git/blobs/{WITNESS_BLOB}'
WITNESS_BYTES = 25065181
DEFAULT_WITNESS = ROOT / '.cache/gemsdoe_public_registry' / (WITNESS_BLOB + '.tif')


def decode_witness(doc: dict) -> bytes:
    """A successful HTTP response is not proof of blob identity."""
    if (not isinstance(doc, dict) or doc.get('encoding') != 'base64'
            or doc.get('sha') != WITNESS_BLOB
            or type(doc.get('size')) is not int or doc['size'] != WITNESS_BYTES
            or not isinstance(doc.get('content'), str)):
        raise ValueError('unexpected witness API metadata')
    data = base64.b64decode(''.join(doc['content'].split()), validate=True)
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if (len(data) != WITNESS_BYTES or blob != WITNESS_BLOB
            or hashlib.sha256(data).hexdigest() != WITNESS_SHA256):
        raise ValueError('witness bytes do not match pinned size/SHA-256/Git blob')
    return data


def fetch_witness(target: Path) -> None:
    """Do not replace invalid cached evidence, even when fetching is requested."""
    if target.exists():
        if target.stat().st_size != WITNESS_BYTES or hashes(target) != (WITNESS_SHA256, WITNESS_BLOB):
            raise ValueError('cached witness is corrupt; refusing to overwrite evidence')
        return
    response = subprocess.run(['gh', 'api', BLOB_API], check=True,
                              capture_output=True, text=True, timeout=120)
    data = decode_witness(json.loads(response.stdout))
    target.parent.mkdir(parents=True, exist_ok=True)
    # Validate first, then atomically install without overwriting a concurrent
    # writer. An interrupted download never leaves a trusted cache filename.
    import os
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tmp:
        tmp_path = Path(tmp.name)
        try:
            tmp.write(data)
            tmp.flush()
            os.fsync(tmp.fileno())
            os.link(tmp_path, target)
        finally:
            tmp_path.unlink(missing_ok=True)


def audit(root: Path, witness: Path) -> dict:
    proof = preflight(root / 'data/bridge/sample_submission.tif', witness)
    if proof['universal_nonempty_in_footprint_overlap_stop'] is not True:
        raise ValueError('universal stop not established; this tool cannot grant clearance')
    status = build_status(root)  # Reuses primary discovery, byte checks and shared run_gates.
    return {
        'schema': 'gemsdoe92-readiness-audit-v1',
        'reviewed_utc': datetime.now(timezone.utc).isoformat(),
        'hypothesis': 'No assigned geological lane; pre-placement protocol audit only.',
        'mechanism': 'The pinned registry positive support covers every finite template pixel.',
        'named_non_fault_mimic': 'Not applicable: no geological inference was performed.',
        'holdout_dti': {
            'evidence_class': 'HOLDOUT-DTI', 'value': None, 'ci95': None,
            'evaluator_version': None, 'withheld_positives': None,
            'reason': 'Not run: universal literal duplicate STOP before feature generation or placement.',
        },
        'leakage_canaries': {'status': 'not_run', 'reason': 'No features generated after STOP.'},
        'correlation_overlap_vs_registry': {
            'evidence_class': 'REGISTRY-MEASUREMENT',
            'forward_overlap_for_any_nonempty_in_footprint_candidate': 1.0,
            'overlap_threshold': 0.70, 'rank_correlation': None,
            'rank_correlation_reason': 'Not needed for rejection; no surface or final dots generated.',
            'scope': 'One hash-pinned witness; sufficient to reject, never to certify uniqueness.',
            'preplacement_proof': proof,
            'final_dots_check': 'not_run_no_new_raster',
        },
        'artifact_role': 'existing research download; NOT a newly generated submission',
        'primary_download': 'docs/' + status['file'],
        'raster_sha256': status['raster_sha256'],
        'validator_output': status['validator_output'],
        'format_pass': status['format_pass'],
        'submission_name': status['submission_name'],
        'note': status['note'],
        'verdict': 'negative', 'submission_eligible': False,
        'new_unique_tiff_generated': False, 'experiments': 0, 'weekly_slots_used': 0,
        'organizer_confirmed_score': None,
        'limitations': status['blocking_reasons'],
        'input_sha256': status['input_sha256'],
        'audit_implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def check_published_audit(root: Path = ROOT) -> list[str]:
    """Bind published status to the active Arena receipt and current source bytes.

    The review48 audit is retained as historical evidence after an integration.
    It is not the current authority.  Recompute the shared format status, verify
    the active byte-bound run-card copies, and re-check the rejection-only proof
    without fetching data or authorizing a submission.
    """
    try:
        from scripts.render_readiness import rejection_proof_errors
        from gems.public_status import validate_status
        from gems.rasters import sha256_file

        errors: list[str] = []
        status = build_status(root)
        published_status = json.loads((root / 'docs/downloads/readiness.json').read_text())
        if published_status != status:
            keys = sorted(set(published_status) | set(status)) if isinstance(published_status, dict) else []
            changed = [key for key in keys if not isinstance(published_status, dict)
                       or published_status.get(key) != status.get(key)]
            errors.extend(f'published readiness status mismatch: {key}' for key in changed or ['document'])

        proof_path = root / 'evidence/preplacement_stop_20261025_arena.json'
        proof = json.loads(proof_path.read_text())
        sample_sha = status['input_sha256']['data/bridge/sample_submission.tif']
        errors.extend(rejection_proof_errors(proof, sample_sha))
        expected_impl = sha256_file(root / 'scripts/preflight_dense_witness.py')
        if proof.get('implementation_sha256') != expected_impl:
            errors.append('published pre-placement proof implementation is stale')

        evidence_card_path = root / 'evidence/arena_review_run_card_20261025.json'
        public_card_path = root / 'docs/downloads/arena_review_run_card_20261025.json'
        evidence_card = json.loads(evidence_card_path.read_text())
        public_card = json.loads(public_card_path.read_text())
        if public_card != evidence_card:
            errors.append('public run card differs from its evidence copy')
        try:
            validate_status(public_card, root, status['file'])
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'invalid current public run card: {exc}')

        if public_card.get('primary_download') != 'docs/' + status['file']:
            errors.append('public run card primary differs from current readiness')
        if public_card.get('raster_sha256') != status['raster_sha256']:
            errors.append('public run card hash differs from current readiness')
        if public_card.get('verdict') != 'negative' or public_card.get('submission_eligible') is not False:
            errors.append('public run card must preserve the negative, not-cleared decision')
        if (public_card.get('new_unique_tiff_generated') is not False
                or public_card.get('new_raster_generated') is not False
                or public_card.get('experiments_run') != 0
                or public_card.get('weekly_slots_used') != 0):
            errors.append('public run card must not claim a new raster, experiment, or slot')
        holdout = public_card.get('holdout_dti')
        if (not isinstance(holdout, dict) or any(holdout.get(key) is not None for key in
                ('dti', 'ci95', 'evaluator_version', 'withheld_positive_count'))):
            errors.append('public run card cannot claim a new HOLDOUT-DTI result')
        organizer = public_card.get('organizer_confirmed_score')
        if (not isinstance(organizer, dict) or organizer.get('score') is not None
                or organizer.get('receipt') is not None):
            errors.append('public run card cannot claim an ORGANIZER-CONFIRMED score')
        claim = public_card.get('claim_boundary', {}).get('GEMSDOE32_0_2778')
        if not isinstance(claim, str) or 'CLAIM' not in claim or 'ORGANIZER-CONFIRMED' not in claim:
            errors.append('GEMSDOE32 0.2778 must remain an unconfirmed CLAIM')

        receipts = public_card.get('source_receipt_sha256', {})
        for rel in ('evidence/preplacement_stop_20261025_arena.json',
                    'evidence/arena_current_primary_witness_20261025.json'):
            path = root / rel
            if receipts.get(rel) != sha256_file(path):
                errors.append(f'current source-receipt hash mismatch: {rel}')
        if public_card.get('preflight_receipt') != 'evidence/preplacement_stop_20261025_arena.json':
            errors.append('public run card must link the active pre-placement receipt')
        for key in ('review_document', 'hypothesis_document'):
            rel = public_card.get(key)
            if not isinstance(rel, str) or not (root / rel).is_file():
                errors.append(f'current public run-card document missing: {key}')
        return errors
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return [f'invalid published readiness audit: {exc}']


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--witness', type=Path, default=DEFAULT_WITNESS)
    parser.add_argument('--fetch-witness', action='store_true')
    parser.add_argument('--output', type=Path, required=True,
                        help='New JSON path; existing receipts are never overwritten.')
    args = parser.parse_args(argv)
    try:
        if args.output.exists():
            raise ValueError('output already exists; choose a new receipt path')
        if args.fetch_witness:
            cache = (ROOT / '.cache').resolve()
            if not args.witness.resolve().is_relative_to(cache):
                raise ValueError('network downloads must stay under ignored .cache/')
            fetch_witness(args.witness)
        card = audit(ROOT, args.witness)
        text = json.dumps(card, indent=2, allow_nan=False) + '\n'
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as dest:
            dest.write(text)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'INCONCLUSIVE — DO NOT SUBMIT: {exc}', file=sys.stderr)
        return 2
    print(f'CONFIRMED DUPLICATE STOP — DO NOT SUBMIT. Receipt: {args.output}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
