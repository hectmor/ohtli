"""What the CLI tells the user when `archive-*`/`reactivate-*` cannot find
the note to transition, or finds more than one that could be it.

The prefix `Not applicable: '<title>' cannot be {archive,reactivate}d.` is
unchanged (no existing test pinned it, but nothing should need to).
`ambiguous_title` and `not_an_ohtli_note` add a sentence after it, the same
shape as Processing Update's `_inbox_reason` (#156) and Knowledge's
`_enrich_reason` (#160), each with its own wording.
"""

import pytest

from ohtli.cli import main
from ohtli.vault_io import paths

KINDS = [
    ("archive-project", "projects", "Project", "create-project"),
    ("archive-area", "areas", "Area", "create-area"),
    ("archive-resource", "resources", "Resource", "create-resource"),
    ("archive-reference", "references", "Reference", "create-reference"),
    ("archive-meeting", "meetings", "Meeting", "create-meeting"),
    ("archive-journal-entry", "journal", "Journal Entry", "create-journal-entry"),
    ("reactivate-project", "projects", "Project", "create-project"),
    ("reactivate-area", "areas", "Area", "create-area"),
    ("reactivate-resource", "resources", "Resource", "create-resource"),
    ("reactivate-reference", "references", "Reference", "create-reference"),
    ("reactivate-meeting", "meetings", "Meeting", "create-meeting"),
    ("reactivate-journal-entry", "journal", "Journal Entry", "create-journal-entry"),
]
BY_KIND = pytest.mark.parametrize(("command", "folder", "label", "create"), KINDS, ids=[k[0] for k in KINDS])


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
        ("AREA_DASHBOARDS_DIR", "dashboards/areas"),
    ):
        monkeypatch.setattr(paths, name, tmp_path / sub)


def _run(capsys, *argv):
    code = main(list(argv))
    return code, capsys.readouterr().out


def _op(command):
    return command.split("-", 1)[0]


@BY_KIND
def test_an_ordinary_refusal_keeps_its_original_message(capsys, tmp_path, command, folder, label, create):
    """No note exists at all: the pre-existing message, unaffected by this
    change."""
    code, out = _run(capsys, command, "Subject")

    assert code == 1
    assert out == f"Not applicable: 'Subject' cannot be {_op(command)}d.\n"


@BY_KIND
def test_a_hand_made_file_is_refused_and_named_not_half_written(capsys, tmp_path, command, folder, label, create):
    path = tmp_path / folder / "subject.md"
    path.parent.mkdir(parents=True)
    expected_context = "operational" if _op(command) == "archive" else "historical"
    before = f"---\ncontext: {expected_context}\n---\n\n# Subject\n\nmine\n".encode()
    path.write_bytes(before)

    code, out = _run(capsys, command, "Subject")

    assert code == 1
    assert out == (
        f"Not applicable: 'Subject' cannot be {_op(command)}d. {path} is titled 'Subject' but is not an "
        f"Ohtli {label} note; it was left untouched.\n"
    )
    assert path.read_bytes() == before


@BY_KIND
def test_two_notes_with_the_same_title_refuse_as_ambiguous(capsys, tmp_path, command, folder, label, create):
    directory = tmp_path / folder
    directory.mkdir(parents=True)
    a = directory / "a.md"
    b = directory / "b.md"
    note_type = label.lower().replace(" ", "_")
    a.write_text(f"---\nid: aaa\nnote_type: {note_type}\n---\n\n# Subject\n\nfirst\n", encoding="utf-8")
    b.write_text(f"---\nid: bbb\nnote_type: {note_type}\n---\n\n# Subject\n\nsecond\n", encoding="utf-8")

    code, out = _run(capsys, command, "Subject")

    assert code == 1
    op = _op(command)
    assert out == (
        f"Not applicable: 'Subject' cannot be {op}d. 2 {label} notes are titled 'Subject' "
        f"(a.md, b.md); rename all but one, then {op} again.\n"
    )
    assert a.read_text(encoding="utf-8").endswith("first\n")
    assert b.read_text(encoding="utf-8").endswith("second\n")


@BY_KIND
def test_a_renamed_note_is_still_transitioned_through_the_cli(capsys, tmp_path, command, folder, label, create):
    assert _run(capsys, create, "Subject")[0] == 0
    renamed = tmp_path / folder / "renamed.md"
    (tmp_path / folder / "subject.md").rename(renamed)
    op = _op(command)
    if op == "reactivate":
        # Reactivate needs a historical note: archive it first through the
        # CLI, at its real (renamed) path.
        assert _run(capsys, command.replace("reactivate-", "archive-"), "Subject")[0] == 0

    code, out = _run(capsys, command, "Subject")

    assert code == 0
    assert out.startswith(f"{op.capitalize()}d 'Subject'")
    assert renamed.exists()


def test_the_operational_dependents_message_still_names_the_target_for_a_renamed_source(capsys, tmp_path):
    """The CLI used to look the source up by slug a second time just to
    name the dependents; after #161 it reads them off the already-located
    `result.dependents` instead, so a renamed source still gets the exact
    same message."""
    assert _run(capsys, "create-resource", "Source")[0] == 0
    assert _run(capsys, "create-project", "Target")[0] == 0
    assert (
        _run(capsys, "link", "--from-type", "resource", "--from", "Source", "--to-type", "project", "--to", "Target")[
            0
        ]
        == 0
    )
    (tmp_path / "resources" / "source.md").rename(tmp_path / "resources" / "renamed-source.md")

    code, out = _run(capsys, "archive-resource", "Source")

    assert code == 1
    assert out == (
        "Not applicable: 'Source' cannot be archived. It is still required "
        "operationally by 'Target'. Archive does not resolve this: unlink it, or "
        "archive the object(s) requiring it, first.\n"
    )
