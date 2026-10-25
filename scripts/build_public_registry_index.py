#!/usr/bin/env python3
"""Download + index every public GEMSDOE* competition-grid raster (owner repos).

Builds a compact, reusable uniqueness index in ``.cache/registry_index/``
(snapshot-excluded) so that any candidate can be screened against the whole
public registry in seconds:

* ``dots_<sha>.npy``  -- int32 flat indices of the raster's *dot set*:
    - ``dot_field`` (positive support <= ``DOT_FIELD_MAX`` px): every positive pixel;
    - ``continuous_surface`` (larger support): the top ``TOP_K`` pixels by value,
      ordered best-first, so a matched-budget dot set is a prefix slice.
* ``ranks.npy``       -- float32 centred unit-norm rank vectors on a fixed
  100,000-pixel footprint subsample (Spearman = dot product).
* ``meta.json``       -- provenance: repo, branch, path, Git blob SHA-1 (verified),
  SHA-256, positive support, representation.

Git blob SHA-1 + byte length are verified for every download (fail closed).
Only single-band rasters on the exact sample-submission grid are indexed.
Re-uses ``get_repositories``/``tree_for``/``fetch_blob`` from
``scripts/audit_public_registry.py`` (shared tool, not a fork).
"""
from __future__ import annotations

import concurrent.futures
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
import audit_public_registry as apr  # noqa: E402

OUT = ROOT / ".cache" / "registry_index"
REF = ROOT / ".cache" / "gems_inputs" / "bridge" / "sample_submission.tif"
DOT_FIELD_MAX = 150_000
TOP_K = 200_000
N_SUB = 100_000
SUB_SEED = 20261025


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    apr.CACHE.mkdir(parents=True, exist_ok=True)
    with rasterio.open(REF) as ds:
        expected = (ds.shape, ds.crs, ds.transform)
        foot = np.isfinite(ds.read(1))
    foot_idx = np.flatnonzero(foot.ravel())
    sub = np.sort(np.random.default_rng(SUB_SEED).choice(foot_idx, N_SUB, replace=False))
    np.save(OUT / "sub_idx.npy", sub)

    t0 = time.time()
    repos = apr.get_repositories()
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        trees = list(ex.map(apr.tree_for, repos))
    items, seen = [], set()
    for t in trees:
        for f in t["files"]:
            if f["git_sha"] not in seen:
                seen.add(f["git_sha"])
                items.append(f)
    print(f"repos={len(repos)} unique_blobs={len(items)} ({time.time()-t0:.0f}s)", flush=True)
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        fetched = list(ex.map(apr.fetch_blob, items))
    errors = [f for f in fetched if "error" in f]
    print(f"fetched ok={len(fetched)-len(errors)} errors={len(errors)} ({time.time()-t0:.0f}s)", flush=True)

    meta, ranks, skipped = [], [], []
    for f in fetched:
        if "error" in f:
            skipped.append(dict(path=f"{f['repo']}/{f['path']}", reason=f["error"][:120]))
            continue
        try:
            with rasterio.open(f["local_path"]) as ds:
                if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected:
                    skipped.append(dict(path=f"{f['repo']}/{f['path']}", reason="grid/band mismatch"))
                    continue
                v = ds.read(1).astype(np.float32)
        except Exception as exc:  # unreadable/odd encodings are logged, not hidden
            skipped.append(dict(path=f"{f['repo']}/{f['path']}", reason=str(exc)[:120]))
            continue
        v = np.nan_to_num(v, nan=0.0, posinf=0.0, neginf=0.0)
        v[~foot] = 0.0
        flat = v.ravel()
        pos = np.flatnonzero(flat > 0)
        if pos.size == 0:
            skipped.append(dict(path=f"{f['repo']}/{f['path']}", reason="empty in footprint"))
            continue
        sha = f["sha256"]
        if pos.size <= DOT_FIELD_MAX:
            rep, dots = "dot_field", pos.astype(np.int32)
        else:
            rep = "continuous_surface"
            k = min(TOP_K, pos.size)
            part = np.argpartition(-flat[pos], k - 1)[:k]
            order = np.lexsort((pos[part], -flat[pos][part]))  # value desc, index asc (deterministic ties)
            dots = pos[part][order].astype(np.int32)
        np.save(OUT / f"dots_{sha}.npy", dots)
        sv = flat[sub].astype(np.float64)
        r = np.argsort(np.argsort(sv, kind="stable"), kind="stable").astype(np.float64)
        # average ties properly
        from scipy.stats import rankdata
        r = rankdata(sv)
        r -= r.mean()
        nrm = np.linalg.norm(r)
        ranks.append((r / nrm).astype(np.float32) if nrm > 0 else np.zeros(N_SUB, np.float32))
        meta.append(dict(repo=f["repo"], branch=f["branch"], path=f["path"], git_sha=f["git_sha"],
                         sha256=sha, positive_support=int(pos.size), representation=rep,
                         distinct_values=int(min(np.unique(flat[pos][:200000]).size, 10**6))))
    np.save(OUT / "ranks.npy", np.stack(ranks) if ranks else np.zeros((0, N_SUB), np.float32))
    doc = dict(built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), owner=apr.OWNER,
               repos_scanned=len(repos), unique_blobs=len(items), indexed=len(meta),
               skipped=skipped, tree_errors=[dict(repo=t["repo"], error=t["error"]) for t in trees if t.get("error")],
               truncated_trees=[t["repo"] for t in trees if t.get("truncated")],
               dot_field_max=DOT_FIELD_MAX, top_k=TOP_K, n_sub=N_SUB, sub_seed=SUB_SEED, meta=meta)
    (OUT / "meta.json").write_text(json.dumps(doc, indent=1))
    print(f"indexed={len(meta)} skipped={len(skipped)} ({time.time()-t0:.0f}s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
