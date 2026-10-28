#!/usr/bin/env python3
"""Render the GitHub Pages site (v3, 2026-10-28) from machine evidence only.

Inputs : PRIMARY_CARD (evidence/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json),
         evidence/gemsdoe92-lbmc1-35801dots-20261027-89a660f6_run_card.json,
         evidence/focus9_sources_20261028.json, evidence/focus9_uniqueness_20261028.json,
         evidence/fleet_8owners_20261028.json, evidence/lbm_v1_prospective_oot_20261028.json,
         evidence/riesz_locked_holdout.json, evidence/riesz_locked_lbm_v2.json,
         evidence/lbm_v1_model.json, evidence/claims_matched_20261028.json,
         evidence/holdout_validity_20261027.json.
Outputs: docs/index.html, docs/how-to-submit.html, docs/nine-sites.html, index.html,
         docs/downloads/current_submission.json, docs/downloads/readiness.json.
``render()`` returns {path: text}; ``main`` writes them. ``check_site.py`` re-renders
and fails closed if any published page or status JSON feed is stale.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DL = DOCS / "downloads"
EVID = ROOT / "evidence"
PRIMARY_CARD = EVID / "gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json"
PRIOR_LBMC1_CARD = EVID / "gemsdoe92-lbmc1-35801dots-20261027-89a660f6_run_card.json"

OFFICIAL = [
    ("DrivenData competition home & problem description (metric, GeoTIFF format)", "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"),
    ("DrivenData submission portal (login required)", "https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/"),
    ("DrivenData public leaderboard (manual review only; never scraped/mirrored)", "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"),
    ("DrivenData Terms of Use (prohibits automated leaderboard scraping)", "https://www.drivendata.org/termsofuse/"),
    ("Official DOE / NLR competition rules PDF (Sept 2026)", "https://docs.nlr.gov/docs/fy26osti/96647.pdf"),
    ("Official DrivenData reference solution (Prof. John Lipor U-Net MC-CV)", "https://github.com/drivendataorg/gems-prize-reference-solution"),
    ("Forum #11516: known USGS/INGENIOUS faults masked pixel-exactly when scoring", "https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4"),
    ("Forum #11550: leaderboard pools TPw/FPw/FNw across all public test pixels", "https://community.drivendata.org/t/leaderboard-aggregation-pooled-over-public-test-pixels-or-mean-of-per-chunk-scores/11550"),
    ("Forum #11536: 'new fault' = any real fault pixel absent from USGS/INGENIOUS", "https://community.drivendata.org/t/where-do-you-draw-the-line/11536"),
    ("Forum #11553: weekly submission limit shown on website prevails (3/week)", "https://community.drivendata.org/t/submission-amount-question/11553"),
    ("Forum #11556: Phase 2 expert labels can be added, removed, or revised", "https://community.drivendata.org/t/questions-about-the-final-round-rules/11556"),
    ("INGENIOUS Great Basin regional dataset (DOE GDR Submission #1391)", "https://gdr.openei.org/submissions/1391"),
    ("USGS GeoDAWN airborne magnetic & radiometric surveys (NW Great Basin)", "https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and"),
    ("USGS 3DEP 1 m LiDAR DEM collection (free public domain, Phase-2 opportunity)", "https://data.usgs.gov/datacatalog/data/USGS:77ae0551-c61e-4979-aedd-d797abdcde0e"),
    ("DrivenData Terms of Use (no automated leaderboard monitoring or mirroring)", "https://www.drivendata.org/termsofuse/"),
]

CSS = """body{font:15.5px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f7f9;color:#1f2933}
main{max-width:1080px;margin:0 auto;padding:1rem 1.2rem 3rem}h1{font-size:1.55rem;margin:.6rem 0}h2{margin-top:2rem;border-bottom:2px solid #e3e7ec;padding-bottom:.2rem}h3{margin-top:1.3rem}
.box{background:#fff;border-radius:12px;padding:1.1rem 1.3rem;box-shadow:0 1px 3px rgba(0,0,0,.08);margin:1rem 0}
.ok{border:3px solid #15803d}.no{border:3px solid #b91c1c}.badge{display:inline-block;padding:.22rem .65rem;border-radius:999px;font-weight:700;color:#fff;font-size:.85rem;white-space:nowrap}
.bok{background:#15803d}.bno{background:#b91c1c}.bwarn{background:#b45309}.bdl{background:#0369a1}
.btn{display:inline-block;background:#1d4ed8;color:#fff!important;padding:.72rem 1.05rem;border-radius:8px;font-weight:700;text-decoration:none;margin:.3rem .4rem .3rem 0}
.btn2{background:#334155}code,.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.88em;overflow-wrap:anywhere}
table{border-collapse:collapse;width:100%;font-size:.9rem}th,td{border-bottom:1px solid #e3e7ec;padding:.42rem .45rem;text-align:left;vertical-align:top}th{background:#eef2f7}
.copy{background:#0f172a;color:#e2e8f0;padding:.55rem .7rem;border-radius:6px;font-family:ui-monospace,Menlo,monospace;overflow-wrap:anywhere}
.small{font-size:.85rem;color:#52606d}.warn{background:#fff7ed;border-left:4px solid #f59e0b;padding:.6rem .8rem;border-radius:6px;margin:.6rem 0}
nav a{margin-right:1rem;font-weight:600}"""


def esc(s) -> str:
    return html.escape(str(s))


def load():
    card = json.loads(PRIMARY_CARD.read_text(encoding="utf-8"))
    prior = json.loads(PRIOR_LBMC1_CARD.read_text(encoding="utf-8"))
    f9 = json.loads((EVID / "focus9_sources_20261028.json").read_text(encoding="utf-8"))
    f9u = json.loads((EVID / "focus9_uniqueness_20261028.json").read_text(encoding="utf-8"))
    fleet = json.loads((EVID / "fleet_8owners_20261028.json").read_text(encoding="utf-8"))
    oot = json.loads((EVID / "lbm_v1_prospective_oot_20261028.json").read_text(encoding="utf-8"))
    hold = json.loads((EVID / "riesz_locked_holdout.json").read_text(encoding="utf-8"))
    lbm2 = json.loads((EVID / "riesz_locked_lbm_v2.json").read_text(encoding="utf-8"))
    model = json.loads((EVID / "lbm_v1_model.json").read_text(encoding="utf-8"))
    val = json.loads((EVID / "holdout_validity_20261027.json").read_text(encoding="utf-8"))
    return card, prior, f9, f9u, fleet, oot, hold, lbm2, model, val


def promotion_blockers(card: dict) -> list[str]:
    """Apply the user protocol literally; MODEL estimates cannot waive a failed gate."""
    blockers = []
    g = card.get("gates_passed", {})
    u = card.get("uniqueness", {})
    if not g.get("format"):
        blockers.append("submission-format validation failed")
    # Rule 1 requires the continuous surface check before placement and the final-dot check.
    # The pinned full-support registry witness has literal overlap 1.0 for this candidate.
    if u.get("literal_reading", {}).get("duplicate_under_literal") is True:
        blockers.append("registry stop: literal full-support witness overlap is 1.0 (> 0.70)")
    if float(u.get("surface_worst_overlap", 1.0)) > 0.70:
        blockers.append("pre-placement surface overlap exceeds 0.70")
    if float(u.get("surface_worst_abs_rho", 1.0)) > 0.90:
        blockers.append("pre-placement absolute rank correlation exceeds 0.90")
    # For final dots, use the protocol's literal witness result where present rather than
    # silently substituting the narrower operative sparse-dot interpretation.
    if u.get("literal_reading", {}).get("duplicate_under_literal") is True:
        blockers.append("final-dot registry stop: literal overlap is 1.0 (> 0.70)")
    elif float(u.get("final_worst_overlap", 1.0)) > 0.70:
        blockers.append("final-dot overlap exceeds 0.70")
    if float(u.get("final_worst_abs_rho", 1.0)) > 0.90:
        blockers.append("final-dot absolute rank correlation exceeds 0.90")
    if not g.get("no_leakage"):
        blockers.append("leakage canary failed")
    h = card.get("holdout_dti", {})
    candidate = h.get("exp1", {}).get("dti")
    control = h.get("r0_recipe_control", {}).get("dti")
    paired_ci = h.get("paired_delta_vs_r0_recipe", {}).get("ci95")
    if (not g.get("catalogue_holdout_beats_r0_recipe") or candidate is None or control is None
            or float(candidate) <= float(control) or not isinstance(paired_ci, list)
            or len(paired_ci) != 2 or float(paired_ci[0]) <= 0):
        blockers.append("HOLDOUT-DTI did not beat the R0 recipe control with paired 95% CI above zero")
    auc = card.get("leakage_canaries", {}).get("max_auc")
    if auc is None or float(auc) > 0.90:
        blockers.append("feature-alone leakage canary is missing or exceeds AUC 0.90")
    return blockers


def status_cards(card: dict) -> tuple[dict, dict]:
    blockers = promotion_blockers(card)
    ok = not blockers and card["verdict"] == "promote" and card["submission_eligible"] is True
    rel = card["raster"]["file"].removeprefix("docs/")
    pt = card["model_estimate"]["point"]
    current = dict(
        file=card["raster"]["file"],
        sha256=card["raster_sha256"],
        bytes=card["raster"]["bytes"],
        n_dots=card["raster"]["n_dots"],
        submission_name=card["submission_name"],
        note=card["note"],
        verdict=card["verdict"],
        ok_to_download=True,
        ok_to_submit=ok,
        run_card=f"downloads/{Path(PRIMARY_CARD).name}",
        model_estimate_point=pt["lbm_v1"],
        model_estimate_lbm_v2_riesz=pt.get("lbm_v2_riesz", pt["lbm_v1"]),
        model_estimate_interval90=[
            card["model_estimate"]["bootstrap"]["q05"],
            card["model_estimate"]["bootstrap"]["q95"],
        ],
        evidence_class_of_estimate="MODEL (not an organizer score)",
        blocking_reasons=blockers,
    )
    readiness = dict(
        file=rel,
        raster_sha256=card["raster_sha256"],
        submission_name=card["submission_name"],
        note=card["note"],
        verdict=card["verdict"],
        submission_eligible=ok,
        download_status="OK TO DOWNLOAD",
        submission_status=(
            "OK TO SUBMIT — separate slot selection is still required"
            if ok
            else "DO NOT SUBMIT — mandatory protocol gate(s) failed; research download only"
        ),
        blocking_reasons=blockers,
        gates=card["gates_passed"],
    )
    return current, readiness


def page(title: str, body: str) -> str:
    footer = (
        '<footer class="small" style="margin-top:2rem;border-top:1px solid #e3e7ec;padding-top:.8rem">'
        'The official DrivenData leaderboard is not mirrored or automatically monitored by this repository; see '
        '<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">competition page</a> and '
        '<a href="https://www.drivendata.org/termsofuse/">DrivenData Terms of Use</a>.'
        "</footer>"
    )
    return (
        f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{esc(title)}</title>\n'
        f"<style>{CSS}</style>\n</head>\n<body>\n<main>\n{body}\n{footer}\n</main>\n</body>\n</html>\n"
    )


def submission_box(card: dict, href_prefix: str = "") -> str:
    ok = card["verdict"] == "promote" and card["submission_eligible"] is True
    r = card["raster"]
    rel = r["file"].removeprefix("docs/")
    me = card["model_estimate"]
    b = me["bootstrap"]
    u = card["uniqueness"]
    dl_badge = '<span class="badge bdl">✅ OK TO DOWNLOAD FOR RESEARCH</span>'
    sub_badge = (
        '<span class="badge bok">✅ OK TO SUBMIT</span>'
        if ok
        else '<span class="badge bno">⛔ DO NOT SUBMIT</span>'
    )
    v2_pt = me["point"].get("lbm_v2_riesz", me["point"]["lbm_v1"])
    return f"""<section class="box {'ok' if ok else 'no'}" id="submit-now">
<h1>{dl_badge} {sub_badge} {esc(Path(rel).name)}</h1>
<p><a class="btn" data-primary="true" href="{href_prefix}{esc(rel)}" download>⬇ Download Format-Validated Research GeoTIFF ({r['bytes']:,} bytes)</a>
<a class="btn btn2" href="{href_prefix}{esc(rel.replace('-zeros.tif', '-zeros.zip'))}" download>⬇ One-TIFF ZIP</a>
<a class="btn btn2" href="{href_prefix}how-to-submit.html">How to submit (3 steps)</a></p>
<table>
<tr><th>Automated clearance</th><td><strong>Research download:</strong> Format-valid under the local validator; this does not establish leaderboard value or organizer acceptance.<br><strong>Portal upload:</strong> {'OK TO SUBMIT only after separate slot selection.' if ok else 'DO NOT SUBMIT — protocol stop(s) failed; this file is research-only.'}</td></tr>
<tr><th>Portal “Submission name”</th><td><div class="copy">{esc(card['submission_name'])}</div></td></tr>
<tr><th>Portal “Note” ({card['note_chars']} ≤ 140 chars)</th><td><div class="copy">{esc(card['note'])}</div></td></tr>
<tr><th>SHA-256</th><td class="mono">{esc(card['raster_sha256'])}</td></tr>
<tr><th>Local format validation (not organizer acceptance)</th><td>{r['n_dots']:,} binary dots (<code>1.0</code>); exact <code>0.0</code> elsewhere including all 7,108,787 exterior cells and mapped catalogue cells. Single-band <code>float32</code>, <code>EPSG:32611</code>, <code>3292×3730</code>, exact sample geotransform, <code>nodata=None</code>, no NaN/Inf; passes the local <code>[0,1]</code> range test. The portal remains authoritative and could apply additional checks.</td></tr>
<tr><th>Score evidence (no projection presented as a score)</th><td><strong>{v2_pt:.4f}</strong> <code>MODEL projection</code> (<code>LBM-v2</code>; not a measured competition score). The user-provided <code>GEMSDOE32 0.2778</code> is a <code>CLAIM</code>; no organizer receipt is present.<br>
<code>HOLDOUT-DTI</code> (<code>gems57-pooled-hide-v2</code>, 22,663 withheld positive pixels): <strong>{card['holdout_dti']['exp1']['dti']:.5f}</strong> [{card['holdout_dti']['exp1']['ci95'][0]:.5f}, {card['holdout_dti']['exp1']['ci95'][1]:.5f}]. The R0 recipe control was <strong>{card['holdout_dti']['r0_recipe_control']['dti']:.5f}</strong> [{card['holdout_dti']['r0_recipe_control']['ci95'][0]:.5f}, {card['holdout_dti']['r0_recipe_control']['ci95'][1]:.5f}]; paired difference was negative with 95% CI [{card['holdout_dti']['paired_delta_vs_r0_recipe']['ci95'][0]:.5f}, {card['holdout_dti']['paired_delta_vs_r0_recipe']['ci95'][1]:.5f}].<br>
<span class="small">The HOLDOUT-DTI artifact is historical and was not independently rerun in this review; neither this nor the MODEL projection is an organizer-confirmed score.</span></td></tr>
<tr><th>Uniqueness under the required stop rule</th><td><strong>NO — DO NOT SUBMIT.</strong> The recorded pre-placement surface overlap is <strong>{u['surface_worst_overlap']:.3f}</strong> and the final literal overlap against the full-support registry witness is <strong>{u['literal_reading']['worst']:.3f}</strong> (both exceed the 0.70 cap). Narrower sparse dot-field interpretation: {u['final_worst_overlap']:.2%} maximum among {u['registry_rasters']:,} indexed rasters; that alternate reading cannot waive the literal lane stop. Surface |ρ| = {u['surface_worst_abs_rho']:.3f} and final |ρ| = {u['final_worst_abs_rho']:.3f}.</td></tr>
</table>
<p class="small">Run card: <a href="{href_prefix}downloads/{esc(Path(PRIMARY_CARD).name)}">JSON</a> · Machine status: <a href="{href_prefix}downloads/current_submission.json">current_submission.json</a> · <a href="{href_prefix}downloads/readiness.json">readiness.json</a>. Weekly limit: 3 submissions per week (DrivenData portal prevails).</p>
</section>"""


def exec_summary_table(card: dict, prior: dict, f9: dict, f9u: dict, model: dict) -> str:
    fitted = {(r["site"], r["name"]): r for r in model["rows"]}
    r_cur = card["raster"]
    rel_cur = r_cur["file"].removeprefix("docs/")
    me_cur = card["model_estimate"]
    u_cur = card["uniqueness"]

    r_pri = prior["raster"]
    rel_pri = r_pri["file"].removeprefix("docs/")
    me_pri = prior["model_estimate"]
    u_pri = prior["uniqueness"]

    rows_html = [
        f"""<tr style="background:#fff7ed">
<td><strong>GEMSDOE92 (2026-10-28 RIESZ-LOCKED artifact; research-only)</strong></td>
<td><a href="{esc(rel_cur)}" download><code>{esc(Path(rel_cur).name)}</code></a><br><span class="small mono">sha256 {esc(card['raster_sha256'][:16])}… · {r_cur['n_dots']:,} dots</span></td>
<td><strong>{me_cur['point']['lbm_v2_riesz']:.4f}</strong> <code>MODEL projection</code> (not a score)<br><code>{card['holdout_dti']['exp1']['dti']:.5f}</code> <code>HOLDOUT-DTI</code> [95% CI: {card['holdout_dti']['exp1']['ci95'][0]:.5f}, {card['holdout_dti']['exp1']['ci95'][1]:.5f}]<br><small>R0: {card['holdout_dti']['r0_recipe_control']['dti']:.5f}; E3 is worse.</small></td>
<td><strong>NO — STOP RULE FAILED</strong><br>pre-placement surface overlap: <strong>{u_cur['surface_worst_overlap']:.1%}</strong><br>literal final overlap: <strong>{u_cur['literal_reading']['worst']:.1%}</strong><br>narrow sparse PI-1: {u_cur['final_worst_overlap']:.2%} (not clearance)</td>
<td><span class="badge bdl">✅ RESEARCH DOWNLOAD</span><br><span class="badge bno">⛔ DO NOT SUBMIT</span></td>
</tr>""",
        f"""<tr style="background:#fffbeb">
<td><strong>GEMSDOE92 (Prior 2026-10-27 Entry)</strong></td>
<td><a href="{esc(rel_pri)}" download><code>{esc(Path(rel_pri).name)}</code></a><br><span class="small mono">sha256 {esc(prior['raster_sha256'][:16])}… · {r_pri['n_dots']:,} dots</span></td>
<td><code>{me_pri['point']['lbm_v1']:.4f}</code> <code>MODEL</code> [90%: {me_pri['bootstrap']['q05']:.3f}–{me_pri['bootstrap']['q95']:.3f}]<br><code>{prior['holdout_dti']['exp1']['dti']:.4f}</code> <code>HOLDOUT-DTI</code><br><span class="small">Unscored in prompt ledger</span></td>
<td>Peer max 3px: <code>{u_pri['final_worst_overlap']:.2%}</code> (2,060-raster snapshot)<br><strong>100% self-match</strong> to 2026-10-27 entry</td>
<td><span class="badge bdl">✅ OK TO DOWNLOAD</span><br><span class="badge bwarn">⚠️ PRIOR ENTRY — DO NOT RE-UPLOAD</span></td>
</tr>""",
    ]

    for site in sorted(f9, key=lambda k: -f9[k]["claim"]):
        s = f9[site]
        fr = fitted.get((site, s["best"]), {})
        u = f9u.get(site, {})
        clones = ", ".join(x.split("/")[1] if "/" in x else x for x in (u.get("identical_bytes_elsewhere") or u.get("worst_overlap_in") or [])[:3])
        rows_html.append(
            f"""<tr>
<td><strong>{esc(site)}</strong> (Focus-9 best)</td>
<td><a href="{esc(s['raw_url'])}"><code>{esc(s['best'])}</code></a><br><span class="small mono">sha256 {esc(s['sha256'][:16])}…</span></td>
<td><strong>{s['claim']:.4f}</strong> <code>CLAIM</code><br><code>{fr.get('logo', float('nan')):.3f}</code> <code>MODEL</code> (LOGO)</td>
<td><strong>NO — DUPLICATE</strong><br>3px overlap <strong>{u.get('worst_overlap', 1.0):.1%}</strong>, |ρ|={abs(u.get('worst_rho', 1.0)):.2f}<br><span class="small">clones: {esc(clones)}</span></td>
<td><span class="badge bdl">✅ STUDY ONLY</span><br><span class="badge bno">⛔ DO NOT SUBMIT (CLONE)</span></td>
</tr>"""
        )

    return (
        "<table><tr><th>Site / Role</th><th>File to Download</th><th>Estimated / Reported Score (Rule-3 Label)</th>"
        "<th>Uniqueness Across 8-Owner Fleet (2,162 Rasters)</th><th>Automated Clearance</th></tr>"
        + "".join(rows_html)
        + "</table>"
    )


def gates_table(card: dict, val: dict) -> str:
    g = card["gates_passed"]
    h = card["holdout_dti"]
    c = card["leakage_canaries"]
    u = card["uniqueness"]
    me = card["model_estimate"]
    oot = me["prospective_oot_20261028"]
    row = lambda name, ok, detail: (
        f"<tr><td><strong>{esc(name)}</strong></td>"
        f"<td>{'✅ PASS' if ok else '⛔ FAIL'}</td><td>{detail}</td></tr>"
    )
    return (
        "<table><tr><th>Automated Gate</th><th>Status</th><th>Measured Receipt</th></tr>"
        + "".join(
            [
                row(
                    "1. GeoTIFF format & [0, 1] portal compliance",
                    g["format"],
                    "11/11 shared gates + gems57.validate PASS on re-read disk bytes: EPSG:32611, 3292×3730, exact transform, float32 single band, nodata=None, binary {0.0, 1.0}, 0 NaN/Inf, 0.0 outside footprint, 0 dots within 200 m of mapped faults.",
                ),
                row(
                    "2. Fleet uniqueness across all 8 GitHub owners (PI-1 & Rule 1)",
                    g["uniqueness_pi1"],
                    f"Final binary dots: worst 3-px overlap <strong>{u['final_worst_overlap']:.4f} ≤ 0.70</strong> and worst |ρ| = <strong>{u['final_worst_abs_rho']:.4f} ≤ 0.90</strong> across all {u['registry_rasters']:,} unique SHA-256 rasters. Overlap vs prior <code>GEMSDOE92 lbmc1</code> = <strong>{u['vs_prior_gemsdoe92_lbmc1_overlap']:.4f}</strong> (≤ 0.56 cap). Pre-placement surface: worst |ρ| = <strong>{u['surface_worst_abs_rho']:.4f} ≤ 0.90</strong> (PI-1b; literal dense-witness caveat {u['literal_reading']['worst']:.3f} also disclosed).",
                ),
                row(
                    "3. Required pre-placement and final registry-overlap stop (Rule 1)",
                    float(u.get("surface_worst_overlap", 1.0)) <= 0.70
                    and float(u.get("literal_reading", {}).get("worst", 1.0)) <= 0.70,
                    f"Recorded pre-placement surface overlap = <strong>{u.get('surface_worst_overlap', 1.0):.3f}</strong>; full-support witness overlap on final dots = <strong>{u.get('literal_reading', {}).get('worst', 1.0):.3f}</strong>. Both must be ≤ 0.70. The narrow sparse-raster PI-1 value does not override this stop.",
                ),
                row(
                    "4. Leaderboard-aligned validation & prospective OOT (MODEL projection only)",

                    g["model_beats_0_2778_at_q05"] and g["model_robust_all_specs_ge_R0"],
                    f"Fitted to 128 matched CLAIMs across 85 groups: <code>LBM-v2</code> LOGO RMSE = <strong>{me['lbm_v2_validation']['logo_rmse_128']:.5f}</strong> (Spearman <strong>{me['lbm_v2_validation']['logo_spearman_128']:.4f}</strong>); true prospective out-of-time RMSE on {oot['n_unseen_claims']} unseen 2026-10-28 CLAIMs = <strong>{oot['rmse']:.5f}</strong>. Candidate 5% bootstrap bound <strong>{me['bootstrap']['q05']:.4f} &gt; 0.2778</strong>; beats R0 across all 5 model specs (P(Δ&gt;0) = {me['bootstrap']['delta_vs_R0']['p_gt0']:.2f}).",
                ),
                row(
                    "5. Single-feature leakage canaries (Rule 4, 20 features)",
                    g["no_leakage"],
                    f"All 16 zero-catalogue RIESZ-LOCKED physical features max symmetric AUC = <strong>{c['riesz_locked_16_max_sym_auc']:.4f} ≤ 0.90</strong>; overall 20-feature max AUC = <strong>{c['max_auc']:.4f} ≤ 0.90</strong> (<code>leakage_flag = False</code>).",
                ),
                row(
                    "6. Spatial hide-and-recover candidate vs prior lbmc1 (HOLDOUT-DTI)",
                    g["catalogue_holdout_beats_lbmc1"],
                    f"<code>gems57-pooled-hide-v2</code> ({h['withheld_positive_pixels']:,} withheld positives, 8 spatial folds): E3 hybrid = <strong>{h['exp1']['dti']:.5f}</strong> [{h['exp1']['ci95'][0]:.5f}, {h['exp1']['ci95'][1]:.5f}] vs lbmc1 <strong>{h['prior_lbmc1_v1_control']['dti']:.5f}</strong> [{h['prior_lbmc1_v1_control']['ci95'][0]:.5f}, {h['prior_lbmc1_v1_control']['ci95'][1]:.5f}]. This comparison alone is insufficient for promotion.",
                ),
                row(
                    "7. Required holdout improvement vs R0 recipe (HOLDOUT-DTI)",
                    g["catalogue_holdout_beats_r0_recipe"],
                    f"E3 hybrid = <strong>{h['exp1']['dti']:.5f}</strong>; R0 = <strong>{h['r0_recipe_control']['dti']:.5f}</strong>; paired difference = <strong>{h['paired_delta_vs_r0_recipe']['delta']:+.5f}</strong>, 95% CI [{h['paired_delta_vs_r0_recipe']['ci95'][0]:+.5f}, {h['paired_delta_vs_r0_recipe']['ci95'][1]:+.5f}]. This gate fails; interval is below zero. Holdout/CLAIM Spearman = {val['spearman_holdout_vs_claim']:.2f} is a separate transfer limitation.",
                ),
            ]
        )
        + "</table>"
    )


def fleet_section(fleet: dict, oot: dict, claims_doc: dict) -> str:
    owner_rows = "".join(
        f"<tr><td><code>{esc(o['owner'])}</code></td><td>{o['total_gemsdoe_repos']}</td><td>{o['repos_with_grid_tifs']}</td>"
        f"<td>{o['grid_tif_files']:,}</td><td>{o['unique_sha256']:,}</td>"
        f"<td class=\"small\">{esc(', '.join(o['empty_repos']) or 'none')}</td></tr>"
        for o in fleet["owners"]
    )
    oot_rows = "".join(
        f"<tr><td><strong>{esc(r['prompt_site'])}</strong></td><td><code>{esc(r['name'])}</code></td>"
        f"<td>{r['n_fp_pos']:,}</td><td><strong>{r['claim']:.4f}</strong></td>"
        f"<td><code>{r['lbm_v1_prospective_oot']:.4f}</code></td><td><code>{r['error']:+.4f}</code></td></tr>"
        for r in oot["rows"]
    )
    unscored_rows = "".join(
        f"<tr><td><strong>{esc(u['prompt_site'])}</strong></td><td><code>{esc(u['name'])}</code></td>"
        f"<td class=\"mono small\">{esc(u['sha256'][:16])}…</td><td>{u['n_fp_pos']:,}</td>"
        f"<td class=\"mono small\">{esc(u['matched_path'])}</td></tr>"
        for u in fleet["unscored_prompt_entries"]
    )
    n_matched = sum("match" in r for r in claims_doc["rows"])
    n_total = len(claims_doc["rows"])
    return f"""<section class="box"><h2 id="fleet-8owners">8-Owner Fleet Audit &amp; 2026-10-28 Prospective OOT Verification</h2>
<p class="small">Complete inventory across all 8 GitHub owners (<code>evidence/fleet_8owners_20261028.json</code>): <strong>{fleet['total_gemsdoe_repos']}</strong> GEMSDOE repositories, <strong>{fleet['total_grid_raster_files']:,}</strong> competition-grid GeoTIFFs, <strong>{fleet['unique_sha256']:,}</strong> unique SHA-256 digests, and <strong>{n_matched}/{n_total}</strong> matched <code>CLAIM</code> rows.</p>
<table><tr><th>GitHub Owner</th><th>Repos</th><th>With Rasters</th><th>Grid GeoTIFFs</th><th>Unique SHA-256</th><th>Empty (0-KB) Repos Flagged</th></tr>{owner_rows}</table>
<h3>True Prospective Out-of-Time Test on the 5 New 2026-10-28 Scored CLAIMs</h3>
<p class="small"><code>LBM-v1</code> fitted strictly to the 123 historical 2026-10-27 claims predicted all 5 newly reported 2026-10-28 scores across 4 owners with zero refitting at <strong>prospective OOT RMSE = {oot['prospective_rmse']:.5f}</strong> (MAE = {oot['prospective_mae']:.5f}; <code>evidence/lbm_v1_prospective_oot_20261028.json</code>):</p>
<table><tr><th>Site</th><th>Submission</th><th>Dots</th><th>New CLAIM</th><th>Prospective MODEL</th><th>Residual (CLAIM − MODEL)</th></tr>{oot_rows}</table>
<h3>7 Unscored Fleet Entries Audited &amp; Enforced in the 2,162-Raster Uniqueness Pool</h3>
<table><tr><th>Site</th><th>Unscored Entry</th><th>SHA-256</th><th>Positive Pixels</th><th>Matched Repository Path</th></tr>{unscored_rows}</table>
</section>"""


def hypotheses_section(hold: dict, lbm2: dict) -> str:
    s = hold["summary_e2_candidate"]["scores"]
    m2 = lbm2["models"]["lbm_v2_h92_q85_128"]
    m1 = lbm2["models"]["lbm_v1_128"]
    return f"""<section class="box"><h2 id="hypotheses">Earlier H-92 Hypothesis Ranking &amp; 3-Experiment Results (not a new experiment proposal)</h2>
<p class="small">Full mathematical specification, layer/band pins, non-fault mimics, and novelty audit across all 59 prior <code>gems/*.py</code> modules: <a href="HYPOTHESES_20261028_RIESZ_LOCKED.md">HYPOTHESES_20261028_RIESZ_LOCKED.md</a>.</p>
<table>
<tr><th>Rank &amp; ID</th><th>Physical Hypothesis &amp; Specific Layers</th><th>Why It Catches Off-Catalogue Faults</th><th>Named Non-Fault Mimic</th><th>Single-Feature Canary AUC</th></tr>
<tr><td><strong>#1 H-92A</strong><br><code>RIESZ-PIEDMONT</code></td><td>Multi-scale 2D Riesz monogenic phase congruency (<code>B13</code> CBA, <code>B02</code> RTP, <code>B16</code> basement) + slope-deconfounded 10 m DEM piedmont scarp &amp; break-in-slope (<code>dem10_100m_7band.tif</code>)</td><td>Amplitude-invariant step detection resolves low-relief range-front &amp; intrabasin alluvial scarps missed by range-core U-Nets</td><td>Lake Lahontan/Bonneville paleoshorelines &amp; incised fan-head gullies</td><td><code>0.6096</code> (PASS ≤ 0.90)</td></tr>
<tr><td><strong>#2 H-92C</strong><br><code>LOCKED-DEFICIT</code></td><td>Interseismic GPS strain-rate vs cumulative slip-proxy deficit (<code>B19</code>, <code>B12</code>, <code>B14</code>) × 10 m fluvial <code>χ</code>/<code>ksn</code> knickzones (<code>dem10_chi_100m_i16.tif</code>)</td><td>Locked blind/incipient normal faults have high regional strain + steep transient footwall channels before surface trace mapping</td><td>Lithologic gorge knickpoints across resistant welded tuffs</td><td><code>0.5721</code> &gt; marginals (PASS)</td></tr>
<tr><td><strong>#3 H-92B</strong><br><code>WIJNS-BIHARMONIC</code></td><td>FFT harmonic Wijns 3D tilt-angle <code>cos(θ)</code> (<code>B13</code>, <code>B02</code> in matched units) × broken-plate biharmonic basement flexure <code>∇⁴B16</code></td><td>Depth-invariant contact normaliser paired with hanging-wall/footwall elastic flexural couple separates faulted steps from plutons</td><td>Undeformed Mesozoic granitoid stocks &amp; caldera ring margins</td><td><code>0.5589</code> &gt; marginals (PASS)</td></tr>
<tr><td><strong>#4 H-92D</strong><br><code>PECLETVENT</code></td><td>Fournier quartz/chalcedony/Na-K-Ca enthalpy disequilibrium <code>ΔT = T_geotherm − T_measured</code> (1,230 GDR wells + 2 m probes) × MT clay-cap (<code>B17</code>) &amp; Grauch magnetic destruction</td><td>Rapid fault-upflow cooling traps high deep silica enthalpy in warm/blind outflow wells lacking boiling hot-spring mounds</td><td>Stratiform permeable ash-flow tuff lateral outflow plumes</td><td><code>0.5355</code> &gt; marginals (PASS)</td></tr>
<tr><td><strong>#5 H-92E</strong><br>(Deferred)</td><td>Azimuthal Curie-point radial spectral depth gradient on GeoDAWN RTP (<code>B02</code>)</td><td>Upwarped Curie isotherm beneath extensional hydrothermal zones</td><td>Silicic volcanic centers; 32 km window too coarse for 300 m DTI</td><td>Deferred (4/5 implemented)</td></tr>
</table>
<p class="small"><strong>Three-experiment budget: USED (3/3); no more experiment or slot is authorized in this review.</strong> E1 and E2's recorded HOLDOUT-DTI values are diagnostics, not evidence of success against the required R0 control. E3's 128-claim <code>MODEL</code> fit is a projection, not a leaderboard score, and its candidate HOLDOUT-DTI (<code>{s['e3_physlbm_unique']['dti']:.5f}</code> [{s['e3_physlbm_unique']['ci95'][0]:.5f}, {s['e3_physlbm_unique']['ci95'][1]:.5f}]) is below R0 (<code>{s['r0_recipe']['dti']:.5f}</code> [{s['r0_recipe']['ci95'][0]:.5f}, {s['r0_recipe']['ci95'][1]:.5f}]). The hybrid candidate therefore fails the required validation gate and is research-only.</p>
</section>"""


def focus9_rows(f9: dict, f9u: dict, model: dict) -> str:
    fitted = {(r["site"], r["name"]): r for r in model["rows"]}
    out = []
    for site, s in f9.items():
        fr = fitted.get((site, s["best"]), {})
        u = f9u.get(site, {})
        dup_where = ", ".join(x.split("/")[-1] for x in (u.get("identical_bytes_elsewhere") or u.get("worst_overlap_in") or []))[:120]
        out.append(
            f'<tr><td><strong>{esc(site)}</strong></td><td><a href="{esc(s["raw_url"])}">{esc(s["best"])}</a>'
            f'<br><span class="small mono">sha256 {esc(s["sha256"][:16])}…</span></td>'
            f'<td>{s["claim"]:.4f}</td><td>{fr.get("logo", float("nan")):.3f}</td>'
            f"<td>{'Yes' if u.get('unique_pi1') else 'No'}: "
            f"{('overlap ' + format(u.get('worst_overlap', 0), '.2f') + ', ρ ' + format(u.get('worst_rho', 0), '.2f') + ' vs ' + esc(dup_where)) if u else ''}</td></tr>"
        )
    return "".join(out)


def official_sources_table() -> str:
    rows = "".join(
        f'<tr><td>{i+1}</td><td>{esc(title)}</td><td><a href="{esc(url)}">{esc(url)}</a></td></tr>'
        for i, (title, url) in enumerate(OFFICIAL)
    )
    return f"<p class=\"warn\"><strong>Source limitation:</strong> these are official-domain reference links from the repository; they were not fetched or authenticated live in this review. The displayed historical claims should be checked against the linked source before relying on them.</p><table><tr><th>#</th><th>Official Reference (live-check status disclosed)</th><th>URL (for review)</th></tr>{rows}</table>"


def _historical_unsafe_render() -> dict[Path, str]:
    card, prior, f9, f9u, fleet, oot, hold, lbm2, model, val = load()
    blockers = promotion_blockers(card)
    if card.get("verdict") == "promote" and blockers:
        raise ValueError("promotion blocked by mandatory protocol gates: " + "; ".join(blockers))
    if card.get("submission_eligible") is True and blockers:
        raise ValueError("submission eligibility blocked by mandatory protocol gates: " + "; ".join(blockers))
    claims_doc = json.loads((EVID / "claims_matched_20261028.json").read_text(encoding="utf-8"))
    current, readiness = status_cards(card)
    idx = f"""<nav class="small"><a href="how-to-submit.html">How to submit</a><a href="nine-sites.html">Nine-site analysis</a><a href="#fleet-8owners">8-owner fleet</a><a href="#why">Why 0.2778</a><a href="#hypotheses">Hypotheses H-92A..E</a><a href="WHY_0_2778.md">Full math note</a><a href="HYPOTHESES_20261028_RIESZ_LOCKED.md">Pre-registration</a><a href="archive.html">Archive</a></nav>
{submission_box(card)}
<section class="box"><h2 id="summary">Executive Summary: Download, Score Estimate, Uniqueness &amp; Clearance</h2>
<p class="small">Every score carries its Protocol Rule-3 honesty label: <code>CLAIM</code> = owner-reported leaderboard score (no organizer receipt in this repo), <code>MODEL</code> = metric-structured truth-density model fitted to 128 matched <code>CLAIM</code>s across all 8 GitHub owners (prospective OOT RMSE = <code>0.00767</code>), and <code>HOLDOUT-DTI</code> = shared spatial hide-and-recover holdout (<code>gems57-pooled-hide-v2</code>, 22,663 withheld positives).</p>
{exec_summary_table(card, prior, f9, f9u, model)}
<h3>Automated Gate Receipts for Primary Candidate</h3>
{gates_table(card, val)}
</section>
<section class="box"><h2 id="nine-sites">Nine Focus Sites: Highest-Scoring &amp; Latest Submissions</h2>
<p class="small">Audited against the repository's pinned 2026-10-28 inventory of <strong>{fleet['unique_sha256']:,}</strong> unique SHA-256 rasters across 123 repos / 8 GitHub owners (<code>evidence/focus9_uniqueness_20261028.json</code>); this is a historical snapshot, not a live registry. No Focus-9 peak is cleared for re-submission. <a href="nine-sites.html">Complete per-site tables of the highest submissions, score claims, model projections and byte/overlap matches →</a></p>
<table><tr><th>Site</th><th>Best File (Commit-Pinned Link)</th><th>CLAIM</th><th>MODEL (LOGO)</th><th>Unique vs 8-Owner Fleet?</th></tr>{focus9_rows(f9, f9u, model)}</table>
</section>
{fleet_section(fleet, oot, claims_doc)}
<section class="box"><h2 id="why">PhD Analysis: Why GEMSDOE32 Scored 0.2778 (vs 0.3195 &amp; 0.4413) &amp; How to Score Higher Uniquely</h2>
<ul>
<li><strong>A plausible, not proven, explanation for GEMSDOE32's <code>0.2778</code> <code>CLAIM</code>:</strong> repository lineage records an R0-like sparse trace candidate followed by thinning and exclusions near mapped faults; the reported stepwise values are consistent with removing redundant false-positive mass under a distance-tolerant metric. The byte/lineage reconstruction and owner-reported values are not organizer receipts. They do <em>not</em> reveal hidden labels or prove that faults near mapped traces are absent, that the organizer applies any additional buffer, or that the listed changes caused the reported score increments. See <a href="WHY_0_2778.md">the evidence and assumption audit</a>.</li>
<li><strong>Why recent drops occurred across Focus-9 sites:</strong> continuous unthresholded probabilities (<code>GEMSDOE28</code> <code>0.0206</code>, <code>GEMSDOE36</code> <code>0.1647</code>) pay massive <code>0.2·FPw</code> background drag; pure topographic/tilt edge picks without canyon-rim deconfounding (<code>GEMSDOE24</code> <code>0.0859</code>, <code>GEMSDOE25</code> <code>0.0742</code>, <code>GEMSDOE33</code> <code>0.0963</code>, <code>GEMSDOE91</code> <code>0.0435</code>) hit volcanic mesa rims and fan gullies; uniform hex packing (<code>WBGGEMSDOE3</code> <code>0.0443</code>) ignores tectonic corridors.</li>
<li><strong>Do not interpret the model projection as a likely leaderboard score:</strong> the logged <code>0.3216</code> is a <code>MODEL</code> projection fit to owner-reported claims, not <code>HOLDOUT-DTI</code> or <code>ORGANIZER-CONFIRMED</code>. The tested RIESZ-LOCKED/LBM-v2 hybrid scored below the R0 recipe on the stored spatial holdout, and the registry checks hit a literal full-support witness stop. The prompt's <code>0.3195</code> and <code>0.4413</code> are user-supplied leaderboard values, not independently confirmed in this sandbox. New data such as USGS 3DEP LiDAR is a future research possibility, not a proven route to those scores. <a href="WHY_0_2778.md">Audit the historical 0.2778 reconstruction and its assumptions →</a></li>
</ul>
</section>
{hypotheses_section(hold, lbm2)}
<section class="box"><h2 id="limits">Limitations, Flagged Irregularities &amp; Next Session Plan</h2>
<ul>
<li><strong>Public-to-private &amp; Phase-2 generalisation:</strong> <code>MODEL</code> estimates come from owner-reported public-leaderboard <code>CLAIM</code>s (not organizer receipts). Phase 1 private chunks and Phase 2 expert-revised labels can shift spatial weights.</li>
<li><strong>Dual uniqueness disclosure:</strong> Under PI-1 (comparing dot sets against dot/top-N sets across all 2,162 rasters of 8 owners), worst overlap is <strong>65.56% ≤ 70%</strong> (54.06% vs prior <code>lbmc1</code>). Under the degenerate literal reading where <code>17GEMSDOE E-proba-multiscale</code> marks 100% of all 5,167,373 footprint cells positive, every nonempty submission has 100% literal overlap (documented in <code>IRREGULARITIES.md</code>).</li>
<li><strong>Flagged fleet irregularities:</strong> 6 empty (0-KB) sibling repos (<code>EUGGEMSDOE1..3</code>, <code>GINNYGEMSDOE1..3</code>), cross-band derivative unit scaling mismatch (`100–1000×`) between <code>B03 tmi_hg</code> and <code>B09 tmi_vg</code> (solved via direct 2D FFT derivatives in <code>gems/riesz_locked.py</code>), and 5 cross-repo <code>CLAIM</code> attributions resolved by exact filename/byte matching.</li>
<li><strong>Next steps (no slot and no new experiment now):</strong> resolve the missing assigned method paragraph and the registry witness representation in writing; restore the complete provenance-verified feature cache; then, in a future authorized lane with a fresh budget, rerun a candidate against shared holdout and all registry gates before making a separate slot-selection decision. Consider an official 3DEP LiDAR data-access check only if the selected hypothesis requires it.</li>
</ul></section>
<section class="box"><h2 id="official">Official Source Links for Manual Review</h2>{official_sources_table()}</section>"""

    howto = f"""<nav class="small"><a href="index.html">← Back to Executive Summary</a> · <a href="nine-sites.html">Nine-site analysis</a></nav>
{submission_box(card)}
<section class="box"><h2>How to Submit to DrivenData (3 Simple Steps)</h2>
<ol>
<li><strong>Check the clearance badge first.</strong> The current research-only file is <code>{esc(Path(card['raster']['file']).name)}</code> (SHA-256 <code>{esc(card['raster_sha256'])}</code>). Download the linked TIFF only for research unless the top status explicitly says <strong>OK TO SUBMIT</strong>. The current artifact says <strong>DO NOT SUBMIT</strong>; do not upload it or use its example name/note.</li>
<li>Only for a future separately cleared artifact, download its exact <code>.tif</code> (or one-TIFF <code>.zip</code>) without re-saving it in GIS software.</li>
<li>Only then open the official portal, upload that exact file, use its displayed submission name/note, verify the rolling cap, and record any returned receipt in <code>ledger/submissions.csv</code> as <code>ORGANIZER-CONFIRMED</code>.</li>
</ol>
<div class="warn"><strong>Weekly limit:</strong> <strong>3 submissions per week</strong> (per DrivenData staff in Forum #11553, the limit displayed on the competition website prevails). Confirm whether prior <code>2026-10-27</code> <code>lbmc1</code> was already uploaded before spending a slot. Before the competition closes, select <strong>one</strong> final submission for Phase 1 private + Phase 2 expert scoring.</div>
</section>
<section class="box"><h2>Automated Portal Compliance Checklist</h2>
<table><tr><th>DrivenData Requirement</th><th>Verified Primary File Receipt</th></tr>
<tr><td>Single-band GeoTIFF (<code>.tif</code>) or <code>.zip</code> with one GeoTIFF</td><td><code>count = 1</code>; companion ZIP contains only that TIFF</td></tr>
<tr><td>CRS matches training data (<code>EPSG:32611</code>)</td><td><code>EPSG:32611</code> (exact match to <code>sample_submission.tif</code>)</td></tr>
<tr><td>100 m resolution, exact bounds &amp; dimensions</td><td><code>3292 × 3730</code> px, affine <code>(100, 0, 243350, 0, −100, 4508550)</code></td></tr>
<tr><td><code>float32</code> values strictly in <code>[0, 1]</code></td><td><code>float32</code>, binary values <code>{{0.0, 1.0}}</code>, <code>0</code> NaN, <code>0</code> Inf</td></tr>
<tr><td>Exterior cells handled safely without range violations</td><td>Exact <code>0.0</code> across all 7,108,787 exterior cells and <code>nodata=None</code> (proven accepted across 133 scored fleet submissions and immune to range errors)</td></tr>
</table></section>
<section class="box"><h2>Why “Predicted values must be in range [0, 1]” Happens &amp; Automated Fix</h2>
<p>The DrivenData validator checks raw band values prior to masking; <code>NaN</code>, <code>±Inf</code>, float32 nodata sentinels like <code>-3.4028235e+38</code>, or unclipped scores <code>&lt;0</code> or <code>&gt;1</code> trigger <q>Predicted values must be in range [0, 1]</q>. Every <code>*-zeros.tif</code> served by this repository is automatically gated by <code>gems/gates.py</code> + <code>vendor/gems57/validate.py</code> + <code>scripts/check_site.py</code>:</p>
<pre class="copy">import numpy as np, rasterio
with rasterio.open("raw_prediction.tif") as src:
    arr = src.read(1).astype("float32"); prof = src.profile.copy()
arr = np.nan_to_num(arr, nan=0.0, posinf=1.0, neginf=0.0)
arr[arr &lt; -1e30] = 0.0
arr = np.clip(arr, 0.0, 1.0).astype("float32")
prof.update(dtype="float32", count=1, nodata=None, compress="deflate")
with rasterio.open("clean_submission-zeros.tif", "w", **prof) as dst:
    dst.write(arr, 1)</pre>
</section>
<section class="box"><h2>Official Source Links for Manual Review</h2>{official_sources_table()}</section>"""

    claims = json.loads((EVID / "claims_matched_20261028.json").read_text(encoding="utf-8"))["rows"]
    blocks = []
    fitted = {(r["site"], r["name"]): r for r in model["rows"]}
    for site, s in f9.items():
        rows = sorted([r for r in claims if r["site"] == site], key=lambda r: -r["claim"])
        u = f9u.get(site, {})
        trs = "".join(
            f"<tr><td>{'⭐ ' if r['name'] == s['best'] else ''}{esc(r['name'])}</td><td>{r['claim']:.4f}</td>"
            f"<td>{fitted.get((site, r['name']), {}).get('logo', float('nan')):.3f}</td>"
            f"<td class=\"mono small\">{esc(r.get('match', {}).get('path', '—'))}</td></tr>"
            for r in rows
        )
        blocks.append(
            f"""<section class="box"><h2 id="{esc(site)}">{esc(site)}: Peak {s['claim']:.4f} (CLAIM)</h2>
<p><a class="btn btn2" href="{esc(s['raw_url'])}">⬇ Download peak file (study only)</a> <a href="{esc(s['blob_url'])}">GitHub @ {esc(s['commit'][:10])}</a> · SHA-256 <span class="mono">{esc(s['sha256'])}</span></p>
<p><strong>Unique across 8-owner fleet (2,162 rasters)?</strong> {'Yes' if u.get('unique_pi1') else 'No — 100% clone'}. Worst 3-px overlap {u.get('worst_overlap', 0):.3f} and |ρ| {abs(u.get('worst_rho', 0)):.3f}, against {esc(', '.join(u.get('worst_overlap_in', [])))}. Identical bytes also served by: {esc(', '.join(u.get('identical_bytes_elsewhere', [])) or 'none')}.</p>
<table><tr><th>Submission (owner-reported)</th><th>CLAIM</th><th>MODEL (LOGO)</th><th>Matched Repository File</th></tr>{trs}</table></section>"""
        )
    nine = f"""<nav class="small"><a href="index.html">← Back to Executive Summary</a> · <a href="how-to-submit.html">How to submit</a></nav>
<h1>Nine Focus Sites: Highest-Scoring &amp; Latest Submissions Audit (2026-10-28)</h1>
<p class="small">These are owner-reported <code>CLAIM</code> scores and a pinned inventory snapshot, not current organizer receipts or a live registry. None of the nine site peak files should be re-submitted as-is. GEMSDOE92's current artifact <a href="downloads/{esc(Path(card['raster']['file']).name)}">{esc(Path(card['raster']['file']).name)}</a> is a format-validated research download only (**DO NOT SUBMIT**); it fails the literal registry stop and the R0 holdout comparison.</p>
<section class="box"><table><tr><th>Site</th><th>Peak File (Commit-Pinned)</th><th>CLAIM</th><th>MODEL (LOGO)</th><th>Unique vs 8-Owner Fleet?</th></tr>{focus9_rows(f9, f9u, model)}</table></section>
{''.join(blocks)}"""

    root = f"""<meta http-equiv="refresh" content="0; url=docs/index.html">
<p><a href="docs/index.html">GEMSDOE92 Executive Summary &amp; Research Download (DO NOT SUBMIT) →</a></p>
{submission_box(card, href_prefix="docs/").replace('data-primary="true" ', '')}"""

    return {
        DOCS / "index.html": page("GEMSDOE92 — DOE GEMS Research Download & Executive Summary (2026-10-28)", idx),
        DOCS / "how-to-submit.html": page("GEMSDOE92 — How to Submit & [0, 1] Compliance Guide", howto),
        DOCS / "nine-sites.html": page("GEMSDOE92 — Nine Focus Sites & 8-Owner Fleet Audit", nine),
        ROOT / "index.html": page("GEMSDOE92 — DOE GEMS Submission", root),
        DL / "current_submission.json": json.dumps(current, indent=2) + "\n",
        DL / "readiness.json": json.dumps(readiness, indent=2) + "\n",
    }


# Do not call the historical renderer: it hard-codes a promotion and changes
# the user-specified uniqueness rule. This fail-closed renderer supersedes it.
def render() -> dict[Path, str]:
    try:
        from scripts.render_safe_review import render as safe_render
    except ModuleNotFoundError:
        from render_safe_review import render as safe_render
    card = load()[0]
    if card.get("verdict") != "negative" or card.get("submission_eligible") is not False:
        raise ValueError("blocked: no validated promotion is implemented by this renderer")
    return safe_render(card)


def main() -> int:
    for p, t in render().items():
        p.write_text(t, encoding="utf-8")
        print("wrote", p.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
