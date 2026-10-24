# Submission executive summary — GEMSDOE92 candidate

## Status: OK TO DOWNLOAD, NOT CLEARED TO SUBMIT

The primary file is a format-valid, all-finite, zeros-outside float32 GeoTIFF and passes all 10 local MUST gates. The separate uniqueness gate **fails**: a broader scan of 1,279 same-grid registry rasters found 100% forward 3-px overlap with multiple registry rasters (131 exceed the 70% stop threshold). Per the operator's literal protocol, this is a duplicate and must not consume a competition slot.

- [Download candidate TIF (negative deliverable)](downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif)
- [Download ZIP containing one TIFF](downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.zip)
- [Format + public-registry audit](downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-audit.json)
- [Full run card](downloads/visible_collar_run_card.json)
- [Public registry scan and scope](downloads/public_registry_uniqueness.json)

**Do not submit this candidate.** The holdout improvement does not override the duplicate stop. No slot was used.

## Research evidence (not a contest score)

**HOLDOUT-DTI** — evaluator `gems57-pooled-hide-v2`; eight buffered spatial folds (four quadrants × seeds 20 and 30); 22,663 withheld catalogue positives; α=0.2, β=0.8, 300 m triangular kernel; 1,000 paired 20 km spatial-cluster bootstrap draws:

- Candidate: `0.046866`, 95% CI `[0.040216, 0.053315]`.
- Parent R0: `0.004006`, 95% CI `[0.003424, 0.004690]`.
- Paired difference: `+0.042860`, 95% CI `[+0.036122, +0.049357]`.
- Leakage canary, visible-fault distance alone: symmetric AUC `0.745593` (<0.90 stop).

This hide-and-recover result rewards recovery of mapped catalogue structure and does not show live performance on private, genuinely uncatalogued faults.

## GeoTIFF format audit

All ten local gates pass: one float32 band; EPSG:32611; shape 3730×3292; matching sample geotransform; finite values in `[0,1]`; no NaN inside the footprint; zeros outside; no positive catalogue mass. This is **format-valid/downloadable**, not **submission-eligible**.

## Form fields (for archive/review only; not a recommendation to upload)

- Name: `GEMSDOE92-visible-collar-r0-excluded-20261024`
- Note (62 characters): `Visible-fault collar 2-3 px; R0 3px halo excluded; 37,654 dots`
- SHA-256: `60082b75a3d8e4648a858622f71f24257c8cfef79286a1a96147c59f05377da7`

The human competitor must authenticate and use the separate selector/weekly quota; this agent does not upload or spend a slot. The registration audit scope covers current public default branches in 102 owner repositories, not all historical/private/site-hosted or other-owner files. The duplicate witness is sufficient to stop under the literal rule.

## Context: GEMSDOE32 claim and leaderboard

`h33-h33-2-b2` at `0.2778` is an owner-reported **CLAIM** without an organizer receipt in this ledger. A plausible, unproven mechanism is a fixed budget of ridge candidates, spatial thinning to reduce redundant mass, pruning, and avoiding known traces under the distance-tolerant asymmetric DTI. The exact evaluated artifact and private truth are unavailable here, so the cause cannot be established.

The repository records a 2026-10-24 read of the official public leaderboard showing `0.4413` at #1 (**LEADERBOARD-SNAPSHOT**, not a receipt for GEMSDOE32 or this candidate); the prompt's `0.3195` is an older conflicting snapshot. This HOLDOUT-DTI is not comparable to either public leaderboard value. A genuine score comparison requires an organizer receipt after a separate human submission.

Canonical HTML: [`SUBMIT.html`](SUBMIT.html). Main site: [`index.html`](index.html).
