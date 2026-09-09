from datetime import date

from ohtli.domain.area import Area
from ohtli.domain.project import Project
from ohtli.representation.area import to_representation as area_to_representation
from ohtli.representation.project import to_representation
from ohtli.representation.context import archive
from ohtli.vault_io.markdown import (
    list_existing_area_titles,
    list_existing_titles,
    list_inbox_entries,
    read_area,
    read_inbox_entry,
    read_project,
    resolve_inbox_entry,
    rewrite_note,
    write_area,
    write_project,
)


def test_write_then_read_round_trip(tmp_path):
    project = Project(title="Persisted Project")
    rep = to_representation(project, today=date(2026, 8, 25))

    path = write_project(rep, base_dir=tmp_path)
    assert path.exists()

    loaded = read_project(path)
    assert loaded["title"] == "Persisted Project"
    assert loaded["properties"]["id"] == project.id
    assert loaded["properties"]["status"] == "planned"


def test_list_existing_titles_reflects_persisted_files(tmp_path):
    assert list_existing_titles(base_dir=tmp_path) == set()

    rep = to_representation(Project(title="Alpha"), today=date(2026, 8, 25))
    write_project(rep, base_dir=tmp_path)

    assert list_existing_titles(base_dir=tmp_path) == {"Alpha"}


def test_list_existing_titles_on_missing_directory(tmp_path):
    missing = tmp_path / "does-not-exist"
    assert list_existing_titles(base_dir=missing) == set()


def test_list_existing_titles_skips_non_frontmatter_notes(tmp_path):
    (tmp_path / "README.md").write_text("# Projects\n\nNavigation note, no frontmatter.\n")
    (tmp_path / "index.md").write_text("# Projects\n\n## Navigation\n")

    rep = to_representation(Project(title="Real Project"), today=date(2026, 8, 25))
    write_project(rep, base_dir=tmp_path)

    assert list_existing_titles(base_dir=tmp_path) == {"Real Project"}


def test_write_then_read_round_trip_for_area(tmp_path):
    """The write/read/list I/O is a single class of transformation
    reused by every Domain Object, not duplicated per type."""
    area = Area(title="Persisted Area")
    rep = area_to_representation(area, today=date(2026, 8, 25))

    path = write_area(rep, base_dir=tmp_path)
    assert path.exists()

    loaded = read_area(path)
    assert loaded["title"] == "Persisted Area"
    assert loaded["properties"]["id"] == area.id
    assert loaded["properties"]["status"] == "active"


def test_list_existing_area_titles_reflects_persisted_files(tmp_path):
    assert list_existing_area_titles(base_dir=tmp_path) == set()

    rep = area_to_representation(Area(title="Health"), today=date(2026, 8, 25))
    write_area(rep, base_dir=tmp_path)

    assert list_existing_area_titles(base_dir=tmp_path) == {"Health"}


def test_project_and_area_titles_are_independent_namespaces(tmp_path):
    """A Project and an Area may share a title: existing_titles are
    checked per-type, not globally, since they are different Domain
    Objects."""
    projects_dir = tmp_path / "projects"
    areas_dir = tmp_path / "areas"

    write_project(to_representation(Project(title="Shared Name"), today=date(2026, 8, 25)), base_dir=projects_dir)
    write_area(area_to_representation(Area(title="Shared Name"), today=date(2026, 8, 25)), base_dir=areas_dir)

    assert list_existing_titles(base_dir=projects_dir) == {"Shared Name"}
    assert list_existing_area_titles(base_dir=areas_dir) == {"Shared Name"}


def test_rewrite_note_updates_content_at_the_same_path(tmp_path):
    rep = to_representation(Project(title="Rewrite Me"), today=date(2026, 8, 25))
    path = write_project(rep, base_dir=tmp_path)

    archived_rep = archive(rep, today=date(2026, 9, 8))
    returned_path = rewrite_note(path, archived_rep)

    assert returned_path == path
    reloaded = read_project(path)
    assert reloaded["properties"]["context"] == "historical"
    assert reloaded["title"] == "Rewrite Me", "rewrite_note must not recompute the path from title"


def test_list_inbox_entries_on_missing_directory(tmp_path):
    missing = tmp_path / "does-not-exist"
    assert list_inbox_entries(base_dir=missing) == []


def test_list_inbox_entries_excludes_reserved_navigation_filenames(tmp_path):
    (tmp_path / "README.md").write_text("# Inbox\n\nNavigation note.\n")
    (tmp_path / "index.md").write_text("# Inbox\n\n## Navigation\n")
    entry = tmp_path / "raw-idea.md"
    entry.write_text("Raw Idea\n\nSome notes.\n")

    assert list_inbox_entries(base_dir=tmp_path) == [entry]


def test_read_inbox_entry_returns_raw_text(tmp_path):
    entry = tmp_path / "raw-idea.md"
    entry.write_text("Raw Idea\n\nSome notes.\n", encoding="utf-8")

    assert read_inbox_entry(entry) == "Raw Idea\n\nSome notes.\n"


def test_resolve_inbox_entry_removes_the_file(tmp_path):
    entry = tmp_path / "raw-idea.md"
    entry.write_text("Raw Idea\n", encoding="utf-8")

    resolve_inbox_entry(entry)

    assert not entry.exists()
