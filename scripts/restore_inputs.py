#!/usr/bin/env python3
"""Restore SHA-256-pinned inputs into gitignored .cache/gems_inputs/ per registry/session_manifest.json.

Strict compliance with Agent Brief v2 §4.1–§4.3:
- Never contacts dropbox.com or drivendata.org.
- Reads exact repository commit SHAs, SHA-256 digests, and byte sizes from registry/session_manifest.json.
- Verifies SHA-256 and byte length on disk before accepting any input; fails closed otherwise.
- Stages all competition/ancillary rasters inside .cache/gems_inputs/ (never tracked in Git).
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "registry" / "session_manifest.json"
VENTSCARP_EXT_MANIFEST_PATH = ROOT / "registry" / "ventscarp_external_manifest.json"
LIDAR1M_EXT_MANIFEST_PATH = ROOT / "registry" / "lidar1m_external_manifest.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_verified(path: Path, expected_sha: str, expected_bytes: int) -> bool:
    return (
        path.is_file()
        and path.stat().st_size == expected_bytes
        and sha256_file(path) == expected_sha
    )


def sparse_fetch(repo_slug: str, commit: str, paths: list[str], tmp_dir: Path) -> Path:
    co = tmp_dir / "checkout"
    url = f"https://github.com/{repo_slug}.git"
    subprocess.run(
        ["git", "clone", "--quiet", "--filter=blob:none", "--sparse", url, str(co)],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(co), "fetch", "--quiet", "--depth=1", "origin", commit],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(co), "checkout", "--quiet", "--detach", commit],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(co), "sparse-checkout", "set", "--no-cone", *("/" + p for p in paths)],
        check=True,
    )
    return co


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validation",
        action="store_true",
        help="Restore all pinned grid, parent R0 lineage, and control inputs without 419 MB training_features.tif",
    )
    parser.add_argument(
        "--ventscarp-external",
        action="store_true",
        help="Also restore SHA-256-pinned USGS 3DEP 10 m and DOE GDR INGENIOUS external inputs from registry/ventscarp_external_manifest.json",
    )
    parser.add_argument(
        "--lidar-1m",
        action="store_true",
        help="Also restore SHA-256-pinned USGS 3DEP 1 m LiDAR micro-scarp raster and DOE GDR #1391 volcanic vents from registry/lidar1m_external_manifest.json",
    )
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = list(manifest["files"])
    if args.ventscarp_external and VENTSCARP_EXT_MANIFEST_PATH.is_file():
        ext_manifest = json.loads(VENTSCARP_EXT_MANIFEST_PATH.read_text(encoding="utf-8"))
        files.extend(ext_manifest["files"])
    if args.lidar_1m and LIDAR1M_EXT_MANIFEST_PATH.is_file():
        lidar_manifest = json.loads(LIDAR1M_EXT_MANIFEST_PATH.read_text(encoding="utf-8"))
        files.extend(lidar_manifest["files"])

    cache_root = ROOT / ".cache" / "gems_inputs"
    cache_root.mkdir(parents=True, exist_ok=True)

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for entry in files:
        if args.validation and entry["id"] == "training_features":
            continue
        target = ROOT / entry["local_path"]
        if is_verified(target, entry["sha256"], int(entry["bytes"])):
            print(f"PIN OK   {entry['id']} ({entry['bytes']} B, {entry['sha256'][:12]})")
            continue
        grouped[(entry["repo"], entry["ref"])].append(entry)

    for (repo_slug, commit), entries in grouped.items():
        needed_paths: list[str] = []
        for entry in entries:
            if entry.get("multipart"):
                needed_paths.extend(entry["parts"])
            else:
                needed_paths.append(entry["path"])
        with tempfile.TemporaryDirectory(dir=cache_root) as td:
            co = sparse_fetch(repo_slug, commit, needed_paths, Path(td))
            for entry in entries:
                target = ROOT / entry["local_path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                if entry.get("multipart"):
                    with target.open("wb") as out:
                        for part in entry["parts"]:
                            with (co / part).open("rb") as inp:
                                shutil.copyfileobj(inp, out, 1 << 20)
                else:
                    shutil.copy2(co / entry["path"], target)
                got_bytes = target.stat().st_size
                got_sha = sha256_file(target)
                if got_bytes != int(entry["bytes"]) or got_sha != entry["sha256"]:
                    target.unlink(missing_ok=True)
                    raise SystemExit(
                        f"SHA-256/SIZE MISMATCH on {entry['id']}: "
                        f"got ({got_bytes}, {got_sha}), expected ({entry['bytes']}, {entry['sha256']})"
                    )
                print(f"RESTORED {entry['id']} ({got_bytes} B, {got_sha[:12]})")

    # Sync .cache/data/ mirror expected by vendor/gems57/grid.py
    cache_data = ROOT / ".cache" / "data"
    cache_data.mkdir(parents=True, exist_ok=True)
    for fname in ("sample_submission.tif", "existing_faults.tif"):
        src = cache_root / "bridge" / fname
        dst = cache_data / fname
        if src.is_file() and (not dst.is_file() or sha256_file(dst) != sha256_file(src)):
            shutil.copy2(src, dst)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
