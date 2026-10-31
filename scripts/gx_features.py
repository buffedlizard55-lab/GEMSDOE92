#!/usr/bin/env python3
"""GX lane feature stack -- built only from externally sourced, publicly
downloadable layers (GeoDAWN radiometrics/magnetics, the 1 m-lidar scarp
product, the USGS SGMC fault compilation and GDR geothermal indicators).

Why this module exists
----------------------
The DrivenData bundle (``training_features.tif``, ``labels.tif``) is behind a
login and is not in this checkout.  Every layer used here is instead pinned by
SHA-256 from a public mirror and described in ``docs/gx-external-sources.md``.
Nothing in this file reads another team's submission raster, so a submission
built from these features is not a copy of a previous submission.

Feature families
----------------
* ``morph``  1 m-lidar scarp product (excess height, step, curvature, facing,
  cross-slope, relief) at 150 m and 350 m smoothing: value, horizontal-gradient
  magnitude (lineament/worm strength) and ridgeness (minus the smallest Hessian
  eigenvalue) -- the latter two are the standard potential-field /
  scarp-lineament operators.
* ``geo``    GeoDAWN K, U, TC, Th/K ratio and TMI upward-continued 150 m: value
  and horizontal-gradient magnitude at 350 m (radiometric/magnetic contacts).
* ``ctx``    scarp-orientation coherence and axial strike (sin2/cos2), lidar
  validity, log-distance to the SGMC fault compilation, log-distance to the
  nearest thermal spring / well / paleo-geothermal deposit.

All features are percentile-ranked inside the footprint so that the uint8
quantisation of the source stacks cannot distort the fit.
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
from gems57.grid import load_grid  # noqa: E402

EXT = ROOT / ".cache" / "ext"
CACHE = ROOT / ".cache" / "gx"
GRID = (3730, 3292)

# (file, band description, 1-based band index, has_missing_zero, families...)
MORPH_BANDS = [
    ("lidar_scarp_features_u8.tif", "ex_max", 1, True),
    ("lidar_scarp_features_u8.tif", "step_max", 3, True),
    ("lidar_scarp_features_u8.tif", "lappos_max", 5, True),
    ("lidar_scarp_features_u8.tif", "cross_max", 8, True),
    ("lidar_scarp_features_u8.tif", "relief", 9, True),
]
GEO_BANDS = [
    ("geodawn_rad_u8.tif", "K", 1, False),
    ("geodawn_rad_u8.tif", "U", 3, False),
    ("geodawn_rad_u8.tif", "TC", 4, False),
    ("geodawn_extensions_u8.tif", "ThK", 1, False),
    ("geodawn_extensions_u8.tif", "TMI_up150", 4, False),
]
SIGMAS_MORPH = (1.5, 3.5)
SIGMA_GEO = 3.5


def rank_transform(v: np.ndarray, foot: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Percentile-rank a band inside ``foot & valid``; outside -> 0.5."""
    out = np.full(v.shape, 0.5, np.float32)
    idx = np.flatnonzero((foot & valid).ravel())
    vals = v.ravel()[idx]
    order = np.argsort(vals, kind="stable")
    ranks = np.arange(vals.size, dtype=np.float64)
    sv = vals[order]
    i = 0
    while i < sv.size:                      # average ranks over ties
        j = i
        while j + 1 < sv.size and sv[j + 1] == sv[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = 0.5 * (i + j)
        i = j + 1
    out.ravel()[idx] = (ranks / max(vals.size - 1, 1)).astype(np.float32)
    return out


def band_measures(b: np.ndarray, sigma: float) -> dict[str, np.ndarray]:
    sm = ndi.gaussian_filter(b, sigma, mode="nearest")
    gy, gx = np.gradient(sm)
    hg = np.hypot(gy, gx).astype(np.float32)
    hyy, hyx = np.gradient(gy)
    hxy, hxx = np.gradient(gx)
    disc = np.sqrt(np.maximum((hxx - hyy) ** 2 + 4.0 * hyx * hxy, 0.0))
    hess_min = 0.5 * (hxx + hyy - disc)
    ridge = np.maximum(-hess_min, 0.0).astype(np.float32)
    return {"sm": sm.astype(np.float32), "hg": hg, "ridge": ridge}


def build(force: bool = False) -> Path:
    """Build (or reuse) the feature memmap; returns the meta path."""
    CACHE.mkdir(parents=True, exist_ok=True)
    meta_path = CACHE / "features_meta.json"
    data_path = CACHE / "features.f32"
    if meta_path.is_file() and data_path.is_file() and not force:
        return meta_path

    grid = load_grid()
    foot = grid.footprint
    names: list[str] = []
    arrays: list[np.ndarray] = []

    def add(name: str, arr: np.ndarray) -> None:
        names.append(name)
        arrays.append(np.asarray(arr, np.float32).ravel())

    for fname, desc, bidx, has_missing in MORPH_BANDS:
        with rasterio.open(EXT / fname) as ds:
            v = ds.read(bidx).astype(np.float32)
        valid = (v > 0) if has_missing else np.ones(v.shape, bool)
        b = rank_transform(v, foot, valid)
        for sig in SIGMAS_MORPH:
            for tag, m in band_measures(b, sig).items():
                add(f"morph_{desc}_s{sig}_{tag}", m)
        del v, b
    for fname, desc, bidx, has_missing in GEO_BANDS:
        with rasterio.open(EXT / fname) as ds:
            v = ds.read(bidx).astype(np.float32)
        valid = (v > 0) if has_missing else np.ones(v.shape, bool)
        b = rank_transform(v, foot, valid)
        m = band_measures(b, SIGMA_GEO)
        add(f"geo_{desc}_sm", m["sm"])
        add(f"geo_{desc}_hg", m["hg"])
        del v, b

    # --- context / prior layers -------------------------------------------------
    with rasterio.open(EXT / "lidar_scarp_features_u8.tif") as ds:
        coh = ds.read(10).astype(np.float32)
        strike = ds.read(11).astype(np.float32)
        valid_lid = ds.read(12) > 0
    coh_b = rank_transform(coh, foot, valid_lid)
    add("ctx_coh100", ndi.gaussian_filter(coh_b, 2.0, mode="nearest"))
    add("ctx_coh100_hg", band_measures(coh_b, 2.0)["hg"])
    th = (strike / 255.0) * np.pi                 # axial (0..pi) orientation
    add("ctx_strike_sin2", np.sin(2.0 * th))
    add("ctx_strike_cos2", np.cos(2.0 * th))
    add("ctx_lidar_valid", valid_lid.astype(np.float32))

    def log_dist(mask: np.ndarray) -> np.ndarray:
        d = ndi.distance_transform_edt(~mask)
        return np.log1p(d).astype(np.float32)

    with rasterio.open(EXT / "derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc = ds.read(1) > 0
    add("ctx_d_sgmc", log_dist(sgmc))

    thermal = np.zeros(foot.shape, bool)
    tp = CACHE / "thermal_points.npy"
    if tp.is_file():
        rc = np.load(tp)
        thermal[rc[:, 0], rc[:, 1]] = True
    add("ctx_d_thermal", log_dist(thermal))

    # Stream the stack to disk one feature at a time.  A 47 x 12.3M float32
    # np.memmap leaves ~2.3 GB of dirty pages and the sandbox OOM-kills the
    # writer; sequential ``tofile`` writes through instead.  (IR-GX-FEAT-OOM)
    n = len(names)
    h = hashlib.sha256()
    with data_path.open("wb") as fh:
        for arr in arrays:
            buf = np.ascontiguousarray(arr, dtype=np.float32)
            h.update(buf.tobytes())
            buf.tofile(fh)
            del buf
    del arrays
    meta = dict(schema="gx-features.v1", n_features=n, shape=list(GRID),
                feature_names=names, dtype="float32",
                data=str(data_path.relative_to(ROOT)),
                sha256=h.hexdigest())
    meta_path.write_text(json.dumps(meta, indent=1))
    print(f"built {n} features -> {data_path} ({data_path.stat().st_size/1e9:.2f} GB)")
    return meta_path


def load():
    meta = json.loads((CACHE / "features_meta.json").read_text())
    mm = np.memmap(ROOT / meta["data"], dtype=np.float32, mode="r",
                   shape=(meta["n_features"], GRID[0] * GRID[1]))
    return meta, mm


if __name__ == "__main__":
    raise SystemExit(0 if build(force="--force" in sys.argv) else 1)
