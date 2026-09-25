"""Capture and Processing's Create must never overwrite an existing file.

Capture's title check is not enough: a note is named by the SLUG of its title,
so "Foo Bar" and "foo-bar" share a file, and a hand-made note (a README, an
index, anything) can already sit at the target path. Creating over any of them
destroyed data, and logged a "Created" event for it.

A refused create leaves everything as it was: no file touched, no Event, and
an Inbox entry stays in the Inbox. The result says why, in `reason`:

- `title_exists`   an object of this type already has this title
- `same_file_name` another Ohtli note already holds the file name this title needs
- `path_occupied`  something that is not an Ohtli note holds it
- `reserved_name`  the slug is `readme` or `index`, never used for a note

Everything runs against `tmp_path`, passing both `base_dir` and `events_dir`.
"""

import os

import pytest

from ohtli.execution import execution
from ohtli.execution.execution import (
    Actor,
    ExecutionRequest,
    ProcessingRequest,
    execute_capture,
    execute_processing,
)
from ohtli.execution.specs import ALL_SPECS
from ohtli.vault_io.markdown import inspect_target
from ohtli.workflow import capture

SPECS = pytest.mark.parametrize("spec", ALL_SPECS, ids=[s.note_type for s in ALL_SPECS])


def _capture(spec, title, tmp_path):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path / "events",
    )


def _process(spec, text, tmp_path, name="entry.md"):
    inbox = tmp_path / "inbox"
    inbox.mkdir(exist_ok=True)
    entry = inbox / name
    entry.write_text(text, encoding="utf-8")
    result = execute_processing(
        ProcessingRequest(entry_path=entry, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path / "events",
    )
    return entry, result


def _snapshot(tmp_path):
    """Bytes and modification time of every file under `tmp_path`."""
    return {
        str(p.relative_to(tmp_path)): (p.read_bytes(), p.stat().st_mtime_ns)
        for p in sorted(tmp_path.rglob("*"))
        if p.is_file() and not p.is_symlink()
    }


def _log(tmp_path):
    log = tmp_path / "events" / "events.jsonl"
    return log.read_bytes() if log.exists() else b""


def _hand_made(spec, tmp_path, title="My Plan", content=b"# mine\n\nprecious\n"):
    path = spec.file_path(title, base_dir=tmp_path / spec.note_type)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def _assert_untouched_refusal(result, tmp_path, before, log_before, reason):
    assert result.applicable is False
    assert result.reason == reason
    assert result.event is None and result.path is None
    assert _snapshot(tmp_path) == before
    assert _log(tmp_path) == log_before


# ---- Capture: a hand-made file at the target path -----------------------------------


@SPECS
def test_a_hand_made_file_at_the_target_path_is_refused_and_left_untouched(spec, tmp_path):
    path = _hand_made(spec, tmp_path)
    before, log = _snapshot(tmp_path), _log(tmp_path)

    result = _capture(spec, "My Plan", tmp_path)

    _assert_untouched_refusal(result, tmp_path, before, log, "path_occupied")
    assert result.blocked_path == path
    assert path.read_bytes() == b"# mine\n\nprecious\n"


@SPECS
def test_a_file_with_frontmatter_but_no_ohtli_identity_is_refused_as_not_an_ohtli_note(spec, tmp_path):
    _hand_made(spec, tmp_path, content=b"---\ntype: note\n---\n\nmine\n")
    before, log = _snapshot(tmp_path), _log(tmp_path)

    result = _capture(spec, "My Plan", tmp_path)

    _assert_untouched_refusal(result, tmp_path, before, log, "path_occupied")


@SPECS
def test_a_directory_at_the_target_path_is_refused(spec, tmp_path):
    path = spec.file_path("My Plan", base_dir=tmp_path / spec.note_type)
    path.mkdir(parents=True)

    result = _capture(spec, "My Plan", tmp_path)

    assert (result.applicable, result.reason) == (False, "path_occupied")
    assert path.is_dir() and list(path.iterdir()) == []
    assert _log(tmp_path) == b""


def _symlink(link, target):
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links are not available here")


@SPECS
def test_a_dangling_symlink_at_the_target_path_is_refused_and_its_target_not_created(spec, tmp_path):
    path = spec.file_path("My Plan", base_dir=tmp_path / spec.note_type)
    path.parent.mkdir(parents=True)
    _symlink(path, tmp_path / "nowhere.md")

    result = _capture(spec, "My Plan", tmp_path)

    assert (result.applicable, result.reason) == (False, "path_occupied")
    assert not (tmp_path / "nowhere.md").exists()
    assert path.is_symlink()
    assert _log(tmp_path) == b""


@SPECS
def test_a_symlink_to_an_outside_file_is_refused_and_the_outside_file_untouched(spec, tmp_path):
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    path = spec.file_path("My Plan", base_dir=tmp_path / spec.note_type)
    path.parent.mkdir(parents=True)
    _symlink(path, outside)

    result = _capture(spec, "My Plan", tmp_path)

    assert (result.applicable, result.reason) == (False, "path_occupied")
    assert outside.read_text(encoding="utf-8") == "outside\n"


# ---- Capture: two titles that share a slug ------------------------------------------


@SPECS
def test_a_second_title_with_the_same_slug_is_refused_and_the_first_note_kept(spec, tmp_path):
    first = _capture(spec, "Foo Bar", tmp_path)
    before, log = _snapshot(tmp_path), _log(tmp_path)

    result = _capture(spec, "foo-bar", tmp_path)

    _assert_untouched_refusal(result, tmp_path, before, log, "same_file_name")
    assert result.blocked_path == first.path
    assert result.occupant_title == "Foo Bar"
    assert len(log.splitlines()) == 1, "exactly one Created event for the one note"


@SPECS
def test_a_file_with_an_ohtli_identity_and_another_title_is_same_file_name(spec, tmp_path):
    _hand_made(
        spec,
        tmp_path,
        content=b"---\nid: abc-123\nnote_type: project\n---\n\n# Something Else\n\nmine\n",
    )

    result = _capture(spec, "My Plan", tmp_path)

    assert (result.applicable, result.reason) == (False, "same_file_name")
    assert result.occupant_title == "Something Else"


@SPECS
def test_the_same_title_is_still_title_exists_with_its_unchanged_meaning(spec, tmp_path):
    _capture(spec, "Foo Bar", tmp_path)
    before, log = _snapshot(tmp_path), _log(tmp_path)

    result = _capture(spec, "Foo Bar", tmp_path)

    _assert_untouched_refusal(result, tmp_path, before, log, "title_exists")


# ---- Capture: the reserved slugs ----------------------------------------------------


@SPECS
@pytest.mark.parametrize("title", ["Index", "index", "INDEX", "README", "Readme"])
def test_the_reserved_slugs_are_always_refused_even_when_no_file_exists(spec, tmp_path, title):
    result = _capture(spec, title, tmp_path)

    assert (result.applicable, result.reason) == (False, "reserved_name")
    assert _snapshot(tmp_path) == {}
    assert _log(tmp_path) == b""


@SPECS
def test_a_hand_made_index_is_left_untouched_by_capturing_index(spec, tmp_path):
    path = spec.file_path("Index", base_dir=tmp_path / spec.note_type)
    path.parent.mkdir(parents=True)
    path.write_text("# My hand-made index\n\nprecious\n", encoding="utf-8")
    before = _snapshot(tmp_path)

    _capture(spec, "Index", tmp_path)

    assert _snapshot(tmp_path) == before


@SPECS
def test_a_title_that_merely_contains_a_reserved_word_is_fine(spec, tmp_path):
    result = _capture(spec, "Index Fund", tmp_path)

    assert result.applicable is True and result.reason is None


# ---- a successful capture is unchanged ----------------------------------------------


@SPECS
def test_a_free_path_still_creates_the_note_and_the_event(spec, tmp_path):
    result = _capture(spec, "Foo Bar", tmp_path)

    assert result.applicable is True and result.reason is None
    assert result.path.exists()
    assert len(_log(tmp_path).splitlines()) == 1


# ---- the race-free backstop: exclusive create ---------------------------------------


@SPECS
def test_writing_a_note_over_an_existing_file_raises_and_leaves_it_untouched(spec, tmp_path):
    path = _hand_made(spec, tmp_path)
    domain_object = capture.transform("My Plan", spec.domain_type)

    with pytest.raises(FileExistsError):
        spec.write(spec.to_representation(domain_object), base_dir=tmp_path / spec.note_type)

    assert path.read_bytes() == b"# mine\n\nprecious\n"


@SPECS
def test_if_the_check_misses_a_file_the_write_still_refuses_and_no_event_is_emitted(
    spec, tmp_path, monkeypatch
):
    """Simulates a file that appears between the check and the write."""
    path = _hand_made(spec, tmp_path)
    monkeypatch.setattr(execution, "inspect_target", lambda target: None)

    result = _capture(spec, "My Plan", tmp_path)

    assert (result.applicable, result.reason) == (False, "path_occupied")
    assert result.event is None
    assert path.read_bytes() == b"# mine\n\nprecious\n"
    assert _log(tmp_path) == b""


# ---- Processing's Create path -------------------------------------------------------


@SPECS
def test_processing_refuses_an_entry_whose_slug_is_taken_and_keeps_the_entry(spec, tmp_path):
    first = _capture(spec, "Foo Bar", tmp_path)
    log = _log(tmp_path)
    note = first.path.read_bytes()

    entry, result = _process(spec, "foo-bar\n", tmp_path)

    assert (result.applicable, result.reason) == (False, "same_file_name")
    assert result.operation is None and result.event is None
    assert entry.read_text(encoding="utf-8") == "foo-bar\n", "the Inbox entry is kept"
    assert first.path.read_bytes() == note
    assert _log(tmp_path) == log


@SPECS
def test_processing_refuses_an_entry_that_would_overwrite_a_hand_made_file(spec, tmp_path):
    path = _hand_made(spec, tmp_path)

    entry, result = _process(spec, "My Plan\n", tmp_path)

    assert (result.applicable, result.reason) == (False, "path_occupied")
    assert entry.exists()
    assert path.read_bytes() == b"# mine\n\nprecious\n"
    assert _log(tmp_path) == b""


@SPECS
def test_if_the_check_misses_a_file_processings_write_still_refuses_and_keeps_the_entry(
    spec, tmp_path, monkeypatch
):
    """Simulates a file that appears between Processing's check and its write."""
    path = _hand_made(spec, tmp_path)
    monkeypatch.setattr(execution, "inspect_target", lambda target: None)

    entry, result = _process(spec, "My Plan\n", tmp_path)

    assert (result.applicable, result.reason) == (False, "path_occupied")
    assert result.event is None and result.operation is None
    assert entry.read_text(encoding="utf-8") == "My Plan\n", "the entry stays in the Inbox"
    assert path.read_bytes() == b"# mine\n\nprecious\n"
    assert _log(tmp_path) == b""


@SPECS
def test_processing_refuses_a_reserved_title_and_keeps_the_entry(spec, tmp_path):
    entry, result = _process(spec, "Index\n", tmp_path)

    assert (result.applicable, result.reason) == (False, "reserved_name")
    assert entry.exists()
    assert _snapshot(tmp_path).keys() == {"inbox/entry.md"}


@SPECS
def test_processing_of_an_existing_title_is_still_an_update_not_a_refusal(spec, tmp_path):
    first = _capture(spec, "Foo Bar", tmp_path)

    entry, result = _process(spec, "Foo Bar\n\nsome new notes\n", tmp_path)

    assert result.applicable is True and result.operation == "update"
    assert result.path == first.path
    assert not entry.exists()


@SPECS
def test_processing_a_free_title_still_creates_and_resolves_the_entry(spec, tmp_path):
    entry, result = _process(spec, "Foo Bar\n", tmp_path)

    assert result.applicable is True and result.operation == "create"
    assert result.path.exists() and not entry.exists()


# ---- inspect_target: what occupies a path -------------------------------------------


def test_a_free_path_inspects_as_nothing(tmp_path):
    assert inspect_target(tmp_path / "x.md") is None


def test_an_ohtli_note_inspects_as_a_note_with_its_title_and_id(tmp_path):
    """An Ohtli note carries `id` and `note_type` in its frontmatter; its title
    is the first `# ` heading of the body, as `read_note` reads it."""
    path = tmp_path / "x.md"
    path.write_text("---\nid: abc-123\nnote_type: project\n---\n\n# Some Title\n\nbody\n", encoding="utf-8")

    assert inspect_target(path) == {"kind": "note", "title": "Some Title", "id": "abc-123"}


@pytest.mark.parametrize(
    "content",
    [
        pytest.param(b"# just markdown\n", id="hand-made-no-frontmatter"),
        pytest.param(b"---\ntype: note\n---\n\nbody\n", id="frontmatter-without-identity"),
        pytest.param(b"---\nid: abc\n---\n\n# T\n", id="id-without-note-type"),
        pytest.param(b"---\nnote_type: project\n---\n\n# T\n", id="note-type-without-id"),
        pytest.param(b"---\n: [unbalanced\n---\n\n# T\n", id="frontmatter-that-is-not-yaml"),
        pytest.param(b"", id="empty"),
        pytest.param(b"\xff\xfe\x00 not utf-8 \x80\x81", id="not-utf-8"),
    ],
)
def test_anything_else_inspects_as_other_and_never_raises(tmp_path, content):
    path = tmp_path / "x.md"
    path.write_bytes(content)

    assert inspect_target(path) == {"kind": "other"}


def test_a_directory_inspects_as_other(tmp_path):
    (tmp_path / "x.md").mkdir()

    assert inspect_target(tmp_path / "x.md") == {"kind": "other"}


def test_a_dangling_symlink_inspects_as_other_not_as_free(tmp_path):
    _symlink(tmp_path / "x.md", tmp_path / "nowhere.md")

    assert inspect_target(tmp_path / "x.md") == {"kind": "other"}


def test_a_symlink_to_a_note_is_not_followed(tmp_path):
    real = tmp_path / "real.md"
    real.write_text("---\nid: abc\nnote_type: project\n---\n\n# T\n", encoding="utf-8")
    _symlink(tmp_path / "x.md", real)

    assert inspect_target(tmp_path / "x.md") == {"kind": "other"}
