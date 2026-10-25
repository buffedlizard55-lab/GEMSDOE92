#!/usr/bin/env python3
"""Render byte-bound supplementary review panels; core pages use gems.public_status.

No network, model training, slot selection, or new predictions. --check is a
publication gate: stale or hand-edited panels fail instead of being published.
This renderer is intentionally rejection-only while the literal witness binds.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CARD = 'docs/downloads/listric_loqo_run_card.json'
BEGIN = '<!-- CURRENT-STATUS:BEGIN -->'
END = '<!-- CURRENT-STATUS:END -->'
PAGES = ('docs/submit.html', 'index.html', 'README.md', 'docs/REVIEW_CURRENT.md',
         'SUBMISSION_READY.md', 'docs/BEAT_0_2778.md')


def load_card(root: Path = ROOT) -> dict:
    card = json.loads((root / CARD).read_text())
    if not isinstance(card, dict):
        raise ValueError('current receipt must be a JSON object')
    if card.get('verdict') != 'negative' or card.get('submission_eligible') is not False:
        raise ValueError('current renderer cannot grant promotion')
    primary = card.get('primary_download', '')
    if not isinstance(primary, str) or not re.fullmatch(r'docs/downloads/[A-Za-z0-9_.-]+-zeros\.tif', primary):
        raise ValueError('primary must be a local zeros-outside research TIFF')
    if hashlib.sha256((root / primary).read_bytes()).hexdigest() != card['raster_sha256']:
        raise ValueError('current status SHA-256 differs from downloadable bytes')
    from scripts.check_site import primary_download
    problems: list[str] = []
    declared = primary_download((root / 'docs/index.html').read_text(), problems)
    if problems or primary != f'docs/{declared}':
        raise ValueError('current status differs from declared site primary')
    if not isinstance(card.get('correlation_overlap_vs_registry'), dict):
        raise ValueError('registry evidence must be an object')
    preflight = json.loads((root / 'evidence/review_f23_preflight.json').read_text())
    from scripts.preflight_dense_witness import SAMPLE_SHA256, WITNESS_SHA256, WITNESS_BLOB
    if (not isinstance(preflight, dict)
            or preflight.get('universal_nonempty_in_footprint_overlap_stop') is not True
            or preflight.get('sample_sha256') != SAMPLE_SHA256
            or preflight.get('sha256') != WITNESS_SHA256
            or preflight.get('git_blob_sha') != WITNESS_BLOB):
        raise ValueError('current rejection differs from pinned preflight receipt')
    audit_path = (root / primary).with_name(Path(primary).stem.removesuffix('-zeros') + '-audit.json')
    validator = json.loads(audit_path.read_text())
    if not isinstance(validator, dict) or validator.get('gates_zeros_pass') is not True:
        raise ValueError('validator evidence must be a passing object')
    rows = validator.get('gates_zeros', [])
    required = {'crs', 'shape', 'transform', 'dtype_and_band', 'values_in_0_1',
                'no_nan_inside_footprint', 'reread_sha256'}
    if (not isinstance(rows, list) or not rows
            or any(not isinstance(g, dict) or g.get('ok') is not True
                   or not isinstance(g.get('name'), str) for g in rows)
            or len({g['name'] for g in rows}) != len(rows)
            or not required.issubset({g['name'] for g in rows})):
        raise ValueError('missing or failing recorded format gates')
    registry = card['correlation_overlap_vs_registry']
    overlap = registry.get('public_dense_witness_forward_overlap')
    if type(overlap) not in (int, float) or overlap != 1.0:
        raise ValueError('missing literal registry rejection evidence')
    if not isinstance(card.get('note'), str) or len(card['note']) > 140:
        raise ValueError('note exceeds form limit')
    return card


def panel(card: dict, page: str) -> str:
    # All destinations are repository-local and escaped. No user-supplied HTML.
    def link(path: str) -> str:
        import posixpath
        return html.escape(posixpath.relpath(path, str(Path(page).parent)), quote=True)

    name = html.escape(Path(card['primary_download']).name)
    download = link(card['primary_download'])
    review = link('docs/REVIEW_C5E3848C.md')
    receipt = link(CARD)
    guide = link('docs/executive-summary.html')
    import posixpath
    from gems.newest_session import html_line, load as load_newest, md_line
    to_docs = posixpath.relpath('docs', str(Path(page).parent))
    to_docs = '' if to_docs == '.' else to_docs + '/'
    ali_card = load_newest(ROOT)
    if page.endswith('.md'):
        return f'''{BEGIN}
## Authoritative decision — Current verified status, 2026-10-25 (LISTRICLOQO 2026-10-25)

{md_line(ali_card, to_docs)}

**OK TO DOWNLOAD FOR RESEARCH. DO NOT SUBMIT.** LISTRICLOQO is a byte-distinct research artifact, but it fails the literal registry-overlap stop and promotion gates.

[Existing LISTRICLOQO research TIFF — not cleared to submit]({download}) · [protocol run card]({receipt}) · [analysis]({link('docs/ANALYSIS_20261025_LISTRICLOQO.md')}) · [three-pass review]({link('docs/REVIEW_20261025_SESSION.md')}) · [executive submission guide]({guide}).

Automated format checks pass. HOLDOUT-DTI (`gems57-pooled-hide-v2`, 22,663 withheld positives) is `0.013295 [0.011713, 0.014980]`; paired improvement over KNICKLOQO is +0.002508 [0.001477, 0.003463]. Public dual-reading overlap is `0.690259 <= 0.70`, but the binding literal dense-witness overlap is `1.0 > 0.70`; this file is not uniqueness-cleared. No ORGANIZER-CONFIRMED score is available; 3/3 experiments and zero weekly slots.

{END}'''
    return f'''{BEGIN}
<section id="current-verified-status" aria-label="Current authoritative submission status" style="max-width:70rem;margin:1rem auto;padding:1.25rem;border:3px solid #991b1b;border-radius:12px;background:#fff7ed;color:#292524;font:1rem/1.6 system-ui,sans-serif;overflow-wrap:anywhere">
<h2 style="margin-top:0">Current decision: research-only TIFF; submission blocked</h2>
<p><strong>OK TO DOWNLOAD FOR RESEARCH · DO NOT SUBMIT · NOT CLEARED FOR A WEEKLY SLOT</strong></p>
{html_line(ali_card, to_docs)}
<p><a href="{download}" download style="display:inline-block;padding:.7rem 1rem;background:#1e3a5f;color:white;border-radius:6px;font-weight:700">Download LISTRICLOQO research TIFF — not cleared to submit</a></p>
<p>{name}<br>SHA-256: <code>{card['raster_sha256']}</code></p>
<p>Automated format checks pass: single band, finite [0, 1], no NaNs, zeros outside the footprint, matching CRS/shape/transform. The file is byte-distinct and passes the public dual-reading diagnostic, but its literal dense-witness overlap is 1.0, above the 0.70 stop; <strong>it is not uniqueness-cleared or eligible to submit</strong>.</p>
<p><strong>Negative verdict:</strong> HOLDOUT-DTI (<code>gems57-pooled-hide-v2</code>, 22,663 withheld positives) is 0.013295 [0.011713, 0.014980], but paired improvement over KNICKLOQO is +0.002508 [0.001477, 0.003463]. Public dual-reading overlap is 0.690259 and literal dense-witness overlap is 1.0; the limit is 0.70. No ORGANIZER-CONFIRMED score is available.</p>
<p><a href="{receipt}">Protocol run card</a> · <a href="{link('docs/ANALYSIS_20261025_LISTRICLOQO.md')}">Analysis and limitations</a> · <a href="{link('docs/REVIEW_20261025_SESSION.md')}">Three-pass review</a> · <a href="{guide}">Executive summary / submission instructions</a></p>
<p>LISTRICLOQO completed 3/3 experiments and used zero weekly slots. Historical ranking statements below are archives, not clearance.</p>
</section>
{END}'''


def render(text: str, block: str, *, markdown: bool) -> str:
    if text.count(BEGIN) != text.count(END) or text.count(BEGIN) > 1:
        raise ValueError('malformed current-status markers')
    if BEGIN in text:
        start, end = text.index(BEGIN), text.index(END) + len(END)
        if text.index(END) < start:
            raise ValueError('malformed current-status markers: end precedes begin')
        if not markdown:
            return text[:start] + block + text[end:]
        # Remove and reinsert below the H1, even if a parallel lane prepended
        # a banner above an already-existing panel. Merely replacing the panel
        # allowed misleading future-dated 'Latest artifact' claims to win.
        text = text[:start] + text[end:]
    if markdown:
        first, sep, rest = text.partition('\n')
        if not sep or not first.startswith('# '):
            raise ValueError('markdown current status requires a project H1')
        return first + sep + '\n' + block + '\n\n' + rest.lstrip('\n')
    body = re.search(r'<body\b[^>]*>', text, re.I)
    if not body:
        raise ValueError('page has no body')
    return text[:body.end()] + '\n' + block + '\n' + text[body.end():]


def archive_lane_banners(text: str, page: str) -> str:
    """Keep prior evidence reachable without several screens of newest banners."""
    archive_whole_page = page in ('docs/SUBMIT_NOW.html', 'docs/index_new.html',
                                  'SUBMISSION_READY.md', 'docs/BEAT_0_2778.md')
    if not archive_whole_page and page not in ('docs/index.html', 'docs/executive-summary.html', 'docs/SUBMIT.html'):
        return text
    marker = '<details data-status-archive="true">'
    if marker in text:
        if text.count(marker) != 1:
            raise ValueError('duplicate lane archive wrappers')
        return text
    start = text.index(END) + len(END)
    if archive_whole_page:
        header = len(text) if page.endswith('.md') else text.lower().rfind('</body>')
    else:
        header = text.find('<header', start)
    if header < start:
        raise ValueError('missing main header or closing body after status panel')
    archived = text[start:header]
    return (text[:start] + '\n' + marker +
            '\n<summary>Archived parallel-lane reports — not current submission clearance</summary>\n' +
            archived + '</details>\n' + text[header:])


def check(root: Path = ROOT, *, write: bool = False) -> list[str]:
    card = load_card(root)
    stale = []
    updates = []
    for page in PAGES:
        path = root / page
        old = path.read_text()
        new = render(old, panel(card, page), markdown=page.endswith('.md'))
        new = archive_lane_banners(new, page)
        # A panel buried below an older banner must also fail the gate.
        prefix = new[:new.index(BEGIN)]
        if page.endswith('.html'):
            body = re.search(r'<body\b[^>]*>', prefix, re.I)
            if not body or prefix[body.end():].strip():
                raise ValueError(f'{page}: current status must precede historical banners')
        if new != old:
            stale.append(page)
            updates.append((path, new))
    # Validate every target before changing any panel.
    if write:
        for path, new in updates:
            path.write_text(new)
    return stale


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    try:
        stale = check(write=not args.check)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'CURRENT STATUS FAIL: {exc}', file=sys.stderr)
        return 1
    if args.check and stale:
        print('CURRENT STATUS STALE: ' + ', '.join(stale), file=sys.stderr)
        return 1
    print('CURRENT STATUS PASS' if args.check else f'Rendered {len(stale)} current status panel(s)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
