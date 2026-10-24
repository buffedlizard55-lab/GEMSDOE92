"""Raster I/O for GEMS candidate submissions.

Two encodings are accepted by the competition (brief section 3): NaN outside the
footprint and zeros outside the footprint. Both are written from the same dot
set so a human can upload whichever the uploader prefers.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import rasterio

FLOAT32 = "float32"


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_pinned_path(root: str | Path, rel: str | Path) -> Path:
    """Resolve a manifest/recipe path recorded in either convention.

    This repo's registries record both styles and both are in active use:

      * ``registry/session_manifest.json`` — data-root relative, e.g.
        ``bridge/sample_submission.tif``
      * ``registry/data_manifest.json`` and ``registry/parents/R0.json`` —
        repo relative, e.g. ``data/bridge/sample_submission.tif``

    Blindly joining onto the data root turns the second form into
    ``data/data/bridge/...`` and reports every pinned input as MISSING, which is
    what ``make manifest`` and ``make verify`` did until 2026-10-25. Trying the
    data root first and then the repo root accepts both, and still refuses a
    third, unintended location (the returned path simply will not exist, so the
    caller's MISSING branch fires as before).
    """
    root = Path(root)
    p = Path(rel)
    joined = root / p
    if joined.is_file():
        return joined
    if p.is_file():
        return p
    return joined  # report the data-root form in the error message


def read_reference(path: str | Path) -> dict:
    """Read the reference grid (sample_submission.tif): CRS, transform, shape."""
    with rasterio.open(path) as ds:
        arr = ds.read(1)
        return {
            "crs": ds.crs,
            "transform": ds.transform,
            "shape": (ds.height, ds.width),
            "dtype": ds.dtypes[0],
            "count": ds.count,
            "arr": arr,
            "footprint": np.isfinite(arr),
        }


def write_candidate(path: str | Path, dots: np.ndarray, reference: dict,
                    outside: str = "nan") -> str:
    """Write float32 dots-on-reference-grid; return sha256 of the file on disk.

    outside: "nan"  -> np.nan outside the footprint
             "zero" -> 0.0 outside the footprint
    """
    if outside not in ("nan", "zero"):
        raise ValueError(f"outside must be 'nan' or 'zero', got {outside!r}")
    fill = np.nan if outside == "nan" else 0.0
    arr = np.full(reference["shape"], fill, dtype=np.float32)
    arr[reference["footprint"]] = 0.0
    band = arr
    band[dots > 0] = dots[dots > 0].astype(np.float32)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        path, "w", driver="GTiff", height=reference["shape"][0],
        width=reference["shape"][1], count=1, dtype=FLOAT32,
        crs=reference["crs"], transform=reference["transform"],
        nodata=np.float32(np.nan) if outside == "nan" else None,
        compress="deflate", tiled=False,
    ) as ds:
        ds.write(band.astype(np.float32), 1)
    # always hash what actually landed on disk
    return sha256_file(path)


def read_dots(path: str | Path) -> np.ndarray:
    """Read a candidate/dot raster as a dense float32 array."""
    with rasterio.open(path) as ds:
        if ds.count != 1:
            raise ValueError(f"expected 1 band, got {ds.count}")
        return ds.read(1).astype(np.float32)
