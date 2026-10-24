# Current Review Status — `GEMSDOE92` (`HYDROCONDUIT` Session, 2026-10-24)

## Headline Decision

- **Current Primary Artifact:** `docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif`
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
