"""The remaining `references` relationships, executed for every source type.

Each source stores its own `relationships` list (inverse never stored). All
against `tmp_path`, never the real vault.
"""

import pytest

from ohtli.execution.execution import (
    Actor,
    ExecutionRequest,
    RelateRequest,
    UnrelateRequest,
    execute_capture,
    execute_relate,
    execute_unrelate,
)
from ohtli.execution.specs import AREA, JOURNAL_ENTRY, MEETING, PROJECT, REFERENCE, RESOURCE
from ohtli.vault_io.events import read_events

PAIRS = [
    pytest.param(PROJECT, JOURNAL_ENTRY, id="project-journal_entry"),
    pytest.param(RESOURCE, REFERENCE, id="resource-reference"),
    pytest.param(MEETING, REFERENCE, id="meeting-reference"),
    pytest.param(MEETING, RESOURCE, id="meeting-resource"),
    pytest.param(JOURNAL_ENTRY, PROJECT, id="journal_entry-project"),
    pytest.param(JOURNAL_ENTRY, AREA, id="journal_entry-area"),
    pytest.param(JOURNAL_ENTRY, RESOURCE, id="journal_entry-resource"),
]


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
            source_title=source_title, target_title=target_title, actor=actor, relationship_type="references"
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
            relationship_type="references",
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


@pytest.mark.parametrize("source,target", PAIRS)
def test_the_source_stores_the_relationship_by_stable_id(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    tgt = _capture(tmp_path, target, "Target")

    result = _link(tmp_path, source, target)

    assert result.applicable
    (entry,) = _entries(source, src.path)
    assert entry["type"] == "references"
    assert entry["target_id"] == tgt.project.id
    assert entry["target_type"] == target.note_type
    assert entry["id"] not in (src.project.id, tgt.project.id)


@pytest.mark.parametrize("source,target", PAIRS)
def test_the_link_event_names_both_ends(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    tgt = _capture(tmp_path, target, "Target")

    result = _link(tmp_path, source, target)

    assert result.event.event_type == f"{source.domain_type.__name__} Linked to {target.domain_type.__name__}"
    assert result.event.object_id == src.project.id
    assert result.event.object_type == source.domain_type.__name__
    assert result.event.target_id == tgt.project.id
    assert result.event.workflow == "processing"


@pytest.mark.parametrize("source,target", PAIRS)
def test_a_source_can_reference_many_targets_but_not_the_same_twice(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    _capture(tmp_path, target, "Target Two")

    assert _link(tmp_path, source, target, target_title="Target").applicable
    assert _link(tmp_path, source, target, target_title="Target Two").applicable
    duplicate = _link(tmp_path, source, target, target_title="Target")

    assert not duplicate.applicable and duplicate.event is None
    assert len(_entries(source, src.path)) == 2
    assert len(_relationship_events(tmp_path)) == 2


@pytest.mark.parametrize("source,target", PAIRS)
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


@pytest.mark.parametrize("source,target", PAIRS)
def test_unlinking_the_last_instance_restores_a_never_linked_shape(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    before_keys = list(source.read(src.path)["properties"])
    _link(tmp_path, source, target)

    _unlink(tmp_path, source, target)

    assert list(source.read(src.path)["properties"]) == before_keys
    assert "relationships" not in source.read(src.path)["properties"]


@pytest.mark.parametrize("source,target", PAIRS)
def test_unlink_without_a_target_is_refused_for_an_unbounded_relationship(tmp_path, source, target):
    src = _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    _link(tmp_path, source, target)

    result = execute_unrelate(
        UnrelateRequest(source_title="Source", actor=Actor.HUMAN, relationship_type="references"),
        spec=source,
        base_dir=tmp_path / source.note_type,
        events_dir=tmp_path,
    )

    assert not result.applicable and result.event is None
    assert len(_entries(source, src.path)) == 1


@pytest.mark.parametrize("source,target", PAIRS)
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


@pytest.mark.parametrize("source,target", PAIRS)
def test_human_and_deterministic_actors_behave_identically(tmp_path, source, target):
    _capture(tmp_path, source, "Source")
    _capture(tmp_path, source, "Source Two")
    _capture(tmp_path, target, "Target")

    human = _link(tmp_path, source, target, source_title="Source", actor=Actor.HUMAN)
    machine = _link(tmp_path, source, target, source_title="Source Two", actor=Actor.DETERMINISTIC)

    assert human.applicable and machine.applicable
    assert human.event.event_type == machine.event.event_type
    assert (human.event.actor, machine.event.actor) == ("human", "deterministic")


@pytest.mark.parametrize("source,target", PAIRS)
def test_a_missing_source_or_target_is_refused_without_an_event(tmp_path, source, target):
    _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")

    assert not _link(tmp_path, source, target, source_title="Nope").applicable
    assert not _link(tmp_path, source, target, target_title="Nope").applicable
    assert _relationship_events(tmp_path) == []


def _refused(tmp_path, source, target, relationship_type):
    src = _capture(tmp_path, source, "Source")
    _capture(tmp_path, target, "Target")
    before = src.path.read_bytes()

    result = execute_relate(
        RelateRequest(
            source_title="Source", target_title="Target", actor=Actor.HUMAN, relationship_type=relationship_type
        ),
        source_spec=source,
        target_spec=target,
        base_dir=tmp_path / source.note_type,
        target_base_dir=tmp_path / target.note_type,
        events_dir=tmp_path,
    )

    assert not result.applicable and result.event is None
    assert src.path.read_bytes() == before


@pytest.mark.parametrize("relationship_type", ["references", "supports", "contains", "belongs to"])
def test_area_contains_project_is_refused_for_every_relationship_type(tmp_path, relationship_type):
    """Derived from `Project belongs to Area`: it can never be established."""
    _refused(tmp_path, AREA, PROJECT, relationship_type)


@pytest.mark.parametrize("relationship_type", ["references", "supports", "belongs to"])
def test_project_contains_meeting_is_refused_for_any_type_other_than_contains(tmp_path, relationship_type):
    _refused(tmp_path, PROJECT, MEETING, relationship_type)


@pytest.mark.parametrize(
    "source,target",
    [
        pytest.param(RESOURCE, PROJECT, id="resource-project"),
        pytest.param(REFERENCE, PROJECT, id="reference-project"),
        pytest.param(MEETING, PROJECT, id="meeting-project"),
    ],
)
@pytest.mark.parametrize("relationship_type", ["references", "contains", "belongs to"])
def test_a_supports_pair_is_refused_for_any_type_other_than_supports(
    tmp_path, source, target, relationship_type
):
    """The table is indexed by relationship type, not only by the pair."""
    _refused(tmp_path, source, target, relationship_type)
