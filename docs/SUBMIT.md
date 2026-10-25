# Executive summary — GEMSDOE92 submission workbench

<!-- CURRENT:BEGIN -->
> ## Newest completed session lane (`2026-10-25`) — `CHILISTRIC` / primary arm `addtail52k` (3 new unique-byte GeoTIFFs)
> **✅ OK TO DOWNLOAD FOR RESEARCH** (`11/11` automated `[0, 1]` gates PASS, `0` NaN; unique across all `124` post-merge local rasters at `0.6773 <= 0.70` & all `1,503` public rasters across `102` repos at `0.6351 <= 0.70`) · **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT** (verdict `negative`, `submission_eligible: false`; literal `17GEMSDOE` dense witness `1.000 > 0.70` & static tie vs `LISTRICLOQO` `0.013295`; `0` weekly slots spent).
>
> **[⬇ Download research GeoTIFF (`h33-h33-2-b2-CHILISTRICaddtail52k-20261025-8c82904d-zeros.tif`)](downloads/h33-h33-2-b2-CHILISTRICaddtail52k-20261025-8c82904d-zeros.tif)** · [one-TIFF ZIP](downloads/h33-h33-2-b2-CHILISTRICaddtail52k-20261025-8c82904d-zeros.zip) · [JSON Run Card](downloads/chilistric_run_card.json) · [Executive Summary & How to Submit](executive-summary.html) · [PhD Analysis (`0.2778` / `0.3195` / `0.4413` & Verified Sources Table)](ANALYSIS_20261025_CHILISTRIC.md) · [Pre-Registered Hypotheses](HYPOTHESES_20261025_CHILISTRIC.md) · [3-Pass Review](REVIEW_20261025_CHILISTRIC.md)
>
> - **Record-only DrivenData #306 form fields (do NOT upload a `negative` file):** SHA-256 `75fcc743420f817d841b9f822e82bf4e63c850ede29e0e2d75e54b26603acf50` · name `GEMSDOE92-CHILISTRIC-addtail52k-20261025` · note (`107/140`): `h33-h33-2-b2; CHILISTRIC addtail52k: 52000 3DEP-10m+adapt-listric+sinter-valve crests; HOLDOUT-DTI 0.013174` · zeros-outside `float32` in `[0, 1]` prevents `"Predicted values must be in range [0, 1]"`.
> - **`HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` withheld positives):** **Strict Draw-Blind OOF (`d_cat > 2.0`) = `0.013208 [0.011537, 0.014860]` (`#1` all-time zero-catalogue OOF in `GEMSDOE92`, beating `LISTRICLOQO` `0.013064`)**; Static (`d_cat > 2.0`) = **`0.013174 [0.011583, 0.014730]`** (paired `+0.000968 [0.000146, 0.001793]` over `no10m_fixed` `0.012206`); Strict Rule-2 (`d_visible > 2.0`) = `0.112471 [0.100285, 0.124646]`; Off-catalogue **`USGS SGMC PROXY` = `0.113149`** (`+9.4%` vs `LISTRICLOQO` `0.103442`); `44/44` canaries PASS (`<= 0.617275`). Siblings: [`adapt37k`](downloads/h33-h33-2-b2-CHILISTRICadapt37k-20261025-82694176-zeros.tif) (`0.012617`) · [`no10m_fixed`](downloads/h33-h33-2-b2-CHILISTRICno10m_fixed-20261025-48950a5f-zeros.tif) (`0.012206`).

> ## Completed session lane (`2026-10-25`) — `RELAYCONDUIT` / hero arm `relay_conduit` (3 new unique-byte GeoTIFFs)
> **✅ OK TO DOWNLOAD FOR RESEARCH** (`11/11` automated `[0, 1]` gates PASS, `0` NaN; locally unique across all `128` rasters at `0.6601 <= 0.70`) · **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT** (verdict `negative`, `submission_eligible: false`; external 102-repo overlap `0.7843 > 0.70` vs `GEMSDOE53` 80k & literal `17GEMSDOE` dense witness `1.000 > 0.70`; `0` weekly slots spent).
>
> **[⬇ Download research GeoTIFF (`gemsdoe92-relayconduit-relay_conduit-37654-20261025-8e4d1e44-zeros.tif`)](downloads/gemsdoe92-relayconduit-relay_conduit-37654-20261025-8e4d1e44-zeros.tif)** · [one-TIFF ZIP](downloads/gemsdoe92-relayconduit-relay_conduit-37654-20261025-8e4d1e44-zeros.zip) · [audit JSON](downloads/gemsdoe92-relayconduit-relay_conduit-37654-20261025-8e4d1e44-audit.json) · [JSON Run Card](downloads/relayconduit_run_card.json) · [holdout JSON](downloads/relayconduit_holdout.json) · [102-repo uniqueness JSON](downloads/relayconduit_uniqueness.json) · [DrivenData form steps](relayconduit.html) · [PhD Analysis (`0.2778` / `0.3195` / `0.4413`)](ANALYSIS_20261025_RELAYCONDUIT.md) · [Pre-Registered Hypotheses](HYPOTHESES_20261025_RELAYCONDUIT.md)
>
> - **Record-only DrivenData form fields (do NOT upload a `negative` artifact):** separate name `GEMSDOE92-RELAYCONDUIT-relay_conduit-20261025` · note (`113/140`): `RELAYCONDUIT relay_conduit: 37654px tip-relay+OOF blind conduit d>3.2px; HOLDOUT-DTI 0.184485 (st 0.000000) [neg]` · zeros-outside `float32` encoding prevents `"Predicted values must be in range [0, 1]"`.
> - **`HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` withheld positives):** hero `relay_conduit` strict Rule-2 **`0.184485 [0.169875, 0.198933]`** (paired `+0.069008 [0.053289, 0.084771]` over rebuilt `control_COULOMBLOQO_d32` `0.115477`; exceeds `FAULTNET netfar` `0.175147` and `VARIO full` `0.150020`); `relay_delta` `0.180061 [0.165231, 0.193562]`; zero-catalogue `conduit_notip` strict Rule-2 `0.076416 [0.063889, 0.088770]`, static `d_cat > 2.0` `0.005733`, off-catalogue **`USGS SGMC PROXY` = `0.106525`** (beats `COULOMBLOQO` `0.089332`, passes all `1,367` external rasters across 102 repos at `0.6557 <= 0.70`, `0.7031` locally vs `RIEDELVALVE riedel_n90k` 90k).
> - **All 3 arms (`negative`, research only):** [`relay_conduit`](downloads/gemsdoe92-relayconduit-relay_conduit-37654-20261025-8e4d1e44-zeros.tif) ([ZIP](downloads/gemsdoe92-relayconduit-relay_conduit-37654-20261025-8e4d1e44-zeros.zip) · [audit](downloads/gemsdoe92-relayconduit-relay_conduit-37654-20261025-8e4d1e44-audit.json)) · [`relay_delta`](downloads/gemsdoe92-relayconduit-relay_delta-37654-20261025-044a9bb0-zeros.tif) ([ZIP](downloads/gemsdoe92-relayconduit-relay_delta-37654-20261025-044a9bb0-zeros.zip) · [audit](downloads/gemsdoe92-relayconduit-relay_delta-37654-20261025-044a9bb0-audit.json)) · [`conduit_notip`](downloads/gemsdoe92-relayconduit-conduit_notip-37654-20261025-bb0e9f59-zeros.tif) ([ZIP](downloads/gemsdoe92-relayconduit-conduit_notip-37654-20261025-bb0e9f59-zeros.zip) · [audit](downloads/gemsdoe92-relayconduit-conduit_notip-37654-20261025-bb0e9f59-audit.json)).

> ## Parallel lane receipt — lane VARIO / arm `vario_full`
> **✅ OK TO DOWNLOAD (format-valid) · ⛔ DO NOT SUBMIT** (verdict `negative`). Reason: registry duplicate under protocol rule 1: 0.9791 of its dots lie within 3 px of the dots of gemsdoe92-faultnet-netctx-37654-20261025-443d044b-zeros.tif (37,654 dots), above the 0.70 limit; did not beat control_FAULTNET_far on the holdout.
>
> **[⬇ Download research GeoTIFF](downloads/gemsdoe92-vario-full-37654-20261025-3c30a41c-zeros.tif)** · [one-TIFF ZIP](downloads/gemsdoe92-vario-full-37654-20261025-3c30a41c-zeros.zip) · [run card](downloads/vario_run_card.json) · [analysis](ANALYSIS_20261025_VARIO.md)
>
> **How to submit (only with a file marked ✅ OK TO SUBMIT, which this one is not):**
> 1. Download the `.tif` (or the ZIP holding only that TIFF).
> 2. Go to https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/ (log in; not live-verified from the sandbox), then choose the file under *File to submit*.
> 3. Paste this into *Note (optional)*: `VARIO full: 24phys+semivar+MTcp+topo10+ctx LOQO; 37654 dots 2.8px dcat>2`
> 4. Name/record: `GEMSDOE92-VARIO-full-20261025`. After scoring, record the receipt in `ledger/submissions.csv`.
>
> Automated validation: float32, EPSG:32611, 3730×3292, sample transform, values finite in [0, 1], 0 NaN, 0 outside the footprint, 0 on the catalogue. SHA-256 `11f92e382b04a2f368c2259d6b092248efe338dd9a81436de4f27217c3b44573`.
> **HOLDOUT-DTI** (gems57-pooled-hide-v2, 22,663 withheld positives): `0.150020 [0.134975, 0.164286]`. control_FAULTNET_far control: `0.175147 [0.159756, 0.189860]`. Paired Δ `-0.025127 [-0.029306, -0.020842]`. A holdout number is not a leaderboard score, and there is no ORGANIZER-CONFIRMED score.
> **Uniqueness** (99 registry rasters): worst overlap `0.9791` (limit 0.70), worst |ρ| `0.8913` / surface `0.1373` (limit 0.90). Literal-support reading: 4 raster(s) > 0.70. The literal reading is binding under the current protocol and triggers the duplicate stop.
> Siblings: [vario_smooth](downloads/gemsdoe92-vario-smooth-37654-20261025-5c5a1192-zeros.tif) (negative, HOLDOUT-DTI 0.141661) · [vario_nctx](downloads/gemsdoe92-vario-nctx-37654-20261025-d2d499d5-zeros.tif) (negative, HOLDOUT-DTI 0.116258). **Read [SESSION_PROMPT.md](../SESSION_PROMPT.md) first in every session.** Other lanes' status and the repository-wide decision follow below this box; a file is cleared only where it is marked ✅ OK TO SUBMIT.
<!-- CURRENT:END -->






































## Current decision — 2026-10-24 UTC

**Existing research TIFFs: OK TO DOWNLOAD for review; DO NOT SUBMIT. No new unique TIFF was generated in this review.** The site's current primary download is the existing SPRINGALIGN artifact; its public-registry uniqueness check is a binding rejection, and its holdout result does not establish live competition performance. The weekly selector/slot was not used.

The policy stop is decisive: the hash-verified 17GEMSDOE E-proba witness has positive support on every competition-footprint cell. Under the literal rule (>70% forward 3-px overlap or absolute Spearman >0.90), every nonempty in-footprint prediction necessarily overlaps that witness beyond threshold. Do not evade this by moving mass outside the footprint, emitting an empty raster, excluding dense support, or changing the rule. The artifact-generation requirement is explicitly **unfulfilled** until the policy owner resolves the contradiction.

- [Current Pages download/index](index.html) · [current status](REVIEW_CURRENT.md) · [current three-pass review](REVIEW_20261024_SESSION.md) · [ranked-hypothesis/source review](REVIEW_AUTOMATED_20261024.md) · [witness run card](downloads/review_20261024_run_card.json) · [current repo review card](downloads/repo_review_run_card_20261024.json)
- [Fresh exact-file witness receipt](downloads/review_20261024_springalign_witness_v2.json) · [SPRINGALIGN format audit](downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-audit.json)

## Existing site-primary artifact — research only

This file predates the current review and is **not a new submission from this session**. The inherited date in its filename is later than the review date; the filename is not evidence of when it was generated.

- **GeoTIFF:** [Download SPRINGALIGN zeros-outside research raster](downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif) · [single-TIFF ZIP](downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.zip)
- **Research identifier (not a request to upload):** `GEMSDOE92-SPRINGALIGN-f33Ctop-20261025`
- **Research note (≤140 characters):** `h33-h33-2-b2; SPRINGALIGN f33Ctop 12426 far dots on spring-pair alignment lines >3px off H19-5`
- **SHA-256:** `1772ad5c62506b6b380e221d2202b583edf0a5be4f96916af655e0478eba11b1`
- **Automated format receipt:** single-band float32; EPSG:32611; 3730 × 3292; template transform matches; all values finite in [0,1]; no NaN in the footprint; zeros outside; zero known-catalogue mass. This is format-valid/downloadable, **not submission-eligible**.
- **REGISTRY-MEASUREMENT:** exact-file forward overlap 1.0 and |Spearman ρ| 0.0437294869 against the cited 17GEMSDOE witness. The witness is positive on 5,167,373 of 5,167,373 footprint cells; therefore any nonempty valid prediction is rejected by the literal overlap gate. This is one rejection witness, not a fresh complete registry scan. The actual SPRINGALIGN pre-placement surface was not checked in that retrospective test.
- **HOLDOUT-DTI (historical; not rerun this review):** evaluator `gems57-pooled-hide-v2`; 22,663 withheld positives; 0.0048650690; 95% CI [0.0040254482, 0.0057850159]. This local hide-and-recover estimate is not a competition score.

## What the reported GEMSDOE32 result supports

`h33-h33-2-b2` at **0.2778 is a CLAIM**, based on the user-supplied GEMSDOE32 site result; this repository has no corresponding organizer receipt. The parent's measured lineage and geometry are consistent with spatial thinning, a fixed prediction budget, pruning and clearance from known faults retaining useful distance-weighted coverage while reducing redundant or masked mass. This is a plausible mechanism, not proof that any one step caused the reported score: the exact organizer-evaluated bytes and private labels are not available here.

The user supplied **0.3195** and **0.4413** as different leaderboard values. They are conflicting, undated snapshots in this task, not refreshed evidence in this review. A score value does not reveal the winning method. It is possible in principle to outperform the GEMSDOE32 CLAIM, but this review does not demonstrate that outcome. HOLDOUT-DTI, public-site CLAIMs and live organizer scores are different quantities and must not be compared as if they were the same metric.

The four ranked, conditional research hypotheses (including DEM cross-profile step-vs-channel discrimination, offset magnetic-edge continuation, terrain-conditioned gravity residuals, and relief-matched spring-alignment testing) are documented in [the automated review](REVIEW_AUTOMATED_20261024.md). They are research ideas, not established gains or proof of global novelty. No new experiment was run: the literal registry stop blocks placement, and the cached `training_features.tif` stack is absent from this checkout. The official [competition data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) is the required source for the stack; account access was not available to this runtime, and owner-mirror hashes do not establish organizer provenance or redistribution rights.

## Submission procedure — only after a future artifact is genuinely cleared

Do **not** submit any current download. A future file may be considered only if its own evidence shows all of the following: strict format validator passes on reread; leakage canaries are reviewed; spatially blocked HOLDOUT-DTI improves over the comparable holdout best with uncertainty; actual pre-placement-surface and final-dot registry checks pass the applicable policy; its run card says `promote`; and a separate selector confirms the current weekly cap. A format pass alone is never slot clearance.

After a separate selector authorizes an exact artifact:

1. Download only its zeros-outside `.tif` (or ZIP containing exactly that one TIFF); verify the exact SHA-256 in its receipt and do not edit/resave it.
2. On DrivenData's **New submission** form, select that file. The supplied form description says it accepts one single-band GeoTIFF or one GeoTIFF inside a ZIP and requires matching CRS, shape and geotransform. The live form was not accessed in this review.
3. Paste the artifact's short note into **Note (optional)**. Keep the unique submission name in the local ledger; do not assume the described form has a separate name field.
4. Record the actual organizer receipt (submission ID, timestamp and score) in `ledger/submissions.csv`. Only a copied receipt is **ORGANIZER-CONFIRMED**; a model projection or HOLDOUT-DTI is not.

## Automated validation and the portal range error

`python -m gems validate <candidate.tif> --reference data/bridge/sample_submission.tif --catalogue data/bridge/existing_faults.tif --prune-radius 2` is the strict local submission preflight: every cell must be finite and in [0,1], cells outside the valid footprint must be zero, and template CRS/shape/transform must match. It rejects NaN/Inf and out-of-range values anywhere in the file. `python scripts/check_site.py` independently gates every served zeros-outside TIFF, exact-byte audit receipt and current site status. The shared legacy/research `run_gates()` API can still accept NaN outside the footprint for historical comparisons, but it is not the CLI upload preflight. No silent clipping or repair is performed.

A local validator pass reduces the risk of the error `Predicted values must be in range [0, 1]`; it cannot guarantee portal acceptance or competition eligibility.

## Source and access limitations

Manual-review links (not all retrieved during this review): [competition problem / metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [competition rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [official DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), and [GDR INGENIOUS #1391](https://gdr.openei.org/submissions/1391).

DrivenData, USGS and GDR were not accessed during this review under the runtime's restricted outbound-host policy; current leaderboard, submission quota, upload acceptance, official data licensing and organizer receipts therefore remain unverified. No credentials are requested or stored. `docs/REVIEW_AUTOMATED_20261024.md`, `docs/REVIEW_CURRENT.md`, `SESSION_PROMPT.md`, and `IRREGULARITIES.md` preserve the source audit, scientific caveats, next steps and unresolved issues.

## Historical candidate files

Other candidate TIFs listed on the site are prior research artifacts, not new outputs from this review. Each download's audit/run card and current stop status must be checked. In particular, local uniqueness against a sparse dot registry does not override the exact public-witness rejection under the literal rule.
