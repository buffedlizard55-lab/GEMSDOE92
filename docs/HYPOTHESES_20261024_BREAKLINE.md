# Historical hypotheses — 2026-10-24 (BREAKLINE session)

> This page records an earlier lane’s pre-build ranking; expected values/projections are not scores, and its “next” language is not current. Current qualitative shortlist/status: [HYPOTHESES.md](HYPOTHESES.md) and [REPO_REVIEW_20261024.md](REPO_REVIEW_20261024.md). No current candidate is cleared to submit.

Protocol step: generate 3–5 geologically distinct, previously untried
hypotheses, rank by expected HOLDOUT-DTI gain per build cost, validate
the top one on the spatially blocked holdout, stay inside the assigned
lane (literal uniqueness vs the registry is a hard stop). Empirical
priors below come from this session's pre-build screens (20 single-band
surfaces + 10 composites, ranked against two *different* proxies:
withheld-catalogue AUC and the off-catalogue USGS SGMC fault control;
screen code preserved in `.cache/diag/`, headline numbers in
`docs/ANALYSIS_20261024.md` §3–4).

Design constraint that shapes every lane: R0 ⊂ SOLO ⊂ D2.8 ⊂ H19-5
exactly (verified), so **any** submission whose dots stay inside the
H19-5 skeleton can share ≤ 70 % of dots within 3 px of R0 only by
emitting skeleton pixels R0 dropped — still a behavioural near-duplicate
of the worm family. True lane separation therefore requires a material
fraction of dots **> 3 px off the whole skeleton**, and the signal must
pay for the parent mass it displaces.

## 1. BREAKLINE (built this session) — DEM scarp-break coherence

- **Layers:** Band 19 `det_elev_slope`, Band 12 `det_elev`
  (`training_features.tif`).
- **Signature:** `L = pct_rank(‖∇Band19‖) × structure-tensor
  coherence(Band12; σd = 1, σt = 2)` — a *linear break-in-slope*: strong
  slope gradient whose local orientation is consistent (scarp face), not
  isotropic roughness.
- **Why it finds catalogue-missing faults:** the live labels are expert
  mapping, plausibly from high-resolution DEMs (repo ships
  `1m_DEM_links.csv`). Faults juxtaposing like lithologies, or offsetting
  only alluvium, make a scarp but no magnetic/gravity contrast — the
  potential-field worm skeleton systematically misses them while an
  expert on a DEM traces exactly this expression.
- **Difference from repo:** every prior lane either stays on the worm
  skeleton or (TIPGAP-far) extrapolates the *catalogue* network. No prior
  lane sources far dots from a DEM-only lineament detector independent
  of both skeleton and catalogue geometry.
- **Screen result:** spaced top-L far sets hit off-catalogue SGMC faults
  at 0.107–0.118 DTI-equivalent vs R0's 0.096, while their
  catalogue-proximity diagnostics *rose* rather than collapsed — the only
  family that did both. Built f33/f38/f45; holdout and controls in
  `evidence/breakline_proxy_audit.json` (f45: HOLDOUT 0.004861,
  SGMC 0.12611, worst forward overlap 0.550).
- **Named mimic (falsifier class):** Pleistocene Lake Lahontan
  shorelines and wave-cut terraces, alluvial-fan segment boundaries and
  incised channel banks — linear, coherent slope breaks with no fault.
- **Rank: 1** — best screen evidence, zero external data, directly
  matches the (terrain) instrument experts map with.

## 2. Signed gravity-HGM gamma crest (unbuilt) — the one signed band

- **Layers:** Band 18 `iso_grav_anom_hg` (signed; every other band is a
  magnitude or rate), corroborated by Band 5 `iso_grav_anom_slope`.
- **Signature:** zero-crossing / crest line of the signed horizontal
  gradient magnitude (a "gamma curve" source-edge estimator), oriented
  with Band-5 maxima: the horizontal-gradient crest sits over the
  near-vertical density edge, offset **basinward** of the surface-mapped
  range-front fault for dipping/listric geometries (USGS maxspot
  literature).
- **Why catalogue-missing:** basin-bounding faults under cover, where the
  surface trace is buried and the density edge is the only expression.
- **Difference from repo:** prior lanes used |grad|-style magnitudes
  (undirected); the *signed* band's zero set and crest offset have never
  been used, and no lane ever placed dots deliberately offset from the
  skeleton line following a dip-direction rule.
- **Screen note:** raw Band-18 surfaces screened weakly as *fields* (the
  discriminative object is the crest curve, not pixel AUC) — validate by
  distance-to-SGMC-fault hit-rate of crest pixels, not pixel ranks.
- **Rank: 2** — cheap (in-stack), geology is textbook, but offset
  geometry needs one careful validation pass; an Euler-deconvolution
  depth filter was checked absent from this repo and stays a possible
  refinement.

## 3. BASEMENT-STEP (screened OUT this session) — depth-to-base scarp

- **Layers:** Band 15 `depth_to_base_surf`, Band 17 `cond_surf`.
- **Signature (hypothesised):** breaks in the depth-to-conductive-basement
  surface = buried basin-edge fault steps.
- **Screen verdict:** AUC vs SGMC control 0.378, spaced top-set SGMC hits
  0.4 % — worse than chance-enriched. The surface is too smooth/inverted
  to expose steps at 100 m posting, or what steps exist are not registered
  to mapped bedrock faults. **Not buildable on this evidence; do not
  retry without a new surface (e.g. a proper Jachens–Moring-style gravity
  basement inversion from the USGS isostatic grid, free via
  https://www.usgs.gov — significant cost, unproven marginal value).**

## 4. Coulomb/dilatation×structure interaction (unbuilt)

- **Layers:** Bands 4/7/8 (geodetic 2nd invariant, shear, dilatation
  rates) × BREAKLINE L.
- **Signature:** coherent DEM break **and** elevated contemporary strain
  rate — a *currently loading*, unmapped structure. The 2020 M6.5 Monte
  Cristo Range earthquake ruptured largely unmapped parts of the
  Candelaria fault: seismogenic, absent from catalogues (USGS pub
  70217872; Koehler et al. 2021 SRL).
- **Difference from repo:** DILATATION used Band 8 to re-rank on-skeleton
  dots (duplicate). Strain as a *multiplier on an independent far
  lineament* has never been tried; pure seismicity/strain fields
  screened too smooth to place dots alone.
- **Rank: 3** — plausible sharpening of BREAKLINE, unmeasurable size;
  test only after one organizer receipt tells us the far-dose direction.

## 5. Terrace/shoreline-suppressed BREAKLINE (unbuilt)

- **Layers:** L (above) − Lahontan shoreline elevation bands (published
  stillstand elevations are free, e.g. USGS/NBMG compilations) −
  contour-parallelism penalty.
- **Signature:** the same scarp detector with the named mimic class
  explicitly masked: breaks tracking known shoreline elevations or
  running contour-parallel for long distances are down-weighted.
- **Why:** if BREAKLINE's live FP mass concentrates in shoreline
  mimics, this is the cheapest dose of geological specificity available.
- **Rank: 4** — directly attacks BREAKLINE's biggest known weakness but
  only measurable cheaply on the same biased instruments; hold until a
  receipt shows whether far dots earn at all.

## Budget accounting (transparency)

Protocol budget = 3 built experiments per session. This session built
the three BREAKLINE doses, then Pass-2 review found an implementation
deviation in the far-emission rule and re-emitted the same three doses
with the screened rule (Ltop), superseding but preserving the first
three rasters. Six rasters were therefore written; three are live
experiments and three are retained solely as the deviation's evidence.
No further variants were built.
