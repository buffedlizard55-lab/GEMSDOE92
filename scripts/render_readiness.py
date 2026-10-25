#!/usr/bin/env python3
"""Render a byte-bound current research status; never authorize a weekly slot.

No network, model fitting, or raster writing. Reuses the shared validator and a
pinned rejection receipt. Historical panels stay in a collapsed archive rather
than competing with the current decision. --check is mandatory before publish.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gems.gates import run_gates
from gems.rasters import sha256_file
import rasterio
from scripts.check_site import primary_download
from scripts.preflight_dense_witness import SAMPLE_SHA256, WITNESS_SHA256, WITNESS_BLOB

PAGES = ('index.html', 'executive-summary.html', 'SUBMIT.html')
START = '<!-- CURRENT-READINESS:BEGIN -->'
END = '<!-- CURRENT-READINESS:END -->'
ARCHIVE_START = '<details id="historical-research-archive"><summary>Historical experiments and downloads — not current clearance</summary>'
ARCHIVE_END = '<!-- HISTORICAL-ARCHIVE:END -->'


def rejection_proof_errors(proof: dict, sample_sha: str) -> list[str]:
    """Validate the pinned proof's identity and rejection semantics, never clearance."""
    expected = {
        'schema': 'gemsdoe92-preplacement-stop-v2',
        'sample_sha256': SAMPLE_SHA256,
        'sha256': WITNESS_SHA256,
        'git_blob_sha': WITNESS_BLOB,
        'grid_checks_pass': True,
        'footprint_pixels': 5167373,
        'positive_in_footprint': 5167373,
        'universal_nonempty_in_footprint_overlap_stop': True,
        'forward_overlap_for_any_nonempty_in_footprint_dot_set': 1.0,
        'threshold': 0.70,
        'verdict': 'negative',
        'submission_eligible': False,
    }
    errors = []
    for key, value in expected.items():
        got = proof.get(key)
        if type(got) is not type(value) or got != value:
            errors.append(f'rejection receipt mismatch: {key}')
    if sample_sha != SAMPLE_SHA256:
        errors.append('sample bytes differ from pinned rejection footprint')
    return errors


def form_note(card: dict) -> str:
    """Accept the two historical schemas, but never hide conflicting aliases."""
    notes = [card[k] for k in ('note', 'submission_note') if k in card]
    if (not notes or any(not isinstance(n, str) or not 0 < len(n) <= 140 for n in notes)
            or len(set(notes)) != 1):
        raise ValueError('primary note must contain 1–140 characters; aliases must agree')
    return notes[0]


def build_status(root: Path = ROOT) -> dict:
    docs = root / 'docs'
    problems: list[str] = []
    relative = primary_download((docs / 'index.html').read_text(), problems)
    if problems:
        raise ValueError('; '.join(problems))
    candidate = docs / relative
    sample = root / 'data/bridge/sample_submission.tif'
    catalogue = root / 'data/bridge/labels.tif'
    proof_path = root / 'evidence/preplacement_stop_20261025_arena.json'
    proof = json.loads(proof_path.read_text())
    problems.extend(rejection_proof_errors(proof, sha256_file(sample)))
    receipt = candidate.with_name(candidate.stem.removesuffix('-zeros') + '-audit.json')
    audit = json.loads(receipt.read_text())
    card_path = (root / audit['run_card']).resolve()
    if not card_path.is_relative_to(root.resolve()):
        raise ValueError('run card must be inside the repository')
    card = json.loads(card_path.read_text())
    digest = sha256_file(candidate)
    if digest != audit.get('sha256_zeros') or digest != card.get('raster_sha256'):
        problems.append('primary bytes do not match audit and run card')
    if audit.get('submission_eligible') is not False or card.get('verdict') != 'negative':
        problems.append('historical primary evidence contradicts the binding rejection')
    note = form_note(card)
    gates = run_gates(candidate, sample, catalogue, prune_radius=2,
                      require_submission_encoding=True)
    problems.extend(f'format gate failed: {gate.name}' for gate in gates if not gate.ok)
    if problems:
        raise ValueError('; '.join(problems))
    bindings = [sample, catalogue, candidate, receipt, card_path, proof_path,
                root / 'gems/gates.py', root / 'scripts/render_readiness.py']
    return {
        'schema': 'gemsdoe92-current-readiness.v1',
        'evidence_class': 'AUTOMATED-FORMAT-CHECK + REGISTRY-MEASUREMENT; not a score',
        'download_status': 'OK TO DOWNLOAD FOR RESEARCH',
        'submission_status': 'DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT',
        'submission_eligible': False,
        'verdict': 'negative',
        'new_unique_tiff_generated': False,
        'experiments_this_review': 0,
        'weekly_slots_used_this_review': 0,
        'file': relative,
        'raster_sha256': digest,
        'submission_name': card['submission_name'],
        'note': note,
        'format_pass': True,
        'validator_output': [asdict(g) for g in gates],
        'correlation_overlap_vs_registry': {
            'evidence_class': 'REGISTRY-MEASUREMENT',
            'scope': 'single pinned universal witness; rejection only, not full registry scan',
            'forward_overlap': 1.0,
            'rank_correlation': None,
            'rank_correlation_reason': 'not measured in this review; overlap alone requires stop',
            'proof': 'downloads/preplacement_stop_20261025_arena.json',
        },
        'holdout_dti': None,
        'holdout_reason': 'No new candidate or holdout after universal pre-placement stop.',
        'organizer_confirmed_score': None,
        'blocking_reasons': [
            'DUPLICATE UNDER THE LITERAL REGISTRY RULE: pinned positive support covers the entire footprint.',
            'Matched-budget overlap is diagnostic, not permission to replace the literal rule.',
            'No candidate was built: the literal pre-placement stop blocks placement and the feature stack is absent.',
            'No verified submission-page receipt or current weekly-cap evidence is available.',
        ],
        'input_sha256': {str(p.relative_to(root)): sha256_file(p) for p in bindings},
    }


def panel(status: dict) -> str:
    e = html.escape
    reasons = '\n'.join(f'<li>{e(reason)}</li>' for reason in status['blocking_reasons'])
    return f'''{START}
<section class="readiness-panel" aria-labelledby="current-readiness-heading">
  <p class="readiness-kicker">GEMSDOE92 · automated submission readiness · review 2026-10-25</p>
  <h1 id="current-readiness-heading">Research file available. Submission blocked.</h1>
  <p><strong>{e(status['download_status'])}</strong><br><strong>{e(status['submission_status'])}</strong></p>
  <p>No new unique TIFF was generated in this review. This is an existing research artifact, not a new submission.</p>
  <p><a class="btn" href="{e(status['file'])}" download>Download existing research GeoTIFF (.tif)</a>
  <a href="SUBMIT.html">Submission guide</a> · <a href="REVIEW_20261025_ARENA.md">Current review, hypotheses and limitations</a> ·
  <a href="downloads/readiness.json">Machine-readable status</a> · <a href="downloads/arena_review_run_card_20261025.json">Review run card</a> ·
  <a href="downloads/preplacement_stop_20261025_arena.json">Fresh duplicate-stop receipt</a></p>
  <p>Fresh automated validation: single band, float32, finite values in [0, 1], zero outside the footprint,
  matching CRS, shape and transform. This is local validation, not organizer acceptance.</p>
  <ul>{reasons}</ul>
  <details><summary>File identity and record-only form fields</summary>
  <p>SHA-256: <code>{e(status['raster_sha256'])}</code></p>
  <p>Name: <code>{e(status['submission_name'])}</code></p>
  <p>Note ({len(status['note'])}/140 characters): <code>{e(status['note'])}</code></p>
  <p>Do not upload this artifact. A later eligible artifact must pass automated scientific and uniqueness gates,
  followed by the separate selector step within the verified weekly cap. No visual inspector is required for file validation.</p></details>
  <details><summary>How to submit a future cleared artifact</summary>
  <p><strong>Do not perform these steps with the current artifact.</strong></p>
  <ol><li>Require current automated format, leakage, comparable holdout-improvement and literal uniqueness gates to pass.
  Complete the separate selector step and verify the actual weekly cap on the submission page.</li>
  <li>Download that exact eligible single-band .tif (or a ZIP containing only it); retain its audit and SHA-256.</li>
  <li>Open the DrivenData competition submission form, choose the file, and copy the artifact's name and short note.</li>
  <li>After upload, record the organizer receipt against the exact file hash. Only that receipt supports an
  ORGANIZER-CONFIRMED score. Do not project a score from the local holdout.</li></ol></details>
  <p>No ORGANIZER-CONFIRMED score. No fresh HOLDOUT-DTI measurement. Older “unique” and “record” claims below are historical,
  not current clearance. A better local surrogate does not establish a better leaderboard score.</p>
</section>
{END}'''


def render_page(text: str, block: str) -> str:
    body = re.search(r'(<body\b[^>]*>)(.*?)(</body>)', text, flags=re.S)
    if body is None:
        raise ValueError('missing body')
    content = body[2]
    # Reuse the concurrently merged shared first-in-body public-status contract.
    # The detailed readiness panel follows the same negative decision.
    from gems.public_status import BEGIN as PUBLIC_BEGIN, END as PUBLIC_END
    public = ''
    if PUBLIC_BEGIN in content or PUBLIC_END in content:
        if content.count(PUBLIC_BEGIN) != 1 or content.count(PUBLIC_END) != 1:
            raise ValueError('ambiguous public-status markers')
        match = re.search(re.escape(PUBLIC_BEGIN) + r'.*?' + re.escape(PUBLIC_END), content, flags=re.S)
        if match is None:
            raise ValueError('malformed public-status panel')
        public = match[0] + '\n'
        content = content[:match.start()] + content[match.end():]
    # Shared lane-result block (scripts/render_current_submission.py, generated from
    # docs/downloads/current_submission.json). The current Arena review supersedes
    # this older lane snapshot, so keep it reachable only inside the collapsed archive.
    lane_result = ''
    CUR_BEGIN, CUR_END = '<!-- CURRENT:BEGIN -->', '<!-- CURRENT:END -->'
    if CUR_BEGIN in content or CUR_END in content:
        if content.count(CUR_BEGIN) != 1 or content.count(CUR_END) != 1:
            raise ValueError('ambiguous lane-result markers')
        match = re.search(re.escape(CUR_BEGIN) + r'.*?' + re.escape(CUR_END), content, flags=re.S)
        lane_result = match[0] + '\n'
        content = content[:match.start()] + content[match.end():]
    if START in content or END in content:
        if content.count(START) != 1 or content.count(END) != 1:
            raise ValueError('ambiguous readiness markers')
        content = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', content, flags=re.S)
    if ARCHIVE_START in content:
        if content.count(ARCHIVE_START) != 1 or content.count('</details>\n' + ARCHIVE_END) != 1:
            raise ValueError('ambiguous archive markers')
        content = content.replace(ARCHIVE_START, '').replace('</details>\n' + ARCHIVE_END, '')
    content = content.strip()
    replacement = (body[1] + '\n' + public + block + '\n' + ARCHIVE_START + '\n' + lane_result + content
                   + '\n</details>\n' + ARCHIVE_END + '\n' + body[3])
    return text[:body.start()] + replacement + text[body.end():]


def retired_page() -> str:
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="0; url=executive-summary.html">
<title>Clearance withdrawn — research only</title><link rel="stylesheet" href="style.css"></head>
<body><h1>DO NOT SUBMIT — prior clearance withdrawn</h1>
<p>The literal registry gate blocks current candidates. Format validation is not submission authorization.</p>
<p><a href="executive-summary.html">Current automated status and research downloads</a> ·
<a href="REVIEW_20261025_ARENA.md">Current rejection evidence and limitations</a></p></body></html>
'''


def corrected_knickloqo_receipt(root: Path) -> dict:
    """Withdraw unsupported parallel clearance; reread metadata instead of guessing."""
    card_path = root / 'evidence/knick_loqo_run_card.json'
    card = json.loads(card_path.read_text())
    candidate = root / card['primary_download']
    digest = sha256_file(candidate)
    if digest != card['raster_sha256']:
        raise ValueError('KNICKLOQO source card does not match bytes')
    gates = run_gates(candidate, root / 'data/bridge/sample_submission.tif',
                      root / 'data/bridge/labels.tif', prune_radius=2,
                      require_submission_encoding=True)
    with rasterio.open(candidate) as ds:
        metadata = {'bytes': candidate.stat().st_size, 'shape': list(ds.shape),
                    'crs': str(ds.crs), 'transform': list(ds.transform)[:6],
                    'band_count': ds.count, 'dtype': ds.dtypes[0], 'nodata': ds.nodata}
    return {
        'schema': 'gemsdoe92-withdrawn-clearance.v1',
        'replaces_unsupported_clearance_commit': '406638a0dbf44b2c65a7feefcdf803ba17d0edd4',
        'source_run_card': 'knick_loqo_run_card.json',
        'source_run_card_sha256': sha256_file(card_path),
        'raster_sha256': digest,
        'file': candidate.name,
        'primary_download': str(candidate.relative_to(root)),
        'metadata_measured_from_disk': metadata,
        'raster_metadata': metadata,
        'supersedes': {'archived_card': 'evidence/review797e_superseded_knickloqo_card.json'},
        'format_pass': all(g.ok for g in gates),
        'validator_output': [asdict(g) for g in gates],
        'holdout_dti': {'evidence_class': 'HOLDOUT-DTI', 'dti': None, 'ci95': None},
        'holdout_note': 'No new evaluation. Historical results remain in the linked source run card.',
        'organizer_confirmed_score': None,
        'correlation_overlap_vs_registry': {
            'evidence_class': 'REGISTRY-MEASUREMENT',
            'forward_overlap': 1.0,
            'scope': 'Pinned universal witness; rejection only, not a complete fresh registry scan.',
            'proof': 'review_f23_preflight.json',
        },
        'submission_name': card['submission_name'],
        'note': form_note(card),
        'verdict': 'negative',
        'submission_eligible': False,
        'new_unique_tiff_generated': False,
        'reason': 'Literal duplicate stop. Prior clearance and private-label projections are withdrawn.',
    }


def sync(root: Path = ROOT, *, check: bool = False) -> list[str]:
    status = build_status(root)
    outputs = {root / 'docs/downloads/readiness.json': json.dumps(status, indent=2, allow_nan=False) + '\n'}
    block = panel(status)
    # Keep one current run card authoritative across readiness and public panels.
    # Refresh the format-gate rows and source pins without changing any scientific result.
    from gems.public_status import install_panel, render_status, validate_status
    public_card_path = root / 'evidence/arena_review_run_card_20261025.json'
    public_card = json.loads(public_card_path.read_text())
    validator = public_card.get('validator_output')
    if not isinstance(validator, dict):
        raise ValueError('Arena run card must retain structured validator flags')
    validator['gates'] = status['validator_output']
    validator['gate_count'] = len(status['validator_output'])
    public_card['new_raster_generated'] = False
    registry = public_card['correlation_overlap_vs_registry']
    registry['forward_overlap'] = registry['existing_primary_forward_overlap_within_3px']
    pin_paths = ('data/bridge/sample_submission.tif', 'data/bridge/labels.tif',
                 'gems/gates.py', 'evidence/preplacement_stop_20261025_arena.json')
    public_card['publication_input_sha256'] = {rel: sha256_file(root / rel) for rel in pin_paths}
    public_card['revalidated_by'] = '2026-10-25 Arena review; existing-primary format checks refreshed, no new scientific evaluation'
    validate_status(public_card, root, status['file'])
    public_text = json.dumps(public_card, indent=2, allow_nan=False) + '\n'
    outputs[public_card_path] = public_text
    outputs[root / 'docs/downloads/arena_review_run_card_20261025.json'] = public_text
    public_panel = render_status(public_card)
    for alias in ('SUBMIT_NOW.html', 'index_new.html'):
        outputs[root / 'docs' / alias] = install_panel(retired_page(), public_panel)
    outputs[root / 'docs/downloads/knickloqo_submission_run_card.json'] = (
        json.dumps(corrected_knickloqo_receipt(root), indent=2, allow_nan=False) + '\n')
    for page in PAGES:
        path = root / 'docs' / page
        outputs[path] = render_page(install_panel(path.read_text(), public_panel), block)
    # Publish the freshly verified rejection proof with exact source bytes.
    outputs[root / 'docs/downloads/preplacement_stop_20261025_arena.json'] = (root / 'evidence/preplacement_stop_20261025_arena.json').read_text()
    stale = []
    for path, expected in outputs.items():
        if not path.exists() or path.read_text() != expected:
            stale.append(str(path.relative_to(root)))
            if not check:
                path.write_text(expected)
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        stale = sync(check=args.check)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'READINESS FAIL: {exc}', file=sys.stderr)
        return 1
    if args.check and stale:
        print('READINESS FAIL: stale current status: ' + ', '.join(stale))
        return 1
    print('READINESS PASS: current research download revalidated; submission remains blocked')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
