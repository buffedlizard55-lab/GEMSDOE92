# GEMSDOE92 — Auditable GEMS research workbench

> **Read this README and [`SESSION_PROMPT.md`](SESSION_PROMPT.md) at the start of every project session.** Before experiments, also read [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md), [`SLOT_PLAN.md`](SLOT_PLAN.md), [`IRREGULARITIES.md`](IRREGULARITIES.md), and the current review/evidence links below. One method lane at a time; negative results are deliverables.

## Current decision — no submission cleared

**Existing files are downloadable for research only. DO NOT SUBMIT any GeoTIFF currently linked from this repository.** The project’s literal registry rule says to stop if more than 70% of a candidate’s positive pixels fall within 3 pixels of any registry raster. A hash-verified public registry witness from 17GEMSDOE has positive support on **100% of this template’s footprint**. Under that literal rule, every nonempty in-footprint candidate overlaps that witness by 100%; no geological placement can pass while the witness and rule remain in force. This is a **REGISTRY-MEASUREMENT**, not a competition score. The exact witness bytes and scope are recorded in [`docs/downloads/current_status.json`](docs/downloads/current_status.json) and [`docs/REPO_REVIEW_20261024.md`](docs/REPO_REVIEW_20261024.md).

No new candidate GeoTIFF was generated in this review: stopping before placement is required by the protocol. No weekly slot was used. The site’s last generated candidates remain available as **negative research artifacts**, clearly marked **OK TO DOWNLOAD FOR RESEARCH — DO NOT SUBMIT**. See the [workbench](https://buffedlizard55-lab.github.io/GEMSDOE92/) and [conditional submission guide](docs/SUBMIT.html).

## What the reported 0.2778 does — and does not — establish

The prompt associates `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` with **CLAIM 0.2778**. This repository has no organizer receipt for that value (`registry/parents/R0.json` has `receipt: null`; `ledger/submissions.csv` contains no matching receipt). It must not be presented as ORGANIZER-CONFIRMED.

The parent’s documented design suggests plausible mechanisms: a fixed prediction budget, thinning spatially redundant line pixels, and limiting predictions on the known-fault catalogue. Under the repository’s implementation of the distance-weighted Tversky score, these choices could improve spatial coverage per emitted pixel. That is a mechanistic hypothesis, **not causal proof**: the exact organizer receipt, evaluated bytes, scoring context, and private targets are unavailable here. The prompt’s leaderboard snapshots (0.3195 and 0.4413) conflict, and the official non-GitHub leaderboard could not be refreshed from this network-restricted session. None is used as a current confirmed score.

A higher competition score is possible in principle, but this checkout cannot show that it has happened or predict it reliably. The best saved local result is **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives), 0.006045 with 95% CI [0.005187, 0.006927]; it is a catalogue hide-and-recover estimate, not a leaderboard score. It also fails the repository’s literal registry-uniqueness gate. See the evidence-labeled [analysis](docs/ANALYSIS.md) and [ranked untested hypotheses](docs/HYPOTHESES.md).

## Submission status and automated checks

- **Format and uniqueness are separate.** A format pass verifies the GeoTIFF’s single band, CRS, shape, transform, finite in-footprint values in [0,1], and outside-footprint convention. It does not prove scientific value, uniqueness, or permission to spend a competition slot.
- The homepage links the zeros-outside research files and says **DO NOT SUBMIT**. The [executive summary / submission guide](docs/SUBMIT.html) explains the exact DrivenData form flow **only for a future artifact** whose exact-byte audit says `submission_eligible: true` and which has been separately selected.
- The DrivenData reference solution supports a CPU-only environment; its README says a GPU makes training faster, not that a GPU is mandatory. The reference repo is linked below. This project review did not train a model.
- The full authorized 19-band feature stack is absent from `.cache/gems_inputs/`. This session did not retrieve competition data or use a public mirror with unchecked redistribution terms. Consequently no new feature was evaluated on holdout and no new score or projection is reported.

Run the checks for the tracked checkout:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest tests -q
.venv/bin/python scripts/check_site.py
.venv/bin/python -m gems manifest --manifest registry/data_manifest.json --data-root data
.venv/bin/python -m gems parent --recipe registry/parents/R0.json --data-root data
```

A new experiment may start only after the data source/provenance is authorized, the pre-placement surface passes the literal registry gate, and the shared `vendor/gems57/evaluate_holdout.py` can run the specified buffered whole-segment hide-and-recover test. Use visible-only catalogue-derived features, pixel-exact visible-fault masking, pooled DTI α=0.2 / β=0.8 / 300 m triangular kernel, a feature-alone leakage canary (symmetric AUC >0.90 is a leakage alarm), a 95% CI, and the shared submission writer. Stop at three experiments or two hours. Do not spend a competition slot as part of development.

## Persistent project brief

The durable goal is a **scientifically grounded, auditable project that can produce a unique, correctly formatted competition GeoTIFF**, with a prominent download link, automated validation, transparent provenance, and an executive summary that explains the upload form. Do not copy an earlier candidate as a new submission. Generate candidate hypotheses before implementation; test one method lane; preserve negative results; never confuse a local HOLDOUT-DTI, model projection, or proxy with an organizer-confirmed receipt. A format-valid file is not necessarily cleared to submit. The current public registry witness is a blocking stop, not an invitation to evade the rule with an empty raster or a cosmetic file mutation.

The user’s core values remain project requirements:

- **Maximize P(Win)** — weigh risk and evidence; do not gamble competition slots on an unvalidated idea.
- **Own the Outcome:** preserve failures, fix shared defects once, and make the final status clear instead of implying success.

The full operating contract, prior sessions, source links, and experiment records are in [`SESSION_PROMPT.md`](SESSION_PROMPT.md), [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md), and [`docs/REPO_REVIEW_20261024.md`](docs/REPO_REVIEW_20261024.md).

## Official / primary-source links for review

- [DrivenData DOE GEMS problem and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData competition data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) — access may require a competitor login.
- [DrivenData reference-solution repository](https://github.com/drivendataorg/gems-prize-reference-solution) — **checked live in this review**; its README directs competitors to download data from the competition site and provides CPU-only environment instructions.
- [Official competition rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [DOE GDR INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391)
- [USGS 3D Elevation Program](https://www.usgs.gov/3d-elevation-program)
- [EPSG:32611](https://epsg.io/32611)

**Verification boundary:** only GitHub is among the external source hosts reachable in this review. Non-GitHub pages above are provided for manual/source-owner review, not claimed as freshly accessed. No DrivenData credentials were used or requested; no upload or slot selection is performed by this project.
