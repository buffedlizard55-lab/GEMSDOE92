# releases/

Candidate rasters live here **locally** and are gitignored (see
`../IRREGULARITIES.md` item 4). Each build produces two files from one dot set:

- `<id>.tif` — NaN outside the footprint (primary upload)
- `<id>-zeros.tif` — 0.0 outside the footprint (fallback if the uploader
  rejects NaN)

`<id>` = `<parent>-<axis><value>-<yyyymmdd>-<sha8>`, e.g.
`h33-h33-2-b2-PRUNEle3px-20261024-1a2b3c4d`.

Current-session CONCENTRATION candidates are generated locally after an exact
R0 rebuild. Every file is reproducible from its ledger row and
`evidence/concentration_session.json` (parent, axis, value, parameters, input
hashes, deterministic rule, and Git SHA). New rasters remain gitignored; older
tracked rasters are a flagged inherited public-repository issue.
