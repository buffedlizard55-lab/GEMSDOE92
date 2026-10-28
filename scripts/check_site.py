#!/usr/bin/env python3
"""Fail closed if the published site (v3, 2026-10-27) is stale, inconsistent or unsafe.

Contract
--------
* docs/index.html, docs/how-to-submit.html, docs/nine-sites.html, index.html and the
  two status JSON feeds are byte-identical to ``scripts/render_site_v3.render()``
  (pages are generated from evidence only; no hand-edited claims).
* docs/index.html declares exactly one ``data-primary="true"`` local
  ``downloads/*-zeros.tif``; the file exists and passes the shared format gates
  (submission encoding: all finite, [0,1], zeros outside the footprint, CRS/shape/
  transform equal to the sample, zero mass on mapped faults) and gems57 validate.
* Its per-file audit and run card are bound to the exact bytes (SHA-256), agree
  on the verdict, and the page says OK TO SUBMIT iff the verdict is ``promote``.
* Every served ``docs/downloads/*-zeros.tif`` passes the format gates and is
  linked from docs/index.html or docs/archive.html.
The legacy (literal-stop) checker is preserved as scripts/check_site_legacy_20261026.py.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402

from gems.gates import run_gates, summarise  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57.validate import assert_submittable, validate  # noqa: E402

DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"
INDEX = DOCS / "index.html"
ARCHIVE = DOCS / "archive.html"
SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
LABELS = ROOT / "data" / "bridge" / "labels.tif"


class _Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.primaries = []

    def handle_starttag(self, tag, attrs):
        if tag == "a" and ("data-primary", "true") in attrs:
            self.primaries.append(dict(attrs))


def primary_download(html: str, problems: list[str]) -> str | None:
    p = _Anchors(); p.feed(html)
    if len(p.primaries) != 1:
        problems.append("index.html must declare exactly one data-primary=true download")
        return None
    href = p.primaries[0].get("href", "")
    if not re.fullmatch(r"downloads/[A-Za-z0-9_.-]+-zeros\.tif", href):
        problems.append("primary must be a local downloads/*-zeros.tif file")
        return None
    return href


def _audit_path(tif: Path) -> Path:
    for name in (tif.stem + "-audit.json", tif.name[: -len("-zeros.tif")] + "-audit.json"):
        p = tif.with_name(name)
        if p.is_file():
            return p
    return tif.with_name(tif.stem + "-audit.json")


def check_rendered(problems: list[str]) -> None:
    try:
        import render_site_v3
        for path, text in render_site_v3.render().items():
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                problems.append(f"stale generated page: {path.relative_to(ROOT)} (run scripts/render_site_v3.py)")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        problems.append(f"site evidence invalid: {exc}")


def check_primary(html: str, problems: list[str]) -> None:
    rel = primary_download(html, problems)
    if not rel:
        return
    tif = DOCS / rel
    if not tif.is_file():
        problems.append(f"primary {rel} does not exist")
        return
    digest = sha256_file(tif)
    audit = json.loads(_audit_path(tif).read_text(encoding="utf-8")) if _audit_path(tif).is_file() else {}
    if not audit:
        problems.append("primary per-file audit missing")
        return
    if audit.get("sha256_zeros") != digest:
        problems.append("primary audit sha256 != primary bytes")
    if audit.get("overall_pass") is not True:
        problems.append("primary audit does not record overall_pass == true")
    rows = audit.get("gates_zeros")
    if not isinstance(rows, list) or not rows or any(r.get("ok") is not True for r in rows):
        problems.append("primary audit gates missing or failing")
    card_path = ROOT / str(audit.get("run_card", ""))
    if not card_path.is_file():
        problems.append("primary run card missing")
        return
    card = json.loads(card_path.read_text(encoding="utf-8"))
    if card.get("raster_sha256") != digest:
        problems.append("run card sha256 != primary bytes")
    verdict = card.get("verdict")
    if verdict not in ("promote", "negative"):
        problems.append("run card verdict must be promote or negative")
    if audit.get("verdict") != verdict or audit.get("submission_eligible") is not card.get("submission_eligible"):
        problems.append("audit and run card disagree on verdict/eligibility")
    for key in ("hypothesis", "mechanism", "named_non_fault_mimic", "holdout_dti", "uniqueness",
                "validator_output", "submission_name", "note"):
        if key not in card:
            problems.append(f"run card missing required field: {key}")
    if not 0 < len(card.get("note", "")) <= 140:
        problems.append("run card note must be 1..140 characters")
    box = html.split('id="submit-now"', 1)[-1].split("</section>", 1)[0]
    # The user protocol requires BOTH holdout improvement and the literal
    # registry checks. A model projection or PI-1 reinterpretation is not a waiver.
    if verdict == "promote" or card.get("submission_eligible") is True:
        gates = card.get("gates_passed", {})
        if gates.get("catalogue_holdout_beats_r0_recipe") is not True:
            problems.append("promotion forbidden: required holdout improvement not established")
        if card.get("uniqueness", {}).get("literal_reading", {}).get("duplicate_under_literal") is not False:
            problems.append("promotion forbidden: literal uniqueness not established")
    if verdict == "promote" and card.get("submission_eligible") is True:
        if "OK TO SUBMIT" not in box or "DO NOT SUBMIT" in box:
            problems.append("eligible primary is not clearly marked OK TO SUBMIT")
    elif "DO NOT SUBMIT" not in box or "OK TO SUBMIT" in box:
        problems.append("non-eligible primary is not clearly marked DO NOT SUBMIT")
    cur = json.loads((DOWNLOADS / "current_submission.json").read_text(encoding="utf-8"))
    rdy = json.loads((DOWNLOADS / "readiness.json").read_text(encoding="utf-8"))
    if cur.get("file") != f"docs/{rel}" or rdy.get("file") != rel:
        problems.append("status JSON files do not point at the primary")
    if cur.get("sha256") != digest or rdy.get("raster_sha256") != digest:
        problems.append("status JSON SHA-256 != primary bytes")
    if cur.get("ok_to_submit") is not rdy.get("submission_eligible") or cur.get("ok_to_submit") is not card.get("submission_eligible"):
        problems.append("status JSON eligibility disagrees with run card")
    if cur.get("submission_name") != card.get("submission_name") or rdy.get("note") != card.get("note"):
        problems.append("status JSON name/note disagree with run card")
    print(f"  PRIMARY {tif.name} sha256 {digest[:16]}… verdict={verdict}")


def check_served(html: str, problems: list[str]) -> int:
    archive = ARCHIVE.read_text(encoding="utf-8") if ARCHIVE.is_file() else ""
    served = sorted(DOWNLOADS.glob("*-zeros.tif"))
    if not served:
        problems.append("no zeros-outside rasters in docs/downloads")
    with rasterio.open(SAMPLE) as ds:
        footprint = np.isfinite(ds.read(1))
    with rasterio.open(LABELS) as ds:
        cat = ds.read(1) > 0.5
    for path in served:
        if f"downloads/{path.name}" not in html and f"downloads/{path.name}" not in archive:
            problems.append(f"{path.name} is served but linked from neither index.html nor archive.html")
        ok, report = summarise(run_gates(str(path), str(SAMPLE), str(LABELS), prune_radius=2,
                                         require_submission_encoding=True))
        if not ok:
            problems.append(f"{path.name}: gates failed\n{report}")
            continue
        with rasterio.open(path) as ds:
            a = ds.read(1)
        if not np.isfinite(a).all() or a.min() < 0 or a.max() > 1:
            problems.append(f"{path.name}: values outside [0,1] or non-finite")
        if np.any((a > 0) & ~footprint):
            problems.append(f"{path.name}: mass outside footprint")
        if np.any(a[cat] > 0):
            problems.append(f"{path.name}: mass on catalogue")
        try:
            assert_submittable(validate(path, footprint, cat))
        except AssertionError as exc:
            problems.append(f"{path.name}: {exc}")
    return len(served)


def main() -> int:
    problems: list[str] = []
    if not INDEX.is_file():
        print("FAIL: docs/index.html missing")
        return 2
    check_rendered(problems)
    html = INDEX.read_text(encoding="utf-8")
    howto = (DOCS / "how-to-submit.html").read_text(encoding="utf-8") if (DOCS / "how-to-submit.html").is_file() else ""
    for needle in ("How to submit", "CLAIM", "MODEL", "HOLDOUT-DTI", "OK TO DOWNLOAD" if False else "Download"):
        if needle not in html:
            problems.append(f"index.html missing {needle!r}")
    if "Predicted values must be in range [0, 1]" not in howto:
        problems.append("how-to-submit.html must explain the portal range error")
    if not re.search(r"(3 per week|weekly limit)", html + howto, re.I):
        problems.append("no weekly-slot caution")
    ids = re.findall(r'\bid="([^"]+)"', html)
    if len(ids) != len(set(ids)):
        problems.append("index.html contains duplicate element ids")
    check_primary(html, problems)
    n = check_served(html, problems)
    if problems:
        print("SITE CHECK FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print(f"SITE CHECK PASS ({n} served raster(s) gated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
