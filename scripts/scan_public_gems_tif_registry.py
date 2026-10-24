#!/usr/bin/env python3
"""Snapshot prediction-like GeoTIFF paths in the owner's public GEMSDOE repos.

This is a metadata inventory only: it records GitHub tree/blob identities and
sizes but does not download or decode raster bytes. Use it to reproduce the
scope of a later byte-level audit, not as a uniqueness clearance by itself.
Requires the GitHub CLI (`gh`) to be authenticated in the current environment.
"""
from __future__ import annotations

import argparse
import concurrent.futures
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote

OWNER = "buffedlizard55-lab"
REPO_PATTERN = re.compile(r"^(?:[0-9]+)?GEMSDOE(?:[0-9]+)?$", re.IGNORECASE)
EXCLUDE_SUBSTRINGS = (
    "/data/", "/inputs/", "/external/", "training_features", "sample_submission",
    "existing_faults", "labels.tif", "dem_", "lidar_scarp_features", "sgmc_faults",
    "h19_5", "d28.tif", "h27_4_solo",
)
PREDICTION_PATH_MARKERS = (
    "downloads", "submission", "release", "registry/rasters", "candidate",
    "prediction", "artifact", "raster",
)


def _gh_json(endpoint: str):
    proc = subprocess.run(
        ["gh", "api", endpoint], capture_output=True, text=True, check=False
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"gh api failed: {endpoint}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON from GitHub API for {endpoint}: {exc}") from exc


def is_candidate_like_path(path: str) -> bool:
    """Conservative path heuristic retained from the initial inventory scan."""
    q = path.lower()
    if q.startswith(("data/", "inputs/", ".cache/")):
        return False
    if any(marker in q for marker in EXCLUDE_SUBSTRINGS):
        return False
    return any(marker in q for marker in PREDICTION_PATH_MARKERS)


def public_owner_repositories(owner: str = OWNER) -> list[dict]:
    repos: list[dict] = []
    page = 1
    while True:
        batch = _gh_json(f"users/{owner}/repos?per_page=100&page={page}")
        if not isinstance(batch, list):
            raise RuntimeError(f"unexpected repository-list response on page {page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    selected = [
        r for r in repos
        if r.get("owner", {}).get("login", "").lower() == owner.lower()
        and not r.get("private", True)
        and REPO_PATTERN.fullmatch(r.get("name", ""))
    ]
    return sorted(selected, key=lambda r: r["name"].lower())


def scan_repo(repo: dict, owner: str = OWNER) -> dict:
    name = repo["name"]
    branch = repo.get("default_branch") or "main"
    tree_ref = quote(branch, safe="")
    endpoint = f"repos/{owner}/{name}/git/trees/{tree_ref}?recursive=1"
    try:
        tree = _gh_json(endpoint)
    except Exception as exc:
        return {"repo": name, "default_branch": branch, "error": str(exc), "tif_count": None,
                "candidate_tif_count": None, "candidate_tifs": []}
    all_tifs = [
        entry for entry in tree.get("tree", [])
        if entry.get("type") == "blob" and entry.get("path", "").lower().endswith((".tif", ".tiff"))
    ]
    candidate_tifs = []
    for entry in all_tifs:
        path = entry["path"]
        if not is_candidate_like_path(path):
            continue
        candidate_tifs.append({
            "path": path,
            "git_blob_sha": entry.get("sha"),
            "bytes": entry.get("size"),
            "blob_api_url": entry.get("url"),
        })
    return {
        "repo": name,
        "default_branch": branch,
        "tree_sha": tree.get("sha"),
        "tree_truncated": bool(tree.get("truncated", False)),
        "tif_count": len(all_tifs),
        "candidate_tif_count": len(candidate_tifs),
        "candidate_tifs": candidate_tifs,
    }


def build_inventory(owner: str = OWNER, workers: int = 8) -> dict:
    repositories = public_owner_repositories(owner)
    rows: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        for row in pool.map(lambda r: scan_repo(r, owner), repositories):
            rows.append(row)
            status = "ERROR " + row["error"] if "error" in row else (
                f"{row['candidate_tif_count']}/{row['tif_count']} candidate-like TIFFs"
                + (" (TREE TRUNCATED)" if row["tree_truncated"] else "")
            )
            print(f"{row['repo']}: {status}", file=sys.stderr, flush=True)

    blobs: dict[str, dict] = {}
    candidate_path_count = 0
    for row in rows:
        for tif in row.get("candidate_tifs", []):
            candidate_path_count += 1
            sha = tif.get("git_blob_sha")
            if not sha:
                continue
            b = blobs.setdefault(sha, {"git_blob_sha": sha, "bytes": tif.get("bytes"), "sources": []})
            if b.get("bytes") != tif.get("bytes"):
                b.setdefault("size_conflicts", []).append({"repo": row["repo"], "path": tif["path"], "bytes": tif.get("bytes")})
            b["sources"].append({"repo": row["repo"], "branch": row.get("default_branch"), "path": tif["path"]})
    unique_blobs = sorted(blobs.values(), key=lambda b: b["git_blob_sha"])
    for blob in unique_blobs:
        blob["sources"].sort(key=lambda s: (s["repo"].lower(), s["path"].lower()))

    errors = [r for r in rows if "error" in r]
    truncated = [r["repo"] for r in rows if r.get("tree_truncated")]
    return {
        "schema_version": 1,
        "inventory_type": "metadata-only public-repository TIFF path inventory",
        "scanned_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "owner": owner,
        "repository_pattern": REPO_PATTERN.pattern,
        "public_repositories_scanned": len(repositories),
        "repo_tree_errors": errors,
        "truncated_repo_trees": truncated,
        "complete_tree_scan": not errors and not truncated and len(rows) == len(repositories),
        "candidate_path_filter": {
            "include_if_path_contains_any": list(PREDICTION_PATH_MARKERS),
            "exclude_if_path_starts_with": ["data/", "inputs/", ".cache/"],
            "exclude_if_path_contains_any": list(EXCLUDE_SUBSTRINGS),
            "warning": "A path heuristic, not an authoritative submission registry; review the recorded scope before treating it as complete.",
        },
        "tif_paths_total": sum(r.get("tif_count") or 0 for r in rows),
        "candidate_like_tif_paths": candidate_path_count,
        "unique_candidate_like_git_blobs": len(unique_blobs),
        "unique_candidate_like_blob_bytes": sum(b.get("bytes") or 0 for b in unique_blobs),
        "metadata_only": True,
        "decoded_or_correlated": False,
        "scope_limitations": [
            "Only publicly listed repositories matching the naming pattern were scanned.",
            "Private, deleted, unlinked, external, or non-owner repositories are out of scope.",
            "Candidate-like paths are selected by a heuristic and may include diagnostics or miss outputs with other names.",
            "Blob metadata is not a raster comparison; download, hash, open, and compare any relevant contents before claiming uniqueness.",
        ],
        "repositories": rows,
        "unique_candidate_like_blobs": unique_blobs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default=OWNER)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out", type=Path, default=Path("registry/public_gems_tif_inventory.json"))
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 16:
        parser.error("--workers must be between 1 and 16")
    inventory = build_inventory(args.owner, args.workers)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "out": str(args.out),
        "complete_tree_scan": inventory["complete_tree_scan"],
        "public_repositories_scanned": inventory["public_repositories_scanned"],
        "candidate_like_tif_paths": inventory["candidate_like_tif_paths"],
        "unique_candidate_like_git_blobs": inventory["unique_candidate_like_git_blobs"],
        "decoded_or_correlated": inventory["decoded_or_correlated"],
    }, indent=2))
    return 0 if inventory["complete_tree_scan"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
