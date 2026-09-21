"""The `supports` relationships, executed for every source type.

`supports` is conceptual, not structural: it implies neither ownership nor
lifecycle dependency (`interaction-model/README.md`). Three are `0..*`; only
`Meeting supports Project` is `0..1`. All against `tmp_path`.
"""

import pytest

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
)
from ohtli.execution.specs import MEETING, PROJECT, REFERENCE, RESOURCE
from ohtli.vault_io.events import read_events

UNBOUNDED = [
    pytest.param(REFERENCE, PROJECT, id="reference-project"),
    pytest.param(REFERENCE, RESOURCE, id="reference-resource"),
    pytest.param(RESOURCE, PROJECT, id="resource-project"),
]
ALL_PAIRS = [*UNBOUNDED, pytest.param(MEETING, PROJECT, id="meeting-project")]


def _capture(tmp_path, spec, title):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path,
    )


def _link(tmp_path, source, target, source_title="Source", target_title="Target", actor=Actor.HUMAN):
    return execute_relate(
        RelateRequest(
            source_title=source_title, target_title=target_title, actor=actor, relationship_type="supports"
        ),
        source_spec=source,
        target_spec=target,
        base_dir=tmp_path / source.note_type,
        target_base_dir=tmp_path / target.note_type,
        events_dir=tmp_path,
    )


def _unlink(tmp_path, source, target, target_title="Target", source_title="Source"):
    return execute_unrelate(
        UnrelateRequest(
            source_title=source_title,
            actor=Actor.HUMAN,
            relationship_type="supports",
            target_title=target_title,
        ),
        spec=source,
        target_spec=target if target_title is not None else None,
        base_dir=tmp_path / source.note_type,
        target_base_dir=tmp_path / target.note_type,
        events_dir=tmp_path,
    )


def _entries(source, path):
    return source.read(path)["properties"].get("relationships", [])


def _relationship_events(tmp_path):
    return [e for e in read_events(events_dir=tmp_path) if "Linked" in e.event_type or "Unlinked" in e.event_type]


@pytest.mark.parametrize("source,target", ALL_PAIRS)
def test_the_source_stores_the_relationship_by_stable_id(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    tgt = _capture(tmp_path, target, "Target")

    result = _link(tmp_path, source, target)

    assert result.applicable
    (entry,) = _entries(source, src.path)
    assert entry["type"] == "supports"
    assert entry["target_id"] == tgt.project.id
    assert entry["target_type"] == target.note_type
    assert entry["id"] not in (src.project.id, tgt.project.id)


@pytest.mark.parametrize("source,target", ALL_PAIRS)
def test_the_link_event_names_both_ends(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    tgt = _capture(tmp_path, target, "Target")

    result = _link(tmp_path, source, target)

    assert result.event.event_type == f"{source.domain_type.__name__} Linked to {target.domain_type.__name__}"
    assert result.event.object_id == src.project.id
    assert result.event.object_type == source.domain_type.__name__
    assert result.event.target_id == tgt.project.id
    assert result.event.workflow == "processing"


@pytest.mark.parametrize("source,target", ALL_PAIRS)
def test_linking_the_same_target_twice_is_refused_without_an_event(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    _link(tmp_path, source, target)

    duplicate = _link(tmp_path, source, target)

    assert not duplicate.applicable and duplicate.event is None
    assert len(_entries(source, src.path)) == 1
    assert len(_relationship_events(tmp_path)) == 1


@pytest.mark.parametrize("source,target", ALL_PAIRS)
def test_linking_never_touches_the_target_or_the_sources_identity_and_lifecycle(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    tgt = _capture(tmp_path, target, "Target")
    before = source.read(src.path)
    target_before = tgt.path.read_bytes()

    _link(tmp_path, source, target)
    after = source.read(src.path)

    assert tgt.path.read_bytes() == target_before, "the inverse is not stored"
    for key in ("id", "status", "context", "note_type", "created"):
        assert after["properties"][key] == before["properties"][key]
    assert after["title"] == before["title"] and after["body"] == before["body"]


@pytest.mark.parametrize("source,target", ALL_PAIRS)
def test_human_and_deterministic_actors_behave_identically(tmp_path, source, target):
    _capture(tmp_path, source, "Source")
    _capture(tmp_path, source, "Source Two")
    _capture(tmp_path, target, "Target")

    human = _link(tmp_path, source, target, source_title="Source", actor=Actor.HUMAN)
    machine = _link(tmp_path, source, target, source_title="Source Two", actor=Actor.DETERMINISTIC)

    assert human.applicable and machine.applicable
    assert human.event.event_type == machine.event.event_type
    assert (human.event.actor, machine.event.actor) == ("human", "deterministic")


@pytest.mark.parametrize("source,target", ALL_PAIRS)
def test_a_missing_source_or_target_is_refused_without_an_event(tmp_path, source, target):
    _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")

    assert not _link(tmp_path, source, target, source_title="Nope").applicable
    assert not _link(tmp_path, source, target, target_title="Nope").applicable
    assert _relationship_events(tmp_path) == []


@pytest.mark.parametrize("source,target", ALL_PAIRS)
def test_supports_does_not_create_a_lifecycle_dependency(tmp_path, source, target):
    """Archiving either end must leave the linking note byte-identical."""
    src = _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    _link(tmp_path, source, target)
    before = src.path.read_bytes()

    execute_archive(
        ArchiveRequest(title="Target", actor=Actor.HUMAN),
        spec=target,
        base_dir=tmp_path / target.note_type,
        events_dir=tmp_path,
    )

    assert src.path.read_bytes() == before


# ---- the three 0..* relationships -------------------------------------------------


@pytest.mark.parametrize("source,target", UNBOUNDED)
def test_an_unbounded_supports_relationship_accepts_many_targets(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    _capture(tmp_path, target, "Target Two")
    _capture(tmp_path, target, "Target Three")

    results = [_link(tmp_path, source, target, target_title=t) for t in ("Target", "Target Two", "Target Three")]

    assert all(r.applicable for r in results)
    assert len(_entries(source, src.path)) == 3


@pytest.mark.parametrize("source,target", UNBOUNDED)
def test_unlink_by_target_removes_exactly_that_instance(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    two = _capture(tmp_path, target, "Target Two")
    _link(tmp_path, source, target, target_title="Target")
    _link(tmp_path, source, target, target_title="Target Two")

    result = _unlink(tmp_path, source, target, target_title="Target")

    assert result.applicable
    assert result.event.event_type == f"{source.domain_type.__name__} Unlinked from {target.domain_type.__name__}"
    assert result.event.object_id == src.project.id
    assert [e["target_id"] for e in _entries(source, src.path)] == [two.project.id]


@pytest.mark.parametrize("source,target", UNBOUNDED)
def test_unlinking_the_last_instance_restores_a_never_linked_shape(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    before_keys = list(source.read(src.path)["properties"])
    _link(tmp_path, source, target)

    _unlink(tmp_path, source, target)

    assert list(source.read(src.path)["properties"]) == before_keys
    assert "relationships" not in source.read(src.path)["properties"]


@pytest.mark.parametrize("source,target", UNBOUNDED)
def test_unlink_without_a_target_is_refused_for_an_unbounded_relationship(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    _link(tmp_path, source, target)

    result = _unlink(tmp_path, source, target, target_title=None)

    assert not result.applicable and result.event is None
    assert len(_entries(source, src.path)) == 1


@pytest.mark.parametrize("source,target", UNBOUNDED)
def test_unlinking_a_target_that_is_not_linked_is_refused(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    _capture(tmp_path, target, "Target Two")
    _link(tmp_path, source, target, target_title="Target")

    result = _unlink(tmp_path, source, target, target_title="Target Two")

    assert not result.applicable and result.event is None
    assert len(_entries(source, src.path)) == 1


# ---- Meeting supports Project (0..1) ----------------------------------------------


def test_a_meeting_supports_at_most_one_project(tmp_path):
    meeting = _capture(tmp_path, MEETING, "Source")
    _capture(tmp_path, PROJECT, "Project A")
    _capture(tmp_path, PROJECT, "Project B")
    assert _link(tmp_path, MEETING, PROJECT, target_title="Project A").applicable

    second = _link(tmp_path, MEETING, PROJECT, target_title="Project B")

    assert not second.applicable and second.event is None
    assert len(_entries(MEETING, meeting.path)) == 1
    assert len(_relationship_events(tmp_path)) == 1, "a refusal by cardinality emits no event"


def test_a_meeting_can_be_unlinked_without_naming_the_project(tmp_path):
    meeting = _capture(tmp_path, MEETING, "Source")
    project = _capture(tmp_path, PROJECT, "Project A")
    _link(tmp_path, MEETING, PROJECT, target_title="Project A")

    result = _unlink(tmp_path, MEETING, PROJECT, target_title=None)

    assert result.applicable
    assert result.event.target_id == project.project.id
    assert "relationships" not in MEETING.read(meeting.path)["properties"]


def test_a_meeting_can_be_unlinked_naming_the_project(tmp_path):
    meeting = _capture(tmp_path, MEETING, "Source")
    _capture(tmp_path, PROJECT, "Project A")
    _link(tmp_path, MEETING, PROJECT, target_title="Project A")

    assert _unlink(tmp_path, MEETING, PROJECT, target_title="Project A").applicable
    assert "relationships" not in MEETING.read(meeting.path)["properties"]


def test_moving_a_meeting_is_an_unlink_then_a_link_with_three_events(tmp_path):
    meeting = _capture(tmp_path, MEETING, "Source")
    a = _capture(tmp_path, PROJECT, "Project A")
    b = _capture(tmp_path, PROJECT, "Project B")

    _link(tmp_path, MEETING, PROJECT, target_title="Project A")
    _unlink(tmp_path, MEETING, PROJECT, target_title=None)
    _link(tmp_path, MEETING, PROJECT, target_title="Project B")

    assert [(e.event_type, e.target_id) for e in _relationship_events(tmp_path)] == [
        ("Meeting Linked to Project", a.project.id),
        ("Meeting Unlinked from Project", a.project.id),
        ("Meeting Linked to Project", b.project.id),
    ]
    (entry,) = _entries(MEETING, meeting.path)
    assert entry["target_id"] == b.project.id


def test_meeting_supports_project_and_meeting_references_coexist(tmp_path):
    """Different relationship types on the same source do not interact: the
    cardinality of `supports` (0..1) never limits `references` (0..*)."""
    meeting = _capture(tmp_path, MEETING, "Source")
    _capture(tmp_path, PROJECT, "Project A")
    _capture(tmp_path, REFERENCE, "Ref One")
    _capture(tmp_path, REFERENCE, "Ref Two")
    assert _link(tmp_path, MEETING, PROJECT, target_title="Project A").applicable

    refs = [
        execute_relate(
            RelateRequest(
                source_title="Source", target_title=t, actor=Actor.HUMAN, relationship_type="references"
            ),
            source_spec=MEETING,
            target_spec=REFERENCE,
            base_dir=tmp_path / MEETING.note_type,
            target_base_dir=tmp_path / REFERENCE.note_type,
            events_dir=tmp_path,
        )
        for t in ("Ref One", "Ref Two")
    ]

    assert all(r.applicable for r in refs)
    assert sorted(e["type"] for e in _entries(MEETING, meeting.path)) == ["references", "references", "supports"]


def test_a_reference_can_both_support_and_be_referenced_independently(tmp_path):
    """`Resource references Reference` and `Reference supports Resource` are two
    distinct relationships the spec defines separately; both may coexist."""
    resource = _capture(tmp_path, RESOURCE, "Res")
    reference = _capture(tmp_path, REFERENCE, "Ref")
    supports = execute_relate(
        RelateRequest(source_title="Ref", target_title="Res", actor=Actor.HUMAN, relationship_type="supports"),
        source_spec=REFERENCE,
        target_spec=RESOURCE,
        base_dir=tmp_path / REFERENCE.note_type,
        target_base_dir=tmp_path / RESOURCE.note_type,
        events_dir=tmp_path,
    )
    references = execute_relate(
        RelateRequest(source_title="Res", target_title="Ref", actor=Actor.HUMAN, relationship_type="references"),
        source_spec=RESOURCE,
        target_spec=REFERENCE,
        base_dir=tmp_path / RESOURCE.note_type,
        target_base_dir=tmp_path / REFERENCE.note_type,
        events_dir=tmp_path,
    )

    assert supports.applicable and references.applicable
    assert [e["type"] for e in _entries(REFERENCE, reference.path)] == ["supports"]
    assert [e["type"] for e in _entries(RESOURCE, resource.path)] == ["references"]
