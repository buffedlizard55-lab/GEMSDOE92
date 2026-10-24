"""Verdict logic for the three uniqueness tiers (pure functions, no I/O beyond the policy file).

Input is the JSON written by scripts/registry_gate.py for the pre-placement surface and for
the final dots.  A tier passes a phase iff, over that tier's rasters, no raster has forward
3 px overlap > 0.70 and none has |Spearman| > 0.90 (thresholds read from the policy file,
never hard-coded here).  The decisive tier comes from registry/uniqueness_policy.json; the
other tiers are always reported next to it.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "registry" / "uniqueness_policy.json"
TIER_KEYS = {"S": "tier_S", "L": "tier_L", "T": "tier_T_all"}


def load_policy(path: Path | str = POLICY) -> dict:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if doc.get("decisive_tier") not in TIER_KEYS:
        raise ValueError("decisive_tier must be one of S, L, T")
    if doc.get("thresholds_unchanged") is not True:
        raise ValueError("policy must declare thresholds_unchanged: true")
    return doc


def tier_pass(gate_doc: dict, tier: str, thresholds: dict) -> dict:
    t = gate_doc[TIER_KEYS[tier]]
    if not t.get("n_distinct"):
        return dict(tier=tier, passed=False, reason="no rasters in tier", n_distinct=0)
    over = t["max_forward_overlap"] > thresholds["forward_overlap"]
    rho = (t.get("max_abs_spearman") or 0.0) > thresholds["abs_spearman"]
    return dict(tier=tier, passed=not (over or rho), n_distinct=t["n_distinct"], n_files=t.get("n_files"),
                max_forward_overlap=t["max_forward_overlap"], n_over_overlap=t["n_distinct_over_0_70"],
                max_abs_spearman=t.get("max_abs_spearman"), n_over_rho=t["n_distinct_over_rho_0_90"],
                worst=(t.get("worst") or [])[:3])


def decide(surface_doc: dict, final_doc: dict, policy: dict | None = None) -> dict:
    policy = policy or load_policy()
    thr = policy["thresholds"]
    out = {"decisive_tier": policy["decisive_tier"], "tiers": {}}
    for tier in "SLT":
        s, f = tier_pass(surface_doc, tier, thr), tier_pass(final_doc, tier, thr)
        out["tiers"][tier] = dict(surface=s, final=f, passed=bool(s["passed"] and f["passed"]))
    out["decisive_passed"] = out["tiers"][policy["decisive_tier"]]["passed"]
    out["literal_passed"] = out["tiers"]["T"]["passed"]
    return out
