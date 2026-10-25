"""PHASEWIND: multi-scale topological charge of the RTP complex-gradient field.

The lane uses only the Band 2 reduced-to-pole magnetic anomaly. At each
Gaussian scale, the complex first derivative ``sigma * (dG/dx + i*dG/dy)``
encodes local gradient orientation. The phase winding around an 8-point ring is
an integer topological-charge estimate; matching charge at two scales is the
candidate contact-termination cue. This is an experimental feature operator,
not a fault detector with established specificity.

No catalogue or label input is read here. Callers own provenance, masks,
holdout folds, emission, and submission packaging.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
from scipy import ndimage as ndi

from .breakline import percentile_rank

SCALES_PX: tuple[float, ...] = (2.0, 4.0, 8.0)
RING_RADIUS_PX = 2
CHARGE_TOLERANCE = 0.25
RING_OFFSETS = (
    (-1, -1), (-1, 0), (-1, 1), (0, 1),
    (1, 1), (1, 0), (1, -1), (0, -1),
)


def phase_winding_scale(
    rtp: np.ndarray,
    valid: np.ndarray,
    sigma_px: float,
    *,
    ring_radius_px: int = RING_RADIUS_PX,
    charge_tolerance: float = CHARGE_TOLERANCE,
) -> dict[str, np.ndarray | float | int]:
    """Compute one scale's charge, amplitude rank, and phase-winding feature.

    ``valid`` is combined with finite-value and large-sentinel checks. Cells
    within ``ceil(4*sigma_px)`` pixels of invalid data are excluded so the
    Gaussian derivative is not driven by the median fill at a mask boundary.
    The output feature is zero outside this safe mask and in cells whose phase
    winding is not approximately one complete turn (absolute charge near 1).
    """
    image = np.asarray(rtp, dtype=np.float32)
    mask = np.asarray(valid, dtype=bool)
    if image.ndim != 2 or image.shape != mask.shape:
        raise ValueError("rtp and valid must be matching 2-D arrays")
    if not np.isfinite(sigma_px) or sigma_px <= 0:
        raise ValueError("sigma_px must be finite and positive")
    if not isinstance(ring_radius_px, (int, np.integer)) or ring_radius_px < 1:
        raise ValueError("ring_radius_px must be a positive integer")
    if not np.isfinite(charge_tolerance) or not 0 < charge_tolerance < 1:
        raise ValueError("charge_tolerance must be in (0,1)")

    mask = mask & np.isfinite(image) & (image > -1.0e30)
    if not mask.any():
        raise ValueError("valid mask has no finite RTP values")
    vals = image[mask]
    fill = np.float32(np.median(vals))
    clean = np.where(mask, image, fill).astype(np.float32, copy=False)

    # Separable Gaussian derivatives avoid a full-grid dense convolution.
    gx = ndi.gaussian_filter(
        clean, sigma=float(sigma_px), order=(0, 1), mode="nearest", truncate=4.0
    ).astype(np.float32, copy=False)
    gy = ndi.gaussian_filter(
        clean, sigma=float(sigma_px), order=(1, 0), mode="nearest", truncate=4.0
    ).astype(np.float32, copy=False)
    amplitude = np.hypot(gx, gy).astype(np.float32, copy=False)
    phase = np.arctan2(gy, gx).astype(np.float32, copy=False)
    del gx, gy

    winding_sum = np.zeros(image.shape, dtype=np.float32)
    ring_min_amp = np.full(image.shape, np.inf, dtype=np.float32)
    ring_sum_amp = np.zeros(image.shape, dtype=np.float32)
    for index, (dy, dx) in enumerate(RING_OFFSETS):
        next_dy, next_dx = RING_OFFSETS[(index + 1) % len(RING_OFFSETS)]
        # For each output cell, shift samples from the corresponding ring site
        # into the cell. The safe mask below excludes wraparound at array edges.
        here_phase = np.roll(phase, shift=(-dy * ring_radius_px, -dx * ring_radius_px), axis=(0, 1))
        next_phase = np.roll(phase, shift=(-next_dy * ring_radius_px, -next_dx * ring_radius_px), axis=(0, 1))
        delta = next_phase - here_phase
        winding_sum += np.arctan2(np.sin(delta), np.cos(delta)).astype(np.float32)
        here_amp = np.roll(amplitude, shift=(-dy * ring_radius_px, -dx * ring_radius_px), axis=(0, 1))
        ring_min_amp = np.minimum(ring_min_amp, here_amp)
        ring_sum_amp += here_amp
        del here_phase, next_phase, delta, here_amp

    charge = (winding_sum / np.float32(2.0 * np.pi)).astype(np.float32)
    edge_guard = max(int(np.ceil(4.0 * float(sigma_px))), ring_radius_px)
    distance_from_invalid = ndi.distance_transform_edt(mask)
    safe = mask & (distance_from_invalid > edge_guard)
    ring_mean_amp = (ring_sum_amp / np.float32(len(RING_OFFSETS))).astype(np.float32)
    positive_amp = ring_mean_amp[safe & np.isfinite(ring_mean_amp) & (ring_mean_amp > 0)]
    amp_ref = float(np.median(positive_amp)) if positive_amp.size else 0.0
    amp_floor = max(np.finfo(np.float32).tiny, amp_ref * 1.0e-6)
    safe &= ring_min_amp > amp_floor

    absolute_charge = np.abs(charge)
    charge_confidence = np.clip(
        1.0 - np.abs(absolute_charge - 1.0) / np.float32(charge_tolerance),
        0.0,
        1.0,
    ).astype(np.float32)
    charge_confidence[~safe] = 0.0
    amplitude_rank = percentile_rank(ring_mean_amp, safe)
    feature = (charge_confidence * amplitude_rank).astype(np.float32)
    feature[~safe] = 0.0
    charge[~safe] = 0.0
    amplitude_rank[~safe] = 0.0

    return {
        "charge": charge,
        "charge_confidence": charge_confidence,
        "amplitude_rank": amplitude_rank,
        "feature": feature,
        "valid": safe,
        "sigma_px": float(sigma_px),
        "edge_guard_px": int(edge_guard),
        "amplitude_floor": float(amp_floor),
    }


def persistent_surface(
    scales: dict[float, dict[str, np.ndarray | float | int]],
    selected_pairs: tuple[tuple[float, float], ...] | None = None,
) -> np.ndarray:
    """Return max(min(feature_i, feature_j)) for same-sign winding pairs.

    Requiring sign agreement avoids treating unrelated high-curvature critical
    points at two scales as persistent. ``selected_pairs`` supports the frozen
    two-scale ablations; the default checks all available pairs.
    """
    if len(scales) < 2:
        raise ValueError("at least two scale responses are required")
    keys = tuple(sorted(scales))
    pairs = selected_pairs or tuple(combinations(keys, 2))
    shape = np.asarray(scales[keys[0]]["feature"]).shape
    out = np.zeros(shape, dtype=np.float32)
    seen = set()
    for left, right in pairs:
        if left not in scales or right not in scales or left == right:
            raise ValueError(f"invalid selected scale pair {(left, right)}")
        pair_key = tuple(sorted((left, right)))
        if pair_key in seen:
            raise ValueError(f"duplicate scale pair {pair_key}")
        seen.add(pair_key)
        fa = np.asarray(scales[left]["feature"], dtype=np.float32)
        fb = np.asarray(scales[right]["feature"], dtype=np.float32)
        qa = np.asarray(scales[left]["charge"], dtype=np.float32)
        qb = np.asarray(scales[right]["charge"], dtype=np.float32)
        if any(arr.shape != shape for arr in (fa, fb, qa, qb)):
            raise ValueError("scale response shape mismatch")
        same_sign = (qa * qb) > 0.0
        out = np.maximum(out, np.where(same_sign, np.minimum(fa, fb), 0.0))
    return np.clip(out, 0.0, 1.0).astype(np.float32, copy=False)


def build_arms(rtp: np.ndarray, valid: np.ndarray) -> dict[str, dict[str, np.ndarray]]:
    """Compute the three pre-registered PHASEWIND arms and per-scale canaries."""
    scale_features = {scale: phase_winding_scale(rtp, valid, scale) for scale in SCALES_PX}
    arms = {
        "phasewind_200_400": persistent_surface(scale_features, ((2.0, 4.0),)),
        "phasewind_400_800": persistent_surface(scale_features, ((4.0, 8.0),)),
        "phasewind_200_400_800": persistent_surface(scale_features),
    }
    return {"scales": scale_features, "arms": arms}
