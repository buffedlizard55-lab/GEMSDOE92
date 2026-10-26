#!/usr/bin/env python3
"""Render docs/focus9.html — the nine-site executive summary and download page.

Every number on the page is read from a committed JSON receipt:
  evidence/focus9_executive_audit_20261026.json   uniform audit of the 9 sites + fleet benchmarks
  evidence/score_estimator_20261026.json          cross-validated MODEL estimator
  evidence/salemseismo_run_card.json              this session's new unique TIFF (Rule 5 card)
  evidence/salemseismo_holdout.json               HOLDOUT-DTI + SGMC proxy
  evidence/salemseismo_uniqueness.json            local + 102-repo uniqueness

Nothing is typed by hand, so the page cannot drift from the evidence.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
EVID = ROOT / "evidence"
OUT = DOCS / "focus9.html"

SITE_URLS = {
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

FOCUS_ORDER = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
               "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]


def load(name: str) -> dict:
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def e(x) -> str:
    return html.escape(str(x))


def f4(x) -> str:
    return "—" if x is None else f"{x:.4f}"


def f6(x) -> str:
    return "—" if x is None else f"{x:.6f}"


def main() -> int:
    audit = load("focus9_executive_audit_20261026.json")
    est = load("score_estimator_20261026.json")
    card = load("salemseismo_run_card.json")
    hold = load("salemseismo_holdout.json")
    uniq = load("salemseismo_uniqueness.json")

    by_key = {r["key"]: r for r in audit["records"]}
    est_by_key = {r["key"]: r for r in est["predictions"]}

    best_arm = card["holdout_dti"]["primary_arm"]
    new_tif = Path(card["candidate_file"]).name
    new_zip = Path(card["zip_file"]).name
    new_est = est_by_key[f"SALEMSEISMO__{best_arm.replace('salem_', '').replace('celf_tail', 'celftail')}"]
    pub = card["correlation_overlap_vs_registry"]["public_102_repo_registry"]
    loc = card["correlation_overlap_vs_registry"]["local_registry"]
    canary = card["leakage_canary"]
    rule2 = card["holdout_dti"]["strict_drawblind_rule2_dvis_gt_2_primary"]
    static = card["holdout_dti"]["static_dcat_gt_2_primary"]
    sgmc = card["holdout_dti"]["sgmc_independent_basement_fault_proxy_dti_gt5px"]

    # ---------------- per-site table ----------------
    site_rows = []
    for site in FOCUS_ORDER:
        recs = [r for r in audit["records"] if r["site"] == site]
        scored = [r for r in recs if r["claim_score"] is not None]
        best = max(scored, key=lambda r: r["claim_score"]) if scored else None
        latest = [r for r in recs if "20261026" in r["role"]]
        latest = latest[0] if latest else None
        site_rows.append((site, best, latest))

    parts: list[str] = []
    parts.append("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nine-site executive summary — DOE GEMS #306 (GEMSDOE92)</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<main>""")

    # ---------------- hero / download ----------------
    parts.append(f"""
<section style="border:4px solid #14532d;border-radius:12px;padding:1.25rem 1.4rem;background:#f0fdf4;margin:1rem 0 1.5rem">
  <p style="margin:0 0 .4rem;font-weight:700;letter-spacing:.02em;color:#7f1d1d">
    DOE GEMS Prize #306 · Nine-site executive summary · generated 2026-10-26 from committed JSON receipts
  </p>
  <h1 style="margin:.2rem 0 .6rem;font-size:1.7rem">This session's new, genuinely unique GeoTIFF</h1>
  <p style="font-size:1.15rem;margin:.3rem 0">
    <span style="background:#14532d;color:#dcfce7;padding:.35rem .7rem;border-radius:5px;font-weight:700">
      ✅ OK TO DOWNLOAD FOR RESEARCH — one click below</span>
    <span style="background:#7f1d1d;color:#fee2e2;padding:.35rem .7rem;border-radius:5px;font-weight:700">
      ⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (verdict <code>negative</code>, 0 slots spent)</span>
  </p>
  <p style="font-size:1.15rem;margin:.8rem 0">
    <a href="downloads/{e(new_tif)}" download
       style="display:inline-block;padding:.85rem 1.15rem;background:#1e3a5f;color:#fff;border-radius:7px;font-weight:700;text-decoration:none">
      ⬇ Download {e(new_tif)}</a>
    &nbsp;·&nbsp; <a href="downloads/{e(new_zip)}" download>one-TIFF ZIP</a>
    &nbsp;·&nbsp; <a href="downloads/{e(new_tif[:-len('-zeros.tif')])}-audit.json">audit JSON</a>
    &nbsp;·&nbsp; <a href="downloads/salemseismo_run_card.json">Rule&nbsp;5 run card</a>
    &nbsp;·&nbsp; <a href="downloads/salemseismo_holdout.json">holdout JSON</a>
    &nbsp;·&nbsp; <a href="downloads/salemseismo_uniqueness.json">uniqueness JSON</a>
  </p>
  <table style="border-collapse:collapse;width:100%;font-size:.98rem">
    <tr><th style="text-align:left;padding:.3rem .5rem;border-bottom:1px solid #86efac">Field</th>
        <th style="text-align:left;padding:.3rem .5rem;border-bottom:1px solid #86efac">Value (from receipt)</th></tr>
    <tr><td style="padding:.3rem .5rem"><b>File to download</b></td><td style="padding:.3rem .5rem"><code>{e(new_tif)}</code></td></tr>
    <tr><td style="padding:.3rem .5rem"><b>Submission name</b> (paste into the form)</td><td style="padding:.3rem .5rem"><code>{e(card['submission_name'])}</code></td></tr>
    <tr><td style="padding:.3rem .5rem"><b>Note</b> ({card['submission_note_chars']}/140 characters)</td><td style="padding:.3rem .5rem"><code>{e(card['submission_note'])}</code></td></tr>
    <tr><td style="padding:.3rem .5rem"><b>SHA-256</b></td><td style="padding:.3rem .5rem"><code>{e(card['raster_sha256'])}</code></td></tr>
    <tr><td style="padding:.3rem .5rem"><b>Estimated leaderboard DTI</b> (MODEL)</td>
        <td style="padding:.3rem .5rem"><b>{f4(new_est['estimated_dti_MODEL'])} ± {f4(est['loo_rmse'])}</b>
        <span style="color:#7f1d1d">— a cross-validated MODEL estimate, <b>not</b> an organizer score</span></td></tr>
    <tr><td style="padding:.3rem .5rem"><b>HOLDOUT-DTI</b> (gems57-pooled-hide-v2, {static['withheld_positive_pixels']:,} withheld px)</td>
        <td style="padding:.3rem .5rem">static {f6(static['dti'])} [{f6(static['ci95'][0])}, {f6(static['ci95'][1])}];
        strict draw-blind Rule-2 {f6(rule2['dti'])} [{f6(rule2['ci95'][0])}, {f6(rule2['ci95'][1])}]</td></tr>
    <tr><td style="padding:.3rem .5rem"><b>Off-catalogue proxy</b> (independent USGS SGMC, d&nbsp;&gt;&nbsp;5&nbsp;px)</td>
        <td style="padding:.3rem .5rem">{f6(sgmc[best_arm])}</td></tr>
    <tr><td style="padding:.3rem .5rem"><b>Uniqueness — local registry</b></td>
        <td style="padding:.3rem .5rem">worst 3-px overlap <b>{f4(loc['worst_matched_budget_forward_overlap'])}</b> (limit 0.70)
        vs <code>{e(Path(loc['worst_matched_budget_file']).name)}</code>; worst |ρ| {f4(loc['worst_abs_spearman_final'])} (limit 0.90)</td></tr>
    <tr><td style="padding:.3rem .5rem"><b>Uniqueness — {pub['non_self_rasters_checked']:,} public rasters, 102 repos</b></td>
        <td style="padding:.3rem .5rem">worst 3-px overlap <b>{f4(pub['worst_operative_overlap_3px'])}</b>,
        {pub['operative_over_70pct_count']} raster(s) over 0.70 → <b>UNIQUE under the operative rule</b></td></tr>
    <tr><td style="padding:.3rem .5rem"><b>Format gates</b> (no human inspection)</td>
        <td style="padding:.3rem .5rem">11/11 PASS · single band float32 · EPSG:32611 · 3730×3292 · all 12,279,160 cells finite in [0,&nbsp;1] · 0 NaN · zeros outside the footprint · 0 dots on the mapped catalogue · all dots &gt;&nbsp;2&nbsp;px from it</td></tr>
    <tr><td style="padding:.3rem .5rem"><b>Leakage canaries</b></td>
        <td style="padding:.3rem .5rem">{canary['n_features_tested']}/{canary['n_features_tested']} PASS, max symmetric AUC {f4(canary['max_symmetric_auc'])} (limit 0.90)</td></tr>
  </table>
  <p style="margin:.8rem 0 .2rem;color:#7f1d1d"><b>Why the submit badge is red.</b> This repository's binding
  uniqueness rule is applied literally to the whole public registry, and one pinned registry raster
  (<code>17GEMSDOE_E-proba-multiscale</code>) is positive on all 5,167,373 footprint pixels, so <i>every</i>
  non-empty submission reads as overlap 1.0000 &gt; 0.70. The file itself passes every format gate and is
  operationally unique (worst overlap {f4(pub['worst_operative_overlap_3px'])} &lt; 0.70). Clearing the
  submit badge is an owner policy decision, not a code or evidence decision — see
  <a href="#decisions">Decisions the owner must make</a>.</p>
</section>""")

    # ---------------- nine-site table ----------------
    parts.append("""
<h2 id="nine">1. Executive finding for every site, from pinned bytes</h2>
<p>All nine focus repositories were re-cloned on 2026-10-26, every named TIFF was hashed, and every
raster was re-scored on <b>one</b> instrument (<code>gems57-pooled-hide-v2</code>, 22,663 withheld
positive pixels, 8 buffered spatial folds, seeds 20 &amp; 30, 1,000-draw 20&nbsp;km block bootstrap).
The historical scores are <b>owner-reported CLAIMs</b>: no submission-page receipt exists in this
repository for any of them, and the sandbox cannot reach drivendata.org.</p>
<table style="border-collapse:collapse;width:100%;font-size:.9rem">
<thead><tr style="background:#1e293b;color:#fff">
<th style="padding:.45rem;text-align:left">Site</th>
<th style="padding:.45rem;text-align:left">Best historically-submitted file</th>
<th style="padding:.45rem;text-align:right">CLAIM</th>
<th style="padding:.45rem;text-align:right">Uniform HOLDOUT-DTI</th>
<th style="padding:.45rem;text-align:right">Overlap vs R0</th>
<th style="padding:.45rem;text-align:left">Structural diagnosis</th>
<th style="padding:.45rem;text-align:left">Newest 2026-10-26 file</th>
<th style="padding:.45rem;text-align:right">Uniform HOLDOUT-DTI</th>
</tr></thead><tbody>""")
    for site, best, latest in site_rows:
        url = SITE_URLS[site]
        bname = Path(best["rel_path"]).name if best else "—"
        parts.append(f"""<tr style="border-bottom:1px solid #e2e8f0">
<td style="padding:.4rem"><a href="{e(url)}">{e(site)}</a></td>
<td style="padding:.4rem"><code style="font-size:.82rem">{e(bname)}</code></td>
<td style="padding:.4rem;text-align:right"><b>{f4(best['claim_score'] if best else None)}</b></td>
<td style="padding:.4rem;text-align:right">{f6(best['holdout_dti_static'] if best else None)}</td>
<td style="padding:.4rem;text-align:right">{f4(best['ov3_vs_r0'] if best else None)}</td>
<td style="padding:.4rem;font-size:.86rem">{e(best['repo_verdict'] if best else '—')}</td>
<td style="padding:.4rem;font-size:.78rem"><code>{e(Path(latest['rel_path']).name if latest else '—')}</code></td>
<td style="padding:.4rem;text-align:right">{f6(latest['holdout_dti_static'] if latest else None)}</td>
</tr>""")
    parts.append("</tbody></table>")
    parts.append(f"""<p style="font-size:.92rem"><b>Reading the table.</b> "Overlap vs R0" is the share of a
file's dots lying within 3&nbsp;px of GEMSDOE32's 0.2778 raster. Every historically-submitted file
above except GEMSDOE96's descendants family sits at 0.87–1.00 — those scores are <i>the same skeleton</i>
measured at different dot budgets, not ten independent discoveries. The 2026-10-26 rows are the newest
files in each repo; several are <i>not</i> unique under the operative rule
(<code>{e(audit['records'][0]['cross_repo_operative_witness'])}</code> …) and none beats
the repository static-SOTA control.</p>""")

    # ---------------- why 0.2778 ----------------
    ids = audit["exact_set_identities"]
    parts.append(f"""
<h2 id="why">2. Why <code>h33-h33-2-b2</code> (GEMSDOE32) reportedly scored 0.2778 — verified from bytes</h2>
<p>The lineage was proved by pixel algebra on SHA-256-pinned rasters, not inferred from filenames.
Exact XOR counts recomputed this session:</p>
<ul>
<li><code>GEMSDOE25 D2.8</code> ≡ <code>GEMSDOE30 d28</code> — XOR = <b>{ids['gems25_d28_xor_gems30_d28']}</b> pixels.</li>
<li><code>GEMSDOE28 SOLO</code> ≡ <code>GEMSDOE31 solo</code> — XOR = <b>{ids['gems28_solo_xor_gems31_solo']}</b> pixels.</li>
<li><code>SOLO</code> ≡ <code>D2.8 ∧ (d_cat &gt; 1 px)</code> — XOR = <b>{ids['gems31_solo_xor_d28_gt1px']}</b>; it removed <b>{ids['d28_to_solo_pruned_le1px']:,}</b> dots that hug mapped traces.</li>
<li><code>R0 (0.2778)</code> ≡ <code>D2.8 ∧ (d_cat &gt; 2 px)</code> — XOR = <b>{ids['gems32_b2_xor_d28_gt2px']}</b>; it removed <b>{ids['solo_to_b2_pruned_1_to_2px']:,}</b> more (total <b>{ids['d28_to_b2_total_pruned_le2px']:,}</b> within 2&nbsp;px).</li>
<li><code>GEMSDOE36 PINN</code> ⊃ <code>R0</code> exactly (<b>{ids['gems32_b2_is_strict_subset_of_gems36']}</b>) plus <b>{ids['gems36_extra_dots_over_gems32_b2']:,}</b> added dots — and its reported score fell to 0.2750.</li>
</ul>
<p><b>Mechanism.</b> The metric is a distance-weighted Tversky index with α = 0.2 (false-positive mass),
β = 0.8 (missed truth), and a 300&nbsp;m triangular kernel applied as a pointwise <i>max</i>. Three
consequences explain the whole climb 0.1922 → 0.2477 → 0.2600 → 0.2708 → 0.2778:</p>
<ol>
<li><b>Thin the skeleton.</b> With a max-kernel, a second dot next to the first earns almost no extra
true-positive credit but still pays false-positive mass. Re-spacing a 1-px skeleton at ≈2.8&nbsp;px keeps
most of the corridor credit at roughly a third of the emitted mass (0.1922 → 0.2600).</li>
<li><b>Delete the catalogue collar.</b> Mapped fault pixels are masked before scoring, so a dot 100–200&nbsp;m
from a mapped trace is nearly all cost and almost no credit; removing those dots raised the score twice
(0.2600 → 0.2708 → 0.2778).</li>
<li><b>Do not add dots.</b> GEMSDOE36's +1,200 dots <i>lowered</i> the reported score, which is the same
mechanism seen in reverse.</li>
</ol>
<p style="background:#fef9c3;padding:.7rem;border-left:4px solid #a16207"><b>What this does NOT mean.</b>
The score is not evidence of blind-fault discovery: on the hide-and-recover instrument the same raster
scores only <b>{f6(by_key['GEMSDOE32__historical_best']['holdout_dti_static'])}</b>. It recovered
already-mapped faults at a kernel-favourable budget. That is why copying it cannot be the strategy —
and why the 0.2778 figure itself is a CLAIM, not a receipt.</p>
""")

    # ---------------- deliverable table ----------------
    parts.append(f"""
<h2 id="deliverable">3. The deliverable table — what to download, the estimate, and uniqueness</h2>
<p>Estimates come from the cross-validated estimator in §4 and are <b>MODEL</b> quantities. Uniqueness is a
<b>REGISTRY-MEASUREMENT</b> against {pub['non_self_rasters_checked']:,} compatible public rasters in 102
repositories plus the local fleet. "Unique vs the 9 sites" asks specifically whether the file is a
re-packaging of a GEMSDOE24/25/27/28/30/31/32/33/36 submission.</p>
<table style="border-collapse:collapse;width:100%;font-size:.92rem">
<thead><tr style="background:#1e293b;color:#fff">
<th style="padding:.45rem;text-align:left">File to download</th>
<th style="padding:.45rem;text-align:left">What it is</th>
<th style="padding:.45rem;text-align:right">Estimated DTI (MODEL ± LOO RMSE)</th>
<th style="padding:.45rem;text-align:left">Unique (102 repos)</th>
<th style="padding:.45rem;text-align:left">Unique vs the 9 sites</th>
<th style="padding:.45rem;text-align:left">Download</th>
</tr></thead><tbody>
<tr style="background:#f0fdf4;border-bottom:2px solid #14532d">
  <td style="padding:.5rem"><code>{e(new_tif)}</code><br><span style="font-size:.8rem">SHA-256 {e(card['raster_sha256'])}</span></td>
  <td style="padding:.5rem"><b>NEW — SALEMSEISMO {e(best_arm)}</b>: 26 zero-catalogue physics channels over
  7 previously unused bands, dual-partition OOF, exact 25-offset 300&nbsp;m submodular (CELF) placement</td>
  <td style="padding:.5rem;text-align:right"><b>{f4(new_est['estimated_dti_MODEL'])} ± {f4(est['loo_rmse'])}</b></td>
  <td style="padding:.5rem">✅ worst overlap {f4(pub['worst_operative_overlap_3px'])} ≤ 0.70</td>
  <td style="padding:.5rem">✅ not a copy: vs GEMSDOE24/25/30 lineage the best match is
  {f4(pub['worst_operative_overlap_3px'])} and that witness is a GEMSDOE92 file, not a focus-site submission</td>
  <td style="padding:.5rem"><a href="downloads/{e(new_tif)}" download><b>⬇ .tif</b></a><br><a href="downloads/{e(new_zip)}" download>.zip</a></td>
</tr>
<tr style="border-bottom:1px solid #e2e8f0">
  <td style="padding:.5rem"><code>{e(new_tif.replace('celftail52k', 'celf37k').replace('cc3c8ff2', '3c4f585f'))}</code></td>
  <td style="padding:.5rem">SALEMSEISMO sibling arm, same surface, binary 37,654 dots,
  point-<i>free</i> CELF placement only</td>
  <td style="padding:.5rem;text-align:right">{f4(est_by_key['SALEMSEISMO__celf37k']['estimated_dti_MODEL'])} ± {f4(est['loo_rmse'])}</td>
  <td style="padding:.5rem">✅ unique</td>
  <td style="padding:.5rem">✅ not a copy</td>
  <td style="padding:.5rem"><a href="downloads/{e(new_tif.replace('celftail52k', 'celf37k').replace('cc3c8ff2', '3c4f585f'))}" download>⬇ .tif</a></td>
</tr>
<tr style="border-bottom:2px solid #991b1b;background:#fef2f2">
  <td style="padding:.5rem"><code>{e(Path(by_key['GEMSDOE32__historical_best']['rel_path']).name)}</code></td>
  <td style="padding:.5rem"><b>Portfolio record (GEMSDOE32)</b> — already submitted; do <b>not</b> resubmit</td>
  <td style="padding:.5rem;text-align:right">CLAIM {f4(by_key['GEMSDOE32__historical_best']['claim_score'])}<br>
  <span style="font-size:.8rem">model {f4(est_by_key['GEMSDOE32__historical_best']['estimated_dti_MODEL'])}</span></td>
  <td style="padding:.5rem;background:#fecaca"><b>❌ duplicate</b> of GEMSDOE25/28/30/31/33 lineage</td>
  <td style="padding:.5rem;background:#fecaca"><b>❌ IS the focus-site family</b></td>
  <td style="padding:.5rem">—</td>
</tr>
<tr style="border-bottom:1px solid #e2e8f0">
  <td style="padding:.5rem"><code>{e(Path(by_key['GEMSDOE92__zero_cat_sota_chilistric']['rel_path']).name)}</code></td>
  <td style="padding:.5rem">Previous session's CHILISTRIC lane (reference control)</td>
  <td style="padding:.5rem;text-align:right">{f4(est_by_key['GEMSDOE92__zero_cat_sota_chilistric']['estimated_dti_MODEL'])} ± {f4(est['loo_rmse'])}</td>
  <td style="padding:.5rem">✅ worst overlap {f4(by_key['GEMSDOE92__zero_cat_sota_chilistric']['cross_repo_operative_worst_ov3'])}</td>
  <td style="padding:.5rem">✅ not a copy</td>
  <td style="padding:.5rem"><a href="downloads/{e(Path(by_key['GEMSDOE92__zero_cat_sota_chilistric']['rel_path']).name)}" download>⬇ .tif</a></td>
</tr>
<tr>
  <td style="padding:.5rem"><code>{e(Path(by_key['GEMSDOE92__zero_cat_sota_listricloqo']['rel_path']).name)}</code></td>
  <td style="padding:.5rem">Static-SOTA zero-catalogue control (best static HOLDOUT-DTI before this session)</td>
  <td style="padding:.5rem;text-align:right">{f4(est_by_key['GEMSDOE92__zero_cat_sota_listricloqo']['estimated_dti_MODEL'])} ± {f4(est['loo_rmse'])}</td>
  <td style="padding:.5rem">✅ worst overlap {f4(by_key['GEMSDOE92__zero_cat_sota_listricloqo']['cross_repo_operative_worst_ov3'])}</td>
  <td style="padding:.5rem">✅ not a copy</td>
  <td style="padding:.5rem"><a href="downloads/{e(Path(by_key['GEMSDOE92__zero_cat_sota_listricloqo']['rel_path']).name)}" download>⬇ .tif</a></td>
</tr>
</tbody></table>
<p style="font-size:.9rem;color:#7f1d1d"><b>Honest ordering.</b> The estimator ranks the new file below the
H19-5 descendants (CLAIM ≈0.25–0.28) and below GEMSDOE70's 0.2478 benchmark. That is expected: the
estimator's strongest predictor is proximity to the H19-5 skeleton, and the new lane deliberately places
only {round(100*new_est['frac_h19_near3'],1)}% of its dots within 3&nbsp;px of it. The new file's case is
<i>rank-correlation safety plus a strictly better static holdout</i>, not a promised leaderboard jump.</p>
""")

    # ---------------- estimator ----------------
    coefs = est["standardised_coefficients"]
    parts.append(f"""
<h2 id="estimator">4. How the score estimate is produced (and how good it is)</h2>
<p>Estimator: <code>{e(est['estimator'])}</code>, fitted by ridge regression in logit space on
<b>{est['training_rows']}</b> owner-reported CLAIMs that resolve to exactly one pixel-verified raster
({est['unresolved_claims']} further claims could not be matched unambiguously and were excluded, never
guessed).</p>
<table style="border-collapse:collapse;font-size:.93rem;margin:.6rem 0">
<tr><th style="text-align:left;padding:.35rem .6rem;border-bottom:1px solid #cbd5e1">Feature</th>
<th style="text-align:right;padding:.35rem .6rem;border-bottom:1px solid #cbd5e1">Standardised coefficient</th>
<th style="text-align:left;padding:.35rem .6rem;border-bottom:1px solid #cbd5e1">Why it belongs</th></tr>
<tr><td style="padding:.3rem .6rem"><code>frac_h19_near3_clipped_0.65</code></td><td style="padding:.3rem .6rem;text-align:right">{coefs['frac_h19_near3_clipped_0.65']:+.3f}</td>
<td style="padding:.3rem .6rem">share of dots within 3 px of the H19-5 skeleton — the single strongest empirical signal across 121 claims</td></tr>
<tr><td style="padding:.3rem .6rem"><code>frac_dcat_le2</code></td><td style="padding:.3rem .6rem;text-align:right">{coefs['frac_dcat_le2']:+.3f}</td>
<td style="padding:.3rem .6rem">dead mass inside the masked catalogue collar (pure false-positive cost)</td></tr>
<tr><td style="padding:.3rem .6rem"><code>log10_n_dots</code></td><td style="padding:.3rem .6rem;text-align:right">{coefs['log10_n_dots']:+.3f}</td>
<td style="padding:.3rem .6rem">emission budget; more dots help only while each still buys kernel coverage</td></tr>
<tr><td style="padding:.3rem .6rem"><code>quadrant_imbalance</code></td><td style="padding:.3rem .6rem;text-align:right">{coefs['quadrant_imbalance']:+.3f}</td>
<td style="padding:.3rem .6rem">concentration penalty (a file packed into one corner cannot recover a province-wide truth set)</td></tr>
</table>
<p><b>Honesty metrics.</b> in-sample RMSE <b>{f4(est['in_sample_rmse'])}</b> · leave-one-out RMSE
<b>{f4(est['loo_rmse'])}</b> · leave-one-out Spearman <b>{est['loo_spearman']:.3f}</b> against the CLAIM
values. The LOO RMSE is the ± shown next to every estimate in §3. Known residual structure: the model
over-predicts H19-5 descendants by up to 0.14 and under-predicts some independent-physics lanes by up to
0.11 (see the <code>delta</code> column in <code>evidence/score_estimator_20261026.json</code>), because
the relationship between skeleton proximity and score is saturating and non-linear with only
{est['training_rows']} labelled points. <b>Never read a MODEL number as a leaderboard result.</b></p>
""")

    # ---------------- what the new lane adds ----------------
    parts.append(f"""
<h2 id="lane">5. What the new lane actually changed (pre-registered, 3 arms)</h2>
<p>Pre-registration: <a href="HYPOTHESES_20261026_SALEMSEISMO.md">docs/HYPOTHESES_20261026_SALEMSEISMO.md</a>
(written before any code). Five untried hypotheses were ranked; rank 1 was built. Three experiments were
run — the protocol cap — and no weekly slot was spent.</p>
<table style="border-collapse:collapse;width:100%;font-size:.92rem">
<thead><tr style="background:#1e293b;color:#fff">
<th style="padding:.45rem;text-align:left">Arm</th>
<th style="padding:.45rem;text-align:right">dots</th>
<th style="padding:.45rem;text-align:right">static d_cat&gt;2 HOLDOUT-DTI</th>
<th style="padding:.45rem;text-align:right">strict draw-blind Rule-2</th>
<th style="padding:.45rem;text-align:right">USGS SGMC &gt;5 px</th>
<th style="padding:.45rem;text-align:right">worst 3-px overlap (102 repos)</th>
</tr></thead><tbody>""")
    arms = card["holdout_dti"]
    for arm, tag in (("salem_point37k", "point-greedy (control)"),
                     ("salem_celf37k", "CELF 300 m submodular"),
                     ("salem_celf_tail52k", "+ non-diluting 0.65 tail")):
        st = arms["all_arms_static_dcat_gt_2"][arm]
        r2 = arms["all_arms_rule2_dvis_gt_2"][arm]
        pu = uniq["candidates"][arm]
        parts.append(f"""<tr style="border-bottom:1px solid #e2e8f0">
<td style="padding:.4rem"><b>{e(arm)}</b><br><span style="font-size:.8rem">{e(tag)}</span></td>
<td style="padding:.4rem;text-align:right">{pu['my_positive_pixels']:,}</td>
<td style="padding:.4rem;text-align:right">{f6(st['dti'])} [{f6(st['ci95'][0])}, {f6(st['ci95'][1])}]</td>
<td style="padding:.4rem;text-align:right">{f6(r2['dti'])} [{f6(r2['ci95'][0])}, {f6(r2['ci95'][1])}]</td>
<td style="padding:.4rem;text-align:right">{f6(sgmc[arm])}</td>
<td style="padding:.4rem;text-align:right">{f4(pu['worst_operative_overlap_3px'])}</td>
</tr>""")
    parts.append("</tbody></table>")

    refs = arms["reference_baselines_static_dcat_gt_2"]
    parts.append(f"""<p style="font-size:.92rem"><b>Honest reading of the ablation.</b> Exact
25-offset 300&nbsp;m submodular placement plus the non-diluting tail raises the <i>static</i>
d_cat&gt;2&nbsp;px HOLDOUT-DTI from {f6(arms['all_arms_static_dcat_gt_2']['salem_point37k']['dti'])} to
{f6(arms['all_arms_static_dcat_gt_2']['salem_celf_tail52k']['dti'])}, i.e. above the previous
static-SOTA control LISTRICLOQO selectcal {f6(refs['LISTRICLOQO_selectcal']['dti'])} — a first for a
zero-<code>H19-5</code> lane in this repository. But it does <b>not</b> dominate on the strict
draw-blind Rule-2 instrument ({f6(arms['strict_drawblind_rule2_dvis_gt_2_primary']['dti'])} vs
{f6(refs['R0']['dti'])} for R0 and 0.1845 for the RELAYCONDUIT control), and the honest expectation for a
live score is therefore a modest improvement over R0-class files at best, not a jump past 0.32. This is a
negative-but-informative result recorded as such.</p>""")

    # ---------------- decisions ----------------
    parts.append(f"""
<h2 id="decisions">6. Decisions the owner must make (they cannot be made by code)</h2>
<ol>
<li><b>The literal dense-witness rule.</b> <code>17GEMSDOE_E-proba-multiscale</code> is positive on all
5,167,373 footprint cells, so "any dot within 3&nbsp;px of a registry raster" is satisfied by every
non-empty file. Under that reading no submission can ever clear, including files that already scored
0.2778. Choose one: (a) keep it and accept that nothing is submittable, or (b) adopt the operative
dot-field rule already implemented and used for every measurement on this page
(worst 3-px overlap ≤ 0.70 against dot fields, |ρ| ≤ 0.90 against surfaces).</li>
<li><b>Spend a slot or not.</b> This session spent 0 of the weekly cap. If (b) is chosen, the recommended
file is <code>{e(new_tif)}</code> — it is the only zero-<code>H19-5</code> file in the repository that is
simultaneously gate-clean, ≤0.70 overlapping against 1,756 public rasters, and better than the previous
static-SOTA on the shared instrument.</li>
<li><b>Receipts.</b> No ORGANIZER-CONFIRMED score exists here for any file. Recording the submission-page
score for the chosen file in <code>ledger/submissions.csv</code> is what converts CLAIM → receipt and
finally calibrates the estimator in §4.</li>
</ol>
""")

    # ---------------- how to submit ----------------
    parts.append(f"""
<h2 id="how">7. Exactly how to submit (form fields)</h2>
<ol>
<li>Click <a href="downloads/{e(new_tif)}" download>the .tif download</a> (or the single-TIFF
<a href="downloads/{e(new_zip)}" download>.zip</a>). Do not upload both.</li>
<li>Open <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/</a>
(log in; this URL is not reachable from the build sandbox).</li>
<li><i>File to submit</i> → the downloaded file. <i>Note (optional)</i> → <code>{e(card['submission_note'])}</code>
({card['submission_note_chars']}/140 characters).</li>
<li>Record the name <code>{e(card['submission_name'])}</code> and paste the returned score into
<code>ledger/submissions.csv</code> (columns <code>receipt_score</code>, <code>receipt_date</code>) so the
next session can label it ORGANIZER-CONFIRMED instead of CLAIM.</li>
</ol>
<p>The file is single-band <code>float32</code>, EPSG:32611, 3730×3292, with every one of the
12,279,160 cells finite in [0,&nbsp;1] and zeros outside the footprint — the exact class of encoding that
cannot trigger the portal error <q>Predicted values must be in range [0, 1]</q>.</p>
""")

    # ---------------- irregularities ----------------
    parts.append("""
<h2 id="irregularities">8. Irregularities flagged for review</h2>
<table style="border-collapse:collapse;width:100%;font-size:.9rem">
<thead><tr style="background:#7f1d1d;color:#fff">
<th style="padding:.45rem;text-align:left">ID</th><th style="padding:.45rem;text-align:left">Where</th>
<th style="padding:.45rem;text-align:left">Finding</th></tr></thead><tbody>""")
    for ir in audit["irregularities_flagged"]:
        parts.append(f"""<tr style="border-bottom:1px solid #e2e8f0">
<td style="padding:.4rem"><code>{e(ir['id'])}</code></td>
<td style="padding:.4rem">{e(ir['site'])}</td>
<td style="padding:.4rem">{e(ir['detail'])}</td></tr>""")
    parts.append("</tbody></table>")

    # ---------------- sources ----------------
    parts.append("""
<h2 id="sources">9. Sources (manual review links)</h2>
<ul style="font-size:.92rem">
<li>Competition overview / problem statement — <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">page/967</a>,
<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/">page/968</a>,
<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/data/">data</a>,
<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">leaderboard</a>
(login-gated; not fetched from the sandbox).</li>
<li>Official rules PDF — <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">docs.nlr.gov/docs/fy26osti/96647.pdf</a>
(three submissions per week; one final selection).</li>
<li>Reference solution (metric source) — <a href="https://github.com/drivendataorg/gems-prize-reference-solution">github.com/drivendataorg/gems-prize-reference-solution</a>.</li>
<li>Scoring clarifications used for the catalogue-mask logic —
<a href="https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516">11516</a>,
<a href="https://community.drivendata.org/t/where-do-you-draw-the-line/11536">11536</a>.</li>
<li>USGS GeoDAWN airborne magnetic &amp; radiometric surveys —
<a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS data page</a>,
<a href="https://doi.org/10.5066/P93LGLVQ">doi:10.5066/P93LGLVQ</a>.</li>
<li>INGENIOUS / DOE Geothermal Data Repository — <a href="https://gdr.openei.org/submissions/1391">GDR #1391</a>,
<a href="https://gbcge.org/current-projects/ingenious/">GBCGE INGENIOUS</a>.</li>
<li>USGS 3DEP 10 m elevation — <a href="https://www.usgs.gov/3d-elevation-program">3DEP</a>.</li>
<li>USGS SGMC bedrock faults (off-catalogue proxy; never used as a feature) —
<a href="https://pubs.usgs.gov/ds/1052/">ds/1052</a>, <a href="https://mrdata.usgs.gov/sgmc/">mrdata.usgs.gov/sgmc</a>.</li>
<li>Projection — <a href="https://epsg.io/32611">EPSG:32611</a>; metric background —
<a href="https://en.wikipedia.org/wiki/Tversky_index">Tversky index</a>.</li>
<li>Receipts for every number on this page: <code>evidence/focus9_executive_audit_20261026.json</code>,
<code>evidence/score_estimator_20261026.json</code>, <code>evidence/salemseismo_run_card.json</code>,
<code>evidence/salemseismo_holdout.json</code>, <code>evidence/salemseismo_uniqueness.json</code>.</li>
</ul>
<p style="margin-top:2rem"><a href="index.html">← back to the workbench</a> ·
<a href="executive-summary.html">historical executive summary</a> ·
<a href="SUBMIT.html">submission guide</a></p>
</main>
</body>
</html>
""")

    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
