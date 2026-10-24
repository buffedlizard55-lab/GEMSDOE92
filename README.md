# GEMSDOE92 — Auditable GEMS Prize Submission Workbench

> **Operating Contract:** Read this README and [`SESSION_PROMPT.md`](SESSION_PROMPT.md) at the start of every session. Every experiment adheres to parallel-run protocol rules (lane discipline, holdout evaluation, leakage canary, registry uniqueness, and machine-readable run cards). Core Values: **Maximize P(Win)** and **Own the Outcome**.

---

## Latest Review: Literal Uniqueness is Blocked Across the Footprint

**OK TO DOWNLOAD for research; NOT OK TO SUBMIT.** The queued BREAKLINE public witness audit finds **REGISTRY-MEASUREMENT 100% forward overlap** with the hash-verified 17GEMSDOE dense raster. Its 3-pixel halo covers the whole footprint, so every nonempty in-footprint candidate fails the current literal rule. No new unique submission was generated, no score improvement is claimed, and no slot was used. [Review and limitations](docs/REVIEW_CURRENT.md) · [witness receipt](docs/downloads/breakline_public_witness.json) · [session JSON card](docs/downloads/session_review_run_card.json).

---

## Executive Summary — Format-Validated Candidate, One-Click Download

**✅ FORMAT-VALID — OK TO DOWNLOAD.** The generated submission raster is an all-finite, single-band float32 GeoTIFF, EPSG:32611, shape 3730 × 3292, matching the competition template geotransform. It contains zero NaNs inside the footprint, zeros outside, values strictly in `[0, 1]`, and passes all 10 local MUST gates on independent re-read from disk. This completely prevents the DrivenData portal error: `Predicted values must be in range [0, 1]`.

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

## Parallel Candidate — BREAKLINE f45Ltop (DEM Scarp-Break Coherence)

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

## In-Depth Scientific Analysis: Why did GEMSDOE32 Score 0.2778 and How to Beat It?

### 1. Mathematical Mechanics of the Competition Metric
The official competition metric is the distance-weighted, asymmetric Tversky Index ($DTI$):
$$\text{DTI} = \frac{\text{TP}_w}{\text{TP}_w + \alpha \cdot \text{FP}_w + \beta \cdot \text{FN}_w + \varepsilon}$$
where $\alpha = 0.2$, $\beta = 0.8$, and $k(d) = \max(0, 1 - d/300\text{ m})$ with cutoff radius $R = 300\text{ m}$ (3 pixels on a 100 m grid).

### 2. Lineage Breakdown of Score Progression
1. **H19-5 (0.1922):** Multiscale potential-field ridge skeleton (gravity & magnetic gradient maximums). Captured regional crustal fault zones across the Great Basin. However, raw continuous skeletons contained dense, adjacent pixels along single fault traces, creating extreme false-positive mass redundancy.
2. **D2.8 (0.2600):** Applied Poisson-disk thinning with $r = 2.8\text{ px}$ (280 m). Because the triangular kernel width is 3 px, adjacent pixels along a line cover the exact same ground truth ($TP_w$ is max-pooled, so credit is earned once), while each pixel adds $1.0$ to emitted mass $S$ and false-positive mass $FP_w$. Spacing dots at $2.8\text{ px}$ eliminated redundancy and surged the score from 0.1922 to 0.2600.
3. **SOLO (0.2708):** Removed sub-bar isolated dots with low expected gain and removed dots within 1 px of mapped known faults.
4. **B2 / R0 (0.2778):** Enforced strict clearance from known mapped faults ($d_{\text{cat}} > 2.0\text{ px}$, zero mass on catalogue, 37,654 dots). Because competition organizers mask all known USGS/INGENIOUS faults pixel-exactly from live scoring, any prediction placed on or touching a mapped fault yields zero true positive credit while paying full false-positive penalty.

### 3. Why 0.2778 Hit an Asymptotic Ceiling vs the 0.4413 Leaderboard Top
- **Target Ground Truth:** The competition target is expert-mapped *new* faults (mapped primarily from 1m LiDAR and 10m DEM high-resolution topography, active geothermal fault scarps, dilatational stepovers, and geothermal conduit permeability zones).
- **Physical Limitation of Potential Fields:** Potential field worms (H19-5) only detect deep lithologic density and susceptibility contrasts. They completely miss active Quaternary normal fault scarps in basin alluvium (alluvium against alluvium), small-throw fault scarps, and shallow geothermal permeability networks.
- **How Top Submissions Score 0.4413:** Fusing:
  1. A high-confidence skeleton core (~20,000 dots) for deep crustal fault systems.
  2. High-resolution DEM scarp-break detection (structure-tensor coherence $\times$ slope gradient) catching subtle surface ruptures.
  3. Dilatational structural stepovers, pull-apart zones, and geothermal vent clusters (INGENIOUS / GDR wellspring concordance).
  4. Radiometric alteration halos (K/Th radiometrics from GeoDAWN).
  5. Exact Poisson-disk spacing discipline across all emitted dots.

---

## Candidate Geological Hypotheses (Ranked)

| Rank | Hypothesis | Target Signature | Layer(s) Involved | Missing Fault Rationale | Expected DTI Rank / Cost | Data Source & Official Link |
|---|---|---|---|---|---|---|
| **1** | **BREAKLINE (Built)** | Structure-tensor coherence on detrended slope breaks | Band 19 (`det_elev_slope`) & Band 12 (`det_elev`) | Quaternary scarps in alluvium lack magnetic/gravity contrast but express as sharp linear breaks on DEMs. | **Top (Rank 1)** / Low (in-stack) | [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) |
| **2** | **GAMMA-CREST** | Signed gravity horizontal gradient zero-crossing & asymmetric crest | Band 18 (`iso_grav_anom_hg`, signed) & Band 5 (`iso_grav_anom_slope`) | Basinward density edge of listric/dipping normal faults buried under thick hanging-wall alluvium. | **Rank 2** / Low (in-stack) | [USGS GeoDAWN Catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) |
| **3** | **DILATATIONAL-STEPOVER** | Positive dilatational strain rate on structural relay bends | Bands 8, 7, 4 (geodetic strain) & Band 19 (DEM breaks) | Geothermal fluid permeability localizes in extensional stepovers and pull-apart jogs between overlapping fault strands. | **Rank 3** / Medium (in-stack) | [UNR Nevada Geodetic Lab](http://geodesy.unr.edu/) |
| **4** | **HYDROTHERMAL-ALTERATION** | K/Th radiometric ratio gradients & magnetic destruction | External GeoDAWN Radiometrics (`geodawn_rad_u8.tif`) & Band 14 (TMI) | Hydrothermal alteration halos trace active fluid-transmitting fault corridors lacking surface scarps. | **Rank 4** / Medium (pinned cache) | [USGS GeoDAWN Radiometrics](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) |
| **5** | **SHORELINE-FILTERED SCARP** | Elevation-band contour-parallel suppressed breaklines | Bands 19, 12 + Lake Lahontan highstand masks (~1330 m AMSL) | Removes wave-cut shoreline terraces (the dominant non-tectonic false-positive mimic in the Great Basin). | **Rank 5** / Medium (requires NBMG shoreline grid) | [Nevada Bureau of Mines & Geology](https://data.nbmg.unr.edu/) |

Detailed documentation: [`docs/HYPOTHESES.html`](docs/HYPOTHESES.html) · [`docs/HYPOTHESES.md`](docs/HYPOTHESES.md).

---

## Core Values & Decision Framework

### Maximize P(Win)
&ldquo;Maximize the Probability of Winning&rdquo;: our decision-making framework. In every decision, we weigh trade-offs, assess risk, and choose the path that maximizes the probability that Arena succeeds. We set aside emotions and make tough decisions in order to maximize P(Win). &ldquo;Maximize P(Win)&rdquo; frees us from constraints and clarifies that we must put Arena first.

### Own the Outcome
We own results end to end &mdash; not just our individual slice of the work. When problems arise and we have the means to act, we do so without waiting for permission or assignment. We treat failure and success as signals and use them to improve. At Arena, we stay accountable to the final outcome.

---

## Reproducible Validation & Verification Pipeline

```bash
# 1. Restore all SHA-256 pinned inputs into .cache/gems_inputs/
python3 scripts/restore_inputs.py

# 2. Run comprehensive automated test suite (117+ tests)
pytest -v

# 3. Verify pinned data manifests and hashes
python3 scripts/verify_manifest.py

# 4. Run automated gate inspection on all served downloads
python3 scripts/check_site.py

# 5. Format validation on submission candidate
python3 scripts/validate_submission.py --candidate docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif
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

## Original Session Prompt

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
