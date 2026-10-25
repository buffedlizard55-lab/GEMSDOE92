# ledger/

`submissions.csv` is the single source of truth for what was built and scored.

Columns: `id, parent, axis, value, n_dots, pct_changed, sha256, status,
predicted_change, receipt_score, receipt_date, notes`.

- A score with a `receipt_date` is a **RECEIPT**. A score without one is a
  **CLAIM** and never counts toward the best score. `python -m gems ledger`
  reports the two separately.
- `raw_paste.txt` (optional) accepts the columns
  `site, name, score, encoding, n_dots, sha8, parent, receipt`; import it with
  `gems.ledger.import_raw_paste`, which collapses exact repeats.
- Dedupe is exact-hash only, plus repeated `(parent, axis, value)`. No
  rank-correlation or dot-overlap "uniqueness" thresholds are applied, per the
  brief.

Currently empty: no receipt was available, so R0's 0.2778 remains a CLAIM and
has not been entered as a score.

This PR appends three BUILT PRUNE-rung rows to the existing ledger without removing earlier MASS or PRUNE rows. `evidence/prune_rungs.json` contains both encoding hashes; candidate rasters are local-only and gitignored. `ledger/raw_paste.txt` and `historical_climb.csv` retain the original prompt's owner-reported historical claims separately; none is receipt-backed.

## `site_scores_claimed_20261025.csv`

Every `GEMSDOE*` site/score pair listed in the 2026-10-25 session brief (119 rows, 115 with a score; max `0.2778` = `GEMSDOE32 h33-h33-2-b2`; median `0.0843`). All are `CLAIM` — owner-reported, no organizer receipt in this repository. Sites `GEMSDOE86/88/91/92` were listed with an empty score. Use for learning only; never as holdout or organizer evidence.
