#!/usr/bin/env python3
"""Rejection-only check of one hash-pinned registry witness (not a full scan).

A duplicate exits 1, an invalid input exits 2, and an inconclusive single-witness
check exits 0. Exit 0 NEVER grants submission eligibility. Reuses the template's
literal overlap/rank helpers; does not run or replace a holdout experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
from gems57.uniqueness import (  # noqa: E402
    OVERLAP_LIMIT, RHO_LIMIT, _near, dot_overlap, surface_rho,
)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(p: Path) -> str:
    h = hashlib.sha1(b"blob " + str(p.stat().st_size).encode() + b"\0")
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def measure_witness(candidate: Path, witness: Path, reference: Path, *,
                    repo: str, path: str, expected_git_sha: str) -> dict:
    """Fail closed before comparing pixels; a witness can reject, never clear.

    Positive support means finite values >0, exactly as in the shared template.
    No thresholding a dense field into different 'dots' to evade the protocol.
    """
    candidate, witness, reference = map(Path, (candidate, witness, reference))
    got_blob = git_blob_sha(witness)
    if got_blob != expected_git_sha:
        raise ValueError(f"witness git blob SHA mismatch: {got_blob} != {expected_git_sha}")
    with rasterio.open(reference) as ref:
        if ref.count != 1 or ref.crs is None:
            raise ValueError("reference must have one band and a CRS")
        footprint = np.isfinite(ref.read(1))
        if not footprint.any():
            raise ValueError("reference footprint is empty")
        arrays = []
        for label, filename in (("candidate", candidate), ("witness", witness)):
            with rasterio.open(filename) as ds:
                if (ds.count != 1 or ds.shape != ref.shape or ds.crs != ref.crs
                        or ds.transform != ref.transform):
                    raise ValueError(f"{label} grid/band mismatch (CRS, shape, transform, count)")
                arrays.append(ds.read(1))
        grid = {"crs": str(ref.crs), "shape": list(ref.shape),
                "transform": list(ref.transform)[:6]}
    cand, wit = arrays
    if not np.isfinite(cand).all() or (cand < 0).any() or (cand > 1).any():
        raise ValueError("candidate must be all-finite in [0,1] (zeros-outside download)")
    if np.any(cand[~footprint] != 0):
        raise ValueError("candidate has nonzero predictions outside footprint")
    if not np.any(cand > 0):
        raise ValueError("empty candidate cannot establish uniqueness")
    if not np.isfinite(wit[footprint]).all():
        raise ValueError("witness is nonfinite inside footprint")
    cand_dots = (cand > 0) & footprint
    wit_support = (wit > 0) & footprint
    # Shared helpers handle an empty witness correctly (EDT on an empty support
    # would otherwise fabricate distances from the array boundary).
    forward = dot_overlap(np.where(footprint, cand, 0), np.where(footprint, wit, 0))
    rho = surface_rho(cand, wit, footprint)["spearman_full_footprint"]
    rho = float(rho) if np.isfinite(rho) else None
    duplicate = bool(forward > OVERLAP_LIMIT or (rho is not None and abs(rho) > RHO_LIMIT))
    halo_covers = bool(_near(wit_support)[footprint].all())
    return {
        "schema": "gemsdoe92-public-witness-check.v2",
        "evidence_class": "REGISTRY-MEASUREMENT (single witness; rejection only)",
        "reviewed_utc": datetime.now(timezone.utc).isoformat(),
        "candidate": {"file": candidate.name, "sha256": sha256_file(candidate),
                      "dots": int(cand_dots.sum())},
        "grid": grid,
        "grid_checks_pass": True,
        "candidate_format_checks": {"all_finite": True, "values_in_0_1": True,
                                    "zero_outside_footprint": True},
        "witness": {
            "raster": f"{repo.split('/')[-1]}/{path}",
            "source_url": f"https://github.com/{repo}/blob/HEAD/{path}",
            "blob_api_url": f"https://api.github.com/repos/{repo}/git/blobs/{expected_git_sha}",
            "git_blob_sha": got_blob, "sha256": sha256_file(witness),
            "bytes": witness.stat().st_size,
            "positive_pixels_in_footprint": int(wit_support.sum()),
            "footprint_pixels": int(footprint.sum()),
            "positive_fraction_of_footprint": float(wit_support.sum() / footprint.sum()),
            "halo_covers_entire_footprint": halo_covers,
        },
        "forward_overlap_candidate_dots_within_3px_of_witness": forward,
        "spearman_full_footprint": rho,
        "literal_rule": "forward overlap > 0.70 OR |Spearman| > 0.90 => duplicate, log and stop",
        "unique_under_literal_rule_vs_this_witness": False if duplicate else None,
        "stop_required_vs_this_witness": duplicate,
        "submission_eligible": False,
        "universal_nonempty_in_footprint_overlap_stop": halo_covers,
        "scope": "Single witness: rejection only, no full-registry or pre-placement clearance.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("candidate", type=Path)
    ap.add_argument("witness", type=Path)
    ap.add_argument("--reference", type=Path, default=ROOT / "data/bridge/sample_submission.tif")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--git-sha", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    # Do not destroy the historical v1 receipts or another run's measurements.
    if args.output.exists():
        ap.error("output already exists; use a new path to preserve historical evidence")
    try:
        doc = measure_witness(args.candidate, args.witness, args.reference,
                              repo=args.repo, path=args.path, expected_git_sha=args.git_sha)
    except (OSError, ValueError, rasterio.errors.RasterioError) as exc:
        ap.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as f:
        f.write(json.dumps(doc, indent=2, allow_nan=False) + "\n")
    print(json.dumps(doc, indent=2, allow_nan=False))
    return 1 if doc["stop_required_vs_this_witness"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
