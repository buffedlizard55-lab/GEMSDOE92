#!/usr/bin/env python3
"""Validate a candidate and print the byte-bound submission decision.

A format pass is not upload clearance.  The decision is read from the
current run card (evidence/vario_run_card.json) and applies only to the
primary bytes it is hash-bound to: exit 0 only when every format gate
passes AND the card verdict is ``promote`` AND the SHA-256 matches this
file.  Otherwise exit 1 = DO NOT SUBMIT.  No score or organizer-acceptance
forecast is made.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import rasterio

from gems.gates import run_gates, summarise
from gems.rasters import sha256_file
from scripts.check_site import primary_download

ROOT = Path(__file__).resolve().parent


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", nargs="?", type=Path)
    args = parser.parse_args(argv)
    try:
        candidate = args.candidate
        if candidate is None:
            problems = []
            rel = primary_download((ROOT / "docs/index.html").read_text(), problems)
            if problems or rel is None:
                raise ValueError("; ".join(problems))
            candidate = ROOT / "docs" / rel
        results = run_gates(
            str(candidate), str(ROOT / "data/bridge/sample_submission.tif"),
            str(ROOT / "data/bridge/labels.tif"), prune_radius=2,
            require_submission_encoding=True,
        )
        ok, report = summarise(results)
        print(report)
        print("FORMAT PASS (local only)" if ok else "FORMAT FAIL")
        card = json.loads((ROOT / "evidence/vario_run_card.json").read_text())
        try:
            digest = sha256_file(candidate)
        except OSError:
            digest = None
        bound = card.get("raster_sha256") == digest and str(ROOT / card["submission_file"]) == str(candidate)
        if ok and bound and card.get("verdict") == "promote" and all((card.get("gates") or {}).values()):
            print(f"OK TO SUBMIT (selector step still applies): {card['submission_name']}")
            return 0
        if not bound:
            print("DO NOT SUBMIT: this file is not the run-card primary (SHA-256 mismatch); no clearance evidence describes it.")
        else:
            print(f"DO NOT SUBMIT: verdict={card.get('verdict')}; " + "; ".join(card.get("blocking_reasons", [])))
        return 1
    except (OSError, ValueError, KeyError, rasterio.errors.RasterioError) as exc:
        print(f"INCONCLUSIVE / DO NOT SUBMIT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
