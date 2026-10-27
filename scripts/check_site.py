#!/usr/bin/env python3
"""Fail closed if the GitHub Pages download is missing, out of range, or mislabeled.

Rewritten 2026-10-25 when the DILATATION lane merged with the TIPGAP lane. The
previous version hard-coded one lane's filename, sha256 and form note, so it
broke the moment the primary changed -- and it only ever checked that one file
even when several were being served. This version derives the primary from the
page itself and gates **every** served zeros-outside raster, so an orphaned or
out-of-range download cannot ship unnoticed.
"""
from __future__ import annotations

import json
from html.parser import HTMLParser
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402

from gems.gates import run_gates, summarise  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57.validate import assert_submittable, validate  # noqa: E402

DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"
INDEX = DOCS / "index.html"
SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
LABELS = ROOT / "data" / "bridge" / "labels.tif"
N_DOTS = 37654


def read_json_object(path: Path, problems: list[str]) -> dict:
    """Turn absent/malformed evidence into an explicit site failure, not a crash."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            raise ValueError("receipt must be a JSON object")
        return doc
    except (OSError, ValueError) as exc:
        problems.append(f"{path.name}: unreadable JSON receipt: {exc}")
        return {}


def check_recorded_gates(doc: dict, problems: list[str]) -> None:
    """A receipt must enumerate actual gates with literal boolean results.

    Re-reading the TIFF below is still authoritative. This check prevents an
    empty list, truthy string, or malformed row from masquerading as recorded
    validation (or crashing publication with an unhelpful TypeError).
    """
    required = {
        'crs', 'shape', 'transform', 'dtype_and_band', 'values_in_0_1',
        'no_nan_inside_footprint', 'nan_outside_footprint',
        'catalogue_zero_mass', 'distance_from_catalogue', 'reread_sha256',
    }
    rows = doc.get('gates_zeros')
    if not isinstance(rows, list) or not rows:
        problems.append('audit receipt gates_zeros must be a nonempty list')
        return
    names = []
    for row in rows:
        if (not isinstance(row, dict) or not isinstance(row.get('name'), str)
                or not isinstance(row.get('ok'), bool)):
            problems.append('audit receipt contains a malformed gate row')
            continue
        names.append(row['name'])
        if row['ok'] is not True:
            problems.append(f"audit receipt records failing format gate: {row['name']}")
    if len(names) != len(set(names)):
        problems.append('audit receipt contains duplicate gate names')
    missing = required - set(names)
    if missing:
        problems.append(f'audit receipt missing required gates: {sorted(missing)}')


def _audit_path(tif: Path) -> Path:
    """Per-file audit naming: older lanes used ``<stem-minus-zeros>-audit.json``;
    FAULTNET/VARIO use ``<full-stem>-audit.json`` (i.e. ``*-zeros-audit.json``)."""
    for name in (tif.name[:-len("-zeros.tif")] + "-audit.json", tif.stem + "-audit.json"):
        p = tif.with_name(name)
        if p.is_file():
            return p
    return tif.with_name(tif.stem + "-audit.json")


def primary_download(html: str, problems: list[str]) -> str | None:
    """Require one explicit, local primary; never guess from link order."""
    class Anchors(HTMLParser):
        def __init__(self):
            super().__init__()
            self.primaries = []

        def handle_starttag(self, tag, attrs):
            if tag == 'a' and ('data-primary', 'true') in attrs:
                self.primaries.append(attrs)

    parser = Anchors()
    parser.feed(html)
    if len(parser.primaries) != 1:
        problems.append('index.html must declare exactly one data-primary=true download')
        return None
    attrs = parser.primaries[0]
    for name in ('href', 'data-primary'):
        if sum(key == name for key, _ in attrs) != 1:
            problems.append(f'primary anchor must have exactly one {name} attribute')
            return None
    href = dict(attrs)['href']
    if not isinstance(href, str) or not re.fullmatch(r'downloads/[A-Za-z0-9_.-]+-zeros\.tif', href):
        problems.append('primary must be a local downloads/*-zeros.tif file')
        return None
    return href


def check_current_status_sources(primary_rel: str, root: Path = ROOT) -> list[str]:
    """Fail closed if the independent current-status JSON feeds drift apart.

    The page anchor, legacy form card and current readiness card are rendered by
    different scripts. Bind all three to the same primary bytes, eligibility,
    form name and note so a stale card cannot look like a current selector result.
    """
    problems: list[str] = []
    if (not isinstance(primary_rel, str)
            or not re.fullmatch(r'downloads/[A-Za-z0-9_.-]+-zeros\.tif', primary_rel)):
        return ['primary path is unsafe for current-status comparison']
    docs = root / 'docs'
    current = read_json_object(docs / 'downloads/current_submission.json', problems)
    readiness = read_json_object(docs / 'downloads/readiness.json', problems)
    expected_file = f'docs/{primary_rel}'

    if current.get('file') != expected_file:
        problems.append('current_submission.json file does not match index.html data-primary')
    if readiness.get('file') != primary_rel:
        problems.append('readiness.json file does not match index.html data-primary')

    if current.get('file') == expected_file:
        candidate = root / expected_file
        if not candidate.is_file():
            problems.append('current primary TIFF is missing from disk')
        else:
            digest = sha256_file(candidate)
            if current.get('sha256') != digest:
                problems.append('current_submission.json SHA-256 does not match primary TIFF')
            if readiness.get('raster_sha256') != digest:
                problems.append('readiness.json SHA-256 does not match primary TIFF')

    aliases = (
        ('submission_name', 'submission_name'),
        ('note', 'note'),
        ('verdict', 'verdict'),
    )
    for current_key, readiness_key in aliases:
        if current.get(current_key) != readiness.get(readiness_key):
            problems.append(f'current status cards disagree on {current_key}')

    current_eligible = current.get('ok_to_submit')
    readiness_eligible = readiness.get('submission_eligible')
    if type(current_eligible) is not bool or type(readiness_eligible) is not bool:
        problems.append('current status cards must contain literal boolean eligibility')
    elif current_eligible != readiness_eligible:
        problems.append('current status cards disagree on submission eligibility')

    if current.get('ok_to_download') is not True:
        problems.append('current_submission.json must say the primary is downloadable')
    if not str(readiness.get('download_status', '')).startswith('OK TO DOWNLOAD'):
        problems.append('readiness.json does not mark the primary as downloadable')
    submission_status = str(readiness.get('submission_status', ''))
    if current_eligible is False and (
            'DO NOT SUBMIT' not in submission_status or 'OK TO SUBMIT' in submission_status):
        problems.append('readiness.json does not clearly block a non-eligible primary')
    if current_eligible is True and (
            'OK TO SUBMIT' not in submission_status or 'DO NOT SUBMIT' in submission_status):
        problems.append('readiness.json does not clearly permit its eligible primary')

    for obj_name, obj in (('current_submission.json', current), ('readiness.json', readiness)):
        note = obj.get('note')
        if not isinstance(note, str) or not 0 < len(note) <= 140:
            problems.append(f'{obj_name} note must contain 1–140 characters')
    return problems


def main() -> int:
    problems: list[str] = []

    if not INDEX.is_file():
        print("FAIL: docs/index.html missing")
        return 2
    html = INDEX.read_text(encoding="utf-8")

    # The current decision is generated from one byte-bound run card (VARIO),
    # not from whichever parallel lane happened to prepend its banner most
    # recently.  Superseded rejection-only renderers delegate to it.
    from scripts.render_vario_status import check as check_vario_status
    try:
        stale = check_vario_status(ROOT)
        if stale:
            problems.append('stale current status panels: ' + ', '.join(stale))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        problems.append(f'current status evidence invalid: {exc}')

    # The executive review, correction run card, grouped-model diagnostic and
    # visible banners are generated from the same rejection-only evidence.
    # A stale renderer output must not reintroduce a misleading estimate or
    # submission instruction at publication time.
    try:
        from scripts import (audit_score_estimator, render_focus9_page, render_focus_site_review,
                             render_review_14f85876, render_review_b4bb558b, render_review_d30d387c,
                             render_review_banner)
        generated = {
            render_focus9_page.OUTPUT: render_focus9_page.render(),
            render_review_14f85876.OUTPUT: json.dumps(render_review_14f85876.build(), indent=2, allow_nan=False) + '\n',
            render_review_b4bb558b.OUTPUT: json.dumps(render_review_b4bb558b.build(), indent=2, allow_nan=False) + '\n',
            render_review_d30d387c.OUTPUT: json.dumps(render_review_d30d387c.build(), indent=2, allow_nan=False) + '\n',
            audit_score_estimator.OUTPUT: json.dumps(audit_score_estimator.audit(), indent=2, allow_nan=False) + '\n',
        }
        if render_review_b4bb558b.PUBLIC_INPUT.read_bytes() != render_review_b4bb558b.INPUT.read_bytes():
            problems.append('public owner-mirror input audit differs from its source receipt')
        if render_review_d30d387c.PUBLIC_INPUT.read_bytes() != render_review_d30d387c.INPUT.read_bytes():
            problems.append('public d30d387c input audit differs from its source receipt')
        if render_review_d30d387c.PUBLIC_FLEET.read_bytes() != render_review_d30d387c.FLEET.read_bytes():
            problems.append('public d30d387c fleet audit differs from its source receipt')
        old_review = json.loads(render_focus_site_review.EVIDENCE.read_text(encoding='utf-8'))
        generated.update(render_focus_site_review.generate(old_review))
        for path, expected in generated.items():
            if not path.is_file() or path.read_text(encoding='utf-8') != expected:
                problems.append(f'stale evidence-bound review output: {path.relative_to(ROOT)}')
        for rel in render_review_banner.PAGES:
            path = ROOT / rel
            text = path.read_text(encoding='utf-8')
            if text != render_review_banner.render_page(text, root_page=rel == 'index.html'):
                problems.append(f'stale independent review banner: {rel}')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        problems.append(f'independent review evidence invalid: {exc}')

    # ---- the page contract, written against properties not one lane's wording --
    for needle in ("OK TO DOWNLOAD", "Predicted values must be in range [0, 1]",
                   "HOLDOUT-DTI",
                   "DUPLICATE UNDER THE LITERAL REGISTRY RULE", "VARIO-STATUS:BEGIN"):
        if needle not in html:
            problems.append(f"index.html missing {needle!r}")
    if not any(s in html for s in ("NOT CLEARED FOR A WEEKLY SLOT", "ELIGIBLE FOR THE SELECTOR STEP")):
        problems.append("index.html missing an explicit weekly-slot decision")
    if not re.search(r"(weekly slot|3/week|weekly competition slot|human step)", html, re.I):
        problems.append("index.html carries no weekly-slot caution")
    if re.search(r'href="downloads/[^"]+-zeros\.tif"', html) is None:
        problems.append("index.html offers no zeros-outside download")
    # a HOLDOUT number must never be dressed as an organizer receipt
    if re.search(r"ORGANIZER-CONFIRMED[^<]{0,40}0\.00\d{4}", html):
        problems.append("holdout number labeled ORGANIZER-CONFIRMED")

    # Reject duplicate HTML element id="..." attributes so anchor links stay unambiguous
    seen_ids: set[str] = set()
    dup_ids: set[str] = set()
    for elem_id in re.findall(r'\bid="([^"]+)"', html):
        if elem_id in seen_ids:
            dup_ids.add(elem_id)
        seen_ids.add(elem_id)
    if dup_ids:
        problems.append(f"index.html contains duplicate element id(s): {sorted(dup_ids)}")

    # Current panel/readiness freshness is covered by the VARIO byte-bound
    # check above (render_vario_status re-derives gates from the TIFF bytes).

    # ---- every served zeros-outside raster must be linked AND pass the gates ---
    served = sorted(DOWNLOADS.glob("*-zeros.tif"))
    if not served:
        problems.append("no zeros-outside rasters in docs/downloads")
    for path in served:
        if f"downloads/{path.name}" not in html:
            problems.append(f"{path.name} is served but not linked from index.html")

    with rasterio.open(SAMPLE) as ds:
        footprint = np.isfinite(ds.read(1))
    with rasterio.open(LABELS) as ds:
        cat = ds.read(1) > 0.5

    for path in served:
        tag = path.name
        ok, report = summarise(run_gates(
            str(path), str(SAMPLE), str(LABELS), prune_radius=2,
            require_submission_encoding=True,
        ))
        if not ok:
            problems.append(f"{tag}: gates failed\n{report}")
            continue  # Do not index malformed/mismatched arrays below.
        expected_dots = N_DOTS
        per_file_audit = _audit_path(path)
        if per_file_audit.is_file():
            try:
                audit_doc = json.loads(per_file_audit.read_text(encoding="utf-8"))
                expected_dots = int(audit_doc.get("n_positive_pixels",
                                      audit_doc.get("raster", {}).get("positive_pixels",
                                      audit_doc.get("n_dots", N_DOTS))))
            except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                problems.append(f"{tag}: invalid per-file audit receipt: {exc}")
        with rasterio.open(path) as ds:
            a = ds.read(1)
            if ds.dtypes[0] != "float32" or ds.count != 1:
                problems.append(f"{tag}: dtype/band")
            if not np.isfinite(a).all():
                problems.append(f"{tag}: NaN/inf present (portal [0,1] risk)")
            if a.min() < 0 or a.max() > 1:
                problems.append(f"{tag}: values [{a.min()}, {a.max()}]")
            if np.any((a > 0) & ~footprint):
                problems.append(f"{tag}: mass outside footprint")
            if np.any(a[cat] > 0):
                problems.append(f"{tag}: mass on catalogue")
            if int((a > 0).sum()) != expected_dots:
                problems.append(f"{tag}: n_dots {int((a > 0).sum())} != audit/expected {expected_dots}")

        try:
            assert_submittable(validate(path, footprint, cat))
        except AssertionError as exc:
            problems.append(f"{tag}: {exc}")

        print(f"  PASS {tag}  sha256 {sha256_file(path)[:16]}…")

    # ---- the primary named on the page must match its audit receipt ----------
    primary_rel = primary_download(html, problems)
    if primary_rel:
        problems.extend(check_current_status_sources(primary_rel, ROOT))
        primary = DOCS / primary_rel
        if not primary.is_file():
            problems.append(f"index.html points at {primary_rel}, which does not exist")
        else:
            audit_path = _audit_path(primary)
            doc = read_json_object(audit_path, problems)
            if doc:
                if doc.get("overall_pass") is not True:
                    problems.append("audit receipt does not record format_pass == true")
                if doc.get("sha256_zeros") != sha256_file(primary):
                    problems.append("audit receipt sha256 != primary bytes on disk")
                check_recorded_gates(doc, problems)
                if doc.get("submission_eligible") is not False:
                    problems.append("audit must say submission_eligible=false (slot selection is a separate selector step)")
                public = doc.get("public_registry_uniqueness", {})
                if not isinstance(public, dict):
                    problems.append('public registry evidence must be an object')
                    public = {}
                if public.get("candidate_hash_matches_scan") is not True:
                    problems.append("public registry audit is absent or not for these exact candidate bytes")
                if public.get("unique_under_literal_rule") is not False or public.get("stop_required") is not True:
                    problems.append("site audit must preserve the literal duplicate stop verdict (binding public witness or full-scan duplicate)")
            card_rel = doc.get("run_card")
            card_path = (ROOT / card_rel) if card_rel else (ROOT / "evidence" / "visible_collar_run_card.json")
            if not card_path.is_file():
                problems.append(f"primary run card missing: {card_path}")
            else:
                card = read_json_object(card_path, problems)
                if card.get("raster_sha256") != sha256_file(primary):
                    problems.append("run card SHA256 != primary bytes")
                if card.get("verdict") not in ("negative", "promote"):
                    problems.append("run card verdict must be negative or promote")
                if doc.get("verdict") != card.get("verdict"):
                    problems.append("audit verdict disagrees with run card")
                try:
                    readiness_doc = json.loads((DOWNLOADS / "readiness.json").read_text())
                    if readiness_doc.get("verdict") != card.get("verdict") or readiness_doc.get("raster_sha256") != card.get("raster_sha256"):
                        problems.append("readiness.json disagrees with run card")
                except (OSError, ValueError) as exc:
                    problems.append(f"readiness.json unreadable: {exc}")
            print(f"  PRIMARY {primary.name}")

    # Canonical VARIO status freshness (byte-bound, first in body) was checked
    # at the top of main() via render_vario_status.check.

    # The fresh receipt linked in the first status panel must not drift from
    # current validation code or served bytes; missing evidence fails closed.
    from scripts.audit_readiness import check_published_audit
    problems.extend(check_published_audit(ROOT))

    if problems:
        print("SITE CHECK FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print(f"SITE CHECK PASS ({len(served)} served raster(s) gated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
