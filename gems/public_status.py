"""One authoritative, byte-bound rejection panel above historical lane banners.

This is a rejection-only publication tool, not a submission selector. It cannot
promote a file or infer a score from format validity. Historical receipts remain
unchanged; checks fail if a lane renderer prepends content above this panel.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import re

from .rasters import sha256_file

BEGIN = '<!-- PUBLIC-STATUS:BEGIN -->'
END = '<!-- PUBLIC-STATUS:END -->'
PAGES = ('index.html', 'executive-summary.html', 'SUBMIT.html',
         'index_new.html', 'SUBMIT_NOW.html')


def validate_status(card: dict, root: Path, primary_rel: str) -> None:
    if not isinstance(card, dict):
        raise ValueError('public status must be an object')
    if not re.fullmatch(r'downloads/[A-Za-z0-9_.-]+-zeros\.tif', primary_rel):
        raise ValueError('unsafe primary path')
    if card.get('primary_download') != 'docs/' + primary_rel:
        raise ValueError('status must describe the explicit primary, not a sibling')
    if card.get('raster_sha256') != sha256_file(root / 'docs' / primary_rel):
        raise ValueError('status raster SHA-256 is stale')
    if (card.get('submission_eligible') is not False or
            card.get('verdict') != 'negative' or
            card.get('new_raster_generated') is not False):
        raise ValueError('review panel cannot authorize submission or claim a new raster')
    rows = card.get('validator_output')
    if not isinstance(rows, list) or not rows or any(
        not isinstance(r, dict) or not isinstance(r.get('name'), str)
        or r.get('ok') is not True for r in rows
    ):
        raise ValueError('research-download status requires passing format checks')
    expected = {'crs', 'shape', 'transform', 'dtype_and_band', 'values_in_0_1',
                'no_nan_inside_footprint', 'submission_encoding', 'reread_sha256'}
    names = [r.get('name') for r in rows]
    if not expected.issubset(names) or len(names) != len(set(names)):
        raise ValueError('status format checks missing or duplicated')
    registry = card.get('correlation_overlap_vs_registry', {})
    if (not isinstance(registry, dict) or registry.get('stop_required') is not True
            or registry.get('forward_overlap') != 1.0):
        raise ValueError('status must preserve the universal literal stop')
    pins = card.get('publication_input_sha256', {})
    required = ('data/bridge/sample_submission.tif', 'data/bridge/labels.tif',
                'gems/gates.py', 'evidence/review797e_preflight.json')
    if not isinstance(pins, dict) or set(pins) != set(required):
        raise ValueError('status input pins missing or unexpected')
    for rel in required:
        if pins[rel] != sha256_file(root / rel):
            raise ValueError(f'status input SHA-256 is stale: {rel}')
    if not isinstance(card.get('note'), str) or not 0 < len(card['note']) <= 140:
        raise ValueError('status note must contain 1..140 characters')


def render_status(card: dict) -> str:
    """Escape all receipt strings; never render an eligibility-dependent CTA."""
    path = escape(card['primary_download'].removeprefix('docs/'), quote=True)
    sha = escape(card['raster_sha256'])
    return f'''{BEGIN}
<section class="banner banner-warn" aria-label="Authoritative submission status">
  <h1>Research download available. DO NOT SUBMIT.</h1>
  <p><strong>OK TO DOWNLOAD FOR RESEARCH · NOT CLEARED FOR A WEEKLY SLOT</strong></p>
  <p><a class="btn" href="{path}" download>Download existing format-validated GeoTIFF (.tif)</a>
  · <a href="executive-summary.html">Submission guide</a>
  · <a href="review48.html">Current review, evidence and limitations</a>
  · <a href="downloads/review48_run_card.json">Fresh automated audit card</a></p>
  <p>This is an existing research artifact, <strong>not a newly generated or unique submission</strong>.
  The literal registry overlap is 1.0 (limit 0.70); matched-budget uniqueness claims below do not override the stop.
  No new model, HOLDOUT-DTI result, organizer receipt or weekly slot was produced in this review.</p>
  <p>Automated format checks pass: finite values in [0, 1], no NaN inside the footprint,
  zeros outside, matching CRS/shape/transform. Format validity is not competition acceptance.</p>
  <p>SHA-256: <code>{sha}</code></p>
</section>
{END}'''


def install_panel(html: str, panel: str) -> str:
    """Move the sole generated panel ahead of any subsequently prepended lane."""
    if html.count(BEGIN) != html.count(END) or html.count(BEGIN) > 1:
        raise ValueError('ambiguous public-status markers')
    if BEGIN in html:
        start, tail = html.split(BEGIN, 1)
        _, finish = tail.split(END, 1)
        html = start + finish
    if html.count('<body>') != 1:
        raise ValueError('expected exactly one body')
    before, body = html.split('<body>', 1)
    return before + '<body>\n' + panel + '\n' + body.lstrip()


def check_panels(card: dict, root: Path, primary_rel: str) -> list[str]:
    problems = []
    try:
        validate_status(card, root, primary_rel)
        panel = render_status(card)
        for name in PAGES:
            html = (root / 'docs' / name).read_text(encoding='utf-8')
            if (html.count(BEGIN) != 1 or html.count(END) != 1
                    or html.split('<body>', 1)[1].lstrip().split(END, 1)[0] + END != panel):
                problems.append(f'{name}: authoritative status missing, stale or not first in body')
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        problems.append(f'invalid public status: {exc}')
    return problems
