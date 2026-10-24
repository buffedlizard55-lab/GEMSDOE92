# Submission status and form guide

**Read first:** the primary p12 file passes the project's local value-range/geometry preflight and is **OK TO DOWNLOAD FOR REVIEW**, but official submission-format acceptance is unresolved: the raster stores zeros outside the footprint while the official problem page says outside-bounds data should be null/NaN. It is also **NOT CLEARED / NOT RECOMMENDED for a weekly competition slot** because 99.37% of its dots fall within 3 px of registry raster R0, exceeding the literal 70% uniqueness stop. Do not submit it; any upload would be a human override.

The HTML executive summary is the canonical user-facing guide: [`SUBMIT.html`](SUBMIT.html). The download page is [`index.html`](index.html).

## Current primary

- File: [`downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-zeros.tif`](downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-zeros.tif)
- SHA-256: `25ba17a26d31df9d574fba2a2f34d03ff58f587f4ffde092dcc4bba9822f8898`
- Local preflight: 10/10 project range/geometry gates PASS after reread; one float32 band, EPSG:32611, shape 3730×3292, sample transform, all stored values in [0,1], no NaN in footprint. Outside is zero-filled, so official format acceptance is unresolved against the problem page's null/NaN statement.
- **HOLDOUT-DTI**: evaluator `gems57-pooled-hide-v2`; 22,663 withheld positives; p12 0.005779, 95% CI [0.004863, 0.006851]. Parent R0 **HOLDOUT-DTI** 0.004006, 95% CI [0.003424, 0.004690]. Paired change **HOLDOUT-DTI** +0.00177, 95% CI [+0.00111, +0.00246]. These are local hide-and-recover measurements, not leaderboard scores.
- Registry overlap: 99.37% of p12 dots are within 3 px of parent R0. This is a uniqueness-gate measurement, not a score, and it blocks promotion.
- Parent score 0.2778 is a **CLAIM**, not ORGANIZER-CONFIRMED in the local ledger; there is no receipt.

## If a future selector approves a file, the DrivenData form is

1. Download exactly the selected single-band GeoTIFF, preferably the `-zeros.tif` encoding, or a ZIP containing exactly one GeoTIFF.
2. Log into the competitor's DrivenData account, open the GEMS competition's New submission form, and choose the file. The project agent does not authenticate or upload.
3. Enter the selected candidate's unique submission name and a concise note (maximum 140 characters); do not include a model projection as a score.
4. After organizer evaluation, copy the submission-page receipt and date into `ledger/submissions.csv`. Only that receipt is **ORGANIZER-CONFIRMED**.

The project validator prevents the reported portal error `Predicted values must be in range [0, 1]` by checking every pixel, including pixels outside the footprint. Format validity alone does not establish scientific value, uniqueness, organizer acceptance, or slot eligibility.

## Official links for review

- Competition problem / metric: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- Competition data and submission form: <https://www.drivendata.org/competitions/306/competition-doe-gems/data/>
- Competition rules: <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
- Full local review, hypotheses and blockers: [`RESEARCH_AND_CANDIDATE_REVIEW_20261024.md`](RESEARCH_AND_CANDIDATE_REVIEW_20261024.md)

Official non-GitHub pages were not freshly fetched from this restricted sandbox. The links are provided for manual verification; no live leaderboard or organizer receipt is claimed.
