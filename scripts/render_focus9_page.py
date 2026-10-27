#!/usr/bin/env python3
"""Render the evidence-bound nine-site executive review without score promotion.

The nine owner reports, the independently rechecked literal witness, the
current primary status, and the estimator audit are separate sources. Render
fails closed if those sources disagree or the research TIFF's hash has changed.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = DOCS / "focus9.html"
FOCUS = DOCS / "downloads/focus_sites_release_review_20261026.json"
REVIEW = DOCS / "downloads/review_14f85876_run_card.json"
LATEST_REVIEW = DOCS / "downloads/review_b4bb558b_run_card.json"
STATUS = DOCS / "downloads/readiness.json"
MODEL_AUDIT = DOCS / "downloads/score_estimator_audit_14f85876.json"
PAIRWISE = DOCS / "downloads/focus9_pairwise_recheck_14f85876.json"
SITES = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")


def _load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render() -> str:
    focus, review, status, model, recheck, latest = map(
        _load, (FOCUS, REVIEW, STATUS, MODEL_AUDIT, PAIRWISE, LATEST_REVIEW))
    if (latest.get('verdict') != 'negative' or latest.get('submission_eligible') is not False
            or latest.get('new_unique_tiff_generated') is not False
            or latest.get('experiments') != 0 or latest.get('weekly_slots_used') != 0):
        raise ValueError('latest review is not a rejection-only result')
    if (review.get("verdict") != "negative" or review.get("submission_eligible") is not False
            or review.get("new_unique_tiff_generated") is not False
            or review.get("experiments") != 0 or review.get("weekly_slots_used") != 0):
        raise ValueError("review must remain rejection-only")
    proof = review["correlation_overlap_vs_registry"]["preplacement_proof"]
    if (proof["universal_nonempty_in_footprint_overlap_stop"] is not True
            or proof["positive_in_footprint"] != proof["footprint_pixels"]
            or proof["forward_overlap_for_any_nonempty_in_footprint_dot_set"] != 1.0):
        raise ValueError("missing literal duplicate proof")
    if (status.get("submission_eligible") is not False or status.get("verdict") != "negative"
            or status.get("raster_sha256") != review.get("raster_sha256")
            or "docs/" + status.get("file", "") != review.get("primary_download")):
        raise ValueError("current research status disagrees with the review")
    primary_rel = status["file"]
    primary = DOCS / primary_rel
    if (not primary.resolve().is_relative_to((DOCS / "downloads").resolve())
            or hashlib.sha256(primary.read_bytes()).hexdigest() != status["raster_sha256"]):
        raise ValueError("primary research bytes or path invalid")
    if not 0 < len(status["note"]) <= 140 or not 0 < len(status["submission_name"]) <= 140:
        raise ValueError("historical form fields exceed 140 characters")
    if (model["valid_leaderboard_prediction"] is not False
            or model["individual_prediction_interval_available"] is not False
            or model["source_sha256"] != hashlib.sha256(
                (ROOT / "evidence/score_estimator_20261026.json").read_bytes()).hexdigest()):
        raise ValueError("model audit is stale or incorrectly claims validation")
    if (recheck["source_sha256"] != hashlib.sha256(FOCUS.read_bytes()).hexdigest()
            or recheck["sample_sha256"] != proof["sample_sha256"]
            or hashlib.sha256(PAIRWISE.read_bytes()).hexdigest() != review["focus_pairwise_correction"]["sha256"]
            or recheck["pairs"] != 36 or len(recheck["comparisons"]) != 36
            or recheck["all_pairs_duplicate_in_at_least_one_direction_or_rho"] is not True):
        raise ValueError("independent pairwise evidence is stale or incomplete")
    sites = focus["selected_site_artifacts"]
    if tuple(r["site"] for r in sites) != SITES or tuple(recheck["sites"]) != SITES:
        raise ValueError("focus-site inventory is incomplete")
    rows = []
    for row in sites:
        ref = row["comparison_reference"]
        link = ref["raw_download_url"]
        parsed = urlsplit(link)
        if parsed.scheme != "https" or parsed.netloc != "github.com":
            raise ValueError("untrusted research download URL")
        if (row["organizer_receipt_verified"] is not False
                or row["cleared_to_submit"] is not False):
            raise ValueError("focus row claims unsupported clearance")
        candidates = []
        for pair in recheck["comparisons"]:
            if pair["site_a"] == row["site"]:
                candidates.append((pair["forward_3px_overlap_a_to_b"], pair["site_b"]))
            elif pair["site_b"] == row["site"]:
                candidates.append((pair["forward_3px_overlap_b_to_a"], pair["site_a"]))
        if len(candidates) != 8:
            raise ValueError("incomplete per-site pairwise comparison")
        overlap, witness = max(candidates)
        if overlap <= 0.70:
            raise ValueError("no directed-overlap rejection for a site")
        rows.append(
            f'<tr><th scope="row">{_esc(row["site"])}</th>'
            f'<td><a href="{_esc(link)}">Research TIFF</a><br><small>{_esc(Path(ref["path"]).name)}</small></td>'
            f'<td>{row["reported_score"]:.4f} <strong>CLAIM</strong><br><small>No organizer receipt</small></td>'
            f'<td>Not supportable</td>'
            f'<td>Duplicate vs {_esc(witness)}; directed overlap '
            f'{overlap:.4f} <small>(3 px)</small></td>'
            f'<td><strong>DO NOT SUBMIT</strong></td></tr>'
        )
    salem = review["historical_salemseismo_correction"]
    salem_rel = salem["artifact"].removeprefix("docs/")
    if hashlib.sha256((DOCS / salem_rel).read_bytes()).hexdigest() != salem["sha256"]:
        raise ValueError("historical SALEMSEISMO bytes changed")
    note = status["note"]
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nine-site executive review — GEMSDOE92</title><link rel="stylesheet" href="style.css">
<style>
main{{max-width:76rem;margin:auto;padding:1rem;font:1rem/1.55 system-ui,sans-serif;color:#17212b}}
nav{{display:flex;flex-wrap:wrap;gap:1rem}} section{{margin:1rem 0;padding:1rem;border:1px solid #cbd5e1;border-radius:8px}}
.stop{{border:3px solid #991b1b;background:#fff7ed}} .badge{{display:inline-block;background:#991b1b;color:white;padding:.3rem .6rem;border-radius:4px;font-weight:800}}
.button{{display:inline-block;background:#1e3a5f;color:white;padding:.65rem .85rem;border-radius:5px;font-weight:700}}
.wrap{{overflow-x:auto}} table{{border-collapse:collapse;min-width:920px;width:100%}} th,td{{border:1px solid #cbd5e1;padding:.55rem;text-align:left;vertical-align:top}} th{{background:#eff6ff}} small{{color:#475569}} code{{overflow-wrap:anywhere}}
</style></head><body><main>
<nav><a href="index.html">Home</a><a href="executive-summary.html">Executive summary</a><a href="SUBMIT.html">Submission guidance</a><a href="HYPOTHESES_20261026_SITE_REVIEW.md">Ranked hypotheses</a></nav>
<section class="stop"><h1>Nine-site executive review</h1>
<p><span class="badge">DO NOT SUBMIT — NO ELIGIBLE TIFF</span> <strong>OK TO DOWNLOAD FOR RESEARCH</strong></p>
<p><a class="button" href="{_esc(primary_rel)}" download>Download historical VARIO research TIFF</a>
 · <a href="downloads/review_b4bb558b_run_card.json">Latest negative run card</a> · <a href="downloads/readiness.json">Current status</a></p>
<p>File: <code>{_esc(Path(primary_rel).name)}</code> · SHA-256: <code>{_esc(status["raster_sha256"])}</code>.<br>
Historical reference name: <code>{_esc(status["submission_name"])}</code>; note ({len(note)}/140): <code>{_esc(note)}</code>. These are identifiers, <strong>not upload instructions</strong>.</p>
<p>No new raster or geological experiment was generated in this review; no slot was used. A pinned registry raster is positive at all {proof["footprint_pixels"]:,} finite template pixels, so every nonempty in-footprint candidate has literal overlap 1.000 &gt; 0.70. This is a binding pre-placement stop, not a format error. See the <a href="downloads/review_b4bb558b_run_card.json">fresh hash-bound proof</a>.</p>
<p><strong>27 October update:</strong> The witness was freshly fetched and rechecked; all 36 nine-site comparisons were independently rerun and match the earlier corrected receipt. The 12 pinned owner-mirror inputs, including the 19-band stack, were verified in an ephemeral cache. This does not establish organizer provenance, redistribution rights, holdout validity, or eligibility. <a href="downloads/input_cache_b4bb558b.json">Input audit</a>. An <a href="REVIEW_20261027_A3DCC0DD.md">independent concurrent review</a> reproduced the same stop (<a href="downloads/review_a3dcc0dd_run_card.json">its run card</a>).</p>
</section>
<section><h2>Executive conclusion</h2><p>Of the nine owner-reported values below, <strong>GEMSDOE32: 0.2778 CLAIM</strong> is highest. It is not an organizer-confirmed score: no submission-page receipt binds it to the raster. A higher public result is possible in principle, but this project has not demonstrated one with a unique, eligible file. No defensible leaderboard estimate is available for the research TIFF.</p>
<p>The <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">official leaderboard</a> is not mirrored or automatically monitored. <a href="https://www.drivendata.org/termsofuse/">DrivenData terms</a> prohibit automated access for monitoring or copying; no leaderboard row is a project receipt.</p></section>
<section><h2>Every requested site</h2><p>Scores are owner <strong>CLAIM</strong>s, not organizer receipts. Downloads are historical reference encodings, not cleared submissions. “Estimated DTI” is unavailable; none has a trustworthy exact-file leaderboard prediction. The directed overlap is against one other selected site, not an exhaustive registry clearance.</p>
<div class="wrap"><table><thead><tr><th>Site</th><th>Download for research</th><th>Reported value / provenance</th><th>Estimated DTI</th><th>Unique vs the 9 sites?</th><th>Eligibility</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p>All 36 selected site pairs breach the configured symmetric pairwise stop in at least one direction. The independent row-safe recheck corrected numeric overlap values in {recheck['pairs_with_changed_metrics']} pairs; duplicate decisions did not change, and the cause of the earlier discrepancy is unproven. <a href="downloads/focus9_pairwise_recheck_14f85876.json">Corrected pairwise measurements</a> · <a href="downloads/focus_sites_release_review_20261026.json">Earlier evidence, file hashes, and source commits</a>. GEMSDOE25 and GEMSDOE30 have identical in-footprint prediction arrays despite different bytes. GEMSDOE36 contains R0 plus 1,200 dots.</p></section>
<section><h2>Repeat the automated project review</h2>
<p>The <a href="REVIEW_E7BC063A.md">27 October three-pass review</a> independently reproduced the pinned-witness STOP and adds a single command for the shared proof, full tests, manifest, parent, all served research-file gates and generated-evidence freshness checks. It does not train, create a TIFF, estimate an organizer score or select a weekly slot.</p>
<pre><code>.venv/bin/python scripts/review_project.py --fetch-witness --output .cache/review-NEW-ID.json</code></pre>
<p>Run from the repository with dependencies installed; use a fresh receipt path. Exit 1 means engineering checks passed but the confirmed protocol STOP remains. Exit 2 means failed, incomplete or inconclusive checks. <strong>Both mean DO NOT SUBMIT.</strong> The output JSON distinguishes the old research-file validator from the absence of a new submission.</p></section>
<section><h2>Why 0.2778? What would it take to beat it?</h2>
<p>R0 (<code>h33-h33-2-b2</code>) is a descendant of H19-5: D2.8 has 44,090 dots, then a &gt;2-pixel catalogue-distance filter leaves 37,654. Thinning can reduce redundant predicted mass while retaining nearby credit under a 300 m triangular kernel. That is a plausible mechanism, not causal proof of the claimed value. <a href="https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2">DrivenData staff clarify</a> that known USGS/INGENIOUS fault pixels are excluded from evaluation; do not assume that removing those exact pixels avoids false-positive penalties, or infer the treatment of a surrounding collar.</p>
<p>Before a slot, a newly assigned method would need a genuine spatially blocked, fold-rebuilt, visible-fault-only holdout win over the same-evaluator best control, individual feature leakage canaries, complete pre-placement and final uniqueness checks, and byte-bound format validation. The <a href="HYPOTHESES_20261026_SITE_REVIEW.md">five ranked hypotheses</a> are untried; the top one is blocked, not disproven.</p></section>
<section><h2>Limits of the earlier estimate and SALEMSEISMO</h2>
<p>The archived model used {model["training_rows"]} owner CLAIMs. Row-wise leave-one-out mixed related or identical-feature rows and selected its saturation cap globally; its RMSE is <strong>not</strong> a per-file ± prediction interval. A partial leave-group-out diagnostic still uses claim labels and is not nested, so it cannot validate an estimate. <a href="downloads/score_estimator_audit_14f85876.json">Reproducible diagnostic</a>.</p>
<p>The historical <a href="{_esc(salem_rel)}" download>SALEMSEISMO research TIFF</a> (SHA-256 <code>{_esc(salem["sha256"])}</code>) remains available for research only. Its runner placed/wrote files before its public scan, and its public rank-correlation check used selected witnesses, not every raster. Static re-scores of already-built predictions and full-catalogue-derived masks do not prove leakage-free prospective holdout performance. A former fast scan also allowed row-boundary wrap in its halo calculations; old scan values need rechecking. Its runner is disabled; <strong>do not submit</strong>.</p></section>
<section><h2>Submission guide — future cleared artifact only</h2><ol>
<li>Stop now: the literal registry rule blocks all nonempty candidates. A sparse-only or matched-budget comparison is not a waiver.</li>
<li>If the protocol is legitimately resolved in a later session, validate the exact file automatically: single-band float32, matching CRS, dimensions and transform, finite in-range values inside bounds, and the required outside-bounds encoding.</li>
<li>The <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">official instructions</a> say null or NaN outside study-area bounds. Local gates instead verify finite zeros outside the sample's finite footprint to address the reported range error. These are not proven equivalent, and a local PASS is not a portal receipt.</li>
<li>Only after every gate and the separate selector approve: use that new file's own name and note (each at most 140 characters), verify the weekly limit on the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">official submission page</a>, and record any organizer receipt against the exact file SHA-256. This session selected and spent no slot.</li></ol></section>
<section><h2>Official research &amp; evidence</h2><p><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Task, metric and format</a> · <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Official rules</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution">Reference solution</a> · <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a> · <a href="https://www.usgs.gov/3d-elevation-program">USGS 3DEP</a> · <a href="https://gdr.openei.org/submissions/1391">GDR INGENIOUS (CC BY 4.0)</a>.</p>
<p>Public source documentation is not proof of data coverage, provenance, predictive value, or access to authenticated competition files. <a href="downloads/review_14f85876_run_card.json">Full session run card</a> · <a href="SITE_REVIEW_20261026.html">Earlier detailed site forensic review</a>.</p></section>
<footer><small>Site comparison recorded 2026-10-26; proof and inputs rechecked 2026-10-27 UTC. No candidate score or organizer receipt is invented.</small></footer>
</main></body></html>\n'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        text = render()
        if args.check:
            if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != text:
                print("STALE nine-site executive page", file=sys.stderr)
                return 1
            print("nine-site executive page: OK")
        else:
            OUTPUT.write_text(text, encoding="utf-8")
            print(f"wrote {OUTPUT}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"nine-site render failed closed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
