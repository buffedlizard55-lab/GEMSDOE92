#!/usr/bin/env python3
"""ALI lane, feature stack: footprint-compressed float32 matrix (41 raw + 11 context operators).

Inputs are the SHA-pinned rasters restored by scripts/restore_inputs.py
(.cache/gems_inputs/).  Every saved array is read back and compared before the
script exits, because this sandbox produced silently zeroed first pages on
large .npy files once (IRREGULARITIES.md, IR-92-NPY-PAGE-ZERO).
"""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path
import numpy as np, rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / ".cache" / "gems_inputs"
OUT = ROOT / ".cache" / "work" / "feat"


def footprint():
    with rasterio.open(G / "bridge" / "sample_submission.tif") as ds:
        return np.isfinite(ds.read(1))


def foot_index():
    return np.flatnonzero(footprint().ravel())


def _sha_arr(a) -> str:
    h = hashlib.sha256()
    a = np.asarray(a)
    step = max(1, (64 << 20) // max(1, a[:1].nbytes))
    for i in range(0, a.shape[0], step):
        h.update(np.ascontiguousarray(a[i:i + step]).tobytes())
    return h.hexdigest()


def safe_save(path: Path, arr: np.ndarray) -> str:
    """np.save + full read-back SHA-256 comparison (NaN-safe, byte-level)."""
    want = _sha_arr(arr)
    np.save(path, arr)
    got = _sha_arr(np.load(path, mmap_mode="r"))
    if got != want:
        raise IOError(f"read-back mismatch for {path}")
    return want


def safe_load(path: Path, sha: str | None = None, mmap=None):
    a = np.load(path, mmap_mode=mmap)
    if sha is not None:
        h = _sha_arr(a)
        if h != sha:
            raise IOError(f"sha mismatch for {path}: {h[:12]} != {sha[:12]}")
    return a


def _fill(a):
    m = np.isfinite(a)
    if m.all():
        return a
    ii = ndimage.distance_transform_edt(~m, return_distances=False, return_indices=True)
    return a[tuple(ii)]


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    idx = foot_index()
    names, cols = [], []

    def add(n, a):
        names.append(n); cols.append(a.ravel()[idx].astype(np.float32))

    bands = {}
    with rasterio.open(G / "training_features.tif") as ds:
        nod = ds.nodata
        for b in range(1, ds.count + 1):
            a = ds.read(b).astype(np.float32)
            a[(a == nod) | ~np.isfinite(a) | (a < -1e30)] = np.nan
            nm = ds.descriptions[b - 1].split(" - ")[0]
            add("tf_" + nm, a)
            if b in (2, 12, 13, 19):
                bands[b] = a
    with rasterio.open(G / "external" / "topo_10m_derived_100m_u8.tif") as ds:
        for b in range(1, ds.count + 1):
            q = ds.read(b).astype(np.float32); t = ds.tags(b)
            lo, hi = float(t["q_lo"]), float(t["q_hi"])
            add("t10_" + t["band_name"], np.where(q == 0, np.nan, lo + (q - 1) / 254 * (hi - lo)))
    with rasterio.open(G / "external" / "dem10_chi_100m_i16.tif") as ds:
        for b in range(1, ds.count + 1):
            a = ds.read(b).astype(np.float32); a[a == ds.nodata] = np.nan
            add("chi_" + ds.descriptions[b - 1], a)
    for fn in ("geodawn_rad_u8.tif", "geodawn_extensions_u8.tif"):
        with rasterio.open(G / "external" / fn) as ds:
            for b in range(1, ds.count + 1):
                a = ds.read(b).astype(np.float32); a[a == 0] = np.nan
                add("rad_" + ds.descriptions[b - 1], a)
    # context operators (computed on gap-filled full grids)
    de = _fill(bands[12])
    for s1, s2 in ((1, 3), (3, 9)):
        add(f"ctx_dog_detelev_{s1}_{s2}", ndimage.gaussian_filter(de, s1) - ndimage.gaussian_filter(de, s2))
    for s in (1, 3, 6):
        add(f"ctx_gradmag_detelev_s{s}", ndimage.gaussian_gradient_magnitude(de, s))
    add("ctx_resid_detelev_s10", de - ndimage.gaussian_filter(de, 10))
    gr = _fill(bands[13])
    for s in (2, 6):
        add(f"ctx_gradmag_grav_s{s}", ndimage.gaussian_gradient_magnitude(gr, s))
    add("ctx_gradmag_rtp_s2", ndimage.gaussian_gradient_magnitude(_fill(bands[2]), 2))
    sl = _fill(bands[19])
    hxx = ndimage.gaussian_filter(sl, 2, order=(0, 2)); hyy = ndimage.gaussian_filter(sl, 2, order=(2, 0))
    hxy = ndimage.gaussian_filter(sl, 2, order=(1, 1))
    det = np.sqrt(((hxx - hyy) / 2) ** 2 + hxy ** 2)
    add("ctx_hess_slope_l1", (hxx + hyy) / 2 - det)
    add("ctx_hess_slope_anis", 2 * det)
    X = np.stack(cols, 1)
    sha = safe_save(OUT / "X_all.npy", X)
    json.dump(dict(names=names, sha256=sha, shape=list(X.shape), n_footprint=int(idx.size)),
              open(OUT / "X_all.json", "w"), indent=1)
    print(X.shape, f"{time.time()-t0:.0f}s", sha[:12])


if __name__ == "__main__":
    main()
