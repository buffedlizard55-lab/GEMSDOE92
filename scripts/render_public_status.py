#!/usr/bin/env python3
"""Render/check the rejection-only status from the current review run card.

Run after any lane renderer: python scripts/render_public_status.py
CI: python scripts/render_public_status.py --check
The raster's format is independently revalidated by scripts/check_site.py.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gems.public_status import PAGES, check_panels, install_panel, render_status, validate_status
from scripts.check_site import primary_download

CARD = ROOT / 'docs/downloads/review797e_run_card.json'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        card = json.loads(CARD.read_text())
        problems = []
        primary = primary_download((ROOT / 'docs/index.html').read_text(), problems)
        if problems or primary is None:
            raise ValueError('; '.join(problems))
        validate_status(card, ROOT, primary)
        if not args.check:
            # Compute every edit first: malformed markers must not partly update the site.
            panel = render_status(card)
            edits = {ROOT / 'docs' / name: install_panel(
                (ROOT / 'docs' / name).read_text(), panel) for name in PAGES}
            for path, text in edits.items():
                path.write_text(text, encoding='utf-8')
        problems = check_panels(card, ROOT, primary)
        if problems:
            raise ValueError('; '.join(problems))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'PUBLIC STATUS FAIL: {exc}', file=sys.stderr)
        return 1
    print('PUBLIC STATUS PASS: primary bytes and first panel agree on all three pages')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
