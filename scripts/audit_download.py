#!/usr/bin/env python3
"""Independent audit receipt for a served primary download.

Usage:
    python scripts/audit_download.py docs/downloads/<stem>-zeros.tif docs/downloads/<stem>.tif
Writes docs/downloads/<stem>-audit.json (schemas checked by
scripts/check_site.py): sha256 of both encodings, gates_zeros/gates_nan as
[{name, ok, detail}] from gems.gates.run_gates on a fresh disk read, and
overall_pass.  Refuses to write a passing receipt when any gate fails.
"""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gems.gates import run_gates
from gems.rasters import sha256_file

def gates(path: Path, *, require_submission_encoding: bool = False):
    res = run_gates(
        str(path), str(ROOT/"data/bridge/sample_submission.tif"),
        str(ROOT/"data/bridge/labels.tif"), prune_radius=2,
        require_submission_encoding=require_submission_encoding,
    )
    return [{"name": r.name, "ok": bool(r.ok), "detail": r.detail} for r in res]

def main() -> int:
    zeros, nan = Path(sys.argv[1]), Path(sys.argv[2])
    # Only the zeros-outside encoding is intended as an upload candidate.
    # Keep the NaN twin in the receipt as a legacy/research comparison.
    gz, gn = gates(zeros, require_submission_encoding=True), gates(nan)
    ok = all(g["ok"] for g in gz) and all(g["ok"] for g in gn)
    doc = {
        "file": zeros.name,
        "sha256_zeros": sha256_file(zeros),
        "sha256_nan": sha256_file(nan),
        "gates_zeros": gz, "gates_nan": gn,
        "overall_pass": ok,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "note": ("All gates PASS on independent disk reread; local format check only, not submission clearance"
                 if ok else "FAIL: one or more gates failed on independent disk reread; do not submit"),
    }
    out = zeros.with_name(zeros.stem.removesuffix("-zeros") + "-audit.json")
    out.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(out, "overall_pass", ok)
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
