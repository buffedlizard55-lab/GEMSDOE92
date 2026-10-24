# Submission executive summary — GEMSDOE92 candidate

## Current site primary: STEPEDGE f60Sraw (2026-10-24) — unique, OK TO DOWNLOAD, DO NOT SUBMIT

New this session: aperture-persistent sustained DEM steps (Band 12). Format-valid
zeros-outside float32 (all gates; [0,1]; 37,654 dots) and **literal-unique vs the
28-raster local dot registry** (surface |ρ| 0.138; final worst forward overlap
0.461, |ρ| 0.396). Verdict **negative by automated gates** (`submission_eligible:
false`, no human inspection): HOLDOUT-DTI 0.003980 [0.003295, 0.004702]
(`gems57-pooled-hide-v2`, 22,663 withheld) does not beat STRAINBREAK f60
(0.005487) or RELIEF p10 (0.006045); paired Δ vs R0 includes 0. SGMC PROXY
0.141464 (repo best) disagrees — holdout gate governs. Dense public-witness
literal overlap 1.000 disclosed (ρ 0.0004). Sibling doses f33/f45 are
duplicates (0.760/0.711); never submit them.

- [Download STEPEDGE TIF (negative deliverable)](downloads/h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif) · [ZIP](downloads/h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.zip) · [audit](downloads/h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-audit.json) · [run card](downloads/stepedge_run_card.json) · [analysis](ANALYSIS_20261024_STEPEDGE.md) · [hypotheses](HYPOTHESES_20261024_STEPEDGE.md)
- Name: `GEMSDOE92-STEPEDGE-f60Sraw-20261024` · Note (93): `h33-h33-2-b2; STEPEDGE f60Sraw 22592 far dots on aperture-persistent DEM steps >3px off H19-5` · SHA-256 `c5dc98f2846ae486e022a7bdae1840334e73c03af44c03e9867c03b6f16d07b4`
- If a future artifact's audit ever says `submission_eligible: true`: download the zeros-outside .tif unedited → DrivenData New submission → exact name/note → record the organizer receipt in `ledger/submissions.csv`. This agent does not upload.

## Parallel artifact: STRAINBREAK f60s2i — OK TO DOWNLOAD, NOT CLEARED TO SUBMIT

Format-valid zeros-outside float32 GeoTIFF (10/10 local MUST gates; values in [0,1], no NaN in footprint). Verdict **negative**: HOLDOUT-DTI 0.005487 [0.004522, 0.006430] (evaluator `gems57-pooled-hide-v2`, 22,663 withheld positives) beats R0 0.004006 but not the holdout best (RELIEF p10 0.006045), and the USGS SGMC off-catalogue control prefers BREAKLINE f45 (0.12611 vs 0.10516). Local literal uniqueness passes (worst forward 3-px overlap 40.0%, 21 rasters); the expanded public-registry result is in the audit receipt. **Do not spend a weekly slot without a separate human selector decision.**

- [Download STRAINBREAK TIF (negative deliverable)](downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif) · [ZIP](downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2.zip) · [audit](downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-audit.json) · [run card](downloads/strainbreak_run_card.json) · [hypotheses](HYPOTHESES_20261024_GRAVCrest.md)
- Name: `GEMSDOE92-STRAINBREAK-f60s2i-20261024` · Note (87): `h33-h33-2-b2; STRAINBREAK f60s2i 22592 far dots on strained scarp-breaks >3px off H19-5` · SHA-256 `000d0bd7e0a549c2d38ca52a5df5b249763a7be998ad2ccfa30cc45136c05c1f`
- If a slot is ever cleared: download zeros-outside .tif unedited -> DrivenData New submission -> exact name/note -> record organizer receipt in `ledger/submissions.csv`. This agent does not upload.
- This session's rank-1 GRAVCrest hypothesis was falsified by the pre-build SGMC screen and never built (`evidence/gravcrest_screen.json`).

## Parallel artifact: ANASIG f45 (prior site primary) — do not submit

Prior site primary was the ANASIG candidate (`GEMSDOE92-ANASIG-f45Atop-20261024`); see `index.html` / `SUBMIT.html` and `downloads/anasig_run_card.json`. It is likewise format-valid and **not cleared** (literal registry stop). STRAINBREAK above is a parallel-session negative deliverable, not a replacement primary.

## Previous artifact: visible collar — duplicate, do not submit

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

## Parallel-session artifact — BREAKLINE f45Ltop (not cleared, negative)

- [Download BREAKLINE TIF](downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif) · [ZIP](downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0.zip) · [gate audit](downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-audit.json) · [run card](downloads/breakline_run_card.json) · [analysis](ANALYSIS_20261024.md)
- Name: `GEMSDOE92-BREAKLINE-f45Ltop-20261024` · Note (90): `h33-h33-2-b2; BREAKLINE f45Ltop 16944 far dots on linear scarp-break ridges >3px off H19-5` · SHA-256 `cd9c8a564588e6542b379cd36cbe05fc6da3be07b8edbc542bf737336907810e`
- HOLDOUT-DTI `0.004861 [0.004032, 0.005822]` (delta vs R0 +0.000854 [+0.000300, +0.001423]); unique within the 18-raster **local** registry (worst 55.0% vs R0; 3.5% vs the collar candidate) and below the holdout-best arms; update 2026-10-24: expanded public scan (1,309 rasters) run — literal duplicate stop triggers (134 >70%; `evidence/breakline_public_registry_uniqueness.json`) → **NOT CLEARED; do not submit without a human selector decision.** If a slot is ever spent: zeros-outside .tif unedited -> DrivenData New submission -> exact name/note -> record receipt in `ledger/submissions.csv`. Never submit more than one BREAKLINE dose.

Canonical HTML: [`SUBMIT.html`](SUBMIT.html). Main site: [`index.html`](index.html).
