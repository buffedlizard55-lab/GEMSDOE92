# Three-pass repository review — d97f969e, 2026-10-24

## Decision first

**OK TO DOWNLOAD FOR RESEARCH; DO NOT SUBMIT.** [Existing APRONRIDGE GeoTIFF](downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif) remains downloadable. It is not newly generated in this review. Zero candidate experiments and zero competition uploads occurred. No previous TIFF was copied or relabeled as new.

The request supplies no identifiable single method paragraph after “your lane is the single method paragraph below.” This review stays in verification-only scope; it does not invent a geological lane. The duplicate-stop protocol takes precedence over generating another raster.

## Pass 1 — verify the inherited blocker

Read the repository operating contract, README and next steps. Restored the Python environment in an ignored virtual environment using the existing requirements. The data-placement/GPU blocker described in the prompt is obsolete for this checkout: mirrored sample, fault labels and prior predictions are already present. `make manifest` verifies eight pinned files; `make verify` proves the parent artifact. Mirror hashes authenticate bytes, not organizer provenance.

Downloaded the immutable [17GEMSDOE witness Git blob](https://api.github.com/repos/buffedlizard55-lab/17GEMSDOE/git/blobs/374c88b1da2b803e2ed160de467fd71ae114010d) and ran the existing shared `scripts/check_public_witness.py`. The command exits 1 deliberately for a duplicate, not a failed download. [Fresh measurement](downloads/review_d97f969e_witness.json) records:

- REGISTRY-MEASUREMENT: all 5,167,373 footprint cells positive in the witness; candidate forward overlap 1.0, Spearman 0.05623747382008243.
- Candidate SHA-256 `1a29a5d81e8561954f04a563b4975cb84d00898b8d7634700a9d409a10e06cbc`.
- Witness SHA-256 `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`, verified Git blob `374c88b1da2b803e2ed160de467fd71ae114010d`.
- No NaN anywhere in candidate, values in [0,1], zero outside footprint, one band, CRS/shape/transform match reference.

This is one decisive rejection-only witness, not a fresh full-fleet scan or a pre-placement pass. Because this witness covers the whole footprint, every nonempty in-footprint candidate would fail the same positive-support overlap test. Stop before building or placing new dots. Do not reinterpret dense values as sparse dots without an explicitly revised protocol.

## Pass 2 — review scientific and presentation assumptions

Found conflicting primary declarations and incorrect “#1” claims. APRONRIDGE is retained as the existing standalone research download; retaining a link is not selection for a real slot. Historical HOLDOUT-DTI (`gems57-pooled-hide-v2`, 22,663 withheld positives):

| Method | Historical HOLDOUT-DTI | 95% CI | Source |
|---|---:|---|---|
| APRONRIDGE free1d | 0.008354 | [0.006823, 0.010135] | `evidence/apronridge_run_card.json` |
| HYDROCONDUIT f45hydro | 0.008549 | [0.007626, 0.009487] | `evidence/hydroconduit_run_card.json` |

The second point estimate is larger, so the homepage's overall-best claim was false. Overlapping intervals also do not establish a significant paired difference. Corrected the headline and added a superseding status notice to the README, homepage, executive summary, current review and next steps. Historical reports remain for audit, not as current instruction.

These static evaluations were not rerun here. Existing documentation admits use of full-catalogue distance exclusions in static evaluations; those are not interchangeable with the requested fold-by-fold visible-only experiment. No static improvement is certified here as a fully compliant hide-and-recover promotion gate. No fresh leakage canary or fold-rebuilt experiment was run because the prior uniqueness gate already requires stop.

### Why the reported GEMSDOE32 result may have improved

The verified parent has 37,654 unit dots, no catalogue mass, and a minimum catalogue distance of 2.236 pixels. The inherited lineage analysis attributes gains to thinning redundant ridge detections and avoiding already mapped faults. Under pooled distance-weighted Tversky, redundant predictions can add false-positive mass without adding proportional recovered truth; spacing can therefore improve the objective. This is a plausible mechanism, not proof of why hidden organizer labels produced the reported result. See [existing detailed lineage analysis](ANALYSIS_20261024.md). The reported 0.2778 and conflicting leaderboard values are unverified user/history claims, not ORGANIZER-CONFIRMED measurements. No claim is made that a candidate will exceed them.

### Research queue, not implementation authorization

No new hypothesis is implemented after the stop. Existing repository lanes already cover scarps, piedmont aprons, hydrothermal alteration, magnetic edges, spring alignment and stepover geometry; calling these new would mislead. Before the next experiment, pre-register a distinct named method, rank 3–5 genuinely untried hypotheses against the complete lane inventory, and run the pre-placement registry test. New official external data must have a verified obtainable source and usage terms before being called viable. This review does not claim that blocked external sources were obtained.

## Pass 3 — automated verification and source scope

Baseline full test suite: 199 passed. Final suite with two new regression tests: 201 passed (103 Rasterio/Affine pending-deprecation warnings). `make manifest`, `make verify`, and `scripts/check_site.py` pass; the site validator checks all 25 served TIFFs, not just the primary. Added a regression test for the corrected top-level status notices. All original raster bytes are unchanged. Final test results are recorded in the PR.

The [official DrivenData reference repository](https://github.com/drivendataorg/gems-prize-reference-solution) root listing was checked live through GitHub. This verifies its availability only; it is not a new line-by-line review of its notebook. Network access here is limited to GitHub and package registries. These official links are for review, **not freshly fetched/verified content**:

- [Competition problem and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Competition data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [GDR INGENIOUS data](https://gdr.openei.org/submissions/1391)
- [Rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

No authenticated DrivenData session, submission receipt, current quota or live leaderboard is available here. GitHub merge publishes repository changes; it neither uploads to the competition nor proves a live Pages deployment.

## Next session, in order

1. Resolve the protocol's dense-support impossibility explicitly; do not silently exempt probability maps or declare global uniqueness from sparse-only tests.
2. Establish one method lane and a common fold-rebuilt baseline. Recompute all catalogue-derived features only from visible segments, buffered appropriately; score with pixel-exact visible masking and shared evaluator/writer.
3. Run feature-alone leakage canaries and paired confidence intervals; keep static and fold-rebuilt instruments distinctly labeled. Compare against the best baseline under the same evaluator, not an inherited incomparable number.
4. Generate a new TIFF only after pre-placement clearance; independently validate final bytes and final registry overlap. Stop at three experiments or two hours.
5. Separate scientific promotion from the selector and its live weekly quota. Preserve organizer receipts if a cleared candidate is eventually submitted. No score guarantee is scientifically defensible.
