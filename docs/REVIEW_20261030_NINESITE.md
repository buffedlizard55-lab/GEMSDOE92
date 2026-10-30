# Repository review — 2026-10-30 (branch `arena/9f125ee7-gemsdoe92`)

**Plain answer: no file is cleared for upload to DrivenData, and no new TIFF was generated in this session.** Every claim below is labelled `ORGANIZER-CONFIRMED`, `OFFICIAL-TEXT`, `REGISTRY-MEASUREMENT` (bytes I hashed or measured), `CLAIM` (owner or user reported, no organizer receipt), `HOLDOUT-DTI`, or `MODEL`. Nothing in this review is a leaderboard estimate.

| Item | Status |
|---|---|
| Best reported GEMSDOE file | GEMSDOE32 `h33-h33-2-b2-…-e5eb6e7e-zeros.tif`, **0.2778 `CLAIM`** (owner page says it is already submitted; no receipt) |
| Safe to submit today | **None.** Local primary `ok_to_submit: false` ([`docs/downloads/current_submission.json`](downloads/current_submission.json)) |
| New unique TIFF this session | **Not generated.** Reasons in §0 |
| Tests | `834 passed, 19 skipped` (`pytest tests`, Python 3.11, numpy 2.4.6, rasterio 1.4.4) |
| Site checker | `SITE CHECK PASS (132 served raster(s) gated)` (`scripts/check_site.py`) |
| Experiments used / weekly slots | `0 / 3` · `0` |

## 0. Why no new TIFF was generated (decision, with evidence)

1. **The repo's own duplicate gate cannot be passed by any in-footprint raster under its literal reading.** The pinned witness `17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` is positive on every one of its `5,167,373` finite cells (`REGISTRY-MEASUREMENT`, §3). Any nonempty candidate therefore has 100% of its dots within 3 px of a witness positive. The protocol does not define "dots" for a continuous raster, so this is a policy gap, not a close call. Only the owner can resolve it.
2. **The method cannot be validated here.** The feature stack and `training_features.tif` are absent from this checkout, and DrivenData needs a login (`IR-1028C-8`). Without a holdout, any new raster would be an unvalidated guess. The protocol forbids spending a slot on that.
3. **Another unvalidated raster adds little.** The repo already holds 144 TIFFs in `docs/downloads`, and every nine-site file is `1.0`-binary and geometrically near-identical to the others (§2).

## 1. Executive summary — best file per site (nine sites you listed)

Overlap columns are my measurements against the other eight files (`REGISTRY-MEASUREMENT`, `scripts/nine_site_byte_check.py`, `evidence/nine_site_byte_check_20261030.json`). "Within 3 px" = share of this file's dots within 3 px of the other file's dots. The protocol's internal duplicate line is >70%.

| Site | Best file to download (exact name) | Reported score (evidence class) | Estimated score | Unique vs the other eight? | OK to download? | OK to submit? |
|---|---|---|---|---|---|---|
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 `CLAIM` | Not estimable | **NO** — min 88.5%, max 100% within 3 px | Research only | **NO** |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 `CLAIM` | Not estimable | **NO** — dot-identical to GEMSDOE30 | Research only | **NO** |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 `CLAIM` | Not estimable | **NO** — min 86.7%, max 98.0% | Research only | **NO** |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.2710 `CLAIM` | Not estimable | **NO** — min 95.5%, max 100% | Research only | **NO** |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 `CLAIM` | Not estimable | **NO** — dot-identical to GEMSDOE25 | Research only | **NO** |
| GEMSDOE31 | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 `CLAIM` | Not estimable | **NO** — min 95.4%, max 100% | Research only | **NO** |
| **GEMSDOE32** | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | **0.2778 `CLAIM`** (highest reported) | Not estimable | **NO** — min 99.9%, max 100% | Research only | **NO** — owner says already submitted; resubmitting spends a slot for no information |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 `CLAIM` | Not estimable | **NO** — min 92.6%, max 99.7% | Research only | **NO** |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 `CLAIM` | Not estimable | **NO** — min 97.3%, max 97.6% | Research only | **NO** |

**Answer to "which one should we submit?": none today.** Among the nine, GEMSDOE32 has the highest reported score (0.2778 `CLAIM`), and its owner already submitted it. Nothing among the nine can be cleared under either reading of uniqueness. The only exact in-footprint duplicate is GEMSDOE25 = GEMSDOE30 (same 44,090 dots, same 0.2600 claim, different outside-footprint encoding; both under owner `buffedlizard55-lab`). The owner pages say the same: GEMSDOE36's page marks every site `NO` (e.g. GEMSDOE24 `max 100.00% within 3 px`), and GEMSDOE28's page says `all 36 pairs exceed the 70% / 3 px rule`.

**Estimated score:** no defensible estimate exists. The repo's own model audit records `"valid_leaderboard_prediction": false` (`docs/downloads/score_estimator_audit_14f85876.json`). Every `MODEL` figure in the repo is fitted to owner-reported claims and must not be read as a score.

## 2. What the nine files are, measured (`REGISTRY-MEASUREMENT`)

- All nine are strictly binary: every positive cell equals `1.0`. All are `EPSG:32611`, `3730 × 3292`, `100 m` transform `(100, 0, 243350, 0, -100, 4508550)`. None has values outside `[0, 1]`.
- Outside-footprint encoding is split. Five use NaN (`7,111,787` NaN cells, GEMSDOE24/25/27/28/31); four use zeros (GEMSDOE30/32/33/36). The official spec says outside bounds should be "null or nan" (§4, IR-0130-2).
- Dot counts: GEMSDOE24 60,069 · 25 44,090 · 27 61,328 · 28 37,660 · 30 44,090 · 31 40,199 · 32 37,654 · 33 41,865 · 36 38,854.
- **The family is one structure, not nine lanes.** A random dot field with GEMSDOE32's dot count, placed in the same footprint, puts `15.1%` of its dots within 3 px of GEMSDOE32 (mean of 5 seeds). The nine files sit at `86.7–100%` (minimum over the other eight, per file). They share a common geometry; the uniqueness picture is weak evidence of novelty.
- **GEMSDOE32 is a strict subset of GEMSDOE30:** all `37,654` GEMSDOE32 dots are present in GEMSDOE30's `44,090`, and `6,436` are removed. This matches the owner-page statement exactly (`verified by byte check`).
- The repo's `data/parent_R0_zeros.tif` has the same SHA-256 as GEMSDOE32's file (`c55bafc4…`) and the same 37,654 dots. The repo's "R0" parent is therefore the 0.2778 bytes.

## 3. Verified items, line by line (with links for manual review)

| # | Claim | Result | Source |
|---|---|---|---|
| V1 | Metric = distance-weighted Tversky, `k(d)=max(1−d/300 m,0)`, α=0.2, β=0.8 | **Verified** against `vendor/gems57/metric.py` (`kernel`, `dti_binary`; `TP_w = Σ_g max p·k`, `FP_w = Σ_{p>0} p·[1−max_g k]`, `DTI = TP/(TP+αFP+βFN)`) | [Problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) |
| V2 | Format: EPSG 32611, 100 m, same bounds, single float32 band, values in [0,1], outside "null or nan" | **Official text verified**; repo files meet all except the outside-bounds encoding (see IR-0130-2) | [Problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/); [Rules PDF §3.2, §3.5](https://docs.nlr.gov/docs/fy26osti/96647.pdf) |
| V3 | Deadline Dec 3 2026 11:59 p.m. UTC (34 days from 2026-10-30) | **Verified** | [Competition home](https://www.drivendata.org/competitions/306/competition-doe-gems/) |
| V4 | Up to 3 submissions per week; one final submission per entity | **Verified** | [Rules PDF §3.2, §3.4](https://docs.nlr.gov/docs/fy26osti/96647.pdf) |
| V5 | "Entire submission is an original work" (A.5.1); generative-AI use must be disclosed (§3.2) | **Verified**; `AI_USE.md` exists but must be updated for any submission | [Rules PDF Appendix A.5](https://docs.nlr.gov/docs/fy26osti/96647.pdf) |
| V6 | Duplicate / similarity rule | **No such clause in the official rules** (all 7 chunks read). The 70%/3 px rule is internal to this repo. | [Rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) |
| V7 | Public leaderboard, read 2026-10-30 | #1 **0.4544** · #2 0.3925 · #3 0.3915 · #4 0.3860 · #5 0.3642 · #22 0.3399. **0.4413 and 0.3195 do not appear in ranks 1–22.** The page has no timestamp, so this is a same-day read, not a dated snapshot. Public-split scores are not the private test score. | [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) |
| V8 | Best GEMSDOE claim (0.2778) sits below rank 22 of the public board | **Verified** (0.2778 < 0.3399). Gap to #1: 0.177; to #5: 0.086. | V7 |
| V9 | Nine-site claimed scores match the repo ledger | **Verified** for all nine (ledger `claims_20261027/28/29.txt`, `site_scores_claimed_20261027.csv`) | `ledger/` |
| V10 | Owner pages for GEMSDOE32, 36, 28, 31 | Read live; each reports `CLAIM`/`OWNER-REPORTED` scores, none with an organizer receipt; each says no file is cleared | Links in §6 |
| V11 | Nine-file SHA-256 prefixes | **Verified** — computed bytes match the prefixes printed on the GEMSDOE36 owner page for all nine | `evidence/nine_site_byte_check_20261030.json` |
| V12 | 17GEMSDOE_E witness: all footprint cells positive | **Verified**: `5,167,373` finite cells, all `> 0` (min 0.00046, max 0.98); SHA-256 `ab0a0a62…` at the default-branch HEAD of `buffedlizard55-lab/17GEMSDOE` | [Repo file](https://github.com/buffedlizard55-lab/17GEMSDOE/blob/main/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif) (default branch, cloned 2026-10-30) |
| V13 | Reference solution is a PyTorch U-Net with Monte-Carlo CV | **Verified** from the repo listing (`unet-mc-cv-reference-solution.ipynb`, README) | [Reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) |
| V14 | Bash allowlist vs fetch tool | `IR-1028C-6` said DrivenData was unreachable. The **fetch tool** reached drivendata.org, herox.com, docs.nlr.gov and github.com; the bash sandbox allowlist is narrower. Both facts are true; use the fetch tool for official pages. | — |

## 4. Irregularities for review (`IR-0130-*`)

- **IR-0130-1 — Primary pointer mismatch on the public page.** `docs/index.html` declares `data-primary="true"` on `downloads/gemsdoe92-rieszlbm2-…-zeros.tif` (`DO NOT SUBMIT`), while the headline "One-Click Download" banner on the same page describes `gemsdoe92-dexpkostrov1-…-ffa21c17-zeros.tif` (also `DO NOT SUBMIT`). Both are negative, so no upload is at risk, but a reader sees two different "current" files. Fix needs a decision on which file is primary; the renderer (`scripts/render_site_v3.py`) owns the page. **Not changed here.**
- **IR-0130-2 — Outside-footprint encoding conflicts with the official text.** The official spec says "data outside the bounds is null or nan". Most repo files use zeros outside. Under the metric formula, zeros and NaN are score-neutral (zero-valued cells add nothing to TP or FP, and ground truth lies inside the footprint), so this is a format question, not a score question. The reason given for zeros (the portal's "Predicted values must be in range [0, 1]") is unverified. The owner page for GEMSDOE31 says a portal "rejected NaN" with that error (conditional wording, unverified), and the user reported the same error. **Needs an organizer answer** on the DrivenData forum.
- **IR-0130-3 — The literal duplicate gate is unsatisfiable, and "dots" is undefined for continuous rasters.** See §0. The official rules have no such gate (V6). The internal gate was adopted by earlier sessions; this review measured that it blocks every in-footprint candidate (17GEMSDOE witness). **Decision needed from the owner** (see §8).
- **IR-0130-4 — The "unique" lanes are near-identical geometry.** Pairwise 86.7–100% within 3 px across the nine files, against a 15% random baseline (§2). Passing a 70% rule is therefore a weak test of novelty. Dot-level novelty is not the same as scientific novelty.
- **IR-0130-5 — Provenance of `data/bridge/`.** `registry/data_manifest.json` says these files were restored from the owner mirror `buffedlizard55-lab/GEMSDOE24`, not from DrivenData. `labels.tif` and `existing_faults.tif` are byte-identical (SHA-256 `7ba308cc…`). `d28.tif` (`91eae1ca…`) is byte-identical to GEMSDOE25's submitted file. So the local "sample submission" and "labels" used by the format validator are **not organizer-authenticated** (`IR-1028C-8` is related). Competition data is also committed to a public repo (`.gitignore` comment); DrivenData's data terms were not verified (login required). **Legal/owner review needed.**
- **IR-0130-6 — A superseded card still says `promote`.** `evidence/review797e_superseded_knickloqo_card.json` has `"verdict": "promote"` and `"submission_eligible": true`, although its filename says superseded. Only that file contains these two values. A naive reader or script could take it as clearance. **Recommend relabelling**; not changed here (evidence file).
- **IR-0130-7 — Broken citation (fixed).** `docs/WHY_0_2778.md` cited `score_estimator_audit_14f85876.json` at an `evidence/` path that does not exist. Corrected to `docs/downloads/score_estimator_audit_14f85876.json` (verified present).
- **IR-0130-8 — Leaderboard-inference risk.** The repo's `MODEL` estimates (the "leaderboard model") are fitted to owner-reported scores matched to other teams' public rasters. The rules require the entire submission to be an original work (A.5.1), and the rules' private-test clause (§3.6.2) is written to discourage tuning to public scores. The repo's own audit reports `valid_leaderboard_prediction: false`. **Recommend that no `MODEL` figure be used to choose a file**, and that the approach get a rules review before any use.
- **IR-0130-9 — Stale open PRs.** 29 PRs are open (1 draft, #162), most from earlier sessions. They overlap in content and are not triaged. **Not closed here** (other sessions' work; no instruction to close).
- **IR-0130-10 — Repo weight.** `docs/downloads` is 45 MB with 144 TIFFs. `README.md` is 185 KB, `SESSION_PROMPT.md` 73 KB, `IRREGULARITIES.md` 1,555 lines. Every session re-reads these. Recommend moving TIFFs to a release asset and archiving stale status blocks.
- **IR-0130-11 — Hallucination history.** `IRREGULARITIES.md` records earlier fabricated SHA-256 digests and wrong band numbers (`#IR-92-LISTRICLOQO-DOC-HALLUCINATED-SHAS-AND-BAND-NUMBERS-FIXED`, `#IR-92-VENTSCARP-DOC-HALLUCINATED-PIXEL-COUNTS…`, both 2026-10-25). This review re-derived every number above from bytes or from fetched text; none is copied from an earlier note without a check.
- **IR-0130-12 — Stated `0.4413` / `0.3195` leaderboard values are stale or wrong.** The live public board shows `0.4544` at #1. The two values were not found in ranks 1–22 (V7). Use the live page, not user snapshots.

## 5. Three-pass review

**Pass 1 — Implement and verify.** Installed pinned requirements in a venv outside the repo (`/home/user/.venv_gems`). Ran `pytest tests` (834 passed, 19 skipped) and `scripts/check_site.py` (PASS, 132 rasters). Verified the official metric, format, rules, leaderboard and owner pages (§3). Built `scripts/nine_site_byte_check.py` and `evidence/nine_site_byte_check_20261030.json` to measure the nine files from bytes (§1–2). Added `tests/test_nine_site_byte_check_20261030.py` to pin those values.

**Pass 2 — Review for bugs and missing requirements.** Found and fixed one broken citation (IR-0130-7). Found and flagged: the primary-pointer mismatch (IR-0130-1), the outside-encoding conflict (IR-0130-2), the unsatisfiable literal gate (IR-0130-3), the provenance gap (IR-0130-5), and the superseded `promote` card (IR-0130-6). The site renderer, primary pointer and superseded card are not edited here, because each change alters a decision that belongs to the owner or needs a regenerated site.

**Pass 3 — Check against the original request.** Table in §7.

## 6. Source links for manual review

- Problem description and metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Competition home (dates, prizes, structure): https://www.drivendata.org/competitions/306/competition-doe-gems/
- Public leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Official rules (NLR PDF): https://docs.nlr.gov/docs/fy26osti/96647.pdf · HeroX mirror: https://www.herox.com/GEMSPrize/resource/2274
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index · Projection: https://epsg.io/32611
- GeoDAWN (USGS, DOI 10.5066/P93LGLVQ): https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- INGENIOUS (GBCGE): https://gbcge.org/current-projects/ingenious/ · Great Basin dataset (DOI 10.15121/1881483, cited in rules §3.3)
- Owner pages read this session: [GEMSDOE32](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) · [GEMSDOE36](https://buffedlizard55-lab.github.io/GEMSDOE36/docs/) · [GEMSDOE28](https://buffedlizard55-lab.github.io/GEMSDOE28/) · [GEMSDOE31](https://buffedlizard55-lab.github.io/GEMSDOE31/docs/)
- Owner repos byte-checked: [24](https://github.com/buffedlizard55-lab/GEMSDOE24) · [25](https://github.com/buffedlizard55-lab/GEMSDOE25) · [27](https://github.com/buffedlizard55-lab/GEMSDOE27) · [28](https://github.com/buffedlizard55-lab/GEMSDOE28) · [30](https://github.com/buffedlizard55-lab/GEMSDOE30) · [31](https://github.com/buffedlizard55-lab/GEMSDOE31) · [32](https://github.com/buffedlizard55-lab/GEMSDOE32) · [33](https://github.com/buffedlizard55-lab/GEMSDOE33) · [36](https://github.com/buffedlizard55-lab/GEMSDOE36)

## 7. Why GEMSDOE32 scored highest among the nine, and whether we can beat 0.2778

**What the evidence supports (`REGISTRY-MEASUREMENT` plus `OFFICIAL-TEXT`):**

1. GEMSDOE32 is a *pure subset* of the 44,090-dot raster in GEMSDOE30. Exactly `6,436` dots are removed (§2, byte-verified). The owner page says the removed dots are the catalogue-near ones (owner statement, not re-measured here).
2. The official problem page says the test faults are *newly identified* faults "not contained within the current public USGS database". Dots adjacent to known faults are therefore less likely to be hits, while they still add false-positive mass under `FP_w`. Removing them raises DTI if the test faults are not adjacent to the catalogue. That is the mechanism the 0.2600 → 0.2778 step is consistent with (`CLAIM`, not measured here).
3. The metric's false-positive term has weight `α = 0.2`, so pruning low-value dots is cheap, while false negatives weigh `β = 0.8`. A pruned raster only helps when the pruned dots carry little truth credit.

**What the evidence does not support:** that 0.2778 is an organizer score; that the mechanism is causal; that the test faults share the catalogue's geometry; or that the same pruning would keep helping beyond this point. The repo's `WHY_0_2778.md` makes the same caveats.

**Can we beat 0.2778?** Possibly, but not shown here. The public top-five sits at `0.3642–0.4544` (V7), so 0.2778 is not the bar. Reaching the public top would need a different information source or model class than dot-pruning. This checkout cannot train or validate one: the official features are not present (§8).

## 8. Decisions only the owner can make (not decided by this agent)

- **D1 — Duplicate rule.** Choose one: (a) drop the 70%/3 px gate and keep only exact-content duplicate checks, which the official rules do not require (V6); (b) keep it but define "dots" for continuous rasters (e.g. top-N by value) and add a random-null z-score, since the literal rule blocks everything (§0); (c) keep it as is and accept that nothing is clearable.
- **D2 — Outside-footprint encoding.** NaN (official text) or zeros (repo convention)? Ask the organizers on the DrivenData forum (https://community.drivendata.org/c/gems-prize-challenge/111) and record the answer.
- **D3 — Legal review.** (i) Whether the `MODEL` leaderboard inference and the use of other teams' public rasters comply with A.5.1; (ii) whether competition-derived files may be committed to a public repo (IR-0130-5).
- **D4 — Primary file and superseded card.** Choose the primary (IR-0130-1) and relabel `review797e_superseded_knickloqo_card.json` (IR-0130-6).

## 9. Hypotheses (not validated; ranked; each needs the official training features)

Honest status: none of these is tested here. "Not found" below means a case-insensitive search of `docs/`, `README.md`, `scripts/`, `gems/` and `IRREGULARITIES.md` returned no match. It does not prove the idea was never tried.

| Rank | Idea | Layers (official names) | Physical signature | Why off-catalogue | Named mimic | Repo status (grep) | Cost | Data needed |
|---|---|---|---|---|---|---|---|---|
| 1 | Train the official-style U-Net on the 100 m feature stack with spatial-block CV, then threshold with the repo's metric rule (`marginal_inclusion_threshold`: keep a dot only if `k > α·DTI`) | All layers in `training_features.tif`: conductivity, detrended elevation & slope, strain rates, isostatic gravity & slope, RTP/TMI and their slopes, top-of-crust depth, earthquake density | Learned multi-layer fault-likelihood | Trained on catalogue labels, but scored on hidden whole segments through the hide-recover holdout | Flight-line or gridding artefacts in magnetics; cultural features in slope | U-Net only *audited* (`ANALYSIS_20261024_COULOMBLOQO.md` cites the reference notebook); no trained model found | Medium–high (CPU feasible, GPU faster) | `training_features.tif`, `labels.tif` (DrivenData login) |
| 2 | Gradient-boosted trees on the same features with spatial-block CV, thresholded the same way | Same as 1 | Same as 1, tree-based | Same as 1 | Same as 1 | `random forest` / `XGBoost` / `graph neural` / `Bayesian` / `Gaussian process`: 0 matches | Low | Same as 1 |
| 3 | Gaussian-process posterior over catalogue-derived lineament density, with magnetic and gravity gradients as covariates | RTP magnetic, horizontal gradient of TMI, isostatic gravity slope | Smooth spatial prior on structure | Prior uses only visible (non-held-out) faults | Catalogue sampling bias | `Gaussian process`: 0 matches; `kriging`: 3 files | Medium | Same as 1 |

**Ranking basis:** expected gain is highest for 1 (a learned model on the official features has never been trained here), cost is lowest for 2, and 3 is the most speculative. None of these is a promotion; each must beat the current holdout best before a slot is considered.

## 10. Limitations and access needed

- **DrivenData data (login):** `training_features.tif`, `labels.tif`, `sample_submission.tif`, `1m_DEM_links.csv`. Without them the feature stack cannot be rebuilt. The user-provided Dropbox links are not bulk-downloadable from this sandbox.
- **Organizer receipts:** the submission page scores are visible only after login. No `ORGANIZER-CONFIRMED` submission score exists in this repo.
- **USGS GeoDAWN and 1 m DEM:** reachable as metadata pages but not in bulk from the sandbox. The DEM link list is in the official data bundle.
- **Weekly-slot decisions** belong to the owner (3 per week).
- **Compute:** a GPU helps the U-Net route; CPU is feasible for the tree and GP routes.

## 11. Next steps (ordered; owner actions marked)

1. **Owner:** decide D1–D4 (§8).
2. **Owner:** download the official data bundle from DrivenData and place it in `data/`, then run `make verify` and `make test`. This unlocks hypothesis 1 or 2.
3. **Owner:** ask the organizers the NaN-versus-zeros question (D2).
4. **Agent:** after step 1–2, run one experiment per hypothesis under the protocol (3 max), validate on the hide-recover holdout, then write a run card. Promotion stays a separate selector step.
5. **Agent:** fix the primary pointer and relabel the superseded card once D4 is decided.
6. **Owner:** triage the 29 open PRs (IR-0130-9). Close the superseded ones.
7. **Agent:** move the 144 research TIFFs to release assets to shrink the repo (IR-0130-10).

## 12. Submission guidance for the user (plain English)

- **Do not submit any file in this repo today.** Every candidate is negative or unvalidated (`ok_to_submit: false`).
- **Do not resubmit GEMSDOE32's file.** Its owner says it is already submitted.
- **Do not use the `MODEL` estimates or the stated 0.4413 / 0.3195 values** for decisions (IR-0130-8, IR-0130-12).
- **Read `docs/how-to-submit.html` only after the owner clears a file** (D1–D4).
