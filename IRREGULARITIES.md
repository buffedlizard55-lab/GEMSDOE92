# IRREGULARITIES

Only items that change a decision. Each says what was expected, what was found,
and what the human must decide.

---

## 1. The brief's opening gate cannot be executed: no inputs, no parent, no ledger

**Expected** (brief section 5): `registry/data_manifest.json` exists, R0 rebuilds
to its recorded sha256, `ledger/` and `SLOT_PLAN.md` describe prior work.

**Found.** The checkout of `buffedlizard55-lab/GEMSDOE92` at `b99296c` contains
exactly one file, an 11-byte `README.md`. `main` has the same single commit. No
branches, no tags, no releases, no LFS objects. There is no `registry/`,
`ledger/`, `releases/`, `docs/`, no data directory, and no R0 recipe, ranking,
or raster.

**Decision taken.** No variants and no rasters were produced this session. The
brief is explicit: *if you cannot rebuild it, stop and report; never approximate
the parent.* Producing a "close enough" R0 and calling it the parent would
poison every downstream comparison, and the ledger already records that at least
8 slots were burned on exact repeats — slot efficiency is the scarce resource
here, so a fabricated parent is worse than an idle session.

**Human must supply**: the pinned inputs, `registry/parents/R0.json` *with*
`expected_sha256`, and the ledger (or `ledger/raw_paste.txt`).

---

## 2. R0's 0.2778 is a CLAIM, and it is the number the whole plan leans on

**Found.** The brief labels 0.2778 as `CLAIM` until a receipt lands in
`ledger/`. There is no ledger in the repo, so there is no receipt.

**Why it changes a decision.** Slot 1 (`PRUNE-le3px`) is chosen because R0 is
the prune that paid +0.0070. If that +0.0070 was never real, the spine of this
plan is wrong. The plan is written to be falsified cheaply (slot 1 is the
cheapest test of exactly that mechanism), but the human should confirm the
0.2708 and 0.2778 numbers against their submission history before spending a
slot on their descendants.

**Ask**: paste the receipt lines into `ledger/raw_paste.txt`. `python -m gems
ledger` then reports best RECEIPT vs best CLAIM separately and stops treating
claims as scores.

---

## 3. The brief gives no closed form for `|G|`; a reading was chosen

**Found.** Section 2 states the algebra `DTI = T / (0.2T + 0.2(S-M) + 0.8|G|)`
and defines `T`, `S`, `M`, but not `|G|`. Marginal-gain ranking is sensitive to
that choice, and ranking is the backbone of MASS, CONCENTRATION and TRACKB.

**Decision taken.** `|G| = sum over truth pixels of (1 - best coverage)`, i.e.
truth mass no dot reaches. This is the reading under which the brief's own
shortcut holds: it makes `dDTI = c - 0.2*DTI` exactly, which is the "a dot pays
iff its credit > 0.2*DTI (~0.056 at 0.28)" sentence. `tests/test_metric.py::
test_gain_add_matches_brief_shortcut` asserts that identity, so if the reading is
wrong, the test fails rather than the ranking silently drifting.

**Residual risk.** If the organizers' `|G|` differs, *relative* ranking of
candidates is mostly preserved (both terms move monotonically), but absolute
gains are not trustworthy. Only trust the sign and ordering.

---

## 4. Competition-derived rasters sit in a PUBLIC repo — unresolved

**Found.** `buffedlizard55-lab/GEMSDOE92` is public (`isPrivate: false`).
Brief constraint 2 says keep competition rasters out of public repos and flag it
if they are already there. There are none in the repo today (nothing is in the
repo today), so this is a flag for the *next* session, not a current breach.

**Why it changes a decision.** The obvious next move is to commit
`releases/<id>.tif` and `releases/<id>-zeros.tif` per brief section 7. Committing
those to a public repo would publish rasters derived from competition data whose
data-use terms are unchecked.

**Decision taken (reversible on one word from the human).** `.gitignore` excludes
`data/` and `releases/*.tif`. The ledger stores sha256 + full parameters, so a
raster can be rebuilt byte-for-byte from the repo without the raster itself
being in the repo. If the human confirms the data-use terms permit redistributing
derived submissions, delete the relevant `.gitignore` lines and commit the tifs.

---

## 5. `TOP_PUBLIC` and the slot count are unset

`TOP_PUBLIC = ____` and "slots left `__`" are blanks only the human can fill, and
the brief forbids scraping the leaderboard (terms of use ban automated access).
The session plan was therefore written target-agnostic: every predicted change is
expressed as a delta against R0, never against a leaderboard position. No code
here ever needs `TOP_PUBLIC` to run.
