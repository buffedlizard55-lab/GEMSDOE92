# Three-pass review: session ee2370c1 (2026-10-27)

Labels: CLAIM = owner-reported score · MODEL = leaderboard-model estimate · HOLDOUT-DTI = shared gems57 instrument.
No number below is organizer-confirmed.

## Pass 1: implement and verify

* Restored the 12 SHA-256-pinned inputs (`scripts/restore_inputs.py`; all PIN OK).
* Streamed **99 public GEMSDOE repositories** across all five listed owners: 3,181 grid rasters and 2,060 unique SHA-256s,
  with 0 errors (`scripts/build_registry_cache.py` → `.cache/registry_v3/inventory.json`).
* Transcribed the 128 owner-reported scores (`ledger/claims_20261027.txt`) and matched 123 of them byte-for-byte. Eight ambiguous
  matches all resolve to support-identical files (`evidence/claims_matched_20261027.json`).
* Fitted the metric-structured leaderboard model, LBM-v1, with 12 parameters. Grouped (leave-one-lineage-out) CV: RMSE 0.0206 and
  Spearman 0.964. With the whole R0/H19 family held out, RMSE is 0.0060 (`evidence/lbm_v1_model.json`).
* Ran EXP1, a two-pool capped exact greedy followed by repair, and built the TIFF with the shared writer. Then re-read it from disk:
  all 11 shared gates passed, plus gems57 validate. The PI-1 audit over 2,060 rasters gave worst overlap 0.6845 and |ρ| 0.113.

## Pass 2: review and fix (defects found by the automated checks)

1. **One dot within 200 m of a mapped fault.** The first build (`ee29e682`) failed the shared `distance_from_catalogue` gate. Cells
   with d_cat ≤ 2 are now ineligible, which matches the R0 finding that such dots carry no credit. The superseded files were deleted.
2. **Model-specification fragility.** Under an almost equally good consensus definition (G-set CLAIM ≥ 0.15), the first candidate
   *tied* R0 (0.2729 vs 0.2731). The candidate was re-placed on the **mean density of both fits**. Now every specification ranks it
   above R0: 0.332 / 0.324 / 0.344 / 0.305 vs about 0.273. A robustness gate was added to the build.
3. **Trust-region cap below R0's own share.** The G015 consensus cap (0.55) was lower than R0's own 0.62. It was reset to the observed
   maximum plus 0.05 (0.78).
4. **Cap-constrained placement deadlocked and churned** when hundreds of registry halos all cover the same high-value cells. It was
   replaced by a union cap on the 30 dominant offenders, followed by repair: novel dots are added outside every violator's halo,
   chosen by exact marginal gain.
5. **Slow O(N) surface Spearman.** It was replaced by an exact O(support) formula. Tests confirm it equals scipy to 1e-12.
6. **Surface-check semantics.** A surface has no dots. The binding pre-placement check is therefore rank correlation (0.495), and the
   top-N overlap (1.00) is reported as a diagnostic (PI-1b, IR-0127-1).

## Pass 3: recheck against the request

| Request | Status |
|---|---|
| Nine-site executive summary with file / estimate / unique table | `docs/nine-sites.html` and the main page. All nine best files are copies of rasters at other sites. |
| PhD-level explanation of 0.2778 and whether it can be beaten | `docs/WHY_0_2778.md`. The nested-lineage algebra shows the collar dots carried zero truth credit. |
| Generate a UNIQUE TIF and make OK/NOT-OK obvious | Done. `gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif`, verdict **promote**, OK TO SUBMIT on the first screen. |
| Estimate scores | `scripts/lbm_estimate.py`, with MODEL label, bootstrap and alternative specifications |
| Validation gates before clearance | format, PI-1 uniqueness, MODEL q05 > 0.2778, robustness, canaries. The holdout is reported (IR-0127-2). |
| 3–5 hypotheses, ranked | `docs/HYPOTHESES_20261027_LBM.md`. H1 was run; H4 (1 m lidar) is blocked in this sandbox. |
| Spatially blocked holdout of the top hypothesis | Run: HOLDOUT-DTI 0.0197 [0.0149, 0.0250] vs R0 recipe 0.0978 (22,663 withheld). Its validity for the leaderboard is measured as Spearman 0.13. |
| Leakage canaries | max single-feature AUC 0.753 ≤ 0.90 |
| Run card JSON with every protocol field | `docs/downloads/…_run_card.json` |
| Prompt in README and SESSION_PROMPT | Done, verbatim summary at the top of SESSION_PROMPT.md, linked first in README |
| How-to-submit page, portal error fix | `docs/how-to-submit.html`, including a repair snippet |
| Clean site with official links, submission first | `docs/index.html`; the old page is `docs/archive.html` |
| Budget of 3 experiments | 1 hypothesis lane (EXP1). Iterations inside it: v1 density → ensemble density. One shared holdout and one validity audit. No slot used. |

## Limitations (not hidden)

* The estimate is fitted to CLAIMs from the public split. Private and Phase-2 scores can differ.
* The candidate concentrates dots more strongly in the consensus class than any scored raster did (55% vs 49%).
* PI-1 is an interpretation. Under the literal reading every candidate is a duplicate.
* Weekly slots and the final pick are human decisions. Record the score after submitting.
