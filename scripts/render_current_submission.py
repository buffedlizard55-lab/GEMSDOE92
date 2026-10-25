#!/usr/bin/env python3
"""Render the historical lane-result box beneath the authoritative decision.

The alias ``docs/downloads/current_submission.json`` is checked against the
freshly byte-validated ``readiness.json`` before writing any page. It can NEVER
authorize a slot on its own. Idempotent: replaces the block between
<!-- CURRENT:BEGIN --> and <!-- CURRENT:END --> or inserts it right after <body>
(HTML) / after the first H1 line (Markdown).
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CUR = ROOT / "docs" / "downloads" / "current_submission.json"
SUBMIT_URL = "https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/"
BEGIN, END = "<!-- CURRENT:BEGIN -->", "<!-- CURRENT:END -->"
HTML_PAGES = {  # page -> prefix from the page to the repo root
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
        ctrl_name=ctrl.get('name', 'control'), ctrl=f"{ctrl['dti']:.6f} {fmt_ci(ctrl['ci95'])}",
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


def html_block(c, pre):
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
    return f"""{BEGIN}
<section aria-label="Current submission" style="border:3px solid {bd};background:{bg};padding:1rem 1.2rem;margin:0 0 1.2rem 0;border-radius:8px;font-family:system-ui,sans-serif">
  <h2 style="margin-top:0">Newest lane result — lane {e(c['lane'])} / arm <code>{e(c['arm'])}</code></h2>
  {status}
  <p style="font-size:1.15rem"><a href="{e(tif)}" download><strong>⬇ Download the GeoTIFF ({e(c['file'].split('/')[-1])})</strong></a> · <a href="{e(zp)}" download>one-TIFF ZIP</a> · <a href="{e(card)}">run card (JSON)</a> · <a href="{e(ana)}">analysis</a></p>
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


def md_block(c, pre):
    f = facts(c)
    tif = pre + c["file"].removeprefix("docs/")
    zp = pre + c["zip"].removeprefix("docs/")
    card = pre + c["run_card"].removeprefix("docs/")
    ana = pre + c.get("analysis", "docs/ANALYSIS_20261025_FAULTNET.md").removeprefix("docs/")
    status = ("**✅ OK TO DOWNLOAD · ✅ OK TO SUBMIT** (passed every automated gate)" if c["ok_to_submit"] else
              f"**✅ OK TO DOWNLOAD (format-valid) · ⛔ DO NOT SUBMIT** (verdict `{c['verdict']}`). Reason: {reason(c)}.")
    sib = " · ".join(f"[{a}]({pre + s['file'].removeprefix('docs/')}) ({s['verdict']}, HOLDOUT-DTI {s['dti']:.6f})" for a, s in c["siblings"].items())
    return f"""{BEGIN}
> ## Newest lane result — lane {c['lane']} / arm `{c['arm']}`
> {status}
>
> **[⬇ Download the GeoTIFF]({tif})** · [one-TIFF ZIP]({zp}) · [run card]({card}) · [analysis]({ana})
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


# Shared status panels that must stay first on a page (scripts/render_readiness.py,
# scripts/render_current_status.py). The lane-result block always sits right after them.
ANCHORS = ("<!-- CURRENT-READINESS:END -->", "<!-- CURRENT-STATUS:END -->")


def inject(text, block, is_html):
    if (text.count(BEGIN) != text.count(END) or text.count(BEGIN) > 1
            or (BEGIN in text and text.index(END) < text.index(BEGIN))):
        raise ValueError('missing, duplicated or reversed lane-result markers')
    pat = re.compile(r"\n?" + re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S)
    text = pat.sub("\n", text, count=1)
    for rd in ANCHORS:
        if rd in text:
            i = text.index(rd) + len(rd)
            return text[:i].rstrip("\n") + "\n" + block + "\n\n" + text[i:].lstrip("\n")
    if is_html:
        i = text.index("<body>") + len("<body>")
        return text[:i] + "\n" + block + "\n" + text[i:].lstrip("\n")
    lines = text.split("\n")
    k = next(i for i, l in enumerate(lines) if l.startswith("# "))
    # A previous implementation added two blank lines on every run for the
    # stand-alone Markdown guide. Normalize only the generated block boundary.
    tail = "\n".join(lines[k + 1:]).lstrip("\n")
    return "\n".join(lines[:k + 1]) + "\n\n" + block + "\n\n" + tail


def main() -> int:
    from gems.status_contract import alias_errors
    from scripts.render_readiness import build_status
    status = build_status(ROOT)
    c = json.loads(CUR.read_text())
    public = json.loads((ROOT / 'docs/downloads/review797e_run_card.json').read_text())
    published = json.loads((ROOT / 'docs/downloads/readiness.json').read_text())
    errors = alias_errors(status, c, public)
    if published != status:
        errors.append('readiness.json differs from freshly validated bytes')
    if errors:
        raise ValueError('cannot render disputed submission status: ' + '; '.join(errors))
    # Pre-compute *every* edit: a malformed later page must never leave half the
    # entry points refreshed and half advertising an old primary.
    edits = {}
    for p, pre in HTML_PAGES.items():
        if p.is_file():
            edits[p] = inject(p.read_text(), html_block(c, pre), True)
    for p, pre in MD_PAGES.items():
        if p.is_file():
            blk = md_block(c, pre)
            if p.name == "SUBMIT.md":
                blk = blk.replace("](SESSION_PROMPT.md)", "](../SESSION_PROMPT.md)")
            edits[p] = inject(p.read_text(), blk, False)
    for p, content in edits.items():
        p.write_text(content)
    # Let the shared page renderers normalise layout so their --check gates stay green
    # (they keep this block directly after their own panels).
    sys.path.insert(0, str(ROOT))
    from scripts import render_current_status, render_readiness
    render_readiness.sync()
    render_current_status.check(write=True)
    print("rendered current-submission block into", len(HTML_PAGES) + len(MD_PAGES), "pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
