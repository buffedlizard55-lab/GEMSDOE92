#!/usr/bin/env python3
"""Render a pinned, read-only current-main review of the nine focus sites.

This page summarizes owner-maintained sources at the exact GitHub main refs
recorded in evidence/focus9_current_main_readback_20261030.json. It is not a
live leaderboard feed and does not audit the current remote TIFF bytes.
"""
from __future__ import annotations

from itertools import combinations
import html
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/focus9-review-20261030.html"
SITES = tuple(f"GEMSDOE{x}" for x in (24, 25, 27, 28, 30, 31, 32, 33, 36))


def _json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _validate_sources() -> tuple[dict, dict, dict, dict, dict, dict]:
    readback = _json("evidence/focus9_current_main_readback_20261030.json")
    freshness = _json("evidence/focus9_freshness_20261030.json")
    sources = _json("evidence/focus9_sources_20261028.json")
    pairwise = _json("docs/downloads/focus9_pairwise_recheck_14f85876.json")
    lineage = _json("docs/downloads/focus_9sites_audit_20261026.json")
    estimator = _json("docs/downloads/score_estimator_audit_14f85876.json")

    if readback.get("schema") != "gemsdoe92-focus9-current-main-readback-v1":
        raise ValueError("unsupported current-main readback schema")
    freshness_path = ROOT / readback["freshness_receipt"]["path"]
    inventory_path = ROOT / readback["historical_focus_inventory"]["path"]
    pairwise_path = ROOT / readback["historical_pairwise_receipt"]["path"]
    import hashlib
    if hashlib.sha256(freshness_path.read_bytes()).hexdigest() != readback["freshness_receipt"]["sha256"]:
        raise ValueError("current-main readback is bound to a different freshness receipt")
    if hashlib.sha256(inventory_path.read_bytes()).hexdigest() != readback["historical_focus_inventory"]["sha256"]:
        raise ValueError("current-main readback is bound to a different historical inventory")
    if hashlib.sha256(pairwise_path.read_bytes()).hexdigest() != readback["historical_pairwise_receipt"]["sha256"]:
        raise ValueError("current-main readback is bound to a different pairwise receipt")
    if pairwise.get("source_sha256") != readback["historical_focus_inventory"]["sha256"]:
        raise ValueError("pairwise receipt source does not match the pinned focus-site inventory")
    if (freshness.get("complete") is not True or freshness.get("changed_count") != len(SITES)
            or freshness.get("unknown_count") != 0
            or readback.get("freshness_receipt", {}).get("changed_count") != len(SITES)):
        raise ValueError("freshness receipt is incomplete or not nine-of-nine")
    if set(sources) != set(SITES) or set(pairwise.get("sites", [])) != set(SITES):
        raise ValueError("historical focus-nine inventory is incomplete")
    if {row.get("site") for row in readback.get("sites", [])} != set(SITES):
        raise ValueError("current-main readback is missing one or more focus sites")
    if len(readback.get("sites", [])) != len(SITES):
        raise ValueError("current-main readback contains duplicate site records")
    if len(pairwise.get("comparisons", [])) != 36 or pairwise.get("submission_eligible") is not False:
        raise ValueError("historical pairwise receipt is incomplete or not rejection-only")

    fresh_by_site = {row["site"]: row for row in freshness["sites"]}
    readback_by_site = {row["site"]: row for row in readback["sites"]}
    expected_pairs = {frozenset(pair) for pair in combinations(SITES, 2)}
    seen: set[frozenset[str]] = set()
    maxima = {site: (0.0, None) for site in SITES}
    for row in pairwise["comparisons"]:
        a, b = row.get("site_a"), row.get("site_b")
        pair = frozenset((a, b))
        if pair not in expected_pairs or pair in seen:
            raise ValueError("invalid or duplicate historical pairwise comparison")
        seen.add(pair)
        ab = float(row["forward_3px_overlap_a_to_b"])
        ba = float(row["forward_3px_overlap_b_to_a"])
        if not (math.isfinite(ab) and math.isfinite(ba) and 0.0 <= ab <= 1.0 and 0.0 <= ba <= 1.0):
            raise ValueError("historical directional overlap is outside [0,1]")
        if row.get("duplicate_by_configured_threshold") is not True:
            raise ValueError("a historical focus-nine pair does not carry the configured duplicate stop")
        if ab > maxima[a][0]:
            maxima[a] = (ab, b)
        if ba > maxima[b][0]:
            maxima[b] = (ba, a)
    if seen != expected_pairs or not all(value[0] > 0.70 for value in maxima.values()):
        raise ValueError("historical pairwise rejection evidence is incomplete")

    for site in SITES:
        current = readback_by_site[site]
        observed = fresh_by_site[site]
        if (current.get("observed_main_commit") != observed.get("observed_main_commit")
                or observed.get("status") != "changed"
                or not re.fullmatch(r"[0-9a-f]{40}", current.get("observed_main_commit", ""))):
            raise ValueError(f"{site} readback commit does not match the freshness receipt")
        if len(current.get("readme_sha256", "")) != 64 or not current.get("owner_summary_excerpt"):
            raise ValueError(f"{site} readback is missing a pinned README hash or status summary")
        for page in current.get("summary_pages", []):
            if (not re.fullmatch(r"[0-9a-f]{64}", page.get("sha256", ""))
                    or page.get("path", "").startswith("/")
                    or ".." in Path(page.get("path", "")).parts
                    or current["observed_main_commit"] not in page.get("url", "")):
                raise ValueError(f"{site} linked summary page is not pinned safely")
        source = sources[site]
        claim = float(source["claim"])
        if not (math.isfinite(claim) and 0.0 <= claim <= 1.0):
            raise ValueError(f"{site} historical score claim is invalid")
        if (not re.fullmatch(r"[0-9a-f]{40}", source.get("commit", ""))
                or source.get("repo") != site
                or source.get("blob_match") is not True
                or source.get("raw_url") != (
                    f"https://github.com/buffedlizard55-lab/{site}/raw/{source['commit']}/{source['path']}")):
            raise ValueError(f"{site} historical source pin is not internally consistent")
    if lineage.get("schema") != "gemsdoe92-focus-9sites-audit.v1":
        raise ValueError("historical B2 lineage receipt schema mismatch")
    if estimator.get("valid_leaderboard_prediction") is not False:
        raise ValueError("exploratory claim model is unexpectedly marked as a valid leaderboard predictor")
    return readback, freshness, sources, pairwise, lineage, estimator


def _a(url: str, label: str, *, cls: str = "") -> str:
    klass = f' class="{html.escape(cls, quote=True)}"' if cls else ""
    return f'<a{klass} href="{html.escape(url, quote=True)}">{label}</a>'


def render() -> str:
    readback, freshness, sources, pairwise, lineage, estimator = _validate_sources()
    readback_by_site = {row["site"]: row for row in readback["sites"]}
    maxima = {site: (0.0, "") for site in SITES}
    for row in pairwise["comparisons"]:
        a, b = row["site_a"], row["site_b"]
        ab = float(row["forward_3px_overlap_a_to_b"])
        ba = float(row["forward_3px_overlap_b_to_a"])
        if ab > maxima[a][0]:
            maxima[a] = (ab, b)
        if ba > maxima[b][0]:
            maxima[b] = (ba, a)

    current_rows = []
    for site in SITES:
        record = readback_by_site[site]
        commit = record["observed_main_commit"]
        linked = " · ".join(
            _a(page["url"], html.escape(Path(page["path"]).name))
            for page in record["summary_pages"]
        )
        current_rows.append(
            f'<tr><th scope="row">{html.escape(site)}</th>'
            f'<td><code>{commit}</code><br>{_a(record["main_commit_url"], "observed main commit")}</td>'
            f'<td>{html.escape(record["owner_summary_excerpt"])}</td>'
            f'<td>{_a(record["readme_url"], "README")}{"<br>" + linked if linked else ""}</td></tr>'
        )

    historical_rows = []
    for site in SITES:
        source = sources[site]
        name = Path(source["path"]).name
        claim = float(source["claim"])
        overlap, peer = maxima[site]
        historical_rows.append(
            f'<tr><th scope="row">{html.escape(site)}</th>'
            f'<td><a href="{html.escape(source["raw_url"], quote=True)}" target="_blank" rel="noopener">'
            f'Open pinned historical file for research/audit</a><br><code>{html.escape(name)}</code></td>'
            f'<td><strong>{claim:.4f}</strong><br><small>USER-/OWNER-REPORTED; no organizer receipt</small></td>'
            f'<td><strong>{overlap:.2%}</strong><br><small>vs {html.escape(peer or "unknown")}; directional 3-px share</small></td>'
            f'<td><strong>NOT ESTIMABLE</strong><br>DO NOT SUBMIT</td></tr>'
        )

    g27 = readback_by_site["GEMSDOE27"]["summary_pages"]
    g30 = readback_by_site["GEMSDOE30"]["summary_pages"]
    g27_verification = next(x["url"] for x in g27 if "43_session20_verification" in x["path"])
    g30_snapshot = next(x["url"] for x in g30 if "leaderboard-snapshot" in x["path"])
    source_receipt = readback["freshness_receipt"]
    reviewed = html.escape(readback["reviewed_utc"])
    source_class = html.escape(readback["score_provenance_note"])
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Focus-9 current-main review — 30 Oct 2026</title>
<style>
:root{{color-scheme:light;--ink:#18212e;--muted:#52606d;--line:#d7dee7;--red:#a61b1b;--redbg:#fff3f1;--blue:#174ea6;--paper:#fff;--bg:#f3f6fa;--amber:#774900;--amberbg:#fff8e8}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.56 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
main{{max-width:1240px;margin:auto;padding:24px}}h1{{font-size:clamp(1.8rem,4vw,2.7rem);line-height:1.12;margin:.5rem 0 1rem}}h2{{font-size:1.5rem;margin-top:0}}h3{{margin:1rem 0 .4rem}}p{{margin:.65rem 0}}section{{background:var(--paper);padding:22px;margin:18px 0;border:1px solid var(--line);border-radius:12px;box-shadow:0 2px 8px #1723330a}}
.stop{{border:3px solid var(--red);background:var(--redbg)}}.caution{{border-left:5px solid #be7d00;background:var(--amberbg);padding:12px 15px;border-radius:8px}}.small,small{{font-size:.88rem;color:var(--muted)}}a{{color:var(--blue);overflow-wrap:anywhere}}code{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.91em;overflow-wrap:anywhere}}nav{{margin-bottom:14px}}nav a{{margin-right:12px}}table{{border-collapse:collapse;width:100%;font-size:.92rem}}th,td{{border-bottom:1px solid var(--line);padding:10px;vertical-align:top;text-align:left}}th{{background:#edf2f8}}.scroll{{overflow-x:auto}}.pill{{display:inline-block;background:#7f1d1d;color:white;font-weight:800;padding:4px 10px;border-radius:999px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(225px,1fr));gap:12px}}.tile{{padding:14px;background:#f7f9fc;border:1px solid var(--line);border-radius:9px}}.tile strong{{display:block;font-size:1.1rem}}ul,ol{{padding-left:1.35rem}}.footer{{color:var(--muted);font-size:.85rem}}
@media(max-width:720px){{main{{padding:14px}}section{{padding:16px}}table{{min-width:760px}}}}
</style></head><body><main>
<nav>{_a("index.html", "Current GEMSDOE92 site status")} · {_a("nine-sites.html", "GEMSDOE92 review")} · {_a("HYPOTHESES_FOCUS9_20261030.md", "Ranked geological hypotheses")}</nav>
<p class="small">Pinned current-main readback · reviewed {reviewed} · {len(SITES)}/9 observed main refs changed since the historical pin</p>
<h1>Focus-9: current owner-source review</h1>
<section class="stop" aria-label="Submission decision">
<p><span class="pill">DO NOT SUBMIT — NO FILE CLEARED</span></p>
<h2>Download for competition use: none. Submit: none.</h2>
<p><strong>No new GeoTIFF, geological experiment, holdout, or score estimate was produced in this review.</strong> Historical pinned rasters below are linked only for provenance and research inspection. The current GEMSDOE92 site's declared primary is Riesz-LBM2 (see the current-site banner), and it remains a research-only negative artifact; the dated DEXP-Kostrov page is not the current primary.</p>
<div class="grid"><div class="tile"><strong>{freshness['changed_count']}/9</strong><span>main refs changed — ref freshness only</span></div><div class="tile"><strong>36/36</strong><span>historical focus-nine pairs cross the configured duplicate threshold</span></div><div class="tile"><strong>0</strong><span>slots selected or used by this review</span></div><div class="tile"><strong>NOT ESTIMABLE</strong><span>new-file public score</span></div></div>
<p class="caution">A local format/range PASS is not uniqueness clearance, a holdout promotion, portal acceptance, or a score. The current-main readback did not fetch current TIFF bytes or organizer submission receipts. No failed uniqueness gate was relaxed.</p>
</section>
<section><h2>What the nine current main pages say</h2>
<p>Each row is a curator summary of the pinned owner-maintained README/summary documents at the exact observed commit, not an independent experiment or organizer record. The links open the exact commit and linked files. A changed Git ref does not mean the TIFF, score claim, or competition status was revalidated.</p>
<div class="scroll"><table><thead><tr><th>Site</th><th>Observed current main</th><th>Owner-maintained status / evidence readback</th><th>Pinned source pages</th></tr></thead><tbody>{''.join(current_rows)}</tbody></table></div>
<p class="small">Source freshness receipt: <a href="../{html.escape(source_receipt['path'])}">{html.escape(source_receipt['path'])}</a> · observed {html.escape(source_receipt['observed_utc'])}. It checks GitHub commit identities only.</p>
</section>
<section><h2>Historical reported peaks — reference files only</h2>
<p>These are the highest historical values in the pinned nine-site inventory. All score entries are owner/user claims, not organizer-confirmed results. Max overlap is directional: the fraction of that row's historical dots within 3 pixels of any peer's dots in the historical nine-file set. The table is not a current-TIFF scan or full-registry clearance.</p>
<div class="scroll"><table><thead><tr><th>Site</th><th>Historical file link</th><th>Reported value</th><th>Max peer overlap</th><th>New-file estimate / submit</th></tr></thead><tbody>{''.join(historical_rows)}</tbody></table></div>
<p>Links are optional research/audit downloads from pinned owner GitHub commits. They are not recommendations to submit or resubmit. The archived 36-pair receipt is <a href="downloads/focus9_pairwise_recheck_14f85876.json">focus9_pairwise_recheck_14f85876.json</a>; the historical inventory hash is <code>{html.escape(readback['historical_focus_inventory']['sha256'])}</code>.</p>
</section>
<section class="stop"><h2>GEMSDOE32's 0.2778 — what the evidence supports</h2>
<p><strong>Evidence class: OWNER-REPORTED / UNVERIFIED, not ORGANIZER-CONFIRMED.</strong> It is the largest of these nine historical claims. No submission-page receipt ties the B2 TIFF bytes to 0.2778, and no calibrated new-file estimate follows from it.</p>
<p><strong>Measured raster lineage:</strong> the pinned byte audits describe B2 (37,654 positive cells) as a deletion-only subset of the D2.8 44,090-dot family: 6,436 dots removed and none added; the removed cells are reported within 1–2 pixels of the public catalogue. A related 40,199-dot H27-4 step sits between D2.8 and B2 in the recorded family tree. This is a pixel-set relationship, not proof that the organizer scored those exact bytes or that pruning caused any score change.</p>
<p><strong>Plausible mechanism, not causal result:</strong> under the locally documented distance-weighted Tversky objective (<code>alpha=0.2</code> false-positive weight, <code>beta=0.8</code> false-negative weight, 300 m triangular kernel), removing dots near known catalogue faults could reduce false-positive penalty while retaining enough distance-kernel credit around hidden faults. It could also hurt if removed dots would have been near unseen faults. Hidden labels and a matched, density-controlled ablation tied to an organizer receipt are absent; proximity to mapped faults does not prove a prediction was false.</p>
<p><strong>Can a new method beat 0.2778?</strong> Possible in principle; no evidence-based probability or public-score estimate is defensible. The current readiness stops (unassigned method lane and literal registry overlap gate), missing organizer receipts, non-comparable holdout evaluators, and lack of a validated holdout-to-leaderboard mapping prevent a submit recommendation.</p>
<p class="small">Lineage and score-source receipts: <a href="downloads/focus_9sites_audit_20261026.json">historical byte audit</a> · <a href="../evidence/focus9_executive_audit_20261026.json">focus-nine executive audit</a> · <a href="{html.escape(g27_verification, quote=True)}">GEMSDOE27 current verification</a>.</p>
</section>
<section><h2>Leaderboard claims and score-estimation limits</h2>
<ul>
<li>The prompted <code>0.4413</code> and <code>0.3195</code> figures conflict. Owner-maintained current-main pages report a later public-board read with <code>0.4544</code> at rank 1; the 29-Oct snapshot reports <code>0.3195</code> at rank 47 and <code>0.3167</code> at rank 50, while a 30-Oct owner verification describes <code>0.3195</code> as rank 50. {_a(g30_snapshot, "29-Oct owner snapshot")} · {_a(g27_verification, "30-Oct owner verification")}.</li>
<li>This review did not fetch the DrivenData leaderboard or a submission receipt. The site-to-team mapping is not present in these records. Treat those leaderboard figures as owner-maintained reports, not our direct confirmation; none establishes that GEMSDOE32 or another site artifact was scored.</li>
<li>Internal <code>HOLDOUT-DTI</code> is a hidden-catalogue-segment diagnostic with its own evaluator, buffer, density, and held-out positives. It is not public leaderboard score and cannot be substituted for one. Site reports disagree across evaluators and some holdout inputs are owner-mirror copies of the public catalogue, undermining independence.</li>
<li>The exploratory 107-row score model trains on unverified owner claims; its recomputed row-LOO RMSE is {estimator['row_loo_rmse_recomputed']:.6f}, grouped holdout RMSE {estimator['leave_group_out_rmse']:.6f}, and it provides no calibrated individual prediction interval. It is explicitly not a valid leaderboard predictor. These errors are too large for ranking close candidate variants or promising an absolute score.</li>
<li>Local format evidence conflicts: the GEMSDOE28 summary says all nine historical files pass its local format/range checks, while the GEMSDOE30 review says B2's finite zeros outside its footprint fail that review's outside-footprint nodata check. Neither statement is an organizer acceptance record; do not resolve this by assuming a portal rule.</li>
</ul>
<p>Label every number by type: owner claim; measured pixel/raster fact; <code>HOLDOUT-DTI</code>; <code>PROJECTION</code>; or organizer-confirmed receipt. A projection is not a score.</p>
</section>
<section><h2>Ranked research leads — not candidates or slot recommendations</h2>
<p>The separate plan links each mechanism to a specific geological signal, a non-fault mimic, the available-data gate, and an assigned whole-segment buffered holdout. These are qualitative research priorities only; no DTI gain or win probability is forecast.</p>
<ol>
<li><strong>InSAR fault-related deformation residuals:</strong> persistent linear LOS velocity/coherence discontinuities across mapped and blind range-front structures; mimic: atmospheric/orbital ramps, aquifer compaction, landslides, and mining. High external-data/processing cost; current data coverage and lane permission unverified.</li>
<li><strong>Multi-temporal thermal/vegetation anomalies:</strong> persistent line-shaped thermal or phenology contrasts tied to fluid pathways; mimic: lithology, soil moisture, irrigation, elevation/aspect, and land-cover boundaries. Medium-high processing cost; time series and coverage not checked.</li>
<li><strong>Observed groundwater-head phase/gradient discontinuities:</strong> wells across structural blocks showing a repeatable hydraulic barrier or conduit response; mimic: pumping, seasonal recharge, screened-depth differences, and basin-fill heterogeneity. Sparse-data and temporal confounding risks; source bytes/coverage unverified.</li>
<li><strong>Hydrochemical/isotope mixing fronts:</strong> independent multi-analyte source-tracer transitions consistent with deep-fluid mixing along concealed structures; mimic: evaporation, lithology/weathering, irrigation return, contamination, and aquifer-depth effects. High cost and potentially sparse assays; source tables not inspected.</li>
</ol>
<p>These ideas are not asserted to be globally novel. Thermal and groundwater concepts already appear in local historical research notes; the exact transforms remain unvalidated. See the <a href="HYPOTHESES_FOCUS9_20261030.md">full ranked hypothesis screen</a>.</p>
</section>
<section><h2>Next steps and remaining limitations</h2>
<ol>
<li>Obtain the exact authorized single-method lane paragraph; do not choose one by inference.</li>
<li>Do not run a new experiment, create/perturb a TIFF, or select a weekly slot while the universal literal-duplicate stop and no-lane blocker remain. Do not replace a failed uniqueness threshold with a narrower comparison after seeing results.</li>
<li>Resolve whether the pinned dense lattice belongs in the uniqueness registry through a prospective, authorized protocol change, not a threshold waiver. Current proof is rejection-only and does not establish global uniqueness.</li>
<li>Get organizer-confirmed training/holdout provenance and exact public/hidden score receipts through the authorized owner workflow; independently retrieve the public leaderboard when permitted and reconcile the Oct-29/Oct-30 snapshots.</li>
<li>After blockers are resolved: preregister one mechanism and its non-fault mimic; derive features from visible faults only; use whole-segment spatial folds with the required buffer, pixel-exact scoring mask, pooled metric and matched control; run per-feature leakage canaries; require a positive paired 95% CI, pre/post placement registry checks, and automated GeoTIFF format validation. A format PASS remains necessary but not sufficient.</li>
<li>Only then can a separate selector consider a weekly slot. A new organizer score requires an owner-controlled upload and archived receipt; this agent did not upload or spend a slot.</li>
</ol>
<p><strong>Three-pass review record:</strong> provenance/ref identity; adversarial evidence and method check; final download/submit and protocol-safety check. They were sequential passes by one agent, not independent reviewers. See <a href="../{html.escape(readback['freshness_receipt']['path'])}">freshness receipt</a> and <a href="../evidence/focus9_current_main_readback_20261030.json">hash-bound current-main readback manifest</a>.</p>
</section>
<p class="footer">Generated from pinned local receipts on {reviewed}. {source_class} No TIFF bytes, live organizer leaderboard, or submission portal were fetched for this current-main review. Page is a dated snapshot, not an auto-refreshing live feed.</p>
</main></body></html>
'''
    return page


def main() -> None:
    OUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
