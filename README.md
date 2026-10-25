# GEMSDOE92 — DOE GEMS Prize #306 Auditable Submission Workbench

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
<!-- CURRENT:BEGIN -->
> ## Newest lane result — lane VARIO / arm `vario_full`
> **✅ OK TO DOWNLOAD (format-valid) · ⛔ DO NOT SUBMIT** (verdict `negative`). Reason: registry duplicate under protocol rule 1: 0.9791 of its dots lie within 3 px of the dots of gemsdoe92-faultnet-netctx-37654-20261025-443d044b-zeros.tif (37,654 dots), above the 0.70 limit; did not beat control_FAULTNET_far on the holdout.
>
> **[⬇ Download the GeoTIFF](docs/downloads/gemsdoe92-vario-full-37654-20261025-3c30a41c-zeros.tif)** · [one-TIFF ZIP](docs/downloads/gemsdoe92-vario-full-37654-20261025-3c30a41c-zeros.zip) · [run card](docs/downloads/vario_run_card.json) · [analysis](docs/ANALYSIS_20261025_VARIO.md)
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
> Siblings: [vario_smooth](docs/downloads/gemsdoe92-vario-smooth-37654-20261025-5c5a1192-zeros.tif) (negative, HOLDOUT-DTI 0.141661) · [vario_nctx](docs/downloads/gemsdoe92-vario-nctx-37654-20261025-d2d499d5-zeros.tif) (negative, HOLDOUT-DTI 0.116258). **Read [SESSION_PROMPT.md](SESSION_PROMPT.md) first in every session.** Other lanes' status and the repository-wide decision follow below this box; a file is cleared only where it is marked ✅ OK TO SUBMIT.
<!-- CURRENT:END -->

> **Read before every session:** this README, [`SESSION_PROMPT.md`](SESSION_PROMPT.md), [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md), the [latest review on this branch](docs/REVIEW_20261025_ARENA_3B4DB247.md), and [ordered next steps](docs/NEXT_STEPS.md). Treat this brief as operating requirements, not as proof of a score or permission to submit.

> ## Fresh repository review — 2026-10-25 UTC (`arena/3b4db247-gemsdoe92`)
> **No new TIFF or geological experiment was generated in this review; 0 weekly slots used.** After merging concurrent `origin/main` (`VARIO`), the current primary (`gemsdoe92-vario-full-37654-20261025-3c30a41c-zeros.tif`, SHA-256 `11f92e382b04a2f368c2259d6b092248efe338dd9a81436de4f27217c3b44573`) remains a format-valid **research download only** (`verdict: negative`, `submission_eligible: false`; local overlap `0.9791 > 0.70` vs FAULTNET and literal full-footprint witness overlap `1.0 > 0.70`), so **DO NOT SUBMIT**. `0.2778` remains a CLAIM without an organizer receipt. [Three-pass review and conditional hypothesis ranking](docs/REVIEW_20261025_ARENA_3B4DB247.md) · [rejection-only run card](evidence/review_20261025_live_stop.json) · [selected primary TIFF](docs/downloads/gemsdoe92-vario-full-37654-20261025-3c30a41c-zeros.tif) · [submission guide](docs/executive-summary.html).
>
> `scripts/check_site.py` now fails if the page's `data-primary` raster, `current_submission.json`, and `readiness.json` drift in path, hash, eligibility, name, or note (catching and repairing `VARIO`'s stale `current_submission.json` during merge). The README below is a historical archive; only the current status panel and its linked byte-bound records govern the current decision.

## ALI session — executive summary (2026-10-25, branch `arena/4eccf0bc-gemsdoe92`)

**Bottom line: a new GeoTIFF was generated, validated and tested. It is OK to download for research and NOT OK to submit.**

| | |
|---|---|
| File | [`gemsdoe92-ali-famnms-37654-20261025T230000Z-68be9b4d-zeros.tif`](docs/downloads/gemsdoe92-ali-famnms-37654-20261025T230000Z-68be9b4d-zeros.tif) · [ZIP](docs/downloads/gemsdoe92-ali-famnms-37654-20261025T230000Z-68be9b4d-zeros.zip) · SHA-256 `25398a5dee456a5fa491cb2b6b4dbd967f60b2e4239e62ac6871297c39ec7b37` |
| Format | PASS: 1 float32 band, EPSG:32611, 3730×3292, matching transform, values exactly {0, 1}, 0 NaN, zeros outside the footprint, 0 dots on catalogued faults |
| Submit? | **NO.** It is a **duplicate** under the registry rule (80.6% of its dots lie within 3 px of 12GEMSDOE `r7-nms3-dem10-scarp`, whose halo covers 31.7% of the domain; 30 discriminating dot fields exceed 0.70). It also **ties** the R0-recipe control on HOLDOUT-DTI: 0.097216 [0.079836, 0.117747] vs 0.097493, paired Δ −0.000278 [−0.015980, +0.015900] (`gems57-pooled-hide-v2`, 22,663 withheld positives). It does not beat the current holdout best (FAULTNET netfar 0.175147). |
| Name / note | `gemsdoe92-ali-famnms-37654-20261025T230000Z-68be9b4d-zeros` / `GEMSDOE92 ALI: OOF physics fault-appearance model, NMS 250 m, 37654 dots >300 m off-catalogue; holdout ties R0 recipe` (117 chars) |

**Why 0.2778 (verified from bytes):**

* `h33-h33-2-b2` = `dotted-h19-5-d2-8` minus every dot within 2 px of a catalogued fault. The 35,483 dots more than 3 px from the catalogue are identical in d2.8 (0.2600), h27-4 (0.2708) and h33-2-b2 (0.2778).
* The gains came from three things:
  1. a strong supervised skeleton (H19-5, 0.1922);
  2. kernel-aware dotting (0.19 → 0.26);
  3. deleting dots that hug catalogued traces. Those dots are masked or unrewarded, but still pay false-positive cost.
* Across 105 owner-reported scores matched to registry rasters, dots within about 2–3 px of the catalogue score about 0.
* The six unique alternatives that kept ≤ 70% overlap all scored 0.18–0.25. None beat 0.2778.

**Full report:** [docs/ALI_LANE.md](docs/ALI_LANE.md) covers the analysis, aggregate-label inversion, ranked hypotheses, holdout table, uniqueness scan, verified sources and limitations. Also see the [run card](docs/downloads/ali_run_card.json) and [next steps](docs/NEXT_STEPS.md).

### How to submit (only when a file is ever cleared)

1. Download the `-zeros.tif` named in the status box. Upload the `.tif` **or** the one-TIFF `.zip`, never both: <https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/>.
2. Paste the **name** and **note** shown for that file. The note must be ≤ 140 characters.
3. Use at most 3 submissions per week (official rules §3.2/§3.4: <https://docs.nlr.gov/docs/fy26osti/96647.pdf>). Choose one final submission before the deadline.
4. **Today no file is cleared.** Every served TIFF is research-only.

### Session prompt (persisted)

Read this README, [SESSION_PROMPT.md](SESSION_PROMPT.md) and [docs/NEXT_STEPS.md](docs/NEXT_STEPS.md) at the start of every session. The 2026-10-25 brief re-states the following. Generate a genuinely new, unique TIFF and make "OK to download / OK to submit" obvious. Explain h33-h33-2-b2 (0.2778 CLAIM) at PhD level. Rank 3–5 untried hypotheses. Validate on the spatially blocked hide-and-recover holdout and never spend a slot on an idea that has not beaten the current holdout best. Obey the single-lane registry stop (|ρ| > 0.90 or > 70% of dots within 3 px of one registry raster's dots, checked on the surface and on the final dots). Label every number (HOLDOUT-DTI with evaluator, withheld positives and 95% CI, or ORGANIZER-CONFIRMED). Run feature-alone leakage canaries (AUC > 0.90 = leakage). Write a run card. Stop at 3 experiments or 2 hours. Verify against official sources, flag irregularities, do three passes, then open and merge a PR. Core values: **Maximize P(Win)** and **Own the Outcome**.

---

> ## This session's repository review (2026-10-25 UTC)
> **No new TIFF or experiment was generated; research downloads only, DO NOT SUBMIT or spend a slot.** No lane was assigned and the literal public-raster stop remains binding. The existing LISTRIC research file passes local format checks but fails recorded public dot overlap (`0.710735 > 0.70`) and is dated 2026-10-26, future relative to this review. [Three-pass audit](docs/REVIEW_20261025_ARENA_REPOSITORY.md) · [run card](evidence/review_20261025_arena_run_card.json) · [existing research TIFF](docs/downloads/h33-h33-2-b2-LISTRICstandalone-20261026-a705162a-zeros.tif).



> ## Latest artifact — LISTRIC (artifact label 2026-10-26; reviewed 2026-10-25, future-date irregularity disclosed)
> ## Latest artifact — NETEXPAND (2026-10-25) — best holdout yet, lane-duplicate: DO NOT SUBMIT
> **✅ OK TO DOWNLOAD (one click below, format-valid)** · **⛔ DO NOT SUBMIT / DO NOT SPEND A WEEKLY SLOT** (`verdict: negative`). Three new byte-unique GeoTIFFs (37,654 dots each, 11/11 format gates, values in [0,1], 0 NaN — portal range error fixed by all-finite zeros encoding). Strict draw-blind **HOLDOUT-DTI `netexpand_far` 0.177976 [0.163109, 0.193227]** (`gems57-pooled-hide-v2`, 22,663 withheld px) beats emission-matched KNICK control by paired **+0.066375 [+0.053280, +0.079413]** (canaries ≤0.7775 PASS) — but final dots overlap FAULTNET `netfar` at **0.7844 > 0.70**, a Protocol Rule-1 lane duplicate, so no slot is cleared. Distinct from R0/H19-5 (overlap ≤0.40); not a copy. "0.2778" remains a **CLAIM** (GEMSDOE32's own page: UNSCORED, no organiser score exists).
>
> **[⬇ Download primary TIF (netexpand_far)](docs/downloads/gemsdoe92-netexpand-netexpandfar-37654-20261025-47bacc15-zeros.tif)** · [one-TIFF ZIP](docs/downloads/gemsdoe92-netexpand-netexpandfar-37654-20261025-47bacc15-zeros.zip) · [conservative d>2 sibling](docs/downloads/gemsdoe92-netexpand-netexpand-37654-20261025-f705be3a-zeros.tif) · [run card (JSON)](docs/downloads/netexpand_run_card.json) · [analysis](docs/ANALYSIS_20261025_NETEXPAND.md) · [hypotheses](docs/HYPOTHESES_20261025_NETEXPAND.md) · [executive summary — how to submit](docs/executive-summary.html)
>
> SHA-256 `a1bc94252d17f7a2…`; name `gemsdoe92-netexpand-netexpand_far-20261025-47bacc15`; note (≤140): `NETEXPAND far: same LOQO pure-crest surface, dots >4px off catalogue; 37654 dots 2.8px`. Verify without any human inspector: `python3 validate_submission.py docs/downloads/gemsdoe92-netexpand-netexpandfar-37654-20261025-47bacc15-zeros.tif` → `FORMAT PASS` (registry stop still applies).

> **✅ OK TO DOWNLOAD FOR RESEARCH** · **⛔ DO NOT SUBMIT / DO NOT SPEND A WEEKLY SLOT** (`verdict: negative`, `submission_eligible: false`). New unique-byte GeoTIFFs (3 experiments); automated [0,1] validation PASS. Static **HOLDOUT-DTI `0.010909 [0.009543, 0.012278]`** (`gems57-pooled-hide-v2`, 22,663 withheld px) nominally tops KNICKLOQO `0.010788` but paired Δ `+0.000121 [-0.001167, +0.001262]` includes 0, SGMC proxy is lower, and the public dual-reading overlap `0.710735 > 0.70` (62GEMSDOE) + literal `1.000` block promotion.
>
> **[Download LISTRIC standalone TIFF](docs/downloads/h33-h33-2-b2-LISTRICstandalone-20261026-a705162a-zeros.tif)** · [one-TIFF ZIP](docs/downloads/h33-h33-2-b2-LISTRICstandalone-20261026-a705162a-zeros.zip) · [run card](docs/downloads/listric_run_card.json) · [analysis](docs/ANALYSIS_20261026_LISTRIC.md) · [hypotheses](docs/HYPOTHESES_20261026_LISTRIC.md) · [three-pass current review](docs/REVIEW_20261025_ARENA_8A5595A3.md) · [executive summary — how to submit](docs/executive-summary.html)
>
> SHA-256 `7e4b46368b2a5949bcf626bfaa4457ed15a89dde38d412a1d07469411a31e2ab`; name `GEMSDOE92-LISTRIC-standalone-20261026`; note (82/140): `h33-h33-2-b2; LISTRIC standalone: 37654 1D quadrant-cal listric offset-pair crests`.

> ## Prior artifact — DRAINAGE-KNICK (2026-10-25)


## Current decision — 2026-10-25 (`f23ca2d2` review; read first)

**OK TO DOWNLOAD FOR RESEARCH. DO NOT SUBMIT. No new unique TIFF was generated.**
The unchanged literal duplicate rule rejects every nonempty candidate against the pinned full-footprint witness. Matched-budget “unique” claims in historical sections below are not binding clearance. We did not copy or rename a previous submission.

[Current automated status](docs/downloads/readiness.json) · [Research workbench / direct TIFF](docs/index.html) · [Executive submission guide](docs/executive-summary.html) · [Three-pass review and conditional hypotheses](docs/REVIEW_F23.md) · [Review run card](docs/downloads/review_f23_run_card.json)

The shared distance validator previously accepted predictions inside a declared prune radius. It now enforces the radius, verifies catalogue alignment, rejects unreadable/mismatched grids cleanly and requires exact transform matching. Status is recomputed from the served bytes, not inferred from a historical PASS label. Run `python scripts/render_readiness.py` after deliberate input changes and `python scripts/check_site.py` to validate all served files and reject stale status.

GitHub Pages is still in **legacy** publishing mode; changing to workflow mode returned HTTP 403. Local/CI verification does not prove the legacy deployment is gated by Actions. No live organizer score, slot cap or portal acceptance was verified.

### Persisted user brief — starting point for every session
### Owner addendum, 2026-10-25 (VARIO session)

The owner directed: review GEMSDOE92 end-to-end; place the required data
yourself; generate a genuinely new unique GeoTIFF (not a copy/rename); make
OK-TO-DOWNLOAD / OK-TO-SUBMIT obvious at the top of the site and executive
summary with one-click download, unique name and <=140-character note; avoid
the portal "Predicted values must be in range [0, 1]" error; answer at PhD
level why GEMSDOE32 h33-h33-2-b2 (claimed 0.2778) scored highest and
whether/how to beat it; pre-register 3–5 untried geological hypotheses and
validate the top one on a spatially blocked holdout before spending any
weekly slot; end with JSON run card, verdict promote/negative, PR merged to
main, remaining limitations. Work products: docs/HYPOTHESES_20261025_VARIO.md,
docs/ANALYSIS_20261025_VARIO.md, docs/vario.html, evidence/vario_run_card.json
(verdict negative; 0 slots used).


Read this README and [SESSION_PROMPT.md](SESSION_PROMPT.md) before work. The [full supplied site-score inventory](ledger/site_scores_claimed_20261025.csv) remains owner-reported claims, not verified receipts. Retain these requirements:

- Generate a genuinely new, distinct competition TIFF, never pass off a copied submission as new. Make download and submission eligibility obvious at the start of the site; finite `[0,1]`, one band, matching template CRS/shape/transform, unique name and a note of at most 140 characters. Automated checks replace visual inspection, not the separate weekly-slot selector.
- Stay in the assigned method lane. Stop if any registry rank correlation exceeds the specified threshold or literal three-pixel dot overlap exceeds the specified threshold; check surface before placement and final dots. Missing lane assignment is not permission to invent a scientific result.
- Reuse the cached stack, shared hide-and-recover evaluator and writer. Hide whole fault segments with buffers, recompute catalogue-derived features from visible faults, and mask visible faults exactly. Use pooled DTI with alpha 0.2, beta 0.8 and the 300 m triangular kernel. Label local HOLDOUT-DTI with version, withheld positives and confidence intervals; only organizer receipts justify ORGANIZER-CONFIRMED.
- Rank three to five geological hypotheses before implementation: layers, physical signature, missing-fault rationale, differences, non-fault mimics, expected value and cost. Verify new free official data are obtainable before claiming viability. Test each feature alone for leakage; do not trust AUC above 0.90 without resolving leakage.
- Complete prior-session next steps first. Stop at three experiments or two hours. Validate on comparable spatial holdouts and beat the current holdout control before promotion; no weekly slot is authorized by format validity alone. Negative results are deliverables.
- Store research with official-source links, provenance and explicit access limitations. Do not invent leaderboard gains or equate fault prediction with proven geothermal vents. Preserve the reported GEMSDOE32 result and conflicting leaderboard figures as unverified unless receipts establish them.
- Maintain a clean GitHub Pages site, executive submission subpage, machine-readable current status, reproducible run card, and no manual pixel-inspection requirement. Run three passes: implement and verify; inspect bugs/assumptions/edge cases; recheck against this brief and fix remaining problems. Create and merge a pull request as requested, and document outstanding work honestly.
- **Maximize P(Win)** means preserving scarce slots and rejecting unsupported score claims. **Own the Outcome** means fixing shared defects and reporting unmet requirements, not weakening a failed gate.

---

## Historical session record (not current clearance)


> ## Latest lane artifact — FLEXMAG (2026-10-25, parallel session)
> **✅ OK TO DOWNLOAD FOR RESEARCH** · **⛔ DO NOT SUBMIT / DO NOT SPEND A WEEKLY SLOT** (`verdict: negative`, `submission_eligible: false`). 3 new byte-unique GeoTIFFs (blind-fault flexure hinge × magnetic ASA; 3/3 pre-registered experiments); automated [0,1] format validation PASS (`nodata=None`, 0 NaN). Primary **HOLDOUT-DTI `0.045554 [0.035846, 0.056751]`** (`gems57-pooled-hide-v2`, 22,663 withheld positives, per-draw re-placement) is below the 0.113316 promotion bar; magnetic-gate paired Δ includes 0. Locally unique (surface |ρ| ≤ 0.0658, final-dot overlap ≤ 0.5567 / 98 rasters); public 102-repo scan not rerun; literal-witness stop above remains binding.
>
> **[Download FLEXMAG primary TIFF](docs/downloads/gemsdoe92-flexmag-20261025T165411Z-flexmag-37654-zeros.tif)** · [one-TIFF ZIP](docs/downloads/gemsdoe92-flexmag-20261025T165411Z-flexmag-37654-zeros.zip) · [run card](docs/downloads/flexmag_run_card.json) · [analysis — why/how 0.2778 + this test](docs/ANALYSIS_20261025_FLEXMAG.md) · [hypotheses](docs/HYPOTHESES_20261025_FLEXMAG.md) · [executive summary — how to submit](docs/executive-summary.html)
>
> SHA-256 `8190e1d07b059f8e6d1c869914a8786dfcbcb2771466f4c3874b60d1668c7261`; name `GEMSDOE92-FLEXMAG-flexmag-20261025`; note (94/140): `FLEXMAG flexmag: 37654 dots; blind-fault flexure hinge x magnetic ASA; HOLDOUT-DTI in run card`. Fresh source check: GEMSDOE32's own page (fetched 2026-10-25) labels `h33-h33-2-b2` **UNSCORED — NO ORGANISER SCORE EXISTS**; `0.2778` remains a CLAIM (see analysis §1).

> ## Latest artifact — DRAINAGE-KNICK (2026-10-25)
> **✅ OK TO DOWNLOAD FOR RESEARCH** · **⛔ DO NOT SUBMIT / DO NOT SPEND A WEEKLY SLOT** (`verdict: negative`). New byte-unique GeoTIFF; all automated format checks pass, but HOLDOUT-DTI `0.061728 [0.047046, 0.075316]` is below the `0.113316` promotion bar and literal public-registry overlap is `1.0 > 0.70`.

> ## Binding decision — read before any download or experiment
> **Research downloads only. DO NOT SUBMIT any current TIFF or spend a weekly slot.** The pinned public registry witness is positive in all 5,167,373 footprint cells, so every nonempty in-footprint prediction raster has literal 3-px forward overlap `1.0 > 0.70`. The pre-placement gate requires stopping. No candidate was generated in this repository review and no artifact is slot-cleared. Read the [current three-pass review](docs/REVIEW_20261025_REPOSITORY_REVIEW.md), [supplemental pre-integration re-audit](docs/REVIEW_20261025_REAUDIT.md), [binding gate evidence](docs/REVIEW_376A8469.md), and [ranked untested hypotheses](docs/HYPOTHESES_20261025_REVIEW.md). The latest lane below is a prior research result, not an exception.
>
> **Persistent operating brief:** read this README and `SESSION_PROMPT.md` at every session start; use shared cached features/evaluator/writer, whole-segment buffered holdouts and leakage canaries; pre-register 3–5 hypotheses; label all metrics and provenance; never call a projection a score; stop at 3 experiments / 2 hours; keep “Maximize P(Win)” and “Own the Outcome” central. Full user prompt summary is retained under [Persistent Session Prompt Reference](#persistent-session-prompt-reference).

## Authoritative review — 2026-10-25 (`797e507a`)

**OK TO DOWNLOAD FOR RESEARCH · DO NOT SUBMIT · no new TIFF generated in this review.**
The requested new unique submission remains **unfulfilled**: a freshly pinned registry witness is positive across the entire footprint, so every nonempty candidate fails the unchanged literal overlap rule. This is an automated rejection, not a request for manual inspection. Matched-budget “unique” claims below are historical diagnostics, not clearance.

**[Download the existing format-validated research TIFF](docs/downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif)** · [Executive guide](docs/executive-summary.html) · [Review, sources and limitations](docs/REVIEW_797E507A.md) · [JSON run card](docs/downloads/review797e_run_card.json) · [Ranked conditional hypotheses](docs/HYPOTHESES_797E507A.md).

No candidate was selected for a slot. Parallel main changed the primary to LISTRICDIP; this review preserved it and rechecked its bytes. SHA-256 `91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e`; REGISTRY-MEASUREMENT overlap `1.0`, Spearman `0.010352227787484035`. No fresh HOLDOUT-DTI or organizer score. Three passes are documented in the review.

### Start every session here

Read this README, including its **Persistent Session Prompt Reference**, then the full [durable operating contract](SESSION_PROMPT.md), [current review](docs/REVIEW_CURRENT.md) and [ordered next steps](docs/NEXT_STEPS.md). The persistent brief is normalized requirements, not a verbatim chat transcript. Preserve the unique-TIF objective, strict automated range/grid validation, named geological hypotheses, visible-only buffered holdout, leakage canaries, literal pre/post-placement uniqueness checks, evidence labels, three-experiment/two-hour budget, run card and separate weekly selector. **Maximize P(Win); Own the Outcome:** a reproducible negative is preferable to a fabricated submission claim.

Publication check: `python scripts/render_public_status.py --check` then `python scripts/check_site.py`. After a lane renderer changes banner order, `python scripts/render_public_status.py` restores the authoritative first-in-body status. Both CI and Pages use the site checker; a missing/stale/buried status blocks publication. Historical lane records follow below and do not override it.

---

<!-- VENTSCARP:BEGIN (rendered from evidence/ventscarp_run_card.json) -->
> ### Parallel lane result — `VENTSCARP` (`2026-10-25`, USGS 3DEP 10 m Scarp + Tufa-Filtered INGENIOUS Hydrothermal Vents)
> **✅ OK TO DOWNLOAD FOR RESEARCH** (`11/11` automated format gates PASS, `float32`, `EPSG:32611`, `3730 × 3292`, finite values strictly in `[0.0, 1.0]`, `0.0` outside footprint, `0` NaNs anywhere — prevents DrivenData's `"Predicted values must be in range [0, 1]"` error) · **⛔ DO NOT SUBMIT FOR A WEEKLY SLOT** (`verdict: "negative"`, `submission_eligible: false` under binding literal `17GEMSDOE` dense-surface overlap `1.000 > 0.70`; `dual_reading_unique = True` at `0.6947 <= 0.70` across `102` public repos & `<= 0.4770` across all merged local rasters) · weekly slots used: **`0`** · experiments: **`3 / 3`**
>
> - **Download (`ventscarp`, `37,654` px):** [`gemsdoe92-ventscarp-ventscarp-37654-20261025-6e97367c-zeros.tif`](docs/downloads/gemsdoe92-ventscarp-ventscarp-37654-20261025-6e97367c-zeros.tif) · [one-TIFF ZIP](docs/downloads/gemsdoe92-ventscarp-ventscarp-37654-20261025-6e97367c-zeros.zip) · [audit JSON](docs/downloads/gemsdoe92-ventscarp-ventscarp-37654-20261025-6e97367c-audit.json) · [JSON Run Card](docs/downloads/ventscarp_run_card.json) · [holdout JSON](docs/downloads/ventscarp_holdout.json) · [102-repo uniqueness JSON](docs/downloads/ventscarp_uniqueness.json) · [PhD Analysis (`GEMSDOE32` `0.2778` `[CLAIM]`, Lipor U-Net critique & path to `0.3195+`)](docs/ANALYSIS_20261025_VENTSCARP.md) · [Pre-Registered Hypotheses](docs/HYPOTHESES_20261025_VENTSCARP.md)
> - **SHA-256 (`-zeros.tif` / `-zeros.zip`):** `a4a342a8ca137e6b141f80ad9346ac483e71e9428a4b4cbddc99d62ea4fd2664` / `e011541c4385f182a17301c6c8e31594d6a09713cb297e0f67dbe07b167124d7`
> - **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, `22,663` withheld positives, 8 LOQO folds):
>   - **Strict Draw-Blind Rule-2 (`d_visible > 2.0`, zero-catalogue LOQO):** `ventscarp` **`0.112213 [0.096670, 0.127254]`** — highest public-registry-unique (`dual_reading_unique = True`) zero-catalogue Rule-2 `HOLDOUT-DTI` in `GEMSDOE92` (beating `KNICKLOQO standalone` `0.109043`, `scarp10m_novent` `0.108862 [0.091993, 0.126805]`, `ventscarp_soft` `0.107019 [0.091774, 0.121673]` by paired `+0.005193 [+0.003555, +0.006627]`, `POISSONKNICK qcal` `0.099241`, `H19-5` `0.071758`, and `R0` `0.004006`; note `FAULTNET` `0.175147` uses catalogue-network context and collides at `0.7586 > 0.70`).
>   - **Static Deployment (`d_cat > 2.0`):** `ventscarp` **`0.008212 [0.007007, 0.009287]`** (`scarp10m_novent` `0.008685`, `ventscarp_soft` `0.007923`, vs `KNICKLOQO standalone` `0.010788`). Off-catalogue `USGS SGMC PROXY`: `0.081321`.
> - **Canaries & Mimic Deconfounding (`26/26 PASS`):** Max single-feature symmetric AUC `0.616694 <= 0.90`; LOQO surface `0.674160 <= 0.90`; excluded `86` Pleistocene Lake Lahontan shoreline `Tufa` mounds (`195` hydrothermal vents kept); places `71.57%` of dots on `< 6°` basin/piedmont scarps (`2.97%` on `>= 12°` cliffs).
> - **Record-Only Name:** `GEMSDOE92-VENTSCARP-ventscarp-20261025` · **Note (`107/140`):** `VENTSCARP ventscarp: 37654px 3DEP-10m scarp + INGENIOUS vents; HOLDOUT-DTI 0.112213 (static 0.008212) [neg]`
> - **Sibling Research TIFFs (`11/11` format gates PASS, DO NOT SUBMIT):** [`gemsdoe92-ventscarp-scarp10m_novent-37654-20261025-3c9a1c6e-zeros.tif`](docs/downloads/gemsdoe92-ventscarp-scarp10m_novent-37654-20261025-3c9a1c6e-zeros.tif) (`b8e88c0083255f87…`) · [`gemsdoe92-ventscarp-ventscarp_soft-47000-20261025-97cebb93-zeros.tif`](docs/downloads/gemsdoe92-ventscarp-ventscarp_soft-47000-20261025-97cebb93-zeros.tif) (`d06c302db19afe2d…`).
<!-- VENTSCARP:END -->

<!-- LISTRICDIP:BEGIN -->
> ### Newest session (2026-10-25) — lane `LISTRICDIP`: 3 new unique GeoTIFFs · verdict **`negative`**
> **✅ OK TO DOWNLOAD FOR RESEARCH** (11/11 format gates, values in `[0, 1]`, 0 NaN, local overlap 0.1968 at scoring; 0.1892 vs the later `DRAINAGE-KNICK` raster) · **⛔ OK TO SUBMIT: NO** (`submission_eligible: false`; literal dense-witness overlap 1.000; not cleared for a weekly slot; 0 slots used)
>
> - **Download:** [`gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif`](docs/downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif) · [zip](docs/downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.zip) · [audit](docs/downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-audit.json) · [run card](docs/downloads/listricdip_run_card.json) · [submit steps](docs/listricdip.html) · [analysis](docs/ANALYSIS_20261025_LISTRICDIP.md) · [pre-registration](docs/HYPOTHESES_20261025_LISTRICDIP.md)
> - **SHA-256:** `91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e` · ZIP `0ac14c467ba046835fcf32c7e3ed43a5eb550f8d2ebcc37cde8d5d7998f2052b`
> - **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives): static `0.005420 [0.004294, 0.006551]`. Beats `R0` `0.004006` (paired +0.001413, CI excludes 0). Loses to `KNICKLOQO` `0.010788` and `COULOMBLOQO` `0.009220` (CIs exclude 0). Re-placed `d_visible > 2`: `0.048225 [0.039232, 0.056882]`. Not an organizer score. Not 0.2778, not 0.3195, not the 2026-10-25 leaderboard snapshot 0.4413.
> - **Name / note (77/140):** `GEMSDOE92-LISTRICDIP-updip50-20261025` / `LISTRICDIP updip50: 37654 listric-offset dots; HOLDOUT-DTI 0.005420; negative`
> - **Siblings (budget not filled, do not pad):** [`anti22` 9,571](docs/downloads/gemsdoe92-listricdip-anti22-9571-20261025T190000Z-zeros.tif) static `0.001291` · [`anti35` 9,555](docs/downloads/gemsdoe92-listricdip-anti35-9555-20261025T190000Z-zeros.tif) static `0.001224`
>
> The standing prompt is in [Persistent Session Prompt Reference](#persistent-session-prompt-reference) below and in `SESSION_PROMPT.md`. Read both at every session start. Maximize P(Win). Own the Outcome.
<!-- LISTRICDIP:END -->

> ## Prior merged lane — DRAINAGE-KNICK (2026-10-25)
> **✅ OK TO DOWNLOAD FOR RESEARCH** · **⛔ DO NOT SUBMIT / DO NOT SPEND A WEEKLY SLOT** (`verdict: negative`). HOLDOUT-DTI `0.061728 [0.047046, 0.075316]` is that lane's strict fold-visible rebuild, not the static instrument used for `LISTRICDIP` `0.005420`. It is below the `0.113316` promotion bar. Literal public-registry overlap is `1.0 > 0.70`.
>
> **[Download the validated TIFF](docs/downloads/gemsdoe92-drainageknick-20261025T120000Z-zeros.tif)** · [one-TIFF ZIP](docs/downloads/gemsdoe92-drainageknick-20261025T120000Z-zeros.zip) · [run card](docs/downloads/gemsdoe92-drainageknick-20261025T120000Z_run_card.json) · [public registry audit](docs/downloads/drainageknick_public_registry.json) · [analysis](docs/ANALYSIS_20261025_DRAINAGE_KNICK.md)
>
> SHA-256 `ef6c27e34fe0f28c6e52615a9fc9601c20ada5337203def25ab8753392aef910`; name `GEMSDOE92-DRAINAGE_KNICK-20261025`; note: `DRAINAGE_KNICK terrain+basement+shear; 37654 dots; HOLDOUT-DTI 0.061728; negative`.

<!-- KNICKLOQO:BEGIN -->
> ### Superseded KNICKLOQO record — research artifact only; **DO NOT SUBMIT**
> KNICKLOQO's earlier matched-budget `dual_reading_decision` was incorrectly presented as uniqueness clearance. It did not apply the binding literal-overlap rule. The full-footprint witness makes the literal overlap `1.000 > 0.70`, so the current verdict is **negative** and `submission_eligible: false`. Its format validation and HOLDOUT-DTI are local research evidence only, not submission clearance or an organizer score.
>
> - [Historical KNICKLOQO GeoTIFF](docs/downloads/h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif) · [superseded run card, corrected metadata and verdict](docs/downloads/knickloqo_submission_run_card.json) · [analysis](docs/ANALYSIS_20261025_KNICKLOQO.md)
> - See [the `0.2778` claim review](docs/BEAT_0_2778.md) for evidence limits. No organizer-confirmed GEMSDOE32 score or score projection is established by this checkout.
<!-- KNICKLOQO:END -->

<!-- PROVINCETOE:BEGIN (rendered by scripts/render_provincetoe_site.py from evidence/provincetoe_run_card.json) -->
> ### Newest Session (2026-10-25) — Lane `PROVINCETOE`: 3 New Unique GeoTIFFs Generated · Verdict **`negative`**
> **✅ OK TO DOWNLOAD FOR RESEARCH** (`11/11` automated format gates PASS in `[0, 1]`, locally unique `<= 0.6846`) · **⛔ DO NOT SUBMIT — verdict negative (submission_eligible: false; Rule-2 HOLDOUT-DTI 0.106452 < COULOMBLOQO 0.113890; 62GEMSDOE 125890-px overlap 0.7918 > 0.70 + literal dense witness 1.0000)** · weekly slots used: **`0`** · experiments: **`3/3`**
>
> - **Primary Research Download (`provincetoe`):** [`gemsdoe92-provincetoe-provincetoe-37654-20261025-8b69d44e-zeros.tif`](docs/downloads/gemsdoe92-provincetoe-provincetoe-37654-20261025-8b69d44e-zeros.tif) · [one-TIFF ZIP](docs/downloads/gemsdoe92-provincetoe-provincetoe-37654-20261025-8b69d44e-zeros.zip) · [audit JSON](docs/downloads/gemsdoe92-provincetoe-provincetoe-37654-20261025-8b69d44e-audit.json) · [JSON run card](docs/downloads/provincetoe_run_card.json) · [holdout JSON](docs/downloads/provincetoe_holdout.json) · [uniqueness JSON](docs/downloads/provincetoe_uniqueness.json) · [PhD Analysis](docs/ANALYSIS_20261025_PROVINCETOE.md) · [Pre-Registered Hypotheses](docs/HYPOTHESES_20261025_PROVINCETOE.md)
> - **SHA-256 (`-zeros.tif` / `-zeros.zip`):** `6d9981f1a45b73be1be51e79220a2dc0cb56baaf2319e3a0829de5bef0bfdac7` / `2f9bc33387a90cfad14229584c0f615b43a79e9b76eff1fefd92ea2ff8e4e831`
> - **Automated Project Validator (zero human inspection):** single-band `float32`, `EPSG:32611`, `3730 × 3292`, exact `sample_submission.tif` transform, finite values strictly in `[0.0, 1.0]`, `0.0` outside footprint (`0` NaN anywhere — prevents DrivenData's `"Predicted values must be in range [0, 1]"` error), `37,654` unit dots, `0` catalogue mass (`gems57.submission_writer` + `gems/gates.py` + `gems57.validate`).
> - **`HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` withheld positives across `seeds 20, 30`):**
>   - **Static deployment (`d_cat > 2.0`) — NEW #1 & #2 ALL-TIME REPOSITORY RECORD:** `piedbasin` **`0.009711 [0.008295, 0.011211]`** (`#1` repo) and `provincetoe` **`0.009685 [0.008306, 0.011150]`** (`#2` repo), surpassing prior `#1` `COULOMBLOQO standalone` `0.009220 [0.007933, 0.010683]`, `HYDROCONDUIT f45hydro` `0.008549`, `COULOMBDM s45coulomb55` `0.007816`, `BLINDFAULT blindtopo` `0.004585`, and parent `R0` `0.004006 [0.003406, 0.004668]` (`+142.4%`). Off-catalogue `USGS SGMC` (`d_cat > 3.0`) `PROXY`: `provincetoe` **`0.091183`** vs `COULOMBLOQO standalone` `0.090569`.
>   - **Strict draw-blind Rule-2 (`d_visible > 2.0`):** `provincetoe` **`0.106452 [0.093042, 0.119461]`** — beats `H19-5` `0.096757 [0.084839, 0.108454]` (paired `Δ = +0.009694 > 0`) and raw-strain control `globalraw` `0.100181 [0.087661, 0.113993]`, while below `COULOMBLOQO standalone` `0.113890 [0.100783, 0.128559]`.
>   - **Cures `#IR-92-NE-QUADRANT-LOQO-COLLAPSE` & Resolves Prior Next Steps #1–#2:** Masked within-quadrant contrasts + label-blind quadrant rank calibration restore `NE` dot share from `6.3%` (`globalraw`) to **`26.3%`** (`provincetoe`, matching `27.6%` footprint) and lift `NE` draw-blind internal `HOLDOUT-DTI` by `+40.9%` (`0.092694 -> 0.130630`). Also proves `COULOMBLOQO standalone` (`0.739842` vs `GEMSDOE23`) fails full `1,403`-raster external `dual_reading_decision` uniqueness due to `45.2%` cliff (`>= 12°`) concentration.
> - **Leakage Canaries & Uniqueness (`REGISTRY-MEASUREMENT`):** `28/28` single-feature canaries PASS (`max symmetric AUC = 0.612372 <= 0.90`). Locally unique across all `92` `GEMSDOE92` rasters (`worst overlap = 0.6846 <= 0.70`, `|ρ| = 0.1857 <= 0.90`) and unique against **all comparable-budget (`<= 50k` px) external rasters** (`max = 0.6604 <= 0.70` for `provincetoe`, `0.6388 <= 0.70` for `piedbasin`), but fails closed (`submission_eligible: false`) on over-budget `55k–126k`-px `dot_field` witnesses (`0.7918` vs `62GEMSDOE` `125,890` px; `#IR-92-OVERBUDGET-SPARSE-WITNESS-ASYMMETRY`) and literal dense witness `17GEMSDOE` (`1.0000`).
> - **Submission Name (local ledger record only):** `GEMSDOE92-PROVINCETOE-provincetoe-20261025` · **Note (`91/140`):** `PROVINCETOE provincetoe: 37654 LOQO Wallace-toe + carbonate-grav dots; HOLDOUT-DTI 0.106452`
> - **Sibling Frozen Arms (`11/11` gates PASS, research only):** [`gemsdoe92-provincetoe-piedbasin-37654-20261025-c22542ae-zeros.tif`](docs/downloads/gemsdoe92-provincetoe-piedbasin-37654-20261025-c22542ae-zeros.tif) (`#1` repo static `HOLDOUT-DTI = 0.009711`, SHA `a8b79fba2c4dd623…`) · [`gemsdoe92-provincetoe-globalraw-37654-20261025-73b06876-zeros.tif`](docs/downloads/gemsdoe92-provincetoe-globalraw-37654-20261025-73b06876-zeros.tif) (raw-strain ablation, SHA `eeb0facc1dfd89de…`).
<!-- PROVINCETOE:END -->

**Read first:** the protocol-gate review below is current; lane banners below it are historical. Older banners further down are historical lane closeouts kept for audit. Two questions are answered for every served file, by the project, with no human inspector: **(1) OK to download?** (format gates) **(2) OK to submit?** (pre-registered holdout gate + dual-reading uniqueness).

> ### Current protocol-gate review — 2026-10-25 (`376a8469`)
> **✅ OK TO DOWNLOAD FOR RESEARCH · ⛔ DO NOT SUBMIT. No new unique TIFF generated.**
> [Existing primary GeoTIFF](docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif) · [three-pass review and ranked conditional hypotheses](docs/REVIEW_376A8469.md) · [fresh run card](docs/downloads/review376a_run_card.json).
> Fresh pinned-witness rejection reproduced. The shared template now enforces **literal** overlap for every raster; matched-budget overlap is diagnostic only. Earlier policy-resolution/uniqueness claims below are historical and superseded. The requested new submission-cleared artifact remains unfulfilled; zero experiments and zero competition slots used in this review.

<!-- POISSONKNICK:BEGIN (rendered by scripts/render_poissonknick_site.py from evidence/poissonknick_run_card.json) -->
> ### Newest Session (2026-10-25) — Lane `POISSONKNICK` (3 new unique GeoTIFFs generated; verdict **`negative`**)
> **✅ OK TO DOWNLOAD FOR RESEARCH** (`11/11` automatic format/range/encoding MUST gates PASS; `float32`, finite `[0, 1]`, `0` NaN/Inf, `0` catalogue mass) · **⛔ DO NOT SUBMIT FOR A WEEKLY SLOT** (`submission_eligible: false`; literal public dense-witness overlap `1.000000 > 0.70` & pooled strict draw-blind `0.098491 < 0.113316` `COULOMBLOQO standalone`) · weekly slots used: **0** · experiments: **3 / 3**
>
> - **Primary Research Download (`qcal`):** [`gemsdoe92-poissonknick-qcal-37654-20261025-9cfcc9b9-zeros.tif`](docs/downloads/gemsdoe92-poissonknick-qcal-37654-20261025-9cfcc9b9-zeros.tif) · [one-TIFF ZIP](docs/downloads/gemsdoe92-poissonknick-qcal-37654-20261025-9cfcc9b9-zeros.zip) · [audit JSON](docs/downloads/gemsdoe92-poissonknick-qcal-37654-20261025-9cfcc9b9-audit.json) · [run card](docs/downloads/poissonknick_run_card.json) · [subpage (`poissonknick.html`)](docs/poissonknick.html) · [PhD analysis](docs/ANALYSIS_20261025_POISSONKNICK.md) · [pre-registered hypotheses](docs/HYPOTHESES_20261025_POISSONKNICK.md)
> - **SHA-256 (`qcal`):** `40c8a83f8b93153f157bae6454dfdf15ce48837478605f5caede6a8c3607104f` · **ZIP SHA-256:** `e5209a8dfe517f2125490441e06968f46ceb21ace406af5ec90ba7aac38dbf2e`
> - **New All-Time Repository Record on Static Deployment `HOLDOUT-DTI`** (`gems57-pooled-hide-v2`, `22,663` withheld positives, `d_cat > 2.0`): **`POISSONKNICK qcal = 0.009304 [0.007836, 0.010810]`**, beating `COULOMBLOQO standalone` (`0.009220 [0.007924, 0.010641]`), `POISSONKNICK uncal` (`0.008877 [0.007596, 0.010238]`), `HYDROCONDUIT f45hydro` (`0.008549`), `APRONRIDGE free1d` (`0.008354`), `COULOMBDM s45coulomb55` (`0.007816`), `POISSONKNICK pkdual40` (`0.007258 [0.006258, 0.008404]`), `BLINDFAULT blindtopo` (`0.004585`), and `R0` (`0.004006 [0.003429, 0.004681]`, paired $\Delta = +0.005298\ [+0.004133, +0.006564]$).
> - **Resolving `#IR-92-NE-QUADRANT-LOQO-COLLAPSE` & Strict Draw-Blind `HOLDOUT-DTI` (`d_visible > 2.0`):** Unlabeled within-quadrant survival-quantile calibration restores `NE` quadrant dots from `2,396` (`6.4%`, `uncal`) / `49` (`0.1%`, `BLINDFAULT`) / `4,221` (`11.2%`, `COULOMBLOQO`) to **`9,967` (`26.5%`, matching `R0`'s `26.9%`)**, lifting `NE` strict draw-blind `HOLDOUT-DTI` by **`+41.3%`** (`0.080880` $\to$ **`0.114274`**) and pooled strict draw-blind `HOLDOUT-DTI` to **`0.098491 [0.086315, 0.112473]`** vs `uncal` `0.090988 [0.079452, 0.103279]` (paired $\Delta = +0.007503\ [+0.000592, +0.015116]$, 95% CI > 0) and `H19_5_vis_d2` `0.071758 [0.062351, 0.081122]` (paired $\Delta = +0.026733\ [+0.017606, +0.036511]$). Off-catalogue `USGS SGMC` (`PROXY` DTI): `pkdual40 = 0.084297`, `qcal = 0.081106` vs `uncal = 0.064487` (`+25.8%`).
> - **Leakage Canaries (`HOLDOUT-CANARY`):** 53 / 53 PASS (`max symmetric AUC = 0.654126 <= 0.90`).
> - **Uniqueness (`REGISTRY-MEASUREMENT`, dual reading `#IR-92-DENSE-WITNESS-MATCHED-BUDGET`):** Local registry (`104` files incl. `COULOMBLOQO` & `EULERFUSE`): worst matched-budget overlap **`0.645668 <= 0.70`** (`local:docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif`), worst $|\rho| = 0.150587 <= 0.90$, `duplicate = False`. Pinned public witnesses (`7` files incl. `GEMSDOE23 100k` & `GEMSDOE52 61k` that tripped `COULOMBLOQO`): worst matched-budget overlap **`0.625432 <= 0.70`**, `duplicate = False`; literal overlap `1.000000` on dense `5,167,373`-px witness `17GEMSDOE_E-proba-multiscale`.
> - **Submission Name:** `GEMSDOE92-POISSONKNICK-qcal-20261025` · **Note (`102/140`):** `POISSONKNICK qcal: 37654 1D Poisson+knick LOQO dots; static DTI 0.009304, drawblind 0.098491; negative`
> - **Sibling arms (`11/11` gates PASS, research only):** [`gemsdoe92-poissonknick-uncal-37654-20261025-da9bfc4a-zeros.tif`](docs/downloads/gemsdoe92-poissonknick-uncal-37654-20261025-da9bfc4a-zeros.tif) (`7ff1b974854f626a…`) · [`gemsdoe92-poissonknick-pkdual40-37654-20261025-6c1bf3ba-zeros.tif`](docs/downloads/gemsdoe92-poissonknick-pkdual40-37654-20261025-6c1bf3ba-zeros.tif) (`4f94d76a17888e28…`).
<!-- POISSONKNICK:END -->
<!-- POISSONFLEX:BEGIN (rendered by scripts/render_poissonflex_site.py from evidence/poissonflex_run_card.json) -->
> ### Newest Session (2026-10-25) — Lane `POISSONFLEX` (`gems/poissonflex.py`; 3 new validated TIFFs; verdict **`negative`**)
> **✅ OK TO DOWNLOAD FOR RESEARCH** (`10/10` `gems.gates` + `13/13` `gems57.validate` PASS; `float32` in `[0, 1]`, `0.0` outside footprint) · **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (`verdict: "negative"`, `submission_eligible: false`; primary HOLDOUT-DTI 0.107466 < holdout-best 0.113890 and 126k-px public witness 0.7541 > 0.70)** · weekly slots used: **0** · experiments: **3/3**
>
> - **Download winning arm (`45,000` dots, nested OOF support):** [`gemsdoe92-poissonflex-poissonflex_opt-45000-20261025-54255bcc-zeros.tif`](docs/downloads/gemsdoe92-poissonflex-poissonflex_opt-45000-20261025-54255bcc-zeros.tif) · [one-TIFF ZIP](docs/downloads/gemsdoe92-poissonflex-poissonflex_opt-45000-20261025-54255bcc-zeros.zip) · [audit JSON](docs/downloads/gemsdoe92-poissonflex-poissonflex_opt-45000-20261025-54255bcc-audit.json) · [JSON Run Card](docs/downloads/poissonflex_run_card.json) · [PhD Analysis](docs/ANALYSIS_20261025_POISSONFLEX.md) · [Pre-Registered Hypotheses](docs/HYPOTHESES_20261025_POISSONFLEX.md)
> - **SHA-256 (`-zeros.tif`):** `37b18c200e84c77b39b07e527b17d4395968389aaf3ff0c175c71204b2065f9b` · ZIP `193ddff4e46015a1086ab4b293d44c271c24686c214988305e421df551fd4035`
> - **Automated Validator (zero human step):** single-band `float32`, `EPSG:32611`, `3730 × 3292` (`100 m`), all values finite in `[0.0, 1.0]` (prevents DrivenData `"Predicted values must be in range [0, 1]"` error), `0.0` outside footprint, `45,000` unit dots (`>= 2.8 px` spacing), `0` catalogue mass (`d_cat > 2.0 px`).
> - **HOLDOUT-DTI (`gems57-pooled-hide-v2`, `22,663` withheld positives, `8` buffered quadrant folds, seeds `20+30`):**
>   - **Primary strict draw-blind (`d_visible > 2.0`):** `poissonflex_opt` **`0.107466 [0.094158, 0.120431]`** (beats `PROVINCETOE` `0.106452`, `H19-5` `0.096757 [0.084298, 0.108421]` by paired `+0.010709 [+0.002297, +0.018444]`, `COULOMBDM` `0.094496`, and `BLINDFAULT` `0.047896`; trails holdout-best `COULOMBLOQO_standalone_dvis2` `0.113890 [0.100124, 0.127440]` by `-0.006424 [-0.013250, +0.000170]`); `poissonflex_eq` `0.103768 [0.090267, 0.117066]`; `poissonflex_raw` `0.102861 [0.089368, 0.116130]`.
>   - **Static deployment (`d_cat > 2.0`):** `poissonflex_opt` **`0.008824 [0.007601, 0.010081]`** (`2.20x` parent `R0` `0.004006 [0.003408, 0.004651]`, vs `COULOMBLOQO standalone` `0.009220 [0.007983, 0.010493]` and `PROVINCETOE piedbasin` `0.009711`).
>   - **Off-catalogue `USGS SGMC` bedrock fault `PROXY` (`62,122` px `> 3 px` from `existing_faults`):** `poissonflex_opt` **`0.120957`** (**`+35.4%`** over `COULOMBLOQO standalone` `0.089332`, **`+32.7%`** over `PROVINCETOE` `0.091183`, and **`+26.8%`** over parent `R0` `0.095386`).
>   - **NE Quadrant LOQO Collapse Cured (`#IR-92-NE-QUADRANT-LOQO-COLLAPSE`):** `NE` dot allocation restored from `0.1%` (`BLINDFAULT`) / `11.2%` (`COULOMBLOQO`) to **`22.7%`** (`NW 21.9% / NE 22.7% / SW 33.8% / SE 21.6%`), beating `COULOMBLOQO` in `NW` (`0.117551` vs `0.111948`).
> - **Leakage Canaries (`32/32 PASS`):** max symmetric AUC **`0.616108 <= 0.90`** (`None`); new `f03_poisson_demag_conduit` = `0.548458` (`3.66x` excess AUC over raw `RTP` tilt `0.513278`).
> - **Uniqueness (`REGISTRY-MEASUREMENT`):** **PASS** vs all `101` local `GEMSDOE92` rasters (`max 3-px overlap = 0.6488 <= 0.70`, `max |ρ| = 0.1674 <= 0.90`; vs `R0`: `0.5031`, vs `COULOMBLOQO standalone`: `0.5997`), **PASS** vs all `<= 80,000`-dot public rasters across `102` repos (`max = 0.6804 <= 0.70`), and **PASS** continuous surface `|ρ|` across all `1404` public blobs (`max |ρ| = 0.4668 <= 0.90`); **STOP** on `100k–126k`-dot public rasters (`0.7541 > 0.70` on `62GEMSDOE/docs/downloads/gems62f-h2r-ventcons-125890-20261012T012736Z-zeros.tif`) and literal dense witness (`1.0000 > 0.70` on `17GEMSDOE`).
> - **Previous-Session Next Steps Closed:** `evidence/coulomb_loqo_dual_reading_selector.json` (`COULOMBLOQO standalone` worst matched-budget overlap `0.739842 > 0.70`, `dual45` `0.722420 > 0.70` -> both `negative`) & `evidence/ne_quadrant_loqo_collapse_diagnostic.json`.
> - **Record-Only Name:** `GEMSDOE92-POISSONFLEX-opt-20261025` · **Note (`86/140`):** `POISSONFLEX opt: 45000 LOQO dots, Poisson-grav/mag+flexure+knick; HOLDOUT-DTI 0.107466`
> - **Sibling Research TIFFs (`37,654` dots, `10/10` format gates PASS, DO NOT SUBMIT):** [`gemsdoe92-poissonflex-poissonflex_eq-37654-20261025-5512bd34-zeros.tif`](docs/downloads/gemsdoe92-poissonflex-poissonflex_eq-37654-20261025-5512bd34-zeros.tif) (`1bea0ae105865371…`) · [`gemsdoe92-poissonflex-poissonflex_raw-37654-20261025-be99276b-zeros.tif`](docs/downloads/gemsdoe92-poissonflex-poissonflex_raw-37654-20261025-be99276b-zeros.tif) (`3048f32162e4b572…`).
<!-- POISSONFLEX:END -->

<!-- BLINDFAULT:BEGIN (rendered by scripts/render_blindfault_site.py from evidence/blindfault_run_card.json) -->
> ### Session 2026-10-25 — lane `BLINDFAULT` (historical research TIFF; verdict **`negative`**)
> **✅ OK TO DOWNLOAD** (format-valid; duplicate under the literal registry rule) · **⛔ DO NOT SUBMIT — literal registry duplicate stop; matched-budget overlap is diagnostic only** · weekly slots used: **0** · experiments: **3/3**
>
> - **Download:** [`gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-zeros.tif`](docs/downloads/gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-zeros.tif) · [one-TIFF ZIP](docs/downloads/gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-zeros.zip) · [audit JSON](docs/downloads/gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-audit.json) · [run card](docs/downloads/blindfault_run_card.json) · [analysis](docs/ANALYSIS_20261025_BLINDFAULT.md) · [pre-registered hypotheses](docs/HYPOTHESES_20261025_BLINDFAULT.md)
> - **SHA-256:** `c91170e5d4ffc67a18378aa9f479b8786ff6e92970e12e6646de14dbc6c5cf3d` · ZIP `5a01bcb7d7066982349d9f9357a4e7172c20e588364ac82b306aac4258a32181`
> - **Validator (automated, no human step):** single band `float32`, `EPSG:32611`, `3730 × 3292`, finite values in `[0, 1]`, `0.0` outside footprint, 37,654 unit dots, 0 catalogue mass — written and re-read through `gems57.submission_writer` / `gems57.validate`.
> - **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives, strict draw-blind LOQO, `d_visible > 2.0`): `blindtopo` **0.047896 [0.038079, 0.057970]**; `blind` (hypothesis arm) 0.037842 [0.029376, 0.047036]; `blindflat` 0.047475 [0.035767, 0.059748]; `H19-5` reference 0.096757 [0.084640, 0.108096]; repository holdout-best `COULOMBLOQO standalone` 0.113316. Low-conspicuity tercile (mechanism instrument, 6,065 positives): `blind` 0.011041 [0.004739, 0.018804] vs `H19-5` 0.007166 [0.004529, 0.010079].
> - **Leakage canaries:** max symmetric AUC 0.5728 (all ≤ 0.90).
> - **Uniqueness (REGISTRY-MEASUREMENT, literal rule binding; matched-budget diagnostic only):** local registry (91 rasters): matched-budget worst overlap 0.4014 (`local:docs/downloads/h33-h33-2-b2-COULOMBLOQOdual45-20261024-dd91d98c-zeros.tif`), literal worst 0.4014, worst |ρ| 0.0923; public registry (1386 Git-blob-verified rasters, 102 repos, complete=True): matched-budget worst overlap 0.5219 (`12GEMSDOE/docs/downloads/12GEMSDOE_r6-nms3-h28-texture_8721329b55c7.tif`), literal worst 1.0000, worst |ρ| 0.3402. Overlap with parent `R0`: 0.2613. Specificity proof: the owner-reported parent `R0` itself has literal overlap 1.000 / matched-budget 0.037 against the dense witness.
> - **Submission name:** `GEMSDOE92-BLINDFAULT-blindtopo-20261025` · **Note (86/140):** `BLINDFAULT blindtopo: 37654 LOQO dots, slope-blind cov-shift wts; HOLDOUT-DTI 0.047896`
> - Sibling arms (also format-valid, research only): `gemsdoe92-blindfault-blind-37654-20261025-d4f09813-zeros.tif` (`b2cd485934adfa9a…`), `gemsdoe92-blindfault-blindflat-37654-20261025-1e27ea5c-zeros.tif` (`3ccf1d798a7a3e18…`).
<!-- BLINDFAULT:END -->

### 🆕 Session 2026-10-25 — lane `RADIOCONTACT` (Rank-1 untried hypothesis): new unique TIFF generated · verdict `negative`

**✅ OK TO DOWNLOAD** (format-valid, 11/11 gates PASS, finite [0, 1], zeros outside footprint) · **⛔ DO NOT SUBMIT — verdict `negative`** (automated gate: primary HOLDOUT-DTI `0.005066 [0.003638, 0.006583]` &lt; holdout-best `0.009220` static / `0.113316` Rule-2; paired CI includes 0) · weekly slots used: **0** · experiments: **1/3**

- **Download:** [`gemsdoe92-radiocontact-20261025T041646Z-zeros.tif`](docs/downloads/gemsdoe92-radiocontact-20261025T041646Z-zeros.tif) · [`gemsdoe92-radiocontact-20261025T041646Z-zeros.zip`](docs/downloads/gemsdoe92-radiocontact-20261025T041646Z-zeros.zip) · [audit JSON](docs/downloads/gemsdoe92-radiocontact-20261025T041646Z-audit.json) · [run card](docs/downloads/gemsdoe92-radiocontact-20261025T041646Z_run_card.json) · [pre-registered hypotheses](docs/HYPOTHESES_20261026_RADIOCONTACT.md)
- **SHA-256:** `026a52ff46d695bb79ae39780c154cba9cc69e039e7d2a4d1fe898c6c0a79345` (ZIP `474ca791630f9acd8e22b0f28278d52451e0fbb2a5bb6a4f939f78e3c03c7c46`)
- **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives): static `0.005066 [0.003638, 0.006583]` vs R0 `0.004006` (paired delta +0.001060, CI [-0.000341, 0.002615] — includes 0); Rule-2 fold-visible `d_visible > 2.0` diagnostic `0.005066` vs R0 `0.004006`. Leakage canaries max symmetric AUC `0.5317` (all ≤ 0.90). Uniqueness vs 93 local rasters: worst matched-budget overlap `0.2418`, worst |ρ| `0.0476` → unique.
- **Submission name:** `GEMSDOE92-RADIOCONTACT-20261025` · **Note (140/140):** `h33-h33-2-b2; RADIOCONTACT: U/K+Th/K alteration x gravity-gradient + MT; 37654 dots d_cat>2px; HOLDOUT-DTI 0.005066 [neg]`

<!-- GRAVQUAD:BEGIN -->
### 🆕 Session 2026-10-25 — lane `GRAVQUAD` (Rank-3 pre-registered hypothesis, `docs/HYPOTHESES_20261026_RADIOCONTACT.md`): new unique TIFF generated · verdict `negative`

**✅ OK TO DOWNLOAD** (format-valid, 9/9 gates PASS on an independent disk re-read, finite `[0, 1]`, zeros outside footprint) · **⛔ DO NOT SUBMIT — verdict `negative`** (static HOLDOUT-DTI `0.005092 [0.004001, 0.006253]` &lt; holdout-best `0.010788` static / `0.113316` Rule-2; paired delta vs `R0` `+0.001086 [-0.000082, +0.002312]` — CI includes 0, not significant) · weekly slots used: **0** · experiments: **2/3** this session arc (`RADIOCONTACT` + `GRAVQUAD`; public-registry scan skipped for `GRAVQUAD` per budget, local 107-raster uniqueness check alone clears it)

- **Mechanism:** gravity analytic-signal amplitude (Band 11 vertical gradient, Band 18 signed E–W horizontal derivative, and a computed N–S derivative of Band 13) × structure-tensor linear-edge coherence — a strike-blind buried-contact detector never previously built as its own lane in this repository.
- **Download:** [`gemsdoe92-gravquad-20261025T145744Z-zeros.tif`](docs/downloads/gemsdoe92-gravquad-20261025T145744Z-zeros.tif) · [`gemsdoe92-gravquad-20261025T145744Z-zeros.zip`](docs/downloads/gemsdoe92-gravquad-20261025T145744Z-zeros.zip) · [audit JSON](docs/downloads/gemsdoe92-gravquad-20261025T145744Z-audit.json) · [run card](docs/downloads/gemsdoe92-gravquad-20261025T145744Z_run_card.json) · [ranked next-session hypotheses](docs/HYPOTHESES_20261025_NEXT.md)
- **SHA-256:** `9ea3e2e01fba5e733964e1252c729a70f0d61edc499c848628d83946d49c7ab5` (ZIP via run card)
- **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives): static `0.005092 [0.004001, 0.006253]`; strict Rule-2 also `0.005092`. Leakage canaries max symmetric AUC `0.5362` (all ≤ 0.90). Uniqueness vs 107 local rasters: worst matched-budget overlap `0.3044` (vs `RADIOCONTACT` sibling), worst |ρ| `0.0523` → unique (local scope only).
- **Submission name:** `GEMSDOE92-GRAVQUAD-20261025` · **Note (133/140):** `h33-h33-2-b2; GRAVQUAD: gravity analytic-signal amplitude x linear-edge coherence; 37654 dots d_cat>2px; see run card for HOLDOUT-DTI`
- **Finding:** three independent zero-label standalone physical transforms this repo has now tested (RADIOCONTACT `0.005066`, DRAINAGE-KNICK, GRAVQUAD `0.005092`) land within a narrow band well below the supervised quadrant-debiased LOQO lanes (`COULOMBLOQO` `0.009220`, `KNICKLOQO` `0.010788`). The highest-ranked untried idea for a future session is folding these transforms into the existing LOQO ensemble as additional features rather than building another standalone deterministic surface — see `docs/HYPOTHESES_20261025_NEXT.md`.
<!-- GRAVQUAD:END -->

**Current review:** [Three-pass closeout and limitations](docs/REVIEW_20261025_BLINDFAULT_CLOSEOUT.md) · [current review index](docs/REVIEW_CURRENT.md). The newest lane added to this repository is **GRAV-QUAD** (immediately above; static HOLDOUT-DTI `0.005092 [0.004001, 0.006253]`, negative); RADIOCONTACT (above) and BLINDFAULT are prior research lanes from the same session arc, also negative. Other parallel sessions subsequently added `LISTRICDIP`, `KNICKLOQO`, `PROVINCETOE`, and `POISSONKNICK`/`POISSONFLEX` (further down this file); none of those lane names overlap with `GRAVQUAD`'s gravity-analytic-signal mechanism, so this remains a non-duplicate contribution. See each lane's run card before using any numbers. The RADIOCONTACT pre-registration filename is dated 2026-10-26 despite the run card's 2026-10-25 date; this chronology irregularity is unresolved and must not be presented as verified pre-registration timing. Read [`SESSION_PROMPT.md`](SESSION_PROMPT.md) and this README at each session start.

**This session — lane `DILATATION` (Band 8 geodetic dilatation rate, Rank-1 pre-registered untried hypothesis):** new unique-byte research GeoTIFF `h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432-zeros.tif` published with ZIP, per-file audit JSON and Protocol Rule 5 run card. ✅ **OK TO DOWNLOAD FOR RESEARCH** — 10/10 automated format gates PASS (`EPSG:32611`, `3730 × 3292`, `float32`, finite `[0, 1]`, `0.0` outside footprint, `37,654` unit dots, `0` catalogue mass) — prevents DrivenData's `"Predicted values must be in range [0, 1]"` portal error. ⛔ **DO NOT SUBMIT — verdict `negative`, `submission_eligible: false`**: static `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, 22,663 withheld positives) `0.005818 [0.004838, 0.006912]` vs parent R0 `0.004006 [0.003424, 0.004690]` — paired `Δ +0.001812 [+0.001106, +0.002535] > 0` beats parent R0 but stays below holdout-best `COULOMBLOQO standalone` (`0.113316` Rule-2 / `0.009220` static); literal registry overlap stop fires (worst 3-px forward overlap `1.0000` vs DILATATION p10 sibling; pinned public dense witness `1.0000 > 0.70`). Leakage canaries max symmetric AUC `0.514862 <= 0.90`. Weekly slots used: `0`; experiments: `1/3`.

- **Download:** [`docs/downloads/h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432-zeros.tif`](docs/downloads/h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432-zeros.tif) · [`...-zeros.zip`](docs/downloads/h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432-zeros.zip) · [audit JSON](docs/downloads/h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432-audit.json) · [run card](docs/downloads/dilatation_run_card.json) · [variant build receipt](evidence/dilatation_variants.json) · [proxy audit](evidence/dilatation_proxy_audit.json)
- **SHA-256 (`-zeros.tif`):** `cc79c48ae0f46b0c22cd410305a773e72b719833718bceed2c5bcda3c8c38052` · ZIP `eb4a76d9c766429b7942283d7501ffec7bef321a8eeac57dc6694ad89b11ae13`
- **Name:** `GEMSDOE92-DILATATION-p15-20261025` · **Note (`139 / 140`):** `h33-h33-2-b2; DILATATION p15: 5648 dots shifted low-to-high geodetic dilatation tercile on H19-5, d_cat>2px; HOLDOUT-DTI 0.005818; negative`

**Latest session review:** [Three-pass findings and ranked conditional hypotheses](docs/REVIEW_918B947A.md) · [fresh run card](docs/downloads/review_918b947a_run_card.json). Subsequent `COULOMBDM` (and parallel `XPHASE`) work generated unique research TIFFs that are **OK TO DOWNLOAD** and **DO NOT SUBMIT**. The literal overlap rule remains unsatisfiable for weekly-slot clearance because a pinned registry raster covers the entire footprint. The operational user brief is retained below and in `SESSION_PROMPT.md`; read both at session start. Maximize P(Win) and Own the Outcome mean preserving negative evidence, not fabricating submission clearance.

> ### Parallel lane closeout — `EULERFUSE gravity`: ✅ OK TO DOWNLOAD FOR RESEARCH; ⛔ DO NOT SUBMIT
> [Exact GeoTIFF](docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif) · [one-TIFF ZIP](docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.zip) · [audit](docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros-audit.json) · [run card](docs/downloads/eulerfuse_run_card.json) · [public scan](docs/downloads/eulerfuse_public_registry.json) · [analysis](docs/ANALYSIS_20261024_EULERFUSE.md). Exact TIF SHA-256: `5820e882512843a334f4497ed7f294af937339f729e4eeeecdc33d9cdafeeab9`; no exact SHA match in the pre-publication scan of `1,378` exact-grid rasters; `11/11` format gates PASS with all values finite in `[0,1]`. Strict draw-blind **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, `22,663` withheld positives) is `0.110387 [0.097279, 0.123179]`, below fresh control `0.113316 [0.101071, 0.126266]`; paired delta `-0.002929 [-0.006700, 0.000763]`. Literal public overlap is `1.000 > 0.70`. Name: `GEMSDOE92-EULERFUSE-gravity-20261024`; 80/140-character record-only note: `EULERFUSE gravity: 37654 LOQO Euler-contact dots; HOLDOUT-DTI 0.110387; negative`. Verdict `negative`; `submission_eligible: false`; 3/3 experiments and 0 weekly slots.

> ### ✅ DOWNLOAD STATUS: **FORMAT-VALID — OK TO DOWNLOAD FOR RESEARCH**
> ### ⛔ SUBMISSION / WEEKLY SLOT STATUS: **DO NOT SUBMIT — NOT CLEARED (`verdict: "negative"`, `submission_eligible: false`; literal public dense-witness stop)**
>
> Read this README, [`SESSION_PROMPT.md`](SESSION_PROMPT.md), and [`docs/REVIEW_CURRENT.md`](docs/REVIEW_CURRENT.md) at every session start.
>
> - **Current research download:** [`docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif`](docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif) · [One-TIFF ZIP](docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.zip) · [Audit JSON](docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-audit.json) (`11 / 11` format MUST gates PASS; `float32`, `EPSG:32611`, `3730 × 3292`, finite `[0, 1]`, `0.0` outside footprint, `0` NaNs anywhere, `37,654` unit-mass dots, `0` catalogue mass).
> - **SHA-256 (`-zeros.tif`):** `44efd202e8b96b9812de4693bd7f1ed05afed28de7e2e9413f72bc139ff18b12` (ZIP: `2d1c23a2ce4b2396c30eebdea86981785b3a24356a77dcd0195ebae0b5a8e754`)
> - **Suggested Submission Name (research record only — DO NOT UPLOAD YET):** `GEMSDOE92-COULOMBDM-s45coulomb55-20261024`
> - **Suggested Submission Note (`112 / 140` chars):** `h33-h33-2-b2; COULOMBDM s45coulomb55: 16944 Coulomb-H19 + 20710 off-skel 1D Coulomb/RTP/clay ridges (>3px H19-5)`
> - **Measured `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` withheld positives):** Static `d_cat > 2.0` **`0.007816 [0.006994, 0.008644]`** (`+95.1%` vs `R0` `0.004006`; `+29.3%` vs `RELIEF p10` `0.006045`); zero-label standalone sibling [`coulomb1d`](docs/downloads/h33-h33-2-b2-COULOMBDMcoulomb1d-20261024-826b2fb3-zeros.tif) (`0% H19-5`, `0%` catalogue supervision) achieves Rule-2 fold-visible `d_vis > 2.0` **`0.094496 [0.085916, 0.102867]`** (matching supervised `H19-5` `0.096757` within 95% CI). Static holdout is below supervised LOQO repository holdout-best `COULOMB-LOQO standalone` `0.009220`. Local `HOLDOUT-DTI` is **not** an `ORGANIZER-CONFIRMED` competition score.
> - **Uniqueness & Stop Gate:** Locally unique against all 58 repository rasters (`worst 3-px overlap = 0.679583 <= 0.70`, `|ρ| = 0.4130 <= 0.90`; vs `COULOMBLOQO` `<= 0.5448`, vs `XPHASE` `<= 0.2979`) and **`0 / 1,181` sparse (`<= 150k` px) public rasters exceed `70%`** across 102 `GEMSDOE` repos ([102-repo scan](docs/downloads/coulombdm_public_registry_uniqueness.json)). Blocked by the literal public dense witness `17GEMSDOE E-proba-multiscale` (`5,167,373` positive footprint cells → `1.000` forward overlap; [witness](docs/downloads/public_witness_s45coulomb55.json) · [Run Card](docs/downloads/coulombdm_run_card.json)). **0 weekly slots spent (`74 BUILT / 0 RECEIPT`).**
> - **Lane:** `COULOMBDM` = zero-label 2D Mohr–Coulomb dilatant shear (`Bands 4, 7, 8`) × 2D FFT upward-continued `Band 2 RTP` (`100/300/600 m`) + `Band 17` MT clay-cap edges + lateral `GeoDAWN K/Th, U/Th` contact gradients + `>= 80 °C` blind `GDR #1391` geothermometers along Canny cross-strike 1D NMS centrelines. Siblings: [coulomb1d](docs/downloads/h33-h33-2-b2-COULOMBDMcoulomb1d-20261024-826b2fb3-zeros.tif) (`0.094496` Rule-2 / `0.006467` static), [s35coulomb65](docs/downloads/h33-h33-2-b2-COULOMBDMs35coulomb65-20261024-1091c5a7-zeros.tif) (`0.007304` static).
> - **Workbench & Analysis:** [Main Workbench](docs/index.html) · [Executive Summary](docs/executive-summary.html) · [Submission Guide](docs/SUBMIT.html) · [Pre-Registered Hypotheses](docs/HYPOTHESES_20261024_COULOMBDM.md) · [PhD Analysis](docs/ANALYSIS_20261024_COULOMBDM.md)
> - **Parallel three-pass repository review (2026-10-24):** [Findings, ranked future hypotheses, verified checks and limitations](docs/REVIEW_20261024_ARENA.md) · [JSON run card](evidence/arena_review_run_card_20261024.json). The literal public-registry duplicate stop remains binding for weekly slots.

## Prior/parallel candidate summary & full technical reference

Among earlier historical baselines, repository holdout-best remains `COULOMBLOQO standalone` (`h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif`, `0.009220 [0.007983, 0.010493]`). `APRONRIDGE free1d` (`h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif`) recorded `0.008354 [0.006823, 0.010135]` while the higher documented HYDROCONDUIT hybrid is `HYDROCONDUIT f45hydro` (`h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif`) at `0.008549 [0.007626, 0.009487]`; merged parallel lanes recorded `COULOMBDM s45coulomb55` (`0.007816 [0.006994, 0.008644]` static; zero-label `coulomb1d` `0.094496` Rule-2 `d_vis > 2.0`), `GEOTENSION free1d` (`0.007615 [0.005832, 0.009386]`), `PIEDFRONT f35Ptop` (`GEMSDOE92-PIEDFRONT-f35Ptop-20261024`, `h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif`, SHA-256 `e314f4c004927ff56334827b4d45c57fc62da3da3010c12682d7cce6d0f185a8`, `0.006425`), `COULOMB seismo` (`0.005808 [0.004846, 0.006809]`), `XPHASE dual40` (`h33-h33-2-b2-XPHASEdual40-20261024-643553cf-zeros.tif`, `0.004653 [0.003955, 0.005390]`), `EULERFUSE gravity` (strict draw-blind `0.110387 [0.097279, 0.123179]`, below its fresh `0.113316` control), `BASEMENTEDGE step3` (`0.000000`), and `MICROSWARM short` (`0.000000`) — all `verdict: "negative"`, `submission_eligible: false`.

---

## PhD Answer: Why `GEMSDOE32` (`h33-h33-2-b2`, `0.2778` `[CLAIM]`) Beat Every Listed `GEMSDOE` Site & How to Beat It

Full mathematical derivation: [`docs/ANALYSIS_20261024_COULOMBLOQO.md`](docs/ANALYSIS_20261024_COULOMBLOQO.md).

1. **Exact DTI Metric Geometry (`#IR-92-ALPHA-BETA-PROSE-SWAP` Corrected):**
   - The [official reference notebook](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb) (Cell 16) confirms the **training-loss** weights only. It does not implement distance-weighted evaluation. The following DTI equation is implemented by the shared local [`vendor/gems57/metric.py`](vendor/gems57/metric.py), not independently certified from the live organizer problem page in this review:
     $$\mathrm{DTI}(A, G) = \frac{\mathrm{TP}_w}{\mathrm{TP}_w + 0.2\,\mathrm{FP}_w + 0.8\,\mathrm{FN}_w}, \qquad K(r) = \max\!\left(0,\, 1 - \frac{r}{300\,\mathrm{m}}\right), \qquad \Omega_{\text{eval}} = \Omega \setminus C.$$
   - Contrary to inverted prose in earlier session docs, **false negatives carry $4\times$ the denominator weight of false positives ($\beta = 0.8$ vs $\alpha = 0.2$)**. The triangular-kernel coverage uses a **pointwise maximum**, so overlapping predictions can be redundant. However, separation below `2.8 px` does **not** imply zero marginal truth credit or a full per-dot false-positive penalty; each depends on the actual truth geometry. Thinning is a plausible mechanism for the reported improvement, not a universally optimal spacing theorem.
2. **Exact Zero-XOR Byte-Verified Ancestor Cascade of `GEMSDOE32` (`R0`):**
   - `H19-5` (`19GEMSDOE`, `121,131` px, `0.1922` `[CLAIM]`) $\to$ `D2.8` (`GEMSDOE25`, `44,090` px Poisson-thinned at `2.83 px ≈ 300 m`, `0.2600` `[CLAIM]`) $\to$ `SOLO` (`GEMSDOE28`, `40,199` px with **`XOR(SOLO, D2.8 & d_cat > 1.0) == 0`**, `-3,891` px at `d_cat == 1.0`, `0.2708` `[CLAIM]`; `#IR-92-SOLO-R1-BYTE-IDENTITY`) $\to$ **`R0` / `GEMSDOE32 h33-2-b2`** (`37,654` px with **`XOR(R0, D2.8 & d_cat > 2.0) == 0`**, `-2,545` px at `1.0 < d_cat <= 2.0`, retaining `2,171` splay/tip dots at `2.0 < d_cat <= 3.0`, `0.2778` `[CLAIM]`).
3. **Why `R0` Has Headroom (`0.3195` / `0.4413` Leaderboard `[CLAIM]`) & How `COULOMB-LOQO` Breaks Through:**
   - `R0` is 100% confined to `H19-5` and thinned in physics-blind row-major scan order (`0.004006` static `HOLDOUT-DTI`). Earlier `GEMSDOE92` un-normalized terrain lanes (`BREAKLINE` `0.004861`, `STEPEDGE` `0.003980`) were hijacked `74.8%` by bare mountain-core cliffs, while rigid piedmont elevation boxcars (`APRONRIDGE` `0.008354`, `HYDROCONDUIT` `0.008549`) starved active bedrock horst faults (causing `HYDROCONDUIT` to lose to `H19-5` on unmasked `d_visible > 2.0` holdout, `0.0852` vs `0.0968`, and lose `22.9%` on `SGMC`).
   - **`COULOMB-LOQO`** trains regularized 4-quadrant Leave-One-Quadrant-Out (`>= 1.2 km` guard band, `> 500 m` negative buffer) boosted trees on **24 strictly catalogue-free physical features** (`gems/coulomb_loqo.py`): multi-scale Hessian scarp ridges, 600 m step monotonicity, signed `Band 18` E–W gravity-gradient footwall polarity concordance ($r = +0.6260$ with $\partial_x\text{Band 13}$), true `Band 2 RTP` tilt/demag/Hessian (replacing mislabeled `Band 6 tc` = Radiometric Total Count), circular cross-physics axial strike phase-locking, N15°E/conjugate 2D Coulomb dilation & slip tendency, MT clay-cap margins, `GeoDAWN K/Th, U/Th`, and `419` blind `>= 80 °C` silica/cation geothermometer cells (`dist_known_fault_px` explicitly dropped).

---

## Multi-Instrument Benchmark Table (All Evidence Labels Explicit; Zero Projections as Scores)

| Candidate / Baseline | Dots (`H19` %) | Static `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` pos, 95% CI) | Rule-2 `d_vis > 2.0` `HOLDOUT-DTI` | `SGMC` `PROXY` (`62,703` px) | Local Overlap (`<=0.70`) | Sparse Public `<=90k` (`1,121` rasters) | Literal Public (`1,368` rasters) |
|---|---:|---|---|---|---|---|---|
| **`KNICKLOQO standalone` (`2026-10-25` Exp 1 — All-Time #1 Static)** | `37,654` (`0%`) | **`0.010788 [0.009468, 0.012201]`** | **`0.109043 [0.097872, 0.120534]`** | **`0.103912`** | **`0.6855` (PASS)** | **`0.6855` (`0 / 1,412 > 70%` dual)** | `1.0000` (dense STOP) |
| **`KNICKLOQO uncal` (`2026-10-25` Exp 2 — Uncalibrated Ablation)** | `37,654` (`0%`) | **`0.010102 [0.008907, 0.011335]`** | **`0.107033 [0.095749, 0.118431]`** | `0.095441` | **`0.6818` (PASS)** | **`0.6818` (`0 / 1,412 > 70%` dual)** | `1.0000` (dense STOP) |
| **`KNICKLOQO dual35` (`2026-10-25` Exp 3 — Hybrid)** | `37,654` (`35%`) | **`0.008976 [0.007871, 0.010008]`** | **`0.097288 [0.086879, 0.107472]`** | **`0.102945`** | **`0.6712` (PASS)** | **`0.6712` (`0 / 1,412 > 70%` dual)** | `1.0000` (dense STOP) |
| **`COULOMBLOQO standalone` (Exp 1 — Primary)** | `37,654` (`0%`) | **`0.009220 [0.007983, 0.010493]`** | **`0.113316 [0.100614, 0.127163]`** | **`0.090569`** | **`0.6164` (PASS)** | `0.7004` (`1 > 70%`) | `1.0000` (dense STOP) |
| **`COULOMBLOQO nocoulomb` (Exp 2 — Ablation)** | `37,654` (`0%`) | **`0.009151 [0.007944, 0.010389]`** | — | `0.091251` | **`0.6640` (PASS)** | `0.7396` (`5 > 70%`) | `1.0000` (dense STOP) |
| **`COULOMBLOQO dual45` (Exp 3 — Hybrid)** | `37,654` (`45%`) | **`0.009107 [0.007977, 0.010325]`** | **`0.101998 [0.090846, 0.112907]`** | **`0.094057`** | **`0.5982` (PASS)** | **`0.6488` (`0 > 70%`)** | `1.0000` (dense STOP) |
| `HYDROCONDUIT f45hydro` | `37,654` (`55%`) | `0.008549 [0.007461, 0.009684]` | `0.085221` | `0.074107` | `0.5500` (PASS) | `0.6518` (`0 > 70%`) | `1.0000` (dense STOP) |
| `APRONRIDGE free1d` | `37,654` (`0%`) | `0.008354 [0.006823, 0.010135]` | `0.086787` | `0.080098` | `0.6507` (PASS) | — | `1.0000` (dense STOP) |
| **`COULOMBDM s45coulomb55` (Current Research Download)** | `37,654` (`45%`) | **`0.007816 [0.006994, 0.008644]`** | **`0.086867`** | **`0.075208`** | **`0.6796` (PASS)** | **`0.6796` (`0 / 1,181 <=150k > 70%`)** | `1.0000` (dense STOP) |
| **`COULOMBDM coulomb1d` (Zero-Label Blind-Fault)** | `37,654` (`0%`) | `0.006467 [0.005660, 0.007214]` | **`0.094496 [0.085916, 0.102867]`** | `0.070345` | **`0.5859` (PASS)** | **`0.5859` (`0 / 1,181 <=150k > 70%`)** | `1.0000` (dense STOP) |
| `GEMSDOE92-PIEDFRONT-f35Ptop-20261024` (`h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif`, SHA-256 `e314f4c004927ff56334827b4d45c57fc62da3da3010c12682d7cce6d0f185a8`) | `37,654` (`65%`) | `0.006425 [0.005375, 0.007479]` | — | `0.059993` | `0.6500` (PASS) | — | `1.0000` (dense STOP) |
| `RELIEF p10piedmont` (`R0`-duplicate ref) | `37,654` (`100%`) | `0.006045 [0.005179, 0.006882]` | — | `0.087245` | `0.9938` (DUP) | — | `1.0000` (DUP) |
| `STRAINBREAK f60s2i` | `37,654` (`40%`) | `0.005487 [0.004550, 0.006386]` | — | `0.105162` | `0.4150` (PASS) | `0.6844` (`0 > 70%`) | `1.0000` (dense STOP) |
| `ANASIG f45Atop` / `SPRINGALIGN f33Ctop` / `BREAKLINE f45Ltop` | `37,654` | `0.004967` / `0.004865` / `0.004861` | — | `0.0806` / `0.0802` / `0.1261` | `0.55–0.67` | — | `1.0000` (dense STOP) |
| `STEPEDGE f60Sraw` | `37,654` (`40%`) | `0.003980 [0.003295, 0.004702]` | — | `0.141464` | `0.4610` (PASS) | — | `1.0000` (dense STOP) |
| `R0` (`h33-h33-2-b2`, `0.2778` `CLAIM`) | `37,654` (`100%`) | `0.004006 [0.003408, 0.004651]` | `0.096757` (`H19`) | `0.096060` | self | — | — |

---

## Audited 19-Band `training_features.tif` Stack (`EPSG:32611`, `3730 × 3292`, `5,167,373` Footprint Cells, `60,988` `existing_faults` Pixels)

| Band | GDAL Description & Verified Physical Identity | Sign | Valid Footprint Px | `q05` | Median (`q50`) | `q95` | Role in `COULOMB-LOQO` |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | `mag_anom` — Magnetic anomaly | Signed | `5,164,312` | `-204.37` | `-57.69` | `162.74` | Superseded by inclination-corrected Band 2 `rtp` |
| **2** | **`rtp` — Reduced-to-Pole magnetic anomaly** | **Signed** | `5,164,312` | `-332.48` | `-137.22` | `153.75` | **Group C: RTP tilt edge, positive-Laplacian demag trough, Hessian ridge, axial strike** |
| 3 | `tmi_hg` — TMI horizontal gradient | Non-neg | `5,164,312` | `1.64` | `13.16` | `93.85` | Archived in `ANASIG` |
| **4** | **`geod_2ndinv` — Geodetic strain-rate 2nd invariant** | **Non-neg** | `5,164,312` | `2.50` | `19.91` | `46.20` | **Group D: Strain magnitude (`f19`)** |
| **5** | **`iso_grav_anom_slope` — Isostatic gravity slope** | **Non-neg** | `5,164,312` | `0.029` | `0.102` | `0.270` | **Group B: AGC-equalized gravity tilt (`f12`)** |
| 6 | `tc` — **Verified Radiometric Total Count** (`r = 0.99714` w/ `GeoDAWN` Band 4; mislabeled as magnetic tilt in header, `#IR-92-BAND6-TC-MISLABEL`) | Non-neg | `5,164,300` | `11.81` | `18.48` | `25.58` | Replaced by clean `GeoDAWN` `K, Th, U` ratios (`f22, f23`) |
| **7** | **`geod_shearrate` — Geodetic shear strain rate** | **Non-neg** | `5,164,312` | `0.00` | `9.70` | `29.14` | **Group D: 2D Coulomb slip tendency (`f18`)** |
| **8** | **`geod_dilaterate` — Geodetic volumetric dilatation rate** | **Signed** | `5,164,312` | `-2.85` | `5.50` | `19.20` | **Group D: N15°E Coulomb dilation tendency (`f17`, AUC `0.5574`)** |
| 9 | `tmi_vg` — TMI vertical gradient | Signed | `5,164,312` | `-0.285` | `-0.009` | `0.319` | Archived in `ANASIG` |
| 10 | `deq_n100a15` — Distance to earthquake | Non-neg | `5,164,312` | `180.80` | `622.80` | `8631.38` | Screened negative (`100 km` smoothing) |
| **11** | **`iso_grav_anom_vg` — Isostatic gravity vertical gradient** | **Signed** | `5,164,312` | `-2.70` | `-0.072` | `2.61` | **Group B: Gravity tilt denominator (`f12`)** |
| **12** | **`det_elev` — Detrended elevation (`3DEP`)** | **Signed** | `5,164,312` | `-330.67` | `-75.58` | `450.24` | **Groups A–C: Step monotonicity, coherence, footwall polarity** |
| **13** | **`iso_grav_anom` — Isostatic gravity anomaly** | **Signed** | `5,164,312` | `-26.09` | `-7.26` | `7.74` | **Groups B–C: Footwall dip concordance (`f09`) & axial strike** |
| 14 | `tmi` — Total magnetic intensity | Signed | `5,164,312` | `-298.64` | `-124.82` | `140.08` | Superseded by Band 2 `rtp` |
| **15** | **`depth_to_base_surf` — Depth to basement / cover thickness (m)** | **Signed** | `5,164,312` | `6.21` | `316.37` | `1881.26` | **Groups A–B: Cover thickness, basement gradient & concordance** |
| 16 | `ieq_n100a15` — Earthquake intensity/density | Non-neg | `5,164,312` | `312.50` | `755.70` | `2723.60` | Screened negative (`100 km` smoothing) |
| **17** | **`cond_surf` — Subsurface MT electrical conductivity** | **Non-neg** | `5,164,312` | `1.84` | `2.89` | `3.91` | **Group E: Smectite clay-cap margin gradient (`f20`) & level (`f21`)** |
| **18** | **`iso_grav_anom_hg` — Signed E–W horizontal gravity derivative** ($r = +0.6260$ w/ $\partial_x\text{B13}$) | **Signed** | `5,164,312` | `-3.40` | `0.038` | `3.30` | **Group B: E–W normal-fault footwall polarity lock (`f11`, AUC `0.5596`)** |
| **19** | **`det_elev_slope` — Detrended elevation slope (`3DEP`)** | **Non-neg** | `5,164,312` | `0.168` | `3.749` | `25.337` | **Group A: Relative log-slope break (`f01`, AUC `0.6039`) & Hessian ridges** |

---

## Reproducible Pipeline (Zero Manual Steps)

`BLINDFAULT` (2026-10-25; 2 CPUs / 3 GB is enough):

```bash
python3 -m venv .venv && .venv/bin/pip install numpy scipy rasterio pandas pytest "scikit-learn>=1.5,<2.0"
.venv/bin/python scripts/restore_inputs.py && .venv/bin/python scripts/verify_manifest.py   # SHA-256-pinned inputs → .cache/gems_inputs/
PYTHONPATH=vendor .venv/bin/python scripts/run_blindfault.py        # features, canaries, 3 LOQO arms, HOLDOUT-DTI, dots → evidence/blindfault_holdout.json
PYTHONPATH=vendor .venv/bin/python scripts/finalize_blindfault.py   # submission_writer TIFFs, local + cached public dual-reading uniqueness, run card
.venv/bin/python scripts/render_blindfault_site.py                  # README/site status blocks rendered from the run card
PYTHON=.venv/bin/python make test && PYTHON=.venv/bin/python make site && PYTHON=.venv/bin/python make verify && PYTHON=.venv/bin/python make ledger
```


Newest `POISSONFLEX` pipeline (`< 1.2 GiB` streaming RSS per stage):

```bash
# 1. Restore & SHA-256-verify all 12 competition/external inputs
.venv/bin/python scripts/restore_inputs.py && .venv/bin/python scripts/verify_manifest.py

# 2. Stream 30-feature POISSONFLEX stack & verify 32/32 single-feature leakage canaries (<= 0.90)
.venv/bin/python scripts/run_poissonflex.py --stage features_canaries

# 3. Run paired COULOMBLOQO control, strict 8-fold draw-blind LOQO holdout, and full deployment fit
.venv/bin/python scripts/run_poissonflex.py --stage cl_worker
.venv/bin/python scripts/run_poissonflex.py --stage holdout_only
.venv/bin/python scripts/run_poissonflex.py --stage deploy_only

# 4. Package via submission_writer, dual-validate [0, 1] GeoTIFFs, scan 97 local + 1,414 public blobs, emit Run Card & render site
.venv/bin/python scripts/finalize_poissonflex.py
.venv/bin/python scripts/render_poissonflex_site.py
```

`EULERFUSE` closeout (use a clean/scratch checkout because the builder refuses to overwrite pinned bytes):

```bash
.venv/bin/python scripts/restore_inputs.py && .venv/bin/python scripts/verify_manifest.py
PYTHONPATH=vendor .venv/bin/python scripts/screen_eulerfuse.py
PYTHONPATH=vendor .venv/bin/python scripts/evaluate_eulerfuse.py
PYTHONPATH=vendor .venv/bin/python scripts/build_eulerfuse_submission.py
PYTHONPATH=vendor .venv/bin/python scripts/audit_public_registry.py \
  --candidate docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif \
  --surface .cache/eulerfuse_surfaces/EULERFUSE-gravity-surface-20261024.tif \
  --output evidence/eulerfuse_public_registry.json
PYTHONPATH=vendor .venv/bin/python scripts/finalize_eulerfuse.py
```

The finalizer validates source-receipt agreement and writes the negative run card without human input. The stored registry scan predates publication of these bytes; a later self-match must not be misrepresented as evidence that the file copied a prior submission.

Current/prior holdout-best pipeline:

```bash
# 1. Restore & SHA-256-verify all 12 competition/external inputs into gitignored .cache/gems_inputs/
.venv/bin/python scripts/restore_inputs.py && .venv/bin/python scripts/verify_manifest.py

# 2. Screen all 43 single-feature/LOQO leakage canaries (<=0.90) & pre-placement local uniqueness
.venv/bin/python scripts/screen_coulomb_loqo.py

# 3. Build & 10/10 gate-check the 3 pre-registered COULOMB-LOQO variants via submission_writer.py
.venv/bin/python scripts/build_coulomb_loqo_variants.py

# 4. Run multi-instrument HOLDOUT-DTI (static + strict Rule-2 d_vis>2.0), SGMC PROXY, & local registry audit
.venv/bin/python scripts/report_coulomb_loqo_proxies.py

# 5. Run live 102-repo Git-blob-verified public registry scan & assemble Protocol Rule 5 Run Card
.venv/bin/python scripts/audit_public_registry.py \
  --candidate docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif \
  --surface .cache/gems_inputs/coulomb_loqo_S_full_surface.tif \
  --out-name coulomb_loqo_public_registry_uniqueness
.venv/bin/python scripts/finalize_coulomb_loqo_run_card.py

# 6. Run full automated unit tests, submission validator, site contract, manifest & ledger gates
PYTHON=.venv/bin/python make test && PYTHON=.venv/bin/python make site && PYTHON=.venv/bin/python make verify && PYTHON=.venv/bin/python make ledger
```

---

## Arena Core Values

- **Maximize P(Win):** Every hypothesis is pre-registered from Basin-and-Range structural & geothermal physics (`docs/HYPOTHESES_20261024_COULOMBLOQO.md`), tested against single-feature leakage canaries (`<= 0.90`), validated on whole-segment spatial holdouts (`gems57-pooled-hide-v2` static AND strict draw-blind `d_visible > 2.0`) plus independent `USGS SGMC` bedrock controls, and scanned across 1,368 public rasters so scarce weekly competition slots (`<= 3 / week`) are never wasted on duplicates or unvalidated heuristics.
- **Own the Outcome:** We own verification end to end — catching and fixing inverted $\alpha/\beta$ Tversky formulas (`#IR-92-ALPHA-BETA-PROSE-SWAP`), `SOLO` byte-identity errors (`#IR-92-SOLO-R1-BYTE-IDENTITY`), spatial-block bootstrap `extend` bugs (`#IR-92-HYDROCONDUIT-EXTEND-TERMS`), `Band 6 tc` header mislabeling (`#IR-92-BAND6-TC-MISLABEL`), and HTML merge seams (`#IR-92-PR49-MERGE-SEAMS`), while validating every served `[0, 1]` GeoTIFF automatically without human inspection.

---

## Trusted Official Sources

- [DrivenData Competition #306 Problem & Metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [About](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/) · [Data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official Competition Rules PDF (NREL/TP-5700-96647)](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DrivenData Official Reference Solution (`drivendataorg/gems-prize-reference-solution`)](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN Airborne Magnetic & Radiometric Surveys](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [USGS Data Catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [DOE Geothermal Data Repository (GDR) INGENIOUS #1391](https://gdr.openei.org/submissions/1391) · [GBCGE INGENIOUS](https://gbcge.org/current-projects/ingenious/)
- [USGS 3D Elevation Program (3DEP)](https://www.usgs.gov/3d-elevation-program) · [USGS State Geologic Map Compilation (SGMC)](https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d)
- [EPSG:32611 WGS 84 / UTM Zone 11N](https://epsg.io/32611) · [Tversky Index (Wikipedia)](https://en.wikipedia.org/wiki/Tversky_index)

---

## Persistent Session Prompt Reference

Full durable operating contract also stored in [`SESSION_PROMPT.md`](SESSION_PROMPT.md). This expandable prompt block is a **normalized, condensed operating brief**, not a verbatim archive of the full historical user message. Read it with the linked contract at every session start. Neither document turns GEMSDOE32's `0.2778` into a verified organizer score or clears a TIFF for submission; follow the binding negative decision at the top of this README and the evidence-linked reviews instead.

<details>
<summary>Click to expand the persisted operating brief (normalized, not verbatim)</summary>

```markdown
Review the repo. Work on the previous sessions' next steps first.

THE FOLLOWING IS THE HIGHEST URGENCY AND MUST BE FOLLOWED!

MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION. DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION. BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION. IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED TIF SUBMISSION.

There should be an easy to download submission tif file as described by the prompt. Read the entire prompt. A lot of sites mention inspection only and a human inspector, but the inspection needs to be done through the project and needs to be validated for submission without human intervention.

PARALLEL-RUN PROTOCOL — read first. This session is one of several running from this same prompt.

1. LANE. Stay inside one method lane. If your raster's rank-correlation with any registry raster exceeds [0.90], or more than [70%] of your dots fall within 3 px of one registry raster's dots, you have drifted into another lane: log it as a duplicate and stop. Check this on the surface before placement AND on the final dots.
2. REUSE, DON'T REBUILD. Use the template's cached feature stack, evaluate_holdout.py and submission_writer.py. Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive every catalogue-based feature only from the visible faults, mask visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared tool is wrong, fix it once in the template and report it; never keep a private fork.
3. LABEL EVERY NUMBER as HOLDOUT-DTI (evaluator version, number of withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). A projection is never written as a score.
4. LEAKAGE CANARY. Test each feature alone on the holdout before trusting any result. AUC above [0.90] means leakage until proven otherwise.
5. RUN CARD. End with one JSON card: hypothesis; mechanism; the named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output (no NaN inside the footprint, values in [0,1], CRS/shape/transform match); submission name + note of at most 140 characters; verdict promote / negative. Negative results are deliverables.
6. BUDGET. Stop after [3] experiments or [2] hours. Do not pick submissions: promotion to a real slot is a separate selector step, within the weekly cap shown on the submission page.

Study GEMSDOE32 (h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778): why and how did this get the highest score among the listed GEMSDOE sites, and are we able to generate a submission that scores higher than 0.2778? Before implementing anything, generate and rank 3-5 candidate geological hypotheses yet to be tried, verify data availability, validate format in [0, 1] without human inspection, provide unique submission name and note + executive summary subpage, store prompt in README.md, uphold Arena Core Values (Maximize P(Win), Own the Outcome), run 3 passes, and create and merge PR into main.
```

</details>


## Session 2026-10-25 — leaderboard research: decision and links

**OK TO DOWNLOAD FOR RESEARCH. DO NOT SUBMIT.** No new submission-eligible TIFF was generated. The binding literal dense-witness stop was re-confirmed from a sha-pinned GitHub blob (exit 1, [receipt](evidence/readiness_20261025_leaderboard.json)). A policy decision is needed before any candidate can be cleared: [analysis §5](docs/ANALYSIS_20261025_LEADERBOARD.md).

- **Why `0.2778` (GEMSDOE32) is a CLAIM, not a receipt, and what the forensic evidence supports:** [analysis §1–3](docs/ANALYSIS_20261025_LEADERBOARD.md).
- **Live leaderboard (fetched 2026-10-25):** #1 `0.4413` (xiaofanhu, not a GEMSDOE entry); `0.3195` is not on the top-50 snapshot. [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).
- **Official rules read this session:** three submissions per week, one final selection, generative-AI disclosure, and human judging by DOE. [NLR Official Rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf).
- **Metric verified:** the shared evaluator matches an independent naive implementation of the official equations to `2.2e-16`. Regression test: `tests/test_metric_independent.py`.
- **Ranked pre-registered hypotheses (none built or scored):** [docs/HYPOTHESES_20261025_LEADERBOARD.md](docs/HYPOTHESES_20261025_LEADERBOARD.md). Top candidate: phase congruency on the RTP band (H1), not yet built because the stop precedes placement.
- **Run card (values computed from files):** [evidence/leaderboard_session_20261025_run_card.json](evidence/leaderboard_session_20261025_run_card.json). The LISTRICDIP research file `gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif` passes every automated format gate (not the current primary; see the status block above).
- **Irregularities for review:** [IRREGULARITIES.md](IRREGULARITIES.md) (2026-10-25 section, IR-25-A to IR-25-I).
- **Budget used:** 0 of 3 experiments, 0 weekly slots.

## Additional parallel research records (not rerun in review797e)

Main `d6f7ac0` added [RADIODECOUPLE](docs/ANALYSIS_20261025_RADIODECOUPLE.md) and [CURIE-DEMAG](docs/ANALYSIS_20261026_CURIEDEMAG.md) research artifacts. Their original run cards and code are preserved. These do not override the literal stop or constitute experiments run in this review. CURIE-DEMAG names are future-dated relative to this review; use receipt hashes and actual verification timestamps.

---

## Session Prompt — Authoritative Operating Contract (read at every session start)

The full durable operating contract below is the starting point for all work on this repository. It is a condensed operating brief, not a verbatim archive of the historical input, and it is not a claim that any GEMSDOE entry received a verified organizer score or that any current TIFF is submission-cleared. Follow the binding negative decision at the top of this README and the evidence-linked reviews instead.

### Highest urgency — MUST

**MUST generate a unique TIF submission for the competition. Do not copy a previous submission unless it's for learning and education. But we must generate a unique TIF submission. It must be obvious whether it is OK to download and submit the generated TIF submission.**

There should be an easy-to-download submission TIF file as described by the prompt. A lot of sites mention inspection only and a human inspector, but the inspection needs to be done through the project and needs to be validated for submission without human intervention.

### Parallel-run protocol

1. **LANE.** Your lane is the single method paragraph below. Stay inside it. If your raster's rank-correlation with any registry raster exceeds 0.90, or more than 70% of your dots fall within 3 px of one registry raster's dots, you have drifted into another lane: log it as a duplicate and stop. Check this on the surface before placement AND on the final dots.

2. **REUSE, DON'T REBUILD.** Use the template's cached feature stack, evaluate_holdout.py and submission_writer.py. Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive every catalogue-based feature only from the visible faults, mask visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared tool is wrong, fix it once in the template and report it; never keep a private fork.

3. **LABEL EVERY NUMBER** as HOLDOUT-DTI (evaluator version, number of withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). A projection is never written as a score.

4. **LEAKAGE CANARY.** Test each feature alone on the holdout before trusting any result. AUC above 0.90 means leakage until proven otherwise.

5. **RUN CARD.** End with one JSON card: hypothesis; mechanism; the named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output (no NaN inside the footprint, values in [0,1], CRS/shape/transform match); submission name + note of at most 140 characters; verdict promote / negative. Negative results are deliverables.

6. **BUDGET.** Stop after 3 experiments or 2 hours. Do not pick submissions: promotion to a real slot is a separate selector step, within the weekly cap shown on the submission page.

### Competition context

- **Competition:** DOE GEMS Prize, DrivenData #306 — <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- **About:** <https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/>
- **Data:** <https://www.drivendata.org/competitions/306/competition-doe-gems/data/> (requires DrivenData login)
- **Leaderboard:** <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/> — current high score 0.4413 (not a GEMSDOE entry); 0.3195 not on the top-50 snapshot
- **Official rules PDF:** <https://docs.nlr.gov/docs/fy26osti/96647.pdf> (three submissions per week, one final selection, generative-AI disclosure, human judging by DOE)
- **Reference solution:** <https://github.com/drivendataorg/gems-prize-reference-solution>
- **USGS GeoDAWN:** <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and>
- **DOE GDR #1391 INGENIOUS:** <https://gdr.openei.org/submissions/1391>
- **GBCGE INGENIOUS:** <https://gbcge.org/current-projects/ingenious/>
- **EPSG:32611:** <https://epsg.io/32611>
- **Tversky index:** <https://en.wikipedia.org/wiki/Tversky_index>

### Submission format (validated in-project, no human inspection)

- Single-band GeoTIFF (.tif) or a .zip containing a single GeoTIFF
- Must match the submission format's CRS (EPSG:32611), shape (3730 × 3292), and geotransform ((100, 0, 243350, 0, -100, 4508550))
- Values must be finite and in [0, 1] (prevents the portal error "Predicted values must be in range [0, 1]")
- Zero outside the footprint; 0 NaN inside the footprint
- Unique submission name and a short note (≤ 140 characters)

### Core values

- **Maximize P(Win):** In every decision, weigh tradeoffs, assess risk, and choose the path that maximizes the probability of winning. Preserve scarce slots; reject unsupported score claims.
- **Own the Outcome:** Own results end to end. Fix shared defects and report unmet requirements; do not weaken a failed gate. A reproducible negative is preferable to a fabricated submission claim.

### Deliverables for this session

1. Generate 3–5 candidate geological hypotheses not yet tried (layers, physical signature, missing-fault rationale, differences, mimic, expected value, cost) — see docs/HYPOTHESES_TILTANGLE.md
2. Validate the top candidate (H1 TILTANGLE: gravity tilt-angle edge corridors) on the spatially-blocked holdout set — HOLDOUT-DTI 0.033466 [gems57-pooled-hide-v2, 45,253 withheld positives]
3. Generate a unique TIF submission — gemsdoe92-tiltangle-tiltangle-37654-20261025T182301Z-zeros.tif (format-valid, SHA-256 f17eae78ff659e3551fb4a4f92ef9e16180fde22a9d157a2114b03ef98a023e7)
4. Create executive summary subpage — docs/tiltangle.html
5. Store the prompt in README.md (this section)
6. Create and merge a pull request onto main
