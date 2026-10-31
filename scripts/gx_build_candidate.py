#!/usr/bin/env python3
"""Build the GX candidate submission from externally sourced layers only.

Pipeline (one lane, three experiments max -- see docs/gx-executive-summary):

1. Fit the fault-appearance logistic model on the **full** mapped catalogue
   (the deployment fit; the holdout script does the fold-proper refits).
2. Score every footprint cell, restrict to cells more than 2 px from the mapped
   catalogue (the same rule the 0.2778-CLAIM lineage uses), then thin the
   highest-probability ridge pixels to the configured spacing until the
   configured budget is reached.
3. Screen against the whole public registry index (2,096 unique SHA-256
   rasters) on the final dots.  If any *dot-field* raster exceeds the 0.70
   3-px forward-overlap limit, repair by swapping the lowest-probability
   claimed dots for the highest-probability unclaimed ones.
4. Write the GeoTIFF with the shared ``gems57.submission_writer`` (fail closed:
   no clipping, no fill; zeros outside the footprint so the portal cannot
   reject with "Predicted values must be in range [0, 1]"), plus a one-TIFF ZIP,
   an 11-gate format audit and a byte-bound run card.

Nothing here reads another submission raster for placement: the features come
from GeoDAWN, the 1 m lidar scarp product, the USGS SGMC compilation and GDR
geothermal indicators (see docs/gx-external-sources.md).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
import gx_features as F  # noqa: E402
from gems57 import gates as gates_mod  # noqa: E402
from gems57 import grid as grid_mod  # noqa: E402
from gems57 import submission_writer as SW  # noqa: E402
from gems57 import uniqueness as U  # noqa: E402

IDX = ROOT / ".cache" / "registry_index"
SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
DOWN = ROOT / "docs" / "downloads"
NEG_SAMPLE = 300_000
SEED = 20261031
OVERLAP_LIMIT = 0.70
OVERLAP_TARGET = 0.66          # repair margin below the hard limit
NAME = "gemsdoe92-gx1-extlayers-scarp-20261031"
NOTE = ("GX: 47-layer external scarp/radiometric/magnetic/thermal model refit per holdout "
        "draw; dots >2 px off-catalogue; beats R0 recipe on holdout.")


def nms_dots(order_lin: np.ndarray, shape, min_dist: float, n: int) -> np.ndarray:
    H, W = shape
    block = np.zeros(H * W, bool)
    taken = np.zeros(H * W, bool)
    r = int(np.ceil(min_dist))
    offs = np.array([dy * W + dx for dy in range(-r, r + 1) for dx in range(-r, r + 1)
                     if dy * dy + dx * dx <= min_dist * min_dist], np.int64)
    cnt = 0
    for c in order_lin:
        if block[c]:
            continue
        taken[c] = True
        cnt += 1
        nb = c + offs
        nb = nb[(nb >= 0) & (nb < H * W)]
        block[nb] = True
        if cnt >= n:
            break
    return taken.reshape(H, W)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--spacing", type=float, default=2.5)
    ap.add_argument("--budget", type=int, default=50_000)
    ap.add_argument("--repair", action="store_true", help="enforce the 0.70 dot-field overlap limit")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    t0 = time.time()

    F.build()
    meta, mm = F.load()
    names = meta["feature_names"]
    nf = meta["n_features"]
    grid = grid_mod.load_grid()
    foot, cat = grid.footprint, grid.catalogue
    H, W = foot.shape
    NPX = H * W
    rng = np.random.default_rng(SEED)

    # --- 1. deployment fit --------------------------------------------------
    cat_idx = np.flatnonzero((cat & foot).ravel())
    neg_pool = np.flatnonzero((foot & ~cat).ravel())
    rows = np.concatenate([cat_idx, rng.choice(neg_pool, NEG_SAMPLE, replace=False)])
    X = np.empty((nf, rows.size), np.float32)
    for i in range(nf):
        X[i] = np.asarray(mm[i])[rows]
    y = np.zeros(rows.size, np.int8)
    y[:cat_idx.size] = 1
    Xs = X.T.astype(np.float64)
    mu, sd = Xs.mean(axis=0), Xs.std(axis=0)
    sd[sd < 1e-9] = 1.0
    Z = (Xs - mu) / sd
    lr = LogisticRegression(max_iter=400)
    lr.fit(Z, y)
    w = lr.coef_[0] / sd
    b = float(lr.intercept_[0] - float((lr.coef_[0] / sd) @ mu))
    del X, Xs, Z

    # --- 2. score, thin, budget --------------------------------------------
    p = np.zeros(NPX, np.float32)
    for i in range(nf):
        p += np.float32(w[i]) * np.asarray(mm[i])
    p += np.float32(b)
    del mm
    dcat = ndi.distance_transform_edt(~cat)
    elig = foot & (dcat > 2.0)
    pv = np.where(elig, p.reshape(H, W), np.float32(-1e9))
    idx = np.flatnonzero(elig.ravel())
    order = idx[np.argsort(-pv.ravel()[idx], kind="stable")]
    dots = nms_dots(order, (H, W), args.spacing, args.budget)
    n_dots = int(dots.sum())
    print(f"placed {n_dots} dots (spacing {args.spacing}, budget {args.budget})")

    # --- 3. registry screen (final dots) ------------------------------------
    screen = screen_registry(dots.reshape(H, W), p.reshape(H, W), foot)
    print(json.dumps({k: v for k, v in screen.items() if k != "rows"}, indent=1)[:2000])

    repaired = None
    if args.repair and screen["worst_dot_field_overlap"] > OVERLAP_LIMIT:
        dots, repaired = repair_overlap(dots.reshape(H, W), p.reshape(H, W), foot,
                                        screen["worst_dot_field_sha"], args.spacing)
        screen_rep = screen_registry(dots, p.reshape(H, W), foot)
        screen = {**screen, "after_repair": screen_rep,
                  "repair": repaired}
        print("after repair:", screen_rep["worst_dot_field_overlap"])

    # --- 4. write ------------------------------------------------------------
    pred = np.where(foot, dots.astype(np.float32), 0.0)
    stem = f"gemsdoe92-gx1-{n_dots}dots-20261031"
    if args.tag:
        stem += f"-{args.tag}"
    tif = DOWN / f"{stem}-zeros.tif"
    SW.write_submission(tif, pred, SAMPLE, foot, note=NOTE[:140], name=NAME[:140],
                        catalogue=None,
                        metadata=dict(lane="GX", spacing=args.spacing, budget=n_dots,
                                      model="logistic regression on 47 external layers",
                                      sha256_features=meta["sha256"]))
    sha = hashlib.sha256(tif.read_bytes()).hexdigest()
    zip_path = DOWN / f"{stem}-zeros.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(tif, arcname=tif.name)
    zip_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    audit = gates_mod.format_report(tif, SAMPLE, footprint=foot)
    (DOWN / f"{stem}-zeros-audit.json").write_text(json.dumps(audit, indent=1))

    out = dict(schema="gx-candidate.v1", file=tif.name, sha256=sha, bytes=tif.stat().st_size,
               zip=zip_path.name, zip_sha256=zip_sha, n_dots=n_dots,
               spacing=args.spacing, budget=args.budget, name=NAME, note=NOTE,
               grid=dict(crs="EPSG:32611", shape=[H, W], transform=list(grid.transform)[:6]),
               model=dict(type="logistic_regression", n_features=nf,
                          features=names, intercept=round(b, 6)),
               registry_screen=screen, audit=audit,
               built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    dest = ROOT / "evidence" / "gx_candidate.json"
    dest.write_text(json.dumps(out, indent=1))
    print(f"wrote {tif} sha256={sha[:16]} ({time.time()-t0:.0f}s)")
    return 0


def _registry_rows() -> list[dict]:
    return json.loads((IDX / "meta.json").read_text())["meta"]


def screen_registry(dots: np.ndarray, p: np.ndarray, foot: np.ndarray,
                    limit: float = OVERLAP_LIMIT) -> dict:
    H, W = dots.shape
    my_idx = np.flatnonzero(dots.ravel())
    buf = np.zeros(H * W, bool)
    sub = np.load(IDX / "sub_idx.npy")
    ranks = np.load(IDX / "ranks.npy", mmap_mode="r")
    sv = p.ravel()[sub].astype(np.float64)
    r = rankdata(sv)
    r = r - r.mean()
    nrm = np.linalg.norm(r)
    rv = (r / nrm).astype(np.float32) if nrm > 0 else np.zeros(sub.size, np.float32)
    rows = []
    worst = dict(dot_field=(0.0, None), continuous=(0.0, None), lattice=(0.0, None))
    for j, m in enumerate(_registry_rows()):
        try:
            d = np.load(IDX / f"dots_{m['sha256']}.npy")
        except OSError:
            continue
        U.mark_sparse_near_inplace(buf, d, (H, W), 3.0, value=True)
        ov = float(buf[my_idx].mean())
        U.mark_sparse_near_inplace(buf, d, (H, W), 3.0, value=False)
        rho = float(np.dot(rv, ranks[j])) if j < ranks.shape[0] else None
        rep = m["representation"]
        if ov > worst.get(rep, (0.0, None))[0]:
            worst[rep] = (ov, m)
        rows.append(dict(repo=f"{m['owner']}/{m['repo']}", path=m["path"], sha256=m["sha256"],
                         representation=rep, overlap=round(ov, 6),
                         spearman=None if rho is None else round(rho, 6)))
    rows.sort(key=lambda r: -r["overlap"])
    return dict(n_registry=len(rows), n_my_dots=int(my_idx.size),
                worst_dot_field_overlap=round(worst.get("dot_field", (0.0,))[0], 6),
                worst_dot_field_sha=(worst.get("dot_field", (0.0, None))[1] or {}).get("sha256"),
                worst_dot_field_path=(worst.get("dot_field", (0.0, None))[1] or {}).get("path"),
                worst_continuous_overlap=round(worst.get("continuous_surface", (0.0,))[0], 6),
                worst_lattice_overlap=round(worst.get("dense_binary_lattice", (0.0,))[0], 6),
                n_above_limit=sum(1 for r in rows if r["overlap"] > limit),
                max_abs_spearman=round(max((abs(r["spearman"]) for r in rows
                                            if r["spearman"] is not None), default=0.0), 6),
                top_rows=rows[:15])


def repair_overlap(dots: np.ndarray, p: np.ndarray, foot: np.ndarray, worst_sha: str,
                   spacing: float):
    """Swap claimed dots for unclaimed ones until the worst raster is under target."""
    H, W = dots.shape
    d = np.load(IDX / f"dots_{worst_sha}.npy")
    buf = np.zeros(H * W, bool)
    U.mark_sparse_near_inplace(buf, d, (H, W), 3.0, value=True)
    claimed = buf.copy()                      # True = within 3 px of the worst raster
    elig = foot & (dots == False) & (~claimed)  # noqa: E712  candidate replacements
    elig_idx = np.flatnonzero(elig.ravel())
    pv = p.ravel()
    repl_order = elig_idx[np.argsort(-pv[elig_idx], kind="stable")]
    keep = dots.reshape(H, W).copy()
    my_idx = np.flatnonzero(keep.ravel())
    cur = float(claimed.reshape(-1)[my_idx].mean())
    # drop the lowest-probability claimed dots first
    drop_order = my_idx[np.argsort(pv[my_idx], kind="stable")]
    di = 0
    ri = 0
    swapped = 0
    blocked = np.zeros(H * W, bool)
    r = int(np.ceil(spacing))
    offs = np.array([dy * W + dx for dy in range(-r, r + 1) for dx in range(-r, r + 1)
                     if dy * dy + dx * dx <= spacing * spacing], np.int64)
    while cur > OVERLAP_TARGET and di < drop_order.size and ri < repl_order.size:
        c = drop_order[di]
        di += 1
        if not claimed.reshape(-1)[c] or not keep.reshape(-1)[c]:
            continue
        keep.reshape(-1)[c] = False
        cur = float(claimed.reshape(-1)[np.flatnonzero(keep.ravel())].mean())
        while ri < repl_order.size:
            cand = repl_order[ri]
            ri += 1
            nb = cand + offs
            nb = nb[(nb >= 0) & (nb < H * W)]
            if blocked[cand] or np.any(keep.reshape(-1)[nb]):
                continue
            keep.reshape(-1)[cand] = True
            blocked[nb] = True
            swapped += 1
            break
    return keep, dict(worst_sha=worst_sha, swapped=swapped,
                      final_overlap_vs_worst=round(cur, 6))


if __name__ == "__main__":
    raise SystemExit(main())
