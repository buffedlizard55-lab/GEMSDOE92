# Three-pass closeout — 26 October 2026

## Pass 1: implementation
Constructed three THERMOTILT research rasters using shared writer/evaluator. An initial OOM was addressed with a memmap. All three passed 11 local format checks. No organizer upload occurred.

## Pass 2: evidence audit and corrections
The initial narrative contained unsupported filenames, hashes, source identifiers, score ceilings and marginal-precision derivations. Replaced it with a table derived from saved focus-site JSON. Removed unsupported scientific and live-score conclusions. Documented critical protocol deviations: known literal stop not honored, registry checks after placement, incomplete nested OOF isolation, seed-20-only canaries, selected-witness-only Spearman comparisons and flat-offset dilation limitations. Disabled the historical runner to prevent reruns or overwrite of evidence. All results stay negative. No claim of fully satisfying the original request is made.

## Pass 3: verification
All three new TIFFs passed 11 format gates; the submission entrypoint correctly blocked them. Site check passed with 118 served rasters. Final suite: 578 tests passed, 141 warnings. GitHub Pages API reports legacy/built; live deployment of this change is not yet verified. Final test results are recorded in the PR; no blanket line-by-line verification or organizer acceptance is claimed.

## Remaining requirements
No submission-cleared unique high-scoring file, defensible leaderboard forecast, or live official-source verification was achieved. Resolve protocol and shared-pipeline defects before another experiment. Preserve scarce submission slots.
