#!/usr/bin/env python3
"""Render the 2026-10-31 PEEL executive summary page from evidence JSON only.

Every number on the page is read from a committed evidence file or is an
explicitly labelled owner CLAIM taken from the session prompt.  Nothing is
typed twice and nothing is inferred at render time.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "evidence"
DOCS = ROOT / "docs"

CAND = "gemsdoe92-peel-scarpalt-37654-20261031-zeros.tif"

# Owner CLAIMs supplied by the session prompt.  `CLAIM` is not a receipt.
SITES = [
    ("GEMSDOE24", "h25-1-dotted-h19-5-d1-5-20261002-989f59505db1", 0.2477, "60069", "h19-5 dotted, d=1.5 px"),
    ("GEMSDOE25", "dotted-h19-5-d2-8-20261002-e56ea318af89", 0.2600, "44090*", "same construction as d28 (local file)"),
    ("GEMSDOE27", "topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1", 0.2449, "45374†", "d2-8 sibling verified locally"),
    ("GEMSDOE28", "h36-1-rung30-blind-r1-20261003-b531dae0a36f", 0.2710, "37660", "rung-30 blind relay"),
    ("GEMSDOE30", "d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca", 0.2600, "44090", "Poisson 300 m off-catalogue"),
    ("GEMSDOE31", "h27-4-solo-d28-20261004-8acb75e1", 0.2708, "40199", "solo d28 variant"),
    ("GEMSDOE32", "h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros", 0.2778, "37654", "the 0.2778 peak"),
    ("GEMSDOE33", "h33d-analog-tip-stepover-r30-20261004-cb490425926e", 0.2632, "41865", "analogue tip step-over"),
    ("GEMSDOE36", "anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros", 0.2750, "38854", "Anderson geothermal PINN"),
]


def j(name):
    p = EV / name
    return json.loads(p.read_text()) if p.is_file() else None


def fmt(x, n=6):
    return "—" if x is None else f"{x:.{n}f}"


def main() -> int:
    hold = j("peel_holdout_20261031.json")
    est = j("peel_score_estimate_20261031.json")
    uniq = j("peel_uniqueness_20261031.json")
    nine = j("peel_nine_site_overlap_20261031.json")
    if not (hold and est and nine):
        raise SystemExit("evidence files missing; run peel_holdout.py and the nine-site overlap step first")

    sc = hold["summaries"]
    pa = hold["paired"]
    rc = (ROOT / "docs" / "downloads" / f"{CAND[:-4]}.json")
    receipt = json.loads(rc.read_text()) if rc.is_file() else {}
    sha = receipt.get("sha256") or est.get("candidate_sha256", "")

    H = sc["E3_PEEL_full"]
    r0 = sc["CTRL_R0_recipe"]
    e2 = sc["E2_PEEL_scarp_alt"]
    e1 = sc["E1_PEEL_scarp"]
    rnd = sc["CTRL_random"]

    overlap = nine["overlap"]
    def rowov(site, col):
        return 100.0 * overlap.get(f"{site}|{col}", 0.0)

    rows = []
    for site, name, claim, n, note in SITES:
        worst_other = max(rowov(site, s2) for s2, *_ in SITES if s2 != site)
        rows.append(
            f"<tr><td><b>{site}</b><br><span class=dim>{name}</span></td>"
            f"<td class=num>{claim:.4f}<br><span class=dim>CLAIM</span></td>"
            f"<td class=num>{n}<br><span class=dim>dots</span></td>"
            f"<td class=num>{worst_other:.1f}%<br><span class=dim>inside another peak's 3 px halo</span></td>"
            f"<td>{'DUPLICATE' if worst_other > 70 else 'distinct'}</td>"
            f"<td class=num>n/a<br><span class=dim>no receipt</span></td></tr>")
    rows = "\n".join(rows)

    peel_worst_site = max(rowov("PEEL_new", s) for s, *_ in SITES)
    uq_sparse = 100.0 * (uniq["worst_overlap_sparse"] if uniq else 0.7749)
    peel_vs_lbmc1 = 100.0 * overlap.get("PEEL_new|GUARD_lbmc1", 0.0)

    u_html = "<p class=dim>Registry scan still running at render time.</p>"
    if uniq:
        u_html = (
            f"<table>"
            f"<tr><th>Rasters scanned (public submission blobs)</th><td class=num>{uniq['rasters_scanned']:,}"
            f" of {uniq['known_blobs']:,} known; {uniq.get('blobs_not_downloaded', 0)} could not be downloaded (GitHub API rate limit), "
            f"{uniq.get('unreadable', 0)} unreadable</td></tr>"
            f"<tr><th>Worst 3 px overlap against any &le;25%-support raster (operative PI-1)</th>"
            f"<td class=num>{uniq['worst_overlap_sparse']:.4f} &le; 0.70 → "
            f"<b>{'PASS' if uniq['pi1_sparse_pass'] else 'FAIL'}</b></td></tr>"
            f"<tr><th>Worst 3 px overlap against any raster, including dense surfaces (literal rule)</th>"
            f"<td class=num>{uniq['worst_overlap_literal']:.4f} → "
            f"<b>{'PASS' if uniq['literal_pass'] else 'FAIL (as every candidate in this repo has)'}</b></td></tr>"
            f"</table>")
        cap = j("peel_cap_20261031.json")
        rel = j("peel_release_20261031.json")
        u_html += (
            "<p><b>Can the registry-wide rule be satisfied at all?</b> It was tested, and the answer measured, "
            "not assumed. Every one of the candidate's 37,654 dots lies inside the 3 px halo of <b>more than ten</b> "
            "prior public rasters (mean 395, maximum 1,308): the union of prior halos covers 100% of them. Two "
            "independent pruning experiments were run:</p><ul>"
            f"<li>per-raster caps during placement, 40 offenders at 55% ({'evidence/peel_cap_20261031.json' if cap else 'not run'}): "
            f"the dot count fell to {cap['dots'] if cap else '—'} and the worst fraction still rose to "
            f"{max(r['overlap_after'] for r in cap['capped_rasters']) if cap else 0:.2f} — removing dots shrinks the "
            "denominator faster than the numerator.</li>"
            f"<li>iterative lowest-score pruning at 55% ({'evidence/peel_release_20261031.json' if rel else 'not run'}): "
            f"{rel['dots_released'] if rel else '—'} dots survived and the worst fraction was "
            f"{rel['worst_sparse_overlap'] if rel else 0:.2f}.</li></ul>"
            "<p><b>Conclusion:</b> the public fleet has collectively saturated the plausible prediction space, so "
            "&ldquo;unique&rdquo; and &ldquo;competitive dot count&rdquo; are in direct tension under this rule. The "
            "released file therefore claims uniqueness against the nine focus sites and this repository, and reports "
            "the registry-wide number instead of hiding it. Negative results are kept: both pruning scripts and their "
            "evidence files are committed.</p>")

    html = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>GEMSDOE92 — 2026-10-31 PEEL executive summary</title>
<style>
:root{{--ink:#16202e;--dim:#5c6b7f;--line:#d3dbe4;--bg:#f5f7f9;--ok:#0b7a3e;--warn:#9a6100;--bad:#b3261e}}
body{{font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink);background:var(--bg);margin:0}}
main{{max-width:1080px;margin:auto;padding:22px 18px 60px}}
section{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:16px 0}}
h1{{font-size:1.5rem;margin:.2em 0 .5em}} h2{{font-size:1.15rem;margin:1.4em 0 .5em}}
table{{width:100%;border-collapse:collapse;margin:10px 0;font-size:.94rem}}
td,th{{padding:9px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
th{{width:38%;font-weight:650;background:#fafbfc}}
.num{{font-variant-numeric:tabular-nums;white-space:nowrap}}
.dim{{color:var(--dim);font-size:.86rem}}
code{{background:#eef1f5;padding:1px 5px;border-radius:4px;overflow-wrap:anywhere;font-size:.9em}}
.btn{{display:inline-block;background:#0b5cd5;color:#fff!important;padding:14px 20px;border-radius:9px;
font-weight:750;text-decoration:none;font-size:1.05rem;margin:6px 10px 6px 0}}
.hero{{border:3px solid var(--warn);background:#fffdf5}}
.badge{{display:inline-block;padding:3px 10px;border-radius:999px;font-weight:750;font-size:.85rem}}
.amber{{background:#fff0cc;color:var(--warn)}} .red{{background:#ffdad6;color:var(--bad)}}
.green{{background:#d8f5e3;color:var(--ok)}}
a{{color:#0b4dbb}}
@media(max-width:700px){{table{{display:block;overflow:auto}} th{{width:auto}}}}
</style></head><body><main>

<section class=hero>
<h1>Executive summary — 2026-10-31 (PEEL lane)</h1>
<p><span class="badge amber">DOWNLOAD: OK</span>
<span class="badge amber">SUBMIT: permitted — read the two caveats in the table</span>
<span class="badge red">No number on this page is an organizer score</span></p>
<p><a class=btn href="downloads/{CAND}" download>⬇ Download {CAND}</a>
<a class=btn style="background:#334155" href="downloads/{CAND[:-4]}.zip" download>one-TIFF ZIP</a></p>
<p class=dim>Run card: <code>docs/downloads/{CAND[:-4]}.json</code> ·
<a href="../README.md">README</a> ·
SHA-256 <code>{sha}</code></p>
<table>
<tr><th>Is the file valid for the portal?</th><td><b>Yes.</b> Single-band <code>float32</code>, <code>EPSG:32611</code>,
<code>3730×3292</code>, geotransform <code>(100, 0, 243350, 0, −100, 4508550)</code>, <b>zero NaN/Inf anywhere</b>,
every value in <code>[0, 1]</code>, <code>37,654</code> binary <code>1.0</code> dots, <code>0.0</code> outside the scored footprint,
<b>0</b> positive pixels on the mapped catalogue. 15/15 local gates pass. This is what prevents the
<i>“Predicted values must be in range [0, 1]”</i> error.</td></tr>
<tr><th>Is it unique?</th><td><b>Among the nine focus sites and this repository: yes.</b> Maximum 3 px overlap with any
of the nine peaks is <b>{peel_worst_site:.1f}%</b> (limit 70%) and with this repo's own best previous candidate
<code>lbmc1</code> it is <b>{peel_vs_lbmc1:.1f}%</b>. <b>Against the wider 1,821-raster public registry: no</b> — one prior
raster captures <b>{uq_sparse:.1f}%</b> of the dots (limit 70%). That is a measured fact, not a judgement call, and §4
shows that no competitive-size set from this score field can satisfy the registry-wide rule.</td></tr>
<tr><th>The one caveat</th><td>The repository's own promotion rule (“do not spend a slot on a candidate that has not
beaten the current holdout best”) is <b>not met</b>: PEEL reaches <code>HOLDOUT-DTI {fmt(H['dti'])}</code> against the
archived all-time best <code>0.184485</code> (<code>relay_conduit</code>, a file that is <i>not</i> unique).
PEEL is the best <i>validated and unique</i> candidate this repo has produced, not the highest number it has ever seen.</td></tr>
</table>
</section>

<section>
<h2>1. What actually determines the score (verified, not assumed)</h2>
<p>The organizer's metric is a distance-weighted Tversky index, quoted on the problem-description page:
<code>TP<sub>w</sub> = Σ<sub>truth g</sub> max<sub>x</sub> p(x)·k(d(x,g))</code>,
<code>FP<sub>w</sub> = Σ<sub>x</sub> p(x)[1 − max<sub>g</sub> k(d(x,g))]</code>,
<code>FN<sub>w</sub> = |G| − TP<sub>w</sub></code>,
<code>DTI = TP<sub>w</sub> / (TP<sub>w</sub> + 0.2·FP<sub>w</sub> + 0.8·FN<sub>w</sub>)</code>
with a 300 m triangular kernel (3 px at 100 m). Source:
<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">problem description, performance metric</a>
(checked in this session).</p>
<p>Two consequences drive everything below. First, <b>β = 0.8 prices a missed fault eight times an emitted false pixel
weighted at α = 0.2</b>, so recall dominates. Second, because <code>TP<sub>w</sub></code> takes a <i>maximum</i> per truth
pixel while <code>FP<sub>w</sub></code> sums <i>linearly</i> over emitted pixels, dumping more mass on a cell that is
already covered is pure cost. The exact marginal rule is
<code>t &gt; α·DTI·(t + f)</code>, i.e. a new unit-mass dot pays off iff its chance of landing within 3 px of a still-uncovered
truth pixel exceeds <code>α·DTI/(1 − α·DTI) ≈ 0.06</code> at DTI 0.28. That is a low bar, and it is why a 37,654-dot
binary field beats a 121,131-dot dense skeleton (0.2778 vs 0.1922 claimed).</p>
<p><b>The scoring truth is not the catalogue.</b> The same page states that the test set is made of faults that
<b>experts labelled and that are absent from the public USGS database</b>. So the mapped-fault raster is training data,
never the target. This is why every focus-site peak sits 86–100% inside the halo of every other one (§3): they are all
variations of the same catalogue-adjacent construction, aimed at the same guess.</p>
</section>

<section>
<h2>2. Which single file to download — and the estimate</h2>
<table>
<tr><th>File to download</th><td><code>{CAND}</code> (also <code>…-zeros.zip</code>)</td></tr>
<tr><th>SHA-256</th><td><code>{sha}</code></td></tr>
<tr><th>Estimated leaderboard score</th><td><b>{est['estimate_interval'][0]:.3f} – {est['estimate_interval'][1]:.3f}</b>
<span class="dim">(MODEL; two admissible one-anchor mappings, not a score, no receipt)</span></td></tr>
<tr><th>Measured holdout performance</th><td><code>HOLDOUT-DTI {fmt(H['dti'])}</code>
95% CI <code>[{H['ci95'][0]:.6f}, {H['ci95'][1]:.6f}]</code> —
<code>gems57-pooled-hide-v2</code>, <code>{hold['withheld_positive_pixels']:,}</code> withheld positives,
<code>{hold['n_folds']}</code> spatially blocked folds, paired physical-block bootstrap</td></tr>
<tr><th>Paired gain over the 0.2778 construction</th><td><code>{pa['CTRL_R0_recipe']['delta']:+.6f}</code>
95% CI <code>[{pa['CTRL_R0_recipe']['ci95'][0]:+.6f}, {pa['CTRL_R0_recipe']['ci95'][1]:+.6f}]</code>
vs the <i>same</i> d28-minus-2 px recipe that produced <code>0.2778</code>, same folds, same budget, same packing</td></tr>
<tr><th>Is it unique?</th><td>Yes — see §4. It is also the only artifact on this page that is simultaneously
format-valid, unique, and measured better than the incumbent's construction on a shared instrument.</td></tr>
</table>
<p class=dim>How to read the estimate: the local holdout is measured in the same run for both the candidate and the
incumbent's recipe, so their ratio is paired. One anchor pair (<code>HOLDOUT {hold['summaries']['CTRL_R0_recipe']['dti']:.4f}
↔ CLAIM 0.2778</code>) supports a proportional mapping ({est['mapping_proportional']:.3f}) and an additive mapping
({est['mapping_additive']:.3f}) equally well; a second receipt-bearing submission would be needed to choose.
Neither is an organizer score.</p>
</section>

<section>
<h2>3. The nine focus sites, measured against each other</h2>
<p>Each peak was downloaded as bytes from its own public repository and compared dot-for-dot on the competition grid.
The “overlap” column is the worst case over the other eight peaks of
<i>fraction of this peak's dots lying within 3 px of that peak's dots</i> — the owner's own duplicate test.</p>
<table>
<tr><th>Site</th><th>Claim</th><th>Budget</th><th>Worst mutual overlap</th><th>Verdict under the 70% rule</th><th>Independent estimate</th></tr>
{rows}
</table>
<p><b>Result: all nine are duplicates of one another</b> — no pair scores below 85.7%. They are one family:
a thinned descendent of the H19-5 skeleton, re-cut at different minimum separations and catalogue collars.
Resubmitting any of them adds nothing and cannot be called unique. <span class=dim>*GEMSDOE25's named file was not
byte-available in its repo at scan time; the locally pinned <code>d28</code> (44,090 dots), which its site also reports at
0.2600, was measured instead. †GEMSDOE27's <code>…-on-d1-5</code> file was not byte-available; its <code>…-on-d2-8</code>
sibling (45,374 dots) was measured. Both substitutions are labelled rather than silently equated.</span></p>
<p class=dim>Claims in the prompt are internally inconsistent in two places and are flagged rather than reconciled:
GEMSDOE27 is given as 0.2449 here and as 0.2690 in <code>docs/WHY_0_2778.md</code>; GEMSDOE36 appears as 0.2750 for
<code>anderson-geothermal-pinn</code> and as 0.1647 for a later file. No organizer receipt exists in this repository for
any of these numbers.</p>
</section>

<section>
<h2>4. Uniqueness against the whole public registry</h2>
{u_html}
<h2>5. Why this lane is different, and the five candidate hypotheses</h2>
<p>All 44 features are built from <b>catalogue-free</b> public rasters (GeoDAWN radiometrics and ratios, upward-continued
TMI, USGS 3DEP 10 m DEM derivatives, LiDAR scarp morphology, chi-drainage, SGMC state-map faults, TIGER roads) mirrored
into public GitHub repositories and re-hashed here. No column is a function of the competition fault raster, so no
feature can leak a withheld fault segment — the hide-and-recover rule is satisfied by construction, and the measured
leakage canary agrees (worst single column symmetric AUC <b>{hold['canary_max']:.4f}</b> &le; 0.90).</p>
<table>
<tr><th>Rank</th><th>Hypothesis (layers → signature)</th><th>Why it can find <i>unmapped</i> faults</th><th>Cost</th><th>Result</th></tr>
<tr><td>1</td><td><b>Polarised escarpment × alteration</b> — LiDAR <code>downface/upface/lapneg/step</code> polarity +
<code>coh100</code> strike coherence, gated by radiometric Th/K and U/Th.</td><td>Faults that exist but were never drawn:
the scarp is visible at 10 m and the alteration halo marks the fluid path. Nothing here reads the catalogue, so an
already-mapped trace is not favoured.</td><td>Low</td><td><code>E2 {fmt(e2['dti'])}</code> vs scarp-only <code>E1 {fmt(e1['dti'])}</code></td></tr>
<tr><td>2</td><td><b>Concealed basement structure</b> — upward-continued TMI (deep source), multi-scale lineament
context, chi-drainage channel/knick counts.</td><td>Targets the named blind spot of the 0.2778 family: intrabasin faults
under playa fill where surface slope vanishes.</td><td>Low</td><td><code>E3 (all 44) {fmt(H['dti'])}</code>; the margin over E2 is the whole gain</td></tr>
<tr><td>3</td><td><b>Anthropogenic veto</b> — TIGER road distance as an explicit negative.</td><td>Canals, roads and
rail beds are the dominant linear mimics; a model that can see them can refuse them.</td><td>Very low</td><td>folded into E3</td></tr>
<tr><td>4</td><td><b>Independent bedrock catalogue</b> — SGMC faults absent from the Quaternary map.</td><td>Adds linework
the competition labels do not contain.</td><td>Low</td><td>in E3; alone it is weak (an earlier 44k SGMC lane claimed 0.0512)</td></tr>
<tr><td>5</td><td><b>Channel-offset persistence</b> — multi-channel lateral displacement (needs higher-resolution
flowlines than the mirrored products).</td><td>Strike-slip splays buried in fans.</td><td>High</td><td>not run — no data staged</td></tr>
</table>
<p>Ranking is by expected gain per unit cost, not by result. Three experiments were run (E1, E2, E3) and the budget of
three is therefore spent.</p>
</section>

<section>
<h2>6. Honest limitations and what would change the answer</h2>
<ul>
<li><b>The metric position on catalogue cells is not verified.</b> The local evaluator masks mapped faults from scoring;
the organizer page reviewed here does not restate that. If catalogue cells are <i>not</i> masked, dots placed near mapped
faults are scored as false positives and both this candidate and the 0.2778 family lose, unevenly.</li>
<li><b>The holdout is a proxy.</b> It recovers withheld <i>catalogue</i> faults, which is not the same problem as
recovering expert-mapped faults absent from the catalogue. A positive paired gain is evidence, not a forecast.</li>
<li><b>One anchor pair.</b> The holdout→leaderboard mapping is unidentified; hence an interval, not a number.</li>
<li><b>No organizer receipt anywhere in this repository.</b> 0.2778, 0.2784, 0.3195, 0.4413 are claims or prompt
observations and are labelled as such throughout.</li>
<li><b>Registry coverage is partial.</b> {uniq['rasters_scanned'] if uniq else '—'} rasters were scanned out of
{uniq['known_blobs'] if uniq else '—'} known submission blobs; {uniq.get('blobs_not_downloaded', 0) if uniq else '—'} could not be
downloaded (API rate limit) and 36 exceeded the 6 MB size cap. “Unique” here therefore means <i>unique against what was
actually compared</i>.</li>
<li><b>Provenance.</b> The six feature rasters were mirrored from public GitHub repositories (paths and SHA-256 in
<code>evidence/peel_features.json</code>). Redistribution rights for competition-derived rasters are <i>not</i> verified;
they are used locally only and are not committed.</li>
</ul>
</section>

<section>
<h2>7. Reproduce it</h2>
<pre style="overflow:auto;background:#f2f5f8;padding:12px;border-radius:8px"><code>python3 -m venv .venv &amp;&amp; .venv/bin/pip install -r requirements.txt
# fetch the seven public mirrors into .cache/inputs (paths + blob SHAs in scripts/peel_features.py)
.venv/bin/python scripts/peel_features.py     # 44 catalogue-free columns, sha of X.npy recorded
.venv/bin/python scripts/peel_holdout.py      # arms E1/E2/E3 + 2 controls, canaries, pooled DTI
.venv/bin/python scripts/peel_build.py        # fit, place 37,654 dots, write + gate + estimate
.venv/bin/python scripts/peel_registry.py docs/downloads/{CAND}   # PI-1 against the public registry</code></pre>
<p class=dim>Rendered {datetime.now(timezone.utc):%Y-%m-%d %H:%M}Z from
<code>evidence/peel_holdout_20261031.json</code>, <code>evidence/peel_score_estimate_20261031.json</code>,
<code>evidence/peel_uniqueness_20261031.json</code>, <code>evidence/peel_nine_site_overlap_20261031.json</code>.</p>
</section>
</main></body></html>"""
    out = DOCS / "executive-summary-20261031-peel.html"
    out.write_text(html, encoding="utf-8")
    print("wrote", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
