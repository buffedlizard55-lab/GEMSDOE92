# Analysis — LCS lane (leaderboard-calibrated lane consensus), session 2026-10-24

Branch `arena/949d4182-gemsdoe92`. Evidence classes: **CLAIM** (operator-reported score) · **MODEL** · **REGISTRY-MEASUREMENT** ·
**HOLDOUT-DTI** (`gems57-pooled-hide-v2`) · **OFFICIAL**. Nothing here is ORGANIZER-CONFIRMED; no slot was selected or used.

## 1. Result in one paragraph

A unique single-band float32 GeoTIFF was generated and passes every automated gate: `GEMSDOE92-lcs-consensus-37654-20261024-58fd2c77-zeros.tif`,
37,654 unit-mass dots, sha256 `04f6b587ad873313…`, strict 3-px catalogue distance, all finite in [0, 1], zeros outside the footprint.
Under the recorded policy it is **OK TO DOWNLOAD** and **OK TO SUBMIT** (valid and not a copy of any operator-scored raster; final dots also not
a copy of any of 861 non-blanket registry rasters), and its **slot verdict is negative** under the pre-registered holdout rule — an
instrument that is degenerate for this file (exactly 0 by construction). Its MODEL projection is 0.263–0.321 against R0's claimed 0.2778 with one typical
model error of ± 0.066, so **no improvement over R0 is claimed**; it is an exploration arm.

## 2. Experiments (budget: 3; all pre-ranked in `HYPOTHESES_20261024_LCS.md`)

| # | experiment | instrument | result |
|---|---|---|---|
| 1 | Does a lane's agreement with the *other* lanes predict its leaderboard-implied credit per dot? | 11 independent lanes, CLAIM scores → MODEL credit; permutation test | Spearman **+0.75** (p = 0.005 permutation; 0.007 analytic); **+0.60** (p = 0.088) without the two SGMC lanes (n = 9) |
| 2 | Leave-one-lane-out credit model; consensus selection under overlap caps | `scripts/lcs_loo_calibration.py`, `build_lcs_candidate.py` | γ = 0.30: Spearman **+0.83**, MAE **0.034** credit/dot (null γ = 0: −0.24 / 0.049); selection feasible under all caps (below) |
| 3 | Registry gates (both phases), HOLDOUT-DTI, canary, SGMC control | vendor `compare_array_to_registry` unchanged; shared evaluator | see §4–§6 |

## 3. Builds and deviations (all disclosed; only the last file is shipped)

1. **v1** `d683f02e` — pool d_cat > 2 px, Tier-S caps only. Superseded.
2. **v2** `74a76cb1` — + Tier-L active set. The vendor gate found one Tier-L violation (0.7254) from a raster that is "dense by support" (22 %) but has halo
   coverage 0.478: my pool step had classified rasters by *support*, not by *halo coverage*. Fixed (halo-coverage class computed in the tracked pool script). Superseded.
3. **v3** `58fd2c77` — pool d_cat > 3 px (brief constraint 4; found while reading `gems/gates.py`: CI's `--prune-radius 2` makes the 3-px gate vacuous, and a new lane
   should honour it honestly), halo-class membership, active-set Tier-L rounds. **Shipped.**
4. **Deviation from pre-registration wording:** γ was fixed at 0.30 when the first prototype had 0.30 as the MAE minimiser. On the final pool the MAE minimiser is 0.75 (0.017)
   while Spearman — the criterion that matters for a *rank-based* selection — still peaks at 0.30. γ was kept; the shift is in `evidence/lcs_loo_calibration.json`.
5. **Correction of my own reading:** an all-at-once Tier-L cap collapses rank-quality (0.244–0.303); that is an optimizer artefact, not a property of the problem (active-set: 0.638).

## 4. What the file is (MEASURED)

* 37,654 dots (budget matched to R0), min spacing 2.83 px (no pair closer), min distance to any mapped fault **3.16 px** (0 dots within 3 px; R0 has 2,171).
* Only **8.3 %** of its dots coincide with R0's; 3.6 % lie within 5 px of a mapped fault (R0: 15.0 %); mean distance to the catalogue 30.7 px (R0 median 19.6).
* Mean lane agreement 5.7 of 10 voters per dot (uncapped selection: 7.1).
* Continuity (dots linked when ≤ 3.2 px apart): singletons **29.2 %** (R0 27.6 %, random control 88.1 %); on strings of ≤ 3 dots 56.7 % (R0 53.9 %); median nearest-neighbour spacing 3.00 px for both. The file is as string-like as R0, not patchier (the zoomed map looks patchier only because of how it is rendered). A continuity prune (the fragment probe's logic) would apply to it equally — a next-step item, not applied here.
* Selection: Lagrangian rank-sum maximisation under per-raster overlap caps (0.67) against the 26 scored rasters plus six Tier-L rasters the first solution violated; deterministic.

## 5. Uniqueness (REGISTRY-MEASUREMENT) — full table in `UNIQUENESS_POLICY_20261024.md`

* Tier S (26 scored rasters; 56 files): final max overlap **0.637**, surface **0.676**, max |ρ| 0.168 / 0.358 — **pass, both phases** (decisive tier).
* Tier L (861 non-blanket rasters): final max **0.697** (pass); **surface fails** — its 331k-pixel support overlaps four very large rasters (336k–1.1M dots) at 0.72–0.81.
* Tier T (literal, 924 distinct rasters): fails (61 distinct / 83 files over 0.70) — and so does a random file (51 / 66).
* Rank correlation is never the binding constraint: max |ρ| = 0.168 against all 924 rasters.

## 6. HOLDOUT-DTI, canary, SGMC (PROXY)

| arm | HOLDOUT-DTI (22,663 withheld; 8 folds) | 95 % CI | SGMC control DTI |
|---|---:|---|---:|
| parent R0 | 0.004006 | [0.003406, 0.004668] | 0.09606 |
| RELIEF p10 (repository holdout best) | 0.006045 | [0.005260, 0.006954] | 0.08725 |
| **LCS (this file)** | **0.000000** | [0, 0] | **0.10921** |
| LCS uncapped (research) | 0.000000 | [0, 0] | 0.10716 |
| random spaced control | 0.000000 | [0, 0] | 0.07426 |

* **The holdout is degenerate for this file, by construction.** Its truth is withheld *mapped* faults; every LCS dot is > 3 px from every mapped fault (withheld ones included),
  so no dot can reach a withheld pixel (kernel radius 3 px). The random control also scores 0. **R0's entire holdout signal (0.004006) comes from its 2,171 dots at 2.24–3.0 px from the
  catalogue** — the population the live ladder says is worth very little (the 1.0 px and 1.41–2.0 px groups carried ≈ 0 credit). The instrument therefore cannot rank any file that honours
  the 3-px rule, and its pre-registered "beat the holdout best" bar is unreachable for such files. Verdict (rule applied literally): **negative**; weight of that verdict as evidence about the idea: ≈ none.
* Leakage canary (lane-vote sum alone, hidden segments vs background): symmetric AUC **0.519** — pass; the consensus does not encode the catalogue.
* SGMC control: LCS 0.1092 vs R0 0.0961 (+0.0131) and random 0.0743. SGMC faults are *not* the leaderboard truth (SGMC-lane files score ≈ 0.05 live), so this is a control, not support.
* Neither holdout nor SGMC is fold-pure for lane voters built from the full catalogue.

## 7. What can and cannot be concluded

* **Supported (CLAIM + MODEL):** consensus among lanes tracks lane quality (ρ +0.60 to +0.83 depending on subset); the catalogue re-detection halo is real (zero-credit ladder, 3.2× enrichment at 1–2 px).
* **Not supported:** that this file beats R0. Projection 0.263 (shrunk) – 0.288 (null) – 0.321 (naive) with ± 0.066 typical model error. The projection is *not* a score.
* **The decisive unknown** is the credit of the consensus dots that lie outside R0's halo and of dots just beyond the re-detection halo (3–7 px); only an organizer receipt resolves it. If a slot is spent on this file, the
  *score difference to R0 at the same budget* is the cleanest experiment available: same N, same spacing, same exclusion rule, different positions.

## 8. Limitations and access needed

* Scores are CLAIMs; 8 of 12 lane↔file ties are by name (`ledger/claimed_scores_20261024.csv`, confidence column); sites 46 and 62 are unmatched.
* Registry scope = the owner's public default branches (1,321 files / 924 distinct contents); sibling sessions in flight and other owners are invisible.
* No access from this sandbox to USGS 3DEP lidar, ScienceBase or the GeoDAWN survey metadata (only `github.com`, PyPI, npm are reachable from the shell; page text of official sites was
  readable through the page-fetch tool, binaries were not). Hypotheses 2 and 5 in the ranked list need that access (or a GPU for hypothesis 2).
* A DrivenData organizer receipt for any file, and the verbatim operator score list, are the two inputs that would change this analysis most.
