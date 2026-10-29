# Pre-Registration (`2026-10-29`): Untried Geological & Geothermal Hypotheses + `ADMITRELAY` 3-Experiment Protocol

**Branch:** `arena/f7a0fcb3-gemsdoe92`  
**Pre-registration timestamp (before feature/experiment code):** `2026-10-29`  
**Selected single method lane (Rule 1):** `ADMITRELAY` (*Multi-Scale Elastic Admittance Breakdown + Lithology-Deconfounded K/U Hydrothermal Metasomatism + Kinetic Geothermometer Mixing + Pollard–Segall Crack-Tip Relay / Broadside Stress-Shadow + Centerline-Monotone Goodhart-Debiased `LBM-v3`*)  
**Experiment budget (Rule 6):** Strictly `<= 3` experiments (`E1`, `E2`, `E3`), `0` weekly slots spent automatically.

---

## 1. Forensic Motivation from the 2026-10-29 Live Score Receipts

Four previously unscored `2026-10-27` submissions across 4 GitHub owners now carry owner-reported `CLAIM` scores in the `2026-10-29` ledger:

1. **`GEMSDOE92` `gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros`:** **`0.2784` (`CLAIM`)** — **#1 all-time reported score across all 123 repositories / 8 GitHub owners**, surpassing `GEMSDOE32` (`h33-h33-2-b2-...-e5eb6e7e-zeros`, `0.2778` `CLAIM`) by `+0.0006` while keeping full-registry 8-owner sparse/top-N `PI-1` max 3-px overlap at `0.6845 <= 0.70`.
2. **`GEMSDOEkarage1` `karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros`:** **`0.1648` (`CLAIM`)** vs `LBM-v1` prospective `0.1817` (`-0.0169`).
3. **`ApartGEMSDOE3` `apartgemsdoe3-h-apart3-1-cfkc-dhc-37654-20261027T215000Z-9dedadfc-zeros`:** **`0.1625` (`CLAIM`)** vs `LBM-v1` prospective `0.1592` (`+0.0033`).
4. **`KANLERGEMSDOE3` `kanlergemsdoe3-h-k3-1-cadg-submod-exp-k3-3-oof8f-37654-20261026-f0565e6d10f9-zeros`:** **`0.1233` (`CLAIM`)** vs `LBM-v1` prospective `0.1562` (`-0.0329`).

### Exact Mathematical Root Cause of `lbmc1`'s `+0.0561` Goodhart Residual (`0.3345` `LBM-v1` vs `0.2784` `CLAIM`)

Decomposing dot placements by perpendicular Euclidean distance `dh19` from the `H19-5` fault-trace centerline exposes why `lbmc1` beat `0.2778` (`0.2784`) yet fell `0.0561` below `LBM-v1` AND failed `HOLDOUT-DTI` (`0.01970 < 0.09775` `R0_recipe`):

- Every `H19-5` training raster (`GEMSDOE32` `R0`, `GEMSDOE25` `D2.8`, `GEMSDOE31` `SOLO`) placed `100%` of its dots on `dh19 == 0` (`37,654 / 37,654` for `R0`).
- Under the `300 m` (`3 px`) triangular kernel $w(d) = \max(0, 1 - d/3)$, dots on `dh19 == 0` cast `2/3` coverage onto `dh19 == 1`. Under `lam = 1e-3` without a perpendicular monotonicity constraint, `LBM-v1` assigned `dh19 == 1` a **`3.73×` higher multiplier** than `dh19 == 0`!
- Greedy placement (`lbm_place.py`) exploited that collinearity artifact (`Goodhart's Law`), placing **`12,440` dots on `dh19 == 1` (`100 m` parallel flank)** and only **`4,764` dots on `dh19 == 0` (`centerline`)** in `lbmc1` (and `17,382` on `dh19 == 1` in `RIESZ-LOCKED`, `17,326` on `dh19 == 1` in `TIPCOMP`). Stepping `100 m` off a true 1D fault trace loses `1/3` of peak kernel credit and misses withheld `gems57-pooled-hide-v2` fault traces!

---

## 2. Five Untried Geological & Geothermal Hypotheses (Verified Against All 62 `gems/*.py` Modules)

Every hypothesis below was audited via `git grep` across all 62 modules in `gems/*.py` and all prior `docs/HYPOTHESES_*.md` files to confirm genuine novelty.

| Rank | ID & Name | Specific Layers / Bands | Physical Signature & Transform | Why Missing from USGS / INGENIOUS Catalogue | Named Non-Fault Mimic | Expected DTI Gain vs Cost |
|---:|---|---|---|---|---|---|
| **1** | **`H-1029A`**<br>Multi-Scale Flexural Admittance Breakdown & Fault-Wedge Residual (`ADMIT-BREAK`) | `training_features.tif`: `B12 det_elev`, `B13 iso_grav_anom`, `B15 depth_to_base_surf`, `B17 cond_surf` | Local Forsyth (1985) gradient admittance $Z_{gh}(\lambda) = \frac{\langle \nabla g \cdot \nabla h \rangle_\lambda}{\langle \|\nabla h\|^2 \rangle_\lambda + \varepsilon}$ & coherence $\gamma^2_{gh}(\lambda)$ at $\lambda \in \{0.6, 3.0\}\text{ km}$, plus asymmetric hanging-wall porous-breccia gravity deficit $-\Delta g_{\text{wedge}} \times \sigma_{\text{MT}}$ | Blind range-front step-overs and buried intrabasin graben faults beneath $300\text{--}1200\text{ m}$ of Quaternary fill lack surface scarps (`QFaults`), yet sever the elastic plate coupling between topography, gravity, and basement relief | Low-density Late Cenozoic diatomite/lacustrine ash basins (Carson Sink) producing broad isotropic gravity lows rather than linear cross-scale coherence breaks | **High gain / Low cost** (in-cache 100 m physics; `0` matches for `admittance`/`forsyth` in `gems/`) |
| **2** | **`H-1029C`**<br>Pollard–Segall Crack-Tip Relay Lobes + Broadside Stress Shadow + Centerline-Monotone `LBM-v3` (`STRESS-SHADOW-LBM3`) | Fold-visible `vis` (`existing_faults.tif` at deploy; strict Rule 2), `anc_h19_5`, `B07 geod_shearrate`, `B08 geod_dilaterate`, `131` verified `2026-10-29` `CLAIM`s | Angular crack-tip continuation lobe $\cos^3(\Delta\theta)$ ($0.2 < r \le 3.5\text{ km}$) minus perpendicular broadside elastic stress-drop shadow ($|\sin(\Delta\theta)| > 0.85$, $0.3 < r \le 2.5\text{ km}$; Pollard & Segall 1987; Crider & Pollard 1998), coupled with `LBM-v3` enforcing $\rho(d_{H19}=0) \ge \rho(d_{H19}=1) \ge \dots$ | Unmapped breaching relay ramps and synthetic fault growth propagate ahead of mapped tips while broadside stress shadows suppress closely spaced parallel scarps; monotone centerline law cures `dh19=1` Goodhart drift | Radial alluvial-fan incised washes emerging perpendicular ($90^\circ$) to range-front fault scarps (explicitly vetoed by the broadside shadow!) | **Very high gain (both `HOLDOUT-DTI` & `CLAIM` calibration) / Low cost** (`0` matches for `stress_shadow` in `gems/`) |
| **3** | **`H-1029B`**<br>Saunders–Dickson Thorium-Regressed K-Metasomatism & Redox Roll-Front Dipole (`TH-DECONF-REDOX`) | `geodawn_rad_u8.tif` (`K`, `Th`, `U`, `TC`), `geodawn_extensions_u8.tif` (`TMI_up150`), `B14 tmi`, `B15 depth_to_base_surf`, `B17 cond_surf` | Non-linear magmatic-differentiation residual $K_d = K - \hat{f}(Th)$ and $U_d = U - \hat{g}(Th)$ (Saunders et al. 1993; Dickson & Scott 1997) + antiparallel redox-front dipole $\max(0, -\nabla K_d \cdot \nabla U_d) \times \text{demag}(TMI_{\text{up150}}, TMI)$ | Unlike `radiocontact`/`radiodecouple`/`listric_loqo` (which used raw `K/(Th+10)` that explodes over low-$Th$ basalts and fires on felsic ignimbrites), $Th$-regressed $K_d$ isolates epithermal adularia/illite fault-conduit alteration in unmapped volcanic highlands | Potassic playa evaporite crusts and potash-fertilized agricultural fields on flat basin floors (vetoed where slope $< 0.8^\circ$ and $\|\nabla g\| \approx 0$) | **Moderate–high gain / Low cost** (uses pinned GeoDAWN radiometrics & `TMI_up150`) |
| **4** | **`H-1029D`**<br>Giggenbach Kinetic Geothermometer Mixing Gap (`T_NaKCa - T_chalc`) × Clay-Cap Margin (`KINETIC-MIX`) | `gdr_wellspring_in_footprint.csv` (`temp_c`, `geothermquartz_c`, `geothermchalc_c`, `geothermcat_c`; **never** `dist_known_fault_px`), `paleo_geothermal_regional.zip`, `2m_temperature_probe`, `B17 cond_surf` | Slow-equilibrating cation vs fast-equilibrating silica chemical-clock gap $\Delta T_{\text{kin}} = \max(0, T_{\text{Na-K-Ca}} - T_{\text{chalc}})$ (Giggenbach 1988) diffused along regional shear/extension azimuth and gated by MT smectite-cap edge $\|\nabla \log \sigma_{\text{MT}}\|$ | Prior modules collapsed all 3 geothermometers via `max()`; $\Delta T_{\text{kin}} > 0$ specifically fingerprints deep ($>180^\circ\text{C}$) blind basement fault upflow undergoing rapid shallow meteoric mixing before any boiling sinter forms | Saline Ca/Na-rich terminal playa brines (Dixie/Humboldt salt pans) that bias empirical Na-K-Ca thermometry (vetoed in closed topographic sinks) | **Moderate gain / Low cost** (`0` matches for `giggenbach` or `T_cat - T_chalc` in `gems/`) |
| **5** | **`H-1029E`**<br>ARIA Sentinel-1 InSAR Seasonal Poroelastic Aquitard Phase-Step (`INSAR-BARRIER`, Deferred External) | NASA JPL / ASF DAAC ARIA Sentinel-1 GUNW unwrapped interferograms (`https://asf.alaska.edu/datasets/daac/aria-sentinel-1-geocoded-unwrapped-interferograms/`) + UNR MIDAS GNSS (`http://geodesy.unr.edu/`) | Cross-season interferometric phase-gradient step $\|\nabla \Delta\phi_{\text{seasonal}}\|$ across impermeable fault-core aquitards bounding compartmentalized alluvial aquifers (Chaussard et al. 2014) | Directly images zero-scarp buried valley-floor hydraulic-barrier faults at 90 m resolution without sparse NWIS well interpolation | Agricultural center-pivot pumping drawdown bowls over stratigraphic clay lenses & playa desiccation | **High potential / Blocked in sandbox** (free official US Gov data, CC0; outbound sandbox allowlist blocks `asf.alaska.edu` & `geodesy.unr.edu` — verified & deferred) |

---

## 3. Pre-Registered 3-Experiment Plan in Single Method Lane `ADMITRELAY`

To maximize **P(Win)** within the strict `<= 3` experiment budget (`Rule 6`) while staying inside **one unified physical-structural lane** (`Rule 1`):

1. **Leakage Canary Gate (Rule 4 — Mandatory Prerequisite Before Fitting):**
   - Compute all `12` zero-catalogue physical channels (`H-1029A` + `H-1029B` + `H-1029D`) plus `6` strictly fold-visible (`fold["visible"]`) `H-1029C` Pollard–Segall tip-relay / broadside-shadow features.
   - Measure single-feature symmetric ROC AUC $\max(\text{AUC}, 1 - \text{AUC})$ on `gems57-pooled-hide-v2` (`22,663` withheld positive pixels across `seeds 20, 30`). Hard stop if any feature exceeds `0.90`.
2. **Experiment 1 (`E1` — Zero-Catalogue `ADMITRELAY` Blind Physics LOQO):**
   - 4-region spatially-blocked `HistGradientBoostingClassifier` using ONLY the `12` zero-catalogue `ADMITRELAY` features (`H-1029A` elastic admittance breakdown, `H-1029B` Th-regressed K/U metasomatism redox dipole, `H-1029D` Giggenbach kinetic mixing × MT cap margin) + `10 m` shoreline-deconfounded scarp context (`topo_10m_derived_100m_u8.tif`), emitted at matched `R0_recipe` dot count with `2.8 px` NMS spacing.
3. **Experiment 2 (`E2` — Fold-Proper `ADMITRELAY` Physics + Pollard–Segall Relay / Broadside Shadow + Centerline Trace LOQO):**
   - Nested fold-proper `HistGradientBoostingClassifier` combining the `E1` zero-catalogue stack with strictly `fold["visible"]`-derived Pollard–Segall crack-tip continuation lobes, perpendicular broadside stress-drop shadow, and zero-catalogue `H19-5` centerline indicator (`dh19 == 0`).
   - Evaluated via `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, `22,663` withheld positives, 1,000-draw 20 km paired block bootstrap) against `r0_recipe` (`0.09775`).
4. **Experiment 3 (`E3` — Full-Registry Unique Deployment Candidate: Centerline-Monotone `LBM-v3` × `ADMITRELAY` `E2` Hybrid):**
   - Fuses the fold-validated `E2` `ADMITRELAY` surface with the Goodhart-debiased `131`-claim `LBM-v3` truth-density prior ($\rho(d_{H19}=0) \ge \rho(d_{H19}=1)$, eliminating flank drift!) so that:
     - **Pre-placement surface (`PI-1b`)** already satisfies `<= 0.70` top-N 3-px overlap AND `|Spearman ρ| <= 0.90` across all `2,262` unique SHA-256 rasters of all 8 GitHub owners;
     - **Fold-proper `E3` on `gems57-pooled-hide-v2`** beats `r0_recipe` (`0.09775`) with paired 95% CI strictly above zero (`ci95[0] > 0`);
     - **Final placed binary dots (`PI-1`)** via `gems/lbm_place.py` + `vendor/gems57/submission_writer.py` pass all 11/11 `[0, 1]` format gates AND achieve `<= 0.70` 3-px overlap and `|ρ| <= 0.90` across **all `2,262` unique SHA-256 rasters** across all 8 GitHub owners (while transparently disclosing `1.000 > 0.70` under the literal full-support `17GEMSDOE` dense witness and keeping `verdict = "negative"` / `submission_eligible = false` fail-closed pending human selector decision).
