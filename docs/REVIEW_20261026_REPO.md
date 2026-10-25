# Repository review — 2026-10-26

## Decision

**OK TO DOWNLOAD FOR RESEARCH; DO NOT SUBMIT or spend a weekly slot.** No TIFF was generated in this review, no geological experiment was run, and no submission slot was used. This respects the repository's binding pre-placement stop rule rather than manufacturing a supposedly eligible artifact.

This review is limited to repository state and executable checks. No external site was fetched during this review; user-provided leaderboard and historical score values remain **CLAIM** unless separately backed by an organizer receipt. No ORGANIZER-CONFIRMED score is asserted here.

## Pass 1 — execute the documented checks

Environment: Python 3.11 virtual environment `/home/user/.venv_gems`, installed from `requirements.txt` plus pytest. The repository checkout itself was not modified to provision it.

| Check | Result |
|---|---|
| `python -m pytest tests -q` | **VERIFIED-RUN:** 498 passed, 140 PendingDeprecationWarnings; 21.89 s. |
| `make manifest` | **VERIFIED-RUN:** `RESULT: OK`; all eight manifest entries checked. |
| `make verify` | **VERIFIED-RUN:** pinned parent R0, SHA-256 prefix `c55bafc47005…`; 37,654 dots; 5,167,373 footprint pixels. The verifier also reports 2,171 parent dots within 3 px of catalogue faults. |
| `python scripts/render_public_status.py --check` | **VERIFIED-RUN:** public panel bytes and ordering agree on all checked public entry pages. |
| `python scripts/check_site.py` | **VERIFIED-RUN:** `SITE CHECK PASS (82 served raster(s) gated)`. |
| `git status --short --branch` | **VERIFIED-RUN:** branch `arena/98b45384-gemsdoe92`, initially clean. |

Commands that import numerical dependencies must use the environment, e.g. `PATH=/home/user/.venv_gems/bin:$PATH make manifest`. Bare system Python lacks NumPy and fails before checks begin; this is an environment/setup issue, not a product test failure.

## Pass 2 — audit consistency and gate behavior

The primary download readiness feed (`docs/downloads/readiness.json`) is fail-closed: it identifies the LISTRICDIP updip50 raster as research-only, says do not submit, records `submission_eligible: false`, and cites a pre-placement universal-witness rejection. The file's recorded format checks include single-band float32, EPSG:32611, 3730×3292, matching sample transform, finite [0,1] values, zero outside footprint, and matching SHA-256. The witness proof's stated interpretation rejects all nonempty in-footprint dot sets; this is a binding rule in the repo, not a finding that the TIFF will score poorly.

**Irregularity: conflicting current-lane pointers.** `docs/downloads/current_submission.json` identifies FAULTNET/netfar (HOLDOUT-DTI 0.175147) while `readiness.json` and the generated public readiness panel identify LISTRICDIP/updip50 and explicitly say no new unique TIFF in this review. `scripts/render_current_submission.py` consumes the former; `scripts/render_readiness.py` consumes the latter. The full public checks pass, so they do not currently enforce that these two status sources name the same lane. The first file is a historical lane record, not evidence that its TIF is cleared; it itself has `ok_to_submit: false` and registry overlaps above the operational threshold. The differing pointers can confuse readers about what is current. I did not regenerate either file or claim a preferred primary because that would rewrite project status without a new authoritative lane decision.

**Irregularity: submission readiness is not a score gate.** The repo correctly separates format validation from submission eligibility. A format-valid GeoTIFF does not pass the literal uniqueness stop. The user prompt's suggested numerical high-score gate is not supported by a documented organizer-defined threshold; the correct project gate must stay evidence-based and cannot guarantee a leaderboard result.

## Pass 3 — check requested outcomes and remaining blockers

- Unique, automatically validated TIFF **for research download:** existing auditable files are available, but this review created none.
- Unique TIFF cleared for competition submission: **not achieved**; current status explicitly forbids submission under the pinned witness rule.
- Holdout: no new holdout was run. Existing HOLDOUT-DTI results use visible-catalogue fault labels and cannot establish performance on genuinely unmapped faults or predict a leaderboard score.
- New 3–5 hypothesis ranking: not generated in this review because repository instructions require a named method lane before experiments, but this prompt supplies no assigned single method paragraph; moreover the binding pre-placement stop prevents a new candidate. The already persisted hypothesis documents remain proposals, not results.
- Submission name/comment and download instructions exist in project records/pages; DrivenData upload and slot selection remain human actions. No receipt, login-walled data, or weekly-cap status was verified here.
- PR/merge request: not created in this review record; repository instructions reserve the active Arena branch. Any PR must use this branch and must not claim the research-only artifact is submission-cleared.

## Recommended next work

1. Resolve the status-source discrepancy by making one generated current-status manifest authoritative for both rendering paths and adding a CI assertion that the homepage, executive guide, README, readiness JSON, and current submission card cannot advertise different candidates. Keep the result fail-closed.
2. Keep the literal overlap stop binding unless the protocol owner formally changes it; do not reinterpret continuous rasters or matched-budget diagnostics as clearance.
3. If an experiment is later authorized, first state one precise geological method paragraph, record the pre-placement surface uniqueness check, test feature-only leakage canaries, run the shared buffered whole-segment holdout, and stop after the three-experiment/two-hour budget. Promote only if evidence beats the existing holdout control and all uniqueness/format gates pass. Such a result remains HOLDOUT-DTI, not an expected organizer score.
4. Obtain official/authorized competition training data through the permitted login route if absent; preserve provenance, hashes, terms, and avoid redistributing data without permission. Obtain an organizer submission-page receipt before labeling any score ORGANIZER-CONFIRMED.
5. Track source access and competition leaderboard snapshots with retrieval date and evidence class. Public third-party site values are claims unless linked to a verifiable receipt.

## Sources and reproducibility

- Repository operating contract: [`SESSION_PROMPT.md`](../SESSION_PROMPT.md)
- Current generated readiness: [`readiness.json`](downloads/readiness.json)
- Current submission lane record: [`current_submission.json`](downloads/current_submission.json)
- Binding preflight proof: [`review_f23_preflight.json`](../evidence/review_f23_preflight.json)
- Reproduce checks: `PATH=/home/user/.venv_gems/bin:$PATH make manifest verify`; `/home/user/.venv_gems/bin/python -m pytest tests -q`; `/home/user/.venv_gems/bin/python scripts/render_public_status.py --check`; `/home/user/.venv_gems/bin/python scripts/check_site.py`.
