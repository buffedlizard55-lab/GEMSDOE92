#!/usr/bin/env python3
"""Decoded-content digests for the cached public registry (REGISTRY-MEASUREMENT).

``gems57.uniqueness.compare_array_to_registry`` decodes every registry raster as
float32, maps non-finite cells to 0 and zeroes everything outside the footprint.
Many registry files differ only in encoding (NaN-outside vs zeros-outside twins,
copies re-staged in docs/downloads).  This script hashes the *decoded* array so a
comparison can be run once per distinct decoded content and then fanned out to
every file with the same digest - the verdict per file is unchanged because the
vendor function is deterministic in the decoded array.

Writes .cache/gemsdoe_public_registry/decoded_digests.json and a
``registry_index_unique.json`` (same schema as registry_index.json, one record per
distinct decoded content, with the list of all files sharing it).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import grid as grid_mod  # noqa: E402

CACHE = ROOT / ".cache" / "gemsdoe_public_registry"


def main() -> int:
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    fp = grid.footprint
    index = json.loads((CACHE / "registry_index.json").read_text())
    digests = {}
    for k, rec in enumerate(index["rasters"]):
        with rasterio.open(rec["cache_file"]) as ds:
            a = ds.read(1).astype(np.float32)
        a = np.where(np.isfinite(a), a, 0.0).astype(np.float32)
        a[~fp] = 0
        digests[rec["sha256"]] = hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
        if (k + 1) % 200 == 0:
            print(f"  digested {k + 1}/{len(index['rasters'])}", flush=True)
    (CACHE / "decoded_digests.json").write_text(json.dumps(digests, indent=0))
    groups: dict[str, list[dict]] = {}
    for rec in index["rasters"]:
        groups.setdefault(digests[rec["sha256"]], []).append(rec)
    uniq = []
    for dig, recs in groups.items():
        first = dict(recs[0])
        first["sources"] = sorted({s for r in recs for s in r["sources"]})
        first["decoded_sha256"] = dig
        first["n_files_sharing_decoded_content"] = len(recs)
        uniq.append(first)
    out = dict(index, rasters=uniq, n_rasters=len(uniq),
               note="one record per distinct decoded content; sources lists every file with that content",
               n_files_total=len(index["rasters"]))
    (CACHE / "registry_index_unique.json").write_text(json.dumps(out))
    print(json.dumps(dict(files=len(index["rasters"]), distinct_decoded=len(uniq)), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
