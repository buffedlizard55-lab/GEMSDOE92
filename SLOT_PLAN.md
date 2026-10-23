# SLOT_PLAN — GEMS Prize #306

**Parent:** R0 `h33-h33-2-b2`; 37,654 dots; both raster SHA-256 values rebuilt exactly this session.
`0.2778` is **CLAIM**, not RECEIPT. `TOP_PUBLIC` and the remaining entity slots are unknown until the
human supplies them. Nothing is submitted automatically.

**Axis this session: CONCENTRATION** (chosen autonomously — MASS and PRUNE values already exist in the
ledger; SNAP and RELIEF need TMI/gravity/detrended-elevation bands that are only available inside the
multipart `training_features.tif`, not separately pinned). New values `C10_b5km`, `C15_b5km`,
`C20_b5km` appear once each; no (parent, axis, value) pair or raster hash repeats.

## What the CONCENTRATION result changes

Nothing here is recommended for a slot. Three local facts drive that:

1. **R0 is locally near-optimal under block reallocation.** Every dose loses against the independent
   SGMC off-catalogue control, monotonically: −0.004851 / −0.007066 / −0.010416.
2. **The loss is mostly generic.** A randomised-block null loses −0.012365 at 20%; the parent's own
   evidence surface loses −0.010423. The ordering buys back ~+0.002 of control, but refill pixels are
   the neighbours Poisson-disk thinning already discarded, so the ceiling sits below R0.
3. **The instruments disagree in sign.** The catalogue hide-and-recover holdout says +0.0018 at every
   dose; the SGMC control says the opposite. The live metric scores new-fault pixels only, so the SGMC
   control is the better analogue — but at three submissions a week the disagreement is the finding.

**Decision rule:** live changes under 0.01 are no evidence. No dose in this grid is predicted to clear
that bar in either direction, so the expected value of a slot spent here is near zero.

## Next three live slots

`TOP_PUBLIC`, the date, and the current rolling-week count must be confirmed before any of these.

1. **Get a RECEIPT on the incumbent first.** Submit `h33-h33-2-b2` itself, or the already-built
   `h33-h33-2-b2-PRUNEp3.5px-refill-20261023-a121a277` if the collar hypothesis is the one the human
   most wants tested. Until one receipt exists every later comparison is against a CLAIM of 0.2778.
2. **If a slot goes to CONCENTRATION anyway**, use
   `h33-h33-2-b2-CONC_C10_b5km-20261023-3127dbd4` (10.00% moved; MODEL −0.001, range [−0.021,+0.011]).
   It is the cheapest test of "is R0 locally optimal?". A receipt gain ≥ +0.01 would vindicate the
   hide-and-recover instrument over the SGMC control and re-open the whole axis.
3. **Hold the third slot** until slot 1 returns. Do not spend it on `C15`/`C20`: their predicted
   changes (−0.003, −0.005) are further below the no-evidence threshold and add no new mechanism.

## Proposed axes — not built this session

- **SUPPORT_EXPANSION** — refill off the H19-5 ridge support. *Mechanism:* the dose-response loss is
  caused by refilling onto thinned-away neighbours (redundant); pixels never on H19-5 are uncorrelated
  with existing dots, so their marginal credit is not cannibalised. *Confounder:* off-support pixels
  have ~0.08 of the evidence weight, so most are pure denominator cost. *Falsifier:* no ≥ +0.01
  receipt gain over the parent at matched count.
- **DENSIFY_RIDGE** — instead of moving mass between blocks, halve the along-strike spacing on the
  top-ranked ridge segments only, funded by deleting whole low-ranked segments. *Mechanism:* line-like
  truth lowers the per-dot credit bar, so a denser chain on a strongly expressed lineament converts
  several truth pixels per dot. *Confounder:* lithologic contacts and dikes are also lineament-continuous.
  *Falsifier:* no ≥ +0.01 gain over `CONC_C10_b5km` at the same count.
- **NETWORK_PRIOR** — allocate by catalogue step-over / intersection / termination density. Measured
  this session and rejected as a block prior: ρ ≈ +0.04 to +0.11 with independent-fault yield, and at
  20% it scored worse than the randomised null.
- **SNAP / RELIEF** — blocked only on inputs. Both need named bands; today they are indices 3, 18 and
  19 inside a 419 MB multipart raster with no published band list. If the human supplies a band list,
  both become buildable and SNAP (mean displacement reported, no count change) is the cleaner test.

## Weeks to 2026-12-03

- **Weeks 1–2:** spend only confirmed slots, in the order above. Record every receipt. Do not combine
  CONCENTRATION with anything: its local evidence is negative or contradictory at every dose tested.
- **Weeks 3–4:** combine only axes with a receipt-backed gain ≥ 0.01. On current evidence the only
  combinable candidate is the PRUNE collar, and only after its receipt lands.
- **Weeks 5–6:** pick one blind final file and one fallback; re-run `python -m gems validate` on both;
  confirm the deadline on the official competition page; complete the generative-AI disclosure in
  `AI_USE.md` before 2026-12-03.

**Standing caution.** The catalogue hide-and-recover holdout previously correlated −0.87 to +0.54 with
live scores (n = 12–14), and this session it moved opposite to the SGMC control. Treat both as
diagnostics. Receipts are the only decision anchor.
