#!/usr/bin/env python3
"""Render docs/index.html, docs/executive-summary.html, docs/SUBMIT.html and docs/submit.html.

Every status line is rendered from docs/downloads/<variant>-audit.json and evidence/lcs_run_card.json
(which scripts/make_lcs_audit.py derived from evidence through gems.verdict / gems.uniqueness_policy).
Nothing about eligibility is typed here.  scripts/check_site.py re-derives the same statuses from the
evidence and fails closed if a page disagrees.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DL = DOCS / "downloads"
e = html.escape

OFFICIAL = [
    ("Competition page", "https://www.drivendata.org/competitions/306/competition-doe-gems/"),
    ("Problem description + metric (page 967)", "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"),
    ("Submit form (login)", "https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/"),
    ("Public leaderboard", "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"),
    ("Official rules (NLR/TP-5700-96647)", "https://docs.nlr.gov/docs/fy26osti/96647.pdf"),
    ("Reference solution (U-Net, DrivenData)", "https://github.com/drivendataorg/gems-prize-reference-solution"),
    ("Forum: known faults are masked (11516)", "https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516"),
    ("Forum: what counts as a new fault (11536)", "https://community.drivendata.org/t/where-do-you-draw-the-line/11536"),
    ("Forum: leaderboard is one pooled Tversky (11550)", "https://community.drivendata.org/t/leaderboard-aggregation-pooled-over-public-test-pixels-or-mean-of-per-chunk-scores/11550"),
    ("Forum: final-round rules (11556)", "https://community.drivendata.org/t/questions-about-the-final-round-rules/11556"),
    ("Forum: truth sources not disclosed (11527)", "https://community.drivendata.org/t/how-were-the-new-test-faults-identified-data-sources-and-fault-types/11527"),
    ("Forum: 3 submissions per week (11553)", "https://community.drivendata.org/t/submission-amount-question/11553"),
    ("GeoDAWN data release (USGS)", "https://doi.org/10.5066/P93LGLVQ"),
]


def load():
    rc = json.loads((ROOT / "evidence" / "lcs_run_card.json").read_text(encoding="utf-8"))
    audit_path = next(DL.glob("GEMSDOE92-lcs-consensus-*-audit.json"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    return rc, audit


def fmt(x, nd=3):
    return "n/a" if x is None else f"{x:.{nd}f}"


def tier_rows(rc):
    names = {"S": "S — previous submissions (operator-scored rasters)",
             "L": "L — every non-blanket registry raster (halo &lt; 50 % of footprint)",
             "T": "T — literal rule: ALL registry rasters incl. blankets"}
    rows = []
    for t in "SLT":
        x = rc["registry"]["tiers"][t]
        s, f = x["surface"], x["final"]
        mark = "✅ pass" if x["passed"] else "⛔ fail"
        decisive = " <strong>(decisive)</strong>" if t == rc["registry"]["policy"]["decisive_tier"] else ""
        rows.append(
            f"<tr><td>{names[t]}{decisive}</td><td>{f['n_rasters']}</td>"
            f"<td>{fmt(s['max_forward_overlap'])} / {s['n_over_0_70']}</td><td>{fmt(f['max_forward_overlap'])} / {f['n_over_0_70']}</td>"
            f"<td>{fmt(f['max_abs_spearman'])}</td><td>{mark}</td></tr>")
    return "\n".join(rows)


def holdout_rows(rc):
    h = rc["holdout"]
    order = ["LCS", "R0", "RELIEF_p10_holdout_best", "LCS_uncapped_research", "RANDOM_spaced"]
    label = {"LCS": "<strong>LCS (this file)</strong>", "R0": "parent R0", "RELIEF_p10_holdout_best": "RELIEF p10 (repo holdout best)",
             "LCS_uncapped_research": "LCS uncapped (research arm)", "RANDOM_spaced": "random spaced control"}
    rows = []
    for k in order:
        if k in h["scores"]:
            v = h["scores"][k]
            rows.append(f"<tr><td>{label[k]}</td><td>{v['dti']:.6f}</td><td>[{v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}]</td></tr>")
    return "\n".join(rows)


def status_blocks(rc):
    st = rc["status"]
    file_ = rc["name"]
    ok_dl = ('<div class="status status-ok"><strong>✅ OK TO DOWNLOAD</strong><br>All 10 MUST format gates pass on the bytes served '
             '(strict 3 px catalogue distance): one float32 band · EPSG:32611 · 3730 × 3292 · template transform · every value finite in [0, 1] · '
             'zeros outside the footprint · no dot on or within 3 px of a mapped fault · sha256 recorded. The portal error '
             '<code>Predicted values must be in range [0, 1]</code> cannot be triggered by this file.</div>') if st["ok_to_download"] else \
        '<div class="status status-warn"><strong>⛔ NOT OK TO DOWNLOAD</strong><br>A format gate failed — see the audit receipt.</div>'
    if st["ok_to_submit"]:
        tl = rc["registry"]["tiers"]["L"]
        dec = rc["registry"]["policy"]["decisive_tier"]
        if tl["passed"]:
            l_txt = f"It also passes Tier L (all {tl['final']['n_rasters']} non-blanket registry rasters, both phases)."
        else:
            l_txt = (f"Against the {tl['final']['n_rasters']} non-blanket registry rasters the <em>final dots</em> pass (max overlap {fmt(tl['final']['max_forward_overlap'])}); "
                     f"the pre-placement <em>surface</em> (a {rc['registry'].get('surface_support_pixels', 0):,}-pixel candidate pool) overlaps {tl['surface']['n_over_0_70']} very large rasters above 0.70 "
                     f"(max {fmt(tl['surface']['max_forward_overlap'])}), so Tier L fails on that phase — shown in the table.")
        lit = ("" if st["literal_registry_rule_passed"] else
               " It does <em>not</em> clear the literal all-registry rule (Tier T), which no file can — a random file fails it against "
               "dozens of rasters: see the table and <a href=\"UNIQUENESS_POLICY_20261024.md\">why</a>.")
        ok_sub = ('<div class="status status-ok"><strong>✅ OK TO SUBMIT</strong><br>Valid for the portal <em>and</em> not a copy of any previous submission: '
                  f'overlap ≤ 0.70 and |Spearman| ≤ 0.90 against every operator-scored raster, both phases (decisive Tier {e(dec)}). {l_txt}{lit} '
                  'Leakage canary passes. This is a validity and non-duplication clearance — <strong>not a score and not a recommendation</strong>.</div>')
    else:
        ok_sub = ('<div class="status status-warn"><strong>⛔ NOT OK TO SUBMIT</strong><br>Blocked by: ' + e("; ".join(st["blocking_reasons"])) + '.</div>')
    v = rc["verdict"]
    hb = rc["holdout"]["lcs_minus_best"]
    if v == "promote":
        slot = ('<div class="status status-ok"><strong>🟢 SLOT VERDICT: promote</strong><br>HOLDOUT-DTI beats the repository holdout best with a paired 95 % CI entirely above 0. '
                'A human selector still decides within the 3-per-week cap.</div>')
    else:
        slot = ('<div class="status status-hold"><strong>🟡 SLOT VERDICT: negative (pre-registered rule)</strong><br>'
                f'HOLDOUT-DTI minus the repository holdout best (RELIEF p10): {hb["delta"]:+.6f} '
                f'[{hb["ci95"][0]:+.6f}, {hb["ci95"][1]:+.6f}] — the paired CI is not entirely above 0, so the protocol does not recommend spending a weekly slot on it. '
                + ('HOLDOUT-DTI of this file is exactly 0 in every fold <em>by construction</em>: the hide-and-recover truth is mapped fault pixels and every dot here is &gt; 3 px from every mapped fault, so no dot can touch a withheld pixel — the instrument cannot rank this file (the random control also scores 0). ' if rc['holdout']['scores']['LCS']['dti'] == 0.0 else 'That instrument rewards recovery of mapped catalogue faults and is not fold-pure for these inputs. ') +
                'It is not the leaderboard (see the analysis). '
                'No weekly slot is selected or used by this repository — submitting is a separate human step.</div>')
    return ok_dl, ok_sub, slot


CSS_EXTRA = """
<style>
.btn-big{font-size:1.25rem;padding:1rem 1.6rem}
.status-grid{display:grid;gap:.7rem;margin:1rem 0}
.status{border-left:6px solid var(--copper);padding:.8rem 1rem;background:var(--panel);border-radius:4px}
.status-ok{border-color:#4ecb71;background:#14291d}.status-warn{border-color:#d45;background:#2a1414}.status-hold{border-color:#c9a227;background:#2a2412}
.copyrow{display:flex;gap:.5rem;align-items:flex-start;flex-wrap:wrap}.copyrow code{flex:1 1 20rem;background:#0f0c09;padding:.4rem .6rem;border:1px solid var(--line);border-radius:4px;word-break:break-word}
button.copy{background:transparent;color:var(--ink);border:1px solid var(--copper);border-radius:4px;padding:.3rem .7rem;cursor:pointer}
details.archive{max-width:860px;margin:1rem auto;padding:0 1.25rem}details.archive>summary{cursor:pointer;color:var(--copper);padding:.6rem 0}
</style>
<script>function cp(id){var t=document.getElementById(id).innerText;if(navigator.clipboard){navigator.clipboard.writeText(t);}}</script>
"""


def head(title, desc):
    return (f'<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'  <meta name="description" content="{e(desc)}">\n  <title>{e(title)}</title>\n  <link rel="stylesheet" href="style.css">{CSS_EXTRA}\n</head>\n<body>\n')


def nav():
    return ('<nav style="margin:.8rem 0;font-size:.95rem"><strong>Go to:</strong> <a href="index.html">Download</a> · '
            '<a href="executive-summary.html">Executive summary: how to submit</a> · <a href="SUBMIT.html">Step-by-step guide</a> · '
            '<a href="WHY_R0_0_2778.md">Why 0.2778?</a> · <a href="HYPOTHESES_20261024_LCS.md">Ranked hypotheses</a> · '
            '<a href="UNIQUENESS_POLICY_20261024.md">Uniqueness policy</a> · <a href="NEXT_STEPS.md">Next steps</a></nav>')


def meta_block(rc, audit):
    f = audit["file"]
    return f"""
  <dl class="meta">
    <div><dt>Submission name (unique; ≤ 140 chars)</dt><dd class="copyrow"><code id="nm">{e(rc['name'])}</code><button class="copy" onclick="cp('nm')">Copy</button></dd></div>
    <div><dt>Note ({rc['note_chars']} chars; limit 140)</dt><dd class="copyrow"><code id="nt">{e(rc['note'])}</code><button class="copy" onclick="cp('nt')">Copy</button></dd></div>
    <div><dt>SHA-256 of the served bytes</dt><dd><code>{audit['sha256_zeros']}</code></dd></div>
    <div><dt>Grid / values</dt><dd>EPSG:32611 · 3730 × 3292 · 100 m · float32 · [0, 1] · {audit['n_dots']:,} unit-mass dots · zeros outside the footprint</dd></div>
    <div><dt>Receipts</dt><dd><a href="downloads/{e(f.replace('-zeros.tif','-audit.json'))}">audit receipt</a> · <a href="downloads/lcs_run_card.json">run-card JSON</a> ·
      <a href="downloads/lcs_registry_final.json">registry gate (final dots)</a> · <a href="downloads/lcs_registry_surface.json">registry gate (surface)</a> ·
      <a href="downloads/lcs_proxy_audit.json">holdout / canary / SGMC</a> · <a href="downloads/lcs_build.json">build + selection</a></dd></div>
  </dl>"""


def build_index(rc, audit):
    f = audit["file"]
    z = f.replace("-zeros.tif", "-zeros.zip")
    size_kb = (DL / f).stat().st_size / 1024
    ok_dl, ok_sub, slot = status_blocks(rc)
    proj = rc["projection_MODEL"]
    archive = (DOCS / "_archive_main_20261024.html").read_text(encoding="utf-8")
    off = "".join(f'<li><a href="{u}">{e(n)}</a></li>' for n, u in OFFICIAL)
    out = head("GEMSDOE92 — download the unique GEMS submission file", "One-click GeoTIFF for DrivenData DOE GEMS Prize #306 with automated validation status.")
    out += f"""<header class="hero">
  <p class="kicker">DOE GEMS Prize · DrivenData #306 · EPSG:32611 · 100 m · built 2026-10-24</p>
  <h1>Your unique submission file — one click</h1>
  <p class="lede">A single-band float32 GeoTIFF, validated automatically (no human inspection). The three status lines below are
  <em>computed from evidence</em> — change the evidence and they change. Nothing here is a leaderboard score.</p>
  {nav()}
  <section class="download-card" id="the-file" data-primary="true">
    <p class="filename">{e(f)}</p>
    <p><a class="btn btn-big" href="downloads/{e(f)}" download>⬇ DOWNLOAD THE TIF ({size_kb:.0f} KB)</a>
       <a class="btn btn-ghost" href="downloads/{e(z)}" download>ZIP (one TIFF)</a></p>
    <div class="status-grid">{ok_dl}{ok_sub}{slot}</div>
    {meta_block(rc, audit)}
    <p><strong>How to submit (human step, 4 clicks):</strong> open the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">submit form</a> ·
    choose the <code>.tif</code> (or the ZIP) · paste the note · send. Full steps and limits: <a href="executive-summary.html">executive summary</a>.
    The portal allows 3 submissions per week and the website limit prevails (<a href="{OFFICIAL[11][1]}">forum 11553</a>); one submission is chosen for both prize rounds.</p>
    <p><strong>What this file is:</strong> {audit['n_dots']:,} dots (the same budget as the 0.2778 parent R0) placed where independent detector lanes agree, weighted by each lane's
    leaderboard-implied credit, kept more than 3 px from every mapped fault, and spread so that no previous submission's 3-px halo contains more than {rc['registry']['tiers']['S']['final']['max_forward_overlap']*100:.0f}% of them.
    <strong>MODEL</strong> projection (never a score): {proj['dti_shrunk']:.3f}–{proj['dti_null']:.3f} against R0's claimed 0.2778; one typical model error is ±{proj['loo_band']:.2f}, so the model cannot say it beats R0.
    It is an exploration arm, not a claim of improvement.</p>
  </section>
</header>
<main>
<section>
  <h2>Gate board</h2>
  <table>
    <tr><th>uniqueness tier (all measured, thresholds 0.70 / 0.90 / 3 px unchanged)</th><th>rasters</th><th>surface: max overlap / # &gt; 0.70</th><th>final dots: max overlap / # &gt; 0.70</th><th>max |Spearman|</th><th>result</th></tr>
    {tier_rows(rc)}
  </table>
  <p>Tier T cannot be passed by any file: {rc['registry']['blanket_rasters']['n_distinct']} registry rasters have a 3-px halo covering ≥ 50 % of the footprint
  (the 17GEMSDOE E-proba surface covers 100 %), so every nonempty candidate overlaps them. Scope: {e(rc['registry']['scope'])}</p>
  <table>
    <tr><th>HOLDOUT-DTI ({e(rc['holdout']['evaluator'])}, {rc['holdout']['withheld_positive_pixels']:,} withheld positives, paired 20 km block bootstrap)</th><th>DTI</th><th>95 % CI</th></tr>
    {holdout_rows(rc)}
  </table>
  <p>Leakage canary (lane-vote sum alone, hidden catalogue segments vs. background): symmetric AUC <strong>{rc['holdout']['canary']['symmetric_auc']:.3f}</strong>
  ({e(rc['holdout']['canary']['status'])}). Not fold-pure: {e(rc['holdout']['not_fold_pure'])}. These are HOLDOUT-DTI proxies; they are not ORGANIZER-CONFIRMED and do not predict the leaderboard.</p>
</section>
<section>
  <h2>Why this file, and why 0.2778</h2>
  <p>R0 (claimed 0.2778) is the H19-5 skeleton thinned to 2.83 px and stripped of every dot within 2 px of a mapped fault — dots the scorer treats as pure false positives.
  Everything else tried in the GEMSDOE family either re-selected skeleton dots (no change), added dots from other sources at credit below break-even (lower), or was an independent lane with lower credit per dot.
  Full derivation with evidence classes: <a href="WHY_R0_0_2778.md">WHY_R0_0_2778.md</a>. Today's live leaderboard (top 50 only) starts at 0.4413 and 0.2778 sits below row 50 (0.2818).</p>
</section>
<section>
  <h2>Official sources used</h2>
  <ul>{off}</ul>
</section>
</main>
<details class="archive"><summary><strong>Earlier research-only candidates (superseded; kept for the audit trail)</strong></summary>
<p>The sections below were written by earlier sessions under the literal all-registry rule (Tier T) and are superseded by the three-tier policy above. Their files remain downloadable and format-gated by CI.</p>
{archive}
</details>
<footer>GEMSDOE92 · Core values: <em>Maximize P(Win)</em> and <em>Own the Outcome</em> · No organizer receipt exists for any file here · Generative-AI use is disclosed in <a href="https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/AI_USE.md">AI_USE.md</a> · <a href="https://github.com/buffedlizard55-lab/GEMSDOE92">repository</a></footer>
</body>
</html>
"""
    (DOCS / "index.html").write_text(out, encoding="utf-8")


def build_exec(rc, audit):
    f = audit["file"]
    ok_dl, ok_sub, slot = status_blocks(rc)
    lit = rc["registry"]["literal_registry_rule_passed"]
    out = head("Executive summary — how to submit (GEMSDOE92)", "File, unique name, note, and the exact portal steps for the GEMS Prize submission.")
    out += f"""<header class="hero">
  <p class="kicker">Executive summary · DrivenData DOE GEMS Prize #306 · EPSG:32611</p>
  <h1>How to submit — the file, the name, the note</h1>
  <p class="lede">Three computed status lines, then the exact steps. Format validation is automated; <strong>OK TO SUBMIT</strong> means valid and not a duplicate — it is not a score and not a prediction that the file will win.</p>
  {nav()}
</header>
<main>
<section class="download-card">
  <h2>Status (derived from evidence, not typed)</h2>
  <div class="status-grid">{ok_dl}{ok_sub}{slot}</div>
  <p class="filename">{e(f)}</p>
  <p><a class="btn btn-big" href="downloads/{e(f)}" download>⬇ Download the TIF</a> <a class="btn btn-ghost" href="downloads/{e(f.replace('-zeros.tif','-zeros.zip'))}" download>ZIP (one TIFF)</a></p>
  {meta_block(rc, audit)}
</section>
<section>
  <h2>Submit in five steps</h2>
  <ol>
    <li>Download the <code>.tif</code> above (or the ZIP that contains exactly that one TIFF). Do not open and re-save it in GIS software; any re-save changes the bytes the audit certifies.</li>
    <li>Sign in at <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData</a> and open the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">submission form</a>.</li>
    <li>Choose the file. If the form shows a separate name field, paste the <strong>submission name</strong>; if it shows only a note field, paste the note — it begins with the lane name and the file name carries the content id.</li>
    <li>Paste the <strong>note</strong> (≤ 140 characters, already checked). Send.</li>
    <li>When the receipt appears, enter the score <em>exactly as shown</em> in <code>ledger/raw_paste.txt</code> / <code>ledger/submissions.csv</code> as an ORGANIZER-CONFIRMED receipt. Never infer a score from the local HOLDOUT-DTI or from the MODEL projection.</li>
  </ol>
  <p><strong>Limits.</strong> Three submissions per week (the website limit prevails — <a href="{OFFICIAL[11][1]}">staff reply</a>); you select <em>one</em> submission for both prize rounds; the Phase-2 truth set is revised by expert review of all Phase-1 submissions, so a prediction can matter for the final round even if it is not top-scoring in Phase 1 (<a href="{OFFICIAL[10][1]}">staff reply</a>).
  Generative-AI use must be disclosed in your narrative (Official Rules §3.2; see <a href="https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/AI_USE.md">AI_USE.md</a>).</p>
</section>
<section>
  <h2>Why "OK TO SUBMIT" and "slot verdict" differ</h2>
  <p><strong>OK TO SUBMIT</strong> = format-valid ∧ unique under the decisive tier ({e(rc['registry']['policy']['decisive_tier'])}) ∧ leakage canary passes ∧ model kill-criterion not triggered.
  <strong>Slot verdict</strong> = the protocol's promote/negative: the paired HOLDOUT-DTI difference against the repository's recorded holdout best must be entirely above 0. The two are independent on purpose: the first says the portal will accept the file and it is not a copy; the second says whether the project's own pre-registered rule recommends a slot.
  The holdout instrument rewards recovery of mapped catalogue faults — which the real scorer masks — so its verdict and the leaderboard can disagree (see <a href="WHY_R0_0_2778.md">analysis</a>).</p>
  <p><strong>Literal all-registry rule (Tier T): {'passed' if lit else 'NOT passed'}.</strong> It cannot be passed by any file at all because blanket rasters overlap everything; the policy and the one-line switch to change the decisive tier are in <a href="UNIQUENESS_POLICY_20261024.md">UNIQUENESS_POLICY_20261024.md</a>. Both tiers S and L are measured and shown on the <a href="index.html">main page</a>.</p>
</section>
<section>
  <h2>Official links for manual review</h2>
  <ul>{"".join(f'<li><a href="{u}">{e(n)}</a></li>' for n, u in OFFICIAL)}</ul>
</section>
<section>
  <h2>Limitations (read before spending a slot)</h2>
  <ul>
    <li>No organizer receipt exists for this file; every score in this repository is a CLAIM or a MODEL.</li>
    <li>The projection range ({rc['projection_MODEL']['dti_shrunk']:.3f}–{rc['projection_MODEL']['dti_naive']:.3f} against R0's 0.2778, one typical model error ±{rc['projection_MODEL']['loo_band']:.2f}) means the file is an <em>exploration arm</em>: the model cannot say it beats 0.2778.</li>
    <li>The holdout is not fold-pure for these inputs, and the registry scope is the owner's public GEMSDOE repositories only.</li>
    <li>The live public board (top 50) starts at 0.4413; 0.2778 is outside the visible rows. A file at R0's level is not a prize-level file.</li>
  </ul>
</section>
</main>
<footer>GEMSDOE92 · Core values: <em>Maximize P(Win)</em> · <em>Own the Outcome</em> · <a href="index.html">← back to the download</a></footer>
</body>
</html>
"""
    (DOCS / "executive-summary.html").write_text(out, encoding="utf-8")
    # step-by-step guide shares the executive page content but keeps the legacy URL alive
    (DOCS / "SUBMIT.html").write_text(out.replace("Executive summary — how to submit", "Step-by-step submission guide").replace(
        "<h1>How to submit — the file, the name, the note</h1>", "<h1>Step-by-step submission guide</h1>"), encoding="utf-8")
    (DOCS / "submit.html").write_text(
        '<!DOCTYPE html>\n<html lang="en"><head><meta charset="UTF-8"><meta http-equiv="refresh" content="0; url=executive-summary.html">'
        '<title>Moved — executive summary</title><link rel="canonical" href="executive-summary.html"></head>\n<body>'
        '<p>This page moved to <a href="executive-summary.html">executive-summary.html</a> (how to submit: file, name, note, steps, limits). '
        'The download is at the top of <a href="index.html">the main page</a>.</p></body></html>\n', encoding="utf-8")


def build_root(rc, audit):
    """Repository-root index.html (the GitHub Pages entry point): direct download + the same derived statuses, then redirect."""
    f = audit["file"]
    st = rc["status"]
    dl = "✅ OK TO DOWNLOAD" if st["ok_to_download"] else "⛔ NOT OK TO DOWNLOAD"
    sub = "✅ OK TO SUBMIT" if st["ok_to_submit"] else "⛔ NOT OK TO SUBMIT"
    slot = "SLOT VERDICT: promote" if rc["verdict"] == "promote" else "SLOT VERDICT: negative (pre-registered rule; see the workbench)"
    out = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="0; url=docs/index.html">
  <title>GEMSDOE92 — download the GEMS submission file</title>
  <link rel="canonical" href="https://buffedlizard55-lab.github.io/GEMSDOE92/docs/index.html">
</head>
<body>
  <h1>GEMSDOE92 submission workbench</h1>
  <p><a href="docs/downloads/{e(f)}" download><strong>⬇ Download the GeoTIFF ({e(f)})</strong></a></p>
  <p><strong>{dl}</strong> · <strong>{sub}</strong> (valid and not a copy of a previous submission; not a score) · <strong>{e(slot)}</strong>.
  Name: <code>{e(rc['name'])}</code>. Note: <code>{e(rc['note'])}</code></p>
  <p><a href="docs/index.html">Open the workbench: evidence, tiers, how to submit</a> · <a href="docs/executive-summary.html">executive summary</a></p>
</body>
</html>
"""
    (ROOT / "index.html").write_text(out, encoding="utf-8")


def main() -> int:
    rc, audit = load()
    build_index(rc, audit)
    build_exec(rc, audit)
    build_root(rc, audit)
    print("rendered index.html, executive-summary.html, SUBMIT.html, submit.html for", audit["file"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
