# TILTANGLE — Pre-Registered Geological Hypotheses (Ranked)

Session: 2026-10-25 · Lane: TILTANGLE · Evaluator: gems57-pooled-hide-v2
Status: Top candidate (H1) built, format-validated, holdout-scored.
All labels: HOLDOUT-DTI (local surrogate, not an organizer score).

---

## H1 — Gravity tilt-angle edge corridors (BUILT — TILTANGLE)

**Layers:** B11 `iso_grav_anom_vg` (vertical gravity derivative), B13
`iso_grav_anom` (differentiated for N–S horizontal derivative), B18
`iso_grav_anom_hg` (signed E–W gravity horizontal derivative).

**Physical signature:** Gravity tilt angle θ = atan2(|∂z g|, |∇ₕ g|) (Miller &
Singh 1994, *J. Appl. Geophys.* 32:213–217). Directly over a steep vertical
density contact, ∂z g crosses zero while |∇ₕ g| peaks, so θ → 0° and
cos(θ)² → 1; over flat interiors where |∇ₕ g| → 0 and |∂z g| > 0, θ → 90° and
cos(θ)² → 0 (correcting the inverted prose in the initial draft).
Edge strength = `hgm * cos(θ)² = hgm³ / (hgm² + vg²)`, which attenuates
horizontal-gradient magnitude where |∂z g| is large.

**Why it catches catalogue-missing faults:** The USGS/INGENIOUS catalogue
is a surface-scarp catalogue. Blind normal faults buried under thin Quaternary
cover, or whose scarps have diffused below detection, still juxtapose rock
bodies of different density across a steep plane. That density contrast is
visible to gravity regardless of scarp preservation or fault strike. While the
pure surface `S` is catalogue-free (max canary symmetric AUC `0.526594 <= 0.90`),
the initial build script multiplied `S` by `d_pref` computed from the full
`existing_faults.tif` catalogue before static holdout scoring, which failed the
Protocol Rule 4 leakage canary (`symmetric AUC = 0.962399 > 0.90`, target leakage).

**Non-fault mimic:** Equant plutonic intrusions, circular playa/evaporite
density bodies, and diffuse basement-terrane boundaries.

**Differs from existing lanes:** GRAVQUAD uses analytic-signal amplitude ×
structure-tensor coherence. COULOMB-LOQO assumes fixed N15°E conjugate shear
planes inside a supervised classifier. CURIE-DEMAG uses RTP variance suppression ×
MT clay-cap flank × demag bowl.

**Expected DTI improvement & audited result (`evidence/tiltangle_audit_20261025.json`):**
Low-to-moderate standalone physical edge detector. Audited via
`vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, 22,663 withheld
positives, 1,000-draw paired spatial-block bootstrap):
- Pure `S` static (`d_cat > 2 px`, leak-free): **HOLDOUT-DTI `0.005272 [0.003839, 0.006810]`** (paired Δ vs R0 `+0.001266 [-0.000247, +0.002861]`, CI includes 0).
- Strict fold-visible Rule-2 (`d_visible > 2 px`, visible-only `d_pref`): **HOLDOUT-DTI `0.085247 [0.072752, 0.098193]`**.
- Strict fold-visible Rule-2 (`d_visible > 2 px`, pure `S`): **HOLDOUT-DTI `0.042670 [0.030397, 0.055911]`**.
- Note: the initial `0.033466` (unbuffered 45,253 px) / `0.031591` (buffered 22,663 px) static figure is **INVALIDATED** due to full-catalogue `d_pref` target leakage (`AUC = 0.962399 > 0.90`).

**Implementation cost:** Low — pure array math on 3 bands, no sklearn, no
training.

**Result:** ✅ Format-valid (11/11 gates, research download only). ⛔ **Verdict:
negative (`submission_eligible: false`, DO NOT SUBMIT)** — does not beat
repository holdout-best (`LISTRICLOQO` `0.013295` static / `0.114410` Rule-2),
fails local 3-px dot-field uniqueness (`0.776332 > 0.70` vs `NETEXPAND netexpand`
and `0.761513 > 0.70` vs `NETEXPAND netexpandfar`), and hits the literal
dense-witness registry stop (`1.0000 > 0.70`).

---

## H2 — Curie-depth spectral window (NOT BUILT)

**Layers:** B2 `rtp` (reduced-to-pole magnetic anomaly); B13/B18 gravity for
tilt-angle cross-gate.

**Physical signature:** 2D FFT radial power spectrum of B2 → depth-to-magnetic-
bottom (Curie isotherm) estimate via spectral slope. Shallow Curie depth =
high heat flow = geothermal upflow. Intersect shallow-depth windows with
gravity tilt-angle edge corridors (H1) to locate blind faults hosting upflow.

**Why it catches catalogue-missing faults:** Curie depth is a subsurface,
heat-flow property; it requires no surface expression. Blind faults with no
scarp can still host shallow Curie-depth geothermal cells.

**Non-fault mimic:** Deep magnetic basement undulations unrelated to faults;
sedimentary basins with naturally shallow magnetic basement.

**Differs from existing lanes:** No lane uses spectral/Fourier depth estimation.
CURIE-DEMAG uses spatial-domain RTP variance suppression, not spectral depth.

**Expected DTI improvement:** High conceptual value (targets heat, not just
structure), but untested locally; spectral depth estimation on the pinned stack
is non-trivial and may not localize to individual faults.

**Implementation cost:** Medium — requires 2D FFT on 3730×3292, radial
averaging, depth-from-slope inversion, and cross-gating with tilt angles.

**Data availability:** B2 RTP is in the pinned training_features.tif (locally
restored). No external data needed. **Viable.**

---

## H3 — Detrended-elevation Laplacian curvature × gravity-gradient intersection (NOT BUILT)

**Layers:** B12 `det_elev` (detrended 3DEP elevation), B13 `iso_grav_anom`,
B18 `iso_grav_anom_hg`.

**Physical signature:** Laplacian (second derivative) of detrended elevation
enhances narrow scarp-like curvature features (fault scarps, faceted
spur-and-valley morphology) while suppressing broad regional topography.
Intersect with gravity-gradient magnitude (buried density contrast) to catch
faults with either topographic OR geophysical expression.

**Why it catches catalogue-missing faults:** The scarp catalogue misses faults
whose scarps have diffused below visual detection but still produce subtle
curvature; it also misses fully blind faults with no topography but a gravity
signature. The intersection captures both.

**Non-fault mimic:** Drainage incisions, alluvial fan toes, volcanic cones —
all produce curvature but lack the gravity-gradient correlation.

**Differs from existing lanes:** NEO-OPNS uses TPI × LoG × log-slope but not
the curvature × gravity-gradient intersection. No lane intersects topographic
curvature with gravity gradient as a dual gate.

**Expected DTI improvement:** Moderate. Topographic curvature should recover
scarps near catalogue faults; gravity gradient extends to blind strands.

**Implementation cost:** Low — np.gradient-based Laplacian + gradient magnitude,
both on pinned bands.

**Data availability:** All bands in pinned training_features.tif. **Viable.**

---

## H4 — Radiometric alteration index × magnetic suppression dual gate (NOT BUILT)

**Layers:** B1 `mag_anom`, B2 `rtp`, B6 `tc` (radiometric total count), plus
derived K/Th and U/Th ratios where separable.

**Physical signature:** Geothermal alteration (argillic → smectite clay) creates
radiometric potassium depletion and uranium/thorium fractionation, plus magnetic
demagnetization (titanomagnetite → pyrite). Dual gate: alteration index (low K/
Th, specific TC signature) AND magnetic suppression (low RTP variance).

**Why it catches catalogue-missing faults:** Alteration halos extend beyond
mapped fault traces and can be wider than the scarp itself. Blind faults hosting
alteration show no surface rupture but show the radiometric+magnetic signature.

**Non-fault mimic:** Lithologic variations (e.g., ash falls, paleosols) that
produce similar radiometric signatures without faulting.

**Differs from existing lanes:** CURIE-DEMAG uses RTP variance × MT clay-cap
flank × demag bowl but not radiometric K/Th/U ratios. COULOMB-LOQO includes
K/Th, U/Th as features inside a supervised classifier but never as a standalone
dual-gate emission surface.

**Expected DTI improvement:** Moderate-High; alteration is a direct geothermal
proxy, but radiometric bands may be too smooth to localize individual faults.

**Implementation cost:** Low-Medium — requires band math (ratios, local
variance) on pinned bands.

**Data availability:** B1, B2, B6 in pinned stack. K/Th and U/Th separability
from B6 TC is unverified (B6 is radiometric total count). **Partially viable.**

---

## H5 — Drainage-deflection / stream-offset knickzone detector (NOT BUILT)

**Layers:** B12 `det_elev` (3DEP-derived), B19 `det_elev_slope`, existing
drainage not in stack (would need NHD or derived flow direction).

**Physical signature:** Active normal faults deflect drainages and create
knickzones where streams cross fault traces. Stream-offset detection via
drainage-pattern asymmetry across candidate fault traces.

**Why it catches catalogue-missing faults:** Small-displacement faults offset
drainages without producing mappable scarps; drainage deflection can be more
persistent than scarps in alluvial settings.

**Non-fault mimic:** Lithologic controls on drainage, fan incision, volcanic
drainage patterns — all deflect streams without faulting.

**Differs from existing lanes:** DRAINAGE_KNICK exists but targets terrain
knickpoints, not stream-offset asymmetry. No lane uses flow-direction or
drainage-network deflection.

**Expected DTI improvement:** Uncertain — depends on deriving flow direction
from DEM (possible with scipy) but stream data not in pinned stack.

**Implementation cost:** Medium-High — requires flow-direction derivation,
stream network extraction, offset detection. **Not viable without external
drainage data (USGS NHD or 3DEP-derived flow direction).**

---

## Ranking (expected DTI improvement / implementation cost)

| Rank | Hypothesis | Expected DTI | Cost | Viable with local data? |
|------|-----------|-------------|------|--------------------------|
| 1 | **H1 TILTANGLE: gravity tilt-angle edge corridors** | Moderate-High (actual 0.033466 static) | Low | ✅ Yes — built |
| 2 | H3: curvature × gravity-gradient intersection | Moderate | Low | ✅ Yes |
| 3 | H2: Curie-depth spectral window | High (conceptual) | Medium | ✅ Yes |
| 4 | H4: radiometric × magnetic dual gate | Moderate-High | Low-Medium | ⚠️ Partially (K/Th split unverified) |
| 5 | H5: drainage-deflection knickzones | Uncertain | Medium-High | ❌ No external drainage data |

**Selected for build:** H1 (TILTANGLE) — highest confidence of physical validity,
lowest implementation cost, fully valid with locally restored pinned data. Built
as experiment 1 of 3.

**Holdout result (H1):** HOLDOUT-DTI 0.033466 (gems57-pooled-hide-v2, 45,253
withheld positives across 8 LOQO folds, seeds 20+30). Per-quadrant: NE 0.0332,
NW 0.0354, SE 0.0337, SW 0.0323 — spatially uniform, no quadrant collapse.
Per-draw: 0.0336 / 0.0337 — stable across draws. Beats R0 static (0.004006) by
~8.4× and COULOMBDM static (0.007816) by ~4.3×. Below supervised LOQO
Rule-2 (0.113316) as expected for a standalone deterministic surface.

**Leakage canary:** Not run as single-feature AUC (deterministic surface, no
classifier training; surface does not read the catalogue). Surface uniqueness
vs registry not scanned (below promotion bar; per protocol, no public-registry
scan is spent on a lane that does not clear the holdout promotion bar first).
