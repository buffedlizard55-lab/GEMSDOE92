# GEMSDOE92 — Auditable GEMS Prize Submission Workbench

> **Operating Contract:** Read this README and [`SESSION_PROMPT.md`](SESSION_PROMPT.md) at the start of every session. Every experiment adheres to parallel-run protocol rules (lane discipline, holdout evaluation, leakage canary, registry uniqueness, and machine-readable run cards). Core Values: **Maximize P(Win)** and **Own the Outcome**.

---

## Current decision — 2026-10-24 review: no submission cleared

**No new unique TIFF (or any new TIFF) was generated in this review. Existing files are downloadable for research only; none is cleared to submit.** **REGISTRY-MEASUREMENT:** a hash-verified registry witness is positive on every target-footprint cell, so every nonempty in-footprint prediction has 100% forward overlap under the literal rule. The exact existing SPRINGALIGN bytes were also measured against that single witness: forward overlap **1.0**, |Spearman| **0.0437295**. This is a decisive single-witness stop, not a fresh exhaustive scan; see the [exact-file receipt](evidence/review_20261024_springalign_witness_v2.json).

| Existing research artifact | Link / metadata |
|---|---|
| **GeoTIFF (zeros-outside)** | [Download SPRINGALIGN research TIFF — DO NOT SUBMIT](docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif) · [one-TIFF ZIP](docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.zip) |
| Internal research identifier (not a verified portal field) | `GEMSDOE92-SPRINGALIGN-f33Ctop-20261025` |
| Research note (not for current upload) | `h33-h33-2-b2; SPRINGALIGN f33Ctop 12426 far dots on spring-pair alignment lines >3px off H19-5` |
| SHA-256 | `1772ad5c62506b6b380e221d2202b583edf0a5be4f96916af655e0478eba11b1` |
| Evidence | [format audit](docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-audit.json) · [exact-file single-witness receipt](evidence/review_20261024_springalign_witness_v2.json) · [run card](evidence/springalign_run_card.json) · [three-pass review](docs/REVIEW_REPO_20261024.md) · [source audit](evidence/review_20261024_source_audit.json) |

**HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives): SPRINGALIGN 0.004865, 95% CI [0.004025, 0.005785]. Paired difference versus RELIEF p10 (recorded holdout best) is −0.001180, 95% CI [−0.002065, −0.000337]. These are local holdout values, not leaderboard scores. The public witness independently blocks all nonempty predictions. No weekly slot was selected or used.

The filename retains its `20261025` suffix as artifact identity; the base commit timestamp is 2026-10-24. Do not treat the suffix as a timestamp for this review.

See [current review](docs/REVIEW_CURRENT.md), [hypothesis queue](docs/HYPOTHESES.md), [submission guide](docs/SUBMIT.html), and [machine-readable negative run card](evidence/repo_review_run_card_20261024.json).

---
## Archived ANASIG research artifact (2026-10-24) — local-only uniqueness, do not submit

**✅ FORMAT-VALID — OK TO DOWNLOAD for research. ⛔ DO NOT SUBMIT / NOT CLEARED FOR A WEEKLY SLOT.**

| Deliverable | Link |
|---|---|
| **GeoTIFF (primary)** | [Download ANASIG zeros-outside GeoTIFF](docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif) |
| ZIP (one TIFF) | [Download ZIP](docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.zip) |
| Submission name | `GEMSDOE92-ANASIG-f45Atop-20261024` |
| Note (84 chars) | `h33-h33-2-b2; ANASIG f45Atop 16944 far dots on analytic-signal ridges >3px off H19-5` |
| SHA-256 | `68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5` |
| Audit | [Gate receipt](docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-audit.json) · [run card](evidence/anasig_run_card.json) · [analysis](docs/ANALYSIS_20261024_ANASIG.md) |

**HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld): ANASIG **0.004967 [0.004098, 0.005940]**, Δ vs R0 +0.000961 [+0.000168, +0.001814], vs holdout-best RELIEF p10 (0.006045) −0.001078 [−0.002034, −0.000112]; canary max 0.551113; SGMC PROXY 0.080556 vs R0 0.096060. Local uniqueness passes (24 rasters: worst forward 0.550, |ρ| 0.547; surface |ρ| 0.024). Slot blockers: holdout-best bar + the footprint-positive public witness below (forward overlap 1.000 for these bytes, `evidence/public_witness_anasig.json`). This session's rank-1 SCARPPOL lane beat BREAKLINE on holdout (0.005315) but overlaps it 0.900–0.913 → duplicate-stopped (`evidence/scarppol_run_card.json`). No slot used. Ranked hypotheses/screens: `docs/HYPOTHESES_20261024_SCARPPOL.md`.

---

## Archived STRAINBREAK f60s2i research artifact (2026-10-24; negative)

**✅ FORMAT-VALID — OK TO DOWNLOAD FOR RESEARCH. ⛔ NOT CLEARED FOR A WEEKLY SLOT (verdict negative).** Existing artifact: 22,592 dots (60%) on strained coherent DEM scarp-breaks (`S = BREAKLINE L × pct_rank(Band 4 geod_2ndinv)`), >3 px off the whole H19-5 skeleton **and** >3 px off BREAKLINE f45's far dots; 15,062 coverage-greedy R0 dots kept; 37,654 total. Hypothesis: scarps on currently-loading structures (young step-over strands) are missed by both catalogue and worms. Mimic: Walker Lane strain shadows, subsidence, Lahontan shorelines in strained crust. This session's rank-1 GRAVCrest (signed Band-18 gravity crest) was **falsified by the pre-build SGMC screen and never built** (far-only SGMC 0.005–0.016 vs 0.072).

| Deliverable | Link |
|---|---|
| **GeoTIFF (zeros-outside)** | [Download](docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif) · [ZIP](docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2.zip) |
| Submission name | `GEMSDOE92-STRAINBREAK-f60s2i-20261024` |
| Note (87 chars) | `h33-h33-2-b2; STRAINBREAK f60s2i 22592 far dots on strained scarp-breaks >3px off H19-5` |
| SHA-256 (zeros) | `000d0bd7e0a549c2d38ca52a5df5b249763a7be998ad2ccfa30cc45136c05c1f` |
| Audit / run card | [audit](docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-audit.json) · [run card](evidence/strainbreak_run_card.json) · [analysis](docs/ANALYSIS_20261024_STRAINBREAK.md) · [hypotheses](docs/HYPOTHESES_20261024_GRAVCrest.md) |

**HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld px): f60s2i **0.005487 [0.004522, 0.006430]** — the best locally-unique holdout in this repo (R0 0.004006, BREAKLINE f45 0.004861), Δ vs R0 +0.001481 [+0.000582, +0.002296]; dose plateau f45 0.005022 → f60 → f75 0.005486. But it does **not** beat the holdout best (RELIEF p10 0.006045, paired Δ CI includes 0) and SGMC prefers BREAKLINE (0.12611 vs 0.10516) → promotion rule fails, verdict **negative**. Local uniqueness: worst forward overlap 40.0% / |ρ| 0.401 (21 rasters; surface worst 10.0% / sampled ρ 0.103). Expanded public-registry scan (1,309 rasters, complete for declared scope; `evidence/strainbreak_public_registry_uniqueness.json`): **literal duplicate stop triggered** — worst forward overlap 1.0 (17GEMSDOE full-footprint E-proba), 89 rasters >70%, worst |ρ| 0.417; even vs sparse dot-like rasters only (≤150k positives, 1,125 checked; diagnostic, not a gate) worst is 0.7105 with 3 over 70%. The queued BREAKLINE public scan was also run this session: likewise duplicate (134 >70%; `evidence/breakline_public_registry_uniqueness.json`). Leakage canary max 0.6216. Queued item closed: visible-collar SGMC = 0.021192 vs R0 0.09606 (its holdout gain does not transfer off-catalogue).

## Archived visible-collar candidate — format-valid research download, duplicate stop

**✅ FORMAT-VALID — OK TO DOWNLOAD.** The generated submission raster is an all-finite, single-band float32 GeoTIFF, EPSG:32611, shape 3730 × 3292, matching the competition template geotransform. It contains zero NaNs inside the footprint, zeros outside, values strictly in `[0, 1]`, and passes all 10 local MUST gates on independent re-read from disk. These checks guard against, but do not guarantee portal acceptance or prevent every cause of, the reported error: `Predicted values must be in range [0, 1]`.

**⛔ NOT CLEARED FOR A WEEKLY SLOT — DUPLICATE UNDER THE LITERAL REGISTRY RULE.** An expanded scan found 100% 3-px forward overlap with public registry rasters (131 of 1,279 exceed 70%). Stop; do not submit. This file remains downloadable as a negative research deliverable. The scan covers current default branches in 102 public owner repositories, not every historic/site-hosted file.

| Deliverable | Link / Metadata |
|---|---|
| **GeoTIFF (.tif)** | [Download zeros-outside submission GeoTIFF](docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif) |
| **ZIP (one TIFF)** | [Download ZIP (contains single TIFF)](docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.zip) |
| **Submission Name** | `GEMSDOE92-visible-collar-r0-excluded-20261024` |
| **Note (62 chars)** | `Visible-fault collar 2-3 px; R0 3px halo excluded; 37,654 dots` |
| **SHA-256 Digest** | `60082b75a3d8e4648a858622f71f24257c8cfef79286a1a96147c59f05377da7` |
| **Grid / Dimensions** | EPSG:32611 · 3730 × 3292 @ 100 m resolution · float32 · 37,654 unit-mass dots |
| **Submission Guide** | [Executive Summary Subpage](docs/executive-summary.html) · [Submission Steps (SUBMIT.html)](docs/SUBMIT.html) · [Live Project Site](https://buffedlizard55-lab.github.io/GEMSDOE92/) |
| **Audit Receipt** | [Format Audit Receipt (JSON)](docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-audit.json) · [Full Run Card (JSON)](evidence/visible_collar_run_card.json) |

**Verdict: Negative (Duplicate).** Local format validity is 100% confirmed, but no competition slot was spent due to literal registry overlap.

---

## Archived BREAKLINE f45Ltop research artifact (DEM scarp-break coherence)

A second session built **BREAKLINE f45Ltop**: keeping 20,710 parent R0 dots via exact expected-DTI greedy under an orientation-coherent slope-break field $L = \text{pct\_rank}(\|\nabla \text{det\_elev\_slope}\|) \times \text{coherence}(\text{det\_elev})$ (Bands 19/12), and allocating 16,944 far dots (45%) to the strongest coherent breaks located **>3 px off the entire H19-5 skeleton**.

- **Download:** [`docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif`](docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif) · [ZIP](docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0.zip)
- **Submission Name:** `GEMSDOE92-BREAKLINE-f45Ltop-20261024`
- **Submission Note (90 chars):** `h33-h33-2-b2; BREAKLINE f45Ltop 16944 far dots on linear scarp-break ridges >3px off H19-5`
- **SHA-256 Digest:** `cd9c8a564588e6542b379cd36cbe05fc6da3be07b8edbc542bf737336907810e`
- **Validation:** 10/10 local MUST gates pass on independent re-read.
- **HOLDOUT-DTI:** **0.004861 [0.004032, 0.005822]**, paired delta vs R0 **+0.000854 [+0.000300, +0.001423]**; dose-monotone f33 &rarr; f38 &rarr; f45; USGS SGMC off-catalogue control **+31% vs R0** (0.12611 vs 0.09606); leakage canary max **0.6216** (<0.90 threshold).
- **Local Uniqueness:** Worst forward overlap **55.0%** (vs parent R0), worst $|\rho| = 0.547$; vs visible collar candidate only **3.5%** forward overlap (&phi; &asymp; 0.001, disjoint lanes).
- **Public Registry Audit:** A live public witness check confirmed 100% forward overlap with GEMSDOE17 E-proba. Duplicate; stop. See `evidence/breakline_public_registry_witness17.json`.
- **Verdict:** Negative / NOT CLEARED for slot (below holdout-best arms; stopped by registry overlap). Full analysis: [`docs/ANALYSIS_20261024.md`](docs/ANALYSIS_20261024.md); run card: [`evidence/breakline_run_card.json`](evidence/breakline_run_card.json).

---

## What the reported GEMSDOE32 value can support

The reported value **0.2778 is a CLAIM** copied from the supplied GEMSDOE32 site history; this checkout has no submission-page receipt for that artifact. A GitHub API audit of the owner site's retrieved HTML snapshot found no `0.2778` string and found that snapshot says no organizer score exists for its artifacts. That snapshot does not disprove a later user-reported result; it cannot authenticate it either. See the [pinned source audit](evidence/review_20261024_source_audit.json). The reported lineage H19-5 → D2.8 → SOLO → B2/R0 is consistent with changes to candidate geometry, thinning, pruning, and known-catalogue clearance. The prompt-reported intermediate values 0.1922, 0.2600, and 0.2708 are also CLAIMs, not organizer-confirmed receipts here.

A plausible mechanism is that thinning spatially redundant predictions reduces false-positive cost while maintaining coverage, and avoiding mapped catalogue pixels avoids predictions that may be masked. This is **mechanistic inference**, not causal proof: attributing score changes requires exact artifacts, identical scoring conditions, controlled ablations, and organizer receipts. Nearby predictions can have overlapping kernel support while each emitted prediction contributes to total prediction mass; that makes redundancy a sensible experiment, not proof that a specific thinning step caused the claimed increase. Local HOLDOUT-DTI is not comparable to private leaderboard scores.

The prompt's **0.3195 and 0.4413 are conflicting leaderboard snapshots/claims**; neither was refreshed in this session. We have no authenticated winning raster or method receipt, so cannot state that the highest-scoring submission fused a skeleton, DEM scarps, stepovers, radiometrics, or vent proximity. A score alone does not reveal its feature set. The project has not established that a candidate beats the 0.2778 CLAIM.

The concepts and previous screens are catalogued in [`docs/HYPOTHESES.html`](docs/HYPOTHESES.html), [`docs/HYPOTHESES.md`](docs/HYPOTHESES.md), and [`docs/REVIEW_CURRENT.md`](docs/REVIEW_CURRENT.md). Their rankings are research priorities, not score forecasts. BREAKLINE, SCARPPOL, ANASIG, and STRAINBREAK are already tested—not new hypotheses. The current full-footprint public-registry witness blocks all nonempty in-footprint predictions under the literal overlap rule; do not emit another submission artifact unless that policy blocker is explicitly resolved.

## Candidate Geological Hypotheses — unvalidated research queue

The current queue contains four untested ideas, each with named layers, physical signature, catalogue-missing rationale, implemented-method distinction, non-fault mimic, qualitative benefit/cost rank, and source-access status. No numeric DTI projection is made. All are blocked today by the full-footprint registry witness and the missing local feature-stack cache.

See [`docs/HYPOTHESES.html`](docs/HYPOTHESES.html) · [`docs/HYPOTHESES.md`](docs/HYPOTHESES.md) · [three-pass repository review](docs/REVIEW_REPO_20261024.md). Previously implemented/tested methods—including BREAKLINE, DILATATION, ANASIG, STRAINBREAK, and SPRINGALIGN—are not presented as new candidates.

---

## Core Values & Decision Framework

### Maximize P(Win)
&ldquo;Maximize the Probability of Winning&rdquo;: our decision-making framework. In every decision, we weigh trade-offs, assess risk, and choose the path that maximizes the probability that Arena succeeds. We set aside emotions and make tough decisions in order to maximize P(Win). &ldquo;Maximize P(Win)&rdquo; frees us from constraints and clarifies that we must put Arena first.

### Own the Outcome
We own results end to end &mdash; not just our individual slice of the work. When problems arise and we have the means to act, we do so without waiting for permission or assignment. We treat failure and success as signals and use them to improve. At Arena, we stay accountable to the final outcome.

---

## Reproducible Validation & Verification Pipeline

There is no new candidate from this review. The 19-band feature cache is absent; `scripts/restore_inputs.py` restores pinned owner-mirror bytes, which does not authenticate official competition provenance or establish redistribution permission. Do not launch an experiment until those issues and the registry stop are resolved.

```bash
# Run repository tests, manifest/parent checks, and ledger audit
make test
make manifest verify ledger

# Re-read and gate every zeros-outside GeoTIFF linked from the public site
make site

# Optional format-only check on an already-existing research raster.
# A format pass does not clear it for a competition slot.
make validate FILE=docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif
```

---

## Trusted Sources & Manual Review Links

- [DrivenData Competition #306 Problem & Metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData DOE GEMS About Page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [DrivenData Competition Rules (PDF)](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DrivenData Reference Solution Repository](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN Airborne Surveys Catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [DOE Geothermal Data Repository (GDR) INGENIOUS #1391](https://gdr.openei.org/submissions/1391)
- [Great Basin Center for Geothermal Energy (INGENIOUS Project)](https://gbcge.org/current-projects/ingenious/)
- [USGS 3D Elevation Program (3DEP)](https://www.usgs.gov/3d-elevation-program)
- [EPSG:32611 WGS 84 / UTM Zone 11N Coordinate Reference System](https://epsg.io/32611)
- [Tversky Index Formulation (Wikipedia)](https://en.wikipedia.org/wiki/Tversky_index)

---

## Original Session Prompt (archival)

The original request is retained verbatim for continuity. The current decision above supersedes its requested build where the literal registry gate makes a compliant nonempty candidate impossible.

```markdown
Review the repo. 

THE FOLLOWING IS THE HIGHEST URGENCY AND MUST BE FOLLOWED!

MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION.  DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION.  BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION.  IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED TIF SUBMISSION.

There should be an easy to download submission tif file as described by the prompt.  Read the entire prompt.  A lot of sites mention inspection only and a human inspector, but the inspection needs to be done through the project and needs to be validated for submission without human intervention.

PARALLEL-RUN PROTOCOL — read first. This session is one of several running from this same prompt.

1. LANE. Your lane is the single method paragraph below. Stay inside it. If your raster's rank-correlation with any registry raster exceeds [0.90], or more than [70%] of your dots fall within 3 px of one registry raster's dots, you have drifted into another lane: log it as a duplicate and stop. Check this on the surface before placement AND on the final dots.

2. REUSE, DON'T REBUILD. Use the template's cached feature stack, evaluate_holdout.py and submission_writer.py. Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive every catalogue-based feature only from the visible faults, mask visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared tool is wrong, fix it once in the template and report it; never keep a private fork.

3. LABEL EVERY NUMBER as HOLDOUT-DTI (evaluator version, number of withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). A projection is never written as a score.

4. LEAKAGE CANARY. Test each feature alone on the holdout before trusting any result. AUC above [0.90] means leakage until proven otherwise.

5. RUN CARD. End with one JSON card: hypothesis; mechanism; the named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output (no NaN inside the footprint, values in [0,1], CRS/shape/transform match); submission name + note of at most 140 characters; verdict promote / negative. Negative results are deliverables.

6. BUDGET. Stop after [3] experiments or [2] hours. Do not pick submissions: promotion to a real slot is a separate selector step, within the weekly cap shown on the submission page.

The following sites should serve as a starting point for understanding how to generate TIF submissions...
WE NEED TO STUDY, ANALYZE, AND UNDERSTAND THE HIGHEST SCORE FROM THE GEMDOE SITE WHERE THE SUBMISSION TIF IS DOWNLOADED FROM WHICH IS THE FOLLOWING:
https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html
h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778
Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.2778?
Answer the question using Phd level experience, knowledge, and judgement. Then use the answer to generate a unique TIF submission into the competition.  Must be unique submission unlike any within the GEMSDOE sites above.  Verify working line by line no hallucinations.
Current competition leaderboard GEMSDOE high score: 0.4413
```
