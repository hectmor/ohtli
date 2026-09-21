"""`Area contains Project` is a derived view: never stored, computed from the
Projects whose `belongs to` targets the Area. All against `tmp_path`."""

import random

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
    read_contained_projects,
)
from ohtli.execution.specs import AREA, PROJECT
from ohtli.vault_io import paths
from ohtli.vault_io.events import read_events


@pytest.fixture(autouse=True)
def _default_events_dir_is_isolated(tmp_path, monkeypatch):
    """Nothing here passes `events_dir` to the read under test, so its default
    must never be the real vault; it also lets a test observe a stray write."""
    monkeypatch.setattr(paths, "EVENTS_DIR", tmp_path / "default-events")


def _capture(tmp_path, spec, title):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path,
    )


def _belong(tmp_path, project, area):
    return execute_relate(
        RelateRequest(source_title=project, target_title=area, actor=Actor.HUMAN),
        base_dir=tmp_path / "project",
        target_base_dir=tmp_path / "area",
        events_dir=tmp_path,
    )


def _leave(tmp_path, project):
    return execute_unrelate(
        UnrelateRequest(source_title=project, actor=Actor.HUMAN),
        base_dir=tmp_path / "project",
        events_dir=tmp_path,
    )


def _contained(tmp_path, area):
    return read_contained_projects(
        area, area_base_dir=tmp_path / "area", project_base_dir=tmp_path / "project"
    )


def _titles(result):
    return [p["title"] for p in result.projects]


def test_it_lists_exactly_the_projects_that_belong_to_the_area(tmp_path):
    _capture(tmp_path, AREA, "Health")
    _capture(tmp_path, AREA, "Finance")
    for title in ("Zeta", "Alpha", "Beta", "Loose"):
        _capture(tmp_path, PROJECT, title)
    _belong(tmp_path, "Zeta", "Health")
    _belong(tmp_path, "Alpha", "Health")
    _belong(tmp_path, "Beta", "Finance")

    health = _contained(tmp_path, "Health")

    assert health.applicable
    assert _titles(health) == ["Alpha", "Zeta"], "sorted by title; excludes other Areas and unlinked Projects"
    assert _titles(_contained(tmp_path, "Finance")) == ["Beta"]


def test_each_entry_carries_the_projects_identity_status_and_context(tmp_path):
    _capture(tmp_path, AREA, "Health")
    project = _capture(tmp_path, PROJECT, "Alpha")
    _belong(tmp_path, "Alpha", "Health")

    (entry,) = _contained(tmp_path, "Health").projects

    assert entry["id"] == project.project.id
    assert entry["title"] == "Alpha"
    assert entry["status"] == "planned"
    assert entry["context"] == "operational"


def test_an_area_with_no_projects_is_applicable_and_empty(tmp_path):
    _capture(tmp_path, AREA, "Health")

    result = _contained(tmp_path, "Health")

    assert result.applicable and result.projects == ()


def test_an_unknown_area_is_not_applicable(tmp_path):
    result = _contained(tmp_path, "Nope")

    assert not result.applicable and result.projects == ()


def test_archived_projects_are_included_and_marked_historical(tmp_path):
    """Archive is non-cascading: the `belongs to` link persists."""
    _capture(tmp_path, AREA, "Health")
    _capture(tmp_path, PROJECT, "Alpha")
    _capture(tmp_path, PROJECT, "Zeta")
    _belong(tmp_path, "Alpha", "Health")
    _belong(tmp_path, "Zeta", "Health")
    execute_archive(
        ArchiveRequest(title="Zeta", actor=Actor.HUMAN),
        base_dir=tmp_path / "project",
        events_dir=tmp_path,
    )

    contexts = {p["title"]: p["context"] for p in _contained(tmp_path, "Health").projects}

    assert contexts == {"Alpha": "operational", "Zeta": "historical"}


def test_an_archived_area_still_answers(tmp_path):
    _capture(tmp_path, AREA, "Health")
    _capture(tmp_path, PROJECT, "Alpha")
    _belong(tmp_path, "Alpha", "Health")
    execute_archive(
        ArchiveRequest(title="Health", actor=Actor.HUMAN),
        spec=AREA,
        base_dir=tmp_path / "area",
        events_dir=tmp_path,
    )

    assert _titles(_contained(tmp_path, "Health")) == ["Alpha"]


def test_the_view_follows_a_project_moving_between_areas_immediately(tmp_path):
    """There is no stored copy on the Area, so nothing can go stale."""
    _capture(tmp_path, AREA, "Health")
    _capture(tmp_path, AREA, "Finance")
    _capture(tmp_path, PROJECT, "Alpha")
    _belong(tmp_path, "Alpha", "Health")
    assert _titles(_contained(tmp_path, "Health")) == ["Alpha"]

    _leave(tmp_path, "Alpha")
    assert _titles(_contained(tmp_path, "Health")) == []
    _belong(tmp_path, "Alpha", "Finance")

    assert _titles(_contained(tmp_path, "Health")) == []
    assert _titles(_contained(tmp_path, "Finance")) == ["Alpha"]


def test_the_view_uses_the_stable_id_not_the_title(tmp_path):
    """Renaming the Area's note file/title does not change who belongs to it:
    the relationship references the Area's `id`."""
    area = _capture(tmp_path, AREA, "Health")
    _capture(tmp_path, PROJECT, "Alpha")
    _belong(tmp_path, "Alpha", "Health")
    renamed = area.path.with_name("wellbeing.md")
    text = area.path.read_text(encoding="utf-8").replace("# Health", "# Wellbeing", 1)
    area.path.unlink()
    renamed.write_text(text, encoding="utf-8")

    assert _titles(_contained(tmp_path, "Wellbeing")) == ["Alpha"]
    assert not _contained(tmp_path, "Health").applicable


def test_reading_writes_nothing_and_emits_no_event(tmp_path):
    area = _capture(tmp_path, AREA, "Health")
    project = _capture(tmp_path, PROJECT, "Alpha")
    _belong(tmp_path, "Alpha", "Health")
    notes_before = (area.path.read_bytes(), project.path.read_bytes())
    events_before = read_events(events_dir=tmp_path)

    _contained(tmp_path, "Health")
    _contained(tmp_path, "Nope")

    assert (area.path.read_bytes(), project.path.read_bytes()) == notes_before
    assert read_events(events_dir=tmp_path) == events_before
    assert not paths.events_file_path().exists(), "a read must not write to the default events log either"


def test_the_area_note_never_stores_a_relationships_key(tmp_path):
    """The whole point of deriving it: nothing is stored on the Area."""
    area = _capture(tmp_path, AREA, "Health")
    _capture(tmp_path, PROJECT, "Alpha")
    _belong(tmp_path, "Alpha", "Health")

    assert "relationships" not in AREA.read(area.path)["properties"]


def test_a_note_without_frontmatter_in_the_projects_folder_is_ignored(tmp_path):
    _capture(tmp_path, AREA, "Health")
    _capture(tmp_path, PROJECT, "Alpha")
    _belong(tmp_path, "Alpha", "Health")
    (tmp_path / "project" / "README.md").write_text("navigation, no frontmatter\n", encoding="utf-8")

    assert _titles(_contained(tmp_path, "Health")) == ["Alpha"]


def test_a_missing_projects_folder_yields_an_empty_view(tmp_path):
    _capture(tmp_path, AREA, "Health")

    result = read_contained_projects(
        "Health", area_base_dir=tmp_path / "area", project_base_dir=tmp_path / "no-such-folder"
    )

    assert result.applicable and result.projects == ()


def test_only_belongs_to_counts_not_other_relationships_to_the_same_area(tmp_path):
    """A Journal Entry that `references` the Area is not a Project it contains,
    and a Project's `belongs to` is the only thing that puts it in the view."""
    _capture(tmp_path, AREA, "Health")
    _capture(tmp_path, PROJECT, "Alpha")
    _capture(tmp_path, PROJECT, "Beta")
    _belong(tmp_path, "Alpha", "Health")
    # Beta gets an unrelated relationship type pointing at the same Area id: it
    # must not be listed.
    beta = tmp_path / "project" / "beta.md"
    area_id = AREA.read(tmp_path / "area" / "health.md")["properties"]["id"]
    beta.write_text(
        beta.read_text(encoding="utf-8").replace(
            "status: planned\n",
            f"status: planned\nrelationships:\n- id: x\n  type: references\n  target_id: {area_id}\n"
            "  target_type: area\n  target_link: '[[areas/health|Health]]'\n",
            1,
        ),
        encoding="utf-8",
    )

    assert _titles(_contained(tmp_path, "Health")) == ["Alpha"]


def test_after_any_sequence_of_project_side_operations_the_view_matches_the_projects(tmp_path):
    """The central property: the view always equals what the Projects say, and
    the Area notes are never touched, whatever the sequence of link/unlink."""
    areas = ["A1", "A2", "A3"]
    projects = ["P1", "P2", "P3", "P4", "P5"]
    area_notes = {a: _capture(tmp_path, AREA, a).path for a in areas}
    for p in projects:
        _capture(tmp_path, PROJECT, p)
    area_bytes = {a: path.read_bytes() for a, path in area_notes.items()}
    belongs = {p: None for p in projects}  # the model: which Area each Project belongs to
    rng = random.Random(20260921)

    for _ in range(120):
        project = rng.choice(projects)
        if belongs[project] is None:
            area = rng.choice(areas)
            assert _belong(tmp_path, project, area).applicable
            belongs[project] = area
        else:
            assert not _belong(tmp_path, project, rng.choice(areas)).applicable, "0..1: already belongs to an Area"
            if rng.random() < 0.6:
                assert _leave(tmp_path, project).applicable
                belongs[project] = None

        for area in areas:
            expected = sorted(p for p, a in belongs.items() if a == area)
            assert _titles(_contained(tmp_path, area)) == expected

    assert {a: path.read_bytes() for a, path in area_notes.items()} == area_bytes
