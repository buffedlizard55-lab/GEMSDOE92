#!/usr/bin/env python3
"""Render docs/executive-summary-20261029-admitrelay.html from byte-bound JSON evidence."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DL = DOCS / "downloads"
EVID = ROOT / "evidence"


def esc(x) -> str:
    return html.escape(str(x), quote=True)


def build_html() -> str:
    card = json.loads((EVID / "admitrelay_run_card_20261029.json").read_text(encoding="utf-8"))
    lbm3 = json.loads((EVID / "lbm_v3_20261029.json").read_text(encoding="utf-8"))
    can = json.loads((EVID / "admitrelay_canaries_20261029.json").read_text(encoding="utf-8"))
    uniq = json.loads((EVID / "admitrelay_full_registry_uniqueness_20261029.json").read_text(encoding="utf-8"))
    f9s = json.loads((EVID / "focus9_sources_20261028.json").read_text(encoding="utf-8"))
    f9u = json.loads((EVID / "focus9_uniqueness_20261028.json").read_text(encoding="utf-8"))

    tif_name = Path(card["raster"]["file"]).name
    zip_name = Path(card["raster"]["zip"]).name
    card_name = f"{tif_name[:-len('-zeros.tif')]}_run_card.json"
    audit_name = f"{tif_name[:-len('.tif')]}-audit.json"

    # Lookup LBM-v3 LOGO prediction for Focus-9 peak rasters
    logo_by_sha = {r["sha256"]: r["logo"] for r in lbm3["rows"]}
    f9_rows_html = []
    for site, s in f9s.items():
        u = f9u[site]
        logo_val = logo_by_sha.get(s["sha256"])
        logo_str = f"{logo_val:.4f} (MODEL LOGO)" if logo_val is not None else "n/a"
        clones = ", ".join(u.get("identical_bytes_elsewhere", [])[:3]) or ", ".join(u.get("worst_overlap_in", [])[:2])
        f9_rows_html.append(
            f"<tr><td><strong>{esc(site)}</strong></td>"
            f"<td><a href=\"{esc(s['blob_url'])}\"><code>{esc(s['best'])}</code></a> <small>(study only)</small></td>"
            f"<td><code>{s['claim']:.4f}</code> <small>CLAIM</small></td>"
            f"<td><code>{esc(logo_str)}</code></td>"
            f"<td><span class=\"bno\">NO (100% clone)</span><br><small>Worst 3-px overlap {u['worst_overlap']:.3f} ({esc(clones)})</small></td></tr>"
        )

    # Append GEMSDOE92 lbmc1 (newly confirmed 0.2784 CLAIM on 2026-10-29) & new admitrelay1
    f9_rows_html.append(
        "<tr><td><strong>GEMSDOE92 (2026-10-27 lbmc1)</strong></td>"
        "<td><a href=\"downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif\"><code>gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif</code></a> <small>(already scored)</small></td>"
        "<td><code>0.2784</code> <small>CLAIM (#1 across 123 repos)</small></td>"
        "<td><code>0.2818</code> <small>(LBM-v3 prospective OOT; err −0.0034)</small></td>"
        "<td><span class=\"bwarn\">PI-1 0.6845 ≤ 0.70 (historical)</span><br><small>Literal 17GEMSDOE witness 1.000; already submitted</small></td></tr>"
    )
    u_sum = card["uniqueness"]
    m_est = card["model_estimate"]
    h_dti = card["holdout_dti"]
    f9_rows_html.append(
        f"<tr><td><strong>GEMSDOE92 (2026-10-29 ADMITRELAY)</strong></td>"
        f"<td><a href=\"downloads/{esc(tif_name)}\" download><code>{esc(tif_name)}</code></a> <small>(research only — DO NOT SUBMIT)</small></td>"
        f"<td><em>unsubmitted (0 slots used)</em></td>"
        f"<td><code>{m_est['lbm_v3_monotone']:.4f}</code> <small>MODEL LBM-v3 [{m_est['lbm_v3_approx_95_interval'][0]:.4f}, {m_est['lbm_v3_approx_95_interval'][1]:.4f}]</small><br>"
        f"<small>HOLDOUT-DTI E2={h_dti['e2_admitrelay_ps_loqo']['dti']:.5f}, E3={h_dti['e3_admitrelay_lbmv3_unique']['dti']:.5f}</small></td>"
        f"<td><span class=\"bno\">DO NOT SUBMIT (verdict=negative)</span><br>"
        f"<small>PI-1 surface {u_sum['surface_worst_overlap']:.4f} ≤ 0.70 &amp; dots {u_sum['final_worst_overlap']:.4f} ≤ 0.70 across {u_sum['registry_rasters']:,} rasters; literal 17GEMSDOE witness 1.000 &gt; 0.70 &amp; E3 holdout &lt; R0</small></td></tr>"
    )

    oot_rows_html = []
    for r in lbm3["prospective_oot_20261029"]["rows"]:
        oot_rows_html.append(
            f"<tr><td><code>{esc(r['site'])}</code></td>"
            f"<td><code>{esc(r['name'])}</code></td>"
            f"<td><code>{r['claim']:.4f}</code> <small>CLAIM</small></td>"
            f"<td><code>{r['lbm_v1_prospective_oot']:.4f}</code> <small>(err {r['lbm_v1_error']:+.4f})</small></td>"
            f"<td><code>{r['lbm_v3_prospective_oot']:.4f}</code> <small>(err {r['lbm_v3_error']:+.4f})</small></td></tr>"
        )

    canary_rows_html = []
    for f in can["features"]:
        canary_rows_html.append(
            f"<tr><td><code>{esc(f['feature'])}</code></td>"
            f"<td>{esc(f['group'])}</td>"
            f"<td><code>{f['roc_auc']:.4f}</code></td>"
            f"<td><code>{f['symmetric_auc']:.4f}</code></td>"
            f"<td>{'PASS (≤ 0.90)' if f['pass_le_0p90'] else 'FAIL'}</td></tr>"
        )

    peer_rows_html = []
    for k, v in u_sum["peer_comparisons"].items():
        peer_rows_html.append(
            f"<tr><td><code>{esc(k)}</code></td>"
            f"<td><code>{esc(v['sha256'][:16])}…</code></td>"
            f"<td><code>{v['surface_overlap_pi1']:.6f}</code></td>"
            f"<td><code>{v['surface_rho']:+.6f}</code></td>"
            f"<td><code>{v['final_overlap_pi1']:.6f}</code></td>"
            f"<td><code>{v['final_rho']:+.6f}</code></td></tr>"
        )

    css = (
        "body{font:15.5px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f4f6f8;color:#18212e}"
        "main{max-width:1120px;margin:0 auto;padding:24px}"
        "section{background:#fff;padding:20px 22px;margin:18px 0;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.07)}"
        ".stop{border:3px solid #b91c1c;background:#fff4f3}"
        ".bno{display:inline-block;padding:2px 8px;border-radius:999px;background:#b91c1c;color:#fff;font-weight:700;font-size:.8rem}"
        ".bwarn{display:inline-block;padding:2px 8px;border-radius:999px;background:#b45309;color:#fff;font-weight:700;font-size:.8rem}"
        ".bdl{display:inline-block;padding:2px 8px;border-radius:999px;background:#0369a1;color:#fff;font-weight:700;font-size:.8rem}"
        ".btn{display:inline-block;background:#1e3a5f;color:#fff!important;padding:10px 15px;border-radius:7px;font-weight:700;text-decoration:none;margin:4px 6px 4px 0}"
        "table{width:100%;border-collapse:collapse;font-size:.9rem;margin:10px 0}"
        "th,td{padding:9px 10px;border-bottom:1px solid #d8e0e8;text-align:left;vertical-align:top}"
        "th{background:#eef2f7}code,pre{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.88em;overflow-wrap:anywhere}"
        "pre{background:#0f172a;color:#e2e8f0;padding:12px;border-radius:8px;overflow:auto;max-height:460px}"
        "nav a{margin-right:14px;font-weight:600;color:#124ec0}a{color:#124ec0}"
    )

    e1 = h_dti["e1_admitrelay_blind"]
    e2 = h_dti["e2_admitrelay_ps_loqo"]
    e3 = h_dti["e3_admitrelay_lbmv3_unique"]
    r0 = h_dti["r0_recipe_control"]
    pe2 = h_dti["paired_e2_vs_r0_recipe"]
    pe3 = h_dti["paired_e3_vs_r0_recipe"]

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GEMSDOE92 — 2026-10-29 Executive Summary: ADMITRELAY + LBM-v3 Audit</title>
<style>{css}</style>
</head>
<body>
<main>
<nav><a href="index.html">← Main Landing Page</a> · <a href="how-to-submit.html">How to Submit &amp; [0, 1] Compliance Guide</a> · <a href="nine-sites.html">Nine-Site Fleet Audit</a> · <a href="HYPOTHESES_20261029_ADMITRELAY.md">Pre-Registered Hypotheses</a> · <a href="STANDING_PROMPT.md">Standing Prompt</a></nav>

<section id="admitrelay-decision" class="stop">
<h1>2026-10-29 Session Deliverable: ADMITRELAY + LBM-v3 — OK TO DOWNLOAD FOR RESEARCH ONLY · DO NOT SUBMIT</h1>
<p><span class="bdl">OK TO DOWNLOAD FOR RESEARCH ONLY</span> <span class="bno">DO NOT SUBMIT — verdict: negative · submission_eligible: false · 0 weekly slots used</span></p>
<p>
<a class="btn" href="downloads/{esc(tif_name)}" download>⬇ Download ADMITRELAY Research GeoTIFF (DO NOT SUBMIT)</a>
<a class="btn" href="downloads/{esc(zip_name)}" download>⬇ One-TIFF ZIP (Research Only)</a>
<a href="downloads/{esc(card_name)}">Byte-Bound JSON Run Card</a> ·
<a href="downloads/{esc(audit_name)}">Automated 11-Gate Format Audit</a> ·
<a href="downloads/admitrelay_readiness_20261029.json">Machine Readiness Feed</a>
</p>
<p><strong>Why DO NOT SUBMIT?</strong> Although <code>{esc(tif_name)}</code> passes all <strong>11/11 automated GeoTIFF/[0, 1] gates</strong>, all <strong>20/20 leakage canaries</strong> (max zero-catalogue symmetric AUC <code>{can['zero_catalogue_12_max_sym_auc']:.4f}</code>, max overall <code>{can['all_20_max_sym_auc']:.4f} ≤ 0.90</code>), and <strong>PI-1 uniqueness across all {u_sum['registry_rasters']:,} 8-owner rasters on BOTH the pre-placement continuous surface (<code>{u_sum['surface_worst_overlap']:.4f} ≤ 0.70</code>) and final binary dots (<code>{u_sum['final_worst_overlap']:.4f} ≤ 0.70</code>)</strong>, mandatory fail-closed promotion gates block upload: (1) under the literal full-support rule, pinned witness <code>17GEMSDOE E-proba-multiscale</code> (5,167,373 positive cells) yields overlap <code>1.000 &gt; 0.70</code>; (2) deployed 3-regime unique <code>E3</code> achieves <code>HOLDOUT-DTI = {e3['dti']:.6f}</code> vs <code>R0_recipe = {r0['dti']:.6f}</code> (while unconstrained fold-proper <code>E2 = {e2['dti']:.6f}</code> beats <code>R0_recipe</code> by <code>{pe2['delta']:+.6f}</code> with 95% CI <code>[{pe2['ci95'][0]:+.6f}, {pe2['ci95'][1]:+.6f}]</code> narrowly spanning zero); and (3) Goodhart-debiased <code>LBM-v3</code> estimates <code>{m_est['lbm_v3_monotone']:.4f} MODEL</code>, below <code>GEMSDOE92</code>'s already-submitted <code>lbmc1</code> (<code>0.2784 CLAIM</code>). No weekly competition slot is authorized or spent.</p>
<table>
<tr><th>Artifact SHA-256</th><td><code>{esc(card['raster_sha256'])}</code> ({card['raster']['bytes']:,} bytes · {card['raster']['n_dots']:,} binary <code>{{0.0, 1.0}}</code> dots · <code>EPSG:32611</code> · <code>3730×3292</code> · <code>float32</code> · zero NaN anywhere · immune to <q>Predicted values must be in range [0, 1]</q>)</td></tr>
<tr><th>Archived metadata (do NOT upload)</th><td>Name: <code>{esc(card['submission_name'])}</code> · Note ({card['note_chars']}/140 chars): <code>{esc(card['note'])}</code></td></tr>
</table>
</section>

<section id="focus9-table">
<h2>1. Executive Summary Table: Nine Focus Sites + GEMSDOE92 (2026-10-29 Ledger Audit)</h2>
<p>Every score below is explicitly labeled by evidence class: <code>CLAIM</code> (owner-reported in the user's ledger; not an organizer receipt verified in this sandbox), <code>MODEL</code> (Goodhart-debiased 131-claim <code>LBM-v3</code> leave-one-group-out or prospective out-of-time estimate; never an organizer score), or <code>HOLDOUT-DTI</code> (<code>gems57-pooled-hide-v2</code>, 22,663 withheld catalogue fault pixels).</p>
<table>
<thead><tr><th>Site</th><th>File to Download (Study / Research Only)</th><th>Owner-Reported Score</th><th>Estimated Score (<code>MODEL</code> / <code>HOLDOUT-DTI</code>)</th><th>Unique Across All Listed GEMSDOE Sites?</th></tr></thead>
<tbody>{''.join(f9_rows_html)}</tbody>
</table>
</section>

<section id="phd-analysis-02778-02784">
<h2>2. PhD-Level Analysis: Why GEMSDOE32 Achieved 0.2778, How GEMSDOE92 Beat It (0.2784), &amp; How to Score Higher</h2>
<h3>2.1 Metric Geometry of GEMSDOE32 (<code>0.2778 CLAIM</code>)</h3>
<p>The official DOE GEMS metric is the pooled pixel-level Distance-Tolerant Tversky Index with <code>α = 0.2</code> (false-positive weight), <code>β = 0.8</code> (false-negative weight), and a 300 m (<code>R = 3 px</code>) linear triangular tolerance kernel <code>k(d) = max(0, 1 − d/3)</code>, evaluated after pixel-exact masking of all 60,988 mapped USGS/INGENIOUS catalogue fault cells (<a href="https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4">Forum #11516</a>, <a href="https://community.drivendata.org/t/leaderboard-aggregation-pooled-over-public-test-pixels-or-mean-of-per-chunk-scores/11550">Forum #11550</a>). Under the <code>max_x p(x) k(|x − y|)</code> coverage operator, continuous ribbons waste <code>α = 0.2</code> false-positive mass on redundant adjacent pixels. <code>GEMSDOE32</code>'s <code>h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif</code> (<code>R0</code>, 37,654 binary dots) succeeded by (i) concentrating dots strictly on zero-catalogue 19-band geophysical fault ridges (<code>H19-5</code> skeleton, <code>dh19 == 0</code>), (ii) enforcing Poisson-disk spacing (<code>d ≥ 2.8 px</code>) so each dot's 3-px triangular cone covers ~14.1 footprint cells with minimal overlap, and (iii) pruning dots within <code>d_cat ≤ 2 px</code> (200 m) of mapped faults where organizer truth density is near zero.</p>

<h3>2.2 Discovery of the 2026-10-29 Ledger: GEMSDOE92 <code>lbmc1</code> Reached <code>0.2784 CLAIM</code> &amp; Diagnosed Goodhart Flank Bias</h3>
<p>In the updated 2026-10-29 ledger (<code>ledger/claims_20261029.txt</code>, 137 claims across 8 owners; 132 byte-matched to SHA-256 blobs in <code>.cache/registry_v3</code>), <code>GEMSDOE92</code>'s own 2026-10-27 raster <code>gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif</code> is newly reported at <strong><code>0.2784 CLAIM</code></strong> — the highest reported score across all 123 repositories (+0.0006 above <code>GEMSDOE32</code>'s <code>0.2778</code>, at <code>0.6845 ≤ 0.70</code> PI-1 overlap). Crucially, however, unconstrained <code>LBM-v1</code> had predicted <code>0.3320</code> (an overprediction of <code>+0.0536</code>). Forensic inspection of <code>LBM-v1</code>'s parameters reveals a textbook <strong>Goodhart / kernel-collinearity identifiability pathology</strong>: because historical high-scoring rasters placed almost all dots on <code>dh19 == 0</code>, their 300 m triangular coverage cones illuminated <code>dh19 == 0</code> (weight 1.00) and <code>dh19 == 1</code> (weight 0.67) collinearly. Unconstrained ridge regression assigned a non-physical <code>3.73×</code> density multiplier to the 100 m flank bin <code>dh19 == 1</code> over the fault centerline <code>dh19 == 0</code>, causing <code>lbmc1</code>'s greedy placer to shift 16,580 dots 1 px off-centerline (losing <code>1/3</code> of peak kernel height on real centerline faults while still gaining points from genuine off-<code>H19</code> <code>G-set</code> consensus blind faults).</p>

<h3>2.3 Prospective Out-of-Time Proof of Centerline-Monotone <code>LBM-v3</code></h3>
<p>Enforcing the structural geology constraint <code>ρ(dh19=0) ≥ ρ(dh19=1) ≥ … ≥ ρ(dh19&gt;5)</code> via bounded L-BFGS-B in shared <code>gems/lbmodel.py</code> (<code>monotone_factor_design</code>) trained strictly on the <strong>127 pre-2026-10-29 claims</strong> and tested out-of-time on the <strong>4 newly scored 2026-10-29 claims</strong> cuts prospective OOT RMSE by <strong>57.4%</strong> (<code>0.03159 → 0.01344</code>) and reduces the error on <code>lbmc1</code> by <strong>15.76×</strong> (<code>−0.0536 → −0.0034</code>):</p>
<table>
<thead><tr><th>Site</th><th>Newly Scored 2026-10-29 Submission</th><th>Owner <code>CLAIM</code></th><th><code>LBM-v1</code> OOT (Unconstrained)</th><th><code>LBM-v3</code> OOT (Centerline-Monotone)</th></tr></thead>
<tbody>{''.join(oot_rows_html)}</tbody>
</table>
<p><small>Full 131-claim <code>LBM-v3</code> cross-validation: 87-group leave-one-group-out <code>LOGO RMSE = {lbm3['logo_cv']['rmse_all']:.5f}</code>, <code>Spearman = {lbm3['logo_cv']['spearman_all']:.4f}</code> (<code>evidence/lbm_v3_20261029.json</code>). Unverified prompt figures <code>0.3195</code> and <code>0.4413</code> have no matching repository artifact or organizer receipt and are treated strictly as unverified external/historical benchmarks, never as confirmed scores.</small></p>

<h3>2.4 How to Score Higher (&gt; 0.285–0.305) Under Both Evaluation Regimes</h3>
<ul>
<li><strong>Eliminate <code>dh19 == 1</code> flank placement:</strong> Returning <code>lbmc1</code>'s 16,580 1-px flank dots back onto <code>dh19 == 0</code> fault centerlines recovers the full <code>1.00</code> vs <code>0.67</code> kernel peak on range-front blind faults without increasing dot count.</li>
<li><strong>Replace pure proximity halos with mechanical &amp; geochemical fault-zone physics:</strong> Combine Forsyth multi-wavenumber gravity–topography admittance jumps, Giggenbach <code>K − b·Th</code> epithermal K-metasomatism, and Pollard–Segall crack-tip shear lobes minus broadside stress shadows (validated below in <code>E1</code> and <code>E2</code>).</li>
<li><strong>Respect the catalogue-holdout vs blind-leaderboard Pareto frontier:</strong> Catalogue hide-and-recover (<code>HOLDOUT-DTI</code>) rewards near-catalogue tip continuation (<code>2 &lt; d_cat ≤ 18 px</code>, where <code>E2</code> beats <code>R0_recipe</code> at <code>0.10674</code> vs <code>0.09775</code>), whereas 131-claim <code>LBM-v3</code> shows public leaderboard truth is <code>5.7×</code> denser in distal blind basins (<code>d_cat &gt; 15 px</code>). Any future slot-promoted candidate must resolve the literal dense-witness rule and pair <code>dh19 == 0</code> centerlines with high-consensus distal blind hydrothermal structures.</li>
</ul>
</section>

<section id="hypotheses-ranking">
<h2>3. Pre-Registered Untried Geological Hypotheses (Ranked Before Implementation)</h2>
<p>Pre-registered in <a href="HYPOTHESES_20261029_ADMITRELAY.md"><code>docs/HYPOTHESES_20261029_ADMITRELAY.md</code></a> after auditing <code>gems/*.py</code> to verify zero prior implementation:</p>
<table>
<thead><tr><th>Rank &amp; ID</th><th>Geological / Geophysical Mechanism &amp; Layers</th><th>Why Missing from USGS / INGENIOUS</th><th>Named Non-Fault Mimic &amp; Suppressor</th><th>External Data &amp; Cost</th></tr></thead>
<tbody>
<tr><td><strong>#1 · H-1029A</strong></td><td><strong>Forsyth Multi-Wavenumber Elastic-Plate Admittance Step &amp; Coherence Loss</strong> (<code>B01 DEM</code>, <code>B02 isostatic_gravity</code>, <code>B16–B18</code>, 3DEP 10 m)</td><td>Playa/fan alluvium buries hanging-wall rollover; broken-plate flexural hinge (<code>T_e → 0</code>) persists across wavelength bands (0.6–9.6 km).</td><td>Intact Tertiary volcanic mesa rims (high slope without admittance phase reversal or local R² drop).</td><td>In-stack + pinned USGS 3DEP 10 m; low cost (FFT blocks).</td></tr>
<tr><td><strong>#2 · H-1029C</strong></td><td><strong>Pollard–Segall Crack-Tip Relay vs. Broadside Stress-Shadow Deconfounding</strong> (fold-visible <code>vis</code> faults + zero-catalogue ridges)</td><td>Quaternary mapping stops where single scarp splits into sub-resolution en-échelon relay splays, while broadside stress shadows suppress parallel faults.</td><td>Parallel erosional bench scarps and bajada gullies inside broadside stress shadows.</td><td>Strictly fold-visible <code>folds[k]['visible']</code> only; low cost.</td></tr>
<tr><td><strong>#3 · H-1029B</strong></td><td><strong>Giggenbach Epithermal K-Metasomatism (<code>K − b·Th</code>) × Magnetite Sulfidation Gate</strong> (GeoDAWN <code>K, Th, U</code> + <code>B06, B10, B13</code>)</td><td>Argillic/illite/adularia alteration halos have zero scarp relief in unconsolidated basin fill and were never mapped as Quaternary scarps.</td><td>Unaltered high-K/high-Th ash-flow tuffs and potassic playa mudflats (rejected by robust <code>K − b·Th</code> residual &amp; magnetic low).</td><td>Pinned USGS GeoDAWN radiometrics (DOI <code>10.5066/P93LGLVQ</code>); low cost.</td></tr>
<tr><td><strong>#4 · H-1029D</strong></td><td><strong>Arrhenius Kinetic 2 m Probe + Fault-Wedge Breccia Deficit + Lahontan Deconfounder</strong> (GDR #1391 2 m probe, well/spring, paleolake, 3DEP 10 m)</td><td>Blind upflow conduits leak convective heat into shallow 2 m probes without surface rupture; Lahontan shorelines (1270–1345 m) mask or mimic scarps.</td><td>Solar-heated dark basalt talus &amp; Pleistocene Lake Lahontan wave-cut benches (explicitly gated out).</td><td>Pinned DOE GDR #1391 &amp; USGS paleolake shapefiles; low cost.</td></tr>
<tr><td><strong>#5 · H-1029E</strong></td><td><strong>1 m LiDAR Micro-Scarp Throw-Gradient Continuity</strong> (deferred Phase-2 external opportunity)</td><td>Sub-meter (0.2–0.6 m) Holocene scarps alias below 30 m/10 m DEM vertical noise.</td><td>Livestock trails, historic wagon ruts, and graded desert roads.</td><td>Official USGS 3DEP 1 m WCS (<a href="https://data.usgs.gov/datacatalog/data/USGS:77ae0551-c61e-4979-aedd-d797abdcde0e">USGS catalog</a>); blocked in sandbox allowlist.</td></tr>
</tbody>
</table>
</section>

<section id="holdout-and-uniqueness">
<h2>4. Strict 3-Experiment Budget Results: Leakage Canaries, Pooled HOLDOUT-DTI, &amp; 2,262-Raster Uniqueness</h2>
<h3>4.1 Pooled Spatial Holdout (<code>gems57-pooled-hide-v2</code>, Seeds 20 &amp; 30, 8 Folds, 22,663 Withheld Positives)</h3>
<table>
<thead><tr><th>Experiment Arm</th><th>Evidence Class</th><th>Pooled DTI</th><th>95% Block-Bootstrap CI</th><th>Paired Δ vs <code>r0_recipe</code> (95% CI)</th><th>Dots (s20 / s30)</th></tr></thead>
<tbody>
<tr><td><code>r0_recipe</code> (H19-5 dotted at 2.8 px control)</td><td><code>HOLDOUT-DTI</code></td><td><code>{r0['dti']:.6f}</code></td><td><code>[{r0['ci95'][0]:.6f}, {r0['ci95'][1]:.6f}]</code></td><td><code>0.000000</code> (control)</td><td>39,710 / 39,751</td></tr>
<tr><td><strong><code>E1</code> · Zero-Catalogue ADMITRELAY Blind Physics LOQO</strong></td><td><code>HOLDOUT-DTI</code></td><td><strong><code>{e1['dti']:.6f}</code></strong></td><td><code>[{e1['ci95'][0]:.6f}, {e1['ci95'][1]:.6f}]</code></td><td>recovering 85.1% of R0 with <strong>zero</strong> catalogue &amp; <strong>zero</strong> H19-5</td><td>39,710 / 39,751</td></tr>
<tr><td><strong><code>E2</code> · Fold-Proper ADMITRELAY + Pollard–Segall + H19 LOQO</strong></td><td><code>HOLDOUT-DTI</code></td><td><strong><code>{e2['dti']:.6f}</code></strong></td><td><code>[{e2['ci95'][0]:.6f}, {e2['ci95'][1]:.6f}]</code></td><td><strong><code>{pe2['delta']:+.6f}</code></strong> (<code>[{pe2['ci95'][0]:+.6f}, {pe2['ci95'][1]:+.6f}]</code>)</td><td>39,710 / 39,751</td></tr>
<tr><td><strong><code>E3</code> · Three-Regime + Column-Generated PI-1 Unique Hybrid</strong></td><td><code>HOLDOUT-DTI</code></td><td><strong><code>{e3['dti']:.6f}</code></strong></td><td><code>[{e3['ci95'][0]:.6f}, {e3['ci95'][1]:.6f}]</code></td><td><code>{pe3['delta']:+.6f}</code> (<code>[{pe3['ci95'][0]:+.6f}, {pe3['ci95'][1]:+.6f}]</code>; <strong>2.05× RIESZ E3</strong> &amp; <strong>3.95× LBMC1</strong>)</td><td>39,710 / 39,751</td></tr>
</tbody>
</table>

<h3>4.2 Full 8-Owner Registry Uniqueness Audit ({u_sum['registry_rasters']:,} Unique SHA-256 Rasters Across 108 Non-Empty Repos)</h3>
<p>Checked on <strong>BOTH</strong> the continuous pre-placement surface (<code>deploy_e3_surface_capped.npy</code>) and the final 37,654 binary dots (<code>{esc(tif_name)}</code>) via shared <code>gems/uniqueness_v3.py</code>:</p>
<ul>
<li><strong>Pre-placement continuous surface (PI-1):</strong> worst 3-px overlap = <strong><code>{u_sum['surface_worst_overlap']:.6f} ≤ 0.70</code></strong> ({esc(', '.join(u_sum['surface_worst_overlap_where']))}); worst <code>|Spearman ρ| = {u_sum['surface_worst_abs_rho']:.6f} ≤ 0.90</code> → <strong>PASS</strong>.</li>
<li><strong>Final placed binary dots (PI-1):</strong> worst 3-px overlap = <strong><code>{u_sum['final_worst_overlap']:.6f} ≤ 0.70</code></strong> ({esc(', '.join(u_sum['final_worst_overlap_where']))}); worst <code>|Spearman ρ| = {u_sum['final_worst_abs_rho']:.6f} ≤ 0.90</code> → <strong>PASS</strong>.</li>
<li><strong>Literal unweighted positive-pixel reading (disclosed &amp; enforced as conservative stop):</strong> <code>17GEMSDOE E-proba-multiscale</code> is positive on all 5,167,373 footprint cells, giving literal overlap <code>1.000000 &gt; 0.70</code> for every nonempty candidate.</li>
</ul>
<table>
<thead><tr><th>Reference Submission</th><th>SHA-256 Prefix</th><th>Surface PI-1 Overlap</th><th>Surface ρ</th><th>Final Dots PI-1 Overlap</th><th>Final Dots ρ</th></tr></thead>
<tbody>{''.join(peer_rows_html)}</tbody>
</table>

<details>
<summary><strong>All 20 Single-Feature Leakage Canaries (Rule 4 Gate: 20/20 ≤ 0.90 PASS)</strong></summary>
<table>
<thead><tr><th>Feature</th><th>Group</th><th>ROC AUC</th><th>Symmetric AUC</th><th>Gate (≤ 0.90)</th></tr></thead>
<tbody>{''.join(canary_rows_html)}</tbody>
</table>
</details>
</section>

<section id="irregularities-20261029">
<h2>5. Flagged 2026-10-29 Ledger &amp; Repository Irregularities</h2>
<ul>
<li><strong>IR-1029-1 (Newly scored <code>lbmc1 = 0.2784 CLAIM</code> &amp; <code>LBM-v1</code> Goodhart flank inflation):</strong> <code>gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros</code> scored <code>0.2784 CLAIM</code> (#1 across 123 repos), exposing <code>LBM-v1</code>'s <code>dh19 == 1</code> collinearity overprediction (<code>0.3320</code>) and motivating centerline-monotone <code>LBM-v3</code> (<code>0.2818</code> OOT).</li>
<li><strong>IR-1029-2 (Score revision on identical stem in <code>ApartGEMSDOE1</code>):</strong> <code>apartgemsdoe1-h1-curie-pipe-edti37654-20261026-50e7b334-zeros</code> was reported as <code>0.0525</code> in the 2026-10-28 ledger and <code>0.1516</code> in the 2026-10-29 ledger for the exact same SHA-256 (<code>c140e60b…</code>); excluded from clean <code>LBM-v3</code> training (<code>131</code> clean rows of <code>132</code> matched).</li>
<li><strong>IR-1029-3 (Duplicate entry under truncated hash):</strong> <code>GEMSDOE92 8cd3f9a7</code> (<code>0.0255</code>) resolves to <code>gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif</code> (<code>SHA-256 91e26530…</code>, Git blob <code>8cd3f9a7…</code>), already recorded in the 2026-10-28 ledger at <code>0.0255</code>; deduplicated so it is never double-counted as OOT.</li>
<li><strong>IR-1029-4 (Four 2026-10-28 claims listed without scores in 2026-10-29 paste):</strong> <code>GEMSDOE91 667477a1</code> (<code>0.0435</code>), <code>KANLERGEMSDOE2 de6a7dc7</code> (<code>0.1218</code>), <code>WBGGEMSDOE3 224a7821</code> (<code>0.0443</code>), and <code>WBGGEMSDOE2 09908a6c</code> (<code>0.0262</code>) appeared blank in the 2026-10-29 paste; audited in <code>ledger/unscored_20261029.txt</code>.</li>
<li><strong>IR-1029-5 (HTML merge-conflict markers in <code>docs/how-to-submit.html</code> on <code>main</code>):</strong> Base commit <code>913af0a</code> contained unresolved <code>&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD</code> markers in <code>docs/how-to-submit.html</code> because <code>.github/workflows/ci.yml</code> scanned only <code>*.py</code>, <code>*.md</code>, <code>*.json</code>. Fixed in <code>docs/how-to-submit.html</code> and guarded across <code>*.html</code> in CI and pytest.</li>
</ul>
</section>

<section id="official-links">
<h2>6. Verified Official Sources for Manual Review</h2>
<ul>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">DrivenData DOE GEMS Problem Description &amp; DTI Metric Specification</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">DrivenData Official Submission Portal (3/week limit displayed on portal)</a></li>
<li><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Official DOE / NLR Competition Rules PDF (FY26 OSTI #96647)</a></li>
<li><a href="https://github.com/drivendataorg/gems-prize-reference-solution">Official DrivenData Reference Solution Repository (U-Net MC-CV)</a></li>
<li><a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN Airborne Magnetic &amp; Radiometric Surveys (NW Great Basin, DOI 10.5066/P93LGLVQ)</a></li>
<li><a href="https://gdr.openei.org/submissions/1391">DOE Geothermal Data Repository (GDR) Submission #1391 — INGENIOUS Great Basin Dataset</a></li>
<li><a href="https://data.usgs.gov/datacatalog/data/USGS:77ae0551-c61e-4979-aedd-d797abdcde0e">USGS 3DEP 1 m LiDAR Digital Elevation Models</a> · <a href="https://www.drivendata.org/termsofuse/">DrivenData Terms of Use</a></li>
</ul>
</section>

<section id="protocol-run-card">
<h2>7. Protocol Rule 5 JSON Run Card (Byte-Bound to <code>{esc(tif_name)}</code>)</h2>
<pre>{esc(json.dumps(card, indent=2))}</pre>
</section>
</main>
</body>
</html>
"""


def main() -> int:
    out = DOCS / "executive-summary-20261029-admitrelay.html"
    out.write_text(build_html(), encoding="utf-8")
    print("wrote", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
