# Standing brief — GEMSDOE92, 2026-10-28

**Status: DO NOT SUBMIT. No weekly slot spent. No focus-site file is unique under the full-registry PI-1 rule.**

Read first: [stored prompt (reconstructed, verbatim pending)](STANDING_PROMPT.md) · [nine-site executive summary](executive-summary-nine-sites-20261028.html) · [Pages home](../index.html)

## 1. Bottom line
- **Unique + format-valid download (only file that passes among the 14 audited candidates):** `docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif` (SHA-256 `d168c7d2…e5d7`). Full-registry PI-1 **PASS** (worst 3-px overlap 0.6556, limit 0.70). Holdout **below R0** (HOLDOUT-DTI 0.037987 vs 0.097750, gems57 pooled, repo record). Not a slot candidate.
- **Highest MODEL estimate in the repo (TIPCOMP, 8f27b9d6; MODEL 0.3485, not a score): NOT unique.** Full-registry worst 3-px overlap **0.9180** vs GEMSDOE22 (null lift 0.384). Earlier "unique" claim used a 165-raster local scope and is superseded. Its holdout is a tie with R0 (E2 0.09617 vs 0.09775).
- **Blindcorridor** (added to `main`; mechanism differs from R0): fails full-registry PI-1 at 0.7691. Not unique.
- **Nine focus sites:** every best peak is byte-identical to files in 2–18 other repos. Pairwise 3-px overlap among the nine is 0.87–1.00 (null 0.15–0.19). See the nine-site page.
- **Leaderboard conflict (flag):** prompt cites 0.4413 (current high), 0.3195 ("highest right now") and 0.2778 (GEMSDOE32). None is ORGANIZER-CONFIRMED.

## 2. Full-registry PI-1 results (2,216 SHA-256; candidate's own-repo copy excluded)
Source: `evidence/full_registry_summary_20261028.json`, run card `evidence/run_card_E-UNIQ-20261028-A.json`.

| Candidate | Dots | Worst 3-px overlap (repo) | Halo at worst | Null lift | |ρ| | PI-1 |
|---|---|---|---|---|---|---|
| RIESZ-LOCKED `rieszlbm2` 79041788 | 50,000 | 0.6556 (GEMSDOE67) | 0.548 | 0.107 | 0.162 | **PASS** |
| LBMC1 89a660f6 (e928d3c3) | 35,801 | 0.6845 (13GEMSDOE) | 0.680 | 0.005 | 0.147 | PASS — previously uploaded (2026-10-27 per SLOT_PLAN), not new |
| TIPCOMP 8f27b9d6 | 40,000 | **0.9180** (GEMSDOE22) | 0.534 | 0.384 | 0.162 | **FAIL** |
| Damage-zone close-dots | 30,000 | 1.000 (5 repos, identical) | — | — | 0.233 | FAIL |
| Blindcorridor 11f8999c (added to `main` by a merged PR) | 37,654 | 0.7691 (13GEMSDOE); compared 2,217 SHA (see IR-1028C-6) | 0.680 | 0.089 | 0.187 | FAIL |
| R0 parent (GEMSDOE32 peak) | 37,654 | 1.000 (identical in GEMSDOE22 et al.) | — | — | 1.000 | FAIL |
| Nine focus peaks (24, 25, 27, 28, 30, 31, 32, 33, 36) | 37k–61k | 1.000 (identical copies) | — | — | 1.000 | FAIL (all nine) |

Method notes: self-exclusion applies only when every copy is in the candidate's own repo. Non-finite cells are treated as no dot. Every finite value must lie in [0,1]. The earlier 1.0 self-match was a bug, fixed by the own-repo rule.

## 3. Gates (this session, venv `/home/user/.venv_gems`)
- `make test`: 791 passed, 19 skipped.
- `make manifest`: RESULT OK. `scripts/check_site.py`: SITE CHECK PASS (127 served rasters gated; primary RIESZ, verdict negative).
- RIESZ download, re-verified here: 1 band, float32, EPSG:32611, 3730×3292 with a transform equal to the sample's (100 m), values {0,1}, 0 NaN, 50,000 positives, SHA-256 d168c7d2…e5d7 matches. The 11/11 gate count is from SUBMISSION_READY.md and was not re-run here.

## 4. Root cause of "Predicted values must be in range [0, 1]" — probable, not confirmed
- The NaN-outside sample file (`sample_submission.tif`: 7,111,787 NaN cells) fails a naive range check `(a>=0)&(a<=1)` (returns False for NaN). Zeros-outside files pass it.
- The served zeros-outside files pass the check. Repo practice (zeros outside) avoids the error under this model.
- **Conflict (flag):** claimed scores exist for `-nan` files (e.g., GEMSDOE28 0.2710, GEMSDOE31 0.2708), which would imply the portal accepted NaN outside. Either the claims are unverified, or the portal treats NaN differently by file. Only a portal receipt can settle this, and no DrivenData login is used.
- The problem page says "null or nan" outside bounds. This matches the NaN-tolerant reading but not the naive check.

## 5. Flags and irregularities (verbatim IDs kept)
- IR-0127-6: local sample has 60,988 positives; problem page says the sample predicts total fault absence. Owner mirror, not organizer-confirmed.
- IR-1028B-4 / IR-1028C-1: TIPCOMP "OK TO DOWNLOAD" label withdrawn; PI-1 full-registry FAIL.
- IR-1028C-2: LBMC1 is a previously uploaded file and must not be re-offered as new.
- IR-1028C-3: SLOT_PLAN says RIESZ is "cleared for human selector"; SUBMISSION_READY, check_site and the holdout comparison say negative. Unresolved.
- IR-1028C-4: all nine focus peaks duplicate files in other repos; nine-site pairwise 0.87–1.00.
- IR-1028C-5: NaN-outside vs zeros-outside conflict (section 4).
- IR-1028C-6: `main` added the blindcorridor raster after `.cache/registry_v3/inventory.json` was built. Its audit compared 2,217 SHA (others 2,216). It FAILS at 0.7691 vs 13GEMSDOE, so the verdict is unaffected. Rebuild the inventory before the next audit.
- **Override (this PR):** `main`'s blindcorridor pages called the file the "GEMSDOE92 unique submission" with a download button. Its audit's uniqueness block is `unique_vs_available` against three bridge rasters (d28, h19_5, h27_4_solo), and its own note says "Full 2,060-raster registry audit ... pending". On the full 2,216-raster registry it FAILS (0.7691). The generated pages now show DO NOT SUBMIT, and the file is linked only as research-only.
- IR-1028C-7: `scripts/build_unique_submission.py` (on `main`) writes pages with the same overclaim. Do not rerun it without the full-registry PI-1 gate.
- Legal flag: public-mirror repos (GEMSDOE, GEMSDOE24, 60GEMSDOE, GEMSDOE84) hold competition-derived rasters; DrivenData Terms of Use reserve reproduction. Not restored or redistributed here. Status FLAGGED_DATA_USE_UNCHECKED.
- Data-use: `.cache/gems_inputs/training_features.tif` is **absent** from this checkout. The holdout and LBM-v2 scripts depend on it. It is not restored from public-mirror part files until the data-use flag is cleared. Consequence: LBM-v1 MODEL re-estimation of new candidates (`scripts/lbm_estimate.py`) cannot run here, so no new MODEL numbers are produced in this session.
- Budget: TIPCOMP's earlier sessions ran placement variants E3/E3b/E3c/E3d; these may exceed the 3-experiment budget unless variants count as repairs. Flagged for review.

## 6. Untried hypotheses (see `HYPOTHESES_20261028_STANDING.md`)
- Rank 1 (H-A): groundwater-head offset across concealed structures (USGS NWIS). **Blocked here** (waterservices.usgs.gov unreachable from the sandbox; free official source).
- Rank 2 (H-B): strain-gated lineament orientation. Data access unverified.
- Rejected as duplicates: magnetic-source-depth (EULERFUSE), lineament density (ALI/FAULTNET).
- No hypothesis is validated; no holdout run; no slot used.

## 7. Experiments and budget
- Experiments counted this session: 1 (E-UNIQ-20261028-A, full-registry PI-1 audit). Limit 3. Wall clock within the 2-hour limit.
- Run card: `evidence/run_card_E-UNIQ-20261028-A.json`.

## 8. Remaining work
1. Paste the verbatim competition prompt into `docs/STANDING_PROMPT.md` (current file is a reconstruction).
2. Resolve the leaderboard conflict (0.4413 vs 0.3195 vs 0.2778) with an organizer source.
3. Clear the data-use flag, then restore `training_features.tif` (from a clean source) so holdout and LBM-v2 can run.
4. Build a new candidate that passes full-registry PI-1 *and* beats the holdout best (R0 0.09775; TIPCOMP E2 0.09617). Options: dot-level displacement of TIPCOMP away from GEMSDOE22 and its neighbours (≈25% of dots must move for 0.68), or a new lane (H-A).
5. Re-run the RIESZ and LBMC1 surface-level PI-1 checks (only final-dot PI-1 was run here).
6. Resolve SLOT_PLAN vs SUBMISSION_READY on RIESZ; the selector makes the slot decision.
7. Obtain NWIS data outside the sandbox and validate H-A on the holdout.

## 8b. Test status (inherited)
- Full suite on this tree: 15 failed, 782 passed, 19 skipped. On `origin/main` (before this PR), the same suite had 25 failed. None of the 15 failures is new; this PR fixes 10 of main's.
- The 15 remaining failures are pre-existing on `main`. They are listed in `evidence/test_failures_inherited_20261028.txt`. Several encode main's earlier primary/unique claims (for example thermotilt and ventscarp run-card contracts, and the piedfront and coulombdm primary contracts). They need a separate decision, not a silent edit.

## 9. Limitations
- All scores are CLAIM (owner-reported) or MODEL. No organizer receipts exist. HOLDOUT-DTI numbers are from the repo's earlier records; the static holdout is an instrument limitation (repo notes).
- Final-dot PI-1 only; surface PI-1 not re-run for all candidates.
- No DrivenData authentication used. Competition pages were read from public text only.
