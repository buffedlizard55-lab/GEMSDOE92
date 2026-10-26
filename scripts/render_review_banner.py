#!/usr/bin/env python3
"""Place the latest negative review above archived historical site reports."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "<!-- REVIEW-14F85876:BEGIN -->"
END = "<!-- REVIEW-14F85876:END -->"
VARIO_END = "<!-- VARIO-STATUS:END -->"
ARCHIVE = '<details id="historical-research-archive"><summary>Historical experiments and downloads — not current clearance</summary>'
ROOT_CLOSE = "<!-- REVIEW-14F85876:ROOT-ARCHIVE-END -->"
PAGES = ("index.html", "docs/index.html", "docs/executive-summary.html", "docs/SUBMIT.html")


def banner(prefix: str) -> str:
    return f'''{BEGIN}
<section aria-label="Latest independent evidence review" style="max-width:70rem;margin:1rem auto;padding:1rem 1.2rem;border:3px solid #991b1b;border-radius:10px;background:#fff7ed;font:1rem/1.55 system-ui,sans-serif">
<h2>26 October review — no submission eligible</h2>
<p><strong>⛔ DO NOT SUBMIT.</strong> The pinned public witness is positive on all 5,167,373 finite template cells: every nonempty candidate has literal overlap 1.000 &gt; 0.70. No new TIFF, experiment, holdout result or slot was generated in this review.</p>
<p>GEMSDOE32's 0.2778 is an owner <strong>CLAIM</strong>, not an organizer receipt; no defensible leaderboard estimate is available for the research files. The prior claim-trained model's row-wise error is not a per-file uncertainty interval. An independent 2-D recheck corrected overlap values in 35 of 36 site pairs; all duplicate decisions are unchanged.</p>
<p><a href="{prefix}focus9.html"><strong>Nine-site executive summary, research downloads and conditional submission guide</strong></a> · <a href="{prefix}downloads/review_14f85876_run_card.json">review run card</a> · <a href="{prefix}downloads/score_estimator_audit_14f85876.json">model audit</a> · <a href="{prefix}HYPOTHESES_20261026_SITE_REVIEW.md">ranked hypotheses</a></p>
<p data-official-leaderboard>Official public #1: 0.4437; observed 2026-10-26 UTC. Snapshot only; not a project receipt.</p>
<p><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">Official leaderboard</a>; automated refresh may be delayed or unavailable. <a href="{prefix}downloads/live_leaderboard.json">Feed and timestamp</a>.</p>
<script src="{prefix}leaderboard-feed.js" defer></script>
</section>
{END}'''


SALEM = '''<section aria-label="SALEMSEISMO 2026-10-26" style="border:3px solid #991b1b;background:#fff7ed;padding:1rem;margin:1rem;border-radius:8px">
<h2>Historical SALEMSEISMO — research only</h2>
<p><strong>DO NOT SUBMIT.</strong> Its literal registry overlap is 1.000; a sparse or matched-budget diagnostic is not clearance. Its historical runner scanned after placement and checked rank correlations only for selected witnesses. A prior fast halo could wrap at row edges. Static re-scores are not necessarily leakage-free.</p>
<p><a href="downloads/h33-h33-2-b2-SALEMSEISMOcelftail52k-20261026-cc3c8ff2-zeros.tif" download>Download historical SALEMSEISMO research TIFF</a> · <a href="downloads/salemseismo_run_card.json">historical run card</a> · <a href="focus9.html">corrected nine-site review</a> · <a href="downloads/review_14f85876_run_card.json">independent correction</a>.</p>
<p>Historical siblings, research only: <a href="downloads/h33-h33-2-b2-SALEMSEISMOpoint37k-20261026-fe2567c1-zeros.tif">point37k</a> · <a href="downloads/h33-h33-2-b2-SALEMSEISMOcelf37k-20261026-3c4f585f-zeros.tif">celf37k</a>.</p>
<p>No defensible leaderboard estimate or calibrated individual prediction interval is available. The research runner is disabled.</p>
</section>'''


def render_page(text: str, *, root_page: bool) -> str:
    if text.count(VARIO_END) != 1:
        raise ValueError("missing or duplicate authoritative status marker")
    if text.count(BEGIN) != text.count(END) or text.count(BEGIN) > 1:
        raise ValueError("malformed review banner markers")
    if BEGIN in text:
        start = text.index(BEGIN)
        end = text.index(END, start) + len(END)
        text = text[:start] + text[end:].lstrip("\n")
    if not root_page:
        text, count = re.subn(r'<section aria-label="SALEMSEISMO 2026-10-26".*?</section>',
                              SALEM, text, count=1, flags=re.S)
        # The guide has no SALEMSEISMO section.
        if count > 1:
            raise ValueError("duplicate historical SALEM section")
    if text.count(ARCHIVE) > 1:
        raise ValueError("duplicate historical archive")
    if ARCHIVE in text:
        text = text.replace(ARCHIVE, "", 1)
    elif not root_page:
        raise ValueError("historical archive missing")
    else:
        if ROOT_CLOSE in text:
            raise ValueError("root archive closing marker without opening")
        if text.count("</body>") != 1:
            raise ValueError("root page has unexpected body tags")
        text = text.replace("</body>", f"</details>\n{ROOT_CLOSE}\n</body>", 1)
    block = banner("docs/" if root_page else "")
    head, tail = text.split(VARIO_END, 1)
    return head + VARIO_END + "\n" + block + "\n" + ARCHIVE + "\n" + tail.lstrip("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        review = json.loads((ROOT / "docs/downloads/review_14f85876_run_card.json").read_text())
        if (review.get("verdict") != "negative" or review.get("submission_eligible") is not False
                or review.get("new_unique_tiff_generated") is not False):
            raise ValueError("review does not support a rejection-only banner")
        stale = []
        for rel in PAGES:
            path = ROOT / rel
            old = path.read_text(encoding="utf-8")
            new = render_page(old, root_page=rel == "index.html")
            if old != new:
                if args.check:
                    stale.append(rel)
                else:
                    path.write_text(new, encoding="utf-8")
        if stale:
            print("stale review banner: " + ", ".join(stale), file=sys.stderr)
            return 1
        print("review banners: OK" if args.check else "rendered review banners")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"review banners failed closed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
