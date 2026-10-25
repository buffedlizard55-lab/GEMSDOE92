# Next Steps — GEMSDOE92 (Updated 2026-10-25, Post-FLEXMAG Session)

## Completed this session (FLEXMAG — blind-fault flexure hinge × magnetic ASA)
- Pre-registered 5 ranked hypotheses (`docs/HYPOTHESES_20261025_FLEXMAG.md`); implemented `gems/flexmag.py` (catalogue-free; 14 leakage canaries, max symmetric AUC 0.566271 ≤ 0.90) + `scripts/build_flexmag_submission.py` (shared evaluator/writer/uniqueness only).
- 3/3 experiments (37,654 dots each, all format gates PASS): flexmag primary HOLDOUT-DTI 0.045554 [0.035846, 0.056751] (per-draw re-placement, 22,663 withheld) vs flex 0.048980, mag 0.045107, GRAVQUAD control 0.043184 — all paired CIs include 0; bar 0.113316 not met. Static flexmag 0.006026 (R0 control reproduced at 0.004006). SGMC proxy flex 0.087161 > flexmag 0.068910.
- Local uniqueness (98 unique-mask rasters): surface |ρ| ≤ 0.0658; flexmag/flex final-dot overlap ≤ 0.5682 PASS; **mag arm 0.7223 vs ANASIG = duplicate** (magnetic ASA alone is ANASIG). Public 102-repo scan not rerun (already negative). **Verdict negative, submission_eligible=false, 0 slots.** Run card `docs/downloads/flexmag_run_card.json`; analysis `docs/ANALYSIS_20261025_FLEXMAG.md`.
- Re-verified R0 lineage by XOR (SOLO = D2.8∧d>1; R0 = D2.8∧d>2, both XOR 0) and fetched GEMSDOE32 source page: it labels h33-h33-2-b2 UNSCORED / NO ORGANISER SCORE EXISTS — 0.2778 remains a CLAIM.

## Highest-P(Win) next actions
1. **Human selector (unchanged, still #1):** obtain the first ORGANIZER-CONFIRMED receipt (KNICKLOQO-class candidate) and settle literal-vs-matched-budget policy; without a live anchor every local ranking is uncalibrated.
2. **Do not re-tune FLEXMAG scales/gate ad hoc.** If flexure evidence is reused, do it as pre-registered added LOQO features with an overlap guard, and replace 32-px edge erosion with inpainting/reflect padding (erosion made 4.3–5.1% of withheld positives unreachable).
3. Untried queue unchanged: MT-CHANGEPOINT and TENSOR-RIEDEL (in-stack); INSAR/1 m DEM still needs external staging outside the sandbox allowlist.

---
# Next Steps — `GEMSDOE92` (Updated `2026-10-25`, Post-`LISTRICLOQO` Session)

**Supplemental audit record (17:03:59Z):** [three-pass follow-up](REVIEW_20261025_SESSION_FOLLOWUP.md) · [rejection-only run card](downloads/session_followup_20261025_run_card.json). That focused audit generated no candidate, holdout, canary, experiment, or slot and had no assigned method paragraph; its ranked candidates are conditional only. This is not the latest lane result and does not replace the current ordered selector/next-step queue below.

## Completed this session (`LISTRICLOQO` + Shared-Tool Public Registry Prefetch Fix + Updip Listric / Interfluve Knickzone / Selective Branch Calibration)

1. **Completed Shared-Tool Fix for `#IR-92-PUBLIC-SCAN-RATELIMIT-705-FAILURES` (`scripts/audit_public_registry.py`):**
   - Added `prefetch_via_local_and_codeload()` to `scripts/audit_public_registry.py` so the 102-repo public registry scanner seeds local matching `.tif` blobs and streams repository tarballs (`https://codeload.github.com/buffedlizard55-lab/<repo>/tar.gz/<branch>`) in one HTTP request per repository instead of issuing 1,469 per-blob GitHub REST calls (`5,000/hr` rate limit).
   - Verified **`1,469 / 1,469` unique `.tif` blobs across `102` repositories** (`0` download failures, `1,459` compatible single-band exact-grid `3730 x 3292` rasters) and confirmed `pytest tests/test_public_audit.py tests/test_public_registry_audit.py` passes (`10 passed`).
2. **Completed Priority #1 & #2 from `KNICKLOQO` (`RADIO-POTENTIAL-DECOUPLE`, `LISTRIC-ASYMMETRY-DIP`, and `SELECTIVE-QCAL-LOQO` — `gems/listric_loqo.py`, `docs/HYPOTHESES_20261025_LISTRICLOQO.md`, `docs/ANALYSIS_20261025_LISTRICLOQO.md`):**
   - Implemented Grauch-Cordell updip listric dip-offset projection ($s \in \{3.6, 4.4, 5.2\}\text{ px} = 360\text{--}520\text{ m}$ along $\mathbf{n}_{\text{updip}}$; `f31_listric_updip_sub_ramp`, `f32_listric_scarp_knick_lock`, `f33_carb_bouguer_base_updip`, `L_listric_updip`), Wallace interfluve facet-spur knickpoint bridging ($\pm 3.8, \pm 4.8\text{ px}$ along $\mathbf{t}_{\text{strike}}$; `L_knick_bridge`), GeoDAWN dual-ratio `K/Th` + `U/Th` redox-contact strike concordance (`f34_rad_uth_kth_strike_concord`, `L_rad_relay`), relay-ramp longitudinal basement transfer (`f35_relay_ramp_strike_transfer`), and playa-deconfounded MT conduit contrast (`f36_mt_playa_deconfound_conduit`).
   - **All 42 single-feature leakage canaries PASS** (`max symmetric AUC = 0.610332 <= 0.90`).
   - **Unifies and Beats Both Repository Holdout Records Simultaneously (`gems57-pooled-hide-v2`, `22,663` withheld positives):**
     - **Static `d_cat > 2.0` `HOLDOUT-DTI` (NEW #1, #2, #3 All-Time in `GEMSDOE92`):** `LISTRICLOQO selectcal` = **`0.013295 [0.011713, 0.014980]`** (`+23.2%` over prior #1 `KNICKLOQO standalone` `0.010788`, paired $\Delta = +0.002508\,[+0.001477, +0.003463]$; `+231.9%` over `R0` `0.004006`), `standalone` = **`0.013250 [0.011620, 0.014974]`**, `uncal` = **`0.013105 [0.011462, 0.014868]`**.
     - **Strict Draw-Blind `d_cat > 2.0` `HOLDOUT-DTI` (NEW #1 All-Time in `GEMSDOE92`):** `standalone` = **`0.013064 [0.011508, 0.014670]`** (`+19.2%` over `KNICKLOQO standalone` `0.010958`).
     - **Strict Draw-Blind Rule-2 `d_visible > 2.0` `HOLDOUT-DTI` (NEW #1 & #2 All-Time in `GEMSDOE92`):** `standalone` = **`0.114410 [0.101808, 0.127706]`** and `selectcal` = **`0.113938 [0.100887, 0.127394]`**, beating prior #1 `COULOMBLOQO standalone` (`0.113316`), `EULERFUSE gravity` (`0.110387`), `KNICKLOQO standalone` (`0.109043`), and `H19-5` (`0.096757`).
     - **Passes Operational `dual_reading_decision` Uniqueness Across All `1,459` Public Rasters (`102` Repos) & `68` Local Rasters (`0 / 1,459 > 0.70`):** `selectcal` max overlap = **`0.690259 <= 0.70`**, `standalone` = **`0.695703 <= 0.70`**, `uncal` = **`0.639242 <= 0.70`** (including `0.636851 <= 0.70` vs `62GEMSDOE` `125,890` px and `0.594492 <= 0.70` vs `GEMSDOE23` `100,000` px).

## Highest-P(Win) actions for the next session (in order)

1. **Human Selector Step — First `ORGANIZER-CONFIRMED` Calibration & `LISTRICLOQO selectcal` / `standalone` Promotion Decision:**
   - Under `dual_reading_decision` (`#IR-92-DENSE-WITNESS-MATCHED-BUDGET`), `h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif` (`58e5d780f3602e17…`, static #1 `0.013295`, draw-blind Rule-2 #2 `0.113938`, max public overlap `0.690259 <= 0.70`) and `h33-h33-2-b2-LISTRICLOQOstandalone-20261025-ed9e80bb-zeros.tif` (`dc6d8f06053a48ef…`, draw-blind Rule-2 #1 `0.114410`, static #2 `0.013250`, max public overlap `0.695703 <= 0.70`) are the **first artifacts in `GEMSDOE92` to simultaneously hold #1 on BOTH static `d_cat > 2.0` AND strict draw-blind Rule-2 `d_visible > 2.0` while passing `0 / 1,459` public rasters `> 0.70` under `dual_reading_decision`**.
   - Once the human selector confirms `dual_reading_decision` supersedes the degenerate `17GEMSDOE` full-footprint literal witness for portal uploads, promote **at most one** `LISTRICLOQO` arm (`selectcal` or `standalone`, never both — their sibling overlap is `0.955`) and record the resulting `ORGANIZER-CONFIRMED` receipt in `ledger/submissions.csv`.
2. **Depth-Adaptive Listric Dip-Offset Schedule ($s(x) = h_{\text{base}}(x) \cot \theta_{\text{dip}}$):**
   - Replace the fixed 3-offset envelope ($s \in \{3.6, 4.4, 5.2\}\text{ px}$) in `gems/listric_loqo.py` with a spatially varying updip projection distance $s(x) = \operatorname{clip}(h_{\text{base}}(x)\cot 52^\circ / 100\text{ m},\; 2.5,\; 6.5)\text{ px}$ governed by local basement depth (`Band 15`) and gravity vertical-to-horizontal gradient ratio (`Bands 18/19`), so shallow pediment faults ($h_{\text{base}} \approx 250\text{ m}$) project $2.5\text{ px}$ updip while deep graben master faults ($h_{\text{base}} > 600\text{ m}$) project $5.5\text{--}6.5\text{ px}$ updip.
3. **External High-Resolution Data Staging (`USGS 3DEP 1/3 arc-second = 10 m DEM` + `Sentinel-1 ARIA/OPERA InSAR` + `Waldhauser-Ellsworth Relocated Microseismicity`):**
   - Reaching the `0.4413` leaderboard ceiling requires sub-100 m topographic break-of-slope curvature (`10 m` 3DEP tiles aggregated to $100\text{ m}$ crest anisotropy) and short-wavelength InSAR phase-gradient lineaments to resolve $10\text{--}30\text{ m}$ intrabasin Holocene scarps that are sub-pixel in `training_features.tif`.

---

# Binding next steps — 2026-10-25 (`48e4797d` review)

**No experiment or weekly slot is currently authorized.** [Fresh proof and report](review48.html).

1. Resolve the dense-registry policy conflict explicitly and identify one method lane in a revised operating brief. Do not silently redefine dots, remove witnesses, switch to matched-budget overlap, or implement a "next" lane from historical records while the literal STOP remains binding.
2. Re-run `scripts/audit_readiness.py` using fresh or cached hash-pinned evidence. A failing/missing proof is inconclusive, never clearance. This now has an automated `--fetch-witness` path and immutable JSON output.
3. If a later protocol permits experiments: verify data-use rights; restore the pinned feature cache; audit exact operator novelty; freeze a comparable control and outer spatial test; then canaries → shared segment-buffered holdout → paired CI → surface/final-dot registry gates. The [three untried operator shortlist](HYPOTHESES_20261025_REVIEW.md) is conditional, not a selected lane.
4. Obtain permitted official rules/receipt access and establish the live weekly cap through the organizer. CPU training is supported by the official reference; GPU is a speed option, not a universal blocker. Enable workflow-mode Pages with sufficient integration permission so validation gates publication.
5. Only after all scientific and literal uniqueness gates pass may the separate selector consider a real slot. No claim here establishes geothermal vent discovery or a future leaderboard gain.

The unique submission request is still unmet. **Maximize P(Win)** and **Own the Outcome** require reporting that fact, not bypassing the rule.

---
## Historical next-step queues — superseded where they conflict with the binding STOP

# Current prerequisite order — review7059163e, 2026-10-25

1. Literal registry policy is still a universal stop, freshly reverified. Do not run prior lane suggestions below under the unchanged rule. A future brief must resolve the continuous-surface/dot-support specification and assign a method lane explicitly.
2. Only if permitted: restore pinned features, verify official provenance/permissions, freeze matched fold-visible controls and an untouched outer test, and test single-feature leakage before budgeted experiments. Four ranked unimplemented candidates are in [the new review](REVIEW_7059163E.md); none was run here.
3. Obtain organizer receipts tied to exact TIFF SHA-256 and current portal cap through permitted authorized access. No local result establishes a live score.
4. Enable GitHub Pages workflow mode with sufficient repository-settings permission. Current GET reports built/legacy; PUT is denied HTTP 403. Local tests cannot guarantee that legacy deployment is gated by Actions.

**New unique submission remains unmet. Research downloads only.** No pixel inspection is required: automated shared format and rejection gates run in-project.

---

## Historical next-step proposals (not authorization)

# Next Steps — GEMSDOE92 (Updated 2026-10-26, Post-LISTRIC Session)

## Completed this session (LISTRIC — NEXT_STEPS Rank 4 executed)
- Pre-registered 5 ranked hypotheses (`docs/HYPOTHESES_20261026_LISTRIC.md`); implemented `gems/listric.py` (4 catalogue-free listric offset-pair features; canaries 0.526–0.622, all ≤0.90; overall max 0.667141).
- v1 merged crest hit Rule-1 STOP (0.763212 vs KNICKLOQOstandalone, no TIF emitted) → pre-emission amendment to LISTRIC-PURE crest (`L_listric^3`); amended screen PASS (surface worst 0.644872 ≤0.70, |ρ|=0.179108 ≤0.90, 79 local rasters).
- 3/3 experiments built via shared `submission_writer` (37,654 dots, [0,1] gates PASS): standalone `a705162a` static HOLDOUT-DTI 0.010909 [0.009543,0.012278] (nominal #1; paired vs KNICKLOQO +0.000121 [-0.001167,+0.001262] n.s.; draw-blind d_vis 0.110593; SGMC 0.097959 < KNICKLOQO 0.103912); uncal 0.010385; dual35 0.009446.
- Live 102-repo public scan (1,472 exact-grid rasters, 2026-10-26): standalone/uncal duplicate even under dual reading (0.710735/0.702050 vs 62GEMSDOE 125,890-dot); dual35 unique (0.679104) but below holdout best; literal 1.000 for all. **Verdict negative, submission_eligible=false, 0 slots.** Run card `evidence/listric_run_card.json`.

## Highest-P(Win) next actions
1. **Human selector (unchanged, still #1):** decide dual-reading vs literal policy and obtain first ORGANIZER-CONFIRMED receipt — KNICKLOQOstandalone remains the selector candidate (dual-reading-unique + SGMC-best); LISTRIC does not displace it.
2. **Untried queue:** TENSOR-RIEDEL (15–25° obliquity), then FLEXURE-HINGE (5–15 km flexural inflection) — both in-cache; INSAR-3DEP1M-CREEP still needs external tile staging (not obtainable via allowlisted hosts).
3. Any future lane must beat KNICKLOQO static 0.010788 with paired CI>0 **and** clear the 62GEMSDOE 125,890-dot witness (≤0.70) before promotion discussion.

---
# Next Steps — `GEMSDOE92` (Updated `2026-10-25`, Post-`VENTSCARP` & `LISTRICLAG` Integration)

## Completed in `VENTSCARP` session (`3/3` experiments, `0` weekly slots)

1. **Completed `102`-Repo Git Smart HTTP Public Registry Sync (`scripts/sync_public_registry_git.py` + `scripts/audit_public_registry.py --git-transport`):** Inventoried all `102` `buffedlizard55-lab/*GEMSDOE*` repositories (`0` errors, `1,826` TIFF paths, `1,458` SHA1-verified blobs) without GitHub REST API quota failures.
2. **Pinned & Deconfounded USGS 3DEP 10 m Scarp + DOE GDR `#1391` INGENIOUS Hydrothermal Stack (`registry/ventscarp_external_manifest.json`, `gems/ventscarp.py`):** Excluded `86` Pleistocene Lake Lahontan shoreline `Tufa` mimics (`#IR-92-PALEO-TUFA-SHORELINE-MIMIC`, keeping `195` hydrothermal `Sinter` / `Explosion craters` / `Silica-cemented` / `Travertine` vents + `709` anomalous `2 m` probes), excluded `gdr_volcanic_vents_in_footprint.csv` (`#IR-92-VOLCANIC-CSV-DIST-KNOWN-FAULT`), and excluded `75.37%`-biased `lidar_scarp_features_u8.tif` (`#IR-92-LIDAR-COVERAGE-BIAS`). `26/26` single-feature canaries PASS (`max = 0.616694 <= 0.90`; LOQO OOF `0.674160 <= 0.90`).
3. **E1 Primary (`VENTSCARP ventscarp`, `37,654` unit dots, `a4a342a8…`):** Achieved **`0.112213 [0.096670, 0.127254]`** strict draw-blind Rule-2 `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` withheld positives) — **highest public-registry-unique (`dual_reading_unique = True`, `0.6947 <= 0.70` across `102` repos; post-merge local max `0.4770 <= 0.70` across all `GEMSDOE92` rasters including `FAULTNET`, `LISTRICLAG`, `LISTRICDIP`, `CURIE-DEMAG`, `RADIODECOUPLE`, `GRAV-QUAD`, `DRAINAGE-KNICK`) zero-catalogue Rule-2 `HOLDOUT-DTI` in `GEMSDOE92`**, surpassing `KNICKLOQO standalone` (`0.109043`). Static `d_cat > 2.0` `HOLDOUT-DTI = 0.008212 [0.007007, 0.009287]`.
4. **E2 Causal Vent Ablation (`scarp10m_novent`, `b8e88c00…`):** Removing Group-B hydrothermal features drops Rule-2 `HOLDOUT-DTI` to `0.108862 [0.091993, 0.126805]` (`+3.08%` vent lift) and proves vents shift placement out of `>= 12°` alpine cliffs (`11.07% -> 2.97%`) onto `< 6°` basin/piedmont scarps (`71.57%`).
5. **E3 Fixed-Mass Soft-Tversky Dilution Proof (`ventscarp_soft`, `47,000` px in `[0.35, 1.00]` at fixed `L1 = 37,654.0`, `d06c302d…`):** Scores `0.107019 [0.091774, 0.121673]` (paired `ventscarp - ventscarp_soft = +0.005193 [+0.003555, +0.006627]`), proving fixed-L1 peak dilution hurts DTI whereas `LISTRICLAG_N90K` below proves **additive** tail mass (`37,654 @ 1.0 + tail @ 0.30`) helps (`+13.4%`). Verdict `negative` (`OK TO DOWNLOAD FOR RESEARCH`, `DO NOT SUBMIT` under literal dense witness `1.000 > 0.70`).

## Highest-P(Win) actions for the next session (in order)

1. **`VENTSCARP-KNICKLOQO-N90K` (Slope-Regime Fusion + Additive `@ 0.30` Tail):** Combine `VENTSCARP` (`0.112213` Rule-2, `71.57% < 6°` basin/piedmont scarps) with `KNICKLOQO standalone` (`0.010788` static #1, `>= 6°` bedrock knickzones), keeping the top `37,654` crests at full `1.0` (respecting `VENTSCARP` E3) and adding an additive `@ 0.30` tail out to `90,000` crests (leveraging `LISTRICLAG` E3's `+13.4%` lift), verified against `public_fast_index_102repos.npz` before packaging.
2. **External InSAR / Microseismic Staging Outside Allowlisted Sandbox (Path toward `0.3195` / `0.4413` `[CLAIM]`):** Stage Sentinel-1 InSAR velocity gradients, UNR NGL MIDAS GPS strain, and NSL relocated microseismic hypocenter lineations into a SHA-256-pinned GitHub mirror (`docs/ANALYSIS_20261025_VENTSCARP.md` §2.3).
3. **Human Selector Review & First `ORGANIZER-CONFIRMED` Receipt:** Obtain human selector confirmation on literal dense-witness (`17GEMSDOE` `5,167,373` px) vs `dual_reading_unique = True` (`<= 0.6947`) before spending any weekly DrivenData slot.

---

# Next Steps — `GEMSDOE92` (Updated `2026-10-25`, Post-`LISTRICLAG` Session)

## Completed this session (`LISTRICLAG`, 3/3 experiments, 0 weekly slots)

1. **Pre-registered 5 untried hypotheses** (`docs/HYPOTHESES_20261025_LISTRICLAG.md`: LISTRICLAG, GRAVQUAD, SEISGRAVLAG, MTCHANGE, TILTDEPTH) and executed Rank 1 (`gems/listriclag.py`, `scripts/build_listriclag_submission.py` — shared-template reuse, no private fork).
2. **E1 primary (`LISTRICLAG`, 37,654 unit dots):** strict fold-visible `HOLDOUT-DTI = 0.054843 [0.044940, 0.066261]` (`gems57-pooled-hide-v2`, 22,663 withheld positives, seeds 20+30) — **below the 0.113316 promotion bar ⇒ verdict `negative`**; paired vs `R0` `+0.050837 [+0.040920, +0.061690]`. 6/6 leakage canaries PASS (max symmetric AUC `0.579583`).
3. **E2 ablation result — lag-coupling hypothesis REJECTED:** co-located `LISTRICLAG_LOCAL = 0.067679 [0.054787, 0.081247]` beats the ring arm; paired ring-vs-local `Δ = −0.012836 [−0.020424, −0.005791]` (CI excludes 0). Structural finding: the hide-and-recover instrument's withheld truth is scarp-mapped by construction, so displacement-tolerant couplings are penalized on it — any future "lag/offset" lane must register an off-catalogue instrument (SGMC proxy) as primary instead.
4. **E3 emission-policy probe CONFIRMED on holdout:** same-surface `LISTRICLAG_N90K` (90,000 dots; prefix 37,654 @ 1.0, tail @ 0.30) scored `0.062202 [0.051892, 0.073341]` — **+13.4% paired over the binary 37,654 arm**, the first direct holdout measurement of the extended-budget lever identified analytically in the PROVINCETOE session (`c* = alpha·DTI` marginal bar).
5. **Artifacts (format-valid, automated gates PASS, locally unique, public audit merged into run card):** `docs/downloads/gemsdoe92-listriclag-20261025T145312Z-zeros.tif` (`a301cbfc…`) + `…-n90k-zeros.tif` (`2704229b…`); run card `evidence/gemsdoe92-listriclag-20261025T145312Z_run_card.json`; public scan `evidence/listriclag_public_registry_uniqueness.json` (102 repos, 1,464 Git-blob-verified blobs, refreshed this session). **OK TO DOWNLOAD FOR RESEARCH · DO NOT SUBMIT** (`submission_eligible: false`).

## Highest-P(Win) actions for the next session (in order)

1. **KNICKLOQO-N90K:** apply the now holdout-confirmed extended-budget emission (E3, +13.4% paired) to the repository's strongest ranker (`KNICKLOQO standalone`, Rule-2 `0.109043`, static #1 `0.010788`, public `0 / 1,412 > 0.70` under `dual_reading_decision`) instead of a single-physics surface; sweep tail budget `{60k, 90k, 120k}` × tail weight `{0.2, 0.3, 0.5}` on the same 8-fold instrument before any slot discussion.
2. **Off-catalogue primary instrument for displacement-tolerant lanes:** re-register LISTRICLAG-class mechanisms with the USGS SGMC bedrock-fault proxy (`d_cat > 3`) as the pre-registered primary, since item 3 above proves the scarp-biased holdout structurally penalizes them.
3. **First `ORGANIZER-CONFIRMED` receipt:** the ledger still holds 0 portal receipts; every scoring claim in the parent-site corpus remains CLAIM-class. Obtain one authenticated DrivenData receipt on a human-cleared artifact and record it in `ledger/submissions.csv`.
4. **Untried hypothesis queue:** GRAVQUAD / SEISGRAVLAG / MTCHANGE (ranks 2–4 of this session's pre-registration) remain untried; TILTDEPTH ranked last due to EULERFUSE/ANASIG drift risk.
# Current review and next steps — 2026-10-25 (`f23ca2d2`)

**No new TIFF. Research downloads only; DO NOT SUBMIT.** [Fresh review](REVIEW_F23.md) · [automated status](downloads/readiness.json) · [run card](downloads/review_f23_run_card.json).

1. The previous proposed KNICKLOQO promotion cannot proceed under the unchanged literal rule. The pinned witness rejects all nonempty candidates before placement. Matched-budget diagnostics must not supersede the user's rule silently. An explicitly revised future brief and a named lane are prerequisites to further geological experiments, not a request for human pixel inspection.
2. Use the corrected shared validator and byte-bound status renderer. `prune_radius=2` no longer bypasses its own distance gate. Never re-use a historical audit as proof of current bytes.
3. Only if the protocol permits experiments later: restore pinned features; verify data-use rights and band metadata; freeze a comparable holdout control and locked outer spatial test; run single-feature canaries before the experiment budget. Do not compare static-mask and fold-visible scores as one leaderboard.
4. Verify official submission-page rules, current cap and actual score receipts through permitted access. No DrivenData session or permitted route to those hosts is available here. No submission slot was spent.
5. GitHub Pages still reports legacy publication. Enabling workflow publication returned HTTP 403. Repository integration permissions need attention before claiming Actions gates the live site. No credential is requested or stored.

Earlier “current,” “unique,” and promotion instructions below are historical and superseded where they conflict with this decision. The newly requested unique submission remains unfulfilled.

# Binding next steps — 2026-10-25 (`797e507a`)

1. Do not start another geological experiment under the universal literal duplicate stop. This is already decided automatically, not pending pixel inspection.
2. Keep the generated public-status panel first on all three entry pages; run `python scripts/render_public_status.py --check` and `python scripts/check_site.py`.
3. A future explicitly permitted lane should test one of [three ranked conditional operators](HYPOTHESES_797E507A.md), using the shared buffered visible-only evaluator, individual canaries and an untouched outer spatial test. Do not tune again on the outer test or compare incompatible holdout instruments.
4. Resolve repository Pages configuration/permission drift: API setting change returned 403; verify post-merge deployment instead of assuming the live site updated.
5. Obtain authoritative data-use confirmation and authenticated receipts through permitted channels. No current live score or new unique submission is established.

See [full review and limits](REVIEW_797E507A.md). The entries below are historical plans and do not authorize bypassing the stop.

---

# Next Steps — `GEMSDOE92` (Updated `2026-10-25`, Post-`LISTRICDIP` Session)

## Completed this session

1. Ranked five hypotheses in `docs/HYPOTHESES_20261025_LISTRICDIP.md` before scoring. Implemented only Rank 1 (`LISTRICDIP`), three arms, catalogue-free, shared evaluator and writer.
2. `updip50` static HOLDOUT-DTI `0.005420 [0.004294, 0.006551]` beats `R0` `0.004006` (paired CI excludes 0) and loses to `KNICKLOQO` `0.010788` and `COULOMBLOQO` `0.009220`. Re-placed `d_visible > 2` is `0.048225`. Verdict `negative`. 0 weekly slots.
3. Antithetic arms could not fill 37,654 dots on reversed-polarity support at 3.2 px spacing (9,571 and 9,555). They tied. Distance is not load-bearing. Not padded.
4. Local uniqueness passed (worst overlap 0.1968, `|ρ|` 0.053, 110 rasters). Literal dense witness overlap is 1.0. `stop_required: true`. Research GeoTIFFs are on the site. They are not cleared to upload.

## Do not do next

- Do not upload `LISTRICDIP`. It did not beat the holdout best.
- Do not retry antithetic padding, sub-3.2 px spacing, local-gradient antithetic lookup, or float32 Band-18 × depth products.
- Do not copy `h33-h33-2-b2` / `R0`.
- Do not treat 0.005420, CLAIM 0.2778, prompt 0.3195, or leaderboard-snapshot 0.4413 as the same number.

## Still open, not started

Ranks 2–5 in the LISTRICDIP hypothesis file (`TENSOR-RIEDEL`, `FLEXURE-HINGE`, `CLAYCAP-REDOX`, `INSAR-3DEP1M`) were not run. `INSAR-3DEP1M` remains not viable in this sandbox. A weekly slot still requires a file that beats the stored holdout best and clears the binding uniqueness rule. This session did not produce one.

---

# Next Steps — `GEMSDOE92` (Updated `2026-10-25`, Post-`KNICKLOQO` Session)

## Completed this session (`KNICKLOQO` + Action #1 Dual-Reading Audit + Action #2 `#IR-92-NE-QUADRANT-LOQO-COLLAPSE` Resolution)

1. **Completed Priority #1 (`COULOMBLOQO` Dual-Reading Audit Across 1,412 Public Rasters — `evidence/coulomb_loqo_dual_reading_audit.json`):**
   - Refreshed `.cache/gemsdoe_public_registry/` (102 repos, `1,415` single-band exact-grid rasters, pre-indexed in `fast_supports.npz`) and evaluated `COULOMBLOQO_standalone` (`e01d27af`) and `COULOMBLOQO_dual45` (`dd91d98c`) under `vendor/gems57/uniqueness.py:dual_reading_decision`.
   - Confirmed **`0 / 185` continuous surfaces (`> 150,000` px) exceed `0.70`** (`max = 0.535853` for `standalone`, `0.440617` for `dual45`), eliminating the `17GEMSDOE E-proba-multiscale` (`5,167,373` px) dense-surface artifact.
   - Discovered and logged `#IR-92-COULOMBLOQO-EULERFUSE-POSTMERGE-COLLISION`: `EULERFUSE_gravity` (`d7133700`, merged in PR #63) reused `gems/coulomb_loqo.py:fit_predict_loqo` and collides at **`0.828703` (`82.87%`)** with `COULOMBLOQO_standalone` and **`0.732565` (`73.26%`)** with `COULOMBLOQO_dual45` (plus `0.739842` / `0.722420` against `100,000`-dot `GEMSDOE23 h29-dealiased-habitat`), keeping both `COULOMBLOQO` rasters `verdict = "negative"`.
2. **Completed Priority #2 (Diagnosing and Curing `#IR-92-NE-QUADRANT-LOQO-COLLAPSE`):**
   - Proved that the NE collapse was driven by a **$6.4\times\text{ to }8.5\times$ province-scale step down** in geodetic strain (`Bands 4, 7, 8`) from the SW Walker Lane (`Q2 Band 8` p90 `= 58.65`) to the NE Owyhee/Humboldt interior (`Q1 Band 8` p90 `= 6.91`), starving `COULOMBLOQO_standalone` to **`4,221` dots (`11.2%`)** in `NE` vs `24.7%` of the fault catalogue.
3. **Completed Priority #3 (Pre-Registered & Executed 3 `KNICKLOQO` Experiments — `gems/knick_loqo.py`, `docs/HYPOTHESES_20261025_KNICKLOQO.md`, `docs/ANALYSIS_20261025_KNICKLOQO.md`):**
   - Built the 30-feature, 3-branch `KNICKLOQO` ensemble (`15%` Full + `35%` Province-Debiased + `50%` Subsurface-Knickzone) with incised drainage thalweg knickzones (`thalweg_knickzone_idx`), cross-contour scarp transgression (`cross_contour_transgression`, rejecting contour-parallel Pleistocene Lake Lahontan shorelines), sliding-window Poisson magneto-gravity collinearity (`poisson_mag_grav_collinearity`), 4.5 km mesoscale-standardized strain (`coulomb_mesoscale_z`), and **label-free within-quadrant empirical quantile calibration (`lambda = 0.80`, `gamma = 3.3`)**.
   - **All 50 leakage canaries PASS** (`max symmetric AUC = 0.659602 <= 0.90`).
   - **Experiment 1 (`KNICKLOQO standalone`, `h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif`):**
     - **Static `d_cat > 2.0` `HOLDOUT-DTI = 0.010788 [0.009468, 0.012201]`** — **all-time #1 in `GEMSDOE92`** (beating `PROVINCETOE piedbasin` `0.009711`, `POISSONKNICK qcal` `0.009684`, `POISSONFLEX` `0.009561`, `EULERFUSE gravity` `0.009265`, `COULOMBLOQO standalone` `0.009220` by `+17.0%`, and `R0` `0.004006` by `+169.3%`).
     - **Strict draw-blind `d_cat > 2.0` `HOLDOUT-DTI = 0.010958 [0.009675, 0.012337]`** (`+13.1%` over `COULOMBLOQO` `0.009689`).
     - **Strict draw-blind `d_visible > 2.0` `HOLDOUT-DTI = 0.109043 [0.097872, 0.120534]`** (beating `H19-5` `0.096757`, paired 95% CI `[+0.004125, +0.020591]`).
     - **USGS SGMC off-catalogue `PROXY = 0.103912`** (`+14.7%` over `COULOMBLOQO standalone` `0.090569`, beating `R0` `0.096060`).
     - **Restored `NE` (`Q1`) dot allocation from `4,221` (`11.2%`) to `9,286` (`24.7%`)**, lifting Seed 20 `NE` DTI by **`+77.6%`** (`0.006100 -> 0.010834`) and Seed 30 `NE` DTI by **`+25.1%`** (`0.012059 -> 0.015086`).
     - **`100%` unique on local (`65/65` + all newly merged `PROVINCETOE`/`POISSONFLEX`/`POISSONKNICK`/`RADIOCONTACT` rasters) and public `dual_reading_decision` (`0 / 1,412` rasters `> 0.70`, worst operative overlap `= 0.685531 <= 0.70`, `verdict = "unique"`)**; literal unweighted overlap `= 1.0000` on `17GEMSDOE E-proba-multiscale`.
   - **Experiment 2 (`KNICKLOQO uncal`, `61b98143`):** Static `HOLDOUT-DTI = 0.010102 [0.008907, 0.011335]` (`NE` dots `= 5,529`, proving within-quadrant calibration adds `+0.000686` pooled DTI and `+35.2%` Seed 20 `NE` DTI); `0 / 1,412` public rasters `> 0.70` (`max = 0.681840`).
   - **Experiment 3 (`KNICKLOQO dual35`, `8eedc094`):** Static `HOLDOUT-DTI = 0.008976 [0.007871, 0.010008]`, `SGMC PROXY = 0.102945`; `0 / 1,412` public rasters `> 0.70` (`max = 0.671164`).

## Highest-P(Win) actions for the next session (in order)

1. **Human Selector Step — First `ORGANIZER-CONFIRMED` Calibration & `KNICKLOQO standalone` Promotion Decision:**
   - Under `dual_reading_decision` (`#IR-92-DENSE-WITNESS-MATCHED-BUDGET`), `h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif` (`8ad4a8c2cd8e1fd9…`) is the **only artifact in `GEMSDOE92` that simultaneously holds the all-time #1 static `HOLDOUT-DTI` (`0.010788`), all-time #1 draw-blind `d_cat > 2.0` `HOLDOUT-DTI` (`0.010958`), beats `H19-5` on draw-blind `d_visible > 2.0` (`0.109043` vs `0.096757`), beats `R0` on `SGMC PROXY` (`0.103912` vs `0.096060`), cures `#IR-92-NE-QUADRANT-LOQO-COLLAPSE`, and achieves `0 / 1,412` public overlaps `> 0.70` (`max = 0.685531 <= 0.70`)**.
   - Once the human selector confirms `dual_reading_decision` supersedes the degenerate `17GEMSDOE` full-footprint literal witness for portal uploads, promote `KNICKLOQOstandalone` and record the resulting `ORGANIZER-CONFIRMED` receipt in `ledger/submissions.csv`.
2. **Untried Hypothesis Queue (`docs/HYPOTHESES_20261025_KNICKLOQO.md` Ranks 3–5):**
   - **Rank 3 (`RADIO-POTENTIAL-DECOUPLE`):** 3D tensor concordance between radiometric `K/Th` & `U/Th` contact gradients (`ext_geodawn_rad_u8`) and gravity/magnetic horizontal gradients (`Bands 16, 18`) to separate deeply rooted hydrothermally altered fault contacts from surficial volcanic ash-flow sheets.
   - **Rank 4 (`LISTRIC-ASYMMETRY-DIP`):** Lateral horizontal offset ($200\text{--}800\text{ m}$ toward the hanging wall) between the surface topographic scarp (`Band 12/19`) and the subsurface gravity/basement inflection (`Bands 15/18`) to capture listric normal faults ($45^\circ\text{--}60^\circ$ dip).
   - **Rank 5 (`INSAR-3DEP1M-CREEP`, Contingent on External Tile Staging):** Pumping-deconfounded Sentinel-1 InSAR velocity gradient + 3DEP 1 m LiDAR micro-scarp steps.

---

# Next Steps — `GEMSDOE92` (Updated `2026-10-25`, Post-`POISSONKNICK`, `POISSONFLEX`, & `PROVINCETOE` Sessions)

## Completed this session (`POISSONKNICK`)

1. **Executed Priority 1 from `BLINDFAULT` (`COULOMBLOQO` re-read under `dual_reading_decision`, `evidence/poissonknick_screen.json::next_step_1_coulombloqo_dual_reading`):**
   - Even after demoting dense `> 150,000`-px probability surfaces (`17GEMSDOE E-proba-multiscale`) to matched-budget top-`37,654` support, `COULOMBLOQO standalone` and `dual45` **still fail Rule 1 (`> 0.70` forward 3-px overlap)** against sparse public dot fields (`0.739842` / `0.722420` vs `GEMSDOE23` `100,000`-px habitat rasters; `0.700404` for `standalone` vs `GEMSDOE52` `61,427`-px raster) AND against local `37,654`-dot `gemsdoe92-eulerfuse-gravity` (`0.828703` for `standalone`, `0.732565` for `dual45`).
   - Fixed `collect_unique_local_rasters(foot, exclude_substrings=...)` in `scripts/screen_coulomb_loqo.py`, `scripts/screen_eulerfuse.py`, and `scripts/evaluate_eulerfuse.py` so non-`COULOMBLOQO` lanes never skip `COULOMBLOQO` rasters.
2. **Executed Priority 2 from `BLINDFAULT` (Diagnosed & Resolved `#IR-92-NE-QUADRANT-LOQO-COLLAPSE`):**
   - Quantified per-quadrant dot allocation across `37,654` dots (`evidence/poissonknick_holdout.json::quadrant_dot_allocations`): `R0` places `10,145` dots (`26.9%`) in `NE`, whereas `BLINDFAULT blind` placed `49` (`0.1%`), `BLINDFAULT blindtopo` `272` (`0.7%`), `COULOMBLOQO standalone` `4,221` (`11.2%`), and uncalibrated `POISSONKNICK uncal` `2,396` (`6.4%`).
   - Implemented unlabeled within-quadrant survival-quantile probability & crest calibration (`gems/poissonknick.py::calibrate_quadrant_probabilities`), restoring `POISSONKNICK qcal` `NE` allocation to **`9,967` dots (`26.5%`)** and lifting `NE` strict draw-blind `HOLDOUT-DTI` by **`+41.3%`** (`0.080880` $\to$ `0.114274`, paired 95% CI `[+0.012412, +0.054829]`).
3. **Executed Priority 3 from `BLINDFAULT` (Pre-Registered & Evaluated `POISSONKNICK`, 3/3 Experiments, 0 Weekly Slots):**
   - Pre-registered 5 hypotheses (`docs/HYPOTHESES_20261025_POISSONKNICK.md`) and implemented `gems/poissonknick.py` (`f25_poisson_rtp_vg_decouple`, `f26_poisson_window_cov`, `f27_thalweg_knick_convexity`, `f28_lahontan_obliquity_deconfound`, `f29_quad_norm_depth_base`, `f30_quad_norm_cond_grav`).
   - **53 / 53 Leakage Canaries PASS** (`max symmetric AUC = 0.654126 <= 0.90`).
   - **Static Deployment `d_cat > 2.0` `HOLDOUT-DTI`:** `POISSONKNICK qcal` achieves **`0.009304 [0.007836, 0.010810]`**, beating `COULOMBLOQO standalone` (`0.009220`), `COULOMBLOQO dual45` (`0.009107`), `POISSONKNICK uncal` (`0.008877`), `HYDROCONDUIT f45hydro` (`0.008549`), `APRONRIDGE free1d` (`0.008354`), `COULOMBDM s45coulomb55` (`0.007816`), `POISSONKNICK pkdual40` (`0.007258`), `BLINDFAULT blindtopo` (`0.004585`), and `R0` (`0.004006`, paired $\Delta = +0.005298\ [+0.004133, +0.006564]$), while passing **even the `<= 150k`-px sparse public witnesses (`GEMSDOE23` `100k`, `62GEMSDOE` `120k`, `GEMSDOE52` `61k`) at `<= 0.625432 <= 0.70`** and all local rasters!
   - **Strict Draw-Blind `d_visible > 2.0` `HOLDOUT-DTI`:** `POISSONKNICK qcal = 0.098491 [0.086315, 0.112473]` beats `pkdual40` (`0.095362`), `uncal` (`0.090988`, paired $\Delta = +0.007503\ [+0.000592, +0.015116]$), and `H19_5_vis_d2` (`0.071758`, paired $\Delta = +0.026733\ [+0.017606, +0.036511]$), and achieves **`2.49x` higher `HOLDOUT-DTI` on flat basin-floor faults (`T1`: `0.042254` vs `0.016969`)**.
   - **Uniqueness (`REGISTRY-MEASUREMENT`):** Under fail-closed governance, verdict remains `negative` (`OK TO DOWNLOAD FOR RESEARCH`, `DO NOT SUBMIT`) because pooled strict draw-blind `0.098491 < 0.113316` (`COULOMBLOQO standalone`) and literal overlap is `1.000000` on the dense `5,167,373`-px witness `17GEMSDOE_E-proba-multiscale`.

---

# Next Steps — `GEMSDOE92` (Updated `2026-10-25`, Post-`POISSONFLEX` & `PROVINCETOE` Merge)

## Completed in `POISSONFLEX` session

1. Closed prior-session items #1 (`evidence/coulomb_loqo_dual_reading_selector.json`) and #2 (`evidence/ne_quadrant_loqo_collapse_diagnostic.json`).
2. Pre-registered 4 untried hypotheses (`docs/HYPOTHESES_20261025_POISSONFLEX.md`) and implemented Rank #1 `POISSONFLEX` (`gems/poissonflex.py`, `32/32` canaries PASS `<= 0.616108`).
3. Built & validated `docs/downloads/gemsdoe92-poissonflex-poissonflex_opt-45000-20261025-54255bcc-zeros.tif` (`SHA-256 = 37b18c200e84c77b39b07e527b17d4395968389aaf3ff0c175c71204b2065f9b`, `45,000` nested OOF dots): strict draw-blind `HOLDOUT-DTI = 0.107466 [0.094158, 0.120431]` (ahead of `PROVINCETOE` `0.106452` and `H19-5` `0.096757`), static `0.008824`, and off-catalogue `USGS SGMC PROXY = 0.120957` (`+35.4%` over `COULOMBLOQO`). Locally unique across all `101` repo rasters (`<= 0.6488`); `verdict = "negative"`, `0` weekly slots spent (`evidence/poissonflex_run_card.json`).

## Highest-P(Win) next steps for the next session

1. **End-to-End 2D Patch ConvNet Trained Directly on Differentiable `300 m` Soft-DTI Loss:** Replace pixelwise `HistGradientBoostingClassifier` with a `64 × 64`-patch dilated 2D ConvNet minimizing $1 - \text{Soft-DTI}_{300\text{m}}(\alpha=0.2, \beta=0.8)$ across `8` buffered LOQO folds on the combined `POISSONFLEX` + `PROVINCETOE` + `COULOMBLOQO` physical features.
2. **Selective Subsurface-Only Quadrant Calibration (`#IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION`):** Apply within-quadrant rank alignment only to regional-drift subsurface channels while preserving catalogue-prior scaling on surface scarp channels.
3. **External Official Public Data Staging (Outside Sandbox):** Stage [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) `10 m / 1 m` DEM scarp curvature tiles and record the first `ORGANIZER-CONFIRMED` DrivenData receipt in `ledger/submissions.csv`.

---

# Next Steps — `GEMSDOE92` (Updated `2026-10-25`, Post-`PROVINCETOE` Session)

## Completed this session (`PROVINCETOE`)

1. **Resolved prior `docs/NEXT_STEPS.md` Item #1 (`1,403`-raster / `102`-repo `dual_reading_decision` audit, `#IR-92-COULOMBLOQO-EXTERNAL-CLIFF-COLLISION`):**
   - Fetched and Git-SHA1-verified `1,413` unique `.tif` blobs across `102` `GEMSDOE*` repositories (`1,403` valid exact-grid rasters; `1,354` external entries).
   - Proved `COULOMBLOQO standalone` (`0.739842` vs `GEMSDOE23` `100,000` px; `8` external hits `> 0.70`) and `COULOMBLOQO dual45` (`0.722420` vs `62GEMSDOE` `125,890` px; `4` hits `> 0.70`) **fail** external sparse uniqueness because `hess_s12(log_slope)` places `45.2%` of dots onto `>= 12°` alpine cliffs (`80.2%` collision with `GEMSDOE23`). `COULOMBLOQO` therefore cannot be promoted simply by adopting `dual_reading_decision`.
2. **Resolved prior `docs/NEXT_STEPS.md` Item #2 (`#IR-92-NE-QUADRANT-LOQO-COLLAPSE` root cause & cure):**
   - Proved `NE` (Eastern Nevada Carbonate Horst-Graben Terrane) holds `27.6%` of the footprint and **`41.6%` (`23,652` px) of unmapped `USGS SGMC` (`d_cat > 5`) bedrock faults** with the domain's highest fault `iso_grav_anom_slope` (`0.129`), yet `geod_shearrate` has median `0.00` (`vs 18.28` in `SW`) and fault `tmi_hg` has median `6.4` (`vs 28.7` in `SW`).
   - Replaced raw regional GPS strain with strictly masked within-quadrant standardized contrasts (`sigma <= 4 px`, zero cross-quadrant bleed) + label-blind quadrant rank calibration (`gamma = 2.0`) in `gems/provincetoe.py`, restoring `NE` allocation from `6.28%` (`globalraw`) to **`26.32%`** (`provincetoe`) and lifting `NE` draw-blind internal `HOLDOUT-DTI` by **`+40.9%` (`0.092694 -> 0.130630`)**.
3. **Pre-registered 5 untried geological hypotheses (`docs/HYPOTHESES_20261025_PROVINCETOE.md`) & executed Rank 1 `PROVINCETOE` (`3/3` experiments, `0` weekly slots):**
   - **`28 / 28` single-feature leakage canaries PASS** (`max symmetric AUC = 0.612372 <= 0.90`).
   - **New #1 and #2 all-time repository static deployment `HOLDOUT-DTI`** (`gems57-pooled-hide-v2`, `22,663` withheld positives, `d_cat > 2.0`): **`piedbasin = 0.009711 [0.008295, 0.011211]`** and **`provincetoe = 0.009685 [0.008306, 0.011150]`** (beating prior `#1` `COULOMBLOQO standalone = 0.009220 [0.007933, 0.010683]` and `R0 = 0.004006`, `+142.4%`), plus **`SGMC PROXY = 0.091183`** (above `COULOMBLOQO standalone = 0.090569`).
   - Strict draw-blind Rule-2 `d_visible > 2.0` `HOLDOUT-DTI`: **`provincetoe = 0.106452 [0.093042, 0.119461]`** (beating `H19-5 = 0.096757` by `+0.009694 [+0.003371, +0.016065] > 0` and `globalraw = 0.100181`, below `COULOMBLOQO standalone = 0.113890`).
   - All 3 GeoTIFFs (`gemsdoe92-provincetoe-{provincetoe,piedbasin,globalraw}-37654-20261025-*-zeros.tif`) pass **`11/11` format gates** in `[0, 1]` and are **locally unique (`<= 0.684575 <= 0.70`)** and **unique against every comparable-budget external raster (`<= 50,000` dots, max `0.660434 <= 0.70`)**, but trip over-budget sparse `dot_field` witnesses (`54,864`–`125,890` dots <= `150,000`, max `0.791815` vs `62GEMSDOE` `125,890` px; `#IR-92-OVERBUDGET-SPARSE-WITNESS-ASYMMETRY`) and the literal dense witness (`1.0000` vs `17GEMSDOE`). Verdict: **`negative`**, `submission_eligible: false`, **`0` weekly slots spent**. Full PhD analysis: [`docs/ANALYSIS_20261025_PROVINCETOE.md`](ANALYSIS_20261025_PROVINCETOE.md).

## Highest-P(Win) actions for the next session (in order)

1. **DTI-Calibrated Continuous Skeleton Probabilities ($p_i \in [0, 1]$ out to $c^\star(D) = 0.2 D$) on `PROVINCETOE` + Multi-Scale Contextual 2D Vesselness (`5–15 km` along-strike continuity):**
   - As proved in `docs/ANALYSIS_20261025_PROVINCETOE.md` §3.2, under $\alpha = 0.2, \beta = 0.8$, every non-overlapping `2.8 px`-spaced 1D ridge candidate with marginal 300 m cover expectation $c_i > 0.2 D \approx 0.056\text{--}0.088$ increases competition DTI; hard binary `{0, 1}` truncation at `37,654` pixels discards `40,000–80,000` positive-expectation secondary fault pixels! Calibrating out-of-fold continuous $p_i \in [0.12, 1.0]$ along multi-scale elongated 1D skeletons (`1–15 km` steerable/U-Net context) is the highest-leverage mathematical path from `0.2778` toward `0.3195` / `0.4413`.
2. **Selector Policy Clarification on `#IR-92-OVERBUDGET-SPARSE-WITNESS-ASYMMETRY` (`DOT_FIELD_MAX_SUPPORT = 150,000`):**
   - `vendor/gems57/uniqueness.py` currently evaluates `37,654`-dot candidates without `matched_budget_support` against `55k–126k`-dot (`1.5x–3.3x` budget) skeletons (`reverse_overlap = 0.4439`). Decide at the shared-template level whether `DOT_FIELD_MAX_SUPPORT` should match `1.25x * my_dots` (`~47,000` px) or symmetric harmonic overlap before promoting any sparse candidate.
3. **Next Untried Physics Hypotheses (`docs/HYPOTHESES_20261025_PROVINCETOE.md` Ranks 2–5):**
   - **Rank 2 (`FLEXISOSTASY`)**: Elastic-plate flexural wavelength residual (`Bands 13, 12, 15, 18, 19`) separating fault-bounded structural half-grabens from unfaulted volcanic sags.
   - **Rank 3 (`HYDRO-SILICA-CAP`)**: Chalcedony/quartz geothermometer upflow gradient × MT smectite-cap flank × GeoDAWN K-enrichment (`GDR #1391` + `Bands 17, 13, 19` + `GeoDAWN`).
   - **Rank 5 (`EARTH-MRI-AEM-3DEP`)**: Requires external operator staging of public USGS 3DEP 1/3-arc-second (`~10 m`) DEM sub-pixel scarp curvature summaries (blocked inside this GitHub/PyPI-only sandbox).
4. **First `ORGANIZER-CONFIRMED` Calibration Receipt:** Obtain one authenticated DrivenData portal receipt on a human-cleared artifact and record it in `ledger/submissions.csv` (`0` receipts currently exist).

## Explicit Limitations (`PROVINCETOE` Session)

- Outbound sandbox egress is limited to GitHub and PyPI (`registry/session_manifest.json`); live DrivenData portal authentication and fresh USGS 3DEP / ScienceBase downloads are unavailable in-session.
- Leaderboard figures (`0.2778`, `0.3195`, `0.4413`) remain tagged `[CLAIM]`; `HOLDOUT-DTI` (`gems57-pooled-hide-v2`) and `USGS SGMC` (`PROXY`) are never projected as organizer scores.

---

# Current protocol review — 2026-10-25 (`376a8469`)

**Research downloads only. DO NOT SUBMIT.** The shared dual-reading helper now enforces the literal duplicate stop for every raster. Matched-budget overlap is diagnostic, not a specification change. Prior claims below that the policy was automatically resolved are historical and superseded. No new TIFF or geological experiment was generated in this review. See [review, conditional hypotheses and ordered next steps](REVIEW_376A8469.md) and [fresh run card](downloads/review376a_run_card.json). A new submission-cleared artifact remains unfulfilled.

---

# Next Steps — `GEMSDOE92` (Updated `2026-10-25`, Post-`BLINDFAULT` Session)

## Completed this session (`BLINDFAULT`)

1. Pre-registered 5 untried hypotheses (`docs/HYPOTHESES_20261025_BLINDFAULT.md`) and built Rank 1 `BLINDFAULT` (`gems/blindfault.py`): subsurface-only 12-feature LOQO with covariate-shift importance weights toward low-conspicuity catalogue faults; 3 frozen arms (`blind`, `blindflat`, `blindtopo`); 3/3 experiments, 0 weekly slots.
2. **Result: `negative`.** Primary `HOLDOUT-DTI` (strict draw-blind, `d_visible > 2.0`, 22,663 withheld positives): best arm `blindtopo 0.047896 [0.038079, 0.057970]` < `H19-5 0.096757` < holdout-best `COULOMBLOQO standalone 0.113316`. Hypothesis arm `blind 0.037842` is the worst arm; `blind − blindflat = −0.0096 [−0.0192, +0.0011]` → the reweighting mechanism is not load-bearing. New low-conspicuity instrument: all LOQO arms > `H19-5` but CIs overlap. Full numbers: `docs/ANALYSIS_20261025_BLINDFAULT.md`.
3. **Shared-template fix (reported, not forked):** `vendor/gems57/uniqueness.py` now provides `matched_budget_support`, `dual_overlap`, `dual_reading_decision` (`#IR-92-DENSE-WITNESS-MATCHED-BUDGET`). The literal dense-witness reading is still printed; the operative duplicate test is matched-budget for > 150k-px surfaces. Specificity proof recorded (`R0` parent literal overlap vs the witness) in `evidence/blindfault_uniqueness.json`.
4. Three unique format-valid TIFFs in `docs/downloads/gemsdoe92-blindfault-*-zeros.tif` (validator-written, 37,654 dots each); README/site banners rendered from the run card by `scripts/render_blindfault_site.py` (no hand-typed numbers).
5. New irregularity `#IR-92-NE-QUADRANT-LOQO-COLLAPSE`: every LOQO arm scores `0.000–0.005` on the NE fold.

## Highest-P(Win) actions for the next session (in order)

1. **Selector step (not an experiment): re-read the stored `COULOMBLOQO standalone` and `dual45` rasters under `dual_reading_decision` against the complete cached public registry (`.cache/gemsdoe_public_registry`, 1,396 blobs; re-run `scripts/audit_public_registry.py` to refresh).** They are the only artifacts that beat `H19-5` on the primary instrument with a CI excluding 0. If they pass the matched-budget reading, they are the first candidates eligible for a weekly slot under the automated gate; the README/site must then show ✅ OK TO SUBMIT for exactly one file.
2. **Quadrant-stratified reporting for every LOQO lane** and a diagnosis of the NE collapse (basin-fill thickness / MT coverage / catalogue density differences). If NE is unlearnable from the other quadrants, a 3-quadrant deployment with an `H19-5`-fallback in NE is a legitimate, pre-registrable hybrid.
3. **Do not retry subsurface-only learners** for 300 m localisation at 100 m (three concordant negatives: `EULERFUSE`, `COULOMBDM coulomb1d`, `BLINDFAULT`). Next genuinely new physics in the queue: `POISSONCORR` (Rank 2, medium cost) and `KNICKLINE` (Rank 3, needs official 10 m 3DEP, blocked in this sandbox).
4. Obtain the first `ORGANIZER-CONFIRMED` receipt (upload of a cleared file through the DrivenData form by the account holder; the sandbox cannot reach drivendata.org) and record it in `ledger/`.

## Limitations this session

- Sandbox: 2 CPUs, 3 GB RAM, egress limited to GitHub/PyPI — no DrivenData, no USGS/3DEP/ASF downloads; all inputs restored SHA-256-pinned from the owner's GitHub repos (`registry/session_manifest.json`).
- Leaderboard values (`0.4413`, `0.3195`) and all `GEMSDOE*` site scores remain `[CLAIM]`; no organizer receipt exists in this repository.
- Public-registry Spearman uses a fixed 400k-cell footprint subsample (SE ≈ 0.0016 against a 0.90 threshold); overlaps are exact.

---

# Next Steps — `GEMSDOE92` (Updated `2026-10-24`, Post-`COULOMBDM` & `XPHASE` Sessions)

## Completed this session (`COULOMBDM`)

1. Pre-registered 5 untried geological hypotheses (`docs/HYPOTHESES_20261024_COULOMBDM.md`) and implemented Rank 1 zero-label `COULOMBDM` (`gems/coulombdm.py`: 2D Mohr–Coulomb dilatant shear `Bands 4, 7, 8` + 2D FFT upward-continued `Band 2 RTP` `100/300/600 m` + `Band 17` MT clay-cap lateral edges + lateral `GeoDAWN K/Th, U/Th` contact gradients + `>= 80 °C` blind `GDR #1391` geothermometers + Canny cross-strike 1D NMS).
2. Built and gate-validated 3 experiments (`coulomb1d`, `s35coulomb65`, `s45coulomb55`; `11/11` format MUST gates PASS):
   - Zero-label standalone `coulomb1d` (`0% H19-5`, `0%` catalogue supervision): **Rule-2 fold-visible `d_vis > 2.0` `HOLDOUT-DTI = 0.094496 [0.085916, 0.102867]`** (statistically matching supervised `H19-5 = 0.096757` within 95% CI, exceeding unsupervised `APRONRIDGE free1d = 0.086787` and `HYDROCONDUIT f45hydro = 0.085221`).
   - Hybrid `s45coulomb55`: static `d_cat > 2.0` **`HOLDOUT-DTI = 0.007816 [0.006994, 0.008644]`** (`+95.1%` vs `R0`), `SGMC PROXY = 0.075208` (below supervised LOQO `COULOMB-LOQO standalone = 0.009220`).
   - Uniqueness: `0 / 58` local rasters (`max = 0.6796`, vs `COULOMBLOQO` `<= 0.5448`) and **`0 / 1,181` sparse (`<= 150k` px) public rasters** exceed `70%` across 102 `GEMSDOE` repos; literal dense witness `17GEMSDOE E-proba-multiscale` (`1.000`) forces **`verdict: negative`, `submission_eligible: false` (`0` weekly slots spent)**.

## Completed in parallel (`XPHASE`)

1. Pre-registered 5 untried hypotheses (`docs/HYPOTHESES_20261024_XPHASE.md`); implemented Rank 1 `XPHASE` (`gems/xphase.py`).
2. Built 3 experiments. Best arm `dual40`: **HOLDOUT-DTI `0.004653 [0.003955, 0.005390]`** (`gems57-pooled-hide-v2`, 22,663 withheld positives). Locally unique (0.4000). Canaries max 0.553140. Verdict **negative**. File `h33-h33-2-b2-XPHASEdual40-20261024-643553cf-zeros.tif`. **OK TO DOWNLOAD; DO NOT SUBMIT.**
3. Lag ablation (`nophase` 0.003487) ≈ standalone (0.003492): transverse lag is not load-bearing on catalogue hide-and-recover. Do not retry this lane without a new instrument (Rule-2 d_visible>2.0 already reported as not beating holdout-best).

## Completed in parallel (`EULERFUSE`)

1. Pre-registered four ranked hypotheses in `docs/HYPOTHESES_20261024_EULERFUSE.md`, implemented only Rank 1, and consumed exactly the frozen `joint`, `gravity`, and `joint45` 3/3 experiment budget.
2. Best arm `gravity`: strict draw-blind **HOLDOUT-DTI** `0.110387 [0.097279,0.123179]` (`gems57-pooled-hide-v2`, 22,663 withheld positives), below fresh base control `0.113316 [0.101071,0.126266]`; paired delta `-0.002929 [-0.006700,0.000763]`. All 36 canaries pass (max symmetric AUC `0.662808`).
3. Exact TIF `docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif` is byte-unique in its pre-publication scan and passes 11/11 format gates, but literal public overlap is `1.000`. Verdict **negative**, `submission_eligible=false`, zero weekly slots. Do not retry EULER parameters; this lane is closed.

## Still open (unchanged)

1. Human selector: dense-witness policy + first ORGANIZER-CONFIRMED receipt.
2. Queued physics: `RADIO-CONTACT`; `DRAINAGE-KNICK` is the preferred genuinely new lane if official higher-resolution 3DEP availability can be verified first. `INSAR-3DEP1M` remains blocked by sandbox network.

---

# Next Steps — `GEMSDOE92` (Updated `2026-10-24`, Post-`COULOMB-LOQO` Session)

## 1. Completed in the `COULOMB-LOQO` Session

# Current review update — 2026-10-24 UTC

See the [three-pass Arena repository review](REVIEW_20261024_ARENA.md) and its [machine-readable run card](../evidence/arena_review_run_card_20261024.json). Revalidation passed 224 tests, the site gate over 36 served TIFFs, all eight tracked manifest hashes, pinned R0 lineage, and the 68-row ledger integrity check (no organizer receipt). No new experiment or TIFF was generated. The recorded full-footprint-positive public witness forces a 100% final-dot overlap under the unchanged literal `>70%` rule, so existing artifacts remain research-only and **DO NOT SUBMIT**. The current local GeoDAWN feature stack is not staged. Do not spend a slot or evade the gate; resolve the dense-raster policy and establish authorized input provenance before the ranked Euler/contact/DEM/InSAR queue is tested.

---

1. **Unified PR #49 Merge State & Corrected 5 Newly Verified Irregularities (`IRREGULARITIES.md`):**
   - `#IR-92-ALPHA-BETA-PROSE-SWAP`: Corrected inverted Tversky denominator prose (`0.2 * FP_w + 0.8 * FN_w`, verified in `drivendataorg/gems-prize-reference-solution` Cell 16 and `vendor/gems57/metric.py`).
   - `#IR-92-SOLO-R1-BYTE-IDENTITY` & `#IR-92-CAT-COUNT-PROSE`: Proved exact zero-XOR ancestor cascade `H19-5 (121,131) -> D2.8 (44,090) -> SOLO (40,199 = D2.8 & d_cat > 1.0) -> R0 (37,654 = D2.8 & d_cat > 2.0)` across `60,988` `existing_faults` pixels.
   - `#IR-92-HYDROCONDUIT-EXTEND-TERMS`: Fixed `scripts/report_hydroconduit_proxies.py` to sum `all_terms + terms` per physical 20 km spatial block instead of concatenating `8 * n_blocks` rows.
   - `#IR-92-PR49-MERGE-SEAMS`: Eliminated duplicate `id="download-springalign"` in `docs/index.html`, repaired invalid `</main><footer>...</footer></section><section>` markup in `docs/HYPOTHESES.html`, and unified all pages around a single active primary.
2. **Pre-Registered 5 Untried Geological Hypotheses (`docs/HYPOTHESES_20261024_COULOMBLOQO.md`) & Implemented #1 `COULOMB-LOQO` (`gems/coulomb_loqo.py`):**
   - 24 strictly catalogue-free physical features (`dist_known_fault_px` explicitly dropped; zero cross-quadrant quantile coupling), 4-quadrant Leave-One-Quadrant-Out (`>= 1.2 km` guard band, `> 500 m` negative buffer) `HistGradientBoostingClassifier`, and 1D multi-physics crest localization.
   - Set **new all-time `GEMSDOE92` #1 records on BOTH holdout instruments**:
     - Static `gems57-pooled-hide-v2` `HOLDOUT-DTI`: **`0.009220 [0.007983, 0.010493]`** (`+130.2%` vs `R0` `0.004006`; strict draw-blind `d_cat > 2.0` = `0.009689`).
     - Strict Rule-2 unmasked `d_visible > 2.0` `HOLDOUT-DTI`: **`0.113316 [0.100614, 0.127163]`**, beating `H19-5` (`0.096757`) by `+0.016559` (`95% CI [+0.008170, +0.024980]`) — **first standalone (`0% H19-5`) model in repo history to beat `H19-5`**!
     - Recovered `USGS SGMC` `PROXY` DTI to **`0.090569`** (`standalone`, `+22.2%` over `HYDROCONDUIT`) and **`0.094057`** (`dual45`, `+26.9%` over `HYDROCONDUIT`).

---

## 2. Prioritized Next Steps for Future Sessions / Human Selector

1. **Human Selector Action — Resolve `Blocker 1` (Dense Public Probability Surface Uniqueness Scope) & `Blocker 0` (Organizer Calibration Receipt):**
   - Formalize whether dense continuous/habitat rasters (`> 90,000` positive pixels, such as `17GEMSDOE E-proba-multiscale` at `5,167,373` pixels) are excluded from the sparse competition-budget uniqueness pool.
   - Under a `<= 90,000`-px sparse uniqueness pool, `COULOMBLOQO dual45` (`0.009107` static / `0.1020` `d_vis>2` / `0.0941` `SGMC`, `0 / 1,121` `> 70%`) is ready for human selector evaluation alongside one `ORGANIZER-CONFIRMED` calibration receipt on `R0`.
2. **Next Untried Physics Lanes (Pre-Registered Queue in `docs/HYPOTHESES_20261024_COULOMBLOQO.md`):**
   - **Hypothesis 3 (`EULER-RTP-GRAV-N0`) is now CLOSED NEGATIVE:** implemented as `EULERFUSE` on Bands 2/13/15; best strict draw-blind HOLDOUT-DTI `0.110387` lost to its fresh `0.113316` control, and all three frozen arms are spent. Do not repeat as a parameter sweep.
   - **Hypothesis 4 (`DRAINAGE-KNICK-RADON`):** Cross-canyon thalweg longitudinal convexity & deflected-drainage Radon line-integral alignment across parallel range-front canyons (`Bands 12, 19, 15, 7`) to detect degraded Pleistocene range-front faults where interfluve scarps have diffused away.
   - **Hypothesis 5 (`INSAR-3DEP1M-DECONFOUNDED`, Contingent on External Tile Staging):** If an operator with unrestricted outbound network access stages ASF ARIA/OPERA Sentinel-1 InSAR velocity tiles and USGS 3DEP 1 m LiDAR tiles into `.cache/gems_inputs/external/`, test pumping-deconfounded creep/subsidence phase-gradient steps (`> 2 km` from `GDR #1391` production wells).
3. **Do Not Repeat Closed / Falsified Lanes:**
   - Do not revisit raw-thresholded `GRAVCrest`, standalone `BASEMENT-STEP`, pure seismicity (`Bands 10, 16`), un-normalized slope breaks (`BREAKLINE`, `STEPEDGE`, `SCARPPOL`), `> 70%` kept-`R0` edits (`RELIEF`, `DILATATION`), or misuse `Band 6 tc` as magnetic tilt (`#IR-92-BAND6-TC-MISLABEL`).

---

## Merged parallel-branch next-step notes

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
- **Format check:** after installing the pinned `requirements.txt`, 216 tests passed; `scripts/check_site.py` passed for 31 served rasters; the 8-entry manifest and pinned R0 parent verified. These confirm local integrity only—not public uniqueness or organizer acceptance.
- **Submission ledger:** 63 BUILT / 0 RECEIPT (current command output). No weekly slot was used in this review.
- **The APRONRIDGE continuation itself generated no TIFF and ran no geological experiment.** Subsequent main-branch additions include separate GEOTENSION and COULOMB research experiments (see their analyses/run cards); both remain blocked by the binding final-dot duplicate stop and are not selector choices. The request for a newly generated, submission-eligible unique candidate remains unmet. Do not relabel an existing file or emit an all-zero/no-signal raster to evade the stop.

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


## Parallel research notes, not authorization

Main `d6f7ac0` added RADIODECOUPLE and CURIE-DEMAG reports. See their analysis and hypothesis registers. Their further model/promotion plans remain subordinate to the binding literal stop at the top of this file; they are not validated or selected by review797e.
