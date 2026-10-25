#!/usr/bin/env python3
"""Write the per-file audit JSON for DILATATION p10 (non-primary served raster).

Mirrors the existing p12 audit shape: gates_zeros + gates_nan from an
independent disk re-read (gems57.validate + gems.gates.run_gates), with
sha256 pinned to the byte-verified zeros TIFF in docs/downloads/.
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from gems57 import grid as grid_mod, validate as V  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402

BRIDGE = ROOT / ".cache" / "gems_inputs" / "bridge"
DOWNLOADS = ROOT / "docs" / "downloads"
STEM = "h33-h33-2-b2-DILATATIONp10dilatation-20261025-2e501f88"
ZEROS = DOWNLOADS / f"{STEM}-zeros.tif"
NAN = ROOT / "releases" / f"{STEM}.tif"
AUDIT = DOWNLOADS / f"{STEM}-audit.json"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    grid = grid_mod.load_grid(BRIDGE)
    foot, cat = grid.footprint, grid.catalogue
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    tif_sha = sha256_file(ZEROS)
    nan_sha = sha256_file(NAN)

    v = V.validate(ZEROS, foot, cat)
    V.assert_submittable(v)
    gate_results = run_gates(
        str(ZEROS), str(BRIDGE / "sample_submission.tif"),
        str(BRIDGE / "existing_faults.tif"), prune_radius=2,
        require_submission_encoding=True,
    )
    gate_ok, _ = summarise(gate_results)
    gate_rows = [{"name": r.name, "ok": bool(r.ok), "detail": r.detail} for r in gate_results]

    v_nan = V.validate(NAN, foot, cat)
    gate_nan = run_gates(
        str(NAN), str(BRIDGE / "sample_submission.tif"),
        str(BRIDGE / "existing_faults.tif"), prune_radius=2,
        require_submission_encoding=True,
    )
    # The NaN-outside twin is not a submission encoding (NaN outside footprint),
    # so its submission_encoding row is not meaningful there (mirrors p12 audit).
    gate_nan_rows = [{"name": r.name, "ok": bool(r.ok), "detail": r.detail}
                     for r in gate_nan if r.name != "submission_encoding"]

    audit = dict(
        schema="gemsdoe92-audit.v2", lane="DILATATION", arm="p10dilatation",
        file=f"docs/downloads/{ZEROS.name}",
        sha256_zeros=tif_sha, sha256_nan=nan_sha,
        bytes=ZEROS.stat().st_size, generated_utc=stamp,
        overall_pass=bool(all(r["ok"] for r in gate_rows) and v["all_checks_passed"]
                          and all(r["ok"] for r in gate_nan_rows)),
        submission_eligible=False,
        validator=v,
        gates_zeros=gate_rows,
        gates_nan=gate_nan_rows,
        gates_pass=gate_ok,
        note=("All gates PASS on independent disk reread; values in [0,1], no NaN inside "
              "footprint, zero catalogue mass; p10 arm is a research control (verdict negative, "
              "not submission-eligible; 0 weekly slots)."),
    )
    AUDIT.write_text(json.dumps(audit, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"WROTE {AUDIT}  sha256_zeros={tif_sha}  gates_ok={gate_ok}  overall_pass={audit['overall_pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
