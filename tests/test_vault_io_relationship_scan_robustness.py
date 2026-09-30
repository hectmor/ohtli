"""`find_note_by_id` and `list_projects_linking_to` must survive whatever else
sits in a note folder, the same way `list_existing_titles` already does
(Phase 38) and `find_notes_titled`/`find_any_note_titled` already do (Phase
39).

These are read-only lookups, not writes: a symlink to a real note is safe to
follow and must still be found (unlike `inspect_target`, which never follows
a symlink because it also guards writes). Excluding a valid symlinked note
here would be less safe, not more: Archive's operational-dependents guard
uses `find_note_by_id`, and missing a real dependent would let an Archive
through that should have been refused.
"""

import os

import pytest

from ohtli.vault_io.markdown import find_note_by_id, list_projects_linking_to

TARGET_ID = "11111111-1111-1111-1111-111111111111"


def _note(directory, name, note_id, *, links_to=None):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    relationships = ""
    if links_to is not None:
        relationships = (
            "relationships:\n"
            "- id: rel-1\n"
            "  type: belongs to\n"
            f"  target_id: {links_to}\n"
            "  target_type: area\n"
        )
    path.write_text(
        f"---\nid: {note_id}\nnote_type: project\nstatus: planned\ncontext: operational\n{relationships}"
        f"---\n\n# {name[:-3]}\n\nbody\n",
        encoding="utf-8",
    )
    return path


def _symlink(link, target):
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links are not available here")


# ---- find_note_by_id ------------------------------------------------------------------


def test_find_note_by_id_skips_a_directory_named_like_a_note(tmp_path):
    real = _note(tmp_path, "real.md", TARGET_ID)
    (tmp_path / "trap.md").mkdir()

    found = find_note_by_id(tmp_path, TARGET_ID)

    assert found is not None and found["path"] == real


def test_find_note_by_id_skips_a_dangling_symlink(tmp_path):
    real = _note(tmp_path, "real.md", TARGET_ID)
    _symlink(tmp_path / "ghost.md", tmp_path / "nowhere.md")

    found = find_note_by_id(tmp_path, TARGET_ID)

    assert found is not None and found["path"] == real


def test_find_note_by_id_skips_a_non_utf8_file(tmp_path):
    real = _note(tmp_path, "real.md", TARGET_ID)
    (tmp_path / "binary.md").write_bytes(b"\xff\xfe\x00 not utf-8 \x80\x81")

    found = find_note_by_id(tmp_path, TARGET_ID)

    assert found is not None and found["path"] == real


def test_find_note_by_id_follows_a_symlink_to_the_real_note(tmp_path):
    """Unlike `inspect_target`, this lookup is read-only: a symlinked note
    must still be found, or Archive's dependents guard could miss a real
    dependency and let a refused Archive through."""
    real_dir = tmp_path / "elsewhere"
    real = _note(real_dir, "real.md", TARGET_ID)
    directory = tmp_path / "projects"
    directory.mkdir()
    _symlink(directory / "linked.md", real)

    found = find_note_by_id(directory, TARGET_ID)

    assert found is not None and found["id"] == TARGET_ID


def test_find_note_by_id_returns_none_when_nothing_matches(tmp_path):
    _note(tmp_path, "real.md", "other-id")

    assert find_note_by_id(tmp_path, TARGET_ID) is None


def test_find_note_by_id_never_reads_a_named_pipe(tmp_path, monkeypatch):
    if not hasattr(os, "mkfifo"):
        pytest.skip("named pipes are not available here")
    real = _note(tmp_path, "real.md", TARGET_ID)
    pipe = tmp_path / "pipe.md"
    os.mkfifo(pipe)
    real_read_text = type(pipe).read_text

    def read_text(self, *args, **kwargs):
        if self == pipe:
            raise AssertionError("a named pipe must be skipped without being read")
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(type(pipe), "read_text", read_text)

    found = find_note_by_id(tmp_path, TARGET_ID)

    assert found is not None and found["path"] == real


# ---- list_projects_linking_to ----------------------------------------------------------


def test_list_projects_linking_to_skips_a_directory_named_like_a_note(tmp_path):
    _note(tmp_path, "real.md", "id-1", links_to=TARGET_ID)
    (tmp_path / "trap.md").mkdir()

    found = list_projects_linking_to(TARGET_ID, "belongs to", base_dir=tmp_path)

    assert [p["id"] for p in found] == ["id-1"]


def test_list_projects_linking_to_skips_a_dangling_symlink(tmp_path):
    _note(tmp_path, "real.md", "id-1", links_to=TARGET_ID)
    _symlink(tmp_path / "ghost.md", tmp_path / "nowhere.md")

    found = list_projects_linking_to(TARGET_ID, "belongs to", base_dir=tmp_path)

    assert [p["id"] for p in found] == ["id-1"]


def test_list_projects_linking_to_skips_a_non_utf8_file(tmp_path):
    _note(tmp_path, "real.md", "id-1", links_to=TARGET_ID)
    (tmp_path / "binary.md").write_bytes(b"\xff\xfe\x00 not utf-8 \x80\x81")

    found = list_projects_linking_to(TARGET_ID, "belongs to", base_dir=tmp_path)

    assert [p["id"] for p in found] == ["id-1"]


def test_list_projects_linking_to_follows_a_symlink_to_a_real_linking_note(tmp_path):
    real_dir = tmp_path / "elsewhere"
    real = _note(real_dir, "real.md", "id-1", links_to=TARGET_ID)
    directory = tmp_path / "projects"
    directory.mkdir()
    _symlink(directory / "linked.md", real)

    found = list_projects_linking_to(TARGET_ID, "belongs to", base_dir=directory)

    assert [p["id"] for p in found] == ["id-1"]


def test_list_projects_linking_to_never_reads_a_named_pipe(tmp_path, monkeypatch):
    if not hasattr(os, "mkfifo"):
        pytest.skip("named pipes are not available here")
    _note(tmp_path, "real.md", "id-1", links_to=TARGET_ID)
    pipe = tmp_path / "pipe.md"
    os.mkfifo(pipe)
    real_read_text = type(pipe).read_text

    def read_text(self, *args, **kwargs):
        if self == pipe:
            raise AssertionError("a named pipe must be skipped without being read")
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(type(pipe), "read_text", read_text)

    found = list_projects_linking_to(TARGET_ID, "belongs to", base_dir=tmp_path)

    assert [p["id"] for p in found] == ["id-1"]
