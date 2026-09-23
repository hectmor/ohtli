"""`read_area_dashboard` / `write_area_dashboard`: the Area Dashboard, a
read-only Projection of an Area and its Projects. All against `tmp_path`.

The read writes nothing and emits no event; the write is guarded (it overwrites
only a file this feature generated) and emits no event either, because a
projection changes no Domain Object.
"""

import hashlib

import pytest

from ohtli.execution.execution import (
    Actor,
    ArchiveRequest,
    ExecutionRequest,
    RelateRequest,
    execute_archive,
    execute_capture,
    execute_relate,
    read_area_dashboard,
    read_contained_projects,
    write_area_dashboard,
)
from ohtli.execution.specs import AREA, PROJECT
from ohtli.representation.area_dashboard import GENERATED_MARKER
from ohtli.vault_io import paths
from ohtli.vault_io.events import read_events
from ohtli.vault_io.markdown import find_note_by_id, list_existing_area_titles, list_existing_titles


@pytest.fixture(autouse=True)
def _defaults_are_isolated_and_observable(tmp_path, monkeypatch):
    """Nothing here relies on a default path reaching the real vault, and a test
    can see whether a default folder was ever created."""
    monkeypatch.setattr(paths, "EVENTS_DIR", tmp_path / "default-events")
    monkeypatch.setattr(paths, "AREA_DASHBOARDS_DIR", tmp_path / "default-dashboards")


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


def _archive(tmp_path, spec, title):
    return execute_archive(
        ArchiveRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path,
    )


def _kw(tmp_path):
    return dict(area_base_dir=tmp_path / "area", project_base_dir=tmp_path / "project")


def _read(tmp_path, area="Health"):
    return read_area_dashboard(area, **_kw(tmp_path))


def _write(tmp_path, area="Health"):
    return write_area_dashboard(area, dashboard_base_dir=tmp_path / "dash", **_kw(tmp_path))


def _files(tmp_path):
    return sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file())


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _notes(tmp_path):
    return {str(p.relative_to(tmp_path)): _sha(p) for d in ("area", "project") for p in (tmp_path / d).glob("*.md")}


def _section(text, heading):
    lines = text.splitlines()
    body = []
    for line in lines[lines.index(heading) + 1 :]:
        if line.startswith("#") or line == "---":
            break
        body.append(line)
    return [line for line in body if line.strip()]


@pytest.fixture
def vault(tmp_path):
    """Health holds Alpha (operational) and Zeta (archived); Finance holds Beta;
    Loose belongs to no Area."""
    _capture(tmp_path, AREA, "Health")
    _capture(tmp_path, AREA, "Finance")
    for title in ("Zeta", "Alpha", "Beta", "Loose"):
        _capture(tmp_path, PROJECT, title)
    _belong(tmp_path, "Zeta", "Health")
    _belong(tmp_path, "Alpha", "Health")
    _belong(tmp_path, "Beta", "Finance")
    _archive(tmp_path, PROJECT, "Zeta")
    return tmp_path


# ---- the read -----------------------------------------------------------------------


def test_it_lists_exactly_the_projects_that_belong_to_the_area(vault):
    text = _read(vault).markdown

    listed = _section(text, "### Operational") + _section(text, "### Historical")
    assert listed == [
        "- [[project/alpha|Alpha]] (status: planned)",
        "- [[project/zeta|Zeta]] (status: planned)",
    ], "no Project of another Area, and none without an Area"


def test_operational_and_archived_projects_go_to_their_own_subsection(vault):
    text = _read(vault).markdown

    assert _section(text, "### Operational") == ["- [[project/alpha|Alpha]] (status: planned)"]
    assert _section(text, "### Historical") == ["- [[project/zeta|Zeta]] (status: planned)"]


def test_projects_are_sorted_by_title(tmp_path):
    _capture(tmp_path, AREA, "Health")
    for title in ("Charlie", "Alpha", "Bravo"):
        _capture(tmp_path, PROJECT, title)
        _belong(tmp_path, title, "Health")

    operational = _section(_read(tmp_path).markdown, "### Operational")

    assert operational == [
        "- [[project/alpha|Alpha]] (status: planned)",
        "- [[project/bravo|Bravo]] (status: planned)",
        "- [[project/charlie|Charlie]] (status: planned)",
    ]


def test_links_are_the_folder_qualified_display_links_of_the_existing_helper(vault):
    """Outside the real vault `_link_display` falls back to `<parent>/<stem>`."""
    text = _read(vault).markdown

    assert "Which Projects belong to [[area/health|Health]], and where does each stand?" in text
    assert "- [[area/health|Health]]" in text.splitlines()


def test_the_areas_title_comes_from_its_note_not_from_the_argument(vault):
    lower = _read(vault, "health")
    upper = _read(vault, "Health")

    assert lower.area_title == "Health"
    assert lower.markdown == upper.markdown
    assert lower.markdown.splitlines()[2] == "# Health: Area Dashboard"


def test_a_project_note_without_a_context_field_counts_as_operational(vault):
    """A pre-Phase-13 note has no `context`; nothing marked it historical."""
    note = vault / "project" / "alpha.md"
    note.write_text(note.read_text(encoding="utf-8").replace("context: operational\n", ""), encoding="utf-8")
    assert "context:" not in note.read_text(encoding="utf-8")

    text = _read(vault).markdown

    assert _section(text, "### Operational") == ["- [[project/alpha|Alpha]] (status: planned)"]


def test_an_area_without_projects_shows_none_twice(tmp_path):
    _capture(tmp_path, AREA, "Empty")

    text = _read(tmp_path, "Empty").markdown

    assert _section(text, "### Operational") == ["None."]
    assert _section(text, "### Historical") == ["None."]


def test_an_archived_area_says_so(vault):
    _archive(vault, AREA, "Health")

    text = _read(vault).markdown

    assert "This Area is historical (archived)." in text.splitlines()


def test_an_operational_area_does_not(vault):
    assert "historical (archived)" not in _read(vault).markdown


def test_an_unknown_area_is_not_applicable(vault):
    result = _read(vault, "Nope")

    assert not result.applicable
    assert result.markdown is None and result.area_title is None


def test_the_first_line_is_the_generated_marker(vault):
    assert _read(vault).markdown.splitlines()[0] == GENERATED_MARKER


def test_it_reflects_the_vault_immediately_because_nothing_is_stored(vault):
    before = _section(_read(vault).markdown, "### Operational")

    _archive(vault, PROJECT, "Alpha")
    after = _read(vault).markdown

    assert before == ["- [[project/alpha|Alpha]] (status: planned)"]
    assert _section(after, "### Operational") == ["None."]
    assert "- [[project/alpha|Alpha]] (status: planned)" in _section(after, "### Historical")


def test_it_agrees_with_read_contained_projects(vault):
    contained = read_contained_projects("Health", **_kw(vault))
    text = _read(vault).markdown

    for project in contained.projects:
        assert f"[[project/{project['path'].stem}|{project['title']}]]" in text
    assert text.count("- [[project/") == len(contained.projects)


# ---- the read changes nothing -------------------------------------------------------


def test_the_read_creates_no_file_anywhere(vault):
    before = _files(vault)

    _read(vault)
    _read(vault, "Nope")

    assert _files(vault) == before
    assert not (vault / "default-dashboards").exists()
    assert not (vault / "dash").exists()


def test_the_read_emits_no_event(vault):
    before = read_events(events_dir=vault)

    _read(vault)

    assert read_events(events_dir=vault) == before
    assert not (vault / "default-events").exists()


def test_the_read_leaves_every_note_byte_identical(vault):
    before = _notes(vault)

    _read(vault)

    assert _notes(vault) == before


# ---- the write ----------------------------------------------------------------------


def test_the_write_creates_exactly_one_file_named_after_the_area(vault):
    before = set(_files(vault))

    result = _write(vault)

    assert result.applicable and result.outcome == "created"
    assert result.area_title == "Health"
    assert result.path == vault / "dash" / "health-dashboard.md"
    assert set(_files(vault)) - before == {"dash/health-dashboard.md"}


def test_the_file_is_exactly_the_markdown_the_read_returns(vault):
    result = _write(vault)

    assert result.path.read_text(encoding="utf-8") == _read(vault).markdown == result.markdown


def test_writing_again_is_unchanged_and_byte_identical(vault):
    first = _write(vault)
    digest = _sha(first.path)

    second = _write(vault)

    assert second.outcome == "unchanged"
    assert _sha(second.path) == digest


def test_after_the_vault_changes_the_write_regenerates_the_whole_file(vault):
    first = _write(vault)
    _archive(vault, PROJECT, "Alpha")

    second = _write(vault)

    assert second.outcome == "updated"
    assert second.path.read_text(encoding="utf-8") == _read(vault).markdown
    assert second.path.read_text(encoding="utf-8") != first.markdown


def test_an_unknown_area_writes_nothing_and_creates_no_folder(vault):
    before = _files(vault)

    result = write_area_dashboard("Nope", dashboard_base_dir=vault / "dash", **_kw(vault))

    assert not result.applicable
    assert (result.outcome, result.path, result.markdown, result.area_title) == (None, None, None, None)
    assert _files(vault) == before
    assert not (vault / "dash").exists(), "the Area is checked before any path is computed or folder created"


def test_a_hand_made_file_at_the_dashboards_path_is_refused_and_untouched(vault):
    decoy = vault / "dash" / "health-dashboard.md"
    decoy.parent.mkdir(parents=True)
    decoy.write_text("# my own precious note\n", encoding="utf-8")
    digest = _sha(decoy)

    result = _write(vault)

    assert result.applicable and result.outcome == "refused"
    assert result.path == decoy
    assert _sha(decoy) == digest


def test_the_write_emits_no_event(vault):
    before = read_events(events_dir=vault)

    _write(vault)
    _write(vault)

    assert read_events(events_dir=vault) == before
    assert not (vault / "default-events").exists()


def test_the_write_leaves_every_area_and_project_note_byte_identical(vault):
    before = _notes(vault)

    _write(vault)

    assert _notes(vault) == before


def test_without_a_dashboard_base_dir_it_writes_under_the_dashboards_constant(vault):
    result = write_area_dashboard("Health", **_kw(vault))

    assert result.path == paths.AREA_DASHBOARDS_DIR / "health-dashboard.md"
    assert result.path.parent == vault / "default-dashboards"


# ---- the generated file cannot be mistaken for a Domain Object ----------------------


def test_a_generated_dashboard_is_invisible_to_every_domain_object_scan(vault):
    """Even copied INTO the Area and Project folders, where a scan could reach
    it, it is skipped: it has no frontmatter."""
    generated = _write(vault).path.read_text(encoding="utf-8")
    titles_before = list_existing_area_titles(base_dir=vault / "area")
    project_titles_before = list_existing_titles(base_dir=vault / "project")
    contained_before = read_contained_projects("Health", **_kw(vault)).projects
    health_id = AREA.read(vault / "area" / "health.md")["properties"]["id"]

    (vault / "area" / "health-dashboard.md").write_text(generated, encoding="utf-8")
    (vault / "project" / "health-dashboard.md").write_text(generated, encoding="utf-8")

    assert list_existing_area_titles(base_dir=vault / "area") == titles_before
    assert list_existing_titles(base_dir=vault / "project") == project_titles_before
    assert read_contained_projects("Health", **_kw(vault)).projects == contained_before
    assert find_note_by_id(vault / "area", health_id)["title"] == "Health"


def test_a_later_capture_with_a_colliding_title_does_not_touch_the_dashboard(vault):
    written = _write(vault)
    digest = _sha(written.path)

    captured = _capture(vault, AREA, "Health Dashboard")

    assert captured.applicable
    assert captured.path == vault / "area" / "health-dashboard.md"
    assert _sha(written.path) == digest, "the dashboard lives in a folder no Capture writes to"
