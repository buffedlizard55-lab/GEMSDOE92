# Candidate handoff — human review and submission only (updated 2026-10-24)

**✅ FORMAT-VALID — OK TO DOWNLOAD. ⚠ NOT CLEARED FOR A WEEKLY SLOT.** The zeros-outside file below re-passes all 10 MUST gates after being written and independently re-read from disk. If you see ✅, the portal error `Predicted values must be in range [0, 1]` is fixed for that file: every one of the 12,279,160 cells is finite, `nodata=None`, values are `0.0`/`1.0` only.

**Do not upload until you confirm the entity's rolling-week quota and independently review the selected raster.** The agent never submits and never contacts the leaderboard. Parent R0 (`h33-h33-2-b2`) score `0.2778` is an owner-reported **CLAIM**, not a `RECEIPT`. This repository holds **zero organizer receipts**; the first upload is also the programme's first calibration point. Upload **at most one** file per slot — the NaN-outside `.tif` and the `-zeros.tif` twin carry identical in-footprint values and score identically, and the three BREAKLINE dose siblings share their keep sets.

## Use the zeros-outside encoding

The portal validates **every** cell, including outside the study-area footprint. Two historical failures produce the same `[0, 1]` message: the training stack's `−3.4028235e+38` nodata sentinel (3,061 such cells lie *inside* the footprint) and a stray NaN. Every `*-zeros.tif` served here is written all-finite and cannot trigger either.

| served file | encoding | portal |
|---|---|---|
| `*-zeros.tif` | zeros outside, `nodata=None` | **PORTAL-SAFE** |
| `*.tif` (no suffix) | NaN outside, `nodata=nan` | valid competition format, but one validator change from rejection |

## Current candidate — BREAKLINE f45Ltop (verdict: negative / NOT_CLEARED)

Same instrument for every number: `gems57-pooled-hide-v2` (whole-segment hiding, seeds 20/30), 22,663 withheld catalogue positives, 157 spatial clusters, 1,000 paired bootstrap draws. **R0 HOLDOUT-DTI = 0.004006.** These are local instruments, **never** leaderboard scores.

| Status | File to upload (zeros-outside) | Submission name | Form note (≤140) | HOLDOUT-DTI | Δ vs R0 (paired 95 % CI) | % within 3 px of R0 | SHA-256 (zeros) |
|---|---|---|---|---|---|---|---|
| **candidate — NOT CLEARED** | `docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif` | `GEMSDOE92-BREAKLINE-f45Ltop-20261024` | `h33-h33-2-b2; BREAKLINE f45Ltop 16944 far dots on linear scarp-break ridges >3px off H19-5` (90) | **0.004861** [0.004032, 0.005822] | **+0.000854** [+0.000300, +0.001423] | **55.0 %** (unique) | `cd9c8a564588e6542b379cd36cbe05fc6da3be07b8edbc542bf737336907810e` |
| same-lane sibling — do not also submit | `docs/downloads/h33-h33-2-b2-BREAKLINEf38Ltop-20261024-c6803c1c-zeros.tif` | — | — | 0.004761 | +0.000755 | 62.0 % | (see ledger) |
| same-lane sibling — do not also submit | `docs/downloads/h33-h33-2-b2-BREAKLINEf33Ltop-20261024-5f112439-zeros.tif` | — | — | 0.004673 | +0.000667 | 67.0 % | (see ledger) |

**Why NOT CLEARED:** the pre-registered promotion rule requires beating the current holdout best. RELIEF p10's HOLDOUT-DTI is 0.006045 and BREAKLINE f45's is 0.004861 (Δ −0.001185 [−0.001995, −0.000394]). RELIEF p10 nonetheless **cannot** be promoted either — at 99.38 % of dots within 3 px of R0 it is a literal duplicate under the brief's ≤ 70 % uniqueness rule, as are all DILATATION doses (99.37–99.40 %). BREAKLINE f45Ltop is the first file in this repository that is **both literal-unique and above its parent on the holdout with CI excluding 0**, and it is +31 % over R0 on the catalogue-independent USGS SGMC bedrock-fault control (0.12611 vs 0.09606) where RELIEF p10 scores 0.08725. Whether those properties justify spending one weekly slot — e.g. as the programme's first calibration measurement — is a human portfolio decision; this page guarantees the file, not the outcome.

**If you do submit:** use the f45Ltop zeros file, name `GEMSDOE92-BREAKLINE-f45Ltop-20261024` and the 90-char note above; submit **one** encoding; record the receipt score and date in `ledger/submissions.csv` (row `h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0`) — that receipt is the only ORGANIZER-CONFIRMED number; holdout and MODEL values are never scores.

## Earlier candidates — built and documented, none cleared

| Lane | HOLDOUT-DTI | Why it is not a slot |
|---|---|---|
| RELIEF p10 (`…RELIEFp10piedmont-20261024-3e900c24-zeros.tif`) | 0.006045 | 99.38 % within 3 px of R0 → literal duplicate; SGMC control falls to 0.08725 |
| DILATATION p10/p12/p15 | 0.005747 / 0.005779 / 0.005818 | 99.37–99.40 % within 3 px of R0 → literal duplicates |
| TIPGAP far18f33 | 0.002723 | Literal-unique (67.0 %) but HOLDOUT-DTI **below** R0 (Δ −0.001283) — a negative-result deliverable that falsifies the tip-continuation hypothesis; do not spend a slot expecting a gain |

Still built (see `ledger/submissions.csv`): `RELIEF p12/p15`, `SNAP scarp2p0px / scarp1p4px / pot2p0px / cap2p0-g0.05/0.10/0.15`, `CONCENTRATION catblk10up10 / up20 / dn10 / phys10`, `PRUNE B3/B4/B5` and `PRUNEp2.5/p3.5/p4.5px-refill`, `MASS D10/A10/SWAP10`. Standing caveats: **MASS** ranked on a binary `h19_5.tif` (value 1.0 at every R0 dot) so it is a random 10 % perturbation control, not a ranking test; **CONCENTRATION** cannot attain the 2.83 px spacing floor on the 1-px skeleton and a nominal 10 % move is 7.34 % in positions. See `IRREGULARITIES.md`.

## Report-only diagnostics (`PROXY`, never gates or scores)

- **BREAKLINE** (`evidence/breakline_proxy_audit.json`) — holdout as tabulated. Leakage canaries (each feature alone, symmetric AUC): L 0.6216, slope-break 0.5685, coherence 0.5521 — max `0.6216 ≪ 0.90` (`REPORT_ONLY_PASS`).
- **SGMC off-catalogue bedrock control** (62,703 px > 3 px from catalogue): R0 `0.096060`; BREAKLINE f33/f38/f45 `0.119338 / 0.121817 / 0.126105` (+24 % / +27 % / +31 %); RELIEF p10 `0.087245`; DILATATION p12 `0.081467`. SGMC maps exhumed bedrock faults, so it is biased toward range-interior structures and against basin-buried ones; it confirms genuine geographical reallocation, nothing more.

## How to submit — 3 steps

1. Download the zeros-outside file for the slot you are spending (table above).
2. At <https://www.drivendata.org/competitions/306/competition-doe-gems/data/> (login required) choose **New submission**, select the `.tif` (or a `.zip` containing one GeoTIFF — both are accepted). Do not edit the file.
3. Paste the submission name and form note from the table, submit, and **copy the receipt score into `ledger/submissions.csv`**. That receipt is the only ORGANIZER-CONFIRMED number.

## Deterministic reproduction

```bash
pip install -r requirements.txt
python scripts/restore_inputs.py               # SHA-256 + byte-verifies all 12 pins
python scripts/build_breakline_variants.py     # rebuilds R0 byte-for-byte, builds f33/f38/f45 Ltop, re-reads, runs gates
python scripts/report_breakline_proxies.py     # pooled holdout + leakage canaries + SGMC control + uniqueness
python scripts/make_breakline_run_card.py      # run card assembled from evidence
make test && make manifest && make verify      # full suite · RESULT: OK · PARENT VERIFIED
```
