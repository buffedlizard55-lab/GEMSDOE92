# Candidate handoff — human review and submission only

**✅ FORMAT-VALID — OK TO DOWNLOAD. ⚠ NOT CLEARED FOR A WEEKLY SLOT.** The zeros-outside files below re-pass all 10 MUST gates after being written and independently re-read from disk. If you see ✅, the portal error `Predicted values must be in range [0, 1]` is fixed for that file: every one of the 12,279,160 cells is finite, `nodata=None`, values are `0.0`/`1.0` only.

**Do not upload until you confirm the entity's rolling-week quota and independently review the selected raster.** The agent never submits and never contacts the leaderboard. Parent R0 (`h33-h33-2-b2`) score `0.2778` is an owner-reported **CLAIM**, not a `RECEIPT`. Upload **at most one** file per slot — the NaN-outside `.tif` and the `-zeros.tif` twin carry identical in-footprint values and score identically, so uploading both wastes a slot.

## Use the zeros-outside encoding

The portal validates **every** cell, including outside the study-area footprint. Two historical failures produce the same `[0, 1]` message: the training stack's `−3.4028235e+38` nodata sentinel (3,061 such cells lie *inside* the footprint) and a stray NaN. Every `*-zeros.tif` below is written all-finite and cannot trigger either.

| served file | encoding | portal |
|---|---|---|
| `*-zeros.tif` | zeros outside, `nodata=None` | **PORTAL-SAFE** |
| `*.tif` (no suffix) | NaN outside, `nodata=nan` | valid competition format, but one validator change from rejection |

## Ranked candidates — by HOLDOUT-DTI, not by MODEL projection

Same instrument for every row: `gems57-pooled-hide-v2`, 8 folds, 22,663 withheld catalogue positives, 157 spatial clusters, 1,000 paired draws, seed 520810. **R0 = 0.004006 [0.003424, 0.004690].** These are local instruments, **never** leaderboard scores.

| Slot | File to upload (zeros-outside) | Submission name | Form note (≤140) | HOLDOUT Δ vs R0 | MODEL | SHA-256 |
|---|---|---|---|---|---|---|
| **1** | `docs/downloads/h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24-zeros.tif` | `GEMSDOE92-RELIEF-p10-20261024` | `h33-h33-2-b2; RELIEF shift 3765 dots (10%) basin/range->piedmont tercile` (73) | **+0.002039** `[0.001483,0.002504]` | +0.005 | `60f0208547efd4fb8b52fd5a298d9151de15208c3c44b04e90e78ec13a978296` |
| **2** | `docs/downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-zeros.tif` | `GEMSDOE92-DILATATION-p12-20261025` | `h33-h33-2-b2; DILATATION shift 4518 dots (12%) low→high dilat; pred MODEL:+0.007` (84) | +0.00177 `[0.001110,0.002455]` | +0.007 | `25ba17a26d31df9d574fba2a2f34d03ff58f587f4ffde092dcc4bba9822f8898` |
| **3** | `docs/downloads/h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432-zeros.tif` | `GEMSDOE92-DILATATION-p15-20261025` | `h33-h33-2-b2; DILATATION shift 5648 dots (15%) low→high dilat; pred MODEL:+0.006` (84) | +0.00181 | +0.006 | `cc79c48ae0f46b0c22cd410305a773e72b719833718bceed2c5bcda3c8c38052` |
| reserve | `docs/downloads/h33-h33-2-b2-DILATATIONp10dilatation-20261025-2e501f88-zeros.tif` | `GEMSDOE92-DILATATION-p10-20261025` | `h33-h33-2-b2; DILATATION shift 3765 dots (10%) low→high dilat; pred MODEL:+0.005` (84) | +0.00174 | +0.005 | `d3b0d4a65aacff6b962056e7a4245734bef89ed72fa54767fe8b9ea3746e8aea` |
| **no** | `docs/downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.tif` | — | — | **−0.001283** | — | `0ca8248acace558f5cf86b153134b8fd5cc2b7d5b343d0a36f000f9fbfe4758f` |

All slot rows: 37,654 unit-mass dots · EPSG:32611 · 3730×3292 · float32 · 1 band · values in `[0,1]` · 0 NaN inside footprint · 0 catalogue mass · `d_cat > 2.0 px` · **10/10 `gems.gates` PASS on independent disk reread**.

**The TIPGAP row is a negative-result deliverable, not a slot.** Its own run card records `verdict: negative`: HOLDOUT-DTI `0.002723` is *below* R0. Moving 33 % of the budget 6–18 px off the D2.8 skeleton onto along-strike tip walks **costs** credit on this instrument, which falsifies the "continuations sit 0.5–1.8 km past the tips" hypothesis. Keep it as evidence; do not spend a slot expecting a gain.

### Two honest caveats on the ranking

- **Slot 1 was not previously submittable.** RELIEF p10 had the largest holdout gain of any arm but was served only in the NaN-outside encoding. A zeros-outside twin has now been built and passes 10/10 gates; its sha256 **reproduces the value recorded in `evidence/relief_variants.json` byte-for-byte**, which independently corroborates the re-encode rather than trusting it.
- **Slots 1 and 2 are not independent.** RELIEF and DILATATION arrivals overlap 28.84 % within 3 px (Jaccard 0.1593), so a win on both is partly the same information. Do not treat two positive receipts from these two arms as two confirmations.

## Earlier sessions' candidates (still built, all documented in `ledger/submissions.csv`)

`RELIEF p12/p15`, `SNAP scarp2p0px / scarp1p4px / pot2p0px / cap2p0-g0.05/0.10/0.15`, `CONCENTRATION catblk10up10 / up20 / dn10 / phys10`, `PRUNE B3/B4/B5` and `PRUNEp2.5/p3.5/p4.5px-refill`, `MASS D10/A10/SWAP10`.

Two standing caveats apply to those rows:

- **MASS:** `h19_5.tif` is binary `{0,1}` with value 1.0 at every R0 dot, so the "ranking" those files used had no ordering. They are a random 10 % perturbation control, **not** a ranking test. See `IRREGULARITIES.md`.
- **CONCENTRATION:** at a fixed count on the 1-px H19-5 skeleton the parent's 2.83 px spacing floor is unattainable (only ~90 legal pixels exist), and at a 2.0 px floor a "10 %" move silently becomes 7.34 % of positions. `CONCENTRATIONphys10` (`MODEL:−0.008`) exists only as the control that says whether a `catblk10up10` win came from the catalogue prior or from reallocation itself.

## Report-only diagnostics (`PROXY`, never gates or scores)

- **DILATATION** (`evidence/dilatation_proxy_audit.json`) — holdout as tabulated above. Leakage canaries, each band tested alone before any result was trusted: Band 8 `0.5145`, Band 7 `0.5128`, Band 4 `0.5102`, Band 15 `0.5149`, Band 17 `0.5060` — max `0.5149 ≪ 0.90` (`REPORT_ONLY_PASS`).
- **SGMC off-catalogue bedrock control** (`n = 62,703` pixels `> 3 px` from the catalogue): R0 `0.096060`; DILATATION p10 `0.083547`, p12 `0.081467`, p15 `0.079888` (`−0.0125` / `−0.0146` / `−0.0162`). Expected: SGMC maps exhumed **range-core** bedrock faults, not dilating piedmonts, so reallocating away from range interiors lowers this control. Recorded as confirmation of genuine geographical reallocation, not presented as a pass.

## How to submit — 3 steps

1. Download the zeros-outside file for the slot you are spending (table above).
2. At <https://www.drivendata.org/competitions/306/competition-doe-gems/data/> (login required) choose **New submission**, select the `.tif` (or a `.zip` containing one GeoTIFF — both are accepted). Do not edit the file.
3. Paste the submission name and form note from the table, submit, and **copy the receipt score into `ledger/submissions.csv`**. That receipt is the only ORGANIZER-CONFIRMED number; holdout and MODEL values are never scores.

## Deterministic reproduction

```bash
pip install -r requirements.txt
python scripts/restore_inputs.py              # SHA-256 + byte-verifies all 12 pins
python scripts/build_dilatation_variants.py   # rebuilds R0 byte-for-byte, builds p10/p12/p15, re-reads, runs gates
python scripts/report_dilatation_proxies.py   # pooled holdout + leakage canaries + SGMC control
make test && make manifest && make verify     # 97 passed · RESULT: OK · PARENT VERIFIED
```
