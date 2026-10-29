# Repository review — 2026-10-29 UTC

## Executive decision

**No TIFF in this checkout is cleared to submit. Do not spend a competition slot.** I generated no new TIFF and ran no geological experiment. This is the protocol-compliant outcome, not a claim that a winning score has been found: the prompt's assigned single-method paragraph is missing, the complete cached feature stack is absent, and the conservative registry stop and exhausted three-experiment lane cannot be waived here.

- The latest primary status feed points to the RIESZ-LOCKED TIFF as a **research download only**. Its machine-readable verdict is `negative`, `submission_eligible: false`.
- Local format validity is not uniqueness, scientific validation, leaderboard performance, or organizer acceptance.
- The requested `0.2778`, `0.3195`, and `0.4413` values are not organizer-confirmed in this checkout. No DrivenData receipt or live leaderboard result was accessed.
- No new HOLDOUT-DTI was calculated in this review. Historical values below are explicitly archived records, not reruns.

## Scope and evidence inspected

Reviewed the working tree and current branch, the current submission/readiness JSON, RIESZ-LOCKED run card, current GitHub Pages landing/summary pages, nine-site report, prior protocol review, experiment hypothesis card, submission validation code, project tests, pinned parent manifest, and available local data files. The relevant focus-site source and uniqueness snapshots are dated 2026-10-28 and are not live feeds.

The following current machine-check results were run in this checkout after installing the pinned `requirements.txt` into the ignored `.venv`:

| Check | Result | Scope |
|---|---|---|
| `python scripts/check_site.py` | PASS; **128 served rasters gated** | Served file format/range gates, page/status consistency, and local receipts; not leaderboard or full-registry authorization |
| `python -m pytest tests -q` | **804 passed, 19 skipped, 171 warnings** | Repository test suite; skips/warnings are retained as reported |
| `make manifest` | PASS | Nine committed parent/data artifacts matched `registry/data_manifest.json` hashes |
| `make verify` | PASS | Pinned R0 parent raster reproduced from committed bytes; `n_dots=37,654`, mass `37,654.0`, footprint `5,167,373` pixels |
| Full feature cache | ABSENT | `.cache/gems_inputs/training_features.tif` was not present; only bridge/sample/catalogue rasters were present under `data/` |

The shared vendor evaluator and writer files are present (`vendor/gems57/evaluate_holdout.py`, `vendor/gems57/submission_writer.py`), but their presence does not reconstruct missing training inputs or reproduce archived holdout receipts.

## Focus-9 executive table

This is the best reported entry per site from the pinned 2026-10-28 audit (see [nine-site detail page](nine-sites.html) and [site evidence](focus9.html)). `CLAIM` is a repository/owner-reported value, not an organizer receipt. `MODEL (LOGO)` is a fitted estimate, not a score. Historical registry uniqueness findings recorded in the audit fail the PI-1 uniqueness criterion for every listed peak; they must not be re-uploaded as unique candidates.

| Site | Highest reported submission (source file stem) | CLAIM | MODEL (LOGO) | Uniqueness / action |
|---|---|---:|---:|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 | 0.25769 | Historical audit: not unique; study only |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 | 0.26702 | Historical audit: not unique; study only |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 | 0.25520 | Historical audit: not unique; study only |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 | 0.27247 | Historical audit: not unique; study only |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 | 0.26702 | Historical audit: not unique; study only |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 | 0.27403 | Historical audit: not unique; study only |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | 0.2778 | 0.27728 | Highest supplied CLAIM among these nine; not unique; study only |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 | 0.27103 | Historical audit: not unique; study only |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 | 0.27471 | Historical audit: not unique; study only |

Later values supplied for comparison were also checked against the session's historical inventory: GEMSDOE24 `0.0859` CLAIM; GEMSDOE25 `0.0742` CLAIM; GEMSDOE27 `0.2190` and `0.2250` CLAIMs; GEMSDOE28 `0.0217` and `0.0206` CLAIMs; GEMSDOE30 `0.1462` CLAIM; GEMSDOE31 no later value supplied; GEMSDOE32 `0.2778` CLAIM; GEMSDOE33 `0.0963` CLAIM; GEMSDOE36 `0.1647` CLAIM. These lower later entries do not change the highest-CLAIM rows above. The source inventory is pinned and stale; no current values are asserted.

### GEMSDOE32 `0.2778`: what the evidence supports

The repository's lineage analysis describes the parent as a sparse H19-5-derived trace pattern with distance pruning from already mapped faults. That is a plausible metric-aligned mechanism: when mapped-fault pixels are masked and nearby predictions are discounted or unhelpful, pruning redundant support and placing remaining points near likely targets can improve a distance-tolerant DTI without proving new fault discovery. The lineage is not a causal experiment, hidden labels are unavailable here, and the user-supplied score has no organizer receipt in this checkout. Therefore the exact cause of `0.2778` is unknown.

The available RIESZ-LOCKED comparison does **not** show that a novel candidate can beat it. The archived run card reports `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, 22,663 withheld positives) `0.037987 [0.031011, 0.044656]`, with R0 recipe control `0.097750 [0.085900, 0.110766]` and paired difference `-0.059763 [-0.072005, -0.046653]`. Those values were not independently reproduced here. The card's `0.321602` is `MODEL`, not a competition score. Holdout DTI and leaderboard score are different evidence instruments; neither the holdout nor this regression output licenses a claim that `0.2778` will be exceeded.

## Protocol gates and blockers

1. **Lane assignment:** the prompt refers to “the single method paragraph below,” but no distinct method paragraph is included. I did not invent or infer a lane.
2. **Budget:** the recorded RIESZ-LOCKED lane used experiment E1–E3 (3/3). No additional experiment was run.
3. **Holdout:** the required full feature stack is unavailable locally, so no buffered, whole-segment visible-only HOLDOUT-DTI can be reproduced in this checkout. Do not present old values as current results.
4. **Registry:** the run card records literal full-support overlap `1.000 > 0.70` both for the pre-placement surface and final raster. A sparse/top-N PI-1 interpretation reports a different result, but the user's instruction says stop when a registry raster's dots exceed the threshold. That interpretation conflict requires explicit protocol resolution; it cannot be silently overridden. The pinned historical inventory size is variously recorded as 2,162 and 2,216 in repository files, so these are not represented as one contemporaneous complete registry count.
5. **Leakage:** the archived card records its canaries, but they were not rerun against a missing feature stack. An archived pass is not a new check.
6. **External verification:** competition/leaderboard, DrivenData submission page, USGS, DOE-GDR and Dropbox hosts were not live-accessible under the environment's network restrictions. Official links for manual review are listed in the site and prior review; no external availability/current score is claimed.
7. **Submission file:** existing research TIFFs can be downloaded for analysis, but there is no new, unique, fully validated, protocol-cleared TIFF from this review. The `OK TO DOWNLOAD` label must not be confused with `OK TO SUBMIT`.

### Official references supplied for review

These links are authoritative destinations by domain/repository, but were not fetched live in this review:

- [DrivenData problem description and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DOE/NREL competition rules (PDF)](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN survey](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [DOE GDR INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391)
- [USGS 3DEP catalog](https://data.usgs.gov/datacatalog/data/USGS:77ae0551-c61e-4979-aedd-d797abdcde0e)
- [EPSG:32611](https://epsg.io/32611)
- [Tversky index](https://en.wikipedia.org/wiki/Tversky_index) (secondary reference, not an official contest source)

## Three review passes

### Pass 1 — inspect and verify
- Read the active session brief, current readiness/status JSON, TIFF run card, focus-site table, documentation, registry/holdout policy, and checks.
- Installed the repository's pinned dependencies into ignored `.venv`; no tracked dependency files changed.
- Executed all four checks listed above.

### Pass 2 — assumptions, contradictions, and edge cases
- Found an inconsistent README headline: it said the RIESZ artifact “passes uniqueness” under PI-1 while the active review and run card say the literal overlap rule is a blocking failure. Corrected the headline to distinguish a diagnostic sparse-dot reading from the conservative literal stop.
- Confirmed the README already carries the Focus-9 summary and a prompt/protocol block, but its prior session date and the request's scope were not obvious at the top. Added this 2026-10-29 addendum and direct review link; retained historical data as dated claims rather than overwriting them.
- Checked that downloadable research files, current readiness, and page checker are not mislabeled as organizer approval. No status feed was changed to grant eligibility.

### Pass 3 — end-to-end request cross-check
- All nine requested sites have one best-reported row with separate `CLAIM`, `MODEL`, and uniqueness status; detailed commit-pinned evidence remains in `nine-sites.html`.
- The GEMSDOE32 rationale is explicitly presented as plausible mechanism, not verified causality; the `0.2778` claim, `0.321602` model output, and archived holdout are not conflated.
- The requested unique submission was **not generated**, because the lane is unspecified, the prior experiment budget is exhausted, the necessary cache is absent, and the conservative uniqueness/holdout gates fail. Generating another raster without those gates would create a misleading or unsafe deliverable.
- The final automated site, test, parent and manifest checks all pass; no claims of a fresh holdout, live official source verification, leaderboard score, or submission authorization are made.

## Next work, in priority order

1. Resolve the literal full-support-vs-sparse-dot interpretation through an authorized documented protocol ruling and supply the missing method paragraph. Until then, stop before placement.
2. Restore and provenance-check the complete feature stack and registry snapshot; then run canaries and the shared evaluator/writer exactly as specified, with fold-visible catalogue features and whole-segment buffered holdouts.
3. Only after the fresh candidate clears pre-placement and final uniqueness plus a positive paired holdout improvement, provide it to the separate weekly-slot selector. Check current official rules/quota on the submission page at that time.
4. Add an organizer receipt to the score ledger when available and label it `ORGANIZER-CONFIRMED`; keep all site mirrors and fitted estimates clearly labeled.

## Final JSON run card

```json
{
  "hypothesis": "No new hypothesis was tested: the assigned method paragraph is absent and this review is limited to repository review and evidence verification.",
  "mechanism": "No raster generation or placement occurred. The RIESZ-LOCKED historical candidate's sparse H19-5-derived trace/pruning mechanism is plausible under a distance-tolerant DTI, but its recorded holdout is below R0 and its literal registry overlap exceeds the limit.",
  "named_non_fault_process_that_could_mimic_it": "Fan-head dissection gullies and incised volcanic canyon or mesa rims can resemble sharp fault scarps; paleoshoreline steps and lithologic contacts can also produce linear edges.",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": "gems57-pooled-hide-v2",
    "withheld_positive_pixels": 22663,
    "candidate": 0.0379871472,
    "candidate_ci95": [0.0310108549, 0.0446562538],
    "r0_recipe_control": 0.0977501041,
    "r0_ci95": [0.0859004763, 0.1107664991],
    "paired_delta_candidate_minus_r0": -0.0597629569,
    "paired_delta_ci95": [-0.0720045951, -0.0466533871],
    "status": "Historical run-card values; not rerun in this review because the full feature stack is absent."
  },
  "correlation_overlap_vs_registry": {
    "preplacement_surface_overlap": 1.0,
    "preplacement_surface_abs_rank_correlation": 0.550328,
    "final_literal_overlap": 1.0,
    "final_sparse_dot_overlap_max": 0.6556,
    "final_abs_rank_correlation_max": 0.144898,
    "interpretation": "Archived RIESZ-LOCKED run-card figures. Literal overlap exceeds 0.70; sparse PI-1 result does not waive the stop. Not freshly re-measured."
  },
  "raster_sha256": "d168c7d2a0ea89f9609426fe5f9d5aa0791223131c98a90d55b1f6aa1cbe5d7a",
  "validator_output": {
    "scope": "scripts/check_site.py, 2026-10-29",
    "served_rasters_passed": 128,
    "no_nan_in_footprint": "Passed for served TIFF set under checker",
    "values_in_0_1": "Passed for served TIFF set under checker",
    "crs_shape_transform_match": "Passed for served TIFF set under checker",
    "new_submission_generated": false
  },
  "submission_name": "gemsdoe92-rieszlbm2-50000d-79041788",
  "submission_note": "Research-only historical artifact. Do not submit; protocol gates fail.",
  "verdict": "negative"
}
```
