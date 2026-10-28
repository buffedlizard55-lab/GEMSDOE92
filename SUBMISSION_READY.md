# Current independent review — 2026-10-28 · session 47314b7f

**RESEARCH DOWNLOAD ONLY · DO NOT SUBMIT.** Prior clearance is withdrawn. Fresh pinned-witness checks find 100% literal overlap (>70%) before placement and on all 50,000 existing dots. The archived candidate HOLDOUT-DTI also fails its R0 control. No new TIFF, geological experiment, or weekly submission slot was generated/used.

[Executive summary and nine-site table](docs/review-47314b7f.html) · [Run card](docs/downloads/review_47314b7f_run_card.json) · [Fresh preflight](evidence/review_47314b7f_preflight.json) · [Fresh final-dot validation](evidence/review_47314b7f_overlap.json).

Read [SESSION_PROMPT.md](SESSION_PROMPT.md) before each session. The user asks for a unique validated TIFF, shared holdout tools, no projections as scores, literal registry stop, separate selector, and at most three experiments/two hours. No distinct single-method paragraph was supplied. Maximize P(Win) and Own the Outcome require reporting a blocker rather than inventing clearance. See the current executive summary for access limitations and next steps.

<details><summary>Superseded reports — not current clearance</summary>

# SUBMISSION READY — 2026-10-27 (session ee2370c1)

**✅ OK TO SUBMIT** (all automated gates passed: format, PI-1 uniqueness, leaderboard-aligned MODEL > 0.2778 at the 5% bound, robustness, no leakage)

* File: [`docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif`](docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif)
* SHA-256: `e928d3c3fde8b3f1f622bb4f6e638620f0a1897fb6f8178cf26fe93f9c3b3a1c`
* Submission name: `gemsdoe92-lbmc1-35801d-89a660f6`
* Note: `LBM-consensus v1: 35801 dots by exact expected-DTI greedy on a truth density fit to 123 scored rasters; 70%/3px registry caps.`
* Expected public DTI: 0.332 (90% interval 0.313–0.351). This is a MODEL estimate, not an organizer score.
* Steps: [docs/how-to-submit.html](docs/how-to-submit.html). Weekly limit: 3 per week; the website's limit prevails.
* Interpretation flags for the owner: IR-0127-1 (PI-1 duplicate rule) and IR-0127-2 (holdout misalignment) in [IRREGULARITIES.md](IRREGULARITIES.md).


---

## Historical (superseded 2026-10-27 by the decision above)

**✅ OK TO DOWNLOAD FOR RESEARCH. ⛔ DO NOT SUBMIT — automated promotion gates not met (see run card).**
The pre-registered VARIO lane generated this historical research GeoTIFF on 2026-10-25; it is not registry-unique and no new TIFF was generated in this review.
([hypotheses](docs/HYPOTHESES_20261025_VARIO.md) · [analysis](docs/ANALYSIS_20261025_VARIO.md) ·
[executive submission guide](docs/vario.html) · [run card](docs/downloads/vario_run_card.json) ·
[machine-readable status](docs/downloads/readiness.json)).

[Download gemsdoe92-vario-full-37654-20261025-3c30a41c-zeros.tif](docs/downloads/gemsdoe92-vario-full-37654-20261025-3c30a41c-zeros.tif) · name `GEMSDOE92-VARIO-full-20261025` · note (72/140) `VARIO full: 24phys+semivar+MTcp+topo10+ctx LOQO; 37654 dots 2.8px dcat>2` · SHA-256 `11f92e382b04a2f368c2259d6b092248efe338dd9a81436de4f27217c3b44573`

Automated validation (no human inspection): finite [0, 1] everywhere, no masked or NaN cells in the footprint, zeros outside, exact CRS/shape/transform. This is a local check, not a guarantee of portal acceptance. **HOLDOUT-DTI** (gems57-pooled-hide-v2, 22663 withheld): `0.150020 [0.134975, 0.164286]`; paired Δ vs best control `control_FAULTNET_far`: `-0.025127 [-0.029306, -0.020842]`. No ORGANIZER-CONFIRMED score; GEMSDOE32 0.2778 and all site-inventory scores remain CLAIMs. Under the conservative rule treating every positive pixel of a continuous-probability raster as a dot, the dense-registry stop is binding. Whether that representation is intended remains unresolved; it is not proof of geological identity, and sparse-only comparison is not clearance. Historical banners below are archives, not current clearance.

<!-- VARIO-STATUS:END -->

## Independent review — 2026-10-26: no submission eligible

**⛔ DO NOT SUBMIT.** No new TIFF or geological experiment was generated in this review, and no slot was selected or spent. The pinned, independently re-fetched 17GEMSDOE witness is positive on all 5,167,373 finite template cells, so literal forward overlap is `1.000 > 0.70` for every nonempty candidate. The rejection is binding before placement. [Review run card](docs/downloads/review_14f85876_run_card.json) · [nine-site executive summary and future-only submission guide](docs/focus9.html).

- **Research only:** the primary VARIO file and its historical name, note and SHA-256 appear in the byte-bound panel above. Its local format gates pass; it is not registry-unique and is not approved for upload. Local zeros outside the sample footprint do not establish compliance with the organizer's null/NaN-outside-study-bounds wording or guarantee portal acceptance.
- **Nine sites:** GEMSDOE32's `h33-h33-2-b2` value `0.2778` is the highest reported among the nine, but is an owner **CLAIM** without an organizer receipt binding score to file. All nine fail at least one directed pairwise comparison. An independent row-safe recheck changed numeric overlap values for 35 of 36 pairs without changing any duplicate decision; the cause of the previous discrepancy is unproven. [Corrected pairs](docs/downloads/focus9_pairwise_recheck_14f85876.json) · [historical source inventory](docs/downloads/focus_sites_release_review_20261026.json).
- **Score estimate unavailable:** the archived model's 107 owner-claim targets are not receipts, related records cross row-wise folds, and its saturation cap was selected globally. Neither row-wise RMSE nor our partial grouped diagnostic is an individual prediction interval. [Reproducible diagnostic](docs/downloads/score_estimator_audit_14f85876.json).
- **Official context:** the [public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) is not monitored or mirrored; no public row is this project's receipt. [DrivenData terms](https://www.drivendata.org/termsofuse/) prohibit automated website access for monitoring or copying. [DrivenData staff](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2) say known USGS/INGENIOUS fault pixels are excluded from evaluation; the effect of an additional distance collar is not established.
- **Prior SALEMSEISMO:** [historical research TIFF](docs/downloads/h33-h33-2-b2-SALEMSEISMOcelftail52k-20261026-cc3c8ff2-zeros.tif) · [historical run card](docs/downloads/salemseismo_run_card.json). The runner scanned after placement and examined public rank correlations only for selected witnesses, not every raster. A former flattened-index halo could wrap at row boundaries; affected archived scan values require rechecking. Static re-scores of already-built predictions are not necessarily leakage-free prospective holdouts. The runner is disabled; **do not submit**.
- **Next:** The [five ranked hypotheses](docs/HYPOTHESES_20261026_SITE_REVIEW.md) remain untested. Resolve the literal rule through an authorized protocol decision and assign a method paragraph before any new experiment. Preserve whole-segment buffered holdouts, visible-fault-only features, the shared evaluator/writer, canaries, and a separate selector.

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

</details>
