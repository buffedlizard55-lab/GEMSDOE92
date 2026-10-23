# Mechanism Cards — MASS axis (2026-10-23)

Parent: h33-h33-2-b2 (GEMSDOE32), 37,654 dots, none within 2px of catalogue, CLAIM 0.2778
Ranking: H19-5 continuous field (121k px) value at dot location, proxy for belief strength.

## h33-h33-2-b2-MASS_D10-20261023-e26a6cb8
- **Hypothesis**: Mass optimum test. If marginal credit of lowest-ranked dots < 0.2*DTI (~0.056 at 0.28), dropping them raises DTI. If next-ranked dots have credit > bar, adding them raises DTI.
- **Mechanism**: DTI = T / (0.2T+0.2(S-M)+0.8|G|). For isolated truth, dot pays iff credit >0.2*DTI. Line-like truth lowers bar. Ranking by H19-5 approximates credit expectation.
- **Non-fault mimic**: H19-5 high values can be lithologic contacts, alteration halos, or topographic ridges without faulting; dropping them may remove false positives but also true faults with weak expression.
- **Predicted sign and size**: slight gain if low-ranked dots are noise; risk loss if they carry credit. MASS_D10: predicted +0.002 to +0.008 if low-ranked dots are noise (based on live inversion: removing 3,891 dots at 0.031 credit/dot raised 0.2600->0.2708). MASS_A10: predicted -0.001 to -0.005 if marginal credit < bar. SWAP10: predicted +0.001 to +0.006 if replacement improves avg credit.
- **Falsifier**: If MASS_D10 live score < parent by >0.01, low-ranked dots carry above-bar credit and mass optimum is higher. If MASS_A10 live > parent, budget is not yet saturated.
- **Details**: parent h33-h33-2-b2, n_dots 33889, pct_changed 10.0%, file releases/h33-h33-2-b2-MASS_D10-20261023-e26a6cb8-zeros.tif, sha8 e26a6cb8

## h33-h33-2-b2-MASS_A10-20261023-e5613a00
- **Hypothesis**: Mass optimum test. If marginal credit of lowest-ranked dots < 0.2*DTI (~0.056 at 0.28), dropping them raises DTI. If next-ranked dots have credit > bar, adding them raises DTI.
- **Mechanism**: DTI = T / (0.2T+0.2(S-M)+0.8|G|). For isolated truth, dot pays iff credit >0.2*DTI. Line-like truth lowers bar. Ranking by H19-5 approximates credit expectation.
- **Non-fault mimic**: H19-5 high values can be lithologic contacts, alteration halos, or topographic ridges without faulting; dropping them may remove false positives but also true faults with weak expression.
- **Predicted sign and size**: likely drop if marginal credit <0.056; test of budget optimum. MASS_D10: predicted +0.002 to +0.008 if low-ranked dots are noise (based on live inversion: removing 3,891 dots at 0.031 credit/dot raised 0.2600->0.2708). MASS_A10: predicted -0.001 to -0.005 if marginal credit < bar. SWAP10: predicted +0.001 to +0.006 if replacement improves avg credit.
- **Falsifier**: If MASS_D10 live score < parent by >0.01, low-ranked dots carry above-bar credit and mass optimum is higher. If MASS_A10 live > parent, budget is not yet saturated.
- **Details**: parent h33-h33-2-b2, n_dots 41419, pct_changed 10.0%, file releases/h33-h33-2-b2-MASS_A10-20261023-e5613a00-zeros.tif, sha8 e5613a00

## h33-h33-2-b2-MASS_SWAP10-20261023-3e776063
- **Hypothesis**: Mass optimum test. If marginal credit of lowest-ranked dots < 0.2*DTI (~0.056 at 0.28), dropping them raises DTI. If next-ranked dots have credit > bar, adding them raises DTI.
- **Mechanism**: DTI = T / (0.2T+0.2(S-M)+0.8|G|). For isolated truth, dot pays iff credit >0.2*DTI. Line-like truth lowers bar. Ranking by H19-5 approximates credit expectation.
- **Non-fault mimic**: H19-5 high values can be lithologic contacts, alteration halos, or topographic ridges without faulting; dropping them may remove false positives but also true faults with weak expression.
- **Predicted sign and size**: best chance: keep budget, improve avg credit. MASS_D10: predicted +0.002 to +0.008 if low-ranked dots are noise (based on live inversion: removing 3,891 dots at 0.031 credit/dot raised 0.2600->0.2708). MASS_A10: predicted -0.001 to -0.005 if marginal credit < bar. SWAP10: predicted +0.001 to +0.006 if replacement improves avg credit.
- **Falsifier**: If MASS_D10 live score < parent by >0.01, low-ranked dots carry above-bar credit and mass optimum is higher. If MASS_A10 live > parent, budget is not yet saturated.
- **Details**: parent h33-h33-2-b2, n_dots 37654, pct_changed 10.0%, file releases/h33-h33-2-b2-MASS_SWAP10-20261023-3e776063-zeros.tif, sha8 3e776063


---

# Mechanism Cards — PRUNE axis (2026-10-23)

Parent: h33-h33-2-b2 (GEMSDOE32), 37,654 unit-mass dots, sha256 `baeae321…077dd`
verified byte-for-byte this session. Min catalogue distance 2.236 px; 0 dots
within 2 px, but **2,171 within 3 px (5.77%)**, 3,825 within 4 px (10.16%),
5,637 within 5 px (14.97%).

Design: remove every parent dot within R px of the catalogue and refill to hold
the count at 37,654 by moving each removed dot to its **nearest legal pixel**
(distance > R, in footprint, not on catalogue, on the H19-5 surface). Nearest
refill keeps every other property of the file fixed, so the only variable is the
distance rule. A ranking-based refill would have imported the MASS axis and
reproduced the confound that made the previous session's MASS files ambiguous.

## Shared hypothesis
Dots sitting on or beside a known trace are credited against *catalogue* truth,
which the organizers mask out. They therefore add to `S` (marginal credit to
`T` only through new-fault truth nearby) while the pixels they sit on are not
scored. Removing them should cut dead denominator mass. The forum answer says
new-fault truth **can** lie within 300 m (3 px) of known traces, so this helps
only up to the radius where real new faults start being deleted.

## Shared mechanism
`DTI = T / (0.2T + 0.2(S−M) + 0.8|G|)`. Each dot contributes `+1` to `S` and at
most `M ≤ 1` per unit; a dot whose marginal credit `c` is below `0.2·DTI`
(≈0.056 at 0.28) lowers the ratio. Dots adjacent to known traces are the
likeliest to have `c` below that bar, because their nearest truth is already
credited.

## Shared non-fault mimic
A dot near a known trace can still be genuinely new: unmapped splays,
step-overs, and along-strike extensions of mapped faults are exactly the
Phase-2 target ("newly mapped geometry of existing systems",
https://community.drivendata.org/t/where-do-you-draw-the-line/11536). So the
prune can delete precisely the highest-value pixels. This is not a nuisance
term; it is the competing hypothesis.

## h33-h33-2-b2-PRUNE_B3-20261023-3d2403c7
- **Value**: remove dots within 3 px (2,171 = 5.77%), refill 2,171, count held.
- **Predicted sign and size**: **+0.002 to +0.006 MODEL**. 3 px is 300 m, the
  stated positional uncertainty of the 400 m-spaced GeoDAWN survey, so dots
  inside it are more likely positional scatter than distinct faults.
- **Falsifier**: live score below parent by >0.01. That would say dots within
  300 m of known traces carry above-bar credit and the distance prior is wrong.
- **This is the primary bet of the session.**

## h33-h33-2-b2-PRUNE_B4-20261023-78e893d7
- **Value**: remove within 4 px (3,825 = 10.16%), refill 3,825, count held.
- **Predicted sign and size**: **+0.001 to +0.004 MODEL**, less confident. 4 px
  = 400 m is past the survey's positional uncertainty, so this dose starts
  eating real new-fault pixels; it should pay only if the dead mass is thick.
- **Falsifier**: if B4 < B3 by >0.005 while both sit above the parent, the
  optimum is between 3 and 4 px.

## h33-h33-2-b2-PRUNE_B5-20261023-85cd67ad
- **Value**: remove within 5 px (5,637 = 14.97%), refill 5,637, count held.
- **Predicted sign and size**: **−0.002 to +0.002 MODEL**, i.e. no gain
  expected. This is the dose-response's negative control: if the mechanism is
  real and bounded, B5 should be the worst of the three.
- **Falsifier**: if B5 is the *best* of the three, the distance effect is
  monotone and unbounded in this range, which contradicts the 300 m survey
  geometry and should redirect the next session to PRUNE B8/B10 rather than to
  a new axis.

## Reading the session as a whole
The three doses are a dose-response curve, not three independent bets. Outcomes:

| pattern | reading | next |
|---|---|---|
| B3 > B4 > parent > B5 | peak near 3 px, mechanism real and bounded | build `PRUNE_B3 + CONCENTRATION` |
| monotone B5 > B4 > B3 > parent | prior is real and unbounded here | go deeper (B8, B10) |
| all ≤ parent | distance prior is false | abandon PRUNE, the 0.2708→0.2778 step was false-positive removal |
| B3 > parent, B4 ≈ B3 | flat optimum 3–4 px | prefer B3 (fewer deletions, less risk) |
