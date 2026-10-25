# Repository review — 2026-10-25 (`797e507a`)

## Executive decision

**OK TO DOWNLOAD FOR RESEARCH. DO NOT SUBMIT.** No new TIFF or geological experiment was generated. The requested new, unique, submission-cleared TIFF **remains unfulfilled**: the unchanged literal uniqueness rule requires stopping before placement for every nonempty candidate. No copied or renamed submission is presented as new. No weekly slot was used or selected.

- [Existing primary GeoTIFF](downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif), inherited from parallel main-branch work, not built or selected here.
- [Automated run card](downloads/review797e_run_card.json), [pre-placement rejection proof](downloads/review797e_preflight.json), [exact-file witness measurement](downloads/review797e_primary_witness.json), [source verification receipt](downloads/review797e_sources.json).
- [Executive submission guide](executive-summary.html) and [form instructions](SUBMIT.html).
- SHA-256: `91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e`.

The inherited filename's `190000Z` time is later than this review's actual UTC time. It is not evidence of a new run or review time. Trust the machine receipt timestamp and hashes, not filename chronology. At session start the primary was COULOMBDM; parallel merge `bbda6c5` changed it to LISTRICDIP. This review retained main's selection, revalidated those bytes, and preserved the initial check under `review797e_prior_primary_witness.json` and `review797e_prior_run_card.json`.

## Pass 1 — inspect, reproduce and implement

Read the README, durable session operating contract, current review and next steps, shared `evaluate_holdout.py`, `submission_writer.py`, literal uniqueness helpers, validator, workflows, manifests and tests. Baseline: **367 tests passed**. The numerical feature cache is not staged in this fresh checkout; the tracked bridge contains the sample grid and catalogue. The prompt's `download_competition_data.sh` and `prepare_data.py` do not exist here; `scripts/restore_inputs.py` is the actual pinned restoration tool. The official reference README explicitly supports CPU-only operation, so “GPU needed” is not an unconditional blocker.

Downloaded the [pinned 17GEMSDOE witness](https://github.com/buffedlizard55-lab/17GEMSDOE/blob/6fc71d19d49dca4960d5434bd81b6dd06fcc030a/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif) through the GitHub blob API. Verified its Git blob SHA-1, SHA-256, single band, CRS, shape and transform against the hash-pinned sample. **REGISTRY-MEASUREMENT:** all **5,167,373** footprint pixels are positive. Any nonempty in-footprint candidate dot set therefore has forward overlap **1.0**, above the **0.70** limit, even at zero distance. This proof does not require creating a candidate or estimating its rank correlation. It is rejection-only, not a complete registry inventory or uniqueness clearance.

Freshly measured existing final dots against the witness: **REGISTRY-MEASUREMENT** overlap **1.0**, Spearman **0.010352227787484035**. Correlation does not undo a failed overlap gate. New surfaces, feature-alone AUCs and HOLDOUT-DTI were **not run**; the protocol says to stop. Three ranked conditional geological proposals are documented in [the hypothesis register](HYPOTHESES_797E507A.md), not implemented or called viable under the stop.

### Publication defect fixed

The prior tests and site gate all passed while several conflicting “newest”/“unique” banners preceded the actual decision. Historical matched-budget claims also described behavior superseded by the literal gate. Passing format checks did not guarantee an obvious truthful first-screen instruction.

Added shared `gems/public_status.py` and `scripts/render_public_status.py`. A **single authoritative rejection panel** is now first in the body of the homepage, executive summary and submission guide. It links the unchanged current primary, describes format validity separately from eligibility, and explicitly says no new unique submission was generated. Historical lane banners remain accessible in a collapsed audit section. `scripts/check_site.py`, used by CI and Pages, fails if the panel is missing, duplicated, stale, edited or buried by another renderer. Primary and input hashes bind the panel to the exact download/reference/catalogue/validator/preflight bytes. No private evaluator or writer fork was created.

## Why the GEMSDOE32 result may be strong — and what is not proven

Freshly retrieved and Git-blob-verified the [GEMSDOE32 page at commit 012e17b](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/012e17b2a115c3c0d5e7885bea625bf9657c99fc/docs/index.html). It describes H33-2-B2 as deleting predictions at catalogue distance at most two pixels from a dotted base. It explicitly says **UNSCORED** and **NO ORGANISER SCORE EXISTS**. Thus the prompt's **0.2778 is USER-REPORTED / UNVERIFIED**, not ORGANIZER-CONFIRMED. The page's own projection is not an observed score. No submission-page receipt was obtained. Prompt leaderboard snapshots **0.3195** and **0.4413** are not verified as current here.

Under the **local** distance-weighted Tversky instrument, truth coverage saturates per truth pixel. Spatially redundant predictions may add false-positive mass with little marginal truth credit; pruning them can help. Removing predictions devoted to already mapped structures can also redirect attention to unseen faults. These are plausible reasons for this family's behavior, not a causal explanation of a private score or proof that all nearby predictions are redundant. Existing metric counterexample tests show that nearby dots can also improve local DTI. Better physical evidence, a locked independent outer spatial test, and reproducible incremental comparisons are needed; optimizing the repeatedly reused surrogate alone risks adaptive overfitting.

**Can a new method exceed the reported score?** Possible in principle; this review supplies no evidence that it does. Neither a format-valid raster nor a HOLDOUT-DTI improvement demonstrates organizer performance. The target is hidden faults relevant to geothermal exploration, not directly vent locations, reservoir temperature or producible fluid flow. Avoid conflating those tasks.

[Official reference repository README](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md) was freshly retrieved and blob-verified. It establishes the baseline workflow and CPU option, **not** an official metric implementation or a score receipt. The template's buffered pooled holdout remains a local surrogate.

## Pass 2 — bugs and edge cases

Regression coverage includes first-in-body ordering on every page, malformed/missing/duplicate gates, truthy non-booleans, stale raster/input hashes, wrong primary/sibling binding, unsafe paths, duplicate markers, idempotent rendering, HTML escaping and prevention of eligibility promotion. Rendering computes every page edit before writing, so a malformed template does not partially update the site. A public run card and evidence mirror must match. Initial post-implementation tests: **392 passed**; later main-branch integration adds the inherited LISTRICDIP tests.

The parallel main merge was explicitly reconciled rather than changing lanes. The initial COULOMBDM receipts were retained, and a new exact-file measurement was generated for inherited LISTRICDIP. Raster bytes and historical scientific results were not changed.

## Pass 3 — complete request check and limitations

Final verification results are recorded in `downloads/review797e_verification.json`. The site checker reopens **all served zero-outside TIFFs**, not merely the current primary; no manual pixel inspector is needed. Both strict format validation and rejection status must pass before publication. Shared manifests, parent proof and ledger checks remain separate gates. No experiment or slot was used.

### Ordered next steps

1. **Do not build another nonempty candidate under the unchanged literal rule.** Only an explicit future protocol change can resolve the universal dense-witness conflict; silently redefining dense rasters or switching to matched budgets is not permitted. Automation has already made the rejection decision; this is not a request for human pixel inspection.
2. Once permitted and assigned one lane, test only the top pre-registered operator, using shared cache/evaluator/writer, individual leakage canaries, whole-segment buffered visible-only features, exact masks, pooled DTI, withheld counts and paired spatial uncertainty. Freshly rerun the current control on the same instrument; do not compare static/full-catalogue and fold-visible scores as if interchangeable.
3. Lock an outer spatial test before further tuning. The many adaptive experiments on the same catalogue holdout make its nominal uncertainty insufficient as an estimate of final generalization.
4. Obtain authoritative data-use/licensing confirmation and authenticated submission receipts through a permitted channel. Owner-mirror hashes are not legal/provenance authorization. Do not commit new competition input stacks to this public repo.
5. Diagnose Pages configuration drift. The Pages API reported `build_type: legacy` and an errored legacy build, despite an Actions deployment workflow. An attempted API change to `workflow` returned **403 Resource not accessible by integration**. This is a repository-integration permission limitation, not a request for credentials. No setting was changed and no live-site refresh is claimed merely from local tests. Confirm the post-merge Actions deployment separately.

### Source access boundary

This sandbox can reach GitHub, npm and PyPI hosts only. It cannot retrieve the current DrivenData leaderboard/data/form, USGS/GDR landing pages or NLR rules PDF directly. Official pointers remain available for later review: [competition/problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/), [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [INGENIOUS GDR](https://gdr.openei.org/submissions/1391). They are **not described as freshly verified here**. No authenticated account access, private test labels or organizer receipt is available. This review does not claim line-by-line certification of the entire inherited repository or all sibling sites.


## Pass 3 integration addendum — parallel false clearance quarantined

While CI was queued, main advanced to `71f6ac4` (including `406638a`). That incoming change introduced alternate “SUBMIT NOW” / “SUBMISSION READY” pages, a new root validator and a promoted run card. They contradicted the unchanged literal gate. The incoming card's size, grid transform and shape order were incorrect. Its SHA-256 was correct; the older inherited KNICKLOQO documentation had the stale hash. An interim review attribution of the hash problem to the incoming card was incorrect and is corrected here. Its assertion of a score improvement was not an organizer receipt. The root validator called shared APIs with missing arguments, caught errors as warnings, and still printed “READY FOR SUBMISSION” with a forecast.

This review preserved the incoming card verbatim in `evidence/review797e_superseded_knickloqo_card.json`, replaced its **public operational** version with a fresh format-valid **negative** card, and explicitly left holdout values null/not rerun. The new alternate HTML pages now receive the same authoritative first-in-body rejection panel; their inherited claims are collapsed as superseded history. Incoming markdown claims are similarly prefaced and archived. The root validator now delegates to shared strict gates and returns a non-success exit for the literal submission stop; validation exceptions cannot become success. Regression tests cover both format outcomes, errors and the corrected public card. The actual KNICKLOQO TIFF is 149,177 bytes, not the incoming card’s 123,456-byte claim. The existing LISTRICDIP primary was not changed. No geological experiment or new TIFF was generated. Historical review links from parallel work remain available at `REVIEW_20261025_REPOSITORY_REVIEW.md`.


### Final integration verification

After integrating parallel research additions through main `d6f7ac0`, **404 tests pass**, all **70 served zero-outside TIFFs** pass fresh site validation, and parent/manifest/ledger/public-status checks pass. Five public HTML entry pages have the authoritative panel first. No new TIFF, holdout or competition slot was generated in this review. See the final verification receipt for implementation hashes.
