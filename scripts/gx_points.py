#!/usr/bin/env python3
"""Build the thermal-indicator point set (row/col) from public geothermal data.

Sources (all public, no login; see ``docs/gx-external-sources.md``):

* ``gdr_wellspring_in_footprint.csv`` -- GDR wells and springs inside the
  competition footprint, already gridded to the 100 m competition raster and
  carrying ``thermalclass``, measured ``temp_c`` and three geothermometers.
* ``Paleo_geothermal_final.csv`` (inside
  ``paleo_geothermal_regional.zip``) -- 709 mapped travertine / sinter / tufa /
  explosion-crater deposits of the Great Basin, in NAD83 geographic coordinates.
* ``gdr_volcanic_vents_in_footprint.csv`` -- 21 Quaternary volcanic vents.

"Thermal indicator" = a record that is classed Hot or Warm, or measured at
>= 30 C, or with any geothermometer >= 100 C.  Cold/unknown water wells are
excluded on purpose: a domestic water well in a basin is not evidence of a
permeable fault, and including the ~19,000 of them would only add a
basin-floor prior.

Output: ``.cache/gx/thermal_points.npy`` -- int32 (row, col) array in the
competition grid, inside the footprint.
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57.grid import load_grid  # noqa: E402

EXT = ROOT / ".cache" / "ext"
OUT = ROOT / ".cache" / "gx"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    grid = load_grid()
    foot = grid.footprint
    H, W = foot.shape
    origin_x, origin_y, px = 243350.0, 4508550.0, 100.0

    def rc_from_xy(x: np.ndarray, y: np.ndarray):
        col = np.floor((x - origin_x) / px).astype(np.int64)
        row = np.floor((origin_y - y) / px).astype(np.int64)
        ok = (row >= 0) & (row < H) & (col >= 0) & (col < W)
        return row[ok], col[ok]

    rows: list[np.ndarray] = []
    cols: list[np.ndarray] = []
    counts: dict[str, int] = {}

    # --- 1. GDR wells and springs (already gridded) ---------------------------
    ws_path = EXT / "gdr_wellspring_in_footprint.csv"
    if ws_path.is_file():
        df = pd.read_csv(ws_path)
        tc = df["thermalclass"].astype("string").str.strip().str.lower()
        thermal = tc.isin(["hot", "warm"])
        temp = pd.to_numeric(df.get("temp_c"), errors="coerce")
        geo = pd.to_numeric(df.get("geothermquartz_c"), errors="coerce")
        geo2 = pd.to_numeric(df.get("geothermchalc_c"), errors="coerce")
        geo3 = pd.to_numeric(df.get("geothermcat_c"), errors="coerce")
        temp = temp.fillna(-999)
        gmax = pd.concat([geo, geo2, geo3], axis=1).max(axis=1).fillna(-999)
        sel = (thermal | (temp >= 30.0) | (gmax >= 100.0)).to_numpy()
        r = df["row"].to_numpy()[sel]
        c = df["col"].to_numpy()[sel]
        inside = (r >= 0) & (r < H) & (c >= 0) & (c < W) & foot[r, c]
        rows.append(r[inside]); cols.append(c[inside])
        counts["gdr_thermal_spring_well"] = int(inside.sum())

    # --- 2. Paleo-geothermal deposits (geographic -> UTM 11N) -----------------
    pz = EXT / "paleo_geothermal_regional.zip"
    if pz.is_file():
        with zipfile.ZipFile(pz) as z:
            with z.open("Paleo_geothermal_final.csv") as fh:
                pdf = pd.read_csv(fh, encoding="latin-1")
        tf = Transformer.from_crs("EPSG:4269", "EPSG:32611", always_xy=True)
        lon = pd.to_numeric(pdf["Long_deg_NAD83"], errors="coerce").to_numpy()
        lat = pd.to_numeric(pdf["Lat_deg_NAD83"], errors="coerce").to_numpy()
        ok = np.isfinite(lon) & np.isfinite(lat)
        x, y = tf.transform(lon[ok], lat[ok])
        r, c = rc_from_xy(np.asarray(x), np.asarray(y))
        inside = (r >= 0) & (r < H) & (c >= 0) & (c < W) & foot[r, c]
        rows.append(r[inside]); cols.append(c[inside])
        counts["paleo_geothermal_deposit"] = int(inside.sum())

    # --- 3. Volcanic vents -----------------------------------------------------
    vv = EXT / "gdr_volcanic_vents_in_footprint.csv"
    if vv.is_file():
        df = pd.read_csv(vv)
        r = df["row"].to_numpy(); c = df["col"].to_numpy()
        inside = (r >= 0) & (r < H) & (c >= 0) & (c < W) & foot[r, c]
        rows.append(r[inside]); cols.append(c[inside])
        counts["volcanic_vent"] = int(inside.sum())

    rr = np.concatenate(rows) if rows else np.zeros(0, np.int64)
    cc = np.concatenate(cols) if cols else np.zeros(0, np.int64)
    arr = np.stack([rr, cc], axis=1).astype(np.int32)
    np.save(OUT / "thermal_points.npy", arr)
    (OUT / "thermal_points_meta.json").write_text(json.dumps(
        dict(schema="gx-thermal-points.v1", n_points=int(arr.size // 2), counts=counts,
             note="Hot/Warm class, temp_c>=30, or any geothermometer >=100 C; plus "
                  "paleo-geothermal deposits and vents."), indent=1))
    print(f"thermal indicators: {arr.size//2} points {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
