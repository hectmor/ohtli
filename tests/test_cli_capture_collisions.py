"""What the CLI tells the user when a create would overwrite a file.

`create-*` and `process-inbox` refuse (exit 1 for a create or a named entry;
a batch still exits 0), change nothing, emit no Event, and say why:

- the title already exists      -> the message every create-* had before, unchanged
- another Ohtli note has the file name -> names the note that holds it
- something that is not an Ohtli note has it -> says it was left untouched
- the file name is reserved (`readme`, `index`) -> says so

Every vault directory is redirected to `tmp_path`.
"""

import pytest

from ohtli.cli import main
from ohtli.vault_io import paths

# command, folder inside the vault, label, indefinite article + label
KINDS = [
    ("create-project", "projects", "Project", "a Project"),
    ("create-area", "areas", "Area", "an Area"),
    ("create-resource", "resources", "Resource", "a Resource"),
    ("create-reference", "references", "Reference", "a Reference"),
    ("create-meeting", "meetings", "Meeting", "a Meeting"),
    ("create-journal-entry", "journal", "Journal Entry", "a Journal Entry"),
]
BY_KIND = pytest.mark.parametrize(
    ("command", "folder", "label", "article"), KINDS, ids=[k[0] for k in KINDS]
)


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


def _snapshot(tmp_path):
    return {
        str(p.relative_to(tmp_path)): (p.read_bytes(), p.stat().st_mtime_ns)
        for p in sorted(tmp_path.rglob("*"))
        if p.is_file()
    }


def _entry(tmp_path, text, name="entry.md"):
    inbox = tmp_path / "inbox"
    inbox.mkdir(exist_ok=True)
    (inbox / name).write_text(text, encoding="utf-8")
    return inbox / name


# ---- create-*: the three ways a create is refused -----------------------------------


@BY_KIND
def test_an_existing_title_keeps_the_message_it_always_had(capsys, tmp_path, command, folder, label, article):
    assert _run(capsys, command, "Foo Bar")[0] == 0
    before = _snapshot(tmp_path)

    code, out = _run(capsys, command, "Foo Bar")

    assert code == 1
    assert out == f"Not applicable: {article} titled 'Foo Bar' already exists.\n"
    assert _snapshot(tmp_path) == before


@BY_KIND
def test_a_title_with_the_same_file_name_names_the_note_that_holds_it(
    capsys, tmp_path, command, folder, label, article
):
    assert _run(capsys, command, "Foo Bar")[0] == 0
    before = _snapshot(tmp_path)
    held = tmp_path / folder / "foo-bar.md"

    code, out = _run(capsys, command, "foo-bar")

    assert code == 1
    assert out == (
        f"Not applicable: {article} titled 'foo-bar' cannot be created: {held} already holds "
        f"{label} 'Foo Bar' (same file name). Choose a different title.\n"
    )
    assert _snapshot(tmp_path) == before


@BY_KIND
def test_a_hand_made_file_is_left_untouched_and_the_message_says_so(
    capsys, tmp_path, command, folder, label, article
):
    path = tmp_path / folder / "my-plan.md"
    path.parent.mkdir(parents=True)
    path.write_text("# mine\n\nprecious\n", encoding="utf-8")
    before = _snapshot(tmp_path)

    code, out = _run(capsys, command, "My Plan")

    assert code == 1
    assert out == (
        f"Not applicable: {article} titled 'My Plan' cannot be created: {path} already exists and is "
        f"not an Ohtli note; it was left untouched. Move or rename it, or choose a different title.\n"
    )
    assert _snapshot(tmp_path) == before


@BY_KIND
def test_a_reserved_file_name_is_refused_even_when_nothing_is_there(
    capsys, tmp_path, command, folder, label, article
):
    code, out = _run(capsys, command, "Index")

    assert code == 1
    assert out == (
        f"Not applicable: {article} titled 'Index' cannot be created: the file name 'index.md' is "
        f"reserved. Choose a different title.\n"
    )
    assert _snapshot(tmp_path) == {}


def test_create_area_index_no_longer_overwrites_a_hand_made_index(capsys, tmp_path):
    index = tmp_path / "areas" / "index.md"
    index.parent.mkdir()
    index.write_text("# My hand-made index\n\nprecious\n", encoding="utf-8")

    code, _ = _run(capsys, "create-area", "Index")

    assert code == 1
    assert index.read_text(encoding="utf-8") == "# My hand-made index\n\nprecious\n"


@BY_KIND
def test_a_refused_create_emits_no_event(capsys, tmp_path, command, folder, label, article):
    _run(capsys, command, "Foo Bar")
    log = (tmp_path / ".ohtli" / "events.jsonl").read_bytes()

    _run(capsys, command, "foo-bar")
    _run(capsys, command, "Index")

    assert (tmp_path / ".ohtli" / "events.jsonl").read_bytes() == log


@BY_KIND
def test_a_free_title_still_creates_normally(capsys, tmp_path, command, folder, label, article):
    code, out = _run(capsys, command, "Foo Bar")

    assert code == 0
    assert out.startswith(f"Captured {label} 'Foo Bar'")
    assert (tmp_path / folder / "foo-bar.md").exists()


# ---- process-inbox ------------------------------------------------------------------


def test_a_named_entry_that_would_overwrite_is_refused_kept_and_exits_one(capsys, tmp_path):
    assert _run(capsys, "create-project", "Foo Bar")[0] == 0
    held = tmp_path / "projects" / "foo-bar.md"
    entry = _entry(tmp_path, "foo-bar\n")
    before = _snapshot(tmp_path)

    code, out = _run(capsys, "process-inbox", "--entry", "entry")

    assert code == 1
    assert out == (
        "Not applicable: 'entry.md' left untouched in Inbox. "
        f"{held} already holds Project 'Foo Bar' (same file name); choose a different title.\n"
    )
    assert entry.read_text(encoding="utf-8") == "foo-bar\n"
    assert _snapshot(tmp_path) == before


def test_in_batch_mode_a_refused_entry_is_reported_kept_and_the_others_still_processed(capsys, tmp_path):
    _run(capsys, "create-project", "Foo Bar")
    bad = _entry(tmp_path, "foo-bar\n", name="a-bad.md")
    good = _entry(tmp_path, "Baz Qux\n", name="b-good.md")

    code, out = _run(capsys, "process-inbox")

    assert code == 0, "batch mode keeps exiting 0 when it refuses entries"
    assert "Not applicable: 'a-bad.md' left untouched in Inbox. " in out
    assert "Processed Project 'Baz Qux'" in out
    assert bad.exists() and not good.exists()
    assert (tmp_path / "projects" / "baz-qux.md").exists()


def test_a_hand_made_file_and_a_reserved_title_are_explained_for_an_entry(capsys, tmp_path):
    path = tmp_path / "projects" / "my-plan.md"
    path.parent.mkdir(parents=True)
    path.write_text("# mine\n", encoding="utf-8")
    _entry(tmp_path, "My Plan\n", name="one.md")
    _entry(tmp_path, "Index\n", name="two.md")

    _, out = _run(capsys, "process-inbox")

    assert (
        f"Not applicable: 'one.md' left untouched in Inbox. {path} already exists and is not an Ohtli "
        f"note; it was left untouched. Move or rename it, or choose a different title.\n"
    ) in out
    assert (
        "Not applicable: 'two.md' left untouched in Inbox. The file name 'index.md' is reserved; "
        "choose a different title.\n"
    ) in out
    assert path.read_text(encoding="utf-8") == "# mine\n"


def test_a_blank_entry_keeps_its_original_message_without_a_reason(capsys, tmp_path):
    _entry(tmp_path, "   \n", name="blank.md")

    _, out = _run(capsys, "process-inbox")

    assert out == "Not applicable: 'blank.md' left untouched in Inbox.\n"


def test_an_entry_for_an_existing_title_is_still_an_update(capsys, tmp_path):
    _run(capsys, "create-project", "Foo Bar")
    _entry(tmp_path, "Foo Bar\n\nsome new notes\n")

    code, out = _run(capsys, "process-inbox")

    assert code == 0
    assert out.startswith("Updated Project 'Foo Bar'")


def test_process_inbox_as_another_kind_explains_with_that_kinds_label(capsys, tmp_path):
    _run(capsys, "create-area", "Foo Bar")
    held = tmp_path / "areas" / "foo-bar.md"
    _entry(tmp_path, "foo-bar\n")

    _, out = _run(capsys, "process-inbox", "--as", "area")

    assert f"{held} already holds Area 'Foo Bar' (same file name)" in out
