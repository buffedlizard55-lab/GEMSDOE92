# H-92M pre-registration — Morpho-Disequilibrium & Concealed-strand prior (MDC), 2026-10-31

Lane: this session's single assigned method. Written **before** any holdout number was
computed, as required by the parallel-run protocol (rule 2/5). Executed with
`scripts/run_mdc_20261031.py` (exactly three experiments, 0 weekly slots spent).

## 1. Hypothesis

Concealed, catalogue-missing range-front strands in the northwestern Great Basin can be
located by **non-local** (kilometre-integrated) morphotectonic disequilibrium functionals
of the published 100 m feature stack, fused with a **buried-basement step projected
across the range-front normal**, and gated by an inverse "topo-blind" contrast
(geophysics strong, DEM quiet). Converting that recall into leaderboard value requires
*adding* it to a validated parent dot set, not replacing any of its dots, because the
metric's TP term is a maximum over dots while its FP term sums linearly.

## 2. Layers and physical signature targeted

| # | Layer / band | Transform | Why it is non-local |
|---|---|---|---|
| 1 | `Band 12 det_elev` | 3.1 km local relative height `(z−zmin_W)/(zmax_W−zmin_W)` (hypsometric analogue, Bull 1978) | an uplifted block stays high against its own valley floor for 10⁴–10⁵ yr after the offset |
| 2 | `Band 12` sign field | bedrock/alluvium contact perimeter-over-√area at 2.1 km (mountain-front sinuosity `Smf`, Bull & McFadden 1977) | front linearity integrates the whole front segment, not one pixel |
| 3 | `Band 12` gradient direction | unit-aspect vector coherence at 1.1 km × slope (facetness / catchment asymmetry analogue, Chen et al. 2003) | a fault-facing planar facet organises kilometres of drainage |
| 4 | `Band 15 depth_to_base_surf` | gradient projected on the front normal (`throw`, not just edge magnitude) | survives sediment cover; a contact parallel to the front gives ~0 projection |
| 5 | `Band 18 × Band 3 × Band 2` | geometric-mean concordance of gravity-HG, TMI-HG and \|RTP\| | a basement-involved fault juxtaposes dense *and* magnetic footwall against light, non-magnetic fill |
| 6 | `Band 8 geod_dilaterate` | relu of the extensional sign only | dilation at bends/steps localises fluid pathway and hence alteration |
| 7 | derived | `topo-blind ratio = rank(step) − rank(scarp energy)` | the amplifier: high only where the DEM cannot see the structure |

Composite: `S = 0.30·f4 + 0.22·f5 + 0.14·f1' + 0.12·f1 + 0.10·f3 + 0.06·f2 + 0.06·f6`,
plus an additive `+0.30·relu(rank(f7)−0.55)/0.45` concealed-strand bonus, clipped to
[0,1]. Emission: top decile of `S` inside the footprint → 1 px crest diagnostics →
greedy spaced-top with a 2.8 px floor (kernel-matched, 280 m < 300 m), a `d_cat > 2 px`
catalogue collar and, for added dots, `d_parent > 3 px`.

## 3. Why this should catch a fault *missing* from the USGS/INGENIOUS catalogue

Every lane in this repository queries the DEM at or within a few pixels of the candidate
cell. A strand under 10–500 m of Plio-Quaternary fan/playa fill has **no** 100 m-pixel
expression, so local detectors cannot propose it, which is the recall deficit recorded for
the parent family in `docs/WHY_0_2778.md` (concealed graben, cover-blinded fronts,
stepover/linkage zones). Catchment-integrated indices are exactly the observable that a
buried strand *does* produce: deflected fans, asymmetric faceted spurs, a basement step
in the gravity field. A resistant stratigraphic contact, by contrast, generates a sharp
DEM/geophysics edge **without** the drainage asymmetry and **with** both topo and
geophysics expressing it, so the topo-blind inverse contrast actively demotes the classic
mimic rather than merely ranking it lower.

## 4. Difference from anything already implemented here

`grep -riE "catchment|accumulation|sinuosity|hypsometr|steepness|front normal" gems/*.py`
returns nothing. No module forms an integrated (window/catchment-scale) morphotectonic
functional, and none projects the basement gradient onto the range-front normal. The
polarity-lock lanes (BLINDFAULT, COULOMB_LOQO, FLEXURE_KNICK_PROVINCE, LISTRICDIP,
POISSONFLEX, RADIOCONTACT) use the *sign* of the E–W gravity derivative only; CHILISTRIC
and DRAINAGE_KNICK use pixel-scale chi/k_sn and knickzone steps, not basin integrals;
ADMITRELAY/RELAYCONDUIT/TIPGAP work on catalogue geometry, not on drainage response.
The additive allocation policy is shared with CHILISTRIC's "non-diluting additive
secondary recall expansion" — that lineage is acknowledged here rather than claimed as
new; what is new is *which* evidence the added mass is drawn from and the registry-aware
disjointness constraint (`d_parent > 3 px`).

## 5. Pre-registered falsifiers and gates

* **Leakage canary (rule 4):** every feature alone on the holdout, symmetric AUC ≤ 0.90.
* **Holdout (rule 2/3):** `gems57-pooled-hide-v2`, 22,663-class pooled folds, promotion
  requires the *new* arm to beat the same-instrument control with a paired 95 % CI above 0.
* **Uniqueness (rule 1):** surface before placement **and** final dots, against every
  registry raster, both one-sided PI-1 and the symmetric PI-2 Tversky gate.
* **Format:** 11 shared gates (finite, [0,1], zeros outside footprint, CRS/shape/transform).
* **Falsifier for the whole idea:** if MDC-only dots score below the H19-5 control on the
  holdout *and* the MODEL break-even hit rate (~10 %) is not plausibly met by the added
  arm, the mechanism is negative and must be reported as such; no slot should be spent on
  it as a promotion candidate.

## 6. Honest limitation of the instrument

`HOLDOUT-DTI` measures recovery of *withheld catalogue* faults. The leaderboard measures
faults **absent** from the catalogue. The two are anti-correlated for a collar-bearing
raster: the parent dot set scores 0.004006 on the holdout and 0.2778 CLAIM on the
leaderboard. The holdout is therefore used for *relative mechanism screening only*, and a
holdout failure is recorded as a negative screening result, never as a leaderboard forecast.
