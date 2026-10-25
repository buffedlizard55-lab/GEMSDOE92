# Three-pass review — BLINDFAULT (2026-10-25)

## Status at closeout

**✅ OK TO DOWNLOAD FOR RESEARCH — ⛔ DO NOT SUBMIT.** The primary artifact is a newly generated unique TIFF, but it fails the pre-registered holdout promotion criterion. `submission_eligible` is `false`, verdict `negative`, and zero weekly competition slots were used. This is a local research result, not an organizer-confirmed score.

- TIFF: [`gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-zeros.tif`](downloads/gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-zeros.tif)
- One-TIFF ZIP: [`gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-zeros.zip`](downloads/gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-zeros.zip)
- Run card: [`blindfault_run_card.json`](downloads/blindfault_run_card.json)
- Analysis: [`ANALYSIS_20261025_BLINDFAULT.md`](ANALYSIS_20261025_BLINDFAULT.md)
- Pre-registration: [`HYPOTHESES_20261025_BLINDFAULT.md`](HYPOTHESES_20261025_BLINDFAULT.md)

## Pass 1 — inspect and verify existing session work

The pre-registration describes five ranked candidates; BLINDFAULT was the first. It ran three pre-registered experiment arms, within the stated 3-experiment budget. This review did not launch another geological experiment or consume a slot.

**HOLDOUT-DTI** (evaluator `gems57-pooled-hide-v2`, 22,663 withheld positives; strict draw-blind LOQO, fold-visible `d_visible > 2.0`): primary `blindtopo` = **0.047896 [0.038079, 0.057970]**; the hypothesis arm `blind` = **0.037842 [0.029376, 0.047036]**; reference `H19-5` = **0.096757 [0.084640, 0.108096]**; repository holdout-best = **0.113316 [0.100614, 0.127163]** (`COULOMBLOQO standalone`). These are local holdout measurements only. The primary does not beat the pre-registered best and its verdict is negative.

**Leakage canaries:** maximum symmetric AUC 0.5728, below the 0.90 stop threshold. **REGISTRY-MEASUREMENT:** cached Git-blob inventory reports 1,386 public exact-grid rasters from 102 repositories; dual-reading matched-budget worst overlap is 0.5219 and literal worst overlap is 1.0000. The literal full-footprint witness result is displayed, not hidden. The run card records the local comparisons and exact-file metrics. Registry overlap is not a competition score or proof of geologic equivalence.

**Format validation:** independent `scripts/validate_submission.py` check passed for the primary TIFF: one float32 band, 3730 × 3292, EPSG:32611, sample transform matched, all pixels finite, values in [0,1], 0 outside footprint, 37,654 positive dots and no catalogue mass. SHA-256: `c91170e5d4ffc67a18378aa9f479b8786ff6e92970e12e6646de14dbc6c5cf3d`. This verifies local format/range only; it does not establish organizer acceptance.

The current explanation for the `GEMSDOE32` result and evidence limits are in the linked analysis and pre-registration. The user-provided `0.2778`, `0.3195`, `0.4413`, and sibling-site scores are claims unless supported by an organizer receipt; they are not independently confirmed in this repository review. No causal explanation of the historic score can be established from the score alone.

## Pass 2 — contradiction and implementation review

Found stale status references: the README and `docs/REVIEW_CURRENT.md` still pointed to the earlier 1f514ffc state (“no new TIFF”), while the top-level rendered status and BLINDFAULT run card describe the subsequent artifact. Updated README to make the newest status explicit and added this dated review document. Earlier reviews remain historical records and must not be overwritten as if their observations were made in this session.

The website's older primary download card is still explicitly a research artifact and contains historical metrics; do not interpret that legacy card as the current candidate. The BLINDFAULT status block at the top of the homepage is authoritative for the newly generated research artifact. A remaining site cleanup item is to make every historical page section clearly date-scoped, avoiding old primary-card prominence.

## Pass 3 — checks and limitations

During PR preparation, `main` advanced with the separate RADIOCONTACT lane. That lane is retained as an independent research result; this review did not select it, rerun it, or combine its numbers with BLINDFAULT. Its stored pre-registration document is named and internally dated 2026-10-26 while the run card is dated 2026-10-25. Because that is future-dated relative to the session date, the claim that it was preregistered before its run cannot be independently established from timestamps here; treat the chronology as an irregularity for review, not verified provenance. No weekly selector decision is made.

Checks run on this checkout:

- `pytest -q`: **294 passed**, 124 upstream Affine pending-deprecation warnings.
- `python scripts/check_site.py`: **49 served rasters passed** the local format gates.
- `python scripts/verify_manifest.py`: all eight listed input/parent hashes verified.
- `python scripts/validate_submission.py <primary TIFF>`: passed.
- `git diff --check`: passed before this documentation-only update; rerun after edits.

No fresh holdout was run here; numbers above are read from the existing run card. The pinned competition cache in this checkout is limited and is not an authenticated DrivenData dataset download. Competition rules, live leaderboard, weekly cap, external licenses, and organizer receipt cannot be confirmed from local tests. Official reference links remain listed in the pre-registration and submission guide.

## Next work

1. Reconcile the old homepage primary card and `docs/REVIEW_CURRENT.md` with the dated BLINDFAULT status, retaining historical evidence and avoiding claims of a current score.
2. Do not spend another experiment: the recorded lane used 3/3. If the budget is reset in a later session, re-register a method and compare identical fold-visible holdouts against the current best before any slot decision.
3. Resolve data access/provenance constraints and verify competition rules/slot cap through the authenticated official competition page; no credentials or organizer scores are available in this checkout.
4. Submission promotion remains a separate selector decision. This negative candidate is not cleared for upload.
