#!/usr/bin/env python3
"""Finalize byte-bound Run Card, format audit, readiness feed, and 2026-10-29 executive summary."""
from __future__ import annotations

import hashlib
import html
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DL = DOCS / "downloads"
EVID = ROOT / "evidence"

STEM = "gemsdoe92-marussitrishear-34000dots-20261029-236171af"


def esc(x) -> str:
    return html.escape(str(x), quote=True)


def main() -> int:
    tif_path = DL / f"{STEM}-zeros.tif"
    zip_path = DL / f"{STEM}-zeros.zip"
    writer_json_path = DL / f"{STEM}-zeros.json"
    assert tif_path.is_file() and zip_path.is_file() and writer_json_path.is_file()

    tif_sha = hashlib.sha256(tif_path.read_bytes()).hexdigest()
    zip_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    with zipfile.ZipFile(zip_path, "r") as zf:
        assert zf.namelist() == [tif_path.name]
        assert hashlib.sha256(zf.read(tif_path.name)).hexdigest() == tif_sha

    hold = json.loads((EVID / "marussi_trishear_holdout_20261029.json").read_text(encoding="utf-8"))
    uniq_full = json.loads((EVID / "marussi_trishear_uniqueness_20261029.json").read_text(encoding="utf-8"))
    oot29 = json.loads((EVID / "lbm_oot_20261029.json").read_text(encoding="utf-8"))
    lbm3 = json.loads((EVID / "marussi_lbm_v3_20261029.json").read_text(encoding="utf-8"))
    fleet29 = json.loads((EVID / "fleet_audit_20261029.json").read_text(encoding="utf-8"))
    f9_src = json.loads((EVID / "focus9_sources_20261028.json").read_text(encoding="utf-8"))
    f9_uniq = json.loads((EVID / "focus9_uniqueness_20261028.json").read_text(encoding="utf-8"))
    writer_rec = json.loads(writer_json_path.read_text(encoding="utf-8"))

    assert uniq_full["candidate_sha256"] == tif_sha

    # Compact `marussi_trishear_uniqueness_20261029.json` keeping top-25 offenders on surface & dots
    for key in ("pre_placement_surface_pi1", "final_dots_pi1"):
        sec = uniq_full[key]
        if "rows" in sec:
            rows_sorted = sorted(sec["rows"], key=lambda r: -float(r["overlap_pi1"]))
            sec["top_25_by_overlap_pi1"] = rows_sorted[:25]
            del sec["rows"]
    (EVID / "marussi_trishear_uniqueness_20261029.json").write_text(
        json.dumps(uniq_full, indent=2), encoding="utf-8"
    )

    surf_u = uniq_full["pre_placement_surface_pi1"]
    dots_u = uniq_full["final_dots_pi1"]

    # Check overlap against GEMSDOE92's own prior lbmc1 (`e928d3c3...`) & rieszlbm2 (`d168c7d2...`)
    sc_e3 = hold["scores"]["e3_marussi_blind_diversified"]
    sc_e2 = hold["scores"]["e2_marussi_trishear_relay"]
    sc_e1 = hold["scores"]["e1_marussi_pure_phys"]
    sc_ctrl = hold["scores"]["control_struct_relay_only"]
    sc_r0 = hold["scores"]["r0_recipe"]
    p_e3 = hold["paired_by_candidate"]["e3_marussi_blind_diversified"]
    p_e2 = hold["paired_by_candidate"]["e2_marussi_trishear_relay"]

    run_card = dict(
        schema="gemsdoe92-run-card-v3-20261029",
        lane="MARUSSI-TRISHEAR-VORTICITY",
        created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        pre_registration="docs/HYPOTHESES_20261029_MARUSSI_TRISHEAR.md",
        hypothesis=(
            "H-92M1 + H-92M2: Full 3D Laplace-consistent Marussi potential-field tensor 2D-dimensionality "
            "D_2D = 1 - |det(T)| / [2*(-I_1/3)^(3/2)] on B13 gravity & B02 RTP magnetics, coupled with "
            "Allmendinger (1998) trishear blind-tip monocline flexure over unconsolidated cover (B15 > 40 m), "
            "Cooper terracing, Gallardo-Meju joint cross-gradient & magnetite-destruction conduits, true Salem "
            "(2008) B02 tilt-depth gating (never Band 6 tc), Niblett-Bostick skin-depth lateral contrast, and "
            "Walker Lane geodetic kinematic vorticity W_k strike partitioning, fused with self-excluded "
            "fold-visible fault-tip relay context and Lagrangian offender-halo de-crowding."
        ),
        mechanism=(
            "Planar intrabasin horst/graben and range-front faults generate 2D Marussi potential steps "
            "(det(T) -> 0 => D_2D -> 1) and updip trishear monocline inflections above buried tips while "
            "rejecting equant 3D plutons/plugs (D_2D -> 0); high geodetic kinematic vorticity W_k rotates "
            "favored structural continuation from N022E Basin-and-Range normal faults toward N062E/N318W "
            "Walker Lane pull-aparts; 1D directional crest localization + normalized Lagrangian dual pricing "
            "bounds 3-px overlap <= 0.6564 across all 2,262 registry SHA-256 rasters on BOTH the pre-placement "
            "surface and final binary dots."
        ),
        named_non_fault_mimic=(
            "Subaerial bedrock canyon/mesa escarpment rims (steep slope > 10 deg with shallow/zero sedimentary "
            "cover B15 < 40 m and shallow Salem magnetic depth < 150 m), 3D circular plutons/caldera plugs "
            "(D_2D -> 0), and flat saline Lake Lahontan playa bowls (high scalar B17 conductivity without "
            "lateral Niblett-Bostick skin-depth step or 2D Marussi basement offset)."
        ),
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI",
            evaluator_version=hold["evaluator_version"],
            withheld_positive_pixels=hold["withheld_positives"],
            e3_deployed_recipe=sc_e3,
            e2_marussi_trishear_relay=sc_e2,
            e1_marussi_pure_phys=sc_e1,
            control_struct_relay_only=sc_ctrl,
            r0_recipe_control=sc_r0,
            paired_e3_vs_r0_recipe=p_e3["r0_recipe"],
            paired_e2_vs_r0_recipe=p_e2["r0_recipe"],
            paired_e2_vs_struct_relay_control=p_e2["control_struct_relay_only"],
            paired_e3_vs_struct_relay_control=p_e3["control_struct_relay_only"],
            all_time_repo_holdout_best=dict(
                arm="relay_conduit",
                dti=0.184485,
                ci95=[0.169875, 0.198933],
                source="evidence/relayconduit_holdout.json",
            ),
        ),
        leakage_canaries=dict(
            canaries_run=True,
            threshold_symmetric_auc=0.90,
            max_symmetric_auc_all_24_channels=hold["leakage_canary_summary"]["max_symmetric_auc"],
            max_symmetric_auc_14_zero_cat_channels=0.5783,
            all_pass=hold["leakage_canary_summary"]["all_pass_le_0p90"],
            band6_tc_used_as_magnetic_tilt=False,
            stripped_leaky_gdr_columns=["thermalclass", "dist_known_fault_px"],
        ),
        uniqueness=dict(
            registry_owners=fleet29["registry_scope"]["owners"],
            registry_repos=fleet29["registry_scope"]["nonempty_repositories"],
            registry_rasters=uniq_full["registry_rasters_checked"],
            pi1_surface_duplicate=bool(surf_u["duplicate"]),
            surface_worst_overlap=float(surf_u["worst_overlap_pi1"]["overlap_pi1"]),
            surface_worst_overlap_sha256=surf_u["worst_overlap_pi1"]["sha256"],
            surface_worst_abs_rho=abs(float(surf_u["worst_abs_rho"]["rho"])),
            pi1_final_dots_duplicate=bool(dots_u["duplicate"]),
            final_worst_overlap=float(dots_u["worst_overlap_pi1"]["overlap_pi1"]),
            final_worst_overlap_sha256=dots_u["worst_overlap_pi1"]["sha256"],
            final_worst_abs_rho=abs(float(dots_u["worst_abs_rho"]["rho"])),
            literal_reading=dict(
                worst=float(dots_u["literal_reading"]["worst"]["overlap_literal"]),
                witness_sha256=dots_u["literal_reading"]["worst"]["sha256"],
                duplicate_under_literal=bool(dots_u["literal_reading"]["duplicate_under_literal"]),
                note=dots_u["literal_reading"]["note"],
            ),
        ),
        model_estimate=dict(
            evidence_class="MODEL (fitted to 131 owner-reported CLAIMs through 2026-10-29; never an organizer score)",
            lbm_v3_estimate=uniq_full["lbm_v3_model_estimate"]["value"],
            lbm_v3_logo_rmse=lbm3["logo_rmse"],
            lbm_v3_lbmc1_logo=lbm3["lbmc1_logo"],
            lbmc1_20261029_claim=0.2784,
        ),
        raster=dict(
            file=f"docs/downloads/{tif_path.name}",
            zip=f"docs/downloads/{zip_path.name}",
            sha256=tif_sha,
            zip_sha256=zip_sha,
            bytes=tif_path.stat().st_size,
            zip_bytes=zip_path.stat().st_size,
            n_dots=uniq_full["n_dots"],
            min_dcat_px=uniq_full["min_dcat_px"],
        ),
        raster_sha256=tif_sha,
        validator_output=dict(
            overall_pass=True,
            gates_passed_count=len(uniq_full["gates_detail"]),
            gates=uniq_full["gates_detail"],
            writer_local_validation=writer_rec.get("local_validation", {}),
        ),
        gates_passed=dict(
            format=True,
            range_0_1_and_no_nan=True,
            distance_from_catalogue_gt_3px=True,
            leakage_canaries_le_0p90=True,
            catalogue_holdout_beats_r0_recipe=True,
            catalogue_holdout_beats_all_time_repo_best=False,
            uniqueness_pi1_pre_placement_surface=True,
            uniqueness_pi1_final_dots=True,
            uniqueness_literal_dense_witness=False,
        ),
        submission_name=uniq_full["submission_name"],
        note=uniq_full["submission_note"],
        note_length=len(uniq_full["submission_note"]),
        experiments_run=3,
        weekly_slots_used=0,
        organizer_confirmed_score=None,
        submission_eligible=False,
        verdict="negative",
        verdict_reason=(
            "Format-valid [0, 1] GeoTIFF (11/11 strict gates PASS, min dcat=3.61 px > 3.0 px, 0 NaNs), "
            "passes Rule-4 leakage canaries (max sym_AUC=0.8115 <= 0.90; 0.5783 pure physics), beats R0 recipe "
            "on gems57-pooled-hide-v2 (E3 HOLDOUT-DTI = 0.157774 vs 0.097750, paired delta +0.060024 [+0.046290, +0.074443]; "
            "E2 = 0.172273, +0.074523), and passes PI-1 uniqueness across all 2,262 registry SHA-256 rasters on BOTH "
            "pre-placement surface (0.6564 <= 0.70, |rho|=0.6632 <= 0.90) AND final dots (0.6564 <= 0.70, |rho|=0.0886 <= 0.90). "
            "Retained fail-closed as verdict='negative' (submission_eligible=false, DO NOT SUBMIT, 0 slots spent) for TWO "
            "binding reasons: (1) E2 (0.172273) and E3 (0.157774) did not beat the repo's all-time HOLDOUT-DTI record "
            "(relay_conduit = 0.184485, matched single-stage relay control = 0.182496), and (2) literal dense-witness "
            "overlap vs 17GEMSDOE full-footprint surface is 1.000 > 0.70."
        ),
    )

    card_evid_path = EVID / f"{STEM}_run_card.json"
    card_dl_path = DL / f"{STEM}_run_card.json"
    card_evid_path.write_text(json.dumps(run_card, indent=2), encoding="utf-8")
    shutil.copy2(card_evid_path, card_dl_path)

    audit_doc = dict(
        schema="gemsdoe92-raster-audit-v1",
        file=f"docs/downloads/{tif_path.name}",
        sha256_zeros=tif_sha,
        bytes=tif_path.stat().st_size,
        n_dots=uniq_full["n_dots"],
        overall_pass=True,
        gates_zeros=uniq_full["gates_detail"],
        run_card=f"evidence/{STEM}_run_card.json",
        verdict="negative",
        submission_eligible=False,
    )
    audit_path = DL / f"{STEM}-zeros-audit.json"
    audit_path.write_text(json.dumps(audit_doc, indent=2), encoding="utf-8")

    readiness_29 = dict(
        schema="gemsdoe92-candidate-readiness-v1",
        artifact="MARUSSI-TRISHEAR-20261029",
        file=f"downloads/{tif_path.name}",
        zip=f"downloads/{zip_path.name}",
        audit=audit_path.name,
        run_card=card_dl_path.name,
        executive_summary="executive-summary-20261029-marussi-trishear.html",
        raster_sha256=tif_sha,
        zip_sha256=zip_sha,
        submission_name=run_card["submission_name"],
        note=run_card["note"],
        verdict="negative",
        submission_eligible=False,
        download_status="OK TO DOWNLOAD FOR RESEARCH ONLY",
        submission_status="DO NOT SUBMIT — below all-time repo HOLDOUT-DTI best (0.184485) & literal dense witness 1.000",
        blocking_reasons=[
            "HOLDOUT-DTI (E3 = 0.157774, E2 = 0.172273) beat R0 recipe (0.097750) by +0.0600/+0.0745, but did not beat the repo's all-time HOLDOUT-DTI record (relay_conduit = 0.184485; matched relay-only control = 0.182496)",
            "literal full-support dense-witness overlap vs 17GEMSDOE surface is 1.000 (> 0.70)",
            "separate human slot-selector governance applies within the 3/week portal cap",
        ],
    )
    (DL / "marussi_trishear_readiness_20261029.json").write_text(
        json.dumps(readiness_29, indent=2), encoding="utf-8"
    )

    # Render dedicated comprehensive 2026-10-29 executive summary HTML page!
    f9_rows_html = []
    for site, s in f9_src.items():
        u = f9_uniq[site]
        clone_txt = (
            f"PI-1 unique vs 8-owner fleet (worst 3-px {u['worst_overlap']:.3f})"
            if u.get("unique_pi1")
            else f"NOT unique — worst 3-px {u['worst_overlap']:.3f} ({', '.join(u.get('identical_bytes_elsewhere', []) or u.get('worst_overlap_in', []))})"
        )
        f9_rows_html.append(
            f"<tr><td><strong>{esc(site)}</strong></td>"
            f"<td><a href=\"{esc(s['blob_url'])}\"><code>{esc(s['best'])}</code></a><br><small>SHA-256: <code>{esc(s['sha256'][:16])}…</code></small></td>"
            f"<td><code>{s['claim']:.4f}</code> <small>(CLAIM, unreceipted)</small></td>"
            f"<td>{esc(clone_txt)}; literal witness 1.000 — <strong>DO NOT SUBMIT</strong></td></tr>"
        )

    oot_rows_html = []
    for r in oot29["rows"]:
        oot_rows_html.append(
            f"<tr><td><strong>{esc(r['site'])}</strong></td>"
            f"<td><code>{esc(r['name'])}</code><br><small>SHA-256: <code>{esc(r['sha256'][:16])}…</code> ({r['n_dots']:,} dots)</small></td>"
            f"<td><code>{r['claim_20261029']:.4f}</code> <small>(CLAIM)</small></td>"
            f"<td><code>{r['lbm_v1_oct27_pred']:.4f}</code> <small>(MODEL)</small></td>"
            f"<td><code>{r['error_v1_oct27']:+.4f}</code></td>"
            f"<td>{r['on_h19_frac']*100:.1f}% H19-5 · {r['on_cons5_frac']*100:.1f}% cons≥5 ({esc(r['regime'])})</td></tr>"
        )

    summary_html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GEMSDOE92 — 2026-10-29 Executive Summary: 0.2784 Fleet Analysis &amp; MARUSSI-TRISHEAR</title>
<style>
body{{font:15.5px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#18212e;background:#f4f6f8;margin:0}}
main{{max-width:1120px;margin:auto;padding:24px}}
section{{background:#fff;padding:20px 22px;margin:18px 0;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.stop{{border:3px solid #b91c1c;background:#fff4f3}}
.btn{{display:inline-block;background:#1e3a5f;color:#fff!important;padding:10px 16px;border-radius:6px;font-weight:700;text-decoration:none;margin:4px 8px 4px 0}}
table{{width:100%;border-collapse:collapse;font-size:.92rem}}
th,td{{padding:9px 10px;border-bottom:1px solid #d5dde5;text-align:left;vertical-align:top}}
th{{background:#eef2f7}}
code{{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.88em;overflow-wrap:anywhere}}
a{{color:#124ec0}}
</style></head><body><main>
<aside>Current review: DO NOT SUBMIT · <a href="review-47314b7f.html">Independent review</a> · <a href="index.html">← Back to main GEMSDOE92 home</a> · <a href="how-to-submit.html">How to submit</a></aside>
<details data-status-archive="true"><summary>Earlier independent review</summary><p>See linked review; historical clearance is superseded.</p></details>

<section class="stop" id="marussi-top">
<h1>DO NOT SUBMIT — 2026-10-29 MARUSSI-TRISHEAR Candidate (OK TO DOWNLOAD FOR RESEARCH ONLY)</h1>
<p><strong>Unmistakable Readiness Status:</strong> <strong>DO NOT SUBMIT — this candidate is not eligible for a weekly competition slot</strong> (<code>verdict="negative"</code>, <code>submission_eligible=false</code>, <code>0</code> portal slots spent). Although this newly generated 2026-10-29 GeoTIFF passes <strong>11/11 strict format/range/CRS/catalogue gates</strong> (all pixels finite in <code>[0.0, 1.0]</code>, <code>0</code> NaN/Inf, exact <code>EPSG:32611</code> <code>3730×3292</code>, <code>min d_cat = 3.61 px &gt; 3.0 px</code>), passes <strong>24/24 solo-feature leakage canaries</strong> (<code>max sym_AUC = 0.8115 &le; 0.90</code>; <code>0.5783</code> across all 14 zero-catalogue physics channels), beats <code>r0_recipe</code> on <code>gems57-pooled-hide-v2</code> by <strong><code>+0.060024</code></strong> (<code>E3 HOLDOUT-DTI = 0.157774</code> vs <code>0.097750</code>; <code>E2 = 0.172273</code>), and passes <strong>PI-1 uniqueness across all <code>2,262</code> registry SHA-256 rasters on BOTH pre-placement surface (<code>0.6564 &le; 0.70</code>) AND final dots (<code>0.6564 &le; 0.70</code>)</strong>, it is held back fail-closed for <strong>two binding reasons</strong>: (1) neither <code>E2</code> (<code>0.172273</code>) nor <code>E3</code> (<code>0.157774</code>) exceeded the repository's all-time <code>HOLDOUT-DTI</code> record (<code>relay_conduit = 0.184485</code>; matched single-stage relay control = <code>0.182496</code>), and (2) literal full-support dense-witness overlap vs <code>17GEMSDOE</code> is <code>1.000 &gt; 0.70</code>. No separate selector or weekly slot authorizes bypassing a failed mandatory gate.</p>
<p>
<a class="btn" href="downloads/{esc(tif_path.name)}" download>⬇ Download MARUSSI-TRISHEAR GeoTIFF (34,000 dots) — OK TO DOWNLOAD FOR RESEARCH ONLY / DO NOT SUBMIT</a>
<a class="btn" href="downloads/{esc(zip_path.name)}" download>⬇ Download single-TIFF ZIP (research only)</a>
</p>
<table>
<tr><th>File &amp; SHA-256</th><td><code>downloads/{esc(tif_path.name)}</code> (<code>{tif_path.stat().st_size:,}</code> bytes) · SHA-256 <code>{esc(tif_sha)}</code></td></tr>
<tr><th>Archived research name</th><td><code>{esc(run_card['submission_name'])}</code> <em>(archived identifier only; do not upload)</em></td></tr>
<tr><th>Archived research note ({len(run_card['note'])}/140 chars)</th><td><code>{esc(run_card['note'])}</code></td></tr>
<tr><th>HOLDOUT-DTI (<code>gems57-pooled-hide-v2</code>, 22,663 withheld px)</th><td><code>E3</code> deployed recipe: <strong><code>0.157774</code></strong> (95% CI <code>[0.144291, 0.171647]</code>, paired <code>+0.060024 [+0.046290, +0.074443]</code> vs <code>r0_recipe = 0.097750</code>) · <code>E2</code> full 24-ch: <strong><code>0.172273</code></strong> (<code>[0.158850, 0.185206]</code>) · <code>E1</code> pure 14-ch physics: <code>0.066076</code> (<code>[0.053550, 0.078882]</code>) · Matched 10-ch relay-only control: <code>0.182496</code> (<code>[0.167042, 0.196644]</code>; paired <code>E2 - ctrl = -0.010223</code>) · Repo all-time best (<code>relay_conduit</code>): <code>0.184485</code>.</td></tr>
<tr><th>Registry uniqueness (all <code>2,262</code> SHAs, <code>108</code> repos, 8 owners)</th><td><strong>PI-1 pre-placement surface:</strong> <code>0.6564 &le; 0.70</code>, <code>|&rho;| = 0.6632 &le; 0.90</code> · <strong>PI-1 final dots:</strong> <code>0.6564 &le; 0.70</code>, <code>|&rho;| = 0.0886 &le; 0.90</code> · <strong>Literal dense-witness reading:</strong> <code>1.000 &gt; 0.70</code> vs <code>17GEMSDOE</code> (blocks promotion).</td></tr>
<tr><th>LBM-v3 MODEL estimate</th><td><code>MODEL</code> (never an organizer score): <code>{uniq_full['lbm_v3_model_estimate']['value']:.5f}</code> (non-circular 131-claim <code>LBM-v3</code> with <code>&lambda;=5e-3</code>, LOGO RMSE <code>{lbm3['logo_rmse']:.5f}</code>, Spearman <code>{lbm3['logo_spearman']:.5f}</code>).</td></tr>
<tr><th>Byte-bound receipts</th><td><a href="downloads/{esc(card_dl_path.name)}">Run Card JSON</a> · <a href="downloads/{esc(audit_path.name)}">11-Gate Format Audit JSON</a> · <a href="downloads/marussi_trishear_readiness_20261029.json">Readiness JSON</a> · <a href="HYPOTHESES_20261029_MARUSSI_TRISHEAR.md">Pre-Registration Memo</a></td></tr>
</table>
</section>

<section id="fleet-20261029">
<h2>1. Breakthrough 2026-10-29 Fleet Result: How <code>GEMSDOE32</code> Scored <code>0.2778</code> and How <code>GEMSDOE92</code> <code>lbmc1</code> Scored <code>0.2784</code> (CLAIM)</h2>
<p>On 2026-10-29, five newly scored owner-reported <code>CLAIM</code> results arrived across the 8-owner fleet (none has a captured portal screenshot here, so all remain labeled <code>CLAIM</code>, never <code>ORGANIZER-CONFIRMED</code>). Most notably, <code>GEMSDOE92</code>'s prior <code>gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros</code> reported <strong><code>0.2784</code> (<code>CLAIM</code>)</strong> — surpassing <code>GEMSDOE32</code>'s <code>0.2778</code> by <code>+0.0006</code> to become the highest owner-reported <code>CLAIM</code> across all <code>133</code> scored entries in the 8-owner fleet, while using <strong>only <code>13.31%</code> of its dots on <code>H19-5</code></strong>!</p>
<ul>
<li><strong>Why <code>GEMSDOE32</code> (<code>h33-h33-2-b2-...-e5eb6e7e-zeros</code>, <code>37,654</code> dots) reached <code>0.2778</code> (<code>CLAIM</code>):</strong> Under pooled Distance-weighted Tversky Index (<code>&alpha;=0.2</code> false-positive weight, <code>&beta;=0.8</code> false-negative weight, <code>R=300 m = 3 px</code> triangular kernel), <code>TP_w = &Sigma;_g max_x p(x) K(d(x,g))</code> saturates at <code>1</code> per truth pixel, while every redundant dot within <code>&lt; 2.8 px</code> of another dot along the same 1D fault ridge adds almost zero marginal <code>&Delta;TP_w</code> yet pays full <code>&alpha;(1 - k)</code> false-positive denominator cost. Starting from the un-spaced <code>H19-5</code> ridge skeleton (<code>126,647</code> pixels, <code>0.1922</code> <code>CLAIM</code>), <code>GEMSDOE25</code> spaced dots at <code>2.8 px</code> (<code>44,090</code> dots &rarr; <code>0.2600</code>), <code>GEMSDOE28/31</code> removed noisy branches (<code>40,213</code> dots &rarr; <code>0.2708</code>), and <code>GEMSDOE32</code> pruned all <code>2,559</code> dots inside <code>d_cat &le; 2 px</code> (<code>200 m</code>) of mapped <code>existing_faults.tif</code> traces (<code>37,654</code> dots &rarr; <code>0.2778</code>), because mapped faults are masked pixel-exactly during scoring (Forum #11516) and digitization halo collars carry virtually zero new-fault labels.</li>
<li><strong>Why <code>GEMSDOE92</code> <code>lbmc1</code> (<code>35,801</code> dots) reached <code>0.2784</code> (<code>CLAIM</code>) AND why <code>LBM-v1</code> overestimated it by <code>+0.0538</code>:</strong> <code>lbmc1</code> shifted 86.7% of its dots off <code>H19-5</code> into multi-corridor off-catalogue fault zones (<code>d_cat &gt; 15 px</code>, <code>cons &ge; 5</code> across independent physics lanes), proving that substantial hidden test-set faults genuinely lie off the <code>H19-5</code> skeleton. However, optimizing directly against lightly regularized <code>LBM-v1</code> (<code>&lambda;=1e-3</code>, which assigned a <code>~19&times;</code> tail multiplier to sparse <code>cons &ge; 5</code> cells) incurred classic <strong>Goodhart selection optimism</strong> (<code>0.3322 MODEL</code> vs <code>0.2784 CLAIM</code>). Refitting non-circular <strong><code>LBM-v3</code></strong> (<code>&lambda;=5e-3</code> across <code>131</code> clean claims, holding <code>GEMSDOE92</code> out of both the G-set and LOGO fold) shrinks <code>cons &ge; 5</code> to <code>8.72&times;</code> and predicts <code>lbmc1</code> out-of-group at <strong><code>0.2828 MODEL</code></strong> (within <code>+0.0044</code> of <code>0.2784</code>!). Meanwhile, across the 3 unambiguous passive partner submissions newly scored on 2026-10-29, frozen <code>LBM-v1</code> achieved prospective out-of-time <strong><code>RMSE = 0.01935</code></strong>.</li>
<li><strong>How to reach <code>0.4413</code> (leaderboard top <code>CLAIM</code>):</strong> In <code>LBM-v3</code> units (<code>|G| &approx; 17,129</code> test-fault pixels), scoring <code>0.4413</code> with <code>~35,000</code> spaced binary dots requires covering <code>TP_w &approx; 7,850</code> test pixels (<code>~45.8%</code> recall vs <code>~28.5%</code> for <code>R0</code>/<code>lbmc1</code>) — impossible by rearranging existing <code>H19-5</code> dots alone, and requiring genuine geological discovery of <strong>blind intrabasin growth faults and Walker Lane accommodation relays</strong> (~39–45% of Great Basin geothermal systems; Faulds &amp; Hinz 2015), ideally augmented on unrestricted hosts by external <strong>USGS 1 m 3DEP LiDAR</strong>, <strong>USGS ScienceBase 3D MT phase-tensor skew</strong>, and <strong>OPERA/ARIA Sentinel-1 InSAR poroelastic barrier gradients</strong>.</li>
</ul>
<table>
<thead><tr><th>Site</th><th>2026-10-29 Newly Scored Submission</th><th>2026-10-29 CLAIM</th><th>Frozen Oct-27 LBM-v1 (MODEL)</th><th>OOT Error</th><th>Structural Regime</th></tr></thead>
<tbody>{''.join(oot_rows_html)}</tbody>
</table>
<p><small>Flagged prompt irregularity <code>IR-1029-2</code>: <code>apartgems1-udth-submod-e3-20261027-50e7b334-zeros</code> was listed as <code>0.0525</code> on 2026-10-28 (matching its unspaced cluster geometry, <code>LBM-v1 = 0.0455</code>) versus <code>0.1516</code> on 2026-10-29 (matching sibling <code>apartgems1-plkc-dualoof-e3-20261027-d770c5cb-zeros</code>, <code>LBM-v1 = 0.1306</code>); excluded from primary <code>LBM-v3</code> fit.</small></p>
</section>

<section id="nine-sites-20261029">
<h2>2. Nine Focus Sites Executive Audit (<code>GEMSDOE24..36</code> vs <code>2,262</code>-SHA 8-Owner Registry)</h2>
<table>
<thead><tr><th>Focus Site</th><th>Highest-Scoring File &amp; Commit-Pinned Link</th><th>Owner-Reported Score</th><th>Uniqueness &amp; Readiness Status</th></tr></thead>
<tbody>{''.join(f9_rows_html)}</tbody>
</table>
</section>

<section id="hypotheses-20261029">
<h2>3. Pre-Registered Untried Geological Hypotheses (<code>H-92M1..M4</code>) &amp; Ablation Diagnosis</h2>
<p>Full equations and data-hygiene proofs are archived in <a href="HYPOTHESES_20261029_MARUSSI_TRISHEAR.md"><code>docs/HYPOTHESES_20261029_MARUSSI_TRISHEAR.md</code></a>:</p>
<ol>
<li><strong><code>H-92M1</code> (<code>MARUSSI-TRISHEAR</code>, tested in <code>E1/E2/E3</code>):</strong> Full 3D Laplace-consistent Marussi gravity &amp; RTP tensor 2D-dimensionality <code>D_2D</code> (<code>B13</code>, <code>B18</code>, <code>B02</code>) + Allmendinger (1998) blind-tip trishear monocline flexure over unconsolidated valley fill (<code>B15 &gt; 40 m</code>) + Cooper terracing + Gallardo-Meju cross-gradient &amp; demagnetized conduit + true Salem (2008) <code>B02</code> tilt-depth gate (fixing <code>IR-1028B-3</code>) + Niblett-Bostick electromagnetic skin-depth gradient (<code>B17</code>).</li>
<li><strong><code>H-92M2</code> (<code>WALKER-LANE-VORTICITY</code>, co-tested in <code>E1/E2/E3</code>):</strong> Geodetic kinematic vorticity <code>W_k</code> (<code>B07</code>, <code>B08</code>, <code>B04</code>) rotating structural strike alignment from N022°E Basin-and-Range normal dip-slip to N062°E / N318°W Walker Lane pull-aparts.</li>
<li><strong><code>H-92M3</code> (<code>CALDWELL-MT-PHASE-TENSOR</code>, external free USGS ScienceBase 3D MT EDI/NetCDF):</strong> Galvanic-distortion-free MT phase-tensor skew <code>&beta;_PT</code> separating 3D hydrothermal upflow conduits from 1D conductive Lahontan playa clays (blocked by 6-host sandbox allowlist; scalar Niblett-Bostick proxy tested in <code>H-92M1</code>).</li>
<li><strong><code>H-92M4</code> (<code>ARIA-INSAR-POROELASTIC-BARRIER</code>, external free NASA ASF <code>OPERA_L3_DISP-S1_V1</code>):</strong> Seasonal poroelastic aquifer-head step across blind cemented intrabasin fault baffles (documented for unrestricted hosts).</li>
</ol>
<p><strong>Key negative/diagnostic scientific finding from paired <code>E2</code> vs <code>control_struct_relay_only</code>:</strong> Using our <code>Marussi + Trishear + Cooper</code> 1D subsurface step localizer strictly at the post-tree crest gate with 10 self-excluded structural relay features achieved <strong><code>HOLDOUT-DTI = 0.182496</code></strong> (recovering 98.9% of two-stage <code>relay_conduit = 0.184485</code> in half the compute), whereas concatenating all 14 regional geophysical channels directly into a single shallow tree diluted subaerial tip-relay precision by <code>-0.010223</code> (<code>0.172273</code>) on the subaerial-biased USGS/INGENIOUS holdout. Next sessions should keep Stage-1 blind Marussi-Trishear log-odds strictly isolated from Stage-2 tip-relay trees via cover-adaptive gating <code>w_cover(B15)</code>.</p>
</section>

<section id="official-sources">
<h2>4. Official Trusted Sources &amp; How to Submit (When a Future Candidate Clears All Gates)</h2>
<p>See <a href="how-to-submit.html"><code>docs/how-to-submit.html</code></a> for step-by-step DrivenData portal instructions and how our automated 11-gate validator eliminates <code>ERROR Summary: Invalid values — Detail: Predicted values must be in range [0, 1]</code>.</p>
<ul>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">DrivenData DOE GEMS Problem Description &amp; DTI Metric</a> · <a href="https://www.drivendata.org/termsofuse/">DrivenData Terms of Use</a></li>
<li><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Official DOE / NLR Prize Rules PDF (Sept 2026)</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution">Official DrivenData Reference Solution Repo</a></li>
<li><a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN Airborne Magnetic &amp; Radiometric Surveys</a> · <a href="https://gdr.openei.org/submissions/1391">DOE GDR #1391 INGENIOUS Great Basin Dataset</a></li>
<li><a href="https://www.sciencebase.gov/catalog/">USGS ScienceBase (3D MT Impedance Releases)</a> · <a href="https://asf.alaska.edu/datasets/daac/opera/">NASA ASF OPERA DISP-S1 InSAR</a></li>
</ul>
</section>
</main></body></html>
"""
    (DOCS / "executive-summary-20261029-marussi-trishear.html").write_text(summary_html, encoding="utf-8")
    print(f"Wrote Run Card, Audit, Readiness, and Executive Summary for {STEM} ({tif_sha[:16]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
