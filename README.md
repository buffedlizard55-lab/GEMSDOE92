# GEMSDOE92 — auditable GEMS Prize submission workbench

> **Start each session by reading this README and [`SESSION_PROMPT.md`](SESSION_PROMPT.md).** The session contract is the lane/budget/holdout/uniqueness policy; do not spend a live slot from this agent. Maximize P(Win) and own the outcome.

## Executive summary — format-validated candidate, one-click download

**✅ FORMAT-VALID — OK TO DOWNLOAD.** The new candidate is an all-finite single-band float32 GeoTIFF, EPSG:32611, shape 3730 × 3292, matching the competition template's transform. It has no NaN inside the footprint, zeros outside, values only in `[0,1]`, and passes all 10 local MUST gates. This prevents the portal error `Predicted values must be in range [0, 1]`.

**⛔ NOT CLEARED FOR A WEEKLY SLOT — duplicate under the literal registry rule.** An expanded scan found 100% 3-px forward overlap with public registry rasters (131 of 1,279 exceed 70%). Stop; do not submit. This file remains downloadable as a negative research deliverable. The scan covers current default branches in 102 public owner repositories, not every historic/site-hosted file.

| Deliverable | Link |
|---|---|
| **GeoTIFF** | [Download zeros-outside submission](docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif) |
| ZIP (one TIFF) | [Download ZIP](docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.zip) |
| Submission name | `GEMSDOE92-visible-collar-r0-excluded-20261024` |
| Note (62 chars) | `Visible-fault collar 2-3 px; R0 3px halo excluded; 37,654 dots` |
| SHA-256 | `60082b75a3d8e4648a858622f71f24257c8cfef79286a1a96147c59f05377da7` |
| Submission steps | [Executive summary](docs/SUBMIT.html) · [site](https://buffedlizard55-lab.github.io/GEMSDOE92/) |
| Audit | [Machine-readable gate receipt](docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-audit.json) · [full run card](evidence/visible_collar_run_card.json) |

**Verdict: negative (duplicate).** No slot was used and no upload was performed. The literal uniqueness rule is binding even though the candidate's local holdout improved.

### Holdout evidence (not a competition score)

**HOLDOUT-DTI**, evaluator `gems57-pooled-hide-v2`, 8 buffered spatial folds (4 quadrants × seeds 20 and 30), 22,663 withheld positive catalogue pixels, pooled DTI α=0.2 / β=0.8 / 300 m triangular kernel, 1,000 paired 20 km spatial-cluster bootstrap draws:

- Candidate: **0.046866**, 95% CI **[0.040216, 0.053315]**.
- Parent R0: **0.004006**, 95% CI **[0.003424, 0.004690]**.
- Paired difference: **+0.042860**, 95% CI **[+0.036122, +0.049357]**.
- Leakage canary (visible-fault distance alone): symmetric AUC **0.745593**, below the 0.90 stop threshold.

This is a large improvement on the **catalogue hide-and-recover proxy**. It does not show that the candidate finds a genuinely new fault, and cannot be translated into an organizer score. Hidden truth is from the mapped catalogue; the live target is private and specifically emphasizes uncatalogued structure.

### Hypothesis and non-fault mimic

Emit 37,654 unit-mass dots at the closest legal cells 2–3 pixels (200–300 m) from visible catalogue faults, while excluding all cells within 3 pixels of parent R0. Hypothesis: blind splays, relay fractures, or parallel strands may occur close to mapped structures but outside the inherited R0 footprint. Named mimic: drainage/alluvial-fan margins and lithologic contacts can create non-tectonic lineaments near mapped faults.

The holdout placement surface used **only each fold's visible catalogue**. The final export additionally used the full known catalogue to enforce zero mass on known faults. This differs from TIPGAP/STEPOVER endpoint-focused lanes and from previous R0 perturbations. It is a geometric association test, not direct geological proof.

Expanded REGISTRY-MEASUREMENT: 1,279 unique same-grid TIFFs from current default branches of 102 public GEMSDOE-named owner repositories. Pre-placement worst |ρ| **0.421367** and final worst |ρ| **0.492957** (below 0.90); however both the surface and final dots have **1.000000 forward 3-px overlap** with registry support, and **131** rasters exceed the 70% stop threshold. Binding witness: [11GEMSDOE structural-area06 raster](https://github.com/buffedlizard55-lab/11GEMSDOE/blob/main/docs/downloads/gems-structural-area06-v1.tif). Verdict is **negative; stop**. Scan scope and failures/omissions are recorded in `evidence/public_registry_uniqueness.json`; this is broad but not exhaustive of historical/private/site-hosted assets.

## What did the claimed 0.2778 result tell us?

The provided record identifies `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` as a **CLAIM 0.2778**, not an organizer-confirmed receipt in this repository. Its reported lineage suggests its score arose from successive improvements in ridge-based placement, Poisson thinning, pruning low-value dots, and avoiding known traces; under DTI's α=0.2, β=0.8 weighting, extra poorly placed mass is costly. These are plausible explanations from the reported lineage—not an independently verified causal analysis. The actual competition score, exact submitted bytes, and organizer evaluation receipt are absent here.

The newly generated HOLDOUT-DTI is on a different, local hide-and-recover instrument and must **not** be compared numerically to 0.2778. The task of beating the public competition result remains unproven until a valid organizer receipt exists. Publicly mentioned leaderboard ceilings 0.3195 and 0.4413 conflict and are not authenticated by this checkout.

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
