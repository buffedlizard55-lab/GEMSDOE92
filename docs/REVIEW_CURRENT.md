# Current review pointer — 2026-10-24

This three-pass review supersedes earlier same-day summaries and any stale “current primary” notes:

- [Full three-pass repository review](REPO_REVIEW_20261024.md)
- [Current machine-readable status](downloads/current_status.json)
- [Current review run card](downloads/current_review_run_card.json)
- [Current ranked hypotheses](HYPOTHESES.md)
- [Submission guide](SUBMIT.html)

## Decision

**No candidate is cleared; all 15 served TIFFs are research-only; DO NOT SUBMIT; no weekly slot was used.** The literal registry rule is blocked by one byte-verified public witness positive on all 5,167,373 cells of the matching footprint. Every nonempty in-footprint prediction has REGISTRY-MEASUREMENT forward overlap 1.0 (>0.70). This single witness is binding for rejection, not an exhaustive public-registry scan. No new candidate or holdout was generated in this review.

The latest prior research artifact is **SPRINGALIGN f33Ctop**, inherited from upstream PR #42, not generated in this review. Its saved **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives) is 0.0048650690, 95% CI [0.0040254482, 0.0057850159], with paired Δ vs saved RELIEF p10 best −0.0011800634, 95% CI [−0.0020652571, −0.0003371520]. It is negative and below the saved best; the public witness independently blocks it. Its `20261025` filename date is unverified because the saved run card lacks a generation timestamp.

## Current checks

- `.venv/bin/python -m pytest tests -q` → **140 passed**, 17 existing Rasterio pending-deprecation warnings.
- `.venv/bin/python scripts/check_site.py` → **15/15 served zeros-outside TIFFs pass** reread, format gates, and page contract; SPRINGALIGN is first and its exact bytes match the saved audit/run card.
- `PYTHON=.venv/bin/python make manifest verify` → pinned data manifest **PASS** and parent R0 **PARENT VERIFIED**.
- Local relative-link scan → **5 HTML files, zero broken targets**; **93 JSON files** under `docs/`, `evidence/`, and `registry/` parse.
- Staged and working-tree whitespace checks using `git -c core.whitespace=cr-at-eol ... --check` → **PASS**; this honors the ledger’s existing CRLF line endings.

See the full review for the three passes, evidence labels, data-access limits, conflicting score snapshots, and source-verification boundaries. The project does not select a weekly slot or upload on the competitor’s behalf.
