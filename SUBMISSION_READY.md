# Submission clearance withdrawn — DO NOT SUBMIT

<!-- CURRENT-STATUS:BEGIN -->
## Authoritative decision — Current verified status, 2026-10-25 (LISTRICLOQO 2026-10-25)

**Also 2026-10-25 — ALI lane: a NEW raster was generated and tested — DO NOT SUBMIT.** [Download it for research](docs/downloads/gemsdoe92-ali-famnms-37654-20261025T230000Z-68be9b4d-zeros.tif) · [full report](docs/ALI_LANE.md) · [run card](docs/downloads/ali_run_card.json). Reasons: **duplicate under the registry rule** (0.806 of its dots lie within 3 px of 12GEMSDOE `12GEMSDOE_r7-nms3-dem10-scarp_0c9199f14e62_allfinite.tif`, whose halo covers only 0.317 of the domain; 30 discriminating dot fields exceed 0.70), and HOLDOUT-DTI 0.097216 [0.079836, 0.117747] only ties the R0-recipe control 0.097493 (paired Δ -0.000278 [-0.015980, +0.015900]; gems57-pooled-hide-v2, 22663 withheld positives).

**OK TO DOWNLOAD FOR RESEARCH. DO NOT SUBMIT.** LISTRICLOQO is a byte-distinct research artifact, but it fails the literal registry-overlap stop and promotion gates.

[Existing LISTRICLOQO research TIFF — not cleared to submit](docs/downloads/h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif) · [protocol run card](docs/downloads/listric_loqo_run_card.json) · [analysis](docs/ANALYSIS_20261025_LISTRICLOQO.md) · [three-pass review](docs/REVIEW_20261025_SESSION.md) · [supplemental initial audit](docs/REVIEW_20261025_SESSION_FOLLOWUP.md) · [audit run card](docs/downloads/session_followup_20261025_run_card.json) · [later leaderboard review](docs/ANALYSIS_20261025_LEADERBOARD.md) · [executive submission guide](docs/executive-summary.html).

Automated format checks pass. HOLDOUT-DTI (`gems57-pooled-hide-v2`, 22,663 withheld positives) is `0.013295 [0.011713, 0.014980]`; paired improvement over KNICKLOQO is +0.002508 [0.001477, 0.003463]. Public dual-reading overlap is `0.690259 <= 0.70`, but the binding literal dense-witness overlap is `1.0 > 0.70`; this file is not uniqueness-cleared. No ORGANIZER-CONFIRMED score is available; 3/3 experiments and zero weekly slots.

<!-- CURRENT-STATUS:END -->

For the evidence review of the user-reported GEMSDOE32 `0.2778` value, see [the sourced explanation and evidence limits](docs/BEAT_0_2778.md). The value is not a verified organizer receipt.

<details data-status-archive="true">
<summary>Archived parallel-lane reports — not current submission clearance</summary>


The clearance published in commit `406638a` was not supported by the binding
literal overlap rule. The known registry witness covers the entire footprint;
all nonempty candidates remain blocked. No new unique TIFF was produced by
renaming or repackaging KNICKLOQO.

- [Current byte-bound status](docs/downloads/readiness.json)
- [Research downloads and executive summary](docs/executive-summary.html)
- [Corrected KNICKLOQO status receipt](docs/downloads/knickloqo_submission_run_card.json)
- [Three-pass review and limitations](docs/REVIEW_F23.md)

The prior TIFF hash correction is valid. A fresh read found the newly published
run card's file size, shape order and transform were wrong, however. Its
projected leaderboard scores and guaranteed portal acceptance were unsupported.
These claims have been withdrawn, not replaced by another projection.

`python validate_submission.py` now delegates to the shared readiness checks and
returns a blocked exit status. A format PASS does not authorize a competition
slot. The original publication is preserved in Git history for audit.
</details>

# GAPBRIDGE unique TIF generated 2026-10-25 — ✅ OK TO DOWNLOAD · ⛔ DO NOT SUBMIT YET
File: docs/downloads/gemsdoe92-gapbridge-ctx-37654-20261025-zeros.tif · SHA-256 14f37bb37fb27ece491b79c16a9b8a29d7c90c18755287ee4c636643ee42219d · Validator 11/11 PASS (values [0,1], no NaN) · Uniqueness worst overlap 0.4376 / |rho| 0.086 (PASS local registry) · HOLDOUT-DTI 0.1015 [0.0887,0.1126] (gems57-pooled-hide-v2, 22,893 withheld) vs R0 0.0039 — does NOT beat repo best 0.1751, so weekly slot NOT cleared. See docs/gapbridge.html + run card docs/downloads/gemsdoe92-gapbridge_run_card.json.
