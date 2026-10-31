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
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

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


def _normalise_repo(repo: object) -> str:
    """Return a safe ``owner/repository`` slug for a GitHub source only."""
    if not isinstance(repo, str) or not repo.strip():
        raise ValueError("manifest entry needs a GitHub repository")
    value = repo.strip()
    if "://" in value:
        parsed = urlsplit(value)
        if (parsed.scheme != "https" or parsed.hostname != "github.com"
                or parsed.username is not None or parsed.password is not None
                or parsed.port is not None or parsed.query or parsed.fragment):
            raise ValueError(f"unsupported repository URL (GitHub HTTPS only): {repo!r}")
        value = parsed.path.strip("/")
        if value.endswith(".git"):
            value = value[:-4]
    elif value.startswith("github.com/"):
        value = value[len("github.com/"):]
    parts = value.split("/")
    if (len(parts) != 2 or any(not part or part in {".", ".."}
                               or not re.fullmatch(r"[A-Za-z0-9_.-]+", part)
                               for part in parts)):
        raise ValueError(f"invalid GitHub owner/repository slug: {repo!r}")
    return "/".join(parts)


def _normalise_repo_path(value: object, field: str) -> str:
    """Validate a repository-relative POSIX path without traversal."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"manifest {field} must be a nonempty POSIX-relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ValueError(f"manifest {field} must not be absolute or contain traversal: {value!r}")
    return path.as_posix()


def normalise_manifest_entry(entry: dict) -> dict:
    """Normalize the legacy ``ref/path`` and newer ``commit/repo_path`` schemas.

    The lidar manifest historically used ``commit``/``repo_path`` and a full
    GitHub URL, while the main and 10 m manifests use ``ref``/``path`` and an
    owner/repository slug.  Normalize once before grouping so every source is
    still pinned to one immutable commit and remains restricted to github.com.
    """
    if not isinstance(entry, dict):
        raise ValueError("manifest file entry must be an object")
    repo = _normalise_repo(entry.get("repo"))
    commit = entry.get("ref") or entry.get("commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise ValueError(f"{entry.get('id', '<unknown>')}: ref/commit must be a full 40-character Git SHA")
    expected_sha = entry.get("sha256")
    size = entry.get("bytes")
    if not isinstance(expected_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        raise ValueError(f"{entry.get('id', '<unknown>')}: invalid SHA-256 pin")
    if type(size) is not int or size <= 0:
        raise ValueError(f"{entry.get('id', '<unknown>')}: bytes pin must be a positive integer")
    if not isinstance(entry.get("id"), str) or not entry["id"].strip():
        raise ValueError("manifest entry needs a nonempty id")

    local_path = _normalise_repo_path(entry.get("local_path"), "local_path")
    if not local_path.startswith(".cache/gems_inputs/"):
        raise ValueError(f"manifest local_path must remain under .cache/gems_inputs/: {local_path!r}")
    multipart = entry.get("multipart", False)
    if type(multipart) is not bool:
        raise ValueError(f"{entry['id']}: multipart must be boolean when present")
    normalised = dict(entry)
    normalised.update(repo=repo, ref=commit.lower(), local_path=local_path)
    if multipart:
        parts = entry.get("parts")
        if not isinstance(parts, list) or not parts:
            raise ValueError(f"{entry['id']}: multipart input needs a nonempty parts list")
        normalised["parts"] = [_normalise_repo_path(part, "multipart part") for part in parts]
    else:
        source_path = entry.get("path") or entry.get("repo_path")
        normalised["path"] = _normalise_repo_path(source_path, "path/repo_path")
    return normalised


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


def main(argv: list[str] | None = None) -> int:
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
    args = parser.parse_args(argv)

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise SystemExit(f"invalid or empty input manifest: {MANIFEST_PATH}")
    files = list(files)
    if args.ventscarp_external:
        if not VENTSCARP_EXT_MANIFEST_PATH.is_file():
            raise SystemExit(f"requested external manifest is missing: {VENTSCARP_EXT_MANIFEST_PATH}")
        ext_manifest = json.loads(VENTSCARP_EXT_MANIFEST_PATH.read_text(encoding="utf-8"))
        extra = ext_manifest.get("files")
        if not isinstance(extra, list) or not extra:
            raise SystemExit(f"invalid or empty external manifest: {VENTSCARP_EXT_MANIFEST_PATH}")
        files.extend(extra)
    if args.lidar_1m:
        if not LIDAR1M_EXT_MANIFEST_PATH.is_file():
            raise SystemExit(f"requested LiDAR manifest is missing: {LIDAR1M_EXT_MANIFEST_PATH}")
        lidar_manifest = json.loads(LIDAR1M_EXT_MANIFEST_PATH.read_text(encoding="utf-8"))
        extra = lidar_manifest.get("files")
        if not isinstance(extra, list) or not extra:
            raise SystemExit(f"invalid or empty LiDAR manifest: {LIDAR1M_EXT_MANIFEST_PATH}")
        files.extend(extra)

    normalized_files = []
    for raw_entry in files:
        if args.validation and isinstance(raw_entry, dict) and raw_entry.get("id") == "training_features":
            continue
        normalized_files.append(normalise_manifest_entry(raw_entry))
    ids = [entry["id"] for entry in normalized_files]
    destinations = [entry["local_path"] for entry in normalized_files]
    if len(set(ids)) != len(ids):
        raise SystemExit("input manifests contain duplicate file IDs")
    if len(set(destinations)) != len(destinations):
        raise SystemExit("input manifests contain duplicate cache destinations")

    cache_root = ROOT / ".cache" / "gems_inputs"
    cache_root.mkdir(parents=True, exist_ok=True)

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for entry in normalized_files:
        target = ROOT / entry["local_path"]
        if is_verified(target, entry["sha256"], entry["bytes"]):
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
