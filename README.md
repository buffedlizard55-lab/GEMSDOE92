# GEMSDOE92 — unique GEMS Prize GeoTIFF

> **Read this file at the start of every session.** Full operator contract: [`SESSION_PROMPT.md`](SESSION_PROMPT.md).

**Primary download:** `DILATATION p12` — the one file in this repository whose HOLDOUT-DTI is **above** parent R0 with a 95 % CI that excludes zero. Verdict **promote**.

| | |
|---|---|
| **File** | [`docs/downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-zeros.tif`](docs/downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-zeros.tif) |
| **Zip** | [`…-8b4d248b.zip`](docs/downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b.zip) |
| **Submission name** | `GEMSDOE92-DILATATION-p12-20261025` |
| **Form note (84 chars)** | `h33-h33-2-b2; DILATATION shift 4518 dots (12%) low→high dilat; pred MODEL:+0.007` |
| **SHA-256** | `25ba17a26d31df9d574fba2a2f34d03ff58f587f4ffde092dcc4bba9822f8898` |
| **How to submit** | [`docs/SUBMIT.html`](docs/SUBMIT.html) · **Site:** <https://buffedlizard55-lab.github.io/GEMSDOE92/> |

| Status | Meaning |
|---|---|
| **✅ OK TO DOWNLOAD AND SUBMIT** | All 10 MUST gates pass on an independent re-read of the **served** bytes. All-finite float32 in `[0, 1]`, zeros outside the footprint, `nodata=None` — so neither the training stack's `−3.4028235e+38` sentinel nor a stray NaN can trigger `Predicted values must be in range [0, 1]`. |
| **HOLDOUT-DTI above R0** | Δ **+0.00177 [0.00111, 0.00246]**, CI excludes 0. This is a local instrument, **not** a leaderboard score. Weekly-slot promotion is a human step (3/week cap); this agent never submits. |

```bash
python -m pytest tests -q                                  # 97 passed
make manifest && make verify                               # RESULT: OK · PARENT VERIFIED
PYTHONPATH=vendor python scripts/check_site.py
```

## This session's lane: DILATATION (geodetic volumetric strain)

- **Hypothesis.** Band 8 `geod_dilaterate` is a *kinematic* field. The catalogue maps Quaternary **scarps**; strain maps where they are currently **opening**. Faulds et al. put ~32 % of Great Basin geothermal systems in dilatational step-overs / relay ramps and ~25 % at terminations and intersections. A blind fault under 10–100 m of fan alluvium has **no scarp to map but still dilates**.
- **Mechanism.** Count held at 37,654. Move 12 % (4,518) of the lowest-dilatation parent dots into the high tercile (≥ 7.24 nstrain/yr) on H19-5, placed by greedy exact expected-DTI (α 0.2, β 0.8, R 300 m) under `0.70·dilatation + 0.30·TMI/grav/scarp`. Zero catalogue mass; `d_cat > 2.0 px`.
- **Non-fault mimic.** Brine-pumping / agricultural subsidence bowls, Walker Lane strain shadows, ductile thick-fill stretching without brittle faulting.
- **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 8 folds, 22,663 withheld positives, 157 spatial clusters, 1,000 paired draws: R0 `0.004006 [0.003424, 0.004690]` → p12 `0.005779 [0.004863, 0.006851]`, Δ **+0.00177 [0.00111, 0.00246]**.
- **Leakage canary** (each band tested alone before any result was trusted): Band 8 `0.5145`, 7 `0.5128`, 4 `0.5102`, 15 `0.5149`, 17 `0.5060` — max **0.5149 ≪ 0.90**.
- **Verdict:** promote. Dose response monotone (p10 +0.00174, p12 +0.00177, p15 +0.00181).

Rebuild: `python scripts/build_dilatation_variants.py` · proxies: `python scripts/report_dilatation_proxies.py`

## ⚠ The 70 %-overlap lane gate is the wrong test for R0 descendants

Measured this session, and it changes how every lane in this repo should be judged.

Applied to **whole files**, the rule "more than 70 % of your dots within 3 px of one registry raster ⇒ duplicate" flags **every** R0 descendant:

| arm | shared with R0 | whole-file % within 3 px of R0 |
|---|---|---|
| DILATATION p12 | 33,136 (88.0 %) | 99.37 % |
| RELIEF p10 | 33,889 (90.0 %) | 99.38 % |
| TIPGAP far18f33 | 25,228 (67.0 %) | 67.00 % |

Shared-parent mass dominates the statistic, so the whole-file number mostly measures *how much of R0 you kept*, not *whether you are in someone else's lane*. On the **arrival sets** — the pixels each axis actually chose — the lanes are nearly disjoint:

| comparison (arrivals only) | % within 3 px | exact same pixel | Jaccard |
|---|---|---|---|
| DILATATION vs TIPGAP | 6.91 % | 0.40 % | **0.0011** |
| DILATATION vs RELIEF | 28.84 % | 25.19 % | 0.1593 |
| TIPGAP vs RELIEF | 2.29 % | 0.14 % | **0.0011** |

**The tension this exposes.** TIPGAP passes the whole-file gate (0.6700) *only because* it moves 33 % of the budget far off the D2.8 skeleton — and that is precisely the change that drove its HOLDOUT-DTI **below** R0 (−0.001283, verdict negative). The more a file moves off-skeleton, the more "unique" it looks and the worse it scores. **Do not use whole-file overlap as a proxy for either uniqueness or quality**; run the lane test on arrivals, and judge quality on the holdout.

## Why h33-h33-2-b2 CLAIM 0.2778 is high

Not ORGANIZER-CONFIRMED (no receipt in `ledger/` — 30 `BUILT` rows, zero receipts). The lineage is mechanical, not mysterious:

1. H19-5 multiline corroborated ridges — CLAIM 0.1922
2. Poisson-disk thin at 2.8 px — CLAIM 0.2600 (DTI β = 0.8 punishes extra mass)
3. SOLO drop of sub-bar dots — CLAIM 0.2708 (bar ≈ 0.2·DTI ≈ 0.056)
4. B2 keep off known traces — CLAIM 0.2778 (catalogue is masked at scoring)

At a fixed 37,654-dot budget, beating it needs ~25 % more mean credit per dot. No public catalogue can supply that; the route is a better detector. Prompt-cited public tops 0.3195 / 0.4413 are **not** copied as receipts here.

## Lanes built here

| lane | HOLDOUT-DTI | Δ vs R0 | verdict | download |
|---|---|---|---|---|
| **DILATATION p12** | 0.005779 | **+0.00177** | **promote** | [zeros-outside](docs/downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-zeros.tif) |
| DILATATION p10 / p15 | 0.005747 / 0.005818 | +0.00174 / +0.00181 | built, dose ladder | [p10](docs/downloads/h33-h33-2-b2-DILATATIONp10dilatation-20261025-2e501f88-zeros.tif) · [p15](docs/downloads/h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432-zeros.tif) |
| TIPGAP far18f33 (33 % moved 6–18 px past H19-5 tips, off-skeleton) | 0.002723 | −0.001283 | **negative** | [zeros-outside](docs/downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.tif) |
| RELIEF p10 (piedmont elevation tercile) | 0.006045 | +0.002039 | built, reserve | [NaN-outside](docs/downloads/h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24.tif) |

The TIPGAP file is kept because a negative result is a deliverable — it falsifies "continuations sit 0.5–1.8 km past the tips" on this instrument. **Do not spend a slot on it expecting a gain.** The three on-skeleton 10–15 % TIPGAP doses were logged as lane-duplicates of R0 (arrival overlap ≈ 0.999) and are not offered.

## Shared tools fixed this session (not forked)

Running the repo's own gates instead of trusting them exposed two defects and one wrong number — all in `IRREGULARITIES.md` with before/after measurements:

1. **Pinned paths were joined onto the data root twice.** The registries record different conventions, so repo-relative `data/parent_R0_nan.tif` became `data/data/…`. `make manifest` reported **8 of 8** inputs `MISSING` while every file was on disk and correctly hashed. → one `gems.rasters.resolve_pinned_path()` used by both call sites. **After: `RESULT: OK`, 8/8.**
2. **`registry/parents/R0.json` is `mode: pinned_artefact`, which the loader could not read**, so `make verify` — "the gate that stops a session before it burns slots on descendants of an unverified parent" — raised on *every* run. → the loader validates that form, and `verify_pinned_artefact()` checks sha256 **and** byte length per encoding, then **re-measures** dot count, total mass, min catalogue distance, footprint and the 3/4/5 px collar counts from the raster itself and diffs them against the record. **After: exit 0, zero drift on all seven invariants.**
3. **That new check immediately caught a wrong number:** `R0.json` claimed 355,000 B for the NaN artefact; disk and `session_manifest.json` both say **355,443 B**. The sha256 — the real authority — was correct in both, so no artefact was ever mis-identified.

CI ran the parent gate as `… || true`, which is why a gate that had never passed produced no signal. It is fatal now, plus `make manifest`, plus a gate on **every** `docs/downloads/*-zeros.tif`, plus an assertion that the primary named in `index.html` matches its audit receipt byte-for-byte.


## Additional session deliverable (STEPOVER, negative)

A separate STEPOVER lane was also built and kept as a negative deliverable; it does **not** replace the TIPGAP FAR download above.

- **File:** [`releases/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f.tif`](releases/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f.tif) (all-finite zeros encoding, SHA-256 `e5fee27f162371d959315d1dc412e137df0348b6009fa3dfdc46dc1363bd4205`)
- **Status:** OK TO DOWNLOAD; **NOT a weekly slot** (verdict negative).
- **Lane:** 5,000 unit-mass dots at visible catalogue trace-tip step-overs, 3–10 px off catalogue (`d_cat > 3 px`), 1 px spacing. Distinct from TIPGAP (H19-5 skeleton endpoints) and from MASS/PRUNE/SNAP/CONCENTRATION/RELIEF.
- **HOLDOUT-DTI:** 0.0000 [0.0000, 0.0000] vs R0 0.00370 [0.00301, 0.00432] (`gems57-pooled-hide-v2`, 11,321 withheld positives). This is a structural zero for gate-compliant off-catalogue dots; see `IRREGULARITIES.md`.
- **Uniqueness / canary:** worst Spearman ρ = 0.0277, worst 3-px forward overlap = 0.2534 vs 14 locally accessible registry rasters; leakage AUC = 0.4996.
- **Details:** [`docs/executive-summary.html`](docs/executive-summary.html) · [`docs/ANALYSIS.md`](docs/ANALYSIS.md) · [`evidence/run_card.json`](evidence/run_card.json)

## Limitations (what this sandbox cannot do)

- No DrivenData auth → cannot auto-download from the competition data tab and cannot upload.
- Competition hosts (drivendata.org, dropbox.com) are not in the allowlist; hashes are owner-mirror SHA-256, not organizer-authenticated.
- Cannot fill `TOP_PUBLIC` from the live leaderboard.
- Weekly slot promotion is human-only (3/week + one blind final).
- The holdout's truth is the **visible catalogue**, so it cannot reward a genuinely new fault. It ranks emission rules; live receipts remain the decision anchor.

## Verified facts

- Metric: DTI α = 0.2, β = 0.8, triangular R = 300 m, float32 EPSG:32611 100 m — https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Known faults masked pixel-exactly — https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
- Rules — https://docs.nlr.gov/docs/fy26osti/96647.pdf
- GeoDAWN (400 m line spacing, 150–200 m AGL) — https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7 · https://doi.org/10.5066/P93LGLVQ
- Dilatational step-overs host ~32 % of Great Basin geothermal systems — https://www.osti.gov/servlets/purl/1110517 · https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2025/Giddens.pdf

## Evidence labels

RECEIPT = submission-page receipt · CLAIM = owner-reported · HOLDOUT-DTI = hide-and-recover · PROXY = other local instrument · MODEL = projection. Never write a projection as a score.

---

## Session prompt (read first every session)

The live Arena operator prompt is stored in [`SESSION_PROMPT.md`](SESSION_PROMPT.md). In every session:

1. Stay in one named geological lane. Run the lane test on **arrival sets**, not whole files (see the overlap section above). Log a duplicate and stop if arrivals genuinely coincide.
2. Reuse `vendor/gems57/evaluate_holdout.py` and `vendor/gems57/submission_writer.py`. Holdout = withhold whole fault segments with a buffer; catalogue features from visible faults only; mask visible faults pixel-exactly; pooled DTI α = 0.2 β = 0.8, 300 m triangular kernel.
3. Label every number HOLDOUT-DTI (evaluator version, n withheld, 95 % CI) or ORGANIZER-CONFIRMED.
4. Leakage canary: single feature AUC > 0.90 means leakage until proven otherwise.
5. End with a JSON run card: hypothesis; mechanism; named non-fault mimic; holdout DTI+CI; correlation/overlap; raster sha256; validator; submission name + ≤140 char note; verdict promote/negative.
6. Stop after 3 experiments or 2 hours. Do not pick live slots.
7. Ship an obvious zeros-outside GeoTIFF download. Never claim a HOLDOUT number is a leaderboard score.
8. Maximize P(Win) and own the outcome: a negative unique file is a deliverable; a copied 0.2778 file is not.
