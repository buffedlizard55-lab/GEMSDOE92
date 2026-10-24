"""ANASIG lane surface: magnetic analytic-signal ridges (session 2026-10-24).

Geology
-------
The analytic signal of a magnetic field peaks over the edges of
magnetised source bodies regardless of magnetisation direction.  In
the pinned 19-band stack the horizontal and vertical TMI gradients
(Band 3 ``tmi_hg``, Band 9 ``tmi_vg``) give a 2-D approximation

    A(x) = sqrt( B3(x)^2 + B9(x)^2 )

whose ridges sit over near-vertical magnetic contacts -- basement
fault offsets and intrusive/lithologic boundaries -- including under
non-magnetic basin fill where there is no DEM scarp (contrast
BREAKLINE/SCARPPOL) and no usable gravity crest (contrast GRAVCREST).
The lane surface gates A by the structure-tensor coherence of Band 14
(``tmi``) so isotropic magnetic noise is down-weighted:

    S(x) = pct_rank(A(x)) * coherence(Band14)(x),   S_pct = pct_rank(S)

ranks over the valid footprint, 1001 knots, project-standard.

Why it could find catalogue-missing faults: the H19-5 skeleton behind
parent R0 is a *multi-line corroborated* worm set; a magnetic contact
supported by the analytic signal alone (no corroborating gravity or
terrain line) could be dropped from that skeleton and from the
USGS/INGENIOUS catalogue, yet still mark a basement fault that
propagates into cover.  Candidate pixels lie >3 px from every H19-5
pixel, so the lane spends its far budget exactly where the
corroborated skeleton is silent.

Named non-fault mimics: lithologic contacts with no fault offset,
dike/sill edges, buried volcanic flow margins, and cultural magnetic
noise.  An analytic-signal ridge is a contact, not proof of a fault.

Nothing here reads the fault catalogue.  Pure array math;
``scripts/build_anasig_variants.py`` owns file I/O.  Pre-build screen
(docs/HYPOTHESES_20261024_SCARPPOL.md): SCREEN-AUC 0.503999,
far-set SGMC PROXY 0.028167; in-memory f45 hybrid HOLDOUT-DTI 0.004967
with forward overlap 0.528 vs BREAKLINE f45 -- the first screened
surface that is both holdout-positive and lane-disjoint.
"""

from __future__ import annotations

import numpy as np

from .breakline import percentile_rank, spaced_top_mask, structure_tensor_coherence

__all__ = ["percentile_rank", "structure_tensor_coherence", "spaced_top_mask",
           "analytic_signal_magnitude", "lane_surface"]


def _clean(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    fill = float(np.median(a[m])) if m.any() else 0.0
    return np.where(np.isfinite(a), a, np.float32(fill)).astype(np.float32)


def analytic_signal_magnitude(tmi_hg: np.ndarray, tmi_vg: np.ndarray,
                              valid: np.ndarray) -> np.ndarray:
    """``sqrt(tmi_hg^2 + tmi_vg^2)`` on sentinel-cleaned bands, float32."""
    valid = np.asarray(valid, bool)
    h = _clean(tmi_hg, valid)
    v = _clean(tmi_vg, valid)
    return np.hypot(h, v).astype(np.float32)


def lane_surface(tmi_hg: np.ndarray, tmi_vg: np.ndarray, tmi: np.ndarray,
                 valid: np.ndarray) -> dict[str, np.ndarray]:
    """ANASIG surface: ``A_pct``, ``coherence``, ``S_raw``, ``S_pct``."""
    valid = np.asarray(valid, bool)
    a_pct = percentile_rank(analytic_signal_magnitude(tmi_hg, tmi_vg, valid), valid)
    coh = structure_tensor_coherence(tmi, valid)
    s_raw = (a_pct * coh).astype(np.float32)
    return {"A_pct": a_pct, "coherence": coh, "S_raw": s_raw,
            "S_pct": percentile_rank(s_raw, valid)}
