# GEMSDOE92 repository review — 2026-10-24 UTC

## Decision first

**Existing primary: OK TO DOWNLOAD FOR RESEARCH; DO NOT SUBMIT.** The served primary is a format-valid research artifact, but it is **not cleared for a weekly competition slot**. No new prediction TIFF, holdout score, organizer receipt, or weekly-slot selection was made in this review. Creating an arbitrary byte-different raster would not satisfy scientific uniqueness; an all-zero map or values outside the target footprint are not loopholes.

The blocking rule is the session's literal registry rule. The existing current-primary full public scan records a full-footprint-positive registry raster and a final-dot forward overlap of 1.0. Since all of the candidate's nonzero predictions lie inside the same target footprint, it fails the `>70%` overlap rule. This proves a stop under that rule; it does **not** prove that the geological surfaces are equivalent. This is the scan's recorded scope, not a fresh scan of every private repository, historical revision, owner, ZIP-only object, or site-only artifact.

## Three-pass review

### Pass 1 — read and reconcile mission, evidence, and current UI

Read `README.md`, the complete `SESSION_PROMPT.md`, `docs/REVIEW_CURRENT.md`, `docs/NEXT_STEPS.md`, current run cards, homepage, submission guide, and executive summary. The site already distinguishes research download validity from selector eligibility and presents the downloadable TIFF prominently. It correctly says **do not submit** while `submission_eligible` is false. That safety state takes precedence over the generic goal of producing a fresh submission.

The current artifact is `docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif` (SHA-256 `8f1f93d8c97b4e1c359ce5fbe07d183214e707aa6bda4ed074c00921f39ad32e`). It is not newly generated here. The existing audit receipt says ten of ten format gates pass: one float32 band, finite values in `[0,1]`, no NaN inside the footprint, zero outside, EPSG:32611, shape 3730×3292, and exact template transform. The exact hash and format receipt were rechecked against the current file and site gate in Pass 3.

### Pass 2 — check the scientific and process claims; identify blockers

**GEMSDOE32 score explanation.** The user-supplied `0.2778` is a **CLAIM**, not an ORGANIZER-CONFIRMED receipt in this checkout. The public GEMSDOE32 page was retrieved for review; it describes a one-click TIFF, an H33-2-B2 sparse/dotted artifact, its validation, and its own modeled/holdout discussion, but explicitly says its artifacts have no organizer score. The repository's local R0 forensics document the structural lineage and pixel filtering (H19-5 → D2.8 → SOLO → R0), and the competition's official metric makes reduced redundant false-positive mass a plausible mechanism. That is an explanation consistent with geometry and metric, **not proof that filtering caused the reported competition value**; the private test labels and an organizer receipt are unavailable here.

The official problem page states that the target is geological faults indicative of geothermal resources, that known-fault labels are incomplete and can contain errors, and that hidden test faults were expert-identified. It defines the DTI with α=0.2, β=0.8 and a 300 m triangular kernel, and states the required single-band float32 probability GeoTIFF format. Therefore a catalogue hide/recover score is not an organizer score and is not evidence of improvement on hidden labels.

**Leaderboard discrepancy.** The prompt gives `0.3195` as a current high score, while repository records preserve a `0.4413` public-leaderboard observation dated 2026-10-24. Neither was refreshed against the live leaderboard in this review. Treat both as time-stamped **CLAIM / LEADERBOARD-SNAPSHOT**, not as current truth and not as a receipt for this artifact. This review makes no claim that a local result exceeds either.

**Universal uniqueness stop.** `evidence/coulomb_loqo_public_registry_uniqueness.json` records 1,368 exact-grid, single-band rasters scanned across the recorded public owner-repository inventory. For the candidate surface, worst forward overlap is 1.0 and worst absolute Spearman correlation is 0.454032; for final dots, worst forward overlap is 1.0 and worst absolute Spearman correlation is 0.096019. The full-footprint-positive witness is `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif`; its recorded Git blob is `374c88b1da2b803e2ed160de467fd71ae114010d`, SHA-256 is `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`, and the record says it is positive on all 5,167,373 footprint pixels. The literal overlap rule consequently prevents any nonempty in-footprint prediction from passing. The registry inventory's scope limitations are retained; this is not a claim of exhaustive global uniqueness.

**Data and provenance.** The current checkout contains the bridge/grid/lineage rasters but does not contain `.cache/gems_inputs/training_features.tif` or the other session-manifest feature inputs. `scripts/restore_inputs.py` can retrieve pinned bytes from owner GitHub mirrors, but the manifest marks upstream provenance/license terms for several competition-derived mirrors as not independently verified; `IRREGULARITIES.md` flags redistribution concerns. Since the public uniqueness rule already stops any nonempty candidate, this review did not restore the 419 MB stack, create a private data fork, or run an experiment. DrivenData data download still requires account access, and no credentials or account session were available. Do not present an owner-mirror hash check as organizer authentication or licensing clearance.

### Pass 3 — validation and corrections

No code, prediction raster, or weekly-slot selector state was changed. This review adds an auditable current-session report and run card, with the current failure state explicit.

Commands run:

- `.venv/bin/python -m pytest tests -q` — **224 passed**, 103 non-fatal Rasterio/Affine `PendingDeprecationWarning`s.
- `PYTHONPATH=vendor .venv/bin/python scripts/check_site.py` — **PASS**, 36 served raster(s) gated; primary identified as COULOMBLOQO standalone.
- `.venv/bin/python scripts/verify_manifest.py` — **PASS**, all eight tracked manifest inputs matched their recorded byte/hash values.
- `.venv/bin/python -m gems parent --recipe registry/parents/R0.json --data-root data` — **PASS**, pinned R0 verified; 37,654 dots.
- `.venv/bin/python -m gems ledger` — **68 rows; no RECEIPT**.
- `.venv/bin/python -m compileall -q gems scripts vendor/gems57 tests` and `git diff --check` — **PASS**.

These are repository/software/integrity checks, not geological validation, competition performance, current leaderboard verification, or organizer acceptance. The public-registry scan is a prior recorded scan; this session did not refresh the public inventory.

## Ranked candidate hypotheses for a later authorized session

These are **research proposals, not tested methods or score projections**. The repository's current method inventory was searched. They are distinguished from the implemented lanes by their primary transform/measurement, but scientific novelty beyond the inspected repository and the listed owner sites is not established. No candidate is actionable until the registry/uniqueness policy is resolved and required inputs can be verified. The ranking is qualitative expected potential relative to cost, not a numeric expected DTI gain.

| Rank | Hypothesis; layers/data | Physical signature and why a catalogued fault may be absent | Difference from methods already implemented here | Named non-fault mimic | Expected value / cost / availability |
|---:|---|---|---|---|---|
| 1 | **Euler-consistent magnetic–gravity source edges.** GeoDAWN training bands: reduced-to-pole magnetic anomaly, magnetic vertical gradient, gravity anomaly/derivatives, and depth-to-basement. | Compare source-location estimates across moving windows and multiple structural indices; a basement discontinuity concealed under basin fill may lack a mapped surface scarp. | The current lanes use gradients, Hessian/curvature, orientation agreement, and supervised cross-fitting; none implements windowed Euler deconvolution with cross-field source-depth stability as the scoring signature. | Pluton margins, remanent volcanic contacts, and non-fault density boundaries. | **Highest conditional value; medium/high compute and method-validation cost.** The competition's own feature description confirms magnetic and gravity inputs exist in the provided stack, but that stack is absent locally. Restore only after provenance/license gate; not viable to validate in this checkout. Official data lead: [USGS GeoDAWN catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7). |
| 2 | **Cross-profile asymmetric scarp-step detector.** Detrended elevation and detrended-elevation slope (bands described in the competition page). | Fit cross-strike profiles for a one-sided elevation offset plus background trend and require consistent polarity/position along strike; this can isolate degraded subtle scarps, including faults absent from current maps. | BREAKLINE/STEPEDGE/SCARPPOL use derivatives, curvature or coherence; the proposed test is explicit model comparison of paired cross-profile step versus smooth/fan alternatives, not another slope-rank threshold. | Lake Lahontan shorelines, alluvial-fan toes, terrace risers, roads, and incised wash banks. | **Moderate conditional value; medium cost.** No external dataset is inherently required, but it still requires the absent local feature stack and proper whole-segment holdout. Dataset is described on the official [DrivenData problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/); actual input bytes are not currently staged. |
| 3 | **Drainage knickpoint / deflected-thalweg structural test.** 1 m DEM links listed by competition; derive drainage profiles and compare lineament-crossing knickpoints with the provided 100 m geology/geophysics. | A blind or degraded fault may offset channels or localize persistent profile breaks even where interfluve scarps are subdued and absent from the catalogue. | Existing terrain work scores slope/scarp ridges, not network-constrained longitudinal channel profiles with cross-channel displacement and along-channel persistence. | Lithologic knickpoints, waterfalls, fan incision, stream capture, roads/culverts, and anthropogenic channels. | **Potentially useful, high data/compute cost. Not viable yet.** Official problem page confirms a `1m_DEM_links.csv` is provided through the competition data area, but access is account-gated; actual URLs, completeness, terms and availability were not inspected here. Do not assert the tiles are obtainable until the CSV and tile responses can be verified. |
| 4 | **Pumping-deconfounded InSAR line-of-sight step.** External Sentinel-1 InSAR velocity/time-series plus existing Band 8 dilatation, Band 7 shear, and Band 15 cover depth. | A spatially coherent deformation gradient that persists across epochs and aligns with structural evidence might flag active blind faulting beneath basin fill. | GEOTENSION uses a coarse geodetic strain stack; this would add independent spaceborne time-series and explicitly model pumping/seasonal subsidence rather than reuse the same strain bands. | Groundwater/brine extraction, seasonal hydrology, mining, atmospheric delay, and decorrelation. | **Potentially high but very high cost and uncertain coverage. Not viable yet.** Official sources to investigate only after the stop is resolved: [NASA OPERA](https://www.jpl.nasa.gov/go/opera/) and [Alaska Satellite Facility DAAC](https://asf.alaska.edu/). Live AOI coverage, downloadable product, licensing and required account access were not verified. |

### Top-candidate validation decision

Rank 1 is **not validated**. There is no local GeoDAWN stack, and under the unchanged literal rule any nonempty emitted raster is already blocked at registry preflight. Therefore no feature can honestly be evaluated on the requested holdout or represented as a submission candidate in this review. The `HOLDOUT-DTI` for this session is **NOT RUN** (no evaluator result, withheld-positive count, or confidence interval is claimed). Do not touch a weekly slot. First restore the official competition download through authorized access or complete provenance/licensing review for any mirror, then obtain a policy-owner ruling on dense continuous rasters before running a surface or placing dots.

## Official references and what they verify

- [DrivenData problem description and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) — retrieved during this review. It verifies the task is fault prediction, the label incompleteness context, available feature categories, stated 1 m DEM link file, metric definition, and GeoTIFF format.
- [DrivenData reference solution repository](https://github.com/drivendataorg/gems-prize-reference-solution) — retrieved during this review; it is a baseline reference, not evidence of any reported score.
- [GEMSDOE32 public page](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) — retrieved for the user-reported artifact and its claims. The page itself distinguishes model/projection from organizer score. It is an owner-reported source, not organizer confirmation.
- [USGS GeoDAWN catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7), [DOE GDR INGENIOUS](https://gdr.openei.org/submissions/1391), and [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) — official source leads preserved for review; their non-GitHub live content was not fetched in this restricted execution.
- [EPSG:32611](https://epsg.io/32611) — official CRS registry lead. The repository's actual TIFF CRS/shape/transform are independently validated locally against the sample submission.

## Remaining work and limitations

1. Resolve the literal registry policy for dense continuous surfaces through the authorized selector/governance path. Until then, do not create or promote a new nonempty TIF.
2. Obtain the competition data and 1 m DEM links with authorized DrivenData access, then establish permitted use/sharing and verify file hashes/provenance. Never request or place credentials in chat.
3. Refresh the public inventory before any later uniqueness claim; the 1,368-raster result is historical relative to this session.
4. Run the ranked top hypothesis only after steps 1–2; use the shared cached-feature/holdout/evaluator/writer pipeline and all single-feature leakage canaries; obey the 3-experiment / 2-hour budget.
5. The project has no ORGANIZER-CONFIRMED receipt in the current ledger. Human upload and selector choice remain outside this automated repository workflow; no local score or projection can replace a receipt.
6. Investigate whether tracked `data/` rasters and public sibling-repository mirrors comply with competition/data licenses. The project already flags this as an irregularity; this review does not silently remove historical files or assume permission.

## Run-card pointer

Machine-readable card: [`../evidence/arena_review_run_card_20261024.json`](../evidence/arena_review_run_card_20261024.json).
