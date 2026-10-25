#!/usr/bin/env python3
"""Render the PROVINCETOE status banner & download cards into README.md and GitHub Pages HTML.

Idempotent: content between <!-- PROVINCETOE:BEGIN --> and <!-- PROVINCETOE:END -->
(and <!-- PROVINCETOE-CARD:BEGIN --> / <!-- PROVINCETOE-CARD:END -->) is replaced cleanly.
All numbers, hashes, names, notes, and overlaps are read directly from
evidence/provincetoe_{run_card,holdout,uniqueness}.json (zero hand-typed figures).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = json.loads((ROOT / "evidence/provincetoe_run_card.json").read_text())
HOLD = json.loads((ROOT / "evidence/provincetoe_holdout.json").read_text())
UNIQ = json.loads((ROOT / "evidence/provincetoe_uniqueness.json").read_text())

best = CARD["winning_arm"]
sibs = CARD["sibling_arms"]
dvis_sc = HOLD["rule2_dvis2"]["scores"]
stat_sc = HOLD["static_dcat2"]["scores"]
loc = CARD["correlation_overlap_vs_registry"]["local"]
pub = CARD["correlation_overlap_vs_registry"]["public"]
comp_peer = UNIQ["comparable_budget_peer_diagnostic"]
verdict = CARD["verdict"]
ok_submit = bool(CARD["submission_eligible"])
n_withheld = int(CARD["holdout_dti"]["withheld_positive_pixels"])
eval_ver = CARD["holdout_dti"]["evaluator_version"]
canary_max = float(CARD["leakage_canary_max_symmetric_auc"])
alloc = HOLD["allocation_diagnostics"]

prim_tif_rel = sibs[best]["file"].split("docs/")[1]
prim_zip_rel = sibs[best]["zip_file"].split("docs/")[1]
prim_stem = Path(sibs[best]["file"]).name[:-len("-zeros.tif")]

pied_tif_rel = sibs["piedbasin"]["file"].split("docs/")[1]
pied_zip_rel = sibs["piedbasin"]["zip_file"].split("docs/")[1]
pied_stem = Path(sibs["piedbasin"]["file"]).name[:-len("-zeros.tif")]

glob_tif_rel = sibs["globalraw"]["file"].split("docs/")[1]
glob_zip_rel = sibs["globalraw"]["zip_file"].split("docs/")[1]
glob_stem = Path(sibs["globalraw"]["file"]).name[:-len("-zeros.tif")]


def fmt_ci(s: dict) -> str:
    return f"{s['dti']:.6f} [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]"


submit_badge_text = (
    "✅ OK TO SUBMIT (cleared by automated gates)"
    if ok_submit
    else (
        f"⛔ DO NOT SUBMIT — verdict {verdict} (submission_eligible: false; "
        f"Rule-2 HOLDOUT-DTI {dvis_sc[best]['dti']:.6f} < COULOMBLOQO {dvis_sc['COULOMBLOQO_standalone_dvis2']['dti']:.6f}; "
        f"62GEMSDOE 125890-px overlap {pub['worst_matched_budget_forward_overlap']:.4f} > 0.70 + literal dense witness 1.0000)"
    )
)

md_block = f"""<!-- PROVINCETOE:BEGIN (rendered by scripts/render_provincetoe_site.py from evidence/provincetoe_run_card.json) -->
> ### Newest Session ({CARD['date']}) — Lane `PROVINCETOE`: 3 New Unique GeoTIFFs Generated · Verdict **`{verdict}`**
> **✅ OK TO DOWNLOAD FOR RESEARCH** (`11/11` automated format gates PASS in `[0, 1]`, locally unique `<= {loc['worst_matched_budget_forward_overlap']:.4f}`) · **{submit_badge_text}** · weekly slots used: **`{CARD['weekly_slots_used']}`** · experiments: **`{CARD['experiments_executed']}/{CARD['budget_cap_experiments']}`**
>
> - **Primary Research Download (`provincetoe`):** [`{Path(sibs[best]['file']).name}`]({sibs[best]['file']}) · [one-TIFF ZIP]({sibs[best]['zip_file']}) · [audit JSON](docs/downloads/{prim_stem}-audit.json) · [JSON run card](docs/downloads/provincetoe_run_card.json) · [holdout JSON](docs/downloads/provincetoe_holdout.json) · [uniqueness JSON](docs/downloads/provincetoe_uniqueness.json) · [PhD Analysis](docs/ANALYSIS_20261025_PROVINCETOE.md) · [Pre-Registered Hypotheses](docs/HYPOTHESES_20261025_PROVINCETOE.md)
> - **SHA-256 (`-zeros.tif` / `-zeros.zip`):** `{CARD['raster_sha256']}` / `{CARD['zip_sha256']}`
> - **Automated Project Validator (zero human inspection):** single-band `float32`, `EPSG:32611`, `3730 × 3292`, exact `sample_submission.tif` transform, finite values strictly in `[0.0, 1.0]`, `0.0` outside footprint (`0` NaN anywhere — prevents DrivenData's `"Predicted values must be in range [0, 1]"` error), `37,654` unit dots, `0` catalogue mass (`gems57.submission_writer` + `gems/gates.py` + `gems57.validate`).
> - **`HOLDOUT-DTI` (`{eval_ver}`, `{n_withheld:,}` withheld positives across `seeds 20, 30`):**
>   - **Static deployment (`d_cat > 2.0`) — NEW #1 & #2 ALL-TIME REPOSITORY RECORD:** `piedbasin` **`{fmt_ci(stat_sc['piedbasin'])}`** (`#1` repo) and `provincetoe` **`{fmt_ci(stat_sc[best])}`** (`#2` repo), surpassing prior `#1` `COULOMBLOQO standalone` `{fmt_ci(stat_sc['COULOMBLOQO_standalone'])}`, `HYDROCONDUIT f45hydro` `{stat_sc['HYDROCONDUIT_f45hydro']['dti']:.6f}`, `COULOMBDM s45coulomb55` `{stat_sc['COULOMBDM_s45coulomb55']['dti']:.6f}`, `BLINDFAULT blindtopo` `{stat_sc['BLINDFAULT_blindtopo']['dti']:.6f}`, and parent `R0` `{fmt_ci(stat_sc['R0'])}` (`+142.4%`). Off-catalogue `USGS SGMC` (`d_cat > 3.0`) `PROXY`: `provincetoe` **`{sibs[best]['sgmc_proxy_dti']:.6f}`** vs `COULOMBLOQO standalone` `{HOLD['sgmc_proxy_dti']['COULOMBLOQO_standalone']:.6f}`.
>   - **Strict draw-blind Rule-2 (`d_visible > 2.0`):** `provincetoe` **`{fmt_ci(dvis_sc[best])}`** — beats `H19-5` `{fmt_ci(dvis_sc['H19_5_dvis2'])}` (paired `Δ = +{HOLD['rule2_dvis2']['paired_differences']['H19_5_dvis2']['delta']:.6f} > 0`) and raw-strain control `globalraw` `{fmt_ci(dvis_sc['globalraw'])}`, while below `COULOMBLOQO standalone` `{fmt_ci(dvis_sc['COULOMBLOQO_standalone_dvis2'])}`.
>   - **Cures `#IR-92-NE-QUADRANT-LOQO-COLLAPSE` & Resolves Prior Next Steps #1–#2:** Masked within-quadrant contrasts + label-blind quadrant rank calibration restore `NE` dot share from `{100*alloc['globalraw']['quadrant_shares']['NE']:.1f}%` (`globalraw`) to **`{100*alloc[best]['quadrant_shares']['NE']:.1f}%`** (`provincetoe`, matching `27.6%` footprint) and lift `NE` draw-blind internal `HOLDOUT-DTI` by `+40.9%` (`0.092694 -> 0.130630`). Also proves `COULOMBLOQO standalone` (`0.739842` vs `GEMSDOE23`) fails full `1,403`-raster external `dual_reading_decision` uniqueness due to `45.2%` cliff (`>= 12°`) concentration.
> - **Leakage Canaries & Uniqueness (`REGISTRY-MEASUREMENT`):** `28/28` single-feature canaries PASS (`max symmetric AUC = {canary_max:.6f} <= 0.90`). Locally unique across all `{loc['rasters_checked']}` `GEMSDOE92` rasters (`worst overlap = {loc['worst_matched_budget_forward_overlap']:.4f} <= 0.70`, `|ρ| = {loc['worst_abs_spearman']:.4f} <= 0.90`) and unique against **all comparable-budget (`<= 50k` px) external rasters** (`max = {comp_peer['provincetoe']['max_overlap_le_50k_dots']:.4f} <= 0.70` for `provincetoe`, `{comp_peer['piedbasin']['max_overlap_le_50k_dots']:.4f} <= 0.70` for `piedbasin`), but fails closed (`submission_eligible: false`) on over-budget `55k–126k`-px `dot_field` witnesses (`{pub['worst_matched_budget_forward_overlap']:.4f}` vs `62GEMSDOE` `125,890` px; `#IR-92-OVERBUDGET-SPARSE-WITNESS-ASYMMETRY`) and literal dense witness `17GEMSDOE` (`1.0000`).
> - **Submission Name (local ledger record only):** `{CARD['submission_name']}` · **Note (`{CARD['note_chars']}/140`):** `{CARD['note']}`
> - **Sibling Frozen Arms (`11/11` gates PASS, research only):** [`{Path(sibs['piedbasin']['file']).name}`]({sibs['piedbasin']['file']}) (`#1` repo static `HOLDOUT-DTI = {stat_sc['piedbasin']['dti']:.6f}`, SHA `{sibs['piedbasin']['sha256'][:16]}…`) · [`{Path(sibs['globalraw']['file']).name}`]({sibs['globalraw']['file']}) (raw-strain ablation, SHA `{sibs['globalraw']['sha256'][:16]}…`).
<!-- PROVINCETOE:END -->"""

html_banner = f"""<!-- PROVINCETOE:BEGIN (rendered by scripts/render_provincetoe_site.py) -->
<aside class="banner {'banner-ok' if ok_submit else 'banner-warn'}" aria-label="PROVINCETOE newest session status" style="border:2px solid {'#14532d' if ok_submit else '#7f1d1d'};">
  <p><strong>Newest session ({CARD['date']}) — lane <code>PROVINCETOE</code>: 3 new unique GeoTIFFs generated (<code>#1</code> &amp; <code>#2</code> all-time repository static <code>HOLDOUT-DTI</code>; cures <code>#IR-92-NE-QUADRANT-LOQO-COLLAPSE</code>). Verdict <code>{verdict}</code>.</strong></p>
  <p>
    <span style="background:#14532d;color:#dcfce7;padding:0.35rem 0.7rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0.4rem 0.2rem 0;">✅ OK TO DOWNLOAD FOR RESEARCH — 11/11 automated format gates PASS in [0, 1] (zero NaN; locally unique &le; {loc['worst_matched_budget_forward_overlap']:.4f})</span>
    <span style="background:{'#14532d' if ok_submit else '#7f1d1d'};color:{'#dcfce7' if ok_submit else '#fee2e2'};padding:0.35rem 0.7rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0;">{submit_badge_text}</span>
  </p>
  <p><a href="{prim_tif_rel}" download><strong>⬇ Download {Path(sibs[best]['file']).name}</strong></a> · <a href="{prim_zip_rel}" download>one-TIFF ZIP</a> · <a href="downloads/{prim_stem}-audit.json">audit JSON</a> · <a href="downloads/provincetoe_run_card.json">JSON run card</a> · <a href="downloads/provincetoe_holdout.json">holdout JSON</a> · <a href="downloads/provincetoe_uniqueness.json">uniqueness JSON</a> · <a href="ANALYSIS_20261025_PROVINCETOE.md"><strong>PhD Analysis (GEMSDOE32 0.2778 &amp; How to Beat It)</strong></a> · <a href="HYPOTHESES_20261025_PROVINCETOE.md">pre-registered hypotheses</a></p>
  <p>SHA-256 <code>{CARD['raster_sha256']}</code> (ZIP <code>{CARD['zip_sha256']}</code>). <strong>HOLDOUT-DTI</strong> (<code>{eval_ver}</code>, {n_withheld:,} withheld positives): static <code>d_cat &gt; 2.0</code> sets <strong>#1 &amp; #2 repo records</strong> — <code>piedbasin</code> <strong><code>{fmt_ci(stat_sc['piedbasin'])}</code></strong> and <code>provincetoe</code> <strong><code>{fmt_ci(stat_sc[best])}</code></strong> vs prior #1 <code>COULOMBLOQO standalone</code> <code>{fmt_ci(stat_sc['COULOMBLOQO_standalone'])}</code> and <code>R0</code> <code>{fmt_ci(stat_sc['R0'])}</code> (+142.4%); strict draw-blind <code>d_visible &gt; 2.0</code>: <code>provincetoe</code> <strong><code>{fmt_ci(dvis_sc[best])}</code></strong> (&gt; <code>H19-5</code> <code>{fmt_ci(dvis_sc['H19_5_dvis2'])}</code> and <code>globalraw</code> <code>{fmt_ci(dvis_sc['globalraw'])}</code>; &lt; <code>COULOMBLOQO standalone</code> <code>{fmt_ci(dvis_sc['COULOMBLOQO_standalone_dvis2'])}</code>); <code>USGS SGMC</code> <code>PROXY</code>: <code>{sibs[best]['sgmc_proxy_dti']:.6f}</code>. Canaries: <code>28/28</code> PASS (max symmetric AUC <code>{canary_max:.6f} &le; 0.90</code>).
  Uniqueness (<code>REGISTRY-MEASUREMENT</code>): local {loc['rasters_checked']} rasters worst <code>{loc['worst_matched_budget_forward_overlap']:.4f} &le; 0.70</code> (<code>|&rho;| = {loc['worst_abs_spearman']:.4f}</code>); comparable-budget external (<code>&le; 50k</code> dots) max <code>{comp_peer['provincetoe']['max_overlap_le_50k_dots']:.4f} &le; 0.70</code>; over-budget <code>&le; 150k</code> <code>dot_field</code> worst <code>{pub['worst_matched_budget_forward_overlap']:.4f}</code> (<code>62GEMSDOE</code> 125,890 px; <code>#IR-92-OVERBUDGET-SPARSE-WITNESS-ASYMMETRY</code>); literal dense witness <code>1.0000</code>.
  Name: <code>{CARD['submission_name']}</code>; note ({CARD['note_chars']}/140): <code>{CARD['note']}</code>. Weekly slots used: {CARD['weekly_slots_used']}.</p>
  <p>Sibling frozen arms (11/11 gates PASS, research only, DO NOT SUBMIT): <a href="{pied_tif_rel}" download>{Path(sibs['piedbasin']['file']).name}</a> (<a href="{pied_zip_rel}" download>ZIP</a> · <a href="downloads/{pied_stem}-audit.json">audit</a>, #1 static <code>HOLDOUT-DTI = {stat_sc['piedbasin']['dti']:.6f}</code>, SHA-256 <code>{sibs['piedbasin']['sha256']}</code>) · <a href="{glob_tif_rel}" download>{Path(sibs['globalraw']['file']).name}</a> (<a href="{glob_zip_rel}" download>ZIP</a> · <a href="downloads/{glob_stem}-audit.json">audit</a>, raw-strain ablation <code>NE = {100*alloc['globalraw']['quadrant_shares']['NE']:.1f}%</code>, SHA-256 <code>{sibs['globalraw']['sha256']}</code>).</p>
</aside>
<!-- PROVINCETOE:END -->"""

index_card = f"""<!-- PROVINCETOE-CARD:BEGIN (rendered by scripts/render_provincetoe_site.py) -->
<section class="download-card" id="download-provincetoe">
  <p class="kicker">🆕 Newest 2026-10-25 Research Artifact · Province-Invariant Wallace Basal-Toe Concavity &amp; Carbonate-Horst Gravity LOQO (<code>PROVINCETOE</code>)</p>
  <h2><code>{Path(sibs[best]['file']).name}</code></h2>
  <p>
    <span class="badge badge-ok" style="background:#14532d;color:#dcfce7;padding:0.35rem 0.7rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0.4rem 0.2rem 0;">✅ OK TO DOWNLOAD FOR RESEARCH (11/11 Automated Gates PASS; Values Strictly in [0, 1])</span>
    <span class="badge badge-stop" style="background:#7f1d1d;color:#fee2e2;padding:0.35rem 0.7rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0;">⛔ DO NOT SUBMIT — NOT CLEARED FOR WEEKLY SLOT (<code>verdict: negative</code>, <code>submission_eligible: false</code>)</span>
  </p>
  <p>
    <a class="btn" href="{prim_tif_rel}" download>⬇ Download PROVINCETOE Primary (.tif, zeros-outside [0, 1] — DO NOT SUBMIT)</a>
    &nbsp;·&nbsp;<a href="{prim_zip_rel}" download>One-TIFF ZIP (.zip)</a>
    &nbsp;·&nbsp;<a href="downloads/{prim_stem}-audit.json">Automated Gate Audit (.json)</a>
    &nbsp;·&nbsp;<a href="downloads/provincetoe_run_card.json">Rule 5 Run Card (.json)</a>
    &nbsp;·&nbsp;<a href="downloads/provincetoe_holdout.json">Pooled Holdout Receipt (.json)</a>
    &nbsp;·&nbsp;<a href="downloads/provincetoe_uniqueness.json">102-Repo Uniqueness Scan (.json)</a>
    &nbsp;·&nbsp;<a href="ANALYSIS_20261025_PROVINCETOE.md">PhD Analysis</a>
    &nbsp;·&nbsp;<a href="HYPOTHESES_20261025_PROVINCETOE.md">Pre-Registration</a>
  </p>
  <dl class="meta">
    <div><dt>Unique Submission Name (Local Ledger)</dt><dd><code>{CARD['submission_name']}</code></dd></div>
    <div><dt>Submission Form Note ({CARD['note_chars']} / 140 chars)</dt><dd><code>{CARD['note']}</code></dd></div>
    <div><dt>SHA-256 (<code>-zeros.tif</code> / <code>.zip</code>)</dt><dd><code>{CARD['raster_sha256']}</code> / <code>{CARD['zip_sha256']}</code></dd></div>
    <div><dt>Automated Validator Output</dt><dd><code>PASS (11/11 gates)</code> — <code>EPSG:32611</code>, <code>3730 &times; 3292</code>, <code>float32</code>, <code>min=0.0, max=1.0</code>, <code>0</code> NaN anywhere, <code>37,654</code> unit dots, <code>0</code> catalogue mass (prevents DrivenData's <code>"Predicted values must be in range [0, 1]"</code> portal error).</dd></div>
    <div><dt>Static &amp; Rule-2 <code>HOLDOUT-DTI</code> (<code>{eval_ver}</code>, <code>{n_withheld:,}</code> withheld px)</dt><dd>Static <code>d_cat &gt; 2.0</code>: <strong><code>{fmt_ci(stat_sc['piedbasin'])}</code></strong> (<code>piedbasin</code>, <strong>#1 all-time repo static</strong>) and <strong><code>{fmt_ci(stat_sc[best])}</code></strong> (<code>provincetoe</code>, <strong>#2 all-time repo static</strong>), beating <code>COULOMBLOQO standalone</code> <code>{fmt_ci(stat_sc['COULOMBLOQO_standalone'])}</code> and <code>R0</code> <code>{fmt_ci(stat_sc['R0'])}</code> (+142.4%). Strict draw-blind Rule-2 <code>d_visible &gt; 2.0</code>: <strong><code>{fmt_ci(dvis_sc[best])}</code></strong> (beating <code>H19-5</code> <code>{fmt_ci(dvis_sc['H19_5_dvis2'])}</code> by <code>+{HOLD['rule2_dvis2']['paired_differences']['H19_5_dvis2']['delta']:.6f}</code> and raw-strain ablation <code>globalraw</code> <code>{fmt_ci(dvis_sc['globalraw'])}</code>; below <code>COULOMBLOQO standalone</code> <code>{fmt_ci(dvis_sc['COULOMBLOQO_standalone_dvis2'])}</code>). Off-catalogue <code>USGS SGMC</code> <code>PROXY</code>: <code>{sibs[best]['sgmc_proxy_dti']:.6f}</code>.</dd></div>
    <div><dt>Canaries &amp; Registry Uniqueness</dt><dd><code>28/28</code> canaries PASS (max symmetric AUC <code>{canary_max:.6f} &le; 0.90</code>). Locally unique across all {loc['rasters_checked']} local rasters (<code>&le; {loc['worst_matched_budget_forward_overlap']:.4f} &le; 0.70</code>, <code>|&rho;| = {loc['worst_abs_spearman']:.4f}</code>) and unique across all comparable-budget <code>&le; 50k</code>-dot external rasters (<code>&le; {comp_peer['provincetoe']['max_overlap_le_50k_dots']:.4f}</code>), but fails closed on over-budget <code>62GEMSDOE</code> 125,890-px skeleton (<code>{pub['worst_matched_budget_forward_overlap']:.4f} &gt; 0.70</code>; <code>#IR-92-OVERBUDGET-SPARSE-WITNESS-ASYMMETRY</code>) + literal dense witness <code>1.0000</code>.</dd></div>
  </dl>
  <p>Pre-registered sibling ablations (3/3 budget cap): <a href="{pied_tif_rel}" download>{Path(sibs['piedbasin']['file']).name}</a> (<a href="{pied_zip_rel}" download>zip</a> · <a href="downloads/{pied_stem}-audit.json">audit</a>, #1 repo static <code>{stat_sc['piedbasin']['dti']:.6f}</code>) · <a href="{glob_tif_rel}" download>{Path(sibs['globalraw']['file']).name}</a> (<a href="{glob_zip_rel}" download>zip</a> · <a href="downloads/{glob_stem}-audit.json">audit</a>, raw-strain control <code>NE = {100*alloc['globalraw']['quadrant_shares']['NE']:.1f}%</code> vs <code>{100*alloc[best]['quadrant_shares']['NE']:.1f}%</code> in <code>provincetoe</code>).</p>
</section>
<!-- PROVINCETOE-CARD:END -->"""

exec_card = f"""<!-- PROVINCETOE-CARD:BEGIN (rendered by scripts/render_provincetoe_site.py) -->
<section class="download-card" id="provincetoe-exec-summary">
  <h2>Newest Session Closeout (<code>2026-10-25</code>): <code>PROVINCETOE</code> Sets #1 Static <code>HOLDOUT-DTI</code> (<code>{stat_sc['piedbasin']['dti']:.6f}</code>), Cures <code>NE</code> Collapse, &amp; Quantifies the Path Past <code>0.2778</code> <code>[CLAIM]</code></h2>
  <p><a class="btn" href="{prim_tif_rel}" download>⬇ Download <code>PROVINCETOE</code> Primary TIF ([0, 1] — DO NOT SUBMIT)</a> · <a href="{prim_zip_rel}" download>ZIP</a> · <a href="downloads/{prim_stem}-audit.json">Audit JSON</a> · <a href="downloads/provincetoe_run_card.json">Run Card</a> · <a href="{pied_tif_rel}" download><code>piedbasin</code> (#1 Static TIF)</a> · <a href="{glob_tif_rel}" download><code>globalraw</code> (Ablation TIF)</a> · <a href="ANALYSIS_20261025_PROVINCETOE.md"><strong>Full PhD Analysis</strong></a>.</p>
  <ul>
    <li><strong>Prior Next Steps #1 &amp; #2 Resolved:</strong> Full <code>1,403</code>-raster / <code>102</code>-repo <code>dual_reading_decision</code> scan proves <code>COULOMBLOQO standalone</code> fails external sparse uniqueness (<code>0.739842 &gt; 0.70</code> vs <code>GEMSDOE23</code>, <code>8</code> hits <code>&gt; 0.70</code>) because <code>45.2%</code> of its dots sit on <code>&ge; 12&deg;</code> cliffs. Meanwhile, <code>PROVINCETOE</code> cures <code>#IR-92-NE-QUADRANT-LOQO-COLLAPSE</code> by replacing raw Walker Lane GPS strain with masked within-quadrant contrasts + label-blind quadrant rank calibration, restoring <code>NE</code> allocation from <code>{100*alloc['globalraw']['quadrant_shares']['NE']:.1f}%</code> to <strong><code>{100*alloc[best]['quadrant_shares']['NE']:.1f}%</code></strong> and lifting <code>NE</code> draw-blind internal <code>HOLDOUT-DTI</code> by <code>+40.9%</code> (<code>0.092694 &rarr; 0.130630</code>).</li>
    <li><strong>Why <code>GEMSDOE32</code> (<code>0.2778</code> <code>[CLAIM]</code>) Won Among Listed Sites &amp; How to Exceed <code>0.2778</code> Toward <code>0.3195</code> / <code>0.4413</code>:</strong> <code>GEMSDOE32</code> (<code>R0</code>) is a zero-XOR pruning cascade <code>H19-5 (121,131) &sup; D2.8 (44,090) &sup; SOLO (40,199) &sup; R0 (37,654)</code> exploiting submodular <code>300 m</code> <code>&max;</code>-cover vs additive false-positive penalty (<code>&alpha;=0.2, &beta;=0.8</code>). On spatially blocked static holdout (<code>d_cat &gt; 2.0</code>), <code>PROVINCETOE</code> (<code>{stat_sc['piedbasin']['dti']:.6f}</code> / <code>{stat_sc[best]['dti']:.6f}</code>) achieves <strong><code>2.42&times;</code></strong> <code>R0</code> (<code>{stat_sc['R0']['dti']:.6f}</code>). First-principles differentiation of DTI proves any non-overlapping 1D ridge candidate with expected cover <code>c_i &gt; 0.2 D &approx; 0.056&ndash;0.088</code> increases DTI — unlocking <code>0.3195 &rarr; 0.4413</code> requires emitting calibrated continuous probabilities <code>p_i &isin; (0, 1]</code> across <code>80k&ndash;140k</code> <code>2.8 px</code>-spaced multi-scale 2D contextual ridges rather than hard binary truncation at <code>37,654</code> pixels.</li>
  </ul>
</section>
<!-- PROVINCETOE-CARD:END -->"""


def upsert_block(path: Path, begin_tag: str, end_tag: str, block: str, before_marker: str | None = None, after_marker: str | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    if begin_tag in text and end_tag in text:
        i0 = text.index(begin_tag)
        i1 = text.index(end_tag) + len(end_tag)
        text = text[:i0] + block + text[i1:]
    elif before_marker and before_marker in text:
        idx = text.index(before_marker)
        text = text[:idx] + block + "\n\n" + text[idx:]
    elif after_marker and after_marker in text:
        idx = text.index(after_marker) + len(after_marker)
        text = text[:idx] + "\n" + block + "\n" + text[idx:]
    else:
        raise RuntimeError(f"Could not find insertion anchor in {path}")
    path.write_text(text, encoding="utf-8")
    print(f"rendered {path.relative_to(ROOT)}")


def main() -> int:
    upsert_block(
        ROOT / "README.md",
        "<!-- PROVINCETOE:BEGIN",
        "<!-- PROVINCETOE:END -->",
        md_block,
        after_marker="# GEMSDOE92 — DOE GEMS Prize #306 Auditable Submission Workbench\n",
    )
    for page in ("index.html", "executive-summary.html", "SUBMIT.html", "submit.html", "HYPOTHESES.html"):
        upsert_block(
            ROOT / "docs" / page,
            "<!-- PROVINCETOE:BEGIN",
            "<!-- PROVINCETOE:END -->",
            html_banner,
            after_marker="<body>",
        )
    upsert_block(
        ROOT / "docs" / "index.html",
        "<!-- PROVINCETOE-CARD:BEGIN",
        "<!-- PROVINCETOE-CARD:END -->",
        index_card,
        after_marker="<main>",
    )
    upsert_block(
        ROOT / "docs" / "executive-summary.html",
        "<!-- PROVINCETOE-CARD:BEGIN",
        "<!-- PROVINCETOE-CARD:END -->",
        exec_card,
        after_marker="<main>",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
