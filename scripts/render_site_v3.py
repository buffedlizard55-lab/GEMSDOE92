#!/usr/bin/env python3
"""Render the GitHub Pages site (v3, 2026-10-27) from machine evidence only.

Inputs : the current run card (docs/downloads/current_submission.json -> run card),
         evidence/focus9_sources_20261027.json, evidence/focus9_uniqueness_20261027.json,
         evidence/lbm_v1_model.json, evidence/claims_matched_20261027.json,
         evidence/holdout_validity_20261027.json.
Outputs: docs/index.html, docs/how-to-submit.html, docs/nine-sites.html, index.html,
         docs/downloads/current_submission.json, docs/downloads/readiness.json.
``render()`` returns {path: text}; ``main`` writes them.  check_site.py re-renders
and fails if any published page is stale.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DL = DOCS / "downloads"
EVID = ROOT / "evidence"
PRIMARY_CARD = EVID / "gemsdoe92-lbmc1-35801dots-20261027-89a660f6_run_card.json"

OFFICIAL = [
    ("Competition home & problem description (metric, format)", "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"),
    ("Submission portal (login required)", "https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/"),
    ("Leaderboard (view manually; not mirrored or scraped here)", "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"),
    ("DrivenData Terms of Use (why the leaderboard is not mirrored)", "https://www.drivendata.org/termsofuse/"),
    ("Official rules PDF (NLR/DOE, Sept 2026)", "https://docs.nlr.gov/docs/fy26osti/96647.pdf"),
    ("Forum: known faults are masked pixel-exactly", "https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4"),
    ("Forum: leaderboard pools all public pixels", "https://community.drivendata.org/t/leaderboard-aggregation-pooled-over-public-test-pixels-or-mean-of-per-chunk-scores/11550"),
    ("Forum: 'new fault' = any pixel not in USGS/INGENIOUS", "https://community.drivendata.org/t/where-do-you-draw-the-line/11536"),
    ("Forum: weekly limit shown on the website prevails", "https://community.drivendata.org/t/submission-amount-question/11553"),
    ("Forum: Phase 2 labels can be added/removed/changed", "https://community.drivendata.org/t/questions-about-the-final-round-rules/11556"),
    ("Reference solution (DrivenData)", "https://github.com/drivendataorg/gems-prize-reference-solution"),
    ("USGS GeoDAWN magnetic & radiometric data", "https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and"),
    ("USGS 3DEP 1 m DEM collection (free, no use restrictions)", "https://data.usgs.gov/datacatalog/data/USGS:77ae0551-c61e-4979-aedd-d797abdcde0e"),
    ("INGENIOUS Great Basin compilation (GDR 1391)", "https://gdr.openei.org/submissions/1391"),
]

CSS = """body{font:16px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f7f9;color:#1f2933}
main{max-width:980px;margin:0 auto;padding:1rem 1.2rem 3rem}h1{font-size:1.6rem;margin:.6rem 0}h2{margin-top:2rem;border-bottom:2px solid #e3e7ec;padding-bottom:.2rem}
.box{background:#fff;border-radius:12px;padding:1.1rem 1.3rem;box-shadow:0 1px 3px rgba(0,0,0,.08);margin:1rem 0}
.ok{border:3px solid #15803d}.no{border:3px solid #b91c1c}.badge{display:inline-block;padding:.25rem .7rem;border-radius:999px;font-weight:700;color:#fff}
.bok{background:#15803d}.bno{background:#b91c1c}.btn{display:inline-block;background:#1d4ed8;color:#fff!important;padding:.75rem 1.1rem;border-radius:8px;font-weight:700;text-decoration:none;margin:.3rem .4rem .3rem 0}
.btn2{background:#334155}code,.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.9em;overflow-wrap:anywhere}
table{border-collapse:collapse;width:100%;font-size:.93rem}th,td{border-bottom:1px solid #e3e7ec;padding:.4rem .45rem;text-align:left;vertical-align:top}th{background:#eef2f7}
.copy{background:#0f172a;color:#e2e8f0;padding:.55rem .7rem;border-radius:6px;font-family:ui-monospace,Menlo,monospace;overflow-wrap:anywhere}
.small{font-size:.86rem;color:#52606d}.warn{background:#fff7ed;border-left:4px solid #f59e0b;padding:.6rem .8rem;border-radius:6px}
nav a{margin-right:1rem}"""


def esc(s) -> str:
    return html.escape(str(s))


def load():
    card = json.loads(PRIMARY_CARD.read_text(encoding="utf-8"))
    f9 = json.loads((EVID / "focus9_sources_20261027.json").read_text(encoding="utf-8"))
    f9u = json.loads((EVID / "focus9_uniqueness_20261027.json").read_text(encoding="utf-8"))
    model = json.loads((EVID / "lbm_v1_model.json").read_text(encoding="utf-8"))
    val = json.loads((EVID / "holdout_validity_20261027.json").read_text(encoding="utf-8"))
    return card, f9, f9u, model, val


def status_cards(card: dict) -> tuple[dict, dict]:
    ok = card["verdict"] == "promote" and card["submission_eligible"] is True
    rel = card["raster"]["file"].removeprefix("docs/")
    current = dict(file=card["raster"]["file"], sha256=card["raster_sha256"], bytes=card["raster"]["bytes"],
                   n_dots=card["raster"]["n_dots"], submission_name=card["submission_name"], note=card["note"],
                   verdict=card["verdict"], ok_to_download=True, ok_to_submit=ok,
                   run_card=f"downloads/{Path(PRIMARY_CARD).name}",
                   model_estimate_point=card["model_estimate"]["point"]["lbm_v1"],
                   model_estimate_interval90=[card["model_estimate"]["bootstrap"]["q05"], card["model_estimate"]["bootstrap"]["q95"]],
                   evidence_class_of_estimate="MODEL (not an organizer score)")
    readiness = dict(file=rel, raster_sha256=card["raster_sha256"], submission_name=card["submission_name"],
                     note=card["note"], verdict=card["verdict"], submission_eligible=ok,
                     download_status="OK TO DOWNLOAD",
                     submission_status=("OK TO SUBMIT — all automated gates passed (format, PI-1 uniqueness, MODEL > 0.2778 at the 5% bound, no leakage)"
                                        if ok else "DO NOT SUBMIT — at least one automated gate failed; see run card"),
                     gates=card["gates_passed"])
    return current, readiness


def page(title: str, body: str, root_rel: str = "") -> str:
    return (f"<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n<title>{esc(title)}</title>\n"
            f"<style>{CSS}</style>\n</head>\n<body>\n<main>\n{body}\n</main>\n</body>\n</html>\n")


def submission_box(card: dict, href_prefix: str = "") -> str:
    ok = card["verdict"] == "promote" and card["submission_eligible"] is True
    r = card["raster"]
    rel = r["file"].removeprefix("docs/")
    me = card["model_estimate"]; b = me["bootstrap"]; u = card["uniqueness"]
    badge = ('<span class="badge bok">✅ OK TO SUBMIT</span>' if ok else '<span class="badge bno">⛔ DO NOT SUBMIT</span>')
    return f"""<section class="box {'ok' if ok else 'no'}" id="submit-now">
<h1>{badge} {esc(Path(rel).name)}</h1>
<p><a class="btn" data-primary="true" href="{href_prefix}{esc(rel)}" download>⬇ Download the GeoTIFF ({r['bytes']:,} bytes)</a>
<a class="btn btn2" href="{href_prefix}{esc(rel.replace('-zeros.tif', '-zeros.zip'))}" download>⬇ One-TIFF ZIP</a>
<a class="btn btn2" href="{href_prefix}how-to-submit.html">How to submit (3 steps)</a></p>
<table>
<tr><th>Portal “Submission name”</th><td><div class="copy">{esc(card['submission_name'])}</div></td></tr>
<tr><th>Portal “Note” ({card['note_chars']} ≤ 140 chars)</th><td><div class="copy">{esc(card['note'])}</div></td></tr>
<tr><th>SHA-256</th><td class="mono">{esc(card['raster_sha256'])}</td></tr>
<tr><th>What it is</th><td>{r['n_dots']:,} binary dots (value 1.0); 0 elsewhere, including outside the study area. Single band float32, EPSG:32611, 3292×3730, sample-submission transform. No NaN anywhere, so the portal's <q>Predicted values must be in range [0, 1]</q> error cannot occur.</td></tr>
<tr><th>Expected public-leaderboard DTI</th><td><strong>{me['point']['lbm_v1']:.3f}</strong> (90% interval {b['q05']:.3f}–{b['q95']:.3f}). For comparison, GEMSDOE32's best is 0.2778 (CLAIM), and the same model gives it {me['r0_same_model']['point']['lbm_v1']:.3f}.
<span class="small">Label: MODEL (fitted to 123 owner-reported scores; grouped-CV RMSE {me['validation']['logo_rmse_all']:.3f}). It is not an organizer score.</span></td></tr>
<tr><th>Unique?</th><td>{'Yes' if not u['duplicate'] else 'No'}: across all {u['registry_rasters']:,} public GEMSDOE rasters, at most {u['final_worst_overlap']:.1%} of its dots fall within 3 px of any one raster's dots (limit 70%), and the largest |rank correlation| is {u['final_worst_abs_rho']:.3f} (limit 0.90). Interpretation PI-1; the degenerate literal reading is also reported.</td></tr>
</table>
<p class="small">Run card: <a href="{href_prefix}downloads/{esc(Path(PRIMARY_CARD).name)}">JSON</a>. Leaderboard values are owner-reported and not mirrored (<a href="https://www.drivendata.org/termsofuse/">DrivenData Terms of Use</a>).
Weekly limit: 3 per week (the website's limit prevails). Choosing your final submission is a separate human step.</p>
</section>"""


def gates_table(card: dict, val: dict) -> str:
    g = card["gates_passed"]; h = card["holdout_dti"]; c = card["leakage_canaries"]; u = card["uniqueness"]
    row = lambda name, ok, detail: f"<tr><td>{esc(name)}</td><td>{'✅ pass' if ok else '⚠️ fail'}</td><td>{detail}</td></tr>"
    return "<table><tr><th>Gate</th><th>Result</th><th>Evidence</th></tr>" + "".join([
        row("Format (portal rules)", g["format"], "CRS, shape and transform match; float32 single band; all finite; values in {0,1}; zeros outside the footprint; no dots on mapped faults (shared writer and gates, re-read from disk)"),
        row("Uniqueness vs public registry (PI-1)", g["uniqueness_pi1"], f"Final dots: worst 3 px overlap {u['final_worst_overlap']:.4f} ≤ 0.70 and worst |ρ| {u['final_worst_abs_rho']:.3f} ≤ 0.90 across {u['registry_rasters']:,} rasters. Pre-placement surface: worst |ρ| {u['surface_worst_abs_rho']:.3f} ≤ 0.90. Diagnostic only: the unconstrained surface's top-N cells overlap {u['surface_worst_overlap']:.2f}, which is why the 70% cap is enforced during placement (PI-1b)."),
        row("Leaderboard-aligned validation (MODEL)", g["model_beats_0_2778_at_q05"], f"5% bootstrap bound {card['model_estimate']['bootstrap']['q05']:.3f} &gt; 0.2778; P(Δ vs R0 &gt; 0) = {card['model_estimate']['bootstrap']['delta_vs_R0']['p_gt0']:.2f}"),
        row("Leakage canaries (each feature alone)", g["no_leakage"], f"max AUC {c['max_auc']:.3f} ≤ 0.90"),
        row("Catalogue hide-and-recover holdout (reported)", g["catalogue_holdout_beats_r0_recipe"],
            f"HOLDOUT-DTI {h['exp1']['dti']:.4f} [{h['exp1']['ci95'][0]:.4f}, {h['exp1']['ci95'][1]:.4f}] vs R0 recipe {h['r0_recipe_control']['dti']:.4f} ({h['evaluator_version']}, {h['withheld_positive_pixels']:,} withheld). This instrument does not predict leaderboard scores: Spearman {val['spearman_holdout_vs_claim']:.2f} over {val['n']} scored rasters, and R0 itself scores 0.004 on it. It is reported, not used as the gate (irregularity IR-0127-2)."),
    ]) + "</table>"


def focus9_rows(f9: dict, f9u: dict, model: dict) -> str:
    fitted = {(r["site"], r["name"]): r for r in model["rows"]}
    out = []
    for site, s in f9.items():
        fr = fitted.get((site, s["best"]), {})
        u = f9u.get(site, {})
        dup_where = ", ".join(x.split("/")[-1] for x in (u.get("identical_bytes_elsewhere") or u.get("worst_overlap_in") or []))[:120]
        out.append(f"<tr><td><strong>{esc(site)}</strong></td><td><a href=\"{esc(s['raw_url'])}\">{esc(s['best'])}</a><br><span class=\"small mono\">sha256 {esc(s['sha256'][:16])}…</span></td>"
                   f"<td>{s['claim']:.4f}</td><td>{fr.get('logo', float('nan')):.3f}</td>"
                   f"<td>{'Yes' if u.get('unique_pi1') else 'No'}: {('overlap ' + format(u.get('worst_overlap', 0), '.2f') + ', ρ ' + format(u.get('worst_rho', 0), '.2f') + ' vs ' + esc(dup_where)) if u else ''}</td></tr>")
    return "".join(out)


def render_legacy_unsafe() -> dict[Path, str]:
    card, f9, f9u, model, val = load()
    current, readiness = status_cards(card)
    best_site = max(f9.items(), key=lambda kv: kv[1]["claim"])
    official = "".join(f"<li><a href=\"{esc(u)}\">{esc(t)}</a></li>" for t, u in OFFICIAL)
    idx = f"""<nav class="small"><a href="how-to-submit.html">How to submit</a><a href="nine-sites.html">Nine-site summary</a><a href="WHY_0_2778.md">Why 0.2778</a><a href="HYPOTHESES_20261027_LBM.md">Hypotheses</a><a href="archive.html">Archive</a></nav>
{submission_box(card)}
<section class="box"><h2 id="summary">Executive summary</h2>
<ul>
<li><strong>The file to submit is above.</strong> It is a new, unique GeoTIFF (not a copy of any GEMSDOE submission). It was built, validated and audited automatically.</li>
<li><strong>Why it should beat 0.2778:</strong> all 123 owner-reported scores were matched byte-for-byte to their public rasters. A model with the exact structure of the official metric was fit to them, and it locates where the hidden new faults are dense: more than 1.5 km from mapped faults (×5.7), 100 m off the H19-5 skeleton (×3.8), and where ≥ 5 of 10 independent good lineages agree (×15). Dots were placed by exact expected-DTI optimisation under that density, with the 70% / 3 px duplicate rule enforced during placement.</li>
<li><strong>Best existing submission:</strong> {esc(best_site[0])} <code>{esc(best_site[1]['best'])}</code>, CLAIM {best_site[1]['claim']:.4f}. All nine reviewed sites' best files are duplicates of rasters at other sites (table below).</li>
<li><strong>Honesty labels:</strong> CLAIM = owner-reported score, MODEL = estimate, HOLDOUT-DTI = shared spatial holdout. No number here is organizer-confirmed until you submit.</li>
</ul>
<h3>Automated gates</h3>
{gates_table(card, val)}
</section>
<section class="box"><h2 id="nine-sites">Nine focus sites: best submission per site</h2>
<p class="small">CLAIM = owner-reported leaderboard score. MODEL = grouped-cross-validated estimate (that site's lineage held out). “Unique?” compares each site's best raster with every raster served by the other sites (PI-1, 2,060 rasters). <a href="nine-sites.html">Details and every scored file per site →</a></p>
<table><tr><th>Site</th><th>File to download (best CLAIM)</th><th>CLAIM</th><th>MODEL (held-out)</th><th>Unique vs other sites?</th></tr>{focus9_rows(f9, f9u, model)}</table>
</section>
<section class="box"><h2 id="why">Why GEMSDOE32 scored 0.2778</h2>
<p>R0 is <code>D2.8 ∧ d_cat &gt; 2</code>: the H19-5 multiline skeleton dotted every 2.8 px (mean on-trace credit 1 − s/12 ≈ 0.77, with 2.7× fewer positives), then with every dot within 200 m of a mapped fault removed. Those removals gained exactly the pure-false-positive amount per dot (2.78×10⁻⁶ and 2.75×10⁻⁶), so there is almost no new-fault truth beside mapped traces. Its remaining weakness, per the model, is that about 97% of its dot mass lands as false positives in low-density classes. <a href="WHY_0_2778.md">Full derivation →</a></p>
</section>
<section class="box"><h2 id="limits">Limitations and next steps</h2>
<ul>
<li>The estimate is a MODEL fitted to CLAIM scores from the <em>public</em> leaderboard subset. The private set and Phase 2 use other or revised labels, so generalisation is not guaranteed.</li>
<li>The candidate concentrates dots more strongly than any scored raster did. The trust-region cap holds the consensus share at ≤ 55% (scored rasters reached 49%), but extrapolation error is not fully captured by the bootstrap.</li>
<li>Uniqueness uses interpretation PI-1. Under the literal reading, a raster positive on every footprint cell makes every candidate a duplicate (reported in the run card).</li>
<li>Next: submit once and record the organizer score in <code>ledger/submissions.csv</code>, then refit the model with it. Biggest untapped data: 1 m 3DEP / GeoDAWN EarthMRI lidar (H4), which this sandbox cannot download.</li>
</ul></section>
<section class="box"><h2 id="official">Official sources (for manual verification)</h2><ul>{official}</ul></section>"""
    howto = f"""<nav class="small"><a href="index.html">← Back to summary</a></nav>
{submission_box(card)}
<section class="box"><h2>How to submit (3 steps)</h2>
<ol>
<li><strong>Download</strong> the GeoTIFF with the blue button above (or the one-TIFF ZIP). Do not open and re-save it in GIS software, which can add a nodata value.</li>
<li><strong>Open</strong> the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">DrivenData submission page</a> (log in) and upload the <code>.tif</code>, or the <code>.zip</code> containing exactly one GeoTIFF.</li>
<li><strong>Paste</strong> the submission name and note from the black boxes above, then press Submit. Afterwards, record the score you see in <code>ledger/submissions.csv</code> with the SHA-256, so the next session can learn from it.</li>
</ol>
<div class="warn"><strong>Weekly limit:</strong> 3 submissions per week (the limit shown on the competition website prevails, per DrivenData staff). Before the deadline you must select <strong>one</strong> final submission. It is scored on the private set (Phase 1) and the expert-revised set (Phase 2).</div>
</section>
<section class="box"><h2>Portal format rules this file satisfies</h2>
<table><tr><th>Rule (problem description)</th><th>This file</th></tr>
<tr><td>Single-band GeoTIFF (.tif), or a .zip containing one GeoTIFF</td><td>1 band; ZIP holds exactly that TIFF</td></tr>
<tr><td>Same CRS as the training data (EPSG:32611)</td><td>EPSG:32611</td></tr>
<tr><td>Same resolution and bounds (100 m; shape and transform of the sample submission)</td><td>3292 × 3730 px, transform (100, 0, 243350, 0, −100, 4508550)</td></tr>
<tr><td>float32 values between 0 and 1</td><td>float32, values ∈ {{0, 1}}</td></tr>
<tr><td>Outside the bounds null/NaN</td><td>0.0 outside the study area. Zeros-outside files have been accepted and scored (e.g. GEMSDOE32's 0.2778 file), and they avoid the range error.</td></tr>
</table></section>
<section class="box"><h2>Fixing “Predicted values must be in range [0, 1]”</h2>
<p>This error comes from cells the validator reads as outside [0, 1]. The usual causes are a nodata sentinel such as −3.4028e38 stored outside the study area, NaN/inf values, values above 1 (e.g. 0–255 or 0–100 scaling), or negative values. All files served here are all-finite with values in [0, 1]. To repair any other raster:</p>
<pre class="copy">import numpy as np, rasterio
with rasterio.open("in.tif") as s:
    a = s.read(1).astype("float32"); prof = s.profile
a = np.nan_to_num(a, nan=0.0, posinf=1.0, neginf=0.0)
a[a &lt; -1e30] = 0.0                      # nodata sentinels
a = np.clip(a, 0.0, 1.0).astype("float32")
prof.update(dtype="float32", count=1, nodata=None, compress="deflate")
with rasterio.open("out.tif", "w", **prof) as d:
    d.write(a, 1)</pre>
</section>
<section class="box"><h2>Official sources</h2><ul>{official}</ul></section>"""
    claims = json.loads((EVID / "claims_matched_20261027.json").read_text(encoding="utf-8"))["rows"]
    blocks = []
    fitted = {(r["site"], r["name"]): r for r in model["rows"]}
    for site, s in f9.items():
        rows = sorted([r for r in claims if r["site"] == site], key=lambda r: -r["claim"])
        u = f9u.get(site, {})
        trs = "".join(
            f"<tr><td>{'⭐ ' if r['name'] == s['best'] else ''}{esc(r['name'])}</td><td>{r['claim']:.4f}</td>"
            f"<td>{fitted.get((site, r['name']), {}).get('logo', float('nan')):.3f}</td>"
            f"<td class=\"mono small\">{esc(r.get('match', {}).get('path', '—'))}</td></tr>" for r in rows)
        blocks.append(f"""<section class="box"><h2 id="{esc(site)}">{esc(site)}: best {s['claim']:.4f} (CLAIM)</h2>
<p><a class="btn btn2" href="{esc(s['raw_url'])}">⬇ Download best file</a> <a href="{esc(s['blob_url'])}">view on GitHub @ {esc(s['commit'][:10])}</a> · SHA-256 <span class="mono">{esc(s['sha256'])}</span></p>
<p><strong>Unique vs other sites:</strong> {'Yes' if u.get('unique_pi1') else 'No'}. Worst 3 px overlap {u.get('worst_overlap', 0):.3f} and |ρ| {abs(u.get('worst_rho', 0)):.3f}, against {esc(', '.join(u.get('worst_overlap_in', [])))}. Identical bytes also served by: {esc(', '.join(u.get('identical_bytes_elsewhere', [])) or 'none')}.</p>
<table><tr><th>Submission (owner-reported)</th><th>CLAIM</th><th>MODEL (held-out)</th><th>Matched file</th></tr>{trs}</table></section>""")
    nine = f"""<nav class="small"><a href="index.html">← Back to summary</a></nav>
<h1>Nine focus sites: executive summary</h1>
<p class="small">Scores are owner-reported CLAIMs (2026-10-27 prompt) matched byte-for-byte to public rasters (<code>evidence/claims_matched_20261027.json</code>). File links are pinned to commits, with blob SHA verified through the GitHub API (<code>evidence/focus9_sources_20261027.json</code>). Uniqueness: <code>evidence/focus9_uniqueness_20261027.json</code>. <strong>None of these nine files is unique</strong>; identical or near-identical copies are served by other GEMSDOE sites. For a unique file to submit, use the <a href="index.html#submit-now">primary download</a>.</p>
<section class="box"><table><tr><th>Site</th><th>File to download (best CLAIM)</th><th>CLAIM</th><th>MODEL (held-out)</th><th>Unique vs other sites?</th></tr>{focus9_rows(f9, f9u, model)}</table></section>
{''.join(blocks)}"""
    root = f"""<meta http-equiv="refresh" content="0; url=docs/index.html">
<p><a href="docs/index.html">GEMSDOE92 submission summary →</a></p>
{submission_box(card, href_prefix="docs/").replace('data-primary="true" ', '')}"""
    return {
        DOCS / "index.html": page("GEMSDOE92 — GEMS Prize submission (unique, validated)", idx),
        DOCS / "how-to-submit.html": page("GEMSDOE92 — how to submit", howto),
        DOCS / "nine-sites.html": page("GEMSDOE92 — nine-site executive summary", nine),
        ROOT / "index.html": page("GEMSDOE92 — GEMS Prize submission", root),
        DL / "current_submission.json": json.dumps(current, indent=2) + "\n",
        DL / "readiness.json": json.dumps(readiness, indent=2) + "\n",
    }


def render() -> dict[Path, str]:
    """Publish a research-only view until every binding gate is supported."""
    card, f9, f9u, model, val = load()
    # Never let a historical model-based waiver grant automatic clearance.
    if card.get("verdict") != "negative" or card.get("submission_eligible") is not False:
        raise ValueError("current artifact is blocked by holdout and literal registry rules")
    current, readiness = status_cards(card)
    current.pop("model_estimate_point", None)
    current.pop("model_estimate_interval90", None)
    current.pop("evidence_class_of_estimate", None)
    readiness["submission_status"] = "DO NOT SUBMIT — holdout gate and literal registry stop"
    h = card["holdout_dti"]
    rows = "".join(
        f'<tr><td>{esc(site)}</td><td><a href="{esc(s["blob_url"])}">{esc(s["best"])}</a></td>'
        f'<td>{s["claim"]:.4f} CLAIM</td><td>Unavailable</td><td>Not cleared</td></tr>'
        for site, s in f9.items()
    )
    panel = f'''<section class="box no" id="submit-now"><h1><span class="badge bno">DO NOT SUBMIT</span> No eligible submission</h1>
<p>Historical research only: <a data-primary="true" href="downloads/{esc(Path(card["raster"]["file"]).name)}" download>Download LBMC1 research TIFF</a>. Do not upload it. <a href="downloads/{esc(Path(PRIMARY_CARD).name)}">Run card</a>.</p>
<p>The candidate failed the required catalogue holdout comparison and was a duplicate under the literal registry interpretation. The earlier model-based clearance is withdrawn. Local format checks cannot guarantee portal acceptance.</p>
<p>HOLDOUT-DTI ({esc(h["evaluator_version"])}, {h["withheld_positive_pixels"]:,} withheld positives): {h["exp1"]["dti"]:.4f}, 95% CI [{h["exp1"]["ci95"][0]:.4f}, {h["exp1"]["ci95"][1]:.4f}]; control {h["r0_recipe_control"]["dti"]:.4f}, 95% CI [{h["r0_recipe_control"]["ci95"][0]:.4f}, {h["r0_recipe_control"]["ci95"][1]:.4f}]. Historical static holdout may not establish prospective fold-local validity.</p></section>'''
    body = panel + f'''<section class="box" id="summary"><h2>Executive summary</h2>
<p>GEMSDOE32 has the highest owner-reported result among the nine listed. CLAIM values are not organizer-confirmed receipts. No reliable leaderboard estimate is established; MODEL projections are not scores. A higher score may be possible but has not been demonstrated by an eligible new file.</p>
<p>The dotted-trace and catalogue-collar lineage plausibly reduced redundant positive pixels, but a causal explanation of the hidden score cannot be proven from reported results alone. <a href="focus9.html">Prior detailed audit and sources</a>.</p>
<div style="overflow-x:auto"><table><tr><th>Site</th><th>Historical research file (not for submission)</th><th>Owner CLAIM</th><th>Score estimate</th><th>Unique / eligible?</th></tr>{rows}</table></div></section>
<section class="box"><h2>Next steps and sources</h2><p>Resolve the assigned method lane and registry interpretation, restore and verify the cached inputs, then run leakage canaries, fold-local buffered holdouts, pre-placement and final registry checks and the shared writer. A separate selector decides whether to use a weekly slot.</p>
<p><a href="how-to-submit.html">How to submit once cleared</a> · <a href="nine-sites.html">Nine-site review</a> · <a href="HYPOTHESES_20261027_D30D387C.md">Prior ranked hypotheses</a> · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Official problem</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution">Official reference solution</a> · <a href="https://www.drivendata.org/termsofuse/">Terms of use</a>. The leaderboard is not mirrored.</p></section>'''
    how = panel + '''<section class="box"><h2>How to submit a future cleared file</h2><p>Do not submit the research file above. Once a separate selector approves a new, byte-bound candidate, download its exact GeoTIFF, open the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">DrivenData submission page</a>, select it and enter its short note. Verify the current weekly limit on the portal; historical documentation mentions 3 submissions per week.</p><p>For “Predicted values must be in range [0, 1]”, check for NaN, infinities, nodata sentinels and out-of-range values against the official sample and format; do not blindly clip scientifically meaningful values. A local format pass is not a portal receipt. Outside-footprint encoding remains unresolved.</p></section>'''
    nine = '''<section class="box no"><h1>Nine-site executive summary</h1><p>DO NOT SUBMIT: historical files are research only. Owner CLAIMs are not organizer receipts and no reliable score estimate is available. <a href="focus9.html">Detailed historical evidence and pairwise comparisons</a>.</p></section>''' + f'<section class="box"><table><tr><th>Site</th><th>Historical research file</th><th>Owner CLAIM</th><th>Score estimate</th><th>Unique / eligible?</th></tr>{rows}</table></section>'
    root = '<meta http-equiv="refresh" content="0; url=docs/index.html"><h1>DO NOT SUBMIT — no eligible TIFF</h1><a href="docs/index.html">Open executive summary</a> · <a href="https://www.drivendata.org/termsofuse/">Terms of use</a>. Leaderboard is not mirrored.'
    return {DOCS / "index.html": page("GEMSDOE92 — blocked", body),
            DOCS / "how-to-submit.html": page("GEMSDOE92 — submission guide", how),
            DOCS / "nine-sites.html": page("GEMSDOE92 — nine sites", nine),
            ROOT / "index.html": page("GEMSDOE92 — blocked", root),
            DL / "current_submission.json": json.dumps(current, indent=2) + "\n",
            DL / "readiness.json": json.dumps(readiness, indent=2) + "\n"}


def main() -> int:
    for p, t in render().items():
        p.write_text(t, encoding="utf-8")
        print("wrote", p.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
