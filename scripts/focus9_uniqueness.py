#!/usr/bin/env python3
"""Nine-site uniqueness: each site's best CLAIM raster vs every raster served by OTHER sites.

Uses the PI-1 gate (gems/uniqueness_v3.py) and also reports the literal
reading.  A raster's "other-site" registry = every unique SHA-256 that occurs in
at least one repository other than the site's own.  Output:
evidence/focus9_uniqueness_20261027.json
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import lbm_data as L  # noqa: E402
from gems import registry_cache as rc  # noqa: E402
from gems import uniqueness_v3 as U  # noqa: E402


def main() -> int:
    src = json.loads((ROOT / "evidence" / "focus9_sources_20261028.json").read_text())
    inv = json.loads((rc.CACHE / "inventory.json").read_text())
    repos_of = defaultdict(set)
    for r in inv["repositories"]:
        for f in r["files"]:
            repos_of[f["sha256"]].add(f"{r['owner']}/{r['repo']}")
    halo = U.load_halo_stats()
    fp = L.footprint()
    out = {}
    for site, s in src.items():
        own = f"buffedlizard55-lab/{site}"
        others = sorted(sha for sha, reps in repos_of.items() if reps - {own})
        p, _ = L.full_from_summary(s["sha256"])
        aud = U.audit(p > 0, fp=fp, shas=others, halo_stats=halo)
        w = aud["worst_overlap_pi1"]; wr = aud["worst_abs_rho"]
        def where(sha):
            return sorted(repos_of[sha] - {own})[:3]
        out[site] = dict(best=s["best"], claim=s["claim"], n_compared=len(others), n_dots=aud["n_dots"],
                         unique_pi1=not aud["duplicate"],
                         worst_overlap=w["overlap_pi1"], worst_overlap_sha=w["sha256"], worst_overlap_in=where(w["sha256"]),
                         worst_rho=wr["rho"], worst_rho_sha=wr["sha256"], worst_rho_in=where(wr["sha256"]),
                         literal_duplicate=aud["literal_reading"]["duplicate_under_literal"],
                         identical_bytes_elsewhere=sorted(repos_of[s["sha256"]] - {own}))
        print(site, out[site]["unique_pi1"], round(w["overlap_pi1"], 4), where(w["sha256"]), round(wr["rho"], 4), flush=True)
    (ROOT / "evidence" / "focus9_uniqueness_20261028.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
