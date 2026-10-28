"""Fail-closed presentation of the 2026-10-28 protocol review.

This renderer is intentionally rejection-only. It never infers eligibility from
model projections or from a format check. Inputs are historical owner claims and
run cards; they are not organizer receipts.
"""
from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
DL = DOCS / 'downloads'

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
    secondary_meta_path = DL / 'gemsdoe92-damagezone-close-dots-20261028-zeros.json'
    secondary = json.loads(secondary_meta_path.read_text()) if secondary_meta_path.is_file() else None
    secondary_section = ''
    if secondary:
        secondary_file = esc(secondary['file'])
        secondary_digest = esc(secondary['sha256'])
        secondary_section = f'''<section><h2>Separate candidate in repository — not cleared</h2>
<p><a href="downloads/{secondary_file}"><code>{secondary_file}</code></a> (SHA-256 <code>{secondary_digest}</code>) was added by a later merged change. It is not this review's selected artifact and was not run through an assigned-lane pre-registration or a full registry uniqueness gate. The local site checker validates format/range/grid only; that cannot authorize a competition slot.</p>
<p>The accompanying experiment note reports a local surrogate HOLDOUT-DTI of 0.05164 against an R0 raster at 0.00473, but below the recorded R0 recipe value of 0.09775; the label raster is byte-identical to the visible-fault catalogue according to the independent review. This is not evidence of generalization to missing faults. Keep this file research-only; do not submit. See <a href="HYPOTHESES_UNTRYED.md">the candidate note</a> and <a href="REVIEW_20261028_SESSION.md">independent limitations review</a>.</p></section>'''
    body = f'''<nav><a href="how-to-submit.html">How to submit</a> · <a href="nine-sites.html">Nine-site review</a> · <a href="REVIEW_20261028_B6AA.md">Full audit and next steps</a> · <a href="REVIEW_20261028_SESSION.md">Independent overlap review</a></nav>
<section id="submit-now" class="stop"><h1>DO NOT SUBMIT — no eligible new TIFF</h1>
<p>No competition slot was used. The prior Riesz candidate fails the requested literal registry rule and did not beat the holdout control. A range-valid raster is not automatically submission-ready.</p>
<p><a data-primary="true" href="downloads/{esc(file)}" download>Download existing Riesz TIFF for research only</a> · <a href="downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json">Historical run card, reclassified negative</a></p>
<p>SHA-256: <code>{digest}</code>. Historical name: <code>{name}</code>. Historical note (not an instruction to upload): <code>{note}</code></p></section>
<section id="summary"><h2>Executive summary</h2><p>No estimated competition score is available for a new, eligible TIFF. User-reported figures below are not organizer-confirmed, are not estimates, and may be stale. No receipt was obtained.</p>
<table><thead><tr><th>Site</th><th>Highest reported file — research only</th><th>Reported value</th><th>Unique and cleared?</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p>The focus inventory and overlap results are historical; a recent full scan is not available. The <a href="downloads/focus9_pairwise_recheck_14f85876.json">row-safe pairwise recheck</a> warns that earlier pairwise results contained errors. A separate pinned full-footprint witness causes a literal stop for any nonempty candidate, not a claim that every pair is byte-identical. A later measurement reports 0.00698 overlap under a top-K reading of this witness, versus 1.0 literally; the representation rule remains unresolved, so this alternate measurement is not clearance or a complete registry uniqueness scan. See the <a href="REVIEW_20261028_SESSION.md">independent review and receipt</a>.</p></section>
<section><h2>Why GEMSDOE32?</h2><p>Its supplied reported value is the highest among the nine, but is not independently verified. Thinning a prediction and excluding cells close to mapped faults could reduce redundant false-positive mass under a distance-tolerant metric. The hidden labels are unavailable, so the cause, absence of true faults near mapped traces, and whether any new method can exceed it are unknown. Prior fitted projections cannot establish that it will be beaten.</p>
<p>Historical HOLDOUT-DTI, <code>gems57-pooled-hide-v2</code>, 22,663 withheld positive pixels: Riesz candidate 0.03799 (95% CI 0.03101–0.04466) vs R0 recipe 0.09775 (95% CI 0.08590–0.11077). These previous measurements were not rerun in this session and may not be prospectively comparable. They are not leaderboard results. <a href="downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json">Evidence</a>.</p></section>
<section><h2>Next steps &amp; limitations</h2><p>The prompt refers to a single lane paragraph that is absent. The pinned dense witness makes the literal overlap criterion impossible for any nonempty in-footprint raster. Restore provenance-checked cached features and a complete registry, resolve the rule before experiments, then run leakage canaries, buffered visible-only holdouts, both registry checks and the shared writer. Separately select a candidate only if the gates pass. This environment cannot reach the organizer portal, USGS, Dropbox or GDR; portal rules, weekly limit and current leaderboard cannot be checked here.</p>
<p><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Official problem</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution">Official reference solution</a> · <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a> · <a href="https://gdr.openei.org/submissions/1391">INGENIOUS</a> · <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Rules PDF</a>. Only the GitHub reference was reachable in this session. The organizer leaderboard is not mirrored. <a href="https://www.drivendata.org/termsofuse/">DrivenData Terms of Use</a>.</p></section>{secondary_section}'''
    guide = f'''<nav><a href="index.html">Executive summary</a></nav><section class="stop"><h1>DO NOT SUBMIT — no eligible file</h1><p>The existing TIFF is for research only. Do not use a competition slot until the mandatory gates and separate selector pass.</p><p>Current research-only file: <code>{esc(file)}</code>; SHA-256 <code>{digest}</code>.</p></section><section><h2>How to submit when a candidate is cleared</h2><ol><li>Download the exact cleared single-band GeoTIFF (or ZIP with one GeoTIFF), without re-saving.</li><li>Open the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">official submission page</a>, check the weekly limit displayed there, and upload the file.</li><li>Use the chosen unique name and short note, submit, and record the organizer receipt. Do not use the historical name as a new submission.</li></ol><p>For “Predicted values must be in range [0, 1]”, validate actual raw pixels for non-finite values, nodata sentinels and values outside [0,1], including exterior pixels. Confirm CRS, shape and transform against the official template. Local checks cannot guarantee portal acceptance.</p></section>'''
    css = 'body{font:16px/1.55 system-ui;color:#18212e;background:#f4f6f8;margin:0}main{max-width:1100px;margin:auto;padding:24px}section{background:white;padding:20px;margin:18px 0;border-radius:8px}.stop{border:3px solid #b91c1c;background:#fff4f3}table{width:100%;border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #ccd5df;text-align:left;vertical-align:top}code{overflow-wrap:anywhere}a{color:#124ec0}@media(max-width:700px){table{display:block;overflow:auto}}'
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
    root = f'<p>The organizer leaderboard is not mirrored. <a href="https://www.drivendata.org/termsofuse/">DrivenData Terms of Use</a></p><h1>GEMSDOE92</h1><section class="stop"><h2>DO NOT SUBMIT — no eligible new TIFF</h2><p>Research-only file: <a href="docs/downloads/{esc(file)}"><code>{esc(file)}</code></a>; SHA-256 <code>{digest}</code>.</p><p><a href="docs/index.html">Read the executive summary and research downloads</a></p><p><a href="docs/how-to-submit.html">How to submit when cleared</a></p><p class=\"small\"><a href=\"docs/executive-summary-nine-sites-20261028.html\">Nine-site executive summary (uniqueness, pairwise overlap)</a> · <a href=\"docs/STANDING_BRIEF_20261028.md\">Standing brief</a> · <a href=\"docs/HYPOTHESES_20261028_STANDING.md\">Untried hypotheses</a> · <a href=\"docs/STANDING_PROMPT.md\">Stored prompt (reconstructed; verbatim pending)</a></p></section>'
    return {DOCS/'index.html':page('GEMSDOE92 — Executive summary',body), DOCS/'nine-sites.html':page('GEMSDOE92 — Nine-site review',body), DOCS/'how-to-submit.html':page('GEMSDOE92 — How to submit',guide), ROOT/'index.html':page('GEMSDOE92',root), DL/'current_submission.json':json.dumps(current,indent=2)+'\n',DL/'readiness.json':json.dumps(readiness,indent=2)+'\n'}
