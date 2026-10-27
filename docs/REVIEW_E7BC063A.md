# Repository review — 27 October 2026 (e7bc063a)

## Executive decision

**DO NOT SUBMIT. No new competition TIFF was generated or cleared.**

The [nine-site executive summary](focus9.html) already lists the exact historical research downloads, reported results, estimate availability and measured uniqueness failures for GEMSDOE24, 25, 27, 28, 30, 31, 32, 33 and 36. It is a pinned historical comparison, **not a live feed**. The new [final machine-readable project review](downloads/review_e7bc063a_final_run_card.json) records the reproducible engineering checks and a fresh rejection proof.

GEMSDOE32's `h33-h33-2-b2` **0.2778 CLAIM** is the highest reported value in that nine-site comparison. There is no authenticated organizer receipt binding that number to a file. No defensible per-file leaderboard estimate is available. Neither 0.3195 nor 0.4413 is asserted to be the current leaderboard best.

### Why a new eligible TIFF cannot be produced under the current instructions

**REGISTRY-MEASUREMENT:** independently fetched the pinned [17GEMSDOE witness](https://github.com/buffedlizard55-lab/17GEMSDOE/blob/6fc71d19d49dca4960d5434bd81b6dd06fcc030a/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif) using the existing shared fetcher. Its Git blob and SHA-256 match the pins. It is positive on all **5,167,373 finite sample-footprint cells**, on the same grid. Every nonempty in-footprint candidate therefore has candidate-directed overlap **1.000 > 0.70**, even without dilation. The literal stop applies before any new candidate surface or dot placement. A renamed file, altered metadata, random perturbation or an empty raster does not satisfy the scientific and submission requirements.

The prompt also references an assigned single-method paragraph but supplies no distinct assigned lane. The existing [five ranked hypotheses](HYPOTHESES_20261026_SITE_REVIEW.md) remain a conditional screen; their top candidate, LOCAL-WAVENUMBER-CONSENSUS, is **not assigned, implemented or evaluated by this review**. No score gain or absolute geological novelty is claimed. External-data candidates are not viable until actual study-area coverage and acquisition are verified.

**HOLDOUT-DTI: not run**; evaluator version, withheld-positive count and CI are null. No leakage canary, geological experiment, final-dot check or weekly-slot selection occurred. This is a negative protocol audit, **not a falsified geological hypothesis**. No policy exception was assumed.

## What was improved

Added `scripts/review_project.py`: one fixed-plan, rejection-only command to reproduce:

1. The shared pinned-witness proof and current historical research-file validator.
2. The complete test suite.
3. Input manifest hashes and parent identity.
4. All served research-raster format checks and site/evidence consistency.
5. Generated nine-site page, prior evidence-card and review-banner freshness checks.
6. Working-tree whitespace checks.

The command records real child exits, durations, stdout/stderr hashes and bounded diagnostic tails. It kills the process group on timeout, applies an overall engineering-check budget, and installs a complete JSON receipt atomically without overwriting prior evidence. It uses the existing shared audit/validators; no private evaluator, training code or submission writer was introduced. New-candidate SHA/name/format fields are null; the old VARIO file's byte-bound validation and identity are explicitly nested as a **historical research reference**.

```sh
# After installing requirements.txt in .venv:
.venv/bin/python scripts/review_project.py \
  --fetch-witness \
  --output .cache/review-$(date -u +%Y%m%dT%H%M%SZ).json
```

Exit **1** means all engineering checks passed **and the confirmed protocol STOP remains**. Exit **2** means failed/incomplete checks or inconclusive evidence. Neither means permission to submit. Existing receipt paths are never overwritten. The command does not access the leaderboard, restore the large feature stack, train, create a raster or select a slot. Network use is limited to the optional existing pinned GitHub witness fetcher. Ignored caches and the virtual environment may need restoration in later workspaces.

## Three-pass record

### Pass 1 — independently reproduce the existing result

Read README and `SESSION_PROMPT.md`, reviewed the shared evaluator/writer paths, historical comparison, ranked hypotheses and prior review. Installed repository requirements in ignored `.venv/` because system Python is externally managed. Baseline engineering verification: **720 tests passed**, with 159 Rasterio pending-deprecation warnings. Independently fetched the pinned witness and wrote [fresh preflight evidence](../evidence/review_e7bc063a_preflight.json). Manifest and parent checks passed. Site validation passed for **123 served research rasters**. These engineering counts are not scientific scores.

### Pass 2 — implementation review and edge cases

Added regression tests covering genuine child failures, missing executables, process timeout, expired total budget, truthy/malformed audit fields, changed witness proof, nonfinite JSON, existing-file/dangling-symlink preservation, and fetch confinement to ignored cache. Historical file identity was moved into its own nested reference so it cannot be mistaken for a new TIFF. The wrapper intentionally never emits successful submission clearance. A second review caught that plain `git diff --check` ignores staged changes; the fixed check compares against `HEAD` so both staged and unstaged tracked changes are covered. The [first complete check receipt](downloads/review_e7bc063a_run_card.json) is preserved rather than overwritten.

### Pass 3 — full-request reconciliation

The final machine receipt records actual outcomes of the complete fixed check plan after these changes: **743 tests passed** (159 Rasterio pending-deprecation warnings), manifest and parent verified, **123 served research rasters** gated, all four generated page/card/banner checks passed, and staged plus unstaged whitespace checks passed. All nine engineering checks exited 0; the overall audit correctly exited 1 for the confirmed protocol STOP. No scientific experiment or claimed score was fabricated to satisfy an impossible gate. The executive summary remains generated from pinned evidence, with explicit research-only download labels and unavailable estimates. The new command reduces repeated manual verification while preserving the binding stop and the separate future selector.

## Scientific interpretation and next work

R0's lineage sparsifies H19-5-derived D2.8 predictions and excludes a catalogue-distance collar. Reducing redundant predicted mass under a 300 m triangular-credit kernel is a plausible explanation for its reported advantage, **not controlled causal proof of the claimed organizer result**. Fault-prospect prediction also does not establish the existence of a geothermal vent. The [organizer reference repository](https://github.com/drivendataorg/gems-prize-reference-solution) is the accessible official code source; the [competition task](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [USGS GeoDAWN record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) and [GDR INGENIOUS 1391](https://gdr.openei.org/submissions/1391) are review links, not fresh source retrievals in this session.

Next work, in dependency order:

1. An authorized protocol decision must resolve the dense-probability-versus-dot-registry conflict and assign a single distinct method lane. Do not silently substitute a sparse-only or matched-budget rule.
2. Establish official input provenance and permitted use. The ignored owner-mirror cache and its historical pin audit do not authenticate organizer origin or redistribution rights. No large-stack restoration was needed for this rejection-only run.
3. If legitimately unblocked, pre-register the lane and rebuild catalogue features from visible faults within buffered whole-segment holdouts. Reuse the shared pooled evaluator (`alpha=0.2`, `beta=0.8`, 300 m triangular kernel). Run feature-only leakage canaries; AUC above 0.90 remains an alarm until explained.
4. Require a paired holdout improvement over a control rebuilt under the same evaluator/folds, with evaluator version, withheld-positive count and 95% CI. Check surfaces before placement and final dots against a complete pinned registry. Revalidate exact downloadable bytes.
5. Resolve the outside-footprint convention with the organizer: historical local downloads use finite zeros, while archived official instructions describe null/NaN outside bounds. A local PASS does not establish portal acceptance. No authenticated competition interface is available here to establish current slot limits or record score-to-file receipts.
6. Only a separate authorized selector can promote an eligible candidate, verify the weekly cap and retain its organizer receipt bound to SHA-256. No slot was spent here.

**Maximize P(Win):** preserve slots rather than label unvalidated work high-scoring. **Own the Outcome:** make the incompatibility, evidence and next dependencies explicit instead of presenting a duplicate as a new submission.
