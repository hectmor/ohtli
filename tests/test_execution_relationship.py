import json

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
from ohtli.execution.specs import AREA, RESOURCE
from ohtli.vault_io import paths
from ohtli.vault_io.events import read_events
from ohtli.vault_io.markdown import read_area, read_project


def _project(tmp_path, title="Website", actor=Actor.HUMAN):
    return execute_capture(
        ExecutionRequest(title=title, actor=actor),
        base_dir=tmp_path / "projects",
        events_dir=tmp_path,
    )


def _area(tmp_path, title="Health"):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=AREA,
        base_dir=tmp_path / "areas",
        events_dir=tmp_path,
    )


def _link(tmp_path, project="Website", area="Health", actor=Actor.HUMAN, **kwargs):
    return execute_relate(
        RelateRequest(source_title=project, target_title=area, actor=actor),
        base_dir=tmp_path / "projects",
        target_base_dir=tmp_path / "areas",
        events_dir=tmp_path,
        **kwargs,
    )


def _unlink(tmp_path, project="Website", actor=Actor.HUMAN):
    return execute_unrelate(
        UnrelateRequest(source_title=project, actor=actor),
        base_dir=tmp_path / "projects",
        events_dir=tmp_path,
    )


def _relationship_events(tmp_path):
    return [e for e in read_events(events_dir=tmp_path) if "Linked" in e.event_type or "Unlinked" in e.event_type]


def test_a_never_linked_project_has_no_relationships_key(tmp_path):
    project = _project(tmp_path)

    assert "relationships" not in read_project(project.path)["properties"]


def test_link_stores_the_relationship_on_the_project_by_stable_id(tmp_path):
    project = _project(tmp_path)
    area = _area(tmp_path)

    result = _link(tmp_path)

    assert result.applicable
    (entry,) = read_project(project.path)["properties"]["relationships"]
    assert entry["type"] == "belongs to"
    assert entry["target_id"] == area.project.id
    assert entry["target_type"] == "area"
    assert entry["target_link"] == "[[areas/health|Health]]"
    assert entry["id"] not in (project.project.id, area.project.id)


def test_link_emits_a_linked_event_naming_both_ends(tmp_path):
    project = _project(tmp_path)
    area = _area(tmp_path)

    result = _link(tmp_path)

    assert result.event.event_type == "Project Linked to Area"
    assert result.event.object_id == project.project.id
    assert result.event.object_type == "Project"
    assert result.event.target_id == area.project.id
    assert result.event.workflow == "processing"


def test_other_operations_leave_target_id_empty(tmp_path):
    project = _project(tmp_path)

    assert project.event.target_id is None


def test_a_second_link_is_rejected_by_the_zero_or_one_cardinality(tmp_path):
    _project(tmp_path)
    _area(tmp_path, "Health")
    _area(tmp_path, "Finance")
    _link(tmp_path, area="Health")

    second = _link(tmp_path, area="Finance")

    assert not second.applicable
    assert second.event is None
    assert len(_relationship_events(tmp_path)) == 1, "a rejection must emit no event"


def test_a_missing_source_is_rejected(tmp_path):
    _area(tmp_path)

    result = _link(tmp_path, project="Nonexistent")

    assert not result.applicable and result.event is None


def test_a_missing_target_is_rejected(tmp_path):
    _project(tmp_path)

    result = _link(tmp_path, area="Nonexistent")

    assert not result.applicable and result.event is None
    assert _relationship_events(tmp_path) == []


def test_a_target_that_is_not_an_area_is_rejected(tmp_path):
    _project(tmp_path)
    execute_capture(
        ExecutionRequest(title="Health", actor=Actor.HUMAN),
        spec=RESOURCE,
        base_dir=tmp_path / "resources",
        events_dir=tmp_path,
    )

    result = execute_relate(
        RelateRequest(source_title="Website", target_title="Health", actor=Actor.HUMAN),
        target_spec=RESOURCE,
        base_dir=tmp_path / "projects",
        target_base_dir=tmp_path / "resources",
        events_dir=tmp_path,
    )

    assert not result.applicable, "Project belongs to Area — a Resource is not an Area"
    assert result.event is None


def test_an_undefined_relationship_type_is_rejected(tmp_path):
    _project(tmp_path)
    _area(tmp_path)

    result = execute_relate(
        RelateRequest(
            source_title="Website", target_title="Health", actor=Actor.HUMAN, relationship_type="relates to"
        ),
        base_dir=tmp_path / "projects",
        target_base_dir=tmp_path / "areas",
        events_dir=tmp_path,
    )

    assert not result.applicable


def test_unlink_removes_the_entry_and_the_key_entirely(tmp_path):
    project = _project(tmp_path)
    _area(tmp_path)
    _link(tmp_path)

    result = _unlink(tmp_path)

    assert result.applicable
    assert "relationships" not in read_project(project.path)["properties"]


def test_unlinking_an_unlinked_project_is_rejected(tmp_path):
    _project(tmp_path)

    result = _unlink(tmp_path)

    assert not result.applicable and result.event is None


def test_moving_a_project_is_an_unlink_then_a_link_with_two_events(tmp_path):
    project = _project(tmp_path)
    health = _area(tmp_path, "Health")
    finance = _area(tmp_path, "Finance")

    _link(tmp_path, area="Health")
    _unlink(tmp_path)
    _link(tmp_path, area="Finance")

    events = _relationship_events(tmp_path)
    assert [(e.event_type, e.target_id) for e in events] == [
        ("Project Linked to Area", health.project.id),
        ("Project Unlinked from Area", health.project.id),
        ("Project Linked to Area", finance.project.id),
    ]
    (entry,) = read_project(project.path)["properties"]["relationships"]
    assert entry["target_id"] == finance.project.id


def test_an_archived_area_is_still_a_valid_target(tmp_path):
    _project(tmp_path)
    _area(tmp_path)
    execute_archive(
        ArchiveRequest(title="Health", actor=Actor.HUMAN),
        spec=AREA,
        base_dir=tmp_path / "areas",
        events_dir=tmp_path,
    )

    assert _link(tmp_path).applicable


def test_archiving_an_area_leaves_its_projects_links_untouched(tmp_path):
    project = _project(tmp_path)
    _area(tmp_path)
    _link(tmp_path)
    before = project.path.read_text(encoding="utf-8")

    execute_archive(
        ArchiveRequest(title="Health", actor=Actor.HUMAN),
        spec=AREA,
        base_dir=tmp_path / "areas",
        events_dir=tmp_path,
    )

    assert project.path.read_text(encoding="utf-8") == before, "Archive is non-cascading"


def test_linking_changes_neither_lifecycle_nor_presence_nor_identity_of_the_project(tmp_path):
    project = _project(tmp_path)
    _area(tmp_path)
    before = read_project(project.path)

    _link(tmp_path)
    after = read_project(project.path)

    for key in ("id", "status", "context", "note_type", "created"):
        assert after["properties"][key] == before["properties"][key]
    assert after["title"] == before["title"]


def test_linking_never_touches_the_area_note(tmp_path):
    _project(tmp_path)
    area = _area(tmp_path)
    before = area.path.read_text(encoding="utf-8")

    _link(tmp_path)

    assert area.path.read_text(encoding="utf-8") == before, "the inverse is not stored"
    assert "relationships" not in read_area(area.path)["properties"]


def test_a_pre_phase_13_note_without_context_can_be_linked(tmp_path):
    projects = tmp_path / "projects"
    projects.mkdir()
    legacy = projects / "legacy.md"
    legacy.write_text(
        "---\nid: 11111111-1111-1111-1111-111111111111\nnote_type: project\n"
        "created: '2026-08-25'\nupdated: '2026-08-25'\ntags: []\naliases: []\nstatus: planned\n---\n\n"
        "# Legacy\n\n## Objective\n",
        encoding="utf-8",
    )
    _area(tmp_path)

    result = _link(tmp_path, project="Legacy")

    assert result.applicable
    properties = read_project(legacy)["properties"]
    assert "context" not in properties, "linking must not invent a context"
    assert len(properties["relationships"]) == 1


def test_the_unlink_event_names_the_removed_target(tmp_path):
    project = _project(tmp_path)
    area = _area(tmp_path)
    _link(tmp_path)

    result = _unlink(tmp_path)

    assert result.event.event_type == "Project Unlinked from Area"
    assert result.event.object_id == project.project.id
    assert result.event.target_id == area.project.id


def test_the_display_link_is_not_authoritative(tmp_path):
    """Corrupting `target_link` must not affect anything: the id is the
    authority, so unlink still names the right target."""
    project = _project(tmp_path)
    area = _area(tmp_path)
    _link(tmp_path)
    text = project.path.read_text(encoding="utf-8")
    assert "[[areas/health|Health]]" in text
    project.path.write_text(text.replace("[[areas/health|Health]]", "garbage"), encoding="utf-8")

    result = _unlink(tmp_path)

    assert result.applicable
    assert result.event.target_id == area.project.id


def test_human_and_deterministic_actors_behave_identically(tmp_path):
    _project(tmp_path, "By Human")
    _project(tmp_path, "By Machine")
    _area(tmp_path)

    human = _link(tmp_path, project="By Human", actor=Actor.HUMAN)
    machine = _link(tmp_path, project="By Machine", actor=Actor.DETERMINISTIC)

    assert human.applicable and machine.applicable
    assert human.event.event_type == machine.event.event_type
    assert human.event.target_id == machine.event.target_id
    assert (human.event.actor, machine.event.actor) == ("human", "deterministic")
    human_entry = read_project(human.path)["properties"]["relationships"][0]
    machine_entry = read_project(machine.path)["properties"]["relationships"][0]
    assert set(human_entry) == set(machine_entry)
    assert human_entry["id"] != machine_entry["id"], "each instance has its own identity"


def test_an_old_event_line_without_target_id_still_reads(tmp_path):
    events_file = paths.events_file_path(tmp_path)
    events_file.parent.mkdir(parents=True, exist_ok=True)
    events_file.write_text(
        json.dumps(
            {
                "event_type": "Project Created",
                "object_id": "old-1",
                "object_type": "Project",
                "actor": "human",
                "execution_id": "e-1",
                "workflow": "capture",
                "event_id": "ev-1",
                "occurred_at": "2026-09-01T00:00:00+00:00",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    (event,) = read_events(events_dir=tmp_path)

    assert event.target_id is None
