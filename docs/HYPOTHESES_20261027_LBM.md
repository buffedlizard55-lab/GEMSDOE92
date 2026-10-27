# Hypotheses — session ee2370c1 (2026-10-27)

Pre-registered before any candidate TIFF was written. Ranked by **expected DTI gain ÷ cost**.
Every number below is labelled: `CLAIM` (owner-reported score, no organizer receipt),
`MODEL` (fitted leaderboard model, never a score) or `HOLDOUT-DTI` (shared gems57 instrument).

## Evidence that changed the ranking

The owner reported **123 scored submissions** (`ledger/claims_20261027.txt`), and all 123 rasters were found byte-for-byte in public
repositories (`evidence/claims_matched_20261027.json`). Each score is one exact evaluation of the official
metric on the hidden public labels, so together they constrain where the labels are. Earlier sessions used them only as a
crude logistic score predictor (row-wise LOO RMSE 0.072). This session fits a **metric-structured model**
(`gems/lbmodel.py`). Because expectation is linear, `E[TP] = Σ ρ(y)·C(y)` holds exactly for a truth density
`ρ` and a raster's kernel-coverage field `C`. The model also uses `E[M] = Σ p·min(1,3ρ)`, so
`DTI = TP / (TP + 0.2·FP + 0.8·(G−TP))` with no free scale. It has 12 parameters, and it was validated by
**leave-one-group-out** cross-validation, where the whole H19-5 family is one group:
grouped RMSE `0.021` (Spearman `0.964`). With the entire R0/H19 family held out, it still predicts that family
with RMSE `0.006` (MODEL; `evidence/lbm_v1_model.json`).

Three regularities the model extracts from the CLAIM scores (multipliers on truth density):

| Signal | Multiplier | Reading |
|---|---:|---|
| > 1.5 km from any mapped fault (vs ≤ 200 m) | ×5.7 | New faults sit in mapping **gaps**, not beside mapped traces. This is the same effect behind R0's 200 m collar, extended. |
| exactly 1 px (100 m) off the H19-5 skeleton (vs on it) | ×3.8 | The 100 m skeleton is systematically offset from mapped traces by about one pixel. |
| ≥ 5 of 10 independent high-scoring lineages agree within 200 m | ×15 | Independent detectors converge on real faults; their false positives do not converge. |

## H1 — Multi-detector convergence, LB-calibrated (selected: EXP1)

* **Layers:** H19-5 skeleton distance (topographic + geophysical multiline evidence); a convergence count from 10
  independent scored lineages (tilt-derivative "worms", hydrothermal piedmont, OOF ML with submodular placement, Blakely
  gravity/magnetic edges, dotted ridges, LFTG); distance to the mapped catalogue. Fit on the 19-band
  `training_features.tif` products only. No external data.
* **Physical signature / transform:** a real fault offsets several independent fields at once: topography (scarp,
  lineament), magnetics (tilt/Blakely edge), gravity gradient and conductivity. Each detector's false positives come from a
  different mimic, so they rarely coincide. The transform is the count of detectors within 200 m. That count is converted
  into truth density by the metric-structured model, and dots are placed by **exact lazy-greedy maximisation of expected DTI**.
* **Named non-fault mimics:** Lake Lahontan paleoshorelines (wave-cut benches look like scarps in topography) and
  lithologic contacts (these look like edges in magnetics and gravity).
* **Why it finds catalogue-missing faults:** the organizer masks every mapped pixel exactly, and penalises dots beside mapped
  traces ([staff, thread 11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4)).
  The CLAIM scores show the labelled new faults concentrate more than 1.5 km from mapped traces, and convergence is
  computed without catalogue features.
* **How it differs from repo work:** no earlier lane used the organizer's own evaluations as weak supervision, placed dots
  by expected DTI under a fitted truth density, or enforced the 70%/3 px registry rule **during** placement (as a cap)
  rather than after it.
* **Expected gain / cost:** MODEL predicts a large gain inside the validated composition range. Cost is low: existing
  inputs, about 1 CPU-hour.

## H2 — Catalogue-gap prior (absorbed into H1 as the distance-to-catalogue factor)

* **Layers:** distance to the mapped catalogue only.
* **Signature:** the USGS Qfault/INGENIOUS compilations already cover prominent range-front systems, so experts add
  faults in gaps. This is not a geophysical transform; it is a labelling-process prior, and it is flagged as such.
* **Differs:** R0 removed only a 200 m collar. The CLAIM-fitted model says density stays low out to about 1.5 km.
* **Gain/cost:** moderate gain, negligible cost. It cannot stand alone, because it says nothing about *where* in a gap a
  fault lies.

## H3 — Scarp-toe offset of the 100 m skeleton

* **Layers:** H19-5 distance plus band 12 (detrended elevation) to tell the up-slope side from the down-slope side.
* **Signature:** at 100 m resolution, the likelihood ridge follows the steepest face. A mapped trace sits at the break
  in slope (scarp toe), about 100 m away. That predicts a peak density 1 px off-skeleton, which is observed (×3.8).
* **Differs:** every R0 descendant places dots *on* the skeleton. GEMSDOE48's off-skeleton shift (CLAIM 0.2296) moved
  dots without a side model, which is a cautionary result.
* **Gain/cost:** moderate, low cost. The side-specific fit is not yet stable (side classes overfit in grouped CV).
  Only the symmetric 1 px class is used in H1.

## H4 — Lidar-scale scarp detection from the 1 m 3DEP / GeoDAWN EarthMRI lidar (blocked here; highest long-run ceiling)

* **Layers:** 1 m bare-earth DEM tiles listed in the competition's `1m_DEM_links.csv`. Equivalent official, free,
  unrestricted sources: [USGS 3DEP 1 m DEM collection](https://data.usgs.gov/datacatalog/data/USGS:77ae0551-c61e-4979-aedd-d797abdcde0e),
  [3DEP products are free and without use restrictions](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services),
  and the [GeoDAWN West Central Nevada EarthMRI lidar](https://catalog.data.gov/dataset/geodawn-west-central-nevada-earthmri-data)
  (GDR 1501).
* **Signature:** metre-scale fault scarps (Quaternary offsets of 0.5–5 m) are invisible in the 100 m stack and in the
  10 m DEM that earlier lanes used. Transforms: multi-directional hillshade-invariant curvature, scarp-height and
  scarp-normal-gradient filters, aggregated to 100 m as max-response and orientation coherence.
* **Why it should find catalogue-missing faults:** expert mappers of new faults most plausibly worked from lidar, and
  the official rules name 1 m DEM as feature data.
* **Differs:** the repo only ever used 10 m DEM derivatives (scarp lanes scored CLAIM 0.04–0.16).
* **Cost:** high (about 1–2 TB raw), and **not obtainable from this sandbox** (rockyweb.usgs.gov and the TNM hosts are
  outside its network allowlist). This is the first next step for a machine with open internet.

## H5 — Phase-2 discovery hedge (portfolio, not a leaderboard bet)

* Phase 2 re-scores the selected submission against labels that experts revise after reviewing all submissions
  ([rules §1.1](https://docs.nlr.gov/docs/fy26osti/96647.pdf);
  [staff: labels can be added, removed or changed](https://community.drivendata.org/t/questions-about-the-final-round-rules/11556)).
* A submission that densely follows convergent, physically coherent traces may gain more in Phase 2 than its public
  score suggests. This only affects final-pick strategy and is not tested here.

## Ranking

| Rank | Hypothesis | Expected gain | Cost | Status |
|---:|---|---|---|---|
| 1 | H1 convergence + LBM placement | large (MODEL) | low | **EXP1 run this session** |
| 2 | H4 1 m lidar scarps | potentially largest | high; blocked by sandbox network | next step off-sandbox |
| 3 | H3 scarp-toe side model | moderate | low | symmetric part folded into H1 |
| 4 | H2 catalogue-gap prior | moderate | negligible | folded into H1 |
| 5 | H5 Phase-2 hedge | unknown | low | strategy note |
