"""Archive and Reactivate must locate the note to transition by TITLE, not by
the slug its title happens to map to -- the same flaw Processing's Update
(#156) and Knowledge's Externalize (#160) had.

The old code read `spec.file_path(title)` directly: a note renamed since it
was captured is reported `missing`; a hand-made file at that slug gets
written into (`rewrite_note`) BEFORE its identity is checked, then crashes
with `KeyError('id')` -- a half-done write, not a clean refusal; a different
Ohtli note already sitting at that slug gets silently transitioned instead,
bypassing Operational Integrity if it has dependents of its own.

A refused Archive/Reactivate touches nothing and emits no Event. `reason` is
`ambiguous_title` (more than one note of this type carries the title;
`candidates`) or `not_an_ohtli_note` (a loose match carries the title but
isn't a valid Ohtli note of this type; `blocked_path`) or `missing` (nothing
at all carries the title -- including a file with no frontmatter, which
`find_any_note_titled` never matches). `search_title` carries the title for
the message, in every case.

Everything runs against `tmp_path`, passing both `base_dir` and `events_dir`.
"""

import os

import pytest

from ohtli.execution import execution
from ohtli.execution.execution import (
    ArchiveRequest,
    Actor,
    ExecutionRequest,
    execute_archive,
    execute_capture,
    execute_reactivate,
)
from ohtli.execution.specs import ALL_SPECS
from ohtli.representation.context import HISTORICAL, OPERATIONAL
from ohtli.workflow import capture as capture_workflow

SPECS = pytest.mark.parametrize("spec", ALL_SPECS, ids=[s.note_type for s in ALL_SPECS])
OPS = pytest.mark.parametrize("op", ["archive", "reactivate"])

_EXECUTE = {"archive": execute_archive, "reactivate": execute_reactivate}
_EXPECTED_CONTEXT = {"archive": OPERATIONAL, "reactivate": HISTORICAL}


def _capture(spec, title, tmp_path):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path / "events",
    )


def _run(op, spec, title, tmp_path):
    return _EXECUTE[op](
        ArchiveRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path / "events",
    )


def _seed(op, spec, title, tmp_path):
    """Capture `title`, then -- for Reactivate -- archive it, so the note
    starts in whichever context the operation under test requires."""
    first = _capture(spec, title, tmp_path)
    if op == "reactivate":
        archived = _run("archive", spec, title, tmp_path)
        assert archived.applicable is True
        return archived
    return first


def _log(tmp_path):
    log = tmp_path / "events" / "events.jsonl"
    return log.read_bytes() if log.exists() else b""


def _hand_text(spec, title, tmp_path, tag):
    """The rendered text of a real, valid note titled `title`, of `spec`'s
    type and with its own id, without placing it anywhere final."""
    domain_object = capture_workflow.transform(title, spec.domain_type)
    representation = spec.to_representation(domain_object)
    scratch = tmp_path / "scratch" / tag
    path = spec.write(representation, base_dir=scratch)
    return path.read_text(encoding="utf-8")


def _different_spec(spec):
    others = [s for s in ALL_SPECS if s is not spec]
    return others[0]


def _symlink(link, target):
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links are not available here")


# ---- the fix: locate by title, not by slug -------------------------------------------


@SPECS
@OPS
def test_a_renamed_note_is_transitioned_at_its_real_path_with_its_own_id(spec, op, tmp_path):
    seeded = _seed(op, spec, "Subject", tmp_path)
    renamed = seeded.path.parent / "my-renamed-note.md"
    seeded.path.rename(renamed)

    result = _run(op, spec, "Subject", tmp_path)

    assert result.applicable is True
    assert result.path == renamed
    assert result.project.id == seeded.project.id


@SPECS
@OPS
def test_a_different_note_sitting_at_the_slug_path_is_never_touched(spec, op, tmp_path):
    seeded = _seed(op, spec, "Subject", tmp_path)
    renamed = seeded.path.parent / "my-renamed-note.md"
    seeded.path.rename(renamed)
    decoy = _capture(spec, "subject", tmp_path)
    decoy_bytes = decoy.path.read_bytes()

    result = _run(op, spec, "Subject", tmp_path)

    assert result.applicable is True and result.path == renamed
    assert result.project.id == seeded.project.id
    assert decoy.path.read_bytes() == decoy_bytes


# ---- the core regression: a hand-made file is refused, never half-written -----------


@SPECS
@OPS
def test_a_hand_made_file_at_the_slug_path_is_refused_not_half_written(spec, op, tmp_path):
    directory = tmp_path / spec.note_type
    directory.mkdir()
    path = directory / "subject.md"
    expected_context = _EXPECTED_CONTEXT[op]
    before = f"---\ncontext: {expected_context}\n---\n\n# Subject\n\nmy own words, untouched\n".encode()
    path.write_bytes(before)

    result = _run(op, spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.blocked_path == path
    assert path.read_bytes() == before, "must never be rewritten before its identity is checked"
    assert _log(tmp_path) == b""


@SPECS
@OPS
def test_a_file_without_any_frontmatter_is_refused_cleanly_not_a_crash(spec, op, tmp_path):
    directory = tmp_path / spec.note_type
    directory.mkdir()
    path = directory / "subject.md"
    before = b"# Subject\n\njust markdown, no frontmatter at all\n"
    path.write_bytes(before)

    result = _run(op, spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "missing")
    assert path.read_bytes() == before
    assert _log(tmp_path) == b""


# ---- refusing when the title cannot be resolved to exactly one note -----------------


@SPECS
@OPS
def test_two_notes_with_the_same_title_refuse_as_ambiguous_and_keep_both(spec, op, tmp_path):
    directory = tmp_path / spec.note_type
    directory.mkdir()
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text(_hand_text(spec, "Subject", tmp_path, "a"), encoding="utf-8")
    b.write_text(_hand_text(spec, "Subject", tmp_path, "b"), encoding="utf-8")
    before = {a: a.read_bytes(), b: b.read_bytes()}

    result = _run(op, spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "ambiguous_title")
    assert set(result.candidates) == {a, b}
    assert a.read_bytes() == before[a] and b.read_bytes() == before[b]
    assert _log(tmp_path) == b""


@SPECS
def test_a_note_of_a_different_type_holding_the_title_is_refused_and_untouched(spec, tmp_path):
    other = _different_spec(spec)
    directory = tmp_path / spec.note_type
    directory.mkdir()
    misfiled = directory / "misfiled.md"
    misfiled.write_text(_hand_text(other, "Subject", tmp_path, "misfiled"), encoding="utf-8")
    before = misfiled.read_bytes()

    result = _run("archive", spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.blocked_path == misfiled
    assert misfiled.read_bytes() == before


@SPECS
def test_a_symlink_that_only_reaches_the_title_from_outside_is_refused_and_the_outside_file_untouched(spec, tmp_path):
    outside_dir = tmp_path / "outside"
    outside = _capture(spec, "Subject", outside_dir)
    before = outside.path.read_bytes()
    directory = tmp_path / spec.note_type
    directory.mkdir()
    link = directory / "linked.md"
    _symlink(link, outside.path)

    result = _run("archive", spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.blocked_path == link
    assert outside.path.read_bytes() == before
    assert _log(tmp_path) == b""


# ---- the race-free revalidation right before the write -------------------------------


@SPECS
@OPS
def test_if_the_note_changes_between_locating_and_transitioning_it_is_refused(spec, op, tmp_path, monkeypatch):
    seeded = _seed(op, spec, "Subject", tmp_path)
    before = seeded.path.read_bytes()
    log_before = _log(tmp_path)
    monkeypatch.setattr(execution, "inspect_target", lambda path: None)

    result = _run(op, spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.event is None
    assert seeded.path.read_bytes() == before
    assert _log(tmp_path) == log_before, "the refusal adds no Event"


# ---- an ordinary transition, with nothing wrong, is unaffected ----------------------


@SPECS
@OPS
def test_an_ordinary_transition_at_the_expected_path_still_works(spec, op, tmp_path):
    seeded = _seed(op, spec, "Subject", tmp_path)

    result = _run(op, spec, "Subject", tmp_path)

    assert result.applicable is True and result.reason is None
    assert result.path == seeded.path
    assert result.event is not None
