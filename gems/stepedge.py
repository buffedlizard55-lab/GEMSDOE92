"""STEPEDGE lane surface: oriented sustained elevation steps (2026-10-24).

Geology
-------
A Quaternary normal fault offsetting a surface produces a *sustained step*
in topography across the trace: ground on one side stays higher than ground
on the other side for hundreds of metres away from the scarp face.  The two
terrain lanes already built in this repo measure local *derivatives* instead:
BREAKLINE uses ``||grad det_elev_slope||`` and SCARPPOL its fall-line
projection.  A derivative magnitude cannot distinguish a step from a
V-shaped incised channel or an inverted-V ridge -- both carry two strong
derivative ridges of opposite sign -- whereas a two-sided aperture step
integrates them away: sampled a few hundred metres either side of the line,
a channel and a ridge read high ~= high (step ~ 0) and only a true offset
reads high vs low.

The lane surface is

    step_A(x) = | mean(det_elev at x + A*u) - mean(det_elev at x - A*u) |
    step(x)   = min(step_{2,3}(x), step_{4,6}(x))     (aperture persistence)
    S(x)      = pct_rank(step(x)) * coherence(det_elev)(x)

The min over apertures is load-bearing, and synthetic tests pin it: at the
short aperture alone a channel *wall* is locally a step (high bank vs low
thalweg), but its offset decays once the aperture exceeds the channel width,
while a fault throw sustains at every aperture (tests/test_stepedge.py:
near/far/min = 5.4/6.0/5.4 m for a 6 m synthetic step vs 3.3/1.3/1.3 m for
a channel of equal relief).

where ``u`` is the dominant-gradient (across-lineament) unit vector from the
structure tensor of ``det_elev`` and ranks are the project-standard
1001-knot percentile ranks inside the valid footprint.  Nothing here reads
the fault catalogue, so catalogue withholding cannot leak through it.

Why this should find faults the catalogue and the parent both miss
------------------------------------------------------------------
Parent R0 sits on the H19-5 potential-field worm skeleton.  A fault
offsetting alluvium against itself (or one lithology against itself) has a
topographic throw but no magnetic/gravity contrast: invisible to the worms,
and -- if the scarp is low -- easily missed by the photo-era mapping behind
the USGS/INGENIOUS catalogue, while DEM-based expert mapping (the source of
the competition's new-fault labels, DrivenData #306 p.967) traces exactly
such steps.  Candidate pixels for this lane lie > 3 px from every H19-5
skeleton pixel (builder-enforced), i.e. sustained steps the worm geometry
never represented.

Named non-fault mimics: pluvial Lake Lahontan wave-cut benches and shoreline
terraces are also sustained steps; so are alluvial-fan segment boundaries,
fluvial terrace edges and bedding-controlled cuestas.  The step statistic
alone cannot separate a shoreline bench from a fault scarp.

Pure array math on caller-supplied float arrays; the builder in
``scripts/build_stepedge_variants.py`` owns file I/O and provenance.
Pre-registration: docs/HYPOTHESES_20261024_STEPEDGE.md.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates

from .breakline import _clean, percentile_rank

__all__ = ["percentile_rank", "spaced_top_mask", "tensor_direction",
           "sustained_step", "transversality", "lane_surface"]

# Re-exported so lane builders use one spacing implementation, not a fork.
from .breakline import spaced_top_mask  # noqa: E402

DERIV_SIGMA_PX = 1.0    # gradient smoothing for the structure tensor (~100 m)
TENSOR_SIGMA_PX = 2.0   # tensor integration scale (~200 m)
STEP_OFFSETS_PX = (2.0, 3.0)  # near aperture: 200-300 m either side
STEP_GROUPS_PX = ((2.0, 3.0), (4.0, 6.0))  # persistence: near AND far (400-600 m)


def tensor_direction(field: np.ndarray, valid: np.ndarray,
                     deriv_sigma: float = DERIV_SIGMA_PX,
                     tensor_sigma: float = TENSOR_SIGMA_PX):
    """Structure-tensor coherence and dominant-gradient unit vector.

    Returns ``(coherence, u_row, u_col)`` float32 arrays.  ``u`` points
    *across* the local lineament (the direction of maximum gradient
    variance); its sign is arbitrary, which is fine because the step uses
    symmetric two-sided sampling.  Coherence is identical in construction
    to ``gems.breakline.structure_tensor_coherence`` (same sigmas), computed
    here from the same tensor so direction and gate cannot drift apart.
    """
    a = gaussian_filter(_clean(field, valid), float(deriv_sigma))
    gy, gx = np.gradient(a)
    jxx = gaussian_filter(gx * gx, float(tensor_sigma))
    jyy = gaussian_filter(gy * gy, float(tensor_sigma))
    jxy = gaussian_filter(gx * gy, float(tensor_sigma))
    coh = np.sqrt((jxx - jyy) ** 2 + 4.0 * jxy * jxy) / np.maximum(jxx + jyy, 1e-12)
    coh = np.clip(coh, 0.0, 1.0).astype(np.float32)
    # Principal eigenvector of [[Jxx, Jxy], [Jxy, Jyy]] in (col, row) axes:
    # theta measured from the col axis toward the row axis.
    theta = 0.5 * np.arctan2(2.0 * jxy, jxx - jyy)
    u_col = np.cos(theta).astype(np.float32)
    u_row = np.sin(theta).astype(np.float32)
    return coh, u_row, u_col


def sustained_step(field: np.ndarray, valid: np.ndarray,
                   u_row: np.ndarray, u_col: np.ndarray,
                   offsets: tuple[float, ...] = STEP_OFFSETS_PX) -> np.ndarray:
    """``|mean(field at +offsets*u) - mean(field at -offsets*u)|`` (float32).

    Bilinear sampling along the across-lineament direction.  Coordinates
    clamp at the array edge (``mode="nearest"``); edge pixels are outside
    the scored footprint in every caller, so clamping cannot place dots.
    """
    a = _clean(field, valid)
    h, w = a.shape
    rows, cols = np.indices((h, w), dtype=np.float32)
    pos = np.zeros((h, w), dtype=np.float64)
    neg = np.zeros((h, w), dtype=np.float64)
    for d in offsets:
        pos += map_coordinates(a, [rows + d * u_row, cols + d * u_col],
                               order=1, mode="nearest")
        neg += map_coordinates(a, [rows - d * u_row, cols - d * u_col],
                               order=1, mode="nearest")
    step = np.abs(pos - neg) / float(len(offsets))
    return step.astype(np.float32)


def transversality(field: np.ndarray, valid: np.ndarray,
                   u_row: np.ndarray, u_col: np.ndarray,
                   regional_sigma: float = 8.0) -> np.ndarray:
    """``|u . g_hat_regional|`` in [0, 1]: line transverse to regional slope.

    ``u`` is across the lineament, so this is 1 when the lineament itself
    runs perpendicular to the regional downslope direction (range-front /
    contour-parallel) and 0 when it runs parallel to it (drainage-like).
    Screen-only diagnostic for the TRANSV hypothesis; flat cells return 0.
    """
    a = gaussian_filter(_clean(field, valid), float(regional_sigma))
    gy, gx = np.gradient(a)
    norm = np.hypot(gy, gx)
    dot = np.abs(u_row * gy + u_col * gx)
    out = np.divide(dot, norm, out=np.zeros_like(dot), where=norm > 1e-12)
    return np.clip(out, 0.0, 1.0).astype(np.float32)


def lane_surface(det_elev: np.ndarray, valid: np.ndarray,
                 groups: tuple[tuple[float, ...], ...] = STEP_GROUPS_PX) -> dict[str, np.ndarray]:
    """Build the STEPEDGE surface and components (float32 arrays).

    ``step`` is the aperture-persistent offset: the minimum, over aperture
    groups, of each group's two-sided sustained step.  Returns ``step``,
    ``step_by_group`` (list, metres), ``step_pct``, ``coherence``,
    ``u_row``/``u_col``, ``S_raw`` (``step_pct * coherence``) and ``S_pct``
    (percentile rank of ``S_raw``).  Ranks over ``valid``.
    """
    valid = np.asarray(valid, bool)
    coh, u_row, u_col = tensor_direction(det_elev, valid)
    by_group = [sustained_step(det_elev, valid, u_row, u_col, g) for g in groups]
    step = by_group[0]
    for other in by_group[1:]:
        step = np.minimum(step, other)
    step_pct = percentile_rank(step, valid)
    s_raw = (step_pct * coh).astype(np.float32)
    return {"step": step, "step_by_group": by_group, "step_pct": step_pct,
            "coherence": coh, "u_row": u_row, "u_col": u_col,
            "S_raw": s_raw, "S_pct": percentile_rank(s_raw, valid)}
