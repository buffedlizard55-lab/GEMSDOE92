# GEMSDOE92 — DILATATION axis session (2026-10-25)

> **Prompt in this repo — read every time we work.** The goal is to place top of the DOE GEMS Prize leaderboard (DrivenData #306) with a scientifically credible, unique submission. The site must generate a **verified, submission-ready single-band GeoTIFF (CRS/shape/transform match, values in [0,1], no NaN inside, zero catalogue mass)** that is **obviously downloadable** from the GitHub Pages site — inspection must be code, not manual eyes. Every number is labelled HOLDOUT-DTI (evaluator version, n_withheld, 95% CI) or ORGANIZER-CONFIRMED (receipt) or MODEL (projection, never a score). Leakage canary: test each feature alone, AUC>0.90 means stop. Run card ends every session. Budget 3 experiments or 2 hours. Core values: Maximize P(Win), Own the Outcome. No hallucination — verify line-by-line with official links.

## CURRENT STATE
- **Parent R0**: `h33-h33-2-b2` (GEMSDOE32), 37,654 unit-mass dots; exact lineage rebuild matches both pinned SHA-256 digests (`zeros`: `c55bafc4…`, `nan`: `baeae321…`). `0.2778` remains **CLAIM** (no receipt in `ledger/`).
- **Best receipt**: none recorded (`ledger/submissions.csv` has 25 `BUILT` rows and zero `RECEIPT` rows).
- **TOP_PUBLIC**: `____` (not supplied; human must fill value and observation date from leaderboard https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ — external top is 0.4413 as of 2026-10-24, but human must confirm).
- **Slots left this week**: `__` / total left to 2026-12-03: `__` (human must confirm entity rolling-week quota = 3/week).
- **AXIS this session**: `DILATATION`, chosen after ranking 5 candidate hypotheses (see `docs/HYPOTHESES.md`). New values: `p10dilatation`, `p12dilatation`, `p15dilatation` — shifting 10%, 12%, 15% of dots from low/mid dilatation (≤7.24 nstrain/yr) into high-dilatation tercile (≥7.24 nstrain/yr) on H19-5 ridge support via greedy exact-marginal-DTI; exact 37,654 dots held; `d_cat > 2.0 px`; zero catalogue mass; all gates PASS.
- **OK TO DOWNLOAD AND SUBMIT**: `docs/downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-zeros.tif` (210 KB, SHA `25ba17a2…`, 210 KB) — **all-finite, values in [0,1], 0 NaN inside, 10/10 gates PASS on independent reread**. See banner on [GitHub Pages](docs/index.html) and [Executive summary & how to submit](docs/SUBMIT.html).
- **Next 3 candidate slots (BUILT, not submitted)**:
  1. `h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b` — 12.0% shift (4,518 dots) low→high dilatation tercile (`MODEL:+0.007` `[-0.003,+0.019]`; HOLDOUT-DTI `+0.00177` `[0.00111,0.00246]` vs R0, gems57-pooled-hide-v2, n=22663).
  2. `h33-h33-2-b2-DILATATIONp10dilatation-20261025-2e501f88` — 10.0% shift (3,765) (`MODEL:+0.005` `[-0.004,+0.016]`; HOLDOUT `+0.00174`).
  3. `h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432` (`MODEL:+0.006`; HOLDOUT `+0.00181`) — or fallback to `h33-h33-2-b2-RELIEFp12piedmont-20261024-a0998ed7` (`MODEL:+0.008`; HOLDOUT `+0.00197`) if DILATATION needs orthogonal validation.
  - Prior session RELIEF p10/p12/p15, SNAP scarp pot, and CONCENTRATION phys10 remain built but DILATATION is orthogonal (geodetic strain vs topography vs edge-snap) and is now the primary. CONCENTRATION’s physics prior and RELIEF remain reserve if DILATATION falsifies.
- **Leakage canary**: Band 8 dilatation symmetric AUC 0.514, max across 5 tested bands 0.515 << 0.90 — `REPORT_ONLY_PASS`.
- **Run card**: p12 HOLDOUT-DTI 0.005779 [0.004863,0.006851] vs R0 0.004006 [0.003424,0.004690], Δ+0.00177 [0.00111,0.00246]; correlation vs R0 0.8997 (<0.90 PASS); validator 10/10 PASS; SHA `8b4d248b…` / `25ba17a2…`; verdict `promote`.

No file was submitted by an agent. Candidate GeoTIFF pairs exist in `releases/` (gitignored) and `docs/downloads/` (GitHub Pages, tracked via `!docs/downloads/*.tif` exception). Regenerate anytime via `python scripts/build_dilatation_variants.py`. See `docs/SUBMIT.md`, `docs/SUBMIT.html`, `docs/index.html`, `SLOT_PLAN.md`.

## Verified facts
- Metric: DTI with alpha 0.2, beta 0.8, triangular kernel R=300m (3px), float32 EPSG:32611 100m, per https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Organizer answers: known faults masked pixel-exactly, new truth can lie within 300m of known traces — https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
- Structure: public leaderboard only some chunks, Phase1 $50k private chunks, Phase2 $250k rescores with expert-expanded labels — rules https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Resolution: GeoDAWN Area 2 flown at 400m line spacing, 150-200m above terrain — https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7 (DOI 10.5066/P93LGLVQ)
- Geodetic dilatation controls geothermal permeability in Great Basin step-overs (32% of systems) — https://www.osti.gov/servlets/purl/1110517 and https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2025/Giddens.pdf

## What we built this session (DILATATION, 2026-10-25)
- Ranked 5 candidate hypotheses (DILATATION, concealed basin-edge, seismicity, conductivity-alteration, radiometric K/Th) by expected HOLDOUT gain per cost; DILATATION ranked #1 (expected MODEL +0.005 to +0.008, cost LOW, no new external data, leakage PASS).
- Built 3 DILATATION dose-response variants differing ONLY in frac (10%, 12%, 15%): drop lowest-dilatation parent dots, regrow via greedy exact expected-DTI on high-dilatation tercile (≥7.24 nstrain/yr) on H19-5, d_cat>2.0, count 37,654 held.
- Validated on spatially-blocked holdout (gems57-pooled-hide-v2, whole-component buffered, 8 folds, 22,663 withheld positives, 157 clusters, 1,000 paired bootstrap): p12 Δ+0.00177 [0.00111,0.00246] vs R0 — CI excludes 0; leakage canary max AUC 0.515 (<0.90 PASS); SGMC control drop −0.012 to −0.016 as expected for this geography.
- Copied primary to `docs/downloads/` with zip twin, wrote audit.json, updated ledger/submissions.csv (25 rows), evidence/dilatation_variants.json, evidence/dilatation_proxy_audit.json, docs/index.html (executive summary + download banner), docs/SUBMIT.html, docs/SUBMIT.md, SLOT_PLAN.md.
- All files pass 10/10 format gates on independent reread (values_in_0_1, no_nan_inside, catalogue_zero_mass, etc.); validator output in audit.json.

## Files
- `releases/` — all candidate rasters (NaN primary, zeros fallback) — gitignored, reproducible
- `docs/downloads/` — GitHub Pages served primaries (tracked, .tif exception) + audit.json
- `gems/` — tested toolkit: metric algebra, axis builders, gates, proxy, ledger, CLI
- `tests/` — 97 tests pass with no competition data (`make test`)
- `scripts/build_dilatation_variants.py` — this session’s build, deterministic, SHA-verified inputs
- `scripts/report_dilatation_proxies.py` — pooled holdout + canaries + SGMC
- `registry/parents/R0.json` — verified parent record
- `ledger/submissions.csv` — build log (25 BUILT, 0 RECEIPT)
- `docs/HYPOTHESES.md` — 5 ranked hypotheses with layers, signatures, why they beat catalogue, mimics, cost
- `docs/index.html` — GitHub Pages site with obvious download, portal-fix explanation, run card, sources
- `docs/SUBMIT.html` — executive summary subpage: 3-step submission guide
- `SLOT_PLAN.md` — next slots and weeks to deadline
- `registry/session_manifest.json` — pinned inputs with sha256

## Evidence labels
- RECEIPT = copied from submission-page receipt
- CLAIM = owner-reported, no receipt
- PROXY = local holdout (gems57-pooled-hide-v2)
- MODEL = projection
Never call PROXY or MODEL a score.

## IRREGULARITIES
See IRREGULARITIES.md — only items that change a decision.

## AI disclosure
See AI_USE.md
