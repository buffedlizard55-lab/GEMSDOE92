# GEMSDOE92

Candidate-raster toolkit for DrivenData **#306 GEMS** (DOE Geothermal Machine
Learning Challenge), built for one human competitor. This repo builds and
validates candidate rasters. It never submits, never logs in, never scrapes.

<!-- CURRENT STATE: the only block a routine session edits -->

## CURRENT STATE

| field | value |
|---|---|
| Parent (R0) | `h33-h33-2-b2` (GEMSDOE32) — 37,654 unit-mass dots, none within 2 px of the catalogue |
| Best receipt | **none yet.** 0.2778 is a `CLAIM` (owner-reported, no receipt in `ledger/`) |
| TOP_PUBLIC | `____` — **human must supply from the leaderboard, with date** |
| Slots left this week | `__` of 3 (human must supply; nothing in this repo can know it) |
| Next 3 slots | 1. `PRUNE-le3px`  2. `CONCENTRATION-blk10px`  3. `MASS-drop10` — see `SLOT_PLAN.md` |
| Session axis | PRUNE (spine: cheapest test of the only receipt-backed mechanism) |
| Status | **BLOCKED**: no pinned inputs, no parent recipe, no ledger in repo. Zero rasters built. |

<!-- END CURRENT STATE -->

## Why nothing was built this session

The brief's opening gate is: verify manifest hashes, rebuild R0, match its
sha256, *or stop and report — never approximate the parent*. On this checkout
there is no `registry/`, no `ledger/`, no `SLOT_PLAN.md`, and no data directory.
`main` is a single commit containing an 11-byte README. So the gate cannot run,
and per the brief the correct move is to stop rather than invent a parent.
Details in `IRREGULARITIES.md` items 1-2.

What this repo does contain is the machinery that makes the next session fast:
a tested implementation of the metric algebra, the axis builders, the MUST-pass
format gates, and the ledger. All 38 tests pass with no competition data.

## Setup

```
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
make test          # 38 tests, no data required
```

Then, once the inputs exist: `make manifest && make verify`.

## Layout

```
gems/metric.py     DTI algebra, exact marginal gains (T/S/M/G), dot ranking
gems/variants.py   one-axis-at-a-time builders: PRUNE MASS CONCENTRATION SNAP RELIEF
gems/gates.py      MUST-pass format gates (CRS/shape/transform/dtype/range/NaN/catalogue)
gems/proxy.py      REPORT-ONLY catalogue holdout PROXY + leakage canary
gems/rasters.py    float32 GeoTIFF I/O, NaN-outside and zeros-outside encodings
gems/parent.py     parent rebuild + sha256 verification (refuses to approximate)
gems/manifest.py   pinned-input hash verification
gems/ledger.py     ledger CSV, dedupe, evidence labels, slot counting
gems/cli.py        `python -m gems {validate,manifest,parent,ledger}`
registry/          data manifest + parent recipes  (TEMPLATES ONLY — see below)
ledger/            submissions ledger               (empty — waiting on data)
```

## What the human must supply before any raster can exist

The toolbox is deliberately data-free. To unblock, provide:

1. `registry/data_manifest.json` — path + sha256 for every pinned input
   (`sample_submission.tif`, the fault catalogue raster, and any band used by an
   axis). Start from `registry/data_manifest.template.json`.
2. `registry/parents/R0.json` — the R0 recipe, **including `expected_sha256`**.
   Without the recorded hash there is no way to prove a rebuild is the parent.
3. `ledger/submissions.csv` or `ledger/raw_paste.txt` — the score history, so
   dedupe and slot accounting work.
4. `TOP_PUBLIC` and the slot count above.

Then: `make test && make verify` reproduces the parent, or refuses and says
exactly which input failed.

## Rules of the road

- Every raster comes from a script, pinned inputs, a fixed seed, a logged git SHA.
- Zero mass on catalogue pixels; >= 3 px from them unless the axis is PRUNE.
- A live change under 0.01 is not evidence (public chunks only).
- `PROXY` and `MODEL` are never called a score. See `docs/SUBMIT.md`.
- Human submits from their own account. This code cannot.
