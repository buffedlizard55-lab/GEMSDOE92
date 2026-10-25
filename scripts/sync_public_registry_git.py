#!/usr/bin/env python3
"""Populate .cache/gemsdoe_public_registry/ using Git Smart HTTP (zero REST blob/tree quota).

Fixes the rate-limit bottleneck documented in docs/NEXT_STEPS.md Item #1:
instead of issuing ~1,520 GitHub REST API calls (`gh api .../git/trees/...` +
`.../git/blobs/...`), this utility clones each `buffedlizard55-lab/*GEMSDOE*`
default branch with `--depth=1 --filter=blob:none --no-checkout -c gc.auto=0`,
reads Git blob SHA-1s instantaneously via `git ls-tree -r -z HEAD` (without `-l`,
which would lazily fetch non-TIFF blobs), sparse-checks out only `.tif` blobs
not yet in `.cache/gemsdoe_public_registry/<sha>.tif`, and verifies
`git_blob_sha(data) == sha` byte-for-byte.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNER = "buffedlizard55-lab"
CACHE = ROOT / ".cache" / "gemsdoe_public_registry"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def discover_repos_api() -> list[dict] | None:
    try:
        raw = subprocess.check_output(
            ["gh", "api", f"users/{OWNER}/repos?per_page=100", "--paginate", "--jq", ".[]"],
            stderr=subprocess.DEVNULL,
            timeout=60,
        )
        repos = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
        return [
            {"name": r["name"], "default_branch": r["default_branch"]}
            for r in sorted(repos, key=lambda x: x["name"])
            if "GEMSDOE" in r["name"].upper()
        ]
    except Exception:
        return None


def discover_repos_git_ls_remote(workers: int = 16) -> list[dict]:
    candidates = sorted(
        {f"GEMSDOE{i}" for i in range(1, 120)}
        | {f"{i}GEMSDOE" for i in range(1, 120)}
        | {"GEMSDOE", "LEARNGEMSDOE"}
    )

    def probe(name: str) -> dict | None:
        url = f"https://github.com/{OWNER}/{name}.git"
        proc = subprocess.run(
            ["git", "ls-remote", "--symref", url, "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            return None
        branch = "main"
        for line in proc.stdout.splitlines():
            if line.startswith("ref: refs/heads/") and "\tHEAD" in line:
                branch = line.split("ref: refs/heads/", 1)[1].split("\t", 1)[0]
        return {"name": name, "default_branch": branch}

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        found = [r for r in pool.map(probe, candidates) if r is not None]
    return sorted(found, key=lambda x: x["name"])


def is_submission_tif(path_str: str) -> bool:
    low = path_str.lower()
    if not low.endswith((".tif", ".tiff")):
        return False
    in_sub = low.startswith("submission") or "/submission" in low
    return "docs/downloads/" in low or low.startswith("releases/") or in_sub


def sync_one_repo(repo_info: dict) -> dict:
    name = repo_info["name"]
    branch = repo_info["default_branch"]
    url = f"https://github.com/{OWNER}/{name}.git"
    try:
        with tempfile.TemporaryDirectory(dir=CACHE) as td:
            co = Path(td) / "co"
            subprocess.run(
                [
                    "git",
                    "-c",
                    "gc.auto=0",
                    "clone",
                    "--quiet",
                    "--depth=1",
                    "--branch",
                    branch,
                    "--filter=blob:none",
                    "--no-checkout",
                    url,
                    str(co),
                ],
                check=True,
                timeout=120,
            )
            ls_out = subprocess.check_output(
                ["git", "-C", str(co), "ls-tree", "-r", "-z", "HEAD"],
                timeout=30,
            ).decode("utf-8", errors="surrogateescape")

            tif_candidates: list[tuple[str, str]] = []
            missing_paths: list[tuple[str, str]] = []
            for rec in ls_out.split("\0"):
                if not rec:
                    continue
                meta, path_str = rec.split("\t", 1)
                parts = meta.split()
                if len(parts) < 3 or parts[1] != "blob":
                    continue
                sha = parts[2]
                if not is_submission_tif(path_str):
                    continue
                tif_candidates.append((path_str, sha))
                target = CACHE / f"{sha}.tif"
                if not target.is_file():
                    missing_paths.append((path_str, sha))

            if missing_paths:
                subprocess.run(
                    ["git", "-C", str(co), "-c", "gc.auto=0", "sparse-checkout", "init", "--no-cone"],
                    check=True,
                    timeout=30,
                )
                unique_paths = sorted({"/" + p for p, _ in missing_paths})
                subprocess.run(
                    ["git", "-C", str(co), "-c", "gc.auto=0", "sparse-checkout", "set", "--no-cone", *unique_paths],
                    check=True,
                    timeout=180,
                )
                subprocess.run(
                    ["git", "-C", str(co), "-c", "gc.auto=0", "checkout", "--quiet", "HEAD"],
                    check=True,
                    timeout=180,
                )
                for path_str, sha in missing_paths:
                    target = CACHE / f"{sha}.tif"
                    if target.is_file():
                        continue
                    data = (co / path_str).read_bytes()
                    if git_blob_sha(data) != sha:
                        raise ValueError(f"SHA mismatch for {name}:{path_str} ({sha})")
                    tmp_target = CACHE / f".tmp.{sha}.{name}.tif"
                    tmp_target.write_bytes(data)
                    shutil.move(str(tmp_target), str(target))

            tifs: list[dict] = []
            for path_str, sha in tif_candidates:
                target = CACHE / f"{sha}.tif"
                size = target.stat().st_size
                tifs.append({"path": path_str, "sha": sha, "size": size})

            return {
                "repo": name,
                "branch": branch,
                "truncated": False,
                "error": None,
                "tifs": tifs,
            }
    except Exception as exc:
        return {
            "repo": name,
            "branch": branch,
            "truncated": False,
            "error": str(exc),
            "tifs": [],
        }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    t0 = time.time()
    CACHE.mkdir(parents=True, exist_ok=True)
    repos = discover_repos_api()
    source = "gh api users/repos + Git Smart HTTP"
    if repos is None:
        repos = discover_repos_git_ls_remote(workers=min(16, args.workers * 2))
        source = "git ls-remote + Git Smart HTTP (zero REST API)"
    print(f"Discovered {len(repos)} {OWNER}/*GEMSDOE* repositories via {source}", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(sync_one_repo, repos))

    results.sort(key=lambda r: r["repo"])
    errors = [r for r in results if r.get("error")]
    n_paths = sum(len(r["tifs"]) for r in results)
    unique_shas = {f["sha"] for r in results for f in r["tifs"]}
    cached_ok = sum(1 for sha in unique_shas if (CACHE / f"{sha}.tif").is_file())

    inv_path = CACHE / "repo_inventory.json"
    inv_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    dt = time.time() - t0
    print(
        f"Synced {len(results)} repos ({len(errors)} errors), "
        f"{n_paths} TIFF paths, {cached_ok}/{len(unique_shas)} unique blobs in {dt:.1f}s -> {inv_path}",
        flush=True,
    )
    if errors:
        for e in errors[:10]:
            print(f"  ERROR {e['repo']}: {e['error']}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
