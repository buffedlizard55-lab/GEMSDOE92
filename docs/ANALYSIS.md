# Current scientific analysis — 2026-10-24 UTC

> **Current disposition: no submission cleared; DO NOT SUBMIT.** The evidence below separates prior local holdout performance, a fresh single-witness registry measurement, unverified score claims, and scientific hypotheses. No new candidate or model experiment was generated in this review.

## 1. What is known about GEMSDOE32 `0.2778`?

`0.2778` is recorded as a **CLAIM** for GEMSDOE32 `h33-h33-2-b2`; `ledger/historical_climb.csv` and `registry/parents/R0.json` do not provide an organizer submission-page receipt. The disputed values `0.3195` and `0.4413` are recorded as unverified **LEADERBOARD-SNAPSHOT** values in [`ledger/score_claims.csv`](https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/ledger/score_claims.csv). No fresh official leaderboard observation was made in this review. No current leaderboard high score is asserted.

A plausible **HYPOTHESIS**, not a causal conclusion, is that a fixed candidate budget, spatial thinning, pruning of redundant mass, and catalogue clearance changed the balance between useful distance-weighted coverage and false-positive mass. The score alone does not identify the cause. The exact organizer-evaluated bytes and private target labels are not established here.

The repository's local holdout evaluator uses pooled distance-weighted Tversky with α=0.2, β=0.8, and a 300 m triangular kernel. Catalogue hide-and-recover can reward recovery of mapped catalogue structures; it is not equivalent to scoring private, genuinely uncatalogued faults.

## 2. Prior ANASIG HOLDOUT-DTI — not rerun in this review

Evidence class **HOLDOUT-DTI**; evaluator `gems57-pooled-hide-v2`; 22,663 withheld positive pixels; paired spatial-cluster 95% CIs. These values are from the prior experiment, not a new run.

| Comparison | HOLDOUT-DTI | 95% CI |
|---|---:|---:|
| ANASIG | 0.004967 | [0.004098, 0.005940] |
| ANASIG − R0 | +0.000961 | [+0.000168, +0.001814] |
| ANASIG − prior holdout-best RELIEF p10 | −0.001078 | [−0.002034, −0.000112] |

The prior result improves on R0 but is below the prior local holdout best. It is not an organizer score and cannot establish live generalization.

## 3. Current registry blocker and candidate status

The current ANASIG zeros-outside file is format-valid for research; its ten local MUST gates pass on disk reread. It remains **NOT CLEARED — DO NOT SUBMIT**.

A fresh **REGISTRY-MEASUREMENT** checked one exact public 17GEMSDOE raster, with Git blob SHA and byte hash recorded in [`downloads/public_witness_anasig.json`](downloads/public_witness_anasig.json). Its positive support covers 100% of the footprint; the 3-pixel halo leaves no allowed cell uncovered. ANASIG final-dot forward overlap is 1.000000, which exceeds the literal >0.70 stop. Full-footprint Spearman is 0.038183, below the absolute 0.90 limit; it does not cancel the overlap failure. The actual pre-placement surface was not checked against this witness in this retrospective review.

This is a single-witness negative result, not a full public scan. Because the witness is positive at every footprint cell, every nonempty in-footprint candidate would fail the literal overlap rule while it remains binding. Do not generate or promote a purportedly unique candidate under that rule.

The older 1,279-raster / 11GEMSDOE scan applies to **visible-collar**, not ANASIG. It must not be attributed to ANASIG. Current measurements and scope are in [`REVIEW_CURRENT.md`](REVIEW_CURRENT.md) and [`downloads/current_registry_stop_run_card_20261024.json`](downloads/current_registry_stop_run_card_20261024.json).

## 4. Current scientific action

No candidate lane is active. The ranked backlog in [`HYPOTHESES.html`](HYPOTHESES.html) contains four formulations that have no tracked build/holdout result in the exact proposed form. The variants identify related methods already screened, named non-fault mimics, value/cost, data requirements, and source verification status. No external data source is treated as verified or viable in this review. The full training feature stack is absent from the current `.cache`.

If the policy and data-access blockers are resolved in a future session, follow the canonical protocol in the [repository README](https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/README.md): one method lane, actual surface comparison before placement, final-dot comparison after, buffered whole-component holdout, visible-fault-only catalogue features, exact masking, pooled DTI, single-feature leakage canaries, automatic format gates, and a maximum of three experiments or two hours. Promotion and slot selection remain separate.

## 5. Evidence and limitations

- **CLAIM** and **LEADERBOARD-SNAPSHOT** are not **ORGANIZER-CONFIRMED** receipts.
- **HOLDOUT-DTI** is a local hide-and-recover diagnostic, not a leaderboard score.
- **PROXY** and **MODEL** values are not private-label performance.
- **REGISTRY-MEASUREMENT** reports exactly what public bytes were checked; the current ANASIG finding is one binding witness, not an exhaustive registry certificate.
- The official DrivenData leaderboard/data page and non-GitHub data sources were not refreshed in this review. Pinned owner-mirror hashes do not prove official origin, license, or redistribution permission.
- Existing filenames dated 2026-10-25 are later than this review date; their provenance/time discrepancy is flagged in the repository's `IRREGULARITIES.md`.

See [`README.md`](https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/README.md) for the full operating prompt, [`SUBMIT.html`](SUBMIT.html) for the current no-submit status, and [`index.html`](index.html) for research-only downloads.
