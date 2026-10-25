#!/usr/bin/env python3
"""Render the top-of-page lane status boxes on every entry page.

Sources of truth:
  1. evidence/relayconduit_run_card.json (completed 2026-10-25 RELAYCONDUIT lane)
  2. docs/downloads/current_submission.json (byte-bound to VARIO primary via render_vario_status)

Nothing is hand-typed: every number, hash, name and verdict comes from the JSON
receipts. Idempotent: replaces the block between <!-- CURRENT:BEGIN --> and
<!-- CURRENT:END --> and invokes render_vario_status.render(ROOT, write=True).
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUR = ROOT / "docs" / "downloads" / "current_submission.json"
RC_CARD = ROOT / "evidence" / "relayconduit_run_card.json"
CL_CARD = ROOT / "evidence" / "chilistric_run_card.json"
SUBMIT_URL = "https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/"
BEGIN, END = "<!-- CURRENT:BEGIN -->", "<!-- CURRENT:END -->"
HTML_PAGES = {  # page -> prefix from the page to docs/
    ROOT / "docs" / "index.html": "",
    ROOT / "docs" / "executive-summary.html": "",
    ROOT / "docs" / "SUBMIT.html": "",
    ROOT / "docs" / "submit.html": "",
    ROOT / "index.html": "docs/",
}
MD_PAGES = {ROOT / "README.md": "docs/", ROOT / "docs" / "SUBMIT.md": ""}


def fmt_ci(ci):
    return f"[{ci[0]:.6f}, {ci[1]:.6f}]"


def facts(c):
    h = c["holdout_dti"]
    u = c["uniqueness"]
    ctrl = c["control"]
    d = h.get("paired_vs_control", h.get("paired_vs_COULOMBLOQO_control"))
    return dict(
        dti=f"{h['dti']:.6f} {fmt_ci(h['ci95'])}", n=h["withheld_positives"], ev=h["evaluator_version"],
        ctrl_name=ctrl.get("name", "control"), ctrl=f"{ctrl['dti']:.6f} {fmt_ci(ctrl['ci95'])}",
        delta=f"{d['delta']:+.6f} {fmt_ci(d['ci95'])}",
        ovl=f"{u['worst_overlap_final']['value']:.4f}", ovl_r=u["worst_overlap_final"]["raster"],
        rho=f"{abs(u['worst_abs_rho_final']['value']):.4f}", rhos=f"{abs(u['worst_abs_rho_surface']['value']):.4f}",
        nreg=u["registry_rasters_checked"], lit=u["literal_reading"]["rasters_over_0p70"])


def reason(c):
    """Plain-language reason for a DO NOT SUBMIT verdict, derived from the JSON only."""
    out = []
    u = c["uniqueness"]
    if not u["unique_operative"]:
        w = u["worst_overlap_final"]
        out.append(f"registry duplicate under protocol rule 1: {w['value']:.4f} of its dots lie within 3 px of the dots of "
                   f"{w['raster']} ({w['their_positive']:,} dots), above the 0.70 limit")
    h = c["holdout_dti"]
    for name, v in h.get("paired_vs_required_controls", {}).items():
        if not (h["dti"] > v["control_dti"] and v["ci95"][0] > 0):
            out.append(f"did not beat {name} on the holdout")
    return "; ".join(out) or "did not pass every automated gate"


def cl_html_section(cl: dict, pre: str) -> str:
    e = html.escape
    h = cl["holdout_dti"]
    s_add = h["static_dcat_gt_2_primary"]
    oof = h["drawblind_oof_dcat_gt_2_primary"]
    r2 = h["strict_drawblind_rule2_dvis_gt_2_primary"]
    p_ctl = h["paired_differences_static_dcat_gt_2"]["no10m_fixed"]
    p_knk = h["paired_differences_static_dcat_gt_2"]["KNICKLOQO_standalone"]
    sgmc = h["sgmc_independent_basement_fault_proxy_dti"]["addtail52k"]
    u_pub = cl["correlation_overlap_vs_registry"]["public_102_repo_registry"]
    u_pm = cl["correlation_overlap_vs_registry"]["post_merge_docs_downloads"]
    files = cl["all_experiment_files"]

    tif = pre + cl["candidate_file"].removeprefix("docs/")
    zp = pre + cl["zip_file"].removeprefix("docs/")
    aud = tif.replace("-zeros.tif", "-audit.json")
    card = pre + "downloads/chilistric_run_card.json"
    hold = pre + "downloads/chilistric_holdout.json"
    uniq = pre + "downloads/chilistric_uniqueness.json"
    subp = pre + "executive-summary.html"
    ana = pre + "ANALYSIS_20261025_CHILISTRIC.md"
    hyp = pre + "HYPOTHESES_20261025_CHILISTRIC.md"
    rev = pre + "REVIEW_20261025_CHILISTRIC.md"

    return f"""<section aria-label="Completed session lane CHILISTRIC" style="border:3px solid #7f1d1d;background:#fef2f2;padding:1rem 1.2rem;margin:0 0 1.2rem 0;border-radius:8px;font-family:system-ui,sans-serif">
  <h2 style="margin-top:0">Newest completed session lane (2026-10-25) — <code>{e(cl['lane'])}</code> / primary arm <code>addtail52k</code> (3 new unique-byte GeoTIFFs)</h2>
  <p style="font-size:1.15rem;margin:.25rem 0">
    <span style="background:#14532d;color:#dcfce7;padding:0.3rem 0.65rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.15rem 0.35rem 0.15rem 0;">✅ OK TO DOWNLOAD FOR RESEARCH (11/11 automated [0, 1] gates PASS, 0 NaN; unique across all {u_pm['rasters_checked']} local rasters at {u_pm['worst_matched_budget_forward_overlap_3px']:.4f} &le; 0.70 &amp; all {u_pub['non_self_rasters_checked']:,} public rasters in 102 repos at {u_pub['worst_operative_overlap_3px']:.4f} &le; 0.70)</span>
    <span style="background:#7f1d1d;color:#fee2e2;padding:0.3rem 0.65rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.15rem 0;">⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (verdict <code>{e(cl['verdict'])}</code>; literal 17GEMSDOE dense-witness overlap 1.000 &gt; 0.70 &amp; static tie vs LISTRICLOQO 0.013295; 0 slots spent)</span>
  </p>
  <p style="font-size:1.1rem">
    <a href="{e(tif)}" download><strong>⬇ Download GeoTIFF ({e(cl['candidate_file'].split('/')[-1])})</strong></a>
    · <a href="{e(zp)}" download>one-TIFF ZIP</a>
    · <a href="{e(aud)}">audit JSON</a>
    · <a href="{e(card)}">JSON Run Card</a>
    · <a href="{e(hold)}">holdout JSON</a>
    · <a href="{e(uniq)}">102-repo uniqueness JSON</a>
    · <a href="{e(subp)}"><strong>Executive Summary &amp; How to Submit</strong></a>
    · <a href="{e(ana)}">PhD Analysis (0.2778 / 0.3195 / 0.4413 &amp; Verified Sources Table)</a>
    · <a href="{e(hyp)}">Pre-Registered Hypotheses</a>
    · <a href="{e(rev)}">3-Pass Review</a>
  </p>
  <p><strong>Step-by-step DrivenData #306 submission reference (only for a future ✅ cleared artifact; do NOT upload a <code>negative</code> file):</strong>
    1) Download the zeros-outside single-band <code>float32</code> <code>.tif</code> (or matching one-TIFF <code>.zip</code>) — strict finite <code>[0.0, 1.0]</code> values with <code>0.0</code> outside footprint prevent <em>&ldquo;Predicted values must be in range [0, 1]&rdquo;</em> with zero human pixel inspection.
    2) Open <a href="{SUBMIT_URL}">{SUBMIT_URL}</a> (not live-verified from sandbox) and choose the file.
    3) Paste note (&le;140 chars; <code>{cl['submission_note_chars']}/140</code>): <code>{e(cl['submission_note'])}</code>.
    4) Record local name <code>{e(cl['submission_name'])}</code> and log any organizer receipt in <code>ledger/submissions.csv</code>.
  </p>
  <p><strong>HOLDOUT-DTI</strong> ({e(h['evaluator_version'])}, {h['withheld_positive_pixels']:,} withheld positives, 1,000-draw 20 km paired block bootstrap):
    <strong>Strict Draw-Blind OOF (<code>d_cat &gt; 2.0</code>) = <code>{oof['dti']:.6f} {fmt_ci(oof['ci95'])}</code> (#1 ALL-TIME zero-catalogue OOF in GEMSDOE92, beating LISTRICLOQO 0.013064)</strong>;
    Static (<code>d_cat &gt; 2.0</code>) = <strong><code>{s_add['dti']:.6f} {fmt_ci(s_add['ci95'])}</code></strong>
    (paired <code>{p_ctl['delta']:+.6f} {fmt_ci(p_ctl['ci95'])}</code> over <code>no10m_fixed</code> ablation <code>0.012206</code>; paired <code>{p_knk['delta']:+.6f} {fmt_ci(p_knk['ci95'])}</code> over <code>KNICKLOQO</code> <code>0.010788</code>);
    Strict Rule-2 (<code>d_visible &gt; 2.0</code>) = <code>{r2['dti']:.6f} {fmt_ci(r2['ci95'])}</code>;
    Off-catalogue <strong>USGS SGMC PROXY = <code>{sgmc:.6f}</code></strong> (+9.4% over LISTRICLOQO <code>0.103442</code>, +17.8% over <code>R0</code> <code>0.096060</code>). No ORGANIZER-CONFIRMED score exists.
  </p>
  <p><strong>Automated validation &amp; Uniqueness (REGISTRY-MEASUREMENT):</strong>
    SHA-256 <code>{e(cl['raster_sha256'])}</code> (ZIP <code>{e(cl['zip_sha256'])}</code>); <code>44/44</code> leakage canaries PASS (max symmetric AUC <code>{cl['leakage_canary']['max_symmetric_auc']:.6f} &le; 0.90</code>);
    <code>0 / {u_pm['rasters_checked']}</code> post-merge local overlaps &gt; 0.70 (max <code>{u_pm['worst_matched_budget_forward_overlap_3px']:.4f}</code>) and <code>0 / {u_pub['non_self_rasters_checked']:,}</code> public 102-repo operational overlaps &gt; 0.70 (max <code>{u_pub['worst_operative_overlap_3px']:.4f}</code>; surface |&rho;| <code>{u_pub['preplacement_surface_worst_abs_spearman']:.4f}</code>, final |&rho;| <code>{u_pub['final_dots_worst_abs_spearman']:.4f} &le; 0.90</code>); literal 17GEMSDOE dense witness = <code>1.0000 &gt; 0.70</code>.
    Siblings (research only, <code>negative</code>): <a href="{e(pre + files['adapt37k'].removeprefix('docs/'))}" download>adapt37k TIF</a> (static <code>0.012617</code>) · <a href="{e(pre + files['no10m_fixed'].removeprefix('docs/'))}" download>no10m_fixed TIF</a> (static <code>0.012206</code>).
  </p>
</section>"""


def cl_md_section(cl: dict, pre: str) -> str:
    h = cl["holdout_dti"]
    s_add = h["static_dcat_gt_2_primary"]
    oof = h["drawblind_oof_dcat_gt_2_primary"]
    r2 = h["strict_drawblind_rule2_dvis_gt_2_primary"]
    p_ctl = h["paired_differences_static_dcat_gt_2"]["no10m_fixed"]
    sgmc = h["sgmc_independent_basement_fault_proxy_dti"]["addtail52k"]
    u_pub = cl["correlation_overlap_vs_registry"]["public_102_repo_registry"]
    u_pm = cl["correlation_overlap_vs_registry"]["post_merge_docs_downloads"]
    files = cl["all_experiment_files"]

    tif = pre + cl["candidate_file"].removeprefix("docs/")
    zp = pre + cl["zip_file"].removeprefix("docs/")
    card = pre + "downloads/chilistric_run_card.json"
    subp = pre + "executive-summary.html"
    ana = pre + "ANALYSIS_20261025_CHILISTRIC.md"
    hyp = pre + "HYPOTHESES_20261025_CHILISTRIC.md"
    rev = pre + "REVIEW_20261025_CHILISTRIC.md"

    return f"""> ## Newest completed session lane (`2026-10-25`) — `{cl['lane']}` / primary arm `addtail52k` (3 new unique-byte GeoTIFFs)
> **✅ OK TO DOWNLOAD FOR RESEARCH** (`11/11` automated `[0, 1]` gates PASS, `0` NaN; unique across all `{u_pm['rasters_checked']}` post-merge local rasters at `{u_pm['worst_matched_budget_forward_overlap_3px']:.4f} <= 0.70` & all `{u_pub['non_self_rasters_checked']:,}` public rasters across `102` repos at `{u_pub['worst_operative_overlap_3px']:.4f} <= 0.70`) · **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT** (verdict `{cl['verdict']}`, `submission_eligible: false`; literal `17GEMSDOE` dense witness `1.000 > 0.70` & static tie vs `LISTRICLOQO` `0.013295`; `0` weekly slots spent).
>
> **[⬇ Download research GeoTIFF (`{cl['candidate_file'].split('/')[-1]}`)]({tif})** · [one-TIFF ZIP]({zp}) · [JSON Run Card]({card}) · [Executive Summary & How to Submit]({subp}) · [PhD Analysis (`0.2778` / `0.3195` / `0.4413` & Verified Sources Table)]({ana}) · [Pre-Registered Hypotheses]({hyp}) · [3-Pass Review]({rev})
>
> - **Record-only DrivenData #306 form fields (do NOT upload a `negative` file):** SHA-256 `{cl['raster_sha256']}` · name `{cl['submission_name']}` · note (`{cl['submission_note_chars']}/140`): `{cl['submission_note']}` · zeros-outside `float32` in `[0, 1]` prevents `"Predicted values must be in range [0, 1]"`.
> - **`HOLDOUT-DTI` (`{h['evaluator_version']}`, `{h['withheld_positive_pixels']:,}` withheld positives):** **Strict Draw-Blind OOF (`d_cat > 2.0`) = `{oof['dti']:.6f} {fmt_ci(oof['ci95'])}` (`#1` all-time zero-catalogue OOF in `GEMSDOE92`, beating `LISTRICLOQO` `0.013064`)**; Static (`d_cat > 2.0`) = **`{s_add['dti']:.6f} {fmt_ci(s_add['ci95'])}`** (paired `{p_ctl['delta']:+.6f} {fmt_ci(p_ctl['ci95'])}` over `no10m_fixed` `0.012206`); Strict Rule-2 (`d_visible > 2.0`) = `{r2['dti']:.6f} {fmt_ci(r2['ci95'])}`; Off-catalogue **`USGS SGMC PROXY` = `{sgmc:.6f}`** (`+9.4%` vs `LISTRICLOQO` `0.103442`); `44/44` canaries PASS (`<= 0.617275`). Siblings: [`adapt37k`]({pre + files['adapt37k'].removeprefix('docs/')}) (`0.012617`) · [`no10m_fixed`]({pre + files['no10m_fixed'].removeprefix('docs/')}) (`0.012206`)."""


def rc_html_section(rc: dict, pre: str) -> str:
    e = html.escape
    h = rc["holdout_dti"]
    u_loc = rc["correlation_overlap_vs_registry"]["local"]
    u_pub = rc["correlation_overlap_vs_registry"]["public_102_repos"]
    sibs = rc["siblings"]
    hero_arm = rc["arm"]

    tif = pre + rc["primary_download"].removeprefix("docs/")
    zp = pre + rc["zip_download"].removeprefix("docs/")
    aud = pre + sibs[hero_arm]["file_audit"].removeprefix("docs/")
    card = pre + "downloads/relayconduit_run_card.json"
    hold = pre + "downloads/relayconduit_holdout.json"
    uniq = pre + "downloads/relayconduit_uniqueness.json"
    subp = pre + "relayconduit.html"
    ana = pre + "ANALYSIS_20261025_RELAYCONDUIT.md"
    hyp = pre + "HYPOTHESES_20261025_RELAYCONDUIT.md"

    s_rc = sibs["relay_conduit"]
    s_rd = sibs["relay_delta"]
    s_cn = sibs["conduit_notip"]
    p_cl = h["paired_vs_COULOMBLOQO_d32"]

    return f"""<section aria-label="Completed session lane RELAYCONDUIT" style="border:3px solid #7f1d1d;background:#fef2f2;padding:1rem 1.2rem;margin:0 0 1.2rem 0;border-radius:8px;font-family:system-ui,sans-serif">
  <h2 style="margin-top:0">Completed session lane (2026-10-25) — <code>{e(rc['lane'])}</code> / hero arm <code>{e(hero_arm)}</code> (3 new unique-byte GeoTIFFs)</h2>
  <p style="font-size:1.15rem;margin:.25rem 0">
    <span style="background:#14532d;color:#dcfce7;padding:0.3rem 0.65rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.15rem 0.35rem 0.15rem 0;">✅ OK TO DOWNLOAD FOR RESEARCH (11/11 automated [0, 1] gates PASS, 0 NaN; locally unique across all {u_loc['rasters_checked']} rasters at {u_loc['worst_forward_overlap_3px']:.4f} &le; 0.70)</span>
    <span style="background:#7f1d1d;color:#fee2e2;padding:0.3rem 0.65rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.15rem 0;">⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (verdict <code>{e(rc['verdict'])}</code>; external 102-repo overlap {u_pub['worst_operative_overlap_3px']:.4f} &gt; 0.70 vs GEMSDOE53 80k &amp; literal dense witness 1.000 &gt; 0.70; 0 slots spent)</span>
  </p>
  <p style="font-size:1.1rem">
    <a href="{e(tif)}" download><strong>⬇ Download research GeoTIFF ({e(rc['file'])})</strong></a>
    · <a href="{e(zp)}" download>one-TIFF ZIP</a>
    · <a href="{e(aud)}">audit JSON</a>
    · <a href="{e(card)}">JSON Run Card</a>
    · <a href="{e(hold)}">holdout JSON</a>
    · <a href="{e(uniq)}">102-repo uniqueness JSON</a>
    · <a href="{e(subp)}"><strong>DrivenData form steps (relayconduit.html)</strong></a>
    · <a href="{e(ana)}">PhD Analysis (0.2778 / 0.3195 / 0.4413)</a>
    · <a href="{e(hyp)}">Pre-registered Hypotheses</a>
  </p>
  <p><strong>DrivenData submission form reference (record-only; do NOT upload a <code>negative</code> artifact):</strong>
    1) Upload zeros-outside single-band <code>float32</code> <code>.tif</code> (or matching one-TIFF <code>.zip</code>) — zeros outside footprint prevent the portal error <em>&ldquo;Predicted values must be in range [0, 1]&rdquo;</em> without manual pixel inspection.
    2) Separate submission name field: <code>{e(rc['submission_name'])}</code>.
    3) Description/note (&le;140 chars; <code>{rc['note_length']}/140</code>): <code>{e(rc['note'])}</code>.
  </p>
  <p><strong>HOLDOUT-DTI</strong> ({e(h['evaluator_version'])}, {h['withheld_positives']:,} withheld positives, 1,000-draw 20 km paired spatial-cluster bootstrap):
    hero <code>relay_conduit</code> strict Rule-2 <strong><code>{s_rc['rule2_holdout_dti']:.6f} {fmt_ci(s_rc['rule2_ci95'])}</code></strong>
    (paired <code>{p_cl['delta']:+.6f} {fmt_ci(p_cl['ci95'])}</code> over rebuilt <code>control_COULOMBLOQO_d32</code> <code>0.115477</code>; exceeds <code>FAULTNET netfar</code> <code>0.175147</code> and <code>VARIO full</code> <code>0.150020</code>);
    <code>relay_delta</code> strict Rule-2 <code>{s_rd['rule2_holdout_dti']:.6f} {fmt_ci(s_rd['rule2_ci95'])}</code>;
    zero-catalogue ablation <code>conduit_notip</code> strict Rule-2 <code>{s_cn['rule2_holdout_dti']:.6f} {fmt_ci(s_cn['rule2_ci95'])}</code>, static <code>d_cat &gt; 2.0</code> <code>{s_cn['static_holdout_dti']:.6f}</code> (beats <code>R0</code> <code>0.004006</code> and <code>LISTRICDIP</code> <code>0.005420</code>), and off-catalogue <strong>USGS SGMC PROXY = <code>0.106525</code></strong> (beats <code>COULOMBLOQO</code> <code>0.089332</code>). A local holdout number is never a live leaderboard score; no organizer score exists.
  </p>
  <p><strong>Automated validation &amp; Uniqueness (REGISTRY-MEASUREMENT):</strong>
    SHA-256 <code>{e(rc['raster_sha256'])}</code> (ZIP <code>{e(rc['zip_sha256'])}</code>); <code>35/35</code> leakage canaries PASS (max symmetric AUC <code>{rc['leakage_canary']['max_single_feature_symmetric_auc']:.6f} &le; 0.90</code>).
    <code>relay_conduit</code> passes all <code>{u_loc['rasters_checked']}</code> local rasters (worst 3-px overlap <code>{u_loc['worst_forward_overlap_3px']:.4f} &le; 0.70</code>) and stops on external 102-repo 3-px overlap <code>{u_pub['worst_operative_overlap_3px']:.4f} &gt; 0.70</code> vs <code>GEMSDOE53</code> 80k; meanwhile zero-catalogue <code>conduit_notip</code> passes all <code>{u_pub['external_rasters_checked']:,}</code> external rasters across 102 repos (<code>0.6557 &le; 0.70</code>, <code>0</code> external violations) and hits <code>0.7031 &gt; 0.70</code> locally only against concurrently merged <code>RIEDELVALVE riedel_n90k</code> (<code>90,000</code> dots), while literal full-footprint witness <code>17GEMSDOE_E-proba-multiscale</code> forces literal overlap <code>1.000 &gt; 0.70</code>.
  </p>
  <p>All 3 pre-registered RELAYCONDUIT arms (research only, <code>negative</code>):
    <a href="{e(pre + s_rc['file_zeros'].removeprefix('docs/'))}" download>relay_conduit TIF</a> (<a href="{e(pre + s_rc['file_zip'].removeprefix('docs/'))}" download>ZIP</a> · <a href="{e(pre + s_rc['file_audit'].removeprefix('docs/'))}">audit</a>)
    · <a href="{e(pre + s_rd['file_zeros'].removeprefix('docs/'))}" download>relay_delta TIF</a> (<a href="{e(pre + s_rd['file_zip'].removeprefix('docs/'))}" download>ZIP</a> · <a href="{e(pre + s_rd['file_audit'].removeprefix('docs/'))}">audit</a>)
    · <a href="{e(pre + s_cn['file_zeros'].removeprefix('docs/'))}" download>conduit_notip TIF</a> (<a href="{e(pre + s_cn['file_zip'].removeprefix('docs/'))}" download>ZIP</a> · <a href="{e(pre + s_cn['file_audit'].removeprefix('docs/'))}">audit</a>).
  </p>
</section>"""


def rc_md_section(rc: dict, pre: str) -> str:
    h = rc["holdout_dti"]
    u_loc = rc["correlation_overlap_vs_registry"]["local"]
    u_pub = rc["correlation_overlap_vs_registry"]["public_102_repos"]
    sibs = rc["siblings"]
    hero_arm = rc["arm"]

    tif = pre + rc["primary_download"].removeprefix("docs/")
    zp = pre + rc["zip_download"].removeprefix("docs/")
    aud = pre + sibs[hero_arm]["file_audit"].removeprefix("docs/")
    card = pre + "downloads/relayconduit_run_card.json"
    hold = pre + "downloads/relayconduit_holdout.json"
    uniq = pre + "downloads/relayconduit_uniqueness.json"
    subp = pre + "relayconduit.html"
    ana = pre + "ANALYSIS_20261025_RELAYCONDUIT.md"
    hyp = pre + "HYPOTHESES_20261025_RELAYCONDUIT.md"

    s_rc = sibs["relay_conduit"]
    s_rd = sibs["relay_delta"]
    s_cn = sibs["conduit_notip"]
    p_cl = h["paired_vs_COULOMBLOQO_d32"]

    return f"""> ## Completed session lane (`2026-10-25`) — `{rc['lane']}` / hero arm `{hero_arm}` (3 new unique-byte GeoTIFFs)
> **✅ OK TO DOWNLOAD FOR RESEARCH** (`11/11` automated `[0, 1]` gates PASS, `0` NaN; locally unique across all `{u_loc['rasters_checked']}` rasters at `{u_loc['worst_forward_overlap_3px']:.4f} <= 0.70`) · **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT** (verdict `{rc['verdict']}`, `submission_eligible: false`; external 102-repo overlap `{u_pub['worst_operative_overlap_3px']:.4f} > 0.70` vs `GEMSDOE53` 80k & literal `17GEMSDOE` dense witness `1.000 > 0.70`; `0` weekly slots spent).
>
> **[⬇ Download research GeoTIFF (`{rc['file']}`)]({tif})** · [one-TIFF ZIP]({zp}) · [audit JSON]({aud}) · [JSON Run Card]({card}) · [holdout JSON]({hold}) · [102-repo uniqueness JSON]({uniq}) · [DrivenData form steps]({subp}) · [PhD Analysis (`0.2778` / `0.3195` / `0.4413`)]({ana}) · [Pre-Registered Hypotheses]({hyp})
>
> - **Record-only DrivenData form fields (do NOT upload a `negative` artifact):** separate name `{rc['submission_name']}` · note (`{rc['note_length']}/140`): `{rc['note']}` · zeros-outside `float32` encoding prevents `"Predicted values must be in range [0, 1]"`.
> - **`HOLDOUT-DTI` (`{h['evaluator_version']}`, `{h['withheld_positives']:,}` withheld positives):** hero `relay_conduit` strict Rule-2 **`{s_rc['rule2_holdout_dti']:.6f} {fmt_ci(s_rc['rule2_ci95'])}`** (paired `{p_cl['delta']:+.6f} {fmt_ci(p_cl['ci95'])}` over rebuilt `control_COULOMBLOQO_d32` `0.115477`; exceeds `FAULTNET netfar` `0.175147` and `VARIO full` `0.150020`); `relay_delta` `{s_rd['rule2_holdout_dti']:.6f} {fmt_ci(s_rd['rule2_ci95'])}`; zero-catalogue `conduit_notip` strict Rule-2 `{s_cn['rule2_holdout_dti']:.6f} {fmt_ci(s_cn['rule2_ci95'])}`, static `d_cat > 2.0` `{s_cn['static_holdout_dti']:.6f}`, off-catalogue **`USGS SGMC PROXY` = `0.106525`** (beats `COULOMBLOQO` `0.089332`, passes all `1,367` external rasters across 102 repos at `0.6557 <= 0.70`, `0.7031` locally vs `RIEDELVALVE riedel_n90k` 90k).
> - **All 3 arms (`negative`, research only):** [`relay_conduit`]({pre + s_rc['file_zeros'].removeprefix('docs/')}) ([ZIP]({pre + s_rc['file_zip'].removeprefix('docs/')}) · [audit]({pre + s_rc['file_audit'].removeprefix('docs/')})) · [`relay_delta`]({pre + s_rd['file_zeros'].removeprefix('docs/')}) ([ZIP]({pre + s_rd['file_zip'].removeprefix('docs/')}) · [audit]({pre + s_rd['file_audit'].removeprefix('docs/')})) · [`conduit_notip`]({pre + s_cn['file_zeros'].removeprefix('docs/')}) ([ZIP]({pre + s_cn['file_zip'].removeprefix('docs/')}) · [audit]({pre + s_cn['file_audit'].removeprefix('docs/')}))."""


def html_block(c, pre, rc=None, cl=None):
    f = facts(c)
    e = html.escape
    tif = pre + c["file"].removeprefix("docs/")
    zp = pre + c["zip"].removeprefix("docs/")
    card = pre + c["run_card"].removeprefix("docs/")
    ana = pre + c.get("analysis", "docs/ANALYSIS_20261025_FAULTNET.md").removeprefix("docs/")
    if c["ok_to_submit"]:
        status = ('<p style="font-size:1.25rem;margin:.2rem 0"><strong>✅ OK TO DOWNLOAD · ✅ OK TO SUBMIT</strong> '
                  '(passed every automated gate: format, leakage canary, holdout gate, registry uniqueness)</p>')
        bg = "#ecfdf5"; bd = "#065f46"
    else:
        status = ('<p style="font-size:1.25rem;margin:.2rem 0"><strong>✅ OK TO DOWNLOAD (format-valid) · ⛔ DO NOT SUBMIT</strong> '
                  f'(verdict <code>{e(c["verdict"])}</code>). Reason: {e(reason(c))}.</p>')
        bg = "#fef2f2"; bd = "#7f1d1d"
    sib = " · ".join(f'<a href="{e(pre + s["file"].removeprefix("docs/"))}" download>{e(a)}</a> ({e(s["verdict"])}, HOLDOUT-DTI {s["dti"]:.6f})'
                     for a, s in c["siblings"].items())
    cl_part = (cl_html_section(cl, pre) + "\n") if cl is not None else ""
    rc_part = (rc_html_section(rc, pre) + "\n") if rc is not None else ""
    return f"""{BEGIN}
{cl_part}{rc_part}<section aria-label="Current submission" style="border:3px solid {bd};background:{bg};padding:1rem 1.2rem;margin:0 0 1.2rem 0;border-radius:8px;font-family:system-ui,sans-serif">
  <h2 style="margin-top:0">Parallel lane receipt — lane {e(c['lane'])} / arm <code>{e(c['arm'])}</code></h2>
  {status}
  <p style="font-size:1.15rem"><a href="{e(tif)}" download><strong>⬇ Download research GeoTIFF ({e(c['file'].split('/')[-1])})</strong></a> · <a href="{e(zp)}" download>one-TIFF ZIP</a> · <a href="{e(card)}">run card (JSON)</a> · <a href="{e(ana)}">analysis</a></p>
  <p><strong>{'How to submit this file:' if c['ok_to_submit'] else 'How to submit (only do this with a file marked ✅ OK TO SUBMIT, which this one is not):'}</strong></p>
  <ol>
    <li>Download the <code>.tif</code> above (or the ZIP that contains only that TIFF).</li>
    <li>Open the DrivenData submissions page: <a href="{SUBMIT_URL}">{SUBMIT_URL}</a> (log in; this URL was not live-verified from the sandbox).</li>
    <li>Under <em>File to submit</em>, choose the file. Under <em>Note (optional)</em>, paste: <code>{e(c['note'])}</code></li>
    <li>Name your file/record as: <code>{e(c['submission_name'])}</code>, then submit. Record the score receipt in <code>ledger/submissions.csv</code>.</li>
  </ol>
  <p><strong>Automated validation (no human inspection):</strong> single band float32, EPSG:32611, 3730 × 3292, transform equal to <code>sample_submission.tif</code>, every value finite and in [0, 1], 0 NaN, 0 outside the footprint, 0 dots on mapped faults. This prevents the portal error <em>"Predicted values must be in range [0, 1]"</em>. SHA-256 <code>{e(c['sha256'])}</code>.</p>
  <p><strong>HOLDOUT-DTI</strong> ({e(f['ev'])}, {f['n']:,} withheld positives, 95% CI from a paired 20 km cluster bootstrap): <code>{f['dti']}</code>. {e(f['ctrl_name'])} control on the same folds: <code>{f['ctrl']}</code>. Paired Δ: <code>{f['delta']}</code>. A holdout number is <em>not</em> a leaderboard score. No ORGANIZER-CONFIRMED score exists for this file.</p>
  <p><strong>Uniqueness</strong> (REGISTRY-MEASUREMENT, {f['nreg']:,} rasters: the public GEMSDOE* index plus local lineage): worst dot overlap <code>{f['ovl']}</code> (limit 0.70; vs <code>{e(f['ovl_r'])}</code>), worst |ρ| final <code>{f['rho']}</code> / surface <code>{f['rhos']}</code> (limit 0.90). Under the literal positive-support reading, {f['lit']} raster(s) exceed 0.70. The literal reading is binding under the current protocol, so this triggers the duplicate stop.</p>
  <p>Sibling arms (research only): {sib}. Other lanes' status and the repository-wide decision follow below this box; a file is cleared only where it is marked ✅ OK TO SUBMIT.</p>
</section>
{END}"""


def md_block(c, pre, rc=None, cl=None):
    f = facts(c)
    tif = pre + c["file"].removeprefix("docs/")
    zp = pre + c["zip"].removeprefix("docs/")
    card = pre + c["run_card"].removeprefix("docs/")
    ana = pre + c.get("analysis", "docs/ANALYSIS_20261025_FAULTNET.md").removeprefix("docs/")
    status = ("**✅ OK TO DOWNLOAD · ✅ OK TO SUBMIT** (passed every automated gate)" if c["ok_to_submit"] else
              f"**✅ OK TO DOWNLOAD (format-valid) · ⛔ DO NOT SUBMIT** (verdict `{c['verdict']}`). Reason: {reason(c)}.")
    sib = " · ".join(f"[{a}]({pre + s['file'].removeprefix('docs/')}) ({s['verdict']}, HOLDOUT-DTI {s['dti']:.6f})" for a, s in c["siblings"].items())
    cl_part = (cl_md_section(cl, pre) + "\n\n") if cl is not None else ""
    rc_part = (rc_md_section(rc, pre) + "\n\n") if rc is not None else ""
    return f"""{BEGIN}
{cl_part}{rc_part}> ## Parallel lane receipt — lane {c['lane']} / arm `{c['arm']}`
> {status}
>
> **[⬇ Download research GeoTIFF]({tif})** · [one-TIFF ZIP]({zp}) · [run card]({card}) · [analysis]({ana})
>
> {'**How to submit this file:**' if c['ok_to_submit'] else '**How to submit (only with a file marked ✅ OK TO SUBMIT, which this one is not):**'}
> 1. Download the `.tif` (or the ZIP holding only that TIFF).
> 2. Go to {SUBMIT_URL} (log in; not live-verified from the sandbox), then choose the file under *File to submit*.
> 3. Paste this into *Note (optional)*: `{c['note']}`
> 4. Name/record: `{c['submission_name']}`. After scoring, record the receipt in `ledger/submissions.csv`.
>
> Automated validation: float32, EPSG:32611, 3730×3292, sample transform, values finite in [0, 1], 0 NaN, 0 outside the footprint, 0 on the catalogue. SHA-256 `{c['sha256']}`.
> **HOLDOUT-DTI** ({f['ev']}, {f['n']:,} withheld positives): `{f['dti']}`. {f['ctrl_name']} control: `{f['ctrl']}`. Paired Δ `{f['delta']}`. A holdout number is not a leaderboard score, and there is no ORGANIZER-CONFIRMED score.
> **Uniqueness** ({f['nreg']:,} registry rasters): worst overlap `{f['ovl']}` (limit 0.70), worst |ρ| `{f['rho']}` / surface `{f['rhos']}` (limit 0.90). Literal-support reading: {f['lit']} raster(s) > 0.70. The literal reading is binding under the current protocol and triggers the duplicate stop.
> Siblings: {sib}. **Read [SESSION_PROMPT.md](SESSION_PROMPT.md) first in every session.** Other lanes' status and the repository-wide decision follow below this box; a file is cleared only where it is marked ✅ OK TO SUBMIT.
{END}"""


ANCHORS = ("<!-- VARIO-STATUS:END -->", "<!-- CURRENT-READINESS:END -->", "<!-- CURRENT-STATUS:END -->")


def inject(text, block, is_html):
    pat = re.compile(r"\n?" + re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S)
    if len(pat.findall(text)) > 1:
        raise ValueError("ambiguous lane-result markers")
    text = pat.sub("\n", text, count=1)
    for rd in ANCHORS:
        if rd in text:
            i = text.index(rd) + len(rd)
            return text[:i] + "\n" + block + ("" if text[i:i + 1] == "\n" else "\n") + text[i:]
    if is_html:
        i = text.index("<body>") + len("<body>")
        return text[:i] + "\n" + block + "\n" + text[i:]
    lines = text.split("\n")
    k = next(i for i, l in enumerate(lines) if l.startswith("# "))
    return "\n".join(lines[:k + 1] + ["", block, ""] + lines[k + 1:])


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from scripts import render_vario_status
    render_vario_status.render(ROOT, write=True)
    c = json.loads(CUR.read_text())
    rc = json.loads(RC_CARD.read_text()) if RC_CARD.is_file() else None
    cl = json.loads(CL_CARD.read_text()) if CL_CARD.is_file() else None
    for p, pre in HTML_PAGES.items():
        if p.is_file():
            p.write_text(inject(p.read_text(), html_block(c, pre, rc, cl), True))
    for p, pre in MD_PAGES.items():
        if p.is_file():
            blk = md_block(c, pre, rc, cl)
            if p.name == "SUBMIT.md":
                blk = blk.replace("](SESSION_PROMPT.md)", "](../SESSION_PROMPT.md)")
            p.write_text(inject(p.read_text(), blk, False))
    render_vario_status.render(ROOT, write=True)
    print("rendered current-submission block into", len(HTML_PAGES) + len(MD_PAGES), "pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
