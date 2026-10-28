# Pre-registered hypotheses — 2026-10-28 session `2123e2a6` (TIPCOMP lane)

*Historical pre-registration for the 2026-10-28 TIPCOMP session. The session has completed; its verdict is `negative` and `submission_eligible` is `false`. Its TIFF is a research download only. No new experiment is authorized by this historical plan. Every number is labelled `HOLDOUT-DTI` (evaluator `gems57-pooled-hide-v2`, withheld-positive count, 95% CI), `MODEL` (fitted to owner-reported `CLAIM`s), or `CLAIM`; no `ORGANIZER-CONFIRMED` receipt exists in this repo. The stored local PI-1 scan does not establish global uniqueness or submission eligibility. See the [follow-up review](REVIEW_20261028_9649DFC1.md) and [current TIPCOMP status](downloads/tipcomp_readiness_20261028.json).

## Data actually obtainable in this sandbox (verified 2026-10-28)

Outbound access is limited to `github.com` / `api.github.com` / package
registries. The 19-band `training_features.tif` stack used by earlier
`gems/*` physics lanes lives only in a previous session's `.cache/`
(DrivenData login / Dropbox mirrors — **not reachable here**; verified
absent from the GitHub trees of `buffedlizard55-lab/GEMSDOE24`). Therefore
every hypothesis below is computable **only** from byte-verified assets
that exist or were re-fetched and SHA-256-checked in this session:

- `data/bridge/` (committed): `sample_submission.tif` (footprint),
  `existing_faults.tif` (USGS/INGENIOUS catalogue), `h19_5.tif`
  (GEMSDOE19 continuous multiline skeleton, CLAIM 0.1922), `d28.tif`
  (CLAIM 0.2600), `h27_4_solo.tif` (CLAIM 0.2708); `data/parent_R0_zeros.tif`
  (GEMSDOE32 `h33-h33-2-b2`, CLAIM 0.2778).
- `.cache/focus9_20261028b/` (re-fetched this session by sparse git clone,
  SHA-256 matched to `evidence/claims_matched_20261028.json`): the peak
  raster of every focus site GEMSDOE24/25/27/28/30/31/32/33/36, the 10
  LBM-v1 "G-set" rasters, and low/mid CLAIM contrast rasters (21 files).
- This repo's own `docs/downloads/*.tif` (144 unique rasters incl.
  `lbmc1` 2026-10-27 and `rieszlbm2` 2026-10-28) — the local registry.

## The five candidates (ranked by expected DTI gain ÷ implementation cost)

### H-92F1 — TIPCOMP: catalogue tip-continuation × claim-fitted density, coverage-complement boosted ⭐ TOP
- **Layers:** `existing_faults.tif` geometry only (segment endpoints +
  local strike), modulated onto the published LBM-v1 truth-density
  (`evidence/lbm_v1_model.json` β; classes dcat×dh19×cons rebuilt exactly
  from the re-fetched G-set).
- **Physical signature:** for every catalogue endpoint (8-neighbour degree
  1), PCA strike of catalogue pixels in a 15 px window; stamp an axial
  Gaussian ridge (σ_along 8 px, σ_across 1.5 px, length 20 px, suppressed
  ≤2.2 px from the trace). Basin-and-Range normal faults grow by tip
  propagation and linkage; the unmapped continuation beyond a mapped tip
  is the single most likely place for a "new" fault pixel.
- **Why missing from USGS/INGENIOUS:** catalogue traces terminate where
  surface expression is buried by alluvium/playa or leaves the mapped
  quadrangle — the fault continues, the line stops. Organizer labels
  (any real fault pixel absent from the catalogue) therefore cluster in
  tip fans, which no focus-9 peak targets explicitly (all are H19-5
  skeleton surgeries).
- **Coverage-complement term:** boost cells on/near the H19-5 ridge
  (`dh19 ≤ 2 px`) that lie **>3 px from every focus-9 peak dot** — 300 m
  kernel-coverage gaps at strand bends where 2.8 px dotting under-covers
  a curved trace.
- **Named non-fault mimic:** map-sheet/compilation edge truncations and
  road/stream line-ends mis-digitised as fault tips; suppressed because
  the tip field only *modulates* (±35%) a claim-fitted density and dots
  still require LBM support.
- **Difference from repo:** `gems/variants.py:tipgap` *moved* parent dots
  onto tip/gap pixels of one parent skeleton; `gems/relayconduit.py`
  stamps tip *relay* cones as standalone physics channels. Neither (a)
  modulates a leaderboard-fitted density, (b) adds a focus-9
  coverage-complement term, nor (c) places under per-raster 3 px caps
  against lbmc1+rieszlbm2+all focus-9 peaks simultaneously.
- **Expected gain / cost:** +0.01–0.03 MODEL over LBM-v1 placement; low cost.

### H-92F2 — cons9: per-site-deduplicated focus-9 consensus as an LBM stratum
- **Layers:** 9 focus peak rasters. **Signature:** count of *distinct
  sites* whose peak has a dot ≤2 px away. **Why missing-fault:** peaks
  agree where independent surgeries keep a strand — a vote for real
  structure vs single-model artefact. **Mimic:** shared H19-5 ancestry
  makes votes non-independent (all peaks are clones/derivatives — see
  executive summary). **Difference:** LBM-v1 `cons` counts G-set
  (off-H19) rasters, not the focus-9 peaks themselves. Expected gain
  small (+0.00–0.01); used as a robustness spec, not the primary.

### H-92F3 — Far-field reallocation under the fitted dcat law
- **Layers:** catalogue distance only. **Signature:** LBM-v1 β implies
  truth density ×0.38 at 200 m–1.5 km vs ×5.65 beyond 1.5 km; spend the
  dots saved by the 200 m collar preferentially at `dcat>15 px`.
  **Mimic:** none (pure allocation). Already embedded in LBM placement;
  listed because it is the largest single fitted effect and constrains
  H-92F1's tip field (tips near traces must not re-fill the dead collar).

### H-92F4 — Bend-density re-dotting of the H19-5 skeleton
- **Layers:** `h19_5.tif` skeleton curvature. **Signature:** local
  skeleton direction-change rate; dot spacing ∝ 1/curvature so kernel
  coverage per strand-metre is constant. **Why:** fixed 2.8 px spacing
  over-covers straight strands (wasted FP) and under-covers bends
  (lost TP). **Mimic:** skeletonisation spurs at junctions. Subsumed by
  H-92F1's complement term in this session (same gaps, cheaper test).

### H-92F5 — 1 m USGS 3DEP LiDAR scarp breaklines — **DEFERRED, not viable here**
- **Specific free official source:** USGS 3D Elevation Program 1 m DEMs
  via The National Map (`https://data.usgs.gov/datacatalog/data/USGS:77ae0551-c61e-4979-aedd-d797abdcde0e`),
  tiles on `prd-tnm.s3.amazonaws.com`. **Obtainability check:** that host
  is outside this sandbox's allow-list, so the idea **cannot be validated
  this session** and is not proposed as viable. It remains the only
  identified route from ~0.32 toward the reported 0.4413 ceiling
  (sub-100 m scarp localisation).

## Experiment plan (exactly 3)

- **E1 — Canaries + static controls.** Single-feature AUC (pooled
  withheld positives) for: tip field (fold-visible), dvis, catalogue
  Gaussian corridors, rebuilt LBM-v1 ρ, cons9. Hard stop if any
  symmetric AUC > 0.90 (leakage). Static re-scores (labelled static, not
  fold-proper) of R0, D2.8, G24-D1.5, lbmc1, rieszlbm2 on the same folds.
- **E2 — Fold-proper TIPCOMP-geometry.** Per seed (20, 30): tip +
  continuation fields from `fold["visible"]` only; NMS-2.8 dots at the
  R0-recipe budget; pooled HOLDOUT-DTI vs R0-recipe control, paired CI.
- **E3 — Full-data candidate.** ρ = LBM-v1 (rebuilt, verified against
  CLAIMs) × tip modulation × complement boost; `gems/lbm_place.place`
  with 3 px caps ≤0.65 vs R0, lbmc1, rieszlbm2 and each focus-9 peak;
  surface + final uniqueness vs the full local registry; MODEL estimate
  (published-β spec + in-session grouped refit/bootstrap); static
  holdout re-score; writer `vendor/gems57/grid.write_submission`
  (zeros mode); 11-gate validation. **Promote only if** format PASS,
  PI-1 overlap ≤0.70 and |rho| ≤0.90 vs every registry raster checked,
  and MODEL bootstrap q05 > 0.2778. Otherwise verdict `negative`
  (a deliverable, no slot spent by this session either way — promotion
  to a weekly slot is the owner's separate selector step).
