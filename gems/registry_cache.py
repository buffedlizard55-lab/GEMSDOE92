"""Compact, hash-verified cache of every public GEMSDOE raster (registry).

Shared tool (2026-10-27, session ee2370c1).  It streams each public repository
tarball from ``codeload.github.com`` (one HTTP request per repository), keeps
only single-band rasters on the exact competition grid, and stores a compact
summary per unique file (SHA-256):

* ``meta``  -- owner/repo/branch/path, git blob SHA-1, SHA-256, bytes, dtype,
  finite/positive/NaN counts inside the sample footprint, value range,
  whether values are binary, and whether any positive mass lies outside it.
* ``top``   -- footprint-linear indices (int32) of the positive pixels ordered
  by value (descending, ties broken by a fixed seeded key), capped at
  ``TOP_CAP``.  For sparse dot fields this is the complete positive support.
* ``topv``  -- the matching values (float32).
* ``samp``  -- values at a fixed seeded random sample of footprint pixels,
  used for rank-correlation (Spearman) estimates.

Nothing here decides uniqueness; see :mod:`gems.uniqueness_v3`.
"""
from __future__ import annotations

import hashlib
import io
import json
import tarfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "registry_v3"
TOP_CAP = 600_000
SAMPLE_N = 200_000
SAMPLE_SEED = 20261027
TIE_SEED = 7
SHAPE = (3730, 3292)
TRANSFORM = (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


@dataclass
class Footprint:
    mask: np.ndarray          # bool (H, W)
    lin: np.ndarray           # int64 footprint-linear -> full-grid linear index
    sample: np.ndarray        # int64 footprint-linear indices of the fixed sample
    tie_key: np.ndarray       # float64 per footprint cell, deterministic tie-break

    @property
    def n(self) -> int:
        return int(self.lin.size)


def load_footprint(sample_tif: Path) -> Footprint:
    import rasterio
    with rasterio.open(sample_tif) as ds:
        a = ds.read(1)
    mask = np.isfinite(a)
    lin = np.flatnonzero(mask.ravel())
    rng = np.random.default_rng(SAMPLE_SEED)
    sample = np.sort(rng.choice(lin.size, size=SAMPLE_N, replace=False))
    tie_key = np.random.default_rng(TIE_SEED).random(lin.size)
    return Footprint(mask=mask, lin=lin, sample=sample, tie_key=tie_key)


def order_desc(values: np.ndarray, tie_key: np.ndarray) -> np.ndarray:
    """Indices of ``values`` sorted descending, ties broken by ``tie_key``."""
    return np.lexsort((tie_key, -values))


def summarize_array(arr: np.ndarray, fp: Footprint) -> tuple[dict, dict]:
    """Return (meta, arrays) for one full-grid raster array."""
    full = np.asarray(arr, dtype=np.float64).ravel()
    v = full[fp.lin]
    finite = np.isfinite(v)
    vz = np.where(finite, v, 0.0)
    pos = vz > 0
    outside = np.ones(full.size, bool)
    outside[fp.lin] = False
    out_vals = full[outside]
    out_finite = np.isfinite(out_vals)
    meta = dict(
        n_fp=int(v.size),
        n_fp_finite=int(finite.sum()),
        n_fp_nan=int((~finite).sum()),
        n_fp_pos=int(pos.sum()),
        n_out_nonzero=int((out_finite & (out_vals != 0)).sum()),
        n_out_nan=int((~out_finite).sum()),
        vmin=float(vz.min()) if v.size else 0.0,
        vmax=float(vz.max()) if v.size else 0.0,
    )
    pv = vz[pos]
    uniq = np.unique(pv[: min(pv.size, 2_000_000)])
    meta["binary"] = bool(uniq.size <= 1 and (uniq.size == 0 or uniq[0] == 1.0))
    meta["n_unique_pos_values"] = int(min(uniq.size, 1_000_000))
    pos_idx = np.flatnonzero(pos)
    if pos_idx.size:
        o = order_desc(vz[pos_idx], fp.tie_key[pos_idx])[:TOP_CAP]
        top = pos_idx[o].astype(np.int32)
        topv = vz[top].astype(np.float32)
    else:
        top = np.empty(0, np.int32)
        topv = np.empty(0, np.float32)
    meta["top_complete"] = bool(pos_idx.size <= TOP_CAP)
    samp = vz[fp.sample].astype(np.float32)
    return meta, dict(top=top, topv=topv, samp=samp)


def raster_from_bytes(data: bytes):
    """Open a GeoTIFF from bytes; return (array, info) or (None, reason)."""
    import rasterio
    from rasterio.io import MemoryFile
    try:
        with MemoryFile(data) as mf, mf.open() as ds:
            info = dict(count=ds.count, shape=ds.shape, dtype=ds.dtypes[0],
                        crs=str(ds.crs) if ds.crs else None,
                        transform=tuple(round(float(x), 6) for x in tuple(ds.transform)[:6]),
                        nodata=None if ds.nodata is None else float(ds.nodata))
            if ds.count != 1:
                return None, dict(info, reason="not single-band")
            if tuple(ds.shape) != SHAPE:
                return None, dict(info, reason="shape mismatch")
            if info["transform"] != TRANSFORM:
                return None, dict(info, reason="transform mismatch")
            if not info["crs"] or "32611" not in info["crs"]:
                return None, dict(info, reason="crs mismatch")
            a = ds.read(1, masked=False).astype(np.float64)
            if ds.nodata is not None and np.isfinite(ds.nodata):
                a[a == ds.nodata] = np.nan
            return a, info
    except Exception as exc:  # noqa: BLE001 - recorded, never silently dropped
        return None, dict(reason=f"unreadable: {type(exc).__name__}: {exc}"[:300])


def stream_repo(owner: str, repo: str, branch: str, fp: Footprint, *,
                cache: Path = CACHE, timeout: int = 600) -> dict:
    """Stream one repository tarball; summarize every grid-compatible TIFF."""
    blobs = cache / "blobs"
    blobs.mkdir(parents=True, exist_ok=True)
    url = f"https://codeload.github.com/{owner}/{repo}/tar.gz/{branch}"
    files, skipped = [], []
    req = urllib.request.Request(url, headers={"User-Agent": "gemsdoe92-registry"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        with tarfile.open(fileobj=resp, mode="r|gz") as tf:
            for m in tf:
                if not m.isfile():
                    continue
                low = m.name.lower()
                if not (low.endswith(".tif") or low.endswith(".tiff")):
                    continue
                path = m.name.split("/", 1)[1] if "/" in m.name else m.name
                fh = tf.extractfile(m)
                if fh is None:
                    continue
                data = fh.read()
                sha256 = hashlib.sha256(data).hexdigest()
                rec = dict(owner=owner, repo=repo, branch=branch, path=path,
                           bytes=len(data), sha256=sha256, git_blob_sha1=git_blob_sha(data))
                npz = blobs / f"{sha256}.npz"
                mj = blobs / f"{sha256}.json"
                if npz.is_file() and mj.is_file():
                    rec["status"] = "cached"
                    files.append(rec)
                    continue
                arr, info = raster_from_bytes(data)
                if arr is None:
                    rec.update(status="skipped", **info)
                    skipped.append(rec)
                    continue
                meta, arrays = summarize_array(arr, fp)
                meta.update(info)
                np.savez_compressed(npz, **arrays)
                mj.write_text(json.dumps(dict(meta=meta, first_seen=rec), indent=1), encoding="utf-8")
                rec["status"] = "summarized"
                files.append(rec)
    return dict(owner=owner, repo=repo, branch=branch, url=url, files=files, skipped=skipped)


def load_summary(sha256: str, cache: Path = CACHE):
    blobs = cache / "blobs"
    meta = json.loads((blobs / f"{sha256}.json").read_text(encoding="utf-8"))
    with np.load(blobs / f"{sha256}.npz") as z:
        arrays = {k: z[k] for k in z.files}
    return meta, arrays
