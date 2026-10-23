"""PRUNE axis, session 2026-10-23.

Question: does distance from the known-fault catalogue predict dead mass?

R0 keeps >= 2.24 px from the catalogue (0 dots within 2 px), but 2,171 dots
(5.77%) sit within 3 px and 5,637 (14.97%) within 5 px. The forum answer says
new-fault truth *can* lie within 300 m (3 px) of known traces
(https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516),
so widening the prune trades dead mass against real signal. That trade has a
location, and this script measures it at three doses.

Design (one axis only -- the dot-to-catalogue distance rule):
  * remove every parent dot with distance <= R px to the catalogue
  * refill to hold the count at 37,654, unit mass, by moving each removed dot to
    its NEAREST legal pixel (distance > R, inside footprint, not on catalogue)

Nearest-legal refill is deliberate: a refill drawn from a ranking would import a
second axis (MASS/ranking), which is exactly the confound that made the previous
session's MASS files ambiguous. Refilling in place keeps everything except the
distance rule constant.

Refill legality checks the H19-5 positivity mask, the field the parent lineage
came from, so refills stay on the same evidence surface as the parent.

Run:  python scripts/build_prune_variants.py [--dry-run]
Writes releases/ and appends to ledger/submissions.csv. Deterministic.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gems.gates import run_gates, summarise          # noqa: E402
from gems.ledger import append_variant, load, hash_seen  # noqa: E402
from gems.rasters import read_reference, write_candidate, sha256_file  # noqa: E402
from gems.variants import Dots, Variant             # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PARENT_ID = "h33-h33-2-b2"
EXPECTED_PARENT_DOTS = 37654
EXPECTED_PARENT_SHA = "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd"
RADII = (3, 4, 5)
DATE = dt.date.today().strftime("%Y%m%d")

PREDICTIONS = {
    3: ("+0.002 to +0.006", "removes 5.8% of dots that pay catalogue credit already counted"),
    4: ("+0.001 to +0.004", "10.2% removed; past the 3px physical uncertainty, so signal loss starts"),
    5: ("-0.002 to +0.002", "15.0% removed; new truth can sit within 3px, so this should over-prune"),
}


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                       text=True).strip()
    except Exception:
        return "UNRECORDED"


def nearest_legal_refill(removed_ys, removed_xs, candidates_ys, candidates_xs):
    """For each removed dot, the nearest unused candidate pixel. Deterministic."""
    tree = cKDTree(np.c_[candidates_ys, candidates_xs])
    used = np.zeros(len(candidates_ys), dtype=bool)
    out_y, out_x = [], []
    for y, x in zip(removed_ys, removed_xs):
        k = min(32, len(candidates_ys))
        for kk in (k, 4 * k):
            _, idxs = tree.query([y, x], k=min(kk, len(candidates_ys)))
            idxs = np.atleast_1d(idxs)
            free = [i for i in idxs if not used[i]]
            if free:
                i = free[0]
                used[i] = True
                out_y.append(candidates_ys[i])
                out_x.append(candidates_xs[i])
                break
        else:
            raise RuntimeError(f"no free refill candidate near ({y},{x})")
    return np.array(out_y), np.array(out_x)


def main(dry_run: bool = False) -> int:
    ref = read_reference(DATA / "bridge" / "sample_submission.tif")
    footprint = ref["footprint"]

    with rasterio.open(DATA / "bridge" / "labels.tif") as ds:
        labels = ds.read(1) > 0.5
    with rasterio.open(DATA / "parent_R0_nan.tif") as ds:
        parent_arr = ds.read(1)
    with rasterio.open(DATA / "bridge" / "h19_5.tif") as ds:
        h19 = ds.read(1)

    got = sha256_file(DATA / "parent_R0_nan.tif")
    if got != EXPECTED_PARENT_SHA:
        print(f"STOP: parent sha256 {got} != recorded {EXPECTED_PARENT_SHA}")
        return 2

    pys, pxs = np.nonzero(parent_arr > 0)
    if len(pys) != EXPECTED_PARENT_DOTS:
        print(f"STOP: parent has {len(pys)} dots, expected {EXPECTED_PARENT_DOTS}")
        return 2
    parent = Dots(pys, pxs, np.ones(len(pys)))

    dist = distance_transform_edt(~labels)
    d_dots = dist[pys, pxs]
    print(f"parent {EXPECTED_PARENT_DOTS} dots, min catalogue distance {d_dots.min():.3f} px")

    h19_ok = np.isfinite(h19) & (h19 > 0)
    existing = load(ROOT / "ledger" / "submissions.csv")
    built = []

    for R in RADII:
        drop = d_dots <= R
        n_drop = int(drop.sum())
        keep = ~drop

        # legal refill pixels: strictly farther than R, on the H19-5 surface,
        # inside the footprint, not already a kept dot
        cand = footprint & h19_ok & (~labels) & (dist > R) & (parent_arr <= 0)
        cy, cx = np.nonzero(cand)
        if len(cy) < n_drop:
            print(f"STOP R={R}: only {len(cy)} refill candidates for {n_drop} removals")
            return 2

        ry, rx = nearest_legal_refill(pys[drop], pxs[drop], cy, cx)
        ys = np.r_[pys[keep], ry]
        xs = np.r_[pxs[keep], rx]
        ps = np.ones(len(ys))
        v = Variant("PRUNE", f"B{R}", Dots(ys, xs, ps), len(parent),
                    int(n_drop), {"n_dropped": n_drop, "radius_px": R})
        v.check_change()
        print(f"  R={R}px: drop {n_drop} ({v.pct_changed:.2f}%), refill {len(ry)}, "
              f"total {len(v.dots)}")
        built.append((R, v))

    if dry_run:
        print("dry run: nothing written")
        return 0

    results = []
    for R, v in built:
        dots = np.zeros(ref["shape"], dtype=np.float32)
        dots[v.dots.ys, v.dots.xs] = v.dots.p.astype(np.float32)

        tmp = ROOT / "releases" / f"_tmp_R{R}.tif"
        sha = write_candidate(tmp, dots, ref, outside="nan")
        sha8 = sha[:8]
        stem = f"{PARENT_ID}-PRUNE_B{R}-{DATE}-{sha8}"
        nan_path = ROOT / "releases" / f"{stem}.tif"
        zeros_path = ROOT / "releases" / f"{stem}-zeros.tif"
        tmp.unlink()
        sha = write_candidate(nan_path, dots, ref, outside="nan")
        sha_z = write_candidate(zeros_path, dots, ref, outside="zero")
        assert sha[:8] == sha8, "sha8 drifted between identical writes"

        if hash_seen(sha, existing):
            print(f"SKIP R={R}: sha256 already in ledger")
            continue

        # gates: default 3px rule, no PRUNE exemption needed
        gate_results = run_gates(nan_path, DATA / "bridge" / "sample_submission.tif",
                                 catalogue_path=DATA / "bridge" / "labels.tif")
        ok, report = summarise(gate_results)
        print(report)
        if not ok:
            print(f"GATE FAILURE on {stem}; aborting before ledger write")
            return 2

        row = {
            "id": stem, "parent": PARENT_ID, "axis": "PRUNE", "value": f"B{R}",
            "n_dots": str(len(v.dots)), "pct_changed": f"{v.pct_changed:.2f}",
            "sha256": sha, "status": "BUILT",
            "predicted_change": f"{PREDICTIONS[R][0]} MODEL",
            "file_zeros": str(zeros_path.relative_to(ROOT)),
            "file_nan": str(nan_path.relative_to(ROOT)),
            "sha8": sha8,
            "change_desc": f"drop parent dots within {R}px of catalogue ({v.n_changed}), "
                           f"refill nearest legal pixel; count held at {EXPECTED_PARENT_DOTS}",
            "receipt_score": "", "receipt_date": "",
            "notes": f"radius={R}px git={git_sha()[:12]}",
        }
        append_variant(row, ROOT / "ledger" / "submissions.csv")
        results.append({**row, "gate_report": report,
                        "stats": {"n_dropped": v.n_changed, "radius": R,
                                  "mean_removed_dist": float(d_dots[d_dots <= R].mean()),
                                  "changed_pct": v.pct_changed}})

    if results:
        (ROOT / "registry" / "prune_session_20261023.json").write_text(
            json.dumps({"git_sha": git_sha(), "radii": RADII, "results": results},
                       indent=2))
    print(f"\nbuilt {len(results)} variants")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    raise SystemExit(main(**vars(ap.parse_args())))
