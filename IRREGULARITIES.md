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
