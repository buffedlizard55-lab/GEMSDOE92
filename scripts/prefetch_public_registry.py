#!/usr/bin/env python3
"""Prefetch the public GEMSDOE registry inventory + blobs into .cache only.

Reuses scripts/audit_public_registry.py primitives (shared tool, no fork of
comparison logic). This performs ONLY the network staging half so that the
binding comparison (`audit_public_registry.py --cache-only`) can run after the
candidate TIF exists without re-downloading ~1,400 blobs.
"""
from __future__ import annotations

import concurrent.futures
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts")]

from audit_public_registry import (  # noqa: E402
    CACHE, fetch_blob, get_repositories, tree_for,
)


def main() -> int:
    t0 = time.time()
    CACHE.mkdir(parents=True, exist_ok=True)
    repos = get_repositories()
    print(f"[{time.time()-t0:7.1f}s] {len(repos)} public GEMSDOE repos", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        tree_results = list(pool.map(tree_for, repos))
    errs = [t for t in tree_results if t.get("error") or t.get("truncated")]
    if errs:
        print(f"WARNING: {len(errs)} tree errors/truncations: "
              f"{[t['repo'] for t in errs]}", flush=True)
    (CACHE / "repo_inventory.json").write_text(json.dumps([
        {"repo": t["repo"], "branch": t.get("branch"),
         "truncated": t.get("truncated", False), "error": t.get("error"),
         "tifs": [{"path": f["path"], "sha": f["git_sha"], "size": f["bytes"]}
                  for f in t.get("files", [])]}
        for t in tree_results], indent=2), encoding="utf-8")
    paths = [f for t in tree_results for f in t["files"]]
    unique = {}
    for item in paths:
        unique.setdefault(item["git_sha"], item)
    print(f"[{time.time()-t0:7.1f}s] {len(paths)} TIFF paths, {len(unique)} unique blobs; fetching...",
          flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        fetched = list(pool.map(fetch_blob, unique.values()))
    bad = [f for f in fetched if "error" in f]
    print(f"[{time.time()-t0:7.1f}s] fetched {len(fetched)-len(bad)} OK, {len(bad)} errors", flush=True)
    for f in bad[:20]:
        print("  ERR", f["repo"], f["path"], f["error"][:100], flush=True)
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
