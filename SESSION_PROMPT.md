## Session start — 2026-10-26 GEMS site review (read first)

Read the README's **Durable project aim and session prompt** block, [`docs/SITE_REVIEW_20261026.html`](docs/SITE_REVIEW_20261026.html), [`docs/HYPOTHESES_20261026_SITE_REVIEW.md`](docs/HYPOTHESES_20261026_SITE_REVIEW.md), and [`evidence/review_20261026_gemsdoe_sites_run_card_v2.json`](evidence/review_20261026_gemsdoe_sites_run_card_v2.json). The report preserves 17 verified source TIFF variants, nine selected site artifacts, all 36 pairwise comparisons, source commit pins, and format-only checks. GEMSDOE32 `.2778` is an owner-reported CLAIM with no organizer receipt. User snapshots `.4413` and `.3195` conflict with GEMSDOE32's owner-page `.4437`; the current official leader is unknown.

**This site review produced no new TIFF, experiment, holdout, leakage canary, or weekly slot.** A separate BLINDEXT research TIFF is present on upstream main; its run card reports one experiment, no HOLDOUT-DTI result, a duplicate stop (`1.000` literal overlap and `|rho|=1.000`), zero slots, and no submission clearance. It is downloadable for research only, not a unique candidate. The pinned 17GEMSDOE witness is positive on all `5,167,373` finite sample-footprint cells, so any nonempty candidate has literal overlap `1.000 > 0.70`. All nine reviewed target masks also fail pairwise uniqueness against at least one other target. Stop before feature generation/placement; do not submit any linked historic or BLINDEXT TIFF. The previous `evidence/review_20261026_gemsdoe_sites_run_card.json` is a retained but superseded record because it inherited stale readiness counters; use v2, whose counters correctly say `false / 0 / 0`. No distinct method paragraph was supplied, so historical lane paragraphs do not authorize a new experiment. Maximize P(Win); Own the Outcome.

---

## Historical session start — 2026-10-25 audit (superseded)

Read the README's "Session request — 2026-10-25" block, then [`docs/REVIEW_20261025_AUDIT_AND_HYPOTHESES.md`](docs/REVIEW_20261025_AUDIT_AND_HYPOTHESES.md) and [`evidence/review_20261025_audit_run_card.json`](evidence/review_20261025_audit_run_card.json). Earlier readiness audit (still valid): docs/REVIEW_20261025_SESSION.md. Current verified state: research downloads only; DO NOT SUBMIT; No new raster was generated this session; 0 of 3 experiments; 0 slots. The literal duplicate rule cannot be satisfied by any in-footprint raster (the public 17GEMSDOE witness is positive on all 5,167,373 footprint cells). Five operator decisions (D1–D5) block promotion; an agent may not decide them silently. The official rules say outside-bounds values should be null or NaN; this repo's gate requires zeros (D2). Leaderboard snapshots remain unverified; do not state a current official leader. GEMSDOE32's 0.2778 is a CLAIM with no receipt.

---
## Current review & TILTANGLE audit addendum — 2026-10-25 (`arena/151c397c-gemsdoe92`)

Read [`docs/REVIEW_20261025_ARENA_151C397C.md`](docs/REVIEW_20261025_ARENA_151C397C.md), [`evidence/tiltangle_audit_20261025.json`](evidence/tiltangle_audit_20261025.json), and [`docs/downloads/review_20261025_151c397c_run_card.json`](docs/downloads/review_20261025_151c397c_run_card.json) alongside the live [VARIO status](docs/downloads/readiness.json). No new raster was generated in this review (`0 / 3` experiments, `0` weekly slots); `scripts/audit_readiness.py --fetch-witness` re-verified the pinned witness `17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` (`5,167,373 / 5,167,373` positive footprint cells -> literal 3-px forward overlap `1.0000 > 0.70` STOP). Audited and remediated the merged `TILTANGLE` artifact (`f17eae78…`): its reported `0.033466` static figure used full-catalogue `d_pref` (including withheld faults; leakage canary symmetric `AUC = 0.962399 > 0.90` FAIL) and collided at `0.776332 > 0.70` with `NETEXPAND netexpand`; leak-free recomputation via `vendor/gems57/evaluate_holdout.py` (`22,663` withheld positives) gives `0.005272 [0.003839, 0.006810]` (pure `S` static) and `0.085247 [0.072752, 0.098193]` (strict fold-visible Rule-2 with visible-only `d_pref`).

## Repository-review addendum — 2026-10-25 (`78db3076`, reconciled with newer main)

Read [our three-pass review](docs/REVIEW_20261025_78DB3076.md), [conditional hypotheses](docs/HYPOTHESES_20261025_78DB3076.md), and [final JSON audit](docs/downloads/session_78db3076_run_card.json) alongside the live [VARIO status](docs/downloads/readiness.json). This audit itself generated no TIFF, holdout, geological experiment or weekly slot. Concurrent main promoted a different VARIO **research** download to the site primary; it remains **DO NOT SUBMIT**, with local HOLDOUT-DTI and a failed sparse-registry comparison, not an organizer score. The literal dense-witness stop still applies. Never treat the earlier LISTRIC snapshot card as proof of current primary bytes. A main-merge orphaned HALO TIFF failed the catalogue distance gate and was quarantined outside the Pages downloads; the shared site checker stays fail-closed. Read the README and this brief at every start. Maximize P(Win); Own the Outcome.

## Current review addendum — 2026-10-26 (session `977778c1`)

Read `docs/REVIEW_20261026_SESSION_977778C1.md` + `evidence/review_20261026_977778c1_run_card.json`. Three-pass review only: no TIFF, experiment, holdout, or slot. Fixed 3 pre-existing failures on main (README contract phrase, unlinked served TILTANGLE TIFF, missing `<main>` in tiltangle.html): **542 tests passed**, site check PASS (93 rasters). Binding literal dense-witness stop still applies; submission-cleared unique TIFF remains unmet; all brief scores remain CLAIM. Next: protocol owner must resolve the literal-rule policy; ensure site-contract tests gate CI.

## Current lane addendum — 2026-10-25 (`RIEDELVALVE`, branch `arena/babe7a99-gemsdoe92`)

Read `docs/ANALYSIS_20261025_RIEDELVALVE.md`, `docs/HYPOTHESES_20261025_RIEDELVALVE.md`, and `evidence/riedelvalve_run_card.json`. `RIEDELVALVE` (transtensional Riedel $R/R'$ shear obliquity + bimodal $\sqrt{\lambda_1\lambda_2}$ fracture nodes + slope-partitioned USGS 3DEP 10 m scarp + bedrock knickzone + Tufa-filtered DOE GDR `#1391` INGENIOUS fault-valve + additive `@ 0.30` N90K secondary skeleton; `gems/riedelvalve.py`, `scripts/run_riedelvalve.py`) generated 3 format-valid (`11/11` gates PASS in `[0, 1]`, `0` NaN) byte-unique GeoTIFFs (`3/3` experiments, `0` slots). Primary `gemsdoe92-riedelvalve-riedel_n90k-90000-20261025-e57353de-zeros.tif` (SHA-256 `75d61cb1e548c27c1fa8804a124287996241988f715cb50f3c65c468cb3bc1e0`) confirms the additive `37,654@1.0 + 52,346@0.30` Tversky tail with `95% CI > 0` (`+0.000875 [+0.000531, +0.001215]` static `HOLDOUT-DTI` vs matched-surface binary `riedelvalve` `0.008180`, reaching `0.009054 [0.007829, 0.010290]` static and `0.108593 [0.095583, 0.120981]` strict Rule-2 on `gems57-pooled-hide-v2`, `22,663` withheld px; `32/32` canaries `<= 0.639492`), reaches **`0.112719` (`#1` among all `dual_reading_unique` LOQO lanes, beating `LISTRICLOQO` `0.103442` and `KNICKLOQO` `0.095878`)** on off-catalogue `USGS SGMC PROXY`, and passes both local (`<= 0.4702 <= 0.70`) and `102`-repo `dual_reading_decision` uniqueness (`0.6384 <= 0.70`), while cleanly falsifying Group-R Riedel obliquity on planar holdout (`-0.000092`, n.s.). Verdict `negative` (`OK TO DOWNLOAD FOR RESEARCH`, `DO NOT SUBMIT`: literal `17GEMSDOE` dense witness `1.000 > 0.70` and static `0.009054 < LISTRICLOQO 0.013295` / `KNICKLOQO 0.010788`).

## Current lane addendum — 2026-10-25 (`NETEXPAND`, branch `arena/a7cdad14-gemsdoe92`)

Read `docs/ANALYSIS_20261025_NETEXPAND.md` + `evidence/netexpand_run_card.json` first. NETEXPAND (KNICK30+LISTRIC4+FAULTNET-context5+ASA/coherence/curie/MT6 LOQO, pure crest) produced 3 format-valid (11/11 gates) byte-unique TIFs. Strict draw-blind HOLDOUT-DTI: netexpand_far 0.177976 [0.163109,0.193227], netexpand 0.146798, nocontext 0.115566 vs control_knick 0.109069 / control_knick_far 0.111601 (22,663 withheld; canaries <=0.7775). All arms verdict negative: Rule-1 lane duplicates vs FAULTNET/KNICKLOQO (0.76-0.81 > 0.70 local, 123 rasters); vs R0/H19-5 <=0.40 (not copies). 3/3 experiments used, 0 slots. GEMSDOE32 0.2778 re-verified live as UNSCORED CLAIM (no organiser score exists). Next: NETEXPAND-R repelled emission or GDR-GEOTHERMOMETER-FIELD (see hypotheses doc); operator must resolve dense-witness literal-rule policy (F2). Maximize P(Win); Own the Outcome.
## Current review addendum — 2026-10-25 (fresh readiness audit)

Start with the generated README decision, the [latest three-pass repository review](docs/REVIEW_20261025_ARENA_REPOSITORY.md), the [readiness audit](docs/REVIEW_20261025_SESSION.md), [ordered next steps](docs/NEXT_STEPS.md), and this full operating contract. Fresh local integration checks: **537 tests passed** (140 non-fatal Rasterio affine deprecation warnings); `scripts/check_site.py` gated 89 served rasters; both current-status render checks, pinned parent, manifest, ledger, and `git diff --check` passed. No new raster was generated in the readiness review; no geological experiment, HOLDOUT-DTI, organizer receipt, or weekly slot was produced by that review. Concurrent branch artifacts already present in main were not generated by this work and remain research-only. The literal pinned-witness overlap stop still binds; hypotheses remain conditional and unvalidated, and the full feature cache is absent. The requested submission-cleared unique TIFF remains unmet. Source limitations and unverified claims are documented in the linked reviews.

## Supplemental initial session follow-up — 2026-10-25 (`17:03:59Z` audit)

[Three-pass follow-up](docs/REVIEW_20261025_SESSION_FOLLOWUP.md) · [rejection-only run card](docs/downloads/session_followup_20261025_run_card.json). This timestamped audit produced no candidate raster, holdout, leakage canary, experiment, or slot and had no method paragraph assigned. Its rank-1 candidate is conditional, not an assigned lane. The audit-time inability to fetch DrivenData is historical: a later main-branch [leaderboard review](docs/ANALYSIS_20261025_LEADERBOARD.md) records a public top-50 snapshot; that is not a submission receipt for GEMSDOE32, whose `0.2778` remains a `CLAIM`. This is a supplemental record for that audit, not a replacement for the current review or later repository lane records below.

---

## Current session addendum — 2026-10-25 (MT-CHANGEPOINT lane, branch `arena/7f2e773e-gemsdoe92`)

Lane `MT-CHANGEPOINT` completed 3/3 pre-registered experiments (`docs/HYPOTHESES_20261025_MT_CHANGEPOINT.md`, `gems/mt_changepoint.py`, `scripts/build_mt_changepoint_submission.py`). Primary `gemsdoe92-mtcp-20261025T182129Z-mtcp-37654-zeros.tif` (SHA-256 `ad3bc4b7a8110c2b…`) is format-valid (`run_gates` 10/10 PASS, single-band float32, EPSG:32611, 3730×3292, values in [0, 1], nodata=None, 0 NaN anywhere, 0 on catalogue). Locally unique across 105 local registry rasters (surface worst |ρ| = 0.0642 ≤ 0.90; final-dot worst overlap = 0.3854 ≤ 0.70). Primary HOLDOUT-DTI `0.043936 [0.036431, 0.051261]` (gems57-pooled-hide-v2, 22,663 withheld positives, per-draw re-placement) is below the 0.113316 bar → **verdict negative, DO NOT SUBMIT, 0 slots spent**. Forensic analysis of GEMSDOE32's claimed 0.2778 score vs 0.4413 / 0.3195 leaderboard documented in `docs/ANALYSIS_20261025_MT_CHANGEPOINT.md`.

---

## CHILISTRIC session addendum — 2026-10-25 (`arena/2d4c152c-gemsdoe92`)

Read the fresh audit addendum above first, then `docs/ANALYSIS_20261025_CHILISTRIC.md`, `docs/HYPOTHESES_20261025_CHILISTRIC.md`, and `evidence/chilistric_run_card.json`. Lane `CHILISTRIC` (sub-pixel USGS 3DEP `10 m` scarp morphology + `10 m` fluvial `chi` disequilibrium + basement-depth-adaptive updip listric projection + paleo-sinter/`2 m`-probe/trimmed-GDR `#1391` fault-valve conduits + non-diluting additive secondary crest recall) completed `3/3` pre-registered experiments (`0` weekly slots spent, `44/44` Rule-4 leakage canaries PASS with `max symmetric AUC = 0.617275 <= 0.90`). Primary `docs/downloads/h33-h33-2-b2-CHILISTRICaddtail52k-20261025-8c82904d-zeros.tif` (`SHA-256 = 75fcc743420f817d841b9f822e82bf4e63c850ede29e0e2d75e54b26603acf50`, `52,000` crests in `{0, 0.65, 1.0}`, `11/11` automated format gates PASS) sets a **new all-time `GEMSDOE92` record on strict draw-blind OOF `d_cat > 2.0` (`HOLDOUT-DTI = 0.013208 [0.011537, 0.014860]`)**, sets a **new zero-catalogue crest record on independent off-catalogue `USGS SGMC` (`0.113149`, `+9.4%` vs `LISTRICLOQO selectcal`)**, reaches `0.013174 [0.011583, 0.014730]` static `d_cat > 2.0` (`+0.000968 [+0.000146, +0.001793]` vs `no10m_fixed` ablation), and passes operational uniqueness across all `1,503` public rasters in `102` repos (`0 / 1,503 > 0.70`, max `0.635115 <= 0.70`). Because the literal `17GEMSDOE` full-footprint dense witness (`1.0000 > 0.70`) and static `d_cat > 2.0` point-estimate gate (`0.013174 < 0.013295`) remain binding, **`verdict = "negative"` and `submission_eligible = false` (OK TO DOWNLOAD FOR RESEARCH · DO NOT SUBMIT)**. Eight fabricated SHA-256 hashes in `ANALYSIS_20261025_LISTRICLOQO.md` and pixel/algebra errors in `ANALYSIS_20261025_VENTSCARP.md` were caught and corrected (`IRREGULARITIES.md`).

---

## Current session addendum — 2026-10-25 (leaderboard research, branch `arena/09f84f2f-gemsdoe92`)

Parallel leaderboard lane (merged after the fresh audit below; read the fresh audit first, then this). Read `docs/ANALYSIS_20261025_LEADERBOARD.md`. Facts established this session: the live DrivenData top score is `0.4413` (#1 xiaofanhu, not a GEMSDOE entry); `0.3195` is not on the top-50 snapshot; `0.2778` (GEMSDOE32) remains `CLAIM receipt=N`. The official rules (NLR PDF, Sept 2026) allow three submissions per week and require one final selection. The shared metric matches an independent naive implementation of the official equations (`tests/test_metric_independent.py`). The fresh witness audit re-confirms the literal universal stop (`evidence/readiness_20261025_leaderboard.json`). Five hypotheses are pre-registered in `docs/HYPOTHESES_20261025_LEADERBOARD.md`; none is built. Experiments used: 0 of 3. The blocking decision (dense-witness policy) is recorded in the analysis, §5. Do not place dots until that decision is made.

---

## Current review addendum — 2026-10-25 (`797e507a`)
## FLEXMAG session — 2026-10-25 (parallel lane; read after the current audit above)

Lane `FLEXMAG` completed 3/3 pre-registered experiments (`docs/HYPOTHESES_20261025_FLEXMAG.md`, `gems/flexmag.py`, `scripts/build_flexmag_submission.py`). Primary `gemsdoe92-flexmag-20261025T165411Z-flexmag-37654-zeros.tif` (SHA-256 `8190e1d0…`) is format-valid and locally unique, but HOLDOUT-DTI `0.045554 [0.035846, 0.056751]` (per-draw re-placement) is far below the 0.113316 bar → **verdict negative, DO NOT SUBMIT, 0 slots**. Fresh facts: GEMSDOE32's own page (fetched 2026-10-25) calls h33-h33-2-b2 UNSCORED with NO ORGANISER SCORE; R0 lineage XOR identities re-verified. Read `docs/ANALYSIS_20261025_FLEXMAG.md`. The audit addendum above and the literal-overlap stop remain the current decision.

---

## Prior current review addendum — 2026-10-25 (`797e507a`)

Read `docs/REVIEW_797E507A.md` before older session-result addenda. This review generated no new TIFF and used no experiment or slot: a fresh pinned universal registry witness requires a stop. Preserve literal overlap, not matched-budget reinterpretations. The existing LISTRICDIP primary inherited from parallel main is research-only. Three public entry pages must have the generated authoritative status first; CI/Pages check byte pins and ordering. The unique-TIF objective remains unfulfilled. Persistent requirements in this file and the README are a normalized operating brief, not a verbatim user-message archive.

---

# Session prompt — GEMSDOE92


## Current review — 2026-10-25 (`f23ca2d2`)

Read the README's current-decision and persisted-brief sections first, then [REVIEW_F23.md](docs/REVIEW_F23.md). No new TIFF or geological experiment was generated. The literal overlap stop remains binding; historical matched-budget uniqueness does not supersede it. The shared validator now enforces the requested clearance radius without an automatic override. A byte-bound status feed and collapsed historical UI prevent old record claims from competing with the current decision. The prompt's new unique, submission-cleared TIFF requirement is still unmet. No new lane paragraph or organizer receipt was supplied. No weekly slot was spent.


Read this at the start of every session, together with `README.md`. The README is the short executive summary; this file is the durable project operating contract. Preserve the user's goals: a unique, easy-to-download submission GeoTIFF, automated format validation, transparent evidence, and no hallucinated claims.

## Current session status — 2026-10-25 (`RELAYCONDUIT`)

Completed pre-registered lane `RELAYCONDUIT` (`docs/HYPOTHESES_20261025_RELAYCONDUIT.md`, `gems/relayconduit.py`, `scripts/run_relayconduit.py`; 3/3 experiments, 0 weekly slots spent):
- Hero zero-catalogue arm `conduit_notip` (`docs/downloads/gemsdoe92-relayconduit-conduit_notip-37654-20261025-bb0e9f59-zeros.tif`, SHA-256 `b509537223cf333f463ebac6a527aa5beabde86201133317d8485584a742d7b9`, 37,654 binary dots, 11/11 format gates PASS in `[0, 1]`, 0 NaNs): passes **all** operative uniqueness gates across 101 local rasters (worst 3-px overlap `0.5070 <= 0.70`) and across 1,367 compatible external rasters in 102 public `*GEMSDOE*` repositories (worst operative 3-px overlap `0.6557 <= 0.70`, `0` violations; worst `<=50k`-dot overlap `0.4180`; worst surface `|rho| = 0.3154 <= 0.90`). Strict Rule-2 `HOLDOUT-DTI = 0.076416 [0.063889, 0.088770]`, static `d_cat > 2.0` `0.005733 [0.004823, 0.006714]` (beats `R0` `0.004006` and `LISTRICDIP` `0.005420`), off-catalogue `USGS SGMC PROXY = 0.106525` (beats `COULOMBLOQO` `0.089332`).
- Self-excluded tip-relay siblings `relay_conduit` (`0.184485 [0.169875, 0.198933]`, paired `+0.069008 [+0.053289, +0.084771]` over rebuilt `control_COULOMBLOQO_d32` `0.115477`; exceeds `FAULTNET netfar` `0.175147`) and `relay_delta` (`0.180061 [0.165231, 0.193562]`) passed local uniqueness (`0.6601`, `0.6233 <= 0.70`) and were automatically halted on 102-repo 3-px overlap (`0.7843`, `0.8364 > 0.70` vs `GEMSDOE53` 80k).
- `35/35` single-feature leakage canaries PASS (`max = 0.811014 <= 0.90`). Verdict: `negative` (`submission_eligible: false`; OK to download for research, DO NOT SUBMIT under the binding literal `17GEMSDOE` dense-surface rule `1.000 > 0.70` and separate weekly-slot selector). Newly supplied prompt claims recorded in `ledger/site_scores_claimed_20261025.csv` (`GEMSDOE91`: `0.1367`, `0.1823`; `GEMSDOE92` `listricdip-updip50`: `0.0255`). Full PhD analysis & `VENTSCARP` §1.3 irregularity corrections: `docs/ANALYSIS_20261025_RELAYCONDUIT.md`; Run Card: `evidence/relayconduit_run_card.json`.

## Current session status — 2026-10-25 (`LISTRICDIP`)

The newest completed lane is `LISTRICDIP`. Three research GeoTIFFs were generated. Static HOLDOUT-DTI for `updip50` is `0.005420 [0.004294, 0.006551]` (`gems57-pooled-hide-v2`, 22,663 withheld positives). It beats `R0` and loses to the stored holdout best (`KNICKLOQO` `0.010788`). Verdict `negative`. OK to download for research. Not OK to submit. Literal dense-witness overlap is 1.0. The `376a8469` note that no new TIFF existed applied to that review, not to this lane. The literal overlap gate is still binding. Read the run card `evidence/listricdip_run_card.json` before trusting any older banner that calls itself newest.

## Current binding clarification — 2026-10-25 (`376a8469`)

Read [the protocol-gate review](docs/REVIEW_376A8469.md) first. The literal overlap gate is binding for every raster. The later historical BLINDFAULT addendum claiming an automatic policy resolution is **superseded**: matched-budget overlap remains diagnostic only. A freshly pinned witness proves all nonempty candidates fail the unchanged rule. Stop rather than fabricate a new eligible TIFF. No new method lane was specified or tested in this review. Full operating requirements remain in the README's persistent session prompt and below; read both at every session start.

## FAULTNET closeout — 2026-10-25 (read with the clarification above)

FAULTNET (catalogue-network context + COULOMBLOQO physics) holds the best **HOLDOUT-DTI** in the repository:
netfar `0.175147 [0.159756, 0.189860]` (gems57-pooled-hide-v2, 22,663 withheld positives) against the rebuilt control at `0.113890`.
It is **NOT** cleared, because its final dots are a literal rule-1 duplicate against over-budget dot fields (worst 0.7586,
GEMSDOE37 80k). A ridge-gated random null scores 0.4949, so the gate is specific. Do not waive it. The binding literal reading above stands.
Both readings fail. See `docs/ANALYSIS_20261025_FAULTNET.md`. The site's top block is rendered by
`scripts/render_current_submission.py` from `docs/downloads/current_submission.json`. Re-render it after any new run.

## Mission

Produce a **unique** GeoTIFF for DrivenData competition 306 (DOE GEMS Prize: hidden geothermal-related faults, NW Great Basin, EPSG:32611 100 m). The file must be obviously downloadable from the GitHub Pages site. Inspection and validation run in the project, without a human inspector in the loop. A human still performs the DrivenData upload and weekly-slot selection.

Study the prompt-reported GEMSDOE32 `h33-h33-2-b2` **CLAIM 0.2778** and other site values as learning context only. They are not ORGANIZER-CONFIRMED receipts unless a submission-page receipt is recorded in `ledger/`. A prior repository record says the official public leaderboard was read on 2026-10-24 and showed 0.4413 at #1 (LEADERBOARD-SNAPSHOT, not a receipt for GEMSDOE32 or GEMSDOE92); the prompt's 0.3195 is an older conflicting snapshot. Never say a local holdout beats a live competition score.

The goal is maximize the probability of placing well through reproducible science: collect public/official data where permitted, organize source and provenance, generate hypotheses, test using spatial holdouts, preserve negative results, and make an audited TIF easy to download. Keep Arena's core values explicit: **Maximize P(Win)** and **Own the Outcome**.

## Parallel-run protocol

1. **Lane.** Stay in one named method. Before placement, compare the prospectivity surface with the accessible registry; after placement, compare final dots. If absolute Spearman rank correlation exceeds 0.90 or more than 70% of dots fall within 3 px of one registry raster's dots, log it as a duplicate and stop. Never reinterpret the threshold to make a result pass. Report local inventory scope; local uniqueness is not proof of uniqueness across every site.
2. **Reuse.** Use the template's cached feature stack when it is actually available, `vendor/gems57/evaluate_holdout.py`, and `vendor/gems57/submission_writer.py` or the shared writer. Holdout = hide whole fault segments/components with a buffer; derive all catalogue-based features from visible faults only; mask visible faults pixel-exactly; pooled DTI α=0.2, β=0.8, 300 m triangular kernel. Fix a shared tool once in the template, never create a private fork.
3. **Label every number** as HOLDOUT-DTI (evaluator version, withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from submission-page receipt). CLAIM, MODEL, PROXY, and REGISTRY-MEASUREMENT must remain distinct. A projection is never written as a score.
4. **Leakage canary.** Test each feature alone on the holdout before trusting a result. AUC above 0.90 means leakage until investigated. Use the symmetric AUC if direction could reverse.
5. **Run card JSON:** hypothesis; mechanism; named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster SHA-256; validator output (no NaN inside footprint, values in [0,1], CRS/shape/transform match); submission name + note ≤140 characters; verdict promote / negative. Negative results are deliverables.
6. **Budget.** Stop after 3 experiments or 2 hours. Do not pick submissions; promotion to a real slot is a separate selector step within the weekly cap.
7. **Hypothesis request.** Before implementing, rank 3–5 candidate geological hypotheses; for each identify layers, physical signature, why it could detect a fault absent from the catalogue, difference from this repo, expected value/cost, and required data. If new data are needed, name a free official source and verify availability before calling the candidate viable. Do not claim a source was retrieved if it was not.

## Site / download rules

- Zeros-outside encoding is the only submission download offered (portal error: `Predicted values must be in range [0, 1]`).
- Homepage must clearly say whether the file is OK to download **and** whether it is recommended for a weekly slot.
- Executive summary subpage explains the DrivenData form (file, name, note).
- No human inspection is needed for format validation (`scripts/check_site.py`, `gems.gates`, `gems57.validate`). Human upload and selector remain separate.
- Never silently change `nodata`, clip out-of-range values, or convert NaNs without a recorded rationale.

## Trusted source starting points

- Competition overview/problem: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Competition about: https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- Competition data: https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- DrivenData reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Competition rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- USGS GeoDAWN catalog: https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7
- GDR / INGENIOUS: https://gdr.openei.org/submissions/1391
- EPSG:32611: https://epsg.io/32611
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- Great Basin Center for Geothermal Energy: https://gbcge.org/current-projects/ingenious/
- USGS 3DEP: https://www.usgs.gov/3d-elevation-program

Competition data may be login-gated. Follow license and data-use terms; owner-mirror hash checks establish byte identity, not organizer authentication or redistribution permission.

## Current session result (2026-10-25) — `POISSONFLEX`

Lane **POISSONFLEX** (Poisson gravity–pseudogravity hydrothermal breakdown + hanging-wall basement rollover flexure + canyon knickpoint strike integrals + quadrant-deconfounded LOQO & nested visible-only OOF support; `gems/poissonflex.py`). Three pre-registered experiments (`poissonflex_eq`, `poissonflex_raw`, `poissonflex_opt`). Winning research file `docs/downloads/gemsdoe92-poissonflex-poissonflex_opt-45000-20261025-54255bcc-zeros.tif` (SHA-256 `37b18c200e84c77b39b07e527b17d4395968389aaf3ff0c175c71204b2065f9b`).

- **Previous-session next steps closed first:** `evidence/coulomb_loqo_dual_reading_selector.json` (`COULOMBLOQO standalone` worst matched-budget overlap `0.739842 > 0.70` across `1,321` non-self public blobs; `dual45` `0.722420 > 0.70` -> both `negative`) and `evidence/ne_quadrant_loqo_collapse_diagnostic.json` (diagnosed `NE` geodetic truncation `B07` median `0.00` + `SW+SE = 62.8%` catalogue skew).
- **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 22,663 withheld positives: strict draw-blind `d_visible > 2.0`: `poissonflex_opt` (`45,000` dots) **0.107466 [0.094158, 0.120431]** (beats `H19-5` `0.096757` by paired `+0.010709 [+0.002297, +0.018444]`, `COULOMBDM` `0.094496`, and `BLINDFAULT` `0.047896`; trails `COULOMBLOQO standalone` `0.113890` by `-0.006424 [-0.013250, +0.000170]`); `poissonflex_eq` `0.103768`; `poissonflex_raw` `0.102861`. Static `d_cat > 2.0`: `poissonflex_opt` **0.008824 [0.007601, 0.010081]** (`2.20x` `R0` `0.004006`). Off-catalogue `USGS SGMC PROXY` (`62,122` px): **0.120957** (`+35.4%` over `COULOMBLOQO standalone` `0.089332`).
- **Leakage canaries:** `32/32 PASS`, max symmetric AUC `0.616108 <= 0.90`.
- **REGISTRY-MEASUREMENT:** local `97` rasters PASS (worst 3-px overlap `0.6488 <= 0.70`, `|ρ| = 0.1674 <= 0.90`); `<= 80k`-dot public rasters across `102` repos PASS (`max = 0.6804 <= 0.70`); continuous surface `|ρ|` across `1,404` valid public blobs PASS (`max = 0.4668 <= 0.90`); `100k–126k`-px public rasters under `150k` dot-field cap STOP (`0.7541 > 0.70` on `62GEMSDOE ventcons`).
- **Validator:** `10/10` `gems.gates` + `13/13` `gems57.validate` PASS; all finite `[0, 1]`; zeros outside; `EPSG:32611` `3730×3292`.
- Verdict: **negative**. Format-valid / OK TO DOWNLOAD FOR RESEARCH. **DO NOT SUBMIT.** 0 weekly slots used.

Hypotheses: `docs/HYPOTHESES_20261025_POISSONFLEX.md`. Analysis: `docs/ANALYSIS_20261025_POISSONFLEX.md`. Run card: `evidence/poissonflex_run_card.json`.

## Prior session result (2026-10-24) — `XPHASE`

Lane **XPHASE** (MT–gravity transverse-phase concordance; `gems/xphase.py`). Three experiments (`standalone`, `nophase`, `dual40`). Primary research file `docs/downloads/h33-h33-2-b2-XPHASEdual40-20261024-643553cf-zeros.tif` (SHA-256 `080018382de33758c78e1b11f80098a1f736ac7de5f4c55641bd84b52b0f7200`).

- **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 22,663 withheld positives: `dual40` **0.004653 [0.003955, 0.005390]**; `standalone` 0.003492; `nophase` 0.003487. R0 0.004006. COULOMB-LOQO standalone remains holdout-best at 0.009220.
- **Leakage canaries:** max symmetric AUC 0.553140 (Band 19) ≤ 0.90.
- **REGISTRY-MEASUREMENT:** local 74 rasters, worst 3-px overlap 0.4000 ≤ 0.70 (`dual40` vs H19-5); |φ| 0.2132. Literal public witness 17GEMSDOE E-proba-multiscale forward overlap 1.000 → stop.
- **Validator:** 10/10 MUST gates pass; all finite [0,1]; zeros outside; EPSG:32611 3730×3292.
- Verdict: **negative**. Format-valid / OK TO DOWNLOAD FOR RESEARCH. **DO NOT SUBMIT.** 0 weekly slots used.

Hypotheses: `docs/HYPOTHESES_20261024_XPHASE.md`. Analysis: `docs/ANALYSIS_20261024_XPHASE.md`. Run card: `evidence/xphase_run_card.json`.

## Prior session result (2026-10-24)

One candidate method was tested: R0-excluded visible-fault collar. Builder: `scripts/build_visible_collar_submission.py`. It generated `docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif` and its run card is `evidence/visible_collar_run_card.json`.

- **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 8 buffered spatial folds, 22,663 withheld positives: candidate 0.046866 (95% CI 0.040216–0.053315); parent R0 0.004006 (0.003424–0.004690); paired difference +0.042860 (0.036122–0.049357). These are local holdout values, not competition scores.
- **Leakage canary:** visible-fault distance alone, symmetric AUC 0.745593 (<0.90).
- **REGISTRY-MEASUREMENT:** the initial local-only comparison passed on 14 rasters, but the expanded literal scan found 1,279 matching-grid rasters across 102 public owner repositories. Pre-placement and final overlap both reach 1.000000; 131 rasters exceed 70%. Worst |ρ| is 0.421367 / 0.492957, below the 0.90 stop, but overlap triggers the binding duplicate rule. The initial inventory came from GitHub API; the final comparison was repeated from SHA-verified cache after API rate limiting (no fresh API refresh). See `evidence/public_registry_uniqueness.json`.
- **Validator:** 10/10 local MUST gates pass; all finite, range [0,1], zero outside; EPSG:32611, 3730×3292, template transform.
- Verdict: **negative — duplicate under the literal registry rule; stop and do not submit**. No weekly slot was selected or used. The local result may reward recovery of mapped catalogue structure and does not prove discovery of new faults.
- The GeoDAWN training stack is not present in this checkout's local cache. The band-based hypotheses in `docs/hypotheses_visible_collar_20261024.md` remain untested.

The earlier TIPGAP FAR result (2026-10-24) is a separate negative deliverable; preserve it and its evidence. Do not overwrite historical evidence or mistake it for this session's primary.

## Addendum — parallel BREAKLINE session (2026-10-24, merged after the collar session)

A second session ran in parallel from the same base and DID restore the feature stack (`python scripts/restore_inputs.py`; the brief's `download_competition_data.sh`/`prepare_data.py` do not exist in this checkout). It tested the band-based lane **BREAKLINE** (Bands 12/19 DEM scarp-break coherence; `gems/breakline.py`, builder `scripts/build_breakline_variants.py`):

- Primary file `h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif` (sha256 `cd9c8a56…810e`), verdict **negative / NOT CLEARED**: HOLDOUT-DTI 0.004861 [0.004032, 0.005822], Δ vs R0 +0.000854 [+0.000300, +0.001423]; SGMC off-catalogue control +31% vs R0; canary max 0.6216.
- **Local-registry uniqueness:** worst 55.0% forward / |ρ| 0.547 vs parent R0 over 18 local rasters; vs the visible-collar candidate only 3.5% (φ≈0.001) — disjoint lanes. **It has NOT been through the 1,279-raster public scan** — run `scripts/audit_public_registry.py` on it before any future uniqueness claim beyond "local".
- Facts: R0 ⊂ SOLO ⊂ D2.8 ⊂ H19-5 exactly; bridge `sample_submission.tif` *is* the catalogue (60,988 px, geometry only); Band 18 is the only signed band; collar count 2,171 (float64 EDT). Emission: spaced top-L beat exact-DTI greedy by +0.000701 [+0.000321, +0.001161] — never deviate at build time from the screened selector. Do not retry BASEMENT-STEP (Band 15, SGMC AUC 0.378), pure-seismicity placement, radiometric K/Th gradients.
- One BREAKLINE dose total may ever be submitted (siblings share keeps; 3 SUPERSEDED greedy siblings in `ledger/`). Full record: `docs/ANALYSIS_20261024.md`, `docs/HYPOTHESES_20261024_BREAKLINE.md`, `evidence/breakline_run_card.json`. Ledger: 36 BUILT / 0 RECEIPT.

## Addendum — SCARPPOL/ANASIG session (2026-10-24, later)

Two lanes were run from `docs/HYPOTHESES_20261024_SCARPPOL.md` (screens for
gravity-crest, analytic-signal, hinge, strain, radiometric and spring
surfaces are recorded there; the 19-band stack was restored and SHA-verified
this session, so band hypotheses are no longer "untested for lack of stack"):

- **SCARPPOL** (fall-line signed second derivative, Bands 12/19): built
  f33/f38/f45. HOLDOUT-DTI f45 0.005315 [0.004387, 0.006418] beats BREAKLINE
  f45, but final dots overlap same-dose BREAKLINE at 0.900–0.913 → duplicate
  under rule 1, stopped. Keeps are >90% shared because the template
  keep-greedy is coverage-dominated — see IRREGULARITIES (this session) #1.
- **ANASIG** (analytic signal Bands 3/9/14; single f45 build): primary file
  `h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif`, SHA-256
  `68964bd6…f4d5`. HOLDOUT-DTI **0.004967 [0.004098, 0.005940]**, Δ vs R0
  +0.000961 [+0.000168, +0.001814], vs holdout-best RELIEF p10 −0.001078
  [−0.002034, −0.000112]; canary max 0.551113; SGMC PROXY 0.080556 < R0.
  Local uniqueness passes (24 rasters: worst forward 0.550, |ρ| 0.547;
  surface |ρ| 0.024). Public witness re-proven at 100% footprint-positive
  (`evidence/public_witness_anasig.json`).
- Verdict **negative / NOT CLEARED**; format-valid ✅ OK TO DOWNLOAD on the
  homepage, with the slot block stated in the first banner. Ledger now has
  3 SCARPPOL + 1 ANASIG BUILT rows added this session; still 0 RECEIPT.
  Next actions: `docs/NEXT_STEPS.md` (top section).


## Latest review: decisive BREAKLINE public witness

See [current review](docs/REVIEW_CURRENT.md). The queued public check now rejects BREAKLINE: 100% forward overlap with the hash-verified 17GEMSDOE full-halo raster. Every nonempty in-footprint candidate fails the current literal gate against this witness. This supersedes the pending-public-scan status above; the full registry was not rescanned. Zero new experiments or submission slots; resolve the policy before more placements.

## Follow-up registry stop (2026-10-24)

**2026-10-24 follow-up — BREAKLINE is now a confirmed duplicate under the literal registry rule.** A live, Git-blob-verified witness check compared one raster from 11GEMSDOE and five from 17GEMSDOE. BREAKLINE final dots have **100% forward 3-px overlap** with the dense 17GEMSDOE E-proba raster. This is REGISTRY-MEASUREMENT, not a competition score. The actual BREAKLINE pre-placement surface was not supplied and was **not checked**; no collar surface was substituted. A final-dot failure alone requires stop. No new experiment or TIFF was generated; no slot used. See [follow-up review](docs/REVIEW_REGISTRY_STOP_20261024.md) and [run card](evidence/breakline_registry_stop_run_card.json). **Download for research only; do not submit.**

## STEPEDGE session (2026-10-24) — read with NEXT_STEPS top section

- New primary download: `h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif`
  (SHA-256 `c5dc98f2…07b4`): aperture-persistent sustained DEM steps (Band 12,
  no coherence gate), 22,592 far dots >3 px off H19-5 and off BREAKLINE/SCARPPOL
  f45 far dots + 15,062 greedy-kept R0. HOLDOUT-DTI **0.003980 [0.003295,
  0.004702]**, Δ vs R0 −0.000026 [−0.000534, +0.000458]; SGMC **0.141464**
  (repo best); canary 0.5797 (max 0.6216 control). Literal-unique vs 28 local
  dot rasters (surface |ρ| 0.138; final 0.461/0.396); dense-witness literal
  overlap 1.000 disclosed (ρ 0.0004). Verdict **negative** (holdout bars fail),
  `submission_eligible: false` by automated gates; f33/f45 siblings are
  duplicates — never submit. Ledger: +3 BUILT, still 0 RECEIPT.
- R0 forensics: CLAIM 0.2778 = spacing→kernel radius + d_cat>2 clearance on a
  fixed skeleton (`evidence/r0_forensics_20261024.json`). Shared-tool fix:
  `gems/metric.py` now implements official DTI (was returning up to 5.0).
  Leaderboard fetched 2026-10-24: #1 0.4413 (LEADERBOARD-SNAPSHOT).
- Analysis `docs/ANALYSIS_20261024_STEPEDGE.md`; run card
  `evidence/stepedge_run_card.json`. Budget spent (3 experiments).

## Current request/review addendum — 2026-10-24 UTC

Read the README's current automated review before all historical run records.
The user's repeated highest-priority request remains a genuinely unique,
one-click downloadable TIFF with autonomous in-project validation, no copied
submission passed off as new, explicit download/submission status, geological
hypotheses ranked before experiments, no invented live score, maximum three
experiments/two hours, and no weekly slot without separate selector clearance.
The new review confirms a binding dense-witness universal overlap stop; no new
TIFF may honestly be promoted under the unchanged rule. This is a limitation,
not successful completion of the requested new-TIFF generation. Preserve the
negative result and exact old bytes, and follow `docs/REVIEW_AUTOMATED_20261024.md`.
The inherited SPRINGALIGN filenames are future-dated relative to today's UTC
date; do not use their dates as proof that this review generated them.

## Addendum — HYDROCONDUIT session (2026-10-24)

Pre-registered 5 untried geological hypotheses (`docs/HYPOTHESES_20261024_HYDROCONDUIT.md`) after discovering `Band 6 tc` is Radiometric Total Count (`r = 0.99714` with `GeoDAWN TC`), `GDR #1391` `'Hot '` whitespace + `419` blind chemical-geothermometer pixels (`>= 80 °C`), and `BREAKLINE`'s `74.8%` bare mountain range-core cliff hijack. Built 3 `HYDROCONDUIT` variants (`gems/hydroconduit.py`, `scripts/build_hydroconduit_variants.py`):

- **Primary file:** `docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif` (`sha256 c9e07ba6627672bfd58b08572a19d48aa16ff07a2f95347993550eaaccba8fdd`, `37,654` unit-mass dots).
- **HOLDOUT-DTI (`gems57-pooled-hide-v2`, `22,663` withheld positives):** **`0.008549 [0.007626, 0.009487]`** — first candidate in `GEMSDOE92` to beat **both** `R0` (`0.004006`, `+113.4%`, Δ `+0.004543 [+0.003770, +0.005315]`) **and** prior holdout-best `RELIEF p10` (`0.006045`, `+41.4%`, Δ `+0.002504 [+0.001795, +0.003222]`). Rule-2 fold-by-fold `d_visible > 2.0` diagnostic (`0.0852` vs `0.0968` `H19-5` skeleton-only) and `USGS SGMC` proxy (`0.0741` vs `0.0961` `R0`) are disclosed alongside.
- **Leakage canaries:** all 24 raw/derived features `<= 0.90` (`max = 0.65012`).
- **Uniqueness (`REGISTRY-MEASUREMENT`):** Local (`29` rasters): pre-placement surface `0.1892 <= 0.70` (`|rho| = 0.1098`), final dots `0.5500 <= 0.70` (`|rho| = 0.2982`). Live 102-repo GitHub API scan (`1,332` rasters, `evidence/hydroconduit_public_registry_uniqueness.json`): **0 / 1,147 sparse (`<= 150k` px) public rasters exceed 70%** (`max = 0.6719 <= 0.70`; `|rho| <= 0.4396`), while `118` dense surfaces (`> 150k` px, led by `17GEMSDOE E-proba-multiscale`, `100%` footprint positive) yield `1.000 > 0.70` under the literal rule.
- **Verdict:** **`negative` (`submission_eligible: false`) — ✅ FORMAT-VALID / OK TO DOWNLOAD FOR RESEARCH; ⛔ DO NOT SUBMIT / NOT CLEARED FOR A WEEKLY SLOT** until a human operator resolves the dense-surface representation policy. Ledger: `49 BUILT / 0 RECEIPT`.

The inherited SPRINGALIGN filenames are future-dated relative to today's UTC
date; do not use their dates as proof that this review generated them.

## Tooling review follow-up — 2026-10-24 UTC

A shared gate defect was fixed: the generic outside-footprint validator previously classified infinities as NaNs. `gems.gates.run_gates()` now rejects infinity and every other nonzero finite value outside; its explicit `require_submission_encoding=True` mode requires the whole raster to be finite and within `[0,1]`, with zeros outside. The public `python -m gems validate` CLI and site check always use the strict mode; there is no permissive CLI override. Historic NaN-outside artifacts may still be inspected through the generic research API, but they are not upload-safe under project policy. No raster or old receipt was changed.

The detailed prior review is [`docs/REVIEW_20261024_SESSION.md`](docs/REVIEW_20261024_SESSION.md), with machine-readable card [`evidence/repo_review_run_card_20261024.json`](evidence/repo_review_run_card_20261024.json) (served mirror: [`docs/downloads/repo_review_run_card_20261024.json`](docs/downloads/repo_review_run_card_20261024.json)); the D97 documentation review is summarized at the top of [`docs/REVIEW_CURRENT.md`](docs/REVIEW_CURRENT.md). Four conditional, unvalidated hypotheses are listed in [`docs/HYPOTHESES_20261024_PREFLIGHT.md`](docs/HYPOTHESES_20261024_PREFLIGHT.md); they are not cleared to build or score. No new geological experiment, candidate feature surface, TIF, holdout, or submission slot was produced/used. Keep downloads explicitly research-only. The unique-TIF requirement remains unfulfilled; do not bypass the literal threshold.

## Continuation review — 2026-10-24 UTC

See [`docs/REVIEW_20261024_CONTINUATION.md`](docs/REVIEW_20261024_CONTINUATION.md), run card [`evidence/review_20261024_continuation_run_card.json`](evidence/review_20261024_continuation_run_card.json), and exact-file witness receipt [`evidence/current_witness_recheck_20261024.json`](evidence/current_witness_recheck_20261024.json). The existing APRONRIDGE file was freshly compared with the Git-blob-verified 17GEMSDOE E-proba raster: the witness is positive across all 5,167,373 footprint pixels, so the existing file's forward 3-px overlap is `1.0`. This is a single-witness rejection, not a new full-registry or candidate-surface scan. No new TIF, experiment, holdout result, placement, or slot was created. Historical APRONRIDGE and HYDROCONDUIT HOLDOUT-DTI values are static records, not rerun or certified here as fold-rebuilt/leak-free promotion evidence and not organizer scores. At that continuation review time, the feature stack and official provenance/licensing were not ready in the checkout. Subsequent main-branch work added the separate GEOTENSION experiment (three variants): the recorded free1d HOLDOUT-DTI is 0.007615 [0.005832, 0.009386] (gems57-pooled-hide-v2, 22,663 withheld positives), below APRONRIDGE and HYDROCONDUIT; its exact-file dense-witness overlap is 1.0, so it remains negative and not submission-eligible. See docs/ANALYSIS_20261025_GEOTENSION.md and evidence/geotension_run_card.json. That addition does not change the continuation's historical scope, the APRONRIDGE/HYDROCONDUIT caution, or the literal duplicate stop. A subsequent main-branch COULOMB session also added three format-valid research variants; its lead `seismo` **HOLDOUT-DTI** is `0.005808 [0.004846, 0.006809]` (`gems57-pooled-hide-v2`, 22,663 withheld positives), still below the documented promotion bar and with the same `1.0` dense-witness overlap. It used no slot and remains a negative research result; see `docs/ANALYSIS_20261024_COULOMB.md` and `evidence/coulomb_run_card.json`. These later artifacts do not authorize a selector choice or alter the four preflight hypotheses. Preserve research-only download status and do not bypass the literal uniqueness gate. Read the README, this complete session contract, and the current review at each session start.

## Addendum — COULOMBDM session (2026-10-24)

Pre-registered 5 untried geological hypotheses (`docs/HYPOTHESES_20261024_COULOMBDM.md`) and implemented zero-label `COULOMBDM` (`gems/coulombdm.py`, `scripts/build_coulombdm_variants.py`, `scripts/report_coulombdm_proxies.py`, `scripts/emit_coulombdm_run_card.py`): 2D Mohr–Coulomb dilatant shear (`Bands 4, 7, 8`) × 2D FFT upward-continued `Band 2 RTP` (`100/300/600 m`) + `Band 17` MT clay-cap edges + lateral `GeoDAWN K/Th, U/Th` contact gradients + `>= 80 °C` blind `GDR #1391` geothermometers along Canny cross-strike 1D NMS centrelines (`35 / 35` leakage canaries `<= 0.90`, `max = 0.640176`). Built 3 format-valid `[0, 1]` GeoTIFFs (`11/11` gates PASS):
- `h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif` (`sha256 = 44efd202e8b96b9812de4693bd7f1ed05afed28de7e2e9413f72bc139ff18b12`): static `HOLDOUT-DTI = 0.007816 [0.006994, 0.008644]`, `SGMC PROXY = 0.075208`.
- `h33-h33-2-b2-COULOMBDMcoulomb1d-20261024-826b2fb3-zeros.tif` (`sha256 = 510c3012f4866e8ea2f0debd0aba799a7b7765a4e18f0954d2d1067ddd01e172`, `0% H19-5`, `0%` catalogue supervision): Rule-2 fold-visible `d_vis > 2.0` `HOLDOUT-DTI = 0.094496 [0.085916, 0.102867]` (matching supervised `H19-5 = 0.096757` within 95% CI, below supervised LOQO `COULOMB-LOQO standalone = 0.113316` / `0.009220` static).
- Both pass all `58` local rasters (`<= 0.6796 <= 0.70`, vs `COULOMBLOQO` `<= 0.5448`) and **`0 / 1,181` sparse (`<= 150k` px) public rasters** (`max = 0.5859` on `coulomb1d`, `0.6796` on `s45coulomb55`), while literal dense witness `17GEMSDOE E-proba-multiscale` (`1.000`) keeps `verdict: "negative"`, `submission_eligible: false`, `0` weekly slots spent (`74 BUILT / 0 RECEIPT`).

## 2026-10-25 addendum (BLINDFAULT session) — items added to the operating contract from the latest user brief

- The brief now lists ~90 prior `GEMSDOE*` sites with their owner-reported scores (`0.0000 – 0.2778`), restates leaderboard `0.4413` (#1) and `0.3195` as `[CLAIM]` snapshots, and repeats: "A lot of sites mention inspection only and a human inspector, but the inspection needs to be done through the project and needs to be validated for submission without human intervention." **Consequence adopted:** the dense-witness uniqueness degeneracy is resolved inside the template (`#IR-92-DENSE-WITNESS-MATCHED-BUDGET`), not deferred to a human selector. Both literal and matched-budget readings are always printed.
- Required pre-build step restated: generate and rank 3–5 **untried** geological hypotheses (layers, signature/transform, why it catches a fault missing from the catalogue, how it differs from `gems/*.py`), validate the top one on the spatially-blocked holdout, and do not spend a weekly slot on anything that has not beaten the current holdout best (`COULOMBLOQO standalone 0.113316` on the strict draw-blind `d_visible > 2.0` instrument).
- Arena Core Values (Maximize P(Win); Own the Outcome) are the decision framework for every trade-off; negative results are deliverables and must be preserved with the same rigour as positive ones.
- Three passes per session (implement/verify → review/fix → recheck against the original request), then PR + merge to `main`, then list remaining work and limitations for the next session.

## Review7059163e — 2026-10-25

Start at the README's top decision and `docs/REVIEW_7059163E.md`. Fresh witness download/hash/grid/footprint verification still requires stopping before placement; no new TIFF or holdout. Preserve the existing normalized operating brief, not a claimed verbatim prompt. The shared supplementary Markdown renderer now repairs a current decision displaced by a prepended lane banner and rejects reversed markers. Archive future-dated “latest” claims rather than accepting their chronology. The Pages API reports built/legacy, but workflow-mode activation is still denied with HTTP 403; publication gating is not established for the live legacy site.

## 26 October 2026 closeout addendum
Read README and this brief each session. The owner requires nine-site executive tables, a genuinely new submission-ready TIFF, automated format/science/uniqueness gates, no unsupported leaderboard projections, three review passes, and PR plus merge. THERMOTILT did not meet promotion requirements. Its runner is disabled; critical protocol deviations are in the run card. Do not spend a slot or rerun this lane before shared nested-OOF and pre-placement checks are repaired and the literal registry stop resolved.
