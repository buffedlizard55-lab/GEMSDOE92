"""LISTRICDIP: cover-dependent listric offset of the basement cutoff.

A Basin-and-Range normal fault that dips δ from horizontal, under cover
thickness C, cuts the basement a horizontal distance

    Δ = C * cot(δ)

down-dip of its near-surface trace. Worms and co-located gravity ridges sit
on the basement cutoff. The catalogue sits on exposed scarps. This module
emits on neither locus. It moves a basement-gradient crest up-dip by Δ, and
separately scores a reversed-polarity antithetic crest one relay-width
down-dip.

No function in this module reads the fault catalogue. Band 6 is not used
(it is radiometric total count, not magnetic tilt).
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates

from .breakline import percentile_rank

EPS = np.float32(1.0e-6)
DIP_DEG = 50.0
COVER_MIN_M = 400.0
COVER_MAX_M = 1100.0
ANTI_PX = (22.0, 35.0)


def _clean(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    fill = float(np.median(a[m])) if m.any() else 0.0
    return np.where(m, a, np.float32(fill)).astype(np.float32)


def sample_shift(field: np.ndarray, ny: np.ndarray, nx: np.ndarray, shift_px) -> np.ndarray:
    """Sample ``field`` at +shift along (ny, nx).

    If (ny, nx) points down-dip, the value returned at a pixel is the field
    value down-dip of that pixel. A crest down-dip of the pixel is therefore
    painted on the up-dip landing.
    """
    field = np.asarray(field, dtype=np.float32)
    ny = np.asarray(ny, dtype=np.float32)
    nx = np.asarray(nx, dtype=np.float32)
    h, w = field.shape
    yy, xx = np.indices((h, w), dtype=np.float32)
    sy = np.asarray(shift_px, dtype=np.float32)
    src_y = yy + sy * ny
    src_x = xx + sy * nx
    return map_coordinates(field, [src_y, src_x], order=1, mode="nearest").astype(np.float32)


def basement_frame(depth: np.ndarray, valid: np.ndarray, sigma: float = 2.0):
    """Smoothed depth, gradient magnitude, and unit vector toward increasing depth."""
    z = gaussian_filter(_clean(depth, valid), float(sigma))
    gy, gx = np.gradient(z)
    mag = np.hypot(gy, gx).astype(np.float32)
    nrm = mag + EPS
    ny = (gy / nrm).astype(np.float32)
    nx = (gx / nrm).astype(np.float32)
    return z.astype(np.float32), mag, ny, nx


def gradient_crest(mag: np.ndarray, ny: np.ndarray, nx: np.ndarray) -> np.ndarray:
    """1-pixel non-maximum suppression along the depth-gradient normal."""
    plus = sample_shift(mag, ny, nx, np.float32(1.0))
    minus = sample_shift(mag, -ny, -nx, np.float32(1.0))
    return ((mag >= plus) & (mag >= minus) & (mag > 0)).astype(np.float32)


def updip_shift_px(cover_m: np.ndarray, dip_deg: float) -> np.ndarray:
    dip = float(dip_deg)
    if not 20.0 < dip < 80.0:
        raise ValueError("dip_deg must be between 20 and 80")
    cot = float(1.0 / np.tan(np.deg2rad(dip)))
    return np.clip(np.asarray(cover_m, dtype=np.float32) * np.float32(cot) / np.float32(100.0), 0.0, 16.0).astype(np.float32)


def cross_contour(elev: np.ndarray, ny: np.ndarray, nx: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Fraction of elevation gradient parallel to basement strike.

    Near 0: the basement contact follows an elevation contour (pluvial bench
    or fan contour). Near 1: the contact crosses contours (a tectonic trace
    climbing or dropping along strike). Band 12 is detrended, so this is not
    an absolute shoreline elevation test.
    """
    z = gaussian_filter(_clean(elev, valid), 1.5)
    gy, gx = np.gradient(z)
    emag = np.hypot(gy, gx).astype(np.float32)
    # Strike tangent (-nx, ny) is perpendicular to the down-dip unit (ny, nx).
    along = np.abs((-nx) * gy + ny * gx).astype(np.float32)
    return (along / (emag + EPS)).astype(np.float32)


def polarity_concordance(depth: np.ndarray, grav_hg: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Positive where the E–W basement slope and Band 18 share a sign.

    The product is computed in float64. Band 18 and the depth gradient can
    each exceed 1e4, and their float32 product overflows to inf.
    """
    gx = np.gradient(gaussian_filter(_clean(depth, valid), 2.0))[1].astype(np.float64)
    hg = _clean(grav_hg, valid).astype(np.float64)
    raw = gx * hg
    raw = np.where(np.isfinite(raw), raw, 0.0)
    return np.clip(raw, 0.0, None).astype(np.float32)


def updip_surface(
    depth: np.ndarray,
    elev: np.ndarray,
    slope: np.ndarray,
    grav: np.ndarray,
    grav_hg: np.ndarray,
    valid: np.ndarray,
    *,
    dip_deg: float = DIP_DEG,
    cover_min_m: float = COVER_MIN_M,
    cover_max_m: float = COVER_MAX_M,
) -> dict[str, np.ndarray]:
    """Catalogue-free up-dip surface-trace score. All ranks are over ``valid``."""
    valid = np.asarray(valid, bool)
    _z, mag, ny, nx = basement_frame(depth, valid)
    crest = gradient_crest(mag, ny, nx) * mag
    cover = gaussian_filter(_clean(depth, valid), 4.0)
    shift = updip_shift_px(cover, dip_deg)
    landed = sample_shift(crest, ny, nx, shift)
    habitat = ((cover >= cover_min_m) & (cover <= cover_max_m) & valid).astype(np.float32)
    trans = cross_contour(elev, ny, nx, valid)
    shore = ((1.0 - trans) ** 2).astype(np.float32)
    # Subtle slope break: reward a break, suppress the steepest cliffs.
    log_s = np.log(np.maximum(_clean(slope, valid), 0.0) + np.float32(1.0))
    break_mag = np.hypot(*np.gradient(gaussian_filter(log_s, 1.0))).astype(np.float32)
    slope_pct = percentile_rank(_clean(slope, valid), valid)
    subtle = percentile_rank(break_mag, valid) * np.clip(1.0 - slope_pct, 0.0, 1.0)
    pol = percentile_rank(polarity_concordance(depth, grav_hg, valid), valid)
    grav_edge = percentile_rank(np.hypot(*np.gradient(gaussian_filter(_clean(grav, valid), 2.0))).astype(np.float32), valid)
    raw = (
        percentile_rank(landed, valid)
        * habitat
        * (0.55 + 0.45 * trans)
        * (1.0 - 0.65 * shore)
        * (0.45 + 0.55 * subtle)
        * (0.60 + 0.40 * pol)
        * (0.70 + 0.30 * grav_edge)
    ).astype(np.float32)
    raw = np.where(valid, raw, 0.0).astype(np.float32)
    return {
        "S_raw": raw,
        "S_pct": percentile_rank(raw, valid),
        "landed": landed.astype(np.float32),
        "shift_px": shift,
        "crest_mag": crest.astype(np.float32),
        "trans": trans,
        "shore": shore,
        "subtle": subtle.astype(np.float32),
        "polarity": pol,
        "habitat": habitat,
        "ny": ny,
        "nx": nx,
        "mag": mag,
    }


def antithetic_surface(
    depth: np.ndarray,
    elev: np.ndarray,
    grav_hg: np.ndarray,
    valid: np.ndarray,
    *,
    anti_px: float,
    regional_sigma: float = 12.0,
) -> dict[str, np.ndarray]:
    """Reversed-polarity crest ``anti_px`` down-dip of a master basement cutoff.

    The regional hanging-wall direction is the gradient of depth smoothed at
    ``regional_sigma`` (default 1.2 km). At a candidate pixel, look that many
    pixels back up the regional dip. Require a strong basement gradient there
    and a local gradient of opposite sense (the antithetic flank). Relay
    widths of 2.2 km (22 px) and 3.5 km (35 px) sit inside the published Great
    Basin step-over width range; this is not a fit to the catalogue.
    """
    if anti_px < 8.0 or anti_px > 60.0:
        raise ValueError("anti_px outside the pre-registered 0.8–6 km window")
    valid = np.asarray(valid, bool)
    _z, mag, ny, nx = basement_frame(depth, valid, sigma=2.5)
    _rz, _rm, ry, rx = basement_frame(depth, valid, sigma=float(regional_sigma))
    mag_up = sample_shift(mag, -ry, -rx, np.float32(anti_px))
    oppose = np.clip(-(ny * ry + nx * rx), 0.0, 1.0).astype(np.float32)
    local_crest = gradient_crest(mag, ny, nx)
    # Rank each magnitude before multiplying so large basement gradients cannot overflow.
    raw_mag = (
        percentile_rank(mag, valid)
        * percentile_rank(mag_up, valid)
        * oppose
        * (0.35 + 0.65 * local_crest)
    ).astype(np.float32)
    trans = cross_contour(elev, ny, nx, valid)
    pol = percentile_rank(polarity_concordance(depth, grav_hg, valid), valid)
    cover = gaussian_filter(_clean(depth, valid), 4.0)
    # Antithetic strands of a half-graben sit in the deeper hanging wall.
    deep = np.clip((cover - np.float32(200.0)) / np.float32(800.0), 0.0, 1.0).astype(np.float32)
    raw = (
        percentile_rank(raw_mag, valid)
        * (0.50 + 0.50 * trans)
        * (0.55 + 0.45 * pol)
        * (0.40 + 0.60 * deep)
    ).astype(np.float32)
    raw = np.where(valid, raw, 0.0).astype(np.float32)
    return {
        "S_raw": raw,
        "S_pct": percentile_rank(raw, valid),
        "oppose": oppose,
        "raw_mag": raw_mag,
        "trans": trans,
        "anti_px": np.float32(anti_px),
    }
