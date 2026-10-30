# Repository review — 2026-10-30

## Executive decision

**No new experiment or TIFF was generated. Do not submit any existing download.** The current standing protocol requires a single assigned method paragraph/lane, and the supplied request does not name that paragraph. Independently, the unchanged literal registry rule flags the positive-support witness (`17GEMSDOE`) at overlap 1.0, above the 0.70 stop threshold for every nonempty in-footprint candidate. Proceeding to feature placement would violate the stop-before-placement requirement. This review therefore records engineering findings only; it does not spend experiments or a competition slot.

## What was inspected

- Root README, session prompt, standing prompt, submission status and current-review/next-step documents.
- Shared `gems/` modules, scripts, registry/evidence layout, existing downloadable artifacts and Git state.
- Branch is `arena/2426e03b-gemsdoe92`, clean at review start, based on `082513e`.

## Findings

1. **Submission controls are fail-closed in project documentation.** `SUBMISSION_READY.md` explicitly says research download only / DO NOT SUBMIT. This is consistent with the standing prompt and readiness record; local TIFF format validity is not competition clearance.
2. **The user's requested new unique TIFF cannot responsibly be produced under the active protocol.** The missing lane assignment and dense-witness stop are blockers, not reasons to guess or silently reinterpret uniqueness. No HOLDOUT-DTI estimate or new submission name is asserted here.
3. **Current documentation has substantial historical duplication and stale status surfaces.** The README is very large and includes dated/historical session addenda; `docs/REVIEW_CURRENT.md` begins with 2025-10-25 content despite later 2026-10-29 evidence elsewhere. A reader can encounter contradictory “current” statements. The dated standing prompt is more recent, but a single generated status source should own top-level status.
4. **Score claims need source typing.** The README and historical site ledgers contain CLAIM, HOLDOUT-DTI, MODEL, and organizer figures. Keep each labeled and avoid treating the reported `0.2778`/`0.2784` or leaderboard `0.4413` as an authenticated receipt unless a submission-page receipt is archived. The project itself reports no organizer-confirmed receipt in the latest standing record.
5. **Data availability limits independent reproduction.** The checked-in `data/` directory contains only small parent rasters and bridge cache directory, not the competition's complete official training inputs. The repo records that DrivenData data access requires login. Do not fabricate a full data-driven result from these files.
6. **Automated test suite was not runnable in this environment:** `pytest -q` failed because the `pytest` executable is absent; `python -m pytest -q` failed because the module is not installed. `scripts/check_site.py` also cannot start because `numpy` is absent. Separately, a standard-library parse of all 737 repository JSON files passed, and `git diff --check` passed. These are environment/format checks, not a passing scientific or full test result.
7. **Pull request/merge is not performed by this review.** No code or site artifact was changed. The requested protocol also calls for promotion via a separate selector, and branch protections/authorization for a merge were not verified.

## Required next steps (ordered)

1. Obtain an explicit method-lane paragraph and an authorized resolution of how the literal dense positive-support witness is interpreted. Until then, do not place candidate dots or run a lane-specific experiment.
2. Restore the SHA-pinned official/cached inputs through the authorized access path; verify hashes and license/redistribution provenance before publication.
3. Install declared dependencies in the supported environment and run the complete test suite, then execute the shared evaluator/writer regression tests.
4. Once authorized, pre-register 3–5 genuinely untried hypotheses, verify external official data availability before choosing any data-dependent candidate, and test each feature alone for leakage. Spend at most the stated experiment budget.
5. Only a candidate beating the locked spatial holdout control with a positive paired confidence interval and passing pre-placement and final-raster uniqueness plus format gates can proceed to the separate weekly selector. Label predictions as HOLDOUT-DTI, MODEL, CLAIM, or ORGANIZER-CONFIRMED as appropriate.
6. Consolidate status pages so `readiness.json` is generated from one validated manifest; add a CI check that rejects stale “current” dates, broken local links, missing TIFFs, and disagreement between the download page, run card, and readiness JSON.

## Three-pass completion record

- **Pass 1 — inspect and record:** reviewed the standing mission/protocol, current submission/readiness statements, repository layout, data inventory, and Git state; documented blockers and next actions.
- **Pass 2 — audit the review itself:** checked claims against files present in this checkout, parsed all 737 JSON files, attempted the existing site checker and test suite, and recorded missing dependencies rather than claiming tests passed.
- **Pass 3 — requirements re-check:** confirmed no new TIFF, experiment, slot, lane, or score estimate was invented; clarified that downloadable research artifacts are not cleared for submission; `git diff --check` passed.

This is a repository/code-and-document review, not an independent scientific re-run. No external pages were fetched in this review; therefore no fresh statements about current official leaderboard status, site contents, competition rules, or data availability are made. The dated reports cited above are repository evidence and should be checked against their captured sources before being treated as current facts.
