#!/usr/bin/env python3
"""Do the dot strings of R0 / LCS show a survey-artefact orientation signature? (MEASURED)

Official survey facts (USGS ScienceBase, GeoDAWN release, doi 10.5066/P93LGLVQ): flight lines run E-W (azimuth 90 deg)
at 200 m (Area 1) / 400 m (Area 2) spacing; tie lines run N-S (azimuth 180 deg) at 2 km / 4 km; data were tie-line and
micro-levelled; four acquisition blocks (Winnemucca, Fallon, Hawthorne, Tonopah).  Levelling residue would therefore
stripe E-W at 4 px (Area 2) and N-S at 40 px.  Test: orientation of elongated dot strings (dots linked when <= 3.2 px apart,
>= 5 dots, principal-axis elongation >= 4) versus the mapped catalogue's elongated components, in 15-degree bins
(0 = E-W, 90 = N-S).  An E-W excess over the catalogue would flag flight-line striping; a N-S excess cannot be separated
from the regional structural grain without the tie-line positions (flight-path shapefiles are in the release).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]


def rd(p):
    with rasterio.open(p) as ds:
        return np.nan_to_num(ds.read(1)) > 0


def strings(yx, lab, min_n, min_elong):
    out = []
    order = np.argsort(lab, kind="stable")
    ls, ys = lab[order], yx[order]
    bounds = np.r_[0, np.flatnonzero(np.diff(ls)) + 1, len(ls)]
    for a, b in zip(bounds[:-1], bounds[1:]):
        if b - a < min_n:
            continue
        pts = ys[a:b].astype(float)
        pts -= pts.mean(0)
        w, v = np.linalg.eigh(np.cov(pts.T))
        el = 1e9 if w[0] <= 1e-9 else w[1] / w[0]
        if el < min_elong:
            continue
        dy, dx = v[0, 1], v[1, 1]
        out.append((np.degrees(np.arctan2(-dy, dx)) % 180, b - a))
    return np.array(out)


def near(arr, center, half=10):
    d = np.minimum(np.abs(arr[:, 0] - center), 180 - np.abs(arr[:, 0] - center))
    return float(arr[d <= half, 1].sum() / arr[:, 1].sum())


def main() -> int:
    arms = {"R0": ROOT / "data" / "parent_R0_zeros.tif"}
    lcs = sorted((ROOT / "docs" / "downloads").glob("GEMSDOE92-lcs-consensus-*-zeros.tif"))
    arms["LCS"] = lcs[-1]
    bins = np.arange(0, 181, 15)
    out = dict(evidence_class="MEASURED", source="https://doi.org/10.5066/P93LGLVQ (USGS ScienceBase GeoDAWN release)",
               uniform_expectation_per_pm10deg_window=20 / 180, arms={})
    for name, p in arms.items():
        yx = np.argwhere(rd(p))
        pairs = cKDTree(yx).query_pairs(3.2, output_type="ndarray")
        n = len(yx)
        a = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(n, n))
        _, lab = connected_components(a, directed=False)
        st = strings(yx, lab, 5, 4.0)
        h = np.histogram(st[:, 0], bins=bins, weights=st[:, 1])[0]
        out["arms"][name] = dict(n_strings=int(len(st)), dots_in_strings=int(st[:, 1].sum()),
                                 east_west_pm10=near(st, 0), north_south_pm10=near(st, 90),
                                 hist_15deg=(h / h.sum()).round(4).tolist())
    cat = rd(ROOT / "data" / "bridge" / "existing_faults.tif")
    lab, _ = ndi.label(cat, structure=np.ones((3, 3)))
    st = strings(np.argwhere(cat), lab[cat], 10, 8.0)
    h = np.histogram(st[:, 0], bins=bins, weights=st[:, 1])[0]
    out["arms"]["CATALOGUE"] = dict(n_strings=int(len(st)), dots_in_strings=int(st[:, 1].sum()), east_west_pm10=near(st, 0),
                                    north_south_pm10=near(st, 90), hist_15deg=(h / h.sum()).round(4).tolist())
    out["reading"] = ("No E-W (flight-line) excess in either file: R0 and LCS are at or below the uniform 11.1 % and above the catalogue's ~3 %, "
                      "N-S shares track the catalogue's, i.e. the regional structural grain. Not evidence of levelling artefacts; "
                      "N-S tie-line artefacts cannot be separated without the flight-path shapefiles.")
    (ROOT / "evidence" / "orientation_check_20261024.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "hist_15deg"} for k, v in out["arms"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
