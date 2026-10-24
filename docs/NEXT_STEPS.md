# NEXT_STEPS — current project state (2026-10-24)

## Current status: blocked before experiment; no slot used

**Do not submit any currently linked TIFF.** All downloads are research-only negative/historical artifacts. No new candidate, experiment, holdout score, TIF, run card for a placement, or organizer receipt was generated in this review; no weekly slot was selected or used.

The literal public-registry rule is blocked by a hash-verified 17GEMSDOE witness with positive support on all `5,167,373 / 5,167,373` footprint cells. **REGISTRY-MEASUREMENT:** every nonempty in-footprint candidate support has forward overlap `1.0` against that witness, above the user’s `0.70` stop threshold. The overlap branch is sufficient; the Spearman rank correlation against a constant all-positive mask is degenerate/undefined. This one witness is decisive for rejection but is not a fresh exhaustive registry scan. Do not reinterpret the rule, exempt a dense raster, or build an empty/cosmetic file to evade it. Exact pins and scope: [`downloads/current_status.json`](downloads/current_status.json) and [`REPO_REVIEW_20261024.md`](REPO_REVIEW_20261024.md).

The local official 19-band feature stack is absent. The shared evaluator/writer exist, but no new method can be constructed or validated from the current local inputs. Current ranked, **untested** ideas are in [`HYPOTHESES.md`](HYPOTHESES.md); none is viable or score-projected in this state.

## Required work if a future policy/data change removes the blocker

1. Get an explicit policy-owner resolution of the literal full-footprint witness rule. Until then, the correct action is stop.
2. Obtain authorized official inputs and verify source, use terms, hashes, band tags/units, masks, CRS, transform, and grid. Owner-mirror identity is not organizer authentication or redistribution permission.
3. Before a method, rank 3–5 distinct geological hypotheses with layers, physical signature, missing-fault rationale, difference from current code, expected qualitative value/cost, named mimic, and data availability. Then declare one lane.
4. Compare the actual candidate pre-placement surface with registry rasters. Stop when `|Spearman ρ| > 0.90` or more than `70%` of support lies within 3 pixels of one registry raster. Do not use another method’s surface as a substitute.
5. Only if it passes, run the shared buffered whole-segment holdout (`vendor/gems57/evaluate_holdout.py`), derive catalogue features only from visible faults, mask visible faults pixel-exactly, report pooled DTI α=0.2 / β=0.8 / 300 m triangular kernel, withheld-positive count, and 95% CI. Test every feature alone; symmetric AUC >0.90 is a leakage alarm until resolved.
6. Compare the final dots to the registry and validate the exact bytes through the shared writer/automated gates. Produce a JSON run card with every result and explicit `NOT_RUN` / `NOT_GENERATED` where appropriate. Stop after three experiments or two hours.
7. The separate human selector checks the weekly cap and decides whether to use a slot. Only a real submission-page receipt is ORGANIZER-CONFIRMED; development work must not use a slot.

## Carefully qualified historical result context

- `h33-h33-2-b2` is associated in the prompt/repository with **CLAIM 0.2778**. `registry/parents/R0.json` has `receipt: null`; there is no organizer-confirmed score in this checkout. Fixed-budget allocation, spatial thinning, and known-fault avoidance are possible mechanisms, not established causal explanations.
- The prompt’s `0.3195` and `0.4413` leaderboard snapshots conflict. They were not refreshed in this network-restricted session; do not present either as a verified current result or use either as a target without an official receipt/snapshot.
- Saved best local reference: **HOLDOUT-DTI**, evaluator `gems57-pooled-hide-v2`, `22,663` withheld positives, `0.0060451323971729325`, 95% CI `[0.005187022524132649, 0.00692683880217307]` (`evidence/run_card_20261024.json`). It was not rerun in this review, is not a competition score, and the corresponding RELIEF artifact has a negative duplicate verdict.
- Historical SPRINGALIGN, visible-collar, ANASIG, BREAKLINE, STRAINBREAK, SCARPPOL, RELIEF, TIPGAP, and STEPOVER artifacts are retained for audit only. SPRINGALIGN came from upstream PR #42, not this review: **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 22,663 withheld positives, 0.0048650690, 95% CI [0.0040254482, 0.0057850159], paired Δ vs saved best −0.0011800634, 95% CI [−0.0020652571, −0.0003371520]; verdict negative. Its local-only uniqueness pass cannot clear the full-footprint witness. Other saved run cards are linked from [`SLOT_PLAN.md`](../SLOT_PLAN.md).
- DILATATION p10/p12/p15 and SPRINGALIGN filenames carry `20261025`, later than this review date `2026-10-24`. DILATATION provenance/timestamps are unresolved; the SPRINGALIGN run card has no generated timestamp. Keep them archived with a prominent future-dated warning; do not present filename dates as verified generation times.

## Session evidence / review

- Three-pass review: [`REPO_REVIEW_20261024.md`](REPO_REVIEW_20261024.md).
- Current machine-readable status: [`downloads/current_status.json`](downloads/current_status.json).
- Current review run card: [`downloads/current_review_run_card.json`](downloads/current_review_run_card.json).
- Shared site pages: [homepage](index.html), [executive summary](executive-summary.html), [submission guide](SUBMIT.html), [hypotheses](HYPOTHESES.html).
- Final verification after the SPRINGALIGN merge reconciliation: 140 tests passed (17 existing Rasterio pending-deprecation warnings); all 15 served TIFFs passed `scripts/check_site.py`; pinned manifest and parent R0 verification passed; 5 HTML files have no broken local links; all 93 reviewed JSON files parse. See `REPO_REVIEW_20261024.md` for exact commands.
