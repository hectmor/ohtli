"""What the CLI tells the user when `enrich-*` cannot find the note to
enrich, or finds more than one that could be it.

The prefix `Not applicable: '<title>' cannot be enriched.` is unchanged (no
existing test pinned it, but nothing should need to). `ambiguous_title` and
`not_an_ohtli_note` add a sentence after it, the same idea as Processing
Update's `_inbox_reason` (#156) but with its own wording: this is not an
Inbox entry, so "process again"/"update" would be the wrong verbs.
"""

import pytest

from ohtli.cli import main
from ohtli.vault_io import paths

KINDS = [
    ("enrich-project", "projects", "Project"),
    ("enrich-area", "areas", "Area"),
    ("enrich-resource", "resources", "Resource"),
]
BY_KIND = pytest.mark.parametrize(("command", "folder", "label"), KINDS, ids=[k[0] for k in KINDS])


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


def _enrich_args(title="Subject"):
    return [title, "--understanding-title", "Learned It", "--understanding", "A fact.", "--provenance", "Source A"]


@BY_KIND
def test_an_ordinary_refusal_keeps_its_original_message(capsys, tmp_path, command, folder, label):
    """No note exists at all: the pre-existing message, unaffected by this
    change."""
    code, out = _run(capsys, command, *_enrich_args())

    assert code == 1
    assert out == "Not applicable: 'Subject' cannot be enriched.\n"


@BY_KIND
def test_a_hand_made_file_is_refused_and_named_not_half_written(capsys, tmp_path, command, folder, label):
    path = tmp_path / folder / "subject.md"
    path.parent.mkdir(parents=True)
    before = b"---\ntags: []\n---\n\n# Subject\n\nmine\n"
    path.write_bytes(before)

    code, out = _run(capsys, command, *_enrich_args())

    assert code == 1
    assert out == (
        f"Not applicable: 'Subject' cannot be enriched. {path} is titled 'Subject' but is not an "
        f"Ohtli {label} note; it was left untouched.\n"
    )
    assert path.read_bytes() == before


@BY_KIND
def test_two_notes_with_the_same_title_refuse_as_ambiguous(capsys, tmp_path, command, folder, label):
    directory = tmp_path / folder
    directory.mkdir(parents=True)
    a = directory / "a.md"
    b = directory / "b.md"
    note_type = label.lower()
    a.write_text(f"---\nid: aaa\nnote_type: {note_type}\n---\n\n# Subject\n\nfirst\n", encoding="utf-8")
    b.write_text(f"---\nid: bbb\nnote_type: {note_type}\n---\n\n# Subject\n\nsecond\n", encoding="utf-8")

    code, out = _run(capsys, command, *_enrich_args())

    assert code == 1
    assert out == (
        f"Not applicable: 'Subject' cannot be enriched. 2 {label} notes are titled 'Subject' "
        "(a.md, b.md); rename all but one, then enrich again.\n"
    )
    assert a.read_text(encoding="utf-8").endswith("first\n")
    assert b.read_text(encoding="utf-8").endswith("second\n")


@BY_KIND
def test_a_renamed_note_is_still_enriched_through_the_cli(capsys, tmp_path, command, folder, label):
    create = {"enrich-project": "create-project", "enrich-area": "create-area", "enrich-resource": "create-resource"}
    assert _run(capsys, create[command], "Subject")[0] == 0
    renamed = tmp_path / folder / "renamed.md"
    (tmp_path / folder / "subject.md").rename(renamed)

    code, out = _run(capsys, command, *_enrich_args())

    assert code == 0
    assert out.startswith("Enriched 'Subject'")
    assert "Learned It" in renamed.read_text(encoding="utf-8")
