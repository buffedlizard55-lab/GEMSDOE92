# Repository review — session 918b947a

## Decision: OK TO DOWNLOAD FOR RESEARCH; DO NOT SUBMIT

**No new unique TIFF was generated in this review.** The requested fresh, submission-cleared artifact remains unfulfilled. This is a binding protocol stop, not a request for human pixel inspection. No model experiment, candidate surface, placement, competition upload, or slot selection was performed.

The existing [COULOMBLOQO research TIFF](downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif) remains available. Its bytes were independently re-read, not copied into a newly named submission. [Current run card](downloads/review_918b947a_run_card.json) · [pre-placement proof](downloads/review_918b947a_preplacement.json) · [exact-file witness test](downloads/review_918b947a_primary_witness.json) · [source verification](downloads/review_918b947a_sources.json).

## Pass 1 — inspect and reproduce

Read README, SESSION_PROMPT, current review, shared evaluator/writer/uniqueness implementation, current primary receipts, and repository hypothesis history. The request does not supply an unambiguous single assigned method paragraph; no new geological lane was assumed.

Retrieved the pinned public witness from GitHub, verified both Git blob identity and SHA-256, and matched its CRS, shape and affine transform against the byte-pinned sample. **REGISTRY-MEASUREMENT:** all 5,167,373 footprint cells are positive. For any nonempty candidate support A contained in the footprint, every a in A is itself in the witness support; distance is zero and forward overlap is exactly 1.0, exceeding the 0.70 limit. No geology-dependent surface or dot placement can change this result. This is a sufficient single-witness rejection, **not** a new full-registry scan or a measured correlation for an unbuilt surface.

**REGISTRY-MEASUREMENT, existing primary only:** forward overlap 1.0; full-footprint Spearman 0.0630200233025519. The low correlation does not override the overlap stop. This mathematical degeneracy is not evidence that every geological method is scientifically a duplicate. The literal rule nevertheless requires stopping. No dense-map exemption, nonzero threshold adjustment, sparse-registry substitution, zero raster, random jitter or renamed copy was used to evade it.

## Scientific answer: why the reported GEMSDOE32 result might improve

The supplied GEMSDOE32 value is an **unverified owner-reported claim**, not an ORGANIZER-CONFIRMED receipt. Likewise the prompt supplies conflicting leaderboard claims; none was refreshed here. They cannot establish which model currently leads or guarantee a higher result.

The repository's recorded lineage removes redundant skeleton predictions and then catalogue-adjacent predictions. Under the shared local metric, truth coverage is a maximum of triangular kernels, while false-positive cost accumulates. Removing a redundant dot can preserve truth coverage while reducing false-positive cost. Removing catalogue-adjacent dots can avoid spending prediction mass in locations that do not recover unseen faults. These are plausible explanations for the reported improvement, **not a causal attribution verified on private labels**. The zero-XOR lineage and local parent are checked by the repository's existing tests; organizer-score ablations are absent.

Two corrections matter scientifically:

- The [official reference notebook at immutable commit](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb) confirms the training-loss coefficients, not the distance-weighted scoring implementation. It is not evidence that the entire local evaluator is organizer-certified. The live problem page and rules PDF could not be retrieved on the available network.
- There is no universal optimal-spacing theorem at 2.8 pixels. Two nearby dots can cover different truth pixels and increase DTI; their false-positive cost depends on distance to truth. Kernel redundancy is a geometry-dependent marginal calculation, not a binary spacing rule.

The site's former all-time-best static HOLDOUT-DTI claim was too broad: it excluded the recorded visible-collar result. Different feature provenance and different eligibility masks also make the static and fold-visible instruments non-interchangeable. This review therefore removes the blanket ranking; stored historical holdout results are not rerun or newly certified leak-free. Recovering mapped fault segments is a useful instrument, but is not proof of discovering geothermal vents, permeable fractures, or commercially productive reservoirs.

## Ranked conditional geological hypotheses (not experiments)

These are qualitative research priorities, **not score projections**. A source-code review found no implementation of the exact operators below in this checkout; novelty across every sibling repository is not established. None is viable for placement under the current stop. No new external data is required in principle, but the pinned feature stack is not staged here. Restore it with the existing `scripts/restore_inputs.py` only after governance permits another experiment and data-use terms have been established. The old brief's `download_competition_data.sh` and `prepare_data.py` do not exist in this repository.

| Rank | Specific layers / operator | Missing-catalogue mechanism (hypothesis) | Difference from implemented lanes | Named non-fault mimic | Expected incremental value / cost |
|---|---|---|---|---|---|
| 1 | B12 `det_elev`: DEM-derived drainage graph; detect repeated, same-signed lateral offsets of independent channel crossings along a proposed line; require matched upstream/downstream curvature | Young oblique-slip strands may offset drainage without a persistent scarp or potential-field contrast | HYDROCONDUIT uses ridge/monotonicity and fluid corroboration; this uses a graph of paired channel crossings and signed displacement consistency, not slope magnitude | Stream capture and alluvial-fan avulsion | Uncertain, potentially complementary / high; coarse grid may erase the target |
| 2 | B2 `rtp`: complex oriented wavelet phase winding around lineament termination, persistent over scale, controlling amplitude | Buried fault splays may terminate a magnetized contact without producing a strong terrain edge | COULOMBLOQO uses RTP tilt, troughs, Hessians and axial agreement, not a complex-phase winding/topological-defect statistic | Intrusion tips and terminating volcanic-flow contacts | Uncertain / medium; source nonuniqueness is substantial |
| 3 | B12 `det_elev`: explicitly fit a shoreline null using constant-elevation contour persistence and closed-contour topology, then test residual cross-contour scarp continuity | Rejecting pluvial terraces could expose weak tectonic traces masked by stronger nontectonic linear features | Prior coherence/step/piedmont gates mention shorelines as a mimic; this explicitly compares a tectonic trace against a fitted shoreline null rather than rewarding another edge | Warped paleoshorelines, terrace risers and DEM datum seams | Uncertain, mainly false-positive suppression / medium; risk of deleting genuine along-contour scarps |

If unblocked, validate the first hypothesis with the shared hide-and-recover evaluator, deriving any catalogue context from visible faults only. Test every constituent feature alone for the leakage canary before model combination. Use identical fold masks, fixed budgets, pooled terms and a paired spatial bootstrap against the best **comparable** baseline. Preserve a negative result if the improvement is not established. No weekly slot may be used merely because a hypothesis sounds plausible.

## Pass 2 — repairs and edge cases

- Hardened the existing shared preflight utility, not a private fork: it now pins the sample's exact SHA-256 before trusting its footprint, records UTC time / implementation hash / scope, rejects absent CRS, and refuses to overwrite earlier evidence. Missing, corrupted or mismatched inputs remain inconclusive, never clearance.
- Hardened site receipt checks: empty or missing gate lists, string/integer pseudo-booleans, duplicate names, omitted MUST gates and malformed rows fail closed without a receipt-parser traceback.
- Corrected first-screen historical/session wording, overly broad rankings, unconditional spacing claims, reference-notebook attribution and an unverified weekly-cap claim. Existing evidence and raster bytes are preserved.
- Added regression tests for those failure modes. Installed dependencies in an ignored virtual environment; no environment or downloaded 25 MB witness was committed.

## Pass 3 — acceptance and remaining limits

Final local validation: **250 tests passed**, with 124 nonfatal Affine deprecation warnings; **36 served zeros-outside TIFFs** passed the site gate; the 8-entry input manifest, pinned parent and 68-row ledger passed; local HTML link audit found no missing targets; `git diff --check` passed. These are software/geometry checks, not competition scores. See the run card and PR checks for evidence. The automated site gate re-reads every served zeros-outside TIFF. The primary passes finite/range/CRS/shape/transform/catalogue/encoding checks. That is **format integrity only**, not scientific validation or permission to submit. No manual inspection is needed to obtain this negative decision.

Still needed, in order:

1. An explicit protocol revision by the owner/selector if dense continuous probability supports were not intended as dot sets. This is a policy change, not a validation bug we can silently fix.
2. A clearly assigned method lane, authorized pinned inputs, and a comparable fold-rebuilt baseline; then the pre-registered experiments within the budget.
3. Official rules/data-use verification, current authenticated submission-page cap, and organizer receipts. GitHub mirror checksums establish identity, not official provenance or redistribution rights.
4. Successful CI and Pages deployment after merge. Live GitHub API reports Pages in **legacy main-root mode**, which bypasses the Actions validation gate. Attempting to switch it to workflow mode returned **HTTP 403: Resource not accessible by integration**; no setting changed. The token lacks this repository-setting permission. The workflow now stages only the public root redirect and docs, preserving existing URLs once Actions mode can be enabled. Legacy-mode site publication must not be described as validation-gated. A local pass alone does not establish that the public site has updated.

### Sources and limitations

[GitHub source receipt](downloads/review_918b947a_sources.json) records the immutable official-reference and GEMSDOE32 owner-workbench sources actually retrieved. [DrivenData problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/), [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), and [GDR INGENIOUS](https://gdr.openei.org/submissions/1391) are manual-review links, **not live-verified sources in this review**. Outbound access is limited to GitHub and package registries. There is no DrivenData session, no current organizer receipt, and no permission to bypass authentication. Automated receipts use the sandbox's actual UTC clock; the session began under the October 24 brief and crossed midnight UTC.
