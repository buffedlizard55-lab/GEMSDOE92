# Current review pointer — 2026-10-24

The current three-pass review supersedes prior same-day review summaries and “current primary” notes:

- [Full three-pass repository review](REPO_REVIEW_20261024.md)
- [Current status feed](downloads/current_status.json)
- [Current review run card](downloads/current_review_run_card.json)
- [Current hypotheses](HYPOTHESES.md)
- [Current submission guide](SUBMIT.html)

## Decision

**No candidate is cleared; all served TIFFs are research-only; DO NOT SUBMIT; no weekly slot was used.** A byte-verified public registry witness is positive on the complete matching footprint. Under the literal rule, every nonempty in-footprint candidate has REGISTRY-MEASUREMENT forward overlap 1.0 (>0.70). This is a single binding witness, not an exhaustive public-registry scan. No candidate surface or new final dots were generated in this review; no new holdout was run.

## Current checks

After the documentation reconciliation, `.venv/bin/python -m pytest tests -q` → 136 passed (17 existing Rasterio pending-deprecation warnings); `scripts/check_site.py` → all 14 served GeoTIFFs pass; pinned data manifest and parent R0 checks pass; `git diff --check` passes; local HTML relative-link scan reports no broken links; all 85 reviewed JSON files parse. See the full review for commands, evidence, and source-access boundaries.
