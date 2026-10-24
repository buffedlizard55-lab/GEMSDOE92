# releases/

Candidate rasters live here **locally** and are gitignored (see
`../IRREGULARITIES.md` item 4). Each build produces two files from one dot set:

- `<id>.tif` — NaN outside the footprint (primary upload)
- `<id>-zeros.tif` — 0.0 outside the footprint (fallback if the uploader
  rejects NaN)

`<id>` = `<parent>-<axis><value>-<yyyymmdd>-<sha8>`, e.g.
`h33-h33-2-b2-RELIEFbasin11pct-20261024-2d06de50`.

As of 2026-10-24 this folder holds 18 built experiments across `ledger/submissions.csv`
(3 MASS, 6 PRUNE, 6 SNAP, 3 RELIEF), each reproducible as a NaN/zeros pair from
its deterministic build script, pinned input SHA-256 digests, fixed seed, and
logged git SHA.
