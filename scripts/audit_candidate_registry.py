#!/usr/bin/env python3
"""Full-registry uniqueness audit for ONE candidate raster (PI-1, gems/uniqueness_v3).

Shared-tool driver (2026-10-28).  It does not re-implement the comparison: it calls
``gems.uniqueness_v3.audit`` with the same footprint (pinned sample grid) and the
same registry cache (``.cache/registry_v3``, built by ``scripts/build_registry_cache.py``)
that the nine-site and RIESZ audits used, so every candidate is compared against
the same population of public GEMSDOE rasters.

Usage::

    python scripts/audit_candidate_registry.py --candidate docs/downloads/X-zeros.tif \
        --output evidence/X_full_registry_uniqueness.json

Nothing here grants clearance.  It reports the PI-1 verdict and the worst overlap
and |rho| with the sha256 and owner/repo where each worst match was found.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]

import lbm_data as L  # noqa: E402
from gems import registry_cache as rc  # noqa: E402
from gems import uniqueness_v3 as U  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--own-repo", default="buffedlizard55-lab/GEMSDOE92",
                    help="repo whose copy of the candidate bytes is the candidate itself (excluded)")
    args = ap.parse_args()

    cand_path = args.candidate if args.candidate.is_absolute() else ROOT / args.candidate
    with rasterio.open(cand_path) as ds:
        arr = ds.read(1)
        shape = ds.shape
    if shape != rc.SHAPE:
        raise SystemExit(f"candidate shape {shape} != competition grid {rc.SHAPE}")
    # Official rules: data outside the bounds may be null/NaN. Non-finite cells are
    # treated as "no dot" (0); every finite value must lie in [0, 1].
    nonfinite_cells = int((~np.isfinite(arr)).sum())
    arr = np.where(np.isfinite(arr), arr, np.float32(0.0))
    if float(arr.min()) < 0.0 or float(arr.max()) > 1.0:
        raise SystemExit("candidate values outside [0, 1]")
    dots = arr > 0

    inventory_path = rc.CACHE / "inventory.json"
    inventory_bytes = inventory_path.read_bytes()
    inv = json.loads(inventory_bytes)
    repos_of: dict[str, set[str]] = defaultdict(set)
    for repo in inv["repositories"]:
        for f in repo["files"]:
            repos_of[f["sha256"]].add(f"{repo['owner']}/{repo['repo']}")
    cand_sha = hashlib.sha256(cand_path.read_bytes()).hexdigest()
    # Only copies that live SOLELY in the candidate's own repo are excluded (a file is not a
    # prior submission of itself).  Identical bytes held by any other repo stay in the
    # comparison set and register as a duplicate (overlap 1.0), which is the point of the audit.
    self_repos = sorted(repos_of.get(cand_sha, set()))
    own_only = bool(self_repos) and set(self_repos) <= {args.own_repo}
    shas = sorted(sha for sha in repos_of if not (sha == cand_sha and own_only))

    fp = L.footprint()
    halo = U.load_halo_stats()
    aud = U.audit(dots, fp=fp, shas=shas, halo_stats=halo)

    def where(sha: str) -> list[str]:
        return sorted(repos_of.get(sha, set()))[:5]

    w = aud["worst_overlap_pi1"]
    r = aud["worst_abs_rho"]
    top = sorted(aud["rows"], key=lambda x: x["overlap_pi1"], reverse=True)[:10]
    out = dict(
        schema="gemsdoe92-candidate-full-registry-uniqueness-v1",
        candidate=str(cand_path.relative_to(ROOT)) if cand_path.is_relative_to(ROOT) else str(cand_path),
        candidate_sha256=cand_sha,
        candidate_identical_copies_in_registry=self_repos,
        n_dots=aud["n_dots"],
        candidate_nonfinite_cells_treated_as_zero=nonfinite_cells,
        registry_unique_sha256=len(shas),
        excluded_self_sha256=cand_sha if own_only else None,
        registry_scope=f"{inv.get('owners', '') or 'owners in .cache/registry_v3/inventory.json'}",
        registry_snapshot=dict(
            schema=inv.get("schema"),
            built_utc=inv.get("built_utc"),
            owners=inv.get("owners", []),
            repository_count=len(inv.get("repositories", [])),
            grid_compatible_raster_records=sum(len(r.get("files", [])) for r in inv.get("repositories", [])),
            unique_sha256_count=len({f["sha256"] for r in inv.get("repositories", []) for f in r.get("files", [])}),
            error_count=len(inv.get("errors", [])),
            inventory_sha256=hashlib.sha256(inventory_bytes).hexdigest(),
        ),
        rule=aud["rule"],
        duplicate_pi1=aud["duplicate"],
        pi1_pass=not aud["duplicate"],
        worst_overlap=dict(value=w["overlap_pi1"], sha256=w["sha256"], representation=w["representation"],
                           repos=where(w["sha256"])),
        worst_abs_rho=dict(value=abs(r["rho"]), sha256=r["sha256"], repos=where(r["sha256"])),
        n_rasters_overlap_over_0_5=aud["n_overlap_over_0_5"],
        literal_reading=dict(worst=aud["literal_reading"]["worst"]["overlap_literal"],
                             duplicate_under_literal=aud["literal_reading"]["duplicate_under_literal"],
                             note=aud["literal_reading"]["note"]),
        top10_overlap=[dict(sha256=t["sha256"], overlap_pi1=t["overlap_pi1"], rho=t["rho"],
                            representation=t["representation"], repos=where(t["sha256"])) for t in top],
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"registry {len(shas)} unique sha256 | n_dots {aud['n_dots']} | "
          f"worst overlap {w['overlap_pi1']:.6f} ({where(w['sha256'])}) | "
          f"worst |rho| {abs(r['rho']):.6f} | PI-1 pass={not aud['duplicate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
