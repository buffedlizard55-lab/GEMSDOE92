# GEMSDOE92 — auditable GEMS Prize submission workbench

> **Start each session by reading this README and [`SESSION_PROMPT.md`](SESSION_PROMPT.md).** The session contract is the lane/budget/holdout/uniqueness policy; do not spend a live slot from this agent. Maximize P(Win) and own the outcome.

## Executive summary — unique ANASIG candidate, format-valid, not cleared for a slot

**✅ FORMAT-VALID — OK TO DOWNLOAD.** The new primary candidate is an all-finite single-band float32 GeoTIFF, EPSG:32611, shape 3730 × 3292, matching the competition template's transform. It has no NaN inside the footprint, zeros outside, values only in `[0,1]`, and passes all 10 local MUST gates. This prevents the portal error `Predicted values must be in range [0, 1]`.

**⛔ NOT CLEARED FOR A WEEKLY SLOT — do not submit it as a competition entry.** (1) Its HOLDOUT-DTI beats parent R0 but not the current holdout best (RELIEF p10). (2) Under the literal public-registry rule, the binding witness 17GEMSDOE `E-proba-multiscale` is positive on 100% of the footprint, giving 100% forward overlap for these exact bytes (single-witness receipt in `evidence/public_witness_anasig.json`; not waived). Against the **local dot registry** (24 rasters) the file **is unique**: worst forward 3-px overlap 0.550, worst |ρ| 0.547, pre-placement surface worst |ρ| 0.024. No slot was used and no upload was performed.

| Deliverable | Link |
|---|---|
| **GeoTIFF (primary)** | [Download ANASIG zeros-outside submission](docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif) |
| ZIP (one TIFF) | [Download ZIP](docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.zip) |
| Submission name | `GEMSDOE92-ANASIG-f45Atop-20261024` |
| Note (84 chars) | `h33-h33-2-b2; ANASIG f45Atop 16944 far dots on analytic-signal ridges >3px off H19-5` |
| SHA-256 | `68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5` |
| Submission steps | [Executive summary](docs/SUBMIT.html) · [site](https://buffedlizard55-lab.github.io/GEMSDOE92/) |
| Audit | [Gate receipt](docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-audit.json) · [run card](evidence/anasig_run_card.json) · [full analysis](docs/ANALYSIS_20261024_ANASIG.md) |

**Verdict: negative (not cleared).** This session first built SCARPPOL (rank-1 hypothesis): HOLDOUT-DTI f45 0.005315 beat BREAKLINE, but final dots overlap same-dose BREAKLINE files at 0.900–0.913 → logged as a duplicate under protocol rule 1 and stopped (`evidence/scarppol_run_card.json`). ANASIG is the lane-unique deliverable that replaced it as primary.

### Holdout evidence (not a competition score)

**HOLDOUT-DTI**, evaluator `gems57-pooled-hide-v2`, 8 buffered spatial folds (seeds 20/30), 22,663 withheld positive catalogue pixels, pooled DTI α=0.2 / β=0.8 / 300 m triangular kernel, 1,000 paired 20 km spatial-cluster bootstrap draws:

- ANASIG f45: **0.004967 [0.004098, 0.005940]**; paired Δ vs R0 **+0.000961 [+0.000168, +0.001814]**.
- Holdout best RELIEF p10: **0.006045 [0.005187, 0.006927]**; paired Δ ANASIG−RELIEF **−0.001078 [−0.002034, −0.000112]**.
- Parent R0: **0.004006 [0.003424, 0.004690]**.
- Leakage canary: ANASIG surface symmetric AUC **0.503999**; max over features **0.551113** (< 0.90).
- Off-catalogue SGMC **PROXY**: ANASIG 0.080556 vs R0 0.096060 (below parent).

Hypothesis: magnetic analytic-signal ridges (`sqrt(Band3²+Band9²)`, coherence-gated on Band14) mark basement contacts dropped by the multi-line-corroborated H19-5 skeleton; 16,944 far dots sit on the strongest such ridges >3 px off the skeleton. Named mimic: lithologic contacts, dikes, volcanic flow margins, cultural noise. Ranked hypotheses + all screens: [`docs/HYPOTHESES_20261024_SCARPPOL.md`](docs/HYPOTHESES_20261024_SCARPPOL.md).

## What did the claimed 0.2778 result tell us?

The provided record identifies `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` as a **CLAIM 0.2778**, not an organizer-confirmed receipt in this repository. Its reported lineage suggests its score arose from successive improvements in ridge-based placement, Poisson thinning, pruning low-value dots, and avoiding known traces; under DTI's α=0.2, β=0.8 weighting, extra poorly placed mass is costly. These are plausible explanations from the reported lineage—not an independently verified causal analysis. The actual competition score, exact submitted bytes, and organizer evaluation receipt are absent here.

The newly generated HOLDOUT-DTI is on a different, local hide-and-recover instrument and must **not** be compared numerically to 0.2778. A prior repo-recorded read of the [official public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) on 2026-10-24 showed **0.4413 at #1** (LEADERBOARD-SNAPSHOT, not a receipt for GEMSDOE32 or this candidate); the prompt's 0.3195 is an older conflicting snapshot. The task of beating the live competition result remains unproven until this project has a valid organizer receipt.

## Hypotheses and scientific queue

See [`docs/hypotheses_visible_collar_20261024.md`](docs/hypotheses_visible_collar_20261024.md) for five ranked candidates with target signatures, rationale, implementation differences, data requirements, and viability. Only the visible-collar candidate was tested this session. The GeoDAWN feature stack is **not present in this checkout's local cache**; band-specific hypotheses are therefore untested. Do not invent band values or availability. Future work should add an off-catalogue proxy and expand cross-site registry coverage before any slot decision.

## Submission form — 3 steps

1. Download the **zeros-outside** GeoTIFF above (or its ZIP).
2. On DrivenData's [competition submission page](https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/), upload it and enter the exact name and note shown above.
3. Review the organizer receipt and record it in `ledger/submissions.csv`. An upload is a separate human action; this agent cannot log in or submit.

See [`docs/SUBMIT.html`](docs/SUBMIT.html) for detailed steps and warnings.

## Reproducible checks

```bash
.venv/bin/python scripts/build_visible_collar_submission.py
.venv/bin/python -m pytest tests -q
make PYTHON=.venv/bin/python manifest
make PYTHON=.venv/bin/python verify
PYTHONPATH=vendor .venv/bin/python scripts/check_site.py
.venv/bin/python scripts/audit_public_registry.py --candidate docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif
```

The public-registry audit requires `gh` API access, hashes/downloads the current matching owner-repository TIFF blobs into ignored `.cache/` (about 1 GB for this scan), and writes a dated audit. It is intentionally not run by the page-build check.

Builder inputs: pinned `data/bridge/` rasters and `data/parent_R0_zeros.tif`; it does not contact DrivenData or require credentials. The script writes a candidate, reruns the hide-and-recover/uniqueness/format checks, and records `evidence/visible_collar_run_card.json`.

## Limitations / irregularities to keep visible

- No DrivenData authentication: competition-tab downloads and uploads are unavailable here. The official training-feature stack is absent locally; the public competition data tab is login-gated in the repository's recorded environment.
- The ledger has no organizer receipt for this candidate. Local HOLDOUT-DTI is not a leaderboard score and may reward recovery of mapped catalogue geometry rather than genuinely new faults.
- Expanded uniqueness inventory covers current default branches of 102 public owner repositories and 1,279 same-grid submission rasters; it is still not exhaustive of history, private repos, site-hosted or other-owner assets. The discovered duplicate alone is sufficient to stop.
- Existing/owner-mirrored raster lineage has SHA-256 checks, but those checks establish byte integrity against the mirror, not organizer authentication. Public-repository redistribution terms remain flagged in `IRREGULARITIES.md`.
- No live submission slot was selected or used. Respect the competition's weekly cap and separate selector step.

## Official references for manual review

- Competition overview/problem: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- Competition about: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/>
- Competition data (login may be required): <https://www.drivendata.org/competitions/306/competition-doe-gems/data/>
- Competition rules PDF: <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
- Reference solution: <https://github.com/drivendataorg/gems-prize-reference-solution>
- USGS GeoDAWN catalog: <https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7>
- GDR/INGENIOUS: <https://gdr.openei.org/submissions/1391>
- EPSG:32611: <https://epsg.io/32611>
- USGS 3DEP: <https://www.usgs.gov/3d-elevation-program>
- Tversky index: <https://en.wikipedia.org/wiki/Tversky_index>

Evidence labels are strict: **HOLDOUT-DTI** = local hide-and-recover; **CLAIM** = owner/prompt-reported value; **ORGANIZER-CONFIRMED** = copied from a submission receipt. No projection is presented as a score.

---

## Session contract

The full operating instructions and parallel-run protocol are maintained in [`SESSION_PROMPT.md`](SESSION_PROMPT.md). Read that file at the start of every session. The governing values are **Maximize P(Win)** and **Own the Outcome**: test candidates before a slot, report negative results, preserve evidence, and distinguish local validation from competition results.
