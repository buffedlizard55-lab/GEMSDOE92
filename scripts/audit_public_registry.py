#!/usr/bin/env python3
"""Audit candidate uniqueness against current public GEMSDOE owner-repo rasters.

Requires the GitHub CLI (``gh``) to have working API access (unless ``--cache-only``
is passed with a populated ``.cache/gemsdoe_public_registry``). Scans current
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
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import grid as grid_mod  # noqa: E402
from vendor.gems57.uniqueness import (  # noqa: E402
    JACCARD_LIMIT,
    OVERLAP_LIMIT,
    RHO_LIMIT,
    _dots,
    _jaccard,
    _near,
    _sha,
    binding_duplicate_decision,
    two_phase_summary,
)

OWNER = "buffedlizard55-lab"
CACHE = ROOT / ".cache" / "gemsdoe_public_registry"
DEFAULT_CANDIDATE = "docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif"

_SHARED: dict = {}


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


def fetch_blob(item: dict) -> dict:
    sha = item["git_sha"]
    target = CACHE / f"{sha}.tif"
    try:
        if target.exists():
            data = target.read_bytes()
        else:
            data = gh_bytes("-H", "Accept: application/vnd.github.raw",
                            f"repos/{OWNER}/{item['repo']}/git/blobs/{sha}")
            target.write_bytes(data)
        if len(data) != item["bytes"] or git_blob_sha(data) != sha:
            target.unlink(missing_ok=True)
            raise ValueError("Git blob SHA or byte length mismatch")
        return {**item, "local_path": str(target), "sha256": hashlib.sha256(data).hexdigest()}
    except Exception as exc:
        return {**item, "error": str(exc)}


def _prep_target(arr: np.ndarray, fp: np.ndarray, file_sha256: str | None = None) -> dict:
    arr = np.asarray(arr, np.float32)
    values = arr[fp]
    ranks = rankdata(values).astype(np.float64)
    ranks -= ranks.mean()
    norm = float(np.linalg.norm(ranks))
    sup = _dots(arr) & fp
    return {
        "ranks": ranks,
        "norm": norm,
        "support": sup,
        "count": int(sup.sum()),
        "near": _near(sup),
        "decoded_digest": hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest(),
        "file_sha256": file_sha256,
    }


def _eval_one_prior(rec: dict) -> dict[str, dict]:
    fp: np.ndarray = _SHARED["fp"]
    targets: dict[str, dict] = _SHARED["targets"]
    p = Path(rec["cache_file"])
    if not p.is_absolute():
        p = ROOT / p
    base = {"repo": rec.get("repo_first"), "submission": rec["sources"][0], "file": str(p)}
    try:
        if not p.exists():
            raise FileNotFoundError("missing registry file; cannot certify uniqueness")
        digest = _sha(p)
        if rec.get("sha256") and digest != rec["sha256"]:
            raise ValueError("registry SHA256 pin mismatch")
        with rasterio.open(p) as src:
            if src.count != 1 or src.shape != fp.shape:
                raise ValueError("registry grid or band-count mismatch")
            if fp.shape == (3730, 3292):
                if src.crs is None or src.crs.to_epsg() != 32611 or src.transform != grid_mod.TRANSFORM:
                    raise ValueError("registry CRS/transform mismatch")
            theirs = src.read(1).astype(np.float32)
        theirs = np.where(np.isfinite(theirs), theirs, 0.0)
        theirs[~fp] = 0.0
        tv = theirs[fp]
        support = (theirs > 0) & fp
        tb = support[fp]
        nt = int(tb.sum())
        n = len(tv)
        ptp = float(np.ptp(tv))
        is_binary = bool(ptp > 0 and np.all((tv == 0) | (tv == 1)))
        tr = None
        tr_norm = 0.0
        if ptp > 0 and not is_binary:
            tr = rankdata(tv).astype(np.float64)
            tr -= tr.mean()
            tr_norm = float(np.linalg.norm(tr))
        near_sup = _near(support)
        halo_cov = float(near_sup[fp].mean())
        their_decoded = hashlib.sha256(np.ascontiguousarray(theirs).tobytes()).hexdigest()

        out: dict[str, dict] = {}
        for key, tgt in targets.items():
            norm = tgt["norm"]
            if norm == 0 or ptp == 0:
                rho = None
            elif is_binary:
                rho = float(tgt["ranks"][tb].sum() / (norm * np.sqrt(nt * (n - nt) / n)))
            else:
                rho = float(np.dot(tgt["ranks"], tr) / (norm * tr_norm))
            my_sup = tgt["support"]
            ov = float(near_sup[my_sup].mean()) if tgt["count"] else 0.0
            reverse = float(tgt["near"][support].mean()) if nt else 0.0
            jac = _jaccard(my_sup, support)
            out[key] = {
                **base,
                "sha256": digest,
                "decoded_sha256": their_decoded,
                "their_dots": nt,
                "my_dots_within_3px_of_theirs": ov,
                "forward_overlap": ov,
                "halo_coverage": halo_cov,
                "their_dots_within_3px_of_mine": reverse,
                "spearman_full_footprint": rho,
                "jaccard_dot_sets": jac,
                "identical_bytes": bool(tgt["file_sha256"] and digest == tgt["file_sha256"]),
                "identical_decoded_predictions": bool(their_decoded == tgt["decoded_digest"]),
                "duplicate_by_rho": bool(rho is not None and abs(rho) > RHO_LIMIT),
                "duplicate_by_overlap": bool(ov > OVERLAP_LIMIT),
                "duplicate_by_jaccard": bool(jac > JACCARD_LIMIT),
            }
        return out
    except (OSError, ValueError, rasterio.errors.RasterioError) as exc:
        return {k: {**base, "error": str(exc)} for k in targets}


def compare_targets_parallel(targets_raw: dict[str, tuple[np.ndarray, str | None]],
                             rasters: list[dict], fp: np.ndarray,
                             proc_workers: int = 2) -> dict[str, list[dict]]:
    _SHARED["fp"] = fp
    _SHARED["targets"] = {
        k: _prep_target(arr, fp, sha) for k, (arr, sha) in targets_raw.items()
    }
    rows_by_key: dict[str, list[dict]] = {k: [] for k in targets_raw}
    with concurrent.futures.ProcessPoolExecutor(max_workers=proc_workers) as pool:
        for res in pool.map(_eval_one_prior, rasters, chunksize=16):
            for k, row in res.items():
                rows_by_key[k].append(row)
    return rows_by_key


def summarize(rows: list[dict], threshold: float = 0.70) -> dict:
    valid = [r for r in rows if "error" not in r]
    rho_rows = [r for r in valid if r.get("spearman_full_footprint") is not None]
    max_rho = max(rho_rows, key=lambda r: abs(r["spearman_full_footprint"]), default=None)
    max_overlap = max(valid, key=lambda r: r.get("my_dots_within_3px_of_theirs", 0.0), default=None)
    duplicates = sorted((r for r in valid if r.get("my_dots_within_3px_of_theirs", 0) > threshold),
                        key=lambda r: r["my_dots_within_3px_of_theirs"], reverse=True)
    return {
        "registries_checked": len(valid),
        "unique_under_literal_rule": not bool(duplicates or any(r.get("duplicate_by_rho") for r in valid)),
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


def diagnostic_discriminating_summary(rows: list[dict], footprint_cells: int,
                                      threshold: float = 0.70) -> dict:
    """Non-binding diagnostic separating continuous/space-filling surfaces from sparse dot fields."""
    valid = [r for r in rows if "error" not in r]
    two_phase = two_phase_summary(valid, footprint_cells)
    halo_decision = binding_duplicate_decision(valid)
    disc_rows = [r for r in valid if float(r.get("halo_coverage", 1.0)) < 0.70]
    disc_over = sorted(
        (r for r in disc_rows if r.get("my_dots_within_3px_of_theirs", 0.0) > threshold),
        key=lambda r: r["my_dots_within_3px_of_theirs"],
        reverse=True,
    )
    worst_disc = max(disc_rows, key=lambda r: r.get("my_dots_within_3px_of_theirs", 0.0), default=None)
    sparse_60k = [r for r in valid if (r.get("their_dots") or 0) <= 60_000]
    sparse_60k_over = sorted(
        (r for r in sparse_60k if r.get("my_dots_within_3px_of_theirs", 0.0) > threshold),
        key=lambda r: r["my_dots_within_3px_of_theirs"],
        reverse=True,
    )
    worst_60k = max(sparse_60k, key=lambda r: r.get("my_dots_within_3px_of_theirs", 0.0), default=None)
    worst_60k_rho = max(sparse_60k, key=lambda r: abs(r.get("spearman_full_footprint") or 0.0), default=None)
    return {
        "binding": False,
        "note": (
            "Diagnostic only; does NOT waive or override the binding literal positive-support rule. "
            "Separates sparse dot-field submissions from dense/continuous probability surfaces "
            "(such as 17GEMSDOE E-proba-multiscale, positive on all 5,167,373 footprint pixels)."
        ),
        "sparse_dotted_le_60k_dots": {
            "count": len(sparse_60k),
            "worst_abs_spearman": (abs(worst_60k_rho["spearman_full_footprint"])
                                   if worst_60k_rho and worst_60k_rho.get("spearman_full_footprint") is not None
                                   else None),
            "worst_rho_raster": (worst_60k_rho.get("submission") if worst_60k_rho else None),
            "worst_forward_overlap": (worst_60k.get("my_dots_within_3px_of_theirs") if worst_60k else None),
            "worst_overlap_raster": (worst_60k.get("submission") if worst_60k else None),
            "rasters_over_70pct_overlap": len(sparse_60k_over),
            "examples_over_70pct": [
                {"raster": r["submission"], "forward_overlap": r["my_dots_within_3px_of_theirs"],
                 "positive_pixels": r.get("their_dots"), "halo_coverage": r.get("halo_coverage")}
                for r in sparse_60k_over[:10]
            ],
        },
        "like_for_like_dot_fields_le_20pct_support": two_phase["like_for_like_reading"],
        "discriminating_priors_lt_70pct_halo": {
            "count": len(disc_rows),
            "space_filling_priors_ge_70pct_halo": halo_decision["space_filling_priors"],
            "worst_forward_overlap": (worst_disc.get("my_dots_within_3px_of_theirs") if worst_disc else None),
            "worst_overlap_raster": (worst_disc.get("submission") if worst_disc else None),
            "rasters_over_70pct_overlap": len(disc_over),
            "examples_over_70pct": [
                {"raster": r["submission"], "forward_overlap": r["my_dots_within_3px_of_theirs"],
                 "positive_pixels": r.get("their_dots"), "halo_coverage": r.get("halo_coverage")}
                for r in disc_over[:10]
            ],
        },
    }


def load_preplacement_surface(surface_arg: str | None, candidate_path: Path,
                              grid: grid_mod.Grid) -> np.ndarray | None:
    if surface_arg:
        sp = (ROOT / surface_arg).resolve() if not Path(surface_arg).is_absolute() else Path(surface_arg)
        if sp.suffix.lower() == ".npy":
            arr = np.load(sp).astype(np.float32)
        else:
            with rasterio.open(sp) as ds:
                arr = ds.read(1).astype(np.float32)
        arr = np.where(grid.footprint & np.isfinite(arr), np.clip(arr, 0.0, 1.0), 0.0).astype(np.float32)
        return arr
    if candidate_path == (ROOT / DEFAULT_CANDIDATE).resolve():
        pre_path = ROOT / "data" / "parent_R0_zeros.tif"
        with rasterio.open(pre_path) as ds:
            parent = (ds.read(1) > 0) & grid.footprint
        full_distance = distance_transform_edt(~grid.catalogue)
        surface_mask = grid.footprint & (full_distance > 2.0) & (full_distance <= 3.0) & ~_near(parent, 3.0)
        surface = np.zeros(grid.footprint.shape, dtype=np.float32)
        surface[surface_mask] = (1.0 / full_distance[surface_mask]).astype(np.float32)
        return surface
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate", default=DEFAULT_CANDIDATE)
    ap.add_argument("--surface", default=None,
                    help="optional pre-placement surface (.npy or .tif in [0,1]) for pre-placement check")
    ap.add_argument("--out", default=None,
                    help="output JSON path (defaults to evidence/public_registry_uniqueness.json)")
    ap.add_argument("--downloads-copy", default=None,
                    help="optional docs/downloads JSON copy path")
    ap.add_argument("--exclude-self-sha256", action="store_true",
                    help="exclude blobs whose SHA-256 equals the candidate itself (when candidate is already merged)")
    ap.add_argument("--exclude-path-substr", action="append", default=[],
                    help="exclude blobs whose repo/path contains this substring (e.g., dose siblings in same lane)")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--proc-workers", type=int, default=2)
    ap.add_argument("--cache-only", action="store_true",
                    help="reuse a previously verified .cache/gemsdoe_public_registry/repo_inventory.json and blob cache; makes no GitHub API requests")
    args = ap.parse_args()
    candidate_path = (ROOT / args.candidate).resolve() if not Path(args.candidate).is_absolute() else Path(args.candidate)
    if not candidate_path.is_file():
        ap.error(f"candidate not found: {candidate_path}")
    cand_sha = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
    CACHE.mkdir(parents=True, exist_ok=True)

    cached_trees = CACHE / "repo_inventory.json"
    scan_source = "current GitHub API"
    if args.cache_only:
        tree_results, repos = read_cached_trees(cached_trees)
        scan_source = "cached GitHub API inventory (no network refresh)"
    else:
        try:
            repos = get_repositories()
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
                tree_results = list(pool.map(tree_for, repos))
            if any(t.get("error") or t.get("truncated") for t in tree_results):
                raise RuntimeError("one or more public repository trees failed or were truncated")
            cached_trees.write_text(json.dumps([
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
    paths = [f for result in tree_results for f in result["files"]]
    unique_by_blob = {}
    for item in paths:
        unique_by_blob.setdefault(item["git_sha"], item)
    print(f"Found {len(repos)} matching public repositories, {len(paths)} TIFF paths, "
          f"{len(unique_by_blob)} unique blobs", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        fetched = list(pool.map(fetch_blob, unique_by_blob.values()))
    fetch_errors = [x for x in fetched if "error" in x]

    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    with rasterio.open(ROOT / "data" / "bridge" / "sample_submission.tif") as ref:
        expected_grid = (ref.shape, ref.crs, ref.transform)
    compatible = []
    exclusions = {"not_single_band_or_grid_mismatch": 0, "invalid_tiff": 0,
                  "excluded_self": 0, "excluded_substr": 0}
    for item in fetched:
        if "error" in item:
            continue
        if args.exclude_self_sha256 and item["sha256"] == cand_sha:
            exclusions["excluded_self"] += 1
            continue
        full_slug = f"{item['repo']}/{item['path']}"
        if any(sub in full_slug for sub in args.exclude_path_substr):
            exclusions["excluded_substr"] += 1
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
                and len(tree_results) == len(repos))
    index = {"schema": "gemsdoe92-public-submission-registry.v1", "complete_accessible_scan": complete,
             "n_rasters": len(rows_for_index), "rasters": rows_for_index,
             "errors": [*fetch_errors, *tree_errors,
                        *[{"repo": t["repo"], "error": "tree truncated"}
                          for t in tree_results if t["truncated"]]]}
    index_path = CACHE / "registry_index.json"
    index_path.write_text(json.dumps(index), encoding="utf-8")

    with rasterio.open(candidate_path) as ds:
        candidate = ds.read(1)
    surface = load_preplacement_surface(args.surface, candidate_path, grid)
    targets_raw: dict[str, tuple[np.ndarray, str | None]] = {
        "final": (candidate, cand_sha),
    }
    if surface is not None:
        targets_raw["pre"] = (surface, None)
    rows_by_key = compare_targets_parallel(
        targets_raw, rows_for_index, grid.footprint, proc_workers=args.proc_workers
    )
    final_rows = rows_by_key["final"]
    pre_rows = rows_by_key.get("pre")
    pre_summary = summarize(pre_rows) if pre_rows is not None else None
    final_summary = summarize(final_rows)
    footprint_cells = int(grid.footprint.sum())
    final_diag = diagnostic_discriminating_summary(final_rows, footprint_cells)
    pre_diag = (diagnostic_discriminating_summary(pre_rows, footprint_cells)
                if pre_rows is not None else None)
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
    full_surface_row = next((r for r in final_rows if r.get("submission") == full_surface_name), None)
    full_surface_item = next((f for f in compatible if f["repo"] + "/" + f["path"] == full_surface_name), None)
    full_surface_witness = None
    if full_surface_row and full_surface_item:
        full_surface_witness = {"raster": full_surface_name,
            "source_url": f"https://github.com/{OWNER}/{full_surface_item['repo']}/blob/{full_surface_item['branch']}/{full_surface_item['path']}",
            "git_blob_sha": full_surface_item["git_sha"], "sha256": full_surface_item["sha256"],
            "bytes": full_surface_item["bytes"], "positive_pixels_in_footprint": full_surface_row.get("their_dots"),
            "forward_overlap": full_surface_row.get("my_dots_within_3px_of_theirs"),
            "spearman": full_surface_row.get("spearman_full_footprint")}
    pre_missing = sum(1 for r in (pre_rows or []) if "error" in r)
    final_missing = sum(1 for r in final_rows if "error" in r)
    result = {
        "schema": "gemsdoe92-public-registry-uniqueness.v1",
        "reviewed_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_class": "REGISTRY-MEASUREMENT",
        "binding_rule": "literal: absolute Spearman >0.90 OR >70% of candidate dots within 3 px of any registry raster; no representation exemption",
        "candidate": {"name": candidate_path.stem.removesuffix("-zeros"),
                      "sha256": cand_sha,
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
        "preplacement_diagnostic": pre_diag,
        "final_dots": final_summary,
        "final_diagnostic": final_diag,
        "binding_witness": {"worst_forward_overlap": witness,
                            "full_footprint_surface": full_surface_witness},
        "saturation_certificate": (
            {
                "universal_overlap_blocker": True,
                "witness_raster": full_surface_name,
                "positive_pixels_in_footprint": footprint_cells,
                "total_footprint_pixels": footprint_cells,
                "coverage_fraction": 1.0,
                "mathematical_consequence": (
                    "Every nonempty valid submission has 100.0% forward 3-px dot overlap against "
                    "this all-positive probability surface under literal positive support (finite > 0). "
                    "Literal rule is enforced without waiver; see final_diagnostic.sparse_dotted_le_60k_dots "
                    "for non-binding comparison against sparse dotted submissions."
                ),
            }
            if full_surface_witness and full_surface_witness.get("positive_pixels_in_footprint") == footprint_cells
            else None
        ),
        "verdict": "negative — duplicate under literal registry rule; stop and do not spend a weekly slot" if final_summary["stop_required"] else ("promote" if complete else "negative — scan incomplete; fail closed"),
        "scan_complete_for_declared_scope": bool(complete and pre_missing == 0 and final_missing == 0),
        "candidate_file_sha256": cand_sha,
        "cache_index": str(index_path.relative_to(ROOT)),
    }
    if args.out:
        out = (ROOT / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)
    else:
        out = ROOT / "evidence" / "public_registry_uniqueness.json"
    serialized = json.dumps(result, indent=2) + "\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(serialized, encoding="utf-8")
    if args.downloads_copy:
        dl_copy = (ROOT / args.downloads_copy).resolve() if not Path(args.downloads_copy).is_absolute() else Path(args.downloads_copy)
        dl_copy.parent.mkdir(parents=True, exist_ok=True)
        dl_copy.write_text(serialized, encoding="utf-8")
    elif args.out is None:
        (ROOT / "docs" / "downloads" / "public_registry_uniqueness.json").write_text(
            serialized, encoding="utf-8")
    print(json.dumps({"output": str(out), "preplacement": pre_summary,
                      "final": final_summary,
                      "final_discriminating_diag": final_diag["discriminating_priors_lt_70pct_halo"],
                      "verdict": result["verdict"]}, indent=2))
    return 0 if result["scan_complete_for_declared_scope"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
