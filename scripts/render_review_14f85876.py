#!/usr/bin/env python3
"""Publish the independently measured, rejection-only review without promotion."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "evidence/preflight_14f85876.json"
OUTPUT = ROOT / "docs/downloads/review_14f85876_run_card.json"


def build() -> dict:
    raw = INPUT.read_bytes()
    card = json.loads(raw)
    proof = card["correlation_overlap_vs_registry"]["preplacement_proof"]
    if (card["verdict"] != "negative" or card["submission_eligible"] is not False
            or card["new_unique_tiff_generated"] is not False or card["experiments"] != 0
            or card["weekly_slots_used"] != 0
            or proof["universal_nonempty_in_footprint_overlap_stop"] is not True
            or proof["positive_in_footprint"] != proof["footprint_pixels"]
            or proof["forward_overlap_for_any_nonempty_in_footprint_dot_set"] != 1.0):
        raise ValueError("review input is not the verified rejection-only proof")
    primary = ROOT / card["primary_download"]
    if hashlib.sha256(primary.read_bytes()).hexdigest() != card["raster_sha256"]:
        raise ValueError("research primary hash differs from the review card")
    if not 0 < len(card["note"]) <= 140 or not 0 < len(card["submission_name"]) <= 140:
        raise ValueError("historical name/note must each be at most 140 characters")
    if not card["validator_output"] or any(g.get("ok") is not True for g in card["validator_output"]):
        raise ValueError("research primary format evidence is incomplete")
    card["schema"] = "gemsdoe92-review-14f85876-v1"
    card["source_preflight_sha256"] = hashlib.sha256(raw).hexdigest()
    card["estimated_leaderboard_score"] = None
    card["score_estimate_reason"] = (
        "No verified score-to-file receipt or validated group-independent model; "
        "static forensic re-scores are not prospective, fold-rebuilt experiments."
    )
    card["historical_salemseismo_correction"] = {
        "artifact": "docs/downloads/h33-h33-2-b2-SALEMSEISMOcelftail52k-20261026-cc3c8ff2-zeros.tif",
        "sha256": "b06dd72feff35b1631a17a52581b46d9b21b92fcba09441eac77d6daa9ba1dda",
        "source_run_card": "docs/downloads/salemseismo_run_card.json",
        "status": "historical research only; DO NOT SUBMIT",
        "limitations": [
            "The historical runner performed placement and wrote files before scanning the public registry.",
            "Its reported public rank correlations covered selected overlap witnesses, not every registry raster.",
            "Matched-budget/sparse overlap measurements cannot override the literal dense-witness stop.",
            "The former flattened-offset halo could wrap across row boundaries; prior scan values require rechecking.",
            "Static catalogue-derived masks and already-built predictions are not a prospective fold-local experiment.",
        ],
        "runner_disabled": True,
    }
    card["model_audit"] = "docs/downloads/score_estimator_audit_14f85876.json"
    card["focus_site_evidence"] = "docs/downloads/focus_sites_release_review_20261026.json"
    pair_path = ROOT / "docs/downloads/focus9_pairwise_recheck_14f85876.json"
    pair_bytes = pair_path.read_bytes()
    pair = json.loads(pair_bytes)
    old_focus = ROOT / card["focus_site_evidence"]
    if (pair["source_sha256"] != hashlib.sha256(old_focus.read_bytes()).hexdigest()
            or pair["sample_sha256"] != proof["sample_sha256"] or pair["pairs"] != 36
            or pair["source_blob_and_sha256_verified"] is not True
            or pair["all_pairs_duplicate_in_at_least_one_direction_or_rho"] is not True
            or pair["submission_eligible"] is not False):
        raise ValueError("independent nine-site pairwise recheck is invalid")
    card["focus_pairwise_correction"] = {
        "path": "docs/downloads/focus9_pairwise_recheck_14f85876.json",
        "sha256": hashlib.sha256(pair_bytes).hexdigest(),
        "pairs_with_changed_metrics": pair["pairs_with_changed_metrics"],
        "pairs_rechecked": pair["pairs"],
        "conclusion": "The corrected 2-D Euclidean overlaps supersede earlier numeric pairwise overlaps; all 36 pairwise duplicate decisions remain unchanged. The cause of the earlier numerical discrepancy was not established.",
    }
    card["official_source_findings"] = [
        {
            "url": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
            "finding": "Single-band float32 on the specified grid, values in [0,1], null or NaN outside study-area bounds; local zero-outside-footprint checks do not prove portal acceptance.",
        },
        {
            "url": "https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2",
            "finding": "DrivenData staff state known USGS/INGENIOUS fault pixels are excluded from initial and final evaluation; this does not establish the treatment of an arbitrary surrounding collar.",
        },
        {
            "url": "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/",
            "finding": "The public leaderboard is not mirrored or automatically monitored; a leaderboard row is not a score-to-file submission receipt.",
        },
        {
            "url": "https://www.drivendata.org/termsofuse/",
            "finding": "DrivenData terms prohibit automatic access to the website, including for monitoring or copying; the previously added scheduled feed was removed.",
        },
        {
            "url": "https://docs.nlr.gov/docs/fy26osti/96647.pdf",
            "finding": "Rules include three weekly submissions, one final selection, reproducibility and generative-AI-use disclosure.",
        },
    ]
    return card


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        text = json.dumps(build(), indent=2, allow_nan=False) + "\n"
        if args.check:
            if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != text:
                print("stale public review run card", file=sys.stderr)
                return 1
            print("review run card: OK")
        else:
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT.write_text(text, encoding="utf-8")
            print(f"wrote {OUTPUT}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"review card failed closed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
