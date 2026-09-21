from ohtli.execution import execution
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
from ohtli.execution.specs import AREA, JOURNAL_ENTRY, MEETING, PROJECT, REFERENCE, RESOURCE
from ohtli.vault_io import paths
from ohtli.vault_io.events import read_events
from ohtli.vault_io.markdown import read_project

_DIRS = {"area": "areas", "resource": "resources", "reference": "references"}
_SPECS = {"area": AREA, "resource": RESOURCE, "reference": REFERENCE}
_TYPES = {"area": "belongs to", "resource": "references", "reference": "references"}


def _project(tmp_path, title="Website"):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        base_dir=tmp_path / "projects",
        events_dir=tmp_path,
    )


def _target(tmp_path, kind, title):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=_SPECS[kind],
        base_dir=tmp_path / _DIRS[kind],
        events_dir=tmp_path,
    )


def _link(tmp_path, kind, title, project="Website", actor=Actor.HUMAN, **kwargs):
    return execute_relate(
        RelateRequest(
            source_title=project, target_title=title, actor=actor, relationship_type=_TYPES[kind], **kwargs
        ),
        target_spec=_SPECS[kind],
        base_dir=tmp_path / "projects",
        target_base_dir=tmp_path / _DIRS[kind],
        events_dir=tmp_path,
    )


def _unlink(tmp_path, kind=None, title=None, project="Website", **kwargs):
    return execute_unrelate(
        UnrelateRequest(
            source_title=project,
            target_title=title,
            actor=Actor.HUMAN,
            relationship_type=_TYPES[kind or "area"],
            **kwargs,
        ),
        target_spec=_SPECS[kind] if kind else None,
        base_dir=tmp_path / "projects",
        target_base_dir=tmp_path / _DIRS[kind] if kind else None,
        events_dir=tmp_path,
    )


def _entries(project):
    return read_project(project.path)["properties"].get("relationships", [])


def _rel_events(tmp_path):
    return [e for e in read_events(events_dir=tmp_path) if "Linked" in e.event_type or "Unlinked" in e.event_type]


def _project_with_many(tmp_path):
    project = _project(tmp_path)
    ids = {
        "r1": _target(tmp_path, "resource", "Res One").project.id,
        "r2": _target(tmp_path, "resource", "Res Two").project.id,
        "f1": _target(tmp_path, "reference", "Ref One").project.id,
    }
    _link(tmp_path, "resource", "Res One")
    _link(tmp_path, "resource", "Res Two")
    _link(tmp_path, "reference", "Ref One")
    return project, ids


def test_a_project_can_reference_many_resources_and_references(tmp_path):
    project, ids = _project_with_many(tmp_path)

    entries = _entries(project)

    assert [(e["type"], e["target_type"], e["target_id"]) for e in entries] == [
        ("references", "resource", ids["r1"]),
        ("references", "resource", ids["r2"]),
        ("references", "reference", ids["f1"]),
    ]
    assert len({e["id"] for e in entries}) == 3


def test_link_events_name_the_target_type_and_both_ids(tmp_path):
    project = _project(tmp_path)
    resource = _target(tmp_path, "resource", "Res One")
    reference = _target(tmp_path, "reference", "Ref One")

    r = _link(tmp_path, "resource", "Res One")
    f = _link(tmp_path, "reference", "Ref One")

    assert (r.event.event_type, r.event.target_id) == ("Project Linked to Resource", resource.project.id)
    assert (f.event.event_type, f.event.target_id) == ("Project Linked to Reference", reference.project.id)
    assert r.event.object_id == f.event.object_id == project.project.id
    assert r.event.object_type == "Project" and r.event.workflow == "processing"


def test_linking_the_same_target_twice_is_refused_without_an_event(tmp_path):
    project = _project(tmp_path)
    _target(tmp_path, "resource", "Res One")
    _link(tmp_path, "resource", "Res One")

    again = _link(tmp_path, "resource", "Res One")

    assert not again.applicable and again.event is None
    assert len(_entries(project)) == 1
    assert len(_rel_events(tmp_path)) == 1


def test_missing_source_or_target_and_wrong_pair_are_refused(tmp_path):
    _project(tmp_path)
    _target(tmp_path, "resource", "Res One")

    assert not _link(tmp_path, "resource", "Res One", project="Nope").applicable
    assert not _link(tmp_path, "resource", "Nope").applicable
    meeting = execute_capture(
        ExecutionRequest(title="Sync", actor=Actor.HUMAN),
        spec=MEETING,
        base_dir=tmp_path / "meetings",
        events_dir=tmp_path,
    )
    result = execute_relate(
        RelateRequest(source_title="Website", target_title="Sync", actor=Actor.HUMAN),
        target_spec=MEETING,
        base_dir=tmp_path / "projects",
        target_base_dir=tmp_path / "meetings",
        events_dir=tmp_path,
    )
    assert meeting.applicable and not result.applicable and result.event is None
    assert _rel_events(tmp_path) == []


def test_unlink_by_target_removes_exactly_one_and_keeps_the_rest(tmp_path):
    project, ids = _project_with_many(tmp_path)

    result = _unlink(tmp_path, "resource", "Res One")

    assert result.applicable
    assert result.event.event_type == "Project Unlinked from Resource"
    assert result.event.target_id == ids["r1"]
    assert [e["target_id"] for e in _entries(project)] == [ids["r2"], ids["f1"]]


def test_unlinking_the_last_instance_drops_the_key(tmp_path):
    project = _project(tmp_path)
    _target(tmp_path, "resource", "Res One")
    _link(tmp_path, "resource", "Res One")

    assert _unlink(tmp_path, "resource", "Res One").applicable
    assert "relationships" not in read_project(project.path)["properties"]


def test_unlink_without_a_target_is_refused_for_an_unbounded_relationship(tmp_path):
    project, _ = _project_with_many(tmp_path)

    result = _unlink(tmp_path, "resource", None)

    assert not result.applicable and result.event is None
    assert len(_entries(project)) == 3


def test_unlinking_a_named_target_that_is_not_linked_is_refused(tmp_path):
    project, _ = _project_with_many(tmp_path)
    _target(tmp_path, "resource", "Res Three")

    result = _unlink(tmp_path, "resource", "Res Three")

    assert not result.applicable and result.event is None
    assert len(_entries(project)) == 3


def test_area_and_many_links_coexist_and_unlink_one_kind_leaves_others(tmp_path):
    project, ids = _project_with_many(tmp_path)
    area = _target(tmp_path, "area", "Health")
    assert _link(tmp_path, "area", "Health").applicable
    assert not _link(tmp_path, "area", "Health").applicable

    assert _unlink(tmp_path, "resource", "Res One").applicable

    assert sorted(e["type"] for e in _entries(project)) == ["belongs to", "references", "references"]
    assert area.project.id in [e["target_id"] for e in _entries(project)]


def test_area_unlink_still_works_without_a_target(tmp_path):
    project = _project(tmp_path)
    _target(tmp_path, "area", "Health")
    _link(tmp_path, "area", "Health")

    result = execute_unrelate(
        UnrelateRequest(source_title="Website", actor=Actor.HUMAN),
        base_dir=tmp_path / "projects",
        events_dir=tmp_path,
    )

    assert result.applicable and result.event.event_type == "Project Unlinked from Area"
    assert "relationships" not in read_project(project.path)["properties"]


def test_linking_never_touches_targets_or_project_identity_and_lifecycle(tmp_path):
    project = _project(tmp_path)
    resource = _target(tmp_path, "resource", "Res One")
    reference = _target(tmp_path, "reference", "Ref One")
    before = read_project(project.path)
    targets_before = (resource.path.read_text(encoding="utf-8"), reference.path.read_text(encoding="utf-8"))

    _link(tmp_path, "resource", "Res One")
    _link(tmp_path, "reference", "Ref One")
    after = read_project(project.path)

    assert (resource.path.read_text(encoding="utf-8"), reference.path.read_text(encoding="utf-8")) == targets_before
    for key in ("id", "status", "context", "note_type", "created"):
        assert after["properties"][key] == before["properties"][key]
    assert after["title"] == before["title"]


def test_an_archived_resource_is_a_valid_target_and_archiving_is_non_cascading(tmp_path):
    project = _project(tmp_path)
    _target(tmp_path, "resource", "Res One")
    execute_archive(
        ArchiveRequest(title="Res One", actor=Actor.HUMAN),
        spec=RESOURCE,
        base_dir=tmp_path / "resources",
        events_dir=tmp_path,
    )
    assert _link(tmp_path, "resource", "Res One").applicable
    before = project.path.read_text(encoding="utf-8")

    _target(tmp_path, "resource", "Res Two")
    execute_archive(
        ArchiveRequest(title="Res Two", actor=Actor.HUMAN),
        spec=RESOURCE,
        base_dir=tmp_path / "resources",
        events_dir=tmp_path,
    )

    assert project.path.read_text(encoding="utf-8") == before


def test_human_and_deterministic_actors_behave_identically(tmp_path):
    _project(tmp_path, "By Human")
    _project(tmp_path, "By Machine")
    _target(tmp_path, "resource", "Res One")

    human = _link(tmp_path, "resource", "Res One", project="By Human", actor=Actor.HUMAN)
    machine = _link(tmp_path, "resource", "Res One", project="By Machine", actor=Actor.DETERMINISTIC)

    assert human.applicable and machine.applicable
    assert human.event.event_type == machine.event.event_type


def test_link_display_is_vault_relative_for_nested_folders():
    path = paths.VAULT_DIR / "journal" / "entries" / "2026-07-29.md"

    assert execution._link_display(path, "Entry") == "[[journal/entries/2026-07-29|Entry]]"


def test_link_display_falls_back_outside_the_vault(tmp_path):
    path = tmp_path / "areas" / "health.md"

    assert execution._link_display(path, "Health") == "[[areas/health|Health]]"


def test_each_spec_note_type_matches_its_representation(tmp_path):
    for spec in (PROJECT, AREA, RESOURCE, REFERENCE, MEETING, JOURNAL_ENTRY):
        result = execute_capture(
            ExecutionRequest(title="Probe", actor=Actor.HUMAN),
            spec=spec,
            base_dir=tmp_path / spec.note_type,
            events_dir=tmp_path,
        )
        text = result.path.read_text(encoding="utf-8")
        assert f"note_type: {spec.note_type}" in text, spec.note_type
