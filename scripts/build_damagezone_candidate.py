#!/usr/bin/env python3
"""Generate a unique candidate submission: damage-zone proximal dots.

Hypothesis H1 (untried): geothermal / Quaternary fault prospects concentrate in
fault damage zones and on parallel strands immediately adjacent to (but not on)
the mapped USGS/INGENIOUS catalogue. All focus-site high scorers (0.24-0.28)
scatter dots 15-30 px from the catalogue; none exploit the 2-12 px damage zone.
This should (a) be unique vs every registry raster (dots sit near the catalogue
where the scattered reference dots are far), and (b) recover withheld holdout
segments better than R0 (GEMSDOE32 winner, holdout DTI 0.09775).

Output: binary {0,1} float32 single-band GeoTIFF matching the sample grid,
zeros outside the footprint, zero mass on the catalogue.
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine
from scipy.ndimage import distance_transform_edt, binary_dilation

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
CATALOGUE = ROOT / "data" / "bridge" / "existing_faults.tif"
OUT_TIF = ROOT / "docs" / "downloads" / "gemsdoe92-damagezone-dots-20261028-zeros.tif"
SEED = 20261028
NDOTS = 30_000
BAND_LO, BAND_HI = 3, 12  # px from catalogue (damage zone; 100 m grid -> 300 m - 1.2 km). Strictly > 2 px to satisfy the catalogue-distance gate.


def main() -> None:
    with rasterio.open(SAMPLE) as ds:
        profile = ds.profile
        sample = ds.read(1).astype(np.float64)
        footprint = np.isfinite(sample)
    with rasterio.open(CATALOGUE) as ds:
        cat = (ds.read(1).astype(np.float64) > 0.5) & footprint

    # Distance from every footprint pixel to the nearest catalogue pixel.
    dt = distance_transform_edt(~cat)
    eligible = footprint & ~cat & (dt >= BAND_LO) & (dt <= BAND_HI)
    n_eligible = int(eligible.sum())
    print(f"footprint={int(footprint.sum())} catalogue_px={int(cat.sum())} "
          f"damage-zone {BAND_LO}-{BAND_HI}px eligible={n_eligible}")
    if n_eligible < NDOTS:
        raise SystemExit(f"not enough eligible damage-zone pixels ({n_eligible} < {NDOTS})")

    rng = np.random.default_rng(SEED)
    idx = rng.choice(np.flatnonzero(eligible.ravel()), size=NDOTS, replace=False)
    pred = np.zeros(sample.shape, dtype=np.float32)
    pred.ravel()[idx] = 1.0

    # Sanity: no mass on catalogue, nothing outside footprint, in [0,1].
    assert not np.any((pred > 0) & cat), "mass on catalogue!"
    assert not np.any((pred > 0) & ~footprint), "mass outside footprint!"
    assert np.isfinite(pred).all() and pred.min() >= 0 and pred.max() <= 1

    # Write GeoTIFF matching the sample grid exactly.
    out_profile = dict(profile)
    out_profile.update(count=1, dtype="float32", nodata=None,
                       driver="GTiff", compress="deflate")
    OUT_TIF.parent.mkdir(parents=True, exist_ok=True)
    if OUT_TIF.exists():
        OUT_TIF.unlink()
    with rasterio.open(OUT_TIF, "w", **out_profile) as ds:
        ds.write(pred.astype(np.float32), 1)

    # Re-open and verify round trip.
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
    print(f"CRS={ds.crs} shape={ds.shape} transform={ds.transform}")
    json_out = OUT_TIF.with_suffix(".json")
    json_out.write_text(json.dumps(dict(file=OUT_TIF.name, sha256=digest,
                                        dots=int((pred>0).sum()),
                                        ndots=NDOTS, band=[BAND_LO, BAND_HI],
                                        seed=SEED), indent=1))
    print("wrote", json_out)


if __name__ == "__main__":
    main()
