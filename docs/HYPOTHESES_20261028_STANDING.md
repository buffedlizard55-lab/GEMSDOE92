# Untried geological hypotheses — standing brief, 2026-10-28

Status: **pre-registered, none validated.** No holdout run, no submission slot used. Every source below was checked against `docs/HYPOTHESES_UNTRYED.md`, `docs/HYPOTHESES.md` and the lane analyses (`docs/ANALYSIS_*.md`) before being listed.

## Novelty check (what the repo already covers)

| Candidate | Repo status | Evidence |
|---|---|---|
| Magnetic-source-depth discontinuity (GeoDAWN) | **Rejected — duplicate.** Euler-deconvolution source depth is the EULERFUSE lane. RELAYCONDUIT only names the signature. | `docs/ANALYSIS_20261024_EULERFUSE.md`; `docs/HYPOTHESES_20261025_RELAYCONDUIT.md` |
| Lineament density | **Rejected — covered.** Lineament work in ALI and FAULTNET lanes. | `docs/ALI_LANE.md`; `docs/ANALYSIS_20261025_FAULTNET.md` |
| Groundwater-head offset across a line (USGS NWIS) | **Untried as a head-offset lane.** Repo has groundwater *thermal/Péclet* and playa-groundwater residuals only. | `docs/HYPOTHESES_20261024_APRONRIDGE.md` (Péclet), `docs/ANALYSIS_20261025_POISSONFLEX.md` |
| Strain-gated lineament orientation (geodetic strain) | **Untried.** COULOMB notes state no lane gates lineament orientation by geodetic strain style. | `docs/ANALYSIS_20261025_*` COULOMB section |

## Ranked candidates (expected DTI gain vs cost)

### H-A (rank 1) — Groundwater-head offset across concealed structures
- **Layers:** USGS NWIS groundwater levels (static water level, depth-to-water) for wells in and around the footprint; footprint = EPSG:32611 bbox (approx. lon −120.04 to −116.18, lat 37.36 to 40.69).
- **Physical signature:** a head discontinuity of several metres across a line, where the gradient is not explained by topography. Compartmentalising fault zones act as hydraulic barriers, so a step in head across a line with no surface scarp is a candidate blind fault.
- **Why it catches missed faults:** the USGS Quaternary database and INGENIOUS lanes depend on surface or geophysical expression. A hydraulic barrier can exist without a mapped scarp or magnetic signature.
- **Difference from repo:** a fluid-pressure channel. Existing groundwater lanes use thermal or playa residuals, not head offsets.
- **Cost:** medium. Pull wells, interpolate heads with a stated variogram, and derive the offset-step field.
- **Data obtainability:** free official source (USGS NWIS, `waterservices.usgs.gov`). **NOT obtainable from this sandbox** — the host returns no response (tested this session). It must be pulled from a machine with internet access before validation. **BLOCKED here.**
- **Validation plan:** gems57 pooled hide-and-recover, DTI alpha 0.2 / beta 0.8, 300 m triangular kernel; canary AUC ≤ 0.90; compare to R0 0.09775 and TIPCOMP E2 0.09617.

### H-B (rank 2) — Strain-gated lineament orientation
- **Layers:** mapped lineaments (existing ALI/catalogue lineament traces) plus a geodetic strain-rate field from GPS velocities (EarthScope/UNAVCO free GNSS velocity products — access not tested here; likely blocked by the same allowlist).
- **Physical signature:** faults that are kinematically compatible with the local principal extension direction, so lineaments parallel to the extension axis get a higher prior.
- **Why it catches missed faults:** it uses orientation and kinematics rather than presence of a scarp or anomaly.
- **Difference from repo:** orientation gated by geodetic strain has not been used (COULOMB uses modelled stress from visible faults only).
- **Cost:** medium-high. Needs a velocity field, strain inversion and orientation statistics.
- **Data obtainability:** not tested; **UNVERIFIED**.

### H-C (rejected) — Magnetic-source-depth discontinuity
Duplicate of EULERFUSE; listed only so the novelty check is transparent. Not ranked.

### H-D (rejected) — Lineament density
Covered by ALI and FAULTNET. Not ranked.

## Ranking rationale
Expected DTI gain cannot be estimated without data, so this ranking uses novelty and cost. H-A is first because its physical channel (fluid pressure) is independent of every existing lane. H-B is second because its data access is unverified.

## Validation status
- Top candidate H-A: **not validated.** Data blocked in this environment; no holdout run; no slot used.
- Gate that any candidate must clear before a slot is considered: a PI-1 pass on the full registry **and** a HOLDOUT-DTI above the holdout best.
