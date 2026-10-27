#!/usr/bin/env python3
"""Cache coverage fields of every CLAIM-matched raster (footprint vectors, float16)."""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import lbm_data as L  # noqa: E402
from gems import lbmodel as M  # noqa: E402

OUT = ROOT / ".cache" / "lbm"

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fp = L.footprint()
    rows = [r for r in L.load_claims_matched() if "match" in r]
    done = 0
    for r in rows:
        sha = r["match"]["sha256"]
        f = OUT / f"{sha}.npz"
        if f.is_file():
            continue
        p, meta = L.full_from_summary(sha)
        C = M.coverage_field(p).ravel()[fp.lin].astype(np.float16)
        pv = p.ravel()[fp.lin]
        pos = np.flatnonzero(pv > 0).astype(np.int32)
        np.savez(f, C=C, pos=pos, val=pv[pos].astype(np.float32))
        done += 1
    print("cached", done, "new coverage fields in", OUT)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
