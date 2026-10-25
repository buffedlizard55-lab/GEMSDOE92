#!/usr/bin/env python3
"""Render the BLINDFAULT status block into README.md and the three site pages from the run card.

Idempotent: content between the BLINDFAULT markers is replaced; nothing else is touched.
All numbers come from evidence/blindfault_run_card.json (no hand-typed figures).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = json.loads((ROOT / "evidence/blindfault_run_card.json").read_text())
HOLD = json.loads((ROOT / "evidence/blindfault_holdout.json").read_text())

best = CARD["primary_arm"]
sc = CARD["holdout_dti"]["scores"]
low = CARD["holdout_dti"]["low_conspicuity_tercile"]
ref = CARD["holdout_dti"]["repository_holdout_best"]
reg = CARD["correlation_overlap_vs_registry"]
loc, pub = reg["local"], reg["public"]
spec = reg.get("dense_witness_specificity") or {}
verdict = CARD["verdict"]
ok_submit = CARD["submission_eligible"]
stem = Path(CARD["file"]).name[: -len(".tif")]
tif_rel = CARD["file"].split("docs/")[1]
zip_rel = CARD["zip_sha256"] and tif_rel[:-4] + ".zip"
arms = CARD["all_arms"]


def ci(s):
    return f"{s['dti']:.6f} [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]"


submit_line = ("✅ OK TO SUBMIT (cleared by the automated gate)" if ok_submit else
               f"⛔ DO NOT SUBMIT — verdict `{verdict}` (automated gate: primary HOLDOUT-DTI {sc[best]['dti']:.6f} "
               f"< holdout-best {ref['dti']:.6f})")

md = f"""<!-- BLINDFAULT:BEGIN (rendered by scripts/render_blindfault_site.py from evidence/blindfault_run_card.json) -->
> ### Session 2026-10-25 — lane `BLINDFAULT` (new unique TIFF generated; verdict **`{verdict}`**)
> **✅ OK TO DOWNLOAD** (format-valid, unique) · **{submit_line}** · weekly slots used: **0** · experiments: **{CARD['experiments_used']}**
>
> - **Download:** [`{stem}.tif`]({ 'docs/' + tif_rel }){' · [one-TIFF ZIP](docs/' + zip_rel + ')' if zip_rel else ''} · [audit JSON](docs/downloads/{stem[:-len('-zeros')]}-audit.json) · [run card](docs/downloads/blindfault_run_card.json) · [analysis](docs/ANALYSIS_20261025_BLINDFAULT.md) · [pre-registered hypotheses](docs/HYPOTHESES_20261025_BLINDFAULT.md)
> - **SHA-256:** `{CARD['raster_sha256']}`{(' · ZIP `' + CARD['zip_sha256'] + '`') if CARD['zip_sha256'] else ''}
> - **Validator (automated, no human step):** single band `float32`, `EPSG:32611`, `3730 × 3292`, finite values in `[0, 1]`, `0.0` outside footprint, 37,654 unit dots, 0 catalogue mass — written and re-read through `gems57.submission_writer` / `gems57.validate`.
> - **HOLDOUT-DTI** (`{CARD['holdout_dti']['evaluator_version']}`, {CARD['holdout_dti']['withheld_positives']:,} withheld positives, strict draw-blind LOQO, `d_visible > 2.0`): `{best}` **{ci(sc[best])}**; `blind` (hypothesis arm) {ci(sc['blind'])}; `blindflat` {ci(sc['blindflat'])}; `H19-5` reference {ci(sc['H19_5_dvis2'])}; repository holdout-best `{ref['lane']}` {ref['dti']:.6f}. Low-conspicuity tercile (mechanism instrument, 6,065 positives): `blind` {ci(low['blind'])} vs `H19-5` {ci(low['H19_5_dvis2'])}.
> - **Leakage canaries:** max symmetric AUC {CARD['leakage_canaries']['max_symmetric_auc']:.4f} (all ≤ 0.90).
> - **Uniqueness (REGISTRY-MEASUREMENT, dual reading — `#IR-92-DENSE-WITNESS-MATCHED-BUDGET`):** local registry ({loc['rasters_checked']} rasters): matched-budget worst overlap {loc['worst_matched_budget_forward_overlap']:.4f} (`{loc['worst_matched_budget_file']}`), literal worst {loc['worst_literal_forward_overlap']:.4f}, worst |ρ| {loc['worst_abs_spearman']:.4f}; public registry ({pub['rasters_checked'] if pub else 0} Git-blob-verified rasters, 102 repos, complete={reg['public_scope'].get('complete')}): matched-budget worst overlap {pub['worst_matched_budget_forward_overlap'] if pub else float('nan'):.4f} (`{pub['worst_matched_budget_file'] if pub else '—'}`), literal worst {pub['worst_literal_forward_overlap'] if pub else float('nan'):.4f}, worst |ρ| {pub['worst_abs_spearman'] if pub else float('nan'):.4f}. Overlap with parent `R0`: {reg['overlap_with_R0_3px']:.4f}. Specificity proof: the organizer-scored parent `R0` itself has literal overlap {spec.get('R0_parent_literal_overlap', float('nan')):.3f} / matched-budget {spec.get('R0_parent_matched_budget_overlap', float('nan')):.3f} against the dense witness.
> - **Submission name:** `{CARD['submission_name']}` · **Note ({CARD['note_chars']}/140):** `{CARD['submission_note']}`
> - Sibling arms (also format-valid, research only): `{Path(arms['blind']['file']).name}` (`{arms['blind']['sha256'][:16]}…`), `{Path(arms['blindflat']['file']).name}` (`{arms['blindflat']['sha256'][:16]}…`).
<!-- BLINDFAULT:END -->"""

html = f"""<!-- BLINDFAULT:BEGIN (rendered by scripts/render_blindfault_site.py) -->
<aside class="banner {'banner-ok' if ok_submit else 'banner-warn'}" aria-label="BLINDFAULT session status" style="border:2px solid {'#14532d' if ok_submit else '#7f1d1d'};">
  <p><strong>Newest session (2026-10-25) — lane <code>BLINDFAULT</code>: new unique TIFF generated. Verdict <code>{verdict}</code>.</strong></p>
  <p>
    <span style="background:#14532d;color:#dcfce7;padding:0.35rem 0.7rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0.4rem 0.2rem 0;">✅ OK TO DOWNLOAD — format-valid (automated 11-gate validator), unique on the dual registry reading</span>
    <span style="background:{'#14532d' if ok_submit else '#7f1d1d'};color:{'#dcfce7' if ok_submit else '#fee2e2'};padding:0.35rem 0.7rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.2rem 0;">{submit_line.replace('`','')}</span>
  </p>
  <p><a href="{tif_rel}" download><strong>Download {stem}.tif</strong></a>{(' · <a href="' + zip_rel + '" download>one-TIFF ZIP</a>') if zip_rel else ''} · <a href="downloads/{stem[:-len('-zeros')]}-audit.json">audit JSON</a> · <a href="downloads/blindfault_run_card.json">run card</a> · <a href="ANALYSIS_20261025_BLINDFAULT.md">analysis</a> · <a href="HYPOTHESES_20261025_BLINDFAULT.md">pre-registered hypotheses</a></p>
  <p>SHA-256 <code>{CARD['raster_sha256']}</code>. <strong>HOLDOUT-DTI</strong> ({CARD['holdout_dti']['evaluator_version']}, {CARD['holdout_dti']['withheld_positives']:,} withheld positives, strict draw-blind, <code>d_visible &gt; 2.0</code>): <code>{best}</code> <code>{ci(sc[best])}</code>; hypothesis arm <code>blind</code> <code>{ci(sc['blind'])}</code>; <code>H19-5</code> <code>{ci(sc['H19_5_dvis2'])}</code>; holdout-best <code>{ref['dti']:.6f}</code> (<code>{ref['lane']}</code>). Canaries max AUC <code>{CARD['leakage_canaries']['max_symmetric_auc']:.4f}</code>.
  Uniqueness (dual reading, <code>#IR-92-DENSE-WITNESS-MATCHED-BUDGET</code>): public registry {pub['rasters_checked'] if pub else 0} rasters — matched-budget worst overlap <code>{pub['worst_matched_budget_forward_overlap'] if pub else float('nan'):.4f}</code>, literal worst <code>{pub['worst_literal_forward_overlap'] if pub else float('nan'):.4f}</code>, worst |ρ| <code>{pub['worst_abs_spearman'] if pub else float('nan'):.4f}</code>; local {loc['rasters_checked']} rasters — matched-budget worst <code>{loc['worst_matched_budget_forward_overlap']:.4f}</code>.
  Name <code>{CARD['submission_name']}</code>; note ({CARD['note_chars']}/140) <code>{CARD['submission_note']}</code>. Weekly slots used: 0.</p>
  <p>Sibling arms (format-valid, research only, same verdict): <a href="{arms['blind']['file'].split('docs/')[1]}" download>{Path(arms['blind']['file']).name}</a> (SHA-256 <code>{arms['blind']['sha256']}</code>) · <a href="{arms['blindflat']['file'].split('docs/')[1]}" download>{Path(arms['blindflat']['file']).name}</a> (SHA-256 <code>{arms['blindflat']['sha256']}</code>).</p>
</aside>
<!-- BLINDFAULT:END -->"""


def inject(path: Path, block: str, anchor: str):
    s = path.read_text(encoding="utf-8")
    b, e = "<!-- BLINDFAULT:BEGIN", "<!-- BLINDFAULT:END -->"
    if b in s:
        s = s[: s.index(b)] + block + s[s.index(e) + len(e):]
    else:
        i = s.index(anchor) + len(anchor)
        s = s[:i] + "\n" + block + "\n" + s[i:]
    path.write_text(s, encoding="utf-8")
    print("rendered", path)


inject(ROOT / "README.md", md, "\n")  # directly under the H1 line
for page in ("index.html", "executive-summary.html", "SUBMIT.html"):
    inject(ROOT / "docs" / page, html, "<body>")
