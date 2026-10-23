#!/usr/bin/env python3
"""Read-only MASS preflight; rebuild R0 but never create candidate variants."""
import csv
import json
import subprocess
from pathlib import Path

import build_prune_rungs as rebuild

ROOT = Path(__file__).resolve().parents[1]


def main():
    inputs = {}
    verified = []
    manifest = ROOT / 'registry/session_manifest.json'
    for entry in json.loads(manifest.read_text())['files']:
        if entry['id'] == 'training_features':
            continue  # unused: no candidate or physical prior is built
        path = ROOT / entry['local_path']
        assert path.stat().st_size == entry['bytes'], entry['id']
        assert rebuild.sha256_file(path) == entry['sha256'], entry['id']
        inputs[entry['id']] = path
        verified.append(entry['id'])
    foot, cat, distance, _, parent = rebuild.build_parent(inputs)
    rows = list(csv.DictReader((ROOT / 'ledger/submissions.csv').open()))
    report = {
        'date': '2026-10-23', 'axis': 'MASS', 'status': 'BLOCKED',
        'git_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'manifest_sha256': rebuild.sha256_file(manifest),
        'verified_inputs': verified,
        'unused_input_not_restored': 'training_features',
        'parent_rebuilt_sha256': parent['parent_hashes'],
        'parent_count': int(parent['r0'].sum()),
        'parent_dots_below_3px': int((parent['r0'] & (distance < 3)).sum()),
        'parent_dots_at_or_below_3px': int((parent['r0'] & (distance <= 3)).sum()),
        'existing_mass_values': [r['value'] for r in rows if r['parent'] == rebuild.PARENT_ID and r['axis'] == 'MASS'],
        'blockers': ['Requested MASS doses already built; do not repeat.',
                     'Parent ranking missing; binary H19-5 is not a ranking.',
                     'R0 retains dots below 3px; repairing their positions adds PRUNE to MASS.'],
        'variants_built': 0, 'submissions': 0,
    }
    (ROOT / 'evidence/mass_preflight.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
