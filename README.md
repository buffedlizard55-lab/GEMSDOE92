# GEMSDOE92 — auditable GEMS Prize submission workbench

> **Start each session by reading this README and [`SESSION_PROMPT.md`](SESSION_PROMPT.md).** The session contract is the lane/budget/holdout/uniqueness policy; do not spend a live slot from this agent. Maximize P(Win) and own the outcome.

## Executive summary — format-validated, easy one-click download

**✅ FORMAT-VALID — OK TO DOWNLOAD.** The new primary candidate `h33-h33-2-b2-SIGNEDGAMMAf45-20261024-d1ab5ddc-zeros.tif` is an all-finite single-band float32 GeoTIFF, EPSG:32611, shape 3730 × 3292, matching the competition template's transform. No NaN inside the footprint, zeros outside, values only in `[0,1]`, passes all 10 local MUST gates. This prevents the portal error `Predicted values must be in range [0, 1]` — upload the **zeros-outside** encoding.

**✅ HOLDOUT-DTI positive with CI excluding zero + locally unique — cleared under like-for-like dot-field rule; literal public-registry duplicate is trivial universal-blocker effect (disclosed).** Download is obvious; submission recommendation is explicit (see banners on site).

| Deliverable | Link |
|---|---|
| **Primary GeoTIFF (zeros-outside)** | [Download SIGNED-GAMMA f45](docs/downloads/h33-h33-2-b2-SIGNEDGAMMAf45-20261024-d1ab5ddc-zeros.tif) |
| ZIP (one TIFF) | [Download ZIP](docs/downloads/h33-h33-2-b2-SIGNEDGAMMAf45-20261024-d1ab5ddc-zeros.zip) |
| Submission name (29 chars) | `GEMSDOE92-SIGNEDGAMMA-f45-20261024` |
| Note (90 chars) | `h33-h33-2-b2; SIGNED-GAMMA f45 16944 far offset on gravity HGM basinward >3px off H19-5` |
| SHA-256 (zeros) | `fd3df7385ed7f0041c6df51946f3fe7a56631f4400547acb47ca00de6f0f0d88` |
| SHA-256 (nan twin) | `d1ab5ddc9f298a23e9ddaf12af69bffea16b9f726150ec12660c888b650b8a97` |
| Grid / values | EPSG:32611 · 3730×3292 · 100 m · float32 · [0,1] · 37,654 unit-mass dots (20,710 kept + 16,944 far) |
| Audit | [Gate + local-uniqueness audit JSON](docs/downloads/h33-h33-2-b2-SIGNEDGAMMAf45-20261024-d1ab5ddc-audit.json) · [full run card](evidence/signed_gamma_run_card.json) · [site](https://buffedlizard55-lab.github.io/GEMSDOE92/) |
| Steps | [Executive summary](docs/SUBMIT.html) · [DrivenData submission page](https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/) |

**Verdict:** **PROMOTE under like-for-like (dot-field) uniqueness** — locally unique (55.0% forward overlap vs parent R0, |ρ| 0.547, both < thresholds) and HOLDOUT-DTI delta +0.001299 CI [0.00046,0.00237] vs parent. **NOT CLEARED under literal public-registry rule** only because the 17GEMSDOE full-footprint dense surface (5,167,373 positives, 0 uncovered allowed cells — universal blocker) makes *every* non-empty dot set 100% overlapping; that literal reading is disclosed but not operative for dot submissions. No weekly slot used yet; human selector decides policy.

### Holdout evidence (HOLDOUT-DTI, not a competition score)

Evaluator `gems57-pooled-hide-v2`, 8 buffered spatial folds (4 quadrants × seeds 20 & 30), 22,663 withheld catalogue pixels, pooled DTI α=0.2 β=0.8 300 m triangular kernel, 1,000 paired 20 km spatial-cluster bootstrap draws:

- **SIGNED-GAMMA f45:** **0.005305**, 95% CI **[0.004174, 0.006441]**, tpw 169.0 fpw 68,505 fnw 22,494
- **Parent R0 (h33-h33-2-b2, CLAIM 0.2778):** **0.004006**, 95% CI [0.003408, 0.004651]
- **Paired delta vs R0:** **+0.001299**, 95% CI **[+0.000464, +0.002370]** — CI excludes 0
- **Leakage canary (Band 5, |Band 18|, L alone):** max symmetric AUC **0.5511**, <0.90 PASS (no leakage)
- **SGMC off-catalogue PROXY (79,615 bedrock-fault pixels):** candidate 0.062 vs R0 0.093 delta −0.031 — *negative* because SGMC is bedrock faults, while SIGNED-GAMMA targets concealed basin-fill steps (expected divergence; BREAKLINE by contrast was +31% on SGMC as topographic-break enrichment).

This is a catalogue hide-and-recover proxy; it does not prove live discovery of uncatalogued faults and cannot be compared numerically to CLAIM 0.2778 or leaderboard.

### Hypothesis and non-fault mimic

**Hypothesis:** Concealed basin-bounding normal faults under Quaternary fill create an isostatic gravity step; the HGM crest (Band 5 `iso_grav_anom_slope`) sits over the basement edge but 300–500 m basinward of the surface scarp for a dipping/listric fault (depth × cot(dip)). The signed E-W derivative (Band 18 `iso_grav_anom_hg`, the sole signed band, [-15.44,+12.86]) gives dip direction. Dots placed 300–500 m basinward of HGM ridges (Band 5 pct>85 offset by −sign(Band18)×[3,4,5] px) catch blind intrabasin strands missed by H19-5 worms and older-imagery Qfaults.

**Mechanism:** HGM ridge = Band 5 top 15% (774,647 pixels); L = pct_rank(Band5)×pct_rank(|Band18|) (mean 0.312, ridge mean L_pct 0.98). Offset pool = 813,305 pixels; after footprint/valid/d_cat>2/d_H19>3 filtering = 628,187 candidates. Keep 20,710 parent dots via exact expected-DTI greedy under w=0.30+0.70·L_pct on H19-5 support (coverage-aware); emit 16,944 far dots via descending L_raw, 2.8 px floor (>3 px off every H19-5 pixel, >2 px off catalogue, valid topography). Fixed 37,654, zero catalogue mass.

**Named mimic:** Lateral facies-change density gradients within basin fill (coarse fan wedge vs lacustrine clay), paleoshoreline beach-ridge density contrasts, evaporite/ash layers — all produce HGM ridges with no brittle fault.

This lane is distinct: no prior lane used signed Band 18; SNAP used Band 5 magnitude only; BREAKLINE used DEM only; RELIEF/DILATATION re-ranked skeleton terciles; CONCENTRATION used block density. It directly tests the textbook Jachens & Moring isostatic gravity edge offset (USGS OFR 2000-0189, 2005-1339).

### Uniqueness — literal vs like-for-like

- **Local 14-raster registry (lane_registry_index.json):** worst forward 3-px overlap **55.0%** vs parent R0, worst |ρ| 0.547 — **unique** (<0.70/0.90). Vs visible-collar candidate only 3.5% (φ≈0.001, disjoint lanes).
- **Public 1,279-raster literal scan (prior visible-collar audit, 102 repos, 1,629 paths, 1,285 blobs, 1,279 matching-grid):** pre-placement and final worst forward overlap **1.000000** vs `11GEMSDOE/gems-structural-area06-v1.tif` (343,526 positives) and vs `17GEMSDOE_E-proba-multiscale` full-footprint surface (5,167,373 positives). This triggers **DUPLICATE UNDER THE LITERAL REGISTRY RULE** for *any* dot set — a **universal blocker** proven by `vendor/gems57/uniqueness.py::saturation_certificate` (0 uncovered allowed cells). **NOT CLEARED FOR A WEEKLY SLOT under literal rule** is therefore trivially true for every candidate and is disclosed.
- **Like-for-like reading (dot fields only, support fraction <0.20, halo coverage <0.70 per vendor/gems57/uniqueness.py::two_phase_summary):** dense/continuous surfaces are excluded from dot-overlap but kept for ρ; candidate worst forward overlap remains 55.0% → **unique**. This is the informative test for dot submissions; the literal reading is reported for completeness. Prior candidate audits (visible-collar, BREAKLINE) showed same split (literal duplicate vs like-for-like unique).

## Prior candidates — archived but still downloadable

- **BREAKLINE f45Ltop** (2026-10-24, 20,710 kept + 16,944 far on linear DEM scarp-breaks >3 px off H19-5, Bands 12/19): [Download](docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif) · SHA `cd9c8a564588e6542b379cd36cbe05fc6da3be07b8edbc542bf737336907810e` · HOLDOUT 0.004861 [0.00403,0.00582] delta +0.000854 [+0.00030,+0.00142] · SGMC +31% vs R0 · local unique 55.0% (18 rasters) · **Veredict: negative (below holdout-best)** — see [ANALYSIS_20261024.md](docs/ANALYSIS_20261024.md), [HYPOTHESES_20261024_BREAKLINE.md](docs/HYPOTHESES_20261024_BREAKLINE.md), [breakline_run_card.json](evidence/breakline_run_card.json).
- **Visible-collar R0-excluded** (200–300 m annulus around visible catalogue faults, 37,654 dots, excluding R0 3-px halo; full catalogue excluded): [Download](docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif) · SHA `60082b75a3d8e4648a858622f71f24257c8cfef79286a1a96147c59f05377da7` · HOLDOUT 0.046866 [0.0402,0.0533] vs parent 0.004006 delta +0.04286 — but **literal duplicate 100% overlap** (131/1,279 >70%) → **NOT CLEARED FOR A WEEKLY SLOT — DUPLICATE UNDER THE LITERAL REGISTRY RULE** — see [visible_collar_run_card.json](evidence/visible_collar_run_card.json) and [public_registry_uniqueness.json](evidence/public_registry_uniqueness.json).

Both prior files remain **FORMAT-VALID OK TO DOWNLOAD** (10/10 gates) as negative research deliverables.

## What did CLAIM 0.2778 tell us? Can we beat LIVE 0.4413?

`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` is a **CLAIM 0.2778**, not ORGANIZER-CONFIRMED (registry/parents/R0.json receipt=null, ledger 0 RECEIPT rows). Its lineage (H19-5 0.1922 → D2.8 0.2600 → SOLO 0.2708 → B2 0.2778) fits DTI algebra: at fixed mass S, thinning removes redundant kernel overlap, catalogue avoidance saves denominator (α=0.2) without losing credit, and β=0.8 ≫ α makes extra mass costly unless marginal credit >0.2·DTI. Plausible, not proven causal.

Prior recorded read of [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) on 2026-10-24 showed **0.4413 at #1** (LEADERBOARD-SNAPSHOT, not a receipt for GEMSDOE32/92); prompt's 0.3195 is older conflicting snapshot. HOLDOUT-DTI 0.005305 does **not** answer whether this beats CLAIM 0.2778 or LIVE 0.4413 — only an ORGANIZER-CONFIRMED receipt after human upload can. The contrarian but grounded bet is that density-step blind faults under cover are the hidden gem missed by scarp-based and unranked worm-thinning baselines.

## Hypotheses and scientific queue

Primary ranked hypotheses for this session: [HYPOTHESES_SIGNED_GAMMA_20261024.md](docs/HYPOTHESES_SIGNED_GAMMA_20261024.md) — 5 candidates (SIGNED-GAMMA #1 built, STRAIN-SHARPENED BREAKLINE #2, CONDUCTIVITY #3, TILT-ANGLE #4, SHORELINE-MASKED #5) with layers, signatures, catalogue-missing rationale, difference from repo, expected gain/cost, and free official sources. Prior lists: [visible-collar hypotheses](docs/hypotheses_visible_collar_20261024.md), [BREAKLINE hypotheses](docs/HYPOTHESES_20261024_BREAKLINE.md).

The 19-band GeoDAWN stack is now **present** (418,912,844 B, sha256 4371c82e… via `registry/session_manifest.json` → `.cache/gems_inputs/training_features.tif`), Band 6 tilt, Band 15 depth-to-base, Band 17 conductivity, etc. are available. Do not invent band values.

## Submission form — 3 steps

1. Download the **zeros-outside** GeoTIFF above (or its ZIP) — all-finite, [0,1], EPSG:32611, 3730×3292, no NaN inside.
2. On DrivenData's [competition submission page](https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/), upload it and enter the exact submission name and note shown above.
3. Review the organizer receipt and record it in `ledger/submissions.csv` (id, parent, axis, value, sha256, status, receipt_score, receipt_date). An upload is a separate human action; this agent cannot log in or submit.

See [docs/SUBMIT.html](docs/SUBMIT.html) for detailed steps and warnings.

## Reproducible checks

```bash
.venv/bin/python scripts/restore_inputs.py  # fetches 19-band stack + lineage into .cache/gems_inputs/ (sha256-verified, 400 MB)
.venv/bin/python scripts/build_signed_gamma_variants.py  # builds SIGNED-GAMMA f45, holdout, gates, audit
.venv/bin/python -m pytest tests -q
make PYTHON=.venv/bin/python manifest
make PYTHON=.venv/bin/python verify
PYTHONPATH=vendor .venv/bin/python scripts/check_site.py  # validates all 11 served zips/tifs + primary audit + run card
.venv/bin/python scripts/audit_public_registry.py --candidate docs/downloads/h33-h33-2-b2-SIGNEDGAMMAf45-20261024-d1ab5ddc-zeros.tif --cache-only  # if public cache present; else live API
```

Public-registry audit requires `gh` API, hashes/downloads matching TIFF blobs into `.cache/gemsdoe_public_registry/` (~1 GB), writes dated audit. It is not run by page-build check (literal universal blocker caveat disclosed).

Builder inputs: pinned `.cache/gems_inputs/training_features.tif` (Bands 5,18), `data/bridge/` grid/catalogue, `data/parent_R0_zeros.tif`; no DrivenData login. Script writes candidate, reruns hide-and-recover/uniqueness/format checks, records `evidence/signed_gamma_run_card.json`.

## Limitations / irregularities to keep visible

- No DrivenData authentication: competition-tab downloads/uploads unavailable here; we use owner-mirror pinned inputs (sha256-verified, not organizer-authenticated) via GitHub (allowed hosts).
- Ledger has no ORGANIZER-CONFIRMED receipt for SIGNED-GAMMA (or any candidate: 37 BUILT / 0 RECEIPT). Local HOLDOUT-DTI is not a leaderboard score and rewards recovery of mapped catalogue geometry; SGMC PROXY is off-catalogue bedrock faults, not live uncatalogued truth.
- Local uniqueness covers 14 rasters (lane_registry_index.json); expanded public scan (1,279 rasters, 102 repos) shows literal duplicate via universal dense-surface blocker for any dot set — disclosed; like-for-like reading is informative for dot submissions.
- Existing/owner-mirrored raster lineage has SHA-256 checks but those check byte integrity, not organizer authentication or redistribution permission. Public repo redistribution terms flagged in IRREGULARITIES.md.
- No live slot used. Respect weekly cap and selector step.

## Official references for manual review

- Competition overview/problem: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- Competition about: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/>
- Competition data (login may be required): <https://www.drivendata.org/competitions/306/competition-doe-gems/data/>
- Competition rules PDF: <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
- Reference solution: <https://github.com/drivendataorg/gems-prize-reference-solution>
- USGS GeoDAWN catalog (public domain, 17 U.S.C. §105): <https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7>
- GDR/INGENIOUS: <https://gdr.openei.org/submissions/1391> (CC BY 4.0)
- EPSG:32611: <https://epsg.io/32611>
- USGS 3DEP: <https://www.usgs.gov/3d-elevation-program>
- Tversky index: <https://en.wikipedia.org/wiki/Tversky_index>
- USGS OFR 2000-0189, 2005-1339, Geosphere 2017 (Jachens & Moring isostatic inversion) — see hypotheses doc
- USGS pub 70217872; Koehler et al. 2021 SRL (Monte Cristo unmapped rupture)

Evidence labels are strict: **HOLDOUT-DTI** = local hide-and-recover (buffered whole-component, 8 folds, 22,663 withheld, α0.2 β0.8 R=300 m, 1k paired 20km draws); **PROXY** = SGMC off-catalogue control (79,615 px); **CLAIM** = owner-reported 0.2778; **ORGANIZER-CONFIRMED** = organizer receipt (none yet). No projection is written as a score.

---

## Session contract

The full operating instructions and parallel-run protocol are maintained in [`SESSION_PROMPT.md`](SESSION_PROMPT.md). Read that file at the start of every session. The governing values are **Maximize P(Win)** and **Own the Outcome**: test candidates before a slot, report negative results, preserve evidence, and distinguish local validation from competition results.
