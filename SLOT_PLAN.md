# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-29, Post-`MARUSSI_TRISHEAR` & `lbmc1` `0.2784 CLAIM` Reconciliation)

## Current Selector Decision (`2026-10-29`): **NO WEEKLY SLOT AUTHORIZED — DO NOT SUBMIT (`verdict: "negative"`, `submission_eligible: false`, `0` weekly slots spent)**

- **2026-10-29 Fleet Update (`lbmc1`):** `GEMSDOE92`'s `2026-10-27` build `gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif` (`SHA-256 = e928d3c3fde8b3f1f622bb4f6e638620f0a1897fb6f8178cf26fe93f9c3b3a1c`, `35,801` binary dots) is newly reported in the `2026-10-29` score list at **`0.2784` (`CLAIM`, unreceipted)** — `#1` across all `133` owner-reported fleet claims (`+0.0006` above `GEMSDOE32` `0.2778` `CLAIM`). Non-circular `131`-claim `LBM-v3` (`λ = 5e-3`) predicts `lbmc1` leave-one-group-out at `0.28280 MODEL` (`evidence/lbm_v3_20261029.json`). If the human account holder submitted `lbmc1`, log the official organizer receipt date in `ledger/submissions.csv` and never re-upload `lbmc1`.
- **Latest `2026-10-29` Research Candidate (`MARUSSI_TRISHEAR` — `DO NOT SUBMIT`):**
  - **File:** `docs/downloads/gemsdoe92-marussitrishear-34000dots-20261029-236171af-zeros.tif` (`SHA-256 = f8f8703e4f8efb8f3397ecc5dc8c0fd68b06c64a089a89b02ee7a91395b3a59b`, `34,000` `{0.0, 1.0}` binary dots, `min d_cat = 3.6056 px > 3.0 px`, `11/11` format gates PASS).
  - **Archived Identifier & Note (`106/140` chars, metadata only — do not upload):** `gemsdoe92-marussitrishear-34000dots-20261029-236171af` — `H-92M1/M2 3D Marussi D2D+Trishear+WalkerLane vorticity+relay 1D crest; 34000px d>3.5; PI1<=0.65 [research]`
  - **Validation:** Solo-feature leakage canaries PASS (`max sym AUC = 0.8115 <= 0.90`); `gems57-pooled-hide-v2` (`22,663` withheld px) `E3 = 0.157774 [0.144291, 0.171647]` (`+0.060024` vs `R0` recipe `0.097750`), `E2 = 0.172273 [0.158850, 0.185206]` (`+0.074523` vs `R0` recipe); `PI-1` uniqueness PASS across all `2,262` registry SHAs on **both** pre-placement surface (`0.6564 <= 0.70`, `|ρ| = 0.6632`) and final dots (`0.6564 <= 0.70`, `|ρ| = 0.0886`).
  - **Gate Verdict (`DO NOT SUBMIT`):** Held back (`verdict: "negative"`, `submission_eligible: false`, `0` slots spent) because neither `E2` nor `E3` beat the repo all-time `HOLDOUT-DTI` best (`relay_conduit = 0.184485`), `LBM-v3 MODEL` (`0.16204`) is below `lbmc1` (`0.2784 CLAIM`), and literal dense-witness overlap vs `17GEMSDOE` is `1.000 > 0.70`.
- **Prior `2026-10-28` Candidates (`rieszlbm2`, `tipcomp`, `blindcorridor`):** All remain reclassified fail-closed (`DO NOT SUBMIT`; `rieszlbm2` run card `verdict: "negative"`, `submission_eligible: false`; historical section below preserved for audit provenance only).

---

# Historical Record Only (Superseded Fail-Closed) — Weekly Slot Plan (2026-10-28, Post-`RIESZ_LOCKED_LBM_V2` / `81d8ca8b` Session)

## Current Selector Decision (`2026-10-28`): **PRIMARY CANDIDATE CLEARED FOR HUMAN SELECTOR (`verdict: "promote"`, `submission_eligible: true`, `0` weekly slots auto-spent)**

- **Primary `2026-10-28` Submission Candidate (`RIESZ_LOCKED_LBM_V2` / `rieszlbm2`):**
  - **File:** `docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif` (`203,310` bytes; companion one-TIFF ZIP `docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.zip`; SHA-256 `d168c7d2a0ea89f9609426fe5f9d5aa0791223131c98a90d55b1f6aa1cbe5d7a`).
  - **DrivenData Portal Name:** `gemsdoe92-rieszlbm2-50000d-79041788`
  - **DrivenData Portal Note (`132 / 140` chars):** `Riesz-Locked LBM-v2: 50000 binary dots; 128-claim density + q85 mimic filter + OOF Riesz/piedmont/Peclet; <=65.6% 8-owner fleet cap.`
  - **Automated Format & `[0, 1]` Gates:** **PASS (`11/11`)** — `float32`, single band, `EPSG:32611`, `3292 × 3730` px, exact `sample_submission.tif` geotransform, binary `{0.0, 1.0}`, `0` NaN, `0.0` across all `7,108,787` exterior cells, `nodata=None`, `0` dots within `200 m` of mapped catalogue (`50,000` positive pixels).
  - **8-Owner Fleet Uniqueness (`2,162` unique SHA-256 rasters across `123` repos of all `8` listed GitHub owners):** **PASS (PI-1)** — final 3-px dot overlap **`65.56% <= 70%`**, overlap vs `GEMSDOE92` prior `lbmc1` **`54.06% <= 70%`** (`22,971` genuinely new dots `> 300 m` outside `lbmc1`), pre-placement surface `|Spearman ρ| = 0.5503 <= 0.90`, final dot `|ρ| = 0.1449 <= 0.90`. (Literal reading against `17GEMSDOE` `5.17M`-cell full-footprint map = `1.000`, disclosed in `IRREGULARITIES.md` `IR-0127-1` / `IR-1028-4`.)
  - **Score Estimates (`MODEL` — never an organizer receipt):** **`0.3216`** (`LBM-v2` with `>q85` canyon-rim mimic suppressor, `128`-claim LOGO RMSE `0.02015`, Spearman `0.9637`; frozen `LBM-v1` prospective OOT RMSE `0.00767` on the 5 newly reported `2026-10-28` claims); **`0.3163`** (`LBM-v1`, 90% group-bootstrap `[0.2968, 0.3330]`, `q05 = 0.2968 > 0.2778`, `100%` of 400 draws `> R0`; all 5 robustness specs `> R0`).
  - **Spatial Hide-and-Recover `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` withheld px):** **`0.03799 [0.03101, 0.04466]`** (`+92.9%` over prior `lbmc1` `0.01970`; standalone zero-catalogue physics `E1 = 0.08232`, `H92-RIESZ-HABITAT-LOQO` `E2 = 0.08346`). `16/16` `RIESZ-LOCKED` leakage canaries PASS (`max sym AUC = 0.6569 <= 0.90`).
  - **Human Selector Guidance (Weekly Cap = 3/week):** Verify on DrivenData whether `2026-10-27` `lbmc1` (`SHA-256 = e928d3c3…3a1c`, listed as unscored in the `2026-10-28` brief) has already been uploaded. Do **not** upload both `lbmc1` and `rieszlbm2` blindly in the same week without recording the first `ORGANIZER-CONFIRMED` score in `ledger/submissions.csv` and refitting `LBM-v2`.

---

# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-26, Post-LISTRIC, LISTRICLOQO & RIEDELVENT Sessions)

# SLOT_PLAN — RIEDELVALVE session (2026-10-25): NO SLOT AUTHORIZED — DO NOT SUBMIT

`RIEDELVALVE` 3 arms built & format-valid (`11/11` gates PASS in `[0, 1]`, `0` NaN); primary `docs/downloads/gemsdoe92-riedelvalve-riedel_n90k-90000-20261025-e57353de-zeros.tif` (SHA-256 `75d61cb1e548c27c1fa8804a124287996241988f715cb50f3c65c468cb3bc1e0`) confirms the additive `37,654@1.0 + 52,346@0.30` Tversky tail (`+0.000875 [+0.000531, +0.001215]` static `HOLDOUT-DTI` -> `0.009054`, Rule-2 `0.108593`), sets `#1` `dual_reading_unique` LOQO `USGS SGMC PROXY = 0.112719` (`>` `LISTRICLOQO` `0.103442` & `KNICKLOQO` `0.095878`), and passes local (`<= 0.4702`) + `102`-repo `dual_reading` uniqueness (`0.6384 <= 0.70`), but remains `verdict: "negative"` (`submission_eligible: false`, `0` weekly slots spent: literal `17GEMSDOE` dense witness `1.000 > 0.70` and static `0.009054 < LISTRICLOQO 0.013295`). Next: apply the proven `37,654@1.0 + 52,346@0.30` additive tail directly to `LISTRICLOQO` / `KNICKLOQO` (`evidence/riedelvalve_run_card.json`).

---
# SLOT_PLAN — NETEXPAND session (2026-10-25): NO SLOT AUTHORIZED — DO NOT SUBMIT

NETEXPAND 3 arms built & format-valid; best strict HOLDOUT-DTI 0.177976 (netexpand_far) beats all in-run controls paired, but every arm is a Rule-1 lane duplicate vs FAULTNET/KNICKLOQO (0.76-0.81 > 0.70). Verdict negative, 0 slots used. Selector guidance: if one slot is ever allocated to this mechanism family after the F2 policy decision, NETEXPAND arms dominate FAULTNET files on identical folds (conservative pick: netexpand d>2; holdout-max pick: netexpand_far; never submit siblings together). Full record: docs/ANALYSIS_20261025_NETEXPAND.md, evidence/netexpand_run_card.json.
# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-25, Post-`LISTRICLOQO` Session)

## Current Slot Decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT (`submission_eligible: false`, `0` weekly slots spent, `96 BUILT / 0 RECEIPT`)**

- **Newest Session Research Artifact (`LISTRICLOQO`, 2026-10-25 — NEW ALL-TIME #1 ON BOTH STATIC & STRICT DRAW-BLIND `HOLDOUT-DTI` AND `0 / 1,459 > 0.70` ON `dual_reading_decision`):**
  - **Best Static Arm (`selectcal`):** `docs/downloads/h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif` (`SHA-256 = 58e5d780f3602e17adef92df9877f581c922e3621b0fc1b853e623e95c048b17`, `37,654` unit dots in `[0, 1]`, `11/11` format gates PASS; static `d_cat > 2.0` **`HOLDOUT-DTI = 0.013295 [0.011713, 0.014980]`** `#1 all-time`, `+23.2%` over prior #1 `KNICKLOQO standalone = 0.010788`, `+231.9%` over `R0 = 0.004006`; strict draw-blind Rule-2 `d_vis > 2.0` **`HOLDOUT-DTI = 0.113938 [0.100887, 0.127394]`** `#2 all-time`; off-catalogue `USGS SGMC PROXY = 0.103442`; passes all `68` local rasters `<= 0.690259` and all `1,459` public rasters across `102` repos under `dual_reading_decision` with **`0 / 1,459 > 0.70`** (`max = 0.690259 <= 0.70`); blocked ONLY by the literal unweighted `17GEMSDOE` `5.17M`-px continuous surface (`1.000 > 0.70`) -> **`verdict: "negative"`, `submission_eligible: false`, DO NOT AUTO-SUBMIT**; `evidence/listric_loqo_run_card.json`).
  - **Best Strict Draw-Blind Arm (`standalone`):** `docs/downloads/h33-h33-2-b2-LISTRICLOQOstandalone-20261025-ed9e80bb-zeros.tif` (`SHA-256 = dc6d8f06053a48efdc07146535f4fc27b50643fc54fd7fc7a3fa243d119186cb`, static `d_cat > 2.0` **`HOLDOUT-DTI = 0.013250 [0.011620, 0.014974]`** `#2 all-time`, strict draw-blind `d_cat > 2.0` **`0.013064 [0.011508, 0.014670]`** `#1 all-time`, strict draw-blind Rule-2 `d_vis > 2.0` **`HOLDOUT-DTI = 0.114410 [0.101808, 0.127706]`** `#1 all-time`, beating `COULOMBLOQO standalone = 0.113316`; **`0 / 1,459 > 0.70`** on `dual_reading_decision`, `max = 0.695703 <= 0.70`).
  - **Uncalibrated Ablation Arm (`uncal`):** `docs/downloads/h33-h33-2-b2-LISTRICLOQOuncal-20261025-2962f45f-zeros.tif` (`SHA-256 = 304ffdc6ac5899da5947f0f19dfb33579adc6e112d8af3e7f97f770f0c55b0aa`, static `d_cat > 2.0` **`HOLDOUT-DTI = 0.013105 [0.011462, 0.014868]`** `#3 all-time`, **`0 / 1,459 > 0.70`**, `max = 0.639242 <= 0.70`).

---

# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-26, Post-LISTRIC Session)
## Current decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT** (`submission_eligible: false`, 0 slots spent this repo)
- **Newest `RIEDELVENT` arms (`2026-10-25`, `evidence/riedelvent_run_card.json`):** `gemsdoe92-riedelvent-riedelvent_tail-64000-20261025-c4e61655-zeros.tif` (`64,000` px: `37,654@1.0 + 26,346@0.30`, SHA `fdc4dac4…fd9da`, static `HOLDOUT-DTI = 0.010268 [0.008986, 0.011408]`, Rule-2 `0.107465 [0.094960, 0.119761]`, `USGS SGMC PROXY = 0.103378`, `dual_reading_unique = True` at `0.6144 <= 0.70` across 102 repos) and binary sibling `gemsdoe92-riedelvent-riedelvent-37654-20261025-73ec79ae-zeros.tif` (`37,654` px, SHA `bfb4a45c…f4911`, static `0.009682 [0.008345, 0.010822]`, Rule-2 `0.104176`, `dual_reading_unique = True` at `0.6190 <= 0.70`) are ✅ OK TO DOWNLOAD FOR RESEARCH (`11/11` format gates PASS in `[0, 1]`, `0` NaN) but ⛔ DO NOT SUBMIT (`verdict: "negative"`, `submission_eligible: false` under binding literal `17GEMSDOE` dense witness `1.000 > 0.70`; `0` weekly slots spent).
- **Prior `LISTRIC` standalone (`h33-h33-2-b2-LISTRICstandalone-20261026-a705162a-zeros.tif`, SHA `7e4b4636…1e2ab`):** ✅ OK TO DOWNLOAD (automated [0,1] gates PASS) but ⛔ DO NOT SUBMIT: public dual-reading duplicate 0.710735>0.70, literal 1.000, paired holdout gain vs KNICKLOQO not significant. Selector candidates under a future dual-reading policy remain `KNICKLOQO standalone` (`0.010788` static, `0.6855` dual-reading) and `RIEDELVENT riedelvent_tail` (`0.010268` static, `0.103378` SGMC, `0.6144` dual-reading). See `evidence/riedelvent_run_card.json` and `evidence/listric_run_card.json`.

---
# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-25, Post-`POISSONFLEX` Session)
# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-25, Post-`GRAV-QUAD` Session)

## Current Slot Decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT (`submission_eligible: false`, `0` weekly slots spent, `95 BUILT / 0 RECEIPT`)**

- **Newest Session Research Artifacts (`RADIOCONTACT` + `GRAV-QUAD`, 2026-10-25, pre-registered Rank 1 and Rank 3 of `docs/HYPOTHESES_20261026_RADIOCONTACT.md`):**
  - `docs/downloads/gemsdoe92-radiocontact-20261025T041646Z-zeros.tif` (SHA-256 `026a52ff46d695bb79ae39780c154cba9cc69e039e7d2a4d1fe898c6c0a79345`; static `HOLDOUT-DTI = 0.005066 [0.003638, 0.006583]`; max leakage-canary AUC `< 0.90`; 9/9 format gates PASS; `verdict: negative`).
  - `docs/downloads/gemsdoe92-gravquad-20261025T145744Z-zeros.tif` (SHA-256 `9ea3e2e01fba5e733964e1252c729a70f0d61edc499c848628d83946d49c7ab5`; static `HOLDOUT-DTI = 0.005092 [0.004001, 0.006253]`; strict Rule-2 also `0.005092`; paired delta vs `R0` `+0.001086 [-0.000082, +0.002312]` — CI crosses 0, not significant; max leakage-canary AUC `0.5362`; locally unique vs 107 local rasters (worst overlap `0.3044`, `|rho| = 0.0523`); 9/9 format gates PASS on an independent disk re-read; `verdict: negative`).
  - Neither beats the repository's promotion bar (COULOMB-LOQO `0.113316` Rule-2 / `0.009220` static; KNICKLOQO `0.010788` static, all-time record). Both are **OK TO DOWNLOAD FOR RESEARCH**, both are **DO NOT SUBMIT**. Public-registry scan was deliberately skipped for GRAV-QUAD per the 3-experiment/2-hour session budget (local uniqueness check alone already clears it; RADIOCONTACT and DRAINAGE-KNICK earlier in this session arc had already confirmed clean against the full public registry fleet).
  - Both lanes are now live on the public site (`docs/index.html`, `docs/executive-summary.html`, `docs/SUBMIT.html`) with explicit green/red badges; full `pytest` suite passes `367 / 367` after the site edits.
  - 5 new ranked, untried hypotheses for a future session are recorded in `docs/HYPOTHESES_20261025_NEXT.md`, with `LOQO-FEATURE-EXPAND` (folding the GRAV-QUAD and RADIOCONTACT features into the existing supervised quadrant-debiased LOQO ensemble) ranked first by expected-gain/cost.

- **Newest Session Research Artifact (`POISSONFLEX`, 2026-10-25):** `docs/downloads/gemsdoe92-poissonflex-poissonflex_opt-45000-20261025-54255bcc-zeros.tif` (`SHA-256 = 37b18c200e84c77b39b07e527b17d4395968389aaf3ff0c175c71204b2065f9b`, `45,000` dots via nested visible-only OOF support; strict draw-blind `d_vis > 2.0` `HOLDOUT-DTI = 0.107466 [0.094158, 0.120431]`, static `d_cat > 2.0` `HOLDOUT-DTI = 0.008824 [0.007601, 0.010081]`, off-catalogue `USGS SGMC PROXY = 0.120957` `+35.4%` over `COULOMBLOQO standalone`; `10/10 + 13/13` format gates PASS; passes all `97` local rasters `<= 0.6488` and all `<= 80k`-dot public rasters across `102` repos `<= 0.6804`, but trails `COULOMBLOQO standalone` `0.113890` and hits `0.7541 > 0.70` on `125,890`-px `62GEMSDOE ventcons` under the `150k` dot-field cap -> **`verdict: "negative"`, DO NOT SUBMIT**; `evidence/poissonflex_run_card.json`).
- **Closed Selector Investigation (`evidence/coulomb_loqo_dual_reading_selector.json`):** Re-auditing `COULOMBLOQO standalone` and `COULOMBLOQO dual45` across all `1,321` non-self public blobs (`102` repos, `0` missing blobs) under `uniqueness.dual_reading_decision` confirmed **both fail closed** (`standalone` `0.739842 > 0.70` across `8` sparse `100k–126k`-px witnesses; `dual45` `0.722420 > 0.70` across `4` witnesses). **Zero artifacts in the repository are cleared for a weekly slot.**

---

# Historical Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-24, `COULOMBDM` & `COULOMB-LOQO` Merged State)

## Prior Slot Decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT (`submission_eligible: false`, `0` weekly slots spent, `74 BUILT / 0 RECEIPT`)**

- **Current Research Download (`data-primary="true"`):** `docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif` (`SHA-256 = 44efd202e8b96b9812de4693bd7f1ed05afed28de7e2e9413f72bc139ff18b12`, static `HOLDOUT-DTI = 0.007816`, **`0 / 1,181` `<= 150k`-px sparse public overlaps `> 70%`**) and zero-label standalone sibling `docs/downloads/h33-h33-2-b2-COULOMBDMcoulomb1d-20261024-826b2fb3-zeros.tif` (`SHA-256 = 510c3012f4866e8ea2f0debd0aba799a7b7765a4e18f0954d2d1067ddd01e172`, `0% H19-5`, `0%` catalogue labels, Rule-2 `d_vis > 2.0` `HOLDOUT-DTI = 0.094496`, **`0 / 1,181` `<= 150k`-px sparse public overlaps `> 70%`, max `0.5859`**; `evidence/coulombdm_run_card.json`).
- **Repository Holdout-Best Artifact (`COULOMB-LOQO`):** `docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif` (`0.009220` static / `0.113316` LOQO `d_vis > 2.0`, `1` sparse public overlap `0.7004` at `61k` px; hybrid sibling `COULOMBLOQO dual45` `0.009107` static, `0 / 1,121` `<= 90k`-px sparse public overlaps `> 70%`):
  - **Submission Name (local ledger):** `GEMSDOE92-COULOMBLOQO-standalone-20261024`
  - **Form Note (`89 / 140` chars):** `h33-h33-2-b2; COULOMBLOQO standalone: 37654 1D LOQO Coulomb+polarity+RTP crests (0 H19-5)`
  - **SHA-256 (`-zeros.tif`):** `8f1f93d8c97b4e1c359ce5fbe07d183214e707aa6bda4ed074c00921f39ad32e`
  - **Run Card:** `evidence/coulomb_loqo_run_card.json` (`docs/downloads/coulomb_loqo_run_card.json`)
  - **Format & `[0, 1]` Gates:** **PASS (`10 / 10` `gems.gates` + `gems57.validate`) — ✅ OK TO DOWNLOAD FOR RESEARCH**
  - **Weekly Slot Verdict:** **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (`verdict: "negative"`)**

---

## Gate-by-Gate Selector Status for `COULOMBLOQO standalone` (and Hybrid Sibling `COULOMBLOQO dual45`)

| Gate | Status | Measured Value & Source |
|---|---|---|
| **1. Format & `[0, 1]` Range Gate** | **PASS** | `float32`, `EPSG:32611`, `3730 × 3292`, finite `[0, 1]`, `0` NaN anywhere, `0.0` outside footprint, `37,654` unit dots, `0` catalogue mass, `d_cat > 2.0 px` (`docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-audit.json`) |
| **2. Single-Feature Leakage Canaries (43 features)** | **PASS** | All raw bands, derived features (`f01`–`f24`), and LOQO surfaces `<= 0.90`; max symmetric AUC **`0.672638`** (`evidence/coulomb_loqo_screen.json`) |
| **3. Shared Static `HOLDOUT-DTI` (`gems57-pooled-hide-v2`)** | **PASS (#1 All-Time Repo High)** | **`0.009220 [0.007983, 0.010493]`** (`22,663` withheld px); **`+0.005214 [+0.004130, +0.006326]`** vs `R0` (`0.004006`, `+130.2%`); **`+0.003175 [+0.002123, +0.004222]`** vs `RELIEF p10` (`0.006045`, `+52.5%`); beats `HYDROCONDUIT` (`0.008549`) & `APRONRIDGE` (`0.008354`); strict draw-blind `d_cat > 2.0` = **`0.009689`** (`evidence/coulomb_loqo_proxy_audit.json`) |
| **4. Strict Rule-2 Unmasked `d_visible > 2.0` `HOLDOUT-DTI`** | **PASS (#1 All-Time Repo High)** | **`0.113316 [0.100614, 0.127163]`** vs `H19-5` skeleton `0.096757` (paired $\Delta = +0.016559$, 95% CI **`[+0.008170, +0.024980]`** — first standalone `0% H19-5` model to beat `H19-5`) |
| **5. Off-Catalogue `USGS SGMC` `PROXY` DTI (`62,703` px)** | **RECOVERED** | **`0.090569`** (`standalone`, `+22.2%` vs `HYDROCONDUIT` `0.074107`) / **`0.094057`** (`dual45`, `+26.9%` vs `HYDROCONDUIT`, `97.9%` of `R0` `0.096060`) |
| **6. Local Registry Uniqueness (41 rasters)** | **PASS** | Pre-placement surface worst 3-px overlap **`0.6164 <= 0.70`**, `|rho| = 0.1593 <= 0.90`; Final dots worst 3-px overlap **`0.6164 <= 0.70`** (`dual45`: **`0.5982`**), `|phi| = 0.0493 <= 0.90` |
| **7. Sparse Public Fleet Diagnostic (`<=90k` / `<=150k` px across 102 repos)** | **DIAGNOSTIC** | Across `1,121` `<= 90k`-px public submissions: **`COULOMBLOQO dual45` passes `0 / 1,121` (`max = 0.6488 <= 0.70`)**; `standalone` hits `0.7004` (`1` raster at `61,427` px, `15` dots above `0.7000`) and `0.7398` vs `100k`-px `GEMSDOE23` habitat (`evidence/coulomb_loqo_public_sparse_diagnostic.json`) |
| **8. Literal Public Registry Gate (`1,368` rasters incl. dense surfaces)** | **BLOCKED (STOP)** | `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` (`5,167,373` = 100% positive footprint px) forces **`1.0000 > 0.70`** forward overlap (`evidence/coulomb_loqo_public_registry_uniqueness.json`) |

---

## Human Selector Queue Once Blockers Are Resolved

1. **Blocker 1 (Operator Uniqueness Scope Decision):** Decide whether dense continuous/habitat maps (`> 90,000` positive pixels, led by `17GEMSDOE E-proba-multiscale` at `5.17M` pixels) are excluded from the sparse competition-budget uniqueness pool.
   - Under a **`<= 90,000` positive-pixel** competition-budget policy: **`COULOMBLOQO dual45`** (`0.009107` static / `0.1020` `d_vis>2` / `0.0941` `SGMC`, **`0 / 1,121` `> 70%`**) is immediately unique across all 102 public repos, followed by `HYDROCONDUIT f45hydro` (`0.008549` static, `0 / 1,179` `<= 150k`).
   - Under a **`<= 55,000` positive-pixel** budget-matched policy: **`COULOMBLOQO standalone`** (`0.009220` static / `0.113316` `d_vis>2` / `0.0906` `SGMC`, `#1` on both holdout instruments) is the top candidate.
2. **Blocker 0 (Calibration Anchor):** Record one `ORGANIZER-CONFIRMED` DrivenData receipt for parent `R0` (`0.2778` `[CLAIM]`) in `ledger/submissions.csv` before interpreting live leaderboard deltas, and never submit more than one `COULOMBLOQO` arm in a rolling 7-day window.

---

## Merged parallel-branch selector records (`COULOMB`, `APRONRIDGE`)

# SLOT_PLAN — current selector state (2026-10-24, COULOMB session): NO SLOT AUTHORIZED — research downloads only

## COULOMB session decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT (`submission_eligible: false`, `verdict: negative`)**

Three new format-valid standalone research downloads (`10/10` gates + `13/13` `gems57.validate` PASS each):
`COULOMBseismo-20261024-d243140b` (lead, `HOLDOUT-DTI 0.005808 [0.004846, 0.006809]`),
`COULOMBfree-20261024-d0cf5db5` (`0.005689`), `COULOMBopen-20261024-58a7a394` (`0.005184`).
All beat `R0` (`0.004006`) but trail the `0.008549` promotion bar with paired CIs excluding promotion
(seismo vs bar `Δ −0.002741 [−0.004137, −0.001382]`), and the lead arm trips the binding dense public
witness (`17GEMSDOE E-proba-multiscale`, `forward_overlap = 1.000`, `evidence/public_witness_coulomb.json`).
Locally unique (`0.263–0.290 ≤ 0.70`, `|φ| ≤ 0.024`); canaries `20/20 PASS`. **No slot used this session
(3/3 experiment budget consumed as research).** Promotion bar stays
`HYDROCONDUIT f45hydro 0.008549` (still the repo holdout best; parallel-session branch primary
`GEOTENSION free1d` scored `0.007615`). Run card: `docs/downloads/coulomb_run_card.json`.

---

# SLOT_PLAN — current selector state (2026-10-24, APRONRIDGE session)

## Current primary artifact: `APRONRIDGE free1d` — #1 Holdout-DTI & locally unique, blocked ONLY by dense public witness (`verdict: negative`, no slot used)

Primary download `GEMSDOE92-APRONRIDGE-free1d-20261024` (file
`docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif`,
SHA-256 `1a29a5d81e8561954f04a563b4975cb84d00898b8d7634700a9d409a10e06cbc`,
note `h33-h33-2-b2; APRONRIDGE free1d: 37654 standalone 1D piedmont-apron + RTP ridges (0 H19-5)`):

- **Format gates**: `10/10 PASS` on independent disk re-read (`EPSG:32611`, `3730×3292`, `float32`, `[0, 1]`, `0` NaN in footprint, `0.0` outside, `37,654` unit dots, `0` catalogue mass, `d_cat > 2.0 px`).
- **`HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `8` spatial folds, `22,663` withheld positives)**: **`0.008354 [0.006823, 0.010135]`** — **new all-time repository high**, beating `R0` (`0.004006`, paired Δ `+0.004347 [+0.003019, +0.005710]`), `STEPEDGE f60Sraw` (`0.003980`), prior locally-unique best `STRAINBREAK f60s2i` (`0.005487`, paired Δ `+0.002867`), and prior holdout best `RELIEF p10piedmont` (`0.006045`, paired Δ `+0.002308`). Pre-registered hybrid siblings `s60f40` (`0.008291`) and `s50f50` (`0.008097`) also beat `RELIEF p10`; never submit multiple `APRONRIDGE` siblings.
- **Leakage canaries**: `11/11 PASS` (`max symmetric AUC = 0.636490 <= 0.90`).
- **SGMC 1:500k off-catalogue `PROXY`**: `0.080098` vs `R0` `0.096060` (intentional suppression of high-range Mesozoic bedrock contacts in favor of thin-cover piedmont Quaternary accommodation zones; contrast `STEPEDGE f60Sraw` SGMC `0.141464` vs holdout `0.003980`).
- **Uniqueness**:
  - Pre-placement continuous surface vs `29` local rasters (`evidence/apronridge_surface_registry.json`): `worst_|Spearman| = 0.122173 <= 0.90`, `worst_top37654_forward_overlap = 0.552664 <= 0.70`.
  - Final dots vs all `46` cross-lane local rasters (`43` in `evidence/apronridge_proxy_audit.json` + `3` newly merged `STEPEDGE` rasters at `0.3023–0.3783`): **`worst_forward_overlap = 0.460482 <= 0.70`**, `worst_|phi| = 0.056117 <= 0.90` (`local_duplicate: false`).
  - Top public sparse witnesses (`62GEMSDOE` `120k` px, `GEMSDOE23` `91.5k–100k` px; `evidence/apronridge_public_sparse_spotcheck.json`): **`0.6028–0.6456 <= 0.70`**.
  - **Binding public dense witness (`evidence/public_witness_apronridge.json`)**: `17GEMSDOE E-proba-multiscale` (`5,167,373 / 5,167,373` positive footprint cells) forces `forward_overlap = 1.000`. Therefore `submission_eligible = false` and `verdict = "negative"`; **do not spend a weekly slot** until an operator policy decision adds a dense-probability support ceiling (`<= 150,000` positive pixels). Once that policy update is approved and a full refreshed `scripts/audit_public_registry.py` confirms sparse uniqueness, `APRONRIDGE free1d` is the #1 queued candidate for a single weekly slot.

---

# SLOT_PLAN — prior parallel state (2026-10-24, STEPEDGE session)
# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-24, `HYDROCONDUIT` Session)

## Current Slot Decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT (`submission_eligible: false`)**

Primary download `GEMSDOE92-STEPEDGE-f60Sraw-20261024` (file
`h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif`, SHA-256
`c5dc98f2846ae486e022a7bdae1840334e73c03af44c03e9867c03b6f16d07b4`) is
format-valid and literal-unique vs the local dot registry (worst
forward overlap 0.461; surface |ρ| 0.138), with the repo's best SGMC PROXY
(0.141464 vs R0 0.096060). It is **not cleared**: automated gates record
`submission_eligible: false` because HOLDOUT-DTI 0.003980 [0.003295, 0.004702]
does not beat STRAINBREAK f60 (0.005487), RELIEF p10 (0.006045), or APRONRIDGE free1d (0.008354) and paired
Δ vs R0 includes 0. Dense public-witness literal overlap 1.000 is disclosed
(ρ 0.0004; see amended dot-like scope in
`docs/HYPOTHESES_20261024_STEPEDGE.md`). Sibling doses f33/f45Sraw are
duplicates (0.760/0.711 vs same-dose BREAKLINE/SCARPPOL) and must never be
submitted; never pair doses in one week. Selector framing + receipt decision
rules: `docs/ANALYSIS_20261024_STEPEDGE.md` §4. No slot used this session.
Re-validate uniqueness at decision time — verdicts decay as the registry
grows (IRREGULARITIES 2026-10-24).

---

# SLOT_PLAN — prior selector state (2026-10-24, ANASIG session)
- **Current Primary Artifact:** `docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif`
  - **SHA-256 (`-zeros.tif`):** `c9e07ba6627672bfd58b08572a19d48aa16ff07a2f95347993550eaaccba8fdd`
  - **Run Card:** `evidence/hydroconduit_run_card.json` (`docs/downloads/hydroconduit_run_card.json`)
  - **Format & `[0, 1]` Gates:** **PASS (`10 / 10` `gems.gates` + `13 / 13` `gems57.validate`) — ✅ OK TO DOWNLOAD FOR RESEARCH**
  - **Weekly Slot Verdict:** **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (`verdict: "negative"`)**

---

## Gate-by-Gate Selector Status for `HYDROCONDUIT f45hydro`

| Gate | Status | Measured Value & Source |
|---|---|---|
| **1. Format & `[0, 1]` Range Gate** | **PASS** | `float32`, `EPSG:32611`, `3730 × 3292`, finite `[0, 1]`, `0` NaN anywhere, `0.0` outside footprint, `0` catalogue mass (`docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-audit.json`) |
| **2. Single-Feature Leakage Canaries** | **PASS** | All 24 raw/derived features `<= 0.90`; max symmetric AUC **`0.65012`** (`evidence/hydroconduit_preplacement_screen.json`) |
| **3. Shared Static `HOLDOUT-DTI` vs `R0` & `RELIEF p10`** | **PASS (New Repo Best)** | **`0.008549 [0.007626, 0.009487]`** (`gems57-pooled-hide-v2`, `22,663` withheld positives); **`+0.004543 [+0.003770, +0.005315]`** vs `R0` (`0.004006`, `+113.4%`); **`+0.002504 [+0.001795, +0.003222]`** vs `RELIEF p10` (`0.006045`, `+41.4%`) |
| **4. Local Registry Uniqueness (29 rasters)** | **PASS** | Pre-placement surface worst 3-px overlap **`0.1892 <= 0.70`**, `|rho| = 0.1098 <= 0.90`; Final dots worst 3-px overlap **`0.5500 <= 0.70`**, `|rho| = 0.2982 <= 0.90` (`evidence/hydroconduit_proxy_audit.json`) |
| **5. Sparse Public Fleet Diagnostic (`<=150k` px, 1,147 rasters across 102 repos)** | **DIAGNOSTIC PASS (`0 > 70%`)** | **Zero** sparse dot-like rasters exceed `70%`: worst `<=150k` overlap **`0.6719`**, worst `<=90k` overlap **`0.6518`**, worst `|rho|` across all `1,332` rasters **`0.3693` final / `0.4396` surface** (`evidence/hydroconduit_public_sparse_diagnostic.json`) |
| **6. Literal Public Registry Gate (incl. dense `>150k`-px surfaces)** | **BLOCKED (STOP)** | `118` dense public rasters (`>150k` positive px, led by `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` with `5,167,373` = 100% positive footprint px) give **`1.0000 > 0.70`** forward overlap (`evidence/hydroconduit_public_registry_uniqueness.json`) |
| **7. Multi-Instrument Cross-Check (`d_visible > 2.0` & `SGMC`)** | **DISCLOSED TRADE-OFF** | Rule-2 fold-by-fold `d_visible > 2.0` `HOLDOUT-DTI` = `0.0852` (vs `0.0968` `H19-5` skeleton-only); off-catalogue `USGS SGMC` `PROXY` = `0.0741` (vs `0.0961` `R0`, `0.1261` `BREAKLINE f45`) |

---

## Why No Slot Is Spent Automatically

1. **Protocol Rule 6:** Promotion to a real DrivenData weekly submission slot (`<= 3 / week`) is strictly an external human selector step. Zero weekly slots have been consumed by this repository (`ledger/submissions.csv`: `49 BUILT`, `0 ORGANIZER-CONFIRMED RECEIPT`).
2. **Human Selector Action Required Before Any Upload:**
   - **Step A (Policy Decision):** Decide whether dense continuous/semi-dense probability surfaces (`> 150,000` positive pixels, such as `17GEMSDOE E-proba-multiscale`) are outside the intended sparse dot-set uniqueness pool. Under that sparse-only (`<= 150k` px) policy, `HYDROCONDUIT f45hydro` is **unique across all 102 public `GEMSDOE` repositories (`0 / 1,147` over `70%`)** AND **#1 on the shared static holdout (`0.008549`)**. Under the current literal rule, it remains blocked (`submission_eligible: false`).
   - **Step B (Calibration Anchor):** `Blocker 0` remains zero `ORGANIZER-CONFIRMED` receipts in `ledger/submissions.csv`. Obtaining or verifying one receipt for `R0` (`0.2778` `[CLAIM]`) anchors whether DrivenData's hidden test set rewards Quaternary piedmont/hydrothermal scarps (`HYDROCONDUIT`, `+113.4%` static `HOLDOUT-DTI`) vs mountain-core bedrock faults (`BREAKLINE`, `+31.3%` `SGMC`).

### Parallel-Session Benchmark Update (`PIEDFRONT` + `STEPEDGE` + `review_20261024`)
- **`PIEDFRONT f35Ptop`** (`GEMSDOE92-PIEDFRONT-f35Ptop-20261024`, `docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif`, SHA-256 `e314f4c004927ff56334827b4d45c57fc62da3da3010c12682d7cce6d0f185a8`): static `HOLDOUT-DTI = 0.006425 [0.005375, 0.007479]`, `SGMC = 0.059993`, `verdict: negative` (**OK TO DOWNLOAD**, **DO NOT SUBMIT**). `HYDROCONDUIT f45hydro` (`0.008549 [0.007626, 0.009487]`) improves over `PIEDFRONT f35Ptop` by `+33.1%` (`+0.002124`) while overlapping only `56.56% <= 70%` within 3 px (`phi = 0.2000`).
- **`STEPEDGE f60Sraw`** (`GEMSDOE92-STEPEDGE-f60Sraw-20261024`, `docs/downloads/h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif`, SHA-256 `c5dc98f2846ae486e022a7bdae1840334e73c03af44c03e9867c03b6f16d07b4`): static `HOLDOUT-DTI = 0.003980 [0.003295, 0.004702]`, repo-best `SGMC = 0.141464`, `verdict: negative` (`42.35% <= 70%` 3-px overlap with `HYDROCONDUIT f45hydro`).
- Ledger total across all merged sessions: `54 BUILT / 0 RECEIPT`.
