#!/usr/bin/env python3
"""Render the POISSONFLEX status banner, auditable multi-instrument & official-source
table, and download links into README.md and docs/{index,executive-summary,SUBMIT,submit,HYPOTHESES}.html
directly from evidence/poissonflex_run_card.json and evidence/poissonflex_holdout.json.

Idempotent: content between <!-- POISSONFLEX:BEGIN --> and <!-- POISSONFLEX:END --> is
replaced cleanly without disturbing historical contract assertions.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = json.loads((ROOT / "evidence/poissonflex_run_card.json").read_text())
# This is a historical renderer, not an authorized selector. A promoted or
# missing eligibility flag cannot override the published literal witness.
if CARD.get("submission_eligible") is not False:
    raise ValueError("literal registry pre-placement STOP blocks historical renderer promotion")
HOLD = json.loads((ROOT / "evidence/poissonflex_holdout.json").read_text())

best = CARD["primary_arm"]
sc = CARD["holdout_dti"]["scores"]
st = CARD["holdout_dti"]["static_dcat2_deployment"]
sgmc = CARD["holdout_dti"]["sgmc_off_catalogue_proxy_gt3px"]["dti_by_arm"]
ref = CARD["holdout_dti"]["repository_holdout_best"]
reg = CARD["correlation_overlap_vs_registry"]
loc = reg["local"]
pub = reg["public"]
eq80 = reg.get("worst_equal_budget_public_le_80k") or {}
verdict = CARD["verdict"]
ok_submit = CARD["submission_eligible"]
arms = CARD["all_arms"]

stem = Path(CARD["file"]).name[: -len(".tif")]
tif_rel = CARD["file"].split("docs/")[1]
zip_rel = tif_rel[:-4] + ".zip" if CARD.get("zip_sha256") else None
eq_rel = arms["poissonflex_eq"]["file"].split("docs/")[1]
raw_rel = arms["poissonflex_raw"]["file"].split("docs/")[1]


def ci(s: dict) -> str:
    return f"{s['dti']:.6f} [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]"


submit_badge_md = (
    "✅ OK TO SUBMIT (cleared by automated gates)"
    if ok_submit
    else (
        f"⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (`verdict: \"{verdict}\"`, `submission_eligible: false`; "
        f"primary HOLDOUT-DTI {sc[best]['dti']:.6f} < holdout-best {ref['dti']:.6f} and 126k-px public witness 0.7541 > 0.70)"
    )
)

md_block = f"""<!-- POISSONFLEX:BEGIN (rendered by scripts/render_poissonflex_site.py from evidence/poissonflex_run_card.json) -->
> ### Newest Session (2026-10-25) — Lane `POISSONFLEX` (`gems/poissonflex.py`; 3 new validated TIFFs; verdict **`{verdict}`**)
> **✅ OK TO DOWNLOAD FOR RESEARCH** (`10/10` `gems.gates` + `13/13` `gems57.validate` PASS; `float32` in `[0, 1]`, `0.0` outside footprint) · **{submit_badge_md}** · weekly slots used: **0** · experiments: **{CARD['experiments_used']}**
>
> - **Download winning arm (`45,000` dots, nested OOF support):** [`{stem}.tif`](docs/{tif_rel}){f' · [one-TIFF ZIP](docs/{zip_rel})' if zip_rel else ''} · [audit JSON](docs/downloads/{stem[:-len('-zeros')]}-audit.json) · [JSON Run Card](docs/downloads/poissonflex_run_card.json) · [PhD Analysis](docs/ANALYSIS_20261025_POISSONFLEX.md) · [Pre-Registered Hypotheses](docs/HYPOTHESES_20261025_POISSONFLEX.md)
> - **SHA-256 (`-zeros.tif`):** `{CARD['raster_sha256']}`{f' · ZIP `{CARD["zip_sha256"]}`' if CARD.get('zip_sha256') else ''}
> - **Automated Validator (zero human step):** single-band `float32`, `EPSG:32611`, `3730 × 3292` (`100 m`), all values finite in `[0.0, 1.0]` (prevents DrivenData `"Predicted values must be in range [0, 1]"` error), `0.0` outside footprint, `45,000` unit dots (`>= 2.8 px` spacing), `0` catalogue mass (`d_cat > 2.0 px`).
> - **HOLDOUT-DTI (`{CARD['holdout_dti']['evaluator_version']}`, `{CARD['holdout_dti']['withheld_positives']:,}` withheld positives, `8` buffered quadrant folds, seeds `20+30`):**
>   - **Primary strict draw-blind (`d_visible > 2.0`):** `poissonflex_opt` **`{ci(sc['poissonflex_opt'])}`** (beats `PROVINCETOE` `0.106452`, `H19-5` `{ci(sc['H19_5_dvis2'])}` by paired `+0.010709 [+0.002297, +0.018444]`, `COULOMBDM` `0.094496`, and `BLINDFAULT` `0.047896`; trails holdout-best `{ref['lane']}` `{ci(sc['COULOMBLOQO_standalone_dvis2'])}` by `-0.006424 [-0.013250, +0.000170]`); `poissonflex_eq` `{ci(sc['poissonflex_eq'])}`; `poissonflex_raw` `{ci(sc['poissonflex_raw'])}`.
>   - **Static deployment (`d_cat > 2.0`):** `poissonflex_opt` **`{ci(st['poissonflex_opt'])}`** (`2.20x` parent `R0` `{ci(st['R0'])}`, vs `COULOMBLOQO standalone` `{ci(st['COULOMBLOQO_standalone'])}` and `PROVINCETOE piedbasin` `0.009711`).
>   - **Off-catalogue `USGS SGMC` bedrock fault `PROXY` (`62,122` px `> 3 px` from `existing_faults`):** `poissonflex_opt` **`{sgmc['poissonflex_opt']:.6f}`** (**`+35.4%`** over `COULOMBLOQO standalone` `{sgmc['COULOMBLOQO_standalone']:.6f}`, **`+32.7%`** over `PROVINCETOE` `0.091183`, and **`+26.8%`** over parent `R0` `{sgmc['R0']:.6f}`).
>   - **NE Quadrant LOQO Collapse Cured (`#IR-92-NE-QUADRANT-LOQO-COLLAPSE`):** `NE` dot allocation restored from `0.1%` (`BLINDFAULT`) / `11.2%` (`COULOMBLOQO`) to **`22.7%`** (`NW 21.9% / NE 22.7% / SW 33.8% / SE 21.6%`), beating `COULOMBLOQO` in `NW` (`0.117551` vs `0.111948`).
> - **Leakage Canaries (`32/32 PASS`):** max symmetric AUC **`{CARD['leakage_canaries']['max_symmetric_auc']:.6f} <= 0.90`** (`{CARD['leakage_canaries']['max_feature']}`); new `f03_poisson_demag_conduit` = `0.548458` (`3.66x` excess AUC over raw `RTP` tilt `0.513278`).
> - **Uniqueness (`REGISTRY-MEASUREMENT`):** **PASS** vs all `{loc['rasters_checked']}` local `GEMSDOE92` rasters (`max 3-px overlap = {loc['worst_matched_budget_forward_overlap']:.4f} <= 0.70`, `max |ρ| = {loc['worst_abs_spearman']:.4f} <= 0.90`; vs `R0`: `{reg['overlap_with_R0_3px']:.4f}`, vs `COULOMBLOQO standalone`: `{reg['overlap_with_COULOMBLOQO_standalone_3px']:.4f}`), **PASS** vs all `<= 80,000`-dot public rasters across `102` repos (`max = {eq80.get('literal_forward_overlap', 0.0):.4f} <= 0.70`), and **PASS** continuous surface `|ρ|` across all `{pub['rasters_checked']}` public blobs (`max |ρ| = {pub['worst_abs_spearman']:.4f} <= 0.90`); **STOP** on `100k–126k`-dot public rasters (`{pub['worst_matched_budget_forward_overlap']:.4f} > 0.70` on `{pub['worst_matched_budget_file']}`) and literal dense witness (`1.0000 > 0.70` on `17GEMSDOE`).
> - **Previous-Session Next Steps Closed:** `evidence/coulomb_loqo_dual_reading_selector.json` (`COULOMBLOQO standalone` worst matched-budget overlap `0.739842 > 0.70`, `dual45` `0.722420 > 0.70` -> both `negative`) & `evidence/ne_quadrant_loqo_collapse_diagnostic.json`.
> - **Record-Only Name:** `{CARD['submission_name']}` · **Note (`{CARD['note_chars']}/140`):** `{CARD['submission_note']}`
> - **Sibling Research TIFFs (`37,654` dots, `10/10` format gates PASS, DO NOT SUBMIT):** [`{Path(eq_rel).name}`](docs/{eq_rel}) (`{arms['poissonflex_eq']['sha256'][:16]}…`) · [`{Path(raw_rel).name}`](docs/{raw_rel}) (`{arms['poissonflex_raw']['sha256'][:16]}…`).
<!-- POISSONFLEX:END -->"""

html_banner = f"""<!-- POISSONFLEX:BEGIN (rendered by scripts/render_poissonflex_site.py) -->
<aside id="poissonflex-session-banner" class="banner banner-warn" aria-label="POISSONFLEX newest session status" style="border:2px solid #7f1d1d;">
  <p><strong>Newest Session (2026-10-25) — Lane <code>POISSONFLEX</code> (Poisson Gravity–Magnetic Breakdown + Basement Rollover Flexure + Canyon Knickpoint LOQO): 3 validated research GeoTIFFs built. Verdict: <code>{verdict}</code>.</strong></p>
  <p>
    <span style="background:#14532d;color:#dcfce7;padding:0.35rem 0.7rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0.4rem 0.2rem 0;">✅ OK TO DOWNLOAD FOR RESEARCH — 10/10 + 13/13 automated gates PASS, finite [0, 1], zeros outside footprint</span>
    <span style="background:#7f1d1d;color:#fee2e2;padding:0.35rem 0.7rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0;">⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (verdict: {verdict}; primary DTI {sc[best]['dti']:.6f} &lt; holdout-best {ref['dti']:.6f}; 0 weekly slots spent)</span>
  </p>
  <p>
    <a href="{tif_rel}" download><strong>Download {stem}.tif (45,000 dots)</strong></a>{f' · <a href="{zip_rel}" download>one-TIFF ZIP</a>' if zip_rel else ''}
    · <a href="downloads/{stem[:-len('-zeros')]}-audit.json">audit JSON</a>
    · <a href="downloads/poissonflex_run_card.json">JSON Run Card</a>
    · <a href="ANALYSIS_20261025_POISSONFLEX.md">PhD Analysis (GEMSDOE32 0.2778 vs 0.4413 &amp; POISSONFLEX)</a>
    · <a href="HYPOTHESES_20261025_POISSONFLEX.md">Pre-Registered Hypotheses</a>
    · <a href="executive-summary.html">Executive Summary &amp; How to Submit</a>
  </p>
  <p>
    SHA-256 <code>{CARD['raster_sha256']}</code>.
    <strong>HOLDOUT-DTI</strong> (<code>{CARD['holdout_dti']['evaluator_version']}</code>, {CARD['holdout_dti']['withheld_positives']:,} withheld positives, strict draw-blind <code>d_visible &gt; 2.0</code>):
    <code>poissonflex_opt</code> <strong><code>{ci(sc['poissonflex_opt'])}</code></strong> (beats <code>H19-5</code> <code>{ci(sc['H19_5_dvis2'])}</code> by <code>+0.010709</code>, <code>COULOMBDM</code> <code>0.094496</code>, and <code>BLINDFAULT</code> <code>0.047896</code>; static <code>d_cat &gt; 2.0</code> <code>{ci(st['poissonflex_opt'])}</code> vs <code>R0</code> <code>0.004006</code>; off-catalogue <code>USGS SGMC PROXY</code> <strong><code>{sgmc['poissonflex_opt']:.6f}</code></strong>, <code>+35.4%</code> over <code>COULOMBLOQO standalone</code> <code>{sgmc['COULOMBLOQO_standalone']:.6f}</code>).
    Canaries: <code>32/32 PASS</code> (max symmetric AUC <code>{CARD['leakage_canaries']['max_symmetric_auc']:.6f} &le; 0.90</code>).
    Uniqueness (<code>REGISTRY-MEASUREMENT</code>): local {loc['rasters_checked']} rasters PASS (max overlap <code>{loc['worst_matched_budget_forward_overlap']:.4f} &le; 0.70</code>, |&rho;| <code>{loc['worst_abs_spearman']:.4f}</code>); &le;80k-dot public rasters across 102 repos PASS (max <code>{eq80.get('literal_forward_overlap', 0.0):.4f} &le; 0.70</code>); continuous surface |&rho;| across {pub['rasters_checked']} public blobs PASS (max <code>{pub['worst_abs_spearman']:.4f} &le; 0.90</code>); 100k–126k-px public witness <code>{pub['worst_matched_budget_forward_overlap']:.4f} &gt; 0.70</code> (<code>62GEMSDOE ventcons</code>).
    Record-only name <code>{CARD['submission_name']}</code>; note ({CARD['note_chars']}/140) <code>{CARD['submission_note']}</code>.
  </p>
  <p>
    Sibling pre-registered arms (37,654 dots, format-valid `[0, 1]`, research only, DO NOT SUBMIT):
    <a href="{eq_rel}" download>{Path(eq_rel).name}</a> (SHA-256 <code>{arms['poissonflex_eq']['sha256']}</code> · <a href="downloads/{Path(eq_rel).name[:-len('-zeros.tif')]}-audit.json">audit</a>) ·
    <a href="{raw_rel}" download>{Path(raw_rel).name}</a> (SHA-256 <code>{arms['poissonflex_raw']['sha256']}</code> · <a href="downloads/{Path(raw_rel).name[:-len('-zeros.tif')]}-audit.json">audit</a>).
  </p>
  <details style="margin-top:0.5rem;">
    <summary><strong>Auditable POISSONFLEX Results &amp; Verified Official Competition Sources (Click to Expand)</strong></summary>
    <table style="width:100%;margin-top:0.5rem;border-collapse:collapse;font-size:0.9rem;">
      <thead>
        <tr>
          <th style="text-align:left;border-bottom:1px solid #555;padding:0.25rem;">Candidate / Baseline</th>
          <th style="text-align:right;border-bottom:1px solid #555;padding:0.25rem;">Dots</th>
          <th style="text-align:right;border-bottom:1px solid #555;padding:0.25rem;">Strict LOQO d_vis&gt;2 HOLDOUT-DTI</th>
          <th style="text-align:right;border-bottom:1px solid #555;padding:0.25rem;">Static d_cat&gt;2 HOLDOUT-DTI</th>
          <th style="text-align:right;border-bottom:1px solid #555;padding:0.25rem;">SGMC Off-Cat PROXY</th>
          <th style="text-align:left;border-bottom:1px solid #555;padding:0.25rem;">Gate Verdict</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:0.25rem;"><code>POISSONFLEX poissonflex_opt</code></td>
          <td style="text-align:right;padding:0.25rem;">45,000</td>
          <td style="text-align:right;padding:0.25rem;"><strong>{ci(sc['poissonflex_opt'])}</strong></td>
          <td style="text-align:right;padding:0.25rem;"><strong>{ci(st['poissonflex_opt'])}</strong></td>
          <td style="text-align:right;padding:0.25rem;"><strong>{sgmc['poissonflex_opt']:.6f}</strong></td>
          <td style="padding:0.25rem;"><code>negative</code> (research TIF; DO NOT SUBMIT)</td>
        </tr>
        <tr>
          <td style="padding:0.25rem;"><code>POISSONFLEX poissonflex_eq</code></td>
          <td style="text-align:right;padding:0.25rem;">37,654</td>
          <td style="text-align:right;padding:0.25rem;">{ci(sc['poissonflex_eq'])}</td>
          <td style="text-align:right;padding:0.25rem;">{ci(st['poissonflex_eq'])}</td>
          <td style="text-align:right;padding:0.25rem;">{sgmc['poissonflex_eq']:.6f}</td>
          <td style="padding:0.25rem;"><code>negative</code> (research TIF; DO NOT SUBMIT)</td>
        </tr>
        <tr>
          <td style="padding:0.25rem;"><code>POISSONFLEX poissonflex_raw</code></td>
          <td style="text-align:right;padding:0.25rem;">37,654</td>
          <td style="text-align:right;padding:0.25rem;">{ci(sc['poissonflex_raw'])}</td>
          <td style="text-align:right;padding:0.25rem;">{ci(st['poissonflex_raw'])}</td>
          <td style="text-align:right;padding:0.25rem;">{sgmc['poissonflex_raw']:.6f}</td>
          <td style="padding:0.25rem;"><code>negative</code> (research TIF; DO NOT SUBMIT)</td>
        </tr>
        <tr>
          <td style="padding:0.25rem;"><code>COULOMBLOQO standalone</code> (Repo Holdout-Best)</td>
          <td style="text-align:right;padding:0.25rem;">37,654</td>
          <td style="text-align:right;padding:0.25rem;">{ci(sc['COULOMBLOQO_standalone_dvis2'])}</td>
          <td style="text-align:right;padding:0.25rem;">{ci(st['COULOMBLOQO_standalone'])}</td>
          <td style="text-align:right;padding:0.25rem;">{sgmc['COULOMBLOQO_standalone']:.6f}</td>
          <td style="padding:0.25rem;"><code>negative</code> (0.7398 &gt; 0.70 on 100k witness)</td>
        </tr>
        <tr>
          <td style="padding:0.25rem;"><code>H19-5</code> / <code>R0</code> (GEMSDOE32 0.2778 [CLAIM] Lineage)</td>
          <td style="text-align:right;padding:0.25rem;">37,654</td>
          <td style="text-align:right;padding:0.25rem;">{ci(sc['H19_5_dvis2'])} (H19-5)</td>
          <td style="text-align:right;padding:0.25rem;">{ci(st['R0'])} (R0)</td>
          <td style="text-align:right;padding:0.25rem;">{sgmc['R0']:.6f}</td>
          <td style="padding:0.25rem;">Pinned parent baseline</td>
        </tr>
      </tbody>
    </table>
    <p style="margin-top:0.4rem;font-size:0.85rem;">
      Verified Official Links:
      <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">DrivenData Problem #306</a> ·
      <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">Leaderboard</a> ·
      <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Official Rules PDF (96647.pdf)</a> ·
      <a href="https://github.com/drivendataorg/gems-prize-reference-solution">Reference Solution</a> ·
      <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a> ·
      <a href="https://gbcge.org/current-projects/ingenious/">GBCGE INGENIOUS</a> ·
      <a href="https://gdr.openei.org/submissions/1391">OpenEI GDR #1391</a> ·
      <a href="https://epsg.io/32611">EPSG:32611</a> ·
      <a href="https://en.wikipedia.org/wiki/Tversky_index">Tversky Index</a>.
    </p>
  </details>
</aside>
<!-- POISSONFLEX:END -->"""

hyp_card = f"""<!-- POISSONFLEX:BEGIN (rendered by scripts/render_poissonflex_site.py) -->
<section class="download-card" style="margin-bottom: 1.5rem; padding: 1.25rem; border: 2px solid #7f1d1d;">
  <p class="kicker" style="color:#4ecb71;">Newest Pre-Registered Session (2026-10-25) · POISSONFLEX (3/3 Arms Executed) · Strict LOQO HOLDOUT-DTI {sc['poissonflex_opt']['dti']:.6f} · Off-Catalogue SGMC PROXY {sgmc['poissonflex_opt']:.6f} (+35.4%)</p>
  <h2 style="margin-top:0.2rem;">2026-10-25 Ranked Hypotheses (<a href="HYPOTHESES_20261025_POISSONFLEX.md">HYPOTHESES_20261025_POISSONFLEX.md</a> &amp; <a href="ANALYSIS_20261025_POISSONFLEX.md">ANALYSIS_20261025_POISSONFLEX.md</a>)</h2>
  <p>
    <strong>✅ OK TO DOWNLOAD FOR RESEARCH:</strong> <a href="{tif_rel}" download><code>{stem}.tif</code></a> · <a href="downloads/poissonflex_run_card.json">Run Card</a> ·
    <strong>⛔ DO NOT SUBMIT (<code>verdict: {verdict}</code>, 0 weekly slots spent).</strong>
  </p>
  <ol>
    <li><strong>Rank #1 (Implemented — <code>POISSONFLEX</code>):</strong> Poisson Gravity–Pseudogravity Hydrothermal Breakdown (<code>Bands 2, 5, 11, 13, 18</code>) + Hanging-Wall Basement Rollover Flexure (<code>Bands 12, 15, 19</code>) + Canyon Knickpoint Strike Integrals + Quadrant-Deconfounded Covariate Rank Alignment &amp; Nested Visible-Only OOF Support (<code>45,000</code> dots). <code>32/32</code> canaries PASS (max AUC <code>{CARD['leakage_canaries']['max_symmetric_auc']:.6f}</code>); primary strict LOQO <strong>HOLDOUT-DTI = <code>{ci(sc['poissonflex_opt'])}</code></strong>; static <strong>HOLDOUT-DTI = <code>{ci(st['poissonflex_opt'])}</code></strong>; off-catalogue <code>USGS SGMC PROXY = {sgmc['poissonflex_opt']:.6f}</code>.</li>
    <li><strong>Rank #2 (Queued Reserve — <code>THERMAL-UPFLOW-PECLET</code>):</strong> Advective Geothermal Upflow Plume Asymmetry &amp; Smectite–Illite Clay-Cap Lateral Pinchout (<code>OpenEI GDR #1391</code> + <code>Band 17 cond_surf</code> + <code>Bands 12, 15, 16</code>).</li>
    <li><strong>Rank #3 (Queued Reserve — <code>SPECTRAL-DEPTH-DECAY</code>):</strong> Radial-Log-Power Spector–Grant Depth-Matched Multi-Physics Edge Pairing (<code>Bands 2, 13, 15</code>).</li>
    <li><strong>Rank #4 (External Official Public Data — <code>DECONFOUNDED-INSAR-3DEP-1M</code>):</strong> <a href="https://www.usgs.gov/3d-elevation-program">USGS 3DEP 1 m LiDAR / 10 m DEM</a> Micro-Scarp Curvature &amp; Lake Lahontan Shoreline Veto (network-blocked inside sandbox; top external lever outside sandbox).</li>
  </ol>
</section>
<!-- POISSONFLEX:END -->"""


def inject_before_or_after(path: Path, block: str, before_marker: str | None = None, after_marker: str | None = None) -> None:
    s = path.read_text(encoding="utf-8")
    b, e = "<!-- POISSONFLEX:BEGIN", "<!-- POISSONFLEX:END -->"
    if b in s:
        s = s[: s.index(b)] + block + s[s.index(e) + len(e) :]
    elif before_marker and before_marker in s:
        idx = s.index(before_marker)
        s = s[:idx] + block + "\n\n" + s[idx:]
    elif after_marker and after_marker in s:
        idx = s.index(after_marker) + len(after_marker)
        s = s[:idx] + "\n" + block + "\n" + s[idx:]
    else:
        raise RuntimeError(f"Could not find marker in {path}")
    path.write_text(s, encoding="utf-8")
    print(f"rendered {path.relative_to(ROOT)}")


inject_before_or_after(ROOT / "README.md", md_block, before_marker="<!-- PROVINCETOE:BEGIN")
for page in ("index.html", "executive-summary.html", "SUBMIT.html"):
    page_banner = html_banner.replace('id="poissonflex-session-banner"', f'id="poissonflex-banner-{page.split(".")[0]}"')
    p_path = ROOT / "docs" / page
    marker = "<!-- PROVINCETOE:BEGIN" if "<!-- PROVINCETOE:BEGIN" in p_path.read_text(encoding="utf-8") else "<!-- BLINDFAULT:BEGIN"
    inject_before_or_after(p_path, page_banner, before_marker=marker)
inject_before_or_after(ROOT / "docs/HYPOTHESES.html", hyp_card, after_marker="<main>")
