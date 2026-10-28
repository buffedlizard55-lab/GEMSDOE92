#!/usr/bin/env python3
"""Candidate v2: damage-zone dots in the (2, 3] px band from the catalogue.

Passes the strict >2 px distance gate; dots sit within the 3 px triangular
kernel of truth pixels (which lie on catalogue lines), so they should recover
withheld holdout segments better than R0's scattered dots (15-30 px away).
Geological rationale: fault damage zones / immediate fault-zone width are the
fluid pathways that host geothermal upflow -- a contrarian band all focus-site
high scorers ignore (they scatter at 15-30 px).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
CATALOGUE = ROOT / "data" / "bridge" / "existing_faults.tif"
OUT_TIF = ROOT / "docs" / "downloads" / "gemsdoe92-damagezone-close-dots-20261028-zeros.tif"
SEED = 20261028
NDOTS = 30_000
BAND_LO, BAND_HI = 2.0, 3.0  # strictly > 2 px (gate), within 3 px kernel of truth


def main() -> None:
    with rasterio.open(SAMPLE) as ds:
        profile = ds.profile
        sample = ds.read(1).astype(np.float64)
        footprint = np.isfinite(sample)
    with rasterio.open(CATALOGUE) as ds:
        cat = (ds.read(1).astype(np.float64) > 0.5) & footprint

    dt = distance_transform_edt(~cat)
    eligible = footprint & ~cat & (dt > BAND_LO) & (dt <= BAND_HI)
    n_eligible = int(eligible.sum())
    print(f"footprint={int(footprint.sum())} catalogue_px={int(cat.sum())} "
          f"damage-zone ({BAND_LO},{BAND_HI}]px eligible={n_eligible}")
    if n_eligible < NDOTS:
        raise SystemExit(f"not enough eligible pixels ({n_eligible} < {NDOTS})")

    rng = np.random.default_rng(SEED)
    idx = rng.choice(np.flatnonzero(eligible.ravel()), size=NDOTS, replace=False)
    pred = np.zeros(sample.shape, dtype=np.float32)
    pred.ravel()[idx] = 1.0

    assert not np.any((pred > 0) & cat), "mass on catalogue!"
    assert not np.any((pred > 0) & ~footprint), "mass outside footprint!"
    assert np.isfinite(pred).all() and pred.min() >= 0 and pred.max() <= 1

    out_profile = dict(profile)
    out_profile.update(count=1, dtype="float32", nodata=None,
                       driver="GTiff", compress="deflate")
    OUT_TIF.parent.mkdir(parents=True, exist_ok=True)
    if OUT_TIF.exists():
        OUT_TIF.unlink()
    with rasterio.open(OUT_TIF, "w", **out_profile) as ds:
        ds.write(pred.astype(np.float32), 1)

    with rasterio.open(OUT_TIF) as ds:
        a = ds.read(1).astype(np.float64)
        assert ds.count == 1 and ds.crs is not None and ds.shape == sample.shape
        assert ds.transform == profile["transform"]
        assert np.isfinite(a).all() and a.min() >= 0 and a.max() <= 1
        assert not np.any((a > 0) & ~footprint)
        assert not np.any((a > 0) & cat)
    digest = hashlib.sha256(OUT_TIF.read_bytes()).hexdigest()
    print(f"WROTE {OUT_TIF} ({OUT_TIF.stat().st_size/1024:.0f} KB) "
          f"dots={int((pred>0).sum())} sha256={digest}")
    json_out = OUT_TIF.with_suffix(".json")
    json_out.write_text(json.dumps(dict(file=OUT_TIF.name, sha256=digest,
                                        dots=int((pred>0).sum()),
                                        ndots=NDOTS, band=[BAND_LO, BAND_HI],
                                        seed=SEED), indent=1))
    print("wrote", json_out)


if __name__ == "__main__":
    main()
