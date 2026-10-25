# Repository review — 2026-10-25 UTC

**Scope:** code, committed evidence, site wiring, and reproducible checks at the pre-integration checkout headed by `4441f6a`. No geological experiment was run, no new raster was generated, and no competition slot was used. The lane-specific code audit below covers `RADIOCONTACT`; it does not re-evaluate the geology or scripts of other lanes. While this PR was being prepared, `origin/main` advanced to `bbda6c5` and added the separate `LISTRICDIP` lane. The merge resolution retains those upstream changes; the `LISTRICDIP` result is therefore newer in the integrated tree and is not audited in this RADIOCONTACT-focused report. This review does not independently verify claims on external websites or submission receipts.

## Executive decision

**Do not upload any current artifact as a competition submission.** The newest lane in the pre-integration checkout (`RADIOCONTACT`) has a recorded DTI result that is not protocol-valid for the requested hide-and-recover comparison, its public-registry scan is absent, and its method-level uniqueness stop is not enforced. In the integrated repository, the binding literal witness is positive across every footprint cell; therefore any nonempty in-footprint prediction raster has **REGISTRY-MEASUREMENT** overlap `1.0`, exceeding the `0.70` stop. This alone disqualifies every current nonempty candidate under the stated protocol. The upstream LISTRICDIP addition also labels its result `negative` and `submission_eligible: false`; the authoritative current repository review provides the latest lane status. No evidence here demonstrates that any local candidate beats the organizer's score for `h33-h33-2-b2` or the leaderboard.

The **recorded** `RADIOCONTACT` result is `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, 22,663 withheld positive pixels, stored 95% CI `[0.003638, 0.006583]`), but this review rejects it as a valid estimate under the project protocol for the reasons in Finding 1. It must not be used for promotion. It is not `ORGANIZER-CONFIRMED` and is not a competition score. The run card's local result and static validation result remain useful for debugging only.

## Findings (ordered by decision impact)

### 1. Critical — RADIOCONTACT holdout prediction uses the full catalogue at placement time

**Locations:** `scripts/build_radiocontact_submission.py`, `build_holdout_terms`, `strict_rule2_terms`, and the emission step in `main` (current code around lines 101–135 and 225–235).

The deployment raster is placed once using `cand = valid & ~cat & (d_cat > 2.0)`, where `cat` and `d_cat` are computed from the complete catalogue. `build_holdout_terms` then evaluates that same prebuilt `dots_arr` in every withheld-segment fold. The `strict_rule2_terms` diagnostic applies a visible-fault distance mask after the same full-catalogue placement; it does not reconstruct the prediction from that fold's visible faults. Thus withheld segment locations influence which candidate pixels were eligible before scoring. RADIOCONTACT has no catalogue-derived *geophysical surface feature*, but its candidate mask and emission support are catalogue-derived and were not fold-local.

This fails the requested hide-and-recover protocol: for each fold, derive catalogue-based candidate masks/features from the visible faults only; withhold entire buffered components; mask visible fault pixels exactly during scoring; and pool the fold scores. The stored `HOLDOUT-DTI` is therefore **not accepted as a compliant holdout result**. Reuse `vendor/gems57/holdout.py`, `evaluate_holdout.py`, the shared writer, and the existing stack; fix the fold-specific prediction path in the shared lane/template code, then rerun and version the evidence. Do not alter or privately fork the metric/evaluator.

### 2. High — the promotion comparison mixes two different instruments

**Location:** `scripts/build_radiocontact_submission.py`, around lines 338–340.

The code sets `beats_rule2 = primary["dti"] > HOLDout_BEST_RULE2`, but `primary` is the static `d_cat > 2.0` result while `HOLDout_BEST_RULE2` is the strict draw-blind, fold-visible benchmark. It separately calculates `beats_static` against the static threshold, but does not use that value in the verdict. This is dimensionally inconsistent decision logic and could incorrectly block or promote a future candidate. Define named, same-instrument promotion comparisons: static versus static and strict fold-visible versus strict fold-visible, with paired intervals computed on the same folds. Keep the current fail-closed behavior until the evaluator issue above is repaired; do not treat a code-level fix as scientific validation.

### 3. High — reported uniqueness is not complete under the supplied stop rule

**Locations:** `compare_to_local`, `dual_reading`, and the verdict block in `scripts/build_radiocontact_submission.py`.

The RADIOCONTACT run card says its public scan is unavailable and records only its local registry. Its duplicate decision uses matched-budget overlap and Spearman correlation, while the lane rule requires the literal share of candidate dots within three pixels of a registry raster. It also checks only after placement; there is no surface-level registry comparison before placement. Thus its `duplicate: false` local result is not a global uniqueness pass. In the integrated repository, the pinned `17GEMSDOE E-proba-multiscale` witness is reported positive across the full footprint (5,167,373 cells); every nonempty in-footprint candidate therefore has literal forward overlap `1.0` with that witness and must stop under the unchanged `0.70` rule. This is a **REGISTRY-MEASUREMENT** result documented in `docs/REVIEW_376A8469.md` and the authoritative review; the full public registry scan remains incomplete. Do not reinterpret matched-budget overlap as clearance.

### 4. High — historical site sections make status auditing harder than necessary

At the pre-integration review point, the README, lane banners, and `data-primary="true"` link described different candidates. The incoming `LISTRICDIP` merge updates the README and current primary to that lane's artifact and explicitly marks it negative / not submission-eligible; this **supersedes the stale-primary observation** from the initial review. The site still contains many stacked historical lane banners. Preserve one unambiguous latest-status summary and move old “newest/current” summaries under an archive label. Do not designate a candidate as upload-ready unless its exact bytes pass the compliant holdout and registry gates.

### 5. Medium — pre-registration chronology is inconsistent

`docs/HYPOTHESES_20261026_RADIOCONTACT.md` says it is a pre-registration for 2026-10-26, but the corresponding run card and TIFF are timestamped 2026-10-25 (`20261025T041646Z`). The file name/date alone does not prove that the hypotheses preceded the build. Preserve this as an unresolved chronology irregularity; do not describe the document as proven pre-registration until timestamped evidence or a corrected, traceable sequence establishes that ordering.

### 6. Medium — repository cleanliness and provenance need an explicit policy

The committed site serves many GeoTIFFs and evidence files, and the repository tracks small bridge raster data. The current checkout does not contain `training_features.tif`, full training labels, or the full cached feature stack; those paths are described in code as `.cache/gems_inputs`. Availability of a served TIFF and a green format gate does not establish permission to redistribute the source-derived raster, organizer provenance, score quality, or uniqueness. Review the source/licensing and artifact-publication policy before adding further rasters or changing download labels.

## Verified checks in this review

- **TEST:** installed the pinned project dependencies into the ignored `.venv`; after the latest main sync (`e1c2ad9`), `404 passed` under `pytest` (126 Rasterio pending-deprecation warnings; no test failures).
- **PUBLIC STATUS / FORMAT SITE GATE:** after that sync, `scripts/render_public_status.py --check` passed and confirmed byte-binding/status order on all entry pages; `scripts/check_site.py` passed and re-read all `70` served `*-zeros.tif` files against the committed bridge grid/catalogue. The designated primary remains the LISTRICDIP research TIFF; it is explicitly not cleared by the literal overlap gate. These are local technical checks, not competition acceptance or proof of public-registry uniqueness.
- **PARENT PROVENANCE:** `make manifest` passed for the committed pinned artifacts. `make verify` reproduced the pinned parent `h33-h33-2-b2` byte hash and reported 37,654 dots. This verifies the committed parent artefact against this repository's recipe; it does not verify the owner-reported `0.2778` score.
- **COMPETITION SCORE:** No submission receipt was found or produced by these checks. The user-provided `0.2778`, `0.3195`, and `0.4413` are not treated as `ORGANIZER-CONFIRMED` evidence in this review.

## Ordered next work

1. Repair RADIOCONTACT's fold-local candidate support and use the shared hide-and-recover evaluator exactly as specified. Add synthetic tests proving that withholding a component changes only the visible-fault support and that no full-catalogue distance mask enters a fold prediction.
2. Correct the same-instrument promotion gate and test it with controlled static/fold-visible examples.
3. Run each feature-only leakage canary before trusting the feature. AUC above 0.90 is a stop pending a leakage investigation.
4. Compare the continuous surface against the registry **before placement**, then compare final dots. Report the exact raster(s), Spearman rank-correlation, 3-pixel dot overlap, method, and registry coverage. If a comparison exceeds the configured stop threshold, log the duplicate and stop that lane.
5. Obtain and scan a complete, current public registry or explicitly keep uniqueness `NOT VERIFIED`. Do not infer uniqueness from a local scan.
6. Rebuild the run card and validator receipt from the corrected run. Only then decide whether a slot selector should consider it. This review does not select a submission or spend a weekly slot.

## Sources / manual verification links

These are references supplied in the project prompt; this review did not fetch or certify their live contents:

- DrivenData competition rules: https://www.drivendata.org/competitions/306/competition-doe-gems/
- DrivenData problem description: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Competition data tab (login may be required): https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- Competition reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- USGS GeoDAWN record: https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7
- GDR / INGENIOUS submission: https://gdr.openei.org/submissions/1391
- EPSG:32611: https://epsg.io/32611

## Review card

The machine-readable card is `evidence/repo_review_20261025.json`. It distinguishes a recorded-but-invalid `HOLDOUT-DTI` from a valid holdout result and records the current artifact's SHA-256 and local format-gate status without asserting public uniqueness or organizer confirmation.
