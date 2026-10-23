#!/usr/bin/env python3
"""Build the SNAP edge/scarp response surface from pinned gradient bands.

The response surface is the "strongest edge response" that the SNAP axis snaps
dots onto. It is built ONLY from three bands of the pinned 19-band stack
(registry/session_manifest.json -> training_features, sha256 verified before
use), and from no labels:

    band  3  tmi_hg             total-magnetic-intensity horizontal gradient
                                magnitude (non-negative in this stack)
    band 13  iso_grav_anom      isostatic gravity anomaly -- the stack's band 18
                                (iso_grav_anom_hg) is a SIGNED directional
                                derivative (21% of pixels negative), so the
                                horizontal-gradient magnitude is computed here
                                from band 13 instead of taking |band 18|
    band 19  det_elev_slope     detrended-elevation slope (scarp response)

Each layer is converted to a percentile rank over the in-footprint pixels (the
three layers have wildly different units) and mixed with the weights already
used by this repository for the same trio in
scripts/build_prune_rungs.py::make_prior (0.40 TMI, 0.35 gravity, 0.25 slope).
The weights are fixed a priori, NOT tuned on the known-fault catalogue.

No truth labels, no holdout, no leaderboard. Output is written to .cache/
(gitignored) and is reproducible from the pinned inputs alone.

Usage: python scripts/make_edge_response.py [--out .cache/gems_inputs/snap_edge_response.npy]
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "session_manifest.json"
TRAIN_ID = "training_features"
SENTINEL = -1e30
WEIGHTS = {"tmi_hg": 0.40, "grav_hg": 0.35, "scarp_slope": 0.25}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pinned_input(wanted: str) -> Path:
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in doc["files"]:
        if entry["id"] != wanted:
            continue
        path = ROOT / entry["local_path"]
        if not path.is_file():
            raise SystemExit(f"pinned input {wanted} missing at {path}: run scripts/restore_inputs.py")
        got = sha256_file(path)
        if got != entry["sha256"] or path.stat().st_size != int(entry["bytes"]):
            raise SystemExit(f"pinned input {wanted} FAILED sha256/size check: {got}")
        print(f"PIN OK {wanted} ({path.stat().st_size} B, {got[:12]})")
        return path
    raise SystemExit(f"{wanted} is not pinned in {MANIFEST.name}")


def clean(a: np.ndarray) -> np.ndarray:
    """Replace the stack's -3.4e38 sentinel with NaN."""
    a = a.astype(np.float32)
    a[a < SENTINEL] = np.nan
    return a


def percentile_rank(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    vals = a[valid]
    vals = vals[np.isfinite(vals)]
    knots = np.quantile(vals, np.linspace(0.0, 1.0, 1001))
    out = np.zeros(a.shape, dtype=np.float32)
    q = np.interp(np.nan_to_num(a, nan=0.0), knots, np.linspace(0.0, 1.0, 1001))
    out[valid] = q[valid].astype(np.float32)
    out[~valid] = 0.0
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / ".cache" / "gems_inputs" / "snap_edge_response.npy"))
    args = ap.parse_args()

    stack = pinned_input(TRAIN_ID)
    with rasterio.open(stack) as ds:
        if ds.count < 19:
            raise SystemExit(f"expected >=19 bands, got {ds.count}")
        names = {i + 1: (ds.tags(i + 1).get("band_name") or "") for i in range(ds.count)}
        if names.get(3) != "tmi_hg" or names.get(13) != "iso_grav_anom" or names.get(19) != "det_elev_slope":
            raise SystemExit(f"unexpected band order: {names}")
        tmi_hg = clean(ds.read(3))
        grav = clean(ds.read(13))
        slope = clean(ds.read(19))

    with rasterio.open(ROOT / "data" / "bridge" / "sample_submission.tif") as ds:
        footprint = np.isfinite(ds.read(1))
    valid = footprint & np.isfinite(tmi_hg) & np.isfinite(slope)

    # gravity horizontal-gradient magnitude from the anomaly itself
    gy, gx = np.gradient(np.nan_to_num(grav, nan=0.0).astype(np.float64))
    grav_hg = np.hypot(gx, gy).astype(np.float32)
    grav_hg[~np.isfinite(grav)] = np.nan
    valid &= np.isfinite(grav_hg)

    layers = {
        "tmi_hg": percentile_rank(tmi_hg, valid),
        "grav_hg": percentile_rank(grav_hg, valid),
        "scarp_slope": percentile_rank(slope, valid),
    }
    response = sum(WEIGHTS[k] * v for k, v in layers.items()).astype(np.float32)
    response[~valid] = np.nan

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.save(out, response)

    meta = {
        "response": str(out.relative_to(ROOT)),
        "weights": WEIGHTS,
        "valid_pixels": int(valid.sum()),
        "layer_source": {
            "tmi_hg": "training_features band 3 (tmi_hg), as supplied (non-negative)",
            "grav_hg": "hypot(d/dy, d/dx) of training_features band 13 (iso_grav_anom); "
                       "band 18 is a signed directional derivative and was not used directly",
            "scarp_slope": "training_features band 19 (det_elev_slope), as supplied (non-negative)",
        },
        "range": [float(np.nanmin(response)), float(np.nanmax(response))],
        "note": "weights fixed a priori from the repository's existing prior "
                "(scripts/build_prune_rungs.py::make_prior); not tuned on the catalogue.",
    }
    (out.with_suffix(".json")).write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
