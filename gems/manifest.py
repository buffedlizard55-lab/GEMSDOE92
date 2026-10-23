"""Pinned-input manifest verification (brief section 2 constraint 2).

The manifest is the only permitted source of inputs. Anything not pinned here
must not be used; anything pinned here must hash exactly, or it is reported as
UNVERIFIED rather than quietly used.
"""

from __future__ import annotations

import json
from pathlib import Path

from .rasters import sha256_file


def verify(manifest_path: str | Path, data_root: str | Path) -> dict:
    p = Path(manifest_path)
    if not p.exists():
        return {"ok": False, "error": f"manifest not found: {p}", "entries": []}
    raw = json.loads(p.read_text())
    files = raw.get("files", raw if isinstance(raw, list) else [])
    root = Path(data_root)
    entries, problems = [], []
    for item in files:
        rel = item.get("dest") or item.get("path") or item.get("name")
        src = item.get("path") or rel
        want = item.get("sha256")
        f = root / rel if rel else None
        if f is None or not f.exists():
            entries.append({"path": rel, "status": "MISSING"})
            problems.append(f"{rel}: MISSING")
            continue
        if not want:
            entries.append({"path": rel, "status": "UNPINNED"})
            problems.append(f"{rel}: no sha256 pinned in manifest")
            continue
        got = sha256_file(f)
        ok = got == want
        entries.append({"path": rel, "source": src,
                        "status": "OK" if ok else "HASH_MISMATCH",
                        "sha256": got})
        if not ok:
            problems.append(f"{rel}: expected {want[:16]}... got {got[:16]}...")
    return {"ok": not problems, "problems": problems, "entries": entries,
            "n": len(entries)}
