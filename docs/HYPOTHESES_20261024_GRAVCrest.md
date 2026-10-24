# Historical hypotheses — 2026-10-24 late session (GRAVCrest screen)

> This page is a historical, pre-build research record. Its projections are not scores and its action language is superseded by the current registry stop. See [HYPOTHESES.md](HYPOTHESES.md) and [REPO_REVIEW_20261024.md](REPO_REVIEW_20261024.md); no current candidate is cleared.

Protocol: 3–5 previously untried geological hypotheses; each names layers,
physical signature, why it should catch a fault missing from the
USGS/INGENIOUS catalogue, and how it differs from everything already built
in this repo (MASS, PRUNE, SNAP, CONCENTRATION, RELIEF, DILATATION, TIPGAP,
STEPOVER, BREAKLINE, VISIBLE-COLLAR). Ranked by expected HOLDOUT-DTI gain
per implementation cost. The top candidate is validated on the shared
spatially-blocked hide-and-recover holdout (`gems57-pooled-hide-v2`)
before any slot recommendation; budget = 3 built experiments.

Band semantics below were read this session from the pinned
`training_features.tif` itself (SHA-256 `4371c82e…`, restored via
`scripts/restore_inputs.py`; 19 bands, EPSG:32611, 3730×3292): Band 4
`geod_2ndinv`, 5 `iso_grav_anom_slope`, 7 `geod_shearrate`, 8
`geod_dilaterate` (signed, 10.3% negative on a decimated read), 10
`deq_n100a15`, 12 `det_elev`, 13 `iso_grav_anom`, 15 `depth_to_base_surf`,
16 `ieq_n100a15`, 17 `cond_surf`, 18 `iso_grav_anom_hg` (**signed**: 49%
negative — the only signed potential-field band), 19 `det_elev_slope`.
No new external data is required for ranks 1–3, so no obtainability claim
is needed; the USGS SGMC control used for screening is already pinned in
`registry/session_manifest.json` (free official source:
https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d).

Design constraint (inherited, re-verified by BREAKLINE): any dots inside
the H19-5 worm skeleton are behavioural near-duplicates of the worm
family. Every lane below therefore emits its new mass **>3 px off the
whole H19-5 skeleton** and >2 px off the catalogue, at the fixed
37,654-dot budget.

## 1. GRAVCrest — signed gravity horizontal-gradient crest (TOP, screened then built)

- **Layers:** Band 18 `iso_grav_anom_hg` (signed horizontal gradient of
  the isostatic gravity anomaly), Band 13 `iso_grav_anom` (orientation
  coherence), Band 5 `iso_grav_anom_slope` (corroborating screen variant).
- **Signature:** `C = pct_rank(|Band18|) × structure-tensor
  coherence(Band13)` — the crest line of the horizontal gravity gradient,
  which sits over a near-vertical density edge (a buried basement fault
  step), restricted to pixels where the gravity field itself is locally
  lineated. Screen also tests `pct_rank(||∇Band18||) × coherence(Band13)`
  and `pct_rank(Band5) × coherence(Band13)`; the screened winner is the
  built surface (pre-registered selection rule in the screen evidence).
- **Why catalogue-missing:** a basin-bounding fault under 50–300 m of
  alluvium has no scarp (invisible to the catalogue's geomorphic mapping
  and to BREAKLINE's DEM detector) and need not juxtapose magnetically
  contrasted units (invisible to the TMI-driven worms), but its basement
  offset is a first-order density edge. USGS horizontal-gradient
  ("maxspot") practice locates exactly these concealed basin edges, and
  the gradient crest for a dipping normal fault sits *basinward* of the
  surface trace — i.e. deliberately off both catalogue and skeleton.
- **Difference from repo:** every prior potential-field use was an
  undirected magnitude (|grad|-style worms inside H19-5, SNAP edges).
  The signed band's crest set, emitted *outside* the skeleton, has never
  been built; BASEMENT-STEP (Band 15/17) was screened out in the
  BREAKLINE session and is a different (inverted-surface) object.
- **Named non-fault mimic:** pluton and caldera margins, basalt-filled
  paleochannels, and purely lithologic density contacts with no
  Quaternary slip all produce identical gravity-gradient crests.
- **Rank 1** — in-stack (zero acquisition cost), textbook concealed-fault
  method, mechanically independent of both prior winning channels
  (terrain scarps, magnetic worms). Falsifier: screened far-set SGMC
  hit-rate at/below the BREAKLINE-L far set, or holdout Δ vs R0 ≤ 0.

## 2. STRAINBREAK — actively dilating coherent scarp-breaks

- **Layers:** BREAKLINE `L` (Bands 19/12) × Band 8 `geod_dilaterate`
  percentile (screen variant: × Band 4 `geod_2ndinv`).
- **Signature:** a linear DEM break-in-slope that is *also* in a
  volumetric-expansion strain cell — a scarp on a structure that is
  currently opening, the Faulds step-over/termination permeability
  setting (~32% + ~25% of Great Basin geothermal systems).
- **Why catalogue-missing:** the catalogue maps Quaternary scarps
  regardless of present-day activity; a young, still-propagating blind
  strand in an extending relay may have a subtle break but high
  dilatation (cf. 2020 M6.5 Monte Cristo Range rupture of largely
  unmapped Candelaria-fault strands — USGS pub 70217872).
- **Difference from repo:** DILATATION re-ranked dots *on* the skeleton
  (a literal duplicate); strain as a multiplier on an independent
  off-skeleton lineament detector has never been tried.
- **Mimic:** alluvial compaction/subsidence bowls and Walker Lane
  elastic strain shadows dilate without a brittle fault.
- **Rank 2** — cheap, but it is a sharpening of BREAKLINE rather than a
  new discovery channel, and its far dots risk >70% 3-px overlap with
  BREAKLINE f45 unless explicitly repelled from that file's far set.

## 3. SEISMIC-PROX — instrumental-seismicity proximity, off-skeleton

- **Layers:** Band 10 `deq_n100a15`, Band 16 `ieq_n100a15`.
- **Signature:** `pct_rank(−log deq) × pct_rank(ieq)` spaced top-set.
- **Why catalogue-missing:** instrumental swarms light up blind faults
  with no Quaternary scarp.
- **Difference from repo:** no prior axis used seismicity at all.
- **Mimic:** induced seismicity (geothermal production, mining).
- **Rank 3 (screen expected to kill it):** the `n100` fields are smoothed
  at ~100 km scale; a 300 m-kernel metric cannot be served by a field
  with no 100 m structure. It is screened only to close the question
  with a number, not built unless the screen contradicts this prior.

## 4. SHORELINE-SUPPRESSED BREAKLINE (unbuilt, held)

- **Layers:** BREAKLINE `L` with Lake Lahontan stillstand-elevation
  suppression (free official compilations via USGS/NBMG; **not yet
  downloaded or coverage-checked in this sandbox**, so per protocol it
  is *not* proposed as viable this session).
- **Rank 4** — attacks BREAKLINE's named mimic directly, but its value
  is only measurable after an organizer receipt prices BREAKLINE's far
  dots. Held, exactly as the BREAKLINE session left it.

## Pre-registered screen → build rule

Screen every rank 1–3 surface the same way (script preserved in
`evidence/gravcrest_screen.json` inputs): (a) leakage-canary symmetric
AUC vs withheld-catalogue positives must be ≤ 0.90; (b) a 16,944-dot
spaced top-set (2.8 px floor, >3 px off H19-5, d_cat > 2 px) is scored
alone on the off-catalogue USGS SGMC control and the fixed-catalogue
diagnostic, against the identical BREAKLINE-L far set as baseline.
Build the best non-baseline surface by SGMC far-set DTI. Then: pooled
HOLDOUT-DTI vs R0, RELIEF p10 (holdout best, duplicate) and BREAKLINE
f45Ltop (best locally-unique); literal uniqueness on the pre-placement
surface AND final dots; 10/10 format gates. **Promote only if** it beats
the holdout-best comparable arm and passes literal uniqueness on every
registry actually scanned — otherwise the verdict is negative and no
slot is recommended. Projections are never written as scores.

## Outcome (appended after the screen/build, same session)

- **Rank 1 GRAVCrest: FALSIFIED at screen, not built.** Far-only SGMC DTI
  0.005259 / 0.016145 / 0.005477 (crestA/B/C) vs BREAKLINE-L baseline
  0.072325 (`evidence/gravcrest_screen.json`).
- **Rank 2 STRAINBREAK: built all 3 budgeted experiments** (f45/f60/f75,
  Band-4 variant per the screen rule, far dots also >3 px off BREAKLINE
  f45's far set). HOLDOUT-DTI 0.005022 / **0.005487** / 0.005486 — dose
  plateau at f60; SGMC 0.10580 / 0.10516 / 0.10327 (below BREAKLINE
  0.12611). Primary f60s2i, verdict **negative** (does not beat holdout
  best RELIEF p10 0.006045). Run card: `evidence/strainbreak_run_card.json`.
- **Rank 3 seismic-proximity: screened out as predicted** (SGMC 0.020558,
  AUC 0.5247). **Rank 4 shoreline-suppression: still held** (needs a
  receipt to price, plus unverified external elevation data).
