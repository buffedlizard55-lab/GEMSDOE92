# Stored competition prompt (verbatim 2026-10-29 session record + standing requirements) — GEMSDOE92

> **Status (2026-10-29):** Updated with the **verbatim** 2026-10-29 session prompt (resolving the prior session's reconstruction caveat in `docs/STANDING_BRIEF_20261028.md`). Read at the start of every session alongside `README.md`, `SUBMISSION_READY.md`, `SLOT_PLAN.md`, and `IRREGULARITIES.md`.
>
> **Evidence-label discipline:** All scores cited inside the prompt text below are **owner-reported `CLAIM` values** (never promoted to `ORGANIZER-CONFIRMED` without a captured submission-portal receipt image/log; see `IRREGULARITIES.md` `IR-1028C-1` and `IR-1029-1..3`).

## Verbatim 2026-10-29 session prompt (core instructions & Parallel-Run Protocol)

```text
First, review our GitHub repo, understand the full project, and check all commits, branches, PRs, issues, README, docs, and code to see what has already been done and what remains. Work on next steps from previous sessions first. Save this prompt into the README for future reference and read it at the start of every session.

Focus on the highest-scoring submissions from each of these sites: GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, GEMSDOE36. Build on their work to create new, better, unique submissions. Create an executive summary for each site, including a table listing the file, its estimated score, and whether it is unique compared to the other sites listed here. Explain how h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros from GEMSDOE32 got the high score of 0.2778 and if/how we can beat it.

Goal: Build a winning submission for the DOE GEMS Prize on DrivenData: https://www.drivendata.org/competitions/306/doe-gems/

Requirements:
- Must generate a unique .tif submission (never copy a previous submission, except for baseline/educational analysis) downloadable directly from the very top of the GitHub Pages site (1-click, obvious, impossible to miss, right in the executive summary). Make it unmistakable whether the .tif is ready to download and submit (e.g., clearly labeled "OK TO DOWNLOAD AND SUBMIT" only if it passes all validation checks). Each submission must also have a unique name and a short comment/description.
- Validation must happen automatically without human intervention before declaring any file unique or ready to submit. Never rely on a human to visually inspect or manually check a file—build and run automated validation scripts within the project to verify format, values, CRS, uniqueness, and compliance.

PARALLEL-RUN PROTOCOL (this session is one of several running in parallel on separate forks — follow strictly so our work compounds instead of colliding):
1. Pick a lane, check uniqueness first. Before training anything, inspect the shared submissions registry / existing outputs and verify your planned approach isn't already covered. Compute pixelwise rank-correlation and 3-px buffer overlap of your candidate against every raster in the registry — BEFORE dot placement (on the surface) AND after. If correlation > 0.90 OR >70% of your dots fall within 3 px of a single existing submission's dots, stop, log it as duplicate, and pivot. Diversity across runs is how we win the ensemble and avoid burning weekly slots on near-clones.
2. Reuse, don't rebuild. Use the repo's shared cached feature stack, shared holdout evaluator (hide-and-recover: whole fault segments withheld with buffer, catalogue features recomputed from visible faults only, visible faults masked pixel-exactly at eval, pooled DTI with alpha=0.2, beta=0.8, 300 m triangular kernel), and shared submission writer/validator. Do NOT write another metric implementation, feature loader, or GeoTIFF writer. If a shared tool has a bug, fix it in place rather than forking a private copy.
3. Evidence labels on every number. Tag every metric you report as either HOLDOUT-DTI (with evaluator version, n withheld positives, and 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). Never write a model projection as a score; projections caused the phantom-0.41 drift in earlier gens.
4. Leakage canary before trusting a gain. Test each new feature solo on the holdout; any single feature with holdout AUC > 0.90 is leakage until proven otherwise (dist_known_fault_px and thermalclass were both caught this way). Confirm training_features.tif and any well/spring CSV are clean of test-set fault proximity.
5. Output one Run Card at the end. Emit a structured JSON record with: hypothesis, geological mechanism, named non-fault mimic process, holdout DTI + CI, correlation/overlap vs. registry, output raster sha256, validator output, proposed submission name + 1-line portal note (<=140 chars), and verdict ("promote" or "negative"). Negative results are first-class deliverables — a clean "tried X, holdout -0.004, do not repeat" saves every parallel session from re-running it. Do not pick submission slots yourself; a separate selector step promotes the top diverse candidates within the weekly cap.
6. Hard budget: stop after <=3 experiments or <=2 hours of compute, whichever comes first, and write up what you found. Quality of one clean experiment beats five half-verified ones.

- Think like a PhD in structural geology and geothermal exploration: use real earth-science principles, fault mechanics, hydrothermal alteration, geophysical signatures, stress regimes, and spatial data science to guide feature engineering and modeling.
- Before implementing, generate 3–5 candidate geological hypotheses we haven't tried yet, each naming: the specific layer(s) involved, the physical signature being targeted (e.g., an edge-detection or curvature transform), why it should catch a fault missing from the USGS/INGENIOUS catalogue rather than one already in it, and how it differs from anything already implemented in this repo. Rank them by expected DTI improvement and implementation cost. Validate the top candidate on our spatially-blocked holdout set before touching a weekly submission slot — do not spend a submission slot on an idea that hasn't beaten the current holdout best. If new external data would help, name a specific free, official source (e.g., USGS, NBMG, OpenTopography, state geological surveys) and confirm it is actually obtainable before designing around it.
- Design a clean, user-friendly GitHub Pages UI with an executive summary (including how to submit, key insights, what works, and next steps), easy file downloads, and links to official sources for verification.
- The current leaderboard high score is 0.4413 (previously 0.4193). Beat it.
- Always fix this submission error: "ERROR Summary: Invalid values — Detail: Predicted values must be in range [0, 1]". All pixel values must be strictly within [0.0, 1.0] with no NaN, Inf, or out-of-range values inside the valid region (and proper handling of nodata/mask as required by the competition format).
- At the end, create a PR and merge it to main. Document all remaining work and limitations.
- Make multiple passes over your work: Pass 1 to implement and verify, Pass 2 to review for bugs, missing requirements, edge cases, and assumptions and fix them, and Pass 3 to re-check everything end-to-end for accuracy, reliability, completeness, and quality before finishing.

Core values: Maximize P(Win). Own the outcome end-to-end. Verify everything from official sources, question assumptions, test hypotheses, iterate relentlessly, and think creatively to beat the benchmark.

Standing instructions: Work autonomously with zero manual input. Use only official, trusted sources and include links for manual review. Flag any irregularities for review. Zero hallucinations—verify everything line by line. Note: DrivenData competition data pages require login—do not attempt to authenticate or bypass login; rely on repo data and public/official sources.
```

## Verbatim 2026-10-29 claim ledger references

The full 133-row scored claim list (`128` base claims + `5` newly reported 2026-10-29 claims, including `GEMSDOE92` `gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros: 0.2784`) and `8` unscored submissions (including `GEMSDOE92` `gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros`) are stored line-by-line in:
- [`ledger/claims_20261029.txt`](../ledger/claims_20261029.txt) (`133` scored `CLAIM` rows; `128` byte-matched across `2,262` registry SHA-256s in [`evidence/claims_matched_20261029.json`](../evidence/claims_matched_20261029.json))
- [`ledger/unscored_20261029.txt`](../ledger/unscored_20261029.txt) (`8` unscored rows)
- [`IRREGULARITIES.md`](../IRREGULARITIES.md) (`IR-1029-1..4`: `udth-submod` `0.0525` vs `0.1516` swap with `plkc-dualoof`, 4 blank-colon Oct-28 rows, CRLF/stale `rieszlbm2` eligibility note in `ledger/submissions.csv`).
