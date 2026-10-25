#!/usr/bin/env python3
"""Compatibility shim: current status is rendered from the VARIO run card.

The rejection-only implementation (review c5e3848c) hard-coded
``new_unique_tiff_generated is False``; the VARIO session generated and
gate-validated new rasters, so that assertion is now false by measurement.
All rendering/checking delegates to scripts/render_vario_status, which is
byte-bound to evidence/vario_run_card.json and fails closed on any
inconsistency.  This module keeps the import surface used by older scripts.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor"))

CARD = "docs/downloads/vario_run_card.json"
BEGIN = "<!-- VARIO-STATUS:BEGIN -->"
END = "<!-- VARIO-STATUS:END -->"
PAGES = ("docs/submit.html", "index.html", "README.md", "SUBMISSION_READY.md")


def load_card(root: Path = ROOT) -> dict:
    from scripts.render_vario_status import load_card as _load
    card = _load(root)
    # legacy field aliases some callers read
    card.setdefault("primary_download", card["submission_file"])
    return card


def panel(card: dict, page: str) -> str:
    from scripts.render_vario_status import panel_html, panel_md, readiness
    st = readiness(card)
    return panel_md(card, st) if page.endswith(".md") else panel_html(card, st)


def render(text: str, block: str, *, markdown: bool) -> str:
    if text.count(BEGIN) != text.count(END) or text.count(BEGIN) > 1:
        raise ValueError("malformed VARIO status markers")
    if BEGIN in text:
        start, end = text.index(BEGIN), text.index(END) + len(END)
        if text.index(END) < start:
            raise ValueError("malformed VARIO status markers: end precedes begin")
        if not markdown:
            return text[:start] + block + text[end:]
        text = text[:start] + text[end:]
    if markdown:
        first, sep, rest = text.partition("\n")
        if not sep or not first.startswith("# "):
            raise ValueError("markdown current status requires a project H1")
        return first + sep + "\n" + block + "\n\n" + rest.lstrip("\n")
    body = re.search(r"<body\b[^>]*>", text, re.I)
    if not body:
        raise ValueError("page has no body")
    return text[:body.end()] + "\n" + block + "\n" + text[body.end():]


def archive_lane_banners(text: str, page: str) -> str:
    """Deprecated no-op: historical banners stay below the VARIO panel."""
    return text


def check(root: Path = ROOT, *, write: bool = False) -> list[str]:
    from scripts.render_vario_status import check as _check, render as _render
    if write:
        _render(root, write=True)
    return _check(root)
