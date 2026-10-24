# Current review — APRONRIDGE site primary (2026-10-24; with HYDROCONDUIT comparison)

## Latest repository review update (2026-10-24 UTC)

- **No new experiment or GeoTIFF was generated.** The requested unique fresh candidate remains unfulfilled, not silently replaced with an inherited raster. Under the unchanged literal registry protocol, the verified public witness is positive at every valid footprint cell; thus any nonempty in-footprint candidate's final dots have 100% forward overlap with that witness and must stop. This is a protocol-level stop, not evidence of geologic similarity. No weekly slot was used.
- **Documentation defect corrected:** the Pages homepage and guides identify APRONRIDGE free1d as the current site-primary research download, but its `HOLDOUT-DTI` (`0.008354 [0.006823, 0.010135]`) is lower than the documented HYDROCONDUIT hybrid (`0.008549 [0.007626, 0.009487]`) on the same evaluator / 22,663 withheld positives. APRONRIDGE is now described as a standalone physics-first result, not the overall repository holdout maximum. Both values are **HOLDOUT-DTI**, not competition scores. The 0.2778 GEMSDOE32 number remains a `CLAIM` absent an organizer receipt; leaderboard values 0.3195 and 0.4413 remain conflicting snapshots not refreshed here.
- **Hypotheses and experiment budget:** the existing ranked queue in [`REVIEW_20261024_SESSION.md`](REVIEW_20261024_SESSION.md) remains conditional. No new lane was ranked as viable and no holdout was run because the binding registry stop makes a nonempty unique placement impossible under the current rule; the training feature stack is not staged in the tracked checkout. There is no defensible projected score.
- **Three-pass review:** Pass 1 found stale README primary naming, an incorrect overall `HOLDOUT-DTI`-winner claim, and a submission-note character-count error. Pass 2 corrected the summary across README / homepage / hypothesis and review pages and added a regression test for primary/ranking consistency. Pass 3 rechecked the guides, exact primary link/hash references, explicit download-vs-slot status, and preserved the registry stop; no TIFF or holdout data were altered.
- **Validation in this review:** 200 tests passed (103 nonfatal Rasterio/Affine warnings); `scripts/check_site.py` passed all 25 served zeros-outside TIFs; a local-link audit found 163 links across the four primary HTML pages with no missing local targets; `compileall` and `git diff --check` passed. These are software and file-format checks only; they do not grant uniqueness clearance or slot eligibility.

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
