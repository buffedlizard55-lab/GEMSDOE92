#!/usr/bin/env python3
"""Reproduce repository checks and a rejection-only submission audit in one command.

Exit 1: engineering checks passed, but confirmed protocol STOP (DO NOT SUBMIT).
Exit 2: incomplete/failed audit (DO NOT SUBMIT). Never exits with clearance.
No training, geological experiment, candidate creation, leaderboard access or slot
selection. Only --fetch-witness permits network access, via the existing pinned
GitHub witness fetcher. Logs stay in the receipt, not a separate private evaluator.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.audit_readiness import DEFAULT_WITNESS, audit, fetch_witness  # noqa: E402
from scripts.render_readiness import rejection_proof_errors  # noqa: E402


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checks(python: str) -> list[tuple[str, list[str]]]:
    """Fixed read-only checks; no arbitrary shell commands or model runners."""
    return [
        ('tests', [python, '-m', 'pytest', 'tests', '-q']),
        ('manifest', [python, '-m', 'gems', 'manifest', '--manifest',
                      'registry/data_manifest.json', '--data-root', 'data']),
        ('parent', [python, '-m', 'gems', 'parent', '--recipe',
                    'registry/parents/R0.json', '--data-root', 'data']),
        ('site', [python, 'scripts/check_site.py']),
        ('focus9_page', [python, 'scripts/render_focus9_page.py', '--check']),
        ('review_14f85876', [python, 'scripts/render_review_14f85876.py', '--check']),
        ('review_b4bb558b', [python, 'scripts/render_review_b4bb558b.py', '--check']),
        ('review_banner', [python, 'scripts/render_review_banner.py', '--check']),
        ('whitespace', ['git', 'diff', '--check', 'HEAD', '--']),
    ]


def run_check(name: str, argv: list[str], root: Path, timeout: int = 900) -> dict:
    """Capture actual exits; kill the child process group if its budget expires."""
    start = time.monotonic()
    timed_out = False
    try:
        with subprocess.Popen(argv, cwd=root, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, start_new_session=True) as proc:
            try:
                stdout, stderr = proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                stdout, stderr = proc.communicate()
            code = proc.returncode
    except OSError as exc:
        code, stdout, stderr = None, b'', str(exc).encode('utf-8')
    return {
        'name': name, 'argv': argv, 'returncode': code,
        'timed_out': timed_out, 'passed': code == 0 and not timed_out,
        'elapsed_seconds': round(time.monotonic() - start, 3),
        'stdout_sha256': sha256(stdout), 'stderr_sha256': sha256(stderr),
        'stdout_tail': stdout[-4096:].decode('utf-8', errors='replace'),
        'stderr_tail': stderr[-4096:].decode('utf-8', errors='replace'),
    }


def validate_stop(card: dict) -> None:
    """Do not promote a truthy/malformed/stale audit to a confirmed rejection."""
    if (card.get('schema') != 'gemsdoe92-readiness-audit-v1'
            or card.get('submission_eligible') is not False
            or card.get('verdict') != 'negative'
            or card.get('new_unique_tiff_generated') is not False
            or type(card.get('experiments')) is not int or card['experiments'] != 0
            or type(card.get('weekly_slots_used')) is not int or card['weekly_slots_used'] != 0):
        raise ValueError('unexpected rejection audit semantics')
    proof = card['correlation_overlap_vs_registry']['preplacement_proof']
    errors = rejection_proof_errors(proof, card['input_sha256'][
        'data/bridge/sample_submission.tif'])
    if errors:
        raise ValueError('; '.join(errors))


def review(root: Path, witness: Path, python: str, budget_seconds: int = 1800) -> dict:
    start = time.monotonic()
    # Check the binding STOP first. Engineering verification is not an experiment
    # and may continue after it; no surface or placement code is invoked.
    card = audit(root, witness)
    validate_stop(card)
    rows = []
    plan = checks(python)
    for name, argv in plan:
        remaining = int(budget_seconds - (time.monotonic() - start))
        if remaining <= 0:
            break
        rows.append(run_check(name, argv, root, timeout=min(900, remaining)))
    complete = len(rows) == len(plan)
    passed = complete and all(row['passed'] is True for row in rows)
    historical = {key: card.pop(key) for key in (
        'primary_download', 'raster_sha256', 'validator_output', 'format_pass',
        'submission_name', 'note', 'artifact_role',
    )}
    historical['status'] = 'existing research file only; DO NOT SUBMIT'
    return {
        **card,
        'schema': 'gemsdoe92-project-review.v1',
        'raster_sha256': None,
        'validator_output': {'status': 'not_run', 'reason': 'No new candidate generated; existing research bytes were revalidated separately.'},
        'format_pass': None,
        'submission_name': None,
        'note': 'Protocol audit only; no new TIFF, holdout or slot. DO NOT SUBMIT.',
        'historical_research_reference': historical,
        'reviewed_utc': datetime.now(timezone.utc).isoformat(),
        'review_implementation_sha256': sha256(Path(__file__).read_bytes()),
        'engineering_checks': rows,
        'engineering_checks_complete': complete,
        'engineering_checks_passed': passed,
        'engineering_budget_seconds': budget_seconds,
        'audit_status': 'confirmed_stop' if passed else 'checks_failed_or_incomplete',
        'score_estimate': None,
        'score_estimate_reason': 'No calibrated organizer-score estimate or organizer receipt.',
        'new_submission_name': None,
        'new_submission_note': None,
        'historical_identity_warning': 'submission_name, note and raster_sha256 identify an existing research file, not a new submission.',
        'official_sources_live_verified': False,
        'verdict': 'negative',
        'submission_eligible': False,
    }


def write_receipt(path: Path, card: dict) -> None:
    """Install a complete JSON receipt atomically without replacing prior evidence."""
    text = json.dumps(card, indent=2, allow_nan=False) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        staged = Path(stream.name)
        try:
            stream.write(text.encode('utf-8'))
            stream.flush()
            os.fsync(stream.fileno())
            os.link(staged, path)
        finally:
            staged.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='Fresh JSON path; never overwrite a historical receipt.')
    parser.add_argument('--witness', type=Path, default=DEFAULT_WITNESS)
    parser.add_argument('--fetch-witness', action='store_true')
    args = parser.parse_args(argv)
    try:
        # lexists catches dangling symlinks as well as existing files.
        if os.path.lexists(args.output):
            raise ValueError('output already exists; use a fresh receipt path')
        if args.fetch_witness:
            if not args.witness.resolve().is_relative_to((ROOT / '.cache').resolve()):
                raise ValueError('network downloads must stay under ignored .cache/')
            fetch_witness(args.witness)
        card = review(ROOT, args.witness, sys.executable)
        write_receipt(args.output, card)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'INCONCLUSIVE — DO NOT SUBMIT: {exc}', file=sys.stderr)
        return 2
    if card['engineering_checks_passed'] is not True:
        print(f'CHECKS FAILED OR INCOMPLETE — DO NOT SUBMIT. Receipt: {args.output}')
        return 2
    print(f'CHECKS PASSED; CONFIRMED PROTOCOL STOP — DO NOT SUBMIT. Receipt: {args.output}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
