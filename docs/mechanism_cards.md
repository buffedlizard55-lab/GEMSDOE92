# Mechanism Cards — MASS axis (2026-10-23)

Parent: h33-h33-2-b2 (GEMSDOE32), 37,654 dots, none within 2px of catalogue, CLAIM 0.2778
Ranking: H19-5 continuous field (121k px) value at dot location, proxy for belief strength.

## h33-h33-2-b2-MASS_D10-20261023-e26a6cb8
- **Hypothesis**: Mass optimum test. If marginal credit of lowest-ranked dots < 0.2*DTI (~0.056 at 0.28), dropping them raises DTI. If next-ranked dots have credit > bar, adding them raises DTI.
- **Mechanism**: DTI = T / (0.2T+0.2(S-M)+0.8|G|). For isolated truth, dot pays iff credit >0.2*DTI. Line-like truth lowers bar. Ranking by H19-5 approximates credit expectation.
- **Non-fault mimic**: H19-5 high values can be lithologic contacts, alteration halos, or topographic ridges without faulting; dropping them may remove false positives but also true faults with weak expression.
- **Predicted sign and size**: slight gain if low-ranked dots are noise; risk loss if they carry credit. MASS_D10: predicted +0.002 to +0.008 if low-ranked dots are noise (based on live inversion: removing 3,891 dots at 0.031 credit/dot raised 0.2600->0.2708). MASS_A10: predicted -0.001 to -0.005 if marginal credit < bar. SWAP10: predicted +0.001 to +0.006 if replacement improves avg credit.
- **Falsifier**: If MASS_D10 live score < parent by >0.01, low-ranked dots carry above-bar credit and mass optimum is higher. If MASS_A10 live > parent, budget is not yet saturated.
- **Details**: parent h33-h33-2-b2, n_dots 33889, pct_changed 10.0%, file releases/h33-h33-2-b2-MASS_D10-20261023-e26a6cb8-zeros.tif, sha8 e26a6cb8

## h33-h33-2-b2-MASS_A10-20261023-e5613a00
- **Hypothesis**: Mass optimum test. If marginal credit of lowest-ranked dots < 0.2*DTI (~0.056 at 0.28), dropping them raises DTI. If next-ranked dots have credit > bar, adding them raises DTI.
- **Mechanism**: DTI = T / (0.2T+0.2(S-M)+0.8|G|). For isolated truth, dot pays iff credit >0.2*DTI. Line-like truth lowers bar. Ranking by H19-5 approximates credit expectation.
- **Non-fault mimic**: H19-5 high values can be lithologic contacts, alteration halos, or topographic ridges without faulting; dropping them may remove false positives but also true faults with weak expression.
- **Predicted sign and size**: likely drop if marginal credit <0.056; test of budget optimum. MASS_D10: predicted +0.002 to +0.008 if low-ranked dots are noise (based on live inversion: removing 3,891 dots at 0.031 credit/dot raised 0.2600->0.2708). MASS_A10: predicted -0.001 to -0.005 if marginal credit < bar. SWAP10: predicted +0.001 to +0.006 if replacement improves avg credit.
- **Falsifier**: If MASS_D10 live score < parent by >0.01, low-ranked dots carry above-bar credit and mass optimum is higher. If MASS_A10 live > parent, budget is not yet saturated.
- **Details**: parent h33-h33-2-b2, n_dots 41419, pct_changed 10.0%, file releases/h33-h33-2-b2-MASS_A10-20261023-e5613a00-zeros.tif, sha8 e5613a00

## h33-h33-2-b2-MASS_SWAP10-20261023-3e776063
- **Hypothesis**: Mass optimum test. If marginal credit of lowest-ranked dots < 0.2*DTI (~0.056 at 0.28), dropping them raises DTI. If next-ranked dots have credit > bar, adding them raises DTI.
- **Mechanism**: DTI = T / (0.2T+0.2(S-M)+0.8|G|). For isolated truth, dot pays iff credit >0.2*DTI. Line-like truth lowers bar. Ranking by H19-5 approximates credit expectation.
- **Non-fault mimic**: H19-5 high values can be lithologic contacts, alteration halos, or topographic ridges without faulting; dropping them may remove false positives but also true faults with weak expression.
- **Predicted sign and size**: best chance: keep budget, improve avg credit. MASS_D10: predicted +0.002 to +0.008 if low-ranked dots are noise (based on live inversion: removing 3,891 dots at 0.031 credit/dot raised 0.2600->0.2708). MASS_A10: predicted -0.001 to -0.005 if marginal credit < bar. SWAP10: predicted +0.001 to +0.006 if replacement improves avg credit.
- **Falsifier**: If MASS_D10 live score < parent by >0.01, low-ranked dots carry above-bar credit and mass optimum is higher. If MASS_A10 live > parent, budget is not yet saturated.
- **Details**: parent h33-h33-2-b2, n_dots 37654, pct_changed 10.0%, file releases/h33-h33-2-b2-MASS_SWAP10-20261023-3e776063-zeros.tif, sha8 3e776063


---

# Mechanism Cards — PRUNE axis (2026-10-23)

Parent: h33-h33-2-b2 (GEMSDOE32), 37,654 unit-mass dots, sha256 `baeae321…077dd`
verified byte-for-byte this session. Min catalogue distance 2.236 px; 0 dots
within 2 px, but **2,171 within 3 px (5.77%)**, 3,825 within 4 px (10.16%),
5,637 within 5 px (14.97%).

Design: remove every parent dot within R px of the catalogue and refill to hold
the count at 37,654 by moving each removed dot to its **nearest legal pixel**
(distance > R, in footprint, not on catalogue, on the H19-5 surface). Nearest
refill keeps every other property of the file fixed, so the only variable is the
distance rule. A ranking-based refill would have imported the MASS axis and
reproduced the confound that made the previous session's MASS files ambiguous.

## Shared hypothesis
Dots sitting on or beside a known trace are credited against *catalogue* truth,
which the organizers mask out. They therefore add to `S` (marginal credit to
`T` only through new-fault truth nearby) while the pixels they sit on are not
scored. Removing them should cut dead denominator mass. The forum answer says
new-fault truth **can** lie within 300 m (3 px) of known traces, so this helps
only up to the radius where real new faults start being deleted.

## Shared mechanism
`DTI = T / (0.2T + 0.2(S−M) + 0.8|G|)`. Each dot contributes `+1` to `S` and at
most `M ≤ 1` per unit; a dot whose marginal credit `c` is below `0.2·DTI`
(≈0.056 at 0.28) lowers the ratio. Dots adjacent to known traces are the
likeliest to have `c` below that bar, because their nearest truth is already
credited.

## Shared non-fault mimic
A dot near a known trace can still be genuinely new: unmapped splays,
step-overs, and along-strike extensions of mapped faults are exactly the
Phase-2 target ("newly mapped geometry of existing systems",
https://community.drivendata.org/t/where-do-you-draw-the-line/11536). So the
prune can delete precisely the highest-value pixels. This is not a nuisance
term; it is the competing hypothesis.

## h33-h33-2-b2-PRUNE_B3-20261023-3d2403c7
- **Value**: remove dots within 3 px (2,171 = 5.77%), refill 2,171, count held.
- **Predicted sign and size**: **+0.002 to +0.006 MODEL**. 3 px is 300 m, the
  stated positional uncertainty of the 400 m-spaced GeoDAWN survey, so dots
  inside it are more likely positional scatter than distinct faults.
- **Falsifier**: live score below parent by >0.01. That would say dots within
  300 m of known traces carry above-bar credit and the distance prior is wrong.
- **This is the primary bet of the session.**

## h33-h33-2-b2-PRUNE_B4-20261023-78e893d7
- **Value**: remove within 4 px (3,825 = 10.16%), refill 3,825, count held.
- **Predicted sign and size**: **+0.001 to +0.004 MODEL**, less confident. 4 px
  = 400 m is past the survey's positional uncertainty, so this dose starts
  eating real new-fault pixels; it should pay only if the dead mass is thick.
- **Falsifier**: if B4 < B3 by >0.005 while both sit above the parent, the
  optimum is between 3 and 4 px.

## h33-h33-2-b2-PRUNE_B5-20261023-85cd67ad
- **Value**: remove within 5 px (5,637 = 14.97%), refill 5,637, count held.
- **Predicted sign and size**: **−0.002 to +0.002 MODEL**, i.e. no gain
  expected. This is the dose-response's negative control: if the mechanism is
  real and bounded, B5 should be the worst of the three.
- **Falsifier**: if B5 is the *best* of the three, the distance effect is
  monotone and unbounded in this range, which contradicts the 300 m survey
  geometry and should redirect the next session to PRUNE B8/B10 rather than to
  a new axis.

## Reading the session as a whole
The three doses are a dose-response curve, not three independent bets. Outcomes:

| pattern | reading | next |
|---|---|---|
| B3 > B4 > parent > B5 | peak near 3 px, mechanism real and bounded | build `PRUNE_B3 + CONCENTRATION` |
| monotone B5 > B4 > B3 > parent | prior is real and unbounded here | go deeper (B8, B10) |
| all ≤ parent | distance prior is false | abandon PRUNE, the 0.2708→0.2778 step was false-positive removal |
| B3 > parent, B4 ≈ B3 | flat optimum 3–4 px | prefer B3 (fewer deletions, less risk) |

---

# SNAP axis — thresholded gain series (2026-10-23)

Parent R0 `h33-h33-2-b2`, 37,654 unit-mass dots, CLAIM 0.2778. Response surface from pinned bands 3/13/19 only; see `scripts/make_edge_response.py` and `evidence/snap_session.json`.

## h33-h33-2-b2-SNAPcap2p0-g0p15-20261023-2ca4294e
- **Hypothesis.** Within the 300 m kernel, a dot pays credit only if it lands within ~3 px of a new-fault pixel. If the parent's lineament positions carry the ~100-300 m location error expected from 400 m flight-line spacing, then sliding each poorly-positioned dot onto the local maximum of the TMI/gravity horizontal gradient and detrended-elevation slope recover(s) credit that R0 loses to position error. Dose g=0.15 = only dots whose local edge maximum is at least that much stronger than their own pixel move.
- **Mechanism.** Potential-field horizontal-gradient maxima and slope maxima are where the physical property contrast across a fault plane projects to the surface; the same construction that makes them edge detectors makes their maxima the best local estimate of the trace position. The DTI denominator is dominated by uncovered truth (|G|), so a dot 3-4 px off-trace earns nothing while a dot on the crest earns ~2-3 units of triangular-kernel credit against the same truth.
- **Non-fault process that could mimic it.** Lithologic contacts, intrusive margins, caldera ring fractures, palaeochannels, erosional scarps and road cuts all produce sharp gradient maxima. A magnetic gradient maximum also sits over the *edge of the magnetised body*, not over the fault plane, so the crest can be systematically offset from the trace.
- **Predicted sign and size.** MODEL:±0.008 (MODEL, range [-0.008,+0.008]). Derivation: one converted dot (zero credit -> credit c~2.5, best-weight 0.8, newly covering c of |G|) is worth [(2.5)(1+0.8*0.278) - 0.278(-1.66)]/D ~ 1.5e-4 at D~19,900, a denominator calibrated from the lineage's own measured 2.8e-6 per zero-credit dot. With 2660 movers the sign of the live change is therefore decided by whether the net conversion rate is above or below zero. The quoted range is about +-2 sigma of a pure-relocation null, sigma(dDTI) ~ 1.22*sigma_c*sqrt(n_movers)/D with sigma_c ~ 1.5 kernel units per moved dot (=> ~0.009); the model cannot resolve a sign below 0.01, so these are two-sided ranges, not gains.
- **Falsifier.** If g=0.05 (52% of dots relocate by ~1 px) lands more than 0.01 BELOW g=0.15 and R0, the edge maxima are worse position estimators than the parent's own lineaments and the SNAP hypothesis is rejected for this region. If g=0.15 gains >0.01 while g=0.05 loses >0.01, only the clearly-mispositioned dots are correctable and later axes must keep a strict evidence threshold. A monotone increase with dose supports composing SNAP onto the best PRUNE rung.
- **Decision rule.** Live change under 0.01 is no evidence. Receipts only; never a PROXY.

## h33-h33-2-b2-SNAPcap2p0-g0p10-20261023-f4e8c114
- **Hypothesis.** Within the 300 m kernel, a dot pays credit only if it lands within ~3 px of a new-fault pixel. If the parent's lineament positions carry the ~100-300 m location error expected from 400 m flight-line spacing, then sliding each poorly-positioned dot onto the local maximum of the TMI/gravity horizontal gradient and detrended-elevation slope recover(s) credit that R0 loses to position error. Dose g=0.10 = only dots whose local edge maximum is at least that much stronger than their own pixel move.
- **Mechanism.** Potential-field horizontal-gradient maxima and slope maxima are where the physical property contrast across a fault plane projects to the surface; the same construction that makes them edge detectors makes their maxima the best local estimate of the trace position. The DTI denominator is dominated by uncovered truth (|G|), so a dot 3-4 px off-trace earns nothing while a dot on the crest earns ~2-3 units of triangular-kernel credit against the same truth.
- **Non-fault process that could mimic it.** Lithologic contacts, intrusive margins, caldera ring fractures, palaeochannels, erosional scarps and road cuts all produce sharp gradient maxima. A magnetic gradient maximum also sits over the *edge of the magnetised body*, not over the fault plane, so the crest can be systematically offset from the trace.
- **Predicted sign and size.** MODEL:±0.015 (MODEL, range [-0.015,+0.015]). Derivation: one converted dot (zero credit -> credit c~2.5, best-weight 0.8, newly covering c of |G|) is worth [(2.5)(1+0.8*0.278) - 0.278(-1.66)]/D ~ 1.5e-4 at D~19,900, a denominator calibrated from the lineage's own measured 2.8e-6 per zero-credit dot. With 7023 movers the sign of the live change is therefore decided by whether the net conversion rate is above or below zero. The quoted range is about +-2 sigma of a pure-relocation null, sigma(dDTI) ~ 1.22*sigma_c*sqrt(n_movers)/D with sigma_c ~ 1.5 kernel units per moved dot (=> ~0.015); the model cannot resolve a sign below 0.01, so these are two-sided ranges, not gains.
- **Falsifier.** If g=0.05 (52% of dots relocate by ~1 px) lands more than 0.01 BELOW g=0.15 and R0, the edge maxima are worse position estimators than the parent's own lineaments and the SNAP hypothesis is rejected for this region. If g=0.15 gains >0.01 while g=0.05 loses >0.01, only the clearly-mispositioned dots are correctable and later axes must keep a strict evidence threshold. A monotone increase with dose supports composing SNAP onto the best PRUNE rung.
- **Decision rule.** Live change under 0.01 is no evidence. Receipts only; never a PROXY.

## h33-h33-2-b2-SNAPcap2p0-g0p05-20261023-2c472bc5
- **Hypothesis.** Within the 300 m kernel, a dot pays credit only if it lands within ~3 px of a new-fault pixel. If the parent's lineament positions carry the ~100-300 m location error expected from 400 m flight-line spacing, then sliding each poorly-positioned dot onto the local maximum of the TMI/gravity horizontal gradient and detrended-elevation slope recover(s) credit that R0 loses to position error. Dose g=0.05 = only dots whose local edge maximum is at least that much stronger than their own pixel move.
- **Mechanism.** Potential-field horizontal-gradient maxima and slope maxima are where the physical property contrast across a fault plane projects to the surface; the same construction that makes them edge detectors makes their maxima the best local estimate of the trace position. The DTI denominator is dominated by uncovered truth (|G|), so a dot 3-4 px off-trace earns nothing while a dot on the crest earns ~2-3 units of triangular-kernel credit against the same truth.
- **Non-fault process that could mimic it.** Lithologic contacts, intrusive margins, caldera ring fractures, palaeochannels, erosional scarps and road cuts all produce sharp gradient maxima. A magnetic gradient maximum also sits over the *edge of the magnetised body*, not over the fault plane, so the crest can be systematically offset from the trace.
- **Predicted sign and size.** MODEL:±0.035 (MODEL, range [-0.035,+0.035]). Derivation: one converted dot (zero credit -> credit c~2.5, best-weight 0.8, newly covering c of |G|) is worth [(2.5)(1+0.8*0.278) - 0.278(-1.66)]/D ~ 1.5e-4 at D~19,900, a denominator calibrated from the lineage's own measured 2.8e-6 per zero-credit dot. With 19565 movers the sign of the live change is therefore decided by whether the net conversion rate is above or below zero. The quoted range is about +-2 sigma of a pure-relocation null, sigma(dDTI) ~ 1.22*sigma_c*sqrt(n_movers)/D with sigma_c ~ 1.5 kernel units per moved dot (=> ~0.026); the model cannot resolve a sign below 0.01, so these are two-sided ranges, not gains.
- **Falsifier.** If g=0.05 (52% of dots relocate by ~1 px) lands more than 0.01 BELOW g=0.15 and R0, the edge maxima are worse position estimators than the parent's own lineaments and the SNAP hypothesis is rejected for this region. If g=0.15 gains >0.01 while g=0.05 loses >0.01, only the clearly-mispositioned dots are correctable and later axes must keep a strict evidence threshold. A monotone increase with dose supports composing SNAP onto the best PRUNE rung.
- **Decision rule.** Live change under 0.01 is no evidence. Receipts only; never a PROXY.

---

# Mechanism Cards — SNAP piedmont break-in-slope & subsurface control (2026-10-23)

Parent: `h33-h33-2-b2` (GEMSDOE32), 37,654 unit-mass dots, rebuilt byte-for-byte
(`zeros` SHA-256 `c55bafc4…`, `nan` SHA-256 `baeae321…`), **CLAIM** `0.2778`.
All three SNAP variants hold exact dot count (`37,654`), total mass (`37,654.0`),
parent catalogue exclusions (`d_cat > 2.0 px`, zero mass on catalogue), and
parent `D2.8` Poisson-disk inter-dot spacing (`min_nn = 2.8284 px`), changing
**only** the `<=2 px` local edge/scarp snap operator (`SNAP` is explicitly
exempt from the 1–50% pixel-change bound per Brief v2 §5).

### Why spacing-preserving SNAP (`min_nn >= 2.8 px`) + break-in-slope is essential
In `R0`, `dot_thin(H19-5, 2.8)` seeded from the north-west pixel of each binary
`H19-5` component (`N=20.0%, W=15.3%` vs `S=35.9%, E=29.5%` neighbor occupancy)
without centering on local scarp or potential-field gradient peaks; within
`<=2 px` (`200 m`), median `det_elev_slope` (`Band 19`) is `+102.9%` higher and
median `tmi_hg` (`Band 3`) is `+64.9%` higher than at `R0` dot centers. Enforcing
`D2.8`'s open-disc spacing `dy^2 + dx^2 >= 2.8^2` (`min_nn = 2.8284 px`) prevents
along-strike clumping inside the `R = 3 px` triangular DTI kernel, while pairing
`det_elev_slope` with the piedmont break-in-slope inflection `||grad(det_elev_slope)||`
and unsigned `Band 5 (iso_grav_anom_slope)` anchors dots on piedmont fault traces
rather than mid-facet bedrock cliffs.

## h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24
- **Value**: `scarp2p0px` — `<=2.0 px` (`200 m`) spacing-preserving snap onto
  `0.35*pct(det_elev_slope [B19]) + 0.35*pct(||grad det_elev_slope||) + 0.20*pct(tmi_hg [B3]) + 0.10*pct(iso_grav_anom_slope [B5])`.
  Mean displacement `1.2340 px` (`123.4 m`), median `1.4142 px`, max `2.0000 px`,
  `82.05%` (`30,896`) pixel positions changed, `min_nn = 2.8284 px`.
- **Hypothesis**: GeoDAWN's `400 m` flight-line spacing (`150–200 m` AGL,
  https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7),
  `50°–60°` normal-fault hanging-wall dip projection of basement potential
  fields, and `D2.8`'s unweighted NW-seeded thinning displace `R0` dots by
  `100–200 m` cross-strike from surface fault traces. Snapping `<=200 m` onto
  the joint topographic scarp + piedmont break-in-slope inflection + TMI/gravity
  horizontal gradient crest centers dots onto brittle fault traces without
  climbing eroded footwall cliffs.
- **Mechanism**: Under `DTI = T / (0.2T + 0.2(S - M) + 0.8|G|)` at fixed
  `S = 37,654`, every `100 m` (`1 px`) reduction in cross-strike offset raises
  triangular-kernel credit `k(d) = max(0, 1 - d/3)` by `+1/3` (`+0.333`) per
  fault pixel, yielding `Delta DTI ≈ 0.26 * DTI * (Delta T / T)`. Including the
  piedmont break-in-slope `||grad(det_elev_slope)||` anchors dots at the
  alluvial-fan/bedrock-facet fault junction rather than mid-facet bedrock cliffs,
  while in flat playas where slope variation is negligible, `tmi_hg` and
  unsigned `iso_grav_anom_slope` steer placement over concealed contacts.
- **Non-fault mimic**: Erosional range-front triangular facets, incised
  alluvial-fan terrace risers, Pleistocene pluvial lake shorelines
  (Lahontan/Bonneville), and resistant ash-flow tuff cliff ledges within `200 m`
  of concealed faults.
- **Predicted sign and size**: **`MODEL:+0.012`** vs `R0` (scenario range
  `[-0.006, +0.025]`; `MODEL` projection, never a score). Report-only `PROXY`
  diagnostics: SGMC off-catalogue bedrock control `+0.002667` (`0.098727` vs
  `0.096060`); buffered catalogue hide-and-recover `+0.000798` (`0.004804` vs
  `0.004006`).
- **Falsifier**: Live receipt delta `<= -0.01` vs `R0` falsifies `<=200 m`
  surface-scarp localization and shows new-fault truth is dominated by concealed
  intrabasinal traces or offset from geomorphic slope breaks; `|delta| < 0.01`
  is treated as no evidence.

## h33-h33-2-b2-SNAPscarp1p4px-20261023-01fb4acc
- **Value**: `scarp1p4px` — `<=sqrt(2) px` (`1.4142 px = 141 m`, 8-connected
  Moore window) spacing-preserving snap onto the **identical** joint response
  surface `R_es`. Mean displacement `0.9540 px` (`95.4 m`), median `1.0000 px`,
  max `1.4142 px`, `78.00%` (`29,370`) pixel positions changed,
  `min_nn = 2.8284 px`.
- **Hypothesis**: Limiting capture radius to `141 m` (one diagonal pixel)
  corrects `D2.8`'s 1-px NW ribbon-edge bias and sub-grid rasterization offset
  while preventing `200 m` upslope excursion onto eroded footwall facets along
  mature Basin-and-Range fronts where the active piedmont fault trace has
  stepped basinward of the retreated bedrock escarpment.
- **Mechanism**: Holds response surface, count (`37,654`), exclusions
  (`d_cat > 2.0`), and spacing (`min_nn >= 2.828 px`) identical to `scarp2p0px`,
  varying **only** `max_shift` (`1.414 px` vs `2.000 px`) to isolate capture
  radius.
- **Non-fault mimic**: Local `100–141 m` stream-cut fan scarps, talus-apron
  margins, and shallow volcanic flow edges bordering geophysical lineaments.
- **Predicted sign and size**: **`MODEL:+0.008`** vs `R0` (scenario range
  `[-0.004, +0.018]`; `MODEL` only). Report-only `PROXY` diagnostics: SGMC
  control `+0.001480` (`0.097540`); hide-and-recover `+0.000550` (`0.004556`).
- **Falsifier**: If `scarp1p4px` beats `scarp2p0px` by `>= +0.01` on live
  receipts, `200 m` capture overshoots onto retreated footwall facets; if both
  trail `R0` by `>= 0.01`, topographic scarp snapping is falsified.

## h33-h33-2-b2-SNAPpot2p0px-20261023-41697f8c
- **Value**: `pot2p0px` — `<=2.0 px` (`200 m`) spacing-preserving snap onto
  subsurface potential-field horizontal gradients **only**:
  `0.65*pct(tmi_hg [B3]) + 0.35*pct(iso_grav_anom_slope [B5])`. Mean
  displacement `1.3656 px` (`136.6 m`), median `1.4142 px`, max `2.0000 px`,
  `79.07%` (`29,773`) pixel positions changed, `min_nn = 2.8284 px`.
- **Hypothesis**: Mechanistic subsurface control. If hidden new-fault truth is
  predominantly concealed intrabasinal faults beneath Quaternary basin fill with
  zero surface scarp, snapping solely to unsigned magnetic and isostatic-gravity
  horizontal gradients centers dots onto basement/volcanic offsets without
  alluvial or shoreline erosion noise. Conversely, if new-fault truth tracks
  surface/piedmont traces of `50°–60°` dipping normal faults, `~63°` geomagnetic
  inclination (unreduced `TMI`) and down-dip hanging-wall density projection pull
  potential-field gradient crests `150–300 m` basinward off the surface fault.
- **Mechanism**: Holds capture radius (`2.0 px`), count (`37,654`), exclusions
  (`d_cat > 2.0`), and spacing (`min_nn >= 2.828 px`) identical to `scarp2p0px`,
  removing only the topographic scarp/break terms. Uses unsigned `Band 5`
  (`iso_grav_anom_slope = ||grad g||`) rather than signed E-W `Band 18`
  (`dg/dx`) so east- and west-dipping normal faults are treated symmetrically.
- **Non-fault mimic**: Unfaulted plutonic intrusive contacts, caldera ring
  fractures, ash-flow tuff stratigraphic pinchouts, and down-dip hanging-wall
  gradient shifts of dipping normal faults.
- **Predicted sign and size**: **`MODEL:-0.002`** vs `R0` (scenario range
  `[-0.014, +0.010]`; `MODEL` only). Report-only `PROXY` diagnostics: SGMC
  control `-0.003303` (`0.092757`, consistent with dip/inclination offset from
  mapped bedrock traces); hide-and-recover `+0.000569` (`0.004575`).
- **Falsifier**: A live receipt gain `>= +0.01` over both `R0` and `scarp2p0px`
  falsifies surface-scarp dominance and proves hidden test faults are primarily
  concealed basement structures best centered by potential-field gradients alone.

---

# Mechanism Cards — CONCENTRATION axis (2026-10-24)

Parent: `h33-h33-2-b2` (GEMSDOE32), 37,654 unit-mass dots, **CLAIM** 0.2778 (no
receipt). Axis: move 10% of the dots (3,765) between **1 km blocks** (10 px at
the 100 m grid) selected by a km-scale prior, holding count and mass exactly.
New dots are restricted to the H19-5 ridge mask, data-valid pixels, and `d_cat >
3.0 px`; inherited dots keep R0's own `d_cat > 2.0 px` rule. All three variants
pass all format gates and were re-read from disk (`evidence/concentration_variants.json`).

Shared arithmetic, stated once:

* `DTI = T / (0.2T + 0.2(S-M) + 0.8|G|)` with `S = 37,654` fixed, so the only
  free variables are `T` (kernel credit on truth) and `M` (mass overlapping truth).
* A dot already tiles the H19-5 skeleton at ~3.0 px (median nn 3.0, min 2.828).
  A 1-px reallocation therefore **removes** a dot that was carrying ~1.0 credit at
  its own pixel and **adds** a neighbour worth ~0.3-0.6 credit, while the `+1` of
  denominator mass stays. The measured mechanical cost, with a flat prior and no
  spatial information at all (`model_flat_prior`), is **-0.013 / -0.016 / -0.021**
  for the three variants. **A CONCENTRATION move can only win if the prior's
  spatial information is worth more than that cost.** This is the single most
  important number in this session and it is recorded per variant in the evidence
  file.

## `h33-h33-2-b2-CONCENTRATIONcatd10-20261024-c313194a` (`catd10`)
- **Prior**: 1 km Gaussian of the pinned known-fault catalogue, renormalised to
  mean 1.0 on the footprint. Block prior of the dots that leave: 0.00; of the
  blocks that receive them: mean 1.41. Median catalogue distance of a moved dot
  goes from 70.6 px (7.1 km) to 5.0 px (0.5 km) — the 10% is collected into the
  collar around mapped structure.
- **Hypothesis**: newly mapped faults are mostly new geometry of existing
  systems, so new-fault pixels per km² track the density of already-mapped
  structure. R0 spreads dots uniformly over its ridge mask (dot density per block
  is uncorrelated with the catalogue prior: r = -0.33), so reallocating 10% toward
  dense blocks should raise `T` where truth is most numerous.
- **Mechanism**: at fixed `S`, moving a dot from a block with near-zero known
  structure to one with several times the regional density raises its expected
  `max k` and raises `M`, shrinking the wasted-mass term `S-M`. Placement is by
  exact expected-DTI marginal gain under the same prior.
- **Non-fault process that could mimic it**: **mapping effort**. The catalogue is
  denser where exposure, access and basin-range normal faults made compilation
  easy, not necessarily where 2020s geothermal-focused mapping found new faults.
  If new truth instead sits in poorly mapped uplands, the prior is
  anti-correlated and this file loses.
- **Predicted sign and size**: **`MODEL:+0.013`**, range `[-0.013,+0.040]` (rule:
  midpoint of the own-prior projection `+0.040` and the other-prior projection
  `-0.013`; the flat-prior mechanics-only cost is `-0.013`). Report-only
  `PROXY`: SGMC off-catalogue control `-0.0037`; catalogue hide-and-recover
  `+0.000005` (flat, and uninformative — see `evidence/concentration_proxy_audit.json`).
- **Falsifier**: a live receipt delta `<= -0.01` vs R0 says the catalogue is a
  mapping-effort artefact at 1 km. `|delta| < 0.01` is no evidence (public chunks
  only), and then `catdS10` decides the sign.

## `h33-h33-2-b2-CONCENTRATIONphys10-20261024-b93a4cf8` (`phys10`)
- **Prior**: 1 km Gaussian of `0.40·pct(band 3 tmi_hg) + 0.35·pct(band 5
  iso_grav_anom_slope) + 0.25·pct(band 19 det_elev_slope)` (the repository's
  pre-existing weight mix, not tuned on any score). Block prior range across the
  dots is 0.69 → 1.42, i.e. a much flatter prior than `catd`: the median moved
  dot barely shifts (22.2 → 20.0 px from the catalogue). This variant is
  effectively "does any 1-km physics prior beat the mechanical cost of the swap?"
- **Hypothesis**: more intensely broken crust per km² hosts more fault pixels;
  magnetic/gravity gradient and detrended-slope energy are a label-free proxy for
  that, with no mapping-effort bias.
- **Mechanism**: same fixed-`S` budget trade as `catd10`; only the donor and
  receiver block sets differ (destination pixels overlap `catd10`'s by Jaccard
  0.087, so the two priors are near-orthogonal).
- **Non-fault mimic**: volcanic flow margins, caldera ring fractures, pluton
  contacts, lithologic scarps — and note the H19-5 mask was itself built from
  these bands, so the implied redistribution is the mildest of the three.
- **Predicted sign and size**: **`MODEL:-0.008`**, range `[-0.014,-0.002]`
  (own-prior `-0.002`, other-prior `-0.014`, mechanics-only `-0.016`). The prior's
  contrast at 1 km (~2x) is too small to pay the swap cost in the model.
  `PROXY`: SGMC `-0.0084`; hide-and-recover `0.003592` vs R0 `0.004006`.
- **Falsifier**: a live gain `>= +0.01` would mean km-scale physics
  favourability is worth more than the model says and would justify a *combined*
  axis (see `SLOT_PLAN.md`); a loss `<= -0.01` alongside `catd10 >= +0.01` says
  the catalogue prior (not "concentration" in general) is what works.

## `h33-h33-2-b2-CONCENTRATIONcatdS10-20261024-6b87f2d7` (`catdS10`)
- **Prior**: identical to `catd10`, run in the **opposite direction** — 10% of the
  dots leave the highest-prior blocks and land in the lowest. Built because the
  2026-10-23 session's `IRREGULARITIES.md` entry requires both directions before a
  CONCENTRATION result can be read as a sign. Median catalogue distance of a moved
  dot goes from 4.1 px to 55.0 px.
- **Hypothesis**: mirror image of `catd10`. If the known-structure-density prior
  is informative, this variant must LOSE, and the pair (`catd10` up, `catdS10`
  down) is a two-sided test of that one statement instead of a one-sided bet.
- **Mechanism**: same bookkeeping with donor and receiver block sets swapped;
  count, mass, mask, catalogue clearance and placement rule identical.
- **Non-fault mimic**: if new-fault truth really is concentrated **away** from
  mapped structure (poorly exposed basins, young volcanic terrain, unmapped
  uplands), this file wins and `catd10` loses on the same evidence.
- **Predicted sign and size**: **`MODEL:-0.070`**, range `[-0.118,-0.022]`
  (own-prior `-0.118`, other-prior `-0.022`, mechanics-only `-0.021`). The model's
  catd-anchored truth total is `|G| ≈ 198,000 px`, which is what makes the
  asymmetry between the two directions large; treat the magnitude as a MODEL
  artefact and the **sign** as the claim. `PROXY`: SGMC `-0.0069`;
  hide-and-recover `0.002106` vs R0 `0.004006` (the mirror does depopulate the
  catalogue collar, as designed, and the instrument confirms it).
- **Falsifier**: `catdS10 >= catd10 + 0.01` falsifies the
  known-structure-density prior outright. All three arms within 0.01 of R0 means
  the axis is inert at 10% and should not be spent on again at this dose.
