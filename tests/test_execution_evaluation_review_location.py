"""Evaluate and Review must locate their note by TITLE, not by the slug the
title happens to map to -- the same flaw Processing's Update (#156),
Knowledge's Externalize (#160), Archive/Reactivate (#161) and Relate/Unrelate
(#162) had.

Unlike those three (which are read-only reads, per the issue text), Evaluate
and Review each emit a permanent Event naming whatever note they located.
The old code read `spec.file_path(title)` directly: a note renamed since
capture is refused as if it did not exist; a hand-made file at that slug
crashes trying to build a Domain Object from it; a different Ohtli note
already sitting at that slug gets silently evaluated/reviewed instead -- the
Event records the DECOY's id, permanently, and Review's `observe` then
filters the Event log by that wrong id, silently ignoring the real note's
own history.

A refused Evaluate/Review touches nothing and emits no Event. `reason` is
`ambiguous_title` (more than one note of this type carries the title;
`candidates`) or `not_an_ohtli_note` (a loose match carries the title but
isn't a valid Ohtli note of this type; `blocked_path`) or `missing` (nothing
at all carries the title). `search_title` carries the title, in every case.

Everything runs against `tmp_path`, passing both `base_dir` and `events_dir`.
"""

import pytest

from ohtli.execution import execution
from ohtli.execution.execution import (
    Actor,
    EvaluationRequest,
    ExecutionRequest,
    ReviewRequest,
    execute_capture,
    execute_evaluation,
    execute_review,
)
from ohtli.execution.specs import AREA, JOURNAL_ENTRY, MEETING, PROJECT, REFERENCE, RESOURCE
from ohtli.workflow import capture as capture_workflow
from ohtli.workflow.evaluation import OperationalResult
from ohtli.workflow.review import ReviewConclusion

EVALUATE_SPECS = pytest.mark.parametrize("spec", [PROJECT, AREA], ids=["project", "area"])
_REVIEW_ALL = [PROJECT, AREA, RESOURCE, REFERENCE, MEETING, JOURNAL_ENTRY]
REVIEW_SPECS = pytest.mark.parametrize("spec", _REVIEW_ALL, ids=[s.note_type for s in _REVIEW_ALL])
OPS = pytest.mark.parametrize("op", ["evaluate", "review"])


def _capture(spec, title, tmp_path):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path / "events",
    )


_DEFAULT_RESULT = {PROJECT: OperationalResult.PROGRESS, AREA: OperationalResult.MAINTENANCE}


def _evaluate(spec, title, tmp_path, result=None):
    return execute_evaluation(
        EvaluationRequest(title=title, result=result or _DEFAULT_RESULT[spec], actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path / "events",
    )


def _review(spec, title, tmp_path):
    return execute_review(
        ReviewRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path / "events",
    )


def _do(op, spec, title, tmp_path):
    return _evaluate(spec, title, tmp_path) if op == "evaluate" else _review(spec, title, tmp_path)


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


def _symlink(link, target):
    import os

    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links are not available here")


# ---- the fix: locate by title, not by slug -------------------------------------------


@EVALUATE_SPECS
@OPS
def test_a_renamed_note_is_evaluated_or_reviewed_at_its_real_path_with_its_own_id(spec, op, tmp_path):
    seeded = _capture(spec, "Subject", tmp_path)
    renamed = seeded.path.parent / "my-renamed-note.md"
    seeded.path.rename(renamed)

    result = _do(op, spec, "Subject", tmp_path)

    assert result.applicable is True
    assert result.path == renamed
    assert result.event is not None
    assert result.event.object_id == seeded.project.id


@EVALUATE_SPECS
@OPS
def test_a_decoy_at_the_slug_path_is_never_evaluated_or_reviewed_instead(spec, op, tmp_path):
    """The core regression: before the fix, the decoy's id was recorded in
    a permanent Event instead of the renamed note's."""
    seeded = _capture(spec, "Subject", tmp_path)
    renamed = seeded.path.parent / "my-renamed-note.md"
    seeded.path.rename(renamed)
    decoy = _capture(spec, "subject", tmp_path)
    decoy_bytes = decoy.path.read_bytes()

    result = _do(op, spec, "Subject", tmp_path)

    assert result.applicable is True and result.path == renamed
    assert result.event.object_id == seeded.project.id
    assert result.event.object_id != decoy.project.id
    assert decoy.path.read_bytes() == decoy_bytes


def test_review_ignores_a_decoys_own_event_history(tmp_path):
    """Before the fix, Review of a renamed note would locate the decoy at
    its old slug and assess the DECOY's history. After the fix, the decoy's
    own Degradation Event (recorded against its own id, correctly) must not
    influence the Review of the real, renamed note, which has no evaluation
    Events of its own."""
    seeded = _capture(PROJECT, "Subject", tmp_path)
    renamed = seeded.path.parent / "my-renamed-note.md"
    seeded.path.rename(renamed)
    decoy = _capture(PROJECT, "subject", tmp_path)
    degraded = _evaluate(PROJECT, "subject", tmp_path, OperationalResult.DEGRADATION)
    assert degraded.applicable is True and degraded.event.object_id == decoy.project.id

    result = _review(PROJECT, "Subject", tmp_path)

    assert result.applicable is True
    assert result.project.id == seeded.project.id
    assert result.assessment.conclusion == ReviewConclusion.INSUFFICIENT_BASIS


# ---- the core regression: a hand-made file is refused, never crashes ----------------


@EVALUATE_SPECS
@OPS
def test_a_hand_made_file_at_the_slug_path_is_refused_not_a_crash(spec, op, tmp_path):
    directory = tmp_path / spec.note_type
    directory.mkdir()
    path = directory / "subject.md"
    before = b"---\ncontext: operational\n---\n\n# Subject\n\nmy own words, untouched\n"
    path.write_bytes(before)

    result = _do(op, spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.blocked_path == path
    assert path.read_bytes() == before
    assert _log(tmp_path) == b""


@EVALUATE_SPECS
@OPS
def test_a_file_without_any_frontmatter_is_refused_cleanly_not_a_crash(spec, op, tmp_path):
    directory = tmp_path / spec.note_type
    directory.mkdir()
    path = directory / "subject.md"
    before = b"# Subject\n\njust markdown, no frontmatter at all\n"
    path.write_bytes(before)

    result = _do(op, spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "missing")
    assert path.read_bytes() == before
    assert _log(tmp_path) == b""


# ---- refusing when the title cannot be resolved to exactly one note -----------------


@EVALUATE_SPECS
@OPS
def test_two_notes_with_the_same_title_refuse_as_ambiguous_and_keep_both(spec, op, tmp_path):
    directory = tmp_path / spec.note_type
    directory.mkdir()
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text(_hand_text(spec, "Subject", tmp_path, "a"), encoding="utf-8")
    b.write_text(_hand_text(spec, "Subject", tmp_path, "b"), encoding="utf-8")
    before = {a: a.read_bytes(), b: b.read_bytes()}

    result = _do(op, spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "ambiguous_title")
    assert set(result.candidates) == {a, b}
    assert a.read_bytes() == before[a] and b.read_bytes() == before[b]
    assert _log(tmp_path) == b""


@OPS
def test_a_note_of_a_different_type_holding_the_title_is_refused_and_untouched(op, tmp_path):
    directory = tmp_path / PROJECT.note_type
    directory.mkdir()
    misfiled = directory / "misfiled.md"
    misfiled.write_text(_hand_text(AREA, "Subject", tmp_path, "misfiled"), encoding="utf-8")
    before = misfiled.read_bytes()

    result = _do(op, PROJECT, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.blocked_path == misfiled
    assert misfiled.read_bytes() == before


@OPS
def test_a_symlink_that_only_reaches_the_title_from_outside_is_refused(op, tmp_path):
    outside_dir = tmp_path / "outside"
    outside = _capture(PROJECT, "Subject", outside_dir)
    before = outside.path.read_bytes()
    directory = tmp_path / PROJECT.note_type
    directory.mkdir()
    link = directory / "linked.md"
    _symlink(link, outside.path)

    result = _do(op, PROJECT, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.blocked_path == link
    assert outside.path.read_bytes() == before
    assert _log(tmp_path) == b""


# ---- the race-free revalidation right before the Event is emitted -------------------


@EVALUATE_SPECS
@OPS
def test_if_the_note_changes_between_locating_and_emitting_it_is_refused(spec, op, tmp_path, monkeypatch):
    seeded = _capture(spec, "Subject", tmp_path)
    before = seeded.path.read_bytes()
    log_before = _log(tmp_path)
    monkeypatch.setattr(execution, "inspect_target", lambda path: None)

    result = _do(op, spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.event is None
    assert seeded.path.read_bytes() == before
    assert _log(tmp_path) == log_before, "the refusal adds no Event"


# ---- ordinary behaviour, with nothing wrong, is unaffected ---------------------------


@REVIEW_SPECS
def test_an_ordinary_review_at_the_expected_path_still_works(spec, tmp_path):
    seeded = _capture(spec, "Subject", tmp_path)

    result = _review(spec, "Subject", tmp_path)

    assert result.applicable is True and result.reason is None
    assert result.path == seeded.path
    assert result.event is not None


@EVALUATE_SPECS
def test_an_ordinary_evaluate_at_the_expected_path_still_works(spec, tmp_path):
    seeded = _capture(spec, "Subject", tmp_path)

    result = _evaluate(spec, "Subject", tmp_path)

    assert result.applicable is True and result.reason is None
    assert result.path == seeded.path
    assert result.event is not None


def test_a_renamed_note_with_a_disallowed_result_is_refused_with_no_reason(tmp_path):
    """The workflow's own refusal (a result this type's `allowed_results`
    excludes) stays a plain `reason=None` refusal -- only the location
    refusals (#163) carry `reason`."""
    seeded = _capture(AREA, "Subject", tmp_path)
    renamed = seeded.path.parent / "my-renamed-note.md"
    seeded.path.rename(renamed)

    result = _evaluate(AREA, "Subject", tmp_path, OperationalResult.OUTCOME_REACHED)

    assert result.applicable is False
    assert result.reason is None
    assert result.event is None
