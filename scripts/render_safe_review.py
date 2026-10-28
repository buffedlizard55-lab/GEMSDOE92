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
    body = f'''<nav><a href="how-to-submit.html">How to submit</a> · <a href="nine-sites.html">Nine-site review</a> · <a href="REVIEW_20261028_B6AA.md">Full audit and next steps</a></nav>
<section id="submit-now" class="stop"><h1>DO NOT SUBMIT — no eligible new TIFF</h1>
<p>No competition slot was used. The prior Riesz candidate fails the requested literal registry rule and did not beat the holdout control. A range-valid raster is not automatically submission-ready.</p>
<p><a data-primary="true" href="downloads/{esc(file)}" download>Download existing Riesz TIFF for research only</a> · <a href="downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json">Historical run card, reclassified negative</a></p>
<p>SHA-256: <code>{digest}</code>. Historical name: <code>{name}</code>. Historical note (not an instruction to upload): <code>{note}</code></p></section>
<section id="summary"><h2>Executive summary</h2><p>No estimated competition score is available for a new, eligible TIFF. User-reported figures below are not organizer-confirmed, are not estimates, and may be stale. No receipt was obtained.</p>
<table><thead><tr><th>Site</th><th>Highest reported file — research only</th><th>Reported value</th><th>Unique and cleared?</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p>The focus inventory and overlap results are historical; a recent full scan is not available. The <a href="downloads/focus9_pairwise_recheck_14f85876.json">row-safe pairwise recheck</a> warns that earlier pairwise results contained errors. A separate pinned full-footprint witness causes a literal stop for any nonempty candidate, not a claim that every pair is byte-identical.</p></section>
<section><h2>Why GEMSDOE32?</h2><p>Its supplied reported value is the highest among the nine, but is not independently verified. Thinning a prediction and excluding cells close to mapped faults could reduce redundant false-positive mass under a distance-tolerant metric. The hidden labels are unavailable, so the cause, absence of true faults near mapped traces, and whether any new method can exceed it are unknown. Prior fitted projections cannot establish that it will be beaten.</p>
<p>Historical HOLDOUT-DTI, <code>gems57-pooled-hide-v2</code>, 22,663 withheld positive pixels: Riesz candidate 0.03799 (95% CI 0.03101–0.04466) vs R0 recipe 0.09775 (95% CI 0.08590–0.11077). These previous measurements were not rerun in this session and may not be prospectively comparable. They are not leaderboard results. <a href="downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json">Evidence</a>.</p></section>
<section><h2>Next steps &amp; limitations</h2><p>The prompt refers to a single lane paragraph that is absent. The pinned dense witness makes the literal overlap criterion impossible for any nonempty in-footprint raster. Restore provenance-checked cached features and a complete registry, resolve the rule before experiments, then run leakage canaries, buffered visible-only holdouts, both registry checks and the shared writer. Separately select a candidate only if the gates pass. This environment cannot reach the organizer portal, USGS, Dropbox or GDR; portal rules, weekly limit and current leaderboard cannot be checked here.</p>
<p><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Official problem</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution">Official reference solution</a> · <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a> · <a href="https://gdr.openei.org/submissions/1391">INGENIOUS</a> · <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Rules PDF</a>. Only the GitHub reference was reachable in this session. The organizer leaderboard is not mirrored. <a href="https://www.drivendata.org/termsofuse/">DrivenData Terms of Use</a>.</p></section>'''
    guide = '''<nav><a href="index.html">Executive summary</a></nav><section class="stop"><h1>DO NOT SUBMIT — no eligible file</h1><p>The existing TIFF is for research only. Do not use a competition slot until the mandatory gates and separate selector pass.</p></section><section><h2>How to submit when a candidate is cleared</h2><ol><li>Download the exact cleared single-band GeoTIFF (or ZIP with one GeoTIFF), without re-saving.</li><li>Open the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">official submission page</a>, check the weekly limit displayed there, and upload the file.</li><li>Use the chosen unique name and short note, submit, and record the organizer receipt. Do not use the historical name as a new submission.</li></ol><p>For “Predicted values must be in range [0, 1]”, validate actual raw pixels for non-finite values, nodata sentinels and values outside [0,1], including exterior pixels. Confirm CRS, shape and transform against the official template. Local checks cannot guarantee portal acceptance.</p></section>'''
    css = 'body{font:16px/1.55 system-ui;color:#18212e;background:#f4f6f8;margin:0}main{max-width:1100px;margin:auto;padding:24px}section{background:white;padding:20px;margin:18px 0;border-radius:8px}.stop{border:3px solid #b91c1c;background:#fff4f3}table{width:100%;border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #ccd5df;text-align:left;vertical-align:top}code{overflow-wrap:anywhere}a{color:#124ec0}@media(max-width:700px){table{display:block;overflow:auto}}'
    def page(title, content):
        return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{css}</style></head><body><main>{content}</main></body></html>\n'
    current = {'file': card['raster']['file'], 'sha256':card['raster_sha256'], 'submission_name':card['submission_name'], 'note':card['note'], 'verdict':'negative','ok_to_download':True,'ok_to_submit':False,'reason':'Research only; literal duplicate stop and holdout below R0.', 'run_card': 'downloads/'+Path(card['raster']['file']).name.replace('-zeros.tif','_run_card.json')}
    readiness = {'file':'downloads/'+file, 'raster_sha256':card['raster_sha256'],'submission_name':card['submission_name'],'note':card['note'], 'verdict':'negative','submission_eligible':False,'download_status':'OK TO DOWNLOAD FOR RESEARCH','submission_status':'DO NOT SUBMIT','reason':current['reason']}
    root = '<p>The organizer leaderboard is not mirrored. <a href="https://www.drivendata.org/termsofuse/">DrivenData Terms of Use</a></p><h1>GEMSDOE92</h1><section class="stop"><h2>DO NOT SUBMIT — no eligible new TIFF</h2><p><a href="docs/index.html">Read the executive summary and research downloads</a></p><p><a href="docs/how-to-submit.html">How to submit when cleared</a></p></section>'
    return {DOCS/'index.html':page('GEMSDOE92 — Executive summary',body), DOCS/'nine-sites.html':page('GEMSDOE92 — Nine-site review',body), DOCS/'how-to-submit.html':page('GEMSDOE92 — How to submit',guide), ROOT/'index.html':page('GEMSDOE92',root), DL/'current_submission.json':json.dumps(current,indent=2)+'\n',DL/'readiness.json':json.dumps(readiness,indent=2)+'\n'}
