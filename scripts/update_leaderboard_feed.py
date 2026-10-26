#!/usr/bin/env python3
"""Disabled: organizer terms prohibit automated website monitoring/copying.

Do not fetch, parse, mirror, or schedule DrivenData leaderboard data with this
entry point. An explicit permitted access mechanism and authorization would be
needed before designing any replacement. Public status pages link to the source.
"""
from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    print(
        "STOP: DrivenData terms prohibit automated website monitoring; "
        "leaderboard feed disabled (https://www.drivendata.org/termsofuse/).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
