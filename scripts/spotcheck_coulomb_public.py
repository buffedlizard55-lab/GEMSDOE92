#!/usr/bin/env python3
"""Public-registry spot-check for the COULOMB lane (2026-10-24 session).

Fetches 5 hash-pinned public blobs (the binding 17GEMSDOE dense witness + the
4 top sparse witnesses that tripped STRAINBREAK f60) via the GitHub API into
gitignored .cache/, verifies Git blob SHA-1 + grid match, and measures forward
3-px overlap + full-footprint Spearman for all 3 COULOMB arms.

This is a DIAGNOSTIC spot-check, not a full-registry scan: a pass here grants
no clearance, and the dense-witness stop (if reproduced) is binding. Full
102-repo scan was not run this session (3-experiment budget consumed on the
holdout-negative COULOMB family); recorded as NOT clearance in the run card.

Writes evidence/coulomb_public_spotcheck.json.
"""
from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache/coulomb_public_spotcheck"
OUT = ROOT / "evidence/coulomb_public_spotcheck.json"

# (repo, path, git blob sha) -- pins inherited from verified prior receipts.
WITNESSES = [
    ("buffedlizard55-lab/17GEMSDOE",
     "docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif",
     "374c88b1da2b803e2ed160de467fd71ae114010d", "dense"),
    ("buffedlizard55-lab/62GEMSDOE",
     "docs/downloads/gems62b-tiltgrad-vote-scarpcorrob-120000-zeros.tif",
     "800e27139c0a4664de786706a4a4d2a0a8862b89", "sparse120k"),
    ("buffedlizard55-lab/GEMSDOE23",
     "docs/downloads/gemsdoe23-h30-arrangement-matched-habitat-20261002-0d4e02e8-allfinite.tif",
     "1cd1123a6a2d963c7145f8bf006fae75fdac4833", "sparse91k"),
    ("buffedlizard55-lab/GEMSDOE23",
     "docs/downloads/gemsdoe23-h29-dealiased-habitat-20261002-7bf9fac6-allfinite.tif",
     "7d19b90ed6e358b14b561bc405690a104c5da64b", "sparse100k"),
    ("buffedlizard55-lab/GEMSDOE23",
     "docs/downloads/gemsdoe23-h24-dispersed-habitat-20261002-ada8df14-allfinite.tif",
     "1374c17668adc23d0ab1c67ee07187bbe48f007b", "sparse100k"),
]


def git_blob_sha(p: Path) -> str:
    h = hashlib.sha1(b"blob " + str(p.stat().st_size).encode() + b"\0")
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_blob(repo: str, sha: str, dest: Path) -> None:
    if dest.is_file() and git_blob_sha(dest) == sha:
        print(f"cache hit {dest.name}", flush=True)
        return
    print(f"fetching {repo}@{sha[:8]} ...", flush=True)
    out = subprocess.run(
        ["gh", "api", f"repos/{repo}/git/blobs/{sha}", "--jq", ".content"],
        capture_output=True, text=True, check=True, cwd=ROOT)
    raw = base64.b64decode("".join(out.stdout.split()))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    got = git_blob_sha(dest)
    assert got == sha, f"blob sha mismatch: {got} != {sha}"


def main() -> int:
    variants = json.loads((ROOT / "evidence/coulomb_variants.json").read_text())["variants"]
    with rasterio.open(ROOT / "data/bridge/sample_submission.tif") as ds:
        ref_shape, ref_crs, ref_tr = (ds.height, ds.width), ds.crs, ds.transform
        foot = np.isfinite(ds.read(1))
    arms = {}
    for v in variants:
        with rasterio.open(ROOT / v["file_zeros"]) as ds:
            a = ds.read(1)
        assert np.isfinite(a).all() and a.min() >= 0 and a.max() <= 1
        arms[v["value"]] = ((a > 0) & foot)
    results = []
    for repo, path, sha, kind in WITNESSES:
        dest = CACHE / f"{repo.split('/')[-1]}__{Path(path).name}"
        fetch_blob(repo, sha, dest)
        with rasterio.open(dest) as ds:
            assert (ds.height, ds.width) == ref_shape and ds.crs == ref_crs \
                and ds.transform == ref_tr and ds.count == 1, f"grid mismatch {dest.name}"
            w = ds.read(1)
        support = (np.nan_to_num(w, nan=0.0) > 0) & foot
        n_pos = int(support.sum())
        d_wit = distance_transform_edt(~support)
        w_flat = np.nan_to_num(w, nan=0.0)[foot].astype(np.float64)
        row = {"raster": f"{repo.split('/')[-1]}/{path}", "kind": kind,
               "git_blob_sha": sha, "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
               "bytes": dest.stat().st_size, "positive_pixels": n_pos,
               "arms": {}}
        for name, mask in arms.items():
            fwd = float(np.mean(d_wit[mask] <= 3.0))
            with rasterio.open(ROOT / [v["file_zeros"] for v in variants
                                       if v["value"] == name][0]) as ds:
                c_flat = ds.read(1)[foot].astype(np.float64)
            rho = float(spearmanr(c_flat, w_flat).statistic)
            row["arms"][name] = {"forward_3px": round(fwd, 6),
                                 "spearman_full_footprint": round(rho, 6) if np.isfinite(rho) else None}
        results.append(row)
        print(row["raster"], {k: v["forward_3px"] for k, v in row["arms"].items()}, flush=True)
    OUT.write_text(json.dumps({
        "evidence_class": "REGISTRY-DIAGNOSTIC (5-witness spot-check; NOT a full scan; grants no clearance)",
        "full_102_repo_scan_run_this_session": False,
        "full_scan_note": ("Not run: 3-experiment budget consumed; COULOMB family is holdout-negative "
                           "vs the 0.008549 bar, so no verdict depends on it. Absence of a full scan "
                           "is recorded as NOT clearance."),
        "results": results,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
