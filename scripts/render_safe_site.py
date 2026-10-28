#!/usr/bin/env python3
"""Render a rejection-only site. This module cannot grant submission clearance."""
from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / 'docs/downloads/review_8857_run_card.json'
SOURCES = ROOT / 'evidence/focus9_sources_20261028.json'

def esc(s):
    return html.escape(str(s), quote=True)

def page(title, body):
    body += '<footer><a href="https://www.drivendata.org/termsofuse/">DrivenData terms</a></footer>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><style>body{{font:16px/1.55 system-ui;margin:0;background:#f4f6f8;color:#17202a}}main{{max-width:1050px;margin:auto;padding:1.5rem}}section{{background:white;border-radius:8px;padding:1.2rem;margin:1rem 0}}.stop{{border-left:7px solid #b42318}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #ddd;text-align:left;vertical-align:top;padding:.6rem;overflow-wrap:anywhere}}a{{color:#174ea6}}code{{overflow-wrap:anywhere}}.scroll{{overflow-x:auto}}</style></head><body><main>{body}</main></body></html>\n'''

def render():
    card = json.loads(CARD.read_text())
    if card['verdict'] != 'negative' or card['submission_eligible'] is not False:
        raise ValueError('rejection-only renderer cannot publish eligibility')
    sources = json.loads(SOURCES.read_text())
    rows = ''.join(f"<tr><td>{esc(site)}</td><td><a href='{esc(s['raw_url'])}'>{esc(s['best'])}</a> (study only)</td><td>{s['claim']:.4f} CLAIM</td><td>Not established; historical pairwise overlap fails</td><td>DO NOT SUBMIT</td></tr>" for site, s in sources.items())
    candidate = 'downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif'
    body = f'''<h1>GEMS submission workbench</h1><section class="stop" id="submit-now"><h2>DO NOT SUBMIT — no candidate currently cleared</h2><p>The previous clearance is withdrawn. A pinned continuous registry raster is positive at every candidate dot; under the literal overlap interpretation it fails the 70% gate. This is a representation-policy conflict, not proof of geological sameness. The candidate also fails the requested holdout-best gate. No weekly slot was used.</p><p><a href="{candidate}" data-primary="true">Download previous TIFF for research only</a> · <a href="downloads/review_8857_run_card.json">Negative run card</a> · <a href="how-to-submit.html">How to submit after clearance</a></p><p>Format check passed, but format validity is not submission eligibility. No defensible estimate of organizer score is provided.</p></section>
<section><h2>Executive summary — focus sites</h2><p>Scores below are user-reported CLAIMs, not organizer receipts. Files are historical research references, not eligible submission recommendations. Evidence is a dated snapshot, not a live feed.</p><div class="scroll"><table><tr><th>Site</th><th>Highest reported file</th><th>Reported score</th><th>Uniqueness vs sites</th><th>Clearance</th></tr>{rows}</table></div><p><a href="nine-sites.html">Detailed nine-site table</a> · <a href="https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/docs/REVIEW_20261027_D30D387C.md">Prior pairwise audit</a></p></section>
<section><h2>Why GEMSDOE32?</h2><p>The reported 0.2778 is a CLAIM, not an organizer-confirmed receipt. Previous analysis describes its pattern as a thinned dotted parent with mapped-fault exclusion; distance-tolerant coverage and reduced redundant placements are plausible contributors, not a causal proof. The private labels and organizer receipt are unavailable. It is not established that a new file beats this result or the differing leaderboard figures supplied in the prompt.</p><p>Previously reported HOLDOUT-DTI (gems57-pooled-hide-v2, 22,663 withheld pixels, 95% CI): candidate 0.03799 [0.03101, 0.04466], baseline 0.09775 [0.08590, 0.11077]. These are retrospective run-card values, not a fresh experiment or an estimate of the leaderboard.</p></section>
<section><h2>Next steps and sources</h2><p>Resolve the registry representation and assigned-lane ambiguity, then run the shared leakage canaries, buffered holdout and uniqueness checks before selecting a weekly slot. Existing <a href="HYPOTHESES_20261028_RIESZ_LOCKED.md">hypotheses</a> are historical and not independently validated in this review.</p><p><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Official competition description</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution">Official reference solution</a> · <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a> · <a href="https://gdr.openei.org/submissions/1391">DOE GDR INGENIOUS</a> · <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Official rules PDF</a>. External sites and live leaderboard were not independently accessed in this sandbox.</p></section>'''
    how = '''<h1>How to submit after clearance</h1><section class="stop"><h2>DO NOT SUBMIT NOW</h2><p>No eligible file is available. Format validation alone does not grant clearance. The weekly submission selector is a separate step; consult the current portal limit.</p></section><section><ol><li>Once all required checks pass, download the newly cleared GeoTIFF from the executive summary.</li><li>At the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">official submission portal</a>, choose the single-band GeoTIFF (or ZIP containing only that GeoTIFF).</li><li>Enter its supplied short note, submit within the portal's current cap, and preserve the organizer receipt.</li></ol><p>For “Predicted values must be in range [0, 1]”, validate every stored pixel, including outside the footprint, for finite values in that range; compare CRS, shape and transform to the official sample. Do not clip a file and presume it is cleared.</p><p><a href="index.html">Executive summary</a></p></section>'''
    nine = f'''<h1>Nine-site research summary</h1><p><strong>DO NOT SUBMIT:</strong> historic files are for research only. Reported numbers are CLAIMs, not receipts. The nine-site row-safe audit found every pair exceeded the duplicate criterion in at least one direction or rank. No independent score estimates or fresh registry-wide uniqueness guarantees are made.</p><div class="scroll"><table><tr><th>Site</th><th>Highest reported file</th><th>Reported score</th><th>Uniqueness</th><th>Decision</th></tr>{rows}</table></div><p><a href="index.html">Executive summary</a></p>'''
    current = {'verdict':'negative','submission_eligible':False,'ok_to_submit':False,'ok_to_download_for_research':True,'file':'docs/'+candidate,'reason':'literal registry overlap stop and holdout-best gate failed','run_card':'downloads/review_8857_run_card.json'}
    readiness = {'verdict':'negative','submission_eligible':False,'submission_status':'DO NOT SUBMIT','reason':current['reason'],'run_card':current['run_card']}
    return {ROOT/'docs/index.html':page('GEMS Executive Summary',body),ROOT/'docs/how-to-submit.html':page('How to submit',how),ROOT/'docs/nine-sites.html':page('Nine-site summary',nine),ROOT/'index.html':page('GEMS workbench','<h1>GEMS workbench</h1><p><strong>DO NOT SUBMIT.</strong> <a href="docs/index.html">Read the executive summary and evidence</a>.</p>'),ROOT/'docs/downloads/current_submission.json':json.dumps(current,indent=2)+'\n',ROOT/'docs/downloads/readiness.json':json.dumps(readiness,indent=2)+'\n'}

def main():
    for path,text in render().items():
        path.write_text(text,encoding='utf-8')
        print('wrote',path.relative_to(ROOT))
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
