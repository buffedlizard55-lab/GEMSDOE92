"""Published pages must not silently ship unresolved merge conflicts."""
from scripts.check_site import check_conflict_markers


def test_rejects_markers_and_diff3_ancestor():
    for marker in ("<<<<<<< HEAD", "=======", ">>>>>>> origin/main", "||||||| base"):
        problems = []
        check_conflict_markers("guide", "text\n" + marker + "\nmore", problems)
        assert problems == ["guide contains unresolved merge conflict markers"]


def test_does_not_flag_normal_prose():
    problems = []
    check_conflict_markers("guide", "No conflict; x = 1.\n", problems)
    assert not problems
