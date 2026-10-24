# GEMSDOE92 — DOE GEMS Geothermal Fault Discovery (`DrivenData #306`)

**Operating Principles:** **Maximize P(Win)** · **Own the Outcome** · **Zero Hallucinations** · **Automated Fail-Closed Verification**

> **Operating Contract:** Read this `README.md` and [`SESSION_PROMPT.md`](SESSION_PROMPT.md) at the start of every session. Every experiment adheres strictly to the Parallel-Run Protocol (lane discipline, shared `evaluate_holdout.py` + `submission_writer.py`, single-feature leakage canary, pre-placement + final-dot registry uniqueness, and machine-readable Run Card JSON).

> ### CURRENT PRIMARY ARTIFACT STATUS (`2026-10-24`)
> - **File:** [`docs/downloads/h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-zeros.tif`](docs/downloads/h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-zeros.tif) ([`.zip`](docs/downloads/h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-zeros.zip) · [`-audit.json`](docs/downloads/h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-audit.json) · [`scarpdipole_run_card.json`](evidence/scarpdipole_run_card.json))
> - **Download & Format Clearance:** **✅ OK TO DOWNLOAD (`10/10` automated format & portal gates PASS)** — single-band `float32`, `3730 × 3292`, `EPSG:32611`, exact sample geotransform, **`0` NaN inside or outside footprint**, values strictly in `[0.0, 1.0]`, `37,654` unit-mass dots, `0.0` mass on `existing_faults`, `min(d_cat) = 2.2361 px` (eliminates portal error `Predicted values must be in range [0, 1]`).
> - **Weekly Slot Clearance:** **⛔ DO NOT SUBMIT / NOT CLEARED FOR A WEEKLY SLOT WITHOUT HUMAN SELECTOR WAIVER (`verdict: negative` under literal all-rasters rule)** — `SCARPDIPOLE f42dipole` passes **100% of sparse dotted public submissions (`0 / 1,004` overlaps `> 70%` across all `<= 60,000`-dot submissions in all `102` public GEMSDOE repos; `max = 68.77%`)** and **`0 / 27` local rasters (`max = 66.05%`)**, with global `max |Spearman ρ| = 0.3152 << 0.90`. However, under the un-waived literal all-rasters positive-support check (`finite > 0`), `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` is strictly positive on all **`5,167,373 / 5,167,373`** footprint pixels (`100.0%` overlap for **every** nonempty submission; see `saturation_certificate` in [`evidence/scarpdipole_public_registry_uniqueness.json`](evidence/scarpdipole_public_registry_uniqueness.json)).
> - **GitHub Pages Site & Submission Guide:** Landing page [`docs/index.html`](docs/index.html) (`https://buffedlizard55-lab.github.io/GEMSDOE92/`) · Executive summary & conditional portal procedure [`docs/SUBMIT.html`](docs/SUBMIT.html) ([`docs/executive-summary.html`](docs/executive-summary.html)).

---

## 1. Executive Summary & Completed Session Objectives

1. **Prior-Session Queued Next Steps Executed First (`docs/NEXT_STEPS.md`):**
   - **Full 1,300-raster public-registry audit on `BREAKLINE f45Ltop` ([`evidence/breakline_public_registry_uniqueness.json`](evidence/breakline_public_registry_uniqueness.json)):** Scanned `102` public `buffedlizard55-lab` GEMSDOE repositories (`1,306` unique SHA-verified blobs; `1,294` non-BREAKLINE compatible rasters, both pre-placement surface and final dots). `BREAKLINE f45Ltop` exceeded `70%` overlap on `122` rasters (`68` space-filling `>=70%`-halo surfaces **plus `54` discriminating `<70%`-halo rasters**, up to `91.30%` vs `GEMSDOE3/coverage-v3-wide`) -> confirmed `negative`.
   - **Off-catalogue `USGS SGMC` control & holdout confound audit on `visible-collar-r0-excluded` ([`evidence/scarpdipole_proxy_audit.json`](evidence/scarpdipole_proxy_audit.json)):** `visible-collar` collapses **`-77.94%`** vs `R0` on off-catalogue `USGS SGMC` bedrock faults (`0.021192` vs `0.096060`, `n = 62,703`), and its previously quoted `11.7×` holdout ratio was proved to be a masking confound (comparing fold-fair `d_visible > 2.0` `0.046866` against pre-punched static `R0` `0.004006` rather than fold-fair `parent_B2_visible` `0.029074`, where the true ratio is `1.61×`).
   - **Defect repairs:** Repaired JSON syntax errors in `evidence/public_registry_uniqueness.json` and `docs/downloads/public_registry_uniqueness.json`, generalized fail-closed `scripts/audit_public_registry.py`, resolved stale subpage copy in `docs/executive-summary.html` & `docs/submit.html`, and generalized `scripts/check_site.py` across all 17 served `*-zeros.tif` downloads.

2. **New Top Geological Candidate Implemented (`SCARPDIPOLE` — [`gems/scarpdipole.py`](gems/scarpdipole.py)):**
   - Formulated and screened **5 untried geological hypotheses** ([`docs/HYPOTHESES_20261024_SCARPDIPOLE.md`](docs/HYPOTHESES_20261024_SCARPDIPOLE.md)) before building any raster.
   - Built a 3-dose ladder (`f42dipole` primary, `f45dipole`, `f50dipole`) via shared `vendor/gems57/submission_writer.py`, differentiating BOTH the `H19-5` keep stage and `>3 px` off-skeleton emission:
     - **Fold-Fair `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `n = 22,663`, `d_visible > 2 px`):** **`0.098565 [0.087985, 0.108974]`** — **#1 in `GEMSDOE92`** (`3.39×` `parent_B2_visible = 0.029074`; `2.10×` `visible_collar = 0.046866`; paired Δ vs `visible_collar` `+0.051699 [+0.037872, +0.064896]`).
     - **Static Final-Raster `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `n = 22,663`, `d_full_cat > 2 px`):** **`0.006812 [0.005770, 0.008034]`** — **#1 in `GEMSDOE92`** (beats `RELIEF p10 = 0.006045`, `STRAINBREAK f60s2i = 0.005487`, `ANASIG f45Atop = 0.004967`, `BREAKLINE f45Ltop = 0.004861`, and `R0 = 0.004006`).
     - **Off-Catalogue `USGS SGMC` DTI (`PROXY`, `n = 62,703`):** **`0.107841`** (`+12.26%` above `R0 = 0.096060`).
     - **Single-Feature Leakage Canaries (`<= 0.90` gate):** Max raw band `symAUC = 0.5531`; `SCARPDIPOLE S_pct` `symAUC = 0.6328` (`PASS`).

---

## 2. Provenance & Metric Taxonomy (Strict Label Discipline)

| Label | Definition & Evidentiary Standing |
|---|---|
| `ORGANIZER-CONFIRMED` | Exact live score copied from a DrivenData submission receipt and logged in `ledger/submissions.csv` (`0` live slots spent in `GEMSDOE92`). |
| `CLAIM` | Owner-reported upstream live score without a local portal receipt attached in this repository (e.g., `GEMSDOE32` `h33-h33-2-b2` = `0.2778`). |
| `LEADERBOARD-SNAPSHOT` | Public leaderboard reference values reported in prompt/prior audits (`0.4413` #1 snapshot recorded 2026-10-24; `0.3195` earlier prompt snapshot). |
| `HOLDOUT-DTI` | Local buffered whole-segment hide-and-recover evaluation via shared `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, `n = 22,663` withheld positives across 8 folds, `α = 0.2`, `β = 0.8`, `300 m` triangular kernel, 1,000 paired 20 km spatial-cluster bootstrap draws). Never comparable numerically to live scores. |
| `PROXY` | Off-catalogue `USGS SGMC` bedrock-fault evaluation (`n = 62,703` pixels `>3 px` from `existing_faults`, `metric.dti_binary`). |
| `REGISTRY-MEASUREMENT` | Measured full-footprint Spearman `ρ` and 3-px forward dot overlap against local (`n = 27`) and cached public (`n = 1,300` across `102` repos) rasters. |

---

## 3. PhD-Level Forensic Analysis: Why `h33-h33-2-b2` (`GEMSDOE32`) Scored `0.2778` (`CLAIM`) & How `0.2778` Can Be Beaten

### 3.1 Exact Metric Mechanics of Distance-Weighted Tversky Index (`DTI`)

On active evaluation cells $\Omega = \text{footprint} \setminus \text{existing\_faults}$ (where mapped faults are masked pixel-exactly), let $F_{\text{new}} \subset \Omega$ denote hidden test faults and $p: \Omega \to [0, 1]$ the submitted prediction. With the competition's `300 m` (`3 px`) radial linear tent kernel $K(r) = \max(0, 1 - r/3)$ and max-pooled cover operator $C(x) = \max_{y \in \Omega} p(y)\,K(\|x - y\|)$:

$$\mathrm{TP}_w = \sum_{x \in F_{\text{new}}} C(x), \qquad \mathrm{FN}_w = \sum_{x \in F_{\text{new}}} (1 - C(x)), \qquad \mathrm{FP}_w = \sum_{x \in \Omega \setminus F_{\text{new}}} \max\bigl(0,\, p(x) - \mathbb{I}[x \text{ credited}]\bigr)$$

$$\mathrm{DTI}(p, F_{\text{new}}) = \frac{\mathrm{TP}_w}{\mathrm{TP}_w + \alpha\,\mathrm{FP}_w + \beta\,\mathrm{FN}_w}, \qquad \alpha = 0.2,\quad \beta = 0.8.$$

Three structural consequences govern every submission in Competition #306:
1. **Intra-kernel redundancy penalty (`D2.8` jump: `0.1922 -> 0.2600` `CLAIM`):** Because $C(x)$ uses a **$\max$** (not a sum) over the 300 m radius while $\mathrm{FP}_w$ sums pixelwise predicted mass $p(y)$ across uncredited pixels, placing multiple unit-mass pixels within `< 2.8 px` along the same geophysical ridge adds **zero** peak $\mathrm{TP}_w$ while multiplying $\alpha\,\mathrm{FP}_w$ by $3\times$. Thinning the `121,131`-pixel multi-scale potential-field worm skeleton (`H19-5`, `0.1922` `CLAIM`) at `2.8 px` Poisson spacing (`D2.8`, `44,090` dots) eliminated ~`77,041` redundant FP pixels while preserving continuous tent-kernel coverage (`0.2600` `CLAIM`, `+0.0678`).
2. **Catalogue-flank exclusion (`SOLO -> R0` jump: `0.2708 -> 0.2778` `CLAIM`):** In `existing_faults`, mapped range-front faults generate strong aeromagnetic (`Band 3 tmi_hg`), gravity (`Band 5 iso_grav_anom_slope`), and topographic (`Band 19 det_elev_slope`) gradients whose 100–200 m flanks lie *outside* the 1-px masked fault line. Those `1 < d_{\text{cat}} \le 2\text{ px}` pixels are geophysical **halos of already-known faults**, not newly discovered parallel faults. Pruning first `B=1 px` (`SOLO`, `40,199` dots, `0.2708` `CLAIM`) and then `B=2 px / 200 m` (`R0`, `37,654` dots, `0.2778` `CLAIM`) stripped `2,545` near-catalogue flank dots where false-positive savings outweighed splayed-fault true positives by `2.08:1`.
3. **Differential operator discipline (`GEMSDOE32` empirical law):** Taking spatial gradients of *raw* potential/elevation grids (`det_elev`, `iso_grav_anom`, `rtp`) isolates physical contacts (`+3.5%` to `+10.1%` AUC), whereas re-differentiating already-differentiated or kriged derivative grids (`Band 6 tc` terrain correction, `Band 7 geod_shearrate`, `Band 3 tmi_hg`) amplifies gridding artifacts and degrades fault AUC by `-0.04` to `-0.06`.

### 3.2 Why `R0` Hits a Ceiling Near `~0.28` & How Submissions Reach `0.3195`–`0.4413` (`LEADERBOARD-SNAPSHOT`)

`R0` (`0.2778` `CLAIM`) has two fundamental ceilings that explain why top leaderboard entries (`0.3195` prompt snapshot; `0.4413` #1 snapshot recorded 2026-10-24) sit `+0.04` to `+0.16` higher:
1. **Geological blindness of pure potential-field skeletons (`H19-5`):** Every single one of `R0`'s `37,654` dots sits on `H19-5`. Faults cutting **intra-alluvial piedmont bajadas** or **homogeneous Tertiary volcanic sheets** juxtapose rocks of nearly identical density and magnetic susceptibility ($\Delta\rho \approx 0$, $\Delta\chi \approx 0$). They produce **zero** `H19-5` worm response, leaving `R0` with $\mathrm{FN}_w = 1$ (weighted $\beta = 0.8$) across entire Quaternary piedmont fault populations.
2. **Binary `{0, 1}` dot discretization vs calibrated continuous probabilities $p(x) \in [0, 1]$:** Under $\alpha = 0.2, \beta = 0.8$, recall is weighted **$4\times$ higher** than precision. A supervised multi-scale spatial model (such as Prof. John Lipor's official Monte-Carlo CV U-Net benchmark in [`drivendataorg/gems-prize-reference-solution`](https://github.com/drivendataorg/gems-prize-reference-solution), upgraded with buffered whole-segment spatial CV and direct differentiable DTI-cover loss) outputs calibrated intermediate probabilities $p(x) \in [0.15, 0.85]$ along uncertain sub-alluvial corridors rather than hard `{0, 1}` isolated dots, capturing $4\times$-weighted $\beta\,\mathrm{TP}_w$ recall across broad geothermal step-overs without paying full unit-dot FP penalties on background pixels.

Within this repository's zero-GPU autonomous physics lane, **`SCARPDIPOLE` directly breaks Ceiling #1** while respecting `R0`'s spacing and flank-exclusion physics: it re-ranks the `H19-5` budget share by piedmont scarp-diffusion physics (`58%`) and reallocates `42%` (`15,815` dots) `>3 px` off `H19-5` onto coherent piedmont scarp-curvature zero-crossings, achieving **`3.39×` `parent_B2_visible`** on fold-fair `HOLDOUT-DTI`, **`1.70×` `R0`** on static `HOLDOUT-DTI`, and **`+12.26%` over `R0`** on off-catalogue `USGS SGMC` faults.

---

## 4. Ranked Pre-Implementation Geological Hypotheses (`2026-10-24`)

Full equations, mimic analysis, and controlled screening (`20,710` kept `R0` + `16,944` far `>3 px` off `H19-5`) are archived in [`docs/HYPOTHESES_20261024_SCARPDIPOLE.md`](docs/HYPOTHESES_20261024_SCARPDIPOLE.md):

| Rank | Hypothesis | Layers | Physical Mechanism & Difference from Prior Repo Lanes | Non-Fault Mimic | Canary `symAUC` | Screen Static `HOLDOUT-DTI` | Screen `USGS SGMC` (`PROXY`) | Decision |
|---:|---|---|---|---|---:|---:|---:|---|
| **1** | **`H1b` / `SCARPDIPOLE`** (Piedmont Scarp-Diffusion Dipole) | `Bands 12, 19` (`det_elev`, `det_elev_slope`) | Hanks–Bucknam–Wallace ($\partial_t z = \kappa\nabla^2 z$) downslope profile-curvature convex$\to$concave zero-crossing ($\partial_s z_{ss} > 0$ at $z_{ss}=0$, low $\|z_{tt}\|$) inside `[p15, p85]` `det_elev` piedmont–range-front corridor. Unlike `BREAKLINE`'s unsigned $\|\nabla(\text{slope})\|$ (double-peaked at crest/toe, `>p85` alpine noise), pinpoints the fault-trace midpoint and jointly re-ranks `H19-5` + off-`H19-5`. | Lake Lahontan paleoshorelines, fluvial terrace risers, landslide headscarps. | `0.6314` | **`0.005181`** (`0.006812` unified) | **`0.106600`** (`0.107841` unified) | **Implemented (`f42`/`f45`/`f50`)** |
| **2** | **`H1`** (Unrestricted Scarp Dipole) | `Bands 12, 19` | Same signed profile-curvature dipole across `[p0, p100]` without piedmont–range-front habitat envelope. | Alpine glaciated cirque cliffs & caprock rims (`>p85`). | `0.6110` | `0.003938` | `0.119880` | Superseded by `H1b` |
| **3** | **`H3`** (`SCARP_MAG_CONCORD`) | `Bands 2, 3, 12, 19` | Azimuthal strike concordance $\cos^2(\theta_{\text{topo}} - \theta_{\text{rtp}})$ between raw `rtp` gradient and scarp strike. | Remanently magnetized basalt flow margins & dikes. | `0.6232` | `0.004973` | `0.091442` | Screened out (`SGMC < R0`) |
| **4** | **`H5`** (`ACTIVE_TRANSTENSION`) | `Bands 7, 8, 9, 12, 19` | Algebraic Walker Lane GPS shear + positive dilatation + 2nd invariant weighting piedmont scarps (no spatial derivative on GPS bands). | 30 km GPS interpolation halos across unfaulted bajadas. | `0.5599` | `0.005105` | `0.071042` | Screened out (`SGMC -26%`) |
| **5** | **`H2` (`GRAV_VGZ`) & `H4` (`HYDRO_DEMAG`)** | `Bands 4, 5` / `GeoDAWN K,eTh` + `GDR 1391` + `Band 3` | Blakely–Simpson raw `iso_grav_anom` zero-crossing (`H2`); hydrothermal K/eTh alteration + magnetite destruction near thermal wells (`H4`). | 2 km gravity gridding shift (`H2`); felsic ash-flow tuffs (`H4`). | `0.5391` / `0.5005` | `0.004858` / `0.003603` | `0.064422` / `0.071205` | Screened out (coarse resolution) |

---

## 5. Audited Evaluation Summary (`SCARPDIPOLE` vs All Merged `GEMSDOE92` Lanes)

All `HOLDOUT-DTI` numbers come from shared `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, `8` buffered whole-component folds, seeds `20` & `30`, `22,663` withheld positives, `1,000` paired 20 km spatial-cluster bootstrap draws). Full machine-readable output: [`evidence/scarpdipole_proxy_audit.json`](evidence/scarpdipole_proxy_audit.json).

| Arm | Dots (`on H19-5` / `>3 px far`) | Fold-Fair `HOLDOUT-DTI` (`d_vis > 2 px`) `[95% CI]` | Static `HOLDOUT-DTI` (`d_cat > 2 px`) `[95% CI]` | Off-Catalogue `USGS SGMC` (`PROXY`, `n=62,703`) | Local `<=3 px` Max Overlap (`n=27`) | Public Sparse `<=60k` Dots `>70%` (`n=1,004`) | Public All-Rasters (`n=1,300`) Binding Verdict |
|---|---:|---|---|---|---:|---:|---|
| **`SCARPDIPOLE f42dipole` (Primary)** | `37,654` (`21,839` / `15,815`) | **`0.098565 [0.0880, 0.1090]`** (`#1`) | **`0.006812 [0.0058, 0.0080]`** (`#1`) | **`0.107841`** (`+12.26%` vs `R0`) | **`0.6605`** (`PASS`) | **`0 / 1,004`** (`max 0.6877`) | `negative` (`17GEMSDOE` 100% surface) |
| `SCARPDIPOLE f45dipole` | `37,654` (`20,710` / `16,944`) | `0.097641 [0.0871, 0.1075]` | `0.006719 [0.0056, 0.0079]` | `0.107849` (`+12.27%` vs `R0`) | `0.6634` (`PASS`) | `0 / 1,004` (`max 0.6657`) | `negative` (`17GEMSDOE` 100% surface) |
| `SCARPDIPOLE f50dipole` | `37,654` (`18,827` / `18,827`) | `0.094286 [0.0840, 0.1036]` | `0.006516 [0.0054, 0.0077]` | `0.107692` (`+12.11%` vs `R0`) | `0.6665` (`PASS`) | `0 / 1,004` (`max 0.6348`) | `negative` (`17GEMSDOE` 100% surface) |
| `RELIEF p10` | `37,654` (`37,654` / `0`) | — | `0.006045 [0.0052, 0.0069]` | `0.087245` (`-9.18%` vs `R0`) | `0.9938` (`DUP`) | Fails (`99.38%` vs `R0`) | `negative` (`R0` duplicate) |
| `STRAINBREAK f60s2i` | `37,654` (`15,062` / `22,592`) | — | `0.005487 [0.0045, 0.0064]` | `0.105160` (`+9.47%` vs `R0`) | `0.5500` (`PASS`) | Fails (`max 0.7105`) | `negative` (`89` rasters `>70%`) |
| `ANASIG f45Atop` | `37,654` (`20,710` / `16,944`) | — | `0.004967 [0.0041, 0.0059]` | `0.080556` (`-16.14%` vs `R0`) | `0.5500` (`PASS`) | Below holdout best | `negative` (`17GEMSDOE` witness) |
| `BREAKLINE f45Ltop` | `37,654` (`20,710` / `16,944`) | — | `0.004861 [0.0040, 0.0058]` | `0.126105` (`+31.28%` vs `R0`) | `0.5500` (`PASS`) | Fails `54` `<70%`-halo rasters | `negative` (`122` rasters `>70%`) |
| `visible-collar-r0-excluded` | `37,654` (`0` / `37,654` collar) | `0.046866 [0.0402, 0.0533]` | N/A *(full-cat collar)* | `0.021192` (`-77.94%` vs `R0`) | `0.0352` | Fails (`11GEMSDOE`) | `negative` (`131` rasters `>70%`) |
| `R0` (`h33-h33-2-b2`, parent `CLAIM 0.2778`) | `37,654` (`37,654` / `0`) | `0.029074 [0.0258, 0.0324]` *(as `parent_B2_visible`)* | `0.004006 [0.0034, 0.0047]` | `0.096060` (`baseline`) | `1.0000` (self) | — | Reference parent (`GEMSDOE32`) |

---

## 6. Official Competition Sources, Pinned Data Provenance & Sandbox Limitations

| Resource / Dataset | Canonical Official URL | Sandbox Access & Verification Status (`2026-10-24`) |
|---|---|---|
| DrivenData Competition #306 Overview & Problem | https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ | Canonical organizer URL (external host blocked by sandbox outbound allowlist; competition rules & metric verified via `gems-prize-reference-solution` and repo manifests). |
| DrivenData Competition #306 Data Tab | https://www.drivendata.org/competitions/306/competition-doe-gems/data/ | Login-gated external host; 12 exact competition/external inputs restored locally and SHA-256 verified via `python scripts/restore_inputs.py` against [`registry/session_manifest.json`](registry/session_manifest.json). |
| Official Organizer Benchmark (`Prof. John Lipor`) | https://github.com/drivendataorg/gems-prize-reference-solution | **Verified live via GitHub API** (`unet-mc-cv-reference-solution.ipynb`, Monte-Carlo CV U-Net). |
| DOE GEMS Prize Official Rules PDF (NREL/OSTI) | https://docs.nlr.gov/docs/fy26osti/96647.pdf | Canonical official rules URL (external host outside sandbox GitHub/PyPI allowlist). |
| USGS GeoDAWN Radiometric/Aeromagnetic Compilation | https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7 | Pinned 4-band subset `.cache/gems_inputs/external/geodawn_rad_u8.tif` SHA-256 verified (`12/12 OK`). |
| DOE GDR #1391 / GBCGE INGENIOUS Dataset | https://gdr.openei.org/submissions/1391 · https://gbcge.org/current-projects/ingenious/ | Pinned footprint thermal well/spring table `.cache/gems_inputs/external/gdr_wellspring_in_footprint.csv` (`27,092` rows) SHA-256 verified. |
| USGS SGMC Bedrock Fault Compilation | https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d | Pinned 100 m off-catalogue control `.cache/gems_inputs/derived_sgmc_faults_100m_u8.tif` (`62,703` eval pixels `>3 px` from `existing_faults`) SHA-256 verified. |
| CRS `EPSG:32611` & Tversky Index Reference | https://epsg.io/32611 · https://en.wikipedia.org/wiki/Tversky_index | Verified in raster headers (`NAD83 / WGS84 UTM Zone 11N`, `100 m` pixels, `3730 × 3292`) and `vendor/gems57/metric.py` (`α=0.2, β=0.8`). |
| Public GEMSDOE Submission Registry (`102` repos) | https://github.com/buffedlizard55-lab | **Verified live via GitHub API + SHA-1 blob cache:** `1,655` TIFF paths -> `1,306` unique blobs -> `1,300` single-band template-grid rasters audited in [`evidence/scarpdipole_public_registry_uniqueness.json`](evidence/scarpdipole_public_registry_uniqueness.json). |

### Explicit Limitations
1. **No Live DrivenData Receipt in This Checkout:** Outbound network access is restricted to GitHub/PyPI/npm, and live DrivenData weekly slots (`3/week`) are never spent autonomously. Every evaluation here is `HOLDOUT-DTI`, `PROXY`, or `REGISTRY-MEASUREMENT`.
2. **Universal Literal Overlap Saturation (`17GEMSDOE`):** Because `17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` is strictly positive on `100.0%` of footprint cells (`5,167,373 / 5,167,373`), the literal all-rasters `>70%` positive-support rule rejects **every** nonempty submission until a human selector explicitly scopes the 3-px dot-overlap check to sparse dot fields (`<= 60,000` dots).
3. **Hardware Envelope:** Built and verified on CPU-only sandbox (`2` vCPUs, `3.8 GiB` RAM, `0 B` swap); closing the gap toward `0.44+` continuous U-Net ensembles requires an off-sandbox GPU run (`docs/NEXT_STEPS.md`).

---

## 7. Reproducible Autonomous Workflow

```bash
# 1. Stage and SHA-256 verify all 12 competition & external inputs (no DrivenData login required)
.venv/bin/python scripts/restore_inputs.py
.venv/bin/python scripts/verify_manifest.py

# 2. Build the 3 deterministic SCARPDIPOLE doses via shared submission_writer.py + 10/10 format gates
.venv/bin/python scripts/build_scarpdipole_variants.py

# 3. Audit pre-placement surface & final dots against the 1,300-raster public registry (cached or live)
.venv/bin/python scripts/audit_public_registry.py --cache-only \
  --candidate docs/downloads/h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-zeros.tif \
  --surface .cache/diag/scarpdipole_S_pct.npy \
  --out evidence/scarpdipole_public_registry_uniqueness.json \
  --downloads-copy docs/downloads/scarpdipole_public_registry_uniqueness.json

# 4. Run shared evaluate_holdout.py v2 (fold-fair + static), leakage canaries, SGMC control & Run Card
.venv/bin/python scripts/report_scarpdipole_proxies.py

# 5. Run all repository gates and pytest suite
make manifest && make verify && make site && make ledger
.venv/bin/pytest -q
```

---

## 8. Canonical JSON Run Card (`evidence/scarpdipole_run_card.json`)

- **Candidate:** `h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-zeros.tif`
- **SHA-256 (`zeros`):** `9febfbd7e301d708b0f60df08dc4add6bd5bd442909ea653bcd2a83a92d36262`
- **Submission Name:** `GEMSDOE92-SCARPDIPOLE-f42dipole-20261024`
- **Submission Note (`95` chars `<= 140`):** `SCARPDIPOLE f42dipole: 15815 off-H19 scarp-dipole dots + 21839 piedmont H19 dots (37,654 total)`
- **Validator:** `passed = true` (`10/10` gates, `0` NaN inside/outside footprint, `[0.0, 1.0]`, `EPSG:32611`, `3730 × 3292`)
- **Verdict:** `negative` (`submission_eligible: false` under un-waived literal all-rasters rule due to `17GEMSDOE` 100%-footprint saturation; `#1` technical candidate in `GEMSDOE92` across fold-fair `HOLDOUT-DTI`, static `HOLDOUT-DTI`, and sparse-submission uniqueness `0 / 1,004`).

---

<details>
<summary><strong>Standing User Prompt & Session Operating Contract (Read at Start of Every Session — Full Text)</strong></summary>

See also [`SESSION_PROMPT.md`](SESSION_PROMPT.md), [`IRREGULARITIES.md`](IRREGULARITIES.md), [`SLOT_PLAN.md`](SLOT_PLAN.md), and [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md).

```markdown
Review the repo.

THE FOLLOWING IS THE HIGHEST URGENCY AND MUST BE FOLLOWED!

MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION. DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION. BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION. IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED TIF SUBMISSION.

There should be an easy to download submission tif file as described by the prompt. Read the entire prompt. A lot of sites mention inspection only and a human inspector, but the inspection needs to be done through the project and needs to be validated for submission without human intervention.

PARALLEL-RUN PROTOCOL — read first. This session is one of several running from this same prompt.

1. LANE. Your lane is the single method paragraph below. Stay inside it. If your raster's rank-correlation with any registry raster exceeds [0.90], or more than [70%] of your dots fall within 3 px of one registry raster's dots, you have drifted into another lane: log it as a duplicate and stop. Check this on the surface before placement AND on the final dots.

2. REUSE, DON'T REBUILD. Use the template's cached feature stack, evaluate_holdout.py and submission_writer.py. Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive every catalogue-based feature only from the visible faults, mask visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared tool is wrong, fix it once in the template and report it; never keep a private fork.

3. LABEL EVERY NUMBER as HOLDOUT-DTI (evaluator version, number of withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). A projection is never written as a score.

4. LEAKAGE CANARY. Test each feature alone on the holdout before trusting any result. AUC above [0.90] means leakage until proven otherwise.

5. RUN CARD. End with one JSON card: hypothesis; mechanism; the named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output (no NaN inside the footprint, values in [0,1], CRS/shape/transform match); submission name + note of at most 140 characters; verdict promote / negative. Negative results are deliverables.

6. BUDGET. Stop after [3] experiments or [2] hours. Do not pick submissions: promotion to a real slot is a separate selector step, within the weekly cap shown on the submission page.

WE NEED TO STUDY, ANALYZE, AND UNDERSTAND THE HIGHEST SCORE FROM THE GEMDOE SITE WHERE THE SUBMISSION TIF IS DOWNLOADED FROM WHICH IS THE FOLLOWING:
https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html
h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778
Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.2778?
Answer the question using Phd level experience, knowledge, and judgement. Then use the answer to generate a unique TIF submission into the competition. Must be unique submission unlike any within the GEMSDOE sites above. Verify working line by line no hallucinations.
Current competition leaderboard GEMSDOE high score: 0.4413
```

</details>
