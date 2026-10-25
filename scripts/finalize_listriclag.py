#!/usr/bin/env python3
"""Merge the binding public-registry audit into the LISTRICLAG run card.

Fail-closed: the public phase can only downgrade a verdict, never upgrade it.
Updates evidence/<stem>_run_card.json + docs/downloads copies in place and
prints the final Protocol Rule 5 run card summary.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stem", required=True, help="e.g. gemsdoe92-listriclag-20261025T145312Z")
    ap.add_argument("--public", required=True,
                    help="evidence JSON written by audit_public_registry.py")
    args = ap.parse_args()

    card_path = ROOT / "evidence" / f"{args.stem}_run_card.json"
    card = json.loads(card_path.read_text(encoding="utf-8"))
    pub = json.loads((ROOT / args.public).read_text(encoding="utf-8"))

    pre = pub.get("preplacement_surface", {})
    fin = pub.get("final_dots", {})
    stop = bool(fin.get("stop_required") or pre.get("stop_required"))
    public_summary = dict(
        evidence_class="REGISTRY-MEASUREMENT",
        source=args.public,
        scan_source=pub.get("inventory", {}).get("scan_source"),
        rasters_compared=pub.get("inventory", {}).get("one_band_exact_template_grid_rasters_compared"),
        scan_complete_for_declared_scope=pub.get("scan_complete_for_declared_scope"),
        preplacement_worst_abs_spearman=pre.get("worst_abs_spearman"),
        preplacement_worst_rho_raster=pre.get("worst_rho_raster"),
        final_worst_forward_overlap=fin.get("worst_forward_overlap"),
        final_worst_overlap_raster=fin.get("worst_overlap_raster"),
        rasters_over_70pct_overlap=fin.get("rasters_over_70pct_overlap"),
        duplicate_examples=fin.get("duplicate_examples"),
        binding_witness=pub.get("binding_witness"),
        stop_required=stop,
        audit_verdict=pub.get("verdict"),
    )
    card["correlation_overlap_vs_registry"]["public"] = public_summary
    for a in (ROOT / "docs" / "downloads" / f"{args.stem}-audit.json",):
        if a.is_file():
            audit = json.loads(a.read_text(encoding="utf-8"))
            audit["public_registry"] = public_summary
            a.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    if stop and card["verdict"] != "negative":
        card["verdict"] = "negative"
        card["submission_eligible"] = False
    card["verdict_reason"] = card["verdict_reason"].replace(
        "public scan pending",
        f"public scan merged (stop_required={stop}, worst literal overlap "
        f"{fin.get('worst_forward_overlap')}, {pub.get('inventory', {}).get('one_band_exact_template_grid_rasters_compared')} rasters)")

    out = json.dumps(card, indent=2) + "\n"
    card_path.write_text(out, encoding="utf-8")
    dl = ROOT / "docs" / "downloads" / f"{args.stem}_run_card.json"
    if dl.is_file():
        dl.write_text(out, encoding="utf-8")
    print(json.dumps(dict(verdict=card["verdict"], submission_eligible=card["submission_eligible"],
                          public=public_summary), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
