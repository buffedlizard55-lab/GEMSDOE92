# releases/

Candidate rasters live here **locally** and are gitignored (see
`../IRREGULARITIES.md` item 4). Each build produces two files from one dot set:

- `<id>.tif` — NaN outside the footprint (primary upload)
- `<id>-zeros.tif` — 0.0 outside the footprint (fallback if the uploader
  rejects NaN)

`<id>` = `<parent>-<axis><value>-<yyyymmdd>-<sha8>`, e.g.
`h33-h33-2-b2-PRUNEle3px-20261024-1a2b3c4d`.

Nothing is here yet: no parent could be rebuilt, so no variant was built.
Every file is reproducible from its ledger row (parent, axis, value, params,
input hashes, seed, git SHA), which is why the rasters themselves need not be
committed.
