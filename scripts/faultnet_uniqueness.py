#!/usr/bin/env python3
"""Registry uniqueness for FAULTNET candidates (protocol rule 1), pre-placement AND final.

Registry = every indexed public GEMSDOE* raster (``.cache/registry_index``, built by
``scripts/build_public_registry_index.py``; Git-blob verified) + local lineage/data
rasters not already indexed (dedup by SHA-256).

For each candidate and each registry raster we report:
  * ``rho_final``   Spearman of the submitted binary raster (100k-pixel fixed subsample)
  * ``rho_surface`` Spearman of the pre-placement surface
  * ``overlap_final``  fraction of our dots within 3 px of the registry raster's dots
                       (dot fields: literal support; continuous surfaces: matched-budget top-n)
  * ``overlap_surface_topn``  same, for the surface's raw top-n pixels before spacing
  * ``overlap_literal`` fraction of our dots within 3 px of ANY positive registry pixel
                       (published for transparency; see #IR-92-FAULTNET-DOT-DEFINITION)
Duplicate (lane drift) iff max |rho| > 0.90 or max operative overlap > 0.70.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
IDX = ROOT / ".cache" / "registry_index"
BLOBS = ROOT / ".cache" / "gemsdoe_public_registry"
INPUTS = ROOT / ".cache" / "gems_inputs"
RHO_MAX, OVL_MAX, DOT_FIELD_MAX = 0.90, 0.70, 150_000
OFFS = [(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if dy * dy + dx * dx <= 9]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def unit_ranks(v: np.ndarray) -> np.ndarray:
    r = rankdata(v.astype(np.float64))
    r -= r.mean()
    n = np.linalg.norm(r)
    return (r / n).astype(np.float32) if n > 0 else np.zeros(v.size, np.float32)


def neighbours(mask: np.ndarray) -> np.ndarray:
    h, w = mask.shape
    yy, xx = np.nonzero(mask)
    out = np.empty((len(OFFS), yy.size), np.int64)
    for k, (dy, dx) in enumerate(OFFS):
        out[k] = np.clip(yy + dy, 0, h - 1) * w + np.clip(xx + dx, 0, w - 1)
    return out


def overlap(nb: np.ndarray, their_flat_idx: np.ndarray, size: int) -> float:
    bm = np.zeros(size, bool)
    bm[their_flat_idx] = True
    return float(bm[nb].any(axis=0).mean())


def screen(cands: dict[str, dict], foot: np.ndarray) -> dict:
    meta_doc = json.loads((IDX / "meta.json").read_text())
    meta = meta_doc["meta"]
    sub = np.load(IDX / "sub_idx.npy")
    ranks = np.load(IDX / "ranks.npy", mmap_mode="r")
    size = foot.size
    known = {m["sha256"] for m in meta}
    # local extras (lineage + data) not in the public index
    extras = []
    for d in (INPUTS / "lineage", ROOT / "data", ROOT / "data" / "bridge"):
        for p in sorted(d.glob("*.tif")):
            if p.name in ("sample_submission.tif", "existing_faults.tif", "labels.tif"):
                continue
            s = sha256(p)
            if s in known:
                continue
            known.add(s)
            with rasterio.open(p) as ds:
                v = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
            v[~foot] = 0
            extras.append((str(p.relative_to(ROOT)), s, v))

    prepared = {}
    for name, c in cands.items():
        dots = c["dots"]
        surf = np.where(foot, c["surface"], 0).astype(np.float32)
        n = int(dots.sum())
        flat = surf.ravel()
        fidx = np.flatnonzero(foot.ravel())
        top = fidx[np.argpartition(-flat[fidx], n - 1)[:n]]
        topm = np.zeros(size, bool); topm[top] = True
        prepared[name] = dict(n=n, nb_final=neighbours(dots), nb_top=neighbours(topm.reshape(foot.shape)),
                              r_final=unit_ranks(dots.ravel()[sub].astype(np.float32)),
                              r_surf=unit_ranks(flat[sub]))
    rows = {name: [] for name in cands}
    # Spearman against all indexed rasters in one pass (chunked, memory-mapped)
    rho_f = {k: np.zeros(len(meta)) for k in cands}
    rho_s = {k: np.zeros(len(meta)) for k in cands}
    for i0 in range(0, len(meta), 128):
        R = np.asarray(ranks[i0:i0 + 128])
        for k, pz in prepared.items():
            rho_f[k][i0:i0 + 128] = R @ pz["r_final"]
            rho_s[k][i0:i0 + 128] = R @ pz["r_surf"]
    for i, m in enumerate(meta):
        dots_idx = np.load(IDX / f"dots_{m['sha256']}.npy")
        lit_support = None
        if m["representation"] == "continuous_surface":
            with rasterio.open(BLOBS / f"{m['git_sha']}.tif") as ds:
                v = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
            lit_support = np.flatnonzero((v.ravel() > 0) & foot.ravel())
            del v
        for k, pz in prepared.items():
            n = pz["n"]
            op = dots_idx if m["representation"] == "dot_field" else dots_idx[:n]
            of = overlap(pz["nb_final"], op, size)
            ot = overlap(pz["nb_top"], op, size)
            ol = of if lit_support is None else overlap(pz["nb_final"], lit_support, size)
            rows[k].append(dict(raster=f"{m['repo']}/{m['path']}", sha256=m["sha256"], git_sha=m["git_sha"],
                                representation=m["representation"], their_positive=m["positive_support"],
                                overlap_final=round(of, 6), overlap_surface_topn=round(ot, 6),
                                overlap_literal=round(ol, 6), rho_final=round(float(rho_f[k][i]), 6),
                                rho_surface=round(float(rho_s[k][i]), 6)))
    for label, s, v in extras:
        flat = v.ravel()
        pos = np.flatnonzero(flat > 0)
        rep = "dot_field" if pos.size <= DOT_FIELD_MAX else "continuous_surface"
        rv = unit_ranks(flat[sub])
        for k, pz in prepared.items():
            n = pz["n"]
            if rep == "dot_field":
                op = pos
            else:
                op = pos[np.lexsort((pos, -flat[pos]))][:n]
            of, ot = overlap(pz["nb_final"], op, size), overlap(pz["nb_top"], op, size)
            ol = overlap(pz["nb_final"], pos, size)
            rows[k].append(dict(raster=label, sha256=s, git_sha=None, representation=rep, their_positive=int(pos.size),
                                overlap_final=round(of, 6), overlap_surface_topn=round(ot, 6), overlap_literal=round(ol, 6),
                                rho_final=round(float(rv @ pz["r_final"]), 6), rho_surface=round(float(rv @ pz["r_surf"]), 6)))
    out = {}
    for k, rr in rows.items():
        def worst(key, absval=False):
            r = max(rr, key=lambda x: abs(x[key]) if absval else x[key])
            return dict(value=r[key], raster=r["raster"], representation=r["representation"], their_positive=r["their_positive"])
        # operative: final-dot overlap + rank-correlation of the final raster AND the pre-placement surface.
        # overlap_surface_topn (raw unspaced top-n of the surface) is diagnostic only: "your dots" exist only after placement.
        dup = [r for r in rr if r["overlap_final"] > OVL_MAX
               or abs(r["rho_final"]) > RHO_MAX or abs(r["rho_surface"]) > RHO_MAX]
        lit_dup = [r for r in rr if r["overlap_literal"] > OVL_MAX]
        top = sorted(rr, key=lambda x: -x["overlap_final"])[:15]
        n_ours = prepared[k]["n"]
        within = [r for r in rr if r["representation"] == "continuous_surface" or r["their_positive"] <= 1.25 * n_ours]
        over = [r for r in rr if r["representation"] == "dot_field" and r["their_positive"] > 1.25 * n_ours]
        out[k] = dict(registry_rasters_checked=len(rr), public_indexed=len(meta), local_extras=len(extras),
                      worst_overlap_final=worst("overlap_final"), worst_overlap_surface_topn=worst("overlap_surface_topn"),
                      worst_abs_rho_final=worst("rho_final", True), worst_abs_rho_surface=worst("rho_surface", True),
                      duplicates_operative=len(dup), duplicate_examples=[d["raster"] for d in dup[:10]],
                      unique_operative=len(dup) == 0,
                      literal_reading=dict(rasters_over_0p70=len(lit_dup),
                                           full_footprint_surfaces=sum(1 for r in rr if r["their_positive"] >= 5_000_000),
                                           note="literal positive-support reading; every non-empty raster fails against full-footprint surfaces"),
                      budget_split=dict(
                          within_1p25x_budget=dict(n=len(within), worst=max((r["overlap_final"] for r in within), default=None),
                                                   over_0p70=sum(r["overlap_final"] > OVL_MAX for r in within)),
                          overbudget_dot_fields=dict(n=len(over), worst=max((r["overlap_final"] for r in over), default=None),
                                                     over_0p70=sum(r["overlap_final"] > OVL_MAX for r in over),
                                                     rasters_over_0p70=[dict(raster=r["raster"], their_positive=r["their_positive"],
                                                                             overlap_final=r["overlap_final"]) for r in over if r["overlap_final"] > OVL_MAX])),
                      top15_by_overlap=top)
    return dict(schema="gemsdoe92-faultnet-uniqueness-v1", evidence_class="REGISTRY-MEASUREMENT",
                thresholds=dict(rho=RHO_MAX, overlap=OVL_MAX, radius_px=3, dot_field_max_support=DOT_FIELD_MAX),
                index_built_utc=meta_doc["built_utc"], repos_scanned=meta_doc["repos_scanned"],
                unique_blobs=meta_doc["unique_blobs"], index_skipped=meta_doc["skipped"],
                spearman_subsample=int(sub.size), results=out)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", nargs="+", default=["netctx", "netdens", "netfar"])
    ap.add_argument("--out", default=str(ROOT / "evidence" / "faultnet_uniqueness.json"))
    ap.add_argument("--null", action="store_true", help="add a ridge-gated random 37,654-dot null candidate (gate calibration)")
    a = ap.parse_args()
    with rasterio.open(INPUTS / "bridge" / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    C = ROOT / ".cache" / "faultnet"
    surf_of = {"netctx": "netctx", "netfar": "netctx", "netdens": "netdens"}
    cands = {arm: dict(dots=np.load(C / f"dots_{arm}.npy"), surface=np.load(C / f"S_{surf_of[arm]}.npy")) for arm in a.arms}
    if a.null:
        sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
        from scipy.ndimage import distance_transform_edt
        from gems import coulomb_loqo as cl
        from gems57 import grid as grid_mod
        cat = grid_mod.load_grid(INPUTS / "bridge").catalogue
        S = np.load(C / "S_netctx.npy")
        valid = foot & (S > 0)
        ridge = cl.directional_ridge_1d(S, valid)
        rnd = np.random.default_rng(20261025).random(foot.shape).astype(np.float32)
        allowed = foot & valid & ridge & (distance_transform_edt(~cat) > 4.0)
        dots = cl.spaced_top_mask(rnd, allowed, int(cands[a.arms[0]]["dots"].sum()), min_dist_px=2.8, cand_cap=900_000)
        cands["null_ridge_random"] = dict(dots=dots, surface=rnd * allowed)
    res = screen(cands, foot)
    Path(a.out).write_text(json.dumps(res, indent=1))
    for k, r in res["results"].items():
        print(k, "unique_operative=", r["unique_operative"], "worst_overlap_final=", r["worst_overlap_final"],
              "worst_rho=", r["worst_abs_rho_final"]["value"], r["worst_abs_rho_surface"]["value"],
              "literal>0.70:", r["literal_reading"]["rasters_over_0p70"])
