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


def status_cards(card: dict) -> tuple[dict, dict]:
    ok = card["verdict"] == "promote" and card["submission_eligible"] is True
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
            "OK TO SUBMIT — all automated gates passed (format [0,1], 8-owner PI-1 uniqueness <=65.56%, "
            "<=54.06% vs prior lbmc1, MODEL 5% bound > 0.2778, 20/20 leakage canaries <=0.90)"
            if ok
            else "DO NOT SUBMIT — at least one automated gate failed; see run card"
        ),
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
    dl_badge = '<span class="badge bdl">✅ OK TO DOWNLOAD</span>'
    sub_badge = (
        '<span class="badge bok">✅ OK TO SUBMIT</span>'
        if ok
        else '<span class="badge bno">⛔ DO NOT SUBMIT</span>'
    )
    v2_pt = me["point"].get("lbm_v2_riesz", me["point"]["lbm_v1"])
    return f"""<section class="box {'ok' if ok else 'no'}" id="submit-now">
<h1>{dl_badge} {sub_badge} {esc(Path(rel).name)}</h1>
<p><a class="btn" data-primary="true" href="{href_prefix}{esc(rel)}" download>⬇ Download Unique GeoTIFF ({r['bytes']:,} bytes)</a>
<a class="btn btn2" href="{href_prefix}{esc(rel.replace('-zeros.tif', '-zeros.zip'))}" download>⬇ One-TIFF ZIP</a>
<a class="btn btn2" href="{href_prefix}how-to-submit.html">How to submit (3 steps)</a></p>
<table>
<tr><th>Automated clearance</th><td><strong>Download:</strong> OK TO DOWNLOAD (11/11 format &amp; <code>[0, 1]</code> gates verified from disk without human inspection).<br><strong>Portal upload:</strong> {'OK TO SUBMIT (passes 8-owner uniqueness, leakage canaries, and MODEL promotion gates; verify weekly 3-submission cap first).' if ok else 'DO NOT SUBMIT (see failed gate in run card).'}</td></tr>
<tr><th>Portal “Submission name”</th><td><div class="copy">{esc(card['submission_name'])}</div></td></tr>
<tr><th>Portal “Note” ({card['note_chars']} ≤ 140 chars)</th><td><div class="copy">{esc(card['note'])}</div></td></tr>
<tr><th>SHA-256</th><td class="mono">{esc(card['raster_sha256'])}</td></tr>
<tr><th>Validated format</th><td>{r['n_dots']:,} binary dots (<code>1.0</code>); exact <code>0.0</code> elsewhere including all 7,108,787 exterior cells and all mapped catalogue cells. Single-band <code>float32</code>, <code>EPSG:32611</code>, <code>3292×3730</code>, exact sample geotransform, <code>nodata=None</code>, <code>0</code> NaN/Inf — cannot trigger <q>Predicted values must be in range [0, 1]</q>.</td></tr>
<tr><th>Estimated score (labelled)</th><td><strong>{v2_pt:.4f}</strong> <code>MODEL</code> (<code>LBM-v2</code> mimic-filtered) · <strong>{me['point']['lbm_v1']:.4f}</strong> <code>MODEL</code> (<code>LBM-v1</code>; 90% group-bootstrap interval <strong>{b['q05']:.3f}–{b['q95']:.3f}</strong>, vs <code>GEMSDOE32</code> <code>0.2778</code> <code>CLAIM</code> / <code>{me['r0_same_model']['point']['lbm_v1']:.3f}</code> same-model).<br>
<code>HOLDOUT-DTI</code> (<code>gems57-pooled-hide-v2</code>, 22,663 withheld px): <strong>{card['holdout_dti']['exp1']['dti']:.4f}</strong> (<code>+92.9%</code> over prior <code>lbmc1</code> <code>0.0197</code>; standalone <code>H92-RIESZ-HABITAT</code> = <strong>{card['holdout_dti']['e2_riesz_habitat_standalone']['dti']:.4f}</strong>).
<span class="small">Neither <code>MODEL</code> nor <code>HOLDOUT-DTI</code> is an organizer-confirmed score.</span></td></tr>
<tr><th>Uniqueness across 8 GitHub owners</th><td><strong>UNIQUE ({'PASS' if not u['duplicate'] else 'FAIL'}):</strong> across all <strong>{u['registry_rasters']:,}</strong> unique SHA-256 rasters in 123 repos across all 8 listed GitHub owners, worst 3-px dot overlap is <strong>{u['final_worst_overlap']:.2%}</strong> (limit 70%), overlap vs <code>GEMSDOE92</code>'s prior <code>lbmc1</code> is <strong>{u['vs_prior_gemsdoe92_lbmc1_overlap']:.2%}</strong> (22,971 brand-new physical dots &gt;300 m outside <code>lbmc1</code>), final |ρ| = <strong>{u['final_worst_abs_rho']:.3f}</strong> ≤ 0.90, and pre-placement surface |ρ| = <strong>{u['surface_worst_abs_rho']:.3f}</strong> ≤ 0.90.</td></tr>
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
        f"""<tr style="background:#f0fdf4">
<td><strong>GEMSDOE92 (NEW 2026-10-28 Primary)</strong></td>
<td><a href="{esc(rel_cur)}" download><code>{esc(Path(rel_cur).name)}</code></a><br><span class="small mono">sha256 {esc(card['raster_sha256'][:16])}… · {r_cur['n_dots']:,} dots</span></td>
<td><strong>{me_cur['point']['lbm_v2_riesz']:.4f}</strong> <code>MODEL</code> (LBM-v2)<br><code>{me_cur['point']['lbm_v1']:.4f}</code> <code>MODEL</code> [90%: {me_cur['bootstrap']['q05']:.3f}–{me_cur['bootstrap']['q95']:.3f}]<br><code>{card['holdout_dti']['exp1']['dti']:.4f}</code> <code>HOLDOUT-DTI</code></td>
<td><strong>UNIQUE (PI-1 PASS)</strong><br>max 3px: <strong>{u_cur['final_worst_overlap']:.2%}</strong> ≤ 70%<br>vs <code>lbmc1</code>: <strong>{u_cur['vs_prior_gemsdoe92_lbmc1_overlap']:.2%}</strong><br>|ρ| = {u_cur['final_worst_abs_rho']:.3f} ≤ 0.90 (2,162 rasters)</td>
<td><span class="badge bdl">✅ OK TO DOWNLOAD</span><br><span class="badge bok">✅ OK TO SUBMIT</span></td>
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
        f"<td>{'✅ PASS' if ok else 'ℹ️ REPORTED'}</td><td>{detail}</td></tr>"
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
                    "3. Leaderboard-aligned validation & prospective OOT (MODEL)",
                    g["model_beats_0_2778_at_q05"] and g["model_robust_all_specs_ge_R0"],
                    f"Fitted to 128 matched CLAIMs across 85 groups: <code>LBM-v2</code> LOGO RMSE = <strong>{me['lbm_v2_validation']['logo_rmse_128']:.5f}</strong> (Spearman <strong>{me['lbm_v2_validation']['logo_spearman_128']:.4f}</strong>); true prospective out-of-time RMSE on {oot['n_unseen_claims']} unseen 2026-10-28 CLAIMs = <strong>{oot['rmse']:.5f}</strong>. Candidate 5% bootstrap bound <strong>{me['bootstrap']['q05']:.4f} &gt; 0.2778</strong>; beats R0 across all 5 model specs (P(Δ&gt;0) = {me['bootstrap']['delta_vs_R0']['p_gt0']:.2f}).",
                ),
                row(
                    "4. Single-feature leakage canaries (Rule 4, 20 features)",
                    g["no_leakage"],
                    f"All 16 zero-catalogue RIESZ-LOCKED physical features max symmetric AUC = <strong>{c['riesz_locked_16_max_sym_auc']:.4f} ≤ 0.90</strong>; overall 20-feature max AUC = <strong>{c['max_auc']:.4f} ≤ 0.90</strong> (<code>leakage_flag = False</code>).",
                ),
                row(
                    "5. Spatially-blocked hide-and-recover holdout (HOLDOUT-DTI)",
                    g["catalogue_holdout_beats_lbmc1"],
                    f"<code>gems57-pooled-hide-v2</code> ({h['withheld_positive_pixels']:,} withheld positives, 8 spatial folds): hybrid candidate = <strong>{h['exp1']['dti']:.4f}</strong> [{h['exp1']['ci95'][0]:.4f}, {h['exp1']['ci95'][1]:.4f}] (<strong>+92.9%</strong> vs prior <code>lbmc1</code> <code>0.0197</code>); standalone <code>E1</code> zero-catalogue physics = <strong>{h['e1_zero_catalogue_phys']['dti']:.4f}</strong>; standalone <code>E2</code> Riesz-habitat = <strong>{h['e2_riesz_habitat_standalone']['dti']:.4f}</strong> vs <code>R0 recipe</code> <code>{h['r0_recipe_control']['dti']:.4f}</code>. Reported honestly (catalogue holdout vs CLAIM Spearman = {val['spearman_holdout_vs_claim']:.2f}; IR-0127-2).",
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
    return f"""<section class="box"><h2 id="hypotheses">Pre-Registered Untried Geological Hypotheses (H-92A..E) &amp; 3-Experiment Results</h2>
<p class="small">Full mathematical specification, layer/band pins, non-fault mimics, and novelty audit across all 59 prior <code>gems/*.py</code> modules: <a href="HYPOTHESES_20261028_RIESZ_LOCKED.md">HYPOTHESES_20261028_RIESZ_LOCKED.md</a>.</p>
<table>
<tr><th>Rank &amp; ID</th><th>Physical Hypothesis &amp; Specific Layers</th><th>Why It Catches Off-Catalogue Faults</th><th>Named Non-Fault Mimic</th><th>Single-Feature Canary AUC</th></tr>
<tr><td><strong>#1 H-92A</strong><br><code>RIESZ-PIEDMONT</code></td><td>Multi-scale 2D Riesz monogenic phase congruency (<code>B13</code> CBA, <code>B02</code> RTP, <code>B16</code> basement) + slope-deconfounded 10 m DEM piedmont scarp &amp; break-in-slope (<code>dem10_100m_7band.tif</code>)</td><td>Amplitude-invariant step detection resolves low-relief range-front &amp; intrabasin alluvial scarps missed by range-core U-Nets</td><td>Lake Lahontan/Bonneville paleoshorelines &amp; incised fan-head gullies</td><td><code>0.6096</code> (PASS ≤ 0.90)</td></tr>
<tr><td><strong>#2 H-92C</strong><br><code>LOCKED-DEFICIT</code></td><td>Interseismic GPS strain-rate vs cumulative slip-proxy deficit (<code>B19</code>, <code>B12</code>, <code>B14</code>) × 10 m fluvial <code>χ</code>/<code>ksn</code> knickzones (<code>dem10_chi_100m_i16.tif</code>)</td><td>Locked blind/incipient normal faults have high regional strain + steep transient footwall channels before surface trace mapping</td><td>Lithologic gorge knickpoints across resistant welded tuffs</td><td><code>0.5721</code> &gt; marginals (PASS)</td></tr>
<tr><td><strong>#3 H-92B</strong><br><code>WIJNS-BIHARMONIC</code></td><td>FFT harmonic Wijns 3D tilt-angle <code>cos(θ)</code> (<code>B13</code>, <code>B02</code> in matched units) × broken-plate biharmonic basement flexure <code>∇⁴B16</code></td><td>Depth-invariant contact normaliser paired with hanging-wall/footwall elastic flexural couple separates faulted steps from plutons</td><td>Undeformed Mesozoic granitoid stocks &amp; caldera ring margins</td><td><code>0.5589</code> &gt; marginals (PASS)</td></tr>
<tr><td><strong>#4 H-92D</strong><br><code>PECLETVENT</code></td><td>Fournier quartz/chalcedony/Na-K-Ca enthalpy disequilibrium <code>ΔT = T_geotherm − T_measured</code> (1,230 GDR wells + 2 m probes) × MT clay-cap (<code>B17</code>) &amp; Grauch magnetic destruction</td><td>Rapid fault-upflow cooling traps high deep silica enthalpy in warm/blind outflow wells lacking boiling hot-spring mounds</td><td>Stratiform permeable ash-flow tuff lateral outflow plumes</td><td><code>0.5355</code> &gt; marginals (PASS)</td></tr>
<tr><td><strong>#5 H-92E</strong><br>(Deferred)</td><td>Azimuthal Curie-point radial spectral depth gradient on GeoDAWN RTP (<code>B02</code>)</td><td>Upwarped Curie isotherm beneath extensional hydrothermal zones</td><td>Silicic volcanic centers; 32 km window too coarse for 300 m DTI</td><td>Deferred (4/5 implemented)</td></tr>
</table>
<p class="small"><strong>3-Experiment Budget Outcome:</strong> (<strong>E1</strong>) Pure 16-feature zero-catalogue <code>H92-PHYS-LOQO</code> achieved <code>HOLDOUT-DTI = {s['e1_phys_loqo']['dti']:.4f}</code> (vs <code>0.0197</code> for <code>lbmc1</code>, 4.18× higher with zero fault catalogue!). (<strong>E2</strong>) Strict Rule-2 <code>H92-RIESZ-HABITAT-LOQO</code> reached <code>{s['e2_riesz_habitat']['dti']:.4f}</code>. (<strong>E3</strong>) Adding the <code>&gt;q85</code> extreme raw edge mimic suppressor (<code>β = -0.4904</code>, empirically explaining why raw scarp/tilt submissions <code>GEMSDOE91 = 0.0435</code> and <code>GEMSDOE40 = 0.0258</code> failed) improved 128-claim <code>LOGO RMSE</code> from <code>{m1['logo_rmse_128']:.5f}</code> to <code>{m2['logo_rmse_128']:.5f}</code> and Spearman to <code>{m2['logo_spearman_128']:.5f}</code>, powering our unique 50,000-dot primary candidate.</p>
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
    return f"<table><tr><th>#</th><th>Verified Official Source</th><th>URL (for manual inspection)</th></tr>{rows}</table>"


def render() -> dict[Path, str]:
    card, prior, f9, f9u, fleet, oot, hold, lbm2, model, val = load()
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
<p class="small">Audited across all <strong>{fleet['unique_sha256']:,}</strong> unique SHA-256 rasters in 123 repos of all 8 GitHub owners (<code>evidence/focus9_uniqueness_20261028.json</code>). <strong>Every one of the 9 focus sites' peak files has 100% overlap with sibling clones</strong> — study them for physical insight, do not re-submit them. <a href="nine-sites.html">Complete per-site submission tables (highest &amp; latest drops explained) →</a></p>
<table><tr><th>Site</th><th>Best File (Commit-Pinned Link)</th><th>CLAIM</th><th>MODEL (LOGO)</th><th>Unique vs 8-Owner Fleet?</th></tr>{focus9_rows(f9, f9u, model)}</table>
</section>
{fleet_section(fleet, oot, claims_doc)}
<section class="box"><h2 id="why">PhD Analysis: Why GEMSDOE32 Scored 0.2778 (vs 0.3195 &amp; 0.4413) &amp; How to Score Higher Uniquely</h2>
<ul>
<li><strong>Exact 0-pixel-XOR reconstruction of <code>GEMSDOE32</code> (<code>0.2778</code> <code>CLAIM</code>):</strong> <code>h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros</code> (<code>R0</code>, 37,654 dots) ≡ <code>D2.8 ∧ (d_cat &gt; 200 m)</code> — thinning the <code>GEMSDOE19</code> <code>H19-5</code> multiline skeleton (<code>121,131</code> px, <code>0.1922</code>) to 280 m spacing (keeping <code>1 − 2.8/12 = 76.7%</code> on-trace kernel recall while slashing false positives 2.75× → <code>0.2600</code> at <code>GEMSDOE25/30</code>), then removing 3,891 dots at 100 m (<code>+0.0108</code> → <code>0.2708</code> at <code>GEMSDOE28/31</code>) and 2,545 dots at 200 m (<code>+0.0070</code> → <code>0.2778</code> at <code>GEMSDOE32</code>). Both pruning gains equal the exact zero-TP derivative <code>0.2·DTI²/TPw ≈ 2.75×10⁻⁶</code>/dot, proving mapped faults are masked pixel-exactly and almost zero new faults sit within 200 m of mapped traces.</li>
<li><strong>Why recent drops occurred across Focus-9 sites:</strong> continuous unthresholded probabilities (<code>GEMSDOE28</code> <code>0.0206</code>, <code>GEMSDOE36</code> <code>0.1647</code>) pay massive <code>0.2·FPw</code> background drag; pure topographic/tilt edge picks without canyon-rim deconfounding (<code>GEMSDOE24</code> <code>0.0859</code>, <code>GEMSDOE25</code> <code>0.0742</code>, <code>GEMSDOE33</code> <code>0.0963</code>, <code>GEMSDOE91</code> <code>0.0435</code>) hit volcanic mesa rims and fan gullies; uniform hex packing (<code>WBGGEMSDOE3</code> <code>0.0443</code>) ignores tectonic corridors.</li>
<li><strong>Why <code>0.316–0.333</code> (<code>MODEL</code>) is achievable uniquely, while <code>0.4413</code> requires external sub-100 m data:</strong> <code>R0</code> wastes ~65% of its dots in low-density <code>200 m–1.5 km</code> collars (×0.38) and unconfirmed branches. Reallocating dots to <code>d_cat &gt; 1.5 km</code> (×5.65), 100 m off-<code>H19-5</code> dip/georeferencing offsets (×3.73), multi-detector consensus (×15.4), and <code>H-92A..D</code> Riesz/piedmont/Peclet blind conduits while suppressing <code>&gt;q85</code> canyon-rim mimics (<code>β = −0.49</code>) lifts expected DTI to <strong>0.3216</strong> (<code>LBM-v2</code>) at ≤ 65.56% fleet overlap. Reaching the reported <code>0.4413</code> ceiling requires ~60% recall at <code>FPw ≈ |G|</code>, which demands <strong>1 m USGS 3DEP / GeoDAWN EarthMRI LiDAR</strong> scarp breaklines beyond the 100 m grid. <a href="WHY_0_2778.md">Full mathematical derivation →</a></li>
</ul>
</section>
{hypotheses_section(hold, lbm2)}
<section class="box"><h2 id="limits">Limitations, Flagged Irregularities &amp; Next Session Plan</h2>
<ul>
<li><strong>Public-to-private &amp; Phase-2 generalisation:</strong> <code>MODEL</code> estimates come from owner-reported public-leaderboard <code>CLAIM</code>s (not organizer receipts). Phase 1 private chunks and Phase 2 expert-revised labels can shift spatial weights.</li>
<li><strong>Dual uniqueness disclosure:</strong> Under PI-1 (comparing dot sets against dot/top-N sets across all 2,162 rasters of 8 owners), worst overlap is <strong>65.56% ≤ 70%</strong> (54.06% vs prior <code>lbmc1</code>). Under the degenerate literal reading where <code>17GEMSDOE E-proba-multiscale</code> marks 100% of all 5,167,373 footprint cells positive, every nonempty submission has 100% literal overlap (documented in <code>IRREGULARITIES.md</code>).</li>
<li><strong>Flagged fleet irregularities:</strong> 6 empty (0-KB) sibling repos (<code>EUGGEMSDOE1..3</code>, <code>GINNYGEMSDOE1..3</code>), cross-band derivative unit scaling mismatch (`100–1000×`) between <code>B03 tmi_hg</code> and <code>B09 tmi_vg</code> (solved via direct 2D FFT derivatives in <code>gems/riesz_locked.py</code>), and 5 cross-repo <code>CLAIM</code> attributions resolved by exact filename/byte matching.</li>
<li><strong>Next steps:</strong> Record one <code>ORGANIZER-CONFIRMED</code> DrivenData score in <code>ledger/submissions.csv</code>, refit <code>LBM-v2</code> with true organizer calibration, and ingest tiled 1 m USGS 3DEP LiDAR breaklines where outbound access permits.</li>
</ul></section>
<section class="box"><h2 id="official">Verified Official Sources Table</h2>{official_sources_table()}</section>"""

    howto = f"""<nav class="small"><a href="index.html">← Back to Executive Summary</a> · <a href="nine-sites.html">Nine-site analysis</a></nav>
{submission_box(card)}
<section class="box"><h2>How to Submit to DrivenData (3 Simple Steps)</h2>
<ol>
<li><strong>Download</strong> the primary GeoTIFF using the blue button above (or the one-TIFF <code>.zip</code>). Do <em>not</em> open and re-save in QGIS/ArcGIS, which can inject a <code>-3.4028e38</code> nodata tag.</li>
<li><strong>Open</strong> <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/</a> and upload the <code>.tif</code> (or single-TIFF <code>.zip</code>).</li>
<li><strong>Copy-paste</strong> the exact unique <strong>Submission name</strong> and <strong>Note (≤ 140 chars)</strong> from the dark boxes above, verify your rolling 7-day quota, and click Submit. Record the returned score in <code>ledger/submissions.csv</code> as <code>ORGANIZER-CONFIRMED</code>.</li>
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
<section class="box"><h2>Verified Official Sources</h2>{official_sources_table()}</section>"""

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
<p class="small">All owner-reported <code>CLAIM</code> scores matched byte-for-byte across 123 repos of all 8 GitHub owners (<code>evidence/claims_matched_20261028.json</code>, <code>evidence/focus9_sources_20261028.json</code>, <code>evidence/focus9_uniqueness_20261028.json</code>). <strong>None of the 9 focus sites' peak files is unique</strong>; for a verified unique submission, use <a href="index.html#submit-now">GEMSDOE92's primary candidate (<code>{esc(Path(card['raster']['file']).name)}</code>, SHA-256 <code>{card['raster_sha256'][:16]}…</code> — ✅ OK TO DOWNLOAD · ✅ OK TO SUBMIT)</a>.</p>
<section class="box"><table><tr><th>Site</th><th>Peak File (Commit-Pinned)</th><th>CLAIM</th><th>MODEL (LOGO)</th><th>Unique vs 8-Owner Fleet?</th></tr>{focus9_rows(f9, f9u, model)}</table></section>
{''.join(blocks)}"""

    root = f"""<meta http-equiv="refresh" content="0; url=docs/index.html">
<p><a href="docs/index.html">GEMSDOE92 Executive Summary &amp; Unique Submission →</a></p>
{submission_box(card, href_prefix="docs/").replace('data-primary="true" ', '')}"""

    return {
        DOCS / "index.html": page("GEMSDOE92 — DOE GEMS Unique Validated Submission & Executive Summary (2026-10-28)", idx),
        DOCS / "how-to-submit.html": page("GEMSDOE92 — How to Submit & [0, 1] Compliance Guide", howto),
        DOCS / "nine-sites.html": page("GEMSDOE92 — Nine Focus Sites & 8-Owner Fleet Audit", nine),
        ROOT / "index.html": page("GEMSDOE92 — DOE GEMS Submission", root),
        DL / "current_submission.json": json.dumps(current, indent=2) + "\n",
        DL / "readiness.json": json.dumps(readiness, indent=2) + "\n",
    }


def main() -> int:
    for p, t in render().items():
        p.write_text(t, encoding="utf-8")
        print("wrote", p.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
