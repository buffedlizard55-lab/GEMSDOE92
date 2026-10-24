#!/usr/bin/env python3
"""Reproduce the shared uniqueness gate's universal-overlap check.

The public 17GEMSDOE multiscale probability raster is hash-pinned below. If it
covers every legal footprint cell, the literal >70% forward-overlap rule blocks
every nonempty prediction, so no candidate should be placed or packaged.
The TIFF is cached only under ignored .cache/; it is never copied into Git.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from vendor.gems57.grid import CRS_EPSG, SHAPE, TRANSFORM, load_grid
from vendor.gems57.metric import RADIUS_PX
from vendor.gems57.uniqueness import OVERLAP_LIMIT, saturation_certificate

OWNER = "buffedlizard55-lab"
REPO = "17GEMSDOE"
BLOB_SHA = "374c88b1da2b803e2ed160de467fd71ae114010d"
EXPECTED_SHA256 = "ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be"
PUBLIC_PATH = "docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif"
DEFAULT_CACHE = Path(".cache/public_gems_tifs/17GEMSDOE_E-proba-multiscale_374c88b1da2b803e2ed160de467fd71ae114010d.tif")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_witness(path: Path) -> None:
    if path.exists() and sha256(path) == EXPECTED_SHA256:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    endpoint = f"repos/{OWNER}/{REPO}/git/blobs/{BLOB_SHA}"
    with path.open("wb") as out:
        proc = subprocess.run(
            ["gh", "api", "-H", "Accept: application/vnd.github.raw", endpoint],
            stdout=out, stderr=subprocess.PIPE, check=False,
        )
    if proc.returncode:
        path.unlink(missing_ok=True)
        raise RuntimeError(proc.stderr.decode("utf-8", "replace").strip() or "GitHub blob download failed")
    actual = sha256(path)
    if actual != EXPECTED_SHA256:
        path.unlink(missing_ok=True)
        raise ValueError(f"witness SHA-256 mismatch: {actual} != {EXPECTED_SHA256}")


def audit(witness: Path) -> dict:
    ensure_witness(witness)
    grid = load_grid()
    result = saturation_certificate(
        witness,
        grid.footprint,
        grid.catalogue,
        expected_grid=(SHAPE, CRS_EPSG, TRANSFORM),
    )
    result.update({
        "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "witness_repo": f"{OWNER}/{REPO}",
        "witness_public_path": PUBLIC_PATH,
        "witness_git_blob_sha": BLOB_SHA,
        "witness_sha256": sha256(witness),
        "witness_bytes": witness.stat().st_size,
        "comparison_tool": "vendor.gems57.uniqueness.saturation_certificate",
        "overlap_radius_px": RADIUS_PX,
        "overlap_threshold": OVERLAP_LIMIT,
        "grid": {
            "shape": list(SHAPE),
            "crs": CRS_EPSG,
            "transform": [float(v) for v in tuple(TRANSFORM)[:6]],
            "allowed_domain": "sample_submission finite footprint minus pixel-exact mapped catalogue",
        },
        "scope": "One hash-verified public candidate-like raster is sufficient to prove a universal blocker under the literal all-raster overlap rule. This is not a complete byte-level audit of all registry rasters.",
        "decision": "STOP_BEFORE_PLACEMENT" if result["universal_overlap_blocker"] else "NO_UNIVERSAL_BLOCKER_ESTABLISHED",
        "candidate_built": False,
        "candidate_uploaded": False,
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--witness", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--out", type=Path, default=Path("evidence/registry_saturation_blocker.json"))
    args = parser.parse_args()
    result = audit(args.witness)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))
    return 2 if result["universal_overlap_blocker"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
