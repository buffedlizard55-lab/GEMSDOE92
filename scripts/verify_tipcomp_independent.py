#!/usr/bin/env python3
"""Independent, line-by-line re-check of the TIPCOMP candidate's stored claims.

Writes evidence/tipcomp_independent_check_20261028.json. Re-computes only what
this sandbox can reach: the candidate's bytes and format gates, the run card's
hash binding, the registry rows whose files are present in the clone (hash
check), and one focus-9 peak re-fetched from codeload.github.com. It does not
re-run the holdout (cached feature stack absent) and never grants clearance.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gems.gates import run_gates, summarise  # noqa: E402

CAND = ROOT / "docs/downloads/gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6-zeros.tif"
CARD = ROOT / "docs/downloads/gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6_run_card.json"
OUT = ROOT / "evidence/tipcomp_independent_check_20261028.json"
PEAK_REPO = "buffedlizard55-lab/GEMSDOE24"
PEAK_SHA_COMMIT = "fdd41b075a05e7df5b222e6e3644344cecc65746"
PEAK_NAME = "gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    card = json.loads(CARD.read_text())
    out: dict = {"schema": 1, "candidate": str(CAND.relative_to(ROOT)), "checks": {}}

    cand_sha = sha256(CAND)
    out["checks"]["candidate_sha256"] = cand_sha
    out["checks"]["run_card_sha256_matches"] = cand_sha == card["raster_sha256"]

    results = run_gates(str(CAND), str(ROOT / "data/bridge/sample_submission.tif"),
                        str(ROOT / "data/bridge/existing_faults.tif"), prune_radius=2,
                        require_submission_encoding=True)
    ok, _ = summarise(results)
    out["checks"]["format_gates_pass"] = bool(ok)
    out["checks"]["format_gates_count"] = len(results)

    rows = card["correlation_overlap_vs_registry"]["rows"]
    present = [r for r in rows if (ROOT / r["file"]).is_file()]
    hash_ok = [r for r in present if sha256(ROOT / r["file"]) == r["sha256"]]
    missing = [r["file"] for r in rows if not (ROOT / r["file"]).is_file()]
    worst = max(present, key=lambda r: r.get("overlap_pi1") or 0)
    out["checks"]["registry_rows_total"] = len(rows)
    out["checks"]["registry_rows_present_in_clone"] = len(present)
    out["checks"]["registry_rows_hash_match"] = len(hash_ok)
    out["checks"]["registry_rows_missing_in_clone"] = missing
    out["checks"]["worst_overlap_pi1_among_present"] = {"value": worst.get("overlap_pi1"), "file": worst["file"]}

    # Re-fetch one focus-9 peak from its GitHub repo archive (codeload is allowed;
    # raw.githubusercontent.com is not) and compare to the pinned hash.
    want = next(r["sha256"] for r in rows if r["file"].endswith("GEMSDOE24_peak_d15.tif"))
    url = f"https://codeload.github.com/{PEAK_REPO}/tar.gz/{PEAK_SHA_COMMIT}"
    matched = None
    with urllib.request.urlopen(url, timeout=600) as resp, tarfile.open(fileobj=resp, mode="r|gz") as tf:
        for m in tf:
            if m.isfile() and m.name.endswith("/" + PEAK_NAME):
                matched = hashlib.sha256(tf.extractfile(m).read()).hexdigest()
                break
    out["checks"]["focus9_GEMSDOE24_peak_refetch_sha256"] = matched
    out["checks"]["focus9_GEMSDOE24_peak_pinned_sha256"] = want
    out["checks"]["focus9_GEMSDOE24_peak_match"] = matched == want

    out["holdout_recheck"] = "NOT RUN: cached feature stack (.cache) absent in clone; holdout numbers are from the run card only"
    out["verdict_from_run_card"] = card["verdict"]
    out["submission_eligible"] = False
    out["note"] = "Verification only. Clearance is not granted by this script."
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["checks"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
