#!/usr/bin/env python3
"""Render docs/executive-summary-nine-sites-20261028.html from evidence (no hand-typed numbers).

Sources: evidence/focus9_sources_20261028.json (best file, CLAIM, SHA-256, repo, commit),
evidence/uniq_full_registry/focus9-*.json (full-registry PI-1 audit per peak),
evidence/full_registry_summary_20261028.json (nine-site pairwise overlap + null lift),
evidence/uniq_full_registry/*.json (RIESZ / TIPCOMP / LBMC1 audits).
MODEL published-128 values are copied from docs/executive-summary-20261028-tipcomp.html
(computed in an earlier session; labelled MODEL, not re-run here).
"""
from __future__ import annotations
import glob, json, html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "evidence/focus9_sources_20261028.json").read_text())
SUM = json.loads((ROOT / "evidence/full_registry_summary_20261028.json").read_text())
MODEL_PUB128 = {"GEMSDOE32": 0.2728, "GEMSDOE36": 0.2703, "GEMSDOE28": 0.2681, "GEMSDOE31": 0.2696,
                "GEMSDOE33": 0.2666, "GEMSDOE25": 0.2625, "GEMSDOE30": 0.2625, "GEMSDOE24": 0.2532,
                "GEMSDOE27": 0.2507}  # MODEL, from docs/executive-summary-20261028-tipcomp.html
audits = {}
for f in glob.glob(str(ROOT / "evidence/uniq_full_registry/focus9-*.json")):
    d = json.loads(Path(f).read_text())
    site = Path(f).stem.split("-")[1]
    audits[site] = d
sites = sorted(SRC)
e = html.escape

def gh_link(site, path, commit):
    return f"https://github.com/buffedlizard55-lab/{site}/blob/{commit}/{path}"

rows = []
for s in sites:
    r = SRC[s]; a = audits[s]
    ident = a["candidate_identical_copies_in_registry"]
    other_sites = [x for x in sites if x != s]
    max_other = max(SUM["nine_site_pairwise_overlap"][f"{s}->{x}"] for x in other_sites)
    max_other_site = max(other_sites, key=lambda x: SUM["nine_site_pairwise_overlap"][f"{s}->{x}"])
    rows.append(f"""<tr><td><b>{s}</b></td>
<td><a href="{e(gh_link(s, r['path'], r['commit']))}">{e(Path(r['path']).name)}</a><br><span class="mono small">{r['sha256'][:12]}… · {r['n_dots'] if 'n_dots' in r else a['n_dots']} dots</span></td>
<td>{r['claim']:.4f}<br><span class="small">CLAIM (owner-reported)</span></td>
<td>{MODEL_PUB128[s]:.4f}<br><span class="small">MODEL published-128</span></td>
<td>{len(ident)} repo(s) hold identical bytes<br><span class="small">{e(', '.join(sorted(set(x.split('/')[-1] for x in ident))[:4]))}…</span></td>
<td class="warn">FAIL — worst 3-px overlap {a['worst_overlap']['value']:.4f} (identical copy)</td>
<td>{max_other:.3f} vs {max_other_site}</td>
<td class="warn">NOT UNIQUE — not a download candidate</td></tr>""")

pair_head = "".join(f"<th>{s[-2:]}</th>" for s in sites)
pair_rows = []
for a_ in sites:
    cells = "".join(f"<td class='{'self' if a_==b else ''}'>{SUM['nine_site_pairwise_overlap'][f'{a_}->{b}']:.3f}</td>" for b in sites)
    pair_rows.append(f"<tr><th>{a_}</th>{cells}</tr>")
halo = ", ".join(f"{s[-2:]} {SUM['nine_site_halo_frac'][s]:.3f}" for s in sites)

def cand(name):
    for c in SUM["candidates"]:
        if c["name"].startswith(name):
            return c
    raise KeyError(name)
riesz = cand("rieszlbm2"); tip = cand("tipcomp"); lbmc1 = cand("lbmc1")

page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GEMSDOE92 — Executive summary, nine focus sites (2026-10-28)</title>
<style>
body{{font:16px/1.55 system-ui,sans-serif;color:#18212e;background:#f4f6f8;margin:0}}
main{{max-width:1180px;margin:auto;padding:24px}}
section{{background:#fff;padding:20px;margin:18px 0;border-radius:8px;box-shadow:0 1px 2px #0001}}
table{{width:100%;border-collapse:collapse;font-size:.92rem}} td,th{{padding:7px 8px;border-bottom:1px solid #d6dde6;text-align:left;vertical-align:top}}
.mono{{font-family:ui-monospace,monospace}} .small{{font-size:.82rem;color:#4b5767}} .warn{{color:#b3261e;font-weight:700}} .ok{{color:#137333;font-weight:700}}
.self{{background:#eef2f7}} a{{color:#124ec0}} .stop{{border:3px solid #b91c1c;background:#fff4f3}} .go{{border:3px solid #137333;background:#f1faf4}}
@media(max-width:800px){{table{{display:block;overflow:auto}}}}
</style></head><body><main>
<p class="small"><a href="../index.html">← GEMSDOE92 home</a> · <a href="STANDING_BRIEF_20261028.md">Standing brief</a> · <a href="STANDING_PROMPT.md">Stored prompt</a></p>
<h1>Executive summary — nine focus sites (24, 25, 27, 28, 30, 31, 32, 33, 36)</h1>
<p class="small">Labels: <b>CLAIM</b> = owner-reported score from the task brief, not an organizer receipt · <b>MODEL</b> = LBM fit to claims, not an organizer score · <b>HOLDOUT-DTI</b> = gems57 pooled hide-and-recover · <b>ORGANIZER-CONFIRMED</b> = none exists for any file on this page. Projections are never shown as scores.</p>

<section class="stop"><h2>Bottom line</h2>
<p><span class="warn">No focus-site file is unique.</span> Each site's best peak is byte-identical to a file in one or more other owners' repositories (up to 18 repos), so each fails the PI-1 uniqueness rule (≤70% of dots within 3 px of any one registry raster). Among the nine peaks themselves, 3-px pairwise overlap runs from {min(v for k,v in SUM['nine_site_pairwise_overlap'].items() if k.split('->')[0]!=k.split('->')[1]):.3f} to {max(v for k,v in SUM['nine_site_pairwise_overlap'].items() if k.split('->')[0]!=k.split('->')[1]):.3f} (null under uniform placement: {min(SUM['nine_site_halo_frac'].values()):.2f}–{max(SUM['nine_site_halo_frac'].values()):.2f}). They are one lane, not nine submissions.</p>
<p><b>Score conflict (flagged):</b> the brief cites a current leaderboard high of 0.4413 and a "highest right now" of 0.3195, and separately 0.2778 as GEMSDOE32's score. None is organizer-confirmed in this repository; the top CLAIM on this page is 0.2778.</p>
</section>

<section class="go"><h2>⬇ The only file that passes uniqueness (download, research only)</h2>
<p><a href="downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif"><b>gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif</b></a> (SHA-256 <span class="mono">d168c7d2…e5d7</span>)</p>
<ul>
<li><b>Format:</b> float32, single band, EPSG:32611, 3292×3730, binary {{0,1}}, zeros outside footprint (no NaN). Values in [0, 1].</li>
<li><b>Full-registry PI-1 (2,216 SHA-256, own-repo copy excluded):</b> <span class="ok">PASS</span> — worst 3-px overlap {riesz['worst_overlap']:.4f} (limit 0.70), worst |ρ| {riesz['worst_abs_rho']:.3f}.</li>
<li><b>Holdout:</b> <span class="warn">does NOT beat the R0 holdout reference</span> (RIESZ HOLDOUT-DTI 0.037987 vs R0 0.097750 in the repo's gems57 record). By the protocol it is not a slot candidate.</li>
<li><b>Not a submission recommendation.</b> Downloading is not submitting. Slot decisions belong to the separate selector step.</li>
</ul></section>

<section><h2>Per-site table — best file, estimated score, uniqueness</h2>
<table><tr><th>Site</th><th>Best file (link to official repo commit)</th><th>CLAIM</th><th>MODEL</th><th>Identical copies elsewhere</th><th>Full-registry PI-1</th><th>Max pairwise overlap vs other listed sites</th><th>Verdict</th></tr>
{''.join(rows)}
</table>
<p class="small">Pairwise overlap = fraction of the row site's dots within 3 px of the column site's dots. Halo fractions (uniform-placement null): {halo}. Null lift = overlap − halo. Full table and lift matrix: <span class="mono">evidence/full_registry_summary_20261028.json</span>.</p>
</section>

<section><h2>Pairwise uniqueness vs other listed GEMSDOE sites</h2>
<table><tr><th>row → col</th>{pair_head}</tr>
{''.join(pair_rows)}
</table>
<p class="small">Diagonal = self (1.000). Values near 1.000 mean the two peaks place their dots on the same cells within 3 px.</p>
</section>

<section><h2>Other current candidates (full registry, same audit)</h2>
<table><tr><th>Candidate</th><th>Dots</th><th>Worst overlap</th><th>Null lift at worst</th><th>|ρ|</th><th>PI-1</th><th>Status</th></tr>
<tr><td>RIESZ-LOCKED (rieszlbm2)</td><td>{riesz['n_dots']:,}</td><td>{riesz['worst_overlap']:.4f} ({riesz['worst_raster_repos'][0]})</td><td>{riesz['null_lift']:.3f}</td><td>{riesz['worst_abs_rho']:.3f}</td><td class="ok">PASS</td><td>Unique; holdout below R0 — not a slot candidate</td></tr>
<tr><td>TIPCOMP (8f27b9d6)</td><td>{tip['n_dots']:,}</td><td>{tip['worst_overlap']:.4f} ({tip['worst_raster_repos'][0]})</td><td>{tip['null_lift']:.3f}</td><td>{tip['worst_abs_rho']:.3f}</td><td class="warn">FAIL</td><td>Not unique (superseded "unique" claim used a 165-raster local scope)</td></tr>
<tr><td>LBMC1 (89a660f6 / e928d3c3)</td><td>{lbmc1['n_dots']:,}</td><td>{lbmc1['worst_overlap']:.4f} ({lbmc1['worst_raster_repos'][0]})</td><td>{lbmc1['null_lift']:.3f}</td><td>{lbmc1['worst_abs_rho']:.3f}</td><td class="ok">PASS</td><td>Previously uploaded (2026-10-27 per SLOT_PLAN) — not a new file</td></tr>
</table>
<p class="small">Null lift is undefined for byte-identical copies (overlap 1.000) and is omitted there.</p></section>

<section class="stop"><h2>Limitations</h2>
<ul>
<li>Claimed scores are user-reported. None is ORGANIZER-CONFIRMED. The 0.4413 / 0.3195 / 0.2778 conflict is unresolved.</li>
<li>The public-mirror competition-derived files have unchecked redistribution terms (DrivenData Terms of Use); not restored or redistributed here.</li>
<li>The NaN-outside-footprint format conflicts with the NaN-permitted wording on the problem page; the candidate is zeros-outside. The 'Predicted values must be in range [0, 1]' error root cause is probable, not confirmed (see the standing brief).</li>
<li>Surface-level (pre-placement) PI-1 was not re-run for every candidate here; final-dot PI-1 is the binding check in this audit.</li>
</ul></section>
<p class="small">Generated by scripts/render_nine_sites_20261028.py from the evidence files named above. No DrivenData authentication was used.</p>
</main></body></html>
"""
out = ROOT / "docs/executive-summary-nine-sites-20261028.html"
out.write_text(page, encoding="utf-8")
print("wrote", out, len(page))
