"""Knowledge's Externalize must locate the note to enrich by TITLE, not by
the slug its title happens to map to — the same flaw Processing's Update had
(#156, `tests/test_execution_processing_update_location.py`).

The old code read `spec.file_path(title)` and rewrote whatever was there
BEFORE checking it had an Ohtli identity: a hand-made file got `## Understanding`
written into it, and only then raised `KeyError('id')` — a half-done write,
not a clean refusal.

A refused enrich touches nothing and emits no Event. `reason` is
`ambiguous_title` (more than one note of this type carries the title;
`candidates`) or `not_an_ohtli_note` (none does; `blocked_path` names the
offending file when one can be identified). `search_title` carries the title
for the message, in both cases.

Everything runs against `tmp_path`, passing both `base_dir` and `events_dir`.
"""

import os

import pytest

from ohtli.execution import execution
from ohtli.execution.execution import Actor, ExecutionRequest, KnowledgeRequest, execute_capture, execute_knowledge
from ohtli.execution.specs import AREA, PROJECT, RESOURCE
from ohtli.workflow import capture as capture_workflow

TARGETS = pytest.mark.parametrize("spec", [PROJECT, AREA, RESOURCE], ids=["project", "area", "resource"])


def _capture(spec, title, tmp_path):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path / "events",
    )


def _enrich(spec, title, tmp_path, understanding_title="Learned It", understanding="A useful fact.", provenance=("Source A",)):
    return execute_knowledge(
        KnowledgeRequest(
            title=title,
            understanding_title=understanding_title,
            understanding=understanding,
            provenance=provenance,
            actor=Actor.HUMAN,
        ),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path / "events",
    )


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
    return PROJECT if spec is not PROJECT else AREA


def _symlink(link, target):
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links are not available here")


# ---- the fix: locate by title, not by slug -------------------------------------------


@TARGETS
def test_a_renamed_note_is_enriched_at_its_real_path_with_its_own_id(spec, tmp_path):
    first = _capture(spec, "Subject", tmp_path)
    renamed = first.path.parent / "my-renamed-note.md"
    first.path.rename(renamed)

    result = _enrich(spec, "Subject", tmp_path)

    assert result.applicable is True
    assert result.path == renamed
    assert result.project.id == first.project.id
    assert "Learned It" in renamed.read_text(encoding="utf-8")


@TARGETS
def test_a_different_note_sitting_at_the_slug_path_is_never_touched(spec, tmp_path):
    subject = _capture(spec, "Subject", tmp_path)
    renamed = subject.path.parent / "my-renamed-note.md"
    subject.path.rename(renamed)
    decoy = _capture(spec, "subject", tmp_path)
    decoy_bytes = decoy.path.read_bytes()

    result = _enrich(spec, "Subject", tmp_path)

    assert result.applicable is True and result.path == renamed
    assert result.project.id == subject.project.id
    assert decoy.path.read_bytes() == decoy_bytes


# ---- the core regression: a hand-made file is refused, never half-written -----------


@TARGETS
def test_a_hand_made_file_at_the_slug_path_is_refused_not_half_written(spec, tmp_path):
    directory = tmp_path / spec.note_type
    directory.mkdir()
    path = directory / "subject.md"
    before = b"---\ntags: []\n---\n\n# Subject\n\nmy own words, untouched\n"
    path.write_bytes(before)

    result = _enrich(spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.blocked_path == path
    assert path.read_bytes() == before, "must never be rewritten before its identity is checked"
    assert _log(tmp_path) == b""


@TARGETS
def test_a_file_without_any_frontmatter_is_refused_cleanly_not_a_crash(spec, tmp_path):
    directory = tmp_path / spec.note_type
    directory.mkdir()
    path = directory / "subject.md"
    before = b"# Subject\n\njust markdown, no frontmatter at all\n"
    path.write_bytes(before)

    result = _enrich(spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert path.read_bytes() == before
    assert _log(tmp_path) == b""


# ---- refusing when the title cannot be resolved to exactly one note -----------------


@TARGETS
def test_two_notes_with_the_same_title_refuse_as_ambiguous_and_keep_both(spec, tmp_path):
    directory = tmp_path / spec.note_type
    directory.mkdir()
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text(_hand_text(spec, "Subject", tmp_path, "a"), encoding="utf-8")
    b.write_text(_hand_text(spec, "Subject", tmp_path, "b"), encoding="utf-8")
    before = {a: a.read_bytes(), b: b.read_bytes()}

    result = _enrich(spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "ambiguous_title")
    assert set(result.candidates) == {a, b}
    assert a.read_bytes() == before[a] and b.read_bytes() == before[b]
    assert _log(tmp_path) == b""


@TARGETS
def test_a_note_of_a_different_type_holding_the_title_is_refused_and_untouched(spec, tmp_path):
    other = _different_spec(spec)
    directory = tmp_path / spec.note_type
    directory.mkdir()
    misfiled = directory / "misfiled.md"
    misfiled.write_text(_hand_text(other, "Subject", tmp_path, "misfiled"), encoding="utf-8")
    before = misfiled.read_bytes()

    result = _enrich(spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.blocked_path == misfiled
    assert misfiled.read_bytes() == before


@TARGETS
def test_a_symlink_that_only_reaches_the_title_from_outside_is_refused_and_the_outside_file_untouched(spec, tmp_path):
    outside_dir = tmp_path / "outside"
    outside = _capture(spec, "Subject", outside_dir)
    before = outside.path.read_bytes()
    directory = tmp_path / spec.note_type
    directory.mkdir()
    link = directory / "linked.md"
    _symlink(link, outside.path)

    result = _enrich(spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.blocked_path == link
    assert outside.path.read_bytes() == before
    assert _log(tmp_path) == b""


# ---- the race-free revalidation right before the write -------------------------------


@TARGETS
def test_if_the_note_changes_between_locating_and_writing_the_enrich_is_refused(spec, tmp_path, monkeypatch):
    first = _capture(spec, "Subject", tmp_path)
    before = first.path.read_bytes()
    log_before = _log(tmp_path)
    monkeypatch.setattr(execution, "inspect_target", lambda path: None)

    result = _enrich(spec, "Subject", tmp_path)

    assert (result.applicable, result.reason) == (False, "not_an_ohtli_note")
    assert result.event is None
    assert first.path.read_bytes() == before
    assert _log(tmp_path) == log_before, "the refusal adds no Event"


# ---- understanding/provenance is still checked, and checked first -------------------


@TARGETS
def test_blank_understanding_is_still_refused_without_a_reason(spec, tmp_path):
    subject = _capture(spec, "Subject", tmp_path)
    before = subject.path.read_bytes()

    result = _enrich(spec, "Subject", tmp_path, understanding="   ")

    assert result.applicable is False and result.reason is None
    assert subject.path.read_bytes() == before


@TARGETS
def test_blank_understanding_is_refused_even_over_a_hand_made_file(spec, tmp_path):
    """The understanding/provenance check runs BEFORE any filesystem lookup,
    so a bad request is refused the same way regardless of what (if anything)
    sits at the slug."""
    directory = tmp_path / spec.note_type
    directory.mkdir()
    path = directory / "subject.md"
    before = b"---\ntags: []\n---\n\n# Subject\n\nmine\n"
    path.write_bytes(before)

    result = _enrich(spec, "Subject", tmp_path, understanding="")

    assert result.applicable is False and result.reason is None
    assert path.read_bytes() == before


# ---- an ordinary enrich, with nothing wrong, is unaffected ---------------------------


@TARGETS
def test_an_ordinary_enrich_at_the_expected_path_still_works(spec, tmp_path):
    subject = _capture(spec, "Subject", tmp_path)

    result = _enrich(spec, "Subject", tmp_path)

    assert result.applicable is True and result.reason is None
    assert result.path == subject.path
    assert result.event is not None
    assert "Learned It" in subject.path.read_text(encoding="utf-8")
