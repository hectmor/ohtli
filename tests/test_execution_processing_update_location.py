"""Processing's Update must locate the note by its TITLE, not by the slug its
title happens to map to.

`is_update` decides Update vs Create by title. The old code then read and
rewrote the note at `spec.file_path(title)` — the slug path — which is a
different question. A note renamed since it was captured no longer lives
there (`FileNotFoundError`), or worse, a DIFFERENT Ohtli note can already sit
at that slug (two titles, one file name): the wrong note got rewritten and an
Update event was logged under the wrong id.

A refused Update touches nothing, emits no Event, and keeps the Inbox entry.
`reason` is `ambiguous_title` (more than one Ohtli note of this type carries
the title; every one of them is in `candidates`) or `not_an_ohtli_note`
(nothing of the right type does; `blocked_path` names what does, when one
readable file can be identified).

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
from ohtli.execution.specs import ALL_SPECS, AREA, PROJECT
from ohtli.workflow import capture as capture_workflow

SPECS = pytest.mark.parametrize("spec", ALL_SPECS, ids=[s.note_type for s in ALL_SPECS])


def _capture(spec, title, tmp_path):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path / "events",
    )


def _entry(tmp_path, text, name="entry.md"):
    inbox = tmp_path / "inbox"
    inbox.mkdir(exist_ok=True)
    path = inbox / name
    path.write_text(text, encoding="utf-8")
    return path


def _process(spec, entry_path, tmp_path):
    return execute_processing(
        ProcessingRequest(entry_path=entry_path, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path / "events",
    )


def _log(tmp_path):
    log = tmp_path / "events" / "events.jsonl"
    return log.read_bytes() if log.exists() else b""


def _hand_text(spec, title, tmp_path, tag):
    """The rendered text of a real, valid note titled `title`, of `spec`'s
    type and with its own id — without placing it anywhere final. Reuses the
    real rendering (via a throwaway directory) instead of hand-writing YAML."""
    domain_object = capture_workflow.transform(title, spec.domain_type)
    representation = spec.to_representation(domain_object)
    scratch = tmp_path / "scratch" / tag
    path = spec.write(representation, base_dir=scratch)
    return path.read_text(encoding="utf-8")


def _different_spec(spec):
    return PROJECT if spec is not PROJECT else AREA


# ---- the fix: locate by title, not by slug -------------------------------------------


@SPECS
def test_a_renamed_note_is_updated_at_its_real_path_with_its_own_id(spec, tmp_path):
    first = _capture(spec, "Foo Bar", tmp_path)
    renamed = first.path.parent / "my-renamed-note.md"
    first.path.rename(renamed)
    _entry(tmp_path, "Foo Bar\n\nsome new notes\n")

    result = _process(spec, tmp_path / "inbox" / "entry.md", tmp_path)

    assert result.applicable is True and result.operation == "update"
    assert result.path == renamed
    assert result.project.id == first.project.id
    assert "some new notes" in renamed.read_text(encoding="utf-8")


@SPECS
def test_a_different_note_sitting_at_the_slug_path_is_never_touched(spec, tmp_path):
    """The flagship regression: "Foo Bar" was renamed away from foo-bar.md, and
    a DIFFERENT note "foo-bar" (different case, a different title) now lives
    there. Only the real "Foo Bar" note may be rewritten."""
    foo_bar = _capture(spec, "Foo Bar", tmp_path)
    renamed = foo_bar.path.parent / "my-renamed-note.md"
    foo_bar.path.rename(renamed)
    decoy = _capture(spec, "foo-bar", tmp_path)
    decoy_bytes = decoy.path.read_bytes()
    _entry(tmp_path, "Foo Bar\n\nsome new notes\n")

    result = _process(spec, tmp_path / "inbox" / "entry.md", tmp_path)

    assert result.applicable is True and result.path == renamed
    assert result.project.id == foo_bar.project.id
    assert decoy.path.read_bytes() == decoy_bytes, "the decoy note must stay byte-identical"


@SPECS
def test_a_blank_remainder_on_a_renamed_note_resolves_without_writing_or_crashing(spec, tmp_path):
    first = _capture(spec, "Foo Bar", tmp_path)
    renamed = first.path.parent / "my-renamed-note.md"
    first.path.rename(renamed)
    before = renamed.read_bytes()
    entry = _entry(tmp_path, "Foo Bar\n")

    result = _process(spec, entry, tmp_path)

    assert result.applicable is True and result.operation == "update"
    assert result.event is None
    assert renamed.read_bytes() == before
    assert not entry.exists()


# ---- refusing when the title cannot be resolved to exactly one note -----------------


@SPECS
def test_two_notes_with_the_same_title_refuse_as_ambiguous_and_keep_the_entry(spec, tmp_path):
    directory = tmp_path / spec.note_type
    directory.mkdir()
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text(_hand_text(spec, "Foo Bar", tmp_path, "a"), encoding="utf-8")
    b.write_text(_hand_text(spec, "Foo Bar", tmp_path, "b"), encoding="utf-8")
    before = {a: a.read_bytes(), b: b.read_bytes()}
    entry = _entry(tmp_path, "Foo Bar\n\nsome new notes\n")

    result = _process(spec, entry, tmp_path)

    assert (result.applicable, result.reason) == (False, "ambiguous_title")
    assert result.event is None and result.operation is None
    assert set(result.candidates) == {a, b}
    assert a.read_bytes() == before[a] and b.read_bytes() == before[b]
    assert entry.exists()
    assert _log(tmp_path) == b""


@SPECS
def test_a_title_held_only_by_a_file_without_ohtli_identity_is_refused_and_untouched(spec, tmp_path):
    directory = tmp_path / spec.note_type
    directory.mkdir()
    path = directory / "hand-made.md"
    path.write_text("---\ntags: []\n---\n\n# Foo Bar\n\nsomething I wrote\n", encoding="utf-8")
    before = path.read_bytes()
    entry = _entry(tmp_path, "Foo Bar\n\nsome new notes\n")

    result = _process(spec, entry, tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.blocked_path == path
    assert path.read_bytes() == before
    assert entry.exists()
    assert _log(tmp_path) == b""


@SPECS
def test_a_note_of_a_different_type_holding_the_title_is_refused_and_untouched(spec, tmp_path):
    other = _different_spec(spec)
    directory = tmp_path / spec.note_type
    directory.mkdir()
    misfiled = directory / "misfiled.md"
    misfiled.write_text(_hand_text(other, "Foo Bar", tmp_path, "misfiled"), encoding="utf-8")
    before = misfiled.read_bytes()
    entry = _entry(tmp_path, "Foo Bar\n\nsome new notes\n")

    result = _process(spec, entry, tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.blocked_path == misfiled
    assert misfiled.read_bytes() == before
    assert entry.exists()


@SPECS
def test_a_misfiled_note_of_another_type_does_not_cause_a_false_ambiguity(spec, tmp_path):
    """Only same-type notes are candidates: a note of a DIFFERENT type that
    happens to share the title is noise, not a second candidate — the real
    note is still found and updated on its own, with no ambiguity."""
    real = _capture(spec, "Foo Bar", tmp_path)
    other = _different_spec(spec)
    misfiled_text = _hand_text(other, "Foo Bar", tmp_path, "misfiled-noise")
    misfiled = real.path.parent / "misfiled.md"
    misfiled.write_text(misfiled_text, encoding="utf-8")
    entry = _entry(tmp_path, "Foo Bar\n\nsome new notes\n")

    result = _process(spec, entry, tmp_path)

    assert result.applicable is True and result.reason is None
    assert result.path == real.path
    assert "some new notes" in real.path.read_text(encoding="utf-8")
    assert misfiled.read_text(encoding="utf-8") == misfiled_text


def _symlink(link, target):
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links are not available here")


@SPECS
def test_a_dangling_symlink_among_the_candidates_does_not_crash_the_search(spec, tmp_path):
    """`find_any_note_titled` (the diagnostic search for the refusal message)
    must survive whatever else sits in the folder, same as `_list_existing_titles`
    already does (Phase 38)."""
    directory = tmp_path / spec.note_type
    directory.mkdir()
    _symlink(directory / "ghost.md", tmp_path / "nowhere.md")
    real = directory / "hand-made.md"
    real.write_text("---\ntags: []\n---\n\n# Foo Bar\n\nmine\n", encoding="utf-8")
    entry = _entry(tmp_path, "Foo Bar\n\nsome new notes\n")

    result = _process(spec, entry, tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.blocked_path == real


@SPECS
def test_a_symlink_that_only_reaches_the_title_from_outside_is_refused_and_the_outside_file_untouched(
    spec, tmp_path
):
    outside_dir = tmp_path / "outside"
    outside = _capture(spec, "Foo Bar", outside_dir)
    before = outside.path.read_bytes()
    directory = tmp_path / spec.note_type
    directory.mkdir()
    link = directory / "linked.md"
    _symlink(link, outside.path)
    entry = _entry(tmp_path, "Foo Bar\n\nsome new notes\n")

    result = _process(spec, entry, tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.blocked_path == link
    assert outside.path.read_bytes() == before
    assert entry.exists()
    assert _log(tmp_path) == b""


# ---- the race-free revalidation right before the write -------------------------------


@SPECS
def test_if_the_note_changes_between_locating_and_writing_the_update_is_refused(spec, tmp_path, monkeypatch):
    """Simulates the file changing between locating it (via `find_notes_titled`,
    unaffected by this patch: it uses its own module-level reference) and the
    write. `execution.inspect_target` is the revalidation step alone."""
    first = _capture(spec, "Foo Bar", tmp_path)
    before = first.path.read_bytes()
    log_before = _log(tmp_path)
    entry = _entry(tmp_path, "Foo Bar\n\nsome new notes\n")
    monkeypatch.setattr(execution, "inspect_target", lambda path: None)

    result = _process(spec, entry, tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.event is None
    assert first.path.read_bytes() == before
    assert entry.exists()
    assert _log(tmp_path) == log_before, "the refusal adds no Event"


# ---- an ordinary Update, with nothing wrong, is unaffected ---------------------------


@SPECS
def test_an_ordinary_update_at_the_expected_path_still_works(spec, tmp_path):
    first = _capture(spec, "Foo Bar", tmp_path)
    entry = _entry(tmp_path, "Foo Bar\n\nsome new notes\n")

    result = _process(spec, entry, tmp_path)

    assert result.applicable is True and result.operation == "update"
    assert result.path == first.path
    assert result.event is not None
    assert not entry.exists()
    assert "some new notes" in first.path.read_text(encoding="utf-8")
