# Three-pass repository review — 2026-10-25 Arena continuation

## Executive decision

**NEGATIVE. Research download only; DO NOT SUBMIT or spend a weekly slot.** This review created no GeoTIFF, did not copy or rename an earlier file, ran no geological experiment and produced no HOLDOUT-DTI or ORGANIZER-CONFIRMED score. The requirement for a genuinely new, eligible GeoTIFF remains unmet.

The stop is evidentiary, not a format judgment: a byte-pinned public-mirror registry witness is positive in every valid footprint cell. Under the unchanged literal three-pixel overlap rule, any nonempty in-footprint prediction has `REGISTRY-MEASUREMENT` forward overlap `1.0`, above the `0.70` stop. The required pre-placement check therefore rejects before a candidate surface can be placed. No surface was built to work around that rule.

The existing site-designated primary remains downloadable for **research only**. Its `gems validate` format checks pass, but the same pinned witness gives its final dots literal overlap `1.0`. A validator pass cannot authorize submission. The fresh receipts are [`preplacement_stop_20261025_arena.json`](downloads/preplacement_stop_20261025_arena.json) and [`arena_current_primary_witness_20261025.json`](downloads/arena_current_primary_witness_20261025.json); this review's machine-readable run card is [`arena_review_run_card_20261025.json`](downloads/arena_review_run_card_20261025.json).

## Three-pass review

### Pass 1 — implementation and verification

1. Re-read the repository README and persistent operating brief; checked the `0.2778` analysis, existing hypothesis shortlist, feature-band map, current primary and shared renderers.
2. Added a four-item, cost-ranked **conditional** shortlist in [`HYPOTHESES_20261025_ARENA.md`](HYPOTHESES_20261025_ARENA.md), supplementing rather than replacing the existing three-hypothesis review. It names layers, physical signatures, uncatalogued-fault rationale, method differences, non-fault mimics, qualitative expected value, cost, and data prerequisites.
3. Reused the previously retrieved exact GitHub-blob witness and pinned pre-placement gate. The receipt confirms the witness hash and Git blob identity, grid agreement, all `5,167,373` footprint cells positive, and the universal literal stop. This is **REGISTRY-MEASUREMENT**, single-witness rejection only—not full-registry clearance.
4. Rechecked the current site-designated LISTRICDIP raster: file SHA-256 `91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e`; `REGISTRY-MEASUREMENT` forward overlap within 3 px `1.0`; full-footprint Spearman `0.010352227787484035`. It fails the literal overlap gate even though the correlation is below its `0.90` threshold.
5. Re-ran `gems validate` against that *existing* primary: **11/11 format gates passed** (grid/CRS/transform, float32 one-band encoding, range, NaN/outside-footprint rules, catalogue distance, submission encoding, and reread SHA). These are format/encoding validations, not uniqueness, holdout, eligibility, or organizer acceptance.
6. No candidate surface, dot set, feature-alone leakage canary or holdout was generated. The shared evaluator/writer was not invoked. Experiment budget used: zero; weekly slots used: zero.

### Pass 2 — bug, assumption and edge-case review

- **Dense witness is dispositive under the standing rule.** Because every valid footprint cell is positive, any nonempty candidate is blocked. This does not depend on the candidate's DTI, rank correlation, geological plausibility, or file format. Do not substitute matched-budget overlap or a different registry rule.
- **Input dependency is unavailable and provenance unresolved.** `data/training_features.tif` and `.cache/gems_inputs/training_features.tif` are absent. The manifest pins a 418,912,844-byte mirrored stack (SHA-256 `4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5`), but marks upstream origin `UNVERIFIED` and public-mirror use as `FLAGGED_DATA_USE_UNCHECKED`. Official competition data-page access is unverified in this environment; login may be required. No authorized fetch or terms verification was performed. No candidate is called viable while either prerequisite is unresolved.
- **Band semantics correction.** `vendor/gems57/geo.py` maps B7 to scalar geodetic shear rate and B8 to scalar geodetic dilatation. These scalar bands cannot yield a principal shear azimuth. Any TENSOR-RIEDEL directional construction requires independent vector strain components or a real strain tensor; the later-dated draft is not evidence of one.
- **No leakage or holdout inference.** With no new surface, there is no feature-alone AUC, buffered whole-segment holdout, withheld-positive count, evaluator version, or 95% CI for a new candidate. A prior result elsewhere in the repository is not this review's measurement.
- **Date/provenance mismatch.** The review receipts are dated `2026-10-25T16:45Z` and `16:47Z`; the existing primary filename embeds `20261025T190000Z`, which is later than those receipt times. The README also opens with a `2026-10-26` LISTRIC banner. These strings conflict with the checkout/review time. This review does not claim when those raster bytes were actually created; future-dated banners are not current evidence and must not be promoted as output of this review.
- **Scope of registry result.** The witness came from a public repository mirror, not an organizer registry receipt. Its Git blob identity and bytes were verified; official authorship, organizer endorsement, completeness of the registry, and mirror reuse rights were not. The receipt is deliberately rejection-only.

### Pass 3 — acceptance-criteria recheck

- The `GEMSDOE32` `0.2778` value remains a **CLAIM**, not an organizer-confirmed score. No submission-page receipt for the named raster was found in the ledger. The repository also records conflicting user-reported `0.3195` and `0.4413` figures; none is upgraded here to a verified score. No causal explanation is asserted.
- All new and repeated numeric evaluations are explicitly identified as **REGISTRY-MEASUREMENT**, **format validation**, or **HOLDOUT-DTI** / **ORGANIZER-CONFIRMED** where applicable. This review has no new HOLDOUT-DTI and no ORGANIZER-CONFIRMED score.
- The unchanged file is made easy to download, but its site status explicitly says research only / do not submit. Existing website and README status feeds must not imply eligibility from the 11/11 format pass.
- Three to five hypotheses are ranked before implementation; the top one remains untested. Do not spend a weekly slot. Stop after the three-experiment/two-hour ceiling.
- No manual pixel review is needed for these rejection and format checks; no authentication or data entitlement was assumed.
- **Maximize P(Win):** preserve the slot and avoid optimizing against an impossible or unverified gate. **Own the Outcome:** publish the negative evidence, correct the public status, and leave the new-TIFF objective openly unmet.

## Understanding the `GEMSDOE32` `0.2778` claim

[`BEAT_0_2778.md`](BEAT_0_2778.md) correctly treats `0.2778` as a claim and explains one *possible* distance-weighted Tversky mechanism: thinning redundant nearby predictions could reduce redundant false-positive mass while retaining proximity credit. That mechanism is not an explanation of the claimed organizer result. The exact scored file, actual submission, metric implementation, score receipt, and causal contribution of thinning are not established by the current ledger. Matched-budget and local hide-and-recover metrics are proxies, not leaderboard scores. A rigorous explanation requires the exact organizer receipt and byte-matched candidate, followed by paired, same-budget ablations under the organizer metric; no such test was run here.

## Holdout and registry results

- **HOLDOUT-DTI:** not run in this review; no candidate surface was built. Evaluator version, withheld-positive count and 95% CI are therefore not applicable. This is not a zero score and must not be represented as one.
- **ORGANIZER-CONFIRMED:** none. No receipt was created or found.
- **REGISTRY-MEASUREMENT — pre-placement witness:** `forward_overlap_for_any_nonempty_in_footprint_dot_set = 1.0`; literal stop threshold `0.70`; universal-stop flag `true`; positive witness pixels / valid footprint pixels `5,167,373 / 5,167,373`. No candidate correlation exists because no candidate surface was generated.
- **REGISTRY-MEASUREMENT — existing site primary:** final-dot overlap `1.0` (blocked); full-footprint Spearman `0.010352227787484035` (below `0.90`, but irrelevant to the overlap failure). This is one pinned-witness rejection, not a full-registry clearance.
- **Automated format validation — existing site primary:** `11/11` gates passed. This does not change the negative eligibility decision.

## Existing primary, download, and form fields

The current site-designated research file is [`gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif`](downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif). SHA-256: `91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e`. It was not created by this review and is **not cleared for submission**. No new submission name or actual form note is proposed; `submission_name` is `null`, and the run card's `note` explicitly says it is not applicable because no new submission was generated. Do not submit this existing file because its format validator passed.

## Required next actions

1. Preserve the negative decision until the duplicate policy is authoritatively clarified or the pinned witness is shown not to be an in-scope registry. Do not silently redefine either threshold.
2. Obtain the competition feature stack through an authorized route, verify its SHA-256 and band metadata, and document reuse/distribution terms. Do not claim success from the public mirror alone.
3. If and only if the policy blocker is resolved, run the preregistered rank-1 magnetic-texture displacement registration inside the assigned method lane. Use the shared evaluator/writer, buffered whole-segment holdouts, fold-visible catalogue features, exact visible-fault masking, the pooled DTI settings in the operating brief, and feature-alone leakage canaries. Report HOLDOUT-DTI with evaluator version, withheld-positive count, and 95% CI. Compare against the locked holdout control before promotion.
4. Run a final automated file validator and both pre-placement-surface and final-dot uniqueness gates before considering the separate weekly-slot selector. A valid TIFF is not a submission authorization.
5. Obtain an organizer submission-page receipt before recording any score as ORGANIZER-CONFIRMED.

## Reproducibility references

- [`docs/HYPOTHESES_20261025_ARENA.md`](HYPOTHESES_20261025_ARENA.md) — expanded candidate ranking and data boundary.
- [`evidence/preplacement_stop_20261025_arena.json`](../evidence/preplacement_stop_20261025_arena.json) — fresh rejection-only pre-placement receipt.
- [`evidence/arena_current_primary_witness_20261025.json`](../evidence/arena_current_primary_witness_20261025.json) — existing-primary single-witness measurement.
- [`docs/downloads/arena_review_run_card_20261025.json`](downloads/arena_review_run_card_20261025.json) — machine-readable negative run card.
- [`SESSION_PROMPT.md`](../SESSION_PROMPT.md) and [`README.md`](../README.md) — durable operating brief and project history.
