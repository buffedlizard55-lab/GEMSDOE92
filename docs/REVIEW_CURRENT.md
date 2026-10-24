# Current review — 2026-10-24 UTC

## Decision first

**Research download only; DO NOT SUBMIT any TIFF or ZIP.** No new candidate raster, model experiment, or holdout run was produced in this review. No weekly submission slot was selected or used.

The existing ANASIG zeros-outside GeoTIFF is format-valid for research: SHA-256 `68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5`, with ten recorded local format gates passing. Its [format receipt](downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-audit.json) does **not** mean it is eligible.

## Fresh ANASIG public-witness recheck

The current [measurement receipt](downloads/public_witness_anasig.json) identifies one public raster at `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif`. The exact Git blob SHA-1 is `374c88b1da2b803e2ed160de467fd71ae114010d`, the downloaded size is 25,065,181 bytes, and its SHA-256 is `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`.

**REGISTRY-MEASUREMENT:** the witness is positive on 5,167,373 / 5,167,373 footprint cells. After the catalogue mask, 5,106,385 cells remain allowed; the witness's 3-pixel halo leaves 0 allowed cells uncovered. Against the exact ANASIG final output, forward 3-pixel overlap is 1.000000 and full-footprint Spearman is 0.038182744. The forward-overlap threshold (`>0.70`) triggers a binding duplicate stop; the Spearman threshold (`|ρ|>0.90`) does not.

Because positive witness support covers every footprint cell, every nonempty candidate restricted to the allowed in-footprint domain would have forward overlap 1.0. Do not evade this by moving dots outside the footprint, emitting no dots, excluding the witness, or changing the interpretation. The outcome is a direct measurement and set-inclusion consequence, not a leaderboard inference.

This is a **single-witness negative check, not a full public-registry scan**. The candidate's actual pre-placement surface was not generated or retained in this review and was **not** compared against this witness. The final-dot failure is sufficient to stop this existing artifact, but this is not a compliant fresh two-phase surface-to-placement uniqueness pass.

### Important scan attribution correction

The earlier 1,279-raster scan and its `11GEMSDOE` witness were run for the **visible-collar** candidate. That inventory/scope is not an ANASIG measurement. The current ANASIG evidence is the one-raster 17GEMSDOE witness recorded above. No fresh exhaustive registry scan was made.

## HOLDOUT-DTI and score provenance

The ANASIG result below is a **prior HOLDOUT-DTI** record, not a result generated or rerun in this review: evaluator `gems57-pooled-hide-v2`, 22,663 withheld positive pixels, 95% paired spatial-cluster CIs.

| Comparison | HOLDOUT-DTI | 95% CI |
|---|---:|---:|
| ANASIG | 0.004967 | [0.004098, 0.005940] |
| ANASIG − R0 | +0.000961 | [+0.000168, +0.001814] |
| ANASIG − prior holdout-best RELIEF p10 | −0.001078 | [−0.002034, −0.000112] |

This local catalogue hide-and-recover diagnostic is not an organizer score and cannot establish performance on private, genuinely uncatalogued faults. ANASIG is below the prior local HOLDOUT-DTI best as well as blocked by the registry rule.

- `0.2778` is a **CLAIM** for GEMSDOE32 `h33-h33-2-b2`; no organizer receipt for it was verified.
- `0.3195` is a user-supplied, unverified **LEADERBOARD-SNAPSHOT**.
- `0.4413` is a prior repository **LEADERBOARD-SNAPSHOT** note dated 2026-10-24; this review did not refresh the official leaderboard, and the note is not a submission-page receipt.
- No current high score is asserted. Provenance is tabulated in [`ledger/score_claims.csv`](https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/ledger/score_claims.csv).

A plausible **HYPOTHESIS**, not a causal finding, is that fixed-budget thinning/pruning and clearance of catalogue traces reduce redundant prediction mass and change distance-weighted precision/recall balance. The available score claim alone cannot identify why it received the reported value. The exact organizer-evaluated bytes and private targets are not established here.

## Current run card and hypothesis queue

- [Current status/run card](downloads/current_registry_stop_run_card_20261024.json) — prior local result, fresh witness scope, current format receipt, and no-new-candidate status.
- [Four ranked unvalidated hypotheses](HYPOTHESES.html) — drainage-network relay, spring-pair strike alignment, host-normalized radiometric residual, and multiseason thermal corridor. Each names layers, physical signature, catalogue-missing rationale, repo distinction, expected value/cost, data requirements, and non-fault mimics. No external source is declared verified or viable.

## Data and source limitations

The 19-band `training_features.tif` stack is absent from `.cache/gems_inputs/` in this checkout. The registry manifest points at owner-mirror GitHub bytes; hash identity is not organizer authentication, data-use permission, or redistribution clearance. The official DrivenData data page and non-GitHub external sources were not verified in this review. No candidate that depends on unverified external data is described as viable.

Three pre-existing DILATATION variants (with zeros-outside and diagnostic TIFF encodings) carry filenames dated `2026-10-25`, later than this review's date (`2026-10-24`). Their existing bytes are preserved but their timestamp/provenance discrepancy is flagged in [`IRREGULARITIES.md`](https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/IRREGULARITIES.md); they are not treated as current work or recommendations.

## Reproduce the checks

```bash
PYTHONPATH=vendor .venv/bin/python -m pytest tests -q
PYTHONPATH=vendor .venv/bin/python scripts/check_site.py
make manifest PYTHON=.venv/bin/python
make verify PYTHON=.venv/bin/python
```

The current site checker validates every served zeros-outside TIFF against the local format gates and checks that each downloadable TIFF/ZIP is explicitly marked **DO NOT SUBMIT**. The one-witness result is rejection evidence only; the full registry was not rescanned.

## Next actions — blocked, not experiments

1. Keep the literal stop in force. A policy owner must explicitly resolve the full-support witness problem before any new placement.
2. Verify official source access, provenance, license/terms, and hashes before restoring data. Do not copy an owner mirror into public artifacts without terms review.
3. Only after those blockers are resolved, pick one named lane from the ranked queue and follow the README protocol: pre-placement surface and post-placement dots; buffered whole-segment holdout; visible-fault-only features and exact masking; pooled DTI; feature-alone leakage canary; automated TIFF validation.
4. Stop after three experiments or two hours. Promotion and a weekly submission slot remain separate selector decisions; no upload occurs here.

Current public entry points: [`index.html`](index.html), [`SUBMIT.html`](SUBMIT.html), and the canonical [`README.md`](https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/README.md).
