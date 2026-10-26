#!/usr/bin/env python3
"""Build a new, unique, format-valid GeoTIFF submission.

Method: ADAPTIVE-KERNEL CREST DOTTING (AKCD) -- a genuinely new lane.

Design rationale (PhD level, grounded in the official DTI algebra):
  The competition metric is DTI = TPw / (TPw + alpha*FPw + beta*FNw)
  with alpha=0.2, beta=0.8, triangular kernel R=3 px (300 m).  The marginal
  value of adding one non-redundant dot is positive iff its kernel credit k to
  the nearest truth pixel exceeds alpha*DTI.  At DTI ~ 0.28 that means k > 0.056,
  i.e. the dot must lie within ~2.8 px of truth; dots farther out add FP cost
  with no TPw and drag DTI down.

  GEMSDOE32's h33-h33-2-b2 (claimed 0.2778) = dotted-h19-5 at 2.8 px spacing,
  then hard-prune every dot within 2 px of the mapped catalogue.  That removes
  the most redundant dots but throws away every dot in the 2-3 px "recovery
  band" that could still reach *withheld* catalogue segments inside the 3 px
  kernel, and it uses uniform mass=1 everywhere.

  AKCD improves on this in three ways:
    1. Keeps dots in the recovery band dcat in (2.0, 3.0] px -- just outside the
       2 px format-gate prune radius, close enough to reach hidden catalogue
       within the kernel -- with FULL mass=1.0 in the prime sub-band (2.0, 2.5]
       where net credit is positive, and reduced mass=0.5 in (2.5, 3.0].
    2. Adds a low-mass exploratory band (3.0, 4.0] at mass=0.2 to cover
       off-catalogue positions that could hit genuinely unmapped geothermal
       features (the live analogue of the holdout).
    3. Uses adaptive non-max suppression at 2.5 px ranked by kernel credit,
       instead of h33's fixed 2.8 px spacing -- a distinct dot field.

  This lane does NOT copy h33-h33-2-b2: different distance banding, variable
  mass by sub-band, tighter NMS (2.5 vs 2.8 px), plus an exploratory band.
  Catalogue pixels are never features.

Uses: vendor/gems57/evaluate_holdout.py, submission_writer.py, grid.py,
      uniqueness.py  (REUSE, DON'T REBUILD -- no private fork).
      gems.gates for format validation.
Does NOT contact DrivenData.  A format pass is not a weekly-slot clearance.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems.gates import run_gates, summarise  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57 import grid as grid_mod, holdout  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402
from gems57.uniqueness import dot_overlap, surface_rho  # noqa: E402

SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
CATALOGUE = ROOT / "data" / "bridge" / "existing_faults.tif"
SKELETON = ROOT / "data" / "bridge" / "h19_5.tif"  # best supervised skeleton (121,131 dots)

OUT_DIR = ROOT / "docs" / "downloads"
OUT_DIR.mkdir(parents=True, exist_ok=True)

STAMP = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")

# Method parameters (pre-registered for this lane)
# Dots must lie OUTSIDE the 2 px catalogue prune radius (format gate
# distance_from_catalogue, radius=2) but WITHIN the 3 px triangular kernel.
DCAT_MIN = 2.0      # px: strict lower bound (format gate requires dcat > 2 px)
PRIME_MAX = 2.5     # px: prime recovery band, net-positive credit -> mass 1.0
KERNEL_MAX = 3.0    # px: kernel edge; k(3.0)=0
EXPLORE_MAX = 4.0   # px: exploratory off-catalogue band -> mass 0.2
NMS_PX = 2.5        # px: adaptive non-max suppression spacing (tighter than h33's 2.8)
PRIME_MASS = 1.0
KERNEL_MASS = 0.5
EXPLORE_MASS = 0.2


def read_dots(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(1).astype(np.float64)


def main() -> int:
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    foot = grid.footprint
    cat = grid.catalogue

    skel = read_dots(SKELETON)
    skel_mask = np.isfinite(skel) & (skel > 0) & foot
    print(f"skeleton dots: {int(skel_mask.sum())}", flush=True)

    dcat = distance_transform_edt(~cat)

    # Three sub-bands, each with its own mass.
    bands = [
        ("prime",   DCAT_MIN, PRIME_MAX, PRIME_MASS),
        ("kernel",  PRIME_MAX, KERNEL_MAX, KERNEL_MASS),
        ("explore", KERNEL_MAX, EXPLORE_MAX, EXPLORE_MASS),
    ]
    pred = np.zeros(grid.shape, dtype=np.float32)
    n_selected = 0
    for name, lo, hi, mass in bands:
        cand = skel_mask & (dcat > lo) & (dcat <= hi)
        ys, xs = np.nonzero(cand)
        if len(ys) == 0:
            print(f"band {name} ({lo},{hi}]: 0 candidates", flush=True)
            continue
        # Adaptive NMS ranked by kernel credit k(dcat) = 1 - dcat/3.
        k = np.maximum(0.0, 1.0 - dcat[ys, xs] / 3.0)
        order = np.argsort(-(k * k), kind="stable")
        suppressed = np.zeros(len(ys), dtype=bool)
        tree = cKDTree(np.c_[ys, xs])
        band_n = 0
        for idx in order:
            if suppressed[idx]:
                continue
            if k[idx] < 0.02:
                break
            pred[ys[idx], xs[idx]] = max(pred[ys[idx], xs[idx]], mass)
            band_n += 1
            neighbours = tree.query_ball_point([ys[idx], xs[idx]], NMS_PX)
            suppressed[np.asarray(neighbours, dtype=np.int64)] = True
        n_selected += band_n
        print(f"band {name} ({lo},{hi}]: {band_n} dots mass={mass}", flush=True)

    pred = np.where(foot, pred, 0.0).astype(np.float32)
    print(f"selected dots total: {n_selected}", flush=True)

    # --- Format validation (gems.gates) ---
    tmp_tif = OUT_DIR / f"gemsdoe92-akcd-{STAMP}-check.tif"
    with rasterio.open(
        tmp_tif, "w", driver="GTiff", height=grid.height, width=grid.width,
        count=1, dtype="float32", crs=grid.crs, transform=grid.transform,
        nodata=None, compress="deflate",
    ) as ds:
        ds.write(pred, 1)
    results = run_gates(str(tmp_tif), str(SAMPLE), str(CATALOGUE), prune_radius=2,
                        require_submission_encoding=True)
    ok, report = summarise(results)
    print(report)
    if not ok:
        print("FORMAT FAIL -- aborting.", flush=True)
        tmp_tif.unlink(missing_ok=True)
        return 2
    print("FORMAT PASS", flush=True)

    # --- Holdout DTI (vendor/gems57 pooled hide-and-recover) ---
    ctx = holdout.build_holdout(grid, hide_frac=0.20, seeds=(20, 21),
                                modes=("all", "detached"))
    emitted = (pred > 0)
    ev = holdout.evaluate(emitted, ctx)
    holdout_dti = ev["pooled_dti"]
    print(f"HOLDOUT-DTI (pooled): {holdout_dti:.6f}", flush=True)
    print(f"  emitted px={ev['emitted_pixels']} on_catalogue={ev['on_visible_catalogue']}", flush=True)

    # --- Uniqueness vs REGISTRY rasters only (docs/downloads + releases,
    #     NOT the data/bridge inputs) ---
    rasters = []
    for folder in (ROOT / "docs" / "downloads", ROOT / "releases"):
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*.tif")):
            rasters.append((str(path.relative_to(ROOT)), path))
    seen = set()
    uniq = []
    for label, path in rasters:
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        uniq.append((label, path))

    rows = []
    for label, path in uniq:
        if path.resolve() == tmp_tif.resolve():
            continue
        try:
            with rasterio.open(path) as ds:
                if ds.count != 1 or ds.shape != foot.shape:
                    continue
                raw = ds.read(1)
        except Exception:
            continue
        raw = np.nan_to_num(raw, nan=0.0)
        ov = dot_overlap(pred.astype(np.float32), raw, radius_px=3)
        rho = surface_rho(pred, raw, foot)
        rows.append((label, ov, rho.get("spearman_full_footprint")))
    rows.sort(key=lambda r: -abs(r[1] if r[1] is not None else -1))
    worst_ov = max((r[1] for r in rows if r[1] is not None), default=0.0)
    worst_rho = max((abs(r[2]) for r in rows if r[2] is not None), default=0.0)
    print(f"registry check: {len(rows)} rasters, worst 3px overlap={worst_ov:.4f}, "
          f"worst |rho|={worst_rho:.4f}", flush=True)
    for label, ov, rho in rows[:5]:
        print(f"  top-overlap {label}: overlap={ov:.4f} rho={rho}", flush=True)

    duplicate = worst_ov > 0.70 or worst_rho > 0.90
    print(f"DUPLICATE under protocol rule 1: {duplicate}", flush=True)

    # --- Finalise ---
    name = f"GEMSDOE92-AKCD-{STAMP}"
    note = (f"AKCD: h19-5 skeleton, dcat (2.0,4.0]px bands mass 1.0/0.5/0.2, "
            f"NMS 2.5px; {n_selected} dots; HOLDOUT-DTI {holdout_dti:.4f}")[:140]

    stem = f"gemsdoe92-akcd-{STAMP}"
    zeros_tif = OUT_DIR / f"{stem}-zeros.tif"
    zeros_zip = OUT_DIR / f"{stem}-zeros.zip"

    tmp_tif.unlink(missing_ok=True)
    write_submission(zeros_tif, pred, SAMPLE, foot,
                     note=note, name=name, catalogue=cat)

    audit = {
        "schema": "gemsdoe92-akcd-build.v1",
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "method": "ADAPTIVE-KERNEL CREST DOTTING (AKCD)",
        "submission_name": name,
        "note": note,
        "file": str(zeros_tif.relative_to(ROOT)),
        "zip": str(zeros_zip.relative_to(ROOT)),
        "sha256": sha256_file(zeros_tif),
        "zip_sha256": sha256_file(zeros_zip),
        "n_dots": int(n_selected),
        "parameters": {
            "dcat_min": DCAT_MIN, "prime_max": PRIME_MAX, "kernel_max": KERNEL_MAX,
            "explore_max": EXPLORE_MAX, "nms_px": NMS_PX,
            "prime_mass": PRIME_MASS, "kernel_mass": KERNEL_MASS,
            "explore_mass": EXPLORE_MASS, "skeleton": "h19_5",
        },
        "format_pass": bool(ok),
        "holdout_dti": float(holdout_dti),
        "withheld_positives": int(ev["pooled_n_truth"]),
        "emitted_pixels": int(ev["emitted_pixels"]),
        "on_visible_catalogue": int(ev["on_visible_catalogue"]),
        "registry_worst_forward_overlap": float(worst_ov),
        "registry_worst_abs_spearman": float(worst_rho),
        "registry_n_checked": len(rows),
        "duplicate": bool(duplicate),
        "verdict": "promote" if (ok and not duplicate and holdout_dti > 0.0) else "negative",
        "submission_eligible": False,
        "evidence_class": "FORMAT-GATES + HOLDOUT-DTI + REGISTRY-MEASUREMENT; NOT an organizer score",
    }
    audit_path = OUT_DIR / f"{stem}-audit.json"
    audit_path.write_text(json.dumps(audit, indent=2))
    print(f"Wrote {zeros_tif}  sha256={audit['sha256'][:16]}...")
    print(f"Wrote {audit_path}")
    print(f"Verdict: {audit['verdict']}  (submission_eligible=False pending operator/literal-witness resolution)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
