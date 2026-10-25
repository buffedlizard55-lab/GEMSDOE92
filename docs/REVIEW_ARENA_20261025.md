# GEMSDOE92 repository review — 2026-10-25 UTC

## Decision

**Existing TIFFs are downloadable for research only; do not submit or spend a weekly slot.** No new TIFF, geological experiment, holdout, or slot was generated/used in this review. This is a repository and delivery-integrity review. The current registry policy rejects candidates against the pinned dense witness; format validity is not uniqueness clearance or organizer acceptance.

The currently designated research download is LISTRICLOQO `selectcal`, identified by [`docs/downloads/current_submission.json`](downloads/current_submission.json) and [`docs/downloads/readiness.json`](downloads/readiness.json). These two files agree on lane, file, name, note, and negative decision. Earlier audit text in `docs/REVIEW_20261026_REPO.md` alleging a FAULTNET/readiness mismatch does not match the checked-in JSON bytes in this checkout and should be treated as stale. The 2026-10-26 labels in some repository files are later than this review's controlling session date (2026-10-25 UTC); that chronology irregularity is not silently corrected here.

No third-party competition page or score was fetched during this review. Scores copied from user-provided GEMSDOE pages are claims unless backed by an organizer receipt. In particular, no score is represented here as ORGANIZER-CONFIRMED.

## Pass 1 — baseline checks and repository map

The checkout was initially clean on `arena/60d10e2c-gemsdoe92`. Python 3.11 was present but the required numerical packages and pytest were absent from system Python. I created an external review venv at `/home/user/.venv_gems_review` from the pinned `requirements.txt`; no environment files were added to the repository.

Commands and results:

| Check | Result |
|---|---|
| `python -m pytest tests -q` (using review venv) | Initial run: 539 passed, 3 failed; all three failures were repository consistency/UI issues detailed below. |
| `PATH=/home/user/.venv_gems_review/bin:$PATH make manifest verify` | PASS: all 8 manifest inputs match; pinned R0 verified. R0 is 37,654 dots, footprint 5,167,373 px, SHA-256 begins `c55bafc47005`. |
| `python scripts/check_site.py` | Initial run failed closed: one served TIFF was not linked from `docs/index.html` (TILTANGLE). After fixes: **SITE CHECK PASS (93 served raster(s) gated)**. |
| `python scripts/render_current_status.py --check` | PASS. |
| `python scripts/render_public_status.py --check` | PASS: primary bytes and first panel agree on checked public entry pages. |
| `python scripts/render_readiness.py --check` | PASS: research download revalidated; submission remains blocked. |
| `git diff --check` | PASS. |
| Final test suite | **542 passed**, 140 `PendingDeprecationWarning`s from Rasterio's affine transform multiplication. |

The site validator read and gated all 93 served `*-zeros.tif` files. It checks sample-grid CRS/shape/transform, one-band float32 encoding, finite values and [0,1] bounds, footprint handling, mapped-catalogue exclusion and the artifact's expected dot count. Passing these local gates does not prove a leaderboard score, artifact uniqueness under the registry protocol, or organizer acceptance.

## Pass 2 — failure analysis and repairs

### Repaired

1. **Prompt reference wording broke a README contract test.** Rephrased the sentence in `README.md` without weakening the requirement that README and `SESSION_PROMPT.md` are starting points. Converted stale TILTANGLE “deliverables for this session” into a clearly historical record, including its known missing confidence interval and negative submission status.
2. **Orphaned served TILTANGLE TIFF.** `scripts/check_site.py` correctly rejected the TILTANGLE raster because it existed under `docs/downloads/` but was not linked from the main workbench. Added a clearly historical, research-only entry and run-card/page links in `docs/index.html`.
3. **TILTANGLE page was misleading and structurally malformed.** Changed “submission-ready” wording to research-only, removed a mismatched `</h1>` closing tag, added the missing `<main>` landmark, and made the upload instructions explicitly say not to upload this artifact. Added a local record name and safe archive note that do not imply eligibility. Marked its reported holdout as incomplete because its archived card lacks a 95% CI.

The repaired page continues to distinguish format validation from promotion. The historical TILTANGLE GeoTIFF itself and its recorded run-card bytes were not modified.

### Current status and operational flags

- The current status feed is fail-closed and synchronized on the selected LISTRICLOQO research artifact. The older review claiming current-submission/readiness disagree is stale relative to these checked-in files.
- The site advertises many historical candidate files. It now links every served zeros-outside raster, but users must heed each explicit negative/research-only status; the download control is not authorization to upload.
- The generated readiness panel calls the download “unique” in the byte-distinct sense while the same panel states registry clearance failed. This can be misread as registry uniqueness. I did not alter its shared renderer because its own source hash is included in the published `review48` audit receipt; a correct wording change requires regenerating and publishing a new byte-bound audit receipt, not just hand-editing the page.
- There are numerous aged, lane-specific summary panels and contradictory historical “best” labels in the archive. They should not be interpreted as current decisions without checking the current generated readiness feed and artifact-bound run card.
- 2026-10-26-dated artifacts and review text occur in a session governed by 2026-10-25 UTC. Keep the timestamp discrepancy visible; do not backdate or infer sequence from filenames alone.
- The displayed historic TILTANGLE holdout is HOLDOUT-DTI (`gems57-pooled-hide-v2`, 45,253 withheld positives), `0.033466`; its 95% CI is absent from its archived run card, therefore it is incomplete and not usable as a promotion comparison.

## Pass 3 — user requirements, scope and next work

- **Unique TIFF:** no new TIFF was created. The repository already contains byte-distinct research artifacts, but the pinned literal dense-witness protocol records 100% forward overlap for any nonempty in-footprint support. Thus no current candidate can truthfully be called registry-cleared or upload-eligible. Do not manufacture a new file merely to satisfy a download requirement.
- **TIF format:** current primary `h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif` is locally format-valid; check the run card and readiness receipt for exact hash/metadata. The download is for research only.
- **Hypotheses/holdout:** no new 3–5-hypothesis ranking or experiment was launched. The prompt requires one assigned method lane, while this checkout presents multiple historical lanes; it also records the experiment budget as already used in prior lane sessions and the universal registry stop. Selecting another lane or treating a prior scored artifact as a fresh experiment would violate the parallel-run protocol. Resume only when a specific lane is assigned and the pre-placement rule permits a candidate.
- **High-score claims:** holdout DTI is an internal surrogate, not a projected competition score. The quoted 0.2778 and 0.3195 values were not re-fetched or verified here. The repo's [`BEAT_0_2778.md`](BEAT_0_2778.md) and [`ANALYSIS_20261025_LEADERBOARD.md`](ANALYSIS_20261025_LEADERBOARD.md) correctly treat the flagship value as a claim: source records say the GEMSDOE32 artifact was labelled UNSCORED, with no receipt in the local ledger. A plausible geometric explanation in those analyses is that R0's thinning/pruning removed redundant or catalogue-adjacent predictions, potentially reducing false-positive mass under a distance-tolerant Tversky metric while retaining local proximity credit. That is conditional mechanism reasoning, not a verified causal explanation; off-catalogue proxy evidence does not confirm it. Scoring above 0.2778 is possible in principle, but no submission receipt in this repo demonstrates it. The page's reported 0.4413/0.3195 leaderboard claims also were not live-verified in this review; only an organizer submission receipt may establish an ORGANIZER-CONFIRMED score.
- **Official-source research:** no external sources were fetched because this review focused on reproducible repository execution. Official references already cited by the project include DrivenData #306 problem/about/data pages, DrivenData's reference-solution repository, USGS GeoDAWN, DOE GDR INGENIOUS, and the NREL rules PDF. Live login-gated data, leaderboard contents, current weekly cap, and portal acceptance remain unverified from this environment.
- **Merge constraint:** do not merge this branch directly into `main` outside the requested PR workflow. This review's code changes are limited to repairing README wording and TILTANGLE discoverability/clarity; they do not promote any file.

## Recommended next actions

1. Resolve the method-lane and registry-policy question before running any new experiment. Retain the literal duplicate stop unless its owner changes it explicitly and documents the scope.
2. If an experiment becomes eligible, use only the shared feature cache, evaluator and writer; first run feature-only leakage canaries, then buffered whole-segment hide-and-recover HOLDOUT-DTI with its evaluator, withheld-positive count and 95% CI, and stop at the stated experiment/time budget.
3. Make status generation single-source across README, homepage, executive guide and machine-readable readiness. A machine check should ensure status, exact file SHA, note and eligibility agree everywhere; maintain fail-closed behavior.
4. Obtain a permitted organizer receipt and record it against the exact raster hash before claiming any competition score. Do not infer the weekly slot cap from old text or a third-party leaderboard snapshot.
5. Keep TILTANGLE's omitted 95% CI explicit or reproduce it from immutable holdout evidence before citing that result in future promotion comparisons.

## Reproduction

```bash
python -m venv /home/user/.venv_gems_review
/home/user/.venv_gems_review/bin/pip install -r requirements.txt
/home/user/.venv_gems_review/bin/python -m pytest tests -q
PATH=/home/user/.venv_gems_review/bin:$PATH make manifest verify
PATH=/home/user/.venv_gems_review/bin:$PATH python scripts/check_site.py
PATH=/home/user/.venv_gems_review/bin:$PATH python scripts/render_current_status.py --check
PATH=/home/user/.venv_gems_review/bin:$PATH python scripts/render_public_status.py --check
PATH=/home/user/.venv_gems_review/bin:$PATH python scripts/render_readiness.py --check
```

## Audit run card

See [`evidence/repo_review_run_card_20261025.json`](../evidence/repo_review_run_card_20261025.json). It summarizes the already-designated research file; it is not a new experiment or a submission clearance.
