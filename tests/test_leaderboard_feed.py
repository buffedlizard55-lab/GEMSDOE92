"""Official leaderboard parsing and unavailable states never affect eligibility."""
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from scripts.update_leaderboard_feed import URL, make_feed, parse_public_leader

ROOT = Path(__file__).resolve().parents[1]


def page(score="0.4437", rank="#1"):
    return f'''<html><body><table><thead><tr>
      <th>Rank</th><th>Team members</th><th>Participant</th>
      <th>Best<br>public<br>DW-Tversky<br>(in descending order)</th><th>Shared work</th>
      </tr></thead><tbody><tr><td>{rank}</td><td><img src="x"></td>
      <td><a href="/users/someone/">someone</a><br>18h ago · 31 submissions</td>
      <td>{score}</td><td></td></tr><tr><td>#2</td><td></td><td>other</td><td>0.3916</td><td></td></tr>
      </tbody></table></body></html>'''


def test_extracts_only_rank_one_score_from_header_bound_table():
    assert parse_public_leader(page()) == 0.4437
    unrelated = "<table><tr><th>Rank</th><th>Other</th></tr><tr><td>#1</td><td>0.99</td></tr></table>"
    assert parse_public_leader(unrelated + page()) == 0.4437
    assert parse_public_leader(page(score="1.0000", rank="1")) == 1.0


@pytest.mark.parametrize("body", [
    "<html><form>Log in</form></html>",
    page(score="1.2"),
    page(score="NaN"),
    page(score="0.4 and 0.5"),
    page(rank="#2"),
    page() + page(score="0.5"),
    page().replace("DW-Tversky", "different metric"),
])
def test_changed_or_ambiguous_markup_is_never_guessed(body):
    with pytest.raises(ValueError):
        parse_public_leader(body)


def test_feed_records_source_timestamp_and_no_submission_receipt():
    now = datetime(2026, 10, 26, 21, 0, tzinfo=timezone.utc)
    feed = make_feed(lambda: page(), now=now)
    assert feed["status"] == "ok"
    assert feed["source"] == URL
    assert feed["checked_at_utc"] == "2026-10-26T21:00:00+00:00"
    assert feed["rank"] == 1 and feed["public_dw_tversky"] == 0.4437
    assert "not a project submission receipt" in feed["provenance"]
    assert "submission_eligible" not in feed


def test_feed_failure_is_explicit_and_contains_no_stale_score():
    def broken():
        raise OSError("upstream failed")

    feed = make_feed(broken)
    assert feed["status"] == "unavailable"
    assert feed["rank"] is None and feed["public_dw_tversky"] is None
    assert "upstream failed" not in feed["reason"]  # no raw network error text
    assert feed["failure_code"] == "fetch_error"
    login = make_feed(lambda: "<html>login</html>")
    assert login["status"] == "unavailable"
    assert login["failure_code"] == "table_missing_or_ambiguous"
    assert make_feed(lambda: page(score="NaN"))["failure_code"] == "rank_one_score_invalid"

    def sensitive_value_error():
        raise ValueError("private upstream details")
    safe = make_feed(sensitive_value_error)
    assert safe["failure_code"] == "invalid_response"
    assert "private upstream details" not in json.dumps(safe)


def test_committed_dated_snapshot_and_scheduled_deploy_are_honest():
    feed = json.loads((ROOT / "docs/downloads/live_leaderboard.json").read_text())
    assert feed["status"] == "snapshot" and feed["source"] == URL
    assert feed["observed_on_utc"] == "2026-10-26"
    assert feed["checked_at_utc"] is None
    assert feed["public_dw_tversky"] == 0.4437
    workflow = (ROOT / ".github/workflows/pages.yml").read_text()
    assert "schedule:" in workflow and "workflow_dispatch:" in workflow
    assert "scripts/update_leaderboard_feed.py" in workflow
    assert ".cache/pages/docs/downloads/live_leaderboard.json" in workflow
    js = (ROOT / "docs/leaderboard-feed.js").read_text()
    assert "textContent" in js and "innerHTML" not in js
