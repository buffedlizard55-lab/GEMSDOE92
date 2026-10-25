# Repository audit, 0.2778 analysis, and untried hypotheses — 2026-10-25

**Decision (unchanged, re-verified): OK TO DOWNLOAD FOR RESEARCH · DO NOT SUBMIT · no new raster generated · 0 of 3 experiments used · 0 weekly slots used.**

This session did not produce a new competition TIFF. The reason is a verified blocker, not a missing step: under the literal duplicate rule in the session protocol, every in-footprint raster overlaps a public full-footprint witness at 1.0, so no candidate can clear the gate. Section 1 gives the evidence. The decision on the rule belongs to the operator (Section 6, D1). Nothing here is an organizer score. Every number is labelled by evidence class.

Evidence labels used below: **OFFICIAL** (rules or competition page, fetched this session) · **LIVE** (public page fetched this session) · **REPRODUCED** (recomputed in this session) · **REPO-CLAIM** (stated in this repo, not re-verified) · **HOLDOUT-DTI** (local hide-and-recover, not a leaderboard score) · **CLAIM** (owner-reported, no receipt).

---

## 0. Three-pass record

| Pass | What was done | Result |
|---|---|---|
| 1 — implement & verify | Installed pinned deps (`requirements.txt`), ran the full test suite, ran `check_site`, `render_public_status --check`, `gems manifest`, `gems ledger`, `make validate` on the current primary | Baseline: 539 passed, **3 failed** |
| 2 — bugs, assumptions, edge cases | Diagnosed the 3 failures: `tiltangle.html` lacked `<main>`; its TIF was served but not linked from `index.html`; README said the brief was both "verbatim" and "normalized". While this session ran, `main` fixed the same three failures in PR #128 (`85b4366`). I discarded my duplicate edits and kept `main`'s versions | Merged branch: 528 passed, 0 failed |
| 3 — recheck against the request | Independently downloaded and hashed the public witness raster; recomputed footprint overlap for the current primary; checked the official metric and format text; wrote this review, run card and README brief | See §1–§7 |

---

## 1. Why no new TIFF can be cleared right now (REPRODUCED)

**Official text** (DrivenData problem page, fetched 2026-10-25): *"Your submission contains a single layer with datatype of 32-bit float (`float32`) with values between 0 and 1"* and *"Your submission has the same bounds as the training data, and data outside the bounds is null or nan."* — <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>

**Witness** (`17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif`, cited in `evidence/current_witness_recheck_20261024.json`). I downloaded the blob through the GitHub API this session:

| Check | Result |
|---|---|
| Git blob SHA-1 (recomputed from bytes) | `374c88b1da2b803e2ed160de467fd71ae114010d` — matches the pin |
| File SHA-256 (recomputed) | `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be` — matches the repo's record |
| Size | 25,065,181 bytes |
| Grid | EPSG:32611, 3730 × 3292, float32, transform (100, 0, 243350, 0, −100, 4508550) — same as the official template |
| Finite cells / positive cells | 5,167,373 / 5,167,373 |
| Official footprint (non-NaN cells of the official `sample_submission.tif`) | 5,167,373 |
| Positive fraction of footprint | **1.000** |

**Current primary** (`h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif`, SHA-256 `58e5d780…048b17`): all **37,654** nonzero cells lie inside the footprint. Because the witness is positive on the whole footprint, every one of those dots is within 0 px of a witness positive. The literal forward overlap is therefore **1.000 > 0.70**. This holds for any in-footprint candidate.

**Every served candidate has the same problem.** I scanned all 109 TIFs in `docs/downloads/` on the merged branch. In every file with positive cells (109 of 109), all positive cells lie inside the official footprint. The literal overlap is therefore 1.000 for every served candidate, including the new VARIO full raster (37,654 of 37,654 positives inside the footprint).

**Consequence.** The literal rule is unsatisfiable for any submission. It does not measure lane duplication. It measures "is this inside the footprint?" The repo's own sparse-public reading (PR #125 and `VENTSCARP`) passes at about 0.41–0.69, and the repo-reported surface Spearman against this witness is 0.056 (APRONRIDGE, `evidence/current_witness_recheck_20261024.json`). That reading is a choice, and the operator must make it. An agent should not make it silently.

---

## 2. Why GEMSDOE32 reportedly scored 0.2778 — and why that is not yet explained

### 2.1 Verified facts

- **OFFICIAL metric.** Distance-weighted Tversky index, α = 0.2 (false positives), β = 0.8 (false negatives), triangular kernel with 300 m support (3 px). Formula on the problem page: TP_w = Σ_g max_x p(x)k(d); FP_w = Σ_x p(x)[1 − max_g k(d)]; FN_w = Σ_g [1 − max_x p(x)k(d)]; DTI = TP_w / (TP_w + αFP_w + βFN_w + ε). <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- **REPRODUCED.** The page's worked example (TP_w = 3.00, FP_w = 1.89, FN_w = 2.00) gives 3/(3 + 0.2·1.89 + 0.8·2.00) = **0.6027**, which the page rounds to 0.60. The repo's independent test (`tests/test_metric_independent.py`) checks the same example.
- **OFFICIAL rules.** "Three submissions per week" and "one final submission" chosen before the private score is known. <https://docs.nlr.gov/docs/fy26osti/96647.pdf> (§3.2, §3.4, §3.5, §3.6.2).
- **OFFICIAL rules §3.2:** generative-AI use must be **indicated in the narrative**. This repo's `AI_USE.md` is the place for that disclosure.
- **LIVE leaderboard** (fetched 2026-10-25): #1 xiaofanhu **0.4413**, #2 cfld__ 0.3916, #3 Batik Shirt Brothers 0.3904, … #22 kinghorton42 0.3261. <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>. Ranks shift between snapshots: the repo's 2026-10-24 snapshot lists #23 at 0.3217, so ranks 23–50 were not re-read today.
- **0.3195 is not in the live top 22.** The repo's 2026-10-24 top-50 snapshot also lacks it (`docs/ANALYSIS_20261025_LEADERBOARD.md`, IR-25-0.3195). Neither source supports "0.3195 is the highest score right now."
- **0.4413 is xiaofanhu's public score, not a GEMSDOE entry** (same analysis, IR-25-0.4413).
- **GEMSDOE32's own page** (LIVE, fetched 2026-10-25) labels its primary file **UNSCORED — "NO ORGANISER SCORE EXISTS"**, gives a projected live DTI of **0.2747 ("a MODEL, not a score")**, and gives an anchor of 0.2708 (already scored). <https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html>. The 0.2778 figure in the brief is therefore **CLAIM** with no receipt.

### 2.2 The mechanism that the metric does imply (derived, REPRODUCED)

Take a unit of prediction mass placed at a pixel whose expected credit is c ∈ [0,1] (its distance-weighted contribution to TP). Under the official definitions, to first order and ignoring max-interactions:

- dTP_w = c, dFP_w = 1 − c, dFN_w = −c.
- dD = dTP + α·dFP + β·dFN = c + α(1 − c) − βc = α + c(1 − α − β) = **α**, since α + β = 1.
- dS/d(mass) ∝ c·D − T·α, so **adding mass helps only if c > α·S = 0.2·S**.

This is the break-even the GEMSDOE32 page cites. Its figure of 0.0548 credit per dot corresponds to S ≈ 0.274, which matches its own projection of 0.2747. That is internal consistency, not a receipt. For S = 0.2778 the break-even is **0.0556**.

Why this matters:

1. **The metric rewards credit density, not raw coverage.** A file improves only if its mass has expected credit above 0.2·S. Thinning a diffuse surface to its highest-credit pixels can raise S even while total mass falls. That is a plausible reason sparse, high-credit sets outscore diffuse surfaces.
2. **The 300 m kernel is generous.** A prediction 1–3 px from a truth pixel still earns partial TP credit, which rewards geometrically plausible placement over exact-pixel placement.
3. **The public test set is new faults, not catalogue faults.** The problem page says the test labels are faults "manually identified… not contained within the current public USGS database." A holdout that hides catalogue segments measures recovery of catalogue geometry, and the repo's own IR-32-PROXY-01 states it "cannot reward a genuinely new fault." **Local HOLDOUT-DTI and the leaderboard can disagree**, and this repo has no organizer receipt that shows how well they agree.

### 2.3 Can we beat 0.2778?

**Not demonstrated, and not measurable from this sandbox.** A beat requires a detector whose expected credit on *new* faults exceeds 0.2·S (≈0.056 for S = 0.278). No local result in this repo has been shown to exceed that on the competition's kind of labels. The best local HOLDOUT-DTI values use different instruments and are not comparable (§4, irregularity I-6). We therefore claim no leaderboard gain. The untried routes that could raise credit density are in §3.

---

## 3. Untried hypotheses — ranked (3–5 required; none validated)

Untried was checked by case-sensitive grep of `gems/` and `scripts/` (code, not docs). Hits: `Landsat`, `NDVI`, `surface temperature`, `NAIP`, `GNSS`: **0 code hits**. `1m DEM` / `1-m DEM`: **0 code hits**; it appears only in `docs/` as "HELD: needs DrivenData login." `GPS` and `InSAR` appear in code comments that describe strain bands already in the training stack (`gems/coulomb.py`, `gems/geotension.py`), so a separate GNSS layer would duplicate them.

Ranking is **qualitative** (High / Med / Low). It is not a DTI projection, and no number here is a score.

| Rank | Hypothesis | Layers | Physical signature | Why it could catch a fault missing from the catalogue | Named non-fault mimic | Difference from implemented code | Cost | Data source and verification |
|---|---|---|---|---|---|---|---|---|
| **1** | **Expert-instrument scarp/lineament detector at 1 m** | 1 m DEM from the competition's `1m_DEM_links.csv` | Sub-10 m linear scarps and shear lineaments (LoG / curvature at 1–3 px), max-aggregated to 100 m | The test labels were drawn by experts. The NLR rules describe "newly identified faults labeled by geology experts" (§2). The 1 m DEM is plausibly the matching terrain source (inference, not stated by the sponsor). Scarps too small for a 10 m DEM would be visible at 1 m. | Roads, canal berms, cut banks, Lake Lahontan shoreline terraces. Mask roads with an official roads layer (not yet verified). | Repo uses only 10 m 3DEP (`gems/ventscarp.py`) and the 100 m template bands. No 1 m code exists. | **High** (multi-GB tiles) | DEM links are in the competition's data tab (DrivenData login). **Not obtainable from this sandbox.** The official problem page says the link list is provided. |
| **2** | **Thermal–greenness lineaments from Landsat** | Landsat Collection 2 Level-2 Surface Temperature (K) and NDVI from Level-2 surface reflectance; multi-year summer composites | Along-strike, season-persistent linear excess in surface temperature and greenness | Fault-conducted groundwater can produce linear thermal and vegetation anomalies with no preserved scarp. Blind faults under cover are the target. | Irrigation, playa margins, topographic thermal shading. Deconfound with the 3DEP aspect and the template's slope bands. | No thermal-IR or vegetation layer in `gems/`. Closest is `docs/HYPOTHESES_20261026_CURIEDEMAG.md` #5, marked "NOT VIABLE in this sandbox." | **High** (scene download, cloud masking, mosaics) | Product verified: USGS Landsat C2 L2 Surface Temperature. <https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products>. **Bulk download route not verified; sandbox cannot reach it.** |
| **3** | **Expert-verifiable round-2 selection policy** (decision rule, not a layer) | Existing candidates only | Prefer high-credit, mappable lineaments with a stated mechanism that experts can check | The Final Prize Round re-scores on labels that experts add after reviewing submissions. Predictions an expert can verify have value beyond the current labels. | Confidently wrong lineaments that experts reject | Not a model. Affects selection, not geophysics. | **Low** | Official: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/> ("Final Prize Round"). **Not holdout-testable.** Only the public leaderboard (3 per week) can test it. |
| **4** | **NAIP tonal/vegetation lineaments** | USDA/USGS NAIP imagery (~1 m) structure-tensor coherence | Linear tonal discontinuity and vegetation contrast along trend | Surface alteration or spring-line vegetation along a blind fault | Roads, fences, field boundaries (mask with roads) | No imagery layer in `gems/`. | **High** | **Not verified in this session.** |

**Top candidate and validation status.** Rank 1 would be the top candidate under the user's rule ("validate the top candidate on the spatially-blocked holdout before touching a weekly slot"). **It cannot be validated here**: the 1 m DEM is login-gated, and the 19-band feature stack is absent from `.cache/` (`evidence/site_download_run_card_20261024.json`). No candidate was built, no holdout was run, and no slot was spent.

---

## 4. Irregularities flagged for review

| ID | Irregularity | Evidence | Severity | Action taken |
|---|---|---|---|---|
| I-1 | The literal duplicate rule is unsatisfiable for any in-footprint raster (dense full-footprint witness). | §1 (REPRODUCED) | **Blocking** | Not changed. Operator decision D1. |
| I-2 | **Encoding conflict.** Official text: outside the bounds, "null or nan." The repo gate (`gems/gates.py`, `submission_encoding`) requires **zeros** outside and no NaN, and `SESSION_PROMPT.md` calls NaN-outside files "not upload-safe." Both encodings exist in `docs/downloads/`: 97 `-zeros.tif` files are zeros-outside; 12 unsuffixed TIFs are NaN-outside (7,111,787 NaN cells, the official template's count). Re-run this session: `gems validate` on `h33-h33-2-b2-DILATATIONp10dilatation-20261025-2e501f88.tif` (NaN-outside) gives PASS for `values_in_0_1` and `nan_outside_footprint`, and **FAIL** for `submission_encoding` (`all_finite=False`, `zero_outside=False`). The same file would pass the official wording; the repo's gate is stricter than the rules. The policy rests on an inferred cause of the portal error (§6, D2), not on a portal test. | Official page; `gems/gates.py`; `SESSION_PROMPT.md`; file scan (REPRODUCED) | **High** | Not changed (changing the gate changes every result). Operator decision D2. |
| I-3 | The brief's 0.2778 is a CLAIM. GEMSDOE32's page says UNSCORED. | §2.1 (LIVE) | High | Labelled CLAIM everywhere. |
| I-4 | The brief's "0.4413 is the GEMSDOE high score" is wrong. It is xiaofanhu's score. | Live leaderboard; repo IR-25-0.4413 | High | Stated in §2.1. |
| I-5 | The brief's "0.3195 is the highest right now" is not supported. The live top 22 does not contain it. | Live leaderboard; repo IR-25-0.3195 | Medium | Stated in §2.1. |
| I-6 | Conflicting "best holdout" claims on different instruments: static deployment `d_cat>2` (LISTRICLOQO 0.013295), Rule-2 `d_visible>2` (COULOMBLOQO 0.113316), and FAULTNET/NETEXPAND contexts (0.175147 / 0.177976). These are not comparable. | README current status, `SESSION_PROMPT.md` | **High** | Flagged; no number was promoted. |
| I-7 | "PRIMARY" differs by banner. `check_site.py` reports LISTRICLOQO; older banners name NETEXPAND, FLEXMAG, LISTRICDIP and VENTSCARP as primary. Several "latest"/"newest" banners conflict. | README; `scripts/check_site.py` output | Medium | `docs/downloads/current_submission.json` is the machine source. Recommend retiring the old banners. |
| I-8 | **Open PR #125** ("GAPBRIDGE-V2: READY TO SUBMIT") puts green READY-TO-SUBMIT banners on the site. Its own text concedes the literal dense-surface overlap is 1.0 and calls it a "category artifact." That contradicts `main`'s binding decision. | `gh pr view 125` | **High** | **Not merged.** Operator decision D1 decides it. |
| I-9 | About 25 open PRs from parallel sessions. Only #126 is merged. | `gh pr list` | Medium | Not touched. |
| I-14 | **Two "current" files.** The README's top banner (VARIO, added to `main` during this session) calls a new raster "a new unique GeoTIFF" and offers it as the lead research download. The machine-readable `docs/downloads/current_submission.json` still names LISTRICLOQO. The VARIO file has the same literal overlap of 1.000 as every other candidate (§1). | README top; `current_submission.json`; full scan (REPRODUCED) | Medium | Not changed. Recommend one machine-readable source for the top banner (see D5). |
| I-15 | **`main` was red before this session's changes.** The LISTRIC-HALO lane (merged via PR #132) served `gemsdoe92-listric-halo-32k-20261025-zeros.tif`, which is not linked from `index.html` and fails the catalogue-distance gate (`dots_within=4750` at radius 2 px; strict `> radius` required). The lane's own run card says `verdict: negative`. Checked on `origin/main` alone (archive export): same 1 failed test and same site-gate failure. | `git archive origin/main` + `pytest` + `scripts/check_site.py` (REPRODUCED) | **High (publication gate)** | I first moved the three files (`.tif`, `.zip`, `.json`) out of the served path to `evidence/quarantine/listric-halo-32k/` (531 tests pass; site gate passes). While this branch was in review, `main` removed the files entirely (upstream tree at cf1f99a contains no LISTRIC-HALO files). This branch accepts that removal and drops my quarantine copy. Git history keeps the files. Current merged tree: 549 tests pass; site gate passes on 103 served rasters. |
| I-10 | **Competition-derived data is tracked in git and mirrored in public repos.** `git ls-files data` shows 8 tracked files, including `data/bridge/labels.tif` (byte-identical to `existing_faults.tif`) and `sample_submission.tif`. `registry/session_manifest.json` pins the 419 MB `training_features` stack to a public mirror, marked "upstream UNVERIFIED" with "redistribution unchecked." | `git ls-files`; `registry/session_manifest.json` (REPRODUCED) | **High (legal)** | Not used to build anything. **Operator/legal review needed** (D4). |
| I-11 | Three failing tests on `main` (site contract, README wording). | `pytest` baseline | Medium | **Fixed on `main` by PR #128** while this session ran; my duplicate fix was dropped in the merge (§0). |
| I-12 | README said the brief was "verbatim" and "normalized" at once. | README lines ~444 and ~494 | Low | **Fixed on `main`** (PR #128). |
| I-13 | Rule 3.2 requires AI-use disclosure in the narrative. Not verified that the submission narrative includes it. | Official rules §3.2 | Medium | `AI_USE.md` exists; the submission narrative must cite it (D5). |

---

## 5. Verification table (line by line; every source fetched or recomputed this session)

| # | Claim | Source | Status |
|---|---|---|---|
| V1 | Metric: distance-weighted Tversky, α = 0.2, β = 0.8, 300 m triangular kernel | <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/> | OFFICIAL (fetched) |
| V2 | Float32, single layer, values in [0,1]; outside bounds "null or nan" | same | OFFICIAL (fetched) |
| V3 | Three submissions/week; one final submission | <https://docs.nlr.gov/docs/fy26osti/96647.pdf> §3.2, §3.4 | OFFICIAL (fetched) |
| V4 | Labels from INGENIOUS and USGS; hidden test = new expert-labelled faults | NLR rules §3.3; problem page | OFFICIAL (fetched) |
| V5 | Live #1 = 0.4413 (xiaofanhu) | <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/> | LIVE (fetched) |
| V6 | GEMSDOE32 primary is UNSCORED; projected 0.2747 is a model | <https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html> | LIVE (fetched) |
| V7 | Worked example → 0.6027 (page: 0.60) | problem page; computed | REPRODUCED |
| V8 | Witness blob SHA-1 / file SHA-256 / 5,167,373 of 5,167,373 positive | GitHub API blob `374c88b1…`; computed | REPRODUCED |
| V9 | Current primary: 37,654 positives, all inside footprint, values in [0,1]. Same check on all 109 TIFs in docs/downloads: 109/109 have every positive inside the footprint | computed against the official template footprint | REPRODUCED |
| V10 | Shared validator PASS (9 gates) on the current primary; NaN-outside file FAILS only `submission_encoding` | `make validate FILE=…`; `gems validate` on the DILATATION NaN-outside file | REPRODUCED |
| V11 | Full test suite: 528 passed on the merged branch (baseline before any fix: 539 passed, 3 failed) | `pytest tests` | REPRODUCED |
| V12 | Site gate: 93 served rasters PASS | `scripts/check_site.py` | REPRODUCED |
| V13 | Break-even credit = α·S (derivation) | §2.2 | DERIVED (algebra checked) |
| V14 | Landsat C2 Surface Temperature is a free USGS product | <https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products> | OFFICIAL (search result; page not fetched in full) |
| V15 | EarthScope GNSS: web services need no login; bulk velocity archive needs a login | <https://www.unavco.org/data/web-services/web-services.html>; <https://www.earthscope.org/data/> | OFFICIAL (search result) |

**Not verified:** Landsat bulk-download route, NAIP access, roads-mask source, USGS National Map reachability. The bash sandbox allow-list is GitHub, npm and PyPI only. `fetch_page` reads public pages; it was not tried on multi-GB tiles.

---

## 6. Operator decisions needed (the user asked for no manual input; these cannot be decided by an agent)

- **D1 — Dense-witness policy.** Options: (a) keep the literal rule (nothing can ever clear); (b) define "dots" for a dense probability surface as its top-K mass and recompute overlap, which VENTSCARP and PR #125 both do, with the reading stated in the run card; (c) exclude full-footprint surfaces from the dot-overlap test and keep the surface Spearman test. This session makes no choice.
- **D2 — Encoding.** Test one upload of a NaN-outside file, or of the official sample template, before choosing. A test upload spends one of three weekly slots. The DTI is unchanged either way, because zeros outside contribute no false positives (FP sums over p > 0).
- **D3 — Data placement.** Download `training_features.tif`, `labels.tif`, `sample_submission.tif` and `1m_DEM_links.csv` from the DrivenData data tab (login) into `data/` or `.cache/gems_inputs/`. Then `python scripts/restore_inputs.py` can verify hashes, and the 1 m DEM can be fetched from the links.
- **D4 — Public competition data.** Decide whether competition-derived files belong in a public repo. Check the DrivenData rules first.
- **D5 — PR backlog and AI disclosure.** Decide which open PRs to close or merge (not PR #125 until D1 is settled). Add the AI-use narrative to the submission.

---

## 7. Limitations and next session

**Limitations in the way of a successful project**

1. No competition feature stack or 1 m DEM in this sandbox. Only GitHub, npm and PyPI are reachable from bash.
2. Literal duplicate rule unsatisfiable (I-1). Format rules conflict (I-2).
3. HOLDOUT-DTI measures catalogue recovery, not new-fault discovery (§2.2 point 3). Local ranking may not transfer to the leaderboard.
4. No organizer receipt for any GEMSDOE file. Owner-reported scores are CLAIM only.
5. Competition data is tracked in a public repo (I-10).

**Next session, in order (no slot until D1–D3 are settled)**

1. Operator makes D1–D3. Confirm the leaderboard snapshot and the GEMSDOE32 status again.
2. If D3 is done: run `scripts/restore_inputs.py` and verify hashes. Build the 1 m DEM scarp detector (rank 1) under the protocol: pre-registered, leakage canaries, buffered holdout. Do not place dots before the holdout beats the current best on the same instrument.
3. Pre-register the Landsat thermal–greenness lineament hypothesis (rank 2) with an explicit mimic test on irrigated fields and playa margins.
4. Settle D2 with one upload, using the operator's weekly slot.

**Maximize P(Win):** a reproducible negative is worth more than a dense-witness-breaking file that might not clear. **Own the Outcome:** the blocker is named, measured and handed to the operator with options.
