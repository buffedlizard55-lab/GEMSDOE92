# Submission clearance withdrawn — DO NOT SUBMIT

<!-- VARIO-STATUS:BEGIN -->
## Current research download — verified decision, 2026-10-25 (VARIO session)

**✅ OK TO DOWNLOAD FOR RESEARCH. ⛔ DO NOT SUBMIT — automated promotion gates not met (see run card).**
A new unique GeoTIFF **was** generated this session by the pre-registered VARIO lane
([hypotheses](docs/HYPOTHESES_20261025_VARIO.md) · [analysis](docs/ANALYSIS_20261025_VARIO.md) ·
[executive submission guide](docs/vario.html) · [run card](docs/downloads/vario_run_card.json) ·
[machine-readable status](docs/downloads/readiness.json)).

[Download gemsdoe92-vario-full-37654-20261025-3c30a41c-zeros.tif](docs/downloads/gemsdoe92-vario-full-37654-20261025-3c30a41c-zeros.tif) · name `GEMSDOE92-VARIO-full-20261025` · note (72/140) `VARIO full: 24phys+semivar+MTcp+topo10+ctx LOQO; 37654 dots 2.8px dcat>2` · SHA-256 `11f92e382b04a2f368c2259d6b092248efe338dd9a81436de4f27217c3b44573`

Automated validation (no human inspection): finite [0, 1] everywhere (the portal "Predicted values must be in range [0, 1]" check), no NaN in footprint, zeros outside, exact CRS/shape/transform. **HOLDOUT-DTI** (gems57-pooled-hide-v2, 22663 withheld): `0.150020 [0.134975, 0.164286]`; paired Δ vs best control `control_FAULTNET_far`: `-0.025127 [-0.029306, -0.020842]`. No ORGANIZER-CONFIRMED score; GEMSDOE32 0.2778 and all site-inventory scores remain CLAIMs. Literal dense-registry disclosure and operative sparse uniqueness are both in the run card. Historical banners below are archives, not current clearance.

<!-- VARIO-STATUS:END -->

## Current lane — 2026-10-26 (`SALEMSEISMO`, 3/3 experiments, 0 weekly slots)

**✅ OK TO DOWNLOAD FOR RESEARCH · ⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT** (`verdict: negative`, `submission_eligible: false`, `0` slots spent).

- **New unique GeoTIFF:** [`h33-h33-2-b2-SALEMSEISMOcelftail52k-20261026-cc3c8ff2-zeros.tif`](docs/downloads/h33-h33-2-b2-SALEMSEISMOcelftail52k-20261026-cc3c8ff2-zeros.tif) · [one-TIFF ZIP](docs/downloads/h33-h33-2-b2-SALEMSEISMOcelftail52k-20261026-cc3c8ff2-zeros.zip) · [audit](docs/downloads/h33-h33-2-b2-SALEMSEISMOcelftail52k-20261026-cc3c8ff2-audit.json) · [Rule 5 run card](docs/downloads/salemseismo_run_card.json) · [holdout](docs/downloads/salemseismo_holdout.json) · [uniqueness](docs/downloads/salemseismo_uniqueness.json).
- **Nine-site executive summary with the download / estimate / uniqueness table:** [`docs/focus9.html`](docs/focus9.html) (rendered from committed JSON receipts by `scripts/render_focus9_page.py`).
- **Estimated DTI `0.0832 ± 0.0722`** — a cross-validated **MODEL** value (leave-one-out RMSE on 107 owner-reported CLAIMs, LOO Spearman `0.750`), **never** a score. Class-consistent comparison: GEMSDOE32 `h33-h33-2-b2` CLAIM `0.2778` → MODEL `0.2519`; GEMSDOE70 `p5-dual-submod` CLAIM `0.2478` → MODEL `0.1908`.
- **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives): static `d_cat>2` **`0.015948`** [`0.013683`, `0.018370`] — above the previous static-SOTA control `LISTRICLOQO selectcal` `0.013295`; strict draw-blind Rule-2 **`0.099345`** [`0.084948`, `0.113946`].
- **Uniqueness (REGISTRY-MEASUREMENT):** worst 3-px overlap **`0.6447 <= 0.70`** across **1,756** compatible public rasters in **102** repositories (`0` over 0.70); worst |ρ| `0.0573 <= 0.90`. It is **not** a copy of GEMSDOE24/25/27/28/30/31/32/33/36 (their best files sit at 0.87–1.00 similarity to each other; this file does not).
- **Automated validation (no human inspection):** 11/11 gates PASS — single-band `float32`, EPSG:32611, 3730×3292, all 12,279,160 cells finite in `[0,1]`, 0 NaN, zeros outside the footprint, 0 dots on the mapped catalogue, all dots >2 px from it; `26/26` leakage canaries PASS (max symmetric AUC `0.6077`).
- **Form fields (record only; do not upload until the badge is green):** name `GEMSDOE92-SALEMSEISMO-celftail52k-20261026` · note (112/140) `SALEMSEISMO celftail52k: 52000px Salem-tilt+Walker-seismo+10m-toe+ThK CELF; HOLDOUT-DTI 0.0993 (st 0.0159) [neg]` · SHA-256 `b06dd72feff35b1631a17a52581b46d9b21b92fcba09441eac77d6daa9ba1dda`.
- **Why the badge is red:** the binding literal registry rule reads overlap `1.0000 > 0.70` against the pinned `17GEMSDOE_E-proba-multiscale` surface, which is positive on every footprint cell — so no non-empty file can ever clear it. That is an owner policy decision (see §6 of `docs/focus9.html`), not a defect in this file.


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
