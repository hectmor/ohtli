"""`find_inbox_entry`: selecting one Inbox entry by file name.

Processing an entry deletes it, so a name must never reach a file outside the
Inbox. Everything here runs against `tmp_path`, with a secret file placed
outside the Inbox to prove it stays unreachable.
"""

import pytest

from ohtli.vault_io.markdown import find_inbox_entry, list_inbox_entries


@pytest.fixture
def vault(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (tmp_path / "secret.md").write_text("OUTSIDE THE INBOX\n", encoding="utf-8")
    (tmp_path / "projects").mkdir()
    (tmp_path / "projects" / "victim.md").write_text("---\nid: x\n---\n\n# Victim\n", encoding="utf-8")
    (inbox / "note.md").write_text("a\n", encoding="utf-8")
    (inbox / "Other Note.md").write_text("b\n", encoding="utf-8")
    (inbox / "README.md").write_text("navigation\n", encoding="utf-8")
    (inbox / "index.md").write_text("navigation\n", encoding="utf-8")
    (inbox / "plain.txt").write_text("not markdown\n", encoding="utf-8")
    (inbox / "sub").mkdir()
    (inbox / "sub" / "deep.md").write_text("in a sub-directory\n", encoding="utf-8")
    return tmp_path


def _find(vault, name):
    found = find_inbox_entry(name, base_dir=vault / "inbox")
    return found.name if found else None


def test_an_entry_is_found_with_or_without_the_md_extension(vault):
    assert _find(vault, "note") == "note.md"
    assert _find(vault, "note.md") == "note.md"


def test_the_returned_path_is_the_one_in_the_inbox(vault):
    found = find_inbox_entry("note", base_dir=vault / "inbox")

    assert found == vault / "inbox" / "note.md"
    assert found in list_inbox_entries(base_dir=vault / "inbox")


def test_a_name_with_spaces_is_matched_exactly(vault):
    assert _find(vault, "Other Note") == "Other Note.md"
    assert _find(vault, "Other Note.md") == "Other Note.md"
    assert _find(vault, "Other  Note") is None


def test_matching_is_exact_and_case_sensitive(vault):
    assert _find(vault, "NOTE") is None
    assert _find(vault, "note ") is None
    assert _find(vault, " note") is None


def test_a_missing_entry_is_none(vault):
    assert _find(vault, "missing") is None
    assert find_inbox_entry("note", base_dir=vault / "no-such-inbox") is None


@pytest.mark.parametrize("name", ["README", "README.md", "index", "index.md"])
def test_reserved_navigation_names_are_not_entries(vault, name):
    assert _find(vault, name) is None


def test_a_file_that_is_not_markdown_is_not_an_entry(vault):
    assert _find(vault, "plain.txt") is None
    assert _find(vault, "plain") is None


@pytest.mark.parametrize("name", ["sub/deep.md", "sub/deep", "deep", "deep.md"])
def test_a_file_in_a_subdirectory_is_not_an_entry(vault, name):
    assert _find(vault, name) is None


@pytest.mark.parametrize(
    "name",
    [
        "../secret.md",
        "../secret",
        "../projects/victim.md",
        "../projects/victim",
        "../inbox/note.md",
        "./note.md",
        "sub/../note.md",
        "note.md/",
        "/note.md",
        "\\note.md",
        "note\\.md",
        ".",
        "..",
    ],
)
def test_no_path_like_name_can_select_anything(vault, name):
    assert _find(vault, name) is None


def test_an_absolute_path_cannot_select_anything(vault):
    assert find_inbox_entry(str(vault / "secret.md"), base_dir=vault / "inbox") is None
    assert find_inbox_entry(str(vault / "projects" / "victim.md"), base_dir=vault / "inbox") is None
    assert find_inbox_entry(str(vault / "inbox" / "note.md"), base_dir=vault / "inbox") is None


@pytest.mark.parametrize("name", ["", " ", "   ", "\t"])
def test_a_blank_name_selects_nothing(vault, name):
    assert _find(vault, name) is None


def test_a_blank_name_does_not_select_a_file_called_exactly_dot_md(vault):
    """`""` would become `.md`; the blank check must stop it before that."""
    (vault / "inbox" / ".md").write_text("hidden\n", encoding="utf-8")

    assert _find(vault, "") is None
    assert _find(vault, ".md") == ".md", "a file with that exact name is in the batch's set too"


def test_the_selectable_set_is_exactly_what_the_batch_lists(vault):
    """Whatever `list_inbox_entries` returns is selectable by its own name, and
    nothing else is: one rule for both modes."""
    inbox = vault / "inbox"
    listed = list_inbox_entries(base_dir=inbox)

    assert [find_inbox_entry(entry.name, base_dir=inbox) for entry in listed] == listed
    everything = {p.name for p in inbox.rglob("*")} | {"", ".", ".."}
    selectable = {n for n in everything if find_inbox_entry(n, base_dir=inbox) is not None}
    assert selectable == {entry.name for entry in listed}


def test_finding_an_entry_reads_and_changes_nothing(vault):
    before = {p: p.read_bytes() for p in vault.rglob("*") if p.is_file()}

    for name in ("note", "../secret.md", "README", "", "missing", "sub/deep.md"):
        _find(vault, name)

    assert {p: p.read_bytes() for p in vault.rglob("*") if p.is_file()} == before
