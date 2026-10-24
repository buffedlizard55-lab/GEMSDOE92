# PhD Analysis — 2026-10-24 `COULOMB` Session: Why `GEMSDOE32` Leads the Listed Sites (`0.2778` `[CLAIM]`), What Orientation-Resolved Opening Taught Us, and Whether `0.2778` Can Be Beaten

Evidence labels: every local number below is `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, 22,663 withheld
positives, 8 buffered folds, 1,000 paired spatial-cluster bootstraps), `PROXY` (USGS SGMC control),
`REGISTRY-MEASUREMENT`, or `CLAIM`. No `ORGANIZER-CONFIRMED` receipt exists in `ledger/` (0 recorded);
no statement here claims a competition score.

---

## 1. Why `h33-h33-2-b2` (`GEMSDOE32`, `0.2778` `[CLAIM]`) leads the listed GEMSDOE sites

### 1.1 The scoring geometry it exploits (verified against the official metric)

The competition scores a Distance-weighted Tversky Index with `α = 0.2`, `β = 0.8` and a 300 m
triangular kernel ([problem p.967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[reference solution](https://github.com/drivendataorg/gems-prize-reference-solution),
[rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)). Three consequences follow algebraically
(verified in-repo: `vendor/gems57/metric.py` matches the official worked example `3.00/1.89/2.00 →
0.6027 ≈ 0.60` and `dti_exact` matches `dti_bruteforce` to `1.7e-16`):

1. **False positives cost 4× false negatives** (`β/α = 0.8/0.2`) per unit kernel mass, so deleting a
   no-credit dot is worth 4× adding a fully-credited one at the margin.
2. **Coverage is max-pooled** (`max_y K(‖x−y‖)·P(y)`): two dots inside one 300 m kernel of the same
   truth pixel earn (nearly) the credit of one while paying double FP mass. Redundant dots are pure loss.
3. **Known-catalogue pixels are masked**: any mass on `existing_faults.tif` earns nothing while paying
   full FP cost.

### 1.2 The four operations, with disk-measured counts (this session re-verified)

| Step | Operation | Dots (measured from `data/` this session) | Reported value `[CLAIM]` |
|---|---|---:|---|
| `H19-5` | 1-px multi-line worm-crest skeleton | **121,131** | `0.1922` |
| `D2.8` | Poisson-disk de-aliasing at 2.828 px ≈ 283 m (kernel-matched) | **44,090** | `0.2600` |
| `SOLO` | Isolated 1–2-dot speckle pruning | **40,199** | `0.2708` |
| `R0/B2` | Delete `d_cat ≤ 2.0 px` (6,436 dots), zeros-outside encoding | **37,654** | `0.2778` |

Each operation removes a class of mass the metric prices punitively: sub-kernel redundancy (`D2.8`,
`+0.0678` `[CLAIM]`, the largest jump — exactly what max-pooling predicts), unsupported speckle
(`SOLO`, `+0.0108`), and masked catalogue mass (`B2`, `+0.0070`), while the zeros-outside encoding
avoids the portal's `Predicted values must be in range [0, 1]` rejection of NaN-outside files. The
parent record (`registry/parents/R0.json`, byte + invariant re-verified) confirms `min d_cat =
2.236 px` with `2,171` dots retained in the `2–3 px` collar — mass close enough to earn kernel credit
from near-catalogue truth without sitting on masked pixels.

> **Doc-hygiene note (this session):** two stale counts in repo prose disagree with disk:
> `docs/...HYDROCONDUIT...` quoted `D2.8` as `46,612` (disk: **44,090**) and `README.md` quoted `SOLO`
> as `39,580` (disk: **40,199**). Disk wins; logged in `IRREGULARITIES.md`. Neither affects any raster.

### 1.3 Why the other listed sites trail (mechanistic inference, not proof)

Attributing leaderboard gaps requires exact artifacts under identical scoring conditions, which no
checkout here has — so this is inference from the metric algebra plus each site's described method:
sites emitting dense probability surfaces or un-thinned skeletons pay the `β = 0.8` FP penalty on
mass that max-pooling cannot credit; sites predicting on/near mapped catalogue traces pay for masked
pixels. `GEMSDOE32` is the listed site that most completely removed all three dead-mass classes while
keeping skeleton coverage. The prompt's `0.3195` / `0.4413` figures are conflicting
`LEADERBOARD-SNAPSHOT` claims with no authenticated raster or method receipt here; a score alone does
not reveal its feature set, and this project has not established that any candidate beats `0.2778`
`[CLAIM]` on the hidden test set.

---

## 2. What the `COULOMB` session tested and measured

Pre-registration: `docs/HYPOTHESES_20261024_COULOMB.md`. Screen: `evidence/coulomb_preplacement_screen.json`
(gate-zero reproduced `BREAKLINE-L` to the digit: canary `0.621604`, far-SGMC `0.072325). Builder:
`scripts/build_coulomb_variants.py` (3/3 budget consumed, all Tier-1 repulsion, pools ≈ 1.1M px).
Report: `evidence/coulomb_proxy_audit.json` (controls reproduced exactly: `R0 0.004006`, `RELIEF p10
0.006045`, `BREAKLINE f45 0.004861`, `APRONRIDGE free1d 0.008354`, `HYDROCONDUIT f45hydro 0.008549`).

| Arm | `HOLDOUT-DTI` [95% CI] | Paired Δ vs `R0` | Paired Δ vs `HYDROCONDUIT` (`0.008549` bar) | `SGMC PROXY` | Worst local overlap |
|---|---|---|---|---|---|
| `seismo` (lead) | `0.005808 [0.004846, 0.006809]` | `+0.001802 [+0.000616, +0.002924]` ✓ | `−0.002741 [−0.004137, −0.001382]` ✗ | `0.035654` | `0.2661` ✓ |
| `free` | `0.005689 [0.004744, 0.006688]` | `+0.001682 [+0.000537, +0.002833]` ✓ | `−0.002861 [−0.004167, −0.001505]` ✗ | `0.035122` | `0.2632` ✓ |
| `open` | `0.005184 [0.004188, 0.006256]` | `+0.001178 [+0.000013, +0.002275]` ✓ | `−0.003365 [−0.004763, −0.001901]` ✗ | `0.039945` | `0.2904` ✓ |

Canaries: all 20 report fields `≤ 0.90` (max symmetric AUC `0.622959`, the relative-scarp component).
Format: `10/10` gates + `gems57.validate` PASS on all 3 served `-zeros.tif` files. Binding public
witness: forward overlap `1.000` vs `17GEMSDOE E-proba` (`evidence/public_witness_coulomb.json`,
halo covers 100% of footprint) → **duplicate stop, `verdict: negative`, `submission_eligible: false`**.
Sparse diagnostic (5 witnesses, not clearance): max `0.4831 ≤ 0.70`.

### 2.1 The mechanism of the shortfall (three measured facts)

1. **The Coulomb weight carries almost no catalogue signal.** Single-feature canary: `O_coulomb`-only
   `0.5423`, vs `rel_scarp`-only `0.6230` (the strongest component screened this session — above the
   `BREAKLINE-L` `0.6216` baseline). Multiplying the best channel by a near-random orientation weight
   reshuffles emission away from high-credit collar-adjacent scarps: `free` places only `44.8%` of dots
   in the piedmont (vs `83.4%` of `HYDROCONDUIT` far dots) and `37.2%` in the deep basin, where neither
   the catalogue holdout nor SGMC can credit them.
2. **`max()` channel fusion lets the weaker channel dominate emission.** Final `free` dots are `71.6%`
   RTP-dominant, yet `rtp_tilt`-only canary is `0.5162` (near-random) while `rel_scarp`-only is `0.6230`.
   `HYDROCONDUIT`'s multiplicative `scarp × conduit` fusion (not `max`) is the empirically better answer
   to two-channel combination on this instrument.
3. **100 km seismicity kernels add nothing at 100 m.** `seismo_prior`-only canary `0.5249`; `seismo` vs
   `free` paired Δ `+0.000120 [−0.000212, +0.000441]` (statistical tie); geography nearly identical
   (`43.8%` vs `44.8%` piedmont). Rank-2 fusion is correctly recorded as a null result, and standalone
   Rank-2/3/4 lanes (`0.5249`/`0.5167`/`0.5166` screen canaries) should not be built without a
   sharper localizer.

### 2.2 Two positive confirmations (ablations that worked as designed)

- **Apron ablation:** removing `H_apron` (`open`: `22.6%` piedmont, `48.1%` basin, `29.3%` range) drops
  `HOLDOUT-DTI` by `−0.000505` vs `free` while raising `SGMC` (`0.0399` vs `0.0351`) — replicating the
  piedmont-holdout / bedrock-SGMC trade-off direction and confirming the apron helps the catalogue
  instrument.
- **Standalone + Tier-1 repulsion separates cleanly:** all 3 arms are locally unique by wide margins
  (`0.263–0.290 ≤ 0.70`, `|φ| ≤ 0.024`) with only `1.7–2.3%` exact-`R0` overlap — the standalone-emission
  construction (APRONRIDGE pattern) again proves the reliable uniqueness mechanism.

### 2.3 Honest caveats (what this session can and cannot conclude)

- The static `d_full_cat > 2.0` holdout self-masks withheld faults within `≤ 200 m`
  (`#IR-92-STATIC-DCAT2-SELFMASK`), so it prices the `2–3 px` collar — exactly where Coulomb
  opening sends *fewer* dots than piedmont repacking. A fold-visible Rule-2 evaluation could rank
  Coulomb differently; it was not run here (budget consumed) and is queued in `NEXT_STEPS.md`.
- `SGMC` bedrock faults and the catalogue holdout price different truths; Coulomb's SGMC collapse
  (`0.035` vs `R0 0.096`) shows it finds neither truth well — the one unambiguous cross-instrument
  failure of this lane.
- Nothing here tests the live leaderboard: only an `ORGANIZER-CONFIRMED` receipt (Blocker 0, still `0`
  recorded) can say whether orientation-resolved opening helps on expert-mapped new faults.

---

## 3. Can we generate a submission scoring higher than `0.2778`? (judgment)

**On the local instruments: not this session, and the reason is informative.** The repo's holdout-best
ladder (`R0 0.004006 → RELIEF p10 0.006045 → PIEDFRONT f35 0.006425 → APRONRIDGE free1d 0.008354 →
HYDROCONDUIT f45hydro 0.008549`) rewards, in order: kernel-matched spacing, piedmont concentration,
hole repair, and multiplicative multi-physics corroboration — all mechanisms that concentrate mass in
the scoring collar of near-catalogue truth. `COULOMB` (`0.005808` best) is the first lane to test
whether *orientation-resolved geomechanics* adds independent signal, and the answer on the catalogue
instrument is no: GPS strain resolved onto strike (`0.5423`) and 100-km seismicity (`0.5249`) are too
smooth and too weakly coupled to Quaternary scarp locations to beat repacking + corroboration at
100 m posting.

**On the leaderboard: unknown and unknowable from here.** `0.2778` is a `CLAIM` without a receipt in
this repo; the hidden test set is expert-mapped new faults, not withheld catalogue; and the highest-
leverage channel — the 1 m DEM label instrument itself (`LIDAR1M-LAHONTAN`, Rank 5, HELD: needs
DrivenData-login `1m_DEM_links.csv` + `apps.nationalmap.gov`, both unreachable from this sandbox) —
remains untested by every lane in this repo. The structural recommendation stands: obtain one
`ORGANIZER-CONFIRMED` receipt to calibrate which local instrument (if any) predicts the hidden test
set before spending further build budgets on smoother physics.

**Session verdict: negative (deliverable).** Three format-valid, locally-unique, byte-unique
standalone GeoTIFFs that beat `R0` on `HOLDOUT-DTI` but trail the `0.008549` bar with CIs excluding
promotion, plus falsification of four screened hypotheses (Coulomb opening, seismicity fusion,
TMI-tilt ratio, MT-edge) at 100 m. **OK TO DOWNLOAD for research; NOT CLEARED for a weekly slot**
(dense-witness duplicate stop). No slot used; budget consumed (3/3 experiments).
