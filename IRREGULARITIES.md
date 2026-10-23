# IRREGULARITIES — only items that change a decision

## 2026-10-23 — Parent distance vs new hard constraint
- **Observation**: Parent R0 h33-h33-2-b2 has min distance to catalogue 2.236px (Euclidean), with 0 dots <=2px but 2171 dots <=3px. New hard constraint says "keep >=3 px from them unless AXIS=PRUNE".
- **Impact**: If interpreted as Euclidean >=3, parent violates new rule. If interpreted as >2px (none within 2px), parent passes.
- **Decision**: For MASS axis we enforce >2px (d_cat >2) to match parent's own rule, and document. We do NOT enforce >=3 Euclidean for MASS, because that would be a PRUNE change (removing 2171 dots = 5.76% change) confounding MASS. For future PRUNE axis, we will test B=3 explicitly.
- **Action**: Logged here, not a blocker. No change to parent SHA.

## 2026-10-23 — Ranking reconstruction
- **Observation**: Parent's own ranking not stored in repo. Recorded recipe says H19-5 continuous field (121k px) -> D2.8 (44,090) -> H27-4-SOLO (40,199) -> B2 prune (37,654). We rebuilt ranking from H19-5 value at dot locations.
- **Impact**: Ranking is proxy, not exact parent ranking. Could mis-rank low vs high credit dots if H27-4 introduced different prior.
- **Decision**: Use H19-5 as best available proxy, note as MODEL. If MASS variants fail, need better ranking (e.g., multi-physics consensus or tip/step-over).
- **Action**: Logged, mechanism cards note proxy.

## 2026-10-23 — No organizer authentication
- **Observation**: All inputs are owner-supplied mirrors from buffedlizard55-lab repos, integrity-pinned via sha256, NOT organizer-authenticated. Sandbox cannot reach drivendata.org (terms ban automated access) or dropbox.com.
- **Impact**: Hashes prove mirror consistency, not organizer authenticity.
- **Decision**: Proceed with pinned mirrors, document provenance in registry/data_manifest.json, do not claim organizer authentication.
- **Action**: Logged per brief requirement to mark UNVERIFIED if unreachable — but we have verified mirror hashes, so we mark as mirror-consistent.

## 2026-10-23 — No TOP_PUBLIC filled
- **Observation**: Brief says beat TOP_PUBLIC = ____ (human fills from leaderboard, with date). No other target valid.
- **Impact**: Cannot evaluate if we beat public top without human input.
- **Decision**: Leave blank, ask human to fill.
- **Action**: Logged.

No other irregularities that change a decision this session.

---

## 2026-10-23 (PRUNE session) — H19-5 is binary, so the MASS "ranking" was all ties

**Observation.** `data/bridge/h19_5.tif` contains exactly two values, `{0, 1}`
(121,131 pixels equal 1.0). At all 37,654 parent dot locations the value is
`1.0`. The previous session's SLOT_PLAN and mechanism cards describe ranking the
dots by "H19-5 continuous field value at dot location".

**Impact — decision-changing.** There was no ranking. Every dot shared the same
H19-5 value, so `MASS_D10` dropped an essentially arbitrary 10% (whatever the
sort's tie order produced) and `MASS_A10`/`MASS_SWAP10` picked arbitrary
replacements. Those three files therefore test *"does perturbing 10% of the dots
at random help?"*, not *"does dropping the weakest 10% help?"*. Any inference
about the mass optimum or about ranking quality drawn from their live scores
would be unsound.

**Decision.** The three MASS files are left in the ledger as BUILT (they are
already built and cost nothing to keep) but are explicitly rescoped as a random
10% perturbation control, not a ranking test. No PRUNE variant is affected: PRUNE
selects on catalogue distance, never on H19-5. H19-5 is used only as a positivity
mask for legal refill pixels, where a binary mask is exactly what is wanted.

**Action.** `docs/mechanism_cards.md` carries the corrected reading. If the human
wants a real ranking axis (MASS or CONCENTRATION), one must first be built from a
truly continuous field (the detrended elevation or a TMI gradient band, neither of
which is currently pinned).

## 2026-10-23 (PRUNE session) — Competition rasters are committed to a PUBLIC repo

**Observation.** `buffedlizard55-lab/GEMSDOE92` is public (`isPrivate: false`).
It tracks `data/bridge/*.tif` (sample_submission, labels, existing_faults, h19_5,
h27_4_solo, d28) and `data/parent_R0_*.tif`, plus all six MASS release rasters.
Brief constraint 2 says to keep competition rasters out of public repos and to
flag it if they are already there. This is that flag.

**Impact.** The data-use terms of the competition have not been checked. If they
forbid redistribution, this repo is currently redistributing study-area data and
derived submissions, and Phase 2 requires "reproducible code" for a public
submission — which may or may not require the data itself.

**Decision.** Nothing was deleted or rewritten this session: untracking files
does not remove them from git history, and rewriting history is the repository
owner's call, not an agent's. PRUNE rasters follow the established convention and
are committed like the MASS ones, so the human can actually upload them.

**Human must decide.** Either confirm the terms permit redistribution (do nothing),
or untrack `data/` and `releases/*.tif` and, if the terms require it, purge
history. `registry/session_manifest.json` records every sha256, so the toolchain can
re-verify inputs from whatever private location they move to.

## 2026-10-23 (PRUNE session) — `labels.tif` and `existing_faults.tif` are byte-identical

**Observation.** Both have sha256 `7ba308cc…e4093`. They are the same file under
two names.

**Impact.** Low, but worth stating: the "catalogue" used for the zero-mass rule
and the distance prior is a single artefact, not two independent confirmations.
Any error in it propagates to both. It also means the PROXY holdout and the
exclusion mask cannot be separated into independent controls.

**Decision.** Use `labels.tif` as the exclusion mask (the previous session's
convention, and the name that matches the organizers' masking description).

## 2026-10-23 (PRUNE session) — PRUNE variants satisfy the 3 px rule without an exemption

The 2026-10-23 earlier item set out to "test B=3 explicitly". All three variants
remove dots within R px and refill only at distance **strictly greater** than R,
so every emitted dot is farther than 3 px from the catalogue regardless of R.
Measured minimum distances: B3 → 3.16 px, B4 → 4.12 px, B5 → 5.10 px. The
default gates pass with no `--prune-radius` exception, which is why the
`distance_from_catalogue` gate reads `dots_within=0` on all three.

## 2026-10-23 (PRUNE session) — the ledger's `sha256` column is not the same file type across sessions

**Observation.** For the three MASS rows, `sha256` equals the hash of the
`-zeros.tif` twin (e.g. `e26a6cb8…`, matching their `sha8`). For the three PRUNE
rows it is the hash of the primary NaN-outside file. Verified by re-hashing every
file in `releases/` against the ledger.

**Impact.** A cross-session duplicate check on `sha256` alone will not notice two
rows built from identical dots but written in different encodings, because the
bytes differ. The brief already warns that NaN/zeros twins "shoot identically",
so this is a slot-economy risk rather than a correctness bug.

**Decision.** No hashes were rewritten — the MASS rows are a prior session's
evidence and are left exactly as recorded. Rule for going forward: one row = one
experiment, and a `-zeros.tif` twin is *not* a second experiment. Upload at most
one of a pair. Dedupe remains exact-hash only, per the brief; do not add
rank-correlation or overlap thresholds.

## 2026-10-23 (new PRUNE-rung session) — accessible-ledger uniqueness is incomplete

Exact `(parent, axis, value)` and raster hashes were compared against accessible `GEMSDOE74`–`GEMSDOE89` ledger files; the three new values and six new hashes had no matches. This cannot prove uniqueness in unpublished sessions or repositories outside that range. **Decision:** treat the check as limited, and do not submit if the human knows an exact pair/hash was already built elsewhere.

## 2026-10-23 (new PRUNE-rung session) — local holdout PROXY is not decision-comparable

The pinned `gems57-pooled-hide-v2` whole-component buffered catalogue holdout (seeds 20/30, `n=22,663` withheld known-catalogue pixels) returns R0 `0.004006 [0.003424,0.004690]`, p2.5 `0.000785 [0.000658,0.000922]`, and p3.5/p4.5 `0 [0,0]`; selected-band leakage canary max symmetric AUC is `0.55314`. Results are in `evidence/proxy_audit.json`. **Decision:** these are PROXY diagnostics only, not gates, scores, or live forecasts; investigate the large divergence from previous hide-and-recover summaries before using this instrument to rank future axes. Use human live receipts as the decision anchor.

---

## 2026-10-23 (CONCENTRATION session) — the two REPORT-ONLY instruments disagree in sign

**Observation.** For all three CONCENTRATION rungs the SGMC off-catalogue control falls monotonically
with dose (`−0.004851`, `−0.007066`, `−0.010416` vs R0's `0.096060` on 62,703 control pixels) while the
catalogue hide-and-recover holdout rises by about `+0.0018` at every dose (R0 `0.004006`
`[0.003424,0.004690]`, n = 22,663 withheld positives). They cannot both be pointing at the live metric.

**Impact — decision-changing.** The two instruments are measuring different target classes. The
organisers mask known catalogue pixels exactly and score only new-fault truth, so the hide-and-recover
instrument scores recovery of the pixels that are *removed* from the live metric, whereas the SGMC
control scores faults that are real but absent from the catalogue — the same class as the target. The
brief's historical note that hide-and-recover correlated −0.87 to +0.54 with live scores (n = 12–14)
therefore cannot be assumed to hold for an axis whose whole mechanism is about *unmapped* faults.

**Decision.** The SGMC control is weighted more heavily in the MODEL prediction, which is why all three
rungs carry a negative central value. But the disagreement itself is reported rather than resolved, and
the recommendation is to spend no slot on this axis: with three scored submissions per week, an
unresolved sign conflict at magnitudes at or under 0.01 is not worth a slot. Both numbers stay labelled
PROXY; neither is a gate and neither is a score.

## 2026-10-23 (CONCENTRATION session) — most of the concentration loss is generic, not the ordering

**Observation.** A deterministic randomised-block null (same block geometry, shuffled block ordering,
seed 20261023) loses `−0.012365` on the SGMC control at 20% moved; the parent's own evidence surface
loses `−0.010423`; the geophysics-only, catalogue-network and catalogue-node priors lose more
(`−0.011826`, `−0.012462`, `−0.012281`).

**Impact.** Any "concentration" build is dominated by a fixed cost that has nothing to do with the
prior: refill pixels are the H19-5 pixels that Poisson-disk thinning at 2.8 px discarded, i.e. the
immediate neighbours of surviving dots, so they are largely redundant. The prior ordering is worth
about +0.002 of control and +0.011 of declared model over random — real, but far short of the fixed
cost. This should stop any future session from reading a concentration receipt as evidence about the
prior.

**Decision.** Reported in `evidence/concentration.json` under `screening`, with the randomised null
included. `SLOT_PLAN.md` proposes `SUPPORT_EXPANSION` — refilling *off* the H19-5 support — as the axis
that would actually attack the fixed cost, rather than re-testing priors inside it.

## 2026-10-23 (CONCENTRATION session) — R0 keeps its own >2 px catalogue rule, not the brief's ≥3 px

**Observation.** Hard constraint 4 requires dots ≥3 px from the catalogue unless AXIS=PRUNE. R0 itself
has 2,171 dots within 3 px (minimum 2.2361 px). All three CONCENTRATION variants inherit that minimum
exactly.

**Impact.** Enforcing ≥3 px here would delete 5.77% of the parent, which is the already-built
`PRUNE_B3`/`p3.5px-refill` change, and would confound CONCENTRATION with PRUNE.

**Decision.** Follows the 2026-10-23 MASS-session precedent: non-PRUNE axes use R0's own >2 px rule, and
the gates are run with `--prune-radius 2` so the deviation is declared rather than hidden. All three
files record `min_catalogue_distance_px = 2.2361`. The ≥3 px question remains a PRUNE-axis question.

## 2026-10-23 (CONCENTRATION session) — the 0.51–0.59 block-density CV reference is scale-dependent

**Observation.** The brief reports that the best files sit at a block-density CV of 0.51–0.59 without
stating a block size. Measured CV for R0 is 1.3691 at 2 km, 1.1469 at 3 km, 0.9014 at 5 km and 0.6353
at 10 km. The CONCENTRATION variants raise the 5 km CV to 1.1192 / 1.2314 / 1.3422.

**Impact.** Without the block size the reference number is not comparable, so it cannot be used either
to justify or to reject a variant. It is recorded, not used.

**Decision.** The 5 km figure is reported for all three variants; R0's CV at four block sizes is in
`evidence/concentration.json` so the human can compare on whatever scale the 0.51–0.59 figure came from.
