# GEMSDOE92 — unique GEMS Prize GeoTIFF

> **Read this file at the start of every session.** Full operator contract: [`SESSION_PROMPT.md`](SESSION_PROMPT.md).

**Primary download (2026-10-24):** `BREAKLINE f45Ltop` — the first file in this repository that is **both** literal-unique under the operator's rule (55.0 % of dots within 3 px of R0, worst of 17 registry rasters) **and** above parent R0 on the holdout with a paired 95 % CI excluding zero. **Format-valid and OK to download, but NOT cleared for a weekly slot:** it does not beat the current holdout best (RELIEF p10, 0.006045 — itself a literal duplicate of R0), so the pre-registered promotion rule returns verdict **negative / NOT_CLEARED**. See ⚠ below.

| | |
|---|---|
| **File** | [`docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif`](docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif) |
| **Zip** | [`…-57fa85f0.zip`](docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0.zip) |
| **Submission name** | `GEMSDOE92-BREAKLINE-f45Ltop-20261024` |
| **Form note (90 chars)** | `h33-h33-2-b2; BREAKLINE f45Ltop 16944 far dots on linear scarp-break ridges >3px off H19-5` |
| **SHA-256** | `cd9c8a564588e6542b379cd36cbe05fc6da3be07b8edbc542bf737336907810e` |
| **How to submit** | [`docs/SUBMIT.html`](docs/SUBMIT.html) · **Site:** <https://buffedlizard55-lab.github.io/GEMSDOE92/> |

| Status | Meaning |
|---|---|
| **✅ FORMAT-VALID — OK TO DOWNLOAD** | All 10 MUST gates pass on an independent re-read of the **served** bytes. All-finite float32 in `[0, 1]`, zeros outside the footprint, `nodata=None` — so neither the training stack's `−3.4028235e+38` sentinel nor a stray NaN can trigger `Predicted values must be in range [0, 1]`. |
| **⚠ NOT CLEARED FOR A SLOT** | HOLDOUT-DTI 0.004861 does not beat the holdout best (RELIEF p10, 0.006045, unsubmittable duplicate). Verdict by the pre-registered rule: **negative**. Any upload is a recorded **human decision**, not an agent recommendation. |
| **HOLDOUT-DTI above R0** | Δ **+0.000854 [+0.000300, +0.001423]**, CI excludes 0; off-catalogue SGMC control **+31 %** vs R0. Local instruments, **not** leaderboard scores. Weekly-slot promotion is a human step (3/week cap); this agent never submits. |

```bash
python -m pytest tests -q                                  # full suite passes (incl. tests/test_breakline_variants.py)
make manifest && make verify                               # RESULT: OK · PARENT VERIFIED
PYTHONPATH=vendor python scripts/check_site.py
```

## This session's lane: BREAKLINE (linear DEM scarp-break coherence)

- **Hypothesis.** Quaternary scarps are *linear breaks-in-slope*. A fault juxtaposing like lithologies or offsetting only alluvium has a scarp but no magnetic/gravity contrast, so the H19-5 potential-field worm skeleton — and the catalogue built from mappable scarps on older imagery — misses it, while expert mapping on high-resolution DEMs (the live label source) traces it. Lane surface: `L = pct_rank(||grad det_elev_slope||) (Band 19) × structure-tensor coherence of det_elev (Band 12)` — `gems/breakline.py`.
- **Mechanism.** Count held at 37,654. Keep 20,710 R0 dots by exact expected-DTI greedy under `0.30 + 0.70·L_pct` (donors = coverage-redundant dots); emit 16,944 far dots (45 %) by descending L at ≥ 2.8 px spacing on pixels > 3 px from **every** H19-5 pixel and > 2 px from the catalogue. Lower doses f33/f38 built as controls; dose-monotone on all local instruments.
- **Non-fault mimic.** Pleistocene Lake Lahontan shorelines and wave-cut terraces; alluvial-fan segment boundaries; incised channel/canyon-rim breaks.
- **HOLDOUT-DTI** `gems57-pooled-hide-v2`, whole-segment hiding (seeds 20/30), 22,663 withheld positives, 157 spatial clusters, 1,000 paired draws: R0 `0.004006` → f33 `0.004673` → f38 `0.004761` → f45 `0.004861 [0.004032, 0.005822]`; RELIEF p10 control reproduced at `0.006045`. **SGMC control** (PROXY, 62,703 off-catalogue truth px): R0 `0.09606` → f45 `0.12611` (+31 %); RELIEF p10 `0.08725`.
- **Leakage canary** (each feature alone, symmetric AUC vs withheld truth): L `0.6216`, Break `0.5685`, coherence `0.5521` — max **0.6216 ≪ 0.90**.
- **Pass-2 correction on record.** The first builds emitted far dots with the exact expected-DTI greedy (ridge-restricted pool) and measured flat vs R0; review showed the screened spaced-top-L emission dominates it on every local instrument (paired **+0.000701 [+0.000321, +0.001161]**). Those three rasters are preserved as SUPERSEDED evidence (`evidence/breakline_*_exactgreedy_superseded.json`); the Ltop doses implement the screened rule.
- **Verdict:** **negative / NOT_CLEARED** — unique and parent-dominating, but below the holdout best. Files are format-valid and served as deliverables.

Rebuild: `python scripts/build_breakline_variants.py` · instruments: `python scripts/report_breakline_proxies.py` · run card: `python scripts/make_breakline_run_card.py` · ranked lanes: [`docs/HYPOTHESES_20261024_BREAKLINE.md`](docs/HYPOTHESES_20261024_BREAKLINE.md) · full analysis: [`docs/ANALYSIS_20261024.md`](docs/ANALYSIS_20261024.md)

### Previous session's lane: DILATATION (retained, not cleared)

Move 10–15 % of the lowest-dilatation parent dots (Band 8 `geod_dilaterate`) into the high tercile on H19-5 by exact expected-DTI greedy. HOLDOUT-DTI p12 `0.005779`, Δ +0.00177 [0.00111, 0.00246]; canary max `0.5149`. All doses measure 99.37–99.40 % within 3 px of R0 → **literal duplicates, NOT cleared**; SGMC control falls ∼ −0.015. Rebuild: `python scripts/build_dilatation_variants.py`.

## ⚠ Unique and parent-dominating at last — but still not cleared

**Update 2026-10-24 — the long-standing blocker moved.** Earlier revisions of this README stated that under the operator's literal rule this repository had *nothing submittable*: every holdout-positive arm was a 99.37 % duplicate of R0, and the only literal-unique arm (TIPGAP) was holdout-negative. BREAKLINE breaks that coupling. Applied to **whole files**, the rule "more than 70 % of your dots within 3 px of one registry raster ⇒ duplicate" now reads:

| arm | shared with R0 | whole-file % within 3 px of R0 |
|---|---|---|
| **BREAKLINE f45Ltop** | 20,710 (55.0 %) | **55.00 %** |
| BREAKLINE f38Ltop / f33Ltop | 23,345 / 25,228 | 62.00 % / 67.00 % |
| DILATATION p12 | 33,136 (88.0 %) | 99.37 % |
| RELIEF p10 | 33,889 (90.0 %) | 99.38 % |
| TIPGAP far18f33 | 25,228 (67.0 %) | 67.00 % |

Because R0 ⊂ SOLO ⊂ D2.8 ⊂ H19-5 **exactly** (re-verified pixelwise 2026-10-24) and every far dot is > 3 px from every skeleton pixel, BREAKLINE's overlap with *any* skeleton file equals its kept fraction by construction; measured worst-case over 17 pre-session registry rasters is the parent, at 0.55001 forward / |ρ| 0.547. **Literal-unique, no reinterpretation needed.** On **arrival sets** the older lanes remain nearly disjoint from each other (DILATATION vs TIPGAP 6.91 % within 3 px, Jaccard 0.0011; DILATATION vs RELIEF 28.84 %, Jaccard 0.1593; TIPGAP vs RELIEF 2.29 %) — relevant to lane attribution, never a substitute for the literal gate.

**Which reading governs.** The literal rule still governs — reinterpreting an operator gate in your own favour is exactly the move that lets a non-compliant file look compliant, and BREAKLINE needs no such favour. What it fails is this repository's *stricter* promotion rule (beat the holdout best). An upload is therefore still a recorded human decision, not an agent recommendation. (An earlier revision of this README carried `Verdict: promote` for DILATATION p12; superseded — see `IRREGULARITIES.md` 2026-10-25.)

**The tension that remains.** The holdout hides catalogue faults, so it prices *rediscovery* of catalogue-style faults — where the duplicate near-skeleton arms excel — while the live board prices *new mapping*, where the catalogue-independent SGMC control says off-skeleton structural lines carry signal every skeleton arm sacrifices. No local instrument arbitrates between those; only an organizer receipt does, and `ledger/` has none (36 BUILT rows, 0 receipts). That is now the programme's single most valuable missing datum — see [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md).

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
- **Details:** [`docs/ANALYSIS.md`](docs/ANALYSIS.md) · [`evidence/run_card.json`](evidence/run_card.json) (the old `docs/executive-summary.html` STEPOVER page now redirects to `docs/SUBMIT.html`)

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
