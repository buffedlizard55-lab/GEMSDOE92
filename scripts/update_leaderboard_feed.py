#!/usr/bin/env python3
"""Refresh an explicitly dated public-leaderboard feed; never infer a receipt.

The Pages deployment runs this against the official unauthenticated leaderboard.
Failures or page-layout changes produce an explicit unavailable state, not a stale
or guessed score. This has no connection to promotion or submission decisions.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import sys
from urllib import request
from urllib.parse import urlsplit

URL = "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"
MAX_BYTES = 2_000_000


class Tables(HTMLParser):
    """Collect text cells from top-level HTML tables without executing markup."""
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.table: list[list[str]] | None = None
        self.row: list[str] | None = None
        self.cell: list[str] | None = None
        self.tables: list[list[list[str]]] = []
        self.ignored = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self.ignored += 1
        if tag == "table":
            self.depth += 1
            if self.depth == 1:
                self.table = []
        elif self.depth == 1 and tag == "tr":
            self.row = []
        elif self.depth == 1 and tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif self.cell is not None and tag in ("br", "p", "div"):
            self.cell.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style") and self.ignored:
            self.ignored -= 1
        if self.depth == 1 and tag in ("td", "th") and self.cell is not None:
            if self.row is not None:
                self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif self.depth == 1 and tag == "tr" and self.row is not None:
            if self.table is not None:
                self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.depth:
            if self.depth == 1 and self.table is not None:
                self.tables.append(self.table)
                self.table = None
            self.depth -= 1

    def handle_data(self, data: str) -> None:
        if self.cell is not None and not self.ignored and self.depth == 1:
            self.cell.append(data)


def parse_public_leader(html: str) -> float:
    """Require the official table headers and exactly one numeric rank-one row."""
    parser = Tables()
    parser.feed(html)
    found: list[float] = []
    for table in parser.tables:
        for header_i, header in enumerate(table):
            norm = [re.sub(r"[^a-z0-9]", "", h.lower()) for h in header]
            ranks = [i for i, h in enumerate(norm) if h == "rank"]
            participants = [i for i, h in enumerate(norm) if h == "participant"]
            scores = [i for i, h in enumerate(norm) if "public" in h and "dwtversky" in h]
            if len(ranks) != 1 or len(participants) != 1 or len(scores) != 1:
                continue
            ri, si = ranks[0], scores[0]
            for row in table[header_i + 1:]:
                if len(row) <= max(ri, si) or not re.fullmatch(r"#?\s*1", row[ri]):
                    continue
                if not re.fullmatch(r"(?:0(?:\.\d+)?|1(?:\.0+)?)", row[si]):
                    raise ValueError("rank-one score is not a plain probability")
                value = float(row[si])
                if not math.isfinite(value) or not 0 <= value <= 1:
                    raise ValueError("rank-one score outside [0,1]")
                found.append(value)
    if len(found) != 1:
        raise ValueError("official leaderboard table missing or ambiguous")
    return found[0]


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # A login or cross-host redirect is not the leaderboard.


def fetch_html() -> str:
    req = request.Request(URL, headers={"User-Agent": "GEMSDOE92-public-status/1.0"})
    opener = request.build_opener(NoRedirect())
    with opener.open(req, timeout=20) as response:
        final = urlsplit(response.geturl())
        expected = urlsplit(URL)
        if (final.scheme, final.netloc, final.path) != (expected.scheme, expected.netloc, expected.path):
            raise ValueError("unexpected redirect away from leaderboard")
        if response.status != 200:
            raise ValueError("leaderboard HTTP response not successful")
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("leaderboard page exceeds size limit")
    return data.decode("utf-8", errors="replace")


def make_feed(fetch=fetch_html, *, now: datetime | None = None) -> dict:
    checked = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
    base = {
        "schema": "gemsdoe92-official-leaderboard-feed-v1",
        "source": URL,
        "checked_at_utc": checked,
        "rank": None,
        "public_dw_tversky": None,
        "provenance": "Official public leaderboard snapshot, not a project submission receipt.",
    }
    try:
        value = parse_public_leader(fetch())
    except Exception as exc:  # Network and upstream markup are untrusted; publish no guessed score.
        base.update(status="unavailable", reason=f"refresh failed ({type(exc).__name__}); consult the official page")
    else:
        base.update(status="ok", rank=1, public_dw_tversky=value)
    return base


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args(argv)
    data = make_feed()
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"feed could not be written: {exc}", file=sys.stderr)
        return 1
    print(f"leaderboard feed: {data['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
