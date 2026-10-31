#!/usr/bin/env python3
"""Render the dated Focus-9 claim/model/hash review from committed receipts.

All reported site scores remain CLAIMs and the LBM values remain MODEL
 diagnostics. The registry join is exact SHA-256/size identity only; it is not a
spatial-overlap, live leaderboard, or organizer-provenance audit.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVID = ROOT / "evidence"
OUTPUT = DOCS / "focus9-review-20261030.html"
EXPECTED_SITES = {
    "GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
    "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36",
}
OFFICIAL_LINKS = [
    ("DrivenData competition problem / scoring page", "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"),
    ("DrivenData public leaderboard", "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"),
    ("DOE / NLR rules PDF", "https://docs.nlr.gov/docs/fy26osti/96647.pdf"),
    ("USGS 3DEP", "https://www.usgs.gov/3d-elevation-program"),
    ("USGS GeoDAWN", "https://doi.org/10.5066/P93LGLVQ"),
    ("DOE GDR #1391 / INGENIOUS", "https://gdr.openei.org/submissions/1391"),
    ("USGS NWIS groundwater-level API documentation", "https://waterservices.usgs.gov/rest/gwlevels-service/"),
    ("NASA LP DAAC ASTER GED v3", "https://lpdaac.usgs.gov/products/ag100v003/"),
    ("USGS Landsat Collection 2 Level-2", "https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products"),
    ("USGS FDSN event service", "https://earthquake.usgs.gov/fdsnws/event/1/"),
    ("USGS ComCat documentation", "https://earthquake.usgs.gov/data/comcat/"),
]


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_page() -> str:
    sources = json.loads((EVID / "focus9_sources_20261028.json").read_text(encoding="utf-8"))
    report = json.loads((EVID / "focus9_registry_20261030.json").read_text(encoding="utf-8"))
    model = json.loads((EVID / "lbm_v3_model_20261029.json").read_text(encoding="utf-8"))
    if set(sources) != EXPECTED_SITES or report.get("summary", {}).get("sites_checked") != 9:
        raise ValueError("Focus-9 source set or registry receipt is incomplete")
    model_rows = {(row["site"], row["name"]): row for row in model["rows"]}
    audit_rows = {row["site"]: row for row in report["rows"]}
    if set(audit_rows) != EXPECTED_SITES:
        raise ValueError("Focus-9 exact-hash receipt does not contain all nine sites")

    table_rows = []
    for site in sorted(EXPECTED_SITES, key=lambda s: (-sources[s]["claim"], s)):
        src = sources[site]
        audit = audit_rows[site]
        model_row = model_rows.get((site, src["best"]))
        if model_row is None:
            raise ValueError(f"{site}: dated LBM-v3 LOGO diagnostic is missing")
        if (audit["sha256"] != src["sha256"] or audit["bytes"] != src["bytes"]
                or audit["claim"] != src["claim"] or audit["best_name"] != src["best"]
                or audit["pinned_source_found_at_exact_path"] is not True
                or audit["has_exact_copy_in_another_repository"] is not True):
            raise ValueError(f"{site}: exact-hash receipt disagrees with the pinned source")
        source_repo = audit["source_repository"]
        other_repos = sorted({
            f"{copy['owner']}/{copy['repo']}"
            for copy in audit["exact_copies_elsewhere"]
            if f"{copy['owner']}/{copy['repo']}" != source_repo
        })
        examples = ", ".join(other_repos[:3])
        table_rows.append(
            "<tr>"
            f"<td><strong>{_esc(site)}</strong></td>"
            f"<td><a href=\"{_esc(src['blob_url'])}\">{_esc(src['best'])}</a><br>"
            f"<span class=\"mono\">{_esc(src['sha256'])}</span><br>{src['bytes']:,} bytes; commit-pinned</td>"
            f"<td><strong>{src['claim']:.4f}</strong> <code>CLAIM</code><br>"
            f"{model_row['logo']:.6f} <code>MODEL</code> (LBM-v3 LOGO; not a score)</td>"
            f"<td><strong>NOT UNIQUE BY EXACT SHA</strong><br>{len(other_repos)} other repositories with exact-byte copies."
            f"<br><span class=\"small\">Examples: {_esc(examples)}</span></td>"
            "<td>Study only; do not re-submit this byte-identical artifact. No new local TIFF was generated.</td>"
            "</tr>"
        )

    snap = report["registry_snapshot"]
    summary = report["summary"]
    links = " · ".join(
        f'<a href="{_esc(url)}">{_esc(title)}</a>' for title, url in OFFICIAL_LINKS
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GEMSDOE92 — Focus-9 Review (2026-10-30)</title>
<style>
body{{font:16px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f4f6f8;color:#18212e}}
main{{max-width:1180px;margin:auto;padding:24px}}section{{background:#fff;padding:20px;margin:18px 0;border-radius:8px}}
.stop{{border:3px solid #b91c1c;background:#fff4f3}}.notice{{border-left:5px solid #b45309;background:#fff7ed;padding:12px}}
.badge{{display:inline-block;padding:4px 10px;border-radius:999px;background:#b91c1c;color:#fff;font-weight:700}}
table{{width:100%;border-collapse:collapse}}td,th{{padding:10px;border-bottom:1px solid #ccd5df;text-align:left;vertical-align:top}}th{{background:#eef2f7}}
code,.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.9em;overflow-wrap:anywhere}}.small{{font-size:.88rem;color:#52606d}}
a{{color:#124ec0}}
</style></head><body><main>
<nav><a href="index.html">Executive summary</a> · <a href="nine-sites.html">Nine-site review</a> · <a href="how-to-submit.html">Submission instructions</a> · <a href="REVIEW_20261030_REPOSITORY.md">Three-pass review</a></nav>
<section class="stop"><h1>Focus-9 review — 2026-10-30</h1>
<p><span class="badge">NO FOCUS-SITE FILE IS CLEARED TO SUBMIT</span></p>
<p>The nine pinned files below are owner-reported score claims and exact-byte registry matches. All nine have identical-byte copies in other public owner-maintained repositories. This is a uniqueness rejection, not a fresh spatial-overlap calculation and not an organizer score verification.</p>
<p><strong>Current project download status:</strong> <a href="downloads/gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e-zeros.tif">the existing LIDAR-SINTERVALVE GeoTIFF</a> is <strong>OK TO DOWNLOAD FOR RESEARCH ONLY</strong> and <strong>DO NOT SUBMIT</strong>. The 2026-10-30 review made no new TIFF and ran no experiment or holdout.</p>
<p><strong>Fresh registry snapshot:</strong> {snap['owner_count']} owners, {snap['repository_count']} repositories, {snap['grid_compatible_raster_records']:,} grid-compatible raster records, {snap['unique_sha256_count']:,} unique SHA-256 values, {snap['error_count']} errors. Built <code>{_esc(snap['built_utc'])}</code>; inventory SHA-256 <code>{_esc(snap['inventory_sha256'])}</code>. This is a public owner-mirror snapshot, not an organizer-authenticated registry.</p>
<p><strong>Exact-hash join:</strong> {summary['source_path_sha_size_matches']}/9 source path/SHA/size identities matched; {summary['sites_with_exact_copies_elsewhere']}/9 have exact copies in another repository. Receipt: <a href="downloads/focus9_registry_20261030.json"><code>focus9_registry_20261030.json</code></a>.</p>
</section>
<section><h2>All nine selected site artifacts</h2>
<table><thead><tr><th>Site</th><th>Commit-pinned file identity</th><th>Reported / modelled value</th><th>Fresh exact-byte result</th><th>Disposition</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table>
<p class="small">The <code>MODEL</code> column is a dated LBM-v3 LOGO diagnostic from <code>evidence/lbm_v3_model_20261029.json</code>. It is not a competition score, a submission estimate, or an organizer receipt.</p>
</section>
<section><h2>Why the GEMSDOE32 0.2778 figure is only a cautious comparison</h2>
<ul>
<li><code>0.2778</code> is associated with <code>GEMSDOE32 h33-h33-2-b2</code> in an owner-maintained project listing; this repository has no organizer submission receipt for that item. The pinned raster is a 37,654-dot binary artifact, SHA-256 <code>c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9</code>.</li>
<li>A plausible metric-based explanation is that a fixed sparse dot budget, spacing near the 300 m triangular-kernel radius, and pruning near the public catalogue can reduce redundant false-positive mass. The raster lineage is consistent with that explanation; it does not identify which choice caused the reported number or reveal hidden labels.</li>
<li>The supplied <code>0.3195</code> and <code>0.4413</code> figures have inconsistent historical context. An in-repository note records a 2026-10-25 public-board snapshot with <code>0.4413</code> for a non-GEMSDOE participant and states <code>0.3195</code> was not in that top-50 list; a separate 2026-10-26 sibling-cache note records xiaofanhu at 0.4437. This review did not fetch the live leaderboard, so none is a current verified score or receipt for GEMSDOE32/GEMSDOE92.</li>
<li>Local <code>HOLDOUT-DTI</code> measures spatially blocked recovery against the visible public catalogue. It is not numerically comparable to a competition leaderboard score and cannot establish performance on hidden test labels.</li>
</ul>
<p>Supporting analysis: <a href="WHY_0_2778_AND_0_2784_20261029.md">historical 0.2778 / 0.2784 analysis</a> and the dated <a href="REVIEW_20261030_REPOSITORY.md">2026-10-30 three-pass review</a>.</p>
</section>
<section><h2>Untried in this repository’s integrated implementation (not novel ideas)</h2>
<p>These hypotheses were previously documented in <code>docs/HYPOTHESES_20261028_9649DFC1.md</code>. No corresponding integrated implementation or experiment receipt was found in the inspected <code>gems/</code> modules. They are untested implementation candidates, not newly invented hypotheses. Because the assigned method paragraph is missing, none is selected as the current method lane and none was run.</p>
<ol>
<li><strong>NWIS hydraulic-head / seasonal phase-lag barrier.</strong> Compare pumping- and screen-depth-controlled groundwater-level response across nearby wells on opposite sides of a candidate concealed structure; seek a persistent cross-strike head or seasonal-lag discontinuity. Main confounders: pumping, irrigation, aquifer boundaries, sparse well coverage. <a href="https://waterservices.usgs.gov/rest/gwlevels-service/">USGS Water Services</a>.</li>
<li><strong>ASTER TIR + Landsat SWIR alteration seam.</strong> Test co-registered silica/clay alteration boundaries against lithology and land-cover controls; require continuity aligned with structural corridors rather than broad felsic or playa units. Main confounders: lithologic contacts, dunes, mine waste, sensor-registration error. <a href="https://lpdaac.usgs.gov/products/ag100v003/">NASA LP DAAC ASTER GED v3</a> · <a href="https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products">USGS Landsat Collection 2</a>.</li>
<li><strong>Event-specific ComCat focal-mechanism consensus × geodetic strain.</strong> Use mechanism-plane uncertainty and event quality to test whether local nodal planes align with geodetic strain and mapped independent lineaments; separate induced sequences and aftershocks. Main confounders: sparse focal mechanisms, multiple nodal planes, induced seismicity, and strong spatial sampling bias. <a href="https://earthquake.usgs.gov/fdsnws/event/1/">USGS FDSN event service</a> · <a href="https://earthquake.usgs.gov/data/comcat/">ComCat documentation</a>.</li>
<li><strong>Repeat-pass thermal persistence.</strong> Test whether seasonally normalized, multi-date land-surface-temperature residual lineaments persist along structures after elevation, aspect, land-cover, irrigation, and cloud-quality controls. Main confounders: transient surface flux, vegetation/soil moisture, emissivity and revisit gaps. <a href="https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products">Landsat Collection 2</a>.</li>
</ol>
<p>No expected numerical gain is asserted. These candidates are ranked only by directness to structures, data/coverage burden, and confounder risk; live data availability and terms were not checked.</p>
</section>
<section><h2>Official links for later manual review (not live-verified here)</h2><p>{links}</p>
<p class="notice"><strong>Source-check boundary:</strong> these URLs are retained for the owner’s later review. They were not fetched from official sites in this sandbox session; this page does not authenticate current rules, current leaderboard values, data rights, or source availability.</p></section>
</main></body></html>
"""


def main() -> int:
    OUTPUT.write_text(render_page(), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
