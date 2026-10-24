# GEMSDOE92 — DOE GEMS submission research and validation

> **Start every session by reading this README and [`SESSION_PROMPT.md`](SESSION_PROMPT.md).** That file records the requested parallel-run protocol, evidence-label policy, experiment budget, and source links. This repository's live files and test-gated behavior are authoritative where earlier session notes conflict.

## Current deliverable — negative-result GeoTIFF

**FORMAT-VALID — OK TO DOWNLOAD. NOT CLEARED FOR A WEEKLY SUBMISSION SLOT; NOT RECOMMENDED.**

| Item | Value |
|---|---|
| Candidate | TIPGAP FAR (`far18f33`), zeros-outside encoding |
| GeoTIFF | [`docs/downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.tif`](docs/downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.tif) |
| ZIP (single TIFF) | [`docs/downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.zip`](docs/downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.zip) |
| Name | `h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a` |
| Note (88 chars) | `h33-h33-2-b2; TIPGAP FAR 33% along-strike >3px off parent skeleton; HOLDOUT-DTI negative` |
| SHA-256 | `0ca8248acace558f5cf86b153134b8fd5cc2b7d5b343d0a36f000f9fbfe4758f` |
| Decision evidence | [`evidence/tipgap_far18f33_submission_card.json`](evidence/tipgap_far18f33_submission_card.json) |
| Guide | [`docs/executive-summary.html`](docs/executive-summary.html) · [project site](https://buffedlizard55-lab.github.io/GEMSDOE92/) |

**Provenance irregularity:** this checkout is being reviewed on 2026-10-24, but several pre-existing artifact filenames and notes say 2026-10-25. Their chronology cannot be reconciled from repository bytes alone; treat those timestamps as unverified metadata, not as work performed in this session.

Local validation records one-band float32, EPSG:32611, 3730×3292, matching sample transform, finite values in [0,1], no NaN, zeros outside the footprint, and 37,654 positive pixels. This addresses the reported portal error `Predicted values must be in range [0, 1]`. Local validation is not organizer acceptance.

**HOLDOUT-DTI** `gems57-pooled-hide-v2`, 22,663 withheld positives: TIPGAP FAR `0.002723 [0.002324, 0.003131]`; R0 `0.004006 [0.003408, 0.004651]`; difference `−0.001283`. This is a negative result, not a score or a forecast. Against the local R0 raster its dot overlap within 3 px is 67.00% and full-footprint Spearman is 0.66898, below the protocol limits. The accessible registry is incomplete relative to external/private sites, so **global uniqueness has not been established**. No slot is recommended.

### Local verification

Use the project environment (after installing `requirements.txt`):

```bash
python -m pytest -q
make manifest
make verify
PYTHONPATH=vendor python scripts/check_site.py
```

The site gate independently re-reads every linked zeros-outside raster and checks value range, footprint, CRS/grid, catalogue exclusion, and its primary audit record. “PASS” means local preflight only; it is not organizer confirmation or global uniqueness.

## Competition and project approach

The goal is to detect geothermal-related faults not already represented in the USGS/INGENIOUS catalogue, create a submission-grid GeoTIFF, and validate it programmatically. The requested review must distinguish scientific hypotheses, local holdout evidence, model projections, and organizer receipts. The holdout can only evaluate recovery of visible catalogue faults; it is not a perfect proxy for discovering genuinely new faults. A human competitor must perform any account-authenticated upload and choose whether to spend a weekly slot.

Historical values cited in prompts, including GEMSDOE32's 0.2778 and leaderboard figures such as 0.3195 or 0.4413, are **claims unless an organizer submission receipt is recorded**. The repository ledger has no organizer receipt for the GEMSDOE32 parent. Never state a local HOLDOUT-DTI as an organizer score.

## Hypotheses and prior results

- [`docs/hypotheses_20261024.md`](docs/hypotheses_20261024.md) lists five candidate mechanisms, their bands/signatures, novelty relative to this repo, expected improvement (explicitly MODEL only), implementation cost, and the tested top candidate.
- The tested DILATATION doses yielded positive local HOLDOUT-DTI deltas but exceed the literal whole-file 70% overlap threshold against R0; they are duplicates under the stated gate and are not recommended.
- TIPGAP FAR is locally under that overlap threshold but underperforms R0 on holdout. It is retained as a negative result.
- The older STEPOVER candidate also recorded a negative holdout. Do not infer a leaderboard outcome from these local experiments.
- Experiments are bounded by the protocol in `SESSION_PROMPT.md`; do not run more than the stated maximum or select a live submission slot in an experiment session.

## Data and reproducibility boundaries

The tracked `data/bridge/` rasters and some derived files originate from owner-maintained mirrors of login-walled competition inputs. Their local SHA-256 integrity can be checked, but their upstream origin and redistribution permission have not been independently authenticated in this sandbox. See [`registry/session_manifest.json`](registry/session_manifest.json) and [`IRREGULARITIES.md`](IRREGULARITIES.md). Do not claim official-source verification where only mirror hashes were verified. No DrivenData authentication is available to download protected files or submit predictions.

## Official/source links for review

- [DrivenData competition overview and problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData about page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [DrivenData competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (may require login)
- [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [DOE GEMS rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [DOE Geothermal Data Repository / INGENIOUS](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)

These links are provided for provenance and manual review; internet restrictions prevented independent retrieval of several non-GitHub sources in this environment. See `docs/executive-summary.html` for submission instructions and limitations.
