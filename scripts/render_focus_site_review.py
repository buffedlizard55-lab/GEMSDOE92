#!/usr/bin/env python3
"""Render the audited nine-site comparison from its durable JSON evidence.

The script never fetches data or creates a GeoTIFF. Its source of truth is
``evidence/focus_sites_release_review_20261026.json``; ``--check`` verifies
that the Markdown, HTML, and public JSON download match that snapshot.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/focus_sites_release_review_20261026.json"
MARKDOWN = ROOT / "docs/SITE_REVIEW_20261026.md"
HTML = ROOT / "docs/SITE_REVIEW_20261026.html"
PUBLIC_JSON = ROOT / "docs/downloads/focus_sites_release_review_20261026.json"


def _e(value: object) -> str:
    return html.escape(str(value), quote=True)


def _pct(value: float) -> str:
    return f"{100.0 * float(value):.2f}%"


def _row_md(site: dict) -> str:
    ref = site["comparison_reference"]
    unique = site["uniqueness_vs_other_eight"]
    provenance = "CLAIM — no organizer receipt"
    link = f"[research TIFF]({ref['raw_download_url']})"
    if site["reported_artifact"]["sha256"] != ref["sha256"]:
        link += f" · [reported encoding]({site['reported_artifact']['raw_download_url']})"
    witness = (
        f"NO — vs {unique['strongest_witness_site']}: "
        f"{_pct(unique['candidate_to_witness_overlap_3px'])} within 3 px; "
        f"|ρ|={unique['abs_binary_support_rank_correlation']:.4f}"
    )
    return (
        f"| {site['site']} | {site['reported_submission_name']} | "
        f"{site['reported_score']:.4f} ({provenance}) | {link} "
        f"(n={ref['positive_pixels_in_footprint']:,}; SHA-256 `{ref['sha256']}`) | "
        f"— (not supportable) | {witness} |"
    )


def render_markdown(data: dict) -> str:
    rows = "\n".join(_row_md(row) for row in data["selected_site_artifacts"])
    sources = "\n".join(
        f"- [{source['name']}]({source['url']}) — {source['status']}."
        for source in data["official_source_links"]
    )
    pairs = data["all_pairwise_comparisons"]
    exact_pairs = [p for p in pairs if p["exact_prediction_match"]]
    exact_text = ", ".join(f"{p['site_a']} ↔ {p['site_b']}" for p in exact_pairs) or "none"
    top = data["strongest_reference"]
    return f"""# GEMS highest-site artifact review — 2026-10-26

> **NO NEW TIFF WAS GENERATED. DO NOT SUBMIT ANY FILE FROM THIS REVIEW.** The public source rasters below are downloadable for research, but none is a new unique candidate and none is cleared for a competition slot. The pinned literal witness covers all {data['protocol']['footprint_cells']:,} finite sample-footprint cells; every nonempty in-footprint candidate therefore has 100% overlap, above the binding 70% stop.

**Executive brief:** [open the web summary](SITE_REVIEW_20261026.html) · [download complete JSON evidence](downloads/focus_sites_release_review_20261026.json) · [ranked hypothesis screen](HYPOTHESES_20261026_SITE_REVIEW.md).

## Decision and evidence boundary

- The strongest *reported reference among these nine* is **{top['site']} `{top['submission_name']}` — {top['score_claim']:.4f} CLAIM**. This is an owner report, not an `ORGANIZER-CONFIRMED` receipt; no submission-page receipt binds the score to these bytes.
- All nine selected public TIFF references were fetched through the GitHub Git Blob API, verified against their Git blob IDs and SHA-256, and compared inside the sample grid. The comparison covers 17 variants from the nine sites and all 36 pairs among the nine selected masks.
- All nine format-safe comparison references passed **9/9 shared strict format-only gates** (single-band float32, grid/CRS/transform, finite `[0,1]`, no NaNs inside, zeros outside, reread SHA-256). This is not a holdout, catalogue-clearance, uniqueness, or submission pass.
- Every selected mask fails the pairwise uniqueness rule against at least one of the other eight sites. In addition, the literal full-footprint witness independently forces a stop for every nonempty candidate. No candidate surface or final dots were generated, no holdout was run, and no score is estimated.
- **Downloadability:** yes, the linked *historical owner-published references* can be downloaded for research. **Submission clearance:** no. Research access does not establish organizer acceptance or redistribution rights.

### Separate current-main artifact — BLINDEXT (outside this review)

Upstream main (`{data['current_upstream_main_context']['verified_main_commit'][:7]}`) also contains the independently produced [BLINDEXT research TIFF](downloads/{Path(data['current_upstream_main_context']['artifact_path']).name}) (SHA-256 `{data['current_upstream_main_context']['artifact_sha256']}`; [run card](downloads/{Path(data['current_upstream_main_context']['run_card_path']).name})). It was not created or holdout-evaluated by this site review and is outside the nine target sites, 17 source variants, and 36 comparisons above. It is **downloadable for research only, not unique or cleared to submit**: its own run card reports one experiment, no HOLDOUT-DTI result, a duplicate stop (literal overlap `1.000`, |ρ|=`1.000` against an existing local raster), zero weekly slots, and `submission_eligible=false`. Do not upload it.

## Strongest reference: GEMSDOE32 / R0 (`h33-h33-2-b2`)

The local pinned R0 bytes match the public GEMSDOE32 zero-outside file (SHA-256 `{top['raster_sha256']}`). The verified support lineage is `{top['local_lineage']}`. R0 is therefore the strongest *learning reference* among the claims supplied here, not a verified contest winner and not a unique raster.

A plausible mechanism is that the competition's distance-weighted Tversky metric uses a 300 m triangular kernel, with false-positive mass weighted by `α=0.2` and false negatives by `β=0.8`. Poisson-like thinning can remove redundant prediction mass where nearby dots already saturate truth credit; removing dots within two pixels of mapped catalogue faults can reallocate predictions away from known traces. That is consistent with the raster lineage, but it is **not causal proof**: the hidden truth and a score-to-file organizer receipt are unavailable. The local review does not estimate what R0 would score.

### How the other approaches differ

- **GEMSDOE24** emits a denser 1.5-pixel H19-5 thinning. **GEMSDOE27** retains all 60,069 GEMSDOE24 dots and adds 1,259 gap-closure dots; it is almost the same support under the requested rule.
- **GEMSDOE25** and **GEMSDOE30** have different file hashes/encodings but identical in-footprint prediction arrays: 44,090 dots. Their reported `.2600` claims are not independent raster evidence.
- **GEMSDOE31** is the D2.8 skeleton with the catalogue collar at `>1 px` (40,199 dots); **GEMSDOE32/R0** is exactly D2.8 with `d_catalogue>2 px` (37,654 dots).
- **GEMSDOE36** (Anderson geothermal PINN) contains every R0 dot and adds 1,200 dots; the R0→GEMSDOE36 pair breaches the 3-pixel overlap rule.
- **GEMSDOE28** uses the H36-1 rung30 blind-R1 artifact; **GEMSDOE33** is an analog tip/step-over artifact. Their owner-published labels identify different constructions, but neither has an organizer receipt here. GEMSDOE33's owner-maintained `receipt-...json` is expected-score metadata, not an organizer-scored receipt; it records a 158-character note, longer than the 140-character form limit.

## Site-by-site comparison

`Reported score` is a claim only. `Supportable estimated score` is intentionally blank for every row: there is no exact-artifact `HOLDOUT-DTI` or organizer receipt. Each research link opens the format-safe public variant used for comparison; where the reported encoding differs, a second link points to that source encoding. Full paths, SHA-256, Git blob IDs, commit pins, grid gates, and all pairwise measurements are in the JSON evidence.

| Site | Reported submission name | Highest reported score & provenance | Download / reference file | Supportable estimated score | Uniqueness vs another listed site |
|---|---|---:|---|---|---|
{rows}

The pairwise check used candidate-directed 3-pixel overlap and binary-support rank correlation. For each row, the named witness is sufficient to reject uniqueness: the candidate-to-witness fraction is above 70% or `|ρ|` is above 0.90. **All 36 pairs breach the configured symmetric pairwise stop** (at least one direction exceeds 70% or `|ρ|` exceeds 0.90). These are comparisons among the nine selected public artifacts only; they do not certify uniqueness against the wider registry. The full 36-pair table is preserved in the JSON evidence. Exact in-footprint prediction match: **{exact_text}**.

## Leaderboard and provenance irregularities

No current official leaderboard or submission-page receipt was verified. The supplied `.4413` and `.3195` snapshots conflict; the current GEMSDOE32 owner-maintained page also reports `.4437`, a secondary-source claim. Treat the current official leader as **unknown**, and do not present any of those values as independently verified. GEMSDOE32's current page explicitly labels `.2778` an owner report and says there is no receipt binding the score to the raster; it also says not to resubmit the file because it is already submitted. That is not a receipt.

## Submission guidance

**Do not upload any linked artifact.** There is no new candidate, no submission-cleared TIFF, and no slot decision. For a future file that is explicitly marked `OK TO SUBMIT` only:

1. Download that exact file (never substitute an older research link); use the project's automated validator to reopen the bytes and verify one-band float32, EPSG:32611, `3730 × 3292`, exact sample transform, finite `[0,1]` values, no NaNs in footprint, and the required outside encoding.
2. Confirm both pre-placement and final-dot uniqueness against the full accessible registry under the unchanged `0.90` correlation / `70%` 3-pixel overlap limits. Stop on a duplicate.
3. Keep the submission name separate from the file path and keep the optional note at **≤140 characters**.
4. Only a human selector may choose a weekly slot. Upload through the official [DrivenData submissions page](https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/) after clearance, then preserve the actual organizer receipt and bind it to the uploaded file's SHA-256 in the ledger.

The web links below are official/reference starting points, not proof that the linked page or current rules were live-checked in this run:

{sources}

## Reproducibility

- Durable machine-readable evidence: [`focus_sites_release_review_20261026.json`](downloads/focus_sites_release_review_20261026.json) (17 source variants, 9 selected artifacts, 36 pairwise comparisons, gates and source commits).
- Corrected rejection-only run card: [JSON on GitHub](https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/evidence/review_20261026_gemsdoe_sites_run_card_v2.json). The original `evidence/review_20261026_gemsdoe_sites_run_card.json` is retained as a superseded pre-fix record; see the [supersession note](https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/evidence/review_20261026_gemsdoe_sites_SUPERSESSION.md). The corrected card reports `new_unique_tiff_generated=false`, `experiments=0`, `weekly_slots_used=0`.
- Local repo checks: `gems.gates.run_gates(..., require_submission_encoding=True)`; 9/9 format-only gates for each comparison reference. No catalogue or holdout evaluation was run.
- Pairwise prediction arrays are normalized inside the finite sample footprint (`SHA-256 {data['protocol']['footprint_sha256']}`), shape `3730×3292`, CRS `EPSG:32611`, 100 m pixels.
"""


def render_html(data: dict) -> str:
    top = data["strongest_reference"]
    protocol = data["protocol"]
    selected = data["selected_site_artifacts"]
    rows = []
    for site in selected:
        ref = site["comparison_reference"]
        report = site["reported_artifact"]
        unique = site["uniqueness_vs_other_eight"]
        original_link = ""
        if report["sha256"] != ref["sha256"]:
            original_link = (
                f'<div class="sub-link"><a href="{_e(report["raw_download_url"])}" '
                f'title="Reported source encoding; research only">Reported source encoding</a></div>'
            )
        witness = (
            f"<strong>NO</strong> — { _e(unique['strongest_witness_site']) }: "
            f"{_pct(unique['candidate_to_witness_overlap_3px'])} of candidate dots "
            f"within 3 px (limit 70%); |ρ|={unique['abs_binary_support_rank_correlation']:.4f}."
        )
        rows.append(
            "<tr>"
            f"<th scope=\"row\">{_e(site['site'])}<br><small>{_e(site['reported_submission_name'])}</small></th>"
            f"<td><strong>{site['reported_score']:.4f} — CLAIM</strong><br><small>No organizer receipt; no score-to-raster binding.</small></td>"
            f"<td><a class=\"download\" href=\"{_e(ref['raw_download_url'])}\" download>⬇ Research TIFF</a>"
            f"{original_link}<br><small>{ref['positive_pixels_in_footprint']:,} positive cells · SHA-256 <code>{_e(ref['sha256'][:12])}…</code></small></td>"
            f"<td>—<br><small>Not supportable</small></td>"
            f"<td>{witness}</td>"
            "</tr>"
        )
    source_items = "\n".join(
        f'<li><a href="{_e(source["url"])}">{_e(source["name"])}</a> — '
        f'<span>{_e(source["status"])}</span></li>'
        for source in data["official_source_links"]
    )
    pair_exact = [p for p in data["all_pairwise_comparisons"] if p["exact_prediction_match"]]
    exact_text = ", ".join(f"{_e(p['site_a'])} ↔ {_e(p['site_b'])}" for p in pair_exact)
    if not exact_text:
        exact_text = "none"
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GEMS high-score site review — 2026-10-26</title>
  <meta name="description" content="Auditable comparison of nine claimed GEMS submissions; no score receipt, no new TIFF, no submission clearance.">
  <style>
    :root {{ color-scheme: light; --ink:#16202a; --muted:#4b5563; --red:#8b1e1e; --line:#d1d5db; --blue:#164e63; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; color:var(--ink); background:#f5f7fa; font:16px/1.58 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    main {{ width:min(1200px,calc(100% - 2rem)); margin:1.2rem auto 4rem; }}
    header,section,.decision {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:1.1rem 1.3rem; margin:0 0 1rem; }}
    nav {{ display:flex; flex-wrap:wrap; gap:.75rem 1.2rem; }} a {{ color:#075985; }} h1 {{ margin:.35rem 0 .7rem; font-size:clamp(1.8rem,4vw,2.6rem); line-height:1.12; }} h2 {{ margin-top:0; font-size:1.35rem; }}
    .decision {{ border:3px solid var(--red); background:#fff4f2; }} .stop {{ display:inline-block; padding:.25rem .6rem; background:var(--red); color:#fff; border-radius:5px; font-weight:800; }}
    .summary-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:.75rem; }} .summary-grid article {{ padding:.75rem; background:#f8fafc; border:1px solid var(--line); border-radius:8px; }}
    .table-wrap {{ overflow-x:auto; }} table {{ width:100%; min-width:1050px; border-collapse:collapse; }} th,td {{ text-align:left; vertical-align:top; padding:.65rem; border:1px solid var(--line); }} thead th {{ background:#e8eef2; }} tbody th {{ min-width:170px; }} small,.sub-link {{ color:var(--muted); font-size:.88rem; }} code {{ overflow-wrap:anywhere; }} .download {{ display:inline-block; padding:.35rem .55rem; border:1px solid var(--blue); border-radius:5px; font-weight:700; text-decoration:none; }}
    .notice {{ border-left:5px solid #b45309; padding:.55rem .8rem; background:#fffbeb; }} footer {{ color:var(--muted); font-size:.9rem; }}
  </style>
</head>
<body><main>
  <header><nav aria-label="Site navigation"><a href="index.html">GEMSDOE92 home</a><a href="executive-summary.html">Executive summary</a><a href="HYPOTHESES_20261026_SITE_REVIEW.md">Hypothesis screen</a><a href="downloads/focus_sites_release_review_20261026.json">Download audit JSON</a></nav></header>
  <aside class="decision" aria-label="Binding submission status">
    <h1>Highest reported GEMSDOE site artifacts</h1>
    <p><span class="stop">NO NEW TIFF · DO NOT SUBMIT</span></p>
    <p>This is an auditable review of nine public, historical references. They are <strong>downloadable for research</strong> from their owner repositories, but no artifact is unique under the requested pairwise rule and none is cleared for a competition slot. The pinned literal witness is positive on <strong>{protocol['footprint_cells']:,}/{protocol['footprint_cells']:,}</strong> finite template cells, so any nonempty in-footprint prediction has literal overlap <strong>1.000 &gt; 0.70</strong>. No file, holdout score, or experiment was generated in this review.</p>
    <p class="notice"><strong>Separate current-main artifact — BLINDEXT (not part of this review):</strong> upstream main ({_e(data['current_upstream_main_context']['verified_main_commit'][:7])}) contains a concurrent <a href="downloads/{_e(Path(data['current_upstream_main_context']['artifact_path']).name)}">research TIFF</a> (SHA-256 <code>{_e(data['current_upstream_main_context']['artifact_sha256'])}</code>; <a href="downloads/{_e(Path(data['current_upstream_main_context']['run_card_path']).name)}">run card</a>). Its run card records one experiment, no HOLDOUT-DTI result, a duplicate stop (literal overlap 1.000 and |ρ|=1.000), zero slots, and no submission clearance. It is downloadable for research only; do not upload it. This review did not create or holdout-evaluate it.</p>
    <p><a href="downloads/focus_sites_release_review_20261026.json"><strong>Download complete machine-readable comparison, hashes, source commits, format gates, and all 36 pair results</strong></a> · <a href="HYPOTHESES_20261026_SITE_REVIEW.md">Ranked untried hypothesis screen</a></p>
  </aside>
  <section aria-labelledby="exec"><h2 id="exec">Executive conclusion</h2>
    <div class="summary-grid">
      <article><strong>Strongest reported reference</strong><br>{_e(top['site'])} <code>{_e(top['submission_name'])}</code>, <strong>{top['score_claim']:.4f} CLAIM</strong>; no organizer receipt.</article>
      <article><strong>Current official leaderboard</strong><br>Unknown. User snapshots {', '.join(str(x['score']) for x in data['leaderboard_claims']['conflicting_unverified_claims'][:2])} conflict; an owner page reports {_e(data['leaderboard_claims']['conflicting_unverified_claims'][2]['score'])} but is secondary.</article>
      <article><strong>Research download</strong><br>Yes — owner-published reference TIFFs. Do not mistake them for a new GEMSDOE92 candidate.</article>
      <article><strong>Submission clearance</strong><br><span class="stop">NONE</span> · No weekly slot used; separate human selector required.</article>
    </div>
  </section>
  <section aria-labelledby="reference"><h2 id="reference">Why GEMSDOE32 / R0 is the best reference among these claims</h2>
    <p>The public GEMSDOE32 <code>h33-h33-2-b2</code> zero-outside raster matches the locally pinned R0 bytes (SHA-256 <code>{_e(top['raster_sha256'])}</code>). Verified lineage: {_e(top['local_lineage'])}</p>
    <p><strong>Plausible mechanism, not causal proof:</strong> under the project's vendored DTI definition, a 300 m triangular kernel weights false positives by α=0.2 and false negatives by β=0.8. Thinning can remove redundant false-positive mass while retaining nearby truth credit; a &gt;2-pixel catalogue collar can avoid spending predictions on mapped faults. Hidden truth and an organizer score-to-file receipt are absent, so this is a mechanistic explanation only.</p>
    <p>Methods diverge from the denser 1.5-pixel H19-5 thinning (GEMSDOE24), the gap-closure extension (GEMSDOE27), the 1-pixel catalogue collar (GEMSDOE31), the exact R0 2-pixel collar (GEMSDOE32), and the Anderson PINN superset (GEMSDOE36). GEMSDOE25 and GEMSDOE30 are identical in-footprint masks despite different file hashes. The complete identities and measurements are in the JSON.</p>
  </section>
  <section aria-labelledby="table"><h2 id="table">Site-by-site table</h2>
    <p>All scores below are claims supplied in the owner-report ledger. “Estimated score” is intentionally blank: there is no exact-file HOLDOUT-DTI or organizer receipt. The download links point to format-safe historical reference encodings used for pixel comparison; they are <strong>not cleared submissions</strong>.</p>
    <div class="table-wrap"><table><thead><tr><th scope="col">Site / claimed submission</th><th scope="col">Highest reported score / provenance</th><th scope="col">Download / reference file</th><th scope="col">Supportable estimated score</th><th scope="col">Uniqueness status</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
    <p>All nine selected references passed 9/9 shared strict <em>format-only</em> gates. Every one fails uniqueness versus at least one of the other eight, and all 36 pairs breach the configured symmetric pairwise stop in at least one direction. These nine-site comparisons are diagnostic, not a complete global registry clearance. Exact in-footprint prediction match: <strong>{exact_text}</strong> (the files are not byte-identical).</p>
  </section>
  <section aria-labelledby="provenance"><h2 id="provenance">Provenance conflicts and irregularities</h2>
    <ul><li>GEMSDOE32's current owner page labels 0.2778 an owner report, with no submission-page receipt binding score to raster; it says the file was already submitted and not to resubmit.</li>
      <li>The prompt's .4413 and .3195 leaderboard snapshots conflict. GEMSDOE32's owner page reports .4437 as a public-page leader. No live organizer page was accessed, so the current official leader is not asserted.</li>
      <li>GEMSDOE33's owner-maintained “receipt” JSON contains an expected DTI range, not a score receipt; its note-length field is 158 characters (&gt;140).</li>
      <li>All 17 public TIFF variants were retrieved via GitHub blobs; Git blob SHA-1 and SHA-256 were verified. Each main-branch tree was rechecked at the commit pinned in the evidence JSON.</li></ul>
  </section>
  <section aria-labelledby="submit"><h2 id="submit">Submission guidance</h2>
    <p class="notice"><strong>Do not upload any file linked on this page.</strong> No linked artifact is cleared. For a future artifact only after the page explicitly says “OK TO SUBMIT”:</p>
    <ol><li>Use the exact cleared TIFF; automatically reopen it and validate single-band float32, EPSG:32611, 3730×3292, exact transform, finite values in [0,1], no NaNs in footprint, and required zero-outside encoding.</li>
      <li>Run the unchanged pre-placement and final-dot uniqueness checks; stop if |ρ| &gt; 0.90 or &gt;70% of candidate dots fall within 3 pixels of any registry raster.</li>
      <li>Use a distinct submission name and an optional note of at most 140 characters. Do not use a research-only file.</li>
      <li>Only a human selector may choose a weekly slot. After clearance, upload through the official <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">DrivenData submissions page</a> and preserve the actual organizer receipt, binding it to the uploaded file's SHA-256.</li></ol>
  </section>
  <section aria-labelledby="sources"><h2 id="sources">Official and reference sources</h2>
    <p>These are source links, not claims of live verification. In this run the sandbox could access GitHub, but not the official competition/data hosts; no current leaderboard, submission receipt, or upstream source page was fetched.</p><ul>{source_items}</ul>
  </section>
  <section><h2>Auditable downloads and status</h2><ul>
    <li><a href="downloads/focus_sites_release_review_20261026.json">Full public JSON evidence</a> (17 variants, 9 selected artifacts, 36 pairwise comparisons, source commits, checksums, and format-gate details).</li>
    <li><a href="HYPOTHESES_20261026_SITE_REVIEW.md">Five-hypothesis ranked screen</a>; no candidate was evaluated because the pre-placement stop bound.</li>
    <li>Corrected rejection-only audit card: <a href="https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/evidence/review_20261026_gemsdoe_sites_run_card_v2.json">v2 JSON</a> (`new_unique_tiff_generated=false`, `experiments=0`, `weekly_slots_used=0`).</li>
    <li>Prior pre-fix card is retained but superseded: <a href="https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/evidence/review_20261026_gemsdoe_sites_SUPERSESSION.md">counter-correction note</a>.</li>
  </ul></section>
  <footer><p>Reviewed 2026-10-26. Evidence class: REGISTRY-MEASUREMENT for raster comparisons; CLAIM for owner-reported scores. No HOLDOUT-DTI or ORGANIZER-CONFIRMED score was generated. Footprint SHA-256: <code>{_e(protocol['footprint_sha256'])}</code>.</p></footer>
</main></body></html>\n'''


def generate(data: dict) -> dict[Path, str]:
    return {
        MARKDOWN: render_markdown(data),
        HTML: render_html(data),
        PUBLIC_JSON: json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if rendered files are stale")
    args = parser.parse_args(argv)
    try:
        data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        outputs = generate(data)
        stale = []
        for path, content in outputs.items():
            if args.check:
                if not path.is_file() or path.read_text(encoding="utf-8") != content:
                    stale.append(str(path.relative_to(ROOT)))
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
        if stale:
            print("STALE focus-site review output(s): " + ", ".join(stale), file=sys.stderr)
            return 1
        if args.check:
            print("focus-site review render check: OK")
        else:
            print("Rendered: " + ", ".join(str(p.relative_to(ROOT)) for p in outputs))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"focus-site review render failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
