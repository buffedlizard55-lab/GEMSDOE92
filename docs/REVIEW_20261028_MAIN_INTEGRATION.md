# Three-pass main-integration review — 2026-10-28

## Executive decision

**NO TIFF IS CLEARED. DO NOT SUBMIT or spend a weekly slot.** The latest artifact introduced by main, BLINDCORRIDOR, is a format pass only: its stored run card says `verdict: format_pass` and `submission_eligible: false`. It has no independently computed `HOLDOUT-DTI`, no feature leakage canaries, only a three-reference local overlap check, no full-registry uniqueness audit, and an unresolved literal dense-witness interpretation.

This follow-up did **not** generate a TIFF, run an experiment, select a slot, or obtain an organizer receipt. The BLINDCORRIDOR artifact came from the integration of `origin/main`; it was not produced or independently revalidated in this follow-up.

## Scope and integration state

- Repository: `/home/user/GEMSDOE92`, branch `arena/9649dfc1-gemsdoe92`.
- The PR branch was brought up to the fetched `origin/main` commit `9699f1d`. Merge conflicts in `README.md` and `docs/executive-summary-20261028-tipcomp.html` were resolved on this branch; the conflict markers were checked absent and the resolved files staged.
- PR #172 is the session PR. Its required `test` check passed after push; merging this documentation and safety work does not authorize any upload. Keep the status feeds and pages fail-closed.
- `docs/downloads/current_submission.json` and `readiness.json` still identify the RIESZ research artifact as the main status-feed primary, with a negative verdict. TIPCOMP remains negative. BLINDCORRIDOR has its own generated status feed.

## Pass 1 — artifact, evidence, and source inventory

1. Bound the BLINDCORRIDOR TIFF to its run card and audit:
   - File: `docs/downloads/gemsdoe92-blindcorridor-37654dots-20261028-11f8999c-zeros.tif`
   - SHA-256: `4027ee1637d8ce478a01684939e12bb31f1f73fe481d2b729be71927f3e52b14`
   - The stored audit records 11/11 file-format gates passing, 37,654 positive dots, and `verdict: format_pass`; this is not scientific validation or submission approval.
2. Read the byte-bound run card and overlap receipt. The reported worst 3-pixel overlap is `0.507675` across only three available bridge references (`d28.tif`, `h19_5.tif`, `h27_4_solo.tif`). This is not a scan of the full 2,060-raster registry and does not establish global uniqueness. The run card says the full registry cache is absent and the literal dense-witness interpretation is unresolved.
3. Confirmed that the run card does not contain an independently computed `HOLDOUT-DTI`, evaluator version, withheld-positive count, or 95% CI. Its full-stack feature leakage canaries were not run. The card's `0.30–0.34` value is a `MODEL` projection only, not a score and not evidence for promotion.
4. No new experiment was run because the assigned lane paragraph remains unavailable and the required input/cache/provenance gates are not met. The input-cache audit records 0/12 pinned files verified; organizer provenance and redistribution rights remain unverified.

## Pass 2 — independent claim and status challenge

- Rejected main-side “unique/ready” and “conditional” upload wording because it overstates a three-reference local check and conflicts with the run card's `submission_eligible: false`.
- Kept the landing-page primary unchanged as the negative RIESZ record; kept TIPCOMP negative; added BLINDCORRIDOR as an explicitly separate, research-only artifact. The new `docs/downloads/blindcorridor_readiness_20261028.json` binds its file hash to the run card and audit and records: `OK TO DOWNLOAD FOR RESEARCH ONLY`, `DO NOT SUBMIT`, missing holdout/canaries, partial uniqueness scope, and unresolved dense-witness status.
- Updated the generated landing pages and the manual executive-summary/how-to pages so no page describes BLINDCORRIDOR as cleared. Added a fail-closed site check and tests for its hash, verdict, eligibility, limited uniqueness scope, and visible status.
- Kept every score class separate. GEMSDOE32 `0.2778` remains a user-reported `CLAIM`; `0.3195` and `0.4413` remain unverified and conflicting. The bounded explanation is in [`WHY_0_2778.md`](WHY_0_2778.md). The `0.30–0.34` BLINDCORRIDOR estimate remains `MODEL` only. No number is labeled `ORGANIZER-CONFIRMED` without a receipt.
- Official links and the audit trail remain in the repository. The DrivenData reference-solution GitHub page was fetched earlier and shown to be a benchmark/reference, not an organizer score receipt. Competition, rules, USGS, and GDR pages were not live-verified in this follow-up.

## Pass 3 — consistency, regression gates, and handoff

- `scripts/render_safe_review.py` now verifies the BLINDCORRIDOR TIFF SHA-256 against the card and audit, checks that the ZIP contains exactly that TIFF, rejects a changed positive status, and generates the research-only readiness feed and landing-page section.
- `scripts/check_site.py` now fails closed if the feed, TIFF/ZIP hashes and payload, run card, audit, download label, submission label, holdout/canary status, uniqueness scope, or rendered page disagree.
- Preserved the older executive-summary audit inventory and submission guide while adding a current BLINDCORRIDOR status panel; the current landing page links to the TIFF, ZIP, audit, card, and readiness feed.
- Regression coverage is in `tests/test_blindcorridor_status_safety.py` and the existing site/render safety suites.
- `.venv/bin/python -m pytest tests -q`: **804 passed, 19 skipped, 171 warnings**.
- `PYTHONPATH=vendor .venv/bin/python scripts/check_site.py`: **SITE CHECK PASS (128 served rasters gated)**, including the new BLINDCORRIDOR hash/status contract.
- `PYTHON=.venv/bin/python make verify`: **PARENT VERIFIED (pinned artefact)**; R0 zeros SHA-256 starts `c55bafc47005…`, 37,654 dots. Manifest regeneration was not repeated in this follow-up.
- Python compilation, `git diff --check`, and local HTML/Markdown link checks: **PASS** (0 missing local links across the eight checked documents).
- The required GitHub `test` check passed. Merge PR #172 only after the final review confirms every download/submission status remains fail-closed; the merge itself does not clear a candidate.

## Unmet acceptance criteria and next gates

The request for a genuinely new, globally checked and experimentally validated unique submission remains **unfulfilled**. No artifact is cleared. Before another experiment: recover the missing assigned method paragraph; restore and provenance-check the required inputs; verify rights; resolve the registry witness policy and obtain the complete registry; then pre-register a lane. Any run must use the shared evaluator/writer, whole-fault-segment buffered holdout, visible-only catalogue features, pixel-exact visible-fault masking, pooled DTI (`α=0.2`, `β=0.8`, 300 m triangular kernel), individual-feature leakage canaries, pre-placement and final-dot checks, a complete JSON run card, and the 3-experiment / 2-hour budget. Slot selection remains separate.

The ranked hypothesis backlog is in [`HYPOTHESES_20261028_9649DFC1.md`](HYPOTHESES_20261028_9649DFC1.md). No new live leaderboard data were retrieved. The current repository still cannot substantiate an organizer score or a claim that a candidate beats the reported values.
