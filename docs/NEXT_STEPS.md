# NEXT_STEPS — after the 2026-10-24 APRONRIDGE session

## Current status (supersedes prior sections below for action purposes)

This section supersedes historical action lists below. **Do not submit any current artifact.** Latest tooling hardening and the three-pass repository review are in [`REVIEW_20261024_SESSION.md`](REVIEW_20261024_SESSION.md); the machine-readable card is [`downloads/repo_review_run_card_20261024.json`](downloads/repo_review_run_card_20261024.json).

**`APRONRIDGE free1d` (`h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif`) is the new primary download — closing both technical challenges from the prior queue (non-R0 standalone emission + beating `RELIEF p10` on `gems57-pooled-hide-v2`), while keeping `verdict: negative` / `submission_eligible: false` under the binding dense public witness.**

- **`HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` withheld positives)**: **`0.008354 [0.006823, 0.010135]`** (hybrid siblings `s60f40 = 0.008291`, `s50f50 = 0.008097`), vs `RELIEF p10 = 0.006045`, `STRAINBREAK f60s2i = 0.005487`, `ANASIG f45Atop = 0.004967`, `SPRINGALIGN f33Ctop = 0.004865`, `BREAKLINE f45Ltop = 0.004861`, `R0 = 0.004006`, and `STEPEDGE f60Sraw = 0.003980`.
- **Leakage canaries**: `11/11 PASS` (`max symmetric AUC = 0.636490 <= 0.90`).
- **Uniqueness**: Locally unique on pre-placement surface (`|ρ| <= 0.1222`, top-37k overlap `0.5527`) and final dots (`worst_forward_overlap = 0.4605 <= 0.70` across all `46` cross-lane local rasters including `STEPEDGE` at `0.3023–0.3783`; `0.6028–0.6456 <= 0.70` against top `62GEMSDOE`/`GEMSDOE23` sparse public witnesses). Blocked solely by `17GEMSDOE E-proba-multiscale` (`100%` footprint positive => `forward_overlap = 1.000`, `evidence/public_witness_apronridge.json`).

## Highest-value next actions, in strict priority order

1. **Operator policy update on dense continuous public rasters (Unblocks Weekly Slot #1)**: Revise Rule 1's binary `> 0` 3-px halo test so continuous probability rasters with `> 150,000` positive pixels are evaluated by continuous Spearman rank correlation (`|ρ| <= 0.90`), while binary/sparse dot rasters (`<= 150,000` positive pixels) retain the `<= 0.70` 3-px halo rule.
2. **Run a full refreshed sparse-plus-Spearman public registry scan (`scripts/audit_public_registry.py --surface .cache/apronridge_surface.tif`) on `APRONRIDGE free1d`** immediately after Step 1's policy update, then flip `submission_eligible: true` if 0 sparse public rasters exceed `0.70`.
3. **Acquire the first `ORGANIZER-CONFIRMED` receipt (`Blocker 0`: `51 BUILT / 0 RECEIPT` in `ledger/submissions.csv`)**: Upload `APRONRIDGE free1d` (single weekly slot; never upload `s60f40` or `s50f50` alongside it) and record the exact DrivenData submission ID, timestamp, and score in `ledger/submissions.csv` to calibrate whether `HOLDOUT-DTI` (`0.008354`) or `SGMC PROXY` (`0.0801` vs `STEPEDGE` `0.1415`) better predicts private expert-mapped test faults.
4. **Shoreline & Drainage-Crossing Mimic Suppression on `APRONRIDGE` (`APRONRIDGE v2`)**: Once official USGS NHD flowlines or NBMG Lake Lahontan stillstand contours are pinned in `registry/session_manifest.json` with SHA-256 hashes and verified redistribution terms, test suppressing contour-parallel Sehoo/Eetza shoreline benches and wash-parallel terrace risers inside `H_apron`.
5. **5-Fold Spatially Blocked Multi-Sensor Patch U-Net / Gradient-Boosted Ridge Learner**: Train a strictly spatially blocked (`holdout.buffered_component_draw`), Tversky-loss (`alpha=0.2, beta=0.8`) multi-band model over `APRONRIDGE` features (`Bands 2, 5, 6, 12, 15, 19` + geothermometer halo from `BLIND-GEOTHERM`), followed by 1D crest extraction + `2.8 px` spaced thresholding (`drivendataorg/gems-prize-reference-solution` architecture adapted to non-redundant kernel-spaced emission).

---

## Historical notes (superseded for action purposes)

### Prior automated review — 2026-10-24 UTC
1. Preserve the literal registry stop; [fresh exact-file check](downloads/review_20261024_springalign_witness_v2.json) proves SPRINGALIGN fails and the witness halo covers the whole footprint.
2. An authorized protocol resolution is required before any candidate can be cleared for upload. Do not silently exempt dense rasters or change the >70% rule. See [prior review](REVIEW_AUTOMATED_20261024.md).

# Prior NEXT_STEPS — after the 2026-10-24 ANASIG session

## Current status (supersedes the collar section below for action purposes)

**ANASIG f45 is the primary download; verdict negative / NOT CLEARED.** Locally lane-unique (worst forward 0.550, |ρ| 0.547 over 24 local rasters; surface |ρ| 0.024), format-valid (10/10 gates), HOLDOUT-DTI 0.004967 [0.004098, 0.005940] (Δ vs R0 +0.000961 [+0.000168, +0.001814]) — but below the holdout best RELIEF p10 (paired Δ −0.001078 [−0.002034, −0.000112]), below R0 on the SGMC proxy (0.080556 vs 0.096060), and stopped by the binding public witness (17GEMSDOE E-proba, 100% footprint-positive; forward overlap 1.000 for these bytes, `evidence/public_witness_anasig.json`). **Do not spend a slot.** Full record: `docs/ANALYSIS_20261024_ANASIG.md`.

## Highest-value work, in order

1. **Operator decision on the literal public rule.** As written, a footprint-positive continuous raster makes every candidate a duplicate (proven, not hypothetical). Until resolved, no candidate in this repo can be both honest and "promote" under that rule — do not silently reinterpret it.
2. **Do not rebuild SCARPPOL or BREAKLINE doses.** Template keep-greedy is coverage-dominated (~90% shared keeps); any new DEM-ridge lane must change the keep stage too, or start from a non-R0 keep set, and must check final dots vs BREAKLINE/SCARPPOL *before* calling itself a new lane.
3. **Beat the holdout best honestly first.** Next lane must clear RELIEF p10 (0.006045) on `gems57-pooled-hide-v2` with paired CI excluding 0 vs R0 *and* stay <0.70 forward overlap vs BREAKLINE/SCARPPOL/R0 — ANASIG cleared uniqueness, not the holdout bar.
4. **Spring-pair alignment (not density)** is the one untested geothermal-vent construction left from this session's screens; it needs a strike-alignment screen before any build.
5. Keep `scripts/audit_public_registry.py` fail-closed: it now requires `--surface` for non-collar candidates (shared-tool fix this session).

---

# NEXT_STEPS — after the 2026-10-24 registry stop

## Current status

One new method was evaluated: a 200–300 m collar around visible mapped faults, excluding the parent R0 dots' 300 m halo. It passes file-format gates and improves the local catalogue hide-and-recover measure, but the expanded public registry scan triggers the protocol's literal duplicate stop. **The result is negative. Do not use a weekly submission slot.** The TIF remains available as a negative deliverable, with the homepage clearly saying format-valid/downloadable but not cleared for submission.

**HOLDOUT-DTI** (`gems57-pooled-hide-v2`; buffered whole-component hide/recover; 8 spatial folds, seeds 20 and 30; 22,663 withheld positives; 1,000 paired 20 km block bootstrap draws): candidate 0.046866 [0.040216, 0.053315]; R0 0.004006 [0.003424, 0.004690]; paired Δ +0.042860 [+0.036122, +0.049357]. This is not a DrivenData score.

## Critical uniqueness finding

The initial in-repository 14-raster audit was too narrow and produced an incorrect selector-positive result. It is superseded. A broader scan of current default branches in 102 public `buffedlizard55-lab` repositories found 1,629 relevant TIFF paths / 1,285 unique Git blobs; 1,279 single-band rasters matched the target grid and were compared. The candidate's pre-placement surface and final dots both have **1.000000** forward 3-px overlap with accessible registry rasters; **131/1,279** exceed the 70% threshold. Worst absolute Spearman is below the 0.90 threshold (0.421367 on the surface; 0.492957 on the final dots), but overlap alone triggers the stop rule.

A concrete witness is [11GEMSDOE `gems-structural-area06-v1.tif`](https://github.com/buffedlizard55-lab/11GEMSDOE/blob/main/docs/downloads/gems-structural-area06-v1.tif), for which all candidate dots are within 3 px of positive support. Another witness is 17GEMSDOE's full-footprint `E-proba-multiscale` surface. Under the user's literal instruction, these are binding; this project does not waive the test because a raster has dense support. Full measurements/scope are `evidence/public_registry_uniqueness.json`.

The scan is broad, not exhaustive: historical branches, private repositories, other owners, unlinked GitHub Pages files, zip-only assets, and assets outside the searched directories may be missing. This caveat does not undo a duplicate already found.

## Highest-value work, in order

1. **Do not submit this candidate.** Keep it as a negative deliverable; preserve the cross-site audit and the corrected negative verdict. The build script must fail closed if the matching global audit is missing or says duplicate.
2. **Keep the registry scan repeatable/current.** `scripts/audit_public_registry.py` queries current public default-branch trees, downloads submission TIFF blobs to ignored `.cache/`, verifies Git blob SHA and size, and records failures. Run it periodically; never claim it covers deleted/history/site-hosted files.
3. **Resolve the literal overlap gate with the operator/policy owner outside this agent.** Until then, any candidate with >70% forward 3-px overlap against any registry raster is a duplicate and must stop. Do not silently substitute arrival-only overlap or exempt dense rasters.
4. **Calibrate with an organizer receipt.** The local evaluator recovers mapped catalogue segments; live target is private/new faults. A human may choose a different candidate only through the separate selector after reviewing policy and weekly quota. Upload/receipt entry are human-only.
5. **Build an off-catalogue validation instrument** before further candidate experiments. Score it separately from HOLDOUT-DTI and label it PROXY, never private test performance.
6. **Obtain the missing GeoDAWN stack through the official competition data tab** if authorized, hash/size/grid verify it, and check license/data terms. The feature stack is absent from this checkout's cache; band-specific hypotheses remain untested.
7. **Resolve redistribution terms** for tracked `data/` and releases; see `IRREGULARITIES.md`.
8. Keep both submission guides, homepage, run card, validator tests and status strings synchronized. A format pass means downloadable, not selected/submittable.

## Candidate queue and experiment budget

The five-hypothesis list is `docs/hypotheses_visible_collar_20261024.md`. Candidate 1 was tested and stopped by the duplicate gate. The lane protocol says stop when a duplicate is found; do not continue by testing more placement variations under this lane. Any future lane requires a fresh session, distinct hypothesis, pre-placement surface registry test, and the stated 3-experiment/2-hour budget.

## Data and evidence boundary

The bridged sample submission, catalogue, and parent are hash-verified against owner mirrors. That proves the local bytes match those pins; it does not authenticate them with DrivenData or establish redistribution permission. Official competition data and upload can require login. No credentials are stored or requested. A HOLDOUT-DTI value is never an organizer score.

## Parallel-session update — BREAKLINE (2026-10-24)

The band-based queue was in fact tested by a parallel session with a restored stack (`scripts/restore_inputs.py`): BREAKLINE f33/f38/f45 (`docs/ANALYSIS_20261024.md`). Consequences for the queue above: (1) **first action next session:** run `scripts/audit_public_registry.py` against `BREAKLINEf45Ltop` — it is unique on the 18-raster local registry (worst 55.0% vs R0) but un-scanned publicly, and the collar precedent shows dense public rasters can stop any candidate under the literal forward-overlap rule; record the result either way. (2) The off-catalogue instrument requested in item 4 partially exists: the USGS SGMC bedrock-fault control (62,703 px) is implemented in `scripts/report_breakline_proxies.py` (BREAKLINE +31% vs R0; collar candidate not yet scored on it — cheap, do it). (3) Blocker 0 unchanged: 36 BUILT / 0 RECEIPT in `ledger/`; one organizer receipt still outranks every local instrument disagreement (collar's catalogue-proximity holdout 0.0469 vs BREAKLINE's discovery-oriented SGMC gain price different things). (4) Do not build a fourth BREAKLINE dose or re-litigate screened-out lanes (BASEMENT-STEP/Band 15 SGMC AUC 0.378; pure seismicity too smooth; radiometrics AUC≈0.50).

## Latest review: decisive BREAKLINE public witness

See [current review](REVIEW_CURRENT.md). The queued public check now rejects BREAKLINE: 100% forward overlap with the hash-verified 17GEMSDOE full-halo raster. Every nonempty in-footprint candidate fails the current literal gate against this witness. This supersedes the pending-public-scan status above; the full registry was not rescanned. Zero new experiments or submission slots; resolve the policy before more placements.

## Follow-up registry stop (2026-10-24)

**2026-10-24 follow-up — BREAKLINE is now a confirmed duplicate under the literal registry rule.** A live, Git-blob-verified witness check compared one raster from 11GEMSDOE and five from 17GEMSDOE. BREAKLINE final dots have **100% forward 3-px overlap** with the dense 17GEMSDOE E-proba raster. This is REGISTRY-MEASUREMENT, not a competition score. The actual BREAKLINE pre-placement surface was not supplied and was **not checked**; no collar surface was substituted. A final-dot failure alone requires stop. No new experiment or TIFF was generated; no slot used. See [follow-up review](REVIEW_REGISTRY_STOP_20261024.md) and [run card](../evidence/breakline_registry_stop_run_card.json). **Download for research only; do not submit.**

## Late-session update — STRAINBREAK + GRAVCrest screen (2026-10-24)

Done this session: (1) fixed corrupt `public_registry_uniqueness.json` (missing comma, both copies); (2) closed the queued collar-on-SGMC item: **0.021192 vs R0 0.09606** — collar holdout gain does not transfer off-catalogue; (3) screened 7 surfaces under a pre-registered rule — GRAVCrest (rank 1) falsified, not built; (4) built STRAINBREAK f45/f60/f75 (3 experiments, budget exhausted): HOLDOUT-DTI up to **0.005487 (f60)**, dose plateau at f60=f75, SGMC 0.10516 < BREAKLINE 0.12611, locally unique (worst 40.0%); primary `h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif` (sha256 `000d0bd7…5c1f`), verdict **negative** (does not beat RELIEF p10 holdout best). Analysis: `docs/ANALYSIS_20261024_STRAINBREAK.md`; run card: `evidence/strainbreak_run_card.json`.

Next, in order: (1) **one organizer receipt** (human selector; BREAKLINE vs STRAINBREAK is now an explicit instruments-disagree choice — SGMC vs holdout — and cannot be resolved locally); (2) do not build a fourth STRAINBREAK dose (plateau measured) or retry GRAVCrest without a new gravity product; (3) shoreline-suppressed BREAKLINE only after a receipt prices far dots; (4) keep `scripts/check_site.py` + full pytest green whenever the served primary changes (primary is now `data-primary`-tagged; audits must carry `run_card` + `verdict`).

## Session update — `PIEDFRONT` (`f35Ptop`, `f40Ptop`, `f45Ptop`) (2026-10-24)

Done this session:
1. **Diagnosed why all prior off-skeleton lanes trailed `RELIEF p10` (`0.006045`):** In `BREAKLINE f45Ltop`, raw $\|\nabla\,\text{det\_elev\_slope}\|$ placed **74.8% (`12,673 / 16,944`)** of off-skeleton dots in steep mountain range interiors (`det_elev >= 38.76 m`) and only **23.1%** in the piedmont transition (`-29.40 <= det_elev < 38.76 m`), while `R0` left **794 spacing-legal holes** on `H19-5` ($d_{\text{R0}} > 2.8\text{ px}, d_{\text{cat}} > 2.0\text{ px}$) when `b2` pruned $d_{\text{cat}} \le 2.0\text{ px}$ dots without re-thinning.
2. **Pre-registered 4 untried geological hypotheses (`docs/HYPOTHESES_20261024_PIEDFRONT.md`):** `PIEDFRONT` (Rank 1), `GRAVTILT` (Rank 2), `GEOTHERM-CHALC` (Rank 3), and `MAGTILT-CONTACT` (Rank 4).
3. **Implemented and evaluated `PIEDFRONT` (`gems/piedfront.py`, `scripts/build_piedfront_variants.py`, `scripts/report_piedfront_proxies.py`):**
   - Combines relative scarp-break $\|\nabla\,\text{det\_elev\_slope}\| / (\max(\text{det\_elev\_slope}, 0) + 2^\circ) \times \text{coh}(\text{det\_elev})$ with the piedmont elevation + basement-depth + isostatic-gravity-slope envelope $W_{\text{pied}}$ (`Bands 12, 19, 5, 15`), refills **4,000 piedmont `H19-5` holes** via exact marginal expected-DTI greedy (`select_exact_marginal_dti_add`), and places 35% (`f35Ptop`), 40% (`f40Ptop`), and 45% (`f45Ptop`) far dots $>3.0\text{ px}$ off `H19-5` and $>3.0\text{ px}$ off all 5 prior off-skeleton lanes' far sets (`78.7%` in the piedmont).
   - **Pooled `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, 22,663 withheld positives):** **`PIEDFRONT f35Ptop = 0.006425 [0.005375, 0.007479]`** (`f40Ptop = 0.006402`, `f45Ptop = 0.006137`) — **highest non-collar `HOLDOUT-DTI` in the repository**, beating `R0` (`0.004006`, paired $\Delta = +0.002418 [+0.001538, +0.003255]$), beating `BREAKLINE f45` (`0.004861`, paired $\Delta = +0.001564 [+0.000471, +0.002607]$), and exceeding `RELIEF p10` (`0.006045`) in point estimate across all three doses (`+0.000379 [-0.000257, +0.001066]`).
   - **Local uniqueness (`REGISTRY-MEASUREMENT`, 29 local rasters):** pre-placement surface worst `|ρ| = 0.127084`, top-37,654 3-px overlap `0.434907`; final dots `f35Ptop` worst 3-px forward overlap **`0.649997` (`h19_5.tif`, $\le 0.70$ PASS)**, worst `|φ| = 0.585871` ($\le 0.90$ PASS).
   - **Verdict (`evidence/piedfront_run_card.json`):** `negative` (`OK TO DOWNLOAD` for research, `NOT CLEARED` for a weekly slot) because the paired 95% CI vs `RELIEF p10` includes 0, `SGMC` bedrock recovery is `0.059993` vs `R0` `0.096060`, and the public dense witness (`17GEMSDOE E-proba`) remains an unresolved policy blocker.

Next, in order:
1. **Operator policy ruling on `17GEMSDOE E-proba` dense surface + one live organizer receipt (`R0 = 0.2778` + one candidate)** before spending a weekly submission slot.
2. **Test a split off-skeleton budget (`PIEDFRONT` in piedmont + `GRAVTILT` / `STRAINBREAK` in bedrock highs)** to test whether a single locally-unique candidate can simultaneously beat `RELIEF p10` on `HOLDOUT-DTI` (`>0.006045` with paired CI $>0$) and `R0` on `SGMC` (`>0.096060`).
## STEPEDGE session update (2026-10-24) — unique + SGMC-best, still negative

Done: (1) R0 forensic audit (`evidence/r0_forensics_20261024.json`): CLAIM climb fully explained by spacing→3 px + catalogue clearance on a fixed skeleton; (2) fixed wrong DTI algebra in shared `gems/metric.py` (vendor evaluator verified clean); (3) screened 6 surfaces with preserved code (baseline reproduced to the digit) — coherence-gated STEPEDGE/TRANSV duplicate-stopped (0.75 vs BREAKLINE far), RADSTEP passed but weaker; (4) built STEPRAW f33/f45/f60 (3 experiments): f60 is **literal-unique on the 28-raster local registry** (0.461) with **SGMC 0.141464 (repo best)** but **HOLDOUT-DTI 0.003980** fails every bar → verdict negative, primary download, no slot. Sibling f33/f45 are duplicates (0.760/0.711) — never submit.

Next, in order: (1) **one organizer receipt** remains Blocker 0 — the selector choice is now STEPEDGE f60 (SGMC-best/unique) vs STRAINBREAK f60 (holdout-best unique) vs BREAKLINE f45 (balanced); receipt decision rules in `docs/ANALYSIS_20261024_STEPEDGE.md` §4; (2) obtain the 1 m DEM links via DrivenData login (largest identified content gap toward 0.4413; unrestorable from sandbox); (3) no fourth STEPEDGE dose, no new coherence-gated terrain lane (three duplicate-stops); shoreline-suppressed steps only after a receipt; (4) re-run local uniqueness at any future selector decision (verdicts decay as registry grows — see IRREGULARITIES 2026-10-24); (5) optional full public scan refresh (`audit_public_registry.py`) before any selector action — this session ran the single binding witness only.
