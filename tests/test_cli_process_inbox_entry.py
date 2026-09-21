"""`ohtli process-inbox --entry NAME`, through the real `main`, with the vault
directories redirected to `tmp_path`.

Processing deletes the entry it consumes, so the tests check both what is
processed and that nothing else is read, changed or removed.
"""

import hashlib
import json

import pytest

from ohtli.cli import main
from ohtli.vault_io import paths

FOLDERS = {
    "project": "projects",
    "area": "areas",
    "resource": "resources",
    "reference": "references",
    "meeting": "meetings",
    "journal-entry": "journal",
}


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
    (tmp_path / "inbox").mkdir()


def _run(capsys, *argv):
    code = main(list(argv))
    return code, capsys.readouterr().out


def _write(tmp_path, name, text):
    (tmp_path / "inbox" / name).write_text(text, encoding="utf-8")


def _seed(tmp_path):
    _write(tmp_path, "one.md", "One\n\nbody one\n")
    _write(tmp_path, "two.md", "Two\n\nbody two\n")
    _write(tmp_path, "three.md", "Three\n\nbody three\n")
    _write(tmp_path, "README.md", "navigation\n")


def _inbox(tmp_path):
    return sorted(p.name for p in (tmp_path / "inbox").iterdir())


def _snapshot(tmp_path, *names):
    return {n: (tmp_path / "inbox" / n).read_bytes() for n in names}


def _notes(tmp_path, kind="project"):
    folder = tmp_path / FOLDERS[kind]
    return sorted(p.name for p in folder.glob("*.md")) if folder.exists() else []


def _events(tmp_path):
    log = tmp_path / ".ohtli" / "events.jsonl"
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []


def test_only_the_named_entry_is_processed(capsys, tmp_path):
    _seed(tmp_path)
    untouched = _snapshot(tmp_path, "one.md", "three.md", "README.md")

    code, out = _run(capsys, "process-inbox", "--entry", "two")

    assert code == 0 and "Processed Project 'Two'" in out
    assert _notes(tmp_path) == ["two.md"]
    assert _inbox(tmp_path) == ["README.md", "one.md", "three.md"], "the processed entry is resolved"
    assert _snapshot(tmp_path, "one.md", "three.md", "README.md") == untouched
    assert [e["event_type"] for e in _events(tmp_path)] == ["Project Created"]


def test_the_name_may_carry_the_md_extension(capsys, tmp_path):
    _seed(tmp_path)

    code, _ = _run(capsys, "process-inbox", "--entry", "two.md")

    assert code == 0 and _notes(tmp_path) == ["two.md"]


@pytest.mark.parametrize("kind", list(FOLDERS))
def test_as_applies_to_the_named_entry_for_every_domain_object(capsys, tmp_path, kind):
    _seed(tmp_path)
    untouched = _snapshot(tmp_path, "one.md", "three.md")

    code, out = _run(capsys, "process-inbox", "--entry", "two", "--as", kind)

    assert code == 0
    assert _notes(tmp_path, kind) == ["two.md"], f"created in the {kind} folder"
    assert _snapshot(tmp_path, "one.md", "three.md") == untouched
    assert len(_events(tmp_path)) == 1


def test_the_option_is_repeatable_and_keeps_the_order_given(capsys, tmp_path):
    _seed(tmp_path)

    code, out = _run(capsys, "process-inbox", "--entry", "three", "--entry", "one")

    assert code == 0
    assert out.index("'Three'") < out.index("'One'")
    assert _notes(tmp_path) == ["one.md", "three.md"]
    assert _inbox(tmp_path) == ["README.md", "two.md"]


def test_the_same_entry_named_twice_is_processed_once(capsys, tmp_path):
    _seed(tmp_path)

    code, out = _run(capsys, "process-inbox", "--entry", "one", "--entry", "one.md", "--as", "area")

    assert code == 0
    assert out.count("Processed") == 1
    assert len(_events(tmp_path)) == 1


def test_an_unknown_name_processes_nothing_and_exits_1(capsys, tmp_path):
    _seed(tmp_path)
    before = _snapshot(tmp_path, "one.md", "two.md", "three.md", "README.md")

    code, out = _run(capsys, "process-inbox", "--entry", "one", "--entry", "nope", "--entry", "two")

    assert code == 1
    assert "no Inbox entry named 'nope'" in out and "Nothing was processed" in out
    assert _snapshot(tmp_path, "one.md", "two.md", "three.md", "README.md") == before
    assert _notes(tmp_path) == [] and _events(tmp_path) == [], "the valid names were not processed either"


def test_every_unknown_name_is_reported(capsys, tmp_path):
    _seed(tmp_path)

    _, out = _run(capsys, "process-inbox", "--entry", "ghost", "--entry", "phantom")

    assert "'ghost'" in out and "'phantom'" in out


@pytest.mark.parametrize(
    "name",
    ["../projects/victim.md", "../projects/victim", "sub/x.md", "./one.md", "..", ".", "", "  "],
)
def test_a_name_that_is_not_an_inbox_file_name_cannot_reach_anything(capsys, tmp_path, name):
    _seed(tmp_path)
    victim = tmp_path / "projects" / "victim.md"
    victim.parent.mkdir()
    victim.write_text("---\nid: x\n---\n\n# Victim\n", encoding="utf-8")
    fingerprint = hashlib.sha256(victim.read_bytes()).hexdigest()
    before = _snapshot(tmp_path, "one.md", "two.md", "three.md", "README.md")

    code, out = _run(capsys, "process-inbox", "--entry", name)

    assert code == 1 and "Nothing was processed" in out
    assert victim.exists() and hashlib.sha256(victim.read_bytes()).hexdigest() == fingerprint
    assert _snapshot(tmp_path, "one.md", "two.md", "three.md", "README.md") == before
    assert _events(tmp_path) == []


def test_an_absolute_path_cannot_reach_a_file_outside_the_inbox(capsys, tmp_path):
    _seed(tmp_path)
    victim = tmp_path / "outside.md"
    victim.write_text("OUTSIDE\n", encoding="utf-8")

    code, out = _run(capsys, "process-inbox", "--entry", str(victim))

    assert code == 1 and victim.read_text(encoding="utf-8") == "OUTSIDE\n"
    assert _notes(tmp_path) == []


@pytest.mark.parametrize("name", ["README", "README.md", "index", "index.md"])
def test_a_reserved_navigation_file_cannot_be_processed(capsys, tmp_path, name):
    _seed(tmp_path)
    _write(tmp_path, "index.md", "navigation\n")

    code, _ = _run(capsys, "process-inbox", "--entry", name)

    assert code == 1
    assert (tmp_path / "inbox" / "README.md").exists() and (tmp_path / "inbox" / "index.md").exists()
    assert _notes(tmp_path) == []


def test_a_named_entry_that_processing_refuses_stays_and_the_others_are_processed(capsys, tmp_path):
    _seed(tmp_path)
    _write(tmp_path, "blank.md", "\n   \n")
    blank = _snapshot(tmp_path, "blank.md")

    code, out = _run(capsys, "process-inbox", "--entry", "blank", "--entry", "one")

    assert code == 1, "an entry asked for by name that could not be processed is a failure"
    assert "'blank.md' left untouched in Inbox" in out and "Processed Project 'One'" in out
    assert _snapshot(tmp_path, "blank.md") == blank
    assert _notes(tmp_path) == ["one.md"]


def test_a_duplicate_title_is_refused_and_the_entry_stays(capsys, tmp_path):
    _seed(tmp_path)
    _run(capsys, "process-inbox", "--entry", "one")
    _write(tmp_path, "one-again.md", "One\n\nagain\n")

    code, out = _run(capsys, "process-inbox", "--entry", "one-again")

    assert code == 1 and "'one-again.md' left untouched in Inbox" in out
    assert (tmp_path / "inbox" / "one-again.md").exists()
    assert len(_events(tmp_path)) == 1


def test_the_same_title_can_still_become_a_different_domain_object(capsys, tmp_path):
    """Applicability is per Domain Object, as with Capture."""
    _seed(tmp_path)
    _run(capsys, "process-inbox", "--entry", "one")
    _write(tmp_path, "one-again.md", "One\n\nagain\n")

    code, _ = _run(capsys, "process-inbox", "--entry", "one-again", "--as", "resource")

    assert code == 0 and _notes(tmp_path, "resource") == ["one.md"]


def test_naming_an_entry_in_an_empty_inbox_is_an_error(capsys, tmp_path):
    code, out = _run(capsys, "process-inbox", "--entry", "one")

    assert code == 1 and "no Inbox entry named 'one'" in out


# ---- without --entry the batch is exactly as before ------------------------------------


def test_without_entry_every_entry_is_processed(capsys, tmp_path):
    _seed(tmp_path)

    code, out = _run(capsys, "process-inbox")

    assert code == 0 and out.count("Processed Project") == 3
    assert _notes(tmp_path) == ["one.md", "three.md", "two.md"]
    assert _inbox(tmp_path) == ["README.md"]


def test_the_batch_still_exits_0_when_it_refuses_entries(capsys, tmp_path):
    _seed(tmp_path)
    _write(tmp_path, "blank.md", "\n  \n")

    code, out = _run(capsys, "process-inbox")

    assert code == 0, "batch mode keeps its exit code"
    assert "'blank.md' left untouched in Inbox" in out
    assert (tmp_path / "inbox" / "blank.md").exists()


def test_the_batch_with_an_empty_inbox_says_so(capsys, tmp_path):
    code, out = _run(capsys, "process-inbox")

    assert code == 0 and out.strip() == "Inbox is empty."


def test_the_batch_still_honours_as(capsys, tmp_path):
    _seed(tmp_path)

    code, _ = _run(capsys, "process-inbox", "--as", "area")

    assert code == 0 and _notes(tmp_path, "area") == ["one.md", "three.md", "two.md"]


def test_the_help_explains_that_the_name_is_a_file_name_not_a_path(capsys):
    with pytest.raises(SystemExit):
        main(["process-inbox", "--help"])
    out = capsys.readouterr().out

    assert "--entry NAME" in out and "never a" in out and "path" in out
