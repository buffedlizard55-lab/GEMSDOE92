#!/usr/bin/env python3
"""Compatibility shim: readiness is rendered from the VARIO run card.

Keeps the still-true pinned dense-witness proof validator
(:func:`rejection_proof_errors` — the literal positive-support reading does
give overlap 1.0 for any non-empty raster, and the VARIO run card discloses
it) and the historical note-alias helper.  Status building/rendering now
delegates to scripts/render_vario_status; the previous implementation
asserted no new raster could exist, which the VARIO session falsified by
generating and gate-validating new TIFFs.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor"))

from scripts.preflight_dense_witness import SAMPLE_SHA256, WITNESS_SHA256, WITNESS_BLOB  # noqa: E402

PAGES = ("index.html", "executive-summary.html", "SUBMIT.html")
START = "<!-- VARIO-STATUS:BEGIN -->"
END = "<!-- VARIO-STATUS:END -->"
ARCHIVE_START = '<details id="historical-research-archive"><summary>Historical experiments and downloads — not current clearance</summary>'
ARCHIVE_END = "<!-- HISTORICAL-ARCHIVE:END -->"


def rejection_proof_errors(proof: dict, sample_sha: str) -> list[str]:
    """Validate the pinned proof's identity and literal-rejection semantics."""
    expected = {
        "schema": "gemsdoe92-preplacement-stop-v2",
        "sample_sha256": SAMPLE_SHA256,
        "sha256": WITNESS_SHA256,
        "git_blob_sha": WITNESS_BLOB,
        "grid_checks_pass": True,
        "footprint_pixels": 5167373,
        "positive_in_footprint": 5167373,
        "universal_nonempty_in_footprint_overlap_stop": True,
        "forward_overlap_for_any_nonempty_in_footprint_dot_set": 1.0,
        "threshold": 0.70,
        "verdict": "negative",
        "submission_eligible": False,
    }
    errors = []
    for key, value in expected.items():
        got = proof.get(key)
        if type(got) is not type(value) or got != value:
            errors.append(f"rejection receipt mismatch: {key}")
    if sample_sha != SAMPLE_SHA256:
        errors.append("sample bytes differ from pinned rejection footprint")
    return errors


def form_note(card: dict) -> str:
    """Accept the two historical schemas, but never hide conflicting aliases."""
    notes = [card[k] for k in ("note", "submission_note") if k in card]
    if (not notes or any(not isinstance(n, str) or not 0 < len(n) <= 140 for n in notes)
            or len(set(notes)) != 1):
        raise ValueError("primary note must contain 1–140 characters; aliases must agree")
    return notes[0]


def build_status(root: Path = ROOT) -> dict:
    from scripts.render_vario_status import load_card, readiness
    return readiness(load_card(root))


def panel(status: dict) -> str:
    from scripts.render_vario_status import load_card, panel_html
    card = load_card(ROOT)
    st = status if status.get("raster_sha256") == card["raster_sha256"] else None
    if st is None:
        raise ValueError("status does not describe the current VARIO primary")
    return panel_html(card, st)


def render_page(text: str, block: str) -> str:
    """Place ``block`` first in <body>, replacing any prior VARIO block (idempotent)."""
    body = re.search(r"(<body\b[^>]*>)(.*?)(</body>)", text, flags=re.S)
    if body is None:
        raise ValueError("missing body")
    content = body[2]
    if START in content or END in content:
        if content.count(START) != 1 or content.count(END) != 1:
            raise ValueError("ambiguous VARIO status markers")
        content = re.sub(re.escape(START) + r".*?" + re.escape(END), "", content, flags=re.S)
    content = content.strip("\n")
    return text[:body.start()] + body[1] + "\n" + block + "\n" + content + "\n" + body[3] + text[body.end():]


def sync(root: Path = ROOT, *, check: bool = False) -> list[str]:
    from scripts.render_vario_status import check as _check, render as _render
    if check:
        out = _render(root, write=False)
        return list(out["stale"])
    out = _render(root, write=True)
    return list(out["stale"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        stale = sync(check=args.check)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"READINESS FAIL: {exc}", file=sys.stderr)
        return 1
    if args.check and stale:
        print("READINESS FAIL: stale current status: " + ", ".join(stale))
        return 1
    print("READINESS PASS: current VARIO status revalidated from bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
