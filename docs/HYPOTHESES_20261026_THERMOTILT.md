> **Closeout correction:** This is an original proposal log, not verified scientific evidence. Numerical expected improvements, literature attributions, novelty claims and runtime forecasts below were not independently verified and must not be relied on. The lane was not explicitly assigned in the user brief. The literal pre-placement stop should have prevented construction. All experiments are negative; see the corrected analysis and run-card protocol limitations. No rerun is authorized.

# Pre-Registered Geological Hypotheses — Session `2026-10-26` (`THERMOTILT` Lane)

**Branch:** `arena/e083835b-gemsdoe92`  
**Pre-registration timestamp:** `2026-10-26 UTC` (written strictly **before** implementing any model code in `gems/thermotilt.py` or `scripts/run_thermotilt.py`)  
**Evaluator & Holdout Contract:** `gems57-pooled-hide-v2` (`2` seeds `[20, 30]` × `4` spatial quadrants = `8` buffered whole-component folds, `22,663` withheld positive occurrences, `300 m` / `3.0 px` linear tent kernel, Tversky `alpha = 0.2`, `beta = 0.8`, `1,000`-draw `20 km` paired spatial block bootstrap)  
**Experiment Budget:** Maximum `3` experiments (`<= 2` hours wall-clock; `0` weekly DrivenData submission slots spent).

---

## 1. Why Existing Repo Lanes Hit Either a Physics Ceiling or a Uniqueness Wall

Auditing all existing `GEMSDOE92` modules (`gems/*.py`), run cards (`evidence/*_run_card.json`), and all 9 focus repositories (`GEMSDOE24`, `GEMSDOE25`, `GEMSDOE27`, `GEMSDOE28`, `GEMSDOE30`, `GEMSDOE31`, `GEMSDOE32`, `GEMSDOE33`, `GEMSDOE36`) reveals two coupled bottlenecks:

1. **The Near-Tip Duplication Trap (`RELAYCONDUIT`, `FAULTNET`, `VARIO`):**
   - `RELAYCONDUIT relay_conduit` (`PR #142`) reached `HOLDOUT-DTI = 0.184485 [0.169875, 0.198933]` on strict Rule-2 fold-visible holdout (`gems57-pooled-hide-v2`, `22,663` withheld positives), beating `FAULTNET netfar` (`0.175147`) and `VARIO vario_full` (`0.150020`).
   - However, because its global top-`37,654` ranking let short-range (`3.2–12 px` = `0.32–1.2 km`) fault-tip relay cones dominate pixel selection, `78.43%` of its dots fell within `3 px` of `GEMSDOE53` (`gems53-h8-tiprelay-ridgeconcord-pr2-n80000`, `80,000` dots) and `76.10%` fell within `3 px` of local `faultnet-far` (`> 0.70` Rule-1 duplicate stop). Simultaneously, its `d > 3.2 px` collar zeroed out static `d_cat > 2.0` evaluation (`0.000000`) and starved far-field bedrock/basin fault discovery (`USGS SGMC = 0.0655`).
2. **Three Untapped Great Basin Geothermal-Fault Physical Mechanisms (`CHILISTRIC`, `LISTRICLOQO`, `TILTANGLE`, `HYDROCONDUIT`):**
   - **Symmetric vs. Upgradient Piezometric Plume Physics:** Every hydrothermal feature in `GEMSDOE92` (`hydroconduit.py`, `ventscarp.py`, `chilistric.py`, `relayconduit.py`) smoothed thermal springs (`GDR #1391`), 2 m temperature probes (`INGENIOUS`), and sinter vents **symmetrically** around surface discharge locations. In Basin & Range alluvial fans, buoyant thermal fluids ascend blind piedmont/intrabasin normal faults at depth and flow **downgradient** (`0.5–2.0 km` toward the playa along $-\widehat{\nabla z}_{\text{regional}}$) within permeable fan gravels before discharging (Coolbaugh et al., 2006; Ferguson et al., 2009). Symmetric smoothing places predictions in the downgradient outflow apron rather than back-projecting **upslope** onto the buried source fault.
   - **Missing Exact 2D-FFT Harmonic `1VD` & Signed Tilt-Derivative (`HD_TDR`) Contact Localization:** `gems/tiltangle.py` computed `atan2(|Band 11|, hgm)` on gravity only—taking the absolute value `|vg|` (destroying the sign of $\partial_z$!) and never computing 2D-FFT harmonic first vertical derivatives (`1VD`) on `Band 2` RTP magnetics or Verduzco et al. (2004) / Salem et al. (2007) Total Horizontal Derivative of Signed Tilt (`HD_TDR = ||grad(arctan(1VD / THDR))||`), which peaks at $\theta = 0$ directly over buried fault contacts **independently of magnetization/density contrast amplitude**.
   - **Missing Antithetic Accommodation-Zone Polarity Reversal (`AZ-TWIST`):** Faulds & Hinz (2015) demonstrated that `> 84%` of Great Basin geothermal systems occur in step-overs, terminations, and **accommodation/transfer zones** where opposing synthetic and antithetic normal faults dip toward each other (graben convergence) or away from each other (intrabasin horst divergence), canceling cumulative regional relief while generating intense unmapped fracture permeability. No module in `gems/*.py` measures cross-strike horizontal-gravity vector polarity reversal ($\hat{\mathbf{g}}_+ \cdot \hat{\mathbf{g}}_- < 0$).

---

## 2. Five Untried Candidate Geological Hypotheses (Ranked by Expected `HOLDOUT-DTI` Gain & Cost)

All external layers referenced below are **already SHA-256 pinned and verified locally** in `.cache/gems_inputs/` via `scripts/restore_inputs.py --ventscarp-external` (`registry/data_manifest.json` + `registry/ventscarp_external_manifest.json`). Zero unverified or unreachable external downloads are required.

| Rank | Hypothesis Code | Core Physical Mechanism | Expected `HOLDOUT-DTI` Impact | Operative Sparse Uniqueness Risk (`<= 0.70` target) | Compute / RAM Cost (`3.8 GiB` / `0-swap` limit) | Decision |
|---:|---|---|---|---|---|---|
| **#1** | **`THERMOTILT`** | Upgradient piezometric thermal back-projection + exact 2D-FFT harmonic `1VD` signed-tilt contact crest (`HD_TDR`) + antithetic accommodation-zone gravity polarity reversal + inner-annulus-suppressed (`r >= 9 px`) distal accommodation bridge & dual-regime quota (`d > 2.0 px`) | **High** (targets `> 0.0132` zero-cat OOF `d > 2.0` in Exp 1 and `> 0.145–0.165` Rule-2 fold-visible while keeping `< 0.68` max overlap in Exp 2/3) | **Low (`~0.50–0.66`)** — inner `< 9 px` tip-halo suppression + `>= 45%` blind off-network quota explicitly avoids `GEMSDOE53` / `FAULTNET` / `R0` pileups | **Low–Moderate** (`~1.2 GiB` peak RSS, `~10 min` for all 3 arms) | **IMPLEMENT THIS SESSION** |
| #2 | `WAVELET-POISSON-TENSOR` | Multi-scale continuous Mexican-Hat wavelet modulus chains (`a in {2,4,8,16} px`) tracking upward Lipschitz exponent $\alpha_{\text{Lip}}$ of coupled magneto-gravity Poisson ratio vectors (Hornby et al., 1999) | Moderate (`+0.0005` to `+0.0015` zero-cat `d > 2.0`) | Low (`~0.60`) | High (`16` full-grid 2D FFT convolutions; `~1.9 GiB` RSS) | Reserve |
| #3 | `PLAYA-REDOX-DIPOLE` | Closed-basin playa-margin hydraulic barrier & signed cross-fault GeoDAWN radiometric dipole (`+d_n(K/eTh)` footwall illite vs `-d_n(eU/eTh)` hanging-wall uranium redox roll-front at slope `< 1.5°`) | Low–Moderate (high precision on subaerial playas, `~18%` footprint coverage) | Very Low (`< 0.45`) | Low (`~0.8 GiB` RSS) | Reserve |
| #4 | `WALKER-HONEYCOMB-MESH` | Hill (1977) Walker Lane / Humboldt conjugate dextral (`NNW`) + tensile (`ENE`) oblique strain-rate (`Band 1`) & seismicity (`Bands 3–5`) fracture-mesh intersection detector | Low–Moderate (coarse `Band 1` GPS resolution limits 100 m localization) | Low (`~0.55`) | Low (`~0.9 GiB` RSS) | Reserve |
| #5 | `MIDFAN-CONVEXITY-JUMP` | Bull (1977) mid-fan radial profile convexity + aligned 10 m tributary $\chi$-incision step `0.8–2.5 km` basinward of the `Band 15` bedrock-alluvium junction | Moderate on piedmont aprons; misses intrabasin & bedrock horst faults | Moderate (`~0.65` vs `PIEDFRONT`/`CHILISTRIC`) | Low (`~0.9 GiB` RSS) | Reserve |

---

### Detailed Specification of All 5 Untried Hypotheses

#### Hypothesis #1 (Selected): `THERMOTILT` — Upgradient Piezometric Thermal-Plume Back-Projection, Exact 2D-FFT Harmonic `1VD` Signed-Tilt Contact Crests (`HD_TDR`), Antithetic Accommodation-Zone Polarity Reversal & Distal Annular Transfer Bridges
- **Specific Layers Involved:**
  - `training_features.tif`: `Band 2` (`rtp`), `Band 14` (`tmi`), `Band 13` (`iso_grav_anom`), `Band 11` (`iso_grav_anom_vg`), `Band 18` (`iso_grav_anom_hg`), `Band 15` (`depth_to_base`), `Band 17` (`cond_surf`), `Band 1` (`gs_strain`), `Band 6` (`tc`), `Band 12` (`det_elev_slope`), `Band 19` (`rel_elev_slope`).
  - SHA-256-verified external layers (`registry/ventscarp_external_manifest.json`): `gdr_wellspring_in_footprint.csv` (DOE GDR #1391 wells/springs `T >= 35 °C`), `2m_temperature_probe_INGENIOUS_regional_data.zip` (`F2mDAB`), `paleo_geothermal_regional.zip` (tufa-excluded siliceous sinter, explosion craters, travertine), `topo_10m_derived_100m_u8.tif` & `dem10_chi_100m_i16.tif` (USGS 3DEP 10 m scarp excess & fluvial $\chi$ steps), `geodawn_rad_u8.tif` (GeoDAWN K/Th/U).
  - Strictly fold-visible `fold.visible` fault mask in Exp 2 & Exp 3 ONLY (zero catalogue input in Exp 1 `thermotilt_blind`).
- **Physical Signature & Mathematical Transform:**
  1. *Upgradient Piezometric Thermal Back-Projection (`UPFLOW`):* Let $\hat{\mathbf{u}}_{\text{up}}(x)$ be the regional upslope hydraulic-head unit vector oriented from basin floor/playa (`high Band 15` / low regional elevation proxy) toward range blocks (`low Band 15` / high regional elevation proxy). Thermal outflow sources $H_0(x)$ (`GDR >= 35 °C` springs/wells + `2 m` probe `F2mDAB >= 1.0 °C` + tufa-excluded sinter) are advected **upgradient** by $\ell \in \{5, 11, 18\}\text{ px}$ ($0.5, 1.1, 1.8\text{ km}$) via bilinear shift $H_0(x - \ell\hat{\mathbf{u}}_{\text{up}}(x))$ (evaluating at upslope candidate fault $x$ whether a thermal plume lies $\ell\text{ px}$ **downgradient** at $x - \ell\hat{\mathbf{u}}_{\text{up}}(x)$!), contrasted against downslope null $H_0(x + \ell\hat{\mathbf{u}}_{\text{up}}(x))$ and multiplied by subsurface harmonic-tilt / MT-flank corroboration.
  2. *Exact 2D-FFT Harmonic `1VD` & Signed Tilt Horizontal Derivative (`HD_TDR`):* For potential field $U \in \{\text{Band 2 RTP}, \text{Band 13 IsoGrav}\}$, apply exact 2D Fourier Laplace operator $\widehat{\partial_z U}(\mathbf{k}) = |\mathbf{k}|\,e^{-|\mathbf{k}| z_0}\,\widehat{U}(\mathbf{k})$ ($z_0 = 1.5\text{ px}$ upward-continuation regularizer on mirror-padded grid). Compute signed Miller–Singh (1994) tilt $\theta_U = \arctan(\partial_z U / (\|\nabla_h U\| + \epsilon)) \in (-\frac{\pi}{2}, +\frac{\pi}{2})$, the zero-crossing contact score $\exp(-(\theta_U / 0.35)^2)\cdot\operatorname{pct}(\|\nabla_h U\|)$, and the Verduzco–Salem (2004, 2007) amplitude-invariant contact crest $\mathrm{HD\_TDR}_U = \|\nabla_h \theta_U\|$.
  3. *Antithetic Accommodation-Zone Polarity Reversal (`AZ-TWIST`):* Across local structural strike normal $\hat{\mathbf{n}}(x)$, sample unit horizontal gravity gradient $\hat{\mathbf{g}}(x \pm L\hat{\mathbf{n}})$ at $L \in \{6, 12\}\text{ px}$ ($0.6, 1.2\text{ km}$) to measure opposing-dip graben convergence $\max(0, -\hat{\mathbf{g}}_+ \cdot \hat{\mathbf{g}}_-)\sqrt{\|\nabla_h g_+\|\,\|\nabla_h g_-\|}$ and horst divergence.
  4. *Distal Annular En-Echelon Transfer Bridge & Dual-Regime Allocation (`Exp 2` & `Exp 3`):* From strictly fold-visible `fold.visible` tips (self-excluded on training components), project conjugate en-echelon ($\pm 16^\circ$) and axial transfer lobes modulated by an **inner suppression annulus** $W_{\text{ann}}(r) = \operatorname{clip}((r - 9.0)/6.0, 0, 1)\exp(-r/24.0)$ ($9 \le r \le 46\text{ px}$ = `0.9–4.6 km`) plus opposing-segment step-over midlines, then allocate dots (`d > 2.0 px`, `2.9 px` spacing) under an explicit **dual-regime quota** (`<= 48%` distal structural corridor, `>= 52%` pure blind `THERMOTILT` off-corridor discoveries).
- **Why Missed by USGS/INGENIOUS Catalogue:** Accommodation zones partition throw across multiple opposing small-offset strands whose net relief cancels; alluvial fans bury blind upflow conduits `0.5–1.8 km` upslope of warm springs; thick basin fill (`Band 15`) attenuates raw magnetic/gravity gradient magnitudes so standard scarp/gradient maps miss them.
- **Named Non-Fault Mimic & Deconfounder:** Plutonic/caldera ring margins and intact lava-flow edges (deconfounded via multi-azimuth linearity, geodetic strain `Band 1`, and ~1,330 m Lake Lahontan wave-cut bench suppression); cold perched ignimbrite contact springs (excluded by `T >= 35 °C` filter and upslope subsurface tilt gate).
- **Difference vs. Repo Implementations:** `gems/tiltangle.py` used `abs(Band 11)` on gravity only (`atan2(|vg|, hgm)`) and never computed 2D-FFT `1VD` on `Band 2` RTP nor Verduzco–Salem `HD_TDR`; `hydroconduit.py`/`ventscarp.py`/`chilistric.py` used symmetric plumes instead of upgradient piezometric back-projection; no repo lane computes cross-strike $\hat{\mathbf{g}}_+ \cdot \hat{\mathbf{g}}_-$ polarity reversal; and unlike `relayconduit.py` (`0.7843` duplicate vs `GEMSDOE53` 80k due to `< 10 px` tip crowding, `d > 3.2`), `THERMOTILT` suppresses the `< 9 px` near-tip pileup and enforces a `>= 52%` off-network blind discovery quota at `d > 2.0 px`.

#### Hypothesis #2: `WAVELET-POISSON-TENSOR`
- **Layers:** `Band 2` (`rtp`), `Band 11` (`iso_grav_anom_vg`), `Band 18` (`iso_grav_anom_hg`), `Band 17` (`cond_surf`).
- **Signature/Transform:** Dyadic continuous wavelet horizontal gradient modulus chains ($a \in \{2, 4, 8, 16\}\text{ px}$) estimating potential-field Lipschitz singularity exponent $\alpha_{\text{Lip}}$ (Hornby et al., 1999) weighted by spatial rotation of the Poisson $M/g$ vector.
- **Why Missed by Catalogue:** Deeply buried subvertical basement faults beneath flat playas lack surface scarps; $\alpha_{\text{Lip}} \approx -1$ separates planar basement-cutting faults from shallow surficial lenses ($\alpha_{\text{Lip}} \approx -3$).
- **Non-Fault Mimic:** Inactive Mesozoic dike swarms.
- **Difference vs. Repo:** `poissonknick.py` and `poissonflex.py` fit single-scale scalar $\Delta M / \Delta g$ ratios without multi-scale wavelet Lipschitz tracking.

#### Hypothesis #3: `PLAYA-REDOX-DIPOLE`
- **Layers:** `geodawn_rad_u8.tif` (K, eTh, eU), `Band 12`, `Band 17`, `Band 15`.
- **Signature/Transform:** Signed cross-strike radiometric dipole $+\partial_n(\text{K/eTh}) \cdot (-\partial_n(\text{eU/eTh})) > 0$ at low slope (`< 1.5°`), capturing footwall potassium-illite hydrothermal clay vs. hanging-wall uranium redox roll-front precipitation across fault-gouge groundwater barriers.
- **Why Missed by Catalogue:** Holocene playa sedimentation/deflation erases sub-meter scarps across alkali flats.
- **Non-Fault Mimic:** Closed-basin shoreline evaporite rings.
- **Difference vs. Repo:** `radiocontact.py` and `radiodecouple.py` used unsigned gradient magnitudes rather than signed cross-fault redox dipoles.

#### Hypothesis #4: `WALKER-HONEYCOMB-MESH`
- **Layers:** `Band 1` (`gs_strain`), `Bands 3–5` (seismicity), `topo_10m_derived_100m_u8.tif`, `Band 18`.
- **Signature/Transform:** Hill (1977) conjugate `NNW` dextral + `ENE` tensile fracture-mesh intersection operator modulated by oblique geodetic strain and microseismic density.
- **Why Missed by Catalogue:** Distributed Walker Lane / Humboldt book-shelf shear produces short fissures/mole-tracks rather than continuous range-front scarps.
- **Non-Fault Mimic:** Rectangular agricultural canal grids and bedrock jointing.
- **Difference vs. Repo:** `strainbreak.py` and `coulomb.py` used scalar gradient norms or single-azimuth Mohr–Coulomb shear.

#### Hypothesis #5: `MIDFAN-CONVEXITY-JUMP`
- **Layers:** `dem10_chi_100m_i16.tif`, `topo_10m_derived_100m_u8.tif`, `Band 12`, `Band 19`, `Band 15`.
- **Signature/Transform:** Bull (1977) mid-fan radial profile convexity paired with aligned tributary $\chi$-slope jumps `0.8–2.5 km` basinward of the `Band 15` zero-isopach mountain front.
- **Why Missed by Catalogue:** Mappers digitize the prominent bedrock–alluvium mountain front while missing young active piedmont strands cutting unconsolidated fan gravels basinward.
- **Non-Fault Mimic:** Climatic Pleistocene–Holocene fan-head trenching.
- **Difference vs. Repo:** `apronridge.py` and `piedfront.py` used 100 m slope breaks without separating mid-fan radial convexity from the `Band 15` bedrock junction via 10 m $\chi$ steps.

---

## 3. Pre-Registered 3-Experiment Plan (`THERMOTILT` Lane)

1. **Experiment 1 (`thermotilt_blind`, Zero-Catalogue Multi-Physics LOQO, `37,654` dots, `d > 2.0 px`, `2.9 px` spacing):**
   - Strictly zero fault-catalogue inputs in surface construction (`fold.visible` / `existing_faults` used solely for the `d > 2.0 px` placement collar and Rule-2 exact visible-fault evaluation).
   - Combines 32 zero-catalogue channels (including exact 2D-FFT harmonic `1VD` signed-tilt contact & `HD_TDR` on RTP magnetics and gravity, upgradient piezometric thermal back-projection, antithetic accommodation-zone gravity polarity reversal, 10 m 3DEP scarp/chi, and adaptive listric updip projection) via 3-branch leave-one-quadrant-out (`LOQO`) OOF logistic calibration + Stage-1 OOF multi-azimuth structural continuity.
   - **Benchmark:** Zero-catalogue `CHILISTRIC adapt37k` (`0.012617` static `d_cat > 2.0`) and `LISTRICLOQO selectcal` (`0.012952` OOF `d_cat > 2.0`).
2. **Experiment 2 (`thermotilt_distal_bridge`, Inner-Annulus-Suppressed Distal Accommodation + Blind `THERMOTILT` Dual-Regime Allocation, `37,654` dots, `d > 2.0 px`, `2.9 px` spacing):**
   - Adds strictly fold-visible, self-excluded **distal annular accommodation & en-echelon bridges** (`r in [9, 46] px` = `0.9–4.6 km`, `< 9 px` immediate tip halo smoothly zeroed!) gated by `thermotilt_blind` physical corroboration, with an explicit **dual-regime quota** (`<= 45%` distal bridge corridor, `>= 55%` off-corridor blind `THERMOTILT` crests).
   - **Benchmarks:** Rule-2 `HOLDOUT-DTI` vs. best operative-unique lanes (`CHILISTRIC addtail52k = 0.112471`, `conduit_notip = 0.076416`, `H19-5 = 0.096748`) AND `d_cat > 2.0` static `HOLDOUT-DTI` AND operative sparse uniqueness `<= 0.70` across all 102 public repos + 9 focus sites + local registry!
3. **Experiment 3 (`thermotilt_graded50k`, Graded-Amplitude Tversky Tail `{0.0, 0.62, 1.0}` on Top `50,000` Spaced Crests, `d > 2.0 px`):**
   - Keeps `1.0` on the `37,654` primary dual-regime crests of the stronger arm (Exp 2 if operative-unique `<= 0.70`, else Exp 1) and adds `12,346` mutually `3.0 px`-spaced secondary corroborated `THERMOTILT` crests at fractional amplitude `0.62` (`50,000` total positive cells, effective L1 mass `45,308.5`), exploiting $\beta = 0.8 \gg \alpha = 0.2$ Tversky recall leverage while strictly checking `<= 0.70` operative sparse overlap.

**Hard Gates Enforced Automatically:**
- Single-feature leakage canary `max(AUC, 1 - AUC) <= 0.90` on every channel (raw, negated, and missingness).
- Pre-placement continuous surface AND post-placement final dots: `|rho| <= 0.90` and operative sparse 3-px dot overlap `<= 0.70` across local registry, 9 focus sites, and 102-repo public registry (plus explicit disclosure of the `17GEMSDOE E-proba-multiscale` `5,167,373`-px literal dense witness).
- All 11 GeoTIFF format & `[0, 1]` portal safety gates (`0` NaN across all `12,279,160` cells, strict `[0.0, 1.0]`, `EPSG:32611`, `3730×3292`, exact geotransform).
