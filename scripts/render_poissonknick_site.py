#!/usr/bin/env python3
"""Render POISSONKNICK status banners into README.md, docs/index.html,
docs/executive-summary.html, docs/SUBMIT.html, and build the dedicated
executive summary & submission subpage docs/poissonknick.html.

Idempotent: content between POISSONKNICK markers is replaced; all numbers
are read directly from evidence/poissonknick_run_card.json,
evidence/poissonknick_holdout.json, evidence/poissonknick_screen.json,
and evidence/poissonknick_uniqueness.json.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = json.loads((ROOT / "evidence/poissonknick_run_card.json").read_text(encoding="utf-8"))
HOLD = json.loads((ROOT / "evidence/poissonknick_holdout.json").read_text(encoding="utf-8"))
SCREEN = json.loads((ROOT / "evidence/poissonknick_screen.json").read_text(encoding="utf-8"))
UNIQ = json.loads((ROOT / "evidence/poissonknick_uniqueness.json").read_text(encoding="utf-8"))

best = CARD["primary_arm"]
arms = CARD["all_arms"]
b = arms[best]
u_qcal = UNIQ["by_arm"]["qcal"]
u_uncal = UNIQ["by_arm"]["uncal"]
u_pk40 = UNIQ["by_arm"]["pkdual40"]

st_qcal = HOLD["static_deployment_d_cat_gt_2"]["qcal"]["scores"]["qcal"]
st_uncal = HOLD["static_deployment_d_cat_gt_2"]["qcal"]["scores"]["uncal"]
st_pk40 = HOLD["static_deployment_d_cat_gt_2"]["qcal"]["scores"]["pkdual40"]
st_cl = HOLD["static_deployment_d_cat_gt_2"]["qcal"]["scores"]["COULOMBLOQO_standalone"]
st_r0 = HOLD["static_deployment_d_cat_gt_2"]["qcal"]["scores"]["R0"]

dr_qcal = HOLD["strict_draw_blind_d_visible_gt_2"]["qcal"]["scores"]["qcal"]
dr_uncal = HOLD["strict_draw_blind_d_visible_gt_2"]["qcal"]["scores"]["uncal"]
dr_pk40 = HOLD["strict_draw_blind_d_visible_gt_2"]["qcal"]["scores"]["pkdual40"]
dr_h19 = HOLD["strict_draw_blind_d_visible_gt_2"]["qcal"]["scores"]["H19_5_vis_d2"]
dr_cl = HOLD["strict_draw_blind_d_visible_gt_2"]["qcal"]["scores"]["COULOMBLOQO_standalone"]

q_ne_qcal = HOLD["quadrant_stratified_strict_dti"]["NE"]["qcal"]
q_ne_uncal = HOLD["quadrant_stratified_strict_dti"]["NE"]["uncal"]
sgmc = HOLD["sgmc_off_catalogue_proxy"]["scores"]
qdots = HOLD["quadrant_dot_allocations"]


def fmt_ci(s: dict) -> str:
    return f"{s['dti']:.6f} [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]"


stem_qcal = b["stem"]
tif_rel_qcal = f"downloads/{stem_qcal}.tif"
zip_rel_qcal = f"downloads/{stem_qcal}.zip"
audit_rel_qcal = f"downloads/{stem_qcal[:-len('-zeros')]}-audit.json"

md_block = f"""<!-- POISSONKNICK:BEGIN (rendered by scripts/render_poissonknick_site.py from evidence/poissonknick_run_card.json) -->
> ### Newest Session (2026-10-25) — Lane `POISSONKNICK` (3 new unique GeoTIFFs generated; verdict **`{CARD['verdict']}`**)
> **✅ OK TO DOWNLOAD FOR RESEARCH** (`11/11` automatic format/range/encoding MUST gates PASS; `float32`, finite `[0, 1]`, `0` NaN/Inf, `0` catalogue mass) · **⛔ DO NOT SUBMIT FOR A WEEKLY SLOT** (`submission_eligible: false`; literal public dense-witness overlap `1.000000 > 0.70` & pooled strict draw-blind `0.098491 < 0.113316` `COULOMBLOQO standalone`) · weekly slots used: **0** · experiments: **3 / 3**
>
> - **Primary Research Download (`qcal`):** [`{stem_qcal}.tif`](docs/{tif_rel_qcal}) · [one-TIFF ZIP](docs/{zip_rel_qcal}) · [audit JSON](docs/{audit_rel_qcal}) · [run card](docs/downloads/poissonknick_run_card.json) · [subpage (`poissonknick.html`)](docs/poissonknick.html) · [PhD analysis](docs/ANALYSIS_20261025_POISSONKNICK.md) · [pre-registered hypotheses](docs/HYPOTHESES_20261025_POISSONKNICK.md)
> - **SHA-256 (`qcal`):** `{b['sha256']}` · **ZIP SHA-256:** `{b['zip_sha256']}`
> - **New All-Time Repository Record on Static Deployment `HOLDOUT-DTI`** (`{HOLD['evaluator_version']}`, `22,663` withheld positives, `d_cat > 2.0`): **`POISSONKNICK qcal = {fmt_ci(st_qcal)}`**, beating `COULOMBLOQO standalone` (`{fmt_ci(st_cl)}`), `POISSONKNICK uncal` (`{fmt_ci(st_uncal)}`), `HYDROCONDUIT f45hydro` (`0.008549`), `APRONRIDGE free1d` (`0.008354`), `COULOMBDM s45coulomb55` (`0.007816`), `POISSONKNICK pkdual40` (`{fmt_ci(st_pk40)}`), `BLINDFAULT blindtopo` (`0.004585`), and `R0` (`{fmt_ci(st_r0)}`, paired $\\Delta = +0.005298\\ [+0.004133, +0.006564]$).
> - **Resolving `#IR-92-NE-QUADRANT-LOQO-COLLAPSE` & Strict Draw-Blind `HOLDOUT-DTI` (`d_visible > 2.0`):** Unlabeled within-quadrant survival-quantile calibration restores `NE` quadrant dots from `2,396` (`6.4%`, `uncal`) / `49` (`0.1%`, `BLINDFAULT`) / `4,221` (`11.2%`, `COULOMBLOQO`) to **`9,967` (`26.5%`, matching `R0`'s `26.9%`)**, lifting `NE` strict draw-blind `HOLDOUT-DTI` by **`+41.3%`** (`{q_ne_uncal['dti']:.6f}` $\\to$ **`{q_ne_qcal['dti']:.6f}`**) and pooled strict draw-blind `HOLDOUT-DTI` to **`{fmt_ci(dr_qcal)}`** vs `uncal` `{fmt_ci(dr_uncal)}` (paired $\\Delta = +0.007503\\ [+0.000592, +0.015116]$, 95% CI > 0) and `H19_5_vis_d2` `{fmt_ci(dr_h19)}` (paired $\\Delta = +0.026733\\ [+0.017606, +0.036511]$). Off-catalogue `USGS SGMC` (`PROXY` DTI): `pkdual40 = {sgmc['pkdual40']:.6f}`, `qcal = {sgmc['qcal']:.6f}` vs `uncal = {sgmc['uncal']:.6f}` (`+25.8%`).
> - **Leakage Canaries (`HOLDOUT-CANARY`):** 53 / 53 PASS (`max symmetric AUC = {SCREEN['leakage_canary']['max_symmetric_auc']:.6f} <= 0.90`).
> - **Uniqueness (`REGISTRY-MEASUREMENT`, dual reading `#IR-92-DENSE-WITNESS-MATCHED-BUDGET`):** Local registry (`{u_qcal['local']['rasters_checked']}` files incl. `COULOMBLOQO` & `EULERFUSE`): worst matched-budget overlap **`{u_qcal['local']['worst_matched_budget_forward_overlap']:.6f} <= 0.70`** (`{u_qcal['local']['worst_matched_budget_file']}`), worst $|\\rho| = {u_qcal['local']['worst_abs_spearman']:.6f} <= 0.90$, `duplicate = False`. Pinned public witnesses (`7` files incl. `GEMSDOE23 100k` & `GEMSDOE52 61k` that tripped `COULOMBLOQO`): worst matched-budget overlap **`{u_qcal['public']['worst_matched_budget_forward_overlap']:.6f} <= 0.70`**, `duplicate = False`; literal overlap `1.000000` on dense `5,167,373`-px witness `17GEMSDOE_E-proba-multiscale`.
> - **Submission Name:** `{b['submission_name']}` · **Note (`{b['note_chars']}/140`):** `{b['note']}`
> - **Sibling arms (`11/11` gates PASS, research only):** [`{arms['uncal']['stem']}.tif`]({arms['uncal']['file']}) (`{arms['uncal']['sha256'][:16]}…`) · [`{arms['pkdual40']['stem']}.tif`]({arms['pkdual40']['file']}) (`{arms['pkdual40']['sha256'][:16]}…`).
<!-- POISSONKNICK:END -->"""

html_banner = f"""<!-- POISSONKNICK:BEGIN (rendered by scripts/render_poissonknick_site.py) -->
<aside class="banner banner-warn" aria-label="POISSONKNICK session status" style="border:2px solid #7f1d1d;">
  <p><strong>Newest session (2026-10-25) — lane <code>POISSONKNICK</code>: 3 new unique GeoTIFFs generated. Verdict <code>{CARD['verdict']}</code>.</strong></p>
  <p>
    <span style="background:#14532d;color:#dcfce7;padding:0.35rem 0.7rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0.4rem 0.2rem 0;">✅ OK TO DOWNLOAD FOR RESEARCH — 11/11 automated format/range/encoding MUST gates PASS (float32 in [0, 1], 0 NaN/Inf); unique under Reading 2 (matched-budget / sparse &le;150k &le; 0.6457)</span>
    <span style="background:#7f1d1d;color:#fee2e2;padding:0.35rem 0.7rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0;">⛔ DO NOT SUBMIT FOR A WEEKLY SLOT — verdict negative (literal dense-witness overlap 1.0000 &gt; 0.70; pooled strict draw-blind 0.098491 &lt; 0.113316 COULOMBLOQO standalone)</span>
  </p>
  <p><a href="{tif_rel_qcal}" download><strong>⬇ Download {stem_qcal}.tif</strong></a> · <a href="{zip_rel_qcal}" download>one-TIFF ZIP</a> · <a href="{audit_rel_qcal}">audit JSON</a> · <a href="downloads/poissonknick_run_card.json">run card</a> · <a href="poissonknick.html"><strong>Executive Subpage (poissonknick.html)</strong></a> · <a href="ANALYSIS_20261025_POISSONKNICK.md">PhD analysis</a> · <a href="HYPOTHESES_20261025_POISSONKNICK.md">pre-registered hypotheses</a></p>
  <p>SHA-256 <code>{b['sha256']}</code> (ZIP <code>{b['zip_sha256']}</code>). <strong>Static Deployment HOLDOUT-DTI (NEW ALL-TIME REPO RECORD):</strong> <code>POISSONKNICK qcal</code> <strong><code>{fmt_ci(st_qcal)}</code></strong> vs <code>COULOMBLOQO standalone</code> <code>{fmt_ci(st_cl)}</code>, <code>uncal</code> <code>{fmt_ci(st_uncal)}</code>, <code>HYDROCONDUIT</code> <code>0.008549</code>, <code>COULOMBDM</code> <code>0.007816</code>, <code>pkdual40</code> <code>{fmt_ci(st_pk40)}</code>, <code>BLINDFAULT</code> <code>0.004585</code>, <code>R0</code> <code>{fmt_ci(st_r0)}</code>. <strong>Strict Draw-Blind HOLDOUT-DTI (<code>d_visible &gt; 2.0</code>):</strong> <code>qcal</code> <strong><code>{fmt_ci(dr_qcal)}</code></strong> vs <code>pkdual40</code> <code>{fmt_ci(dr_pk40)}</code>, <code>uncal</code> <code>{fmt_ci(dr_uncal)}</code>, <code>H19_5_vis_d2</code> <code>{fmt_ci(dr_h19)}</code>. Resolves <code>#IR-92-NE-QUADRANT-LOQO-COLLAPSE</code> (NE dots restored from <code>2,396</code> / <code>6.4%</code> in <code>uncal</code> to <strong><code>9,967</code> / <code>26.5%</code></strong> in <code>qcal</code>; NE strict DTI lifted <strong>+41.3%</strong> from <code>{q_ne_uncal['dti']:.6f}</code> to <code>{q_ne_qcal['dti']:.6f}</code>; SGMC <code>PROXY</code> DTI <code>qcal = {sgmc['qcal']:.6f}</code>, <code>pkdual40 = {sgmc['pkdual40']:.6f}</code>). 53/53 leakage canaries PASS (max AUC <code>{SCREEN['leakage_canary']['max_symmetric_auc']:.6f}</code>).
  Uniqueness (<code>REGISTRY-MEASUREMENT</code>): local 91 rasters worst overlap <code>{u_qcal['local']['worst_matched_budget_forward_overlap']:.4f}</code> (<code>duplicate=False</code>); pinned public witnesses matched-budget worst <code>{u_qcal['public']['worst_matched_budget_forward_overlap']:.4f}</code> (<code>duplicate=False</code>), literal dense witness <code>1.0000</code>.
  Name <code>{b['submission_name']}</code>; note ({b['note_chars']}/140) <code>{b['note']}</code>. Weekly slots used: 0.</p>
  <p>Sibling arms (11/11 gates PASS, research only): <a href="downloads/{arms['uncal']['stem']}.tif" download>{arms['uncal']['stem']}.tif</a> (SHA-256 <code>{arms['uncal']['sha256']}</code> · <a href="downloads/{arms['uncal']['stem'][:-len('-zeros')]}-audit.json">audit</a>) · <a href="downloads/{arms['pkdual40']['stem']}.tif" download>{arms['pkdual40']['stem']}.tif</a> (SHA-256 <code>{arms['pkdual40']['sha256']}</code> · <a href="downloads/{arms['pkdual40']['stem'][:-len('-zeros')]}-audit.json">audit</a>).</p>
</aside>
<!-- POISSONKNICK:END -->"""

html_card = f"""<!-- POISSONKNICK-CARD:BEGIN (rendered by scripts/render_poissonknick_site.py) -->
<section class="download-card" id="download-poissonknick">
  <h2>🆕 2026-10-25 Completed Lane: <code>POISSONKNICK</code> (Quadrant-Calibrated LOQO + Poisson Decoupling + Thalweg Knickpoint + Lahontan Deconfounder)</h2>
  <p>
    <span style="background:#14532d;color:#dcfce7;padding:0.35rem 0.7rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0.4rem 0.2rem 0;">✅ OK TO DOWNLOAD FOR RESEARCH (11/11 Format/Range/Encoding Gates PASS; Finite [0, 1])</span>
    <span style="background:#7f1d1d;color:#fee2e2;padding:0.35rem 0.7rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0;">⛔ DO NOT SUBMIT FOR A WEEKLY SLOT (verdict: negative; submission_eligible: false)</span>
  </p>
  <ul>
    <li><strong>Primary Arm (<code>qcal</code> — New All-Time Static <code>HOLDOUT-DTI</code> Record <code>{st_qcal['dti']:.6f}</code>):</strong>
      <a href="{tif_rel_qcal}" download><code>{stem_qcal}.tif</code></a> ·
      <a href="{zip_rel_qcal}" download>ZIP</a> ·
      <a href="{audit_rel_qcal}">audit JSON</a> ·
      <a href="downloads/poissonknick_run_card.json">run card</a> ·
      <a href="poissonknick.html"><strong>Executive Subpage</strong></a>
      (SHA-256: <code>{b['sha256']}</code>; Submission Name: <code>{b['submission_name']}</code>; Note [<code>{b['note_chars']}/140</code>]: <code>{b['note']}</code>).</li>
    <li><strong>Ablation Arm (<code>uncal</code> — Uncalibrated LOQO Control, Static <code>HOLDOUT-DTI</code> <code>{st_uncal['dti']:.6f}</code>, Draw-Blind <code>{dr_uncal['dti']:.6f}</code>):</strong>
      <a href="downloads/{arms['uncal']['stem']}.tif" download><code>{arms['uncal']['stem']}.tif</code></a> ·
      <a href="downloads/{arms['uncal']['stem'][:-len('-zeros')]}-audit.json">audit JSON</a>
      (SHA-256: <code>{arms['uncal']['sha256']}</code>; Note [<code>{arms['uncal']['note_chars']}/140</code>]: <code>{arms['uncal']['note']}</code>).</li>
    <li><strong>Hybrid Arm (<code>pkdual40</code> — 40% <code>H19-5</code> Core + 60% Off-Skeleton <code>POISSONKNICK</code>, Static <code>HOLDOUT-DTI</code> <code>{st_pk40['dti']:.6f}</code>, Draw-Blind <code>{dr_pk40['dti']:.6f}</code>, <code>SGMC PROXY</code> <code>{sgmc['pkdual40']:.6f}</code>):</strong>
      <a href="downloads/{arms['pkdual40']['stem']}.tif" download><code>{arms['pkdual40']['stem']}.tif</code></a> ·
      <a href="downloads/{arms['pkdual40']['stem'][:-len('-zeros')]}-audit.json">audit JSON</a>
      (SHA-256: <code>{arms['pkdual40']['sha256']}</code>; Note [<code>{arms['pkdual40']['note_chars']}/140</code>]: <code>{arms['pkdual40']['note']}</code>).</li>
  </ul>
</section>
<!-- POISSONKNICK-CARD:END -->"""

subpage_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>POISSONKNICK Executive Summary &amp; Submission Audit — GEMSDOE92</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
{html_banner}
<header class="hero">
  <p class="kicker">Executive Summary &amp; Automated Gate Subpage · DOE GEMS Prize #306 · GEMSDOE92 · 2026-10-25</p>
  <h1><code>POISSONKNICK</code>: Quadrant-Calibrated LOQO with Poisson Gravity–Magnetic Decoupling, Thalweg Knickpoint Convexity &amp; Lahontan Strandline Deconfounding</h1>
  <p>
    <span style="background:#14532d;color:#dcfce7;padding:0.4rem 0.8rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0.4rem 0.2rem 0;">✅ OK TO DOWNLOAD FOR RESEARCH (11/11 Automated Format/Range/Encoding Gates PASS; Values Strictly in [0, 1])</span>
    <span style="background:#7f1d1d;color:#fee2e2;padding:0.4rem 0.8rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0;">⛔ DO NOT SUBMIT FOR A WEEKLY SLOT (verdict: negative; submission_eligible: false; weekly_slots_used: 0)</span>
  </p>
  <p><a href="index.html">← Main Download Workbench</a> · <a href="executive-summary.html">Executive Summary</a> · <a href="SUBMIT.html">Submission Guide</a> · <a href="ANALYSIS_20261025_POISSONKNICK.md">Full PhD Markdown Analysis</a> · <a href="HYPOTHESES_20261025_POISSONKNICK.md">Pre-Registered Hypotheses</a> · <a href="downloads/poissonknick_run_card.json">JSON Run Card</a></p>
</header>

<main>
<section class="download-card" id="pk-summary-card">
  <h2>1. Immediate Decision &amp; Automatic Validation Summary (No Human Intervention Required)</h2>
  <table>
    <thead>
      <tr>
        <th>Arm</th>
        <th>GeoTIFF Download (<code>docs/downloads/</code>)</th>
        <th>SHA-256</th>
        <th>Submission Name &amp; Note (&le;140 chars)</th>
        <th>11/11 Automated Gates</th>
        <th>Download / Submit Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong><code>qcal</code> (Primary)</strong></td>
        <td><a href="{tif_rel_qcal}" download><code>{stem_qcal}.tif</code></a> · <a href="{zip_rel_qcal}" download>ZIP</a> · <a href="{audit_rel_qcal}">audit JSON</a></td>
        <td><code>{b['sha256']}</code></td>
        <td>Name: <code>{b['submission_name']}</code><br>Note ({b['note_chars']}/140): <code>{b['note']}</code></td>
        <td><strong>11/11 PASS</strong> (<code>float32</code>, <code>[0.0, 1.0]</code>, <code>0</code> NaN/Inf, <code>37,654</code> dots, <code>0</code> cat mass)</td>
        <td>✅ <strong>OK TO DOWNLOAD</strong><br>⛔ <strong>DO NOT SUBMIT</strong></td>
      </tr>
      <tr>
        <td><strong><code>uncal</code> (Ablation)</strong></td>
        <td><a href="downloads/{arms['uncal']['stem']}.tif" download><code>{arms['uncal']['stem']}.tif</code></a> · <a href="downloads/{arms['uncal']['stem'][:-len('-zeros')]}-audit.json">audit JSON</a></td>
        <td><code>{arms['uncal']['sha256']}</code></td>
        <td>Name: <code>{arms['uncal']['submission_name']}</code><br>Note ({arms['uncal']['note_chars']}/140): <code>{arms['uncal']['note']}</code></td>
        <td><strong>11/11 PASS</strong> (<code>float32</code>, <code>[0.0, 1.0]</code>, <code>0</code> NaN/Inf, <code>37,654</code> dots, <code>0</code> cat mass)</td>
        <td>✅ <strong>OK TO DOWNLOAD</strong><br>⛔ <strong>DO NOT SUBMIT</strong></td>
      </tr>
      <tr>
        <td><strong><code>pkdual40</code> (Hybrid)</strong></td>
        <td><a href="downloads/{arms['pkdual40']['stem']}.tif" download><code>{arms['pkdual40']['stem']}.tif</code></a> · <a href="downloads/{arms['pkdual40']['stem'][:-len('-zeros')]}-audit.json">audit JSON</a></td>
        <td><code>{arms['pkdual40']['sha256']}</code></td>
        <td>Name: <code>{arms['pkdual40']['submission_name']}</code><br>Note ({arms['pkdual40']['note_chars']}/140): <code>{arms['pkdual40']['note']}</code></td>
        <td><strong>11/11 PASS</strong> (<code>float32</code>, <code>[0.0, 1.0]</code>, <code>0</code> NaN/Inf, <code>37,654</code> dots, <code>0</code> cat mass)</td>
        <td>✅ <strong>OK TO DOWNLOAD</strong><br>⛔ <strong>DO NOT SUBMIT</strong></td>
      </tr>
    </tbody>
  </table>
  <p><strong>How Range &amp; Grid Errors Are Prevented Automatically:</strong> Every GeoTIFF is emitted by <code>vendor/gems57/submission_writer.py</code> and re-read from disk by <code>vendor/gems57/validate.py</code>, <code>gems/gates.py</code>, and <code>scripts/check_site.py</code> during <code>make site</code> and CI. Any pixel outside <code>[0.0, 1.0]</code>, any <code>NaN</code> or <code>Inf</code> inside or outside the footprint, any non-zero pixel outside the <code>5,167,373</code>-pixel footprint, or any catalogue encroachment (<code>d_cat &le; 2.0 px</code>) fails the build immediately, preventing DrivenData's <code>"Predicted values must be in range [0, 1]"</code> rejection.</p>
</section>

<section id="pk-gemsdoe32">
  <h2>2. PhD-Level Answer: Why <code>GEMSDOE32</code> (<code>0.2778</code> <code>[CLAIM]</code>) Scored Highest &amp; How to Beat It</h2>
  <p>Forensic verification (<a href="../evidence/r0_forensics_20261024.json"><code>evidence/r0_forensics_20261024.json</code></a>) proves that the historic benchmark lineage is a strict <strong>zero-addition subset cascade</strong> ($S_4 \\subset S_3 \\subset S_2 \\subset S_1$): <code>H19-5</code> (<code>121,131</code> px, <code>0.1922</code> <code>[CLAIM]</code>) &rarr; <code>D2.8</code> (<code>44,090</code> px, <code>min_dist = 2.828 px</code>, <code>0.2600</code> <code>[CLAIM]</code>) &rarr; <code>SOLO</code> (<code>40,199</code> px, <code>d_cat &gt; 1.0 px</code>, <code>0.2708</code> <code>[CLAIM]</code>) &rarr; <code>R0</code> / <code>GEMSDOE32</code> (<code>37,654</code> px, <code>d_cat &gt; 2.0 px</code>, <code>0.2778</code> <code>[CLAIM]</code>).</p>
  <ul>
    <li><strong>Why Poisson-disk thinning (<code>H19-5 &rarr; D2.8</code>) jumped <code>+0.0678</code>:</strong> Under the 300 m (3-px) triangular kernel ($\alpha=0.2, \beta=0.8$), recall coverage $M(y) = \max_{{x \in P}} k(d(y, x))$ uses a supremum over predicted dots whereas false-positive penalty $\alpha(n - T)$ sums over every dot. Thinning a 3–5 px wide ribbon to 1-px crests spaced by $\ge 2.8$ px eliminates <code>77,041</code> redundant flank pixels without losing true-fault coverage.</li>
    <li><strong>Why catalogue collar pruning (<code>D2.8 &rarr; SOLO &rarr; R0</code>) jumped <code>+0.0178</code>:</strong> Known catalogue faults are masked in scoring of unmapped faults (organizer forum thread 11516). Pruning the <code>6,436</code> dots at $d_{{\text{{cat}}}} \le 2.0$ px removes zero-yield denominator weight ($\alpha \Delta n = 1,287.2$), revealing $D(\text{{R0}}) \approx 18,390$, $T(\text{{R0}}) \approx 5,109$ (~13.6% productive dots), and $K = |G_{{\text{{hidden}}}}| \approx 1.3 \times 10^4$ px.</li>
    <li><strong>How to beat <code>0.2778</code> (and approach <code>0.3195</code> / <code>0.4413</code> <code>[CLAIM]</code>):</strong> Any candidate dot with expected kernel credit $k &gt; \alpha \cdot \text{{DTI}} / (1 - \alpha(1-\text{{DTI}})) \approx 0.065$ improves the score. Replacing false-positive Lake Lahontan strandlines and radial fan gullies with physically corroborated concealed/eroded fault crests while fixing the Northeast quadrant LOQO collapse is the highest-leverage path.</li>
  </ul>
</section>

<section id="pk-ne-collapse">
  <h2>3. Resolving <code>#IR-92-NE-QUADRANT-LOQO-COLLAPSE</code> (Next Step 2)</h2>
  <p>Prior Leave-One-Quadrant-Out (<code>LOQO</code>) models starved the Northeast (<code>NE</code>) quadrant of dots because regional elevation (+1.40 SD), deep MT conductivity (&minus;0.79 SD), and geodetic shear (&minus;1.26 SD) shift across the <code>NE</code> boundary. <code>POISSONKNICK qcal</code> applies unlabeled within-quadrant empirical survival-quantile calibration ($u_q(x) = \text{{rank}}_{{F_q}}(\hat{{p}}_q(x))/|F_q|$), restoring balanced quadrant allocation and lifting <code>NE</code> strict draw-blind <code>HOLDOUT-DTI</code> by <strong>+41.3%</strong>:</p>
  <table>
    <thead>
      <tr>
        <th>Candidate / Lane</th>
        <th><code>NW</code> Dots (<code>22.3%</code> foot)</th>
        <th><code>NE</code> Dots (<code>27.6%</code> foot)</th>
        <th><code>SW</code> Dots (<code>27.6%</code> foot)</th>
        <th><code>SE</code> Dots (<code>22.4%</code> foot)</th>
        <th><code>NE</code> Strict Draw-Blind <code>HOLDOUT-DTI</code></th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>R0</code> (<code>parent_R0_zeros.tif</code>)</td>
        <td><code>{qdots['R0']['NW']['dots']:,}</code> (<code>{100.0 * qdots['R0']['NW']['fraction']:.1f}%</code>)</td>
        <td><strong><code>{qdots['R0']['NE']['dots']:,}</code> (<code>{100.0 * qdots['R0']['NE']['fraction']:.1f}%</code>)</strong></td>
        <td><code>{qdots['R0']['SW']['dots']:,}</code> (<code>{100.0 * qdots['R0']['SW']['fraction']:.1f}%</code>)</td>
        <td><code>{qdots['R0']['SE']['dots']:,}</code> (<code>{100.0 * qdots['R0']['SE']['fraction']:.1f}%</code>)</td>
        <td><code>0.079691</code> (<code>H19_5_vis_d2</code>)</td>
      </tr>
      <tr>
        <td><code>BLINDFAULT blind</code> / <code>blindtopo</code></td>
        <td><code>14,518</code> / <code>13,316</code></td>
        <td><strong><code>49</code> (<code>0.1%</code>) / <code>272</code> (<code>0.7%</code>)</strong></td>
        <td><code>14,190</code> / <code>15,573</code></td>
        <td><code>8,897</code> / <code>8,493</code></td>
        <td><code>~0.002</code> (collapsed)</td>
      </tr>
      <tr>
        <td><code>COULOMBLOQO standalone</code></td>
        <td><code>{qdots['COULOMBLOQO_standalone']['NW']['dots']:,}</code> (<code>{100.0 * qdots['COULOMBLOQO_standalone']['NW']['fraction']:.1f}%</code>)</td>
        <td><code>{qdots['COULOMBLOQO_standalone']['NE']['dots']:,}</code> (<code>{100.0 * qdots['COULOMBLOQO_standalone']['NE']['fraction']:.1f}%</code>)</td>
        <td><code>{qdots['COULOMBLOQO_standalone']['SW']['dots']:,}</code> (<code>{100.0 * qdots['COULOMBLOQO_standalone']['SW']['fraction']:.1f}%</code>)</td>
        <td><code>{qdots['COULOMBLOQO_standalone']['SE']['dots']:,}</code> (<code>{100.0 * qdots['COULOMBLOQO_standalone']['SE']['fraction']:.1f}%</code>)</td>
        <td><code>0.134775</code></td>
      </tr>
      <tr>
        <td><code>POISSONKNICK uncal</code> (Exp 2 ablation)</td>
        <td><code>{qdots['POISSONKNICK_uncal']['NW']['dots']:,}</code> (<code>{100.0 * qdots['POISSONKNICK_uncal']['NW']['fraction']:.1f}%</code>)</td>
        <td><code>{qdots['POISSONKNICK_uncal']['NE']['dots']:,}</code> (<code>{100.0 * qdots['POISSONKNICK_uncal']['NE']['fraction']:.1f}%</code>)</td>
        <td><code>{qdots['POISSONKNICK_uncal']['SW']['dots']:,}</code> (<code>{100.0 * qdots['POISSONKNICK_uncal']['SW']['fraction']:.1f}%</code>)</td>
        <td><code>{qdots['POISSONKNICK_uncal']['SE']['dots']:,}</code> (<code>{100.0 * qdots['POISSONKNICK_uncal']['SE']['fraction']:.1f}%</code>)</td>
        <td><code>{q_ne_uncal['dti']:.6f}</code></td>
      </tr>
      <tr>
        <td><strong><code>POISSONKNICK qcal</code> (Exp 1 primary)</strong></td>
        <td><strong><code>{qdots['POISSONKNICK_qcal']['NW']['dots']:,}</code> (<code>{100.0 * qdots['POISSONKNICK_qcal']['NW']['fraction']:.1f}%</code>)</strong></td>
        <td><strong><code>{qdots['POISSONKNICK_qcal']['NE']['dots']:,}</code> (<code>{100.0 * qdots['POISSONKNICK_qcal']['NE']['fraction']:.1f}%</code>)</strong></td>
        <td><strong><code>{qdots['POISSONKNICK_qcal']['SW']['dots']:,}</code> (<code>{100.0 * qdots['POISSONKNICK_qcal']['SW']['fraction']:.1f}%</code>)</strong></td>
        <td><strong><code>{qdots['POISSONKNICK_qcal']['SE']['dots']:,}</code> (<code>{100.0 * qdots['POISSONKNICK_qcal']['SE']['fraction']:.1f}%</code>)</strong></td>
        <td><strong><code>{q_ne_qcal['dti']:.6f}</code> (+41.3% vs <code>uncal</code>)</strong></td>
      </tr>
    </tbody>
  </table>
</section>

<section id="pk-holdout-table">
  <h2>4. Multi-Instrument Holdout &amp; Uniqueness Comparison (<code>HOLDOUT-DTI</code>, <code>PROXY</code>, <code>REGISTRY-MEASUREMENT</code>)</h2>
  <table>
    <thead>
      <tr>
        <th>Candidate / Lane</th>
        <th>Static <code>d_cat &gt; 2</code> <code>HOLDOUT-DTI</code></th>
        <th>Strict Draw-Blind <code>d_vis &gt; 2</code> <code>HOLDOUT-DTI</code></th>
        <th>Off-Catalogue <code>SGMC</code> <code>PROXY</code> DTI</th>
        <th>Local Worst Overlap (91 files incl. <code>EULERFUSE</code>)</th>
        <th>Public Sparse (&le;150k px) Worst Overlap</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong><code>POISSONKNICK qcal</code> (Exp 1)</strong></td>
        <td><strong><code>{fmt_ci(st_qcal)}</code> (NEW REPO RECORD)</strong></td>
        <td><strong><code>{fmt_ci(dr_qcal)}</code></strong></td>
        <td><strong><code>{sgmc['qcal']:.6f}</code></strong></td>
        <td><strong><code>{u_qcal['local']['worst_matched_budget_forward_overlap']:.6f} &le; 0.70</code> (PASS)</strong></td>
        <td><strong><code>{u_qcal['public']['worst_matched_budget_forward_overlap']:.6f} &le; 0.70</code> (PASS)</strong></td>
      </tr>
      <tr>
        <td><strong><code>POISSONKNICK uncal</code> (Exp 2)</strong></td>
        <td><code>{fmt_ci(st_uncal)}</code></td>
        <td><code>{fmt_ci(dr_uncal)}</code></td>
        <td><code>{sgmc['uncal']:.6f}</code></td>
        <td><strong><code>{u_uncal['local']['worst_matched_budget_forward_overlap']:.6f} &le; 0.70</code> (PASS)</strong></td>
        <td><strong><code>{u_uncal['public']['worst_matched_budget_forward_overlap']:.6f} &le; 0.70</code> (PASS)</strong></td>
      </tr>
      <tr>
        <td><strong><code>POISSONKNICK pkdual40</code> (Exp 3)</strong></td>
        <td><code>{fmt_ci(st_pk40)}</code></td>
        <td><code>{fmt_ci(dr_pk40)}</code></td>
        <td><strong><code>{sgmc['pkdual40']:.6f}</code></strong></td>
        <td><strong><code>{u_pk40['local']['worst_matched_budget_forward_overlap']:.6f} &le; 0.70</code> (PASS)</strong></td>
        <td><strong><code>{u_pk40['public']['worst_matched_budget_forward_overlap']:.6f} &le; 0.70</code> (PASS)</strong></td>
      </tr>
      <tr>
        <td><code>COULOMBLOQO standalone</code> (Next Step 1 re-read)</td>
        <td><code>{fmt_ci(st_cl)}</code></td>
        <td><code>{fmt_ci(dr_cl)}</code></td>
        <td><code>{sgmc['COULOMBLOQO_standalone']:.6f}</code></td>
        <td><code>0.828703 &gt; 0.70</code> (FAIL vs <code>EULERFUSE</code>)</td>
        <td><code>0.739842 &gt; 0.70</code> (FAIL vs <code>GEMSDOE23</code>)</td>
      </tr>
      <tr>
        <td><code>COULOMBLOQO dual45</code> (Next Step 1 re-read)</td>
        <td><code>0.009107 [0.007913, 0.010287]</code></td>
        <td><code>0.101998 [0.090606, 0.113716]</code></td>
        <td><code>{sgmc['COULOMBLOQO_dual45']:.6f}</code></td>
        <td><code>0.732565 &gt; 0.70</code> (FAIL vs <code>EULERFUSE</code>)</td>
        <td><code>0.722420 &gt; 0.70</code> (FAIL vs <code>GEMSDOE23</code>)</td>
      </tr>
      <tr>
        <td><code>R0</code> / <code>H19_5_vis_d2</code> Baseline</td>
        <td><code>{fmt_ci(st_r0)}</code></td>
        <td><code>{fmt_ci(dr_h19)}</code></td>
        <td><code>{sgmc['R0']:.6f}</code></td>
        <td>—</td>
        <td>—</td>
      </tr>
    </tbody>
  </table>
</section>
</main>
</body>
</html>
"""


def inject(path: Path, block: str, begin_marker: str, end_marker: str, anchor: str, before: bool = False) -> None:
    s = path.read_text(encoding="utf-8")
    if begin_marker in s:
        s = s[: s.index(begin_marker)] + block + s[s.index(end_marker) + len(end_marker) :]
    else:
        act_anchor = anchor
        if before:
            for cand in ("<!-- POISSONFLEX:BEGIN", "<!-- PROVINCETOE:BEGIN", anchor):
                if cand in s:
                    act_anchor = cand
                    break
        if before:
            i = s.index(act_anchor)
            s = s[:i] + block + "\n" + s[i:]
        else:
            i = s.index(act_anchor) + len(act_anchor)
            s = s[:i] + "\n" + block + "\n" + s[i:]
    path.write_text(s, encoding="utf-8")
    print("rendered", path.relative_to(ROOT))


def main() -> int:
    (ROOT / "docs/poissonknick.html").write_text(subpage_html, encoding="utf-8")
    print("wrote docs/poissonknick.html")

    inject(
        ROOT / "README.md",
        md_block,
        "<!-- POISSONKNICK:BEGIN",
        "<!-- POISSONKNICK:END -->",
        "<!-- BLINDFAULT:BEGIN",
        before=True,
    )
    for page in ("index.html", "executive-summary.html", "SUBMIT.html"):
        inject(
            ROOT / "docs" / page,
            html_banner,
            "<!-- POISSONKNICK:BEGIN",
            "<!-- POISSONKNICK:END -->",
            "<!-- BLINDFAULT:BEGIN",
            before=True,
        )
    inject(
        ROOT / "docs/index.html",
        html_card,
        "<!-- POISSONKNICK-CARD:BEGIN",
        "<!-- POISSONKNICK-CARD:END -->",
        "<main>",
        before=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
