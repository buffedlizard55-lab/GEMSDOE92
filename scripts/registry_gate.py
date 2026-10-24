#!/usr/bin/env python3
"""Authoritative registry comparison for one raster (dots or pre-placement surface).

Calls the shared ``gems57.uniqueness.compare_array_to_registry`` UNCHANGED, on the
distinct-decoded-content index produced by scripts/registry_digests.py (identical
decoded arrays give identical rows, so each distinct array is compared once and the
verdict is fanned out to every file that shares it).  Then tiers the rows:

  Tier S  rasters that carry an operator-claimed leaderboard score ("previous submissions")
  Tier L  every registry raster whose 3 px halo covers < 50 % of the footprint (lane witnesses)
  Tier T  literal rule: ALL rasters including blankets (halo coverage >= 50 %)

All three are reported side by side.  Which tier decides "OK to submit" is a policy
recorded in registry/uniqueness_policy.json and evaluated by gems/uniqueness_policy.py;
this script never decides.  Scope statement is embedded in the output.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import grid as grid_mod  # noqa: E402
from gems57.uniqueness import compare_array_to_registry, OVERLAP_LIMIT, RHO_LIMIT  # noqa: E402

REG = ROOT / ".cache" / "gemsdoe_public_registry"
BLANKET_HALO = 0.50


def _sha256_file(p: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True, type=Path)
    ap.add_argument("--phase", choices=["surface", "final"], required=True)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    fp = grid.footprint
    with rasterio.open(ROOT / "data" / "bridge" / "sample_submission.tif") as ref:
        expected = (ref.shape, ref.crs, ref.transform)
    with rasterio.open(args.candidate) as ds:
        if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected:
            raise ValueError("candidate grid mismatch")
        mine = ds.read(1)
    index = json.loads((REG / "registry_index_unique.json").read_text())
    full_index = json.loads((REG / "registry_index.json").read_text())
    t0 = time.time()

    def progress(i, n, row):
        if i % 50 == 0 or i == n:
            print(f"[{args.phase}] {i}/{n} ({time.time() - t0:.0f}s)", flush=True)

    res = compare_array_to_registry(mine, index, fp, progress=progress, expected_grid=expected)
    rows = [r for r in res["rows"] if "error" not in r]
    errors = [r for r in res["rows"] if "error" in r]

    claims = list(csv.DictReader(open(ROOT / "ledger" / "claimed_scores_20261024.csv")))
    claimed_files = {c["registry_match_file"] for c in claims if c["registry_match_file"]}
    digests = json.loads((REG / "decoded_digests.json").read_text())
    uniq_by_dec = {r["decoded_sha256"]: r for r in index["rasters"]}
    # which distinct contents carry a claimed score
    claimed_dec = set()
    for rec in full_index["rasters"]:
        src = rec["sources"][0]
        if src in claimed_files:
            claimed_dec.add(digests[rec["sha256"]])
    # parent R0 is a data file, not a registry blob: tie it by decoded content
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        import hashlib
        a = ds.read(1).astype(np.float32)
    a = np.where(np.isfinite(a), a, 0.0).astype(np.float32)
    a[~fp] = 0
    claimed_dec.add(hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest())

    def tier_of(r):
        dec = r.get("decoded_sha256")
        return dict(S=dec in claimed_dec, L=r["halo_coverage"] < BLANKET_HALO, T=True)

    n_files = {r["decoded_sha256"]: uniq_by_dec[r["decoded_sha256"]].get("n_files_sharing_decoded_content", 1) for r in rows}

    def summarize(sel):
        rs = [r for r in rows if sel(r)]
        if not rs:
            return dict(n_distinct=0)
        ov = [r["forward_overlap"] for r in rs]
        rho = [abs(r["spearman_full_footprint"]) for r in rs if r.get("spearman_full_footprint") is not None]
        over = [r for r in rs if r["forward_overlap"] > OVERLAP_LIMIT]
        rho_over = [r for r in rs if r.get("spearman_full_footprint") is not None and abs(r["spearman_full_footprint"]) > RHO_LIMIT]
        worst = sorted(rs, key=lambda r: -r["forward_overlap"])[:8]
        return dict(
            n_distinct=len(rs), n_files=int(sum(n_files[r["decoded_sha256"]] for r in rs)),
            max_forward_overlap=max(ov), n_distinct_over_0_70=len(over),
            n_files_over_0_70=int(sum(n_files[r["decoded_sha256"]] for r in over)),
            max_abs_spearman=max(rho) if rho else None, n_distinct_over_rho_0_90=len(rho_over),
            worst=[dict(submission=w["submission"], forward_overlap=w["forward_overlap"], halo_coverage=w["halo_coverage"],
                        their_dots=w["their_dots"], abs_spearman=(abs(w["spearman_full_footprint"]) if w.get("spearman_full_footprint") is not None else None))
                   for w in worst])

    out = dict(
        schema="gemsdoe92-registry-gate.v1", evidence_class="REGISTRY-MEASUREMENT", phase=args.phase,
        candidate_file=str(args.candidate.name), candidate_dots=int(((mine > 0) & fp).sum()),
        candidate_sha256=_sha256_file(args.candidate),
        thresholds=dict(forward_overlap=OVERLAP_LIMIT, abs_spearman=RHO_LIMIT, radius_px=3.0),
        scope=("Hash-verified cached public default-branch rasters of the owner's GEMSDOE repositories (docs/downloads, releases, "
               "submission* paths); distinct decoded contents compared with the shared vendor function and fanned out to all files "
               "sharing the content. NOT organizer-complete: history, private repos, other owners, zip-only/site-only objects absent; "
               f"{len(full_index.get('errors', []))} index errors, 5 non-single-band/grid-mismatch files and 1 invalid TIFF excluded at cache time."),
        n_files_total=index.get("n_files_total"), n_distinct_compared=len(rows), compare_errors=len(errors),
        tier_S=summarize(lambda r: tier_of(r)["S"]),
        tier_L=summarize(lambda r: tier_of(r)["L"]),
        tier_T_all=summarize(lambda r: True),
        blankets=dict(n_distinct=sum(r["halo_coverage"] >= BLANKET_HALO for r in rows),
                      threshold_halo_coverage=BLANKET_HALO,
                      note=("A raster whose 3 px halo covers >= 50 % of the footprint is hit by random placement at >= 50 % and by any "
                            "candidate in the fault-rich terrain at ~100 %; a 70 % threshold cannot identify a lane against it.")),
        complete_accessible_scan=bool(res.get("complete_accessible_scan")),
        seconds=round(time.time() - t0),
    )
    # compact per-raster table for the site / audit (distinct contents)
    out["rows"] = [dict(submission=r["submission"], decoded_sha256=r["decoded_sha256"], their_dots=r["their_dots"],
                        halo_coverage=r["halo_coverage"], forward_overlap=r["forward_overlap"],
                        reverse_overlap=r["their_dots_within_3px_of_mine"], abs_spearman=(abs(r["spearman_full_footprint"]) if r.get("spearman_full_footprint") is not None else None),
                        tier_S=tier_of(r)["S"], tier_L=tier_of(r)["L"]) for r in rows]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("phase", "tier_S", "tier_L")}, indent=1)[:2500])
    print("T_all:", {k: v for k, v in out["tier_T_all"].items() if k != "worst"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
