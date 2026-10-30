# Repository review — 2026-10-30

## Executive decision

**DO NOT SUBMIT any file from this checkout, and do not spend a competition slot.** No new TIFF was generated in this review. The repository's gate records mark all recent candidate experiments negative; the strongest currently recorded local holdout result still does not clear the promotion/uniqueness protocol. A format-valid TIFF is not equivalent to a unique, scientifically validated, organizer-accepted submission.

The prompt's `0.2778`, `0.3195`, and `0.4413` leaderboard figures are **CLAIM / user-supplied snapshot values**, not organizer receipts in `ledger/submissions.csv`. The focus-site best historical claims and TIFF identities below are based on the checked-in 2026-10-26 forensic audit; they were not refreshed from the live sites in this review. No robust estimate of future organizer score is available. Do not rename a claim, holdout result, proxy, or model projection as an estimate or score.

## Focus-site executive summary

Each row names the highest reported historical item supplied for the requested site set. The filename comes from the archived 2026-10-30 owner-repository byte audit; the TIFF bytes are **not present in this checkout**. The linked site is a navigation pointer, not a verified direct download. `CLAIM` means the score was reported by a site/owner; the repo records no organizer receipt for these values. The holdout column is an archived static re-evaluation of the repository's prior local variant, **not** a prospective validation of a model trained without the withheld segment or proof of an exact-byte score for the current owner copy. `Estimated future score` is deliberately `N/A`: the existing score estimator is not sufficiently validated for a per-file prediction.

| Site (owner page; not live-checked) | Highest reported historical filename (bytes are not in this checkout) | Reported result | Archived HOLDOUT-DTI* | Unique vs other eight focus sites? | Estimated future score |
|---|---|---:|---:|---|---|
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` ([site](https://buffedlizard55-lab.github.io/GEMSDOE24/)) | **0.2477 CLAIM** | 0.090296 [0.079385, 0.102871] | **No** — fails pairwise focus-set duplicate threshold(s) | N/A |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` ([site](https://buffedlizard55-lab.github.io/GEMSDOE25/)) | **0.2600 CLAIM** | 0.093234 [0.082019, 0.105955] | **No** — exact same support as GEMSDOE30 D28 (0-XOR) | N/A |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` ([site](https://buffedlizard55-lab.github.io/GEMSDOE27/)) | **0.2449 CLAIM** | 0.089959 [0.079128, 0.102269] | **No** — fails pairwise focus-set duplicate threshold(s) | N/A |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` ([site](https://buffedlizard55-lab.github.io/GEMSDOE28/)) | **0.2710 CLAIM** | 0.027383 [0.024059, 0.030894] | **No** — fails pairwise focus-set duplicate threshold(s) | N/A |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` ([site](https://buffedlizard55-lab.github.io/GEMSDOE30/)) | **0.2600 CLAIM** | 0.093234 [0.082019, 0.105955] | **No** — exact same support as GEMSDOE25 D2.8 (0-XOR) | N/A |
| GEMSDOE31 | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` ([site](https://buffedlizard55-lab.github.io/GEMSDOE31/)) | **0.2708 CLAIM** | 0.029358 [0.026029, 0.032708] | **No** — exact same support as GEMSDOE28 h27-4 solo (0-XOR) | N/A |
| GEMSDOE32 | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` ([site](https://buffedlizard55-lab.github.io/GEMSDOE32/)) | **0.2778 CLAIM** — highest in this focus set | 0.004006 [0.003406, 0.004668] | **No** — exact R0 support; pairwise duplicates in the focus set | N/A |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` ([site](https://buffedlizard55-lab.github.io/GEMSDOE33/)) | **0.2632 CLAIM** | 0.053143 [0.047148, 0.059510] | **No** — fails pairwise focus-set duplicate threshold(s) | N/A |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` ([site](https://buffedlizard55-lab.github.io/GEMSDOE36/)) | **0.2750 CLAIM** | 0.004192 [0.003594, 0.004846] | **No** — contains all 37,654 GEMSDOE32 dots plus 1,200 extras | N/A |

\* **HOLDOUT-DTI** values above are the archived static audit's `gems57-pooled-hide-v2` output (8 spatial folds, 22,663 withheld positives; 95% intervals as stored in `evidence/focus9_executive_audit_20261026.json`). They are *not* evidence that these historical files were generated prospectively with fold-visible-only catalogue features. The records themselves flag this distinction. This static audit ran 2026-10-26 and is not newly reproduced here. For the 24/25/27/28/31 rows, the 2026-10-30 byte audit points to NaN-outside owner-copy variants (7,111,787 NaN cells each), while the older holdout evidence uses different archived byte hashes; do not treat those static values as exact-byte re-scores of those current owner copies. The project’s strict all-finite validator rejects such NaN-outside rasters; official portal handling was not live-verified.

The newer byte-level geometry receipt (`evidence/nine_site_byte_check_20261030.json`, generated by `scripts/nine_site_byte_check.py`) contains 72 directional comparisons for the selected historical best file from each site; each site's minimum directional 3-pixel overlap is 0.867190 or higher, so every selected file violates the >0.70 duplicate criterion against every other one. The exact dot-set duplicate among these nine selected best files is GEMSDOE25/GEMSDOE30. This is a nine-site rejection audit, **not** a complete cross-fleet clearance. The older `focus9_pairwise_recheck_14f85876.json` analyzes a different set of artifacts and should not be conflated with this new selected-best comparison. The highest-claim artifacts are not safe recommendations to submit again. A name in this table is not itself a downloadable local file.

## Why GEMSDOE32 plausibly led this focus set — and what remains unproven

The byte-level lineage in the archived audit gives a plausible, testable mechanism, not causal proof of the reported score:

1. The `h33-h33-2-b2` file has 37,654 binary dots and is recorded as a subset of the H19-5 / D2.8 family. Its support is D2.8 with dots within 2 pixels of the catalogue removed. D2.8 has 44,090 dots; the difference is exactly 6,436 pixels in the stored lineage audit.
2. Sparse, line-like predictions can reduce false-positive mass while preserving some coverage of elongated unseen structures under a distance-weighted score. The repo's archived analysis describes this as a precision/coverage tradeoff under the local evaluator's asymmetric DTI weights.
3. The 2-pixel pruning is not automatically beneficial: official scoring's known-fault mask is not established by this review to be a broad buffer, and unmasked nearby predictions may still earn credit. The reported increase could be due to the complete prediction pattern, holdout composition, a particular public split, or other effects. The sibling-site reported scores are owner claims and are not a controlled organizer experiment.
4. The historical raster's archived static HOLDOUT-DTI is only 0.004006 (95% interval 0.003406–0.004668). This large difference from `0.2778 CLAIM` is a warning that static re-evaluation is not a substitute for leakage-free, fold-rebuilt prospective holdout. It does **not** refute the organizer claim or establish a corrected organizer score.

**Can we responsibly claim to beat 0.2778? No.** A model projection or historical claim cannot establish that. A new candidate must beat the frozen, same-evaluator holdout control with a paired spatial-block confidence interval above zero, pass leakage and uniqueness gates, and then receive an organizer receipt if actually entered. The current input/cache and uniqueness stops prevent doing that in this review.

## Review passes

### Pass 1 — scope and implementation inventory

- Confirmed active branch `arena/578be746-gemsdoe92`; repository was clean before review.
- Reviewed the standing README requirements, current submission/readiness JSON, `SUBMISSION_READY.md`, focus-site reports, run-card/evidence layout, shared evaluator/writer packages, test suite, and the input/registry audit.
- The required unique method paragraph is not supplied in the prompt. Repository notes also record the prior method's three-experiment cap as exhausted. No new lane was invented and no additional experiment was run.

### Pass 2 — independent checks and edge cases

- Installed the pinned `requirements.txt` in ignored `.venv`.
- `.venv/bin/python -m pytest tests -q`: **839 passed, 19 skipped**, 171 warnings on the final merged-branch rerun (63.07 seconds).
- `PYTHONPATH=vendor .venv/bin/python scripts/check_site.py`: **PASS**, 132 served raster files gated. This verifies the repository's site/raster gates; it is not leaderboard evidence or a new global registry scan.
- `scripts/audit_input_cache.py`: **exit 1 / fail closed**, 0/12 pinned input files verified. The full feature stack, official-label/sample bundle, and external inputs are not in this checkout's ignored cache.
- Confirmed the ignored public registry cache is absent. The historical registry witness stop is documented in prior run cards, but could not be freshly re-audited against the complete registry in this workspace.
- Live DrivenData, DOE GDR, USGS, NASA/ASF and other non-GitHub official endpoints were not verified in this review; the sandbox egress restriction does not allow these hosts. Existing URLs below are review pointers, not live availability receipts.

### Pass 3 — cross-checks and remaining defects

- The site checks and tests pass, but this does **not** prove the current site banner is the most recent candidate. There is a material freshness inconsistency: `docs/downloads/current_submission.json` and `readiness.json` still identify the 2026-10-28 RIESZ-LBM2 artifact; `SUBMISSION_READY.md` foregrounds 2026-10-29 MARUSSI-TRISHEAR and ADMITRELAY; a later `lidarsintervalve_readiness_20261029.json` exists and is negative. The site contract passes while status recency is not enforced. Treat this as an irregularity; do not infer a cleared or current best candidate from any one banner.
- The current latest candidate evidence I found, `LIDAR_SINTERVALVE`, is marked **negative / DO NOT SUBMIT**: holdout `0.178619 [0.163071, 0.193316]`, paired difference against its selected same-draw control `[-0.002525, +0.004321]`, and the literal dense-witness rule remains a blocker. This is an archived run-card result, not freshly reproduced here.
- `docs/focus9.html` is an old forensic summary. Its audit timestamp is 2026-10-26; it must not be presented as a current feed. The new 2026-10-30 summary above makes its evidence age explicit.
- No experimental TIF was produced. Creating one despite missing full inputs, absent lane paragraph, exhausted budget, and the recorded universal dense-witness duplicate stop would contradict the user-specified stop protocol. Existing research files are not cleared to submit.

## Candidate hypotheses: disposition

The repository already contains an October 29 pre-registration (`docs/HYPOTHESES_20261029_DEXP_KOSTROV.md`) with reserve hypotheses. The current prompt does not provide the single required method paragraph, so I do **not** recast those reserves as lane-compliant candidates or run them. They are explicitly **unvalidated, not score estimates, and not viable for a submission slot now**:

| Archived reserve | Layers/signature and target | Difference / named mimic | Cost and official data status |
|---|---|---|---|
| Potential-field curvature terracing + tensor invariants | Gravity/magnetic bands (B13/B11/B02); curvature-sign terracing and horizontal gravity-gradient tensor invariants to sharpen buried block boundaries | The exact terracing + tensor combination is distinct from scalar-gradient and trishear work recorded in the repo; differential compaction or lithologic contacts can mimic it | Low–medium implementation cost per archived proposal; requires the full training stack, absent here. Official data origin/access was not re-verified in this session. |
| OPERA Sentinel-1 seasonal deformation phase-step | OPERA L3 DISP-S1 displacement time series; spatial discontinuity in annual phase/amplitude or LOS velocity across concealed hydraulic barriers | Distinct from coarse GNSS strain grids; stratigraphic aquitards and pumping cones can mimic it | Medium; official NASA/JPL/ASF product access and footprint coverage were not checked because those hosts cannot be reached here. **Blocked; not proposed as viable.** |
| USGS NWIS piezometric barrier | Official groundwater-level observations; spatial head-step residuals normalized by terrain | Distinct from thermal/Péclet groundwater proxies; perched water tables and pumping can mimic it | Medium; official NWIS endpoint access and in-footprint well density were not checked because the endpoint is outside allowed egress. **Blocked; not proposed as viable.** |

No numerical expected DTI gain is assigned: there is no qualifying holdout result, and inventing a projection would violate the run-card evidence rule. The next experiment requires a new explicit lane assignment and budget authorization, provenance-verified inputs, and a resolved policy on the literal registry witness; it must not consume a weekly submission slot.

## Irregularities / limitations requiring follow-up

1. **Stale top-level submission status:** current JSON points to RIESZ-LBM2 while newer negative experiments are present. Add a machine-checked recency/provenance rule and regenerate the top-level status from one authoritative run-card source; keep fail-closed behavior.
2. **No new TIF clearance:** uniqueness, model lift, and organizer acceptance are separate gates. No artifact in this review is approved for upload.
3. **No independent live-site / official leaderboard check:** `0.2778`, `0.3195`, and `0.4413` remain claims/snapshots. The discrepancy between the stated current highs is unresolved.
4. **Missing inputs:** the audit records 0/12 pinned items present. Competition credentials are not available, and owner-maintained mirror pins do not establish official provenance or redistribution rights.
5. **Uniqueness audit freshness:** complete registry cache absent. Previous universal dense-witness stop is sufficient under the literal rule to reject nonempty candidates, but this review did not download/re-hash the witness or rescan the entire registry.
6. **Automated feed:** static Pages content and a passing local site check do not equal a live, current leaderboard feed. Implement only with a permitted source endpoint, timestamp/hash provenance, stale-data warning and failure tests.

## Official references for later verification

- [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) and [competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (login may be required).
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution).
- [USGS GeoDAWN data record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and).
- [DOE GDR INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391).
- [USGS NWIS groundwater levels](https://waterservices.usgs.gov/nwis/gwlevels/) and [NASA/JPL OPERA products](https://www.jpl.nasa.gov/go/opera/).
- [Official competition rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf); [EPSG:32611](https://epsg.io/32611).

Links are supplied for review. This session did not verify their current response, dataset coverage, terms, or submission-page receipt.

## Final run card — review only

```json
{
  "hypothesis": "No geological hypothesis tested; the required single method paragraph is absent and the prior three-experiment budget is recorded exhausted.",
  "mechanism": "Three-pass repository, evidence and regression review; no surface generation, placement, holdout run or weekly-slot selection.",
  "named_non_fault_process_that_could_mimic_it": "Not applicable: no new raster or geological signal was generated.",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": "not run in this review",
    "withheld_positive_pixels": null,
    "ci95": null,
    "note": "Archived focus-site values are static historical re-evaluations, not prospective validation; latest candidate evidence is not freshly reproduced."
  },
  "correlation_overlap_vs_registry": {
    "measurement": "not rerun; complete public registry cache absent",
    "prior_status": "archived literal dense-witness STOP; no new candidate",
    "preplacement": null,
    "final_dots": null,
    "verdict": "negative / no clearance"
  },
  "raster_sha256": null,
  "validator_output": {
    "new_raster": "not generated",
    "no_nan_inside_footprint": "not applicable",
    "values_in_0_1": "not applicable",
    "crs_shape_transform_match": "not applicable",
    "site_check": "PASS; 132 served rasters gated",
    "tests": "839 passed, 19 skipped; 171 warnings",
    "input_cache": "FAIL CLOSED; 0 of 12 pinned inputs verified"
  },
  "submission_name": null,
  "submission_note": "No candidate; do not submit or spend a slot.",
  "verdict": "negative"
}
```
