#!/usr/bin/env python3
"""Restore the 13 SHA-256-pinned inputs of registry/data_manifest.json.

Manifest-driven: entries are grouped by (repo, ref) and sparse-fetched
from the owner's public GitHub mirrors at the pinned commits; every file
is hash- and size-verified after copying. The 419 MB 19-band stack is
assembled from its five ordered parts in buffedlizard55-lab/GEMSDOE.
No DrivenData/Dropbox contact; competition rasters land in gitignored
data/ only.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "data_manifest.json"
FEATURE_PARTS = [
    f"data/bridge/gems-geodawn-numerical-features.tif.part-{i:03d}" for i in range(5)
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ok(entry: dict) -> bool:
    p = ROOT / entry["local_path"]
    return p.is_file() and p.stat().st_size == entry["bytes"] and sha256(p) == entry["sha256"]


def sparse_fetch(repo: str, commit: str, paths: list[str], tmp: Path) -> Path:
    co = tmp / "m"
    subprocess.run(["git", "clone", "--quiet", "--filter=blob:none", "--sparse",
                    f"https://github.com/{repo}.git", str(co)], check=True)
    subprocess.run(["git", "-C", str(co), "fetch", "--quiet", "--depth=1", "origin", commit], check=True)
    subprocess.run(["git", "-C", str(co), "checkout", "--quiet", "--detach", commit], check=True)
    subprocess.run(["git", "-C", str(co), "sparse-checkout", "set", "--no-cone",
                    *("/" + p for p in paths)], check=True)
    return co


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--validation", action="store_true",
                    help="Restore everything except the 419 MB 19-band feature stack")
    args = ap.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = manifest["files"]
    # multipart feature stack: verify assembled file or rebuild from parts
    feat = next(e for e in entries if e["id"] == "training_features")
    others = [e for e in entries if e["id"] != "training_features"]
    groups: dict[tuple[str, str], list[dict]] = {}
    for e in others:
        groups.setdefault((e["repo"], e["ref"]), []).append(e)
    for (repo, commit), items in groups.items():
        missing = [e for e in items if not ok(e)]
        if not missing:
            print(f"PIN OK  {repo}@{commit[:8]} ({len(items)} files)")
            continue
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            co = sparse_fetch(repo, commit, [e["path"] for e in missing], Path(tmp))
            for e in missing:
                target = ROOT / e["local_path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(co / e["path"], target)
                if not ok(e):
                    target.unlink(missing_ok=True)
                    sys.exit(f"SHA256 MISMATCH for {e['local_path']}")
        print(f"RESTORED {repo}@{commit[:8]} ({len(missing)}/{len(items)} files)")
    if args.validation:
        print("SKIP features (--validation)")
        return 0
    if not ok(feat):
        target = ROOT / feat["local_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            co = sparse_fetch(feat["repo"], feat["ref"], FEATURE_PARTS, Path(tmp))
            with target.open("wb") as out:
                for part in FEATURE_PARTS:
                    with (co / part).open("rb") as inp:
                        shutil.copyfileobj(inp, out, 1 << 20)
        if not ok(feat):
            target.unlink(missing_ok=True)
            sys.exit("SHA256 MISMATCH for training_features.tif")
        print("RESTORED features (data/training_features.tif)")
    else:
        print("PIN OK  features (data/training_features.tif)")
    print(f"Verified {len(entries)}/{len(entries)} pinned inputs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
