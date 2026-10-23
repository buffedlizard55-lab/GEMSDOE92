# Candidate handoff — human review and submission only

**Do not upload until you confirm rolling-week quota and independently review the raster.** The agent does not submit. R0's `0.2778` is an owner-reported **CLAIM**, not a receipt. `TOP_PUBLIC` and remaining slots are unknown. Current SGMC **PROXY** evidence is negative for all three arms; this is a conditional falsification queue, not a recommendation to spend slots.

Every candidate has 37,654 unit-mass dots, zero catalogue mass, minimum catalogue distance 3.162278 px, and passes all 10 local gates after re-reading both encodings from disk. Upload only one of the NaN-outside primary and zero-outside fallback for any slot. Notes are ≤140 characters.

| Order | Primary raster (NaN outside) | Fallback | Submission name | Form note | Moved | NaN SHA-256 | Format receipt |
|---|---|---|---|---|---:|---|---|
| 1 | `releases/h33-h33-2-b2-CONCENTRATIONblk1km-f10-20261023-af953ada.tif` | `releases/h33-h33-2-b2-CONCENTRATIONblk1km-f10-20261023-af953ada-zeros.tif` | `h33-h33-2-b2-CONCENTRATIONblk1km-f10-20261023-af953ada` | `h33-h33-2-b2; CONC 1km f10; moved 3765 (10.00%); fixed 37654; pred MODEL:+0.001` | 3,765 (9.998938%) | `af953adaee32d1f39e85e015dd0c50219fcb68cee7818725ab5a27467806f071` | PASS: EPSG:32611; 3730×3292; exact transform; float32; 1 band; finite inside; NaN outside; [0,1]; 37,654 dots; no catalogue mass; 0 dots ≤3 px. |
| 2 | `releases/h33-h33-2-b2-CONCENTRATIONblk1km-f15-20261023-72f02044.tif` | `releases/h33-h33-2-b2-CONCENTRATIONblk1km-f15-20261023-72f02044-zeros.tif` | `h33-h33-2-b2-CONCENTRATIONblk1km-f15-20261023-72f02044` | `h33-h33-2-b2; CONC 1km f15; moved 5648 (15.00%); fixed 37654; pred MODEL:+0.002` | 5,648 (14.999734%) | `72f02044efdd2b38a29aa938cd412035c37dd96c49a5c08eed4cc0c67a927574` | Same 10-gate PASS; zero-outside fallback independently re-read and passed. |
| 3 | `releases/h33-h33-2-b2-CONCENTRATIONblk1km-f20-20261023-22404075.tif` | `releases/h33-h33-2-b2-CONCENTRATIONblk1km-f20-20261023-22404075-zeros.tif` | `h33-h33-2-b2-CONCENTRATIONblk1km-f20-20261023-22404075` | `h33-h33-2-b2; CONC 1km f20; moved 7531 (20.00%); fixed 37654; pred MODEL:-0.001` | 7,531 (20.000531%) | `22404075800bf16d3ebe9a76126e070f132ca2226cdf918591551be718849dfa` | Same 10-gate PASS; zero-outside fallback independently re-read and passed. |

## Mechanism and contrary evidence

- **Mechanism:** relocate fixed-count dots from lower to higher mean multiphysics-response 1 km blocks, retaining H19-5 support. All arms share 2,171 mandatory catalogue-clearance movers; destination selection is nearest block centre, not SNAP or truth/DTI ranking.
- **Mimic:** lithologic contacts, basin-fill density contrasts, intrusions, and erosional scarps can raise the block prior without new faults.
- **Prospective MODEL predictions:** recorded before diagnostics in the ledger; they are not scores. Live changes below 0.01 are no evidence.
- **SGMC PROXY (62,703 control pixels):** R0 `0.096060`; f10 `0.091628` (`−0.004432`); f15 `0.087697` (`−0.008363`); f20 `0.083890` (`−0.012170`). This monotone warning opposes promotion.
- **Catalogue holdout PROXY:** `n=22,663`; R0 `0.004006 [0.003424,0.004690]`; every candidate `0 [0,0]`, structurally forced by >3 px catalogue clearance. It is not a ranker or gate.
- **Leakage canary:** maximum symmetric AUC `0.55314`, below the 0.90 stop-and-investigate threshold.

## Reproduction and local format receipt

1. `python -m pip install -r requirements.txt`
2. `python scripts/restore_inputs.py` (every pinned input is SHA-256/byte checked before use).
3. `python scripts/build_concentration_variants.py` (rebuilds R0 and stops unless both parent hashes match exactly).
4. `python scripts/report_proxies.py --receipt evidence/concentration_session.json --output evidence/concentration_proxy_audit.json --candidate blk1km-f15`

`evidence/concentration_session.json` records both encoding hashes, exact parent diffs, CV, gates, mechanism cards, builder Git SHA `3133962301df56a8b234430c300de17bae481dff`, and form notes. New TIFFs are local and gitignored; regenerate them if absent rather than substituting another file. Fill `receipt_score` and `receipt_date` only from the human's submission-page receipt.
