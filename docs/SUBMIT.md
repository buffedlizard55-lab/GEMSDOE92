# Candidate handoff — human review and submission only

**Do not upload until you confirm the weekly quota and independently review the selected raster.**
The agent does not submit. The parent score `0.2778` is an owner-reported **CLAIM**, not a
receipt-backed score; there is no receipt-backed best score in this checkout.

## This session: CONCENTRATION (2026-10-23)

All candidates have 37,654 binary unit-mass dots and change only the block allocation of the budget.
Each is a NaN-outside primary plus a zero-outside fallback encoding the same inside-footprint raster —
**upload only one file per slot**. Form notes are 113 characters.

| Order | Local primary raster (NaN outside) | Fallback (`-zeros.tif`) | Submission name | Note | Dots moved | NaN SHA-256 |
|---|---|---|---|---:|---:|---|
| 1 | `releases/h33-h33-2-b2-CONC_C10_b5km-20261023-3127dbd4.tif` | `…-3127dbd4-zeros.tif` | `h33-h33-2-b2-CONC_C10_b5km-20261023-3127dbd4` | `h33-h33-2-b2; CONCENTRATION move 10% of dots from lowest- to highest-prior 5 km blocks; fixed 37654; MODEL:-0.001` | 3,765 (10.00%) | `3127dbd4ca478b4bae5ec7abfeb24631ab3fb770e5e5e35db5f20bf3635c2904` |
| 2 | `releases/h33-h33-2-b2-CONC_C15_b5km-20261023-bb01093f.tif` | `…-bb01093f-zeros.tif` | `h33-h33-2-b2-CONC_C15_b5km-20261023-bb01093f` | `h33-h33-2-b2; CONCENTRATION move 15% of dots from lowest- to highest-prior 5 km blocks; fixed 37654; MODEL:-0.003` | 5,648 (15.00%) | `bb01093fece239dd357015872281fac2873e5044b07a9829bbacbed33f6630f9` |
| 3 | `releases/h33-h33-2-b2-CONC_C20_b5km-20261023-8c425d13.tif` | `…-8c425d13-zeros.tif` | `h33-h33-2-b2-CONC_C20_b5km-20261023-8c425d13` | `h33-h33-2-b2; CONCENTRATION move 20% of dots from lowest- to highest-prior 5 km blocks; fixed 37654; MODEL:-0.005` | 7,531 (20.00%) | `8c425d133b6d824cbd00c325f32e962413cfb26cdcb59f8c1415e32ff4f2f416` |

**Format receipt (identical for all six files, from a disk re-read after writing):** PASS on 10 gates —
CRS EPSG:32611 and transform identical to `sample_submission.tif`; shape 3730×3292; float32, 1 band;
values in [0,1]; no NaN inside the footprint; NaN outside (zeros twin: 0 outside); zero mass on
catalogue pixels; no dot within 2 px of the catalogue (minimum 2.2361 px, R0's own rule); 37,654 dots.

### Recommendation

**No slot is recommended for these three.** No dose is predicted to move the live score by 0.01, and
the two REPORT-ONLY instruments disagree in sign. If you spend one slot anyway, take order 1.

## Mechanism and uncertainty

- **Hypothesis:** the marginal fault yield per dot is higher inside 5 km blocks where the parent's own
  geophysical evidence surface is strong, so moving budget from the weakest to the strongest blocks
  improves distance-tolerant detection.
- **Mechanism:** the 300 m triangular kernel rewards covering continuous, strongly expressed
  lineaments — one dot inside a dense scarp segment converts several truth pixels at once, the regime
  in which a dot pays for its 0.2 denominator cost. R0's Poisson-disk thinning instead spaces dots
  evenly along every H19-5 ridge regardless of expression, so block evidence and block dot count are
  only partly aligned (ρ = +0.82 between block evidence and block dot count, but only +0.12 for
  catalogue-network density).
- **Mimics:** TMI/gravity gradient highs and steep slope also mark lithologic contacts, dikes, caldera
  ring fractures and erosional scarps, so the strongest blocks can be geophysically loud and
  structurally barren.
- **Prediction:** MODEL −0.001 / −0.003 / −0.005 with ranges [−0.021,+0.011] / [−0.023,+0.011] /
  [−0.026,+0.011]. Treat public live changes under 0.01 as no evidence.
- **Report-only diagnostics (never gates):**
  - SGMC off-catalogue control, 62,703 pixels: R0 `0.096060`; deltas `−0.004851`, `−0.007066`,
    `−0.010416`. This is the closer analogue of new-fault truth.
  - Catalogue hide-and-recover, 22,663 withheld positives, paired 20 km block bootstrap: R0 `0.004006`
    `[0.003424,0.004690]`; deltas `+0.001807`, `+0.001853`, `+0.001870`. This scores known catalogued
    faults, which the organisers mask out of the live metric.
  - Leakage canary: maximum symmetric AUC `0.55314` (band 19 slope), below the 0.90 investigate
    threshold. No single feature leaks.
  - Block dot-density CV at 5 km: R0 `0.9014` → `1.1192` / `1.2314` / `1.3422`.
- **Falsifier:** a receipt gain ≥ +0.01 at any dose rejects "R0's block allocation is already locally
  optimal" and vindicates the hide-and-recover instrument over the SGMC control. A loss materially
  worse than the stated ranges shows refill pixels degrade faster than either instrument indicates.

## Reproduction

1. `pip install -r requirements.txt`
2. `python scripts/restore_inputs.py` — all 12 pinned inputs SHA-256 and byte-length verified into
   `.cache/gems_inputs/`.
3. `python scripts/build_concentration_variants.py` — rebuilds R0, refuses to continue unless both
   parent hashes match exactly, builds and re-reads all six rasters.
4. `python scripts/report_proxies.py --receipt evidence/concentration.json --out evidence/proxy_audit_concentration.json`
   then `python scripts/merge_proxy_audit.py` — REPORT-ONLY instruments, folded into the receipt.
5. `python scripts/screen_concentration_priors.py 0.10 0.20` — the prior/dose screen that ordered this
   build (slow; not needed to reproduce the rasters).

`evidence/concentration.json` carries parent hashes, the input-manifest hash, both encoding hashes,
parent diffs, block statistics, the screening table and the merged proxy audit.
`ledger/submissions.csv` keeps the nine earlier rows and appends three `BUILT` CONCENTRATION rows.

**Public-repository safeguard:** competition and candidate TIFFs are gitignored and untracked; the six
local TIFFs are not in the PR. Regenerate them with step 3 if absent — do not substitute another file.
Fill `receipt_score` and `receipt_date` only from the human's submission-page receipt.
