#!/usr/bin/env python3
"""Run the registry gate on a uniformly RANDOM control (same budget, spacing floor and catalogue exclusion as LCS).

Purpose: show what the literal all-registry rule (Tier T) says about a file with NO information at all.  If a random
file also "duplicates" dozens of registry rasters, the rule cannot identify lanes (docs/UNIQUENESS_POLICY_20261024.md).
Deterministic (seed 520810); writes only .cache/ and evidence/lcs_random_control_registry.json.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems import lcs  # noqa: E402
from gems57 import grid as grid_mod  # noqa: E402


def main() -> int:
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    d_cat = ndi.distance_transform_edt(~grid.catalogue)
    cand = np.argwhere(grid.footprint & (d_cat > lcs.MIN_CATALOGUE_DISTANCE_PX))
    rng = np.random.default_rng(520810)
    sel = lcs.spaced_capped_greedy(rng.permutation(len(cand)), cand, grid.footprint.shape, lcs.N_TARGET)
    arr = np.zeros(grid.footprint.shape, np.float32)
    arr[cand[sel.index, 0], cand[sel.index, 1]] = 1.0
    out = ROOT / ".cache" / "lcs" / "random_control_37654.tif"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    grid_mod.write_geotiff(out, arr, nodata=None)
    print(f"random control: {int((arr > 0).sum())} dots -> {out}", flush=True)
    return subprocess.call([sys.executable, str(ROOT / "scripts" / "registry_gate.py"), "--candidate", str(out), "--phase", "final",
                            "--out", str(ROOT / "evidence" / "lcs_random_control_registry.json")])


if __name__ == "__main__":
    raise SystemExit(main())
