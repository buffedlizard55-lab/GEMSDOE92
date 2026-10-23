# AI_USE

Required by the competition rules (generative-AI disclosure; see the rules PDF at
https://docs.nlr.gov/docs/fy26osti/96647.pdf).

## What the AI wrote

Everything in this repository, in one session on 2026-10-23, under human
direction from the session brief v2:

- `gems/metric.py` — the DTI algebra and exact marginal-gain ranking.
- `gems/variants.py` — the PRUNE / MASS / CONCENTRATION / SNAP / RELIEF builders.
- `gems/gates.py`, `gems/rasters.py` — format gates and GeoTIFF I/O.
- `gems/proxy.py` — the catalogue holdout PROXY and leakage canary.
- `gems/parent.py`, `gems/manifest.py`, `gems/ledger.py`, `gems/cli.py`.
- `tests/` — 38 tests, all passing without any competition data.
- This file, `SLOT_PLAN.md`, `IRREGULARITIES.md`, `docs/SUBMIT.md`, `README.md`.

## What the human decided or supplied

- The parent R0 (`h33-h33-2-b2`) and its 0.2778 `CLAIM`. The AI did not verify
  it and could not: no ledger or receipt was available.
- The choice of session axis (PRUNE) and the slot ordering in `SLOT_PLAN.md`.
  The brief offered a free choice of entity; no axis preference was overridden.
- `TOP_PUBLIC`, the rolling-week slot count, and every scored submission.
- The pinned inputs and their sha256 values (still outstanding — see
  `IRREGULARITIES.md` item 1).

## What was NOT done by AI, and never will be

- No leaderboard access, no scraping, no automated submission, no login.
- No label probing: no region-isolated or patterned file was built to discover
  where public-test faults lie.
- No fabricated numbers. Where a value was unknown (parent hash, TOP_PUBLIC,
  slot count, R0's ranking rule) it was left blank or flagged, not guessed.

## No rasters were produced this session

No candidate raster was built, because the parent could not be reproduced. All
code is unexercised against real competition data; its tests use synthetic
fixtures only.
