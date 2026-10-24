# Repository review — 2026-10-24

## Executive decision

**No new TIFF was generated. No current TIFF is cleared for competition submission.** This is a deliberate negative result, not a failed build. The required literal registry rule is stopped by a hash-verified public witness whose positive support covers the entire target footprint: any nonempty in-footprint candidate has 100% forward overlap at zero distance. Emitting an empty raster, changing the threshold, or moving dots outside the footprint would evade the task rather than satisfy it. No experiment or weekly slot was used in this review.

An existing zeros-outside GeoTIFF remains available for **research download only** from the [workbench homepage](index.html). It is format-valid but must not be uploaded. The project now states that distinction prominently on the homepage and submission guide.

## Three review passes

### Pass 1 — inventory and verify the starting point

- Read `README.md`, `SESSION_PROMPT.md`, current review/next-step notes, experiment cards, manifests, hypothesis pages, site pages, tests, and repository history.
- Confirmed the active branch is `arena/664bcef5-gemsdoe92` and started with a clean worktree.
- Confirmed `vendor/gems57/evaluate_holdout.py` and `vendor/gems57/submission_writer.py` are present. The 19-band `training_features.tif` is **not** in `.cache/gems_inputs/`; the folder is absent. The tracked `data/bridge/` files are grid/catalogue/lineage rasters, not the full feature stack.
- Confirmed that `scripts/download_competition_data.sh` and `scripts/prepare_data.py` do not exist in this checkout. `scripts/restore_inputs.py` is a separate GitHub owner-mirror restoration route; it was not run because no candidate can pass the pre-placement stop and mirror identity does not establish official provenance or reuse permission.
- The exact parent `h33-h33-2-b2` is pinned in `registry/parents/R0.json`. Its `CLAIM_score` is `0.2778` and `receipt` is `null`; the ledger has no organizer receipt.

### Pass 2 — scientific, registry, code, and UI audit; correct the defects

#### Why the reported GEMSDOE32 `0.2778` may have occurred

The repository records a lineage H19-5 → D2.8 → SOLO → B2/R0. The pinned R0 raster has 37,654 unit-mass pixels on the competition grid, zero positive mass on the mapped catalogue, minimum catalogue distance 2.236 px, and 2,171 dots within 3 px of it. These are **raster/registry measurements**, not proof of why a competition score changed. The parent record says its original ranking is unavailable; H19-5 is binary at the R0 dots, so it cannot recover a per-dot ranking.

A plausible, unproven mechanism is that spatial thinning reduces redundant prediction mass and pruning/known-fault clearance avoids mass that cannot earn credit. Under an asymmetric, distance-tolerant Tversky-style metric, that can improve precision while preserving coverage. But there is no organizer receipt, controlled ablation under identical scoring conditions, or private target truth in this checkout. We therefore cannot establish causation, call `0.2778` ORGANIZER-CONFIRMED, or promise to beat it. The prompt's `0.3195` and `0.4413` leaderboard snapshots conflict and were not refreshed here.

The official [DrivenData reference solution repository](https://github.com/drivendataorg/gems-prize-reference-solution) was checked through the allowed GitHub API on 2026-10-24. Its README describes a U-Net/Tversky-loss baseline and a CPU-only environment option; it says a GPU is faster, not required. This verifies what that GitHub README says, not the current DrivenData leaderboard, competition data access, or any submission score.

#### Binding uniqueness stop

Existing `REGISTRY-MEASUREMENT` receipts identify the public `17GEMSDOE_E-proba-multiscale` raster and report positive support on 5,167,373 / 5,167,373 target-footprint cells. The receipt is a single decisive witness, not a new full-registry scan. Under the literal rule, every nonempty in-footprint surface and every final in-footprint dot set is therefore 100% forward-overlapping that witness within 3 px. Surface placement is stopped before build; no alternative lane or final-dot placement was attempted.

#### Defects found and fixed

- The homepage headline claimed a “unique download” and its lead paragraph described ANASIG while the `data-primary` card linked SPRINGALIGN.
- `executive-summary.html`, `SUBMIT.html`, `submit.html`, and `SUBMIT.md` did not agree on the current artifact/status. Some wording could make a format-valid research file look eligible to upload.
- `HYPOTHESES.md` and `HYPOTHESES.html` presented already-tested methods as a current untried queue and included numerical expected-DTI projections and unsupported “verified line-by-line” claims. They now list four untested, qualitatively ranked research questions, name layers/signatures/mimics/distinctions/costs, disclose that the feature cache is absent, and mark the hydrography-dependent proposal non-viable until its official data availability and license can be checked.
- The site tests asserted ANASIG on legacy pages but did not assert that the homepage's declared primary, executive summary, and submission guide agreed. The tests and automated site check were tightened to enforce one explicit primary, consistent `DO NOT SUBMIT` wording, and an audit/run card for the exact primary bytes.
- The Makefile initially used system `python3`, which had no NumPy/pytest in this sandbox. The review environment was installed from `requirements.txt`; the Makefile now prefers `.venv/bin/python` when present while still honoring `PYTHON=...` overrides.

#### No new geological experiment

The top untested proposal is paired-profile DEM throw persistence (Band 12 `det_elev` and Band 19 `det_elev_slope`). It was **not** evaluated on holdout: the required feature stack is absent and the registry witness fails before placement. Thus there is no new HOLDOUT-DTI, canary AUC, candidate raster SHA, or submission name/note. The current review run card records nulls rather than inventing values.

### Pass 3 — independent recheck after the fixes

The final checks were run against the edited tree. Pass 3 first exposed four stale site assertions that still treated the archived visible-collar artifact as the current primary or expected obsolete copy. The tests and archive labels were corrected; the final run then passed:

- `make test` (expanded command: `.venv/bin/python -m pytest tests -q`) — **139 passed**, 17 Rasterio/Affine pending-deprecation warnings.
- `make manifest verify ledger` — **PASS**: all eight manifest rasters verified; parent `h33-h33-2-b2` verified (37,654 dots; 5,167,373 footprint pixels); 45 ledger rows, all `UNSCORED`, no best receipt.
- `make site` (expanded command: `PYTHONPATH=vendor .venv/bin/python scripts/check_site.py`) — **SITE CHECK PASS**; all 15 served zeros-outside rasters passed local reread gates, and the explicitly declared SPRINGALIGN research primary matched its audit and negative run card.
- Local-link scan of the five edited HTML pages — **PASS**.
- `git diff --check` — **PASS**.

No new GeoTIFF, ZIP, public-registry cache, or external-data artifact was added. Existing downloads and their bytes remain unchanged; the homepage's archive links and status copy were updated for clarity.

## Source verification and access limits

- **Verified in this review:** GitHub API metadata and the README of the official `drivendataorg/gems-prize-reference-solution` repository. The reference README lists CPU-only support and says training is faster on a GPU.
- **Not refreshed:** DrivenData problem/data/leaderboard/submission pages, USGS GeoDAWN/3DEP/3DHP services, DOE GDR, EPSG.io, and the supplied competition PDF. The sandbox's outbound host allow-list excludes those hosts. The links below are retained for manual review, not described as newly fetched.
- **No DrivenData authentication, upload, weekly-quota check, or organizer receipt** is available to this workflow. No credential was requested or used.
- **Provenance caveat:** the feature/input manifest identifies owner-mirror GitHub pins. Hash equality would verify those mirror bytes only; it would not authenticate the competition download or authorize redistribution.
- **Repository data-use risk:** the public repository tracks competition/grid/lineage rasters and derived GeoTIFFs. Existing `IRREGULARITIES.md` flags that competition redistribution terms have not been checked. No files were untracked or history rewritten in this review.
- Some artifact filenames include a `2026-10-25` suffix while the base commit timestamp is `2026-10-24`. The suffix is preserved as artifact identity; it is not treated as proof of when this review ran.

## Ranked hypotheses

See the maintained shortlist in [`HYPOTHESES.md`](HYPOTHESES.md) and [`HYPOTHESES.html`](HYPOTHESES.html). The qualitative ranking is not a score forecast. None is validated or viable under the current data/registry blockers.

## Highest-value next work

1. Resolve whether full-footprint positive registry rasters are included in the literal rule. Until a policy owner explicitly revises it, keep the fail-closed stop.
2. Obtain authorized competition feature bytes and written/data-use terms; verify the actual file hashes, CRS, transform, tags, and coverage. Do not treat a sibling GitHub mirror as organizer authentication.
3. Once the registry rule permits research to proceed, select one named lane, restore the shared feature stack, test every feature-alone leakage canary, then run the shared buffered whole-segment holdout against comparable controls.
4. Require the paired HOLDOUT-DTI confidence interval to clear the comparable holdout-best bar before any selector considers a slot. This is not a projected live score.
5. Keep pre-placement and final-dot uniqueness checks, automated format gates, and the separate human/authorized slot selector. Capture ORGANIZER-CONFIRMED values only from a submission-page receipt.
6. Review data redistribution terms for already-tracked rasters and decide whether to remove them from the public branch/history; no history rewrite was performed here.

## Machine-readable review card

[`evidence/repo_review_run_card_20261024.json`](../evidence/repo_review_run_card_20261024.json) records the aborted top hypothesis, registry stop, no-build status, and null candidate metrics. It is a negative review card, not a submission record.
