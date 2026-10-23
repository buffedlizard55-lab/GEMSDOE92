"""Submission ledger: the single source of truth for what has been built and scored.

Columns (brief section 7, extended with receipt fields the human fills):
    id, parent, axis, value, n_dots, pct_changed, sha256, status,
    predicted_change, receipt_score, receipt_date, notes

Status vocabulary:
    BUILT     raster written and gates passed here
    SUBMITTED human uploaded it from their own account
    SCORED    receipt_score filled from the submission-page receipt
    VOID      superseded / never submitted

Evidence labels (brief section 8) live in the score text: a bare number is a
RECEIPT only when receipt_date is present; otherwise it is a CLAIM.
"""

from __future__ import annotations

import csv
from pathlib import Path

LEDGER = Path("ledger/submissions.csv")
COLUMNS = ["id", "parent", "axis", "value", "n_dots", "pct_changed", "sha256",
           "status", "predicted_change", "receipt_score", "receipt_date", "notes"]


def load(path: str | Path = LEDGER) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh))


def save(rows: list[dict], path: str | Path = LEDGER) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in COLUMNS})


def hash_seen(sha: str, rows: list[dict] | None = None) -> bool:
    rows = load() if rows is None else rows
    return any((r.get("sha256") or "").strip() == sha.strip() for r in rows)


def pair_seen(parent: str, axis: str, value: str, rows: list[dict] | None = None) -> bool:
    """Dedupe on repeated (parent, axis, value) -- the brief's second dedupe rule."""
    rows = load() if rows is None else rows
    return any((r.get("parent"), r.get("axis"), r.get("value")) == (parent, axis, value)
               for r in rows)


def append_variant(row: dict, path: str | Path = LEDGER) -> None:
    """Append one BUILT row, refusing exact-hash and repeated-cell duplicates."""
    rows = load(path)
    sha = (row.get("sha256") or "").strip()
    if not sha:
        raise ValueError("row has no sha256; hash the file on disk first")
    if hash_seen(sha, rows):
        raise ValueError(f"sha256 {sha[:12]}... is already in the ledger")
    if pair_seen(row["parent"], row["axis"], row["value"], rows):
        raise ValueError(f"({row['parent']}, {row['axis']}, {row['value']}) already built")
    rows.append(row)
    save(rows, path)


def import_raw_paste(raw_path: str | Path, out_path: str | Path = LEDGER) -> int:
    """Build the ledger from ledger/raw_paste.txt, collapsing exact repeats.

    Expected columns: site, name, score, encoding, n_dots, sha8, parent, receipt
    """
    p = Path(raw_path)
    if not p.exists():
        return 0
    with open(p, newline="") as fh:
        reader = csv.DictReader(fh)
        seen, rows = set(), []
        for r in reader:
            key = (r.get("sha8") or "").strip()
            if key and key in seen:
                continue  # collapse exact repeats
            seen.add(key)
            rows.append({
                "id": (r.get("name") or "").strip(),
                "parent": (r.get("parent") or "").strip(),
                "axis": "", "value": "",
                "n_dots": (r.get("n_dots") or "").strip(),
                "pct_changed": "",
                "sha256": key,
                "status": "SCORED" if (r.get("score") or "").strip() else "BUILT",
                "predicted_change": "",
                "receipt_score": (r.get("score") or "").strip(),
                "receipt_date": "",
                "notes": f"site={r.get('site','').strip()} encoding={r.get('encoding','').strip()}",
            })
    save(rows, out_path)
    return len(rows)


def best_receipt(rows: list[dict]) -> tuple[str, float | None]:
    """Highest score that is backed by a date (i.e. a RECEIPT, not a CLAIM)."""
    best, best_id = None, ""
    for r in rows:
        sc = (r.get("receipt_score") or "").strip()
        date = (r.get("receipt_date") or "").strip()
        if not sc or not date:
            continue
        try:
            val = float(sc)
        except ValueError:
            continue
        if best is None or val > best:
            best, best_id = val, r.get("id", "")
    return best_id, best


def evidence(row: dict) -> str:
    """Classify a row's score per brief section 8 -- never call a claim a score."""
    sc = (row.get("receipt_score") or "").strip()
    if not sc:
        return "UNSCORED"
    return "RECEIPT" if (row.get("receipt_date") or "").strip() else "CLAIM"


def week_slots(rows: list[dict], week_start: str, per_week: int = 3) -> dict:
    """Count scored submissions in the rolling week (exact repeats still cost a slot)."""
    used = sum(1 for r in rows
               if (r.get("receipt_date") or "").strip() >= week_start
               and (r.get("receipt_score") or "").strip())
    return {"week_start": week_start, "used": used, "left": max(0, per_week - used),
            "per_week": per_week}
