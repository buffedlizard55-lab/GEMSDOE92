#!/usr/bin/env python3
"""Independently recheck the nine selected masks with the shared 2-D halo.

Downloads only pinned public GitHub blobs into ignored .cache/, verifies Git
blob and SHA-256 identities, and compares the 36 pairs with the earlier receipt.
This is rejection-only research analysis: it creates no candidate or holdout.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from vendor.gems57 import uniqueness as U  # noqa: E402

SOURCE = ROOT / "docs/downloads/focus_sites_release_review_20261026.json"
SAMPLE = ROOT / "data/bridge/sample_submission.tif"
CACHE = ROOT / ".cache/focus9_pairwise_recheck"
SAMPLE_SHA = "2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc"


def validate_blob(data: bytes, *, blob: str, sha256: str, size: int) -> None:
    git_sha = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if len(data) != size or git_sha != blob or hashlib.sha256(data).hexdigest() != sha256:
        raise ValueError("Git blob/SHA-256/size mismatch")


def get_raster(row: dict, *, fetch: bool) -> Path:
    repo = row["source_repository"]
    ref = row["comparison_reference"]
    blob, digest, size = ref["git_blob_sha1"], ref["sha256"], ref["bytes"]
    if (not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo)
            or not re.fullmatch(r"[a-f0-9]{40}", blob)
            or not re.fullmatch(r"[a-f0-9]{64}", digest)
            or type(size) is not int or not 0 < size < 20_000_000):
        raise ValueError("invalid pinned source metadata")
    path = CACHE / f"{blob}.tif"
    if path.exists():
        data = path.read_bytes()
        validate_blob(data, blob=blob, sha256=digest, size=size)
        return path
    if not fetch:
        raise FileNotFoundError(f"pinned raster not cached: {row['site']}")
    result = subprocess.run(["gh", "api", f"repos/{repo}/git/blobs/{blob}"],
                            check=True, capture_output=True, text=True, timeout=90)
    obj = json.loads(result.stdout)
    if obj.get("sha") != blob or obj.get("size") != size or obj.get("encoding") != "base64":
        raise ValueError("unexpected GitHub blob response")
    data = base64.b64decode("".join(obj["content"].split()), validate=True)
    validate_blob(data, blob=blob, sha256=digest, size=size)
    CACHE.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as fh:
            fh.write(data)
    except FileExistsError:
        validate_blob(path.read_bytes(), blob=blob, sha256=digest, size=size)
    return path


def pair_statistics(a: np.ndarray, b: np.ndarray, footprint: np.ndarray) -> dict:
    a = np.asarray(a, dtype=bool) & footprint
    b = np.asarray(b, dtype=bool) & footprint
    na, nb, n = int(a.sum()), int(b.sum()), int(footprint.sum())
    if not 0 < na < n or not 0 < nb < n:
        raise ValueError("empty or constant candidate support")
    inter = int((a & b).sum())
    # Binary Spearman midrank correlation is the Pearson/phi coefficient.
    phi = (inter * n - na * nb) / math.sqrt(na * (n - na) * nb * (n - nb))
    a_to_b = float(U._near(b, 3)[a].mean())
    b_to_a = float(U._near(a, 3)[b].mean())
    return {
        "exact_prediction_match": bool(np.array_equal(a, b)),
        "intersection_dots": inter,
        "forward_3px_overlap_a_to_b": a_to_b,
        "forward_3px_overlap_b_to_a": b_to_a,
        "spearman_binary_support_phi": phi,
        "duplicate_by_configured_threshold": bool(max(a_to_b, b_to_a) > 0.70 or abs(phi) > 0.90),
    }


def recheck(*, fetch: bool) -> dict:
    raw = SOURCE.read_bytes()
    data = json.loads(raw)
    if hashlib.sha256(SAMPLE.read_bytes()).hexdigest() != SAMPLE_SHA:
        raise ValueError("sample footprint hash mismatch")
    with rasterio.open(SAMPLE) as ds:
        foot = np.isfinite(ds.read(1))
        grid = (ds.shape, ds.crs, ds.transform)
    masks = {}
    for row in data["selected_site_artifacts"]:
        path = get_raster(row, fetch=fetch)
        with rasterio.open(path) as ds:
            if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != grid:
                raise ValueError(f"grid mismatch: {row['site']}")
            vals = ds.read(1)
        if (not np.isfinite(vals[foot]).all()
                or (vals[foot] < 0).any() or (vals[foot] > 1).any()):
            raise ValueError(f"invalid in-footprint values: {row['site']}")
        masks[row["site"]] = (vals > 0) & foot
    if len(masks) != 9:
        raise ValueError("expected nine distinct sites")
    pairs = []
    differences = []
    max_diff = 0.0
    for old in data["all_pairwise_comparisons"]:
        a, b = old["site_a"], old["site_b"]
        now = pair_statistics(masks[a], masks[b], foot)
        changed = {}
        for key, value in now.items():
            if isinstance(value, float):
                diff = abs(value - old[key])
                max_diff = max(max_diff, diff)
                if diff > 1e-10:
                    changed[key] = {"prior": old[key], "row_safe_recheck": value}
            elif value != old[key]:
                changed[key] = {"prior": old[key], "row_safe_recheck": value}
        if changed:
            differences.append({"site_a": a, "site_b": b, "fields": changed})
        pairs.append({"site_a": a, "site_b": b, **now})
    if len(pairs) != 36:
        raise ValueError("pairwise inventory must contain 36 pairs")
    return {
        "schema": "gemsdoe92-focus9-row-safe-recheck-v1",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "sample_sha256": SAMPLE_SHA,
        "method": "Shared vendor/gems57/uniqueness._near 2-D Euclidean 3-pixel halo; exact binary-support phi.",
        "evidence_class": "REGISTRY-MEASUREMENT; nine sites only; rejection-only, not global clearance",
        "sites": list(masks),
        "source_blob_and_sha256_verified": True,
        "pairs": len(pairs),
        "all_match_prior": not differences,
        "pairs_with_changed_metrics": len(differences),
        "max_absolute_float_difference": max_diff,
        "all_pairs_duplicate_in_at_least_one_direction_or_rho": all(
            p["duplicate_by_configured_threshold"] for p in pairs),
        "new_tiff_generated": False,
        "holdout_run": False,
        "submission_eligible": False,
        "differences_from_prior": differences,
        "comparisons": pairs,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fetch", action="store_true", help="fetch missing public Git blobs into ignored cache")
    ap.add_argument("--output", type=Path, required=True, help="new receipt path; never overwrite")
    args = ap.parse_args(argv)
    try:
        if args.output.exists():
            raise ValueError("output already exists; choose a new receipt")
        result = recheck(fetch=args.fetch)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, allow_nan=False)
            fh.write("\n")
        print(f"36 row-safe comparisons; {result['pairs_with_changed_metrics']} pairs differ from prior values: {args.output}")
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f"focus-site recheck inconclusive: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
