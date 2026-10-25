#!/usr/bin/env python3
"""Build .cache/gemsdoe_public_registry/fast_supports.npz from registry_index.json.

Representation per vendor/gems57/uniqueness.py: dot_field if <=150,000 positive
footprint px (literal support), else continuous_surface (matched-budget
top-37,654 support via matched_budget_support). Consumed by
scripts/report_*_proxies.py dual-reading audits.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import grid as grid_mod  # noqa: E402
from vendor.gems57.uniqueness import matched_budget_support, DOT_FIELD_MAX_SUPPORT  # noqa: E402

CACHE = ROOT / ".cache/gemsdoe_public_registry"


def main() -> int:
    idx = json.loads((CACHE / "registry_index.json").read_text(encoding="utf-8"))
    grid = grid_mod.load_grid(ROOT / "data/bridge")
    foot = grid.footprint
    all_idx, offsets, meta = [], [0], []
    for r in idx["rasters"]:
        path = ROOT / r["cache_file"] if not Path(r["cache_file"]).is_absolute() else Path(r["cache_file"])
        with rasterio.open(path) as ds:
            arr = ds.read(1)
        dots = np.isfinite(arr) & (arr > 0) & foot
        n = int(dots.sum())
        if n <= DOT_FIELD_MAX_SUPPORT:
            support, rep = dots, "dot_field"
        else:
            support, rep = matched_budget_support(arr, foot, 37654), "continuous_surface"
        flat = np.flatnonzero(np.asarray(support, bool).ravel()).astype(np.int64)
        all_idx.append(flat); offsets.append(offsets[-1] + int(flat.size))
        meta.append({"file": r["sources"][0], "sha256": r["sha256"], "their_dots": n, "representation": rep})
    np.savez_compressed(CACHE / "fast_supports.npz",
                        all_idx=np.concatenate(all_idx) if all_idx else np.empty(0, np.int64),
                        offsets=np.asarray(offsets, np.int64), meta_json=json.dumps(meta))
    print(f"fast_supports: {len(meta)} rasters, {offsets[-1]} support px")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
