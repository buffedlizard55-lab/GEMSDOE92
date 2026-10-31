#!/usr/bin/env python3
"""Build the public-registry uniqueness index OFFLINE from the prefetched cache.

This exists because ``scripts/build_public_registry_index.py`` needs live GitHub
REST calls (``users/<owner>/repos``) and those are rate-limited (5,000/hour,
shared across concurrent sessions). It re-uses the shared helpers in
``scripts/audit_public_registry.py`` -- ``_is_submission_tif_path`` and
``classify_and_extract_dots`` come from the shared module so the dot-set
definition is never forked -- and only reads the blobs that
``scripts/prefetch_public_registry.py`` already staged and Git-blob-SHA verified
in ``.cache/gemsdoe_public_registry``.

Outputs, in ``.cache/registry_index`` (gitignored, snapshot-excluded):

* ``dots_<sha256>.npy``  int32 flat indices of each raster's dot set
* ``ranks.npy``          float32 centred unit-norm rank vectors on a fixed
                         100,000-pixel footprint subsample (Spearman = dot product)
* ``meta.json``          provenance: repo, branch, path, Git blob SHA-1,
                         SHA-256, positive support, representation
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]

import audit_public_registry as apr  # noqa: E402
from build_public_registry_index import (  # noqa: E402
    DOT_FIELD_MAX, N_SUB, OUT, SUB_SEED, TOP_K, classify_and_extract_dots,
)

CACHE = apr.CACHE
REF = ROOT / ".cache" / "gems_inputs" / "bridge" / "sample_submission.tif"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with rasterio.open(REF) as ds:
        expected = (ds.shape, ds.crs, ds.transform)
        foot = np.isfinite(ds.read(1))
    foot_idx = np.flatnonzero(foot.ravel())
    sub = np.sort(np.random.default_rng(SUB_SEED).choice(foot_idx, N_SUB, replace=False))
    np.save(OUT / "sub_idx.npy", sub)

    inv_path = CACHE / "repo_inventory.json"
    if not inv_path.is_file():
        print(f"ERROR: {inv_path} missing; run scripts/prefetch_public_registry.py first", file=sys.stderr)
        return 2
    inventory = json.loads(inv_path.read_text(encoding="utf-8"))

    items, seen = [], set()
    for entry in inventory:
        for f in entry.get("tifs", []):
            if not apr._is_submission_tif_path(f["path"]):
                continue
            sha = f["sha"]
            if sha in seen:
                continue
            seen.add(sha)
            items.append({
                "owner": entry.get("owner") or apr.OWNER,
                "repo": entry["repo"], "branch": entry.get("branch"),
                "path": f["path"], "git_sha": sha, "bytes": f["size"],
                "local_path": str(CACHE / f"{sha}.tif"),
            })

    t0 = time.time()
    meta, ranks, skipped = [], [], []
    for i, f in enumerate(items):
        p = Path(f["local_path"])
        if not p.is_file() or p.stat().st_size != f["bytes"]:
            skipped.append(dict(path=f"{f['owner']}/{f['repo']}/{f['path']}", reason="blob not cached"))
            continue
        try:
            with rasterio.open(p) as ds:
                if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected:
                    skipped.append(dict(path=f"{f['owner']}/{f['repo']}/{f['path']}", reason="grid/band mismatch"))
                    continue
                v = ds.read(1).astype(np.float32)
        except Exception as exc:  # unreadable/odd encodings are logged, not hidden
            skipped.append(dict(path=f"{f['owner']}/{f['repo']}/{f['path']}", reason=str(exc)[:120]))
            continue
        v = np.nan_to_num(v, nan=0.0, posinf=0.0, neginf=0.0)
        v[~foot] = 0.0
        flat = v.ravel()
        pos = np.flatnonzero(flat > 0)
        if pos.size == 0:
            skipped.append(dict(path=f"{f['owner']}/{f['repo']}/{f['path']}", reason="empty in footprint"))
            continue
        sha = sha256_file(p)
        rep, dots, tie_truncated, distinct_vals = classify_and_extract_dots(flat, pos)
        np.save(OUT / f"dots_{sha}.npy", dots)
        sv = flat[sub].astype(np.float64)
        r = rankdata(sv)
        r -= r.mean()
        nrm = np.linalg.norm(r)
        ranks.append((r / nrm).astype(np.float32) if nrm > 0 else np.zeros(N_SUB, np.float32))
        meta.append(dict(owner=f["owner"], repo=f["repo"], branch=f["branch"], path=f["path"],
                         git_sha=f["git_sha"], sha256=sha, positive_support=int(pos.size),
                         representation=rep, indexed_dots=int(dots.size),
                         tie_truncated=bool(tie_truncated), distinct_values=distinct_vals))
        if (i + 1) % 250 == 0:
            print(f"  [{time.time()-t0:6.0f}s] {i+1}/{len(items)}", flush=True)

    np.save(OUT / "ranks.npy", np.stack(ranks) if ranks else np.zeros((0, N_SUB), np.float32))
    doc = dict(built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               builder="scripts/gx_registry_index.py (offline; no REST calls)",
               source_inventory=str(inv_path), owners=list(apr.DEFAULT_OWNERS),
               repos_scanned=len(inventory), unique_blobs=len(items), indexed=len(meta),
               skipped=skipped, dot_field_max=DOT_FIELD_MAX, top_k=TOP_K,
               n_sub=N_SUB, sub_seed=SUB_SEED, meta=meta)
    (OUT / "meta.json").write_text(json.dumps(doc, indent=1))
    print(f"indexed={len(meta)} skipped={len(skipped)} ({time.time()-t0:.0f}s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
