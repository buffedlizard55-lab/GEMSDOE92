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
