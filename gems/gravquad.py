"""GRAV-QUAD lane: gravity analytic-signal amplitude x local edge-linearity coherence.

Geology
-------
The USGS/INGENIOUS catalogue is built from *surface scarp* mapping. A blind
basin-and-range normal fault buried under thin Quaternary cover, or one whose
scarp has diffused below detection, still juxtaposes rock bodies of different
density across its plane. That density contrast produces a measurable edge in
the region's isostatic gravity field regardless of fault strike, because the
gravity *analytic signal amplitude* -- the vector sum of all orthogonal
gradient components of a potential field -- is (to first order) independent
of the strike/dip of the causative body (Nabighian, 1972, "The analytic
signal of two-dimensional magnetic bodies with polygonal cross-section",
Geophysics 37(3); the gravity analogue is the same construction applied to
isostatic gravity gradients instead of magnetic ones). This makes it a
strike-blind structural-edge detector, unlike lanes in this repo that assume
a fixed preferred strike (e.g. COULOMB's N15 degrees E conjugate shear
planes) or that fold gravity-gradient magnitude into one of many features
inside a supervised classifier (COULOMB-LOQO, which never evaluates a
gravity-only analytic-signal surface standalone).

Surface (pure array math on caller-supplied arrays; the catalogue is read
only by the caller for masking, never to build features):

    vg   = B11 iso_grav_anom_vg                        (one gradient component)
    hg_ew= B18 iso_grav_anom_hg                         (signed E-W derivative;
                                                          empirically r=+0.65
                                                          with d(B13)/dx on the
                                                          pinned stack, verified
                                                          in this session)
    hg_ns= d(B13 iso_grav_anom)/dy                      (pure finite-difference
                                                          second horizontal
                                                          component, computed
                                                          here only -- no band
                                                          in the stack supplies
                                                          it directly)
    ASA  = sqrt(vg^2 + hg_ew^2 + hg_ns^2)               analytic-signal amplitude
    coh  = local structure-tensor linear coherence of   penalizes equant/blob
           (d(ASA)/dx, d(ASA)/dy) over a 7x7 window      anomalies, rewards
                                                          elongated linear ones
    S    = pct_rank(ASA) * pct_rank(coh)

Named non-fault mimic: equant plutonic intrusions, circular playa/evaporite
density bodies, and diffuse basement-terrane boundaries all produce gravity
edges but have low structure-tensor linear coherence (coh), unlike a fault
trace, which is locally straight.

Difference from existing lanes: no lane in this repository computes a
gravity-only analytic-signal amplitude or a structure-tensor edge-linearity
coherence. COULOMB/COULOMBDM assume fixed conjugate shear strikes; COULOMB-LOQO
and RADIOCONTACT use |vg|*|hg_ew| (or similar) as one term inside a larger
percentile-rank product or boosted-tree feature set, never a rotation-robust
3-component analytic signal with its own linearity filter.
"""

from __future__ import annotations

import numpy as np
import rasterio

SENTINEL = -3.4028235e+38

# 1-based band numbers in training_features.tif (GDAL-verified in README band audit)
BAND = dict(
    grav_vg=11,      # iso_grav_anom_vg
    grav_anom=13,    # iso_grav_anom (raw field; used only to derive hg_ns here)
    grav_hg_ew=18,   # iso_grav_anom_hg (signed E-W derivative, verified r=+0.65 vs d/dx B13)
)

__all__ = ["BAND", "SENTINEL", "read_stack_band", "clean", "percentile_rank",
           "analytic_signal_amplitude", "structure_tensor_coherence", "lane_surface"]


def read_stack_band(path, band: int) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(int(band)).astype(np.float32)


def clean(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Replace sentinel / non-finite cells with the finite-valid median (float32)."""
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a) & (a > SENTINEL + 1e6)
    fill = float(np.median(a[m])) if m.any() else 0.0
    return np.where(np.isfinite(a) & (a > SENTINEL + 1e6), a, np.float32(fill)).astype(np.float32)


def percentile_rank(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Percentile rank in [0, 1] over ``valid`` finite cells (1001 knots)."""
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    out = np.zeros(a.shape, np.float32)
    vals = a[m]
    if vals.size == 0:
        return out
    knots = np.quantile(vals, np.linspace(0.0, 1.0, 1001))
    out[m] = np.interp(vals, knots, np.linspace(0.0, 1.0, 1001)).astype(np.float32)
    return out


def analytic_signal_amplitude(vg: np.ndarray, hg_ew: np.ndarray,
                              grav_anom: np.ndarray) -> np.ndarray:
    """3-component gravity analytic-signal amplitude.

    ``vg`` and ``hg_ew`` are two orthogonal gradient components supplied by
    the pinned stack; ``hg_ns`` (the third, north-south horizontal component)
    is computed here as a plain central-difference gradient of the raw
    isostatic gravity anomaly field -- pure array math, no external data.
    """
    gy_ns, _gx = np.gradient(grav_anom.astype(np.float64))
    asa = np.sqrt(vg.astype(np.float64) ** 2 + hg_ew.astype(np.float64) ** 2
                 + gy_ns ** 2)
    return asa.astype(np.float32)


def structure_tensor_coherence(field: np.ndarray, valid: np.ndarray,
                               window: int = 7) -> np.ndarray:
    """Local linear-edge coherence of ``field`` via the 2x2 gradient structure tensor.

    coherence = (lambda1 - lambda2) / (lambda1 + lambda2) in [0, 1]; 1 means a
    single dominant local gradient orientation (a linear edge, i.e. a fault
    trace), 0 means an isotropic/blob-like anomaly (e.g. an equant pluton).
    Uses a box filter (``scipy.ndimage.uniform_filter``) for the window sum,
    which is separable and runs in O(N) per axis regardless of window size.
    """
    from scipy.ndimage import uniform_filter

    f = np.asarray(field, np.float64)
    gy, gx = np.gradient(f)
    jxx = uniform_filter(gx * gx, size=window, mode="nearest")
    jyy = uniform_filter(gy * gy, size=window, mode="nearest")
    jxy = uniform_filter(gx * gy, size=window, mode="nearest")
    trace = jxx + jyy
    disc = np.sqrt(np.maximum((jxx - jyy) ** 2 + 4.0 * jxy ** 2, 0.0))
    lam1 = 0.5 * (trace + disc)
    lam2 = 0.5 * (trace - disc)
    denom = lam1 + lam2
    coh = np.where(denom > 1e-12, (lam1 - lam2) / np.maximum(denom, 1e-12), 0.0)
    return np.clip(coh, 0.0, 1.0).astype(np.float32)


def lane_surface(stack_path: str, footprint: np.ndarray) -> dict:
    """Build the GRAV-QUAD surface and its components.

    Returns float32 arrays keyed ``asa``, ``coherence``, ``S`` (the surface),
    plus ``valid``. Nothing here reads the fault catalogue, so catalogue
    withholding cannot leak through the surface.
    """
    foot = np.asarray(footprint, bool)
    grav_vg = clean(read_stack_band(stack_path, BAND["grav_vg"]), foot)
    grav_hg = clean(read_stack_band(stack_path, BAND["grav_hg_ew"]), foot)
    grav_anom = clean(read_stack_band(stack_path, BAND["grav_anom"]), foot)

    valid = (foot
             & np.isfinite(grav_vg) & (grav_vg > SENTINEL + 1e6)
             & np.isfinite(grav_hg) & (grav_hg > SENTINEL + 1e6)
             & np.isfinite(grav_anom) & (grav_anom > SENTINEL + 1e6))

    asa = analytic_signal_amplitude(grav_vg, grav_hg, grav_anom)
    del grav_vg, grav_hg, grav_anom
    coh = structure_tensor_coherence(asa, valid, window=7)

    asa_pct = percentile_rank(asa, valid)
    coh_pct = percentile_rank(coh, valid)
    S = (asa_pct * coh_pct).astype(np.float32)

    return dict(valid=valid, asa=asa_pct, coherence=coh_pct, S=S)
