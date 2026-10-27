#!/usr/bin/env python3
"""Record GitHub main-ref freshness for the nine pinned research references.

This does NOT fetch a leaderboard, score new files, inspect a Pages deployment,
or establish uniqueness. An unavailable or changed main ref means the pinned
historical inventory may be incomplete. The receipt never grants a submission.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / 'docs/downloads/focus_sites_release_review_20261026.json'
SITES = tuple(f'GEMSDOE{s}' for s in (24, 25, 27, 28, 30, 31, 32, 33, 36))
SHA = re.compile(r'[0-9a-f]{40}\Z')


def github_head(site: str) -> dict:
    """Read exactly one public GitHub commit; never contact DrivenData."""
    if site not in SITES:
        raise ValueError('site is not in the fixed nine-site inventory')
    response = subprocess.run(
        ['gh', 'api', f'repos/buffedlizard55-lab/{site}/commits/main',
         '--jq', '{sha: .sha, commit_date: .commit.committer.date}'],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return json.loads(response.stdout)


def make_receipt(inventory_path: Path = INVENTORY, *,
                 fetch: Callable[[str], dict] = github_head,
                 observed_utc: str | None = None) -> dict:
    raw = inventory_path.read_bytes()
    inventory = json.loads(raw)
    if not isinstance(inventory, dict) or not isinstance(inventory.get('selected_site_artifacts'), list):
        raise ValueError('invalid source inventory')
    records = inventory['selected_site_artifacts']
    if tuple(r.get('site') for r in records if isinstance(r, dict)) != SITES:
        raise ValueError('source inventory must contain the nine sites in order')
    observations = []
    for rec in records:
        site = rec['site']
        pin = rec.get('repository_commit')
        if (rec.get('source_repository') != f'buffedlizard55-lab/{site}'
                or not isinstance(pin, str) or not SHA.fullmatch(pin)):
            raise ValueError(f'invalid pinned repository or commit for {site}')
        current, date, error = None, None, None
        try:
            obj = fetch(site)
            if not isinstance(obj, dict) or not isinstance(obj.get('sha'), str) or not SHA.fullmatch(obj['sha']):
                raise ValueError('GitHub response has no valid commit SHA')
            current = obj['sha']
            date = obj.get('commit_date')
            if date is not None and (not isinstance(date, str) or len(date) > 40):
                raise ValueError('GitHub response has an invalid commit date')
        except (OSError, ValueError, TypeError, json.JSONDecodeError, subprocess.SubprocessError):
            # Do not copy subprocess stderr, which can contain environment
            # details, into a public receipt. A failure is unknown, not fresh.
            current, date, error = None, None, 'GitHub main ref could not be verified'
        observations.append({
            'site': site, 'pinned_commit': pin, 'observed_main_commit': current,
            'observed_main_commit_date': date,
            'status': 'unknown' if current is None else ('unchanged' if current == pin else 'changed'),
            'error': error,
            'pinned_commit_url': f'https://github.com/buffedlizard55-lab/{site}/commit/{pin}',
            'main_url': f'https://github.com/buffedlizard55-lab/{site}/commits/main/',
        })
    return {
        'schema': 'gemsdoe92-github-focus-freshness-v1',
        'evidence_class': 'SOURCE-FRESHNESS (GitHub refs only, not scores)',
        'observed_utc': observed_utc or datetime.now(timezone.utc).isoformat(),
        'inventory_path': 'docs/downloads/focus_sites_release_review_20261026.json',
        'inventory_sha256': hashlib.sha256(raw).hexdigest(),
        'method': 'GitHub commits/main API; comparison of commit identities only',
        'complete': all(row['status'] != 'unknown' for row in observations),
        'changed_count': sum(row['status'] == 'changed' for row in observations),
        'unknown_count': sum(row['status'] == 'unknown' for row in observations),
        'sites': observations,
        'scope_limit': ('A changed ref does not identify changed TIFFs or scores; an unchanged ref does not '
                        'prove a GitHub Pages deployment or complete registry. Neither result grants clearance.'),
        'organizer_confirmed_score': None,
        'submission_eligible': False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path,
                        help='New JSON receipt path; existing receipts are never overwritten.')
    args = parser.parse_args(argv)
    try:
        if args.output.exists():
            raise ValueError('receipt already exists')
        receipt = make_receipt()
        text = json.dumps(receipt, indent=2, allow_nan=False) + '\n'
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as f:
            f.write(text)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f'INCONCLUSIVE — DO NOT SUBMIT: {exc}', file=sys.stderr)
        return 2
    print(f"GitHub ref snapshot: {receipt['changed_count']} changed, {receipt['unknown_count']} unknown; "
          f"never submission clearance. Receipt: {args.output}")
    return 0 if receipt['complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
