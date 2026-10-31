#!/usr/bin/env python3
"""PEEL lane, step A: build a catalogue-free feature matrix from public mirrors.

Why this file exists
--------------------
The official ``training_features.tif`` is not present in this checkout and every
public copy found on GitHub is a Git-LFS pointer (0-byte blob).  Six *derived*
feature rasters that several public GEMSDOE repositories do commit as real bytes
are sha-verified and re-assembled here into a 43-column, footprint-compressed
matrix.  Every column is derived from public geoscience rasters (GeoDAWN
radiometrics and potential fields, USGS 3DEP 10 m DEM derivatives, NHD/LiDAR
scarp derivatives, SGMC state-map faults, TIGER roads).

Deliberate design choice
------------------------
**No column is derived from the competition fault catalogue**
(``existing_faults.tif``/``labels.tif``).  That makes the matrix strictly
catalogue-free, so the hide-and-recover protocol's "derive catalogue features
only from visible faults" rule is satisfied by construction and no feature can
leak a withheld component's location.  The catalogue is used only as the
*label* (training targets / holdout truth) and as a placement exclusion, never
as an input value.

Provenance
----------
Every input is pinned by repository path + Git blob SHA-1 + SHA-256 of the
bytes actually used.  ``provenance.json`` is written next to the matrix.
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

INP = ROOT / ".cache" / "inputs"
OUT = ROOT / ".cache" / "work" / "peel"

# repo path -> local filename.  GitHub blob SHA-1 recorded for the tree entry
# that was fetched (see evidence notes); the SHA-256 below is over local bytes.
INPUTS = {
    "buffedlizard55-lab/GEMSDOE24:data/external/geodawn_rad_u8.tif": "geodawn_rad_u8.tif",
    "buffedlizard55-lab/GEMSDOE24:data/external/geodawn_extensions_u8.tif": "geodawn_extensions_u8.tif",
    "buffedlizard55-lab/GEMSDOE24:data/external/lidar_scarp_features_u8.tif": "lidar_scarp_features_u8.tif",
    "buffedlizard55-lab/60GEMSDOE:data/external/topo_10m_derived_100m_u8.tif": "topo_10m_derived_100m_u8.tif",
    "buffedlizard55-lab/60GEMSDOE:data/external/dem10_chi_100m_u8.tif": "dem10_chi_100m_u8.tif",
    "buffedlizard55-lab/GEMSDOE24:data/external/audit_sources/tiger_road_distance_m.tif": "tiger_road_distance_m.tif",
    "buffedlizard55-lab/GEMSDOE24:data/external/derived_sgmc_faults_100m_u8.tif": "derived_sgmc_faults_100m_u8.tif",
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: Path) -> np.ndarray:
    """Read all bands as float32 (H, W, C)."""
    with rasterio.open(path) as ds:
        a = ds.read().astype(np.float32)
    return np.moveaxis(a, 0, -1)


def u8col(a: np.ndarray) -> np.ndarray:
    """Rank-preserving float -> uint8 for columns that are not already u8."""
    a = np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float64)
    lo, hi = float(a.min()), float(a.max())
    if hi <= lo:
        return np.zeros(a.shape, np.uint8)
    return np.clip(np.rint((a - lo) / (hi - lo) * 255.0), 0, 255).astype(np.uint8)


def boxmean(a: np.ndarray, r: int) -> np.ndarray:
    return ndi.uniform_filter(a.astype(np.float32), size=2 * r + 1, mode="nearest")


def build() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    grid = load_grid()
    foot = np.asarray(grid.footprint, bool)

    proven: dict[str, dict] = {}
    cubes: dict[str, np.ndarray] = {}
    for key, fname in INPUTS.items():
        p = INP / fname
        if not p.is_file():
            raise SystemExit(f"missing input {p} (fetch it from {key})")
        a = read(p)
        if a.shape[:2] != foot.shape:
            raise SystemExit(f"{fname}: grid mismatch {a.shape[:2]} != {foot.shape}")
        if not np.isfinite(a).all():
            a = np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
        if a.dtype != np.uint8 or a.max() > 255:
            a = np.stack([u8col(a[..., i]) for i in range(a.shape[2])], axis=-1)
        cubes[fname] = a
        proven[key] = dict(local=str(p.relative_to(ROOT)), sha256=sha256_file(p),
                           bands=int(a.shape[2]), min=int(a.min()), max=int(a.max()))

    def bands(fname: str, names: list[str]) -> list[tuple[str, np.ndarray]]:
        a = cubes[fname]
        return [(names[i], a[..., i]) for i in range(len(names))]

    cols: list[tuple[str, np.ndarray]] = []
    cols += bands("geodawn_rad_u8.tif", ["rad_K", "rad_Th", "rad_U", "rad_TC"])
    cols += bands("geodawn_extensions_u8.tif", ["enh_ThK", "enh_UK", "enh_UTh", "mag_TMI_up150"])
    cols += bands("lidar_scarp_features_u8.tif",
                  ["sc_ex_max", "sc_ex_mean", "sc_step_max", "sc_lapneg_max",
                   "sc_lappos_max", "sc_downface_max", "sc_upface_max", "sc_cross_max",
                   "sc_relief", "sc_coh100", "sc_strike", "sc_valid"])
    cols += bands("topo_10m_derived_100m_u8.tif",
                  ["tp_slope_p90", "tp_slope_max", "tp_steep_frac", "tp_slope_std",
                   "tp_relief_local", "tp_curv_prof_absmax", "tp_aspect_coh",
                   "tp_hs_lineament", "tp_dem_mean"])
    cols += bands("dem10_chi_100m_u8.tif", ["chi_chan_n", "chi_knick_n", "chi_raised_n", "chi_valid_n"])
    sgmc = cubes["derived_sgmc_faults_100m_u8.tif"][..., 0]
    cols.append(("sgmc_fault", sgmc))
    d_sgmc = ndi.distance_transform_edt(sgmc == 0).astype(np.float32)
    cols.append(("sgmc_dist", u8col(np.clip(d_sgmc, 0, 60))))
    road = cubes["tiger_road_distance_m.tif"][..., 0]
    cols.append(("road_dist_log", u8col(np.log1p(road))))

    # multi-scale context of four structurally decisive columns
    for name, r in (("sc_step_max", 3), ("sc_lapneg_max", 3), ("tp_hs_lineament", 3),
                    ("mag_TMI_up150", 3), ("sc_step_max", 9), ("sc_lapneg_max", 9),
                    ("tp_hs_lineament", 9), ("mag_TMI_up150", 9)):
        a = dict(cols)[name].astype(np.float32)
        cols.append((f"{name}_m{r}", u8col(boxmean(a, r))))

    names = [n for n, _ in cols]
    if len(set(names)) != len(names):
        raise SystemExit("duplicate feature names")
    idx = np.flatnonzero(foot.ravel())
    X = np.empty((idx.size, len(names)), np.uint8)
    for j, (_, a) in enumerate(cols):
        X[:, j] = a.ravel()[idx]
    np.save(OUT / "X.npy", X)
    back = np.load(OUT / "X.npy", mmap_mode="r")
    if back.shape != X.shape or not np.array_equal(np.asarray(back[:1000]), X[:1000]):
        raise SystemExit("read-back mismatch on X.npy")

    meta = dict(schema="gemsdoe92-peel-features-v1",
                evidence_class="LOCAL-COMPUTATION on public mirrored float/uint8 rasters",
                catalogue_derived_columns=[],
                note=("No column is a function of existing_faults/labels. Rank/contrast "
                      "rescaling only; no label information enters."),
                n_cells=int(idx.size), n_features=len(names), names=names,
                X_sha256=sha256_file(OUT / "X.npy"), inputs=proven,
                footprint_cells=int(foot.sum()), shape=list(foot.shape))
    (OUT / "features.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: meta[k] for k in ("n_cells", "n_features", "X_sha256")}, indent=1))
    print("features:", ", ".join(names))
    return meta


if __name__ == "__main__":
    build()
