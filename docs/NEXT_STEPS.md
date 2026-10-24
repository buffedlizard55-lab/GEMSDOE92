# Next steps — current status as of 2026-10-24 UTC

## Current decision

The existing ANASIG TIFF is format-valid for research but **NOT CLEARED — DO NOT SUBMIT**. A fresh `REGISTRY-MEASUREMENT` confirms 100% final-dot overlap with one hash-verified 17GEMSDOE raster positive on the entire footprint. This is one sufficient negative witness, not a full public scan. No new model, holdout experiment, or TIFF was generated; no slot was used.

The older 1,279-raster scan / 11GEMSDOE finding is for the visible-collar candidate, not ANASIG. See [`REVIEW_CURRENT.md`](REVIEW_CURRENT.md), the [ANASIG witness receipt](downloads/public_witness_anasig.json), and the [current run card](downloads/current_registry_stop_run_card_20261024.json).

## Blockers before any candidate work

1. **Resolve the literal uniqueness policy outside model work.** The witness is positive at every footprint cell, so every nonempty in-footprint candidate gets 100% forward overlap and fails the stated >70% rule. Do not generate a candidate, reinterpret the rule, or move dots outside the valid domain.
2. **Verify data access and terms.** The large feature stack is missing from `.cache/gems_inputs/`. `registry/session_manifest.json` pins owner-mirror bytes but does not authenticate them with the organizer or establish redistribution permission. Verify official provenance, access, license/terms, and exact hashes before restoration.
3. **Choose one lane only after those gates clear.** The [ranked hypothesis page](HYPOTHESES.html) is backlog-only; all external sources are explicitly unverified and every candidate is marked not viable now.

## If policy and provenance are later resolved

- Follow the canonical protocol in the [repository README](https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/README.md): one named method lane, actual surface comparison before placement, final-dot comparison after placement, duplicate stop at absolute Spearman >0.90 or >70% forward 3-pixel overlap against any one accessible raster.
- Reuse the shared cached stack, `vendor/gems57/evaluate_holdout.py`, and `vendor/gems57/submission_writer.py`. Hold out whole fault components with a buffer, derive catalogue features from visible faults only, mask visible faults pixel-exactly, use pooled DTI α=0.2 / β=0.8 / 300 m triangular kernel, and run feature-alone leakage canaries. AUC >0.90 is leakage until investigated.
- Automate the exact-byte TIFF gates and complete run card. Stop after three experiments or two hours. Promotion is a separate selector decision under the weekly cap; do not choose a submission slot here.

## Current score/evidence boundary

ANASIG's prior result is **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 22,663 withheld positive pixels, 95% CI: `0.004967 [0.004098, 0.005940]`. It is below the prior local HOLDOUT-DTI best and is not a competition score. `0.2778` remains a **CLAIM**; `0.3195` and `0.4413` remain unverified **LEADERBOARD-SNAPSHOT** values. No fresh official leaderboard read or organizer receipt was obtained. See [`ledger/score_claims.csv`](https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/ledger/score_claims.csv).
