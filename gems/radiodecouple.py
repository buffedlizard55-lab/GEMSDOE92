"""RADIODECOUPLE lane: 3D Radiometric Alteration x Potential-Field Tensor Decoupling.

Geology & Physical Principles
-----------------------------
Active and concealed geothermal upflow in the northwestern Great Basin is
structurally controlled by permeable fault damage zones. Hydrothermal fluid
circulation creates characteristic geochemical alteration fronts:
1. Potassium metasomatism (illite/adularia formation) reflected in elevated K/Th.
2. Mobile hexavalent uranium migration and reduction selvages (U/Th).
3. Magnetite destruction / sulfidation creating Reduced-to-Pole (RTP) magnetic troughs.
4. Conductive smectite clay caps in magnetotelluric sounding (cond_surf, Band 17).

The primary geological challenge:
Flat-lying Tertiary rhyolitic ash-flow tuffs (ignimbrites) produce high radiogenic
concentrations and sharp erosional contact scarps that mimic hydrothermal alteration.
To decouple deep, fault-controlled alteration from rootless surficial ash sheets:
- True tectonic fault zones root into crystalline basement, creating sharp
  isostatic gravity horizontal gradients and vertical gradient steps.
- We compute the 3D cross-physics vector collinearity |n_rad . n_grav| between
  the radiometric contact normal vector n_rad = grad(K/Th) / ||grad(K/Th)|| and
  the potential-field gravity gradient normal vector n_grav = grad(g_iso) / ||grad(g_iso)||.
- When n_rad and n_grav are collinear (|n_rad . n_grav| -> 1), the radiometric
  alteration is structurally rooted to a deep basement fault.
- When they are decoupled (|n_rad . n_grav| -> 0), the edge is a rootless surficial
  ash-flow sheet or sediment facies boundary and is suppressed.

Layers used (from pinned inputs in .cache/gems_inputs/):
- geodawn_rad_u8: Bands K, Th, U (USGS GeoDAWN radiometrics)
- training_features.tif:
  - Band 2: rtp (Reduced-to-Pole magnetic anomaly)
  - Band 5: iso_grav_anom_slope (gravity tilt magnitude)
  - Band 11: iso_grav_anom_vg (isostatic gravity vertical gradient -> steep contact)
  - Band 13: iso_grav_anom (isostatic gravity anomaly -> field derivative)
  - Band 17: cond_surf (subsurface MT electrical conductivity -> clay cap)
  - Band 18: iso_grav_anom_hg (signed E-W horizontal gravity derivative)
"""
from __future__ import annotations

import numpy as np
import rasterio
from scipy.ndimage import laplace

SENTINEL = -3.4028235e+38

# 1-based band numbers in training_features.tif
BAND = dict(
    rtp=2,          # Reduced-to-Pole magnetic anomaly
    grav_slope=5,   # iso_grav_anom_slope
    grav_vg=11,     # iso_grav_anom_vg (isostatic gravity vertical gradient)
    grav_iso=13,    # iso_grav_anom (isostatic gravity anomaly)
    cond_surf=17,   # cond_surf (MT conductivity)
    grav_hg_ew=18,  # iso_grav_anom_hg (signed E-W horizontal gravity gradient)
)

__all__ = [
    "BAND", "SENTINEL", "read_stack_band", "read_radiometrics", "clean",
    "percentile_rank", "compute_radiodecouple_features", "lane_surfaces"
]


def read_stack_band(path, band: int) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(int(band)).astype(np.float32)


def read_radiometrics(path) -> dict[str, np.ndarray]:
    """Return {'K', 'Th', 'U'} float32 arrays from the pinned GeoDAWN radiometrics layer."""
    with rasterio.open(path) as ds:
        desc = [str(d).upper() for d in ds.descriptions]
        idx = {name: i + 1 for i, name in enumerate(desc)}
        lookup = {"K": "K", "TH": "Th", "U": "U"}
        missing = [up for up in lookup if up not in idx]
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
    """Percentile rank in [0, 1] over valid finite cells using 1001 quantile knots."""
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    out = np.zeros(a.shape, np.float32)
    vals = a[m]
    if vals.size == 0:
        return out
    knots = np.quantile(vals, np.linspace(0.0, 1.0, 1001))
    out[m] = np.interp(vals, knots, np.linspace(0.0, 1.0, 1001)).astype(np.float32)
    return out


def _grad_2d(a: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (gy, gx, mag) where mag = hypot(gy, gx)."""
    gy, gx = np.gradient(a)
    mag = np.hypot(gy, gx).astype(np.float32)
    return gy.astype(np.float32), gx.astype(np.float32), mag


def compute_radiodecouple_features(stack_path: str, radio_path: str, footprint: np.ndarray) -> dict:
    """Compute the multi-physics decoupled alteration and potential-field features.

    Zero fault-catalogue data is read here, ensuring that spatial holdout folds
    cannot leak catalogue truth into feature extraction.
    """
    foot = np.asarray(footprint, bool)

    # 1. Load potential-field and geophysical bands
    grav_slope = clean(read_stack_band(stack_path, BAND["grav_slope"]), foot)
    grav_vg = clean(read_stack_band(stack_path, BAND["grav_vg"]), foot)
    grav_iso = clean(read_stack_band(stack_path, BAND["grav_iso"]), foot)
    grav_hg_ew = clean(read_stack_band(stack_path, BAND["grav_hg_ew"]), foot)
    rtp = clean(read_stack_band(stack_path, BAND["rtp"]), foot)
    cond = clean(read_stack_band(stack_path, BAND["cond_surf"]), foot)

    # 2. Load radiometrics
    radio = read_radiometrics(radio_path)
    K = radio["K"]
    Th = radio["Th"]
    U = radio["U"]

    # 3. Valid calculation mask
    valid = (
        foot
        & np.isfinite(grav_slope) & (grav_slope > SENTINEL + 1e6)
        & np.isfinite(grav_vg) & (grav_vg > SENTINEL + 1e6)
        & np.isfinite(grav_iso) & (grav_iso > SENTINEL + 1e6)
        & np.isfinite(grav_hg_ew) & (grav_hg_ew > SENTINEL + 1e6)
        & np.isfinite(rtp) & (rtp > SENTINEL + 1e6)
        & np.isfinite(cond) & (cond > SENTINEL + 1e6)
        & np.isfinite(K) & np.isfinite(Th) & np.isfinite(U)
    )

    # 4. Radiometric alteration ratio & gradient vectors
    eps0 = 1.0
    k_th = np.where((K > 0) & (Th > 0), K / np.maximum(Th, eps0), 0.0).astype(np.float32)
    u_th = np.where((U > 0) & (Th > 0), U / np.maximum(Th, eps0), 0.0).astype(np.float32)

    # Horizontal gradient of K/Th
    rad_gy, rad_gx, rad_mag = _grad_2d(k_th)
    rad_mag_u, _, _ = _grad_2d(u_th)
    # Combined alteration gradient magnitude
    alteration_mag = np.maximum(rad_mag, rad_mag_u)

    # Normalized radiometric gradient normal vector
    eps_norm = 1e-4
    n_rad_y = rad_gy / (rad_mag + eps_norm)
    n_rad_x = rad_gx / (rad_mag + eps_norm)

    # 5. Potential-field gravity gradient vector
    # Band 18 is signed E-W horizontal derivative: gx ~ grav_hg_ew
    # Central difference of Band 13 in y gives gy
    grav_gy, _, _ = _grad_2d(grav_iso)
    grav_gx = grav_hg_ew
    grav_mag = np.hypot(grav_gy, grav_gx).astype(np.float32)

    n_grav_y = grav_gy / (grav_mag + eps_norm)
    n_grav_x = grav_gx / (grav_mag + eps_norm)

    # 6. 3D Vector Collinearity Decoupling Operator: |n_rad . n_grav|
    collinearity = np.abs(n_rad_x * n_grav_x + n_rad_y * n_grav_y).astype(np.float32)
    collinearity = np.clip(collinearity, 0.0, 1.0)
    collinearity = np.where(valid, collinearity, 0.0)

    # 7. Basement density contact strength (vertical derivative magnitude * slope)
    grav_contact = (np.abs(grav_vg) * grav_slope).astype(np.float32)

    # 8. Magnetic demagnetization trough: positive Laplacian of RTP
    # High-temperature hydrothermal alteration destroys primary magnetic titanomagnetite
    rtp_lap = laplace(rtp).astype(np.float32)
    rtp_demag = np.clip(rtp_lap, 0.0, None)

    # 9. Percentile ranking of component indicators
    alteration_pct = percentile_rank(alteration_mag, valid)
    collinearity_pct = percentile_rank(collinearity, valid)
    grav_contact_pct = percentile_rank(grav_contact, valid)
    rtp_demag_pct = percentile_rank(rtp_demag, valid)
    cond_pct = percentile_rank(cond, valid)

    # 10. Synthesized decoupled surfaces
    # S_standalone: alteration gradient * collinearity with basement step * gravity contact * MT conductivity
    S_standalone = (alteration_pct * collinearity_pct * grav_contact_pct * cond_pct).astype(np.float32)
    S_standalone = np.where(valid, S_standalone, 0.0)

    # S_demag: S_standalone * magnetic demagnetization trough
    S_demag = (S_standalone * rtp_demag_pct).astype(np.float32)
    S_demag = np.where(valid, S_demag, 0.0)

    return dict(
        valid=valid,
        alteration_mag=alteration_pct,
        collinearity=collinearity_pct,
        grav_contact=grav_contact_pct,
        rtp_demag=rtp_demag_pct,
        cond=cond_pct,
        S_standalone=S_standalone,
        S_demag=S_demag,
    )


def lane_surfaces(stack_path: str, radio_path: str, footprint: np.ndarray) -> dict:
    """Convenience wrapper returning all candidate surfaces and features."""
    return compute_radiodecouple_features(stack_path, radio_path, footprint)
