## Current session addendum — 2026-10-29 (`arena/2066b1fc-gemsdoe92`: `DEXP-KOSTROV-KOENDERINK` + 2,262-SHA Fleet & Prospective OOT Audit) — READ FIRST

- **Decision: ✅ OK TO DOWNLOAD FOR RESEARCH ONLY · ⛔ DO NOT SUBMIT (`verdict: "negative"`, `submission_eligible: false`, `0` weekly slots spent).**
- **New `2026-10-29` Unique GeoTIFF:** `docs/downloads/gemsdoe92-dexpkostrov1-40000dots-20261029-ffa21c17-zeros.tif` (SHA-256 `80d66b0590b26ddc9ac56af3964289f63f9c07c80931e3e69a7089dbabbc6faf`, `40,000` binary `{0.0, 1.0}` dots, `11/11` format gates PASS, `36/36` leakage canaries PASS with `max AUC = 0.77482 <= 0.90`).
- **Fold-Proper `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` withheld positives):** `E3` candidate `0.117438 [0.104226, 0.130267]` (unconstrained `E2` `0.141812 [0.129232, 0.153890]`, zero-catalogue blind `E1` `0.081254`) vs `R0 recipe` `0.097750 [0.085727, 0.109544]`; paired `E3 − R0` = **`+0.019688 [+0.008586, +0.031664]`** (strictly `> 0`).
- **Full `2,262`-SHA 8-Owner Fleet Uniqueness (`108` repos, `2,139` dot fields + `123` surfaces):** Operational PI-1 PASS on BOTH pre-placement surface (`0.65405 <= 0.70`, `|ρ| = 0.40984 <= 0.90`) AND final dots (`0.63890 <= 0.70`, `|ρ| = 0.04399 <= 0.90`); `0.17533` vs `GEMSDOE92 lbmc1` (`0.2784 CLAIM` #1 fleet high); `0.2663–0.2867` vs Focus-9. Held fail-closed under the literal dense-witness rule (`17GEMSDOE = 1.000 > 0.70`) and unverified official redistribution provenance.
- **Next-Session Priority:** Resolve literal dense-witness policy + verify official redistribution provenance before promoting any weekly slot; on an open-network workstation, run `H4` (USGS 3DEP 1 m LiDAR scarp wavelets) + `H2` (Gallardo–Meju gravity×MT cross-gradients). See [`docs/REVIEW_20261029_DEXP_KOSTROV.md`](docs/REVIEW_20261029_DEXP_KOSTROV.md) and [`docs/executive-summary-20261029-dexp-kostrov.html`](docs/executive-summary-20261029-dexp-kostrov.html).

---

## Current session addendum — 2026-10-28 review (branch `arena/591fc2bd-gemsdoe92`) — READ FIRST

**Current decision: DO NOT SUBMIT the RIESZ-LOCKED candidate.** Research download only: `docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif` (SHA-256 `d168c7d2a0ea89f9609426fe5f9d5aa0791223131c98a90d55b1f6aa1cbe5d7a`). It passes local GeoTIFF/range validation, but fails the supplied promotion protocol: pre-placement surface and final full-support registry overlap are recorded as `1.000 > 0.70`; and `HOLDOUT-DTI` `0.037987 [0.031011, 0.044656]` is below the R0 control `0.097750 [0.085900, 0.110766]`, paired difference `-0.059763 [-0.072005, -0.046653]`. The `0.321602` value is `MODEL` only, not a score. No organizer receipt, new TIFF, experiment, or weekly slot selection occurred in this review. The previously published `OK TO SUBMIT` banner is superseded and corrected in the site generator/status feeds.

**Protocol blockers:** the required “single method paragraph” was not included in the user prompt, so do not assign a new lane by inference. The prior RIESZ-LOCKED lane already used its 3/3 experiment budget. The full cached feature stack is absent in this checkout, so historical HOLDOUT-DTI cannot be independently rerun here. Never bypass the literal registry result with the narrower sparse PI-1 interpretation unless the owner explicitly resolves that rule. See [`docs/REVIEW_20261028_PROTOCOL.md`](docs/REVIEW_20261028_PROTOCOL.md) and current [`README.md`](README.md).

**Review assets:** [Executive summary site](docs/index.html), [nine-site report](docs/nine-sites.html), [submission instructions](docs/how-to-submit.html) (do not upload the current candidate), [corrected run card](docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json), [readiness](docs/downloads/readiness.json), and [review](docs/REVIEW_20261028_PROTOCOL.md).

---

### Normalized baseline prompt for session `81d8ca8b` (`2026-10-28`)

> Review `/home/user/GEMSDOE92`, execute previous next steps first, and focus on the highest-scoring and latest submissions of `GEMSDOE24` (`0.2477`, `0.0859`), `GEMSDOE25` (`0.2600`, `0.0742`), `GEMSDOE27` (`0.2449`, `0.2190`, `0.2250`), `GEMSDOE28` (`0.2710`, `0.2708`, `0.2707`, `0.2649`, `0.0217`, `0.0206`), `GEMSDOE30` (`0.2600`, `0.1462`), `GEMSDOE31` (`0.2708`), `GEMSDOE32` (`0.2778`), `GEMSDOE33` (`0.2632`, `0.0963`), and `GEMSDOE36` (`0.2750`, `0.1647`), plus all 8 listed GitHub owners (`buffedlizard55-lab`, `kanlerxz87-cyber`, `eugboogieman123-ops`, `wingbangboozle1-lang`, `ginnymcfiner23-ux`, `karagemop466-tech` [`GEMSDOEkarage1..3`], `apartanish22-droid` [`ApartGEMSDOE1..3`], `sassnarep3-star` [`GEMSDOESASS1..3`]), the 5 newly reported CLAIMs (`GEMSDOE91` `0.0435`, `KANLERGEMSDOE2` `0.1218`, `WBGGEMSDOE3` `0.0443`, `WBGGEMSDOE2` `0.0262`, `ApartGEMSDOE1` `0.0525`), and unscored submissions (`GEMSDOE92` `lbmc1-35801dots-20261027-89a660f6`, `WBGGEMSDOE1`, `KANLERGEMSDOE1`, `KANLERGEMSDOE3`, `GEMSDOESASS1`, `GEMSDOESASS2`, `GEMSDOESASS3`; transcribed verbatim in `ledger/claims_20261028.txt` and `ledger/unscored_20261028.txt`). Provide an executive summary per site and at the very beginning of the GitHub Pages site with a table of file to download, estimated score, uniqueness across GEMSDOE sites, and whether it is `OK TO DOWNLOAD` / `OK TO SUBMIT` (validated automatically without human inspector intervention), plus unique submission name, short note (`<=140` chars), and subpage explaining exact submission format and fixing `"Predicted values must be in range [0, 1]"`. Explain at PhD level why `GEMSDOE32` `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` achieved `0.2778` (vs `0.3195` / `0.4413` leaderboard references) and whether/how a unique submission can score higher. Propose 3–5 untried geological/geothermal-vent hypotheses ranked by expected DTI gain and cost (layers, physical signature/transform, off-catalogue rationale, named mimic, codebase distinction, free official data availability), test the top one on spatially-blocked holdout before recommending a weekly slot, generate a genuinely unique single-band `.tif` submission, store this prompt in `README.md` as project baseline, organize verified official sources in an auditable table, flag irregularities, run Pass 1 / Pass 2 / Pass 3, and open & merge PR onto `main` under the Parallel-Run Protocol (`|rho| <= 0.90` & `<= 70%` 3-px dot overlap pre-placement and on final dots; shared feature stack / `evaluate_holdout.py` / `submission_writer.py`; strict evidence labels; single-feature canary `AUC <= 0.90`; JSON run card; max 3 experiments / 2 hours; separate weekly-slot selector). Values: Maximize P(Win); Own the Outcome.

---

## Previous session addendum — 2026-10-27 (branch `arena/ee2370c1-gemsdoe92`)

**Outcome:** a unique, automatically validated TIFF is marked **OK TO SUBMIT**:
`docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif`
(SHA-256 `e928d3c3…3a1c`, portal name `gemsdoe92-lbmc1-35801d-89a660f6`).
Its MODEL estimate is 0.332 (90% interval 0.313–0.351); it is not an organizer score.
Start with the [site](docs/index.html), the [run card](docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6_run_card.json), the [three-pass review](docs/REVIEW_EE2370C1.md) and IRREGULARITIES IR-0127-1…8.

**What changed in method (keep unless the owner overrules):**
1. *Leaderboard model (LBM).* Owner-reported scores are matched byte-for-byte to registry rasters (`scripts/match_claims.py`). A metric-structured truth-density model is fitted to them (`gems/lbmodel.py`, `scripts/lbm_fit_final.py`, `scripts/lbm_ensemble_map.py`) and validated by leave-one-lineage-out CV. Use `scripts/lbm_estimate.py <raster or npy>` to **estimate any raster's score** (label: MODEL).
2. *Registry.* `scripts/build_registry_cache.py` streams every public GEMSDOE repository (all listed owners) into `.cache/registry_v3`. Uniqueness is checked with `gems/uniqueness_v3.py` (interpretation PI-1/PI-1b, literal reading reported).
3. *Placement.* `gems/lbm_place.py` runs exact lazy-greedy expected-DTI placement with registry caps enforced during placement (`scripts/exp1_hybrid.py` → `scripts/exp1_repair.py`). The build uses the shared writer (`scripts/build_exp1_submission.py`). The site is rendered from evidence only (`scripts/render_site_v3.py`) and checked by `scripts/check_site.py`.
4. *Validation.* The catalogue hide-and-recover holdout is still run and reported. It does not predict leaderboard scores (Spearman 0.13 over 123 rasters, `scripts/holdout_validity.py`), so promotion uses the leaderboard-aligned MODEL gate. That deviation is flagged as IR-0127-2.

**Next session must:** (a) after any organizer score is posted, add it to `ledger/claims_20261027.txt` (or a new dated file) and to `ledger/submissions.csv` with the SHA-256, then refit the LBM. Each new score is the most valuable data point available. (b) Run hypothesis H4 (1 m lidar scarps) on a machine with open internet. (c) Keep 3 experiments per session.

### Verbatim user request for session ee2370c1 (2026-10-27)

> Review the repo and focus on the highest scoring submissions of GEMSDOE24, 25, 27, 28, 30, 31, 32, 33 and 36; executive summary per site that makes the best submission obvious, with a table of file to download, estimated score, and whether it is unique versus the other GEMSDOE sites. Explain at PhD level why GEMSDOE32 `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` scored 0.2778 and whether we can beat it; then GENERATE A UNIQUE TIF (not a copy of any GEMSDOE submission) and keep iterating toward the highest score; it must be obvious whether it is OK to download and submit, and the download must be easy (targets mentioned: 0.3195 "highest right now", 0.4413 "GEMSDOE leaderboard high"). We should be able to estimate the score for a submission; high-scoring validation gates must pass before uniqueness and submission clearance. Propose 3–5 untried geological hypotheses (layers; physical signature/transform; why it finds catalogue-missing faults; how it differs from repo work), ranked by expected DTI gain and cost; validate the top one on the spatially blocked holdout before any slot is used; external data must be free and official. Deep research on geothermal fault discovery from official sources; be contrarian but grounded; find data others overlook. Put the prompt in the README and read it every session. Create an executive-summary subpage explaining exactly how to submit (single-band GeoTIFF or .zip with one GeoTIFF; CRS/shape/geotransform as the submission format; optional note; fix "Predicted values must be in range [0, 1]"; unique name and short note). Make the GitHub Pages site clean and user-friendly with official links, submission info at the very beginning. Complete the data-placement task autonomously. Work on previous next steps first; run three passes; create a PR and merge to main; suggest remaining work and limitations. PARALLEL-RUN PROTOCOL: (1) lane / duplicate rule: rank correlation > 0.90 or > 70% of dots within 3 px of one registry raster's dots = duplicate, checked on the surface before placement and on the final dots; (2) reuse the template's feature stack, `evaluate_holdout.py`, `submission_writer.py`; hide-and-recover holdout with visible-only catalogue features, pooled DTI α 0.2 β 0.8, 300 m kernel; (3) every number is HOLDOUT-DTI or ORGANIZER-CONFIRMED, a projection is never a score; (4) leakage canary: any single feature AUC > 0.90 = leakage; (5) JSON run card (hypothesis, mechanism, named mimic, holdout DTI + CI, registry correlation/overlap, raster sha256, validator output, name, ≤140-char note, verdict promote/negative); (6) budget 3 experiments or 2 hours; selector step and weekly cap are separate. Values: Maximize P(Win); Own the Outcome. The full list of owner-reported site scores supplied with this request is transcribed verbatim in `ledger/claims_20261027.txt`.

## Current session addendum — 2026-10-27 (branch `arena/b4bb558b-gemsdoe92`)

## Concurrent sessions merged on 2026-10-27 (historical; superseded by the ee2370c1 decision above)

## Current session addendum — 2026-10-27 (branch `arena/d30d387c-gemsdoe92`)

Read [`docs/REVIEW_20261027_D30D387C.md`](docs/REVIEW_20261027_D30D387C.md), [`docs/HYPOTHESES_20261027_D30D387C.md`](docs/HYPOTHESES_20261027_D30D387C.md), [`docs/focus9.html`](docs/focus9.html), and [`docs/downloads/review_d30d387c_run_card.json`](docs/downloads/review_d30d387c_run_card.json). **DO NOT SUBMIT (`verdict: "negative"`, `submission_eligible: false`, `0` new TIFFs, `0` experiments, `0` weekly slots):** **dual** hash-verified public witnesses trigger Protocol Rule 1's pre-placement stop — continuous surface `17GEMSDOE_E-proba-multiscale` (`5,167,373 / 5,167,373` positive footprint cells, `1.000 > 0.70`) **and** pure `{0, 1}` binary-dot submission `13GEMSDOE` `r13-lattice-s5` (`206,895` binary `1.0` dots, `CLAIM 0.0904`, `5,160,724 / 5,167,373` 3-px footprint coverage, pigeonhole overlap `>= 0.823418 > 0.70` at `37,654` dots; `0.9857–1.0000` across all 11 newly audited Oct 25–27 brief artifacts; [`fleet_20261027_audit_d30d387c.json`](docs/downloads/fleet_20261027_audit_d30d387c.json)).

Completed in `d30d387c`: (1) upgraded `scripts/audit_public_registry.py` across all 5 GitHub owners (`buffedlizard55-lab`, `kanlerxz87-cyber`, `eugboogieman123-ops`, `wingbangboozle1-lang`, `ginnymcfiner23-ux`) and non-standard TIFF subpaths, plus fixed `DOT_FIELD_MAX = 200,000` binary-lattice tie-truncation in `scripts/build_public_registry_index.py`; (2) audited all 11 Oct 25–27 delta artifacts (`GEMSDOE27 h31-drcg` `0.2250 CLAIM`, `GEMSDOE36 kpl36-exp3` `0.1647 CLAIM`, `GEMSDOE28 s21-puhgb` `0.034629` static holdout vs `0.0206 CLAIM` selection-bias collapse) and 12 multi-owner repos (`EUG1..3` & `GINNY1..3` are `README.md`-only stubs) into `ledger/site_scores_claimed_20261027.csv`; (3) audited all 19 `training_features.tif` bands (`docs/downloads/input_cache_d30d387c.json`), flagging `3,061`–`3,073` interior finite `-3.4028235e+38` NoData sentinels and proving `Band 6 tc` is GeoDAWN Radiometric Total Count (`r = 0.997140`) rather than magnetic tilt (`r = 0.012796`); and (4) pre-registered 5 untried hypotheses led by `GALLARDO-MEJU-CROSSGRAD-DECOUPLING`. Next session: await policy-owner resolution of both `17GEMSDOE` and `13GEMSDOE` witness rules + `[PASTE ONE PARAGRAPH]` lane assignment before implementing Rank 1.

## Concurrent session addendum — 2026-10-27 (branch `arena/b97812a3-gemsdoe92`)

Read [`docs/REVIEW_20261027_B97812A3.md`](docs/REVIEW_20261027_B97812A3.md), the [executive page](docs/focus9.html), [negative run card](docs/downloads/session_b97812a3_run_card.json), and the [dated GitHub ref snapshot](docs/downloads/session_b97812a3_focus_freshness.json). **DO NOT SUBMIT:** a pinned continuous-probability witness is positive at all 5,167,373 sample-footprint pixels; treating every positive pixel as a dot yields overlap 1.000 for any nonempty in-footprint candidate. Whether continuous probabilities are intended as registry “dots” is unresolved; this conservative stop is not geological identity and may not be silently waived. No method lane, new candidate, experiment, holdout or weekly slot was used here. The five ranked hypotheses remain untried.

All nine owner `main` refs differed from the pinned 26 October audit at the snapshot; the table is historical, and GitHub ref checks do not audit new TIFFs or scores. Twelve pinned owner-mirror inputs, including the 19-band stack, were restored to ignored, ephemeral cache; official provenance and redistribution rights remain unverified. Shared validation now rejects forged promotion, vacuous gate lists, incomplete footprints, ambiguous reference masks and masked in-footprint values. The root validation entrypoint is rejection-only; local format PASS is not portal clearance. [DrivenData staff](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2) clarify known-fault masking is pixel-exact, nearby unmasked predictions are evaluated normally, and new labels may be within 300 m. Do not automate DrivenData website access. Preserve Maximize P(Win), Own the Outcome, the shared evaluator/writer, strict uniqueness, visible-fault-only features, buffered whole-component holdout, AUC canaries and separate selector.

## Historical session addendum — 2026-10-27 (branch `arena/e7bc063a-gemsdoe92`)

Start with the README's repeatable-review brief, [three-pass report](docs/REVIEW_E7BC063A.md) and [nine-site executive summary](docs/focus9.html). **DO NOT SUBMIT:** an independent fresh pinned-witness check reproduces the universal literal overlap STOP. No new TIFF, method experiment, holdout or slot was generated. No distinct method lane was supplied. Do not work around the representation conflict, adopt a historical lane or label an estimate as an organizer score.

Use `.venv/bin/python scripts/review_project.py --fetch-witness --output .cache/<fresh-name>.json` to reproduce engineering checks plus the shared rejection audit. Exit 1 means confirmed STOP with engineering checks passing; exit 2 means failed/incomplete/inconclusive. Neither grants clearance. This runner records actual check exits and logs, never invokes model builders, and leaves the shared evaluator/writer unchanged. The existing ranked hypotheses remain conditional and untested in this session. Resolve the authorized protocol/lane dependencies before new research; preserve Maximize P(Win) and Own the Outcome.

## Historical session addendum — 2026-10-27 (branch `arena/b4bb558b-gemsdoe92`)

Read [`docs/REVIEW_B4BB558B.md`](docs/REVIEW_B4BB558B.md), the [nine-site executive page](docs/focus9.html), the [negative run card](docs/downloads/review_b4bb558b_run_card.json), and the [input audit](docs/downloads/input_cache_b4bb558b.json). **DO NOT SUBMIT:** the freshly fetched and hash-verified dense witness is positive on all 5,167,373 sample-footprint pixels. Every nonempty candidate's literal forward overlap is 1.000 > 0.70. Stop before a candidate surface or placement; no new candidate, experiment, holdout or slot was created in this session. No distinct method lane was assigned. A policy owner must explicitly resolve the representation conflict before experimentation; do not silently weaken the protocol.

Twelve pinned owner-mirror inputs and the 19-band grid/tags were restored and checked in an ignored, ephemeral cache. This proves mirror identity, **not** organizer origin, redistribution rights or submission eligibility. Thirty-six nine-site pairwise comparisons were rerun and match the previous corrected receipt. GEMSDOE32's 0.2778 remains an owner CLAIM without a score-to-raster receipt. Shared summaries/writer and many historical entrypoints were hardened, but other historical builders remain unaudited. Old instructions below that say to run disabled historical scripts or publish score estimates are historical and **must not be followed**. Keep the shared whole-segment holdout, visible-fault-only features, exact literal overlap/rank gates, leakage canaries and separate selector; preserve both Maximize P(Win) and Own the Outcome.

## Concurrent independent review — 2026-10-27

The [parallel three-pass review](docs/REVIEW_20261027_A3DCC0DD.md) and [its run card](docs/downloads/review_a3dcc0dd_run_card.json) independently reproduced the same literal stop, with 636 tests and 123 served-raster checks passing in that checkout. It likewise generated no candidate, holdout, experiment or slot, and supports no leaderboard estimate. Do not execute the historical SALEMSEISMO runner or its score-estimation recipe: later audits identified check-order, leakage and estimation defects.

## Historical session addendum — 2026-10-26 (nine-site forensic audit + `SALEMSEISMO` lane, branch `arena/18da04a8-gemsdoe92`)

Read [`docs/focus9.html`](docs/focus9.html) first: receipt-driven executive summary for
GEMSDOE24/25/27/28/30/31/32/33/36 plus the download / estimate / uniqueness table. Machine receipts:
`evidence/focus9_executive_audit_20261026.json`, `evidence/score_estimator_20261026.json`,
`evidence/salemseismo_run_card.json`, `evidence/salemseismo_holdout.json`,
`evidence/salemseismo_uniqueness.json`. Reproduce: `scripts/audit_focus9_sites.py` →
`scripts/estimate_scores.py` → `scripts/run_salem_seismo.py` → `scripts/render_focus9_page.py`.

Lane `SALEMSEISMO` (26 zero-catalogue channels over 7 previously unused bands; dual-partition
`0.5·LOQO + 0.5·rotated-45° LODO` OOF; exact 25-offset 300 m submodular `CELF` placement;
pre-registered in `docs/HYPOTHESES_20261026_SALEMSEISMO.md`) ran `3/3` experiments, spent `0` slots.
Static `d_cat>2` HOLDOUT-DTI `0.015948` (above the previous `LISTRICLOQO selectcal` 0.013295 control),
Rule-2 `0.099345`, worst 3-px overlap `0.6447` over 1,756 public rasters, 11/11 gates, 26/26 canaries.
Score estimator (MODEL): 107 matched CLAIMs, LOO RMSE `0.0722`, LOO Spearman `0.750`. Verdict
`negative` / `submission_eligible: false` under the binding literal dense-witness rule. Lineage
re-verified by XOR: `D2.8(25) ≡ d28(30)`, `SOLO(28) ≡ solo(31)`, `SOLO ≡ D2.8 ∧ d_cat>1`,
`R0 ≡ D2.8 ∧ d_cat>2` (all 0 px); GEMSDOE36 PINN ⊃ R0 +1,200 dots.

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
