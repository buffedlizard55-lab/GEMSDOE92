# Candidate hypotheses — 2026-10-24

Evidence labels in this page are deliberate: local results are **HOLDOUT-DTI**, reported competition values without a receipt are **CLAIM**, and forecasts are never scores.

| Rank | Candidate and layers | Physical signature | Why it may find uncatalogued faults | Difference from this repository | Expected DTI improvement | Cost |
|---:|---|---|---|---|---|---|
| 1 | Piedmont relief reallocation: `det_elev` (band 12), H19-5 support, TMI/gravity/scarp prior | Intermediate detrended relief plus coincident potential-field and slope-break response | Active range-front traces may cross piedmont/alluvium while catalogues and map controls favor exposed range-interior structures | Existing RELIEF implementation is the first controlled terrain-position reallocation; earlier PRUNE/MASS/SNAP changed collar, count, or local position | **MODEL**, not score: +0.005 to +0.008 | Low |
| 2 | Analytic-signal ridge persistence: TMI (bands 1–3) and gravity anomaly/slope (bands 5, 13) | Multiscale maxima of orientation-invariant analytic-signal amplitude | Buried structures can produce coincident magnetic and density boundaries without mapped surface expression | Repo uses percentile edge mixtures, not multiscale ridge persistence | **MODEL**, not score: unknown positive | Medium |
| 3 | Radiometric alteration boundary: pinned USGS radiometrics plus topographic wetness/drainage proxies | K/U/Th ratio gradients intersecting structural permeability corridors | Hydrothermal alteration may reveal permeable fault damage zones whose central trace is absent from catalogues | Repo pins radiometrics but has no ratio-boundary/structural-intersection candidate | **MODEL**, not score: unknown | Medium |
| 4 | Concealed basin-depth hinge: gravity anomaly curvature (band 13) plus detrended elevation | Second derivative/curvature hinge under low relief | Basin-bounding and intrabasin faults can be concealed by alluvium and omitted from surface catalogues | Repo uses first-gradient ranks and terrain terciles, not gravity curvature conditioned on basin position | **MODEL**, not score: unknown | Medium |
| 5 | Spring-line discontinuity: pinned GDR well/spring points plus gravity/TMI lineament orientation | Anisotropic KDE ridge and abrupt along-strike density change | Discharge alignment may mark permeable blind faults, while catalogue traces need not host modern flow | Repo uses the GDR layer only for corroboration; it has no leakage-safe, fold-derived spring-line feature | **MODEL**, not score: unknown | High |

## Validation decision

Only rank 1 was executed, respecting the three-experiment budget (`p10`, `p12`, `p15`). The best arm was `p10`: **HOLDOUT-DTI** `0.006045` (evaluator `gems57-pooled-hide-v2`; 22,663 withheld positives; spatial-cluster bootstrap 95% CI `[0.005187, 0.006927]`) versus R0 `0.004006` (`[0.003424, 0.004690]`). Single-feature canary maximum symmetric AUC was `0.55314`, below the `0.90` leakage stop.

The lane uniqueness gate then failed: `99.3812%` of candidate dots are within 3 pixels of R0, above the `70%` stop. Therefore the result is a **negative deliverable** and must not consume a competition slot. See `evidence/run_card_20261024.json`.

## Source/provenance boundaries

* Competition rules/problem and organizer metric links are recorded in the repository README and manifests.
* USGS GeoDAWN source: <https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7>.
* GDR/INGENIOUS source: <https://gdr.openei.org/submissions/1391>.
* The sandbox could not independently retrieve those non-GitHub pages. Input bytes came from commit-pinned owner mirrors and passed SHA-256 verification; this is mirror integrity, **not organizer authentication**.
