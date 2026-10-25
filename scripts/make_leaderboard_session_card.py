#!/usr/bin/env python3
"""Assemble the protocol run card for the 2026-10-25 leaderboard research session.

Every number is computed from a file in this repository (sha256, validator
checks, dot count, the fresh readiness receipt) or copied from a cited official
page snapshot. Nothing is a projection written as a score. No new raster is
generated here: the session's binding stop precedes placement.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

PRIMARY = ROOT / "docs/downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif"
SAMPLE = ROOT / "data/bridge/sample_submission.tif"
READINESS = ROOT / "evidence/readiness_20261025_leaderboard.json"
OUT = ROOT / "evidence/leaderboard_session_20261025_run_card.json"
N_DOTS = 37654


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(path: Path) -> list[dict]:
    with rasterio.open(SAMPLE) as ref, rasterio.open(path) as src:
        foot = np.isfinite(ref.read(1))
        arr = src.read(1)
        checks = [
            {"name": "single_band", "ok": src.count == 1, "detail": f"count={src.count}"},
            {"name": "dtype_float32", "ok": src.dtypes[0] == "float32", "detail": src.dtypes[0]},
            {"name": "crs_match", "ok": src.crs == ref.crs, "detail": str(src.crs)},
            {"name": "shape_match", "ok": src.shape == ref.shape, "detail": str(src.shape)},
            {"name": "transform_match", "ok": src.transform == ref.transform, "detail": str(src.transform)},
            {"name": "no_nan_inside_footprint", "ok": bool(np.isfinite(arr[foot]).all()),
             "detail": f"footprint={int(foot.sum())}"},
            {"name": "values_in_0_1", "ok": bool(((arr >= 0) & (arr <= 1)).all()),
             "detail": f"min={float(np.nanmin(arr))} max={float(np.nanmax(arr))}"},
            {"name": "zero_outside_footprint", "ok": bool((arr[~foot] == 0).all()), "detail": "zeros file"},
            {"name": "positive_cells_equal_dots", "ok": int((arr > 0).sum()) == N_DOTS,
             "detail": f"positive={int((arr > 0).sum())} expected={N_DOTS}"},
        ]
    return checks


def main() -> int:
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    checks = validate(PRIMARY)
    card = {
        "schema": "gemsdoe92-leaderboard-session-run-card-v1",
        "date_utc": "2026-10-25",
        "session_branch": "arena/09f84f2f-gemsdoe92",
        "hypothesis": (
            "Phase congruency (Kovesi log-Gabor, multi-orientation) of the RTP magnetic band (Band 2) "
            "marks low-contrast magnetic contacts that gradient- and analytic-signal ridges miss. "
            "Pre-registered in docs/HYPOTHESES_20261025_LEADERBOARD.md as H1; NOT built, NOT placed."
        ),
        "mechanism": "Local phase agreement across scales/orientations is contrast-invariant; contacts with low amplitude but coherent phase would be ranked.",
        "named_non_fault_mimic": "Lithologic contacts without offset, dike or sill margins, cultural magnetic noise.",
        "holdout_dti": {
            "evidence_class": "NOT RUN",
            "value": None,
            "reason": "Holdout requires placed dots; the literal universal duplicate stop precedes placement.",
        },
        "correlation_overlap_vs_registry": {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "forward_overlap_any_nonempty_in_footprint": readiness["correlation_overlap_vs_registry"][
                "forward_overlap_for_any_nonempty_in_footprint_candidate"],
            "threshold": 0.70,
            "rank_correlation": None,
            "note": "Pinned 17GEMSDOE E-proba witness is positive at all footprint cells; readiness receipt "
                    "evidence/readiness_20261025_leaderboard.json.",
        },
        "research_download_sha256": sha256(PRIMARY),
        "research_download_path": str(PRIMARY.relative_to(ROOT)),
        "validator_output": checks,
        "validator_all_pass": all(c["ok"] for c in checks),
        "submission_name": "GEMSDOE92-LISTRICDIP-updip50-20261025",
        "submission_note": "LISTRICDIP updip50 research TIFF; not cleared; duplicate under literal witness rule",
        "verdict": "negative",
        "submission_eligible": False,
        "new_unique_tiff_generated": False,
        "experiments_used": 0,
        "experiment_budget": 3,
        "weekly_slots_used": 0,
        "organizer_confirmed_score": None,
        "readiness_receipt": "evidence/readiness_20261025_leaderboard.json",
        "readiness_verdict": readiness.get("verdict"),
    }
    assert len(card["submission_note"]) <= 140, "note exceeds 140 characters"
    OUT.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  validator_all_pass={card['validator_all_pass']}")
    return 0 if card["validator_all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
