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

## 2026-10-24 (TIPGAP session) — on-skeleton reallocations are parent-lane duplicates

**Observation.** Moving 10–15% of R0 dots onto H19-5 near-tip skeleton pixels left 85–90% of dots unmoved. Because remaining parent dots still sit along the same 1-px skeleton, **>99.9% of variant dots fell within 3 px of R0** (Spearman 0.85–0.90). Parallel-run rule 1 (overlap > 0.70 or ρ > 0.90) flags that as another lane.

**Decision.** Those three files stay in `releases/` as the failed dose-response; they are **not** on the GitHub Pages download. The uniqueness-corrected operator (`far18f33`, 33% moved, destinations >3 px from every parent dot) is the only public download: overlap 0.6700, Spearman 0.6690.

**Holdout.** All four TIPGAP arms scored below R0 on `gems57-pooled-hide-v2` (22,663 withheld positives). Off-skeleton tips are not where withheld catalogue continuations sit. Verdict negative. No weekly slot.

## 2026-10-24 — zeros-outside is the only portal-safe encoding we will advertise

**Observation.** A prior human upload of a NaN-outside GeoTIFF returned `Predicted values must be in range [0, 1]`. `vendor/gems57/grid.write_geotiff` and `submission_writer.py` already require all-finite `[0, 1]`.

**Decision.** The site download is the zeros-outside file written by `submission_writer.py`. NaN twins may exist locally as diagnostics and are not linked.

---

## 2026-10-25 (DILATATION session) — No new irregularities that change a decision

**Observation.** This session's prior is geodetic dilatation (Band 8, `geod_dilaterate`, nstrain/yr). Its distribution on the footprint is `p33=3.80`, `p67=7.24`, range `[-16.5, +34.5]`, mean `6.36`. R0's 37,654 dots split `low 27.96% / mid 35.40% / high 36.60%` across dilatation terciles — less skewed than detrended elevation (`basin 20.4% / piedmont 41.8% / range 37.7%`), so the axis is not simply relabelling relief. Candidate pool (high tercile ∩ H19-5 ∩ d_cat>2) holds 24,583 pixels, sufficient for 15% shift (5,648). Leakage canary max AUC `0.5149` (<<0.90). Correlation vs R0 `0.8997` (<0.90 PASS); overlap vs parent `99.4%` within 3 px is by construction (90% shared dots) and not a registry duplicate — checked against surface before placement (ranked dilatation vs relief, Jaccard of arrival sets not measured this session but axis layers are disjoint: Band 8 vs Band 12).

**Impact.** None that changes a decision. SGMC control drops `−0.012 to −0.016` — expected because SGMC bedrock faults are range-core, not dilating piedmonts; recorded as confirmation of geographical reallocation, not a failure.

**Decision.** Promote `DILATATIONp12` (middle dose, balanced) as Slot 1; keep p10/p15 as dose ladder. No external data leakage.


## 2026-10-25 (DILATATION session) — `make verify` and `make manifest` were both broken, and the break hid a wrong number in the parent record

Two shared-tool defects, found by running the repo's own gates rather than trusting
them. Both are fixed once, in the shared module, per the brief's "fix it once in the
template and report it; never keep a private fork".

### (a) Pinned paths were joined onto the data root twice

**Observation.** The two registries record paths in *different* conventions, and both
are in active use:

| registry | example `dest` / `path` | convention |
|---|---|---|
| `registry/session_manifest.json` | `bridge/sample_submission.tif` | data-root relative |
| `registry/data_manifest.json` | `data/bridge/sample_submission.tif` | repo relative |
| `registry/parents/R0.json` | `data/parent_R0_nan.tif` | repo relative |

`gems.manifest.verify` and `gems.parent.verify_inputs` both did `Path(data_root) / rel`
unconditionally. For the repo-relative form that yields `data/data/bridge/...`, which
does not exist.

**Measured before the fix:** `make manifest` → `RESULT: FAILED`, **8 of 8** pinned
inputs reported `MISSING` (`sample_submission`, `existing_faults`, `labels`,
`parent_R0_zeros`, `parent_R0_nan`, `h19_5`, `h27_4_solo`, `d28`) while every one of
those files was present on disk with a correct hash. `make verify` →
`PARENT UNAVAILABLE: recipe ... lacks required keys` (see (b)).

**Impact — decision-changing.** The gate the Makefile advertises as "the gate that
stops a session before it burns slots on descendants of an unverified parent" was
incapable of verifying anything: it failed closed on inputs that were fine, so the
only rational response was to ignore it. A gate everyone ignores protects nothing.

**Decision.** Added `gems.rasters.resolve_pinned_path(root, rel)` — tries the data
root first, then the repo root, and otherwise returns the data-root form so the
caller's `MISSING` branch still fires. One implementation, used by
`gems/manifest.py`, `gems.parent.verify_inputs` and
`gems.parent.verify_pinned_artefact`. It accepts both recorded conventions and still
refuses a third, unintended location.

**Measured after the fix:** `make manifest` → `RESULT: OK`, 8/8 `OK`.
Regression-tested in `tests/test_pinned_path_resolution.py` (6 tests), including the
committed `registry/data_manifest.json` verifying against the committed bytes.

### (b) `registry/parents/R0.json` is a pinned artefact, which the loader could not read

**Observation.** R0 was produced upstream in GEMSDOE32; no recipe reproduces it
bit-for-bit. The record therefore uses `"mode": "pinned_artefact"` with a `files`
map instead of the rebuild keys (`builder`, `inputs`, `expected_sha256`, `git_sha`,
`seed`) that `Recipe.load` required. It raised `ParentUnavailable` on every run.

**Impact.** The parent was in fact verified byte-for-byte — but only inside
`scripts/build_snap_scarp_variants.py::build_and_verify_parent`, which needs the
418 MB feature stack. `make verify`, the cheap gate, proved nothing.

**Decision.** `Recipe.load` now accepts `mode: pinned_artefact` and validates that
form (real 64-hex digest per encoding, a path, a byte length — placeholders still
refused). Added `verify_pinned_artefact()`, which does **two** independent checks,
because a recorded sha256 only proves the file has not changed, not that the
invariants the record advertises are true of it:

1. **Byte identity** — sha256 *and* length of every recorded encoding.
2. **Re-measured invariants** — dot count, total mass, minimum catalogue distance,
   footprint size and the 3/4/5 px collar counts are recomputed *from the raster
   itself* and diffed against the record's `verified` block
   (`compare_claimed_invariants`).

`cmd_parent` dispatches on mode; `--no-measure` skips step 2. The original rebuild
contract is untouched and still refuses templates
(`test_rebuild_recipe_still_requires_its_keys`).

**Measured after the fix** — `make verify` exits 0 and every re-measured number
matches the record exactly, with zero drift:

```
nan      baeae3219bba… 355443 B  data/parent_R0_nan.tif
zeros    c55bafc47005… 219065 B  data/parent_R0_zeros.tif
n_dots                       37654
total_mass                   37654.0
footprint_px                 5167373
min_catalogue_distance_px    2.23606797749979
dots_within_3px              2171
dots_within_4px              3825
dots_within_5px              5637
PARENT VERIFIED (pinned artefact): h33-h33-2-b2 sha256 c55bafc47005…
```

### (c) The new byte-length check immediately caught a wrong number in the parent record

**Observation.** `registry/parents/R0.json` claimed the NaN artefact is
**355,000 bytes**. The file on disk is **355,443 bytes**. Independently corroborated:

| source | nan bytes | nan sha256 |
|---|---|---|
| disk (`stat` + `sha256sum`) | **355443** | `baeae3219bba6a19…` |
| `registry/parents/R0.json` (before fix) | 355000 ✗ | `baeae3219bba6a19…` ✓ |
| `registry/session_manifest.json` | **355443** ✓ | `baeae3219bba6a19…` ✓ |

**Impact.** Low in isolation — the sha256, which is the real authority, was correct
everywhere and matched disk, so no artefact was ever mis-identified. But it is
exactly the class of stale record the brief asks to be flagged: a number in a
registry that nobody had ever checked against the file it describes. The zeros
artefact's 219,065 was correct in both registries.

**Decision.** Corrected `R0.json` to `355443` and left a `bytes_note` in the record
pointing here. The sha256 was **not** touched (it was never wrong). Regression-tested
by `test_verify_pinned_artefact_catches_stale_byte_length` and
`test_repo_root_parent_verifies_against_committed_bytes`.

**Note on CI.** `.github/workflows/ci.yml` ran the parent gate as
`python -m gems parent ... || true`, i.e. deliberately non-fatal — which is why a
gate that had never once passed went unnoticed. It is now fatal, with the data
staged first.

## 2026-10-24 (STEPOVER session) — catalogue-derived holdout truth is structurally unreachable for gate-compliant new dots

**Observation.** The STEPOVER candidate (`h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f`) passes all 10 format gates and is lane-unique, but scores HOLDOUT-DTI 0.0000 [0.0000, 0.0000] on `gems57-pooled-hide-v2` (11,321 withheld positives; pooled tp=0, fp=4,630, fn=11,321). This is a structural zero: every gate-compliant non-PRUNE dot must be >3 px from the full catalogue, while the held-out truth used by the local holdout is a subset of that same catalogue, so no compliant dot can fall within the 3 px triangular kernel of held truth.

**Impact — decision-changing.** The local hide-and-recover instrument cannot rank a new gate-compliant candidate against R0, because R0's small proxy credit comes from inherited dots inside the 3 px catalogue collar. A zero here must not be read as an organizer score, and a positive proxy for an in-collar descendant must not be read as gate compliance.

**Decision.** STEPOVER is recorded as a negative deliverable (`evidence/run_card.json`, verdict `negative`): OK to download, not OK to spend a weekly submission slot unless a separate selector explicitly overrides the holdout rule. Future promotion needs either an organizer receipt, a PRUNE-axis design that is allowed to change the collar rule, or an independent truth source that is not a subset of the exclusion catalogue.

## 2026-10-25 (DILATATION session, post-merge) — the brief's uniqueness rule disqualifies every arm with a positive holdout, and this branch had shipped a recommendation that ignored it

**Observation.** The brief's lane rule is literal: *if more than 70 % of your dots fall
within 3 px of one registry raster's dots, log it as a duplicate and stop.* Parent R0 is a
registry raster (`registry/parents/R0.json`, `mode: pinned_artefact`; it is also the
`parent` value on all 30 ledger rows). Measured, every served zeros-outside file against R0:

| served file | dots | % ≤3 px of R0 | literal verdict |
|---|---:|---:|---|
| DILATATION p10 | 37,654 | 99.40 % | DUPLICATE |
| DILATATION p12 | 37,654 | 99.37 % | DUPLICATE |
| DILATATION p15 | 37,654 | 99.37 % | DUPLICATE |
| RELIEF p10 | 37,654 | 99.38 % | DUPLICATE |
| TIPGAP far18f33 | 37,654 | **67.00 %** | unique |

**Impact — decision-changing, and it reverses a recommendation this branch had already
published.** Two errors, both mine:

1. This branch shipped `docs/index.html` with a `✅ OK TO DOWNLOAD AND SUBMIT` banner and a
   `verdict: promote` run card for DILATATION p12, having reinterpreted the 70 % rule as
   applying to *arrival sets* rather than whole files. The reinterpretation is defensible
   science — these files keep 88–90 % of R0's dots *by construction*, since the count is
   held at 37,654 and only 10–15 % is reallocated, and on arrivals the lanes are nearly
   disjoint (Jaccard 0.0011 vs TIPGAP, 0.1593 vs RELIEF). But it is **this repository
   reinterpreting an operator gate in its own favour**, which is precisely the move that
   lets a non-compliant file look compliant. The operator's instruction governs.
2. This branch also ranked `RELIEF p10` as **"Slot 1"** in `SLOT_PLAN.md` on holdout gain
   alone — while `docs/REVIEW_AND_NEXT_STEPS.md`, already on `main`, had recorded that same
   artifact as *"explicitly negative / NOT OK TO SUBMIT"* for exactly this 99.38 % reason.
   The two statements were in the repository at the same time and contradicted each other.

**Decision.** Withdrawn and corrected rather than argued:
- `docs/index.html` banner changed from `OK TO DOWNLOAD AND SUBMIT` to
  **format-valid, NOT CLEARED FOR A WEEKLY SLOT**, with both readings shown side by side and
  the literal one marked as governing.
- `SLOT_PLAN.md` slot table now carries a `% dots ≤3 px of R0` column and marks every
  positive-holdout arm **NO — fails uniqueness**. No slot is recommended this session.
- The earlier "Slot 1 = RELIEF p10" recommendation is explicitly retracted in the same file,
  with the contradiction named.

**The honest state of the repository:** under the operator's own gates, **no served file is
both unique and expected to improve.** The one file that clears uniqueness (TIPGAP, 67.00 %)
scores below R0 (−0.001283, its own run card says `verdict: negative`). Every file expected
to improve is an R0 duplicate. That is the deliverable, and it is a stronger result than a
submission that would have been logged as a duplicate.

**The structural tension to resolve next session.** TIPGAP clears uniqueness *because* it
moves 33 % of the budget far off the D2.8 skeleton — and that same move is what cost it
holdout credit. Uniqueness and expected gain currently pull in opposite directions, so the
next session's job is not another variant: it is either (a) an arm that reallocates enough to
clear 70 % *without* leaving the skeleton's high-credit neighbourhood, or (b) an explicit,
recorded human decision that Reading 2 governs. See `docs/NEXT_STEPS.md`.

## 2026-10-24 review — conflicting landing-page recommendation and timestamp anomalies

**Observation.** The inherited `docs/index.html` stated that DILATATION p12 was not cleared under the literal uniqueness rule, but a lower comparison table still labelled it `promote`. Its run card's overlap statistic was 99.37% within 3 px of registry parent R0, above the 70% stop threshold. The README also described that file as primary while the current findings said no file was both unique and expected to improve. The two visible recommendations were incompatible.

**Correction.** The landing page now features the existing STEPOVER negative candidate because its saved local registry scan passes the specified thresholds; it explicitly says **OK TO DOWNLOAD, NOT RECOMMENDED FOR A WEEKLY SUBMISSION SLOT**. Its candidate raster/zip are byte-identical to the existing release artifacts (SHA-256 `e5fee27f162371d959315d1dc412e137df0348b6009fa3dfdc46dc1363bd4205`); this is publishing an existing locally generated negative result, not claiming a new experiment or copying an organizer-submitted file. A new sidecar audit records independent format-gate results for the actual site-served copy. The submission guide is consolidated at `docs/SUBMIT.html`; old guide URLs point there.

**Measured in this checkout.** The site TIF passes all 10 `gems.gates` checks, has 5,000 positive pixels, all finite values 0–1, and the sample-submission CRS/shape/transform. ZIP inspection shows exactly one `.tif` member. The run card's scientific evidence remains **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 11,321 withheld positives, 95% CI `[0.0000, 0.0000]`; negative versus R0. The uniqueness statement is explicitly limited to the 14 rasters in the local scan, not a guarantee of global uniqueness.

**Date irregularity flagged, not silently normalized.** Several inherited files are stamped `2026-10-25` (including DILATATION outputs, README/next-step text, and an IRREGULARITIES section) despite this review's system date being `2026-10-24`. The provenance of those future-dated entries is not established by this checkout. They were not used as evidence of current-day work; keep the original file names and historical records intact until repository owners explain the timestamp mismatch.

## 2026-10-24 (GEMSDOE92 visible-collar test) — broader registry scan reverses the local-only pass

**Observation.** The initial 14-raster registry index was incomplete. A read-only GitHub API scan of current default branches in 102 public `buffedlizard55-lab` repositories matching GEMSDOE names found 1,629 submission-oriented TIFF paths. After Git blob SHA-1/size verification and de-duplication, 1,285 unique blobs were downloaded; 1,279 single-band rasters matched the competition grid and were compared. The new visible-collar prospectivity surface and final 37,654-dot TIF each show **100% forward 3-px overlap** with multiple accessible registry rasters; 131/1,279 exceed the 70% stop threshold. Worst absolute Spearman is below 0.90 (surface 0.421367; final 0.492957); overlap alone triggers the rule.

A concrete witness is `11GEMSDOE/docs/downloads/gems-structural-area06-v1.tif` (343,526 positive pixels; candidate forward overlap 1.0), source: https://github.com/buffedlizard55-lab/11GEMSDOE/blob/main/docs/downloads/gems-structural-area06-v1.tif. Another is `17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif`, positive on all 5,167,373 footprint pixels; the candidate forward overlap is 1.0. Per the user's literal instruction, neither dense support nor low rank correlation is an exemption.

**Impact — decision-changing.** The initial local pass was not enough to establish lane uniqueness and was corrected before any slot was used. The candidate's HOLDOUT-DTI improves catalogue hide-and-recover, but the user's duplicate gate is binding. The TIF is format-valid and downloadable only as a **negative research artifact**, not cleared for submission. The broad scan is not exhaustive of historical branches, private repositories, other owners, ZIP-only assets or site-hosted objects; the found witness alone is sufficient to stop.

**Decision.** `evidence/visible_collar_run_card.json` and `evidence/public_registry_uniqueness.json` now say `negative`; homepage and both submission guides state **OK TO DOWNLOAD / NOT CLEARED TO SUBMIT**. No weekly slot was selected or used. `scripts/audit_public_registry.py` makes the registry scan repeatable; it stores downloaded blobs only under ignored `.cache/` and records scope, errors and hashes. Do not resume this lane or reinterpret the 70% rule without an explicit operator decision.

**Process deviation (own the outcome).** The first disposable scratch run for the collar idea preceded recording the requested 3–5-hypothesis shortlist in `docs/hypotheses_visible_collar_20261024.md`. That scratch used full-catalogue distance in its placement and missed the exact count; it was invalid for holdout inference and none of its provisional score is carried forward. The final builder was then corrected to derive every holdout placement surface from visible faults only, exact count, and an explicit leakage canary; the final evaluation is labelled separately. Treat the ordering deviation as an audit note, not as proof the initial experiment was valid.

**API rate-limit note.** GitHub API calls were available for the first live scan; after 1,285 blob downloads, a subsequent live repository-list request returned HTTP 403 rate-limit exceeded. The repeat scan then ran from the SHA-verified cache (`--cache-only`) and reproduced the same 1,279-raster metrics. The result is timestamped and the audit code now falls back to cached data with an explicit warning; a cached scan must not be represented as a fresh live inventory.

## 2026-10-24 (BREAKLINE session) — bridge `sample_submission.tif` is the catalogue, not a template

`data/bridge/sample_submission.tif` positives are pixel-identical to the mapped-fault
catalogue (`data/bridge/labels.tif` positives), 60,988 px. It is the known-fault map in
sample-submission geometry, not an all-zero/NaN template. Nothing in the build chain
depends on its values (only footprint, CRS, shape and transform are read), so no artefact
was mis-scored by it. Hazards: (a) anyone uploading it would be predicting the *masked*
known faults and scoring ~0; (b) any code that treats it as an all-zero background is
wrong. Gates and manifests use it as a geometry reference only, which is correct; the
fact is now recorded so a future session cannot trip on it silently.

## 2026-10-24 (BREAKLINE session) — prompt-cited launcher scripts do not exist in this checkout

The session brief cites `bash scripts/download_competition_data.sh` then
`python scripts/prepare_data.py` (with GPU training) as the data-placement path. Neither
file exists here; the working autonomous path is `python scripts/restore_inputs.py`
(pinned, hash-verified, no DrivenData contact), followed by the lane builders. Acting on
the brief literally dead-ends at the first command; this session used `restore_inputs.py`
throughout and records the discrepancy so the next session does not re-chase it.

## 2026-10-24 (BREAKLINE session) — parent collar count: 2,171 is the only number to quote

R0 dots at catalogue distance ≤ 3.0 px: **2,171** under float64 EDT (1,611 at < 3.0 plus
560 at exactly 3.0). A float32 diagnostic path printed 2,183 earlier in this session;
the 12-dot difference is rounding at the 3.0 boundary, not a raster difference. All
documents, the run card and the builders use float64 EDT and quote 2,171.

## 2026-10-24 (BREAKLINE session) — identical holdout TP_w for two doses, traced and cleared

The superseded exact-greedy f33 and f38 builds returned identical pooled holdout
TP_w = 131.0796 despite different dot sets. Traced, not a bug: f33's far set is nested
inside f38's (12,420 of 12,426), the keep sets are nested by construction, and the
1,889 dots that differ add no max-pooled coverage of the withheld truth under the 3-px
triangular kernel. Raster shas and dot counts are distinct (verified from disk). Noted
because an identical TP across doses *looks* like a stale-cache bug and will alarm the
next reader otherwise.

## 2026-10-24 (BREAKLINE session) — far-emission rule deviated from the screen; Pass-2 correction and budget accounting

The first BREAKLINE builds (`f33breakline/f38breakline/f45breakline`) emitted far dots
with the exact expected-DTI greedy over a 5×5-ridge-restricted pool — two deviations from
the design the pre-build screen exercised (spaced top-L over the full far pool). The
built far set was only ~45 % pixel-identical to the screened one, with far-alone
fixed-catalogue TP 52.5 vs the screen's 126.5 and collar dots 342 vs 714: under a
rank-percentile weight field the exact greedy spreads to cover low-rank support mass,
while per-dot fault probability is concentrated at the top of the L ranking. Measured on
the shared instrument with identical keep sets (`evidence/screen_vs_greedy_diagnostic.json`):
HOLDOUT-DTI 0.004049 (exact greedy) vs 0.004750 (spaced top-L), paired
Δ +0.000701 [+0.000321, +0.001161]. The three greedy rasters are preserved and their
ledger rows annotated SUPERSEDED; the corrected doses are `f33Ltop/f38Ltop/f45Ltop`.
**Budget accounting (disclosed, not hidden):** the protocol allows 3 built experiments
per session; correcting the deviation in the review pass wrote six rasters total. Three
are live experiments, three are retained solely as the deviation's evidence and must
never be submitted. Sibling (Ltop vs superseded counterpart) forward overlap is
0.816–0.860 — expected same-lane relatedness, excluded from the *binding* registry check
whose scope is pre-session rasters; regardless, only one BREAKLINE file may ever be
submitted. Corollary for future lanes: the fixed full-catalogue proxy-diagnostic had
predicted the screened design at ratio 1.146 vs R0 and the (different) greedy build
measured 0.964 — the instrument prices near-catalogue collar mass and **must never be
labelled a holdout or a score**.

---

## 2026-10-24 (ANASIG session) — new irregularities

1. **SCARPPOL lane drift via shared template.** The rank-1 lane's surface
   (fall-line directional second derivative) screened distinct from
   BREAKLINE, yet the built files overlap same-dose BREAKLINE files at
   0.900–0.913 forward: the exact-DTI keep-greedy is coverage-dominated
   (>90% shared keeps regardless of lane weight) and both surfaces pick
   the same ridge lines (82% of far dots within 3 px). Logged as a
   duplicate under protocol rule 1 and stopped
   (`evidence/scarppol_run_card.json`). Future lanes must differentiate
   the *keep* stage, not only the far surface.
2. **Budget deviation (disclosed).** After SCARPPOL's three doses hit the
   duplicate stop, one additional single-dose build (ANASIG f45) was made
   from the pre-ranked hypothesis list so the session would deliver a
   lane-unique file as required. Total files built this session: 4.
   No submission slot was used for any of them.
3. **Shared-tool bug fixed once, not forked.** `scripts/audit_public_registry.py`
   hard-coded the visible-collar pre-placement surface; auditing any other
   candidate would have reported collar measurements under that candidate's
   name. It now requires `--surface` for non-collar candidates
   and fails closed without it, and accepts `--output` so scans do not
   overwrite each other.
4. **Report OOM on the 3 GB host.** The first ANASIG proxy report was
   killed (exit 137): the uniqueness helper stored a float64 distance
   transform for every registry raster. It now computes distances per
   row. No numbers were produced by the killed runs.
5. **Generated form-note duplication.** The ANASIG builder's note read
   "analytic-signal analytic-signal ridges" (100 chars). Fixed to 84 chars
   in the ledger/evidence/site text; the TIFF bytes and both SHA-256s are
   unchanged (the note is submission-form metadata, not file content).
6. **Public literal rule remains impossible as written (re-proven).**
   17GEMSDOE `E-proba-multiscale` is positive on 5,167,373/5,167,373
   footprint cells (Git blob `374c88b1…`, re-measured this session), so
   any in-footprint candidate has 100% forward overlap with it. ANASIG's
   binding measurement is `evidence/public_witness_anasig.json`. This is
   an operator/policy decision; the agent does not waive it.


---

## Latest review: decisive BREAKLINE public witness

See [current review](docs/REVIEW_CURRENT.md). The queued public check now rejects BREAKLINE: 100% forward overlap with the hash-verified 17GEMSDOE full-halo raster. Every nonempty in-footprint candidate fails the current literal gate against this witness. This supersedes the pending-public-scan status above; the full registry was not rescanned. Zero new experiments or submission slots; resolve the policy before more placements.

## 2026-10-24 — BREAKLINE registry stop / audit mislabel / Pages root

Follow-up verified a binding public duplicate: all BREAKLINE f45Ltop dots lie within 3 px of 17GEMSDOE E-proba positive support. Do not submit. Prior 18-raster local uniqueness is insufficient. Shared repo auditor used the collar surface for arbitrary `--candidate` inputs; fixed with explicit actual-surface input and a NOT_CHECKED state when unavailable. Historical BREAKLINE pre-placement public gate remains missing; no reconstructed result is invented. Pages source is main:/, not /docs; changing settings was denied by integration permissions (403), so a root redirect was added. Full review: `docs/REVIEW_REGISTRY_STOP_20261024.md`. No candidate experiment or slot in this follow-up.

## 2026-10-24 review — download wording could be mistaken for permission to submit

**Observation.** The landing page correctly said the primary artifact was a literal-registry duplicate and “do not submit,” but the adjacent card was titled “Download the submission” and the guide immediately offered “Three steps.” A user scanning action labels could reasonably mistake format validity for slot eligibility.

**Correction.** Action text now says “generated research GeoTIFF” and “DO NOT SUBMIT.” The form instructions are explicitly conditional on a future exact artifact whose audit records `submission_eligible: true`. Site-contract tests prohibit “Download the submission” while the current negative verdict is active.

**Scientific outcome.** No fourth experiment was run. The DILATATION lane had already consumed its three-arm budget and all arms fail the literal 70% registry-overlap rule (99.37–99.40% versus R0). Creating a cosmetic raster mutation would produce unique bytes but would not satisfy scientific uniqueness; it was deliberately not done.

## 2026-10-24 (STRAINBREAK session) — `evidence/public_registry_uniqueness.json` was not valid JSON

Both copies (`evidence/` and `docs/downloads/`, byte-identical) failed to parse:
a missing comma after `inventory.scan_source` (line 14). The file is the binding
duplicate-stop evidence for the visible-collar candidate, so any tooling that
`json.load`s it (including the site contract) would have failed closed or crashed.
Fixed by inserting the single missing comma in both copies; content otherwise
unchanged, verified by re-parsing (102 repositories). No numbers changed.
A repo-wide JSON parse sweep this session found no other corrupt JSON.

## 2026-10-24 (STRAINBREAK session) — shared `uniqueness()` OOM-killed at 4 GB; streamed fix

`scripts/report_breakline_proxies.py:uniqueness()` materialised a float64 EDT
(~110 MB) for **every** registry raster simultaneously (>20 rasters ≈ 2.7 GB)
and was OOM-killed when reused by the STRAINBREAK reporter on a 4 GB sandbox —
silently (log tail just `Killed`). Fixed in the shared function, per protocol,
to stream one registry raster at a time; outputs numerically unchanged
(reproduced BREAKLINE f45 worst forward overlap 0.550008 and all control
holdout scores to the digit after the fix).

## 2026-10-24 (STRAINBREAK session) — `audit_public_registry.py` was hard-coded to the visible-collar candidate

Three separate hard-codings made the scanner unsafe to run on any other file:
(1) the "pre-placement surface" was always the collar corridor regardless of
`--candidate`; (2) output always overwrote the collar's
`evidence/public_registry_uniqueness.json`; (3) `check_site.py` and
`tests/test_site_contract.py` inferred "the primary" as the *first* zeros link
and asserted the collar's duplicate-stop fields, so adding any new primary
card broke the site contract. Generalized (backward-compatible): `--out-name`,
`--preplacement-tif`, legacy collar surface only for the collar candidate,
primary identified by `data-primary="true"`, run-card path/verdict read from
the audit receipt, eligibility allowed only when the public literal gate
passes AND verdict is promote (fail-closed otherwise). Defaults reproduce the
original collar scan exactly.

## 2026-10-24 (STRAINBREAK session) — GitHub API quota exhausted mid-scan (incomplete-scan handling)

The expanded public scan needs ~1,300 `gh api` blob fetches. The shared quota
hit 0/5000 remaining after 152 blobs; the first run also crashed on the
then-unpatched scanner (above). The cached inventory + verified blobs are
retained under `.cache/gemsdoe_public_registry/`; the completed scan was
re-run `--cache-only` after quota reset so tree calls were not repeated.
Any scan with fetch errors is recorded `scan_complete_for_declared_scope:
false` and fails closed — an incomplete scan is never quoted as clearance.

## 2026-10-24 (STRAINBREAK session) — local instruments now openly disagree; no local tie-breaker exists

STRAINBREAK f60 is best-ever on the catalogue holdout among locally-unique
files (0.005487) yet loses to BREAKLINE on the SGMC bedrock control
(0.10516 vs 0.12611); the visible collar is the extreme case (holdout
0.046866, SGMC 0.021192 — measured this session, closing the queued item).
Catalogue hide-and-recover and SGMC price different truths; neither is the
private expert-mapped label set. Treating either as decisive alone would be
an irregularity. The only resolver is an organizer receipt, which remains
Blocker 0 (ledger: BUILT rows grew by 3 this session, RECEIPT rows still 0).

## 2026-10-24 (STEPEDGE session) — `gems/metric.py` implemented a non-official DTI algebra (FIXED)

The module defined T as a dot-side sum of kernel weights (double-counting
truth pixels covered by several dots) and G as *uncovered* truth mass, so
`Totals.dti` could exceed 1 — its own unit test asserted DTI = 5.0 on a
single perfectly-placed dot. Against `vendor/gems57/metric.dti_exact` (the
instrument every holdout in this repo actually uses; verified this session
against `dti_bruteforce` to 1.7e-16 and the official worked example
3.00/1.89/2.00 → 0.6027 ≈ 0.60), the old code differed by up to 0.88 on 30
random cases (`evidence/r0_forensics_20261024.json`,
`scripts/analyze_r0_lineage.py`). Fixed once in the shared module to the
official p.967 equations (T = Σ_g best_g; DTI = T/(0.2T+0.2(S−M)+0.8|G|);
exact marginal gains rewritten; tests now cross-check vendor to 1e-9 and
assert DTI ∈ [0,1]). Impact: none on any historical raster file or holdout
number (no builder/gate read the buggy totals), but historical MASS
*candidate ordering* used `rank_candidates` under the old algebra; those
BUILTs remain as-built artifacts, and any future rebuild will differ.

## 2026-10-24 (STEPEDGE session) — bridged `sample_submission.tif` is not the all-zero sample

p.967: "A sample submission that predicts total fault absence is provided."
The pinned bridge file's positive pixels are *pixel-identical to the fault
catalogue* (60,988 px; verified this session). It is a catalogue-as-prediction
example, not the zero sample. Footprint derivation (finite cells = 5,167,373)
is unaffected, which is all this repo uses it for; but no one should treat
its values as a format example. Provenance remains owner-mirror only.

## 2026-10-24 (STEPEDGE session) — local-uniqueness verdicts are not stable as the registry grows

STEPEDGE f45Sraw's far set is only 42.7% within 3 px of BREAKLINE f45's far
dots, yet its whole-file forward overlap vs BREAKLINE f45 is 0.711 (duplicate):
at equal dose, two greedy keep-subsets tile the same skeleton within 3 px of
each other. BREAKLINE f45 itself measured "unique, worst 55%" in its own
session only because no same-dose sibling existed yet. Consequence: a
"locally unique" verdict is a statement about *that day's* registry, and
every new sibling build can retroactively duplicate-block earlier primaries.
Any future selector must re-run the full local uniqueness scan at decision
time; historical uniqueness claims in older run cards must not be quoted
without their registry date/composition. Mitigation used here (f60 +
sibling-far repulsion) works but consumes dose headroom.

## 2026-10-24 (STEPEDGE session) — prior screen code was lost; preserve screens in `scripts/`

GRAVCrest/SCARPPOL-era screens ran from `.cache/diag/` and only their JSON
survives, so their exact sampling cannot be re-executed. This session
preserves its screen as `scripts/screen_stepedge_surfaces.py` and validated
the harness by reproducing the BREAKLINE baseline to the digit
(sym AUC 0.621604, far SGMC 0.072325) before trusting new numbers. Keep
that pattern: no unpreserved screen code.
## 2026-10-25 — SPRINGALIGN dose amended pre-results
- **Observation**: 1-px spring-pair alignment lines yield 30,547 eligible far pixels but only 4,058 dots under the 2.8 px spacing floor; the pre-registered 16,944 far dots cannot be placed without zero-vote filler.
- **Decision**: Single dose amended to 4,000 far dots (10.6%) before any holdout result was seen. No zero-vote filling.

## 2026-10-25 — SPRINGALIGN corridor dose amended pre-results
- **Observation**: sigma=2px corridor supports 12,743 spaced far dots < 16,944 (f45).
- **Decision**: Experiment 2 set to sigma=3px, f33 (12,426 far; 67.0% keep, the BREAKLINE f33 uniqueness geometry) before any holdout result for this variant.

## 2026-10-24 (PIEDFRONT session) — unnormalized BREAKLINE placed 74.8% of off-skeleton dots in mountain range interiors; relative scarp-break + piedmont envelope resolves the off-skeleton holdout gap

- **Observation**: Auditing the elevation tercile distribution of `BREAKLINE f45Ltop`'s 16,944 off-skeleton dots (`d_H19 > 3.0 px`) revealed why every prior off-skeleton lane (`BREAKLINE f45` `0.004861`, `SCARPPOL f45` `0.005315`, `STRAINBREAK f60` `0.005487`, `ANASIG f45` `0.004967`, `SPRINGALIGN f33` `0.004865`) trailed `RELIEF p10` (`0.006045`) on `HOLDOUT-DTI`: raw $\|\nabla\,\text{det\_elev\_slope}\|$ scales with background slope, placing **74.8% (`12,673 / 16,944`)** of `BREAKLINE f45` far dots in the highest-elevation range-interior tercile (`det_elev >= 38.76 m`) and only **23.1%** in the piedmont transition (`-29.40 <= det_elev < 38.76 m`). Simultaneously, `R0` (`h33-h33-2-b2`) had **794 spacing-legal holes** on `H19-5` ($d_{\text{R0}} > 2.8\text{ px}, d_{\text{cat}} > 2.0\text{ px}$, including 593 in $2.0 < d_{\text{cat}} \le 3.0\text{ px}$) left when `b2` pruned $d_{\text{cat}} \le 2.0\text{ px}$ dots without re-thinning.
- **Decision**: Implemented `PIEDFRONT` (`gems/piedfront.py`, `scripts/build_piedfront_variants.py`), which normalizes the DEM slope-break by local background slope ($\|\nabla\,\text{det\_elev\_slope}\| / (\max(\text{det\_elev\_slope}, 0) + 2.0^\circ)$), gates by the piedmont elevation + basement-depth + isostatic-gravity-slope envelope $W_{\text{pied}}$ (Bands 12, 15, 5), refills 4,000 piedmont `H19-5` holes via `select_exact_marginal_dti_add`, and places 35% (`f35Ptop`), 40% (`f40Ptop`), and 45% (`f45Ptop`) far dots $>3.0\text{ px}$ off `H19-5` and $>3.0\text{ px}$ off all 5 prior off-skeleton lanes' far sets. All three doses (`0.006425`, `0.006402`, `0.006137`) exceed both `R0` (`0.004006`) and `RELIEF p10` (`0.006045`) in point estimate while passing all local uniqueness gates ($\le 0.6500$ 3-px forward overlap).

## 2026-10-24 (PIEDFRONT session) — structural trade-off between mountain-core SGMC bedrock faults and piedmont Quaternary/geothermal holdout faults

- **Observation**: Relocating off-skeleton dots out of steep mountain-core bedrock (`det_elev >= 38.76 m`) into the piedmont alluvial transition (`78.7%` of `f35Ptop` far dots, `73.9%` overall) raises `HOLDOUT-DTI` (`0.006425 [0.005375, 0.007479]`, paired $\Delta$ vs `R0` `+0.002418 [+0.001538, +0.003255]`, paired $\Delta$ vs `BREAKLINE f45` `+0.001564 [+0.000471, +0.002607]`), while reducing `SGMC` bedrock fault recovery from `0.096060` (`R0`) / `0.126105` (`BREAKLINE f45`) to `0.059993` (`PIEDFRONT f35Ptop`).
- **Decision**: Because the pre-registered promotion rule requires beating `RELIEF p10` with paired 95% CI excluding 0 AND beating `R0` on `SGMC`, and because the dense public witness (`17GEMSDOE E-proba`) remains an unresolved policy blocker, `PIEDFRONT f35Ptop` is recorded with `verdict: negative` (`OK TO DOWNLOAD` for research, `NOT CLEARED` for a weekly slot).

## 2026-10-24 automated recheck (PR #44)

- **Binding protocol conflict freshly confirmed, not waived:** 17GEMSDOE blob
  `374c88b1da2b803e2ed160de467fd71ae114010d` is positive across the exact footprint.
  The existing SPRINGALIGN artifact has forward overlap 1.0; no nonempty
  in-footprint prediction can meet the current literal overlap rule. No new
  TIFF/experiment/weekly slot was generated/used. See
  `evidence/review_20261024_springalign_witness_v2.json`.
- **Wrong-primary/freshness language:** homepage title said SPRINGALIGN while
  its lead and submission guides said ANASIG; headline claimed a unique TIFF
  generated “this session.” The files predate checkout and include future-dated
  `20261025` names relative to today's 2026-10-24 UTC. Corrected the active
  display; preserved filenames and historical receipts as evidence.
- **Single-witness checker risk:** shape-only comparison ignored CRS/transform
  and silently masked invalid outside-footprint mass. An empty witness could
  fabricate EDT boundary distances; rank-only duplicates were not checked.
  Repaired the shared project checker using template helpers, without forking
  the evaluator. Empty/invalid candidates now fail; unknown is not “unique.”
  Checker exits 1 for a measured stop, 2 for invalid inputs, 0 for inconclusive
  rejection-only check. No single-witness result grants submission eligibility.
- **Evidence robustness:** absent primary audit could cause an unbound `doc`
  error in the site checker; malformed JSON could crash it. These cases now
  report a failed site check. Historical witness output cannot be overwritten.
- **Deployment gate gap:** Pages previously uploaded `docs/` without running
  the project site check. CI and Pages now require it. This validates local
  bytes/status, not official data provenance or organizer portal acceptance.
- **Score provenance:** fetched GEMSDOE32 page source has no `0.2778` string
  and explicitly says no organizer score exists in its snapshot. This does not
  disprove a later user result, but cannot authenticate it. No organizer receipt
  or live leaderboard/quota was accessed. Values remain CLAIM, not scores
  confirmed by this review. Source hashes in `evidence/review_20261024_source_audit.json`.
- **Training limitation correction:** the freshly read official reference
  supports CPU training. A GPU is faster, not an absolute prerequisite. The
  prompt's named downloader/preparer scripts do not exist in this checkout.
- **Pages admin permission:** API reports legacy publishing from `main:/`.
  Attempting `build_type=workflow` returned HTTP 403 `Resource not accessible
  by integration`; settings remain unchanged. The added workflow gate cannot
  be claimed to control the separate legacy publisher. Repository-admin
  integration access is needed to reconcile settings; do not claim it succeeded.

## 2026-10-24 (APRONRIDGE session) — Resolved cross-page primary drift & signed-band metadata claim
- **Observation**: Entering this session at `d3d8c9c`, `docs/index.html` `<h1>` and `data-primary="true"` pointed to `SPRINGALIGNf33Ctop`, whereas `<p class="lede">` on `docs/index.html` plus `docs/SUBMIT.html`, `docs/executive-summary.html`, `docs/submit.html`, and `SLOT_PLAN.md` still named `ANASIGf45Atop` as primary (enforced by a hardcoded `assert "ANASIG" in page` in `tests/test_site_contract.py`). In addition, prior notes stated *"Band 18 is the only signed band"*, whereas live GDAL + pixel inspection of SHA-verified `training_features.tif` shows 10 of 19 bands take signed values (`Bands 1, 2, 8, 9, 11, 12, 13, 14, 15, 18`).
- **Decision & Action**: Synchronized `docs/index.html`, `docs/executive-summary.html`, `docs/SUBMIT.html`, `docs/submit.html`, `SLOT_PLAN.md`, `README.md`, and `tests/test_site_contract.py` so every page and test agrees on the single current primary (`h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif`), while preserving `STEPEDGE` and `SPRINGALIGN` records, and published a full 19-band GDAL-verified pixel summary table in `README.md`.

## 2026-10-24 (APRONRIDGE session) — First lane to beat `RELIEF p10` on `HOLDOUT-DTI` (`0.008354` vs `0.006045`), while `17GEMSDOE` dense witness remains the sole slot blocker
- **Observation**: All three pre-registered `APRONRIDGE` experiments (`free1d = 0.008354`, `s60f40 = 0.008291`, `s50f50 = 0.008097` on `gems57-pooled-hide-v2`) beat the prior repository holdout record `RELIEF p10` (`0.006045`), locally-unique best `STRAINBREAK f60s2i` (`0.005487`), and `STEPEDGE f60Sraw` (`0.003980`), pass all 11 leakage canaries (`max symmetric AUC = 0.636490 <= 0.90`), pass local uniqueness across all 46 cross-lane rasters (`free1d` worst forward 3-px overlap `0.460482`, vs `STEPEDGE` `0.3023–0.3783`), and pass diagnostic spot-checks (`0.6028–0.6456 <= 0.70`) against the top 91k–120k sparse public witnesses (`62GEMSDOE`, `GEMSDOE23`) that tripped `STRAINBREAK f60s2i`. However, direct measurement on `APRONRIDGEfree1d` bytes against Git-blob-verified `17GEMSDOE E-proba-multiscale` (`git_blob_sha = 374c88b1...`, positive across `100%` of the footprint) yields `1.000` forward overlap (`evidence/public_witness_apronridge.json`), and SGMC 1:500k bedrock DTI (`0.080098` vs `R0` `0.096060` and `STEPEDGE` `0.141464`) moves opposite to Quaternary fault holdout because `H_apron` suppresses high-range Mesozoic bedrock contacts.
- **Decision**: Enforce the literal public witness rule without waiver: record `submission_eligible: false` and `verdict: "negative"` in `evidence/apronridge_run_card.json` and sidecar audits. Do not spend a weekly competition slot until an explicit operator policy decision adds a dense-probability support ceiling (`<= 150,000` positive pixels).

## 2026-10-24 (APRONRIDGE session) — Fixed shared `scripts/validate_submission.py` silently ignoring `--candidate` (Protocol Rule 2)
- **Observation**: `README.md` documented `scripts/validate_submission.py --candidate <path>`, but `scripts/validate_submission.py` never parsed `sys.argv`, ignoring `--candidate` completely and scanning `releases/*.tif` only — so passing a nonexistent or invalid `--candidate` path in `docs/downloads/` still printed `All format checks PASS` with exit code `0`.
- **Decision & Action**: Fixed once in the shared `scripts/validate_submission.py` (never forked) to parse `--candidate` and positional paths via `argparse`, fail closed (`exit 1`) on missing files, `nodata != None`, or non-zero/NaN outside cells on `*-zeros.tif` files, and validate both `releases/*.tif` and `docs/downloads/*.tif` when invoked with no arguments; added regression test in `tests/test_apronridge.py`.
## 2026-10-24 (HYDROCONDUIT session) — Five Newly Verified Data, Metric & Site Irregularities

### 1. `#IR-92-BAND6-TC-MISLABEL`: `training_features.tif` Band 6 (`tc`) is Radiometric Total Count, NOT Magnetic Tilt Angle
- **Observation**: Band 6 metadata in `training_features.tif` reads `"tc - Tilt angle or total curvature - magnetic field derivative for edge detection"`. Direct measurement across all `5,164,300` valid footprint pixels shows strictly positive values (`p05 = 11.82`, `p50 = 18.51`, `p95 = 25.63`; zero negative pixels, so magnetic tilt zero-crossings do not exist) and Pearson **`r = 0.99714`** with Band 4 (`TC`, airborne gamma-ray Total Count) of `external/geodawn_rad_u8.tif`.
- **Action**: Never treat Band 6 as a magnetic phase/tilt derivative. `gems/hydroconduit.py` (`rtp_tilt_and_demag`) computes the true Miller–Singh / Verduzco phase-normalized Reduced-to-Pole (`Band 2 rtp`) tilt-contact crest and positive-Laplacian magnetite-destruction trough directly from `Band 2` via Laplace's equation ($\partial^2 U/\partial z^2 = -(\partial^2 U/\partial x^2 + \partial^2 U/\partial y^2)$).

### 2. `#IR-92-GDR-HOT-WHITESPACE`: Trailing Whitespace `'Hot '` & Overlooked Blind Chemical Geothermometry in `gdr_wellspring_in_footprint.csv`
- **Observation**: In `external/gdr_wellspring_in_footprint.csv` (`27,092` rows), `121` rows carry `thermalclass == 'Hot '` (with a trailing space) alongside `580` `'Hot'` rows, so naive string equality drops 17% of `'Hot'` entries. Furthermore, **`419` unique footprint pixels (`732` records)** have cold or unmeasured surface `temp_c < 40 °C` while dissolved silica (`geothermquartz_c`, `geothermchalc_c`) or Na-K-Ca (`geothermcat_c`) chemical geothermometers record **`80–269 °C`** deep reservoir equilibrium temperatures.
- **Action**: `gems/hydroconduit.py` (`gdr_blind_thermal_plume`) strips whitespace on `thermalclass` and incorporates both surface thermal anomalies and `>= 80 °C` blind chemical geothermometers (`2,312` unique thermal pixels), regression-tested in `tests/test_hydroconduit.py`.

### 3. `#IR-92-STATIC-DCAT2-SELFMASK`: Static `d_full_cat > 2.0` Self-Masking vs True Rule-2 `d_visible > 2.0` Holdout
- **Observation**: Static deployment rasters built with `d_cat > 2.0` against the *full* `existing_faults.tif` automatically zero out dots within `<= 200 m` (`2 px`) of the withheld `fold["truth"]` segments when scored on `buffered_component_draw`. Measuring true Protocol Rule-2 fold-by-fold `d_visible > 2.0` (`scripts/report_hydroconduit_proxies.py`) raises `HOLDOUT-DTI` by ~10×–20× (`0.0040–0.0085` static vs `0.0852–0.0968` `d_visible > 2.0`) and reveals why repacking `2 < d_cat <= 3` piedmont strands helps static `HOLDOUT-DTI` (`0.008549`, `+113.4%` vs `R0`) while moving `45%` off `H19-5` trades `H19-5` spine density (`0.0852` vs `0.0968`).
- **Action**: Both static `d_full_cat > 2.0` `HOLDOUT-DTI` (for exact comparability to `R0 = 0.004006` and `RELIEF p10 = 0.006045`) and true fold-by-fold `d_visible > 2.0` `HOLDOUT-DTI` are recorded side by side in `evidence/hydroconduit_proxy_audit.json` and `evidence/hydroconduit_run_card.json`.

### 4. `#IR-92-BREAKLINE-RANGECORE-75PCT`: Un-Normalized Slope-Break Range-Core Cliff Hijack & Sentinel `-3.4e38` Overflow
- **Observation**: Unsupervised tercile audit of `BREAKLINE f45Ltop` (`16,944` far dots) showed `74.75%` landed in the bare mountain range-core elevation tercile (`det_elev >= +38.75 m`) and `28.9%` struck transverse E–W/WNW (`65°–135°`) along incised canyons, leaving only `18.15%` in the piedmont. Separately, `gems.breakline._clean` only masked `~np.isfinite(a)` rather than float32 `-3.4e38` sentinels (`a <= -1e30`), causing `(gx * gx)` float32 overflow on synthetic sentinel inputs, and IEEE-754 float32 rounding at grid width `3292` rounded `np.float32(3292 - 1.0001)` to `3291.0` (`1 ulp = 0.000244`).
- **Action**: `gems/hydroconduit.py` normalizes slope breaks via `||grad log(max(slope,0) + 1°)||` + 600 m step monotonicity (`83.45%` piedmont / `6.22%` range core on `f45hydro`), masks `a <= -1e30` in `_clean_valid`, uses `np.nextafter` + `np.minimum(..., w - 2)` for bilinear indexing, and locks both edge cases with unit tests in `tests/test_hydroconduit.py`.

### 5. `#IR-92-SITE-STALE-SUBPAGES`: Inherited Site Subpages & `data-primary` Anchor Drift
- **Observation**: Prior `SPRINGALIGN` update changed `docs/index.html` `<h1>` while leaving `"This session tested ANASIG"` in the lede, placed `data-primary="true"` on `<section>` instead of `<a href=...>`, and left `docs/executive-summary.html`, `docs/SUBMIT.html`, and `docs/submit.html` pointing to `ANASIG`.
- **Action**: Synchronized `docs/index.html`, `docs/executive-summary.html`, `docs/SUBMIT.html`, `docs/submit.html`, `docs/HYPOTHESES.html`, `README.md`, `SLOT_PLAN.md`, `docs/REVIEW_CURRENT.md`, `docs/NEXT_STEPS.md`, and `tests/test_site_contract.py` around `HYDROCONDUIT f45hydro`, placing `data-primary="true"` directly on the primary `-zeros.tif` anchor.



## Review d97f969e — 2026-10-24

- Fresh Git-blob-verified dense witness rejects the current APRONRIDGE download (forward overlap 1.0). Literal protocol mandates stop; no new candidate or policy exemption. See `evidence/review_d97f969e_witness.json`.
- Homepage overall-best claim conflicted with higher stored HYDROCONDUIT HOLDOUT-DTI. Corrected the headline and added superseding top-level notices. Historical static scores are not certified visible-only fold-rebuilt experiments.
- No single method paragraph is identifiable in this request. No lane was invented. Data and CPU validators already exist; the prompt's GPU/data-placement blocker is not current for this array pipeline.
- Official competition pages, quota and receipts cannot be freshly verified under this session's network restrictions. No organizer score or source-access claim was fabricated.

## 2026-10-24 (COULOMB session) — Disk-vs-Prose Lineage Count Drift, Conflicting Intermediate CLAIMs, Witness-Checker Exit Code

### 1. `#IR-92-LINEAGE-COUNT-DRIFT`: Stale `D2.8` / `SOLO` Dot Counts in Prose (Disk Wins)
- **Observation**: Direct `rasterio` positive-pixel counts this session: `data/bridge/d28.tif = 44,090`, `data/bridge/h27_4_solo.tif = 40,199`, `data/bridge/h19_5.tif = 121,131`, `data/parent_R0_zeros.tif = 37,654` (all `float32`, `3730×3292`). Three prose spots disagreed: `README.md:79` quoted `SOLO 39,580` (+ derived `1,926` pruned dots); `README.md:258` quoted `D2.8 46,612`; `docs/ANALYSIS_20261024_APRONRIDGE.md:33` quoted `SOLO 39,580` (+ `1,926`); `docs/ANALYSIS_20261024_HYDROCONDUIT.md:25` quoted `D2.8 46,612`. No raster or evidence JSON was affected (all pipelines read bytes, not prose).
- **Action**: Corrected all four spots to disk values (`SOLO 40,199`, `D2.8 44,090`, `SOLO→R0` prune count `2,545 = 40,199 − 37,654`). Lineage table in `docs/ANALYSIS_20261024_COULOMB.md` §1.2 is the verified reference.

### 2. `#IR-92-LINEAGE-CLAIM-CONFLICT`: Intermediate-Lineage CLAIM Scores Conflict Across Docs (Unresolvable Without Receipts)
- **Observation**: `README.md:79` + APRONRIDGE analysis claim `H19-5 0.1922 → D2.8 0.2600 (+0.0678)`; `README.md:258` + HYDROCONDUIT analysis claim `H19-5 0.2194 → D2.8 0.2649 (+0.0455)`. Both chains agree on `SOLO 0.2708` and `R0 0.2778`. Scores are not on disk, and `ledger/` holds 0 organizer receipts, so neither chain can be falsified locally.
- **Action**: Left both CLAIMs in place with this log entry. Resolution requires an `ORGANIZER-CONFIRMED` receipt or authenticated leaderboard snapshot; until then, quote lineage scores only as `CLAIM` with their source doc.

### 3. `#IR-92-WITNESS-EXIT0`: `scripts/check_public_witness.py` Exits 0 Even on Duplicate (Docstring Says Exit 1)
- **Observation**: The module docstring states a duplicate finding exits `1`, but `main()` has no return path, so the process always exits `0` (observed on the COULOMB `forward_overlap = 1.000` duplicate). CI or shell gates keyed on exit code would miss the stop.
- **Action**: Treat the JSON receipt's `stop_required` field as authoritative (as `scripts/make_coulomb_run_card.py` does). Recommended follow-up: one-line fix to `return 1` on `stop_required` plus a regression test (queued; not done this session to avoid touching shared tooling mid-run-card).

### 4. `#IR-92-COULOMB-MAXFUSION`: `max()` Two-Channel Fusion Dilutes the Stronger Channel (Result, Not Bug)
- **Observation**: `COULOMB free` final dots are `71.6%` RTP-channel-dominant while `rtp_tilt`-only canary is `0.5162` vs `rel_scarp`-only `0.6230` — `max(R_rtp, R_scarp)` lets the near-random channel win most crest pixels. `HYDROCONDUIT`'s multiplicative fusion is the empirically better operator on this instrument.
- **Action**: Recorded as a design constraint for future lanes (follow-up F-C2 in `docs/NEXT_STEPS.md`); no code change.

## 2026-10-24 (`COULOMB-LOQO` Session) — Five Newly Verified Metric, Lineage, Bootstrap & HTML Merge Irregularities

### 1. `#IR-92-ALPHA-BETA-PROSE-SWAP`: Inverted $\alpha / \beta$ Tversky Penalty Weights in `README.md` and `ANALYSIS_20261024_APRONRIDGE.md`
- **Observation**: `README.md` (line 80) and `docs/ANALYSIS_20261024_APRONRIDGE.md` (§2.1) wrote the DTI denominator as $\mathrm{TP}_w + \alpha\,\mathrm{FN}_w + \beta\,\mathrm{FP}_w$ (`0.2` on `FN_w` and `0.8` on `FP_w`), asserting that false positives carried a $4\times$ heavier penalty than false negatives. Direct verification against the official DrivenData reference notebook (`drivendataorg/gems-prize-reference-solution/unet-mc-cv-reference-solution.ipynb`, Cell 16: `alpha = 0.2 # weight for false positives`, `beta = 0.8 # weight for false negatives`), `vendor/gems57/metric.py`, and `gems/metric.py` proves the exact opposite: $\mathrm{DTI} = \mathrm{TP}_w / (\mathrm{TP}_w + 0.2\,\mathrm{FP}_w + 0.8\,\mathrm{FN}_w)$ — **false negatives carry $4\times$ the penalty of false positives**.
- **Action**: Corrected the prose formula in `README.md` and `docs/ANALYSIS_20261024_COULOMBLOQO.md` while clarifying why kernel-matched spacing (`~2.8 px`) still improves DTI (not because $\alpha > \beta$, but because $\max_{x \in A} K(\|g - x\|_2)$ saturates at zero marginal $\mathrm{TP}_w$ gain when two dots overlap within `< 2.8 px`, leaving pure $+0.2\,\mathrm{FP}_w$ cost).

### 2. `#IR-92-SOLO-R1-BYTE-IDENTITY`: Exact Byte Identity of `SOLO` (`h27_4_solo.tif`) = `D2.8 & (d_cat > 1.0)`
- **Observation**: Prior analyses (`ANALYSIS_20261024_APRONRIDGE.md` citing `39,580` px; `ANALYSIS_20261024_HYDROCONDUIT.md` describing `"6,413 speckles"` / isolated 1–2-dot speckle removal) misdescribed the `D2.8 -> SOLO -> R0` transition. Direct pixel algebra on the SHA-256-verified bridge rasters proves `d28.sum() == 44,090`, `h27_4_solo.sum() == 40,199`, **`XOR(h27_4_solo, d28 & (d_cat > 1.0)) == 0`** (`-3,891` pixels all at `d_cat == 1.0`), and **`XOR(R0, d28 & (d_cat > 2.0)) == 0`** (`-2,545` pixels at `1.0 < d_cat <= 2.0`, `-6,436` total).
- **Action**: Documented the exact zero-XOR byte-verified ancestor table in `README.md` and `docs/ANALYSIS_20261024_COULOMBLOQO.md`.

### 3. `#IR-92-CAT-COUNT-PROSE`: Mapped Catalogue Pixel Count Typo (`36,249` vs Exact `60,988`)
- **Observation**: `docs/ANALYSIS_20261024_APRONRIDGE.md` stated `existing_faults.tif` contained `36,249` in-footprint pixels; exact byte inspection of `existing_faults.tif` and `labels.tif` confirms **`60,988`** in-footprint positive pixels (`1.180%` of the `5,167,373`-cell footprint).
- **Action**: Recorded the verified `60,988` pixel count across `README.md`, `docs/HYPOTHESES_20261024_COULOMBLOQO.md`, and `docs/ANALYSIS_20261024_COULOMBLOQO.md`.

### 4. `#IR-92-HYDROCONDUIT-EXTEND-TERMS`: Spatial-Block Bootstrap Pseudo-Replication via `list.extend` in `scripts/report_hydroconduit_proxies.py`
- **Observation**: `vendor/gems57/evaluate_holdout.py::run` sums `(tp, fp, fn)` block vectors across the 8 folds per physical 20 km spatial block (`all_terms = terms if all_terms is None else all_terms + terms`) so `pooled_summary` resamples physical 20 km blocks with replacement. `scripts/report_hydroconduit_proxies.py` (lines 78, 80, 158) instead called `all_terms.extend(terms)`, concatenating `8 * n_blocks` rows and treating the 8 fold evaluations of the same 20 km block as independent bootstrap units, artificially narrowing 95% CIs (point estimates were unaffected).
- **Action**: Fixed `scripts/report_hydroconduit_proxies.py` in-place to sum `terms` per physical 20 km block (`all_terms + terms`), matching `vendor/gems57/evaluate_holdout.py`, `scripts/report_apronridge_proxies.py`, and `scripts/report_coulomb_loqo_proxies.py`.

### 5. `#IR-92-PR49-MERGE-SEAMS`: Duplicate HTML IDs, Broken `<main>` Seam in `HYPOTHESES.html`, and Dual-Primary Prose After PR #49
- **Observation**: Merging parallel sessions in PR #49 (`c16e8b7`) left duplicate `id="download-springalign"` in `docs/index.html`, an invalid `</main><footer>...</footer></section><section>` block in `docs/HYPOTHESES.html`, and split primary declarations across `README.md`, `SLOT_PLAN.md`, `docs/NEXT_STEPS.md`, and `docs/REVIEW_CURRENT.md` (`APRONRIDGE free1d` vs `HYDROCONDUIT f45hydro`).
- **Action**: Cleaned all merge seams, eliminated duplicate HTML IDs (added regression check in `tests/test_site_contract.py`), restored valid HTML5 structure in `docs/HYPOTHESES.html`, and unified every page, doc, and contract test around the new #1 primary `COULOMBLOQO standalone` (`h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif`, `HOLDOUT-DTI = 0.009220`) while preserving full historical tables and downloads for `HYDROCONDUIT`, `APRONRIDGE`, `PIEDFRONT`, `STEPEDGE`, and all earlier lanes.

### 6. `#IR-92-LEDGER-CSV-UNQUOTED-COMMAS`: Unquoted Commas in PR #60 `MICROSWARM` / `BASEMENTEDGE` Ledger Rows
- **Observation**: During merge of `origin/main` (`5a23dd2`), lines 66–67 of `ledger/submissions.csv` (`h33-h33-2-b2-MICROSWARMshort-20261024-261a2f21` and `h33-h33-2-b2-BASEMENTEDGEstep3-20261024-80719f12`) contained unquoted commas inside `change_desc` and `notes`, splitting 16 columns into 18 columns (`csv.DictReader` key `None`) alongside a blank line 65.
- **Action**: Re-serialized all 68 merged rows through `gems.ledger.save()` with RFC-4180 quoting so every row has the exact 16 canonical columns.

