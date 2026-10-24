#!/usr/bin/env python3
"""Download-only phase of the public-registry audit (no candidate required).

Re-uses the verified helpers in ``scripts/audit_public_registry.py`` (git blob
SHA-1 + byte-length verification, same TIFF-path selection) so a session can
populate the gitignored ``.cache/gemsdoe_public_registry/`` once and then
compare *any* number of candidates offline with ``scripts/registry_gate.py``.

Scope is unchanged from the audit script: current default branches of the
owner's public repositories whose name contains GEMSDOE; TIFF paths under
``docs/downloads/``, ``releases/`` and ``submission*`` directories; unique git
blobs.  It is NOT an exhaustive inventory (history, private repos, other owners,
ZIP-only or site-only objects are out of scope) and says so in its output.

Writes (all under .cache/, never tracked):
  repo_inventory.json   per-repo TIFF tree listing (cache-only mode input)
  registry_index.json   rasters on the exact competition grid, single band
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]

import rasterio  # noqa: E402

import audit_public_registry as aud  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--cache-only", action="store_true",
                    help="reuse the cached inventory; make no GitHub API requests")
    args = ap.parse_args()

    cache = aud.CACHE
    cache.mkdir(parents=True, exist_ok=True)
    inv_path = cache / "repo_inventory.json"
    t0 = time.time()
    if args.cache_only:
        tree_results, repos = aud.read_cached_trees(inv_path)
        source = "cached inventory"
    else:
        repos = aud.get_repositories()
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            tree_results = list(pool.map(aud.tree_for, repos))
        bad = [t for t in tree_results if t.get("error") or t.get("truncated")]
        if bad:
            print("WARNING: failed/truncated trees:", [(b["repo"], b.get("error")) for b in bad], file=sys.stderr)
        inv_path.write_text(json.dumps([
            {"repo": t["repo"], "branch": t.get("branch"), "truncated": t.get("truncated", False),
             "error": t.get("error"),
             "tifs": [{"path": f["path"], "sha": f["git_sha"], "size": f["bytes"]} for f in t.get("files", [])]}
            for t in tree_results], indent=2), encoding="utf-8")
        source = "live GitHub API"
    paths = [f for r in tree_results for f in r["files"]]
    unique = {}
    for item in paths:
        unique.setdefault(item["git_sha"], item)
    print(f"[{source}] {len(repos)} repos, {len(paths)} TIFF paths, {len(unique)} unique blobs", flush=True)

    done = 0
    fetched = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(aud.fetch_blob, it, cache_only=args.cache_only) for it in unique.values()]
        for fu in concurrent.futures.as_completed(futs):
            fetched.append(fu.result())
            done += 1
            if done % 100 == 0:
                print(f"  fetched {done}/{len(unique)}  ({time.time() - t0:.0f}s)", flush=True)
    errors = [x for x in fetched if "error" in x]

    with rasterio.open(ROOT / "data" / "bridge" / "sample_submission.tif") as ref:
        expected = (ref.shape, ref.crs, ref.transform)
    compatible, excl = [], {"not_single_band_or_grid_mismatch": 0, "invalid_tiff": 0}
    for it in fetched:
        if "error" in it:
            continue
        try:
            with rasterio.open(it["local_path"]) as ds:
                if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected:
                    excl["not_single_band_or_grid_mismatch"] += 1
                    continue
            compatible.append(it)
        except Exception:
            excl["invalid_tiff"] += 1
    rows = [{"repo_first": f["repo"], "sources": [f["repo"] + "/" + f["path"]],
             "cache_file": f["local_path"], "sha256": f["sha256"], "git_sha": f["git_sha"], "bytes": f["bytes"]}
            for f in sorted(compatible, key=lambda z: (z["repo"], z["path"]))]
    tree_errors = [t for t in tree_results if t.get("error")]
    complete = (not errors and not tree_errors and not any(t.get("truncated") for t in tree_results)
                and bool(compatible) and excl["invalid_tiff"] == 0 and len(tree_results) == len(repos))
    index = {"schema": "gemsdoe92-public-submission-registry.v1", "complete_accessible_scan": complete,
             "n_rasters": len(rows), "rasters": rows, "exclusions": excl,
             "errors": [*errors, *tree_errors],
             "scope": ("Current public default branches of owner repos whose name contains GEMSDOE; TIFF paths under "
                       "docs/downloads/, releases/, submission*; unique git blobs. Not organizer-complete.")}
    (cache / "registry_index.json").write_text(json.dumps(index), encoding="utf-8")
    print(json.dumps({"repos": len(repos), "tiff_paths": len(paths), "unique_blobs": len(unique),
                      "downloaded_ok": len(fetched) - len(errors), "download_errors": len(errors),
                      "single_band_template_grid": len(rows), "exclusions": excl,
                      "complete_accessible_scan": complete, "seconds": round(time.time() - t0)}, indent=2))
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
