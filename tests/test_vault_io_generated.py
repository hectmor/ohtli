"""`write_generated_file`: overwrite only what this feature itself generated.

A generated dashboard is a copy of other notes. The one thing it must never do
is destroy something a person wrote, so an existing file is overwritten only if
its first line is exactly the marker. Everything runs against `tmp_path`.
"""

import hashlib
import os

import pytest

from ohtli.vault_io.generated import write_generated_file

MARKER = "<!-- ohtli:generated test -->"
GOOD = MARKER + "\n\n# Title\n"


def _write(path, text=GOOD):
    return write_generated_file(path, text, marker=MARKER)


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _age(path):
    """Set a modification time far in the past, so a rewrite (even of identical
    bytes) is visible as a change."""
    os.utime(path, ns=(1_000_000_000, 1_000_000_000))
    return path.stat().st_mtime_ns


# ---- creating and regenerating ------------------------------------------------------


def test_it_creates_the_file_and_any_missing_parent_folders(tmp_path):
    path = tmp_path / "deep" / "nested" / "d.md"

    assert _write(path) == "created"
    assert path.read_text(encoding="utf-8") == GOOD


def test_a_second_identical_call_is_unchanged_and_writes_nothing(tmp_path):
    path = tmp_path / "d.md"
    _write(path)
    aged = _age(path)

    assert _write(path) == "unchanged"
    assert path.stat().st_mtime_ns == aged, "an unchanged file must not even be touched"


def test_new_content_over_a_generated_file_is_updated(tmp_path):
    path = tmp_path / "d.md"
    _write(path)

    assert _write(path, GOOD + "more\n") == "updated"
    assert path.read_text(encoding="utf-8") == GOOD + "more\n"


def test_regenerating_is_whole_never_a_merge(tmp_path):
    path = tmp_path / "d.md"
    _write(path, GOOD + "first version\n")

    _write(path, GOOD + "second version\n")

    assert "first version" not in path.read_text(encoding="utf-8")


def test_a_person_editing_a_generated_file_is_overwritten_as_the_marker_promises(tmp_path):
    path = tmp_path / "d.md"
    _write(path)
    path.write_text(GOOD + "an edit somebody made by hand\n", encoding="utf-8")

    assert _write(path) == "updated"
    assert path.read_text(encoding="utf-8") == GOOD


# ---- refusing anything that is not a generated file ---------------------------------

NOT_GENERATED = [
    pytest.param(b"# Mine\n\nprecious\n", id="hand-made-note"),
    pytest.param(b"---\nid: x\n---\n\n# Real\n", id="real-domain-object-with-frontmatter"),
    pytest.param(b"", id="empty-file"),
    pytest.param((MARKER + " extra text\n# x\n").encode(), id="marker-is-only-a-prefix-of-the-line"),
    pytest.param(("# first\n" + MARKER + "\n").encode(), id="marker-on-the-second-line"),
    pytest.param(MARKER.encode(), id="marker-without-a-trailing-newline"),
    pytest.param(("\n" + MARKER + "\n").encode(), id="marker-after-a-blank-line"),
    pytest.param((" " + MARKER + "\n").encode(), id="marker-with-a-leading-space"),
    pytest.param(b"<!-- ohtli:generated something-else -->\n# x\n", id="a-different-marker"),
    pytest.param(b"\xff\xfe\x00 not utf-8 \x80\x81", id="not-utf-8"),
]


@pytest.mark.parametrize("content", NOT_GENERATED)
def test_a_file_that_is_not_generated_is_refused_and_left_untouched(tmp_path, content):
    path = tmp_path / "d.md"
    path.write_bytes(content)
    aged = _age(path)

    assert _write(path) == "refused"
    assert path.read_bytes() == content
    assert path.stat().st_mtime_ns == aged


def test_a_directory_at_the_path_is_refused(tmp_path):
    path = tmp_path / "d.md"
    path.mkdir()

    assert _write(path) == "refused"
    assert path.is_dir() and list(path.iterdir()) == []


def _make_non_regular(path, kind):
    if kind == "directory":
        path.mkdir()
    else:
        if not hasattr(os, "mkfifo"):
            pytest.skip("named pipes are not available here")
        os.mkfifo(path)


@pytest.mark.parametrize("kind", ["directory", "fifo"])
def test_a_non_regular_file_is_refused_before_it_is_ever_read(tmp_path, monkeypatch, kind):
    """Reading a named pipe or a device blocks forever, so the `is_file()` check
    must come first. `read_text` is replaced by a function that fails, so a
    regression fails this test at once instead of hanging the suite."""
    path = tmp_path / "d.md"
    _make_non_regular(path, kind)

    def must_not_be_read(*args, **kwargs):
        raise AssertionError("a non-regular file must be refused without being read")

    monkeypatch.setattr(type(path), "read_text", must_not_be_read)

    assert _write(path) == "refused"


# ---- symbolic links: writing through one could reach a file outside the vault -------


def _symlink(link, target):
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links are not available here")


def test_a_symlink_to_a_generated_file_is_refused_and_its_target_untouched(tmp_path):
    target = tmp_path / "elsewhere.md"
    _write(target)
    link = tmp_path / "d.md"
    _symlink(link, target)
    before = _sha(target)

    assert _write(link, GOOD + "changed\n") == "refused"
    assert _sha(target) == before
    assert link.is_symlink()


def test_a_symlink_to_a_hand_made_file_is_refused(tmp_path):
    target = tmp_path / "mine.md"
    target.write_text("# Mine\n", encoding="utf-8")
    link = tmp_path / "d.md"
    _symlink(link, target)

    assert _write(link) == "refused"
    assert target.read_text(encoding="utf-8") == "# Mine\n"


def test_a_dangling_symlink_is_refused_and_its_target_is_not_created(tmp_path):
    link = tmp_path / "d.md"
    _symlink(link, tmp_path / "nowhere.md")

    assert _write(link) == "refused"
    assert not (tmp_path / "nowhere.md").exists()


def test_a_symlink_to_a_directory_is_refused(tmp_path):
    (tmp_path / "adir").mkdir()
    link = tmp_path / "d.md"
    _symlink(link, tmp_path / "adir")

    assert _write(link) == "refused"


# ---- misuse -------------------------------------------------------------------------


def test_text_without_the_marker_raises_and_writes_nothing(tmp_path):
    path = tmp_path / "deep" / "d.md"

    with pytest.raises(ValueError):
        write_generated_file(path, "# no marker\n", marker=MARKER)

    assert not path.exists()
    assert not path.parent.exists(), "validation happens before any folder is created"


def test_a_marker_not_followed_by_a_newline_raises(tmp_path):
    with pytest.raises(ValueError):
        write_generated_file(tmp_path / "d.md", MARKER + " and no line break", marker=MARKER)


def test_text_where_the_marker_is_not_the_first_line_raises(tmp_path):
    with pytest.raises(ValueError):
        write_generated_file(tmp_path / "d.md", "# title\n" + MARKER + "\n", marker=MARKER)


def test_a_file_whose_parent_is_a_regular_file_raises_instead_of_being_swallowed(tmp_path):
    (tmp_path / "blocker").write_text("i am a file", encoding="utf-8")

    with pytest.raises((FileExistsError, NotADirectoryError)):
        _write(tmp_path / "blocker" / "d.md")


# ---- line endings: deliberate, see the function's docstring --------------------------


def test_a_generated_file_converted_to_crlf_by_an_editor_is_still_recognised(tmp_path):
    """`read_text` normalises line endings, so a legitimate dashboard whose
    endings an editor or git converted is regenerated, not stranded."""
    path = tmp_path / "d.md"
    path.write_bytes(GOOD.replace("\n", "\r\n").encode())

    assert _write(path, GOOD + "new\n") == "updated"
    assert path.read_text(encoding="utf-8") == GOOD + "new\n"


def test_a_crlf_file_with_the_same_content_is_unchanged_and_left_as_it_is(tmp_path):
    path = tmp_path / "d.md"
    crlf = GOOD.replace("\n", "\r\n").encode()
    path.write_bytes(crlf)

    assert _write(path) == "unchanged"
    assert path.read_bytes() == crlf


def test_the_line_ending_style_is_not_what_protects_a_hand_written_file(tmp_path):
    """What protects a hand-written file is the exact marker line, so a
    hand-written CRLF file without it is refused just like an LF one."""
    path = tmp_path / "d.md"
    content = b"# my note\r\n" + MARKER.encode() + b"\r\n"
    path.write_bytes(content)

    assert _write(path) == "refused"
    assert path.read_bytes() == content
