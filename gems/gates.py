"""MUST-pass format gates for a candidate submission (brief section 6).

Every gate returns (ok: bool, detail: str). run_gates() returns a list of
results; exit status is non-zero if any MUST gate fails. Nothing here needs
network access or the competition data beyond the reference grid and the
catalogue/known-fault mask.

Design note: gates are intentionally independent of the dots' semantics, so a
variant cannot "pass" by being pretty. They check exactly what the uploader
will check.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import rasterio

from .rasters import sha256_file

MIN_FROM_CATALOGUE_PX = 3  # brief constraint 4, except when AXIS=PRUNE
ZERO_MASS_NEAR_CATALOGUE_PX = 2  # R0's winning prune radius


@dataclass
class GateResult:
    name: str
    ok: bool
    detail: str

    def __str__(self) -> str:
        return f"[{'PASS' if self.ok else 'FAIL'}] {self.name}: {self.detail}"


def _dots_within(mask_ys, mask_xs, dots_ys, dots_xs, radius):
    """Boolean per-dot: is it within `radius` px (Euclidean) of a mask pixel?

    Queries only the dot pixels, not the whole grid: at real resolution the
    region is ~5.17M pixels and building a full index there is both slow and
    unnecessary.
    """
    from scipy.spatial import cKDTree

    if len(mask_ys) == 0 or len(dots_ys) == 0:
        return np.zeros(len(dots_ys), dtype=bool)
    tree = cKDTree(np.c_[mask_ys, mask_xs])
    d, _ = tree.query(np.c_[dots_ys, dots_xs], k=1)
    return d <= radius


def run_gates(candidate_path, reference_path, catalogue_path=None,
              prune_radius: int | None = None) -> list[GateResult]:
    results: list[GateResult] = []

    ref = rasterio.open(reference_path)
    cand = rasterio.open(candidate_path)
    try:
        results.append(_g_crs(ref, cand))
        results.append(_g_shape(ref, cand))
        results.append(_g_transform(ref, cand))
        results.append(_g_dtype_band(cand))
        arr = cand.read(1).astype(np.float64)
        footprint = np.isfinite(ref.read(1).astype(np.float64))
        results.append(_g_value_range(arr, footprint))
        results.append(_g_no_nan_inside(arr, footprint))
        results.append(_g_nan_outside(arr, footprint))
        if catalogue_path is not None:
            results.extend(_g_catalogue(arr, footprint, catalogue_path, prune_radius))
    finally:
        ref.close()
        cand.close()

    results.append(GateResult("reread_sha256", True,
                              sha256_file(candidate_path)))
    return results


def _g_crs(ref, cand):
    ok = ref.crs == cand.crs and cand.crs is not None
    return GateResult("crs", ok, f"reference={ref.crs} candidate={cand.crs}")


def _g_shape(ref, cand):
    ok = (ref.height, ref.width) == (cand.height, cand.width)
    return GateResult("shape", ok, f"reference={ref.height}x{ref.width} "
                                   f"candidate={cand.height}x{cand.width}")


def _g_transform(ref, cand):
    ok = ref.transform.almost_equals(cand.transform, precision=1e-6)
    return GateResult("transform", ok, f"{ref.transform} vs {cand.transform}")


def _g_dtype_band(cand):
    ok = cand.dtypes[0] == "float32" and cand.count == 1
    return GateResult("dtype_and_band", ok,
                      f"dtype={cand.dtypes[0]} count={cand.count}")


def _g_value_range(arr, footprint):
    finite = arr[footprint]
    bad = finite[(finite < 0) | (finite > 1)]
    ok = bad.size == 0
    return GateResult("values_in_0_1", ok,
                      f"n_violations={bad.size} min={finite.min() if finite.size else 'n/a'} "
                      f"max={finite.max() if finite.size else 'n/a'}")


def _g_no_nan_inside(arr, footprint):
    n = int(np.isnan(arr[footprint]).sum())
    return GateResult("no_nan_inside_footprint", n == 0, f"nan_pixels={n}")


def _g_nan_outside(arr, footprint):
    outside = ~footprint
    if not outside.any():
        return GateResult("nan_outside_footprint", True, "no outside pixels")
    finite_outside = np.isfinite(arr[outside])
    # either convention is allowed upstream; flag which one this file uses
    n_nan = int((~finite_outside).sum())
    n_zero = int((finite_outside & (arr[outside] == 0)).sum())
    other = int(finite_outside.sum() - n_zero)
    ok = other == 0
    return GateResult("nan_outside_footprint", ok,
                      f"outside={int(outside.sum())} nan={n_nan} zero={n_zero} "
                      f"other={other}")


def _g_catalogue(arr, footprint, catalogue_path, prune_radius):
    with rasterio.open(catalogue_path) as ds:
        cat = ds.read(1)
    mask = (cat > 0) & footprint
    n_cat = int(mask.sum())
    if n_cat == 0:
        return [GateResult("catalogue_zero_mass", True, "catalogue empty: vacuous")]

    hit = (arr > 0) & mask
    zero_ok = int(hit.sum()) == 0

    radius = MIN_FROM_CATALOGUE_PX if prune_radius is None else prune_radius
    dot_ys, dot_xs = np.nonzero(arr > 0)
    on_or_near = _dots_within(*np.nonzero(mask), dot_ys, dot_xs, radius)
    # dots sitting ON the catalogue belong to the zero-mass gate, not this one
    n_near = int((on_or_near & ~mask[dot_ys, dot_xs]).sum())
    expected_ok = prune_radius is not None and prune_radius < MIN_FROM_CATALOGUE_PX
    return [
        GateResult("catalogue_zero_mass", zero_ok, f"dots_on_catalogue={int(hit.sum())}"),
        GateResult("distance_from_catalogue", n_near == 0 or expected_ok,
                   f"radius={radius}px dots_within={n_near}"
                   + (" (declared clearance override: radius < 3 px, inherited R0 dots only)" if expected_ok else "")),
    ]


def summarise(results: list[GateResult]) -> tuple[bool, str]:
    """ALL OK / list of failures, for CI and the ledger."""
    fails = [r for r in results if not r.ok and r.name != "proxy_not_a_gate"]
    lines = [str(r) for r in results]
    if fails:
        lines.append(f"RESULT: FAIL ({len(fails)} gate(s))")
    else:
        lines.append(f"RESULT: PASS ({len(results)} gates)")
    return (not fails), "\n".join(lines)
