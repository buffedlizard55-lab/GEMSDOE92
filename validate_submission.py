#!/usr/bin/env python3
"""Validate format and explain the current rejection-only decision.

A format pass is not upload clearance. The current registry pre-placement
stop applies even if a run card is edited to say ``promote``. This command
never selects a weekly submission slot or returns success as an authorization;
it exits 1 for DO NOT SUBMIT and 2 for inconclusive/invalid input. A future
selector requires a separately authorized protocol and fresh evidence. No
score or organizer-acceptance forecast is made.
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
        if not isinstance(card, dict):
            raise ValueError("run card must be a JSON object")
        try:
            digest = sha256_file(candidate)
        except OSError:
            digest = None
        bound = (
            digest is not None and card.get("raster_sha256") == digest
            and (ROOT / card["submission_file"]).resolve() == candidate.resolve()
        )
        if not bound:
            print("DO NOT SUBMIT: this file is not the byte-bound run-card primary; no clearance evidence describes it.")
        elif card.get("verdict") != "negative":
            # Do not rely on all({}.values()), truthy strings, or a forged
            # promotion flag. The separately verified dense-witness stop is
            # binding regardless of this historical run card's contents.
            print("DO NOT SUBMIT: current literal registry stop blocks promotion; a run-card verdict cannot override it.")
        else:
            reasons = card.get("blocking_reasons")
            if not isinstance(reasons, list) or not all(isinstance(x, str) for x in reasons):
                reasons = []
            print(f"DO NOT SUBMIT: verdict=negative; " + "; ".join(reasons))
        return 1
    except (OSError, ValueError, KeyError, TypeError, rasterio.errors.RasterioError) as exc:
        print(f"INCONCLUSIVE / DO NOT SUBMIT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
