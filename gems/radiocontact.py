"""RADIOCONTACT lane: radiometric alteration contact x gravity-gradient concordance.

Geology
-------
Geothermal systems are alteration-controlled: blind basement faults channel
fluids that produce potassium enrichment (illicite/adularia) and Th/U ratio
contrasts at the alteration front, coincident with buried density-contact
gravity gradients and a footwall-polarity horizontal derivative.  The
USGS/INGENIOUS catalogue is a scarp catalogue -- faults buried under
playa/alluvium or with diffused Quaternary scarps were never mapped -- but
their alteration halos and buried density contacts remain visible to
radiometrics and gravity.  RADIOCONTACT therefore targets catalogue-missing
blind, fluid-conducting structures rather than the mapped scarp population.

Surface (pure array math on caller-supplied arrays; the catalogue is read only
by the caller for masking, never to build features):

    rad_edge   = pct_rank( max( |grad(U/K)|, |grad(Th/K)| ) )   alteration contact
    grav_con   = pct_rank( |B11 iso_grav_anom_vg| * |B18 iso_grav_anom_hg_ew| )
                                           buried density contact + E-W footwall polarity
    mt_level   = pct_rank( B17 cond_surf )                      fluid pathway / clay-cap
    S          = rad_edge * grav_con * mt_level                   product of percentile ranks

All ranks are percentile ranks over the valid footprint (1001 knots).

Named non-fault mimic: K-rich ash-fall beds, non-tectonic basin-fill contacts,
playa/evaporite conductivity, irrigation salinity.

Layers
------
* B5  iso_grav_anom_slope  (gravity tilt magnitude context)
* B11 iso_grav_anom_vg     (isostatic gravity vertical gradient -> buried contact)
* B18 iso_grav_anom_hg     (signed E-W horizontal gravity derivative -> footwall polarity)
* B17 cond_surf            (subsurface MT electrical conductivity)
* ext_geodawn_rad_u8 bands K, Th, U (public-domain USGS GeoDAWN radiometrics)

Band numbers are 1-based positions in the pinned 19-band GeoDAWN stack
(``training_features.tif``).  Stack bands use the -3.4028235e+38 float32
sentinel for off-footprint cells; the radiometrics layer is uint8 0-255 on the
same pinned grid.
"""

from __future__ import annotations

import numpy as np
import rasterio

SENTINEL = -3.4028235e+38

# 1-based band numbers in training_features.tif (GDAL-verified in README band audit)
BAND = dict(
    grav_slope=5,   # iso_grav_anom_slope
    grav_vg=11,     # iso_grav_anom_vg  (buried density contact)
    grav_hg_ew=18,  # iso_grav_anom_hg  (signed E-W footwall polarity)
    cond_surf=17,   # cond_surf (MT fluid pathway)
)

__all__ = ["BAND", "SENTINEL", "read_stack_band", "read_radiometrics", "clean",
           "percentile_rank", "rad_contact_edge", "gravity_concordance",
           "mt_level", "lane_surface"]


def read_stack_band(path, band: int) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(int(band)).astype(np.float32)


def read_radiometrics(path) -> dict:
    """Return {'K','Th','U'} float32 arrays from the pinned GeoDAWN radiometrics layer."""
    with rasterio.open(path) as ds:
        desc = [str(d).upper() for d in ds.descriptions]
        idx = {name: i + 1 for i, name in enumerate(desc)}
        lookup = {n.upper(): n for n in ("K", "Th", "U")}
        missing = [n for n in lookup if n not in idx]
        if missing:
            raise ValueError(f"radiometrics layer missing bands {missing}; descriptions={desc}")
        return {orig: ds.read(idx[up]).astype(np.float32) for up, orig in lookup.items()}


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


def _grad_mag(a: np.ndarray) -> np.ndarray:
    gy, gx = np.gradient(a)
    return np.hypot(gy, gx).astype(np.float32)


def rad_contact_edge(K: np.ndarray, Th: np.ndarray, U: np.ndarray,
                     valid: np.ndarray) -> np.ndarray:
    """Alteration-contact strength: steeper of the U/K and Th/K ratio gradients."""
    eps = 1.0
    uk = np.where((K > 0) & (U > 0), U / np.maximum(K, eps), 0.0).astype(np.float32)
    tk = np.where((K > 0) & (Th > 0), Th / np.maximum(K, eps), 0.0).astype(np.float32)
    return np.maximum(_grad_mag(uk), _grad_mag(tk)).astype(np.float32)


def gravity_concordance(grav_vg: np.ndarray, grav_hg_ew: np.ndarray,
                        valid: np.ndarray) -> np.ndarray:
    """Buried-contact x footwall-polarity concordance: |vertical gradient| * |E-W derivative|."""
    return (np.abs(grav_vg) * np.abs(grav_hg_ew)).astype(np.float32)


def mt_level(cond: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """MT conductivity level as a fluid-pathway / clay-cap indicator."""
    return percentile_rank(cond, valid)


def lane_surface(stack_path: str, radio_path: str, footprint: np.ndarray) -> dict:
    """Build the RADIOCONTACT surface and its components.

    Returns float32 arrays keyed ``rad_edge``, ``grav_con``, ``mt_level``,
    ``S`` (the surface), plus ``valid``.  Nothing here reads the fault
    catalogue, so catalogue withholding cannot leak through the surface.
    """
    foot = np.asarray(footprint, bool)
    grav_slope = clean(read_stack_band(stack_path, BAND["grav_slope"]), foot)
    grav_vg = clean(read_stack_band(stack_path, BAND["grav_vg"]), foot)
    grav_hg = clean(read_stack_band(stack_path, BAND["grav_hg_ew"]), foot)
    cond = clean(read_stack_band(stack_path, BAND["cond_surf"]), foot)
    radio = read_radiometrics(radio_path)
    K, Th, U = radio["K"], radio["Th"], radio["U"]

    valid = (foot
             & np.isfinite(grav_slope) & (grav_slope > SENTINEL + 1e6)
             & np.isfinite(grav_vg) & (grav_vg > SENTINEL + 1e6)
             & np.isfinite(grav_hg) & (grav_hg > SENTINEL + 1e6)
             & np.isfinite(cond) & (cond > SENTINEL + 1e6))

    del grav_slope

    rad = rad_contact_edge(K, Th, U, valid)
    del K, Th, U
    grav = gravity_concordance(grav_vg, grav_hg, valid)
    del grav_vg, grav_hg

    rad_pct = percentile_rank(rad, valid)
    del rad
    grav_pct = percentile_rank(grav, valid)
    del grav
    mt_pct = percentile_rank(cond, valid)
    del cond

    S = (rad_pct * grav_pct * mt_pct).astype(np.float32)

    return dict(valid=valid, rad_edge=rad_pct, grav_con=grav_pct,
                mt_level=mt_pct, S=S)
