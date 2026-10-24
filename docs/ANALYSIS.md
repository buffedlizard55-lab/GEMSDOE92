# Historical GEMSDOE92 evidence review (2026-10-24)

> This earlier score/evidence analysis is retained for its source reasoning. The current repository-wide status supersedes its “current disposition” wording: see [REPO_REVIEW_20261024.md](REPO_REVIEW_20261024.md) and [current status JSON](downloads/current_status.json). No current candidate is cleared; all served TIFs are research-only.

## Question: why is `h33-h33-2-b2` associated with 0.2778, and can a new candidate exceed it?

### Evidence class

The supplied GEMSDOE32 listing associates `h33-h33-2-b2` with 0.2778. In this checkout that is an owner-reported **CLAIM**, not an **ORGANIZER-CONFIRMED** submission receipt: there is no receipt date/score row for this item in `ledger/submissions.csv`, and `registry/parents/R0.json` has `receipt: null`. The prompt gives 0.3195 and 0.4413 as conflicting snapshots. An earlier repository note records a 2026-10-24 public-leaderboard check that displayed 0.4413 at #1 (**LEADERBOARD-SNAPSHOT**); this current review did not independently refresh it. It is not a submission-page receipt for GEMSDOE32 or GEMSDOE92. The [GEMSDOE32 project page](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) itself distinguishes model/holdout evidence from organizer scoring and says that no organizer score exists for its artifacts.

### Mechanistic explanation: plausible, not causal proof

The documented parent uses a fixed 37,654-pixel prediction budget, H19-5 ridge support, D2.8 Poisson spacing, and an off-known-trace mask. Given the competition's distance-weighted, asymmetric Tversky scoring, a fixed budget of spatially distinct predictions near hidden faults can be more efficient than diffuse or redundant positive mass. That is a reason the design *could* do well; without the submission receipt and private test labels, we cannot prove which design choice caused 0.2778.

The competition page describes the target as geological faults, says the public known-fault data is incomplete and may contain errors, and defines expert-labelled new faults for scoring. Therefore the catalogue-derived holdout is a diagnostic, not an equivalent sample of private new-fault truth.

### Can GEMSDOE92 score higher?

**Possible in principle; not established by this checkout.** No local HOLDOUT-DTI, feature AUC, scientific rationale, or projection is an organizer score. The only evidence for live performance is an ORGANIZER-CONFIRMED receipt after a human submission. The safer next action is better data- and leakage-controlled validation, not more score forecasts.

## Candidate evidence and current disposition

### STEPOVER — unique local negative deliverable

The repository's STEPOVER run card records this recipe: derive visible trace tips from the visible catalogue only; construct strike continuation/step-over favourability; select off-catalogue dots; and use `gems57-pooled-hide-v2` with buffered whole-segment holdout, pooled DTI α=0.2, β=0.8, 300 m triangular kernel. The run card reports 11,321 withheld positives and HOLDOUT-DTI `0.0000 [0.0000, 0.0000]` vs R0 proxy baseline `0.0037 [0.0031, 0.0044]`. Its stated explanation is a structural zero: held truth is a subset of the catalogue, while the candidate is constrained away from the full catalogue. The zero does not establish the live score for genuinely unmapped faults.

The saved lane scan's 14-file local comparison reported maximum surface rank correlation 0.0277, final-dot rank correlation 0.0082, and maximum 3-px dot overlap 0.2534; these clear thresholds only within that incomplete local scan. A later broader audit found a full-support duplicate witness: under the literal >70%/3-px rule, the STEPOVER and other nonempty candidates are not cleared for a slot. The file remains format-valid and downloadable, but its HOLDOUT-DTI is negative and global uniqueness fails.

### RELIEF and DILATATION — positive local holdout, failed literal uniqueness rule

Their saved run cards report positive catalogue-derived holdout deltas. However, 99.37–99.40% of their dots lie within 3 px of registered parent R0, above the operator's 70% duplication threshold. Record them as duplicates; do not substitute arrival-set comparisons for the stated whole-dot rule. Their local result does not clear them for a slot.

### Historical comparison

TIPGAP FAR clears the recorded R0 overlap threshold at 67.00% of dots within 3 px but its `gems57-pooled-hide-v2` HOLDOUT-DTI is below R0. It remains a negative deliverable. The conflicting trade-off is evidence against another derivative of the same parent, not a reason to reinterpret the lane gate.

## Candidate hypotheses for a future reset

Three to five untried hypotheses with layer names, physical signatures, why they might detect unmapped structures, differences from implemented methods, qualitative priority/cost, non-fault mimics, and data availability are in [`hypotheses_20261024.md`](hypotheses_20261024.md). The current highest-priority idea cannot be tested here because the authorized 19-band feature stack is absent from `.cache/gems_inputs/`. The official DrivenData data page is login-gated in this environment. No experiment was started and no weekly slot was touched.

Before any future slot selector action: restore authorized inputs and verify hashes; run each feature-alone leakage canary; use whole-segment buffered holdout, visible-only features, exact visible-catalogue mask, pooled DTI and 95% CI; run correlation/overlap checks before and after placement; stop on a duplicate; and run local format checks on the actual served bytes.

## Sources and verification boundaries

- [DrivenData problem and metric page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) — consulted directly; it describes the goal, incomplete known-fault data, feature classes, and distance-weighted Tversky metric.
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) — public code/repository; it is a baseline, not an organizer receipt for this candidate.
- [USGS GeoDAWN catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) — official data provenance.
- [DOE GDR INGENIOUS #1391](https://gdr.openei.org/submissions/1391) — source link.
- [Official competition rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf).

Source-page availability is not the same as local input availability. This review checked the local repository and official references; it did not access DrivenData account-only data, private test truth, or a submission receipt.
