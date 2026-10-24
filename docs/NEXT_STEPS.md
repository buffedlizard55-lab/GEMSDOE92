# NEXT_STEPS — after the 2026-10-24 COULOMB session (negative verdict; queue unchanged, 4 follow-ups appended)

## Completed this session (COULOMB, 2026-10-24)

1. Pre-registered 5 ranked hypotheses (`docs/HYPOTHESES_20261024_COULOMB.md`) before any screen/build; gate-zero reproduced `BREAKLINE-L` exactly (canary `0.621604`, far-SGMC `0.072325`).
2. Built + scored 3 experiments (`free 0.005689`, `open 0.005184`, `seismo 0.005808` on `HOLDOUT-DTI`), all Tier-1 repulsion, `20/20` canaries PASS, locally unique (`0.263–0.290`).
3. Falsified at 100 m: Coulomb opening weighting (`0.5423` canary), 100 km seismicity fusion (statistical tie), TMI-tilt zero-contours (`0.5167`), MT-edge × dilatation (`0.5166`).
4. Falsified `max()` two-channel fusion vs multiplicative: weaker RTP channel (`0.5162`) dominates `71.6%` of `max()` emission over stronger relative-scarp (`0.6230`).
5. Disk-verified lineage counts (`D2.8 44,090`, `SOLO 40,199`, `R0 37,654`) and corrected 4 stale prose spots (3 files); logged conflicting intermediate `CLAIM` scores.

## New follow-ups (appended behind Blocker 0 + dense-policy decision; strict order preserved below)

- **F-C1. Rule-2 Coulomb re-evaluation**: score the built `COULOMB` rasters under fold-visible `d_visible > 2.0` to test whether the static self-mask (`#IR-92-STATIC-DCAT2-SELFMASK`) under-prices off-collar Coulomb emission. Zero new builds; one reporting script.
- **F-C2. Multiplicative re-fusion**: rebuild the Coulomb screen as `rel_scarp × O_coulomb` (HYDROCONDUIT pattern) instead of `max(R_rtp, R_scarp) × O` and re-screen only — tests whether the fusion operator, not the physics, caused the shortfall.
- **F-C3. Relative-scarp standalone lane**: `rel_scarp`-only screened `0.6230`, above the `BREAKLINE-L` baseline — the strongest unbuilt single component in the repo. Pre-register + screen + (if gate passes) build as its own lane.
- **F-C4. LIDAR1M-LAHONTAN stays HELD**: still blocked on `1m_DEM_links.csv` + `apps.nationalmap.gov`; remains the highest-leverage untested instrument.

---

# NEXT_STEPS — after the 2026-10-24 APRONRIDGE session
> **Latest verification (2026-10-24):** [D97F969E three-pass review](REVIEW_D97F969E.md) adds a freshly downloaded witness receipt and corrects the overall-best claim. No generation or policy exemption.

# NEXT_STEPS — current review status (2026-10-24)

## Current state (this section supersedes historical queues below)

**Current research download:** `APRONRIDGE free1d`, [`docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif`](downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif). It is format-valid and available for research download, but **NOT CLEARED FOR A WEEKLY SLOT; DO NOT SUBMIT**. Its exact-file witness measurement records `1.000` final-dot forward overlap with a hash-verified raster whose support is positive on every cell in the competition footprint. Under the literal rule, this mandates a stop for every nonempty prediction; it does not show geological equivalence. See [witness receipt](downloads/public_witness_apronridge.json) and [review](REVIEW_CURRENT.md).

- **HOLDOUT-DTI (historical, not rerun in this repository review):** `gems57-pooled-hide-v2`, 8 spatial folds, 22,663 withheld positive pixels; APRONRIDGE free1d `0.008354`, 95% CI `[0.006823, 0.010135]`. This is a local hide-and-recover result, not a competition score. See its [run card](../evidence/apronridge_run_card.json).
- **Format check:** after installing the pinned `requirements.txt`, 199 tests passed; `scripts/check_site.py` passed for 25 served rasters; the 8-entry manifest and pinned R0 parent verified. These confirm local integrity only—not public uniqueness or organizer acceptance.
- **Submission ledger:** 57 BUILT / 0 RECEIPT (current command output). No weekly slot was used in this review.
- **Current session generated no TIFF and ran no geological experiment.** The requested new unique candidate remains unmet: the binding final-dot duplicate stop prevents honest promotion under the literal rule. Do not relabel an existing file or emit an all-zero/no-signal raster to evade the stop.

## Next actions (fail-closed order)

1. Preserve the literal registry stop. No candidate construction or placement until the protocol's treatment of full-footprint continuous probability rasters is formally resolved; do not locally exempt them or silently change the `>70%` threshold.
2. Once a policy resolution is authorized, restore/check the cached feature stack and available registry; pre-register one method lane, compare its actual continuous surface before placement, run single-feature leakage canaries, then whole-segment buffered `gems57-pooled-hide-v2` validation with `vendor/gems57/evaluate_holdout.py`. Keep within the 3-experiment / 2-hour cap.
3. Only if holdout best is beaten under the registered comparison, emit one candidate via the shared `vendor/gems57/submission_writer.py`, validate independently, and run final-dot uniqueness against a refreshed registry. Promotion to any real slot is a separate selector decision; no slot is selected here.
4. Obtain an `ORGANIZER-CONFIRMED` receipt only after a candidate is explicitly cleared and uploaded by the authorized account holder; record its exact portal receipt. No organizer receipt or current leaderboard was obtained in this review.
5. The full training feature stack (`training_features.tif`) is absent from this checkout's staged `data/`; `data/` currently contains only bridge/template and parent rasters. The user-provided competition data page is login-gated per prior repository records. Do not claim a fresh official download or training run until the official source is accessible and provenance/use terms are checked.

## Prioritized Remaining Blockers & Future Work

### Prior automated review — 2026-10-24 UTC
1. Preserve the literal registry stop; [fresh exact-file check](downloads/review_20261024_springalign_witness_v2.json) proves SPRINGALIGN fails and the witness halo covers the whole footprint.
2. An authorized protocol resolution is required before any candidate can be cleared for upload. Do not silently exempt dense rasters or change the >70% rule. See [prior review](REVIEW_AUTOMATED_20261024.md).

# Prior NEXT_STEPS — after the 2026-10-24 ANASIG session
### Priority 0 — Human Operator / Selector Decisions (Cannot Be Resolved Autonomously)
1. **Dense-Surface Representation Policy Decision (`17GEMSDOE E-proba-multiscale`):**
   - `17GEMSDOE_E-proba-multiscale` (`5,167,373` positive footprint cells = `100%` of footprint) makes literal 3-px forward overlap equal `1.000` for **every** nonempty in-footprint raster.
   - If the human operator scopes the 3-px dot-overlap uniqueness rule to sparse dot-set candidates (`<= 150,000` positive pixels, `<= 2.9%` of footprint) while retaining `|Spearman rho| <= 0.90` on all `1,332` rasters (`max = 0.4396`), `HYDROCONDUIT f45hydro` (`c9e07ba6…`) already passes every uniqueness, format, canary, and static-holdout gate. Until that explicit human policy update, keep `submission_eligible: false`.
2. **Blocker 0 — Obtain First `ORGANIZER-CONFIRMED` Submission Receipt:**
   - `ledger/submissions.csv` now holds `49 BUILT` rows and `0 RECEIPT` rows. Recording even one organizer submission-page receipt (e.g. confirming `R0 = 0.2778` or testing one selector-cleared candidate) is the only way to calibrate whether DrivenData's hidden test set aligns closer to Quaternary piedmont/geothermal recovery (`HYDROCONDUIT`) or exposed bedrock mapping (`BREAKLINE` / `SGMC`).

### Priority 1 — External Data Acquisition (Blocked by Sandbox Network Policy)
3. **1 m USGS 3DEP LiDAR Micro-Scarp + Lake Lahontan Shoreline Mask (Hypothesis #5 in `HYPOTHESES_20261024_HYDROCONDUIT.md`):**
   - In an environment with outbound access to `apps.nationalmap.gov` / DrivenData's `1m_DEM_links.csv` and orthometric (AMSL) elevation tiles, extract sub-meter alluvial scarp doublets and mask Pleistocene Lake Lahontan highstand (~1330–1338 m AMSL) and recessional beach ridges (which cannot be isolated from detrended `Band 12` alone).

### Priority 2 — Methodological Next Steps (In-Stack, No External Access Needed)
4. **Resolve the Static vs Fold-Visible (`d_visible > 2.0`) Holdout Gap:**
   - Our new `fold_visible_rule2` diagnostic (`scripts/report_hydroconduit_proxies.py`) showed `100% H19-5` (`d_visible > 2.0`) reaches `0.0968` vs `0.0852` when `45%` of dots are forced `> 300 m` off `H19-5`. Test whether **2D Coulomb transtensional slip + dilation tendency** (`Bands 4, 7, 8` projected onto joint `Band 12 + Band 2 RTP` fault normals, Hypothesis #4) or **blind geothermometer strike bridges across MT clay-cap lateral gradients** (`||\nabla \text{Band 17}||`, Hypothesis #3) lifts **both** fold-visible `d_visible > 2.0` `HOLDOUT-DTI` **and** `SGMC` `PROXY` simultaneously.

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
### Parallel-Session Benchmark Update (`PIEDFRONT` + `STEPEDGE` + `review_20261024`)
- **`PIEDFRONT f35Ptop`** (`GEMSDOE92-PIEDFRONT-f35Ptop-20261024`, `docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif`, SHA-256 `e314f4c004927ff56334827b4d45c57fc62da3da3010c12682d7cce6d0f185a8`): static `HOLDOUT-DTI = 0.006425 [0.005375, 0.007479]`, `SGMC = 0.059993`, `verdict: negative` (**OK TO DOWNLOAD**, **DO NOT SUBMIT**). `HYDROCONDUIT f45hydro` (`0.008549 [0.007626, 0.009487]`) improves over `PIEDFRONT f35Ptop` by `+33.1%` (`+0.002124`) while overlapping only `56.56% <= 70%` within 3 px (`phi = 0.2000`).
- **`STEPEDGE f60Sraw`** (`GEMSDOE92-STEPEDGE-f60Sraw-20261024`, `docs/downloads/h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif`, SHA-256 `c5dc98f2846ae486e022a7bdae1840334e73c03af44c03e9867c03b6f16d07b4`): static `HOLDOUT-DTI = 0.003980 [0.003295, 0.004702]`, repo-best `SGMC = 0.141464`, `verdict: negative` (`42.35% <= 70%` 3-px overlap with `HYDROCONDUIT f45hydro`).
- Ledger total across all merged sessions: `54 BUILT / 0 RECEIPT`.
