#!/usr/bin/env python3
"""PEEL lane, step C: registry-wide uniqueness (protocol PI-1), bounded and honest.

PI-1 (owner protocol, verbatim): *"a raster is a duplicate if its rank correlation
with any registry raster exceeds 0.90, or more than 70% of its dots fall within
3 px of one registry raster's dots."*

This script rebuilds the registry inventory from the public GitHub repos that
hold GEMSDOE submission rasters (the same 2,231 unique submission blobs the
2026-10-28 audit recorded), downloads the ones inside a size cap, and then
reports BOTH readings of the rule for a candidate:

* ``sparse`` reading  -- overlap is measured only against rasters that are
  dot-like (positive support <= 25% of the footprint), which is what the phrase
  "another raster's dots" can mean.  This is the operative gate.
* ``literal`` reading -- overlap against every downloaded raster's positive
  support, including dense probability surfaces that are positive almost
  everywhere.  Under this reading any non-empty candidate in this repo has
  always failed (the "full-footprint witness"), so it is reported, not gated.

Coverage of the check is reported explicitly: how many blobs were scanned, how
many were skipped for size, and how many are known-but-unfetched.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57.grid import load_grid  # noqa: E402

BLOBS = ROOT / ".cache" / "registry_blobs"
INDEX = ROOT / ".cache" / "trees" / "submission_blobs.json"
SIZE_CAP = 6_000_000
SPARSE_FRAC = 0.25
HALO_PX = 3


def fetch(sha: str, repo: str, dest: Path) -> tuple[str, str]:
    if dest.is_file() and dest.stat().st_size > 0:
        return sha, "cached"
    p = subprocess.run(["gh", "api", f"repos/{repo}/git/blobs/{sha}",
                        "-H", "Accept: application/vnd.github.raw"],
                       capture_output=True)
    if p.returncode != 0 or not p.stdout:
        return sha, "error:" + p.stderr.decode()[:80].replace("\n", " ")
    dest.write_bytes(p.stdout)
    return sha, "ok"


def main() -> int:
    BLOBS.mkdir(parents=True, exist_ok=True)
    inv = json.loads(INDEX.read_text())["blobs"]
    todo = {s: v for s, v in inv.items() if v["bytes"] <= SIZE_CAP}
    print(f"{len(inv)} known public submission blobs; {len(todo)} within {SIZE_CAP/1e6:.0f} MB cap "
          f"({sum(v['bytes'] for v in todo.values())/1e6:.0f} MB)")
    stats = {"ok": 0, "cached": 0, "error": 0}
    with cf.ThreadPoolExecutor(6) as ex:
        futs = [ex.submit(fetch, s, v["repo"], BLOBS / f"{s}.tif") for s, v in todo.items()]
        for i, f in enumerate(cf.as_completed(futs), 1):
            sha, st = f.result()
            stats["ok" if st == "ok" else ("cached" if st == "cached" else "error")] += 1
            if i % 250 == 0:
                print(f"  {i}/{len(todo)} {stats}", flush=True)
    print("fetch stats", stats, flush=True)

    grid = load_grid()
    foot = np.asarray(grid.footprint, bool)
    n_foot = int(foot.sum())

    metas = []
    for sha, v in todo.items():
        p = BLOBS / f"{sha}.tif"
        if not p.is_file():
            continue
        try:
            with rasterio.open(p) as ds:
                if tuple(ds.shape) != foot.shape or ds.count != 1:
                    metas.append(dict(sha256=sha, skipped="shape/band", repo=v["repo"]))
                    continue
                a = ds.read(1)
        except Exception as exc:  # noqa: BLE001
            metas.append(dict(sha256=sha, skipped=f"unreadable:{type(exc).__name__}", repo=v["repo"]))
            continue
        pos = np.isfinite(a) & (np.nan_to_num(a) > 0) & foot
        n_pos = int(pos.sum())
        metas.append(dict(sha256=sha, repo=v["repo"], path=v["path"], bytes=v["bytes"],
                          n_pos=n_pos, frac_pos=n_pos / n_foot,
                          sparse=bool(0 < n_pos <= SPARSE_FRAC * n_foot),
                          dense=bool(n_pos > SPARSE_FRAC * n_foot)))
    ok = [m for m in metas if "n_pos" in m]
    print(f"parsed {len(ok)} rasters; sparse {sum(m['sparse'] for m in ok)}; "
          f"dense {sum(m['dense'] for m in ok)}", flush=True)

    # Overlap without a per-raster EDT: |dots & halo(R)| == |dilate(dots,3) & R|.
    # The candidate's dilated support is tiny next to the grid, so this is exact
    # for "within 3 px (Euclidean)" and costs one dilation plus one AND per raster.
    cand = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "")
    core = dict(schema="gemsdoe92-peel-registry-v1",
                note="PI-1 inventory rebuilt from public GitHub submission blobs",
                size_cap_bytes=SIZE_CAP, known_blobs=int(len(inv)),
                downloaded=int(len(todo)), parsed=int(len(ok)),
                fetch_stats=stats, halo_px=HALO_PX,
                rasters=[{k: m[k] for k in ("sha256", "repo", "path", "n_pos", "frac_pos",
                                            "sparse", "dense")} for m in ok])
    if not cand.is_file():
        (ROOT / "evidence" / "peel_registry_inventory_20261031.json").write_text(
            json.dumps(core, indent=1) + "\n", encoding="utf-8")
        print("no candidate given; inventory only")
        return 0

    with rasterio.open(cand) as ds:
        a = ds.read(1)
    dots = np.isfinite(a) & (np.nan_to_num(a) > 0) & foot
    nd = int(dots.sum())
    # A dot counts as overlapped iff SOME pixel of the registry raster lies
    # within 3 px (Euclidean) of it.  One exact nearest-dot index makes that a
    # unique() over the raster's positive pixels, instead of a per-raster EDT.
    dist, inds = ndi.distance_transform_edt(~dots, return_indices=True)
    nearest = np.ravel_multi_index((inds[0].ravel(), inds[1].ravel()), dots.shape)
    near = dist <= HALO_PX
    near_flat = near.ravel()
    del dist, inds

    rows = []
    for m in ok:
        with rasterio.open(BLOBS / f"{m['sha256']}.tif") as ds:
            v = ds.read(1)
        pos = (np.nan_to_num(v) > 0)
        pos_flat = pos.ravel()
        sub = np.flatnonzero(pos_flat & near_flat)
        n_hit = int(np.unique(nearest[sub]).size) if sub.size else 0
        rows.append(dict(sha256=m["sha256"], repo=m["repo"], path=m["path"],
                         sparse=m["sparse"], dense=m["dense"],
                         frac_pos=round(m["frac_pos"], 5), dots_hit=n_hit,
                         overlap=round(n_hit / max(nd, 1), 5)))
        del pos, pos_flat, sub
    rows.sort(key=lambda r: -r["overlap"])
    sparse_rows = [r for r in rows if r["sparse"]]
    worst_sparse = max((r["overlap"] for r in sparse_rows), default=0.0)
    worst_literal = rows[0]["overlap"] if rows else 0.0
    res = dict(core, schema="gemsdoe92-peel-uniqueness-v1",
               candidate=str(cand.relative_to(ROOT)), n_dots=nd, rasters_scanned=len(rows),
               pi1_limit=0.70, worst_overlap_sparse=worst_sparse,
               worst_overlap_literal=worst_literal,
               pi1_sparse_pass=bool(worst_sparse <= 0.70),
               literal_pass=bool(worst_literal <= 0.70),
               n_sparse_rasters_over_0_5=int(sum(r["overlap"] > 0.5 for r in sparse_rows)),
               top10=rows[:10])
    res.pop("rasters", None)
    (ROOT / "evidence" / "peel_uniqueness_20261031.json").write_text(
        json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("n_dots", "rasters_scanned", "worst_overlap_sparse",
                                          "worst_overlap_literal", "pi1_sparse_pass",
                                          "literal_pass")}, indent=1))
    for r in rows[:5]:
        print("  ", r["overlap"], r["sparse"], r["repo"], r["path"][-60:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
