#!/usr/bin/env python3
"""Compatibility entry point for current readiness, not an organizer validator.

Uses the same byte-bound shared checks as the site. Exit 1 means blocked (even
when local format checks pass); no exception may be converted to clearance.
For format-only checks of another file use ``python -m gems validate``.
"""
import json
import sys
from scripts.render_readiness import build_status


def main() -> int:
    try:
        status = build_status()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'VALIDATION FAILED: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(status, indent=2, allow_nan=False))
    print(status['submission_status'])
    # This entry point provides no selector/weekly-cap authorization mechanism.
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
