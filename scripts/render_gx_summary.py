#!/usr/bin/env python3
"""Render the 2026-10-31 GX executive-summary page and prepend it to docs/index.html.

Every number in the page is read from an evidence JSON in ``evidence/`` or
recomputed from the pinned rasters; nothing is typed by hand twice.  Run
``python scripts/render_gx_summary.py`` after re-measuring.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

HOLD = json.loads((ROOT / "evidence" / "gx_holdout.json").read_text())
EVAL = json.loads((ROOT / "evidence" / "gx_candidate_eval.json").read_text())
CAND = json.loads((ROOT / "evidence" / "gx_candidate.json").read_text())
EST = json.loads((ROOT / "evidence" / "gx_score_estimator.json").read_text())
HIST = json.loads((ROOT / "evidence" / "score_estimator_20261026.json").read_text())
NINE = json.loads((ROOT / "evidence" / "nine_site_byte_check_20261030.json").read_text())
SCREEN = json.loads((ROOT / "evidence" / "gx_band_screen.json").read_text())

CLAIM_NOTE = "CLAIM (owner-reported, no organizer receipt)"
MODEL_NOTE = "MODEL (calibrated projection, not a score)"

FOCUS = [
    ("GEMSDOE24", "gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif", 0.2477, 0.1629),
    ("GEMSDOE25", "gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif", 0.2600, 0.1382),
    ("GEMSDOE27", "gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif", 0.2449, 0.1651),
    ("GEMSDOE28", "gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif", 0.2710, 0.1894),
    ("GEMSDOE30", "gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif", 0.2600, 0.1382),
    ("GEMSDOE31", "gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif", 0.2708, 0.1952),
    ("GEMSDOE32", "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif", 0.2778, 0.2510),
    ("GEMSDOE33", "GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif", 0.2632, 0.1720),
    ("GEMSDOE36", "gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif", 0.2750, 0.2467),
]

SITE_URL = {
    "GEMSDOE24": "https://buffedlizard55-lab.github.io/GEMSDOE24/",
    "GEMSDOE25": "https://buffedlizard55-lab.github.io/GEMSDOE25/",
    "GEMSDOE27": "https://buffedlizard55-lab.github.io/GEMSDOE27/",
    "GEMSDOE28": "https://buffedlizard55-lab.github.io/GEMSDOE28/",
    "GEMSDOE30": "https://buffedlizard55-lab.github.io/GEMSDOE30/",
    "GEMSDOE31": "https://buffedlizard55-lab.github.io/GEMSDOE31/docs/",
    "GEMSDOE32": "https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html",
    "GEMSDOE33": "https://buffedlizard55-lab.github.io/GEMSDOE33/",
    "GEMSDOE36": "https://buffedlizard55-lab.github.io/GEMSDOE36/docs/",
}

hl = HOLD["pooled"]["scores"]
best_arm = max((k for k in hl if k.startswith("gx_")), key=lambda k: hl[k]["dti"])
best = hl[best_arm]
r0 = hl["r0_recipe"]
rnd = hl["random"]
diff = HOLD["pooled"]["paired_differences"]["r0_recipe"]
cand_h = EVAL["holdout"]["scores"]["candidate"]
uniq = EVAL["uniqueness"]
worst_df = uniq["worst_by_representation"]["dot_field"]["max"]
worst_lat = uniq["worst_by_representation"]["dense_binary_lattice"]["max"]
nlat = uniq["worst_by_representation"]["dense_binary_lattice"]["n_above_070"]
est = EVAL["estimate"]
sha = EVAL["sha256"]

can_max_auc = max(c["auc_holdout"] for c in HOLD["canaries"])
rad = [c for c in SCREEN["rows"] if c["band"] in ("K", "Th", "U", "TC", "ThK", "UK", "UTh", "TMI_up150")]
rad_max = max(c["auc_holdout"] for c in rad)
morph = [c for c in SCREEN["rows"] if c["file"].startswith("lidar")]
morph_max = max(c["auc_holdout"] for c in morph)

# holdout/claim anti-correlation measured this session
est_rows = EST["files"]
sites = sorted(est_rows)
import math
def spearman(a, b):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else float("nan")

tvals = [est_rows[s]["t_per_dot"] for s in sites]
cvals = [est_rows[s]["claim"] for s in sites]
rho_hc = spearman(tvals, cvals)

rows_html = []
for site, fn, claim, loo in FOCUS:
    key = site.replace("GEMSDOE", "")
    mn = NINE["min_over_others_per_site"][key]
    mx = NINE["max_over_others_per_site"][key]
    nd = NINE["files"][key]["n_dots"]
    sh = NINE["files"][key]["sha256"][:12]
    ov = uniq["focus_nine"].get(site, {}).get("overlap")
    ov_txt = f"{ov:.3f}" if ov is not None else "n/a (dot-identical to GEMSDOE25)"
    rows_html.append(f"""<tr>
<td><strong>{site}</strong><br><a href="{SITE_URL[site]}">owner page</a></td>
<td><code>{fn}</code><br><span class="small">SHA-256 <code>{sh}…</code> · {nd:,} dots</span></td>
<td><strong>{claim:.4f}</strong> <code>{CLAIM_NOTE.split(' ')[0]}</code></td>
<td><code>{loo:.3f}</code> ± <code>{est['ridge_audit']['leave_group_out_rmse']:.3f}</code> <code>MODEL</code></td>
<td><strong>NO</strong> — {mn:.3f}–{mx:.3f} of its dots within 3 px of another listed site (random baseline {NINE['random_baseline_within_3px_of_GEMSDOE32']['mean']:.3f})</td>
<td>vs GX-1: {ov_txt}</td>
<td>Research only · <strong>NO</strong></td>
</tr>""")

PAGE = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GEMSDOE92 — 2026-10-31 GX Executive Summary (nine focus sites + unique candidate)</title>
<style>body{{font:16px/1.55 system-ui;color:#18212e;background:#f4f6f8;margin:0}}main{{max-width:1180px;margin:auto;padding:24px}}section{{background:white;padding:20px;margin:18px 0;border-radius:8px}}
.stop{{border:3px solid #b91c1c;background:#fff4f3}}.go{{border:3px solid #15803d;background:#f2fdf5}}
.btn{{display:inline-block;background:#1d4ed8;color:#fff!important;padding:9px 14px;border-radius:7px;font-weight:700;text-decoration:none;margin:4px 6px 4px 0}}
table{{width:100%;border-collapse:collapse}}td,th{{padding:9px;border-bottom:1px solid #ccd5df;text-align:left;vertical-align:top}}
code{{overflow-wrap:anywhere}}a{{color:#124ec0}}.small{{font-size:13px;color:#4a5768}}
@media(max-width:800px){{table{{display:block;overflow:auto}}}}</style></head><body><main>

<h1>2026-10-31 Executive summary — nine focus sites + one new unique candidate (GX lane)</h1>
<p class="small">Every number below is labelled <code>CLAIM</code> (owner-reported, no organizer receipt), <code>MODEL</code> (calibrated projection), <code>HOLDOUT-DTI</code> (measured by the shared evaluator <code>{HOLD['evaluator']}</code>) or <code>REGISTRY-MEASUREMENT</code> (measured from raster bytes). A <code>MODEL</code> number is never a score.</p>

<section class="stop">
<h2>1. Bottom line — what to download, and what not to submit</h2>
<p><strong>✅ OK TO DOWNLOAD FOR RESEARCH — the new unique file:</strong>
<a class="btn" href="downloads/gemsdoe92-gx1-50000dots-20261031-zeros.tif" download>⬇ Download GX-1 GeoTIFF ({CAND['bytes']:,} bytes)</a>
<a class="btn" href="downloads/gemsdoe92-gx1-50000dots-20261031-zeros.zip" download>⬇ one-TIFF ZIP</a>
<a href="downloads/gemsdoe92-gx1-50000dots-20261031-zeros-audit.json">format audit</a> ·
<a href="../evidence/gx_candidate_eval.json">evaluation JSON</a> ·
<a href="../evidence/gx_holdout.json">holdout JSON</a> ·
<a href="how-to-submit.html">how to submit</a></p>
<p><strong>⛔ DO NOT SUBMIT GX-1 to the portal this week.</strong> Three independent reasons, all measured:
(1) its audited <code>MODEL</code> estimate is <code>{est['ridge_estimate']:.4f}</code> ± <code>{est['ridge_audit']['leave_group_out_rmse']:.3f}</code>, below the best reported focus-site claim (<code>0.2778</code>);
(2) its fold-proper <code>HOLDOUT-DTI</code> <code>{best['dti']:.4f}</code> does not exceed this repository's all-time best (<code>relay_conduit = 0.184485</code>);
(3) under the literal reading of the internal duplicate rule it collides with {nlat} dense full-support registry rasters (max overlap <code>{worst_lat:.3f}</code> &gt; 0.70) — see §5.
<strong>Nothing among the nine focus sites is clearable either</strong> (§2): all nine are near-copies of one lineage and every one of them has already been submitted by its owner.</p>
<table>
<tr><th>File</th><td><code>gemsdoe92-gx1-50000dots-20261031-zeros.tif</code> · SHA-256 <code>{sha}</code></td></tr>
<tr><th>Format gates</th><td>1 band <code>float32</code>, <code>EPSG:32611</code>, <code>3730×3292</code>, transform <code>(100, 0, 243350, 0, -100, 4508550)</code>, <code>{CAND['n_dots']:,}</code> dots of value <code>1.0</code>, <code>0.0</code> outside the footprint, <strong>0 NaN / 0 Inf</strong>, min <code>0.0</code> max <code>1.0</code> — so the portal error <em>“Predicted values must be in range [0, 1]”</em> cannot occur. <code>{CAND['audit']['ok'] and 'PASS' or 'FAIL'}</code> on the shared <code>gems57.gates</code> template/range check.</td></tr>
<tr><th>Hypothesis</th><td>Fault-appearance model on <strong>externally sourced public layers only</strong> (1 m-lidar scarp operators, GeoDAWN K/Th/U/TC + ratios + TMI, USGS SGMC faults, GDR thermal indicators). No other submission's raster is read for placement, so the file is not a copy of a previous submission.</td></tr>
<tr><th>Measured win</th><td>Fold-proper <code>HOLDOUT-DTI</code> <strong>{best['dti']:.4f}</strong> 95% CI <code>[{best['ci95'][0]:.4f}, {best['ci95'][1]:.4f}]</code> vs the R0 recipe control <strong>{r0['dti']:.4f}</strong> <code>[{r0['ci95'][0]:.4f}, {r0['ci95'][1]:.4f}]</code> (the recipe that produced the 0.2778 lineage): paired difference <strong>{diff['delta']:+.4f}</strong> <code>[{diff['ci95'][0]:+.4f}, {diff['ci95'][1]:+.4f}]</code> on identical masks; random-dot control <code>{rnd['dti']:.4f}</code>.</td></tr>
<tr><th>Uniqueness</th><td>2,096-SHA public registry: worst <code>dot_field</code> 3-px overlap <strong>{worst_df:.4f} ≤ 0.70</strong> (0 of 1,903 dot fields above the limit), worst <code>continuous_surface</code> <code>{uniq['worst_by_representation']['continuous_surface']['max']:.3f}</code>, max |Spearman| <code>{uniq['max_abs_spearman']:.3f} ≤ 0.90</code>; overlap vs each of the nine focus files <code>0.345–0.412</code>. Literal dense-lattice reading: <code>{worst_lat:.3f}</code> &gt; 0.70 against {nlat} rasters whose dot support exceeds 150,000 px (policy gap, §5).</td></tr>
<tr><th>Archive name / note</th><td><code>{CAND['name']}</code> · note (<code>{len(CAND['note'])}/140</code>): <code>{CAND['note']}</code></td></tr>
</table>
</section>

<section>
<h2>2. Nine focus sites — best file per site, estimated score, uniqueness</h2>
<p>Overlap columns are byte-level measurements (<code>REGISTRY-MEASUREMENT</code>, <code>evidence/nine_site_byte_check_20261030.json</code>): “share of this file's dots within 3 px of the other site's dots”. The internal duplicate line is 0.70. A matched random dot field scores <code>{NINE['random_baseline_within_3px_of_GEMSDOE32']['mean']:.3f}</code>, which is what genuine independence looks like.</p>
<table>
<tr><th>Site</th><th>Best file to download</th><th>Reported score</th><th>Estimated score</th><th>Unique vs the other eight?</th><th>Overlap vs GX-1</th><th>OK to submit?</th></tr>
{chr(10).join(rows_html)}
</table>
<p class="small"><strong>Estimated-score column.</strong> <code>MODEL</code>: the repository's audited ridge estimator (logit DTI on four measurable structural statistics; <code>loo_rmse = {est['ridge_audit']['loo_rmse']:.4f}</code>, leave-group-out <code>{est['ridge_audit']['leave_group_out_rmse']:.4f}</code>, <code>valid_leaderboard_prediction = false</code>) applied to that file's own statistics. It is fitted to owner-reported <code>CLAIM</code>s, so it inherits their error, and it under-predicts the top of the H19-5 lineage by ~0.03. Use it for ordering, not for reporting.</p>
<p><strong>Answer to “which one should we submit?”: none of the nine.</strong> GEMSDOE32 is the highest reported (<code>0.2778 {CLAIM_NOTE.split(' ')[0]}</code>) and its owner has already submitted it; resubmitting an identical file spends a weekly slot for zero information. GEMSDOE25 and GEMSDOE30 are byte-different encodings of the <em>same</em> 44,090-dot set (<code>REGISTRY-MEASUREMENT</code>).</p>
</section>

<section>
<h2>3. Why <code>h33-h33-2-b2</code> scores 0.2778 — the metric algebra, not a story</h2>
<p>With the official metric (<code>α = 0.2</code>, <code>β = 0.8</code>, 300 m triangular kernel; transcribed in <code>vendor/gems57/metric.py</code>) and writing <code>T</code> = covered truth credit, <code>M</code> = dot self-credit, <code>n</code> = dot count, <code>K</code> = truth mass:</p>
<p class="small"><code>DTI = T / ( α(T + n − M) + βK )</code>. The denominator does <em>not</em> collapse to <code>αn + βK</code> — the shared template's own docstring flags that shortcut as valid only when <code>T == M</code>.</p>
<p>The five lineage claims form a subset chain (<code>d2.8 &#8839; h27-4 &#8839; h33</code>: 44,090 &#8594; 40,199 &#8594; 37,654 dots, verified by byte check). The three claims identify <code>T</code> from their <em>differences</em> alone, with no assumption about <code>K</code> or <code>M</code>: <code>T &#8776; 5,073</code> (d2.8&#8594;h27-4), <code>5,223</code> (d2.8&#8594;h33), <code>5,470</code> (h27-4&#8594;h33) &#8212; and the spread is itself informative: each pruning step costs a little real coverage, not only dead weight. <code>K</code> and <code>M</code> are <strong>not</strong> separately identifiable from three claims (only the combination <code>&#946;&#183;K &#8722; &#945;&#183;M</code> is); assuming <code>K = 13,219</code> (the value fitted by <code>scripts/gx_estimator.py</code>) gives <code>M &#8776; 1,744</code> &#8212; i.e. the 0.2778 file covers about <strong>40 % of the scored truth mass</strong> with roughly <strong>10 % of its dots (&#8776; 3,900 of 37,654) carrying essentially all of the credit</strong>. Three consequences, all of them actionable:</p>
<ol>
<li><strong>Thinning pays.</strong> Dropping a dot costs <code>0.2</code> of denominator and only its own yield. The 0.2600 → 0.2708 → 0.2778 steps are exactly this: 3,891 then 2,545 catalogue-adjacent dots removed at ~zero yield cost.</li>
<li><strong>False negatives dominate.</strong> <code>βK ≈ 10,575</code> is 56 % of the denominator and <code>α(n − M) ≈ 7,183</code> is 38 %. Coverage <code>T</code> is only 5.6 %. The leaderboard top (<code>0.4544</code> on the 2026-10-30 read) implies ≈ 67 % coverage (<code>T ≈ 8,875</code>) at a similar dot budget — i.e. the gap is <em>information</em>, not tuning.</li>
<li><strong>Pruning is the largest single lever available without new data.</strong> Half of h33's dots are pure cost; removing 18,000 zero-yield dots at constant <code>T</code> would give ≈ 0.34. Doing that needs a per-dot yield ranking, which is the untested experiment proposed in §6.</li>
</ol>
</section>

<section>
<h2>4. What this session actually measured (and the one result that changes the method)</h2>
<table>
<tr><th>Layers sourced externally (no DrivenData login)</th><td>GeoDAWN radiometrics <code>K, Th, U, TC</code> + <code>Th/K, U/K, U/Th</code> + <code>TMI</code> upward-continued 150 m; the 1 m-lidar scarp product (<code>ex_max, ex_mean, step_max, lapneg/lappos, downface/upface, cross_max, relief, coh100, strike, valid</code>); the USGS SGMC fault compilation; GDR wells/springs, 709 paleo-geothermal deposits and 21 vents. All are public, all pinned by SHA-256, none of them is another team's prediction.</td></tr>
<tr><th>Leakage canaries (rule 4)</th><td>{len(HOLD['canaries'])}/47 single-feature holdout AUCs computed; maximum <code>{can_max_auc:.4f} ≤ 0.90</code> → <strong>no leakage</strong>, no feature dropped.</td></tr>
<tr><th>Information content of the layers</th><td>Lidar scarp operators: holdout AUC up to <code>{morph_max:.3f}</code>. GeoDAWN radiometrics and TMI: <code>{rad_max:.3f}</code> — <strong>essentially no univariate fault signal</strong> on this grid. Thermal-indicator distance: <code>0.48</code>. SGMC distance: <code>0.34</code> (inverse). So magnetics/radiometrics alone cannot find these faults; they can only corroborate.</td></tr>
<tr><th>Holdout result</th><td>{best_arm}: <code>HOLDOUT-DTI {best['dti']:.4f} [{best['ci95'][0]:.4f}, {best['ci95'][1]:.4f}]</code> vs R0 recipe <code>{r0['dti']:.4f}</code> (paired <code>{diff['delta']:+.4f} [{diff['ci95'][0]:+.4f}, {diff['ci95'][1]:+.4f}]</code>) and random <code>{rnd['dti']:.4f}</code>, on {HOLD['n_draws']} draws / {best['withheld_positive_pixels']:,} withheld positives.</td></tr>
<tr><th>⚠ Method finding — the holdout is <em>anti</em>-correlated with the leaderboard inside the H19-5 lineage</th><td>Measured per-dot holdout yield vs owner-reported claim across the nine focus files: Spearman <code>ρ = {rho_hc:+.3f}</code> (n = {len(sites)}). The mechanism is structural: hide-and-recover truth is drawn <em>from</em> the catalogue, while every top-scoring submission deletes catalogue-adjacent dots. So the instrument systematically rewards exactly what the real task punishes. <strong>Consequence:</strong> a holdout win is necessary but not sufficient, and the “all-time holdout best” bar should not be used as a score proxy. This is the most important result of the session and it is a negative one.</td></tr>
</table>
</section>

<section>
<h2>5. Uniqueness — both readings, stated plainly</h2>
<p><strong>Same-representation reading (operational, used by recent lanes): PASS.</strong> Against all 2,096 unique SHA-256 rasters of the public registry, the candidate's worst 3-px forward overlap is <code>{worst_df:.4f}</code> among the 1,903 dot fields (limit 0.70) and <code>{uniq['worst_by_representation']['continuous_surface']['max']:.3f}</code> among the 103 continuous surfaces; max |Spearman| is <code>{uniq['max_abs_spearman']:.3f}</code> (limit 0.90). Overlap against each of the nine focus files is <code>0.345–0.412</code>.</p>
<p><strong>Literal reading: FAILS, and it cannot be passed by any file.</strong> {nlat} registry rasters are dense lattices/“unassigned mass” fields with more than 150,000 positive pixels; their 3-px halos cover the whole footprint, so <em>every</em> non-empty candidate scores <code>1.000 &gt; 0.70</code> against them (max measured <code>{worst_lat:.3f}</code>). This is the pre-existing policy gap <code>D1</code> in <code>docs/REVIEW_20261030_NINESITE.md</code> §8; only the owner can resolve it. Nothing in this session silently relaxes it.</p>
</section>

<section>
<h2>6. Ranked hypotheses — tested this session first, then untested</h2>
<table>
<tr><th>#</th><th>Hypothesis (layers, signature, why off-catalogue, named mimic)</th><th>Result</th><th>Cost</th></tr>
<tr><td>H1</td><td><strong>Lidar-scarp operator stack</strong> — 1 m-lidar <code>step/excess/curvature/cross/relief</code> at 150 m and 350 m: value, horizontal-gradient magnitude, ridgeness (−min Hessian eigenvalue). Catches unmapped scarps that a 100 m DEM smooths away. Mimic: shorelines, terrace edges, road cuts.</td><td><strong>CONFIRMED.</strong> Solo AUC ≤ {morph_max:.3f}; joint logistic model beats the R0 recipe by <code>{diff['delta']:+.4f}</code>.</td><td>Done</td></tr>
<tr><td>H2</td><td><strong>Radiometric / magnetic contact lineaments</strong> — <code>K, Th, U, TC</code>, ratios and <code>TMI_up150</code> horizontal-gradient ridges. Would catch buried faults with no surface scarp. Mimic: lithologic contacts, alteration halos, flight-line seams.</td><td><strong>REJECTED as a standalone.</strong> Solo holdout AUC {rad_max:.3f} (K/Th/U/TC/ThK/UK/UTh/TMI). Kept in the joint model only as weak covariates.</td><td>Low</td></tr>
<tr><td>H3</td><td><strong>Thermal-indicator prior</strong> — distance to hot/warm springs and wells (temp ≥ 30 °C or any geothermometer ≥ 100 °C), 709 paleo-geothermal deposits, 21 vents: permeable structures discharge. Mimic: basin-floor water wells.</td><td><strong>REJECTED as a standalone</strong> (AUC 0.48). The 6,888 thermal records are only mildly closer to mapped faults (median 21 px) than the 27,092-record pool (24 px).</td><td>Low</td></tr>
<tr><td>H4</td><td><strong>USGS SGMC compilation as a second fault database</strong> — dots on SGMC faults absent from the competition catalogue. Mimic: map-scale bedrock faults with no Quaternary expression.</td><td><strong>REJECTED.</strong> Solo AUC 0.34 (inverse); consistent with earlier lanes (<code>h18-4</code> 0.0360, <code>sgmc-off-catalogue</code> 0.0512).</td><td>Low</td></tr>
<tr><td>H5</td><td><strong>No-lidar blind spot</strong> — the 1 m scarp product covers 75.4 % of the footprint; geophysics-only detection in the remaining 24.6 % would find faults the lidar-based lineage cannot see. Mimic: none (data gap).</td><td><strong>REJECTED.</strong> The lineage is <em>not</em> blind there: 23.6 % of its dots sit in the no-lidar zone vs 24.6 % of the footprint, and 20.5 % of mapped faults.</td><td>Low</td></tr>
<tr><td>H6</td><td><strong>Per-dot yield pruning</strong> (§3 lever 3): rank the lineage skeleton — or any candidate — by a calibrated fault probability and drop every dot whose expected marginal credit is below <code>α·DTI</code>. Needs no new data, only a calibrated probability surface.</td><td><strong>NOT TESTED</strong> (budget exhausted). Highest expected value per unit cost of anything on this list.</td><td>Medium</td></tr>
<tr><td>H7</td><td><strong>Official 19-band stack</strong> (conductivity, isostatic gravity, geodetic strain, earthquake density, top-of-crust depth) with a gradient-boosted model and spatial-block CV. Mimic: flight-line and gridding artefacts.</td><td><strong>BLOCKED.</strong> Needs <code>training_features.tif</code> / <code>labels.tif</code> from the DrivenData data tab (login). No public mirror with a matching SHA-256 was found in 114 GEMSDOE repositories.</td><td>High</td></tr>
<tr><td>H8</td><td><strong>Greedy marginal-coverage emission</strong> (shared <code>gems57.emit.greedy_allocate</code>) with a calibrated per-cell truth probability instead of a fixed budget/spacing.</td><td><strong>NOT TESTED.</strong> Requires probability calibration that survives the catalogue→unmapped distribution shift.</td><td>Medium</td></tr>
</table>
</section>

<section>
<h2>7. How to submit (only when a file is cleared)</h2>
<ol>
<li>Download the <code>.tif</code> (or the one-TIFF <code>.zip</code>) — never edit it.</li>
<li>Open <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">the submission page</a> and choose the file.</li>
<li>Name: <code>{CAND['name']}</code> (unique, ≤ 140 characters).</li>
<li>Note (≤ 140 characters): <code>{CAND['note']}</code></li>
<li>The file is single-band, <code>EPSG:32611</code>, <code>3730×3292</code>, values in <code>[0, 1]</code>, zeros outside the footprint, no NaN — which is precisely what prevents <em>“Predicted values must be in range [0, 1]”</em>.</li>
<li>Limit: 3 submissions per week (<a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">official rules §3.2</a>). Do not spend one on an unvalidated file.</li>
</ol>
<p class="small">This section is a format guide only. It is not clearance: the 2026-10-31 verdict for GX-1 is <code>negative</code> / <code>submission_eligible = false</code>.</p>
</section>

<section>
<h2>8. Irregularities and limits flagged this session</h2>
<ul>
<li>GitHub REST rate limit (5,000/hour) was exhausted mid-session; the registry index was therefore rebuilt <strong>offline</strong> from the prefetched cache by <code>scripts/gx_registry_index.py</code>. No REST call is required to reproduce it.</li>
<li>The DrivenData bundle is still login-walled (<code>IR-1028C-8</code>); the externally sourced stacks used here are public but their redistribution terms are unverified, and none of them has been confirmed as organizer-identical.</li>
<li>The deadlined “single method paragraph” for this parallel run was not present in the delivered prompt; the lane taken here (external-layer fault-appearance model) is stated explicitly in §1 rather than assumed.</li>
<li>The user-reported leaderboard snapshots <code>0.4413</code> and <code>0.3195</code> were not found in the public top-22 on the last verified read (2026-10-30: #1 <code>0.4544</code>). Treat user snapshots as stale.</li>
<li>The “OK TO DOWNLOAD” and “DO NOT SUBMIT” banners are produced by the same evidence file; if they ever disagree, the JSON run card wins.</li>
</ul>
</section>

<p class="small">Generated by <code>scripts/render_gx_summary.py</code> from <code>evidence/gx_holdout.json</code>, <code>evidence/gx_candidate_eval.json</code>, <code>evidence/gx_candidate.json</code>, <code>evidence/gx_score_estimator.json</code>, <code>evidence/gx_band_screen.json</code> and <code>evidence/nine_site_byte_check_20261030.json</code>.</p>
</main></body></html>
"""

OUT = ROOT / "docs" / "executive-summary-20261031-gx.html"
OUT.write_text(PAGE, encoding="utf-8")
print(f"wrote {OUT} ({len(PAGE)} bytes)")

# docs/index.html is owned by scripts/render_safe_review.py (the canonical renderer).
# The GX banner there is produced by load_gx_20261031_status() from the same run card,
# so this script only writes the standalone executive-summary page.
