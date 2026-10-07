"""`read_contained_projects` and the Area Dashboard must locate the Area by
TITLE, not by the slug the title happens to map to -- the same flaw
Processing's Update (#156), Knowledge's Externalize (#160),
Archive/Reactivate (#161) and Relate/Unrelate (#162) had, applied to a
read-only Projection (#163).

Unlike Evaluate/Review, nothing here emits an Event or writes to a Domain
Object note, so there is no reason taxonomy and no pre-write revalidation
(the same precedent `read_operational_dependents`, #161, set for a
read-only lookup): `applicable=False` with no further detail is the whole
story, because nothing was ever going to be touched or recorded.

The old code read `AREA.file_path(area_title)` directly: a renamed Area is
reported as not existing, even though it does; a different Area already
sitting at that slug has its Projects (and, for the dashboard, its title
and link) silently substituted for the real one's.
"""

from ohtli.execution.execution import (
    Actor,
    ExecutionRequest,
    RelateRequest,
    execute_capture,
    execute_relate,
    read_area_dashboard,
    read_contained_projects,
    write_area_dashboard,
)
from ohtli.execution.specs import AREA, PROJECT
from ohtli.workflow import capture as capture_workflow


def _capture(spec, title, tmp_path):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path / "events",
    )


def _belong(project_title, area_title, tmp_path):
    return execute_relate(
        RelateRequest(source_title=project_title, target_title=area_title, actor=Actor.HUMAN),
        base_dir=tmp_path / "project",
        target_base_dir=tmp_path / "area",
        events_dir=tmp_path / "events",
    )


def _contained(area_title, tmp_path):
    return read_contained_projects(
        area_title, area_base_dir=tmp_path / "area", project_base_dir=tmp_path / "project"
    )


def _dashboard(area_title, tmp_path):
    return read_area_dashboard(
        area_title, area_base_dir=tmp_path / "area", project_base_dir=tmp_path / "project"
    )


def _write(area_title, tmp_path):
    return write_area_dashboard(
        area_title,
        area_base_dir=tmp_path / "area",
        project_base_dir=tmp_path / "project",
        dashboard_base_dir=tmp_path / "dash",
    )


def _hand_text(spec, title, tmp_path, tag):
    domain_object = capture_workflow.transform(title, spec.domain_type)
    representation = spec.to_representation(domain_object)
    scratch = tmp_path / "scratch" / tag
    path = spec.write(representation, base_dir=scratch)
    return path.read_text(encoding="utf-8")


def _symlink(link, target):
    import os
    import pytest

    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links are not available here")


# ---- the fix: locate the Area by title, not by slug ----------------------------------


def test_a_renamed_area_still_lists_its_contained_projects(tmp_path):
    area = _capture(AREA, "Health", tmp_path)
    project = _capture(PROJECT, "Alpha", tmp_path)
    _belong("Alpha", "Health", tmp_path)
    renamed = area.path.parent / "renamed-area.md"
    area.path.rename(renamed)

    result = _contained("Health", tmp_path)

    assert result.applicable is True
    assert [p["id"] for p in result.projects] == [project.project.id]


def test_a_decoy_at_the_areas_slug_is_never_used_for_contains(tmp_path):
    area = _capture(AREA, "Health", tmp_path)
    project = _capture(PROJECT, "Alpha", tmp_path)
    _belong("Alpha", "Health", tmp_path)
    renamed = area.path.parent / "renamed-area.md"
    area.path.rename(renamed)
    decoy = _capture(AREA, "health", tmp_path)
    decoy_bytes = decoy.path.read_bytes()

    result = _contained("Health", tmp_path)

    assert result.applicable is True
    assert [p["id"] for p in result.projects] == [project.project.id]
    assert decoy.path.read_bytes() == decoy_bytes


def test_a_renamed_area_still_renders_its_real_dashboard(tmp_path):
    area = _capture(AREA, "Health", tmp_path)
    project = _capture(PROJECT, "Alpha", tmp_path)
    _belong("Alpha", "Health", tmp_path)
    renamed = area.path.parent / "renamed-area.md"
    area.path.rename(renamed)

    result = _dashboard("Health", tmp_path)

    assert result.applicable is True
    assert result.area_title == "Health"
    assert "Alpha" in result.markdown


def test_a_decoy_at_the_areas_slug_is_never_rendered_instead(tmp_path):
    area = _capture(AREA, "Health", tmp_path)
    _capture(PROJECT, "Alpha", tmp_path)
    _belong("Alpha", "Health", tmp_path)
    renamed = area.path.parent / "renamed-area.md"
    area.path.rename(renamed)
    decoy = _capture(AREA, "health", tmp_path)
    decoy_bytes = decoy.path.read_bytes()

    result = _dashboard("Health", tmp_path)

    assert result.applicable is True
    assert result.area_title == "Health"
    assert "Alpha" in result.markdown
    assert decoy.path.read_bytes() == decoy_bytes


def test_writing_the_dashboard_for_a_renamed_area_with_a_decoy_still_writes_the_real_one(tmp_path):
    area = _capture(AREA, "Health", tmp_path)
    _capture(PROJECT, "Alpha", tmp_path)
    _belong("Alpha", "Health", tmp_path)
    renamed = area.path.parent / "renamed-area.md"
    area.path.rename(renamed)
    _capture(AREA, "health", tmp_path)

    written = _write("Health", tmp_path)

    assert written.applicable is True
    assert written.area_title == "Health"
    assert "Alpha" in written.path.read_text(encoding="utf-8")


# ---- refusing cleanly, never crashing -------------------------------------------------


def test_a_hand_made_file_at_the_areas_slug_is_not_applicable_not_a_crash(tmp_path):
    directory = tmp_path / "area"
    directory.mkdir(parents=True)
    path = directory / "health.md"
    before = b"---\ncontext: operational\n---\n\n# Health\n\nmine\n"
    path.write_bytes(before)

    contained = _contained("Health", tmp_path)
    dashboard = _dashboard("Health", tmp_path)

    assert contained.applicable is False and contained.projects == ()
    assert dashboard.applicable is False and dashboard.markdown is None
    assert path.read_bytes() == before


def test_a_file_without_any_frontmatter_is_not_applicable_not_a_crash(tmp_path):
    directory = tmp_path / "area"
    directory.mkdir(parents=True)
    path = directory / "health.md"
    before = b"# Health\n\njust markdown, no frontmatter at all\n"
    path.write_bytes(before)

    assert _contained("Health", tmp_path).applicable is False
    assert _dashboard("Health", tmp_path).applicable is False
    assert path.read_bytes() == before


def test_two_areas_with_the_same_title_are_not_applicable(tmp_path):
    directory = tmp_path / "area"
    directory.mkdir(parents=True)
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text(_hand_text(AREA, "Health", tmp_path, "a"), encoding="utf-8")
    b.write_text(_hand_text(AREA, "Health", tmp_path, "b"), encoding="utf-8")

    assert _contained("Health", tmp_path).applicable is False
    assert _dashboard("Health", tmp_path).applicable is False


def test_a_symlink_that_only_reaches_the_title_from_outside_is_not_applicable(tmp_path):
    outside_dir = tmp_path / "outside"
    outside = _capture(AREA, "Health", outside_dir)
    before = outside.path.read_bytes()
    directory = tmp_path / "area"
    directory.mkdir(parents=True)
    link = directory / "linked.md"
    _symlink(link, outside.path)

    assert _contained("Health", tmp_path).applicable is False
    assert _dashboard("Health", tmp_path).applicable is False
    assert outside.path.read_bytes() == before
