#!/usr/bin/env python3
"""Stream every public GEMSDOE repository and build the compact registry cache.

Usage:  python scripts/build_registry_cache.py [--owners a,b,...] [--workers 2]

Discovers repositories with the GitHub API (``gh``), then streams one tarball
per repository from codeload.github.com.  Results: ``.cache/registry_v3/``
(``inventory.json`` + one summary per unique SHA-256).  Re-runs reuse cached
summaries.  Network: github.com / api.github.com / codeload.github.com only.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gems import registry_cache as rc  # noqa: E402

DEFAULT_OWNERS = ["buffedlizard55-lab", "kanlerxz87-cyber", "eugboogieman123-ops",
                  "wingbangboozle1-lang", "ginnymcfiner23-ux", "karagemop466-tech",
                  "apartanish22-droid", "sassnarep3-star"]
SAMPLE = ROOT / ".cache" / "gems_inputs" / "bridge" / "sample_submission.tif"


def discover(owner: str) -> list[dict]:
    raw = subprocess.check_output(["gh", "api", f"users/{owner}/repos?per_page=100", "--paginate",
                                   "--jq", ".[] | [.name, .default_branch, .size, .pushed_at] | @tsv"],
                                  timeout=120).decode()
    out = []
    for line in raw.splitlines():
        name, branch, size, pushed = line.split("\t")
        if "GEMSDOE" in name.upper():
            out.append(dict(owner=owner, repo=name, branch=branch, size_kb=int(size), pushed_at=pushed))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--owners", default=",".join(DEFAULT_OWNERS))
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--only", default="", help="comma list of repo names to (re)scan")
    args = ap.parse_args()
    fp = rc.load_footprint(SAMPLE)
    repos = []
    for owner in args.owners.split(","):
        repos.extend(discover(owner))
    if args.only:
        keep = set(args.only.split(","))
        repos = [r for r in repos if r["repo"] in keep]
    repos = [r for r in repos if r["size_kb"] > 0]
    print(f"{len(repos)} non-empty repositories to stream", flush=True)
    rc.CACHE.mkdir(parents=True, exist_ok=True)
    results, errors = [], []

    def run(r):
        t0 = time.time()
        for attempt in range(3):
            try:
                res = rc.stream_repo(r["owner"], r["repo"], r["branch"], fp)
                res.update(size_kb=r["size_kb"], pushed_at=r["pushed_at"], seconds=round(time.time() - t0, 1))
                return res
            except Exception as exc:  # noqa: BLE001
                err = f"{type(exc).__name__}: {exc}"
                time.sleep(5 * (attempt + 1))
        return dict(owner=r["owner"], repo=r["repo"], branch=r["branch"], error=err)

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for res in ex.map(run, repos):
            if "error" in res:
                errors.append(res)
                print(f"ERROR {res['owner']}/{res['repo']}: {res['error']}", flush=True)
            else:
                results.append(res)
                print(f"{res['owner']}/{res['repo']}: {len(res['files'])} rasters, "
                      f"{len(res['skipped'])} skipped, {res['seconds']}s", flush=True)
    inv_path = rc.CACHE / ("inventory.json" if not args.only else f"inventory_partial_{int(time.time())}.json")
    inv = dict(schema="gemsdoe92-registry-v3", built_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
               owners=args.owners.split(","), repositories=results, errors=errors,
               footprint_cells=fp.n, top_cap=rc.TOP_CAP, sample_n=rc.SAMPLE_N, sample_seed=rc.SAMPLE_SEED)
    inv_path.write_text(json.dumps(inv, indent=1), encoding="utf-8")
    n_files = sum(len(r["files"]) for r in results)
    uniq = {f["sha256"] for r in results for f in r["files"]}
    print(f"DONE {len(results)} repos, {n_files} grid rasters, {len(uniq)} unique SHA-256, "
          f"{len(errors)} errors -> {inv_path}", flush=True)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
