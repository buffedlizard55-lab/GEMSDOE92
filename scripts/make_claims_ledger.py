#!/usr/bin/env python3
"""Rebuild ledger/claimed_scores_20261024.csv (CLAIM, not receipts).

The claim values were reconstructed from the operator's session prompt as it
survived in session memory (verbatim text is NOT stored in this repo).  The
registry match for each claim is re-derived here from the cached public
registry catalogue so it can be audited; `match_confidence` records how sure the
file<->claim tie is.  Unmatched claims are kept, never silently dropped.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CAT = pd.read_csv(ROOT / "evidence" / "registry_catalog_20261024.csv")

# site label, name, claimed score, registry repo, path substring, confidence, note
ROWS = [
    ("GEMSDOE32", "h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros", 0.2778, "@R0", None, "exact",
     "parent R0; sha256 c55bafc4... verified against data/parent_R0_zeros.tif and the GEMSDOE32 README"),
    ("GEMSDOE36", "anderson-geothermal-pinn-38854", 0.2750, "GEMSDOE36", "anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros", "high",
     "= R0 + 1,200 dots (measured set relation); name and dot count agree"),
    ("GEMSDOE28", "h36-1-rung30-blind-r1", 0.2710, "GEMSDOE28", "h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan", "high",
     "SOLO-based replacement set measured vs SOLO: 27,853 shared, 9,807 new, 12,346 removed; 37,660 dots"),
    ("GEMSDOE31", "solo-d28", 0.2708, "GEMSDOE31", "h27-4-solo-d28-20261004-8acb75e1-nan", "high",
     "SOLO emission (40,199 dots); GEMSDOE28 h27-4-r1-solo-d2-8 carries the same 0.2708 claim"),
    ("GEMSDOE28", "h38-1-hf-euler-r30-r1", 0.2707, "GEMSDOE28", "h38-1-hf-euler-r30-r1-20261003-56a9f473edc7-nan", "high", "37,860 dots"),
    ("GEMSDOE28", "h32-1-prethin-tip-euler-d2-8", 0.2649, "GEMSDOE28", "h32-1-prethin-tip-euler-d2-8-20261003-31e35eee884e-nan", "high", "42,294 dots"),
    ("GEMSDOE33", "h33d-analog-tip-stepover-r30", 0.2632, "GEMSDOE33", "GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-nanoutside", "high", "41,865 dots"),
    ("GEMSDOE25", "dotted-h19-5-d2-8 (= GEMSDOE30 d28-poisson, GEMSDOE29 efd28-repro)", 0.2600, "GEMSDOE29", "refd28-repro-20261003-1cc7dc534d51-nan", "high",
     "three pixel-identical 44,090-dot rasters (GEMSDOE32 evidence/d28_forensic_autopsy.json)"),
    ("GEMSDOE29", "wormrank-d28", 0.2560, "GEMSDOE29", "wormrank-d28-20261003-59dcaf6dd11d-nan", "high", "41,338 dots; R0-lineage"),
    ("GEMSDOE70", "(site best score) p5-dual-submod300-oof38k", 0.2478, "GEMSDOE70", "gems70-p5-dual-submod300-oof38k", "medium",
     "site-level score recalled from the operator list; file chosen by name"),
    ("GEMSDOE24", "dotted-h19-5-d1-5", 0.2477, "GEMSDOE24", "h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan", "high", "60,069 dots"),
    ("GEMSDOE27", "topo-gap-closure on d1-5", 0.2449, "GEMSDOE27", "topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan", "high", "61,328 dots"),
    ("GEMSDOE49", "gate_ortho_w0.25-40k", 0.2376, "GEMSDOE49", "gate_ortho_w0.25-40k-20261006T213721Z-zeros", "medium", "site-level score; file chosen by name"),
    ("GEMSDOE76", "ptcf-tiltworm-submod39k", 0.2343, "GEMSDOE76", "ptcf-tiltworm-submod39k-20261021T034000Z-6316481d-zeros", "high", "39,200 dots"),
    ("GEMSDOE63", "cvarlw-thin-s3p17-54864", 0.2303, "GEMSDOE63", "cvarlw-thin-s3p17-54864-20261011T220606Z-c58f60c4-zeros", "medium", "site-level score; file chosen by name"),
    ("GEMSDOE48", "h59-cover-ds-belief-b2xh33d", 0.2296, "GEMSDOE48", "h59-cover-ds-belief-b2xh33d-20261008T184547Z", "medium",
     "R0-lineage; re-introduces 3,468 dots within 2 px and 598 on the catalogue"),
    ("GEMSDOE19", "h19-5-powerlaw-budget-multiline", 0.1922, "19GEMSDOE", "h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan", "high", "121,131 dots (skeleton)"),
    ("GEMSDOE73", "h73-mcsc-seamfree-blakely-37654dots", 0.1917, "GEMSDOE73", "h73-mcsc-seamfree-blakely-37654dots-20261021T073716Z-b27ac445-zeros", "medium", "site-level score; file chosen by name"),
    ("GEMSDOE19", "h19-4-multiline-corroborated", 0.1894, "19GEMSDOE", "h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan", "high", "123,779 dots"),
    ("GEMSDOE82", "h82-submodular-punoisyor", 0.1886, "GEMSDOE82", "h82-submodular-punoisyor-20261021T235456Z-fe137199-zeros", "medium", "site-level score; file chosen by name"),
    ("GEMSDOE10", "h28-dotted-ridge", 0.1839, "GEMSDOE10", "h28-dotted-ridge", "medium", "site-level score; file chosen by name"),
    ("GEMSDOE75", "trlt-radon-loco-ridge", 0.1627, "GEMSDOE75", "trlt-radon-loco-ridge-20261021-zeros", "medium", "36,800 dots"),
    ("GEMSDOE46", "(site score 0.1589)", 0.1589, None, None, "unmatched", "nine distinct rasters in this site; which one was scored is not retained"),
    ("GEMSDOE78", "h78sigx-fuse-b5-44090dots", 0.1564, "GEMSDOE78", "h78sigx-fuse-b5-44090dots-20261022T021932Z-zeros", "medium", "site-level score; file chosen by name"),
    ("GEMSDOE1/5/8", "(0.1563 group)", 0.1563, "8GEMSDOE", "8GEMSDOE_Hedge-v2_submission", "low", "three sites reported at 0.1563; Hedge-v2 is a 227,507-dot raster"),
    ("GEMSDOE29", "sgmc-off-catalogue-44k", 0.0500, "GEMSDOE29", "sgmc-off-catalogue-44k-20261003-c8dcd780e3fd-nan", "medium",
     "operator list gave a 0.049-0.051 range for the SGMC off-catalogue lanes; 0.0500 used"),
    ("GEMSDOE72", "h72-1-sgmc-offcatalogue", 0.0500, "GEMSDOE72", "h72-1-sgmc-offcatalogue-20261020T195456Z-6e6525e5-zeros", "medium", "same range as above"),
    ("GEMSDOE62", "(site score)", 0.0000, None, None, "unmatched", "reported 0.0000; which of 24 rasters was scored is not retained"),
]


def main() -> int:
    out = ROOT / "ledger" / "claimed_scores_20261024.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["site", "name", "claimed_score", "evidence_label", "registry_match_file", "n_dots",
                    "sha256", "match_confidence", "note"])
        for site, name, score, repo, sub, conf, note in ROWS:
            if repo == "@R0":
                w.writerow([site, name, score, "CLAIM", "data/parent_R0_zeros.tif", 37654, "c55bafc47005...", conf, note])
                continue
            m = None
            if sub:
                hit = CAT[CAT.path.str.contains(sub, regex=False) & (CAT.repo == repo)]
                m = hit.iloc[0] if len(hit) else None
                if m is None:
                    conf, note = "unmatched", note + " | NO REGISTRY FILE FOUND for the substring"
            w.writerow([site, name, score, "CLAIM", (f"{m.repo}/{m.path}" if m is not None else ""),
                        (int(m.n_pos) if m is not None else ""), (m.sha256[:16] + "..." if m is not None else ""), conf, note])
    print(f"wrote {out.relative_to(ROOT)} ({len(ROWS)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
