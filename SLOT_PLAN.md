# Slot plan — no selection currently authorized

**Decision:** no file in this checkout is cleared or recommended for a competition slot. This document does not select a submission. Slot promotion is a separate selector step and remains outside the agent's remit.

The current primary is downloadable **for review only**. It passes the project's local value-range/geometry checks, but (a) its zeros-outside encoding conflicts with the official problem page's stated null/NaN outside-bounds requirement, and (b) it **fails uniqueness** by breaching the literal local threshold against registry parent R0. Do not upload it. A local checker pass is not organizer validation.

## Verified official submission requirements

The current DrivenData problem page says the submission must be a single-layer float32 GeoTIFF, predictions in [0,1], EPSG:32611, 100 m resolution, matching bounds, and null/NaN outside bounds. The page was retrieved in this review. The official data page redirected to login. No authenticated submission check or organizer receipt is stored here.

- Problem description / metric / format: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- Official data page: <https://www.drivendata.org/competitions/306/competition-doe-gems/data/>
- Reference solution: <https://github.com/drivendataorg/gems-prize-reference-solution>
- Detailed current review and sources: [`docs/RESEARCH_AND_CANDIDATE_REVIEW_20261024.md`](docs/RESEARCH_AND_CANDIDATE_REVIEW_20261024.md)

## Existing local evidence (not leaderboard scores)

Every entry below is **HOLDOUT-DTI**, evaluator `gems57-pooled-hide-v2`, with 22,663 withheld catalogue positives and the listed 95% CI. These historical holdout artifacts were not independently recomputed during this review because the full 19-band feature stack is absent from `data/` and `.cache/`.

| Existing arm | HOLDOUT-DTI (95% CI) | Disposition | Local registry check |
|---|---|---|---|
| R0 parent | 0.004006 [0.003424, 0.004690] | Baseline; historical claimed live score 0.2778 has no receipt in this checkout | Registered parent raster |
| DILATATION p10 | 0.005747 [0.004867, 0.006788] | Negative for promotion | 99.40% within 3 px of R0; duplicate-stop |
| DILATATION p12 | 0.005779 [0.004863, 0.006851] | Negative for promotion | Recomputed in `scripts/check_site.py`: Spearman 0.879132; 99.373241% within 3 px of R0; duplicate-stop |
| DILATATION p15 | 0.005818 [0.004838, 0.006912] | Negative for promotion | 99.37% within 3 px of R0; duplicate-stop |
| RELIEF p10 | 0.006045 [0.005187, 0.006927] | Negative for promotion | 99.38% within 3 px of R0; duplicate-stop |
| TIPGAP FAR | 0.002723 [0.002324, 0.003131] | Negative; below R0 | 67.00% within 3 px of R0 in its recorded local screen; this alone is not global uniqueness clearance |

The holdout evaluates recovery of withheld catalogue structure, not hidden organizer labels. A positive catalogue holdout is not evidence that an arm will score better on the competition's private set or final expert-expanded labels.

## Promotion gates before any selector considers a slot

1. Obtain the official competition feature stack through the authorized data page and verify its approved hash/provenance. Do not treat owner mirrors as official data when redistribution/usage terms are unresolved.
2. Propose three to five scientifically distinct hypotheses with a named non-fault mimic, then choose one active lane. Do not exceed the shared three-experiment / two-hour budget.
3. Run each feature alone as a leakage canary. AUC above 0.90 is a stop pending leakage investigation.
4. Before placement, compare the candidate score surface against a complete, refreshed local registry; after placement, compare final dots. Stop if Spearman exceeds 0.90 or more than 70% of candidate dots fall within 3 px of any registry raster.
5. Reuse the shared whole-segment buffered hide-and-recover evaluator and writer; report pooled DTI, evaluator version, withheld-positive count, paired 95% CI, raster SHA-256 and validator output. A projection is never a score.
6. Reconcile the official null/NaN outside-bounds requirement with the portal's range validation. Do not claim format compliance from the current zeros-outside preflight alone.
7. Only candidates that pass uniqueness, holdout and official-format gates may be sent to a separate human selector. The agent does not rank or select competition slots, authenticate, upload, or claim organizer results without a receipt.

## Run card for this review

The current diagnostic artifact and blocked new candidate are recorded in [`evidence/review_run_card_20261024.json`](evidence/review_run_card_20261024.json). The proposed extensional-strain-coherence candidate is `BLOCKED_NOT_RUN` because its official feature stack is unavailable; zero experiments and zero weekly slots were spent in this review.
