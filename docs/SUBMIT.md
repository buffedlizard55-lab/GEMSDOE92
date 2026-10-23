# Submission handoff

**STOP — no candidate is available or authorized for upload.**

| Required field | Current state |
| --- | --- |
| Candidate file / fallback | None built; no release artifacts |
| Submission name | Not assigned |
| Form note (at most 140 characters) | Not applicable; no experiment built |
| Parent | `h33-h33-2-b2` per brief; exact rebuild and SHA256 match blocked |
| Selected session axis | MASS; no values built or checked against history |
| Input-hash verification | BLOCKED: manifest and inputs missing |
| Format receipt | NOT RUN: sample submission, footprint and raster missing |
| Catalogue exclusion / zero mass | NOT RUN: catalogue and raster missing |
| Ledger/hash and axis-value de-duplication | BLOCKED: ledger/raw paste missing |
| Parent-diff statistics / reread | NOT RUN: parent and candidate missing |
| PROXY, leakage canary, SGMC control | NOT RUN; no measurements available |
| Live receipt / dated TOP_PUBLIC | None supplied |
| Available slots / official deadline | Unknown / not independently confirmed |

See `IRREGULARITIES.md` for the exact private handoff. No ledger has been fabricated from the aggregate claims in the brief.

After the stop condition is resolved, candidates must come from deterministic scripts and pinned inputs, carry the build Git SHA and full SHA256, pass the specified gates, be reread from disk, and receive mechanism cards and exact parent-diff statistics. Unit-test the supplied DTI algebra before using it. Report optional local diagnostics honestly; a single-feature leakage canary above 0.90 requires investigation before proceeding.

The repository is public. Keep competition inputs, `releases/<id>.tif` and `<id>-zeros.tif` in private/local storage, not commits or public GitHub releases. Record their hashes and validation receipts in text. The human uploads only one encoding per available slot from their own account; this agent never logs in or submits. The human records the dated submission-page receipt afterward.
