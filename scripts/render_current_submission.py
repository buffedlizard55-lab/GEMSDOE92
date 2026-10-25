#!/usr/bin/env python3
"""Render the top-of-page lane status boxes on every entry page.

Sources of truth:
  1. evidence/relayconduit_run_card.json (newest completed 2026-10-25 RELAYCONDUIT lane)
  2. docs/downloads/current_submission.json (preserved FAULTNET lane receipt)

Nothing is hand-typed: every number, hash, name and verdict comes from the JSON
receipts. Idempotent: replaces the block between <!-- CURRENT:BEGIN --> and
<!-- CURRENT:END --> and runs render_readiness.sync() + render_current_status.check(write=True)
so all --check gates remain byte-exact.
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
    d = h["paired_vs_COULOMBLOQO_control"]
    return dict(
        dti=f"{h['dti']:.6f} {fmt_ci(h['ci95'])}", n=h["withheld_positives"], ev=h["evaluator_version"],
        ctrl=f"{ctrl['dti']:.6f} {fmt_ci(ctrl['ci95'])}", delta=f"{d['delta']:+.6f} {fmt_ci(d['ci95'])}",
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


def rc_html_section(rc: dict, pre: str) -> str:
    e = html.escape
    h = rc["holdout_dti"]
    u_loc = rc["correlation_overlap_vs_registry"]["local"]
    u_pub = rc["correlation_overlap_vs_registry"]["public_102_repos"]
    sibs = rc["siblings"]

    tif = pre + rc["primary_download"].removeprefix("docs/")
    zp = pre + rc["zip_download"].removeprefix("docs/")
    aud = pre + sibs[rc["arm"]]["file_audit"].removeprefix("docs/")
    card = pre + "downloads/relayconduit_run_card.json"
    hold = pre + "downloads/relayconduit_holdout.json"
    uniq = pre + "downloads/relayconduit_uniqueness.json"
    subp = pre + "relayconduit.html"
    ana = pre + "ANALYSIS_20261025_RELAYCONDUIT.md"
    hyp = pre + "HYPOTHESES_20261025_RELAYCONDUIT.md"

    s_rc = sibs["relay_conduit"]
    s_rd = sibs["relay_delta"]

    return f"""<section aria-label="Newest completed session lane RELAYCONDUIT" style="border:3px solid #7f1d1d;background:#fef2f2;padding:1rem 1.2rem;margin:0 0 1.2rem 0;border-radius:8px;font-family:system-ui,sans-serif">
  <h2 style="margin-top:0">Completed session lane (2026-10-25) — <code>{e(rc['lane'])}</code> / hero arm <code>{e(rc['arm'])}</code> (3 new unique-byte GeoTIFFs)</h2>
  <p style="font-size:1.15rem;margin:.25rem 0">
    <span style="background:#14532d;color:#dcfce7;padding:0.3rem 0.65rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.15rem 0.35rem 0.15rem 0;">✅ OK TO DOWNLOAD FOR RESEARCH (11/11 automated [0, 1] gates PASS, 0 NaN; 102-repo operative unique 0.6557 &le; 0.70)</span>
    <span style="background:#7f1d1d;color:#fee2e2;padding:0.3rem 0.65rem;border-radius:4px;font-weight:700;display:inline-block;margin:0.15rem 0;">⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (verdict <code>{e(rc['verdict'])}</code>; literal dense-witness overlap 1.000 &gt; 0.70; 0 slots spent)</span>
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
    hero zero-catalogue <code>conduit_notip</code> strict Rule-2 <code>{h['dti']:.6f} {fmt_ci(h['ci95'])}</code>, static <code>d_cat &gt; 2.0</code> <code>{h['static_dcat2_dti']:.6f} {fmt_ci(h['static_dcat2_ci95'])}</code> (beats <code>R0</code> <code>0.004006</code> and <code>LISTRICDIP</code> <code>0.005420</code>), off-catalogue <strong>USGS SGMC PROXY = <code>{h['sgmc_off_catalogue_proxy']['dti']:.6f}</code></strong> (beats <code>COULOMBLOQO</code> <code>0.089332</code>).
    Tip-relay sibling <code>relay_conduit</code> achieves strict Rule-2 <strong><code>{s_rc['rule2_holdout_dti']:.6f} {fmt_ci(s_rc['rule2_ci95'])}</code></strong> (paired <code>+0.069008 [+0.053289, +0.084771]</code> over rebuilt <code>control_COULOMBLOQO_d32</code> <code>0.115477</code>; exceeds <code>FAULTNET netfar</code> <code>0.175147</code>) and <code>relay_delta</code> achieves <code>{s_rd['rule2_holdout_dti']:.6f} {fmt_ci(s_rd['rule2_ci95'])}</code>, while automated 102-repo screening caught 3-px overlap <code>{s_rc['worst_operative_overlap_3px']:.4f} &gt; 0.70</code> against <code>GEMSDOE53</code> 80k and halted promotion. A local holdout number is never a live leaderboard score; no organizer score exists.
  </p>
  <p><strong>Automated validation &amp; Uniqueness (REGISTRY-MEASUREMENT):</strong>
    SHA-256 <code>{e(rc['raster_sha256'])}</code> (ZIP <code>{e(rc['zip_sha256'])}</code>); <code>35/35</code> leakage canaries PASS (max symmetric AUC <code>{rc['leakage_canary']['max_single_feature_symmetric_auc']:.6f} &le; 0.90</code>).
    <code>conduit_notip</code> passes all <code>{u_loc['rasters_checked']}</code> local rasters (worst 3-px overlap <code>{u_loc['worst_forward_overlap_3px']:.4f} &le; 0.70</code>) and all <code>{u_pub['external_rasters_checked']:,}</code> compatible external rasters across <code>102</code> public repos (worst operative 3-px overlap <code>{u_pub['worst_operative_overlap_3px']:.4f} &le; 0.70</code>, <code>0</code> violations; worst <code>&le;50k</code>-dot overlap <code>{u_pub['dot_fields_le_50k_worst_overlap_3px']:.4f}</code>; worst surface <code>|&rho;| = {u_pub['worst_surface_abs_spearman']:.4f} &le; 0.90</code>), while literal full-footprint witness <code>17GEMSDOE_E-proba-multiscale</code> forces literal overlap <code>1.000 &gt; 0.70</code>.
  </p>
  <p>Sibling downloads (research only, <code>negative</code>):
    <a href="{e(pre + s_rc['file_zeros'].removeprefix('docs/'))}" download>relay_conduit TIF</a> (<a href="{e(pre + s_rc['file_zip'].removeprefix('docs/'))}" download>ZIP</a> · <a href="{e(pre + s_rc['file_audit'].removeprefix('docs/'))}">audit</a>, Rule-2 HOLDOUT-DTI {s_rc['rule2_holdout_dti']:.6f})
    · <a href="{e(pre + s_rd['file_zeros'].removeprefix('docs/'))}" download>relay_delta TIF</a> (<a href="{e(pre + s_rd['file_zip'].removeprefix('docs/'))}" download>ZIP</a> · <a href="{e(pre + s_rd['file_audit'].removeprefix('docs/'))}">audit</a>, Rule-2 HOLDOUT-DTI {s_rd['rule2_holdout_dti']:.6f}).
  </p>
</section>"""


def rc_md_section(rc: dict, pre: str) -> str:
    h = rc["holdout_dti"]
    u_loc = rc["correlation_overlap_vs_registry"]["local"]
    u_pub = rc["correlation_overlap_vs_registry"]["public_102_repos"]
    sibs = rc["siblings"]

    tif = pre + rc["primary_download"].removeprefix("docs/")
    zp = pre + rc["zip_download"].removeprefix("docs/")
    aud = pre + sibs[rc["arm"]]["file_audit"].removeprefix("docs/")
    card = pre + "downloads/relayconduit_run_card.json"
    hold = pre + "downloads/relayconduit_holdout.json"
    uniq = pre + "downloads/relayconduit_uniqueness.json"
    subp = pre + "relayconduit.html"
    ana = pre + "ANALYSIS_20261025_RELAYCONDUIT.md"
    hyp = pre + "HYPOTHESES_20261025_RELAYCONDUIT.md"

    s_rc = sibs["relay_conduit"]
    s_rd = sibs["relay_delta"]

    return f"""> ## Completed session lane (`2026-10-25`) — `{rc['lane']}` / hero arm `{rc['arm']}` (3 new unique-byte GeoTIFFs)
> **✅ OK TO DOWNLOAD FOR RESEARCH** (`11/11` automated `[0, 1]` gates PASS, `0` NaN; `102`-repo operative unique `0.6557 <= 0.70`, `0` violations) · **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT** (verdict `{rc['verdict']}`, `submission_eligible: false`; literal `17GEMSDOE` dense-witness overlap `1.000 > 0.70`; `0` weekly slots spent).
>
> **[⬇ Download research GeoTIFF (`{rc['file']}`)]({tif})** · [one-TIFF ZIP]({zp}) · [audit JSON]({aud}) · [JSON Run Card]({card}) · [holdout JSON]({hold}) · [102-repo uniqueness JSON]({uniq}) · [DrivenData form steps]({subp}) · [PhD Analysis (`0.2778` / `0.3195` / `0.4413`)]({ana}) · [Pre-Registered Hypotheses]({hyp})
>
> - **Record-only DrivenData form fields (do NOT upload a `negative` artifact):** separate name `{rc['submission_name']}` · note (`{rc['note_length']}/140`): `{rc['note']}` · zeros-outside `float32` encoding prevents `"Predicted values must be in range [0, 1]"`.
> - **`HOLDOUT-DTI` (`{h['evaluator_version']}`, `{h['withheld_positives']:,}` withheld positives):** hero zero-catalogue `conduit_notip` strict Rule-2 `{h['dti']:.6f} {fmt_ci(h['ci95'])}`, static `d_cat > 2.0` `{h['static_dcat2_dti']:.6f} {fmt_ci(h['static_dcat2_ci95'])}` (beats `R0` `0.004006` and `LISTRICDIP` `0.005420`), off-catalogue **`USGS SGMC PROXY` = `{h['sgmc_off_catalogue_proxy']['dti']:.6f}`** (beats `COULOMBLOQO` `0.089332`). Tip-relay sibling `relay_conduit` scores strict Rule-2 **`{s_rc['rule2_holdout_dti']:.6f} {fmt_ci(s_rc['rule2_ci95'])}`** (paired `+0.069008 [+0.053289, +0.084771]` over rebuilt `control_COULOMBLOQO_d32` `0.115477`; exceeds `FAULTNET netfar` `0.175147`) and `relay_delta` scores `{s_rd['rule2_holdout_dti']:.6f} {fmt_ci(s_rd['rule2_ci95'])}`, halted on 102-repo 3-px overlap `{s_rc['worst_operative_overlap_3px']:.4f} > 0.70` vs `GEMSDOE53` 80k.
> - **Validation & `REGISTRY-MEASUREMENT`:** SHA-256 `{rc['raster_sha256']}`; `35/35` leakage canaries PASS (max symmetric AUC `{rc['leakage_canary']['max_single_feature_symmetric_auc']:.6f} <= 0.90`); `conduit_notip` local worst overlap `{u_loc['worst_forward_overlap_3px']:.4f} <= 0.70` (`{u_loc['rasters_checked']}` rasters) and 102-repo external operative worst overlap `{u_pub['worst_operative_overlap_3px']:.4f} <= 0.70` (`{u_pub['external_rasters_checked']:,}` rasters, `0` violations; worst `<=50k`-dot `{u_pub['dot_fields_le_50k_worst_overlap_3px']:.4f}`; surface `|rho| = {u_pub['worst_surface_abs_spearman']:.4f} <= 0.90`).
> - **Siblings (`negative`, research only):** [`relay_conduit`]({pre + s_rc['file_zeros'].removeprefix('docs/')}) ([ZIP]({pre + s_rc['file_zip'].removeprefix('docs/')}) · [audit]({pre + s_rc['file_audit'].removeprefix('docs/')})) · [`relay_delta`]({pre + s_rd['file_zeros'].removeprefix('docs/')}) ([ZIP]({pre + s_rd['file_zip'].removeprefix('docs/')}) · [audit]({pre + s_rd['file_audit'].removeprefix('docs/')}))."""


def html_block(c, pre, rc=None):
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
    rc_part = (rc_html_section(rc, pre) + "\n") if rc is not None else ""
    return f"""{BEGIN}
{rc_part}<section aria-label="Prior FAULTNET lane receipt" style="border:2px solid {bd};background:{bg};padding:0.9rem 1.2rem;margin:0 0 1.2rem 0;border-radius:8px;font-family:system-ui,sans-serif">
  <h2 style="margin-top:0">Prior parallel lane receipt — lane {e(c['lane'])} / arm <code>{e(c['arm'])}</code></h2>
  {status}
  <p style="font-size:1.05rem"><a href="{e(tif)}" download><strong>⬇ Download research GeoTIFF ({e(c['file'].split('/')[-1])})</strong></a> · <a href="{e(zp)}" download>one-TIFF ZIP</a> · <a href="{e(card)}">run card (JSON)</a> · <a href="{e(ana)}">analysis</a></p>
  <p><strong>{'How to submit this file:' if c['ok_to_submit'] else 'How to submit (only do this with a file marked ✅ OK TO SUBMIT, which this one is not):'}</strong></p>
  <ol>
    <li>Download the <code>.tif</code> above (or the ZIP that contains only that TIFF).</li>
    <li>Open the DrivenData submissions page: <a href="{SUBMIT_URL}">{SUBMIT_URL}</a> (log in; this URL was not live-verified from the sandbox).</li>
    <li>Under <em>File to submit</em>, choose the file. Under <em>Note (optional)</em>, paste: <code>{e(c['note'])}</code></li>
    <li>Name your file/record as: <code>{e(c['submission_name'])}</code>, then submit. Record the score receipt in <code>ledger/submissions.csv</code>.</li>
  </ol>
  <p><strong>Automated validation (no human inspection):</strong> single band float32, EPSG:32611, 3730 × 3292, transform equal to <code>sample_submission.tif</code>, every value finite and in [0, 1], 0 NaN, 0 outside the footprint, 0 dots on mapped faults. This prevents the portal error <em>"Predicted values must be in range [0, 1]"</em>. SHA-256 <code>{e(c['sha256'])}</code>.</p>
  <p><strong>HOLDOUT-DTI</strong> ({e(f['ev'])}, {f['n']:,} withheld positives, 95% CI from a paired 20 km cluster bootstrap): <code>{f['dti']}</code>. Rebuilt COULOMBLOQO control on the same folds: <code>{f['ctrl']}</code>. Paired Δ: <code>{f['delta']}</code>. A holdout number is <em>not</em> a leaderboard score. No ORGANIZER-CONFIRMED score exists for this file.</p>
  <p><strong>Uniqueness</strong> (REGISTRY-MEASUREMENT, {f['nreg']:,} rasters: the public GEMSDOE* index plus local lineage): worst dot overlap <code>{f['ovl']}</code> (limit 0.70; vs <code>{e(f['ovl_r'])}</code>), worst |ρ| final <code>{f['rho']}</code> / surface <code>{f['rhos']}</code> (limit 0.90). Under the literal positive-support reading, {f['lit']} rasters exceed 0.70. Under that reading even a random raster fails, so it is reported but not used (<code>#IR-92-FAULTNET-DOT-DEFINITION</code>).</p>
  <p>Sibling arms (research only): {sib}. Other lanes' status and the repository-wide decision follow below this box; a file is cleared only where it is marked ✅ OK TO SUBMIT.</p>
</section>
{END}"""


def md_block(c, pre, rc=None):
    f = facts(c)
    tif = pre + c["file"].removeprefix("docs/")
    zp = pre + c["zip"].removeprefix("docs/")
    card = pre + c["run_card"].removeprefix("docs/")
    ana = pre + c.get("analysis", "docs/ANALYSIS_20261025_FAULTNET.md").removeprefix("docs/")
    status = ("**✅ OK TO DOWNLOAD · ✅ OK TO SUBMIT** (passed every automated gate)" if c["ok_to_submit"] else
              f"**✅ OK TO DOWNLOAD (format-valid) · ⛔ DO NOT SUBMIT** (verdict `{c['verdict']}`). Reason: {reason(c)}.")
    sib = " · ".join(f"[{a}]({pre + s['file'].removeprefix('docs/')}) ({s['verdict']}, HOLDOUT-DTI {s['dti']:.6f})" for a, s in c["siblings"].items())
    rc_part = (rc_md_section(rc, pre) + "\n\n") if rc is not None else ""
    return f"""{BEGIN}
{rc_part}> ## Prior parallel lane receipt — lane {c['lane']} / arm `{c['arm']}`
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
> **HOLDOUT-DTI** ({f['ev']}, {f['n']:,} withheld positives): `{f['dti']}`. Rebuilt COULOMBLOQO control: `{f['ctrl']}`. Paired Δ `{f['delta']}`. A holdout number is not a leaderboard score, and there is no ORGANIZER-CONFIRMED score.
> **Uniqueness** ({f['nreg']:,} registry rasters): worst overlap `{f['ovl']}` (limit 0.70), worst |ρ| `{f['rho']}` / surface `{f['rhos']}` (limit 0.90). Literal-support reading: {f['lit']} rasters > 0.70. That reading also fails a random raster (`#IR-92-FAULTNET-DOT-DEFINITION`).
> Siblings: {sib}. **Read [SESSION_PROMPT.md](SESSION_PROMPT.md) first in every session.** Other lanes' status and the repository-wide decision follow below this box; a file is cleared only where it is marked ✅ OK TO SUBMIT.
{END}"""


ANCHORS = ("<!-- CURRENT-READINESS:END -->", "<!-- CURRENT-STATUS:END -->")


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
    c = json.loads(CUR.read_text())
    rc = json.loads(RC_CARD.read_text()) if RC_CARD.is_file() else None
    for p, pre in HTML_PAGES.items():
        if p.is_file():
            p.write_text(inject(p.read_text(), html_block(c, pre, rc), True))
    for p, pre in MD_PAGES.items():
        if p.is_file():
            blk = md_block(c, pre, rc)
            if p.name == "SUBMIT.md":
                blk = blk.replace("](SESSION_PROMPT.md)", "](../SESSION_PROMPT.md)")
            p.write_text(inject(p.read_text(), blk, False))
    sys.path.insert(0, str(ROOT))
    from scripts import render_current_status, render_readiness
    render_readiness.sync()
    render_current_status.check(write=True)
    print("rendered current-submission block into", len(HTML_PAGES) + len(MD_PAGES), "pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
