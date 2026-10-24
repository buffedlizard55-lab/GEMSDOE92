# GEMSDOE92 — unique GEMS Prize GeoTIFF

A parallel RELIEF session on `main` produced `RELIEFp10piedmont` that **fails** the 70% overlap gate (99.38% within 3 px of R0) and is inspection-only. This branch's TIPGAP FAR file is the unique zeros-outside download (overlap 0.6700).

**Read this file at the start of every session.** Full operator contract: [`SESSION_PROMPT.md`](SESSION_PROMPT.md).

## Download (start here)

| Status | Meaning |
|---|---|
| **OK TO DOWNLOAD** | Local format gates passed. All-finite float32 in `[0, 1]`. Zeros outside the footprint. Use this file — a NaN-outside twin previously triggered `Predicted values must be in range [0, 1]`. |
| **NOT a weekly slot** | HOLDOUT-DTI is below parent R0. Verdict = **negative**. Human quota check required before any DrivenData upload. This agent never submits. |

- **Site:** <https://buffedlizard55-lab.github.io/GEMSDOE92/> (enable GitHub Pages → `docs/` if the URL 404s)
- **File:** [`docs/downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.tif`](docs/downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.tif)
- **Zip:** [`docs/downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.zip`](docs/downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.zip)
- **Submission name:** `h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a`
- **Form note (89 chars):** `h33-h33-2-b2; TIPGAP FAR 33% along-strike >3px off parent skeleton e6-18; unique lane`
- **SHA-256:** `0ca8248acace558f5cf86b153134b8fd5cc2b7d5b343d0a36f000f9fbfe4758f`
- **How to submit:** [`docs/submit.html`](docs/submit.html)

```bash
python -m pytest tests -q
PYTHONPATH=vendor python scripts/check_site.py
```

## Why h33-h33-2-b2 CLAIM 0.2778 is high

Not ORGANIZER-CONFIRMED (no receipt in `ledger/`). The lineage is:

1. H19-5 multiline corroborated ridges — CLAIM 0.1922
2. Poisson-disk thin at 2.8 px — CLAIM 0.2600 (DTI β=0.8 punishes extra mass)
3. SOLO drop of sub-bar dots — CLAIM 0.2708
4. B2 keep off known traces — CLAIM 0.2778 (catalogue is masked at scoring)

Beating 0.2778 on the live public chunks is possible in principle (prompt-cited public tops 0.3195 / 0.4413 are **not** copied as receipts here). This session’s unique far-tip file did **not** beat R0 on hide-and-recover.

## This session (TIPGAP FAR)

- **Lane:** along-strike tip extensions of the H19-5 skeleton that sit **>3 px from every parent dot** (off the D2.8 packing). Not SNAP (≤2 px cross-strike), not RELIEF (elevation tercile), not PRUNE (catalogue distance), not CONCENTRATION (1 km blocks), not MASS.
- **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 22,663 withheld positives, 95% CI: **0.002723 [0.002324, 0.003131]** vs R0 **0.004006 [0.003408, 0.004651]**. Delta −0.001283 (HOLDOUT-DTI, never a score).
- **Leakage canary** (distance to H19-5 endpoint) symmetric AUC 0.6199 ≪ 0.90.
- **Uniqueness vs local registry:** parent overlap-within-3 px = 0.6700; Spearman = 0.6690. On-skeleton 10–15% doses overlapped parent at ~0.999 and were **not** offered for download.
- **Verdict:** negative.

Rebuild: `PYTHONPATH=vendor python scripts/build_tipgap_far.py`


## Additional session deliverable (STEPOVER, negative)

A separate STEPOVER lane was also built and kept as a negative deliverable; it does **not** replace the TIPGAP FAR download above.

- **File:** [`releases/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f.tif`](releases/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f.tif) (all-finite zeros encoding, SHA-256 `e5fee27f162371d959315d1dc412e137df0348b6009fa3dfdc46dc1363bd4205`)
- **Status:** OK TO DOWNLOAD; **NOT a weekly slot** (verdict negative).
- **Lane:** 5,000 unit-mass dots at visible catalogue trace-tip step-overs, 3–10 px off catalogue (`d_cat > 3 px`), 1 px spacing. Distinct from TIPGAP (H19-5 skeleton endpoints) and from MASS/PRUNE/SNAP/CONCENTRATION/RELIEF.
- **HOLDOUT-DTI:** 0.0000 [0.0000, 0.0000] vs R0 0.00370 [0.00301, 0.00432] (`gems57-pooled-hide-v2`, 11,321 withheld positives). This is a structural zero for gate-compliant off-catalogue dots; see `IRREGULARITIES.md`.
- **Uniqueness / canary:** worst Spearman ρ = 0.0277, worst 3-px forward overlap = 0.2534 vs 14 locally accessible registry rasters; leakage AUC = 0.4996.
- **Details:** [`docs/executive-summary.html`](docs/executive-summary.html) · [`docs/ANALYSIS.md`](docs/ANALYSIS.md) · [`evidence/run_card.json`](evidence/run_card.json)

## Limitations (what this sandbox cannot do)

- No DrivenData auth → cannot auto-download `training_features.tif` from the competition data tab and cannot upload.
- Competition hosts (drivendata.org, dropbox.com) are not in the allowlist; hashes are owner-mirror SHA-256, not organizer-authenticated.
- Cannot fill `TOP_PUBLIC` from the live leaderboard.
- Weekly slot promotion is human-only (3/week + one blind final).

## Verified facts

- Metric: DTI α=0.2, β=0.8, triangular R=300 m, float32 EPSG:32611 100 m — https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Known faults masked pixel-exactly — https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
- Rules — https://docs.nlr.gov/docs/fy26osti/96647.pdf
- GeoDAWN — https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7

## Evidence labels

RECEIPT = submission-page receipt · CLAIM = owner-reported · HOLDOUT-DTI = hide-and-recover · PROXY = other local instrument · MODEL = projection. Never write a projection as a score.

---

## Session prompt (read first every session)

The live Arena operator prompt is stored in [`SESSION_PROMPT.md`](SESSION_PROMPT.md). In every session:

1. Stay in one named geological lane. If rank-correlation with a registry raster exceeds 0.90 **or** more than 70% of dots fall within 3 px of one registry raster, log a duplicate and stop.
2. Reuse `vendor/gems57/evaluate_holdout.py` and `vendor/gems57/submission_writer.py`. Holdout = withhold whole fault segments with a buffer; catalogue features from visible faults only; mask visible faults pixel-exactly; pooled DTI α=0.2 β=0.8, 300 m triangular kernel.
3. Label every number HOLDOUT-DTI (evaluator version, n withheld, 95% CI) or ORGANIZER-CONFIRMED.
4. Leakage canary: single feature AUC > 0.90 means leakage until proven otherwise.
5. End with a JSON run card: hypothesis; mechanism; named non-fault mimic; holdout DTI+CI; correlation/overlap; raster sha256; validator; submission name + ≤140 char note; verdict promote/negative.
6. Stop after 3 experiments or 2 hours. Do not pick live slots.
7. Ship an obvious zeros-outside GeoTIFF download. Never claim a HOLDOUT number is a leaderboard score.
8. Maximize P(Win) and own the outcome: a negative unique file is a deliverable; a copied 0.2778 file is not.
