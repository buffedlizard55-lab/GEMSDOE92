# Hypotheses — 2026-10-25 SPRINGALIGN session (ranked BEFORE building)

> **Historical upstream hypothesis record; not current or authorized.** The filename date is later than this review's 2026-10-24 date and source/cache statements were not revalidated here. No candidate can pass the current literal full-footprint witness stop. See [`REVIEW_CURRENT.md`](REVIEW_CURRENT.md) and the current [`HYPOTHESES.md`](HYPOTHESES.md).

Budget: max 3 experiments / 2 h. Top candidate validated on shared
`gems57-pooled-hide-v2` holdout (22,663 withheld positives) before any
slot recommendation. No slot is spent here regardless of outcome.

| Rank | Hypothesis (layers + signature) | Why a catalogue-missing fault | Differs from this repo | Cost / viability |
|---|---|---|---|---|
| 1 | **SPRINGALIGN** — GDR wellspring CSV (pinned `gdr_wellspring_in_footprint`, GDR #1391 https://gdr.openei.org/submissions/1391): hot points (temp_c ≥ 40 °C, deduped by pixel, max temp kept); pair segments 10–60 px apart; vote along segment + 25% strike extension, weighted √(TᵢTⱼ)/100; surface = accumulated strike votes, percentile-ranked | Geothermal upflow needs fracture permeability; springs on a blind/splay fault align along its strike even where the fault has no scarp, no magnetic contrast and no catalogue trace. Alignment (pair geometry) is the signal, not spring proximity | NEXT_STEPS (ANASIG session) item 4 names spring-pair *alignment* as the one untested vent construction; no prior lane used pair geometry (density/proximity screens only, never built) | Low; data already pinned & SHA-verified in-repo. No new external data needed |
| 2 | GRAVCrest crest-line (Band 18 signed × coherence Band 13) | Buried density edge under alluvium | Never built, but **screened 2026-10-24: far SGMC 0.005–0.016 vs BREAKLINE 0.072 → falsified**; not retried without a new gravity product | Low / not viable on screen |
| 3 | Radiometric K/Th gradient (GeoDAWN rad, pinned) | Alteration halo on fluid conduit | Screened AUC≈0.50 in prior sessions ("do not retry radiometric K/Th gradients") | Medium / not viable on screen |
| 4 | SHORELINE-suppressed BREAKLINE (Bands 12/19 − Lahontan stillstand mask) | Scarp detector minus its named mimic | Needs NBMG/USGS shoreline grid **not downloaded/coverage-checked here** → per protocol not proposed as viable this session; also BREAKLINE-family keep overlap risk | Medium / held |
| 5 | Coulomb/dilatation × far lineament (Bands 4/7/8 × BREAKLINE L) | Currently-loading blind strand | STRAINBREAK already built this family (f45–f75, plateau, negative vs RELIEF p10) | Low / exhausted |

**Named non-fault mimic for rank 1:** springs also align along lithologic
contacts, paleochannel margins, irrigation/aqueduct lines and playa
shorelines; a spring line is permeability, not proof of a fault.

**Pre-registered build rule (rank 1, single dose, far count capped by spaced line capacity (amended pre-results to 4,000; see IRREGULARITIES 2026-10-25)):** 37,654 dots;
keep = exact-DTI greedy over R0 under w=0.30+0.70·S_pct (H19-5 support);
far = 16,944 spaced-top-S dots (2.8 px floor), >3 px off H19-5, d_cat>2 px.
Promote only if: HOLDOUT-DTI beats RELIEF p10 (0.006045) with paired CI
excluding 0 vs R0, canary ≤0.90, local final-dot overlap ≤0.70 and |ρ|≤0.90
vs every local registry raster, 10/10 format gates. Otherwise **negative**:
format-valid, OK to download for research, NOT cleared for a weekly slot.
The known dense-registry witness (17GEMSDOE E-proba, 100% footprint halo)
is reported, not waived.
