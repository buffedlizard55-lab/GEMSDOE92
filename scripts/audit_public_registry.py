#!/usr/bin/env python3
"""Audit candidate uniqueness against current public GEMSDOE owner-repo rasters.

Requires the GitHub CLI (``gh``) to have working API access. Scans current
(default-branch) public repositories whose names contain GEMSDOE, downloads
unique Git blobs from submission-oriented TIFF directories into ignored
``.cache/``, verifies Git blob SHA-1 and bytes, then compares only single-band
rasters on the exact competition grid. This is intentionally not described as
an exhaustive inventory of old branches, other owners, ZIP-only assets, or
unlinked GitHub Pages objects.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import grid as grid_mod  # noqa: E402
from vendor.gems57.uniqueness import _near, compare_array_to_registry  # noqa: E402

OWNER = "buffedlizard55-lab"
CACHE = ROOT / ".cache" / "gemsdoe_public_registry"

def gh_bytes(*args: str, timeout: int = 120) -> bytes:
    return subprocess.check_output(["gh", "api", *args], stderr=subprocess.STDOUT, timeout=timeout)


def get_repositories() -> list[dict]:
    raw = gh_bytes(f"users/{OWNER}/repos?per_page=100", "--paginate", "--jq", ".[]")
    repos = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    return [r for r in repos if "GEMSDOE" in r["name"].upper()]


def tree_for(repo: dict) -> dict:
    try:
        branch = quote(repo["default_branch"], safe="")
        raw = gh_bytes(f"repos/{OWNER}/{repo['name']}/git/trees/{branch}?recursive=1")
        doc = json.loads(raw)
        selected = []
        for node in doc.get("tree", []):
            p = node.get("path", "")
            low = p.lower()
            if node.get("type") != "blob" or not low.endswith((".tif", ".tiff")):
                continue
            in_submission_path = low.startswith("submission") or "/submission" in low
            if "docs/downloads/" in low or low.startswith("releases/") or in_submission_path:
                selected.append({"repo": repo["name"], "branch": repo["default_branch"],
                                 "path": p, "git_sha": node["sha"], "bytes": int(node["size"])})
        return {"repo": repo["name"], "branch": repo["default_branch"],
                "truncated": bool(doc.get("truncated", False)), "files": selected}
    except Exception as exc:
        return {"repo": repo["name"], "branch": repo.get("default_branch"),
                "truncated": False, "files": [], "error": str(exc)}


def read_cached_trees(path: Path) -> tuple[list[dict], list[dict]]:
    if not path.is_file():
        raise FileNotFoundError(f"cached inventory missing: {path}")
    cached = json.loads(path.read_text(encoding="utf-8"))
    tree_results = []
    for item in cached:
        tree_results.append({"repo": item["repo"], "branch": item["branch"],
                             "truncated": item.get("truncated", False), "error": item.get("error"),
                             "files": [{"repo": item["repo"], "branch": item["branch"],
                                        "path": f["path"], "git_sha": f["sha"], "bytes": f["size"]}
                                       for f in item.get("tifs", [])
                                       if "docs/downloads/" in f["path"].lower()
                                       or f["path"].lower().startswith("releases/")
                                       or f["path"].lower().startswith("submission")
                                       or "/submission" in f["path"].lower()]})
    repos = [{"name": t["repo"], "default_branch": t["branch"]} for t in tree_results]
    return tree_results, repos


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def fetch_blob(item: dict, *, cache_only: bool = False) -> dict:
    sha = item["git_sha"]
    target = CACHE / f"{sha}.tif"
    try:
        if target.exists():
            data = target.read_bytes()
        else:
            if cache_only:
                raise FileNotFoundError("blob absent in cache-only mode")
            data = gh_bytes("-H", "Accept: application/vnd.github.raw",
                            f"repos/{OWNER}/{item['repo']}/git/blobs/{sha}")
            target.write_bytes(data)
        if len(data) != item["bytes"] or git_blob_sha(data) != sha:
            target.unlink(missing_ok=True)
            raise ValueError("Git blob SHA or byte length mismatch")
        return {**item, "local_path": str(target), "sha256": hashlib.sha256(data).hexdigest()}
    except Exception as exc:
        return {**item, "error": str(exc)}


def summarize(rows: list[dict], threshold: float = 0.70) -> dict:
    valid = [r for r in rows if "error" not in r]
    rho_rows = [r for r in valid if r.get("spearman_full_footprint") is not None]
    max_rho = max(rho_rows, key=lambda r: abs(r["spearman_full_footprint"]), default=None)
    max_overlap = max(valid, key=lambda r: r.get("my_dots_within_3px_of_theirs", 0.0), default=None)
    duplicates = sorted((r for r in valid if r.get("my_dots_within_3px_of_theirs", 0) > threshold),
                        key=lambda r: r["my_dots_within_3px_of_theirs"], reverse=True)
    return {
        "registries_checked": len(valid),
        "unique_under_literal_rule": bool(valid) and len(valid) == len(rows) and not bool(duplicates or any(r.get("duplicate_by_rho") for r in valid)),
        "stop_required": bool(duplicates or any(r.get("duplicate_by_rho") for r in valid)),
        "worst_abs_spearman": abs(max_rho["spearman_full_footprint"]) if max_rho else None,
        "worst_rho": max_rho["spearman_full_footprint"] if max_rho else None,
        "worst_rho_raster": max_rho["submission"] if max_rho else None,
        "worst_forward_overlap": max_overlap.get("my_dots_within_3px_of_theirs") if max_overlap else None,
        "worst_overlap_raster": max_overlap.get("submission") if max_overlap else None,
        "rasters_over_70pct_overlap": len(duplicates),
        "duplicate_examples": [
            {"raster": r["submission"], "forward_overlap": r["my_dots_within_3px_of_theirs"],
             "positive_pixels": r.get("their_dots"), "spearman": r.get("spearman_full_footprint")}
            for r in duplicates[:10]
        ],
    }


def audit_verdict(pre_compare: dict, final_compare: dict, inventory_complete: bool) -> str:
    """No phase, missing row, or empty inventory can authorize selector review."""
    summaries = [summarize(c["rows"]) for c in (pre_compare, final_compare)]
    if any(s["stop_required"] for s in summaries):
        return "negative — duplicate under literal registry rule; stop and do not spend a weekly slot"
    if (inventory_complete and all(c.get("complete_accessible_scan") and c.get("unique")
                                   for c in (pre_compare, final_compare))):
        return "selector-review-only; no slot authorization"
    return "negative — scan incomplete; fail closed"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate", default="docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--cache-only", action="store_true",
                    help="reuse a previously verified .cache/gemsdoe_public_registry/repo_inventory.json and blob cache; makes no GitHub API requests")
    ap.add_argument("--surface", type=Path, help="Actual lane pre-placement GeoTIFF; never substitute another lane")
    ap.add_argument("--witness-repo", help="Check one public owner repo for a binding duplicate; cannot clear uniqueness")
    ap.add_argument("--output", type=Path, default=ROOT / "evidence/public_registry_uniqueness.json")
    ap.add_argument("--out-name", default=None,
                    help="compat alias (STRAINBREAK session): evidence/<name>.json + docs/downloads/<name>.json")
    ap.add_argument("--preplacement-tif", type=Path, default=None,
                    help="compat alias for --surface")
    args = ap.parse_args()
    if args.preplacement_tif and not args.surface:
        args.surface = args.preplacement_tif
    if args.out_name:
        args.output = ROOT / "evidence" / f"{args.out_name}.json"
    candidate_path = (ROOT / args.candidate).resolve()
    if not candidate_path.is_file():
        ap.error(f"candidate not found: {candidate_path}")
    if (candidate_path.name != "GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif"
            and args.output.resolve() == (ROOT / "evidence/public_registry_uniqueness.json").resolve()):
        ap.error("non-collar candidate requires a separate --output; preserve collar evidence")
    CACHE.mkdir(parents=True, exist_ok=True)

    cached_trees = CACHE / "repo_inventory.json"
    scan_source = "current GitHub API"
    if args.cache_only:
        tree_results, repos = read_cached_trees(cached_trees)
        scan_source = "cached GitHub API inventory (no network refresh)"
    else:
        try:
            repos = get_repositories()
            if args.witness_repo:
                repos = [r for r in repos if r["name"] == args.witness_repo]
                if not repos:
                    raise ValueError("witness repository not found")
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
                tree_results = list(pool.map(tree_for, repos))
            if any(t.get("error") or t.get("truncated") for t in tree_results):
                raise RuntimeError("one or more public repository trees failed or were truncated")
            inventory_target = CACHE / "witness_inventory.json" if args.witness_repo else cached_trees
            inventory_target.write_text(json.dumps([
                {"repo": t["repo"], "branch": t.get("branch"), "truncated": t.get("truncated", False),
                 "error": t.get("error"),
                 "tifs": [{"path": f["path"], "sha": f["git_sha"], "size": f["bytes"]}
                          for f in t.get("files", [])]} for t in tree_results], indent=2), encoding="utf-8")
        except Exception as exc:
            if not cached_trees.is_file():
                raise
            print(f"WARNING: live GitHub inventory refresh failed ({exc}); using cached inventory, not claiming it is current.", file=sys.stderr)
            tree_results, repos = read_cached_trees(cached_trees)
            scan_source = "cached GitHub API inventory (live refresh failed)"
    if args.witness_repo:
        tree_results = [t for t in tree_results if t["repo"] == args.witness_repo]
        repos = [r for r in repos if r["name"] == args.witness_repo]
    paths = [f for result in tree_results for f in result["files"]]
    unique_by_blob = {}
    for item in paths:
        unique_by_blob.setdefault(item["git_sha"], item)
    print(f"Found {len(repos)} matching public repositories, {len(paths)} TIFF paths, "
          f"{len(unique_by_blob)} unique blobs", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        fetched = list(pool.map(lambda item: fetch_blob(item, cache_only=args.cache_only), unique_by_blob.values()))
    fetch_errors = [x for x in fetched if "error" in x]

    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    with rasterio.open(ROOT / "data" / "bridge" / "sample_submission.tif") as ref:
        expected_grid = (ref.shape, ref.crs, ref.transform)
    compatible = []
    exclusions = {"not_single_band_or_grid_mismatch": 0, "invalid_tiff": 0}
    for item in fetched:
        if "error" in item:
            continue
        try:
            with rasterio.open(item["local_path"]) as ds:
                if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected_grid:
                    exclusions["not_single_band_or_grid_mismatch"] += 1
                    continue
            compatible.append(item)
        except Exception:
            exclusions["invalid_tiff"] += 1
    rows_for_index = [{"repo_first": f["repo"], "sources": [f["repo"] + "/" + f["path"]],
                       "cache_file": f["local_path"], "sha256": f["sha256"]}
                      for f in compatible]
    tree_errors = [t for t in tree_results if t.get("error")]
    complete = (not fetch_errors and not tree_errors and not any(t["truncated"] for t in tree_results)
                and bool(compatible) and exclusions["invalid_tiff"] == 0
                and len(tree_results) == len(repos))
    index = {"schema": "gemsdoe92-public-submission-registry.v1", "complete_accessible_scan": complete,
             "n_rasters": len(rows_for_index), "rasters": rows_for_index,
             "errors": [*fetch_errors, *tree_errors,
                        *[{"repo": t["repo"], "error": "tree truncated"}
                          for t in tree_results if t["truncated"]]]}
    index_path = CACHE / ("witness_registry_index.json" if args.witness_repo else "registry_index.json")
    index_path.write_text(json.dumps(index), encoding="utf-8")

    with rasterio.open(candidate_path) as ds:
        if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected_grid:
            raise ValueError("candidate grid mismatch")
        candidate = ds.read(1)
    surface = None
    if args.surface:
        with rasterio.open(args.surface) as ds:
            if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected_grid:
                raise ValueError("pre-placement surface grid mismatch")
            surface = ds.read(1)
    elif candidate_path.name == "GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif":
        with rasterio.open(ROOT / "data/parent_R0_zeros.tif") as ds:
            parent = (ds.read(1) > 0) & grid.footprint
        full_distance = distance_transform_edt(~grid.catalogue)
        surface_mask = grid.footprint & (full_distance > 2.0) & (full_distance <= 3.0) & ~_near(parent, 3.0)
        surface = np.zeros(grid.footprint.shape, dtype=np.float32)
        surface[surface_mask] = (1.0 / full_distance[surface_mask]).astype(np.float32)
    pre_compare = compare_array_to_registry(surface, index, grid.footprint) if surface is not None else None
    final_compare = compare_array_to_registry(candidate, index, grid.footprint,
                                              file_sha256=hashlib.sha256(candidate_path.read_bytes()).hexdigest())
    pre_summary = summarize(pre_compare["rows"]) if pre_compare else {"status": "NOT_CHECKED: actual lane surface not supplied", "unique_under_literal_rule": False}
    final_summary = summarize(final_compare["rows"])
    witness_name = final_summary["worst_overlap_raster"]
    witness_item = next((f for f in compatible if f["repo"] + "/" + f["path"] == witness_name), None)
    witness = None
    if witness_item:
        witness = {"raster": witness_name,
                   "source_url": f"https://github.com/{OWNER}/{witness_item['repo']}/blob/{witness_item['branch']}/{witness_item['path']}",
                   "git_blob_sha": witness_item["git_sha"], "sha256": witness_item["sha256"],
                   "bytes": witness_item["bytes"],
                   "forward_overlap": final_summary["worst_forward_overlap"]}
    full_surface_name = "17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif"
    full_surface_row = next((r for r in final_compare["rows"] if r.get("submission") == full_surface_name), None)
    full_surface_item = next((f for f in compatible if f["repo"] + "/" + f["path"] == full_surface_name), None)
    full_surface_witness = None
    if full_surface_row and full_surface_item:
        full_surface_witness = {"raster": full_surface_name,
            "source_url": f"https://github.com/{OWNER}/{full_surface_item['repo']}/blob/{full_surface_item['branch']}/{full_surface_item['path']}",
            "git_blob_sha": full_surface_item["git_sha"], "sha256": full_surface_item["sha256"],
            "bytes": full_surface_item["bytes"], "positive_pixels_in_footprint": full_surface_row.get("their_dots"),
            "forward_overlap": full_surface_row.get("my_dots_within_3px_of_theirs"),
            "spearman": full_surface_row.get("spearman_full_footprint")}
    result = {
        "schema": "gemsdoe92-public-registry-uniqueness.v1",
        "reviewed_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_class": "REGISTRY-MEASUREMENT",
        "binding_rule": "literal: absolute Spearman >0.90 OR >70% of candidate dots within 3 px of any registry raster; no representation exemption",
        "candidate": {"name": candidate_path.stem.removesuffix("-zeros"),
                      "sha256": hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
                      "dots": int((candidate > 0).sum())},
        "inventory": {"owner": OWNER, "scan_source": scan_source, "matching_public_repositories": len(repos),
                      "default_branch_trees_complete": sum(not t["truncated"] for t in tree_results),
                      "tree_errors": len(tree_errors), "truncated_trees": sum(t["truncated"] for t in tree_results),
                      "submission_tiff_paths": len(paths), "unique_git_blobs": len(unique_by_blob),
                      "download_verified": len(fetched) - len(fetch_errors), "download_failures": len(fetch_errors),
                      "one_band_exact_template_grid_rasters_compared": len(compatible),
                      "exclusions": exclusions,
                      "scope": "Current public default branches; TIFF paths under docs/downloads/, releases/, and submission directories; unique Git blobs. Does not cover history, private repositories, other owners, zip-only objects, or site-hosted objects not in those paths."},
        "preplacement_surface": pre_summary,
        "final_dots": final_summary,
        "binding_witness": {"worst_forward_overlap": witness,
                            "full_footprint_surface": full_surface_witness},
        "verdict": audit_verdict(pre_compare or {"rows": []}, final_compare, complete and not args.witness_repo),
        "witness_only": bool(args.witness_repo),
        "scan_complete_for_declared_scope": bool(complete and not args.witness_repo and pre_compare is not None and pre_compare["complete_accessible_scan"] and final_compare["complete_accessible_scan"]),
        "candidate_file_sha256": hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
        "cache_index": str(index_path.relative_to(ROOT)),
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(result, indent=2) + "\n"
    out.write_text(serialized, encoding="utf-8")
    if out.resolve() == (ROOT / "evidence/public_registry_uniqueness.json").resolve():
        (ROOT / "docs/downloads/public_registry_uniqueness.json").write_text(serialized, encoding="utf-8")
    if args.out_name:
        (ROOT / "docs/downloads" / f"{args.out_name}.json").write_text(serialized, encoding="utf-8")
    print(json.dumps({"output": str(out), "preplacement": pre_summary,
                      "final": final_summary, "verdict": result["verdict"]}, indent=2))
    return 0 if result["scan_complete_for_declared_scope"] or final_summary["stop_required"] or pre_summary.get("stop_required") else 2


if __name__ == "__main__":
    raise SystemExit(main())
