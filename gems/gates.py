"""MUST-pass format gates for a candidate submission (brief section 6).

Every gate returns (ok: bool, detail: str). run_gates() returns a list of
results; exit status is non-zero if any MUST gate fails. Nothing here needs
network access or the competition data beyond the reference grid and the
catalogue/known-fault mask.

Design note: gates are intentionally independent of the dots' semantics, so a
variant cannot "pass" by being pretty. The default mode preserves the legacy
NaN-outside encoding for research artifacts. The CLI uses the stricter
submission mode: every cell must be finite and in [0,1], and cells outside the
reference footprint must be zero. A local pass is not organizer acceptance.
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
              prune_radius: int | None = None, *,
              require_submission_encoding: bool = False) -> list[GateResult]:
    results: list[GateResult] = []
    if prune_radius is not None and (
        isinstance(prune_radius, (bool, np.bool_))
        or not isinstance(prune_radius, (int, float, np.integer, np.floating))
        or not np.isfinite(prune_radius) or prune_radius < 0
    ):
        return [GateResult("prune_radius", False, "radius must be finite and nonnegative")]
    try:
        with rasterio.open(reference_path) as ref, rasterio.open(candidate_path) as cand:
            results.extend((_g_crs(ref, cand), _g_shape(ref, cand),
                            _g_transform(ref, cand), _g_dtype_band(cand)))
            reference_ok = ref.count == 1 and ref.crs is not None
            if not reference_ok:
                results.append(GateResult("reference_grid", False,
                                          "reference requires one band and a CRS"))
            # Never index a mismatched grid, or interpret a multiband reference.
            if not reference_ok or cand.count < 1 or ref.shape != cand.shape:
                return results
            arr = cand.read(1).astype(np.float64)
            footprint = np.isfinite(ref.read(1).astype(np.float64))
            if not footprint.any():
                results.append(GateResult("reference_footprint", False, "empty footprint"))
            results.extend((_g_value_range(arr, footprint), _g_no_nan_inside(arr, footprint),
                            _g_nan_outside(arr, footprint)))
            if require_submission_encoding:
                results.append(_g_submission_encoding(arr, footprint))
            if catalogue_path is not None:
                with rasterio.open(catalogue_path) as cat:
                    aligned = (cat.count == 1 and cat.shape == ref.shape
                               and cat.crs == ref.crs and cat.transform == ref.transform)
                if not aligned:
                    results.append(GateResult("catalogue_grid", False,
                                              "catalogue CRS/shape/transform/band mismatch"))
                else:
                    results.extend(_g_catalogue(arr, footprint, catalogue_path, prune_radius))
        results.append(GateResult("reread_sha256", True, sha256_file(candidate_path)))
    except (OSError, rasterio.errors.RasterioError) as exc:
        results.append(GateResult("readable_raster", False, str(exc)))
    return results


def _g_crs(ref, cand):
    ok = ref.crs == cand.crs and cand.crs is not None
    return GateResult("crs", ok, f"reference={ref.crs} candidate={cand.crs}")


def _g_shape(ref, cand):
    ok = (ref.height, ref.width) == (cand.height, cand.width)
    return GateResult("shape", ok, f"reference={ref.height}x{ref.width} "
                                   f"candidate={cand.height}x{cand.width}")


def _g_transform(ref, cand):
    ok = ref.transform == cand.transform
    return GateResult("transform", ok, f"{ref.transform} vs {cand.transform}")


def _g_dtype_band(cand):
    ok = cand.count == 1 and cand.dtypes[0] == "float32"
    return GateResult("dtype_and_band", ok,
                      f"dtype={cand.dtypes} count={cand.count}")


def _g_value_range(arr, footprint):
    finite = arr[footprint]
    bad = finite[(finite < 0) | (finite > 1)]
    ok = bad.size == 0
    return GateResult("values_in_0_1", ok,
                      f"n_violations={bad.size} min={finite.min() if finite.size else 'n/a'} "
                      f"max={finite.max() if finite.size else 'n/a'}")


def _g_no_nan_inside(arr, footprint):
    n = int((~np.isfinite(arr[footprint])).sum())
    return GateResult("no_nan_inside_footprint", n == 0, f"nonfinite_pixels={n}")


def _g_nan_outside(arr, footprint):
    outside = ~footprint
    if not outside.any():
        return GateResult("nan_outside_footprint", True, "no outside pixels")
    outside_values = arr[outside]
    finite_outside = np.isfinite(outside_values)
    # Either NaN or zero is allowed by this legacy/research gate. Infinity and
    # any other finite value are not valid outside encodings.
    n_nan = int(np.isnan(outside_values).sum())
    n_inf = int(np.isinf(outside_values).sum())
    n_zero = int((finite_outside & (outside_values == 0)).sum())
    other = int(finite_outside.sum() - n_zero)
    ok = n_inf == 0 and other == 0
    return GateResult("nan_outside_footprint", ok,
                      f"outside={int(outside.sum())} nan={n_nan} inf={n_inf} "
                      f"zero={n_zero} other={other}")


def _g_submission_encoding(arr, footprint):
    """Require the project's upload-safe, all-finite, zeros-outside encoding."""
    all_finite = bool(np.isfinite(arr).all())
    in_range = bool(all_finite and (arr >= 0).all() and (arr <= 1).all())
    zero_outside = bool(np.all(arr[~footprint] == 0))
    nonempty_footprint = bool(footprint.any())
    ok = all_finite and in_range and zero_outside and nonempty_footprint
    if all_finite:
        lo = float(arr.min())
        hi = float(arr.max())
    else:
        lo = hi = None
    return GateResult(
        "submission_encoding", ok,
        f"all_finite={all_finite} global_range=[{lo}, {hi}] "
        f"zero_outside={zero_outside} nonempty_footprint={nonempty_footprint}",
    )


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
    return [
        GateResult("catalogue_zero_mass", zero_ok, f"dots_on_catalogue={int(hit.sum())}"),
        GateResult("distance_from_catalogue", n_near == 0,
                   f"radius={radius}px dots_within={n_near}; strict distance > radius required"),
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
