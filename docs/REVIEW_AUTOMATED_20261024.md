# Automated repo review — 2026-10-24 UTC

## Decision first

**OK TO DOWNLOAD existing format-valid research TIFFs. DO NOT SUBMIT.**
**No new unique TIFF was generated; no experiment or weekly slot was used.**
The user's literal duplicate-stop gate is binding. This review does not waive
it, exempt dense rasters, or spend compute building an inevitably blocked file.

The current downloadable research artifact is SPRINGALIGN, not ANASIG.
Its inherited name contains `20261025` even though this review is dated
2026-10-24. Those bytes already existed at checkout. Historical names and
receipts are preserved, not relabeled as a new submission.

## What was actually verified

The public 17GEMSDOE E-proba blob was downloaded again through GitHub's API.
Its Git blob SHA-1 matches `374c88b1da2b803e2ed160de467fd71ae114010d`;
SHA-256 matches `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`.
The new instrument verifies the reference, witness and candidate have the same
CRS, exact transform, dimensions and single-band count before comparing them.

**REGISTRY-MEASUREMENT:** the witness is positive on every one of the
5,167,373 finite reference-footprint pixels. Its 3-pixel halo therefore covers
the entire footprint. The existing SPRINGALIGN file has forward overlap 1.0,
Spearman 0.04372948694731268. Overlap alone requires rejection. For any
nonempty candidate whose support is within the footprint, every predicted
pixel is necessarily within the witness support. This proves a universal
stop under the stated rule; it does **not** prove geological equivalence.
An empty prediction or predictions outside the footprint are not loopholes.

[Fresh rejection receipt](downloads/review_20261024_springalign_witness_v2.json) ·
[Review run card](downloads/review_20261024_run_card.json).
This is a single witness, not a refreshed full public inventory. The actual
SPRINGALIGN pre-placement surface was not rerun; no substitute surface was
used. Since final-dot rejection is decisive, no pre-placement pass is claimed.

## Why the reported GEMSDOE32 result might have worked

**CLAIM 0.2778**, supplied in the prompt, is not ORGANIZER-CONFIRMED here.
The GEMSDOE32 HTML source was retrieved from its GitHub repository. That
snapshot has no `0.2778` string and explicitly says no organizer score exists
for its artifacts. This may be a stale page; it neither verifies nor disproves
the user's subsequent result. The page's projected value is labeled MODEL,
not a receipt. The prompt's leaderboard values are conflicting, unrefreshed
CLAIMs; no current winning model can be inferred from them.

The pinned parent is locally verified as a spaced/pruned off-catalogue subset
of earlier skeleton-derived predictions, with 37,654 positive pixels. A
reasonable **mechanistic hypothesis**, not a demonstrated causal explanation
of the reported score, is that fewer redundant/off-target predictions retained
most distance-weighted true-positive credit while reducing false-positive
mass. In the shared evaluator, writing T for weighted true positives, F for
weighted false positives and N for withheld positives gives

`DTI = T / (0.2 T + 0.2 F + 0.8 N)`.

Holding T and N fixed, decreasing F improves this metric. However pruning can
also reduce T; its net effect depends on unknown private labels. More dots,
more vent proximity, or a novel filename need not improve competition score.
The positive/negative transfer between catalogue hide/recover and SGMC controls
in prior runs makes that uncertainty material, not cosmetic. Higher performance
is possible in principle, but not established by this review or by a local
holdout result alone. Fault mapping is the model target; direct geothermal
vent discovery is an application, not a verified label definition here.

## Ranked conditional research queue (not executed)

No separate single-method lane paragraph was supplied in this request. This
session stayed in the queued **registry-validation/review** lane and stopped.
The following conceptual extensions are ranked by qualitative expected utility
relative to implementation cost, not projected DTI numbers. They are not claims
of global novelty across all GEMSDOE sites. Existing code and hypothesis
records were checked; some are extensions of earlier conceptual proposals,
not wholly new ideas. **All are blocked by the universal registry stop.**

| Rank | Hypothesis and specific existing layers | Physical signature and missing-fault rationale | Distinction from implemented methods / mimic | Expected utility / cost / data boundary |
|---|---|---|---|---|
| 1 | Cross-profile step model selection: Band 12 `det_elev`, Band 19 `det_elev_slope` | Fit an offset-step plus background slope against a smooth channel cross-section across candidate breaks; require consistent offset polarity along strike. A same-lithology alluvial fault may lack magnetic contrast or a catalogue trace. | BREAKLINE uses magnitude/coherence; SCARPPOL uses fall-line derivatives. Neither implements a step-versus-channel likelihood fit in the checked modules. Lake benches and terrace risers still mimic it. Earlier reviews proposed related antisymmetry tests; do not claim this entire idea is new. | Highest qualitative priority for rejecting a known DEM mimic, improvement unknown; medium cost. Uses pinned stack after restoration; no new external dataset proposed. |
| 2 | Offset continuation of magnetic edges: Band 14 `tmi`, Band 12 elevation | Estimate ridge tangents on each side of a DEM discontinuity and test paired lateral displacement versus continuous-edge null. Seek a fault cutting, rather than coinciding with, a lithologic magnetic contact. | ANASIG scores ridge strength; this uses displaced edge correspondence across the break, not pointwise fusion. Intrusions and gridding seams mimic offset edges. | Unmeasured moderate potential; high cost, sensitive to native resolution. Existing stack only; band product derivation must be checked before trusting polarity. |
| 3 | Gravity residual across a matched terrain boundary: Band 13 `iso_grav_anom`, Band 12 elevation | Fit gravity against elevation/long-wavelength trend using training blocks only, then seek coherent residual jumps crossing a low-relief piedmont. Buried density contrasts can persist without a mapped surface scarp. | GRAVCrest's direct signed/gradient crests failed; this is a nuisance-conditioned residual hypothesis, not another crest threshold. Basin-fill or lithologic changes remain a mimic. | Lower confidence after failed gravity screens; medium/high cost. Existing stack; nuisance model and normalization must be trained within each fold. |
| 4 | Relief-normalized spring-alignment null test: existing GDR spring table plus Band 12 elevation | Compare SPRINGALIGN line votes with conditional random locations matched on local relief/elevation to reject topographic clustering. A residual line may indicate a blind permeable structure. | SPRINGALIGN counts spring-pair votes; this explicitly tests a conditional discharge/topography null. Paleochannels and lithologic contacts still mimic a residual. | Low priority given the recorded negative SPRINGALIGN result; medium cost. Restore the pinned spring table only if its mirror and reuse provenance can be verified. No new official access is claimed. |

These are technically specified but **not presently viable for promotion**.
The feature stack is not in this checkout's cache; restoring a mirror does not
prove official authenticity or license. No external shoreline, thermal satellite,
or earthquake dataset was proposed as obtainable: official non-GitHub endpoints
are outside this environment's allowed outbound hosts. The first experiment
must wait for protocol resolution, then test each feature alone on the common
holdout, with symmetric AUC >0.90 treated as leakage until explained. Derive
catalogue-dependent features from visible faults only. Reuse the common
`vendor/gems57/evaluate_holdout.py` and `submission_writer.py`; no private
metric or evaluator fork was created.

## Source/provenance table

| Source | Verification this review | What it supports / does not support |
|---|---|---|
| [DrivenData reference README](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md) | Retrieved via GitHub API at pinned commit | Official reference supports CPU training; a GPU is faster, not an absolute training requirement. Data must be obtained separately. |
| [DrivenData reference notebook](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb) | Retrieved and code cells inspected | U-Net, Monte Carlo patch splits, training TverskyLoss alpha 0.2 / beta 0.8. Does not establish our stricter segment holdout, the official 300 m scoring kernel, or any leaderboard value. |
| [GEMSDOE32 site source](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/docs/index.html) | Retrieved; content hash pinned in source audit | Owner's method description and download URLs, not an official competition receipt. Rendered Pages endpoint not fetched. |
| [17GEMSDOE witness blob](https://api.github.com/repos/buffedlizard55-lab/17GEMSDOE/git/blobs/374c88b1da2b803e2ed160de467fd71ae114010d) | Downloaded, byte/hash/grid checked and compared | Rejection under the literal registry rule; not geological ground truth. |
| [Competition problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) | Not retrieved this review | Retained official URLs for later review; no new claim about login behavior, live scores, quota or portal acceptance. |
| [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [GDR INGENIOUS](https://gdr.openei.org/submissions/1391), [NLR rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | Not retrieved: host restriction | Source leads, not freshly verified availability, license or factual citations. |

Exact source hashes: `evidence/review_20261024_source_audit.json`.
Owner mirrors are not trusted official provenance simply because their bytes hash.

## Three review passes

1. **Implementation:** reretrieved decisive witness; hardened the rejection-only
   checker using template overlap/rank helpers; verified exact primary bytes;
   corrected stale/mixed primary names, false uniqueness language and conditional
   submission instructions. Historical artifacts remain unchanged.
2. **Bug/edge review:** tests cover wrong CRS, transform or band count, empty
   candidate/witness, out-of-footprint mass, NaN/infinity/out-of-range values,
   rank-only rejection, hash mismatch, strict JSON and historical-receipt
   overwrite protection. Missing/corrupt primary JSON now yields site failure
   rather than an unbound-variable/JSON parsing crash.
3. **Requirements/reliability review:** synchronize guides and main status,
   retain negative artifacts, enforce site gate in CI and before Pages upload,
   audit source claims, and record the unfulfilled unique-TIFF request explicitly.
   No confidence interval, canary, score or new geological discovery is invented.

## Next session / limitations

1. **Policy conflict is the blocker**, not TIFF serialization: an authorized
   protocol revision must specify dense-surface versus sparse-dot comparisons
   before further placement. This agent has not made that revision.
2. Verify official data provenance and public redistribution terms; restore
   pinned feature inputs only if authorized. The request's
   `download_competition_data.sh` and `prepare_data.py` are not in this checkout;
   `scripts/restore_inputs.py` is the actual mirror-restoration entry point.
3. After clearance, pre-register one hypothesis and its null; use the common
   buffered whole-segment holdout, canaries and paired uncertainty versus the
   comparable holdout best. Limit to the requested experiments/time budget.
4. Maintain separate off-catalogue controls and capture an organizer receipt
   only after a selector clears exact bytes and confirms the current weekly cap.
5. Network access is restricted to GitHub/package registries. Official external
   data, current portal/quota and leaderboard could not be refreshed. No account
   credentials are needed in chat. CPU-based work is possible; a GPU is not the
   sole blocker nor a guarantee of competitive performance.

### Verification record

- Pass 1 baseline: 138 tests passed; the site gated 15 served TIFFs.
- Pass 2 caught an existing contract requiring the explicit BREAKLINE duplicate
  warning in the canonical guide. Restored the warning rather than weakening
  the test. Added wrong-dimension cases and consistent-guide/deployment tests.
- Pass 3: **165 tests passed**; 95 Rasterio/Affine pending-deprecation warnings
  (nonfatal). `scripts/check_site.py` passed for all **15** served TIFFs.
  All **8** input-manifest hashes and `make verify` parent proof passed.
  `git diff --check` passed. These are software/format checks, not model scores.
- The new witness CLI returned **exit 1** and saved a negative receipt, as
  intended for a binding overlap stop. No historic receipt or raster was changed.
- GitHub Pages API initially reported legacy publishing from `main:/` while
  the workflow uploads `docs/`. This is a deployment-setting mismatch; publication
  status/configuration will be checked separately from local format validity.

### GitHub publishing permission finding

The attempt to align Pages with workflow publishing returned HTTP 403,
`Resource not accessible by integration`. No Pages setting changed: the API
still reports legacy publishing from `main:/`. This is a GitHub integration
permission limitation, not a TIFF/model validation failure. The repository's
Pages workflow exists and has historically succeeded, but this review cannot
claim the legacy publisher is governed by the new workflow gate. Branch CI
validates this patch; Pages configuration requires separate repository-admin
access. No GitHub password or token is requested or stored.
