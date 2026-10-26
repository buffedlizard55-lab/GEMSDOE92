"""DrivenData leaderboard monitoring must stay disabled without authorization."""
from pathlib import Path
import socket
import subprocess
import sys

from scripts import update_leaderboard_feed

ROOT = Path(__file__).resolve().parents[1]
TERMS = "https://www.drivendata.org/termsofuse/"


def test_disabled_entry_point_never_uses_network_or_writes_feed(tmp_path, monkeypatch, capsys):
    def forbidden(*args, **kwargs):
        raise AssertionError("network access must not be attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    output = tmp_path / "feed.json"
    assert update_leaderboard_feed.main(["--output", str(output)]) == 1
    assert not output.exists()
    assert "STOP" in capsys.readouterr().err


def test_disabled_command_fails_closed_without_writing(tmp_path):
    output = tmp_path / "feed.json"
    p = subprocess.run([sys.executable, str(ROOT / "scripts/update_leaderboard_feed.py"),
                        "--output", str(output)], capture_output=True, text=True)
    assert p.returncode != 0
    assert "STOP" in p.stderr and TERMS in p.stderr
    assert not output.exists()


def test_pages_deploy_contains_no_scheduled_organizer_fetch_or_mirror():
    workflow = (ROOT / ".github/workflows/pages.yml").read_text()
    assert "workflow_dispatch:" in workflow and "push:" in workflow
    assert "schedule:" not in workflow
    assert "scripts/update_leaderboard_feed.py" not in workflow
    assert not (ROOT / "docs/downloads/live_leaderboard.json").exists()
    assert not (ROOT / "docs/leaderboard-feed.js").exists()
    for rel in ("index.html", "docs/index.html", "docs/executive-summary.html",
                "docs/SUBMIT.html", "docs/focus9.html"):
        text = (ROOT / rel).read_text()
        assert TERMS in text
        assert "leaderboard-feed.js" not in text
        assert "live_leaderboard.json" not in text
        assert "not mirrored" in text
