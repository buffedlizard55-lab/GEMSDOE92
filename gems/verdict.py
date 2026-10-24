"""Derive the three public status lines from evidence (never typed into HTML).

OK TO DOWNLOAD      format gates pass on the bytes served (single float32 band, EPSG:32611, 3730x3292,
                    template transform, finite, values in [0,1], zero outside the footprint, zero dots
                    on or within 3 px of the catalogue, sha256 recorded).  Prevents the portal error
                    "Predicted values must be in range [0, 1]".
OK TO SUBMIT        OK TO DOWNLOAD  AND  the decisive uniqueness tier (registry/uniqueness_policy.json)
                    passes both phases  AND  the leakage canary passes  AND  the MODEL kill criterion is
                    not triggered.  This is validity + non-duplication, i.e. "the portal will take it and
                    it is not a copy of a previous submission".  It is NOT a score and NOT a recommendation.
SLOT VERDICT        the protocol's promote / negative: promote iff OK TO SUBMIT and the HOLDOUT-DTI paired
                    difference against the repository's recorded holdout best has a 95 % CI entirely > 0.
                    The selector (a human, within 3 submissions per week) decides; this never picks one.
"""
from __future__ import annotations


def derive(format_pass: bool, policy: dict, canary_ok: bool, model_ok: bool,
           holdout_vs_best: dict | None) -> dict:
    ok_download = bool(format_pass)
    decisive = bool(policy.get("decisive_passed"))
    ok_submit = bool(ok_download and decisive and canary_ok and model_ok)
    reasons = []
    if not ok_download:
        reasons.append("a format gate failed")
    if not decisive:
        reasons.append(f"decisive uniqueness tier {policy.get('decisive_tier')} failed")
    if not canary_ok:
        reasons.append("leakage canary above 0.90")
    if not model_ok:
        reasons.append("MODEL kill criterion triggered")
    beats = False
    if holdout_vs_best is not None:
        lo, hi = holdout_vs_best["ci95"]
        beats = bool(holdout_vs_best["delta"] > 0 and lo > 0)
    promote = bool(ok_submit and beats)
    return dict(
        ok_to_download=ok_download, ok_to_submit=ok_submit, blocking_reasons=reasons,
        beats_holdout_best=beats, verdict="promote" if promote else "negative",
        slot_recommended=promote,
        literal_registry_rule_passed=bool(policy.get("literal_passed")),
    )
