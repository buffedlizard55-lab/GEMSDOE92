"""Pinned-input manifest verification (brief section 2 constraint 2).

The manifest is the only permitted source of inputs. Anything not pinned here
must not be used; anything pinned here must hash exactly (and match its recorded
byte length, when present), or it is reported as UNVERIFIED rather than quietly
used.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .rasters import resolve_pinned_path, sha256_file

_SHA256 = re.compile(r"[0-9a-f]{64}")


def verify(manifest_path: str | Path, data_root: str | Path) -> dict:
    p = Path(manifest_path)
    if not p.exists():
        return {"ok": False, "error": f"manifest not found: {p}", "entries": []}
    try:
        raw = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": f"manifest is unreadable JSON: {exc}",
                "entries": []}
    if isinstance(raw, dict):
        files = raw.get("files", [])
    elif isinstance(raw, list):
        files = raw
    else:
        return {"ok": False, "error": "manifest root must be an object or list",
                "entries": []}
    if not isinstance(files, list):
        return {"ok": False, "error": "manifest files must be a list", "entries": []}

    root = Path(data_root)
    entries, problems = [], []
    for index, item in enumerate(files):
        entry_name = f"<entry {index}>"
        if not isinstance(item, dict):
            entries.append({"path": entry_name, "status": "MALFORMED"})
            problems.append(f"{entry_name}: expected an object")
            continue
        rel = item.get("dest") or item.get("path") or item.get("name")
        src = item.get("path") or rel
        if (not isinstance(rel, str) or not rel or Path(rel).is_absolute()
                or ".." in Path(rel).parts):
            entries.append({"path": rel if isinstance(rel, str) else entry_name,
                            "status": "INVALID_PATH"})
            problems.append(f"{entry_name}: invalid repository-relative path {rel!r}")
            continue
        want = item.get("sha256")
        f = resolve_pinned_path(root, rel)
        if not f.exists():
            entries.append({"path": rel, "status": "MISSING"})
            problems.append(f"{rel}: MISSING")
            continue
        if not isinstance(want, str) or _SHA256.fullmatch(want) is None:
            entries.append({"path": rel, "source": src,
                            "status": "INVALID_SHA256_PIN"})
            problems.append(f"{rel}: expected a 64-character lowercase sha256 pin")
            continue

        got = sha256_file(f)
        hash_ok = got == want
        want_bytes = item.get("bytes")
        got_bytes = f.stat().st_size
        invalid_size_pin = (want_bytes is not None and
                            (isinstance(want_bytes, bool) or
                             not isinstance(want_bytes, int) or want_bytes < 0))
        size_ok = (want_bytes is None or
                   (not invalid_size_pin and got_bytes == want_bytes))
        if invalid_size_pin:
            status = ("INVALID_BYTES_PIN" if hash_ok else
                      "HASH_MISMATCH_AND_INVALID_BYTES_PIN")
        elif hash_ok and size_ok:
            status = "OK"
        elif not hash_ok and not size_ok:
            status = "HASH_AND_SIZE_MISMATCH"
        elif not hash_ok:
            status = "HASH_MISMATCH"
        else:
            status = "SIZE_MISMATCH"
        entries.append({"path": rel, "source": src, "status": status,
                        "sha256": got, "bytes": got_bytes})
        if not hash_ok:
            problems.append(f"{rel}: expected {want[:16]}... got {got[:16]}...")
        if invalid_size_pin:
            problems.append(f"{rel}: invalid bytes pin {want_bytes!r}; expected a nonnegative integer")
        elif not size_ok:
            problems.append(f"{rel}: expected {want_bytes} bytes, got {got_bytes}")
    return {"ok": not problems, "problems": problems, "entries": entries,
            "n": len(entries)}
