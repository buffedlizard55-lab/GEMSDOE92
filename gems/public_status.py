"""Authoritative byte-bound publication status (VARIO card).

The current pinned full-footprint witness enforces a rejection-only decision;
recorded booleans alone cannot override it. A future policy change requires
new separately reviewed evidence, not an edited historical card.

* the card must be the VARIO run card for the exact primary bytes on disk;
* ``promote`` is rejected, even when every recorded gate is ``True``;
  a ``negative`` verdict requires a failed gate and blocking reasons;
* no organizer score may be present without a receipt (must be ``None``);
* the panel text is rendered by ``scripts.render_vario_status`` from the
  same card, so this module and the site renderer cannot disagree.
"""
from __future__ import annotations

import re
from pathlib import Path

from .rasters import sha256_file

BEGIN = "<!-- VARIO-STATUS:BEGIN -->"
END = "<!-- VARIO-STATUS:END -->"
PAGES = ("index.html", "executive-summary.html", "SUBMIT.html")
GATE_KEYS = ("format", "canary", "holdout_beats_best_control", "operative_uniqueness")
REQUIRED_GATES = {"crs", "shape", "transform", "dtype_and_band", "values_in_0_1",
                  "no_nan_inside_footprint", "submission_encoding", "reread_sha256"}


def validate_status(card: dict, root: Path, primary_rel: str) -> None:
    if not isinstance(card, dict):
        raise ValueError("public status must be an object")
    if not re.fullmatch(r"downloads/[A-Za-z0-9_.-]+-zeros\.tif", str(primary_rel)):
        raise ValueError("unsafe primary path")
    if card.get("lane") != "VARIO":
        raise ValueError("status card must be the VARIO run card")
    if card.get("submission_file") != "docs/" + primary_rel:
        raise ValueError("status must describe the explicit primary, not a sibling")
    if card.get("raster_sha256") != sha256_file(root / "docs" / primary_rel):
        raise ValueError("status raster SHA-256 is stale")
    verdict = card.get("verdict")
    if verdict not in ("promote", "negative"):
        raise ValueError("verdict must be promote or negative")
    if verdict == "promote":
        raise ValueError("literal registry pre-placement STOP blocks promotion")
    gates = card.get("gates")
    if not isinstance(gates, dict) or set(gates) != set(GATE_KEYS) or any(not isinstance(v, bool) for v in gates.values()):
        raise ValueError("gate evidence must be literal booleans for the pre-registered gates")
    if (verdict == "promote") != all(gates.values()):
        raise ValueError("verdict inconsistent with recorded gates")
    if verdict == "negative" and not card.get("blocking_reasons"):
        raise ValueError("negative verdict requires blocking reasons")
    if card.get("submission_eligible") is not False:
        raise ValueError("slot selection is a separate selector step; never granted here")
    if card.get("weekly_slots_used") != 0:
        raise ValueError("this session must record zero weekly slots used")
    if card.get("organizer_confirmed_score") is not None:
        raise ValueError("no organizer score without a receipt")
    rows = card.get("validator_output")
    if not isinstance(rows, list) or not rows or any(
            not isinstance(r, dict) or not isinstance(r.get("name"), str) or r.get("ok") is not True
            for r in rows):
        raise ValueError("status requires passing recorded format gates")
    names = [r["name"] for r in rows]
    if not REQUIRED_GATES.issubset(names) or len(names) != len(set(names)):
        raise ValueError("status format checks missing or duplicated")
    hold = card.get("holdout_dti") or {}
    prim = (hold.get("scores") or {}).get(card.get("primary_arm", ""))
    if hold.get("evidence_class") != "HOLDOUT-DTI" or not prim or not prim.get("withheld_positive_pixels"):
        raise ValueError("missing labelled HOLDOUT-DTI for the primary arm")
    if not isinstance(card.get("note"), str) or not 0 < len(card["note"]) <= 140:
        raise ValueError("status note must contain 1..140 characters")


def render_status(card: dict) -> str:
    from scripts.render_vario_status import panel_html, readiness
    return panel_html(card, readiness(card))


def install_panel(html_text: str, panel: str) -> str:
    if html_text.count(BEGIN) != html_text.count(END) or html_text.count(BEGIN) > 1:
        raise ValueError("ambiguous VARIO status markers")
    if BEGIN in html_text:
        start, tail = html_text.split(BEGIN, 1)
        _, finish = tail.split(END, 1)
        html_text = start + finish
    if html_text.count("<body>") != 1:
        # pages may carry attributes on <body>; fall back to a regex insert,
        # but still require exactly one body element
        matches = list(re.finditer(r"<body\b[^>]*>", html_text))
        if len(matches) != 1:
            raise ValueError("expected exactly one body element")
        m = matches[0]
        return html_text[:m.end()] + "\n" + panel + "\n" + html_text[m.end():].lstrip()
    before, body = html_text.split("<body>", 1)
    return before + "<body>\n" + panel + "\n" + body.lstrip()


def check_panels(card: dict, root: Path, primary_rel: str) -> list[str]:
    problems: list[str] = []
    try:
        validate_status(card, root, primary_rel)
        panel = render_status(card)
        for name in PAGES:
            text = (root / "docs" / name).read_text(encoding="utf-8")
            if text.count(BEGIN) != 1 or text.count(END) != 1 or panel not in text:
                problems.append(f"{name}: authoritative VARIO status missing or stale")
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        problems.append(f"invalid public status: {exc}")
    return problems
