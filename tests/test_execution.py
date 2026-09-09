from ohtli.domain.area import Area
from ohtli.execution.execution import (
    Actor,
    ArchiveRequest,
    ExecutionRequest,
    ProcessingRequest,
    execute_archive,
    execute_capture,
    execute_processing,
    execute_reactivate,
)
from ohtli.execution.specs import AREA


def test_execution_occurs_when_applicable(tmp_path):
    request = ExecutionRequest(title="First Project", actor=Actor.HUMAN)
    result = execute_capture(request, base_dir=tmp_path)

    assert result.applicable
    assert result.project is not None
    assert result.project.title == "First Project"
    assert result.path is not None
    assert result.path.exists()


def test_execution_does_not_occur_when_not_applicable(tmp_path):
    first = ExecutionRequest(title="Duplicate", actor=Actor.HUMAN)
    execute_capture(first, base_dir=tmp_path)

    second = ExecutionRequest(title="Duplicate", actor=Actor.DETERMINISTIC)
    result = execute_capture(second, base_dir=tmp_path)

    assert not result.applicable
    assert result.project is None
    assert result.path is None


def test_execution_preserves_identity_between_request_and_result(tmp_path):
    request = ExecutionRequest(title="Identity Check", actor=Actor.HUMAN)
    result = execute_capture(request, base_dir=tmp_path)

    assert result.request is request
    assert result.request.execution_id == request.execution_id


def test_processing_occurs_when_applicable(tmp_path):
    entry_path = tmp_path / "raw-entry.md"
    entry_path.write_text("New Idea From Inbox\n\nSome notes.\n", encoding="utf-8")

    request = ProcessingRequest(entry_path=entry_path, actor=Actor.HUMAN)
    result = execute_processing(request, base_dir=tmp_path / "projects")

    assert result.applicable
    assert result.project is not None
    assert result.project.title == "New Idea From Inbox"
    assert result.path is not None
    assert result.path.exists()
    assert not entry_path.exists(), "a processed Inbox entry must be resolved"


def test_processing_does_not_occur_when_entry_has_no_derivable_title(tmp_path):
    entry_path = tmp_path / "empty-entry.md"
    entry_path.write_text("\n   \n", encoding="utf-8")

    request = ProcessingRequest(entry_path=entry_path, actor=Actor.HUMAN)
    result = execute_processing(request, base_dir=tmp_path / "projects")

    assert not result.applicable
    assert result.project is None
    assert result.path is None
    assert entry_path.exists(), "a non-applicable Inbox entry must remain untouched"


def test_processing_does_not_occur_when_title_already_exists(tmp_path):
    projects_dir = tmp_path / "projects"
    first_entry = tmp_path / "first-entry.md"
    first_entry.write_text("Duplicate Title\n", encoding="utf-8")
    execute_processing(
        ProcessingRequest(entry_path=first_entry, actor=Actor.HUMAN), base_dir=projects_dir
    )

    second_entry = tmp_path / "second-entry.md"
    second_entry.write_text("Duplicate Title\n", encoding="utf-8")
    result = execute_processing(
        ProcessingRequest(entry_path=second_entry, actor=Actor.DETERMINISTIC), base_dir=projects_dir
    )

    assert not result.applicable
    assert result.project is None
    assert result.path is None
    assert second_entry.exists()


def test_capture_executes_for_a_different_domain_object_via_spec(tmp_path):
    """The same execute_capture generalizes to Area by passing spec=AREA
    — no duplicate execute_capture_area function."""
    request = ExecutionRequest(title="Health", actor=Actor.HUMAN)
    result = execute_capture(request, spec=AREA, base_dir=tmp_path)

    assert result.applicable
    assert isinstance(result.project, Area)
    assert result.project.title == "Health"
    assert result.path is not None
    assert result.path.exists()


def test_processing_executes_for_a_different_domain_object_via_spec(tmp_path):
    entry_path = tmp_path / "raw-entry.md"
    entry_path.write_text("New Area From Inbox\n\nOngoing responsibility.\n", encoding="utf-8")

    request = ProcessingRequest(entry_path=entry_path, actor=Actor.DETERMINISTIC)
    result = execute_processing(request, spec=AREA, base_dir=tmp_path / "areas")

    assert result.applicable
    assert isinstance(result.project, Area)
    assert result.project.title == "New Area From Inbox"
    assert not entry_path.exists(), "a processed Inbox entry must be resolved"


def test_capture_project_and_area_do_not_share_an_applicability_namespace(tmp_path):
    projects_dir = tmp_path / "projects"
    areas_dir = tmp_path / "areas"

    project_result = execute_capture(
        ExecutionRequest(title="Shared Name", actor=Actor.HUMAN), base_dir=projects_dir
    )
    area_result = execute_capture(
        ExecutionRequest(title="Shared Name", actor=Actor.HUMAN), spec=AREA, base_dir=areas_dir
    )

    assert project_result.applicable
    assert area_result.applicable


def test_archive_is_not_applicable_when_target_does_not_exist(tmp_path):
    request = ArchiveRequest(title="Nonexistent", actor=Actor.HUMAN)
    result = execute_archive(request, base_dir=tmp_path)

    assert not result.applicable
    assert result.project is None
    assert result.path is None


def test_archive_then_reactivate_round_trip(tmp_path):
    execute_capture(ExecutionRequest(title="Round Trip", actor=Actor.HUMAN), base_dir=tmp_path)

    archived = execute_archive(
        ArchiveRequest(title="Round Trip", actor=Actor.HUMAN), base_dir=tmp_path
    )
    assert archived.applicable
    assert archived.path is not None

    reactivated = execute_reactivate(
        ArchiveRequest(title="Round Trip", actor=Actor.DETERMINISTIC), base_dir=tmp_path
    )
    assert reactivated.applicable
    assert reactivated.path == archived.path


def test_archive_is_not_applicable_a_second_time(tmp_path):
    execute_capture(ExecutionRequest(title="Once", actor=Actor.HUMAN), base_dir=tmp_path)
    execute_archive(ArchiveRequest(title="Once", actor=Actor.HUMAN), base_dir=tmp_path)

    second = execute_archive(ArchiveRequest(title="Once", actor=Actor.HUMAN), base_dir=tmp_path)

    assert not second.applicable


def test_reactivate_is_not_applicable_before_archive(tmp_path):
    execute_capture(ExecutionRequest(title="Never Archived", actor=Actor.HUMAN), base_dir=tmp_path)

    result = execute_reactivate(
        ArchiveRequest(title="Never Archived", actor=Actor.HUMAN), base_dir=tmp_path
    )

    assert not result.applicable


def test_archive_does_not_change_status_or_id(tmp_path):
    from ohtli.vault_io.markdown import read_project

    capture_result = execute_capture(
        ExecutionRequest(title="Preserve Me", actor=Actor.HUMAN), base_dir=tmp_path
    )
    before = read_project(capture_result.path)

    execute_archive(ArchiveRequest(title="Preserve Me", actor=Actor.HUMAN), base_dir=tmp_path)
    after = read_project(capture_result.path)

    assert after["properties"]["status"] == before["properties"]["status"]
    assert after["properties"]["id"] == before["properties"]["id"]
    assert after["properties"]["context"] == "historical"


def test_archive_is_non_cascading(tmp_path):
    """Archiving one Project must leave an unrelated Project untouched."""
    execute_capture(ExecutionRequest(title="Archive This", actor=Actor.HUMAN), base_dir=tmp_path)
    other = execute_capture(
        ExecutionRequest(title="Leave This Alone", actor=Actor.HUMAN), base_dir=tmp_path
    )

    execute_archive(ArchiveRequest(title="Archive This", actor=Actor.HUMAN), base_dir=tmp_path)

    from ohtli.vault_io.markdown import read_project

    untouched = read_project(other.path)
    assert untouched["properties"]["context"] == "operational"


def test_archive_and_reactivate_work_for_a_second_domain_object(tmp_path):
    execute_capture(
        ExecutionRequest(title="Household", actor=Actor.HUMAN), spec=AREA, base_dir=tmp_path
    )

    archived = execute_archive(
        ArchiveRequest(title="Household", actor=Actor.DETERMINISTIC), spec=AREA, base_dir=tmp_path
    )
    assert archived.applicable
    assert isinstance(archived.project, Area)

    reactivated = execute_reactivate(
        ArchiveRequest(title="Household", actor=Actor.HUMAN), spec=AREA, base_dir=tmp_path
    )
    assert reactivated.applicable
    assert isinstance(reactivated.project, Area)
