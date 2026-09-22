"""Archive's Operational Integrity: archiving the *source* of a `supports`
relationship is refused while its *target* (the requirer) is still
operational. `supports` is the one canonical relationship type chosen to
express "operationally required by" (Phase 35 issue) — every other
relationship type never blocks. All against `tmp_path`.
"""

import pytest

from ohtli.representation.relationship import relate
from ohtli.vault_io.markdown import read_note, rewrite_note

from ohtli.execution.execution import (
    Actor,
    ArchiveRequest,
    ExecutionRequest,
    RelateRequest,
    UnrelateRequest,
    execute_archive,
    execute_capture,
    execute_relate,
    execute_unrelate,
    read_operational_dependents,
)
from ohtli.execution.specs import AREA, MEETING, PROJECT, REFERENCE, RESOURCE
from ohtli.vault_io.events import read_events
from ohtli.workflow import archive as archive_workflow

SUPPORTS_PAIRS = [
    pytest.param(REFERENCE, PROJECT, id="reference-project"),
    pytest.param(REFERENCE, RESOURCE, id="reference-resource"),
    pytest.param(RESOURCE, PROJECT, id="resource-project"),
    pytest.param(MEETING, PROJECT, id="meeting-project"),
]

# a non-`supports` pair for each of the other three relationship types
NON_REQUIRING_PAIRS = [
    pytest.param(PROJECT, AREA, "belongs to", id="belongs_to"),
    pytest.param(PROJECT, MEETING, "contains", id="contains"),
    pytest.param(RESOURCE, REFERENCE, "references", id="references"),
]


def _capture(tmp_path, spec, title):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN), spec=spec, base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path,
    )


def _link(tmp_path, source, target, relationship_type, source_title="Source", target_title="Target", actor=Actor.HUMAN):
    return execute_relate(
        RelateRequest(
            source_title=source_title, target_title=target_title, actor=actor, relationship_type=relationship_type
        ),
        source_spec=source,
        target_spec=target,
        base_dir=tmp_path / source.note_type,
        target_base_dir=tmp_path / target.note_type,
        events_dir=tmp_path,
    )


def _unlink(tmp_path, source, target, source_title="Source", target_title="Target"):
    return execute_unrelate(
        UnrelateRequest(
            source_title=source_title, actor=Actor.HUMAN, relationship_type="supports", target_title=target_title
        ),
        spec=source,
        target_spec=target,
        base_dir=tmp_path / source.note_type,
        target_base_dir=tmp_path / target.note_type,
        events_dir=tmp_path,
    )


def _archive(tmp_path, spec, title):
    return execute_archive(
        ArchiveRequest(title=title, actor=Actor.HUMAN), spec=spec, base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path,
    )


# ---- the mechanism, isolated (workflow layer) --------------------------------------


def test_is_applicable_blocks_only_when_operational_and_required():
    assert archive_workflow.is_applicable("operational")
    assert not archive_workflow.is_applicable("operational", has_operational_dependents=True)
    assert not archive_workflow.is_applicable("historical")
    assert not archive_workflow.is_applicable("historical", has_operational_dependents=True)


def test_supports_is_the_only_operationally_requiring_type():
    assert archive_workflow.OPERATIONALLY_REQUIRING_TYPES == frozenset({"supports"})


# ---- the block itself, all 4 `supports` pairs ---------------------------------------


@pytest.mark.parametrize("source,target", SUPPORTS_PAIRS)
def test_archiving_the_source_is_blocked_while_the_target_is_operational(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    _link(tmp_path, source, target, "supports")
    before = src.path.read_bytes()
    events_before = len(read_events(events_dir=tmp_path))

    result = _archive(tmp_path, source, "Source")

    assert not result.applicable
    assert result.reason == "operational_dependents"
    assert result.event is None
    assert src.path.read_bytes() == before
    assert len(read_events(events_dir=tmp_path)) == events_before


@pytest.mark.parametrize("source,target", SUPPORTS_PAIRS)
def test_unlinking_first_lets_the_source_be_archived(tmp_path, source, target):
    _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    _link(tmp_path, source, target, "supports")

    assert _unlink(tmp_path, source, target).applicable
    result = _archive(tmp_path, source, "Source")

    assert result.applicable and result.reason is None


@pytest.mark.parametrize("source,target", SUPPORTS_PAIRS)
def test_archiving_the_requirer_first_lets_the_source_be_archived(tmp_path, source, target):
    _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    _link(tmp_path, source, target, "supports")

    requirer_archived = _archive(tmp_path, target, "Target")
    assert requirer_archived.applicable

    result = _archive(tmp_path, source, "Source")

    assert result.applicable and result.reason is None


@pytest.mark.parametrize("source,target", SUPPORTS_PAIRS)
def test_an_already_historical_requirer_never_blocked_in_the_first_place(tmp_path, source, target):
    _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    assert _archive(tmp_path, target, "Target").applicable  # historical before the link exists
    _link(tmp_path, source, target, "supports")

    result = _archive(tmp_path, source, "Source")

    assert result.applicable and result.reason is None


@pytest.mark.parametrize("source,target", SUPPORTS_PAIRS)
def test_read_operational_dependents_names_the_blocking_target(tmp_path, source, target):
    _capture(tmp_path, source, "Source")
    tgt = _capture(tmp_path, target, "Target")
    _link(tmp_path, source, target, "supports")

    dependents = read_operational_dependents("Source", source, base_dir=tmp_path / source.note_type)

    assert [d["id"] for d in dependents] == [tgt.project.id]
    assert dependents[0]["context"] == "operational"


# ---- direction matters: archiving the TARGET (requirer) is never blocked -----------


@pytest.mark.parametrize("source,target", SUPPORTS_PAIRS)
def test_archiving_the_target_requirer_is_never_blocked_by_this_rule(tmp_path, source, target):
    """The rule only constrains the source (the required thing). Archiving
    the target while the source is operational is unaffected."""
    _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    _link(tmp_path, source, target, "supports")

    result = _archive(tmp_path, target, "Target")

    assert result.applicable and result.reason is None


# ---- every other relationship type never blocks -------------------------------------


@pytest.mark.parametrize("source,target,relationship_type", NON_REQUIRING_PAIRS)
def test_other_relationship_types_never_block_archiving_the_source(tmp_path, source, target, relationship_type):
    _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    linked = _link(tmp_path, source, target, relationship_type)
    assert linked.applicable, f"could not even establish {relationship_type}"

    result = _archive(tmp_path, source, "Source")

    assert result.applicable and result.reason is None


# ---- robustness -----------------------------------------------------------------------


def test_a_dangling_relationship_target_does_not_block_and_does_not_crash(tmp_path):
    src = _capture(tmp_path, RESOURCE, "Source")
    text = src.path.read_text(encoding="utf-8").replace(
        "tags: []",
        "tags: []\nrelationships:\n- id: x\n  type: supports\n  target_id: no-such-id\n"
        "  target_type: project\n  target_link: '[[x|x]]'",
    )
    src.path.write_text(text, encoding="utf-8")

    result = _archive(tmp_path, RESOURCE, "Source")

    assert result.applicable and result.reason is None


def test_a_missing_note_still_reports_missing_not_operational_dependents(tmp_path):
    result = _archive(tmp_path, RESOURCE, "Nope")

    assert not result.applicable and result.reason == "missing"


def test_read_operational_dependents_is_empty_for_a_note_that_does_not_exist(tmp_path):
    assert read_operational_dependents("Nope", RESOURCE, base_dir=tmp_path / "resource") == ()


# ---- reactivate is unaffected ---------------------------------------------------------


def test_reactivate_never_sets_a_reason(tmp_path):
    """Operational Integrity is Archive-only this phase; Reactivate results
    never carry a `reason` (it stays the dataclass default, `None`)."""
    from ohtli.execution.execution import execute_reactivate

    result = execute_reactivate(
        ArchiveRequest(title="Nope", actor=Actor.HUMAN),
        spec=RESOURCE,
        base_dir=tmp_path / "resource",
        events_dir=tmp_path,
    )
    assert result.reason is None


def test_a_pre_phase_13_target_with_no_context_field_still_blocks(tmp_path):
    """Regression: `Demo Vertical Slice Project` in the real vault has no
    `context` field (pre-Phase-13). Missing context is implicitly
    operational — a note is never explicitly marked historical until
    Archive does it — so it must still block, not be silently excluded."""
    src = _capture(tmp_path, RESOURCE, "Source")
    projects = tmp_path / "project"
    projects.mkdir(parents=True, exist_ok=True)
    (projects / "legacy.md").write_text(
        "---\nid: 22222222-2222-2222-2222-222222222222\nnote_type: project\n"
        "created: '2026-08-25'\nupdated: '2026-08-25'\ntags: []\naliases: []\nstatus: planned\n---\n\n"
        "# Legacy\n\n## Objective\n",
        encoding="utf-8",
    )

    linked = relate(
        read_note(src.path),
        relationship_type="supports",
        target_id="22222222-2222-2222-2222-222222222222",
        target_type="project",
        target_link="[[projects/legacy|Legacy]]",
    )
    rewrite_note(src.path, linked)

    result = _archive(tmp_path, RESOURCE, "Source")

    assert not result.applicable and result.reason == "operational_dependents"
