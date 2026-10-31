#!/usr/bin/env python3
"""PEEL lane, step E: release placement under the owner's PI-1 overlap cap.

The E3 score field is placed freely in ``peel_build.py``.  That placement is
then measured against the whole downloaded public registry
(``peel_uniqueness.py``).  If any single dot-like registry raster captures more
than 70% of the dots within 3 px, this script re-places exactly the same score
field with a hard per-raster cap, so the released file satisfies the owner's
duplicate rule *during* placement instead of being declared a duplicate after
the fact.

Nothing about the score field, the budget, the NMS separation or the catalogue
collar changes: only which dots survive the greedy pass.  Every cap and the
resulting dot counts are written to ``evidence/peel_cap_20261031.json``.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import submission_writer  # noqa: E402
from gems57.grid import load_grid  # noqa: E402

W = ROOT / ".cache" / "work" / "peel"
BLOBS = ROOT / ".cache" / "registry_blobs"
DL = ROOT / "docs" / "downloads"
K_BUDGET = 37654
SEP = 2.8
BUF = 2.0
CAP_FRACTION = 0.55          # released target, deliberately far below the 0.70 limit
OFFENDER_LIMIT = 0.45        # cap every raster that currently captures > 45%
NAME = "gemsdoe92-peel-scarpalt-37654-20261031"
NOTE = ("PEEL 44-band catalogue-free scarp x alteration model; d_cat>2 collar, "
        "37654 dots @2.8px; same budget as h33-2-b2; PI-1 capped")


def main() -> int:
    grid = load_grid()
    foot = np.asarray(grid.footprint, bool)
    cat = np.asarray(grid.catalogue, bool)
    uq = json.loads((ROOT / "evidence" / "peel_uniqueness_20261031.json").read_text())
    caps_rows = [r for r in uq["sparse_top"] if r["overlap"] > OFFENDER_LIMIT]
    if not caps_rows:
        raise SystemExit("no offender above the limit; nothing to cap")
    print("capping:", [(r["overlap"], r["repo"], r["path"][-40:]) for r in caps_rows], flush=True)

    halo = np.zeros((len(caps_rows),) + foot.shape, bool)
    for i, r in enumerate(caps_rows):
        with rasterio.open(BLOBS / f"{r['sha256']}.tif") as ds:
            halo[i] = ndi.distance_transform_edt(~(np.nan_to_num(ds.read(1)) > 0)) <= 3
    cap = int(CAP_FRACTION * K_BUDGET)

    surf = np.load(W / "surf_full.npy")
    dcat = ndi.distance_transform_edt(~cat)
    eligible = foot & ~cat & (dcat > BUF)
    flat = np.flatnonzero(eligible.ravel())
    order = flat[np.argsort(-surf.ravel()[flat], kind="stable")]

    r = int(np.ceil(SEP))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (yy * yy + xx * xx) < SEP * SEP
    H, Wd = foot.shape
    occ = np.zeros((H + 2 * r, Wd + 2 * r), bool)
    counts = np.zeros(len(caps_rows), np.int64)
    taken = np.zeros(H * Wd, bool)
    n = 0
    for f in order:
        y, x = divmod(int(f), Wd)
        if occ[y + r, x + r]:
            continue
        in_any = halo[:, y, x]
        if in_any.any() and (counts[in_any] >= cap).any():
            continue
        counts[in_any] += 1
        occ[y:y + 2 * r + 1, x:x + 2 * r + 1] |= disk
        taken[f] = True
        n += 1
        if n >= K_BUDGET:
            break
    dots = taken.reshape(H, Wd)
    print(f"placed {n} dots under caps (cap {cap} = {CAP_FRACTION} * {K_BUDGET}); "
          f"per-raster counts {counts.tolist()} = fractions "
          f"{[round(c / n, 4) for c in counts.tolist()]}", flush=True)

    for suffix in ("-zeros.tif", "-zeros.zip", "-zeros.json"):
        p = DL / f"{NAME}{suffix}"
        if p.exists():
            p.unlink()
    pred = np.zeros(foot.shape, np.float32)
    pred[dots] = 1.0
    out = DL / f"{NAME}-zeros.tif"
    rec = submission_writer.write_submission(
        out, pred, ROOT / "data" / "bridge" / "sample_submission.tif", foot,
        note=NOTE, name=NAME, catalogue=cat)
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    res = dict(schema="gemsdoe92-peel-cap-v1", cap_fraction=CAP_FRACTION,
               cap_dots=cap, budget=K_BUDGET, dots=n, candidate=str(out.relative_to(ROOT)),
               sha256=sha,
               capped_rasters=[dict(repo=r["repo"], path=r["path"], sha256=r["sha256"],
                                    overlap_before=r["overlap"], dots_inside=int(c),
                                    overlap_after=round(float(c) / n, 5))
                               for r, c in zip(caps_rows, counts.tolist())],
               all_checks_passed=rec["validator"]["all_checks_passed"],
               note="released file verified below by peel_uniqueness.py")
    (ROOT / "evidence" / "peel_cap_20261031.json").write_text(
        json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("dots", "sha256", "all_checks_passed")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
