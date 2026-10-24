# Research and candidate review — 2026-10-24

## Executive decision

**No new raster was built and no competition slot was touched.** This is a deliberate fail-closed decision, not a claim that the goal is complete. The top candidate below needs the pinned 19-band feature stack, but that stack is absent from both `data/` and `.cache/` in this checkout. The official DrivenData data page is the named source; it is login-gated according to the project record. The owner-mirror source is not a substitute for the official file because its redistribution terms have not been established. Consequently, a fresh holdout score, feature-only leakage canary, and novel TIFF cannot honestly be produced here.

The existing primary download passes the project's local range/geometry preflight and is **OK TO DOWNLOAD FOR REVIEW**, but **NOT CLEARED / NOT RECOMMENDED for competition submission**. It breaches the literal uniqueness gate against parent R0. In addition, the official problem page states that data outside the submission bounds should be null/NaN, while the served zeros-outside raster stores zero there. No organizer receipt resolves whether that encoding is accepted. Local preflight must not be described as official format acceptance, uniqueness clearance, or promotion.

## What the cited score does and does not tell us

`h33-h33-2-b2` is the parent raster associated with the prompt-cited **CLAIM 0.2778**. The checked-in parent record says `receipt: null`; the local ledger has no organizer receipt for that entry. Thus we cannot verify the score, its exact evaluation context, or that its reported position was actually highest on the named site. The prompt also gives two different public leaderboard highs, **0.3195** and **0.4413**; neither is treated here as ORGANIZER-CONFIRMED.

The parent construction is documented as a fixed-budget, spaced H19-5 ridge-supported prediction with catalogue exclusion. Those choices are *plausible* contributors under a tolerance-kernel DTI: a sparse prediction budget can avoid redundant false-positive mass while nearby predictions receive partial spatial credit. But no available experiment isolates those design choices, so that explanation is a mechanistic hypothesis, not a causal account of the claimed live score. The only way to confirm a live result is an organizer submission receipt copied into the ledger.

Manual-review sources:

- Competition problem, metric and task definition: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- Competition about/resources page: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/>
- Official training/submission files (login may be required): <https://www.drivendata.org/competitions/306/competition-doe-gems/data/>
- Organizer reference implementation: <https://github.com/drivendataorg/gems-prize-reference-solution>
- Organizer rules PDF: <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
- USGS GeoDAWN data record: <https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7> · DOI: <https://doi.org/10.5066/P93LGLVQ>
- DOE GDR INGENIOUS record: <https://gdr.openei.org/submissions/1391>

**Freshly checked during this review:** DrivenData problem page 967, About page 968, and data page. The problem/About pages loaded; the data page redirected to DrivenData login. The official problem page explicitly specifies a single-layer float32 GeoTIFF, values in [0,1], EPSG:32611, 100 m resolution, same bounds, and null/NaN outside bounds. The official data page did not expose files without login. USGS/OSTI/DOE GDR pages and the rules PDF were not fetched in this review; their current content, access status and licensing terms remain unverified here.

## Official competition information checked in this review

The DrivenData **problem page** and **About page** were retrieved during this session; the **data tab** redirected to the login page. Verified from the current official text:

- The challenge targets geological faults indicative of geothermal resources; the initial test faults were manually identified by experts and are not contained in the public USGS database. This is the organizer's stated setup, not evidence that any local candidate finds a new fault.
- The distance-weighted Tversky metric uses a triangular kernel with 300 m support, α=0.2 and β=0.8. The official metric gives partial distance credit; it does not imply that a named parent raster achieved a particular score.
- The official submission-format text requires a single-layer float32 GeoTIFF, predictions in [0,1], EPSG:32611, 100 m resolution, matching bounds, and null/NaN outside those bounds.
- The served p12 zeros-outside encoding differs from that stated outside-bounds requirement. The project currently checks its all-finite range/geometry properties, but has no authenticated submission validation or organizer receipt. Treat the mismatch as a hard format uncertainty; do not submit this file.
- The official data page redirected to login; the full `training_features.tif` was therefore not obtainable through that page in this session.

## Candidate hypotheses: five testable hypotheses

These are candidates not found as completed experiment arms in this checkout's builders, tests, evidence, or ledger. That is a bounded repo audit, **not** a claim that no sibling GEMSDOE site or other competitor has tried them. Rankings below are qualitative research priorities, not score projections. “Expected gain” means scientific plausibility only; no numeric gain is forecast.

| Rank | Candidate and project layer(s) | Physical signature to test | Why it may find catalogue-missing faults | Difference from implemented experiments | Expected DTI potential / cost | Data status and named mimic |
|---:|---|---|---|---|---|---|
| 1 | **Extensional-strain coherence** — competition feature stack Band 8 `geod_dilaterate`, Band 7 `geod_shearrate`, Band 4 `geod_2ndinv`; repository band names from `vendor/gems57/geo.py` and DILATATION builder | Positive volumetric dilation that is high relative to local shear / second-invariant strain, evaluated as a continuous, robustly normalized ratio rather than a Band-8 high-tercile threshold | An opening-dominated strain patch is a plausible permeability proxy for blind normal-fault splays beneath cover; the discriminant attempts to separate extension from generic high-strain corridors | Existing DILATATION arms select by Band-8 quantile and use bands 7/4 as leakage-canary variables, not as a joint extensional-coherence prediction score | **Highest within the active DILATATION lane; unknown expected score. Medium cost.** | Needs the missing official 19-band stack. Mimics: groundwater/brine extraction subsidence and broad basin-fill deformation without brittle faults. **Not viable for validation until official stack bytes are available and hash-checked.** |
| 2 | **Scale-persistent magnetic analytic-signal ridges** — Bands 1–3 TMI / horizontal-gradient content, with Bands 5/13 gravity context | Orientation-tolerant analytic-signal amplitude maxima that persist across several smoothing scales and have coincident gravity support | Buried fault damage or juxtaposed units can create geophysical edges despite no mapped Quaternary scarp | Existing SNAP blends supplied edge responses; no multiscale persistence/analytic-signal experiment is identified in the checked-in builders or ledger | **Unknown; potentially useful but not ranked above active-lane work. Medium-high cost.** | Needs the same missing competition stack. Mimics: dikes and lithologic contacts. Not tested. |
| 3 | **Concealed basin hinge curvature** — Band 13 gravity anomaly plus Band 15 depth-to-basement / Band 12 detrended elevation | Sign-consistent second derivative or curvature hinge, conditioned on low relief and basement-depth transition | Intra-basin and basin-margin structures can be concealed by alluvium and absent from surface-fault inventories | Existing RELIEF uses terrain-position ranking and other arms use first-order edge/gradient proxies; no controlled gravity-curvature candidate is recorded | **Unknown; medium cost.** | Needs the missing competition stack. Mimics: sediment compaction, lithologic density boundaries and nontectonic basin geometry. Not tested. |
| 4 | **Cross-scale DEM curvature-break persistence** — Band 12 detrended elevation plus Band 19 detrended slope | A paired profile/plan-curvature break whose orientation and sign persist across scale, not simply high relief or slope | Subtle buried/partly mantled normal-fault scarps can leave a geomorphic break that is not in the existing catalogue | Existing RELIEF uses elevation terciles; curvature helper code exists in `vendor/gems57/geo.py`, but no corresponding tested submission arm was found. This is not wholly novel code; the novelty would be the calibrated, scale-persistent submission test | **Unknown; medium cost.** | Needs the missing competition stack. Mimics: erosional scarps, shorelines, terrace risers and lithologic contacts. Not tested. |
| 5 | **Radiometric alteration residual** — Official USGS GeoDAWN K, eU, eTh layers, normalized against local lithology/relief and tested only as independent corroboration | Local radiometric ratio/residual anomaly and edge concordance, rather than raw K/Th/U level | Hydrothermal alteration may change near-surface radiometry around permeable systems even where the fault trace is not mapped | No radiometric output arm is in the checked-in builders/ledger; geophysical/terrain candidates do not use radiometric residuals | **Unknown; high data/provenance cost.** | Official source to check: USGS GeoDAWN record / DOI above. Although a hash pin is mentioned in historical manifests, the external raster is not present here and the USGS page was not fetched in this review; current obtainability was **not verified**. Do not call this candidate viable until source bytes and redistribution/usage terms are checked. Mimics: bedrock composition, weathering and non-geothermal alteration. |

### Validation choice and holdout status

Candidate 1 is the top research candidate because it stays in the active DILATATION lane, uses layers already named by the project, and tests a distinct physical contrast instead of another dose of the existing Band-8-only allocation. However, it cannot be generated from the available files. No input values were imputed, no substitute data were downloaded, and no holdout metric or leakage AUC is claimed for it. This means the requested top-candidate holdout validation is **blocked**, not passed. No slot was spent.

Before any future build, the authorized official feature stack must be staged locally and verified against an approved manifest. Then run, in order: (a) single-feature and composite leakage canaries on buffered whole-segment folds; (b) pre-placement surface rank-correlation and final-dot overlap against a refreshed registry; (c) the shared `gems57-pooled-hide-v2` pooled DTI evaluator with paired spatial-cluster 95% CI; (d) the shared submission writer and format validator. Any rank-correlation above 0.90 or more than 70% of final dots within 3 px of a registry raster means log duplicate and stop. A positive holdout is necessary but not proof of private/live score.

## Measured existing-file disposition

All values in this subsection labelled **HOLDOUT-DTI** are from `gems57-pooled-hide-v2`; 22,663 catalogue positives were withheld in the cited pooled run. They are local hide-and-recover results, never organizer scores.

- Parent R0: **HOLDOUT-DTI** 0.004006, 95% CI [0.003424, 0.004690].
- DILATATION p12: **HOLDOUT-DTI** 0.005779, 95% CI [0.004863, 0.006851]; paired change vs R0 **HOLDOUT-DTI** +0.00177, 95% CI [+0.00111, +0.00246].
- DILATATION p12 versus registry raster R0: Spearman 0.879132 on the finite submission footprint, and 99.373241% of candidate dots within 3 px (both registry measurements, not scores). The overlap exceeds the protocol's 70% stop threshold. Verdict: **duplicate / negative for promotion** despite the positive catalogue holdout. `scripts/check_site.py` now calculates this parent-R0 screen automatically; it reports a format PASS separately from `PROMOTION BLOCKED`.
- Reproducible review card: [`evidence/review_run_card_20261024.json`](../evidence/review_run_card_20261024.json). It clearly marks the p12 holdout as inherited evidence and the proposed new strain-coherence experiment as `BLOCKED_NOT_RUN`.
- Existing TIPGAP FAR: **HOLDOUT-DTI** 0.002723, 95% CI [0.002324, 0.003131], below R0; it clears the recorded R0 dot-overlap gate at 67.00% but is a negative local result. The scan's stated scope is local and does not certify global uniqueness.
- The project's site checker independently re-read all five served `*-zeros.tif` files and passed format gates during this review. That is **format validation only**, not uniqueness clearance or organizer acceptance.

The published DILATATION p12 zero-outside raster SHA-256 is `25ba17a26d31df9d574fba2a2f34d03ff58f587f4ffde092dcc4bba9822f8898`. It is downloadable as a format-test artifact, but do not interpret that as a recommendation to use a weekly competition slot.

## Irregularities and limitations to resolve

1. **Conflicting project state:** earlier `SESSION_PROMPT.md` text called TIPGAP FAR the current deliverable while README/site made DILATATION p12 primary. The session file now separates TIPGAP history from the current review scope; both records remain in the repository.
2. **Contradictory recommendation:** an existing README table says DILATATION p12 “promote” despite later prose and the site saying its 99.37% overlap is a duplicate. The table is corrected in this change.
3. **Duplicate submission guides:** `docs/SUBMIT.html` and `docs/submit.html` previously gave opposite answers. The lower-case page now redirects to the canonical guide; both README and HTML status distinguish local preflight from official-format uncertainty and the slot recommendation.
4. **Official format discrepancy:** the live official problem page says data outside the submission bounds should be null/NaN. The project's portal-range-oriented diagnostic files instead store zeros outside. Neither a successful submission receipt nor an authenticated form-validation result is present to resolve this; no current raster is certified for submission.
5. **Date provenance:** the repository's primary filename and run evidence contain `20261025`, later than this review date (2026-10-24 UTC). This may be a date/clock or imported-artifact irregularity; no artifact was renamed and no creation-date claim is made.
6. **Data terms / provenance:** pinned rasters are present in the checkout while registry notes describe some competition inputs as gitignored and terms as unchecked. Review data redistribution rights before publishing or retaining those input rasters. This review did not delete or rewrite historical data.
7. **No organizer evidence:** no receipt is available for the cited 0.2778 claim or current public highs. Leaderboard improvement remains unknown.
8. **No autonomous upload:** this repository cannot authenticate to DrivenData, consume a submission slot, or record a receipt. Upload remains a competitor-account action.

## Sources and scientific judgement

The DrivenData problem and About pages were fetched during this review; the data page redirected to login. The organizer's GitHub reference solution was also fetched. The rules PDF and USGS/OSTI/GDR sources were not fetched in this review; their links remain for manual review, and their current contents/access/licensing are not claimed as verified. The repository preserves input hashes, but a hash verifies bytes, not organizer provenance or license. The scientific hypotheses are testable mechanisms, not established site-specific observations. A positive catalogue holdout indicates recovery of withheld catalogue structure under the local instrument; it does not by itself demonstrate discovery of an uncatalogued geothermal vent or fault.
