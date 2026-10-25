# Submission clearance withdrawn — DO NOT SUBMIT

<!-- CURRENT-STATUS:BEGIN -->
## Current verified decision — 2026-10-25

**Newest session (2026-10-25, ALI lane): a NEW raster was generated and tested — DO NOT SUBMIT.** [Download it for research](docs/downloads/gemsdoe92-ali-famnms-37654-20261025T230000Z-68be9b4d-zeros.tif) · [full report](docs/ALI_LANE.md) · [run card](docs/downloads/ali_run_card.json). Reasons: **duplicate under the registry rule** (0.806 of its dots lie within 3 px of 12GEMSDOE `12GEMSDOE_r7-nms3-dem10-scarp_0c9199f14e62_allfinite.tif`, whose halo covers only 0.317 of the domain; 30 discriminating dot fields exceed 0.70), and HOLDOUT-DTI 0.097216 [0.079836, 0.117747] only ties the R0-recipe control 0.097493 (paired Δ -0.000278 [-0.015980, +0.015900]; gems57-pooled-hide-v2, 22663 withheld positives).

**OK TO DOWNLOAD FOR RESEARCH. DO NOT SUBMIT.** No new unique TIFF exists: the new ALI raster is a registry duplicate, so no file is cleared for a weekly slot. Primary research download below (review c5e3848c, unchanged earlier file):

[Current research download](docs/downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif) · [fresh run card](docs/downloads/review_c5e3848c_integrated_run_card.json) · [three-pass review](docs/REVIEW_C5E3848C.md) · [executive submission guide](docs/executive-summary.html).

Automated format checks pass on the unchanged primary; literal registry overlap is 1.0 and requires stopping before placement. Historical “newest”, “unique” and holdout rankings below are not current clearance. Review c5e3848c reran no HOLDOUT-DTI; no ORGANIZER-CONFIRMED score is available. Weekly slots used: zero.

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
