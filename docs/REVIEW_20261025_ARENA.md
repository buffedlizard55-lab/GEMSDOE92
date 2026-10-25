# Repository review — 2026-10-25

## Executive outcome

**Research-downloadable artifacts exist; no submission-cleared TIFF exists. Do not submit or spend a weekly slot.** This review did not generate a new raster. The binding literal registry gate and the pinned dense witness make any nonempty prediction fail before placement: the witness has positive support in every sample-footprint pixel, so every in-footprint dot is within 3 px of that witness. A format-valid raster is not an eligible competition submission.

A concurrent main-branch update during PR preparation added a LISTRICDIP research lane. Its artifact is now the site primary but remains negative and blocked by the same literal witness rule. This review did not generate that raster. The repo review also found a publication-level inconsistency: `docs/index.html` opened with a historical KNICKLOQO banner that called its outputs “unique” under matched-budget / dual-reading, while the later binding review explicitly says matched-budget overlap is diagnostic only and literal overlap is the gate. The current-protocol warning appeared much farther down the page. `docs/REVIEW_CURRENT.md` also began with the stale KNICKLOQO assessment. These have now been brought into alignment: the homepage and README open with the no-submit decision; the old banner is clearly historical and no longer calls dual-reading clearance current uniqueness.

## Multi-pass review

### Pass 1 — inspect the project contract and evidence

- Read `README.md`, `SESSION_PROMPT.md`, `docs/REVIEW_376A8469.md`, the site, submission instructions, and current machine-readable run card.
- Confirmed the project has an auditable single-band GeoTIFF submission path and a strict local validator. The current canonical primary is the existing COULOMBDM research TIFF; its local format status does not override the registry stop.
- Confirmed the repository's dense-witness preflight records a single pinned witness, not an exhaustive all-sites uniqueness guarantee. It should be described as a rejection proof, not as comprehensive registry clearance.
- The user-reported GEMSDOE32 `0.2778` and supplied leaderboard snapshots `0.3195` / `0.4413` are not organizer receipts in this checkout. No claim that this repo beats those values is warranted.

### Pass 2 — check bugs, claims, and user-facing risks

- Discovered that top-of-page language exposed a stale dual-reading uniqueness result before the binding literal stop, risking accidental upload.
- Checked raster links, audit metadata, local manifests, pinned parent, and ledger. The served-TIFF audit script verifies each file's finite `[0,1]` values, zeros outside footprint, grid, catalogue exclusion and expected dot count.
- No feature stack was restored for a new method, no new holdout was run, and no official data/competition portal was accessed during this review. Therefore no new score, official validation, upload receipt, or source availability claim is made.
- A format-validation result is not an organizer acceptance. A better local surrogate DTI is not a competition score.

### Pass 3 — changes and recheck

- Put a prominent authoritative submission decision at the top of the GitHub Pages home page, linked to the existing validated research TIFF, current review, run card, and submission guide.
- Clarified the README executive summary and reordered `docs/REVIEW_CURRENT.md` so historical “unique” wording cannot be mistaken for current clearance.
- Added regression assertions that the current stop appears before historical method banners and the README opens with the no-submit status.
- No scientific method, raster, submission slot, shared evaluator, or upstream template code was changed.

## Ranked conditional research hypotheses (not implemented)

The exact operators below were ranked in `docs/REVIEW_376A8469.md` relative to the inspected local methods. Expected DTI gain is unknown. None can proceed to placement while the binding pre-placement stop remains active. The feature cache is not staged in this checkout; no claim of currently obtainable layers is made. Before a future test, verify the required layer bytes, provenance, and use rights from the competition data source.

| Rank | Candidate | Layer and target signature | Rationale for catalogue-missing faults | Difference from implemented methods | Cost / confounder |
|---|---|---|---|---|---|
| 1 | Offset magnetic-texture registration | Band 2 RTP magnetic field; bidirectional local window registration for a consistent along-strike step in magnetic-texture displacement | A buried splay could offset pre-existing magnetic fabric without preserving a surface scarp | Tests kinematic texture restoration, not magnetic amplitude, tilt, Hessian ridges, Euler depth, or phase winding | High; intrusive contacts or distinct lava flows can mimic displacement |
| 2 | Persistent magnetic topology | Band 2 RTP; persistent component/hole-count changes over locally standardized level sets across trial lines | Offset contacts may fragment magnetic domains even where field amplitude is weak | Topological persistence rather than derivative-ridge or Euler-source-depth measures | Medium; remanent domains and survey seams; require seam controls and amplitude-matched nulls |
| 3 | Basin-divide migration residual | Band 12 DEM; paired basin hypsometry and opposite-side channel steepness / divide residual conditioned on local relief | Distributed deformation may shift divides where erosion has erased a sharp scarp | Basin-integrated geomorphic imbalance, not local scarp, knickpoint, shoreline-subtraction, or channel-alignment scores | High; lithologic erodibility, capture, and precipitation gradients can mimic it |

No candidate is declared viable just because a data product is named. The competition's authenticated data page is the appropriate source for the existing stack; access and license/redistribution terms must be verified before use. Official manual-review references are linked below. Existing repository reviews contain prior pinned-source audits, but this review did not freshly retrieve non-GitHub pages.

## Source links for manual review

- [DrivenData problem statement](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Competition rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [GDR / INGENIOUS](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)

## Checks run in this environment

Using dependencies installed in the repository-local ignored `.venv`:

- `python -m pytest -q`: **367 passed**.
- `python scripts/check_site.py`: **PASS**, 63 served TIFFs gated; primary identified and its byte-matched audit/run card checked.
- `python -m gems manifest --manifest registry/data_manifest.json --data-root data`: **PASS**.
- `python -m gems parent --recipe registry/parents/R0.json --data-root data`: **PASS**, pinned parent `h33-h33-2-b2` verified.
- `python -m gems ledger`: **PASS**, 93 entries; no organizer receipt recorded.
- The test output includes 126 Rasterio pending-deprecation warnings. They did not fail tests, but should be addressed during a deliberate dependency/API update rather than an untested change here.

## Remaining work / limitations

1. Get an explicit operator/specification decision about the binding literal overlap rule versus the full-footprint witness. Do not silently substitute matched-budget overlap.
2. Obtain and document authorized access to the official competition feature stack if a future lane is permitted; confirm exact inputs and checksums.
3. Maintain a locked outer spatial test to reduce adaptive holdout selection bias, then use the shared evaluator and leakage canaries for any future candidate.
4. Do not select or upload any existing raster based on local HOLDOUT-DTI alone. The weekly selector and actual organizer receipt remain separate human/portal steps.
5. The reported GEMSDOE32 score and leaderboard numbers remain unverified claims here. A current official leaderboard or submission receipt was not accessible in this review.
