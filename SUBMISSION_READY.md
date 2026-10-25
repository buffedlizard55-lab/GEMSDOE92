# Submission clearance withdrawn — DO NOT SUBMIT

<!-- CURRENT-STATUS:BEGIN -->
## Authoritative decision — Current verified status, 2026-10-25 (LISTRICLOQO 2026-10-25)

**OK TO DOWNLOAD FOR RESEARCH. DO NOT SUBMIT.** The completed LISTRICLOQO lane generated a byte-unique TIFF, but it failed promotion gates.

[Current unique research download](docs/downloads/h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif) · [protocol run card](docs/downloads/listric_loqo_run_card.json) · [analysis](docs/ANALYSIS_20261025_LISTRICLOQO.md) · [executive submission guide](docs/executive-summary.html).

Automated format checks pass. HOLDOUT-DTI (`gems57-pooled-hide-v2`, 22,663 withheld positives) is `0.013295 [0.011713, 0.014980]`; paired improvement over KNICKLOQO is +0.002508 [0.001477, 0.003463]. Public dual-reading overlap is `0.690259 <= 0.70`, and literal dense-witness overlap is `1.0`. No ORGANIZER-CONFIRMED score is available; 3/3 experiments and zero weekly slots.

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
