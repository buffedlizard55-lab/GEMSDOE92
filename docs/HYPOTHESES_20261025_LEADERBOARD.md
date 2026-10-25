# Pre-registered geological hypotheses — leaderboard research session, 2026-10-25

**Status: proposals only. No hypothesis was built, placed or scored in this session.**
Experiments used: **0 of 3**. Weekly slots used: **0**. Organizer-confirmed scores: **none**.

Every "expected improvement" below is a **projection, not a score**. Only the
shared holdout (`HOLDOUT-DTI`, `gems57-pooled-hide-v2`) or an organizer receipt
can produce a number that may be called a score.

## Why none of these can be promoted yet

The binding literal pre-placement stop still applies. The pinned 17GEMSDOE E-proba
witness is positive at all `5,167,373` footprint cells, so any nonempty in-footprint
dot set has forward 3-px overlap `1.0 > 0.70`
(`evidence/readiness_20261025_leaderboard.json`, re-run fresh 2026-10-25, sha-pinned blob).
Placement is therefore not permitted under the current protocol. Each hypothesis
below is ranked and pre-registered so the next session can run it immediately
once the policy question in `docs/ANALYSIS_20261025_LEADERBOARD.md` is decided.

## Verified data availability (checked this session)

| Layer / source | Status | Evidence |
|---|---|---|
| 19-band `training_features.tif` (EPSG:32611, 100 m, 3730×3292) | **Restored**, pinned SHA-256 `4371c82e…` | `.cache/gems_inputs/` (gitignored); `scripts/restore_inputs.py` |
| Band 2 `rtp` (reduced-to-pole magnetics) | Available | band list read from the restored file |
| Band 6 `tc` (tilt / total curvature) | Available | band list |
| 1 m DEM (USGS 3DEP) | **Not obtainable** from the sandbox. Only `github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org` are reachable. The DEM links are in the login-gated DrivenData download. | sandbox allowlist; `registry/session_manifest.json` |
| USGS ComCat earthquake catalogue (for b-value) | **Not obtainable** from the sandbox (`earthquake.usgs.gov` is not on the allowlist). | sandbox allowlist |

## Ranked hypotheses

Ranking key: expected DTI improvement (projection) first, then implementation cost.

### H1 — PHASE-CONGRUENCY-RTP (rank 1; recommended first build)

- **Layer(s):** Band 2 `rtp`. Optional cross-check against Band 6 `tc`.
- **Physical signature:** Multi-scale, multi-orientation phase congruency
  (log-Gabor quadrature pairs; Kovesi's measure). It responds to coherent step
  and line structure whatever its amplitude. Source: Kovesi (1999), *Image Features
  from Phase Congruency*, Videre 1(3): https://www.peterkovesi.com/papers/Kovesi_Videre_v1n3001.pdf
- **Why it could catch a catalogue-missing fault:** Amplitude-based detectors
  (`tmi_hg` gradient magnitude, ANASIG analytic signal, `tc` tilt) are dominated by
  strong contacts. A buried fault with low susceptibility contrast still gives a
  phase-coherent offset of the magnetic fabric. That is the case the catalogue
  misses, and the one that amplitude ridges miss too.
- **Difference from implemented code:** `grep -ril "phase.congr" gems scripts vendor` → **0 files**.
  ANASIG uses `hypot(tmi_hg, tmi_vg)` (gradient amplitude). tc/tilt is a normalised
  derivative, not a phase measure.
- **Named non-fault mimic:** lithologic contacts with no offset; dike and sill margins;
  cultural magnetic noise. Falsifier: a contact-only field would show the same phase
  pattern with no displacement, so the test is holdout recovery of withheld segments.
- **Expected HOLDOUT-DTI improvement:** *not quantified* (no holdout run; a projection
  would be an invented number). Implementation cost: **low–moderate** (FFT log-Gabor bank, about 150 lines).
- **Pre-registered gates:** single-feature canary symmetric AUC ≤ 0.90; surface
  Spearman vs every local registry raster ≤ 0.90; final-dot overlap ≤ 0.70 (currently
  blocked by the universal stop); HOLDOUT-DTI paired CI vs `VENTSCARP` Rule-2 best
  (`0.112213`) and static best `KNICKLOQO` (`0.010788`).

### H2 — RADON-LINE-INTEGRATION (rank 2)

- **Layer(s):** Band 6 `tc` edge map and/or Band 2 `rtp`.
- **Physical signature:** Line integrals of edge strength over straight paths
  (Radon transform, binned by angle), which accumulate long, nearly straight
  lineaments (fault traces ≥ 5 km) and suppress short noise.
- **Why:** Faults are long, quasi-linear features. Local operators (gradient, Euler,
  lineament orientation) cannot see a feature whose contrast is only visible when
  integrated along its length.
- **Difference:** `grep -ril "radon" gems scripts vendor` → **0 files**. Existing lineament
  work (`breakline`, `stepedge`, `strainbreak`, `coulomb`, `geotension`, `scarppol`) uses
  *local* orientation, not integration along straight paths.
- **Named non-fault mimic:** linear anthropogenic features (roads, pipelines, survey lines)
  and stratigraphic or dike-swarm trends.
- **Expected HOLDOUT-DTI improvement:** *not quantified*. **Cost: moderate** (angle-binned
  line sums over a 12-million-cell grid).

### H3 — RTP TEXTURE-DISPLACEMENT REGISTRATION (rank 3; carried from the 2026-10-25 shortlist)

- **Layer(s):** Band 2 `rtp`, optionally Band 11 `iso_grav_anom_vg` as an independent check.
- **Physical signature:** A stable along-strike offset of magnetic texture across
  trial traces, meaning a lateral displacement, not merely an edge.
- **Why:** A buried strike-slip or oblique structure can offset older magnetic fabric
  after the scarp has degraded, and this is a displacement signal rather than an edge signal.
- **Difference:** No exact registration operator was found in `gems/*.py` (see
  `docs/HYPOTHESES_20261025_REVIEW.md`).
- **Named non-fault mimic:** texture changes from unit boundaries with no displacement.
- **Expected HOLDOUT-DTI improvement:** *not quantified*. **Cost: high** (new registration engine, its own validation).

### H4 — EARTHQUAKE b-VALUE ANOMALY (rank 4; **blocked**)

- **Layer(s):** Raw earthquake catalogue (not the pinned bands 10 and 16, which are
  already density summaries).
- **Physical signature:** Gutenberg–Richter b-value lows along active fault zones.
- **Why:** Would separate active structures from background seismicity.
- **Blocker:** The raw catalogue is USGS ComCat, which is not reachable from the
  sandbox. It would need an official staged copy. **Not viable this session.**

### H5 — MULTIFRACTAL / HURST ROUGHNESS OF THE 1 m DEM (rank 5; **blocked**)

- **Layer(s):** 1 m USGS DEM (external, login-gated links in the competition data).
- **Physical signature:** Fault-surface roughness with a power-law (Hurst) scaling. Sources:
  Renard et al. (2013), GRL: https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2012GL054143 ;
  Candela et al. (2012), JGR: https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2011jb009041
- **Why it is ranked last:** The cited roughness is measured at mm to tens-of-metres scales. A
  100 m grid cannot resolve it, so the signal would have to come from the 1 m DEM.
- **Blocker:** The 1 m DEM is not reachable from the sandbox. A separate verification
  is needed before this can be proposed as viable.
- **Difference:** `grep -ril "roughness\|box.count" gems scripts` finds no multifractal
  or Hurst operator in `gems/`.

## Recommended next action (for the next session, after the policy decision)

1. Build **H1** as a single lane. Run the canary and the surface gate before placement.
2. If the surface gate passes, run the holdout against `VENTSCARP` Rule-2 (`0.112213`)
   and `KNICKLOQO` static (`0.010788`) on identical folds.
3. Stop at the final-dot gate if the universal witness rule still applies.
