"""The `contains` command and the derived-relationship message, through the
real `main`, with the vault directories redirected to `tmp_path`."""

import pytest

from ohtli.cli import main
from ohtli.vault_io import paths


@pytest.fixture(autouse=True)
def _isolated_vault(tmp_path, monkeypatch):
    for name, sub in (
        ("PROJECTS_DIR", "projects"),
        ("AREAS_DIR", "areas"),
        ("RESOURCES_DIR", "resources"),
        ("REFERENCES_DIR", "references"),
        ("MEETINGS_DIR", "meetings"),
        ("JOURNAL_ENTRIES_DIR", "journal"),
        ("INBOX_DIR", "inbox"),
        ("EVENTS_DIR", ".ohtli"),
    ):
        monkeypatch.setattr(paths, name, tmp_path / sub)


def _run(capsys, *argv):
    code = main(list(argv))
    return code, capsys.readouterr().out


def _seed(capsys):
    for kind, title in (("area", "Health"), ("area", "Finance"), ("project", "Alpha"), ("project", "Zeta")):
        assert _run(capsys, f"create-{kind}", title)[0] == 0
    for project in ("Alpha", "Zeta"):
        code, _ = _run(capsys, "link", "--from-type", "project", "--from", project, "--to-type", "area", "--to", "Health")
        assert code == 0


def test_contains_lists_the_projects_of_an_area(capsys):
    _seed(capsys)

    code, out = _run(capsys, "contains", "Health")

    assert code == 0
    assert "Area 'Health' contains 2 Project(s):" in out
    assert out.index("Alpha") < out.index("Zeta")


def test_contains_marks_an_archived_project_as_historical(capsys):
    _seed(capsys)
    _run(capsys, "archive-project", "Zeta")

    _, out = _run(capsys, "contains", "Health")

    assert "Zeta [historical]" in out
    assert "Alpha [historical]" not in out


def test_contains_for_an_area_without_projects_succeeds_with_a_clear_message(capsys):
    _seed(capsys)

    code, out = _run(capsys, "contains", "Finance")

    assert code == 0 and out.strip() == "Area 'Finance' contains no Projects."


def test_contains_for_an_unknown_area_is_refused(capsys):
    code, out = _run(capsys, "contains", "Nope")

    assert code == 1 and "no Area titled 'Nope'" in out


def test_contains_does_not_write_events_or_notes(capsys, tmp_path):
    _seed(capsys)
    events = (tmp_path / ".ohtli" / "events.jsonl").read_bytes()
    notes = {p.name: p.read_bytes() for p in (tmp_path / "projects").glob("*.md")}

    _run(capsys, "contains", "Health")
    _run(capsys, "contains", "Nope")

    assert (tmp_path / ".ohtli" / "events.jsonl").read_bytes() == events
    assert {p.name: p.read_bytes() for p in (tmp_path / "projects").glob("*.md")} == notes


def test_linking_from_the_area_side_is_refused_and_points_to_the_project_side(capsys):
    _seed(capsys)

    code, out = _run(capsys, "link", "--from-type", "area", "--from", "Health", "--to-type", "project", "--to", "Alpha")

    assert code == 1
    assert "derived from 'Project belongs to Area'" in out
    assert "--from-type project" in out and "--to-type area" in out
    assert "ohtli contains" in out


def test_unlinking_from_the_area_side_is_refused_the_same_way(capsys):
    _seed(capsys)

    code, out = _run(capsys, "unlink", "--from-type", "area", "--from", "Health", "--to-type", "project", "--to", "Alpha")

    assert code == 1 and "derived from 'Project belongs to Area'" in out and "ohtli unlink" in out


def test_a_refused_derived_link_changes_nothing(capsys, tmp_path):
    _seed(capsys)
    _run(capsys, "create-project", "Loose")
    events = (tmp_path / ".ohtli" / "events.jsonl").read_bytes()

    _run(capsys, "link", "--from-type", "area", "--from", "Health", "--to-type", "project", "--to", "Loose")

    assert (tmp_path / ".ohtli" / "events.jsonl").read_bytes() == events
    _, out = _run(capsys, "contains", "Health")
    assert "Loose" not in out


def test_the_derived_message_does_not_leak_to_other_undefined_pairs(capsys):
    _run(capsys, "create-meeting", "Sync")
    _run(capsys, "create-area", "Health")

    code, out = _run(capsys, "link", "--from-type", "meeting", "--from", "Sync", "--to-type", "area", "--to", "Health")

    assert code == 1 and "No canonical relationship is implemented" in out and "derived" not in out


def test_project_contains_meeting_links_through_the_generic_command(capsys):
    _run(capsys, "create-project", "Alpha")
    _run(capsys, "create-meeting", "Sync")

    code, out = _run(capsys, "link", "--from-type", "project", "--from", "Alpha", "--to-type", "meeting", "--to", "Sync")

    assert code == 0 and "Project Linked to Meeting" in out and "'Alpha' contains 'Sync'" in out
