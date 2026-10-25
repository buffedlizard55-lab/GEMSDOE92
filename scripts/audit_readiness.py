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
        'new_unique_tiff_generated': bool(status.get('new_unique_tiff_generated', False)), 'experiments': int(status.get('experiments_this_session', 0)), 'weekly_slots_used': int(status.get('weekly_slots_used_this_session', 0)),
        'organizer_confirmed_score': None,
        'limitations': status.get('blocking_reasons', []),
        'input_sha256': status.get('input_sha256') or {
            'data/bridge/sample_submission.tif': hashlib.sha256(
                (root / 'data/bridge/sample_submission.tif').read_bytes()).hexdigest()},
        'audit_implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def check_published_audit(root: Path = ROOT) -> list[str]:
    """Bind the published review48 receipt to the bytes it itself records.

    Historical semantics (VARIO integration, 2026-10-25): review48 was
    generated against the then-current LISTRICLOQO primary.  The current
    primary is now decided by the VARIO run card (scripts/check_site.py
    verifies that binding separately), so this receipt is checked for
    *internal* consistency only: its recorded file must still hash to its
    recorded SHA-256, its recorded gates must all pass, it must stay
    rejection-only, and the pinned dense-witness literal STOP must be
    preserved.  It can never grant clearance.
    """
    try:
        from scripts.render_readiness import rejection_proof_errors
        card = json.loads((root / 'docs/downloads/review48_run_card.json').read_text())
        expected = {
            'schema': 'gemsdoe92-readiness-audit-v1',
            'verdict': 'negative', 'submission_eligible': False,
            'new_unique_tiff_generated': False, 'experiments': 0, 'weekly_slots_used': 0,
            'organizer_confirmed_score': None, 'format_pass': True,
        }
        errors = [f'published readiness audit mismatch: {key}' for key, value in expected.items()
                  if type(card.get(key)) is not type(value) or card.get(key) != value]
        primary = root / card['primary_download']
        if hashlib.sha256(primary.read_bytes()).hexdigest() != card['raster_sha256']:
            errors.append('published readiness audit raster SHA-256 is stale')
        rows = card.get('validator_output')
        if not isinstance(rows, list) or not rows or any(
                not isinstance(r, dict) or r.get('ok') is not True for r in rows):
            errors.append('published readiness audit validator rows must all pass')
        if not isinstance(card.get('note'), str) or not 0 < len(card['note']) <= 140:
            errors.append('published readiness audit note must contain 1..140 characters')
        impl = card.get('audit_implementation_sha256')
        if not isinstance(impl, str) or len(impl) != 64:
            errors.append('published readiness audit implementation hash malformed')
        registry = card['correlation_overlap_vs_registry']
        if (registry['forward_overlap_for_any_nonempty_in_footprint_candidate'] != 1.0
                or registry['rank_correlation'] is not None
                or registry['overlap_threshold'] != 0.70):
            errors.append('published audit must preserve literal overlap STOP and unmeasured rank')
        proof = registry['preplacement_proof']
        errors.extend(rejection_proof_errors(proof, card['input_sha256'][
            'data/bridge/sample_submission.tif']))
        if len(str(proof.get('implementation_sha256', ''))) != 64:
            errors.append('published pre-placement proof implementation hash malformed')
        holdout = card['holdout_dti']
        if any(holdout[key] is not None for key in (
                'value', 'ci95', 'evaluator_version', 'withheld_positives')):
            errors.append('rejection-only audit cannot claim a holdout measurement')
        if not (root / 'docs/review48.html').is_file():
            errors.append('published audit review page is missing')
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
