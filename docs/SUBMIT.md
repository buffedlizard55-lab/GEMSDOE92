# Submission guide — GEMSDOE92

## Current status: OK TO DOWNLOAD FOR RESEARCH — DO NOT SUBMIT

No current artifact is cleared for the competition. The primary existing research file is [SPRINGALIGN f33Ctop zeros-outside GeoTIFF](downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif); its one-TIFF ZIP is [here](downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.zip). It passes the local format audit, but is **not unique under the literal registry rule** and is below the current holdout-best bar. Download is for research only; do not upload it.

- Audit: [JSON](downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-audit.json)
- Run card: [JSON](downloads/springalign_run_card.json)
- Full review: [REVIEW_REPO_20261024.md](REVIEW_REPO_20261024.md)
- SHA-256: `1772ad5c62506b6b380e221d2202b583edf0a5be4f96916af655e0478eba11b1`
- Internal research identifier (not a verified portal field): `GEMSDOE92-SPRINGALIGN-f33Ctop-20261025`
- Research note (not for current upload): `h33-h33-2-b2; SPRINGALIGN f33Ctop 12426 far dots on spring-pair alignment lines >3px off H19-5`

**REGISTRY-MEASUREMENT:** an existing hash-verified witness is positive on every target-footprint cell. Any nonempty in-footprint prediction therefore has 100% forward overlap at 0 px with that witness. This is a decisive single-witness stop, not a fresh full-registry scan. No new TIFF or weekly slot was used in the review.

**HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives): SPRINGALIGN 0.004865, 95% CI `[0.004025, 0.005785]`; its paired difference versus RELIEF p10 (recorded holdout best) is −0.001180, 95% CI `[−0.002065, −0.000337]`. Local holdout values are not competition scores.

## How a future eligible file would be submitted

Do not use these steps for any file currently linked in the site. They apply only when the exact file's run card says `verdict: promote`, its registry checks pass before placement and on final dots, it clears the paired holdout-best gate, and its audit says `submission_eligible: true`.

1. Download the exact zeros-outside `.tif` named in the cleared run card; do not change or re-save it.
2. Open the official DrivenData “New submission” page and choose the file under **File to submit**. The supplied form description accepts one GeoTIFF or a ZIP containing one GeoTIFF.
3. Paste the run-card note into **Note (optional)**. The project identifier is a ledger/research name; the form description supplied by the user does not show a separate submission-name field.
4. Slot selection is a separate selector decision. After an authorized upload, copy the submission-page receipt's ID, date, and score into `ledger/submissions.csv`. Never substitute HOLDOUT-DTI for an organizer score.

The repository automates raster inspection and validation; no human pixel inspector is required. DrivenData authentication, live quota checking, slot selection, upload, and receipt capture are not automated. No credentials are requested or stored.

## Reproducible local checks

```bash
.venv/bin/python -m pytest -q
PYTHONPATH=vendor .venv/bin/python scripts/check_site.py
.venv/bin/python -m gems manifest --manifest registry/data_manifest.json --data-root data
.venv/bin/python -m gems parent --recipe registry/parents/R0.json --data-root data
```

Passing format checks means **OK TO DOWNLOAD FOR RESEARCH**, not **OK TO SUBMIT**.
