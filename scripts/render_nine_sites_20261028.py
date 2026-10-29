#!/usr/bin/env python3
"""Render the historical focus-nine executive page; never grant upload clearance.

The row-safe pairwise receipt supersedes the earlier pairwise matrix. Neither it
nor this page establishes global uniqueness, leaderboard score, or provenance.
"""
from __future__ import annotations

import html
import json
import math
import re
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/executive-summary-nine-sites-20261028.html"
SITES = tuple(f"GEMSDOE{x}" for x in (24, 25, 27, 28, 30, 31, 32, 33, 36))


def render() -> str:
    sources = json.loads((ROOT / "evidence/focus9_sources_20261028.json").read_text())
    receipt = json.loads((ROOT / "docs/downloads/focus9_pairwise_recheck_14f85876.json").read_text())
    if set(sources) != set(SITES) or set(receipt["sites"]) != set(SITES):
        raise ValueError("focus-site inventory is incomplete")
    comparisons = receipt["comparisons"]
    expected_pairs = {frozenset(p) for p in combinations(SITES, 2)}
    seen = set()
    maxima = {site: 0.0 for site in SITES}
    for item in comparisons:
        a, b = item["site_a"], item["site_b"]
        pair = frozenset((a, b))
        if pair not in expected_pairs or pair in seen:
            raise ValueError("invalid or repeated focus-site comparison")
        seen.add(pair)
        ab = float(item["forward_3px_overlap_a_to_b"])
        ba = float(item["forward_3px_overlap_b_to_a"])
        rho = float(item["spearman_binary_support_phi"])
        if not all(math.isfinite(x) for x in (ab, ba, rho)) or not (0 <= ab <= 1 and 0 <= ba <= 1 and abs(rho) <= 1):
            raise ValueError("invalid overlap or correlation")
        maxima[a] = max(maxima[a], ab)
        maxima[b] = max(maxima[b], ba)
    if seen != expected_pairs:
        raise ValueError("focus-site comparisons are incomplete")
    rows = []
    for site in SITES:
        r = sources[site]
        # Uniqueness is directional: never borrow the reverse overlap to declare failure.
        status = "FAIL (overlap > 0.70)" if maxima[site] > 0.70 else "Not established"
        claim = float(r["claim"])
        commit, rel = r["commit"], r["path"]
        if (not math.isfinite(claim) or not 0 <= claim <= 1
                or not re.fullmatch(r"[0-9a-f]{40}", commit)
                or not re.fullmatch(r"docs/downloads/[A-Za-z0-9_.-]+\.tif", rel)):
            raise ValueError("invalid focus-site claim or pinned file")
        listed = r["all"]
        if (not listed or any(not math.isfinite(float(value)) or not 0 <= float(value) <= 1 for _, value in listed)
                or claim != max(float(value) for _, value in listed)
                or not any(name == r["best"] and float(value) == claim for name, value in listed)):
            raise ValueError("focus-site peak does not match supplied inventory")
        url = f"https://github.com/buffedlizard55-lab/{site}/blob/{commit}/{rel}"
        if r["blob_url"] != url:
            raise ValueError("focus-site link does not match pinned repository and path")
        path = html.escape(url, quote=True)
        name = html.escape(Path(rel).name)
        rows.append(f'<tr><th scope="row">{site}</th><td><a href="{path}">{name}</a><br><small>Historical research only</small></td>'
                    f'<td>{claim:.4f} <small>user-reported, unverified</small></td>'
                    f'<td>Not available</td><td>{status}; max directional overlap {maxima[site]:.3f}</td><td>DO NOT SUBMIT</td></tr>')
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nine-site executive summary — GEMSDOE92</title><style>
body{font:16px/1.5 system-ui,sans-serif;color:#18212e;background:#f4f6f8;margin:0}main{max-width:1180px;margin:auto;padding:24px}
section{background:white;padding:20px;margin:18px 0;border-radius:8px}.stop{border:3px solid #b91c1c;background:#fff4f3}
table{width:100%;border-collapse:collapse}td,th{padding:8px;border-bottom:1px solid #ccd5df;text-align:left;vertical-align:top}
a{color:#124ec0}small{color:#4b5767}@media(max-width:800px){table{display:block;overflow:auto}}
</style></head><body><main>
<nav><a href="index.html">Home</a> · <a href="how-to-submit.html">How to submit after clearance</a> · <a href="WHY_0_2778.md">GEMSDOE32 analysis</a></nav>
<h1>Executive summary: nine focus sites</h1>
<section class="stop"><h2>DO NOT SUBMIT — no cleared new TIFF</h2>
<p>No validated leaderboard estimate or eligible unique submission is available. No weekly slot has been selected in this review. Format validation is not scientific validation or organizer acceptance.</p>
<p><a href="downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif" download>Download RIESZ TIFF for research only — DO NOT SUBMIT</a>. Its stored run card fails the literal registry stop and the holdout comparison; an older sparse-only overlap is not clearance.</p></section>
<section><h2>Historical per-site comparison</h2>
<p>The entries below are the highest values supplied for each site in the pinned inventory, not verified organizer receipts or current leaderboard scores. The prior score model is not a validated predictor, so no numerical estimates are shown. Links are pinned owner-repository files, not official organizer downloads.</p>
<table><thead><tr><th>Site</th><th>Historical file</th><th>User-reported value</th><th>Estimated leaderboard score</th><th>Uniqueness against other focus sites</th><th>Submission status</th></tr></thead><tbody>''' + "\n".join(rows) + '''</tbody></table>
<p>Directional overlap is the fraction of row-site positive cells within 3 pixels of another focus site's positive cells. These are historical measurements, not a new scan. See the <a href="downloads/focus9_pairwise_recheck_14f85876.json">row-safe receipt</a>; it superseded the earlier pairwise matrix. This nine-site comparison is rejection-only and cannot establish uniqueness against the full registry.</p></section>
<section><h2>Why the GEMSDOE32 result may be strong</h2>
<p>Its user-reported 0.2778 is the highest among the nine supplied values. Sparse thinning and a mapped-fault collar could reduce redundant or unscored prediction mass under a distance-tolerant metric. This is a hypothesis, not proof of the reported score, fault discovery, or a causal improvement; hidden labels and a receipt are unavailable. See the <a href="WHY_0_2778.md">bounded evidence review</a>.</p>
<p>Historical HOLDOUT-DTI (<code>gems57-pooled-hide-v2</code>, 22,663 withheld positives): RIESZ 0.037987, 95% CI [0.031011, 0.044656]; R0 recipe 0.097750, 95% CI [0.085900, 0.110766]. These are stored results, not rerun here or leaderboard scores. <a href="downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json">Run card</a>.</p></section>
<section class="stop"><h2>Remaining blockers</h2><p>The specified single-method lane is missing; the full feature cache and complete registry are not available here. A dense probability-surface witness triggers the literal overlap stop for any nonempty in-footprint candidate; an alternative interpretation has not been authorized. The portal, competition data hosts, rules and live leaderboard cannot be reached from this environment. Do not spend a slot until the protocol gates and a separate selector pass.</p>
<p><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Official problem</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution">Official reference solution</a> · <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Rules PDF</a> · <a href="REVIEW_20261028_SESSION.md">Registry interpretation and limitations</a></p></section>
<p><small>Generated from the pinned 2026-10-28 inventory and row-safe receipt; not a live feed.</small></p></main></body></html>
'''


def main() -> None:
    OUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
