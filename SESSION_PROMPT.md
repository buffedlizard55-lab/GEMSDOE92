# Session prompt — GEMSDOE92

Read this at the start of every session, together with `README.md`. The README is the short executive summary; this file is the durable project operating contract. Preserve the user's goals: a unique, easy-to-download submission GeoTIFF, automated format validation, transparent evidence, and no hallucinated claims.

## Mission

Produce a **unique** GeoTIFF for DrivenData competition 306 (DOE GEMS Prize: hidden geothermal-related faults, NW Great Basin, EPSG:32611 100 m). The file must be obviously downloadable from the GitHub Pages site. Inspection and validation run in the project, without a human inspector in the loop. A human still performs the DrivenData upload and weekly-slot selection.

Study the prompt-reported GEMSDOE32 `h33-h33-2-b2` **CLAIM 0.2778** and other site values as learning context only. They are not ORGANIZER-CONFIRMED receipts unless a submission-page receipt is recorded in `ledger/`. A prior repository record says the official public leaderboard was read on 2026-10-24 and showed 0.4413 at #1 (LEADERBOARD-SNAPSHOT, not a receipt for GEMSDOE32 or GEMSDOE92); the prompt's 0.3195 is an older conflicting snapshot. Never say a local holdout beats a live competition score.

The goal is maximize the probability of placing well through reproducible science: collect public/official data where permitted, organize source and provenance, generate hypotheses, test using spatial holdouts, preserve negative results, and make an audited TIF easy to download. Keep Arena's core values explicit: **Maximize P(Win)** and **Own the Outcome**.

## Parallel-run protocol

1. **Lane.** Stay in one named method. Before placement, compare the prospectivity surface with the accessible registry; after placement, compare final dots. If absolute Spearman rank correlation exceeds 0.90 or more than 70% of dots fall within 3 px of one registry raster's dots, log it as a duplicate and stop. Never reinterpret the threshold to make a result pass. Report local inventory scope; local uniqueness is not proof of uniqueness across every site.
2. **Reuse.** Use the template's cached feature stack when it is actually available, `vendor/gems57/evaluate_holdout.py`, and `vendor/gems57/submission_writer.py` or the shared writer. Holdout = hide whole fault segments/components with a buffer; derive all catalogue-based features from visible faults only; mask visible faults pixel-exactly; pooled DTI α=0.2, β=0.8, 300 m triangular kernel. Fix a shared tool once in the template, never create a private fork.
3. **Label every number** as HOLDOUT-DTI (evaluator version, withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from submission-page receipt). CLAIM, MODEL, PROXY, and REGISTRY-MEASUREMENT must remain distinct. A projection is never written as a score.
4. **Leakage canary.** Test each feature alone on the holdout before trusting a result. AUC above 0.90 means leakage until investigated. Use the symmetric AUC if direction could reverse.
5. **Run card JSON:** hypothesis; mechanism; named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster SHA-256; validator output (no NaN inside footprint, values in [0,1], CRS/shape/transform match); submission name + note ≤140 characters; verdict promote / negative. Negative results are deliverables.
6. **Budget.** Stop after 3 experiments or 2 hours. Do not pick submissions; promotion to a real slot is a separate selector step within the weekly cap.
7. **Hypothesis request.** Before implementing, rank 3–5 candidate geological hypotheses; for each identify layers, physical signature, why it could detect a fault absent from the catalogue, difference from this repo, expected value/cost, and required data. If new data are needed, name a free official source and verify availability before calling the candidate viable. Do not claim a source was retrieved if it was not.

## Site / download rules

- Zeros-outside encoding is the only submission download offered (portal error: `Predicted values must be in range [0, 1]`).
- Homepage must clearly say whether the file is OK to download **and** whether it is recommended for a weekly slot.
- Executive summary subpage explains the DrivenData form (file, name, note).
- No human inspection is needed for format validation (`scripts/check_site.py`, `gems.gates`, `gems57.validate`). Human upload and selector remain separate.
- Never silently change `nodata`, clip out-of-range values, or convert NaNs without a recorded rationale.

## Trusted source starting points

- Competition overview/problem: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Competition about: https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- Competition data: https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- DrivenData reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Competition rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- USGS GeoDAWN catalog: https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7
- GDR / INGENIOUS: https://gdr.openei.org/submissions/1391
- EPSG:32611: https://epsg.io/32611
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- Great Basin Center for Geothermal Energy: https://gbcge.org/current-projects/ingenious/
- USGS 3DEP: https://www.usgs.gov/3d-elevation-program

Competition data may be login-gated. Follow license and data-use terms; owner-mirror hash checks establish byte identity, not organizer authentication or redistribution permission.

## Current session result (2026-10-24)

One candidate method was tested: R0-excluded visible-fault collar. Builder: `scripts/build_visible_collar_submission.py`. It generated `docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif` and its run card is `evidence/visible_collar_run_card.json`.

- **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 8 buffered spatial folds, 22,663 withheld positives: candidate 0.046866 (95% CI 0.040216–0.053315); parent R0 0.004006 (0.003424–0.004690); paired difference +0.042860 (0.036122–0.049357). These are local holdout values, not competition scores.
- **Leakage canary:** visible-fault distance alone, symmetric AUC 0.745593 (<0.90).
- **REGISTRY-MEASUREMENT:** the initial local-only comparison passed on 14 rasters, but the expanded literal scan found 1,279 matching-grid rasters across 102 public owner repositories. Pre-placement and final overlap both reach 1.000000; 131 rasters exceed 70%. Worst |ρ| is 0.421367 / 0.492957, below the 0.90 stop, but overlap triggers the binding duplicate rule. The initial inventory came from GitHub API; the final comparison was repeated from SHA-verified cache after API rate limiting (no fresh API refresh). See `evidence/public_registry_uniqueness.json`.
- **Validator:** 10/10 local MUST gates pass; all finite, range [0,1], zero outside; EPSG:32611, 3730×3292, template transform.
- Verdict: **negative — duplicate under the literal registry rule; stop and do not submit**. No weekly slot was selected or used. The local result may reward recovery of mapped catalogue structure and does not prove discovery of new faults.
- The GeoDAWN training stack is not present in this checkout's local cache. The band-based hypotheses in `docs/hypotheses_visible_collar_20261024.md` remain untested.

The earlier TIPGAP FAR result (2026-10-24) is a separate negative deliverable; preserve it and its evidence. Do not overwrite historical evidence or mistake it for this session's primary.

## Addendum — parallel BREAKLINE session (2026-10-24, merged after the collar session)

A second session ran in parallel from the same base and DID restore the feature stack (`python scripts/restore_inputs.py`; the brief's `download_competition_data.sh`/`prepare_data.py` do not exist in this checkout). It tested the band-based lane **BREAKLINE** (Bands 12/19 DEM scarp-break coherence; `gems/breakline.py`, builder `scripts/build_breakline_variants.py`):

- Primary file `h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif` (sha256 `cd9c8a56…810e`), verdict **negative / NOT CLEARED**: HOLDOUT-DTI 0.004861 [0.004032, 0.005822], Δ vs R0 +0.000854 [+0.000300, +0.001423]; SGMC off-catalogue control +31% vs R0; canary max 0.6216.
- **Local-registry uniqueness:** worst 55.0% forward / |ρ| 0.547 vs parent R0 over 18 local rasters; vs the visible-collar candidate only 3.5% (φ≈0.001) — disjoint lanes. **It has NOT been through the 1,279-raster public scan** — run `scripts/audit_public_registry.py` on it before any future uniqueness claim beyond "local".
- Facts: R0 ⊂ SOLO ⊂ D2.8 ⊂ H19-5 exactly; bridge `sample_submission.tif` *is* the catalogue (60,988 px, geometry only); Band 18 is the only signed band; collar count 2,171 (float64 EDT). Emission: spaced top-L beat exact-DTI greedy by +0.000701 [+0.000321, +0.001161] — never deviate at build time from the screened selector. Do not retry BASEMENT-STEP (Band 15, SGMC AUC 0.378), pure-seismicity placement, radiometric K/Th gradients.
- One BREAKLINE dose total may ever be submitted (siblings share keeps; 3 SUPERSEDED greedy siblings in `ledger/`). Full record: `docs/ANALYSIS_20261024.md`, `docs/HYPOTHESES_20261024_BREAKLINE.md`, `evidence/breakline_run_card.json`. Ledger: 36 BUILT / 0 RECEIPT.

## Addendum — SCARPDIPOLE session (2026-10-24)

1. **Completed prior-session action items first:**
   - Ran the full 1,300-raster public-registry scan (`102` repos) on `BREAKLINE f45Ltop` (`evidence/breakline_public_registry_uniqueness.json`): `122` rasters exceed `70%` overlap (`68` `>=70%`-halo surfaces + `54` `<70%`-halo rasters up to `0.9130` vs `GEMSDOE3/coverage-v3-wide`), `verdict: negative`.
   - Measured off-catalogue `USGS SGMC` bedrock-fault DTI (`n = 62,703`) on `visible-collar-r0-excluded`: **`0.021192` (`-77.94%` vs `R0 = 0.096060`)**, and uncovered a repo-wide masking confound in prior `visible-collar` reporting (`0.046866` fold-fair `d_visible > 2` was compared against static pre-punched `R0 = 0.004006` instead of fold-fair `parent_B2_visible = 0.029074`).
   - Repaired trailing-comma JSON syntax error in `evidence/public_registry_uniqueness.json` and `docs/downloads/public_registry_uniqueness.json`.
2. **Screened 5 untried geological hypotheses (`docs/HYPOTHESES_20261024_SCARPDIPOLE.md`) and implemented `SCARPDIPOLE` (`gems/scarpdipole.py`, `scripts/build_scarpdipole_variants.py`, `scripts/report_scarpdipole_proxies.py`):**
   - Built 3 doses (`f42dipole` primary, `f45dipole`, `f50dipole`) via shared `vendor/gems57/submission_writer.py`.
   - Primary `h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-zeros.tif` (`sha256: 9febfbd7e301d708b0f60df08dc4add6bd5bd442909ea653bcd2a83a92d36262`):
     - **Fold-Fair `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `n = 22,663`):** **`0.098565 [0.087985, 0.108974]`** (`#1` in `GEMSDOE92`; paired Δ vs `parent_B2_visible` `+0.069492 [+0.060008, +0.077790]`, `3.39×`; paired Δ vs `visible_collar` `+0.051699 [+0.037872, +0.064896]`, `2.10×`).
     - **Static `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `n = 22,663`):** **`0.006812 [0.005770, 0.008034]`** (`#1` in `GEMSDOE92`; paired Δ vs `R0` `+0.002806 [+0.001946, +0.003686]`).
     - **Off-Catalogue `USGS SGMC` (`PROXY`, `n = 62,703`):** **`0.107841`** (`+12.26%` vs `R0`).
     - **Leakage Canary:** max raw band `0.5531`, `S_pct` `0.6328` (`<= 0.90` PASS).
     - **Uniqueness (`REGISTRY-MEASUREMENT`):** `0 / 20` local overlaps `> 70%` (`max = 0.6605`); **`0 / 1,004` overlaps `> 70%` across ALL sparse dotted public submissions (`<= 60,000` dots) in all `102` public GEMSDOE repos** (`max = 0.6877` for `f42dipole`, `0.6657` for `f45dipole`, `0.6348` for `f50dipole`); global `max |ρ| = 0.3152 << 0.90`.
     - **Binding Literal All-Rasters Verdict:** **`negative` / NOT CLEARED FOR LIVE WEEKLY SLOT** without human selector waiver because `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` has positive support on `100.0%` (`5,167,373 / 5,167,373`) of footprint pixels (`saturation_certificate`). Ledger: 39 BUILT / 0 RECEIPT.

