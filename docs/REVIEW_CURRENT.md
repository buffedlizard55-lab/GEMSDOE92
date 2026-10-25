# Current review — 2026-10-25 (`BLINDFAULT`)

**✅ OK TO DOWNLOAD FOR RESEARCH; ⛔ DO NOT SUBMIT** (`verdict: negative`, fails the pre-registered holdout gate; submission_eligible=false). The newly generated artifact and current run card are linked in the [three-pass closeout review](REVIEW_20261025_BLINDFAULT_CLOSEOUT.md). Primary **HOLDOUT-DTI** is `0.047896 [0.038079, 0.057970]` (`gems57-pooled-hide-v2`, 22,663 withheld positives, strict draw-blind `d_visible > 2.0`), below the recorded repository holdout-best `0.113316`. The run card reports dual registry measurements: matched-budget worst overlap `0.5219`, literal worst `1.000`, worst absolute correlation `0.3402`; literal result is not omitted. These do not establish organizer acceptance or a competition score.

The current session used 3/3 experiments and 0 weekly slots. The prior `1F514FFC` review below is historical, not current. The current result is documented in [`ANALYSIS_20261025_BLINDFAULT.md`](ANALYSIS_20261025_BLINDFAULT.md), [`downloads/blindfault_run_card.json`](downloads/blindfault_run_card.json), and [`NEXT_STEPS.md`](NEXT_STEPS.md).
## Archived session — 2026-10-25 (1f514ffc)

See [historical three-pass review](REVIEW_1F514FFC.md) and [run card](downloads/review_1f514ffc_run_card.json). Its “no new TIFF” and then-current test counts describe that earlier checkpoint only; the newer BLINDFAULT closeout above supersedes it as the current status.

---

# Current Repository & Gate Review — `GEMSDOE92` (`2026-10-24`, `COULOMBDM s45coulomb55` Current Download; `EULERFUSE` Parallel Closeout)

**OK TO DOWNLOAD FOR RESEARCH; DO NOT SUBMIT.** Subsequent to [session 918b947a](REVIEW_918B947A.md) ([run card](downloads/review_918b947a_run_card.json)), merged sessions generated unique `COULOMBDM` and `XPHASE` research TIFFs. The universal dense-witness overlap stop still bars weekly-slot clearance. No current organizer score is claimed.

---

## 0A. Current research download (`COULOMBDM`)

- **Research GeoTIFF:** `docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif` (standalone zero-label sibling: `docs/downloads/h33-h33-2-b2-COULOMBDMcoulomb1d-20261024-826b2fb3-zeros.tif`)
  - **SHA-256:** `44efd202e8b96b9812de4693bd7f1ed05afed28de7e2e9413f72bc139ff18b12` (`coulomb1d`: `510c3012f4866e8ea2f0debd0aba799a7b7765a4e18f0954d2d1067ddd01e172`)
  - **Name / note:** `GEMSDOE92-COULOMBDM-s45coulomb55-20261024` / `h33-h33-2-b2; COULOMBDM s45coulomb55: 16944 Coulomb-H19 + 20710 off-skel 1D Coulomb/RTP/clay ridges (>3px H19-5)`
  - **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives): static `0.007816 [0.006994, 0.008644]` (`+95.1%` vs `R0`); zero-label standalone `coulomb1d` Rule-2 fold-visible `d_vis > 2.0` **`0.094496 [0.085916, 0.102867]`** (below supervised LOQO repository holdout-best `COULOMB-LOQO standalone` `0.009220` static / `0.113316` LOQO `d_vis > 2.0`).
  - **Download:** ✅ OK TO DOWNLOAD FOR RESEARCH (11/11 format gates; `0 / 58` local and `0 / 1,181` sparse `<=150k` public overlaps `>70%`). **Weekly slot:** ⛔ DO NOT SUBMIT (`verdict: negative`, dense witness overlap 1.000).
  - Run card: `evidence/coulombdm_run_card.json`. Analysis: `docs/ANALYSIS_20261024_COULOMBDM.md`. Hypotheses: `docs/HYPOTHESES_20261024_COULOMBDM.md`.

## 0B. Parallel session (`XPHASE`)

- **Research GeoTIFF:** `docs/downloads/h33-h33-2-b2-XPHASEdual40-20261024-643553cf-zeros.tif`
  - **SHA-256:** `080018382de33758c78e1b11f80098a1f736ac7de5f4c55641bd84b52b0f7200`
  - **Name / note:** `GEMSDOE92-XPHASE-dual40-20261024` / `h33-h33-2-b2; XPHASE dual40: 15062 H19-5 + 22592 far MT-grav phase crests`
  - **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives): **`0.004653 [0.003955, 0.005390]`** vs R0 `0.004006` (paired Δ CI includes 0). Below holdout-best `COULOMB-LOQO` `0.009220`.
  - **Download:** ✅ OK TO DOWNLOAD FOR RESEARCH (10/10 format gates). **Weekly slot:** ⛔ DO NOT SUBMIT (`verdict: negative`, dense witness overlap 1.000).
  - Run card: `evidence/xphase_run_card.json`. Analysis: `docs/ANALYSIS_20261024_XPHASE.md`. Hypotheses: `docs/HYPOTHESES_20261024_XPHASE.md`.

## 0C. Parallel completed lane (`EULERFUSE`)

- **Research GeoTIFF:** `docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif`
  - **SHA-256:** `5820e882512843a334f4497ed7f294af937339f729e4eeeecdc33d9cdafeeab9`; pre-publication exact SHA matches: `0` among 1,378 exact-grid public rasters.
  - **Name / note:** `GEMSDOE92-EULERFUSE-gravity-20261024` / `EULERFUSE gravity: 37654 LOQO Euler-contact dots; HOLDOUT-DTI 0.110387; negative` (80/140 characters).
  - **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives): strict draw-blind `0.110387 [0.097279,0.123179]`, below fresh base `0.113316 [0.101071,0.126266]`; paired delta `-0.002929 [-0.006700,0.000763]`.
  - **Download:** ✅ OK TO DOWNLOAD FOR RESEARCH (`11/11` format gates, finite `[0,1]`). **Weekly slot:** ⛔ DO NOT SUBMIT (`verdict: negative`; `submission_eligible=false`; literal public overlap `1.000`; 3/3 experiments and 0 weekly slots).
  - Run card: `evidence/eulerfuse_run_card.json`. Analysis: `docs/ANALYSIS_20261024_EULERFUSE.md`. Hypotheses: `docs/HYPOTHESES_20261024_EULERFUSE.md`.

### EULERFUSE cumulative passes

1. **Implementation / verification:** froze four hypotheses before code, reused the pinned stack/shared evaluator/shared writer, tested 36 canaries, executed exactly three arms, independently reopened the emitted TIF, and ran local plus current-public representation checks.
2. **Bug / edge review:** fixed batched solve RHS dimensions, changed the large design matrix to a memory map after an OOM, added shape/residual-scale guards, retained main's hardened explicit-primary site validator, embedded the exact validator receipt in the run card, and pinned exact SHA/one-file ZIP contracts.
3. **Requirement recheck:** applied the user's literal dense-raster rule without exemption, synchronized all public guides, labeled every numeric outcome, recorded source-access limitations, and preserved format validity separately from eligibility. Combined post-merge verification: `278 passed` (124 non-failing Rasterio deprecation warnings), `git diff --check` PASS, and site gate PASS across all `43` served rasters.

## 1. Prior Active Primary & Automated Gate Status (`COULOMB-LOQO`, still repository holdout-best)

- **Primary Served GeoTIFF:** `docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif`
  - **SHA-256 (`-zeros.tif`):** `8f1f93d8c97b4e1c359ce5fbe07d183214e707aa6bda4ed074c00921f39ad32e`
  - **ZIP (`-zeros.zip`):** `docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.zip` (`448395137acb4860c24402fb53002539f3c688f8c232c79c23991353623c4c48`)
  - **Unique Submission Name (local ledger):** `GEMSDOE92-COULOMBLOQO-standalone-20261024`
  - **Submission Form Note (`89 / 140` chars):** `h33-h33-2-b2; COULOMBLOQO standalone: 37654 1D LOQO Coulomb+polarity+RTP crests (0 H19-5)`
  - **Protocol Rule 5 Run Card:** `evidence/coulomb_loqo_run_card.json` (`docs/downloads/coulomb_loqo_run_card.json`)
- **Two-Question Automated Decision:**
  1. **Download Gate:** **✅ OK TO DOWNLOAD FOR RESEARCH** (`10/10` `gems.gates` + `gems57.validate` + `scripts/check_site.py` PASS; `EPSG:32611`, `3730 × 3292`, `float32`, finite `[0.0, 1.0]`, `0.0` outside footprint, `0` NaN anywhere, `37,654` unit dots, `0` catalogue mass, `d_cat > 2.0 px`).
  2. **Weekly Slot Gate:** **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT** (`submission_eligible: false`, `verdict: "negative"`, `0` weekly slots used) under the literal Rule-1 public scan (`1.000` forward overlap vs dense `17GEMSDOE E-proba-multiscale`, `5,167,373` positive footprint cells).

## 2. Summary of Verified Evidence Across All Instruments

- **Static `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` withheld positives):** **`0.009220 [0.007983, 0.010493]`** (#1 all-time repository high; strict draw-blind `d_cat > 2.0` = `0.009689`; beats `HYDROCONDUIT` `0.008549`, `APRONRIDGE` `0.008354`, `PIEDFRONT` `0.006425`, `RELIEF p10` `0.006045`, `STRAINBREAK` `0.005487`, `R0` `0.004006`).
- **Strict Rule-2 Unmasked `d_visible > 2.0` `HOLDOUT-DTI`:** **`0.113316 [0.100614, 0.127163]`** vs `H19-5` `0.096757` (paired 95% CI `[+0.008170, +0.024980]` — first standalone `0% H19-5` model in repo history to beat `H19-5`).
- **Off-Catalogue `USGS SGMC` `PROXY` DTI (`62,703` px):** **`0.090569`** (`standalone`, `+22.2%` over `HYDROCONDUIT` `0.074107`) / **`0.094057`** (`dual45`, `+26.9%` over `HYDROCONDUIT`).
- **Single-Feature Leakage Canaries (`43` raw/derived/LOQO features):** **PASS** (`max symmetric AUC = 0.672638 <= 0.90`).
- **Registry Uniqueness (`REGISTRY-MEASUREMENT`):**
  - Local `GEMSDOE92` (`41` cross-lane rasters): **PASS** (`worst 3-px overlap = 0.6164 <= 0.70`, `|phi| = 0.0493 <= 0.90`).
  - Live 102-repo public scan (`1,368` template rasters): literal STOP (`1.0` vs `17GEMSDOE E-proba-multiscale`); sparse `<= 90k`-px diagnostic (`1,121` rasters): `dual45` **`0 / 1,121` (`max = 0.6488`)**, `standalone` `0.7004` (`1` raster at `61,427` px).

---

## Merged parallel-branch review records (`D97`, `CONTINUATION`, `GEOTENSION`, `COULOMB`, `APRONRIDGE`)

# Current review — updated after main-branch COULOMB closeout (2026-10-24)

## Latest safety decision

**✅ OK TO DOWNLOAD FOR RESEARCH; ⛔ DO NOT SUBMIT.** APRONRIDGE remains the site research download, not a selector choice. The D97 review's caution stands: APRONRIDGE and HYDROCONDUIT HOLDOUT-DTI numbers are stored historical static evaluations, not freshly rerun or certified here as fold-rebuilt/leak-free promotion evidence and not organizer scores. The D97 and continuation exact-file checks each reject against a single Git-blob-verified witness; neither is a fresh exhaustive registry scan or candidate-surface clearance. That witness is positive across all `5,167,373` footprint cells, so every nonempty in-footprint prediction has literal forward overlap `1.0`; no dense-map exemption is authorized.

## Later main-branch research records (not selector decisions)

- **APRONRIDGE free1d / HYDROCONDUIT f45hydro:** historical **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives) `0.008354 [0.006823, 0.010135]` / `0.008549 [0.007626, 0.009487]`; the hybrid is higher by point estimate. Preserve the D97 and continuation caveat above.
- **GEOTENSION free1d:** a separate later main-branch experiment records **HOLDOUT-DTI** `0.007615 [0.005832, 0.009386]` with the same evaluator and withheld-positive count. It is below both APRONRIDGE and HYDROCONDUIT; its exact-file witness overlap is `1.0`, so it is a negative, research-only artifact.
- **COULOMB seismo:** the later main-branch session tested three variants. Lead **HOLDOUT-DTI** `0.005808 [0.004846, 0.006809]` (`gems57-pooled-hide-v2`, 22,663 withheld positives); it beats R0 but trails HYDROCONDUIT, has lower SGMC proxy, and is still blocked by the same witness (`1.0`). It is format-valid/local-unique, not submission-cleared. The three-experiment budget for that session was consumed; no weekly slot was used.
- The four conditional hypotheses in [`HYPOTHESES_20261024_PREFLIGHT.md`](HYPOTHESES_20261024_PREFLIGHT.md) remain unvalidated and are not cleared to build or score. The separate ranked COULOMB proposals and experiment results are in [`HYPOTHESES_20261024_COULOMB.md`](HYPOTHESES_20261024_COULOMB.md) and [`ANALYSIS_20261024_COULOMB.md`](ANALYSIS_20261024_COULOMB.md).

## Review records and evidence

[D97 three-pass review](REVIEW_D97F969E.md) · [D97 run card](downloads/review_d97f969e_run_card.json) · [D97 witness receipt](downloads/review_d97f969e_witness.json) · [continuation review](REVIEW_20261024_CONTINUATION.md) · [GEOTENSION analysis/run card](ANALYSIS_20261025_GEOTENSION.md) / [`../evidence/geotension_run_card.json`](../evidence/geotension_run_card.json) · [COULOMB analysis/run card](ANALYSIS_20261024_COULOMB.md) / [served run card](downloads/coulomb_run_card.json) · [COULOMB witness receipt](downloads/public_witness_coulomb.json).

No artifact from these later main-branch sessions is promoted to a competition submission by this review. Download validity, local HOLDOUT-DTI, local uniqueness, and organizer confirmation remain distinct.

---

# Historical APRONRIDGE review (read the latest status above first)

> **OK TO DOWNLOAD FOR RESEARCH; DO NOT SUBMIT.** The existing APRONRIDGE TIF remains the research download; it is not a newly generated candidate or a selector choice. The latest exact-file witness test is a **single-witness rejection**, not a new full-registry scan or pre-placement candidate-surface evaluation. APRONRIDGE and HYDROCONDUIT HOLDOUT-DTI figures below are historical static evaluation results and are not certified here as fold-rebuilt, leak-free promotion evidence. No dense-map exemption or submission selection is authorized. Details: [three-pass review](REVIEW_D97F969E.md), [witness receipt](downloads/review_d97f969e_witness.json), [run card](downloads/review_d97f969e_run_card.json).

## Documentation review performed in this session

- **No new experiment or GeoTIFF was generated.** The requested fresh unique candidate remains unfulfilled; the full-footprint witness mathematically forces `100%` final-dot overlap for every nonempty in-footprint raster under the literal rule. That is a protocol-level stop, not evidence of geologic similarity. No weekly slot was used.
- **Ranking correction:** the stored APRONRIDGE `HOLDOUT-DTI` is `0.008354 [0.006823, 0.010135]`, lower in point estimate than HYDROCONDUIT `0.008549 [0.007626, 0.009487]` on the same evaluator / 22,663 withheld positives. Both remain historical static evaluations; no paired significance or fold-rebuilt validation is newly claimed. The 0.2778 GEMSDOE32 value remains a `CLAIM`; the supplied 0.3195 and 0.4413 leaderboard values were not refreshed.
- **Hypotheses and limits:** four concepts are in [`HYPOTHESES_20261024_PREFLIGHT.md`](HYPOTHESES_20261024_PREFLIGHT.md), unvalidated and conditional on policy resolution and restoring the absent feature stack. No candidate was implemented or scored, and no projected score is offered.
- **Three-pass review:** Pass 1 found README/site primary and ranking drift plus a form-note length error. Pass 2 corrected current-facing summaries and added consistency checks. Pass 3 rechecked the stop status, guides, primary hashes, tests, and site gates; no TIFF bytes were changed.
- **Post-resolution local validation:** 216 tests passed (103 nonfatal Rasterio/Affine warnings); the site gate passed all 31 served zeros-outside TIFs. The 8-entry input manifest, pinned R0 parent, and 63-row ledger checks passed; local HTML link audit found no missing targets. These establish format/software integrity only, not eligibility.

---

# Historical APRONRIDGE review (read the latest override above first)

> Latest continuation: [fresh exact-file witness recheck, ranked untested hypotheses, current download/submission decision, and three-pass review](REVIEW_20261024_CONTINUATION.md) · [machine-readable run card](downloads/review_20261024_continuation_run_card.json). This follow-up is another **single-witness rejection only**, not a full-registry scan or candidate-surface evaluation; its historical HOLDOUT-DTI references are not rerun or certified as fold-rebuilt/leak-free promotion evidence.
>
> Subsequent main-branch research added three GEOTENSION variants. The free1d **HOLDOUT-DTI** is `0.007615 [0.005832, 0.009386]` (`gems57-pooled-hide-v2`, 22,663 withheld positives), lower than both APRONRIDGE and HYDROCONDUIT. It is format-valid and locally unique but has `1.0` overlap with the same full-footprint-positive dense witness (`submission_eligible: false`); it is an additional research artifact, not a selector choice or organizer result. See [analysis](ANALYSIS_20261025_GEOTENSION.md) and [run card](../evidence/geotension_run_card.json).

## Download status comes first

**✅ OK TO DOWNLOAD for research; ⛔ NOT CLEARED FOR A WEEKLY SLOT (`verdict: negative`, `submission_eligible: false`).**
The current primary artifact [`h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif`](downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif)
was generated and validated in the `2026-10-24` `APRONRIDGE` session:
- **10/10 automated format gates PASS** on independent disk re-read (`EPSG:32611`, `3730×3292`, `float32`, finite `[0, 1]`, `0` NaN in footprint, `0.0` outside, `37,654` unit dots, `0` catalogue mass, `d_cat > 2.0 px`).
- **Standalone physics-first `HOLDOUT-DTI`**: **`0.008354 [0.006823, 0.010135]`** on `gems57-pooled-hide-v2` (`22,663` withheld positive pixels across 8 buffered folds). The higher documented result is the parallel `HYDROCONDUIT` hybrid: **`0.008549 [0.007626, 0.009487]`** (same evaluator / withheld count). APRONRIDGE beats `RELIEF p10` (`0.006045`) by **`+38.2%`**, `STRAINBREAK f60s2i` (`0.005487`) by **`+52.2%`**, and `R0` (`0.004006`) by **`+108.5%`** (paired Δ `+0.004347 [+0.003019, +0.005710]`), with zero `H19-5` or `R0` input.
- **Locally Unique (`local_duplicate: false`)**: Pre-placement continuous surface `worst_|Spearman| = 0.122173 <= 0.90`, `worst_top37654_forward_overlap = 0.552664 <= 0.70` (`29` rasters); final dots **`worst_forward_overlap = 0.460482 <= 0.70`**, `worst_|phi| = 0.056117 <= 0.90` (`43` cross-lane rasters); diagnostic spot-check against top sparse public witnesses (`62GEMSDOE` `120k` px, `GEMSDOE23` `91.5k–100k` px) also passes (`0.6028–0.6456 <= 0.70`).
- **Sole Remaining Slot Blocker (Binding Public Dense Witness)**: Direct measurement on `APRONRIDGEfree1d` bytes against Git-blob-verified `buffedlizard55-lab/17GEMSDOE` `17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` (`git_blob_sha = 374c88b1da2b803e2ed160de467fd71ae114010d`, positive on `5,167,373 / 5,167,373` footprint cells) gives `forward_overlap = 1.000` ([witness receipt](downloads/public_witness_apronridge.json), [run card](downloads/apronridge_run_card.json), [PhD analysis](ANALYSIS_20261024_APRONRIDGE.md)). Under the literal unweighted rule, `submission_eligible` stays `false` until an operator policy update excludes dense continuous probability maps (`> 150,000` positive pixels).

---

# Earlier closeout note — BREAKLINE witness check (2026-10-24)
# Archived parallel-session review — `HYDROCONDUIT` (2026-10-24; superseded as site primary by APRONRIDGE)

## Headline Decision

- **Historical HYDROCONDUIT artifact (parallel candidate; not current site primary):** `docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif`
  - **SHA-256 (`-zeros.tif`):** `c9e07ba6627672bfd58b08572a19d48aa16ff07a2f95347993550eaaccba8fdd`
  - **Download Clearance:** **✅ FORMAT-VALID — OK TO DOWNLOAD FOR RESEARCH** (`10 / 10` `gems.gates` + `13 / 13` `gems57.validate` checks pass; finite `[0, 1]`, zero NaNs anywhere, zeros outside footprint, zero catalogue mass, `37,654` unit-mass dots).
  - **Submission / Slot Clearance:** **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (`verdict: "negative"`, `submission_eligible: false`; DUPLICATE UNDER THE LITERAL REGISTRY RULE).**

---

## Summary of What Changed in This Session

1. **Resolved Both Open Structural Bottlenecks on the Local Holdout & Sparse Fleet:**
   - Prior off-skeleton lanes (`BREAKLINE`, `SCARPPOL`, `ANASIG`, `STRAINBREAK`, `SPRINGALIGN`) either failed to beat `RELIEF p10` (`0.006045`) on the shared `gems57-pooled-hide-v2` static holdout (`max = 0.005487` on `STRAINBREAK f60`) or exceeded `70%` forward overlap against large (`91k–120k` px) sparse rasters in the public fleet (`STRAINBREAK f60 = 0.7105`).
   - By normalizing slope breaks (`||grad log(slope + 1°)||` × 600 m cross-strike step monotonicity $\mu_{\text{step}}$), shifting off-skeleton dots from bare range-core cliffs (`74.8% -> 6.2%`) onto piedmont/shallow-basement scarps (`18.2% -> 83.4%`), repacking `H19-5` piedmont strands (`55%`), and adding the true `Band 2 RTP` tilt/demagnetization + `GeoDAWN K/Th` + `Band 17` MT + `GDR #1391` blind chemical geothermometer (`>= 80 °C`) conduit factor, **`HYDROCONDUIT f45hydro` achieved:**
     - **Static `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` withheld positives):** **`0.008549 [0.007626, 0.009487]`** — **`+113.4%` over `R0` (`0.004006`)** and **`+41.4%` over `RELIEF p10` (`0.006045`)** (`Δ = +0.002504 [+0.001795, +0.003222]`).
     - **Single-feature leakage canaries:** all 24 features `<= 0.90` (`max = 0.65012`).
     - **Local registry uniqueness (`29` rasters):** pre-placement surface `0.1892 <= 0.70` (`|rho| = 0.1098`); final dots `0.5500 <= 0.70` (`|rho| = 0.2982`).
     - **Sparse public fleet diagnostic (`1,147` rasters `<= 150k` px across all `102` public `GEMSDOE` repos):** **`0` rasters over `70%`** (`max = 0.6719 <= 0.70`; `<= 90k` max `= 0.6518 <= 0.70`).

2. **Why the Literal Public Gate Still Stops Promotion (`submission_eligible: false`):**
   - Full live GitHub API scan (`evidence/hydroconduit_public_registry_uniqueness.json`, `102` repos, `1,338` unique Git blobs verified, `1,332` compatible single-band rasters compared on **both** continuous pre-placement surface and final dots) confirms that `118` dense rasters (`> 150,000` positive pixels, led by `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` with `5,167,373` = 100% positive footprint cells) produce `1.0000 > 0.70` forward 3-px overlap under the literal Rule-1 definition (`support = (theirs > 0) & footprint`, no representation exemption).
   - Under the repository's fail-closed governance (`scripts/check_site.py`, `tests/test_site_contract.py`), only a human operator policy change can exempt dense probability surfaces (`> 150k` positive cells).

3. **Transparent Multi-Instrument Disclosure:**
   - **Rule-2 Fold-by-Fold `d_visible > 2.0` Diagnostic:** `0.085221 [0.075098, 0.094963]` for `HYDROCONDUIT f45hydro` vs `0.096757 [0.087402, 0.106214]` for `100% H19-5` skeleton-only (`d_visible > 2.0`), proving that static `d_full_cat > 2.0` self-masks withheld faults within `<= 200 m` and that moving `45%` of mass `> 300 m` off `H19-5` trades `H19-5` spine density for lane uniqueness.
   - **Off-Catalogue `USGS SGMC` Proxy (`62,703` px):** `0.074107` (`f45hydro`, `+0.00080` over `f45pied` `0.073312`) vs `0.096060` (`R0`) and `0.126105` (`BREAKLINE f45`), reflecting the deliberate suppression of bare mountain range-core bedrock cliffs (`74.8% -> 6.2%`).

See full methodology and tables in [`ANALYSIS_20261024_HYDROCONDUIT.md`](ANALYSIS_20261024_HYDROCONDUIT.md) and [`HYPOTHESES_20261024_HYDROCONDUIT.md`](HYPOTHESES_20261024_HYDROCONDUIT.md).

### Parallel-Session Benchmark Update (`PIEDFRONT` + `STEPEDGE` + `review_20261024`)
- **`PIEDFRONT f35Ptop`** (`GEMSDOE92-PIEDFRONT-f35Ptop-20261024`, `docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif`, SHA-256 `e314f4c004927ff56334827b4d45c57fc62da3da3010c12682d7cce6d0f185a8`): static `HOLDOUT-DTI = 0.006425 [0.005375, 0.007479]`, `SGMC = 0.059993`, `verdict: negative` (**OK TO DOWNLOAD**, **DO NOT SUBMIT**). `HYDROCONDUIT f45hydro` (`0.008549 [0.007626, 0.009487]`) improves over `PIEDFRONT f35Ptop` by `+33.1%` (`+0.002124`) while overlapping only `56.56% <= 70%` within 3 px (`phi = 0.2000`).
- **`STEPEDGE f60Sraw`** (`GEMSDOE92-STEPEDGE-f60Sraw-20261024`, `docs/downloads/h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif`, SHA-256 `c5dc98f2846ae486e022a7bdae1840334e73c03af44c03e9867c03b6f16d07b4`): static `HOLDOUT-DTI = 0.003980 [0.003295, 0.004702]`, repo-best `SGMC = 0.141464`, `verdict: negative` (`42.35% <= 70%` 3-px overlap with `HYDROCONDUIT f45hydro`).
- Ledger total across all merged sessions: `54 BUILT / 0 RECEIPT`.
