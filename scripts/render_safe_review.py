"""Fail-closed presentation of the 2026-10-28 protocol review.

This renderer is intentionally rejection-only. It never infers eligibility from
model projections or from a format check. Inputs are historical owner claims and
run cards; they are not organizer receipts.
"""
from __future__ import annotations
import html
import json
from pathlib import Path

try:
    from scripts.render_20261029_pages import (
        load_lidarsintervalve_20261029,
        render_executive_summary_20261029,
        render_lidarsintervalve_hero,
    )
except ImportError:  # pragma: no cover - direct script execution from scripts/
    from render_20261029_pages import (  # type: ignore[no-redef]
        load_lidarsintervalve_20261029,
        render_executive_summary_20261029,
        render_lidarsintervalve_hero,
    )

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
DL = DOCS / 'downloads'

def load_blindcorridor_status():
    """Load and bind the additional format-only artifact without authorizing it."""
    import hashlib
    import math

    card_path = DL / 'gemsdoe92-blindcorridor-37654dots-20261028-11f8999c_run_card.json'
    if not card_path.is_file():
        return None
    try:
        card = json.loads(card_path.read_text(encoding='utf-8'))
        tif_name = Path(card['raster']['file']).name
        zip_name = Path(card['raster']['zip']).name
        tif_path = DL / tif_name
        zip_path = DL / zip_name
        audit_path = tif_path.with_name(tif_path.stem + '-audit.json')
        audit = json.loads(audit_path.read_text(encoding='utf-8'))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValueError(f'BLINDCORRIDOR evidence is incomplete: {exc}') from exc

    digest = hashlib.sha256(tif_path.read_bytes()).hexdigest() if tif_path.is_file() else None
    if digest is None or digest != card.get('raster_sha256') or digest != card.get('raster', {}).get('sha256'):
        raise ValueError('BLINDCORRIDOR raster SHA-256 does not match its run card')
    if not zip_path.is_file() or not audit_path.is_file():
        raise ValueError('BLINDCORRIDOR ZIP or format audit is missing')
    try:
        import zipfile
        with zipfile.ZipFile(zip_path) as archive:
            members = [name for name in archive.namelist() if not name.endswith('/')]
            if len(members) != 1 or Path(members[0]).name != tif_name:
                raise ValueError('BLINDCORRIDOR ZIP must contain exactly the bound TIFF')
            if hashlib.sha256(archive.read(members[0])).hexdigest() != digest:
                raise ValueError('BLINDCORRIDOR ZIP payload does not match the TIFF bytes')
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValueError(f'BLINDCORRIDOR ZIP is invalid: {exc}') from exc
    zip_digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    if card.get('verdict') != 'format_pass' or card.get('submission_eligible') is not False:
        raise ValueError('BLINDCORRIDOR must remain format_pass only and not submission-eligible')
    if audit.get('sha256_zeros') != digest or audit.get('verdict') != 'format_pass' or audit.get('submission_eligible') is not False:
        raise ValueError('BLINDCORRIDOR audit disagrees with its byte-bound run card')
    gates = audit.get('gates_zeros')
    if audit.get('overall_pass') is not True or not isinstance(gates, list) or not gates or any(row.get('ok') is not True for row in gates):
        raise ValueError('BLINDCORRIDOR format audit is missing or has a failing gate')

    holdout = card.get('holdout_dti', {})
    if (not isinstance(holdout, dict) or 'dti' in holdout or 'ci95' in holdout
            or 'evaluator_version' in holdout or 'withheld_positive_pixels' in holdout
            or card.get('leakage_canaries', {}).get('canaries_run') is not False):
        raise ValueError('BLINDCORRIDOR holdout/canary status changed; review and update required')
    uniqueness = card.get('uniqueness', {})
    references = uniqueness.get('references')
    if not isinstance(references, list) or not references:
        raise ValueError('BLINDCORRIDOR local reference scope is missing')
    measured_worst = max(float(ref['overlap_3px']) for ref in references)
    recorded_worst = float(uniqueness['worst_overlap_3px'])
    if not math.isclose(measured_worst, recorded_worst, rel_tol=0, abs_tol=1e-9):
        raise ValueError('BLINDCORRIDOR worst local overlap disagrees with its reference rows')

    status = {
        'schema': 'gemsdoe92-candidate-readiness-v1',
        'artifact': 'BLINDCORRIDOR',
        'file': f'downloads/{tif_name}',
        'zip': f'downloads/{zip_name}',
        'audit': audit_path.name,
        'run_card': card_path.name,
        'raster_sha256': digest,
        'zip_sha256': zip_digest,
        'submission_name': card['submission_name'],
        'note': card['note'],
        'verdict': 'format_pass',
        'submission_eligible': False,
        'download_status': 'OK TO DOWNLOAD FOR RESEARCH ONLY',
        'submission_status': 'DO NOT SUBMIT',
        'format_validation': {'status': 'recorded pass', 'gate_count': len(gates)},
        'holdout_dti': {'status': 'not independently computed', 'evidence_class': 'no HOLDOUT-DTI result'},
        'leakage_canaries': {'status': 'not run', 'canaries_run': False},
        'uniqueness': {
            'status': 'partial local check only',
            'scope': 'available bridge rasters only',
            'checked_reference_count': len(references),
            'worst_overlap_3px': recorded_worst,
            'full_registry_audit': 'not performed',
            'literal_dense_witness': 'unresolved',
        },
        'blocking_reasons': [
            'independent HOLDOUT-DTI and 95% CI are absent',
            'individual-feature leakage canaries were not run',
            'the full public registry uniqueness audit was not performed',
            'the literal dense-witness interpretation remains unresolved',
        ],
    }
    return card, audit, status


def render(card):
    if card.get('verdict') != 'negative' or card.get('submission_eligible') is not False:
        raise ValueError('blocked: review renderer cannot authorize promotion')
    esc = lambda x: html.escape(str(x), quote=True)
    sources = json.loads((ROOT / 'evidence/focus9_sources_20261028.json').read_text())
    unique = json.loads((ROOT / 'evidence/focus9_uniqueness_20261028.json').read_text())
    rows = []
    for site, d in sources.items():
        u = unique[site]
        if u['best'] != d['best'] or u['claim'] != d['claim']:
            raise ValueError('focus site records disagree')
        rows.append(f"<tr><td>{esc(site)}</td><td><a href=\"{esc(d['blob_url'])}\">{esc(d['best'])}</a> <small>(research only)</small></td><td>{d['claim']:.4f} user-reported, unverified</td><td>Fails historical registry test; not eligible</td></tr>")
    file = Path(card['raster']['file']).name
    name = esc(card['submission_name']); note = esc(card['note']); digest = esc(card['raster_sha256'])

    # Show the latest TIPCOMP artifact on the landing page, but keep it explicitly
    # research-only: its own byte-bound run card is negative and non-eligible.
    tipcomp_card_path = DL / 'gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6_run_card.json'
    tipcomp_section = ''
    if tipcomp_card_path.is_file():
        tipcomp = json.loads(tipcomp_card_path.read_text())
        tip_rel = tipcomp['raster']['file'].removeprefix('docs/')
        tip_file = DL / Path(tip_rel).name
        import hashlib
        if hashlib.sha256(tip_file.read_bytes()).hexdigest() != tipcomp.get('raster_sha256'):
            raise ValueError('TIPCOMP raster SHA-256 does not match its run card')
        if tipcomp.get('verdict') != 'negative' or tipcomp.get('submission_eligible') is not False:
            raise ValueError('review renderer cannot advertise a non-negative TIPCOMP candidate')
        h = tipcomp['holdout_dti']
        e2 = h['foldproper_e2']; control = h['r0_recipe_control']; paired = h['paired_e2_vs_r0_recipe']
        model = tipcomp['model_estimate']['candidate']
        registry = tipcomp['correlation_overlap_vs_registry']
        tipcomp_section = f'''<section class="stop"><h2>Latest additional candidate: TIPCOMP — DO NOT SUBMIT</h2>
<p><a href="downloads/{esc(Path(tip_rel).name)}" download>Download TIPCOMP GeoTIFF for research only — DO NOT SUBMIT</a> ·
<a href="downloads/{esc(tipcomp_card_path.name)}">byte-bound run card</a> ·
<a href="executive-summary-20261028-tipcomp.html">full experiment summary</a></p>
<p>SHA-256 <code>{esc(tipcomp['raster_sha256'])}</code>. Local format validation was recorded as 11/11 gates PASS; that is only file-format validation, not science or organizer acceptance. Metadata is archived for audit and is not a portal-upload recommendation.</p>
<table><tr><th>Estimated value</th><td><code>MODEL</code>, not a score: published-128 estimate {model['published128']:.4f}; 26-claim refit {model['refit26']:.4f} (bootstrap q05 {model['bootstrap_refit26']['q05']:.4f}). The pre-registered q05 bound 0.2778 was not met.</td></tr>
<tr><th>HOLDOUT-DTI</th><td><code>{esc(e2['evaluator_version'])}</code>, {e2['withheld_positive_pixels']:,} withheld positives: fold-proper TIPCOMP {e2['dti']:.5f} [{e2['ci95'][0]:.5f}, {e2['ci95'][1]:.5f}]; R0-recipe control {control['dti']:.5f} [{control['ci95'][0]:.5f}, {control['ci95'][1]:.5f}]; paired difference {paired['delta']:.5f} [{paired['ci95'][0]:.5f}, {paired['ci95'][1]:.5f}] (CI spans zero; no holdout win).</td></tr>
<tr><th>Uniqueness scope</th><td>The archived PI-1 measurement reports {registry['registry_unique_rasters']} local rasters, max dot overlap {registry['worst_overlap']['value']:.5f}, and max sampled |ρ| {registry['worst_abs_rho_surface']['value']:.5f}. This is not a complete registry scan and does not resolve the dense-witness interpretation; do not claim global uniqueness.</td></tr>
<tr><th>Decision</th><td><strong>DO NOT SUBMIT.</strong> Run card verdict is negative and <code>submission_eligible=false</code>. No slot was selected. No organizer-confirmed score is recorded.</td></tr></table></section>'''

    blindcorridor = load_blindcorridor_status()
    blindcorridor_section = ''
    blindcorridor_feed_path = DL / 'blindcorridor_readiness_20261028.json'
    if blindcorridor:
        blind_card, blind_audit, blind_status = blindcorridor
        blind_file = Path(blind_status['file']).name
        blind_zip = Path(blind_status['zip']).name
        blind_refs = blind_card['uniqueness']['references']
        blind_worst = blind_status['uniqueness']['worst_overlap_3px']
        blind_model = blind_card.get('model_estimate', {}).get('projection', 'not recorded')
        blindcorridor_section = f'''<section id="blindcorridor" class="stop"><h2>Latest additional artifact: BLINDCORRIDOR — FORMAT PASS ONLY; DO NOT SUBMIT</h2>
<p><a href="downloads/{esc(blind_file)}" download>Download GeoTIFF for research only — DO NOT SUBMIT</a> ·
<a href="downloads/{esc(blind_zip)}" download>one-TIFF ZIP (research only)</a> ·
<a href="downloads/{esc(blind_status['run_card'])}">byte-bound run card</a> ·
<a href="downloads/{esc(blind_status['audit'])}">format audit</a> ·
<a href="downloads/{esc(blindcorridor_feed_path.name)}">readiness feed</a></p>
<p>SHA-256 <code>{esc(blind_status['raster_sha256'])}</code>. The stored file-format audit records {blind_status['format_validation']['gate_count']}/{blind_status['format_validation']['gate_count']} gates PASS; this is not scientific validation or upload approval.</p>
<table><tr><th>Run-card projection</th><td><code>MODEL</code>, not a score: {esc(blind_model)}. The run card has no independent <code>HOLDOUT-DTI</code> or 95% CI, so this projection is not validated and is not a submission basis.</td></tr>
<tr><th>HOLDOUT-DTI</th><td>Not independently computed; withheld-positive count and 95% CI are absent.</td></tr>
<tr><th>Leakage canaries</th><td>Not run on the full feature stack.</td></tr>
<tr><th>Local overlap scope</th><td>Recorded worst 3-px overlap {blind_worst:.6f} across {len(blind_refs)} available bridge references only. The full registry audit was not performed; the literal dense-witness interpretation remains unresolved. This is not globally unique or cleared.</td></tr>
<tr><th>Decision</th><td><strong>DO NOT SUBMIT.</strong> Run card says <code>verdict=format_pass</code> and <code>submission_eligible=false</code>. Do not use the stored submission name or note as upload instructions.</td></tr></table></section>'''

    secondary_meta_path = DL / 'gemsdoe92-damagezone-close-dots-20261028-zeros.json'
    secondary = json.loads(secondary_meta_path.read_text()) if secondary_meta_path.is_file() else None
    secondary_section = ''
    if secondary:
        secondary_file = esc(secondary['file'])
        secondary_digest = esc(secondary['sha256'])
        secondary_section = f'''<section><h2>Separate candidate in repository — not cleared</h2>
<p><a href="downloads/{secondary_file}"><code>{secondary_file}</code></a> (SHA-256 <code>{secondary_digest}</code>) was added by a later merged change. It is not this review's selected artifact and was not run through an assigned-lane pre-registration or a full registry uniqueness gate. The local site checker validates format/range/grid only; that cannot authorize a competition slot.</p>
<p>The accompanying experiment note reports a local surrogate HOLDOUT-DTI of 0.05164 against an R0 raster at 0.00473, but below the recorded R0 recipe value of 0.09775; the label raster is byte-identical to the visible-fault catalogue according to the independent review. This is not evidence of generalization to missing faults. Keep this file research-only; do not submit. See <a href="HYPOTHESES_UNTRYED.md">the candidate note</a> and <a href="REVIEW_20261028_SESSION.md">independent limitations review</a>.</p></section>'''
    legacy_knickloqo = '''<!-- KNICKLOQO:BEGIN -->
<section class="stop" id="historical-knickloqo"><h2>Historical KNICKLOQO record — DO NOT SUBMIT</h2>
<p>This superseded diagnostic recorded literal registry overlap <strong>1.000 &gt; 0.70</strong>; a sparse matched-budget reading was diagnostic only and did not clear any weekly slot. It is retained for audit, not as a candidate recommendation.</p>
</section>
<!-- KNICKLOQO:END -->'''
    lsv29 = load_lidarsintervalve_20261029()
    lsv_hero = render_lidarsintervalve_hero(lsv29[0], lsv29[2]) if lsv29 else ''
    lsv_root_hero = render_lidarsintervalve_hero(lsv29[0], lsv29[2], href_prefix='docs/') if lsv29 else ''
    body = f'''<p class="small"><a href="executive-summary-20261029-lidarsintervalve.html"><strong>2026-10-29 Nine-Site &amp; 8-Owner Executive Summary</strong></a> · <a href="executive-summary-nine-sites-20261028.html">2026-10-28 Nine-site summary</a> · <a href="WHY_0_2778_AND_0_2784_20261029.md">Why 0.2778 vs 0.2784</a> · <a href="HYPOTHESES_20261029_LIDAR_SINTERVALVE.md">2026-10-29 Untried hypotheses</a> · <a href="STANDING_PROMPT.md">Standing prompt</a></p><nav><a href="how-to-submit.html">How to submit</a> · <a href="nine-sites.html">Nine-site review</a> · <a href="executive-summary-20261029-lidarsintervalve.html">2026-10-29 Full Audit</a> · <a href="REVIEW_20261028_MAIN_INTEGRATION.md">Main-integration review</a> · <a href="REVIEW_20261028_B6AA.md">Historical audit</a> · <a href="REVIEW_20261028_SESSION.md">Independent overlap review</a></nav>
{lsv_hero}
<section id="submit-now" class="stop"><h1>DO NOT SUBMIT — no eligible new TIFF</h1>
<p>No competition slot was used. The prior Riesz candidate fails the requested literal registry rule and did not beat the holdout control. A range-valid raster is not automatically submission-ready.</p>
<p><a data-primary="true" href="downloads/{esc(file)}" download>Download existing Riesz TIFF for research only</a> · <a href="downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json">Historical run card, reclassified negative</a></p>
<p>SHA-256: <code>{digest}</code>. Historical name: <code>{name}</code>. Historical note (not an instruction to upload): <code>{note}</code></p></section>
{tipcomp_section}
{blindcorridor_section}
{legacy_knickloqo}
<section id="summary"><h2>Executive summary</h2><p>No estimated competition score is available for a new, eligible TIFF. User-reported figures below are not organizer-confirmed, are not estimates, and may be stale. No receipt was obtained.</p>
<table><thead><tr><th>Site</th><th>Highest reported file — research only</th><th>Reported value</th><th>Unique and cleared?</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p>The focus inventory and overlap results are historical; a recent full scan is not available. The <a href="downloads/focus9_pairwise_recheck_14f85876.json">row-safe pairwise recheck</a> warns that earlier pairwise results contained errors. A separate pinned full-footprint witness causes a literal stop for any nonempty candidate, not a claim that every pair is byte-identical. A later measurement reports 0.00698 overlap under a top-K reading of this witness, versus 1.0 literally; the representation rule remains unresolved, so this alternate measurement is not clearance or a complete registry uniqueness scan. See the <a href="REVIEW_20261028_SESSION.md">independent review and receipt</a>.</p></section>
<section><h2>Why GEMSDOE32?</h2><p>Its supplied reported value is the highest among the nine, but is not independently verified. Thinning a prediction and excluding cells close to mapped faults could reduce redundant false-positive mass under a distance-tolerant metric. The hidden labels are unavailable, so the cause, absence of true faults near mapped traces, and whether any new method can exceed it are unknown. Prior fitted projections cannot establish that it will be beaten.</p>
<p>Historical HOLDOUT-DTI, <code>gems57-pooled-hide-v2</code>, 22,663 withheld positive pixels: Riesz candidate 0.03799 (95% CI 0.03101–0.04466) vs R0 recipe 0.09775 (95% CI 0.08590–0.11077). These previous measurements were not rerun in this session and may not be prospectively comparable. They are not leaderboard results. <a href="downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json">Evidence</a>.</p></section>
<section><h2>Next steps &amp; limitations</h2><p>The prompt refers to a single lane paragraph that is absent. The pinned dense witness makes the literal overlap criterion impossible for any nonempty in-footprint raster. Restore provenance-checked cached features and a complete registry, resolve the rule before experiments, then run leakage canaries, buffered visible-only holdouts, both registry checks and the shared writer. Separately select a candidate only if the gates pass. This environment cannot reach the organizer portal, USGS, Dropbox or GDR; portal rules, weekly limit and current leaderboard cannot be checked here.</p>
<p><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Official problem</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution">Official reference solution</a> · <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a> · <a href="https://gdr.openei.org/submissions/1391">INGENIOUS</a> · <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Rules PDF</a>. Only the GitHub reference was reachable in this session. The organizer leaderboard is not mirrored. <a href="https://www.drivendata.org/termsofuse/">DrivenData Terms of Use</a>.</p></section>{secondary_section}'''
    guide = f'''<nav><a href="index.html">← Main Landing Page</a> · <a href="executive-summary-20261029-lidarsintervalve.html">2026-10-29 Nine-Site Executive Summary</a> · <a href="nine-sites.html">Nine-site review</a></nav>
{lsv_hero}
<section class="stop"><h1>DO NOT SUBMIT — no new candidate is authorized for a weekly slot</h1>
<p><strong>2026-10-29 LIDAR-SINTERVALVE status:</strong> <code>gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e-zeros.tif</code> achieved a new repository fold-proper <code>HOLDOUT-DTI</code> high (<code>0.178619</code> [<code>0.163071</code>, <code>0.193316</code>], 54/54 leakage canaries PASS, sparse PI-1 overlap <code>0.6909 &le; 0.70</code> across all 2,263 unique SHA-256 rasters, 11/11 portal format gates PASS), but remains <strong>OK TO DOWNLOAD FOR RESEARCH ONLY · DO NOT SUBMIT</strong> because its paired 95% CI vs <code>control_netexpand_far</code> (<code>0.177976</code>) spans zero [<code>-0.002525</code>, <code>+0.004321</code>] and the literal dense-witness rule (<code>17GEMSDOE</code>, overlap <code>1.000 &gt; 0.70</code>) remains unresolved.</p>
<p><strong>Already-submitted 0.2784 entry:</strong> <code>gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif</code> (<code>0.2784</code> <code>CLAIM</code> — #1 in the 8-owner fleet) has already been submitted; <strong>do NOT re-upload it</strong>.</p>
<p><strong>Historical artifacts (DO NOT SUBMIT):</strong> <code>BLINDCORRIDOR</code> is a format pass only (<code>submission_eligible=false</code>, no independent <code>HOLDOUT-DTI</code>, and full-registry PI-1 overlap is <code>0.7691 &gt; 0.70</code> vs <code>13GEMSDOE</code>). The status-feed primary remains research-only file <code>{esc(file)}</code>; SHA-256 <code>{digest}</code>. See the <a href="index.html#blindcorridor">BLINDCORRIDOR audit and download status</a>.</p></section>
<section><h2>How to submit when a future candidate is explicitly cleared (3-per-week rolling limit)</h2>
<ol>
<li>Verify locally with zero manual pixel inspection: run <code>.venv/bin/python validate_submission.py path/to/candidate-zeros.tif</code> and confirm <code>RESULT: PASS (11 gates)</code> and an explicitly promoted byte-bound <code>_run_card.json</code>.</li>
<li>Download the exact cleared single-band GeoTIFF (<code>*-zeros.tif</code>) or single-TIFF <code>.zip</code> directly without opening or re-saving in desktop GIS software.</li>
<li>Open the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">official DrivenData submission page</a>, verify the rolling weekly limit (<strong>3 per week</strong> rolling 168-hour window; 1 entity per rules §3.4), upload the file, enter the unique submission name and short note (&le;140 chars), submit, and record the organizer receipt timestamp and score in <code>ledger/submissions.csv</code>. Do not reuse historical names.</li>
</ol></section>
<section><h2>Fixing “Predicted values must be in range [0, 1]” Automatically</h2>
<p>DrivenData's validator reads the raw raster array without masking nodata tags. Any <code>NaN</code> outside the <code>5,167,373</code>-cell footprint (as present in <code>sample_submission.tif</code>), any GDAL sentinel (e.g. <code>-9999</code> or <code>-3.4e38</code>), any uncalibrated logit outside <code>[0, 1]</code>, or a multi-file ZIP triggers <code>Predicted values must be in range [0, 1]</code>.</p>
<p>All <code>*-zeros.tif</code> artifacts in <code>GEMSDOE92</code> are written by <code>vendor/gems57/submission_writer.py</code> (single-band <code>float32</code>, <code>EPSG:32611</code>, <code>3730×3292</code> H×W / <code>3292×3730</code> W×H, <code>nodata=None</code>, <code>0.0</code> outside footprint, <code>np.clip(arr, 0.0, 1.0)</code> inside footprint) and verified automatically by <code>gems.gates</code> + <code>gems57.validate</code>:</p>
<pre><code>.venv/bin/python -m gems validate docs/downloads/gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e-zeros.tif \\
  --reference data/bridge/sample_submission.tif \\
  --catalogue data/bridge/existing_faults.tif --prune-radius 2</code></pre>
<p>Local checks verify file specification and range compliance automatically; they cannot guarantee portal acceptance without live portal access.</p></section>'''
    css = 'body{font:16px/1.55 system-ui;color:#18212e;background:#f4f6f8;margin:0}main{max-width:1100px;margin:auto;padding:24px}section{background:white;padding:20px;margin:18px 0;border-radius:8px}.stop{border:3px solid #b91c1c;background:#fff4f3}table{width:100%;border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #ccd5df;text-align:left;vertical-align:top}code{overflow-wrap:anywhere}pre{background:#f1f5f9;padding:12px;border-radius:6px;overflow:auto}a{color:#124ec0}@media(max-width:700px){table{display:block;overflow:auto}}'
    def page(title, content):
        prefix = '<aside>Current review: DO NOT SUBMIT · <a href="' + ('docs/' if title == 'GEMSDOE92' else '') + 'review-47314b7f.html">Independent review</a></aside><details data-status-archive="true"><summary>Earlier independent review</summary><p>See linked review; historical clearance is superseded.</p></details>'
        return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{css}</style></head><body><main>{prefix}{content}</main></body></html>\n'
    uniqueness = card.get('uniqueness', {})
    literal = uniqueness.get('literal_reading', {})
    holdout = card.get('holdout_dti', {})
    candidate_dti = holdout.get('exp1', {}).get('dti')
    r0_dti = holdout.get('r0_recipe_control', {}).get('dti')
    paired_ci = holdout.get('paired_delta_vs_r0_recipe', {}).get('ci95')
    blockers = []
    surface_overlap = uniqueness.get('surface_worst_overlap')
    if surface_overlap is None or float(surface_overlap) > 0.70:
        blockers.append('pre-placement surface overlap is missing or exceeds 0.70')
    if literal.get('duplicate_under_literal') is not False:
        blockers.append('literal full-support registry witness triggers the Rule 1 duplicate stop')
    if (candidate_dti is None or r0_dti is None or float(candidate_dti) <= float(r0_dti)
            or not isinstance(paired_ci, list) or len(paired_ci) != 2 or float(paired_ci[0]) <= 0):
        blockers.append('HOLDOUT-DTI did not beat the R0 recipe control with paired 95% CI above zero')
    canary_auc = card.get('leakage_canaries', {}).get('max_auc')
    if canary_auc is None or float(canary_auc) > 0.90:
        blockers.append('feature-alone leakage canary is missing or exceeds AUC 0.90')
    reason = 'Research only; mandatory promotion protocol gates failed.'
    current = {'file': card['raster']['file'], 'sha256':card['raster_sha256'], 'submission_name':card['submission_name'], 'note':card['note'], 'verdict':'negative','ok_to_download':True,'ok_to_submit':False,'reason':reason,'blocking_reasons':blockers, 'run_card': 'downloads/'+Path(card['raster']['file']).name.replace('-zeros.tif','_run_card.json')}
    readiness = {'file':'downloads/'+file, 'raster_sha256':card['raster_sha256'],'submission_name':card['submission_name'],'note':card['note'], 'verdict':'negative','submission_eligible':False,'download_status':'OK TO DOWNLOAD FOR RESEARCH','submission_status':'DO NOT SUBMIT','reason':reason,'blocking_reasons':blockers,'gates':card.get('gates_passed',{})}
    root = f'<p>The organizer leaderboard is not mirrored. <a href="https://www.drivendata.org/termsofuse/">DrivenData Terms of Use</a></p><h1>GEMSDOE92</h1><p class="small"><a href="docs/executive-summary-20261029-lidarsintervalve.html"><strong>2026-10-29 Nine-site &amp; 8-owner executive summary</strong></a> · <a href="docs/executive-summary-nine-sites-20261028.html">2026-10-28 Nine-site summary</a> · <a href="docs/WHY_0_2778_AND_0_2784_20261029.md">Why 0.2778 vs 0.2784</a> · <a href="docs/HYPOTHESES_20261029_LIDAR_SINTERVALVE.md">2026-10-29 Untried hypotheses</a> · <a href="docs/STANDING_PROMPT.md">Standing prompt</a></p>{lsv_root_hero}<section class="stop"><h2>DO NOT SUBMIT — no eligible new TIFF</h2><p>Research-only file: <a href="docs/downloads/{esc(file)}"><code>{esc(file)}</code></a>; SHA-256 <code>{digest}</code>.</p><p>The additional BLINDCORRIDOR artifact is format-pass only and also <strong>DO NOT SUBMIT</strong>; see its <a href="docs/index.html#blindcorridor">byte-bound status and audit</a>.</p><p><a href="docs/index.html">Read the executive summary and research downloads</a></p><p><a href="docs/how-to-submit.html">How to submit when cleared</a></p></section>'
    outputs = {
        DOCS/'index.html': page('GEMSDOE92 — Executive summary', body),
        DOCS/'nine-sites.html': page('GEMSDOE92 — Nine-site review', body),
        DOCS/'how-to-submit.html': page('GEMSDOE92 — How to submit', guide),
        ROOT/'index.html': page('GEMSDOE92', root),
        DL/'current_submission.json': json.dumps(current, indent=2)+'\n',
        DL/'readiness.json': json.dumps(readiness, indent=2)+'\n',
    }
    if lsv29:
        outputs[DOCS/'executive-summary-20261029-lidarsintervalve.html'] = render_executive_summary_20261029(lsv29[0], lsv29[2])
    if blindcorridor:
        outputs[blindcorridor_feed_path] = json.dumps(blind_status, indent=2)+'\n'
    return outputs
