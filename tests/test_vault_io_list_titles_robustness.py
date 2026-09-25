"""`list_existing_titles` must survive whatever else sits in a note folder.

Capture lists the titles of a folder before it writes. A directory named
`x.md`, a dangling symlink, or a file that is not UTF-8 used to make that
listing raise, which broke EVERY capture in the folder, whatever its title.
Anything that is not a readable Ohtli note is skipped, as a file without
frontmatter already was.
"""

import os
from datetime import date

import pytest

from ohtli.domain.project import Project
from ohtli.representation.project import to_representation
from ohtli.vault_io.markdown import list_existing_titles, write_project


def _note(tmp_path, title="Real Project"):
    return write_project(to_representation(Project(title=title), today=date(2026, 8, 25)), base_dir=tmp_path)


def test_a_directory_named_like_a_note_is_skipped(tmp_path):
    _note(tmp_path)
    (tmp_path / "trap.md").mkdir()

    assert list_existing_titles(base_dir=tmp_path) == {"Real Project"}


def test_a_dangling_symlink_is_skipped(tmp_path):
    _note(tmp_path)
    try:
        os.symlink(tmp_path / "nowhere.md", tmp_path / "dangling.md")
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links are not available here")

    assert list_existing_titles(base_dir=tmp_path) == {"Real Project"}


def test_a_file_that_is_not_utf8_is_skipped(tmp_path):
    _note(tmp_path)
    (tmp_path / "binary.md").write_bytes(b"\xff\xfe\x00 not utf-8 \x80\x81")

    assert list_existing_titles(base_dir=tmp_path) == {"Real Project"}


def test_a_symlink_to_a_real_note_still_counts_as_that_note(tmp_path):
    """Skipping symlinks wholesale would change what existed before."""
    real = _note(tmp_path / "real", title="Linked Project")
    try:
        os.symlink(real, tmp_path / "link.md")
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links are not available here")

    assert "Linked Project" in list_existing_titles(base_dir=tmp_path)


def test_notes_beside_the_skipped_entries_are_all_still_listed(tmp_path):
    _note(tmp_path, "Alpha")
    _note(tmp_path, "Beta")
    (tmp_path / "trap.md").mkdir()
    (tmp_path / "README.md").write_text("# Projects\n", encoding="utf-8")

    assert list_existing_titles(base_dir=tmp_path) == {"Alpha", "Beta"}


def test_a_named_pipe_is_skipped_without_ever_being_read(tmp_path, monkeypatch):
    """Reading a named pipe blocks forever, and `OSError` handling cannot help
    with that, so a non-regular file must be skipped BEFORE it is read.
    `read_text` fails for the pipe, so a regression fails at once instead of
    hanging the suite."""
    if not hasattr(os, "mkfifo"):
        pytest.skip("named pipes are not available here")
    _note(tmp_path)
    pipe = tmp_path / "pipe.md"
    os.mkfifo(pipe)
    real_read_text = type(pipe).read_text

    def read_text(self, *args, **kwargs):
        if self == pipe:
            raise AssertionError("a named pipe must be skipped without being read")
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(type(pipe), "read_text", read_text)

    assert list_existing_titles(base_dir=tmp_path) == {"Real Project"}
