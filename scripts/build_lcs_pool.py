#!/usr/bin/env python3
"""LCS step 1: consensus pool, credit scores, and registry halo membership.

Outputs (gitignored cache, rebuilt deterministically):
  .cache/lcs/pool.npz            candidate pixels + votes + stratified excess + credit score
  .cache/lcs/member_packed.npy   packed bool (n_rasters, ceil(pool/8)): pool pixel within 3 px of raster r
  .cache/lcs/member_keys.json    raster identity for each membership row
Tracked evidence:
  evidence/lcs_pool_summary.json

Voters are the independent lanes in scripts/lb_concordance.py (organizer-CLAIMED scores
-> MODEL credit per dot).  Nothing here reads the withheld holdout; the catalogue enters
only through the d_cat > 3.0 px exclusion (brief constraint 4) and the halo-survival profile.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems import lcs  # noqa: E402
from gems57 import grid as grid_mod  # noqa: E402

CACHE = ROOT / ".cache" / "lcs"
REG = ROOT / ".cache" / "gemsdoe_public_registry"
BLANKET_HALO = 0.50   # halo-coverage cut that defines Tier L vs blankets (see registry/uniqueness_policy.json)


def _load_lanes_module():
    spec = importlib.util.spec_from_file_location("lbc", ROOT / "scripts" / "lb_concordance.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    lbc = _load_lanes_module()
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    fp, cat = grid.footprint, grid.catalogue
    nfp = int(fp.sum())
    d_cat = ndi.distance_transform_edt(~cat).astype(np.float32)

    # ---- voters: dots, halos, LB-implied credit (MODEL) -------------------------------
    c_rand = lcs.random_dot_credit(nfp)
    voters = {}
    for key, sub, repo, score, _ in lbc.LANES:
        p = lbc.find_file(sub, repo)
        with rasterio.open(p) as ds:
            a = ds.read(1)
        dots = np.isfinite(a) & (a > 0) & fp
        n = int(dots.sum())
        halo = (ndi.distance_transform_edt(~dots) <= lcs.RADIUS_PX) & fp
        voters[key] = dict(dots=dots, halo=halo, n=n, score=score, credit=lcs.credit_per_dot(score, n),
                           file=str(p.relative_to(ROOT)) if str(p).startswith(str(ROOT)) else str(p),
                           sha256=sha256_file(p))
    w = lcs.lane_weights({k: v["credit"] for k, v in voters.items()}, c_rand)

    # ---- pool = union of voter dots, > 3 px from every mapped fault (brief constraint 4) ------------------
    vote_keys = [k for k in voters if "sgmc" not in k]       # SGMC lanes are negative controls, not voters
    pool = np.zeros(fp.shape, bool)
    for k in vote_keys:
        pool |= voters[k]["dots"]
    pool &= (d_cat > lcs.MIN_CATALOGUE_DISTANCE_PX) & fp
    votes = np.zeros(fp.shape, np.float32)
    count = np.zeros(fp.shape, np.int8)
    for k in vote_keys:
        votes += np.float32(w[k]) * voters[k]["halo"]
        count += voters[k]["halo"]
    strata = lcs.stratum_index(d_cat)
    z = lcs.stratified_excess(votes, strata, pool)

    with rasterio.open(ROOT / "data" / "bridge" / "h19_5.tif") as ds:
        h195 = np.nan_to_num(ds.read(1)) > 0
    edges, surv, bg = lcs.halo_survival_profile(d_cat, fp, h195)
    score = lcs.credit_score(z, d_cat, edges, surv).astype(np.float32)

    yx = np.argwhere(pool).astype(np.int32)
    flat = pool.ravel()
    np.savez_compressed(
        CACHE / "pool.npz", yx=yx, votes=votes[pool], z=z[pool], score=score[pool], d_cat=d_cat[pool],
        lane_count=count[pool], strata=strata[pool],
        survival_edges=edges, survival=surv, background_enrichment=np.float64(bg))
    print(f"pool {len(yx):,} px; lane-count histogram {np.bincount(count[pool].astype(int)).tolist()}", flush=True)

    # ---- membership against every distinct sparse registry raster -----------------------
    uniq = json.loads((REG / "registry_index_unique.json").read_text())
    keys, packed_rows, blanket_rows, empty_rows = [], [], [], []
    disk = np.zeros((7, 7), bool)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            disk[dy + 3, dx + 3] = dy * dy + dx * dx <= 9      # identical to gems57.uniqueness._near at 3 px
    coverage_all = {}
    for k, rec in enumerate(uniq["rasters"]):
        with rasterio.open(rec["cache_file"]) as ds:
            a = ds.read(1).astype(np.float32)
        a = np.where(np.isfinite(a), a, 0.0)
        a[~fp] = 0
        sup = a > 0
        n = int(sup.sum())
        row = dict(decoded_sha256=rec["decoded_sha256"], n_dots=n, source=rec["sources"][0],
                   n_files_sharing=rec.get("n_files_sharing_decoded_content", 1))
        if n == 0:
            empty_rows.append(row)
            continue
        # classify by 3 px halo coverage of the footprint (what the overlap test actually sees), never by support alone
        cov_r = float(ndi.binary_dilation(sup, structure=disk)[fp].mean())
        row["halo_coverage"] = cov_r
        coverage_all[rec["decoded_sha256"]] = cov_r
        if cov_r >= BLANKET_HALO:
            blanket_rows.append(row)
            continue
        tree = cKDTree(np.argwhere(sup))
        dist, _ = tree.query(yx, k=1, distance_upper_bound=lcs.RADIUS_PX + 1e-6)
        member = np.isfinite(dist)
        row["pool_coverage"] = float(member.mean())
        keys.append(row)
        packed_rows.append(np.packbits(member))
        if (k + 1) % 100 == 0:
            print(f"  membership {k + 1}/{len(uniq['rasters'])}", flush=True)
    (CACHE / "halo_coverage.json").write_text(json.dumps([dict(decoded_sha256=h, halo_coverage=c) for h, c in coverage_all.items()]))
    np.save(CACHE / "member_packed.npy", np.vstack(packed_rows))
    (CACHE / "member_keys.json").write_text(json.dumps(dict(sparse=keys, blanket=blanket_rows, empty=empty_rows)))
    summary = dict(
        evidence_class="MODEL+REGISTRY-MEASUREMENT", pool_pixels=int(len(yx)),
        voters={k: dict(n=v["n"], score_claim=v["score"], credit_per_dot=v["credit"], vote_weight=w[k],
                        file=v["file"], sha256=v["sha256"], used_as_voter=(k in vote_keys)) for k, v in voters.items()},
        c_random=c_rand, background_enrichment=bg,
        halo_survival={str(d): float(np.interp(d, edges, surv)) for d in (2, 3, 4, 5, 7, 10, 15, 20)},
        lane_count_hist=np.bincount(count[pool].astype(int)).tolist(),
        registry=dict(distinct_decoded=len(uniq["rasters"]), tier_L_members=len(keys), blankets=len(blanket_rows), empty=len(empty_rows)),
        constants=dict(G_EST=lcs.G_EST, GAMMA=lcs.GAMMA, CAP_FRACTION=lcs.CAP_FRACTION, N_TARGET=lcs.N_TARGET,
                       MIN_SPACING_SQ=lcs.MIN_SPACING_SQ, STRATA_EDGES=list(lcs.STRATA_EDGES[:-1])),
    )
    (ROOT / "evidence" / "lcs_pool_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary["registry"]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
