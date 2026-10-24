# GEMSDOE92 — GEMS Prize candidate research and TIFF preflight

> **Read this file at the start of every session.** Full operator contract: [`SESSION_PROMPT.md`](SESSION_PROMPT.md).

**Primary diagnostic download:** `DILATATION p12` — **local preflight PASS and OK TO DOWNLOAD FOR REVIEW**, but **NOT CLEARED / NOT RECOMMENDED for competition submission**. It breaches the uniqueness stop (99.37% of dots within 3 px of R0). Separately, its all-zero outside-footprint encoding conflicts with the official problem page's stated null/NaN outside-bounds requirement; no organizer receipt confirms acceptance. This is a diagnostic artifact, not a submission recommendation.

| | |
|---|---|
| **File** | [`docs/downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-zeros.tif`](docs/downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-zeros.tif) |
| **Zip** | [`…-8b4d248b.zip`](docs/downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b.zip) |
| **Submission name** | `GEMSDOE92-DILATATION-p12-20261025` |
| **Form note (103 chars)** | `HOLDOUT-DTI 0.005779 [0.004863,0.006851], gems57-pooled-hide-v2, n=22663; DILATATION p12 duplicate-stop` |
| **SHA-256** | `25ba17a26d31df9d574fba2a2f34d03ff58f587f4ffde092dcc4bba9822f8898` |
| **Submission guide** | [`docs/SUBMIT.html`](docs/SUBMIT.html) — distinguishes local range preflight, official format uncertainty, and slot clearance |
| **Research/candidate review** | [`docs/RESEARCH_AND_CANDIDATE_REVIEW_20261024.md`](docs/RESEARCH_AND_CANDIDATE_REVIEW_20261024.md) — five hypotheses, source boundaries, and why no new candidate was built |
| **Site** | <https://buffedlizard55-lab.github.io/GEMSDOE92/> |

| Status | Meaning |
|---|---|
| **✅ LOCAL PREFLIGHT PASS — OK TO DOWNLOAD FOR REVIEW** | All 10 project format/range gates pass on an independent reread of the served bytes. However, the official problem page says cells outside the submission bounds should be null/NaN; this zeros-outside encoding has no organizer acceptance receipt. It is not certified as submission-format compliant. |
| **⛔ NOT CLEARED FOR SUBMISSION** | The 99.37% within-3-px overlap exceeds the 70% uniqueness stop. The zeros-outside file also differs from the official page's null/NaN outside-bounds specification. Do not upload it. |
| **HOLDOUT-DTI above R0** | `gems57-pooled-hide-v2`, 22,663 withheld positives: paired Δ **+0.00177**, 95% CI **[+0.00111, +0.00246]**. This is a local instrument, **not** a leaderboard score. No weekly slot was spent. |

```bash
.venv/bin/python -m pytest tests -q                         # 111 passed in this review
PATH="$PWD/.venv/bin:$PATH" make manifest && PATH="$PWD/.venv/bin:$PATH" make verify
.venv/bin/python scripts/check_site.py                     # format pass + explicit promotion block
```

## This session's lane: DILATATION (geodetic volumetric strain)

- **Hypothesis.** Band 8 `geod_dilaterate` is a *kinematic* field. The catalogue maps Quaternary **scarps**; strain maps where they are currently **opening**. Faulds et al. put ~32 % of Great Basin geothermal systems in dilatational step-overs / relay ramps and ~25 % at terminations and intersections. A blind fault under 10–100 m of fan alluvium has **no scarp to map but still dilates**.
- **Mechanism.** Count held at 37,654. Move 12 % (4,518) of the lowest-dilatation parent dots into the high tercile (≥ 7.24 nstrain/yr) on H19-5, placed by greedy exact expected-DTI (α 0.2, β 0.8, R 300 m) under `0.70·dilatation + 0.30·TMI/grav/scarp`. Zero catalogue mass; `d_cat > 2.0 px`.
- **Non-fault mimic.** Brine-pumping / agricultural subsidence bowls, Walker Lane strain shadows, ductile thick-fill stretching without brittle faulting.
- **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 8 folds, 22,663 withheld positives, 157 spatial clusters, 1,000 paired draws: R0 `0.004006 [0.003424, 0.004690]` → p12 `0.005779 [0.004863, 0.006851]`, Δ **+0.00177 [0.00111, 0.00246]**.
- **Leakage canary** (each band tested alone before any result was trusted): Band 8 `0.5145`, 7 `0.5128`, 4 `0.5102`, 15 `0.5149`, 17 `0.5060` — max **0.5149 ≪ 0.90**.
- **Verdict:** **NOT CLEARED** — dose response is monotone (p10 +0.00174, p12 +0.00177, p15 +0.00181) but all three measure 99.37–99.40 % within 3 px of registry raster R0, over the brief's 70 % limit. Logged as duplicates under the operator's rule.

Rebuild: `python scripts/build_dilatation_variants.py` · proxies: `python scripts/report_dilatation_proxies.py`

## ⚠ No served file is both unique and expected to improve

Measured this session, and it is the finding that should drive the next one. **Under the operator's literal rule this repository has nothing submittable.**

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

**Which reading governs.** Reading 2 is the better science, but it is *this repository reinterpreting an operator gate in its own favour* — exactly the move that lets a non-compliant file look compliant. So **the literal rule governs**: every positive-holdout arm above is logged as a duplicate of R0, and no slot is recommended. An upload is a recorded human override, not an agent recommendation. This supersedes an earlier revision of this README that carried `Verdict: promote` for DILATATION p12; see `IRREGULARITIES.md` 2026-10-25.

**The tension this exposes.** TIPGAP clears the whole-file gate (67.00 %) *only because* it moves 33 % of the budget far off the D2.8 skeleton — and that is precisely the change that drove its HOLDOUT-DTI **below** R0 (−0.001283, verdict negative). Uniqueness and expected gain currently pull in opposite directions. Resolving that, not building another variant, is the next session's job — see [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md).

## Why the reported h33-h33-2-b2 CLAIM 0.2778 cannot yet be explained

`registry/parents/R0.json` records 0.2778 as `CLAIM_score` and has `receipt: null`; the local ledger contains no organizer receipt for it. The public snapshots in the prompt also conflict (0.3195 versus 0.4413). These are not verified leaderboard results in this checkout.

The checked-in lineage associates the parent with H19-5 support, Poisson-style thinning, and catalogue exclusion. Those are plausible contributors under the official distance-weighted Tversky metric, which gives partial credit for predictions near hidden fault pixels and uses α=0.2 / β=0.8. But no controlled experiment isolates those factors, so claiming they caused a specific live score would be speculation. A higher live score is unknown until a distinct candidate receives an organizer score receipt. See [`docs/RESEARCH_AND_CANDIDATE_REVIEW_20261024.md`](docs/RESEARCH_AND_CANDIDATE_REVIEW_20261024.md) for the five-hypothesis review and blockers.

## Lanes built here

| lane | HOLDOUT-DTI (`gems57-pooled-hide-v2`; 22,663 withheld positives; 95% CI) | verdict | download |
|---|---|---|---|
| **DILATATION p12** | 0.005779 [0.004863, 0.006851] | **negative: DUPLICATE-STOP** (99.37% within 3 px of R0) | [zeros-outside diagnostic](docs/downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-zeros.tif) |
| DILATATION p10 | 0.005747 [0.004867, 0.006788] | negative: duplicate R0 | [zeros-outside diagnostic](docs/downloads/h33-h33-2-b2-DILATATIONp10dilatation-20261025-2e501f88-zeros.tif) |
| DILATATION p15 | 0.005818 [0.004838, 0.006912] | negative: duplicate R0 | [zeros-outside diagnostic](docs/downloads/h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432-zeros.tif) |
| TIPGAP far18f33 (33 % moved 6–18 px past H19-5 tips, off-skeleton) | 0.002723 [0.002324, 0.003131] | **negative**; R0 overlap check is local only | [zeros-outside diagnostic](docs/downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.tif) |
| RELIEF p10 (piedmont elevation tercile) | 0.006045 [0.005187, 0.006927] | negative: duplicate R0 | [zeros-outside diagnostic](docs/downloads/h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24-zeros.tif) |

The TIPGAP file is kept because a negative result is a deliverable — it falsifies "continuations sit 0.5–1.8 km past the tips" on this instrument. **Do not spend a slot on it expecting a gain.** The three on-skeleton 10–15 % TIPGAP doses were logged as lane-duplicates of R0 (arrival overlap ≈ 0.999) and are not offered.

## Shared tools fixed this session (not forked)

Running the repo's own gates instead of trusting them exposed two defects and one wrong number — all in `IRREGULARITIES.md` with before/after measurements:

1. **Pinned paths were joined onto the data root twice.** The registries record different conventions, so repo-relative `data/parent_R0_nan.tif` became `data/data/…`. `make manifest` reported **8 of 8** inputs `MISSING` while every file was on disk and correctly hashed. → one `gems.rasters.resolve_pinned_path()` used by both call sites. **After: `RESULT: OK`, 8/8.**
2. **`registry/parents/R0.json` is `mode: pinned_artefact`, which the loader could not read**, so `make verify` — "the gate that stops a session before it burns slots on descendants of an unverified parent" — raised on *every* run. → the loader validates that form, and `verify_pinned_artefact()` checks sha256 **and** byte length per encoding, then **re-measures** dot count, total mass, min catalogue distance, footprint and the 3/4/5 px collar counts from the raster itself and diffs them against the record. **After: exit 0, zero drift on all seven invariants.**
3. **That new check immediately caught a wrong number:** `R0.json` claimed 355,000 B for the NaN artefact; disk and `session_manifest.json` both say **355,443 B**. The sha256 — the real authority — was correct in both, so no artefact was ever mis-identified.

CI ran the parent gate as `… || true`, which is why a gate that had never passed produced no signal. It is fatal now, plus `make manifest`, plus a gate on **every** `docs/downloads/*-zeros.tif`, plus an assertion that the primary named in `index.html` matches its local format-audit JSON byte-for-byte.


## Additional session deliverable (STEPOVER, negative)

A separate STEPOVER lane was also built and kept as a negative deliverable; it does **not** replace the TIPGAP FAR download above.

- **File:** [`releases/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f.tif`](releases/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f.tif) (all-finite zeros encoding, SHA-256 `e5fee27f162371d959315d1dc412e137df0348b6009fa3dfdc46dc1363bd4205`)
- **Status:** local preflight / OK TO DOWNLOAD FOR REVIEW; outside-mask official-format acceptance unresolved; **NOT a weekly slot** (verdict negative).
- **Lane:** 5,000 unit-mass dots at visible catalogue trace-tip step-overs, 3–10 px off catalogue (`d_cat > 3 px`), 1 px spacing. Distinct from TIPGAP (H19-5 skeleton endpoints) and from MASS/PRUNE/SNAP/CONCENTRATION/RELIEF.
- **HOLDOUT-DTI:** 0.0000 [0.0000, 0.0000] vs R0 0.00370 [0.00301, 0.00432] (`gems57-pooled-hide-v2`, 11,321 withheld positives). This is a structural zero for gate-compliant off-catalogue dots; see `IRREGULARITIES.md`.
- **Uniqueness / canary:** worst Spearman ρ = 0.0277, worst 3-px forward overlap = 0.2534 vs 14 locally accessible registry rasters; leakage AUC = 0.4996.
- **Details:** [`docs/executive-summary.html`](docs/executive-summary.html) · [`docs/ANALYSIS.md`](docs/ANALYSIS.md) · [`evidence/run_card.json`](evidence/run_card.json)

## Limitations (what this sandbox cannot do)

- No DrivenData auth → the official data page redirects to login, so this sandbox cannot download the competition stack or upload a submission. The data-page redirect was directly observed during this review.
- Some historical inputs are from owner mirrors with pinned SHA-256; a hash verifies bytes, not organizer provenance, permissions, or acceptance.
- Cannot fill `TOP_PUBLIC` from the live leaderboard.
- Weekly slot promotion is human-only (3/week + one blind final).
- The holdout's truth is the **visible catalogue**, so it cannot reward a genuinely new fault. It ranks emission rules; live receipts remain the decision anchor.

## Verified facts

- Official problem page: DTI α = 0.2, β = 0.8, triangular R = 300 m; single-band float32 EPSG:32611 at 100 m, same bounds, with null/NaN outside bounds — https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ (retrieved during this review). The current zeros-outside file does not match the stated outside-bounds convention.
- Known faults masked pixel-exactly — https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
- Rules — https://docs.nlr.gov/docs/fy26osti/96647.pdf
- GeoDAWN (400 m line spacing, 150–200 m AGL) — https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7 · https://doi.org/10.5066/P93LGLVQ
- Dilatational step-overs host ~32 % of Great Basin geothermal systems — https://www.osti.gov/servlets/purl/1110517 · https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2025/Giddens.pdf

## Evidence labels

RECEIPT = submission-page receipt · CLAIM = owner-reported · HOLDOUT-DTI = hide-and-recover · PROXY = other local instrument · MODEL = projection. Never write a projection as a score.

---

## Session prompt (read first every session)

The complete operator contract and this session's scope are stored in [`SESSION_PROMPT.md`](SESSION_PROMPT.md). Read it together with this README at the start of each session. In every session:

1. Stay in one named geological lane. Compare the raster surface before placement and final dots with the registry; stop on Spearman > 0.90 or >70% within 3 px of any registry raster.
2. Reuse `vendor/gems57/evaluate_holdout.py` and `vendor/gems57/submission_writer.py`. Holdout = withhold whole fault segments with a buffer; catalogue features from visible faults only; mask visible faults pixel-exactly; pooled DTI α = 0.2 β = 0.8, 300 m triangular kernel.
3. Label every score HOLDOUT-DTI (evaluator version, n withheld, 95% CI) or ORGANIZER-CONFIRMED receipt. A projection or model target is never a score.
4. Leakage canary: test each feature alone; AUC > 0.90 means leakage until proven otherwise.
5. End with a JSON run card: hypothesis; mechanism; named non-fault mimic; holdout DTI+CI; correlation/overlap; raster SHA-256; validator; submission name + ≤140-character note; verdict promote/negative.
6. Stop after 3 experiments or 2 hours. Do not pick live slots.
7. Keep download validity separate from slot clearance. Validate files in code; prominently say whether they are format-valid and whether they are recommended for submission.
8. Maximize P(Win) and own the outcome: a negative result is a deliverable; never copy a prior TIFF as a new submission.
