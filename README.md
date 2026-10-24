# GEMSDOE92 — auditable GEMS Prize submission workbench

> **Start each session by reading this README and [`SESSION_PROMPT.md`](SESSION_PROMPT.md).** The session contract is the lane/budget/holdout/uniqueness policy; do not spend a live slot from this agent. Maximize P(Win) and own the outcome.

## Latest review: literal uniqueness is blocked across the footprint

**OK TO DOWNLOAD for research; NOT OK TO SUBMIT.** The queued BREAKLINE public
witness audit now finds **REGISTRY-MEASUREMENT 100% forward overlap** with the
hash-verified 17GEMSDOE dense raster. Its 3-pixel halo covers the whole footprint,
so every nonempty in-footprint candidate would fail the current literal rule.
No new unique submission was generated, no score improvement is claimed, and no
slot was used. [Review and limitations](docs/REVIEW_CURRENT.md) ·
[witness receipt](docs/downloads/breakline_public_witness.json) ·
[session JSON card](docs/downloads/session_review_run_card.json).
This supersedes the older statement below that BREAKLINE was unscanned publicly;
the full historical registry scan was **not** repeated.

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

Expanded REGISTRY-MEASUREMENT: 1,279 unique same-grid TIFFs from current default branches of 102 public GEMSDOE-named owner repositories. Pre-placement worst |ρ| **0.421367** and final worst |ρ| **0.492957** (below 0.90); however both the surface and final dots have **1.000000 forward 3-px overlap** with registry support, and **131** rasters exceed the 70% stop threshold. Binding witnesses include [11GEMSDOE structural-area06](https://github.com/buffedlizard55-lab/11GEMSDOE/blob/main/docs/downloads/gems-structural-area06-v1.tif) and 17GEMSDOE's full-footprint E-proba raster. Verdict is **negative; stop**. The latter may act as a universal blocker under the literal positive-support definition. Scan scope and omissions are recorded in `evidence/public_registry_uniqueness.json`; inventory was first fetched live then compared from SHA-verified cache after GitHub API rate limiting, and is not exhaustive of historical/private/site-hosted assets.

## Parallel-session candidate — BREAKLINE f45Ltop (also negative)

A second 2026-10-24 session (merged after the candidate above) built **BREAKLINE**: keep 20,710 R0 dots by exact expected-DTI greedy under a DEM scarp-break field `L = pct_rank(||grad det_elev_slope||) x structure-tensor coherence(det_elev)` (Bands 19/12), and spend the freed 16,944 dots (45%) on the strongest coherent breaks **>3 px off the whole H19-5 skeleton**. Hypothesis: faults with a scarp but no magnetic/gravity contrast are missed by the worm skeleton and the older-imagery catalogue, while expert DEM mapping (the live label source) traces them. Named mimic: Lahontan shorelines, fan-toe breaks, channel banks.

- **Download:** [`docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif`](docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif) · name `GEMSDOE92-BREAKLINE-f45Ltop-20261024` · note (90) `h33-h33-2-b2; BREAKLINE f45Ltop 16944 far dots on linear scarp-break ridges >3px off H19-5` · SHA-256 `cd9c8a564588e6542b379cd36cbe05fc6da3be07b8edbc542bf737336907810e`.
- **Format:** 10/10 MUST gates on independent re-read (audit receipt in `docs/downloads/`).
- **HOLDOUT-DTI** (same instrument): **0.004861 [0.004032, 0.005822]**, paired delta vs R0 **+0.000854 [+0.000300, +0.001423]**; dose-monotone f33/f38/f45; off-catalogue USGS SGMC control **+31% vs R0**; leakage-canary max **0.6216**.
- **Uniqueness (local registry):** worst forward overlap **55.0%** (parent R0), worst |rho| 0.547 over 18 local rasters; vs the visible-collar candidate only **3.5%** forward overlap (phi ~0.001) — the lanes are disjoint. **Caveat:** BREAKLINE has *not* been run through the 1,279-raster public-registry scan that stopped the collar candidate; under that scan's dense-raster forward-overlap logic the local result is not global clearance (`scripts/audit_public_registry.py` on this file is queued work — see `docs/NEXT_STEPS.md`).
- **Verdict: negative / NOT CLEARED** (does not beat the holdout-best arms). Full line-by-line analysis of why 0.2778 is high: [`docs/ANALYSIS_20261024.md`](docs/ANALYSIS_20261024.md); ranked lanes: [`docs/HYPOTHESES_20261024_BREAKLINE.md`](docs/HYPOTHESES_20261024_BREAKLINE.md); run card: [`evidence/breakline_run_card.json`](evidence/breakline_run_card.json). Ledger now holds 36 BUILT / 0 RECEIPT rows (3 BREAKLINE rows are SUPERSEDED emission evidence; the visible-collar candidate predates the ledger row convention used there — see its run card).

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
