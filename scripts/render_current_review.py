#!/usr/bin/env python3
"""Render the authoritative first-screen status from the current review evidence.

This renderer does not choose or promote a competition submission. It verifies
that the review card, exact TIFF bytes, format audit, and literal-stop evidence
agree, then makes the research download and its DO-NOT-SUBMIT status unambiguous
on the README and three public entry pages.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CARD_PATH = ROOT / "evidence" / "review_2e1a649e_run_card.json"
PRE_PATH = ROOT / "evidence" / "review_2e1a649e_preflight.json"
WITNESS_PATH = ROOT / "evidence" / "review_2e1a649e_drainage_witness.json"
BEGIN = "<!-- CURRENT-REVIEW-2E1A649E:BEGIN -->"
END = "<!-- CURRENT-REVIEW-2E1A649E:END -->"
README_BEGIN = "<!-- CURRENT-REVIEW-2E1A649E-README:BEGIN -->"
README_END = "<!-- CURRENT-REVIEW-2E1A649E-README:END -->"


def load_object(path: Path) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return doc


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_or_insert(text: str, block: str, begin: str, end: str, anchor: str) -> str:
    if text.count(begin) != text.count(end):
        raise ValueError(f"unbalanced renderer markers {begin} / {end}")
    if begin in text:
        if text.count(begin) != 1:
            raise ValueError(f"expected at most one {begin} block")
        before, rest = text.split(begin, 1)
        _, after = rest.split(end, 1)
        return before + block + after
    if text.count(anchor) != 1:
        raise ValueError(f"expected one insertion anchor {anchor!r}")
    return text.replace(anchor, anchor + "\n" + block, 1)


def html_block(card: dict, pre: dict, witness: dict, *, primary: bool) -> str:
    rel = card["file"].removeprefix("docs/")
    name = html.escape(card["submission_name"])
    note = html.escape(card["note"])
    sha = html.escape(card["raster_sha256"])
    primary_attr = ' data-primary="true"' if primary else ""
    dti = card["holdout_dti"]
    ci = dti["ci95"]
    return f"""{BEGIN}
<aside id="current-review-2e1a649e" class="banner banner-warn" aria-label="Current verified decision" style="border:4px solid #7f1d1d; margin:1rem; padding:1rem;">
  <h1>Current verified decision — research download only</h1>
  <p><strong>✅ OK TO DOWNLOAD FOR RESEARCH: YES.</strong> The exact GeoTIFF passes automated format/range/grid checks without human inspection.</p>
  <p><strong>⛔ OK TO SUBMIT / SPEND A WEEKLY SLOT: NO.</strong> <strong>DUPLICATE UNDER THE LITERAL REGISTRY RULE</strong>: the pinned full-footprint witness forces 3-pixel forward overlap <code>{pre['forward_overlap_for_any_nonempty_in_footprint_dot_set']:.1f} &gt; {pre['threshold']:.2f}</code> for every nonempty candidate. The existing artifact also has exact-file overlap <code>{witness['forward_overlap_candidate_dots_within_3px_of_witness']:.1f}</code>. Verdict <code>negative</code>; <code>submission_eligible: false</code>; weekly slots used: <code>0</code>.</p>
  <p><a class="btn" href="{html.escape(rel)}"{primary_attr} download><strong>⬇ Current research download: {html.escape(Path(rel).name)} — DO NOT SUBMIT</strong></a> · <a href="downloads/gemsdoe92-drainageknick-20261025T120000Z-zeros.zip" download>one-TIFF ZIP</a> · <a href="downloads/gemsdoe92-drainageknick-20261025T120000Z-audit.json">format audit</a> · <a href="downloads/review_2e1a649e_run_card.json">current JSON run card</a> · <a href="downloads/current_status.json">machine status</a> · <a href="REVIEW_2E1A649E.md">three-pass review</a></p>
  <p>SHA-256 <code>{sha}</code>. Carried-forward <strong>HOLDOUT-DTI</strong> (<code>{html.escape(dti['evaluator_version'])}</code>, <code>{dti['withheld_positives']:,}</code> withheld positives, 95% CI): <code>{dti['dti']:.6f} [{ci[0]:.6f}, {ci[1]:.6f}]</code>, below the recorded comparable promotion bar <code>{dti['promotion_bar']:.6f}</code>. This was not rerun in this review and is not an organizer score.</p>
  <p>Record-only name: <code>{name}</code>. Note (<code>{card['note_chars']}/140</code>): <code>{note}</code>.</p>
  <p><strong>No new TIFF was generated in this review.</strong> The mandatory pre-placement stop fired before feature construction; generating a nonempty file afterward would violate Rule 1. The linked DRAINAGE-KNICK file was independently generated in prior PR #78, not copied here. Format validity does not override scientific/registry ineligibility.</p>
</aside>
{END}"""


def readme_block(card: dict, pre: dict) -> str:
    dti = card["holdout_dti"]
    ci = dti["ci95"]
    return f"""{README_BEGIN}
> ## Current verified decision — 2026-10-25 review `2e1a649e`
> **✅ OK TO DOWNLOAD FOR RESEARCH: YES** · **⛔ OK TO SUBMIT / USE A WEEKLY SLOT: NO** (`verdict: negative`, `submission_eligible: false`). The binding pre-placement `REGISTRY-MEASUREMENT` is universal: a SHA-256/Git-blob-pinned registry raster is positive on all `{pre['footprint_pixels']:,}` footprint cells, so every nonempty candidate has literal 3-pixel forward overlap `{pre['forward_overlap_for_any_nonempty_in_footprint_dot_set']:.1f} > {pre['threshold']:.2f}`. The protocol says stop; no new TIFF or experiment was generated in this review.
>
> **Current research download:** [DRAINAGE-KNICK GeoTIFF]({card['file']}) (**DO NOT SUBMIT**) · [one-TIFF ZIP](docs/downloads/gemsdoe92-drainageknick-20261025T120000Z-zeros.zip) · [format audit](docs/downloads/gemsdoe92-drainageknick-20261025T120000Z-audit.json) · [current run card](docs/downloads/review_2e1a649e_run_card.json) · [machine status](docs/downloads/current_status.json) · [three-pass review](docs/REVIEW_2E1A649E.md) · [ranked conditional hypotheses](docs/HYPOTHESES_20261025_REVIEW2E1A.md).
>
> Exact SHA-256 `{card['raster_sha256']}`. The linked file was generated independently in prior PR #78, not copied or renamed in this review. Carried-forward **HOLDOUT-DTI** (`{dti['evaluator_version']}`, `{dti['withheld_positives']:,}` withheld positives, 95% CI) `{dti['dti']:.6f} [{ci[0]:.6f}, {ci[1]:.6f}]` is below the `{dti['promotion_bar']:.6f}` comparable promotion bar and is **not** an organizer score.
{README_END}"""


def root_landing(card: dict, pre: dict) -> str:
    rel = card["file"]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="0; url=docs/index.html">
  <title>GEMSDOE92 — current verified research download (submission blocked)</title>
  <link rel="canonical" href="https://buffedlizard55-lab.github.io/GEMSDOE92/docs/index.html">
</head>
<body>
  <h1>GEMSDOE92 current verified decision</h1>
  <p><strong>✅ OK TO DOWNLOAD FOR RESEARCH: YES.</strong></p>
  <p><strong>⛔ OK TO SUBMIT / USE A WEEKLY SLOT: NO — DO NOT SUBMIT.</strong> The literal registry rule forces overlap <code>{pre['forward_overlap_for_any_nonempty_in_footprint_dot_set']:.1f} &gt; {pre['threshold']:.2f}</code> for every nonempty candidate; verdict <code>negative</code>, <code>submission_eligible: false</code>.</p>
  <p><a href="{html.escape(rel)}" download>Current DRAINAGE-KNICK research GeoTIFF — DO NOT SUBMIT</a> · <a href="docs/index.html">Open the audited workbench</a> · <a href="docs/REVIEW_2E1A649E.md">Read the three-pass review</a></p>
  <p>No new TIFF was generated in review <code>2e1a649e</code>; the mandatory pre-placement gate stopped before experiment 1.</p>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="fail if committed first-screen blocks differ from evidence")
    args = parser.parse_args(argv)
    card = load_object(CARD_PATH)
    pre = load_object(PRE_PATH)
    witness = load_object(WITNESS_PATH)
    if card.get("verdict") != "negative" or card.get("submission_eligible") is not False:
        raise ValueError("current review must preserve the negative literal-stop verdict")
    if pre.get("universal_nonempty_in_footprint_overlap_stop") is not True:
        raise ValueError("pre-placement evidence does not establish the recorded stop")
    if witness.get("stop_required_vs_this_witness") is not True:
        raise ValueError("exact-file witness evidence does not record a stop")
    tif = ROOT / card["file"]
    if digest(tif) != card["raster_sha256"] or digest(tif) != witness["candidate"]["sha256"]:
        raise ValueError("current TIFF bytes disagree with review evidence")

    stale: list[str] = []
    landing = ROOT / "index.html"
    landing_original = landing.read_text(encoding="utf-8")
    landing_rendered = root_landing(card, pre)
    if args.check:
        if landing_rendered != landing_original:
            stale.append(str(landing.relative_to(ROOT)))
    else:
        landing.write_text(landing_rendered, encoding="utf-8")

    for page_name in ("index.html", "executive-summary.html", "SUBMIT.html"):
        path = DOCS / page_name
        original = path.read_text(encoding="utf-8")
        # The machine-readable primary means current research artifact, not slot approval.
        # Remove stale markers before writing exactly one on the canonical index.
        rendered = original.replace(' data-primary="true"', "")
        block = html_block(card, pre, witness, primary=page_name == "index.html")
        rendered = replace_or_insert(rendered, block, BEGIN, END, "<body>")
        if args.check:
            if rendered != original:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(rendered, encoding="utf-8")

    readme = ROOT / "README.md"
    original = readme.read_text(encoding="utf-8")
    block = readme_block(card, pre)
    rendered = replace_or_insert(original, block, README_BEGIN, README_END,
                                 "# GEMSDOE92 — DOE GEMS Prize #306 Auditable Submission Workbench")
    if args.check:
        if rendered != original:
            stale.append(str(readme.relative_to(ROOT)))
    else:
        readme.write_text(rendered, encoding="utf-8")
    if stale:
        parser.error("stale current-review rendering: " + ", ".join(stale))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
