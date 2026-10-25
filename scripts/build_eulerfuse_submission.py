#!/usr/bin/env python3
"""Package the holdout-selected EULERFUSE negative research artifact.

This consumes no competition slot and never marks the file promoted. It exists
because a unique, directly downloadable, range-safe GeoTIFF was explicitly
requested even when the pre-registered holdout decision is negative.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from evaluate_eulerfuse import emit, load_mask  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems.ledger import append_variant, pair_seen  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57 import grid as grid_mod, submission_writer  # noqa: E402
from gems57.validate import assert_submittable, validate  # noqa: E402

CACHE = ROOT / ".cache/gems_inputs/eulerfuse_cache.npz"
HOLDOUT = ROOT / "evidence/eulerfuse_holdout.json"
OUTDIR = ROOT / "docs/downloads"
DATE = "20261024"


def main() -> int:
    hold = json.loads(HOLDOUT.read_text())
    if hold["best_arm"] != "gravity":
        raise SystemExit(f"frozen build expects holdout-selected gravity arm, got {hold['best_arm']}")
    if hold["decision"]["promotion_gate_pass"]:
        raise SystemExit("unexpected promotion state; selector handling is a separate process")

    cache = np.load(CACHE)
    grid = grid_mod.load_grid(ROOT / ".cache/gems_inputs/bridge")
    foot, cat = grid.footprint, grid.catalogue
    valid = cache["valid"].astype(bool)
    surface = cache["S_gravity_full"].astype(np.float32)
    d_cat = distance_transform_edt(~cat)
    h19 = load_mask(ROOT / "data/bridge/h19_5.tif", foot)
    d_h19 = distance_transform_edt(~h19)
    mask = emit("gravity", surface, valid, d_cat, h19, d_h19)
    if np.any(mask & cat) or np.any(d_cat[mask] <= 2.0):
        raise RuntimeError("catalogue exclusion failed")

    mask_sha = hashlib.sha256(np.packbits(mask).tobytes()).hexdigest()
    stem = f"gemsdoe92-eulerfuse-gravity-37654-{DATE}-{mask_sha[:8]}-zeros"
    out = OUTDIR / f"{stem}.tif"
    name = "GEMSDOE92-EULERFUSE-gravity-20261024"
    note = "EULERFUSE gravity: 37654 LOQO Euler-contact dots; HOLDOUT-DTI 0.110387; negative"
    if len(note) > 140:
        raise AssertionError("submission note exceeds 140 characters")

    pred = mask.astype(np.float32)
    if out.exists():
        raise FileExistsError(f"refusing to overwrite {out}")
    receipt = submission_writer.write_submission(
        out,
        pred,
        ROOT / ".cache/gems_inputs/bridge/sample_submission.tif",
        foot,
        note=note,
        name=name,
        catalogue=cat,
        metadata={
            "lane": "EULERFUSE",
            "arm": "gravity",
            "verdict": "negative",
            "promotion_gate_pass": False,
            "weekly_slots_used": 0,
            "holdout_evidence": "evidence/eulerfuse_holdout.json",
        },
    )

    disk_sha = sha256_file(out)
    if disk_sha != receipt["sha256"]:
        raise RuntimeError("writer receipt SHA does not match exact on-disk TIFF")
    report = validate(out, foot, cat)
    assert_submittable(report)
    gates = run_gates(
        str(out),
        str(ROOT / ".cache/gems_inputs/bridge/sample_submission.tif"),
        str(ROOT / ".cache/gems_inputs/bridge/existing_faults.tif"),
        prune_radius=2,
        require_submission_encoding=True,
    )
    ok, text = summarise(gates)
    if not ok:
        raise RuntimeError(text)

    values = hold["primary_drawblind_visible_mask"]["pooled_by_candidate"]["gravity"]["scores"]["gravity"]
    audit = {
        "schema": "gemsdoe92.eulerfuse-download-audit.v1",
        "file": out.name,
        "sha256": disk_sha,
        "zip_file": out.with_suffix(".zip").name,
        "zip_sha256": sha256_file(out.with_suffix(".zip")),
        "submission_name": name,
        "note": note,
        "note_chars": len(note),
        "holdout_dti": values,
        "verdict": "negative",
        "submission_eligible": False,
        "weekly_slots_used": 0,
        "validator_output": report,
        "gates": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates],
        "all_gates_pass": ok,
        "dot_count": int(mask.sum()),
        "catalogue_mass": int((mask & cat).sum()),
        "min_catalogue_distance_px": float(d_cat[mask].min()),
        "mask_sha256": mask_sha,
        "status_text": "OK TO DOWNLOAD FOR RESEARCH; DO NOT SUBMIT — holdout promotion gate failed and public uniqueness is pending.",
    }
    audit_path = OUTDIR / f"{stem}-audit.json"
    audit_path.write_text(json.dumps(audit, indent=2, allow_nan=False) + "\n")

    if not pair_seen("h33-h33-2-b2", "EULERFUSE", "gravity"):
        append_variant({
            "id": stem.removesuffix("-zeros"),
            "parent": "h33-h33-2-b2",
            "axis": "EULERFUSE",
            "value": "gravity",
            "n_dots": "37654",
            "pct_changed": "",
            "sha256": disk_sha,
            "status": "BUILT",
            "predicted_change": "none; HOLDOUT-DTI recorded in evidence/eulerfuse_holdout.json",
            "file_zeros": f"docs/downloads/{out.name}",
            "file_nan": "",
            "sha8": disk_sha[:8],
            "change_desc": "EULERFUSE gravity: LOQO gravity-Euler contact-source crests; 37654 unit dots",
            "receipt_score": "",
            "receipt_date": "",
            "notes": "verdict=negative; no weekly slot; strict draw-blind HOLDOUT-DTI 0.110387; exact CI/run metadata in evidence/eulerfuse_holdout.json",
        })

    print(json.dumps({
        "file": str(out), "sha256": disk_sha, "zip": str(out.with_suffix('.zip')),
        "audit": str(audit_path), "note_chars": len(note), "verdict": "negative",
        "submission_eligible": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
