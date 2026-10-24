"""STRAINBREAK lane surface: coherent DEM scarp-breaks under active strain.

Session 2026-10-24 (late).  Design and screen: docs/HYPOTHESES_20261024_GRAVCrest.md
(rank 2; rank-1 GRAVCrest was falsified by the pre-build screen,
evidence/gravcrest_screen.json) and evidence/gravcrest_screen.json.

Geology
-------
BREAKLINE (gems/breakline.py) places far dots on linear breaks-in-slope:
``L = pct_rank(||grad det_elev_slope||) * coherence(det_elev)``.  STRAINBREAK
multiplies that label-free terrain lineament field by the percentile rank of
the geodetic strain-rate magnitude (Band 4 ``geod_2ndinv``, the second
invariant of the GPS/InSAR strain-rate tensor):

    S(x) = L_raw(x) * pct_rank(geod_2ndinv)(x)

The target is a scarp-break on a structure that is *currently loading*:
young, still-propagating strands in extensional step-overs and relay ramps
(the Faulds dilatational settings hosting a large share of Great Basin
geothermal systems) can be geomorphically subtle -- hence missing from a
catalogue built from mappable Quaternary scarps -- while sitting in
high-strain-rate crust.  The 2020 M6.5 Monte Cristo Range earthquake
ruptured largely unmapped strands of the Candelaria fault: seismogenic,
strained, and absent from the catalogue.

Why the second invariant and not dilatation (Band 8): the pre-registered
screen scored identical 16,944-dot far sets on the off-catalogue USGS SGMC
bedrock-fault control -- L x pct(2ndinv) 0.058377 vs L x pct(dilatation)
0.040133 (plain L 0.072325).  The screen rule named SGMC the primary
selector, so Band 4 is the built field; the dilatation variant is recorded
as screened-and-not-built.

Named non-fault mimics: Walker Lane elastic strain shadows (high total
strain, shear-parallel, no open normal fault), alluvial compaction /
subsidence strain, and -- inherited from L -- Lake Lahontan shoreline
terraces and fan-segment boundaries that happen to lie in strained crust.

Everything here is pure array math reusing gems.breakline components; the
builder owns file I/O.  Nothing reads the fault catalogue.
"""

from __future__ import annotations

import numpy as np

from .breakline import lane_surface, percentile_rank


def strainbreak_surface(det_elev: np.ndarray, det_elev_slope: np.ndarray,
                        geod_2ndinv: np.ndarray, valid_topo: np.ndarray,
                        valid_strain: np.ndarray) -> dict[str, np.ndarray]:
    """Build S = L_raw * pct_rank(geod_2ndinv) and its percentile rank.

    ``valid_topo`` / ``valid_strain`` are the finite-value masks for the
    topographic bands (12/19) and the strain band (4).  Percentile ranks are
    taken over each field's own valid mask (project-standard 1001-knot
    construction via gems.breakline.percentile_rank); ``S_pct`` is ranked
    over the intersection.
    """
    valid_topo = np.asarray(valid_topo, bool)
    valid_strain = np.asarray(valid_strain, bool)
    both = valid_topo & valid_strain
    bl = lane_surface(det_elev, det_elev_slope, valid_topo)
    strain_pct = percentile_rank(geod_2ndinv, valid_strain)
    s_raw = (bl["L_raw"] * strain_pct).astype(np.float32)
    s_raw[~both] = 0.0
    s_pct = percentile_rank(s_raw, both)
    return {"L_raw": bl["L_raw"], "L_pct": bl["L_pct"],
            "strain_pct": strain_pct, "S_raw": s_raw, "S_pct": s_pct,
            "valid_both": both}
