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
        try:
            digest = sha256_file(candidate)
        except OSError:
            digest = None

        # Prefer the artifact's adjacent run card so a newer candidate is not
        # accidentally described by an unrelated historical card. Retain the
        # old VARIO card only as compatibility fallback for the old CLI contract.
        adjacent_cards = []
        if candidate.name.endswith("-zeros.tif"):
            adjacent_cards.append(candidate.with_name(candidate.name[:-len("-zeros.tif")] + "_run_card.json"))
        adjacent_cards.append(candidate.with_name(candidate.stem + "_run_card.json"))
        card_path = next((p for p in adjacent_cards if p.is_file()), ROOT / "evidence/vario_run_card.json")
        card = json.loads(card_path.read_text())
        if not isinstance(card, dict):
            raise ValueError("run card must be a JSON object")
        card_raster = card.get("submission_file")
        if card_raster is None and isinstance(card.get("raster"), dict):
            card_raster = card["raster"].get("file")
        bound_path = None
        if isinstance(card_raster, str):
            bound_path = Path(card_raster)
            if not bound_path.is_absolute():
                bound_path = ROOT / bound_path
        bound = (digest is not None and card.get("raster_sha256") == digest
                 and bound_path is not None and bound_path.resolve() == candidate.resolve())
        if not bound:
            print(f"DO NOT SUBMIT: no run card byte-bound to {candidate}; format validation is not clearance.")
        elif card.get("verdict") != "negative" or card.get("submission_eligible") is not False:
            # This validator is intentionally not a slot selector, including
            # when a card says promote. A separate current-policy selector is required.
            print("DO NOT SUBMIT: this validator never authorizes a competition slot; a separate selector is required.")
        else:
            reasons = card.get("blocking_reasons")
            if not isinstance(reasons, list) or not all(isinstance(x, str) for x in reasons):
                reasons = []
            detail = "; ".join(reasons) or "candidate run card is negative and submission_eligible=false"
            print(f"DO NOT SUBMIT: byte-bound run card {card_path.name}; verdict=negative; {detail}")
        return 1
    except (OSError, ValueError, KeyError, TypeError, rasterio.errors.RasterioError) as exc:
        print(f"INCONCLUSIVE / DO NOT SUBMIT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
