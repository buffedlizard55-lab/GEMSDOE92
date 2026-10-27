#!/usr/bin/env python3
"""Render the evidence-bound nine-site and multi-owner executive review without score promotion.

The nine owner reports, the independently rechecked literal witnesses, the
current primary status, the GitHub ref freshness snapshot, the 2026-10-27
multi-owner delta receipt, and the estimator audit are separate sources. Render
fails closed if those sources disagree or the research TIFF's hash has changed.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = DOCS / "focus9.html"
FOCUS = DOCS / "downloads/focus_sites_release_review_20261026.json"
REVIEW = DOCS / "downloads/review_14f85876_run_card.json"
LATEST_REVIEW = DOCS / "downloads/review_b4bb558b_run_card.json"
D30_REVIEW = DOCS / "downloads/review_d30d387c_run_card.json"
FLEET_20261027 = DOCS / "downloads/fleet_20261027_audit_d30d387c.json"
STATUS = DOCS / "downloads/readiness.json"
MODEL_AUDIT = DOCS / "downloads/score_estimator_audit_14f85876.json"
PAIRWISE = DOCS / "downloads/focus9_pairwise_recheck_14f85876.json"
FRESHNESS = DOCS / "downloads/session_b97812a3_focus_freshness.json"
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
    focus, review, status, model, recheck, latest, freshness, d30, fleet = map(
        _load, (FOCUS, REVIEW, STATUS, MODEL_AUDIT, PAIRWISE, LATEST_REVIEW, FRESHNESS, D30_REVIEW, FLEET_20261027))
    if (latest.get('verdict') != 'negative' or latest.get('submission_eligible') is not False
            or latest.get('new_unique_tiff_generated') is not False
            or latest.get('experiments') != 0 or latest.get('weekly_slots_used') != 0):
        raise ValueError('latest review is not a rejection-only result')
    if (d30.get('verdict') != 'negative' or d30.get('submission_eligible') is not False
            or d30.get('new_unique_tiff_generated') is not False
            or d30.get('experiments') != 0 or d30.get('weekly_slots_used') != 0
            or len(fleet.get('prompt_20261027_delta_artifacts', [])) != 11
            or len(fleet.get('multi_owner_repositories_20261027', [])) != 12):
        raise ValueError('d30d387c review or fleet audit is incomplete')
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
    fresh_rows = freshness.get("sites")
    if (freshness.get("schema") != "gemsdoe92-github-focus-freshness-v1"
            or freshness.get("inventory_sha256") != hashlib.sha256(FOCUS.read_bytes()).hexdigest()
            or freshness.get("submission_eligible") is not False
            or not isinstance(fresh_rows, list)
            or tuple(r.get("site") for r in fresh_rows) != SITES):
        raise ValueError("GitHub freshness snapshot is inconsistent with the pinned inventory")
    changed_count = sum(r.get("status") == "changed" for r in fresh_rows)
    unknown_count = sum(r.get("status") == "unknown" for r in fresh_rows)
    if (freshness.get("changed_count") != changed_count or freshness.get("unknown_count") != unknown_count
            or not isinstance(freshness.get("observed_utc"), str)):
        raise ValueError("GitHub freshness snapshot counts or time are invalid")
    rows = []
    for row, fresh in zip(sites, fresh_rows):
        pin, observed = fresh.get("pinned_commit"), fresh.get("observed_main_commit")
        state = fresh.get("status")
        expected = "unknown" if observed is None else ("unchanged" if pin == observed else "changed")
        if (pin != row.get("repository_commit") or not isinstance(pin, str)
                or not re.fullmatch(r"[0-9a-f]{40}", pin)
                or (observed is not None and (not isinstance(observed, str)
                    or not re.fullmatch(r"[0-9a-f]{40}", observed)))
                or state != expected):
            raise ValueError("GitHub freshness row is inconsistent")
        initial = {"changed": "Main ref changed since pinned audit; artifacts not re-audited",
                   "unchanged": "Same main ref as pinned audit; artifacts not re-audited",
                   "unknown": "GitHub check unavailable — historical snapshot only"}[fresh["status"]]
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
            f'<td><span data-focus-repo="{_esc(row["site"])}" '
            f'data-pinned-sha="{_esc(row["repository_commit"])}" '
            f'data-freshness="{_esc(fresh["status"])}">{_esc(initial)}</span></td>'
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
    delta_rows = []
    for item in fleet["prompt_20261027_delta_artifacts"]:
        raw_url = f'https://github.com/{item["owner"]}/{item["site"]}/raw/HEAD/{item["path"]}'
        parsed_d = urlsplit(raw_url)
        if parsed_d.scheme != "https" or parsed_d.netloc != "github.com":
            raise ValueError("untrusted delta research download URL")
        if item["strict_submission_encoding_gates_pass"] is not True:
            raise ValueError("delta artifact failed strict submission encoding gates")
        if item["ov3_vs_13gemsdoe_r13_lattice"] <= 0.70 or item["ov3_vs_17gemsdoe_dense"] <= 0.70:
            raise ValueError("delta artifact unexpectedly cleared dual witnesses")
        claim_cell = (
            f'{item["reported_claim_score"]:.4f} <strong>CLAIM</strong><br><small>No organizer receipt</small>'
            if item["reported_claim_score"] is not None
            else 'Unscored in brief<br><small>No organizer receipt</small>'
        )
        hd = item["holdout_dti_static_diagnostic"]
        delta_rows.append(
            f'<tr><th scope="row">{_esc(item["site"])}</th>'
            f'<td><a href="{_esc(raw_url)}">Research TIFF</a><br>'
            f'<small>{_esc(Path(item["path"]).name)} ({item["positive_in_footprint"]:,} dots · SHA-256 <code>{_esc(item["sha256"][:12])}…</code> · 11/11 [0,1] gates PASS)</small></td>'
            f'<td>{claim_cell}</td>'
            f'<td><strong>HOLDOUT-DTI</strong> (static diagnostic, <code>{_esc(hd["evaluator_version"])}</code>, {hd["withheld_positive_pixels"]:,} withheld px): '
            f'{hd["dti"]:.6f} [{hd["ci95"][0]:.6f}, {hd["ci95"][1]:.6f}]<br><small>Not a leaderboard estimate</small></td>'
            f'<td>vs R0: {item["ov3_vs_r0"]:.4f} · vs 13GEMSDOE binary lattice: {item["ov3_vs_13gemsdoe_r13_lattice"]:.4f} '
            f'· vs 17GEMSDOE: {item["ov3_vs_17gemsdoe_dense"]:.4f} <small>(3 px &gt; 0.70)</small></td>'
            f'<td><strong>DO NOT SUBMIT</strong></td></tr>'
        )
    owner_rows = []
    for m in fleet["multi_owner_repositories_20261027"]:
        repo_url = f'https://github.com/{m["owner"]}/{m["repo"]}'
        status_note = (
            "Stub repository (README.md only; 0 GeoTIFF blobs)"
            if m["stub_readme_only"]
            else f'{m["tiff_blob_count"]} GeoTIFF blob(s) on {m["default_branch"]}; audited under 5-owner scanner'
        )
        owner_rows.append(
            f'<tr><th scope="row"><a href="{_esc(repo_url)}">{_esc(m["owner"] + "/" + m["repo"])}</a></th>'
            f'<td>{m["total_blobs"]}</td><td>{m["tiff_blob_count"]}</td>'
            f'<td>{_esc(status_note)}</td><td><strong>DO NOT SUBMIT</strong></td></tr>'
        )
    w_bin = next(
        w for w in fleet["dual_witness_preplacement_certificate"]["witnesses"]
        if w["id"] == "binary_lattice_13gemsdoe"
    )
    note = status["note"]
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nine-site &amp; multi-owner executive review — GEMSDOE92</title><link rel="stylesheet" href="style.css">
<script defer src="focus-freshness.js"></script>
<style>
body{{background:#f5f7fb;color:#17212b}} main{{max-width:76rem;margin:auto;padding:1rem;font:1rem/1.55 system-ui,sans-serif;color:#17212b}}
a{{color:#164e8a}} a:focus-visible,.wrap:focus-visible{{outline:3px solid #1d4ed8;outline-offset:3px}}
nav{{display:flex;flex-wrap:wrap;gap:1rem}} section{{max-width:none;margin:1rem 0;padding:1rem;border:1px solid #cbd5e1;border-radius:8px;background:#fff}}
.stop{{border:3px solid #991b1b;background:#fff7ed}} .badge{{display:inline-block;background:#991b1b;color:white;padding:.3rem .6rem;border-radius:4px;font-weight:800}}
.button{{display:inline-block;background:#1e3a5f;color:white;padding:.65rem .85rem;border-radius:5px;font-weight:700}}
.wrap{{overflow-x:auto}} table{{border-collapse:collapse;min-width:1100px;width:100%}} th,td{{border:1px solid #cbd5e1;padding:.55rem;text-align:left;vertical-align:top}} th{{background:#eff6ff}} small,footer{{color:#475569}} code{{overflow-wrap:anywhere}}
</style></head><body><main>
<nav><a href="index.html">Home</a><a href="executive-summary.html">Executive summary</a><a href="SUBMIT.html">Submission guidance</a><a href="HYPOTHESES_20261027_D30D387C.md">2026-10-27 untried hypotheses</a><a href="HYPOTHESES_20261026_SITE_REVIEW.md">Ranked hypotheses</a><a href="REVIEW_20261027_D30D387C.md">Session d30d387c PhD audit</a></nav>
<section class="stop"><h1>Nine-site &amp; multi-owner executive review</h1>
<p><span class="badge">DO NOT SUBMIT — NO ELIGIBLE TIFF</span> <strong>OK TO DOWNLOAD FOR RESEARCH</strong></p>
<p><a class="button" href="{_esc(primary_rel)}" download>Download historical VARIO research TIFF</a>
 · <a href="downloads/review_d30d387c_run_card.json">Session d30d387c negative run card</a> · <a href="downloads/fleet_20261027_audit_d30d387c.json">Dual-witness &amp; 2026-10-27 fleet receipt</a> · <a href="downloads/session_b97812a3_run_card.json">b97812a3 negative run card</a> · <a href="downloads/readiness.json">Current status</a></p>
<p>File: <code>{_esc(Path(primary_rel).name)}</code> · SHA-256: <code>{_esc(status["raster_sha256"])}</code>.<br>
Historical reference name: <code>{_esc(status["submission_name"])}</code>; note ({len(note)}/140): <code>{_esc(note)}</code>. These are identifiers, <strong>not upload instructions</strong>.</p>
<p>No new raster, geological experiment or slot was generated in this review. A pinned, <strong>continuous-probability</strong> registry raster is positive at all {proof["footprint_pixels"]:,} finite template pixels. If every positive pixel is treated as a dot, every nonempty in-footprint candidate has literal overlap 1.000 &gt; 0.70. In addition, session <code>d30d387c</code> proved that even among pure <code>{{0, 1}}</code> binary-dot submissions, <code>13GEMSDOE</code> <code>r13-lattice-s5</code> ({w_bin["positive_in_footprint"]:,} binary 1.0 dots, owner <strong>CLAIM</strong> 0.0904) covers {w_bin["halo_3px_in_footprint"]:,} / {proof["footprint_pixels"]:,} footprint cells within 3 px, forcing a mathematical pigeonhole overlap &ge; {w_bin["pigeonhole_min_overlap_at_37654_dots"]:.4f} &gt; 0.70 at the 37,654-dot budget (0.9857–1.0000 observed across all 11 newly audited October 25–27 brief artifacts). This conservative pre-placement stop is a representation ambiguity, not proof of geological identity; do not silently waive the stop. <a href="downloads/session_b97812a3_preflight_final.json">Fresh hash-bound preflight</a> · <a href="downloads/session_b97812a3_witness_support.json">Witness value statistics</a> · <a href="downloads/fleet_20261027_audit_d30d387c.json">Dual-witness &amp; fleet receipt</a>.</p>
<p><strong>27 October update:</strong> All 12 core + 7 external pinned owner-mirror inputs, including the 19-band stack, were verified in an ephemeral cache (uncovering 3,061–3,073 interior finite <code>-3.4028235e+38</code> sentinel cells and proving <code>Band 6 tc</code> is GeoDAWN Radiometric Total Count rather than magnetic tilt). This does not establish organizer provenance, redistribution rights, holdout validity, or eligibility. <a href="downloads/input_cache_d30d387c.json">d30d387c input audit</a> · <a href="downloads/session_b97812a3_input_audit.json">b97812a3 input audit</a> · <a href="REVIEW_20261027_D30D387C.md">d30d387c PhD review</a> · <a href="REVIEW_20261027_B97812A3.md">b97812a3 review</a> · <a href="REVIEW_20261027_A3DCC0DD.md">a3dcc0dd review</a>.</p>
</section>
<section><h2>Executive conclusion</h2><p>Of the nine owner-reported values below (and across the expanded October 25–27 multi-owner list), <strong>GEMSDOE32: 0.2778 CLAIM</strong> is highest; the highest newly added October 26 owner report is <strong>GEMSDOE27 (<code>h31-drcg-wl-celf28</code>): 0.2250 CLAIM</strong>, followed by <strong>GEMSDOE36 (<code>kpl36-exp3</code>): 0.1647 CLAIM</strong>. It is not an organizer-confirmed score: no submission-page receipt binds it to the raster. A higher public result is possible in principle, but this project has not demonstrated one with a unique, eligible file. No defensible leaderboard estimate is available for the research TIFF.</p>
<p>The <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">official leaderboard</a> is not mirrored or automatically monitored. <a href="https://www.drivendata.org/termsofuse/">DrivenData terms</a> prohibit automated access for monitoring or copying; no leaderboard row is a project receipt.</p></section>
<section><h2>Every requested site — frozen historical audit</h2><p><strong>Not a current or complete inventory.</strong> At {_esc(freshness['observed_utc'])}, GitHub main refs had changed for {changed_count} of 9 sites; {unknown_count} checks were unavailable. The table below describes the selected files at the pinned 26 October commits; the newly added October 25–27 brief artifacts from those updated repositories are audited in the next section. <a href="downloads/session_b97812a3_focus_freshness.json">GitHub-only snapshot and source commits</a>.</p>
<p>When this page opens it attempts a live GitHub <em>commit-only</em> comparison; a changed ref does not say what changed, and even the same ref is not an artifact or score audit. If GitHub is blocked or rate-limited, the status is unknown. <span data-freshness-time aria-live="polite">Showing the dated snapshot; browser check pending if JavaScript is enabled.</span></p>
<p>Values are owner <strong>CLAIM</strong>s, not organizer receipts. Downloads are historical references, not cleared submissions. “Estimated DTI” is unavailable; none has a trustworthy exact-file leaderboard prediction. Directed overlap is against one other selected historical site, not exhaustive registry clearance.</p>
<div class="wrap" tabindex="0" aria-label="Scrollable historical nine-site table"><table><thead><tr><th scope="col">Site</th><th scope="col">GitHub main freshness</th><th scope="col">Download for research</th><th scope="col">Reported value / provenance</th><th scope="col">Estimated DTI</th><th scope="col">Unique vs the 9 sites?</th><th scope="col">Eligibility</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p>All 36 selected site pairs breach the configured symmetric pairwise stop in at least one direction. The independent row-safe recheck corrected numeric overlap values in {recheck['pairs_with_changed_metrics']} pairs; duplicate decisions did not change, and the cause of the earlier discrepancy is unproven. <a href="downloads/focus9_pairwise_recheck_14f85876.json">Corrected pairwise measurements</a> · <a href="downloads/focus_sites_release_review_20261026.json">Earlier evidence, file hashes, and source commits</a>. GEMSDOE25 and GEMSDOE30 have identical in-footprint prediction arrays despite different bytes. GEMSDOE36 contains R0 plus 1,200 dots.</p></section>
<section><h2>October 25–27 session-brief delta artifacts &amp; multi-owner fleet</h2>
<p>All 11 newly added or hash-updated artifacts in the 2026-10-27 brief pass strict <code>[0, 1]</code> format gates, yet every one has 0.9857–1.0000 directed 3-px overlap against the pure <code>{{0, 1}}</code> binary-dot submission <code>13GEMSDOE</code> <code>r13-lattice-s5</code> as well as 1.0000 against <code>17GEMSDOE</code>. Static diagnostic <strong>HOLDOUT-DTI</strong> values below measure off-catalogue recall on buffered whole-segment holdout folds of existing catalogue faults — they are <strong>not</strong> prospective training measurements or leaderboard projections.</p>
<div class="wrap" tabindex="0" aria-label="Scrollable October 25-27 delta artifact table"><table><thead><tr><th scope="col">Site</th><th scope="col">Download &amp; format verification</th><th scope="col">Reported value / provenance</th><th scope="col">Diagnostic HOLDOUT-DTI (not leaderboard projection)</th><th scope="col">Registry overlap measurements</th><th scope="col">Eligibility</th></tr></thead><tbody>{''.join(delta_rows)}</tbody></table></div>
<h3>Newly added multi-owner repositories (KANLER / EUG / WBG / GINNY)</h3>
<div class="wrap" tabindex="0" aria-label="Scrollable multi-owner repository table"><table><thead><tr><th scope="col">Repository</th><th scope="col">Total Git blobs</th><th scope="col">GeoTIFF blobs</th><th scope="col">Forensic status</th><th scope="col">Eligibility</th></tr></thead><tbody>{''.join(owner_rows)}</tbody></table></div></section>
<section><h2>Repeat the automated project review</h2>
<p>The <a href="REVIEW_E7BC063A.md">27 October three-pass review</a> independently reproduced the pinned-witness STOP and adds a single command for the shared proof, full tests, manifest, parent, all served research-file gates and generated-evidence freshness checks. It does not train, create a TIFF, estimate an organizer score or select a weekly slot.</p>
<pre><code>.venv/bin/python scripts/review_project.py --fetch-witness --output .cache/review-NEW-ID.json</code></pre>
<p>Run from the repository with dependencies installed; use a fresh receipt path. Exit 1 means engineering checks passed but the confirmed protocol STOP remains. Exit 2 means failed, incomplete or inconclusive checks. <strong>Both mean DO NOT SUBMIT.</strong> The output JSON distinguishes the old research-file validator from the absence of a new submission.</p></section>
<section><h2>Why 0.2778? What would it take to beat it?</h2>
<p>R0 (<code>h33-h33-2-b2</code>) is a descendant of H19-5: D2.8 has 44,090 dots, then a &gt;2-pixel catalogue-distance filter leaves 37,654. Thinning can reduce redundant predicted mass while retaining nearby credit under a 300 m triangular kernel (&alpha; = 0.2 on false positives, &beta; = 0.8 on false negatives). That is a plausible mechanism, not causal proof of the claimed value. <a href="https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2">DrivenData staff clarify</a> that the known-fault mask is pixel-exact, not a surrounding buffer: nearby unmasked predictions are evaluated normally, and new labels can lie within 300 m. Removing a wider collar may therefore discard potentially useful predictions; any effect needs a controlled test. Consistent with catalogue selection-bias risk, pixelwise Positive-Unlabeled gradient boosting in <code>GEMSDOE28 s21-puhgb</code> achieved the highest static catalogue-holdout DTI among the new October 26 artifacts (0.034629) yet dropped to <strong>0.0206 CLAIM</strong>, whereas submodular ridge/lineament placement in <code>GEMSDOE27 h31-drcg-wl-celf28</code> reached <strong>0.2250 CLAIM</strong>.</p>
<p>Before a slot, a newly assigned method would need an explicit policy-owner resolution of both the <code>17GEMSDOE</code> continuous witness and the <code>13GEMSDOE</code> binary-lattice witness, masking of the 3,061–3,073 interior <code>-3.4028235e+38</code> finite sentinel pixels, a genuine spatially blocked, fold-rebuilt, visible-fault-only holdout win over the same-evaluator best control, individual feature leakage canaries, complete 5-owner pre-placement and final uniqueness checks, and byte-bound format validation. See the <a href="HYPOTHESES_20261027_D30D387C.md">five newly pre-registered 2026-10-27 untried hypotheses</a> (led by Gallardo–Meju cross-gradient decoupling) and <a href="HYPOTHESES_20261026_SITE_REVIEW.md">earlier ranked hypotheses</a>; the top one is blocked, not disproven.</p></section>
<section><h2>Limits of the earlier estimate and SALEMSEISMO</h2>
<p>The archived model used {model["training_rows"]} owner CLAIMs. Row-wise leave-one-out mixed related or identical-feature rows and selected its saturation cap globally; its RMSE is <strong>not</strong> a per-file ± prediction interval. A partial leave-group-out diagnostic still uses claim labels and is not nested, so it cannot validate an estimate. <a href="downloads/score_estimator_audit_14f85876.json">Reproducible diagnostic</a>.</p>
<p>The historical <a href="{_esc(salem_rel)}" download>SALEMSEISMO research TIFF</a> (SHA-256 <code>{_esc(salem["sha256"])}</code>) remains available for research only. Its runner placed/wrote files before its public scan, used selected witnesses rather than every raster, and misread <code>Band 6 tc</code> (GeoDAWN Radiometric Total Count, <em>r</em> = 0.99714) as Salem magnetic tilt angle (<em>r</em> = 0.01280). Static re-scores of already-built predictions and full-catalogue-derived masks do not prove leakage-free prospective holdout performance. A former fast scan also allowed row-boundary wrap in its halo calculations; old scan values need rechecking. Its runner is disabled; <strong>do not submit</strong>.</p></section>
<section><h2>Submission guide — future cleared artifact only</h2><ol>
<li>Stop now: both the continuous registry witness (<code>17GEMSDOE</code>) and the binary-dot lattice witness (<code>13GEMSDOE</code>) block nonempty 37,654-dot candidates. A sparse-only or matched-budget comparison is not a waiver.</li>
<li>If the protocol is legitimately resolved in a later session, validate the exact file automatically: single-band float32, matching CRS, dimensions and transform, finite in-range values inside bounds, and the required outside-bounds encoding.</li>
<li>The <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">official instructions</a> say null or NaN outside study-area bounds. Local gates instead verify finite zeros outside the sample's finite footprint to address the reported range error. These are not proven equivalent, and a local PASS is not a portal receipt.</li>
<li>Only after every gate and the separate selector approve: use that new file's own name and note (each at most 140 characters), verify the weekly limit and mandatory AI-use narrative disclosure (<a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Official Rules §3.2</a>) on the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">official submission page</a>, and record any organizer receipt against the exact file SHA-256. This session selected and spent no slot.</li></ol></section>
<section><h2>Official research &amp; evidence</h2><p><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Task, metric and format</a> · <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Official rules</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution">Reference solution</a> · <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a> · <a href="https://www.usgs.gov/3d-elevation-program">USGS 3DEP</a> · <a href="https://gdr.openei.org/submissions/1391">GDR INGENIOUS (CC BY 4.0)</a> · <a href="https://epsg.io/32611">EPSG:32611</a>.</p>
<p>Public source documentation is not proof of data coverage, provenance, predictive value, or access to authenticated competition files. <a href="downloads/review_d30d387c_run_card.json">Session d30d387c run card</a> · <a href="downloads/session_b97812a3_run_card.json">b97812a3 run card</a> · <a href="downloads/review_14f85876_run_card.json">14f85876 run card</a> · <a href="SITE_REVIEW_20261026.html">Earlier detailed site forensic review</a>.</p></section>
<footer><small>Site comparison recorded 2026-10-26; dual-witness, 11-artifact delta, 12-repo multi-owner, 19-band input, and GitHub ref checks completed 2026-10-27 UTC. Ref checks are not a new site comparison. No candidate score or organizer receipt is invented.</small></footer>
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
