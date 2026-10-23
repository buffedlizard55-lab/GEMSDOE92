#!/usr/bin/env python3
"""Fold the report-only proxy audit into the build receipt and the ledger.

``scripts/build_concentration_variants.py`` writes the rasters, the receipt and
the ledger rows. ``scripts/report_proxies.py`` separately measures the two
REPORT-ONLY instruments (catalogue hide-and-recover, SGMC off-catalogue
control) plus the leakage canaries. This script merges the second into the
first so one file carries the whole story.

Nothing here gates anything and nothing here is a score.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    receipt_path = ROOT / "evidence" / "concentration.json"
    audit_path = ROOT / "evidence" / "proxy_audit_concentration.json"
    ledger_path = ROOT / "ledger" / "submissions.csv"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))

    hold = audit["holdout_protocol"]["scores"]["scores"]
    sgmc = audit["sgmc_control"]
    canary = audit["leakage_canaries"]
    r0_hold = hold["R0"]["dti"]

    merged = {
        "evidence_label": "PROXY",
        "source": str(audit_path.relative_to(ROOT)),
        "catalogue_hide_and_recover": {
            "evaluator": audit["holdout_protocol"]["evaluator"],
            "withheld_positive_pixels": audit["holdout_protocol"]["withheld_positive_pixels"],
            "ci_method": audit["holdout_protocol"]["ci_method"],
            "dti_by_arm": {k: round(v["dti"], 6) for k, v in hold.items()},
            "ci95_by_arm": {k: [round(x, 6) for x in v["ci95"]] for k, v in hold.items()},
            "delta_vs_r0": {k: round(v["dti"] - r0_hold, 6) for k, v in hold.items()},
            "caveat": ("Scores recovery of KNOWN catalogue pixels, which the organisers mask "
                       "out of the live metric; it is the weaker analogue of new-fault truth."),
        },
        "sgmc_off_catalogue_control": {
            "evidence_label": "PROXY",
            "truth_pixels": sgmc["truth_pixels_after_catalogue_and_3px_exclusion"],
            "dti_by_arm": sgmc["dti_by_arm"],
            "delta_vs_r0": sgmc["delta_vs_r0"],
            "caveat": ("Real faults absent from the competition catalogue, i.e. the same class "
                       "as the new-fault target; the better of the two analogues."),
        },
        "leakage_canaries": {
            "max_symmetric_auc": canary["max_symmetric_auc"],
            "stop_and_investigate": canary["stop_and_investigate_if_any_gt_0_90"],
            "features": canary["features"],
        },
        "instrument_disagreement": (
            "The two instruments disagree in sign for this axis: the SGMC control falls "
            "monotonically with dose while the catalogue hide-and-recover rises by about "
            "+0.0018 at every dose. Because the live metric scores new-fault pixels only, "
            "the SGMC control is weighted more heavily in the MODEL prediction, but with "
            "3 scored submissions a week the disagreement is itself the finding: no dose "
            "in this grid is predicted to move the live score by 0.01."
        ),
    }
    receipt["proxy_audit"] = merged
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    rows: list[dict] = []
    fields: list[str] = []
    with ledger_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    hold_by_id = {}
    for rec in receipt["variants"]:
        hold_by_id[rec["value"]] = merged["catalogue_hide_and_recover"]["delta_vs_r0"].get(
            rec["value"])
    for row in rows:
        if row.get("axis") != "CONCENTRATION":
            continue
        d = hold_by_id.get(row.get("value"))
        if d is None:
            continue
        extra = (f" hide-and-recover PROXY delta {d:+.6f} (n="
                 f"{merged['catalogue_hide_and_recover']['withheld_positive_pixels']}); "
                 f"SGMC PROXY disagrees in sign; see evidence/concentration.json.")
        if "hide-and-recover PROXY delta" not in row.get("notes", ""):
            row["notes"] = (row.get("notes", "") + extra).strip()
    with ledger_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print("merged proxy audit into", receipt_path.relative_to(ROOT), "and",
          ledger_path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
