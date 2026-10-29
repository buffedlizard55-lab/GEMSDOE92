# Standing Competition Prompt & Parallel-Run Protocol — GEMSDOE92 (Updated 2026-10-29)

> **Status (`2026-10-29`):** Authoritative standing baseline for `GEMSDOE92`, incorporating the `2026-10-29` prompt updates (notably `gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros: 0.2784` `CLAIM`, plus newly reported external `CLAIM`s across `KANLERGEMSDOE3`, `GEMSDOEkarage1`, `ApartGEMSDOE3`, `ApartGEMSDOE1`, and `GEMSDOE92` `listricdip-updip50: 0.0255`). Read this file alongside [`README.md`](../README.md), [`SESSION_PROMPT.md`](../SESSION_PROMPT.md), and [`IRREGULARITIES.md`](../IRREGULARITIES.md) at the start of every session before running any experiment or modifying site outputs.

## Standing Project Mission & Deliverables

1. **Previous Session Follow-Through First:** Review the repository and execute open next steps from previous sessions before starting new modeling work. Keep this prompt in `README.md` / `docs/STANDING_PROMPT.md` and read it at the start of every session so every iteration builds on a verified, everyday-usable foundation.
2. **Competition Target & Grid Compliance:** Compete in DrivenData Competition #306 (**DOE GEMS: Geothermal Exploration using Machine Learning and Statistics**) predicting unmapped subsurface & Quaternary faults across the northwestern Great Basin study area (`EPSG:32611`, `3730 × 3292` / `3292 × 3730` 100 m template matching `sample_submission.tif`, single-band `float32`, finite values strictly in `[0, 1]`, eliminating `"Predicted values must be in range [0, 1]"`). Scored by the **Distance-Tolerant Tversky Index (DTI)** with `alpha = 0.2` (FP weight), `beta = 0.8` (FN weight), and `300 m` (`3 px`) Euclidean triangular tolerance kernel, with mapped USGS/INGENIOUS catalogue pixels masked pixel-exactly.
3. **Focus-9 & 8-Owner Fleet Executive Summary:** Provide an executive summary at the very top of the GitHub Pages site and per focus site (`GEMSDOE24`, `GEMSDOE25`, `GEMSDOE27`, `GEMSDOE28`, `GEMSDOE30`, `GEMSDOE31`, `GEMSDOE32`, `GEMSDOE33`, `GEMSDOE36`) plus `GEMSDOE92` and all 8 GitHub owners (`buffedlizard55-lab`, `kanlerxz87-cyber`, `eugboogieman123-ops`, `wingbangboozle1-lang`, `ginnymcfiner23-ux`, `karagemop466-tech`, `apartanish22-droid`, `sassnarep3-star`), with a clear table showing:
   - Exact file to download,
   - Estimated / reported score (strictly labeled per Rule 3),
   - Whether it is unique across all listed GEMSDOE sites, and
   - Unmistakable automated clearance (`OK TO DOWNLOAD` vs `DO NOT SUBMIT` / `OK TO SUBMIT` only when all mandatory validation + uniqueness + policy gates pass without human inspector intervention).
4. **How-To-Submit Executive Summary Subpage:** Provide a clear subpage (`docs/how-to-submit.html`) explaining step-by-step how to upload a single-band `.tif` (or single-TIFF `.zip`), choose a unique submission name and short note (`<= 140` characters), respect the weekly submission limit, and prevent `"Predicted values must be in range [0, 1]"`.
5. **PhD-Level Score Forensics:** Explain at a PhD level why and how `GEMSDOE32` (`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778`) achieved its score, why `GEMSDOE92` (`gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros: 0.2784`) surpassed it while diverging from its `0.3322` `LBM-v1` projection, how those relate to the `0.3195` and `0.4413` leaderboard references, and how to score higher with a genuinely unique submission.
6. **Pre-Registered Untried Geological Hypotheses (3–5):** Before implementing, generate 3–5 untried candidate geological/geothermal hypotheses, each naming:
   - Specific layers/bands,
   - Physical signature and mathematical transform,
   - Why it detects faults missing from the USGS/INGENIOUS catalogue,
   - Named non-fault geological/anthropogenic mimic,
   - How it differs from all existing repository modules, and
   - Free official external source + obtainability verification if external data is required.
   Rank by expected DTI gain vs implementation cost, and validate the top candidate on the shared spatially-blocked holdout before spending any weekly slot.
7. **Unique Validated `.tif` Generation:** Generate a genuinely unique `.tif` submission (never copying any existing GEMSDOE submission except for baseline comparison/learning), validated automatically without human intervention, and surfaced cleanly for 1-click download at the top of the site.

## Mandatory Parallel-Run Protocol

1. **LANE & DUPLICATE STOP:** Stay inside one method lane per session. If raster Spearman rank-correlation `|rho|` with any registry raster exceeds `0.90`, OR `> 70%` of dots fall within `3 px` (`300 m`) of one registry raster's dots, log as duplicate and stop. Check on **both** the pre-placement continuous surface **and** the final placed dots across the complete 8-owner registry (disclosing both sparse/top-N `PI-1` and the literal full-support `17GEMSDOE` dense-witness reading).
2. **REUSE, DON'T REBUILD:** Use the shared cached feature stack (`.cache/gems_inputs/`), `vendor/gems57/evaluate_holdout.py`, and `vendor/gems57/submission_writer.py` (whole-fault-segment buffered spatial holdout `gems57-pooled-hide-v2`, strictly fold-visible catalogue features, pixel-exact visible-fault masking, pooled DTI `alpha = 0.2, beta = 0.8`, `300 m` triangular kernel). Fix shared tools once if needed; never maintain a private fork.
3. **LABEL EVERY NUMBER:** Every numerical claim must carry its explicit evidence class:
   - `HOLDOUT-DTI` (with evaluator version, withheld-positive pixel count, and 95% block-bootstrap CI),
   - `ORGANIZER-CONFIRMED` (copied from an authenticated organizer submission receipt; `None` locally),
   - `CLAIM` (owner-reported score in prompt/repo text; unverified locally),
   - `MODEL` (metric-structured projection fitted to `CLAIM`s; never written as an actual score), or
   - `REGISTRY-MEASUREMENT` (byte-verified overlap/correlation measurement).
4. **LEAKAGE CANARY:** Evaluate every candidate feature **alone** on the spatially-blocked holdout before training or combining; symmetric `AUC > 0.90` (`max(AUC, 1 - AUC) > 0.90`) is treated as catalogue leakage until proven otherwise.
5. **JSON RUN CARD:** Emit one protocol-compliant JSON Run Card containing: `hypothesis`, `mechanism`, `named_non_fault_mimic`, `holdout_dti` (+ 95% CI), `correlation_overlap_vs_registry`, `raster_sha256`, `validator_output`, `submission_name`, `note` (`<= 140` chars), and `verdict` (`promote` / `negative`). Negative verdicts are first-class scientific deliverables.
6. **BUDGET & SEPARATE SELECTOR:** Stop after at most `3` experiments or `2` hours. Promotion to a real weekly competition slot (`3/week` cap) is a separate human selector step — never auto-spend a slot on a candidate that fails any mandatory holdout or uniqueness gate.
7. **THREE-PASS QUALITY & GIT WORKFLOW:** Execute three explicit passes (**Pass 1:** implement & verify; **Pass 2:** audit bugs, assumptions, edge cases & fix; **Pass 3:** re-verify against every prompt requirement & polish), open a PR from the session branch, merge onto `main`, and document remaining suggestions and limitations. Core values: **Maximize P(Win)** and **Own the Outcome**.

## Dated Ledger Files Referenced by This Baseline

- `ledger/claims_20261029.txt` & `ledger/unscored_20261029.txt`: Complete `2026-10-29` owner-reported `CLAIM` and unscored fleet tables across all 8 GitHub owners (superseding `2026-10-28` unscored status for `lbmc1`, `KANLERGEMSDOE3`, `GEMSDOEkarage1`, and `ApartGEMSDOE3`, with discrepancies documented in `IRREGULARITIES.md` `IR-1029-1..3`).
