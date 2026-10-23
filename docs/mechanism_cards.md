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

