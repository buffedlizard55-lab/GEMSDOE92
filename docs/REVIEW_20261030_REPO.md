# Repository review — 2026-10-30

## Executive decision

**No new GeoTIFF is cleared for a competition upload. Do not spend a weekly slot.** The repository's automated site gate and full test suite pass, but those checks establish software/data-integrity and submission-format properties—not organizer acceptance, leaderboard rank, or authorization to upload. The machine-readable feed `docs/downloads/readiness.json` records `verdict: negative` and `submission_eligible: false`; `scripts/check_site.py` identifies the RIESZ-LOCKED TIFF as the current site primary and reports 132 served rasters gated.

The claimed best result in the supplied material, GEMSDOE32 `0.2778`, is not backed by an organizer receipt in this checkout. The local ledger ends with `best RECEIPT: none`. Treat `0.2778`, the user-reported `0.3195` and `0.4413`, and the repository's `0.2784` report as **CLAIM / unverified**, not as confirmed scores. The repository's `0.2784` row concerns GEMSDOE92's LBMC1 and is documented as a user/owner claim; it is not the same artifact as the GEMSDOE32 `0.2778` submission.

## Verification performed

- `python -m pytest tests -q` in a clean project virtual environment: **834 passed, 19 skipped** (171 warnings; primarily Rasterio/Affine deprecations and synthetic-test georeferencing warnings).
- `PYTHONPATH=vendor python scripts/check_site.py`: **PASS**, all **132** served raster artifacts gated. The script reports the current primary as `gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif`, SHA-256 prefix `d168c7d2a0ea89f9`, verdict `negative`.
- `python -m gems manifest --manifest registry/data_manifest.json --data-root data`: **PASS**, all eight pinned inputs verified.
- `python -m gems parent --recipe registry/parents/R0.json --data-root data`: **PASS**; pinned parent `h33-h33-2-b2`, 37,654 dots, 5,167,373 footprint pixels, minimum catalogue separation 2.236 px.
- `python -m gems ledger`: **141 rows; best RECEIPT: none**.
- Initial runs against the system Python failed because `pytest`/`numpy` were not installed. The pinned `requirements.txt` was installed into ignored `.venv/`; this is an environment limitation, not a project test failure.
- No candidate was created and no weekly slot was used in this review.

## Findings and risks (ordered by impact)

1. **No eligible file / score validation gate.** Current readiness and site check explicitly say `negative` / `DO NOT SUBMIT`. A file passing TIF metadata/range validation is not necessarily scientifically predictive, unique under the stated conservative registry rule, or eligible to submit. Do not interpret a MODEL projection or cross-site score claim as a predicted official score.
2. **Current-facing page has competing “latest” narratives.** `docs/index.html` promotes DEXP-KOSTROV in its opening section, then presents LIDAR-SINTERVALVE as a 2026-10-29 session candidate, then labels MARUSSI-TRISHEAR and ADMITRELAY as latest/additional candidates. In contrast, the checked readiness feed names RIESZ-LOCKED and `check_site.py` reports RIESZ-LOCKED as primary. All are marked not for submission, but the chronology makes the active recommendation ambiguous. Consolidate this into one generated status block sourced from `readiness.json`, and move older items into a clearly historical archive.
3. **Score evidence needs provenance discipline.** `ledger` contains no organizer-confirmed receipt. The documentation itself classifies external scores as CLAIM, but some prominent copy calls a reported value “#1” or a “leaderboard milestone.” Restrict such claims to explicitly dated, attributed, unverified report language until a submission-page receipt is archived. The current live leaderboard was not queried in this review.
4. **Literal uniqueness rule blocks all nonempty candidates if the dense footprint-wide witness is binding.** Multiple run cards document the `17GEMSDOE` dense witness yielding 1.0 under the literal overlap calculation. Sparse/matched-budget PI-1 results are useful diagnostics but do not override that hard stop unless the protocol owner formally resolves the rule. Keep both pre-placement and final-dot measurements and clearly name which interpretation is binding.
5. **Reproducibility limits for new discovery.** The checkout includes bridge rasters and generated evidence, but no full cached numerical feature stack is present in `data/`. Historical holdout numbers cannot be independently recomputed from the current checkout alone. Preserve their evaluator/version/withheld-count/CI labels and do not present a historical result as freshly validated. Do not launch another hypothesis experiment until the required cache and evaluator inputs can be verified.
6. **Public data/artifact exposure.** `.gitignore` explicitly notes that data and generated submission rasters are tracked/public by convention. Confirm competition terms and redistribution rights before publishing any participant-provided data or derivative artifacts; the DEXP run card also records unresolved official redistribution provenance.

## Focus-nine submission comparison (reported values, not organizer-verified here)

The scores below are copied from the request/repository narrative; the ledger has no official receipts for them. They are therefore **CLAIM**, not estimates produced by this repository. This table summarizes the top named entry supplied per site, not a fresh audit of every remote site's files.

| Site | Best named submission in supplied record | Reported score | Evidence status | Review decision |
|---|---|---:|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 | CLAIM | Historical comparator only |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 | CLAIM | Historical comparator only |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 | CLAIM | Historical comparator only |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 | CLAIM | Highest among entries listed for this site; historical comparator only |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 | CLAIM | Historical comparator only |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 | CLAIM | Historical comparator only |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | 0.2778 | CLAIM | Highest user-cited focus-nine score; not independently confirmed |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 | CLAIM | Historical comparator only |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 | CLAIM | Historical comparator only |

**Download/submission answer:** none of the current candidate TIFs is approved for upload. The project can make a format-valid downloadable file, but no defensible score estimate can guarantee a leaderboard result; a score estimate must remain clearly labelled `MODEL` unless confirmed by the competition organizer.

## Ranked next hypotheses (proposal only; none validated)

These are testable directions drawn from the existing project layers and prior hypothesis backlog. They are proposals, not evidence of improvement; rank reflects expected value relative to implementation cost, not a score forecast.

| Rank | Hypothesis / available layers | Physical target and missed-catalogue rationale | Difference from existing approaches | Cost / main confounder |
|---:|---|---|---|---|
| 1 | **Multi-scale magnetic-gradient tensor orientation coherence** — airborne magnetic/geophysical bands in the GeoDawn numerical-feature raster | Coherent, near-linear horizontal-gradient direction changes may expose buried basement structures whose surface expression is weak and absent from mapped-fault catalogues. | Use tensor eigenvector orientation consistency and scale persistence, rather than another scalar edge/intensity ridge score; audit prior `EULERFUSE`, `FLEXMAG`, `CURIEDEMAG` implementations before coding. | Medium; lithologic contacts and survey-strip artifacts can mimic faults. No new source required if cached raster bands are present and verified. |
| 2 | **Drainage knickpoint alignment conditioned on lithology-independent channel geometry** — DEM derivatives / drainage proxies | Persistent, aligned knickpoints can indicate differential uplift or structurally controlled incision where no mapped fault exists. | Condition alignment on stream order, local relief and opposing-bank geometry; unlike simple knickpoint density, require cross-scale spatially coherent breaks. | Medium-high; lithologic resistance, dams, and DEM artifacts are major mimics. Current DEM availability/cache must be confirmed. |
| 3 | **Radiometric contact displacement / alteration contrast** — airborne K, eTh, eU and magnetic structure | Spatially coherent changes in radiometric ratios coincident with structural discontinuities can identify hydrothermal alteration or fluid pathways missed by a fault-only inventory. | Test cross-channel contact offsets and contrast asymmetry, not direct proximity to USGS fault pixels; inspect existing `RADIOCONTACT`/`RADIODECOUPLE` first. | Medium; soil moisture, vegetation, and lithologic boundaries mimic alteration. Likely no new data if GeoDawn bands are cached. |
| 4 | **Terrain-slope directional anisotropy and curvature sign transitions** — DEM, multi-directional slope, profile/plan curvature | Repeated directional slope breaks and curvature transitions may capture scarps or subtle fault-propagation folds with weak local relief. | Require persistent curvature-sign topology across scales and orientation coherence, rather than scoring slope magnitude or single-scale scarp edges. | Low-medium; erosional scarps, alluvial fans, and roads are mimics. Need verified DEM/cache availability. |
| 5 | **Geothermal surface-expression interaction screen** — official springs/wells/thermal occurrences, if such labeled layers are already available | Distinctive alignments of independently reported thermal manifestations with structural proxies may help rank blind fluid pathways outside mapped faults. | Treat occurrences as independent covariates with spatially blocked ablation, not as copied fault catalogues or direct target labels. | High and data-dependent. Do not treat as viable until an official, freely accessible source and permitted download are verified; candidate sources to investigate include USGS geothermal data and DOE GDR/OpenEI. |

### Required experiment controls

Before an experiment, use the shared evaluator/writer and existing cached feature stack; withhold whole fault segments with a buffer; derive catalogue-dependent features using visible faults only; mask visible faults pixel-exactly; pool DTI with alpha 0.2, beta 0.8 and the 300 m triangular kernel; report evaluator version, withheld-positive count and 95% CI; run each feature alone as a leakage canary (AUC > 0.90 is a stop pending leakage proof); compare pre-placement surface and final dots against the registry; stop after three experiments or two hours. A candidate is not promotable merely because its point estimate exceeds a comparator: use paired uncertainty and all protocol gates. Submission-slot selection remains separate.

## Three-pass conclusion

1. **Pass 1 — implementation/state inspection:** checked repo status, status JSON, current site primary, data manifest, parent pin, ledger, and focus-nine page.
2. **Pass 2 — independent execution:** installed pinned requirements into ignored `.venv`; ran full tests, full site gate, manifest verification, parent verification, and ledger audit. No failures in project tests or site checks.
3. **Pass 3 — request-level reconciliation:** confirmed there is no organizer receipt, current candidates remain negative, score claims are not verified, and the requested “highest-scoring upload-ready” submission cannot be honestly selected or generated from the evidence available. No TIF was created and no competition slot was used.

## Official references supplied for manual/source review

These links are recorded from the project request; this review did not access login-gated DrivenData content or independently confirm the current leaderboard.

- [DrivenData competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition rules / about](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [Competition data page (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [DOE GEMS report PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [GDR / OpenEI submission 1391](https://gdr.openei.org/submissions/1391)
- [USGS GeoDawn survey data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [EPSG:32611](https://epsg.io/32611)
- [Tversky index background](https://en.wikipedia.org/wiki/Tversky_index)
- [Competition leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
