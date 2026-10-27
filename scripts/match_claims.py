#!/usr/bin/env python3
"""Match owner-reported CLAIM scores (ledger/claims_20261027.txt) to registry rasters.

A claim matches a raster when the claim's submission name equals the file stem
or is contained in it (case-insensitive), preferring files in the claim's own
site repository.  Ambiguous matches (different bytes) are reported, never
silently resolved; files with identical in-footprint support are merged.
Output: evidence/claims_matched_20261027.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gems import registry_cache as rc  # noqa: E402

CLAIMS = ROOT / "ledger" / "claims_20261027.txt"
OUT = ROOT / "evidence" / "claims_matched_20261027.json"


def load_claims():
    rows = []
    for line in CLAIMS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        site, url, name, score = line.split("|")
        rows.append(dict(site=site, site_url=url, name=name, claim=float(score),
                         evidence_class="CLAIM (owner-reported 2026-10-27 prompt; no organizer receipt)"))
    return rows


def main() -> int:
    inv = json.loads((rc.CACHE / "inventory.json").read_text(encoding="utf-8"))
    files = [f for r in inv["repositories"] for f in r["files"]]
    claims = load_claims()
    out = []
    for c in claims:
        key = c["name"].lower()
        hits = []
        for f in files:
            stem = Path(f["path"]).name.lower()
            for ext in (".tiff", ".tif"):
                if stem.endswith(ext):
                    stem = stem[: -len(ext)]
            if stem == key or key in stem:
                exact = stem == key or stem.endswith(key) or stem.startswith(key)
                same_repo = f["repo"].upper() == c["site"].upper()
                hits.append((0 if same_repo else 1, 0 if stem == key else (1 if exact else 2),
                             0 if "docs/downloads/" in f["path"] else 1, f))
        hits.sort(key=lambda t: t[:3])
        shas = []
        for h in hits:
            if h[3]["sha256"] not in shas:
                shas.append(h[3]["sha256"])
        rec = dict(c, n_hits=len(hits), n_distinct_sha=len(shas))
        if hits:
            best = hits[0][3]
            rec.update(match=dict(repo=best["repo"], owner=best["owner"], path=best["path"],
                                  sha256=best["sha256"], bytes=best["bytes"]))
            rec["alternatives"] = [dict(repo=h[3]["repo"], path=h[3]["path"], sha256=h[3]["sha256"])
                                   for h in hits[1:6] if h[3]["sha256"] != best["sha256"]]
        out.append(rec)
    matched = sum(1 for r in out if "match" in r)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(dict(schema="gemsdoe92-claims-matched-v1", claims=len(out), matched=matched,
                                   rows=out), indent=1), encoding="utf-8")
    print(f"{matched}/{len(out)} claims matched -> {OUT}")
    for r in out:
        if "match" not in r:
            print("UNMATCHED", r["site"], r["name"], r["claim"])
        elif r["n_distinct_sha"] > 1:
            print("AMBIGUOUS", r["site"], r["name"], r["n_distinct_sha"], "->", r["match"]["repo"], r["match"]["path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
