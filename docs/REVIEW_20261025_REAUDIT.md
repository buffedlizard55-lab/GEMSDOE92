# Repository re-audit — 2026-10-25

## Decision

**Latest artifact: format-valid and OK TO DOWNLOAD FOR RESEARCH. DO NOT SUBMIT.** No new GeoTIFF, experiment, slot selection, or organizer score was produced in this review. The latest pre-existing research artifact is `DRAINAGE_KNICK`; its local holdout is below the current repository holdout-best and the literal public-registry rule stops it. A submission-cleared file cannot be produced under the binding protocol while the pinned full-footprint witness is included.

- [Download the existing DRAINAGE_KNICK research TIFF](downloads/gemsdoe92-drainageknick-20261025T120000Z-zeros.tif) — download is for research, **not submission**.
- [DRAINAGE_KNICK run card](downloads/gemsdoe92-drainageknick-20261025T120000Z_run_card.json) · [automated audit](downloads/gemsdoe92-drainageknick-20261025T120000Z-audit.json) · [analysis](ANALYSIS_20261025_DRAINAGE_KNICK.md).
- Competition name, record-only: `GEMSDOE92-DRAINAGE_KNICK-20261025`.
- Record-only form note (131/140 characters): `h33-h33-2-b2; DRAINAGE_KNICK: terrain-knick persistence x basement edge x shear; 37654 dots d_cat>2px; see run card for HOLDOUT-DTI`.
- GeoTIFF SHA-256: `ef6c27e34fe0f28c6e52615a9fc9601c20ada5337203def25ab8753392aef910`.

## Pass 1 — state and evidence review

Read `README.md`, `SESSION_PROMPT.md`, `docs/REVIEW_CURRENT.md`, the 376a protocol-gate review, the latest run card, site validator and test contracts. The durable prompt is already in README and is linked to `SESSION_PROMPT.md`.

The user-supplied scores `0.2778`, `0.3195`, and `0.4413` are claims/snapshots, not organizer receipts in this checkout. The prior pinned-GitHub review of GEMSDOE32 says its own page labels its result UNSCORED. No DrivenData receipt or live weekly-slot cap is present. Therefore this review does not infer a competition result or claim that a local holdout exceeds any leaderboard score.

The latest artifact's recorded **HOLDOUT-DTI** is `0.0617276004 [0.0470464759, 0.0753160429]` (`gems57-pooled-hide-v2`; 22,663 withheld positives; strict fold-visible `d_visible > 2.0`; 1000-draw paired spatial-block bootstrap CI). It does not beat the saved repository holdout-best `0.113316` under that instrument. This is local hide-and-recover evidence, not a leaderboard score or proof of geothermal discovery.

The run card reports **REGISTRY-MEASUREMENT**: 106 local rasters, worst local 3-pixel forward overlap `0.47732`, worst local absolute Spearman `0.063413`; the public scan compared 747 rasters but had 705 download failures and was explicitly incomplete. Its literal witness is `17GEMSDOE_E-proba-multiscale`, overlap `1.0`; there were 71 reported public overlaps above 70%. Thus no global uniqueness clearance is justified. Independently, the pinned witness in `evidence/review376a_preflight.json` is positive in every footprint cell, so any nonempty in-footprint candidate necessarily fails the literal 70% forward-overlap gate. The current protocol says to stop at that result.

The existing DRAINAGE_KNICK TIFF's recorded format validation says single-band float32; EPSG:32611; shape 3730×3292; matching sample transform; no NaN or infinity; values in [0,1]; zeros outside footprint; and 37,654 positive cells. The automated site gate re-read all served TIFFs against local sample/catalogue rasters. This establishes local format validation only, not organizer acceptance or eligibility.

## Pass 2 — bugs, omissions, and corrections

### Finding: current status was not first or reliably prominent

The homepage began with an older KNICKLOQO status block and contained the latest literal-rule stop farther down. Its test and site checker required warning phrases anywhere in the HTML, so an obsolete warning could satisfy the contract while the most prominent status was stale. That weakens the user's key requirement that download-vs-submit status be obvious immediately.

**Fix:** Added a canonical current-status banner at the top of the homepage, explicitly linking the latest research TIFF while stating **OK TO DOWNLOAD FOR RESEARCH / DO NOT SUBMIT** and explaining the universal literal-overlap stop. The site validator and regression tests now require this banner to precede the historical lane blocks and link to the exact expected file. Historical records remain intact.

### Specification and model-governance findings

- The single named method paragraph required by the parallel protocol is not clearly designated in the current prompt; this review did no new geological method work rather than silently picking a lane.
- A cached numerical feature stack is not staged in the checkout. `data/bridge/` contains grid/catalogue/label bridge files and previous rasters; `.cache/gems_inputs/` is not present. Do not claim a fresh model run from cached features.
- The repository contains substantial sequential holdout tuning. A locked outer spatial test is needed before treating best-of-many local holdouts as an unbiased promotion estimate.
- Current public scan of DRAINAGE_KNICK is incomplete. The full-footprint pinned witness alone is sufficient for rejection under the literal rule, not for exhaustive uniqueness certification.
- Automated format validity does not imply uniqueness, superior holdout, a valid weekly-slot choice, or organizer acceptance.

### Conditional candidate hypotheses (not implemented; no score projections)

These are candidate *research ideas* from the preceding protocol review, ranked by potential distinctness and cost; none is viable for placement under the unchanged duplicate stop. They could reuse GeoDAWN magnetic/DEM layers only after the input cache is restored and band provenance is verified. No additional external dataset is proposed; availability of the required cached layers is not established in this checkout.

| Rank / qualitative expected incremental HOLDOUT-DTI value / implementation cost | Layers and target signature | Why it may reveal an uncatalogued fault | Distinction from existing repo methods | Main non-fault mimic / falsification |
|---|---|---|---|---|
| 1 / potentially high / high | Band 2 RTP magnetic texture; bidirectional local-window registration, with a consistent along-strike step in best-fit texture displacement | A buried lateral splay can offset inherited magnetic texture without preserving a surface scarp | Tests displacement/kinematic restoration, not amplitude, tilt, Hessian, Euler-depth, or phase ridges | Separate lava/intrusive contacts; reject single-contact matches and require held-out texture restoration plus window-scale stability |
| 2 / medium / medium | Band 2 RTP; persistent connected-component/hole topology across locally standardized thresholds; paired topology change across a trial line | A low-amplitude offset may split a magnetic domain even when gradient strength is weak | Topological persistence rather than derivative-ridge or Euler-source-depth scoring | Remanent volcanic domains and survey seams; compare to seam controls and amplitude-matched null lines |
| 3 / low-to-medium / high | Band 12 DEM; neighboring-basin divide migration residual jointly with basin hypsometry and opposite-side channel steepness | Distributed deformation may tilt drainage divides after erosion erases a discrete scarp | Basin-integrated geomorphic imbalance, not local scarp, stream-offset, shoreline, or conduit-alignment features | Lithology, drainage capture, precipitation; require consistent sign in neighboring independent basins and test matched lithology/relief controls |

Expected HOLDOUT-DTI improvement is unknown. Current feature-stack availability and exact band provenance were not reverified in this review. If the gate is explicitly revised, restore and hash-verify the template inputs, freeze a comparable control and locked outer spatial test, test every feature alone for leakage, and use the shared buffered whole-segment hide-and-recover evaluator. Do not run these ideas while the literal gate still requires stopping.

## Pass 3 — recheck and acceptance

Revalidated current repository state with the declared dependency pins (temporary ignored `.venv`):

- `python -m pytest tests -q`: **367 passed**, 126 upstream Affine pending-deprecation warnings.
- `PYTHONPATH=vendor python scripts/check_site.py`: **PASS; 63 served GeoTIFFs gated** against the bridge sample grid/catalogue.
- `python -m gems manifest --manifest registry/data_manifest.json --data-root data`: PASS.
- `python -m gems parent --recipe registry/parents/R0.json --data-root data`: pinned parent verified.
- `python -m gems ledger`: 93 rows; best receipt none.
- `git diff --check`: PASS.

These are software and format checks. No holdout was rerun; the cited holdout, public scan, and file hash are transcribed from the existing DRAINAGE_KNICK evidence and not recertified as new measurements. No external non-GitHub official page was live verified in this environment.

## Official sources for follow-up / manual review

Links from the durable project prompt; live availability/authentication was not verified in this review:

- [DrivenData problem statement](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [About](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/) · [Data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) · [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) · [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [USGS GeoDAWN catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [GDR INGENIOUS #1391](https://gdr.openei.org/submissions/1391) · [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) · [EPSG:32611](https://epsg.io/32611)

**Maximize P(Win):** do not spend a weekly slot on a negative holdout or a literal duplicate. **Own the Outcome:** surface the negative status at the top, preserve the downloadable research artifact, and report precisely why no submission-cleared TIFF can be offered under the current protocol.
