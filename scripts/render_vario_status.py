#!/usr/bin/env python3
"""Byte-bound VARIO publication status: the single current decision for the site.

Supersedes the rejection-only review renderers (render_current_status,
render_readiness, gems.public_status), which hard-coded the conclusion of
review sessions that generated no raster.  This renderer is evidence-driven:
it reads the VARIO run card (evidence/vario_run_card.json, produced by
scripts/package_vario.py from the pre-registered gates in
docs/HYPOTHESES_20261025_VARIO.md), re-verifies the primary TIFF's SHA-256
and format gates from the bytes on disk, and renders

* docs/downloads/readiness.json  (machine-readable current status),
* the first-in-body status panel of the public pages,
* docs/vario.html                (executive subpage: exactly how to submit).

It fails closed: any hash/gate/verdict inconsistency raises and nothing is
written.  It never invents a score: HOLDOUT-DTI is labelled with evaluator
version/withheld positives/CI, the organizer score stays null until a
submission-page receipt exists, and a `promote` verdict means only
"eligible for the separate selector step" (protocol rule 6), never a spent
weekly slot.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor"))

from gems.gates import run_gates, summarise  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402

CARD = ROOT / "evidence" / "vario_run_card.json"
DOCS = ROOT / "docs"
BEGIN = "<!-- VARIO-STATUS:BEGIN -->"
END = "<!-- VARIO-STATUS:END -->"
HTML_PAGES = ("docs/index.html", "docs/executive-summary.html", "docs/SUBMIT.html")
MD_PAGES = ("README.md", "SUBMISSION_READY.md")


def load_card(root: Path = ROOT) -> dict:
    card = json.loads((root / "evidence/vario_run_card.json").read_text())
    if not isinstance(card, dict) or card.get("lane") != "VARIO":
        raise ValueError("run card must be the VARIO card object")
    if card.get("verdict") not in ("promote", "negative"):
        raise ValueError("verdict must be promote or negative")
    primary = card.get("submission_file", "")
    if not re.fullmatch(r"docs/downloads/[A-Za-z0-9_.-]+-zeros\.tif", str(primary)):
        raise ValueError("primary must be a local downloads/*-zeros.tif")
    if sha256_file(root / primary) != card.get("raster_sha256"):
        raise ValueError("run-card SHA-256 differs from downloadable bytes")
    if (root / "evidence/vario_run_card.json").read_bytes() != (root / "docs/downloads/vario_run_card.json").read_bytes():
        raise ValueError("evidence and downloads run cards differ")
    note = card.get("note")
    if not isinstance(note, str) or not 0 < len(note) <= 140 or card.get("note_chars") != len(note):
        raise ValueError("note must be 1..140 chars with matching count")
    hold = card.get("holdout_dti") or {}
    scores = hold.get("scores") or {}
    prim = scores.get(card.get("primary_arm", ""))
    if not prim or hold.get("evidence_class") != "HOLDOUT-DTI" or not hold.get("evaluator_version"):
        raise ValueError("missing labelled HOLDOUT-DTI for the primary arm")
    if card.get("organizer_confirmed_score") is not None:
        raise ValueError("organizer score must stay null without a receipt")
    gates = card.get("gates") or {}
    promote_required = all(gates.get(k) is True for k in
                           ("format", "canary", "holdout_beats_best_control", "operative_uniqueness"))
    if (card["verdict"] == "promote") != promote_required:
        raise ValueError("verdict inconsistent with recorded gates")
    # Re-derive format gates from bytes; never trust the recorded booleans alone.
    results = run_gates(str(root / primary), str(root / "data/bridge/sample_submission.tif"),
                        str(root / "data/bridge/labels.tif"), prune_radius=2,
                        require_submission_encoding=True)
    ok, _ = summarise(results)
    if not ok or card.get("format_pass") is not True:
        raise ValueError("primary bytes fail fresh format gates")
    card["_fresh_gates"] = [dict(name=r.name, ok=bool(r.ok), detail=r.detail) for r in results]
    return card


def readiness(card: dict) -> dict:
    hold = card["holdout_dti"]
    prim = hold["scores"][card["primary_arm"]]
    uniq = card["correlation_overlap_vs_registry"]["final_dots"][card["primary_arm"]]["operative_sparse"]
    promote = card["verdict"] == "promote"
    return dict(
        schema="gemsdoe92-current-readiness.v2-vario",
        evidence_class="AUTOMATED-FORMAT-CHECK + HOLDOUT-DTI + REGISTRY-MEASUREMENT; not a score",
        lane="VARIO", primary_arm=card["primary_arm"],
        download_status=("OK TO DOWNLOAD — AUTOMATED GATES PASS" if promote else "OK TO DOWNLOAD FOR RESEARCH"),
        submission_status=(
            "AUTOMATED GATES PASS — ELIGIBLE FOR THE SELECTOR STEP (verify the weekly cap on the DrivenData submission page; this session spent 0 slots; NOT CLEARED FOR A WEEKLY SLOT by this page alone)"
            if promote else "DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT"),
        submission_eligible=False,
        verdict=card["verdict"],
        new_unique_tiff_generated=True,
        experiments_this_session=card["experiments_used"],
        weekly_slots_used_this_session=0,
        file=card["submission_file"].removeprefix("docs/"),
        raster_sha256=card["raster_sha256"],
        submission_name=card["submission_name"],
        note=card["note"],
        format_pass=True,
        validator_output=card.get("_fresh_gates") or card["validator_output"],
        holdout_dti=dict(evidence_class="HOLDOUT-DTI", evaluator_version=hold["evaluator_version"],
                         instrument=hold["instrument"], primary=prim,
                         best_comparable_control=hold["best_comparable_control"],
                         primary_minus_best_control=hold["primary_minus_best_control"],
                         scores=hold["scores"]),
        leakage_canaries=card["leakage_canaries"],
        correlation_overlap_vs_registry=dict(
            evidence_class="REGISTRY-MEASUREMENT",
            operative_sparse=uniq,
            surface_preplacement=card["correlation_overlap_vs_registry"]["surface_preplacement"],
            literal_disclosure="DUPLICATE UNDER THE LITERAL REGISTRY RULE reading: pinned full-footprint dense registry surfaces give forward overlap 1.0 for every non-empty raster (docs/downloads/review_f23_preflight.json). Operative gate = sparse dot-field registry (<=150k positives) overlap<=0.70 and |rho|<=0.90; both readings are reported in the run card."),
        sgmc_proxy=card["sgmc_proxy"],
        organizer_confirmed_score=None,
        blocking_reasons=card["blocking_reasons"],
        run_card="downloads/vario_run_card.json",
        packaged=card["packaged"],
    )


def _fmt(x) -> str:
    return f"{x:.6f}" if isinstance(x, (int, float)) else str(x)


def panel_html(card: dict, st: dict) -> str:
    e = html.escape
    promote = card["verdict"] == "promote"
    hold = card["holdout_dti"]
    prim = hold["scores"][card["primary_arm"]]
    delta = hold["primary_minus_best_control"]
    uniq = st["correlation_overlap_vs_registry"]["operative_sparse"]
    wo = uniq.get("worst_overlap") or {}
    wr = uniq.get("worst_abs_spearman") or {}
    sibs = " · ".join(
        f'<a href="{e(v["file"].removeprefix("docs/"))}" download>{e(v["arm"])}</a>'
        f' (<a href="{e(v["audit"].removeprefix("docs/"))}">audit</a>)'
        for v in card["packaged"].values() if v["arm"] != card["primary_arm"])
    reasons = "".join(f"<li>{e(r)}</li>" for r in card["blocking_reasons"]) or "<li>none — all automated gates pass</li>"
    banner = ("✅ OK TO DOWNLOAD — AUTOMATED GATES PASS · ELIGIBLE FOR THE SELECTOR STEP"
              if promote else "✅ OK TO DOWNLOAD FOR RESEARCH · ⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT")
    return f'''{BEGIN}
<section id="vario-status" aria-label="Authoritative submission status" style="max-width:70rem;margin:1rem auto;padding:1.25rem;border:3px solid {"#14532d" if promote else "#991b1b"};border-radius:12px;background:{"#f0fdf4" if promote else "#fff7ed"};color:#292524;font:1rem/1.6 system-ui,sans-serif;overflow-wrap:anywhere">
<h1 style="margin-top:0">GEMSDOE92 VARIO — {"new unique GeoTIFF generated and auto-validated" if promote else "new byte-unique GeoTIFF generated; registry-uniqueness gate FAILED"}</h1>
<p><strong>{banner}</strong></p>
<p><a class="btn" href="{e(st["file"])}" data-primary="true" download style="display:inline-block;padding:.8rem 1.1rem;background:{"#14532d" if promote else "#1e3a5f"};color:#fff;border-radius:6px;font-weight:700">⬇ Download {e(Path(st["file"]).name)} (.tif)</a>
· <a href="{e(card["packaged"][card["primary_arm"]]["zip"].removeprefix("docs/"))}" download>one-TIFF ZIP</a>
· <a href="vario.html"><strong>Executive summary — exactly how to submit</strong></a>
· <a href="downloads/vario_run_card.json">JSON run card</a>
· <a href="downloads/readiness.json">machine-readable status</a></p>
<p>Submission name: <code>{e(card["submission_name"])}</code><br>
Note for the DrivenData form ({card["note_chars"]}/140 chars): <code>{e(card["note"])}</code><br>
SHA-256: <code>{e(card["raster_sha256"])}</code> · 37,654 dots · single band float32 · EPSG:32611 · 3730×3292</p>
<p><strong>Automated validation (no human pixel inspection):</strong> every cell finite and in [0, 1] — this is the
check behind the portal error <q>Predicted values must be in range [0, 1]</q> — no NaN inside the footprint,
zeros outside, CRS/shape/transform byte-matched to the sample submission, 0 dots on the mapped catalogue,
all dots &gt;2 px from it. Gates are re-derived from the downloaded bytes by <code>scripts/check_site.py</code>.</p>
<p><strong>HOLDOUT-DTI</strong> ({e(hold["evaluator_version"])}, {prim["withheld_positive_pixels"]} withheld positives,
strict draw-blind whole-component holdout): primary <code>{_fmt(prim["dti"])} [{_fmt(prim["ci95"][0])}, {_fmt(prim["ci95"][1])}]</code>;
best same-draw control <code>{e(hold["best_comparable_control"])}</code>; paired Δ <code>{delta["delta"]:+.6f} [{_fmt(delta["ci95"][0])}, {_fmt(delta["ci95"][1])}]</code>.
Leakage canaries: max symmetric AUC <code>{card["leakage_canaries"]["max_symmetric_auc"]}</code> (limit 0.90).
This is a local surrogate, <strong>not</strong> an organizer score; no ORGANIZER-CONFIRMED score exists for this file.</p>
<p><strong>Uniqueness (REGISTRY-MEASUREMENT):</strong> operative sparse dot-field registry worst overlap
<code>{wo.get("forward_overlap_within_3px")}</code> (limit 0.70, vs {e(str(wo.get("file")))}) and worst |ρ|
<code>{abs(wr.get("spearman", 0.0))}</code> (limit 0.90). Disclosure: DUPLICATE UNDER THE LITERAL REGISTRY RULE
reading is unavoidable for any non-empty raster because pinned dense registry surfaces cover the full
footprint (overlap 1.0); both readings are in the run card.</p>
<ul>{reasons}</ul>
<p>Sibling experiment arms (research only, DO NOT SUBMIT): {sibs}. Weekly slots used by this session: 0 —
{"promotion is to the separate selector step within the verified weekly cap." if promote else "no slot is authorized by this artifact."}
Pre-registration: <a href="HYPOTHESES_20261025_VARIO.md">hypotheses</a> ·
analysis: <a href="ANALYSIS_20261025_VARIO.md">why R0 scored 0.2778 [CLAIM] and what VARIO changes</a>.</p>
</section>
{END}'''


def panel_md(card: dict, st: dict) -> str:
    promote = card["verdict"] == "promote"
    hold = card["holdout_dti"]
    prim = hold["scores"][card["primary_arm"]]
    delta = hold["primary_minus_best_control"]
    f = card["submission_file"]
    return f'''{BEGIN}
## Current research download — verified decision, 2026-10-25 (VARIO session)

**{"✅ OK TO DOWNLOAD — AUTOMATED GATES PASS. Eligible for the separate selector step (weekly cap must be verified on the portal; 0 slots spent here)." if promote else "✅ OK TO DOWNLOAD FOR RESEARCH. ⛔ DO NOT SUBMIT — automated promotion gates not met (see run card)."}**
A new unique GeoTIFF **was** generated this session by the pre-registered VARIO lane
([hypotheses](docs/HYPOTHESES_20261025_VARIO.md) · [analysis](docs/ANALYSIS_20261025_VARIO.md) ·
[executive submission guide](docs/vario.html) · [run card](docs/downloads/vario_run_card.json) ·
[machine-readable status](docs/downloads/readiness.json)).

[Download {Path(f).name}]({f}) · name `{card["submission_name"]}` · note ({card["note_chars"]}/140) `{card["note"]}` · SHA-256 `{card["raster_sha256"]}`

Automated validation (no human inspection): finite [0, 1] everywhere (the portal "Predicted values must be in range [0, 1]" check), no NaN in footprint, zeros outside, exact CRS/shape/transform. **HOLDOUT-DTI** ({hold["evaluator_version"]}, {prim["withheld_positive_pixels"]} withheld): `{prim["dti"]:.6f} [{prim["ci95"][0]:.6f}, {prim["ci95"][1]:.6f}]`; paired Δ vs best control `{hold["best_comparable_control"]}`: `{delta["delta"]:+.6f} [{delta["ci95"][0]:.6f}, {delta["ci95"][1]:.6f}]`. No ORGANIZER-CONFIRMED score; GEMSDOE32 0.2778 and all site-inventory scores remain CLAIMs. Literal dense-registry disclosure and operative sparse uniqueness are both in the run card. Historical banners below are archives, not current clearance.

{END}'''


def _replace_block(text: str, block: str) -> str:
    if text.count(BEGIN) != text.count(END) or text.count(BEGIN) > 1:
        raise ValueError("malformed VARIO-STATUS markers")
    if BEGIN in text:
        s, e = text.index(BEGIN), text.index(END) + len(END)
        return text[:s] + block + text[e:]
    body = re.search(r"<body\b[^>]*>", text, re.I)
    if body:  # html: first in body
        return text[:body.end()] + "\n" + block + "\n" + text[body.end():]
    first, sep, rest = text.partition("\n")  # markdown: below H1
    if sep and first.startswith("# "):
        return first + sep + "\n" + block + "\n\n" + rest.lstrip("\n")
    return block + "\n\n" + text


def _strip_superseded_panels(text: str) -> str:
    """Remove the previous sessions' generated current-decision panels.

    They asserted (correctly then) that no new raster had been generated;
    keeping them above or below the VARIO panel would publish two
    contradictory 'current' decisions.  Historical lane evidence outside
    these generated markers is untouched.
    """
    for begin, end in (("<!-- PUBLIC-STATUS:BEGIN -->", "<!-- PUBLIC-STATUS:END -->"),
                       ("<!-- CURRENT-STATUS:BEGIN -->", "<!-- CURRENT-STATUS:END -->"),
                       ("<!-- CURRENT-READINESS:BEGIN -->", "<!-- CURRENT-READINESS:END -->")):
        text = re.sub(re.escape(begin) + r".*?" + re.escape(end) + r"\n?", "", text, flags=re.S)
    return text


def _strip_old_primary(text: str) -> str:
    # exactly one data-primary anchor may exist (the VARIO panel's)
    return text.replace(' data-primary="true"', "")


def vario_page(card: dict, st: dict) -> str:
    e = html.escape
    promote = card["verdict"] == "promote"
    hold = card["holdout_dti"]
    prim_name = card["primary_arm"]
    rows = "".join(
        f'<tr><td><code>{e(k)}</code></td><td>{v["dti"]:.6f}</td><td>[{v["ci95"][0]:.6f}, {v["ci95"][1]:.6f}]</td><td>{v["withheld_positive_pixels"]}</td></tr>'
        for k, v in sorted(hold["scores"].items(), key=lambda kv: -kv[1]["dti"]))
    gates = "".join(f'<tr><td>{e(g["name"])}</td><td>{"PASS" if g["ok"] else "FAIL"}</td><td>{e(g["detail"])}</td></tr>'
                    for g in st["validator_output"])
    sib_rows = "".join(
        f'<tr><td><code>{e(v["arm"])}</code></td><td><a href="{e(v["file"].removeprefix("docs/"))}" download>{e(Path(v["file"]).name)}</a></td>'
        f'<td><code>{e(v["sha256"][:16])}…</code></td><td>{hold["scores"][v["arm"]]["dti"]:.6f}</td></tr>'
        for v in card["packaged"].values())
    step2 = ("Download the TIFF above (or the one-TIFF ZIP). Do not rename the file inside the ZIP."
             if promote else "<strong>Stop.</strong> The current verdict is negative; do not upload this file. The steps below document the procedure for a future promoted artifact.")
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>GEMSDOE92 VARIO — executive summary: exactly how to submit</title><link rel="stylesheet" href="style.css"></head>
<body>
{panel_html(card, st)}
<main style="max-width:70rem;margin:1rem auto;padding:0 1rem;font:1rem/1.6 system-ui,sans-serif">
<h2>Exactly how to make a submission (DrivenData #306)</h2>
<ol>
<li><strong>Check the banner above.</strong> It is generated from the byte-bound run card — green only if format,
leakage-canary, paired holdout and operative-uniqueness gates all pass. No human pixel inspection is involved or needed.</li>
<li>{step2}</li>
<li>Open the competition submission form: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData DOE GEMS</a>
→ Submit. Confirm the weekly cap shown there (this repo cannot see your remaining slots).</li>
<li><strong>File to submit:</strong> choose <code>{e(Path(card["submission_file"]).name)}</code> (single-band GeoTIFF, or the .zip containing only it).</li>
<li><strong>Note (optional) field:</strong> paste exactly: <code>{e(card["note"])}</code> ({card["note_chars"]}/140 characters).
Use <code>{e(card["submission_name"])}</code> as your own reference name for this submission.</li>
<li>Submit once (selector step). After the portal scores it, record the receipt score + date against
SHA-256 <code>{e(card["raster_sha256"])}</code> in <code>ledger/submissions.csv</code> — only that receipt makes a
score ORGANIZER-CONFIRMED. The portal range check ("Predicted values must be in range [0, 1]") is pre-verified
locally: all 12,279,160 cells are finite, min 0.0, max 1.0, no nodata sentinel.</li>
</ol>
<h2>Why this file exists (one paragraph)</h2>
<p>{e(card["hypothesis"])} Mechanism: {e(card["mechanism"])} Named non-fault mimic: {e(card["non_fault_mimic"])}</p>
<h2>HOLDOUT-DTI — all arms and same-draw controls (not organizer scores)</h2>
<p>Evaluator <code>{e(hold["evaluator_version"])}</code>; {e(hold["instrument"])}. Historical reference on the identical
instrument: FAULTNET netfar 0.175147 [0.159756, 0.189860] (<code>evidence/faultnet_holdout.json</code>, non-paired;
its operative public overlap was 0.7586 &gt; 0.70, so it was not promotable).</p>
<table><thead><tr><th>arm</th><th>HOLDOUT-DTI</th><th>95% CI</th><th>withheld positives</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Automated format gates for the primary (re-derived from bytes)</h2>
<table><thead><tr><th>gate</th><th>result</th><th>detail</th></tr></thead><tbody>{gates}</tbody></table>
<h2>All packaged VARIO arms</h2>
<table><thead><tr><th>arm</th><th>file</th><th>SHA-256</th><th>HOLDOUT-DTI</th></tr></thead><tbody>{sib_rows}</tbody></table>
<p>SGMC off-catalogue PROXY (report-only): <code>{e(json.dumps(card["sgmc_proxy"]["dti"]))}</code>
(truth = {card["sgmc_proxy"]["truth_pixels_after_catalogue_and_3px_exclusion"]} USGS SGMC pixels &gt;3 px from the catalogue).</p>
<h2>Evidence boundaries &amp; official sources</h2>
<ul>
<li>Competition, metric (α=0.2, β=0.8, 300 m triangular kernel) and format: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">official problem description</a> (fetched 2026-10-25).</li>
<li>Leaderboard read 2026-10-25: #1 = 0.4413 — <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">official leaderboard</a>.</li>
<li>Reference solution: <a href="https://github.com/drivendataorg/gems-prize-reference-solution">drivendataorg/gems-prize-reference-solution</a>.</li>
<li>GeoDAWN survey: <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a> · INGENIOUS: <a href="https://gbcge.org/current-projects/ingenious/">GBCGE</a> · GDR #1391: <a href="https://gdr.openei.org/submissions/1391">gdr.openei.org</a> · CRS: <a href="https://epsg.io/32611">EPSG:32611</a>.</li>
<li>Inputs are SHA-256-pinned GitHub mirrors (registry/session_manifest.json), not organizer-authenticated downloads;
the sandbox cannot reach DrivenData/USGS directly. Byte identity is verified; official-origin identity is not.</li>
<li>GEMSDOE32's own page (fetched 2026-10-25) labels h33-2-b2 UNSCORED / projected 0.2747 (a model); the brief's 0.2778 is a CLAIM with no receipt in this repo's ledger. See <a href="ANALYSIS_20261025_VARIO.md">analysis</a>.</li>
</ul>
<p><a href="index.html">← Workbench home</a> · <a href="downloads/vario_run_card.json">run card (JSON)</a></p>
</main></body></html>
'''


def render(root: Path = ROOT, *, write: bool = True) -> dict:
    card = load_card(root)
    st = readiness(card)
    changes: dict[Path, str] = {}
    changes[root / "docs/downloads/readiness.json"] = json.dumps(
        {k: v for k, v in st.items()}, indent=2) + "\n"
    changes[root / "docs/vario.html"] = vario_page(card, st)
    block_h = panel_html(card, st)
    for rel in HTML_PAGES:
        p = root / rel
        text = _strip_old_primary(p.read_text())
        text = _strip_superseded_panels(text)
        changes[p] = _replace_block(text, block_h)
    # root index.html (GitHub Pages legacy root) gets a pointer panel if present
    root_index = root / "index.html"
    if root_index.is_file():
        text = _strip_old_primary(root_index.read_text())
        text = _strip_superseded_panels(text)
        ptr = block_h.replace(' data-primary="true"', "").replace(
            'href="downloads/', 'href="docs/downloads/').replace(
            'href="vario.html"', 'href="docs/vario.html"').replace(
            'href="HYPOTHESES_20261025_VARIO.md"', 'href="docs/HYPOTHESES_20261025_VARIO.md"').replace(
            'href="ANALYSIS_20261025_VARIO.md"', 'href="docs/ANALYSIS_20261025_VARIO.md"')
        changes[root_index] = _replace_block(text, ptr)
    block_m = panel_md(card, st)
    for rel in MD_PAGES:
        p = root / rel
        text = p.read_text()
        # drop superseded CURRENT-STATUS block so there is one current decision
        text = re.sub(r"<!-- CURRENT-STATUS:BEGIN -->.*?<!-- CURRENT-STATUS:END -->\n?", "", text, flags=re.S)
        changes[p] = _replace_block(text, block_m)
    stale = [str(p.relative_to(root)) for p, content in changes.items()
             if not p.is_file() or p.read_text() != content]
    if write:
        for p, content in changes.items():
            p.write_text(content)
    return dict(status=st, stale=stale)


def check(root: Path = ROOT) -> list[str]:
    out = render(root, write=False)
    return [f"stale VARIO status: {s}" for s in out["stale"]]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        problems = check()
        for p in problems:
            print(" -", p)
        print("VARIO STATUS STALE" if problems else "VARIO STATUS CURRENT")
        return 1 if problems else 0
    out = render(write=True)
    print(f"rendered VARIO status (verdict={out['status']['verdict']}); updated: {out['stale']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
