#!/usr/bin/env python3
"""Measure one named public-registry witness raster against a candidate.

This is NOT the full public scan (scripts/audit_public_registry.py). It
exists because one already-identified witness -- 17GEMSDOE's
E-proba-multiscale raster, positive on 100% of the footprint -- is by
itself binding under the literal forward-overlap rule for any candidate
whose dots lie inside the footprint. Fetching and measuring that single
blob (Git blob SHA verified) records the binding measurement without
re-downloading the full ~1,279-raster inventory; the result must never
be described as a complete public scan.

Usage:
    python scripts/check_public_witness.py <candidate.tif> <witness.tif> \
        --repo buffedlizard55-lab/17GEMSDOE --path docs/downloads/<file> \
        --git-sha <blob sha> --output evidence/<out>.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(p: Path) -> str:
    data = p.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("candidate", type=Path)
    ap.add_argument("witness", type=Path)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--git-sha", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    got_blob = git_blob_sha(args.witness)
    if got_blob != args.git_sha:
        raise SystemExit(f"witness git blob SHA mismatch: {got_blob} != {args.git_sha}")

    with rasterio.open("data/bridge/sample_submission.tif") as ds:
        footprint = np.isfinite(ds.read(1))
    with rasterio.open(args.candidate) as ds:
        cand = ds.read(1)
    with rasterio.open(args.witness) as ds:
        wit = ds.read(1)
    if cand.shape != wit.shape or cand.shape != footprint.shape:
        raise SystemExit("grid shape mismatch among candidate/witness/footprint")

    cand_dots = (cand > 0) & footprint
    wit_support = np.isfinite(wit) & (wit > 0) & footprint
    d_wit = distance_transform_edt(~wit_support)
    forward = float((d_wit[cand_dots] <= 3.0).mean()) if cand_dots.any() else 0.0
    doc = {
        "schema": "gemsdoe92-public-witness-check.v1",
        "evidence_class": "REGISTRY-MEASUREMENT (single binding witness; not a full public scan)",
        "reviewed_utc": datetime.now(timezone.utc).isoformat(),
        "candidate": {"file": args.candidate.name, "sha256": sha256_file(args.candidate),
                      "dots": int(cand_dots.sum())},
        "witness": {
            "raster": f"{args.repo.split('/')[-1]}/{args.path}",
            "source_url": f"https://github.com/{args.repo}/blob/main/{args.path}",
            "git_blob_sha": got_blob,
            "sha256": sha256_file(args.witness),
            "bytes": args.witness.stat().st_size,
            "positive_pixels_in_footprint": int(wit_support.sum()),
            "footprint_pixels": int(footprint.sum()),
            "positive_fraction_of_footprint": float(wit_support.sum() / footprint.sum()),
        },
        "forward_overlap_candidate_dots_within_3px_of_witness": forward,
        "literal_rule": "forward overlap > 0.70 OR |Spearman| > 0.90 => duplicate, log and stop",
        "unique_under_literal_rule_vs_this_witness": bool(forward <= 0.70),
        "stop_required_vs_this_witness": bool(forward > 0.70),
        "scope": ("Single-witness measurement. A pass here would NOT be public "
                  "uniqueness; a fail here IS binding for this witness. The full "
                  "scan remains scripts/audit_public_registry.py."),
    }
    args.output.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(doc, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
