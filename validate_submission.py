#!/usr/bin/env python3
"""Compatibility check for the historical KNICKLOQO download. Rejection-only.

Uses the shared validator, not a second implementation of the organizer's
validator. A local format pass is not organizer acceptance or slot clearance.
Exit 1: format failure or binding registry stop; exit 2: invalid arguments.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from gems.gates import run_gates, summarise

ROOT = Path(__file__).resolve().parent
DEFAULT = ROOT / 'docs/downloads/h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif'


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', nargs='?', type=Path, default=DEFAULT)
    args = parser.parse_args(argv)
    try:
        gates = run_gates(args.file, ROOT / 'data/bridge/sample_submission.tif',
                          ROOT / 'data/bridge/existing_faults.tif', prune_radius=2,
                          require_submission_encoding=True)
        ok, report = summarise(gates)
        print(report)
    except (OSError, ValueError) as exc:
        print(f'FORMAT CHECK INCONCLUSIVE: {exc}')
        return 1
    print(f'FORMAT-VALIDATION: {"PASS" if ok else "FAIL"}')
    print('DO NOT SUBMIT. The literal full-footprint registry witness binds every '
          'nonempty candidate. No organizer score, acceptance, or promotion is established.')
    # This compatibility command cannot authorize the selector or weekly slot.
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
