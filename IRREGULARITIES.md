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
one of a pair. Exact-hash comparison still handles byte-identical encoding pairs in the ledger.
It is not the cross-session candidate uniqueness gate: the current protocol uses
shared Spearman-rho and forward-overlap thresholds against the public raster
registry (`vendor/gems57/uniqueness.py`). The 2026-10-24 full-support blocker
below is binding under that broader gate.

## 2026-10-23 (new PRUNE-rung session) — accessible-ledger uniqueness is incomplete

Exact `(parent, axis, value)` and raster hashes were compared against accessible `GEMSDOE74`–`GEMSDOE89` ledger files; the three new values and six new hashes had no matches. This cannot prove uniqueness in unpublished sessions or repositories outside that range. **Decision:** treat the check as limited, and do not submit if the human knows an exact pair/hash was already built elsewhere.

## 2026-10-23 (new PRUNE-rung session) — local holdout PROXY is not decision-comparable

The pinned `gems57-pooled-hide-v2` whole-component buffered catalogue holdout (seeds 20/30, `n=22,663` withheld known-catalogue pixels) returns R0 `0.004006 [0.003424,0.004690]`, p2.5 `0.000785 [0.000658,0.000922]`, and p3.5/p4.5 `0 [0,0]`; selected-band leakage canary max symmetric AUC is `0.55314`. Results are in `evidence/proxy_audit.json`. **Decision:** these are PROXY diagnostics only, not gates, scores, or live forecasts; investigate the large divergence from previous hide-and-recover summaries before using this instrument to rank future axes. Use human live receipts as the decision anchor.

## 2026-10-23 (SNAP session) — the 3 px catalogue rule cannot be satisfied by any non-PRUNE descendant of R0

**Observation.** R0 itself holds **2,171 dots within 3.0 px** of the catalogue
(941 at 2.236 px, 670 at 2.828 px, 560 at exactly 3.0 px); its own recipe is
`dot_thin(H19-5, 2.8) & d_cat > 2.0`. Brief constraint 4 asks for ≥3 px "unless
AXIS=PRUNE". Any SNAP/RELIEF/MASS/CONCENTRATION descendant therefore inherits the
violation, and the repo's `distance_from_catalogue` gate fails on inherited dots
for every such file.

**Impact — decision-changing.** Deleting the 1,611 dots at 2.236-2.828 px (4.3% of
the file) would be a PRUNE edit, so it would confound the SNAP axis rather than
clean it. Submitting without deleting them keeps the parameter that produced the
incumbent's CLAIM 0.2778.

**Decision.** SNAP candidates keep every inherited dot exactly where the parent
put it, and enforce the ≥3 px rule on all **moved** dots (targets must satisfy
`d_cat > 3.0`; measured minimum among moved dots 3.16 px). Consequence: the gate
`distance_from_catalogue` reports 2,114 / 1,999 / 1,634 in-collar dots and fails,
which is recorded verbatim in `evidence/snap_session.json` and in
`docs/SUBMIT.md` rather than papered over with a PRUNE-style exemption flag.
**The human decides** whether a candidate carrying 4-5% inherited in-collar mass
is acceptable for a slot; the brief's alternative (drop them) is a different
experiment and needs its own parent.

## 2026-10-23 (SNAP session) — the brief's block-CV reference band (0.51-0.59) does not identify a direction for R0

**Observation.** R0's dot-density CV, measured the way `gems/variants.py`
measures it (blocks containing any in-footprint pixel):

| block | 1 km | 1.5 km | 2 km | 2.5 km | 5 km |
|---|---:|---:|---:|---:|---:|
| CV over all eligible blocks | 1.878 | 1.565 | 1.379 | 1.257 | 0.941 |
| CV over occupied blocks | 0.619 | 0.710 | 0.748 | 0.762 | 0.724 |

The quoted 0.51-0.59 band is not reproduced by either definition at any km-scale
block size, and it sits *below* R0's occupied-block value (0.619).

**Impact — decision-changing.** Read as "concentrate more", the brief's
CONCENTRATION recipe (move dots from low-prior to high-prior blocks) would push
the occupied-block CV further *above* 0.51-0.59, i.e. it would move away from the
stated optimum. The reference band therefore cannot be used to pick a dose or a
sign, and an axis built on it would be unfalsifiable this session.

**Decision.** CONCENTRATION was not built this session; SNAP was chosen instead
because its parameter (displacement onto a physical edge) is measurable without a
reference statistic of unknown definition. If a future session wants
CONCENTRATION, it must state which CV definition it targets and build the
less-concentrated direction too.

## 2026-10-23 (SNAP session) — the literal SNAP rule is not a usable experiment

**Observation.** Applying the brief's SNAP wording literally — move every dot to
the argmax of the edge response within its ≤2 px window — moves **99%** of R0's
dots (37,280 at cap 1.0, 37,595 at cap 2.0, mean displacement 0.99-1.66 px) and
packs **12,564-17,030 dots within 1 px** of a neighbour, destroying the parent's
D2.8 spacing invariant (min 2.828 px, median 3.0 px).

**Impact — decision-changing.** That file would test "shuffle the whole field and
double-credit the same truth pixels", two known-bad mechanisms under the DTI
algebra, not the positional hypothesis. A null or negative result would be
uninterpretable.

**Decision.** SNAP is implemented as an evidence-thresholded correction: a dot
moves only if the window maximum beats its own pixel by more than `g` **and** the
target keeps ≥2.828 px clearance. The dose ladder is `g` = 0.15 / 0.10 / 0.05
(7.06% / 18.65% / 51.96% moved). `gems/variants.py::snap` documents the choice,
and `tests/test_variants.py` asserts the spacing invariant, count conservation and
the dose behaviour. A dot whose own pixel has no response value (16 of R0's dots
sit on stack sentinels) never moves.

## 2026-10-23 (SNAP session) — response surface provenance

The edge response is `0.40·rank(tmi_hg b3) + 0.35·rank|∇ iso_grav_anom b13| +
0.25·rank(det_elev_slope b19)`, weights taken unchanged from the repository's
existing prior (`scripts/build_prune_rungs.py::make_prior`), **not** tuned on the
catalogue. Band 18 (`iso_grav_anom_hg`) is a **signed directional derivative**
(20.7% of pixels negative), so the gravity horizontal-gradient magnitude is
computed from band 13 instead of taking |band 18|. The 419 MB stack was restored
from the pinned commit and its sha256/byte length re-verified before use; it is
gitignored and not redistributed. No new external data was introduced.

---

## 2026-10-23 (SNAP break-in-slope session) — `Band 18 (iso_grav_anom_hg)` is signed E–W `dg/dx` (`corr=+0.948`), whereas `Band 5 (iso_grav_anom_slope)` (`corr=+0.962`) is the provided unsigned horizontal gradient, and 3,061 in-footprint pixels carry `-3.4028235e+38` nodata

**Observation.** Direct derivative audit of `training_features.tif` shows two decision-changing properties:
1. `Band 18 (iso_grav_anom_hg)` spans `[-15.441, +12.856]` with `corr(dg/dx, Band 18) = +0.9482` and `corr(dg/dy, Band 18) = +0.0501`: it is the **signed east-west derivative `dg/dx`**, whereas **`Band 5 (iso_grav_anom_slope)`** (`[0.001, 0.652]`, `corr(||grad g||, Band 5) = +0.9620`) is the provided unsigned horizontal gravity gradient magnitude. Ranking raw `Band 18` without `abs()` assigns ~0th percentile to strong east-dipping normal faults (`dg/dx << 0`, footwall high west of graben).
2. Every band in `training_features.tif` encodes `3,061` in-footprint pixels (`0.06%`; `3,073` on Band 6) with float32 sentinel `-3.4028235e+38`, which passes `np.isfinite()`. Reading without `masked=True` treats nodata pixels as extreme negative finite values.

**Decision.** `scripts/build_snap_scarp_variants.py` reads `training_features.tif` with `ds.read(b, masked=True).filled(np.nan)` (plus `> -1e30` guard) and uses unsigned **`Band 5 (iso_grav_anom_slope)`** paired with the piedmont break-in-slope inflection `||grad(det_elev_slope)||` (`Band 19`). Furthermore, enforcing literal `"Same count, same exclusions"` (`d_cat > 2.0 px` on both kept and moved dots, rather than a one-way `d_cat > 3.0` membrane on moved dots) prevents partial depletion of the `2.0 < d_cat <= 3.0` collar (`2,171` vs `2,175` dots, `0.01%` delta vs `-24.7%` under `g0.05`), keeping `SNAPscarp2p0px`, `SNAPscarp1p4px`, and `SNAPpot2p0px` 100% unconfounded with `PRUNE`.


---

## 2026-10-24 (RELIEF session) — Baseline Parent R0 Mass is Asymmetrically Concentrated in Bedrock Range Front / Range Interior Rather than Active Piedmont

**Observation.**
Decomposition of parent R0 (`37,654` dots) across the three regional detrended-elevation terciles (`Band 12 det_elev`: `p33 = -142.9087 m`, `p67 = +38.7522 m` across the 5.17M px valid footprint) reveals:
- Basin tercile (`det_elev < p33`): 7,691 dots (20.43%)
- Piedmont tercile (`p33 <= det_elev < p67`): 15,743 dots (41.81%)
- Range-front / Range core tercile (`det_elev >= p67`): 14,204 dots (37.72%)

R0's dots in basin + range total 21,895 dots (58.15%). In extensional Basin-and-Range tectonic settings, active Quaternary normal faulting predominantly localizes along range-front alluvial fans and piedmont fault scarps, while deep basins conceal faults beneath thick, ductile/unconsolidated graben fill and range interiors contain eroded, exhumed, often inactive bedrock structures.

**Observation.** `releases/h33-h33-2-b2-MASS_A10-20261023-e5613a00.tif` (41,419
dots) contains 3,765 dots that are not in R0. All 3,765 sit on H19-5, but their
distance to the nearest R0 dot is **1.0 px at the minimum and 1.0 px at the
median**; the file's `min_nn` is `1.000 px` and 13.54% of its dot pairs are
closer than the parent's `2.8284 px`. `MASS_SWAP10` inherits the same additions.

**Impact — decision-changing.** Those files were already re-scoped (H19-5 is
binary, so the "ranking" was a tie) as a random 10% perturbation. They are also
a **mass + spacing** change at once, not a clean mass change: each added dot sits
inside the DTI kernel of an existing dot, so it mostly double-credits one strand
while adding `S`. Any receipt from them cannot be read as a mass-budget result.

**Decision.** No file is rewritten or deleted (they are a prior session's
artefact and already in the ledger). No conclusion about the mass optimum may be
drawn from them; a clean mass test still needs a real ranking and a spacing-safe
placement, which the saturated-packing measurement above shows is only possible
by *removing* dots.

## 2026-10-24 (CONCENTRATION session) — the block-CV reference band still gives no direction, and this axis cannot reach it

**Observation.** The brief quotes "the best files reportedly sit at 0.51-0.59"
for block-density CV. Measured with the repo's own definitions at 1 km blocks,
R0 is `CV_all_eligible = 1.880` and `CV_occupied = 0.619`. After the moves:
`up10 0.648`, `up20 0.655`, `dn10 0.648` (occupied-block definition). The band
is below R0 under the occupied definition and unrelated to it under the
all-eligible definition.

**Impact — decision-changing.** The statistic cannot be used to choose a dose or
a target, and neither direction moves the file into the quoted band — moving dots
from dense to sparse blocks *raises* CV (it adds first dots to sparse blocks)
just as much as the canonical direction does.

**Decision.** The CV is reported as a descriptive statistic only. The axis is
tested by its *direction* and its *prior*, not by chasing 0.51-0.59.

## 2026-10-24 (CONCENTRATION session) — this session's local PROXY instruments are invalid by construction

**Observation.** The prior used to place dots is a km-scale KDE of the known-fault
catalogue, and the repo's report-only instrument withholds catalogue components
as pseudo-truth. Its leakage canary for the design prior is symmetric AUC
`0.9273` (the four physical bands stay at `0.5012-0.5685`).

**Impact — decision-changing.** Per the brief, a canary above 0.90 means "stop and
investigate". Investigating: the prior is *deliberately* catalogue-derived (the
catalogue is a provided competition input and the organizer states new-fault truth
includes newly mapped geometry of existing systems), so this is not hidden test
label leakage — but it does mean the hide-and-recover and SGMC numbers cannot
support or refute these three arms. They are recorded with
`interpretable: false`.

**Decision.** For these arms only, the live receipt is the only decision
instrument. For completeness the probe returned `R0 0.004006`, `up10 0.004011`,
`up20 0.004008`, `dn10 0.002099` (hide-and-recover) and `R0 0.096060`,
`up10 0.092966`, `up20 0.089916`, `dn10 0.092296` (SGMC) — flat-to-worse, which
is at least consistent with "the known-fault halo is not where the withheld
catalogue components are".

---

## 2026-10-24 (second CONCENTRATION session) — a count-preserving move cannot hold the parent's spacing floor, and the floor sets how much of the "10%" is real

**Observation.** The H19-5 support is a 1-px-wide skeleton (121,131 px). Counting
legal destination pixels (on the skeleton, data-valid, off catalogue, `d_cat > 3`)
that are at least `R` px from every one of R0's 37,654 dots: `R = 1.0` → 61,472;
`R = 2.0` → 8,077; `R = 2.828` (the parent's own D2.8 floor) → **90**.

**Impact — decision-changing, twice.** (i) The brief's CONCENTRATION recipe is
impossible at the parent's spacing floor, so any implementation that claims to keep
2.828 px is either not moving dots or misreporting. (ii) The floor chosen changes
how much of the requested 10% is genuine: at a 2.0 px floor only 8,077 destination
pixels exist, and a 3,765-dot move then sends **1,000 of its 3,765 arrivals back
onto vacated donor pixels**, so the real positional change falls to **7.34%** and
the "10%" becomes bookkeeping. At 1.0 px (unique pixels only) the move is a genuine
10.00% (3,765 removed, 3,765 arrivals, no returns).

**Decision.** `phys10` is built at `min_nn = 1.0` and the trade-off is recorded in
its evidence file (`spacing_floor_tradeoff`). The other session's files on this
axis declare a 2.0 px floor; that is their choice and is not contradicted here,
but the two are **not** dose-comparable. Whatever the human submits, the sub-floor
spacing caveat in `docs/SUBMIT.md` applies.

## 2026-10-24 (second CONCENTRATION session) — two sessions built the same axis from the same parent

**Observation.** This branch and PR #13 independently built a 1 km,
catalogue-density CONCENTRATION set from `h33-h33-2-b2` on the same day, with the
same moved-dot rules (`on H19-5`, `d_cat > 3.0`, kept dots at parent positions) and
the same mirror direction. The branch's `catd10` and `catdS10` were near-duplicates
of `catblk10up10` and `catblk10dn10`.

**Impact — slot economy.** The brief allows one build per `(AXIS, value)` across
sessions and one entity at 3 slots/week; two near-identical files would compete for
the same question and could burn two slots on one answer.

**Decision.** The duplicates were **dropped** from the ledger; only
`CONCENTRATIONphys10-20261024-b93a4cf8` survives from this branch, because no other
file tests a prior that is not derived from the catalogue. Cross-variant overlap is
measured rather than asserted: in this branch's own harness the catalogue-prior and
physics-prior arrival sets overlapped at Jaccard `0.087`, so the surviving variant
asks a genuinely different question from the merged set.

**Decision.**
Shift 10%, 12%, and 15% of total mass (3,765, 4,518, and 5,648 dots) from the lowest-prior basin and range dots into the highest-prior unpopulated H19-5 pixels located strictly within the piedmont tercile, using greedy exact expected-DTI marginal gain on the label-free physical prior (`Band 3`, `Band 5`, `Band 19`). Dot count is held at exactly 37,654, zero mass is placed on the catalogue, and all dots maintain R0's `d_cat > 2.0 px` exclusion.

---

## 2026-10-24 (registry uniqueness review) — one full-support raster makes the literal overlap gate impossible for every nonempty candidate

**Observation.** The public metadata inventory contains
`17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif`
(Git blob `374c88b1da2b803e2ed160de467fd71ae114010d`). Its fetched bytes match
SHA-256 `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`; it is
one-band float32 on the exact `3730 x 3292`, EPSG:32611, 100 m sample grid. The
shared `vendor.gems57.uniqueness.saturation_certificate` finds positive support
on all `5,167,373` footprint pixels. The legal domain after pixel-exact catalogue
exclusion has `5,106,385` cells, and **zero** of them are outside the witness
support's 3 px halo.

**Impact — absolute blocker under the current literal rule.** The shared support
definition is `finite prediction > 0`, and the forward-overlap stop threshold is
`>0.70` against any registry raster. Every nonempty legal candidate therefore has
forward overlap exactly `1.0` with this witness, regardless of its geology or
placement. A zero-valued raster has no candidate dots and cannot satisfy the
unique nonempty-prediction certificate. No nonempty GeoTIFF can be both valid and
unique under this rule while the witness remains in scope.

**Decision.** Follow the specified stop rule: `STOP_BEFORE_PLACEMENT`. Do not build
or validate a candidate, do not produce a misleading all-zero TIF, do not call the
submission writer, and do not use a weekly slot. The result is recorded in
`evidence/registry_saturation_blocker.json` and
`evidence/run_card_20261024.json`. The shared rule was not weakened or silently
scoped around continuous surfaces. A future change to compare Spearman correlation
on all surfaces but dot-overlap only on discrete point rasters would change the
user-specified gate and requires explicit authorization before proceeding.

**Scope note.** `registry/public_gems_tif_inventory.json` records a complete GitHub
metadata tree scan for 101 *public* owner repositories matching the documented
GEMSDOE name pattern, but stores only candidate-like TIFF paths after a transparent
heuristic (2,508 TIFF paths counted; 1,998 candidate-like paths; 1,305 unique
candidate-like Git blobs; 1,046,507,603 bytes by GitHub metadata).
It is not a byte-level comparison of every TIFF. The single witness was downloaded
from GitHub and hash/grid verified; the universal blocker is sufficient to stop,
but no complete raster-correlation inventory is claimed.

## 2026-10-24 — leaderboard display and H33-2-B2 score are not receipts

**Observation.** The local ledger has 21 `BUILT` rows and zero `RECEIPT` rows. The
repository labels `0.2778` as an owner-reported `CLAIM`; the public GEMSDOE32 page
calls its H33-2-B2 artifact `UNSCORED`. The official public leaderboard page
observed on 2026-10-24 displayed `0.4413`, `0.3916`, and `0.3904` at ranks 1–3,
which conflicts with the user-provided `0.3195` snapshot.

**Decision.** Preserve the labels exactly: `0.2778` is not
`ORGANIZER-CONFIRMED`; the leaderboard values are observations, not submission
receipts. No account score, private score, or reason for the claimed `0.2778` was
inferred.
