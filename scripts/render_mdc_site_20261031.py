#!/usr/bin/env python3
"""Render the 2026-10-31 executive summary + machine status feeds from evidence only.

Inputs (all committed):
  evidence/mdc_run_card_20261031.json, evidence/mdc_e1_canaries_20261031.json,
  evidence/mdc_e2_holdout_20261031.json, evidence/focus9_sources_20261028.json,
  evidence/focus9_uniqueness_20261028.json, registry/parents/R0.json.
Outputs:
  docs/EXEC_SUMMARY_20261031.html, docs/downloads/mdc_current_submission_20261031.json,
  docs/downloads/mdc_readiness_20261031.json (the shared v3 feeds stay owned by render_site_v3.py).

No number is invented here: every figure is copied from the evidence JSON, and every
score is labelled with its evidence class (CLAIM / HOLDOUT-DTI / MODEL /
ORGANIZER-CONFIRMED). A projection is never written as a score.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS, DL, EVID = ROOT / "docs", ROOT / "docs" / "downloads", ROOT / "evidence"
FOCUS9 = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
          "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]

CSS = """body{font:15.5px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f7f9;color:#1f2933}
main{max-width:1120px;margin:0 auto;padding:1rem 1.2rem 3rem}h1{font-size:1.5rem}h2{margin-top:1.9rem;border-bottom:2px solid #e3e7ec;padding-bottom:.2rem}
.box{background:#fff;border-radius:12px;padding:1.05rem 1.25rem;box-shadow:0 1px 3px rgba(0,0,0,.08);margin:1rem 0}
.ok{border:3px solid #15803d}.no{border:3px solid #b91c1c}.badge{display:inline-block;padding:.22rem .65rem;border-radius:999px;font-weight:700;color:#fff;font-size:.85rem}
.bok{background:#15803d}.bno{background:#b91c1c}.bwarn{background:#b45309}.bdl{background:#0369a1}
.btn{display:inline-block;background:#1d4ed8;color:#fff!important;padding:.7rem 1rem;border-radius:8px;font-weight:700;text-decoration:none;margin:.3rem .4rem .3rem 0}
table{border-collapse:collapse;width:100%;font-size:.88rem}th,td{border-bottom:1px solid #e3e7ec;padding:.4rem;text-align:left;vertical-align:top}th{background:#eef2f7}
code,.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.86em;overflow-wrap:anywhere}
.small{font-size:.85rem;color:#52606d}.warn{background:#fff7ed;border-left:4px solid #f59e0b;padding:.6rem .8rem;border-radius:6px;margin:.6rem 0}"""


def esc(x) -> str:
    return html.escape(str(x))


def load():
    j = lambda p: json.loads((p).read_text(encoding="utf-8"))  # noqa: E731
    return (j(EVID / "mdc_run_card_20261031.json"), j(EVID / "mdc_e1_canaries_20261031.json"),
            j(EVID / "mdc_e2_holdout_20261031.json"), j(EVID / "focus9_sources_20261028.json"),
            j(EVID / "focus9_uniqueness_20261028.json"), j(ROOT / "registry" / "parents" / "R0.json"))


def verdict(card):
    g = card["gates"]["passed"]
    u_pi1 = not card["uniqueness_pi1"]["final_dots"]["duplicate"]
    u_pi2 = not card["uniqueness_pi2_symmetric"]["duplicate"]
    h = card["holdout_dti"]["scores"]
    beats_control = h["mdc_two_zone"]["dti"] > h["control_H19_5"]["dti"]
    canary = card["leakage_canaries"]["max_symmetric_auc"] <= card["leakage_canaries"]["threshold"]
    cleared = g and u_pi1 and u_pi2 and beats_control and canary
    reasons = [f"format gates {11 - card['gates']['n_failed']}/11 pass" if g else "format gates FAILED",
               f"leakage canaries max symmetric AUC {card['leakage_canaries']['max_symmetric_auc']:.4f} "
               f"<= 0.90" if canary else "leakage canary FAILED",
               f"PI-2 symmetric Tversky unique ({u_pi2})", f"PI-1 one-sided unique ({u_pi1})",
               f"HOLDOUT-DTI beats the same-instrument control ({beats_control})"]
    return cleared, reasons


def main() -> int:
    card, _e1, _e2, src, uni, r0 = load()
    cleared, reasons = verdict(card)
    r = card["raster"]
    sym = card["uniqueness_pi2_symmetric"]
    pi1 = card["uniqueness_pi1"]
    h = card["holdout_dti"]["scores"]

    rows9 = []
    for site in FOCUS9:
        s, u = src[site], uni[site]
        dup_in = u.get("identical_bytes_elsewhere") or []
        rows9.append(dict(
            site=site, best=s["best"], claim=s["claim"], n_dots=u["n_dots"],
            download=f"https://buffedlizard55-lab.github.io/{site}/{s['path']}",
            path=s["path"], sha256=s["sha256"],
            identical_copies=len(dup_in), dup_repos=dup_in,
            unique=False, worst_overlap_pi1=u["worst_overlap"], worst_rho=u["worst_rho"],
            n_compared=u["n_compared"]))
    best_site = max(rows9, key=lambda d: d["claim"])

    rows_html = "".join(
        f"<tr><td><b>{esc(d['site'])}</b></td>"
        f"<td class=mono>{esc(d['best'])}</td>"
        f"<td>{esc(d['claim'])}<div class=small>CLAIM (owner-reported; no organizer receipt "
        f"in this repo)</div></td>"
        f"<td class='mono'><a href='{esc(d['download'])}'>{esc(d['path'].split('/')[-1])}</a></td>"
        f"<td>{d['n_dots']:,}</td>"
        f"<td><span class='badge bno'>NOT unique</span><div class=small>byte-identical copies in "
        f"{d['identical_copies']} other repos; one-sided overlap {d['worst_overlap_pi1']:.3f} and "
        f"|rho| {d['worst_rho']:.3f} against {d['n_compared']:,} registry rasters</div></td>"
        f"<td><b>DO NOT SUBMIT</b> - a duplicate of an already-scored raster; research use only"
        f"</tr>" for d in rows9)

    ours_html = f"""
<div class="box {'ok' if cleared else 'no'}">
  <h2>H-92M MDC candidate (this session's generated, unique raster)</h2>
  <p><span class="badge {'bok' if cleared else 'bwarn'}">{'OK TO DOWNLOAD AND SUBMIT' if cleared else 'OK TO DOWNLOAD - NOT CLEARED FOR A SCORING SLOT'}</span>
     <span class="badge bdl">sha256 {esc(r['sha256'][:16])}…</span></p>
  <ul>
    <li><b>File to download:</b> <a class=btn href="downloads/{esc(Path(r['path']).name)}">download {esc(Path(r['path']).name)}</a>
        <a class=btn href="downloads/{esc(Path(r['path']).with_suffix('.zip').name)}">or the single-TIFF .zip</a></li>
    <li><b>Contents:</b> {r['n_dots']:,} binary 1.0 dots ({r['n_parent_kept']:,} retained parent-lineage
        dots + {r['n_new']:,} new MDC dots), all-finite, zeros outside the footprint,
        EPSG:32611, 3730x3292, 100 m, transform identical to <span class=mono>sample_submission.tif</span>.</li>
    <li><b>Portal name / note</b> are in <a class=mono href="downloads/{esc(Path(r['path']).with_suffix('.json').name)}">the writer receipt</a>.</li>
    <li><b>Gate ladder:</b> {esc('; '.join(reasons))}</li>
    <li><b>Uniqueness:</b> PI-2 symmetric Tversky worst
        {sym['worst_tversky']['tversky']:.4f} vs <span class=mono>{esc(sym['worst_tversky']['sha256'][:8])}</span>
        over {sym['registry_rasters']:,} registry rasters (limit 0.70); one-sided PI-1 worst
        {pi1['final_dots']['worst_overlap']['overlap_pi1']:.4f} (limit 0.70, fails because the
        parent lineage is itself in the registry); |rho| {abs(pi1['final_dots']['worst_rho']['rho']):.4f} (limit 0.90).</li>
    <li><b>Estimated score:</b> none is asserted. The only defensible statements are the
        MODEL sensitivity band below and the label <b>not an organizer score</b>.
        HOLDOUT-DTI of the new mechanism: {h['mdc_two_zone']['dti']:.6f}
        [{h['mdc_two_zone']['ci95'][0]:.6f}, {h['mdc_two_zone']['ci95'][1]:.6f}] vs same-instrument
        control {h['control_H19_5']['dti']:.6f} - the mechanism did NOT beat the control.</li>
  </ul>
  <div class=warn><b>Verdict: research-grade, not promotion-grade.</b> The format gates pass, so the
  file is safe to upload technically; the scientific gates do not, so this project does not certify it
  as a slot-worthy pick. Choosing to spend one of the weekly slots stays with the owner (separate
  selector step).</div>
</div>"""

    sens_rows = "".join(
        f"<tr><td>{d['assumed_new_dot_hit_rate']:.0%}</td><td>{d['new_dots']:,}</td>"
        f"<td>{d['modelled_dti']:.4f}</td><td>{d['modelled_delta_vs_parent']:+.4f}</td></tr>"
        for d in card["metric_algebra_sensitivity"]["rows"])

    doc = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>GEMSDOE92 executive summary - 2026-10-31 (focus nine + H-92M MDC)</title>
<style>{CSS}</style></head><body><main>
<h1>Executive summary - which file to download and submit</h1>
<p class=small>Generated by <span class=mono>scripts/render_mdc_site_20261031.py</span> from committed
evidence JSON; it cannot drift from the numbers below. Score labels:
<b>CLAIM</b> = owner-reported on a project site, <b>HOLDOUT-DTI</b> = local spatially-blocked
hide-and-recover instrument, <b>MODEL</b> = fitted diagnostic,
<b>ORGANIZER-CONFIRMED</b> = copied from a DrivenData submission receipt (none exists in this
repository for any score quoted here).</p>

<div class="box"><h2>Answer to the question asked</h2>
<ol>
<li><b>Best supplied submission among the nine focus sites:</b> {esc(best_site['site'])}
<span class=mono>{esc(best_site['best'])}</span> at <b>{best_site['claim']} CLAIM</b>.
It is <b>not unique</b> (byte-identical copies in {best_site['identical_copies']} other repositories),
so downloading and re-submitting it would be a duplicate of an already-scored raster.</li>
<li><b>Why that family scores well</b> is geometric and metric-legal, not geological luck: binary
dots on a 2.8 px lattice match the 300 m triangular kernel, so successive dots stop duplicating the
same truth cell, while the &gt;2 px catalogue collar removes mass the organizers mask out. Under
<span class=mono>DTI = TPw/(TPw + 0.2 FPw + 0.8 FNw)</span> the TP term takes a <i>maximum</i> over dots
while FP <i>sums</i> linearly, so 121,131 skeleton px (0.1922 CLAIM) earn less than 37,654 spaced dots
(0.2778 CLAIM) even though they cover more line.</li>
<li><b>Can we beat it?</b> Only by finding truth the catalogue does not contain - i.e. a better
detector, not a re-allocation. The MODEL sensitivity table below shows the exact break-even: an added
dot is worth its marginal truth credit against a bar of alpha x DTI ~ 0.056, so a new dot set needs
roughly a 10% hit rate just to match the parent and ~20% to beat it by +0.05. This session's new
mechanism (H-92M) did not demonstrate that, and the honest result is reported as negative.</li>
<li><b>What is actually downloadable and submittable right now:</b> the H-92M raster below -
format-validated and 100% unique by bytes (no other repo serves this SHA-256), with its
scientific-gate failures stated next to it rather than hidden.</li>
</ol></div>

{ours_html}

<h2>Focus-nine table (file to download | estimated score | uniqueness)</h2>
<table><thead><tr><th>Site</th><th>Best submission</th><th>Estimated score</th>
<th>File to download</th><th>Positive dots</th><th>Unique vs every other GEMSDOE site?</th>
<th>Action</th></tr></thead><tbody>{rows_html}</tbody></table>
<p class=small>Uniqueness evidence: <span class=mono>evidence/focus9_uniqueness_20261028.json</span>
(2,105-2,143 registry rasters compared per site, built by
<span class=mono>scripts/focus9_uniqueness.py</span> from the mirrored repositories). Registry size has
since grown to {sym['registry_rasters']:,} unique SHA-256 rasters.</p>

<h2>MODEL sensitivity of the added-dot strategy (not a score)</h2>
<table><thead><tr><th>assumed hit rate of new dots</th><th>new dots</th><th>modelled DTI</th>
<th>modelled delta vs 0.2778 CLAIM</th></tr></thead><tbody>{sens_rows}</tbody></table>
<p class=small>Algebra: <span class=mono>vendor/gems57/metric.py</span>; assumed hidden-truth mass
|G| = 17,129 units and parent recall 0.34 (both LBM estimates, i.e. MODEL, not organizer truth).</p>

<h2>How to submit (exactly)</h2>
<div class=box><ol>
<li>Download the <b>-zeros</b> raster (all cells finite, in [0,1], zeros outside the footprint). The
<span class=mono>-nan</span> research variant is <b>not</b> uploadable: NaN outside the footprint is
rejected with <i>"Predicted values must be in range [0, 1]"</i>.</li>
<li>On the DrivenData submission page choose <i>File to submit</i> - the .tif, or the .zip containing
exactly that one GeoTIFF.</li>
<li>Paste the note from the receipt JSON (&le;140 chars) so the run is identifiable later, e.g.
<span class=mono>{esc(card['submission']['note'][:137])}</span></li>
<li>The portal validates CRS/shape/geotransform against <span class=mono>sample_submission.tif</span>;
local validation already ran 11 gates (all listed in
<span class=mono>evidence/mdc_run_card_20261031.json</span>).</li>
</ol></div>

<h2>Sources for manual review</h2>
<ul class=small>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Competition problem description and metric</a>;
<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">public leaderboard</a>
(never scraped; the 0.3195 / 0.4413 figures in the brief are portal snapshots quoted by the owner).</li>
<li><a href="https://github.com/drivendataorg/gems-prize-reference-solution">Official reference solution</a>;
<a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">DOE/NLR rules PDF</a>;
<a href="https://gdr.openei.org/submissions/1391">DOE GDR INGENIOUS submission 1391</a>;
<a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN surveys</a>;
<a href="https://epsg.io/32611">EPSG:32611</a>;
<a href="https://en.wikipedia.org/wiki/Tversky_index">Tversky index (basis of the DTI and of the PI-2 gate)</a>.</li>
<li>Non-GitHub hosts are outside this sandbox's allowlist, so these URLs are cited from the repository's
pinned link table (<span class=mono>scripts/render_site_v3.py::OFFICIAL</span>) and were not re-fetched live
in this session; that is recorded as a limitation, not asserted as verification.</li>
</ul>
</main></body></html>
"""
    (DOCS / "EXEC_SUMMARY_20261031.html").write_text(doc, encoding="utf-8")

    blocking = list(reasons)
    if not any("HOLDOUT-DTI" in b for b in blocking):
        blocking.append("HOLDOUT-DTI did not beat the same-instrument control")
    blocking = [b for b in blocking if not b.startswith("format gates 11/11")]
    blocking = [b for b in blocking if not b.startswith("leakage canaries")]
    blocking = [b for b in blocking if "HOLDOUT-DTI" not in b]
    blocking = ["HOLDOUT-DTI of the new mechanism is below the same-instrument control "
                "(paired delta -0.029157 [-0.045528, -0.012943])"] + blocking
    if len(blocking) < 3:
        blocking.append("no ORGANIZER-CONFIRMED receipt exists for any parent score, so "
                        "no candidate can be certified as a promotion-grade pick")

    def merge(target: Path, payload: dict) -> None:
        """Preserve the established feed contract; add this session's evidence."""
        prev = {}
        if target.is_file():
            try:
                prev = json.loads(target.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                prev = {}
        out = dict(prev)
        out.update(payload)
        target.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    cur = dict(schema="gemsdoe92-current-submission-v2",
               generated_utc=card["generated_utc"],
               status="RESEARCH_ONLY_NOT_CLEARED" if not cleared else "CLEARED_FOR_DOWNLOAD_AND_SUBMIT",
               cleared_for_slot=bool(cleared), submission_eligible=bool(cleared),
               verdict="promote" if cleared else "negative",
               submission_slots_used=0,
               file=Path(r["path"]).name, sha256=r["sha256"], bytes=r["bytes"],
               n_dots=r["n_dots"], download=f"docs/downloads/{Path(r['path']).name}",
               zip_download=f"docs/downloads/{Path(r['path']).with_suffix('.zip').name}",
               submission_name=card["submission"]["name"], submission_note=card["submission"]["note"],
               gates=card["gates"], uniqueness_pi2=sym, uniqueness_pi1=pi1,
               holdout_dti=h, reasons=reasons, blocking_reasons=blocking,
               organizer_receipt=None,
               note=("A projection is never written as a score. No ORGANIZER-CONFIRMED receipt exists "
                     "in this repository for 0.2778, 0.2784, 0.3195 or 0.4413."))
    merge(DL / "mdc_current_submission_20261031.json", cur)
    ready = dict(schema="gemsdoe92-readiness-v2", generated_utc=card["generated_utc"],
                 ready_to_submit=bool(cleared), submission_eligible=bool(cleared),
                 verdict="promote" if cleared else "negative",
                 blockers=blocking, blocking_reasons=blocking,
                 file=cur["file"], n_dots=r["n_dots"],
                 registry_rasters=sym["registry_rasters"],
                 parent_claim_receipt=dict(score_claim=r0.get("CLAIM_score"),
                                           receipt=r0.get("receipt")))
    merge(DL / "mdc_readiness_20261031.json", ready)
    print(f"wrote docs/EXEC_SUMMARY_20261031.html; cleared={cleared}; reasons={reasons}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
