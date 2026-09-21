"""`Project contains Meeting`: an independent, stored, `0..*` relationship.

The spec does not declare it complementary to `Meeting supports Project`, so it
is stored on the Project like every other relationship and may legitimately
differ from what the Meeting says. (`Area contains Project`, by contrast, is
derived and never stored.) All against `tmp_path`.
"""

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
from ohtli.execution.specs import MEETING, PROJECT
from ohtli.vault_io.events import read_events


def _capture(tmp_path, spec, title):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path,
    )


def _relate(tmp_path, source, target, source_title, target_title, relationship_type, actor=Actor.HUMAN):
    return execute_relate(
        RelateRequest(
            source_title=source_title,
            target_title=target_title,
            actor=actor,
            relationship_type=relationship_type,
        ),
        source_spec=source,
        target_spec=target,
        base_dir=tmp_path / source.note_type,
        target_base_dir=tmp_path / target.note_type,
        events_dir=tmp_path,
    )


def _contain(tmp_path, meeting="Meeting", project="Project", actor=Actor.HUMAN):
    return _relate(tmp_path, PROJECT, MEETING, project, meeting, "contains", actor)


def _uncontain(tmp_path, meeting="Meeting", project="Project"):
    return execute_unrelate(
        UnrelateRequest(
            source_title=project, actor=Actor.HUMAN, relationship_type="contains", target_title=meeting
        ),
        spec=PROJECT,
        target_spec=MEETING if meeting is not None else None,
        base_dir=tmp_path / PROJECT.note_type,
        target_base_dir=tmp_path / MEETING.note_type,
        events_dir=tmp_path,
    )


def _entries(path):
    return PROJECT.read(path)["properties"].get("relationships", [])


def _relationship_events(tmp_path):
    return [e for e in read_events(events_dir=tmp_path) if "Linked" in e.event_type or "Unlinked" in e.event_type]


def test_the_project_stores_the_relationship_by_stable_id(tmp_path):
    project = _capture(tmp_path, PROJECT, "Project")
    meeting = _capture(tmp_path, MEETING, "Meeting")

    result = _contain(tmp_path)

    assert result.applicable
    (entry,) = _entries(project.path)
    assert entry["type"] == "contains"
    assert entry["target_id"] == meeting.project.id
    assert entry["target_type"] == "meeting"
    assert entry["id"] not in (project.project.id, meeting.project.id)


def test_the_link_event_names_both_ends(tmp_path):
    project = _capture(tmp_path, PROJECT, "Project")
    meeting = _capture(tmp_path, MEETING, "Meeting")

    result = _contain(tmp_path)

    assert result.event.event_type == "Project Linked to Meeting"
    assert result.event.object_id == project.project.id
    assert result.event.object_type == "Project"
    assert result.event.target_id == meeting.project.id
    assert result.event.workflow == "processing"


def test_a_project_can_contain_many_meetings_but_not_the_same_one_twice(tmp_path):
    project = _capture(tmp_path, PROJECT, "Project")
    for title in ("Meeting", "Meeting Two", "Meeting Three"):
        _capture(tmp_path, MEETING, title)

    assert all(_contain(tmp_path, meeting=t).applicable for t in ("Meeting", "Meeting Two", "Meeting Three"))
    duplicate = _contain(tmp_path, meeting="Meeting Two")

    assert not duplicate.applicable and duplicate.event is None
    assert len(_entries(project.path)) == 3
    assert len(_relationship_events(tmp_path)) == 3


def test_unlink_by_target_removes_exactly_that_instance(tmp_path):
    project = _capture(tmp_path, PROJECT, "Project")
    _capture(tmp_path, MEETING, "Meeting")
    two = _capture(tmp_path, MEETING, "Meeting Two")
    _contain(tmp_path, meeting="Meeting")
    _contain(tmp_path, meeting="Meeting Two")

    result = _uncontain(tmp_path, meeting="Meeting")

    assert result.applicable
    assert result.event.event_type == "Project Unlinked from Meeting"
    assert [e["target_id"] for e in _entries(project.path)] == [two.project.id]


def test_unlinking_the_last_instance_restores_a_never_linked_shape(tmp_path):
    project = _capture(tmp_path, PROJECT, "Project")
    _capture(tmp_path, MEETING, "Meeting")
    before_keys = list(PROJECT.read(project.path)["properties"])
    _contain(tmp_path)

    _uncontain(tmp_path)

    assert list(PROJECT.read(project.path)["properties"]) == before_keys
    assert "relationships" not in PROJECT.read(project.path)["properties"]


def test_unlink_without_a_target_is_refused_for_an_unbounded_relationship(tmp_path):
    project = _capture(tmp_path, PROJECT, "Project")
    _capture(tmp_path, MEETING, "Meeting")
    _contain(tmp_path)

    result = _uncontain(tmp_path, meeting=None)

    assert not result.applicable and result.event is None
    assert len(_entries(project.path)) == 1


def test_unlinking_a_meeting_that_is_not_contained_is_refused(tmp_path):
    project = _capture(tmp_path, PROJECT, "Project")
    _capture(tmp_path, MEETING, "Meeting")
    _capture(tmp_path, MEETING, "Other")
    _contain(tmp_path, meeting="Meeting")

    result = _uncontain(tmp_path, meeting="Other")

    assert not result.applicable and result.event is None
    assert len(_entries(project.path)) == 1


def test_a_missing_project_or_meeting_is_refused_without_an_event(tmp_path):
    _capture(tmp_path, PROJECT, "Project")
    _capture(tmp_path, MEETING, "Meeting")

    assert not _contain(tmp_path, project="Nope").applicable
    assert not _contain(tmp_path, meeting="Nope").applicable
    assert _relationship_events(tmp_path) == []


def test_linking_never_touches_the_meeting_or_the_projects_identity_and_lifecycle(tmp_path):
    project = _capture(tmp_path, PROJECT, "Project")
    meeting = _capture(tmp_path, MEETING, "Meeting")
    before = PROJECT.read(project.path)
    meeting_before = meeting.path.read_bytes()

    _contain(tmp_path)
    after = PROJECT.read(project.path)

    assert meeting.path.read_bytes() == meeting_before, "the inverse is not stored"
    for key in ("id", "status", "context", "note_type", "created"):
        assert after["properties"][key] == before["properties"][key]
    assert after["title"] == before["title"] and after["body"] == before["body"]


def test_archiving_the_meeting_leaves_the_project_untouched(tmp_path):
    """`contains` is organization, not lifecycle dependency: Archive is non-cascading."""
    project = _capture(tmp_path, PROJECT, "Project")
    _capture(tmp_path, MEETING, "Meeting")
    _contain(tmp_path)
    before = project.path.read_bytes()

    execute_archive(
        ArchiveRequest(title="Meeting", actor=Actor.HUMAN),
        spec=MEETING,
        base_dir=tmp_path / MEETING.note_type,
        events_dir=tmp_path,
    )

    assert project.path.read_bytes() == before


def test_human_and_deterministic_actors_behave_identically(tmp_path):
    _capture(tmp_path, PROJECT, "By Human")
    _capture(tmp_path, PROJECT, "By Machine")
    _capture(tmp_path, MEETING, "Meeting")

    human = _contain(tmp_path, project="By Human", actor=Actor.HUMAN)
    machine = _contain(tmp_path, project="By Machine", actor=Actor.DETERMINISTIC)

    assert human.applicable and machine.applicable
    assert human.event.event_type == machine.event.event_type
    assert (human.event.actor, machine.event.actor) == ("human", "deterministic")


def test_it_is_independent_of_what_the_meeting_says_it_supports(tmp_path):
    """The spec does not make `Project contains Meeting` and `Meeting supports
    Project` complementary: they may name different Projects, and neither
    operation looks at, changes, or reconciles the other."""
    project = _capture(tmp_path, PROJECT, "Project")
    other = _capture(tmp_path, PROJECT, "Other Project")
    meeting = _capture(tmp_path, MEETING, "Meeting")

    supports = _relate(tmp_path, MEETING, PROJECT, "Meeting", "Other Project", "supports")
    contains = _contain(tmp_path)

    assert supports.applicable and contains.applicable
    assert [e["target_id"] for e in _entries(project.path)] == [meeting.project.id]
    (support_entry,) = MEETING.read(meeting.path)["properties"]["relationships"]
    assert (support_entry["type"], support_entry["target_id"]) == ("supports", other.project.id)

    assert _uncontain(tmp_path).applicable
    assert len(MEETING.read(meeting.path)["properties"]["relationships"]) == 1, "the Meeting's own link is untouched"


def test_containing_does_not_use_up_the_projects_belongs_to_slot(tmp_path):
    """Different relationship types on the same Project do not interact."""
    from ohtli.execution.specs import AREA

    project = _capture(tmp_path, PROJECT, "Project")
    _capture(tmp_path, MEETING, "Meeting")
    _capture(tmp_path, AREA, "Health")

    assert _contain(tmp_path).applicable
    assert _relate(tmp_path, PROJECT, AREA, "Project", "Health", "belongs to").applicable
    assert sorted(e["type"] for e in _entries(project.path)) == ["belongs to", "contains"]
