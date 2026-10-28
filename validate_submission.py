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


def _card_sha(card: dict):
    raster = card.get("raster")
    if isinstance(raster, dict) and isinstance(raster.get("sha256"), str):
        return raster["sha256"]
    return card.get("raster_sha256")


def _card_file(card: dict):
    raster = card.get("raster")
    rel = card.get("submission_file")
    if rel is None and isinstance(raster, dict):
        rel = raster.get("file")
    return rel if isinstance(rel, str) else None


def bound_cards(candidate: pathlib.Path, root: pathlib.Path) -> list[tuple[pathlib.Path, dict]]:
    """Run cards whose SHA-256 AND file path both name this exact candidate.

    IR-1028B-1 (2026-10-28): the old check read only evidence/vario_run_card.json,
    so every newer file was reported as unbound. Matching is now candidate-relative.
    """
    try:
        digest = sha256_file(candidate)
    except OSError:
        return []  # unreadable file: no card can bind it; caller still says DO NOT SUBMIT
    found = []
    seen = set()
    for pattern in ("evidence/*run_card*.json", "docs/downloads/*run_card*.json"):
        for path in sorted(root.glob(pattern)):
            if path in seen:
                continue
            seen.add(path)
            try:
                card = json.loads(path.read_text())
            except (OSError, ValueError):
                continue
            if not isinstance(card, dict) or _card_sha(card) != digest:
                continue
            rel = _card_file(card)
            if rel is None or (root / rel).resolve() != candidate.resolve():
                continue
            found.append((path, card))
    return found


def clearance_message(candidate: pathlib.Path, root: pathlib.Path) -> str:
    """Always a rejection. A format pass and a run-card verdict never grant a slot."""
    cards = bound_cards(candidate, root)
    if not cards:
        return ("DO NOT SUBMIT: no run card is byte-bound to this file (SHA-256 and path); "
                "no clearance evidence describes it.")
    lines = []
    for path, card in cards:
        verdict = card.get("verdict")
        reasons = card.get("blocking_reasons")
        if not isinstance(reasons, list) or not all(isinstance(x, str) for x in reasons):
            reasons = []
        detail = "; ".join(reasons) if reasons else "no blocking_reasons recorded in the card"
        lines.append(f"  card {path.relative_to(root)}: verdict={verdict!r} "
                     f"submission_eligible={card.get('submission_eligible')!r} ({detail})")
    if all(card.get("verdict") == "negative" for _, card in cards):
        head = "DO NOT SUBMIT: verdict=negative in every bound run card."
    else:
        head = ("DO NOT SUBMIT: the current literal registry stop and holdout gates still apply; "
                "a run-card verdict cannot override them.")
    return head + "\n" + "\n".join(lines)


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
        print(clearance_message(candidate, ROOT))
        return 1
    except (OSError, ValueError, KeyError, TypeError, rasterio.errors.RasterioError) as exc:
        print(f"INCONCLUSIVE / DO NOT SUBMIT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
