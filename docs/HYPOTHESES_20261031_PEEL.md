# 2026-10-31 — PEEL lane: pre-registered hypotheses (written before implementation)

## What the evidence says before writing any code

1. **The scoring truth is not the catalogue.** The problem description states that the test set is made of faults
   expert-labelled *and absent from the public USGS database*
   ([page 967, "Competition structure"](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)).
   The competition `labels.tif` is byte-identical to `existing_faults.tif` in this repository
   (`sha256 7ba308cc…4093`), i.e. it *is* the mapped catalogue. Predicting the catalogue therefore earns nothing
   directly; it only costs `α·FP` where it is wrong about a *new* fault.
2. **Recall dominates, but emitted mass is not free.** `DTI = TPw / (TPw + 0.2·FPw + 0.8·FNw)` with a 300 m triangular
   kernel; `TPw` takes a per-truth-pixel maximum while `FPw` sums linearly. The marginal test for adding one unit-mass
   dot is `t > α·DTI·(t+f)`, i.e. it pays if its chance of landing within 3 px of a still-uncovered truth pixel exceeds
   `α·DTI/(1−α·DTI) ≈ 0.06` at DTI 0.28. That single inequality explains the whole observed score ladder
   (121,131 dots → 0.1922; 44,090 → 0.2600; 37,654 → 0.2778): the dots are being removed until the average marginal
   contribution stops clearing the bar.
3. **The nine focus sites are one artifact.** Measured this session, dot-for-dot from the bytes each site publishes:
   no pair of the nine peaks has less than **85.7%** of one's dots inside the other's 3 px halo
   (`evidence/peel_nine_site_overlap_20261031.json`). Any new candidate must therefore come from a different
   *score field*, not from re-tuning the same skeleton.
4. **The catalogue-free inputs exist in public mirrors.** The official `training_features.tif` is a Git-LFS pointer in
   every public copy located; six derived rasters are committed as real bytes and were sha-verified locally
   (`evidence/peel_features.json`). They cover radiometrics + ratios, upward-continued TMI, 10 m DEM scarp morphology,
   topographic lineaments, chi-drainage, SGMC faults and TIGER roads.

## Candidate hypotheses (ranked by expected gain per unit cost)

Each entry names the layers, the physical signature, why it should find a fault that is *missing from the catalogue*
rather than one already in it, and how it differs from what this repository has already run.

| # | Hypothesis | Layers → signature | Why it targets *unmapped* faults | Differs from existing code | Non-fault mimic | Rank rationale | Cost |
|---|---|---|---|---|---|---|---|
| H1 | **Polarised-escarpment × alteration concordance** | LiDAR `downface_max`/`upface_max`/`lapneg_max`/`step_max` + `coh100` strike coherence; gated by radiometric `ThK`, `UK`, `UTh` | A scarp that exists at 10 m but was never drawn into a 1:500k–1:1M compilation, with an alteration halo marking the fluid path. Nothing reads the catalogue, so an already-mapped trace gets no bonus | Earlier relief lanes used the official `det_elev_slope` band and analytic-signal magnetics; the *polarised* down-face/up-face pair plus 100 m strike coherence and a radiometric ratio gate is a different operator set | Bedrock lithologic contacts, volcanic rims, eolian/playa margins, canals | Highest specificity per unit cost: the signature is morphological and cheap, and the alteration gate is an independent physical constraint | Low (all columns present) |
| H2 | **Concealed-basement magnetic structure** | `mag_TMI_up150` (upward-continued, deep source) + multi-scale lineament context + `chi_chan_n`/`chi_knick_n`/`chi_raised_n` | This is the named blind spot of the 0.2778 family: intrabasin faults under playa/lacustrine fill where surface slope vanishes and topographic detectors are blind | Upward-continued TMI suppresses shallow volcanic noise, which is the opposite of the analytic-signal emphasis used in `EULERFUSE`/`ANASIG`; chi-drainage is a fluvial-response operator, not a relief one | Remanent magnetisation, basaltic flows, demagnetised alteration zones | Potentially the largest recall gain because it addresses the failure mode the incumbent cannot see; noisier, so it must be tested inside a joint model rather than alone | Low |
| H3 | **Anthropogenic veto** | `tiger_road_distance_m` as an explicit negative | Canals, roads and rail beds are the dominant straight-line mimics in an arid basin; a model that can *see* them can refuse them | Prior lanes filtered length/straightness geometrically; this is a direct confounder covariate | — (this *is* the confounder model) | Precision-only gain; cheap and additive to any arm | Very low |
| H4 | **Independent bedrock catalogue** | SGMC `derived_sgmc_faults_100m` presence + distance | Adds linework the competition labels do not contain at all | Earlier lane `sgmc-off-catalogue-44k` used SGMC alone and claimed 0.0512 — weak as a primary field | Pre-Quaternary bedrock faults with no Quaternary expression | Low as a primary field, plausible as one input among many | Low |
| H5 | **Channel-offset persistence** | Multi-channel lateral displacement (needs 1 m DEM + high-resolution flowlines) | Strike-slip splays buried in fans | Not implemented; requires data not staged here | Irrigation, drainage capture, inherited topography | Genuinely novel but not runnable | High — **not viable from this checkout**, so not proposed as an experiment |

## Pre-registered experiment plan (three arms, one factor at a time, budget 3)

* **E1** = H1 only (structural columns, no radiometrics).
* **E2** = H1 + radiometrics/ratios (adds the alteration gate).
* **E3** = all 44 columns (adds H2, H3, H4 and multi-scale context).
* Controls: the incumbent's construction (`d28` minus 2 px of visible catalogue) and a uniform-random dot field at the
  same budget and the same exclusion collar.
* Fixed by design so that arms differ in exactly one thing: budget 37,654 unit-mass dots, NMS separation 2.8 px,
  ≥2 px catalogue clearance, and the shared `gems57-pooled-hide-v2` instrument with 8 spatially blocked folds.
* Stop rule: three experiments, then report. **No submission slot is selected here**; promotion is a separate decision
  and requires beating the repository's archived all-time holdout best.

## Leakage control

No column is a function of `existing_faults.tif`/`labels.tif`; the catalogue enters only as the training label and as a
placement exclusion. The hide-and-recover rule ("derive every catalogue-based feature only from the visible faults") is
therefore satisfied by construction, and is additionally checked empirically by a single-column canary
(`AUC > 0.90` ⇒ leakage) on the withheld truth.

## Results (filled in after the run; see the executive summary)

See [`executive-summary-20261031-peel.html`](executive-summary-20261031-peel.html),
[`evidence/peel_holdout_20261031.json`](../evidence/peel_holdout_20261031.json) and
[`evidence/peel_score_estimate_20261031.json`](../evidence/peel_score_estimate_20261031.json).
