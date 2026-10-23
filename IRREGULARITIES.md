# Decision-changing irregularities

## 2026-10-23 — BLOCKED at mandatory R0 preflight

- **Local evidence:** at start commit `b99296cae6f52dd1885497e9b9c05efaf85c02fc`, `git ls-tree -r --name-only HEAD` and the working-tree inventory contained only `README.md` (11 bytes). No manifest or equivalent, competition inputs, sample submission, catalogue, parent raster, rebuild recipe, ranking, validator, tests, ledger, raw paste, or slot plan was present.
- **Decision:** no manifest hashes can be verified and R0 cannot be rebuilt or matched to an expected full SHA256. Stop before experiments. Do not approximate the parent, invent historical rows, produce candidate rasters, or infer a usable submission slot. No data hashes were verified; no experiment, metric test, raster validation, proxy evaluation, or submission occurred.
- **Axis:** MASS is selected for a future unblocked run. No `(parent, axis, value)` has been built or reserved; the missing ledger prevents duplicate checks. This is not permission to spend a slot.
- **Evidence status:** the brief's R0 identity `h33-h33-2-b2` (GEMSDOE32), count of 37,654 unit dots, and reported 0.2778 remain **CLAIM**, not RECEIPT. No live result or MODEL prediction was created. TOP_PUBLIC and slot availability are unknown.

### Required private handoff

1. `registry/data_manifest.json` (or the existing equivalent), including expected SHA256 hashes, and every input needed by the recorded R0 recipe. Include `sample_submission.tif`, the exact footprint and catalogue masks or their deterministic derivation inputs, and any parent ranking inputs. External inputs need their source URL and license permitting challenge use and sponsor sharing.
2. The exact R0 reference TIFF, its expected full SHA256 and encoding, and deterministic rebuild code/recipe with dependencies, parameters, fixed seed, original code Git SHA, and stored ranking or its exact reconstruction recipe. A similar raster or a rounded score is not a substitute.
3. `ledger/submissions.csv`, or `ledger/raw_paste.txt` from which to reconstruct it, with historical hashes/axis values and any submission-page receipts; also the existing `SLOT_PLAN.md`, if one exists. Do not reconstruct absent history from the brief's aggregate summary.
4. Dated submission usage sufficient to determine the rolling-week allowance, remaining weekly/final slots, dated TOP_PUBLIC, and a human-provided official deadline confirmation. Never send credentials.

### Access and publication decisions

- `gh repo view --json nameWithOwner,isPrivate,defaultBranchRef` reported `isPrivate: false` for <https://github.com/buffedlizard55-lab/GEMSDOE92>. No competition rasters were found in the initial tracked tree. Competition data-use/publication terms remain unchecked; keep inputs and output rasters off public Git and GitHub releases. Ignore rules are a safeguard, not a license review or protection against force-add.
- The supplied 2026-12-03 deadline is **UNVERIFIED in this session**. No DrivenData, community, Dropbox, leaderboard, or login page was fetched. Official page supplied by the brief: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>; automated-access restriction supplied by the brief: <https://www.drivendata.org/termsofuse/>. Obtain confirmation from the human, not an automated request.
- There was no validator, test suite, or CI configuration in the starting checkout. Documentation/whitespace checks cannot establish raster validity or green scientific CI. Leave the documentation-only PR open; do not merge or nominate an upload.
- The post-creation status of [PR #3](https://github.com/buffedlizard55-lab/GEMSDOE92/pull/3) reported `mergeable: CONFLICTING` and an empty `statusCheckRollup`. Local documentation checks passed with no conflict markers; that does not establish mergeability against the current remote base. Leave the PR open under the brief's merge rule; no merge was attempted.
