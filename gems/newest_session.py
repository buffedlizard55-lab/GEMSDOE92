"""Data-driven 'newest session' line for the status panels.

Every number comes from ``evidence/ali_run_card.json`` (written by
``scripts/ali_run_card.py``) and every hash is re-checked against the served
bytes, so a stale or hand-edited panel fails the site check instead of
publishing.  This helper can only *reject*: it refuses to render anything if the
run card claims eligibility or a non-negative verdict.
"""
from __future__ import annotations

import hashlib
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "evidence" / "ali_run_card.json"


def load(root: Path = ROOT) -> dict:
    card = json.loads((root / "evidence" / "ali_run_card.json").read_text(encoding="utf-8"))
    if card.get("verdict") != "negative" or card.get("submission_eligible") is not False:
        raise ValueError("newest-session panel is rejection-only")
    tif = root / card["raster"]["path"]
    if hashlib.sha256(tif.read_bytes()).hexdigest() != card["raster_sha256"]:
        raise ValueError("newest-session raster SHA-256 differs from served bytes")
    if not 0 < len(card.get("note", "")) <= 140:
        raise ValueError("newest-session note must contain 1..140 characters")
    return card


def facts(card: dict) -> dict:
    h = card["holdout_dti"]
    ctrl = card["holdout_controls"]["CTRL_R0recipe_d28_minus_dvis2"]
    d = card["paired_differences"]["CTRL_R0recipe_d28_minus_dvis2"]
    disc = card["correlation_overlap_vs_registry"]["final_dots"]["discriminating_dot_fields"]
    tight = disc["tightest_collision"]
    worst = tight["file"].split(":", 1)
    return dict(
        file=card["raster"]["path"].removeprefix("docs/"),
        name=card["submission_name"], sha=card["raster_sha256"],
        dti=f"{h['dti']:.6f} [{h['ci95'][0]:.6f}, {h['ci95'][1]:.6f}]",
        ctrl=f"{ctrl['dti']:.6f}", delta=f"{d['delta']:+.6f} [{d['ci95'][0]:+.6f}, {d['ci95'][1]:+.6f}]",
        n=h["withheld_positive_pixels"], ev=h["evaluator_version"],
        ovl=f"{tight['forward_overlap']:.3f}", ovl_repo=worst[0],
        ovl_file=worst[1].rsplit("/", 1)[-1] if len(worst) > 1 else worst[0],
        halo=f"{tight['halo_coverage']:.3f}", n_fire=len(disc["firing"]))


def html_line(card: dict, prefix: str = "") -> str:
    """One paragraph; ``prefix`` is the path from the page to docs/."""
    f = {k: escape(str(v), quote=True) for k, v in facts(card).items()}
    return (f'<p><strong>Also 2026-10-25 — ALI lane: a NEW raster was generated and tested — '
            f'DO NOT SUBMIT.</strong> <a href="{prefix}{f["file"]}" download>Download it for research</a> · '
            f'<a href="{prefix}ALI_LANE.md">full report</a> · <a href="{prefix}downloads/ali_run_card.json">run card</a>. '
            f'Reasons: <strong>duplicate under the registry rule</strong> ({f["ovl"]} of its dots lie within 3 px of '
            f'{f["ovl_repo"]} <code>{f["ovl_file"]}</code>, whose halo covers only {f["halo"]} of the domain; '
            f'{f["n_fire"]} discriminating dot fields exceed 0.70), and HOLDOUT-DTI {f["dti"]} only ties the R0-recipe '
            f'control {f["ctrl"]} (paired Δ {f["delta"]}; {f["ev"]}, {f["n"]} withheld positives).</p>')


def md_line(card: dict, prefix: str = "") -> str:
    f = facts(card)
    return (f"**Also 2026-10-25 — ALI lane: a NEW raster was generated and tested — DO NOT SUBMIT.** "
            f"[Download it for research]({prefix}{f['file']}) · [full report]({prefix}ALI_LANE.md) · "
            f"[run card]({prefix}downloads/ali_run_card.json). Reasons: **duplicate under the registry rule** "
            f"({f['ovl']} of its dots lie within 3 px of {f['ovl_repo']} `{f['ovl_file']}`, whose halo covers only "
            f"{f['halo']} of the domain; {f['n_fire']} discriminating dot fields exceed 0.70), and HOLDOUT-DTI "
            f"{f['dti']} only ties the R0-recipe control {f['ctrl']} (paired Δ {f['delta']}; {f['ev']}, "
            f"{f['n']} withheld positives).")
