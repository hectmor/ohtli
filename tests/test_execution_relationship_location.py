"""Relate and Unrelate must locate both ends -- the source, and the target
(named or not) -- by TITLE, not by the slug the title happens to map to --
the same flaw Processing's Update (#156), Knowledge's Externalize (#160) and
Archive/Reactivate (#161) had.

The old code read `spec.file_path(title)` directly for every end. A note
renamed since it was captured is reported missing for Relate, or silently
skipped for Unrelate's named target; a hand-made file at that slug gets
written into (`rewrite_note`) BEFORE its identity is checked, then crashes
with `KeyError('id')`; a different Ohtli note already sitting at that slug
is silently used instead -- for Unrelate, the wrong relationship entry gets
removed (or the real, renamed one is refused as "not linked"); for Relate's
target, the DECOY's `id` gets stored in the source, a lasting wrong link.

A refused Relate/Unrelate touches nothing and emits no Event. `reason` is
`ambiguous_title` (more than one note of this type carries the title;
`candidates`) or `not_an_ohtli_note` (a loose match carries the title but
isn't a valid Ohtli note of this type; `blocked_path`) or `missing` (nothing
at all carries the title). `search_title` carries the title, and `end`
(`"source"` or `"target"`) says which note of the two it was, for every case.

Everything runs against `tmp_path`, passing `base_dir`/`target_base_dir` and
`events_dir`.
"""

import pytest

from ohtli.execution import execution
from ohtli.execution.execution import (
    Actor,
    ExecutionRequest,
    RelateRequest,
    UnrelateRequest,
    execute_capture,
    execute_relate,
    execute_unrelate,
)
from ohtli.execution.specs import ALL_SPECS
from ohtli.vault_io.events import read_events
from ohtli.workflow import capture as capture_workflow
from ohtli.workflow import processing

_SPEC_BY_NAME = {spec.domain_type.__name__: spec for spec in ALL_SPECS}

_ALL_PAIRS = [(d.source_type, d.target_type) for d in processing.CANONICAL_RELATIONSHIPS]
_ALL_PAIR_IDS = [f"{s}-{t}" for s, t in _ALL_PAIRS]
ALL_PAIRS = pytest.mark.parametrize("source_name,target_name", _ALL_PAIRS, ids=_ALL_PAIR_IDS)

_REPRESENTATIVE = [("Project", "Area"), ("Project", "Resource")]
REPRESENTATIVE = pytest.mark.parametrize("source_name,target_name", _REPRESENTATIVE, ids=["bounded", "unbounded"])

OPS = pytest.mark.parametrize("op", ["link", "unlink"])

BOUNDED = ("Project", "Area")
UNBOUNDED = ("Project", "Resource")


def _relationship_type(source_name: str, target_name: str) -> str:
    return processing.relationship_for_pair(source_name, target_name).relationship_type


def _capture(spec, title, tmp_path):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path / "events",
    )


def _do(op, source_spec, source_title, target_spec, target_title, tmp_path, relationship_type):
    if op == "link":
        return execute_relate(
            RelateRequest(
                source_title=source_title,
                target_title=target_title,
                actor=Actor.HUMAN,
                relationship_type=relationship_type,
            ),
            source_spec=source_spec,
            target_spec=target_spec,
            base_dir=tmp_path / source_spec.note_type,
            target_base_dir=tmp_path / target_spec.note_type,
            events_dir=tmp_path / "events",
        )
    return execute_unrelate(
        UnrelateRequest(
            source_title=source_title,
            actor=Actor.HUMAN,
            relationship_type=relationship_type,
            target_title=target_title,
        ),
        spec=source_spec,
        target_spec=target_spec,
        base_dir=tmp_path / source_spec.note_type,
        target_base_dir=tmp_path / target_spec.note_type,
        events_dir=tmp_path / "events",
    )


def _seed(op, source_spec, source_title, target_spec, target_title, tmp_path, relationship_type):
    """Capture both ends, then -- for Unlink -- link them first, so the
    relationship exists for the operation under test to remove."""
    source = _capture(source_spec, source_title, tmp_path)
    target = _capture(target_spec, target_title, tmp_path)
    if op == "unlink":
        linked = _do("link", source_spec, source_title, target_spec, target_title, tmp_path, relationship_type)
        assert linked.applicable is True
    return source, target


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


# ---- the fix: both ends are located by title, not by slug ---------------------------


@ALL_PAIRS
@OPS
def test_a_renamed_source_is_still_located_and_transitioned_by_title(source_name, target_name, op, tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME[source_name], _SPEC_BY_NAME[target_name]
    relationship_type = _relationship_type(source_name, target_name)
    source, target = _seed(op, source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)
    renamed = source.path.parent / "renamed-source.md"
    source.path.rename(renamed)

    result = _do(op, source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert result.applicable is True
    assert result.path == renamed
    assert result.reason is None


@ALL_PAIRS
def test_relate_stores_the_renamed_targets_id_not_the_old_paths(source_name, target_name, tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME[source_name], _SPEC_BY_NAME[target_name]
    relationship_type = _relationship_type(source_name, target_name)
    source = _capture(source_spec, "Source", tmp_path)
    target = _capture(target_spec, "Target", tmp_path)
    renamed = target.path.parent / "renamed-target.md"
    target.path.rename(renamed)

    result = _do("link", source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert result.applicable is True
    from ohtli.vault_io.markdown import read_note

    (entry,) = [
        e
        for e in read_note(source.path)["properties"]["relationships"]
        if e.get("type") == relationship_type
    ]
    assert entry["target_id"] == target.project.id
    assert renamed.name.split(".")[0] in entry["target_link"]


@REPRESENTATIVE
@OPS
def test_a_decoy_at_the_source_slug_is_never_touched_instead_of_the_renamed_source(
    source_name, target_name, op, tmp_path
):
    source_spec, target_spec = _SPEC_BY_NAME[source_name], _SPEC_BY_NAME[target_name]
    relationship_type = _relationship_type(source_name, target_name)
    source, target = _seed(op, source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)
    renamed = source.path.parent / "renamed-source.md"
    source.path.rename(renamed)
    decoy = _capture(source_spec, "source", tmp_path)
    decoy_bytes = decoy.path.read_bytes()

    result = _do(op, source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert result.applicable is True
    assert result.path == renamed
    assert decoy.path.read_bytes() == decoy_bytes


@REPRESENTATIVE
def test_relate_with_a_decoy_at_the_target_slug_stores_the_real_targets_id(source_name, target_name, tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME[source_name], _SPEC_BY_NAME[target_name]
    relationship_type = _relationship_type(source_name, target_name)
    source = _capture(source_spec, "Source", tmp_path)
    target = _capture(target_spec, "Target", tmp_path)
    renamed = target.path.parent / "renamed-target.md"
    target.path.rename(renamed)
    decoy = _capture(target_spec, "target", tmp_path)
    decoy_bytes = decoy.path.read_bytes()

    result = _do("link", source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert result.applicable is True
    from ohtli.vault_io.markdown import read_note

    (entry,) = [
        e
        for e in read_note(source.path)["properties"]["relationships"]
        if e.get("type") == relationship_type
    ]
    assert entry["target_id"] == target.project.id
    assert decoy.path.read_bytes() == decoy_bytes


def test_unlink_with_a_decoy_at_the_target_slug_removes_only_the_real_targets_entry(tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME["Project"], _SPEC_BY_NAME["Resource"]
    relationship_type = _relationship_type("Project", "Resource")
    source = _capture(source_spec, "Source", tmp_path)
    target = _capture(target_spec, "Target", tmp_path)
    other = _capture(target_spec, "Other", tmp_path)
    assert _do("link", source_spec, "Source", target_spec, "Target", tmp_path, relationship_type).applicable
    assert _do("link", source_spec, "Source", target_spec, "Other", tmp_path, relationship_type).applicable
    renamed = target.path.parent / "renamed-target.md"
    target.path.rename(renamed)
    decoy = _capture(target_spec, "target", tmp_path)
    decoy_bytes = decoy.path.read_bytes()

    result = _do("unlink", source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert result.applicable is True
    from ohtli.vault_io.markdown import read_note

    remaining = [
        e["target_id"]
        for e in (read_note(source.path)["properties"].get("relationships") or [])
        if e.get("type") == relationship_type
    ]
    assert remaining == [other.project.id]
    assert decoy.path.read_bytes() == decoy_bytes


# ---- the core regression: a hand-made file is refused, never half-written -----------


@REPRESENTATIVE
@OPS
def test_a_hand_made_file_at_the_source_slug_is_refused_not_half_written(source_name, target_name, op, tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME[source_name], _SPEC_BY_NAME[target_name]
    relationship_type = _relationship_type(source_name, target_name)
    directory = tmp_path / source_spec.note_type
    directory.mkdir(parents=True)
    path = directory / "source.md"
    before = b"---\ncontext: operational\n---\n\n# Source\n\nmy own words, untouched\n"
    path.write_bytes(before)
    _capture(target_spec, "Target", tmp_path)
    log_before = _log(tmp_path)

    result = _do(op, source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert (result.applicable, result.reason, result.end) == (False, "not_an_ohtli_note", "source")
    assert result.blocked_path == path
    assert path.read_bytes() == before, "must never be rewritten before its identity is checked"
    assert _log(tmp_path) == log_before


@REPRESENTATIVE
@OPS
def test_a_hand_made_file_at_the_target_slug_is_refused_not_half_written(source_name, target_name, op, tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME[source_name], _SPEC_BY_NAME[target_name]
    relationship_type = _relationship_type(source_name, target_name)
    source = _capture(source_spec, "Source", tmp_path)
    before_source = source.path.read_bytes()
    directory = tmp_path / target_spec.note_type
    directory.mkdir(parents=True)
    path = directory / "target.md"
    before = b"---\ncontext: operational\n---\n\n# Target\n\nmy own words, untouched\n"
    path.write_bytes(before)
    log_before = _log(tmp_path)

    result = _do(op, source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert (result.applicable, result.reason, result.end) == (False, "not_an_ohtli_note", "target")
    assert result.blocked_path == path
    assert path.read_bytes() == before
    assert source.path.read_bytes() == before_source
    assert _log(tmp_path) == log_before


@REPRESENTATIVE
@OPS
def test_a_file_without_any_frontmatter_at_the_source_slug_is_refused_cleanly(source_name, target_name, op, tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME[source_name], _SPEC_BY_NAME[target_name]
    relationship_type = _relationship_type(source_name, target_name)
    directory = tmp_path / source_spec.note_type
    directory.mkdir(parents=True)
    path = directory / "source.md"
    before = b"# Source\n\njust markdown, no frontmatter at all\n"
    path.write_bytes(before)
    _capture(target_spec, "Target", tmp_path)
    log_before = _log(tmp_path)

    result = _do(op, source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert (result.applicable, result.reason, result.end) == (False, "missing", "source")
    assert path.read_bytes() == before
    assert _log(tmp_path) == log_before


# ---- refusing when a title cannot be resolved to exactly one note -------------------


@REPRESENTATIVE
@OPS
def test_two_notes_with_the_source_title_refuse_as_ambiguous(source_name, target_name, op, tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME[source_name], _SPEC_BY_NAME[target_name]
    relationship_type = _relationship_type(source_name, target_name)
    directory = tmp_path / source_spec.note_type
    directory.mkdir(parents=True)
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text(_hand_text(source_spec, "Source", tmp_path, "a"), encoding="utf-8")
    b.write_text(_hand_text(source_spec, "Source", tmp_path, "b"), encoding="utf-8")
    before = {a: a.read_bytes(), b: b.read_bytes()}
    _capture(target_spec, "Target", tmp_path)
    log_before = _log(tmp_path)

    result = _do(op, source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert (result.applicable, result.reason, result.end) == (False, "ambiguous_title", "source")
    assert set(result.candidates) == {a, b}
    assert a.read_bytes() == before[a] and b.read_bytes() == before[b]
    assert _log(tmp_path) == log_before


def test_an_ambiguous_target_refuses_before_anything_is_written(tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME["Project"], _SPEC_BY_NAME["Resource"]
    relationship_type = _relationship_type("Project", "Resource")
    source = _capture(source_spec, "Source", tmp_path)
    before_source = source.path.read_bytes()
    directory = tmp_path / target_spec.note_type
    directory.mkdir(parents=True)
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text(_hand_text(target_spec, "Target", tmp_path, "a"), encoding="utf-8")
    b.write_text(_hand_text(target_spec, "Target", tmp_path, "b"), encoding="utf-8")

    result = _do("link", source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert (result.applicable, result.reason, result.end) == (False, "ambiguous_title", "target")
    assert set(result.candidates) == {a, b}
    assert source.path.read_bytes() == before_source


def test_a_note_of_a_different_type_holding_the_source_title_is_refused(tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME["Project"], _SPEC_BY_NAME["Area"]
    relationship_type = _relationship_type("Project", "Area")
    directory = tmp_path / source_spec.note_type
    directory.mkdir(parents=True)
    misfiled = directory / "misfiled.md"
    misfiled.write_text(_hand_text(target_spec, "Source", tmp_path, "misfiled"), encoding="utf-8")
    before = misfiled.read_bytes()
    _capture(target_spec, "Target", tmp_path)

    result = _do("link", source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert (result.applicable, result.reason, result.end) == (False, "not_an_ohtli_note", "source")
    assert result.blocked_path == misfiled
    assert misfiled.read_bytes() == before


def test_a_symlink_that_only_reaches_the_source_title_from_outside_is_refused(tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME["Project"], _SPEC_BY_NAME["Area"]
    relationship_type = _relationship_type("Project", "Area")
    outside_dir = tmp_path / "outside"
    outside = _capture(source_spec, "Source", outside_dir)
    before = outside.path.read_bytes()
    directory = tmp_path / source_spec.note_type
    directory.mkdir(parents=True)
    link = directory / "linked.md"
    _symlink(link, outside.path)
    _capture(target_spec, "Target", tmp_path)
    log_before = _log(tmp_path)

    result = _do("link", source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert (result.applicable, result.reason, result.end) == (False, "not_an_ohtli_note", "source")
    assert result.blocked_path == link
    assert outside.path.read_bytes() == before
    assert _log(tmp_path) == log_before


def test_a_missing_target_reports_end_target(tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME["Project"], _SPEC_BY_NAME["Area"]
    relationship_type = _relationship_type("Project", "Area")
    _capture(source_spec, "Source", tmp_path)

    result = _do("link", source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert (result.applicable, result.reason, result.end) == (False, "missing", "target")


def test_a_shared_title_still_names_the_right_end(tmp_path):
    """Source and target share a title; only the target is missing. `end`
    must say "target", not just repeat `search_title`, which would be the
    same string for either end."""
    source_spec, target_spec = _SPEC_BY_NAME["Project"], _SPEC_BY_NAME["Resource"]
    relationship_type = _relationship_type("Project", "Resource")
    _capture(source_spec, "X", tmp_path)

    result = _do("link", source_spec, "X", target_spec, "X", tmp_path, relationship_type)

    assert (result.applicable, result.reason, result.end) == (False, "missing", "target")
    assert result.search_title == "X"


def test_when_both_ends_are_missing_the_source_is_reported_first(tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME["Project"], _SPEC_BY_NAME["Area"]
    relationship_type = _relationship_type("Project", "Area")

    result = _do("link", source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert (result.applicable, result.reason, result.end) == (False, "missing", "source")


# ---- the race-free revalidation right before the write -------------------------------


def test_if_the_source_changes_between_locating_and_writing_it_is_refused(tmp_path, monkeypatch):
    source_spec, target_spec = _SPEC_BY_NAME["Project"], _SPEC_BY_NAME["Area"]
    relationship_type = _relationship_type("Project", "Area")
    source = _capture(source_spec, "Source", tmp_path)
    target = _capture(target_spec, "Target", tmp_path)
    before = source.path.read_bytes()
    log_before = _log(tmp_path)
    real_inspect = execution.inspect_target

    def _flaky(path):
        if path == source.path:
            return None
        return real_inspect(path)

    monkeypatch.setattr(execution, "inspect_target", _flaky)

    result = _do("link", source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert (result.applicable, result.reason, result.end) == (False, "not_an_ohtli_note", "source")
    assert result.event is None
    assert source.path.read_bytes() == before
    assert _log(tmp_path) == log_before


def test_if_the_target_changes_between_locating_and_writing_it_is_refused(tmp_path, monkeypatch):
    source_spec, target_spec = _SPEC_BY_NAME["Project"], _SPEC_BY_NAME["Area"]
    relationship_type = _relationship_type("Project", "Area")
    source = _capture(source_spec, "Source", tmp_path)
    target = _capture(target_spec, "Target", tmp_path)
    before = source.path.read_bytes()
    log_before = _log(tmp_path)
    real_inspect = execution.inspect_target

    def _flaky(path):
        if path == target.path:
            return None
        return real_inspect(path)

    monkeypatch.setattr(execution, "inspect_target", _flaky)

    result = _do("link", source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert (result.applicable, result.reason, result.end) == (False, "not_an_ohtli_note", "target")
    assert result.event is None
    assert source.path.read_bytes() == before
    assert _log(tmp_path) == log_before


# ---- an ordinary relate/unrelate, with nothing wrong, is unaffected ------------------


@REPRESENTATIVE
@OPS
def test_an_ordinary_relate_unrelate_at_the_expected_paths_still_works(source_name, target_name, op, tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME[source_name], _SPEC_BY_NAME[target_name]
    relationship_type = _relationship_type(source_name, target_name)
    source, target = _seed(op, source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    result = _do(op, source_spec, "Source", target_spec, "Target", tmp_path, relationship_type)

    assert result.applicable is True and result.reason is None
    assert result.path == source.path
    assert result.event is not None


def test_a_bounded_unlink_without_to_still_works_for_a_renamed_source(tmp_path):
    source_spec, target_spec = _SPEC_BY_NAME[BOUNDED[0]], _SPEC_BY_NAME[BOUNDED[1]]
    relationship_type = _relationship_type(*BOUNDED)
    source = _capture(source_spec, "Source", tmp_path)
    _capture(target_spec, "Target", tmp_path)
    assert _do("link", source_spec, "Source", target_spec, "Target", tmp_path, relationship_type).applicable
    renamed = source.path.parent / "renamed-source.md"
    source.path.rename(renamed)

    result = execute_unrelate(
        UnrelateRequest(source_title="Source", actor=Actor.HUMAN, relationship_type=relationship_type),
        spec=source_spec,
        base_dir=tmp_path / source_spec.note_type,
        events_dir=tmp_path / "events",
    )

    assert result.applicable is True
    assert result.path == renamed
