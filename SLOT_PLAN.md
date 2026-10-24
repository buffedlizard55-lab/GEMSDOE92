# SLOT_PLAN — Current Selector State (2026-10-24)

## Primary Artifact: `SCARPDIPOLE f42dipole` — Format-Valid (`10/10`), `#1` on Both Holdout Regimes, `+12.26%` on `USGS SGMC`, `0 / 1,004` Sparse-Submission Overlaps `> 70%`, Recorded `negative` Under Un-Waived Literal All-Rasters Gate (No Live Slot Spent)

`h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-zeros.tif` (submission name `GEMSDOE92-SCARPDIPOLE-f42dipole-20261024`, SHA-256 `9febfbd7e301d708b0f60df08dc4add6bd5bd442909ea653bcd2a83a92d36262`) is the primary downloadable GeoTIFF on the GitHub Pages site (`docs/downloads/`).

- **Format & Portal Validation (`10/10` PASS):** `float32`, single band, `3730 × 3292`, `EPSG:32611`, exact sample geotransform, `0` NaN inside footprint, `0` NaN outside footprint, `0` Inf anywhere, values strictly in `[0.0, 1.0]`, `37,654` unit-mass dots (`21,839` piedmont-reranked `H19-5` dots + `15,815` off-skeleton `>3 px` scarp-dipole dots), `0.0` mass on `existing_faults`, `min(d_cat) = 2.2361 px > 2.0 px`.
- **Fold-Fair Hide-and-Recover `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `n = 22,663` withheld positives, 8 folds, `d_visible > 2.0 px` per fold):**
  - `SCARPDIPOLE f42dipole`: **`0.098565 [0.087985, 0.108974]`** (`#1` in `GEMSDOE92`)
  - Paired Δ vs `parent_B2_visible` (`0.029074`): **`+0.069492 [+0.060008, +0.077790]`** (`3.39×` parent)
  - Paired Δ vs `visible_collar` (`0.046866`): **`+0.051699 [+0.037872, +0.064896]`** (`2.10×` prior holdout high)
- **Static Final-Raster `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `n = 22,663`, `d_full_catalogue > 2.0 px` pre-punched):**
  - `SCARPDIPOLE f42dipole`: **`0.006812 [0.005770, 0.008034]`** (`#1` in `GEMSDOE92`)
  - Paired Δ vs `R0` (`0.004006`): **`+0.002806 [+0.001946, +0.003686]`**
  - Paired Δ vs `BREAKLINE f45Ltop` (`0.004861`): **`+0.001951 [+0.001091, +0.002781]`**
  - Paired Δ vs `RELIEF p10` (`0.006045`): **`+0.000767 [-0.000090, +0.001595]`**
- **Off-Catalogue `USGS SGMC` Bedrock-Fault Control (`PROXY`, `n = 62,703` pixels `>3 px` from `existing_faults`):**
  - `SCARPDIPOLE f42dipole`: **`0.107841`** (`+12.26%` above `R0 = 0.096060`; vs `visible_collar = 0.021192`, `-77.94%`).
- **Leakage Canary (`<= 0.90` gate):** Max raw band symmetric AUC = **`0.5531`**; `SCARPDIPOLE S_pct` symmetric AUC = **`0.6328`** (`PASS`).
- **`REGISTRY-MEASUREMENT` (`1,300` compatible rasters across `102` public `buffedlizard55-lab` GEMSDOE repos):**
  - **Local `GEMSDOE92` registry (`20` prior rasters):** `PASS` (`worst_local_3px_overlap = 0.6605 <= 0.70`, `worst |ρ| = 0.2698 <= 0.90`).
  - **All sparse dotted public submissions (`<= 60,000` dots, `n = 1,004` across all `102` repos):** **`0 / 1,004` rasters `> 70%` overlap** (`max = 0.6877` vs `GEMSDOE48/H57-ds-relief-augmented`; `max |ρ| = 0.2742`).
  - **Binding literal all-rasters rule (no continuous-surface exemption):** **`STOP` (`verdict: negative`, `submission_eligible: false`)** because `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` is strictly positive on all **`5,167,373 / 5,167,373`** footprint pixels (`100.0%` forward 3-px overlap for every nonempty submission; `123` dense/wide rasters `>70%` total; global `max |ρ| = 0.3152 << 0.90`).

No weekly DrivenData submission slot was spent in this session. Promotion to a live weekly slot requires an explicit human selector decision scoping the 3-px dot-overlap check to sparse dot-field submissions (`<= 60,000` dots).

---

## Audited Cross-Lane Comparison Table (`GEMSDOE92`)

| Candidate / Baseline | Dots | Fold-Fair `HOLDOUT-DTI` (`d_vis > 2`) | Static `HOLDOUT-DTI` (`d_cat > 2`) | Off-Cat `USGS SGMC` (`PROXY`) | Local `<=3 px` Max Overlap | Public Sparse (`<=60k`, `n=1,004`) `>70%` Count | Public All-Rasters (`n=1,300`) Binding Verdict | Live Slot Recommendation |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `R0` (`h33-h33-2-b2`, parent `CLAIM 0.2778`) | 37,654 | `0.029074` *(as `parent_B2_visible`)* | `0.004006` | `0.096060` | `1.0000` (is `R0`) | — | Reference parent | Already submitted upstream (`GEMSDOE32`) |
| **`SCARPDIPOLE f42dipole` (Primary)** | **37,654** | **`0.098565` `[0.0880, 0.1090]`** | **`0.006812` `[0.0058, 0.0080]`** | **`0.107841` (`+12.3%`)** | **`0.6605` (PASS)** | **`0 / 1,004` (`max 0.6877`)** | **`negative` (`17GEMSDOE` 100% surface)** | **Hold slot unless selector scopes gate to sparse dot fields (`#1` technical candidate)** |
| `SCARPDIPOLE f45dipole` | 37,654 | `0.097641` `[0.0871, 0.1075]` | `0.006719` `[0.0056, 0.0079]` | `0.107849` (`+12.3%`) | `0.6634` (PASS) | `0 / 1,004` (`max 0.6657`) | `negative` (`17GEMSDOE` 100% surface) | Dose sibling — never pair with `f42dipole` in same week |
| `SCARPDIPOLE f50dipole` | 37,654 | `0.094286` `[0.0840, 0.1036]` | `0.006516` `[0.0054, 0.0077]` | `0.107692` (`+12.1%`) | `0.6665` (PASS) | `0 / 1,004` (`max 0.6348`) | `negative` (`17GEMSDOE` 100% surface) | Dose sibling — never pair with `f42dipole` in same week |
| `visible-collar-r0-excluded` | 37,654 | `0.046866` `[0.0402, 0.0533]` | N/A *(full-cat collar)* | `0.021192` (`-77.9%`) | `0.0352` vs `BREAKLINE` | Fails (`11GEMSDOE` / collar priors) | `negative` (`131` rasters `>70%`) | **Do NOT submit** — collapses `-77.9%` on off-catalogue `SGMC` |
| `BREAKLINE f45Ltop` | 37,654 | — | `0.004861` `[0.0040, 0.0058]` | `0.126105` (`+31.3%`) | `0.5500` vs `R0` | Overlaps `54` `<70%`-halo rasters | `negative` (`122` rasters `>70%`) | Superseded on both holdout regimes by `SCARPDIPOLE f42dipole` |
| `RELIEF p10` / `DILATATION p12` | 37,654 | — | `0.006045` / `0.005781` | `0.087245` (`-9.2%`) | `0.9938` / `0.9937` | Fails (`~99.4%` vs `R0`) | `negative` (`R0` duplicate) | **Do NOT submit** — `99.4%` duplicate of `R0` |
| `TIPGAP far18f33` / `STEPOVER` | 37,654 / 5,000 | — | `0.002724` / `0.000000` | — | `0.6700` / `<0.70` | — | `negative` (below `R0` holdout) | **Do NOT submit** — below `R0` on holdout |

---

## Receipt Decision Rule (If Human Selector Authorizes 1 Weekly Slot for `SCARPDIPOLE f42dipole`)

- **If `ORGANIZER-CONFIRMED` live score `>= 0.2878` (`Δ >= +0.010` vs `R0` `CLAIM 0.2778`):** Off-skeleton piedmont scarp-dipole emission + piedmont `H19-5` re-ranking earn real private/hidden-fault credit; test calibrated `[0, 1]` continuous cover-aware emission or `f45dipole` in a subsequent week.
- **If `ORGANIZER-CONFIRMED` live score `<= 0.2678` (`Δ <= -0.010` vs `R0` `CLAIM 0.2778`):** Dropping `42%` of potential-field `H19-5` mass loses blind sub-alluvial basin-floor faults faster than topographic scarps add piedmont faults; retire pure topographic off-skeleton replacement and pivot to multi-physics U-Net/ensemble learning with organizer-authorized GPUs.
- **If `|Δ| < 0.010`:** Inconclusive within single-submission variance; do **not** spend a second weekly slot on `f45dipole` or `f50dipole`.
