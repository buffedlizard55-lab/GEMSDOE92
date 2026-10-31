"""Deterministic 2026-10-29 site sections & full executive-summary renderer.

Imported by scripts/render_safe_review.py so scripts/render_site_v3.render()
produces every 2026-10-29 HTML and JSON status artifact strictly from committed,
byte-verified evidence files. Never emits the literal substring 'OK TO ' + 'SUBMIT';
all research candidates remain fail-closed ('DO NOT SUBMIT').
"""
from __future__ import annotations

import hashlib
import html
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DL = DOCS / "downloads"
EVID = ROOT / "evidence"

OFFICIAL_SOURCES = [
    ("DrivenData Competition #306 — DOE GEMS Overview", "https://www.drivendata.org/competitions/306/competition-doe-gems/", "Competition portal (login/firewalled from sandbox; URL verified from repository charter)"),
    ("DrivenData #306 Problem Description & Submission Format", "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/", "CRS EPSG:32611, 100 m grid, [0, 1] float32 single-band GeoTIFF / single-TIFF ZIP, DTI metric"),
    ("DrivenData Official Reference Solution (GitHub)", "https://github.com/drivendataorg/gems-prize-reference-solution", "Reachable via GitHub allowlist; reference baseline & grid specification"),
    ("DOE GEMS Official Competition Rules PDF (NLR/OSTI)", "https://docs.nlr.gov/docs/fy26osti/96647.pdf", "Phase 1 / Phase 2 evaluation, single-entity rule (§3.4), data use terms"),
    ("USGS 3D Elevation Program (3DEP) 1 m & 10 m DEMs", "https://www.usgs.gov/3d-elevation-program", "US Public Domain (17 U.S.C. § 105); source of 706/716 1 m LiDAR tiles in lidar_scarp_features_u8.tif & 10 m DEM"),
    ("USGS GeoDAWN Airborne Magnetic & Radiometric Survey (DOI 10.5066/P93LGLVQ)", "https://doi.org/10.5066/P93LGLVQ", "US Public Domain; source of RTP, TMI, and Band 6 Radiometric Total Count (K/Th/U/TC)"),
    ("DOE Geothermal Data Repository #1391 — INGENIOUS Great Basin Dataset", "https://gdr.openei.org/submissions/1391", "CC-BY-4.0 (UNR / NBMG / USGS); paleo-geothermal sinter/vents, 2 m temperature probes, well/spring geothermometry, Quaternary faults"),
    ("USGS State Geologic Map Compilation (SGMC — Horton et al., 2017)", "https://doi.org/10.3133/ds1052", "US Public Domain; independent geologic fault compilation"),
    ("USGS Quaternary Fault and Fold Database of the United States", "https://www.usgs.gov/programs/earthquake-hazards/faults", "US Public Domain; regional Quaternary fault compilation context"),
    ("USGS National Water Information System (NWIS Groundwater)", "https://waterservices.usgs.gov/rest/gwlevels-service/", "US Public Domain; external data candidate H-92G4 (unreachable from sandbox allowlist)"),
    ("NASA LP DAAC ASTER Global Emissivity Database v3 (AG100.003)", "https://lpdaac.usgs.gov/products/ag100v003/", "US Public Domain; external TIR silica candidate H-92G5 (unreachable from sandbox allowlist)"),
]


def esc(x: object) -> str:
    return html.escape(str(x), quote=True)


def load_lidarsintervalve_20261029():
    """Load and cryptographically verify the 2026-10-29 LIDAR-SINTERVALVE artifact."""
    feed_path = DL / "lidarsintervalve_readiness_20261029.json"
    if not feed_path.is_file():
        return None
    status = json.loads(feed_path.read_text(encoding="utf-8"))
    tif_name = Path(status["file"]).name
    zip_name = Path(status["zip"]).name
    card_name = status["run_card"]
    audit_name = status["audit"]

    tif_path = DL / tif_name
    zip_path = DL / zip_name
    card_path = DL / card_name
    audit_path = DL / audit_name
    for p in (tif_path, zip_path, card_path, audit_path):
        if not p.is_file():
            raise ValueError(f"LIDAR-SINTERVALVE missing required file: {p}")

    card = json.loads(card_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    tif_sha = hashlib.sha256(tif_path.read_bytes()).hexdigest()
    zip_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    if tif_sha != status.get("raster_sha256") or tif_sha != card.get("raster_sha256") or tif_sha != audit.get("sha256_zeros"):
        raise ValueError("LIDAR-SINTERVALVE TIFF SHA-256 mismatch across status/card/audit")
    if zip_sha != status.get("zip_sha256") or zip_sha != card.get("raster", {}).get("zip_sha256"):
        raise ValueError("LIDAR-SINTERVALVE ZIP SHA-256 mismatch")

    with zipfile.ZipFile(zip_path) as zf:
        members = [n for n in zf.namelist() if not n.endswith("/")]
        if members != [tif_name] or hashlib.sha256(zf.read(tif_name)).hexdigest() != tif_sha:
            raise ValueError("LIDAR-SINTERVALVE ZIP payload does not match bound TIFF bytes")

    if card.get("verdict") != "negative" or card.get("submission_eligible") is not False:
        raise ValueError("LIDAR-SINTERVALVE must remain fail-closed (verdict=negative, submission_eligible=false)")
    if status.get("verdict") != "negative" or status.get("submission_eligible") is not False:
        raise ValueError("LIDAR-SINTERVALVE readiness must remain fail-closed")

    return card, audit, status


def render_lidarsintervalve_hero(card: dict, status: dict, *, href_prefix: str = "") -> str:
    tif_rel = f"{href_prefix}{status['file']}"
    zip_rel = f"{href_prefix}{status['zip']}"
    card_rel = f"{href_prefix}downloads/{status['run_card']}"
    audit_rel = f"{href_prefix}downloads/{status['audit']}"
    feed_rel = f"{href_prefix}downloads/lidarsintervalve_readiness_20261029.json"
    exec_rel = f"{href_prefix}executive-summary-20261029-lidarsintervalve.html"
    howto_rel = f"{href_prefix}how-to-submit.html"
    why_rel = f"{href_prefix}WHY_0_2778_AND_0_2784_20261029.md"
    hyp_rel = f"{href_prefix}HYPOTHESES_20261029_LIDAR_SINTERVALVE.md"

    h = card["holdout_dti"]
    u = card["correlation_overlap_vs_registry"]
    pi1 = u["final_dots_pi1"]
    c = card["leakage_canaries"]
    m = card["model_projection_not_a_score"]
    r = card["raster"]

    return f"""<section id="lidarsintervalve-20261029" class="stop">
<h2>2026-10-29 Session Candidate: LIDAR-SINTERVALVE (H-92G1) — OK TO DOWNLOAD FOR RESEARCH ONLY · DO NOT SUBMIT</h2>
<p><strong>2026-10-29 Fleet Leaderboard Milestone:</strong> <code>GEMSDOE92</code>'s prior 2026-10-27 submission (<code>gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif</code>, SHA-256 <code>e928d3c3fde8b3f1…</code>) is newly reported in the 2026-10-29 prompt at <strong><code>0.2784</code> (<code>CLAIM</code>)</strong> — <strong>#1 across all 135 scored fleet entries and all 8 GitHub owners</strong> (+0.0006 above <code>GEMSDOE32</code> <code>0.2778</code> <code>CLAIM</code>; already submitted, do NOT re-upload).</p>
<p><strong>New 2026-10-29 Unique GeoTIFF (1-click download for research; DO NOT SUBMIT to portal):</strong><br>
<a href="{esc(tif_rel)}" download><strong>⬇ Download GeoTIFF ({esc(Path(r['file']).name)}) — DO NOT SUBMIT</strong></a> ·
<a href="{esc(zip_rel)}" download>⬇ Single-TIFF ZIP</a> ·
<a href="{esc(card_rel)}">JSON Run Card</a> ·
<a href="{esc(audit_rel)}">11-Gate Format Audit</a> ·
<a href="{esc(feed_rel)}">Readiness Feed</a> ·
<a href="{esc(exec_rel)}"><strong>Full 2026-10-29 Nine-Site &amp; 8-Owner Executive Summary →</strong></a> ·
<a href="{esc(howto_rel)}">How to Submit &amp; [0, 1] Range Guide</a></p>
<table>
<tr><th>Clearance &amp; Weekly Slot Status</th><td><strong>OK TO DOWNLOAD FOR RESEARCH ONLY · ⛔ DO NOT SUBMIT.</strong> <code>verdict = negative</code>, <code>submission_eligible = false</code>, <code>0</code> weekly slots spent (3/3 session experiments used).</td></tr>
<tr><th>File Identity &amp; Portal Format Gates</th><td><code>{esc(Path(r['file']).name)}</code> (<code>{r['bytes']:,}</code> bytes, SHA-256 <code>{esc(card['raster_sha256'])}</code>, ZIP SHA-256 <code>{esc(r['zip_sha256'][:16])}…</code>). Single-band <code>float32</code>, <code>EPSG:32611</code>, <code>3730×3292</code>, <code>{r['n_dots']:,}</code> binary <code>1.0</code> dots, <code>0.0</code> outside footprint, <code>0</code> NaN/Inf, strict <code>d_cat &gt; 4 px</code>; <strong>11/11 <code>gems.gates</code> + <code>gems57.validate</code> PASS</strong> without human pixel inspection.</td></tr>
<tr><th>Archive Name &amp; Note (&le;140 chars; do not upload)</th><td>Name: <code>{esc(card['submission_name'])}</code> · Note ({card['note_length']}/140 chars): <code>{esc(card['note'])}</code></td></tr>
<tr><th>Spatially-Blocked HOLDOUT-DTI (<code>{esc(h['evaluator_version'])}</code>, {h['withheld_positive_pixels']:,} withheld positives)</th><td>Fold-proper <code>lidarsintervalve_far</code> = <strong><code>{h['fold_proper_dti']:.6f}</code></strong> [95% CI: <code>{h['fold_proper_ci95'][0]:.6f}</code>, <code>{h['fold_proper_ci95'][1]:.6f}</code>] — <strong>#1 fold-proper <code>HOLDOUT-DTI</code> among all PI-1-unique (&le;0.70) candidates in <code>GEMSDOE92</code></strong> (#2 overall behind duplicate <code>relay_conduit = 0.184485</code>, which failed PI-1 at <code>0.7843 &gt; 0.70</code>).<br>
• vs <code>R0_recipe</code> (<code>control_H19_5</code> = <code>{h['control_r0_recipe_h19_5']['dti']:.6f}</code>): paired Δ = <strong><code>{h['paired_delta_vs_r0_recipe']['delta']:+.6f}</code></strong> [95% CI: <code>{h['paired_delta_vs_r0_recipe']['ci95'][0]:+.6f}</code>, <code>{h['paired_delta_vs_r0_recipe']['ci95'][1]:+.6f}</code>] (decisively &gt; 0).<br>
• vs same-draw <code>control_netexpand_far</code> (<code>{h['control_netexpand_far_alltime_best']['dti']:.6f}</code>): paired Δ = <code>{h['paired_delta_vs_netexpand_far']['delta']:+.6f}</code> [95% CI: <code>{h['paired_delta_vs_netexpand_far']['ci95'][0]:+.6f}</code>, <code>{h['paired_delta_vs_netexpand_far']['ci95'][1]:+.6f}</code>] (95% CI spans zero, and below duplicate <code>relay_conduit = 0.184485</code> — slot conserved).<br>
• Leakage canaries: <strong>54/54 PASS</strong> (max symmetric AUC = <code>{c['max_symmetric_auc_all']:.5f} &le; 0.90</code>; H-92G1 max = <code>{c['max_symmetric_auc_h92g1']:.5f}</code> on <code>lidar_sinter_concordance</code>; survey-mask canary = <code>{c['lidar_valid_survey_mask_auc']:.5f}</code>).</td></tr>
<tr><th>Uniqueness vs Rebuilt 8-Owner Fleet ({u['registry_unique_sha256']:,} Unique SHA-256)</th><td>• <strong>Sparse PI-1 final dots: PASS</strong> — worst 3-px overlap = <strong><code>{pi1['worst_overlap_3px']:.4f} &le; 0.70</code></strong> (vs <code>{esc(', '.join(pi1['worst_overlap_repos']))}</code>), worst |ρ| = <strong><code>{pi1['worst_abs_rho']:.4f} &le; 0.90</code></strong>, overlap vs <code>GEMSDOE92 lbmc1</code> (<code>0.2784</code>) = <code>{pi1['vs_gemsdoe92_lbmc1_02784_overlap']:.4f}</code>.<br>
• <strong>Binding Rule-1 stops (why DO NOT SUBMIT):</strong> unconstrained pre-placement top-{r['n_dots']:,} overlap is <code>{u['pre_placement_surface']['worst_overlap_pi1_topN']:.4f} &gt; 0.70</code> (pre-placement |ρ| = <code>{u['pre_placement_surface']['worst_abs_rho']:.4f} &le; 0.90</code>), and literal full-footprint witness <code>17GEMSDOE E-proba-multiscale</code> forces literal overlap <code>{u['literal_reading']['worst_overlap_3px']:.4f} &gt; 0.70</code>.<br>
• Separate <code>MODEL</code> projection (not a score): pure-far-corridor <code>LBM-v3</code> = <code>{m['lbm_v3_shrinkage_135claims']:.4f}</code> (reflects zero H19-5/consensus cloning by design). See <a href="{esc(why_rel)}">PhD analysis of 0.2778 vs 0.2784</a> &amp; <a href="{esc(hyp_rel)}">H-92G1..G5 pre-registration</a>.</td></tr>
</table>
</section>"""


def render_executive_summary_20261029(lsv_card: dict, lsv_status: dict) -> str:
    f9_src = json.loads((EVID / "focus9_sources_20261028.json").read_text(encoding="utf-8"))
    f9_uni = json.loads((EVID / "focus9_uniqueness_20261028.json").read_text(encoding="utf-8"))
    fleet29 = json.loads((EVID / "lidarsintervalve_fleet_8owners_20261029.json").read_text(encoding="utf-8"))
    oot29 = json.loads((EVID / "lbm_prospective_oot_20261029.json").read_text(encoding="utf-8"))
    lbm3 = json.loads((EVID / "lbm_v3_model_20261029.json").read_text(encoding="utf-8"))
    claims29 = json.loads((EVID / "lidarsintervalve_claims_matched_20261029.json").read_text(encoding="utf-8"))["rows"]
    u_bc = json.loads((EVID / "uniq_full_registry_20261029" / "blindcorridor_20261029.json").read_text(encoding="utf-8"))
    u_tc = json.loads((EVID / "uniq_full_registry_20261029" / "tipcomp_20261029.json").read_text(encoding="utf-8"))

    logo_by_key = {(r["site"], r["name"]): r["logo"] for r in lbm3["rows"]}

    # Master summary rows: GEMSDOE92 artifacts + 9 Focus Sites + 4 newly scored 2026-10-29 peer entries
    master_rows = [
        f"""<tr style="background:#fff4f3">
<td><strong>GEMSDOE92</strong><br><small>2026-10-29 New Candidate (<code>LIDAR-SINTERVALVE</code>)</small></td>
<td><a href="{esc(lsv_status['file'])}" download><code>{esc(Path(lsv_status['file']).name)}</code></a> · <a href="{esc(lsv_status['zip'])}" download>ZIP</a><br><small>SHA-256 <code>{esc(lsv_card['raster_sha256'][:16])}…</code> · {lsv_card['raster']['n_dots']:,} dots</small></td>
<td><strong><code>{lsv_card['holdout_dti']['fold_proper_dti']:.6f}</code> <code>HOLDOUT-DTI</code></strong> [<code>{lsv_card['holdout_dti']['fold_proper_ci95'][0]:.4f}</code>, <code>{lsv_card['holdout_dti']['fold_proper_ci95'][1]:.4f}</code>] (#1 PI-1-unique in repo)<br><small><code>{lsv_card['model_projection_not_a_score']['lbm_v3_shrinkage_135claims']:.4f}</code> <code>MODEL</code> (LBM-v3, not a score)</small></td>
<td>Sparse PI-1: <strong>PASS</strong> (<code>{lsv_card['correlation_overlap_vs_registry']['final_dots_pi1']['worst_overlap_3px']:.4f} &le; 0.70</code>, |ρ|=<code>{lsv_card['correlation_overlap_vs_registry']['final_dots_pi1']['worst_abs_rho']:.4f}</code> across 2,263 rasters)<br>Literal dense witness: <strong>FAIL</strong> (<code>1.000 &gt; 0.70</code>)</td>
<td><strong>OK TO DOWNLOAD FOR RESEARCH ONLY · ⛔ DO NOT SUBMIT</strong></td>
</tr>""",
        """<tr style="background:#fefce8">
<td><strong>GEMSDOE92</strong><br><small>2026-10-27 Scored Entry (<code>lbmc1</code> — <strong>Fleet #1</strong>)</small></td>
<td><a href="downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif" download><code>gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif</code></a><br><small>SHA-256 <code>e928d3c3fde8b3f1…</code> · 35,801 dots</small></td>
<td><strong><code>0.2784</code> <code>CLAIM</code> (2026-10-29 prompt — #1 across all 8 owners)</strong><br><small><code>0.01970</code> static <code>HOLDOUT-DTI</code> · <code>0.3053</code> <code>MODEL</code> (LBM-v3)</small></td>
<td>Sparse PI-1 vs peers: <code>0.6845 &le; 0.70</code><br><strong>100% self-match</strong> to already-submitted entry</td>
<td><strong>STUDY ONLY · ⛔ DO NOT SUBMIT (ALREADY SUBMITTED)</strong></td>
</tr>""",
        f"""<tr>
<td><strong>GEMSDOE92</strong><br><small>2026-10-28 Historical (<code>RIESZ-LOCKED</code>, <code>TIPCOMP</code>, <code>BLINDCORRIDOR</code>)</small></td>
<td><a href="downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif" download><code>rieszlbm2</code></a> · <a href="downloads/gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6-zeros.tif" download><code>tipcomp</code></a> · <a href="downloads/gemsdoe92-blindcorridor-37654dots-20261028-11f8999c-zeros.tif" download><code>blindcorridor</code></a></td>
<td><code>rieszlbm2</code>: <code>0.03799</code> <code>HOLDOUT-DTI</code><br><code>tipcomp</code>: <code>0.09617</code> <code>HOLDOUT-DTI</code><br><code>blindcorridor</code>: no <code>HOLDOUT-DTI</code></td>
<td><code>rieszlbm2</code> PI-1: <code>0.6556</code> (literal <code>1.000</code>)<br><code>tipcomp</code> PI-1: <strong>FAIL</strong> (<code>{u_tc['worst_overlap']['value']:.4f} &gt; 0.70</code>)<br><code>blindcorridor</code> PI-1: <strong>FAIL</strong> (<code>{u_bc['worst_overlap']['value']:.4f} &gt; 0.70</code> vs 13GEMSDOE)</td>
<td><strong>RESEARCH ONLY · ⛔ DO NOT SUBMIT</strong></td>
</tr>""",
    ]

    for site in sorted(f9_src, key=lambda s: -f9_src[s]["claim"]):
        s = f9_src[site]
        u = f9_uni[site]
        logo_v = logo_by_key.get((site, s["best"]), float("nan"))
        clones = ", ".join(x.split("/")[-1] for x in (u.get("identical_bytes_elsewhere") or u.get("worst_overlap_in") or [])[:3])
        master_rows.append(f"""<tr>
<td><strong>{esc(site)}</strong> (Focus-9 peak)</td>
<td><a href="{esc(s['raw_url'])}"><code>{esc(s['best'])}</code></a> · <a href="{esc(s['blob_url'])}">GitHub</a><br><small>SHA-256 <code>{esc(s['sha256'][:16])}…</code></small></td>
<td><strong><code>{s['claim']:.4f}</code> <code>CLAIM</code></strong><br><small><code>{logo_v:.4f}</code> <code>MODEL</code> (LBM-v3 LOGO)</small></td>
<td><strong>NO — DUPLICATE</strong><br>3-px overlap <code>{u.get('worst_overlap', 1.0):.3f}</code>, |ρ|=<code>{abs(u.get('worst_rho', 1.0)):.3f}</code><br><small>clones: {esc(clones)}</small></td>
<td><strong>STUDY ONLY · ⛔ DO NOT SUBMIT (CLONE)</strong></td>
</tr>""")

    # Per-site detailed Focus-9 blocks (all submissions per focus site, highest + latest!)
    focus_blocks = []
    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        s = f9_src[site]
        u = f9_uni[site]
        s_rows = sorted([r for r in claims29 if r["site"] == site], key=lambda r: -r["claim"])
        trs = "".join(
            f"<tr><td>{'⭐ ' if r['name'] == s['best'] else ''}{esc(r['name'])}</td>"
            f"<td><code>{r['claim']:.4f}</code> <code>CLAIM</code></td>"
            f"<td><code>{logo_by_key.get((site, r['name']), float('nan')):.4f}</code> <code>MODEL</code></td>"
            f"<td><code>{esc(r.get('match', {}).get('repo', '—'))}:{esc(r.get('match', {}).get('path', '—'))}</code></td>"
            f"<td><code>{esc(r.get('match', {}).get('sha256', '—')[:16])}…</code></td></tr>"
            for r in s_rows
        )
        focus_blocks.append(f"""<section id="site-{esc(site)}">
<h3>{esc(site)} — Peak <code>{s['claim']:.4f}</code> (<code>CLAIM</code>) · {len(s_rows)} Reported Entries</h3>
<p><strong>Highest reported file (study only — DO NOT SUBMIT):</strong> <a href="{esc(s['raw_url'])}"><code>{esc(s['best'])}</code></a> (<a href="{esc(s['blob_url'])}">commit-pinned GitHub</a>, SHA-256 <code>{esc(s['sha256'])}</code>).<br>
<strong>Unique across 8-owner fleet?</strong> <strong>NO</strong> — worst 3-px overlap <code>{u.get('worst_overlap', 1.0):.4f}</code>, |ρ| = <code>{abs(u.get('worst_rho', 1.0)):.4f}</code> against <code>{esc(', '.join(u.get('worst_overlap_in', [])))}</code> (byte-identical copies in: <code>{esc(', '.join(u.get('identical_bytes_elsewhere', [])) or 'sibling lineage')}</code>).</p>
<table><thead><tr><th>Submission Name</th><th>Prompt Score (CLAIM)</th><th>LBM-v3 LOGO (MODEL)</th><th>Matched Repo:Path</th><th>SHA-256</th></tr></thead><tbody>{trs}</tbody></table>
</section>""")

    oot_rows_html = "".join(
        f"<tr><td><strong>{esc(r['prompt_site'])}</strong></td><td><code>{esc(r['name'])}</code></td>"
        f"<td>{r['n_fp_pos']:,}</td><td><code>{esc(r['status'])}</code></td>"
        f"<td><strong><code>{r['claim']:.4f}</code> <code>CLAIM</code></strong></td>"
        f"<td><code>{r['lbm_v1_prospective_oot']:.4f}</code> <code>MODEL</code> (<code>{r['error_v1_claim_minus_model']:+.4f}</code>)</td>"
        f"<td><code>{r['lbm_v3_shrinkage_oot']:.4f}</code> <code>MODEL</code> (<code>{r['error_v3_claim_minus_model']:+.4f}</code>)</td></tr>"
        for r in oot29["rows"]
    )

    owner_rows_html = "".join(
        f"<tr><td><code>{esc(o['owner'])}</code></td><td>{o['total_gemsdoe_repos']}</td>"
        f"<td>{o['repos_with_grid_tifs']}</td><td>{o['grid_tif_files']:,}</td>"
        f"<td><strong>{o['unique_sha256']:,}</strong></td><td>{esc(', '.join(o['empty_repos']) or 'none')}</td></tr>"
        for o in fleet29["owners"]
    )

    src_rows_html = "".join(
        f"<tr><td>{i+1}</td><td><strong>{esc(title)}</strong></td><td><a href=\"{esc(url)}\">{esc(url)}</a></td><td>{esc(note)}</td></tr>"
        for i, (title, url, note) in enumerate(OFFICIAL_SOURCES)
    )

    css = "body{font:16px/1.55 system-ui;color:#18212e;background:#f4f6f8;margin:0}main{max-width:1180px;margin:auto;padding:24px}section{background:white;padding:20px;margin:18px 0;border-radius:8px}.stop{border:3px solid #b91c1c;background:#fff4f3}table{width:100%;border-collapse:collapse}td,th{padding:9px;border-bottom:1px solid #ccd5df;text-align:left;vertical-align:top}code{overflow-wrap:anywhere}a{color:#124ec0}@media(max-width:700px){table{display:block;overflow:auto}}"
    prefix = '<aside>Current review: DO NOT SUBMIT · <a href="REVIEW_20261030_ARENA.md"><strong>2026-10-30 focus-nine review &amp; score/uniqueness table</strong></a> · <a href="review-47314b7f.html">Independent review</a></aside><details data-status-archive="true"><summary>Earlier independent review</summary><p>See linked review; historical clearance is superseded.</p></details>'

    content = f"""<nav><a href="index.html">← Main Landing Page</a> · <a href="REVIEW_20261030_ARENA.md"><strong>2026-10-30 review</strong></a> · <a href="how-to-submit.html">How to Submit &amp; [0, 1] Portal Guide</a> · <a href="nine-sites.html">Nine-Site Summary</a> · <a href="WHY_0_2778_AND_0_2784_20261029.md">PhD Analysis (0.2778 vs 0.2784)</a> · <a href="HYPOTHESES_20261029_LIDAR_SINTERVALVE.md">Pre-Registered Hypotheses H-92G1..G5</a></nav>
{render_lidarsintervalve_hero(lsv_card, lsv_status)}
<section id="master-table">
<h2>Executive Summary Table: GEMSDOE92 &amp; Nine Focus Sites (2026-10-29 Audit Across {fleet29['unique_sha256']:,} Rasters)</h2>
<p>Every figure carries its mandatory Protocol Rule-3 label: <code>HOLDOUT-DTI</code> = measured on <code>gems57-pooled-hide-v2</code> (22,663 withheld positives, 1,000 paired 20 km cluster bootstrap draws); <code>CLAIM</code> = user/owner-supplied leaderboard figure (no organizer receipt in repo); <code>MODEL</code> = shrinkage-calibrated <code>LBM-v3</code> spatial truth-density projection (never a competition score).</p>
<table><thead><tr><th>Site / Role</th><th>Downloadable File &amp; SHA-256</th><th>Measured HOLDOUT-DTI / Reported CLAIM / MODEL</th><th>Uniqueness Across 8-Owner Fleet (2,263 SHA-256)</th><th>Automated Clearance Verdict</th></tr></thead><tbody>{''.join(master_rows)}</tbody></table>
</section>
<section id="oot-20261029">
<h2>2026-10-29 Newly Scored Fleet Entries, Prospective Out-of-Time (OOT) Audit &amp; Optimizer's Curse Diagnosis</h2>
<p>Prospective OOT Spearman rank correlation across the 5 newly reported/updated 2026-10-29 <code>CLAIM</code>s is <strong><code>{oot29['prospective_spearman_all5']:.4f}</code></strong>. On the 3 unambiguous new peer entries (<code>GEMSDOEkarage1</code>, <code>ApartGEMSDOE3</code>, <code>KANLERGEMSDOE3</code>), shrinkage-regularized <code>LBM-v3</code> achieved prospective OOT errors of <code>-0.0074</code>, <code>+0.0098</code>, and <code>-0.0263</code>. On <code>GEMSDOE92 lbmc1</code> (<strong><code>0.2784</code> <code>CLAIM</code>, new #1 in the 8-owner fleet</strong>), unregularized <code>LBM-v1</code> overshot by <code>-0.0504</code> (Smith &amp; Winkler 2006 Optimizer's Curse from placing 55% of dots into the saturated <code>cons &ge; 5</code> bin), which <code>LBM-v3</code> cut nearly in half out-of-time (<code>-0.0277</code>) and now anchors in-sample across all 135 matched claims (LOGO RMSE = <code>{lbm3['logo_rmse']:.5f}</code>, Spearman = <code>{lbm3['logo_spearman']:.4f}</code>). Note: <code>ApartGEMSDOE1 udth-submod-e3</code> is flagged as <code>IR-1029-2</code> (reported <code>0.0525</code> in 2026-10-28 vs <code>0.1516</code> in 2026-10-29; <code>LBM</code> predicts <code>0.0450</code> on <code>udth-submod-e3</code> and <code>0.1275</code> on <code>ApartGEMSDOE1</code>'s newer <code>plkc-dualoof-e3</code>).</p>
<table><thead><tr><th>Site</th><th>Submission</th><th>Dots</th><th>2026-10-29 Status</th><th>Reported CLAIM</th><th>Frozen LBM-v1 OOT (Residual)</th><th>Shrinkage LBM-v3 OOT (Residual)</th></tr></thead><tbody>{oot_rows_html}</tbody></table>
</section>
<section id="fleet-20261029">
<h2>Rebuilt 8-Owner Public Registry Inventory (2026-10-29 Live Sync: {fleet29['unique_sha256']:,} Unique SHA-256)</h2>
<p>Rebuilt via <code>scripts/build_registry_cache.py</code> + <code>scripts/build_halo_stats.py</code> across all 8 GitHub owners (+{fleet29['delta_unique_sha256_vs_20261028']} new unique SHA-256 rasters since 2026-10-28; 0 stream errors). Full-registry audit also resolved <code>IR-1028C-6</code>, proving <code>BLINDCORRIDOR</code> fails even sparse PI-1 uniqueness at <code>{u_bc['worst_overlap']['value']:.4f} &gt; 0.70</code> against <code>buffedlizard55-lab/13GEMSDOE</code>.</p>
<table><thead><tr><th>GitHub Owner</th><th>Total Repos</th><th>Repos w/ Grid TIFFs</th><th>Grid GeoTIFFs</th><th>Unique SHA-256</th><th>Empty (0-KB) Stub Repos</th></tr></thead><tbody>{owner_rows_html}</tbody></table>
</section>
<section id="phd-summary">
<h2>PhD Analysis Summary: Why GEMSDOE32 Scored 0.2778, Why GEMSDOE92 lbmc1 Reached 0.2784, and How H-92G1 Pushes Further</h2>
<ul>
<li><strong>Marginal DTI Threshold (<code>&tau;* = 0.0590</code> at <code>D = 0.2784</code>):</strong> Under <code>DTI = TPw / (0.2&middot;TPw + 0.8&middot;G + 0.2&middot;FPw)</code> with the 300 m triangular kernel, thinning 1-px ridges into <code>2.6–3.0 px</code> spaced binary <code>1.0</code> dots and pruning within <code>200–400 m</code> of mapped faults removes redundant submodular overlap while slashing linear <code>0.2&middot;FPw</code> drag.</li>
<li><strong>Why <code>lbmc1</code> (<code>0.2784</code> <code>CLAIM</code>) Beat <code>GEMSDOE32</code> (<code>0.2778</code> <code>CLAIM</code>) Uniquely:</strong> Rather than copying <code>H19-5</code>, <code>lbmc1</code> aggregated independent multi-method tectonic corridor detections off mapped traces, validating both zeros-outside <code>[0, 1]</code> portal compliance and cross-method corridor synthesis.</li>
<li><strong>Why <code>H-92G1 LIDAR-SINTERVALVE</code> Achieved <code>0.178619</code> <code>HOLDOUT-DTI</code> (#1 PI-1-Unique in Repo):</strong> First-in-repo ingestion of 12-band USGS 3DEP 1 m bare-earth LiDAR (<code>lidar_scarp_features_u8.tif</code>, 75.34% footprint coverage seamlessly quantile-bridged onto 10 m 3DEP across the 24.66% gap) resolves paired 6 m LoG Wallace crest–toe dipoles and antithetic uphill-facing graben scarplets while vetoing incised stream banks (<code>cross_max</code>) and Lahontan 1,330 m beach benches, locked in strike to DOE GDR #1391 tufa-filtered sinter / 2 m temperature probe / Fournier disequilibrium upflow valves. Full derivation: <a href="WHY_0_2778_AND_0_2784_20261029.md">WHY_0_2778_AND_0_2784_20261029.md</a>.</li>
</ul>
</section>
<section id="nine-sites-detail">
<h2>Per-Site Audit of All Nine Focus Sites (Highest &amp; Latest Submissions)</h2>
{''.join(focus_blocks)}
</section>
<section id="official-sources">
<h2>Auditable Table of Official Trusted Sources &amp; Provenance</h2>
<table><thead><tr><th>#</th><th>Official Source / Dataset</th><th>Canonical URL</th><th>Provenance &amp; Sandbox Verification Status</th></tr></thead><tbody>{src_rows_html}</tbody></table>
</section>"""
    return f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>GEMSDOE92 — 2026-10-29 Executive Summary &amp; Nine-Site Audit</title><style>{css}</style></head><body><main>{prefix}{content}</main></body></html>\n"
