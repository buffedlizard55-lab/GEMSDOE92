# Repository review — 2026-10-27

## Executive decision

**DO NOT SUBMIT any current research download. No new TIFF was generated.**

The [nine-site executive summary](focus9.html) contains the requested per-site download, reported result, estimate availability, and uniqueness table. Its source inventory is historical, not a live leaderboard feed. GEMSDOE32's `h33-h33-2-b2` **0.2778 CLAIM** is the highest supplied result among those nine. There is no organizer receipt available here to confirm it. Neither the conflicting user snapshots 0.3195 and 0.4413 nor a local holdout establishes today's leaderboard best.

## Pass 1 — reproduce rather than inherit clearance

Installed `requirements.txt` in ignored `.venv/` (system Python is externally managed). Ran:

```sh
.venv/bin/python -m pytest tests -q
.venv/bin/python scripts/audit_readiness.py --fetch-witness --output docs/downloads/review_a3dcc0dd_run_card.json
.venv/bin/python scripts/check_site.py
```

- Engineering verification: **636 tests passed**, 141 rasterio pending-deprecation warnings, no test failures.
- Engineering verification: **SITE CHECK PASS**, 123 served research rasters gated; primary remains VARIO full.
- **REGISTRY-MEASUREMENT:** re-fetched hash-pinned witness; confirmed universal in-footprint directed overlap **1.000**, exceeding **0.70**. Audit exit **1** means confirmed rejection, not tool failure. The [fresh run card](downloads/review_a3dcc0dd_run_card.json) includes hashes and actual local validator results.
- **HOLDOUT-DTI: not run**, evaluator/positive count/CI null. No geological experiment, surface, dots, leakage canary, or weekly slot was generated/used. This is a protocol rejection, not a falsified geological hypothesis.

## Pass 2 — contradictions and missing requirements

The session prompt's former opening recommended executing SALEMSEISMO despite subsequent audit findings disabling its runner. Added a current, overriding start block to prevent that unsafe handoff. Historical evidence is retained rather than rewritten.

The literal registry rule and the requirement to generate a qualifying nonempty unique TIFF are jointly unsatisfiable with the verified witness. A new filename, metadata change, raster perturbation, sparse-only interpretation or zero raster would not solve this scientific/validation problem. No agent should silently waive the rule.

No distinct lane method paragraph is assigned in this request. The [five ranked hypotheses](HYPOTHESES_20261026_SITE_REVIEW.md) remain a conditional screen, not permission to adopt another session's lane. LOCAL-WAVENUMBER-CONSENSUS remains top screen priority; no performance estimate or claim of novelty beyond the documented code review is added here. External-data candidates remain not viable until actual AOI coverage and acquisition are verified.

## Pass 3 — original-request reconciliation

- Easy research downloads, nine-site comparison and future-only submission guide already exist in [focus9](focus9.html); no file is newly cleared.
- Finite [0,1], no in-footprint NaN and matching CRS/shape/transform are local format gates, **not** uniqueness, leaderboard performance, organizer acceptance or scientific discovery of geothermal vents.
- The task predicts fault prospects; sparse fault predictions do not independently identify geothermal vents.
- Plausible explanation of R0's reported result: sparsification and catalogue-distance filtering may reduce redundant prediction mass under distance-tolerant scoring. Without hidden labels or controlled organizer receipts, its causal score advantage and a higher-score guarantee cannot be established.
- No credible leaderboard estimate is available. Owner-claim regression and family-contaminated row-wise validation are not acceptable substitutes for prospective evidence.
- Official source URLs and the prior source-verification boundaries remain in the executive summary. This session verified GitHub access to the [organizer reference repository](https://github.com/drivendataorg/gems-prize-reference-solution); it did not retrieve official competition pages, the rules PDF, authenticated data, current cap, or live leaderboard. Sandbox outbound access is restricted; no receipt or source freshness is invented.

## Next work, in dependency order

1. An authorized protocol revision must explicitly resolve whether a dense probability raster is a dot registry entry. Until then retain the literal stop. Do not silently replace it with a matched-budget test.
2. Assign one distinct method lane; restore hash-pinned inputs using the existing shared restore path, documenting owner-mirror versus official provenance.
3. Only if allowed, build the top method with buffered whole-segment, fold-visible-only features and per-feature leakage canaries; compare against a control rebuilt under the same evaluator and folds. Retain negative results.
4. Check the complete registry on surfaces before placement and final dots after placement; validate exact downloadable bytes and outside-footprint convention against current organizer requirements.
5. Promotion remains a separate selector action within the verified weekly cap. Store organizer receipt and SHA-256 before calling any score ORGANIZER-CONFIRMED.

**Outcome:** safety/evidence review completed; requested new submission remains blocked, not completed. Maximize P(Win) means not spending a slot on unvalidated evidence; Own the Outcome means exposing this incompatibility plainly.
