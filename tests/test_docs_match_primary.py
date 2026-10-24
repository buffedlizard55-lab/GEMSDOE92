"""The README, SLOT_PLAN and NEXT_STEPS must describe the primary that the site actually serves (hash, name, note)."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _primary():
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    m = re.search(r'href="downloads/([^"]+-zeros\.tif)"', html)
    assert m
    f = ROOT / "docs" / "downloads" / m.group(1)
    card = json.loads((ROOT / "evidence" / "lcs_run_card.json").read_text())
    return f, card


def test_readme_names_the_served_primary_hash_name_and_note():
    f, card = _primary()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    assert f.name in readme and sha in readme
    assert card["name"] in readme and card["note"] in readme


def test_slot_plan_and_next_steps_lead_with_the_served_primary():
    f, card = _primary()
    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    slot = (ROOT / "SLOT_PLAN.md").read_text(encoding="utf-8")[:3000]
    nxt = (ROOT / "docs" / "NEXT_STEPS.md").read_text(encoding="utf-8")[:6000]
    assert sha in slot and f.name.split("-zeros")[0].replace("GEMSDOE92-lcs-consensus-37654-20261024-", "") in slot
    assert f.name in nxt


def test_standing_brief_and_core_values_are_in_the_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for needle in ("Standing brief", "Maximize P(Win)", "Own the Outcome", "Original Session Prompt",
                   "Predicted values must be in range [0, 1]", "lane paragraph"):
        assert needle in readme, needle


def test_every_irregularity_referenced_by_the_docs_exists():
    irr = (ROOT / "IRREGULARITIES.md").read_text(encoding="utf-8")
    refs = set()
    for p in ("README.md", "docs/NEXT_STEPS.md", "docs/UNIQUENESS_POLICY_20261024.md", "docs/ANALYSIS_20261024_LCS.md",
              "docs/WHY_R0_0_2778.md", "docs/HYPOTHESES_20261024_LCS.md", "SESSION_PROMPT.md", "AI_USE.md"):
        refs |= set(re.findall(r"IR-92-\d\d", (ROOT / p).read_text(encoding="utf-8")))
    assert refs, "no IR-92 references found"
    for r in refs:
        assert f"## {r} " in irr, f"{r} is referenced but not defined in IRREGULARITIES.md"


def test_claimed_scores_ledger_is_labelled_claim_and_has_no_receipts():
    import csv
    rows = list(csv.DictReader(open(ROOT / "ledger" / "claimed_scores_20261024.csv", encoding="utf-8")))
    assert rows and all(r["evidence_label"] == "CLAIM" for r in rows)
    assert any(r["match_confidence"] == "exact" and r["claimed_score"] == "0.2778" for r in rows)
    assert {r["site"] for r in rows if r["match_confidence"] == "unmatched"} == {"GEMSDOE46", "GEMSDOE62"}
