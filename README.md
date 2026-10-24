# GEMSDOE92 — Auditable GEMS research workbench

> **Start every session here.** This README is the canonical, complete operating prompt and current decision record. Read it before running code, interpreting old notes, or touching a submission artifact. `SESSION_PROMPT.md` is only a pointer to this file; historical analyses do not override the current status below.
>
> **Current decision (2026-10-24 UTC): research download only; DO NOT SUBMIT any artifact.** No new candidate raster or experiment was produced in this review, and no submission slot was used.

## Current status — a binding public witness blocks every nonempty candidate

The existing ANASIG zeros-outside GeoTIFF is **FORMAT-VALID — OK TO DOWNLOAD FOR RESEARCH** but **NOT CLEARED — DO NOT SUBMIT**. The fresh check is a **single-witness `REGISTRY-MEASUREMENT`, not a full public-registry scan or an organizer receipt**:

- Candidate: [`ANASIG zeros-outside GeoTIFF — OK TO DOWNLOAD FOR RESEARCH ONLY — DO NOT SUBMIT`](docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif); SHA-256 `68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5`.
- Witness: `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif`; its Git blob SHA-1 and file SHA-256 are pinned in the [fresh witness receipt](docs/downloads/public_witness_anasig.json).
- The witness has positive support on **100% of the 5,167,373-cell footprint**. The allowed domain after the catalogue mask is 5,106,385 cells; the 3-pixel halo leaves none uncovered. The existing ANASIG final dots have **100% forward overlap** and final-output Spearman `0.038183` with that witness. The overlap alone exceeds the literal `>70%` stop threshold.
- This single witness is sufficient to stop; it is not evidence that the registry scan was exhaustive. **Any nonempty in-footprint candidate would also have 100% forward overlap with this witness.** For this retrospective measurement, the pre-placement ANASIG surface was not compared; do not claim a completed two-phase uniqueness pass. Do not generate an allegedly unique raster, move dots outside the footprint, emit an empty raster, or waive the threshold. More placement experiments are blocked unless the policy owner explicitly changes the rule.
- The often-cited **1,279-raster / 11GEMSDOE** scan belongs to the earlier **visible-collar** candidate. It is **not** an ANASIG scan. ANASIG has the single-witness measurement above; no fresh complete public-registry scan was made in this review.

The current receipt, including scope and limitations, is [`current registry-stop run card`](docs/downloads/current_registry_stop_run_card_20261024.json). The public site lists every archived TIFF/ZIP as research-only and **DO NOT SUBMIT**; see [`docs/index.html`](docs/index.html).

### Additional future-dated artifact inherited from upstream main

The updated upstream `main` contains a SPRINGALIGN zeros-outside TIFF and ZIP dated `2026-10-25`, after this review's `2026-10-24` date. They were not generated, rerun, or approved in this review. The raster is preserved as an **archived research artifact — DO NOT SUBMIT** ([Archived SPRINGALIGN research GeoTIFF — DO NOT SUBMIT](docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif) · [Archived SPRINGALIGN research ZIP — DO NOT SUBMIT](docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.zip)); its future-dated provenance is unresolved and flagged in [`IRREGULARITIES.md`](IRREGULARITIES.md). The upstream local-uniqueness record is not a check against the current full-support witness. Because that witness covers every footprint cell, this artifact is blocked by the same literal overlap rule as every other nonempty in-footprint TIFF. It is not a new current candidate or a submission recommendation.

## What the reported scores do—and do not—establish

No fresh official leaderboard check was made, and this repository has no organizer submission receipt for the disputed values. The exact classes are preserved in [`ledger/score_claims.csv`](ledger/score_claims.csv):

| Value | Evidence class | What is known |
|---:|---|---|
| `0.2778` | **CLAIM** | Owner-lineage value for GEMSDOE32 `h33-h33-2-b2`; `ledger/historical_climb.csv` records no receipt. It is not independently confirmed by an organizer receipt here. |
| `0.3195` | **LEADERBOARD-SNAPSHOT (user-supplied, unverified)** | Conflicting value supplied in the request; no source receipt was available to verify it. |
| `0.4413` | **LEADERBOARD-SNAPSHOT (prior repository note, not refreshed)** | A prior note records this as the public #1 value on 2026-10-24. This review did not re-read the official page, and the figure is not a receipt for GEMSDOE32 or GEMSDOE92. |

A plausible but **unproven `HYPOTHESIS`** for the GEMSDOE32 lineage is that a fixed dot budget, spatial thinning, pruning of redundant mass, and catalogue clearance changed the balance between recovered truth and false-positive mass under the distance-weighted metric. The score alone cannot identify the cause; the exact organizer-evaluated bytes and private targets are not established by the receipts here. No local HOLDOUT-DTI value can be compared numerically with a live leaderboard score, and this repository does not claim to beat `0.2778`.

The existing ANASIG result is prior **HOLDOUT-DTI**, not a new run in this review: evaluator `gems57-pooled-hide-v2`, 22,663 withheld positive pixels, 95% paired spatial-cluster confidence intervals.

| Comparison | **HOLDOUT-DTI** estimate | 95% CI |
|---|---:|---:|
| ANASIG | `0.004967` | `[0.004098, 0.005940]` |
| ANASIG − R0 | `+0.000961` | `[+0.000168, +0.001814]` |
| ANASIG − prior holdout-best RELIEF p10 | `−0.001078` | `[−0.002034, −0.000112]` |

These are local catalogue hide-and-recover estimates conditional on the recorded folds, masks, and model. They are not organizer-confirmed scores and do not demonstrate performance on private, genuinely uncatalogued faults. ANASIG does not beat the repository's prior HOLDOUT-DTI best.

## Operating prompt — mandatory in every session

### Mission and evidence boundary

1. **Mission:** build reproducible, scientifically defensible research about previously unmapped geothermal-related faults in the NW Great Basin. A candidate is not a submission merely because its TIFF is valid. Maximize the probability of a sound result; own and publish negative outcomes.
2. Do not claim organizer confirmation without a submission-page receipt copied into `ledger/`. Label local catalogue hide-and-recover results **HOLDOUT-DTI**, with evaluator version, withheld-positive count, and 95% CI. Keep **CLAIM**, **MODEL**, **PROXY**, **LEAKAGE-CANARY**, and **REGISTRY-MEASUREMENT** separate. A projected or proxy value is never a leaderboard score.
3. Do not invent missing leaderboard observations or causal explanations. If an official source is inaccessible, say so. No credentials are requested, stored, or used in this project.

### Single-lane experiment protocol

4. **Stay in one named method lane.** Before placement, compare that lane's actual prospectivity surface to every accessible registry raster. After placement, compare the final dots as well. Against any one raster, stop and record a duplicate if absolute Spearman rank correlation is `>0.90` **or** more than `70%` of candidate dots are within `3 px`. Report the inventory scope. Do not exclude dense priors, redefine overlap, shift dots outside the competition footprint, or tune around a failed threshold.
5. The present full-footprint-positive witness makes the current literal overlap gate impossible for every nonempty in-footprint candidate. Do not run placement or promote a candidate while that binding rule stands. A policy change must be explicit and external to a model experiment.
6. Reuse the pinned cached feature stack only after verifying its exact bytes and terms; reuse `vendor/gems57/evaluate_holdout.py`, `vendor/gems57/submission_writer.py`, and the shared template. Fix defects in shared tools, not a private fork. Do not silently rebuild or substitute evaluator code.
7. Hold out **whole fault segments/components with a spatial buffer**. Derive catalogue-based features only from visible faults in each fold; mask visible faults pixel-exactly. Use pooled DTI with `α=0.2`, `β=0.8`, and the `300 m` triangular kernel. Do not tune on withheld labels.
8. Run a feature-alone leakage canary before trusting a model. Use symmetric AUC where direction can reverse. `AUC >0.90` is leakage until investigated; record the investigation and disposition.
9. Before implementation, rank `3–5` genuinely unvalidated geological hypotheses. For each, document layers, physical signature, why it may reveal a catalogue-missing fault, distinction from prior repo methods, named non-fault mimic, expected scientific value/cost, data requirements, and provenance. If a candidate needs external data, identify a free official source and verify availability **before** calling it viable. Do not claim unverified sources were downloaded.
10. Keep each method lane within **3 experiments or 2 hours**, whichever comes first. Record no-run/negative outcomes. Experiment work does not choose a submission or consume a submission slot. Promotion is a separate selector decision under the weekly cap; this agent does not upload or select a slot.

### Run-card and format contract

11. Every experiment/run card must record: hypothesis and mechanism; named non-fault mimic; HOLDOUT-DTI result and 95% CI (or explicit not-run); evaluator version and withheld-positive count; leakage canary; pre-placement surface and post-placement final-dot registry measurements; exact registry scope; candidate SHA-256; validator output; artifact filename/status; submission name/note only as archived metadata; and verdict (`promote` or `negative`). If no candidate was generated, say so explicitly and do not fabricate a raster hash or validation result.
12. Format validation is automated in-project; no human pixel inspector is acceptable. For any research download, gate the exact bytes on disk: one float32 band; matching CRS, shape, and transform; finite values in `[0,1]`; no NaN inside the footprint; zeros outside; no catalogue mass; recorded SHA-256. Never silently clip, replace NaN, or edit a TIFF after validation.
13. **Download status and submission status are separate.** Every linked TIFF/ZIP must be clearly identified as a research or diagnostic file and marked **DO NOT SUBMIT** while not eligible. Describe exact bytes as format-valid / **OK TO DOWNLOAD FOR RESEARCH** only after automated gates pass. A format pass never implies slot eligibility. The site's `scripts/check_site.py`, automated tests, and CI enforce the link-label and format contract.

## Reproduce the current checks

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
PYTHONPATH=vendor .venv/bin/python -m pytest tests -q
PYTHONPATH=vendor .venv/bin/python scripts/check_site.py
make manifest PYTHON=.venv/bin/python
make verify PYTHON=.venv/bin/python
```

The ANASIG file's local receipt records ten format gates passing on exact bytes: one-band float32, EPSG:32611, `3730 × 3292`, matching transform, all-finite values in `[0,1]`, no NaN inside the footprint, zeros outside, and zero catalogue mass. That is **FORMAT-VALID / RESEARCH ONLY**, not submission eligibility. The fresh public-witness result is in [`docs/downloads/public_witness_anasig.json`](docs/downloads/public_witness_anasig.json).

## Data access, provenance, and limitations

- `data/bridge/` and the pinned parent are available for local checks. The larger `training_features.tif` and external feature stack are **not present in `.cache/gems_inputs/` in this checkout**. `registry/session_manifest.json` points to GitHub owner mirrors and `scripts/restore_inputs.py`; matching a mirror hash proves byte identity only, not official origin, license, or redistribution permission.
- The official DrivenData data page and external official data sources were not reachable from the permitted network hosts in this review. No candidate that requires those bytes is declared viable. Obtain authorization and verify official provenance/terms before restoring or redistributing them.
- The full accessible public registry was not rescanned in this review. The one hash-verified full-support witness is a sufficient negative result under the literal rule, not a completeness certificate.
- Three pre-existing DILATATION variants (six TIFF encodings) carry the future date `2026-10-25` even though this review is dated `2026-10-24`. Their provenance/time inconsistency is flagged in [`IRREGULARITIES.md`](IRREGULARITIES.md); they are archived research-only artifacts, not new work or current recommendations.

## Project map

- [`docs/index.html`](docs/index.html) — public status page; all download links are labeled.
- [`docs/SUBMIT.html`](docs/SUBMIT.html) and [`docs/SUBMIT.md`](docs/SUBMIT.md) — current no-submit status; no actionable upload is authorized.
- [`docs/HYPOTHESES.html`](docs/HYPOTHESES.html) / [`docs/HYPOTHESES.md`](docs/HYPOTHESES.md) — ranked, unvalidated research backlog; no active lane.
- [`docs/REVIEW_CURRENT.md`](docs/REVIEW_CURRENT.md) — latest recheck, scope, and limitations.
- [`docs/downloads/current_registry_stop_run_card_20261024.json`](docs/downloads/current_registry_stop_run_card_20261024.json) — machine-readable current decision.
- [`ledger/score_claims.csv`](ledger/score_claims.csv) — disputed score provenance; no receipt verified.
- [`IRREGULARITIES.md`](IRREGULARITIES.md) — material provenance, data, and implementation irregularities.

**Core values:** Maximize P(Win) · Own the Outcome · never trade scientific integrity for a downloadable file or a submission slot.
